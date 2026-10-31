# Graph Report - agent-a7de873ad2204d222  (2026-10-31)

## Corpus Check
- 22 files · ~23,258 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .example 1, .css 1)

## Summary
- 552 nodes · 1326 edges · 15 communities (11 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 36 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f4502214`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Database and API Routes
- Frontend App Logic
- Anthropic Provider Tests
- db.py
- PDF Parsing and Citations
- AI Feature Prompts
- Environment Configuration
- retrieval.py
- conftest.py
- Frontend UI Layout
- Static File Caching
- Graphify Graph Output
- Lantern Paper Reader
- Lantern — 個人用 AI 論文閱讀器
- CLAUDE.md

## God Nodes (most connected - your core abstractions)
1. `conn()` - 30 edges
2. `_paper_or_404()` - 30 edges
3. `sse()` - 28 edges
4. `_id()` - 27 edges
5. `escapeHTML()` - 19 edges
6. `功能對照` - 17 edges
7. `parse_pdf()` - 16 edges
8. `cache_get()` - 14 edges
9. `cache_set()` - 14 edges
10. `stream_chat()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `前端畫面` --references--> `api()`  [INFERRED]
  docs/workspaces.md → frontend/app.js
- `功能對照` --references--> `search_chunks()`  [INFERRED]
  README.md → backend/db.py
- `名詞解釋` --references--> `_ThinkStripper`  [INFERRED]
  README.md → backend/llm.py
- `範圍限制` --references--> `_mark_in_library()`  [INFERRED]
  docs/workspaces.md → backend/main.py
- `功能對照` --references--> `find_figures()`  [INFERRED]
  README.md → backend/pdf_parse.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (15 total, 4 thin omitted)

### Community 0 - "Database and API Routes"
Cohesion: 0.06
Nodes (82): addAnnotation(), addCopy(), addMsg(), aiCard(), api(), AUTO, bibtex(), buildPages() (+74 more)

### Community 1 - "Frontend App Logic"
Cohesion: 0.06
Nodes (61): stream_chat(), add_annotation(), add_to_workspace(), annotations(), AnnotIn, ArxivIn, auth_users(), auto_highlight() (+53 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (39): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+31 more)

### Community 3 - "db.py"
Cohesion: 0.06
Nodes (48): add_annotation(), add_message(), add_paper(), add_to_workspace(), add_workspace(), annotation_paper(), cache_get(), cache_set() (+40 more)

### Community 4 - "PDF Parsing and Citations"
Cohesion: 0.08
Nodes (34): citing_contexts(), _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), find_figures(), find_text_rects() (+26 more)

### Community 5 - "AI Feature Prompts"
Cohesion: 0.06
Nodes (24): _build(), check(), _claude(), _claude_block(), _claude_stream(), complete(), complete_json(), _create() (+16 more)

### Community 6 - "Environment Configuration"
Cohesion: 0.07
Nodes (34): ai_outline(), auto_highlight(), guarded(), one(), chat_messages(), _check(), cite_reason_messages(), _est_tokens() (+26 more)

### Community 7 - "retrieval.py"
Cohesion: 0.07
Nodes (9): _load_dotenv(), _bm25(), make_chunks(), _tokens(), /api/health endpoint, backend/main.py (FastAPI app), BM25 retrieval, Lantern AI Paper Reader (+1 more)

### Community 8 - "conftest.py"
Cohesion: 0.08
Nodes (14): bob(), client(), fake_server(), _free_port(), papers(), pdfs(), _answer(), chat() (+6 more)

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `/api/health endpoint`, `BM25 retrieval` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 169 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `Database and API Routes`, `db.py`, `PDF Parsing and Citations`, `AI Feature Prompts`, `Environment Configuration`?**
  _High betweenness centrality (0.292) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Database and API Routes` be split into smaller, more focused modules?**
  _Cohesion score 0.05593008739076155 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `PDF Parsing and Citations`, `AI Feature Prompts`, `Environment Configuration`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Should `Frontend App Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.06460674157303371 - nodes in this community are weakly interconnected._
- **Why does `功能對照` connect `Environment Configuration` to `db.py`, `PDF Parsing and Citations`, `Lantern — 個人用 AI 論文閱讀器`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.06836055656382335 - nodes in this community are weakly interconnected._