"""檢索（Retrieval）：問問題時，從論文裡找出最相關的幾段給 LLM 看。

這就是 RAG（Retrieval-Augmented Generation，檢索增強生成）：
  1. 切塊（chunking）：把論文切成 ~800 字元的段落，記住它在第幾頁
  2. 建索引：每段算一個向量（embedding），或用 BM25 關鍵字統計
  3. 查詢：問題也轉向量 → 算相似度 → 取前 k 段
  4. 把這 k 段連同頁碼塞進 prompt，要求模型回答時標註 [p.X]

短論文其實可以整篇塞進 context（見 features.paper_context），
RAG 主要是為了長論文 / 小 context 的本地模型。
"""
from __future__ import annotations

import math
import re
from collections import Counter

import numpy as np

from . import config, db, llm
from .pdf_parse import Block, _is_ref_head

CHUNK_CHARS = 800
CANDIDATES = 30  # 有 reranker 時先粗撈幾段再重排
# 參考文獻後面接的附錄標題（Appendix、A Proofs、A.1 Setup）：從這裡起又是正文
_APPENDIX_RE = re.compile(r"^\s*(appendix|appendices|supplementary|[A-H](\.\d+)*\.?\s+[A-Z][a-z])", re.I)


def _pieces(text: str) -> list[str]:
    """太長的單一區塊依句子切到 CHUNK_CHARS 以內（實測 19% 的段落超標，最長 4763 字元）。"""
    if len(text) <= CHUNK_CHARS:
        return [text]
    out, cur = [], ""
    for sent in re.split(r"(?<=[.!?。！？])\s+|(?<=[。！？])", text):
        if cur and len(cur) + len(sent) + 1 > CHUNK_CHARS:
            out.append(cur)
            cur = ""
        cur = f"{cur} {sent}" if cur else sent
        while len(cur) > CHUNK_CHARS:  # 一句就超長（表格、公式）：硬切
            out.append(cur[:CHUNK_CHARS])
            cur = cur[CHUNK_CHARS:]
    return out + [cur] if cur else out


def make_chunks(blocks: list[Block]) -> list[dict]:
    """相鄰、同頁的 block 合併到大約 CHUNK_CHARS 字元；單一 block 太長就切開。"""
    chunks: list[dict] = []
    cur: dict | None = None
    for b in blocks:
        if len(b.text) < 3:
            continue
        # 參考文獻、附錄標題一定開新段，search 才認得出參考文獻區
        head = _is_ref_head(b.text) or (len(b.text) < 80 and _APPENDIX_RE.match(b.text))
        for i, text in enumerate(_pieces(b.text)):
            if cur and not (head and i == 0) and cur["page"] == b.page and len(cur["text"]) + len(text) < CHUNK_CHARS:
                cur["text"] += " " + text
                cur["bbox"].append(b.bbox)
            else:
                if cur:
                    chunks.append(cur)
                cur = {"page": b.page, "text": text, "bbox": [b.bbox]}
    if cur:
        chunks.append(cur)
    return chunks


async def build_index(pid: str, blocks: list[Block]) -> int:
    chunks = make_chunks(blocks)
    try:
        vecs = await llm.embed([c["text"] for c in chunks])
    except Exception as e:  # embedding 服務掛了不能讓上傳失敗：先只用關鍵字，之後 reindex 補向量
        print(f"[retrieval] embed failed, BM25 only: {type(e).__name__}: {e}")
        vecs = None
    if vecs:
        for c, v in zip(chunks, vecs):
            arr = np.asarray(v, dtype=np.float32)
            c["emb"] = (arr / (np.linalg.norm(arr) + 1e-9)).tobytes()  # 先正規化，之後內積 = cosine
        # 記下是哪個模型算的：換了 embedding 模型，舊向量就不能跟新的問題向量比
        db.cache_set(pid, "embed_model", config.EMBED_MODEL)
    db.save_chunks(pid, chunks)
    return len(chunks)


_TOKEN_RE = re.compile(r"[A-Za-z0-9]+|[一-鿿]")


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


def _bm25(query: str, docs: list[str], k1: float = 1.5, b: float = 0.75) -> list[float]:
    """BM25：經典關鍵字排序法。詞在這段出現越多、在全部段落越稀有，分數越高。"""
    toks = [_tokens(d) for d in docs]
    avgdl = sum(map(len, toks)) / max(1, len(toks))
    df = Counter(t for ts in toks for t in set(ts))
    n = len(docs)
    q = _tokens(query)
    scores = []
    for ts in toks:
        tf = Counter(ts)
        s = 0.0
        for t in q:
            if t not in tf:
                continue
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            s += idf * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(ts) / avgdl))
        scores.append(s)
    return scores


def _not_refs(chunks: list[dict]) -> list[dict]:
    """拿掉參考文獻區（最後一個參考文獻標題到下一個附錄標題）：一堆專有名詞，常把檢索帶偏。"""
    start = max((i for i, c in enumerate(chunks) if _is_ref_head(c["text"].split(" ", 1)[0])), default=None)
    if start is None:
        return chunks
    end = next((i for i in range(start + 1, len(chunks)) if _APPENDIX_RE.match(chunks[i]["text"][:80])), len(chunks))
    return chunks[:start] + chunks[end:]


_CJK_RE = re.compile(r"[一-鿿]")
_english_cache: dict[str, str] = {}


async def english_query(q: str) -> str:
    """中文問題先改寫成英文檢索詞：論文是英文，BM25 和 reranker 對英文問題準很多（中文 0.1 vs 英文 0.9）。"""
    if not _CJK_RE.search(q) or config.LLM_MOCK:
        return q
    if q not in _english_cache:  # Wiki 問答會對每篇來源論文各查一次，同一題只改寫一次
        try:
            en = await llm.complete([{"role": "user", "content":
                "Rewrite this question about a research paper as a concise English search query. "
                "Keep technical terms; leave out generic words like 'paper' or 'authors'. "
                f"Output only the query.\n\n{q}"}], task="query", max_tokens=200)
        except Exception as e:  # 改寫失敗就用原句，bge-m3 本來就跨語言
            print(f"[retrieval] query rewrite failed: {type(e).__name__}: {e}")
            return q
        if len(_english_cache) > 500:
            _english_cache.clear()
        _english_cache[q] = en or q
    return _english_cache[q]


async def search(pid: str, query: str, k: int = 6) -> list[dict]:
    chunks = _not_refs(db.load_chunks(pid))
    if not chunks:
        return []
    query = await english_query(query)
    texts = [c["text"] for c in chunks]
    kw = np.asarray(_bm25(query, texts))
    if kw.max() > 0:
        kw = kw / kw.max()

    score = kw
    # 向量是目前這個 embedding 模型算的才用；換過模型的舊論文退回 BM25（重新匯入即可重建向量）
    same_model = db.cache_get(pid, "embed_model") == config.EMBED_MODEL
    if chunks[0]["emb"] is not None and same_model:
        qv = await llm.embed([query])
        if qv:
            q = np.asarray(qv[0], dtype=np.float32)
            q /= np.linalg.norm(q) + 1e-9
            mat = np.stack([np.frombuffer(c["emb"], dtype=np.float32) for c in chunks])
            if mat.shape[1] == q.shape[0]:
                sem = mat @ q
                # 混合檢索：語意相似度為主，關鍵字補強（專有名詞、公式符號很有用）
                score = 0.7 * sem + 0.3 * kw

    top = [i for i in np.argsort(-score)[:CANDIDATES if config.RERANK_MODEL else k] if score[i] > 0]
    try:
        rr = await llm.rerank(query, [texts[i] for i in top])
    except Exception as e:  # reranker 掛了退回混合分數，聊天照常
        print(f"[retrieval] rerank failed: {type(e).__name__}: {e}")
        rr = None
    if rr:  # 用名次不用門檻：中文問題的 reranker 分數普遍偏低，但順序是對的
        top = [i for _, i in sorted(zip(rr, top), key=lambda x: -x[0])]
        score = np.zeros(len(chunks))
        score[top] = rr
    hits = [chunks[i] | {"score": float(score[i])} for i in top[:k]]
    return sorted(hits, key=lambda c: (c["page"], c["idx"]))  # 照閱讀順序排，模型比較好理解
