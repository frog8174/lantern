# 部署到 k8s

檔案：`Dockerfile`、`.dockerignore`、`deploy/k8s/`（kustomize）。登入設計見 `docs/auth.md`。

## 架構
```
Ingress（TLS、上傳 160 MB、SSE 不緩衝）
  └ Service lantern :80
      └ Deployment lantern（replicas 1、Recreate）
          ├ ConfigMap lantern-config（非機密設定）
          ├ Secret lantern-secrets（client secret、session secret、模型 key）
          └ PVC lantern-data → /data（SQLite、PDF、縮圖）
```
- **單副本**：SQLite 只能單寫者；Wiki 更新、整篇翻譯等背景工作在程序記憶體。多副本前要先換 Postgres 與工作佇列。
- **Pod 重啟**：背景工作會中斷，已完成的部分（已翻的頁、已整理的論文）保留，重按會續做。
- **映像唯讀**：只有 `/data`（PVC）與 `/tmp`（emptyDir）可寫；以 uid 10001 執行，drop 所有 capabilities。

## 1. 建映像
```bash
docker build -t REGISTRY/lantern:0.1.0 .
docker push REGISTRY/lantern:0.1.0
```
`deploy/k8s/kustomization.yaml` 的 `images.newName／newTag` 改成同一個。

## 2. Keycloak 正式 client
在 realm `Toolmen_application` 另建 client（例如 `lantern`，和本機的 `lantern-local` 分開）：
- Client authentication ON、只勾 Standard flow、PKCE Method **S256**（正式環境要勾）
- Valid redirect URIs：`https://LANTERN_HOST/api/auth/callback`
- Valid post logout redirect URIs：`https://LANTERN_HOST/`
- Web origins：`https://LANTERN_HOST`

## 3. Secret（不要 commit）
```bash
kubectl create namespace lantern
kubectl -n lantern create secret generic lantern-secrets \
  --from-literal=OIDC_CLIENT_SECRET='…' \
  --from-literal=SESSION_SECRET="$(python -c 'import secrets;print(secrets.token_urlsafe(48))')" \
  --from-literal=ANTHROPIC_API_KEY='…'
  # 其他模型 key（LLM_API_KEY、VLM_API_KEY…）照 .env 需要的加
```

## 4. 設定與套用
1. `deploy/k8s/configmap.yaml`：`PUBLIC_BASE_URL`、`OIDC_CLIENT_ID`，並把本機 `.env` 的**非機密**模型設定搬過來。
2. `deploy/k8s/ingress.yaml`：`LANTERN_HOST`、`ingressClassName`、TLS（或打開 cert-manager annotation）。
3. `deploy/k8s/pvc.yaml`：需要時填 `storageClassName`。
4. 套用：`kubectl apply -k deploy/k8s`
5. 驗證：
   ```bash
   kubectl -n lantern rollout status deploy/lantern
   kubectl -n lantern logs deploy/lantern
   curl https://LANTERN_HOST/api/livez        # {"ok": true}
   ```
   然後瀏覽器開 `https://LANTERN_HOST` 登入一次。

## 常見問題
- **登入後 redirect_uri 不符**：`PUBLIC_BASE_URL` 要和 Ingress host 完全一致（含 https）；Keycloak client 的 redirect URI 也要一致。
- **Pod 連不到 Keycloak 公開網域**（叢集 hairpin）：在 Pod 裡 `curl https://keycloak…/realms/…/.well-known/openid-configuration` 測；不通時要加叢集內位址的設定（docs/auth.md 的 `OIDC_INTERNAL_URL`，目前未實作，需要時再做）。
- **SSE 字一次全跳出來**：Ingress 有緩衝；確認 `proxy-buffering: off`（非 nginx 的 controller 要找對應設定）。
- **上傳大 PDF 413**：Ingress body size。
- **/api/health 不要當 probe**：它會真的呼叫模型。
- **備份**：只要備份 PVC（`/data`）；SQLite 建議用 `sqlite3 /data/app.db ".backup …"` 或停機時複製。

## 待填
- [ ] 映像倉庫（REGISTRY）
- [ ] Lantern 公開網域（LANTERN_HOST）
- [ ] IngressClass、TLS 方式（cert-manager？）
- [ ] StorageClass（若不是預設）
- [ ] 正式 Keycloak client ID
