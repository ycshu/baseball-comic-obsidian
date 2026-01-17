const GITHUB_OWNER = "ycshu";
const GITHUB_REPO  = "baseball-comic-obsidian";
const BRANCH       = "main";

const STUDENTS_DIR = "data/students";
const NAME_MAP_REL = "../data/student_name_map.json";

const GH_API_BASE = "https://api.github.com";
const contentsUrl = (path) =>
  `${GH_API_BASE}/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${path}?ref=${BRANCH}`;
const rawUrl = (path) =>
  `https://raw.githubusercontent.com/${GITHUB_OWNER}/${GITHUB_REPO}/${BRANCH}/${path}`;

function isStudentId(s) {
  return /^[A-Za-z0-9]{10}$/.test(s);
}

async function fetchJson(url) {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`Fetch failed: ${url} (${res.status})`);
  return await res.json();
}

async function fetchOptionalNameMap() {
  try { return await fetchJson(NAME_MAP_REL); } catch { return {}; }
}

async function listStudentFolders() {
  const items = await fetchJson(contentsUrl(STUDENTS_DIR));
  return items
    .filter(x => x.type === "dir" && isStudentId(x.name))
    .map(x => x.name)
    .sort((a, b) => a.localeCompare(b));
}

async function loadStudentIndex(studentId) {
  const path = `${STUDENTS_DIR}/${studentId}/index.json`;
  return await fetchJson(rawUrl(path));
}

function setStatus(html) {
  const el = document.getElementById("status");
  if (el) el.innerHTML = html;
}

// DATASETS: [{ studentId, displayName, index, ok, error? }]
const DATASETS = [];
let NAME_MAP = {};
let SELECTED_STUDENT_IDS = new Set(); // empty => all
let LAST_RESULTS = [];
let SELECTED_ITEMS = new Map();

function normalize(s) {
  return (s ?? "").toString().toLowerCase();
}

function stringifyTags(tags) {
  if (!tags) return "";
  if (Array.isArray(tags)) return tags.join(" ");
  return String(tags);
}

function buildSearchableText(item) {
  const fields = [
    item.name_zh, item.name_en, item.title, item.term,
    item.summary, item.explain_zh, item.comic_use,
    item.facts && item.facts.join(" "),
    item.story_hooks && item.story_hooks.join(" "),
    stringifyTags(item.tags),
    stringifyTags(item.roles),
    stringifyTags(item.era),
    item.datasetOwner
  ];
  return normalize(fields.filter(Boolean).join(" | "));
}

function tokenize(q) {
  return q.split(/\s+/).map(x => x.trim()).filter(Boolean);
}

function getActiveStudentIds() {
  const okIds = new Set(DATASETS.filter(d => d.ok).map(d => d.studentId));
  // SELECTED_STUDENT_IDS = empty => all
  if (SELECTED_STUDENT_IDS === null || SELECTED_STUDENT_IDS.size === 0) return okIds;
  const active = new Set();
  for (const id of SELECTED_STUDENT_IDS) if (okIds.has(id)) active.add(id);
  return active.size ? active : okIds;
}

function gatherItemsFromDatasets(activeIds) {
  const items = [];
  for (const ds of DATASETS) {
    if (!ds.ok) continue;
    if (!activeIds.has(ds.studentId)) continue;

    const ownerLabel = ds.displayName ? `${ds.displayName}（${ds.studentId}）` : ds.studentId;
    const index = ds.index || {};

    const pushItems = (arr, type) => {
      if (!Array.isArray(arr)) return;
      for (const it of arr) {
        const item = { ...it };
        item._type = type;
        item._studentId = ds.studentId;
        item._ownerLabel = ownerLabel;
        item._searchText = buildSearchableText({ ...item, datasetOwner: ownerLabel });
        const baseId = item.id || item.term || item.title || item.name_zh || item.name_en || Math.random().toString(36).slice(2);
        item._key = `${type}::${ds.studentId}::${baseId}`;
        items.push(item);
      }
    };

    pushItems(index.players, "player");
    pushItems(index.events, "event");
    pushItems(index.glossary, "glossary");
  }
  return items;
}

function scoreItem(item, tokens) {
  let score = 0;
  const text = item._searchText;
  for (const t of tokens) {
    const tt = normalize(t);
    if (!tt) continue;
    if (text.includes(tt)) score += 1;

    const nameBoost = normalize(item.name_zh || item.name_en || item.title || item.term);
    if (nameBoost.includes(tt)) score += 3;

    const aliases = normalize((item.aliases && item.aliases.join(" ")) || "");
    if (aliases.includes(tt)) score += 2;

    const tags = normalize(stringifyTags(item.tags));
    if (tags.includes(tt)) score += 2;
  }
  return score;
}

function search(q) {
  const tokens = tokenize(q);
  const activeIds = getActiveStudentIds();
  const pool = gatherItemsFromDatasets(activeIds);

  if (tokens.length === 0) {
    return { tokens, activeIds, items: [], totalPool: pool.length };
  }

  const scored = pool
    .map(it => ({ it, score: scoreItem(it, tokens) }))
    .filter(x => x.score > 0)
    .sort((a, b) => b.score - a.score);

  const top = scored.slice(0, 30).map(x => x.it);
  return { tokens, activeIds, items: top, totalPool: pool.length };
}

function el(id) { return document.getElementById(id); }

function renderScopeInfo(activeIds) {
  const scopeInfo = el("scopeInfo");
  if (!scopeInfo) return;

  const total = DATASETS.filter(d => d.ok).length;
  const selected = (SELECTED_STUDENT_IDS === null || SELECTED_STUDENT_IDS.size === 0) ? total : Math.min(activeIds.size, total);
  scopeInfo.innerHTML = `搜尋範圍：<span class="pill">${selected}/${total}</span> 份資料集（${selected === total ? "全班" : "已勾選"}）`;
}

function escapeHtml(s) {
  return (s ?? "").toString()
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderResults(result) {
  const resultsDiv = el("results");
  const summary = el("resultsSummary");
  if (!resultsDiv || !summary) return;

  resultsDiv.innerHTML = "";
  SELECTED_ITEMS.clear();
  LAST_RESULTS = result.items;

  if (result.tokens.length === 0) {
    summary.innerHTML = `請輸入關鍵字開始搜尋（目前可用資料池：${result.totalPool} 筆條目）。`;
    return;
  }

  summary.innerHTML = `命中 <strong>${result.items.length}</strong> 筆（顯示前 30），資料池共有 ${result.totalPool} 筆條目。`;

  for (const item of result.items) {
    const card = document.createElement("div");
    card.className = "card";

    const title = item._type === "player"
      ? (item.name_zh || item.name_en || "(未命名球員)")
      : item._type === "event"
        ? (item.title || "(未命名事件)")
        : (item.term || "(未命名術語)");

    const sub = document.createElement("div");
    sub.className = "muted small";
    sub.textContent = `${item._ownerLabel}｜${item._type}`;

    const head = document.createElement("div");
    head.className = "row";
    head.style.justifyContent = "space-between";

    const left = document.createElement("div");
    left.innerHTML = `<strong>${escapeHtml(title)}</strong>`;

    const right = document.createElement("div");
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.id = `sel-${item._key}`;
    cb.addEventListener("change", () => {
      if (cb.checked) SELECTED_ITEMS.set(item._key, item);
      else SELECTED_ITEMS.delete(item._key);
    });
    const lab = document.createElement("label");
    lab.htmlFor = cb.id;
    lab.textContent = "納入腳本";

    right.appendChild(cb);
    right.appendChild(document.createTextNode(" "));
    right.appendChild(lab);

    head.appendChild(left);
    head.appendChild(right);

    const meta = document.createElement("div");
    meta.className = "muted small";
    const tags = stringifyTags(item.tags);
    const era = stringifyTags(item.era);
    const roles = stringifyTags(item.roles);
    meta.textContent = [roles, era, tags].filter(Boolean).join("｜");

    const body = document.createElement("div");
    body.className = "small";
    const snippet = item.summary || item.explain_zh || (item.facts && item.facts[0]) || (item.story_hooks && item.story_hooks[0]) || "";
    body.textContent = snippet;

    card.appendChild(head);
    card.appendChild(sub);
    if (meta.textContent) card.appendChild(meta);
    if (body.textContent) card.appendChild(body);

    resultsDiv.appendChild(card);
  }
}

function renderProvidersWithNone() {
  const list = el("providersList");
  if (!list) return;
  list.innerHTML = "";

  const okDatasets = DATASETS.filter(d => d.ok);
  const ids = okDatasets.map(x => x.studentId);

  for (const ds of okDatasets) {
    const li = document.createElement("li");

    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = (SELECTED_STUDENT_IDS === null) ? false
               : (SELECTED_STUDENT_IDS.size === 0) ? true
               : SELECTED_STUDENT_IDS.has(ds.studentId);

    cb.addEventListener("change", () => {
      if (SELECTED_STUDENT_IDS === null) SELECTED_STUDENT_IDS = new Set();
      if (SELECTED_STUDENT_IDS.size === 0) SELECTED_STUDENT_IDS = new Set(ids);

      if (cb.checked) SELECTED_STUDENT_IDS.add(ds.studentId);
      else SELECTED_STUDENT_IDS.delete(ds.studentId);

      if (SELECTED_STUDENT_IDS.size === ids.length) SELECTED_STUDENT_IDS = new Set();
      if (SELECTED_STUDENT_IDS.size === 0) SELECTED_STUDENT_IDS = null;

      renderProvidersWithNone();
      renderScopeInfo(getActiveStudentIds());
    });

    const label = document.createElement("label");
    label.style.marginLeft = "8px";
    label.textContent = ds.displayName ? `${ds.displayName}（${ds.studentId}）` : ds.studentId;

    li.appendChild(cb);
    li.appendChild(label);
    list.appendChild(li);
  }

  const note = el("providersNote");
  if (note) {
    const totalOk = okDatasets.length;
    const selectedCount =
      (SELECTED_STUDENT_IDS === null) ? 0 :
      (SELECTED_STUDENT_IDS.size === 0) ? totalOk :
      SELECTED_STUDENT_IDS.size;
    note.textContent = `可用資料集：${totalOk}｜目前勾選：${selectedCount}（0 代表仍以全班搜尋）`;
  }
}

function renderProviders() {
  // 預設全班：empty set
  if (SELECTED_STUDENT_IDS !== null && SELECTED_STUDENT_IDS.size === 0) {
    renderProvidersWithNone();
  } else {
    renderProvidersWithNone();
  }

  const okDatasets = DATASETS.filter(d => d.ok);
  const ids = okDatasets.map(x => x.studentId);

  el("btnAll")?.addEventListener("click", () => {
    SELECTED_STUDENT_IDS = new Set(); // all
    renderProvidersWithNone();
    renderScopeInfo(getActiveStudentIds());
  });

  el("btnNone")?.addEventListener("click", () => {
    SELECTED_STUDENT_IDS = null; // none (但搜尋仍視為全班)
    renderProvidersWithNone();
    renderScopeInfo(getActiveStudentIds());
  });

  el("btnInvert")?.addEventListener("click", () => {
    let cur;
    if (SELECTED_STUDENT_IDS === null) cur = new Set();
    else if (SELECTED_STUDENT_IDS.size === 0) cur = new Set(ids);
    else cur = new Set(SELECTED_STUDENT_IDS);

    const inv = new Set(ids.filter(id => !cur.has(id)));
    SELECTED_STUDENT_IDS = (inv.size === ids.length) ? new Set() : (inv.size === 0 ? null : inv);

    renderProvidersWithNone();
    renderScopeInfo(getActiveStudentIds());
  });
}

function generateScriptMarkdown(query, selectedItemsArr, activeIds) {
  const selectedPlayers = selectedItemsArr.filter(x => x._type === "player");
  const selectedEvents  = selectedItemsArr.filter(x => x._type === "event");
  const selectedGloss   = selectedItemsArr.filter(x => x._type === "glossary");

  const providerLabels = DATASETS
    .filter(d => d.ok && activeIds.has(d.studentId))
    .map(d => d.displayName ? `${d.displayName}（${d.studentId}）` : d.studentId);

  const lines = [];
  lines.push(`# 台灣棒球漫畫生成腳本（給 ChatGPT / Gemini）`);
  lines.push(``);
  lines.push(`## 使用者查詢（關鍵字）`);
  lines.push(`- ${query || "(未提供)"}`);
  lines.push(``);
  lines.push(`## 資料來源範圍（資料提供者）`);
  lines.push(`- ${providerLabels.join("、") || "(無)"}`);
  lines.push(``);
  lines.push(`## 任務`);
  lines.push(`請根據下列「人物 / 事件 / 術語」素材，生成一篇 **8 格漫畫分鏡**（可調整為 6–12 格）。`);
  lines.push(`- 風格：熱血 + 幽默（可自然穿插科普）`);
  lines.push(`- 目標讀者：高中到大學初學者`);
  lines.push(`- 必須包含至少 1 個棒球知識點（術語解釋要自然，不要像教科書）`);
  lines.push(`- 避免使用未授權隊徽/商標；以「顏色/球衣描述」替代具體 Logo`);
  lines.push(``);
  lines.push(`## 素材（請務必使用）`);

  const block = (title, arr, fmtFn) => {
    lines.push(`### ${title}（${arr.length}）`);
    if (arr.length === 0) {
      lines.push(`- （未選）`);
      lines.push(``);
      return;
    }
    for (const it of arr.slice(0, 8)) lines.push(fmtFn(it));
    lines.push(``);
  };

  block("人物", selectedPlayers, (p) => {
    const name = p.name_zh || p.name_en || "(未命名)";
    const tags = stringifyTags(p.tags);
    const hooks = (p.story_hooks || []).slice(0, 2).join("；");
    return `- ${name}｜${p._ownerLabel}${tags ? `｜tags: ${tags}` : ""}${hooks ? `｜hooks: ${hooks}` : ""}`;
  });

  block("事件", selectedEvents, (e) => {
    const title = e.title || "(未命名)";
    const tags = stringifyTags(e.tags);
    const summary = e.summary || "";
    return `- ${title}｜${e._ownerLabel}${tags ? `｜tags: ${tags}` : ""}${summary ? `｜summary: ${summary}` : ""}`;
  });

  block("術語", selectedGloss, (g) => {
    const term = g.term || "(未命名)";
    const explain = g.explain_zh || "";
    return `- ${term}｜${g._ownerLabel}${explain ? `｜解釋: ${explain}` : ""}`;
  });

  lines.push(`## 輸出格式要求`);
  lines.push(`請輸出以下三段：`);
  lines.push(`1) **故事大綱**（100–200 字）`);
  lines.push(`2) **角色表**（角色、動機、衝突）`);
  lines.push(`3) **分鏡腳本**：每格請包含：畫面描述、角色對白、旁白（如有）、鏡位/構圖、情緒`);
  lines.push(``);
  lines.push(`## 額外要求（生成圖片提示）`);
  lines.push(`最後請為每一格提供「圖片生成提示詞」(prompt)，包含：場景、人物外觀一致性描述、動作、鏡位、光線、漫畫風格。`);

  return lines.join("\n");
}

function wireEvents() {
  el("btnSearch")?.addEventListener("click", () => runSearch());
  el("q")?.addEventListener("keydown", (e) => { if (e.key === "Enter") runSearch(); });

  el("btnClear")?.addEventListener("click", () => {
    el("q").value = "";
    el("results").innerHTML = "";
    el("resultsSummary").textContent = "";
    el("scriptOut").value = "";
    SELECTED_ITEMS.clear();
    LAST_RESULTS = [];
  });

  el("btnGenerate")?.addEventListener("click", () => {
    const q = el("q").value.trim();
    const activeIds = getActiveStudentIds();

    let selectedArr = Array.from(SELECTED_ITEMS.values());
    if (selectedArr.length === 0 && LAST_RESULTS.length > 0) selectedArr = LAST_RESULTS.slice(0, 6);

    el("scriptOut").value = generateScriptMarkdown(q, selectedArr, activeIds);
  });

  el("btnCopy")?.addEventListener("click", async () => {
    const t = el("scriptOut").value;
    if (!t) return;
    try {
      await navigator.clipboard.writeText(t);
      setStatus(`已複製腳本到剪貼簿。<span class="muted">（請貼到 ChatGPT / Gemini）</span>`);
    } catch {
      setStatus(`<span class="error">複製失敗</span>：請手動全選複製。`);
    }
  });
}

function runSearch() {
  const q = el("q").value.trim();
  const result = search(q);
  renderScopeInfo(result.activeIds);
  renderResults(result);
}

async function init() {
  setStatus(`正在載入學號→姓名對應表…`);
  NAME_MAP = await fetchOptionalNameMap();

  setStatus(`正在掃描 GitHub：<code>${STUDENTS_DIR}/</code>（分支：<code>${BRANCH}</code>）…`);
  const studentIds = await listStudentFolders();

  if (studentIds.length === 0) {
    setStatus(`<span class="error">未掃描到任何學生資料夾。</span> 請確認 <code>${STUDENTS_DIR}/&lt;10碼學號&gt;/</code> 已存在於 <code>${BRANCH}</code>。`);
    return;
  }

  setStatus(`掃描到 <strong>${studentIds.length}</strong> 位資料提供者，正在載入每位的 <code>index.json</code>…`);

  for (const sid of studentIds) {
    const displayName = NAME_MAP[sid] || "";
    try {
      const index = await loadStudentIndex(sid);
      DATASETS.push({ studentId: sid, displayName, index, ok: true });
    } catch (e) {
      DATASETS.push({ studentId: sid, displayName, index: null, ok: false, error: String(e) });
    }
  }

  const okN = DATASETS.filter(d => d.ok).length;
  setStatus(`完成載入：<strong>${okN}</strong> 份可用資料集（以 <code>${BRANCH}</code> 分支為準）。`);

  SELECTED_STUDENT_IDS = new Set(); // all
  renderProvidersWithNone();
  renderProviders();
  renderScopeInfo(getActiveStudentIds());
  wireEvents();
}

init().catch(err => {
  console.error(err);
  setStatus(`<span class="error">初始化失敗：</span> ${err.message}`);
});

