# Graph Report - paper-reader  (2026-11-04)

## Corpus Check
- 64 files · ~50,641 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .example 1, .css 1)

## Summary
- 1414 nodes · 2890 edges · 96 communities (89 shown, 7 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 105 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `58766b8d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- _paper_or_404
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
- llm.py
- Workspace LLM Wiki（MVP）
- escapeHTML
- 閱讀器：選取、螢光筆與中英對照
- drawHighlights
- cite.py
- aiCard
- update_wiki
- pumpTranslation
- data
- find_duplicate
- k8s-labse/ingress.yaml
- 論文聊天的檢索服務：bge-m3 ＋ reranker
- test_anthropic.py
- Uid
- _paper_or_404
- conftest.py
- _header
- backend/__init__.py
- current_user
- loadNote
- drawOutline
- Lantern — 個人用 AI 論文閱讀器
- asyncio
- retrieval.py
- recommendations
- logout
- UX 第一輪（已定案）
- k8s-labse/service.yaml
- renderWiki
- containers
- features.py
- ingress.yaml
- containers
- service.yaml
- spec
- Ingress bge-m3
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
- containers
- spec
- Ingress bge-reranker
- test_paper_cards.py
- k8s-retrieval/pvc.yaml
- _ingest
- k8s-labse/kustomization.yaml
- k8s-labse/namespace.yaml
- LaBSE 句向量服務（中英逐句對齊）
- delete_paper
- test_sentalign.py
- test_notes.py
- find_figures
- 4. 設計提案
- pymupdf
- Service bge-m3
- Service bge-reranker
- annotations
- volumes
- annotations
- volumes
- paper_thumb
- s2_get
- k8s-retrieval/kustomization.yaml
- ports
- ports
- time
- 功能對照

## God Nodes (most connected - your core abstractions)
1. `conn()` - 54 edges
2. `_paper_or_404()` - 39 edges
3. `escapeHTML()` - 39 edges
4. `api()` - 35 edges
5. `data` - 34 edges
6. `sse()` - 34 edges
7. `_id()` - 27 edges
8. `cache_get()` - 25 edges
9. `post()` - 24 edges
10. `cache_set()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `資料表（`backend/db.py`）` --references--> `list_papers()`  [INFERRED]
  docs/paper-cards.md → backend/db.py
- `API` --references--> `_ws_or_404()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `Lantern 端設定` --references--> `_align_map()`  [INFERRED]
  docs/labse.md → backend/main.py
- `螢光筆同步到譯文` --references--> `align()`  [INFERRED]
  docs/reader.md → backend/main.py
- `更新流程（後端，`features.py` 放 prompt）` --references--> `wiki()`  [INFERRED]
  docs/wiki.md → backend/main.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (96 total, 7 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.04
Nodes (50): AUTO, calmMotion, card, cardHTML, cardPaper(), caretAt(), CITE_STYLES, citeStyles (+42 more)

### Community 1 - "_paper_or_404"
Cohesion: 0.10
Nodes (26): cache_get(), cache_set(), align_map(), auth_config(), auth_users(), chat_history(), cite_paper(), _ensure_bib() (+18 more)

### Community 2 - "test_api.py"
Cohesion: 0.10
Nodes (29): sse(), test_bilingual_blocks(), _id(), test_ai_outline(), test_annotation_kinds(), test_annotations_crud(), test_ask_ai_on_selection(), test_author_year_reference() (+21 more)

### Community 3 - "db.py"
Cohesion: 0.12
Nodes (26): annotation_paper(), clear_messages(), clear_wiki_messages(), conn(), delete_annotation(), delete_wiki_exchange(), delete_workspace(), get_note() (+18 more)

### Community 4 - "re"
Cohesion: 0.17
Nodes (15): _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), find_texts_rects(), _guess_title(), _is_ref_head() (+7 more)

### Community 5 - "test_units.py"
Cohesion: 0.15
Nodes (14): _translatable(), _build(), parse_pdf(), ParsedPaper, llm._ThinkStripper, 調整與擴充, test_build_adjustments(), test_build_default_sends_vllm_params() (+6 more)

### Community 6 - "containers"
Cohesion: 0.04
Nodes (47): apiVersion, args, command, env, image, livenessProbe, name, ports (+39 more)

### Community 7 - "Lantern 視覺系統（燈下的那一頁）"
Cohesion: 0.18
Nodes (10): Lantern 視覺系統（燈下的那一頁）, 原則, 字體分工, 捲軸, 用語, 登入頁與標誌, 自動畫重點標籤（無印風）, 自動畫重點的頁邊標籤 (+2 more)

### Community 8 - "fake_api.py"
Cohesion: 0.08
Nodes (13): cos(), _answer(), chat(), claude_messages(), gen(), embeddings(), _err(), files() (+5 more)

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "main.py"
Cohesion: 0.09
Nodes (26): get_user(), add_annotation(), admin_usage(), AlignMark, AnnotIn, ArxivIn, AskIn, CommentIn (+18 more)

### Community 15 - "llm.py"
Cohesion: 0.10
Nodes (16): check(), _claude(), _claude_block(), _claude_stream(), cost_usd(), _create(), _mock_answer(), _record() (+8 more)

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.11
Nodes (39): ago(), allTile(), api(), bibtex(), cardsBusy(), enter(), escapeHTML(), focusWikiTitle() (+31 more)

### Community 18 - "閱讀器：選取、螢光筆與中英對照"
Cohesion: 0.29
Nodes (7): 並排模式：對應的段落亮起來, 螢光筆同步到譯文, 連續的選取與螢光筆, 閱讀器：選取、螢光筆與中英對照, mergeRects(), readSelection(), selRects()

### Community 19 - "drawHighlights"
Cohesion: 0.22
Nodes (19): 1. Lantern 現在已經有什麼, clearLitAlign(), colorKey(), deleteAnnotation(), drawHighlights(), drawLabels(), flashItem(), icon() (+11 more)

### Community 20 - "cite.py"
Cohesion: 0.19
Nodes (18): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+10 more)

### Community 21 - "aiCard"
Cohesion: 0.18
Nodes (19): 逐句對應（並排模式）, addAnnotation(), aiCard(), alignHighlight(), closeAiCard(), commentEditor(), correspond(), explainCrop() (+11 more)

### Community 22 - "update_wiki"
Cohesion: 0.13
Nodes (13): list_wiki_messages(), wiki_mark_ingested(), wiki_page(), wiki_pages(), wiki_pending(), wiki_save(), update_wiki(), wiki_ask_messages() (+5 more)

### Community 23 - "pumpTranslation"
Cohesion: 0.18
Nodes (16): buildPages(), clearCrop(), drawRail(), drawTranslation(), fitText(), loadAlignMap(), pumpTranslation(), queueTranslation() (+8 more)

### Community 24 - "data"
Cohesion: 0.05
Nodes (39): apiVersion, data, ADMIN_USERS, ALIGN_EMBED_MODEL, ALIGN_EMBED_URL, AUTH_MODE, DISABLE_THINKING, EMBED_BASE_URL (+31 more)

### Community 26 - "k8s-labse/ingress.yaml"
Cohesion: 0.10
Nodes (20): cert-manager.io/cluster-issuer, traefik.ingress.kubernetes.io/router.entrypoints, traefik.ingress.kubernetes.io/router.tls, apiVersion, paths, kind, metadata, annotations (+12 more)

### Community 27 - "論文聊天的檢索服務：bge-m3 ＋ reranker"
Cohesion: 0.29
Nodes (6): Lantern 端設定, 查詢流程（`retrieval.search()`）, 要注意, 論文聊天的檢索服務：bge-m3 ＋ reranker, 部署（`deploy/k8s-retrieval/`）, 重建索引

### Community 28 - "test_anthropic.py"
Cohesion: 0.17
Nodes (11): claude(), _pid(), test_auto_highlight_json(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape(), test_mixed_providers(), test_no_fallback_for_haiku() (+3 more)

### Community 29 - "Uid"
Cohesion: 0.18
Nodes (17): add_to_workspace(), chat_clear(), delete(), delete_workspace(), papers(), remove_annotation(), remove_from_workspace(), rename_workspace() (+9 more)

### Community 30 - "_paper_or_404"
Cohesion: 0.15
Nodes (18): stream_chat(), _cached_text(), chat(), ChatIn, explain(), explain_image(), ImageIn, note_draft() (+10 more)

### Community 31 - "conftest.py"
Cohesion: 0.14
Nodes (6): allow_duplicates(), bob(), client(), fake_server(), papers(), pdfs()

### Community 32 - "_header"
Cohesion: 0.23
Nodes (9): chat_messages(), _est_tokens(), full_text_fits(), _header(), note_draft_messages(), _pages_text(), _paper_body(), summary_messages() (+1 more)

### Community 33 - "backend/__init__.py"
Cohesion: 0.12
Nodes (5): FakeKC, _oidc(), test_oidc_login_creates_user_and_session(), test_oidc_login_failure_redirects(), test_auto_translate_setting()

### Community 34 - "current_user"
Cohesion: 0.10
Nodes (17): current_user(), k8s 部署要一起處理的事（不處理會壞）, Keycloak 端要建的 client, 建議架構：後端當 OIDC client（Authorization Code + PKCE）, 待確認, 既有資料, 登入系統：Keycloak（OIDC）, 設定（`.env`／k8s Secret） (+9 more)

### Community 35 - "loadNote"
Cohesion: 0.13
Nodes (30): 實作狀態（2026-11）, fmtDate(), insertIntoNote(), loadNote(), nbGet(), nbHead(), nbHeadings(), nbKey() (+22 more)

### Community 36 - "drawOutline"
Cohesion: 0.29
Nodes (7): drawOutline(), goToPage(), hideFigure(), markOutline(), renderOutline(), setLibDrawer(), showFigure()

### Community 37 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.11
Nodes (13): _ThinkStripper, Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 名詞解釋, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API (+5 more)

### Community 38 - "asyncio"
Cohesion: 0.19
Nodes (9): align(), _align_map(), AlignIn, annotations(), _block_translation(), _build_align_map(), health(), _in_block() (+1 more)

### Community 39 - "retrieval.py"
Cohesion: 0.08
Nodes (16): embed(), rerank(), _bm25(), english_query(), make_chunks(), _not_refs(), search(), _tokens() (+8 more)

### Community 40 - "recommendations"
Cohesion: 0.40
Nodes (3): _mark_in_library(), recommendations(), 範圍限制

### Community 41 - "logout"
Cohesion: 0.25
Nodes (3): logout(), oidc_callback(), oidc_login()

### Community 42 - "UX 第一輪（已定案）"
Cohesion: 0.33
Nodes (5): A. 閱讀頁重新排版, B. 研究主題頁與流程, C. 全站主題切換, UX 第一輪（已定案）, 不做

### Community 43 - "k8s-labse/service.yaml"
Cohesion: 0.17
Nodes (11): apiVersion, kind, metadata, name, name, port, targetPort, app (+3 more)

### Community 44 - "renderWiki"
Cohesion: 0.17
Nodes (16): 薛西弗斯（等待、完成、空狀態）, addAsk(), addCopy(), addMsg(), addSave(), citeChip(), loadChat(), pushLater() (+8 more)

### Community 45 - "containers"
Cohesion: 0.17
Nodes (12): args, command, env, image, livenessProbe, name, ports, readinessProbe (+4 more)

### Community 46 - "features.py"
Cohesion: 0.16
Nodes (13): _bib_arxiv(), _bib_llm(), _bib_s2(), cite_reason_messages(), citing_contexts(), fetch_bib(), _guess_ref_title(), lookup_reference() (+5 more)

### Community 47 - "ingress.yaml"
Cohesion: 0.10
Nodes (20): cert-manager.io/cluster-issuer, traefik.ingress.kubernetes.io/router.entrypoints, traefik.ingress.kubernetes.io/router.tls, apiVersion, paths, kind, metadata, annotations (+12 more)

### Community 48 - "containers"
Cohesion: 0.17
Nodes (12): envFrom, image, name, ports, readinessProbe, resources, volumeMounts, httpGet (+4 more)

### Community 49 - "service.yaml"
Cohesion: 0.17
Nodes (11): apiVersion, kind, metadata, name, name, port, targetPort, app (+3 more)

### Community 50 - "spec"
Cohesion: 0.18
Nodes (12): apiVersion, kind, metadata, spec, Deployment bge-m3, app, labels, replicas (+4 more)

### Community 51 - "Ingress bge-m3"
Cohesion: 0.17
Nodes (12): Ingress bge-m3, paths, apiVersion, kind, spec, host, http, ingressClassName (+4 more)

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
Cohesion: 0.16
Nodes (10): align_span(), _strip_fence(), suggested_questions(), _wiki_concept(), _wiki_index(), _wiki_plan(), wiki_qa_page(), complete() (+2 more)

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

### Community 68 - "containers"
Cohesion: 0.17
Nodes (12): args, command, env, image, livenessProbe, name, ports, readinessProbe (+4 more)

### Community 69 - "spec"
Cohesion: 0.18
Nodes (12): apiVersion, kind, metadata, spec, Deployment bge-reranker, app, labels, replicas (+4 more)

### Community 70 - "Ingress bge-reranker"
Cohesion: 0.17
Nodes (12): Ingress bge-reranker, paths, apiVersion, kind, spec, host, http, ingressClassName (+4 more)

### Community 71 - "test_paper_cards.py"
Cohesion: 0.25
Nodes (6): byline(), _row(), test_byline(), test_cards_scoped_to_owner(), test_cite_cached_and_year(), test_patch_fields_independently()

### Community 72 - "k8s-retrieval/pvc.yaml"
Cohesion: 0.18
Nodes (10): apiVersion, kind, metadata, name, storage, requests, spec, accessModes (+2 more)

### Community 73 - "_ingest"
Cohesion: 0.18
Nodes (10): add_to_workspace(), get_paper(), get_settings(), _auto_wiki(), _duplicate(), _first_doi(), _ingest(), _ocr_pages() (+2 more)

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

### Community 78 - "test_sentalign.py"
Cohesion: 0.10
Nodes (19): align_dp(), _embed(), page_map(), sim(), _spans(), split_en(), split_zh(), _fake() (+11 more)

### Community 79 - "test_notes.py"
Cohesion: 0.29
Nodes (3): test_delete_paper_deletes_note(), test_note_crud_and_conflict(), test_note_draft()

### Community 81 - "4. 設計提案"
Cohesion: 0.12
Nodes (18): 0. 一句話結論, 2. 現成編輯器評估（不使用 bundler、從 CDN 載入）, 3. 別人怎麼做論文筆記（取重點）, 4.10 測試與驗收重點, 4.1 範圍, 4.3 引用語法（沿用 Wiki）, 4.4 API, 4.5 介面位置 (+10 more)

### Community 82 - "pymupdf"
Cohesion: 0.35
Nodes (6): _is_scanned(), authoryear(), make_all(), numeric(), scanned(), _text()

### Community 83 - "Service bge-m3"
Cohesion: 0.22
Nodes (8): Service bge-m3, app, app, matchLabels, apiVersion, kind, spec, selector

### Community 84 - "Service bge-reranker"
Cohesion: 0.22
Nodes (8): Service bge-reranker, app, app, matchLabels, apiVersion, kind, spec, selector

### Community 87 - "annotations"
Cohesion: 0.29
Nodes (7): cert-manager.io/cluster-issuer, traefik.ingress.kubernetes.io/router.entrypoints, traefik.ingress.kubernetes.io/router.tls, metadata, annotations, name, metadata

### Community 88 - "volumes"
Cohesion: 0.29
Nodes (7): kubernetes.io/hostname, nodeSelector, volumes, spec, emptyDir, name, persistentVolumeClaim

### Community 89 - "annotations"
Cohesion: 0.29
Nodes (7): cert-manager.io/cluster-issuer, traefik.ingress.kubernetes.io/router.entrypoints, traefik.ingress.kubernetes.io/router.tls, metadata, annotations, name, metadata

### Community 90 - "volumes"
Cohesion: 0.29
Nodes (7): kubernetes.io/hostname, nodeSelector, volumes, spec, emptyDir, name, persistentVolumeClaim

### Community 91 - "paper_thumb"
Cohesion: 0.24
Nodes (7): auto_highlight(), figure_png(), paper_pdf(), paper_thumb(), _pdf_path(), region_png(), render_page_png()

### Community 92 - "s2_get"
Cohesion: 0.13
Nodes (11): _check(), recommend(), s2_get(), s2_paper_id(), S2Error, API, 前端（論文卡）, 決定 (+3 more)

### Community 95 - "k8s-retrieval/kustomization.yaml"
Cohesion: 0.40
Nodes (4): apiVersion, kind, namespace, resources

### Community 96 - "ports"
Cohesion: 0.50
Nodes (4): name, port, targetPort, ports

### Community 97 - "ports"
Cohesion: 0.50
Nodes (4): name, port, targetPort, ports

### Community 98 - "time"
Cohesion: 0.14
Nodes (10): add_annotation(), add_message(), add_paper(), add_usage(), add_wiki_message(), add_workspace(), new_id(), save_note() (+2 more)

### Community 99 - "功能對照"
Cohesion: 0.16
Nodes (10): ai_outline(), explain_messages(), _history_block(), image_messages(), local_context(), stream_block_translation(), run(), ocr_image() (+2 more)

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `vLLM (Qwen3.5-9B)`, `/api/health endpoint` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 597 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `app.js`, `db.py`, `re`, `features.py`, `llm.py`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.035897435897435895 - nodes in this community are weakly interconnected._
- **Why does `_ThinkStripper` connect `Lantern — 個人用 AI 論文閱讀器` to `test_units.py`, `llm.py`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Should `_paper_or_404` be split into smaller, more focused modules?**
  _Cohesion score 0.10158730158730159 - nodes in this community are weakly interconnected._
- **Why does `current_user()` connect `current_user` to `logout`, `main.py`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Should `test_api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10128205128205128 - nodes in this community are weakly interconnected._