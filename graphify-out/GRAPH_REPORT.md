# Graph Report - paper-reader  (2026-10-31)

## Corpus Check
- 24 files · ~25,679 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .example 1, .css 1)

## Summary
- 588 nodes · 1458 edges · 22 communities (18 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 40 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ebe9bd61`
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
- Workspace LLM Wiki（MVP）
- test_units.py
- s2_paper_id
- 功能對照
- complete_json
- auto_highlight

## God Nodes (most connected - your core abstractions)
1. `conn()` - 38 edges
2. `_paper_or_404()` - 30 edges
3. `sse()` - 29 edges
4. `_id()` - 27 edges
5. `escapeHTML()` - 22 edges
6. `api()` - 17 edges
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

## Communities (22 total, 4 thin omitted)

### Community 0 - "Database and API Routes"
Cohesion: 0.05
Nodes (91): addAnnotation(), addCopy(), addMsg(), aiCard(), api(), AUTO, bibtex(), buildPages() (+83 more)

### Community 1 - "Frontend App Logic"
Cohesion: 0.07
Nodes (72): cache_get(), cache_set(), stream_chat(), add_annotation(), add_to_workspace(), annotations(), AnnotIn, ArxivIn (+64 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (39): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+31 more)

### Community 3 - "db.py"
Cohesion: 0.07
Nodes (49): add_annotation(), add_message(), add_paper(), add_to_workspace(), add_workspace(), annotation_paper(), clear_messages(), conn() (+41 more)

### Community 4 - "pdf_parse.py"
Cohesion: 0.18
Nodes (17): _wiki_slug(), _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), _guess_title(), _is_ref_head() (+9 more)

### Community 5 - "AI Feature Prompts"
Cohesion: 0.06
Nodes (25): _build(), check(), _claude(), _claude_block(), _claude_stream(), _create(), _mock_answer(), ocr_image() (+17 more)

### Community 6 - "features.py"
Cohesion: 0.17
Nodes (15): chat_messages(), cite_reason_messages(), _est_tokens(), explain_messages(), full_text_fits(), _header(), _history_block(), image_messages() (+7 more)

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
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

### Community 15 - "conftest.py"
Cohesion: 0.09
Nodes (12): _load_dotenv(), bob(), client(), fake_server(), _free_port(), papers(), pdfs(), authoryear() (+4 more)

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.22
Nodes (8): API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定, 資料表（`backend/db.py`）, 這次不做, 頁面種類與 slug

### Community 17 - "test_units.py"
Cohesion: 0.17
Nodes (9): citing_contexts(), _translatable(), llm._ThinkStripper, test_citing_contexts(), test_page_blocks_and_render(), test_parse_numeric(), test_scanned_detection(), test_think_stripper() (+1 more)

### Community 18 - "s2_paper_id"
Cohesion: 0.20
Nodes (7): _check(), _guess_ref_title(), lookup_reference(), recommend(), s2_get(), s2_paper_id(), S2Error

### Community 19 - "功能對照"
Cohesion: 0.17
Nodes (9): page_translate_messages(), stream_block_translation(), run(), translate_messages(), find_figures(), match_author_year(), 功能對照, test_find_figures() (+1 more)

### Community 20 - "complete_json"
Cohesion: 0.25
Nodes (8): ai_outline(), _strip_fence(), _wiki_concept(), _wiki_index(), _wiki_plan(), complete(), complete_json(), _mock_json()

### Community 21 - "auto_highlight"
Cohesion: 0.32
Nodes (6): auto_highlight(), guarded(), one(), _reference_start_page(), find_text_rects(), test_find_text_rects()

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `ParsedPaper structure`, `vLLM (Qwen3.5-9B)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 170 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `Database and API Routes`, `db.py`, `pdf_parse.py`, `AI Feature Prompts`, `features.py`?**
  _High betweenness centrality (0.298) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Database and API Routes` be split into smaller, more focused modules?**
  _Cohesion score 0.05215419501133787 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `功能對照`, `pdf_parse.py`, `AI Feature Prompts`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Should `Frontend App Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.06513157894736842 - nodes in this community are weakly interconnected._
- **Why does `功能對照` connect `功能對照` to `db.py`, `pdf_parse.py`, `AI Feature Prompts`, `features.py`, `Lantern — 個人用 AI 論文閱讀器`, `s2_paper_id`, `complete_json`, `auto_highlight`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._