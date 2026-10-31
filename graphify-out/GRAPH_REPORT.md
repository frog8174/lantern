# Graph Report - paper-reader  (2026-10-31)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 474 nodes · 1122 edges · 13 communities (10 shown, 3 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.81)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e9e01f1f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Database and API Routes
- Frontend App Logic
- Anthropic Provider Tests
- LLM Provider Client
- PDF Parsing and Citations
- AI Feature Prompts
- Environment Configuration
- Fake LLM API Server
- RAG Retrieval and BM25
- Frontend UI Layout
- Static File Caching
- Graphify Graph Output
- Lantern Paper Reader

## God Nodes (most connected - your core abstractions)
1. `sse()` - 27 edges
2. `_id()` - 27 edges
3. `_paper_or_404()` - 24 edges
4. `conn()` - 20 edges
5. `escapeHTML()` - 19 edges
6. `parse_pdf()` - 15 edges
7. `cache_get()` - 14 edges
8. `cache_set()` - 14 edges
9. `stream_chat()` - 14 edges
10. `drawHighlights()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `test_route_prefixes()` --calls--> `route()`  [EXTRACTED]
  tests/test_anthropic.py → backend/llm.py
- `test_think_stripper()` --calls--> `_ThinkStripper`  [EXTRACTED]
  tests/test_units.py → backend/llm.py
- `test_parse_numeric()` --calls--> `parse_pdf()`  [EXTRACTED]
  tests/test_units.py → backend/pdf_parse.py
- `test_scanned_detection()` --calls--> `parse_pdf()`  [EXTRACTED]
  tests/test_units.py → backend/pdf_parse.py
- `test_page_blocks_and_render()` --calls--> `render_page_png()`  [EXTRACTED]
  tests/test_units.py → backend/pdf_parse.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (13 total, 3 thin omitted)

### Community 0 - "Database and API Routes"
Cohesion: 0.06
Nodes (82): addAnnotation(), addCopy(), addMsg(), aiCard(), api(), AUTO, bibtex(), buildPages() (+74 more)

### Community 1 - "Frontend App Logic"
Cohesion: 0.07
Nodes (49): cache_get(), cache_set(), s2_paper_id(), add_annotation(), annotations(), AnnotIn, ArxivIn, auto_highlight() (+41 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (40): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+32 more)

### Community 3 - "LLM Provider Client"
Cohesion: 0.07
Nodes (34): add_annotation(), add_message(), add_paper(), clear_messages(), conn(), delete_annotation(), delete_paper(), get_paper() (+26 more)

### Community 4 - "PDF Parsing and Citations"
Cohesion: 0.08
Nodes (33): citing_contexts(), _translatable(), _build(), _abstract(), apply_ocr(), _author_year_refs(), Block, _clean() (+25 more)

### Community 5 - "AI Feature Prompts"
Cohesion: 0.06
Nodes (25): ai_outline(), stream_block_translation(), run(), check(), _claude(), _claude_block(), _claude_stream(), complete() (+17 more)

### Community 6 - "Environment Configuration"
Cohesion: 0.09
Nodes (25): auto_highlight(), guarded(), one(), chat_messages(), _check(), cite_reason_messages(), _est_tokens(), explain_messages() (+17 more)

### Community 7 - "Fake LLM API Server"
Cohesion: 0.10
Nodes (11): _load_dotenv(), client(), fake_server(), _free_port(), papers(), pdfs(), authoryear(), make_all() (+3 more)

### Community 8 - "RAG Retrieval and BM25"
Cohesion: 0.16
Nodes (8): _answer(), chat(), claude_messages(), gen(), embeddings(), _err(), files(), _sse()

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `/api/health endpoint`, `BM25 retrieval` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 133 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `LLM Provider Client` to `Database and API Routes`, `PDF Parsing and Citations`, `AI Feature Prompts`, `Environment Configuration`?**
  _High betweenness centrality (0.334) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Database and API Routes` be split into smaller, more focused modules?**
  _Cohesion score 0.05593008739076155 - nodes in this community are weakly interconnected._
- **Why does `Lantern index.html` connect `Frontend UI Layout` to `Database and API Routes`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Should `Frontend App Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.07081377151799687 - nodes in this community are weakly interconnected._
- **Why does `sse()` connect `Anthropic Provider Tests` to `LLM Provider Client`, `Fake LLM API Server`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.06721215663354763 - nodes in this community are weakly interconnected._