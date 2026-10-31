"""引用格式化（backend/cite.py）單元測試。"""
from __future__ import annotations

from backend import cite
from backend.features import _bib

A, B, C = ({"given": "Ashish", "family": "Vaswani"}, {"given": "Noam M.", "family": "Shazeer"},
           {"given": "Jean-Paul", "family": "Sartre"})
FULL = _bib(title="Attention Is All You Need", authors=[A, B, C], year=2017, venue="Neural Computation",
            volume="30", issue="4", pages="100-110", doi="https://doi.org/10.1000/xyz")


def test_multiple_authors():
    s = cite.styles(FULL)
    assert s["apa"] == ("Vaswani, A., Shazeer, N. M., & Sartre, J.-P. (2017). Attention Is All You Need. "
                        "Neural Computation, 30(4), 100–110. https://doi.org/10.1000/xyz")
    assert s["ieee"] == ('A. Vaswani, N. M. Shazeer, and J.-P. Sartre, "Attention Is All You Need," '
                         "Neural Computation, vol. 30, no. 4, pp. 100–110, 2017, doi: 10.1000/xyz.")
    assert s["mla"] == ('Vaswani, Ashish, et al. "Attention Is All You Need." '
                        "Neural Computation, vol. 30, no. 4, 2017, pp. 100–110.")
    assert s["bibtex"].startswith("@article{vaswani2017attention,\n")
    assert "author = {Vaswani, Ashish and Shazeer, Noam M. and Sartre, Jean-Paul}" in s["bibtex"]
    assert "pages = {100--110}" in s["bibtex"] and "doi = {10.1000/xyz}" in s["bibtex"]


def test_two_and_single_author():
    two = _bib(title="T", authors=[A, B], year=2020)
    assert cite.apa(two).startswith("Vaswani, A., & Shazeer, N. M. (2020).")
    assert cite.ieee(two).startswith("A. Vaswani and N. M. Shazeer, ")
    assert cite.mla(two).startswith("Vaswani, Ashish, and Noam M. Shazeer. ")
    one = _bib(title="Solo Work", authors=[A], year=2021, venue="J")
    assert cite.apa(one) == "Vaswani, A. (2021). Solo Work. J."
    assert cite.ieee(one) == 'A. Vaswani, "Solo Work," J, 2021.'
    assert cite.mla(one) == 'Vaswani, Ashish. "Solo Work." J, 2021.'


def test_missing_fields_no_dangling_punctuation():
    bare = _bib(title="Only a Title?")
    assert cite.apa(bare) == "Only a Title?"
    assert cite.ieee(bare) == '"Only a Title?"'
    assert cite.mla(bare) == '"Only a Title?"'
    assert cite.bibtex(bare) == "@misc{only,\n  title = {Only a Title?}\n}"
    no_title = _bib(authors=[A], year=2019)
    assert cite.apa(no_title) == "Vaswani, A. (2019)."
    assert cite.ieee(no_title) == "A. Vaswani, 2019."
    assert cite.mla(no_title) == "Vaswani, Ashish. 2019."
    empty = _bib()
    assert cite.styles(empty) == {"apa": "", "ieee": "", "mla": "", "bibtex": "@misc{paper}"}
    for s in cite.styles(_bib(title="X", authors=[A], venue="V", pages="5")).values():
        assert ",," not in s and ", ." not in s and "()" not in s


def test_arxiv_preprint():
    b = _bib(title="A Preprint", authors=[A], year=2023, arxiv="2301.00001", url="https://arxiv.org/abs/2301.00001")
    bt = cite.bibtex(b)
    assert bt.startswith("@misc{vaswani2023preprint,")
    assert "eprint = {2301.00001}" in bt and "archivePrefix = {arXiv}" in bt and "journal" not in bt
    assert cite.apa(b) == ("Vaswani, A. (2023). A Preprint. arXiv preprint arXiv:2301.00001. "
                           "https://arxiv.org/abs/2301.00001")


def test_apa_over_20_authors():
    many = [{"given": "G", "family": f"F{i}"} for i in range(25)]
    s = cite.apa(_bib(title="T", authors=many))
    assert "F18, G., … F24, G. T." in s and "F19" not in s and "&" not in s


def test_doi_forms():
    for d in ("10.1/abc", "doi:10.1/abc", "https://dx.doi.org/10.1/abc"):
        b = _bib(title="T", doi=d)
        assert cite.apa(b).endswith("https://doi.org/10.1/abc")
        assert cite.ieee(b) == '"T," doi: 10.1/abc.'
