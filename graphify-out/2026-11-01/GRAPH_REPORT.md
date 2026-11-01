# Graph Report - paper-reader  (2026-11-01)

## Corpus Check
- 33 files · ~34,442 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .example 1, .css 1)

## Summary
- 787 nodes · 1923 edges · 47 communities (42 shown, 5 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 48 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8dcaecb7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- features.py
- Anthropic Provider Tests
- db.py
- re
- asyncio
- citing_contexts
- Lantern 視覺系統（燈下的那一頁）
- fake_api.py
- Frontend UI Layout
- Static File Caching
- Graphify Graph Output
- Lantern Paper Reader
- main.py
- CLAUDE.md
- config.py
- Workspace LLM Wiki（MVP）
- escapeHTML
- retrieval.py
- drawHighlights
- cite.py
- aiCard
- streamInto
- pumpTranslation
- _paper_or_404
- Uid
- drawOutline
- 登入系統：Keycloak（OIDC）
- auto_highlight
- post
- get
- conftest.py
- s2_get
- _to_claude
- complete_json
- paintWsCards
- Lantern — 個人用 AI 論文閱讀器
- test_anthropic.py
- _ThinkStripper
- _build
- asyncio
- import_url
- UX 第一輪（已定案）
- chat_messages
- login
- local_context
- 論文卡：備註、星號、排序、複製引用

## God Nodes (most connected - your core abstractions)
1. `conn()` - 46 edges
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

## Communities (47 total, 5 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.05
Nodes (30): AUTO, calmMotion, card, caretAt(), CITE_STYLES, citeStyles, COLORS, customColor (+22 more)

### Community 1 - "features.py"
Cohesion: 0.20
Nodes (11): _bib_arxiv(), _bib_llm(), _bib_s2(), fetch_bib(), _guess_ref_title(), lookup_reference(), _name(), page_translate_messages() (+3 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.10
Nodes (29): sse(), test_bilingual_blocks(), _id(), test_ai_outline(), test_annotation_kinds(), test_annotations_crud(), test_ask_ai_on_selection(), test_author_year_reference() (+21 more)

### Community 3 - "db.py"
Cohesion: 0.06
Nodes (55): add_annotation(), add_message(), add_paper(), add_to_workspace(), add_wiki_message(), add_workspace(), annotation_paper(), clear_messages() (+47 more)

### Community 4 - "re"
Cohesion: 0.07
Nodes (38): stream_block_translation(), run(), _translatable(), _abstract(), apply_ocr(), _author_year_refs(), Block, _clean() (+30 more)

### Community 5 - "asyncio"
Cohesion: 0.24
Nodes (6): check(), _create(), route(), _stream(), _test_image(), test_route_prefixes()

### Community 6 - "citing_contexts"
Cohesion: 0.50
Nodes (3): cite_reason_messages(), citing_contexts(), test_citing_contexts()

### Community 7 - "Lantern 視覺系統（燈下的那一頁）"
Cohesion: 0.25
Nodes (7): Lantern 視覺系統（燈下的那一頁）, 原則, 字體分工, 捲軸, 用語, 色彩 token, 薛西弗斯（等待、完成、空狀態）

### Community 8 - "fake_api.py"
Cohesion: 0.11
Nodes (12): _answer(), chat(), claude_messages(), gen(), embeddings(), _err(), files(), _sse() (+4 more)

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "main.py"
Cohesion: 0.13
Nodes (13): CommentIn, create_workspace(), edit_annotation(), edit_paper(), get_settings(), NameIn, _own_annotation(), paper() (+5 more)

### Community 15 - "config.py"
Cohesion: 0.06
Nodes (12): _load_dotenv(), byline(), FakeKC, _oidc(), test_oidc_login_creates_user_and_session(), test_oidc_login_failure_redirects(), _row(), test_byline() (+4 more)

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.15
Nodes (32): api(), bibtex(), cardsBusy(), enter(), escapeHTML(), importArxiv(), ingest(), loadAsk() (+24 more)

### Community 18 - "retrieval.py"
Cohesion: 0.15
Nodes (11): embed(), _bm25(), build_index(), make_chunks(), search(), _tokens(), /api/health endpoint, backend/main.py (FastAPI app) (+3 more)

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

### Community 24 - "_paper_or_404"
Cohesion: 0.23
Nodes (15): cache_get(), cache_set(), _block_translation(), _cached_text(), cite_paper(), _ensure_bib(), outline_ai(), _paper_or_404() (+7 more)

### Community 25 - "Uid"
Cohesion: 0.21
Nodes (15): add_to_workspace(), chat_clear(), delete(), delete_workspace(), PaperRefIn, papers(), remove_annotation(), remove_from_workspace() (+7 more)

### Community 26 - "drawOutline"
Cohesion: 0.29
Nodes (7): drawOutline(), goToPage(), hideFigure(), markOutline(), renderOutline(), setLibDrawer(), showFigure()

### Community 27 - "登入系統：Keycloak（OIDC）"
Cohesion: 0.10
Nodes (17): current_user(), _mark_in_library(), k8s 部署要一起處理的事（不處理會壞）, Keycloak 端要建的 client, 建議架構：後端當 OIDC client（Authorization Code + PKCE）, 待確認, 既有資料, 登入系統：Keycloak（OIDC） (+9 more)

### Community 28 - "auto_highlight"
Cohesion: 0.50
Nodes (4): auto_highlight(), guarded(), one(), _reference_start_page()

### Community 29 - "post"
Cohesion: 0.14
Nodes (18): stream_chat(), add_annotation(), AnnotIn, AskIn, chat(), ChatIn, explain(), explain_image() (+10 more)

### Community 30 - "get"
Cohesion: 0.12
Nodes (11): annotations(), auth_config(), auth_users(), chat_history(), health(), livez(), me(), paper_wiki() (+3 more)

### Community 31 - "conftest.py"
Cohesion: 0.13
Nodes (6): allow_duplicates(), bob(), client(), fake_server(), papers(), pdfs()

### Community 32 - "s2_get"
Cohesion: 0.19
Nodes (7): _check(), recommend(), s2_get(), s2_paper_id(), S2Error, recommendations(), API

### Community 33 - "_to_claude"
Cohesion: 0.14
Nodes (8): _claude(), _claude_block(), _claude_stream(), _mock_answer(), _to_claude(), vLLM (Qwen3.5-9B), test_cache_breakpoint_only_for_multi_turn(), test_to_claude_conversion()

### Community 34 - "complete_json"
Cohesion: 0.15
Nodes (11): ai_outline(), _strip_fence(), suggested_questions(), wiki_ask_messages(), _wiki_concept(), _wiki_index(), _wiki_plan(), wiki_qa_page() (+3 more)

### Community 35 - "paintWsCards"
Cohesion: 0.33
Nodes (7): cardPaper(), fmtDate(), openNote(), paintWsCards(), patchPaper(), showWikiPage(), trRing()

### Community 36 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

### Community 37 - "test_anthropic.py"
Cohesion: 0.18
Nodes (10): claude(), _pid(), test_auto_highlight_json(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape(), test_mixed_providers(), test_no_fallback_for_haiku() (+2 more)

### Community 39 - "_build"
Cohesion: 0.67
Nodes (3): _build(), test_build_adjustments(), test_build_default_sends_vllm_params()

### Community 40 - "asyncio"
Cohesion: 0.33
Nodes (3): ocr_image(), _ocr_pages(), one()

### Community 41 - "import_url"
Cohesion: 0.15
Nodes (10): ArxivIn, auto_highlight(), figure_png(), figures(), _figures(), import_url(), paper_pdf(), paper_thumb() (+2 more)

### Community 42 - "UX 第一輪（已定案）"
Cohesion: 0.33
Nodes (5): A. 閱讀頁重新排版, B. 研究主題頁與流程, C. 全站主題切換, UX 第一輪（已定案）, 不做

### Community 43 - "chat_messages"
Cohesion: 0.27
Nodes (8): chat_messages(), _est_tokens(), full_text_fits(), _header(), _pages_text(), _paper_body(), summary_messages(), _wiki_source()

### Community 44 - "login"
Cohesion: 0.20
Nodes (5): login(), LoginIn, logout(), oidc_callback(), oidc_login()

### Community 45 - "local_context"
Cohesion: 0.40
Nodes (4): explain_messages(), _history_block(), image_messages(), local_context()

### Community 46 - "論文卡：備註、星號、排序、複製引用"
Cohesion: 0.33
Nodes (5): 前端（論文卡）, 決定, 論文卡：備註、星號、排序、複製引用, 資料表（`backend/db.py`）, 這次不做

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `Semantic Scholar API`, `graphify-out/graph.json`, `graphify usage rules`, `/api/health endpoint` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 254 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `app.js`, `features.py`, `_to_claude`, `db.py`, `re`?**
  _High betweenness centrality (0.316) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `Semantic Scholar API`, `graphify-out/graph.json` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.04994192799070848 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `re`, `_ThinkStripper`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.10128205128205128 - nodes in this community are weakly interconnected._
- **Why does `current_user()` connect `登入系統：Keycloak（OIDC）` to `db.py`, `login`, `main.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Should `db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05627705627705628 - nodes in this community are weakly interconnected._