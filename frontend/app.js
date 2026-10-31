/* Lantern 前端：純 JS，不需要打包工具。
 *
 * 結構：
 *   PDF.js 把每一頁畫成 <canvas>（看得到的圖），再疊一層透明的 textLayer（選得到的字）
 *   ，再疊一層 hlLayer（螢光筆）。三層座標一致，所以選到的字、標註都能對齊。
 *   每頁旁邊另有一個 .twin（並排翻譯用的譯文頁），平常隱藏。
 *
 * 互動（仿 Moonlight）：選字 → 浮動工具列（解釋 / 螢光筆 / 翻譯 / 註解 / Ask AI）→ 浮動 AI 卡片；
 * 解釋、標註、註解都記在右側「活動面板」；聊天是右下角的浮動視窗。
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
  const r = await fetch(path, {
    headers: opts.body && !(opts.body instanceof FormData) ? { "Content-Type": "application/json" } : {},
    ...opts,
    body: opts.body && !(opts.body instanceof FormData) ? JSON.stringify(opts.body) : opts.body,
  });
  if (r.status === 401 && document.body.dataset.view !== "login") showLogin();  // 沒登入或登入失效
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText);
  return r.json();
}

/** 讀 SSE：伺服器每推一段 data: {"t": "..."}，就呼叫 onText 一次。 */
async function stream(path, { body, method = "POST" } = {}, onText) {
  const r = await fetch(path, {
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
let library = [], tagFilter = null;

async function loadLibrary() {
  library = await api("/api/papers");
  renderLibrary();
}

function renderLibrary() {
  const q = $("#libSearch").value.trim().toLowerCase();
  // 標籤列：所有用過的標籤，點一下只看那個標籤
  const tags = [...new Set(library.flatMap((p) => p.tags))].sort();
  if (tagFilter && !tags.includes(tagFilter)) tagFilter = null;
  $("#tagBar").innerHTML = tags.map((t) =>
    `<button class="chip ${t === tagFilter ? "on" : ""}" data-tag="${escapeHTML(t)}">#${escapeHTML(t)}</button>`).join("");
  $$("#tagBar .chip").forEach((b) => (b.onclick = () => {
    tagFilter = tagFilter === b.dataset.tag ? null : b.dataset.tag; renderLibrary();
  }));

  const ul = $("#paperList");
  ul.innerHTML = "";
  const shown = library.filter((p) => (!tagFilter || p.tags.includes(tagFilter))
    && (!q || `${p.title} ${p.filename} ${p.tags.join(" ")}`.toLowerCase().includes(q)));
  if (!library.length) ul.innerHTML = '<li class="muted small">還沒有論文</li>';
  else if (!shown.length) ul.innerHTML = '<li class="muted small">沒有符合的論文；按 Enter 搜尋全文</li>';
  for (const p of shown) {
    const li = document.createElement("li");
    li.dataset.id = p.id;
    li.innerHTML = `<div class="ptitle"><span>${escapeHTML(p.title || p.filename)}</span>
        ${p.tags.length ? `<div class="ptags">${p.tags.map((t) => `<span>#${escapeHTML(t)}</span>`).join(" ")}</div>` : ""}</div>
      <button class="del tagbtn" data-k="tag" title="編輯標籤">#</button><button class="del" data-k="del" title="刪除">×</button>`;
    if (S.paper && S.paper.id === p.id) li.classList.add("on");
    li.onclick = async (e) => {
      const k = e.target.dataset.k;
      if (k === "del") {
        if (confirm("刪除這篇論文與所有標註？")) api(`/api/papers/${p.id}`, { method: "DELETE" }).then(loadLibrary);
      } else if (k === "tag") {
        const v = prompt("標籤（用逗號分隔，例如：NLP, 待讀）", p.tags.join(", "));
        if (v === null) return;
        p.tags = (await api(`/api/papers/${p.id}`, { method: "PATCH", body: { tags: v.split(/[,，]/) } })).tags;
        renderLibrary();
      } else openPaper(p.id);
    };
    ul.appendChild(li);
  }
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
    li.innerHTML = `<div><div class="small muted">${escapeHTML(h.title)} · p.${h.page + 1}</div>
      <div class="small">${escapeHTML(h.snippet).replace(re, (m) => `<mark>${m}</mark>`)}</div></div>`;
    li.onclick = async () => {
      if (S.paper?.id !== h.paper_id) await openPaper(h.paper_id);
      setTimeout(() => goToPage(h.page), 300);
    };
    out.appendChild(li);
  }
});
$("#searchClose").onclick = () => { $("#searchOut").hidden = true; };

async function ingest(promise, st = $("#ingestStatus")) {
  st.textContent = "解析中…（擷取文字、建立索引）";
  try {
    const res = await promise;
    st.textContent = `完成：${res.num_pages} 頁、${res.chunks} 個段落`;
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
    openPaper(res.id);
  } catch (e) {
    st.innerHTML = `<span class="err">失敗：${escapeHTML(e.message)}</span>`;
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
$("#file").onchange = (e) => e.target.files[0] && uploadFile(e.target.files[0]);
const drop = $("#drop");
["dragover", "dragenter"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("over"); }));
["dragleave", "drop"].forEach((ev) => drop.addEventListener(ev, () => drop.classList.remove("over")));
drop.addEventListener("drop", (e) => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f) uploadFile(f); });
$("#arxivForm").onsubmit = (e) => {
  e.preventDefault();
  const url = $("#arxivInput").value.trim();
  if (url) importArxiv(url);
};

/* ---------------- 開啟論文、畫 PDF ---------------- */
async function openPaper(id) {
  S.paper = await api(`/api/papers/${id}`);
  setView("reader");
  S.annotations = await api(`/api/papers/${id}/annotations`);
  S.tr = {}; S.trQueue = []; S.figures = []; S.refs = [];
  api(`/api/papers/${id}/figures`).then((f) => { S.figures = f; }).catch(() => {});
  api(`/api/papers/${id}/references`).then((r) => { S.refs = r; renderRefs(); }).catch(() => {});
  $("#paperTitle").textContent = S.paper.title;
  $("#empty").hidden = true;
  $("#pageTotal").textContent = `/ ${S.paper.num_pages}`;
  $$("#paperList li").forEach((li) => li.classList.toggle("on", li.dataset.id === id));
  renderOutline(S.paper.outline);
  S.pdf = await pdfjsLib.getDocument(`/api/papers/${id}/pdf`).promise;
  buildPages();
  renderInfo();
  renderActivity();
  $("#summaryOut").innerHTML = "";
  $("#relatedList").innerHTML = '<li class="muted small">按上方按鈕取得推薦（資料來自 Semantic Scholar）。</li>';
  closeAiCard();
  chatLoaded = false;
  if (!$("#chatWin").hidden) loadChat();
  history.replaceState(null, "", `#${id}`);
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
    row.innerHTML = `<div class="page" data-page="${i}" style="${size}"><div class="hlLayer"></div>
        <div class="pno">${i + 1} / ${S.paper.num_pages}</div></div>
      <div class="twin" style="${size}"><div class="trLayer"></div><div class="pno">譯 ${i + 1}</div></div>`;
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

  const tl = document.createElement("div");
  tl.className = "textLayer";
  pg.el.style.setProperty("--scale-factor", S.scale);
  pg.el.appendChild(tl);
  await pdfjsLib.renderTextLayer({
    textContentSource: await page.getTextContent(), container: tl, viewport, textDivs: [],
  }).promise;
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
    for (const [x0, y0, x1, y1] of a.rects) {
      const d = document.createElement("div");
      d.className = `hl ${cls}`;
      d.dataset.id = a.id;
      if (a.kind === "user" && isHex(a.color)) d.style.background = tint(a.color, 0.34);
      Object.assign(d.style, { left: `${x0 * 100}%`, top: `${y0 * 100}%`,
                               width: `${(x1 - x0) * 100}%`, height: `${(y1 - y0) * 100}%` });
      layer.appendChild(d);
    }
    const [x0, y0] = a.rects[0] || [0, 0];
    const side = x0 < 0.5 ? "left" : "right";  // 標籤放在離它最近的頁邊
    if (AUTO[a.kind] && S.filter.labels) {
      layer.insertAdjacentHTML("beforeend",
        `<span class="mlabel ${side} ${a.kind.slice(5)}" style="top:${y0 * 100}%">${AUTO[a.kind]}</span>`);
    } else if (a.kind === "comment") {
      const m = document.createElement("button");
      m.className = `cmark ${side}`;
      m.style.top = `${y0 * 100}%`;
      m.title = a.comment;
      m.innerHTML = icon("comment");
      m.onclick = () => { openPanel("comments"); flashItem(a.id); };
      layer.appendChild(m);
    }
  }
}

function visibleOnPage(a) {
  const f = S.filter;
  if (a.kind === "user") return f.colors.has(colorKey(a.color));
  if (AUTO[a.kind]) return f.auto && f.autoKinds.has(a.kind);
  return true;
}

function goToPage(i, flashId) {
  const pg = S.pages[i];
  if (!pg) return;
  pg.el.scrollIntoView({ behavior: "smooth", block: "start" });
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
}, { passive: true });

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
$("#toggleLib").onclick = () => {
  const m = $("main");
  if (innerWidth <= 1100) m.classList.toggle("showlib"); else m.classList.toggle("nolib");
};
$("#togglePanel").onclick = () => $("main").classList.toggle("nopanel");

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
    li.innerHTML = `<span class="caret">${it.parent ? (it.open ? "▾" : "▸") : ""}</span><span>${escapeHTML(it.title)}</span>`;
    li.onclick = (e) => {
      if (e.target.classList.contains("caret") && it.parent) { it.open = !it.open; drawOutline(); }
      else goToPage(it.page);
    };
    ul.appendChild(li);
  }
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
function readSelection() {
  const sel = getSelection();
  const text = sel.toString().trim();
  const pageEl = sel.anchorNode?.parentElement?.closest(".page");
  if (!text || text.length < 2 || !pageEl || !sel.rangeCount) return null;
  const range = sel.getRangeAt(0);
  const pr = pageEl.getBoundingClientRect();
  const rects = [...range.getClientRects()]
    .filter((r) => r.width > 1 && r.height > 1 && r.top >= pr.top - 2 && r.bottom <= pr.bottom + 2)
    .map((r) => [(r.left - pr.left) / pr.width, (r.top - pr.top) / pr.height,
                 (r.right - pr.left) / pr.width, (r.bottom - pr.top) / pr.height]);
  return { text: text.replace(/\s+/g, " "), page: +pageEl.dataset.page, rects, box: range.getBoundingClientRect() };
}

document.addEventListener("mouseup", (e) => {
  if (e.button !== 0 || selBar.contains(e.target) || S.cropping || crop) return;
  if (!e.target.closest?.("#pages")) return;
  setTimeout(() => {
    lastSel = readSelection();
    if (!lastSel) { selBar.hidden = true; return; }
    const b = lastSel.box;
    selBar.hidden = false;
    const w = selBar.offsetWidth;
    selBar.style.left = `${Math.min(innerWidth - w - 8, Math.max(8, b.left + b.width / 2 - w / 2))}px`;
    selBar.style.top = `${b.top > 110 ? b.top - 52 : b.bottom + 10}px`;
  }, 0);
});
document.addEventListener("mousedown", (e) => {
  if (!selBar.contains(e.target)) selBar.hidden = true;
  if (!$("#ctxMenu").contains(e.target)) $("#ctxMenu").hidden = true;
  if (!$("#citeCard").contains(e.target)) $("#citeCard").hidden = true;
  if (!$("#figCard").contains(e.target)) $("#figCard").hidden = true;
});

selBar.addEventListener("click", (e) => {
  const sw = e.target.closest("[data-color]");
  if (sw) { S.hlColor = sw.dataset.color === "custom" ? customColor : sw.dataset.color; return selAction("highlight"); }
  const b = e.target.closest("[data-act]");
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
    await addAnnotation({ page, rects, color: S.hlColor, text });
    return getSelection().removeAllRanges();
  }
  if (act === "comment") return commentEditor(sel);
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

// 快捷鍵：選字後按 E 解釋、H 螢光筆、T 翻譯、C 註解；Esc 關閉浮動元件
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    setCropping(false); clearCrop(); closeAiCard();
    selBar.hidden = true; $("#ctxMenu").hidden = true; $("#citeCard").hidden = true; hideFigure();
    return;
  }
  if (selBar.hidden || e.ctrlKey || e.metaKey || e.altKey || /INPUT|TEXTAREA/.test(document.activeElement?.tagName)) return;
  const act = { e: "explain", h: "highlight", t: "translate", c: "comment" }[e.key.toLowerCase()];
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
  m.style.top = `${Math.min(innerHeight - 190, e.clientY)}px`;
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
async function streamInto(target, url, body, method = "POST") {
  target.classList.add("cursor");
  try {
    const full = await stream(url, { body, method }, (t) => renderMD(target, t));
    renderMD(target, full);
    return full;
  } catch (e) {
    target.innerHTML = `<span class="err">${escapeHTML(e.message)}</span>`;
    return null;
  } finally {
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
    openPanel("comments");
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
      .filter(Boolean).join(" · ");
    div.innerHTML = `<div class="tag small">${escapeHTML(items[k].label)}</div>
      ${p ? `<h4><a href="${safeUrl(p.url)}" target="_blank" rel="noopener">${escapeHTML(p.title)}</a></h4>
        <div class="small muted">${escapeHTML((p.authors || []).slice(0, 4).map((a) => a.name).join(", "))}${(p.authors || []).length > 4 ? ` +${p.authors.length - 4}` : ""}
        · ${escapeHTML(p.venue || "")} ${p.year ?? ""}</div>
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
  $$("#trMode button").forEach((x) => x.classList.toggle("on", x.dataset.mode === mode));
  $("#pages").classList.toggle("tr-overlay", mode === "overlay");
  $("#pages").classList.toggle("tr-side", mode === "side");
  if (mode === "off") { S.trQueue = []; return; }
  if (mode === "side") {
    // 兩頁並排放不下就自動縮小到剛好塞滿閱讀區寬度
    const w = Math.max(...S.paper.page_sizes.map(([pw]) => pw)), room = $("#viewer").clientWidth - 48;
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
  try {
    const auto = await api(`/api/papers/${S.paper.id}/auto-highlight${refresh ? "?refresh=true" : ""}`, { method: "POST" });
    S.annotations = S.annotations.filter((a) => !a.kind.startsWith("auto:")).concat(auto);
    S.filter.auto = true;
    $("#showAuto").checked = true;
    S.pages.forEach((_, i) => drawHighlights(i));
    renderActivity();
    openPanel("notes");
  } catch (e) {
    alert(`自動標註失敗：${e.message}`);
  }
  btn.disabled = false;
  btn.lastChild.textContent = "自動標註";
};

/* ---------------- 活動面板 ---------------- */
function openPanel(name) {
  $("main").classList.remove("nopanel");
  $$(".tabs button[data-tab]").forEach((b) => b.classList.toggle("on", b.dataset.tab === name));
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
    <div class="small muted">${p.num_pages} 頁 · ${p.references} 筆參考文獻 · ${escapeHTML(p.filename)}</div>
    ${p.abstract ? `<details open><summary class="small">摘要（原文）</summary><p class="small">${escapeHTML(p.abstract)}</p></details>` : ""}`;
}

function renderActivity() { renderNotes(); renderExplains(); renderComments(); }

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
      <button class="link small del" data-k="del">刪除</button></div>${inner}`;
  li.addEventListener("click", (e) => {
    if (e.target.dataset.k === "del") return deleteAnnotation(a);
    if (!/TEXTAREA|SUMMARY|A/.test(e.target.tagName)) goToPage(a.page, a.id);
  });
  return li;
}

function renderNotes() {
  const ul = $("#notesList");
  const q = S.filter.q;
  const items = S.annotations.filter((a) => (a.kind === "user" || AUTO[a.kind]) && visibleOnPage(a)
    && (!q || `${a.text} ${a.comment}`.toLowerCase().includes(q)));
  ul.innerHTML = items.length ? "" : '<li class="muted small empty">還沒有標註。選取文字按螢光筆（H），或按上方「自動標註」。</li>';
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
  ul.innerHTML = items.length ? "" : '<li class="muted small empty">選字後按「解釋」（E）或在 Ask AI 提問，結果會記在這裡。</li>';
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
  ul.innerHTML = items.length ? "" : '<li class="muted small empty">選取文字後按右鍵 →「加註解」，或按工具列的註解圖示（C）。</li>';
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

/* ---------------- 摘要 ---------------- */
async function runSummary(refresh) {
  if (!S.paper) return;
  await streamInto($("#summaryOut"), `/api/papers/${S.paper.id}/summary${refresh ? "?refresh=true" : ""}`, null, "GET");
}
$("#btnSummary").onclick = () => runSummary(false);
$("#btnSummaryRe").onclick = () => runSummary(true);

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
        · ${r.year ?? ""}${r.venue ? " · " + escapeHTML(r.venue) : ""} · 被引用 ${r.citationCount ?? "?"} 次</div>
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

/* ---------------- 浮動聊天視窗 ---------------- */
let chatLoaded = false;
const chatWin = $("#chatWin");
$("#fab").onclick = () => {
  chatWin.hidden = !chatWin.hidden;
  if (!chatWin.hidden) { if (!chatLoaded) loadChat(); $("#chatInput").focus(); }
};
$("#chatClose").onclick = () => { chatWin.hidden = true; };
makeDraggable(chatWin, $(".chead", chatWin));

async function loadChat() {
  if (!S.paper) { $("#chatOut").innerHTML = '<p class="muted">先開啟一篇論文。</p>'; return; }
  chatLoaded = true;
  const out = $("#chatOut"), pid = S.paper.id;
  out.innerHTML = "";
  const msgs = await api(`/api/papers/${pid}/chat`);
  for (const m of msgs) addMsg(m.role, m.content);
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

function addMsg(role, text) {
  const d = document.createElement("div");
  d.className = `msg ${role}`;
  if (role === "user") d.textContent = text; else { renderMD(d, text); addCopy(d, text); }
  $("#chatOut").appendChild(d);
  d.scrollIntoView({ block: "end" });
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
  const full = await streamInto(d, `/api/papers/${S.paper.id}/chat`, { question: q, page: S.current });
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
$("#chatClear").onclick = async () => {
  if (!S.paper || !confirm("清除這篇論文的對話紀錄？")) return;
  await api(`/api/papers/${S.paper.id}/chat`, { method: "DELETE" });
  loadChat();
};

/* ---------------- 畫面切換：登入 / 首頁 / workspace / 閱讀 ---------------- */
// CSS 依 body[data-view] 決定顯示哪一頁（閱讀頁的工具列、側欄等在其他頁都收起來）
const setView = (v) => { document.body.dataset.view = v; };
let workspaces = [], curWs = null;  // curWs = 目前的 workspace；null = 全部論文

async function showLogin() {
  setView("login");
  const g = $("#userGrid");
  g.innerHTML = "";
  try {
    const users = await api("/api/auth/users");
    g.innerHTML = users.length
      ? users.map((u) => `<button class="card" data-id="${escapeHTML(u.id)}"><span class="uinit">${escapeHTML([...u.name][0])}</span>
          <span class="cname">${escapeHTML(u.name)}</span></button>`).join("")
      : '<p class="cards-empty">沒有可登入的測試使用者（請在 .env 設定 TEST_USERS）。</p>';
  } catch (e) {
    g.innerHTML = `<p class="cards-empty err">讀不到使用者清單：${escapeHTML(e.message)}</p>`;
  }
  $$("#userGrid .card").forEach((b) => (b.onclick = async () =>
    enter(await api("/api/auth/login", { method: "POST", body: { user_id: b.dataset.id } }))));
}

async function enter(user) {
  $("#userName").textContent = user.name;
  const id = location.hash.slice(1);
  if (id) openPaper(id).catch(showHome); else showHome();
}

const tile = (id, name, n, cls = "") => `<button class="card ${cls}" data-id="${escapeHTML(id)}">
  <span class="cname">${escapeHTML(name)}</span><span class="ccount">${n} 篇論文</span></button>`;

async function showHome() {
  setView("home");
  history.replaceState(null, "", location.pathname);
  [workspaces] = await Promise.all([api("/api/workspaces"), loadLibrary()]);
  $("#wsGrid").innerHTML = tile("", "全部論文", library.length, "all")
    + workspaces.map((w) => tile(w.id, w.name, w.count)).join("")
    + '<button class="card new" data-new="1"><span class="plus">＋</span>新增 workspace</button>'
    + (workspaces.length ? "" : '<p class="cards-empty">還沒有 workspace。按「＋ 新增 workspace」把論文依主題分類；論文本身都會留在「全部論文」。</p>');
}
$("#wsGrid").onclick = async (e) => {
  const b = e.target.closest("button.card");
  if (!b) return;
  if (!b.dataset.new) return showWs(workspaces.find((w) => w.id === b.dataset.id) || null);
  const name = prompt("新 workspace 的名稱（例如：RAG、待讀）")?.trim();
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
  const papers = wsPaperList = ws ? await api(`/api/papers?workspace=${encodeURIComponent(ws.id)}`) : (await loadLibrary(), library);
  const del = ws ? "移出這個 workspace（論文本身保留）" : "刪除這篇論文";
  $("#wsPapers").innerHTML = papers.map((p) => `<div class="card" data-id="${escapeHTML(p.id)}">
      <button class="copen">${escapeHTML(p.title || p.filename)}</button>
      ${p.tags.length ? `<div class="ptags">${p.tags.map((t) => `#${escapeHTML(t)}`).join(" ")}</div>` : ""}
      <span class="ccount">${fmtDate(p.created)}</span>${trRing(p)}
      <button class="cdel" title="${del}" aria-label="${del}">×</button></div>`).join("")
    || `<p class="cards-empty">${ws ? "這個 workspace 還沒有論文：上傳 PDF、匯入 arXiv，或加入既有論文。" : "還沒有論文：上傳 PDF 或匯入 arXiv 開始。"}</p>`;
  // 有論文還在背景翻譯：過幾秒再刷新，直到都跑完或離開這頁
  if (papers.some((p) => p.translating)) setTimeout(() => {
    if (document.body.dataset.view === "ws" && curWs === ws) showWs(ws);
  }, 4000);
}

/** 背景對照翻譯的進度圈（只有圈，不顯示數字）；沒開始翻譯的論文不畫。 */
function trRing(p) {
  if (!p.tr_done && !p.translating) return "";
  const pct = Math.round(100 * Math.min(1, p.tr_done / (p.tr_total || 1)));
  return `<svg class="tr-ring${pct >= 100 ? " done" : ""}" viewBox="0 0 20 20" role="img" aria-label="對照翻譯 ${pct}%">
    <circle cx="10" cy="10" r="8"/><circle class="fill" cx="10" cy="10" r="8" pathLength="100" stroke-dasharray="${pct} 100"/></svg>`;
}
$("#wsPapers").onclick = async (e) => {
  const id = e.target.closest(".card")?.dataset.id;
  if (!id) return;
  if (!e.target.closest(".cdel")) return openPaper(id);
  if (curWs) await api(`/api/workspaces/${curWs.id}/papers/${id}`, { method: "DELETE" });
  else if (confirm("刪除這篇論文與所有標註？")) await api(`/api/papers/${id}`, { method: "DELETE" });
  else return;
  showWs();
};

/* ---------------- Workspace Wiki（docs/wiki.md） ---------------- */
let wsTab = "papers", wsPaperList = [], wikiSlug = null, wikiBusy = false;

function setWsTab(t) {
  wsTab = t;
  $$("#wsTabs button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.tab === t));
  $("#wsPapers").hidden = t !== "papers";
  $("#wsWiki").hidden = t !== "wiki";
  if (t === "wiki") loadWiki();
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
    const c = /^paper:([^#\s]+)#p(\d+)$/.exec(target);
    if (c) {
      const p = wsPaperList.find((x) => x.id === c[1]);
      const full = p ? p.title || p.filename : "論文";
      out.push(`<button class="wcite" data-pid="${escapeHTML(c[1])}" data-page="${c[2]}" title="${escapeHTML(full)}，第 ${c[2]} 頁"
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
    page.innerHTML = `<p class="cards-empty err">讀不到這個 workspace 的 Wiki：${escapeHTML(e.message)}</p>`;
    return;
  }
  if (curWs?.id !== ws.id) return;
  $("#wikiPending").textContent = w.pending ? `${w.pending} 篇論文待整理` : w.pages.length ? "所有論文都已整理" : "";
  $("#wikiUpdate").disabled = wikiBusy || !w.pending;
  $("#wikiList").innerHTML = w.pages.map((p) => `<li><button class="witem${p.slug === "index" ? " home" : ""}" data-slug="${escapeHTML(p.slug)}">${escapeHTML(p.title)}</button></li>`).join("");
  if (!w.pages.length) {
    page.innerHTML = `<div class="wempty"><h3>這個 workspace 還沒有 Wiki</h3>
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
  renderWiki($(".wbody", page), p.markdown || "");
}

$("#wsWiki").onclick = async (e) => {
  const l = e.target.closest("[data-slug]");
  if (l) {
    e.preventDefault();
    await showWikiPage(l.dataset.slug);
    const h = $("#wikiPage .wtitle");
    if (h) { h.focus({ preventScroll: true }); if (h.getBoundingClientRect().top < 60) h.scrollIntoView({ block: "start" }); }
    return;
  }
  const c = e.target.closest(".wcite");
  if (!c) return;
  try {
    await openPaper(c.dataset.pid);
    setTimeout(() => goToPage(+c.dataset.page - 1), 300);  // 同搜尋結果：等頁面排好再跳
  } catch (err) {
    showWs();
    $("#wikiProg").innerHTML = `<span class="err">開不了這篇論文：${escapeHTML(err.message)}（可能已經被刪除）</span>`;
  }
};

$("#wikiUpdate").onclick = async () => {
  const ws = curWs, prog = $("#wikiProg"), bar = $("#wikiBar");
  const here = () => curWs?.id === ws.id;
  wikiBusy = true;
  $("#wikiUpdate").disabled = true;
  prog.textContent = "開始整理…";
  bar.removeAttribute("value"); bar.hidden = false;
  try {
    await stream(`/api/workspaces/${ws.id}/wiki/update`, {}, (_, t) => {
      let m;
      try { m = JSON.parse(t); } catch { m = { msg: t }; }
      if (!here()) return;
      prog.textContent = m.msg || "";
      bar.hidden = false;
      if (m.total) { bar.max = m.total; bar.value = m.done || 0; }
    });
    if (here()) prog.textContent = "Wiki 已更新。";
  } catch (e) {
    if (here()) prog.innerHTML = `<span class="err">更新沒有完成：${escapeHTML(e.message)}。已整理好的論文會保留，再按一次「更新 Wiki」只做剩下的。</span>`;
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
$("#wsArxiv").onclick = () => {
  const url = prompt("arXiv 編號或 PDF 網址")?.trim();
  if (url) importArxiv(url, curWs?.id, $("#wsStatus"));
};
$("#wsAdd").onclick = async () => {
  const inWs = new Set($$("#wsPapers .card").map((c) => c.dataset.id));
  await loadLibrary();
  const rest = library.filter((p) => !inWs.has(p.id));
  $("#addList").innerHTML = rest.map((p) => `<li><button class="aitem" data-id="${escapeHTML(p.id)}">${escapeHTML(p.title || p.filename)}</button></li>`).join("")
    || '<li class="muted small">所有論文都已經在這個 workspace 裡了。</li>';
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
$("#wsRename").onclick = async () => {
  const name = prompt("workspace 名稱", curWs.name)?.trim();
  if (name && name !== curWs.name) showWs(await api(`/api/workspaces/${curWs.id}`, { method: "PATCH", body: { name } }));
};
$("#wsDelete").onclick = async () => {
  if (!confirm(`刪除 workspace「${curWs.name}」？裡面的論文不會刪除，仍在「全部論文」。`)) return;
  await api(`/api/workspaces/${curWs.id}`, { method: "DELETE" });
  showHome();
};
$("#wsBack").onclick = showHome;
$("#btnHome").onclick = showHome;
$("#btnSettings").onclick = async () => {
  $("#setAutoTranslate").checked = (await api("/api/me/settings")).auto_translate;
  $("#setDlg").showModal();
};
$("#setAutoTranslate").onchange = async (e) => {
  e.target.checked = (await api("/api/me/settings", { method: "PUT", body: { auto_translate: e.target.checked } })).auto_translate;
};
$("#setClose").onclick = () => $("#setDlg").close();
$("#btnLogout").onclick = async () => {
  await api("/api/auth/logout", { method: "POST" });
  history.replaceState(null, "", location.pathname);
  showLogin();
};

/* ---------------- 啟動 ---------------- */
// 401 時 api() 已經切到登入頁；其他錯誤（例如伺服器沒開）也退回登入頁顯示錯誤
api("/api/me").then(enter).catch(() => document.body.dataset.view || showLogin());
