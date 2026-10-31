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


def test_wiki_ask_and_backlinks(client, bob, pdfs, monkeypatch):
    monkeypatch.setattr(config, "LLM_MOCK", True)
    w = client.post("/api/workspaces", json={"name": "Ask"}).json()
    ask = f"/api/workspaces/{w['id']}/ask"
    with open(pdfs["numeric"], "rb") as f:
        pid = client.post("/api/papers", files={"file": ("a.pdf", f, "application/pdf")},
                          data={"workspace": w["id"]}).json()["id"]
    assert client.post(ask, json={"question": "q"}).status_code == 400  # wiki 還沒有頁面
    sse(client, "POST", f"/api/workspaces/{w['id']}/wiki/update")

    text, _, err = sse(client, "POST", ask, {"question": "這篇在做什麼？"})
    assert err is None and text
    hist = client.get(ask).json()
    assert [(m["role"], m["content"]) for m in hist] == [("user", "這篇在做什麼？"), ("assistant", text)]
    sse(client, "POST", ask, {"question": "第二題"})
    assert bob.delete(f"{ask}/{hist[0]['id']}").status_code == 404
    assert client.delete(f"{ask}/{hist[0]['id']}").json() == {"ok": True}  # 只刪第一題（問題 + 回答）
    assert [m["content"] for m in client.get(ask).json() if m["role"] == "user"] == ["第二題"]
    assert client.delete(f"{ask}/{hist[0]['id']}").status_code == 404
    assert client.delete(ask).json() == {"ok": True} and client.get(ask).json() == []

    r = client.post(ask + "/save", json={"question": "Q", "answer": f"A [[paper:{pid}#p1]] [[paper:zzz#p2]]"}).json()
    assert r["slug"].startswith("qa-") and r["title"]
    assert client.get(f"/api/workspaces/{w['id']}/wiki/{r['slug']}").json()["sources"] == [pid]

    links = client.get(f"/api/papers/{pid}/wiki").json()
    assert links[0] == {"workspace_id": w["id"], "workspace_name": "Ask", "slug": f"paper-{pid}", "title": "MOCK 論文頁"}
    assert {"index", "mock-concept", r["slug"]} <= {x["slug"] for x in links}

    assert bob.get(f"/api/papers/{pid}/wiki").status_code == 404
    assert bob.get(ask).status_code == 404 and bob.delete(ask).status_code == 404
    assert bob.post(ask, json={"question": "q"}).status_code == 404
    assert bob.post(ask + "/save", json={"question": "q", "answer": "a"}).status_code == 404
    client.delete(f"/api/workspaces/{w['id']}")
    assert db.list_wiki_messages(w["id"]) == [] and client.get(f"/api/papers/{pid}/wiki").json() == []
    client.delete(f"/api/papers/{pid}")


def test_auto_wiki(client, papers, monkeypatch):
    import time
    monkeypatch.setattr(config, "LLM_MOCK", True)
    client.put("/api/me/settings", json={"auto_wiki": True})
    try:
        w = client.post("/api/workspaces", json={"name": "Auto"}).json()
        client.post(f"/api/workspaces/{w['id']}/papers", json={"paper_id": papers["numeric"]["id"]})
        for _ in range(100):  # 背景任務在 app 的事件迴圈裡跑
            if not db.wiki_pending(w["id"]) and w["id"] not in main._wiki_jobs:
                break
            time.sleep(0.1)
        assert db.wiki_pending(w["id"]) == [] and db.wiki_page(w["id"], "index")
        client.delete(f"/api/workspaces/{w['id']}")
    finally:
        client.put("/api/me/settings", json={"auto_wiki": False})
