"""測試用的假論文，用 PyMuPDF 現場產生，測試不需要網路、也不用放二進位檔進專案。

- numeric.pdf    ：編號式引用 [1]、一張圖（Figure 1）、一張有框線的表（Table 1）
- authoryear.pdf ：作者-年份引用（ACL 風格），參考文獻用懸掛縮排
- scanned.pdf    ：把 numeric.pdf 每頁畫成圖片，模擬掃描檔（沒有文字層）
"""
from __future__ import annotations

from pathlib import Path

import pymupdf

W, H = 612, 792  # Letter
BODY = (
    "Reading scientific papers requires connecting each sentence to the surrounding argument and definitions. "
    "We introduce a lantern encoder that keeps a running memory of the definitions introduced so far. "
    "The decoder attends to this memory whenever a technical term appears in the selected passage. "
    "Our experiments show that the lantern encoder improves explanation accuracy by twelve points. "
)


def _text(page, y: float, text: str, size: float = 10, font: str = "helv", h: float | None = None) -> float:
    """在 y 放一段文字，回傳下一段可以開始的 y。段落之間留空，PyMuPDF 才會切成不同 block。"""
    h = h or size * 1.5 * (len(text) // 95 + 1) + 4
    rc = page.insert_textbox(pymupdf.Rect(72, y, W - 72, y + h), text, fontsize=size, fontname=font)
    if rc < 0:  # 框太小時 PyMuPDF 會「什麼都不畫」，這裡直接報錯，免得測資默默少一段
        raise ValueError(f"textbox too small by {-rc:.1f}pt: {text[:40]}")
    return y + h + 14


def numeric(path: Path) -> Path:
    doc = pymupdf.open()
    p = doc.new_page(width=W, height=H)
    y = _text(p, 60, "Sparse Lantern Networks for Document Reading", 20, "hebo", 40)
    y = _text(p, y, "Ada Lovelace and Alan Turing", 11)
    y = _text(p, y, "Abstract", 11, "hebo")
    y = _text(p, y, "We present sparse lantern networks, a model that explains passages of scientific papers "
                    "in the context of the whole document. " + BODY, 10)
    y = _text(p, y, "1 Introduction", 12, "hebo")
    y = _text(p, y, "Prior work on reading assistants [1] treats each passage in isolation, and retrieval "
                    "methods [2, 3] ignore the structure of the paper. The overall pipeline is shown in "
                    "Figure 1 and the main results are reported in Table 1. " + BODY, 10)

    p = doc.new_page(width=W, height=H)
    y = _text(p, 60, "2 Method", 12, "hebo")
    y = _text(p, y, BODY, 10)
    # 圖：幾個方塊 + 箭頭，圖說在下方
    for i, x in enumerate((120, 260, 400)):
        p.draw_rect(pymupdf.Rect(x, 230, x + 100, 300), color=(0, 0, 0), fill=(0.8, 0.9, 1.0))
        if i:
            p.draw_line((x - 40, 265), (x, 265))
    _text(p, 320, "Figure 1: Overview of the lantern pipeline.", 9)
    # 表：標題在上方，三條橫線（booktabs 風格）
    _text(p, 400, "Table 1: Explanation accuracy on the benchmark.", 9)
    for ly in (430, 450, 500):
        p.draw_line((150, ly), (460, ly), width=0.6)
    p.insert_text((160, 444), "Model                     Accuracy", fontsize=9)
    p.insert_text((160, 466), "Baseline                  61.2", fontsize=9)
    p.insert_text((160, 486), "Lantern (ours)            73.4", fontsize=9)

    p = doc.new_page(width=W, height=H)
    y = _text(p, 60, "3 Conclusion", 12, "hebo")
    y = _text(p, y, BODY, 10)
    y = _text(p, y, "References", 12, "hebo")
    for ref in ("[1] J. Smith and K. Lee. Reading assistants for science. In ACL, 2019.",
                "[2] P. Lewis et al. Retrieval-augmented generation for knowledge-intensive tasks. In NeurIPS, 2020.",
                "[3] V. Karpukhin et al. Dense passage retrieval for open-domain question answering. In EMNLP, 2020.",
                "[4] A. Vaswani et al. Attention is all you need. In NeurIPS, 2017."):
        y = _text(p, y, ref, 9, h=16)
    doc.save(path)
    return path


def authoryear(path: Path) -> Path:
    doc = pymupdf.open()
    p = doc.new_page(width=W, height=H)
    y = _text(p, 60, "Contextual Lanterns for Reading", 20, "hebo", 40)
    y = _text(p, y, "Abstract", 11, "hebo")
    y = _text(p, y, "Contextual word representations (Peters et al., 2018a) changed how models read text, "
                    "and Devlin et al. (2019) showed that bidirectional pre-training helps. " + BODY, 10)

    p = doc.new_page(width=W, height=H)
    p.insert_text((72, 80), "References", fontsize=12, fontname="hebo")
    y = 120
    entries = [
        ("Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. 2019. BERT: Pre-training",
         "of deep bidirectional transformers for language understanding. In NAACL."),
        ("Matthew Peters, Mark Neumann, Mohit Iyyer, Matt Gardner, and Luke Zettlemoyer. 2018a.",
         "Deep contextualized word representations. In NAACL."),
        ("Matthew Peters, Mark Neumann, Luke Zettlemoyer, and Wen-tau Yih. 2018b. Dissecting",
         "contextual word embeddings: Architecture and representation. In EMNLP."),
        ("Ashish Vaswani, Noam Shazeer, Niki Parmar, and Jakob Uszkoreit. 2017. Attention is all",
         "you need. In NeurIPS."),
    ]
    for first, rest in entries:  # 懸掛縮排：第一行貼左緣，續行縮 12pt
        p.insert_text((72, y), first, fontsize=9)
        p.insert_text((84, y + 11), rest, fontsize=9)
        y += 30
    doc.save(path)
    return path


def scanned(src: Path, path: Path) -> Path:
    s = pymupdf.open(src)
    out = pymupdf.open()
    for page in s:
        pix = page.get_pixmap(dpi=100)
        np_ = out.new_page(width=page.rect.width, height=page.rect.height)
        np_.insert_image(np_.rect, stream=pix.tobytes("png"))
    out.save(path)
    return path


def make_all(folder: Path) -> dict[str, Path]:
    folder.mkdir(parents=True, exist_ok=True)
    n = numeric(folder / "numeric.pdf")
    return {"numeric": n, "authoryear": authoryear(folder / "authoryear.pdf"),
            "scanned": scanned(n, folder / "scanned.pdf")}
