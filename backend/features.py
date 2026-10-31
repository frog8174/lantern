"""每個功能 = 一組 prompt + 要給模型看的上下文。

Moonlight 的「Context-aware」其實就是：不只丟你選的那句話，
還附上論文標題、摘要、所在頁面的前後文，模型才知道這個術語在這篇裡的意思。
這裡集中管理這些 prompt，要調整語氣、輸出格式都改這支檔案就好。
"""
from __future__ import annotations

import asyncio
import re
from typing import AsyncIterator

import httpx

from . import config, db, llm, retrieval
from .pdf_parse import find_text_rects

LANG = config.TARGET_LANG

SYSTEM = (
    "你是一位耐心、嚴謹的研究同事，正在陪使用者讀一篇學術論文。"
    f"一律使用{LANG}回答；專有名詞第一次出現時保留英文原文，例如「注意力機制（attention）」。"
    "數學式用 LaTeX，行內用 $...$，獨立式用 $$...$$。"
    "只根據論文內容回答；論文沒寫的要明說「論文中沒有提到」，不要編造。"
)


def _est_tokens(text: str) -> int:
    return len(text) // 3  # 粗估：英文約 4 字元/token，中文約 1.5，取中間值


def _pages_text(paper: dict, pages: range) -> str:
    out = []
    for p in pages:
        if 0 <= p < len(paper["meta"]["pages"]):
            out.append(f"=== 第 {p + 1} 頁 ===\n{paper['meta']['pages'][p]}")
    return "\n\n".join(out)


def _header(paper: dict) -> str:
    m = paper["meta"]
    return f"論文標題：{m['title']}\n摘要：{m['abstract'] or '（未偵測到）'}"


def full_text_fits(paper: dict) -> bool:
    total = sum(_est_tokens(p) for p in paper["meta"]["pages"])
    return total < config.LLM_CONTEXT_TOKENS * 0.6  # 留 40% 給問題與回答


def local_context(paper: dict, page: int) -> str:
    """選字解釋用：標題 + 摘要 + 所在頁與前後一頁。"""
    return _header(paper) + "\n\n" + _pages_text(paper, range(page - 1, page + 2))


# ---------------- 選字：解釋 / 翻譯 ----------------
def _history_block(history: str) -> str:
    """接續對話時附上先前的問答；太長只留最後一段（最近的對話最相關）。"""
    return f"\n\n先前針對這段的對話（請接續）：\n{history[-6000:]}" if history.strip() else ""


def explain_messages(paper: dict, selection: str, page: int, question: str = "", history: str = "") -> list:
    task = (f"使用者針對這段問：{question}\n請根據論文內容回答，精簡為主。" if question else
            "請解釋這段在這篇論文中的意思：\n"
            "1. 用白話說明它在講什麼\n"
            "2. 若有術語或符號，逐一解釋它們在本文中的定義\n"
            "3. 若是公式，說明每個變數代表什麼、這條式子的直覺\n"
            "4. 它在整篇論文的論證中扮演什麼角色\n"
            "第一行用「## 」寫一個 15 字內的標題，精簡為主，不要重述原文。")
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content":
            f"{local_context(paper, page)}\n\n"
            f"---\n使用者在第 {page + 1} 頁選取了這段：\n「{selection}」{_history_block(history)}\n\n{task}"},
    ]


def translate_messages(paper: dict, selection: str, page: int) -> list:
    return [
        {"role": "system", "content":
            f"你是學術翻譯。把使用者給的論文段落翻成{LANG}。"
            "術語採用該領域慣用譯名，必要時括號附英文；公式與引用編號原樣保留。只輸出譯文。"},
        {"role": "user", "content":
            f"（背景：論文《{paper['meta']['title']}》）\n\n要翻譯的段落：\n{selection}"},
    ]


def page_translate_messages(paper: dict, page: int) -> list:
    return translate_messages(paper, paper["meta"]["pages"][page], page) + [
        {"role": "system", "content": "依段落分段輸出，保留章節標題。"}
    ]


# ---------------- 對照翻譯：逐段翻譯，疊回原文位置 ----------------
_MARK_RE = re.compile(r"<<(\d+)>>")


def _translatable(text: str) -> bool:
    """頁碼、單一符號、純公式不翻，保留原文。"""
    return len(text) >= 4 and len(re.findall(r"[A-Za-z]{2,}", text)) >= 2


async def stream_block_translation(paper: dict, blocks: list[dict]) -> AsyncIterator[dict]:
    """把一頁的文字區塊分批翻譯，每翻完一段就 yield {"i": 區塊序號, "tr": 譯文}。

    要模型照 <<編號>> 標記逐段輸出（比要它輸出 JSON 穩定：譯文裡有引號、反斜線也不會壞），
    邊串流邊切：看到下一個 <<k>> 就代表上一段翻完了。
    """
    todo = [(i, b["text"]) for i, b in enumerate(blocks) if _translatable(b["text"])]
    batches, cur, size = [], [], 0
    for item in todo:  # 每批約 2500 字元，譯文才不會超過 max_tokens
        if cur and size + len(item[1]) > 2500:
            batches.append(cur)
            cur, size = [], 0
        cur.append(item)
        size += len(item[1])
    if cur:
        batches.append(cur)

    queue: asyncio.Queue = asyncio.Queue()

    async def run(batch: list[tuple[int, str]]):
        try:
            if config.LLM_MOCK:
                for i, t in batch:
                    await queue.put({"i": i, "tr": f"（MOCK 譯文）{t[:60]}"})
                return
            src = "\n\n".join(f"<<{i}>> {t}" for i, t in batch)
            msgs = [
                {"role": "system", "content":
                    f"你是學術翻譯。把論文段落翻成{LANG}。術語用該領域慣用譯名，必要時括號附英文；"
                    "公式、引用編號、變數名原樣保留。"
                    "每段開頭保留原本的 <<編號>> 標記，一段對一段，不要合併、不要省略、不要加任何說明。"},
                {"role": "user", "content": f"（論文《{paper['meta']['title']}》）\n\n{src}"},
            ]
            buf, last = "", None
            async for piece in llm.stream_chat(msgs, task="translate", max_tokens=4096):
                buf += piece
                marks = list(_MARK_RE.finditer(buf))
                if len(marks) >= 2:  # 倒數第二個標記之前的段落都完整了
                    for a, b in zip(marks, marks[1:]):
                        await queue.put({"i": int(a.group(1)), "tr": buf[a.end(): b.start()].strip()})
                    buf = buf[marks[-1].start():]
            m = _MARK_RE.match(buf.strip())
            if m:
                await queue.put({"i": int(m.group(1)), "tr": buf.strip()[m.end():].strip()})
        except Exception as e:
            await queue.put({"error": f"{type(e).__name__}: {e}"})
        finally:
            await queue.put(None)

    # 各批同時送：vLLM 會把並行請求合併計算，比一批接一批快
    tasks = [asyncio.create_task(run(b)) for b in batches]
    done = 0
    while done < len(tasks):
        item = await queue.get()
        if item is None:
            done += 1
        else:
            yield item


# ---------------- 圖片 / 公式截圖解釋（需要視覺模型）----------------
def image_messages(paper: dict, image_data_url: str, page: int, question: str, history: str = "") -> list:
    q = question or "請解釋這張圖（或這條公式）：它呈現什麼、怎麼讀、和論文主張的關係。"
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": [
            {"type": "text", "text": f"{local_context(paper, page)}\n\n---\n使用者框選了第 {page + 1} 頁的這個區域。"
                                     f"{_history_block(history)}\n\n{q}"},
            {"type": "image_url", "image_url": {"url": image_data_url}},
        ]},
    ]


# ---------------- 聊天（RAG）----------------
async def chat_messages(paper: dict, history: list[dict], question: str, page: int | None) -> tuple[list, list]:
    if full_text_fits(paper):
        context = _header(paper) + "\n\n" + _pages_text(paper, range(paper["meta"]["num_pages"]))
        hits: list[dict] = []
    else:
        hits = await retrieval.search(paper["id"], question, k=8)
        parts = [f"[p.{h['page'] + 1}] {h['text']}" for h in hits]
        context = _header(paper) + "\n\n相關段落：\n" + "\n\n".join(parts)
        if page is not None:  # 使用者正在看的那頁也附上
            context += "\n\n使用者目前所在頁面：\n" + _pages_text(paper, range(page, page + 1))
    sys = SYSTEM + (
        "\n回答中引用論文內容時，在句尾標出頁碼，格式固定為 [p.頁碼]，例如 [p.3]。"
    )
    msgs = [{"role": "system", "content": sys},
            {"role": "user", "content": f"以下是論文內容，之後的問題都以此為準：\n\n{context}"},
            {"role": "assistant", "content": "好的，我已讀完，請問。"}]
    msgs += history[-10:]  # 只帶最近 10 則，避免爆 context
    msgs.append({"role": "user", "content": question})
    return msgs, hits


# ---------------- 摘要 ----------------
def _paper_body(paper: dict) -> str:
    if full_text_fits(paper):
        return _pages_text(paper, range(paper["meta"]["num_pages"]))
    n = paper["meta"]["num_pages"]  # 太長就取前段 + 結論附近
    return _pages_text(paper, range(0, 3)) + "\n\n...\n\n" + _pages_text(paper, range(max(3, n - 3), n))


def summary_messages(paper: dict) -> list:
    body = _paper_body(paper)
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content":
            f"{_header(paper)}\n\n{body}\n\n---\n請用 Markdown 整理這篇論文，段落如下：\n"
            "## 一句話總結\n## 研究問題與動機\n## 方法（關鍵步驟條列）\n"
            "## 主要結果（盡量附數字與頁碼 [p.X]）\n## 貢獻與新穎之處\n## 限制與可延伸方向"},
    ]


# ---------------- Workspace wiki（規格見 docs/wiki.md）----------------
WIKI_RULES = (
    f"你在維護一個研究主題的 wiki，用{LANG}寫 Markdown，專有名詞保留英文原文。"
    "每個說法都要附原文引用，格式固定為 [[paper:<論文id>#p<頁碼>]]（頁碼從 1 起），例如 [[paper:abc123#p3]]。"
    "連到其他 wiki 頁用 [[slug]] 或 [[slug|顯示文字]]。只根據提供的內容寫，不要編造。"
)


def _wiki_slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def _wiki_source(paper: dict) -> str:
    """論文取材：有快取的摘要就用（短又精），沒有就取全文或前後幾頁。"""
    summary = db.cache_get(paper["id"], "summary")
    return (f"論文 id：{paper['id']}\n{_header(paper)}\n\n"
            + (f"摘要筆記：\n{summary}" if summary else _paper_body(paper)))


def _strip_fence(text: str) -> str:
    m = re.fullmatch(r"\s*```(?:markdown|md)?\s*\n(.*?)```\s*", text, re.S)
    return (m.group(1) if m else text).strip()


async def _wiki_plan(source: str, pages: list[dict]) -> dict:
    existing = "\n".join(f"- {p['slug']}：{p['title']}" for p in pages) or "（還沒有）"
    prompt = (f"{source}\n\n---\n現有 wiki 頁面：\n{existing}\n\n"
              "請為這篇論文規劃 wiki 更新：\n"
              "1. paper_page：這篇的論文頁，段落為問題、方法、結果、限制，並用 [[slug]] 連到相關概念頁。\n"
              "2. concepts：這篇涉及的 2–5 個關鍵概念 / 方法 / 資料集。現有頁面裡有相同或同義概念的，"
              "一定沿用它的 slug；新的 slug 用小寫英文 kebab-case（例：attention-mechanism）。"
              "note 寫這篇對該概念的重點（含引用）。\n"
              '只輸出 JSON：{"paper_page":{"title":"...","markdown":"..."},'
              '"concepts":[{"slug":"...","title":"...","note":"..."}]}')
    data = await llm.complete_json([{"role": "system", "content": WIKI_RULES},
                                    {"role": "user", "content": prompt}], task="wiki", max_tokens=4000)
    return data if isinstance(data, dict) else {}


async def _wiki_concept(old: dict | None, slug: str, title: str, note: str, source: str) -> str:
    prompt = (f"概念頁 [[{slug}]]（{title}）目前內容：\n{old['markdown'] if old else '（新頁面，還沒有內容）'}\n\n"
              f"---\n新論文：\n{source}\n\n這篇對此概念的重點：{note}\n\n---\n"
              "請輸出這個概念頁合併後的完整新版 Markdown（不是附加在後面）：定義、各論文怎麼用、比較、爭議。"
              "舊內容的資訊與引用都要保留。第一行用「# 」寫頁名。只輸出 Markdown。")
    return _strip_fence(await llm.complete([{"role": "system", "content": WIKI_RULES},
                                            {"role": "user", "content": prompt}], task="wiki", max_tokens=4000))


async def _wiki_index(pages: list[dict]) -> str:
    listing = "\n".join(f"- [[{p['slug']}]]：{p['title']}\n  {p['markdown'][:300]}" for p in pages)
    prompt = (f"wiki 現有頁面（含開頭內容）：\n{listing}\n\n---\n"
              "請寫 wiki 首頁 Markdown：先一段這個 workspace 的主題概述，再把所有頁面分類列成目錄"
              "（論文、概念、方法、資料集…），每項用 [[slug|標題]] 並附一句說明。第一行用「# 」寫標題。只輸出 Markdown。")
    return _strip_fence(await llm.complete([{"role": "system", "content": WIKI_RULES},
                                            {"role": "user", "content": prompt}], task="wiki", max_tokens=3000))


async def update_wiki(wid: str) -> AsyncIterator[dict]:
    """增量整理：每篇未整理的論文 → 規劃 → 論文頁 + 概念頁；全部做完重寫 index。
    每篇做完就記 wiki_ingested，中斷後重跑只做剩下的。yield 進度 {"msg", "done", "total"}。"""
    todo = db.wiki_pending(wid)
    total = len(todo)
    if not total:
        yield {"msg": "沒有需要整理的新論文", "done": 0, "total": 0}
        return
    for i, pid in enumerate(todo):
        paper = db.get_paper(pid)
        name = paper["meta"]["title"] or paper["filename"]
        yield {"msg": f"規劃：{name}", "done": i, "total": total}
        source = _wiki_source(paper)
        plan = await _wiki_plan(source, db.wiki_pages(wid))
        pp = plan.get("paper_page") if isinstance(plan.get("paper_page"), dict) else {}
        db.wiki_save(wid, f"paper-{pid}", str(pp.get("title") or name), str(pp.get("markdown") or ""), [pid])
        for con in plan.get("concepts") or []:
            if not isinstance(con, dict):
                continue
            slug = _wiki_slug(str(con.get("slug") or con.get("title") or ""))
            if not slug or slug == "index" or slug.startswith("paper-"):
                continue
            old = db.wiki_page(wid, slug)
            title = (old or {}).get("title") or str(con.get("title") or slug)
            yield {"msg": f"更新概念頁：{title}", "done": i, "total": total}
            md = await _wiki_concept(old, slug, title, str(con.get("note") or ""), source)
            db.wiki_save(wid, slug, title, md, sorted(set((old or {}).get("sources", [])) | {pid}))
        db.wiki_mark_ingested(wid, pid)
        yield {"msg": f"完成：{name}", "done": i + 1, "total": total}
    yield {"msg": "重寫首頁", "done": total, "total": total}
    pages = [db.wiki_page(wid, p["slug"]) for p in db.wiki_pages(wid) if p["slug"] != "index"]
    sources = sorted({s for p in pages for s in p["sources"]})
    db.wiki_save(wid, "index", "首頁", await _wiki_index(pages), sources)
    yield {"msg": "Wiki 已更新", "done": total, "total": total}


# ---------------- 自動標註 ----------------
HL_COLORS = {"novelty": "purple", "method": "blue", "result": "green"}


async def auto_highlight(paper: dict, pdf_path: str) -> list[dict]:
    """每 2 頁問一次模型：哪些句子是新穎性 / 方法 / 結果。要求「逐字照抄」，
    再用 PyMuPDF 在原頁搜尋那句話的位置，就能畫在 PDF 上。"""
    pages = paper["meta"]["pages"]
    ref_page = _reference_start_page(paper)
    windows = [range(i, min(i + 2, ref_page)) for i in range(0, ref_page, 2)]

    async def one(win: range):
        text = _pages_text(paper, win)
        prompt = (
            "以下是論文的部分頁面。請挑出最關鍵的句子，分成三類：\n"
            "- novelty：作者宣稱的新貢獻、和前人不同之處\n"
            "- method：方法的核心步驟或設計\n"
            "- result：具體的實驗結果或結論（最好含數字）\n"
            "每類最多 2 句，沒有就給空陣列。句子必須「逐字」從原文複製（英文原文，不要翻譯、不要改寫），"
            "並附上它所在的頁碼。只輸出 JSON，格式：\n"
            '{"novelty":[{"page":1,"text":"..."}],"method":[...],"result":[...]}\n\n'
            f"{text}"
        )
        try:
            data = await llm.complete_json([{"role": "user", "content": prompt}], task="highlight", max_tokens=1200)
        except Exception:
            return []
        out = []
        for cat, items in (data or {}).items():
            if cat not in HL_COLORS or not isinstance(items, list):
                continue
            for it in items:
                if not isinstance(it, dict) or not it.get("text"):
                    continue
                p = int(it.get("page", win.start + 1)) - 1
                tried = [p] + [q for q in win if q != p]
                for q in tried:  # 模型頁碼可能抓錯，同窗口內每頁都試
                    rects = find_text_rects(pdf_path, q, it["text"])
                    if rects:
                        out.append({"page": q, "rects": rects, "text": it["text"],
                                    "color": HL_COLORS[cat], "kind": f"auto:{cat}"})
                        break
        return out

    sem = asyncio.Semaphore(4)  # 同時最多 4 個請求，避免把 vLLM 打爆

    async def guarded(win):
        async with sem:
            return await one(win)

    results = await asyncio.gather(*(guarded(w) for w in windows))
    return [h for r in results for h in r]


def _reference_start_page(paper: dict) -> int:
    for item in paper["meta"]["outline"]:
        if re.match(r"^\s*(\d+\.?\s*)?(references|bibliography)\s*$", item["title"], re.I):
            return max(1, item["page"] + 1)
    return paper["meta"]["num_pages"]


# ---------------- 沒有目錄時，請 AI 產生大綱 ----------------
async def ai_outline(paper: dict) -> list[dict]:
    heads = []
    for p, txt in enumerate(paper["meta"]["pages"]):
        heads.append(f"=== 第 {p + 1} 頁（前 600 字）===\n{txt[:600]}")
    prompt = ("根據以下各頁開頭，列出這篇論文的章節大綱。只輸出 JSON："
              '{"outline":[{"level":1,"title":"1 Introduction","page":1}]}\n\n' + "\n\n".join(heads))
    data = await llm.complete_json([{"role": "user", "content": prompt}], task="outline")
    items = data.get("outline", []) if isinstance(data, dict) else []
    return [{"level": int(i.get("level", 1)), "title": str(i.get("title", "")), "page": int(i.get("page", 1)) - 1}
            for i in items if isinstance(i, dict)]


# ---------------- 智慧引用 ----------------
async def lookup_reference(paper: dict, num: str) -> dict:
    ref = paper["meta"]["references"].get(num)
    out = {"num": num, "raw": ref, "paper": None}
    if not ref or not config.SEMANTIC_SCHOLAR_LOOKUP:
        return out
    # 參考文獻格式五花八門，粗略抓出「標題」再丟 Semantic Scholar 搜尋
    title_guess = _guess_ref_title(ref)
    try:
        r = await s2_get("/graph/v1/paper/search", params={
            "query": title_guess, "limit": 1, "fields": S2_FIELDS})
        if r.status_code == 200 and r.json().get("data"):
            out["paper"] = r.json()["data"][0]
        elif r.status_code == 429:
            out["note"] = "Semantic Scholar 限流中，稍後再試（或在 .env 設 SEMANTIC_SCHOLAR_API_KEY）"
    except httpx.HTTPError:
        pass  # 沒網路就只回原文
    return out


S2_FIELDS = "title,abstract,year,authors,venue,citationCount,url,externalIds"


# ---------------- 引用原因：作者為什麼引用這篇、值不值得讀 ----------------
def citing_contexts(paper: dict, num: str, ref: str, limit: int = 5) -> list[str]:
    """在正文裡找出引用這筆參考文獻的句子（含頁碼）。
    編號式找 [12]、[3, 12]、[10–14]；作者-年份式找「第一作者姓氏 … 年份」。"""
    year = re.search(r"\b(19|20)\d{2}[a-z]?\b", ref or "")
    surname = re.match(r"\s*([A-Z][\w'’-]+)", ref or "")
    out = []
    for p, text in enumerate(paper["meta"]["pages"]):
        # 到參考文獻標題就停：清單本身不算「引用它的句子」
        end = re.search(r"(?:^|\n)\s*(?:references|bibliography|參考文獻)\s*(?:\n|$)", text, re.I)
        if end:
            text = text[:end.start()]
        for sent in re.split(r"(?<=[.!?])\s+", text):
            hit = False
            for m in re.finditer(r"\[([\d,\s–-]+)\]", sent):
                for part in m.group(1).split(","):
                    a, _, b = part.strip().replace("–", "-").partition("-")
                    if a.isdigit() and (a == num or (b.isdigit() and int(a) <= int(num) <= int(b))):
                        hit = True
            if not hit and year and surname and surname.group(1) in sent and year.group(0) in sent:
                hit = True
            if hit:
                out.append(f"[p.{p + 1}] {sent.strip()[:400]}")
                if len(out) >= limit:
                    return out
        if end:
            break
    return out


def cite_reason_messages(paper: dict, num: str, ref: str) -> list:
    ctx = "\n".join(citing_contexts(paper, num, ref)) or "（正文中找不到明確的引用句）"
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content":
            f"{_header(paper)}\n\n被引用的參考文獻：{ref}\n\n本文引用它的句子：\n{ctx}\n\n"
            "請用兩小段回答：\n**為何引用**：作者引用它是為了什麼（背景、比較基準、採用的方法、反駁…），附頁碼。\n"
            "**值得讀嗎**：讀這篇論文時有沒有必要回頭讀它、適合什麼情況讀。各 2–3 句。"},
    ]


async def suggested_questions(paper: dict) -> list[str]:
    """聊天視窗一開始的建議問題。失敗就回固定的三題（不快取），不影響聊天本身。"""
    prompt = (f"{_header(paper)}\n\n針對這篇論文，列出讀者最可能想問的 3 個問題，每題 25 字內，用{LANG}。"
              '只輸出 JSON：{"questions": ["...", "...", "..."]}')
    try:
        data = await llm.complete_json([{"role": "user", "content": prompt}], task="suggest", max_tokens=400)
        qs = [str(q) for q in (data.get("questions") or [])][:3]
        if qs:
            return qs
    except Exception:
        pass
    return []


# ---------------- 相關論文推薦（Semantic Scholar Recommendations）----------------
class S2Error(Exception):
    pass


def _check(r: httpx.Response) -> httpx.Response:
    if r.status_code == 429:
        raise S2Error("Semantic Scholar 限流中，稍後再試（或在 .env 設 SEMANTIC_SCHOLAR_API_KEY）")
    if r.status_code >= 400:
        raise S2Error(f"Semantic Scholar 回應 HTTP {r.status_code}")
    return r


async def s2_paper_id(paper: dict) -> str | None:
    """找出這篇在 Semantic Scholar 的 paperId：arXiv 匯入的用編號查，其他用標題比對。結果快取。"""
    cached = db.cache_get(paper["id"], "s2id")
    if cached:
        return cached
    m = re.match(r"arXiv-(\d{4}\.\d{4,5})", paper["filename"] or "")
    if m:
        r = await s2_get(f"/graph/v1/paper/arXiv:{m.group(1)}", params={"fields": "paperId"})
    else:
        r = await s2_get("/graph/v1/paper/search/match",
                         params={"query": paper["meta"]["title"], "fields": "paperId"})
    if r.status_code == 404:
        return None
    data = _check(r).json()
    sid = data.get("paperId") or (data.get("data") or [{}])[0].get("paperId")
    if sid:
        db.cache_set(paper["id"], "s2id", sid)
    return sid


async def recommend(seed_ids: list[str], limit: int = 15) -> list[dict]:
    """一篇 → forpaper 端點；多篇（整個論文庫）→ 以它們為正例的推薦。"""
    if len(seed_ids) == 1:
        r = await s2_get(f"/recommendations/v1/papers/forpaper/{seed_ids[0]}",
                         params={"fields": S2_FIELDS, "limit": limit, "from": "all-cs"})
    else:
        r = await s2_get("/recommendations/v1/papers/", method="POST",
                         params={"fields": S2_FIELDS, "limit": limit},
                         json={"positivePaperIds": seed_ids[:100]})
    return _check(r).json().get("recommendedPapers", [])


async def s2_get(path: str, **kw) -> httpx.Response:
    """呼叫 Semantic Scholar API。有 key 就帶上（額度高很多）。"""
    headers = {"x-api-key": config.SEMANTIC_SCHOLAR_API_KEY} if config.SEMANTIC_SCHOLAR_API_KEY else {}
    async with httpx.AsyncClient(timeout=12, base_url="https://api.semanticscholar.org") as client:
        return await client.request(kw.pop("method", "GET"), path, headers=headers, **kw)


def _guess_ref_title(ref: str) -> str:
    q = re.search(r"[“\"](.+?)[”\"]", ref)  # IEEE 風格常把標題放引號裡
    if q:
        return q.group(1)
    parts = [p.strip() for p in re.split(r"\.\s+", ref) if len(p.strip()) > 15]
    return parts[1] if len(parts) > 1 else ref[:150]
