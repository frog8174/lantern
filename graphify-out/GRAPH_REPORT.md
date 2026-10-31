# Graph Report - agent-aa6a76495d5161644  (2026-10-31)

## Corpus Check
- 31 files · ~32,398 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .example 1, .css 1)

## Summary
- 738 nodes · 1826 edges · 28 communities (24 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 46 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `403c80ed`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- main.py
- Anthropic Provider Tests
- db.py
- pdf_parse.py
- llm.py
- features.py
- Lantern 視覺系統（燈下的那一頁）
- fake_api.py
- Frontend UI Layout
- Static File Caching
- Graphify Graph Output
- Lantern Paper Reader
- conftest.py
- CLAUDE.md
- test_paper_cards.py
- Workspace LLM Wiki（MVP）
- escapeHTML
- Lantern — 個人用 AI 論文閱讀器
- drawHighlights
- cite.py
- aiCard
- escapeHTML
- pumpTranslation
- UX 第一輪（已定案）
- drawOutline
- 多使用者論文庫 + Workspace（測試登入版）
- showCite

## God Nodes (most connected - your core abstractions)
1. `conn()` - 44 edges
2. `_paper_or_404()` - 33 edges
3. `escapeHTML()` - 32 edges
4. `sse()` - 29 edges
5. `_id()` - 27 edges
6. `api()` - 25 edges
7. `_ws_or_404()` - 18 edges
8. `_ingest()` - 18 edges
9. `cache_get()` - 17 edges
10. `功能對照` - 17 edges

## Surprising Connections (you probably didn't know these)
- `資料表（`backend/db.py`）` --references--> `list_papers()`  [INFERRED]
  docs/paper-cards.md → backend/db.py
- `API` --references--> `_ws_or_404()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `範圍限制` --references--> `_mark_in_library()`  [INFERRED]
  docs/workspaces.md → backend/main.py
- `更新流程（後端，`features.py` 放 prompt）` --references--> `wiki()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `前端畫面` --references--> `api()`  [INFERRED]
  docs/workspaces.md → frontend/app.js

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (28 total, 4 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.05
Nodes (28): AUTO, card, caretAt(), chatWin, CITE_STYLES, citeStyles, COLORS, customColor (+20 more)

### Community 1 - "main.py"
Cohesion: 0.05
Nodes (88): cache_get(), cache_set(), list_papers(), s2_paper_id(), stream_chat(), add_annotation(), add_to_workspace(), annotations() (+80 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.07
Nodes (39): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+31 more)

### Community 3 - "db.py"
Cohesion: 0.05
Nodes (59): add_annotation(), add_message(), add_paper(), add_to_workspace(), add_wiki_message(), add_workspace(), annotation_paper(), clear_messages() (+51 more)

### Community 4 - "pdf_parse.py"
Cohesion: 0.06
Nodes (44): auto_highlight(), guarded(), one(), _reference_start_page(), stream_block_translation(), run(), _translatable(), _abstract() (+36 more)

### Community 5 - "llm.py"
Cohesion: 0.06
Nodes (22): _build(), check(), _claude(), _claude_block(), _claude_stream(), _create(), _mock_answer(), ocr_image() (+14 more)

### Community 6 - "features.py"
Cohesion: 0.05
Nodes (46): ai_outline(), _bib_arxiv(), _bib_llm(), _bib_s2(), chat_messages(), _check(), cite_reason_messages(), citing_contexts() (+38 more)

### Community 7 - "Lantern 視覺系統（燈下的那一頁）"
Cohesion: 0.29
Nodes (6): Lantern 視覺系統（燈下的那一頁）, 原則, 字體分工, 捲軸, 用語, 色彩 token

### Community 8 - "fake_api.py"
Cohesion: 0.07
Nodes (13): _answer(), chat(), claude_messages(), gen(), embeddings(), _err(), files(), _sse() (+5 more)

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "conftest.py"
Cohesion: 0.08
Nodes (12): _load_dotenv(), allow_duplicates(), bob(), client(), fake_server(), papers(), pdfs(), authoryear() (+4 more)

### Community 15 - "test_paper_cards.py"
Cohesion: 0.25
Nodes (6): byline(), _row(), test_byline(), test_cards_scoped_to_owner(), test_cite_cached_and_year(), test_patch_fields_independently()

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.21
Nodes (18): api(), cardsBusy(), enter(), importArxiv(), ingest(), loadLibrary(), loadPaperWiki(), openCite() (+10 more)

### Community 18 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

### Community 19 - "drawHighlights"
Cohesion: 0.30
Nodes (12): colorKey(), deleteAnnotation(), drawHighlights(), flashItem(), isHex(), noteItem(), refreshHighlights(), renderActivity() (+4 more)

### Community 20 - "cite.py"
Cohesion: 0.19
Nodes (18): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+10 more)

### Community 21 - "aiCard"
Cohesion: 0.22
Nodes (13): addAnnotation(), aiCard(), closeAiCard(), commentEditor(), explainCrop(), explainImage(), imageFollowup(), openPanel() (+5 more)

### Community 22 - "escapeHTML"
Cohesion: 0.18
Nodes (19): addAsk(), addSave(), cardPaper(), escapeHTML(), fmtDate(), loadAsk(), loadRelated(), loadWiki() (+11 more)

### Community 23 - "pumpTranslation"
Cohesion: 0.31
Nodes (10): buildPages(), drawTranslation(), fitText(), pumpTranslation(), queueTranslation(), renderPage(), setTrMode(), syncTwin() (+2 more)

### Community 24 - "UX 第一輪（已定案）"
Cohesion: 0.33
Nodes (5): A. 閱讀頁重新排版, B. 研究主題頁與流程, C. 全站主題切換, UX 第一輪（已定案）, 不做

### Community 26 - "drawOutline"
Cohesion: 0.40
Nodes (5): drawOutline(), goToPage(), hideFigure(), renderOutline(), showFigure()

### Community 27 - "多使用者論文庫 + Workspace（測試登入版）"
Cohesion: 0.25
Nodes (7): Workspace API, 前端畫面, 多使用者論文庫 + Workspace（測試登入版）, 決定, 範圍限制, 資料表（`backend/db.py`）, 這次不做

### Community 29 - "showCite"
Cohesion: 0.22
Nodes (13): addCopy(), addMsg(), bibtex(), icon(), loadChat(), renderExplains(), renderMD(), renderRefs() (+5 more)

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `/api/health endpoint`, `BM25 retrieval` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 230 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `pdf_parse.py` to `app.js`, `db.py`, `llm.py`, `features.py`?**
  _High betweenness centrality (0.297) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.052564102564102565 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `pdf_parse.py`, `llm.py`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05126050420168067 - nodes in this community are weakly interconnected._
- **Why does `功能對照` connect `pdf_parse.py` to `Lantern — 個人用 AI 論文閱讀器`, `db.py`, `llm.py`, `features.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._