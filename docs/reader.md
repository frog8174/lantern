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
- 在英文上畫螢光筆（這頁的譯文已翻完時）：取重疊面積最大的翻譯區塊，先查逐句對應表（見下方「逐句對應」），對不到才呼叫 `/align` 問模型譯文裡對應哪一段，結果用 `PATCH /api/annotations/{id}` 存在標註的 `align` 欄（`{"block": i, "zh": "…"}`），之後不再問。
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
- 選完字（放開滑鼠）後：選英文 → 譯文只亮對應的那句（燈光色 mark，借 `markTranslation` 畫）；選中文 → 原文頁畫出那句的位置（`.srclit`）。
- **先查逐句對應表（即時、不連網）**：
  - 後端（`backend/sentalign.py`）把區塊原文、譯文各自切句並記字元位置：英文在 `. ? !` 後切，但跳過 e.g.、i.e.、et al.、Fig.、Eq.、No.、vs. 等縮寫、單一字母縮寫（J.）、小數（28.4）和下一句小寫開頭的；中文在 `。！？；` 和後面接空白的 `; ! ?` 切。
  - 整頁所有句子一次送 LaBSE（`ALIGN_EMBED_URL`，docs/labse.md）拿句向量（英文截 800 字、中文截 250 字，LaBSE 上限 256 token），每個區塊用小型動態規劃配對：允許 1-1、1-2、2-1 與跳過，分數＝(餘弦 − 0.5) × 涵蓋句數 / 2，順序單調。合併句的向量用相加近似。
  - 結果是 `{區塊序號: [{"en": [起, 迄], "zh": [起, 迄], "score", "rects"}]}`，位置是 `b.text` / `b.tr` 的字元索引；`rects` 是英文句在原文頁上的位置（`pdf_parse.find_texts_rects`，只留區塊內的），選中文時直接畫。
  - 何時算：一頁的對照翻譯寫進快取後，背景算好存 `cache`（kind `align_map`，key 頁碼，值帶整頁 [原文, 譯文] 的雜湊；重新翻譯雜湊不同就重算）。舊的、這功能之前就翻好的頁，第一次 `GET /api/papers/{pid}/align-map?page=N` 時現算。同一頁同一版譯文同時只算一次。
  - 前端在那頁翻完時取表放 `S.amap[page]`。`mapPairs()` 把選取的字（去空白、連字號後）在區塊原文／譯文裡找位置；整段找不到（跨區塊）就用頭尾 20 字定位，取重疊到的句對，連續幾句合成一段。
- **退回 LLM**：沒設定 LaBSE、端點失敗（回空表、只印警告，不擋翻譯）、表還沒拿到、或選取在表裡對不到，才呼叫 `/align`。等待回應時先顯示整段淡框；回應到了換成逐句，對不到就保留整段淡框。LLM 結果有伺服器快取。
- 螢光筆同步（`alignHighlight`，使用者與自動標註）和在譯文上畫螢光筆（`highlightTranslation`）也一樣先查表，對不到才問 LLM；存進標註的 `align.zh` 格式不變。
- 自動標註（新穎／方法／結果）也同步到譯文，用類別色；翻譯前就有的標註在那頁翻完時補同步。
