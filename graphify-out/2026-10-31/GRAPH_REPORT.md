# Graph Report - paper-reader  (2026-10-31)

## Corpus Check
- 23 files · ~24,672 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .example 1, .css 1)

## Summary
- 565 nodes · 1380 edges · 17 communities (13 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 39 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4479166b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Database and API Routes
- Frontend App Logic
- Anthropic Provider Tests
- db.py
- features.py
- AI Feature Prompts
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

## God Nodes (most connected - your core abstractions)
1. `conn()` - 32 edges
2. `_paper_or_404()` - 30 edges
3. `sse()` - 27 edges
4. `_id()` - 27 edges
5. `escapeHTML()` - 22 edges
6. `api()` - 17 edges
7. `功能對照` - 17 edges
8. `parse_pdf()` - 16 edges
9. `cache_get()` - 15 edges
10. `cache_set()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `API` --references--> `_ws_or_404()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `前端畫面` --references--> `api()`  [INFERRED]
  docs/workspaces.md → frontend/app.js
- `功能對照` --references--> `search_chunks()`  [INFERRED]
  README.md → backend/db.py
- `功能對照` --references--> `explain_messages()`  [INFERRED]
  README.md → backend/features.py
- `功能對照` --references--> `translate_messages()`  [INFERRED]
  README.md → backend/features.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (17 total, 4 thin omitted)

### Community 0 - "Database and API Routes"
Cohesion: 0.05
Nodes (91): addAnnotation(), addCopy(), addMsg(), aiCard(), api(), AUTO, bibtex(), buildPages() (+83 more)

### Community 1 - "Frontend App Logic"
Cohesion: 0.07
Nodes (68): cache_get(), cache_set(), stream_chat(), add_annotation(), add_to_workspace(), annotations(), AnnotIn, ArxivIn (+60 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (39): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+31 more)

### Community 3 - "db.py"
Cohesion: 0.08
Nodes (41): add_annotation(), add_message(), add_paper(), add_to_workspace(), add_workspace(), annotation_paper(), clear_messages(), conn() (+33 more)

### Community 4 - "features.py"
Cohesion: 0.07
Nodes (38): stream_block_translation(), run(), _translatable(), _abstract(), apply_ocr(), _author_year_refs(), Block, _clean() (+30 more)

### Community 5 - "AI Feature Prompts"
Cohesion: 0.06
Nodes (27): ai_outline(), _build(), check(), _claude(), _claude_block(), _claude_stream(), complete(), complete_json() (+19 more)

### Community 6 - "features.py"
Cohesion: 0.08
Nodes (28): auto_highlight(), guarded(), one(), chat_messages(), _check(), cite_reason_messages(), citing_contexts(), _est_tokens() (+20 more)

### Community 7 - "retrieval.py"
Cohesion: 0.09
Nodes (12): embed(), _bm25(), build_index(), make_chunks(), search(), _tokens(), /api/health endpoint, backend/main.py (FastAPI app) (+4 more)

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
Cohesion: 0.10
Nodes (7): _load_dotenv(), bob(), client(), fake_server(), _free_port(), papers(), pdfs()

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.22
Nodes (8): API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定, 資料表（`backend/db.py`）, 這次不做, 頁面種類與 slug

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `ParsedPaper structure`, `Semantic Scholar API` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 167 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `Database and API Routes`, `db.py`, `features.py`, `AI Feature Prompts`, `features.py`?**
  _High betweenness centrality (0.307) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Database and API Routes` be split into smaller, more focused modules?**
  _Cohesion score 0.05215419501133787 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `features.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Should `Frontend App Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.06862026862026863 - nodes in this community are weakly interconnected._
- **Why does `功能對照` connect `features.py` to `AI Feature Prompts`, `db.py`, `Lantern — 個人用 AI 論文閱讀器`, `features.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._