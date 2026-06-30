// Value / ROI view. Renders the per-task by-hand-baseline vs agentic-cost
// comparison from usage.json v2 (window.USAGE) using console-side labor rates
// (window.LABOR_RATES). Person-hours is primary; $ is a derived overlay applied
// HERE (never in the committed data). Headlines lead with the conservative `min`.
(function () {
  const U = window.USAGE || {};
  const RATES = window.LABOR_RATES || {};
  const CUR = window.CURRENCY || "USD";
  const tasks = U.tasks || {};

  const usd = n => new Intl.NumberFormat(undefined, { style: "currency", currency: CUR,
    maximumFractionDigits: n >= 100 ? 0 : 2 }).format(n || 0);
  const hrs = n => (Math.round((n || 0) * 10) / 10).toLocaleString();
  const rateFor = p => (p in RATES ? RATES[p] : (RATES.default || 0));

  // Anonymize people: map each task_folder ("ben") to a stable "Member N",
  // keeping the task number visible (value is task-scoped, people are not ranked).
  const folders = [...new Set(Object.keys(tasks).map(r => r.split("/")[0]))].sort();
  const memberOf = {};
  folders.forEach((f, i) => { memberOf[f] = "Member " + (i + 1); });

  // Per-task rows (only tasks that carry a by-hand estimate; "_unattributed" has none).
  const rows = [];
  for (const [ref, t] of Object.entries(tasks)) {
    const est = t.estimate;
    if (!est) continue;
    const [tf, id] = [ref.split("/")[0], ref.split("/").slice(1).join("/")];
    // by-hand $ from per-persona hours × that persona's loaded rate (min & max bands)
    let manMin = 0, manMax = 0;
    for (const [p, h] of Object.entries(est.by_persona || {})) {
      manMin += (h.min || 0) * rateFor(p);
      manMax += (h.max || 0) * rateFor(p);
    }
    const agentic = t.cost || 0;
    rows.push({
      label: memberOf[tf] + " · " + id,
      sessions: t.sessions || 0,
      agentic,
      hMin: est.manual_hours?.min || 0, hMax: est.manual_hours?.max || 0,
      manMin, manMax,
      // Leverage = conservative by-hand $ floor ÷ measured agentic $.
      lev: agentic > 0 ? manMin / agentic : null,
      conf: est.confidence_mix || {},
    });
  }
  rows.sort((a, b) => b.manMin - a.manMin);

  // Program totals (estimated tasks only).
  const T = rows.reduce((a, r) => ({
    hMin: a.hMin + r.hMin, hMax: a.hMax + r.hMax,
    manMin: a.manMin + r.manMin, manMax: a.manMax + r.manMax,
    agentic: a.agentic + r.agentic,
  }), { hMin: 0, hMax: 0, manMin: 0, manMax: 0, agentic: 0 });
  const progLev = T.agentic > 0 ? T.manMin / T.agentic : null;

  // ---- hero cards (headline the conservative low end) ----
  const hero = document.getElementById("vv-hero");
  if (hero) {
    const card = (k, v, cls) => `<div class="vv-card"><div class="k">${k}</div>` +
      `<div class="v ${cls || ""}">${v}</div></div>`;
    hero.innerHTML =
      card("By-hand effort", `${hrs(T.hMin)}–${hrs(T.hMax)} <small>person-hrs</small>`, "vv-hero") +
      card("By-hand cost", `${usd(T.manMin)}–${usd(T.manMax)}`) +
      card("Agentic cost (tokens)", usd(T.agentic)) +
      card("Leverage", progLev ? `${progLev.toFixed(0)}×<small> (≥, conservative)</small>` : "—", "vv-hero") +
      card("Tasks valued", String(rows.length));
  }

  // ---- per-task table ----
  const confSpan = c => Object.entries(c).map(([k, n]) =>
    `<span class="vv-conf-${k}">${n}${k[0]}</span>`).join(" ");
  const tb = document.querySelector("#vv-tbl tbody");
  if (tb) {
    tb.innerHTML = rows.map(r => `<tr>
      <td>${r.label}<span class="vv-badge measured">measured $</span><span class="vv-badge est">est. hrs</span></td>
      <td class="vv-mono">${r.sessions}</td>
      <td class="vv-mono">${usd(r.agentic)}</td>
      <td class="vv-mono">${hrs(r.hMin)}–${hrs(r.hMax)}</td>
      <td class="vv-mono">${usd(r.manMin)}–${usd(r.manMax)}</td>
      <td class="vv-mono">${r.lev ? r.lev.toFixed(0) + "×" : "—"}</td>
      <td class="vv-mono">${confSpan(r.conf)}</td>
    </tr>`).join("");
  }
  const tf = document.querySelector("#vv-tbl tfoot");
  if (tf) {
    tf.innerHTML = `<tr>
      <td>Total (${rows.length} task${rows.length === 1 ? "" : "s"})</td>
      <td class="vv-mono">${rows.reduce((a, r) => a + r.sessions, 0)}</td>
      <td class="vv-mono">${usd(T.agentic)}</td>
      <td class="vv-mono">${hrs(T.hMin)}–${hrs(T.hMax)}</td>
      <td class="vv-mono">${usd(T.manMin)}–${usd(T.manMax)}</td>
      <td class="vv-mono">${progLev ? progLev.toFixed(0) + "×" : "—"}</td>
      <td></td></tr>`;
  }

  const disc = document.getElementById("vv-disc");
  if (disc) {
    disc.textContent =
      "By-hand hours are ranged per-task estimates (method-versioned, persona-tagged); " +
      "confidence shown as counts of high/med/low todos. By-hand $ = persona hours × console " +
      "labor_rates ([VERIFY] demo placeholders). Leverage = conservative by-hand $ floor ÷ " +
      "measured agentic token $ — indicative, not subscription billing. Tasks without a " +
      "recorded estimate (incl. _unattributed overhead) are omitted from this view.";
  }
})();
