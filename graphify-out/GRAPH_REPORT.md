# Graph Report - paper-reader  (2026-11-01)

## Corpus Check
- 55 files · ~46,696 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .example 1, .css 1)

## Summary
- 1205 nodes · 2589 edges · 78 communities (69 shown, 9 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 97 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8c1ae124`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- time
- test_api.py
- db.py
- re
- _header
- containers
- Lantern 視覺系統（燈下的那一頁）
- fake_api.py
- Frontend UI Layout
- Static File Caching
- Graphify Graph Output
- Lantern Paper Reader
- main.py
- CLAUDE.md
- sentalign.py
- Workspace LLM Wiki（MVP）
- escapeHTML
- backend/__init__.py
- drawHighlights
- cite.py
- aiCard
- cache_get
- pumpTranslation
- data
- Uid
- k8s-labse/ingress.yaml
- 4. 設計提案
- get_paper
- update_wiki
- _paper_or_404
- conftest.py
- features.py
- test_sentalign.py
- 登入系統：Keycloak（OIDC）
- loadNote
- Lantern — 個人用 AI 論文閱讀器
- _to_claude
- align
- _pdf_path
- streamInto
- get
- UX 第一輪（已定案）
- k8s-labse/service.yaml
- test_workspaces.py
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
- test_align.py
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
- local_context
- drawOutline
- config.py
- wiki_update
- find_duplicate
- _ingest
- k8s-labse/kustomization.yaml
- k8s-labse/namespace.yaml
- LaBSE 句向量服務（中英逐句對齊）
- delete_paper

## God Nodes (most connected - your core abstractions)
1. `conn()` - 50 edges
2. `_paper_or_404()` - 38 edges
3. `escapeHTML()` - 38 edges
4. `api()` - 34 edges
5. `sse()` - 33 edges
6. `_id()` - 27 edges
7. `cache_get()` - 24 edges
8. `data` - 24 edges
9. `cache_set()` - 20 edges
10. `openPaper()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `資料表（`backend/db.py`）` --references--> `list_papers()`  [INFERRED]
  docs/paper-cards.md → backend/db.py
- `API` --references--> `_ws_or_404()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `Lantern 端設定` --references--> `_align_map()`  [INFERRED]
  docs/labse.md → backend/main.py
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

## Communities (78 total, 9 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.04
Nodes (45): AUTO, calmMotion, card, cardPaper(), caretAt(), CITE_STYLES, citeStyles, CM_URLS (+37 more)

### Community 1 - "time"
Cohesion: 0.20
Nodes (8): add_annotation(), add_message(), add_wiki_message(), add_workspace(), init(), new_id(), save_note(), upsert_user()

### Community 2 - "test_api.py"
Cohesion: 0.06
Nodes (43): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+35 more)

### Community 3 - "db.py"
Cohesion: 0.13
Nodes (23): annotation_paper(), clear_messages(), clear_wiki_messages(), conn(), delete_annotation(), delete_wiki_exchange(), delete_workspace(), get_note() (+15 more)

### Community 4 - "re"
Cohesion: 0.05
Nodes (49): auto_highlight(), guarded(), one(), chat_messages(), _reference_start_page(), stream_block_translation(), run(), _translatable() (+41 more)

### Community 5 - "_header"
Cohesion: 0.18
Nodes (10): cite_reason_messages(), citing_contexts(), _est_tokens(), full_text_fits(), _header(), note_draft_messages(), _paper_body(), summary_messages() (+2 more)

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
Cohesion: 0.10
Nodes (21): add_annotation(), AlignMark, AnnotIn, ArxivIn, CommentIn, create_workspace(), edit_annotation(), edit_paper() (+13 more)

### Community 15 - "sentalign.py"
Cohesion: 0.24
Nodes (7): align_dp(), _embed(), page_map(), sim(), _spans(), split_en(), split_zh()

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.12
Nodes (39): addAsk(), addSave(), api(), bibtex(), cardsBusy(), citeChip(), escapeHTML(), importArxiv() (+31 more)

### Community 18 - "backend/__init__.py"
Cohesion: 0.23
Nodes (4): FakeKC, _oidc(), test_oidc_login_creates_user_and_session(), test_oidc_login_failure_redirects()

### Community 19 - "drawHighlights"
Cohesion: 0.17
Nodes (22): 1. Lantern 現在已經有什麼, 連續的選取與螢光筆, clearLitAlign(), colorKey(), deleteAnnotation(), drawHighlights(), drawLabels(), flashItem() (+14 more)

### Community 20 - "cite.py"
Cohesion: 0.19
Nodes (18): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+10 more)

### Community 21 - "aiCard"
Cohesion: 0.14
Nodes (23): 逐句對應（並排模式）, addAnnotation(), aiCard(), alignHighlight(), closeAiCard(), commentEditor(), correspond(), explainCrop() (+15 more)

### Community 22 - "cache_get"
Cohesion: 0.16
Nodes (17): cache_get(), cache_set(), s2_paper_id(), cite_paper(), _ensure_bib(), figures(), _figures(), outline_ai() (+9 more)

### Community 23 - "pumpTranslation"
Cohesion: 0.22
Nodes (13): buildPages(), drawRail(), drawTranslation(), fitText(), loadAlignMap(), pumpTranslation(), queueTranslation(), renderPage() (+5 more)

### Community 24 - "data"
Cohesion: 0.07
Nodes (29): apiVersion, data, ALIGN_EMBED_MODEL, ALIGN_EMBED_URL, AUTH_MODE, DISABLE_THINKING, LLM_CONCURRENCY, LLM_CONTEXT_TOKENS (+21 more)

### Community 25 - "Uid"
Cohesion: 0.20
Nodes (16): add_to_workspace(), chat_clear(), delete(), delete_workspace(), papers(), remove_annotation(), remove_from_workspace(), rename_workspace() (+8 more)

### Community 26 - "k8s-labse/ingress.yaml"
Cohesion: 0.10
Nodes (20): cert-manager.io/cluster-issuer, traefik.ingress.kubernetes.io/router.entrypoints, traefik.ingress.kubernetes.io/router.tls, apiVersion, paths, kind, metadata, annotations (+12 more)

### Community 27 - "4. 設計提案"
Cohesion: 0.12
Nodes (18): 0. 一句話結論, 2. 現成編輯器評估（不使用 bundler、從 CDN 載入）, 3. 別人怎麼做論文筆記（取重點）, 4.10 測試與驗收重點, 4.1 範圍, 4.3 引用語法（沿用 Wiki）, 4.4 API, 4.5 介面位置 (+10 more)

### Community 28 - "get_paper"
Cohesion: 0.20
Nodes (7): get_paper(), list_papers(), _mark_in_library(), _prefetch_bib(), _pretranslate(), recommendations(), 範圍限制

### Community 29 - "update_wiki"
Cohesion: 0.15
Nodes (12): list_wiki_messages(), wiki_mark_ingested(), wiki_page(), wiki_pages(), wiki_pending(), wiki_save(), update_wiki(), wiki_ask_messages() (+4 more)

### Community 30 - "_paper_or_404"
Cohesion: 0.18
Nodes (16): stream_chat(), AskIn, _cached_text(), chat(), ChatIn, explain(), explain_image(), ImageIn (+8 more)

### Community 31 - "conftest.py"
Cohesion: 0.09
Nodes (11): allow_duplicates(), bob(), client(), fake_server(), papers(), pdfs(), authoryear(), make_all() (+3 more)

### Community 32 - "features.py"
Cohesion: 0.11
Nodes (22): ai_outline(), align_span(), _bib_arxiv(), _bib_llm(), _bib_s2(), fetch_bib(), _guess_ref_title(), lookup_reference() (+14 more)

### Community 33 - "test_sentalign.py"
Cohesion: 0.25
Nodes (7): _cut(), _fake_embed(), _sim_from(), test_dp_merge_and_skip(), test_dp_one_to_one(), test_split_en_keeps_abbreviations_and_offsets(), test_split_zh()

### Community 34 - "登入系統：Keycloak（OIDC）"
Cohesion: 0.12
Nodes (14): current_user(), k8s 部署要一起處理的事（不處理會壞）, Keycloak 端要建的 client, 建議架構：後端當 OIDC client（Authorization Code + PKCE）, 待確認, 既有資料, 登入系統：Keycloak（OIDC）, 設定（`.env`／k8s Secret） (+6 more)

### Community 35 - "loadNote"
Cohesion: 0.15
Nodes (27): 實作狀態（2026-11）, fmtDate(), insertIntoNote(), loadNote(), nbGet(), nbHeadings(), nbKey(), nbLine() (+19 more)

### Community 36 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

### Community 37 - "_to_claude"
Cohesion: 0.15
Nodes (8): _claude(), _claude_block(), _claude_stream(), _mock_answer(), _to_claude(), vLLM (Qwen3.5-9B), test_cache_breakpoint_only_for_multi_turn(), test_to_claude_conversion()

### Community 38 - "align"
Cohesion: 0.14
Nodes (12): align(), align_map(), _align_map(), AlignIn, annotations(), _block_translation(), _build_align_map(), _in_block() (+4 more)

### Community 39 - "_pdf_path"
Cohesion: 0.24
Nodes (7): auto_highlight(), figure_png(), paper_pdf(), paper_thumb(), _pdf_path(), region_png(), render_page_png()

### Community 40 - "streamInto"
Cohesion: 0.27
Nodes (10): 薛西弗斯（等待、完成、空狀態）, addCopy(), addMsg(), loadChat(), pushLater(), reach(), runSummary(), sendChat() (+2 more)

### Community 41 - "get"
Cohesion: 0.08
Nodes (15): auth_config(), auth_users(), chat_history(), get_note(), livez(), logout(), me(), oidc_callback() (+7 more)

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

### Community 56 - "test_align.py"
Cohesion: 0.36
Nodes (5): _fake(), test_align_invalid_falls_back(), test_align_scoped_to_owner(), test_align_valid_substring(), _translated_block()

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

### Community 68 - "local_context"
Cohesion: 0.29
Nodes (5): explain_messages(), _history_block(), image_messages(), local_context(), _pages_text()

### Community 69 - "drawOutline"
Cohesion: 0.25
Nodes (8): drawOutline(), enter(), goToPage(), markOutline(), openAt(), openCite(), renderOutline(), setLibDrawer()

### Community 73 - "_ingest"
Cohesion: 0.31
Nodes (7): add_paper(), add_to_workspace(), get_settings(), _auto_wiki(), _duplicate(), _first_doi(), _ingest()

### Community 74 - "k8s-labse/kustomization.yaml"
Cohesion: 0.40
Nodes (4): apiVersion, kind, namespace, resources

### Community 75 - "k8s-labse/namespace.yaml"
Cohesion: 0.40
Nodes (4): apiVersion, kind, metadata, name

### Community 76 - "LaBSE 句向量服務（中英逐句對齊）"
Cohesion: 0.40
Nodes (4): LaBSE 句向量服務（中英逐句對齊）, Lantern 端設定, 要注意, 部署（`deploy/k8s-labse/`）

### Community 77 - "delete_paper"
Cohesion: 0.67
Nodes (3): delete_paper(), 4.2 資料表（`backend/db.py`）, 資料表（`backend/db.py`）

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `Semantic Scholar API`, `vLLM (Qwen3.5-9B)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 479 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `re` to `features.py`, `app.js`, `db.py`, `_to_claude`?**
  _High betweenness centrality (0.190) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.039473684210526314 - nodes in this community are weakly interconnected._
- **Why does `current_user()` connect `登入系統：Keycloak（OIDC）` to `get`, `db.py`, `main.py`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Should `test_api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05827505827505827 - nodes in this community are weakly interconnected._
- **Why does `chat()` connect `fake_api.py` to `db.py`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Should `db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12688172043010754 - nodes in this community are weakly interconnected._