# LaBSE 句向量服務（中英逐句對齊）

Lantern 並排對照的逐句對應：翻完一頁就把兩邊切句、向 LaBSE 要向量，用餘弦相似度＋動態規劃配對，存成這頁的對應表；選字時查表即可。
LaBSE 是專為雙語對照句訓練的模型（Bertalign 的預設），比每次問 LLM 快、準、免 API 費。

## 部署（`deploy/k8s-labse/`）
| 項目 | 設定 |
|---|---|
| 伺服器 | vLLM `vllm/vllm-openai:v0.10.2`，`--runner pooling --convert embed`，OpenAI 相容 `/v1/embeddings`，模型名 `labse` |
| GPU | 節點用 `nodeSelector`（`kubernetes.io/hostname`），**第一張卡**用 `NVIDIA_VISIBLE_DEVICES=0` 直接掛（不向 device plugin 要 `nvidia.com/gpu`），顯存只拿 10% |
| 模型快取 | PVC `hf-cache` 10Gi（rook-ceph-hdd-block） |
| 叢集內位址 | `http://labse.embedding.svc.cluster.local:8000/v1`（Lantern 正式環境用這個） |
| 對外 | Ingress `labse.toolmen.bime.ntu.edu.tw`（traefik-private、cert-manager-prod），本機開發用；**一定要 API key** |

步驟：
1. `deployment.yaml` 的 `GPU_NODE` 改成 GPU 節點名稱；`ingress.yaml` 確認網域。
2. 叢集沒有 RuntimeClass `nvidia`（`kubectl get runtimeclass`）而 docker 預設 runtime 已是 nvidia 時，刪掉 `runtimeClassName` 那行。
3. 建 Secret：
   ```bash
   kubectl create namespace embedding
   kubectl -n embedding create secret generic labse-secrets \
     --from-literal=VLLM_API_KEY="$(python -c 'import secrets;print(secrets.token_urlsafe(32))')"
   ```
4. `kubectl apply -k deploy/k8s-labse`；第一次啟動要下載模型（約 1.9 GB），startup probe 給了 10 分鐘。
5. 驗證：
   ```bash
   curl -s https://labse.toolmen.bime.ntu.edu.tw/v1/embeddings \
     -H "Authorization: Bearer <key>" -H "Content-Type: application/json" \
     -d '{"model":"labse","input":["hello","你好"]}' | head -c 300
   ```
   再跑 `deploy/k8s-labse/check_labse.py` 比對官方 sentence-transformers 的輸出（餘弦應 > 0.99）。

## 要注意
- **「指定第一張卡」的代價**：沒有向 k8s 要 `nvidia.com/gpu`，排程器不知道這張卡被用了，別的工作仍可能排到同一張卡。LaBSE 很小，共用沒問題；若要獨占，改成 `resources.limits: {nvidia.com/gpu: 1}`（但就不能指定是哪一張）。
- **LaBSE 的 Dense 頭**：官方 LaBSE 是 CLS → Dense(tanh) → 正規化。不同版本的 vLLM 不一定會套 sentence-transformers 的 Dense 層；`check_labse.py` 不過時，備案是改用 HuggingFace Text Embeddings Inference（TEI）或換 vLLM 版本，Lantern 端不用改（同樣是 `/v1/embeddings`）。
- Lantern 端設定（之後實作）：`ALIGN_EMBED_URL`、`ALIGN_EMBED_MODEL=labse`、`ALIGN_EMBED_API_KEY`（Secret）。端點連不到時退回本機規則，再不行才問 LLM。
