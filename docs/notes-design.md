# 筆記本：在 Lantern 裡寫自己的論文筆記（設計稿）

狀態：設計稿，尚未實作。寫給使用者決定方向，也寫給之後實作的人當規格起點。

## 0. 一句話結論
**MVP 不引入編輯器套件**：用原生 `<textarea>`（霞鶩文楷）＋ 既有的 `renderMD()`（marked + DOMPurify + KaTeX）做「編輯｜預覽」切換與寬版左右對照，
加上 Lantern 自己才有的東西：**一鍵把標註／AI 解釋引用進筆記，引用可點回 PDF 那一頁那一段**，以及「AI 從我的標註擬初稿」。
中文輸入法（注音、倉頡、拼音的選字組字）是這個功能的命脈，原生 textarea 是唯一保證零問題的選項；其他編輯器的好處（語法上色、所見即所得）都換不回這個風險。
之後若真的需要語法上色，再升級到 CodeMirror 6（esm.sh + import map），資料格式不用改。

---

## 1. Lantern 現在已經有什麼

| 現有功能 | 在哪裡 | 內容 | 跟「寫筆記」的關係 |
|---|---|---|---|
| 閱讀頁「我的筆記」分頁 | `frontend/app.js` `renderNotes()`、`noteItem()` | 列出 `annotations` 裡 `kind=user`（螢光筆）與 `auto:*`（自動畫重點）；每則一個 `<textarea>` 寫備註，`onchange` 時 `PATCH /api/annotations/{id}` | 是「逐句的旁註」，不是一篇筆記。可當筆記的**素材來源** |
| 「讀懂」裡的 AI 解釋清單 | `renderExplains()` | `kind=explain`，`comment` 存多輪問答（以 `\n---\n` 分段），用 `renderMD` 顯示 | 素材來源：AI 講解過的段落 |
| 註解清單 | `renderComments()` | `kind=comment`，使用者對選字寫的註解 | 素材來源 |
| 論文卡備註 | `papers.note`（見 `docs/paper-cards.md`） | 純文字短備註，卡片上展開 textarea，顯示前兩行摘錄 | 一句話的「這篇在講什麼／為什麼存它」，跟長筆記定位不同 |
| 研究主題 Wiki | `wiki_pages`（見 `docs/wiki.md`） | LLM 擁有、使用者唯讀；連結語法 `[[slug]]`、`[[paper:<pid>#p<n>]]` | 筆記可以**連到** Wiki 頁、沿用同一套引用語法 |
| Markdown 顯示 | `renderMD(el, text)`（app.js 約 L92） | 先把 `$…$`、`$$…$$`、`\(…\)`、`\[…\]` 挖出來保護 → `marked.parse`（cdnjs marked 12.0.2）→ `DOMPurify.sanitize`（3.0.9）→ 放回公式 → `[p.3]` 轉成可跳頁連結 → KaTeX 0.16.9 auto-render | 預覽直接用它，零新依賴 |
| 跳頁 | `goToPage(page, annotationId?)` | 跳到頁並可閃一下該標註 | 引用回連 PDF 的落點 |
| 網址 | `location.hash` = `#<pid>` 開論文 | 只到論文層級 | 匯出時若要「可點回 Lantern」需擴充成 `#<pid>/p3/<aid>`（見開放問題） |

注意：`annotations` 表沒有 `user_id`，歸屬是透過 `papers.user_id`（`_paper_or_404(pid, uid)`）判斷；新表也照這個習慣，但筆記可能不屬於單一論文，所以新表**自己存 `user_id`**（同 `workspaces`）。

結論：**目前沒有任何「長篇、自由書寫」的筆記功能**。「我的筆記」名字容易讓人誤會，它其實是標註清單。

---

## 2. 現成編輯器評估（不使用 bundler、從 CDN 載入）

評估條件依重要性排序：①中文輸入法組字穩定 ②能從 cdnjs/jsdelivr/esm.sh 釘版本載入、不用打包 ③Markdown 來回不失真（存的就是 .md）④能用霞鶩文楷（非等寬字）⑤KaTeX ⑥用 CSS 變數吃深淺主題 ⑦授權與維護 ⑧體積。

| 方案 | 載入方式 | 體積（約） | 中文輸入法 | Markdown 保真 | 字體 | KaTeX | 主題 | 授權／維護 | 適合度 |
|---|---|---|---|---|---|---|---|---|---|
| **原生 textarea + 既有 `renderMD`** | 不用載 | 0 | 瀏覽器原生，**完美** | 100%（存的就是原文） | 任意（文楷） | 已有 | 已有 token | — | **MVP 首選** |
| **CodeMirror 6**（或 ink-mde 包裝） | 官方不提供瀏覽器單檔，需 esm.sh + import map 讓所有 `@codemirror/*` 共用同一份 `@codemirror/state`[^cm-esm][^cm-status]；ink-mde 官方支援 esm.sh[^ink] | 150–300 KB | CM6 重寫了輸入層，大致可用，但仍有零星中文標點掉字等回報[^cm-ime-punct][^cm-dev-1654] | 100%（純文字編輯器） | 任意 | 需自寫預覽 | 用 `EditorView.theme` + CSS 變數 | MIT，維護活躍 | **第二階段升級選項** |
| **EasyMDE** | jsdelivr 單檔 `easymde.min.js` + css[^easymde] | ~300 KB（含 CM5） | 底層 CodeMirror 5，維護者表示輸入法問題留給 CM6 解[^cm5-5087]；有選取中文字內容消失的回報[^cm5-7021] | 100% | 任意 | 預覽可接自訂 `previewRender` → `renderMD` | 要覆寫一堆 class | MIT，2.21.0[^easymde] | 可用但不建議（CM5 已停止演進） |
| **OverType** | jsdelivr IIFE/ESM 單檔[^overtype] | ~117 KB | 原生 textarea（理論上好），文件未談 CJK | 100% | **必須等寬、同字級**[^overtype] | 無 | 內建 Solar/Cave 主題物件 | MIT | 不適合：違反「筆記用文楷」 |
| **Toast UI Editor 3** | cdn 有 `toastui-editor-all.min.js` | ~500 KB+ | WYSIWYG 端是 ProseMirror[^tui] | Markdown↔WYSIWYG 轉換會改寫格式 | 可覆寫 | 需外掛 | 有 dark theme css | MIT；3.0 之後少有大版更新，維護狀態不明[^tui] | 不建議：太重、風格難融入 |
| **Milkdown Crepe** | npm/jsdelivr 有 ESM build，官方範例以 bundler 為主[^crepe] | 數百 KB | ProseMirror，contentEditable 組字有已知坑[^pm-ime] | 走 remark，大致保真但會正規化 | 可 | 有 latex 外掛 | CSS 變數 | MIT，維護活躍 | 第三選：要所見即所得時再看 |
| **Tiptap** | 官方提供 esm.sh「測試／示範用」[^tiptap] | 中等，外掛另計 | ProseMirror（同上） | **核心不是 Markdown**，要外掛轉換，會失真 | 可 | 外掛 | headless，自己寫 | MIT 核心 + 付費外掛 | 不建議 |
| Editor.js | CDN 可 | 小 | contentEditable | 輸出 JSON block，**不是 Markdown** | 可 | 外掛 | 自己寫 | Apache-2.0 | 不適合 |
| Lexical | 需 bundler 為主 | 中 | contentEditable | 需轉換 | 可 | 自己寫 | 自己寫 | MIT | 不適合（無打包環境） |

**前三名**：
1. **原生 textarea + `renderMD`**：零依賴、輸入法零風險、文楷原生可用、預覽與 Wiki／AI 回答顯示完全一致。缺點是沒有語法上色，工具列與快捷鍵要自己寫（約 100 行）。
2. **CodeMirror 6（esm.sh import map，或 ink-mde）**：語法上色、行內高亮、未來可做 `[[` 自動完成。代價是第一個 ES module 依賴、要處理多份 `@codemirror/state` 的坑、中文輸入法要實測。
3. **Milkdown Crepe**：真正所見即所得、Notion 風。但 contentEditable 的輸入法風險最高，且「存的是不是原本那份 Markdown」不保證。

為什麼不挑所見即所得：論文筆記大量出現公式、引用標記 `[[paper:…]]`、表格，原文可控比漂亮重要；匯出到 Obsidian 也要求 Markdown 原文乾淨。

---

## 3. 別人怎麼做論文筆記（取重點）

| 產品 | 值得學的 | Lantern 要不要做 |
|---|---|---|
| Zotero 7 筆記 | 從標註拖進筆記，自動帶引用與回 PDF 位置的連結；筆記模板以 `{{highlight}} {{citation}} {{comment}}` 組合[^zotero-tpl]；使用者一直要求更精確的「回到該標註」連結[^zotero-link] | **要**：引用標註 = 原文 + 頁碼 + 可點回該標註 |
| Readwise Reader | 右側 Notebook 集中所有標註，匯出 Markdown 模板可自訂（Jinja2），直接接 Obsidian[^readwise] | 要（匯出）；自訂模板之後再說 |
| Obsidian + Zotero Integration | 以 citekey 為檔名、YAML frontmatter 放書目、每段標註附回 Zotero 的連結 | **要**：匯出 .md 帶 frontmatter（title/authors/year/doi） |
| MarginNote / LiquidText | 筆記與原文空間上並排、拉線連結 | 部分：寬版左右並排（PDF｜筆記） |
| Heptabase | 白板卡片、跨文件主題整理 | 對應到「研究主題筆記」，之後再說 |

共通要素：①引用帶回連 ②每篇論文一份 + 跨論文主題筆記 ③模板 ④乾淨的 Markdown 匯出。AI 擬稿是 Lantern 可以做得比它們好的地方（已有標註、AI 解釋、摘要可當素材）。

---

## 4. 設計提案

### 4.1 範圍
**MVP**
- 每篇論文一份筆記（使用者 × 論文唯一）。
- 編輯：textarea（文楷 15px、行高 1.9），模式切換「編輯｜預覽」；寬版時「左編輯右預覽」。
- 小工具列：粗體、標題、清單、引用區塊、公式 `$`、插入 Wiki 連結；快捷鍵 Ctrl+B / Ctrl+I / Ctrl+K（連結）。
- 引用進筆記：①「我的筆記→標註」每則多一個「引用」按鈕 ②PDF 選字後選字列與右鍵選單多一項「引用到筆記」（快捷鍵 `Q`，目前 e/h/t/c 已占用）。
- 自動儲存（停止打字 1 秒後 + 失焦 + 關分頁前），顯示「已儲存 14:03」。
- 匯出：.md（Obsidian 友善）、列印／存 PDF。
- AI 擬初稿（從標註／註解／AI 解釋／摘要）。

**之後**
- 研究主題筆記（workspace 層、跨論文）、Wiki 編輯合流、版本紀錄還原、.docx、自訂匯出模板、`[[` 自動完成、CodeMirror 6 語法上色、筆記全文搜尋併入書庫搜尋。

**不做**：即時多人協作、所見即所得。

### 4.2 資料表（`backend/db.py`）
```
notes (
  id TEXT PRIMARY KEY,          -- uuid hex，同 annotations
  user_id TEXT NOT NULL,
  paper_id TEXT,                -- 論文筆記；研究主題筆記為 NULL
  workspace_id TEXT,            -- 研究主題筆記（之後）；論文筆記為 NULL
  title TEXT DEFAULT '',
  markdown TEXT DEFAULT '',
  created REAL, updated REAL
);
CREATE UNIQUE INDEX IF NOT EXISTS notes_paper ON notes(user_id, paper_id) WHERE paper_id IS NOT NULL;
```
- 刪論文 → 刪其筆記（照 `delete_paper` 一併清 annotations 的做法）。刪研究主題 → 刪其主題筆記。
- 版本紀錄 MVP 不做；但衝突保護要做：PUT 帶 `base_updated`，與資料庫 `updated` 不同 → 409，前端提示「另一個分頁改過了」並給兩份讓使用者選（避免兩個分頁互相覆蓋造成資料遺失）。
- 之後要版本：`note_versions(note_id, markdown, saved)`，每 10 分鐘有變更才存一份、保留 50 份。

### 4.3 引用語法（沿用 Wiki）
- 論文頁：`[[paper:<pid>#p<n>]]`（已存在，Wiki 前端已會渲染成「短標題 p.n」引用標記）。
- **新增**標註錨點：`[[paper:<pid>#p<n>@<annotation_id>]]`，點了 `openPaper(pid)` → `goToPage(n-1, aid)`；該標註被刪 → 退回只跳頁。
- 本篇內的簡寫 `[p.3]` 已被 `renderMD` 轉成跳頁連結，照用。
- 「引用」插入的格式：
  ```
  > 選到的原文句子
  > [[paper:3f2a…#p3@9c1e…]]

  （游標停在這裡，接著寫自己的想法）
  ```
  有使用者備註（`annotation.comment`）就附在引用區塊下一行。
- 實作：把 Wiki 的 `[[…]]` 轉換抽成共用函式，筆記預覽與 Wiki 共用，只多解析 `@aid`。

### 4.4 API
全部要登入；論文筆記用 `_paper_or_404(pid, uid)` 檢查歸屬。

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/api/papers/{pid}/note` | `{id, title, markdown, updated}`；還沒寫過回空內容、`updated: null`（不建列） |
| PUT | `/api/papers/{pid}/note` | body `{markdown, title?, base_updated}` → 新增或更新；衝突 409 回 `{markdown, updated}`（伺服器版本）。回 `{updated}` |
| POST | `/api/papers/{pid}/note/draft` | SSE（沿用 `sse()`），body `{sources: ["highlights","comments","explains","summary"]}`，串回 Markdown 草稿；**不寫入資料庫**，由前端插入游標處後走正常儲存 |
| GET | `/api/papers/{pid}/note/export.md` | （選做）伺服器組 frontmatter；MVP 前端組就好 |

markdown 大小上限 1 MB（信任邊界驗證）。

### 4.5 介面位置
閱讀頁右側「我的筆記」分頁內加分段切換：**「標註｜筆記本」**（標註 = 現在的清單，不動）。
右側面板窄，所以筆記本有「展開」鈕：把右側面板拉寬到約 50%，PDF 縮在左邊並排（MarginNote 式），此時編輯與預覽左右對照。
論文卡底部的「備註」維持原樣（見 4.8）；卡片多一個小標記「有筆記」，點了開論文並直接到筆記本。

**窄版（預設，右側面板）**
```
┌ PDF ─────────────────────────────┐┌ 讀懂｜我的筆記｜文獻｜Wiki ──────┐
│                                   ││  [ 標註 | 筆記本 ]       ⤢ 展開   │
│   ...the model attends to ...     ││ ─────────────────────────────── │
│   ████████ (選字)                 ││ [編輯|預覽]  B  H  •  ❝  ∑  [[ ] │
│   ┌──────────────────────────┐    ││ ┌─────────────────────────────┐ │
│   │解釋 畫重點 翻譯 註解 引用│    ││ │## 這篇在解決什麼            │ │
│   └──────────────────────────┘    ││ │> attention is all you need  │ │
│                                   ││ │> [[paper:…#p3@…]]           │ │
│                                   ││ │我覺得這裡的假設是…▌         │ │
│                                   ││ └─────────────────────────────┘ │
│                                   ││ AI 從標註擬初稿   匯出 ▾  已儲存 14:03│
└───────────────────────────────────┘└──────────────────────────────────┘
```

**寬版（展開後）**
```
┌ PDF（縮窄）──────────┐┌ 筆記本：Attention Is All You Need ──────── ⤡ 收合 ┐
│                       ││ B  H  •  ❝  ∑  [[ ]]           匯出 ▾  已儲存 14:03│
│  ...attends to ...    ││ ┌ 編輯（文楷）──────────┐┌ 預覽（sheet 紙面）────┐│
│                       ││ │## 方法                 ││ 方法                   ││
│                       ││ │> Scaled dot-product…   ││ ┃ Scaled dot-product…  ││
│                       ││ │> [[paper:…#p4@…]]      ││ ┃ Attention… p.4  ←可點││
│                       ││ │$\mathrm{softmax}(QK^T)$││ softmax(QKᵀ/√d)V      ││
│                       ││ └────────────────────────┘└────────────────────────┘│
└───────────────────────┘└───────────────────────────────────────────────────┘
```

**AI 擬稿對話框**
```
┌ 從我的標註擬初稿 ─────────────────────┐
│ 要用的素材：                           │
│ [x] 螢光筆標註與備註（23 則）          │
│ [x] 註解（4 則）                       │
│ [x] AI 解釋（6 則）                    │
│ [ ] 摘要                               │
│ 草稿會插在游標處，不會覆蓋你寫的內容。 │
│                       取消   [ 擬稿 ]  │
└────────────────────────────────────────┘
```
視覺：編輯區底色 `--desk`、字 `--ink`、焦點框 `--lamp`（燈光＝輸入中，符合 design.md 原則 2）；預覽用 `--sheet` 紙面，同 Wiki 內文；使用者寫的字一律文楷。

### 4.6 自動儲存
- 停止輸入 1 秒（`compositionend` 之後才計時，組字中不存）、失焦、`visibilitychange` 為 hidden 時存。
- 失敗保留在 `localStorage`（`lantern.note.<pid>`）當草稿，下次開啟若比伺服器新就提示「有未儲存的草稿，要還原嗎？」。這是避免資料遺失的必要保護，不是快取。

### 4.7 匯出
全部在前端做（不加後端依賴）：
| 格式 | 做法 |
|---|---|
| **.md（Obsidian 友善）** | `Blob` 下載。開頭 YAML frontmatter：`title, authors, year, doi, url, tags`（書目取 `/cite` 的 `bib`，沒有就略）；`[[paper:<pid>#p3@…]]` 轉成 `（p.3）`，可選附 Lantern 深連結；`[[slug]]` 轉成 Wiki 頁標題純文字或 Obsidian `[[標題]]`。Notion 匯入 Markdown 也吃這份 |
| **列印／存 PDF** | 開一個只含預覽的列印頁，`@media print` 樣式（白底、文楷、KaTeX 已渲染），`window.print()` |
| .docx（之後） | 兩個選項：前端 `docx` 套件（要走 ESM、體積大）或後端 pandoc（映像檔多約 100 MB）。先看有沒有人要 |

### 4.8 跟論文卡備註（`papers.note`）的關係
**建議：保留兩者，不合併。** 卡片備註是「一句話標籤」，在書架上一眼看到；筆記本是長文，在閱讀頁寫。合併會讓卡片摘錄變成筆記開頭的 `## 標題` 之類的雜訊。
筆記本頂端顯示卡片備註（唯讀、點了可改），讓兩者看得到彼此。日後若使用者覺得重複，再做「把卡片備註變成筆記第一段」的一次性遷移。

### 4.9 AI 擬初稿
- 新 task 名稱 `note`，加進 `config.TEXT_TASKS`，`.env` 可設 `LLM_MODEL_NOTE`，沒設走 `LLM_MODEL`；`LLM_MOCK` 回固定草稿，測試不打模型。
- prompt 放 `features.py`：輸入為所選素材（每則帶 `pid`、頁碼、`aid`、原文、使用者備註／AI 解釋），要求：用 `TARGET_LANG`、以**使用者的觀點與備註為主軸**組織（而不是重寫論文摘要）、每個論點附 `[[paper:<pid>#p<n>@<aid>]]`、不得捏造素材外的內容、標註少於 3 則就回一段說明請使用者多標一點。
- 成本：素材通常 2–8k tokens 輸入、1–2k 輸出；以 Haiku 級模型約 US$0.01 以內一次，本機 vLLM 免費。素材超過 `LLM_CONTEXT_TOKENS` 時依頁碼順序截斷並在草稿最後註明。
- 串流呈現：草稿先串到對話框內的預覽，使用者按「插入」才放進筆記（避免邊串邊改 textarea 打亂游標與組字）。

### 4.10 測試與驗收重點
- 後端：歸屬（別人的 pid 404）、唯一索引（同一篇只有一份）、409 衝突、刪論文連帶刪筆記、1 MB 上限、mock 擬稿。
- 前端（Chrome 實測）：注音／倉頡／拼音輸入時自動儲存不打斷組字；`$…$` 與引用標記在預覽正確；引用點了跳到正確頁並閃標註；匯出 .md 在 Obsidian 開起來 frontmatter 正確；深淺主題；新 id 不與 index.html 既有 id 重複。

---

## 5. 建議與理由（摘要）
1. **編輯器用原生 textarea + `renderMD`**：中文輸入法零風險、零新依賴、字體與主題直接沿用、預覽與 Wiki 一致。
2. **差異化放在「引用回連」與「AI 從標註擬稿」**，這兩件是 Zotero／Readwise 沒做好、而 Lantern 已有素材的部分。
3. **MVP 只做每篇論文一份筆記**，放在閱讀頁「我的筆記」分頁內的「筆記本」，可展開成並排寬版；研究主題筆記等 MVP 用過再做。
4. **匯出 .md（帶 frontmatter）+ 列印 PDF 先做，.docx 看需求。**
5. **論文卡備註保留**，筆記本頂端顯示它。

## 6. 開放問題（請使用者決定）
1. 每篇論文**一份**筆記夠嗎？還是要能開多份（例如「讀書會報告」「方法細節」各一）？
2. 「研究主題筆記」（跨論文）要不要進 MVP？要的話放研究主題頁第四個分頁「論文｜Wiki｜問答｜筆記」。
3. 筆記本放在「我的筆記」分頁裡（分段切換），還是另開第五個分頁「筆記本」？右側分頁已有四個。
4. 匯出 .md 時引用要不要附**可點回 Lantern 的網址**？要的話網址 hash 需擴充成 `#<pid>/p3/<aid>`，且分享出去別人點不開（要登入且是本人的論文）。
5. 需要 .docx 嗎？（決定要不要加 pandoc 或前端 docx 套件）
6. AI 擬稿的預設語氣：條列重點、還是成段的讀書筆記？要不要提供幾個模板（讀書會報告、文獻回顧段落、方法比較）？
7. 筆記要不要被「問 AI」與 Wiki 當素材（例如 Wiki 更新時參考你的筆記）？這會讓私人想法進入 LLM 整理的頁面。
8. 論文卡備註要維持獨立，還是乾脆併進筆記第一段？

---

## 參考資料
[^cm-esm]: CodeMirror 論壇，ESM-compatible CodeMirror build（esm.sh `*` 前綴 + import map 共用 `@codemirror/state`）：https://discuss.codemirror.net/t/esm-compatible-codemirror-build-directly-importable-in-browser/5933
[^cm-status]: CodeMirror 6 status update（作者表示不提供瀏覽器預建檔）：https://discuss.codemirror.net/t/codemirror-6-status-update/2792
[^ink]: ink-mde（CodeMirror 6 Markdown 編輯器，官方支援 esm.sh）：https://npmjs.com/package/ink-mde
[^cm-ime-punct]: CodeMirror 論壇，中文輸入法標點每兩下掉一下：https://discuss.codemirror.net/t/chinese-ime-punctuation-input-loses-every-other-keypress-requires-2-presses-per-character/9741
[^cm-dev-1654]: codemirror/dev #1654（組字與 decoration）：https://github.com/codemirror/dev/issues/1654
[^cm5-5087]: codemirror5 #5087（輸入法問題留待 CM6）：https://github.com/codemirror/codemirror5/issues/5087
[^cm5-7021]: codemirror5 #7021（選取剛輸入的中文字後內容消失）：https://github.com/codemirror/codemirror5/issues/7021
[^easymde]: EasyMDE（MIT，CodeMirror 5，jsdelivr 載入方式）：https://npmjs.com/package/easymde ；https://summary.ecosyste.ms/projects/373005
[^overtype]: OverType README（MIT、約 117 KB、須等寬同字級）：https://cdn.jsdelivr.net/npm/overtype@2.4.0/README.md ；https://github.com/panphora/overtype
[^tui]: TOAST UI Editor 3.0 改用 ProseMirror（CodeZine）：https://codezine.jp/news/detail/14461 ；https://github.com/nhn/tui.editor
[^crepe]: Milkdown Crepe：https://www.jsdelivr.com/package/npm/@milkdown/crepe ；https://npmjs.com/package/@milkdown/crepe
[^pm-ime]: ProseMirror 論壇，組字跨段落問題：https://discuss.prosemirror.net/t/issue-report-issue-on-composition-with-a-selection-cross-paragraph/4535 ；IME 多出文字：https://discuss.prosemirror.net/t/extra-unexpected-text-input-when-selection-end-is-touch-mark-which-inclusive-is-false-with-ime-mode/6603
[^tiptap]: Tiptap CDN 安裝（esm.sh，測試／示範用）：https://tiptap.dev/docs/editor/installation/cdn
[^zotero-tpl]: Zotero Note Templates：https://www.zotero.org/support/note_templates
[^zotero-link]: Zotero 論壇，模板缺 PDF 位置連結：https://forums.zotero.org/discussion/comment/424174/ ；拖曳只產生 Go to Page：https://forums.zotero.org/discussion/110125/zotero-7-beta-cannot-quickcopy-a-note-annotation-that-does-not-have-a-comment-on-it
[^readwise]: Readwise Reader 匯出（Jinja2 Markdown 模板）：https://docs.readwise.io/reader/docs/faqs/exporting ；Obsidian 匯出：https://docs.readwise.io/readwise/docs/exporting-highlights/obsidian

（以上網路資料於 2026-11 查證；版本號與維護狀態實作前請再確認並釘版本。）
