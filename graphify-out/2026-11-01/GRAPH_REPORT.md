# Graph Report - paper-reader  (2026-11-01)

## Corpus Check
- 45 files · ~41,342 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .example 1, .css 1)

## Summary
- 1025 nodes · 2291 edges · 70 communities (61 shown, 9 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 75 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f98e35da`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- features.py
- test_api.py
- db.py
- re
- sse
- conftest.py
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
- escapeHTML
- pumpTranslation
- data
- Uid
- time
- 登入系統：Keycloak（OIDC）
- auto_highlight
- post
- _paper_or_404
- chat_messages
- 功能對照
- llm.py
- complete_json
- saveNote
- Lantern — 個人用 AI 論文閱讀器
- _to_claude
- 閱讀器：選取、螢光筆與中英對照
- addMsg
- _ingest
- import_url
- UX 第一輪（已定案）
- update_wiki
- oidc_callback
- _ThinkStripper
- s2_get
- ingress.yaml
- containers
- service.yaml
- check
- find_duplicate
- pvc.yaml
- 部署到 k8s
- kustomization.yaml
- test_notes.py
- config.py
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
- test_chat_after_switching_embedding_model
- test_explain_image_with_text_only_model

## God Nodes (most connected - your core abstractions)
1. `conn()` - 50 edges
2. `_paper_or_404()` - 37 edges
3. `escapeHTML()` - 35 edges
4. `sse()` - 33 edges
5. `api()` - 31 edges
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

## Communities (70 total, 9 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.04
Nodes (40): AUTO, calmMotion, card, cardPaper(), caretAt(), CITE_STYLES, citeStyles, COLORS (+32 more)

### Community 1 - "features.py"
Cohesion: 0.15
Nodes (16): _bib_arxiv(), _bib_llm(), _bib_s2(), cite_reason_messages(), citing_contexts(), fetch_bib(), _guess_ref_title(), lookup_reference() (+8 more)

### Community 2 - "test_api.py"
Cohesion: 0.11
Nodes (25): _id(), test_ai_outline(), test_annotation_kinds(), test_annotations_crud(), test_ask_ai_on_selection(), test_author_year_reference(), test_auto_highlight_finds_sentence(), test_bilingual_blocks() (+17 more)

### Community 3 - "db.py"
Cohesion: 0.12
Nodes (24): annotation_paper(), clear_messages(), clear_wiki_messages(), conn(), delete_annotation(), delete_wiki_exchange(), delete_workspace(), get_note() (+16 more)

### Community 4 - "re"
Cohesion: 0.08
Nodes (30): _abstract(), apply_ocr(), _author_year_refs(), Block, _clean(), find_figures(), find_text_rects(), _guess_title() (+22 more)

### Community 5 - "sse"
Cohesion: 0.18
Nodes (12): sse(), claude(), _pid(), test_auto_highlight_json(), test_bilingual_blocks(), test_chat_uses_prompt_cache(), test_explain_image(), test_explain_request_shape() (+4 more)

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
Cohesion: 0.08
Nodes (22): add_to_workspace(), auth_config(), CommentIn, create_workspace(), edit_annotation(), edit_paper(), get_settings(), health() (+14 more)

### Community 15 - "backend/__init__.py"
Cohesion: 0.07
Nodes (16): byline(), _fake(), test_align_invalid_falls_back(), test_align_scoped_to_owner(), test_align_valid_substring(), _translated_block(), FakeKC, _oidc() (+8 more)

### Community 16 - "Workspace LLM Wiki（MVP）"
Cohesion: 0.15
Nodes (12): 1. Wiki 問答（workspace 第三個分頁「論文｜Wiki｜問答」）, 2. 加入論文就自動更新 Wiki（使用者設定）, 3. 閱讀頁反向連結, API, Workspace LLM Wiki（MVP）, 前端, 更新流程（後端，`features.py` 放 prompt）, 決定 (+4 more)

### Community 17 - "escapeHTML"
Cohesion: 0.15
Nodes (25): api(), cardsBusy(), closeAiCard(), enter(), goToPage(), importArxiv(), ingest(), loadLibrary() (+17 more)

### Community 18 - "retrieval.py"
Cohesion: 0.18
Nodes (8): embed(), _bm25(), build_index(), make_chunks(), search(), _tokens(), BM25 retrieval, RAG for long papers

### Community 19 - "drawHighlights"
Cohesion: 0.26
Nodes (17): 1. Lantern 現在已經有什麼, colorKey(), deleteAnnotation(), drawHighlights(), drawLabels(), flashItem(), isHex(), markTranslation() (+9 more)

### Community 20 - "cite.py"
Cohesion: 0.19
Nodes (18): _and(), apa(), bibtex(), _doi(), _end(), ieee(), _initials(), mla() (+10 more)

### Community 21 - "aiCard"
Cohesion: 0.26
Nodes (12): addAnnotation(), aiCard(), commentEditor(), explainCrop(), explainImage(), highlightTranslation(), imageFollowup(), placeFloating() (+4 more)

### Community 22 - "escapeHTML"
Cohesion: 0.14
Nodes (24): 薛西弗斯（等待、完成、空狀態）, addAsk(), addSave(), bibtex(), escapeHTML(), focusWikiTitle(), loadAsk(), loadRelated() (+16 more)

### Community 23 - "pumpTranslation"
Cohesion: 0.20
Nodes (14): alignHighlight(), buildPages(), drawRail(), drawTranslation(), fitText(), overlap(), pumpTranslation(), queueTranslation() (+6 more)

### Community 24 - "data"
Cohesion: 0.07
Nodes (26): apiVersion, data, AUTH_MODE, DISABLE_THINKING, LLM_CONCURRENCY, LLM_CONTEXT_TOKENS, LLM_EFFORT, LLM_MODEL (+18 more)

### Community 25 - "Uid"
Cohesion: 0.14
Nodes (21): auth_users(), chat_clear(), chat_history(), delete(), delete_workspace(), get_note(), me(), paper_wiki() (+13 more)

### Community 26 - "time"
Cohesion: 0.20
Nodes (8): add_annotation(), add_message(), add_wiki_message(), add_workspace(), init(), new_id(), save_note(), upsert_user()

### Community 27 - "登入系統：Keycloak（OIDC）"
Cohesion: 0.05
Nodes (38): delete_paper(), current_user(), _mark_in_library(), k8s 部署要一起處理的事（不處理會壞）, Keycloak 端要建的 client, 建議架構：後端當 OIDC client（Authorization Code + PKCE）, 待確認, 既有資料 (+30 more)

### Community 28 - "auto_highlight"
Cohesion: 0.50
Nodes (4): auto_highlight(), guarded(), one(), _reference_start_page()

### Community 29 - "post"
Cohesion: 0.10
Nodes (20): add_annotation(), AlignIn, AlignMark, AnnotIn, AskIn, chat(), ChatIn, explain() (+12 more)

### Community 30 - "_paper_or_404"
Cohesion: 0.16
Nodes (21): cache_get(), cache_set(), s2_paper_id(), stream_chat(), align(), annotations(), _block_translation(), _cached_text() (+13 more)

### Community 31 - "chat_messages"
Cohesion: 0.19
Nodes (10): chat_messages(), _est_tokens(), full_text_fits(), _header(), note_draft_messages(), _pages_text(), _paper_body(), suggested_questions() (+2 more)

### Community 32 - "功能對照"
Cohesion: 0.20
Nodes (9): ai_outline(), explain_messages(), _history_block(), image_messages(), local_context(), stream_block_translation(), run(), _outline() (+1 more)

### Community 33 - "llm.py"
Cohesion: 0.18
Nodes (5): _mock_answer(), /api/health endpoint, backend/main.py (FastAPI app), Lantern AI Paper Reader, vLLM (Qwen3.5-9B)

### Community 34 - "complete_json"
Cohesion: 0.20
Nodes (9): align_span(), _strip_fence(), _wiki_concept(), _wiki_index(), _wiki_plan(), wiki_qa_page(), complete(), complete_json() (+1 more)

### Community 35 - "saveNote"
Cohesion: 0.25
Nodes (14): fmtDate(), insertIntoNote(), loadNote(), nbKey(), nbMsg(), nbStatus(), noteChanged(), noteConflict() (+6 more)

### Community 36 - "Lantern — 個人用 AI 論文閱讀器"
Cohesion: 0.17
Nodes (11): Lantern — 個人用 AI 論文閱讀器, 各元件的模型, 啟動 vLLM（範例）, 已知限制, 快速開始, 接其他 OpenAI 相容 API, 操作方式（仿 Moonlight）, 架構 (+3 more)

### Community 37 - "_to_claude"
Cohesion: 0.22
Nodes (6): _claude(), _claude_block(), _claude_stream(), _to_claude(), test_cache_breakpoint_only_for_multi_turn(), test_to_claude_conversion()

### Community 38 - "閱讀器：選取、螢光筆與中英對照"
Cohesion: 0.29
Nodes (7): 並排模式：對應的段落亮起來, 螢光筆同步到譯文, 連續的選取與螢光筆, 閱讀器：選取、螢光筆與中英對照, mergeRects(), readSelection(), selRects()

### Community 39 - "addMsg"
Cohesion: 0.38
Nodes (7): addCopy(), addMsg(), hideFigure(), icon(), loadChat(), sendChat(), showFigure()

### Community 40 - "_ingest"
Cohesion: 0.16
Nodes (12): add_paper(), add_to_workspace(), get_paper(), get_settings(), _auto_wiki(), _duplicate(), _first_doi(), _ingest() (+4 more)

### Community 41 - "import_url"
Cohesion: 0.13
Nodes (12): ArxivIn, auto_highlight(), figure_png(), figures(), _figures(), import_url(), paper_pdf(), paper_thumb() (+4 more)

### Community 42 - "UX 第一輪（已定案）"
Cohesion: 0.33
Nodes (5): A. 閱讀頁重新排版, B. 研究主題頁與流程, C. 全站主題切換, UX 第一輪（已定案）, 不做

### Community 43 - "update_wiki"
Cohesion: 0.15
Nodes (11): list_wiki_messages(), wiki_mark_ingested(), wiki_page(), wiki_pages(), wiki_pending(), wiki_save(), update_wiki(), wiki_ask_messages() (+3 more)

### Community 45 - "_ThinkStripper"
Cohesion: 0.25
Nodes (3): _ThinkStripper, 名詞解釋, test_think_stripper()

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

### Community 55 - "test_notes.py"
Cohesion: 0.29
Nodes (3): test_delete_paper_deletes_note(), test_note_crud_and_conflict(), test_note_draft()

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
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Lantern AI Paper Reader` connect `llm.py` to `app.js`, `features.py`, `db.py`, `re`, `retrieval.py`?**
  _High betweenness centrality (0.233) - this node is a cross-community bridge._
- **What connects `lantern-paper-reader`, `Semantic Scholar API`, `graphify-out/graph.json` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.js` be split into smaller, more focused modules?**
  _Cohesion score 0.043740573152337855 - nodes in this community are weakly interconnected._
- **Why does `1. Lantern 現在已經有什麼` connect `drawHighlights` to `登入系統：Keycloak（OIDC）`, `Uid`, `update_wiki`, `_paper_or_404`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Should `features.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14624505928853754 - nodes in this community are weakly interconnected._
- **Why does `pushLater()` connect `escapeHTML` to `app.js`, `escapeHTML`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Should `test_api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10606060606060606 - nodes in this community are weakly interconnected._