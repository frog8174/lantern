"""引用格式：APA 7、IEEE、MLA 9、BibTeX。純函式，輸入是 features.fetch_bib 的書目 dict（規格見 docs/paper-cards.md）。
缺的欄位整段略過，不留空殼標點。"""
from __future__ import annotations

import re

STOPWORDS = {"a", "an", "the", "on", "of", "in", "for", "to", "and", "with", "from", "by", "at", "is", "are",
             "towards", "toward", "via", "how", "what", "why", "do", "does", "can"}


def _end(s: str, ch: str = ".") -> str:
    """補上結尾標點，已有 .?! 就不重複。"""
    return s if s[-1:] in ".?!" else s + ch


def _initials(given: str | None) -> str:
    """'Jean-Paul Noam' → 'J.-P. N.'"""
    return " ".join("-".join(p[0] + "." for p in w.split("-") if p) for w in (given or "").replace(".", " ").split())


def _pages(b: dict) -> str:
    return re.sub(r"\s*-+\s*", "–", b.get("pages") or "")


def _doi(b: dict) -> str:
    return re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", b.get("doi") or "", flags=re.I)


def _venue(b: dict) -> str:
    return b.get("venue") or (f"arXiv preprint arXiv:{b['arxiv']}" if b.get("arxiv") else "")


def _and(names: list[str], comma_and: str = ", and ") -> str:
    if len(names) <= 2:
        return " and ".join(names)
    return ", ".join(names[:-1]) + comma_and + names[-1]


def apa(b: dict) -> str:
    names = [f"{a['family']}, {_initials(a.get('given'))}".rstrip(", ") for a in b.get("authors") or []]
    if len(names) > 20:
        authors = ", ".join(names[:19]) + ", … " + names[-1]
    elif len(names) > 1:
        authors = ", ".join(names[:-1]) + ", & " + names[-1]
    else:
        authors = "".join(names)
    vol = (b.get("volume") or "") + (f"({b['issue']})" if b.get("issue") else "")
    src = ", ".join(x for x in (_venue(b), vol, _pages(b)) if x)
    doi = _doi(b)
    segs = [_end(authors) if authors else "", f"({b['year']})." if b.get("year") else "",
            _end(b.get("title") or "") if b.get("title") else "", _end(src) if src else "",
            f"https://doi.org/{doi}" if doi else (b.get("url") or "")]
    return " ".join(s for s in segs if s)


def ieee(b: dict) -> str:
    authors = _and([f"{_initials(a.get('given'))} {a['family']}".strip() for a in b.get("authors") or []])
    rest = [x for x in (_venue(b), b.get("volume") and f"vol. {b['volume']}", b.get("issue") and f"no. {b['issue']}",
                        _pages(b) and f"pp. {_pages(b)}", b.get("year") and str(b["year"]),
                        _doi(b) and f"doi: {_doi(b)}") if x]
    out, title = authors, b.get("title")
    if title:  # 標題放引號裡，後面的逗號/句號也在引號內
        out = (out + ", " if out else "") + '"' + _end(title, "," if rest else ".") + '"'
    if rest:
        out = (out + (" " if title else ", ") if out else "") + _end(", ".join(rest))
    return out if title or not out else _end(out)


def mla(b: dict) -> str:
    au = b.get("authors") or []

    def inv(a):  # 第一位作者姓在前
        return f"{a['family']}, {a['given']}" if a.get("given") else a["family"]

    def norm(a):
        return f"{a['given']} {a['family']}" if a.get("given") else a["family"]
    if len(au) >= 3:
        authors = inv(au[0]) + ", et al"
    elif len(au) == 2:
        authors = f"{inv(au[0])}, and {norm(au[1])}"
    else:
        authors = inv(au[0]) if au else ""
    rest = [x for x in (_venue(b), b.get("volume") and f"vol. {b['volume']}", b.get("issue") and f"no. {b['issue']}",
                        b.get("year") and str(b["year"]), _pages(b) and f"pp. {_pages(b)}") if x]
    segs = [_end(authors) if authors else "", '"' + _end(b["title"]) + '"' if b.get("title") else "",
            _end(", ".join(rest)) if rest else ""]
    return " ".join(s for s in segs if s)


def bibtex(b: dict) -> str:
    au = b.get("authors") or []
    word = next((w for w in re.findall(r"[a-z0-9]+", (b.get("title") or "").lower()) if w not in STOPWORDS), "")
    key = re.sub(r"[^a-z0-9]", "", (au[0]["family"].lower() if au else "")) + str(b.get("year") or "") + word
    kind = "article" if b.get("venue") else "misc"
    pages = (b.get("pages") or "") and re.sub(r"\s*[-–]+\s*", "--", b["pages"])
    fields = [("title", b.get("title")),
              ("author", " and ".join(f"{a['family']}, {a['given']}" if a.get("given") else a["family"] for a in au)),
              ("journal", b.get("venue")), ("year", b.get("year")), ("volume", b.get("volume")),
              ("number", b.get("issue")), ("pages", pages), ("doi", _doi(b)), ("url", b.get("url")),
              ("eprint", b.get("arxiv")), ("archivePrefix", b.get("arxiv") and "arXiv")]
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields if v)
    return f"@{kind}{{{key or 'paper'},\n{body}\n}}" if body else f"@{kind}{{{key or 'paper'}}}"


def styles(b: dict) -> dict:
    return {"apa": apa(b), "ieee": ieee(b), "mla": mla(b), "bibtex": bibtex(b)}
