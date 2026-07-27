"""BQ-11 — Sold-but-underused: per-site utilization vs expected, with materiality tier.

Contract: run(corpus_root, out, pins) per computations.py module dispatch.
Deterministic; trailing 3 months = the 3 newest months in the pinned telemetry
snapshot. The account-revenue tie the question asks for is BLOCKED by a missing
site→account key — published as an unavailable series, per plans/BQ-11.md.
"""

import statistics

import computations as C

TELEM_DS = "commercial/internal-telemetry-utilization"
FLEET_DS = "commercial/internal-fleet"
SALES_DS = "commercial/internal-sales-accounts"


def run(corpus_root, out, pins):
    p = C.params_for("BQ-11")
    telem, tsnap = C.load_pin_csv(corpus_root, pins, TELEM_DS)
    fleet, fsnap = C.load_pin_csv(corpus_root, pins, FLEET_DS)
    sales, ssnap = C.load_pin_csv(corpus_root, pins, SALES_DS)
    tsrc = f"{TELEM_DS}@{tsnap}"
    fsrc = f"{FLEET_DS}@{fsnap}"
    ssrc = f"{SALES_DS}@{ssnap}"
    thr = float(p["underuse_threshold_pct"])
    win_months = int(p["window_months"])
    min_dev = int(p["min_devices"])

    months_all = sorted({r["month"] for r in telem})
    window = months_all[-win_months:]
    w0, w1 = window[0], window[-1]

    conn_by_site = {}
    for r in fleet:
        if r["connected"] == "yes":
            conn_by_site[r["site_id"]] = conn_by_site.get(r["site_id"], 0) + 1

    site = {}
    for r in telem:
        if r["month"] in window:
            s = site.setdefault(r["site_id"], {"hours": 0, "expected": 0, "region": r["region"]})
            s["hours"] += int(r["infusion_hours"])
            s["expected"] += int(r["expected_hours"])
    util_raw = {sid: 100.0 * s["hours"] / s["expected"] for sid, s in site.items()}
    util = {sid: round(u, 1) for sid, u in util_raw.items()}

    # flag and sort on the UNROUNDED ratio — a 59.95-59.99% site must not escape the
    # threshold via display rounding; util (1dp) is display-only
    flagged = sorted([sid for sid, u in util_raw.items() if u < thr],
                     key=lambda sid: util_raw[sid])
    material = [sid for sid in flagged if conn_by_site.get(sid, 0) >= min_dev]
    watch_tier = [sid for sid in flagged if sid not in material]

    rev_by_region = {}
    for r in sales:
        if r["fy"] == "FY2026H1":
            rev_by_region[r["region"]] = rev_by_region.get(r["region"], 0) + int(r["revenue_usd"])

    headline = (f"{len(flagged)} connected site(s) ran below {thr:.0f}% of expected infusion hours "
                f"over {w0}..{w1} (worst {util[flagged[0]]}%); {len(material)} clear the "
                f"≥{min_dev}-connected-device materiality bar ({', '.join(material)}); the "
                f"account-revenue tie the question asks for is blocked — no site→account key exists "
                f"in any pinned dataset" if flagged else
                f"No connected site ran below {thr:.0f}% of expected infusion hours over {w0}..{w1}")

    # E-11.1 — account-scoped expectation, evaluated at SITE level as a proxy (join gap)
    mat_txt = "; ".join(f"{sid} {util[sid]}%" for sid in material) or "none"
    exp_results = {
        "E-11.1": (f"site-level proxy (account join unavailable): {len(material)} site(s) with "
                   f">= {min_dev} connected devices below {thr:.0f}%: {mat_txt}",
                   "not-met" if material else "met",
                   ["derived: flagged-sites", f"src: {tsrc}", f"src: {fsrc}"]),
    }
    exps = C.evaluate_expectations("BQ-11", exp_results)

    narrative = {"issues": [], "risks": [], "watch": []}
    for i, sid in enumerate(material, 1):
        narrative["issues"].append({
            "id": f"I{i}", "severity": "high",
            "statement": f"{sid} runs at {util[sid]}% of expected hours across "
                         f"{conn_by_site.get(sid, 0)} connected devices over {w0}..{w1} — "
                         "sold-but-underused at material scale (early churn warning)",
            "action": "Customer-success intervention this month: confirm case-mix vs shelfware vs "
                      "connectivity root cause on site; review against renewal timeline",
            "evidence": ["derived: flagged-sites", f"src: {tsrc}", f"src: {fsrc}"]})
    narrative["risks"].append({
        "id": "R1", "severity": "high",
        "statement": "Account-level revenue-at-risk cannot be computed: no pinned dataset carries "
                     "a site→account key (sales-accounts is account-level with no site list) — "
                     "the churn-risk framing stops at regional context",
        "mitigation": "Acquire a site→account mapping (CRM account-hierarchy export) as a corpus "
                      "dataset; until then intervention priority uses site scale, not dollars",
        "evidence": ["derived: account-revenue-at-risk"]})
    if watch_tier:
        narrative["watch"].append({
            "id": "W1",
            "statement": f"{len(watch_tier)} additional site(s) below the floor but under the "
                         f"{min_dev}-device materiality bar: "
                         + ", ".join(f"{sid} ({util[sid]}%, {conn_by_site.get(sid, 0)} devices)"
                                     for sid in watch_tier)
                         + " — materiality filters priority, not visibility",
            "evidence": ["derived: flagged-sites", f"src: {fsrc}"]})
    narrative["risks"].append({
        "id": "R2", "severity": "medium",
        "statement": "expected_hours is the dataset's per-segment norm, not a contract term — a "
                     "site with a legitimately different case mix looks underused against it",
        "mitigation": "Validate the norm against contracted usage or peer-cohort baselines before "
                      "escalating beyond customer-success outreach",
        "evidence": [f"src: {tsrc}"]})

    lines = [
        "# BQ-11 — Sold but underused: utilization divergence at connected sites", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {tsrc}] [src: {fsrc}] "
        f"[config: commercial.yml]", "",
        f"## Flagged sites (trailing {win_months} months: {w0}..{w1}) [config: commercial.yml]", "",
        "_Scope: Cloud Suite CONNECTED devices only — unconnected fleet utilization is",
        "unobservable and is a stated gap, not an extrapolation. Site utilization is",
        "hours-weighted: total infusion hours ÷ total expected hours over the window",
        f"[src: {tsrc}]. Materiality = ≥{min_dev} connected devices per the fleet registry "
        f"[src: {fsrc}] [config: commercial.yml]._", "",
        "| Site | Region | Utilization (window) | Connected devices | Tier |",
        "|---|---|---|---|---|",
    ]
    for sid in flagged:
        tier = "MATERIAL — intervene" if sid in material else "below materiality bar — watch"
        lines.append(f"| {sid} [derived: flagged-sites] [src: {tsrc}] | {site[sid]['region']} | "
                     f"{util[sid]}% | {conn_by_site.get(sid, 0)} | {tier} |")
    # true median (statistics.median handles even counts); computed on unrounded
    # ratios, rounded once for display
    med_raw = statistics.median(util_raw.values())
    fleet_median = round(med_raw, 1)
    # "far below the fleet norm" is asserted only when computed (least-bad flagged site
    # ≥20pp under the median); otherwise the computed gap is stated instead
    if flagged:
        gap = round(med_raw - util_raw[flagged[-1]], 1)
        norm_note = (" — the flagged sites sit far below the fleet norm" if gap >= 20 else
                     f" — the flagged sites sit ≥{gap}pp below the fleet median")
    else:
        norm_note = ""
    lines += [
        "",
        f"- Connected-site median utilization over the window: {fleet_median}% across "
        f"{len(util)} sites{norm_note} "
        f"[derived: site-utilization] [src: {tsrc}]",
        "",
        "## Churn-risk framing — what the data allows", "",
        "- Account-level revenue at risk: NOT COMPUTABLE — no site→account key in any pinned",
        "  dataset; published as an unavailable series naming the missing join",
        "  [derived: account-revenue-at-risk].",
        f"- Regional context (explicitly context, not attribution): FY2026H1 direct-book revenue "
        + ", ".join(f"{reg} ${rev_by_region.get(reg, 0):,}"
                    for reg in sorted({site[s]['region'] for s in flagged}))
        + f" — flagged sites sit inside these books [src: {ssrc}]",
        "",
        "## Monthly trajectory (worst three flagged sites vs fleet median)", "",
        f"- Charted per month across the full snapshot span; pick rule: the three lowest-utilization "
        f"flagged sites plus the connected-fleet median as reference (≤4 lines) "
        f"[derived: monthly-utilization] [src: {tsrc}]",
    ]
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Utilization measured from [src: {tsrc}]; connected-device counts from the fleet "
        f"registry [src: {fsrc}]; thresholds and window from [config: commercial.yml].",
        f"- Regional revenue context from [src: {ssrc}] (demo-fabricated direct book).",
        "- E-11.1 is account-scoped but evaluated at site level as a proxy [derived: flagged-sites]",
        "  — the site→account join gap is the reason, and closing it is the named fix.",
    ]

    # monthly lines: worst 3 flagged sites + fleet median
    worst3 = flagged[:3]
    by_site_month = {}
    monthly_ratios = {m: [] for m in months_all}
    per_site_month = {}
    for r in telem:
        key = (r["site_id"], r["month"])
        e = per_site_month.setdefault(key, [0, 0])
        e[0] += int(r["infusion_hours"])
        e[1] += int(r["expected_hours"])
    for (sid, m), (h, ex) in per_site_month.items():
        by_site_month[(sid, m)] = round(100.0 * h / ex, 1)
        monthly_ratios[m].append(100.0 * h / ex)
    tlines = [{"label": sid,
               "points": [{"x": m + "-01", "y": by_site_month.get((sid, m), 0)}
                          for m in months_all]} for sid in worst3]
    tlines.append({"label": "connected-fleet median",
                   "points": [{"x": m + "-01",
                               "y": round(statistics.median(monthly_ratios[m]), 1)}
                              for m in months_all]})

    data = {
        "bq": "BQ-11",
        "series": [
            {"id": "flagged-stat", "label": "Underused connected sites", "unit": "sites",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": f"sites with hours-weighted utilization < {thr:.0f}% over the "
                                      f"trailing {win_months} months; material = ≥{min_dev} "
                                      "connected devices",
                            "inputs": [f"src: {tsrc}", f"src: {fsrc}", "config: commercial.yml"]},
             "provenance": {"dataset": TELEM_DS, "snapshot": tsnap},
             "points": [{"label": f"below {thr:.0f}% of expected hours ({w0}..{w1})",
                         "value": len(flagged)},
                        {"label": f"of which material (≥{min_dev} connected devices)",
                         "value": len(material)}]},
            {"id": "site-utilization", "label": "Window utilization — flagged sites vs fleet median",
             "unit": "%", "evidence_class": "measured",
             "provenance": {"dataset": TELEM_DS, "snapshot": tsnap},
             "points": [{"label": sid, "value": util[sid],
                         "connected_devices": conn_by_site.get(sid, 0)} for sid in flagged]
                       + [{"label": "connected-fleet median", "value": fleet_median}]},
            {"id": "flagged-sites", "label": "Flagged sites (tiered by materiality)", "unit": "",
             "evidence_class": "derived",
             "derivation": {"method": "utilization threshold + connected-device materiality bar",
                            "inputs": [f"src: {tsrc}", f"src: {fsrc}", "config: commercial.yml"]},
             "provenance": {"dataset": TELEM_DS, "snapshot": tsnap},
             "points": [{"label": sid,
                         "value": ("material" if sid in material else "watch (below materiality bar)")}
                        for sid in flagged]},
            {"id": "monthly-utilization", "label": "Monthly utilization — worst 3 flagged sites vs median",
             "unit": "%", "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": TELEM_DS, "snapshot": tsnap},
             "lines": tlines, "points": []},
            {"id": "account-revenue-at-risk", "label": "Account revenue tied to flagged sites",
             "unit": "USD", "evidence_class": "unavailable",
             "provenance": {"note": "no site→account key in any pinned dataset (sales-accounts is "
                                    "account-level with no site list) — needs a CRM "
                                    "account-hierarchy export as a corpus dataset; regional revenue "
                                    "shown as context only"},
             "points": []},
            {"id": "region-revenue-context", "label": "FY2026H1 direct-book revenue by region (context)",
             "unit": "USD", "evidence_class": "measured",
             "provenance": {"dataset": SALES_DS, "snapshot": ssnap},
             "points": [{"label": reg, "value": rev_by_region[reg]}
                        for reg in sorted(rev_by_region)]},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
