"""FQ-08 — budget vs actual YTD by function with headcount variance; breach drivers.

Deterministic per the FQ-08 analysis plan: YTD = every period in the pinned GL snapshot
(all belong to the configured fy — asserted). Variance = (actual − budget) ÷ budget per
function; a function breaches when |variance| exceeds the per-function tolerance. The
"why" is computed: the cost center with the largest absolute dollar variance inside a
breaching function, and — for under-spends — the latest-period headcount shortfall.
Spend by project is NOT in the ledger and is published as an unavailable series.
"""

import computations as C

GL_DS = "finance/internal-gl-budget"
TREND_FUNCS = 3   # functions with the largest |YTD variance| charted with the total


def _var(a, b):
    return 100.0 * (a - b) / b if b else None


def _fmt(v):
    return "n/a" if v is None else f"{v:+.1f}%"


def _kfmt(v):
    """Signed dollars in $K: +$427K / -$401K."""
    k = C.kusd(v)
    return f"{'+' if k >= 0 else '-'}${abs(k)}K"


def _m(v):
    return f"{C.musd(v):.2f}"


def run(corpus_root, out, pins):
    p = C.params_for("FQ-08")
    fy = str(p["fy"])
    tol = float(p["tolerance_pct"])
    tol_total = float(p["total_tolerance_pct"])
    gl, snap = C.load_pin_csv(corpus_root, pins, GL_DS)
    src = f"{GL_DS}@{snap}"

    periods = sorted({r["period"] for r in gl})
    off_year = [m for m in periods if not m.startswith(fy)]
    if off_year:
        raise SystemExit(f"{GL_DS}: periods outside fy {fy} in the pin: {off_year} — the YTD window is undefined")
    latest = periods[-1]
    window_name = f"YTD {fy} ({periods[0]}..{latest})"
    funcs = sorted({r["function"] for r in gl})

    def agg(rows):
        b = sum(int(r["budget_usd"]) for r in rows)
        a = sum(int(r["actual_usd"]) for r in rows)
        return b, a

    tb, ta = agg(gl)
    tv = _var(ta, tb)
    within_total = tv is not None and abs(tv) <= tol_total
    f_rows = []
    for f in funcs:
        sub = [r for r in gl if r["function"] == f]
        b, a = agg(sub)
        lat = [r for r in sub if r["period"] == latest]
        hb = sum(int(r["headcount_budget"]) for r in lat)
        ha = sum(int(r["headcount_actual"]) for r in lat)
        f_rows.append((f, b, a, _var(a, b), hb, ha))
    breach = sorted([r for r in f_rows if r[3] is not None and abs(r[3]) > tol], key=lambda r: -abs(r[3]))
    over = [r for r in breach if r[3] > 0]
    under = [r for r in breach if r[3] < 0]

    # drivers: cost centers inside breaching functions, ranked by |$ variance|
    drivers = {}
    cc_points = []
    for f, _, _, fv, hb, ha in breach:
        ccs = sorted({r["cost_center"] for r in gl if r["function"] == f})
        cc_rows = []
        for cc in ccs:
            b, a = agg([r for r in gl if r["cost_center"] == cc])
            cc_rows.append((cc, b, a, a - b, _var(a, b)))
        cc_rows.sort(key=lambda r: (-abs(r[3]), r[0]))
        drivers[f] = cc_rows
        cc_points += [{"label": f"{cc} ({f})", "value": C.kusd(d), "variance_pct": round(vp, 1) if vp is not None else None}
                      for cc, _, _, d, vp in cc_rows]

    def why(f, fv, hb, ha):
        top = drivers[f][0]
        bits = [f"driver {top[0]} {_kfmt(top[3])} ({_fmt(top[4])})"]
        if fv < 0 and ha < hb:
            bits.append(f"headcount {ha} vs {hb} budget at {latest} — hiring lag")
        elif fv > 0 and ha > hb:
            bits.append(f"headcount {ha} vs {hb} budget at {latest}")
        return "; ".join(bits)

    # monthly trend: total + top-N functions by |YTD variance|
    def monthly_var(rows_filter):
        pts = []
        for m in periods:
            b, a = agg([r for r in gl if r["period"] == m and rows_filter(r)])
            v = _var(a, b)
            pts.append({"x": C.month_iso(m), "y": round(v, 1) if v is not None else None})
        return pts

    trend = [{"label": "total opex", "points": monthly_var(lambda r: True)}]
    for f, _, _, _, _, _ in sorted(f_rows, key=lambda r: -abs(r[3] or 0))[:TREND_FUNCS]:
        trend.append({"label": f, "points": monthly_var(lambda r, f=f: r["function"] == f)})

    # ---- expectations
    exps = C.evaluate_expectations("FQ-08", {
        "E-08.1": (f"{len(breach)} of {len(f_rows)} functions beyond ±{tol:.0f}%"
                   + (": " + ", ".join(f"{f} {_fmt(v)}" for f, _, _, v, _, _ in breach) if breach else ""),
                   "met" if not breach else "not-met", ["derived: variance-pct-by-function"]),
        "E-08.2": (f"{_fmt(tv)} total ({window_name})", "met" if within_total else "not-met",
                   ["derived: ytd-variance-stat"]),
    })

    # ---- verdict (rollup-survival: carries the per-function breaches and their drivers)
    parts = [f"{window_name} opex ${_m(ta)}M vs budget ${_m(tb)}M ({_fmt(tv)}, "
             f"{'within' if within_total else 'OUTSIDE'} the ±{tol_total:.0f}% total tolerance); "
             f"{len(breach)} of {len(f_rows)} functions breach the ±{tol:.0f}% band"]
    for f, _, _, fv, hb, ha in breach:
        parts.append(f"{f} {_fmt(fv)} ({why(f, fv, hb, ha)})")
    headline = "; ".join(parts)

    # ---- narrative
    narrative = {"issues": [], "risks": [], "watch": []}
    for i, (f, b, a, fv, hb, ha) in enumerate(over, 1):
        narrative["issues"].append({
            "id": f"I{i}", "severity": "high" if fv > 2 * tol else "medium",
            "statement": f"{f} is {_fmt(fv)} over budget {window_name} (${_m(a)}M vs ${_m(b)}M) — "
                         f"{why(f, fv, hb, ha)}",
            "action": "Re-plan the driving cost center at the monthly close: confirm the spend is buying a "
                      "milestone, then reforecast or re-phase",
            "evidence": ["derived: variance-by-function", "derived: cost-center-drivers", f"src: {src}", C.CONFIG_MARKER],
        })
    for j, (f, b, a, fv, hb, ha) in enumerate(under, len(over) + 1):
        narrative["issues"].append({
            "id": f"I{j}", "severity": "medium",
            "statement": f"{f} is {_fmt(fv)} under budget {window_name} (${_m(a)}M vs ${_m(b)}M) — "
                         f"{why(f, fv, hb, ha)}",
            "action": "Treat the under-spend as deferred work, not savings: confirm hiring pipeline vs plan "
                      "and the revenue-plan dependency on the missing heads",
            "evidence": ["derived: variance-by-function", "derived: headcount-by-function", f"src: {src}", C.CONFIG_MARKER],
        })
    narrative["risks"].append({
        "id": "R1", "severity": "medium",
        "statement": f"The ±{tol:.0f}% per-function and ±{tol_total:.0f}% total tolerances are stand-ins — the "
                     "budget book names no variance trigger, so the breach list is only as firm as an unratified band",
        "mitigation": "Have the controller ratify the tolerances in the budget book and mark E-08.1 / E-08.2 validated",
        "evidence": [C.CONFIG_MARKER],
    })
    if over and under:
        narrative["watch"].append({
            "id": "W1",
            "statement": "Netting inside the total: " + ", ".join(f"{f} {_fmt(v)}" for f, _, _, v, _, _ in over)
                         + " over is offset by " + ", ".join(f"{f} {_fmt(v)}" for f, _, _, v, _, _ in under)
                         + " under — the company total understates both",
            "evidence": ["derived: variance-by-function", "derived: ytd-variance-stat"],
        })
    narrative["watch"].append({
        "id": f"W{len(narrative['watch']) + 1}",
        "statement": "The ledger export carries no program / project dimension — an R&D overrun cannot be "
                     "attributed to a milestone or assessed for capitalization here",
        "evidence": ["derived: variance-by-project", f"src: {src}"],
    })

    lines = [
        "# FQ-08 — Budget vs actual YTD by function; headcount variance; breach drivers", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [{C.CONFIG_MARKER}]", "",
        "## Variance by function", "",
        f"_Window: {periods[0]}..{latest} (every period in the pin) [src: {src}]; tolerances ±{tol:.0f}% per "
        f"function, ±{tol_total:.0f}% total [{C.CONFIG_MARKER}]; headcount at {latest}._", "",
        "| Function | Budget $M | Actual $M | Variance % | Variance $K | Heads budget | Heads actual |",
        "|---|---|---|---|---|---|---|",
    ]
    for f, b, a, fv, hb, ha in f_rows:
        flag = " ⚠️" if fv is not None and abs(fv) > tol else ""
        lines.append(f"| {f} [src: {src}] | {_m(b)} | {_m(a)} | {_fmt(fv)}{flag} | {_kfmt(a - b)} | {hb} | {ha} |")
    hb_t = sum(r[4] for r in f_rows)
    ha_t = sum(r[5] for r in f_rows)
    lines += [
        f"| **Total** [src: {src}] | {_m(tb)} | {_m(ta)} | {_fmt(tv)} | {_kfmt(ta - tb)} | {hb_t} | {ha_t} |",
        "",
        "## Breach drivers — cost centers inside breaching functions", "",
    ]
    if not breach:
        lines.append(f"- No function breaches the ±{tol:.0f}% band [src: {src}] [{C.CONFIG_MARKER}].")
    for f, _, _, fv, hb, ha in breach:
        lines += [f"### {f} ({_fmt(fv)}) [src: {src}]", "",
                  "| Cost center | Budget $M | Actual $M | Variance $K | Variance % |",
                  "|---|---|---|---|---|"]
        for cc, b, a, d, vp in drivers[f]:
            lines.append(f"| {cc} [src: {src}] | {_m(b)} | {_m(a)} | {_kfmt(d)} | {_fmt(vp)} |")
        lines += [f"- {why(f, fv, hb, ha)} [src: {src}] [derived: cost-center-drivers]", ""]
    lines += [
        "## Spend by project: not in the ledger (stated, not approximated)", "",
        f"- The GL export carries function and cost center only [src: {src}]; program attribution and the "
        "capitalization view need a project dimension (roadmap FQ-10) [derived: variance-by-project].",
    ]
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Budget and actual summed from [src: {src}] over every period in the pin; variance = (actual − budget) ÷ "
        f"budget; tolerances [{C.CONFIG_MARKER}]; breach drivers ranked by absolute dollar variance.",
        f"- Historical view: monthly variance for the total and the {TREND_FUNCS} largest-variance functions is charted "
        f"[derived: monthly-variance-trend] [src: {src}].",
        "- Verdict and expectation actuals carry the breaching functions and their drivers so a rollup cannot drop "
        "them [derived: v-main].",
    ]

    data = {
        "bq": "FQ-08",
        "series": [
            {"id": "ytd-variance-stat", "label": "Total opex vs budget YTD", "unit": "%", "kind": "stat",
             "evidence_class": "derived",
             "derivation": {"method": "(Σ actual − Σ budget) ÷ Σ budget over every period in the pin",
                            "inputs": [f"src: {src}", C.CONFIG_MARKER]},
             "provenance": {"dataset": GL_DS, "snapshot": snap},
             "points": [{"label": f"{window_name} variance", "value": round(tv, 1) if tv is not None else None,
                         "sub": f"actual ${C.musd(ta)}M vs budget ${C.musd(tb)}M; {len(breach)} of {len(f_rows)} functions breach ±{tol:.0f}%"}]},
            {"id": "variance-by-function", "label": "Actual vs budget by function (YTD)", "unit": "USD M",
             "kind": "paired-bars", "pairs": {"a_label": "actual", "b_label": "budget"}, "evidence_class": "derived",
             "derivation": {"method": "Σ actual and Σ budget per function over the window", "inputs": [f"src: {src}"]},
             "provenance": {"dataset": GL_DS, "snapshot": snap},
             "points": [{"label": f, "a": C.musd(a), "b": C.musd(b), "variance_pct": round(fv, 1) if fv is not None else None}
                        for f, b, a, fv, _, _ in f_rows]},
            {"id": "variance-pct-by-function", "label": "Variance % by function (YTD)", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "(actual − budget) ÷ budget per function over the window", "inputs": [f"src: {src}", C.CONFIG_MARKER]},
             "provenance": {"dataset": GL_DS, "snapshot": snap},
             "points": [{"label": f, "value": round(fv, 1) if fv is not None else None} for f, _, _, fv, _, _ in f_rows]},
            {"id": "headcount-by-function", "label": f"Headcount: actual vs budget at {latest}", "unit": "heads",
             "kind": "paired-bars", "pairs": {"a_label": "actual", "b_label": "budget"}, "evidence_class": "measured",
             "provenance": {"dataset": GL_DS, "snapshot": snap},
             "points": [{"label": f, "a": ha, "b": hb} for f, _, _, _, hb, ha in f_rows]},
            {"id": "monthly-variance-trend", "label": "Monthly variance %: total and largest-variance functions",
             "unit": "%", "kind": "timeseries", "evidence_class": "derived",
             "derivation": {"method": "(actual − budget) ÷ budget per month for the total and the top functions by |YTD variance|",
                            "inputs": [f"src: {src}"]},
             "provenance": {"dataset": GL_DS, "snapshot": snap},
             "lines": trend, "points": []},
            {"id": "cost-center-drivers", "label": "Cost-center variance inside breaching functions (YTD)", "unit": "USD K",
             "evidence_class": "derived",
             "derivation": {"method": "Σ actual − Σ budget per cost center for functions beyond the tolerance, ranked by |variance|",
                            "inputs": [f"src: {src}", C.CONFIG_MARKER]},
             "provenance": {"dataset": GL_DS, "snapshot": snap},
             "points": cc_points},
            {"id": "variance-by-project", "label": "Spend by program / project", "unit": "USD M",
             "evidence_class": "unavailable",
             "provenance": {"note": "the GL export (internal-gl-budget) carries function and cost center only; "
                                    "program attribution and capitalization need a project dimension in the ledger feed."},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
