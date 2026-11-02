# Graph Report - paper-reader  (2026-11-01)

## Corpus Check
- 55 files · ~47,983 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .example 1, .css 1)

## Summary
- 1218 nodes · 2614 edges · 72 communities (66 shown, 6 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 97 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c7cd3b03`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- 閱讀器：選取、螢光筆與中英對照
- test_api.py
- db.py
- pdf_parse.py
- features.py
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
- check
- drawHighlights
- backend/__init__.py
- aiCard
- 功能對照
- pumpTranslation
- data
- _to_claude
- k8s-labse/ingress.yaml
- test_units.py
- test_anthropic.py
- Uid
- _paper_or_404
- conftest.py
- _header
- fetch_bib
- 4. 設計提案
- loadNote
- _ThinkStripper
- Lantern — 個人用 AI 論文閱讀器
- cache_get
- wiki_ask_messages
- recommendations
- logout
- UX 第一輪（已定案）
- k8s-labse/service.yaml
- addMsg
- s2_get
- ingress.yaml
- containers
- service.yaml
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
- drawOutline
- _ingest
- k8s-labse/kustomization.yaml
- k8s-labse/namespace.yaml
- LaBSE 句向量服務（中英逐句對齊）
- test_sentalign.py
- test_notes.py

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
10. `drawHighlights()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `資料表（`backend/db.py`）` --references--> `list_papers()`  [INFERRED]
  docs/paper-cards.md → backend/db.py
- `API` --references--> `_ws_or_404()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `Lantern 端設定` --references--> `_align_map()`  [INFERRED]
  docs/labse.md → backend/main.py
- `螢光筆同步到譯文` --references--> `align()`  [INFERRED]
  docs/reader.md → backend/main.py
- `範圍限制` --references--> `_mark_in_library()`  [INFERRED]
  docs/workspaces.md → backend/main.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (72 total, 6 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.03
Nodes (52): AUTO, calmMotion, card, cardHTML, cardPaper(), caretAt(), CITE_STYLES, citeStyles (+44 more)

### Community 1 - "閱讀器：選取、螢光筆與中英對照"
Cohesion: 0.50
Nodes (3): 並排模式：對應的段落亮起來, 螢光筆同步到譯文, 閱讀器：選取、螢光筆與中英對照

### Community 2 - "test_api.py"
Cohesion: 0.09
Nodes (27): _id(), test_ai_outline(), test_annotation_kinds(), test_annotations_crud(), test_ask_ai_on_selection(), test_author_year_reference(), test_auto_highlight_finds_sentence(), test_bilingual_blocks() (+19 more)

### Community 3 - "db.py"
Cohesion: 0.07
Nodes (46): add_annotation(), add_message(), add_paper(), add_wiki_message(), add_workspace(), annotation_paper(), clear_messages(), clear_wiki_messages() (+38 more)

### Community 4 - "pdf_parse.py"
Cohesion: 0.06
Nodes (38): _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), find_figures(), find_texts_rects(), _guess_title() (+30 more)

### Community 5 - "features.py"
Cohesion: 0.17
Nodes (13): cite_reason_messages(), citing_contexts(), _guess_ref_title(), lookup_reference(), page_translate_messages(), _reference_start_page(), stream_block_translation(), run() (+5 more)

### Community 6 - "containers"
Cohesion: 0.04
Nodes (47): apiVersion, args, command, env, image, livenessProbe, name, ports (+39 more)

### Community 7 - "Lantern 視覺系統（燈下的那一頁）"
Cohesion: 0.18
Nodes (10): Lantern 視覺系統（燈下的那一頁）, 原則, 字體分工, 捲軸, 用語, 登入頁與標誌, 自動畫重點標籤（無印風）, 自動畫重點的頁邊標籤 (+2 more)

### Community 8 - "fake_api.py"
Cohesion: 0.12
Nodes (11): _answer(), chat(), claude_messages(), gen(), embeddings(), _err(), files(), _sse() (+3 more)

### Community 9 - "Frontend UI Layout"
Cohesion: 0.32
Nodes (8): Lantern index.html, Floating AI card (aiCard), Chat window (chatWin), Crop toolbar (cropBar), Activity panel, PDF.js 3.11.174, Selection toolbar (selBar), style.css

### Community 13 - "main.py"
Cohesion: 0.07
Nodes (30): add_annotation(), AlignMark, AnnotIn, ArxivIn, AskIn, auth_config(), auth_users(), ChatIn (+22 more)

### Community 15 - "llm.py"
Cohesion: 0.18
Nodes (4): _mock_answer(), ocr_image(), one(), vLLM (Qwen3.5-9B)

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.10
Nodes (46): 薛西弗斯（等待、完成、空狀態）, addAsk(), addSave(), ago(), allTile(), api(), bibtex(), cardsBusy() (+38 more)

### Community 18 - "check"
Cohesion: 0.24
Nodes (6): check(), _create(), route(), _stream(), _test_image(), test_route_prefixes()

### Community 19 - "drawHighlights"
Cohesion: 0.17
Nodes (23): 1. Lantern 現在已經有什麼, 連續的選取與螢光筆, clearLitAlign(), colorKey(), deleteAnnotation(), drawHighlights(), drawLabels(), flashItem() (+15 more)

### Community 20 - "backend/__init__.py"
Cohesion: 0.06
Nodes (29): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+21 more)

### Community 21 - "aiCard"
Cohesion: 0.18
Nodes (19): 逐句對應（並排模式）, addAnnotation(), aiCard(), alignHighlight(), commentEditor(), correspond(), explainCrop(), explainImage() (+11 more)

### Community 22 - "功能對照"
Cohesion: 0.24
Nodes (7): search_chunks(), ai_outline(), explain_messages(), _history_block(), image_messages(), local_context(), 功能對照

### Community 23 - "pumpTranslation"
Cohesion: 0.29
Nodes (11): buildPages(), drawTranslation(), fitText(), loadAlignMap(), pumpTranslation(), queueTranslation(), refreshCanvas(), renderPage() (+3 more)

### Community 24 - "data"
Cohesion: 0.07
Nodes (29): apiVersion, data, ALIGN_EMBED_MODEL, ALIGN_EMBED_URL, AUTH_MODE, DISABLE_THINKING, LLM_CONCURRENCY, LLM_CONTEXT_TOKENS (+21 more)

### Community 25 - "_to_claude"
Cohesion: 0.22
Nodes (6): _claude(), _claude_block(), _claude_stream(), _to_claude(), test_cache_breakpoint_only_for_multi_turn(), test_to_claude_conversion()

### Community 26 - "k8s-labse/ingress.yaml"
Cohesion: 0.10
Nodes (20): cert-manager.io/cluster-issuer, traefik.ingress.kubernetes.io/router.entrypoints, traefik.ingress.kubernetes.io/router.tls, apiVersion, paths, kind, metadata, annotations (+12 more)

### Community 27 - "test_units.py"
Cohesion: 0.28
Nodes (6): _build(), llm._ThinkStripper, test_build_adjustments(), test_build_default_sends_vllm_params(), test_think_stripper(), test_translatable()

### Community 28 - "test_anthropic.py"
Cohesion: 0.18
Nodes (12): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+4 more)

### Community 29 - "Uid"
Cohesion: 0.18
Nodes (16): chat_clear(), delete(), delete_workspace(), papers(), remove_annotation(), remove_from_workspace(), rename_workspace(), search() (+8 more)

### Community 30 - "_paper_or_404"
Cohesion: 0.17
Nodes (15): stream_chat(), _cached_text(), chat(), explain(), explain_image(), note_draft(), PageIn, reference_why() (+7 more)

### Community 31 - "conftest.py"
Cohesion: 0.14
Nodes (6): allow_duplicates(), bob(), client(), fake_server(), papers(), pdfs()

### Community 32 - "_header"
Cohesion: 0.19
Nodes (10): chat_messages(), _est_tokens(), full_text_fits(), _header(), note_draft_messages(), _pages_text(), _paper_body(), suggested_questions() (+2 more)

### Community 33 - "fetch_bib"
Cohesion: 0.29
Nodes (5): _bib_arxiv(), _bib_llm(), _bib_s2(), fetch_bib(), _name()

### Community 34 - "4. 設計提案"
Cohesion: 0.06
Nodes (36): delete_paper(), current_user(), k8s 部署要一起處理的事（不處理會壞）, Keycloak 端要建的 client, 建議架構：後端當 OIDC client（Authorization Code + PKCE）, 待確認, 既有資料, 登入系統：Keycloak（OIDC） (+28 more)

### Community 35 - "loadNote"
Cohesion: 0.13
Nodes (30): 實作狀態（2026-11）, fmtDate(), insertIntoNote(), loadNote(), nbGet(), nbHead(), nbHeadings(), nbKey() (+22 more)

### Community 37 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

### Community 38 - "cache_get"
Cohesion: 0.09
Nodes (33): cache_get(), cache_set(), align(), align_map(), _align_map(), AlignIn, annotations(), _block_translation() (+25 more)

### Community 39 - "wiki_ask_messages"
Cohesion: 0.33
Nodes (4): wiki_ask_messages(), embed(), build_index(), search()

### Community 41 - "logout"
Cohesion: 0.25
Nodes (3): logout(), oidc_callback(), oidc_login()

### Community 42 - "UX 第一輪（已定案）"
Cohesion: 0.33
Nodes (5): A. 閱讀頁重新排版, B. 研究主題頁與流程, C. 全站主題切換, UX 第一輪（已定案）, 不做

### Community 43 - "k8s-labse/service.yaml"
Cohesion: 0.17
Nodes (11): apiVersion, kind, metadata, name, name, port, targetPort, app (+3 more)

### Community 44 - "addMsg"
Cohesion: 0.83
Nodes (4): addCopy(), addMsg(), loadChat(), sendChat()

### Community 46 - "s2_get"
Cohesion: 0.13
Nodes (11): _check(), recommend(), s2_get(), s2_paper_id(), S2Error, API, 前端（論文卡）, 決定 (+3 more)

### Community 47 - "ingress.yaml"
Cohesion: 0.10
Nodes (20): cert-manager.io/cluster-issuer, traefik.ingress.kubernetes.io/router.entrypoints, traefik.ingress.kubernetes.io/router.tls, apiVersion, paths, kind, metadata, annotations (+12 more)

### Community 48 - "containers"
Cohesion: 0.17
Nodes (12): envFrom, image, name, ports, readinessProbe, resources, volumeMounts, httpGet (+4 more)

### Community 49 - "service.yaml"
Cohesion: 0.17
Nodes (11): apiVersion, kind, metadata, name, name, port, targetPort, app (+3 more)

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
Cohesion: 0.20
Nodes (9): align_span(), _strip_fence(), _wiki_concept(), _wiki_index(), _wiki_plan(), wiki_qa_page(), complete(), complete_json() (+1 more)

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
Cohesion: 0.38
Nodes (5): auto_highlight(), guarded(), one(), find_text_rects(), test_find_text_rects()

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
Cohesion: 0.12
Nodes (3): _load_dotenv(), test_wiki_ask_and_backlinks(), test_wiki_update()

### Community 69 - "drawOutline"
Cohesion: 0.20
Nodes (10): drawOutline(), enter(), goToPage(), hideFigure(), markOutline(), openAt(), openCite(), renderOutline() (+2 more)

### Community 73 - "_ingest"
Cohesion: 0.14
Nodes (12): add_to_workspace(), get_settings(), add_to_workspace(), _auto_wiki(), _duplicate(), _first_doi(), _ingest(), _ocr_pages() (+4 more)

### Community 74 - "k8s-labse/kustomization.yaml"
Cohesion: 0.40
Nodes (4): apiVersion, kind, namespace, resources

### Community 75 - "k8s-labse/namespace.yaml"
Cohesion: 0.40
Nodes (4): apiVersion, kind, metadata, name

### Community 76 - "LaBSE 句向量服務（中英逐句對齊）"
Cohesion: 0.40
Nodes (4): LaBSE 句向量服務（中英逐句對齊）, Lantern 端設定, 要注意, 部署（`deploy/k8s-labse/`）

### Community 78 - "test_sentalign.py"
Cohesion: 0.10
Nodes (20): align_dp(), _embed(), page_map(), sim(), _spans(), split_en(), split_zh(), _fake() (+12 more)

### Community 79 - "test_notes.py"
Cohesion: 0.29
Nodes (3): test_delete_paper_deletes_note(), test_note_crud_and_conflict(), test_note_draft()

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `/api/health endpoint`, `BM25 retrieval` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 485 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `pdf_parse.py` to `app.js`, `db.py`, `features.py`, `llm.py`?**
  _High betweenness centrality (0.192) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.03467954345917471 - nodes in this community are weakly interconnected._
- **Why does `1. Lantern 現在已經有什麼` connect `drawHighlights` to `4. 設計提案`, `db.py`, `cache_get`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `test_api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09309309309309309 - nodes in this community are weakly interconnected._
- **Why does `current_user()` connect `4. 設計提案` to `logout`, `db.py`, `main.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07244843997884717 - nodes in this community are weakly interconnected._