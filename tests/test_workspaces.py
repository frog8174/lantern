"""測試登入、使用者之間的範圍限制、workspace（規格見 docs/workspaces.md）。"""
from __future__ import annotations

from fastapi.testclient import TestClient

from backend import config
from backend.main import app


def test_login_required(fake_server, monkeypatch):
    monkeypatch.setattr(config, "LLM_MOCK", True)  # health 不連模型：別的事件迴圈會弄壞 llm 快取的連線
    with TestClient(app) as anon:
        assert anon.get("/api/papers").status_code == 401
        assert anon.get("/api/me").status_code == 401
        assert anon.get("/api/health").status_code == 200
        assert anon.post("/api/auth/login", json={"user_id": "mallory"}).status_code == 401
        users = anon.get("/api/auth/users").json()
        assert {"id": "alice", "name": "alice"} in users and {"id": "bob", "name": "bob"} in users
        anon.cookies.set("uid", "mallory")  # 偽造不存在的使用者
        assert anon.get("/api/papers").status_code == 401


def test_me_and_logout(fake_server):
    with TestClient(app) as c:
        assert c.post("/api/auth/login", json={"user_id": "bob"}).json() == {"id": "bob", "name": "bob"}
        assert c.get("/api/me").json() == {"id": "bob", "name": "bob"}
        assert c.post("/api/auth/logout").json() == {"ok": True}
        assert c.get("/api/me").status_code == 401


def test_users_isolated(papers, client, bob):
    pid = papers["numeric"]["id"]
    assert client.get(f"/api/papers/{pid}").status_code == 200
    for path in (f"/api/papers/{pid}", f"/api/papers/{pid}/pdf", f"/api/papers/{pid}/chat",
                 f"/api/papers/{pid}/annotations"):
        assert bob.get(path).status_code == 404, path
    assert bob.delete(f"/api/papers/{pid}").status_code == 404
    assert all(p["id"] != pid for p in bob.get("/api/papers").json())
    assert client.get("/api/search", params={"q": "lantern encoder"}).json()
    assert bob.get("/api/search", params={"q": "lantern encoder"}).json() == []
    a = client.post(f"/api/papers/{pid}/annotations", json={"page": 0, "rects": []}).json()
    assert bob.patch(f"/api/annotations/{a['id']}", json={"comment": "x"}).status_code == 404
    assert bob.delete(f"/api/annotations/{a['id']}").status_code == 404
    client.delete(f"/api/annotations/{a['id']}")


def test_workspace_crud(papers, client, bob):
    p1, p2 = papers["numeric"]["id"], papers["authoryear"]["id"]
    a = client.post("/api/workspaces", json={"name": "NLP"}).json()
    b = client.post("/api/workspaces", json={"name": "Vision"}).json()
    assert a["name"] == "NLP" and a["count"] == 0 and a["created"]
    assert client.post("/api/workspaces", json={"name": ""}).status_code == 422
    for wid in (a["id"], b["id"]):
        assert client.post(f"/api/workspaces/{wid}/papers", json={"paper_id": p1}).json() == {"ok": True}
    client.post(f"/api/workspaces/{a['id']}/papers", json={"paper_id": p1})  # 重複加入不報錯
    client.post(f"/api/workspaces/{a['id']}/papers", json={"paper_id": p2})

    ws = {w["id"]: w for w in client.get("/api/workspaces").json()}
    assert list(ws)[:2] == [b["id"], a["id"]]  # 新到舊
    assert ws[a["id"]]["count"] == 2 and ws[b["id"]]["count"] == 1
    ids = lambda wid: [p["id"] for p in client.get("/api/papers", params={"workspace": wid}).json()]
    assert set(ids(a["id"])) == {p1, p2} and ids(b["id"]) == [p1]
    assert {p1, p2} <= {p["id"] for p in client.get("/api/papers").json()}

    r = client.patch(f"/api/workspaces/{a['id']}", json={"name": "NLP 2"}).json()
    assert r["name"] == "NLP 2" and r["count"] == 2
    assert client.delete(f"/api/workspaces/{a['id']}/papers/{p2}").json() == {"ok": True}
    assert ids(a["id"]) == [p1]

    # 別人的 workspace → 404
    assert bob.get("/api/workspaces").json() == []
    assert bob.get("/api/papers", params={"workspace": a["id"]}).status_code == 404
    assert bob.patch(f"/api/workspaces/{a['id']}", json={"name": "x"}).status_code == 404
    assert bob.delete(f"/api/workspaces/{a['id']}").status_code == 404
    mine = bob.post("/api/workspaces", json={"name": "bob's"}).json()
    assert bob.post(f"/api/workspaces/{a['id']}/papers", json={"paper_id": p1}).status_code == 404
    assert bob.post(f"/api/workspaces/{mine['id']}/papers", json={"paper_id": p1}).status_code == 404  # 別人的論文
    assert client.post(f"/api/workspaces/{mine['id']}/papers", json={"paper_id": p1}).status_code == 404

    # 刪 workspace，論文還在
    for wid in (a["id"], b["id"]):
        assert client.delete(f"/api/workspaces/{wid}").json() == {"ok": True}
    assert client.get(f"/api/papers/{p1}").status_code == 200
    assert client.get("/api/papers", params={"workspace": a["id"]}).status_code == 404
    bob.delete(f"/api/workspaces/{mine['id']}")


def test_upload_into_workspace(client, bob, pdfs):
    w = client.post("/api/workspaces", json={"name": "inbox"}).json()
    path = pdfs["numeric"]
    with open(path, "rb") as f:
        r = client.post("/api/papers", files={"file": (path.name, f, "application/pdf")}, data={"workspace": w["id"]})
    pid = r.json()["id"]
    assert [p["id"] for p in client.get("/api/papers", params={"workspace": w["id"]}).json()] == [pid]
    with open(path, "rb") as f:  # 上傳到別人的 workspace → 404
        assert bob.post("/api/papers", files={"file": (path.name, f, "application/pdf")},
                        data={"workspace": w["id"]}).status_code == 404
    client.delete(f"/api/papers/{pid}")  # 刪論文也清掉 workspace 關聯
    assert client.get("/api/workspaces").json()[0]["count"] == 0
    client.delete(f"/api/workspaces/{w['id']}")


def test_auto_translate_setting(client, pdfs):
    import time
    from backend import db
    assert client.get("/api/me/settings").json() == {"auto_translate": False}
    assert client.put("/api/me/settings", json={"auto_translate": True}).json() == {"auto_translate": True}
    try:
        pid = client.post("/api/papers", files={"file": ("n.pdf", pdfs["numeric"].read_bytes(), "application/pdf")}).json()["id"]
        for _ in range(100):  # 背景任務在 app 的事件迴圈裡跑
            if db.cache_get(pid, "block_translation", "0"):
                break
            time.sleep(0.1)
        assert any(b.get("tr") for b in db.cache_get(pid, "block_translation", "0"))
        row = next(p for p in client.get("/api/papers").json() if p["id"] == pid)
        assert row["tr_done"] >= 1 and row["tr_total"] >= row["tr_done"] and "translating" in row
        client.delete(f"/api/papers/{pid}")
    finally:
        client.put("/api/me/settings", json={"auto_translate": False})
