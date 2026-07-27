"""BQ-28 — revenue vs plan by line and region (volume/price/timing).

Deterministic per the BQ-28 analysis plan: actuals = closed quarters of the configured
fy in the pinned internal-financials snapshot; plan = matching quarterly rows of the
pinned internal-revenue-plan snapshot; variance flagged against the (stand-in)
tolerance. The volume-vs-price split is NOT computable — the plan carries no units —
and is published as an unavailable series, never approximated.
"""

import computations as C

FIN_DS = "commercial/internal-financials"
PLAN_DS = "commercial/internal-revenue-plan"
Q_MONTH = {"Q1": "01", "Q2": "04", "Q3": "07", "Q4": "10"}


def _musd(v):
    return round(v / 1e6, 1)


def _var(a, p):
    return round(100.0 * (a - p) / p, 1) if p else 0.0


def run(corpus_root, out, pins):
    p = C.params_for("BQ-28")
    fy = str(p["fy"])
    tol = float(p["tolerance_pct"])
    act, asnap = C.load_pin_csv(corpus_root, pins, FIN_DS)
    plan, psnap = C.load_pin_csv(corpus_root, pins, PLAN_DS)
    asrc, psrc = f"{FIN_DS}@{asnap}", f"{PLAN_DS}@{psnap}"

    quarters = sorted({r["period"] for r in act if r["period"].startswith(fy + "-Q")})
    a_win = [r for r in act if r["period"] in quarters]
    p_win = [r for r in plan if r["period"] in quarters]

    def agg(rows, key):
        d = {}
        for r in rows:
            d[r[key]] = d.get(r[key], 0) + int(r["revenue_usd"])
        return d

    a_line, p_line = agg(a_win, "product_line"), agg(p_win, "product_line")
    a_reg, p_reg = agg(a_win, "region"), agg(p_win, "region")
    a_q, p_q = agg(a_win, "period"), agg(p_win, "period")
    lines_all = sorted(set(a_line) | set(p_line))
    regions = sorted(set(a_reg) | set(p_reg))
    ta, tp = sum(a_line.values()), sum(p_line.values())
    tv = _var(ta, tp)

    line_rows = [(l, a_line.get(l, 0), p_line.get(l, 0), _var(a_line.get(l, 0), p_line.get(l, 0)))
                 for l in lines_all]
    reg_rows = [(g, a_reg.get(g, 0), p_reg.get(g, 0), _var(a_reg.get(g, 0), p_reg.get(g, 0)))
                for g in regions]
    q_rows = [(q, a_q.get(q, 0), p_q.get(q, 0), _var(a_q.get(q, 0), p_q.get(q, 0)))
              for q in quarters]
    under = sorted([r for r in line_rows if r[3] < -tol], key=lambda r: r[3])
    over = sorted([r for r in line_rows if r[3] > tol], key=lambda r: -r[3])
    reg_breach = [r for r in reg_rows if abs(r[3]) > tol]
    last_q = q_rows[-1] if q_rows else None
    deteriorating = len(q_rows) >= 2 and q_rows[-1][3] < q_rows[0][3] and q_rows[-1][3] < -tol

    window_name = ("H1 " + fy) if quarters == [f"{fy}-Q1", f"{fy}-Q2"] else \
        (fy + " " + "+".join(q[-2:] for q in quarters))
    within = abs(tv) <= tol
    parts = [f"{window_name} revenue ${_musd(ta)}M vs plan ${_musd(tp)}M ({tv:+.1f}%, "
             f"{'within' if within else 'OUTSIDE'} the ±{tol:.0f}% tolerance overall; "
             f"{len(under)} of {len(line_rows)} lines breach the band individually on the "
             f"downside)"]
    if under:
        parts.append("under plan: " + ", ".join(f"{l} {v:+.1f}%" for l, _, _, v in under))
    if over:
        parts.append("masked by " + ", ".join(f"{l} {v:+.1f}%" for l, _, _, v in over))
    if last_q and last_q[3] < -tol:
        parts.append(f"{last_q[0]} alone breached at {last_q[3]:+.1f}%")
    headline = "; ".join(parts)

    # timeseries: actual quarterly total (all history) vs plan quarterly total (fy)
    a_hist = {}
    for r in act:
        a_hist[r["period"]] = a_hist.get(r["period"], 0) + int(r["revenue_usd"])
    p_hist = {}
    for r in plan:
        if r["period"].startswith(fy + "-Q"):
            p_hist[r["period"]] = p_hist.get(r["period"], 0) + int(r["revenue_usd"])

    def qx(period):
        y, q = period.split("-")
        return f"{y}-{Q_MONTH[q]}-01"

    trend_lines = [
        {"label": "actual revenue", "points": [{"x": qx(q), "y": _musd(v)}
                                               for q, v in sorted(a_hist.items())]},
        {"label": f"plan {fy} (LRP)", "points": [{"x": qx(q), "y": _musd(v)}
                                                 for q, v in sorted(p_hist.items())]},
    ]

    # narrative — deterministic from computed facts
    narrative = {"issues": [], "risks": [], "watch": []}
    for i, (l, a, pl, v) in enumerate(under, 1):
        narrative["issues"].append({
            "id": f"I{i}", "severity": "high" if v < -2 * tol else "medium",
            "statement": f"{l} is {v:+.1f}% under plan for {window_name} "
                         f"(${_musd(a)}M actual vs ${_musd(pl)}M plan) — beyond the ±{tol:.0f}% "
                         "flagging tolerance",
            "action": "Confirm driver with the win/loss and funnel reviews; decide reforecast vs "
                      "recovery plan for the line at the monthly close",
            "evidence": ["derived: variance-by-line", f"src: {asrc}", f"src: {psrc}",
                         "config: commercial.yml"],
        })
    rn = 0
    if deteriorating:
        rn += 1
        narrative["risks"].append({
            "id": f"R{rn}", "severity": "medium",
            "statement": f"Quarter-over-quarter timing is deteriorating: "
                         + " → ".join(f"{q} {v:+.1f}%" for q, _, _, v in q_rows)
                         + f" — the latest quarter breaches the ±{tol:.0f}% band on its own",
            "mitigation": "Treat the next monthly close as the reforecast trigger check; do not "
                          "wait for the YTD composite to breach",
            "evidence": ["derived: variance-by-quarter", f"src: {asrc}", f"src: {psrc}",
                         "config: commercial.yml"],
        })
    rn += 1
    narrative["risks"].append({
        "id": f"R{rn}", "severity": "medium",
        "statement": f"The ±{tol:.0f}% tolerance is a stand-in — the plan of record names no "
                     "reforecast trigger, so the within/outside verdict is only as good as an "
                     "unratified threshold",
        "mitigation": "Have finance ratify a tolerance in the plan of record and mark E-28.1 "
                      "validated",
        "evidence": ["config: commercial.yml"],
    })
    if over:
        narrative["watch"].append({
            "id": "W1",
            "statement": "Mix masking: " + ", ".join(f"{l} at {v:+.1f}%" for l, _, _, v in over)
                         + " over plan offsets the under-plan lines inside the composite — the "
                           "total variance understates the flagship/growth miss",
            "evidence": ["derived: variance-by-line", "derived: variance-contribution"],
        })
    for g, a, pl, v in reg_breach:
        narrative["watch"].append({
            "id": f"W{len(narrative['watch']) + 1}",
            "statement": f"{g} region at {v:+.1f}% vs plan breaches the ±{tol:.0f}% band",
            "evidence": ["derived: variance-by-region", "config: commercial.yml"],
        })

    exp_results = {
        "E-28.1": (f"{tv:+.1f}% YTD ({window_name}) — "
                   f"{'within' if within else 'OUTSIDE'} tolerance overall; "
                   f"{len(under)} of {len(line_rows)} lines breach the ±{tol:.0f}% band "
                   f"individually on the downside",
                   "met" if within else "not-met",
                   ["derived: ytd-variance", "derived: variance-by-line"]),
    }
    exps = C.evaluate_expectations("BQ-28", exp_results)

    lines = [
        "# BQ-28 — Revenue vs plan: line, region, timing", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {asrc}] [src: {psrc}] "
        f"[config: commercial.yml]", "",
        "## Variance by product line", "",
        f"_Window: {', '.join(quarters)} (closed quarters in the pinned actuals) [src: {asrc}]; "
        f"plan rows from the plan of record [src: {psrc}]; flagging tolerance ±{tol:.0f}% "
        f"[config: commercial.yml]._", "",
        "| Product line | Actual $M | Plan $M | Variance % | Variance $M |",
        "|---|---|---|---|---|",
    ]
    for l, a, pl, v in line_rows:
        flag = " ⚠️" if abs(v) > tol else ""
        lines.append(f"| {l} [src: {asrc}] [src: {psrc}] | {_musd(a)} | {_musd(pl)} | "
                     f"{v:+.1f}%{flag} | {_musd(a - pl):+.1f} |")
    lines += [
        "",
        "## Variance by region", "",
        "| Region | Actual $M | Plan $M | Variance % | Variance $M |",
        "|---|---|---|---|---|",
    ]
    for g, a, pl, v in reg_rows:
        flag = " ⚠️" if abs(v) > tol else ""
        lines.append(f"| {g} [src: {asrc}] [src: {psrc}] | {_musd(a)} | {_musd(pl)} | "
                     f"{v:+.1f}%{flag} | {_musd(a - pl):+.1f} |")
    lines += [
        "",
        "## Timing — variance by quarter", "",
        "| Quarter | Actual $M | Plan $M | Variance % |",
        "|---|---|---|---|",
    ]
    for q, a, pl, v in q_rows:
        flag = " ⚠️" if abs(v) > tol else ""
        lines.append(f"| {q} [src: {asrc}] [src: {psrc}] | {_musd(a)} | {_musd(pl)} | {v:+.1f}%{flag} |")
    lines += [
        "",
        "## Volume vs price: not computable (stated, not approximated)", "",
        "- The plan of record carries revenue only — NO planned units — so a volume-vs-price",
        f"  bridge has no plan side [src: {psrc}]. Actual units exist [src: {asrc}], but an",
        "  actual-side ASP alone cannot attribute variance between volume and price. The split is",
        "  published as an unavailable series [derived: price-volume-split] until planned units",
        "  land in the LRP export.",
    ]
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Actuals summed from [src: {asrc}]; plan from [src: {psrc}]; comparison restricted to "
        f"matching closed quarters; tolerance and fiscal year [config: commercial.yml].",
        "- Variance $M contribution per line/region is charted so the composite's netting is "
        "visible [derived: variance-contribution].",
        f"- Historical view: quarterly actual revenue vs the {fy} plan phasing is charted "
        f"[derived: quarterly-trend] [src: {asrc}] [src: {psrc}].",
    ]

    data = {
        "bq": "BQ-28",
        "series": [
            {"id": "ytd-variance", "label": "YTD revenue vs plan", "unit": "%",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "(sum of actual revenue − sum of plan revenue) ÷ plan revenue over the closed quarters of the fiscal year",
                            "inputs": [f"src: {asrc}", f"src: {psrc}", "config: commercial.yml"]},
             "provenance": {"dataset": FIN_DS, "snapshot": asnap},
             "points": [{"label": f"{window_name} variance vs plan",
                         "value": tv,
                         "sub": f"actual ${_musd(ta)}M vs plan ${_musd(tp)}M"}]},
            {"id": "quarterly-trend", "label": f"Quarterly revenue: actual vs {fy} plan", "unit": "USD M",
             "kind": "timeseries", "evidence_class": "derived",
             "derivation": {"method": "quarterly totals of actual revenue (all history in the pin) and of the fiscal-year plan rows",
                            "inputs": [f"src: {asrc}", f"src: {psrc}"]},
             "provenance": {"dataset": FIN_DS, "snapshot": asnap},
             "lines": trend_lines, "points": []},
            {"id": "variance-by-line", "label": "Actual vs plan by product line", "unit": "USD M",
             "kind": "paired-bars", "pairs": {"a_label": "actual", "b_label": "plan"},
             "evidence_class": "derived",
             "derivation": {"method": "revenue summed per product line over the closed quarters, actual and plan",
                            "inputs": [f"src: {asrc}", f"src: {psrc}"]},
             "provenance": {"dataset": FIN_DS, "snapshot": asnap},
             "points": [{"label": l, "a": _musd(a), "b": _musd(pl), "variance_pct": v}
                        for l, a, pl, v in line_rows]},
            {"id": "variance-by-region", "label": "Actual vs plan by region", "unit": "USD M",
             "kind": "paired-bars", "pairs": {"a_label": "actual", "b_label": "plan"},
             "evidence_class": "derived",
             "derivation": {"method": "revenue summed per region over the closed quarters, actual and plan",
                            "inputs": [f"src: {asrc}", f"src: {psrc}"]},
             "provenance": {"dataset": FIN_DS, "snapshot": asnap},
             "points": [{"label": g, "a": _musd(a), "b": _musd(pl), "variance_pct": v}
                        for g, a, pl, v in reg_rows]},
            {"id": "variance-by-quarter", "label": "Variance vs plan by quarter", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "(actual − plan) ÷ plan per closed quarter",
                            "inputs": [f"src: {asrc}", f"src: {psrc}"]},
             "provenance": {"dataset": FIN_DS, "snapshot": asnap},
             "points": [{"label": q, "value": v} for q, _, _, v in q_rows]},
            {"id": "variance-contribution", "label": "Variance contribution ($M) by line", "unit": "USD M",
             "evidence_class": "derived",
             "derivation": {"method": "actual − plan in dollars per product line — the netting inside the composite",
                            "inputs": [f"src: {asrc}", f"src: {psrc}"]},
             "provenance": {"dataset": FIN_DS, "snapshot": asnap},
             "points": [{"label": l, "value": _musd(a - pl)} for l, a, pl, _ in line_rows]},
            {"id": "price-volume-split", "label": "Volume vs price variance bridge", "unit": "USD M",
             "evidence_class": "unavailable",
             "provenance": {"note": "the plan of record (internal-revenue-plan) carries no planned "
                                    "units — a volume/price bridge needs plan-side units; actuals "
                                    "alone cannot attribute the variance. Acquire planned units in "
                                    "the LRP export to unlock this."},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
