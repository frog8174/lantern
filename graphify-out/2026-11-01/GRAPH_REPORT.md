# Graph Report - paper-reader  (2026-11-01)

## Corpus Check
- 55 files · ~47,692 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .example 1, .css 1)

## Summary
- 1214 nodes · 2605 edges · 69 communities (63 shown, 6 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 97 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `12e3083f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- 閱讀器：選取、螢光筆與中英對照
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
- sentalign.py
- Workspace LLM Wiki（MVP）
- escapeHTML
- drawHighlights
- cite.py
- aiCard
- retrieval.py
- pumpTranslation
- data
- k8s-labse/ingress.yaml
- test_anthropic.py
- update_wiki
- _paper_or_404
- conftest.py
- features.py
- 4. 設計提案
- loadNote
- llm.py
- cache_get
- pymupdf
- get
- UX 第一輪（已定案）
- k8s-labse/service.yaml
- s2_get
- ingress.yaml
- containers
- service.yaml
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
- drawOutline
- backend/__init__.py
- _sim_from
- _ingest
- k8s-labse/kustomization.yaml
- k8s-labse/namespace.yaml
- LaBSE 句向量服務（中英逐句對齊）
- test_workspaces.py
- backend/__init__.py
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

## Communities (69 total, 6 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.04
Nodes (51): AUTO, calmMotion, card, cardHTML, cardPaper(), caretAt(), CITE_STYLES, citeStyles (+43 more)

### Community 1 - "閱讀器：選取、螢光筆與中英對照"
Cohesion: 0.29
Nodes (7): 並排模式：對應的段落亮起來, 螢光筆同步到譯文, 連續的選取與螢光筆, 閱讀器：選取、螢光筆與中英對照, mergeRects(), readSelection(), selRects()

### Community 2 - "test_api.py"
Cohesion: 0.10
Nodes (29): sse(), test_bilingual_blocks(), _id(), test_ai_outline(), test_annotation_kinds(), test_annotations_crud(), test_ask_ai_on_selection(), test_author_year_reference() (+21 more)

### Community 3 - "db.py"
Cohesion: 0.08
Nodes (38): add_annotation(), add_message(), add_paper(), add_wiki_message(), add_workspace(), annotation_paper(), clear_messages(), clear_wiki_messages() (+30 more)

### Community 4 - "re"
Cohesion: 0.15
Nodes (19): _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), find_texts_rects(), _guess_title(), _is_ref_head() (+11 more)

### Community 5 - "test_units.py"
Cohesion: 0.10
Nodes (15): cite_reason_messages(), citing_contexts(), stream_block_translation(), run(), _translatable(), find_figures(), match_author_year(), llm._ThinkStripper (+7 more)

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
Cohesion: 0.08
Nodes (34): AlignMark, AnnotIn, ArxivIn, ChatIn, CommentIn, create_workspace(), delete(), delete_workspace() (+26 more)

### Community 15 - "sentalign.py"
Cohesion: 0.24
Nodes (7): align_dp(), _embed(), page_map(), sim(), _spans(), split_en(), split_zh()

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.10
Nodes (46): 薛西弗斯（等待、完成、空狀態）, addAsk(), addSave(), api(), bibtex(), cardsBusy(), citeChip(), enter() (+38 more)

### Community 19 - "drawHighlights"
Cohesion: 0.22
Nodes (19): 1. Lantern 現在已經有什麼, clearLitAlign(), colorKey(), deleteAnnotation(), drawHighlights(), drawLabels(), flashItem(), isHex() (+11 more)

### Community 20 - "cite.py"
Cohesion: 0.19
Nodes (18): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+10 more)

### Community 21 - "aiCard"
Cohesion: 0.18
Nodes (19): 逐句對應（並排模式）, addAnnotation(), aiCard(), alignHighlight(), closeAiCard(), commentEditor(), correspond(), explainCrop() (+11 more)

### Community 22 - "retrieval.py"
Cohesion: 0.16
Nodes (8): _bm25(), make_chunks(), _tokens(), /api/health endpoint, backend/main.py (FastAPI app), BM25 retrieval, Lantern AI Paper Reader, RAG for long papers

### Community 23 - "pumpTranslation"
Cohesion: 0.29
Nodes (11): buildPages(), drawTranslation(), fitText(), loadAlignMap(), pumpTranslation(), queueTranslation(), refreshCanvas(), renderPage() (+3 more)

### Community 24 - "data"
Cohesion: 0.07
Nodes (29): apiVersion, data, ALIGN_EMBED_MODEL, ALIGN_EMBED_URL, AUTH_MODE, DISABLE_THINKING, LLM_CONCURRENCY, LLM_CONTEXT_TOKENS (+21 more)

### Community 26 - "k8s-labse/ingress.yaml"
Cohesion: 0.10
Nodes (20): cert-manager.io/cluster-issuer, traefik.ingress.kubernetes.io/router.entrypoints, traefik.ingress.kubernetes.io/router.tls, apiVersion, paths, kind, metadata, annotations (+12 more)

### Community 28 - "test_anthropic.py"
Cohesion: 0.16
Nodes (11): claude(), _pid(), test_auto_highlight_json(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape(), test_mixed_providers(), test_no_fallback_for_haiku() (+3 more)

### Community 29 - "update_wiki"
Cohesion: 0.16
Nodes (11): list_wiki_messages(), wiki_pages(), wiki_pending(), wiki_ask_messages(), AskIn, wiki(), wiki_ask(), wiki_ask_history() (+3 more)

### Community 30 - "_paper_or_404"
Cohesion: 0.12
Nodes (29): list_annotations(), list_messages(), stream_chat(), add_annotation(), annotations(), auto_highlight(), _cached_text(), chat() (+21 more)

### Community 31 - "conftest.py"
Cohesion: 0.14
Nodes (6): allow_duplicates(), bob(), client(), fake_server(), papers(), pdfs()

### Community 32 - "features.py"
Cohesion: 0.10
Nodes (26): _bib_arxiv(), _bib_llm(), _bib_s2(), chat_messages(), _est_tokens(), explain_messages(), fetch_bib(), full_text_fits() (+18 more)

### Community 34 - "4. 設計提案"
Cohesion: 0.06
Nodes (36): delete_paper(), current_user(), k8s 部署要一起處理的事（不處理會壞）, Keycloak 端要建的 client, 建議架構：後端當 OIDC client（Authorization Code + PKCE）, 待確認, 既有資料, 登入系統：Keycloak（OIDC） (+28 more)

### Community 35 - "loadNote"
Cohesion: 0.14
Nodes (29): 實作狀態（2026-11）, fmtDate(), insertIntoNote(), loadNote(), nbGet(), nbHead(), nbHeadings(), nbKey() (+21 more)

### Community 37 - "llm.py"
Cohesion: 0.05
Nodes (31): _build(), check(), _claude(), _claude_block(), _claude_stream(), _create(), _mock_answer(), ocr_image() (+23 more)

### Community 38 - "cache_get"
Cohesion: 0.11
Nodes (23): cache_get(), cache_set(), _wiki_source(), embed(), align(), align_map(), _align_map(), AlignIn (+15 more)

### Community 39 - "pymupdf"
Cohesion: 0.44
Nodes (5): authoryear(), make_all(), numeric(), scanned(), _text()

### Community 41 - "get"
Cohesion: 0.07
Nodes (17): list_papers(), auth_config(), auth_users(), cite_paper(), figures(), health(), livez(), logout() (+9 more)

### Community 42 - "UX 第一輪（已定案）"
Cohesion: 0.33
Nodes (5): A. 閱讀頁重新排版, B. 研究主題頁與流程, C. 全站主題切換, UX 第一輪（已定案）, 不做

### Community 43 - "k8s-labse/service.yaml"
Cohesion: 0.17
Nodes (11): apiVersion, kind, metadata, name, name, port, targetPort, app (+3 more)

### Community 46 - "s2_get"
Cohesion: 0.14
Nodes (10): _check(), s2_get(), s2_paper_id(), S2Error, API, 前端（論文卡）, 決定, 論文卡：備註、星號、排序、複製引用 (+2 more)

### Community 47 - "ingress.yaml"
Cohesion: 0.10
Nodes (20): cert-manager.io/cluster-issuer, traefik.ingress.kubernetes.io/router.entrypoints, traefik.ingress.kubernetes.io/router.tls, apiVersion, paths, kind, metadata, annotations (+12 more)

### Community 48 - "containers"
Cohesion: 0.17
Nodes (12): envFrom, image, name, ports, readinessProbe, resources, volumeMounts, httpGet (+4 more)

### Community 49 - "service.yaml"
Cohesion: 0.17
Nodes (11): apiVersion, kind, metadata, name, name, port, targetPort, app (+3 more)

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

### Community 69 - "drawOutline"
Cohesion: 0.18
Nodes (13): addCopy(), addMsg(), drawOutline(), goToPage(), hideFigure(), icon(), loadChat(), markOutline() (+5 more)

### Community 70 - "backend/__init__.py"
Cohesion: 0.25
Nodes (4): FakeKC, _oidc(), test_oidc_login_creates_user_and_session(), test_oidc_login_failure_redirects()

### Community 71 - "_sim_from"
Cohesion: 0.50
Nodes (3): _sim_from(), test_dp_merge_and_skip(), test_dp_one_to_one()

### Community 73 - "_ingest"
Cohesion: 0.13
Nodes (13): add_to_workspace(), get_settings(), add_to_workspace(), _auto_wiki(), _duplicate(), _first_doi(), _ingest(), _ocr_pages() (+5 more)

### Community 74 - "k8s-labse/kustomization.yaml"
Cohesion: 0.40
Nodes (4): apiVersion, kind, namespace, resources

### Community 75 - "k8s-labse/namespace.yaml"
Cohesion: 0.40
Nodes (4): apiVersion, kind, metadata, name

### Community 76 - "LaBSE 句向量服務（中英逐句對齊）"
Cohesion: 0.40
Nodes (4): LaBSE 句向量服務（中英逐句對齊）, Lantern 端設定, 要注意, 部署（`deploy/k8s-labse/`）

### Community 78 - "backend/__init__.py"
Cohesion: 0.18
Nodes (10): _fake(), test_align_invalid_falls_back(), test_align_scoped_to_owner(), test_align_valid_substring(), _translated_block(), _cut(), _fake_embed(), test_align_map_endpoint() (+2 more)

### Community 79 - "test_notes.py"
Cohesion: 0.29
Nodes (3): test_delete_paper_deletes_note(), test_note_crud_and_conflict(), test_note_draft()

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules`, `/api/health endpoint`, `BM25 retrieval` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 484 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `retrieval.py` to `features.py`, `app.js`, `db.py`, `re`, `llm.py`?**
  _High betweenness centrality (0.193) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `graphify-out/graph.json`, `graphify usage rules` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.035278154681139755 - nodes in this community are weakly interconnected._
- **Why does `_ThinkStripper` connect `llm.py` to `test_units.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `test_api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0975609756097561 - nodes in this community are weakly interconnected._
- **Why does `current_user()` connect `4. 設計提案` to `get`, `db.py`, `main.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08345428156748912 - nodes in this community are weakly interconnected._