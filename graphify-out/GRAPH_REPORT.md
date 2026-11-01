# Graph Report - paper-reader  (2026-11-01)

## Corpus Check
- 45 files · ~41,629 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .example 1, .css 1)

## Summary
- 1028 nodes · 2299 edges · 60 communities (53 shown, 7 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 76 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `40542675`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- features.py
- test_api.py
- db.py
- re
- test_units.py
- Lantern 視覺系統（燈下的那一頁）
- conftest.py
- Frontend UI Layout
- Static File Caching
- Graphify Graph Output
- Lantern Paper Reader
- main.py
- CLAUDE.md
- backend/__init__.py
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
- 登入系統：Keycloak（OIDC）
- auto_highlight
- post
- _paper_or_404
- 功能對照
- llm.py
- complete_json
- saveNote
- Lantern — 個人用 AI 論文閱讀器
- _to_claude
- 閱讀器：選取、螢光筆與中英對照
- drawOutline
- import_url
- UX 第一輪（已定案）
- oidc_callback
- _ThinkStripper
- s2_get
- ingress.yaml
- containers
- service.yaml
- check
- pvc.yaml
- 部署到 k8s
- kustomization.yaml
- deployment.yaml
- spec
- securityContext
- volumes
- _stream
- namespace.yaml
- livenessProbe
- securityContext
- startupProbe
- spec
- ocr_image

## God Nodes (most connected - your core abstractions)
1. `conn()` - 50 edges
2. `_paper_or_404()` - 37 edges
3. `escapeHTML()` - 35 edges
4. `sse()` - 33 edges
5. `api()` - 32 edges
6. `_id()` - 27 edges
7. `data` - 22 edges
8. `cache_get()` - 20 edges
9. `openPaper()` - 19 edges
10. `drawHighlights()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `資料表（`backend/db.py`）` --references--> `list_papers()`  [INFERRED]
  docs/paper-cards.md → backend/db.py
- `API` --references--> `_ws_or_404()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `螢光筆同步到譯文` --references--> `align()`  [INFERRED]
  docs/reader.md → backend/main.py
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

## Communities (60 total, 7 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.04
Nodes (38): AUTO, calmMotion, card, cardPaper(), caretAt(), CITE_STYLES, citeStyles, COLORS (+30 more)

### Community 1 - "features.py"
Cohesion: 0.12
Nodes (20): _bib_arxiv(), _bib_llm(), _bib_s2(), chat_messages(), cite_reason_messages(), _est_tokens(), fetch_bib(), full_text_fits() (+12 more)

### Community 2 - "test_api.py"
Cohesion: 0.06
Nodes (42): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+34 more)

### Community 3 - "db.py"
Cohesion: 0.05
Nodes (57): add_annotation(), add_message(), add_paper(), add_to_workspace(), add_wiki_message(), add_workspace(), annotation_paper(), clear_messages() (+49 more)

### Community 4 - "re"
Cohesion: 0.15
Nodes (19): _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), _guess_title(), _is_ref_head(), _is_scanned() (+11 more)

### Community 5 - "test_units.py"
Cohesion: 0.14
Nodes (10): citing_contexts(), _translatable(), find_figures(), llm._ThinkStripper, test_citing_contexts(), test_find_figures(), test_parse_numeric(), test_scanned_detection() (+2 more)

### Community 7 - "Lantern 視覺系統（燈下的那一頁）"
Cohesion: 0.18
Nodes (10): Lantern 視覺系統（燈下的那一頁）, 原則, 字體分工, 捲軸, 用語, 登入頁與標誌, 自動畫重點標籤（無印風）, 自動畫重點的頁邊標籤 (+2 more)

### Community 8 - "conftest.py"
Cohesion: 0.05
Nodes (24): _load_dotenv(), allow_duplicates(), bob(), client(), fake_server(), papers(), pdfs(), _answer() (+16 more)

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "main.py"
Cohesion: 0.08
Nodes (22): add_to_workspace(), auth_config(), CommentIn, create_workspace(), edit_annotation(), edit_paper(), get_settings(), health() (+14 more)

### Community 15 - "backend/__init__.py"
Cohesion: 0.07
Nodes (16): byline(), _fake(), test_align_invalid_falls_back(), test_align_scoped_to_owner(), test_align_valid_substring(), _translated_block(), FakeKC, _oidc() (+8 more)

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.13
Nodes (34): api(), bibtex(), cardsBusy(), closeAiCard(), escapeHTML(), importArxiv(), ingest(), loadAsk() (+26 more)

### Community 18 - "retrieval.py"
Cohesion: 0.15
Nodes (11): embed(), _bm25(), build_index(), make_chunks(), search(), _tokens(), /api/health endpoint, backend/main.py (FastAPI app) (+3 more)

### Community 19 - "drawHighlights"
Cohesion: 0.15
Nodes (25): 1. Lantern 現在已經有什麼, 連續的選取與螢光筆, alignHighlight(), clearLitAlign(), colorKey(), correspond(), deleteAnnotation(), drawHighlights() (+17 more)

### Community 20 - "cite.py"
Cohesion: 0.19
Nodes (18): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+10 more)

### Community 21 - "aiCard"
Cohesion: 0.23
Nodes (13): addAnnotation(), aiCard(), commentEditor(), explainCrop(), explainImage(), highlightTranslation(), imageFollowup(), placeFloating() (+5 more)

### Community 22 - "streamInto"
Cohesion: 0.36
Nodes (8): 薛西弗斯（等待、完成、空狀態）, addCopy(), addMsg(), loadChat(), pushLater(), runSummary(), sendChat(), streamInto()

### Community 23 - "pumpTranslation"
Cohesion: 0.24
Nodes (12): buildPages(), drawRail(), drawTranslation(), fitText(), pumpTranslation(), queueTranslation(), renderPage(), setTrMode() (+4 more)

### Community 24 - "data"
Cohesion: 0.07
Nodes (26): apiVersion, data, AUTH_MODE, DISABLE_THINKING, LLM_CONCURRENCY, LLM_CONTEXT_TOKENS, LLM_EFFORT, LLM_MODEL (+18 more)

### Community 25 - "Uid"
Cohesion: 0.14
Nodes (21): auth_users(), chat_clear(), chat_history(), delete(), delete_workspace(), get_note(), me(), paper_wiki() (+13 more)

### Community 27 - "登入系統：Keycloak（OIDC）"
Cohesion: 0.05
Nodes (38): delete_paper(), current_user(), _mark_in_library(), k8s 部署要一起處理的事（不處理會壞）, Keycloak 端要建的 client, 建議架構：後端當 OIDC client（Authorization Code + PKCE）, 待確認, 既有資料 (+30 more)

### Community 28 - "auto_highlight"
Cohesion: 0.32
Nodes (6): auto_highlight(), guarded(), one(), _reference_start_page(), find_text_rects(), test_find_text_rects()

### Community 29 - "post"
Cohesion: 0.10
Nodes (20): add_annotation(), AlignIn, AlignMark, AnnotIn, AskIn, chat(), ChatIn, explain() (+12 more)

### Community 30 - "_paper_or_404"
Cohesion: 0.16
Nodes (21): cache_get(), cache_set(), s2_paper_id(), stream_chat(), align(), annotations(), _block_translation(), _cached_text() (+13 more)

### Community 32 - "功能對照"
Cohesion: 0.20
Nodes (9): explain_messages(), _history_block(), image_messages(), local_context(), page_translate_messages(), stream_block_translation(), run(), translate_messages() (+1 more)

### Community 34 - "complete_json"
Cohesion: 0.18
Nodes (10): ai_outline(), align_span(), _strip_fence(), _wiki_concept(), _wiki_index(), _wiki_plan(), wiki_qa_page(), complete() (+2 more)

### Community 35 - "saveNote"
Cohesion: 0.20
Nodes (19): addAsk(), addSave(), fmtDate(), insertIntoNote(), loadNote(), nbKey(), nbMsg(), nbStatus() (+11 more)

### Community 36 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

### Community 37 - "_to_claude"
Cohesion: 0.22
Nodes (6): _claude(), _claude_block(), _claude_stream(), _to_claude(), test_cache_breakpoint_only_for_multi_turn(), test_to_claude_conversion()

### Community 38 - "閱讀器：選取、螢光筆與中英對照"
Cohesion: 0.40
Nodes (4): 並排模式：對應的段落亮起來, 螢光筆同步到譯文, 逐句對應（並排模式）, 閱讀器：選取、螢光筆與中英對照

### Community 39 - "drawOutline"
Cohesion: 0.20
Nodes (10): drawOutline(), enter(), goToPage(), hideFigure(), icon(), markOutline(), openAt(), renderOutline() (+2 more)

### Community 41 - "import_url"
Cohesion: 0.13
Nodes (12): ArxivIn, auto_highlight(), figure_png(), figures(), _figures(), import_url(), paper_pdf(), paper_thumb() (+4 more)

### Community 42 - "UX 第一輪（已定案）"
Cohesion: 0.33
Nodes (5): A. 閱讀頁重新排版, B. 研究主題頁與流程, C. 全站主題切換, UX 第一輪（已定案）, 不做

### Community 46 - "s2_get"
Cohesion: 0.14
Nodes (10): _check(), recommend(), s2_get(), S2Error, API, 前端（論文卡）, 決定, 論文卡：備註、星號、排序、複製引用 (+2 more)

### Community 47 - "ingress.yaml"
Cohesion: 0.10
Nodes (20): cert-manager.io/cluster-issuer, traefik.ingress.kubernetes.io/router.entrypoints, traefik.ingress.kubernetes.io/router.tls, apiVersion, paths, kind, metadata, annotations (+12 more)

### Community 48 - "containers"
Cohesion: 0.17
Nodes (12): envFrom, image, name, ports, readinessProbe, resources, volumeMounts, httpGet (+4 more)

### Community 49 - "service.yaml"
Cohesion: 0.17
Nodes (11): apiVersion, kind, metadata, name, name, port, targetPort, app (+3 more)

### Community 50 - "check"
Cohesion: 0.29
Nodes (4): check(), route(), _test_image(), test_route_prefixes()

### Community 52 - "pvc.yaml"
Cohesion: 0.18
Nodes (10): apiVersion, kind, metadata, name, storage, requests, spec, accessModes (+2 more)

### Community 53 - "部署到 k8s"
Cohesion: 0.18
Nodes (10): 1. 建映像, 2. Keycloak client（沿用 `lantern-local`）, 3. Secret（不要 commit）, 4. 設定與套用, Traefik, 常見問題, 待填, 本機驗證（2026-11-01） (+2 more)

### Community 54 - "kustomization.yaml"
Cohesion: 0.22
Nodes (8): apiVersion, images, name, newName, newTag, kind, namespace, resources

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

### Community 61 - "_stream"
Cohesion: 0.40
Nodes (5): _build(), _create(), _stream(), test_build_adjustments(), test_build_default_sends_vllm_params()

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

### Community 67 - "ocr_image"
Cohesion: 0.40
Nodes (3): ocr_image(), _ocr_pages(), one()

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `Semantic Scholar API`, `graphify-out/graph.json`, `graphify usage rules`, `BM25 retrieval` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 390 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `app.js`, `features.py`, `llm.py`, `db.py`, `re`?**
  _High betweenness centrality (0.242) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `Semantic Scholar API`, `graphify-out/graph.json` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.044081632653061226 - nodes in this community are weakly interconnected._
- **Why does `pushLater()` connect `streamInto` to `app.js`, `escapeHTML`, `saveNote`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Should `features.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12315270935960591 - nodes in this community are weakly interconnected._
- **Why does `薛西弗斯（等待、完成、空狀態）` connect `streamInto` to `Lantern 視覺系統（燈下的那一頁）`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Should `test_api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.060515873015873016 - nodes in this community are weakly interconnected._