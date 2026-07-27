"""BQ-20 — Franchise-killer signal watch: opioid over-delivery / PCA-by-proxy.

Per plans/BQ-20.md: event-level enumeration of watch-category records (single events,
not trends, are the signal), signal-register loop linkage, and the REAL class-wide
MAUDE PCA trend as context (counts only — no denominator, lag tail excluded).
Deterministic: all anchors derive from the pinned snapshots; no clocks, no network.
"""

import datetime as dt

import computations as C

COMPLAINTS_DS = "commercial/internal-complaints"
SIGNALS_DS = "commercial/internal-signal-register"
MAUDE_PCA_DS = "commercial/openfda-maude-pca-monthly"
DOCKET_DS = "commercial/internal-regulatory-docket"
# Trailing months excluded from the MAUDE chart: the dataset README warns the
# reporting-lag tail runs ~3–6 months, so the trim sits at the lower bound of that
# range (was 2 — shallower than the dataset's own warning; red-team finding RT-20-2).
LAG_TRIM_MONTHS = 3


def month_range(a: str, b: str):
    """Every YYYY-MM from a to b inclusive — zero-filled monthly series make
    'single events' visible against a flatline instead of hiding empty months."""
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
    p = C.params_for("BQ-20")
    watch = list(p["watch_categories"])
    crows, csnap = C.load_pin_csv(corpus_root, pins, COMPLAINTS_DS)
    srows, ssnap = C.load_pin_csv(corpus_root, pins, SIGNALS_DS)
    mrows, msnap = C.load_pin_csv(corpus_root, pins, MAUDE_PCA_DS)
    drows, dsnap = C.load_pin_csv(corpus_root, pins, DOCKET_DS)
    csrc = f"{COMPLAINTS_DS}@{csnap}"
    ssrc = f"{SIGNALS_DS}@{ssnap}"
    msrc = f"{MAUDE_PCA_DS}@{msnap}"
    dsrc = f"{DOCKET_DS}@{dsnap}"

    # --- internal watch-category complaint events (event-level, per plan) ----
    events = sorted((r for r in crows if r["category"] in watch),
                    key=lambda r: r["date_opened"])
    by_cat = {w: [r for r in events if r["category"] == w] for w in watch}
    over = by_cat.get("over-delivery", [])
    proxy = by_cat.get("pca-by-proxy-suspected", [])
    mdr_filed = [r for r in events if r["mdr_filed"] == "yes"]
    under_inv = [r for r in events if r["status"] == "under-investigation"]

    # --- signal-register loop linkage (joined by category, per plan) ---------
    wsignals = sorted((r for r in srows if r["category"] in watch),
                      key=lambda r: r["opened_date"])
    closed_loop = [r for r in wsignals
                   if r["disposition"] in ("design-input", "requirement-change", "upgrade-item")]
    loop_pairs = ", ".join(f"{r['signal_id']} → {r['disposition_ref']}"
                           for r in closed_loop if r["disposition_ref"])

    # --- regulatory-docket linkage (category-level join, per plan) -----------
    # Derived from the pinned docket rows — never a string literal: open MDR-type
    # records whose category is on the watch list. The join is category-level only
    # (no shared key exists between the complaint log and the docket).
    dock_watch = sorted((r for r in drows
                         if r["type"] == "mdr" and r["status"] == "open"
                         and r["category"] in watch),
                        key=lambda r: r["opened_date"])
    dock_ids = ", ".join(r["record_id"] for r in dock_watch) or "none open"
    over_ui = [r for r in over if r["status"] == "under-investigation"]

    # --- real class-wide MAUDE PCA monthly trend (counts only) ---------------
    monthly = {}
    for r in mrows:
        t = r["term"]
        m = f"{t[:4]}-{t[4:6]}"
        monthly[m] = monthly.get(m, 0) + int(r["count"])
    months_sorted = sorted(monthly)
    lag_cut = months_sorted[-LAG_TRIM_MONTHS:] if len(months_sorted) > LAG_TRIM_MONTHS else []
    charted = [m for m in months_sorted if m not in lag_cut]
    hist_pts = [{"x": m + "-01", "y": monthly[m]} for m in charted]
    total_class = sum(monthly[m] for m in charted)

    # --- internal watch timeseries: monthly events per category, zero-filled --
    span = month_range(min(r["date_opened"] for r in crows)[:7],
                       max(r["date_opened"] for r in crows)[:7])
    watch_lines = []
    for w in watch:
        per_m = {}
        for r in by_cat.get(w, []):
            per_m[r["date_opened"][:7]] = per_m.get(r["date_opened"][:7], 0) + 1
        watch_lines.append({"label": w,
                            "points": [{"x": m + "-01", "y": per_m.get(m, 0)} for m in span]})

    headline = (f"WATCH TRIGGERED on our internal log (demo-fabricated): {len(over)} over-delivery "
                f"and {len(proxy)} PCA-by-proxy-suspected complaint records ({len(mdr_filed)} MDR-filed, "
                f"{len(under_inv)} under investigation) — E-20.1 zero-tolerance NOT met; the "
                f"signal→upgrade loop closed for {len(closed_loop)} watch-category signals; real "
                f"class-wide MAUDE context is counts-only (no denominator)")

    # --- expectations --------------------------------------------------------
    exp_results = {
        "E-20.1": (f"{len(over)} over-delivery complaint records on the log "
                   f"({sum(1 for r in over if r['mdr_filed'] == 'yes')} MDR-filed, "
                   f"{sum(1 for r in over if r['status'] == 'under-investigation')} under "
                   f"investigation) — zero-tolerance breached per the plan's 'confirmed' definition",
                   "not-met" if over else "met",
                   ["derived: watch-events", f"src: {csrc}"]),
    }
    exps = C.evaluate_expectations("BQ-20", exp_results)

    # --- narrative (deterministic from computed facts) -----------------------
    narrative = {"issues": [], "risks": [], "watch": []}
    if over:
        narrative["issues"].append({
            "id": "I1", "severity": "high",
            "statement": f"{len(over)} over-delivery complaint records on the internal log — the "
                         f"franchise-killer category; newest is {over[-1]['complaint_id']} "
                         f"({over[-1]['date_opened']}, {over[-1]['status']}, MDR filed: "
                         f"{over[-1]['mdr_filed']})"
                         + (f"; the docket carries open over-delivery MDR item(s) {dock_ids} — a "
                            f"category-level join, no shared key (see BQ-21)" if dock_watch else ""),
            "action": "CMO review of each event this cycle; confirm the open investigation's MDR "
                      "stays on deadline; assess whether the risk file's over-delivery controls "
                      "need re-evaluation",
            "evidence": ["derived: watch-events", "derived: docket-watch",
                         f"src: {csrc}", f"src: {dsrc}"],
        })
    if proxy:
        narrative["issues"].append({
            "id": f"I{len(narrative['issues']) + 1}", "severity": "high",
            "statement": f"{len(proxy)} PCA-by-proxy-suspected records (unauthorized bolus by "
                         f"family/visitor suspected); {sum(1 for r in proxy if r['status'] == 'open')} "
                         f"still open — a use-environment hazard the pump's lockout design must answer",
            "action": "Route to human-factors / risk-management review; check labeling and "
                      "in-service training coverage of proxy dosing at the affected sites",
            "evidence": ["derived: watch-events", f"src: {csrc}"],
        })
    narrative["risks"].append({
        "id": "R1", "severity": "medium",
        "statement": "The question asks for alarm data, but raw alarm telemetry is not a corpus "
                     "dataset — only signals sourced from alarm analytics are visible, so an "
                     "alarm-signature precursor of over-delivery could be missed",
        "mitigation": "Acquire an alarm-analytics event-level dataset; until then this watch is "
                      "complaints + register only (stated in the plan)",
        "evidence": ["derived: alarm-data-gap"],
    })
    narrative["watch"].append({
        "id": "W1",
        "statement": f"Loop-closing counter-beat: {len(closed_loop)} watch-category signals reached "
                     f"the corrective pipeline ({loop_pairs or 'none with refs'}) — "
                     f"the signal→corrective loop is demonstrably closing for this category (see BQ-22)",
        "evidence": ["derived: watch-signals", f"src: {ssrc}"],
    })
    narrative["watch"].append({
        "id": "W2",
        "statement": f"Real class-wide PCA MAUDE events run {total_class:,} since 2023 in the "
                     f"lag-trimmed window — context only: counts, never rates, and never compared "
                     f"numerically to our internal log",
        "evidence": ["derived: total-class-events", f"src: {msrc}"],
    })

    # --- report --------------------------------------------------------------
    lines = [
        "# BQ-20 — Franchise-killer watch: opioid over-delivery / PCA-by-proxy", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {csrc}] [config: commercial.yml]", "",
        "## Watch-category events on the internal complaint log (event-level)", "",
        "_Single events, not trends, are the signal here — every record is listed. Watch",
        "categories are declared in [config: commercial.yml]; 'confirmed' for E-20.1 is any",
        "record not dismissed as unfounded (the log has no dismissed status) [config: commercial.yml]._", "",
        "| Complaint | Opened | Region | Model / firmware | Category | Severity | Status | MDR filed |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in events:
        lines.append(f"| {r['complaint_id']} [src: {csrc}] | {r['date_opened']} | {r['region']} | "
                     f"{r['model']} / {r['firmware_version']} | {r['category']} | {r['severity']} | "
                     f"{r['status']} | {r['mdr_filed']} |")
    lines += [
        "",
        f"- {len(events)} watch-category records total: {len(over)} over-delivery, {len(proxy)} "
        f"PCA-by-proxy-suspected; {len(mdr_filed)} MDR-filed, {len(under_inv)} under investigation "
        f"[derived: watch-events] [src: {csrc}]",
        f"- Under-investigation over-delivery event(s) on the log: "
        f"{', '.join(r['complaint_id'] for r in over_ui) or 'none'} [src: {csrc}]. The docket's open "
        f"over-delivery MDR item(s): {dock_ids} [derived: docket-watch] [src: {dsrc}] — a "
        f"category-level join (no shared key between the complaint log and the docket, per the "
        f"plan); deadline posture is BQ-21's answer",
        "",
        "## Signal-register linkage — is the loop closing for this category?", "",
        "| Signal | Opened | Source | Category | Disposition | Ref | Closed |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in wsignals:
        lines.append(f"| {r['signal_id']} [src: {ssrc}] | {r['opened_date']} | {r['source']} | "
                     f"{r['category']} | {r['disposition']} | {r['disposition_ref'] or '—'} | "
                     f"{r['closed_date'] or 'open'} |")
    lines += [
        "",
        f"- {len(closed_loop)} of {len(wsignals)} watch-category signals reached the corrective "
        f"pipeline (both over-delivery signals landed as upgrade-items) [derived: watch-signals] "
        f"[src: {ssrc}]",
        "",
        "## Class-wide context — real PCA MAUDE trend (counts only)", "",
        f"- Monthly MAUDE event counts for product code MEA (PCA pumps) since 2023 are charted "
        f"[derived: class-monthly-events] [src: {msrc}]; the trailing {LAG_TRIM_MONTHS} months "
        f"({', '.join(lag_cut)}) are EXCLUDED — MAUDE reporting lag makes them artificially low, "
        f"and charting them would fake a decline [src: {msrc}].",
        f"- Lag caveat: the dataset README warns the reporting-lag tail runs ~3–6 months, so the "
        f"{LAG_TRIM_MONTHS}-month trim is the lower bound of that range and the lag may run longer "
        f"than the trim — the charted tail can still be incomplete; read a recent-month dip as lag, "
        f"not signal [src: {msrc}].",
        f"- {total_class:,} class-wide events in the charted window [derived: total-class-events] "
        f"[src: {msrc}].",
        "- NO DENOMINATOR: MAUDE carries no installed-base or therapy-volume denominator, so no",
        "  rate is computed or published — a rate would require the installed-base assumption",
        "  [assume: A-001], which is deliberately not yet quantified; counts support trend/shape",
        "  reading only.",
        "- These are REAL public data about the whole PCA class; our internal events above are",
        "  demo-fabricated. The two are never compared numerically (different populations,",
        "  reporting propensities, and provenance) — see the analysis plan.",
    ]
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Watch-category events and MDR flags measured from [src: {csrc}]; watch list "
        f"[config: commercial.yml].",
        f"- Signal dispositions measured from [src: {ssrc}]; the complaint↔docket tie is derived "
        f"from the pinned docket rows [src: {dsrc}] as a category-level join (no shared key), "
        f"per the plan [derived: docket-watch].",
        f"- Class-wide trend measured from openFDA's date-count API [src: {msrc}] (public domain); "
        f"lag-tail exclusion and the no-denominator constraint per the plan and [assume: A-001].",
    ]

    data = {
        "bq": "BQ-20",
        "series": [
            {"id": "watch-stat", "label": "Watch-category field events (internal log)",
             "unit": "events", "kind": "stat", "evidence_class": "measured",
             "provenance": {"dataset": COMPLAINTS_DS, "snapshot": csnap},
             "points": [{"label": "over-delivery complaints on the log", "value": len(over)},
                        {"label": "PCA-by-proxy-suspected complaints", "value": len(proxy)}]},
            {"id": "watch-events", "label": "Watch-category events by category", "unit": "events",
             "evidence_class": "measured",
             "provenance": {"dataset": COMPLAINTS_DS, "snapshot": csnap},
             "points": [{"label": w, "value": len(by_cat.get(w, []))} for w in watch]},
            {"id": "watch-monthly", "label": "Internal watch-category events per month (demo)",
             "unit": "events/month", "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": COMPLAINTS_DS, "snapshot": csnap},
             "lines": watch_lines, "points": []},
            {"id": "watch-signals", "label": "Watch-category signals and dispositions", "unit": "",
             "evidence_class": "measured",
             "provenance": {"dataset": SIGNALS_DS, "snapshot": ssnap},
             "points": [{"label": r["signal_id"],
                         "value": f"{r['category']} → {r['disposition']}"
                                  + (f" ({r['disposition_ref']})" if r["disposition_ref"] else "")}
                        for r in wsignals]},
            {"id": "docket-watch", "label": "Open docket MDR items in watch categories", "unit": "items",
             "evidence_class": "derived",
             "derivation": {"method": "open MDR-type docket records whose category is on the "
                                      "declared watch list; joined to complaints by category only "
                                      "(no shared key between the two logs)",
                            "inputs": [f"src: {dsrc}", "config: commercial.yml"]},
             "provenance": {"dataset": DOCKET_DS, "snapshot": dsnap},
             "points": [{"label": r["record_id"],
                         "value": f"{r['category']} — opened {r['opened_date']}, "
                                  f"deadline {r['regulatory_deadline']}"}
                        for r in dock_watch]},
            {"id": "class-monthly-events", "label": "Class-wide PCA MAUDE events per month (REAL)",
             "unit": "events", "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": MAUDE_PCA_DS, "snapshot": msnap},
             "lines": [{"label": "MEA class (lag-trimmed)", "points": hist_pts}], "points": []},
            {"id": "total-class-events", "label": "Class-wide PCA MAUDE events (charted window)",
             "unit": "events", "kind": "stat", "evidence_class": "measured",
             "provenance": {"dataset": MAUDE_PCA_DS, "snapshot": msnap},
             "points": [{"label": "MEA events since 2023, lag tail excluded", "value": total_class}]},
            {"id": "class-event-rate", "label": "PCA-class event rate per installed device",
             "unit": "events/device", "evidence_class": "unavailable",
             "provenance": {"assumption": "A-001",
                            "note": "MAUDE has no denominator; blocked until A-001 quantifies "
                                    "installed bases — never published as a rate"},
             "points": []},
            {"id": "alarm-data-gap", "label": "Alarm-analytics event-level data", "unit": "events",
             "evidence_class": "unavailable",
             "provenance": {"note": "raw alarm telemetry is not a corpus dataset — only signals "
                                    "sourced from alarm analytics are visible in the register"},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "measured"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
