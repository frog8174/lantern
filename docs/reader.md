# 閱讀器：選取、螢光筆與中英對照

## 連續的選取與螢光筆
- PDF.js 文字層的 span 之間有縫，原生選取色和存下來的 `getClientRects()` 畫出來都是一格一格的。
- `mergeRects()`（`frontend/app.js`）把矩形併成每行一條色帶：垂直重疊的算同一行、x 接起來（相距超過頁寬 2.5% 才分開，例如雙欄）；上下兩行靠得近就切在中線，剛好相接、不重疊加深。結果再併一次不變。
- 存標註（`readSelection`）和畫標註（`drawHighlights`）都過一次，所以舊標註不用改資料也會連續。
- 文字層的 `::selection` 設成透明，選取中改由 `.selLayer .sel` 用燈光色（`--lamp-fill`）畫；選取消失就清掉。

## 並排模式：對應的段落亮起來
- 在原文頁選字：選取範圍和哪些翻譯區塊（`S.tr[頁][i].bbox`）重疊，譯文頁那些 `.trb` 加 `.lit`（燈光色框 + 淡底），原文頁同一區塊畫淡淡的燈光框（`.srcbox`）。
- 在譯文頁選中文：選到的 `.trb` 一樣兩邊都亮。對應是區塊層級，不自動捲動。
- 譯文頁（`.twin`）也有 `data-page`，選中文一樣會出現選字工具列。

## 螢光筆同步到譯文
- 在英文上畫螢光筆（這頁的譯文已翻完時）：取重疊面積最大的翻譯區塊，呼叫 `/align` 問模型譯文裡對應哪一段，結果用 `PATCH /api/annotations/{id}` 存在標註的 `align` 欄（`{"block": i, "zh": "…"}`），之後不再問。
- 在中文（並排頁或疊加層）上畫螢光筆：反向對回英文原句，後端用 PyMuPDF 找出原句在頁上的位置當標註矩形；找不到就用整個區塊。`align.zh` 就是選到的中文。
- 譯文裡用 `<mark class="trm">` 標出 `zh`（標註的顏色）；`zh` 是空的或在譯文裡找不到，就淡淡地標整段。疊加、並排兩份都畫。刪除標註兩邊一起消失。
- 限制：畫螢光筆時這頁譯文還沒翻完就不會同步（之後也不補）；同一區塊裡重疊的對應段只畫先開始的那段。

## API
`POST /api/papers/{pid}/align`，body `{page, block, quote, direction: "en2zh" | "zh2en"}`（只限論文擁有者）
- 需要這頁的對照翻譯已經在快取（`block_translation`），否則 409。
- 模型（task `align`，`LLM_MODEL_ALIGN`，沒設就同 `LLM_MODEL_TRANSLATE`，effort 預設 low）只能從另一邊逐字抄一段；不是子字串就當失敗。
- 回傳 `{match, fallback}`：`match` 一定是另一邊的子字串，失敗時為 `""`、`fallback: true`（前端改標整段）。`zh2en` 另回 `rects`：英文原句在這個區塊內的位置，找不到就是 `[bbox]`。
- 成功的結果存 `cache`（kind `align`，key `頁:區塊:方向:quote`）；失敗的不快取。

`annotations` 表多一欄 `align TEXT DEFAULT 'null'`（JSON；`init()` 裡用 PRAGMA table_info + ALTER 升級舊資料庫）。`POST /annotations` 可帶 `align`；`PATCH /api/annotations/{id}` 的 `comment`、`align` 都選填，只改有給的。

## 逐句對應（並排模式）
- 選完字（放開滑鼠）後呼叫 `/align`：選英文 → 譯文只亮對應的那句（燈光色 mark，借 `markTranslation` 畫）；選中文 → 原文頁畫出那句的位置（`.srclit`）。
- 等待回應時先顯示整段淡框；回應到了換成逐句，對不到就保留整段淡框。結果有伺服器快取，同一句第二次是即時的。
- 自動標註（新穎／方法／結果）也同步到譯文，用類別色；翻譯前就有的標註在那頁翻完時補同步。
