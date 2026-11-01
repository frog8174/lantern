# Graph Report - paper-reader  (2026-11-01)

## Corpus Check
- 44 files · ~39,180 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .example 1, .css 1)

## Summary
- 996 nodes · 2189 edges · 63 communities (59 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 71 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2f2dda05`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- features.py
- Anthropic Provider Tests
- db.py
- re
- test_paper_cards.py
- conftest.py
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
- sendAsk
- pumpTranslation
- data
- Uid
- escapeHTML
- 登入系統：Keycloak（OIDC）
- auto_highlight
- post
- _paper_or_404
- chat_messages
- local_context
- llm.py
- complete_json
- paintWsCards
- Lantern — 個人用 AI 論文閱讀器
- 論文卡：備註、星號、排序、複製引用
- 閱讀器：選取、螢光筆與中英對照
- addMsg
- _ingest
- import_url
- UX 第一輪（已定案）
- update_wiki
- get
- s2_get
- ingress.yaml
- containers
- service.yaml
- json
- pvc.yaml
- 部署到 k8s
- kustomization.yaml
- config.py
- deployment.yaml
- spec
- securityContext
- volumes
- namespace.yaml
- livenessProbe
- securityContext
- startupProbe
- spec

## God Nodes (most connected - your core abstractions)
1. `conn()` - 46 edges
2. `_paper_or_404()` - 34 edges
3. `escapeHTML()` - 34 edges
4. `sse()` - 31 edges
5. `api()` - 30 edges
6. `_id()` - 27 edges
7. `data` - 22 edges
8. `cache_get()` - 19 edges
9. `drawHighlights()` - 19 edges
10. `_ws_or_404()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `資料表（`backend/db.py`）` --references--> `list_papers()`  [INFERRED]
  docs/paper-cards.md → backend/db.py
- `API` --references--> `_ws_or_404()`  [INFERRED]
  docs/wiki.md → backend/main.py
- `螢光筆同步到譯文` --references--> `align()`  [INFERRED]
  docs/reader.md → backend/main.py
- `範圍限制` --references--> `_mark_in_library()`  [INFERRED]
  docs/workspaces.md → backend/main.py
- `更新流程（後端，`features.py` 放 prompt）` --references--> `wiki()`  [INFERRED]
  docs/wiki.md → backend/main.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI backend modules pipeline** — readme_backend_main, backend_pdf_parse, backend_retrieval, backend_features, backend_llm, backend_db [EXTRACTED 0.85]
- **Automated test suite** — tests_fake_api, tests_sample_pdfs, tests_test_units, tests_test_api [EXTRACTED 0.90]
- **Floating AI interaction widgets** — frontend_index_selbar, frontend_index_cropbar, frontend_index_aicard, frontend_index_chatwin [INFERRED 0.75]

## Communities (63 total, 4 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.05
Nodes (35): AUTO, calmMotion, card, caretAt(), CITE_STYLES, citeStyles, COLORS, customColor (+27 more)

### Community 1 - "features.py"
Cohesion: 0.21
Nodes (9): _bib_arxiv(), _bib_llm(), _bib_s2(), fetch_bib(), _name(), page_translate_messages(), translate_messages(), _wiki_slug() (+1 more)

### Community 2 - "Anthropic Provider Tests"
Cohesion: 0.05
Nodes (48): _claude_block(), _to_claude(), sse(), _fake(), test_align_invalid_falls_back(), test_align_scoped_to_owner(), test_align_valid_substring(), _translated_block() (+40 more)

### Community 3 - "db.py"
Cohesion: 0.11
Nodes (25): add_annotation(), add_message(), add_wiki_message(), add_workspace(), annotation_paper(), clear_messages(), clear_wiki_messages(), conn() (+17 more)

### Community 4 - "re"
Cohesion: 0.07
Nodes (42): citing_contexts(), stream_block_translation(), run(), _translatable(), _build(), _abstract(), apply_ocr(), _author_year_refs() (+34 more)

### Community 5 - "test_paper_cards.py"
Cohesion: 0.25
Nodes (6): byline(), _row(), test_byline(), test_cards_scoped_to_owner(), test_cite_cached_and_year(), test_patch_fields_independently()

### Community 6 - "conftest.py"
Cohesion: 0.14
Nodes (6): allow_duplicates(), bob(), client(), fake_server(), papers(), pdfs()

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
Nodes (23): add_annotation(), AlignIn, AlignMark, AnnotIn, ArxivIn, AskIn, ChatIn, CommentIn (+15 more)

### Community 15 - "config.py"
Cohesion: 0.12
Nodes (5): FakeKC, _oidc(), test_oidc_login_creates_user_and_session(), test_oidc_login_failure_redirects(), test_auto_translate_setting()

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.17
Nodes (23): api(), cardsBusy(), closeAiCard(), enter(), importArxiv(), ingest(), loadLibrary(), loadPaperWiki() (+15 more)

### Community 18 - "retrieval.py"
Cohesion: 0.16
Nodes (10): load_chunks(), save_chunks(), embed(), _bm25(), build_index(), make_chunks(), search(), _tokens() (+2 more)

### Community 19 - "drawHighlights"
Cohesion: 0.26
Nodes (17): 1. Lantern 現在已經有什麼, colorKey(), deleteAnnotation(), drawHighlights(), drawLabels(), flashItem(), isHex(), markTranslation() (+9 more)

### Community 20 - "cite.py"
Cohesion: 0.19
Nodes (18): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+10 more)

### Community 21 - "aiCard"
Cohesion: 0.26
Nodes (12): addAnnotation(), aiCard(), commentEditor(), explainCrop(), explainImage(), highlightTranslation(), imageFollowup(), placeFloating() (+4 more)

### Community 22 - "sendAsk"
Cohesion: 0.22
Nodes (11): addAsk(), addSave(), focusWikiTitle(), loadAsk(), openWikiPage(), reach(), renderWiki(), sendAsk() (+3 more)

### Community 23 - "pumpTranslation"
Cohesion: 0.20
Nodes (14): alignHighlight(), buildPages(), drawRail(), drawTranslation(), fitText(), overlap(), pumpTranslation(), queueTranslation() (+6 more)

### Community 24 - "data"
Cohesion: 0.07
Nodes (26): apiVersion, data, AUTH_MODE, DISABLE_THINKING, LLM_CONCURRENCY, LLM_CONTEXT_TOKENS, LLM_EFFORT, LLM_MODEL (+18 more)

### Community 25 - "Uid"
Cohesion: 0.16
Nodes (19): list_papers(), add_to_workspace(), chat_clear(), delete(), delete_workspace(), _mark_in_library(), papers(), recommendations() (+11 more)

### Community 26 - "escapeHTML"
Cohesion: 0.18
Nodes (17): 薛西弗斯（等待、完成、空狀態）, bibtex(), escapeHTML(), goToPage(), hideFigure(), icon(), loadRelated(), openCite() (+9 more)

### Community 27 - "登入系統：Keycloak（OIDC）"
Cohesion: 0.06
Nodes (36): delete_paper(), current_user(), k8s 部署要一起處理的事（不處理會壞）, Keycloak 端要建的 client, 建議架構：後端當 OIDC client（Authorization Code + PKCE）, 待確認, 既有資料, 登入系統：Keycloak（OIDC） (+28 more)

### Community 28 - "auto_highlight"
Cohesion: 0.50
Nodes (4): auto_highlight(), guarded(), one(), _reference_start_page()

### Community 29 - "post"
Cohesion: 0.20
Nodes (11): stream_chat(), chat(), explain(), explain_image(), PageIn, SelectionIn, sse(), translate() (+3 more)

### Community 30 - "_paper_or_404"
Cohesion: 0.17
Nodes (19): cache_get(), cache_set(), s2_paper_id(), align(), annotations(), _block_translation(), _cached_text(), cite_paper() (+11 more)

### Community 31 - "chat_messages"
Cohesion: 0.19
Nodes (10): chat_messages(), cite_reason_messages(), _est_tokens(), full_text_fits(), _header(), _pages_text(), _paper_body(), suggested_questions() (+2 more)

### Community 32 - "local_context"
Cohesion: 0.40
Nodes (4): explain_messages(), _history_block(), image_messages(), local_context()

### Community 33 - "llm.py"
Cohesion: 0.17
Nodes (7): _mock_answer(), ocr_image(), one(), /api/health endpoint, backend/main.py (FastAPI app), Lantern AI Paper Reader, vLLM (Qwen3.5-9B)

### Community 34 - "complete_json"
Cohesion: 0.18
Nodes (10): ai_outline(), align_span(), _strip_fence(), _wiki_concept(), _wiki_index(), _wiki_plan(), wiki_qa_page(), complete() (+2 more)

### Community 35 - "paintWsCards"
Cohesion: 0.33
Nodes (7): cardPaper(), fmtDate(), openNote(), paintWsCards(), patchPaper(), showWikiPage(), trRing()

### Community 36 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.07
Nodes (22): check(), _claude(), _claude_stream(), _create(), route(), _stream(), _test_image(), _ThinkStripper (+14 more)

### Community 37 - "論文卡：備註、星號、排序、複製引用"
Cohesion: 0.33
Nodes (5): 前端（論文卡）, 決定, 論文卡：備註、星號、排序、複製引用, 資料表（`backend/db.py`）, 這次不做

### Community 38 - "閱讀器：選取、螢光筆與中英對照"
Cohesion: 0.29
Nodes (7): 並排模式：對應的段落亮起來, 螢光筆同步到譯文, 連續的選取與螢光筆, 閱讀器：選取、螢光筆與中英對照, mergeRects(), readSelection(), selRects()

### Community 39 - "addMsg"
Cohesion: 0.83
Nodes (4): addCopy(), addMsg(), loadChat(), sendChat()

### Community 40 - "_ingest"
Cohesion: 0.13
Nodes (13): add_paper(), add_to_workspace(), get_paper(), get_settings(), _auto_wiki(), _duplicate(), _first_doi(), _ingest() (+5 more)

### Community 41 - "import_url"
Cohesion: 0.19
Nodes (9): auto_highlight(), figure_png(), figures(), _figures(), paper_pdf(), paper_thumb(), _pdf_path(), region_png() (+1 more)

### Community 42 - "UX 第一輪（已定案）"
Cohesion: 0.33
Nodes (5): A. 閱讀頁重新排版, B. 研究主題頁與流程, C. 全站主題切換, UX 第一輪（已定案）, 不做

### Community 43 - "update_wiki"
Cohesion: 0.22
Nodes (7): wiki_mark_ingested(), wiki_page(), wiki_pending(), wiki_save(), update_wiki(), wiki_ask_messages(), test_auto_wiki()

### Community 44 - "get"
Cohesion: 0.09
Nodes (14): auth_config(), auth_users(), chat_history(), livez(), logout(), me(), oidc_callback(), oidc_login() (+6 more)

### Community 46 - "s2_get"
Cohesion: 0.20
Nodes (7): _check(), _guess_ref_title(), lookup_reference(), recommend(), s2_get(), S2Error, API

### Community 47 - "ingress.yaml"
Cohesion: 0.10
Nodes (20): cert-manager.io/cluster-issuer, traefik.ingress.kubernetes.io/router.entrypoints, traefik.ingress.kubernetes.io/router.tls, apiVersion, paths, kind, metadata, annotations (+12 more)

### Community 48 - "containers"
Cohesion: 0.17
Nodes (12): envFrom, image, name, ports, readinessProbe, resources, volumeMounts, httpGet (+4 more)

### Community 49 - "service.yaml"
Cohesion: 0.17
Nodes (11): apiVersion, kind, metadata, name, name, port, targetPort, app (+3 more)

### Community 51 - "json"
Cohesion: 0.22
Nodes (6): find_duplicate(), list_annotations(), norm_title(), set_settings(), update_annotation(), update_paper()

### Community 52 - "pvc.yaml"
Cohesion: 0.18
Nodes (10): apiVersion, kind, metadata, name, storage, requests, spec, accessModes (+2 more)

### Community 53 - "部署到 k8s"
Cohesion: 0.18
Nodes (10): 1. 建映像, 2. Keycloak client（沿用 `lantern-local`）, 3. Secret（不要 commit）, 4. 設定與套用, Traefik, 常見問題, 待填, 本機驗證（2026-11-01） (+2 more)

### Community 54 - "kustomization.yaml"
Cohesion: 0.22
Nodes (8): apiVersion, images, name, newName, newTag, kind, namespace, resources

### Community 56 - "config.py"
Cohesion: 0.17
Nodes (3): _load_dotenv(), list_wiki_messages(), test_wiki_ask_and_backlinks()

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

## Knowledge Gaps
- **13 isolated node(s):** `lantern-paper-reader`, `Semantic Scholar API`, `graphify-out/graph.json`, `graphify usage rules`, `/api/health endpoint` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 385 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `llm.py` to `app.js`, `features.py`, `db.py`, `re`, `retrieval.py`?**
  _High betweenness centrality (0.216) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `Semantic Scholar API`, `graphify-out/graph.json` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.04625346901017576 - nodes in this community are weakly interconnected._
- **Why does `1. Lantern 現在已經有什麼` connect `drawHighlights` to `登入系統：Keycloak（OIDC）`, `db.py`, `get`, `_paper_or_404`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Should `Anthropic Provider Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.05213089802130898 - nodes in this community are weakly interconnected._
- **Why does `pushLater()` connect `escapeHTML` to `app.js`, `escapeHTML`, `sendAsk`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11260504201680673 - nodes in this community are weakly interconnected._