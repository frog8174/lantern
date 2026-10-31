# Graph Report - agent-ad0d76101ab36784c  (2026-10-31)

## Corpus Check
- 30 files · ~32,316 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .example 1, .css 1)

## Summary
- 725 nodes · 1800 edges · 44 communities (38 shown, 6 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 45 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `403c80ed`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- Uid
- Anthropic Provider Tests
- db.py
- pdf_parse.py
- llm.py
- features.py
- Lantern 視覺系統（燈下的那一頁）
- fake_api.py
- Frontend UI Layout
- Static File Caching
- Graphify Graph Output
- Lantern Paper Reader
- 論文卡：備註、星號、排序、複製引用
- CLAUDE.md
- test_paper_cards.py
- Workspace LLM Wiki（MVP）
- escapeHTML
- retrieval.py
- drawHighlights
- cite.py
- aiCard
- streamInto
- pumpTranslation
- _ingest
- backend/__init__.py
- drawOutline
- 多使用者論文庫 + Workspace（測試登入版）
- s2_get
- main.py
- sse
- conftest.py
- chat_messages
- _ws_or_404
- edit_annotation
- paintWsCards
- Lantern — 個人用 AI 論文閱讀器
- asyncio
- complete_json
- backend/__init__.py
- config.py
- 功能對照
- UX 第一輪（已定案）
- auto_highlight

## God Nodes (most connected - your core abstractions)
1. `conn()` - 43 edges
2. `_paper_or_404()` - 33 edges
3. `escapeHTML()` - 32 edges
4. `sse()` - 30 edges
5. `_id()` - 27 edges
6. `api()` - 26 edges
7. `_ws_or_404()` - 18 edges
8. `cache_get()` - 17 edges
9. `功能對照` - 17 edges
10. `parse_pdf()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `資料表（`backend/db.py`）` --references--> `list_papers()`  [INFERRED]
  docs/paper-cards.md → backend/db.py
- `API` --references--> `_ws_or_404()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `更新流程（後端，`features.py` 放 prompt）` --references--> `wiki()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `前端畫面` --references--> `api()`  [INFERRED]
  docs/workspaces.md → frontend/app.js
- `功能對照` --references--> `search_chunks()`  [INFERRED]
  README.md → backend/db.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (44 total, 6 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.06
Nodes (27): AUTO, calmMotion, card, caretAt(), CITE_STYLES, citeStyles, COLORS, customColor (+19 more)

### Community 1 - "Uid"
Cohesion: 0.13
Nodes (29): cache_get(), cache_set(), annotations(), _cached_text(), chat_history(), cite_paper(), _ensure_bib(), figure_png() (+21 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.09
Nodes (27): _id(), test_ai_outline(), test_annotation_kinds(), test_annotations_crud(), test_ask_ai_on_selection(), test_author_year_reference(), test_auto_highlight_finds_sentence(), test_bilingual_blocks() (+19 more)

### Community 3 - "db.py"
Cohesion: 0.10
Nodes (29): add_annotation(), add_paper(), add_wiki_message(), add_workspace(), conn(), delete_annotation(), delete_wiki_exchange(), get_workspace() (+21 more)

### Community 4 - "pdf_parse.py"
Cohesion: 0.08
Nodes (32): _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), find_figures(), find_text_rects(), _guess_title() (+24 more)

### Community 5 - "llm.py"
Cohesion: 0.07
Nodes (21): _build(), check(), _claude(), _claude_block(), _claude_stream(), _create(), _mock_answer(), route() (+13 more)

### Community 6 - "features.py"
Cohesion: 0.22
Nodes (10): _bib_arxiv(), _bib_llm(), _bib_s2(), fetch_bib(), _guess_ref_title(), lookup_reference(), _name(), page_translate_messages() (+2 more)

### Community 7 - "Lantern 視覺系統（燈下的那一頁）"
Cohesion: 0.29
Nodes (6): Lantern 視覺系統（燈下的那一頁）, 原則, 字體分工, 捲軸, 用語, 色彩 token

### Community 8 - "fake_api.py"
Cohesion: 0.16
Nodes (8): _answer(), chat(), claude_messages(), gen(), embeddings(), _err(), files(), _sse()

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "論文卡：備註、星號、排序、複製引用"
Cohesion: 0.33
Nodes (5): 前端（論文卡）, 決定, 論文卡：備註、星號、排序、複製引用, 資料表（`backend/db.py`）, 這次不做

### Community 15 - "test_paper_cards.py"
Cohesion: 0.25
Nodes (6): byline(), _row(), test_byline(), test_cards_scoped_to_owner(), test_cite_cached_and_year(), test_patch_fields_independently()

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.18
Nodes (25): api(), bibtex(), cardsBusy(), enter(), escapeHTML(), importArxiv(), ingest(), loadLibrary() (+17 more)

### Community 18 - "retrieval.py"
Cohesion: 0.15
Nodes (11): embed(), _bm25(), build_index(), make_chunks(), search(), _tokens(), /api/health endpoint, backend/main.py (FastAPI app) (+3 more)

### Community 19 - "drawHighlights"
Cohesion: 0.26
Nodes (14): colorKey(), deleteAnnotation(), drawHighlights(), flashItem(), icon(), isHex(), noteItem(), refreshHighlights() (+6 more)

### Community 20 - "cite.py"
Cohesion: 0.18
Nodes (19): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+11 more)

### Community 21 - "aiCard"
Cohesion: 0.22
Nodes (13): addAnnotation(), aiCard(), closeAiCard(), commentEditor(), explainCrop(), explainImage(), imageFollowup(), openPanel() (+5 more)

### Community 22 - "streamInto"
Cohesion: 0.23
Nodes (13): addAsk(), addCopy(), addMsg(), addSave(), loadChat(), renderMD(), renderWiki(), runSummary() (+5 more)

### Community 23 - "pumpTranslation"
Cohesion: 0.24
Nodes (12): buildPages(), drawRail(), drawTranslation(), fitText(), pumpTranslation(), queueTranslation(), renderPage(), setTrMode() (+4 more)

### Community 24 - "_ingest"
Cohesion: 0.15
Nodes (13): add_to_workspace(), get_paper(), get_settings(), add_to_workspace(), _auto_wiki(), _block_translation(), _ingest(), PaperRefIn (+5 more)

### Community 25 - "backend/__init__.py"
Cohesion: 0.21
Nodes (9): wiki_mark_ingested(), wiki_page(), wiki_pages(), wiki_pending(), update_wiki(), wiki_ask_messages(), wiki(), wiki_page() (+1 more)

### Community 26 - "drawOutline"
Cohesion: 0.25
Nodes (8): drawOutline(), goToPage(), hideFigure(), markOutline(), openCite(), renderOutline(), setLibDrawer(), showFigure()

### Community 27 - "多使用者論文庫 + Workspace（測試登入版）"
Cohesion: 0.20
Nodes (8): _mark_in_library(), Workspace API, 前端畫面, 多使用者論文庫 + Workspace（測試登入版）, 決定, 範圍限制, 資料表（`backend/db.py`）, 這次不做

### Community 28 - "s2_get"
Cohesion: 0.19
Nodes (7): _check(), recommend(), s2_get(), s2_paper_id(), S2Error, recommendations(), API

### Community 29 - "main.py"
Cohesion: 0.11
Nodes (26): add_message(), get_user(), list_messages(), stream_chat(), add_annotation(), AnnotIn, ArxivIn, AskIn (+18 more)

### Community 30 - "sse"
Cohesion: 0.15
Nodes (14): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+6 more)

### Community 31 - "conftest.py"
Cohesion: 0.16
Nodes (6): bob(), client(), fake_server(), _free_port(), papers(), pdfs()

### Community 32 - "chat_messages"
Cohesion: 0.14
Nodes (13): chat_messages(), cite_reason_messages(), citing_contexts(), _est_tokens(), full_text_fits(), _header(), _pages_text(), _paper_body() (+5 more)

### Community 33 - "_ws_or_404"
Cohesion: 0.16
Nodes (14): clear_messages(), clear_wiki_messages(), delete_paper(), delete_workspace(), list_wiki_messages(), remove_from_workspace(), chat_clear(), delete() (+6 more)

### Community 34 - "edit_annotation"
Cohesion: 0.15
Nodes (12): annotation_paper(), rename_workspace(), update_annotation(), update_paper(), CommentIn, edit_annotation(), edit_paper(), NameIn (+4 more)

### Community 35 - "paintWsCards"
Cohesion: 0.18
Nodes (12): cardPaper(), fmtDate(), focusWikiTitle(), loadAsk(), loadWiki(), openNote(), openWikiPage(), paintWsCards() (+4 more)

### Community 36 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

### Community 37 - "asyncio"
Cohesion: 0.18
Nodes (7): stream_block_translation(), run(), _translatable(), ocr_image(), _ocr_pages(), one(), test_translatable()

### Community 38 - "complete_json"
Cohesion: 0.24
Nodes (8): _strip_fence(), _wiki_concept(), _wiki_index(), _wiki_plan(), wiki_qa_page(), complete(), complete_json(), _mock_json()

### Community 41 - "功能對照"
Cohesion: 0.32
Nodes (6): ai_outline(), explain_messages(), _history_block(), image_messages(), local_context(), 功能對照

### Community 42 - "UX 第一輪（已定案）"
Cohesion: 0.33
Nodes (5): A. 閱讀頁重新排版, B. 研究主題頁與流程, C. 全站主題切換, UX 第一輪（已定案）, 不做

### Community 43 - "auto_highlight"
Cohesion: 0.50
Nodes (4): auto_highlight(), guarded(), one(), _reference_start_page()

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `/api/health endpoint`, `BM25 retrieval` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 218 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `app.js`, `db.py`, `pdf_parse.py`, `llm.py`, `features.py`?**
  _High betweenness centrality (0.307) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05555555555555555 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `功能對照`, `pdf_parse.py`, `llm.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Should `Uid` be split into smaller, more focused modules?**
  _Cohesion score 0.1349527665317139 - nodes in this community are weakly interconnected._
- **Why does `功能對照` connect `功能對照` to `chat_messages`, `db.py`, `Lantern — 個人用 AI 論文閱讀器`, `asyncio`, `features.py`, `pdf_parse.py`, `auto_highlight`, `s2_get`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.09309309309309309 - nodes in this community are weakly interconnected._