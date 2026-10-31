# Graph Report - agent-ab18f88d9f36fa63f  (2026-10-31)

## Corpus Check
- 21 files · ~22,695 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .example 1, .css 1)

## Summary
- 508 nodes · 1195 edges · 16 communities (12 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 37 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f4502214`
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
- retrieval.py
- Lantern — 個人用 AI 論文閱讀器
- CLAUDE.md

## God Nodes (most connected - your core abstractions)
1. `sse()` - 27 edges
2. `_id()` - 27 edges
3. `_paper_or_404()` - 24 edges
4. `escapeHTML()` - 22 edges
5. `conn()` - 20 edges
6. `api()` - 17 edges
7. `功能對照` - 17 edges
8. `parse_pdf()` - 16 edges
9. `cache_get()` - 14 edges
10. `cache_set()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `前端畫面` --references--> `api()`  [INFERRED]
  docs/workspaces.md → frontend/app.js
- `功能對照` --references--> `search_chunks()`  [INFERRED]
  README.md → backend/db.py
- `功能對照` --references--> `explain_messages()`  [INFERRED]
  README.md → backend/features.py
- `功能對照` --references--> `translate_messages()`  [INFERRED]
  README.md → backend/features.py
- `功能對照` --references--> `stream_block_translation()`  [INFERRED]
  README.md → backend/features.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (16 total, 4 thin omitted)

### Community 0 - "Database and API Routes"
Cohesion: 0.05
Nodes (90): addAnnotation(), addCopy(), addMsg(), aiCard(), api(), AUTO, bibtex(), buildPages() (+82 more)

### Community 1 - "Frontend App Logic"
Cohesion: 0.07
Nodes (52): cache_get(), cache_set(), _check(), recommend(), s2_get(), s2_paper_id(), add_annotation(), annotations() (+44 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (40): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+32 more)

### Community 3 - "LLM Provider Client"
Cohesion: 0.09
Nodes (30): add_annotation(), add_message(), add_paper(), clear_messages(), conn(), delete_annotation(), delete_paper(), get_paper() (+22 more)

### Community 4 - "PDF Parsing and Citations"
Cohesion: 0.08
Nodes (34): citing_contexts(), _translatable(), _build(), _abstract(), apply_ocr(), _author_year_refs(), Block, _clean() (+26 more)

### Community 5 - "AI Feature Prompts"
Cohesion: 0.08
Nodes (24): ai_outline(), stream_block_translation(), run(), check(), _claude(), _claude_block(), _claude_stream(), complete() (+16 more)

### Community 6 - "Environment Configuration"
Cohesion: 0.10
Nodes (24): auto_highlight(), guarded(), one(), chat_messages(), cite_reason_messages(), _est_tokens(), explain_messages(), full_text_fits() (+16 more)

### Community 7 - "Fake LLM API Server"
Cohesion: 0.10
Nodes (11): _load_dotenv(), client(), fake_server(), _free_port(), papers(), pdfs(), authoryear(), make_all() (+3 more)

### Community 8 - "RAG Retrieval and BM25"
Cohesion: 0.16
Nodes (8): _answer(), chat(), claude_messages(), gen(), embeddings(), _err(), files(), _sse()

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "retrieval.py"
Cohesion: 0.14
Nodes (11): embed(), _bm25(), build_index(), make_chunks(), search(), _tokens(), /api/health endpoint, backend/main.py (FastAPI app) (+3 more)

### Community 14 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.11
Nodes (13): _ThinkStripper, Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 名詞解釋, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API (+5 more)

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `/api/health endpoint`, `BM25 retrieval` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 150 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `Database and API Routes`, `LLM Provider Client`, `PDF Parsing and Citations`, `AI Feature Prompts`, `Environment Configuration`?**
  _High betweenness centrality (0.328) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Database and API Routes` be split into smaller, more focused modules?**
  _Cohesion score 0.05280875236692615 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `PDF Parsing and Citations`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Should `Frontend App Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.06561859193438141 - nodes in this community are weakly interconnected._
- **Why does `功能對照` connect `PDF Parsing and Citations` to `Frontend App Logic`, `LLM Provider Client`, `AI Feature Prompts`, `Environment Configuration`, `Lantern — 個人用 AI 論文閱讀器`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.06721215663354763 - nodes in this community are weakly interconnected._