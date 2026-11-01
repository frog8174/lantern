# Graph Report - paper-reader  (2026-11-01)

## Corpus Check
- 55 files · ~47,391 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .example 1, .css 1)

## Summary
- 1211 nodes · 2596 edges · 75 communities (70 shown, 5 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 97 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fd962f03`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- align
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
- _pdf_path
- drawHighlights
- cite.py
- aiCard
- retrieval.py
- pumpTranslation
- data
- Uid
- k8s-labse/ingress.yaml
- check
- test_anthropic.py
- update_wiki
- _paper_or_404
- conftest.py
- features.py
- _ThinkStripper
- 4. 設計提案
- loadNote
- Lantern — 個人用 AI 論文閱讀器
- llm.py
- cache_get
- pymupdf
- renderWiki
- _paper_or_404
- UX 第一輪（已定案）
- k8s-labse/service.yaml
- _stream
- ocr_image
- s2_get
- ingress.yaml
- containers
- service.yaml
- logout
- test_paper_cards.py
- pvc.yaml
- 部署到 k8s
- kustomization.yaml
- k8s-labse/pvc.yaml
- complete_json
- deployment.yaml
- spec
- securityContext
- volumes
- auto_highlight
- namespace.yaml
- livenessProbe
- securityContext
- startupProbe
- spec
- config.py
- 功能對照
- drawOutline
- json
- _ingest
- k8s-labse/kustomization.yaml
- k8s-labse/namespace.yaml
- LaBSE 句向量服務（中英逐句對齊）

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

## Communities (75 total, 5 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.04
Nodes (42): AUTO, calmMotion, card, caretAt(), CITE_STYLES, citeStyles, CM_URLS, COLORS (+34 more)

### Community 1 - "align"
Cohesion: 0.20
Nodes (8): align(), AlignIn, annotations(), _in_block(), API, 並排模式：對應的段落亮起來, 螢光筆同步到譯文, 閱讀器：選取、螢光筆與中英對照

### Community 2 - "test_api.py"
Cohesion: 0.10
Nodes (29): sse(), test_bilingual_blocks(), _id(), test_ai_outline(), test_annotation_kinds(), test_annotations_crud(), test_ask_ai_on_selection(), test_author_year_reference() (+21 more)

### Community 3 - "db.py"
Cohesion: 0.11
Nodes (25): add_annotation(), add_message(), add_wiki_message(), add_workspace(), annotation_paper(), clear_messages(), clear_wiki_messages(), conn() (+17 more)

### Community 4 - "re"
Cohesion: 0.16
Nodes (18): _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), find_texts_rects(), _guess_title(), _is_ref_head() (+10 more)

### Community 5 - "test_units.py"
Cohesion: 0.12
Nodes (12): citing_contexts(), _translatable(), find_figures(), render_page_png(), llm._ThinkStripper, test_citing_contexts(), test_find_figures(), test_page_blocks_and_render() (+4 more)

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
Nodes (23): AlignMark, AnnotIn, ArxivIn, AskIn, ChatIn, CommentIn, create_workspace(), edit_annotation() (+15 more)

### Community 15 - "backend/__init__.py"
Cohesion: 0.06
Nodes (24): align_dp(), _embed(), page_map(), sim(), _spans(), split_en(), split_zh(), _fake() (+16 more)

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.12
Nodes (38): api(), bibtex(), cardPaper(), cardsBusy(), escapeHTML(), importArxiv(), ingest(), loadAsk() (+30 more)

### Community 18 - "_pdf_path"
Cohesion: 0.22
Nodes (7): figure_png(), figures(), _figures(), paper_pdf(), paper_thumb(), _pdf_path(), region_png()

### Community 19 - "drawHighlights"
Cohesion: 0.17
Nodes (23): 1. Lantern 現在已經有什麼, 連續的選取與螢光筆, clearLitAlign(), colorKey(), deleteAnnotation(), drawHighlights(), drawLabels(), flashItem() (+15 more)

### Community 20 - "cite.py"
Cohesion: 0.19
Nodes (18): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+10 more)

### Community 21 - "aiCard"
Cohesion: 0.18
Nodes (19): 逐句對應（並排模式）, addAnnotation(), aiCard(), alignHighlight(), closeAiCard(), commentEditor(), correspond(), explainCrop() (+11 more)

### Community 22 - "retrieval.py"
Cohesion: 0.10
Nodes (13): load_chunks(), save_chunks(), embed(), _bm25(), build_index(), make_chunks(), search(), _tokens() (+5 more)

### Community 23 - "pumpTranslation"
Cohesion: 0.20
Nodes (14): buildPages(), drawRail(), drawTranslation(), fitText(), loadAlignMap(), pumpTranslation(), queueTranslation(), renderPage() (+6 more)

### Community 24 - "data"
Cohesion: 0.07
Nodes (29): apiVersion, data, ALIGN_EMBED_MODEL, ALIGN_EMBED_URL, AUTH_MODE, DISABLE_THINKING, LLM_CONCURRENCY, LLM_CONTEXT_TOKENS (+21 more)

### Community 25 - "Uid"
Cohesion: 0.17
Nodes (17): add_to_workspace(), chat_clear(), delete(), delete_workspace(), papers(), remove_annotation(), remove_from_workspace(), rename_workspace() (+9 more)

### Community 26 - "k8s-labse/ingress.yaml"
Cohesion: 0.10
Nodes (20): cert-manager.io/cluster-issuer, traefik.ingress.kubernetes.io/router.entrypoints, traefik.ingress.kubernetes.io/router.tls, apiVersion, paths, kind, metadata, annotations (+12 more)

### Community 27 - "check"
Cohesion: 0.29
Nodes (4): check(), route(), _test_image(), health()

### Community 28 - "test_anthropic.py"
Cohesion: 0.16
Nodes (11): claude(), _pid(), test_auto_highlight_json(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape(), test_mixed_providers(), test_no_fallback_for_haiku() (+3 more)

### Community 29 - "update_wiki"
Cohesion: 0.15
Nodes (11): list_wiki_messages(), wiki_mark_ingested(), wiki_page(), wiki_pages(), wiki_pending(), wiki_save(), update_wiki(), wiki_ask_messages() (+3 more)

### Community 30 - "_paper_or_404"
Cohesion: 0.21
Nodes (18): stream_chat(), add_annotation(), auto_highlight(), _cached_text(), chat(), explain(), explain_image(), note_draft() (+10 more)

### Community 31 - "conftest.py"
Cohesion: 0.14
Nodes (6): allow_duplicates(), bob(), client(), fake_server(), papers(), pdfs()

### Community 32 - "features.py"
Cohesion: 0.13
Nodes (20): _bib_arxiv(), _bib_llm(), _bib_s2(), chat_messages(), cite_reason_messages(), _est_tokens(), fetch_bib(), full_text_fits() (+12 more)

### Community 34 - "4. 設計提案"
Cohesion: 0.05
Nodes (37): delete_paper(), current_user(), _mark_in_library(), k8s 部署要一起處理的事（不處理會壞）, Keycloak 端要建的 client, 建議架構：後端當 OIDC client（Authorization Code + PKCE）, 待確認, 既有資料 (+29 more)

### Community 35 - "loadNote"
Cohesion: 0.16
Nodes (26): 實作狀態（2026-11）, fmtDate(), insertIntoNote(), loadNote(), nbGet(), nbHeadings(), nbKey(), nbLine() (+18 more)

### Community 36 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

### Community 37 - "llm.py"
Cohesion: 0.15
Nodes (8): _claude(), _claude_block(), _claude_stream(), _mock_answer(), _to_claude(), vLLM (Qwen3.5-9B), test_cache_breakpoint_only_for_multi_turn(), test_to_claude_conversion()

### Community 38 - "cache_get"
Cohesion: 0.19
Nodes (14): cache_get(), cache_set(), s2_paper_id(), align_map(), _align_map(), _block_translation(), _build_align_map(), _ensure_bib() (+6 more)

### Community 39 - "pymupdf"
Cohesion: 0.47
Nodes (5): authoryear(), make_all(), numeric(), scanned(), _text()

### Community 40 - "renderWiki"
Cohesion: 0.23
Nodes (12): 薛西弗斯（等待、完成、空狀態）, addAsk(), addSave(), citeChip(), pushLater(), reach(), renderWiki(), runSummary() (+4 more)

### Community 41 - "_paper_or_404"
Cohesion: 0.10
Nodes (14): auth_config(), auth_users(), chat_history(), cite_paper(), get_note(), livez(), me(), paper() (+6 more)

### Community 42 - "UX 第一輪（已定案）"
Cohesion: 0.33
Nodes (5): A. 閱讀頁重新排版, B. 研究主題頁與流程, C. 全站主題切換, UX 第一輪（已定案）, 不做

### Community 43 - "k8s-labse/service.yaml"
Cohesion: 0.17
Nodes (11): apiVersion, kind, metadata, name, name, port, targetPort, app (+3 more)

### Community 44 - "_stream"
Cohesion: 0.40
Nodes (5): _build(), _create(), _stream(), test_build_adjustments(), test_build_default_sends_vllm_params()

### Community 45 - "ocr_image"
Cohesion: 0.40
Nodes (3): ocr_image(), _ocr_pages(), one()

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

### Community 50 - "logout"
Cohesion: 0.25
Nodes (3): logout(), oidc_callback(), oidc_login()

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

### Community 56 - "complete_json"
Cohesion: 0.18
Nodes (10): ai_outline(), align_span(), _strip_fence(), _wiki_concept(), _wiki_index(), _wiki_plan(), wiki_qa_page(), complete() (+2 more)

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

### Community 61 - "auto_highlight"
Cohesion: 0.32
Nodes (6): auto_highlight(), guarded(), one(), _reference_start_page(), find_text_rects(), test_find_text_rects()

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

### Community 67 - "config.py"
Cohesion: 0.14
Nodes (4): _load_dotenv(), test_delete_paper_deletes_note(), test_note_crud_and_conflict(), test_note_draft()

### Community 68 - "功能對照"
Cohesion: 0.16
Nodes (10): explain_messages(), _history_block(), image_messages(), local_context(), page_translate_messages(), stream_block_translation(), run(), translate_messages() (+2 more)

### Community 69 - "drawOutline"
Cohesion: 0.16
Nodes (14): addCopy(), addMsg(), drawOutline(), enter(), goToPage(), hideFigure(), icon(), loadChat() (+6 more)

### Community 72 - "json"
Cohesion: 0.17
Nodes (8): find_duplicate(), list_annotations(), list_papers(), norm_title(), set_settings(), update_annotation(), update_paper(), recommendations()

### Community 73 - "_ingest"
Cohesion: 0.15
Nodes (12): add_paper(), add_to_workspace(), get_paper(), get_settings(), _auto_wiki(), _duplicate(), _first_doi(), _ingest() (+4 more)

### Community 74 - "k8s-labse/kustomization.yaml"
Cohesion: 0.40
Nodes (4): apiVersion, kind, namespace, resources

### Community 75 - "k8s-labse/namespace.yaml"
Cohesion: 0.40
Nodes (4): apiVersion, kind, metadata, name

### Community 76 - "LaBSE 句向量服務（中英逐句對齊）"
Cohesion: 0.40
Nodes (4): LaBSE 句向量服務（中英逐句對齊）, Lantern 端設定, 要注意, 部署（`deploy/k8s-labse/`）

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `/api/health endpoint`, `BM25 retrieval` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 484 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `features.py`, `app.js`, `db.py`, `re`, `llm.py`?**
  _High betweenness centrality (0.192) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.03623611922852133 - nodes in this community are weakly interconnected._
- **Why does `Lantern — 個人用 AI 論文閱讀器` connect `Lantern — 個人用 AI 論文閱讀器` to `_ThinkStripper`, `功能對照`, `re`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Should `test_api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0975609756097561 - nodes in this community are weakly interconnected._
- **Why does `current_user()` connect `4. 設計提案` to `logout`, `db.py`, `main.py`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Should `db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._