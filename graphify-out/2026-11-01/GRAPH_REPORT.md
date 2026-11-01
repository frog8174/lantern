# Graph Report - paper-reader  (2026-11-01)

## Corpus Check
- 41 files · ~35,671 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .example 1, .css 1)

## Summary
- 941 nodes · 2071 edges · 68 communities (62 shown, 6 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 48 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a239b0d4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- features.py
- Anthropic Provider Tests
- db.py
- re
- asyncio
- test_units.py
- Lantern 視覺系統（燈下的那一頁）
- fake_api.py
- Frontend UI Layout
- Static File Caching
- Graphify Graph Output
- Lantern Paper Reader
- main.py
- CLAUDE.md
- config.py
- Workspace LLM Wiki（MVP）
- escapeHTML
- retrieval.py
- drawHighlights
- cite.py
- aiCard
- streamInto
- pumpTranslation
- data
- Uid
- drawOutline
- 登入系統：Keycloak（OIDC）
- auto_highlight
- post
- get
- conftest.py
- cache_get
- _to_claude
- complete_json
- paintWsCards
- Lantern — 個人用 AI 論文閱讀器
- test_anthropic.py
- _ThinkStripper
- _stream
- _ingest
- import_url
- UX 第一輪（已定案）
- update_wiki
- login
- local_context
- s2_get
- ingress.yaml
- containers
- service.yaml
- llm.py
- json
- pvc.yaml
- 部署到 k8s
- kustomization.yaml
- sample_pdfs.py
- config.py
- deployment.yaml
- spec
- securityContext
- volumes
- find_duplicate
- namespace.yaml
- livenessProbe
- securityContext
- startupProbe
- spec
- Lantern AI Paper Reader

## God Nodes (most connected - your core abstractions)
1. `conn()` - 46 edges
2. `escapeHTML()` - 34 edges
3. `_paper_or_404()` - 33 edges
4. `sse()` - 29 edges
5. `api()` - 28 edges
6. `_id()` - 27 edges
7. `data` - 22 edges
8. `_ws_or_404()` - 18 edges
9. `_ingest()` - 18 edges
10. `openPaper()` - 18 edges

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

## Communities (68 total, 6 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.05
Nodes (31): AUTO, calmMotion, card, caretAt(), CITE_STYLES, citeStyles, COLORS, customColor (+23 more)

### Community 1 - "features.py"
Cohesion: 0.13
Nodes (19): _bib_arxiv(), _bib_llm(), _bib_s2(), chat_messages(), _est_tokens(), fetch_bib(), full_text_fits(), _header() (+11 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.11
Nodes (28): sse(), _id(), test_ai_outline(), test_annotation_kinds(), test_annotations_crud(), test_ask_ai_on_selection(), test_author_year_reference(), test_auto_highlight_finds_sentence() (+20 more)

### Community 3 - "db.py"
Cohesion: 0.12
Nodes (23): add_annotation(), add_message(), add_wiki_message(), add_workspace(), annotation_paper(), clear_messages(), clear_wiki_messages(), conn() (+15 more)

### Community 4 - "re"
Cohesion: 0.13
Nodes (21): _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), find_figures(), _guess_title(), _is_ref_head() (+13 more)

### Community 5 - "asyncio"
Cohesion: 0.25
Nodes (5): check(), route(), _test_image(), health(), test_route_prefixes()

### Community 6 - "test_units.py"
Cohesion: 0.18
Nodes (9): cite_reason_messages(), citing_contexts(), _translatable(), llm._ThinkStripper, test_citing_contexts(), test_parse_numeric(), test_scanned_detection(), test_think_stripper() (+1 more)

### Community 7 - "Lantern 視覺系統（燈下的那一頁）"
Cohesion: 0.22
Nodes (8): Lantern 視覺系統（燈下的那一頁）, 原則, 字體分工, 捲軸, 用語, 登入頁與標誌, 色彩 token, 薛西弗斯（等待、完成、空狀態）

### Community 8 - "fake_api.py"
Cohesion: 0.12
Nodes (11): _answer(), chat(), claude_messages(), gen(), embeddings(), _err(), files(), _sse() (+3 more)

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "main.py"
Cohesion: 0.10
Nodes (21): get_workspace(), add_annotation(), add_to_workspace(), AnnotIn, AskIn, ChatIn, CommentIn, create_workspace() (+13 more)

### Community 15 - "config.py"
Cohesion: 0.08
Nodes (11): byline(), FakeKC, _oidc(), test_oidc_login_creates_user_and_session(), test_oidc_login_failure_redirects(), _row(), test_byline(), test_cards_scoped_to_owner() (+3 more)

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.14
Nodes (33): api(), bibtex(), cardsBusy(), enter(), escapeHTML(), importArxiv(), ingest(), loadAsk() (+25 more)

### Community 18 - "retrieval.py"
Cohesion: 0.22
Nodes (5): _bm25(), make_chunks(), _tokens(), BM25 retrieval, RAG for long papers

### Community 19 - "drawHighlights"
Cohesion: 0.26
Nodes (14): colorKey(), deleteAnnotation(), drawHighlights(), flashItem(), icon(), isHex(), noteItem(), refreshHighlights() (+6 more)

### Community 20 - "cite.py"
Cohesion: 0.19
Nodes (18): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+10 more)

### Community 21 - "aiCard"
Cohesion: 0.22
Nodes (13): addAnnotation(), aiCard(), closeAiCard(), commentEditor(), explainCrop(), explainImage(), imageFollowup(), openPanel() (+5 more)

### Community 22 - "streamInto"
Cohesion: 0.21
Nodes (15): addAsk(), addCopy(), addMsg(), addSave(), loadChat(), pushLater(), reach(), renderMD() (+7 more)

### Community 23 - "pumpTranslation"
Cohesion: 0.24
Nodes (12): buildPages(), drawRail(), drawTranslation(), fitText(), pumpTranslation(), queueTranslation(), renderPage(), setTrMode() (+4 more)

### Community 24 - "data"
Cohesion: 0.07
Nodes (26): apiVersion, data, AUTH_MODE, DISABLE_THINKING, LLM_CONCURRENCY, LLM_CONTEXT_TOKENS, LLM_EFFORT, LLM_MODEL (+18 more)

### Community 25 - "Uid"
Cohesion: 0.21
Nodes (15): delete_annotation(), auto_highlight(), chat_clear(), delete(), delete_workspace(), papers(), remove_annotation(), remove_from_workspace() (+7 more)

### Community 26 - "drawOutline"
Cohesion: 0.29
Nodes (7): drawOutline(), goToPage(), hideFigure(), markOutline(), renderOutline(), setLibDrawer(), showFigure()

### Community 27 - "登入系統：Keycloak（OIDC）"
Cohesion: 0.11
Nodes (16): current_user(), k8s 部署要一起處理的事（不處理會壞）, Keycloak 端要建的 client, 建議架構：後端當 OIDC client（Authorization Code + PKCE）, 待確認, 既有資料, 登入系統：Keycloak（OIDC）, 設定（`.env`／k8s Secret） (+8 more)

### Community 28 - "auto_highlight"
Cohesion: 0.32
Nodes (6): auto_highlight(), guarded(), one(), _reference_start_page(), find_text_rects(), test_find_text_rects()

### Community 29 - "post"
Cohesion: 0.17
Nodes (15): stream_chat(), _cached_text(), chat(), explain(), explain_image(), PageIn, reference_why(), SelectionIn (+7 more)

### Community 30 - "get"
Cohesion: 0.11
Nodes (18): annotations(), auth_config(), auth_users(), chat_history(), cite_paper(), figures(), livez(), me() (+10 more)

### Community 31 - "conftest.py"
Cohesion: 0.13
Nodes (6): allow_duplicates(), bob(), client(), fake_server(), papers(), pdfs()

### Community 32 - "cache_get"
Cohesion: 0.21
Nodes (11): cache_get(), cache_set(), list_papers(), _check(), recommend(), s2_paper_id(), _block_translation(), _ensure_bib() (+3 more)

### Community 33 - "_to_claude"
Cohesion: 0.22
Nodes (6): _claude(), _claude_block(), _claude_stream(), _to_claude(), test_cache_breakpoint_only_for_multi_turn(), test_to_claude_conversion()

### Community 34 - "complete_json"
Cohesion: 0.24
Nodes (8): _strip_fence(), _wiki_concept(), _wiki_index(), _wiki_plan(), wiki_qa_page(), complete(), complete_json(), _mock_json()

### Community 35 - "paintWsCards"
Cohesion: 0.33
Nodes (7): cardPaper(), fmtDate(), openNote(), paintWsCards(), patchPaper(), showWikiPage(), trRing()

### Community 36 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

### Community 37 - "test_anthropic.py"
Cohesion: 0.16
Nodes (11): claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape(), test_mixed_providers() (+3 more)

### Community 39 - "_stream"
Cohesion: 0.40
Nodes (5): _build(), _create(), _stream(), test_build_adjustments(), test_build_default_sends_vllm_params()

### Community 40 - "_ingest"
Cohesion: 0.14
Nodes (13): add_paper(), add_to_workspace(), get_paper(), get_settings(), _auto_wiki(), _duplicate(), _first_doi(), _ingest() (+5 more)

### Community 41 - "import_url"
Cohesion: 0.18
Nodes (9): ArxivIn, figure_png(), _figures(), import_url(), paper_pdf(), paper_thumb(), _pdf_path(), region_png() (+1 more)

### Community 42 - "UX 第一輪（已定案）"
Cohesion: 0.33
Nodes (5): A. 閱讀頁重新排版, B. 研究主題頁與流程, C. 全站主題切換, UX 第一輪（已定案）, 不做

### Community 43 - "update_wiki"
Cohesion: 0.13
Nodes (12): list_wiki_messages(), wiki_mark_ingested(), wiki_page(), wiki_pages(), wiki_pending(), wiki_save(), update_wiki(), wiki_ask_messages() (+4 more)

### Community 44 - "login"
Cohesion: 0.20
Nodes (5): login(), LoginIn, logout(), oidc_callback(), oidc_login()

### Community 45 - "local_context"
Cohesion: 0.22
Nodes (8): ai_outline(), explain_messages(), _history_block(), image_messages(), local_context(), stream_block_translation(), run(), 功能對照

### Community 46 - "s2_get"
Cohesion: 0.17
Nodes (9): _guess_ref_title(), lookup_reference(), s2_get(), API, 前端（論文卡）, 決定, 論文卡：備註、星號、排序、複製引用, 資料表（`backend/db.py`） (+1 more)

### Community 47 - "ingress.yaml"
Cohesion: 0.10
Nodes (20): cert-manager.io/cluster-issuer, traefik.ingress.kubernetes.io/router.entrypoints, traefik.ingress.kubernetes.io/router.tls, apiVersion, paths, kind, metadata, annotations (+12 more)

### Community 48 - "containers"
Cohesion: 0.17
Nodes (12): envFrom, image, name, ports, readinessProbe, resources, volumeMounts, httpGet (+4 more)

### Community 49 - "service.yaml"
Cohesion: 0.17
Nodes (11): apiVersion, kind, metadata, name, name, port, targetPort, app (+3 more)

### Community 50 - "llm.py"
Cohesion: 0.18
Nodes (4): _mock_answer(), ocr_image(), one(), vLLM (Qwen3.5-9B)

### Community 51 - "json"
Cohesion: 0.22
Nodes (8): list_annotations(), load_chunks(), save_chunks(), set_settings(), update_paper(), embed(), build_index(), search()

### Community 52 - "pvc.yaml"
Cohesion: 0.18
Nodes (10): apiVersion, kind, metadata, name, storage, requests, spec, accessModes (+2 more)

### Community 53 - "部署到 k8s"
Cohesion: 0.18
Nodes (10): 1. 建映像, 2. Keycloak client（沿用 `lantern-local`）, 3. Secret（不要 commit）, 4. 設定與套用, Traefik, 常見問題, 待填, 本機驗證（2026-11-01） (+2 more)

### Community 54 - "kustomization.yaml"
Cohesion: 0.22
Nodes (8): apiVersion, images, name, newName, newTag, kind, namespace, resources

### Community 55 - "sample_pdfs.py"
Cohesion: 0.44
Nodes (5): authoryear(), make_all(), numeric(), scanned(), _text()

### Community 57 - "deployment.yaml"
Cohesion: 0.29
Nodes (6): apiVersion, kind, app, metadata, labels, name

### Community 58 - "spec"
Cohesion: 0.29
Nodes (7): app, matchLabels, spec, replicas, selector, strategy, type

### Community 59 - "securityContext"
Cohesion: 0.29
Nodes (7): type, fsGroup, runAsGroup, runAsNonRoot, runAsUser, seccompProfile, securityContext

### Community 60 - "volumes"
Cohesion: 0.33
Nodes (6): sizeLimit, claimName, volumes, emptyDir, name, persistentVolumeClaim

### Community 61 - "find_duplicate"
Cohesion: 0.40
Nodes (3): find_duplicate(), norm_title(), test_find_duplicate_rules()

### Community 62 - "namespace.yaml"
Cohesion: 0.40
Nodes (4): apiVersion, kind, metadata, name

### Community 63 - "livenessProbe"
Cohesion: 0.50
Nodes (4): livenessProbe, failureThreshold, httpGet, periodSeconds

### Community 64 - "securityContext"
Cohesion: 0.50
Nodes (4): securityContext, allowPrivilegeEscalation, capabilities, readOnlyRootFilesystem

### Community 65 - "startupProbe"
Cohesion: 0.50
Nodes (4): startupProbe, failureThreshold, httpGet, periodSeconds

### Community 66 - "spec"
Cohesion: 0.50
Nodes (4): template, terminationGracePeriodSeconds, metadata, spec

### Community 67 - "Lantern AI Paper Reader"
Cohesion: 0.67
Nodes (3): /api/health endpoint, backend/main.py (FastAPI app), Lantern AI Paper Reader

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `Semantic Scholar API`, `graphify-out/graph.json`, `graphify usage rules`, `/api/health endpoint` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 360 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `Lantern AI Paper Reader` to `app.js`, `features.py`, `db.py`, `re`, `retrieval.py`, `llm.py`?**
  _High betweenness centrality (0.225) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `Semantic Scholar API`, `graphify-out/graph.json` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.048726467331118496 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `re`, `local_context`, `_ThinkStripper`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `features.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12615384615384614 - nodes in this community are weakly interconnected._
- **Why does `current_user()` connect `登入系統：Keycloak（OIDC）` to `db.py`, `login`, `main.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._