# Lantern 視覺系統（燈下的那一頁）

打樣：https://claude.ai/artifact/KiXgSmJRyK9C4PBxLBq2gJ （四張板：基礎、元件、書架首頁、淺色主題）

## 原則
1. 深色書桌是主場，論文是桌上最亮的紙。
2. **燈光色只代表「目前位置／進行中」**：目前分頁、目前 Wiki 頁、輸入中的欄位與鍵盤焦點、正在讀的句子、翻譯或整理中的進度、點亮的星號。絕不當裝飾。
3. 朱色只用在刪除、錯誤。
4. 動態只回應操作；拿掉卡片 hover 浮起等裝飾性動畫。
5. 不用：全大寫小標（LIBRARY）、◆ 裝飾、中點分隔「A · B」、中文斜體（中文沒有斜體，強調用字重）。

## 色彩 token
| token | 深色（預設 prefers-color-scheme: dark） | 淺色 | 用途 |
|---|---|---|---|
| `--desk` | `#1C1B19` | `#E9E7E2` | 頁面底 |
| `--panel` | `#24221F` | `#F4F3EF` | 卡片、面板、對話框 |
| `--sheet` | `#F3F0EA` | `#FFFFFF` | 論文本身：縮圖、Wiki 內文、回答 |
| `--sheet-ink` | `#2A2825` | `#23211E` | 紙上的字 |
| `--ink` | `#E6E0D4` | `#23211E` | 桌上的字 |
| `--ink-2` | `#A9A193` | `#5E594F` | 次要字（≥4.5:1） |
| `--rule` | `#3A3732` | `#D3D0C8` | 細線 |
| `--rule-strong` | `#4A463F` | `#B9B5AC` | 輸入框、次要按鈕邊框 |
| `--lamp` | `#E8B85C` | `#A06E14` | 燈光：線、圈、焦點（淺色用深琥珀以達 3:1） |
| `--lamp-fill` | `rgba(232,184,92,.38)` | `rgba(232,184,92,.40)` | 燈光照到的文字底 |
| `--seal` | `#D9836E` | `#A9452F` | 刪除、錯誤 |
| `--link` | 紙上 `#2F4F6B` | `#2F4F6B` | Wiki 站內連結（點線底線） |
- 主要按鈕：深色模式 `--ink` 底 + `--desk` 字；淺色模式 `--ink` 底 + 白字。每個畫面最多一個。
- 圓角依材質：紙 2px、控制項 6px、卡片 8px、對話框 10px。
- 既有的螢光筆色、自動標註三類色維持現有值（閱讀頁 UX 定案後再調）。

## 字體分工
| 角色 | 字體 | 用在 |
|---|---|---|
| 標題 | `"Source Serif 4", "Noto Serif TC", serif` | 論文標題、研究主題名稱、頁面標題、Wiki 頁標題 |
| 內文 | `"LXGW WenKai TC", serif`，行高 1.9 | Wiki 內文、翻譯譯文、使用者的備註、問答裡的問題（含輸入框）、使用者畫的標註註解 |
| 工具 | `"Noto Sans TC", sans-serif` | 按鈕、選單、分頁、數字、標籤、**AI 的回答** |
- Google Fonts：Noto Sans TC 400/500/700、Noto Serif TC 400/600/700、LXGW WenKai TC 400/700、Source Serif 4 400/600。移除 Cormorant Garamond、Libre Baskerville。
- 字級：39 / 25 / 20 / 16 / 14。中文最小 14px（文楷最小 15px）；唯一例外：內文旁的引用標籤 13px。

## 捲軸
- 一般捲動區：細軌、透明底、圓頭；平常 `--rule-strong`，滑鼠移到區塊上變亮。不用燈光色。`scrollbar-width: thin` + `scrollbar-color`，加 `::-webkit-scrollbar` 後備。
- 閱讀器頁面導軌：等閱讀頁 UX 定案。

## 用語
- 「workspace」一律改稱「**研究主題**」（介面文字；程式與 API 名稱不動）。
