"""FQ-01 — gross margin by line and region vs prior year + standard-vs-actual cost
variance by line.

Deterministic per the FQ-01 analysis plan: window = the closed quarters of the
configured fy present in the pinned internal-financials snapshot; prior year = the same
quarters one year earlier. Gross margin = (revenue − COGS) ÷ revenue. Actual unit cost
= COGS ÷ units per (quarter, line, revenue type) summed over regions; the standard
comes from the pinned internal-standard-costs snapshot; variance is (actual − standard)
per unit × units, positive = unfavorable. Standard-cost variance by region is NOT
computable (standards carry no region) and is published as an unavailable series.
"""

import computations as C

FIN_DS = "commercial/internal-financials"
STD_DS = "finance/internal-standard-costs"
TREND_LINES = 3   # largest lines charted individually alongside the company total


def _gm_raw(rev, cogs):
    return 100.0 * (rev - cogs) / rev if rev else None


def _fmt_pts(v):
    # round first, then + 0.0 so a −0.04 renders as +0.0, not −0.0
    return "n/a" if v is None else f"{round(v, 1) + 0.0:+.1f} pts"


def _fmt_pct(v):
    return "n/a" if v is None else f"{v:.1f}%"


def _m(v):
    return f"{C.musd(v):.2f}"


def run(corpus_root, out, pins):
    p = C.params_for("FQ-01")
    fy = str(p["fy"])
    floor = float(p["gm_floor_pct"])
    erosion = float(p["erosion_threshold_pts"])
    tol = float(p["cost_variance_tolerance_pct"])
    fin, fsnap = C.load_pin_csv(corpus_root, pins, FIN_DS)
    std, ssnap = C.load_pin_csv(corpus_root, pins, STD_DS)
    fsrc, ssrc = f"{FIN_DS}@{fsnap}", f"{STD_DS}@{ssnap}"

    quarters = sorted({r["period"] for r in fin if r["period"].startswith(fy + "-Q")})
    prior_q = [f"{int(fy) - 1}-Q{q[-1]}" for q in quarters]
    window_name = ("H1 " + fy) if quarters == [f"{fy}-Q1", f"{fy}-Q2"] else \
        (fy + " " + "+".join(q[-2:] for q in quarters))
    prior_name = window_name.replace(fy, str(int(fy) - 1))
    cur = [r for r in fin if r["period"] in quarters]
    pri = [r for r in fin if r["period"] in prior_q]

    def agg(rows, key=None):
        d = {}
        for r in rows:
            k = r[key] if key else "_total"
            rv, cg = d.get(k, (0, 0))
            d[k] = (rv + int(r["revenue_usd"]), cg + int(r["cogs_usd"]))
        return d

    c_tot, p_tot = agg(cur)["_total"], agg(pri).get("_total", (0, 0))
    gm_c, gm_p = _gm_raw(*c_tot), _gm_raw(*p_tot)
    gm_delta = (gm_c - gm_p) if (gm_c is not None and gm_p is not None) else None
    c_line, p_line = agg(cur, "product_line"), agg(pri, "product_line")
    c_reg, p_reg = agg(cur, "region"), agg(pri, "region")
    lines_all = sorted(set(c_line) | set(p_line))
    regions = sorted(set(c_reg) | set(p_reg))

    def rows_for(cd, pd, keys):
        outr = []
        for k in keys:
            gc = _gm_raw(*cd.get(k, (0, 0)))
            gp = _gm_raw(*pd.get(k, (0, 0)))
            delta = (gc - gp) if (gc is not None and gp is not None) else None
            outr.append((k, cd.get(k, (0, 0))[0], gc, gp, delta))
        return outr

    line_rows = rows_for(c_line, p_line, lines_all)
    reg_rows = rows_for(c_reg, p_reg, regions)
    eroding = sorted([r for r in line_rows if r[4] is not None and r[4] <= erosion], key=lambda r: r[4])
    reg_eroding = [r for r in reg_rows if r[4] is not None and r[4] <= erosion]
    above_floor = gm_c is not None and gm_c >= floor

    # ---- standard-cost variance (window) — actual unit cost vs standard, by line/type
    std_map = {(r["period"], r["product_line"], r["revenue_type"]): float(r["std_unit_cost_usd"]) for r in std}
    act = {}
    for r in cur:
        k = (r["period"], r["product_line"], r["revenue_type"])
        cg, u = act.get(k, (0, 0))
        act[k] = (cg + int(r["cogs_usd"]), u + int(r["units"]))
    var_line = {}       # line -> [variance_usd, standard_usd]
    missing_std = sorted({k for k in act if k not in std_map})
    for k, (cg, u) in act.items():
        if k not in std_map or not u:
            continue
        s = std_map[k]
        v = (cg / u - s) * u
        a = var_line.setdefault(k[1], [0.0, 0.0])
        a[0] += v
        a[1] += s * u
    # hardware-only variance per line over the window — the leading indicator the line
    # total dilutes (consumables / service carry small stable gaps)
    hw_line = {}
    for k, (cg, u) in act.items():
        if k[2] != "hardware" or k not in std_map or not u:
            continue
        s = std_map[k]
        a = hw_line.setdefault(k[1], [0.0, 0.0])
        a[0] += (cg / u - s) * u
        a[1] += s * u
    var_rows = [(l, var_line[l][0], C.pct_raw(var_line[l][0], var_line[l][1]),
                 C.pct_raw(hw_line[l][0], hw_line[l][1]) if l in hw_line else None)
                for l in lines_all if l in var_line]
    unfav = sorted([r for r in var_rows if r[2] > tol], key=lambda r: -r[2])
    fav = sorted([r for r in var_rows if r[2] < -tol], key=lambda r: r[2])
    breach = unfav + fav
    hw_unfav = sorted([r for r in var_rows if r[3] is not None and r[3] > tol], key=lambda r: -r[3])
    hw_fav = sorted([r for r in var_rows if r[3] is not None and r[3] < -tol], key=lambda r: r[3])
    hw_lines_n = sum(1 for r in var_rows if r[3] is not None)
    # hardware variance % per quarter per line (all history) for the trend
    all_periods = sorted({r["period"] for r in fin})
    hw_act = {}
    for r in fin:
        if r["revenue_type"] != "hardware":
            continue
        k = (r["period"], r["product_line"])
        cg, u = hw_act.get(k, (0, 0))
        hw_act[k] = (cg + int(r["cogs_usd"]), u + int(r["units"]))
    hw_lines = [l for l in lines_all if any((q, l) in hw_act for q in all_periods)]

    def hw_var(q, l):
        if (q, l) not in hw_act or (q, l, "hardware") not in std_map or not hw_act[(q, l)][1]:
            return None
        cg, u = hw_act[(q, l)]
        s = std_map[(q, l, "hardware")]
        return C.pct_raw(cg / u - s, s)

    var_trend = []
    for l in hw_lines[:4]:
        pts = [{"x": C.quarter_iso(q), "y": round(hw_var(q, l), 1)} for q in all_periods if hw_var(q, l) is not None]
        if pts:
            var_trend.append({"label": f"{l} hardware", "points": pts})

    # ---- GM trend (all history): company + top-N lines by window revenue
    q_tot, q_line = {}, {}
    for r in fin:
        rv, cg = q_tot.get(r["period"], (0, 0))
        q_tot[r["period"]] = (rv + int(r["revenue_usd"]), cg + int(r["cogs_usd"]))
        k = (r["period"], r["product_line"])
        rv, cg = q_line.get(k, (0, 0))
        q_line[k] = (rv + int(r["revenue_usd"]), cg + int(r["cogs_usd"]))
    top_lines = [l for l, _, _, _, _ in sorted(line_rows, key=lambda r: -r[1])[:TREND_LINES]]
    gm_trend = [{"label": "company", "points": [{"x": C.quarter_iso(q), "y": round(_gm_raw(*q_tot[q]), 1)}
                                                 for q in all_periods]}]
    for l in top_lines:
        gm_trend.append({"label": l, "points": [{"x": C.quarter_iso(q), "y": round(_gm_raw(*q_line[(q, l)]), 1)}
                                                for q in all_periods if (q, l) in q_line]})

    # ---- verdict (rollup-survival: carries the eroding-line and breach counts)
    parts = [f"{window_name} gross margin {_fmt_pct(gm_c)} vs {_fmt_pct(gm_p)} {prior_name} "
             f"({_fmt_pts(gm_delta)}) — {'at or above' if above_floor else 'BELOW'} the {floor:.0f}% floor; "
             f"{len(eroding)} of {len(line_rows)} lines eroding (GM down {abs(erosion):.0f} pt or more YoY)"]
    if eroding:
        parts.append("eroding: " + ", ".join(f"{l} {_fmt_pts(d)}" for l, _, _, _, d in eroding))
    parts.append(f"standard-cost variance beyond ±{tol:.0f}% on {len(breach)} of {len(var_rows)} lines (all revenue types)")
    if unfav:
        parts.append("unfavorable: " + ", ".join(f"{l} {v:+.1f}%" for l, _, v, _ in unfav))
    if fav:
        parts.append("favorable: " + ", ".join(f"{l} {v:+.1f}%" for l, _, v, _ in fav))
    parts.append(f"hardware-only variance beyond ±{tol:.0f}% on {len(hw_unfav) + len(hw_fav)} of {hw_lines_n} device lines"
                 + ((" — unfavorable " + ", ".join(f"{l} {h:+.1f}%" for l, _, _, h in hw_unfav)) if hw_unfav else "")
                 + ((", favorable " + ", ".join(f"{l} {h:+.1f}%" for l, _, _, h in hw_fav)) if hw_fav else ""))
    headline = "; ".join(parts)

    # ---- narrative — deterministic from computed facts
    narrative = {"issues": [], "risks": [], "watch": []}
    for i, (l, rev, gc, gp, d) in enumerate(eroding, 1):
        vrow = next((r for r in var_rows if r[0] == l), None)
        tail = ""
        if vrow and vrow[2] > tol:
            tail = f" while its standard-cost variance runs {vrow[2]:+.1f}% (actual above standard)"
        elif vrow and vrow[3] is not None and vrow[3] > tol:
            tail = (f" while its hardware unit cost runs {vrow[3]:+.1f}% above standard "
                    f"(line total {vrow[2]:+.1f}%, diluted by consumables and service)")
        narrative["issues"].append({
            "id": f"I{i}", "severity": "high" if d <= 2 * erosion else "medium",
            "statement": f"{l} gross margin {_fmt_pct(gc)} in {window_name} vs {_fmt_pct(gp)} in {prior_name} "
                         f"({_fmt_pts(d)}){tail}",
            "action": "Cost review of the line: reset the standard to actual, then decide price action vs "
                      "run-down at the quarterly margin review",
            "evidence": ["derived: gm-by-line", "derived: cost-variance-by-line", f"src: {fsrc}", f"src: {ssrc}",
                         C.CONFIG_MARKER],
        })
    rn = 0
    if not above_floor:
        rn += 1
        narrative["risks"].append({
            "id": f"R{rn}", "severity": "medium",
            "statement": f"Company gross margin {_fmt_pct(gm_c)} sits below the {floor:.0f}% floor — the floor "
                         "is a stand-in (no plan of record names one), so the miss is only as firm as an "
                         "unratified target",
            "mitigation": "Have finance ratify a margin floor in the plan of record and mark E-01.1 validated",
            "evidence": ["derived: gm-stat", C.CONFIG_MARKER],
        })
    if unfav or hw_unfav:
        rn += 1
        flattered = sorted({l for l, _, _, _ in unfav} | {l for l, _, _, _ in hw_unfav})
        narrative["risks"].append({
            "id": f"R{rn}", "severity": "medium",
            "statement": "Margin reporting on standards flatters " + ", ".join(flattered)
                         + " — hardware unit cost runs above standard ("
                         + ", ".join(f"{l} {h:+.1f}%" for l, _, _, h in hw_unfav)
                         + "), so booked unit costs understate actual cost",
            "mitigation": "Standard reset at the next standards cycle; interim margin reporting on actual unit cost",
            "evidence": ["derived: cost-variance-by-line", "derived: cost-variance-trend", f"src: {fsrc}", f"src: {ssrc}"],
        })
    if gm_delta is not None and gm_delta > 0 and eroding:
        narrative["watch"].append({
            "id": "W1",
            "statement": f"Mix masking: company margin is up {_fmt_pts(gm_delta)} YoY while "
                         f"{len(eroding)} line(s) erode — the aggregate is lifted by mix, not by line health",
            "evidence": ["derived: gm-stat", "derived: gm-by-line"],
        })
    for g, _, gc, gp, d in reg_eroding:
        narrative["watch"].append({
            "id": f"W{len(narrative['watch']) + 1}",
            "statement": f"{g} region margin {_fmt_pct(gc)} vs {_fmt_pct(gp)} ({_fmt_pts(d)}) — a regional "
                         "pricing/discounting check is warranted",
            "evidence": ["derived: gm-by-region", f"src: {fsrc}"],
        })
    if missing_std:
        narrative["watch"].append({
            "id": f"W{len(narrative['watch']) + 1}",
            "statement": f"{len(missing_std)} actual cell(s) have no standard in the roll-up and are excluded "
                         "from the variance — actual and standard vocabularies differ in the pins",
            "evidence": [f"src: {fsrc}", f"src: {ssrc}"],
        })

    exp_results = {
        "E-01.1": (f"{_fmt_pct(gm_c)} ({window_name}); {len(eroding)} of {len(line_rows)} lines eroding",
                   "met" if above_floor else "not-met",
                   ["derived: gm-stat", "derived: gm-by-line"]),
        "E-01.2": (f"{len(breach)} of {len(var_rows)} lines beyond ±{tol:.0f}% (all revenue types)"
                   + (": " + ", ".join(f"{l} {v:+.1f}%" for l, _, v, _ in breach) if breach else "")
                   + f"; hardware-only {len(hw_unfav) + len(hw_fav)} of {hw_lines_n}"
                   + (": " + ", ".join(f"{l} {h:+.1f}%" for l, _, _, h in hw_unfav + hw_fav) if (hw_unfav or hw_fav) else ""),
                   "met" if not breach else "not-met",
                   ["derived: cost-variance-by-line"]),
    }
    exps = C.evaluate_expectations("FQ-01", exp_results)

    lines = [
        "# FQ-01 — Gross margin by line and region; standard-vs-actual cost variance", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {fsrc}] [src: {ssrc}] [{C.CONFIG_MARKER}]", "",
        "## Gross margin by product line", "",
        f"_Window: {', '.join(quarters)} (closed quarters in the pinned actuals) vs {', '.join(prior_q)} "
        f"[src: {fsrc}]; erosion threshold {erosion:+.1f} pts YoY and margin floor {floor:.0f}% "
        f"[{C.CONFIG_MARKER}]._", "",
        f"| Product line | Revenue $M ({window_name}) | GM % | GM % prior year | Δ pts |",
        "|---|---|---|---|---|",
    ]
    for l, rev, gc, gp, d in line_rows:
        flag = " ⚠️" if d is not None and d <= erosion else ""
        lines.append(f"| {l} [src: {fsrc}] | {_m(rev)} | {_fmt_pct(gc)} | {_fmt_pct(gp)} | {_fmt_pts(d)}{flag} |")
    lines += [
        f"| **Company** [src: {fsrc}] | {_m(c_tot[0])} | {_fmt_pct(gm_c)} | {_fmt_pct(gm_p)} | {_fmt_pts(gm_delta)} |",
        "",
        "## Gross margin by region", "",
        "| Region | Revenue $M | GM % | GM % prior year | Δ pts |",
        "|---|---|---|---|---|",
    ]
    for g, rev, gc, gp, d in reg_rows:
        flag = " ⚠️" if d is not None and d <= erosion else ""
        lines.append(f"| {g} [src: {fsrc}] | {_m(rev)} | {_fmt_pct(gc)} | {_fmt_pct(gp)} | {_fmt_pts(d)}{flag} |")
    lines += [
        "",
        "## Standard-vs-actual cost variance by line", "",
        f"_Actual unit cost = COGS ÷ units per quarter × line × revenue type, summed over regions [src: {fsrc}]; "
        f"standard from the cost roll-up [src: {ssrc}]; variance = (actual − standard) × units over the window, "
        f"positive = unfavorable; review tolerance ±{tol:.0f}% applied to the line total (all revenue types) "
        f"[{C.CONFIG_MARKER}]. The hardware-only column is the leading indicator the line total dilutes._", "",
        "| Product line | Variance $K | Variance % of standard (all types) | Hardware-only variance % |",
        "|---|---|---|---|",
    ]
    for l, v, vp, hw in var_rows:
        flag = " ⚠️" if abs(vp) > tol else ""
        hflag = " ⚠️" if hw is not None and abs(hw) > tol else ""
        hw_txt = "n/a" if hw is None else f"{round(hw, 1) + 0.0:+.1f}%"   # no −0.0 at render
        lines.append(f"| {l} [src: {fsrc}] [src: {ssrc}] | {C.kusd(v):+d} | {round(vp, 1) + 0.0:+.1f}%{flag} | "
                     f"{hw_txt}{hflag} |")
    lines += [
        "",
        "## Standard-cost variance by region: not computable (stated, not approximated)", "",
        f"- The standard-cost roll-up carries no region dimension [src: {ssrc}]; actual COGS is regional",
        f"  [src: {fsrc}], but a regional variance needs a regional standard or a regional actual-cost feed.",
        "  Published as an unavailable series [derived: cost-variance-by-region].",
    ]
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Gross margin = (revenue − COGS) ÷ revenue from [src: {fsrc}]; window and prior-year quarters "
        f"matched one-to-one; thresholds [{C.CONFIG_MARKER}].",
        f"- Historical view: quarterly gross margin for the company and the largest {TREND_LINES} lines is "
        f"charted [derived: gm-trend] [src: {fsrc}]; hardware unit-cost variance per quarter is charted "
        f"[derived: cost-variance-trend] [src: {fsrc}] [src: {ssrc}].",
        "- Verdict and expectation actuals carry the eroding-line and variance-breach counts so a rollup "
        "cannot drop them [derived: v-main].",
    ]

    data = {
        "bq": "FQ-01",
        "series": [
            {"id": "gm-stat", "label": "Company gross margin", "unit": "%", "kind": "stat",
             "evidence_class": "derived",
             "derivation": {"method": "(revenue − COGS) ÷ revenue over the closed quarters of the fiscal year; prior year = same quarters",
                            "inputs": [f"src: {fsrc}", C.CONFIG_MARKER]},
             "provenance": {"dataset": FIN_DS, "snapshot": fsnap},
             "points": [{"label": f"{window_name} gross margin", "value": round(gm_c, 1) if gm_c is not None else None,
                         "sub": f"{prior_name} {_fmt_pct(gm_p)} ({_fmt_pts(gm_delta)}); floor {floor:.0f}%"}]},
            {"id": "gm-by-line", "label": "Gross margin by product line: window vs prior year", "unit": "%",
             "kind": "paired-bars", "pairs": {"a_label": window_name, "b_label": prior_name},
             "evidence_class": "derived",
             "derivation": {"method": "(revenue − COGS) ÷ revenue per product line, window and prior-year quarters",
                            "inputs": [f"src: {fsrc}"]},
             "provenance": {"dataset": FIN_DS, "snapshot": fsnap},
             "points": [{"label": l, "a": round(gc, 1) if gc is not None else None,
                         "b": round(gp, 1) if gp is not None else None,
                         "delta_pts": round(d, 1) if d is not None else None} for l, _, gc, gp, d in line_rows]},
            {"id": "gm-by-region", "label": "Gross margin by region: window vs prior year", "unit": "%",
             "kind": "paired-bars", "pairs": {"a_label": window_name, "b_label": prior_name},
             "evidence_class": "derived",
             "derivation": {"method": "(revenue − COGS) ÷ revenue per region, window and prior-year quarters",
                            "inputs": [f"src: {fsrc}"]},
             "provenance": {"dataset": FIN_DS, "snapshot": fsnap},
             "points": [{"label": g, "a": round(gc, 1) if gc is not None else None,
                         "b": round(gp, 1) if gp is not None else None,
                         "delta_pts": round(d, 1) if d is not None else None} for g, _, gc, gp, d in reg_rows]},
            {"id": "gm-trend", "label": "Quarterly gross margin: company and largest lines", "unit": "%",
             "kind": "timeseries", "evidence_class": "derived",
             "derivation": {"method": "quarterly (revenue − COGS) ÷ revenue for the company and the top lines by window revenue",
                            "inputs": [f"src: {fsrc}"]},
             "provenance": {"dataset": FIN_DS, "snapshot": fsnap},
             "lines": gm_trend, "points": []},
            {"id": "cost-variance-by-line", "label": "Standard-cost variance by line (window)", "unit": "USD K",
             "evidence_class": "derived",
             "derivation": {"method": "Σ over quarter × revenue type of (COGS ÷ units − standard unit cost) × units; positive = unfavorable",
                            "inputs": [f"src: {fsrc}", f"src: {ssrc}", C.CONFIG_MARKER]},
             "provenance": {"datasets": [{"dataset": FIN_DS, "snapshot": fsnap}, {"dataset": STD_DS, "snapshot": ssnap}]},
             "points": [{"label": l, "value": C.kusd(v), "variance_pct": round(vp, 1),
                         "hardware_variance_pct": round(hw, 1) if hw is not None else None} for l, v, vp, hw in var_rows]},
            {"id": "cost-variance-trend", "label": "Hardware unit-cost variance vs standard, by quarter", "unit": "%",
             "kind": "timeseries", "evidence_class": "derived",
             "derivation": {"method": "(hardware COGS ÷ hardware units − hardware standard) ÷ standard per quarter per line",
                            "inputs": [f"src: {fsrc}", f"src: {ssrc}"]},
             "provenance": {"datasets": [{"dataset": FIN_DS, "snapshot": fsnap}, {"dataset": STD_DS, "snapshot": ssnap}]},
             "lines": var_trend, "points": []},
            {"id": "cost-variance-by-region", "label": "Standard-cost variance by region", "unit": "USD K",
             "evidence_class": "unavailable",
             "provenance": {"note": "the standard-cost roll-up (internal-standard-costs) carries no region "
                                    "dimension; a regional variance needs regional standards or a regional "
                                    "actual-cost feed from the ERP."},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
