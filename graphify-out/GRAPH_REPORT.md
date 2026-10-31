# Graph Report - paper-reader  (2026-10-31)

## Corpus Check
- 22 files · ~23,966 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .example 1, .css 1)

## Summary
- 546 nodes · 1337 edges · 20 communities (15 shown, 5 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 38 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6defd973`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Database and API Routes
- Frontend App Logic
- Anthropic Provider Tests
- db.py
- pdf_parse.py
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
- test_units.py
- recommend
- auto_highlight
- citing_contexts

## God Nodes (most connected - your core abstractions)
1. `conn()` - 30 edges
2. `_paper_or_404()` - 30 edges
3. `sse()` - 27 edges
4. `_id()` - 27 edges
5. `escapeHTML()` - 22 edges
6. `api()` - 17 edges
7. `功能對照` - 17 edges
8. `parse_pdf()` - 16 edges
9. `cache_get()` - 14 edges
10. `cache_set()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `名詞解釋` --references--> `_ThinkStripper`  [INFERRED]
  README.md → backend/llm.py
- `範圍限制` --references--> `_mark_in_library()`  [INFERRED]
  docs/workspaces.md → backend/main.py
- `前端畫面` --references--> `api()`  [INFERRED]
  docs/workspaces.md → frontend/app.js
- `功能對照` --references--> `search_chunks()`  [INFERRED]
  README.md → backend/db.py
- `功能對照` --references--> `stream_block_translation()`  [INFERRED]
  README.md → backend/features.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (20 total, 5 thin omitted)

### Community 0 - "Database and API Routes"
Cohesion: 0.05
Nodes (90): addAnnotation(), addCopy(), addMsg(), aiCard(), api(), AUTO, bibtex(), buildPages() (+82 more)

### Community 1 - "Frontend App Logic"
Cohesion: 0.07
Nodes (67): cache_get(), cache_set(), s2_paper_id(), add_annotation(), add_to_workspace(), annotations(), AnnotIn, ArxivIn (+59 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (40): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+32 more)

### Community 3 - "db.py"
Cohesion: 0.08
Nodes (39): add_annotation(), add_message(), add_paper(), add_to_workspace(), add_workspace(), annotation_paper(), clear_messages(), conn() (+31 more)

### Community 4 - "pdf_parse.py"
Cohesion: 0.19
Nodes (16): _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), _guess_title(), _is_ref_head(), _is_scanned() (+8 more)

### Community 5 - "AI Feature Prompts"
Cohesion: 0.06
Nodes (28): ai_outline(), stream_block_translation(), run(), _build(), check(), _claude(), _claude_block(), _claude_stream() (+20 more)

### Community 6 - "features.py"
Cohesion: 0.17
Nodes (16): chat_messages(), cite_reason_messages(), _est_tokens(), explain_messages(), full_text_fits(), _header(), _history_block(), image_messages() (+8 more)

### Community 7 - "retrieval.py"
Cohesion: 0.09
Nodes (10): embed(), _bm25(), make_chunks(), search(), _tokens(), /api/health endpoint, backend/main.py (FastAPI app), BM25 retrieval (+2 more)

### Community 8 - "fake_api.py"
Cohesion: 0.16
Nodes (8): _answer(), chat(), claude_messages(), gen(), embeddings(), _err(), files(), _sse()

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.15
Nodes (12): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 名詞解釋, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight） (+4 more)

### Community 15 - "conftest.py"
Cohesion: 0.09
Nodes (12): _load_dotenv(), bob(), client(), fake_server(), _free_port(), papers(), pdfs(), authoryear() (+4 more)

### Community 16 - "test_units.py"
Cohesion: 0.12
Nodes (12): _translatable(), find_figures(), match_author_year(), render_page_png(), llm._ThinkStripper, test_find_figures(), test_page_blocks_and_render(), test_parse_author_year() (+4 more)

### Community 17 - "recommend"
Cohesion: 0.22
Nodes (6): _check(), _guess_ref_title(), lookup_reference(), recommend(), s2_get(), S2Error

### Community 18 - "auto_highlight"
Cohesion: 0.32
Nodes (6): auto_highlight(), guarded(), one(), _reference_start_page(), find_text_rects(), test_find_text_rects()

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `ParsedPaper structure`, `vLLM (Qwen3.5-9B)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 158 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `Database and API Routes`, `db.py`, `pdf_parse.py`, `AI Feature Prompts`, `features.py`?**
  _High betweenness centrality (0.312) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Database and API Routes` be split into smaller, more focused modules?**
  _Cohesion score 0.05280875236692615 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `pdf_parse.py`, `features.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Should `Frontend App Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.06593406593406594 - nodes in this community are weakly interconnected._
- **Why does `功能對照` connect `features.py` to `db.py`, `pdf_parse.py`, `AI Feature Prompts`, `Lantern — 個人用 AI 論文閱讀器`, `test_units.py`, `recommend`, `auto_highlight`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.06721215663354763 - nodes in this community are weakly interconnected._