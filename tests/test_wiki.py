"""測試 workspace wiki（規格見 docs/wiki.md）。LLM_MOCK：不打模型。"""
from __future__ import annotations

import json

from backend import config, db, main
from tests.conftest import sse


def test_wiki_update(client, bob, pdfs, monkeypatch):
    monkeypatch.setattr(config, "LLM_MOCK", True)
    w = client.post("/api/workspaces", json={"name": "Wiki"}).json()
    base = f"/api/workspaces/{w['id']}/wiki"
    with open(pdfs["numeric"], "rb") as f:
        pid = client.post("/api/papers", files={"file": ("w.pdf", f, "application/pdf")},
                          data={"workspace": w["id"]}).json()["id"]
    assert client.get(base).json() == {"pages": [], "pending": 1, "running": False}

    _, events, err = sse(client, "POST", base + "/update")
    assert err is None
    steps = [json.loads(e) for e in events]
    assert steps[-1]["done"] == steps[-1]["total"] == 1 and all("msg" in s for s in steps)

    r = client.get(base).json()
    slugs = [p["slug"] for p in r["pages"]]
    assert r["pending"] == 0 and slugs[0] == "index"
    assert {f"paper-{pid}", "mock-concept"} <= set(slugs)
    page = client.get(f"{base}/mock-concept").json()
    assert page["sources"] == [pid] and page["markdown"] and page["updated"]
    assert client.get(f"{base}/index").json()["sources"] == [pid]
    assert client.get(f"{base}/nope").status_code == 404

    _, events, _ = sse(client, "POST", base + "/update")  # 沒有新論文：什麼都不做
    assert [json.loads(e)["total"] for e in events] == [0]
    assert [p["updated"] for p in client.get(base).json()["pages"]] == [p["updated"] for p in r["pages"]]

    assert client.get(base).json()["running"] is False
    steps = main._wiki_jobs[w["id"]] = [{"msg": "x", "done": 0, "total": 1}, None]  # 假裝正在跑
    try:
        assert client.get(base).json()["running"] is True
        _, events, _ = sse(client, "POST", base + "/update")  # 接上同一個進度，不另跑一份
        assert [json.loads(e)["msg"] for e in events] == ["x"] and main._wiki_jobs[w["id"]] is steps
    finally:
        main._wiki_jobs.pop(w["id"], None)

    for path in (base, f"{base}/index"):
        assert bob.get(path).status_code == 404
    assert bob.post(base + "/update").status_code == 404

    client.delete(f"/api/papers/{pid}")
    with db.conn() as c:
        assert not c.execute("SELECT 1 FROM wiki_ingested WHERE paper_id=?", (pid,)).fetchall()
    client.delete(f"/api/workspaces/{w['id']}")
    assert db.wiki_pages(w["id"]) == []
