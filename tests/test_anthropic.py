"""LLM_PROVIDER=anthropic：走 Claude 官方 SDK，打 tests/fake_api.py 的假 Messages API。
除了功能結果，也檢查送出去的請求長得對（沒有 temperature、system 在頂層、圖片格式、快取斷點、fallback）。"""
from __future__ import annotations

import base64
import json

import pytest

from backend import config, llm
from tests import fake_api
from tests.conftest import sse

OPUS = "claude-opus-5-5"


@pytest.fixture
def claude(monkeypatch):
    monkeypatch.setattr(config, "LLM_PROVIDER", "anthropic")
    for name in ("LLM_MODEL", "VLM_MODEL", "OCR_MODEL"):
        monkeypatch.setattr(config, name, OPUS)
    fake_api.claude_calls.clear()
    return fake_api.claude_calls


def _pid(papers):
    return papers["numeric"]["id"]


# ---------------- 訊息轉換（純函式）----------------
def test_to_claude_conversion():
    png = "data:image/png;base64,QUJD"
    system, msgs = llm._to_claude([
        {"role": "system", "content": "規則一"},
        {"role": "user", "content": [{"type": "image_url", "image_url": {"url": png}}, {"type": "text", "text": "看圖"}]},
        {"role": "assistant", "content": "  "},  # 空白訊息要丟掉
        {"role": "system", "content": "規則二"},
    ])
    assert system == "規則一\n\n規則二"
    assert [m["role"] for m in msgs] == ["user"]
    assert msgs[0]["content"][0] == {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "QUJD"}}


def test_cache_breakpoint_only_for_multi_turn():
    _, single = llm._to_claude([{"role": "user", "content": "一次性的問題"}])
    assert single[0]["content"] == "一次性的問題"  # 不會重用的請求不寫快取（寫快取比原價貴）
    _, chat = llm._to_claude([{"role": "user", "content": "整篇論文"}, {"role": "assistant", "content": "好"},
                              {"role": "user", "content": "問題"}])
    assert chat[0]["content"][0]["cache_control"] == {"type": "ephemeral"}
    assert chat[-1]["content"] == "問題"


# ---------------- 功能 ----------------
def test_explain_request_shape(claude, papers, client):
    text, _, err = sse(client, "POST", f"/api/papers/{_pid(papers)}/explain", {"text": "lantern encoder", "page": 0})
    assert err is None and text == "這是假 API 的回答 [p.1]。"  # 思考區塊沒有混進回答
    body, beta = claude[-1]["body"], claude[-1]["beta"]
    assert body["model"] == OPUS and "temperature" not in body
    assert body["output_config"] == {"effort": config.LLM_EFFORT}
    assert body["system"] and body["max_tokens"] >= 16000
    assert body["fallbacks"] == "default" and "server-side-fallback-2026-07-01" in beta


def test_no_fallback_for_haiku(claude, papers, client, monkeypatch):
    monkeypatch.setattr(config, "LLM_MODEL", "claude-haiku-5-5")
    sse(client, "POST", f"/api/papers/{_pid(papers)}/translate", {"text": "We propose a method.", "page": 0})
    assert "fallbacks" not in claude[-1]["body"] and "server-side-fallback" not in claude[-1]["beta"]


def test_chat_uses_prompt_cache(claude, papers, client):
    pid = _pid(papers)
    client.delete(f"/api/papers/{pid}/chat")
    text, _, err = sse(client, "POST", f"/api/papers/{pid}/chat", {"question": "What is the lantern encoder?", "page": 0})
    assert err is None and text
    first_user = claude[-1]["body"]["messages"][0]
    assert first_user["content"][0]["cache_control"] == {"type": "ephemeral"}


def test_explain_image(claude, papers, client):
    pid = _pid(papers)
    png = client.get(f"/api/papers/{pid}/figures/figure/1.png").content
    url = "data:image/png;base64," + base64.b64encode(png).decode()
    text, _, err = sse(client, "POST", f"/api/papers/{pid}/explain-image", {"image": url, "page": 1})
    assert err is None and text == "白色"


def test_bilingual_blocks(claude, papers, client):
    pid = papers["authoryear"]["id"]  # 用另一篇，避開 openai 測試留下的快取
    _, events, err = sse(client, "POST", f"/api/papers/{pid}/translate-blocks", {"page": 0})
    done = [json.loads(e) for e in events[1:]]
    assert err is None and done and all(d["tr"].startswith("第") for d in done)


def test_auto_highlight_json(claude, papers, client):
    hls = client.post(f"/api/papers/{_pid(papers)}/auto-highlight?refresh=true").json()
    assert hls and all(h["rects"] for h in hls)


def test_ocr_scanned_pdf(claude, client, pdfs, allow_duplicates):
    with open(pdfs["scanned"], "rb") as f:
        r = client.post("/api/papers", files={"file": ("scan2.pdf", f, "application/pdf")}).json()
    assert r["ocr_pages"] == 3 and r["ocr_error"] is None and r["chunks"] > 0
    assert any(b["type"] == "image" for c in claude for m in c["body"]["messages"]
               if isinstance(m["content"], list) for b in m["content"])


def test_refusal_is_reported(claude, papers, client, monkeypatch):
    monkeypatch.setattr(config, "LLM_MODEL", "claude-refusing")
    _, _, err = sse(client, "POST", f"/api/papers/{_pid(papers)}/explain", {"text": "x", "page": 0})
    assert err and "拒絕" in err and "bio" in err


def test_health(claude, client):
    h = client.get("/api/health").json()
    assert h["ok"] and h["llm"]["model"] == OPUS and h["vlm"]["ok"]
    assert h["ocr"] == {"same_as": "vlm"}


# ---------------- 各元件用不同模型 ----------------
def test_route_prefixes(monkeypatch):
    monkeypatch.setattr(config, "LLM_PROVIDER", "anthropic")
    monkeypatch.setattr(config, "LLM_MODEL", OPUS)
    monkeypatch.setitem(config.TASK_MODELS, "translate", "openai:qwen3.5-9b")
    monkeypatch.setitem(config.TASK_MODELS, "outline", "qwen3:8b")  # Ollama 風格的冒號不是服務商前綴
    assert llm.route("translate")[::2] == ("openai", "qwen3.5-9b")
    assert llm.route("outline")[::2] == ("anthropic", "qwen3:8b")
    assert llm.route("chat")[::2] == ("anthropic", OPUS)  # 沒設就用 LLM_MODEL


def test_per_task_model_and_effort(claude, papers, client, monkeypatch):
    monkeypatch.setitem(config.TASK_MODELS, "translate", "claude-haiku-5-5")
    pid = _pid(papers)
    sse(client, "POST", f"/api/papers/{pid}/translate", {"text": "We propose a method.", "page": 0})
    t = claude[-1]["body"]
    assert t["model"] == "claude-haiku-5-5" and t["output_config"] == {"effort": "low"}  # 翻譯預設 low
    sse(client, "POST", f"/api/papers/{pid}/explain", {"text": "lantern encoder", "page": 0})
    e = claude[-1]["body"]
    assert e["model"] == OPUS and e["output_config"] == {"effort": config.LLM_EFFORT}


def test_mixed_providers(claude, papers, client, monkeypatch):
    """主服務商是 Claude，翻譯改走 OpenAI 相容的服務（例如本機 vLLM）。"""
    monkeypatch.setitem(config.TASK_MODELS, "translate", "openai:strict-model")
    fake_api.calls.clear()
    text, _, err = sse(client, "POST", f"/api/papers/{_pid(papers)}/translate", {"text": "We propose a method.", "page": 0})
    assert err is None and text
    assert [c["model"] for c in fake_api.calls][-1] == "strict-model" and not claude


def test_health_lists_task_models(claude, client, monkeypatch):
    monkeypatch.setitem(config.TASK_MODELS, "translate", "claude-haiku-5-5")
    h = client.get("/api/health").json()
    assert h["tasks"]["translate"] == "anthropic:claude-haiku-5-5"
    assert h["tasks"]["chat"] == f"anthropic:{OPUS}"
    assert h["translate"]["ok"] and h["translate"]["model"] == "claude-haiku-5-5"  # 另外指定的模型也測了一次


# ---------------- 用量記錄（docs/usage.md）----------------
def test_usage_is_recorded_and_admin_only(claude, papers, client, monkeypatch):
    from backend import db
    pid = _pid(papers)
    sse(client, "POST", f"/api/papers/{pid}/explain", {"text": "lantern encoder", "page": 0})
    with db.conn() as c:
        row = dict(c.execute("SELECT * FROM llm_usage ORDER BY rowid DESC LIMIT 1").fetchone())
    assert (row["user_id"], row["paper_id"], row["task"], row["model"]) == ("alice", pid, "explain", OPUS)
    assert (row["input"], row["output"]) == (10, 5) and row["cost"] == pytest.approx((10 * 4 + 5 * 20) / 1e6)
    assert llm.cost_usd(OPUS, 0, 0, 1_000_000, 1_000_000) == pytest.approx(5 + 0.2)  # 快取寫 1.25×、讀 0.2

    monkeypatch.setattr(config, "ADMIN_USERS", set())
    assert client.get("/api/me").json()["admin"] is False
    assert client.get("/api/admin/usage").status_code == 403
    monkeypatch.setattr(config, "ADMIN_USERS", {"alice"})
    assert client.get("/api/me").json()["admin"] is True
    rep = client.get("/api/admin/usage?days=7").json()
    assert any(t["task"] == "explain" and t["calls"] >= 1 for t in rep["by_task"]) and rep["total"]["cost"] > 0
