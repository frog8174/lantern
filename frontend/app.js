/* Lantern 前端：純 JS，不需要打包工具。
 *
 * 結構：
 *   PDF.js 把每一頁畫成 <canvas>（看得到的圖），再疊一層透明的 textLayer（選得到的字）
 *   ，再疊一層 hlLayer（螢光筆）。三層座標一致，所以選到的字、標註都能對齊。
 *   每頁旁邊另有一個 .twin（並排翻譯用的譯文頁），平常隱藏。
 *
 * 互動（仿 Moonlight）：選字 → 浮動工具列（解釋 / 螢光筆 / 翻譯 / 註解 / Ask AI）→ 浮動 AI 卡片；
 * 右側面板五個分頁：讀懂（摘要、解釋紀錄、聊天）｜標註｜筆記｜文獻｜Wiki。
 * PDF 區的捲軸換成「頁面導軌」（#rail），縮放與頁碼是右下角的浮動小控制。
 */
pdfjsLib.GlobalWorkerOptions.workerSrc =
  "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

const COLORS = ["yellow", "green", "blue", "pink", "purple"];
// 自訂色：存成 #rrggbb；篩選時歸在 "custom" 這一類
const isHex = (c) => /^#[0-9a-f]{6}$/i.test(c || "");
const colorKey = (c) => (isHex(c) ? "custom" : c);
const tint = (hex, a) => `rgba(${[1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(", ")}, ${a})`;
const store = {  // localStorage 可能被封鎖（無痕視窗等），讀寫失敗就用預設值
  get(k, d) { try { return localStorage.getItem(k) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* 忽略 */ } },
  del(k) { try { localStorage.removeItem(k); } catch { /* 忽略 */ } },
};
let customColor = store.get("lantern.customColor", "#7f9ea0");
const AUTO = { "auto:novelty": "新穎", "auto:method": "方法", "auto:result": "結果" };

const S = {
  paper: null, pdf: null, scale: 1.2, pages: [], annotations: [], figures: [], refs: [],
  current: 0, observer: null, cropping: false, chatBusy: false,
  trMode: "off", tr: {}, trQueue: [], trBusy: false,  // 翻譯：tr[頁] = 區塊陣列
  hlColor: "yellow",
  filter: { colors: new Set([...COLORS, "custom"]), auto: true, autoKinds: new Set(Object.keys(AUTO)), labels: true, q: "" },
};

/* ---------------- API 與串流 ---------------- */
async function api(path, opts = {}) {
  const r = await reach(path, {
    headers: opts.body && !(opts.body instanceof FormData) ? { "Content-Type": "application/json" } : {},
    ...opts,
    body: opts.body && !(opts.body instanceof FormData) ? JSON.stringify(opts.body) : opts.body,
  });
  // 沒登入或登入失效；已經在用（有 view）才算中途失效，登入頁改顯示休息的薛西弗斯
  if (r.status === 401 && document.body.dataset.view !== "login") showLogin(!!document.body.dataset.view);
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText);
  return r.json();
}

/** fetch 本身失敗（不是 HTTP 錯誤）＝連不上伺服器：亮起 #offline；之後有回應就收起來。 */
async function reach(path, opts) {
  try {
    const r = await fetch(path, opts);
    $("#offline").hidden = true;
    return r;
  } catch (e) {
    $("#offline").hidden = false;
    throw e;
  }
}

/** 讀 SSE：伺服器每推一段 data: {"t": "..."}，就呼叫 onText 一次。 */
async function stream(path, { body, method = "POST" } = {}, onText) {
  const r = await reach(path, {
    method, headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText);
  const reader = r.body.getReader();
  const dec = new TextDecoder();
  let buf = "", full = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let i;
    while ((i = buf.indexOf("\n\n")) !== -1) {
      const line = buf.slice(0, i).replace(/^data: /, "");
      buf = buf.slice(i + 2);
      if (line === "[DONE]") return full;
      const msg = JSON.parse(line);
      if (msg.error) throw new Error(msg.error);
      full += msg.t;
      onText(full, msg.t);
    }
  }
  return full;
}

/* ---------------- Markdown + LaTeX 顯示 ---------------- */
function renderMD(el, text) {
  // 先把公式挖出來，避免 marked 把 _ 和 * 當成斜體
  const math = [];
  const protect = text.replace(/\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]|\$[^$\n]+?\$|\\\([^\n]+?\\\)/g, (m) => {
    math.push(m); return `@@MATH${math.length - 1}@@`;
  });
  let html = DOMPurify.sanitize(marked.parse(protect));
  html = html.replace(/@@MATH(\d+)@@/g, (_, i) => math[i].replace(/&/g, "&amp;").replace(/</g, "&lt;"));
  // [p.3] → 可點擊跳頁
  html = html.replace(/\[p\.?\s*(\d+)\]/gi, '<a class="pref" data-page="$1">p.$1</a>');
  el.innerHTML = html;
  el.classList.add("md");
  try {
    renderMathInElement(el, {
      delimiters: [
        { left: "$$", right: "$$", display: true }, { left: "\\[", right: "\\]", display: true },
        { left: "$", right: "$", display: false }, { left: "\\(", right: "\\)", display: false },
      ], throwOnError: false,
    });
  } catch (_) { /* KaTeX 失敗就顯示原文 */ }
}
document.addEventListener("click", (e) => {
  const a = e.target.closest("a.pref");
  if (a) goToPage(+a.dataset.page - 1);
});

function escapeHTML(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
const icon = (name) => `<svg><use href="#i-${name}"/></svg>`;
// 外部資料（Semantic Scholar）給的網址只接受 http(s)，擋掉 javascript: 之類
const safeUrl = (u) => (/^https?:\/\//i.test(u || "") ? escapeHTML(u) : "#");
const fmtDate = (t) => new Date(t * 1000).toLocaleString("zh-TW", { dateStyle: "short", timeStyle: "short" });

/** 滑鼠座標底下的字：回傳 Range（startContainer = 文字節點、startOffset = 第幾個字）。 */
function caretAt(x, y) {
  if (document.caretRangeFromPoint) return document.caretRangeFromPoint(x, y);
  const p = document.caretPositionFromPoint?.(x, y);
  if (!p) return null;
  const r = document.createRange(); r.setStart(p.offsetNode, p.offset); return r;
}

/* ---------------- 論文庫 ---------------- */
// sideList：閱讀頁左欄列的論文＝這篇所在研究主題的論文（從「全部論文」開的就是全部）
let library = [], tagFilter = null, sideList = [];

async function loadLibrary() {
  library = await api("/api/papers");
  renderLibrary();
}

function renderLibrary() {
  const q = $("#libSearch").value.trim().toLowerCase();
  // 標籤列：所有用過的標籤，點一下只看那個標籤
  const tags = [...new Set(sideList.flatMap((p) => p.tags))].sort();
  if (tagFilter && !tags.includes(tagFilter)) tagFilter = null;
  $("#tagBar").innerHTML = tags.map((t) =>
    `<button class="chip ${t === tagFilter ? "on" : ""}" data-tag="${escapeHTML(t)}">#${escapeHTML(t)}</button>`).join("");
  $$("#tagBar .chip").forEach((b) => (b.onclick = () => {
    tagFilter = tagFilter === b.dataset.tag ? null : b.dataset.tag; renderLibrary();
  }));

  const ul = $("#paperList");
  ul.innerHTML = "";
  const shown = sideList.filter((p) => (!tagFilter || p.tags.includes(tagFilter))
    && (!q || `${p.title} ${p.filename} ${p.tags.join(" ")}`.toLowerCase().includes(q)));
  if (!sideList.length) ul.innerHTML = '<li class="muted small">還沒有論文</li>';
  else if (!shown.length) ul.innerHTML = '<li class="muted small">沒有符合的論文；按 Enter 搜尋全文</li>';
  for (const p of shown) {
    const li = document.createElement("li");
    li.dataset.id = p.id;
    li.innerHTML = `<div class="ptitle"><span>${escapeHTML(p.title || p.filename)}</span>
        ${p.tags.length ? `<div class="ptags">${p.tags.map((t) => `<span>#${escapeHTML(t)}</span>`).join(" ")}</div>` : ""}</div>
      <button class="del tagbtn" data-k="tag" title="編輯標籤">#</button>`;
    if (S.paper && S.paper.id === p.id) { li.classList.add("on"); li.setAttribute("aria-current", "page"); }
    li.onclick = async (e) => {
      const k = e.target.dataset.k;
      if (k === "tag") {
        const v = prompt("標籤（用逗號分隔，例如：NLP, 待讀）", p.tags.join(", "));
        if (v === null) return;
        p.tags = (await api(`/api/papers/${p.id}`, { method: "PATCH", body: { tags: v.split(/[,，]/) } })).tags;
        renderLibrary();
      } else { mainEl.classList.remove("showlib"); openPaper(p.id); }
    };
    ul.appendChild(li);
  }
}
async function loadSideList() {
  const ws = S.fromWs;
  $("#sideHead").textContent = ws ? "同主題的論文" : "全部論文";
  const list = ws ? await api(`/api/papers?workspace=${encodeURIComponent(ws.id)}`) : (await loadLibrary(), library);
  if (S.fromWs !== ws) return;  // 等的時候又換了來源
  sideList = list;
  renderLibrary();
}

$("#libSearch").addEventListener("input", renderLibrary);
$("#libSearch").addEventListener("keydown", async (e) => {
  if (e.key !== "Enter" || e.isComposing) return;
  const q = e.target.value.trim();
  if (q.length < 2) return;
  const out = $("#searchList");
  $("#searchOut").hidden = false;
  out.innerHTML = '<li class="muted small">搜尋中…</li>';
  const hits = await api(`/api/search?q=${encodeURIComponent(q)}`);
  out.innerHTML = hits.length ? "" : '<li class="muted small">所有論文裡都找不到</li>';
  const re = new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
  for (const h of hits) {
    const li = document.createElement("li");
    li.innerHTML = `<div><div class="small muted">${escapeHTML(h.title)}　p.${h.page + 1}</div>
      <div class="small">${escapeHTML(h.snippet).replace(re, (m) => `<mark>${m}</mark>`)}</div></div>`;
    li.onclick = async () => {
      if (S.paper?.id !== h.paper_id) await openPaper(h.paper_id);
      setTimeout(() => goToPage(h.page), 300);
    };
    out.appendChild(li);
  }
});
$("#searchClose").onclick = () => { $("#searchOut").hidden = true; };

/** 薛西弗斯圖示（docs/design.md）：push＝推石（等待中）、summit＝石頭到頂（完成）、rest＝休息（空狀態浮水印）、fall＝石頭滾回（失敗，做好的保留）。純裝飾，文字另外寫。 */
function sisyphus(kind, size = 48, cls = "") {
  const layers = kind === "rest" ? '<i class="f"></i>' : '<i class="r"></i><i class="f"></i><i class="s"></i>';
  return `<span class="sis sis-${kind} ${cls}" style="--sz:${size}px" aria-hidden="true">${layers}</span>`;
}

/** 等超過 400ms 才用 place(el) 放上推石（短等待不閃一下）；回傳的函式取消或收掉它，可重複呼叫。 */
function pushLater(place, size = 32, text = "", cls = "sis-line") {
  const w = document.createElement("span");
  w.className = cls;
  w.innerHTML = sisyphus("push", size) + (text && `<span class="muted small">${escapeHTML(text)}</span>`);
  const t = setTimeout(() => place(w), 400);
  return () => { clearTimeout(t); w.remove(); };
}

/** 右下角的小提示，5 秒後自己收掉（不擋操作）。 */
function toast(html) {
  const t = $("#toast");
  t.innerHTML = html;
  t.hidden = false;
  clearTimeout(t.timer);
  t.timer = setTimeout(() => { t.hidden = true; }, 5000);
}

async function ingest(promise, st = $("#ingestStatus")) {
  const stay = document.body.dataset.view === "ws";  // 研究主題頁上傳：留在原頁，新卡片排最前面
  st.innerHTML = `<span class="sis-line">${sisyphus("push", 32)}解析中…（擷取文字、建立索引）</span>`;
  try {
    const res = await promise;
    st.textContent = res.duplicate ? `這篇已經在論文庫裡${stay && curWs ? "，已加入這個研究主題" : ""}`
      : `完成：${res.num_pages} 頁、${res.chunks} 個段落`;
    if (res.scanned_pages) {
      // 掃描版：沒文字層的頁要靠 OCR，否則 AI 讀不到內容
      const msg = res.ocr_pages
        ? `其中 ${res.scanned_pages} 頁是掃描圖片，已用 OCR 轉成文字（這些頁無法選字與自動標註）`
        : !res.ocr_enabled
          ? `有 ${res.scanned_pages} 頁是掃描圖片，OCR 已關閉（OCR_ENABLED=false），AI 讀不到這些頁`
          : `有 ${res.scanned_pages} 頁是掃描圖片，OCR 失敗：${res.ocr_error}`;
      st.innerHTML += `<br><span class="${res.ocr_pages ? "warn" : "err"}">${escapeHTML(msg)}</span>`;
    }
    await loadLibrary();
    if (stay) renderWsCards(curWs); else openPaper(res.id);
  } catch (e) {
    st.innerHTML = `<span class="sis-line">${sisyphus("fall", 48)}<span class="err">沒有匯入：${escapeHTML(e.message)}。論文庫沒有變動；確認檔案是 PDF（或 arXiv 編號、網址正確）後再試一次。</span></span>`;
  }
}

// ws：有帶就同時加入那個 workspace；st：顯示進度的元素
function uploadFile(file, ws, st) {
  const fd = new FormData();
  fd.append("file", file);
  if (ws) fd.append("workspace", ws);
  ingest(api("/api/papers", { method: "POST", body: fd }), st);
}
const importArxiv = (url, ws, st) =>
  ingest(api("/api/papers/arxiv", { method: "POST", body: ws ? { url, workspace: ws } : { url } }), st);

/* ---------------- 開啟論文、畫 PDF ---------------- */
async function openPaper(id) {
  S.paper = await api(`/api/papers/${id}`);
  // 從研究主題頁（或它的 Wiki）打開才記下來源；在閱讀頁裡換篇沿用原來的
  if (document.body.dataset.view !== "reader") S.fromWs = curWs;
  setView("reader");
  $("#backName").textContent = S.fromWs?.name || "全部論文";
  $("#btnHome").setAttribute("aria-label", `回到${S.fromWs ? `研究主題「${S.fromWs.name}」` : "全部論文"}`);
  loadSideList().catch(() => {});
  loadNote(id);
  S.annotations = await api(`/api/papers/${id}/annotations`);
  S.tr = {}; S.trQueue = []; S.figures = []; S.refs = [];
  api(`/api/papers/${id}/figures`).then((f) => { S.figures = f; }).catch(() => {});
  api(`/api/papers/${id}/references`).then((r) => { S.refs = r; renderRefs(); }).catch(() => {});
  $("#paperTitle").textContent = S.paper.title;
  $("#empty").hidden = true;
  $("#pageTotal").textContent = `/ ${S.paper.num_pages}`;
  renderOutline(S.paper.outline);
  S.firstPage?.();
  S.firstPage = pushLater((w) => $(".stage").append(w), 64, "打開論文中…", "vwait");  // renderPage 畫好第一頁就收
  try {
    S.pdf = await pdfjsLib.getDocument(`/api/papers/${id}/pdf`).promise;
  } catch (e) {
    S.firstPage();
    throw e;
  }
  buildPages();
  clearTimeout(trPoll);
  watchTranslation(id);
  renderInfo();
  renderActivity();
  $("#summaryOut").innerHTML = "";
  loadPaperWiki(id);
  $("#relatedList").innerHTML = '<li class="muted small">按上方按鈕取得推薦（資料來自 Semantic Scholar）。</li>';
  closeAiCard();
  loadChat();
  history.replaceState(null, "", `#${id}`);
}

/* 背景整篇翻譯：開著的這篇還在翻就每 5 秒看一次，翻完跳提示；換篇或離開閱讀頁就停 */
let trPoll = 0;
async function watchTranslation(id, seen = false) {
  if (S.paper?.id !== id || document.body.dataset.view !== "reader") return;
  const p = (await api("/api/papers").catch(() => [])).find((x) => x.id === id);
  if (S.paper?.id !== id) return;
  if (p?.translating) trPoll = setTimeout(() => watchTranslation(id, true), 5000);
  else if (seen && p) toast(`${sisyphus("summit", 48)}<span>整篇翻譯完成</span>`);
}

function buildPages() {
  const wrap = $("#pages");
  wrap.innerHTML = "";
  const sc = S.paper.scanned_pages.length, oc = S.paper.ocr_pages.length;
  if (sc) {  // 掃描版提示
    const b = document.createElement("div");
    b.className = "banner";
    b.textContent = oc
      ? `這份 PDF 有 ${sc} 頁是掃描圖片，已用 OCR 轉成文字：聊天、摘要可用；這些頁無法選字，請改用「框選」問 AI。`
      : `這份 PDF 有 ${sc} 頁是掃描圖片且沒有 OCR，AI 讀不到這些頁。請設定視覺模型後重新匯入，或改用「框選」。`;
    wrap.appendChild(b);
  }
  S.observer?.disconnect();
  S.pages = [];
  // IntersectionObserver：頁面捲進畫面才畫，100 頁的論文也不會卡
  S.observer = new IntersectionObserver((ents) => {
    for (const e of ents) if (e.isIntersecting) renderPage(+e.target.dataset.page);
  }, { root: $("#viewer"), rootMargin: "600px 0px" });

  S.paper.page_sizes.forEach(([w, h], i) => {
    const row = document.createElement("div");
    row.className = "prow";
    const size = `width:${w * S.scale}px;height:${h * S.scale}px`;
    row.innerHTML = `<div class="page" data-page="${i}" style="${size}"><div class="hlLayer"></div><div class="selLayer"></div>
        <div class="pno">${i + 1} / ${S.paper.num_pages}</div></div>
      <div class="twin" data-page="${i}" style="${size}"><div class="trLayer"></div><div class="pno">譯 ${i + 1}</div></div>`;
    wrap.appendChild(row);
    const el = $(".page", row);
    S.pages.push({ el, twin: $(".twin", row), rendered: false });
    S.observer.observe(el);
  });
  // 最後一頁之後的「書末頁」：每次開論文隨機一句
  const fin = document.createElement("div");
  fin.className = "fin";
  fin.innerHTML = `<div class="fin-mark">Finis</div><p>${escapeHTML(FIN_LINES[Math.floor(Math.random() * FIN_LINES.length)])}</p>`;
  wrap.appendChild(fin);
  $("#zoomLabel").textContent = `${Math.round(S.scale * 100)}%`;
  drawRail();
}

const FIN_LINES = [
  "Scrolled that fast? Surely you read every single word.",
  "The End. Reviewer 2 still has a few comments.",
  "Finished already? The appendix would like a word.",
  "You made it. Now you know more than half the people who cited it.",
  "If you skimmed, your advisor will never know. Probably.",
  "Congratulations, you have officially read the abstract and the conclusion.",
  "Fin. Time to pretend you understood Section 3.",
  "That was the last page. The supplementary material is 40 more.",
];

async function renderPage(i) {
  const pg = S.pages[i];
  if (!pg || pg.rendered) return;
  pg.rendered = true;
  const page = await S.pdf.getPage(i + 1);
  const viewport = page.getViewport({ scale: S.scale });
  const dpr = window.devicePixelRatio || 1;
  const canvas = document.createElement("canvas");
  canvas.width = Math.floor(viewport.width * dpr);
  canvas.height = Math.floor(viewport.height * dpr);
  canvas.style.width = `${viewport.width}px`;
  canvas.style.height = `${viewport.height}px`;
  pg.el.prepend(canvas);
  pg.canvas = canvas;
  await page.render({ canvasContext: canvas.getContext("2d"), viewport,
                      transform: dpr !== 1 ? [dpr, 0, 0, dpr, 0, 0] : null }).promise;
  S.firstPage?.();

  const tl = document.createElement("div");
  tl.className = "textLayer";
  pg.el.style.setProperty("--scale-factor", S.scale);
  pg.el.appendChild(tl);
  await pdfjsLib.renderTextLayer({
    textContentSource: await page.getTextContent(), container: tl, viewport, textDivs: [],
  }).promise;
  // PDF.js 檢視器的做法：拖選時一塊墊底的 endOfContent 蓋滿整層，游標落在字與字之間的空白時，
  // 選取停在最近的字，不會一路跳到頁尾（否則腳註也被選進去）
  const eoc = document.createElement("div");
  eoc.className = "endOfContent";
  tl.appendChild(eoc);
  tl.addEventListener("mousedown", () => tl.classList.add("selecting"));
  drawHighlights(i);
  if (S.trMode === "side") syncTwin(i);
  if (S.trMode !== "off") S.tr[i] ? drawTranslation(i) : queueTranslation(i);
}

/** 標註畫到頁面上：螢光筆、自動標註（含邊欄標籤）、註解（虛線底線 + 邊欄圖示）、解釋（淡底線）。 */
function drawHighlights(i) {
  const pg = S.pages[i];
  if (!pg) return;
  const layer = $(".hlLayer", pg.el);
  layer.innerHTML = "";
  for (const a of S.annotations.filter((a) => a.page === i && visibleOnPage(a))) {
    const cls = AUTO[a.kind] ? a.kind.slice(5) : a.kind === "user" ? colorKey(a.color) : a.kind;
    for (const [x0, y0, x1, y1] of mergeRects(a.rects)) {
      const d = document.createElement("div");
      d.className = `hl ${cls}`;
      d.dataset.id = a.id;
      if (a.kind === "user" && isHex(a.color)) d.style.background = tint(a.color, 0.34);
      Object.assign(d.style, { left: `${x0 * 100}%`, top: `${y0 * 100}%`,
                               width: `${(x1 - x0) * 100}%`, height: `${(y1 - y0) * 100}%` });
      layer.appendChild(d);
    }
    const [x0, y0] = a.rects[0] || [0, 0];
    const side = x0 < 0.5 ? "left" : "right";  // 圖示放在離它最近的頁邊
    if (a.kind === "comment") {
      const m = document.createElement("button");
      m.className = `cmark ${side}`;
      m.style.top = `${y0 * 100}%`;
      m.title = a.comment;
      m.innerHTML = icon("comment");
      m.onclick = () => { openPanel("notes"); flashItem(a.id); };
      layer.appendChild(m);
    }
  }
  drawLabels(i, layer);
  markTranslation(i);
}

/* 自動標註的頁邊標籤：寬螢幕放在紙外的留白（#pages 的 --mgut），細線箭頭指回那段字的第一行；
 * 同一側依目標高度由上往下排、至少隔 LH，不互相疊。並排翻譯時一律放左邊，才不會蓋到譯文頁。
 * 窄螢幕沒有留白，退回放在頁面白邊裡的舊樣式。 */
const wideView = matchMedia("(min-width: 900px)");
wideView.addEventListener("change", refreshHighlights);
function drawLabels(i, layer) {
  if (!S.filter.labels) return;
  const list = S.annotations.filter((a) => a.page === i && AUTO[a.kind] && a.rects[0] && visibleOnPage(a));
  const sideOf = (a) => (S.trMode === "side" || a.rects[0][0] < 0.5 ? "left" : "right");
  if (!wideView.matches) {
    for (const a of list) layer.insertAdjacentHTML("beforeend",
      `<span class="mlabel ${sideOf(a)} ${a.kind.slice(5)}" style="top:${a.rects[0][1] * 100}%">${AUTO[a.kind]}</span>`);
    return;
  }
  const el = S.pages[i].el, W = el.offsetWidth, H = el.offsetHeight;
  const LH = 24, RUN = 28;  // 標籤列高（含間距）、引線在紙外的水平段（px）
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "mlead");
  for (const s of ["left", "right"]) {
    let floor = -Infinity;
    const items = list.filter((a) => sideOf(a) === s).map((a) => {
      const [, y0, , y1] = a.rects[0];  // 指到段落最外緣（所有行最左／最右），高度對齊第一行
      const edge = s === "left" ? Math.min(...a.rects.map((r) => r[0])) : Math.max(...a.rects.map((r) => r[2]));
      return { a, tx: s === "left" ? edge * W - 4 : edge * W + 4, ty: (y0 + y1) / 2 * H };
    }).sort((p, q) => p.ty - q.ty);
    for (const { a, tx, ty } of items) {
      const y = floor = Math.max(ty, floor + LH);
      const k = a.kind.slice(5), sx = s === "left" ? -RUN : W + RUN, bx = s === "left" ? -6 : W + 6;
      // 無印風：一條細淡線，終點一顆小圓點停在段落邊上，不用箭頭
      const path = document.createElementNS(svg.namespaceURI, "path");
      path.setAttribute("class", k);
      path.setAttribute("d", `M${sx} ${y}L${bx} ${y}L${tx} ${ty}`);
      const dot = document.createElementNS(svg.namespaceURI, "circle");
      dot.setAttribute("class", k);
      dot.setAttribute("cx", tx); dot.setAttribute("cy", ty); dot.setAttribute("r", 1.8);
      svg.append(path, dot);
      const b = document.createElement("button");
      b.className = `mlabel out ${s} ${k}`;
      b.style.top = `${y}px`;
      b.textContent = AUTO[a.kind];
      b.title = "在筆記中查看";
      const hot = (on) => {
        path.classList.toggle("hot", on);
        dot.classList.toggle("hot", on);
        $$(`.hl[data-id="${a.id}"]`, layer).forEach((d) => d.classList.toggle("hot", on));
      };
      b.onmouseenter = b.onfocus = () => hot(true);
      b.onmouseleave = b.onblur = () => hot(false);
      b.onclick = () => { openPanel("notes"); flashItem(a.id); };
      layer.appendChild(b);
    }
  }
  layer.prepend(svg);
}

/** 選取 / 標註的矩形 → 每行一條連續色帶。PDF.js 的 span 之間有縫，原始矩形畫出來是一格一格的：
 *  垂直重疊的併成同一行、x 接起來（隔太遠才分開，例如雙欄）；上下兩行靠得近就切在中線，剛好相接不重疊。
 *  存檔時和畫的時候都過一次（結果不變），舊標註不用改資料。座標是頁內 0~1 的 [x0, y0, x1, y1]。 */
function mergeRects(rects) {
  const lines = [];
  for (const r of [...rects].sort((a, b) => a[1] - b[1])) {
    const l = lines.find((l) => Math.min(l.y1, r[3]) - Math.max(l.y0, r[1]) > 0.5 * Math.min(l.y1 - l.y0, r[3] - r[1]));
    if (l) { l.rs.push(r); l.y0 = Math.min(l.y0, r[1]); l.y1 = Math.max(l.y1, r[3]); }
    else lines.push({ y0: r[1], y1: r[3], rs: [r] });
  }
  lines.sort((a, b) => a.y0 - b.y0);
  const near = (p, n) => n.y0 - p.y1 < 0.6 * Math.min(p.y1 - p.y0, n.y1 - n.y0);
  const ys = lines.map((l, k) => {
    const p = lines[k - 1], n = lines[k + 1];
    return [p && near(p, l) ? (p.y1 + l.y0) / 2 : l.y0, n && near(l, n) ? (l.y1 + n.y0) / 2 : l.y1];
  });
  return lines.flatMap((l, k) => {
    const segs = [];
    for (const r of l.rs.sort((a, b) => a[0] - b[0])) {
      const g = segs.at(-1);
      if (g && r[0] - g[1] < 0.025) g[1] = Math.max(g[1], r[2]);
      else segs.push([r[0], r[2]]);
    }
    return segs.map(([x0, x1]) => [x0, ys[k][0], x1, ys[k][1]]);
  });
}
console.assert((() => {  // 同一行兩段接成一條、上下兩行切在中線、雙欄分開；再合併一次結果不變
  const m = mergeRects([[0.1, 0.1, 0.2, 0.12], [0.21, 0.101, 0.4, 0.12], [0.1, 0.125, 0.3, 0.145], [0.6, 0.126, 0.8, 0.145]]);
  return m.length === 3 && m[0][2] === 0.4 && m[0][3] === m[1][1] && JSON.stringify(mergeRects(m)) === JSON.stringify(m);
})(), "mergeRects self-check");

/** 兩個 0~1 矩形重疊的面積。 */
const overlap = (r, b) => Math.max(0, Math.min(r[2], b[2]) - Math.max(r[0], b[0])) * Math.max(0, Math.min(r[3], b[3]) - Math.max(r[1], b[1]));

function visibleOnPage(a) {
  const f = S.filter;
  if (a.kind === "user") return f.colors.has(colorKey(a.color));
  if (AUTO[a.kind]) return f.auto && f.autoKinds.has(a.kind);
  return true;
}

function goToPage(i, flashId) {
  const pg = S.pages[i];
  if (!pg) return;
  pg.el.scrollIntoView({ behavior: calmMotion.matches ? "auto" : "smooth", block: "start" });
  if (flashId) setTimeout(() => {
    $$(`.hl[data-id="${flashId}"]`).forEach((d) => { d.classList.add("flash"); setTimeout(() => d.classList.remove("flash"), 1600); });
  }, 500);
}

$("#viewer").addEventListener("scroll", () => {
  const top = $("#viewer").getBoundingClientRect().top + 80;
  for (const [i, pg] of S.pages.entries()) {
    if (pg.el.getBoundingClientRect().bottom > top) { S.current = i; break; }
  }
  if (document.activeElement !== $("#pageInput")) $("#pageInput").value = S.current + 1;
  syncRail();
  markOutline();
}, { passive: true });

/* ---------------- 頁面導軌：取代閱讀區的捲軸 ----------------
 * 座標都取自 #viewer 這個真正的捲動容器：導軌高度 ↔ scrollHeight。滾輪、觸控板、鍵盤照常捲 #viewer，
 * 導軌只跟著畫。刻度＝有螢光筆或註解的頁，放在那頁最上面一個標註的位置。 */
const viewerEl = $("#viewer"), rail = $("#rail");
const calmMotion = matchMedia("(prefers-reduced-motion: reduce)");
function drawRail() {
  if (!S.pages.length) return;
  const H = viewerEl.scrollHeight || 1, top = new Map();
  for (const a of S.annotations) {
    if ((a.kind === "user" || a.kind === "comment") && a.rects[0]) top.set(a.page, Math.min(top.get(a.page) ?? 1, a.rects[0][1]));
  }
  $(".rticks", rail).innerHTML = [...top].map(([p, y]) => {
    const el = S.pages[p]?.el;  // .page 的 offsetParent 是 #viewer（position: relative），offsetTop 就是捲動座標
    return el ? `<button class="rtick" tabindex="-1" data-page="${p}" aria-label="跳到第 ${p + 1} 頁（有標註）"
      style="top:${((el.offsetTop + y * el.offsetHeight) / H) * 100}%"></button>` : "";
  }).join("");
  $(".rend", rail).textContent = S.pages.length;
  rail.setAttribute("aria-valuemax", S.pages.length);
  syncRail();
}
function syncRail() {
  const H = viewerEl.scrollHeight || 1, n = S.pages.length, cur = S.current + 1;
  const top = (viewerEl.scrollTop / H) * 100, h = Math.min(100, (viewerEl.clientHeight / H) * 100);
  Object.assign($(".rlamp", rail).style, { top: `${top}%`, height: `${h}%` });
  const lab = $(".rcur", rail);
  lab.textContent = cur;
  lab.style.top = `${Math.min(97, Math.max(3, top + h / 2))}%`;
  rail.classList.toggle("at-start", top + h / 2 < 8);
  rail.classList.toggle("at-end", top + h / 2 > 92);
  rail.setAttribute("aria-valuenow", cur);
  rail.setAttribute("aria-valuetext", `第 ${cur} 頁，共 ${n} 頁`);
}
rail.addEventListener("pointerdown", (e) => {
  if (!S.pages.length || e.button !== 0) return;
  const tick = e.target.closest(".rtick");
  if (tick) { e.preventDefault(); return goToPage(+tick.dataset.page); }
  e.preventDefault();
  rail.focus({ preventScroll: true, focusVisible: false });
  const r = rail.getBoundingClientRect(), k = viewerEl.scrollHeight / r.height;
  // 點軌道：那個位置移到畫面中間；點在燈光段上就不跳。接著按住不放都能拖
  if (!e.target.closest(".rlamp")) viewerEl.scrollTop = (e.clientY - r.top) * k - viewerEl.clientHeight / 2;
  const y0 = e.clientY, s0 = viewerEl.scrollTop;
  const move = (ev) => { viewerEl.scrollTop = s0 + (ev.clientY - y0) * k; };
  rail.setPointerCapture(e.pointerId);
  rail.classList.add("dragging");
  rail.addEventListener("pointermove", move);
  rail.addEventListener("lostpointercapture", () => {
    rail.removeEventListener("pointermove", move);
    rail.classList.remove("dragging");
  }, { once: true });
});
rail.addEventListener("keydown", (e) => {
  const n = S.pages.length, c = S.current;
  const to = { ArrowDown: c + 1, ArrowRight: c + 1, PageDown: c + 1, ArrowUp: c - 1, ArrowLeft: c - 1, PageUp: c - 1, Home: 0, End: n - 1 }[e.key];
  if (to == null || !n) return;
  e.preventDefault();
  // 直接跳（不平滑）：連按時 S.current 才跟得上
  S.pages[Math.max(0, Math.min(n - 1, to))].el.scrollIntoView({ block: "start" });
});
// 視窗或面板寬度變了：scrollHeight 跟著變，刻度位置要重算
new ResizeObserver(() => drawRail()).observe(viewerEl);

$("#pageInput").addEventListener("keydown", (e) => {
  if (e.key !== "Enter" || !S.paper) return;
  const n = Math.min(S.paper.num_pages, Math.max(1, parseInt(e.target.value) || 1));
  e.target.value = n;
  goToPage(n - 1);
  e.target.blur();
});

function zoom(f) {
  if (!S.paper) return;
  const v = $("#viewer"), ratio = v.scrollTop / v.scrollHeight;
  S.scale = Math.min(3, Math.max(0.5, +(S.scale * f).toFixed(2)));
  buildPages();
  v.scrollTop = ratio * v.scrollHeight;
}
$("#btnZoomIn").onclick = () => zoom(1.15);
$("#btnZoomOut").onclick = () => zoom(1 / 1.15);
// 窄螢幕的左欄抽屜
function setLibDrawer(on) {
  $("main").classList.toggle("showlib", on);
  $("#toggleLib").setAttribute("aria-expanded", on);
  if (on) $("#lib").focus();
}
$("#toggleLib").onclick = () => setLibDrawer(!$("main").classList.contains("showlib"));
// 寬螢幕的左欄：預設滑過才展開；按圖釘固定（記在這台瀏覽器）
function setLibPin(on) {
  $("main").classList.toggle("libauto", !on);
  $("#libPin").setAttribute("aria-pressed", on);
  try { localStorage.setItem("lantern.libPin", on ? "1" : "0"); } catch {}
}
$("#libPin").onclick = () => setLibPin($("main").classList.contains("libauto"));
setLibPin((() => { try { return localStorage.getItem("lantern.libPin") === "1"; } catch { return false; } })());
$("#togglePanel").onclick = () => $("main").classList.toggle("nopanel");
// 手機寬度：面板預設收起，要看時從頂列的面板鈕叫出來
if (innerWidth < 700) $("main").classList.add("nopanel");

/* ---------------- 活動面板：拖曳左緣調寬、彈出成浮動視窗 ---------------- */
const mainEl = $("main"), panelEl = $(".panel");
const setPanelWidth = (w) => mainEl.style.setProperty("--panel-w", `${w}px`);
setPanelWidth(+store.get("lantern.panelW", 380));
$("#panelGrip").addEventListener("mousedown", (e) => {
  e.preventDefault();
  const grip = e.currentTarget;
  grip.classList.add("dragging");
  let w = panelEl.offsetWidth;
  const move = (ev) => { w = Math.round(Math.min(innerWidth * 0.55, Math.max(280, innerWidth - ev.clientX))); setPanelWidth(w); };
  const up = () => {
    grip.classList.remove("dragging");
    store.set("lantern.panelW", w);
    removeEventListener("mousemove", move); removeEventListener("mouseup", up);
  };
  addEventListener("mousemove", move);
  addEventListener("mouseup", up);
});
function setPanelFloat(on) {
  mainEl.classList.toggle("floatpanel", on);
  mainEl.classList.remove("nopanel");
  if (!on) panelEl.removeAttribute("style");  // 清掉浮動時拖曳 / 拉大小留下的位置與尺寸
  store.set("lantern.panelFloat", on ? "1" : "");
}
$("#panelFloat").onclick = () => setPanelFloat(true);
$("#panelDock").onclick = () => setPanelFloat(false);
makeDraggable(panelEl, $(".phead", panelEl));
if (store.get("lantern.panelFloat", "")) setPanelFloat(true);

/* ---------------- 大綱（可收合） ---------------- */
let outline = [];
function renderOutline(items) {
  // 項目多時預設全部收起，只看得到第一層
  outline = items.map((it, i) => ({ ...it, open: items.length <= 25, parent: (items[i + 1]?.level ?? 0) > it.level }));
  drawOutline();
}
function drawOutline() {
  const ul = $("#outline");
  ul.innerHTML = outline.length ? "" : '<li class="muted small">這份 PDF 沒有目錄，可按「AI 生成」</li>';
  const closedAt = [];  // 目前被收起的祖先層級
  for (const it of outline) {
    while (closedAt.length && closedAt[closedAt.length - 1] >= it.level) closedAt.pop();
    const hidden = closedAt.length > 0;
    if (it.parent && !it.open) closedAt.push(it.level);
    if (hidden) continue;
    const li = document.createElement("li");
    li.dataset.level = Math.min(3, it.level);
    li.dataset.page = it.page;
    li.innerHTML = `<span class="caret">${it.parent ? (it.open ? "▾" : "▸") : ""}</span><span>${escapeHTML(it.title)}</span>`;
    li.onclick = (e) => {
      if (e.target.classList.contains("caret") && it.parent) { it.open = !it.open; drawOutline(); }
      else { setLibDrawer(false); goToPage(it.page); }
    };
    ul.appendChild(li);
  }
  markOutline();
}
/** 目前章節：看得到的大綱項目裡，最後一個起始頁不超過目前頁的那個，用燈光色標示。 */
function markOutline() {
  const items = $$("#outline li[data-page]");
  const cur = items.filter((li) => +li.dataset.page <= S.current).pop();
  items.forEach((li) => (li === cur ? li.setAttribute("aria-current", "location") : li.removeAttribute("aria-current")));
}
$("#btnAiOutline").onclick = async () => {
  if (!S.paper) return;
  $("#outline").innerHTML = '<li class="muted small">生成中…</li>';
  try { renderOutline(await api(`/api/papers/${S.paper.id}/outline-ai`)); }
  catch (e) { $("#outline").innerHTML = `<li class="err small">${escapeHTML(e.message)}</li>`; }
};

/* ---------------- 選字 → 浮動工具列 ---------------- */
const selBar = $("#selBar");
let lastSel = null;

$("#palette").innerHTML = COLORS.map((c, i) =>
  `<button class="sw ${c}" data-color="${c}" title="螢光筆 ${i + 1}">${i + 1}</button>`).join("") +
  `<span class="customsw"><button class="sw" data-color="custom" title="自訂色">6</button>
   <input type="color" id="customColor" title="換自訂色（選好就直接畫上）" aria-label="自訂螢光筆顏色"></span>`;
const customSw = $('#palette [data-color="custom"]');
function setCustomColor(c) {
  customColor = c;
  customSw.style.background = c;
  $("#customColor").value = c;
}
setCustomColor(customColor);
// 選好顏色就記住，並直接用新顏色畫上目前選取的文字
$("#customColor").addEventListener("change", (e) => {
  setCustomColor(e.target.value);
  store.set("lantern.customColor", customColor);
  S.hlColor = customColor;
  selAction("highlight");
});

/** 讀目前的選取：文字、頁碼、頁內 0~1 座標（存標註用）、螢幕上的範圍（擺浮動元件用）。 */
/** block：選在譯文（.trb，並排頁或疊加層）裡時是第幾個翻譯區塊，否則 null。 */
function readSelection() {
  const sel = getSelection();
  const text = sel.toString().trim();
  const pageEl = sel.anchorNode?.parentElement?.closest(".page, .twin");
  if (!text || text.length < 2 || !pageEl || !sel.rangeCount) return null;
  const range = sel.getRangeAt(0), trb = sel.anchorNode.parentElement.closest(".trb");
  return { text: text.replace(/\s+/g, " "), page: +pageEl.dataset.page, rects: mergeRects(selRects(range, pageEl)),
           box: range.getBoundingClientRect(), block: trb ? +trb.dataset.i : null };
}

/** range 落在 el（原文頁或譯文頁）上的矩形，換成 el 內 0~1 座標。 */
function selRects(range, el) {
  const pr = el.getBoundingClientRect();
  return [...range.getClientRects()]
    .filter((r) => r.width > 1 && r.height > 1 && r.top >= pr.top - 2 && r.bottom <= pr.bottom + 2
                   && r.left >= pr.left - 2 && r.right <= pr.right + 2)
    .map((r) => [(r.left - pr.left) / pr.width, (r.top - pr.top) / pr.height,
                 (r.right - pr.left) / pr.width, (r.bottom - pr.top) / pr.height]);
}

/* 選取中：原文頁改畫自己的連續選取色帶（原生 ::selection 被 span 縫隙切碎，CSS 已設透明）；
 * 並排模式再點亮對應的區塊：選英文 → 譯文區塊亮框、原文區塊淡框；選中文也一樣兩邊都亮。 */
let litEls = [];
document.addEventListener("selectionchange", () => {
  litEls.forEach((el) => (el.classList.contains("trb") ? el.classList.remove("lit") : el.remove()));
  litEls = [];
  clearLitAlign();
  const sel = getSelection();
  const host = !sel.isCollapsed && sel.rangeCount && sel.anchorNode?.parentElement?.closest(".page, .twin");
  const i = host ? +host.dataset.page : -1, pg = S.pages[i];
  if (!pg) return;
  const range = sel.getRangeAt(0), rects = mergeRects(selRects(range, host));
  const box = (r, cls) => {
    const d = document.createElement("div");
    d.className = cls;
    Object.assign(d.style, { left: `${r[0] * 100}%`, top: `${r[1] * 100}%`,
                             width: `${(r[2] - r[0]) * 100}%`, height: `${(r[3] - r[1]) * 100}%` });
    $(".selLayer", pg.el).appendChild(d);
    litEls.push(d);
  };
  if (host === pg.el && !sel.anchorNode.parentElement.closest(".trb")) rects.forEach((r) => box(r, "sel"));
  const blocks = S.trMode === "side" && S.tr[i];
  if (!blocks) return;
  const lit = host === pg.twin
    ? $$(".trb", pg.twin).filter((d) => range.intersectsNode(d)).map((d) => +d.dataset.i)
    : blocks.flatMap((b, k) => (b.tr && rects.some((r) => overlap(r, b.bbox) > 0) ? [k] : []));
  for (const k of lit) {
    const d = $(`.trb[data-i="${k}"]`, pg.twin);
    if (d) { d.classList.add("lit"); litEls.push(d); }
    box(blocks[k].bbox, "srcbox");
  }
});

/* 並排模式的逐句對應：選完字（放開滑鼠）後問 /align，對方那邊只亮「對應的那句」，取代整段的淡框。
 * 英→中：譯文裡那段用燈光色 mark 標出（借 markTranslation 畫）；中→英：原文頁畫出那句的位置。結果有伺服器快取。 */
let litAlign = null, litJob = 0;
function clearLitAlign() {
  litJob++;
  if (!litAlign) return;
  const p = litAlign.page;
  litAlign = null;
  markTranslation(p);
}
async function correspond(sel) {
  const blocks = S.trMode === "side" && S.tr[sel.page];
  if (!blocks?.done) return;
  const fromZh = sel.block != null;
  const area = (b) => sel.rects.reduce((s, r) => s + overlap(r, b.bbox), 0);
  const k = fromZh ? sel.block : blocks.reduce((best, b, j) => (b.tr && area(b) > (best < 0 ? 0 : area(blocks[best])) ? j : best), -1);
  if (k < 0 || !blocks[k]?.tr) return;
  const job = ++litJob, pid = S.paper.id, pg = S.pages[sel.page];
  const r = await api(`/api/papers/${pid}/align`, { method: "POST",
    body: { page: sel.page, block: k, quote: sel.text.slice(0, 2000), direction: fromZh ? "zh2en" : "en2zh" } }).catch(() => null);
  if (job !== litJob || S.paper?.id !== pid || !r?.match) return;  // 選取已經換了，或對不到（保留整段淡框）
  litEls.filter((el) => el.classList.contains("srcbox") || el.classList.contains("trb"))
    .forEach((el) => (el.classList.contains("trb") ? el.classList.remove("lit") : el.remove()));
  if (fromZh) {
    for (const rc of r.rects || []) {
      const d = document.createElement("div");
      d.className = "srclit";
      Object.assign(d.style, { left: `${rc[0] * 100}%`, top: `${rc[1] * 100}%`,
                               width: `${(rc[2] - rc[0]) * 100}%`, height: `${(rc[3] - rc[1]) * 100}%` });
      $(".selLayer", pg.el).appendChild(d);
      litEls.push(d);
    }
  } else {
    litAlign = { page: sel.page, block: k, zh: r.match };
    markTranslation(sel.page);
  }
}

document.addEventListener("mouseup", (e) => {
  $$(".textLayer.selecting").forEach((t) => t.classList.remove("selecting"));
  if (e.button !== 0 || selBar.contains(e.target) || S.cropping || crop) return;
  if (!e.target.closest?.("#pages")) return;
  setTimeout(() => {
    lastSel = readSelection();
    if (!lastSel) { selBar.hidden = true; return; }
    const b = lastSel.box;
    $("#askInput").hidden = true;
    selBar.hidden = false;
    const w = selBar.offsetWidth;
    selBar.style.left = `${Math.min(innerWidth - w - 8, Math.max(8, b.left + b.width / 2 - w / 2))}px`;
    selBar.style.top = `${b.top > 110 ? b.top - 52 : b.bottom + 10}px`;
    correspond(lastSel);
  }, 0);
});
document.addEventListener("mousedown", (e) => {
  if (!selBar.contains(e.target)) selBar.hidden = true;
  if (!$("#ctxMenu").contains(e.target)) $("#ctxMenu").hidden = true;
  if (!$("#citeCard").contains(e.target)) $("#citeCard").hidden = true;
  if (!$("#figCard").contains(e.target)) $("#figCard").hidden = true;
  if (mainEl.classList.contains("showlib") && !e.target.closest("#lib, #toggleLib")) setLibDrawer(false);
});

selBar.addEventListener("click", (e) => {
  const sw = e.target.closest("[data-color]");
  if (sw) { S.hlColor = sw.dataset.color === "custom" ? customColor : sw.dataset.color; return selAction("highlight"); }
  const b = e.target.closest("[data-act]");
  if (b?.dataset.act === "ask") {  // 「問 AI」：在工具列上展開輸入框
    const ask = $("#askInput");
    ask.hidden = false;
    selBar.style.left = `${Math.max(8, Math.min(innerWidth - selBar.offsetWidth - 8, parseFloat(selBar.style.left)))}px`;
    return ask.focus();
  }
  if (b) selAction(b.dataset.act);
});
$("#askInput").addEventListener("keydown", (e) => {
  if (e.key !== "Enter" || e.isComposing || !e.target.value.trim()) return;
  const q = e.target.value.trim();
  e.target.value = "";
  selAction("ask", q);
});

async function selAction(act, question = "") {
  const sel = lastSel;
  if (!sel || !S.paper) return;
  selBar.hidden = true;
  $("#ctxMenu").hidden = true;
  const { text, page, rects, box } = sel;
  const quote = `<blockquote>${escapeHTML(text.length > 220 ? text.slice(0, 220) + "…" : text)}</blockquote>`;
  const base = `/api/papers/${S.paper.id}`;
  if (act === "copy") return navigator.clipboard.writeText(text);
  if (act === "highlight") {
    getSelection().removeAllRanges();
    if (sel.block != null) return highlightTranslation(sel);
    return alignHighlight(await addAnnotation({ page, rects, color: S.hlColor, text }));
  }
  if (act === "comment") return commentEditor(sel);
  if (act === "quote") { getSelection().removeAllRanges(); return quoteToNote(text, page); }
  if (act === "translate") {
    return aiCard({ title: "翻譯", anchor: box, quote, url: `${base}/translate`, body: { text, page } });
  }
  // explain / ask：結果記到活動面板的「解釋」
  aiCard({
    title: question ? `問：${question}` : "解釋", anchor: box, quote, question,
    url: `${base}/explain`, body: { text, page, question },
    followup: textFollowup(text, page),
    save: (thread) => addAnnotation({ page, rects, text, kind: "explain", color: "explain", comment: thread }),
  });
}

// 快捷鍵：選字後按 E 解釋、H 螢光筆、T 翻譯、C 註解、Q 引用到筆記；Esc 關閉浮動元件
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    setCropping(false); clearCrop(); closeAiCard(); setLibDrawer(false);
    selBar.hidden = true; $("#ctxMenu").hidden = true; $("#citeCard").hidden = true; hideFigure();
    return;
  }
  if (selBar.hidden || e.ctrlKey || e.metaKey || e.altKey || /INPUT|TEXTAREA/.test(document.activeElement?.tagName)) return;
  const act = { e: "explain", h: "highlight", t: "translate", c: "comment", q: "quote" }[e.key.toLowerCase()];
  if (act) { e.preventDefault(); selAction(act); }
});

/* ---------------- 右鍵選單 ---------------- */
$("#pages").addEventListener("contextmenu", (e) => {
  const sel = readSelection();
  if (!sel) return;  // 沒選字就用瀏覽器原本的選單
  e.preventDefault();
  lastSel = sel;
  selBar.hidden = true;
  const m = $("#ctxMenu");
  m.hidden = false;
  m.style.left = `${Math.min(innerWidth - 180, e.clientX)}px`;
  m.style.top = `${Math.min(innerHeight - 230, e.clientY)}px`;
});
$("#ctxMenu").addEventListener("click", (e) => {
  const b = e.target.closest("[data-act]");
  if (b) selAction(b.dataset.act);
});

/* ---------------- 浮動 AI 卡片 ---------------- */
const card = $("#aiCard");
let cardJob = 0;  // 開新卡片時，舊的串流結果就不要再寫進來

function placeFloating(el, anchor, width) {
  if (el.dataset.sized) width = el.offsetWidth || width;  // 使用者拉過大小就沿用，只換位置
  else el.style.width = `${width}px`;
  el.style.left = `${Math.min(innerWidth - width - 12, Math.max(12, anchor.left))}px`;
  const below = innerHeight - anchor.bottom - 16;
  if (el.dataset.sized) {
    const h = el.offsetHeight;
    el.style.maxHeight = "none"; el.style.bottom = "";
    el.style.top = `${Math.max(8, below >= h ? anchor.bottom + 10 : Math.min(innerHeight - h - 8, anchor.top - h - 10))}px`;
  } else if (below >= 280) {
    el.style.top = `${anchor.bottom + 10}px`; el.style.bottom = "";
    el.style.maxHeight = `${below - 10}px`;
  } else {
    el.style.top = ""; el.style.bottom = `${innerHeight - anchor.top + 10}px`;
    el.style.maxHeight = `${Math.max(240, anchor.top - 70)}px`;
  }
}

function closeAiCard() { card.hidden = true; cardJob++; }

/** 串流一段回答到 target，回傳完整文字；失敗就在 target 顯示錯誤並回傳 null。 */
// wait：第一段文字出來前，在 target 裡放多大的推石（0 = 不放）
async function streamInto(target, url, body, method = "POST", wait = 0) {
  target.classList.add("cursor");
  const stop = wait ? pushLater((w) => target.append(w), wait, "回答中…") : () => {};
  try {
    const full = await stream(url, { body, method }, (t) => { stop(); renderMD(target, t); });
    renderMD(target, full);
    return full;
  } catch (e) {
    target.innerHTML = `<span class="err">${escapeHTML(e.message)}</span>`;
    return null;
  } finally {
    stop();
    target.classList.remove("cursor");
  }
}

/**
 * 開一張浮動卡片，串流 url 的回答。
 * save(answer)：第一段回答完成後呼叫（存解釋紀錄）；followup(q) 回傳 {url, body}：卡片底部可以追問。
 */
// 解釋紀錄的格式：第一段 + 每次追問以 --- 分隔。** 後面要空一格，否則緊接全形冒號時粗體不會生效
const qa = (q, a) => (q ? `**問：** ${q}\n\n${a}` : a);

/**
 * prior + annId：從「解釋」分頁接續舊對話（不重新產生，直接顯示先前的問答）。
 * card.thread 是整串對話的 Markdown，追問時當作 history 送給後端，也會存回解釋紀錄。
 */
async function aiCard({ title, anchor, quote = "", url, body, method = "POST", question = "", save = null,
                        followup = null, html = null, prior = null, annId = null }) {
  const job = ++cardJob;
  card.hidden = false;
  $(".atitle", card).textContent = title;
  const bodyEl = $(".abody", card);
  bodyEl.innerHTML = quote;
  $(".afollow", card).hidden = !followup;
  card.followup = followup;
  card.thread = prior || "";
  card.annId = annId;
  placeFloating(card, anchor, 460);
  if (html) { bodyEl.insertAdjacentHTML("beforeend", html); return; }
  const out = document.createElement("div");
  out.className = "ans";
  bodyEl.appendChild(out);
  if (prior) { renderMD(out, prior); $("input", $(".afollow", card)).focus(); return; }
  const full = await streamInto(out, url, body, method);
  if (job !== cardJob) return;
  // 回答第一行若是「## 標題」，拿來當卡片標題（Moonlight 的 "Understanding …"）
  const h = full && full.match(/^\s*##\s*(.+)/);
  if (h) { $(".atitle", card).textContent = h[1].trim(); $("h2", out)?.remove(); }
  if (!full) return;
  card.thread = qa(question, full);
  if (save) {
    const a = await save(card.thread);
    if (job === cardJob) card.annId = a.id;
  }
}

$(".afollow", card).addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = $("input", e.target), q = input.value.trim();
  if (!q || !card.followup) return;
  input.value = "";
  const job = cardJob;
  const { url, body } = card.followup(q, card.thread);
  const bodyEl = $(".abody", card);
  bodyEl.insertAdjacentHTML("beforeend", `<div class="fq">${escapeHTML(q)}</div>`);
  const out = document.createElement("div");
  out.className = "ans";
  bodyEl.appendChild(out);
  out.scrollIntoView({ block: "end" });
  const full = await streamInto(out, url, body);
  if (!full || job !== cardJob) return;
  // 追問也存回解釋紀錄，之後關掉卡片還能從「解釋」分頁接續
  card.thread = `${card.thread}\n\n---\n\n${qa(q, full)}`;
  const a = S.annotations.find((x) => x.id === card.annId);
  if (a) {
    a.comment = card.thread;
    api(`/api/annotations/${a.id}`, { method: "PATCH", body: { comment: a.comment } });
    renderExplains();
  }
});
card.addEventListener("click", (e) => {
  const k = e.target.closest("[data-k]")?.dataset.k;
  if (k === "close") closeAiCard();
  if (k === "copy") navigator.clipboard.writeText($$(".ans", card).map((a) => a.innerText).join("\n\n"));
});
makeDraggable(card, $(".ahead", card));
// 右下角拉大小（CSS resize）：拉過之後記住尺寸，自動算的 max-height 也要拿掉，否則拉不高
let cardSize = null;
card.addEventListener("mousedown", (e) => {
  const r = card.getBoundingClientRect();  // 只認右下角的拉把，避免串流中內容長高被誤判成手動調整
  if (e.clientX > r.right - 20 && e.clientY > r.bottom - 20) cardSize = [card.offsetWidth, card.offsetHeight];
});
addEventListener("mouseup", () => {
  if (cardSize && (cardSize[0] !== card.offsetWidth || cardSize[1] !== card.offsetHeight)) {
    card.dataset.sized = "1";
    card.style.maxHeight = "none";
  }
  cardSize = null;
});

/** 拖曳標題列移動浮動視窗。 */
function makeDraggable(el, handle) {
  handle.addEventListener("mousedown", (e) => {
    if (e.target.closest("button")) return;
    const r = el.getBoundingClientRect(), dx = e.clientX - r.left, dy = e.clientY - r.top;
    const move = (ev) => {
      el.style.left = `${Math.max(0, Math.min(innerWidth - 80, ev.clientX - dx))}px`;
      el.style.top = `${Math.max(0, Math.min(innerHeight - 40, ev.clientY - dy))}px`;
      el.style.bottom = "auto"; el.style.right = "auto";
    };
    const up = () => { removeEventListener("mousemove", move); removeEventListener("mouseup", up); };
    addEventListener("mousemove", move);
    addEventListener("mouseup", up);
    e.preventDefault();
  });
}

/* ---------------- 註解 ---------------- */
function commentEditor(sel) {
  const quote = `<blockquote>${escapeHTML(sel.text.slice(0, 220))}</blockquote>`;
  aiCard({ title: "新增註解", anchor: sel.box, quote,
           html: `<textarea class="cedit" rows="4" placeholder="寫下你的想法或疑問…"></textarea>
                  <div class="row end"><button class="link small" data-c="cancel">取消</button><button data-c="save">儲存</button></div>` });
  const ta = $(".cedit", card);
  ta.focus();
  $('[data-c="cancel"]', card).onclick = closeAiCard;
  $('[data-c="save"]', card).onclick = async () => {
    if (!ta.value.trim()) return;
    await addAnnotation({ page: sel.page, rects: sel.rects, text: sel.text, kind: "comment", color: "comment",
                          comment: ta.value.trim() });
    closeAiCard();
    getSelection().removeAllRanges();
    openPanel("notes");
  };
}

async function addAnnotation(body) {
  const a = await api(`/api/papers/${S.paper.id}/annotations`, { method: "POST", body });
  S.annotations.push(a);
  drawHighlights(a.page);
  renderActivity();
  return a;
}

async function deleteAnnotation(a) {
  await api(`/api/annotations/${a.id}`, { method: "DELETE" });
  S.annotations = S.annotations.filter((x) => x.id !== a.id);
  drawHighlights(a.page);
  renderActivity();
}

/** 英文螢光筆 → 問模型譯文裡對應哪一段，存在標註上（之後不再問）。對應到重疊面積最大的翻譯區塊。
 *  譯文還沒翻完時先跳過；那頁翻完時 pumpTranslation 會再掃一次沒有 align 的螢光筆補上。 */
async function alignHighlight(a) {
  const blocks = S.tr[a.page];
  if (!blocks?.done) return;
  const area = (b) => a.rects.reduce((s, r) => s + overlap(r, b.bbox), 0);
  const k = blocks.reduce((best, b, j) => (b.tr && area(b) > (best < 0 ? 0 : area(blocks[best])) ? j : best), -1);
  if (k < 0) return;
  const r = await api(`/api/papers/${S.paper.id}/align`, { method: "POST",
    body: { page: a.page, block: k, quote: a.text.slice(0, 2000) } }).catch(() => ({ match: "" }));
  a.align = { block: k, zh: r.match };
  await api(`/api/annotations/${a.id}`, { method: "PATCH", body: { align: a.align } }).catch(() => {});
  drawHighlights(a.page);
}

/** 在譯文上畫螢光筆：對回英文原句、標在原文頁上（譯文那段也標）；對不到就標整個原文區塊。 */
async function highlightTranslation(sel) {
  const { page, block, text } = sel, b = S.tr[page]?.[block];
  if (!b) return;
  const r = await api(`/api/papers/${S.paper.id}/align`, { method: "POST",
    body: { page, block, quote: text.slice(0, 2000), direction: "zh2en" } }).catch(() => ({ match: "", rects: [b.bbox] }));
  return addAnnotation({ page, rects: r.rects, color: S.hlColor, text: r.match || text, align: { block, zh: text } });
}

/* ---------------- 圖表預覽：滑過 "Figure 3" / "Table 2" ---------------- */
const figCard = $("#figCard");
const FIG_RE = /\b(Figure|Fig\.?|Table|Tab\.)\s*(\d+)/gi;
let figKey = null, figShowT = null, figHideT = null, figMoveT = 0;

function figureUnder(x, y) {
  const pos = caretAt(x, y);
  const node = pos?.startContainer;
  if (!node || node.nodeType !== 3 || !node.parentElement.closest(".textLayer")) return null;
  // "Figure" 和 "3" 有時被 PDF.js 拆成相鄰兩個 span，接起來再比對
  const next = node.parentElement.nextElementSibling?.textContent || "";
  const txt = node.textContent + " " + next, off = pos.startOffset;
  for (const m of txt.matchAll(FIG_RE)) {
    if (m.index <= off && off <= m.index + m[0].length && m.index < node.textContent.length) {
      const kind = m[1].toLowerCase().startsWith("tab") ? "table" : "figure";
      return S.figures.find((f) => f.kind === kind && f.num === m[2]) || null;
    }
  }
  return null;
}

$("#pages").addEventListener("mousemove", (e) => {
  if (!S.figures.length || S.cropping || e.buttons) return;
  const now = Date.now();
  if (now - figMoveT < 80) return;  // 節流：caretRangeFromPoint 不便宜
  figMoveT = now;
  const fig = figureUnder(e.clientX, e.clientY);
  const key = fig && `${fig.kind}${fig.num}`;
  if (key && key === figKey) { clearTimeout(figHideT); return; }
  clearTimeout(figShowT);
  if (fig) {
    figShowT = setTimeout(() => showFigure(fig, e.clientX, e.clientY), 250);
  } else if (!figCard.hidden) {
    figHideT = setTimeout(hideFigure, 350);
  }
});
figCard.addEventListener("mouseenter", () => clearTimeout(figHideT));
figCard.addEventListener("mouseleave", () => { figHideT = setTimeout(hideFigure, 350); });
function hideFigure() { figCard.hidden = true; figKey = null; }

function showFigure(fig, x, y) {
  clearTimeout(figHideT);
  figKey = `${fig.kind}${fig.num}`;
  const src = `/api/papers/${S.paper.id}/figures/${fig.kind}/${fig.num}.png`;
  const label = fig.kind === "table" ? "表" : "圖";
  figCard.innerHTML = `<img src="${src}" alt="">
    <div class="small cap">${escapeHTML(fig.caption)}</div>
    <div class="acts"><button class="link small" data-k="go">跳到第 ${fig.page + 1} 頁 →</button>
    <button class="link small" data-k="ai">${icon("explain")}請 AI 解釋這張${label}</button></div>`;
  figCard.hidden = false;
  const w = 460;
  figCard.style.left = `${Math.max(8, Math.min(innerWidth - w - 8, x - w / 2))}px`;
  // 放在游標下方；太靠底就放上方
  const below = y + 20, h = Math.min(420, innerHeight * 0.6);
  figCard.style.top = `${below + h < innerHeight ? below : Math.max(8, y - h - 14)}px`;
  $('[data-k="go"]', figCard).onclick = () => { hideFigure(); goToPage(fig.page); };
  $('[data-k="ai"]', figCard).onclick = async () => {
    const anchor = figCard.getBoundingClientRect();
    hideFigure();
    const blob = await (await fetch(src)).blob();
    const image = await new Promise((r) => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(blob); });
    explainImage(image, fig.page, "", anchor, fig.bbox, `${label} ${fig.num}`);
  };
}

/* ---------------- 智慧引用：點 [12] 或 (Peters et al., 2018a) ---------------- */
$("#pages").addEventListener("click", async (e) => {
  if (S.cropping || !S.paper || getSelection().toString()) return;
  if (!e.target.closest(".textLayer")) return;
  const pos = caretAt(e.clientX, e.clientY);
  if (!pos) return;
  const node = pos.startContainer, txt = node.textContent || "", off = pos.startOffset;
  const base = `/api/papers/${S.paper.id}`;
  const at = { left: e.clientX, top: e.clientY, bottom: e.clientY + 8 };
  // 樣式一：[12] / [3, 5–7]
  const l = txt.lastIndexOf("[", off), r = txt.indexOf("]", off);
  const inner = l !== -1 && r !== -1 && r - l <= 30 ? txt.slice(l + 1, r) : "";
  if (/^[\d,\s–-]+$/.test(inner)) {
    const nums = [];
    for (const part of inner.split(",")) {
      const [a, b] = part.split(/[–-]/).map((s) => parseInt(s));
      if (b && b - a < 10) for (let k = a; k <= b; k++) nums.push(k); else if (a) nums.push(a);
    }
    return showCite(nums.map((n) => ({ label: `[${n}]`, url: `${base}/reference/${n}` })), at);
  }
  // 樣式二：(Peters et al., 2018a) / Devlin and Chang (2019)。引用常跨行，把前後 span 接起來找
  const prev = node.parentElement?.previousElementSibling?.textContent || "";
  const next = node.parentElement?.nextElementSibling?.textContent || "";
  const joined = `${prev} ${txt} ${next}`, pos2 = prev.length + 1 + off;
  const AY = /([A-Z][\p{L}'’-]+)(?:\s+et\s+al\.?|\s+(?:and|&)\s+[A-Z][\p{L}'’-]+)?,?\s*\(?((?:19|20)\d{2}[a-z]?)\b/gu;
  for (const m of joined.matchAll(AY)) {
    if (m.index <= pos2 && pos2 <= m.index + m[0].length) {
      return showCite([{ label: m[0].replace(/^\(|\s+/g, " ").trim(),
                         url: `${base}/reference-search?author=${encodeURIComponent(m[1])}&year=${m[2]}` }], at);
    }
  }
});

/** 由 Semantic Scholar 的資料拼一份 BibTeX（沒有查到就用原文當 note）。 */
function bibtex(r) {
  const p = r.paper;
  if (!p) return `@misc{ref${r.num},\n  note = {${r.raw}}\n}`;
  const first = (p.authors?.[0]?.name || "anon").split(" ").pop().toLowerCase();
  const word = (p.title.match(/[A-Za-z]{4,}/) || ["paper"])[0].toLowerCase();
  const f = [`title = {${p.title}}`, `author = {${(p.authors || []).map((a) => a.name).join(" and ")}}`,
             p.venue && `journal = {${p.venue}}`, p.year && `year = {${p.year}}`,
             p.externalIds?.DOI && `doi = {${p.externalIds.DOI}}`, p.externalIds?.ArXiv && `eprint = {${p.externalIds.ArXiv}}`];
  return `@article{${first}${p.year || ""}${word},\n  ${f.filter(Boolean).join(",\n  ")}\n}`;
}

/** items: [{label, url}]，每個 url 回傳 {num, raw, paper, note}。 */
async function showCite(items, at) {
  const c = $("#citeCard");
  c.hidden = false;
  placeFloating(c, at, 440);
  c.innerHTML = '<span class="muted small">查詢中…</span>';
  const parts = await Promise.all(items.slice(0, 5).map((it) => api(it.url).catch(() => null)));
  c.innerHTML = "";
  parts.forEach((r, k) => {
    const div = document.createElement("div");
    div.className = "cite";
    if (!r || !r.raw) {
      div.innerHTML = `<p class="muted small">${escapeHTML(items[k].label)} 找不到這筆參考文獻</p>`;
      return c.appendChild(div);
    }
    const p = r.paper, abs = p?.abstract || "";
    const ax = p?.externalIds?.ArXiv;
    const have = ax && library.some((x) => (x.filename || "").includes(ax));
    // 原文連結：DOI 優先（學校網路下通常能直接看全文），沒有 Semantic Scholar 資料時從參考文獻原文抓
    const doi = p?.externalIds?.DOI || (r.raw.match(/\b10\.\d{4,9}\/[^\s,;]+/) || [""])[0].replace(/[.)]+$/, "");
    const q = p?.title || r.raw.replace(/^\[\d+\]\s*/, "").slice(0, 160);
    const links = [doi && `<a href="${safeUrl(`https://doi.org/${doi}`)}" target="_blank" rel="noopener">原文（DOI）</a>`,
                   ax && `<a href="${safeUrl(`https://arxiv.org/abs/${ax}`)}" target="_blank" rel="noopener">arXiv</a>`,
                   `<a href="${safeUrl(`https://scholar.google.com/scholar?q=${encodeURIComponent(q)}`)}" target="_blank" rel="noopener">Google Scholar</a>`]
      .filter(Boolean).join("　");
    div.innerHTML = `<div class="tag small">${escapeHTML(items[k].label)}</div>
      ${p ? `<h4><a href="${safeUrl(p.url)}" target="_blank" rel="noopener">${escapeHTML(p.title)}</a></h4>
        <div class="small muted">${escapeHTML((p.authors || []).slice(0, 4).map((a) => a.name).join(", "))}${(p.authors || []).length > 4 ? ` +${p.authors.length - 4}` : ""}
        　${escapeHTML(p.venue || "")} ${p.year ?? ""}</div>
        ${abs ? `<p class="small abs">${escapeHTML(abs)}</p>${abs.length > 260 ? '<button class="link small" data-k="more">展開</button>' : ""}` : ""}`
        : `<div class="raw">${escapeHTML(r.raw)}</div>`}
      ${r.note ? `<div class="small warn">${escapeHTML(r.note)}</div>` : ""}
      <div class="small links">${links}</div>
      <div class="acts">
        <button class="chip" data-k="why">為何引用？</button>
        <button class="chip" data-k="bib">BibTeX</button>
        ${ax ? (have ? '<span class="small muted">✓ 已在論文庫</span>' : '<button class="chip" data-k="save">存到論文庫</button>') : ""}
        ${p ? `<span class="small muted cnt">${icon("quote")}${p.citationCount ?? "?"}</span>` : ""}
      </div>
      <div class="why"></div>`;
    div.addEventListener("click", async (e) => {
      const kk = e.target.closest("[data-k]")?.dataset.k;
      if (kk === "more") { $(".abs", div).classList.add("open"); e.target.remove(); }
      if (kk === "bib") { navigator.clipboard.writeText(bibtex(r)); e.target.textContent = "已複製"; }
      if (kk === "save") {
        e.target.disabled = true; e.target.textContent = "匯入中…";
        ingest(api("/api/papers/arxiv", { method: "POST", body: { url: ax } }));
      }
      if (kk === "why") {
        e.target.disabled = true;
        await streamInto($(".why", div), `/api/papers/${S.paper.id}/reference/${encodeURIComponent(r.num)}/why`, null, "GET");
      }
    });
    c.appendChild(div);
  });
}

/* ---------------- 框選圖表 / 公式：Ctrl/⌘（或 Shift）＋拖曳，或按「框選」 ---------------- */
let crop = null, cropDone = null;
function setCropping(on) {
  S.cropping = on;
  $("#viewer").classList.toggle("cropping", on);
  $("#btnCrop").classList.toggle("active", on);
}
function clearCrop() { cropDone?.box.remove(); cropDone = null; $("#cropBar").hidden = true; }
$("#btnCrop").onclick = () => setCropping(!S.cropping);
$("#pages").addEventListener("mousedown", (e) => {
  const pageEl = e.target.closest(".page");
  if (!pageEl || e.button !== 0 || !(S.cropping || e.shiftKey || e.ctrlKey || e.metaKey)) return;
  e.preventDefault();
  clearCrop();
  if (!S.cropping) setCropping(true);
  const pr = pageEl.getBoundingClientRect();
  const box = document.createElement("div");
  box.className = "cropBox";
  pageEl.appendChild(box);
  crop = { pageEl, pr, box, x0: e.clientX - pr.left, y0: e.clientY - pr.top };
});
document.addEventListener("mousemove", (e) => {
  if (!crop) return;
  const x = Math.max(0, Math.min(crop.pr.width, e.clientX - crop.pr.left));
  const y = Math.max(0, Math.min(crop.pr.height, e.clientY - crop.pr.top));
  Object.assign(crop.box.style, {
    left: `${Math.min(x, crop.x0)}px`, top: `${Math.min(y, crop.y0)}px`,
    width: `${Math.abs(x - crop.x0)}px`, height: `${Math.abs(y - crop.y0)}px`,
  });
  crop.x1 = x; crop.y1 = y;
});
document.addEventListener("mouseup", () => {
  if (!crop) return;
  const c = crop;
  crop = null;
  setCropping(false);
  selBar.hidden = true;
  getSelection().removeAllRanges();
  if (c.x1 == null || Math.abs(c.x1 - c.x0) < 12 || Math.abs(c.y1 - c.y0) < 12) { c.box.remove(); return; }
  // 框保留在頁面上，旁邊浮出工具列（Moonlight 的作法），不再跳 prompt 視窗
  cropDone = c;
  const r = c.box.getBoundingClientRect(), bar = $("#cropBar");
  bar.hidden = false;
  bar.style.left = `${Math.min(innerWidth - bar.offsetWidth - 8, Math.max(8, r.right - bar.offsetWidth))}px`;
  bar.style.top = `${r.bottom + 8 + 50 < innerHeight ? r.bottom + 8 : r.top - 52}px`;
  $("#cropAsk").focus();
});
$("#cropBar").addEventListener("click", (e) => {
  const act = e.target.closest("[data-act]")?.dataset.act;
  if (act === "close") clearCrop();
  if (act === "explain") explainCrop("");
});
$("#cropAsk").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.isComposing && e.target.value.trim()) { explainCrop(e.target.value.trim()); e.target.value = ""; }
});

function explainCrop(question) {
  if (!cropDone) return;
  const { pageEl, box, x0, y0, x1, y1, pr } = cropDone;
  const page = +pageEl.dataset.page;
  const canvas = S.pages[page].canvas;
  if (!canvas) return;
  // 頁面上的 CSS 像素 → canvas 實際像素（高 DPI 螢幕會差 2 倍）
  const k = canvas.width / pr.width;
  const sx = Math.min(x0, x1) * k, sy = Math.min(y0, y1) * k;
  const sw = Math.abs(x1 - x0) * k, sh = Math.abs(y1 - y0) * k;
  const out = document.createElement("canvas");
  const f = Math.min(1, 1280 / Math.max(sw, sh));  // 太大的圖縮小，省 token
  out.width = sw * f; out.height = sh * f;
  out.getContext("2d").drawImage(canvas, sx, sy, sw, sh, 0, 0, out.width, out.height);
  const rect = [Math.min(x0, x1) / pr.width, Math.min(y0, y1) / pr.height, Math.max(x0, x1) / pr.width, Math.max(y0, y1) / pr.height];
  const anchor = box.getBoundingClientRect();
  $("#cropBar").hidden = true;
  explainImage(out.toDataURL("image/png"), page, question, anchor, rect, "框選區域");
}

function explainImage(image, page, question, anchor, rect, label) {
  aiCard({
    title: question ? `問：${question}` : `解釋${label}`, anchor, question,
    quote: `<img class="qimg" src="${image}" alt="">`,
    url: `/api/papers/${S.paper.id}/explain-image`, body: { image, page, question },
    followup: imageFollowup(image, page),
    // color "image"：之後接續時知道要重新取框選區域的圖
    save: (thread) => addAnnotation({ page, rects: [rect], text: `［${label}］`, kind: "explain", color: "image", comment: thread }),
  });
}

const textFollowup = (text, page) => (q, history) =>
  ({ url: `/api/papers/${S.paper.id}/explain`, body: { text, page, question: q, history } });
const imageFollowup = (image, page) => (q, history) =>
  ({ url: `/api/papers/${S.paper.id}/explain-image`, body: { image, page, question: q, history } });

/** 從「解釋」分頁接續之前的對話；框選的會從 PDF 重新切出當時那塊區域的圖。 */
async function resumeExplain(a, anchor) {
  const short = a.text.length > 18 ? `${a.text.slice(0, 18)}…` : a.text;
  if (a.color === "image" || a.text.startsWith("［")) {  // 舊紀錄沒有 image 標記，用「［框選區域］」這類文字判斷
    const [x0, y0, x1, y1] = a.rects[0];
    const blob = await (await fetch(`/api/papers/${S.paper.id}/region.png?page=${a.page}&x0=${x0}&y0=${y0}&x1=${x1}&y1=${y1}`)).blob();
    const image = await new Promise((r) => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(blob); });
    return aiCard({ title: `接續：${short}`, anchor, quote: `<img class="qimg" src="${image}" alt="">`,
                    followup: imageFollowup(image, a.page), prior: a.comment, annId: a.id });
  }
  aiCard({ title: `接續：${short}`, anchor, quote: `<blockquote>${escapeHTML(a.text.slice(0, 220))}</blockquote>`,
           followup: textFollowup(a.text, a.page), prior: a.comment, annId: a.id });
}

/* ---------------- 保留版面翻譯：疊加 / 並排 ----------------
 * 只翻「畫面上已畫出來的頁」，一次一頁、目前這頁優先；翻過的頁後端有快取。 */
$("#trMode").addEventListener("click", (e) => {
  const b = e.target.closest("[data-mode]");
  if (!b || !S.paper) return;
  setTrMode(b.dataset.mode);
});

function setTrMode(mode) {
  S.trMode = mode;
  $$("#trMode button").forEach((x) => {
    x.classList.toggle("on", x.dataset.mode === mode);
    x.setAttribute("aria-pressed", x.dataset.mode === mode);
  });
  $("#pages").classList.toggle("tr-overlay", mode === "overlay");
  $("#pages").classList.toggle("tr-side", mode === "side");
  S.pages.forEach((_, i) => drawHighlights(i));  // 頁邊標籤的位置跟著並排與否換邊
  if (mode === "off") { S.trQueue = []; return; }
  if (mode === "side") {
    // 兩頁並排放不下就自動縮小到剛好塞滿閱讀區寬度
    const w = Math.max(...S.paper.page_sizes.map(([pw]) => pw)), room = $("#viewer").clientWidth - 48 - (wideView.matches ? 80 : 0);  // 80 = 左側標籤留白 --mgut
    if (w * S.scale * 2 + 14 > room) {
      const cur = S.current;
      S.scale = Math.max(0.5, +((room - 14) / (2 * w)).toFixed(2));
      buildPages();
      goToPage(cur);
      return;  // 新頁面畫出來時 renderPage 會自己補譯文頁
    }
  }
  queueTranslation(S.current, true);
  S.pages.forEach((pg, i) => {
    if (!pg.rendered) return;
    if (mode === "side") syncTwin(i);
    S.tr[i] ? drawTranslation(i) : queueTranslation(i);
  });
  goToPage(S.current);
}

/** 並排模式：把原文頁的畫面複製到譯文頁當底圖，圖表、公式原樣保留，文字段落再蓋上譯文。 */
function syncTwin(i) {
  const pg = S.pages[i];
  if (!pg?.canvas || $("canvas", pg.twin)) return;
  const c = document.createElement("canvas");
  c.width = pg.canvas.width; c.height = pg.canvas.height;
  c.style.width = pg.canvas.style.width; c.style.height = pg.canvas.style.height;
  c.getContext("2d").drawImage(pg.canvas, 0, 0);
  pg.twin.prepend(c);
}

function queueTranslation(i, first = false) {
  if (S.tr[i] || S.trQueue.includes(i)) return;
  first ? S.trQueue.unshift(i) : S.trQueue.push(i);
  pumpTranslation();
}

async function pumpTranslation() {
  if (S.trBusy || !S.trQueue.length || S.trMode === "off") return;
  S.trBusy = true;
  const page = S.trQueue.shift(), pid = S.paper.id;
  const blocks = [];
  try {
    await stream(`/api/papers/${pid}/translate-blocks`, { body: { page } }, (_full, piece) => {
      if (S.paper?.id !== pid) return;  // 翻到一半換了論文
      const ev = JSON.parse(piece);
      if (ev.blocks) { blocks.push(...ev.blocks); S.tr[page] = blocks; drawTranslation(page); }
      else if (ev.error) throw new Error(ev.error);
      else { blocks[ev.i].tr = ev.tr; drawTranslation(page, ev.i); }
    });
    if (S.paper?.id === pid && S.tr[page]) { blocks.done = true; drawTranslation(page); }
    // 翻譯前就畫好的螢光筆，現在補同步到譯文
    if (S.paper?.id === pid) S.annotations.filter((x) => x.page === page && (x.kind === "user" || AUTO[x.kind]) && !x.align).forEach(alignHighlight);
  } catch (e) {
    delete S.tr[page];
    const pg = S.pages[page];
    if (pg) for (const host of [pg.el, pg.twin]) {
      const layer = trLayer(host);
      layer.innerHTML = `<div class="trErr">第 ${page + 1} 頁翻譯失敗：${escapeHTML(e.message)}</div>`;
    }
  }
  S.trBusy = false;
  pumpTranslation();
}

function trLayer(host) {
  let layer = $(".trLayer", host);
  if (!layer) { layer = document.createElement("div"); layer.className = "trLayer"; host.appendChild(layer); }
  return layer;
}

/** 畫譯文：疊加層（原文頁上）和並排頁各畫一份。只給 idx 時只更新那一段（串流時用）。 */
function drawTranslation(page, idx) {
  const pg = S.pages[page], blocks = S.tr[page];
  if (!pg || !blocks) return;
  for (const host of [pg.el, pg.twin]) {
    const layer = trLayer(host);
    const list = idx == null ? blocks.map((b, i) => [b, i]) : [[blocks[idx], idx]];
    if (idx == null) layer.innerHTML = "";
    for (const [b, i] of list) {
      if (blocks.done && !b.tr) continue;  // 翻完了還沒譯文的是公式、頁碼這類刻意不翻的區塊：顯示原文
      let d = $(`.trb[data-i="${i}"]`, layer);
      if (!d) {
        d = document.createElement("div");
        d.className = "trb";
        d.dataset.i = i;
        const [x0, y0, x1, y1] = b.bbox;
        Object.assign(d.style, { left: `${x0 * 100}%`, top: `${y0 * 100}%`,
                                 width: `${(x1 - x0) * 100}%`, height: `${(y1 - y0) * 100}%` });
        d.title = b.text;  // 滑鼠停著可看原文
        layer.appendChild(d);
      }
      if (b.tr) { d.textContent = b.tr; d.classList.add("done"); fitText(d, b.size); }
    }
  }
  markTranslation(page);
}

/** 譯文裡標出螢光筆的對應段落（疊加層、並排頁都畫）。zh 是空的或在譯文裡找不到，就淡淡地標整段。 */
function markTranslation(i) {
  const pg = S.pages[i], blocks = S.tr[i];
  if (!pg || !blocks) return;
  const anns = S.annotations.filter((a) => a.page === i && a.align && visibleOnPage(a));
  if (litAlign?.page === i) anns.push({ id: "lit", align: litAlign, lit: true });
  for (const d of [pg.el, pg.twin].flatMap((host) => $$(".trb.done", host))) {
    const tr = blocks[d.dataset.i].tr, marks = [];
    for (const a of anns.filter((a) => a.align.block === +d.dataset.i)) {
      const at = a.align.zh ? tr.indexOf(a.align.zh) : -1;
      marks.push(at < 0 ? [0, tr.length, a, "weak"] : [at, at + a.align.zh.length, a, ""]);
    }
    if (!marks.length && !d.children.length) continue;
    d.textContent = "";
    let pos = 0;
    for (const [s, e, a, weak] of marks.sort((x, y) => x[0] - y[0] || (y[2].lit ? 1 : 0) - (x[2].lit ? 1 : 0))) {
      if (s < pos) continue;  // shortcut: 重疊的對應段只畫先開始的那段；要疊色再拆成小段
      const m = document.createElement("mark");
      m.className = `trm ${weak}${a.lit ? " lit" : ""}`;
      m.dataset.id = a.id;
      // 自動標註用類別色（新穎／方法／結果），螢光筆用使用者選的顏色，選取對應用燈光色
      m.style.setProperty("--c", a.lit ? "var(--lamp-fill)" : AUTO[a.kind] ? `var(--${a.kind.slice(5)}-bg)`
        : isHex(a.color) ? tint(a.color, 0.34) : `var(--hl-${a.color})`);
      m.textContent = tr.slice(s, e);
      d.append(tr.slice(pos, s), m);
      pos = e;
    }
    d.append(tr.slice(pos));
  }
}

/** 從原文字級開始，縮小到譯文塞得進原文的框。size 是 PDF 的 pt，乘上縮放倍率就是畫面 px。 */
function fitText(el, size = 10) {
  if (!el.offsetParent) return;  // 隱藏中的層量不到高度，等顯示時重畫
  let fs = Math.max(7, size * S.scale);
  el.style.fontSize = `${fs}px`;
  while (el.scrollHeight > el.clientHeight + 1 && fs > 6) { fs -= 0.5; el.style.fontSize = `${fs}px`; }
}

/* ---------------- 自動標註 ---------------- */
$("#btnHighlight").onclick = async () => {
  if (!S.paper) return;
  const btn = $("#btnHighlight");
  const refresh = S.annotations.some((a) => a.kind.startsWith("auto:"))
    && confirm("已經有自動標註了，要重新產生嗎？（取消 = 只顯示現有的）");
  btn.disabled = true;
  btn.lastChild.textContent = "標註中…";
  const stop = pushLater((w) => btn.after(w));
  try {
    const auto = await api(`/api/papers/${S.paper.id}/auto-highlight${refresh ? "?refresh=true" : ""}`, { method: "POST" });
    S.annotations = S.annotations.filter((a) => !a.kind.startsWith("auto:")).concat(auto);
    auto.forEach(alignHighlight);  // 已翻好的頁馬上同步到譯文；沒翻的頁等翻完時補
    S.filter.auto = true;
    $("#showAuto").checked = true;
    S.pages.forEach((_, i) => drawHighlights(i));
    renderActivity();
    openPanel("notes");
  } catch (e) {
    alert(`自動標註失敗：${e.message}`);
  }
  stop();
  btn.disabled = false;
  btn.lastChild.textContent = "自動畫重點";
};

/* ---------------- 活動面板 ---------------- */
function openPanel(name) {
  $("main").classList.remove("nopanel");
  $$(".tabs button[data-tab]").forEach((b) => {
    b.classList.toggle("on", b.dataset.tab === name);
    b.setAttribute("aria-selected", b.dataset.tab === name);
  });
  $$(".tab").forEach((t) => t.classList.toggle("on", t.id === `tab-${name}`));
}
$$(".tabs button[data-tab]").forEach((b) => (b.onclick = () => openPanel(b.dataset.tab)));

function flashItem(id) {
  setTimeout(() => {
    const li = $(`.notes li[data-id="${id}"]`);
    if (li) { li.scrollIntoView({ block: "center" }); li.classList.add("flash"); setTimeout(() => li.classList.remove("flash"), 1600); }
  }, 50);
}

function renderInfo() {
  const p = S.paper;
  $("#paperInfo").innerHTML = `<h3>${escapeHTML(p.title)}</h3>
    <div class="small muted">${p.num_pages} 頁　${p.references} 筆參考文獻　${escapeHTML(p.filename)}</div>
    ${p.abstract ? `<details open><summary class="small">摘要（原文）</summary><p class="small">${escapeHTML(p.abstract)}</p></details>` : ""}`;
}

function renderActivity() { renderNotes(); renderExplains(); renderComments(); drawRail(); }

// 標註分頁的篩選器
$("#colorFilter").innerHTML = [...COLORS, "custom"].map((c) =>
  `<button class="sw ${c} on" data-color="${c}" title="${c === "custom" ? "自訂色" : c}"></button>`).join("");
$("#autoFilter").innerHTML = Object.entries(AUTO).map(([k, v]) =>
  `<label class="mtag ${k.slice(5)}"><input type="checkbox" data-auto="${k}" checked>${v}</label>`).join("");
$("#colorFilter").onclick = (e) => {
  const c = e.target.dataset.color;
  if (!c) return;
  S.filter.colors.has(c) ? S.filter.colors.delete(c) : S.filter.colors.add(c);
  e.target.classList.toggle("on", S.filter.colors.has(c));
  refreshHighlights();
};
$("#autoFilter").onchange = (e) => {
  const k = e.target.dataset.auto;
  e.target.checked ? S.filter.autoKinds.add(k) : S.filter.autoKinds.delete(k);
  refreshHighlights();
};
$("#showAuto").onchange = (e) => { S.filter.auto = e.target.checked; refreshHighlights(); };
$("#showLabels").onchange = (e) => { S.filter.labels = e.target.checked; refreshHighlights(); };
$("#noteSearch").oninput = (e) => { S.filter.q = e.target.value.trim().toLowerCase(); renderNotes(); };
function refreshHighlights() { S.pages.forEach((_, i) => drawHighlights(i)); renderNotes(); }

function noteItem(a, inner) {
  const li = document.createElement("li");
  li.dataset.id = a.id;
  li.className = a.kind === "user" ? colorKey(a.color) : a.kind.replace("auto:", "auto ");
  if (a.kind === "user" && isHex(a.color)) li.style.borderLeftColor = a.color;
  li.innerHTML = `<div class="meta"><span>p.${a.page + 1}</span><span>${fmtDate(a.created)}</span>
      <button class="link small quote" data-k="quote" title="把這則引用到「筆記」分頁">引用</button>
      <button class="link small del" data-k="del">刪除</button></div>${inner}`;
  li.addEventListener("click", (e) => {
    if (e.target.dataset.k === "del") return deleteAnnotation(a);
    if (e.target.dataset.k === "quote") return quoteToNote(a.text, a.page, a);
    if (!/TEXTAREA|SUMMARY|A/.test(e.target.tagName)) goToPage(a.page, a.id);
  });
  return li;
}

function renderNotes() {
  const ul = $("#notesList");
  const q = S.filter.q;
  const items = S.annotations.filter((a) => (a.kind === "user" || AUTO[a.kind]) && visibleOnPage(a)
    && (!q || `${a.text} ${a.comment}`.toLowerCase().includes(q)));
  ul.innerHTML = items.length ? "" : '<li class="muted small empty">還沒有標註。選取文字按「畫重點」（H），或按頂列的「自動畫重點」。</li>';
  for (const a of items) {
    const tag = AUTO[a.kind] ? `<span class="mtag ${a.kind.slice(5)}">${AUTO[a.kind]}</span>` : "";
    const li = noteItem(a, `${tag}<div class="txt">${escapeHTML(a.text)}</div>
      <textarea rows="1" placeholder="加備註…">${escapeHTML(a.comment || "")}</textarea>`);
    $("textarea", li).onchange = (e) => {
      a.comment = e.target.value;
      api(`/api/annotations/${a.id}`, { method: "PATCH", body: { comment: a.comment } });
    };
    ul.appendChild(li);
  }
}

function renderExplains() {
  const ul = $("#explainList");
  const items = S.annotations.filter((a) => a.kind === "explain").sort((a, b) => b.created - a.created);
  ul.innerHTML = items.length ? "" : '<li class="muted small empty">選字後按「解釋」（E）或「問 AI」，結果會記在這裡。</li>';
  for (const a of items) {
    const turns = ((a.comment || "").match(/\n---\n/g) || []).length + 1;
    const li = noteItem(a, `<blockquote>${escapeHTML(a.text.slice(0, 160))}</blockquote>
      <details><summary class="small">看解釋${turns > 1 ? `（${turns} 段對話）` : ""}</summary><div class="ans"></div></details>
      <button class="link small resume" data-k="resume">${icon("chat")}繼續對話</button>`);
    renderMD($(".ans", li), a.comment || "");
    $(".resume", li).addEventListener("click", (e) => {
      e.stopPropagation();  // 不要觸發整列的「跳到那一頁」
      const r = li.getBoundingClientRect();
      resumeExplain(a, { left: r.left - 472, top: r.top, bottom: r.top });
    });
    ul.appendChild(li);
  }
}

function renderComments() {
  const ul = $("#commentList");
  const items = S.annotations.filter((a) => a.kind === "comment").sort((a, b) => b.created - a.created);
  ul.innerHTML = items.length ? "" : '<li class="muted small empty">選取文字後按「寫註解」（C），或按右鍵 →「寫註解」。</li>';
  for (const a of items) {
    const li = noteItem(a, `<blockquote>${escapeHTML(a.text.slice(0, 160))}</blockquote>
      <textarea rows="2">${escapeHTML(a.comment)}</textarea>`);
    $("textarea", li).onchange = (e) => {
      a.comment = e.target.value;
      api(`/api/annotations/${a.id}`, { method: "PATCH", body: { comment: a.comment } });
      drawHighlights(a.page);
    };
    ul.appendChild(li);
  }
}

function renderRefs() {
  const ul = $("#refList"), q = $("#refSearch").value.trim().toLowerCase();
  const items = S.refs.filter((r) => !q || r.raw.toLowerCase().includes(q));
  ul.innerHTML = items.length ? "" : '<li class="muted small empty">這份 PDF 沒有解析出參考文獻。</li>';
  for (const r of items) {
    const li = document.createElement("li");
    li.innerHTML = `<span class="rnum">${escapeHTML(r.num)}</span><span class="small">${escapeHTML(r.raw)}</span>`;
    li.onclick = () => {
      const b = li.getBoundingClientRect();
      showCite([{ label: `[${r.num}]`, url: `/api/papers/${S.paper.id}/reference/${encodeURIComponent(r.num)}` }],
               { left: b.left - 450, top: b.top, bottom: b.top });
    };
    ul.appendChild(li);
  }
}
$("#refSearch").oninput = renderRefs;

/* ---------------- 筆記分頁（docs/notes-design.md）----------------
 * 每篇一份 Markdown，原生 textarea（中文輸入法最穩）＋ renderWiki 預覽。
 * 自動儲存：停手 1 秒、失焦、切走分頁時存；組字中不存。PUT 帶 base_updated，別的分頁先存過會回 409，不覆蓋。
 * 還沒存進伺服器的內容隨時備份在 localStorage（lantern.note.<pid>），存成功才清掉。 */
const nbText = $("#nbText");
const NB = { pid: null, updated: null, saved: "", timer: 0, busy: false, again: false, conflict: null, composing: false };
const nbKey = (pid) => `lantern.note.${pid}`;
const nbStatus = (t, cls = "") => { $("#nbStatus").textContent = t; $("#nbStatus").className = `nbstatus small ${cls || "muted"}`; };

/** 筆記頂端的提示列（衝突、還原草稿）：文字 + 幾個動作按鈕；不給 actions 就收起來。 */
function nbMsg(text, actions = []) {
  const m = $("#nbMsg");
  m.hidden = !text;
  m.innerHTML = text ? `<span>${escapeHTML(text)}</span>` : "";
  for (const [label, fn] of actions) {
    const b = document.createElement("button");
    b.className = "small";
    b.textContent = label;
    b.onclick = () => { nbMsg(""); fn(); };
    m.append(b);
  }
}

async function loadNote(pid) {
  if (NB.pid && NB.pid !== pid) saveNote();  // 換篇前把上一篇沒存的送出去（saveNote 先記下 pid 與內容）
  clearTimeout(NB.timer);
  Object.assign(NB, { pid, updated: null, saved: "", conflict: null });
  nbText.value = "";
  nbText.readOnly = true;  // 讀到伺服器那份之前不能打字，免得被蓋掉
  nbMsg(""); nbStatus("");
  $("#nbDraftBox").hidden = true;
  const cardNote = S.paper?.note;
  $("#nbCardNote").hidden = !cardNote;
  $("#nbCardNote").textContent = cardNote ? `論文卡備註：${cardNote}` : "";
  let n;
  try {
    n = await api(`/api/papers/${pid}/note`);
  } catch (e) {
    if (NB.pid === pid) nbStatus(`讀不到筆記：${e.message}`, "err");
    return;
  }
  if (NB.pid !== pid) return;
  Object.assign(NB, { updated: n.updated, saved: n.markdown });
  nbText.value = n.markdown;
  nbText.readOnly = false;
  if ($("#nbMode .on").dataset.m === "preview") renderWiki($("#nbPreview"), n.markdown);
  if (n.updated) nbStatus(`上次儲存 ${fmtDate(n.updated)}`);
  const local = store.get(nbKey(pid), null);
  if (local == null || local === n.markdown) return store.del(nbKey(pid));
  nbMsg("這台電腦上有一份還沒存進伺服器的筆記內容（可能上次存檔失敗或分頁被關掉）。", [
    ["還原那份", () => { nbText.value = local; noteChanged(); }],
    ["不用了", () => store.del(nbKey(pid))],
  ]);
}

/** 內容變了：先備份到 localStorage，停手 1 秒後存。組字中（注音、倉頡選字）什麼都不做，等 compositionend。 */
function noteChanged() {
  if (NB.composing || !NB.pid) return;
  store.set(nbKey(NB.pid), nbText.value);
  clearTimeout(NB.timer);
  NB.timer = setTimeout(saveNote, 1000);
  if (!NB.conflict) nbStatus("尚未儲存…");
}
nbText.addEventListener("input", (e) => { if (!e.isComposing) noteChanged(); });
nbText.addEventListener("compositionstart", () => { NB.composing = true; clearTimeout(NB.timer); });
nbText.addEventListener("compositionend", () => { NB.composing = false; noteChanged(); });
nbText.addEventListener("blur", () => { if (!NB.composing) saveNote(); });
document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") saveNote(); });

async function saveNote() {
  clearTimeout(NB.timer);
  const pid = NB.pid, md = nbText.value;
  if (!pid || nbText.readOnly || md === NB.saved || NB.conflict) return;
  if (NB.busy) { NB.again = true; return; }  // 一次只送一個，不然第二個會拿舊的 updated 撞 409
  NB.busy = true;
  nbStatus("儲存中…");
  try {
    const r = await reach(`/api/papers/${pid}/note`, { method: "PUT", headers: { "Content-Type": "application/json" },
                                                      body: JSON.stringify({ markdown: md, base_updated: NB.updated }) });
    const out = await r.json().catch(() => ({}));
    if (r.status === 401) showLogin(true);
    if (NB.pid !== pid) {  // 送出後已換篇：只收尾備份
      if (r.ok) store.del(nbKey(pid));
    } else if (r.status === 409) {
      noteConflict(out);
    } else if (!r.ok) {
      throw new Error(r.status === 422 ? "筆記太長（上限約一百萬字）" : out.detail || r.statusText);
    } else {
      Object.assign(NB, { updated: out.updated, saved: md });
      if (nbText.value === md) store.del(nbKey(pid));
      nbStatus(`已儲存 ${new Date(out.updated * 1000).toLocaleTimeString("zh-TW", { hour: "2-digit", minute: "2-digit" })}`);
    }
  } catch (e) {
    if (NB.pid === pid) nbStatus(`沒存進去（${e.message}）。內容已留在這台電腦上，繼續編輯或離開欄位時會再試。`, "err");
  } finally {
    NB.busy = false;
    if (NB.again) { NB.again = false; saveNote(); }
  }
}

/** 409：伺服器上的版本比這裡新（另一個分頁或裝置改過）。不自動覆蓋任何一邊，讓使用者選。 */
function noteConflict(server) {
  NB.conflict = server;
  nbStatus("暫停自動儲存：有另一份比較新的版本", "warn");
  nbMsg("另一個分頁（或裝置）改過這份筆記。你這邊的內容還在編輯框裡，沒有被蓋掉。", [
    ["用我這份", () => { NB.updated = server.updated; NB.conflict = null; saveNote(); }],
    ["改用另一份（我這份先複製）", async () => {
      await navigator.clipboard.writeText(nbText.value).then(() => toast("<span>你原本那份已複製到剪貼簿</span>"),
        () => toast('<span class="err">複製失敗；你原本那份仍備份在這台電腦上</span>'));
      Object.assign(NB, { updated: server.updated, saved: server.markdown, conflict: null });
      nbText.value = server.markdown;
      if ($("#nbMode .on").dataset.m === "preview") renderWiki($("#nbPreview"), server.markdown);
      nbStatus(`已載入較新的版本 ${fmtDate(server.updated)}`);
    }],
  ]);
}

function setNbMode(m) {
  $$("#nbMode button").forEach((b) => { b.classList.toggle("on", b.dataset.m === m); b.setAttribute("aria-pressed", b.dataset.m === m); });
  nbText.hidden = m === "preview";
  $("#nbPreview").hidden = m !== "preview";
  if (m === "preview") {
    renderWiki($("#nbPreview"), nbText.value || "*（還沒寫任何東西）*");
    saveNote();
  }
}
$("#nbMode").onclick = (e) => { const b = e.target.closest("button[data-m]"); if (b) setNbMode(b.dataset.m); };

// 預覽裡的引用：同一篇直接跳頁並閃標註；別篇先開那篇
$("#nbPreview").onclick = (e) => {
  if (e.target.closest("a.wref")) return e.preventDefault();  // [[slug]] 是 Wiki 頁，閱讀頁裡沒有對應，只顯示
  const c = e.target.closest(".wcite");
  if (c) openAt(c.dataset.pid, +c.dataset.page, c.dataset.aid)
    .catch((err) => toast(`<span class="err">開不了這篇論文：${escapeHTML(err.message)}（可能已經被刪除）</span>`));
};

/** 在游標處插入一段 Markdown（前後補空行），切到編輯並觸發自動儲存。 */
function insertIntoNote(md) {
  if (nbText.readOnly) return toast("<span>筆記還在載入，稍等一下再試</span>");
  openPanel("notebook");
  setNbMode("edit");
  const s = nbText.selectionStart, pre = nbText.value.slice(0, s);
  const lead = !pre || pre.endsWith("\n\n") ? "" : pre.endsWith("\n") ? "\n" : "\n\n";
  nbText.focus();
  nbText.setRangeText(`${lead}${md.trim()}\n\n`, s, nbText.selectionEnd, "end");
  noteChanged();
}

/** 引用到筆記：原文做成引用區塊 + 回連標記；從標註來的帶 @aid（點了會閃那則標註），選字來的只到頁。 */
function quoteToNote(text, page, a = null) {
  if (!S.paper) return;
  const link = `[[paper:${S.paper.id}#p${page + 1}${a ? `@${a.id}` : ""}]]`;
  let md = `> ${String(text).replace(/\s+/g, " ").trim()}\n> ${link}`;
  if (a && a.kind !== "explain" && a.comment?.trim()) md += `\n\n${a.comment.trim()}`;  // 使用者的備註接在下面
  insertIntoNote(md);
}

// AI 擬初稿：串到草稿框，按「插入」才放進筆記（不邊串邊改 textarea，免得打亂游標與組字）
$("#nbDraft").onclick = async () => {
  if (!S.paper) return;
  const btn = $("#nbDraft"), out = $("#nbDraftOut"), pid = S.paper.id;
  $("#nbDraftBox").hidden = false;
  $("#nbInsert").disabled = true;
  btn.disabled = true;
  out.innerHTML = "";
  const stop = pushLater((w) => out.append(w), 32, "擬稿中…");
  try {
    NB.draft = await stream(`/api/papers/${pid}/note/draft`, {}, (t) => { stop(); renderWiki(out, t); });
    if (S.paper?.id === pid) { renderWiki(out, NB.draft); $("#nbInsert").disabled = !NB.draft; }
  } catch (e) {
    out.innerHTML = `<span class="err">擬稿失敗：${escapeHTML(e.message)}</span>`;
  } finally {
    stop();
    btn.disabled = false;
  }
};
$("#nbInsert").onclick = () => { insertIntoNote(NB.draft || ""); $("#nbDraftBox").hidden = true; };
$("#nbDraftClose").onclick = () => { $("#nbDraftBox").hidden = true; };

/** 匯出 .md（Obsidian 友善）：YAML frontmatter + 引用標記換成可點回 Lantern 的網址 #<pid>/p<n>/<aid>。 */
$("#nbExport").onclick = async () => {
  if (!S.paper) return;
  const p = S.paper, base = location.origin + location.pathname;
  const bib = await api(`/api/papers/${p.id}/cite`).then((r) => r.bib || {}, () => ({}));  // 書目拿不到就略過作者年份
  const body = nbText.value.replace(/\[\[paper:([^#\s\]]+)#p(\d+)(?:@(\w+))?(?:\|[^\]]*)?\]\]/g,
    (_, pid, n, aid) => `[p.${n}](${base}#${pid}/p${n}${aid ? `/${aid}` : ""})`);
  const q = (s) => JSON.stringify(String(s));  // JSON 字串也是合法的 YAML 雙引號字串
  const authors = (bib.authors || []).map((a) => [a.given, a.family].filter(Boolean).join(" ")).filter(Boolean);
  const fm = [`title: ${q(p.title || p.filename)}`,
    authors.length ? `authors:\n${authors.map((a) => `  - ${q(a)}`).join("\n")}` : "",
    bib.year ? `year: ${q(bib.year)}` : "", bib.doi ? `doi: ${q(bib.doi)}` : "",
    `source: ${q(`${base}#${p.id}`)}`, `exported: ${q(new Date().toISOString().slice(0, 10))}`].filter(Boolean).join("\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([`---\n${fm}\n---\n\n${body}\n`], { type: "text/markdown;charset=utf-8" }));
  a.download = `${(p.title || p.filename).replace(/[\\/:*?"<>|]+/g, " ").slice(0, 80).trim() || "note"}.md`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
};

// 列印／存成 PDF：只印渲染好的筆記（style.css 的 body.printnote）
$("#nbPrint").onclick = () => {
  const area = $("#nbPrintArea");
  renderWiki(area, `# ${S.paper?.title || ""}\n\n${nbText.value}`);
  document.body.classList.add("printnote");
  addEventListener("afterprint", () => document.body.classList.remove("printnote"), { once: true });
  print();
};

/* ---------------- 摘要 ---------------- */
async function runSummary(refresh) {
  const btn = $("#btnSummary");
  if (!S.paper || btn.disabled) return;
  btn.disabled = true;
  btn.textContent = "產生中…";
  const stop = pushLater((w) => btn.parentElement.prepend(w));
  await streamInto($("#summaryOut"), `/api/papers/${S.paper.id}/summary${refresh ? "?refresh=true" : ""}`, null, "GET");
  stop();
  btn.disabled = false;
  btn.textContent = "產生摘要";
}
$("#btnSummary").onclick = () => runSummary(false);
$("#btnSummaryRe").onclick = () => runSummary(true);

/* Wiki 分頁：這篇的論文頁（slug = paper-<id>）置頂，其他提到這篇的頁面收成「還有 N 頁提到這篇」 */
async function loadPaperWiki(pid) {
  const box = $("#paperWiki");
  box.innerHTML = '<p class="muted small">讀取中…</p>';
  const links = await api(`/api/papers/${pid}/wiki`).catch(() => []);
  if (S.paper?.id !== pid) return;
  const item = (l) => `<li><button class="wbitem" data-ws="${escapeHTML(l.workspace_id)}" data-slug="${escapeHTML(l.slug)}">
    ${escapeHTML(l.title)}<span class="small muted">${escapeHTML(l.workspace_name)}</span></button></li>`;
  const own = links.filter((l) => l.slug === `paper-${pid}`), rest = links.filter((l) => l.slug !== `paper-${pid}`);
  box.innerHTML = !links.length
    ? '<p class="muted">這篇還沒整理進任何研究主題的 Wiki。到研究主題的 Wiki 分頁按「更新 Wiki」，它的論文頁就會出現在這裡。</p>'
    : `${own.length ? `<section class="psec"><h3>這篇的論文頁</h3><ul class="wblist">${own.map(item).join("")}</ul></section>` : ""}
      ${rest.length ? `<details class="psec wmore"${own.length ? "" : " open"}><summary>還有 ${rest.length} 頁提到這篇</summary>
        <ul class="wblist">${rest.map(item).join("")}</ul></details>` : ""}`;
}
$("#paperWiki").onclick = async (e) => {
  const b = e.target.closest("button[data-ws]");
  if (!b) return;
  const ws = (await api("/api/workspaces")).find((w) => w.id === b.dataset.ws);
  if (!ws) return;
  await showWs(ws);
  openWikiPage(b.dataset.slug);
};

/* ---------------- 相關論文推薦 ---------------- */
async function loadRelated(url) {
  const ul = $("#relatedList");
  ul.innerHTML = '<li class="muted small">查詢中…</li>';
  let recs;
  try { recs = await api(url); }
  catch (e) { ul.innerHTML = `<li class="err small">${escapeHTML(e.message)}</li>`; return; }
  ul.innerHTML = recs.length ? "" : '<li class="muted small">沒有推薦結果</li>';
  for (const r of recs) {
    const ax = r.externalIds?.ArXiv;
    const li = document.createElement("li");
    const abs = r.abstract || "";
    li.innerHTML = `<a href="${safeUrl(r.url)}" target="_blank" rel="noopener">${escapeHTML(r.title)}</a>
      <div class="small muted">${escapeHTML((r.authors || []).slice(0, 3).map((a) => a.name).join(", "))}${(r.authors || []).length > 3 ? " 等" : ""}
        　${r.year ?? ""}${r.venue ? "　" + escapeHTML(r.venue) : ""}　被引用 ${r.citationCount ?? "?"} 次</div>
      ${abs ? `<details class="small"><summary>摘要</summary>${escapeHTML(abs)}</details>` : ""}
      <div class="acts">${r.in_library ? '<span class="small muted">✓ 已在論文庫</span>'
        : ax ? `<button class="link small" data-ax="${escapeHTML(ax)}">匯入 arXiv:${escapeHTML(ax)}</button>` : ""}</div>`;
    const btn = $("[data-ax]", li);
    if (btn) btn.onclick = () => { btn.disabled = true; btn.textContent = "匯入中…";
      ingest(api("/api/papers/arxiv", { method: "POST", body: { url: ax } })); };
    ul.appendChild(li);
  }
}
$("#btnRelated").onclick = () => S.paper && loadRelated(`/api/papers/${S.paper.id}/related`);
$("#btnRecLib").onclick = () => loadRelated("/api/recommendations");

/* ---------------- 問這篇論文（「讀懂」分頁底部的聊天） ---------------- */
async function loadChat() {
  if (!S.paper) { $("#chatOut").innerHTML = '<p class="muted">先開啟一篇論文。</p>'; return; }
  const out = $("#chatOut"), pid = S.paper.id;
  out.innerHTML = "";
  const msgs = await api(`/api/papers/${pid}/chat`).catch(() => []);
  if (S.paper?.id !== pid) return;  // 等的時候換了論文
  for (const m of msgs) addMsg(m.role, m.content, false);
  if (!msgs.length) {
    out.innerHTML = '<div class="suggest"><p class="muted small">可以這樣問：</p></div>';
    const qs = await api(`/api/papers/${pid}/suggestions`).catch(() => []);
    const list = qs.length ? qs : ["這篇的主要貢獻是什麼？", "方法的核心步驟有哪些？", "實驗結果說明了什麼？"];
    if (S.paper?.id !== pid) return;
    for (const q of list) {
      const b = document.createElement("button");
      b.className = "chip";
      b.textContent = q;
      b.onclick = () => sendChat(q);
      $(".suggest", out)?.appendChild(b);
    }
  }
}

// scroll = false：開論文時載入舊對話，分頁要停在最上面的摘要，不要捲到底
function addMsg(role, text, scroll = true) {
  const d = document.createElement("div");
  d.className = `msg ${role}`;
  if (role === "user") d.textContent = text; else { renderMD(d, text); addCopy(d, text); }
  $("#chatOut").appendChild(d);
  if (scroll) d.scrollIntoView({ block: "end" });
  return d;
}
function addCopy(d, text) {
  const b = document.createElement("button");
  b.className = "icon mcopy";
  b.title = "複製";
  b.innerHTML = icon("copy");
  b.onclick = () => navigator.clipboard.writeText(text);
  d.appendChild(b);
}

async function sendChat(q) {
  if (!q || !S.paper || S.chatBusy) return;
  S.chatBusy = true;
  $(".suggest", $("#chatOut"))?.remove();
  addMsg("user", q);
  const d = addMsg("assistant", "");
  const full = await streamInto(d, `/api/papers/${S.paper.id}/chat`, { question: q, page: S.current }, "POST", 32);
  if (full) addCopy(d, full);
  d.scrollIntoView({ block: "end" });
  S.chatBusy = false;
}
$("#chatForm").onsubmit = (e) => {
  e.preventDefault();
  const q = $("#chatInput").value.trim();
  $("#chatInput").value = "";
  sendChat(q);
};
$("#chatInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); $("#chatForm").requestSubmit(); }
});
// 不用 confirm()：第一下只是「上膛」，三秒內再按一次才真的清除
$("#chatClear").onclick = async (e) => {
  const b = e.currentTarget;
  if (!S.paper) return;
  if (!b.dataset.armed) {
    b.dataset.armed = "1";
    b.textContent = "再按一次清除";
    setTimeout(() => { delete b.dataset.armed; b.textContent = "清除對話"; }, 3000);
    return;
  }
  await api(`/api/papers/${S.paper.id}/chat`, { method: "DELETE" });
  delete b.dataset.armed; b.textContent = "清除對話";
  loadChat();
};

/* ---------------- 畫面切換：登入 / 首頁 / workspace / 閱讀 ---------------- */
// CSS 依 body[data-view] 決定顯示哪一頁（閱讀頁的工具列、側欄等在其他頁都收起來）
const setView = (v) => { document.body.dataset.view = v; };
let workspaces = [], curWs = null;  // curWs = 目前的 workspace；null = 全部論文

/* 登入頁的短句：每 10 秒淡入換一句；第三欄是只在這幾點出現（當地時間，可跨午夜） */
const SAYINGS = [
  ["燈亮著，就還能再讀一頁。"], ["夜很長，論文也是；燈先替你點好了。"], ["把一頁讀懂，比翻過十頁有用。"], ["字太小的地方，燈會幫你照近一點。"],
  ["石頭又滾下來了，那就再推一次。"], ["今天也推到山頂一次就好。"], ["讀不完的論文，就是那顆石頭；但山頂的風景是真的。"],
  ["Related work 不會自己寫，但我們可以先讀。"], ["先讀摘要，不丟臉。"], ["你下載的論文，總有一天會讀到。"], ["Reviewer 2 不在這裡，放心讀。"],
  ["鍥而不舍，金石可鏤。", "《荀子》"], ["業精於勤，荒於嬉。", "韓愈"], ["學而不思則罔，思而不學則殆。", "《論語》"],
  ["讀累了就休息，論文不會跑掉。"], ["卡住的地方先標起來，明天再看會比較清楚。"], ["今天讀得少也沒關係，有讀就好。"],
  ["慢慢來，理解比速度重要。"], ["你不是一個人在讀，燈陪著你。"],
  ["喝口水吧，論文不會因為你脫水而變短。"], ["眼睛說它想看看遠方，不是下一篇 PDF。"], ["椅子也累了，起來走兩步再回來。"],
  ["咖啡是燃料，不是正餐。"], ["讀不懂不一定是你的問題，有些作者自己也沒想清楚。"], ["第三杯咖啡了？燈都替你擔心。"],
  ["已經很晚了，這一頁讀完就去睡吧；Reviewer 2 也睡了。", "", [23, 5]],
  ["早安，先從一篇摘要開始吧；咖啡可以邊讀邊喝。", "", [5, 10]],
];
let sayTimer = 0, sayLast = "";
function nextSaying() {
  if (document.body.dataset.view !== "login") { clearInterval(sayTimer); sayTimer = 0; return; }
  const h = new Date().getHours();
  const pool = SAYINGS.filter(([t, , w]) => t !== sayLast && (!w || (w[0] < w[1] ? h >= w[0] && h < w[1] : h >= w[0] || h < w[1])));
  const [text, who] = pool[Math.floor(Math.random() * pool.length)];
  sayLast = text;
  const el = $("#loginSay");
  const set = () => {
    el.textContent = text;
    if (who) el.insertAdjacentHTML("beforeend", `<small>${escapeHTML(who)}</small>`);
    el.classList.remove("fade");
  };
  if (!el.textContent || matchMedia("(prefers-reduced-motion: reduce)").matches) return set();
  el.classList.add("fade");
  setTimeout(set, 900);
}

const LAMP = '<span class="llamp" aria-hidden="true"><i class="f"></i><i class="l"></i></span>';
// expired：用到一半登入失效（401）
async function showLogin(expired = false) {
  setView("login");
  if (!sayTimer) { nextSaying(); sayTimer = setInterval(nextSaying, 10000); }
  const g = $("#userGrid"), note = $("#loginNote");
  g.innerHTML = "";
  note.textContent = "";
  const cfg = await api("/api/auth/config").catch(() => ({ mode: "dev" }));
  $("#appVer").textContent = cfg.version ? `v${cfg.version}` : "";
  if (cfg.mode === "oidc") {  // Keycloak：整頁導去登入，回來時後端已建好 session
    const failed = new URLSearchParams(location.search).has("login_error");
    note.textContent = failed ? "登入沒有完成：請再試一次；若一直失敗，請聯絡管理員確認帳號。"
      : expired ? "登入已失效，請重新登入。" : "";
    g.innerHTML = `<a class="sso" href="/api/auth/login">${LAMP}以 Toolmen SSO 登入</a>`;
    return;
  }
  note.textContent = expired ? "登入已失效，點一下自己的名片重新進入。"
    : "測試登入：免密碼，點一下名片就進入自己的論文庫。";
  try {
    const users = await api("/api/auth/users");
    g.innerHTML = users.length
      ? '<div class="cards users">' + users.map((u) => `<button class="card" data-id="${escapeHTML(u.id)}"><span class="uinit">${escapeHTML([...u.name][0])}</span>
          <span class="cname">${escapeHTML(u.name)}</span></button>`).join("") + "</div>"
      : '<p class="cards-empty">沒有可登入的測試使用者（請在 .env 設定 TEST_USERS）。</p>';
  } catch (e) {
    g.innerHTML = `<p class="cards-empty err">讀不到使用者清單：${escapeHTML(e.message)}</p>`;
  }
  $$("#userGrid .card").forEach((b) => (b.onclick = async () =>
    enter(await api("/api/auth/login", { method: "POST", body: { user_id: b.dataset.id } }))));
}

async function enter(user) {
  $("#userName").textContent = user.name;
  const [id, p, aid] = location.hash.slice(1).split("/");
  if (id) openAt(id, +(p || "").slice(1), aid).catch(showHome); else showHome();
}

/** 深連結 #<pid>/p<n>/<aid>（匯出的筆記用）：開論文、跳到第 n 頁（從 1 起）、閃一下那則標註。只有 #<pid> 就只開論文。 */
async function openAt(pid, page, aid) {
  if (S.paper?.id !== pid || document.body.dataset.view !== "reader") {
    await openPaper(pid);
    if (page) await new Promise((r) => setTimeout(r, 300));  // 同 openCite：等頁面排好再跳
  }
  if (page) goToPage(page - 1, /^\w+$/.test(aid || "") ? aid : undefined);  // aid 會進 CSS 選擇器，只收英數
}
addEventListener("hashchange", () => {
  const [id, p, aid] = location.hash.slice(1).split("/");
  if (id && document.body.dataset.view && document.body.dataset.view !== "login") openAt(id, +(p || "").slice(1), aid).catch(() => {});
});

const tile = (id, name, n, cls = "") => `<button class="card ${cls}" data-id="${escapeHTML(id)}">
  <span class="cname">${escapeHTML(name)}</span><span class="ccount">${n} 篇論文</span></button>`;

async function showHome() {
  setView("home");
  history.replaceState(null, "", location.pathname);
  [workspaces] = await Promise.all([api("/api/workspaces"), loadLibrary()]);
  $("#wsGrid").innerHTML = tile("", "全部論文", library.length, "all")
    + workspaces.map((w) => tile(w.id, w.name, w.count)).join("")
    + '<button class="card new" data-new="1"><span class="plus">＋</span>新增研究主題</button>'
    + (workspaces.length ? "" : `<p class="cards-empty">${sisyphus("rest", 240, "wm")}<span>還沒有研究主題。按「＋ 新增研究主題」把論文依主題分類；論文本身都會留在「全部論文」。</span></p>`);
}
$("#wsGrid").onclick = async (e) => {
  const b = e.target.closest("button.card");
  if (!b) return;
  if (!b.dataset.new) return showWs(workspaces.find((w) => w.id === b.dataset.id) || null);
  const name = await inlineInput(b, "新研究主題的名稱", "", "例如：RAG、待讀");
  if (name) showWs(await api("/api/workspaces", { method: "POST", body: { name } }));
};

async function showWs(ws = curWs) {
  if (ws?.id !== curWs?.id) { wsTab = "papers"; wikiSlug = null; $("#wikiProg").textContent = ""; $("#wikiBar").hidden = true; }
  curWs = ws;
  setView("ws");
  $("#wsTitle").textContent = ws ? ws.name : "全部論文";
  $$("#wsView .ws-only").forEach((b) => (b.hidden = !ws));
  $("#wsStatus").textContent = "";
  setWsTab(ws ? wsTab : "papers");
  await renderWsCards(ws);
}

/** 只重畫論文卡片（背景翻譯輪詢也走這裡，不動分頁、Wiki、上傳狀態）。 */
async function renderWsCards(ws) {
  wsPaperList = ws ? await api(`/api/papers?workspace=${encodeURIComponent(ws.id)}`) : (await loadLibrary(), library);
  // 正在寫備註或看引用時不重畫，免得打到一半被洗掉；關掉編輯器／對話框時會用最新清單重畫
  if (!cardsBusy()) paintWsCards();
  // 有論文還在背景取書目或翻譯：過幾秒再刷新，直到都跑完或離開這頁
  if (wsPaperList.some((p) => p.translating || p.fetching_bib)) setTimeout(() => {
    if (document.body.dataset.view === "ws" && curWs === ws) renderWsCards(ws);
  }, 4000);
}
const cardsBusy = () => !!$("#wsPapers .cnote-ed, #wsPapers [data-armed]") || $("#citeDlg").open;

// 排序在前端做（清單已經抓回來了）；同分時用加入時間新→舊
// added：加入這個研究主題的時間（全部論文 = 上傳時間），重複上傳加進來的舊論文也排最前面
const SORTS = {
  new: (a, b) => b.added - a.added,
  old: (a, b) => a.added - b.added,
  title: (a, b) => (a.title || a.filename).localeCompare(b.title || b.filename, "zh-Hant", { sensitivity: "base" }) || b.created - a.created,
  star: (a, b) => !!b.starred - !!a.starred || b.created - a.created,
  // 沒年份當 -∞ 排最後；兩篇都沒有會得 NaN，落到加入時間
  year: (a, b) => (b.year ?? -Infinity) - (a.year ?? -Infinity) || b.created - a.created,
};
let wsSort = store.get("lantern.wsSort", "new");
if (!SORTS[wsSort]) wsSort = "new";
$("#wsSort").value = wsSort;
$("#wsSort").onchange = (e) => { wsSort = e.target.value; store.set("lantern.wsSort", wsSort); paintWsCards(); };

/** 用 wsPaperList 畫卡片；focusId + sel 指定重畫後焦點放回哪顆按鈕。 */
function paintWsCards(focusId, sel) {
  const del = curWs ? "移出這個研究主題（論文本身保留）" : "刪除這篇論文";
  $("#wsPapers").innerHTML = [...wsPaperList].sort(SORTS[wsSort]).map((p) => `<div class="card${p.starred ? " starred" : ""}${p.translating || p.fetching_bib ? " busy" : ""}" data-id="${escapeHTML(p.id)}">
      <img class="cthumb" src="/api/papers/${encodeURIComponent(p.id)}/thumb.png" alt="" loading="lazy">
      <div class="cbody">
      <button class="copen">${escapeHTML(p.title || p.filename)}</button>
      ${p.byline ? `<span class="cby">${escapeHTML(p.byline)}</span>` : ""}
      ${p.fetching_bib || p.translating ? `<span class="cstage">${[p.fetching_bib && "取得書目中", p.translating && "翻譯中"].filter(Boolean).join("、")}</span>` : ""}
      ${p.tags.length ? `<div class="ptags">${p.tags.map((t) => `#${escapeHTML(t)}`).join(" ")}</div>` : ""}
      ${p.note ? `<p class="cnote">${escapeHTML(p.note)}</p>` : ""}
      <div class="cfoot"><span class="ccount">${fmtDate(p.created)}</span><span class="cacts">
        <button class="cact cstar" aria-pressed="${!!p.starred}" aria-label="星號" title="${p.starred ? "取消星號" : "加星號"}">${p.starred ? "★" : "☆"}</button>
        <button class="cact cnote-btn" aria-expanded="false" title="${p.note ? "編輯備註" : "寫備註"}"><svg aria-hidden="true"><use href="#i-pen"/></svg>備註</button>
        <button class="cact ccite" aria-haspopup="dialog" title="複製引用格式"><svg aria-hidden="true"><use href="#i-quote"/></svg>引用</button>
      </span></div></div>${trRing(p)}
      <button class="cdel" title="${del}" aria-label="${del}">×</button></div>`).join("")
    || `<p class="cards-empty">${sisyphus("rest", 240, "wm")}<span>${curWs ? "這個研究主題還沒有論文：上傳 PDF、匯入 arXiv，或加入既有論文。" : "還沒有論文：上傳 PDF 或匯入 arXiv 開始。"}</span></p>`;
  if (focusId) $(`#wsPapers .card[data-id="${CSS.escape(focusId)}"] ${sel}`)?.focus();
}
const cardPaper = (id) => wsPaperList.find((x) => x.id === id);
// 回傳 {tags, note, starred}；寫回目前清單裡那一筆（輪詢可能已經換掉清單物件）
const patchPaper = async (id, body) => Object.assign(cardPaper(id) || {}, await api(`/api/papers/${id}`, { method: "PATCH", body }));

/** 在卡片裡展開備註編輯框：失焦或 Ctrl+Enter 存，Esc 放棄。 */
function openNote(card, p) {
  const ta = document.createElement("textarea");
  ta.className = "cnote-ed"; ta.rows = 4; ta.value = p.note || "";
  ta.placeholder = "寫下這篇的重點或待辦…";
  ta.setAttribute("aria-label", `《${p.title || p.filename}》的備註（Ctrl+Enter 儲存，Esc 取消）`);
  const old = card.querySelector(".cnote");
  old ? old.replaceWith(ta) : card.querySelector(".cfoot").before(ta);
  card.querySelector(".cnote-btn").setAttribute("aria-expanded", "true");
  ta.focus();
  let done = false;
  ta.onblur = async () => {
    if (done) return;
    done = true;
    const note = ta.value.trim();
    try {
      if (note !== (cardPaper(p.id)?.note || "")) await patchPaper(p.id, { note });
      paintWsCards(p.id, ".cnote-btn");
    } catch (err) {  // 存失敗：留著編輯框和內容，再點進去、離開就會重試
      done = false;
      card.querySelector(".cerr")?.remove();
      ta.insertAdjacentHTML("afterend", `<p class="cerr" role="alert">備註沒存到：${escapeHTML(err.message)}</p>`);
    }
  };
  ta.onkeydown = (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); ta.blur(); }
    else if (e.key === "Escape") { e.stopPropagation(); done = true; paintWsCards(p.id, ".cnote-btn"); }
  };
}

/** 背景對照翻譯的進度圈（只有圈，不顯示數字）；沒開始翻譯的論文不畫。 */
function trRing(p) {
  if (!p.tr_done && !p.translating) return "";
  const pct = Math.round(100 * Math.min(1, p.tr_done / (p.tr_total || 1)));
  return `<svg class="tr-ring${pct >= 100 ? " done" : ""}" viewBox="0 0 20 20" role="img" aria-label="對照翻譯 ${pct}%">
    <circle cx="10" cy="10" r="8"/><circle class="fill" cx="10" cy="10" r="8" pathLength="100" stroke-dasharray="${pct} 100"/></svg>`;
}
$("#wsPapers").onclick = async (e) => {
  const card = e.target.closest(".card");
  const id = card?.dataset.id;
  if (!id || e.target.closest(".cnote-ed")) return;
  if (e.target.closest(".cstar")) {
    try { await patchPaper(id, { starred: !cardPaper(id)?.starred }); }
    catch (err) { $("#wsStatus").textContent = `星號沒存到：${err.message}`; return; }
    return paintWsCards(id, ".cstar");
  }
  if (e.target.closest(".cnote-btn")) return card.querySelector(".cnote-ed")?.focus() ?? openNote(card, cardPaper(id));
  if (e.target.closest(".ccite")) return openCiteDlg(cardPaper(id));
  const del = e.target.closest(".cdel");
  if (!del) return openPaper(id);
  if (!armDelete(del)) return;
  await api(curWs ? `/api/workspaces/${curWs.id}/papers/${id}` : `/api/papers/${id}`, { method: "DELETE" });
  showWs();
};

/* 引用對話框：GET /api/papers/{pid}/cite，第一次比較慢（後端要去查書目） */
const CITE_STYLES = [["apa", "APA 7"], ["ieee", "IEEE"], ["mla", "MLA 9"], ["bibtex", "BibTeX"]];
let citePid = null, citeStyles = {};
async function openCiteDlg(p) {
  citePid = p.id; citeStyles = {};
  $("#citePaper").textContent = p.title || p.filename;
  $("#citeBody").innerHTML = '<p class="muted small">正在取得書目資料…第一次會花幾秒。</p>';
  $("#citeDlg").showModal();
  try {
    const { styles } = await api(`/api/papers/${p.id}/cite`);
    if (citePid !== p.id) return;
    citeStyles = styles;
    $("#citeBody").innerHTML = CITE_STYLES.filter(([k]) => styles[k]).map(([k, name]) => `<section class="cstyle" data-k="${k}">
        <div class="chead"><span>${name}</span><button class="small ccopy" data-k="${k}"><svg aria-hidden="true"><use href="#i-copy"/></svg><span>複製</span></button></div>
        <pre>${escapeHTML(styles[k])}</pre></section>`).join("")
      || '<p class="muted small">這篇論文的書目資料不夠，產生不了引用。</p>';
  } catch (err) {
    if (citePid === p.id) $("#citeBody").innerHTML = `<p class="err small">取不到書目資料：${escapeHTML(err.message)}</p>`;
  }
}
$("#citeBody").onclick = async (e) => {
  const b = e.target.closest(".ccopy");
  if (!b) return;
  const label = b.querySelector("span");
  try { await navigator.clipboard.writeText(citeStyles[b.dataset.k]); label.textContent = "已複製"; }
  catch { label.textContent = "無法複製，請手動選取"; }
  clearTimeout(b._t); b._t = setTimeout(() => (label.textContent = "複製"), 2000);
};
$("#citeClose").onclick = () => $("#citeDlg").close();
// 開著時輪詢沒重畫卡片：關掉後補畫，焦點回到「引用」鈕
$("#citeDlg").onclose = () => { const id = citePid; citePid = null; paintWsCards(id, ".ccite"); };

/* ---------------- Workspace Wiki（docs/wiki.md） ---------------- */
let wsTab = "papers", wsPaperList = [], wikiSlug = null, wikiBusy = false;

function setWsTab(t) {
  wsTab = t;
  $$("#wsTabs button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.tab === t));
  $("#wsPapers").hidden = $("#wsSort").hidden = t !== "papers";
  $("#wsWiki").hidden = t !== "wiki";
  $("#wsAsk").hidden = t !== "ask";
  if (t === "ask") loadAsk();
  if (t === "wiki") return loadWiki();
}
$("#wsTabs").onclick = (e) => {
  const b = e.target.closest("button[data-tab]");
  if (b && b.dataset.tab !== wsTab) setWsTab(b.dataset.tab);
};

// 論文短標題：取冒號前那段（「BERT: Pre-training…」→「BERT」），太長就截斷
const shortTitle = (t) => { t = String(t).split(/[:：]/)[0].trim(); return t.length > 26 ? t.slice(0, 24) + "…" : t; };

/** 把 [[slug|字]]、[[paper:pid#pN]] 換成自己產生的標記；先用佔位字串躲過 marked / DOMPurify，所有內容都 escape。 */
function renderWiki(el, md) {
  const out = [];
  const text = md.replace(/\[\[([^\]|\n]+)(?:\|([^\]\n]+))?\]\]/g, (_, target, label) => {
    target = target.trim();
    const c = /^paper:([^#\s]+)#p(\d+)(?:@(\w+))?$/.exec(target);  // @aid：筆記裡的標註錨點
    if (c) {
      const p = wsPaperList.find((x) => x.id === c[1]) || library.find((x) => x.id === c[1]) || (S.paper?.id === c[1] && S.paper);
      const full = p ? p.title || p.filename : "論文";
      out.push(`<button class="wcite" data-pid="${escapeHTML(c[1])}" data-page="${c[2]}"${c[3] ? ` data-aid="${c[3]}"` : ""} title="${escapeHTML(full)}，第 ${c[2]} 頁"
        aria-label="開啟《${escapeHTML(full)}》第 ${c[2]} 頁">${escapeHTML(shortTitle(full))}<span class="wcp">p.${c[2]}</span></button>`);
    } else {
      out.push(`<a class="wref" href="#" data-slug="${escapeHTML(target)}">${escapeHTML(label?.trim() || target)}</a>`);
    }
    return `@@WL${out.length - 1}@@`;
  });
  renderMD(el, text);
  el.innerHTML = el.innerHTML.replace(/@@WL(\d+)@@/g, (_, i) => out[i]);
}

async function loadWiki() {
  const ws = curWs, page = $("#wikiPage");
  let w;
  try {
    w = await api(`/api/workspaces/${ws.id}/wiki`);
  } catch (e) {
    page.innerHTML = `<p class="cards-empty err">讀不到這個研究主題的 Wiki：${escapeHTML(e.message)}</p>`;
    return;
  }
  if (curWs?.id !== ws.id) return;
  $("#wikiPending").textContent = w.pending ? `${w.pending} 篇論文待整理` : w.pages.length ? "所有論文都已整理" : "";
  $("#wikiUpdate").disabled = wikiBusy || !w.pending;
  if (w.running && !wikiBusy) $("#wikiUpdate").onclick();  // 重新整理前已在跑：接回進度
  $("#wikiList").innerHTML = w.pages.map((p) => `<li><button class="witem${p.slug === "index" ? " home" : ""}" data-slug="${escapeHTML(p.slug)}">${escapeHTML(p.title)}</button></li>`).join("");
  if (!w.pages.length) {
    page.innerHTML = `<div class="wempty">${sisyphus("rest", 240, "wm")}<h3>這個研究主題還沒有 Wiki</h3>
      <p>按「更新 Wiki」，Lantern 會逐篇讀過這裡的論文，為每篇寫一頁重點，把反覆出現的方法、概念與資料集整理成跨論文的條目，最後寫一頁總覽串起全部。</p>
      <p>每個說法都標著出處，點一下就回到論文的那一頁。之後加入新論文再按一次，只會整理新的那幾篇。</p>
      ${w.pending ? "" : "<p>先到「論文」分頁加入論文，才有東西可以整理。</p>"}</div>`;
    return;
  }
  await showWikiPage(w.pages.some((p) => p.slug === wikiSlug) ? wikiSlug : w.pages[0].slug);
}

async function showWikiPage(slug) {
  const ws = curWs, page = $("#wikiPage");
  let p;
  try {
    p = await api(`/api/workspaces/${ws.id}/wiki/${encodeURIComponent(slug)}`);
  } catch (e) {
    page.innerHTML = `<p class="cards-empty err">開不了「${escapeHTML(slug)}」這一頁：${escapeHTML(e.message)}</p>`;
    return;
  }
  if (curWs?.id !== ws.id) return;
  wikiSlug = slug;
  $$("#wikiList .witem").forEach((b) => (b.dataset.slug === slug ? b.setAttribute("aria-current", "page") : b.removeAttribute("aria-current")));
  page.innerHTML = `<h1 class="wtitle" tabindex="-1">${escapeHTML(p.title)}</h1><div class="wbody"></div>
    <p class="wmeta">更新於 ${fmtDate(p.updated)}${p.sources?.length ? `，整理自 ${p.sources.length} 篇論文` : ""}</p>`;
  // 模型常把標題再寫一次成 # 標題：頁首已經有了，同名就拿掉
  const md = (p.markdown || "").replace(/^\s*#\s+(.+)\n/, (m, t) => (t.trim() === p.title.trim() ? "" : m));
  renderWiki($(".wbody", page), md);
}

function focusWikiTitle() {
  const h = $("#wikiPage .wtitle");
  if (h) { h.focus({ preventScroll: true }); if (h.getBoundingClientRect().top < 60) h.scrollIntoView({ block: "start" }); }
}
/** 從 Wiki 以外的地方（問答、閱讀頁）跳到目前 workspace 的某一頁 Wiki。 */
async function openWikiPage(slug) {
  wikiSlug = slug;
  await setWsTab("wiki");
  focusWikiTitle();
}
/** Wiki 頁與問答共用：點引用標記就開論文跳到那一頁。 */
async function openCite(c) {
  try {
    await openPaper(c.dataset.pid);
    setTimeout(() => goToPage(+c.dataset.page - 1), 300);  // 同搜尋結果：等頁面排好再跳
  } catch (err) {
    showWs();
    $("#wsStatus").innerHTML = `<span class="err">開不了這篇論文：${escapeHTML(err.message)}（可能已經被刪除）</span>`;
  }
}
$("#wsWiki").onclick = async (e) => {
  const l = e.target.closest("[data-slug]");
  if (l) {
    e.preventDefault();
    await showWikiPage(l.dataset.slug);
    focusWikiTitle();
    return;
  }
  const c = e.target.closest(".wcite");
  if (c) openCite(c);
};

/* ---------------- Wiki 問答（docs/wiki.md 第二階段） ---------------- */
let askBusy = false;

async function loadAsk() {
  const ws = curWs, out = $("#askOut");
  let msgs, w;
  try {
    [msgs, w] = await Promise.all([api(`/api/workspaces/${ws.id}/ask`), api(`/api/workspaces/${ws.id}/wiki`)]);
  } catch (e) {
    out.innerHTML = `<p class="cards-empty err">讀不到問答紀錄：${escapeHTML(e.message)}</p>`;
    return;
  }
  if (curWs?.id !== ws.id) return;
  out.innerHTML = "";
  let q = "";
  for (const m of msgs) {
    if (m.role === "user") q = m.content;
    addAsk(m.role, m.content, q, m.id);
  }
  const empty = !w.pages.length;
  $("#qaInput").disabled = $("#qaForm button").disabled = empty;
  $("#askClear").hidden = !msgs.length;
  if (empty) out.insertAdjacentHTML("beforeend", `<div class="wempty qempty"><h3>先有 Wiki，才能問</h3>
    <p>問答會先查這個研究主題的 Wiki 再回答。現在還沒有任何 Wiki 頁：到 Wiki 分頁按「更新 Wiki」，整理好就能回來問。</p>
    <button class="tool" data-go="wiki">到 Wiki 分頁</button></div>`);
}

/** 一則問答：問題是可收合的條目標題（<details>），回答是一張羊皮紙放在同一個條目裡；
 *  q 是回答前那個問題（存成 Wiki 頁要一起送）；id 是問題在伺服器上的編號（刪單題用）。 */
function addAsk(role, text, q, id) {
  if (role === "user") {
    const item = document.createElement("details");
    item.className = "qitem";
    item.open = true;
    if (id) item.dataset.id = id;
    item.innerHTML = '<summary class="qa user"><span class="qtext"></span><button class="qdel" type="button" aria-label="刪除這一題">×</button></summary>';
    $(".qtext", item).textContent = text;
    $("#askOut").appendChild(item);
    return item.firstChild;
  }
  const d = document.createElement("div");
  d.className = `qa ${role}`;
  d.innerHTML = '<div class="wbody qbody" aria-live="polite"></div>';
  renderWiki(d.firstChild, text);
  if (text) addSave(d, q, text);
  ($("#askOut > .qitem:last-of-type") || $("#askOut")).appendChild(d);
  return d;
}

function addSave(d, question, answer) {
  const f = document.createElement("div");
  f.className = "qsave";
  f.innerHTML = '<button class="qsavebtn">存成 Wiki 頁</button><span class="qstat" role="status"></span>';
  const b = f.firstChild, st = f.lastChild, ws = curWs;
  b.onclick = async () => {
    b.disabled = true;
    st.textContent = "整理成 Wiki 頁中…";
    try {
      const p = await api(`/api/workspaces/${ws.id}/ask/save`, { method: "POST", body: { question, answer } });
      b.remove();
      st.innerHTML = `已存成 Wiki 頁<a class="wref" href="#" data-slug="${escapeHTML(p.slug)}">${escapeHTML(p.title)}</a>`;
      $("a", st).focus();
    } catch (e) {
      b.disabled = false;
      st.innerHTML = `<span class="err">沒有存成：${escapeHTML(e.message)}</span>`;
    }
  };
  d.appendChild(f);
}

async function sendAsk(q) {
  const ws = curWs;
  askBusy = true;
  $("#askClear").hidden = false;
  const head = addAsk("user", q);
  head.scrollIntoView({ block: "start", behavior: "smooth" });
  const d = addAsk("assistant", ""), body = d.firstChild;
  body.classList.add("cursor");
  body.setAttribute("aria-busy", "true");  // 串完才念出整段，不要一個字一個字報
  const stop = pushLater((w) => body.append(w), 32, "回答中…");
  try {
    const full = await stream(`/api/workspaces/${ws.id}/ask`, { body: { question: q } }, (t) => { stop(); renderWiki(body, t); });
    renderWiki(body, full);
    addSave(d, q, full);
    // 串流不回編號：串完再查一次，拿最新那則問題的 id，這題才能單獨刪
    const last = (await api(`/api/workspaces/${ws.id}/ask`)).findLast((m) => m.role === "user");
    if (last) head.parentElement.dataset.id = last.id;
  } catch (e) {
    body.innerHTML = `<span class="err">${escapeHTML(e.message)}</span>`;
  } finally {
    stop();
    body.classList.remove("cursor");
    body.removeAttribute("aria-busy");
    askBusy = false;
  }
}
$("#qaForm").onsubmit = (e) => {
  e.preventDefault();
  const q = $("#qaInput").value.trim();
  if (!q || askBusy) return;
  $("#qaInput").value = "";
  sendAsk(q);
};
$("#qaInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); $("#qaForm").requestSubmit(); }
});
$("#askClear").onclick = async (e) => {
  if (!armDelete(e.currentTarget)) return;
  await api(`/api/workspaces/${curWs.id}/ask`, { method: "DELETE" });
  loadAsk();
};
$("#wsAsk").onclick = async (e) => {
  const del = e.target.closest(".qdel");
  if (del) {  // 在 summary 裡：不要觸發收合
    e.preventDefault();
    const item = del.closest(".qitem");
    if (!armDelete(del)) return;
    try {
      await api(`/api/workspaces/${curWs.id}/ask/${item.dataset.id}`, { method: "DELETE" });
      item.remove();
      if (!$("#askOut .qitem")) $("#askClear").hidden = true;
    } catch (err) {
      del.textContent = "刪不掉";
    }
    return;
  }
  if (e.target.closest("[data-go]")) return setWsTab("wiki");
  const l = e.target.closest("a[data-slug]");
  if (l) { e.preventDefault(); return openWikiPage(l.dataset.slug); }
  const c = e.target.closest(".wcite");
  if (c) openCite(c);
};

$("#wikiUpdate").onclick = async () => {
  const ws = curWs, prog = $("#wikiProg"), bar = $("#wikiBar");
  const here = () => curWs?.id === ws.id;
  wikiBusy = true;
  $("#wikiUpdate").disabled = true;
  // 推石動畫只建一次，之後只換文字（重建會讓動畫跳回第一格）
  prog.innerHTML = `<span class="sis-line">${sisyphus("push", 48)}<span class="wmsg">開始整理…</span></span>`;
  bar.removeAttribute("value"); bar.hidden = false;
  try {
    await stream(`/api/workspaces/${ws.id}/wiki/update`, {}, (_, t) => {
      let m;
      try { m = JSON.parse(t); } catch { m = { msg: t }; }
      if (!here()) return;
      const msg = $(".wmsg", prog);
      if (msg) msg.textContent = m.msg || ""; else prog.textContent = m.msg || "";
      bar.hidden = false;
      if (m.total) { bar.max = m.total; bar.value = m.done || 0; }
    });
    if (here()) prog.innerHTML = `<span class="sis-line">${sisyphus("summit", 48)}Wiki 已更新。</span>`;
  } catch (e) {
    if (here()) prog.innerHTML = `<span class="sis-line">${sisyphus("fall", 48)}<span class="err">更新沒有完成：${escapeHTML(e.message)}。已整理好的論文會保留，再按一次「更新 Wiki」只做剩下的。</span></span>`;
  }
  wikiBusy = false;
  bar.hidden = true;
  if (here() && wsTab === "wiki") loadWiki();
};

$("#wsUpload").onclick = () => $("#wsFile").click();
$("#wsFile").onchange = (e) => {
  const f = e.target.files[0];
  e.target.value = "";  // 同一個檔案再選一次也要觸發
  if (f) uploadFile(f, curWs?.id, $("#wsStatus"));
};
$("#wsArxiv").onclick = async (e) => {
  const url = await inlineInput(e.currentTarget, "arXiv 編號或 PDF 網址", "", "arXiv 編號或 PDF 網址");
  if (url) importArxiv(url, curWs?.id, $("#wsStatus"));
};
$("#wsAdd").onclick = async () => {
  const inWs = new Set($$("#wsPapers .card").map((c) => c.dataset.id));
  await loadLibrary();
  const rest = library.filter((p) => !inWs.has(p.id));
  $("#addList").innerHTML = rest.map((p) => `<li><button class="aitem" data-id="${escapeHTML(p.id)}">${escapeHTML(p.title || p.filename)}</button></li>`).join("")
    || '<li class="muted small">所有論文都已經在這個研究主題裡了。</li>';
  $("#addDlg").showModal();
};
$("#addList").onclick = async (e) => {
  const b = e.target.closest("button[data-id]");
  if (!b) return;
  await api(`/api/workspaces/${curWs.id}/papers`, { method: "POST", body: { paper_id: b.dataset.id } });
  b.closest("li").remove();  // 對話框不關，可以連續加好幾篇
  showWs();
};
$("#addClose").onclick = () => $("#addDlg").close();
$("#wsRename").onclick = async (e) => {
  const name = await inlineInput(e.currentTarget, "研究主題名稱", curWs.name);
  if (name && name !== curWs.name) showWs(await api(`/api/workspaces/${curWs.id}`, { method: "PATCH", body: { name } }));
};
$("#wsDelete").onclick = async (e) => {
  if (!armDelete(e.currentTarget)) return;
  await api(`/api/workspaces/${curWs.id}`, { method: "DELETE" });
  showHome();
};
$("#wsBack").onclick = showHome;
$("#btnHome").onclick = () => showWs(S.fromWs || null);

/** 就地輸入框（取代 prompt()）：暫時換掉 anchor 按鈕。Enter 確認、Esc 或離開取消；回傳去掉空白的值，取消回 null。 */
function inlineInput(anchor, label, value = "", placeholder = "") {
  return new Promise((resolve) => {
    const inp = document.createElement("input");
    inp.className = "inline-in";
    inp.value = value;
    inp.placeholder = placeholder;
    inp.setAttribute("aria-label", `${label}（Enter 確認，Esc 取消）`);
    anchor.hidden = true;
    anchor.after(inp);
    inp.focus();
    inp.select();
    let done = false;
    const finish = (v) => {
      if (done) return;
      done = true;
      inp.remove();
      anchor.hidden = false;
      if (v === null) anchor.focus();  // 取消：焦點回到原按鈕
      resolve(v);
    };
    inp.onkeydown = (e) => {
      if (e.isComposing) return;
      if (e.key === "Enter") { e.preventDefault(); finish(inp.value.trim() || null); }
      else if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); finish(null); }
    };
    inp.onblur = () => finish(null);
  });
}

// 刪除一律按兩下（不用 confirm()）：第一下按鈕變朱色、換成一句俚語提醒刪了救不回來，3 秒內再按才刪
const DELETE_IDIOMS = ["覆水難收，再按一次", "潑出去的水收不回來", "一去不復返，確定？", "船過水無痕，真的要刪？", "此去無回頭，再按一次"];
let idiomTurn = 0;
/** 回傳 true = 已上膛的第二下，該刪了；false = 第一下，只上膛。 */
function armDelete(b) {
  if (b.dataset.armed) return true;
  const html = b.innerHTML, label = b.getAttribute("aria-label"), msg = DELETE_IDIOMS[idiomTurn++ % DELETE_IDIOMS.length];
  b.dataset.armed = "1";
  b.textContent = msg;
  if (label) b.setAttribute("aria-label", msg);
  setTimeout(() => {
    delete b.dataset.armed;
    b.innerHTML = html;
    if (label) b.setAttribute("aria-label", label);
  }, 3000);
  return false;
}
const showSettings = (s) => { $("#setAutoTranslate").checked = s.auto_translate; $("#setAutoWiki").checked = !!s.auto_wiki; };
// 主題：自動（跟系統）→ 淺色 → 深色；<head> 裡的小段程式在畫面出來前就套用
const THEMES = { auto: "自動（跟隨系統）", light: "淺色", dark: "深色" };
function setTheme(t) {
  if (t === "auto") delete document.documentElement.dataset.theme;
  else document.documentElement.dataset.theme = t;
  store.set("lantern.theme", t);
  const keys = Object.keys(THEMES), next = keys[(keys.indexOf(t) + 1) % keys.length];
  const b = $("#btnTheme"), label = `主題：${THEMES[t]}。按一下改成${THEMES[next]}`;
  b.innerHTML = `<svg aria-hidden="true"><use href="#i-theme-${t}"/></svg>`;
  b.setAttribute("aria-label", label);
  b.title = label;
}
setTheme(store.get("lantern.theme", "auto") in THEMES ? store.get("lantern.theme", "auto") : "auto");
$("#btnTheme").onclick = () => {
  const keys = Object.keys(THEMES), cur = document.documentElement.dataset.theme || "auto";
  setTheme(keys[(keys.indexOf(cur) + 1) % keys.length]);
};
$("#btnSettings").onclick = async () => {
  showSettings(await api("/api/me/settings"));
  $("#setDlg").showModal();
};
$("#setAutoTranslate").onchange = $("#setAutoWiki").onchange = async () => {
  showSettings(await api("/api/me/settings", { method: "PUT",
    body: { auto_translate: $("#setAutoTranslate").checked, auto_wiki: $("#setAutoWiki").checked } }));
};
$("#setClose").onclick = () => $("#setDlg").close();
$("#btnLogout").onclick = async () => {
  const r = await api("/api/auth/logout", { method: "POST" });
  if (r.logout_url) { location.href = r.logout_url; return; }  // Keycloak：連同 Keycloak 那邊一起登出，再回到首頁
  history.replaceState(null, "", location.pathname);
  showLogin();
};

/* ---------------- 啟動 ---------------- */
// 401 時 api() 已經切到登入頁；其他錯誤（例如伺服器沒開）也退回登入頁顯示錯誤
api("/api/me").then(enter).catch(() => document.body.dataset.view || showLogin());
