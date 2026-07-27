"""BQ-22 — Closed loop: do field signals land as design inputs / upgrade items,
or die in a spreadsheet?

Per plans/BQ-22.md: disposition funnel over the trailing-12-month cohort and lifetime,
died-in-a-spreadsheet = no-action + open>SLA, SLA verdict (E-22.1), time-to-disposition
distribution, and named loop-closed exemplars. Deterministic: as-of = latest date in
the pinned register; no clocks, no network.
"""

import datetime as dt

import computations as C

SIGNALS_DS = "commercial/internal-signal-register"
LANDED_DESIGN = ("design-input", "requirement-change")
LANDED_UPGRADE = ("upgrade-item",)
BUCKETS = [(0, 30, "0–30 days"), (31, 60, "31–60 days"), (61, 90, "61–90 days"),
           (91, 120, "91–120 days"), (121, 180, "121–180 days"), (181, 10 ** 6, ">180 days")]


def month_range(a: str, b: str):
    """Every YYYY-MM from a to b inclusive (zero-fill scaffold)."""
    ya, ma = int(a[:4]), int(a[5:7])
    yb, mb = int(b[:4]), int(b[5:7])
    out = []
    while (ya, ma) <= (yb, mb):
        out.append(f"{ya:04d}-{ma:02d}")
        ma += 1
        if ma == 13:
            ya, ma = ya + 1, 1
    return out


def run(corpus_root, out, pins):
    p = C.params_for("BQ-22")
    sla = int(p["sla_days"])
    rows, snap = C.load_pin_csv(corpus_root, pins, SIGNALS_DS)
    src = f"{SIGNALS_DS}@{snap}"

    # Fail loudly if the register ever carries a disposition outside the funnel
    # vocabulary — a new value would silently escape every bucket (and both "died"
    # and "landed") while the printed Total still counts it (review finding F-22-3).
    known_disp = set(LANDED_DESIGN) | set(LANDED_UPGRADE) | {"monitoring", "no-action", "open"}
    unknown_disp = sorted({r["disposition"] for r in rows} - known_disp)
    if unknown_disp:
        raise SystemExit(f"BQ-22: unexpected disposition value(s) {unknown_disp} — "
                         f"extend the funnel buckets before publishing")

    as_of = max([r["opened_date"] for r in rows] +
                [r["closed_date"] for r in rows if r["closed_date"]])
    win_start = (dt.date.fromisoformat(as_of) - dt.timedelta(days=365)).isoformat()
    cohort = [r for r in rows if r["opened_date"] > win_start]

    def age_days(r):
        return (dt.date.fromisoformat(as_of) - dt.date.fromisoformat(r["opened_date"])).days

    def disp_days(r):
        return (dt.date.fromisoformat(r["closed_date"])
                - dt.date.fromisoformat(r["opened_date"])).days

    def funnel(sub):
        design = [r for r in sub if r["disposition"] in LANDED_DESIGN]
        upgrade = [r for r in sub if r["disposition"] in LANDED_UPGRADE]
        monitoring = [r for r in sub if r["disposition"] == "monitoring"]
        no_action = [r for r in sub if r["disposition"] == "no-action"]
        stale_open = [r for r in sub if r["disposition"] == "open" and age_days(r) > sla]
        recent_open = [r for r in sub if r["disposition"] == "open" and age_days(r) <= sla]
        died = no_action + stale_open
        return {"design": design, "upgrade": upgrade, "monitoring": monitoring,
                "no_action": no_action, "stale_open": stale_open,
                "recent_open": recent_open, "died": died}

    fc, fl = funnel(cohort), funnel(rows)
    died_pct_c = C.pct(len(fc["died"]), len(cohort))
    died_pct_l = C.pct(len(fl["died"]), len(rows))
    landed_c = len(fc["design"]) + len(fc["upgrade"])
    landed_l = len(fl["design"]) + len(fl["upgrade"])

    # --- SLA verdict (E-22.1) over the cohort, per plan ----------------------
    dispositioned = [r for r in cohort if r["closed_date"]]
    within = [r for r in dispositioned if disp_days(r) <= sla]
    breach = [r for r in dispositioned if disp_days(r) > sla] + fc["stale_open"]
    pending = fc["recent_open"]
    sla_pct = C.pct(len(within), len(within) + len(breach))

    # --- time-to-disposition distribution (all dispositioned, lifetime) ------
    all_disp = [r for r in rows if r["closed_date"]]
    dist = []
    for lo, hi, label in BUCKETS:
        dist.append({"label": label,
                     "value": sum(1 for r in all_disp if lo <= disp_days(r) <= hi)})
    # True median (mean of the middle pair for even n) — sorted[n//2] is the upper
    # middle element, which overstated the median (red-team finding RT-22-1)
    median_days = C._median([disp_days(r) for r in all_disp]) if all_disp else None

    # --- loop-closed exemplars ----------------------------------------------
    exemplars = sorted((r for r in rows if r["disposition"] in LANDED_DESIGN + LANDED_UPGRADE),
                       key=lambda r: r["opened_date"])
    over_ex = [r for r in exemplars if r["category"] == "over-delivery"]

    # E-22.1 verdict computed once; the headline's met/NOT-met clause derives from it —
    # never narrated (review finding F-22-1: a breach-free refresh must not render a
    # self-contradicting report).
    e221_met = not breach
    headline = (f"{len(fl['died'])} of {len(rows)} lifetime signals ({died_pct_l}%) died in a "
                f"spreadsheet (no-action or open past the {sla}-day SLA); trailing 12 months: "
                f"{len(fc['died'])} of {len(cohort)} ({died_pct_c}%) died vs {landed_c} landed in "
                f"design/upgrade — "
                + (f"and only {sla_pct}% of adjudicated cohort signals met the SLA, so E-22.1 is "
                   f"NOT met" if not e221_met else
                   f"and {sla_pct}% of adjudicated cohort signals met the SLA, so E-22.1 is met"))

    # --- monthly trend: opened vs dispositioned (zero-filled) ----------------
    span = month_range(min(r["opened_date"] for r in rows)[:7], as_of[:7])
    opened_m, closed_m = {}, {}
    for r in rows:
        m = r["opened_date"][:7]
        opened_m[m] = opened_m.get(m, 0) + 1
        if r["closed_date"]:
            cm = r["closed_date"][:7]
            closed_m[cm] = closed_m.get(cm, 0) + 1
    trend_lines = [
        {"label": "signals opened", "points": [{"x": m + "-01", "y": opened_m.get(m, 0)} for m in span]},
        {"label": "dispositions closed", "points": [{"x": m + "-01", "y": closed_m.get(m, 0)} for m in span]},
    ]

    # --- expectations --------------------------------------------------------
    exp_results = {
        "E-22.1": (f"{sla_pct}% of adjudicated cohort signals dispositioned within {sla} days "
                   f"({len(within)} within, {len(breach)} breached incl. {len(fc['stale_open'])} "
                   f"stale-open; {len(pending)} recent-open pending, excluded)",
                   "met" if e221_met else "not-met",
                   ["derived: sla-compliance", f"src: {src}"]),
    }
    exps = C.evaluate_expectations("BQ-22", exp_results)

    # --- narrative -----------------------------------------------------------
    narrative = {"issues": [], "risks": [], "watch": []}
    narrative["issues"].append({
        "id": "I1", "severity": "high",
        "statement": f"{died_pct_l}% of lifetime signals ({len(fl['no_action'])} no-action + "
                     f"{len(fl['stale_open'])} open past {sla} days) never reached the design or "
                     f"upgrade pipeline — the post-market → design-input loop is leaking",
        "action": "Triage every stale-open signal to a disposition this quarter; require a "
                  "recorded rationale for no-action dispositions; put SLA aging on the "
                  "management-review dashboard",
        "evidence": ["derived: funnel", f"src: {src}", "config: commercial.yml"],
    })
    if breach:
        narrative["issues"].append({
            "id": "I2", "severity": "medium",
            "statement": f"Even signals that DO get dispositioned run slow: only {sla_pct}% of the "
                         f"adjudicated cohort met the {sla}-day SLA (median lifetime "
                         f"time-to-disposition {median_days} days)",
            "action": "Set a triage checkpoint at day 30 for every open signal; report aging "
                      "weekly to the signal-review board",
            "evidence": ["derived: sla-compliance", "derived: disposition-distribution", f"src: {src}"],
        })
    narrative["risks"].append({
        "id": "R1", "severity": "medium",
        "statement": f"The {sla}-day SLA is a stand-in, not yet traced to the post-market SOP — "
                     f"the verdict is only as good as its threshold",
        "mitigation": "Verify the SLA against the QMS post-market surveillance SOP and mark "
                      "E-22.1 validated",
        "evidence": ["config: commercial.yml"],
    })
    narrative["risks"].append({
        "id": "R2", "severity": "medium",
        "statement": "Landed dispositions are trusted from the register's DI-/REQ-/UPG- refs — "
                     "no cross-system trace yet verifies those refs exist in the requirements or "
                     "upgrade systems",
        "mitigation": "Build the register ↔ DHF ↔ upgrade-campaign trace as a follow-on check",
        "evidence": ["derived: exemplars"],
    })
    narrative["watch"].append({
        "id": "W1",
        "statement": f"The loop CAN close: {len(exemplars)} signals landed with refs"
                     + (f", including {'both' if len(over_ex) == 2 else str(len(over_ex))} "
                        f"over-delivery signal(s) "
                        f"({', '.join(r['signal_id'] + ' → ' + r['disposition_ref'] for r in over_ex)})"
                        if over_ex else "")
                     + " — the counter-beat to BQ-20's franchise-killer watch",
        "evidence": ["derived: exemplars", f"src: {src}"],
    })

    # --- report --------------------------------------------------------------
    lines = [
        "# BQ-22 — Closed loop: field signals → design inputs, or death by spreadsheet", "",
        C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [config: commercial.yml]", "",
        f"## Disposition funnel (trailing 12 months: opened after {win_start}; anchor {as_of})", "",
        "_Died in a spreadsheet = `no-action` plus signals still open past the "
        f"{sla}-day SLA [config: commercial.yml] — an undispositioned signal is functionally dead "
        "even though the register calls it open (plan definition)._", "",
        "| Funnel bucket | Trailing 12 months | Lifetime |",
        "|---|---|---|",
    ]
    for key, label in (("design", "Landed as design input / requirement change"),
                       ("upgrade", "Landed in the upgrade pipeline"),
                       ("monitoring", "Monitoring (explicit watch decision)"),
                       ("no_action", "No action"),
                       ("stale_open", f"Still open > {sla} days (functionally dead)"),
                       ("recent_open", f"Open ≤ {sla} days (in process)")):
        lines.append(f"| {label} [derived: funnel] [src: {src}] | {len(fc[key])} | {len(fl[key])} |")
    lines += [
        f"| **Total** [src: {src}] | {len(cohort)} | {len(rows)} |",
        "",
        f"- Died in a spreadsheet: {len(fc['died'])} of {len(cohort)} trailing ({died_pct_c}%); "
        f"{len(fl['died'])} of {len(rows)} lifetime ({died_pct_l}%) [derived: funnel] [src: {src}]",
        f"- Landed (design + upgrade): {landed_c} trailing, {landed_l} lifetime "
        f"[derived: funnel] [src: {src}]",
        "",
        "## Time to disposition (lifetime, all dispositioned signals)", "",
        "| Days opened → closed | Signals |",
        "|---|---|",
    ]
    for d in dist:
        lines.append(f"| {d['label']} [derived: disposition-distribution] [src: {src}] | {d['value']} |")
    lines += [
        "",
        f"- Median time to disposition: {median_days} days — the {sla}-day SLA line sits between "
        f"the third and fourth buckets [derived: disposition-distribution] [src: {src}] "
        f"[config: commercial.yml]",
        f"- Monthly signals opened vs dispositions closed are charted (zero-filled) "
        f"[derived: signal-trend] [src: {src}]",
        "",
        "## Where the loop DID close (exemplars with refs)", "",
        "| Signal | Opened | Category | Disposition | Ref | Days to disposition |",
        "|---|---|---|---|---|---|",
    ]
    for r in exemplars:
        lines.append(f"| {r['signal_id']} [src: {src}] | {r['opened_date']} | {r['category']} | "
                     f"{r['disposition']} | {r['disposition_ref']} | {disp_days(r)} |")
    # Over-delivery closure sentence derived from the same computed exemplar set as W1
    # (count- and disposition-aware), never a duplicate string literal (finding F-22-2).
    if over_ex:
        oe_disp = sorted({r["disposition"].replace("-", " ") for r in over_ex})
        oe_qty = "Both" if len(over_ex) == 2 else str(len(over_ex))
        oe_noun = "signal" if len(over_ex) == 1 else "signals"
        oe_plural = "s" if len(over_ex) > 1 and len(oe_disp) == 1 else ""
        over_body = (f"- {oe_qty} over-delivery {oe_noun} closed the loop into "
                     f"{', '.join(oe_disp)}{oe_plural} "
                     f"({', '.join(r['signal_id'] + ' → ' + r['disposition_ref'] for r in over_ex)}) — "
                     f"see BQ-20's franchise-killer watch [derived: exemplars] [src: {src}]")
    else:
        over_body = (f"- No over-delivery signal appears among the loop-closed exemplars — "
                     f"see BQ-20's franchise-killer watch [derived: exemplars] [src: {src}]")
    lines += [
        "",
        over_body,
        "- Refs are trusted from the register; a cross-system trace (register ↔ DHF ↔ upgrade",
        "  campaign) has not yet verified them (stated gap, per the plan).",
    ]
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- All funnel and SLA facts measured from [src: {src}]; SLA and window constants "
        f"[config: commercial.yml].",
        f"- As-of anchor = latest date present in the pinned register ({as_of}) — no clocks; "
        f"the trailing window is the 365 days ending there [derived: funnel] [src: {src}].",
        "- SLA verdict excludes recent-open signals from the denominator (in-process, counted",
        f"  and stated) [derived: sla-compliance] [src: {src}].",
    ]

    data = {
        "bq": "BQ-22",
        "series": [
            {"id": "died-stat", "label": "Died in a spreadsheet", "unit": "%",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "no-action signals + signals open past the SLA at the "
                                      "as-of anchor, over the signal population",
                            "inputs": [f"src: {src}", "config: commercial.yml"]},
             "provenance": {"dataset": SIGNALS_DS, "snapshot": snap},
             "points": [{"label": f"of {len(rows)} lifetime signals", "value": died_pct_l},
                        {"label": f"of {len(cohort)} trailing-12-month signals", "value": died_pct_c}]},
            {"id": "funnel", "label": "Disposition funnel: trailing 12 months vs lifetime",
             "unit": "signals", "kind": "paired-bars",
             "pairs": {"a_label": "trailing 12 months", "b_label": "lifetime"},
             "evidence_class": "derived",
             "derivation": {"method": "signals bucketed by disposition; died = no-action + open "
                                      "past SLA at the as-of anchor; cohort = opened in the 365 "
                                      "days ending at the anchor",
                            "inputs": [f"src: {src}", "config: commercial.yml"]},
             "provenance": {"dataset": SIGNALS_DS, "snapshot": snap},
             "points": [
                 {"label": "landed: design", "a": len(fc["design"]), "b": len(fl["design"])},
                 {"label": "landed: upgrade", "a": len(fc["upgrade"]), "b": len(fl["upgrade"])},
                 {"label": "monitoring", "a": len(fc["monitoring"]), "b": len(fl["monitoring"])},
                 {"label": "no action", "a": len(fc["no_action"]), "b": len(fl["no_action"])},
                 {"label": f"open > {sla}d", "a": len(fc["stale_open"]), "b": len(fl["stale_open"])},
                 {"label": f"open ≤ {sla}d", "a": len(fc["recent_open"]), "b": len(fl["recent_open"])},
             ]},
            {"id": "disposition-distribution", "label": "Time to disposition (days)",
             "unit": "signals", "evidence_class": "derived",
             "derivation": {"method": "closed_date − opened_date for every dispositioned signal, "
                                      "bucketed 0–30/31–60/61–90/91–120/121–180/>180",
                            "inputs": [f"src: {src}"]},
             "provenance": {"dataset": SIGNALS_DS, "snapshot": snap},
             "points": dist},
            {"id": "sla-compliance", "label": f"Cohort SLA compliance ({sla} days)", "unit": "signals",
             "evidence_class": "derived",
             "derivation": {"method": "adjudicated cohort signals split by (closed_date − "
                                      "opened_date) <= SLA; stale-open counted as breach; "
                                      "recent-open excluded as pending",
                            "inputs": [f"src: {src}", "config: commercial.yml"]},
             "provenance": {"dataset": SIGNALS_DS, "snapshot": snap},
             "points": [{"label": "within SLA", "value": len(within)},
                        {"label": "breached", "value": len(breach)},
                        {"label": "pending (open ≤ SLA)", "value": len(pending)}]},
            {"id": "signal-trend", "label": "Signals opened vs dispositions closed per month",
             "unit": "signals/month", "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": SIGNALS_DS, "snapshot": snap},
             "lines": trend_lines, "points": []},
            {"id": "exemplars", "label": "Loop-closed exemplars (signal → ref)", "unit": "",
             "evidence_class": "measured",
             "provenance": {"dataset": SIGNALS_DS, "snapshot": snap},
             "points": [{"label": r["signal_id"],
                         "value": f"{r['category']} → {r['disposition']} ({r['disposition_ref']})"}
                        for r in exemplars]},
            {"id": "ref-verification", "label": "Cross-system verification of disposition refs",
             "unit": "", "evidence_class": "unavailable",
             "provenance": {"note": "register ↔ DHF ↔ upgrade-campaign trace not yet built — "
                                    "landed dispositions are trusted from the register's refs"},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
