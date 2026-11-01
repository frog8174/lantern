"""設定集中在這裡。全部從環境變數（或專案根目錄的 .env）讀取。

LLM 走「OpenAI 相容 API」：vLLM、Ollama、LM Studio、OpenAI、DeepSeek、
OpenRouter … 都提供同一套 /v1/chat/completions 介面，所以只要換
LLM_BASE_URL / LLM_API_KEY / LLM_MODEL 就能切換，程式碼不用動。
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    """極簡 .env 讀取器（KEY=VALUE，一行一個）。
    同一個名稱出現多次時以「最後一次」為準（下方的方案可以直接蓋過上方的預設）；
    已存在的環境變數仍然優先。設 LANTERN_NO_DOTENV=1 可完全不讀（測試用，避免吃到個人設定）。"""
    if not path.exists() or os.environ.get("LANTERN_NO_DOTENV") == "1":
        return
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    for key, value in values.items():
        os.environ.setdefault(key, value)


_load_dotenv(ROOT / ".env")


def _bool(name: str, default: bool) -> bool:
    return os.environ.get(name, str(default)).lower() in {"1", "true", "yes", "on"}


# ---- 模型服務商 ----
# openai    ：任何 OpenAI 相容 API（vLLM、OpenAI、DeepSeek…），用下面的 LLM_* / VLM_* / OCR_* 設定
# anthropic ：Claude 官方 SDK。金鑰放 ANTHROPIC_API_KEY；文字、看圖、OCR 都用 LLM_MODEL（可用 VLM_MODEL / OCR_MODEL 另指）
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai").lower()
# Claude 的思考深度：low / medium / high / xhigh / max。閱讀助手要快就用 low
LLM_EFFORT = os.environ.get("LLM_EFFORT", "medium")

# ---- 文字 LLM（解釋、翻譯、聊天、摘要、自動標註）----
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:8000/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "EMPTY")  # vLLM 預設不檢查 key
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen3.5-9b")
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "2048"))
# Qwen3 系列預設會先輸出 <think>…</think>。閱讀助手通常不需要，關掉比較快。
DISABLE_THINKING = _bool("DISABLE_THINKING", True)
# 模型的 context 長度（token）。論文全文小於這個比例時，直接整篇塞進 prompt。
LLM_CONTEXT_TOKENS = int(os.environ.get("LLM_CONTEXT_TOKENS", "65536"))
# 同時送給模型的請求上限（自動標註、對照翻譯會並行送）。外部 API 被限流（429）就調小
LLM_CONCURRENCY = max(1, int(os.environ.get("LLM_CONCURRENCY", "4")))

# ---- 各元件用哪個模型（留空 = 用 LLM_MODEL）----
# 環境變數 LLM_MODEL_<元件>，例：LLM_MODEL_TRANSLATE=claude-haiku-5-5。
# 名稱前加 "openai:" 或 "anthropic:" 可以讓這個元件換服務商，
# 例：LLM_PROVIDER=anthropic 但 LLM_MODEL_TRANSLATE=openai:qwen3.5-9b → 翻譯走本機 vLLM（LLM_BASE_URL）
TEXT_TASKS = ("explain", "chat", "summary", "translate", "highlight", "outline", "cite", "suggest", "wiki", "align", "note")
TASK_MODELS = {t: os.environ.get(f"LLM_MODEL_{t.upper()}", "") for t in TEXT_TASKS}
# 中英對齊（螢光筆同步到譯文）是又小又多的工作：沒另外設就跟翻譯用同一個便宜模型
TASK_MODELS["align"] = TASK_MODELS["align"] or TASK_MODELS["translate"]
# 各元件的思考深度（只用在 Claude；留空 = LLM_EFFORT）。量大又單純的工作預設 low
_EFFORT_DEFAULTS = {"translate": "low", "outline": "low", "suggest": "low", "align": "low"}
TASK_EFFORT = {t: os.environ.get(f"LLM_EFFORT_{t.upper()}", "") or _EFFORT_DEFAULTS.get(t, "") for t in TEXT_TASKS}

# ---- 視覺模型（圖表 / 公式截圖解釋）。留空就用文字模型（若它本身支援影像）----
VLM_BASE_URL = os.environ.get("VLM_BASE_URL", "") or LLM_BASE_URL
VLM_API_KEY = os.environ.get("VLM_API_KEY", "") or LLM_API_KEY
VLM_MODEL = os.environ.get("VLM_MODEL", "")

# ---- OCR（掃描版 PDF）。預設用上面的視覺模型；也可指到專門的 OCR 模型（如 PaddleOCR-VL）----
OCR_ENABLED = _bool("OCR_ENABLED", True)
OCR_BASE_URL = os.environ.get("OCR_BASE_URL", "") or VLM_BASE_URL
OCR_API_KEY = os.environ.get("OCR_API_KEY", "") or VLM_API_KEY
OCR_MODEL = os.environ.get("OCR_MODEL", "") or VLM_MODEL or LLM_MODEL
# PaddleOCR-VL 這類專門模型只認固定指令（"OCR:"）；通用視覺模型用預設的中文指令即可
OCR_PROMPT = os.environ.get("OCR_PROMPT", "") or (
    "把這張論文頁面的文字完整轉寫出來，依閱讀順序（雙欄先左後右）輸出 Markdown。"
    "數學式用 LaTeX，表格用 Markdown 表格，圖片只寫 [圖]。只輸出轉寫結果，不要加任何說明。"
)

# ---- Embedding 模型（向量檢索）。留空就改用 BM25 關鍵字檢索 ----
EMBED_BASE_URL = os.environ.get("EMBED_BASE_URL", "") or LLM_BASE_URL
EMBED_API_KEY = os.environ.get("EMBED_API_KEY", "") or LLM_API_KEY
EMBED_MODEL = os.environ.get("EMBED_MODEL", "")

# ---- 逐句對應用的 LaBSE 句向量（docs/labse.md）。URL 留空 = 不做，選字時改問 LLM ----
ALIGN_EMBED_URL = os.environ.get("ALIGN_EMBED_URL", "")
ALIGN_EMBED_MODEL = os.environ.get("ALIGN_EMBED_MODEL", "labse")
ALIGN_EMBED_API_KEY = os.environ.get("ALIGN_EMBED_API_KEY", "")

# ---- 其他 ----
TARGET_LANG = os.environ.get("TARGET_LANG", "繁體中文（台灣用語）")
DATA_DIR = Path(os.environ.get("DATA_DIR", ROOT / "data"))
SEMANTIC_SCHOLAR_LOOKUP = _bool("SEMANTIC_SCHOLAR_LOOKUP", True)
# 選填。沒 key 也能用，但共用額度常被限流（HTTP 429）。申請：https://www.semanticscholar.org/product/api
SEMANTIC_SCHOLAR_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
# 設為 true 時不呼叫任何模型，回傳假資料，方便開發前端。
LLM_MOCK = _bool("LLM_MOCK", False)

# ---- 登入 ----
# dev：測試登入（選使用者、免密碼，cookie 未簽章），只能自己開發用
VERSION = os.environ.get("APP_VERSION", "0.1.0")  # 登入頁右下角顯示；部署新版時跟著映像 tag 改
AUTH_MODE = os.environ.get("AUTH_MODE", "dev").lower()  # dev＝選測試使用者；oidc＝Keycloak（docs/auth.md）
TEST_USERS = [u.strip() for u in os.environ.get("TEST_USERS", "alice,bob").split(",") if u.strip()]
# OIDC（Keycloak）。OIDC_ISSUER 必須和 token 的 iss 完全一樣；PUBLIC_BASE_URL 用來組 redirect URI
OIDC_ISSUER = os.environ.get("OIDC_ISSUER", "").rstrip("/")
# 本機開發用另一個 client（OIDC_DEV_CLIENT_ID／OIDC_DEV_SECRET，只放本機 .env）；上線環境沒有這兩個變數
OIDC_CLIENT_ID = os.environ.get("OIDC_DEV_CLIENT_ID") or os.environ.get("OIDC_CLIENT_ID", "")
OIDC_CLIENT_SECRET = os.environ.get("OIDC_DEV_SECRET") or os.environ.get("OIDC_CLIENT_SECRET", "")
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "http://localhost:7800").rstrip("/")
SESSION_SECRET = os.environ.get("SESSION_SECRET", "")
SESSION_MAX_AGE = int(os.environ.get("SESSION_MAX_AGE", 8 * 3600))

DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "pdfs").mkdir(exist_ok=True)
