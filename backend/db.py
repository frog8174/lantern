"""SQLite 儲存：單一檔案 data/app.db，個人使用夠用了。

資料表：
- papers      ：論文本身（檔名、標題、解析結果 JSON）
- chunks      ：切好的段落 + 向量（給檢索）
- cache       ：LLM 產出的快取（摘要、自動標註、整頁翻譯），避免重複花算力
- annotations ：使用者的螢光筆與註解
- messages    ：每篇論文的聊天紀錄
"""
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from contextlib import contextmanager

from . import config

DB_PATH = config.DATA_DIR / "app.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS papers (
  id TEXT PRIMARY KEY, filename TEXT, title TEXT, created REAL, meta TEXT
);
CREATE TABLE IF NOT EXISTS chunks (
  paper_id TEXT, idx INTEGER, page INTEGER, text TEXT, bbox TEXT, emb BLOB,
  PRIMARY KEY (paper_id, idx)
);
CREATE TABLE IF NOT EXISTS cache (
  paper_id TEXT, kind TEXT, key TEXT, value TEXT, PRIMARY KEY (paper_id, kind, key)
);
CREATE TABLE IF NOT EXISTS annotations (
  id TEXT PRIMARY KEY, paper_id TEXT, page INTEGER, rects TEXT, color TEXT,
  text TEXT, comment TEXT, kind TEXT, created REAL
);
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT, paper_id TEXT, role TEXT, content TEXT, created REAL
);
"""


@contextmanager
def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init() -> None:
    with conn() as c:
        c.executescript(SCHEMA)
        # 舊資料庫升級：papers 加上 tags 欄（JSON 陣列）
        cols = {r["name"] for r in c.execute("PRAGMA table_info(papers)")}
        if "tags" not in cols:
            c.execute("ALTER TABLE papers ADD COLUMN tags TEXT DEFAULT '[]'")


def new_id() -> str:
    return uuid.uuid4().hex[:12]


# ---------- papers ----------
def add_paper(pid: str, filename: str, title: str, meta: dict) -> None:
    with conn() as c:
        c.execute("INSERT INTO papers (id, filename, title, created, meta) VALUES (?,?,?,?,?)",
                  (pid, filename, title, time.time(), json.dumps(meta, ensure_ascii=False)))


def get_paper(pid: str) -> dict | None:
    with conn() as c:
        r = c.execute("SELECT * FROM papers WHERE id=?", (pid,)).fetchone()
    if not r:
        return None
    return {**dict(r), "meta": json.loads(r["meta"]), "tags": json.loads(r["tags"] or "[]")}


def list_papers() -> list[dict]:
    with conn() as c:
        rows = c.execute("SELECT id, filename, title, created, tags FROM papers ORDER BY created DESC").fetchall()
    return [{**dict(r), "tags": json.loads(r["tags"] or "[]")} for r in rows]


def set_tags(pid: str, tags: list[str]) -> None:
    with conn() as c:
        c.execute("UPDATE papers SET tags=? WHERE id=?", (json.dumps(tags, ensure_ascii=False), pid))


def search_chunks(q: str, limit: int = 40) -> list[dict]:
    """全文搜尋：在所有論文的段落裡找關鍵字（英文不分大小寫）。"""
    with conn() as c:
        rows = c.execute(
            "SELECT k.paper_id, k.page, k.text, p.title FROM chunks k JOIN papers p ON p.id = k.paper_id "
            "WHERE k.text LIKE ? ESCAPE '\\' ORDER BY p.created DESC, k.idx LIMIT ?",
            ("%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%", limit),
        ).fetchall()
    return [dict(r) for r in rows]


def delete_paper(pid: str) -> None:
    with conn() as c:
        for t in ("papers", "chunks", "cache", "annotations", "messages"):
            col = "id" if t == "papers" else "paper_id"
            c.execute(f"DELETE FROM {t} WHERE {col}=?", (pid,))


# ---------- chunks ----------
def save_chunks(pid: str, chunks: list[dict]) -> None:
    with conn() as c:
        c.executemany(
            "INSERT OR REPLACE INTO chunks VALUES (?,?,?,?,?,?)",
            [(pid, i, ch["page"], ch["text"], json.dumps(ch["bbox"]), ch.get("emb")) for i, ch in enumerate(chunks)],
        )


def load_chunks(pid: str) -> list[dict]:
    with conn() as c:
        rows = c.execute("SELECT * FROM chunks WHERE paper_id=? ORDER BY idx", (pid,)).fetchall()
    return [{"idx": r["idx"], "page": r["page"], "text": r["text"],
             "bbox": json.loads(r["bbox"]), "emb": r["emb"]} for r in rows]


# ---------- cache ----------
def cache_get(pid: str, kind: str, key: str = ""):
    with conn() as c:
        r = c.execute("SELECT value FROM cache WHERE paper_id=? AND kind=? AND key=?", (pid, kind, key)).fetchone()
    return json.loads(r["value"]) if r else None


def cache_set(pid: str, kind: str, value, key: str = "") -> None:
    with conn() as c:
        c.execute("INSERT OR REPLACE INTO cache VALUES (?,?,?,?)",
                  (pid, kind, key, json.dumps(value, ensure_ascii=False)))


# ---------- annotations ----------
def add_annotation(pid: str, a: dict) -> dict:
    a = {"id": new_id(), "created": time.time(), "comment": "", "kind": "user", **a}
    with conn() as c:
        c.execute("INSERT INTO annotations VALUES (?,?,?,?,?,?,?,?,?)",
                  (a["id"], pid, a["page"], json.dumps(a["rects"]), a.get("color", "yellow"),
                   a.get("text", ""), a["comment"], a["kind"], a["created"]))
    return a


def list_annotations(pid: str) -> list[dict]:
    with conn() as c:
        rows = c.execute("SELECT * FROM annotations WHERE paper_id=? ORDER BY page, created", (pid,)).fetchall()
    return [{**dict(r), "rects": json.loads(r["rects"])} for r in rows]


def update_annotation(aid: str, comment: str) -> None:
    with conn() as c:
        c.execute("UPDATE annotations SET comment=? WHERE id=?", (comment, aid))


def delete_annotation(aid: str) -> None:
    with conn() as c:
        c.execute("DELETE FROM annotations WHERE id=?", (aid,))


# ---------- messages ----------
def add_message(pid: str, role: str, content: str) -> None:
    with conn() as c:
        c.execute("INSERT INTO messages (paper_id, role, content, created) VALUES (?,?,?,?)",
                  (pid, role, content, time.time()))


def list_messages(pid: str, limit: int = 50) -> list[dict]:
    with conn() as c:
        rows = c.execute("SELECT role, content FROM messages WHERE paper_id=? ORDER BY id DESC LIMIT ?",
                         (pid, limit)).fetchall()
    return [dict(r) for r in reversed(rows)]


def clear_messages(pid: str) -> None:
    with conn() as c:
        c.execute("DELETE FROM messages WHERE paper_id=?", (pid,))
