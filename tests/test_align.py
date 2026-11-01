"""中英對齊（/align）：螢光筆同步到譯文。模型回答用 monkeypatch 指定。"""
from __future__ import annotations

from backend import db, llm
from tests.conftest import sse


P = 1  # 用第 2 頁：第 1 頁的快取留給 test_api 的對照翻譯測試


def _translated_block(client, pid: str) -> tuple[int, dict]:
    _, events, _ = sse(client, "POST", f"/api/papers/{pid}/translate-blocks", {"page": P})
    blocks = db.cache_get(pid, "block_translation", str(P))
    assert blocks, events
    return next((i, b) for i, b in enumerate(blocks) if b.get("tr"))


def _fake(monkeypatch, answer: str) -> None:
    async def complete(messages, **kw):
        return answer
    monkeypatch.setattr(llm, "complete", complete)


def test_align_valid_substring(papers, client, monkeypatch):
    pid = papers["numeric"]["id"]
    i, b = _translated_block(client, pid)
    want = b["tr"][:3]
    _fake(monkeypatch, f"「{want}」\n")
    r = client.post(f"/api/papers/{pid}/align", json={"page": P, "block": i, "quote": b["text"][:20]})
    assert r.status_code == 200 and r.json() == {"match": want, "fallback": False}
    # 反向：中文 → 英文，回傳英文原句在頁上的位置
    en = b["text"].split()[0]
    _fake(monkeypatch, en)
    r = client.post(f"/api/papers/{pid}/align", json={"page": P, "block": i, "quote": want, "direction": "zh2en"}).json()
    assert r["match"] == en and r["rects"] and all(len(x) == 4 for x in r["rects"])


def test_align_invalid_falls_back(papers, client, monkeypatch):
    pid = papers["numeric"]["id"]
    i, b = _translated_block(client, pid)
    _fake(monkeypatch, "模型改寫過、原文裡沒有的句子")
    r = client.post(f"/api/papers/{pid}/align", json={"page": P, "block": i, "quote": "zzz unique quote"}).json()
    assert r == {"match": "", "fallback": True}
    r = client.post(f"/api/papers/{pid}/align",
                    json={"page": P, "block": i, "quote": "zzz 中文", "direction": "zh2en"}).json()
    assert r["fallback"] and r["rects"] == [b["bbox"]]  # 找不到就標整個區塊
    # 還沒翻譯的頁 / 區塊
    assert client.post(f"/api/papers/{pid}/align", json={"page": P, "block": 9999, "quote": "x"}).status_code == 409


def test_align_scoped_to_owner(papers, client, bob):
    pid = papers["numeric"]["id"]
    i, _ = _translated_block(client, pid)
    assert bob.post(f"/api/papers/{pid}/align", json={"page": P, "block": i, "quote": "x"}).status_code == 404


def test_annotation_keeps_align(papers, client):
    pid = papers["numeric"]["id"]
    a = client.post(f"/api/papers/{pid}/annotations", json={"page": 0, "rects": [[0.1, 0.1, 0.3, 0.12]], "text": "x"}).json()
    assert a["align"] is None
    client.patch(f"/api/annotations/{a['id']}", json={"align": {"block": 2, "zh": "譯文"}})
    got = next(x for x in client.get(f"/api/papers/{pid}/annotations").json() if x["id"] == a["id"])
    assert got["align"] == {"block": 2, "zh": "譯文"} and got["comment"] == ""
    client.delete(f"/api/annotations/{a['id']}")
