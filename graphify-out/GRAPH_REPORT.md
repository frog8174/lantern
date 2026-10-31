# Graph Report - agent-a73601610a330c945  (2026-10-31)

## Corpus Check
- 23 files · ~25,145 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .example 1, .css 1)

## Summary
- 570 nodes · 1395 edges · 21 communities (15 shown, 6 thin omitted)
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
- pdf_parse.py
- llm.py
- features.py
- test_workspaces.py
- fake_api.py
- Frontend UI Layout
- Static File Caching
- Graphify Graph Output
- Lantern Paper Reader
- Lantern — 個人用 AI 論文閱讀器
- CLAUDE.md
- conftest.py
- test_units.py
- check
- _to_claude
- Workspace LLM Wiki（MVP）
- _ThinkStripper

## God Nodes (most connected - your core abstractions)
1. `conn()` - 32 edges
2. `_paper_or_404()` - 30 edges
3. `sse()` - 27 edges
4. `_id()` - 27 edges
5. `escapeHTML()` - 25 edges
6. `api()` - 19 edges
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

## Communities (21 total, 6 thin omitted)

### Community 0 - "Database and API Routes"
Cohesion: 0.05
Nodes (96): addAnnotation(), addCopy(), addMsg(), aiCard(), api(), AUTO, bibtex(), buildPages() (+88 more)

### Community 1 - "Frontend App Logic"
Cohesion: 0.07
Nodes (69): cache_get(), cache_set(), stream_chat(), add_annotation(), add_to_workspace(), annotations(), AnnotIn, ArxivIn (+61 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (39): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+31 more)

### Community 3 - "db.py"
Cohesion: 0.08
Nodes (41): add_annotation(), add_message(), add_paper(), add_to_workspace(), add_workspace(), annotation_paper(), clear_messages(), conn() (+33 more)

### Community 4 - "pdf_parse.py"
Cohesion: 0.06
Nodes (40): stream_block_translation(), run(), embed(), ocr_image(), _ingest(), _ocr_pages(), one(), _abstract() (+32 more)

### Community 5 - "llm.py"
Cohesion: 0.18
Nodes (6): ai_outline(), complete(), complete_json(), _mock_answer(), _mock_json(), vLLM (Qwen3.5-9B)

### Community 6 - "features.py"
Cohesion: 0.08
Nodes (30): auto_highlight(), guarded(), one(), chat_messages(), _check(), cite_reason_messages(), citing_contexts(), _est_tokens() (+22 more)

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

### Community 16 - "test_units.py"
Cohesion: 0.18
Nodes (9): _translatable(), _build(), llm._ThinkStripper, test_build_adjustments(), test_build_default_sends_vllm_params(), test_parse_numeric(), test_scanned_detection(), test_think_stripper() (+1 more)

### Community 17 - "check"
Cohesion: 0.21
Nodes (7): check(), _create(), route(), _stream(), _test_image(), health(), test_route_prefixes()

### Community 18 - "_to_claude"
Cohesion: 0.22
Nodes (6): _claude(), _claude_block(), _claude_stream(), _to_claude(), test_cache_breakpoint_only_for_multi_turn(), test_to_claude_conversion()

### Community 19 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.22
Nodes (8): API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定, 資料表（`backend/db.py`）, 這次不做, 頁面種類與 slug

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `ParsedPaper structure`, `Semantic Scholar API` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 168 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `pdf_parse.py` to `Database and API Routes`, `db.py`, `llm.py`, `features.py`?**
  _High betweenness centrality (0.315) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Database and API Routes` be split into smaller, more focused modules?**
  _Cohesion score 0.05022404779686333 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `pdf_parse.py`, `_ThinkStripper`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Should `Frontend App Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.06736741519350214 - nodes in this community are weakly interconnected._
- **Why does `功能對照` connect `pdf_parse.py` to `llm.py`, `db.py`, `Lantern — 個人用 AI 論文閱讀器`, `features.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._