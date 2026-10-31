"""故意很「挑剔」的假 OpenAI 相容 API，用來測相容處理，不需要真的模型。

模型：
  strict-model     不收 chat_template_kwargs、不收 max_tokens（像 OpenAI 新模型）
  reasoning-model  再加上不收 temperature（像部分推理模型）
  text-only        不收圖片
  vision-model     收圖片
Embedding：emb-a → 8 維、emb-b → 16 維（測換模型）
每個請求都要帶 "Authorization: Bearer test-key"。
回答會夾雜空的 choices 和 <think>…</think>，測串流處理。

也能單獨跑起來手動玩：uv run python tests/fake_api.py 8011
"""
from __future__ import annotations

import hashlib
import json
import re
import sys

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

API_KEY = "test-key"
app = FastAPI()
calls: list[dict] = []  # 每個請求送了哪些參數，測試用來檢查


def _err(status: int, msg: str):
    return JSONResponse({"error": {"message": msg, "type": "invalid_request_error"}}, status_code=status)


def _answer(prompt: str) -> str:
    marks = re.findall(r"<<(\d+)>>", prompt)
    if marks:  # 對照翻譯：照標記逐段回
        return "\n\n".join(f"<<{m}>> 第{m}段譯文" for m in marks)
    if "novelty" in prompt and "JSON" in prompt:  # 自動標註：從原文挑一句「逐字照抄」
        sents = [s.strip() for s in re.split(r"(?<=\.)\s+", prompt)
                 if 60 < len(s.strip()) < 200 and "JSON" not in s and "：" not in s]
        return "```json\n" + json.dumps({"novelty": [{"page": 1, "text": sents[0] if sents else ""}],
                                         "method": [], "result": []}) + "\n```"
    if '"questions"' in prompt:  # 聊天的建議問題
        return json.dumps({"questions": ["主要貢獻是什麼？", "方法怎麼運作？", "結果代表什麼？"]}, ensure_ascii=False)
    if '"outline"' in prompt:
        return json.dumps({"outline": [{"level": 1, "title": "1 Introduction", "page": 1}]})
    return "<think>internal reasoning</think>\n\n這是假 API 的回答 [p.1]。"


@app.post("/v1/chat/completions")
async def chat(req: Request):
    if req.headers.get("authorization") != f"Bearer {API_KEY}":
        return _err(401, "invalid api key")
    body = await req.json()
    model = body.get("model")
    calls.append({"model": model, "params": sorted(k for k in body if k != "messages"),
                  "prompt": json.dumps(body["messages"], ensure_ascii=False)})
    if model not in ("strict-model", "reasoning-model", "text-only", "vision-model"):
        return _err(404, f"model {model} not found")
    if "chat_template_kwargs" in body:
        return _err(400, "Unrecognized request argument supplied: chat_template_kwargs")
    if model in ("strict-model", "reasoning-model") and "max_tokens" in body:
        return _err(400, "Unsupported parameter: 'max_tokens'. Use 'max_completion_tokens' instead.")
    if model == "reasoning-model" and "temperature" in body:
        return _err(400, "Unsupported parameter: 'temperature'")
    has_image = any(isinstance(m["content"], list) and any(p.get("type") == "image_url" for p in m["content"])
                    for m in body["messages"])
    if model == "text-only" and has_image:
        return _err(400, "This model does not support image input")
    prompt = "\n".join(m["content"] if isinstance(m["content"], str)
                       else " ".join(p.get("text", "") for p in m["content"]) for m in body["messages"])
    text = "（OCR）Sparse lantern networks explain scanned pages too." if has_image and "轉寫" in prompt \
        else "白色" if has_image else _answer(prompt)

    def gen():
        head = {"id": "x", "object": "chat.completion.chunk", "created": 0, "model": model}
        yield "data: " + json.dumps(head | {"choices": []}) + "\n\n"  # 有些服務會送空的 choices
        for i in range(0, len(text), 7):
            delta = {"index": 0, "delta": {"content": text[i:i + 7]}, "finish_reason": None}
            yield "data: " + json.dumps(head | {"choices": [delta]}, ensure_ascii=False) + "\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.post("/v1/embeddings")
async def embeddings(req: Request):
    if req.headers.get("authorization") != f"Bearer {API_KEY}":
        return _err(401, "invalid api key")
    body = await req.json()
    dim = {"emb-a": 8, "emb-b": 16}.get(body["model"])
    if not dim:
        return _err(404, "model not found")
    inputs = body["input"] if isinstance(body["input"], list) else [body["input"]]
    data = [{"object": "embedding", "index": i,
             "embedding": [b / 255 for b in hashlib.sha256(str(t).encode()).digest()[:dim]]}
            for i, t in enumerate(inputs)]
    return {"object": "list", "data": data, "model": body["model"],
            "usage": {"prompt_tokens": 1, "total_tokens": 1}}


# ---------------- 假 Claude Messages API（LLM_PROVIDER=anthropic 用）----------------
# 照真實 API 的規則擋：不收 temperature、messages 裡不能有 system、圖片要是 image 區塊。
claude_calls: list[dict] = []


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/v1/messages")
async def claude_messages(req: Request):
    # SDK 2.x 用 Authorization: Bearer 帶 API key；舊版和 curl 用 x-api-key，兩種都收
    if API_KEY not in (req.headers.get("x-api-key"), req.headers.get("authorization", "").removeprefix("Bearer ")):
        return JSONResponse({"type": "error", "error": {"type": "authentication_error", "message": "invalid x-api-key"}},
                            status_code=401)
    body = await req.json()
    claude_calls.append({"body": body, "beta": req.headers.get("anthropic-beta", "")})

    def bad(msg):
        return JSONResponse({"type": "error", "error": {"type": "invalid_request_error", "message": msg}}, status_code=400)

    if "temperature" in body:
        return bad("temperature is not supported for this model")
    if any(m["role"] == "system" for m in body["messages"]) or body["messages"][0]["role"] != "user":
        return bad("messages must start with user and contain no system role")
    blocks = [p for m in body["messages"] if isinstance(m["content"], list) for p in m["content"]]
    if any(p["type"] == "image_url" for p in blocks):
        return bad("image_url is not a valid content block type")
    has_image = any(p["type"] == "image" and p["source"]["type"] == "base64" for p in blocks)
    prompt = "\n".join(m["content"] if isinstance(m["content"], str)
                       else " ".join(p.get("text", "") for p in m["content"]) for m in body["messages"])
    model = body["model"]
    refuse = model == "claude-refusing"
    text = "" if refuse else ("（OCR）Sparse lantern networks explain scanned pages too." if has_image and "轉寫" in prompt
                              else "白色" if has_image else _answer(prompt).replace("<think>internal reasoning</think>\n\n", ""))

    def gen():
        yield _sse("message_start", {"type": "message_start", "message": {
            "id": "msg_fake", "type": "message", "role": "assistant", "model": model, "content": [],
            "stop_reason": None, "stop_sequence": None, "usage": {"input_tokens": 10, "output_tokens": 1}}})
        # 先來一個思考區塊（內容預設是空的），確認程式不會把它當成回答
        yield _sse("content_block_start", {"type": "content_block_start", "index": 0,
                                           "content_block": {"type": "thinking", "thinking": "", "signature": ""}})
        yield _sse("content_block_delta", {"type": "content_block_delta", "index": 0,
                                           "delta": {"type": "signature_delta", "signature": "sig"}})
        yield _sse("content_block_stop", {"type": "content_block_stop", "index": 0})
        yield _sse("content_block_start", {"type": "content_block_start", "index": 1,
                                           "content_block": {"type": "text", "text": ""}})
        for i in range(0, len(text), 7):
            yield _sse("content_block_delta", {"type": "content_block_delta", "index": 1,
                                               "delta": {"type": "text_delta", "text": text[i:i + 7]}})
        yield _sse("content_block_stop", {"type": "content_block_stop", "index": 1})
        stop = {"stop_reason": "refusal", "stop_sequence": None,
                "stop_details": {"type": "refusal", "category": "bio", "explanation": "x"}} if refuse \
            else {"stop_reason": "end_turn", "stop_sequence": None}
        yield _sse("message_delta", {"type": "message_delta", "delta": stop, "usage": {"output_tokens": 5}})
        yield _sse("message_stop", {"type": "message_stop"})

    return StreamingResponse(gen(), media_type="text/event-stream")


# ---------------- 假的期刊網站：測「用 PDF 網址匯入」 ----------------
pdf_bytes: bytes = b""  # 測試前塞進一份 PDF


@app.get("/files/{name}")
async def files(name: str):
    from fastapi.responses import Response
    if name.endswith(".pdf"):
        return Response(pdf_bytes, media_type="application/pdf")
    return Response("<html><body>文章頁</body></html>", media_type="text/html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(sys.argv[1]) if len(sys.argv) > 1 else 8011)
