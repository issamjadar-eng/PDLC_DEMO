"""MQ-03 — NCR rate and aging, CAPA open count, past-due share, effectiveness backlog.

Deterministic per the MQ-03 analysis plan: "open" = no closed_date at the snapshot
as_of; "past due" = open with due_date before as_of; ages are days from opened_date to
as_of. The past-due history is RECONSTRUCTED at each month-end from the record dates
alone (opened / due / closed), so the trend needs no prior snapshots. Effectiveness
backlog = closed CAPAs whose effectiveness_verified is not "true".
"""

import computations as C

DS = "manufacturing/internal-ncr-capa"
STATUSES = ("open", "in-progress", "closed", "overdue-open")
SOURCES = ("production", "supplier", "complaint", "audit", "field")
SEVERITIES = ("minor", "major", "critical")


def _r(v):
    return None if v is None else round(v, 1)


def run(corpus_root, out, pins):
    p = C.params_for("MQ-03")
    eff_floor = float(p["effectiveness_verified_floor_pct"])
    rows, snap = C.load_pin_csv(corpus_root, pins, DS)
    C.assert_vocab(rows, "status", STATUSES, DS)
    C.assert_vocab(rows, "source", SOURCES, DS)
    C.assert_vocab(rows, "severity", SEVERITIES, DS)
    src = f"{DS}@{snap}"
    as_of = C.snapshot_as_of(corpus_root, pins, DS)
    months = C.month_range(min(r["opened_date"] for r in rows)[:7], as_of[:7])

    ncrs = [r for r in rows if r["type"] == "NCR"]
    capas = [r for r in rows if r["type"] == "CAPA"]

    def is_open(r, at=as_of):
        return r["opened_date"] <= at and (not r["closed_date"] or r["closed_date"] > at)

    def past_due(r, at=as_of):
        return is_open(r, at) and r["due_date"] < at

    open_capa = [r for r in capas if is_open(r)]
    pd_capa = [r for r in open_capa if past_due(r)]
    crit_pd = [r for r in pd_capa if r["severity"] == "critical"]
    pd_ages = [C.days_between(r["due_date"], as_of) for r in pd_capa]
    closed_capa = [r for r in capas if r["closed_date"]]
    verified = [r for r in closed_capa if r["effectiveness_verified"] == "true"]
    backlog = [r for r in closed_capa if r["effectiveness_verified"] != "true"]
    ver_pct_raw = C.pct_raw(len(verified), len(closed_capa))

    open_ncr = [r for r in ncrs if is_open(r)]
    pd_ncr = [r for r in open_ncr if past_due(r)]
    ncr_ages = [C.days_between(r["opened_date"], as_of) for r in open_ncr]
    win3 = C.trailing_months(as_of, 3)
    prior3 = C.trailing_months(win3[0], 4)[:3]
    ncr_win = [r for r in ncrs if r["opened_date"][:7] in win3]
    ncr_prior = [r for r in ncrs if r["opened_date"][:7] in prior3]
    ncr_rate, ncr_rate_prior = len(ncr_win) / 3, len(ncr_prior) / 3

    sup_ncr = [r for r in ncrs if r["source"] == "supplier"]
    by_sup = {}
    for r in sup_ncr:
        by_sup[r["supplier_id"] or "(unattributed)"] = by_sup.get(r["supplier_id"] or "(unattributed)", 0) + 1
    sup_rank = sorted(by_sup.items(), key=lambda kv: (-kv[1], kv[0]))
    top_sup = sup_rank[0] if sup_rank else None

    # cuts
    def count(rows_, pred):
        return sum(1 for r in rows_ if pred(r))

    capa_by_source = [(s, count(open_capa, lambda r, s=s: r["source"] == s),
                       count(pd_capa, lambda r, s=s: r["source"] == s)) for s in SOURCES]
    capa_by_sev = [(s, count(open_capa, lambda r, s=s: r["severity"] == s),
                    count(pd_capa, lambda r, s=s: r["severity"] == s)) for s in SEVERITIES]
    ncr_by_sev = [(s, count(open_ncr, lambda r, s=s: r["severity"] == s),
                   C.mean(C.days_between(r["opened_date"], as_of) for r in open_ncr if r["severity"] == s))
                  for s in SEVERITIES]
    ncr_by_source_win = [(s, count(ncr_win, lambda r, s=s: r["source"] == s)) for s in SOURCES]

    # effectiveness by closure quarter
    def quarter(d):
        return f"{d[:4]}-Q{(int(d[5:7]) - 1) // 3 + 1}"
    quarters = sorted({quarter(r["closed_date"]) for r in closed_capa})
    eff_by_q = [(q, count(verified, lambda r, q=q: quarter(r["closed_date"]) == q),
                 count(backlog, lambda r, q=q: quarter(r["closed_date"]) == q)) for q in quarters]

    # trends (reconstructed at month-ends)
    def month_end(mo):
        return C.month_range(mo, mo)[0] + "-31" if mo != as_of[:7] else as_of  # string compare: "-31" sorts after any day
    pd_line = {"label": "past-due open CAPAs", "points": []}
    pd_crit_line = {"label": "of which critical", "points": []}
    open_line = {"label": "open CAPAs", "points": []}
    for mo in months:
        me = month_end(mo)
        pd_line["points"].append({"x": f"{mo}-01", "y": count(capas, lambda r, me=me: past_due(r, me))})
        pd_crit_line["points"].append({"x": f"{mo}-01", "y": count(capas, lambda r, me=me: past_due(r, me) and r["severity"] == "critical")})
        open_line["points"].append({"x": f"{mo}-01", "y": count(capas, lambda r, me=me: is_open(r, me))})
    ncr_total_line = {"label": "NCRs opened", "points": [{"x": f"{mo}-01", "y": count(ncrs, lambda r, mo=mo: r["opened_date"][:7] == mo)} for mo in months]}
    ncr_sup_line = {"label": "supplier-sourced", "points": [{"x": f"{mo}-01", "y": count(sup_ncr, lambda r, mo=mo: r["opened_date"][:7] == mo)} for mo in months]}
    pd_first, pd_last = pd_line["points"][0]["y"], pd_line["points"][-1]["y"]
    pd_prev6 = pd_line["points"][-7]["y"] if len(pd_line["points"]) >= 7 else pd_first
    rising = pd_last > pd_prev6

    pd_share = C.pct_raw(len(pd_capa), len(open_capa))
    headline = (f"At {as_of}: {len(open_capa)} open CAPAs, {len(pd_capa)} past due ({pd_share:.0f}%), "
                f"{len(crit_pd)} critical past due; past-due count {'rising' if rising else 'not rising'} "
                f"({pd_prev6} six months earlier → {pd_last}); effectiveness verified on {len(verified)} of "
                f"{len(closed_capa)} closed CAPAs ({ver_pct_raw:.0f}% vs {eff_floor:.0f}% floor, backlog {len(backlog)}); "
                f"{len(open_ncr)} open NCRs ({len(pd_ncr)} past due, mean age {C.mean(ncr_ages) or 0:.0f} d), "
                f"NCR intake {ncr_rate:.1f}/month vs {ncr_rate_prior:.1f} prior")
    if top_sup:
        headline += (f"; supplier NCRs concentrate on {top_sup[0]} ({top_sup[1]} of {len(sup_ncr)}, "
                     f"{C.pct_raw(top_sup[1], len(sup_ncr)):.0f}%)")

    narrative = {"issues": [], "risks": [], "watch": []}
    if crit_pd:
        narrative["issues"].append({
            "id": "I1", "severity": "high",
            "statement": f"{len(crit_pd)} critical CAPA(s) past due at {as_of}: "
                         + ", ".join(f"{r['record_id']} ({C.days_between(r['due_date'], as_of)} d over, {r['source']})" for r in sorted(crit_pd, key=lambda r: r["due_date"])),
            "action": "Escalate to the management-review agenda; assign owners and re-baselined due dates this week",
            "evidence": ["derived: capa-open-by-severity", f"src: {src}"],
        })
    if ver_pct_raw < eff_floor:
        narrative["issues"].append({
            "id": f"I{len(narrative['issues']) + 1}", "severity": "high",
            "statement": f"Effectiveness verification is lagging: {ver_pct_raw:.0f}% of closed CAPAs verified against "
                         f"a {eff_floor:.0f}% floor; the backlog of {len(backlog)} unverified closures grows by closure quarter",
            "action": "Schedule effectiveness checks for the oldest closures first; do not close new CAPAs without a dated verification plan",
            "evidence": ["derived: effectiveness-by-quarter", f"src: {src}", C.CONFIG_MARKER],
        })
    if rising:
        narrative["risks"].append({
            "id": "R1", "severity": "high",
            "statement": f"CAPA aging is rising — past-due open CAPAs went from {pd_prev6} to {pd_last} over six months; "
                         f"median days over due among past-due items is {C.median(pd_ages) or 0:.0f}",
            "mitigation": "Cap concurrent open CAPAs per owner; convert stalled investigations into interim containment + re-scoped CAPAs",
            "evidence": ["derived: capa-pastdue-trend", f"src: {src}"],
        })
    if top_sup and C.pct_raw(top_sup[1], len(sup_ncr)) >= 40:
        narrative["risks"].append({
            "id": f"R{len(narrative['risks']) + 1}", "severity": "medium",
            "statement": f"Supplier-sourced NCRs concentrate on {top_sup[0]} ({top_sup[1]} of {len(sup_ncr)}) — "
                         "a single supplier is driving the supplier nonconformance load",
            "mitigation": "Cross-check with the supplier scorecard and audit currency (MQ-05); consider a supplier corrective action request",
            "evidence": ["derived: supplier-ncr-concentration", f"src: {src}"],
        })
    narrative["watch"].append({
        "id": "W1",
        "statement": f"NCR intake {ncr_rate:.1f}/month in {win3[0]}..{win3[-1]} vs {ncr_rate_prior:.1f}/month in the prior three months; "
                     f"{len(pd_ncr)} open NCRs are past their due date",
        "evidence": ["derived: ncr-trend", "derived: ncr-open-by-severity", f"src: {src}"],
    })

    exp_results = {
        "E-03.1": (f"{len(crit_pd)} critical CAPA(s) past due at {as_of}",
                   "met" if not crit_pd else "not-met", ["derived: capa-open-by-severity"]),
        "E-03.2": (f"{ver_pct_raw:.0f}% of closed CAPAs effectiveness-verified ({len(verified)} of {len(closed_capa)})",
                   "met" if ver_pct_raw >= eff_floor else "not-met", ["derived: effectiveness-by-quarter"]),
    }
    exps = C.evaluate_expectations("MQ-03", exp_results)

    lines = [
        "# MQ-03 — Nonconformance and CAPA: rate, aging, past-due share, effectiveness backlog", "",
        C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [{C.CONFIG_MARKER}]", "",
        "## Headline", "",
        f"- Status is evaluated at the snapshot as-of {as_of}: open = no closure date; past due = open and "
        f"due date passed; effectiveness floor {eff_floor:.0f}% [src: {src}] [{C.CONFIG_MARKER}].",
        f"- Open CAPAs {len(open_capa)}, past due {len(pd_capa)} ({pd_share:.1f}%), critical past due {len(crit_pd)}; "
        f"median days over due among past-due CAPAs {C.median(pd_ages) or 0:.0f} [derived: capa-stat] [src: {src}].",
        f"- Closed CAPAs {len(closed_capa)}: verified {len(verified)}, unverified backlog {len(backlog)} "
        f"({ver_pct_raw:.1f}% verified) [derived: capa-stat] [src: {src}].",
        f"- Open NCRs {len(open_ncr)} ({len(pd_ncr)} past due), mean open age {C.mean(ncr_ages) or 0:.0f} d, "
        f"median {C.median(ncr_ages) or 0:.0f} d [derived: ncr-open-by-severity] [src: {src}].", "",
        "## Open CAPAs by source", "", "| Source | Open | Past due |", "|---|---|---|",
    ]
    lines += [f"| {s} [src: {src}] | {o} | {pdv} |" for s, o, pdv in capa_by_source]
    lines += ["", "## Open CAPAs by severity", "", "| Severity | Open | Past due |", "|---|---|---|"]
    lines += [f"| {s} [src: {src}] | {o} | {pdv} |" for s, o, pdv in capa_by_sev]
    lines += ["", "## Open NCRs by severity (aging)", "", "| Severity | Open | Mean age (days) |", "|---|---|---|"]
    lines += [f"| {s} [src: {src}] | {o} | {'—' if a is None else f'{a:.0f}'} |" for s, o, a in ncr_by_sev]
    lines += ["", f"## NCRs opened by source — {win3[0]}..{win3[-1]}", "", "| Source | NCRs opened |", "|---|---|"]
    lines += [f"| {s} [src: {src}] | {n} |" for s, n in ncr_by_source_win]
    lines += ["", "## Effectiveness verification by closure quarter", "",
              "| Closure quarter | Verified | Not verified |", "|---|---|---|"]
    lines += [f"| {q} [src: {src}] | {v} | {b} |" for q, v, b in eff_by_q]
    lines += ["", "## Supplier-sourced NCRs by supplier", "", "| Supplier | NCRs |", "|---|---|"]
    lines += [f"| {s} [src: {src}] | {n} |" for s, n in sup_rank]
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- All counts from the pinned NCR/CAPA register [src: {src}]; the effectiveness floor is a plan "
        f"constant [{C.CONFIG_MARKER}].",
        "- The past-due history is reconstructed at each month-end from opened / due / closed dates, so "
        "the trend is exact for this register and needs no prior snapshots [derived: capa-pastdue-trend].",
        "- NCR intake is charted monthly (all sources vs supplier-sourced) [derived: ncr-trend]; the "
        "supplier concentration uses the register's supplier_id on supplier-sourced NCRs "
        "[derived: supplier-ncr-concentration].",
        "- Not computed: an NCR rate per unit produced (needs the lot dataset as a denominator — "
        "roadmap MQ-04) and CAPA cost (roadmap MQ-09).",
    ]

    prov = {"dataset": DS, "snapshot": snap}
    data = {
        "bq": "MQ-03",
        "series": [
            {"id": "capa-stat", "label": "CAPA posture", "unit": "count", "kind": "stat",
             "evidence_class": "derived",
             "derivation": {"method": "open = no closure date at as_of; past due = open and due < as_of; verified = effectiveness_verified true among closed",
                            "inputs": [f"src: {src}", C.CONFIG_MARKER]},
             "provenance": prov,
             "points": [{"label": "open CAPAs", "value": len(open_capa), "sub": f"at {as_of}"},
                        {"label": "past due", "value": len(pd_capa), "sub": f"{pd_share:.0f}% of open; {len(crit_pd)} critical"},
                        {"label": "effectiveness verified", "value": round(ver_pct_raw, 1), "sub": f"of {len(closed_capa)} closed; backlog {len(backlog)}"},
                        {"label": "open NCRs", "value": len(open_ncr), "sub": f"{len(pd_ncr)} past due"}]},
            {"id": "capa-pastdue-trend", "label": "Open and past-due CAPAs at month-end", "unit": "count",
             "kind": "timeseries", "evidence_class": "derived",
             "derivation": {"method": "at each month-end: CAPAs opened on/before, not closed by, and (past due) due before that date",
                            "inputs": [f"src: {src}"]},
             "provenance": prov, "lines": [open_line, pd_line, pd_crit_line], "points": []},
            {"id": "ncr-trend", "label": "NCRs opened per month", "unit": "count", "kind": "timeseries",
             "evidence_class": "derived",
             "derivation": {"method": "count of NCRs by opened month, all sources and supplier-sourced", "inputs": [f"src: {src}"]},
             "provenance": prov, "lines": [ncr_total_line, ncr_sup_line], "points": []},
            {"id": "capa-open-by-source", "label": "Open vs past-due CAPAs by source", "unit": "count",
             "kind": "paired-bars", "pairs": {"a_label": "open", "b_label": "past due"},
             "evidence_class": "derived",
             "derivation": {"method": "open / past-due CAPA counts per source at as_of", "inputs": [f"src: {src}"]},
             "provenance": prov, "points": [{"label": s, "a": o, "b": pdv} for s, o, pdv in capa_by_source]},
            {"id": "capa-open-by-severity", "label": "Open vs past-due CAPAs by severity", "unit": "count",
             "kind": "paired-bars", "pairs": {"a_label": "open", "b_label": "past due"},
             "evidence_class": "derived",
             "derivation": {"method": "open / past-due CAPA counts per severity at as_of", "inputs": [f"src: {src}"]},
             "provenance": prov, "points": [{"label": s, "a": o, "b": pdv} for s, o, pdv in capa_by_sev]},
            {"id": "ncr-open-by-severity", "label": "Open NCRs by severity (mean age)", "unit": "count",
             "evidence_class": "derived",
             "derivation": {"method": "open NCR count per severity; mean age = days from opened to as_of", "inputs": [f"src: {src}"]},
             "provenance": prov, "points": [{"label": s, "value": o, "mean_age_days": _r(a)} for s, o, a in ncr_by_sev]},
            {"id": "ncr-by-source", "label": f"NCRs opened by source, {win3[0]}..{win3[-1]}", "unit": "count",
             "evidence_class": "derived",
             "derivation": {"method": "NCRs opened in the trailing three months per source", "inputs": [f"src: {src}"]},
             "provenance": prov, "points": [{"label": s, "value": n} for s, n in ncr_by_source_win]},
            {"id": "effectiveness-by-quarter", "label": "Closed CAPAs: effectiveness verified vs not, by closure quarter",
             "unit": "count", "kind": "paired-bars", "pairs": {"a_label": "verified", "b_label": "not verified"},
             "evidence_class": "derived",
             "derivation": {"method": "closed CAPAs grouped by closure quarter, split on effectiveness_verified", "inputs": [f"src: {src}"]},
             "provenance": prov, "points": [{"label": q, "a": v, "b": b} for q, v, b in eff_by_q]},
            {"id": "supplier-ncr-concentration", "label": "Supplier-sourced NCRs by supplier", "unit": "count",
             "evidence_class": "derived",
             "derivation": {"method": "count of supplier-sourced NCRs per supplier_id over the whole register", "inputs": [f"src: {src}"]},
             "provenance": prov, "points": [{"label": s, "value": n} for s, n in sup_rank]},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
