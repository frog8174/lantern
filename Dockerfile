# Lantern 論文閱讀器（部署說明：docs/deploy.md）
# 兩段式：先用 uv 依 uv.lock 裝好套件，執行映像只帶 .venv 與程式碼。

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS build
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-install-project

FROM python:3.12-slim-bookworm
WORKDIR /app
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin lantern \
 && mkdir /data && chown 10001:10001 /data   # 沒掛 volume 也能啟動（k8s 會掛 PVC 蓋過去）
COPY --from=build /app/.venv /app/.venv
COPY backend ./backend
COPY frontend ./frontend
# 資料（SQLite、PDF、縮圖）全部寫在 DATA_DIR，k8s 掛 PVC；映像本身可唯讀
# FORWARDED_ALLOW_IPS：uvicorn 只信任這些來源的 X-Forwarded-*（Ingress 終結 TLS 時，redirect URI 才會是 https）
ENV PATH=/app/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    DATA_DIR=/data FORWARDED_ALLOW_IPS="*"
USER 10001
EXPOSE 7800
# 單一 worker：SQLite 單寫者，背景工作（Wiki 更新、整篇翻譯）在程序記憶體裡
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7800", "--proxy-headers", "--timeout-graceful-shutdown", "20"]
