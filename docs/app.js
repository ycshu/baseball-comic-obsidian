// ===== Repo configuration =====
const GITHUB_OWNER = "ycshu";
const GITHUB_REPO  = "baseball-comic-obsidian";
const BRANCH       = "main";

const STUDENTS_DIR  = "data/students";
const NAME_MAP_PATH = "data/student_name_map.json";

// ===== Utilities =====
function isStudentId(name) {
  return /^[A-Za-z0-9]{9,10}$/.test(name);
}

function ghApi(path) {
  return `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${path}?ref=${BRANCH}`;
}

async function fetchJson(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

function decodeContent(j) {
  const b64 = (j.content || "").replace(/\n/g, "");
  return decodeURIComponent(escape(atob(b64)));
}

function el(id){ return document.getElementById(id); }

function djb2(str){
  let h = 5381;
  for(let i=0;i<str.length;i++){
    h = ((h << 5) + h) + str.charCodeAt(i);
    h = h & 0xffffffff;
  }
  return (h >>> 0).toString(16);
}

function itemLabel(item){
  return item.name_zh || item.title || item.term || item.name_en || item.id || "(未命名)";
}

// ===== App State =====
let nameMap = {};
let datasets = [];     // [{owner, path, data}]
let lastHits = [];     // [{key, owner, sec, item}]
let selectedHitKeys = new Set(); // keys selected from search results

// ===== Loaders =====
async function loadNameMap(){
  try{
    const j = await fetchJson(ghApi(NAME_MAP_PATH));
    nameMap = JSON.parse(decodeContent(j));
  }catch(e){
    console.warn("Name map load failed:", e);
    nameMap = {};
  }
}

async function scanStudents(){
  const listing = await fetchJson(ghApi(STUDENTS_DIR));
  const dirs = listing.filter(x => x.type === "dir" && isStudentId(x.name));
  return dirs.map(d => d.name);
}

async function loadDataset(studentId){
  const path = `${STUDENTS_DIR}/${studentId}/index.json`;
  const j = await fetchJson(ghApi(path));
  const data = JSON.parse(decodeContent(j));
  return { owner: studentId, path, data };
}

// ===== Providers UI =====
function renderProviders(){
  const ul = el("providersList");
  ul.innerHTML = "";
  datasets.forEach(ds=>{
    const li = document.createElement("li");
    const id = ds.owner;
    const label = nameMap[id] ? `${nameMap[id]}（${id}）` : id;
    li.innerHTML = `<label><input type="checkbox" data-owner="${id}" checked> ${label}</label>`;
    ul.appendChild(li);
  });
  el("providersNote").textContent = `共 ${datasets.length} 位`;
}

function selectedOwners(){
  return Array.from(document.querySelectorAll("#providersList input[type=checkbox]:checked"))
    .map(x=>x.dataset.owner);
}

// ===== Search + Results UI (with checkboxes) =====
function buildHits(q){
  const owners = new Set(selectedOwners());
  const hits = [];
  datasets.forEach(ds=>{
    if(!owners.has(ds.owner)) return;
    ["players","events","glossary"].forEach(sec=>{
      (ds.data[sec]||[]).forEach(item=>{
        const blob = JSON.stringify(item);
        if(blob.includes(q)){
          const key = `${ds.owner}|${sec}|${djb2(blob)}`;
          hits.push({ key, owner: ds.owner, sec, item });
        }
      });
    });
  });
  return hits;
}

function renderResults(hits){
  lastHits = hits;
  const box = el("results");
  box.innerHTML = "";
  el("resultsSummary").textContent = `找到 ${hits.length} 筆（可勾選要納入腳本的項目）`;

  // Default: auto-select all hits
  selectedHitKeys = new Set(hits.map(h => h.key));

  hits.forEach(h=>{
    const d = document.createElement("div");
    d.className = "card small";
    const label = `[${h.owner}] ${h.sec} :: ${itemLabel(h.item)}`;
    d.innerHTML = `
      <label style="display:flex;gap:10px;align-items:center;">
        <input type="checkbox" class="hitCheck" data-key="${h.key}" checked>
        <span>${label}</span>
      </label>
    `;
    box.appendChild(d);
  });

  box.querySelectorAll("input.hitCheck").forEach(cb=>{
    cb.addEventListener("change", (e)=>{
      const k = e.target.dataset.key;
      if(e.target.checked) selectedHitKeys.add(k);
      else selectedHitKeys.delete(k);
    });
  });
}

function resultsSelectAll(val){
  const box = el("results");
  box.querySelectorAll("input.hitCheck").forEach(cb=>{
    cb.checked = val;
    const k = cb.dataset.key;
    if(val) selectedHitKeys.add(k);
    else selectedHitKeys.delete(k);
  });
}

// ===== Script generation (from selected search hits) =====
function generateScriptFromSelectedHits(){
  if(!lastHits.length){
    el("scriptOut").value = "尚無搜尋結果可用。請先搜尋，再勾選要納入腳本的項目。";
    return;
  }
  const picked = lastHits.filter(h => selectedHitKeys.has(h.key));

  const byOwner = new Map();
  picked.forEach(h=>{
    if(!byOwner.has(h.owner)) byOwner.set(h.owner, []);
    byOwner.get(h.owner).push(h);
  });

  const parts = [];
  parts.push(`# 棒球漫畫腳本素材（由查詢結果生成）`);
  parts.push(`- 來源資料集：${Array.from(byOwner.keys()).length} 位提供者`);
  parts.push(`- 納入條目：${picked.length} 筆`);
  parts.push("");

  Array.from(byOwner.keys()).sort().forEach(owner=>{
    const display = nameMap[owner] ? `${nameMap[owner]}（${owner}）` : owner;
    parts.push(`## 資料提供者：${display}`);
    const items = byOwner.get(owner);
    const secOrder = ["players","events","glossary"];
    secOrder.forEach(sec=>{
      const group = items.filter(x=>x.sec===sec);
      if(!group.length) return;
      parts.push(`### ${sec}`);
      group.forEach(x=>{
        const label = itemLabel(x.item);
        const summary = x.item.summary || x.item.explain_zh || x.item.description || "";
        parts.push(`- ${label}${summary ? `：${summary}` : ""}`);
      });
      parts.push("");
    });
  });

  parts.push("## 生成指令（可貼給 ChatGPT/Gemini）");
  parts.push("請根據以上素材，產生一段 6–10 格的棒球漫畫分鏡腳本，包含：場景、人物對白、動作、鏡頭描述。");
  parts.push("若素材不足，請合理補齊，但不得捏造真實人物的敏感個資。");

  el("scriptOut").value = parts.join("\n");
}

// ===== Init =====
async function init(){
  try{
    await loadNameMap();
    const ids = await scanStudents();
    const loaded = [];
    for(const id of ids){
      try{ loaded.push(await loadDataset(id)); }
      catch(e){ console.warn("Dataset load failed:", id, e); }
    }
    datasets = loaded;
    el("status").textContent = `完成載入：${datasets.length} 份可用資料集`;
    renderProviders();
  }catch(e){
    console.error(e);
    el("status").textContent = "載入失敗";
  }
}

document.addEventListener("DOMContentLoaded", ()=>{
  init();

  el("btnSearch").onclick = ()=>{
    const q = el("q").value.trim();
    renderResults(q ? buildHits(q) : []);
  };

  el("btnClear").onclick = ()=>{
    el("q").value = "";
    el("results").innerHTML = "";
    el("resultsSummary").textContent = "";
    lastHits = [];
    selectedHitKeys = new Set();
  };

  // Generate from selected search hits
  el("btnGenerate").onclick = generateScriptFromSelectedHits;

  el("btnCopy").onclick = ()=>{
    el("scriptOut").select();
    document.execCommand("copy");
  };

  // Provider selection helpers
  el("btnAll").onclick = ()=>document.querySelectorAll("#providersList input").forEach(x=>x.checked=true);
  el("btnNone").onclick = ()=>document.querySelectorAll("#providersList input").forEach(x=>x.checked=false);
  el("btnInvert").onclick = ()=>document.querySelectorAll("#providersList input").forEach(x=>x.checked=!x.checked);

  // Optional result selection buttons (if present in HTML)
  const rAll = document.getElementById("btnResultsAll");
  const rNone = document.getElementById("btnResultsNone");
  if(rAll)  rAll.onclick  = ()=>resultsSelectAll(true);
  if(rNone) rNone.onclick = ()=>resultsSelectAll(false);
});
