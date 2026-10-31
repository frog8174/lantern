# Workspace LLM Wiki（MVP）

前後端共用規格。參考 Karpathy「LLM Wiki」模式：原始論文不動、wiki 頁由 LLM 擁有並維護、這份文件就是給 LLM 的整理規則（schema）。

## 決定
- 觸發：手動按「更新 Wiki」；只整理還沒整理過的論文（增量）。
- 頁面只由 LLM 寫，使用者唯讀（編輯之後再說）。
- 語言：`config.TARGET_LANG`，專有名詞保留英文原文。
- 每個說法都要能回到原文：引用寫成 `[[paper:<pid>#p<頁碼從 1 起>]]`。

## 資料表（`backend/db.py`）
```
wiki_pages    (workspace_id, slug, title, markdown, sources TEXT /*JSON [pid]*/, updated REAL,
               PRIMARY KEY (workspace_id, slug))
wiki_ingested (workspace_id, paper_id, ingested REAL, PRIMARY KEY (workspace_id, paper_id))
```
- 刪除 workspace → 一併刪它的 wiki 兩張表資料。刪除論文 → 刪 `wiki_ingested` 該篇；頁面保留（shortcut）。

## 頁面種類與 slug
| 種類 | slug | 內容 |
|---|---|---|
| 首頁 | `index` | workspace 主題概述 + 所有頁面分類目錄 |
| 論文頁 | `paper-<pid>` | 這篇的問題、方法、結果、限制，連到相關概念頁 |
| 概念 / 方法 / 資料集頁 | 小寫英文 kebab，例 `attention-mechanism` | 跨論文整理：定義、各論文怎麼用、比較、爭議 |

連結語法（Markdown 內）：
- 頁面互連：`[[slug]]` 或 `[[slug|顯示文字]]`
- 引用原文：`[[paper:<pid>#p<n>]]`

## 更新流程（後端，`features.py` 放 prompt）
對每篇未整理的論文：
1. 取材：標題、摘要；有快取的 summary 就用，沒有就用 `features` 既有方式取全文或前幾頁（受 context 上限控制）。
2. 規劃：LLM 回 JSON：`{paper_page: {title, markdown}, concepts: [{slug, title, note}]}`，給它現有頁面的 slug/title 清單，優先沿用既有概念頁（避免同義重複頁）。
3. 每個概念頁：給舊 markdown（沒有就空）+ 這篇的重點，LLM 回整頁新 markdown（合併，不是附加），保留舊引用。
4. 全部論文處理完，重寫 `index`。
5. 每篇完成就寫 `wiki_ingested`，中斷後重按只做剩下的。
- 用 `llm` 既有的 task 路由（新增 task 名稱 `wiki`，`.env` 可設 `LLM_MODEL_WIKI`，沒設走預設）。`LLM_MOCK` 時回固定假內容，測試不打模型。

## API
| 方法 | 路徑 | 回傳 |
|---|---|---|
| GET | `/api/workspaces/{wid}/wiki` | `{pages: [{slug, title, updated}], pending: <未整理論文數>}`，index 排第一 |
| GET | `/api/workspaces/{wid}/wiki/{slug}` | `{slug, title, markdown, sources, updated}`；不存在 404 |
| POST | `/api/workspaces/{wid}/wiki/update` | SSE（沿用 `sse()`）。每則 `{"t": JSON 字串}`，內容 `{"msg": "...", "done": n, "total": m}`；結束 `[DONE]`；錯誤照 `sse()` 的 `{"error"}` |
- 都要登入且 workspace 屬於自己（`_ws_or_404`）。
- 更新是伺服器背景任務，不綁瀏覽器連線：重新整理、離開頁面都不會中斷。GET 清單多回 `running`；
  已在跑時再 POST 不會另跑一份，而是接上同一個進度串流（前端打開 Wiki 看到 `running` 就自動接回）。

## 前端
- workspace 頁標題下加分頁切換：「論文」｜「Wiki」。
- Wiki 分頁：左側頁面清單（index 置頂），右側用既有 markdown 渲染（marked + DOMPurify + KaTeX，同 app.js 現有函式）顯示。
- `[[slug]]` → 站內連結切頁；`[[paper:<pid>#p<n>]]` → 顯示成小引用標記（論文短標題 + p.n），點了 `openPaper(pid)` 後跳到該頁。
- 「更新 Wiki」按鈕，旁邊顯示 pending 數；更新中顯示 SSE 的 msg 與進度，結束後重載清單。pending 為 0 時按鈕停用。
- 空狀態：還沒有任何頁面時，說明按「更新 Wiki」會做什麼。
- 不用 `prompt()/confirm()/alert()`。

## 這次不做
用 wiki 回答問題、定期一致性檢查、使用者編輯、論文移出 workspace 時改寫頁面、頁面版本紀錄。

---

# 第二階段：Wiki 問答、自動更新、反向連結

## 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）
**流程（先查 wiki，不做向量 RAG）**
1. 頁面挑選：wiki 全文估計放得進 context（沿用 features 的 token 估算與 `LLM_CONTEXT_TOKENS` 規則）就全部帶上；
   放不下就把每頁 slug、title、前 300 字給 LLM，請它挑最多 6 頁（`complete_json`）。
2. 補原文：從挑中頁面的 `sources` 論文，用 `retrieval.search(pid, question, k=4)` 各取段落，標成 `[[paper:<pid>#p<n>]]` 可引用的來源。
3. 回答：系統規則同 `WIKI_RULES`（語言、引用、連結格式、不捏造；wiki 沒寫到就明說）；可用 `[[slug]]` 指向 wiki 頁。
   帶最近 10 則對話。task 名稱 `wiki`（沿用 `LLM_MODEL_WIKI`）。

**資料表**：`wiki_messages (id INTEGER PK AUTOINCREMENT, workspace_id, role, content, created)`；刪 workspace 一併刪。

**API**
| 方法 | 路徑 | 說明 |
|---|---|---|
| POST | `/api/workspaces/{wid}/ask` | body `{question}`。SSE，和單篇聊天一樣每則 `{"t": 文字片段}`，串完寫入 wiki_messages（user + assistant）。wiki 沒有任何頁面 → 400「先按更新 Wiki」 |
| GET | `/api/workspaces/{wid}/ask` | `[{role, content}]` 最近 50 則，舊到新 |
| DELETE | `/api/workspaces/{wid}/ask` | 清空對話 `{ok: true}` |
| POST | `/api/workspaces/{wid}/ask/save` | body `{question, answer}` → LLM 把這則問答整理成一頁 wiki（保留引用），slug `qa-<new_id>`，title 用 LLM 給的短標題，sources = 答案引用到的 pid。回 `{slug, title}` |

**前端**：問答分頁＝對話串（沿用單篇聊天的樣式與 markdown 渲染）、輸入框、清空按鈕。回答裡 `[[slug]]` 點了切到 Wiki 分頁該頁；
`[[paper:…]]` 引用同 Wiki 頁的引用標記。每則回答底下「存成 Wiki 頁」→ 成功後提示並可點過去。wiki 沒頁面時顯示引導（去 Wiki 分頁按更新）。

## 2. 加入論文就自動更新 Wiki（使用者設定）
- `/api/me/settings` 多一個 `auto_wiki: bool`（預設 false），設定視窗多一個勾選項。
- 開啟時：論文加入某 workspace（上傳/arXiv 帶 workspace、或 `POST /api/workspaces/{wid}/papers`）→ 該 workspace 沒在跑就啟動同一個背景更新任務；
  在跑的話，任務結束前若又有 pending 且設定仍開著，就接著再跑一輪（直到沒有 pending）。

## 3. 閱讀頁反向連結
- `GET /api/papers/{pid}/wiki` → `[{workspace_id, workspace_name, slug, title}]`：使用者自己的 workspace 中，sources 含這篇的 wiki 頁（論文頁排最前）。
- 前端：閱讀頁右側「摘要」分頁底下加一段「在 Wiki 中」（沒有就不顯示），點了回到該 workspace 的 Wiki 分頁並打開那頁。
