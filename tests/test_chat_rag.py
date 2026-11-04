"""聊天的段落累積式 RAG（docs/chat-rag.md）：送過的段落不重送、追問改寫、全篇問題分流、第 8 題改全文。"""
from __future__ import annotations

import asyncio

import pytest

from backend import config, db, features, retrieval

PAPER = {"id": "chat-rag-paper", "meta": {"title": "Lantern", "abstract": "A lantern encoder.", "num_pages": 2,
                                          "pages": ["Page one text about the encoder. " * 100, "Page two results. " * 100]}}
HITS = [{"page": 0, "idx": 0, "text": "The lantern encoder uses sparse attention."},
        {"page": 1, "idx": 1, "text": "Accuracy improves by 3 points."}]


@pytest.fixture
def fake(monkeypatch):
    monkeypatch.setattr(config, "LLM_CONTEXT_TOKENS", 100_000)  # 測試設定刻意很小；這裡要「全文放得下」
    calls = {"plan": [], "search": []}

    async def plan(history, question):
        calls["plan"].append(question)
        return {"query": "lantern encoder drawbacks" if "缺點" in question else question,
                "scope": "global" if "貢獻" in question else "local"}

    async def search(pid, query, k=6):
        calls["search"].append(query)
        return HITS

    monkeypatch.setattr(features, "plan_question", plan)
    monkeypatch.setattr(retrieval, "search", search)
    db.cache_set(PAPER["id"], "summary", "")  # 預設沒有整理
    return calls


def run(history, q, page=None, strategy=None):
    return asyncio.run(features.chat_messages(PAPER, history, q, page, strategy))


def test_passages_accumulate_without_resending(fake):
    msgs, ctx1 = run([], "encoder 怎麼運作？")
    assert "sparse attention" in ctx1 and msgs[-1]["content"].endswith("問題：encoder 怎麼運作？")
    hist = [{"role": "user", "content": "encoder 怎麼運作？", "ctx": ctx1}, {"role": "assistant", "content": "答"}]
    msgs2, ctx2 = run(hist, "那它的缺點呢？")
    assert ctx2 == ""                                   # 同樣的段落已經送過，不重送
    assert fake["search"][-1] == "lantern encoder drawbacks"  # 追問用改寫後的檢索句
    assert msgs2[3]["content"] == msgs[3]["content"]    # 前一題原封不動 → 對話前綴不變，快取接得上


def test_current_page_sent_once(fake):
    _, ctx = run([], "這頁在說什麼？", page=1)
    assert "=== 第 2 頁 ===" in ctx
    _, again = run([{"role": "user", "content": "q", "ctx": ctx}, {"role": "assistant", "content": "a"}], "還有呢？", page=1)
    assert "=== 第 2 頁 ===" not in again


def test_global_question_uses_summary_then_full(fake):
    db.cache_set(PAPER["id"], "summary", "## 一句話總結\n燈籠編碼器")
    _, ctx = run([], "主要貢獻是什麼？")
    assert ctx.startswith("【論文整理】") and not fake["search"]
    db.cache_set(PAPER["id"], "summary", "")
    _, ctx = run([], "主要貢獻是什麼？")
    assert ctx == features.FULL                        # 沒有整理：改送整篇


def test_switches_to_full_text_after_many_turns(fake):
    hist = []
    for i in range(features.FULL_AFTER_TURNS - 1):
        hist += [{"role": "user", "content": f"q{i}", "ctx": ""}, {"role": "assistant", "content": "a"}]
    msgs, ctx = run(hist, "再一題")
    assert ctx == features.FULL and "Page two results." in msgs[-1]["content"]
    _, after = run(hist + [{"role": "user", "content": "再一題", "ctx": ctx}, {"role": "assistant", "content": "a"}], "還有")
    assert after == "" and len(fake["plan"]) == 0      # 全文已在前面：不再改寫、不再檢索


def test_full_strategy_matches_old_behaviour(fake):
    _, ctx = run([], "encoder 怎麼運作？", strategy="full")
    assert ctx == features.FULL and not fake["plan"]


def test_endpoint_stores_ctx(papers, client):
    pid = papers["numeric"]["id"]
    client.delete(f"/api/papers/{pid}/chat")
    from tests.conftest import sse
    sse(client, "POST", f"/api/papers/{pid}/chat", {"question": "What is the lantern encoder?", "page": 0})
    hist = db.list_messages(pid, ctx=True)
    assert hist[0]["role"] == "user" and hist[0]["ctx"]           # 附了什麼存起來，下一題才能原樣重組
    assert "ctx" not in client.get(f"/api/papers/{pid}/chat").json()[0]  # 前端拿不到
