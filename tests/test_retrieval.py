"""檢索：參考文獻區不進候選、reranker 決定名次、reranker 掛了退回混合分數。"""
from __future__ import annotations

import asyncio

from backend import config, db, llm, retrieval
from backend.pdf_parse import Block

TEXTS = ["Introduction lantern encoder overview", "Method lantern encoder loss function",
         "Results lantern encoder accuracy table", "References", "[1] Smith lantern encoder 2020",
         "A Proofs of the lantern encoder bound"]


def _setup():
    blocks = [Block(page=i, text=t, bbox=[0, 0, 1, 1], size=10) for i, t in enumerate(TEXTS)]
    chunks = retrieval.make_chunks(blocks)
    db.save_chunks("rt-paper", chunks)
    db.cache_set("rt-paper", "embed_model", "none")  # 不是目前的 EMBED_MODEL → 只用 BM25，不打 embedding


def test_refs_excluded_and_rerank_orders(monkeypatch):
    _setup()
    monkeypatch.setattr(config, "RERANK_MODEL", "r")
    seen = {}

    async def fake_rerank(q, docs):
        seen["docs"] = docs
        return [1.0 if "Results" in d else 0.1 for d in docs]

    monkeypatch.setattr(llm, "rerank", fake_rerank)
    hits = asyncio.run(retrieval.search("rt-paper", "lantern encoder", k=1))
    assert not any(d.startswith(("References", "[1]")) for d in seen["docs"])  # 參考文獻區被拿掉
    assert any(d.startswith("A Proofs") for d in seen["docs"])                # 附錄還在
    assert [h["text"] for h in hits] == ["Results lantern encoder accuracy table"]


def test_rerank_failure_falls_back(monkeypatch):
    _setup()
    monkeypatch.setattr(config, "RERANK_MODEL", "r")

    async def broken(q, docs):
        raise RuntimeError("down")

    monkeypatch.setattr(llm, "rerank", broken)
    assert len(asyncio.run(retrieval.search("rt-paper", "lantern encoder", k=2))) == 2
