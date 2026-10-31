# Graph Report - paper-reader  (2026-10-31)

## Corpus Check
- 24 files · ~28,061 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .example 1, .css 1)

## Summary
- 631 nodes · 1596 edges · 24 communities (20 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 42 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `28125d04`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- Frontend App Logic
- Anthropic Provider Tests
- db.py
- pdf_parse.py
- llm.py
- features.py
- retrieval.py
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
- aiCard
- streamInto
- pumpTranslation
- drawOutline

## God Nodes (most connected - your core abstractions)
1. `conn()` - 42 edges
2. `_paper_or_404()` - 31 edges
3. `escapeHTML()` - 30 edges
4. `sse()` - 30 edges
5. `_id()` - 27 edges
6. `api()` - 22 edges
7. `_ws_or_404()` - 17 edges
8. `功能對照` - 17 edges
9. `cache_get()` - 16 edges
10. `parse_pdf()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `API` --references--> `_ws_or_404()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `更新流程（後端，`features.py` 放 prompt）` --references--> `wiki()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `前端畫面` --references--> `api()`  [INFERRED]
  docs/workspaces.md → frontend/app.js
- `功能對照` --references--> `search_chunks()`  [INFERRED]
  README.md → backend/db.py
- `資料表（`backend/db.py`）` --references--> `delete_paper()`  [INFERRED]
  docs/workspaces.md → backend/db.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (24 total, 4 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.07
Nodes (22): AUTO, card, caretAt(), chatWin, COLORS, customColor, customSw, drop (+14 more)

### Community 1 - "Frontend App Logic"
Cohesion: 0.06
Nodes (80): cache_get(), cache_set(), s2_paper_id(), stream_chat(), add_annotation(), add_to_workspace(), annotations(), AnnotIn (+72 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (39): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+31 more)

### Community 3 - "db.py"
Cohesion: 0.07
Nodes (51): add_annotation(), add_message(), add_paper(), add_to_workspace(), add_wiki_message(), add_workspace(), annotation_paper(), clear_messages() (+43 more)

### Community 4 - "pdf_parse.py"
Cohesion: 0.07
Nodes (38): stream_block_translation(), run(), _translatable(), _abstract(), apply_ocr(), _author_year_refs(), Block, _clean() (+30 more)

### Community 5 - "llm.py"
Cohesion: 0.06
Nodes (23): _build(), check(), _claude(), _claude_block(), _claude_stream(), _create(), _mock_answer(), ocr_image() (+15 more)

### Community 6 - "features.py"
Cohesion: 0.06
Nodes (39): ai_outline(), auto_highlight(), guarded(), one(), chat_messages(), _check(), cite_reason_messages(), citing_contexts() (+31 more)

### Community 7 - "retrieval.py"
Cohesion: 0.15
Nodes (11): embed(), _bm25(), build_index(), make_chunks(), search(), _tokens(), /api/health endpoint, backend/main.py (FastAPI app) (+3 more)

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
Cohesion: 0.07
Nodes (8): _load_dotenv(), bob(), client(), fake_server(), _free_port(), papers(), pdfs(), test_auto_translate_setting()

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.16
Nodes (28): api(), bibtex(), enter(), escapeHTML(), fmtDate(), importArxiv(), ingest(), loadAsk() (+20 more)

### Community 18 - "多使用者論文庫 + Workspace（測試登入版）"
Cohesion: 0.20
Nodes (8): _mark_in_library(), Workspace API, 前端畫面, 多使用者論文庫 + Workspace（測試登入版）, 決定, 範圍限制, 資料表（`backend/db.py`）, 這次不做

### Community 19 - "drawHighlights"
Cohesion: 0.25
Nodes (15): addAnnotation(), colorKey(), deleteAnnotation(), drawHighlights(), flashItem(), icon(), isHex(), noteItem() (+7 more)

### Community 21 - "aiCard"
Cohesion: 0.21
Nodes (12): aiCard(), closeAiCard(), commentEditor(), explainCrop(), explainImage(), imageFollowup(), openPanel(), placeFloating() (+4 more)

### Community 22 - "streamInto"
Cohesion: 0.23
Nodes (13): addAsk(), addCopy(), addMsg(), addSave(), loadChat(), renderMD(), renderWiki(), runSummary() (+5 more)

### Community 23 - "pumpTranslation"
Cohesion: 0.31
Nodes (10): buildPages(), drawTranslation(), fitText(), pumpTranslation(), queueTranslation(), renderPage(), setTrMode(), syncTwin() (+2 more)

### Community 26 - "drawOutline"
Cohesion: 0.33
Nodes (6): drawOutline(), goToPage(), hideFigure(), openCite(), renderOutline(), showFigure()

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `ParsedPaper structure`, `vLLM (Qwen3.5-9B)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 179 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `app.js`, `db.py`, `pdf_parse.py`, `llm.py`, `features.py`?**
  _High betweenness centrality (0.313) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06881720430107527 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `pdf_parse.py`, `llm.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Should `Frontend App Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.05871980250396756 - nodes in this community are weakly interconnected._
- **Why does `功能對照` connect `pdf_parse.py` to `llm.py`, `db.py`, `Lantern — 個人用 AI 論文閱讀器`, `features.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._