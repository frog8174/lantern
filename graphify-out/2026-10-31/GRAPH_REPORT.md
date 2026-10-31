# Graph Report - paper-reader  (2026-10-31)

## Corpus Check
- 24 files · ~26,293 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .example 1, .css 1)

## Summary
- 594 nodes · 1476 edges · 28 communities (24 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 40 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `af56a1ac`
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
- s2_paper_id
- drawHighlights
- complete_json
- aiCard
- streamInto
- pumpTranslation
- local_context
- _to_claude
- drawOutline
- Lantern AI Paper Reader

## God Nodes (most connected - your core abstractions)
1. `conn()` - 38 edges
2. `_paper_or_404()` - 30 edges
3. `sse()` - 29 edges
4. `_id()` - 27 edges
5. `escapeHTML()` - 25 edges
6. `api()` - 19 edges
7. `功能對照` - 17 edges
8. `cache_get()` - 16 edges
9. `parse_pdf()` - 16 edges
10. `cache_set()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `API` --references--> `_ws_or_404()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `更新流程（後端，`features.py` 放 prompt）` --references--> `wiki()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `前端畫面` --references--> `api()`  [INFERRED]
  docs/workspaces.md → frontend/app.js
- `功能對照` --references--> `search_chunks()`  [INFERRED]
  README.md → backend/db.py
- `功能對照` --references--> `explain_messages()`  [INFERRED]
  README.md → backend/features.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (28 total, 4 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.07
Nodes (20): AUTO, card, caretAt(), chatWin, COLORS, customColor, customSw, drop (+12 more)

### Community 1 - "Frontend App Logic"
Cohesion: 0.06
Nodes (75): cache_get(), cache_set(), s2_paper_id(), stream_chat(), add_annotation(), add_to_workspace(), annotations(), AnnotIn (+67 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (39): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+31 more)

### Community 3 - "db.py"
Cohesion: 0.07
Nodes (48): add_annotation(), add_message(), add_paper(), add_to_workspace(), add_workspace(), annotation_paper(), clear_messages(), conn() (+40 more)

### Community 4 - "pdf_parse.py"
Cohesion: 0.05
Nodes (47): auto_highlight(), guarded(), one(), cite_reason_messages(), citing_contexts(), _reference_start_page(), stream_block_translation(), run() (+39 more)

### Community 5 - "llm.py"
Cohesion: 0.13
Nodes (10): check(), _claude(), _claude_stream(), _create(), _mock_answer(), route(), _stream(), _test_image() (+2 more)

### Community 6 - "features.py"
Cohesion: 0.19
Nodes (13): chat_messages(), _est_tokens(), full_text_fits(), _header(), page_translate_messages(), _pages_text(), _paper_body(), suggested_questions() (+5 more)

### Community 7 - "retrieval.py"
Cohesion: 0.18
Nodes (8): embed(), _bm25(), build_index(), make_chunks(), search(), _tokens(), BM25 retrieval, RAG for long papers

### Community 8 - "fake_api.py"
Cohesion: 0.16
Nodes (8): _answer(), chat(), claude_messages(), gen(), embeddings(), _err(), files(), _sse()

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.11
Nodes (13): _ThinkStripper, Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 名詞解釋, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API (+5 more)

### Community 15 - "conftest.py"
Cohesion: 0.07
Nodes (13): _load_dotenv(), bob(), client(), fake_server(), _free_port(), papers(), pdfs(), authoryear() (+5 more)

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.22
Nodes (8): API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定, 資料表（`backend/db.py`）, 這次不做, 頁面種類與 slug

### Community 17 - "escapeHTML"
Cohesion: 0.18
Nodes (25): api(), bibtex(), enter(), escapeHTML(), fmtDate(), importArxiv(), ingest(), loadLibrary() (+17 more)

### Community 18 - "s2_paper_id"
Cohesion: 0.22
Nodes (6): _check(), _guess_ref_title(), lookup_reference(), recommend(), s2_get(), S2Error

### Community 19 - "drawHighlights"
Cohesion: 0.26
Nodes (14): colorKey(), deleteAnnotation(), drawHighlights(), flashItem(), icon(), isHex(), noteItem(), refreshHighlights() (+6 more)

### Community 20 - "complete_json"
Cohesion: 0.25
Nodes (8): ai_outline(), _strip_fence(), _wiki_concept(), _wiki_index(), _wiki_plan(), complete(), complete_json(), _mock_json()

### Community 21 - "aiCard"
Cohesion: 0.22
Nodes (13): addAnnotation(), aiCard(), closeAiCard(), commentEditor(), explainCrop(), explainImage(), imageFollowup(), openPanel() (+5 more)

### Community 22 - "streamInto"
Cohesion: 0.27
Nodes (10): addCopy(), addMsg(), loadChat(), renderMD(), renderWiki(), runSummary(), sendChat(), shortTitle() (+2 more)

### Community 23 - "pumpTranslation"
Cohesion: 0.31
Nodes (10): buildPages(), drawTranslation(), fitText(), pumpTranslation(), queueTranslation(), renderPage(), setTrMode(), syncTwin() (+2 more)

### Community 24 - "local_context"
Cohesion: 0.40
Nodes (4): explain_messages(), _history_block(), image_messages(), local_context()

### Community 25 - "_to_claude"
Cohesion: 0.40
Nodes (4): _claude_block(), _to_claude(), test_cache_breakpoint_only_for_multi_turn(), test_to_claude_conversion()

### Community 26 - "drawOutline"
Cohesion: 0.40
Nodes (5): drawOutline(), goToPage(), hideFigure(), renderOutline(), showFigure()

### Community 27 - "Lantern AI Paper Reader"
Cohesion: 0.67
Nodes (3): /api/health endpoint, backend/main.py (FastAPI app), Lantern AI Paper Reader

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `ParsedPaper structure`, `vLLM (Qwen3.5-9B)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 171 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `Lantern AI Paper Reader` to `app.js`, `db.py`, `pdf_parse.py`, `llm.py`, `features.py`, `retrieval.py`?**
  _High betweenness centrality (0.308) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.07407407407407407 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `pdf_parse.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Should `Frontend App Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.05998835177635411 - nodes in this community are weakly interconnected._
- **Why does `功能對照` connect `pdf_parse.py` to `db.py`, `features.py`, `Lantern — 個人用 AI 論文閱讀器`, `s2_paper_id`, `complete_json`, `local_context`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._