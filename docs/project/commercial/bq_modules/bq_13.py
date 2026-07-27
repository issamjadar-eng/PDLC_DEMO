"""BQ-13 — Predictive-monitoring runway: is the F6 Y3 (2028-H2) slot defensible?

Contract: run(corpus_root, out, pins) — see plans/BQ-13.md for the committed
definitions (data anchor, launch anchor, A-005 runway bands, acquisition scenario,
watch keywords). Deterministic: all dates derive from pinned data + config.
"""

import calendar
import datetime as dt

import yaml

import computations as C

FDA_DS = "commercial/openfda-510k-infusion"
FEAT_DS = "commercial/external-competitor-features"

# Smallness threshold (days) under which the hardware-edge margin is called
# RAZOR-THIN / "by only N days" — above it, the qualifier is dropped (F13-2)
FRAGILE_EDGE_DAYS = 90


def add_months(d: dt.date, months: int) -> dt.date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def months_between(a: dt.date, b: dt.date) -> int:
    """Signed whole months from a to b (b - a), rounded."""
    return round((b - a).days / 30.44)


def run(corpus_root, out, pins):
    p = C.params_for("BQ-13")
    rows510, snap510 = C.load_pin_csv(corpus_root, pins, FDA_DS)
    feats, fsnap = C.load_pin_csv(corpus_root, pins, FEAT_DS)
    src510 = f"{FDA_DS}@{snap510}"
    srcf = f"{FEAT_DS}@{fsnap}"
    aliases = yaml.safe_load(open(p["aliases"]))["canonical"]

    def canon(name):
        u = name.upper()
        for c in aliases:
            if any(u.startswith(pref.upper()) for pref in c["prefixes"]):
                return c["name"]
        return name.title()

    # 1) Verify the premise: nobody in the matrix documents shipping predictive monitoring
    pred_rows = [r for r in feats if r["attribute"] == "predictive_monitoring"]
    shipping = [r for r in pred_rows if r["value"].strip().lower().startswith("yes")]
    check_pts = [{"label": f"{r['vendor']} {r['product']}", "value": r["value"],
                  "verified": r["verified"]} for r in pred_rows]

    # 2) Runway model (A-005 bands from the data anchor vs our launch anchor)
    anchor = max(r["decision_date"] for r in rows510 if r["decision_date"])
    anchor_d = dt.date.fromisoformat(anchor)
    launch = dt.date.fromisoformat(p["our_launch_anchor"])
    launch_late = dt.date.fromisoformat(p["our_launch_anchor_late"])
    samd_lo, samd_hi = (add_months(anchor_d, m) for m in p["samd_lead_months"])
    hw_lo, hw_hi = (add_months(anchor_d, m) for m in p["hardware_lead_months"])
    # RT-13.1: the hardware-scenario reassurance margin, both anchor readings
    hw_edge_days = (hw_lo - launch).days            # fast hardware edge vs favorable anchor
    hw_beats_late = hw_lo <= launch_late            # does it beat the end-of-period reading?
    hw_late_margin = abs(months_between(hw_lo, launch_late))

    def posture(lo, hi):
        if hi < launch:
            return "beats our launch anchor"
        if lo < launch:
            return "straddles our launch anchor"
        return "clears after our launch anchor"

    scen = [
        ("SaMD-only entrant", samd_lo, samd_hi, posture(samd_lo, samd_hi)),
        ("Hardware-integrated / clinical-evidence program", hw_lo, hw_hi, posture(hw_lo, hw_hi)),
        ("Incumbent acquires AI entrant (SaMD clock on incumbent channel)",
         samd_lo, samd_hi, posture(samd_lo, samd_hi)),
    ]
    margin = months_between(samd_hi, launch)  # months our launch trails a worst-case-for-us SaMD clearance
    # F13-1: the direction word is computed from the sign of the margin — never a literal
    if margin > 0:
        samd_rel = f"about {margin} months before"
    elif margin < 0:
        samd_rel = f"about {-margin} months after"
    else:
        samd_rel = "in the same month as"
    # F13-2: the hardware-edge sentence branches on the sign of the margin, and the
    # fragility qualifier applies only when the (positive) margin is actually small
    hw_edge_small = 0 <= hw_edge_days <= FRAGILE_EDGE_DAYS

    # 3) Recent-clearance watch: trailing 12 months ending at the anchor, keyword-flagged
    win_start = (anchor_d - dt.timedelta(days=365)).isoformat()
    kw = p["watch_keywords"]

    def flags(name):
        u = name.upper()
        return [lane for lane, kws in kw.items() if any(k in u for k in kws)]

    recent = sorted((r for r in rows510 if r["decision_date"] and win_start <= r["decision_date"] <= anchor),
                    key=lambda r: r["decision_date"], reverse=True)
    watch = [(r, flags(r["device_name"])) for r in recent]
    watch_flagged = [(r, f) for r, f in watch if f]
    ai_flagged = [(r, f) for r, f in watch_flagged if "ai-predictive" in f]

    # 4) History: clearances per quarter — all vs software-flagged vs ai-predictive-flagged
    def quarter_key(d):
        return f"{d[:4]}-Q{(int(d[5:7]) - 1) // 3 + 1}"

    dated = [r for r in rows510 if r["decision_date"]]
    qs = sorted({quarter_key(r["decision_date"]) for r in dated})
    # zero-fill the full quarter range
    def q_iter(first, last):
        y, q = int(first[:4]), int(first[-1])
        while f"{y}-Q{q}" <= last:
            yield f"{y}-Q{q}"
            q += 1
            if q == 5:
                y, q = y + 1, 1
    all_q = list(q_iter(qs[0], qs[-1]))
    q_start_month = {1: "01", 2: "04", 3: "07", 4: "10"}

    def q_counts(pred):
        c = {}
        for r in dated:
            if pred(r):
                c[quarter_key(r["decision_date"])] = c.get(quarter_key(r["decision_date"]), 0) + 1
        return [{"x": f"{q[:4]}-{q_start_month[int(q[-1])]}-01", "y": c.get(q, 0)} for q in all_q]

    ts_lines = [
        {"label": "all FRN clearances", "points": q_counts(lambda r: True)},
        {"label": "software-flagged", "points": q_counts(lambda r: "software" in flags(r["device_name"]))},
        {"label": "ai/predictive-flagged", "points": q_counts(lambda r: "ai-predictive" in flags(r["device_name"]))},
    ]

    if shipping:
        headline = (f"RUNWAY MOOT: {len(shipping)} competitor product(s) already document shipping "
                    f"predictive monitoring — the gap is closed, not closing")
    else:
        if hw_edge_days < 0:
            hw_head = (f"The hardware scenario is NO reassurance: its fast edge beats even the "
                       f"favorable launch anchor by {-hw_edge_days} days")
        elif hw_edge_small:
            hw_head = (f"The hardware-scenario reassurance is FRAGILE: its fast "
                       f"edge clears the favorable launch anchor by only {hw_edge_days} days")
        else:
            hw_head = (f"The hardware-scenario reassurance holds: its fast edge clears the "
                       f"favorable launch anchor by {hw_edge_days} days")
        headline = (f"Nobody in the competitive matrix documents predictive monitoring today, but the "
                    f"runway is assumption-thin: a SaMD-only entrant starting at the data anchor "
                    f"({anchor}) could clear {samd_lo} to {samd_hi} — {samd_rel} "
                    f"our F6 {p['our_launch_period']} launch anchor; an incumbent acquisition inherits "
                    f"the same clock; {len(ai_flagged)} ai/predictive-flagged clearance(s) in the "
                    f"trailing-12-month watch. {hw_head}"
                    + (f" and beats an end-of-{p['our_launch_period']} launch reading by ~{hw_late_margin} "
                       f"months" if hw_beats_late else "")
                    + " — and the H2 anchor refinement is a catalog config choice, not a strategy-doc "
                      "commitment")

    lines = [
        "# BQ-13 — Predictive-monitoring runway vs our F6 slot", "",
        f"**Verdict**: {headline} [derived: v-main] [assume: A-005] [src: {src510}] "
        f"[src: {srcf}] [config: commercial.yml]", "",
        "## Premise check — does anyone document shipping predictive monitoring?", "",
        "| Vendor / product | predictive_monitoring | Verified |",
        "|---|---|---|",
    ]
    for r in pred_rows:
        lines.append(f"| {r['vendor']} {r['product']} [src: {srcf}] | {r['value']} | {r['verified']} |")
    # F13-3: the universal ("every row reads no") is only claimed when it is true
    if shipping:
        premise_bullet = (f"- {len(shipping)} of {len(pred_rows)} documented rows read `yes` — the "
                          f"premise fails [derived: predictive-shipping-check] [src: {srcf}]. Products "
                          f"absent from the matrix are absent, not cleared — the matrix cannot prove "
                          f"entrant absence.")
    else:
        premise_bullet = (f"- Every documented row reads `no` — {len(pred_rows)} products checked, "
                          f"{len(shipping)} shipping [derived: predictive-shipping-check] [src: {srcf}]. Products "
                          f"absent from the matrix are absent, not cleared — the matrix cannot prove entrant absence.")
    lines += [
        "",
        premise_bullet,
        "",
        "## Runway model — A-005 lead-time bands from the data anchor", "",
        f"_Data anchor = newest decision date in the pinned snapshot ({anchor}); our launch anchor = "
        f"first day of {p['our_launch_period']} ({p['our_launch_anchor']}, the favorable-to-us "
        f"reading; the unfavorable end-of-period reading is {p['our_launch_anchor_late']}) "
        f"[src: {src510}] [config: commercial.yml]. Anchor provenance caveat: the H2 half-year "
        f"refinement exists ONLY in the question catalog [config: commercial.yml] — the strategy doc "
        f"(D-COMM-1.4) commits F6 to bare 'Y3 (2028)' with no half-year granularity, so both "
        f"readings below are config-sensitive, not strategy-committed._", "",
        "| Entry scenario | Projected clearance window | Vs our launch anchor |",
        "|---|---|---|",
    ]
    for name, lo, hi, post in scen:
        lines.append(f"| {name} [assume: A-005] [derived: entry-scenarios] | {lo} → {hi} | {post} |")
    # F13-1: the slow-end bullet's framing branches on the sign of the margin
    if margin > 0:
        slow_bullet = (f"- Best-case-for-us reading: even the SLOW end of the SaMD band ({samd_hi}) lands about "
                       f"{margin} months before our launch anchor [derived: runway-margin] [assume: A-005].")
    else:
        slow_bullet = (f"- The SLOW end of the SaMD band ({samd_hi}) lands {samd_rel} our launch "
                       f"anchor — the worst-case-for-us SaMD entrant no longer beats our date; only the "
                       f"FAST end ({samd_lo}) does [derived: runway-margin] [assume: A-005].")
    # F13-2: the hardware-edge bullet branches on sign + smallness
    if hw_edge_days < 0:
        hw_bullet_mid = (f"— NO reassurance under any reading: the fast edge beats even the favorable "
                         f"anchor ({p['our_launch_anchor']}) by {-hw_edge_days} days")
    elif hw_edge_small:
        hw_bullet_mid = (f"— but that reassurance is RAZOR-THIN and anchor-reading-dependent: "
                         f"the fast edge clears the favorable anchor ({p['our_launch_anchor']}) by only {hw_edge_days} days")
    else:
        hw_bullet_mid = (f"— anchor-reading-dependent: the fast edge clears the favorable anchor "
                         f"({p['our_launch_anchor']}) by {hw_edge_days} days")
    lines += [
        "",
        slow_bullet,
        f"- The hardware-integrated / clinical-evidence band ({hw_lo} → {hw_hi}) "
        f"{posture(hw_lo, hw_hi)} {hw_bullet_mid}"
        + (f", and under the end-of-period reading ({p['our_launch_anchor_late']}) it BEATS "
           f"our launch by ~{hw_late_margin} months" if hw_beats_late else "")
        + " [derived: hardware-edge-margin] [assume: A-005] [config: commercial.yml]. 'A hardware "
          "incumbent building in-house is not the fast threat' holds only under the favorable anchor "
          "reading; an acquisition converting an incumbent to the SaMD clock remains the fast threat "
          "under every reading [derived: entry-scenarios].",
        "",
        "## Recent-clearance watch (trailing 12 months ending at the data anchor)", "",
        f"_Window {win_start} → {anchor}; keyword flags on public device names are a triage aid, "
        f"never a capability judgment [config: commercial.yml] [src: {src510}]._", "",
    ]
    if watch_flagged:
        lines += ["| K-number | Applicant (canonical) | Device | Decision | Flags |",
                  "|---|---|---|---|---|"]
        for r, f in watch_flagged:
            lines.append(f"| {r['k_number']} [src: {src510}] [config: entity-aliases.yml] | "
                         f"{canon(r['applicant'])} | {r['device_name'][:55]} | {r['decision_date']} | "
                         f"{', '.join(f)} |")
    else:
        lines.append(f"- No keyword-flagged clearances in the window [src: {src510}]")
    lines += [
        "",
        f"- {len(watch_flagged)} of {len(recent)} window clearances carry software/AI-adjacent flags; "
        f"{len(ai_flagged)} carry the ai-predictive flag [derived: watch-flagged] [src: {src510}].",
    ]

    narrative = {"issues": [], "risks": [], "watch": []}
    narrative["risks"].append({
        "id": "R1", "severity": "high",
        "statement": f"The F6 runway verdict is assumption-bounded: the entire lead-time model is "
                     f"A-005 (medium confidence), and the entrant clock is modeled from the data "
                     f"anchor ({anchor}) — a program already underway is ahead of every figure here",
        "mitigation": "Treat A-005's refresh triggers as standing: recompute on every 510(k) "
                      "snapshot refresh and on any predictive-monitoring announcement; widen the "
                      "corpus beyond product code FRN before relying on entrant absence",
        "evidence": ["assume: A-005", f"src: {src510}"],
    })
    narrative["risks"].append({
        "id": "R2", "severity": "medium",
        "statement": f"Acquisition scenario: an incumbent buying an AI entrant applies the "
                     f"{p['samd_lead_months'][0]}-{p['samd_lead_months'][1]}-month SaMD clock to an "
                     f"established hospital channel — the fastest modeled path to closing our gap, "
                     f"and it is an assumption-class scenario, not an observed signal",
        "mitigation": "Track M&A signals alongside the clearance watch; a deal announcement "
                      "collapses the runway to the SaMD band immediately",
        "evidence": ["assume: A-005", "derived: entry-scenarios", "config: commercial.yml"],
    })
    # F13-2: R3 restates the hardware-edge facts — same sign/smallness branches
    if hw_edge_days < 0:
        r3_margin = (f"fails even under the favorable anchor reading (the fast edge beats our launch "
                     f"by {-hw_edge_days} days)")
        r3_late = ""
    else:
        r3_margin = (f"holds by {'only ' if hw_edge_small else ''}{hw_edge_days} days at the fast edge "
                     f"under the favorable anchor reading")
        r3_late = (f", and flips under the end-of-period reading ({p['our_launch_anchor_late']}: the "
                   f"fast edge beats our launch by ~{hw_late_margin} months)" if hw_beats_late
                   else f", and holds under the end-of-period reading ({p['our_launch_anchor_late']}) as well")
    narrative["risks"].append({
        "id": "R3", "severity": "medium",
        "statement": f"The hardware-scenario reassurance ('clears after our launch anchor') "
                     f"{r3_margin}{r3_late}; the H2 anchor "
                     f"refinement itself is a catalog config choice — the strategy doc commits only "
                     f"'Y3 (2028)'",
        "mitigation": "Ground the launch anchor in the plan of record (commit a half-year or a date "
                      "in commercial-strategy.md D-COMM-1.4), and never quote the hardware-scenario "
                      "reassurance without its margin",
        "evidence": ["derived: hardware-edge-margin", "assume: A-005", "config: commercial.yml"],
    })
    narrative["watch"].append({
        "id": "W1",
        "statement": "Entry could be underway undetected: unannounced development programs are "
                     "invisible in public data by construction, and FRN-only scope cannot see a "
                     "De Novo or non-FRN predictive SaMD — absence of signal is not absence of entrant",
        "evidence": [f"src: {src510}", "derived: watch-flagged"],
    })

    lines += C.expectations_section(C.evaluate_expectations("BQ-13", {}))
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Premise check measured from [src: {srcf}] (predictive_monitoring rows).",
        f"- Runway windows derived: A-005 band endpoints added to the data anchor "
        f"[assume: A-005] [src: {src510}]; launch anchor from [config: commercial.yml].",
        "- Anchor sensitivity: both launch-anchor readings (first day / last day of the config "
        "period) are stated wherever a scenario's posture depends on them; the half-year "
        "refinement is config-only — the strategy doc commits the year, not the half "
        "[config: commercial.yml] [derived: hardware-edge-margin].",
        f"- Watch flags are keyword matches on public device names [config: commercial.yml]; "
        f"applicant names normalized via [config: entity-aliases.yml].",
        "- Historical view: quarterly clearance counts, software-flagged and ai/predictive-flagged, "
        "are charted zero-filled — the ai/predictive line is flat at zero, which IS the finding "
        f"[derived: clearances-by-quarter] [src: {src510}].",
        "- Scope: product code FRN only; the dataset README's known limitation stands — widen the "
        "product-code scope before concluding no entrant activity.",
    ]

    data = {
        "bq": "BQ-13",
        "series": [
            {"id": "runway-margin", "label": "Months our launch trails a slow SaMD entrant", "unit": "months",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "our launch anchor minus (data anchor + slow end of the A-005 SaMD band), in months",
                            "inputs": ["assume: A-005", f"src: {src510}", "config: commercial.yml"]},
             "provenance": {"dataset": FDA_DS, "snapshot": snap510},
             "points": [{"label": f"months {'before' if margin >= 0 else 'after'} our "
                                  f"{p['our_launch_period']} anchor a slow "
                                  f"({p['samd_lead_months'][1]}-month) SaMD entrant starting {anchor} would clear",
                         "value": abs(margin)}]},
            {"id": "hardware-edge-margin", "label": "Hardware-scenario margin vs our launch anchor",
             "unit": "", "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "fast hardware edge (data anchor + fast end of the A-005 hardware band) minus each launch-anchor reading (first/last day of our_launch_period)",
                            "inputs": ["assume: A-005", f"src: {src510}", "config: commercial.yml"]},
             "provenance": {"dataset": FDA_DS, "snapshot": snap510},
             "points": [{"label": f"days the fast hardware edge ({hw_lo}) clears the favorable "
                                  f"anchor ({p['our_launch_anchor']})", "value": hw_edge_days},
                        {"label": f"months the fast hardware edge beats the end-of-period reading "
                                  f"({p['our_launch_anchor_late']})",
                         "value": hw_late_margin if hw_beats_late else 0}]},
            {"id": "predictive-shipping-check", "label": "predictive_monitoring by product", "unit": "",
             "evidence_class": "measured",
             "provenance": {"dataset": FEAT_DS, "snapshot": fsnap}, "points": check_pts},
            {"id": "entry-scenarios", "label": "Modeled clearance window by entry scenario", "unit": "",
             "evidence_class": "assumed",
             "provenance": {"assumption": "A-005",
                            "note": "A-005 lead-time bands projected from the pinned snapshot's newest decision date; the acquisition scenario is modeled, not observed"},
             "points": [{"label": name, "value": f"{lo} → {hi} ({post})"} for name, lo, hi, post in scen]},
            {"id": "watch-flagged", "label": "Keyword-flagged clearances (trailing 12 months)", "unit": "",
             "evidence_class": "measured",
             "provenance": {"dataset": FDA_DS, "snapshot": snap510},
             "points": [{"label": r["k_number"], "value": f"{canon(r['applicant'])} — {', '.join(f)}"}
                        for r, f in watch_flagged]},
            {"id": "clearances-by-quarter", "label": "FRN clearances per quarter (all / software / ai-predictive)",
             "unit": "clearances", "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": FDA_DS, "snapshot": snap510}, "lines": ts_lines, "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "assumed"}],
        "narrative": narrative,
        "expectations": C.evaluate_expectations("BQ-13", {}),
    }
    C.write(out, lines, data)
