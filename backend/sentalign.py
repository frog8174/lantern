"""逐句對應：切句 → LaBSE 句向量 → 動態規劃配對（Bertalign / Vecalign 的簡化版）。

對照翻譯每翻完一頁，算出這頁每個區塊「英文第幾個字到第幾個字 ↔ 譯文第幾個字到第幾個字」，
前端選字時查表就好，不用每次問 LLM。
"""
from __future__ import annotations

import re

import httpx
import numpy as np

from . import config

# 句點後面不算句尾的縮寫（比對時不分大小寫，去掉句點）
_ABBR = {"e.g", "i.e", "al", "fig", "figs", "eq", "eqs", "no", "nos", "vs", "cf", "sec", "ref", "refs",
         "tab", "approx", "resp", "dr", "mr", "ms", "prof", "vol", "pp", "ch", "app", "ca", "st"}
_EN_END = re.compile(r"[.?!][\"'”’)\]]*(?=\s+|$)")
_ZH_END = re.compile(r"[。！？；][」』”’）)]*|[;!?](?=\s|$)")


def _spans(text: str, cuts: list[int]) -> list[tuple[int, int]]:
    """依切點切段，去掉頭尾空白，回傳 (start, end) 字元位置。"""
    out, s = [], 0
    for e in cuts + [len(text)]:
        a, b = s, e
        while a < b and text[a].isspace():
            a += 1
        while b > a and text[b - 1].isspace():
            b -= 1
        if b > a:
            out.append((a, b))
        s = e
    return out


def split_en(text: str) -> list[tuple[int, int]]:
    cuts = []
    for m in _EN_END.finditer(text):
        word = re.search(r"(\S+)$", text[: m.start()])
        w = word.group(1).lower().lstrip("([\"'") if word else ""
        if m.group()[0] == "." and (w in _ABBR or w.endswith(("e.g", "i.e")) or (len(w) == 1 and w.isalpha())):
            continue  # e.g. / et al. / Fig. / 名字縮寫 "J."
        nxt = text[m.end():].lstrip()[:1]
        if nxt and nxt.islower():
            continue  # 下一句不會小寫開頭：多半是沒列到的縮寫
        cuts.append(m.end())
    return _spans(text, cuts)


def split_zh(text: str) -> list[tuple[int, int]]:
    return _spans(text, [m.end() for m in _ZH_END.finditer(text)])


# 1-1、1-2、2-1、1-0、0-1；合併的分數乘上涵蓋句數，才不會老是拆成 1-1 加跳過
_MOVES = ((1, 1), (1, 2), (2, 1), (1, 0), (0, 1))
MIN_SIM = 0.5  # 低於這個寧可跳過（實測真配對 0.79~0.93，配錯 ≤ 0.39）


def align_dp(n: int, m: int, sim) -> list[tuple[int, int, int, int, float]]:
    """sim(i0, i1, j0, j1) = 英文句 [i0, i1) 與中文句 [j0, j1) 的餘弦。
    回傳配對 (i0, i1, j0, j1, 餘弦)，依順序（單調）。跳過的句子不出現。"""
    best = np.full((n + 1, m + 1), -np.inf)
    back: dict[tuple[int, int], tuple[int, int, float]] = {}
    best[0, 0] = 0
    for i in range(n + 1):
        for j in range(m + 1):
            if best[i, j] == -np.inf:
                continue
            for di, dj in _MOVES:
                a, b = i + di, j + dj
                if a > n or b > m:
                    continue
                c = sim(i, a, j, b) if di and dj else 0.0
                gain = (c - MIN_SIM) * (di + dj) / 2 if di and dj else 0.0
                if best[i, j] + gain > best[a, b]:
                    best[a, b] = best[i, j] + gain
                    back[a, b] = (i, j, c)
    out, (i, j) = [], (n, m)
    while (i, j) != (0, 0):
        pi, pj, c = back[i, j]
        if i > pi and j > pj:
            out.append((pi, i, pj, j, c))
        i, j = pi, pj
    return out[::-1]


async def _embed(texts: list[str]) -> np.ndarray:
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(f"{config.ALIGN_EMBED_URL.rstrip('/')}/embeddings",
                              headers={"Authorization": f"Bearer {config.ALIGN_EMBED_API_KEY}"},
                              json={"model": config.ALIGN_EMBED_MODEL, "input": texts})
        r.raise_for_status()
    v = np.array([d["embedding"] for d in sorted(r.json()["data"], key=lambda d: d["index"])], dtype=np.float32)
    return v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)


async def page_map(blocks: list[dict]) -> dict[str, list[dict]]:
    """整頁一次送 embedding，逐區塊配對。回傳 {區塊序號: [{"en": [s,e], "zh": [s,e], "score"}]}。"""
    todo = [(k, split_en(b["text"]), split_zh(b["tr"])) for k, b in enumerate(blocks) if b.get("tr")]
    texts = []
    for k, en, zh in todo:
        # LaBSE 最多 256 token：英文約 4 字元一 token，中文約 1 字一 token
        texts += [blocks[k]["text"][s:e][:800] for s, e in en] + [blocks[k]["tr"][s:e][:250] for s, e in zh]
    if not texts:
        return {}
    vecs, at, out = await _embed(texts), 0, {}
    for k, en, zh in todo:
        E, Z = vecs[at: at + len(en)], vecs[at + len(en): at + len(en) + len(zh)]
        at += len(en) + len(zh)

        def sim(i0, i1, j0, j1, E=E, Z=Z):
            # shortcut: 合併句用向量相加近似「整段一起嵌入」，省一次請求；不準再改成真的嵌入合併句
            e, z = E[i0:i1].sum(0), Z[j0:j1].sum(0)
            return float(e @ z / (np.linalg.norm(e) * np.linalg.norm(z) + 1e-9))

        out[str(k)] = [{"en": [en[i0][0], en[i1 - 1][1]], "zh": [zh[j0][0], zh[j1 - 1][1]], "score": round(c, 3)}
                       for i0, i1, j0, j1, c in align_dp(len(en), len(zh), sim)]
    return out
