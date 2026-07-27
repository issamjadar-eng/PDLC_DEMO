"""BQ-05 — Regulatory dependency of the plan: exposure per plan year + slip scenarios.

Deterministic: computes ONLY from the pinned internal-revenue-plan and
openfda-510k-infusion snapshots. See plans/BQ-05.md for the committed definitions
(dependent = pccp-enabled + new-submission; uniform-slip method with past-window
truncation; FRN review-interval stat as public context only).
"""

import datetime as dt

import computations as C

PLAN_DS = "commercial/internal-revenue-plan"
FDA_DS = "commercial/openfda-510k-infusion"

PLAN_YEARS = ["FY2026", "FY2027", "FY2028", "FY2029", "FY2030"]
DEP_ORDER = ["cleared", "letter-to-file", "pccp-enabled", "new-submission"]


def _musd(v):
    return f"${v / 1e6:,.1f}M"


def _fy_iso(fy):
    return f"{fy[2:]}-01-01"


def run(corpus_root, out, pins):
    p = C.params_for("BQ-05")
    plan, psnap = C.load_pin_csv(corpus_root, pins, PLAN_DS)
    fda, fsnap = C.load_pin_csv(corpus_root, pins, FDA_DS)
    psrc = f"{PLAN_DS}@{psnap}"
    fsrc = f"{FDA_DS}@{fsnap}"
    thr = float(p["exposure_threshold_pct"])
    slips = [int(m) for m in p["slip_scenarios_months"]]
    dep_cats = set(p["dependent_categories"])

    # per-year totals by dependency (FY2026 = sum of quarterly rows)
    by_year = {y: {d: 0 for d in DEP_ORDER} for y in PLAN_YEARS}
    for r in plan:
        y = "FY2026" if r["period"].startswith("2026-Q") else r["period"]
        if y in by_year:
            by_year[y][r["regulatory_dependency"]] += int(r["revenue_usd"])
    tot = {y: sum(by_year[y].values()) for y in PLAN_YEARS}
    dep = {y: sum(v for d, v in by_year[y].items() if d in dep_cats) for y in PLAN_YEARS}
    expo = {y: C.pct(dep[y], tot[y]) for y in PLAN_YEARS}
    breaches = [y for y in PLAN_YEARS if expo[y] > thr]
    total_dep = sum(dep.values())
    window_total = sum(tot.values())

    # slip scenarios: uniform within-year earning; M months slip moves M/12 of each
    # year's dependent revenue into the following year; past-FY2030 leaves the window
    scen = {}
    for m in slips:
        frac = m / 12.0
        adj = {}
        prev_in = 0.0
        for y in PLAN_YEARS:
            nondep = tot[y] - dep[y]
            adj[y] = nondep + dep[y] * (1 - frac) + prev_in
            prev_in = dep[y] * frac
        scen[m] = {"years": adj, "lost": prev_in}  # prev_in after FY2030 = fell out of window

    # FRN review-interval context (real public data)
    ivs = []
    for r in fda:
        if r["decision_date"] and r["date_received"]:
            ivs.append((dt.date.fromisoformat(r["decision_date"])
                        - dt.date.fromisoformat(r["date_received"])).days)
    med = C._median(ivs)

    peak = max(PLAN_YEARS, key=lambda y: expo[y])
    headline = (f"{_musd(total_dep)} of the {_musd(window_total)} five-year plan sits behind FDA "
                f"decisions not yet received; exposure crosses the {thr:.0f}% threshold in "
                f"{', '.join(breaches)} (peak {expo[peak]}% in {peak})"
                if breaches else
                f"{_musd(total_dep)} of the {_musd(window_total)} five-year plan sits behind FDA "
                f"decisions not yet received; every plan year stays under the {thr:.0f}% threshold")

    narrative = {"issues": [], "risks": [], "watch": []}
    ni = 0
    for y in breaches:
        ni += 1
        narrative["issues"].append({
            "id": f"I{ni}", "severity": "high",
            "statement": f"{y} exposure is {expo[y]}% — {_musd(dep[y])} of {_musd(tot[y])} sits "
                         f"behind pccp-enabled or new-submission decisions, over the {thr:.0f}% "
                         f"threshold",
            "action": "Require a formal contingency in the plan narrative for the year; tie each "
                      "dependent revenue block to a named submission milestone so slips become "
                      "trackable events",
            "evidence": ["derived: exposure-by-year", f"src: {psrc}", "config: commercial.yml"],
        })
    for m in slips:
        lost = scen[m]["lost"]
        worst_y = max(PLAN_YEARS, key=lambda y: tot[y] - scen[m]["years"][y])
        worst_delta = tot[worst_y] - scen[m]["years"][worst_y]
        narrative["risks"].append({
            "id": f"R{len(narrative['risks']) + 1}", "severity": "medium" if m == slips[0] else "high",
            "statement": f"A uniform {m}-month slip of all dependent revenue cuts {worst_y} by "
                         f"{_musd(worst_delta)} and pushes {_musd(lost)} past FY2030 — out of the "
                         f"five-year window entirely",
            "mitigation": "The slip is arithmetic, not probability — pair it with the regulatory "
                          "team's submission-timeline confidence before treating either scenario "
                          "as the planning case",
            "evidence": ["derived: slip-scenarios", f"src: {psrc}", "config: commercial.yml"],
        })
    narrative["watch"].append({
        "id": "W1",
        "statement": f"Public base rate: median FRN 510(k) review runs {med} days "
                     f"received-to-decision across {len(ivs)} clearances since 2021 — one review "
                     f"cycle is on the order of the smaller slip scenario, and that measures "
                     f"cleared traditional/special 510(k)s, not PCCP or novel pathways",
        "evidence": ["derived: fda-review-stat", f"src: {fsrc}"],
    })
    narrative["watch"].append({
        "id": "W2",
        "statement": "The slip method moves all dependent revenue uniformly — the plan data has "
                     "no submission-event linkage, so per-program slips are not computable (stated "
                     "gap; a submission register dataset would fix it)",
        "evidence": ["derived: slip-scenarios"],
    })

    exp_results = {
        "E-05.1": (("; ".join(f"{y}: {expo[y]}%" for y in PLAN_YEARS)
                    + (f" — over threshold in {', '.join(breaches)}" if breaches else " — all within")),
                   "not-met" if breaches else "met",
                   ["derived: exposure-by-year"]),
    }
    exps = C.evaluate_expectations("BQ-05", exp_results)

    rl = [
        "# BQ-05 — Plan revenue behind FDA decisions not yet received", "", C.BANNER, "",
        "_The plan data is demo-fabricated; the FDA review-interval context below is real",
        "openFDA public data._", "",
        f"**Verdict**: {headline} [derived: v-main] [src: {psrc}] [config: commercial.yml]", "",
        "## Plan revenue by regulatory dependency per plan year", "",
        "_Dependent = pccp-enabled + new-submission per [config: commercial.yml] — revenue behind",
        "an FDA decision not yet received. letter-to-file needs internal documentation, not an",
        "FDA decision, and is deliberately not counted (see the analysis plan)._", "",
        "| Plan year | cleared | letter-to-file | pccp-enabled | new-submission | Total | Dependent | Exposure |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for y in PLAN_YEARS:
        b = by_year[y]
        flag = " ⚠️" if expo[y] > thr else ""
        rl.append(f"| {y} [src: {psrc}] [derived: exposure-by-year] | {_musd(b['cleared'])} | "
                  f"{_musd(b['letter-to-file'])} | {_musd(b['pccp-enabled'])} | "
                  f"{_musd(b['new-submission'])} | {_musd(tot[y])} | {_musd(dep[y])} | "
                  f"{expo[y]}%{flag} |")
    rl += [
        "",
        f"- Threshold: {thr:.0f}% of plan-year revenue [config: commercial.yml]; five-year "
        f"dependent total {_musd(total_dep)} of {_musd(window_total)} "
        f"[derived: exposure-by-year] [src: {psrc}]",
        "",
        "## Slip scenarios (derived — method stated)", "",
        "- Method: dependent revenue is treated as earned uniformly within its plan year; a slip",
        "  of M months moves M/12 of each year's dependent revenue into the following year "
        "[derived: slip-scenarios] [config: commercial.yml];",
        "  revenue pushed past the final plan year leaves the five-year window and is reported as",
        "  the window shortfall [derived: slip-scenarios] [config: commercial.yml]", "",
        "| Plan year | Plan of record |" + "".join(f" {m}-month slip |" for m in slips),
        "|---|---|" + "---|" * len(slips),
    ]
    for y in PLAN_YEARS:
        rl.append(f"| {y} [src: {psrc}] [derived: slip-scenarios] | {_musd(tot[y])} |"
                  + "".join(f" {_musd(scen[m]['years'][y])} |" for m in slips))
    rl += [
        "",
        "- Five-year window shortfall (revenue pushed past the last plan year): "
        + "; ".join(f"{m}-month slip {_musd(scen[m]['lost'])}" for m in slips)
        + " [derived: slip-scenarios]",
        "",
        "## Context: how long one FDA review cycle runs (real public data)", "",
        f"- Median FRN infusion-pump 510(k) review interval, received to decision: {med} days "
        f"across {len(ivs)} clearances since 2021 [derived: fda-review-stat] [src: {fsrc}]",
        f"- Scope stated: traditional/special 510(k) clearances for product code FRN only "
        f"[src: {fsrc}] — NOT a PCCP or",
        "  De Novo/PMA timeline, and not our own history (our demo K-numbers are fabricated).",
    ]
    rl += C.expectations_section(exps)
    rl += C.narrative_section(narrative)
    rl += [
        "## Method & provenance", "",
        f"- Plan revenue and dependency tags measured from [src: {psrc}]; review intervals "
        f"computed from public decision/received dates in [src: {fsrc}].",
        f"- Dependent-category definition, threshold, and slip months live in "
        f"[config: commercial.yml]; the slip arithmetic is declared per series.",
        "- Exposure history across plan versions is unavailable — only one plan version is",
        "  snapshotted; the history series states the gap rather than faking a trend",
        "  [derived: exposure-history].",
    ]

    data = {
        "bq": "BQ-05",
        "series": [
            {"id": "exposure-stat", "label": "Regulatory exposure of the plan", "unit": "mixed",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "dependent (pccp-enabled + new-submission) revenue ÷ total "
                                      "plan revenue, per plan year and across the window",
                            "inputs": [f"src: {psrc}", "config: commercial.yml"]},
             "provenance": {"dataset": PLAN_DS, "snapshot": psnap},
             "points": [
                 {"label": "five-year dependent revenue ($M)", "value": round(total_dep / 1e6, 1)},
                 {"label": f"peak exposure ({peak}, %)", "value": expo[peak]},
                 {"label": "plan years over the threshold", "value": len(breaches)},
             ]},
            {"id": "plan-by-dependency", "label": "Plan revenue by regulatory dependency ($M)",
             "unit": "$M", "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": PLAN_DS, "snapshot": psnap},
             "lines": [{"label": d,
                        "points": [{"x": _fy_iso(y), "y": round(by_year[y][d] / 1e6, 1)}
                                   for y in PLAN_YEARS]} for d in DEP_ORDER],
             "points": []},
            {"id": "exposure-by-year", "label": "Exposure % per plan year", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "per plan year: (pccp-enabled + new-submission revenue) ÷ "
                                      "total plan revenue",
                            "inputs": [f"src: {psrc}", "config: commercial.yml"]},
             "provenance": {"dataset": PLAN_DS, "snapshot": psnap},
             "points": [{"label": y, "value": expo[y]} for y in PLAN_YEARS]},
            {"id": "slip-scenarios", "label": "Plan totals under uniform slips ($M)", "unit": "$M",
             "kind": "timeseries", "evidence_class": "derived",
             "derivation": {"method": "uniform within-year earning; an M-month slip moves M/12 of "
                                      "each year's dependent revenue to the next year; "
                                      "past-final-year revenue leaves the window",
                            "inputs": [f"src: {psrc}", "config: commercial.yml",
                                       "derived: exposure-by-year"]},
             "provenance": {"dataset": PLAN_DS, "snapshot": psnap},
             "lines": [{"label": "plan of record",
                        "points": [{"x": _fy_iso(y), "y": round(tot[y] / 1e6, 1)}
                                   for y in PLAN_YEARS]}]
                      + [{"label": f"{m}-month slip",
                          "points": [{"x": _fy_iso(y), "y": round(scen[m]["years"][y] / 1e6, 1)}
                                     for y in PLAN_YEARS]} for m in slips],
             "points": []},
            {"id": "fda-review-stat", "label": "FRN 510(k) review interval (public)", "unit": "days",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "median of (decision_date − date_received) across FRN "
                                      "clearances with both dates in the pinned snapshot",
                            "inputs": [f"src: {fsrc}"]},
             "provenance": {"dataset": FDA_DS, "snapshot": fsnap},
             "points": [{"label": f"median days, {len(ivs)} clearances since 2021", "value": med}]},
            {"id": "exposure-history", "label": "Exposure % across plan versions", "unit": "%",
             "kind": "timeseries", "evidence_class": "unavailable",
             "provenance": {"note": "only plan version LRP-2026.1 is snapshotted — exposure "
                                    "history needs successive plan-of-record snapshots"},
             "lines": [], "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, rl, data)
