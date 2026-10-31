"""功能測試：透過 FastAPI 的 API 跑每個功能，模型是 tests/fake_api.py 的挑剔假 API。"""
from __future__ import annotations

import base64
import json

from backend import config
from tests import fake_api
from tests.conftest import sse


def _id(papers, name):
    return papers[name]["id"]


# ---------------- 匯入 ----------------
def test_upload(papers):
    p = papers["numeric"]
    assert p["title"] == "Sparse Lantern Networks for Document Reading"
    assert p["num_pages"] == 3 and p["chunks"] > 3 and p["scanned_pages"] == 0


def test_scanned_upload_runs_ocr(papers, client):
    p = papers["scanned"]
    assert p["scanned_pages"] == 3 and p["ocr_pages"] == 3 and p["ocr_error"] is None
    info = client.get(f"/api/papers/{p['id']}").json()
    assert info["ocr_pages"] == [0, 1, 2]
    assert p["chunks"] > 0  # OCR 文字有進檢索索引


def test_reject_non_pdf(client):
    r = client.post("/api/papers", files={"file": ("a.txt", b"hello", "text/plain")})
    assert r.status_code == 400


# ---------------- 連線檢查與參數相容 ----------------
def test_health_adapts_params_per_model(client):
    h = client.get("/api/health").json()
    assert h["ok"] and h["all_ok"], h
    assert h["llm"]["adjusted"] == ["no_template_kwargs", "max_completion_tokens"]
    assert h["vlm"]["adjusted"] == ["no_template_kwargs"]  # vision-model 收 max_tokens
    assert "no_temperature" in h["ocr"]["adjusted"]
    assert h["embed"]["dim"] == 8


def test_learned_params_are_reused(papers, client):
    body = {"text": "lantern encoder", "page": 0}
    sse(client, "POST", f"/api/papers/{_id(papers, 'numeric')}/explain", body)  # 第一次：被拒、退讓、記住
    fake_api.calls.clear()
    sse(client, "POST", f"/api/papers/{_id(papers, 'numeric')}/explain", body)
    sent = [c["params"] for c in fake_api.calls if c["model"] == "strict-model"]
    assert len(sent) == 1, "學到的參數組合應該直接用，不該再被拒一次"
    assert "max_completion_tokens" in sent[0] and "chat_template_kwargs" not in sent[0]


# ---------------- 選字、翻譯 ----------------
def test_explain_strips_think(papers, client):
    text, _, err = sse(client, "POST", f"/api/papers/{_id(papers, 'numeric')}/explain",
                       {"text": "lantern encoder", "page": 0})
    assert err is None and text.strip() == "這是假 API 的回答 [p.1]。"


def test_translate_selection(papers, client):
    text, _, err = sse(client, "POST", f"/api/papers/{_id(papers, 'numeric')}/translate",
                       {"text": "We propose a new method.", "page": 0})
    assert err is None and text


def test_translate_page(papers, client):
    pid = _id(papers, "numeric")
    first, _, err = sse(client, "POST", f"/api/papers/{pid}/translate-page", {"page": 0})
    again, _, _ = sse(client, "POST", f"/api/papers/{pid}/translate-page", {"page": 0})
    assert err is None and first and again == first  # 第二次走快取


def test_bilingual_blocks(papers, client):
    pid = _id(papers, "numeric")
    _, events, err = sse(client, "POST", f"/api/papers/{pid}/translate-blocks", {"page": 0})
    evs = [json.loads(e) for e in events]
    blocks = evs[0]["blocks"]
    done = {e["i"]: e["tr"] for e in evs[1:]}
    assert err is None and blocks and all("bbox" in b and "size" in b for b in blocks)
    assert done and all(t.startswith("第") for t in done.values())
    # 第二次：直接回快取，只有一則訊息，譯文都在
    _, ev2, _ = sse(client, "POST", f"/api/papers/{pid}/translate-blocks", {"page": 0})
    cached = json.loads(ev2[0])["blocks"]
    assert len(ev2) == 1 and sum("tr" in b for b in cached) == len(done)


# ---------------- 聊天、摘要、標註、大綱 ----------------
def test_chat_rag_with_embeddings(papers, client):
    pid = _id(papers, "numeric")
    assert client.get(f"/api/papers/{pid}").json()["full_text_fits"] is False  # 確定走 RAG
    text, _, err = sse(client, "POST", f"/api/papers/{pid}/chat", {"question": "What is the lantern encoder?", "page": 0})
    assert err is None and text
    hist = client.get(f"/api/papers/{pid}/chat").json()
    assert [m["role"] for m in hist][-2:] == ["user", "assistant"]
    client.delete(f"/api/papers/{pid}/chat")
    assert client.get(f"/api/papers/{pid}/chat").json() == []


def test_chat_after_switching_embedding_model(papers, client, monkeypatch):
    """換了 embedding 模型（維度 8 → 16）：舊論文要退回 BM25，不能當掉。"""
    monkeypatch.setattr(config, "EMBED_MODEL", "emb-b")
    text, _, err = sse(client, "POST", f"/api/papers/{_id(papers, 'numeric')}/chat",
                       {"question": "lantern encoder memory", "page": 0})
    assert err is None and text


def test_summary_cached(papers, client):
    pid = _id(papers, "numeric")
    a, _, err = sse(client, "GET", f"/api/papers/{pid}/summary")
    b, _, _ = sse(client, "GET", f"/api/papers/{pid}/summary")
    assert err is None and a and a == b


def test_auto_highlight_finds_sentence(papers, client):
    hls = client.post(f"/api/papers/{_id(papers, 'numeric')}/auto-highlight").json()
    assert hls and all(h["rects"] and h["kind"].startswith("auto:") for h in hls)


def test_ai_outline(papers, client):
    out = client.get(f"/api/papers/{_id(papers, 'numeric')}/outline-ai").json()
    assert out == [{"level": 1, "title": "1 Introduction", "page": 0}]


# ---------------- 圖表 ----------------
def test_figures_and_png(papers, client):
    pid = _id(papers, "numeric")
    figs = client.get(f"/api/papers/{pid}/figures").json()
    assert {(f["kind"], f["num"]) for f in figs} == {("figure", "1"), ("table", "1")}
    r = client.get(f"/api/papers/{pid}/figures/figure/1.png")
    assert r.status_code == 200 and r.headers["content-type"] == "image/png"
    assert client.get(f"/api/papers/{pid}/figures/figure/9.png").status_code == 404


def test_explain_image(papers, client):
    pid = _id(papers, "numeric")
    png = client.get(f"/api/papers/{pid}/figures/figure/1.png").content
    url = "data:image/png;base64," + base64.b64encode(png).decode()
    text, _, err = sse(client, "POST", f"/api/papers/{pid}/explain-image", {"image": url, "page": 1})
    assert err is None and text == "白色"


def test_explain_image_with_text_only_model(papers, client, monkeypatch):
    """視覺模型其實不收圖：要回清楚的錯誤（真正原因），不是當掉、也不是參數錯誤。"""
    monkeypatch.setattr(config, "VLM_MODEL", "text-only")
    pid = _id(papers, "numeric")
    png = client.get(f"/api/papers/{pid}/figures/figure/1.png").content
    url = "data:image/png;base64," + base64.b64encode(png).decode()
    _, _, err = sse(client, "POST", f"/api/papers/{pid}/explain-image", {"image": url, "page": 1})
    assert err and "does not support image" in err


# ---------------- 引用 ----------------
def test_numeric_reference(papers, client):
    r = client.get(f"/api/papers/{_id(papers, 'numeric')}/reference/2").json()
    assert "Retrieval-augmented generation" in r["raw"]


def test_author_year_reference(papers, client):
    pid = _id(papers, "authoryear")
    r = client.get(f"/api/papers/{pid}/reference-search", params={"author": "Peters", "year": "2018b"}).json()
    assert "Dissecting" in r["raw"]
    r = client.get(f"/api/papers/{pid}/reference-search", params={"author": "Nobody", "year": "2001"}).json()
    assert r["raw"] is None


# ---------------- 論文庫、註解 ----------------
def test_tags_and_fulltext_search(papers, client):
    pid = _id(papers, "numeric")
    r = client.patch(f"/api/papers/{pid}", json={"tags": [" NLP", "必讀", "NLP", ""]}).json()
    assert r["tags"] == ["NLP", "必讀"]  # 去空白、去重複
    assert next(p for p in client.get("/api/papers").json() if p["id"] == pid)["tags"] == ["NLP", "必讀"]
    hits = client.get("/api/search", params={"q": "lantern encoder"}).json()
    assert hits and all("lantern encoder" in h["snippet"].lower() for h in hits)
    assert client.get("/api/search", params={"q": "100%_"}).json() == []  # 萬用字元要被跳脫


def test_annotations_crud(papers, client):
    pid = _id(papers, "numeric")
    a = client.post(f"/api/papers/{pid}/annotations",
                    json={"page": 0, "rects": [[0.1, 0.1, 0.3, 0.12]], "text": "x"}).json()
    client.patch(f"/api/annotations/{a['id']}", json={"comment": "重要"})
    got = [x for x in client.get(f"/api/papers/{pid}/annotations").json() if x["id"] == a["id"]]
    assert got[0]["comment"] == "重要"
    client.delete(f"/api/annotations/{a['id']}")
    assert all(x["id"] != a["id"] for x in client.get(f"/api/papers/{pid}/annotations").json())


def test_mock_mode(papers, client, monkeypatch):
    monkeypatch.setattr(config, "LLM_MOCK", True)
    text, _, _ = sse(client, "POST", f"/api/papers/{_id(papers, 'numeric')}/explain", {"text": "x", "page": 0})
    assert "MOCK" in text


def test_delete_paper(client, pdfs, allow_duplicates):
    with open(pdfs["numeric"], "rb") as f:
        pid = client.post("/api/papers", files={"file": ("tmp.pdf", f, "application/pdf")}).json()["id"]
    assert client.delete(f"/api/papers/{pid}").json() == {"ok": True}
    assert client.get(f"/api/papers/{pid}").status_code == 404


# ---------------- 仿 Moonlight 介面用到的 API ----------------
def test_ask_ai_on_selection(papers, client):
    fake_api.calls.clear()
    text, _, err = sse(client, "POST", f"/api/papers/{_id(papers, 'numeric')}/explain",
                       {"text": "lantern encoder", "page": 0, "question": "它跟 RNN 有什麼不同？"})
    assert err is None and text
    assert "它跟 RNN 有什麼不同？" in fake_api.calls[-1]["prompt"]


def test_annotation_kinds(papers, client):
    pid = _id(papers, "numeric")
    for kind in ("explain", "comment"):
        a = client.post(f"/api/papers/{pid}/annotations",
                        json={"page": 0, "rects": [[0.1, 0.1, 0.2, 0.12]], "text": "x", "kind": kind, "comment": "c"}).json()
        assert a["kind"] == kind
        client.delete(f"/api/annotations/{a['id']}")
    # auto:* 只能由自動標註產生，前端不能自己塞
    r = client.post(f"/api/papers/{pid}/annotations", json={"page": 0, "rects": [], "kind": "auto:novelty"})
    assert r.status_code == 422


def test_reference_list_and_why(papers, client):
    pid = _id(papers, "numeric")
    refs = client.get(f"/api/papers/{pid}/references").json()
    assert [r["num"] for r in refs] == ["1", "2", "3", "4"]
    fake_api.calls.clear()
    text, _, err = sse(client, "GET", f"/api/papers/{pid}/reference/2/why")
    assert err is None and text
    assert "[2, 3]" in fake_api.calls[-1]["prompt"]  # 找到正文裡引用它的句子
    again, _, _ = sse(client, "GET", f"/api/papers/{pid}/reference/2/why")
    assert again == text  # 第二次走快取
    assert client.get(f"/api/papers/{pid}/reference/99/why").status_code == 404


def test_suggestions_cached(papers, client):
    pid = _id(papers, "numeric")
    qs = client.get(f"/api/papers/{pid}/suggestions").json()
    assert qs == ["主要貢獻是什麼？", "方法怎麼運作？", "結果代表什麼？"]
    fake_api.calls.clear()
    assert client.get(f"/api/papers/{pid}/suggestions").json() == qs and not fake_api.calls


# ---------------- 自訂色、接續對話、區域圖、網址匯入 ----------------
def test_custom_highlight_color(papers, client):
    pid = _id(papers, "numeric")
    ok = client.post(f"/api/papers/{pid}/annotations", json={"page": 0, "rects": [[0.1, 0.1, 0.2, 0.12]], "color": "#7f9ea0"})
    assert ok.status_code == 200 and ok.json()["color"] == "#7f9ea0"
    client.delete(f"/api/annotations/{ok.json()['id']}")
    for bad in ("red", "#12345", "#zzzzzz", "yellow;background:url(x)"):
        r = client.post(f"/api/papers/{pid}/annotations", json={"page": 0, "rects": [], "color": bad})
        assert r.status_code == 422, bad


def test_followup_carries_history(papers, client):
    fake_api.calls.clear()
    history = "**問：**它跟 RNN 有什麼不同？\n\n不需要循環結構。"
    sse(client, "POST", f"/api/papers/{_id(papers, 'numeric')}/explain",
        {"text": "lantern encoder", "page": 0, "question": "那速度呢？", "history": history})
    prompt = fake_api.calls[-1]["prompt"]
    assert "不需要循環結構" in prompt and "那速度呢？" in prompt


def test_region_png(papers, client):
    pid = _id(papers, "numeric")
    r = client.get(f"/api/papers/{pid}/region.png", params={"page": 1, "x0": 0.1, "y0": 0.2, "x1": 0.9, "y1": 0.5})
    assert r.status_code == 200 and r.content[:4] == b"\x89PNG"
    bad = client.get(f"/api/papers/{pid}/region.png", params={"page": 1, "x0": 0.9, "y0": 0.2, "x1": 0.1, "y1": 0.5})
    assert bad.status_code == 400
    assert client.get(f"/api/papers/{pid}/region.png", params={"page": 99, "x0": 0, "y0": 0, "x1": 1, "y1": 1}).status_code == 400


def test_import_from_pdf_url(client, pdfs, allow_duplicates):
    from tests.conftest import PORT
    fake_api.pdf_bytes = pdfs["numeric"].read_bytes()
    r = client.post("/api/papers/arxiv", json={"url": f"http://127.0.0.1:{PORT}/files/journal-article.pdf?token=1"})
    assert r.status_code == 200, r.text
    p = client.get(f"/api/papers/{r.json()['id']}").json()
    assert p["filename"] == "journal-article.pdf" and p["title"] == "Sparse Lantern Networks for Document Reading"
    html = client.post("/api/papers/arxiv", json={"url": f"http://127.0.0.1:{PORT}/files/landing"})
    assert html.status_code == 400 and "不是 PDF" in html.json()["detail"]
    assert client.post("/api/papers/arxiv", json={"url": "not a url"}).status_code == 400
    client.delete(f"/api/papers/{r.json()['id']}")


def test_semantic_scholar_can_be_off(papers, client):
    # conftest 設了 SEMANTIC_SCHOLAR_LOOKUP=false：引用卡片只回原文，推薦明確說明已關閉
    pid = _id(papers, "numeric")
    ref = client.get(f"/api/papers/{pid}/reference/2").json()
    assert ref["raw"] and ref["paper"] is None
    r = client.get(f"/api/papers/{pid}/related")
    assert r.status_code == 503 and "SEMANTIC_SCHOLAR_LOOKUP" in r.json()["detail"]
