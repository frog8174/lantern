"""單元測試：純函式，不打 API。"""
from __future__ import annotations

import pytest

from backend import features, llm, pdf_parse


# ---------------- <think> 過濾 ----------------
@pytest.mark.parametrize("chunks, expected", [
    (["<thi", "nk>想一想</th", "ink>\n\n答案"], "答案"),        # 標籤被切在串流片段中間
    (["沒有思考", "的回答"], "沒有思考的回答"),
    (["a < b 而且 <", "tag> 不是 think"], "a < b 而且 <tag> 不是 think"),  # 像標籤但不是
])
def test_think_stripper(chunks, expected):
    s = llm._ThinkStripper()
    out = "".join(s.feed(c) for c in chunks) + s.flush()
    assert out == expected


# ---------------- API 參數相容 ----------------
def test_build_default_sends_vllm_params():
    p = llm._build("m", [], True, (), {})
    assert p["extra_body"] == {"chat_template_kwargs": {"enable_thinking": False}}
    assert "max_tokens" in p and "temperature" in p


def test_build_adjustments():
    p = llm._build("m", [], True, ("no_template_kwargs", "max_completion_tokens", "no_temperature"),
                   {"max_tokens": 123})
    assert "extra_body" not in p and "temperature" not in p and "max_tokens" not in p
    assert p["max_completion_tokens"] == 123


# ---------------- PDF 解析 ----------------
def test_parse_numeric(pdfs):
    p = pdf_parse.parse_pdf(str(pdfs["numeric"]))
    assert p.title == "Sparse Lantern Networks for Document Reading"
    assert p.abstract.startswith("We present sparse lantern networks")
    assert [o["title"] for o in p.outline][:3] == ["1 Introduction", "2 Method", "3 Conclusion"]
    assert set(p.references) == {"1", "2", "3", "4"}
    assert "Attention is all you need" in p.references["4"]
    assert p.scanned_pages == []


def test_parse_author_year(pdfs):
    p = pdf_parse.parse_pdf(str(pdfs["authoryear"]))
    assert p.title == "Contextual Lanterns for Reading"
    assert len(p.references) == 4  # 懸掛縮排切出 4 筆，續行有接回去
    k = pdf_parse.match_author_year(p.references, "Peters", "2018b")
    assert "Dissecting contextual word embeddings" in p.references[k]
    k = pdf_parse.match_author_year(p.references, "Peters", "2018a")
    assert "Deep contextualized" in p.references[k]
    assert pdf_parse.match_author_year(p.references, "Nobody", "2018") is None


def test_scanned_detection(pdfs):
    assert pdf_parse.parse_pdf(str(pdfs["scanned"])).scanned_pages == [0, 1, 2]


def test_find_figures(pdfs):
    figs = {(f["kind"], f["num"]): f for f in pdf_parse.find_figures(str(pdfs["numeric"]))}
    assert set(figs) == {("figure", "1"), ("table", "1")}
    x0, y0, x1, y1 = figs[("figure", "1")]["bbox"]
    assert x0 < 120 / 612 and x1 > 500 / 612  # 圖說比圖窄，三個方塊仍要全部框進來
    assert y0 < 230 / 792 and y1 > 330 / 792  # 圖在上、圖說在下
    _, ty0, _, ty1 = figs[("table", "1")]["bbox"]
    assert ty0 < 400 / 792 and 500 / 792 < ty1 < 520 / 792  # 到最後一條框線為止，不多吃


def test_page_blocks_and_render(pdfs):
    blocks = pdf_parse.page_blocks(str(pdfs["numeric"]), 0)
    assert blocks and all(0 <= v <= 1 for b in blocks for v in b.bbox)
    png = pdf_parse.render_page_png(str(pdfs["numeric"]), 1, 72, [0.1, 0.1, 0.5, 0.5])
    assert png[:8] == b"\x89PNG\r\n\x1a\n"


def test_find_text_rects(pdfs):
    rects = pdf_parse.find_text_rects(str(pdfs["numeric"]), 0, "Prior work on reading assistants")
    assert rects and all(0 <= v <= 1 for r in rects for v in r)


@pytest.mark.parametrize("text, ok", [
    ("We propose a new method for reading.", True),
    ("12", False),
    ("$x^2$", False),
])
def test_translatable(text, ok):
    assert features._translatable(text) is ok


def test_citing_contexts(pdfs):
    p = pdf_parse.parse_pdf(str(pdfs["numeric"]))
    paper = {"meta": {"pages": p.pages}}
    one = features.citing_contexts(paper, "1", p.references["1"])
    assert one and one[0].startswith("[p.1]") and "[1]" in one[0]
    three = features.citing_contexts(paper, "3", p.references["3"])  # 落在 [2, 3] 裡
    assert three and "[2, 3]" in three[0]
    assert features.citing_contexts(paper, "4", p.references["4"]) == []  # 正文沒引用 [4]
