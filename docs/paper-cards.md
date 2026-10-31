# 論文卡：備註、星號、排序、複製引用

前後端共用規格。適用 workspace 頁（含「全部論文」）的論文卡。

## 決定
- 備註、星號跟著**論文**走（不分 workspace），同一篇在不同 workspace 看到的一樣。
- 排序選擇存在瀏覽器 localStorage（每人自己的偏好），不進資料庫。
- 引用格式：APA 7、IEEE、MLA 9、BibTeX。格式化用程式碼（確定性），不讓 LLM 排版。

## 資料表（`backend/db.py`）
`papers` 加兩欄：`note TEXT DEFAULT ''`、`starred INTEGER DEFAULT 0`（沿用 init() 裡 PRAGMA table_info + ALTER 的升級寫法）。
`list_papers` 每列多回 `note`、`starred`（bool）、`year`（有書目資料才有，否則 null）。

## API
| 方法 | 路徑 | body / 回傳 |
|---|---|---|
| PATCH | `/api/papers/{pid}` | body 欄位都選填：`{tags?, note?, starred?}`，只改有給的。回 `{tags, note, starred}` |
| GET | `/api/papers/{pid}/cite` | `{bib: {...}, styles: {apa, ieee, mla, bibtex}}`；第一次呼叫才取書目並寫快取 |

**書目資料 `bib`**：`{title, authors: [{given, family}], year, venue, volume, issue, pages, doi, url, arxiv}`，缺的欄位為 null/空。
取得順序（第一次 `/cite` 時，結果存 `cache` kind=`bib`）：
1. arXiv 匯入的論文（檔名 `arXiv-<id>.pdf`）→ arXiv API（`export.arxiv.org/api/query?id_list=`）。
2. 否則用標題查 Semantic Scholar（沿用 features 既有的 `s2_get` / 429 處理），取 authors、year、venue、externalIds.DOI、journal volume/pages。
3. 都失敗 → LLM 從第一頁文字抽 JSON（`complete_json`，task `cite`），不得編造：沒看到就 null。
4. `LLM_MOCK` 與測試不打網路：mock 回固定書目。

**格式化**（純函式，放 `backend/cite.py`，附單元測試）：
- APA 7：`Family, G. G., & Family, G. (Year). Title. Venue, Vol(Issue), pages. https://doi.org/…`（20 位以上作者依 APA 規則截斷可先不做，>20 時列前 19 + … + 最後一位）。
- IEEE：`G. Family, G. Family, and G. Family, "Title," Venue, vol. X, no. Y, pp. A–B, Year, doi: …`
- MLA 9：`Family, Given, et al. "Title." Venue, vol. X, no. Y, Year, pp. A–B.`（3 位以上作者用 et al.）
- BibTeX：`@article{<family><year><第一個實詞>, …}`；arXiv 無 venue 用 `@misc` + `eprint`。
- 缺欄位就略過該段，不留空殼標點。

## 前端（論文卡）
- 卡片底部一列小操作：☆/★ 星號（切換即 PATCH）、備註、引用。
- **備註**：點了在卡片內展開 textarea（不用 prompt()），失焦或 Ctrl+Enter 存；有備註時卡片顯示前兩行摘錄。
- **引用**：點了開一個小選單/對話框列出 APA / IEEE / MLA / BibTeX，各自「複製」按鈕（`navigator.clipboard.writeText`），複製後就地提示「已複製」；載入中顯示等待狀態，失敗顯示原因。
- **排序**：workspace 標題列加排序選單：加入時間（新→舊，預設）、加入時間（舊→新）、標題 A–Z、星號優先、出版年份（沒有年份的排最後）。選擇存 localStorage。
- 點卡片標題仍是打開論文；新操作的點擊不能誤觸開論文。進度圈、刪除/移出按鈕維持原位。
- 不用 `prompt()/confirm()/alert()`；新 id 不可與 index.html 既有 id 重複。

## 這次不做
批次匯出整個 workspace 的引用、Chicago/GB-T 7714 格式、使用者手動修改書目資料。
