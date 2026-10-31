"""FastAPI 入口。啟動：uv run uvicorn backend.main:app --reload --port 7800

API 一覽（前端 app.js 會呼叫）：
  POST   /api/papers                 上傳 PDF（multipart）
  POST   /api/papers/arxiv           用 arXiv 網址或編號匯入
  GET    /api/papers                 論文列表
  GET    /api/papers/{id}            論文資訊（標題、大綱、摘要…）
  GET    /api/papers/{id}/pdf        PDF 原檔（給 PDF.js 顯示）
  DELETE /api/papers/{id}
  POST   /api/papers/{id}/explain        選字解釋        （SSE 串流）
  POST   /api/papers/{id}/translate      選字翻譯        （SSE）
  POST   /api/papers/{id}/translate-page 整頁翻譯        （SSE，會快取）
  POST   /api/papers/{id}/explain-image  框選圖片/公式解釋（SSE）
  POST   /api/papers/{id}/chat           聊天            （SSE）
  GET    /api/papers/{id}/summary        摘要            （SSE，會快取）
  POST   /api/papers/{id}/auto-highlight 自動標註
  GET    /api/papers/{id}/outline-ai     AI 產生大綱
  GET    /api/papers/{id}/reference/{n}  引用卡片
  GET/POST/PATCH/DELETE .../annotations  螢光筆與註解
  /api/auth/*、/api/me、/api/workspaces…  測試登入與 workspace（見 docs/workspaces.md）

SSE（Server-Sent Events）：伺服器用一條 HTTP 連線持續推送 "data: ...\n\n"，
前端邊收邊顯示，所以模型生成時你就能看到字一個個出來。
"""
from __future__ import annotations

import asyncio
import base64
import json
import re
from typing import Annotated, AsyncIterator, Callable, Literal

import httpx
from fastapi import Cookie, Depends, FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config, db, features, llm, pdf_parse, retrieval
from .pdf_parse import parse_pdf

app = FastAPI(title="Paper Reader")
db.init()

PDF_DIR = config.DATA_DIR / "pdfs"


# ---------------- 登入 ----------------
# shortcut: unsigned dev cookie, replace current_user() when real auth lands
def current_user(uid: str | None = Cookie(None)) -> str:
    if not uid or not db.get_user(uid):
        raise HTTPException(401, "not logged in")
    return uid


Uid = Annotated[str, Depends(current_user)]


@app.get("/api/auth/users")
def auth_users():
    if config.AUTH_MODE != "dev":
        raise HTTPException(404, "Not Found")
    return db.list_users()


class LoginIn(BaseModel):
    user_id: str


@app.post("/api/auth/login")
def login(body: LoginIn, response: Response):
    u = db.get_user(body.user_id) if config.AUTH_MODE == "dev" else None
    if not u:
        raise HTTPException(401, "unknown user")
    response.set_cookie("uid", u["id"], httponly=True, samesite="lax")
    return u


@app.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie("uid")
    return {"ok": True}


@app.get("/api/me")
def me(uid: Uid):
    return db.get_user(uid)


class SettingsIn(BaseModel):
    auto_translate: bool = False  # 上傳後在背景先把整篇對照翻譯跑完


@app.get("/api/me/settings")
def get_settings(uid: Uid):
    return SettingsIn(**db.get_settings(uid)).model_dump()


@app.put("/api/me/settings")
def put_settings(body: SettingsIn, uid: Uid):
    db.set_settings(uid, body.model_dump())
    return body.model_dump()


# ---------------- 工具函式 ----------------
def _paper_or_404(pid: str, uid: str) -> dict:
    p = db.get_paper(pid)
    if not p or p["user_id"] != uid:
        raise HTTPException(404, "paper not found")
    return p


def _ws_or_404(wid: str, uid: str) -> dict:
    w = db.get_workspace(uid, wid)
    if not w:
        raise HTTPException(404, "workspace not found")
    return w


def _pdf_path(pid: str) -> str:
    return str(PDF_DIR / f"{pid}.pdf")


def sse(gen: AsyncIterator[str], on_done: Callable[[str], None] | None = None) -> StreamingResponse:
    async def wrapped():
        full = []
        try:
            async for piece in gen:
                full.append(piece)
                yield f"data: {json.dumps({'t': piece}, ensure_ascii=False)}\n\n"
            if on_done:
                on_done("".join(full))
        except Exception as e:  # 模型連不上、context 太長…都回報給前端顯示
            yield f"data: {json.dumps({'error': f'{type(e).__name__}: {e}'}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(wrapped(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


async def _cached_text(text: str) -> AsyncIterator[str]:
    yield text


async def _ocr_pages(path: str, pages: list[int]) -> tuple[dict[int, str], str | None]:
    """掃描頁丟給 OCR 模型。一次最多 2 頁並行，避免單張 GPU 被塞爆。"""
    sem = asyncio.Semaphore(2)

    async def one(pno: int):
        async with sem:
            png = await asyncio.to_thread(pdf_parse.render_page_png, path, pno, 150)
            return pno, await llm.ocr_image("data:image/png;base64," + base64.b64encode(png).decode())

    try:
        return dict(await asyncio.gather(*(one(p) for p in pages))), None
    except Exception as e:  # 模型不支援影像、連不上…論文照樣匯入，只是那幾頁沒文字
        return {}, f"{type(e).__name__}: {e}"


async def _ingest(uid: str, pid: str, filename: str, path: str, workspace: str | None) -> dict:
    parsed = parse_pdf(path)
    ocr_error = None
    if parsed.scanned_pages and config.OCR_ENABLED:
        results, ocr_error = await _ocr_pages(path, parsed.scanned_pages)
        pdf_parse.apply_ocr(parsed, results)
    n = await retrieval.build_index(pid, parsed.blocks)
    meta = parsed.to_dict()
    db.add_paper(uid, pid, filename, parsed.title, meta)
    if workspace:
        db.add_to_workspace(workspace, pid)
    if db.get_settings(uid).get("auto_translate"):
        task = asyncio.create_task(_pretranslate(pid))
        _bg_tasks.add(task)  # 留住參考，不然 task 可能被回收
        task.add_done_callback(_bg_tasks.discard)
    return {"id": pid, "title": parsed.title, "num_pages": parsed.num_pages, "chunks": n,
            "scanned_pages": len(parsed.scanned_pages), "ocr_pages": len(parsed.ocr_pages),
            "ocr_error": ocr_error, "ocr_enabled": config.OCR_ENABLED}


def _public(p: dict) -> dict:
    m = p["meta"]
    return {"id": p["id"], "filename": p["filename"], "title": m["title"], "num_pages": m["num_pages"],
            "page_sizes": m["page_sizes"], "outline": m["outline"], "abstract": m["abstract"],
            "references": len(m["references"]), "full_text_fits": features.full_text_fits(p),
            "scanned_pages": m.get("scanned_pages", []), "ocr_pages": m.get("ocr_pages", []),
            "tags": p.get("tags", [])}


# ---------------- 論文 ----------------
@app.post("/api/papers")
async def upload(file: UploadFile, uid: Uid, workspace: str | None = Form(None)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "只接受 PDF")
    if workspace:
        _ws_or_404(workspace, uid)
    pid = db.new_id()
    path = _pdf_path(pid)
    with open(path, "wb") as f:
        f.write(await file.read())
    return await _ingest(uid, pid, file.filename, path, workspace)


class ArxivIn(BaseModel):
    url: str
    workspace: str | None = None


MAX_PDF_BYTES = 150 * 1024 * 1024


@app.post("/api/papers/arxiv")
async def import_url(body: ArxivIn, uid: Uid):
    """用 arXiv 編號 / 網址，或任何直接指向 PDF 的網址匯入。
    伺服器在你的電腦上下載，所以學校網路（IP 授權）能看的期刊 PDF 也抓得到。"""
    if body.workspace:
        _ws_or_404(body.workspace, uid)
    url = body.url.strip()
    m = re.fullmatch(r"(?:arxiv:)?(\d{4}\.\d{4,5}(?:v\d+)?)", url, re.I) or \
        (re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5}(?:v\d+)?)", url) if "arxiv.org" in url else None)
    if m:
        src, name = f"https://arxiv.org/pdf/{m.group(1)}", f"arXiv-{m.group(1)}.pdf"
    elif re.match(r"https?://", url, re.I):
        src = url
        name = (re.sub(r"[^\w.-]", "_", url.split("?")[0].rstrip("/").rsplit("/", 1)[-1]) or "paper")[:80]
        name = name if name.lower().endswith(".pdf") else name + ".pdf"
    else:
        raise HTTPException(400, "請輸入 arXiv 編號（例：2401.01234）或 PDF 的網址（http/https）")
    try:
        async with httpx.AsyncClient(timeout=90, follow_redirects=True,
                                     headers={"User-Agent": "Mozilla/5.0 (Lantern paper reader)"}) as client:
            r = await client.get(src)
    except httpx.HTTPError as e:
        raise HTTPException(502, f"下載失敗：{type(e).__name__}")
    if r.status_code != 200:
        raise HTTPException(502, f"下載失敗（HTTP {r.status_code}）")
    if not r.content.startswith(b"%PDF"):
        # 期刊的 DOI / 文章頁通常是 HTML，要的是頁面上「下載 PDF」那個連結
        raise HTTPException(400, "這個網址回傳的不是 PDF（可能是文章頁）。請貼上「下載 PDF」按鈕的連結")
    if len(r.content) > MAX_PDF_BYTES:
        raise HTTPException(413, "PDF 超過 150 MB")
    pid = db.new_id()
    path = _pdf_path(pid)
    with open(path, "wb") as f:
        f.write(r.content)
    return await _ingest(uid, pid, name, path, body.workspace)


@app.get("/api/papers")
def papers(uid: Uid, workspace: str | None = None):
    if workspace:
        _ws_or_404(workspace, uid)
    return db.list_papers(uid, workspace)


@app.get("/api/papers/{pid}")
def paper(pid: str, uid: Uid):
    return _public(_paper_or_404(pid, uid))


@app.get("/api/papers/{pid}/pdf")
def paper_pdf(pid: str, uid: Uid):
    _paper_or_404(pid, uid)
    return FileResponse(_pdf_path(pid), media_type="application/pdf")


class TagsIn(BaseModel):
    tags: list[str]


@app.patch("/api/papers/{pid}")
def edit_paper(pid: str, uid: Uid, body: TagsIn):
    _paper_or_404(pid, uid)
    tags = list(dict.fromkeys(t.strip() for t in body.tags if t.strip()))  # 去空白、去重複、保留順序
    db.set_tags(pid, tags)
    return {"tags": tags}


@app.get("/api/search")
def search(q: str, uid: Uid):
    """全文搜尋所有論文，回傳 [{paper_id, title, page, snippet}]。"""
    q = q.strip()
    if len(q) < 2:
        return []
    out = []
    for r in db.search_chunks(uid, q):
        i = r["text"].lower().find(q.lower())
        s = max(0, i - 60)
        out.append({"paper_id": r["paper_id"], "title": r["title"], "page": r["page"],
                    "snippet": ("…" if s else "") + r["text"][s: i + len(q) + 80] + "…"})
    return out


@app.delete("/api/papers/{pid}")
def delete(pid: str, uid: Uid):
    _paper_or_404(pid, uid)
    db.delete_paper(pid)
    try:
        (PDF_DIR / f"{pid}.pdf").unlink()
    except FileNotFoundError:
        pass
    return {"ok": True}


# ---------------- AI 功能 ----------------
class SelectionIn(BaseModel):
    text: str
    page: int = 0
    question: str = ""  # 選字工具列的「Ask AI」：針對選取段落提問
    history: str = ""   # 接續之前的解釋對話時，先前的問答（Markdown）


@app.post("/api/papers/{pid}/explain")
async def explain(pid: str, uid: Uid, body: SelectionIn):
    p = _paper_or_404(pid, uid)
    return sse(llm.stream_chat(features.explain_messages(p, body.text, body.page, body.question, body.history), task="explain"))


@app.post("/api/papers/{pid}/translate")
async def translate(pid: str, uid: Uid, body: SelectionIn):
    p = _paper_or_404(pid, uid)
    return sse(llm.stream_chat(features.translate_messages(p, body.text, body.page), task="translate"))


class PageIn(BaseModel):
    page: int


@app.post("/api/papers/{pid}/translate-page")
async def translate_page(pid: str, uid: Uid, body: PageIn):
    p = _paper_or_404(pid, uid)
    cached = db.cache_get(pid, "page_translation", str(body.page))
    if cached:
        return sse(_cached_text(cached))
    return sse(llm.stream_chat(features.page_translate_messages(p, body.page), task="translate", max_tokens=4096),
               on_done=lambda t: db.cache_set(pid, "page_translation", t, str(body.page)))


@app.post("/api/papers/{pid}/translate-blocks")
async def translate_blocks(pid: str, uid: Uid, body: PageIn):
    """對照翻譯（SSE）。第一則訊息是整頁的區塊座標 {"blocks": [...]}，
    之後每翻完一段推一則 {"i": 序號, "tr": 譯文}。整頁翻完才寫快取。"""
    return sse(_block_translation(_paper_or_404(pid, uid), body.page))


async def _block_translation(p: dict, page: int) -> AsyncIterator[str]:
    pid, key = p["id"], str(page)
    cached = db.cache_get(pid, "block_translation", key)
    if cached:
        yield json.dumps({"blocks": cached}, ensure_ascii=False)
        return
    blocks = [{"bbox": b.bbox, "text": b.text, "size": b.size}
              for b in await asyncio.to_thread(pdf_parse.page_blocks, _pdf_path(pid), page)]
    yield json.dumps({"blocks": blocks}, ensure_ascii=False)
    failed = False
    async for item in features.stream_block_translation(p, blocks):
        if "error" in item:
            failed = True
        else:
            blocks[item["i"]]["tr"] = item["tr"]
        yield json.dumps(item, ensure_ascii=False)
    if not failed:
        db.cache_set(pid, "block_translation", blocks, key)


_bg_tasks: set[asyncio.Task] = set()


async def _pretranslate(pid: str) -> None:
    """背景逐頁跑對照翻譯，結果進快取；之後打開那頁就直接顯示。"""
    # shortcut: 使用者若在背景跑完前打開同一頁，會重複翻一次（多花一點 token）；之後可加 per-page 鎖
    p = db.get_paper(pid)
    for page in range(p["meta"]["num_pages"]):
        if not db.get_paper(pid):  # 中途被刪了就停
            return
        try:
            async for _ in _block_translation(p, page):
                pass
        except Exception as e:  # 某頁失敗不影響其他頁；打開那頁時會再試
            print(f"[pretranslate] {pid} p.{page}: {type(e).__name__}: {e}")


class ImageIn(BaseModel):
    image: str  # data:image/png;base64,...
    page: int = 0
    question: str = ""
    history: str = ""


@app.post("/api/papers/{pid}/explain-image")
async def explain_image(pid: str, uid: Uid, body: ImageIn):
    p = _paper_or_404(pid, uid)
    return sse(llm.stream_chat(features.image_messages(p, body.image, body.page, body.question, body.history), task="vision"))


class ChatIn(BaseModel):
    question: str
    page: int | None = None


@app.post("/api/papers/{pid}/chat")
async def chat(pid: str, uid: Uid, body: ChatIn):
    p = _paper_or_404(pid, uid)
    history = db.list_messages(pid)
    msgs, _hits = await features.chat_messages(p, history, body.question, body.page)
    db.add_message(pid, "user", body.question)
    return sse(llm.stream_chat(msgs, task="chat"), on_done=lambda t: db.add_message(pid, "assistant", t))


@app.get("/api/papers/{pid}/chat")
def chat_history(pid: str, uid: Uid):
    _paper_or_404(pid, uid)
    return db.list_messages(pid, limit=200)


@app.delete("/api/papers/{pid}/chat")
def chat_clear(pid: str, uid: Uid):
    _paper_or_404(pid, uid)
    db.clear_messages(pid)
    return {"ok": True}


@app.get("/api/papers/{pid}/summary")
async def summary(pid: str, uid: Uid, refresh: bool = False):
    p = _paper_or_404(pid, uid)
    cached = None if refresh else db.cache_get(pid, "summary")
    if cached:
        return sse(_cached_text(cached))
    return sse(llm.stream_chat(features.summary_messages(p), task="summary", max_tokens=3000),
               on_done=lambda t: db.cache_set(pid, "summary", t))


@app.post("/api/papers/{pid}/auto-highlight")
async def auto_highlight(pid: str, uid: Uid, refresh: bool = False):
    p = _paper_or_404(pid, uid) | {"id": pid}
    existing = [a for a in db.list_annotations(pid) if a["kind"].startswith("auto:")]
    if existing and not refresh:
        return existing
    for a in existing:
        db.delete_annotation(a["id"])
    hls = await features.auto_highlight(p, _pdf_path(pid))
    return [db.add_annotation(pid, h) for h in hls]


@app.get("/api/papers/{pid}/outline-ai")
async def outline_ai(pid: str, uid: Uid):
    p = _paper_or_404(pid, uid)
    cached = db.cache_get(pid, "outline")
    if cached is None:
        cached = await features.ai_outline(p)
        db.cache_set(pid, "outline", cached)
    return cached


def _figures(pid: str) -> list[dict]:
    cached = db.cache_get(pid, "figures")
    if cached is None:
        cached = pdf_parse.find_figures(_pdf_path(pid))
        db.cache_set(pid, "figures", cached)
    return cached


@app.get("/api/papers/{pid}/figures")
def figures(pid: str, uid: Uid):
    """所有圖 / 表的位置與圖說，前端滑過 "Figure 3" 時用來預覽。"""
    _paper_or_404(pid, uid)
    return _figures(pid)


@app.get("/api/papers/{pid}/figures/{kind}/{num}.png")
def figure_png(pid: str, uid: Uid, kind: str, num: str):
    _paper_or_404(pid, uid)
    fig = next((f for f in _figures(pid) if f["kind"] == kind and f["num"] == num), None)
    if not fig:
        raise HTTPException(404, "找不到這張圖")
    png = pdf_parse.render_page_png(_pdf_path(pid), fig["page"], 144, fig["bbox"])
    return Response(png, media_type="image/png", headers={"Cache-Control": "max-age=86400"})


def _mark_in_library(recs: list[dict], uid: str) -> list[dict]:
    """推薦清單裡已經在論文庫的，標上 in_library（用 arXiv 編號或標題比對）。"""
    have_arxiv, have_title = set(), set()
    for p in db.list_papers(uid):
        m = re.match(r"arXiv-(\d{4}\.\d{4,5})", p["filename"] or "")
        if m:
            have_arxiv.add(m.group(1))
        have_title.add((p["title"] or "").lower().strip())
    for r in recs:
        ax = (r.get("externalIds") or {}).get("ArXiv")
        r["in_library"] = ax in have_arxiv or (r.get("title") or "").lower().strip() in have_title
    return recs


@app.get("/api/papers/{pid}/related")
async def related(pid: str, uid: Uid, refresh: bool = False):
    """與這篇相關的論文。"""
    p = _paper_or_404(pid, uid)
    if not config.SEMANTIC_SCHOLAR_LOOKUP:
        raise HTTPException(503, "已關閉 Semantic Scholar（.env 的 SEMANTIC_SCHOLAR_LOOKUP=false），沒有推薦資料來源")
    cached = None if refresh else db.cache_get(pid, "related")
    if cached is None:
        try:
            sid = await features.s2_paper_id(p)
            if not sid:
                raise HTTPException(404, "Semantic Scholar 找不到這篇論文，無法推薦")
            cached = await features.recommend([sid])
        except features.S2Error as e:
            raise HTTPException(503, str(e))
        db.cache_set(pid, "related", cached)
    return _mark_in_library(cached, uid)


@app.get("/api/recommendations")
async def recommendations(uid: Uid):
    """依整個論文庫推薦（Moonlight 的 Scholar Deep Search 類似功能）。"""
    if not config.SEMANTIC_SCHOLAR_LOOKUP:
        raise HTTPException(503, "已關閉 Semantic Scholar（.env 的 SEMANTIC_SCHOLAR_LOOKUP=false），沒有推薦資料來源")
    ids = []
    try:
        for p in db.list_papers(uid)[:30]:
            sid = await features.s2_paper_id(db.get_paper(p["id"]))
            if sid:
                ids.append(sid)
        if not ids:
            raise HTTPException(404, "論文庫是空的，或都在 Semantic Scholar 找不到")
        recs = await features.recommend(ids, limit=20)
    except features.S2Error as e:
        raise HTTPException(503, str(e))
    return _mark_in_library(recs, uid)


@app.get("/api/papers/{pid}/region.png")
def region_png(pid: str, uid: Uid, page: int, x0: float, y0: float, x1: float, y1: float):
    """頁面上任一塊區域（0~1 座標）的 PNG：接續框選解釋的對話時，重新取得當時框的圖。"""
    p = _paper_or_404(pid, uid)
    if not (0 <= page < p["meta"]["num_pages"] and 0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        raise HTTPException(400, "頁碼或區域超出範圍")
    png = pdf_parse.render_page_png(_pdf_path(pid), page, 150, [x0, y0, x1, y1])
    return Response(png, media_type="image/png", headers={"Cache-Control": "max-age=86400"})


@app.get("/api/papers/{pid}/reference-search")
async def reference_search(pid: str, uid: Uid, author: str, year: str):
    """作者-年份引用：(Peters et al., 2018a) → author=Peters&year=2018a"""
    p = _paper_or_404(pid, uid)
    key = pdf_parse.match_author_year(p["meta"]["references"], author, year)
    if key is None:
        return {"num": f"{author} {year}", "raw": None, "paper": None}
    return await reference(pid, uid, key)


@app.get("/api/papers/{pid}/reference/{num}")
async def reference(pid: str, uid: Uid, num: str):
    p = _paper_or_404(pid, uid)
    cached = db.cache_get(pid, "reference", num)
    if cached is None:
        cached = await features.lookup_reference(p, num)
        if cached.get("paper"):
            db.cache_set(pid, "reference", cached, num)
    return cached


@app.get("/api/papers/{pid}/references")
def references(pid: str, uid: Uid):
    """整篇的參考文獻清單，給活動面板的「引用」分頁。"""
    refs = _paper_or_404(pid, uid)["meta"]["references"]
    return [{"num": k, "raw": v} for k, v in refs.items()]


@app.get("/api/papers/{pid}/reference/{num}/why")
async def reference_why(pid: str, uid: Uid, num: str):
    """引用卡片的「為何引用」：找出正文引用它的句子，請 AI 說明引用原因、值不值得讀（SSE，會快取）。"""
    p = _paper_or_404(pid, uid)
    ref = p["meta"]["references"].get(num)
    if not ref:
        raise HTTPException(404, "找不到這筆參考文獻")
    cached = db.cache_get(pid, "cite_reason", num)
    if cached:
        return sse(_cached_text(cached))
    return sse(llm.stream_chat(features.cite_reason_messages(p, num, ref), task="cite"),
               on_done=lambda t: db.cache_set(pid, "cite_reason", t, num))


@app.get("/api/papers/{pid}/suggestions")
async def suggestions(pid: str, uid: Uid):
    p = _paper_or_404(pid, uid)
    cached = db.cache_get(pid, "suggestions")
    if cached is None:
        cached = await features.suggested_questions(p)
        if cached:
            db.cache_set(pid, "suggestions", cached)
    return cached

# ---------------- 註解 ----------------
class AnnotIn(BaseModel):
    page: int
    rects: list[list[float]]
    # 標準色名稱或自訂色 #rrggbb；explain / image / comment 是解釋（文字 / 框選）與註解的標記
    color: str = Field("yellow", pattern=r"^(yellow|green|blue|pink|purple|explain|image|comment|#[0-9a-fA-F]{6})$")
    text: str = ""
    comment: str = ""  # 螢光筆的備註；kind=explain 時存 AI 的解釋（含追問）；kind=comment 時是註解內容
    kind: Literal["user", "explain", "comment"] = "user"  # auto:* 只能由自動標註產生


@app.get("/api/papers/{pid}/annotations")
def annotations(pid: str, uid: Uid):
    _paper_or_404(pid, uid)
    return db.list_annotations(pid)


@app.post("/api/papers/{pid}/annotations")
def add_annotation(pid: str, uid: Uid, body: AnnotIn):
    _paper_or_404(pid, uid)
    return db.add_annotation(pid, body.model_dump())


class CommentIn(BaseModel):
    comment: str


def _own_annotation(aid: str, uid: str) -> None:
    pid = db.annotation_paper(aid)
    if not pid:
        raise HTTPException(404, "annotation not found")
    _paper_or_404(pid, uid)


@app.patch("/api/annotations/{aid}")
def edit_annotation(aid: str, body: CommentIn, uid: Uid):
    _own_annotation(aid, uid)
    db.update_annotation(aid, body.comment)
    return {"ok": True}


@app.delete("/api/annotations/{aid}")
def remove_annotation(aid: str, uid: Uid):
    _own_annotation(aid, uid)
    db.delete_annotation(aid)
    return {"ok": True}


# ---------------- Workspace ----------------
class NameIn(BaseModel):
    name: str = Field(min_length=1)


class PaperRefIn(BaseModel):
    paper_id: str


@app.get("/api/workspaces")
def workspaces(uid: Uid):
    return db.list_workspaces(uid)


@app.post("/api/workspaces")
def create_workspace(body: NameIn, uid: Uid):
    return db.get_workspace(uid, db.add_workspace(uid, body.name.strip()))


@app.patch("/api/workspaces/{wid}")
def rename_workspace(wid: str, body: NameIn, uid: Uid):
    _ws_or_404(wid, uid)
    db.rename_workspace(wid, body.name.strip())
    return _ws_or_404(wid, uid)


@app.delete("/api/workspaces/{wid}")
def delete_workspace(wid: str, uid: Uid):
    _ws_or_404(wid, uid)
    db.delete_workspace(wid)
    return {"ok": True}


@app.post("/api/workspaces/{wid}/papers")
def add_to_workspace(wid: str, body: PaperRefIn, uid: Uid):
    _ws_or_404(wid, uid)
    _paper_or_404(body.paper_id, uid)
    db.add_to_workspace(wid, body.paper_id)
    return {"ok": True}


@app.delete("/api/workspaces/{wid}/papers/{pid}")
def remove_from_workspace(wid: str, pid: str, uid: Uid):
    _ws_or_404(wid, uid)
    db.remove_from_workspace(wid, pid)
    return {"ok": True}


# ---------------- Workspace wiki（docs/wiki.md）----------------
_wiki_running: set[str] = set()  # shortcut: in-process lock, breaks with multiple uvicorn workers


@app.get("/api/workspaces/{wid}/wiki")
def wiki(wid: str, uid: Uid):
    _ws_or_404(wid, uid)
    return {"pages": db.wiki_pages(wid), "pending": len(db.wiki_pending(wid))}


@app.get("/api/workspaces/{wid}/wiki/{slug}")
def wiki_page(wid: str, slug: str, uid: Uid):
    _ws_or_404(wid, uid)
    page = db.wiki_page(wid, slug)
    if not page:
        raise HTTPException(404, "wiki page not found")
    return page


@app.post("/api/workspaces/{wid}/wiki/update")
async def wiki_update(wid: str, uid: Uid):
    _ws_or_404(wid, uid)
    if wid in _wiki_running:
        raise HTTPException(409, "wiki update already running")
    _wiki_running.add(wid)

    async def run() -> AsyncIterator[str]:
        try:
            async for step in features.update_wiki(wid):
                yield json.dumps(step, ensure_ascii=False)
        finally:
            _wiki_running.discard(wid)

    return sse(run())


@app.get("/api/health")
async def health():
    """檢查每個模型角色的連線：在瀏覽器打開 /api/health 就知道哪個 API 沒接好。
    tasks 列出每個元件實際用的「服務商:模型」；另外指定模型的元件也會各測一次。

    llm   文字（解釋、翻譯、聊天、摘要、標註）
    vlm   看圖（框選圖表、圖表預覽解釋）— 會送一張測試圖
    ocr   掃描頁轉文字（跟 vlm 同一組設定時不重複測）
    embed 語意檢索（沒設就略過，改用 BM25）
    """
    if config.LLM_MOCK:
        return {"ok": True, "mock": True}
    roles = ["llm", "vlm"]
    vlm_id = (config.VLM_BASE_URL, config.VLM_MODEL or config.LLM_MODEL)
    if config.OCR_ENABLED and (config.OCR_BASE_URL, config.OCR_MODEL) != vlm_id:
        roles.append("ocr")
    if config.EMBED_MODEL:
        roles.append("embed")
    # 各元件另外指定的模型：每個不同的模型測一次（用第一個用到它的元件當代表）
    default = llm.route("llm")[::2]
    extra: dict[tuple, str] = {}
    for t in config.TEXT_TASKS:
        key = llm.route(t)[::2]
        if key != default:
            extra.setdefault(key, t)
    roles += list(extra.values())
    results = dict(zip(roles, await asyncio.gather(*(llm.check(r) for r in roles))))
    results["tasks"] = {t: "{}:{}".format(*llm.route(t)[::2]) for t in config.TEXT_TASKS}
    if "ocr" not in results and config.OCR_ENABLED:
        results["ocr"] = {"same_as": "vlm"}
    if "embed" not in results:
        results["embed"] = {"skipped": "沒設 EMBED_MODEL，檢索用 BM25"}
    # 文字模型是必要的；其他壞掉只影響對應功能
    return {"ok": results["llm"]["ok"], "all_ok": all(r.get("ok", True) for r in results.values()),
            **results}


class _FrontendFiles(StaticFiles):
    """前端檔案每次都跟伺服器確認版本（有 ETag，沒改就回 304 不重傳），
    否則瀏覽器會拿快取裡的舊 CSS / JS，改版後要強制重新整理才看得到。"""

    async def get_response(self, path, scope):
        resp = await super().get_response(path, scope)
        resp.headers["Cache-Control"] = "no-cache"
        return resp


# 前端靜態檔：放最後，才不會蓋掉 /api 路由
app.mount("/", _FrontendFiles(directory=config.ROOT / "frontend", html=True), name="frontend")
