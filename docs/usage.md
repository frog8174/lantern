# API 用量記錄

每次呼叫 Claude 結束時，`backend/llm.py` 的 `_record()` 會從回應的 `usage` 讀出 token 數，存成 `llm_usage` 表裡的一列：

- 時間、使用者、論文、功能（`chat`、`translate`…）、實際用的模型；
- 輸入、輸出、快取寫入、快取讀取的 token 數；
- 估算的美元金額，用 `llm.PRICES` 價目表計算。快取寫入以輸入價 ×1.25 計算；價目調整時要改這張表。

使用者和論文由 `current_user()` / `_paper_or_404()` 寫進 `llm.usage_ctx`。背景工作（預翻譯、書目）建立時會複製這個值，所以也會記到觸發它的那篇論文。

## 誰看得到
只有 `ADMIN_USERS` 名單裡的人看得到：
- 名單用 email（oidc）或使用者 id（dev），以逗號分隔；
- 本機設在 `.env`，正式環境設在 ConfigMap。

看的地方是「設定 → 查看 API 用量與花費」。內容包括總花費、快取命中率，以及依功能、模型、使用者、論文、日期分組的表格。

API 是 `GET /api/admin/usage?days=30`，非管理者呼叫會得到 403。

## 沒記到的
- 走 OpenAI 相容服務（自架 vLLM）的呼叫：沒有 API 費用，所以不記。
- 中途失敗、沒有拿到最終訊息的串流。
- 實際帳單以 Anthropic Console 為準；這裡是依價目表估算，用來看「哪個功能最花錢」。
