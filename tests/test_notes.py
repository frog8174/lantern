"""論文筆記：每人每篇一份、409 衝突、使用者隔離、AI 擬稿、刪論文連帶刪（規格見 docs/notes-design.md）。"""
from __future__ import annotations

from backend import config, db
from tests import fake_api
from tests.conftest import sse


def test_note_crud_and_conflict(papers, client):
    pid = papers["authoryear"]["id"]
    url = f"/api/papers/{pid}/note"
    assert client.get(url).json() == {"markdown": "", "updated": None}
    first = client.put(url, json={"markdown": "# 第一版", "base_updated": None})
    assert first.status_code == 200
    u1 = first.json()["updated"]
    assert client.get(url).json() == {"markdown": "# 第一版", "updated": u1}
    u2 = client.put(url, json={"markdown": "# 第二版", "base_updated": u1}).json()["updated"]
    assert u2 > u1
    # 拿舊的 updated 再存（另一個分頁）→ 409，回伺服器那份，資料不被蓋掉
    stale = client.put(url, json={"markdown": "舊分頁", "base_updated": u1})
    assert stale.status_code == 409 and stale.json() == {"markdown": "# 第二版", "updated": u2}
    # 已經有筆記還當新的建 → 也是 409，不會多出第二份
    assert client.put(url, json={"markdown": "又一份", "base_updated": None}).status_code == 409
    with db.conn() as c:
        assert c.execute("SELECT COUNT(*) FROM notes WHERE paper_id=?", (pid,)).fetchone()[0] == 1
    assert client.put(url, json={"markdown": "x" * 1_000_001, "base_updated": u2}).status_code == 422


def test_note_private_to_owner(papers, client, bob):
    pid = papers["authoryear"]["id"]
    assert bob.get(f"/api/papers/{pid}/note").status_code == 404
    assert bob.put(f"/api/papers/{pid}/note", json={"markdown": "偷寫", "base_updated": None}).status_code == 404
    assert bob.post(f"/api/papers/{pid}/note/draft").status_code == 404


def test_note_draft(papers, client, monkeypatch):
    pid = papers["numeric"]["id"]
    with monkeypatch.context() as m:  # 其他測試可能已在這篇畫過標註
        m.setattr(db, "list_annotations", lambda pid: [])
        text, _, err = sse(client, "POST", f"/api/papers/{pid}/note/draft")
    assert err is None and "還沒有標註" in text  # 沒素材不打模型
    a = client.post(f"/api/papers/{pid}/annotations",
                    json={"page": 0, "rects": [[0, 0, .1, .1]], "text": "lantern encoder", "comment": "這是重點"}).json()
    fake_api.calls.clear()
    monkeypatch.setattr(db, "list_annotations", lambda pid: [a])  # 只看這則，免得被其他測試的標註擠出預算
    text, _, err = sse(client, "POST", f"/api/papers/{pid}/note/draft")
    assert err is None and text
    prompt = fake_api.calls[-1]["prompt"]
    assert f"[[paper:{pid}#p1@{a['id']}]]" in prompt and "這是重點" in prompt
    monkeypatch.setattr(config, "LLM_MOCK", True)
    text, _, err = sse(client, "POST", f"/api/papers/{pid}/note/draft")
    assert err is None and "MOCK" in text
    client.delete(f"/api/annotations/{a['id']}")


def test_delete_paper_deletes_note(client, pdfs, allow_duplicates):
    with open(pdfs["numeric"], "rb") as f:
        pid = client.post("/api/papers", files={"file": ("tmp.pdf", f, "application/pdf")}).json()["id"]
    client.put(f"/api/papers/{pid}/note", json={"markdown": "會被刪", "base_updated": None})
    client.delete(f"/api/papers/{pid}")
    with db.conn() as c:
        assert c.execute("SELECT COUNT(*) FROM notes WHERE paper_id=?", (pid,)).fetchone()[0] == 0
