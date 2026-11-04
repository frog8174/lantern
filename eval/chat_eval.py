"""聊天策略評估：full（第一題送整篇）vs auto（段落累積式 RAG），比答案品質和實際花費。docs/chat-rag.md

用法：uv run python -m eval.chat_eval [論文篇數，預設 4]
- 會花真錢（4 篇約 $1）：出題、兩種策略各跑一輪、評分都呼叫 Claude。
- 題目存在 eval/questions.json、作答存在 eval/answers.json，第二次起沿用；要重新作答就刪掉 answers.json。
- 花費從 llm_usage 表讀（eval-full / eval-auto / eval-judge 三個假使用者），結果寫到 eval/results/。
- 每篇論文是一段連續對話（5 題：細節、追問、細節、整篇、追問），題與題之間沒有停頓，
  所以 full 的快取一直是熱的 —— 這是對 full 最有利的情境；冷啟動的差距看第 1 題的花費。
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
import time
from pathlib import Path

from backend import config, db, features, llm

HERE = Path(__file__).parent
QFILE = HERE / "questions.json"
JUDGE = "anthropic:claude-sonnet-5-5"
STRATEGIES = ("full", "auto")
ORDER = ("local", "followup", "local", "global", "followup")  # 出題要求的順序；模型漏寫 type 時照位置補
AFILE = HERE / "answers.json"  # 作答結果先存檔：評分出錯時重跑不用再付作答的錢
_CJK = re.compile(r"[一-鿿]")
RUN = time.strftime("%Y%m%d-%H%M%S")  # 加進系統提示：每輪都冷啟動，不會讀到上一輪留下的快取（第一次評估就被這個污染過）


def pick_papers(n: int) -> list[dict]:
    with db.conn() as c:
        rows = c.execute("SELECT id FROM papers ORDER BY created").fetchall()
    out, seen = [], set()
    for (pid,) in rows:
        p = db.get_paper(pid)
        title = p["meta"]["title"] or ""
        if title in seen or _CJK.search(title) or p["meta"].get("ocr_pages") or not features.full_text_fits(p):
            continue
        if not 5 <= p["meta"]["num_pages"] <= 25:
            continue
        seen.add(title)
        out.append(p)
    return out[:n]


async def make_questions(p: dict) -> list[dict]:
    full = features._pages_text(p, range(p["meta"]["num_pages"]))
    data = await llm.complete_json([{"role": "user", "content":
        f"{full}\n\n---\n你要出一組題目，測試「陪讀論文的聊天助理」答得對不對。依序出 5 題，模擬一個研究生連續提問（繁體中文）：\n"
        "1. local：問一個具體細節（資料集、數字、設定、某個元件怎麼做）\n"
        "2. followup：接著第 1 題追問，用「它」「那個」之類的代名詞，不重複主詞\n"
        "3. local：另一個具體細節，答案在不同頁\n"
        "4. global：問整篇的事（主要貢獻、整體流程、優缺點）\n"
        "5. followup：接著第 4 題追問細節\n"
        "每題附上參考答案（根據論文、2～4 句）和答案所在頁碼。只輸出 JSON：\n"
        '{"turns": [{"q": "...", "type": "local", "answer": "...", "pages": [3]}]}'}],
        task="eval", max_tokens=4000)
    return data["turns"]


async def run_conversation(p: dict, turns: list[dict], strategy: str) -> list[dict]:
    llm.usage_ctx.set((f"eval-{strategy}", p["id"]))
    history, out = [], []
    for t in turns:
        msgs, ctx = await features.chat_messages(p, history, t["q"], None, strategy)
        msgs[0] = msgs[0] | {"content": msgs[0]["content"] + f"
（評估批次 {RUN}）"}
        t0 = time.time()
        answer = await llm.complete(msgs, task="chat")
        mode = "full" if ctx == features.FULL else "summary" if ctx.startswith("【論文整理】") else "rag" if ctx else "(none)"
        out.append({"answer": answer, "ctx_mode": mode, "ctx_chars": len(ctx), "secs": round(time.time() - t0, 1)})
        history += [{"role": "user", "content": t["q"], "ctx": ctx}, {"role": "assistant", "content": answer}]
    return out


async def judge(turns: list[dict], i: int, answer: str) -> dict:
    t = turns[i]
    before = f"（前一題：{turns[i - 1]['q']}；參考答案：{turns[i - 1]['answer']}）\n" if t["type"] == "followup" else ""
    data = await llm.complete_json([{"role": "user", "content":
        f"{before}問題：{t['q']}\n參考答案：{t['answer']}（第 {t['pages']} 頁）\n\n受評答案：\n{answer}\n\n---\n"
        "依參考答案評分：2＝正確且涵蓋重點；1＝部分正確或漏了重點；0＝錯誤、答非所問，或說論文沒提到但其實有。\n"
        '只輸出 JSON：{"score": 2, "reason": "一句話"}'}], task="eval", max_tokens=300)
    return data if isinstance(data, dict) and data.get("score") in (0, 1, 2) else {"score": 0, "reason": "評分失敗"}


def costs(since: float) -> dict:
    with db.conn() as c:
        rows = c.execute("SELECT user_id, task, COUNT(*) n, SUM(cost) cost, SUM(input) i, SUM(cache_write) w, "
                         "SUM(cache_read) r, SUM(output) o FROM llm_usage WHERE ts>=? AND user_id LIKE 'eval-%' "
                         "GROUP BY user_id, task", (since,)).fetchall()
    return {f"{r['user_id']}/{r['task']}": dict(r) for r in rows}


async def main(n: int) -> None:
    db.init()
    config.TASK_MODELS["eval"] = JUDGE
    config.TASK_EFFORT["eval"] = "low"
    since = time.time()
    papers = pick_papers(n)
    qs = json.loads(QFILE.read_text(encoding="utf-8")) if QFILE.exists() else {}
    llm.usage_ctx.set(("eval-judge", None))
    for p in papers:
        if p["id"] not in qs:
            print("出題：", p["meta"]["title"][:60])
            qs[p["id"]] = {"title": p["meta"]["title"], "turns": await make_questions(p)}
    for v in qs.values():
        for i, t in enumerate(v["turns"]):
            t.setdefault("type", ORDER[i] if i < len(ORDER) else "local")
    QFILE.write_text(json.dumps(qs, ensure_ascii=False, indent=1), encoding="utf-8")

    results: dict = json.loads(AFILE.read_text(encoding="utf-8")) if AFILE.exists() else {}
    for s in STRATEGIES:
        todo = [p for p in papers if p["id"] not in results.get(s, {})]
        if todo:
            print("作答：", s, len(todo), "篇")
            answers = await asyncio.gather(*(run_conversation(p, qs[p["id"]]["turns"], s) for p in todo))
            results.setdefault(s, {}).update(zip([p["id"] for p in todo], answers))
            AFILE.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    llm.usage_ctx.set(("eval-judge", None))
    print("評分")
    for s in STRATEGIES:
        for p in papers:
            turns = qs[p["id"]]["turns"]
            scores = await asyncio.gather(*(judge(turns, i, a["answer"]) for i, a in enumerate(results[s][p["id"]])))
            for a, sc in zip(results[s][p["id"]], scores):
                a |= sc | {"cites": bool(re.search(r"\[p\.\d+\]", a["answer"]))}

    report = render(papers, qs, results, costs(since))
    out = HERE / "results" / time.strftime("%Y%m%d-%H%M")
    out.parent.mkdir(exist_ok=True)
    out.with_suffix(".md").write_text(report, encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps({"questions": qs, "results": results}, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
    print(report)
    print("寫到", out.with_suffix(".md"))


def render(papers, qs, results, cost) -> str:
    lines = [f"# 聊天策略評估 {time.strftime('%Y-%m-%d %H:%M')}", "",
             f"{len(papers)} 篇論文 × 5 題連續對話；作答模型 {config.TASK_MODELS.get('chat') or config.LLM_MODEL}，評分 {JUDGE}。", "",
             "## 總表", "", "| 策略 | 平均分（0–2） | 有標頁碼 | 作答花費 | 每題花費 |", "|---|---|---|---|---|"]
    for s in STRATEGIES:
        ans = [a for p in papers for a in results[s][p["id"]]]
        spend = sum(v["cost"] for k, v in cost.items() if k.startswith(f"eval-{s}/"))
        lines.append(f"| {s} | {sum(a['score'] for a in ans) / len(ans):.2f} | {sum(a['cites'] for a in ans)}/{len(ans)} "
                     f"| ${spend:.4f} | ${spend / len(ans):.4f} |")
    lines += ["", "## 依題型平均分", "", "| 題型 | " + " | ".join(STRATEGIES) + " |", "|---|" + "---|" * len(STRATEGIES)]
    for typ in ("local", "followup", "global"):
        row = []
        for s in STRATEGIES:
            sc = [a["score"] for p in papers for t, a in zip(qs[p["id"]]["turns"], results[s][p["id"]]) if t["type"] == typ]
            row.append(f"{sum(sc) / len(sc):.2f}（{len(sc)} 題）" if sc else "–")
        lines.append(f"| {typ} | " + " | ".join(row) + " |")
    lines += ["", "## 花費明細（llm_usage）", "", "| 使用者/功能 | 次數 | 花費 | 輸入 | 快取寫 | 快取讀 | 輸出 |", "|---|---|---|---|---|---|---|"]
    for k, v in sorted(cost.items()):
        lines.append(f"| {k} | {v['n']} | ${v['cost']:.4f} | {v['i']} | {v['w']} | {v['r']} | {v['o']} |")
    lines += ["", "## 逐題", ""]
    for p in papers:
        lines += [f"### {qs[p['id']]['title'][:80]}", "", "| # | 題型 | 問題 | " + " | ".join(STRATEGIES) + " |",
                  "|---|---|---|" + "---|" * len(STRATEGIES)]
        for i, t in enumerate(qs[p["id"]]["turns"]):
            cells = [f"{results[s][p['id']][i]['score']}（{results[s][p['id']][i]['ctx_mode']}）" for s in STRATEGIES]
            lines.append(f"| {i + 1} | {t['type']} | {t['q'][:50]} | " + " | ".join(cells) + " |")
        lines.append("")
    lines += ["## 扣分原因", ""]
    for s in STRATEGIES:
        for p in papers:
            for i, a in enumerate(results[s][p["id"]]):
                if a["score"] < 2:
                    lines.append(f"- {s} · {qs[p['id']]['title'][:30]} 第 {i + 1} 題（{a['score']}）：{a['reason']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else 4))
