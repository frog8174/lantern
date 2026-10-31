# Graph Report - paper-reader  (2026-11-01)

## Corpus Check
- 32 files · ~33,842 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .example 1, .css 1)

## Summary
- 759 nodes · 1876 edges · 42 communities (36 shown, 6 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 48 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9957d988`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- features.py
- Anthropic Provider Tests
- db.py
- re
- asyncio
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
- llm.py
- update_wiki
- drawOutline
- 登入系統：Keycloak（OIDC）
- auto_highlight
- main.py
- _ingest
- conftest.py
- s2_get
- _to_claude
- complete_json
- paintWsCards
- Lantern — 個人用 AI 論文閱讀器
- json
- _ThinkStripper
- _stream
- asyncio
- UX 第一輪（已定案）

## God Nodes (most connected - your core abstractions)
1. `conn()` - 44 edges
2. `_paper_or_404()` - 33 edges
3. `escapeHTML()` - 33 edges
4. `sse()` - 29 edges
5. `api()` - 28 edges
6. `_id()` - 27 edges
7. `_ws_or_404()` - 18 edges
8. `_ingest()` - 18 edges
9. `openPaper()` - 18 edges
10. `cache_get()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `資料表（`backend/db.py`）` --references--> `list_papers()`  [INFERRED]
  docs/paper-cards.md → backend/db.py
- `API` --references--> `_ws_or_404()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `更新流程（後端，`features.py` 放 prompt）` --references--> `wiki()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `前端畫面` --references--> `api()`  [INFERRED]
  docs/workspaces.md → frontend/app.js
- `薛西弗斯（等待、完成、空狀態）` --references--> `pushLater()`  [INFERRED]
  docs/design.md → frontend/app.js

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (42 total, 6 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.05
Nodes (30): AUTO, calmMotion, card, caretAt(), CITE_STYLES, citeStyles, COLORS, customColor (+22 more)

### Community 1 - "features.py"
Cohesion: 0.12
Nodes (21): _bib_arxiv(), _bib_llm(), _bib_s2(), chat_messages(), cite_reason_messages(), _est_tokens(), explain_messages(), fetch_bib() (+13 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (39): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+31 more)

### Community 3 - "db.py"
Cohesion: 0.12
Nodes (24): add_annotation(), add_message(), add_wiki_message(), add_workspace(), annotation_paper(), clear_messages(), clear_wiki_messages(), conn() (+16 more)

### Community 4 - "re"
Cohesion: 0.16
Nodes (18): _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), _guess_title(), _is_ref_head(), _is_scanned() (+10 more)

### Community 5 - "asyncio"
Cohesion: 0.25
Nodes (5): check(), route(), _test_image(), health(), test_route_prefixes()

### Community 6 - "test_units.py"
Cohesion: 0.17
Nodes (9): citing_contexts(), _translatable(), llm._ThinkStripper, test_citing_contexts(), test_page_blocks_and_render(), test_parse_numeric(), test_scanned_detection(), test_think_stripper() (+1 more)

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
Cohesion: 0.22
Nodes (7): page_translate_messages(), stream_block_translation(), run(), translate_messages(), find_figures(), 功能對照, test_find_figures()

### Community 15 - "backend/__init__.py"
Cohesion: 0.25
Nodes (6): byline(), _row(), test_byline(), test_cards_scoped_to_owner(), test_cite_cached_and_year(), test_patch_fields_independently()

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.15
Nodes (32): api(), bibtex(), cardsBusy(), enter(), escapeHTML(), importArxiv(), ingest(), loadAsk() (+24 more)

### Community 18 - "retrieval.py"
Cohesion: 0.13
Nodes (13): load_chunks(), save_chunks(), embed(), _bm25(), build_index(), make_chunks(), search(), _tokens() (+5 more)

### Community 19 - "drawHighlights"
Cohesion: 0.25
Nodes (15): addAnnotation(), colorKey(), deleteAnnotation(), drawHighlights(), flashItem(), icon(), isHex(), noteItem() (+7 more)

### Community 20 - "cite.py"
Cohesion: 0.19
Nodes (18): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+10 more)

### Community 21 - "aiCard"
Cohesion: 0.21
Nodes (12): aiCard(), closeAiCard(), commentEditor(), explainCrop(), explainImage(), imageFollowup(), openPanel(), placeFloating() (+4 more)

### Community 22 - "streamInto"
Cohesion: 0.21
Nodes (15): addAsk(), addCopy(), addMsg(), addSave(), loadChat(), pushLater(), reach(), renderMD() (+7 more)

### Community 23 - "pumpTranslation"
Cohesion: 0.24
Nodes (12): buildPages(), drawRail(), drawTranslation(), fitText(), pumpTranslation(), queueTranslation(), renderPage(), setTrMode() (+4 more)

### Community 25 - "update_wiki"
Cohesion: 0.14
Nodes (11): list_wiki_messages(), wiki_mark_ingested(), wiki_page(), wiki_pages(), wiki_pending(), wiki_save(), update_wiki(), wiki_ask_messages() (+3 more)

### Community 26 - "drawOutline"
Cohesion: 0.29
Nodes (7): drawOutline(), goToPage(), hideFigure(), markOutline(), renderOutline(), setLibDrawer(), showFigure()

### Community 27 - "登入系統：Keycloak（OIDC）"
Cohesion: 0.11
Nodes (17): current_user(), _mark_in_library(), k8s 部署要一起處理的事（不處理會壞）, Keycloak 端要建的 client, 建議架構：後端當 OIDC client（Authorization Code + PKCE）, 待確認, 既有資料, 登入系統：Keycloak（OIDC） (+9 more)

### Community 28 - "auto_highlight"
Cohesion: 0.32
Nodes (6): auto_highlight(), guarded(), one(), _reference_start_page(), find_text_rects(), test_find_text_rects()

### Community 29 - "main.py"
Cohesion: 0.05
Nodes (86): cache_get(), cache_set(), s2_paper_id(), stream_chat(), add_annotation(), add_to_workspace(), annotations(), AnnotIn (+78 more)

### Community 30 - "_ingest"
Cohesion: 0.18
Nodes (11): add_paper(), add_to_workspace(), get_paper(), get_settings(), _auto_wiki(), _duplicate(), _first_doi(), _ingest() (+3 more)

### Community 31 - "conftest.py"
Cohesion: 0.06
Nodes (13): _load_dotenv(), allow_duplicates(), bob(), client(), fake_server(), papers(), pdfs(), authoryear() (+5 more)

### Community 32 - "s2_get"
Cohesion: 0.12
Nodes (12): _check(), _guess_ref_title(), lookup_reference(), recommend(), s2_get(), S2Error, API, 前端（論文卡） (+4 more)

### Community 33 - "_to_claude"
Cohesion: 0.22
Nodes (6): _claude(), _claude_block(), _claude_stream(), _to_claude(), test_cache_breakpoint_only_for_multi_turn(), test_to_claude_conversion()

### Community 34 - "complete_json"
Cohesion: 0.22
Nodes (9): ai_outline(), _strip_fence(), _wiki_concept(), _wiki_index(), _wiki_plan(), wiki_qa_page(), complete(), complete_json() (+1 more)

### Community 35 - "paintWsCards"
Cohesion: 0.33
Nodes (7): cardPaper(), fmtDate(), openNote(), paintWsCards(), patchPaper(), showWikiPage(), trRing()

### Community 36 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

### Community 37 - "json"
Cohesion: 0.22
Nodes (6): find_duplicate(), list_annotations(), list_papers(), norm_title(), set_settings(), update_paper()

### Community 39 - "_stream"
Cohesion: 0.40
Nodes (5): _build(), _create(), _stream(), test_build_adjustments(), test_build_default_sends_vllm_params()

### Community 40 - "asyncio"
Cohesion: 0.33
Nodes (3): ocr_image(), _ocr_pages(), one()

### Community 42 - "UX 第一輪（已定案）"
Cohesion: 0.33
Nodes (5): A. 閱讀頁重新排版, B. 研究主題頁與流程, C. 全站主題切換, UX 第一輪（已定案）, 不做

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `/api/health endpoint`, `BM25 retrieval` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 238 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `app.js`, `features.py`, `db.py`, `re`, `llm.py`?**
  _High betweenness centrality (0.325) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.04994192799070848 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `re`, `功能對照`, `_ThinkStripper`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Should `features.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11827956989247312 - nodes in this community are weakly interconnected._
- **Why does `current_user()` connect `登入系統：Keycloak（OIDC）` to `db.py`, `main.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._