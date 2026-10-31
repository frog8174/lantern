# Graph Report - paper-reader  (2026-10-31)

## Corpus Check
- 29 files · ~31,565 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .example 1, .css 1)

## Summary
- 712 nodes · 1779 edges · 32 communities (27 shown, 5 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 46 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `931fb672`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- main.py
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
- config.py
- Workspace LLM Wiki（MVP）
- escapeHTML
- retrieval.py
- drawHighlights
- cite.py
- aiCard
- escapeHTML
- pumpTranslation
- _ingest
- backend/__init__.py
- drawOutline
- 多使用者論文庫 + Workspace（測試登入版）
- list_papers
- addMsg
- wiki_backlinks
- paintWsCards

## God Nodes (most connected - your core abstractions)
1. `conn()` - 43 edges
2. `_paper_or_404()` - 33 edges
3. `escapeHTML()` - 32 edges
4. `sse()` - 30 edges
5. `_id()` - 27 edges
6. `api()` - 25 edges
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

## Communities (32 total, 5 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.06
Nodes (27): AUTO, card, caretAt(), chatWin, CITE_STYLES, citeStyles, COLORS, customColor (+19 more)

### Community 1 - "main.py"
Cohesion: 0.06
Nodes (84): cache_get(), cache_set(), stream_chat(), add_annotation(), add_to_workspace(), annotations(), AnnotIn, ArxivIn (+76 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (39): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+31 more)

### Community 3 - "db.py"
Cohesion: 0.12
Nodes (28): add_annotation(), add_message(), add_wiki_message(), add_workspace(), annotation_paper(), clear_messages(), clear_wiki_messages(), conn() (+20 more)

### Community 4 - "pdf_parse.py"
Cohesion: 0.07
Nodes (36): citing_contexts(), _translatable(), _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), find_figures() (+28 more)

### Community 5 - "llm.py"
Cohesion: 0.05
Nodes (31): _build(), check(), _claude(), _claude_block(), _claude_stream(), _create(), _mock_answer(), _mock_json() (+23 more)

### Community 6 - "features.py"
Cohesion: 0.05
Nodes (50): ai_outline(), auto_highlight(), guarded(), one(), _bib_arxiv(), _bib_llm(), _bib_s2(), chat_messages() (+42 more)

### Community 7 - "Lantern 視覺系統（燈下的那一頁）"
Cohesion: 0.29
Nodes (6): Lantern 視覺系統（燈下的那一頁）, 原則, 字體分工, 捲軸, 用語, 色彩 token

### Community 8 - "fake_api.py"
Cohesion: 0.08
Nodes (14): bob(), client(), fake_server(), _free_port(), papers(), pdfs(), _answer(), chat() (+6 more)

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "論文卡：備註、星號、排序、複製引用"
Cohesion: 0.33
Nodes (5): 前端（論文卡）, 決定, 論文卡：備註、星號、排序、複製引用, 資料表（`backend/db.py`）, 這次不做

### Community 15 - "config.py"
Cohesion: 0.08
Nodes (8): _load_dotenv(), byline(), _row(), test_byline(), test_cards_scoped_to_owner(), test_cite_cached_and_year(), test_patch_fields_independently(), test_auto_translate_setting()

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.17
Nodes (20): api(), cardsBusy(), closeAiCard(), enter(), importArxiv(), ingest(), loadLibrary(), loadPaperWiki() (+12 more)

### Community 18 - "retrieval.py"
Cohesion: 0.15
Nodes (11): embed(), _bm25(), build_index(), make_chunks(), search(), _tokens(), /api/health endpoint, backend/main.py (FastAPI app) (+3 more)

### Community 19 - "drawHighlights"
Cohesion: 0.26
Nodes (14): colorKey(), deleteAnnotation(), drawHighlights(), flashItem(), icon(), isHex(), noteItem(), refreshHighlights() (+6 more)

### Community 20 - "cite.py"
Cohesion: 0.19
Nodes (18): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+10 more)

### Community 21 - "aiCard"
Cohesion: 0.21
Nodes (14): addAnnotation(), aiCard(), commentEditor(), explainCrop(), explainImage(), imageFollowup(), openPanel(), qa() (+6 more)

### Community 22 - "escapeHTML"
Cohesion: 0.22
Nodes (16): addAsk(), addSave(), bibtex(), escapeHTML(), loadAsk(), loadRelated(), loadWiki(), placeFloating() (+8 more)

### Community 23 - "pumpTranslation"
Cohesion: 0.27
Nodes (11): buildPages(), drawTranslation(), fitText(), pumpTranslation(), queueTranslation(), renderPage(), setTrMode(), stream() (+3 more)

### Community 24 - "_ingest"
Cohesion: 0.19
Nodes (10): add_paper(), add_to_workspace(), get_paper(), get_settings(), _auto_wiki(), _ingest(), _prefetch_bib(), _pretranslate() (+2 more)

### Community 25 - "backend/__init__.py"
Cohesion: 0.17
Nodes (8): list_wiki_messages(), wiki_page(), wiki_pages(), wiki_pending(), wiki_ask_messages(), test_auto_wiki(), test_wiki_ask_and_backlinks(), test_wiki_update()

### Community 26 - "drawOutline"
Cohesion: 0.40
Nodes (5): drawOutline(), goToPage(), hideFigure(), renderOutline(), showFigure()

### Community 27 - "多使用者論文庫 + Workspace（測試登入版）"
Cohesion: 0.18
Nodes (10): get_user(), init(), current_user(), Workspace API, 前端畫面, 多使用者論文庫 + Workspace（測試登入版）, 決定, 登入 (+2 more)

### Community 28 - "list_papers"
Cohesion: 0.40
Nodes (4): list_papers(), _mark_in_library(), recommendations(), 範圍限制

### Community 29 - "addMsg"
Cohesion: 0.83
Nodes (4): addCopy(), addMsg(), loadChat(), sendChat()

### Community 35 - "paintWsCards"
Cohesion: 0.40
Nodes (6): cardPaper(), fmtDate(), openNote(), paintWsCards(), patchPaper(), trRing()

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `/api/health endpoint`, `BM25 retrieval` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 211 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `app.js`, `db.py`, `pdf_parse.py`, `llm.py`, `features.py`?**
  _High betweenness centrality (0.303) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.057057057057057055 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `llm.py` to `pdf_parse.py`, `features.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05515170670037927 - nodes in this community are weakly interconnected._
- **Why does `功能對照` connect `features.py` to `db.py`, `pdf_parse.py`, `llm.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._