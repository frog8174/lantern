"""LLM 抽象層：所有模型呼叫都經過這裡。

用官方 openai SDK，但把 base_url 指到你自己的 vLLM（或任何 OpenAI 相容服務）。
- stream_chat  ：串流回傳文字片段（給前端逐字顯示）
- complete     ：一次拿完整回覆
- complete_json：要求模型回 JSON 並解析
- embed        ：把文字轉成向量（給語意檢索用）
"""
from __future__ import annotations

import asyncio
import base64
import json
import re
from contextvars import ContextVar
from typing import AsyncIterator

import anthropic
import httpx
import openai
from openai import AsyncOpenAI

from . import config, db

_chat = AsyncOpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)
_vision = AsyncOpenAI(base_url=config.VLM_BASE_URL, api_key=config.VLM_API_KEY)
_embed = AsyncOpenAI(base_url=config.EMBED_BASE_URL, api_key=config.EMBED_API_KEY)
_ocr = AsyncOpenAI(base_url=config.OCR_BASE_URL, api_key=config.OCR_API_KEY)

# 同時送給模型的請求上限。自架 vLLM 可以開大；外部 API 有速率限制就調小
_slots = asyncio.Semaphore(config.LLM_CONCURRENCY)

# ---- 參數相容 ----
# 各家「OpenAI 相容」API 收的參數不完全一樣：
#   - chat_template_kwargs 是 vLLM 專用（關 Qwen 思考模式），其他服務會回 400
#   - OpenAI 新模型（o 系列、GPT-5…）不收 max_tokens，要改 max_completion_tokens
#   - 部分推理模型不收 temperature
# 被拒（HTTP 400）時依序退讓重試；成功的組合按「網址＋模型」記住，之後直接用。
_ADJUSTMENTS = ("no_template_kwargs", "max_completion_tokens", "no_temperature")
_learned: dict[tuple[str, str], tuple[str, ...]] = {}


def _build(model: str, messages: list, stream: bool, adj: tuple[str, ...], kw: dict) -> dict:
    p = dict(model=model, messages=messages, stream=stream, **kw)
    p["temperature"] = kw.get("temperature", config.LLM_TEMPERATURE)
    p["max_tokens"] = kw.get("max_tokens", config.LLM_MAX_TOKENS)
    if config.DISABLE_THINKING and "no_template_kwargs" not in adj:
        # vLLM 會把 chat_template_kwargs 傳給 Qwen 的 chat template，關掉思考模式
        p["extra_body"] = {"chat_template_kwargs": {"enable_thinking": False}}
    if "max_completion_tokens" in adj:
        p["max_completion_tokens"] = p.pop("max_tokens")
    if "no_temperature" in adj:
        p.pop("temperature")
    return p


class _ThinkStripper:
    """串流過濾器：把 <think>…</think> 區塊吃掉，只留正式回答。"""

    def __init__(self) -> None:
        self.buf = ""
        self.inside = False
        self.trim = False  # 剛結束 </think>，吃掉接下來的換行

    def feed(self, text: str) -> str:
        out = self._feed(text)
        if self.trim:
            out = out.lstrip("\n")
            if out:
                self.trim = False
        return out

    def _feed(self, text: str) -> str:
        self.buf += text
        out = []
        while self.buf:
            if self.inside:
                end = self.buf.find("</think>")
                if end == -1:
                    self.buf = self.buf[-8:]  # 保留尾巴，避免標籤被切半
                    return "".join(out)
                self.buf = self.buf[end + len("</think>"):]
                self.inside = False
                self.trim = True
            else:
                start = self.buf.find("<think>")
                if start == -1:
                    # 尾巴可能是半個 "<think>"，先留著
                    keep = 0
                    for k in range(1, min(7, len(self.buf) + 1)):
                        if "<think>".startswith(self.buf[-k:]):
                            keep = k
                    out.append(self.buf[: len(self.buf) - keep])
                    self.buf = self.buf[len(self.buf) - keep:]
                    return "".join(out)
                out.append(self.buf[:start])
                self.buf = self.buf[start + len("<think>"):]
                self.inside = True
        return "".join(out)

    def flush(self) -> str:
        rest = "" if self.inside else self.buf
        self.buf = ""
        return rest.lstrip("\n") if self.trim else rest


async def _create(client: AsyncOpenAI, model: str, messages: list, stream: bool, **kw):
    key = (str(client.base_url), model)
    adj = _learned.get(key, ())
    try:
        return await client.chat.completions.create(**_build(model, messages, stream, adj, kw))
    except openai.BadRequestError as e:
        # 一次多讓一步；全部讓完還是 400，就是真的錯（例如 context 太長、模型不收圖片）。
        # 回報最後一個錯誤：參數都讓掉之後剩下的，才是真正的原因
        last = e
        for step in _ADJUSTMENTS:
            if step in adj:
                continue
            adj = adj + (step,)
            try:
                resp = await client.chat.completions.create(**_build(model, messages, stream, adj, kw))
            except openai.BadRequestError as e2:
                last = e2
                continue
            _learned[key] = adj
            return resp
        raise last


def route(task: str) -> tuple[str, AsyncOpenAI, str]:
    """元件 → (服務商, OpenAI 相容 client, 模型)。
    task：config.TEXT_TASKS 之一、"vision"、"ocr"，或 "llm"（預設的 LLM_MODEL）。"""
    if task == "vision":
        client, spec = _vision, config.VLM_MODEL or config.LLM_MODEL
    elif task == "ocr":
        client, spec = _ocr, config.OCR_MODEL
    else:
        client, spec = _chat, config.TASK_MODELS.get(task) or config.LLM_MODEL
    # 只認這兩個前綴：Ollama 之類的模型名稱本身就有冒號（qwen3:8b）
    provider, _, name = spec.partition(":")
    if provider in ("openai", "anthropic") and name:
        return provider, client, name
    return config.LLM_PROVIDER, client, spec


async def stream_chat(messages: list, *, task: str, **kw) -> AsyncIterator[str]:
    if config.LLM_MOCK:
        for word in _mock_answer(messages).split(" "):
            yield word + " "
        return
    provider, client, model = route(task)
    effort = config.TASK_EFFORT.get(task) or config.LLM_EFFORT
    async for text in _stream(client, model, messages, provider=provider, effort=effort, task=task, **kw):
        yield text


async def _stream(client: AsyncOpenAI, model: str, messages: list, *,
                  provider: str | None = None, effort: str | None = None, task: str = "health",
                  **kw) -> AsyncIterator[str]:
    if (provider or config.LLM_PROVIDER) == "anthropic":
        async with _slots:
            async for text in _claude_stream(model, messages, effort or config.LLM_EFFORT, task):
                yield text
        return
    stripper = _ThinkStripper()
    async with _slots:
        resp = await _create(client, model, messages, stream=True, **kw)
        async for chunk in resp:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content or ""  # reasoning_content 直接忽略
            text = stripper.feed(delta)
            if text:
                yield text
    tail = stripper.flush()
    if tail:
        yield tail


# ---------- Claude（LLM_PROVIDER=anthropic）----------
# features.py 一律寫 OpenAI 格式的訊息，這裡轉成 Claude Messages API 的格式。
_claude_client: anthropic.AsyncAnthropic | None = None
# 這幾個模型被安全分類器拒答時，伺服器會自動換模型重跑（server-side fallback）
_FALLBACK_MODELS = {"claude-fable-5-1", "claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5"}


def _claude() -> anthropic.AsyncAnthropic:
    """第一次用到才建立：金鑰從 ANTHROPIC_API_KEY（或 `ant auth login`）讀，沒設時不影響 openai 模式啟動。"""
    global _claude_client
    if _claude_client is None:
        _claude_client = anthropic.AsyncAnthropic()
    return _claude_client


def _claude_block(part: dict) -> dict:
    if part.get("type") != "image_url":
        return part  # {"type": "text", ...} 兩邊格式相同
    url = part["image_url"]["url"]
    m = re.match(r"data:(image/[\w.+-]+);base64,(.*)", url, re.S)
    src = {"type": "base64", "media_type": m.group(1), "data": m.group(2)} if m else {"type": "url", "url": url}
    return {"type": "image", "source": src}


def _to_claude(messages: list) -> tuple[str, list]:
    """system 訊息集中到頂層 system；圖片轉成 Claude 的 image 區塊；空白訊息丟掉（Claude 會回 400）。"""
    system, out = [], []
    for m in messages:
        c = m["content"]
        if m["role"] == "system":
            system.append(c)
            continue
        if isinstance(c, list):
            c = [_claude_block(p) for p in c]
        elif not c.strip():
            continue
        out.append({"role": m["role"], "content": c})
    # 聊天時（有多個 user 訊息）第一則 user 是整篇論文：在它後面放快取斷點，
    # 同一篇論文接下來的提問只付快取讀取價（Opus 5.5：$0.20 vs $4 / 百萬 token）
    users = [m for m in out if m["role"] == "user"]
    if len(users) > 1 and isinstance(users[0]["content"], str):
        users[0]["content"] = [{"type": "text", "text": users[0]["content"], "cache_control": {"type": "ephemeral"}}]
    return "\n\n".join(system), out


# ---------- 用量記錄（docs/usage.md）----------
# 誰、哪篇論文在用：current_user / _paper_or_404 設定；背景 task 建立時會複製一份，所以預翻譯也算得到
usage_ctx: ContextVar[tuple[str | None, str | None]] = ContextVar("usage_ctx", default=(None, None))
# 美元／百萬 token：(輸入, 輸出, 快取讀取)；快取寫入（5 分鐘）＝輸入 ×1.25。價目變了改這裡
PRICES = {"claude-opus-5-5": (4.0, 20.0, 0.20), "claude-sonnet-5-5": (2.0, 10.0, 0.20),
          "claude-haiku-5-5": (0.10, 0.50, 0.01)}


def cost_usd(model: str, inp: int, out: int, cache_write: int, cache_read: int) -> float:
    pin, pout, pread = PRICES.get(model, (0.0, 0.0, 0.0))  # 不在表上（自架 vLLM）算 0
    if model == "claude-haiku-5-5" and inp + cache_write + cache_read > 100_000:
        pin, pout, pread = pin * 5, pout * 5, pread * 5  # Haiku 5.5 超過 100K 輸入走長文價
    return (inp * pin + cache_write * pin * 1.25 + cache_read * pread + out * pout) / 1e6


def _record(task: str, model: str, u) -> None:
    uid, pid = usage_ctx.get()
    w, r = u.cache_creation_input_tokens or 0, u.cache_read_input_tokens or 0
    try:
        db.add_usage(uid, pid, task, model, u.input_tokens, u.output_tokens, w, r,
                     cost_usd(model, u.input_tokens, u.output_tokens, w, r))
    except Exception as e:  # 記錄失敗不能讓回答失敗
        print(f"[usage] {type(e).__name__}: {e}")


async def _claude_stream(model: str, messages: list, effort: str, task: str = "health") -> AsyncIterator[str]:
    system, msgs = _to_claude(messages)
    # 不送 temperature：Claude 4.7 之後的模型會回 400。
    # max_tokens 給大：思考也算在裡面，太小會把答案截斷；串流不怕逾時，只按實際用量計費
    params: dict = dict(model=model, max_tokens=64000, messages=msgs, output_config={"effort": effort})
    if system:
        params["system"] = system
    if model in _FALLBACK_MODELS:
        params |= {"betas": ["server-side-fallback-2026-07-01"], "fallbacks": "default"}
    async with _claude().beta.messages.stream(**params) as stream:
        async for text in stream.text_stream:  # 思考區塊不會出現在 text_stream
            yield text
        final = await stream.get_final_message()
    _record(task, getattr(final, "model", None) or model, final.usage)  # 伺服器端換模型時記實際用的
    if final.stop_reason == "refusal":
        cat = final.stop_details.category if final.stop_details else None
        raise RuntimeError(f"Claude 拒絕回答這個請求（類別：{cat or '未提供'}）")


async def complete(messages: list, **kw) -> str:
    parts = [t async for t in stream_chat(messages, **kw)]
    return "".join(parts).strip()


async def complete_json(messages: list, **kw):
    """要求模型輸出 JSON。小模型常會多包一層 ```json，這裡容錯處理。"""
    if config.LLM_MOCK:
        return _mock_json(messages)
    text = await complete(messages, temperature=0.1, **kw)
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1)
    start = min([i for i in (text.find("{"), text.find("[")) if i != -1], default=0)
    try:
        return json.loads(text[start:])
    except json.JSONDecodeError:
        # 截斷到最後一個完整的括號再試一次
        end = max(text.rfind("}"), text.rfind("]"))
        return json.loads(text[start: end + 1])


async def ocr_image(image_data_url: str) -> str:
    """掃描頁 → 文字。走 OCR_* 設定（預設就是視覺模型）。"""
    if config.LLM_MOCK:
        return "（MOCK OCR）這是掃描頁面轉寫出來的假文字。Attention is all you need."
    messages = [{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": image_data_url}},
        {"type": "text", "text": config.OCR_PROMPT},
    ]}]
    parts = [t async for t in stream_chat(messages, task="ocr", temperature=0.0, max_tokens=4096)]
    return "".join(parts).strip()


async def embed(texts: list[str]) -> list[list[float]] | None:
    """回傳向量；沒設定 EMBED_MODEL 時回 None，呼叫端會改用 BM25。"""
    if not config.EMBED_MODEL or config.LLM_MOCK:
        return None
    out: list[list[float]] = []
    for i in range(0, len(texts), 64):  # 分批，避免一次送太大
        resp = await _embed.embeddings.create(model=config.EMBED_MODEL, input=texts[i: i + 64])
        out.extend(d.embedding for d in resp.data)
    return out


async def rerank(query: str, docs: list[str]) -> list[float] | None:
    """每段和問題的相關分數（跟 docs 同順序）；沒設定 RERANK_MODEL 時回 None。"""
    if not config.RERANK_MODEL or config.LLM_MOCK or not docs:
        return None
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{config.RERANK_BASE_URL.rstrip('/')}/rerank",
                         headers={"Authorization": f"Bearer {config.RERANK_API_KEY}"},
                         json={"model": config.RERANK_MODEL, "query": query, "documents": docs})
    r.raise_for_status()
    scores = [0.0] * len(docs)
    for x in r.json()["results"]:
        scores[x["index"]] = x["relevance_score"]
    return scores


# ---------- 連線檢查（/api/health）----------
def _test_image() -> str:
    """32×32 白圖。太小（例如 1×1）的圖有些視覺模型會直接拒收。"""
    import pymupdf
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 32, 32), False)
    pix.clear_with(255)
    return "data:image/png;base64," + base64.b64encode(pix.tobytes("png")).decode()


async def check(role: str) -> dict:
    """實際打一次 API，確認網址、key、模型名稱都對；視覺 / OCR 會附一張圖，確認模型收得下影像。
    role："llm"、"vlm"、"ocr"、"embed"，或 config.TEXT_TASKS 裡的元件名稱。"""
    if role == "embed":
        provider, client, model = "openai", _embed, config.EMBED_MODEL
    else:
        provider, client, model = route("vision" if role == "vlm" else role)
    claude = provider == "anthropic"
    info = {"base_url": str(_claude().base_url if claude else client.base_url),
            "model": f"{provider}:{model}" if provider != config.LLM_PROVIDER else model}
    try:
        if role == "embed":
            resp = await _embed.embeddings.create(model=model, input=["ping"])
            return info | {"ok": True, "dim": len(resp.data[0].embedding)}
        content: list | str = "只回覆 OK 兩個字"
        if role in ("vlm", "ocr"):
            content = [{"type": "image_url", "image_url": {"url": _test_image()}},
                       {"type": "text", "text": "這張圖是什麼顏色？只回答顏色。"}]
        parts = [t async for t in _stream(client, model, [{"role": "user", "content": content}],
                                          provider=provider, max_tokens=16)]
        info = info | {"ok": True, "reply": "".join(parts).strip()[:40]}
        adj = _learned.get((str(client.base_url), model))
        return info | ({"adjusted": list(adj)} if adj else {})
    except Exception as e:
        return info | {"ok": False, "error": f"{type(e).__name__}: {e}"[:300]}


# ---------- 假資料（LLM_MOCK=true 時使用）----------
def _mock_answer(messages: list) -> str:
    return "（MOCK 模式）這是一段假的回答，用來測試前端串流顯示。引用範例 [p.1]。"


def _mock_json(messages: list):
    prompt = json.dumps(messages, ensure_ascii=False)
    if "paper_page" in prompt:  # workspace wiki 規劃
        return {"paper_page": {"title": "MOCK 論文頁", "markdown": "（MOCK）論文頁 [[mock-concept]]"},
                "concepts": [{"slug": "mock-concept", "title": "Mock Concept", "note": "MOCK 重點"}]}
    if "qa_page" in prompt:  # wiki 問答存成頁面
        return {"title": "MOCK 問答", "markdown": "# MOCK 問答\n（MOCK）整理後的問答"}
    if "highlight" in prompt.lower():
        return {"novelty": [], "method": [], "result": []}
    return {"outline": []}
