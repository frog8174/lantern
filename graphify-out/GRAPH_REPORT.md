# Graph Report - paper-reader  (2026-10-31)

## Corpus Check
- 28 files · ~30,701 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .example 1, .css 1)

## Summary
- 690 nodes · 1738 edges · 37 communities (33 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 46 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6065191a`
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
- _ingest
- fake_api.py
- Frontend UI Layout
- Static File Caching
- Graphify Graph Output
- Lantern Paper Reader
- Lantern — 個人用 AI 論文閱讀器
- CLAUDE.md
- conftest.py
- Workspace LLM Wiki（MVP）
- escapeHTML
- 多使用者論文庫 + Workspace（測試登入版）
- drawHighlights
- cite.py
- aiCard
- streamInto
- pumpTranslation
- post
- _paper_or_404
- drawOutline
- update_wiki
- get_user
- _block_translation
- complete_json
- chat_messages
- s2_get
- local_context
- 論文卡：備註、星號、排序、複製引用
- paintWsCards
- auto_highlight

## God Nodes (most connected - your core abstractions)
1. `conn()` - 42 edges
2. `_paper_or_404()` - 32 edges
3. `escapeHTML()` - 32 edges
4. `sse()` - 30 edges
5. `_id()` - 27 edges
6. `api()` - 24 edges
7. `cache_get()` - 17 edges
8. `_ws_or_404()` - 17 edges
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
- `登入` --references--> `init()`  [INFERRED]
  docs/workspaces.md → backend/db.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (37 total, 4 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.06
Nodes (28): AUTO, card, caretAt(), chatWin, CITE_STYLES, citeStyles, COLORS, customColor (+20 more)

### Community 1 - "main.py"
Cohesion: 0.11
Nodes (34): add_annotation(), add_to_workspace(), AnnotIn, ArxivIn, auth_users(), chat_clear(), CommentIn, create_workspace() (+26 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (39): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+31 more)

### Community 3 - "db.py"
Cohesion: 0.10
Nodes (36): add_annotation(), add_message(), add_paper(), add_to_workspace(), add_wiki_message(), add_workspace(), annotation_paper(), clear_messages() (+28 more)

### Community 4 - "pdf_parse.py"
Cohesion: 0.05
Nodes (48): citing_contexts(), stream_block_translation(), run(), _translatable(), _abstract(), apply_ocr(), _author_year_refs(), Block (+40 more)

### Community 5 - "llm.py"
Cohesion: 0.06
Nodes (24): _build(), check(), _claude(), _claude_block(), _claude_stream(), _create(), _mock_answer(), ocr_image() (+16 more)

### Community 6 - "features.py"
Cohesion: 0.22
Nodes (10): _bib_arxiv(), _bib_llm(), _bib_s2(), fetch_bib(), _guess_ref_title(), lookup_reference(), _name(), page_translate_messages() (+2 more)

### Community 7 - "_ingest"
Cohesion: 0.24
Nodes (7): get_settings(), embed(), _auto_wiki(), _ingest(), upload(), build_index(), search()

### Community 8 - "fake_api.py"
Cohesion: 0.16
Nodes (8): _answer(), chat(), claude_messages(), gen(), embeddings(), _err(), files(), _sse()

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

### Community 15 - "conftest.py"
Cohesion: 0.05
Nodes (15): _load_dotenv(), bob(), client(), fake_server(), _free_port(), papers(), pdfs(), _row() (+7 more)

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.15
Nodes (29): api(), bibtex(), cardsBusy(), closeAiCard(), enter(), escapeHTML(), importArxiv(), ingest() (+21 more)

### Community 18 - "多使用者論文庫 + Workspace（測試登入版）"
Cohesion: 0.18
Nodes (9): _mark_in_library(), Workspace API, 前端畫面, 多使用者論文庫 + Workspace（測試登入版）, 決定, 登入, 範圍限制, 資料表（`backend/db.py`） (+1 more)

### Community 19 - "drawHighlights"
Cohesion: 0.26
Nodes (14): colorKey(), deleteAnnotation(), drawHighlights(), flashItem(), icon(), isHex(), noteItem(), refreshHighlights() (+6 more)

### Community 20 - "cite.py"
Cohesion: 0.19
Nodes (18): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+10 more)

### Community 21 - "aiCard"
Cohesion: 0.27
Nodes (11): addAnnotation(), aiCard(), commentEditor(), explainCrop(), explainImage(), imageFollowup(), openPanel(), qa() (+3 more)

### Community 22 - "streamInto"
Cohesion: 0.23
Nodes (13): addAsk(), addCopy(), addMsg(), addSave(), loadChat(), renderMD(), renderWiki(), runSummary() (+5 more)

### Community 23 - "pumpTranslation"
Cohesion: 0.31
Nodes (10): buildPages(), drawTranslation(), fitText(), pumpTranslation(), queueTranslation(), renderPage(), setTrMode(), syncTwin() (+2 more)

### Community 24 - "post"
Cohesion: 0.13
Nodes (16): wiki_pages(), wiki_ask_messages(), stream_chat(), AskIn, chat(), ChatIn, explain(), explain_image() (+8 more)

### Community 25 - "_paper_or_404"
Cohesion: 0.13
Nodes (26): cache_get(), cache_set(), s2_paper_id(), annotations(), _cached_text(), chat_history(), cite_paper(), figure_png() (+18 more)

### Community 26 - "drawOutline"
Cohesion: 0.40
Nodes (5): drawOutline(), goToPage(), hideFigure(), renderOutline(), showFigure()

### Community 27 - "update_wiki"
Cohesion: 0.33
Nodes (5): wiki_pending(), update_wiki(), _wiki_plan(), _wiki_slug(), _wiki_job()

### Community 28 - "get_user"
Cohesion: 0.67
Nodes (3): get_user(), current_user(), me()

### Community 29 - "_block_translation"
Cohesion: 0.33
Nodes (4): _block_translation(), PageIn, _pretranslate(), translate_blocks()

### Community 30 - "complete_json"
Cohesion: 0.20
Nodes (9): ai_outline(), _strip_fence(), suggested_questions(), _wiki_concept(), _wiki_index(), wiki_qa_page(), complete(), complete_json() (+1 more)

### Community 31 - "chat_messages"
Cohesion: 0.21
Nodes (10): chat_messages(), cite_reason_messages(), _est_tokens(), full_text_fits(), _header(), _pages_text(), _paper_body(), summary_messages() (+2 more)

### Community 32 - "s2_get"
Cohesion: 0.25
Nodes (5): _check(), recommend(), s2_get(), S2Error, API

### Community 33 - "local_context"
Cohesion: 0.40
Nodes (4): explain_messages(), _history_block(), image_messages(), local_context()

### Community 34 - "論文卡：備註、星號、排序、複製引用"
Cohesion: 0.33
Nodes (5): 前端（論文卡）, 決定, 論文卡：備註、星號、排序、複製引用, 資料表（`backend/db.py`）, 這次不做

### Community 35 - "paintWsCards"
Cohesion: 0.40
Nodes (6): cardPaper(), fmtDate(), openNote(), paintWsCards(), patchPaper(), trRing()

### Community 36 - "auto_highlight"
Cohesion: 0.50
Nodes (4): auto_highlight(), guarded(), one(), _reference_start_page()

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `ParsedPaper structure`, `vLLM (Qwen3.5-9B)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 197 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `pdf_parse.py` to `app.js`, `db.py`, `llm.py`, `features.py`?**
  _High betweenness centrality (0.311) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06006006006006006 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `pdf_parse.py`, `llm.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10782241014799154 - nodes in this community are weakly interconnected._
- **Why does `功能對照` connect `pdf_parse.py` to `s2_get`, `local_context`, `db.py`, `auto_highlight`, `llm.py`, `features.py`, `Lantern — 個人用 AI 論文閱讀器`, `complete_json`, `chat_messages`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._