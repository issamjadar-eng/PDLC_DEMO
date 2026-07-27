"""BQ-01 — Which lines fund the company, which consume it (trailing-4Q funding map).

Deterministic: computes ONLY from the pinned internal-financials snapshot; the window
anchors at the latest period IN the data (no clocks). See plans/BQ-01.md for the
committed definitions (window, gross-margin basis, funds-vs-consumes rule, the
<=4-line trend grouping).
"""

import computations as C

FIN_DS = "commercial/internal-financials"


def _q_iso(period):
    """'2025-Q3' -> '2025-07-01' (first day of the calendar quarter)."""
    y, q = period.split("-Q")
    return f"{y}-{(int(q) - 1) * 3 + 1:02d}-01"


def _musd(v):
    return f"${v / 1e6:,.1f}M"


def run(corpus_root, out, pins):
    p = C.params_for("BQ-01")
    rows, snap = C.load_pin_csv(corpus_root, pins, FIN_DS)
    src = f"{FIN_DS}@{snap}"
    n_trail = int(p["trailing_quarters"])
    top_n_lines = int(p["timeseries_top_lines"])

    periods = sorted({r["period"] for r in rows})
    window = periods[-n_trail:]
    prior = periods[-2 * n_trail:-n_trail]
    lines_all = sorted({r["product_line"] for r in rows})

    def agg(line, prds):
        rev = sum(int(r["revenue_usd"]) for r in rows if r["product_line"] == line and r["period"] in prds)
        cogs = sum(int(r["cogs_usd"]) for r in rows if r["product_line"] == line and r["period"] in prds)
        return rev, rev - cogs

    stats = {}
    for ln in lines_all:
        rev, gm = agg(ln, window)
        prev_rev, prev_gm = agg(ln, prior)
        stats[ln] = {
            "rev": rev, "gm": gm, "gm_pct": C.pct(gm, rev),
            "prior_gm_pct": C.pct(prev_gm, prev_rev),
        }
    total_rev = sum(s["rev"] for s in stats.values())
    total_gm = sum(s["gm"] for s in stats.values())
    for ln in lines_all:
        stats[ln]["gm_share"] = C.pct(stats[ln]["gm"], total_gm)
        stats[ln]["gm_pct_delta"] = round(stats[ln]["gm_pct"] - stats[ln]["prior_gm_pct"], 1)

    ranked = sorted(lines_all, key=lambda ln: -stats[ln]["gm"])
    negatives = [ln for ln in lines_all if stats[ln]["gm"] < 0]
    funders = ranked[:2]
    funders_share = round(sum(stats[ln]["gm_share"] for ln in funders), 1)
    pair_gm = sum(stats[ln]["gm"] for ln in funders)
    compressing = sorted((ln for ln in lines_all if stats[ln]["gm_pct_delta"] <= -1.0),
                         key=lambda ln: stats[ln]["gm_pct_delta"])

    headline = (f"{funders[0]} and {funders[1]} fund the company — {funders_share}% of "
                f"trailing-4Q gross margin ({_musd(pair_gm)} of the portfolio's "
                f"{_musd(total_gm)} GM on {_musd(total_rev)} revenue, "
                f"window {window[0]}..{window[-1]}); "
                + (f"{', '.join(negatives)} gross-margin NEGATIVE"
                   if negatives else "all six lines gross-margin positive")
                + (f"; margins compressing on {', '.join(compressing)}" if compressing else ""))

    # trend chart: top-N lines by trailing-4Q revenue individually, rest aggregated
    top_rev = sorted(lines_all, key=lambda ln: -stats[ln]["rev"])[:top_n_lines]
    rest = [ln for ln in lines_all if ln not in top_rev]
    per_q = {(ln, q): 0 for ln in lines_all for q in periods}
    for r in rows:
        per_q[(r["product_line"], r["period"])] += int(r["revenue_usd"])
    trend_lines = [{"label": ln,
                    "points": [{"x": _q_iso(q), "y": round(per_q[(ln, q)] / 1e6, 2)} for q in periods]}
                   for ln in top_rev]
    trend_lines.append({"label": f"other ({'+'.join(rest)})",
                        "points": [{"x": _q_iso(q),
                                    "y": round(sum(per_q[(ln, q)] for ln in rest) / 1e6, 2)}
                                   for q in periods]})

    # narrative — deterministic rules over the computed facts
    narrative = {"issues": [], "risks": [], "watch": []}
    for i, ln in enumerate(negatives, 1):
        narrative["issues"].append({
            "id": f"I{i}", "severity": "high",
            "statement": f"{ln} is gross-margin negative over the trailing four quarters "
                         f"({_musd(stats[ln]['gm'])} on {_musd(stats[ln]['rev'])})",
            "action": "Bring a keep/fix/exit analysis to the next portfolio review",
            "evidence": ["derived: gm-by-line", f"src: {src}"],
        })
    rn = 0
    for ln in compressing:
        rn += 1
        narrative["risks"].append({
            "id": f"R{rn}", "severity": "medium",
            "statement": f"{ln} gross margin is compressing — {stats[ln]['gm_pct']}% in the trailing "
                         f"window vs {stats[ln]['prior_gm_pct']}% in the prior four quarters "
                         f"({stats[ln]['gm_pct_delta']} pts)",
            "mitigation": "Review pricing and COGS drivers for the line; set a floor at which "
                          "the phase-out conversation formally opens",
            "evidence": ["derived: gm-trend", f"src: {src}"],
        })
    if stats[ranked[0]]["gm_share"] > 50:
        rn += 1
        narrative["risks"].append({
            "id": f"R{rn}", "severity": "medium",
            "statement": f"Funding is concentrated: {ranked[0]} alone carries "
                         f"{stats[ranked[0]]['gm_share']}% of total gross margin — a single-line "
                         f"shock is a company-level shock",
            "mitigation": "Track the concentration alongside the BQ-02 customer-concentration "
                          "read; both feed the same board risk discussion",
            "evidence": ["derived: gm-share", f"src: {src}"],
        })
    narrative["watch"].append({
        "id": "W1",
        "statement": "Gross margin only — no opex allocation exists per line, so a GM-positive "
                     "line can still consume the company at operating level (stated data gap)",
        "evidence": ["derived: opex-by-line"],
    })

    exp_results = {
        "E-01.1": ((f"{', '.join(negatives)} negative" if negatives
                    else f"all lines positive; thinnest is {min(lines_all, key=lambda l: stats[l]['gm_pct'])} "
                         f"at {min(s['gm_pct'] for s in stats.values())}%"),
                   "not-met" if negatives else "met",
                   ["derived: gm-by-line"]),
    }
    exps = C.evaluate_expectations("BQ-01", exp_results)

    rl = [
        "# BQ-01 — Funding map: which lines fund the company, which consume it", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}]", "",
        f"## Trailing-4Q economics by line (window {window[0]}..{window[-1]} [src: {src}])", "",
        "| Line | Revenue | Gross margin | GM % | Share of total GM | GM % vs prior 4Q |",
        "|---|---|---|---|---|---|",
    ]
    for ln in ranked:
        s = stats[ln]
        rl.append(f"| {ln} [src: {src}] [derived: gm-by-line] | {_musd(s['rev'])} | {_musd(s['gm'])} | "
                  f"{s['gm_pct']}% | {s['gm_share']}% | {s['gm_pct_delta']:+.1f} pts |")
    rl += [
        "",
        f"- Window = trailing {n_trail} quarters anchored at the latest period in the pinned "
        f"snapshot ({window[-1]}) — no clocks [config: commercial.yml] [src: {src}]",
        f"- Totals: revenue {_musd(total_rev)}, gross margin {_musd(total_gm)} "
        f"({C.pct(total_gm, total_rev)}%) [derived: totals-stat] [src: {src}]",
        f"- Quarterly revenue trajectory is charted for the top {top_n_lines} lines by trailing-4Q "
        f"revenue, remaining lines aggregated as one series to respect the chart-line cap "
        f"[config: commercial.yml] [derived: revenue-trend]",
    ]
    rl += C.expectations_section(exps)
    rl += C.narrative_section(narrative)
    rl += [
        "## Data gap (stated, not papered over)", "",
        "- No per-line operating-expense allocation exists in the corpus — \"consumes the",
        "  company\" is asserted at gross-margin level only; the opex series is marked",
        "  unavailable [derived: opex-by-line].",
        "",
        "## Method & provenance", "",
        f"- Revenue and COGS measured from [src: {src}] (all regions, all revenue types);",
        f"  gross margin, shares, and margin drift are arithmetic derivations",
        f"  [derived: gm-by-line] [derived: gm-trend].",
        f"- Funds-vs-consumes rule and the trend-chart grouping are committed in the analysis",
        f"  plan; window length and grouping constants live in [config: commercial.yml].",
    ]

    data = {
        "bq": "BQ-01",
        "series": [
            {"id": "totals-stat", "label": "Trailing-4Q portfolio totals", "unit": "mixed",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "portfolio totals = Σ line revenue and Σ (revenue − COGS) "
                                      "over the trailing window; funder-pair GM and its share = "
                                      "pair GM ÷ total GM",
                            "inputs": [f"src: {src}", "derived: gm-by-line"]},
             "provenance": {"dataset": FIN_DS, "snapshot": snap},
             "points": [
                 {"label": f"revenue, {window[0]}..{window[-1]} ($M)", "value": round(total_rev / 1e6, 1)},
                 {"label": "gross margin ($M)", "value": round(total_gm / 1e6, 1)},
                 {"label": f"gross margin from {funders[0]} + {funders[1]} ($M)",
                  "value": round(pair_gm / 1e6, 1)},
                 {"label": f"of gross margin from {funders[0]} + {funders[1]} (%)", "value": funders_share},
             ]},
            {"id": "gm-by-line", "label": "Trailing-4Q revenue vs gross margin by line ($M)",
             "unit": "$M", "kind": "paired-bars",
             "pairs": {"a_label": "revenue", "b_label": "gross margin"},
             "evidence_class": "derived",
             "derivation": {"method": "per line over the trailing four quarters: revenue = "
                                      "Σ revenue_usd (measured); gross margin = revenue − COGS",
                            "inputs": [f"src: {src}"]},
             "provenance": {"dataset": FIN_DS, "snapshot": snap},
             "points": [{"label": ln, "a": round(stats[ln]["rev"] / 1e6, 1),
                         "b": round(stats[ln]["gm"] / 1e6, 1)} for ln in ranked]},
            {"id": "gm-share", "label": "Share of total gross margin by line", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "line trailing-4Q gross margin ÷ total trailing-4Q gross margin",
                            "inputs": [f"src: {src}", "derived: gm-by-line"]},
             "provenance": {"dataset": FIN_DS, "snapshot": snap},
             "points": [{"label": ln, "value": stats[ln]["gm_share"]} for ln in ranked]},
            {"id": "gm-trend", "label": "GM% — prior 4Q vs trailing 4Q by line", "unit": "%",
             "kind": "paired-bars", "pairs": {"a_label": "trailing 4Q", "b_label": "prior 4Q"},
             "evidence_class": "derived",
             "derivation": {"method": "per line: (revenue − COGS) ÷ revenue over the trailing four "
                                      "quarters vs the four quarters before them",
                            "inputs": [f"src: {src}", "config: commercial.yml"]},
             "provenance": {"dataset": FIN_DS, "snapshot": snap},
             "points": [{"label": ln, "a": stats[ln]["gm_pct"], "b": stats[ln]["prior_gm_pct"]}
                        for ln in ranked]},
            {"id": "revenue-trend", "label": f"Quarterly revenue by line ($M; top {top_n_lines} + other)",
             "unit": "$M", "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": FIN_DS, "snapshot": snap},
             "lines": trend_lines, "points": []},
            {"id": "opex-by-line", "label": "Operating expense by line", "unit": "$M",
             "evidence_class": "unavailable",
             "provenance": {"note": "no opex-allocation dataset in the corpus — funds/consumes is "
                                    "a gross-margin statement until one exists"},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, rl, data)
