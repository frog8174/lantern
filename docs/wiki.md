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
- 都要登入且 workspace 屬於自己（`_ws_or_404`）。同一 workspace 同時只能跑一個 update，第二個回 409。

## 前端
- workspace 頁標題下加分頁切換：「論文」｜「Wiki」。
- Wiki 分頁：左側頁面清單（index 置頂），右側用既有 markdown 渲染（marked + DOMPurify + KaTeX，同 app.js 現有函式）顯示。
- `[[slug]]` → 站內連結切頁；`[[paper:<pid>#p<n>]]` → 顯示成小引用標記（論文短標題 + p.n），點了 `openPaper(pid)` 後跳到該頁。
- 「更新 Wiki」按鈕，旁邊顯示 pending 數；更新中顯示 SSE 的 msg 與進度，結束後重載清單。pending 為 0 時按鈕停用。
- 空狀態：還沒有任何頁面時，說明按「更新 Wiki」會做什麼。
- 不用 `prompt()/confirm()/alert()`。

## 這次不做
用 wiki 回答問題、定期一致性檢查、使用者編輯、論文移出 workspace 時改寫頁面、頁面版本紀錄。
