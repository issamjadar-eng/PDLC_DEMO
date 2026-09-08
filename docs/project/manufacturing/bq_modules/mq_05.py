"""MQ-05 — supplier quality: incoming reject rate and on-time by supplier / component
family, scorecard distribution, single-source exposure, audit currency.

Deterministic per the MQ-05 analysis plan: the trailing window is the last
`window_months` periods ending at the snapshot as_of month; reject rate = lots rejected
÷ lots received (lot-weighted); on-time = lot-weighted mean of the period on_time_pct;
audit currency = next_audit_due vs as_of; the scorecard distribution uses each
supplier's latest-period grade.
"""

import computations as C

DS = "manufacturing/internal-suppliers"
STATUSES = ("approved", "conditional", "probation")
GRADES = ("A", "B", "C", "D")


def _r(v):
    return None if v is None else round(v, 1)


def run(corpus_root, out, pins):
    p = C.params_for("MQ-05")
    n_win = int(p["window_months"])
    ceiling = float(p["reject_ceiling_pct"])
    rows, snap = C.load_pin_csv(corpus_root, pins, DS)
    C.assert_vocab(rows, "approval_status", STATUSES, DS)
    C.assert_vocab(rows, "scorecard", GRADES, DS)
    src = f"{DS}@{snap}"
    as_of = C.snapshot_as_of(corpus_root, pins, DS)
    periods = sorted({r["period"] for r in rows})
    win = [m for m in C.trailing_months(as_of, n_win) if m in set(periods)]
    win_label = f"{win[0]}..{win[-1]}"
    w = [r for r in rows if r["period"] in win]
    latest = max(periods)

    def rej(sub):
        rec = sum(int(r["lots_received"]) for r in sub)
        return (C.pct_raw(sum(int(r["lots_rejected"]) for r in sub), rec) if rec else None), rec

    def ontime(sub):
        rec = sum(int(r["lots_received"]) for r in sub)
        return sum(float(r["on_time_pct"]) * int(r["lots_received"]) for r in sub) / rec if rec else None

    sups = sorted({r["supplier_id"] for r in rows})
    reg = {r["supplier_id"]: r for r in rows if r["period"] == latest}
    per_sup = []
    for s in sups:
        sub = [r for r in w if r["supplier_id"] == s]
        rr, rec = rej(sub)
        m = reg[s]
        per_sup.append({"id": s, "name": m["supplier_name"], "family": m["component_family"],
                        "single": m["single_source"] == "true", "status": m["approval_status"],
                        "reject": rr, "received": rec, "ontime": ontime(sub),
                        "grade": m["scorecard"], "audit_days": C.days_between(m["next_audit_due"], as_of),
                        "last_audit": m["last_audit_date"], "next_audit": m["next_audit_due"]})
    fams = sorted({r["component_family"] for r in rows})
    per_fam = []
    for f in fams:
        sub = [r for r in w if r["component_family"] == f]
        rr, rec = rej(sub)
        per_fam.append((f, rr, ontime(sub), rec, sum(1 for s in per_sup if s["family"] == f),
                        sum(1 for s in per_sup if s["family"] == f and s["single"])))
    all_rr, all_rec = rej(w)
    all_ot = ontime(w)
    above = sorted([s for s in per_sup if s["reject"] is not None and s["reject"] > ceiling], key=lambda s: -s["reject"])
    overdue = sorted([s for s in per_sup if s["audit_days"] > 0], key=lambda s: -s["audit_days"])
    single = [s for s in per_sup if s["single"]]
    probation = [s for s in per_sup if s["status"] == "probation"]
    grades = {g: sum(1 for s in per_sup if s["grade"] == g) for g in GRADES}

    # trend: monthly reject rate — all suppliers + the suppliers above ceiling (≤4 lines)
    def line_for(label, pred):
        pts = []
        for m in periods:
            rr, _ = rej([r for r in rows if r["period"] == m and pred(r)])
            pts.append({"x": f"{m}-01", "y": _r(rr)})
        return {"label": label, "points": pts}
    trend = [line_for("all suppliers", lambda r: True)]
    for s in above[:3]:
        trend.append(line_for(f"{s['id']} ({s['family']})", lambda r, s=s: r["supplier_id"] == s["id"]))

    def label(s):
        return f"{s['id']} {s['name']} ({s['family']})"

    headline = (f"Incoming reject rate {all_rr:.1f}% across {len(per_sup)} suppliers in {win_label} "
                f"({all_rec} lots received), on-time {all_ot:.1f}%; {len(above)} supplier(s) above the {ceiling:.0f}% ceiling"
                + (": " + ", ".join(f"{s['id']} {s['reject']:.1f}%" + (" single-source" if s["single"] else "")
                                    + (f" {s['status']}" if s["status"] != "approved" else "") for s in above) if above else "")
                + f"; {len(overdue)} audit(s) overdue"
                + (" (" + ", ".join(f"{s['id']} by {s['audit_days']} d" for s in overdue) + ")" if overdue else "")
                + f"; {len(single)} single-source supplier(s) ({', '.join(s['family'] for s in single)}); "
                f"scorecards A {grades['A']} / B {grades['B']} / C {grades['C']} / D {grades['D']}")

    narrative = {"issues": [], "risks": [], "watch": []}
    for i, s in enumerate(above, 1):
        narrative["issues"].append({
            "id": f"I{i}", "severity": "high" if s["single"] or s["reject"] > 2 * ceiling else "medium",
            "statement": f"{label(s)} rejects {s['reject']:.1f}% of incoming lots in {win_label} against the {ceiling:.0f}% ceiling"
                         + (f"; approval status {s['status']}" if s["status"] != "approved" else "")
                         + (f"; audit overdue by {s['audit_days']} d" if s["audit_days"] > 0 else ""),
            "action": "Issue a supplier corrective action request; tighten incoming sampling for the family until two clean periods",
            "evidence": ["derived: reject-by-supplier", f"src: {src}", C.CONFIG_MARKER],
        })
    for s in single:
        sev = "high" if (s["reject"] is not None and s["reject"] > ceiling) or s["audit_days"] > 0 else "medium"
        narrative["risks"].append({
            "id": f"R{len(narrative['risks']) + 1}", "severity": sev,
            "statement": f"Single-source exposure on {s['family']}: {label(s)} is the only approved source; "
                         f"scorecard {s['grade']}, reject {s['reject']:.1f}%, next audit due {s['next_audit']}"
                         + (f" (overdue {s['audit_days']} d)" if s["audit_days"] > 0 else ""),
            "mitigation": "Qualify a second source or hold safety stock sized to the requalification lead time; bring the audit current",
            "evidence": ["derived: single-source-exposure", "derived: audit-currency", f"src: {src}"],
        })
    for s in probation:
        narrative["watch"].append({
            "id": f"W{len(narrative['watch']) + 1}",
            "statement": f"{label(s)} is on probation — scorecard {s['grade']}, reject {s['reject']:.1f}%, on-time {s['ontime']:.1f}% in {win_label}",
            "evidence": ["derived: reject-by-supplier", "derived: ontime-by-supplier", f"src: {src}"],
        })
    narrative["risks"].append({
        "id": f"R{len(narrative['risks']) + 1}", "severity": "medium",
        "statement": f"The {ceiling:.0f}% reject ceiling and the 'no overdue audit' rule are stand-ins — the approved-supplier "
                     "procedure on record names neither, so the verdict is only as good as an unratified threshold",
        "mitigation": "Have supplier quality ratify the ceiling and audit-interval rule in the ASL procedure and mark E-05.x validated",
        "evidence": [C.CONFIG_MARKER],
    })

    exp_results = {
        "E-05.1": (f"{len(overdue)} supplier audit(s) overdue at {as_of}"
                   + (": " + ", ".join(f"{s['id']} ({s['audit_days']} d)" for s in overdue) if overdue else ""),
                   "met" if not overdue else "not-met", ["derived: audit-currency"]),
        "E-05.2": (f"{len(above)} of {len(per_sup)} suppliers above {ceiling:.0f}% in {win_label}"
                   + (": " + ", ".join(f"{s['id']} {s['reject']:.1f}%" for s in above) if above else ""),
                   "met" if not above else "not-met", ["derived: reject-by-supplier"]),
    }
    exps = C.evaluate_expectations("MQ-05", exp_results)

    def fmt(v):
        return "—" if v is None else f"{v:.1f}"

    lines = [
        "# MQ-05 — Supplier quality: incoming rejects, on-time, scorecards, single-source exposure, audit currency", "",
        C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [{C.CONFIG_MARKER}]", "",
        "## Headline", "",
        f"- Window: trailing {n_win} periods {win_label}, anchored on the snapshot as-of {as_of}; reject ceiling "
        f"{ceiling:.0f}% [src: {src}] [{C.CONFIG_MARKER}].",
        f"- Reject rate {all_rr:.1f}% on {all_rec} lots, on-time {all_ot:.1f}% (lot-weighted) [derived: supplier-stat] [src: {src}].", "",
        "## By supplier", "",
        "| Supplier | Family | Status | Single source | Reject % | On-time % | Scorecard | Next audit due |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for s in sorted(per_sup, key=lambda s: -(s["reject"] or 0)):
        flag = " ⚠️" if s["reject"] is not None and s["reject"] > ceiling else ""
        aud = f"{s['next_audit']}" + (f" (overdue {s['audit_days']} d)" if s["audit_days"] > 0 else "")
        lines.append(f"| {s['id']} {s['name']} [src: {src}] | {s['family']} | {s['status']} | "
                     f"{'yes' if s['single'] else 'no'} | {fmt(s['reject'])}{flag} | {fmt(s['ontime'])} | {s['grade']} | {aud} |")
    lines += ["", "## By component family", "",
              "| Family | Reject % | On-time % | Lots received | Suppliers | Single-source |", "|---|---|---|---|---|---|"]
    lines += [f"| {f} [src: {src}] | {fmt(rr)} | {fmt(ot)} | {rec} | {n} | {ns} |" for f, rr, ot, rec, n, ns in per_fam]
    lines += ["", "## Scorecard distribution (latest period)", "", "| Grade | Suppliers |", "|---|---|"]
    lines += [f"| {g} [src: {src}] | {grades[g]} |" for g in GRADES]
    lines += ["", "## Single-source exposure", "",
              "| Supplier | Family | Scorecard | Reject % | Audit status |", "|---|---|---|---|---|"]
    lines += [f"| {s['id']} {s['name']} [src: {src}] | {s['family']} | {s['grade']} | {fmt(s['reject'])} | "
              f"{'overdue ' + str(s['audit_days']) + ' d' if s['audit_days'] > 0 else 'current, due ' + s['next_audit']} |" for s in single]
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- All figures from the pinned supplier register × incoming-inspection log [src: {src}]; window and "
        f"ceiling are plan constants [{C.CONFIG_MARKER}].",
        "- Reject rate is lot-weighted (rejected ÷ received over the window), on-time is lot-weighted; the "
        "scorecard distribution uses each supplier's latest-period grade [derived: scorecard-distribution].",
        "- Audit currency = next audit due vs the as-of date (positive = overdue) [derived: audit-currency].",
        "- Monthly reject-rate history is charted for all suppliers and each supplier above the ceiling "
        "[derived: reject-trend].",
    ]

    prov = {"dataset": DS, "snapshot": snap}
    data = {
        "bq": "MQ-05",
        "series": [
            {"id": "supplier-stat", "label": "Incoming quality", "unit": "%", "kind": "stat",
             "evidence_class": "derived",
             "derivation": {"method": "lots rejected ÷ lots received and lot-weighted on-time over the trailing window",
                            "inputs": [f"src: {src}", C.CONFIG_MARKER]},
             "provenance": prov,
             "points": [{"label": f"reject rate {win_label}", "value": _r(all_rr), "sub": f"{all_rec} lots received"},
                        {"label": "on-time", "value": _r(all_ot), "sub": "lot-weighted"},
                        {"label": "suppliers above ceiling", "value": len(above), "sub": f"of {len(per_sup)}"},
                        {"label": "audits overdue", "value": len(overdue), "sub": f"single-source {len(single)}"}]},
            {"id": "reject-by-supplier", "label": "Incoming reject rate by supplier", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "lots rejected ÷ lots received per supplier over the trailing window", "inputs": [f"src: {src}"]},
             "provenance": prov,
             "points": [{"label": label(s), "value": _r(s["reject"]), "single_source": s["single"], "status": s["status"]}
                        for s in sorted(per_sup, key=lambda s: -(s["reject"] or 0))]},
            {"id": "ontime-by-supplier", "label": "On-time delivery by supplier", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "lot-weighted mean of period on_time_pct per supplier over the trailing window", "inputs": [f"src: {src}"]},
             "provenance": prov,
             "points": [{"label": label(s), "value": _r(s["ontime"])} for s in sorted(per_sup, key=lambda s: (s["ontime"] or 0))]},
            {"id": "reject-by-family", "label": "Incoming reject rate by component family", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "lots rejected ÷ lots received per component family over the trailing window", "inputs": [f"src: {src}"]},
             "provenance": prov, "points": [{"label": f, "value": _r(rr), "suppliers": n, "single_source": ns} for f, rr, _, _, n, ns in per_fam]},
            {"id": "scorecard-distribution", "label": "Suppliers by scorecard (latest period)", "unit": "count",
             "evidence_class": "derived",
             "derivation": {"method": "count of suppliers per latest-period scorecard grade", "inputs": [f"src: {src}"]},
             "provenance": prov, "points": [{"label": g, "value": grades[g]} for g in GRADES]},
            {"id": "single-source-exposure", "label": "Single-source suppliers: reject rate", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "single_source suppliers with their window reject rate, scorecard and audit status", "inputs": [f"src: {src}"]},
             "provenance": prov,
             "points": [{"label": label(s), "value": _r(s["reject"]), "scorecard": s["grade"], "audit_overdue_days": max(0, s["audit_days"])} for s in single]},
            {"id": "audit-currency", "label": "Days to next supplier audit (negative = overdue)", "unit": "days",
             "evidence_class": "derived",
             "derivation": {"method": "next_audit_due − as_of per supplier", "inputs": [f"src: {src}"]},
             "provenance": prov,
             "points": [{"label": label(s), "value": -s["audit_days"], "last_audit": s["last_audit"]} for s in sorted(per_sup, key=lambda s: -s["audit_days"])]},
            {"id": "reject-trend", "label": "Monthly incoming reject rate", "unit": "%", "kind": "timeseries",
             "evidence_class": "derived",
             "derivation": {"method": "lots rejected ÷ lots received per period, all suppliers and each supplier above the ceiling", "inputs": [f"src: {src}"]},
             "provenance": prov, "lines": trend[:4], "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
