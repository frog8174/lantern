# Lantern — 個人用 AI 論文閱讀器

仿 Moonlight 的功能組合，全部跑在自己的電腦上：PDF 放本地、模型用你自己的 vLLM（或任何 OpenAI 相容 API）。

## 功能對照

| Moonlight 功能 | 這裡的做法 | 程式位置 |
|---|---|---|
| 選字解釋（Explanation） | 選取文字 → 帶「標題＋摘要＋前後頁」給 LLM | `features.explain_messages` |
| 對照翻譯（保留版面） | 按「雙 對照翻譯」：逐段翻譯並疊在原文位置，滑過譯文看原文；只翻畫面上的頁，有快取 | `features.stream_block_translation`、`app.js` 對照翻譯段 |
| 翻譯（選字 / 整頁到面板） | 同選字解釋的上下文，整頁結果存快取 | `features.translate_messages` |
| 圖表、公式解釋 | 框選區域 → 從 canvas 裁圖 → 丟視覺模型 | `app.js` 框選段、`features.image_messages` |
| 圖表預覽（Preview） | 滑過正文的 "Figure 3" / "Table 2" → 浮出那張圖，可一鍵請 AI 解釋 | `pdf_parse.find_figures` |
| 聊天（Chat） | 短論文整篇塞進 context；長論文走 RAG，回答附 `[p.X]` 可點擊跳頁 | `features.chat_messages`、`retrieval.py` |
| 自動標註（Auto Highlight） | LLM 逐字挑出新穎性 / 方法 / 結果句 → PyMuPDF 在原頁找座標 → 畫螢光筆 | `features.auto_highlight` |
| 智慧引用（Smart Citation） | 點 `[12]` 或 `(Peters et al., 2018a)` → 參考文獻原文 ＋ Semantic Scholar 摘要、引用數 | `pdf_parse._references`、`match_author_year` |
| 相關論文（Scholar Deep Search） | 「相關」分頁：依本篇或整個論文庫推薦，arXiv 論文一鍵匯入 | `features.recommend` |
| AI 大綱（Document Outlining） | 先讀 PDF 內建書籤，沒有就用字級猜，還不行按「AI 生成」 | `pdf_parse._outline`、`features.ai_outline` |
| 論文庫 | 標籤、篩選、全文搜尋（Enter，跨所有論文、點結果跳頁） | `db.search_chunks` |
| 螢光筆、註解 | SQLite 存；閱讀頁「標註」分頁列出全部 | `db.py` |
| 論文筆記 | 閱讀頁「筆記」分頁：每篇一份 Markdown 筆記，編輯／預覽、自動儲存、標註一鍵引用（可點回原處）、AI 從標註擬初稿、匯出 .md、列印 | `db.save_note`、`features.note_draft_messages`、`app.js` 筆記段 |
| 摘要 | 結構化 Markdown，存快取 | `features.summary_messages` |
| 掃描版 PDF | 自動偵測沒文字層的頁 → 畫成圖丟 OCR 模型 → 文字給聊天 / 摘要 / 檢索用 | `pdf_parse._is_scanned`、`llm.ocr_image` |

## 操作方式（仿 Moonlight）

| 想做的事 | 怎麼操作 |
|---|---|
| 解釋一段文字 | 選字 → 浮動工具列的放大鏡（或按 **E**）→ 結果出現在選取處旁的浮動卡片，卡片底部可以繼續追問 |
| 針對一段文字提問 | 選字 → 工具列的「Ask AI …」輸入問題按 Enter |
| 螢光筆 | 選字 → 筆的圖示（或按 **H**）；滑過筆的圖示可選 5 種顏色 |
| 翻譯一段 | 選字 → 地球圖示（或按 **T**） |
| 加註解 | 選字 → 按右鍵 →「加註解」（或按 **C**）；頁邊會出現註解圖示 |
| 寫筆記、引用原文 | 右側「筆記」分頁直接寫（Markdown，自動儲存）；選字按「引用」（或按 **Q**），或在「標註」分頁某則按「引用」，原文和可點回原處的連結會插進筆記 |
| 解釋圖表 / 公式 | 按住 **Ctrl / ⌘** 拖曳框選（或先按頂部「框選」），框旁的工具列按解釋或直接輸入問題 |
| 整頁翻譯 | 頂部「原文 / 疊加 / 並排」：疊加 = 譯文蓋在原文位置；並排 = 原文頁和譯文頁左右對照，圖表原樣保留 |
| 看圖表 | 滑鼠移到正文的「Figure 3」「Table 2」上 |
| 看引用 | 點 `[12]` 或 `(Peters et al., 2018a)` → 引用卡片：摘要、為何引用（AI）、BibTeX、存到論文庫 |
| 和論文聊天 | 右下角的對話按鈕，可拖曳、可調整大小，一開始有建議問題 |
| 回顧 | 右側活動面板：摘要、標註（可依顏色 / 類別篩選、搜尋）、解釋紀錄、註解、參考文獻、相關論文 |

Esc 關閉所有浮動元件。

## 架構

```
瀏覽器（frontend/，純 JS，免打包）
 ├─ PDF.js：每頁 = canvas（看得到的圖）＋ textLayer（透明、可選取的字）＋ hlLayer（螢光筆）
 ├─ 選字工具列 / 框選 / 引用卡片 / 右側面板
 └─ fetch + SSE 串流 ──────────────┐
                                    ▼
FastAPI（backend/）
 ├─ pdf_parse.py  PyMuPDF：文字 + 座標（正規化 0~1）、大綱、摘要、參考文獻
 ├─ retrieval.py  切塊 → embedding 或 BM25 → 混合檢索
 ├─ features.py   每個功能的 prompt 與上下文組裝（要調 prompt 改這裡）
 ├─ llm.py        OpenAI SDK，base_url 指到 vLLM；過濾 Qwen 的 <think>；OCR 呼叫
 └─ db.py         SQLite：papers / chunks / cache / annotations / messages
                                    │ OpenAI 相容 API（/v1/chat/completions、/v1/embeddings）
                                    ▼
          vLLM（Qwen3.5-9B：文字＋看圖＋OCR）·（可選）OCR 專用模型 ·（可選）embedding 模型
          或 OpenAI / DeepSeek / OpenRouter …
```

## 快速開始

套件用 [uv](https://docs.astral.sh/uv/) 管理（`pyproject.toml` + `uv.lock`），虛擬環境會自動建在 `.venv/`。

```bash
cd paper-reader
uv sync                       # 依 uv.lock 安裝套件（第一次或換電腦時）
cp .env.example .env          # 改成你的模型位址（已附一份預設 .env）
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 7800
```

打開 http://localhost:7800 。先開 http://localhost:7800/api/health 確認 `"ok": true`，代表模型接上了。

`--host 0.0.0.0` 讓同網路的其他裝置（手機、平板、另一台電腦）用 `http://<這台電腦的 IP>:7800` 連進來；只想自己用就拿掉這個參數（預設只聽 127.0.0.1）。

> **注意**：這個服務沒有登入機制。開 0.0.0.0 時，同一個網路上的任何人都能讀你的論文、刪除論文，並用你的 Claude API 額度。
> 只在家裡或信任的網路開；在公共 Wi-Fi、辦公室網路請改回只聽本機，或用 Tailscale 這類私人網路連回來。

沒有模型也能先看介面：`.env` 設 `LLM_MOCK=true`。

加套件用 `uv add <套件>`（會同時更新 `pyproject.toml` 和 `uv.lock`），不要用 pip。

> **Windows 注意**：Hyper-V / WSL 會保留一段連接埠（查詢：`netsh int ipv4 show excludedportrange protocol=tcp`），
> 這台電腦的 8793–8892 就被保留，所以預設用 7800。出現 `[WinError 10013]` 就換一個不在範圍內的 port。

### 啟動 vLLM（範例）

vLLM 只支援 Linux：在 Windows 上請跑在 WSL2 或另一台 GPU 主機，`.env` 的 `LLM_BASE_URL` 指過去即可
（例如 `http://192.168.1.20:8000/v1`；WSL2 預設可用 `http://localhost:8000/v1`）。

```bash
# 12GB 顯卡（RTX 3080 Ti）推薦：一顆 Qwen3.5-9B 4-bit 同時當文字、視覺、OCR 模型
# --max-model-len 要跟 .env 的 LLM_CONTEXT_TOKENS 一致
vllm serve QuantTrio/Qwen3.5-9B-AWQ --served-model-name qwen3.5-9b --port 8000 \
  --max-model-len 65536 --gpu-memory-utilization 0.85 --reasoning-parser qwen3

# 不確定模型名稱要填什麼？問 vLLM：
curl http://localhost:8000/v1/models     # 回傳的 "id" 就是 LLM_MODEL
```

`LLM_MODEL` 填的是 vLLM 對外公布的模型名稱（`/v1/models` 回傳的 id），不是檔案路徑。若啟動時用了 `--served-model-name`，就填那個名字。

- 啟動時 OOM（顯存不足）：先把 `--max-model-len` 降到 32768（`.env` 同步改），再不行降 `--gpu-memory-utilization`。WSL2 跟 Windows 桌面共用顯卡，桌面本身會吃掉約 0.5–1 GB。
- `QuantTrio/Qwen3.5-9B-AWQ` 是社群量化版（官方只出 BF16，9B 的 BF16 要 ~19GB 放不進 12GB）。也可以換 `cyankiwi/Qwen3.5-9B-AWQ-4bit`。
- 沒設 `EMBED_MODEL` → 檢索改用 BM25 關鍵字比對。64K context 下大部分論文會整篇送進 prompt，根本用不到檢索。

## 用 Claude（Anthropic 官方 SDK）

`.env` 設 `LLM_PROVIDER=anthropic`（範例見 `.env.example` 的方案 D），金鑰放 `ANTHROPIC_API_KEY`，`LLM_MODEL` 填 Claude 模型名稱（例：`claude-opus-5-5`）。

- **不需要另外的視覺 / OCR 服務**：Claude 能直接看圖，框選圖表、掃描頁 OCR 都用同一個模型（`VLM_MODEL` 留空）。
- **不用 RAG**：`LLM_CONTEXT_TOKENS=1000000`，論文一律整篇送進去。Claude 沒有 embedding API，`EMBED_MODEL` 留空。
- **Prompt caching**：聊天時整篇論文放在快取斷點前面，同一篇論文接下來的提問，論文部分只付快取讀取價（Opus 5.5：$0.20 vs $4 / 百萬 token；快取 5 分鐘內有效）。
- **思考深度**：`LLM_EFFORT`（low / medium / high / xhigh / max）。翻譯、解釋要快就用 `low`。
- **拒答**：Opus 5.5 / Sonnet 5.5 等模型被安全分類器拒答時，伺服器會自動換模型重跑（server-side fallback）；整條鏈都拒答時，畫面上會顯示「Claude 拒絕回答」與類別。
- 程式架構不變：`features.py` 照舊寫 OpenAI 格式的訊息，`llm.py` 在送出前轉成 Claude 的格式；切回 `LLM_PROVIDER=openai` 就回到 vLLM / 其他 API。

## 各元件的模型

每個 AI 元件可以用不同的模型：`.env` 設 `LLM_MODEL_<元件>`（沒設就用 `LLM_MODEL`），思考深度設 `LLM_EFFORT_<元件>`（只對 Claude 有效）。
模型名稱前加 `anthropic:` 或 `openai:` 可以讓該元件換服務商，例如聊天用 Claude、翻譯用本機 vLLM（`LLM_MODEL_TRANSLATE=openai:qwen3.5-9b`，走 `LLM_BASE_URL`）。

| 元件 | 設定 | 推薦（Claude） | 思考深度 | 為什麼 |
|---|---|---|---|---|
| 聊天 | `LLM_MODEL_CHAT` | Opus 5.5 | medium | 要跨整篇推理；論文放在快取裡，追問很便宜 |
| 摘要 | `LLM_MODEL_SUMMARY` | Opus 5.5 | medium | 每篇只跑一次且會快取，品質優先 |
| 看圖（框選、圖表解釋） | `VLM_MODEL` | Opus 5.5 | medium | 讀圖表數字、公式最吃能力 |
| 選字解釋 / Ask AI | `LLM_MODEL_EXPLAIN` | Sonnet 5.5 | medium | 最常用、要秒回；速度與品質的平衡點 |
| 自動標註 | `LLM_MODEL_HIGHLIGHT` | Sonnet 5.5 | medium | 要判斷重點又要逐字照抄原句，小模型常改寫而標不上 |
| 為何引用 | `LLM_MODEL_CITE` | Sonnet 5.5 | medium | 短回答但要理解論證脈絡 |
| 掃描版 OCR | `OCR_MODEL` | Sonnet 5.5 | medium | 轉寫要準，量通常不大 |
| 翻譯（選字、整頁、對照） | `LLM_MODEL_TRANSLATE` | Haiku 5.5 | low（預設） | 量最大（整篇逐段），$0.10 / $0.50 每百萬 token |
| AI 大綱 | `LLM_MODEL_OUTLINE` | Haiku 5.5 | low（預設） | 簡單的 JSON 整理 |
| 聊天建議問題 | `LLM_MODEL_SUGGEST` | Haiku 5.5 | low（預設） | 三個短問題，每篇只跑一次 |
| 中英對齊（螢光筆同步到譯文） | `LLM_MODEL_ALIGN` | 沒設就同翻譯 | low（預設） | 只要從一段裡抄出對應的子字串（docs/reader.md） |
| 筆記 AI 擬初稿 | `LLM_MODEL_NOTE` | Sonnet 5.5 | medium | 依你的標註與備註組織成筆記，要照抄引用標記（docs/notes-design.md） |

- 翻譯品質不滿意就把 `LLM_MODEL_TRANSLATE` 換成 `anthropic:claude-sonnet-5-5`；要省錢就把聊天、摘要也降到 Sonnet 5.5。
- 改完打開 `/api/health`：`tasks` 列出每個元件實際用的模型，另外指定的模型也會各測一次連線。
- 快取以模型為單位：同一個元件固定用同一個模型，快取才命中。

## 接其他 OpenAI 相容 API

任何提供 `/v1/chat/completions`（和 `/v1/embeddings`）的服務都能接：vLLM、Ollama、LM Studio、OpenAI、DeepSeek、OpenRouter、各家雲端…
四個角色可以各接各的，改 `.env` 就好，不用改程式：

| 角色 | 設定 | 用在 | 沒設時 |
|---|---|---|---|
| 文字 | `LLM_BASE_URL` `LLM_API_KEY` `LLM_MODEL` | 解釋、翻譯、聊天、摘要、標註、大綱 | 必填 |
| 視覺 | `VLM_BASE_URL` `VLM_API_KEY` `VLM_MODEL` | 框選圖表、圖表預覽解釋 | 沿用文字 |
| OCR | `OCR_BASE_URL` `OCR_API_KEY` `OCR_MODEL` `OCR_PROMPT` | 掃描頁轉文字 | 沿用視覺 |
| 向量 | `EMBED_BASE_URL` `EMBED_API_KEY` `EMBED_MODEL` | 長論文的語意檢索 | 改用 BM25 |

換完先開 **http://localhost:7800/api/health**，它會對每個角色實際打一次 API（視覺 / OCR 會附一張測試圖），哪個網址、key、模型名稱錯了一眼就看得出來。

程式已經處理好的相容問題：
- **參數差異**：被服務拒絕（HTTP 400）時自動退讓重試——拿掉 vLLM 專用的 `chat_template_kwargs`、`max_tokens` 改成 `max_completion_tokens`（OpenAI 新模型）、拿掉 `temperature`（部分推理模型）。成功的組合會記住，`/api/health` 的 `adjusted` 欄位會列出這組 API 被調整了什麼。
- **思考模型**：回答裡的 `<think>…</think>` 會被濾掉；放在 `reasoning_content` 的推理內容直接忽略。
- **速率限制**：`LLM_CONCURRENCY` 控制同時送出的請求數（預設 4）；SDK 遇到 429 也會自動退避重試 2 次。
- **換 embedding 模型**：舊論文的向量是舊模型算的，檢索會自動退回 BM25，不會壞；想用新模型的語意檢索就重新匯入那篇。

換模型後要注意：摘要、對照翻譯、整頁翻譯、AI 大綱都有**快取**，還是舊模型的結果。摘要可按「重新產生」；其他的刪掉論文重新匯入即可。

## 模型推薦

依各功能「需要什麼能力」挑。結論：**12GB 顯卡就跑一顆 Qwen3.5-9B（4-bit）全包**，品質不夠的功能再接外部 API。

| 功能 | 用到 | 需要的能力 | 本機（12GB） | 品質升級 |
|---|---|---|---|---|
| 選字解釋、聊天、摘要 | LLM | 長 context、中文表達、推理 | Qwen3.5-9B | Qwen3.8-27B |
| 對照翻譯、整頁翻譯 | LLM | 速度、照格式輸出（`<<編號>>`）；關思考模式 | Qwen3.5-9B | 求快可降 Qwen3.5-4B |
| 自動標註 | LLM | 逐字照抄原句 + JSON；小模型會改寫句子而標不上 | Qwen3.5-9B（勉強） | Qwen3.8-27B 明顯較好 |
| AI 大綱 | LLM | JSON 輸出 | Qwen3.5-9B | — |
| 框選圖表 / 公式、圖表預覽解釋 | VLM | 讀圖、讀公式、讀表格數字 | Qwen3.5-9B（原生看圖） | Qwen3.8-27B（原生看圖） |
| 掃描版 OCR | OCR | 版面還原、公式轉 LaTeX | Qwen3.5-9B（沿用 VLM） | PaddleOCR-VL-1.6（0.9B） |
| 語意檢索 | Embedding | 中英跨語檢索 | 不用（BM25 就夠） | Qwen3-Embedding-0.6B |

挑選理由：
- **Qwen3.5-9B**：Apache-2.0；文字與影像同一顆模型，省下第二份顯存；32 層裡只有 8 層是完整注意力（其餘是線性注意力），KV cache 每 token 只要約 32 KB，所以 12GB 也開得到 64K context，大部分論文能整篇送進去。
- **Qwen3.8-27B**（2026/08）：同樣原生看圖，品質明顯好，但 4-bit 也要約 17 GB，12GB 放不下。要用就接外部 API（`.env` 方案 B），或用 24GB 以上的顯卡。旗艦 Qwen3.8-2.4T-A95B、Qwen3.8-Flash-Next（180B）是伺服器等級，個人用不到。
- **PaddleOCR-VL-1.6**：0.9B、Apache-2.0，在 OmniDocBench 文件解析排名第一，掃描論文多時值得另開一個服務（依其模型卡的 vLLM 啟動方式），`.env` 設 `OCR_BASE_URL`、`OCR_MODEL`、`OCR_PROMPT=OCR:`。偶爾才讀掃描檔就沿用 Qwen3.5-9B。
- **思考模式**：Qwen3.5 預設會先「想」再回答。閱讀助手要的是快，`DISABLE_THINKING=true` 會關掉；想要更深的推理（例如難懂的證明）可暫時改成 `false`。

> 以上依 2026/10 的公開模型與 Hugging Face 模型卡整理；本專案只用 mock 模式測過流程，各模型的實際品質請自己用幾篇論文試。

## 名詞解釋

- **OpenAI 相容 API**：OpenAI 定義的 HTTP 介面格式（`POST /v1/chat/completions`）。vLLM、Ollama、多數雲端服務都實作同一套，所以程式只要換 `base_url` 就能切換模型供應者。
- **SSE（Server-Sent Events）**：伺服器在同一條 HTTP 連線上持續推送 `data: …` 的機制。模型每產生幾個字就推一次，前端邊收邊畫，就是「打字機效果」。
- **RAG（檢索增強生成）**：先從論文找出跟問題相關的段落，再把段落塞進 prompt 讓模型回答。用在論文太長、塞不進模型 context 的時候。
- **Context（上下文長度）**：模型一次能看的 token 上限。程式粗估論文長度，小於 `LLM_CONTEXT_TOKENS` 的 60% 就整篇送，否則走 RAG。
- **Embedding**：把一段文字變成一串數字（向量），意思相近的文字向量也相近，可用來做語意搜尋。
- **BM25**：不需要模型的關鍵字排序法。詞在段落裡出現越多、在整篇裡越少見，分數越高。
- **bbox（bounding box）**：框住一段文字的矩形 `[x0, y0, x1, y1]`。這裡統一除以頁寬、頁高變成 0~1，前端縮放時直接乘回去。
- **textLayer**：PDF.js 疊在畫面上的一層透明文字，位置與 canvas 上的字重疊，讓「圖片」可以被選取。
- **Thinking 模式**：Qwen3 預設會先輸出 `<think>…</think>` 推理過程。`DISABLE_THINKING=true` 會透過 vLLM 的 `chat_template_kwargs` 關掉；就算模型還是輸出了，`llm._ThinkStripper` 也會把它濾掉。

## 測試

三種測試，各管不同的事：

**1. 自動測試（改完程式就跑）**——不用模型、不用網路，約 3 秒：

```bash
uv sync                # 第一次：連同 pytest 一起裝
uv run pytest          # 全部
uv run pytest -v       # 列出每一項
uv run pytest tests/test_units.py            # 只跑單元測試
uv run pytest -k translate                   # 只跑名稱含 translate 的
uv run pytest -x                             # 遇到第一個失敗就停
```

- `tests/fake_api.py`：故意很挑剔的假 OpenAI 相容 API（不收 vLLM 參數、不收 `max_tokens`、有模型不收圖片、回答夾 `<think>`），測相容處理
- `tests/sample_pdfs.py`：現場產生測試論文（編號引用＋圖表、作者-年份引用、掃描版）
- `tests/test_units.py`：純函式（`<think>` 過濾、參數退讓、PDF 解析、圖表定位、引用比對）
- `tests/test_api.py`：每個功能走一次 API（匯入、OCR、解釋、翻譯、對照翻譯、聊天 RAG、摘要、標註、大綱、圖表、引用、標籤、搜尋、註解）
- 測試資料放在系統暫存資料夾，跑完自動刪除；你的 `.env`、`data/` 不會被動到

**2. 真模型連線**——接上 vLLM 或外部 API 後：先啟動服務，打開 http://localhost:7800/api/health，每個角色都要 `"ok": true`。

**3. 介面手動測**——自動測試不涵蓋前端互動（選字、框選、滑過圖表、對照翻譯的版面）。不接模型也能測：

```bash
# .env 暫時加一行 LLM_MOCK=true，然後
uv run uvicorn backend.main:app --reload --port 7800
```

匯入一篇論文（例：arXiv `1706.03762`），逐項點：選字 → 解釋 / 翻譯 / 螢光筆、「雙 對照翻譯」、滑過正文的 "Figure 1"、點 `[12]` 引用、「相關」分頁、論文庫搜尋。

## 調整與擴充

- **換 prompt 或回答語言**：`backend/features.py`，`TARGET_LANG` 在 `.env`。
- **版面解析更準（雙欄、表格、公式轉 LaTeX）**：把 `pdf_parse.parse_pdf` 換成 MinerU / Marker / GROBID，只要輸出同樣的 `ParsedPaper` 結構，其他程式不用改。
- **部署到 K8s**：前後端是同一個 FastAPI 服務，包一個 Docker image，`DATA_DIR` 掛 PVC 即可；`LLM_BASE_URL` 指到叢集內 vLLM 的 Service。
- **測試**：見下方「測試」。

## 已知限制

- 掃描版 PDF 經 OCR 後，聊天、摘要、整頁翻譯可用，但那些頁**無法選字、自動標註、對照翻譯**（OCR 沒有逐字座標）；要問特定段落請用「✂ 框選」。
- 自動標註靠模型「逐字照抄」原句再搜尋座標；小模型偶爾改寫句子，那幾句就會標不上去。
- 圖表預覽靠圖說（"Figure 3:" 開頭）和旁邊的圖形線條定位，少數排版（圖說在側邊、圖跨兩頁）會框不準。
- 作者-年份引用靠「懸掛縮排」切參考文獻條目；沒有縮排的排版會退回一個區塊一筆，可能對不上。
- Semantic Scholar 沒 API key 時常被限流（HTTP 429），引用卡片與相關論文會暫時只顯示原文或錯誤訊息。
- 對照翻譯一次翻一頁、目前這頁優先；9B 模型在 3080 Ti 上一頁約需數十秒，翻過的頁會快取。
- 選字工具列與框選是為滑鼠設計，手機上不好操作。
