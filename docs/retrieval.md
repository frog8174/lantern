# 論文聊天的檢索服務：bge-m3 ＋ reranker

長論文聊天不送全文時，`backend/retrieval.py` 會挑出相關段落再送給模型。原本只有關鍵字（BM25），中文問題對英文論文幾乎對不到；這兩個服務補上跨語言的語意檢索：

| 服務 | 模型 | 用途 | 端點 |
|---|---|---|---|
| `bge-m3` | `BAAI/bge-m3`（1024 維） | 段落與問題轉向量，算相似度粗撈 | `/v1/embeddings`，模型名 `bge-m3` |
| `bge-reranker` | `BAAI/bge-reranker-v2-m3` | 粗撈的候選段落逐一和問題比對、重新排序 | `/v1/rerank`，模型名 `bge-reranker` |

## 部署（`deploy/k8s-retrieval/`）
跟 LaBSE 同一套做法（docs/labse.md）：vLLM `v0.28.0`、節點 `toolmen-server3`、第一張卡、同 namespace `aaron-personal`，**共用 Secret `labse-secrets` 的 `VLLM_API_KEY`**（不用再建 Secret）。新的 PVC `hf-cache-retrieval` 15Gi 給兩個模型共用。

1. `kubectl apply -k deploy/k8s-retrieval`；第一次啟動各要下載約 2.3 GB。
2. `kubectl -n aaron-personal get pods -l 'app in (bge-m3,bge-reranker)' -w` 等到 Ready。
3. 驗證（金鑰從環境變數讀）：
   ```bash
   VLLM_API_KEY=... uv run python deploy/k8s-retrieval/check_retrieval.py
   ```
   印出 `OK` 表示中文問題能找到對的英文段落、reranker 也把它排第一。

## 要注意
- **顯存**：bge-m3 設 `--gpu-memory-utilization 0.03`、reranker 設 0.08，和 LaBSE 的 0.03 加起來約 14%，同卡上的其他服務要留得下；卡比較小或啟動時報顯存不足就調高。
- **`--max-model-len 8192`**（兩個模型的上限）：段落約 800 字元，但中文論文一個字約一個 token，加上偶爾有很長的單一區塊，1024 會不夠（實際遇過 400 錯誤）。
- **網域**：Ingress 用 `lantern-bge.` / `lantern-reranker.toolmen.bime.ntu.edu.tw`，跟 LaBSE 一樣走 traefik-private，只給本機開發用；Lantern 正式環境走叢集內位址。

## Lantern 端設定
| 變數 | 本機 `.env` | 正式（k8s） |
|---|---|---|
| `EMBED_BASE_URL` | `https://lantern-bge.toolmen.bime.ntu.edu.tw/v1` | ConfigMap：`http://bge-m3.aaron-personal.svc.cluster.local:8000/v1` |
| `EMBED_MODEL` | `bge-m3` | ConfigMap：`bge-m3` |
| `EMBED_API_KEY` | 同 `VLLM_API_KEY` | Secret `lantern-secrets` |
| `RERANK_BASE_URL` | `https://lantern-reranker.toolmen.bime.ntu.edu.tw/v1` | ConfigMap：`http://bge-reranker.aaron-personal.svc.cluster.local:8000/v1` |
| `RERANK_MODEL` | `bge-reranker` | ConfigMap：`bge-reranker` |
| `RERANK_API_KEY` | 不設＝沿用 `EMBED_API_KEY` | 同左 |
| `LLM_MODEL_QUERY` | `anthropic:claude-haiku-5-5` | ConfigMap |

## 查詢流程（`retrieval.search()`）
1. 拿掉參考文獻區：從最後一個「References」標題開始，到下一個附錄標題為止。切段時這兩種標題一定會開新段。
2. 中文問題先用 `query` 模型（Haiku）改寫成英文。同一題只改寫一次，失敗就用原句。
3. 用 bge-m3 和 BM25 算混合分數，取前 30 段。
4. 用 reranker 重排，取前 k 段。**依名次，不設分數門檻**：中文問題的分數普遍偏低，但順序是對的。

容錯：
- reranker 掛了：退回混合分數。
- embedding 服務掛了：上傳照常，只建關鍵字索引。

## 重建索引
設好或換了 `EMBED_MODEL` 之後，執行 `uv run python -m backend.reindex`。
- 先備份 `data/app.db`。
- 一般論文會重新解析 PDF。
- 掃描版論文會用現有段落重算向量，保留 OCR 文字。
