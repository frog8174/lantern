"""逐句對應：切句、動態規劃配對、/align-map 端點（LaBSE 用假向量代替）。"""
from __future__ import annotations

import numpy as np

from backend import config, db, sentalign
from tests.test_align import P, _translated_block


def _cut(text, spans):
    return [text[s:e] for s, e in spans]


def test_split_en_keeps_abbreviations_and_offsets():
    t = ("We follow He et al. and use ResNet (Fig. 2), e.g. on COCO.  Accuracy rose to 28.4 points! "
         "Why? See Eq. 3 vs. Eq. 4. Prof. J. Smith agrees.")
    assert _cut(t, sentalign.split_en(t)) == [
        "We follow He et al. and use ResNet (Fig. 2), e.g. on COCO.",
        "Accuracy rose to 28.4 points!",
        "Why?",
        "See Eq. 3 vs. Eq. 4.",
        "Prof. J. Smith agrees.",
    ]


def test_split_zh():
    t = "我們提出新方法。效果如何？很好！其一；其二; 最後一句沒有句號"
    assert _cut(t, sentalign.split_zh(t)) == ["我們提出新方法。", "效果如何？", "很好！", "其一；", "其二;", "最後一句沒有句號"]


def _sim_from(table):
    """table[(i0,i1,j0,j1)] = 餘弦；沒列的當成不相干（0.1）。"""
    return lambda i0, i1, j0, j1: table.get((i0, i1, j0, j1), 0.1)


def test_dp_one_to_one():
    t = {(i, i + 1, i, i + 1): 0.9 for i in range(3)}
    assert [p[:4] for p in sentalign.align_dp(3, 3, _sim_from(t))] == [(0, 1, 0, 1), (1, 2, 1, 2), (2, 3, 2, 3)]


def test_dp_merge_and_skip():
    # 英文 0 被譯成中文 0、1 兩句；英文 1 譯文裡沒有（跳過）；英文 2 ↔ 中文 2
    t = {(0, 1, 0, 2): 0.88, (0, 1, 0, 1): 0.62, (0, 1, 1, 2): 0.58, (2, 3, 2, 3): 0.9, (1, 2, 2, 3): 0.3}
    assert [p[:4] for p in sentalign.align_dp(3, 3, _sim_from(t))] == [(0, 1, 0, 2), (2, 3, 2, 3)]
    # 2-1：兩句英文併成一句中文
    t = {(0, 2, 0, 1): 0.85, (0, 1, 0, 1): 0.6}
    assert [p[:4] for p in sentalign.align_dp(2, 1, _sim_from(t))] == [(0, 2, 0, 1)]


def _fake_embed(monkeypatch, calls):
    async def embed(texts):
        calls.append(len(texts))
        return np.ones((len(texts), 4), dtype=np.float32) / 2  # 全部一樣：每對都 1.0
    monkeypatch.setattr(sentalign, "_embed", embed)
    monkeypatch.setattr(config, "ALIGN_EMBED_URL", "http://labse.test/v1")


def test_align_map_endpoint(papers, client, bob, monkeypatch):
    pid = papers["numeric"]["id"]
    i, b = _translated_block(client, pid)
    url = f"/api/papers/{pid}/align-map?page={P}"
    assert client.get(url).json() == {"blocks": {}}  # 沒設定 LaBSE：空的

    calls = []
    _fake_embed(monkeypatch, calls)
    db.cache_set(pid, "align_map", None, str(P))  # 清掉翻譯時可能在背景算好的
    m = client.get(url).json()["blocks"]
    pairs = m[str(i)]
    assert pairs and calls == [calls[0]]
    for p in pairs:
        assert 0 <= p["en"][0] < p["en"][1] <= len(b["text"]) and 0 <= p["zh"][0] < p["zh"][1] <= len(b["tr"])
        assert p["rects"] and all(len(r) == 4 for r in p["rects"])
    assert client.get(url).json()["blocks"] == m and len(calls) == 1  # 第二次走快取
    assert bob.get(url).status_code == 404

    # 譯文變了 → 雜湊不同 → 重算
    blocks = db.cache_get(pid, "block_translation", str(P))
    old = blocks[i]["tr"]
    blocks[i]["tr"] = old + "補一句。"
    db.cache_set(pid, "block_translation", blocks, str(P))
    try:
        assert client.get(url).json()["blocks"][str(i)] and len(calls) == 2
    finally:
        blocks[i]["tr"] = old
        db.cache_set(pid, "block_translation", blocks, str(P))


def test_align_map_endpoint_failure_is_empty(papers, client, monkeypatch):
    pid = papers["numeric"]["id"]
    _translated_block(client, pid)
    monkeypatch.setattr(config, "ALIGN_EMBED_URL", "http://labse.test/v1")

    async def boom(texts):
        raise RuntimeError("down")
    monkeypatch.setattr(sentalign, "_embed", boom)
    db.cache_set(pid, "align_map", None, str(P))
    assert client.get(f"/api/papers/{pid}/align-map?page={P}").json() == {"blocks": {}}
    assert db.cache_get(pid, "align_map", str(P)) is None  # 失敗不快取
    assert client.get(f"/api/papers/{pid}/align-map?page=999").json() == {"blocks": {}}  # 沒翻過的頁
