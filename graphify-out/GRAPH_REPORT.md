# Graph Report - paper-reader  (2026-11-04)

## Corpus Check
- 70 files · ~57,547 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .example 1, .css 1)

## Summary
- 1463 nodes · 2995 edges · 100 communities (91 shown, 9 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 112 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `684b9d41`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- Uid
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
- annotations
- drawHighlights
- cite.py
- aiCard
- test_chat_rag.py
- pumpTranslation
- data
- 聊天策略評估 2026-11-04 09:45
- k8s-labse/ingress.yaml
- check
- test_anthropic.py
- backend/__init__.py
- _paper_or_404
- conftest.py
- test_sentalign.py
- backend/__init__.py
- current_user
- loadNote
- drawOutline
- Lantern — 個人用 AI 論文閱讀器
- cache_get
- retrieval.py
- s2_paper_id
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
- chat_eval.py
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
- test_workspaces.py
- sentalign.py
- test_notes.py
- _ThinkStripper
- 4. 設計提案
- pymupdf
- Service bge-m3
- Service bge-reranker
- paintWsCards
- _stream
- annotations
- volumes
- annotations
- volumes
- paper_thumb
- s2_get
- _to_claude
- k8s-retrieval/kustomization.yaml
- ports
- ports
- 聊天：段落累積式 RAG
- ocr_image

## God Nodes (most connected - your core abstractions)
1. `conn()` - 56 edges
2. `_paper_or_404()` - 39 edges
3. `escapeHTML()` - 39 edges
4. `sse()` - 36 edges
5. `api()` - 35 edges
6. `data` - 34 edges
7. `_id()` - 27 edges
8. `cache_get()` - 26 edges
9. `post()` - 24 edges
10. `cache_set()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `資料表（`backend/db.py`）` --references--> `list_papers()`  [INFERRED]
  docs/paper-cards.md → backend/db.py
- `為什麼要這樣設計` --references--> `_to_claude()`  [INFERRED]
  docs/chat-rag.md → backend/llm.py
- `API` --references--> `_ws_or_404()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `Lantern 端設定` --references--> `_align_map()`  [INFERRED]
  docs/labse.md → backend/main.py
- `螢光筆同步到譯文` --references--> `align()`  [INFERRED]
  docs/reader.md → backend/main.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (100 total, 9 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.04
Nodes (46): AUTO, calmMotion, card, cardHTML, caretAt(), CITE_STYLES, citeStyles, CM_URLS (+38 more)

### Community 1 - "Uid"
Cohesion: 0.09
Nodes (31): get_user(), admin_usage(), auth_config(), auth_users(), chat_clear(), chat_history(), cite_paper(), delete() (+23 more)

### Community 2 - "test_api.py"
Cohesion: 0.09
Nodes (27): _id(), test_ai_outline(), test_annotation_kinds(), test_annotations_crud(), test_ask_ai_on_selection(), test_author_year_reference(), test_auto_highlight_finds_sentence(), test_bilingual_blocks() (+19 more)

### Community 3 - "db.py"
Cohesion: 0.06
Nodes (56): add_annotation(), add_message(), add_paper(), add_to_workspace(), add_usage(), add_wiki_message(), add_workspace(), annotation_paper() (+48 more)

### Community 4 - "re"
Cohesion: 0.12
Nodes (21): _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), find_figures(), find_texts_rects(), _guess_title() (+13 more)

### Community 5 - "test_units.py"
Cohesion: 0.13
Nodes (11): citing_contexts(), stream_block_translation(), run(), _translatable(), llm._ThinkStripper, test_citing_contexts(), test_page_blocks_and_render(), test_parse_numeric() (+3 more)

### Community 6 - "containers"
Cohesion: 0.04
Nodes (47): apiVersion, args, command, env, image, livenessProbe, name, ports (+39 more)

### Community 7 - "Lantern 視覺系統（燈下的那一頁）"
Cohesion: 0.18
Nodes (10): Lantern 視覺系統（燈下的那一頁）, 原則, 字體分工, 捲軸, 用語, 登入頁與標誌, 自動畫重點標籤（無印風）, 自動畫重點的頁邊標籤 (+2 more)

### Community 8 - "fake_api.py"
Cohesion: 0.09
Nodes (13): cos(), _answer(), chat(), claude_messages(), gen(), embeddings(), _err(), files() (+5 more)

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "main.py"
Cohesion: 0.09
Nodes (25): add_to_workspace(), AlignIn, AlignMark, AnnotIn, AskIn, ChatIn, CommentIn, create_workspace() (+17 more)

### Community 15 - "llm.py"
Cohesion: 0.16
Nodes (7): _claude_stream(), cost_usd(), embed(), _mock_answer(), _record(), rerank(), vLLM (Qwen3.5-9B)

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.12
Nodes (37): ago(), allTile(), api(), bibtex(), cardsBusy(), enter(), escapeHTML(), importArxiv() (+29 more)

### Community 18 - "annotations"
Cohesion: 0.33
Nodes (5): annotations(), API, 並排模式：對應的段落亮起來, 螢光筆同步到譯文, 閱讀器：選取、螢光筆與中英對照

### Community 19 - "drawHighlights"
Cohesion: 0.16
Nodes (24): 1. Lantern 現在已經有什麼, 連續的選取與螢光筆, clearLitAlign(), colorKey(), deleteAnnotation(), drawHighlights(), drawLabels(), flashItem() (+16 more)

### Community 20 - "cite.py"
Cohesion: 0.19
Nodes (18): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+10 more)

### Community 21 - "aiCard"
Cohesion: 0.18
Nodes (19): 逐句對應（並排模式）, addAnnotation(), aiCard(), alignHighlight(), closeAiCard(), commentEditor(), correspond(), explainCrop() (+11 more)

### Community 22 - "test_chat_rag.py"
Cohesion: 0.22
Nodes (8): fake(), run(), test_current_page_sent_once(), test_endpoint_stores_ctx(), test_full_strategy_matches_old_behaviour(), test_global_question_uses_summary_then_full(), test_passages_accumulate_without_resending(), test_switches_to_full_text_after_many_turns()

### Community 23 - "pumpTranslation"
Cohesion: 0.18
Nodes (16): buildPages(), clearCrop(), drawRail(), drawTranslation(), fitText(), loadAlignMap(), pumpTranslation(), queueTranslation() (+8 more)

### Community 24 - "data"
Cohesion: 0.05
Nodes (39): apiVersion, data, ADMIN_USERS, ALIGN_EMBED_MODEL, ALIGN_EMBED_URL, AUTH_MODE, DISABLE_THINKING, EMBED_BASE_URL (+31 more)

### Community 25 - "聊天策略評估 2026-11-04 09:45"
Cohesion: 0.17
Nodes (11): Adapting Vision Foundation Models for Plant Phenotyping, Image recognition-based petal arrangement estimation, Leaf only SAM: A segment anything pipeline for zero-shot automated leaf segmenta, Translating High-Throughput Phenotyping into Genetic Gain, 依題型平均分, 扣分原因, 總表（未校正）, 聊天策略評估 2026-11-04 09:45 (+3 more)

### Community 26 - "k8s-labse/ingress.yaml"
Cohesion: 0.10
Nodes (20): cert-manager.io/cluster-issuer, traefik.ingress.kubernetes.io/router.entrypoints, traefik.ingress.kubernetes.io/router.tls, apiVersion, paths, kind, metadata, annotations (+12 more)

### Community 27 - "check"
Cohesion: 0.20
Nodes (5): check(), _claude(), route(), _test_image(), test_route_prefixes()

### Community 28 - "test_anthropic.py"
Cohesion: 0.17
Nodes (13): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+5 more)

### Community 29 - "backend/__init__.py"
Cohesion: 0.31
Nodes (5): _fake(), test_align_invalid_falls_back(), test_align_scoped_to_owner(), test_align_valid_substring(), _translated_block()

### Community 30 - "_paper_or_404"
Cohesion: 0.21
Nodes (19): stream_chat(), add_annotation(), auto_highlight(), _cached_text(), chat(), explain(), explain_image(), note_draft() (+11 more)

### Community 31 - "conftest.py"
Cohesion: 0.14
Nodes (6): allow_duplicates(), bob(), client(), fake_server(), papers(), pdfs()

### Community 32 - "test_sentalign.py"
Cohesion: 0.27
Nodes (6): _cut(), _fake_embed(), _sim_from(), test_dp_one_to_one(), test_split_en_keeps_abbreviations_and_offsets(), test_split_zh()

### Community 33 - "backend/__init__.py"
Cohesion: 0.23
Nodes (4): FakeKC, _oidc(), test_oidc_login_creates_user_and_session(), test_oidc_login_failure_redirects()

### Community 34 - "current_user"
Cohesion: 0.10
Nodes (17): current_user(), k8s 部署要一起處理的事（不處理會壞）, Keycloak 端要建的 client, 建議架構：後端當 OIDC client（Authorization Code + PKCE）, 待確認, 既有資料, 登入系統：Keycloak（OIDC）, 設定（`.env`／k8s Secret） (+9 more)

### Community 35 - "loadNote"
Cohesion: 0.15
Nodes (28): 實作狀態（2026-11）, insertIntoNote(), loadNote(), nbGet(), nbHead(), nbHeadings(), nbKey(), nbLine() (+20 more)

### Community 36 - "drawOutline"
Cohesion: 0.29
Nodes (7): drawOutline(), goToPage(), hideFigure(), markOutline(), renderOutline(), setLibDrawer(), showFigure()

### Community 37 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

### Community 38 - "cache_get"
Cohesion: 0.14
Nodes (18): cache_get(), cache_set(), align(), align_map(), _align_map(), _block_translation(), _build_align_map(), _ensure_bib() (+10 more)

### Community 39 - "retrieval.py"
Cohesion: 0.07
Nodes (24): new_context(), plan_question(), _bm25(), english_query(), make_chunks(), _not_refs(), _pieces(), search() (+16 more)

### Community 40 - "s2_paper_id"
Cohesion: 0.24
Nodes (7): _check(), recommend(), s2_paper_id(), _mark_in_library(), recommendations(), related(), 範圍限制

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
Cohesion: 0.09
Nodes (29): ai_outline(), _bib_arxiv(), _bib_llm(), _bib_s2(), chat_messages(), cite_reason_messages(), _est_tokens(), _expand() (+21 more)

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

### Community 56 - "chat_eval.py"
Cohesion: 0.14
Nodes (16): align_span(), _strip_fence(), _wiki_concept(), _wiki_index(), _wiki_plan(), wiki_qa_page(), complete(), complete_json() (+8 more)

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
Cohesion: 0.09
Nodes (12): ArxivIn, _auto_wiki(), _duplicate(), _first_doi(), import_url(), _ingest(), _ocr_pages(), _prefetch_bib() (+4 more)

### Community 74 - "k8s-labse/kustomization.yaml"
Cohesion: 0.40
Nodes (4): apiVersion, kind, namespace, resources

### Community 75 - "k8s-labse/namespace.yaml"
Cohesion: 0.40
Nodes (4): apiVersion, kind, metadata, name

### Community 76 - "LaBSE 句向量服務（中英逐句對齊）"
Cohesion: 0.40
Nodes (4): LaBSE 句向量服務（中英逐句對齊）, Lantern 端設定, 要注意, 部署（`deploy/k8s-labse/`）

### Community 78 - "sentalign.py"
Cohesion: 0.21
Nodes (8): align_dp(), _embed(), page_map(), sim(), _spans(), split_en(), split_zh(), test_dp_merge_and_skip()

### Community 79 - "test_notes.py"
Cohesion: 0.29
Nodes (3): test_delete_paper_deletes_note(), test_note_crud_and_conflict(), test_note_draft()

### Community 81 - "4. 設計提案"
Cohesion: 0.12
Nodes (18): 0. 一句話結論, 2. 現成編輯器評估（不使用 bundler、從 CDN 載入）, 3. 別人怎麼做論文筆記（取重點）, 4.10 測試與驗收重點, 4.1 範圍, 4.3 引用語法（沿用 Wiki）, 4.4 API, 4.5 介面位置 (+10 more)

### Community 82 - "pymupdf"
Cohesion: 0.44
Nodes (5): authoryear(), make_all(), numeric(), scanned(), _text()

### Community 83 - "Service bge-m3"
Cohesion: 0.22
Nodes (8): Service bge-m3, app, app, matchLabels, apiVersion, kind, spec, selector

### Community 84 - "Service bge-reranker"
Cohesion: 0.22
Nodes (8): Service bge-reranker, app, app, matchLabels, apiVersion, kind, spec, selector

### Community 85 - "paintWsCards"
Cohesion: 0.33
Nodes (7): cardPaper(), fmtDate(), openNote(), paintWsCards(), patchCards(), patchPaper(), trRing()

### Community 86 - "_stream"
Cohesion: 0.40
Nodes (5): _build(), _create(), _stream(), test_build_adjustments(), test_build_default_sends_vllm_params()

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
Cohesion: 0.33
Nodes (3): paper_thumb(), region_png(), render_page_png()

### Community 92 - "s2_get"
Cohesion: 0.17
Nodes (9): _guess_ref_title(), lookup_reference(), s2_get(), API, 前端（論文卡）, 決定, 論文卡：備註、星號、排序、複製引用, 資料表（`backend/db.py`） (+1 more)

### Community 93 - "_to_claude"
Cohesion: 0.40
Nodes (4): _claude_block(), _to_claude(), test_cache_breakpoint_only_for_multi_turn(), test_to_claude_conversion()

### Community 95 - "k8s-retrieval/kustomization.yaml"
Cohesion: 0.40
Nodes (4): apiVersion, kind, namespace, resources

### Community 96 - "ports"
Cohesion: 0.50
Nodes (4): name, port, targetPort, ports

### Community 97 - "ports"
Cohesion: 0.50
Nodes (4): name, port, targetPort, ports

### Community 98 - "聊天：段落累積式 RAG"
Cohesion: 0.50
Nodes (3): 為什麼要這樣設計, 聊天：段落累積式 RAG, 評估（`uv run python -m eval.chat_eval`）

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `vLLM (Qwen3.5-9B)`, `/api/health endpoint` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 618 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `app.js`, `db.py`, `re`, `features.py`, `llm.py`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.035959809624537285 - nodes in this community are weakly interconnected._
- **Why does `1. Lantern 現在已經有什麼` connect `drawHighlights` to `4. 設計提案`, `Uid`, `annotations`, `db.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `Uid` be split into smaller, more focused modules?**
  _Cohesion score 0.08658536585365853 - nodes in this community are weakly interconnected._
- **Why does `complete_json()` connect `chat_eval.py` to `db.py`, `retrieval.py`, `features.py`, `llm.py`, `Workspace LLM Wiki（MVP）`, `s2_get`, `auto_highlight`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Should `test_api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09309309309309309 - nodes in this community are weakly interconnected._