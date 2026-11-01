# Graph Report - paper-reader  (2026-11-01)

## Corpus Check
- 53 files · ~44,779 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .example 1, .css 1)

## Summary
- 1162 nodes · 2476 edges · 79 communities (69 shown, 10 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 87 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7e9819a0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- features.py
- test_api.py
- db.py
- re
- test_units.py
- containers
- Lantern 視覺系統（燈下的那一頁）
- fake_api.py
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
- k8s-labse/ingress.yaml
- 4. 設計提案
- auto_highlight
- post
- _paper_or_404
- conftest.py
- 功能對照
- sse
- 登入系統：Keycloak（OIDC）
- loadNote
- Lantern — 個人用 AI 論文閱讀器
- _to_claude
- align
- drawOutline
- _header
- _paper_or_404
- UX 第一輪（已定案）
- k8s-labse/service.yaml
- oidc_callback
- _ThinkStripper
- s2_get
- ingress.yaml
- containers
- service.yaml
- check
- test_paper_cards.py
- pvc.yaml
- 部署到 k8s
- kustomization.yaml
- k8s-labse/pvc.yaml
- pymupdf
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
- test_align.py
- test_workspaces.py
- config.py
- test_notes.py
- recommendations
- k8s-labse/kustomization.yaml
- k8s-labse/namespace.yaml
- LaBSE 句向量服務（中英逐句對齊）
- Lantern AI Paper Reader
- test_chat_after_switching_embedding_model

## God Nodes (most connected - your core abstractions)
1. `conn()` - 50 edges
2. `escapeHTML()` - 38 edges
3. `_paper_or_404()` - 37 edges
4. `api()` - 33 edges
5. `sse()` - 33 edges
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
- `更新流程（後端，`features.py` 放 prompt）` --references--> `wiki()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `前端畫面` --references--> `api()`  [INFERRED]
  docs/workspaces.md → frontend/app.js
- `逐句對應（並排模式）` --references--> `markTranslation()`  [INFERRED]
  docs/reader.md → frontend/app.js

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (79 total, 10 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.04
Nodes (45): AUTO, calmMotion, card, caretAt(), CITE_STYLES, citeStyles, CM_URLS, COLORS (+37 more)

### Community 1 - "features.py"
Cohesion: 0.11
Nodes (20): ai_outline(), align_span(), _bib_arxiv(), _bib_llm(), _bib_s2(), fetch_bib(), _guess_ref_title(), lookup_reference() (+12 more)

### Community 2 - "test_api.py"
Cohesion: 0.10
Nodes (26): _id(), test_ai_outline(), test_annotation_kinds(), test_annotations_crud(), test_ask_ai_on_selection(), test_author_year_reference(), test_auto_highlight_finds_sentence(), test_bilingual_blocks() (+18 more)

### Community 3 - "db.py"
Cohesion: 0.05
Nodes (60): add_annotation(), add_message(), add_paper(), add_to_workspace(), add_wiki_message(), add_workspace(), annotation_paper(), clear_messages() (+52 more)

### Community 4 - "re"
Cohesion: 0.18
Nodes (17): _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), _guess_title(), _is_ref_head(), match_author_year() (+9 more)

### Community 5 - "test_units.py"
Cohesion: 0.14
Nodes (10): citing_contexts(), _translatable(), render_page_png(), llm._ThinkStripper, test_citing_contexts(), test_page_blocks_and_render(), test_parse_numeric(), test_scanned_detection() (+2 more)

### Community 6 - "containers"
Cohesion: 0.04
Nodes (47): apiVersion, args, command, env, image, livenessProbe, name, ports (+39 more)

### Community 7 - "Lantern 視覺系統（燈下的那一頁）"
Cohesion: 0.18
Nodes (10): Lantern 視覺系統（燈下的那一頁）, 原則, 字體分工, 捲軸, 用語, 登入頁與標誌, 自動畫重點標籤（無印風）, 自動畫重點的頁邊標籤 (+2 more)

### Community 8 - "fake_api.py"
Cohesion: 0.11
Nodes (12): _answer(), chat(), claude_messages(), gen(), embeddings(), _err(), files(), _sse() (+4 more)

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "main.py"
Cohesion: 0.09
Nodes (19): ArxivIn, auth_config(), CommentIn, create_workspace(), edit_annotation(), edit_paper(), get_settings(), import_url() (+11 more)

### Community 15 - "backend/__init__.py"
Cohesion: 0.21
Nodes (4): FakeKC, _oidc(), test_oidc_login_creates_user_and_session(), test_oidc_login_failure_redirects()

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.12
Nodes (37): api(), bibtex(), cardPaper(), cardsBusy(), escapeHTML(), importArxiv(), ingest(), loadAsk() (+29 more)

### Community 18 - "retrieval.py"
Cohesion: 0.18
Nodes (8): embed(), _bm25(), build_index(), make_chunks(), search(), _tokens(), BM25 retrieval, RAG for long papers

### Community 19 - "drawHighlights"
Cohesion: 0.15
Nodes (25): 1. Lantern 現在已經有什麼, 連續的選取與螢光筆, alignHighlight(), clearLitAlign(), colorKey(), correspond(), deleteAnnotation(), drawHighlights() (+17 more)

### Community 20 - "cite.py"
Cohesion: 0.19
Nodes (18): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+10 more)

### Community 21 - "aiCard"
Cohesion: 0.21
Nodes (14): addAnnotation(), aiCard(), closeAiCard(), commentEditor(), explainCrop(), explainImage(), highlightTranslation(), imageFollowup() (+6 more)

### Community 22 - "streamInto"
Cohesion: 0.31
Nodes (9): 薛西弗斯（等待、完成、空狀態）, addAsk(), addSave(), pushLater(), reach(), runSummary(), sendAsk(), stream() (+1 more)

### Community 23 - "pumpTranslation"
Cohesion: 0.24
Nodes (12): buildPages(), drawRail(), drawTranslation(), fitText(), pumpTranslation(), queueTranslation(), renderPage(), setTrMode() (+4 more)

### Community 24 - "data"
Cohesion: 0.07
Nodes (26): apiVersion, data, AUTH_MODE, DISABLE_THINKING, LLM_CONCURRENCY, LLM_CONTEXT_TOKENS, LLM_EFFORT, LLM_MODEL (+18 more)

### Community 25 - "Uid"
Cohesion: 0.17
Nodes (15): chat_clear(), delete(), delete_workspace(), papers(), remove_annotation(), remove_from_workspace(), search(), upload() (+7 more)

### Community 26 - "k8s-labse/ingress.yaml"
Cohesion: 0.10
Nodes (20): cert-manager.io/cluster-issuer, traefik.ingress.kubernetes.io/router.entrypoints, traefik.ingress.kubernetes.io/router.tls, apiVersion, paths, kind, metadata, annotations (+12 more)

### Community 27 - "4. 設計提案"
Cohesion: 0.12
Nodes (18): 0. 一句話結論, 2. 現成編輯器評估（不使用 bundler、從 CDN 載入）, 3. 別人怎麼做論文筆記（取重點）, 4.10 測試與驗收重點, 4.1 範圍, 4.3 引用語法（沿用 Wiki）, 4.4 API, 4.5 介面位置 (+10 more)

### Community 28 - "auto_highlight"
Cohesion: 0.32
Nodes (6): auto_highlight(), guarded(), one(), _reference_start_page(), find_text_rects(), test_find_text_rects()

### Community 29 - "post"
Cohesion: 0.13
Nodes (16): add_annotation(), add_to_workspace(), AlignMark, AnnotIn, AskIn, chat(), ChatIn, explain_image() (+8 more)

### Community 30 - "_paper_or_404"
Cohesion: 0.16
Nodes (20): cache_get(), cache_set(), s2_paper_id(), stream_chat(), _block_translation(), _cached_text(), _ensure_bib(), explain() (+12 more)

### Community 31 - "conftest.py"
Cohesion: 0.14
Nodes (6): allow_duplicates(), bob(), client(), fake_server(), papers(), pdfs()

### Community 32 - "功能對照"
Cohesion: 0.13
Nodes (12): explain_messages(), _history_block(), image_messages(), local_context(), page_translate_messages(), stream_block_translation(), run(), translate_messages() (+4 more)

### Community 33 - "sse"
Cohesion: 0.16
Nodes (13): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+5 more)

### Community 34 - "登入系統：Keycloak（OIDC）"
Cohesion: 0.12
Nodes (14): current_user(), k8s 部署要一起處理的事（不處理會壞）, Keycloak 端要建的 client, 建議架構：後端當 OIDC client（Authorization Code + PKCE）, 待確認, 既有資料, 登入系統：Keycloak（OIDC）, 設定（`.env`／k8s Secret） (+6 more)

### Community 35 - "loadNote"
Cohesion: 0.16
Nodes (27): 實作狀態（2026-11）, citeChip(), fmtDate(), insertIntoNote(), loadNote(), nbGet(), nbKey(), nbLine() (+19 more)

### Community 36 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

### Community 37 - "_to_claude"
Cohesion: 0.16
Nodes (8): _claude(), _claude_block(), _claude_stream(), _mock_answer(), _to_claude(), vLLM (Qwen3.5-9B), test_cache_breakpoint_only_for_multi_turn(), test_to_claude_conversion()

### Community 38 - "align"
Cohesion: 0.22
Nodes (8): align(), AlignIn, annotations(), API, 並排模式：對應的段落亮起來, 螢光筆同步到譯文, 逐句對應（並排模式）, 閱讀器：選取、螢光筆與中英對照

### Community 39 - "drawOutline"
Cohesion: 0.16
Nodes (14): addCopy(), addMsg(), drawOutline(), enter(), goToPage(), hideFigure(), icon(), loadChat() (+6 more)

### Community 40 - "_header"
Cohesion: 0.21
Nodes (10): chat_messages(), cite_reason_messages(), _est_tokens(), full_text_fits(), _header(), note_draft_messages(), _pages_text(), _paper_body() (+2 more)

### Community 41 - "_paper_or_404"
Cohesion: 0.13
Nodes (19): auth_users(), auto_highlight(), chat_history(), cite_paper(), figure_png(), figures(), _figures(), get_note() (+11 more)

### Community 42 - "UX 第一輪（已定案）"
Cohesion: 0.33
Nodes (5): A. 閱讀頁重新排版, B. 研究主題頁與流程, C. 全站主題切換, UX 第一輪（已定案）, 不做

### Community 43 - "k8s-labse/service.yaml"
Cohesion: 0.17
Nodes (11): apiVersion, kind, metadata, name, name, port, targetPort, app (+3 more)

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
Nodes (4): check(), route(), _test_image(), health()

### Community 51 - "test_paper_cards.py"
Cohesion: 0.25
Nodes (6): byline(), _row(), test_byline(), test_cards_scoped_to_owner(), test_cite_cached_and_year(), test_patch_fields_independently()

### Community 52 - "pvc.yaml"
Cohesion: 0.18
Nodes (10): apiVersion, kind, metadata, name, storage, requests, spec, accessModes (+2 more)

### Community 53 - "部署到 k8s"
Cohesion: 0.18
Nodes (10): 1. 建映像, 2. Keycloak client（沿用 `lantern-local`）, 3. Secret（不要 commit）, 4. 設定與套用, Traefik, 常見問題, 待填, 本機驗證（2026-11-01） (+2 more)

### Community 54 - "kustomization.yaml"
Cohesion: 0.22
Nodes (8): apiVersion, images, name, newName, newTag, kind, namespace, resources

### Community 55 - "k8s-labse/pvc.yaml"
Cohesion: 0.18
Nodes (10): apiVersion, kind, metadata, name, storage, requests, spec, accessModes (+2 more)

### Community 56 - "pymupdf"
Cohesion: 0.47
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
Cohesion: 0.33
Nodes (3): ocr_image(), _ocr_pages(), one()

### Community 68 - "test_align.py"
Cohesion: 0.36
Nodes (5): _fake(), test_align_invalid_falls_back(), test_align_scoped_to_owner(), test_align_valid_substring(), _translated_block()

### Community 71 - "test_notes.py"
Cohesion: 0.29
Nodes (3): test_delete_paper_deletes_note(), test_note_crud_and_conflict(), test_note_draft()

### Community 72 - "recommendations"
Cohesion: 0.40
Nodes (3): _mark_in_library(), recommendations(), 範圍限制

### Community 74 - "k8s-labse/kustomization.yaml"
Cohesion: 0.40
Nodes (4): apiVersion, kind, namespace, resources

### Community 75 - "k8s-labse/namespace.yaml"
Cohesion: 0.40
Nodes (4): apiVersion, kind, metadata, name

### Community 76 - "LaBSE 句向量服務（中英逐句對齊）"
Cohesion: 0.50
Nodes (3): LaBSE 句向量服務（中英逐句對齊）, 要注意, 部署（`deploy/k8s-labse/`）

### Community 77 - "Lantern AI Paper Reader"
Cohesion: 0.67
Nodes (3): /api/health endpoint, backend/main.py (FastAPI app), Lantern AI Paper Reader

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `Semantic Scholar API`, `graphify-out/graph.json`, `graphify usage rules`, `/api/health endpoint` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 463 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `Lantern AI Paper Reader` to `app.js`, `features.py`, `db.py`, `re`, `_to_claude`, `retrieval.py`?**
  _High betweenness centrality (0.193) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `Semantic Scholar API`, `graphify-out/graph.json` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.039473684210526314 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `功能對照`, `re`, `_ThinkStripper`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Should `features.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11083743842364532 - nodes in this community are weakly interconnected._
- **Why does `1. Lantern 現在已經有什麼` connect `drawHighlights` to `4. 設計提案`, `_paper_or_404`, `db.py`, `align`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `test_api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09915966386554621 - nodes in this community are weakly interconnected._