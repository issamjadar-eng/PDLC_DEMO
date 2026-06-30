// Value / ROI tab. The headline is HOURS SAVED = by-hand person-hour estimate
// (ranged) minus how long it actually took us (agentic_hours). Category = the
// by-hand specialist persona(s). Agentic cost = measured token $ (real rates).
// Reads usage.json v2 (window.USAGE) + console labor rates (window.LABOR_RATES).
(function () {
  const U = window.USAGE || {};
  const CUR = window.CURRENCY || "USD";
  const tasks = U.tasks || {};
  const vs = U.value_summary || {};

  const usd = n => new Intl.NumberFormat(undefined, { style: "currency", currency: CUR,
    maximumFractionDigits: (n || 0) >= 100 ? 0 : 2 }).format(n || 0);
  const hrs = n => (Math.round((n || 0) * 10) / 10).toLocaleString();
  const rng = o => o ? `${hrs(o.min)}–${hrs(o.max)}` : "—";
  const confLabel = m => !m ? "—" : (m.low ? "low" : (m.med ? "med" : (m.high ? "high" : "—")));

  // Anonymize people; keep the task number (value is task-scoped, people aren't ranked).
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
      category: cats.length ? cats.slice(0, 3).join(", ") + (cats.length > 3 ? "…" : "") : "—",
      agentic_h: e.agentic_hours,
      byhand: e.manual_hours,
      saved: e.hours_saved,
      cost: t.cost || 0,
      conf: confLabel(e.confidence_mix),
      savedMin: e.hours_saved ? e.hours_saved.min : -1,
    });
  }
  rows.sort((a, b) => b.savedMin - a.savedMin);

  const totCost = rows.reduce((a, r) => a + r.cost, 0);

  // ---- hero cards (headline hours saved, conservative low end) ----
  const hero = document.getElementById("vv-hero");
  if (hero) {
    const card = (k, v, cls) => `<div class="vv-card"><div class="k">${k}</div>` +
      `<div class="v ${cls || ""}">${v}</div></div>`;
    hero.innerHTML =
      card("Person-hours saved", vs.hours_saved ? `${rng(vs.hours_saved)} <small>hrs</small>` : "—", "vv-hero") +
      card("By-hand effort", `${rng(vs.manual_hours)} <small>hrs</small>`) +
      card("Agentic time", `${hrs(vs.agentic_hours)} <small>hrs (est.)</small>`) +
      card("Agentic cost", `${usd(totCost)} <small>tokens</small>`) +
      card("Tasks valued", String(rows.length));
  }

  // ---- per-task table ----
  const tb = document.querySelector("#vv-tbl tbody");
  if (tb) {
    tb.innerHTML = rows.map(r => `<tr>
      <td>${r.label}</td>
      <td>${r.category}</td>
      <td class="vv-mono">${r.agentic_h != null ? hrs(r.agentic_h) : "—"}</td>
      <td class="vv-mono">${rng(r.byhand)}</td>
      <td class="vv-mono vv-hero">${r.saved ? rng(r.saved) : "—"}</td>
      <td class="vv-mono">${usd(r.cost)}</td>
      <td class="vv-mono vv-conf-${r.conf}">${r.conf}</td>
    </tr>`).join("");
  }
  const tf = document.querySelector("#vv-tbl tfoot");
  if (tf) {
    tf.innerHTML = `<tr>
      <td>Total (${rows.length} task${rows.length === 1 ? "" : "s"})</td><td></td>
      <td class="vv-mono">${hrs(vs.agentic_hours)}</td>
      <td class="vv-mono">${rng(vs.manual_hours)}</td>
      <td class="vv-mono vv-hero">${vs.hours_saved ? rng(vs.hours_saved) : "—"}</td>
      <td class="vv-mono">${usd(totCost)}</td><td></td></tr>`;
  }

  const disc = document.getElementById("vv-disc");
  if (disc) {
    disc.textContent =
      "Hours saved = by-hand person-hour estimate (ranged) − agentic time (estimate of how long it " +
      "actually took us). Category = the by-hand specialist persona(s). Agentic cost = measured token $ " +
      "(real Anthropic list rates; indicative, not subscription billing). Confidence is the task's " +
      "lowest-tier todo (conservative). Tasks with no recorded estimate (incl. _unattributed overhead) " +
      "are omitted.";
  }
})();
