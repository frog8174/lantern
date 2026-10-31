"""論文卡：備註、星號、標籤、複製引用（規格見 docs/paper-cards.md）。"""
from __future__ import annotations

from backend import config, features


def _row(client, pid):
    return next(p for p in client.get("/api/papers").json() if p["id"] == pid)


def test_patch_fields_independently(papers, client):
    pid = papers["numeric"]["id"]
    assert client.patch(f"/api/papers/{pid}", json={"tags": [" nlp ", "nlp", ""]}).json() == \
        {"tags": ["nlp"], "note": "", "starred": False}
    assert client.patch(f"/api/papers/{pid}", json={"note": "讀第三節"}).json() == \
        {"tags": ["nlp"], "note": "讀第三節", "starred": False}
    assert client.patch(f"/api/papers/{pid}", json={"starred": True}).json() == \
        {"tags": ["nlp"], "note": "讀第三節", "starred": True}
    row = _row(client, pid)
    assert (row["tags"], row["note"], row["starred"]) == (["nlp"], "讀第三節", True)
    client.patch(f"/api/papers/{pid}", json={"tags": [], "note": "", "starred": False})


def test_cite_cached_and_year(papers, client, monkeypatch):
    monkeypatch.setattr(config, "LLM_MOCK", True)  # 不打網路
    pid = papers["authoryear"]["id"]
    row = _row(client, pid)
    assert row["year"] is None and row["starred"] is False and row["note"] == ""
    calls = []
    real = features.fetch_bib

    async def counting(p):
        calls.append(p["id"])
        return await real(p)
    monkeypatch.setattr(features, "fetch_bib", counting)
    r1 = client.get(f"/api/papers/{pid}/cite").json()
    assert r1["bib"] == features.MOCK_BIB
    assert set(r1["styles"]) == {"apa", "ieee", "mla", "bibtex"}
    assert r1["styles"]["apa"].startswith("Lovelace, A., & Turing, A. (2024). MOCK Paper Title.")
    assert client.get(f"/api/papers/{pid}/cite").json() == r1
    assert calls == [pid]  # 第二次走快取
    assert _row(client, pid)["year"] == 2024


def test_cards_scoped_to_owner(papers, client, bob):
    pid = papers["numeric"]["id"]
    assert bob.patch(f"/api/papers/{pid}", json={"starred": True}).status_code == 404
    assert bob.get(f"/api/papers/{pid}/cite").status_code == 404
    assert _row(client, pid)["starred"] is False


def test_byline():
    from backend.db import byline
    assert byline({}) is None
    bib = {"authors": [{"given": "F", "family": "Chen"}, {"given": "M", "family": "Giuffrida"}, {"given": "S", "family": "Tsaftaris"}],
           "venue": "2023 IEEE/CVF International Conference on Computer Vision Workshops (ICCVW)", "year": 2023}
    assert byline(bib) == "Chen, Giuffrida, Tsaftaris，ICCVW 2023"
    bib["authors"].append({"family": "Lee"})
    assert byline(bib) == "Chen 等，ICCVW 2023"
    assert byline({"arxiv": "2401.01234", "year": 2024}) == "arXiv 2024"


def test_thumb(client, papers, bob):
    pid = papers["numeric"]["id"]
    r = client.get(f"/api/papers/{pid}/thumb.png")
    assert r.status_code == 200 and r.content[:4] == b"\x89PNG"
    assert bob.get(f"/api/papers/{pid}/thumb.png").status_code == 404
