"""PDF 解析：把 PDF 變成「帶座標的文字」。

為什麼要座標？前端要在原 PDF 上畫螢光筆（自動標註）、點引用跳到正確位置，
都需要知道某段文字在第幾頁、在頁面上哪個矩形（bbox, bounding box）。

座標一律正規化成 0~1（除以頁寬、頁高），前端不管縮放多少都能直接乘回去。

這裡用 PyMuPDF：快、純本地、不用 GPU。若之後要更好的版面分析
（雙欄、表格、公式轉 LaTeX），可以換成 MinerU / Marker / GROBID，
只要輸出同樣的 ParsedPaper 結構即可。
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

import pymupdf


@dataclass
class Block:
    page: int  # 0-based
    text: str
    bbox: list[float]  # [x0, y0, x1, y1]，0~1
    size: float  # 平均字級，用來猜標題


@dataclass
class ParsedPaper:
    title: str
    num_pages: int
    page_sizes: list[list[float]]
    pages: list[str]  # 每頁純文字
    blocks: list[Block]
    outline: list[dict]  # [{level, title, page}]
    abstract: str
    references: dict[str, str] = field(default_factory=dict)  # "12" -> 參考文獻原文
    scanned_pages: list[int] = field(default_factory=list)  # 沒文字層、只有圖片的頁
    ocr_pages: list[int] = field(default_factory=list)  # 已用 OCR 補上文字的頁

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("blocks")
        return d


_HEADING_RE = re.compile(
    r"^((\d+(\.\d+)*)\.?|[IVX]+\.|[A-Z]\.)\s+[A-Z][A-Za-z].{0,80}$"
)
_REF_HEAD_RE = re.compile(r"^\s*(references|bibliography|參考文獻)\s*$", re.I)


def _clean(text: str) -> str:
    text = text.replace("­", "")  # soft hyphen
    text = re.sub(r"-\n(?=[a-z])", "", text)  # 行尾斷字 "experi-\nment"
    text = re.sub(r"\s*\n\s*", " ", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def _page_blocks(page, pno: int) -> list[Block]:
    w, h = page.rect.width, page.rect.height
    out: list[Block] = []
    for b in page.get_text("dict", sort=True)["blocks"]:
        if b.get("type") != 0:  # 0 = 文字，1 = 圖片
            continue
        # 跳過直排 / 旋轉的字，例如 arXiv 左側的 "arXiv:xxxx [cs.CL]" 浮水印，
        # 否則字級很大，會被誤當成標題
        lines = [ln for ln in b["lines"] if abs(ln.get("dir", (1, 0))[1]) < 0.1]
        if not lines:
            continue
        spans = [s for line in lines for s in line["spans"]]
        raw = "\n".join("".join(s["text"] for s in line["spans"]) for line in lines)
        text = _clean(raw)
        if not text:
            continue
        avg = sum(s["size"] * len(s["text"]) for s in spans) / max(1, sum(len(s["text"]) for s in spans))
        x0 = min(ln["bbox"][0] for ln in lines); y0 = min(ln["bbox"][1] for ln in lines)
        x1 = max(ln["bbox"][2] for ln in lines); y1 = max(ln["bbox"][3] for ln in lines)
        out.append(Block(pno, text, [x0 / w, y0 / h, x1 / w, y1 / h], round(avg, 1)))
    return out


def page_blocks(path: str, page_no: int) -> list[Block]:
    """單頁的文字區塊（含座標），給「對照翻譯」逐段疊在原文位置上。"""
    doc = pymupdf.open(path)
    try:
        return _page_blocks(doc[page_no], page_no)
    finally:
        doc.close()


def parse_pdf(path: str) -> ParsedPaper:
    doc = pymupdf.open(path)
    blocks: list[Block] = []
    pages: list[str] = []
    sizes: list[list[float]] = []

    for pno, page in enumerate(doc):
        sizes.append([page.rect.width, page.rect.height])
        page_blocks = _page_blocks(page, pno)
        blocks += page_blocks
        pages.append("\n".join(b.text for b in page_blocks))

    title = _guess_title(doc, blocks)
    outline = _outline(doc, blocks)
    abstract = _abstract(blocks)
    references = _references(blocks, doc)
    scanned = [i for i, pg in enumerate(doc) if _is_scanned(pg, pages[i])]
    doc.close()
    return ParsedPaper(title, len(pages), sizes, pages, blocks, outline, abstract, references, scanned)


# ---------------- 圖表定位（滑過 "Figure 3" 就預覽）----------------
_CAPTION_RE = re.compile(r"^(Figure|Fig\.?|Table|Tab\.)\s*(\d+)\s*[:.|]", re.I)


def find_figures(path: str) -> list[dict]:
    """找出每張圖 / 表的位置：先找圖說（"Figure 3:" 開頭的文字區塊），再找它旁邊的圖形。

    圖的圖說通常在下方 → 往上找圖片和向量線條；表的標題通常在上方 → 往下找。
    找不到圖形時退而求其次，取圖說上方（或下方）一段固定高度。
    回傳 [{kind: "figure"|"table", num, page, bbox(0~1), caption}]，同一編號只取第一個。
    """
    doc = pymupdf.open(path)
    out: dict[tuple[str, str], dict] = {}
    try:
        for pno, page in enumerate(doc):
            W, H = page.rect.width, page.rect.height
            caps = []
            text_blocks = page.get_text("blocks", sort=True)
            # 雙欄排版：長段落大多不到半頁寬
            paras = [b for b in text_blocks if len(b[4]) > 150]
            two_col = bool(paras) and sum(b[2] - b[0] < 0.55 * W for b in paras) > len(paras) / 2
            for b in text_blocks:
                m = _CAPTION_RE.match(b[4].strip())
                if m and b[6] == 0:
                    kind = "table" if m.group(1).lower().startswith("tab") else "figure"
                    if (kind, m.group(2)) not in out:
                        caps.append((kind, m.group(2), pymupdf.Rect(b[:4]), _clean(b[4])))
            if not caps:
                continue
            graphics = [pymupdf.Rect(i["bbox"]) & page.rect for i in page.get_image_info()]
            # 向量圖形與表格框線。框線是高度 0 的矩形（PyMuPDF 視為空），補 1pt 厚度
            for d in page.get_drawings():
                r = pymupdf.Rect(d["rect"])
                if r.width > 3 or r.height > 3:
                    graphics.append(r + (-0.5, -0.5, 0.5, 0.5))
            for kind, num, cap, text in caps:
                below = kind == "table"  # 表格內容在標題下方
                lo, hi = (cap.y1 - 4, cap.y1 + 0.6 * H) if below else (cap.y0 - 0.65 * H, cap.y0 + 4)
                # 圖說常比圖窄（靠左或置中），橫向改看「圖說所在的欄」：左欄、右欄或跨欄
                if not two_col:
                    cx0, cx1 = 0, W
                elif cap.x1 <= W / 2 + 10:
                    cx0, cx1 = 0, W / 2 + 10
                elif cap.x0 >= W / 2 - 10:
                    cx0, cx1 = W / 2 - 10, W
                else:
                    cx0, cx1 = 0, W
                near = [g for g in graphics if not g.is_empty
                        and (lo <= g.y0 and g.y1 <= hi) and g.x0 >= cx0 - 2 and g.x1 <= cx1 + 2]
                region = pymupdf.Rect(cap)
                # 從圖說往外一塊塊吸進來，只收「跟目前範圍相連」的，才不會吃到下一段的公式
                gap = (0.15 if below else 0.1) * H  # 表格框線之間隔著好幾列字，容許的間距大一點
                for g in sorted(near, key=lambda g: g.y0 if below else -g.y1):
                    if (g.y0 <= region.y1 + gap) if below else (g.y1 >= region.y0 - gap):
                        region |= g
                if region == cap:  # 沒找到圖形：取圖說上方（表格取下方）一段
                    if below:
                        region.y1 = min(H, cap.y1 + 0.3 * H)
                    else:
                        region.y0 = max(0, cap.y0 - 0.3 * H)
                region = (region + (-6, -6, 6, 6)) & page.rect
                out[(kind, num)] = {"kind": kind, "num": num, "page": pno, "caption": text[:400],
                                    "bbox": [region.x0 / W, region.y0 / H, region.x1 / W, region.y1 / H]}
    finally:
        doc.close()
    return list(out.values())


# ---------------- 掃描版 PDF ----------------
def _is_scanned(page, text: str) -> bool:
    """幾乎沒有文字、卻有一張大圖蓋住頁面 → 掃描頁。
    單純的空白頁、全圖頁（論文裡的大圖）文字也少，所以要同時看圖片面積。"""
    if len(text.strip()) >= 40:
        return False
    area = page.rect.width * page.rect.height
    covered = sum(abs(pymupdf.Rect(i["bbox"]) & page.rect) for i in page.get_image_info())
    return covered > 0.5 * area


def render_page_png(path: str, page_no: int, dpi: int = 150, clip: list[float] | None = None) -> bytes:
    """把一頁（或頁上的一塊，clip 為 0~1 座標）畫成 PNG，給 OCR、圖表預覽用。"""
    doc = pymupdf.open(path)
    try:
        page = doc[page_no]
        rect = None
        if clip:
            w, h = page.rect.width, page.rect.height
            rect = pymupdf.Rect(clip[0] * w, clip[1] * h, clip[2] * w, clip[3] * h)
        return page.get_pixmap(dpi=dpi, clip=rect).tobytes("png")
    finally:
        doc.close()


def apply_ocr(paper: ParsedPaper, results: dict[int, str]) -> None:
    """把 OCR 文字放回解析結果。OCR 沒有逐字座標，所以每段的 bbox 給整頁；
    聊天、摘要、檢索都能用，但自動標註畫不到這些頁上。"""
    if not results:
        return
    paper.blocks = [b for b in paper.blocks if b.page not in results]
    for pno, md in sorted(results.items()):
        paper.pages[pno] = md
        for para in re.split(r"\n\s*\n", md):
            text = _clean(para.lstrip("# ").strip())
            if text:
                size = 20.0 if para.startswith("# ") else 14.0 if para.startswith("#") else 10.0
                paper.blocks.append(Block(pno, text, [0.0, 0.0, 1.0, 1.0], size))
    paper.blocks.sort(key=lambda b: b.page)
    paper.ocr_pages = sorted(results)
    # 標題、大綱、摘要、參考文獻都依賴文字，重算一次
    if 0 in results:
        heads = re.findall(r"^#\s+(.+)$", results[0], re.M)
        lines = [ln.strip() for ln in results[0].splitlines() if len(ln.strip()) > 5]
        paper.title = (heads[0] if heads else lines[0] if lines else paper.title)[:200]
    md_outline = [{"level": len(m.group(1)), "title": m.group(2).strip(), "page": pno}
                  for pno, md in sorted(results.items())
                  for m in re.finditer(r"^(#{2,4})\s+(.+)$", md, re.M)]
    if md_outline and not paper.outline:
        paper.outline = md_outline[:80]
    paper.abstract = paper.abstract or _abstract(paper.blocks)
    paper.references = paper.references or _references(paper.blocks)


def _guess_title(doc, blocks: list[Block]) -> str:
    meta = (doc.metadata or {}).get("title", "").strip()
    if len(meta) > 8 and not meta.lower().endswith((".pdf", ".dvi", ".tex")):
        return meta
    first = [b for b in blocks if b.page == 0 and len(b.text) > 5]
    if not first:
        return "Untitled"
    top = max(first, key=lambda b: b.size)
    # 標題常折成兩行、被切成相鄰兩個 block（例：BERT 的 "...Transformers for" / "Language Understanding"）
    i = first.index(top)
    parts = [top.text]
    for b in first[i + 1: i + 3]:
        if abs(b.size - top.size) > 0.6 or b.bbox[1] - top.bbox[3] > 0.06:
            break
        parts.append(b.text)
    return " ".join(parts)[:200]


def _outline(doc, blocks: list[Block]) -> list[dict]:
    toc = doc.get_toc(simple=True)  # PDF 內建書籤
    if toc:
        return [{"level": lv, "title": t, "page": p - 1} for lv, t, p in toc]
    # 沒書籤：用「字比內文大 or 有編號」猜章節標題
    body = sorted(b.size for b in blocks)
    body_size = body[len(body) // 2] if body else 10
    out = []
    for b in blocks:
        short = len(b.text) < 90
        numbered = bool(_HEADING_RE.match(b.text))
        bigger = b.size > body_size * 1.15
        if short and (numbered or (bigger and b.page > 0)) and not b.text.endswith("."):
            m = re.match(r"^(\d+(\.\d+)*)", b.text)
            level = m.group(1).count(".") + 1 if m else 1
            out.append({"level": level, "title": b.text, "page": b.page})
    return out[:80]


def _abstract(blocks: list[Block]) -> str:
    for i, b in enumerate(blocks[:60]):
        if b.text.lower().startswith("abstract"):
            text = re.sub(r"^abstract[\s.:—-]*", "", b.text, flags=re.I)
            nxt = blocks[i + 1].text if i + 1 < len(blocks) else ""
            if len(text) < 200 and nxt and not _HEADING_RE.match(nxt):
                text += " " + nxt
            return text.strip()[:3000]  # "Abstract" 自己一個 block 時，前面會多一個空白
    return ""


def _is_ref_head(text: str) -> bool:
    return bool(_REF_HEAD_RE.match(text) or re.match(r"^\s*references\b", text, re.I) and len(text) < 30)


def _references(blocks: list[Block], doc=None) -> dict[str, str]:
    start = None
    for i, b in enumerate(blocks):
        if _is_ref_head(b.text):
            start = i
    if start is None:
        return {}
    text = " ".join(b.text for b in blocks[start + 1:])
    refs: dict[str, str] = {}
    # 樣式一：[12] Author ...
    parts = re.split(r"\[(\d{1,3})\]\s*", text)
    if len(parts) > 5:
        for num, body in zip(parts[1::2], parts[2::2]):
            refs[num] = body.strip()[:600]
        return refs
    # 樣式二（作者-年份，如 ACL、NeurIPS）：靠「懸掛縮排」切條目
    if doc is not None:
        refs = _author_year_refs(doc, blocks[start].page)
        if refs:
            return refs
    for k, b in enumerate(blocks[start + 1:], start=1):  # 退路：一個 block 當一筆
        if re.search(r"\b(19|20)\d{2}\b", b.text):
            refs[str(k)] = b.text[:600]
    return refs


def _author_year_refs(doc, start_page: int) -> dict[str, str]:
    """作者-年份格式的參考文獻：每筆第一行貼齊欄左緣，續行往右縮排。
    逐行讀，貼齊左緣 = 新的一筆；遇到比參考文獻字大的短行（例如附錄標題）就停。"""
    lines: list[tuple[int, float, float, str]] = []  # (欄位 key, x0, 字級, 文字)
    started = False
    for pno in range(start_page, len(doc)):
        page = doc[pno]
        half = page.rect.width / 2
        for b in page.get_text("dict")["blocks"]:  # 不排序：PyMuPDF 預設順序就是一欄一欄
            if b.get("type") != 0:
                continue
            for ln in b["lines"]:
                t = "".join(s["text"] for s in ln["spans"]).strip()
                if not t or abs(ln.get("dir", (1, 0))[1]) > 0.1:
                    continue
                if not started:
                    started = pno == start_page and _is_ref_head(t)
                    continue
                size = max(s["size"] for s in ln["spans"])
                col = pno * 2 + (ln["bbox"][0] > half)
                lines.append((col, ln["bbox"][0], size, t))
    if not lines:
        return {}
    sizes = sorted(s for _, _, s, _ in lines)
    body = sizes[len(sizes) // 2]
    margin: dict[int, float] = {}
    for col, x0, _, _ in lines:
        margin[col] = min(margin.get(col, x0), x0)
    entries: list[str] = []
    for col, x0, size, t in lines:
        if size > body * 1.15 and len(t) < 80:  # 附錄等新章節開始
            break
        if x0 <= margin[col] + 2.5 or not entries:
            entries.append(t)
        else:
            entries[-1] += "\n" + t
    refs = {str(i): _clean(e)[:600] for i, e in enumerate(entries, 1)
            if re.search(r"\b(19|20)\d{2}[a-z]?\b", e)}
    return refs if len(refs) >= 3 else {}


def match_author_year(refs: dict[str, str], author: str, year: str) -> str | None:
    """(Peters et al., 2018a) → 找出作者姓氏出現在「年份之前」、年份（含 a/b 字尾）相符的那筆。"""
    best, best_score = None, 0
    for key, ref in refs.items():
        m = re.search(rf"\b{re.escape(year[:4])}{re.escape(year[4:])}\b", ref)
        if not m:
            continue
        authors = ref[: m.start()]
        if not re.search(rf"\b{re.escape(author)}\b", authors, re.I):
            continue
        # 第一作者（姓氏出現在最前面）分數最高
        score = 3 if re.search(rf"\b{re.escape(author)}\b", authors[:40], re.I) else 1
        if score > best_score:
            best, best_score = key, score
    return best


def find_text_rects(path: str, page_no: int, needle: str) -> list[list[float]]:
    """在指定頁找一段文字，回傳正規化矩形。給自動標註、引用定位用。

    LLM 抄回來的句子常跟原文有些微差異（空白、連字號），所以：
    先找整句 → 找不到就切成幾段短的分別找。
    """
    doc = pymupdf.open(path)
    try:
        page = doc[page_no]
        w, h = page.rect.width, page.rect.height
        needle = re.sub(r"\s+", " ", needle).strip()
        candidates = [needle]
        words = needle.split(" ")
        if len(words) > 10:
            candidates += [" ".join(words[i: i + 8]) for i in range(0, len(words) - 4, 8)]
        rects: list[list[float]] = []
        for cand in candidates:
            hits = page.search_for(cand)
            if hits:
                rects += [[r.x0 / w, r.y0 / h, r.x1 / w, r.y1 / h] for r in hits]
                if cand is needle:
                    break
        return rects
    finally:
        doc.close()
