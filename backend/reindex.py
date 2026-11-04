"""重建所有論文的檢索索引：設好（或換了）EMBED_MODEL 之後，讓舊論文也有向量、參考文獻區分段。
用法：uv run python -m backend.reindex
掃描版（有 OCR 頁）的論文不重新解析 PDF（會丟掉 OCR 文字），改用現有段落重算向量。"""
from __future__ import annotations

import asyncio

from . import config, db, retrieval
from .pdf_parse import Block, parse_pdf


async def main() -> None:
    db.init()
    with db.conn() as c:
        papers = [(r["id"], r["title"]) for r in c.execute("SELECT id, title FROM papers")]
    print(f"{len(papers)} 篇，EMBED_MODEL={config.EMBED_MODEL or '（未設定，只建關鍵字索引）'}")
    for pid, title in papers:
        p = db.get_paper(pid)
        try:
            if p["meta"].get("ocr_pages"):
                blocks = [Block(ch["page"], ch["text"], ch["bbox"][0], 0) for ch in db.load_chunks(pid)]
            else:
                blocks = parse_pdf(str(config.DATA_DIR / "pdfs" / f"{pid}.pdf")).blocks
            n = await retrieval.build_index(pid, blocks)
        except Exception as e:  # 一篇壞掉（PDF 不見了）不影響其他篇
            print(f"  失敗 {(title or pid)[:60]}：{type(e).__name__}: {e}")
            continue
        vec = db.cache_get(pid, "embed_model") == config.EMBED_MODEL and bool(config.EMBED_MODEL)
        print(f"  {n:4d} 段 {'向量' if vec else '關鍵字'}  {(title or pid)[:60]}")


if __name__ == "__main__":
    asyncio.run(main())
