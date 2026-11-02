"""驗證 bge-m3 和 reranker：中文問題要能找到對的英文段落。
用法：VLLM_API_KEY=<labse-secrets 那把> uv run python deploy/k8s-retrieval/check_retrieval.py [網域後綴]
金鑰只從環境變數讀，不印出來。"""
import json
import math
import os
import sys
import urllib.request

SUFFIX = sys.argv[1] if len(sys.argv) > 1 else "toolmen.bime.ntu.edu.tw"
KEY = os.environ["VLLM_API_KEY"]
Q = "這篇論文的損失函數是怎麼設計的？"
DOCS = [
    "We train the model with a contrastive loss that pulls matched image-text pairs together "
    "and pushes mismatched pairs apart, plus an auxiliary reconstruction term weighted by 0.1.",
    "The dataset contains 1.2 million images collected from public sources between 2018 and 2021.",
    "We thank the anonymous reviewers for their helpful comments.",
]


def post(host: str, path: str, body: dict) -> dict:
    req = urllib.request.Request(f"https://{host}.{SUFFIX}/v1/{path}", json.dumps(body).encode(),
                                 {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))


vecs = [d["embedding"] for d in post("lantern-bge", "embeddings", {"model": "bge-m3", "input": [Q, *DOCS]})["data"]]
sims = [cos(vecs[0], v) for v in vecs[1:]]
print("bge-m3   dim", len(vecs[0]), "cosine", [round(s, 3) for s in sims])
assert len(vecs[0]) == 1024 and sims[0] == max(sims), "bge-m3：損失函數那段應該最相似"

res = post("lantern-reranker", "rerank", {"model": "bge-reranker", "query": Q, "documents": DOCS})["results"]
order = [r["index"] for r in res]
print("reranker order", order, "scores", [round(r["relevance_score"], 3) for r in res])
assert order[0] == 0, "reranker：損失函數那段應該排第一"
print("OK")
