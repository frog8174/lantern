# Graph Report - agent-a1d0eed6a976e0e90  (2026-10-31)

## Corpus Check
- 25 files · ~28,880 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .example 1, .css 1)

## Summary
- 647 nodes · 1623 edges · 29 communities (24 shown, 5 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 45 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e22003e5`
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
- _to_claude
- aiCard
- streamInto
- pumpTranslation
- check
- _ThinkStripper
- drawOutline
- renderWsCards
- _stream

## God Nodes (most connected - your core abstractions)
1. `conn()` - 42 edges
2. `_paper_or_404()` - 31 edges
3. `escapeHTML()` - 31 edges
4. `sse()` - 30 edges
5. `_id()` - 27 edges
6. `api()` - 24 edges
7. `_ws_or_404()` - 17 edges
8. `功能對照` - 17 edges
9. `cache_get()` - 16 edges
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

## Communities (29 total, 5 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.06
Nodes (30): AUTO, card, cardPaper(), caretAt(), chatWin, CITE_STYLES, citeStyles, COLORS (+22 more)

### Community 1 - "Frontend App Logic"
Cohesion: 0.05
Nodes (86): cache_get(), cache_set(), s2_paper_id(), stream_chat(), add_annotation(), add_to_workspace(), annotations(), AnnotIn (+78 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (39): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+31 more)

### Community 3 - "db.py"
Cohesion: 0.07
Nodes (48): add_annotation(), add_message(), add_paper(), add_to_workspace(), add_wiki_message(), add_workspace(), annotation_paper(), clear_messages() (+40 more)

### Community 4 - "pdf_parse.py"
Cohesion: 0.07
Nodes (38): stream_block_translation(), run(), _translatable(), _abstract(), apply_ocr(), _author_year_refs(), Block, _clean() (+30 more)

### Community 5 - "llm.py"
Cohesion: 0.18
Nodes (4): _mock_answer(), ocr_image(), one(), vLLM (Qwen3.5-9B)

### Community 6 - "features.py"
Cohesion: 0.05
Nodes (45): ai_outline(), auto_highlight(), guarded(), one(), chat_messages(), _check(), cite_reason_messages(), citing_contexts() (+37 more)

### Community 7 - "retrieval.py"
Cohesion: 0.14
Nodes (10): embed(), _bm25(), build_index(), make_chunks(), _tokens(), /api/health endpoint, backend/main.py (FastAPI app), BM25 retrieval (+2 more)

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
Cohesion: 0.15
Nodes (30): addAsk(), addSave(), api(), bibtex(), closeAiCard(), enter(), escapeHTML(), importArxiv() (+22 more)

### Community 18 - "多使用者論文庫 + Workspace（測試登入版）"
Cohesion: 0.20
Nodes (8): _mark_in_library(), Workspace API, 前端畫面, 多使用者論文庫 + Workspace（測試登入版）, 決定, 範圍限制, 資料表（`backend/db.py`）, 這次不做

### Community 19 - "drawHighlights"
Cohesion: 0.26
Nodes (14): colorKey(), deleteAnnotation(), drawHighlights(), flashItem(), icon(), isHex(), noteItem(), refreshHighlights() (+6 more)

### Community 20 - "_to_claude"
Cohesion: 0.22
Nodes (6): _claude(), _claude_block(), _claude_stream(), _to_claude(), test_cache_breakpoint_only_for_multi_turn(), test_to_claude_conversion()

### Community 21 - "aiCard"
Cohesion: 0.27
Nodes (11): addAnnotation(), aiCard(), commentEditor(), explainCrop(), explainImage(), imageFollowup(), openPanel(), qa() (+3 more)

### Community 22 - "streamInto"
Cohesion: 0.36
Nodes (8): addCopy(), addMsg(), loadChat(), renderMD(), runSummary(), sendChat(), stream(), streamInto()

### Community 23 - "pumpTranslation"
Cohesion: 0.31
Nodes (10): buildPages(), drawTranslation(), fitText(), pumpTranslation(), queueTranslation(), renderPage(), setTrMode(), syncTwin() (+2 more)

### Community 24 - "check"
Cohesion: 0.29
Nodes (4): check(), route(), _test_image(), test_route_prefixes()

### Community 26 - "drawOutline"
Cohesion: 0.40
Nodes (5): drawOutline(), goToPage(), hideFigure(), renderOutline(), showFigure()

### Community 27 - "renderWsCards"
Cohesion: 0.29
Nodes (7): cardsBusy(), focusWikiTitle(), openCite(), openWikiPage(), renderWsCards(), setWsTab(), showWs()

### Community 28 - "_stream"
Cohesion: 0.40
Nodes (5): _build(), _create(), _stream(), test_build_adjustments(), test_build_default_sends_vllm_params()

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `ParsedPaper structure`, `vLLM (Qwen3.5-9B)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 187 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `app.js`, `db.py`, `pdf_parse.py`, `llm.py`, `features.py`?**
  _High betweenness centrality (0.324) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06072874493927125 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `_ThinkStripper`, `pdf_parse.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Should `Frontend App Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.05200637404027234 - nodes in this community are weakly interconnected._
- **Why does `功能對照` connect `pdf_parse.py` to `llm.py`, `db.py`, `Lantern — 個人用 AI 論文閱讀器`, `features.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._