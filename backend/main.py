"""FastAPI 入口。啟動：uv run uvicorn backend.main:app --reload --port 7800

API 一覽（前端 app.js 會呼叫）：
  POST   /api/papers                 上傳 PDF（multipart）；已有同一篇就回傳既有那篇 + duplicate: true
  POST   /api/papers/arxiv           用 arXiv 網址或編號匯入
  GET    /api/papers                 論文列表
  GET    /api/papers/{id}            論文資訊（標題、大綱、摘要…）
  GET    /api/papers/{id}/pdf        PDF 原檔（給 PDF.js 顯示）
  DELETE /api/papers/{id}
  POST   /api/papers/{id}/explain        選字解釋        （SSE 串流）
  POST   /api/papers/{id}/translate      選字翻譯        （SSE）
  POST   /api/papers/{id}/translate-page 整頁翻譯        （SSE，會快取）
  POST   /api/papers/{id}/explain-image  框選圖片/公式解釋（SSE）
  POST   /api/papers/{id}/chat           聊天            （SSE）
  GET    /api/papers/{id}/summary        摘要            （SSE，會快取）
  POST   /api/papers/{id}/auto-highlight 自動標註
  GET    /api/papers/{id}/outline-ai     AI 產生大綱
  GET    /api/papers/{id}/reference/{n}  引用卡片
  PATCH  /api/papers/{id}                標籤、備註、星號
  GET    /api/papers/{id}/cite           複製引用（APA/IEEE/MLA/BibTeX）
  GET/POST/PATCH/DELETE .../annotations  螢光筆與註解
  /api/auth/*、/api/me、/api/workspaces…  測試登入與 workspace（見 docs/workspaces.md）

SSE（Server-Sent Events）：伺服器用一條 HTTP 連線持續推送 "data: ...\n\n"，
前端邊收邊顯示，所以模型生成時你就能看到字一個個出來。
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import re
from typing import Annotated, AsyncIterator, Callable, Literal

import secrets
from urllib.parse import urlencode

import httpx
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Cookie, Depends, FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.sessions import SessionMiddleware

from . import cite, config, db, features, llm, pdf_parse, retrieval
from .pdf_parse import parse_pdf

app = FastAPI(title="Paper Reader")
db.init()

# 登入 session：簽章 cookie（OIDC 的 state／nonce／PKCE 也暫存在這裡）。
# OIDC 模式一定要設 SESSION_SECRET；dev 模式沒設就每次啟動隨機產生（重啟後要重新登入）
if config.AUTH_MODE == "oidc" and not (config.SESSION_SECRET and config.OIDC_ISSUER and config.OIDC_CLIENT_ID and config.OIDC_CLIENT_SECRET):
    raise RuntimeError("AUTH_MODE=oidc 需要 OIDC_ISSUER、OIDC_CLIENT_ID、OIDC_CLIENT_SECRET、SESSION_SECRET（見 docs/auth.md）")
app.add_middleware(SessionMiddleware, secret_key=config.SESSION_SECRET or secrets.token_urlsafe(32),
                   session_cookie="lantern_session", max_age=config.SESSION_MAX_AGE, same_site="lax",
                   https_only=config.PUBLIC_BASE_URL.startswith("https://"))
oauth = OAuth()
if config.AUTH_MODE == "oidc":
    oauth.register("kc", client_id=config.OIDC_CLIENT_ID, client_secret=config.OIDC_CLIENT_SECRET,
                   server_metadata_url=f"{config.OIDC_ISSUER}/.well-known/openid-configuration",
                   client_kwargs={"scope": "openid profile email", "code_challenge_method": "S256"})

PDF_DIR = config.DATA_DIR / "pdfs"


# ---------------- 登入（docs/auth.md） ----------------
def current_user(request: Request, uid: str | None = Cookie(None)) -> str:
    """oidc：讀簽章 session 裡的 Keycloak sub；dev：讀測試用的 uid cookie（未簽章，只能本機開發用）。"""
    if config.AUTH_MODE == "oidc":
        uid = request.session.get("uid")
    if not uid or not db.get_user(uid):
        raise HTTPException(401, "not logged in")
    return uid


Uid = Annotated[str, Depends(current_user)]


@app.get("/api/auth/config")
def auth_config():
    """前端用來決定登入頁長什麼樣：dev＝使用者名片；oidc＝「用 Keycloak 登入」按鈕。"""
    return {"mode": config.AUTH_MODE, "version": config.VERSION}


@app.get("/api/auth/users")
def auth_users():
    if config.AUTH_MODE != "dev":
        raise HTTPException(404, "Not Found")
    return db.list_users()


class LoginIn(BaseModel):
    user_id: str


@app.post("/api/auth/login")
def login(body: LoginIn, response: Response):
    u = db.get_user(body.user_id) if config.AUTH_MODE == "dev" else None
    if not u:
        raise HTTPException(401, "unknown user")
    response.set_cookie("uid", u["id"], httponly=True, samesite="lax")
    return u


@app.get("/api/auth/login")
async def oidc_login(request: Request):
    """導到 Keycloak 登入頁（Authorization Code + PKCE S256；state、nonce 存在 session）。"""
    if config.AUTH_MODE != "oidc":
        raise HTTPException(404, "Not Found")
    return await oauth.kc.authorize_redirect(request, f"{config.PUBLIC_BASE_URL}/api/auth/callback")


@app.get("/api/auth/callback")
async def oidc_callback(request: Request):
    """Keycloak 帶 code 回來：換 token、驗 ID token（簽章、iss、aud、exp、nonce 由 Authlib 檢查），建立或更新使用者。"""
    if config.AUTH_MODE != "oidc":
        raise HTTPException(404, "Not Found")
    try:
        token = await oauth.kc.authorize_access_token(request)
    except OAuthError as e:  # 使用者按取消、state 不符、code 過期…回首頁顯示登入失敗
        print(f"[oidc] callback failed: {e.error}")
        return RedirectResponse("/?login_error=1", status_code=302)
    info = token.get("userinfo") or {}
    sub = info.get("sub")
    if not sub:
        return RedirectResponse("/?login_error=1", status_code=302)
    db.upsert_user(sub, info.get("name") or info.get("preferred_username") or info.get("email") or sub, info.get("email") or "")
    request.session.clear()
    request.session.update({"uid": sub, "id_token": token.get("id_token", "")})
    return RedirectResponse("/", status_code=302)


@app.post("/api/auth/logout")
async def logout(request: Request, response: Response):
    """dev：清 cookie。oidc：清 session，並回傳 Keycloak 的登出網址讓前端導過去（一併結束 Keycloak 那邊的登入）。"""
    response.delete_cookie("uid")
    if config.AUTH_MODE != "oidc":
        return {"ok": True}
    id_token = request.session.get("id_token", "")
    request.session.clear()
    meta = await oauth.kc.load_server_metadata()
    query = {"client_id": config.OIDC_CLIENT_ID, "post_logout_redirect_uri": f"{config.PUBLIC_BASE_URL}/"}
    if id_token:
        query["id_token_hint"] = id_token
    return {"ok": True, "logout_url": f"{meta['end_session_endpoint']}?{urlencode(query)}"}


@app.get("/api/livez")
def livez():
    """給 k8s probe：只確認程式活著，不碰模型（/api/health 會真的呼叫模型）。"""
    return {"ok": True}


@app.get("/api/me")
def me(uid: Uid):
    return db.get_user(uid)


class SettingsIn(BaseModel):
    auto_translate: bool = False  # 上傳後在背景先把整篇對照翻譯跑完
    auto_wiki: bool = False  # 論文加入 workspace 就在背景更新該 workspace 的 wiki


@app.get("/api/me/settings")
def get_settings(uid: Uid):
    return SettingsIn(**db.get_settings(uid)).model_dump()


@app.put("/api/me/settings")
def put_settings(body: SettingsIn, uid: Uid):
    db.set_settings(uid, body.model_dump())
    return body.model_dump()


# ---------------- 工具函式 ----------------
def _paper_or_404(pid: str, uid: str) -> dict:
    p = db.get_paper(pid)
    if not p or p["user_id"] != uid:
        raise HTTPException(404, "paper not found")
    return p


def _ws_or_404(wid: str, uid: str) -> dict:
    w = db.get_workspace(uid, wid)
    if not w:
        raise HTTPException(404, "workspace not found")
    return w


def _pdf_path(pid: str) -> str:
    return str(PDF_DIR / f"{pid}.pdf")


def sse(gen: AsyncIterator[str], on_done: Callable[[str], None] | None = None) -> StreamingResponse:
    async def wrapped():
        full = []
        try:
            async for piece in gen:
                full.append(piece)
                yield f"data: {json.dumps({'t': piece}, ensure_ascii=False)}\n\n"
            if on_done:
                on_done("".join(full))
        except Exception as e:  # 模型連不上、context 太長…都回報給前端顯示
            yield f"data: {json.dumps({'error': f'{type(e).__name__}: {e}'}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(wrapped(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


async def _cached_text(text: str) -> AsyncIterator[str]:
    yield text


async def _ocr_pages(path: str, pages: list[int]) -> tuple[dict[int, str], str | None]:
    """掃描頁丟給 OCR 模型。一次最多 2 頁並行，避免單張 GPU 被塞爆。"""
    sem = asyncio.Semaphore(2)

    async def one(pno: int):
        async with sem:
            png = await asyncio.to_thread(pdf_parse.render_page_png, path, pno, 150)
            return pno, await llm.ocr_image("data:image/png;base64," + base64.b64encode(png).decode())

    try:
        return dict(await asyncio.gather(*(one(p) for p in pages))), None
    except Exception as e:  # 模型不支援影像、連不上…論文照樣匯入，只是那幾頁沒文字
        return {}, f"{type(e).__name__}: {e}"


_DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s\"<>]+")


def _first_doi(parsed) -> str | None:
    """第一頁上的 DOI（期刊論文通常印在頁首或頁尾）。"""
    m = _DOI_RE.search(" ".join(b.text for b in parsed.blocks if b.page == 0))
    return m.group(0).rstrip(".,;)]") if m else None


def _duplicate(uid: str, pid: str, path: str, workspace: str | None) -> dict:
    """已經有這篇：丟掉剛存的檔案，回傳既有那篇；在研究主題裡上傳就把它加進去。"""
    os.remove(path)
    if workspace:
        db.add_to_workspace(workspace, pid)
        _auto_wiki(uid, workspace)
    return {"id": pid, "title": db.get_paper(pid)["title"], "duplicate": True}


async def _ingest(uid: str, pid: str, filename: str, path: str, workspace: str | None) -> dict:
    with open(path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    if dup := db.find_duplicate(uid, sha256=sha):  # 同一個檔案：連解析都不用
        return _duplicate(uid, dup, path, workspace)
    parsed = parse_pdf(path)
    ocr_error = None
    if parsed.scanned_pages and config.OCR_ENABLED:
        results, ocr_error = await _ocr_pages(path, parsed.scanned_pages)
        pdf_parse.apply_ocr(parsed, results)
    if dup := db.find_duplicate(uid, doi=_first_doi(parsed), title=parsed.title):  # 在建索引（最花時間）之前
        return _duplicate(uid, dup, path, workspace)
    n = await retrieval.build_index(pid, parsed.blocks)
    meta = parsed.to_dict()
    db.add_paper(uid, pid, filename, parsed.title, meta, sha)
    if workspace:
        db.add_to_workspace(workspace, pid)
        _auto_wiki(uid, workspace)
    jobs = [_prefetch_bib(pid)] + ([_pretranslate(pid)] if db.get_settings(uid).get("auto_translate") else [])
    for job in jobs:
        task = asyncio.create_task(job)
        _bg_tasks.add(task)  # 留住參考，不然 task 可能被回收
        task.add_done_callback(_bg_tasks.discard)
    return {"id": pid, "title": parsed.title, "num_pages": parsed.num_pages, "chunks": n,
            "scanned_pages": len(parsed.scanned_pages), "ocr_pages": len(parsed.ocr_pages),
            "ocr_error": ocr_error, "ocr_enabled": config.OCR_ENABLED}


def _public(p: dict) -> dict:
    m = p["meta"]
    return {"id": p["id"], "filename": p["filename"], "title": m["title"], "num_pages": m["num_pages"],
            "page_sizes": m["page_sizes"], "outline": m["outline"], "abstract": m["abstract"],
            "references": len(m["references"]), "full_text_fits": features.full_text_fits(p),
            "scanned_pages": m.get("scanned_pages", []), "ocr_pages": m.get("ocr_pages", []),
            "tags": p.get("tags", [])}


# ---------------- 論文 ----------------
@app.post("/api/papers")
async def upload(file: UploadFile, uid: Uid, workspace: str | None = Form(None)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "只接受 PDF")
    if workspace:
        _ws_or_404(workspace, uid)
    pid = db.new_id()
    path = _pdf_path(pid)
    with open(path, "wb") as f:
        f.write(await file.read())
    return await _ingest(uid, pid, file.filename, path, workspace)


class ArxivIn(BaseModel):
    url: str
    workspace: str | None = None


MAX_PDF_BYTES = 150 * 1024 * 1024


@app.post("/api/papers/arxiv")
async def import_url(body: ArxivIn, uid: Uid):
    """用 arXiv 編號 / 網址，或任何直接指向 PDF 的網址匯入。
    伺服器在你的電腦上下載，所以學校網路（IP 授權）能看的期刊 PDF 也抓得到。"""
    if body.workspace:
        _ws_or_404(body.workspace, uid)
    url = body.url.strip()
    m = re.fullmatch(r"(?:arxiv:)?(\d{4}\.\d{4,5}(?:v\d+)?)", url, re.I) or \
        (re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5}(?:v\d+)?)", url) if "arxiv.org" in url else None)
    if m:
        src, name = f"https://arxiv.org/pdf/{m.group(1)}", f"arXiv-{m.group(1)}.pdf"
    elif re.match(r"https?://", url, re.I):
        src = url
        name = (re.sub(r"[^\w.-]", "_", url.split("?")[0].rstrip("/").rsplit("/", 1)[-1]) or "paper")[:80]
        name = name if name.lower().endswith(".pdf") else name + ".pdf"
    else:
        raise HTTPException(400, "請輸入 arXiv 編號（例：2401.01234）或 PDF 的網址（http/https）")
    try:
        async with httpx.AsyncClient(timeout=90, follow_redirects=True,
                                     headers={"User-Agent": "Mozilla/5.0 (Lantern paper reader)"}) as client:
            r = await client.get(src)
    except httpx.HTTPError as e:
        raise HTTPException(502, f"下載失敗：{type(e).__name__}")
    if r.status_code != 200:
        raise HTTPException(502, f"下載失敗（HTTP {r.status_code}）")
    if not r.content.startswith(b"%PDF"):
        # 期刊的 DOI / 文章頁通常是 HTML，要的是頁面上「下載 PDF」那個連結
        raise HTTPException(400, "這個網址回傳的不是 PDF（可能是文章頁）。請貼上「下載 PDF」按鈕的連結")
    if len(r.content) > MAX_PDF_BYTES:
        raise HTTPException(413, "PDF 超過 150 MB")
    pid = db.new_id()
    path = _pdf_path(pid)
    with open(path, "wb") as f:
        f.write(r.content)
    return await _ingest(uid, pid, name, path, body.workspace)


@app.get("/api/papers")
def papers(uid: Uid, workspace: str | None = None):
    if workspace:
        _ws_or_404(workspace, uid)
    return [{**p, "translating": p["id"] in _translating, "fetching_bib": p["id"] in _fetching_bib}
            for p in db.list_papers(uid, workspace)]


@app.get("/api/papers/{pid}")
def paper(pid: str, uid: Uid):
    return _public(_paper_or_404(pid, uid))


@app.get("/api/papers/{pid}/pdf")
def paper_pdf(pid: str, uid: Uid):
    _paper_or_404(pid, uid)
    return FileResponse(_pdf_path(pid), media_type="application/pdf")


class TagsIn(BaseModel):  # 欄位都選填，只改有給的
    tags: list[str] | None = None
    note: str | None = Field(None, max_length=20000)
    starred: bool | None = None


@app.patch("/api/papers/{pid}")
def edit_paper(pid: str, uid: Uid, body: TagsIn):
    p = _paper_or_404(pid, uid)
    tags = p["tags"] if body.tags is None else         list(dict.fromkeys(t.strip() for t in body.tags if t.strip()))  # 去空白、去重複、保留順序
    note = (p["note"] or "") if body.note is None else body.note
    starred = bool(p["starred"]) if body.starred is None else body.starred
    db.update_paper(pid, tags, note, starred)
    return {"tags": tags, "note": note, "starred": starred}


@app.get("/api/papers/{pid}/cite")
async def cite_paper(pid: str, uid: Uid):
    """書目資料 + APA / IEEE / MLA / BibTeX。第一次才取書目並快取（docs/paper-cards.md）。"""
    p = _paper_or_404(pid, uid)
    try:
        bib = await _ensure_bib(p)
    except Exception as e:  # LLM 也失敗：回原因給前端，不寫快取
        raise HTTPException(502, f"取得書目資料失敗：{e}")
    return {"bib": bib, "styles": cite.styles(bib)}


async def _ensure_bib(p: dict) -> dict:
    bib = db.cache_get(p["id"], "bib")
    if bib is None:
        bib = await features.fetch_bib(p)
        db.cache_set(p["id"], "bib", bib)
    return bib


async def _prefetch_bib(pid: str) -> None:
    """匯入後在背景先取書目，卡片才一開始就有作者與出處；失敗就等使用者按「引用」再試。"""
    _fetching_bib.add(pid)
    try:
        await _ensure_bib(db.get_paper(pid))
    except Exception as e:
        print(f"[bib] {pid}: {type(e).__name__}: {e}")
    finally:
        _fetching_bib.discard(pid)


_fetching_bib: set[str] = set()  # 背景取書目中的論文 id（卡片上的「取得書目中」）


THUMB_DIR = config.DATA_DIR / "thumbs"


@app.get("/api/papers/{pid}/thumb.png")
def paper_thumb(pid: str, uid: Uid):
    """第一頁縮圖（論文卡、書架用）。畫一次就存檔。"""
    _paper_or_404(pid, uid)
    f = THUMB_DIR / f"{pid}.png"
    if not f.exists():
        THUMB_DIR.mkdir(parents=True, exist_ok=True)
        f.write_bytes(pdf_parse.render_page_png(_pdf_path(pid), 0, dpi=36))
    return FileResponse(f, media_type="image/png", headers={"Cache-Control": "private, max-age=86400"})


@app.get("/api/search")
def search(q: str, uid: Uid):
    """全文搜尋所有論文，回傳 [{paper_id, title, page, snippet}]。"""
    q = q.strip()
    if len(q) < 2:
        return []
    out = []
    for r in db.search_chunks(uid, q):
        i = r["text"].lower().find(q.lower())
        s = max(0, i - 60)
        out.append({"paper_id": r["paper_id"], "title": r["title"], "page": r["page"],
                    "snippet": ("…" if s else "") + r["text"][s: i + len(q) + 80] + "…"})
    return out


@app.delete("/api/papers/{pid}")
def delete(pid: str, uid: Uid):
    _paper_or_404(pid, uid)
    db.delete_paper(pid)
    for f in (PDF_DIR / f"{pid}.pdf", THUMB_DIR / f"{pid}.png"):
        f.unlink(missing_ok=True)
    return {"ok": True}


# ---------------- AI 功能 ----------------
class SelectionIn(BaseModel):
    text: str
    page: int = 0
    question: str = ""  # 選字工具列的「Ask AI」：針對選取段落提問
    history: str = ""   # 接續之前的解釋對話時，先前的問答（Markdown）


@app.post("/api/papers/{pid}/explain")
async def explain(pid: str, uid: Uid, body: SelectionIn):
    p = _paper_or_404(pid, uid)
    return sse(llm.stream_chat(features.explain_messages(p, body.text, body.page, body.question, body.history), task="explain"))


@app.post("/api/papers/{pid}/translate")
async def translate(pid: str, uid: Uid, body: SelectionIn):
    p = _paper_or_404(pid, uid)
    return sse(llm.stream_chat(features.translate_messages(p, body.text, body.page), task="translate"))


class PageIn(BaseModel):
    page: int


@app.post("/api/papers/{pid}/translate-page")
async def translate_page(pid: str, uid: Uid, body: PageIn):
    p = _paper_or_404(pid, uid)
    cached = db.cache_get(pid, "page_translation", str(body.page))
    if cached:
        return sse(_cached_text(cached))
    return sse(llm.stream_chat(features.page_translate_messages(p, body.page), task="translate", max_tokens=4096),
               on_done=lambda t: db.cache_set(pid, "page_translation", t, str(body.page)))


@app.post("/api/papers/{pid}/translate-blocks")
async def translate_blocks(pid: str, uid: Uid, body: PageIn):
    """對照翻譯（SSE）。第一則訊息是整頁的區塊座標 {"blocks": [...]}，
    之後每翻完一段推一則 {"i": 序號, "tr": 譯文}。整頁翻完才寫快取。"""
    return sse(_block_translation(_paper_or_404(pid, uid), body.page))


async def _block_translation(p: dict, page: int) -> AsyncIterator[str]:
    pid, key = p["id"], str(page)
    cached = db.cache_get(pid, "block_translation", key)
    if cached:
        yield json.dumps({"blocks": cached}, ensure_ascii=False)
        return
    blocks = [{"bbox": b.bbox, "text": b.text, "size": b.size}
              for b in await asyncio.to_thread(pdf_parse.page_blocks, _pdf_path(pid), page)]
    yield json.dumps({"blocks": blocks}, ensure_ascii=False)
    failed = False
    async for item in features.stream_block_translation(p, blocks):
        if "error" in item:
            failed = True
        else:
            blocks[item["i"]]["tr"] = item["tr"]
        yield json.dumps(item, ensure_ascii=False)
    if not failed:
        db.cache_set(pid, "block_translation", blocks, key)


class AlignIn(BaseModel):
    page: int
    block: int
    quote: str = Field(min_length=1, max_length=2000)
    direction: Literal["en2zh", "zh2en"] = "en2zh"


@app.post("/api/papers/{pid}/align")
async def align(pid: str, uid: Uid, body: AlignIn):
    """中英對齊：在對照翻譯的同一個區塊裡，找出 quote 對應的那段。
    回傳 {"match": 對應段落（必是子字串，找不到為 ""）, "fallback": 是否只能標整段}；
    zh2en 另回 "rects"：英文原句在頁上的位置（找不到就是整個區塊）。"""
    p = _paper_or_404(pid, uid)
    blocks = db.cache_get(pid, "block_translation", str(body.page)) or []
    if not 0 <= body.block < len(blocks) or not blocks[body.block].get("tr"):
        raise HTTPException(409, "translation not ready")
    b = blocks[body.block]
    src, dst = (b["text"], b["tr"]) if body.direction == "en2zh" else (b["tr"], b["text"])
    key = f"{body.page}:{body.block}:{body.direction}:{body.quote}"
    match = db.cache_get(pid, "align", key)
    if match is None:
        match = await features.align_span(src, dst, body.quote)
        if match:  # 失敗的不快取：可能只是暫時連不上
            db.cache_set(pid, "align", match, key)
    out = {"match": match, "fallback": not match}
    if body.direction == "zh2en":
        x0, y0, x1, y1 = b["bbox"]
        hits = await asyncio.to_thread(pdf_parse.find_text_rects, _pdf_path(pid), body.page, match) if match else []
        # 同一句可能在頁上出現好幾次，只留這個區塊裡的
        out["rects"] = [r for r in hits if x0 - .01 <= (r[0] + r[2]) / 2 <= x1 + .01
                        and y0 - .01 <= (r[1] + r[3]) / 2 <= y1 + .01] or [b["bbox"]]
    return out


_bg_tasks: set[asyncio.Task] = set()
_translating: set[str] = set()  # 背景翻譯中的論文 id（卡片進度圈用）


async def _pretranslate(pid: str) -> None:
    """背景逐頁跑對照翻譯，結果進快取；之後打開那頁就直接顯示。"""
    # shortcut: 使用者若在背景跑完前打開同一頁，會重複翻一次（多花一點 token）；之後可加 per-page 鎖
    p = db.get_paper(pid)
    _translating.add(pid)
    try:
        for page in range(p["meta"]["num_pages"]):
            if not db.get_paper(pid):  # 中途被刪了就停
                return
            try:
                async for _ in _block_translation(p, page):
                    pass
            except Exception as e:  # 某頁失敗不影響其他頁；打開那頁時會再試
                print(f"[pretranslate] {pid} p.{page}: {type(e).__name__}: {e}")
    finally:
        _translating.discard(pid)


class ImageIn(BaseModel):
    image: str  # data:image/png;base64,...
    page: int = 0
    question: str = ""
    history: str = ""


@app.post("/api/papers/{pid}/explain-image")
async def explain_image(pid: str, uid: Uid, body: ImageIn):
    p = _paper_or_404(pid, uid)
    return sse(llm.stream_chat(features.image_messages(p, body.image, body.page, body.question, body.history), task="vision"))


class ChatIn(BaseModel):
    question: str
    page: int | None = None


@app.post("/api/papers/{pid}/chat")
async def chat(pid: str, uid: Uid, body: ChatIn):
    p = _paper_or_404(pid, uid)
    history = db.list_messages(pid)
    msgs, _hits = await features.chat_messages(p, history, body.question, body.page)
    db.add_message(pid, "user", body.question)
    return sse(llm.stream_chat(msgs, task="chat"), on_done=lambda t: db.add_message(pid, "assistant", t))


@app.get("/api/papers/{pid}/chat")
def chat_history(pid: str, uid: Uid):
    _paper_or_404(pid, uid)
    return db.list_messages(pid, limit=200)


@app.delete("/api/papers/{pid}/chat")
def chat_clear(pid: str, uid: Uid):
    _paper_or_404(pid, uid)
    db.clear_messages(pid)
    return {"ok": True}


@app.get("/api/papers/{pid}/summary")
async def summary(pid: str, uid: Uid, refresh: bool = False):
    p = _paper_or_404(pid, uid)
    cached = None if refresh else db.cache_get(pid, "summary")
    if cached:
        return sse(_cached_text(cached))
    return sse(llm.stream_chat(features.summary_messages(p), task="summary", max_tokens=3000),
               on_done=lambda t: db.cache_set(pid, "summary", t))


@app.post("/api/papers/{pid}/auto-highlight")
async def auto_highlight(pid: str, uid: Uid, refresh: bool = False):
    p = _paper_or_404(pid, uid) | {"id": pid}
    existing = [a for a in db.list_annotations(pid) if a["kind"].startswith("auto:")]
    if existing and not refresh:
        return existing
    for a in existing:
        db.delete_annotation(a["id"])
    hls = await features.auto_highlight(p, _pdf_path(pid))
    return [db.add_annotation(pid, h) for h in hls]


@app.get("/api/papers/{pid}/outline-ai")
async def outline_ai(pid: str, uid: Uid):
    p = _paper_or_404(pid, uid)
    cached = db.cache_get(pid, "outline")
    if cached is None:
        cached = await features.ai_outline(p)
        db.cache_set(pid, "outline", cached)
    return cached


def _figures(pid: str) -> list[dict]:
    cached = db.cache_get(pid, "figures")
    if cached is None:
        cached = pdf_parse.find_figures(_pdf_path(pid))
        db.cache_set(pid, "figures", cached)
    return cached


@app.get("/api/papers/{pid}/figures")
def figures(pid: str, uid: Uid):
    """所有圖 / 表的位置與圖說，前端滑過 "Figure 3" 時用來預覽。"""
    _paper_or_404(pid, uid)
    return _figures(pid)


@app.get("/api/papers/{pid}/figures/{kind}/{num}.png")
def figure_png(pid: str, uid: Uid, kind: str, num: str):
    _paper_or_404(pid, uid)
    fig = next((f for f in _figures(pid) if f["kind"] == kind and f["num"] == num), None)
    if not fig:
        raise HTTPException(404, "找不到這張圖")
    png = pdf_parse.render_page_png(_pdf_path(pid), fig["page"], 144, fig["bbox"])
    return Response(png, media_type="image/png", headers={"Cache-Control": "max-age=86400"})


def _mark_in_library(recs: list[dict], uid: str) -> list[dict]:
    """推薦清單裡已經在論文庫的，標上 in_library（用 arXiv 編號或標題比對）。"""
    have_arxiv, have_title = set(), set()
    for p in db.list_papers(uid):
        m = re.match(r"arXiv-(\d{4}\.\d{4,5})", p["filename"] or "")
        if m:
            have_arxiv.add(m.group(1))
        have_title.add((p["title"] or "").lower().strip())
    for r in recs:
        ax = (r.get("externalIds") or {}).get("ArXiv")
        r["in_library"] = ax in have_arxiv or (r.get("title") or "").lower().strip() in have_title
    return recs


@app.get("/api/papers/{pid}/related")
async def related(pid: str, uid: Uid, refresh: bool = False):
    """與這篇相關的論文。"""
    p = _paper_or_404(pid, uid)
    if not config.SEMANTIC_SCHOLAR_LOOKUP:
        raise HTTPException(503, "已關閉 Semantic Scholar（.env 的 SEMANTIC_SCHOLAR_LOOKUP=false），沒有推薦資料來源")
    cached = None if refresh else db.cache_get(pid, "related")
    if cached is None:
        try:
            sid = await features.s2_paper_id(p)
            if not sid:
                raise HTTPException(404, "Semantic Scholar 找不到這篇論文，無法推薦")
            cached = await features.recommend([sid])
        except features.S2Error as e:
            raise HTTPException(503, str(e))
        db.cache_set(pid, "related", cached)
    return _mark_in_library(cached, uid)


@app.get("/api/recommendations")
async def recommendations(uid: Uid):
    """依整個論文庫推薦（Moonlight 的 Scholar Deep Search 類似功能）。"""
    if not config.SEMANTIC_SCHOLAR_LOOKUP:
        raise HTTPException(503, "已關閉 Semantic Scholar（.env 的 SEMANTIC_SCHOLAR_LOOKUP=false），沒有推薦資料來源")
    ids = []
    try:
        for p in db.list_papers(uid)[:30]:
            sid = await features.s2_paper_id(db.get_paper(p["id"]))
            if sid:
                ids.append(sid)
        if not ids:
            raise HTTPException(404, "論文庫是空的，或都在 Semantic Scholar 找不到")
        recs = await features.recommend(ids, limit=20)
    except features.S2Error as e:
        raise HTTPException(503, str(e))
    return _mark_in_library(recs, uid)


@app.get("/api/papers/{pid}/region.png")
def region_png(pid: str, uid: Uid, page: int, x0: float, y0: float, x1: float, y1: float):
    """頁面上任一塊區域（0~1 座標）的 PNG：接續框選解釋的對話時，重新取得當時框的圖。"""
    p = _paper_or_404(pid, uid)
    if not (0 <= page < p["meta"]["num_pages"] and 0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        raise HTTPException(400, "頁碼或區域超出範圍")
    png = pdf_parse.render_page_png(_pdf_path(pid), page, 150, [x0, y0, x1, y1])
    return Response(png, media_type="image/png", headers={"Cache-Control": "max-age=86400"})


@app.get("/api/papers/{pid}/reference-search")
async def reference_search(pid: str, uid: Uid, author: str, year: str):
    """作者-年份引用：(Peters et al., 2018a) → author=Peters&year=2018a"""
    p = _paper_or_404(pid, uid)
    key = pdf_parse.match_author_year(p["meta"]["references"], author, year)
    if key is None:
        return {"num": f"{author} {year}", "raw": None, "paper": None}
    return await reference(pid, uid, key)


@app.get("/api/papers/{pid}/reference/{num}")
async def reference(pid: str, uid: Uid, num: str):
    p = _paper_or_404(pid, uid)
    cached = db.cache_get(pid, "reference", num)
    if cached is None:
        cached = await features.lookup_reference(p, num)
        if cached.get("paper"):
            db.cache_set(pid, "reference", cached, num)
    return cached


@app.get("/api/papers/{pid}/references")
def references(pid: str, uid: Uid):
    """整篇的參考文獻清單，給活動面板的「引用」分頁。"""
    refs = _paper_or_404(pid, uid)["meta"]["references"]
    return [{"num": k, "raw": v} for k, v in refs.items()]


@app.get("/api/papers/{pid}/reference/{num}/why")
async def reference_why(pid: str, uid: Uid, num: str):
    """引用卡片的「為何引用」：找出正文引用它的句子，請 AI 說明引用原因、值不值得讀（SSE，會快取）。"""
    p = _paper_or_404(pid, uid)
    ref = p["meta"]["references"].get(num)
    if not ref:
        raise HTTPException(404, "找不到這筆參考文獻")
    cached = db.cache_get(pid, "cite_reason", num)
    if cached:
        return sse(_cached_text(cached))
    return sse(llm.stream_chat(features.cite_reason_messages(p, num, ref), task="cite"),
               on_done=lambda t: db.cache_set(pid, "cite_reason", t, num))


@app.get("/api/papers/{pid}/suggestions")
async def suggestions(pid: str, uid: Uid):
    p = _paper_or_404(pid, uid)
    cached = db.cache_get(pid, "suggestions")
    if cached is None:
        cached = await features.suggested_questions(p)
        if cached:
            db.cache_set(pid, "suggestions", cached)
    return cached

# ---------------- 註解 ----------------
class AlignMark(BaseModel):
    """螢光筆在譯文裡的對應：第 block 個翻譯區塊裡的 zh 這段（空字串 = 標整段）。"""
    block: int = Field(ge=0)
    zh: str = Field("", max_length=4000)


class AnnotIn(BaseModel):
    page: int
    rects: list[list[float]]
    # 標準色名稱或自訂色 #rrggbb；explain / image / comment 是解釋（文字 / 框選）與註解的標記
    color: str = Field("yellow", pattern=r"^(yellow|green|blue|pink|purple|explain|image|comment|#[0-9a-fA-F]{6})$")
    text: str = ""
    comment: str = ""  # 螢光筆的備註；kind=explain 時存 AI 的解釋（含追問）；kind=comment 時是註解內容
    kind: Literal["user", "explain", "comment"] = "user"  # auto:* 只能由自動標註產生
    align: AlignMark | None = None


@app.get("/api/papers/{pid}/annotations")
def annotations(pid: str, uid: Uid):
    _paper_or_404(pid, uid)
    return db.list_annotations(pid)


@app.post("/api/papers/{pid}/annotations")
def add_annotation(pid: str, uid: Uid, body: AnnotIn):
    _paper_or_404(pid, uid)
    return db.add_annotation(pid, body.model_dump())


class CommentIn(BaseModel):
    comment: str | None = None
    align: AlignMark | None = None


def _own_annotation(aid: str, uid: str) -> None:
    pid = db.annotation_paper(aid)
    if not pid:
        raise HTTPException(404, "annotation not found")
    _paper_or_404(pid, uid)


@app.patch("/api/annotations/{aid}")
def edit_annotation(aid: str, body: CommentIn, uid: Uid):
    _own_annotation(aid, uid)
    db.update_annotation(aid, body.comment, body.align.model_dump() if body.align else None)
    return {"ok": True}


@app.delete("/api/annotations/{aid}")
def remove_annotation(aid: str, uid: Uid):
    _own_annotation(aid, uid)
    db.delete_annotation(aid)
    return {"ok": True}


# ---------------- Workspace ----------------
class NameIn(BaseModel):
    name: str = Field(min_length=1)


class PaperRefIn(BaseModel):
    paper_id: str


@app.get("/api/workspaces")
def workspaces(uid: Uid):
    return db.list_workspaces(uid)


@app.post("/api/workspaces")
def create_workspace(body: NameIn, uid: Uid):
    return db.get_workspace(uid, db.add_workspace(uid, body.name.strip()))


@app.patch("/api/workspaces/{wid}")
def rename_workspace(wid: str, body: NameIn, uid: Uid):
    _ws_or_404(wid, uid)
    db.rename_workspace(wid, body.name.strip())
    return _ws_or_404(wid, uid)


@app.delete("/api/workspaces/{wid}")
def delete_workspace(wid: str, uid: Uid):
    _ws_or_404(wid, uid)
    db.delete_workspace(wid)
    return {"ok": True}


@app.post("/api/workspaces/{wid}/papers")
async def add_to_workspace(wid: str, body: PaperRefIn, uid: Uid):  # async：背景任務要在事件迴圈裡建立
    _ws_or_404(wid, uid)
    _paper_or_404(body.paper_id, uid)
    db.add_to_workspace(wid, body.paper_id)
    _auto_wiki(uid, wid)
    return {"ok": True}


@app.delete("/api/workspaces/{wid}/papers/{pid}")
def remove_from_workspace(wid: str, pid: str, uid: Uid):
    _ws_or_404(wid, uid)
    db.remove_from_workspace(wid, pid)
    return {"ok": True}


# ---------------- Workspace wiki（docs/wiki.md）----------------
# 正在跑的更新：wid → 已推出的進度（None = 結束）。更新是背景任務，不綁瀏覽器連線：
# 重新整理或離開頁面不會中斷，再打開 Wiki 會接回同一個進度。
_wiki_jobs: dict[str, list] = {}  # shortcut: in-process state, breaks with multiple uvicorn workers


async def _wiki_job(wid: str, uid: str) -> None:
    steps = _wiki_jobs[wid]
    try:
        while True:
            async for step in features.update_wiki(wid):
                steps.append(step)
            # 跑的期間又加了論文、且 auto_wiki 仍開著 → 接著再跑一輪
            if not (db.wiki_pending(wid) and db.get_settings(uid).get("auto_wiki")):
                break
    except Exception as e:  # 已整理好的論文已寫入 wiki_ingested，再按一次只做剩下的
        steps.append({"error": f"{type(e).__name__}: {e}"})
    finally:
        steps.append(None)
        _wiki_jobs.pop(wid, None)


def _start_wiki(wid: str, uid: str) -> list:
    """沒在跑就啟動背景更新；回傳該任務的進度串列。"""
    if wid not in _wiki_jobs:
        _wiki_jobs[wid] = []
        task = asyncio.create_task(_wiki_job(wid, uid))
        _bg_tasks.add(task)
        task.add_done_callback(_bg_tasks.discard)
    return _wiki_jobs[wid]


def _auto_wiki(uid: str, wid: str) -> None:
    if db.get_settings(uid).get("auto_wiki"):
        _start_wiki(wid, uid)


@app.get("/api/workspaces/{wid}/wiki")
def wiki(wid: str, uid: Uid):
    _ws_or_404(wid, uid)
    return {"pages": db.wiki_pages(wid), "pending": len(db.wiki_pending(wid)), "running": wid in _wiki_jobs}


@app.get("/api/workspaces/{wid}/wiki/{slug}")
def wiki_page(wid: str, slug: str, uid: Uid):
    _ws_or_404(wid, uid)
    page = db.wiki_page(wid, slug)
    if not page:
        raise HTTPException(404, "wiki page not found")
    return page


@app.post("/api/workspaces/{wid}/wiki/update")
async def wiki_update(wid: str, uid: Uid):
    """開始更新；已經在跑就接上同一個進度（不會跑第二份）。"""
    _ws_or_404(wid, uid)
    steps = _start_wiki(wid, uid)

    async def follow() -> AsyncIterator[str]:
        i = 0
        while True:
            while i >= len(steps):
                await asyncio.sleep(0.3)
            step, i = steps[i], i + 1
            if step is None:
                return
            if "error" in step:
                raise RuntimeError(step["error"])
            yield json.dumps(step, ensure_ascii=False)

    return sse(follow())


class AskIn(BaseModel):
    question: str


class QaIn(BaseModel):
    question: str
    answer: str


@app.post("/api/workspaces/{wid}/ask")
async def wiki_ask(wid: str, uid: Uid, body: AskIn):
    _ws_or_404(wid, uid)
    if not db.wiki_pages(wid):
        raise HTTPException(400, "先按更新 Wiki")
    msgs = await features.wiki_ask_messages(wid, db.list_wiki_messages(wid), body.question)
    db.add_wiki_message(wid, "user", body.question)
    return sse(llm.stream_chat(msgs, task="wiki"), on_done=lambda t: db.add_wiki_message(wid, "assistant", t))


@app.get("/api/workspaces/{wid}/ask")
def wiki_ask_history(wid: str, uid: Uid):
    _ws_or_404(wid, uid)
    return db.list_wiki_messages(wid)


@app.delete("/api/workspaces/{wid}/ask")
def wiki_ask_clear(wid: str, uid: Uid):
    _ws_or_404(wid, uid)
    db.clear_wiki_messages(wid)
    return {"ok": True}


@app.delete("/api/workspaces/{wid}/ask/{mid}")
def wiki_ask_delete(wid: str, mid: int, uid: Uid):
    """刪單一題（問題 id 來自 GET /ask），連同它的回答。"""
    _ws_or_404(wid, uid)
    if not db.delete_wiki_exchange(wid, mid):
        raise HTTPException(404, "question not found")
    return {"ok": True}


@app.post("/api/workspaces/{wid}/ask/save")
async def wiki_ask_save(wid: str, uid: Uid, body: QaIn):
    _ws_or_404(wid, uid)
    page = await features.wiki_qa_page(body.question, body.answer)
    cited = set(re.findall(r"\[\[paper:([\w-]+)", body.answer))
    sources = sorted(cited & {p["id"] for p in db.list_papers(uid, wid)})  # 只收這個 workspace 的論文
    slug = f"qa-{db.new_id()}"
    db.wiki_save(wid, slug, page["title"], page["markdown"], sources)
    return {"slug": slug, "title": page["title"]}


@app.get("/api/papers/{pid}/wiki")
def paper_wiki(pid: str, uid: Uid):
    _paper_or_404(pid, uid)
    return db.wiki_backlinks(uid, pid)


@app.get("/api/health")
async def health():
    """檢查每個模型角色的連線：在瀏覽器打開 /api/health 就知道哪個 API 沒接好。
    tasks 列出每個元件實際用的「服務商:模型」；另外指定模型的元件也會各測一次。

    llm   文字（解釋、翻譯、聊天、摘要、標註）
    vlm   看圖（框選圖表、圖表預覽解釋）— 會送一張測試圖
    ocr   掃描頁轉文字（跟 vlm 同一組設定時不重複測）
    embed 語意檢索（沒設就略過，改用 BM25）
    """
    if config.LLM_MOCK:
        return {"ok": True, "mock": True}
    roles = ["llm", "vlm"]
    vlm_id = (config.VLM_BASE_URL, config.VLM_MODEL or config.LLM_MODEL)
    if config.OCR_ENABLED and (config.OCR_BASE_URL, config.OCR_MODEL) != vlm_id:
        roles.append("ocr")
    if config.EMBED_MODEL:
        roles.append("embed")
    # 各元件另外指定的模型：每個不同的模型測一次（用第一個用到它的元件當代表）
    default = llm.route("llm")[::2]
    extra: dict[tuple, str] = {}
    for t in config.TEXT_TASKS:
        key = llm.route(t)[::2]
        if key != default:
            extra.setdefault(key, t)
    roles += list(extra.values())
    results = dict(zip(roles, await asyncio.gather(*(llm.check(r) for r in roles))))
    results["tasks"] = {t: "{}:{}".format(*llm.route(t)[::2]) for t in config.TEXT_TASKS}
    if "ocr" not in results and config.OCR_ENABLED:
        results["ocr"] = {"same_as": "vlm"}
    if "embed" not in results:
        results["embed"] = {"skipped": "沒設 EMBED_MODEL，檢索用 BM25"}
    # 文字模型是必要的；其他壞掉只影響對應功能
    return {"ok": results["llm"]["ok"], "all_ok": all(r.get("ok", True) for r in results.values()),
            **results}


class _FrontendFiles(StaticFiles):
    """前端檔案每次都跟伺服器確認版本（有 ETag，沒改就回 304 不重傳），
    否則瀏覽器會拿快取裡的舊 CSS / JS，改版後要強制重新整理才看得到。"""

    async def get_response(self, path, scope):
        resp = await super().get_response(path, scope)
        resp.headers["Cache-Control"] = "no-cache"
        return resp


# 前端靜態檔：放最後，才不會蓋掉 /api 路由
app.mount("/", _FrontendFiles(directory=config.ROOT / "frontend", html=True), name="frontend")
