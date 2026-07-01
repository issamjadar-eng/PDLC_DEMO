// Value / ROI tab. Headline = HOURS SAVED = by-hand estimate (ranged) − agentic time.
// Category = by-hand specialist persona(s). Agentic cost = measured token $.
// A page-level date range (All / 30 / 60 / 90 days) filters EVERY section (hero,
// category cards, table) by each task's last-updated date. Reads usage.json v2.
(function () {
  const U = window.USAGE || {};
  const CUR = window.CURRENCY || "USD";
  const tasks = U.tasks || {};
  const $ = id => document.getElementById(id);

  const usd = n => new Intl.NumberFormat(undefined, { style: "currency", currency: CUR, maximumFractionDigits: (n || 0) >= 100 ? 0 : 2 }).format(n || 0);
  const hrs = n => (Math.round((n || 0) * 10) / 10).toLocaleString();
  const hrs0 = n => Math.round(n || 0).toLocaleString();   // whole hours (category cards)
  const usd0 = n => new Intl.NumberFormat(undefined, { style: "currency", currency: CUR, maximumFractionDigits: 0 }).format(n || 0);
  const rng = o => o ? `${hrs(o.min)}–${hrs(o.max)}` : "—";
  const pctRange = (sv, bh) => {
    if (!sv || !bh || !bh.min || !bh.max) return null;
    const lo = Math.round(sv.min / bh.min * 100), hi = Math.round(sv.max / bh.max * 100);
    const a = Math.min(lo, hi), b = Math.max(lo, hi);
    return a === b ? `${a}%` : `${a}–${b}%`;
  };
  const esc = s => (s || "").replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
  const shortTitle = t => {
    if (!t) return "";
    const w = t.replace(/\(.*?\)/g, "").replace(/[:—-]+/g, " ").split(/\s+/).filter(Boolean);
    return esc(w.slice(0, 5).join(" "));
  };

  // anonymize people; keep task number (value is task-scoped, people aren't ranked)
  const folders = [...new Set(Object.keys(tasks).map(r => r.split("/")[0]))].sort();
  const memberOf = {};
  folders.forEach((f, i) => { memberOf[f] = "Member " + (i + 1); });

  const rows = [];
  for (const [ref, t] of Object.entries(tasks)) {
    const e = t.estimate;
    if (!e) continue;
    const id = ref.split("/").slice(1).join("/");
    const cats = e.personas || [];
    rows.push({
      label: memberOf[ref.split("/")[0]] + " · " + id,
      title: e.title, updated: e.updated || "", retro: !!e.retrospective,
      personas: cats, category: cats.length ? cats.slice(0, 3).join(", ") + (cats.length > 3 ? "…" : "") : "—",
      agentic_h: e.agentic_hours, byhand: e.manual_hours, saved: e.hours_saved,
      by_persona: e.by_persona || {}, pct: pctRange(e.hours_saved, e.manual_hours),
      cost: t.cost || 0, savedMin: e.hours_saved ? e.hours_saved.min : -1,
    });
  }

  // ---- page-level date range ----
  let rangeDays = 0;                       // 0 = all
  const nowMs = Date.now();
  const inRange = r => {
    if (!rangeDays) return true;
    const cut = new Date(nowMs - rangeDays * 864e5).toISOString().slice(0, 10);
    return r.updated && r.updated >= cut;
  };

  // ---- table-only filters/sort (on top of the range) ----
  const state = { q: "", cat: "", meas: false, key: "updated", dir: -1, pageSize: 50, page: 0 };
  const numKey = { agentic: r => r.agentic_h || 0, byhand: r => (r.byhand ? r.byhand.min : 0), saved: r => r.savedMin, cost: r => r.cost };
  const strKey = { title: r => (r.title || "").toLowerCase(), updated: r => r.updated || "", category: r => r.category.toLowerCase() };
  const keep = r => {
    if (state.meas && r.retro) return false;
    if (state.cat && !(r.personas || []).includes(state.cat)) return false;
    if (state.q && !`${r.title} ${r.label} ${r.category}`.toLowerCase().includes(state.q)) return false;
    return true;
  };
  const sortRows = arr => {
    const f = numKey[state.key] || strKey[state.key], isNum = !!numKey[state.key];
    return arr.slice().sort((a, b) => (isNum ? (f(a) - f(b)) : String(f(a)).localeCompare(String(f(b)))) * state.dir);
  };
  const fmtRow = r => `<tr>
    <td><div class="vv-title">${shortTitle(r.title) || r.label}${r.retro ? '<span class="vv-badge est">retro</span>' : ''}</div><div class="vv-id">${r.label}</div></td>
    <td class="vv-mono">${r.updated || "—"}</td>
    <td class="vv-cat">${r.category}</td>
    <td class="vv-mono">${r.agentic_h != null ? hrs(r.agentic_h) : "—"}</td>
    <td class="vv-mono">${rng(r.byhand)}</td>
    <td class="vv-hero"><span class="vv-mono">${r.saved ? rng(r.saved) : "—"}</span>${r.pct ? `<div class="vv-pct">${r.pct}</div>` : ""}</td>
    <td class="vv-mono">${usd(r.cost)}</td></tr>`;

  const sums = list => list.reduce((a, r) => ({
    bMin: a.bMin + (r.byhand ? r.byhand.min : 0), bMax: a.bMax + (r.byhand ? r.byhand.max : 0),
    sMin: a.sMin + (r.saved ? r.saved.min : 0), sMax: a.sMax + (r.saved ? r.saved.max : 0),
    ag: a.ag + (r.agentic_h || 0), cost: a.cost + r.cost,
  }), { bMin: 0, bMax: 0, sMin: 0, sMax: 0, ag: 0, cost: 0 });

  let rf = rows.slice();  // range-filtered set (drives hero + cats + table)

  function renderHero(list) {
    const hero = $("vv-hero"); if (!hero) return;
    const T = sums(list);
    const pct = pctRange({ min: T.sMin, max: T.sMax }, { min: T.bMin, max: T.bMax });
    const card = (k, v, cls) => `<div class="vv-card"><div class="k">${k}</div><div class="v ${cls || ""}">${v}</div></div>`;
    hero.innerHTML =
      card("Person-hours saved", (T.sMin || T.sMax) ? `${hrs(T.sMin)}–${hrs(T.sMax)} <small>hrs${pct ? " · " + pct + " of by-hand" : ""}</small>` : "—", "vv-hero") +
      card("By-hand effort", `${hrs(T.bMin)}–${hrs(T.bMax)} <small>hrs</small>`) +
      card("Agentic time", `${hrs(T.ag)} <small>hrs (est.)</small>`) +
      card("Agentic cost", `${usd(T.cost)} <small>tokens</small>`) +
      card("Tasks valued", String(list.length));
  }

  function renderCats(list) {
    const catEl = $("vv-cats"); if (!catEl) return;
    const cats = {};
    for (const r of list) {
      const bp = r.by_persona; if (!bp) continue;
      const denom = Object.values(bp).reduce((a, h) => a + (h.max || 0), 0) || 1;
      for (const [p, h] of Object.entries(bp)) {
        const w = (h.max || 0) / denom;
        const c = cats[p] || (cats[p] = { bhMin: 0, bhMax: 0, svMin: 0, svMax: 0, ag: 0, cost: 0, tasks: 0 });
        c.bhMin += h.min || 0; c.bhMax += h.max || 0;
        if (r.saved) { c.svMin += (r.saved.min || 0) * w; c.svMax += (r.saved.max || 0) * w; }
        c.ag += (r.agentic_h || 0) * w; c.cost += (r.cost || 0) * w; c.tasks += 1;
      }
    }
    // "All" aggregate card — true totals (each task once), not the per-persona split.
    const A = sums(list);
    const allPct = pctRange({ min: A.sMin, max: A.sMax }, { min: A.bMin, max: A.bMax });
    const allCard = `<div class="vv-catcard vv-catall">
      <div class="vv-catname">All categories<span class="vv-catn"> · ${list.length} task${list.length === 1 ? "" : "s"}</span></div>
      <div class="vv-catrow"><span>Hours saved</span><span class="vv-mono"><span class="vv-hero">${hrs0(A.sMin)}–${hrs0(A.sMax)}</span>${allPct ? ` <span class="vv-catpct">${allPct}</span>` : ""}</span></div>
      <div class="vv-catrow"><span>By-hand effort</span><span class="vv-mono">${hrs0(A.bMin)}–${hrs0(A.bMax)} hrs</span></div>
      <div class="vv-catrow"><span>Agentic time</span><span class="vv-mono">${hrs0(A.ag)} hrs</span></div>
      <div class="vv-catrow"><span>Agentic cost</span><span class="vv-mono">${usd0(A.cost)}</span></div>
    </div>`;
    const html = Object.entries(cats).sort((a, b) => b[1].svMin - a[1].svMin).map(([p, c]) => {
      const share = list.length ? Math.round(c.tasks / list.length * 100) : 0;
      const catPct = pctRange({ min: c.svMin, max: c.svMax }, { min: c.bhMin, max: c.bhMax });
      return `<div class="vv-catcard">
        <div class="vv-catname">${p}<span class="vv-catn"> · ${c.tasks} task${c.tasks === 1 ? "" : "s"} · ${share}% of tasks</span></div>
        <div class="vv-catrow"><span>Hours saved</span><span class="vv-mono"><span class="vv-hero">${hrs0(c.svMin)}–${hrs0(c.svMax)}</span>${catPct ? ` <span class="vv-catpct">${catPct}</span>` : ""}</span></div>
        <div class="vv-catrow"><span>By-hand effort</span><span class="vv-mono">${hrs0(c.bhMin)}–${hrs0(c.bhMax)} hrs</span></div>
        <div class="vv-catrow"><span>Agentic time</span><span class="vv-mono">${hrs0(c.ag)} hrs</span></div>
        <div class="vv-catrow"><span>Agentic cost</span><span class="vv-mono">${usd0(c.cost)}</span></div>
      </div>`;
    }).join("");
    catEl.innerHTML = list.length ? (allCard + html) : '<div style="color:var(--muted,#8b93a7);font-size:12px">No tasks in this range.</div>';
  }

  function renderTable(list) {
    const tb = document.querySelector("#vv-tbl tbody"), tf = document.querySelector("#vv-tbl tfoot");
    const filtered = sortRows(list.filter(keep));
    const total = filtered.length, ps = state.pageSize;   // ps 0 = all
    const pageCount = ps ? Math.max(1, Math.ceil(total / ps)) : 1;
    state.page = Math.min(Math.max(0, state.page), pageCount - 1);
    const slice = ps ? filtered.slice(state.page * ps, state.page * ps + ps) : filtered;
    if (tb) tb.innerHTML = slice.length ? slice.map(fmtRow).join("")
      : '<tr><td colspan="7" style="text-align:center;color:var(--muted,#8b93a7);padding:16px">No tasks match the filter.</td></tr>';
    const T = sums(filtered);   // footer totals span ALL filtered rows, not just the page
    const fPct = pctRange({ min: T.sMin, max: T.sMax }, { min: T.bMin, max: T.bMax });
    if (tf) tf.innerHTML = `<tr>
      <td>Total (${total} task${total === 1 ? "" : "s"})</td><td></td><td></td>
      <td class="vv-mono">${hrs(T.ag)}</td>
      <td class="vv-mono">${hrs(T.bMin)}–${hrs(T.bMax)}</td>
      <td class="vv-hero"><span class="vv-mono">${hrs(T.sMin)}–${hrs(T.sMax)}</span>${fPct ? `<div class="vv-pct">${fPct}</div>` : ""}</td>
      <td class="vv-mono">${usd(T.cost)}</td></tr>`;
    const pg = $("vv-pageinfo");
    if (pg) pg.textContent = total === 0 ? "No tasks"
      : (ps ? `Showing ${state.page * ps + 1}–${Math.min(total, (state.page + 1) * ps)} of ${total}` : `Showing all ${total}`);
    if ($("vv-prev")) $("vv-prev").disabled = !ps || state.page <= 0;
    if ($("vv-next")) $("vv-next").disabled = !ps || state.page >= pageCount - 1;
    document.querySelectorAll('#vv-tbl th[data-k]').forEach(th => {
      const on = th.dataset.k === state.key;
      th.classList.toggle('vv-sorted', on);
      const a = th.querySelector('.vv-arrow'); if (a) a.textContent = on ? (state.dir < 0 ? '▼' : '▲') : '';
    });
  }

  function renderAll() { rf = rows.filter(inRange); renderHero(rf); renderCats(rf); renderTable(rf); }

  const repage = () => { state.page = 0; renderTable(rf); };
  // category select (stable options from all rows)
  const catSel = $("vv-catfilter");
  if (catSel) {
    const all = [...new Set(rows.flatMap(r => r.personas || []))].sort();
    catSel.innerHTML = '<option value="">All categories</option>' + all.map(c => `<option value="${c}">${c}</option>`).join("");
    catSel.addEventListener("change", e => { state.cat = e.target.value; repage(); });
  }
  if ($("vv-search")) $("vv-search").addEventListener("input", e => { state.q = e.target.value.toLowerCase().trim(); repage(); });
  if ($("vv-measonly")) $("vv-measonly").addEventListener("change", e => { state.meas = e.target.checked; repage(); });
  if ($("vv-pagesize")) $("vv-pagesize").addEventListener("change", e => { state.pageSize = +e.target.value; repage(); });
  if ($("vv-prev")) $("vv-prev").addEventListener("click", () => { state.page--; renderTable(rf); });
  if ($("vv-next")) $("vv-next").addEventListener("click", () => { state.page++; renderTable(rf); });
  document.querySelectorAll('#vv-tbl th[data-k]').forEach(th => th.addEventListener('click', () => {
    const k = th.dataset.k;
    if (state.key === k) state.dir = -state.dir; else { state.key = k; state.dir = numKey[k] ? -1 : 1; }
    repage();
  }));
  document.querySelectorAll('.vv-range [data-days]').forEach(b => b.addEventListener('click', () => {
    rangeDays = +b.dataset.days; state.page = 0;
    document.querySelectorAll('.vv-range [data-days]').forEach(x => x.classList.toggle('active', x === b));
    renderAll();
  }));

  const disc = $("vv-disc");
  if (disc) disc.textContent =
    "Hours saved = by-hand person-hour estimate (ranged) − agentic time (estimate of how long it " +
    "actually took us); % = saved ÷ by-hand. Category = the by-hand specialist persona(s). Agentic cost = " +
    "measured token $ (real Anthropic list rates; indicative). The date range filters every section by " +
    "each task's last-updated date. Tasks with no recorded estimate (incl. _unattributed) are omitted.";

  renderAll();
})();
