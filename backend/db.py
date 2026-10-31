"""SQLite 儲存：單一檔案 data/app.db，個人使用夠用了。

資料表：
- papers      ：論文本身（檔名、標題、解析結果 JSON）
- chunks      ：切好的段落 + 向量（給檢索）
- cache       ：LLM 產出的快取（摘要、自動標註、整頁翻譯），避免重複花算力
- annotations ：使用者的螢光筆與註解
- messages    ：每篇論文的聊天紀錄
- users / workspaces / workspace_papers：使用者、各自的 workspace、論文 ↔ workspace（多對多）
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
  id TEXT PRIMARY KEY, user_id TEXT, filename TEXT, title TEXT, created REAL, meta TEXT, tags TEXT DEFAULT '[]'
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
CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT, created REAL);
CREATE TABLE IF NOT EXISTS workspaces (id TEXT PRIMARY KEY, user_id TEXT, name TEXT, created REAL);
CREATE TABLE IF NOT EXISTS workspace_papers (
  workspace_id TEXT, paper_id TEXT, added REAL, PRIMARY KEY (workspace_id, paper_id)
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
        # 測試使用者：user id = 名字
        c.executemany("INSERT OR IGNORE INTO users VALUES (?,?,?)",
                      [(u, u, time.time()) for u in config.TEST_USERS])


def get_user(uid: str) -> dict | None:
    with conn() as c:
        r = c.execute("SELECT id, name FROM users WHERE id=?", (uid,)).fetchone()
    return dict(r) if r else None


def list_users() -> list[dict]:
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT id, name FROM users ORDER BY created, id")]


def new_id() -> str:
    return uuid.uuid4().hex[:12]


# ---------- papers ----------
def add_paper(uid: str, pid: str, filename: str, title: str, meta: dict) -> None:
    with conn() as c:
        c.execute("INSERT INTO papers (id, user_id, filename, title, created, meta) VALUES (?,?,?,?,?,?)",
                  (pid, uid, filename, title, time.time(), json.dumps(meta, ensure_ascii=False)))


def get_paper(pid: str) -> dict | None:
    with conn() as c:
        r = c.execute("SELECT * FROM papers WHERE id=?", (pid,)).fetchone()
    if not r:
        return None
    return {**dict(r), "meta": json.loads(r["meta"]), "tags": json.loads(r["tags"] or "[]")}


def list_papers(uid: str, workspace: str | None = None) -> list[dict]:
    sql = "SELECT p.id, p.filename, p.title, p.created, p.tags FROM papers p "
    args: tuple = (uid,)
    if workspace:
        sql += "JOIN workspace_papers w ON w.paper_id = p.id AND w.workspace_id = ? "
        args = (workspace, uid)
    with conn() as c:
        rows = c.execute(sql + "WHERE p.user_id=? ORDER BY p.created DESC", args).fetchall()
    return [{**dict(r), "tags": json.loads(r["tags"] or "[]")} for r in rows]


def set_tags(pid: str, tags: list[str]) -> None:
    with conn() as c:
        c.execute("UPDATE papers SET tags=? WHERE id=?", (json.dumps(tags, ensure_ascii=False), pid))


def search_chunks(uid: str, q: str, limit: int = 40) -> list[dict]:
    """全文搜尋：在該使用者所有論文的段落裡找關鍵字（英文不分大小寫）。"""
    with conn() as c:
        rows = c.execute(
            "SELECT k.paper_id, k.page, k.text, p.title FROM chunks k JOIN papers p ON p.id = k.paper_id "
            "WHERE p.user_id = ? AND k.text LIKE ? ESCAPE '\\' ORDER BY p.created DESC, k.idx LIMIT ?",
            (uid, "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%", limit),
        ).fetchall()
    return [dict(r) for r in rows]


def delete_paper(pid: str) -> None:
    with conn() as c:
        for t in ("papers", "chunks", "cache", "annotations", "messages"):
            col = "id" if t == "papers" else "paper_id"
            c.execute(f"DELETE FROM {t} WHERE {col}=?", (pid,))
        c.execute("DELETE FROM workspace_papers WHERE paper_id=?", (pid,))


# ---------- workspaces ----------
_WS = ("SELECT w.id, w.name, w.created, COUNT(wp.paper_id) AS count FROM workspaces w "
       "LEFT JOIN workspace_papers wp ON wp.workspace_id = w.id ")


def list_workspaces(uid: str) -> list[dict]:
    with conn() as c:
        rows = c.execute(_WS + "WHERE w.user_id=? GROUP BY w.id ORDER BY w.created DESC", (uid,)).fetchall()
    return [dict(r) for r in rows]


def get_workspace(uid: str, wid: str) -> dict | None:
    with conn() as c:
        r = c.execute(_WS + "WHERE w.user_id=? AND w.id=? GROUP BY w.id", (uid, wid)).fetchone()
    return dict(r) if r else None


def add_workspace(uid: str, name: str) -> str:
    wid = new_id()
    with conn() as c:
        c.execute("INSERT INTO workspaces VALUES (?,?,?,?)", (wid, uid, name, time.time()))
    return wid


def rename_workspace(wid: str, name: str) -> None:
    with conn() as c:
        c.execute("UPDATE workspaces SET name=? WHERE id=?", (name, wid))


def delete_workspace(wid: str) -> None:
    with conn() as c:
        c.execute("DELETE FROM workspaces WHERE id=?", (wid,))
        c.execute("DELETE FROM workspace_papers WHERE workspace_id=?", (wid,))


def add_to_workspace(wid: str, pid: str) -> None:
    with conn() as c:
        c.execute("INSERT OR IGNORE INTO workspace_papers VALUES (?,?,?)", (wid, pid, time.time()))


def remove_from_workspace(wid: str, pid: str) -> None:
    with conn() as c:
        c.execute("DELETE FROM workspace_papers WHERE workspace_id=? AND paper_id=?", (wid, pid))


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


def annotation_paper(aid: str) -> str | None:
    with conn() as c:
        r = c.execute("SELECT paper_id FROM annotations WHERE id=?", (aid,)).fetchone()
    return r["paper_id"] if r else None


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
