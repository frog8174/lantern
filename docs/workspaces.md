# 多使用者論文庫 + Workspace（測試登入版）

前後端共用的規格。改了這份就要同步告知另一邊。

## 決定
- 論文 ↔ workspace 多對多；首頁另有「全部論文」方塊。
- 測試登入：選使用者、免密碼，只在 `AUTH_MODE=dev` 開放。
- 閱讀頁：側欄不動，加「← 回論文庫」按鈕。
- 舊資料清空，新 schema 直接寫進 `CREATE TABLE`，不做遷移。

## 資料表（`backend/db.py`）
```
users            (id TEXT PK, name TEXT, created REAL)
workspaces       (id TEXT PK, user_id TEXT, name TEXT, created REAL)
workspace_papers (workspace_id TEXT, paper_id TEXT, added REAL, PRIMARY KEY (workspace_id, paper_id))
papers           + user_id TEXT
```
- `delete_paper` 一併刪 `workspace_papers`。
- `list_papers(uid, workspace=None)`、`search_chunks(uid, q)` 只看該使用者。

## 登入
- `.env`：`AUTH_MODE=dev`、`TEST_USERS=alice,bob`（`db.init()` 建立；user id = 名字）。
- Cookie `uid`；`current_user()` dependency，沒登入或不存在 → 401。
  未簽章 cookie，只能 dev 用；正式登入只換 `current_user()`。
- `GET /api/auth/users` → `[{id, name}]`（只在 dev）
- `POST /api/auth/login {user_id}` → `{id, name}` 並設 cookie
- `POST /api/auth/logout` → `{ok: true}`
- `GET /api/me` → `{id, name}` 或 401
- `/api/health` 與靜態檔不需登入。

## 範圍限制
- `_paper_or_404(pid, uid)`：別人的論文 → 404。所有 `/api/papers/{pid}/...` 都經過它。
- 也要限制：`GET /api/papers`、`/api/search`、`_mark_in_library`、`/api/recommendations`、上傳 / arXiv 匯入寫入 `user_id`、`/api/annotations/{aid}` 的改 / 刪（檢查註解所屬論文）。

## Workspace API
| 方法 | 路徑 | body | 回傳 |
|---|---|---|---|
| GET | `/api/workspaces` | | `[{id, name, created, count}]`（新到舊） |
| POST | `/api/workspaces` | `{name}` | `{id, name, created, count}` |
| PATCH | `/api/workspaces/{wid}` | `{name}` | 同上 |
| DELETE | `/api/workspaces/{wid}` | | `{ok: true}`；論文保留在全部論文 |
| POST | `/api/workspaces/{wid}/papers` | `{paper_id}` | `{ok: true}`（重複加入不報錯） |
| DELETE | `/api/workspaces/{wid}/papers/{pid}` | | `{ok: true}` |
| GET | `/api/papers?workspace=<wid>` | | 原本的論文清單格式，只含該 workspace |

- 上傳 `POST /api/papers`（multipart）可帶 form 欄位 `workspace`；`POST /api/papers/arxiv` body 可帶 `workspace`。有帶就同時加入該 workspace。
- 別人的 workspace → 404。

## 前端畫面
```
登入頁（使用者卡片）
 → 首頁：大方塊網格 [全部論文] [workspace…] [＋ 新增]
   → workspace 頁：論文卡片網格（上傳到這裡 / 加入既有論文 / 移出 / 改名 / 刪除）
     → 閱讀頁（原樣 + ← 回論文庫）
右上角：使用者名稱 · 登出
```
- `api()` 收到 401 → 顯示登入頁。

## 這次不做
卡片縮圖、跨使用者共用解析快取、正式登入、分享 workspace。
