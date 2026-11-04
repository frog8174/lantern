# 部署到 k8s

檔案：`Dockerfile`、`.dockerignore`、`deploy/k8s/`（kustomize）。登入設計見 `docs/auth.md`。

## 架構
```
Ingress（Traefik，TLS）
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

## 2. Keycloak client（沿用 `lantern-local`）
在 client `lantern-local` 的設定**加上**正式網域（本機的那幾行保留）：
- Valid redirect URIs：加 `https://lantern.toolmen.bime.ntu.edu.tw/api/auth/callback`
- Valid post logout redirect URIs：加 `https://lantern.toolmen.bime.ntu.edu.tw/`
- Web origins：加 `https://lantern.toolmen.bime.ntu.edu.tw`
- 上線前建議把 Advanced 分頁的 PKCE Method 設成 **S256**（強制 PKCE；Lantern 本來就會帶）。
- 正式和本機共用同一把 client secret：本機 `.env` 的 `OIDC_CLIENT_SECRET` 就是 Secret 要放的那一把。

## 3. Secret（不要 commit）
```bash
kubectl create namespace lantern
kubectl -n lantern create secret generic lantern-secrets \
  --from-literal=OIDC_CLIENT_SECRET='…' \
  --from-literal=SESSION_SECRET="$(python -c 'import secrets;print(secrets.token_urlsafe(48))')" \
  --from-literal=ANTHROPIC_API_KEY='…'   --from-literal=ALIGN_EMBED_API_KEY='…'   # LaBSE 的 VLLM_API_KEY（docs/labse.md）；沒有就拿掉，逐句對應退回問 LLM
  # --from-literal=EMBED_API_KEY='…'     # bge-m3／reranker 的 VLLM_API_KEY（同一把，docs/retrieval.md）
  # 本機有設 SEMANTIC_SCHOLAR_API_KEY 的話也加上（沒有 key 時 Semantic Scholar 常被限流）
```

## 4. 設定與套用
1. `deploy/k8s/configmap.yaml`：已填好（網域、client、與本機相同的模型設定）。
2. `deploy/k8s/ingress.yaml`：已填好（Traefik、cert-manager-prod）；確認 `ingressClassName` 與 `kubectl get ingressclass` 一致。
3. `deploy/k8s/pvc.yaml`：已填 `rook-ceph-hdd-block`。
4. 套用：`kubectl apply -k deploy/k8s`
5. 驗證：
   ```bash
   kubectl -n lantern rollout status deploy/lantern
   kubectl -n lantern logs deploy/lantern
   curl https://lantern.toolmen.bime.ntu.edu.tw/api/livez        # {"ok": true}
   ```
   然後瀏覽器開 `https://lantern.toolmen.bime.ntu.edu.tw` 登入一次。

## Traefik
Ingress 這層不用額外設定：上傳大小預設無上限、SSE 預設即時轉送不緩衝、回應預設沒有寫入逾時。
要和叢集管理者確認的是 Traefik 的 **entrypoint 靜態設定**（Helm values 的 `ports.websecure.transport`／`additionalArguments`）：
- `respondingTimeouts.readTimeout`：Traefik v3 預設 **60 秒**，指的是「讀完整個請求」的時間。上傳 150 MB 的 PDF 在慢網路可能超過 → 建議 `--entryPoints.websecure.transport.respondingTimeouts.readTimeout=600s`。
- `respondingTimeouts.idleTimeout`：預設 180 秒，只影響閒置的 keep-alive 連線，SSE 串流持續有資料不受影響。
- HTTP 轉 HTTPS：通常已在 `web` entrypoint 設好 redirect；沒有的話加 `--entryPoints.web.http.redirections.entryPoint.to=websecure`。
- Traefik 會送 `X-Forwarded-Proto`，映像的 uvicorn 已開 `--proxy-headers`，登入的 redirect URI 會是 https。

## 常見問題
- **登入後 redirect_uri 不符**：`PUBLIC_BASE_URL` 要和 Ingress host 完全一致（含 https）；Keycloak client 的 redirect URI 也要一致。
- **Pod 連不到 Keycloak 公開網域**（叢集 hairpin）：在 Pod 裡 `curl https://keycloak…/realms/…/.well-known/openid-configuration` 測；不通時要加叢集內位址的設定（docs/auth.md 的 `OIDC_INTERNAL_URL`，目前未實作，需要時再做）。
- **SSE 字一次全跳出來**：中間有東西在緩衝。Traefik 預設不會；檢查是否另外掛了 Buffering middleware 或前面還有一層代理／CDN。
- **上傳大 PDF 失敗**：多半是 Traefik `readTimeout`（見上）或另外掛的 Buffering middleware 的 `maxRequestBodyBytes`。
- **/api/health 不要當 probe**：它會真的呼叫模型。
- **備份**：只要備份 PVC（`/data`）；SQLite 建議用 `sqlite3 /data/app.db ".backup …"` 或停機時複製。

## 待填
- [ ] 映像倉庫（`kustomization.yaml` 的 `REGISTRY`）
- [ ] Keycloak `lantern-local` 加上正式網域的 redirect URI（見第 2 步）
- [ ] 確認 IngressClass 名稱是 `traefik`、ClusterIssuer 名稱是 `cert-manager-prod`
- [ ] Traefik `websecure` 的 `readTimeout` 是否要拉長（大檔上傳）
- [x] 網域 lantern.toolmen.bime.ntu.edu.tw、StorageClass rook-ceph-hdd-block、TLS cert-manager-prod

## 本機驗證（2026-11-01）
- `docker build -t lantern:0.1.0 .`：成功，映像約 757 MB。
- 以 k8s 相同限制執行（唯讀根目錄、uid 10001、drop ALL、只有 /data 與 /tmp 可寫）：首頁、薛西弗斯素材、dev 登入、上傳並解析 22 頁 PDF、縮圖都正常；寫入 /app 被拒（唯讀生效）。
- OIDC 正式設定 + `X-Forwarded-Proto: https`：登入導向的 redirect_uri 為 `https://lantern.toolmen.bime.ntu.edu.tw/api/auth/callback`，session cookie 帶 secure、httponly、samesite=lax。
- `AUTH_MODE=oidc` 缺設定時拒絕啟動並說明缺哪些變數。
- 唯讀根目錄時 /data 一定要掛 volume（k8s 的 PVC）；一般 `docker run` 不掛 volume 也能啟動。
