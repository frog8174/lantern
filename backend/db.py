"""SQLite 儲存：單一檔案 data/app.db，個人使用夠用了。

資料表：
- papers      ：論文本身（檔名、標題、解析結果 JSON）
- chunks      ：切好的段落 + 向量（給檢索）
- cache       ：LLM 產出的快取（摘要、自動標註、整頁翻譯），避免重複花算力
- annotations ：使用者的螢光筆與註解
- messages    ：每篇論文的聊天紀錄
- users / workspaces / workspace_papers：使用者、各自的 workspace、論文 ↔ workspace（多對多）
- wiki_pages / wiki_ingested / wiki_messages：workspace 的 LLM wiki 頁面、已整理過的論文、wiki 問答紀錄（規格見 docs/wiki.md）
- notes       ：使用者自己寫的論文筆記，每人每篇一份（規格見 docs/notes-design.md）
"""
from __future__ import annotations

import json
from collections import Counter
import re
import sqlite3
import time
import uuid
from contextlib import contextmanager

from . import config

DB_PATH = config.DATA_DIR / "app.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS papers (
  id TEXT PRIMARY KEY, user_id TEXT, filename TEXT, title TEXT, created REAL, meta TEXT, tags TEXT DEFAULT '[]',
  note TEXT DEFAULT '', starred INTEGER DEFAULT 0, sha256 TEXT
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
  text TEXT, comment TEXT, kind TEXT, created REAL, align TEXT DEFAULT 'null'
);
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT, paper_id TEXT, role TEXT, content TEXT, created REAL
);
CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT, created REAL, settings TEXT DEFAULT '{}');
CREATE TABLE IF NOT EXISTS llm_usage (
  ts REAL, user_id TEXT, paper_id TEXT, task TEXT, model TEXT,
  input INTEGER, output INTEGER, cache_write INTEGER, cache_read INTEGER, cost REAL
);
CREATE INDEX IF NOT EXISTS llm_usage_ts ON llm_usage(ts);
CREATE TABLE IF NOT EXISTS workspaces (id TEXT PRIMARY KEY, user_id TEXT, name TEXT, created REAL);
CREATE TABLE IF NOT EXISTS workspace_papers (
  workspace_id TEXT, paper_id TEXT, added REAL, PRIMARY KEY (workspace_id, paper_id)
);
CREATE TABLE IF NOT EXISTS wiki_pages (
  workspace_id TEXT, slug TEXT, title TEXT, markdown TEXT, sources TEXT, updated REAL,
  PRIMARY KEY (workspace_id, slug)
);
CREATE TABLE IF NOT EXISTS wiki_ingested (
  workspace_id TEXT, paper_id TEXT, ingested REAL, PRIMARY KEY (workspace_id, paper_id)
);
CREATE TABLE IF NOT EXISTS wiki_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT, workspace_id TEXT, role TEXT, content TEXT, created REAL
);
CREATE TABLE IF NOT EXISTS notes (
  id TEXT PRIMARY KEY, user_id TEXT NOT NULL, paper_id TEXT NOT NULL, markdown TEXT DEFAULT '', created REAL, updated REAL
);
CREATE UNIQUE INDEX IF NOT EXISTS notes_paper ON notes(user_id, paper_id);
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
        # 舊資料庫升級：users 加上 settings 欄（JSON 物件）
        ucols = {r["name"] for r in c.execute("PRAGMA table_info(users)")}
        if "settings" not in ucols:
            c.execute("ALTER TABLE users ADD COLUMN settings TEXT DEFAULT '{}'")
        if "email" not in ucols:  # Keycloak 登入帶回的 email
            c.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''")
        # papers 加上備註、星號（docs/paper-cards.md）
        cols = {r["name"] for r in c.execute("PRAGMA table_info(papers)")}
        if "note" not in cols:
            c.execute("ALTER TABLE papers ADD COLUMN note TEXT DEFAULT ''")
        if "starred" not in cols:
            c.execute("ALTER TABLE papers ADD COLUMN starred INTEGER DEFAULT 0")
        if "sha256" not in cols:  # 重複偵測用；舊論文沒有，靠 DOI／標題比對
            c.execute("ALTER TABLE papers ADD COLUMN sha256 TEXT")
        # annotations 加上中英對齊結果（譯文裡對應的那段，docs/reader.md）
        if "align" not in {r["name"] for r in c.execute("PRAGMA table_info(annotations)")}:
            c.execute("ALTER TABLE annotations ADD COLUMN align TEXT DEFAULT 'null'")
        # 測試使用者：user id = 名字
        c.executemany("INSERT OR IGNORE INTO users (id, name, created) VALUES (?,?,?)",
                      [(u, u, time.time()) for u in config.TEST_USERS])


def get_user(uid: str) -> dict | None:
    with conn() as c:
        r = c.execute("SELECT id, name, email FROM users WHERE id=?", (uid,)).fetchone()
    return dict(r) if r else None


def add_usage(uid, pid, task, model, inp, out, cache_write, cache_read, cost) -> None:
    with conn() as c:
        c.execute("INSERT INTO llm_usage VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (time.time(), uid, pid, task, model, inp, out, cache_write, cache_read, cost))


def usage_report(days: int) -> dict:
    """管理者看的全站用量：最近 days 天，依功能、模型、使用者、論文、日期加總。"""
    since = time.time() - days * 86400
    sums = ("COUNT(*) calls, SUM(cost) cost, SUM(input) input, SUM(output) output, "
            "SUM(cache_write) cache_write, SUM(cache_read) cache_read")
    with conn() as c:
        def q(sql):
            return [dict(r) for r in c.execute(sql, (since,))]
        return {
            "days": days,
            "total": q(f"SELECT {sums} FROM llm_usage WHERE ts>=?")[0],
            "by_task": q(f"SELECT task, {sums} FROM llm_usage WHERE ts>=? GROUP BY task ORDER BY cost DESC"),
            "by_model": q(f"SELECT model, {sums} FROM llm_usage WHERE ts>=? GROUP BY model ORDER BY cost DESC"),
            "by_user": q(f"SELECT COALESCE(NULLIF(u.email,''), u.name, l.user_id, '（背景）') who, {sums} "
                         "FROM llm_usage l LEFT JOIN users u ON u.id=l.user_id WHERE ts>=? "
                         "GROUP BY l.user_id ORDER BY cost DESC"),
            "top_papers": q(f"SELECT COALESCE(p.title, l.paper_id) title, {sums} FROM llm_usage l "
                            "LEFT JOIN papers p ON p.id=l.paper_id WHERE ts>=? AND l.paper_id IS NOT NULL "
                            "GROUP BY l.paper_id ORDER BY cost DESC LIMIT 10"),
            "daily": q(f"SELECT date(ts, 'unixepoch', 'localtime') day, {sums} FROM llm_usage "
                       "WHERE ts>=? GROUP BY day ORDER BY day"),
        }


def get_settings(uid: str) -> dict:
    with conn() as c:
        r = c.execute("SELECT settings FROM users WHERE id=?", (uid,)).fetchone()
    return json.loads(r["settings"] or "{}") if r else {}


def set_settings(uid: str, settings: dict) -> None:
    with conn() as c:
        c.execute("UPDATE users SET settings=? WHERE id=?", (json.dumps(settings, ensure_ascii=False), uid))


def upsert_user(uid: str, name: str, email: str) -> None:
    """OIDC 登入：第一次進來就建一筆；之後每次登入同步名稱與 email。"""
    with conn() as c:
        c.execute("INSERT INTO users (id, name, created, email) VALUES (?,?,?,?) "
                  "ON CONFLICT(id) DO UPDATE SET name=excluded.name, email=excluded.email",
                  (uid, name, time.time(), email))


def list_users() -> list[dict]:
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT id, name FROM users ORDER BY created, id")]


def new_id() -> str:
    return uuid.uuid4().hex[:12]


# ---------- papers ----------
def add_paper(uid: str, pid: str, filename: str, title: str, meta: dict, sha256: str | None = None) -> None:
    with conn() as c:
        c.execute("INSERT INTO papers (id, user_id, filename, title, created, meta, sha256) VALUES (?,?,?,?,?,?,?)",
                  (pid, uid, filename, title, time.time(), json.dumps(meta, ensure_ascii=False), sha256))


def norm_title(t: str | None) -> str:
    """比對重複用：不分大小寫、去掉空白與標點。「Untitled」（抓不到標題）不算。"""
    t = re.sub(r"[\W_]+", "", (t or "").casefold())
    return "" if t == "untitled" else t


def find_duplicate(uid: str, sha256: str | None = None, doi: str | None = None, title: str | None = None) -> str | None:
    """使用者庫裡相同檔案（sha256）、相同 DOI（書目快取）或相同正規化標題的論文 id。"""
    doi, title = (doi or "").lower(), norm_title(title)
    with conn() as c:
        rows = c.execute("SELECT p.id, p.title, p.sha256, "
                         "(SELECT k.value FROM cache k WHERE k.paper_id = p.id AND k.kind = 'bib') AS bib "
                         "FROM papers p WHERE p.user_id=? ORDER BY p.created", (uid,)).fetchall()
    for r in rows:
        bib = json.loads(r["bib"] or "null") or {}
        if (sha256 and r["sha256"] == sha256) or (title and norm_title(r["title"]) == title) \
                or (doi and (bib.get("doi") or "").lower() == doi):
            return r["id"]
    return None


def get_paper(pid: str) -> dict | None:
    with conn() as c:
        r = c.execute("SELECT * FROM papers WHERE id=?", (pid,)).fetchone()
    if not r:
        return None
    return {**dict(r), "meta": json.loads(r["meta"]), "tags": json.loads(r["tags"] or "[]")}


def list_papers(uid: str, workspace: str | None = None) -> list[dict]:
    # tr_done / tr_total：已有對照翻譯快取的頁數 / 總頁數（給卡片上的進度圈）
    # year / byline：有書目快取才有，否則 null
    # added：加入研究主題的時間（全部論文 = 上傳時間）
    sql = ("SELECT p.id, p.filename, p.title, p.created, p.tags, p.note, p.starred, "
           + ("w.added" if workspace else "p.created") + " AS added, "
           "json_extract(p.meta, '$.num_pages') AS tr_total, "
           "(SELECT COUNT(*) FROM cache k WHERE k.paper_id = p.id AND k.kind = 'block_translation') AS tr_done, "
           "(SELECT k.value FROM cache k WHERE k.paper_id = p.id AND k.kind = 'bib') AS bib "
           "FROM papers p ")
    args: tuple = (uid,)
    if workspace:
        sql += "JOIN workspace_papers w ON w.paper_id = p.id AND w.workspace_id = ? "
        args = (workspace, uid)
    with conn() as c:
        # 研究主題裡依加入時間：既有論文（例如重複上傳）加進來也排最前面
        rows = c.execute(sql + "WHERE p.user_id=? ORDER BY added DESC", args).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        bib = json.loads(d.pop("bib") or "null") or {}
        out.append({**d, "tags": json.loads(r["tags"] or "[]"), "note": r["note"] or "", "starred": bool(r["starred"]),
                    "year": bib.get("year"), "byline": byline(bib)})
    return out


def byline(bib: dict) -> str | None:
    """卡片上的一行出處：「Chen, Giuffrida, Tsaftaris，ICCVW 2023」；沒有書目資料回 None。"""
    fams = [a.get("family") for a in bib.get("authors") or [] if a.get("family")]
    who = (", ".join(fams) if len(fams) <= 3 else f"{fams[0]} 等") if fams else ""
    venue = bib.get("venue") or ("arXiv" if bib.get("arxiv") else "")
    abbr = re.search(r"\(([A-Z][\w-]{1,15})\)", venue)  # 「…Workshops (ICCVW)」取括號裡的縮寫
    venue = abbr.group(1) if abbr else venue[:40]
    where = " ".join(str(x) for x in (venue, bib.get("year")) if x)
    return "，".join(x for x in (who, where) if x) or None


def update_paper(pid: str, tags: list[str], note: str, starred: bool) -> None:
    with conn() as c:
        c.execute("UPDATE papers SET tags=?, note=?, starred=? WHERE id=?",
                  (json.dumps(tags, ensure_ascii=False), note, int(starred), pid))


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
        for t in ("papers", "chunks", "cache", "annotations", "messages", "notes"):
            col = "id" if t == "papers" else "paper_id"
            c.execute(f"DELETE FROM {t} WHERE {col}=?", (pid,))
        c.execute("DELETE FROM workspace_papers WHERE paper_id=?", (pid,))
        c.execute("DELETE FROM wiki_ingested WHERE paper_id=?", (pid,))  # shortcut: 頁面保留，內容可能提到已刪的論文


# ---------- 論文筆記（docs/notes-design.md）----------
def get_note(uid: str, pid: str) -> dict | None:
    with conn() as c:
        r = c.execute("SELECT markdown, updated FROM notes WHERE user_id=? AND paper_id=?", (uid, pid)).fetchone()
    return dict(r) if r else None


def save_note(uid: str, pid: str, markdown: str, base_updated: float | None) -> tuple[bool, dict]:
    """樂觀並行：base_updated 要等於資料庫裡的 updated（還沒有筆記 = None）才寫入。
    回傳 (成功?, 成功時新的 {updated}、衝突時伺服器那份 {markdown, updated})。"""
    now = time.time()
    with conn() as c:
        if base_updated is None:
            try:
                c.execute("INSERT INTO notes (id, user_id, paper_id, markdown, created, updated) VALUES (?,?,?,?,?,?)",
                          (uuid.uuid4().hex, uid, pid, markdown, now, now))
                return True, {"updated": now}
            except sqlite3.IntegrityError:  # 別的分頁已經先建了
                pass
        else:
            # 條件式 UPDATE：比對和寫入在同一句，兩個請求同時到也只有一個成功
            now = max(now, base_updated + 1e-3)
            if c.execute("UPDATE notes SET markdown=?, updated=? WHERE user_id=? AND paper_id=? AND updated=?",
                         (markdown, now, uid, pid, base_updated)).rowcount:
                return True, {"updated": now}
        r = c.execute("SELECT markdown, updated FROM notes WHERE user_id=? AND paper_id=?", (uid, pid)).fetchone()
    return False, dict(r) if r else {"markdown": "", "updated": None}


# ---------- workspaces ----------
_WS = ("SELECT w.id, w.name, w.created, COUNT(wp.paper_id) AS count FROM workspaces w "
       "LEFT JOIN workspace_papers wp ON wp.workspace_id = w.id ")


def list_workspaces(uid: str) -> list[dict]:
    """首頁卡片用：每個研究主題另附 recent（最新加入的 3 篇 id）、updated（最後加入時間）、tags（最常見 2 個標籤）。"""
    with conn() as c:
        rows = c.execute(_WS + "WHERE w.user_id=? GROUP BY w.id ORDER BY w.created DESC", (uid,)).fetchall()
        members = c.execute("SELECT wp.workspace_id AS wid, p.id, p.tags, wp.added FROM workspace_papers wp "
                            "JOIN workspaces w ON w.id = wp.workspace_id JOIN papers p ON p.id = wp.paper_id "
                            "WHERE w.user_id=? ORDER BY wp.added DESC", (uid,)).fetchall()
    out = [{**dict(r), "recent": [], "updated": None, "tags": []} for r in rows]
    by, tagc = {w["id"]: w for w in out}, {}
    for m in members:
        w = by[m["wid"]]
        if len(w["recent"]) < 3:
            w["recent"].append(m["id"])
        w["updated"] = w["updated"] or m["added"]
        tagc.setdefault(m["wid"], Counter()).update(json.loads(m["tags"] or "[]"))
    for wid, cnt in tagc.items():
        by[wid]["tags"] = [t for t, _ in cnt.most_common(2)]
    return out


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
        for t in ("workspace_papers", "wiki_pages", "wiki_ingested", "wiki_messages"):
            c.execute(f"DELETE FROM {t} WHERE workspace_id=?", (wid,))


def add_to_workspace(wid: str, pid: str) -> None:
    with conn() as c:
        c.execute("INSERT OR IGNORE INTO workspace_papers VALUES (?,?,?)", (wid, pid, time.time()))


def remove_from_workspace(wid: str, pid: str) -> None:
    with conn() as c:
        c.execute("DELETE FROM workspace_papers WHERE workspace_id=? AND paper_id=?", (wid, pid))


# ---------- workspace wiki ----------
def wiki_pages(wid: str) -> list[dict]:
    with conn() as c:
        rows = c.execute("SELECT slug, title, updated FROM wiki_pages WHERE workspace_id=? "
                         "ORDER BY slug != 'index', title", (wid,)).fetchall()
    return [dict(r) for r in rows]


def wiki_page(wid: str, slug: str) -> dict | None:
    with conn() as c:
        r = c.execute("SELECT slug, title, markdown, sources, updated FROM wiki_pages "
                      "WHERE workspace_id=? AND slug=?", (wid, slug)).fetchone()
    return {**dict(r), "sources": json.loads(r["sources"] or "[]")} if r else None


def wiki_save(wid: str, slug: str, title: str, markdown: str, sources: list[str]) -> None:
    with conn() as c:
        c.execute("INSERT OR REPLACE INTO wiki_pages VALUES (?,?,?,?,?,?)",
                  (wid, slug, title, markdown, json.dumps(sources), time.time()))


def wiki_pending(wid: str) -> list[str]:
    """workspace 裡還沒整理進 wiki 的論文（舊到新）。"""
    with conn() as c:
        rows = c.execute("SELECT wp.paper_id FROM workspace_papers wp LEFT JOIN wiki_ingested i "
                         "ON i.workspace_id = wp.workspace_id AND i.paper_id = wp.paper_id "
                         "WHERE wp.workspace_id=? AND i.paper_id IS NULL ORDER BY wp.added", (wid,)).fetchall()
    return [r["paper_id"] for r in rows]


def wiki_mark_ingested(wid: str, pid: str) -> None:
    with conn() as c:
        c.execute("INSERT OR REPLACE INTO wiki_ingested VALUES (?,?,?)", (wid, pid, time.time()))


def wiki_backlinks(uid: str, pid: str) -> list[dict]:
    """使用者自己的 workspace 中，sources 含這篇的 wiki 頁（論文頁排最前）。"""
    with conn() as c:
        rows = c.execute("SELECT w.id AS workspace_id, w.name AS workspace_name, p.slug, p.title "
                         "FROM wiki_pages p JOIN workspaces w ON w.id = p.workspace_id "
                         "WHERE w.user_id=? AND EXISTS (SELECT 1 FROM json_each(p.sources) WHERE value=?) "
                         "ORDER BY p.slug != ?, w.name, p.title", (uid, pid, f"paper-{pid}")).fetchall()
    return [dict(r) for r in rows]


def add_wiki_message(wid: str, role: str, content: str) -> None:
    with conn() as c:
        c.execute("INSERT INTO wiki_messages (workspace_id, role, content, created) VALUES (?,?,?,?)",
                  (wid, role, content, time.time()))


def list_wiki_messages(wid: str, limit: int = 50) -> list[dict]:
    with conn() as c:
        rows = c.execute("SELECT id, role, content FROM wiki_messages WHERE workspace_id=? ORDER BY id DESC LIMIT ?",
                         (wid, limit)).fetchall()
    return [dict(r) for r in reversed(rows)]


def delete_wiki_exchange(wid: str, mid: int) -> bool:
    """刪一題問答：這則問題，加上它到下一個問題之前的回答。"""
    with conn() as c:
        if not c.execute("SELECT 1 FROM wiki_messages WHERE id=? AND workspace_id=? AND role='user'", (mid, wid)).fetchone():
            return False
        nxt = c.execute("SELECT MIN(id) FROM wiki_messages WHERE workspace_id=? AND role='user' AND id>?", (wid, mid)).fetchone()[0]
        c.execute("DELETE FROM wiki_messages WHERE workspace_id=? AND id>=? AND id<?", (wid, mid, nxt or 2**62))
    return True


def clear_wiki_messages(wid: str) -> None:
    with conn() as c:
        c.execute("DELETE FROM wiki_messages WHERE workspace_id=?", (wid,))


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
    a = {"id": new_id(), "created": time.time(), "comment": "", "kind": "user", "align": None, **a}
    with conn() as c:
        c.execute("INSERT INTO annotations (id, paper_id, page, rects, color, text, comment, kind, created, align)"
                  " VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (a["id"], pid, a["page"], json.dumps(a["rects"]), a.get("color", "yellow"),
                   a.get("text", ""), a["comment"], a["kind"], a["created"], json.dumps(a["align"], ensure_ascii=False)))
    return a


def list_annotations(pid: str) -> list[dict]:
    with conn() as c:
        rows = c.execute("SELECT * FROM annotations WHERE paper_id=? ORDER BY page, created", (pid,)).fetchall()
    return [{**dict(r), "rects": json.loads(r["rects"]), "align": json.loads(r["align"] or "null")} for r in rows]


def annotation_paper(aid: str) -> str | None:
    with conn() as c:
        r = c.execute("SELECT paper_id FROM annotations WHERE id=?", (aid,)).fetchone()
    return r["paper_id"] if r else None


def update_annotation(aid: str, comment: str | None = None, align: dict | None = None) -> None:
    with conn() as c:
        if comment is not None:
            c.execute("UPDATE annotations SET comment=? WHERE id=?", (comment, aid))
        if align is not None:
            c.execute("UPDATE annotations SET align=? WHERE id=?", (json.dumps(align, ensure_ascii=False), aid))


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
