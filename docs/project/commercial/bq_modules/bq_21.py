"""BQ-21 — Regulatory exposure: field-action docket, MDR timeliness, open items.

Per plans/BQ-21.md: docket roll-up by type × status, trailing-12-month MDR on-time
rate (filing-date basis), days-to-deadline on open items (snapshot-date anchor), FSCA
rollout as recorded, and the "if FDA walks in tomorrow" exposure list. Deterministic:
event windows anchor on the latest event date in the pin; deadline urgency anchors on
the snapshot date. No clocks, no network.
"""

import datetime as dt
import re

import computations as C

DOCKET_DS = "commercial/internal-regulatory-docket"


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
    p = C.params_for("BQ-21")
    rows, snap = C.load_pin_csv(corpus_root, pins, DOCKET_DS)
    src = f"{DOCKET_DS}@{snap}"
    trailing_days = round(int(p["trailing_months"]) * 365 / 12)  # 12 months -> 365 days

    # anchors (per plan): events → latest event date in the pin; urgency → snapshot date
    event_anchor = max([r["opened_date"] for r in rows] +
                       [r["filed_date"] for r in rows if r["filed_date"]])
    snap_anchor = snap.split(".")[0]  # edition pin date — deterministic proxy for "now"
    win_start = (dt.date.fromisoformat(event_anchor) - dt.timedelta(days=trailing_days)).isoformat()

    # --- docket roll-up: type × status --------------------------------------
    types = sorted({r["type"] for r in rows})
    statuses = ["open", "filed", "closed"]
    roll = {t: {s: sum(1 for r in rows if r["type"] == t and r["status"] == s)
                for s in statuses} for t in types}

    # --- MDR timeliness ------------------------------------------------------
    def days_late(r):
        return (dt.date.fromisoformat(r["filed_date"])
                - dt.date.fromisoformat(r["regulatory_deadline"])).days

    mdrs_filed = [r for r in rows if r["type"] == "mdr" and r["filed_date"]]
    late_all = sorted((r for r in mdrs_filed if days_late(r) > 0), key=lambda r: r["filed_date"])
    in_win = [r for r in mdrs_filed if win_start < r["filed_date"] <= event_anchor]
    late_win = [r for r in in_win if days_late(r) > 0]
    ontime_rate = C.pct(len(in_win) - len(late_win), len(in_win))
    # Lifetime late filings that fall outside the trailing window — computed, never a
    # string literal (red-team finding RT-21-1).
    late_prewin = [r for r in late_all if not (win_start < r["filed_date"] <= event_anchor)]

    # --- basis sensitivity: the published rate vs the other defensible bases ---
    # (adversarial-verification caveat: publish the alternates so the reader sees
    # whether the committed basis flatters, and whether any verdict flips)
    pin_win_start = (dt.date.fromisoformat(snap_anchor)
                     - dt.timedelta(days=trailing_days)).isoformat()
    in_win_pin = [r for r in mdrs_filed if pin_win_start < r["filed_date"] <= snap_anchor]
    late_win_pin = [r for r in in_win_pin if days_late(r) > 0]
    in_win_open = [r for r in mdrs_filed if win_start < r["opened_date"] <= event_anchor]
    late_win_open = [r for r in in_win_open if days_late(r) > 0]
    bases = [
        ("filed-date window, latest-event anchor (published)", in_win, late_win),
        ("filed-date window, pin-date anchor", in_win_pin, late_win_pin),
        ("opened-date window, latest-event anchor", in_win_open, late_win_open),
        ("lifetime (all filed MDRs)", mdrs_filed, late_all),
    ]
    basis_rows = [(lbl, C.pct(len(w) - len(lt), len(w)), len(w) - len(lt), len(w), len(lt))
                  for lbl, w, lt in bases]
    alt_rates = [rate for _, rate, _, _, _ in basis_rows[1:]]
    most_favorable = ontime_rate >= max(alt_rates) if alt_rates else True
    # E-21.1 flips iff any basis disagrees with the published basis on "any late filing"
    basis_flips = [lbl for lbl, _, _, _, n_late in basis_rows
                   if (n_late > 0) != (len(late_win) > 0)]

    # --- open items vs deadline (snapshot-date anchor) -----------------------
    open_items = [r for r in rows if r["status"] == "open"]
    open_detail = []
    for r in open_items:
        if r["filed_date"]:
            posture = "report filed on time; action open pending completion" \
                if r["filed_date"] <= r["regulatory_deadline"] else "report filed LATE; action open"
            dtd = None
        else:
            dtd = (dt.date.fromisoformat(r["regulatory_deadline"])
                   - dt.date.fromisoformat(snap_anchor)).days
            posture = (f"unfiled — {dtd} days to deadline" if dtd >= 0
                       else f"unfiled — deadline BLOWN by {-dtd} days")
        open_detail.append((r, dtd, posture))

    fsca = next((r for r in rows if r["type"] == "fsca"), None)
    # FSCA rollout state parsed from the pinned record's description (plan commitment) —
    # never a hard-coded summary (red-team finding RT-21-1). If the description carries
    # no "Rollout status:" clause, the report says so instead of inventing one.
    fsca_rollout, fsca_pending = None, []
    if fsca:
        m = re.search(r"Rollout status:\s*(.+?)\s*$", fsca["description"])
        if m:
            fsca_rollout = m.group(1).strip()
            fsca_pending = re.findall(r"(\w+) pending", fsca_rollout)

    # --- exposure list ("if FDA walks in tomorrow") --------------------------
    exposure = [(r["record_id"], posture) for r, _, posture in open_detail]
    exposure += [(r["record_id"], f"filed {days_late(r)} days late ({r['filed_date']})")
                 for r in late_win]

    unfiled_urgent = [(r, dtd) for r, dtd, _ in open_detail if dtd is not None]
    open_bits = [f"{r['record_id']} due in {dtd} days at the pin date" for r, dtd in unfiled_urgent]
    if fsca and fsca["status"] == "open":
        open_bits.append(f"{fsca['record_id']} rollout incomplete")
    headline = (f"If FDA walks in tomorrow: {len(open_items)} open docket item(s) "
                f"({'; '.join(open_bits) or 'none urgent'}) and {len(late_win)} late MDR "
                f"filing(s) in the trailing 12 months — on-time rate {ontime_rate}% "
                f"({len(in_win) - len(late_win)} of {len(in_win)}); E-21.1 "
                f"{'NOT met' if late_win else 'met'}")

    # --- monthly filing trend (zero-filled) ----------------------------------
    span = month_range(min(r["filed_date"] for r in mdrs_filed)[:7],
                       max(r["filed_date"] for r in mdrs_filed)[:7])
    per_m, per_m_late = {}, {}
    for r in mdrs_filed:
        m = r["filed_date"][:7]
        per_m[m] = per_m.get(m, 0) + 1
        if days_late(r) > 0:
            per_m_late[m] = per_m_late.get(m, 0) + 1
    trend_lines = [
        {"label": "MDR filings", "points": [{"x": m + "-01", "y": per_m.get(m, 0)} for m in span]},
        {"label": "late filings", "points": [{"x": m + "-01", "y": per_m_late.get(m, 0)} for m in span]},
    ]

    # --- expectations --------------------------------------------------------
    exp_results = {
        "E-21.1": (f"{len(late_win)} late filing(s) in the trailing 12 months "
                   + (f"({'; '.join(r['record_id'] + ' +' + str(days_late(r)) + 'd' for r in late_win)}); "
                      if late_win else "; ")
                   + f"lifetime record holds {len(late_all)} late filing(s)",
                   "not-met" if late_win else "met",
                   ["derived: ontime-rate", f"src: {src}"]),
    }
    exps = C.evaluate_expectations("BQ-21", exp_results)

    # --- narrative -----------------------------------------------------------
    narrative = {"issues": [], "risks": [], "watch": []}
    ni = 0
    for r, dtd in unfiled_urgent:
        ni += 1
        narrative["issues"].append({
            "id": f"I{ni}", "severity": "high",
            "statement": f"{r['record_id']} ({r['category']}) is open and unfiled with {dtd} days "
                         f"to its regulatory deadline ({r['regulatory_deadline']}) at the pin date"
                         + (" — the over-delivery event under investigation (see BQ-20)"
                            if r["category"] == "over-delivery" else ""),
            "action": "Confirm the MDR narrative is in final review NOW; file before the deadline; "
                      "escalate to RA leadership if investigation inputs are the blocker",
            "evidence": ["derived: open-items", f"src: {src}"],
        })
    if fsca:
        ni += 1
        narrative["issues"].append({
            "id": f"I{ni}", "severity": "medium",
            "statement": f"{fsca['record_id']} ({fsca['category']}) remains open"
                         + (f": rollout as recorded — \"{fsca_rollout}\"" if fsca_rollout
                            else "; no rollout status is recorded in the docket description")
                         + (f" — an FDA investigator will ask why "
                            f"{', '.join(fsca_pending)} has not started" if fsca_pending else ""),
            "action": ((f"Get the pending region(s) ({', '.join(fsca_pending)}) scheduled and "
                        f"in-progress completion dated; " if fsca_pending else "")
                       + "track per-site completion evidence for the FSCA file"),
            "evidence": ["derived: open-items", f"src: {src}"],
        })
    if late_win:
        narrative["risks"].append({
            "id": "R1", "severity": "medium",
            "statement": f"{len(late_win)} MDR(s) filed late inside the trailing window "
                         f"({'; '.join(r['record_id'] + ' +' + str(days_late(r)) + 'd' for r in late_win)}) — "
                         f"a repeat-observation pattern an investigator can cite even at a "
                         f"{ontime_rate}% on-time rate",
            "mitigation": "Root-cause the late filing (intake-to-decision lag vs narrative "
                          "drafting); add a deadline-minus-7-days internal gate to the RA tracker",
            "evidence": ["derived: ontime-rate", f"src: {src}"],
        })
    narrative["risks"].append({
        "id": f"R{2 if late_win else 1}", "severity": "medium",
        "statement": "This docket audits filing timeliness of what was docketed — the "
                     "complaint-to-MDR reportability decision trail is not a corpus dataset, so "
                     "under-docketing would be invisible here",
        "mitigation": "Acquire the reportability-decision log as a dataset; until then pair this "
                      "answer with BQ-20's complaint-level watch",
        "evidence": ["derived: docket-rollup"],
    })
    narrative["watch"].append({
        "id": "W1",
        "statement": f"Lifetime late filings: {len(late_all)} "
                     f"({'; '.join(r['record_id'] + ' +' + str(days_late(r)) + 'd' for r in late_all)})"
                     + (f" — {len(late_prewin)} "
                        f"({', '.join(r['record_id'] for r in late_prewin)}) predate(s) the "
                        f"trailing window but stay(s) on the audit record" if late_prewin
                        else " — all fall inside the trailing window"),
        "evidence": ["derived: ontime-rate", f"src: {src}"],
    })

    # --- report --------------------------------------------------------------
    lines = [
        "# BQ-21 — Regulatory exposure: docket, MDR timeliness, open items", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [config: commercial.yml]", "",
        f"## Docket roll-up (type × status; {len(rows)} records) [src: {src}]", "",
        "| Type | Open | Filed | Closed | Total |",
        "|---|---|---|---|---|",
    ]
    for t in types:
        r_ = roll[t]
        lines.append(f"| {t} [src: {src}] | {r_['open']} | {r_['filed']} | {r_['closed']} | "
                     f"{sum(r_.values())} |")
    lines += [
        "",
        "## MDR timeliness — trailing 12 months (filing-date basis)", "",
        f"- On-time rate: {ontime_rate}% — {len(in_win) - len(late_win)} of {len(in_win)} MDRs "
        f"filed in the window ({win_start} → {event_anchor}) met their deadline "
        f"[derived: ontime-rate] [src: {src}]",
        f"- Late in window: " + (", ".join(f"{r['record_id']} (+{days_late(r)}d)" for r in late_win)
                                 if late_win else "none")
        + f" [derived: ontime-rate] [src: {src}]",
        f"- Lifetime late filings: " + ", ".join(f"{r['record_id']} (+{days_late(r)}d)" for r in late_all)
        + (f" — {', '.join(r['record_id'] for r in late_prewin)} predate(s) the trailing window; "
           if late_prewin else " — all inside the trailing window; ")
        + f"the window narrows the rate, it does not hide the record "
        f"[derived: ontime-rate] [src: {src}]",
        f"- Monthly filings vs late filings are charted (zero-filled) [derived: filing-trend] "
        f"[src: {src}]",
        "",
        "## Basis sensitivity (disclosed, not absorbed)", "",
        "_The trailing on-time rate is published on the plan-committed basis (filed-date window,",
        "latest-event anchor). The other defensible bases are shown so the reader sees how much",
        "the basis choice moves the rate — and whether any verdict flips._", "",
        "| Basis | On-time rate | On time / in basis | Late |",
        "|---|---|---|---|",
    ] + [
        f"| {lbl} [derived: basis-sensitivity] [src: {src}] | {rate}% | {ok} of {n} | {n_late} |"
        for lbl, rate, ok, n, n_late in basis_rows
    ] + [
        "",
        (f"- The published basis yields the most favorable rate of the "
         f"{len(basis_rows)} defensible bases" if most_favorable else
         f"- The published basis is not the most favorable of the {len(basis_rows)} defensible "
         f"bases") + " [derived: basis-sensitivity]",
        ("- E-21.1 does NOT flip under any basis — every basis carries at least one late filing "
         "[derived: basis-sensitivity]" if not basis_flips and late_win else
         f"- E-21.1 verdict is basis-SENSITIVE — it flips under: {'; '.join(basis_flips)} "
         f"[derived: basis-sensitivity]" if basis_flips else
         "- E-21.1 holds (met) under every basis [derived: basis-sensitivity]"),
        "",
        f"## Open items vs deadline (urgency anchored at the pin date {snap_anchor})", "",
        "| Record | Type | Category | Opened | Deadline | Posture |",
        "|---|---|---|---|---|---|",
    ]
    for r, dtd, posture in open_detail:
        lines.append(f"| {r['record_id']} [src: {src}] | {r['type']} | {r['category']} | "
                     f"{r['opened_date']} | {r['regulatory_deadline']} | {posture} |")
    if fsca:
        lines += [
            "",
            f"- FSCA rollout as recorded in the docket: \"{fsca['description']}\" [src: {src}] — "
            f"reported qualitatively; per-site completion telemetry is not a corpus dataset "
            f"(stated gap).",
        ]
    lines += [
        "",
        "## Exposure list — what an investigator finds tomorrow", "",
    ]
    for rid, posture in exposure:
        lines.append(f"- {rid}: {posture} [derived: exposure-list] [src: {src}]")
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- All docket facts measured from [src: {src}]; trailing window "
        f"[config: commercial.yml].",
        f"- Two anchors per the plan: event windows at the latest event date in the pin "
        f"({event_anchor}); deadline urgency at the snapshot date ({snap_anchor}) — both "
        f"deterministic, no clocks [src: {src}].",
        "- On-time = filed on or before the regulatory deadline; the rate covers MDRs by",
        f"  filing date within the window [derived: ontime-rate] [src: {src}].",
    ]

    data = {
        "bq": "BQ-21",
        "series": [
            {"id": "ontime-stat", "label": "MDR on-time rate (trailing 12 months)", "unit": "%",
             "kind": "stat", "evidence_class": "measured",
             "provenance": {"dataset": DOCKET_DS, "snapshot": snap},
             "points": [{"label": f"of {len(in_win)} MDRs filed in the window, on time",
                         "value": ontime_rate},
                        {"label": "open docket items", "value": len(open_items)}]},
            {"id": "docket-rollup", "label": "Docket records by type", "unit": "records",
             "evidence_class": "measured",
             "provenance": {"dataset": DOCKET_DS, "snapshot": snap},
             "points": [{"label": t, "value": sum(roll[t].values()),
                         "open": roll[t]["open"], "filed": roll[t]["filed"],
                         "closed": roll[t]["closed"]} for t in types]},
            {"id": "filing-trend", "label": "MDR filings vs late filings per month",
             "unit": "filings/month", "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": DOCKET_DS, "snapshot": snap},
             "lines": trend_lines, "points": []},
            {"id": "open-items", "label": "Open items vs deadline", "unit": "",
             "evidence_class": "measured",
             "provenance": {"dataset": DOCKET_DS, "snapshot": snap},
             "points": [{"label": r["record_id"], "value": posture} for r, _, posture in open_detail]},
            {"id": "ontime-rate", "label": "On-time vs late (trailing window)", "unit": "MDRs",
             "evidence_class": "derived",
             "derivation": {"method": "MDRs with filed_date in the 365 days ending at the latest "
                                      "event date in the pin, split by filed_date <= regulatory_deadline",
                            "inputs": [f"src: {src}", "config: commercial.yml"]},
             "provenance": {"dataset": DOCKET_DS, "snapshot": snap},
             "points": [{"label": "on time", "value": len(in_win) - len(late_win)},
                        {"label": "late", "value": len(late_win)}]},
            {"id": "basis-sensitivity", "label": "On-time rate under alternative bases", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "on-time rate recomputed under the pin-date-anchored "
                                      "filed-date window, the opened-date window, and lifetime — "
                                      "alongside the published filed-date/latest-event basis",
                            "inputs": [f"src: {src}", "config: commercial.yml",
                                       "derived: ontime-rate"]},
             "provenance": {"dataset": DOCKET_DS, "snapshot": snap},
             "points": [{"label": lbl, "value": rate, "on_time": ok, "in_basis": n, "late": n_late}
                        for lbl, rate, ok, n, n_late in basis_rows]},
            {"id": "exposure-list", "label": "Exposure list (open + late items)", "unit": "items",
             "evidence_class": "derived",
             "derivation": {"method": "union of open docket items and late filings inside the "
                                      "trailing window, enumerated by record id",
                            "inputs": [f"src: {src}", "derived: ontime-rate", "derived: open-items"]},
             "provenance": {"dataset": DOCKET_DS, "snapshot": snap},
             "points": [{"label": rid, "value": posture} for rid, posture in exposure]},
        ],
        # v-main carries the derived on-time rate, so its evidence class is derived
        # (was "measured" — taxonomy inconsistency, red-team finding RT-21-2)
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
