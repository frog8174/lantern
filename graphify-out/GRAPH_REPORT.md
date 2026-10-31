# Graph Report - paper-reader  (2026-11-01)

## Corpus Check
- 31 files · ~33,165 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .example 1, .css 1)

## Summary
- 747 nodes · 1848 edges · 37 communities (33 shown, 4 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 45 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c5ab010f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- chat_messages
- Anthropic Provider Tests
- db.py
- re
- llm.py
- test_units.py
- Lantern 視覺系統（燈下的那一頁）
- fake_api.py
- Frontend UI Layout
- Static File Caching
- Graphify Graph Output
- Lantern Paper Reader
- 功能對照
- CLAUDE.md
- backend/__init__.py
- Workspace LLM Wiki（MVP）
- escapeHTML
- retrieval.py
- drawHighlights
- cite.py
- aiCard
- streamInto
- pumpTranslation
- _ingest
- update_wiki
- drawOutline
- 多使用者論文庫 + Workspace（測試登入版）
- auto_highlight
- main.py
- 論文卡：備註、星號、排序、複製引用
- conftest.py
- features.py
- json
- escapeHTML
- Lantern — 個人用 AI 論文閱讀器
- UX 第一輪（已定案）

## God Nodes (most connected - your core abstractions)
1. `conn()` - 44 edges
2. `_paper_or_404()` - 33 edges
3. `escapeHTML()` - 32 edges
4. `sse()` - 29 edges
5. `_id()` - 27 edges
6. `api()` - 26 edges
7. `_ws_or_404()` - 18 edges
8. `_ingest()` - 18 edges
9. `cache_get()` - 17 edges
10. `功能對照` - 17 edges

## Surprising Connections (you probably didn't know these)
- `資料表（`backend/db.py`）` --references--> `list_papers()`  [INFERRED]
  docs/paper-cards.md → backend/db.py
- `API` --references--> `_ws_or_404()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `範圍限制` --references--> `_mark_in_library()`  [INFERRED]
  docs/workspaces.md → backend/main.py
- `更新流程（後端，`features.py` 放 prompt）` --references--> `wiki()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `前端畫面` --references--> `api()`  [INFERRED]
  docs/workspaces.md → frontend/app.js

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (37 total, 4 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.05
Nodes (30): AUTO, calmMotion, card, caretAt(), CITE_STYLES, citeStyles, COLORS, customColor (+22 more)

### Community 1 - "chat_messages"
Cohesion: 0.15
Nodes (12): chat_messages(), cite_reason_messages(), citing_contexts(), _est_tokens(), full_text_fits(), _header(), _pages_text(), _paper_body() (+4 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (39): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+31 more)

### Community 3 - "db.py"
Cohesion: 0.11
Nodes (26): add_annotation(), add_message(), add_wiki_message(), add_workspace(), annotation_paper(), clear_messages(), clear_wiki_messages(), conn() (+18 more)

### Community 4 - "re"
Cohesion: 0.15
Nodes (19): _wiki_slug(), _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), _guess_title(), _is_ref_head() (+11 more)

### Community 5 - "llm.py"
Cohesion: 0.06
Nodes (23): _build(), check(), _claude(), _claude_block(), _claude_stream(), _create(), _mock_answer(), ocr_image() (+15 more)

### Community 6 - "test_units.py"
Cohesion: 0.17
Nodes (9): _translatable(), find_figures(), llm._ThinkStripper, test_find_figures(), test_page_blocks_and_render(), test_parse_numeric(), test_scanned_detection(), test_think_stripper() (+1 more)

### Community 7 - "Lantern 視覺系統（燈下的那一頁）"
Cohesion: 0.25
Nodes (7): Lantern 視覺系統（燈下的那一頁）, 原則, 字體分工, 捲軸, 用語, 色彩 token, 薛西弗斯（等待、完成、空狀態）

### Community 8 - "fake_api.py"
Cohesion: 0.11
Nodes (12): _answer(), chat(), claude_messages(), gen(), embeddings(), _err(), files(), _sse() (+4 more)

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "功能對照"
Cohesion: 0.20
Nodes (9): explain_messages(), _history_block(), image_messages(), local_context(), page_translate_messages(), stream_block_translation(), run(), translate_messages() (+1 more)

### Community 15 - "backend/__init__.py"
Cohesion: 0.11
Nodes (7): byline(), _row(), test_byline(), test_cards_scoped_to_owner(), test_cite_cached_and_year(), test_patch_fields_independently(), test_auto_translate_setting()

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.19
Nodes (20): api(), cardsBusy(), enter(), importArxiv(), ingest(), loadLibrary(), loadPaperWiki(), loadSideList() (+12 more)

### Community 18 - "retrieval.py"
Cohesion: 0.13
Nodes (13): load_chunks(), save_chunks(), embed(), _bm25(), build_index(), make_chunks(), search(), _tokens() (+5 more)

### Community 19 - "drawHighlights"
Cohesion: 0.28
Nodes (13): addAnnotation(), colorKey(), deleteAnnotation(), drawHighlights(), flashItem(), isHex(), noteItem(), refreshHighlights() (+5 more)

### Community 20 - "cite.py"
Cohesion: 0.19
Nodes (18): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+10 more)

### Community 21 - "aiCard"
Cohesion: 0.21
Nodes (12): aiCard(), closeAiCard(), commentEditor(), explainCrop(), explainImage(), imageFollowup(), openPanel(), placeFloating() (+4 more)

### Community 22 - "streamInto"
Cohesion: 0.22
Nodes (13): addCopy(), addMsg(), bibtex(), icon(), loadChat(), renderExplains(), renderMD(), renderRefs() (+5 more)

### Community 23 - "pumpTranslation"
Cohesion: 0.24
Nodes (12): buildPages(), drawRail(), drawTranslation(), fitText(), pumpTranslation(), queueTranslation(), renderPage(), setTrMode() (+4 more)

### Community 24 - "_ingest"
Cohesion: 0.20
Nodes (10): add_paper(), add_to_workspace(), get_paper(), get_settings(), _auto_wiki(), _duplicate(), _first_doi(), _ingest() (+2 more)

### Community 25 - "update_wiki"
Cohesion: 0.13
Nodes (13): list_wiki_messages(), wiki_mark_ingested(), wiki_page(), wiki_pages(), wiki_pending(), wiki_save(), update_wiki(), wiki_ask_messages() (+5 more)

### Community 26 - "drawOutline"
Cohesion: 0.29
Nodes (7): drawOutline(), goToPage(), hideFigure(), markOutline(), renderOutline(), setLibDrawer(), showFigure()

### Community 27 - "多使用者論文庫 + Workspace（測試登入版）"
Cohesion: 0.25
Nodes (7): Workspace API, 前端畫面, 多使用者論文庫 + Workspace（測試登入版）, 決定, 範圍限制, 資料表（`backend/db.py`）, 這次不做

### Community 28 - "auto_highlight"
Cohesion: 0.32
Nodes (6): auto_highlight(), guarded(), one(), _reference_start_page(), find_text_rects(), test_find_text_rects()

### Community 29 - "main.py"
Cohesion: 0.05
Nodes (86): cache_get(), cache_set(), list_papers(), stream_chat(), add_annotation(), add_to_workspace(), annotations(), AnnotIn (+78 more)

### Community 30 - "論文卡：備註、星號、排序、複製引用"
Cohesion: 0.33
Nodes (5): 前端（論文卡）, 決定, 論文卡：備註、星號、排序、複製引用, 資料表（`backend/db.py`）, 這次不做

### Community 31 - "conftest.py"
Cohesion: 0.09
Nodes (12): _load_dotenv(), allow_duplicates(), bob(), client(), fake_server(), papers(), pdfs(), authoryear() (+4 more)

### Community 32 - "features.py"
Cohesion: 0.10
Nodes (23): ai_outline(), _bib_arxiv(), _bib_llm(), _bib_s2(), _check(), fetch_bib(), _guess_ref_title(), lookup_reference() (+15 more)

### Community 34 - "json"
Cohesion: 0.25
Nodes (5): find_duplicate(), list_annotations(), norm_title(), set_settings(), update_paper()

### Community 35 - "escapeHTML"
Cohesion: 0.18
Nodes (19): addAsk(), addSave(), cardPaper(), escapeHTML(), fmtDate(), loadAsk(), loadRelated(), loadWiki() (+11 more)

### Community 36 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

### Community 42 - "UX 第一輪（已定案）"
Cohesion: 0.33
Nodes (5): A. 閱讀頁重新排版, B. 研究主題頁與流程, C. 全站主題切換, UX 第一輪（已定案）, 不做

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `/api/health endpoint`, `BM25 retrieval` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 233 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `features.py`, `app.js`, `db.py`, `re`, `llm.py`?**
  _High betweenness centrality (0.306) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.04994192799070848 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `llm.py`, `re`, `功能對照`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._
- **Why does `功能對照` connect `功能對照` to `features.py`, `chat_messages`, `db.py`, `Lantern — 個人用 AI 論文閱讀器`, `llm.py`, `test_units.py`, `re`, `auto_highlight`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Should `db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11092436974789915 - nodes in this community are weakly interconnected._