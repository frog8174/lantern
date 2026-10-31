"""測試共用設定。

1. 在背景執行緒啟動 tests/fake_api.py（挑剔的假 OpenAI 相容 API）
2. 把所有模型設定指到它、資料放暫存資料夾 —— 必須在 import backend 之前設好環境變數，
   因為 backend/config.py 在 import 時就讀設定（你自己的 .env、data/ 完全不會被動到）
3. 現場產生測試 PDF（tests/sample_pdfs.py），不需要網路
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import tempfile
import threading
import time
from pathlib import Path

import pytest
import uvicorn

from tests import fake_api
from tests.sample_pdfs import make_all


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


PORT = _free_port()
TMP = Path(tempfile.mkdtemp(prefix="lantern-test-"))
os.environ.update({
    "LANTERN_NO_DOTENV": "1",           # 不讀專案的 .env：個人的模型、金鑰設定不能影響測試
    "LLM_MOCK": "false",
    "LLM_BASE_URL": f"http://127.0.0.1:{PORT}/v1",
    "LLM_API_KEY": fake_api.API_KEY,
    "LLM_MODEL": "strict-model",        # 不收 chat_template_kwargs、max_tokens
    "VLM_BASE_URL": "", "VLM_API_KEY": "",
    "VLM_MODEL": "vision-model",
    "OCR_BASE_URL": "", "OCR_API_KEY": "", "OCR_PROMPT": "",
    "OCR_MODEL": "reasoning-model",     # 再加上不收 temperature
    "OCR_ENABLED": "true",
    "EMBED_BASE_URL": "", "EMBED_API_KEY": "",
    "EMBED_MODEL": "emb-a",
    "LLM_CONTEXT_TOKENS": "500",        # 故意很小：聊天一定走 RAG + embedding 檢索
    "LLM_CONCURRENCY": "2",
    "DISABLE_THINKING": "true",
    "SEMANTIC_SCHOLAR_LOOKUP": "false",  # 不連外網
    "DATA_DIR": str(TMP / "data"),
    # Claude 測試（tests/test_anthropic.py）也打同一個假伺服器
    "ANTHROPIC_BASE_URL": f"http://127.0.0.1:{PORT}",
    "ANTHROPIC_API_KEY": fake_api.API_KEY,
    "LLM_PROVIDER": "openai",
})


@pytest.fixture(scope="session", autouse=True)
def fake_server():
    server = uvicorn.Server(uvicorn.Config(fake_api.app, host="127.0.0.1", port=PORT, log_level="warning"))
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    yield server
    server.should_exit = True
    t.join(timeout=5)
    shutil.rmtree(TMP, ignore_errors=True)


@pytest.fixture(scope="session")
def pdfs() -> dict[str, Path]:
    return make_all(TMP / "samples")


@pytest.fixture(scope="session")
def client(fake_server):
    from fastapi.testclient import TestClient

    from backend.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def papers(client, pdfs) -> dict[str, dict]:
    """把三份測試 PDF 都匯入一次，整個測試共用。"""
    out = {}
    for name, path in pdfs.items():
        with open(path, "rb") as f:
            r = client.post("/api/papers", files={"file": (path.name, f, "application/pdf")})
        assert r.status_code == 200, r.text
        out[name] = r.json()
    return out


def sse(client, method: str, path: str, body: dict | None = None) -> tuple[str, list[str], str | None]:
    """讀 SSE 回應 → (完整文字, 每則訊息, 錯誤訊息)。"""
    text, events, err = "", [], None
    with client.stream(method, path, json=body) as r:
        assert r.status_code == 200, r.read()
        buf = ""
        for chunk in r.iter_text():
            buf += chunk
            while "\n\n" in buf:
                line, buf = buf.split("\n\n", 1)
                line = line.removeprefix("data: ")
                if line == "[DONE]":
                    return text, events, err
                msg = json.loads(line)
                if "error" in msg:
                    err = msg["error"]
                else:
                    text += msg["t"]
                    events.append(msg["t"])
    return text, events, err
