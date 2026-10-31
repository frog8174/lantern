# 登入系統：Keycloak（OIDC）

現況：`AUTH_MODE=dev` 測試登入（選使用者、未簽章 cookie `uid`）。所有 API 都經過 `backend/main.py` 的 `current_user()`，正式登入只換這一層。

## 建議架構：後端當 OIDC client（Authorization Code + PKCE）
```
瀏覽器 ──(1) GET /api/auth/login──▶ Lantern 後端 ──302──▶ Keycloak 登入頁
       ◀──(2) 302 /api/auth/callback?code&state── Keycloak
Lantern 後端 ──(3) code 換 token（client secret + PKCE verifier）──▶ Keycloak token endpoint
            ──(4) 驗 ID token：簽章（JWKS）、iss、aud、exp、nonce
            ──(5) 以 sub 對應 users 列（沒有就建立），寫入簽章 session cookie
瀏覽器 ◀── 302 回首頁（之後每個請求帶 session cookie，current_user() 讀它）
登出：清 session → 302 到 Keycloak end_session_endpoint（id_token_hint + post_logout_redirect_uri）
```
- **為什麼放在後端**：token 不進瀏覽器（只有 HttpOnly session cookie），前端幾乎不用改；`current_user()` 換實作即可，其餘 API 不動。
- **套件**：Authlib（Starlette 整合，處理 discovery、state、nonce、PKCE、JWKS 驗章）＋ Starlette `SessionMiddleware`（itsdangerous 簽章 cookie）。驗章、JWKS 輪替這類安全邏輯不自己寫。
- **Session**：簽章 cookie（HttpOnly、Secure、SameSite=Lax），只放 `uid` 與 `id_token`（登出用），有效期與 Keycloak session 對齊（例如 8 小時）；過期 → 401 → 前端導向 `/api/auth/login`。
- **使用者對應**：`users.id = sub`（Keycloak 使用者 UUID，不會變）；`name` 取 `name` 或 `preferred_username`，另存 `email`。每次登入更新名稱與 email。
- **權限（可選）**：限定 Keycloak 群組或 client role（例如 `lantern-user`）才能登入；不符 → 403 頁面說明找誰開通。

## 設定（`.env`／k8s Secret）
| 變數 | 例 | 說明 |
|---|---|---|
| `AUTH_MODE` | `oidc` | 本機開發仍可用 `dev` |
| `OIDC_ISSUER` | `https://sso.example.com/realms/research` | 公開 issuer，必須與 token 的 `iss` 完全相同 |
| `OIDC_INTERNAL_URL` | `http://keycloak.keycloak.svc:8080/realms/research` | 選填：Pod 連不到公開網域時（hairpin），discovery／token／JWKS 走叢集內位址，但仍以公開 issuer 驗 `iss` |
| `OIDC_CLIENT_ID` / `OIDC_CLIENT_SECRET` | `lantern` / （Secret） | confidential client |
| `PUBLIC_BASE_URL` | `https://lantern.example.com` | 組 redirect URI；Ingress 終結 TLS 時不能靠請求的 Host |
| `SESSION_SECRET` | （Secret，≥32 bytes 隨機） | session cookie 簽章 |
| `OIDC_REQUIRED_ROLE` | `lantern-user` | 選填 |

## Keycloak 端要建的 client
- Client type：OpenID Connect、**Client authentication ON**（confidential）、Standard flow ON、Direct access grants OFF、PKCE `S256`。
- Valid redirect URIs：`https://lantern.example.com/api/auth/callback`（本機測試再加一個 dev client：`http://localhost:7800/api/auth/callback`）。
- Valid post logout redirect URIs：`https://lantern.example.com/`；Web origins：`https://lantern.example.com`。
- （選）client role `lantern-user`，指派給允許的使用者或群組；mapper 讓 role 進 ID token。

## k8s 部署要一起處理的事（不處理會壞）
1. **反向代理標頭**：uvicorn 加 `--proxy-headers --forwarded-allow-ips=<ingress 網段>`，否則 redirect URI 變成 http。
2. **SQLite 與多副本**：SQLite 只能單寫者 → **replicas: 1** + PVC（`DATA_DIR`）；要多副本得先換 Postgres。
3. **背景工作在記憶體**：Wiki 更新、整篇翻譯、書目預取都在程序內（`_wiki_jobs`、`_translating`…），Pod 重啟會中斷（已保存的部分不會掉，重按會續做）。單副本可接受；多副本前要改成工作佇列。
4. **Secrets**：`OIDC_CLIENT_SECRET`、`SESSION_SECRET`、模型 API key 放 k8s Secret，不進映像檔。
5. **健康檢查**：`/api/health` 目前會真的打模型（花錢、慢）→ 加一個不打模型的 `/api/livez` 給 probe。

## 既有資料
測試帳號（alice、bob）的論文會留在原 user id 下。上線時二選一：清空重來，或做一次性對應（以 email 把 `alice` 的資料改掛到某個 Keycloak `sub`）。

## 待確認
1. Keycloak 的 issuer（網域＋realm 名稱），以及 Lantern 之後的公開網域。
2. Pod 能不能直接連到 Keycloak 的公開網域（決定要不要 `OIDC_INTERNAL_URL`）。
3. 要不要限定群組／角色才能登入？
4. 本機開發要不要另建一個 dev client（redirect 到 localhost），還是本機一律用 `AUTH_MODE=dev`？
5. 現有測試資料要不要保留、要對應到哪個帳號？
