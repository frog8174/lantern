# Graph Report - paper-reader  (2026-10-31)

## Corpus Check
- 22 files · ~24,250 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .example 1, .css 1)

## Summary
- 555 nodes · 1368 edges · 15 communities (11 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 38 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `26c2afd4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Database and API Routes
- Frontend App Logic
- Anthropic Provider Tests
- db.py
- features.py
- AI Feature Prompts
- retrieval.py
- fake_api.py
- Frontend UI Layout
- Static File Caching
- Graphify Graph Output
- Lantern Paper Reader
- Lantern — 個人用 AI 論文閱讀器
- CLAUDE.md
- conftest.py

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
- `前端畫面` --references--> `api()`  [INFERRED]
  docs/workspaces.md → frontend/app.js
- `功能對照` --references--> `search_chunks()`  [INFERRED]
  README.md → backend/db.py
- `功能對照` --references--> `ai_outline()`  [INFERRED]
  README.md → backend/features.py
- `功能對照` --references--> `recommend()`  [INFERRED]
  README.md → backend/features.py
- `名詞解釋` --references--> `_ThinkStripper`  [INFERRED]
  README.md → backend/llm.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (15 total, 4 thin omitted)

### Community 0 - "Database and API Routes"
Cohesion: 0.05
Nodes (90): addAnnotation(), addCopy(), addMsg(), aiCard(), api(), AUTO, bibtex(), buildPages() (+82 more)

### Community 1 - "Frontend App Logic"
Cohesion: 0.07
Nodes (64): stream_chat(), add_annotation(), add_to_workspace(), annotations(), AnnotIn, ArxivIn, auth_users(), auto_highlight() (+56 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (39): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+31 more)

### Community 3 - "db.py"
Cohesion: 0.06
Nodes (54): add_annotation(), add_message(), add_paper(), add_to_workspace(), add_workspace(), annotation_paper(), cache_get(), cache_set() (+46 more)

### Community 4 - "features.py"
Cohesion: 0.05
Nodes (57): auto_highlight(), guarded(), one(), chat_messages(), cite_reason_messages(), citing_contexts(), _est_tokens(), explain_messages() (+49 more)

### Community 5 - "AI Feature Prompts"
Cohesion: 0.06
Nodes (27): ai_outline(), _build(), check(), _claude(), _claude_block(), _claude_stream(), complete(), complete_json() (+19 more)

### Community 7 - "retrieval.py"
Cohesion: 0.09
Nodes (9): _bm25(), make_chunks(), _tokens(), /api/health endpoint, backend/main.py (FastAPI app), BM25 retrieval, Lantern AI Paper Reader, RAG for long papers (+1 more)

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
Cohesion: 0.09
Nodes (12): _load_dotenv(), bob(), client(), fake_server(), _free_port(), papers(), pdfs(), authoryear() (+4 more)

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `ParsedPaper structure`, `vLLM (Qwen3.5-9B)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 160 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `Database and API Routes`, `db.py`, `features.py`, `AI Feature Prompts`?**
  _High betweenness centrality (0.308) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Database and API Routes` be split into smaller, more focused modules?**
  _Cohesion score 0.05280875236692615 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `features.py`, `AI Feature Prompts`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Should `Frontend App Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.06843090082865544 - nodes in this community are weakly interconnected._
- **Why does `功能對照` connect `features.py` to `AI Feature Prompts`, `db.py`, `Lantern — 個人用 AI 論文閱讀器`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._