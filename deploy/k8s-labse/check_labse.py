"""比對 vLLM 端點與 sentence-transformers 官方 LaBSE 的向量是否一致（LaBSE 有 Dense+Normalize 頭，vLLM 版本可能沒套到）。

用法：
  LABSE_URL=https://labse.toolmen.bime.ntu.edu.tw/v1 LABSE_API_KEY=... \
    uv run --no-project --with sentence-transformers python -I deploy/k8s-labse/check_labse.py
"""
import json
import os
import urllib.request

import numpy as np
from sentence_transformers import SentenceTransformer

PAIRS = [
    ("Experiments on two machine translation tasks show these models to be superior in quality.",
     "在兩項機器翻譯任務上的實驗顯示，這些模型在品質上更為優異。"),
    ("We propose a new simple network architecture, the Transformer.",
     "我們提出一種全新而簡單的網路架構——Transformer。"),
    ("Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task.",
     "我們的模型在 WMT 2014 英翻德任務上達到 28.4 BLEU。"),
]
texts = [t for p in PAIRS for t in p]

req = urllib.request.Request(
    os.environ["LABSE_URL"].rstrip("/") + "/embeddings",
    data=json.dumps({"model": "labse", "input": texts}).encode(),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {os.environ.get('LABSE_API_KEY', '')}"},
)
remote = np.array([d["embedding"] for d in json.load(urllib.request.urlopen(req))["data"]])
local = SentenceTransformer("sentence-transformers/LaBSE").encode(texts, normalize_embeddings=True)

norm = lambda m: m / np.linalg.norm(m, axis=1, keepdims=True)
same = (norm(remote) * norm(local)).sum(1)
print("同一句 vLLM 與官方的餘弦（應 > 0.99）：", np.round(same, 4))
sim = norm(remote) @ norm(remote).T
print("對照句相似度（英↔中，應明顯高於錯配）：")
for i in range(len(PAIRS)):
    print(f"  第 {i + 1} 對：對的 {sim[2 * i, 2 * i + 1]:.3f}，"
          f"錯配 {max(sim[2 * i, 2 * j + 1] for j in range(len(PAIRS)) if j != i):.3f}")
assert same.min() > 0.99, "vLLM 輸出和官方 LaBSE 不一致：多半是 Dense 頭沒套到，見 docs/labse.md 的備案"
print("OK")
