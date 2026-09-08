"""MQ-08 — process-validation and calibration posture: overdue / due items by site and
product line, and the blockers for PP3500 rev C release.

Deterministic per the MQ-08 analysis plan: statuses are read from the pinned register
(they are derived by the system of record against its data horizon); "days overdue" is
due_date vs the snapshot as_of. Rev C blockers join two pins: validation records for
PP3500 assets/processes carrying "rev C" that are not validated, and PP3500 rev C lots
that are unreleased (DHR-incomplete = blocked; DHR-complete = in process).
"""

import computations as C

VAL_DS = "manufacturing/internal-process-validation"
LOTS_DS = "manufacturing/internal-production-lots"
STATUSES = ("validated", "due", "overdue", "in-progress", "not-started")
TYPES = ("IQ", "OQ", "PQ", "calibration", "preventive-maintenance")
REV_C_LINE, REV_C = "PP3500", "C"


def run(corpus_root, out, pins):
    p = C.params_for("MQ-08")
    due_soon = int(p["due_soon_days"])
    val, vsnap = C.load_pin_csv(corpus_root, pins, VAL_DS)
    lots, lsnap = C.load_pin_csv(corpus_root, pins, LOTS_DS)
    C.assert_vocab(val, "status", STATUSES, VAL_DS)
    C.assert_vocab(val, "type", TYPES, VAL_DS)
    vsrc, lsrc = f"{VAL_DS}@{vsnap}", f"{LOTS_DS}@{lsnap}"
    as_of = C.snapshot_as_of(corpus_root, pins, VAL_DS)

    overdue = [r for r in val if r["status"] == "overdue"]
    due = [r for r in val if r["status"] == "due"]
    inprog = [r for r in val if r["status"] in ("in-progress", "not-started")]
    sites = sorted({r["site"] for r in val})
    lines_ = sorted({r["product_line"] or "shared" for r in val})

    def cnt(rows_, pred):
        return sum(1 for r in rows_ if pred(r))

    by_site = [(s, cnt(overdue, lambda r, s=s: r["site"] == s), cnt(due, lambda r, s=s: r["site"] == s),
                cnt(val, lambda r, s=s: r["site"] == s)) for s in sites]
    by_type = [(t, cnt(overdue, lambda r, t=t: r["type"] == t), cnt(due, lambda r, t=t: r["type"] == t),
                cnt(val, lambda r, t=t: r["type"] == t)) for t in TYPES]
    by_line = [(l, cnt(overdue, lambda r, l=l: (r["product_line"] or "shared") == l),
                cnt(due, lambda r, l=l: (r["product_line"] or "shared") == l),
                cnt(val, lambda r, l=l: (r["product_line"] or "shared") == l)) for l in lines_]
    overdue_cal = sorted([r for r in overdue if r["type"] == "calibration"],
                         key=lambda r: (r["site"], -C.days_between(r["due_date"], as_of)))
    worst_site = max(by_site, key=lambda t: t[1]) if by_site else None
    cal_by_site = {s: cnt(overdue_cal, lambda r, s=s: r["site"] == s) for s in sites}

    # rev C blockers — validation side
    revc_val = [r for r in val if r["product_line"] == REV_C_LINE and "rev C" in r["asset_or_process"]]
    revc_open = sorted([r for r in revc_val if r["status"] != "validated"], key=lambda r: r["due_date"])
    # rev C blockers — lot side
    revc_lots = [r for r in lots if r["product_line"] == REV_C_LINE and r["hw_rev"] == REV_C]
    released = [r for r in revc_lots if r["release_date"]]
    blocked = [r for r in revc_lots if not r["release_date"] and r["dhr_complete"] != "true"]
    in_process = [r for r in revc_lots if not r["release_date"] and r["dhr_complete"] == "true"]
    first_release = min((r["release_date"] for r in released), default=None)
    pq_open = [r for r in revc_open if r["type"] == "PQ"]

    headline = (f"At {as_of}: {len(overdue)} overdue and {len(due)} due-within-{due_soon}-day items across {len(val)} "
                f"register entries; overdue calibrations {', '.join(f'{s} {cal_by_site[s]}' for s in sites)}"
                + (f" — the cluster is at {worst_site[0]}" if worst_site and worst_site[1] > 0 else "")
                + f"; PP3500 rev C release blockers: {len(revc_open)} validation item(s) not validated ("
                + ", ".join(f"{r['type']} {r['status']} due {r['due_date']}" for r in revc_open) + ")"
                + f" and {len(blocked)} DHR-incomplete lot(s); {len(released)} rev C lots already released"
                + (f" since {first_release}" if first_release else "")
                + (f" while the fixture PQ is still {pq_open[0]['status']}" if pq_open else ""))

    narrative = {"issues": [], "risks": [], "watch": []}
    if overdue_cal:
        narrative["issues"].append({
            "id": "I1", "severity": "high",
            "statement": f"{len(overdue_cal)} calibrations overdue ({', '.join(f'{s} {cal_by_site[s]}' for s in sites)}); the "
                         f"oldest is {max(C.days_between(r['due_date'], as_of) for r in overdue_cal)} d past due — measurements "
                         "taken with out-of-calibration equipment put the affected lot records in question",
            "action": "Pull the overdue instruments from use, assess impact on lots measured since the due date, and "
                      "re-baseline the metrology schedule at the affected site",
            "evidence": ["derived: overdue-calibrations", f"src: {vsrc}"],
        })
    if blocked:
        narrative["issues"].append({
            "id": f"I{len(narrative['issues']) + 1}", "severity": "medium",
            "statement": f"{len(blocked)} PP3500 rev C lot(s) cannot be released because the device history record is "
                         f"incomplete: " + ", ".join(f"{r['lot_id']} ({r['site']}, {r['line_station']}, started {r['start_date']})" for r in blocked),
            "action": "Close the DHR gaps (missing records / signatures) and release, or disposition through an NCR",
            "evidence": ["derived: revc-lots", f"src: {lsrc}"],
        })
    if revc_open and released:
        narrative["risks"].append({
            "id": "R1", "severity": "high",
            "statement": f"{len(released)} PP3500 rev C lots have been released since {first_release} while "
                         f"{len(revc_open)} rev C validation item(s) remain open: "
                         + ", ".join(f"{r['asset_or_process']} {r['type']} ({r['status']}, due {r['due_date']}, {r['site']})" for r in revc_open)
                         + " — the register does not record which fixture tested each lot, so whether those lots ran on the "
                           "validated rev B fixture or the unvalidated rev C fixture is not determinable from these data",
            "mitigation": "Confirm the test-fixture routing for released rev C lots from the DHRs; if any ran on the rev C fixture "
                          "before PQ completion, open a CAPA and assess the released units",
            "evidence": ["derived: revc-blockers", "derived: revc-lots", f"src: {vsrc}", f"src: {lsrc}"],
        })
    if due:
        narrative["watch"].append({
            "id": "W1",
            "statement": f"{len(due)} item(s) fall due within {due_soon} days of {as_of}: "
                         + ", ".join(f"{r['asset_or_process']} ({r['type']}, {r['site']}, due {r['due_date']})" for r in sorted(due, key=lambda r: r["due_date"])[:6])
                         + (" …" if len(due) > 6 else ""),
            "evidence": ["derived: posture-by-site", f"src: {vsrc}", C.CONFIG_MARKER],
        })
    narrative["watch"].append({
        "id": f"W{len(narrative['watch']) + 1}",
        "statement": "Posture history is not available: this is a single snapshot of a status register, so 'is overdue "
                     "count rising' cannot be answered until recurring snapshots exist",
        "evidence": ["derived: posture-history"],
    })

    exp_results = {
        "E-08.1": (f"{len(overdue_cal)} overdue calibration(s) at {as_of} ({', '.join(f'{s} {cal_by_site[s]}' for s in sites)})",
                   "met" if not overdue_cal else "not-met", ["derived: overdue-calibrations"]),
        "E-08.2": (f"{len(pq_open)} rev C fixture PQ record(s) {pq_open[0]['status'] if pq_open else 'validated'}; "
                   f"{len(released)} rev C lots released" + (f" since {first_release}" if first_release else ""),
                   "met" if not (pq_open and released) else "not-met", ["derived: revc-blockers", "derived: revc-lots"]),
    }
    exps = C.evaluate_expectations("MQ-08", exp_results)

    lines = [
        "# MQ-08 — Validation and calibration posture; PP3500 rev C release blockers", "",
        C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {vsrc}] [src: {lsrc}] [{C.CONFIG_MARKER}]", "",
        "## Headline", "",
        f"- Register statuses are read as recorded at the snapshot as-of {as_of}; days overdue = due date vs "
        f"as-of; the due-soon window is {due_soon} days [src: {vsrc}] [{C.CONFIG_MARKER}].",
        f"- Overdue {len(overdue)}, due soon {len(due)}, in progress / not started {len(inprog)} of {len(val)} "
        f"entries [derived: posture-stat] [src: {vsrc}].", "",
        "## By site", "", "| Site | Overdue | Due soon | Entries |", "|---|---|---|---|",
    ]
    lines += [f"| {s} [src: {vsrc}] | {o} | {d} | {n} |" for s, o, d, n in by_site]
    lines += ["", "## By record type", "", "| Type | Overdue | Due soon | Entries |", "|---|---|---|---|"]
    lines += [f"| {t} [src: {vsrc}] | {o} | {d} | {n} |" for t, o, d, n in by_type]
    lines += ["", "## By product line", "", "| Product line | Overdue | Due soon | Entries |", "|---|---|---|---|"]
    lines += [f"| {l} [src: {vsrc}] | {o} | {d} | {n} |" for l, o, d, n in by_line]
    lines += ["", "## Overdue calibrations", "", "| Asset | Site | Product line | Due | Days overdue |", "|---|---|---|---|---|"]
    lines += [f"| {r['asset_or_process']} [src: {vsrc}] | {r['site']} | {r['product_line'] or 'shared'} | {r['due_date']} | "
              f"{C.days_between(r['due_date'], as_of)} |" for r in overdue_cal] or [f"| (none) [src: {vsrc}] | — | — | — | — |"]
    lines += ["", "## PP3500 rev C release blockers", "", "### Validation side", "",
              "| Asset / process | Type | Site | Status | Due | Owner |", "|---|---|---|---|---|---|"]
    lines += [f"| {r['asset_or_process']} [src: {vsrc}] | {r['type']} | {r['site']} | {r['status']} | {r['due_date']} | {r['owner_function']} |"
              for r in revc_open] or [f"| (all rev C validation items validated) [src: {vsrc}] | — | — | — | — | — |"]
    lines += ["", "### Lot side", "",
              f"- PP3500 rev C lots in the pinned records: {len(revc_lots)} — released {len(released)}"
              + (f" (first release {first_release})" if first_release else "")
              + f", in process {len(in_process)}, DHR-incomplete (blocked) {len(blocked)} [derived: revc-lots] [src: {lsrc}]."]
    lines += [f"- Blocked: {r['lot_id']} — {r['site']}, {r['line_station']}, started {r['start_date']} [src: {lsrc}]" for r in blocked]
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Validation / calibration statuses and dates from [src: {vsrc}]; PP3500 rev C lot release state from "
        f"[src: {lsrc}]; the due-soon window is a plan constant [{C.CONFIG_MARKER}].",
        "- Rev C blockers join the two pins on product line + hardware revision: validation records whose asset "
        "or process names rev C and is not validated, plus rev C lots without a release date "
        "[derived: revc-blockers] [derived: revc-lots].",
        "- Not computed: a posture trend (single snapshot — published as unavailable) [derived: posture-history]; "
        "which test fixture each released lot ran on (not in either pin).",
    ]

    vprov = {"dataset": VAL_DS, "snapshot": vsnap}
    data = {
        "bq": "MQ-08",
        "series": [
            {"id": "posture-stat", "label": "Validation & calibration posture", "unit": "count", "kind": "stat",
             "evidence_class": "derived",
             "derivation": {"method": "counts of register entries by status at as_of; rev C blockers = open rev C validation items + DHR-incomplete rev C lots",
                            "inputs": [f"src: {vsrc}", f"src: {lsrc}", C.CONFIG_MARKER]},
             "provenance": {"datasets": [vprov, {"dataset": LOTS_DS, "snapshot": lsnap}]},
             "points": [{"label": "overdue items", "value": len(overdue), "sub": f"of {len(val)} entries"},
                        {"label": f"due within {due_soon} d", "value": len(due), "sub": f"at {as_of}"},
                        {"label": "overdue calibrations", "value": len(overdue_cal), "sub": ", ".join(f"{s} {cal_by_site[s]}" for s in sites)},
                        {"label": "rev C blockers", "value": len(revc_open) + len(blocked), "sub": f"{len(revc_open)} validation, {len(blocked)} DHR"}]},
            {"id": "posture-by-site", "label": "Overdue vs due-soon items by site", "unit": "count",
             "kind": "paired-bars", "pairs": {"a_label": "overdue", "b_label": "due soon"},
             "evidence_class": "derived",
             "derivation": {"method": "register entries with status overdue / due per site", "inputs": [f"src: {vsrc}"]},
             "provenance": vprov, "points": [{"label": s, "a": o, "b": d, "entries": n} for s, o, d, n in by_site]},
            {"id": "posture-by-type", "label": "Overdue vs due-soon items by record type", "unit": "count",
             "kind": "paired-bars", "pairs": {"a_label": "overdue", "b_label": "due soon"},
             "evidence_class": "derived",
             "derivation": {"method": "register entries with status overdue / due per type", "inputs": [f"src: {vsrc}"]},
             "provenance": vprov, "points": [{"label": t, "a": o, "b": d, "entries": n} for t, o, d, n in by_type]},
            {"id": "posture-by-line", "label": "Overdue vs due-soon items by product line", "unit": "count",
             "kind": "paired-bars", "pairs": {"a_label": "overdue", "b_label": "due soon"},
             "evidence_class": "derived",
             "derivation": {"method": "register entries with status overdue / due per product line (empty = shared)", "inputs": [f"src: {vsrc}"]},
             "provenance": vprov, "points": [{"label": l, "a": o, "b": d, "entries": n} for l, o, d, n in by_line]},
            {"id": "overdue-calibrations", "label": "Overdue calibrations — days past due", "unit": "days",
             "evidence_class": "derived",
             "derivation": {"method": "as_of − due_date for calibration entries with status overdue", "inputs": [f"src: {vsrc}"]},
             "provenance": vprov,
             "points": [{"label": f"{r['asset_or_process']} · {r['site']}", "value": C.days_between(r["due_date"], as_of),
                         "product_line": r["product_line"] or "shared"} for r in overdue_cal]},
            {"id": "revc-blockers", "label": "PP3500 rev C — validation items not yet validated", "unit": "status",
             "evidence_class": "measured",
             "provenance": vprov,
             "points": [{"label": f"{r['asset_or_process']} {r['type']} · {r['site']}", "value": r["status"], "due": r["due_date"],
                         "owner": r["owner_function"]} for r in revc_open]},
            {"id": "revc-lots", "label": "PP3500 rev C lots by release state", "unit": "count",
             "evidence_class": "derived",
             "derivation": {"method": "rev C lots: released = release_date set; in process = unreleased with DHR complete; blocked = unreleased with DHR incomplete",
                            "inputs": [f"src: {lsrc}"]},
             "provenance": {"dataset": LOTS_DS, "snapshot": lsnap},
             "points": [{"label": "released", "value": len(released), "first_release": first_release},
                        {"label": "in process", "value": len(in_process)},
                        {"label": "blocked (DHR incomplete)", "value": len(blocked), "lots": [r["lot_id"] for r in blocked]}]},
            {"id": "posture-history", "label": "Overdue / due items over time", "unit": "count",
             "kind": "timeseries", "evidence_class": "unavailable",
             "provenance": {"note": "a status register captures posture at one as-of date; a trend needs recurring "
                                    "corpus snapshots of manufacturing/internal-process-validation (refresh on the "
                                    "dataset's 30-day cadence) — nothing is reconstructed or approximated here"},
             "lines": [], "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
