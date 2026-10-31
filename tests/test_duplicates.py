"""重複論文（docs/ux-round1.md B3）與卡片處理階段欄位（B2）。"""
from __future__ import annotations

import hashlib

import pymupdf

from backend import db, main


def _upload(client, data: bytes, name: str, ws: str | None = None):
    r = client.post("/api/papers", files={"file": (name, data, "application/pdf")},
                    data={"workspace": ws} if ws else None)
    assert r.status_code == 200, r.text
    return r.json()


def test_same_file_returns_existing(papers, client, pdfs):
    pid = papers["numeric"]["id"]
    before = len(client.get("/api/papers").json())
    r = _upload(client, pdfs["numeric"].read_bytes(), "again.pdf")
    assert r == {"id": pid, "title": "Sparse Lantern Networks for Document Reading", "duplicate": True}
    assert len(client.get("/api/papers").json()) == before
    # 在研究主題裡上傳：加進主題，且排在最前面
    w = client.post("/api/workspaces", json={"name": "dup"}).json()
    other = papers["authoryear"]["id"]
    client.post(f"/api/workspaces/{w['id']}/papers", json={"paper_id": other})
    assert _upload(client, pdfs["numeric"].read_bytes(), "x.pdf", w["id"])["duplicate"] is True
    assert [p["id"] for p in client.get("/api/papers", params={"workspace": w["id"]}).json()] == [pid, other]
    client.delete(f"/api/workspaces/{w['id']}")
    # 別人的庫不算重複
    sha = hashlib.sha256(pdfs["numeric"].read_bytes()).hexdigest()
    assert db.find_duplicate("alice", sha256=sha) == pid and db.find_duplicate("bob", sha256=sha) is None


def test_same_title_different_file(papers, client, pdfs, tmp_path):
    doc = pymupdf.open(pdfs["numeric"])
    doc.set_metadata({"title": "SPARSE lantern networks:  for document-reading"})  # 大小寫、空白、標點不同
    out = tmp_path / "v2.pdf"
    doc.save(out)
    data = out.read_bytes()
    assert data != pdfs["numeric"].read_bytes()
    r = _upload(client, data, "v2.pdf")
    assert r["duplicate"] is True and r["id"] == papers["numeric"]["id"]


def test_find_duplicate_rules(papers):
    pid = papers["authoryear"]["id"]
    db.cache_set(pid, "bib", {"doi": "10.1234/ABC.5"})
    try:
        assert db.find_duplicate("alice", doi="10.1234/abc.5") == pid
        assert db.find_duplicate("bob", doi="10.1234/abc.5") is None
        assert db.find_duplicate("alice", title="Untitled") is None
        assert db.find_duplicate("alice", title="contextual lanterns, for READING") == pid
    finally:
        db.cache_set(pid, "bib", None)


def test_list_has_stage_fields(papers, client):
    pid = papers["numeric"]["id"]
    main._fetching_bib.add(pid)
    try:
        row = next(p for p in client.get("/api/papers").json() if p["id"] == pid)
        assert row["fetching_bib"] is True and row["translating"] is False
    finally:
        main._fetching_bib.discard(pid)
    row = next(p for p in client.get("/api/papers").json() if p["id"] == pid)
    assert row["fetching_bib"] is False
