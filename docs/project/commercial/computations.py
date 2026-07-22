#!/usr/bin/env python3
"""Deterministic computations for the PDLC_DEMO business-question catalog.

Contract (per the commercial skill): invoked as
    python3 computations.py <BQ-ID> --corpus-root <abs> --out <abs-edition-dir>
with cwd = docs/project/commercial/. Reads {out}/pins.json and computes ONLY from the
pinned snapshots. Writes report.md + data.json. Deterministic: no clocks, no network —
"as-of" dates derive from the data itself. Internal (fabricated) data reports carry the
demo banner.
"""

import argparse
import csv
import datetime as dt
import json
from pathlib import Path

import yaml

BANNER = "_Demo sample data — not for clinical use._"

CAMPAIGN_DS = "commercial/internal-upgrade-campaign"
FLEET_DS = "commercial/internal-fleet"
MAUDE_DS = "commercial/openfda-maude-infusion-mfr"

COMPLETED = ("completed", "completed-after-retry")
ATTEMPT_FAIL = ("completed-after-retry", "failed-pending-retry", "rolled-back")


def load_pin_csv(corpus_root, pins, dataset):
    snap = pins[dataset]
    path = corpus_root / dataset / "snapshots" / snap / "normalized" / "records.csv"
    with open(path, newline="") as f:
        return list(csv.DictReader(f)), snap


def _entry(bq):
    cfg = yaml.safe_load(open("commercial.yml"))
    for q in cfg["questions"]:
        if q["id"] == bq:
            return q
    return {}


def params_for(bq):
    return _entry(bq).get("params", {})


def expectations_for(bq):
    return _entry(bq).get("expectations", [])


def evaluate_expectations(bq, results):
    """Join catalog expectations with computed {id: (actual, verdict, evidence[])}.
    Verdicts: met | at-risk | not-met | not-evaluable. Every expectation in the
    catalog appears in the output — an unevaluated expectation is itself a finding."""
    out = []
    for e in expectations_for(bq):
        actual, verdict, evidence = results.get(e["id"], ("not evaluated by this computation", "not-evaluable", []))
        out.append({**e, "actual": actual, "verdict": verdict, "evidence": evidence})
    return out


def expectations_section(exps):
    """Linted report rendering of the expectations table."""
    if not exps:
        return []
    lines = ["", "## Assumptions & expectations — plan vs actual", "",
             "_`unvalidated` means the expectation itself is a stand-in that has not been grounded",
             "in a plan of record or the risk file — challenge the assumption, not just the actual._", "",
             "| ID | Expectation | Expected | Actual | Verdict | Basis | Evidence |",
             "|---|---|---|---|---|---|---|"]
    for e in exps:
        ev = " ".join(f"[{x}]" for x in e.get("evidence", [])) or "—"
        val = "" if e.get("validated") else " (unvalidated)"
        lines.append(f"| {e['id']} | {e['statement']} | {e['expected']} | {e['actual']} | "
                     f"{e['verdict']}{val} | {e['basis']} | {ev} [config: commercial.yml] |")
    return lines


def write(out, report_lines, data):
    (out / "report.md").write_text("\n".join(report_lines) + "\n")
    (out / "data.json").write_text(json.dumps(data, indent=1))


def pct(n, d):
    return round(100.0 * n / d, 1) if d else 0.0


def week_start(iso_date: str) -> str:
    d = dt.date.fromisoformat(iso_date)
    return (d - dt.timedelta(days=d.weekday())).isoformat()


def week_range(a: str, b: str):
    """Every Monday from week_start(a) to week_start(b) inclusive — zero-filled
    trend lines make stalls VISIBLE instead of silently skipping empty weeks."""
    cur, end = dt.date.fromisoformat(week_start(a)), dt.date.fromisoformat(week_start(b))
    out = []
    while cur <= end:
        out.append(cur.isoformat())
        cur += dt.timedelta(days=7)
    return out


def weekly_completion_lines(rows, regions):
    """Timeseries lines: completions per week per region, zero-filled across the
    full campaign span."""
    dates = [r["completed_date"] for r in rows if r["completed_date"]]
    if not dates:
        return []
    weeks = week_range(min(dates), max(dates))
    lines = []
    for reg in regions:
        counts = {}
        for r in rows:
            if r["region"] == reg and r["completed_date"] and r["status"] in COMPLETED:
                counts[week_start(r["completed_date"])] = counts.get(week_start(r["completed_date"]), 0) + 1
        lines.append({"label": reg, "points": [{"x": w, "y": counts.get(w, 0)} for w in weeks]})
    return lines


def narrative_section(narrative):
    """Render the narrative block into linted report lines (the report is the
    linted surface; data.json mirrors it for the console panel)."""
    lines = ["", "## Narrative — Risks / Mitigations / Issues", ""]
    for grp, title in (("issues", "Issues (materialized — needs action)"),
                       ("risks", "Risks (potential — mitigation identified)"),
                       ("watch", "Watch")):
        items = narrative.get(grp, [])
        if not items:
            continue
        lines.append(f"### {title}")
        lines.append("")
        for it in items:
            ev = " ".join(f"[{e}]" for e in it.get("evidence", []))
            lines.append(f"- **{it['id']} ({it.get('severity', 'medium')})** — {it['statement']} {ev}")
            # mitigation/action lines may carry figures — they cite the same evidence
            if it.get("mitigation"):
                lines.append(f"  - _Mitigation_: {it['mitigation']} {ev}")
            if it.get("action"):
                lines.append(f"  - _Action_: {it['action']} {ev}")
        lines.append("")
    return lines


# ---------------------------------------------------------------- BQ-23 coverage

def bq23(corpus_root, out, pins):
    p = params_for("BQ-23")
    rows, snap = load_pin_csv(corpus_root, pins, CAMPAIGN_DS)
    src = f"{CAMPAIGN_DS}@{snap}"
    close = p["close_date"]
    regions = sorted({r["region"] for r in rows})
    as_of = max((r["completed_date"] for r in rows if r["completed_date"]), default="")
    window_start = (dt.date.fromisoformat(as_of) - dt.timedelta(days=27)).isoformat()

    cov, proj, series_pts, rate_pts, proj_pts = {}, {}, [], [], []
    for reg in regions:
        sub = [r for r in rows if r["region"] == reg]
        done = [r for r in sub if r["status"] in COMPLETED]
        recent = [r for r in done if r["completed_date"] and window_start <= r["completed_date"] <= as_of]
        weekly = len(recent) / 4.0
        remaining = len(sub) - len(done)
        if remaining == 0:
            pdate = as_of
        elif weekly > 0:
            pdate = (dt.date.fromisoformat(as_of) + dt.timedelta(weeks=remaining / weekly)).isoformat()
        else:
            pdate = "no-recent-completions"
        cov[reg] = (len(sub), len(done), pct(len(done), len(sub)))
        proj[reg] = (round(weekly, 1), remaining, pdate)
        series_pts.append({"label": reg, "value": pct(len(done), len(sub))})
        rate_pts.append({"label": reg, "value": round(weekly, 1)})
        proj_pts.append({"label": reg, "value": pdate})

    misses = [reg for reg in regions
              if proj[reg][2] == "no-recent-completions" or proj[reg][2] > close]
    total, total_done = len(rows), sum(1 for r in rows if r["status"] in COMPLETED)
    headline = (f"Campaign C-2026-02 is {pct(total_done, total)}% complete; at current run-rate "
                f"{', '.join(misses) if misses else 'no region'} will miss the {close} close")

    # cumulative coverage trend (% of regional target, zero-filled weekly)
    dates = [r["completed_date"] for r in rows if r["completed_date"]]
    weeks = week_range(min(dates), max(dates)) if dates else []
    cum_lines = []
    for reg in regions:
        target = cov[reg][0]
        per_week = {}
        for r in rows:
            if r["region"] == reg and r["completed_date"] and r["status"] in COMPLETED:
                per_week[week_start(r["completed_date"])] = per_week.get(week_start(r["completed_date"]), 0) + 1
        run, pts_c = 0, []
        for w in weeks:
            run += per_week.get(w, 0)
            pts_c.append({"x": w, "y": pct(run, target)})
        cum_lines.append({"label": reg, "points": pts_c})

    # narrative
    narrative = {"issues": [], "risks": [], "watch": []}
    ni = nr = 0
    for reg in regions:
        w, rem, pdate = proj[reg]
        if pdate == "no-recent-completions" and rem:
            ni += 1
            narrative["issues"].append({
                "id": f"I{ni}", "severity": "high",
                "statement": f"{reg} has zero completions in the trailing four-week window with "
                             f"{rem} devices remaining — the wave is stalled, not slow",
                "action": "Confirm scheduling vs technical root cause with the regional service "
                          "lead; restart the wave or formally re-baseline",
                "evidence": ["derived: projected-finish", f"src: {src}"],
            })
        elif pdate > close:
            nr += 1
            narrative["risks"].append({
                "id": f"R{nr}", "severity": "medium",
                "statement": f"{reg} projects to finish {pdate}, past the {close} close "
                             f"({rem} remaining at {w}/wk)",
                "mitigation": "Raise the completion rate (remote conversion, surge capacity) or "
                              "re-baseline the close with customer notification — see the capacity "
                              "outlook answer for the required-rate math",
                "evidence": ["derived: projected-finish", "config: commercial.yml"],
            })
        else:
            narrative["watch"].append({
                "id": f"W{len(narrative['watch']) + 1}",
                "statement": f"{reg} on track ({pdate} projected vs {close} close) — verify weekly",
                "evidence": ["derived: projected-finish"],
            })

    # expectations vs actuals
    exp_results = {
        "E-23.1": (f"{pct(total_done, total)}% coverage as of the pin; projected finishes: "
                   + ", ".join(f"{r} {proj[r][2]}" for r in regions),
                   "not-met" if misses else "met",
                   ["derived: projected-finish", "derived: coverage-by-region"]),
        "E-23.2": (", ".join(f"{r}: {proj[r][0]}/wk" for r in regions),
                   "not-met" if misses else "met",
                   ["derived: weekly-run-rate"]),
    }
    exps = evaluate_expectations("BQ-23", exp_results)

    lines = [
        "# BQ-23 — Campaign coverage: planned vs actual", "", BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [config: commercial.yml]", "",
        "## Coverage by region", "",
        "| Region | Target devices | Completed | Coverage | Weekly run-rate | Projected finish | Evidence |",
        "|---|---|---|---|---|---|---|",
    ]
    for reg in regions:
        t, d, c = cov[reg]
        w, rem, pd = proj[reg]
        lines.append(f"| {reg} | {t} | {d} | {c}% | {w}/wk | {pd} | [src: {src}] [derived: projected-finish] |")
    lines += [
        "",
        f"- Plan reference: campaign close {close}, coverage target {p['target_pct']}% "
        f"[config: commercial.yml]",
        f"- Run-rate window: 28 days ending {as_of} (as-of = latest completion in the pinned "
        f"snapshot) [derived: weekly-run-rate] [src: {src}]",
        f"- Cumulative coverage trend per region is charted weekly toward the {p['target_pct']}% "
        f"target [derived: cumulative-coverage] [config: commercial.yml]",
    ]
    lines += expectations_section(exps)
    lines += narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Coverage counts measured from [src: {src}] (statuses `completed`, `completed-after-retry`).",
        "- Projected finish is derived: remaining ÷ trailing four-week completion rate — it",
        "  assumes the recent rate holds [derived: projected-finish].",
    ]
    data = {
        "bq": "BQ-23",
        "series": [
            {"id": "cumulative-coverage", "label": "Cumulative coverage % by region", "unit": "%",
             "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": CAMPAIGN_DS, "snapshot": snap}, "lines": cum_lines,
             "points": []},
            {"id": "coverage-by-region", "label": "Coverage %", "unit": "%",
             "evidence_class": "measured",
             "provenance": {"dataset": CAMPAIGN_DS, "snapshot": snap}, "points": series_pts},
            {"id": "weekly-run-rate", "label": "Completions per week (trailing 4w)", "unit": "devices/week",
             "evidence_class": "derived",
             "provenance": {"dataset": CAMPAIGN_DS, "snapshot": snap}, "points": rate_pts},
            {"id": "projected-finish", "label": "Projected finish date", "unit": "date",
             "evidence_class": "derived",
             "provenance": {"dataset": CAMPAIGN_DS, "snapshot": snap}, "points": proj_pts},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    write(out, lines, data)


# ---------------------------------------------------------------- BQ-24 failure clusters

def bq24(corpus_root, out, pins):
    p = params_for("BQ-24")
    rows, snap = load_pin_csv(corpus_root, pins, CAMPAIGN_DS)
    src = f"{CAMPAIGN_DS}@{snap}"
    thr, min_n = float(p["pause_threshold_pct"]), int(p["min_cohort"])

    cohorts = {}
    for r in rows:
        cohorts.setdefault((r["hw_rev"], r["from_version"]), []).append(r)
    stats, pts = [], []
    for (hw, fv), sub in sorted(cohorts.items()):
        attempted = [r for r in sub if r["status"] != "scheduled"]
        fails = sum(1 for r in attempted if r["status"] in ATTEMPT_FAIL)
        rate = pct(fails, len(attempted))          # primary: per attempted device
        rate_all = pct(fails, len(sub))            # secondary: over the whole cohort
        stats.append({"hw": hw, "fv": fv, "n": len(sub), "attempted": len(attempted),
                      "fails": fails, "rate": rate, "rate_all": rate_all})
        pts.append({"label": f"hw {hw} / from {fv}", "value": rate, "n_attempted": len(attempted)})
    flagged = [s for s in stats if s["attempted"] >= min_n and s["rate"] > thr]
    all_attempted = [r for r in rows if r["status"] != "scheduled"]
    overall = pct(sum(1 for r in all_attempted if r["status"] in ATTEMPT_FAIL), len(all_attempted))
    if flagged:
        worst = max(flagged, key=lambda s: s["rate"])
        headline = (f"PAUSE TRIGGER: cohort hw {worst['hw']} upgrading from {worst['fv']} fails on "
                    f"{worst['rate']}% of attempted devices (threshold {thr}%) — pause the wave for "
                    f"this cohort and escalate")
    else:
        headline = f"No cohort exceeds the {thr}% pause threshold; overall per-attempt failure {overall}%"

    lines = [
        "# BQ-24 — Update failure clusters & the pause trigger", "", BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [config: commercial.yml]", "",
        "## Attempt-failure rate by cohort (hw rev × from-version)", "",
        "_Primary metric is per **attempted** device (excludes still-scheduled); the whole-cohort",
        "rate is shown for context — including never-attempted devices understates severity",
        "(adversarial-verification finding)._", "",
        "| Cohort | Devices | Attempted | Failures | Per-attempt rate | Whole-cohort rate | Evidence |",
        "|---|---|---|---|---|---|---|",
    ]
    for s in stats:
        flag = " ⚠️" if s in flagged else ""
        lines.append(f"| hw {s['hw']} / from {s['fv']} | {s['n']} | {s['attempted']} | {s['fails']} | "
                     f"{s['rate']}%{flag} | {s['rate_all']}% | [src: {src}] |")
    lines += [
        "",
        f"- Overall per-attempt failure rate: {overall}% [derived: failure-by-cohort] [src: {src}]",
        f"- Pause rule: per-attempt cohort rate > {thr}% with attempted n ≥ {min_n} [config: commercial.yml]",
    ]
    narrative = {"issues": [], "risks": [], "watch": []}
    for i, s in enumerate(flagged, 1):
        narrative["issues"].append({
            "id": f"I{i}", "severity": "high",
            "statement": f"Cohort hw {s['hw']} / from {s['fv']} fails on {s['rate']}% of attempted "
                         f"devices ({s['fails']} of {s['attempted']}) — above the pause threshold",
            "action": "Pause the wave for this cohort; open an engineering investigation on the "
                      "hw-rev × firmware interaction; resume only with a fixed package or a "
                      "cohort-specific procedure",
            "evidence": ["derived: failure-by-cohort", f"src: {src}", "config: commercial.yml"],
        })
    narrative["risks"].append({
        "id": "R1", "severity": "medium",
        "statement": "The pause threshold itself is a demo stand-in — not derived from the risk "
                     "file, so the trigger level is unvalidated",
        "mitigation": "Derive the threshold from the risk file's acceptability criteria and record "
                      "it as a validated expectation",
        "evidence": ["config: commercial.yml"],
    })
    exp_results = {
        "E-24.1": ((f"worst cohort {max(flagged, key=lambda s: s['rate'])['rate']}% (hw "
                    f"{max(flagged, key=lambda s: s['rate'])['hw']} / from "
                    f"{max(flagged, key=lambda s: s['rate'])['fv']})") if flagged
                   else f"worst qualifying cohort within threshold; overall {overall}%",
                   "not-met" if flagged else "met",
                   ["derived: failure-by-cohort"]),
    }
    exps = evaluate_expectations("BQ-24", exp_results)
    lines += expectations_section(exps)
    lines += narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Attempt failure = status in `completed-after-retry`, `failed-pending-retry`, `rolled-back`,",
        f"  measured from [src: {src}].",
    ]
    data = {
        "bq": "BQ-24",
        "series": [{"id": "failure-by-cohort", "label": "Per-attempt failure rate", "unit": "%",
                    "evidence_class": "measured",
                    "provenance": {"dataset": CAMPAIGN_DS, "snapshot": snap}, "points": pts}],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "measured"}],
        "narrative": narrative,
        "expectations": exps,
    }
    write(out, lines, data)


# ---------------------------------------------------------------- BQ-25 customer struggle & cost

def bq25(corpus_root, out, pins):
    rows, snap = load_pin_csv(corpus_root, pins, CAMPAIGN_DS)
    src = f"{CAMPAIGN_DS}@{snap}"
    assume_path = corpus_root / MAUDE_DS  # placeholder; A-002 lives on the campaign dataset
    a002 = yaml.safe_load(open(corpus_root / CAMPAIGN_DS / "assumptions" / "A-002.yml"))
    model = a002["model"]

    regions = sorted({r["region"] for r in rows})
    tick_pts, method_pts = [], []
    lines_rows = []
    for reg in regions:
        # consistent basis: tickets AND denominator both over attempted devices
        # (adversarial-verification finding: mixed basis inflated regional comparison)
        att = [r for r in rows if r["region"] == reg and r["status"] != "scheduled"]
        ticks = sum(int(r["tickets_opened"]) for r in att)
        rate = round(100.0 * ticks / len(att), 1) if att else 0.0
        tick_pts.append({"label": reg, "value": rate})
        lines_rows.append((reg, len(att), ticks, rate))
    for m in ("remote", "onsite"):
        att = [r for r in rows if r["method"] == m and r["status"] != "scheduled"]
        ticks = sum(int(r["tickets_opened"]) for r in att)
        method_pts.append({"label": m, "value": round(100.0 * ticks / len(att), 1) if att else 0.0})
    rollback_sites = sorted({r["site_id"] for r in rows if r["status"] == "rolled-back"})
    onsite_done = sum(1 for r in rows if r["method"] == "onsite" and r["status"] in COMPLETED)
    lo = round(onsite_done * model["hours_per_device"][0] * model["labor_rate_usd_hr"][0])
    hi = round(onsite_done * model["hours_per_device"][1] * model["labor_rate_usd_hr"][1])

    worst = max(lines_rows, key=lambda x: x[3])
    headline = (f"Tickets per 100 attempted upgrades are highest in {worst[0]} at {worst[3]}; "
                f"{len(rollback_sites)} site(s) rolled back; estimated customer-side cost of the "
                f"on-site portion so far ${lo:,}–${hi:,}")

    lines = [
        "# BQ-25 — Customer struggle & customer cost", "", BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [assume: A-002]", "",
        "## Tickets per 100 attempted upgrades", "",
        "_Basis: attempted devices (excludes still-scheduled) for both tickets and denominator —",
        "a consistent basis per the adversarial-verification finding._", "",
        "| Region | Attempted | Tickets | Tickets per 100 | Evidence |",
        "|---|---|---|---|---|",
    ]
    for reg, att_n, ticks, rate in lines_rows:
        lines.append(f"| {reg} | {att_n} | {ticks} | {rate} | [src: {src}] |")
    lines += [
        "",
        f"- By method: remote {method_pts[0]['value']} vs onsite {method_pts[1]['value']} tickets/100 "
        f"[derived: tickets-by-method] [src: {src}]",
        f"- Rollback sites: {', '.join(rollback_sites) if rollback_sites else 'none'} "
        f"[derived: rollback-sites] [src: {src}]",
        "",
        "## Customer cost of taking the update (stated assumption)", "",
        f"- Customer-side biomed effort and rates are NOT in our systems. The estimated range of "
        f"${lo:,}–${hi:,} for {onsite_done} completed on-site updates rests entirely on "
        f"[assume: A-002] (modeled hours-per-device × benchmark labor rate; confidence: "
        f"{a002['confidence']}).",
        "",
        "## Method & provenance", "",
        f"- Ticket and rollback counts measured from [src: {src}].",
        "- Customer cost is an assumed estimate [assume: A-002] — revisit when reference-account",
        "  validation lands (A-002 refresh trigger).",
    ]
    data = {
        "bq": "BQ-25",
        "series": [
            {"id": "tickets-per-100", "label": "Tickets per 100 attempted upgrades", "unit": "tickets/100",
             "evidence_class": "measured",
             "provenance": {"dataset": CAMPAIGN_DS, "snapshot": snap}, "points": tick_pts},
            {"id": "tickets-by-method", "label": "Tickets per 100 attempted, by method", "unit": "tickets/100",
             "evidence_class": "measured",
             "provenance": {"dataset": CAMPAIGN_DS, "snapshot": snap}, "points": method_pts},
            {"id": "rollback-sites", "label": "Sites with rollbacks", "unit": "sites",
             "evidence_class": "measured",
             "provenance": {"dataset": CAMPAIGN_DS, "snapshot": snap},
             "points": [{"label": s, "value": 1} for s in rollback_sites]},
            {"id": "customer-cost-range", "label": "Estimated customer-side cost (on-site portion)",
             "unit": "USD", "evidence_class": "assumed",
             "provenance": {"assumption": "A-002"},
             "points": [{"label": "low", "value": lo}, {"label": "high", "value": hi}]},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "assumed"}],
    }
    write(out, lines, data)


# ---------------------------------------------------------------- BQ-26 capacity outlook

def bq26(corpus_root, out, pins):
    p = params_for("BQ-26")
    rows, snap = load_pin_csv(corpus_root, pins, CAMPAIGN_DS)
    src = f"{CAMPAIGN_DS}@{snap}"
    close = p["close_date"]
    as_of = max((r["completed_date"] for r in rows if r["completed_date"]), default="")
    window_start = (dt.date.fromisoformat(as_of) - dt.timedelta(days=27)).isoformat()
    regions = sorted({r["region"] for r in rows})

    pts, need = [], []
    for reg in regions:
        sub = [r for r in rows if r["region"] == reg]
        done = [r for r in sub if r["status"] in COMPLETED]
        remaining = len(sub) - len(done)
        onsite_rem = sum(1 for r in sub if r["status"] not in COMPLETED and r["method"] == "onsite")
        recent = [r for r in done if r["completed_date"] and window_start <= r["completed_date"] <= as_of]
        weekly = len(recent) / 4.0
        weeks_left = max(0.0, (dt.date.fromisoformat(close) - dt.date.fromisoformat(as_of)).days / 7.0)
        required_rate = round(remaining / weeks_left, 1) if weeks_left else float(remaining)
        pts.append({"label": reg, "value": required_rate, "current_rate": round(weekly, 1),
                    "remaining": remaining, "onsite_remaining": onsite_rem})
        if required_rate > weekly:
            need.append((reg, round(weekly, 1), required_rate, onsite_rem))

    if need:
        gaps = "; ".join(f"{r}: needs {req}/wk vs current {cur}/wk ({ons} on-site remaining)"
                         for r, cur, req, ons in need)
        headline = f"Capacity gap to hit the {close} close — {gaps}"
    else:
        headline = f"Current run-rates cover the remaining work before {close}"

    # trend: weekly completions per region (zero-filled — stalls show as flatlines)
    trend_lines = weekly_completion_lines(rows, regions)
    stalled = [reg for reg in regions
               if next((q for q in pts if q["label"] == reg), {}).get("current_rate", 0) == 0
               and next((q for q in pts if q["label"] == reg), {}).get("remaining", 0) > 0]
    last_completion = {reg: max((r["completed_date"] for r in rows
                                 if r["region"] == reg and r["completed_date"]), default="never")
                       for reg in regions}

    # narrative — deterministic, from the computed facts
    narrative = {"issues": [], "risks": [], "watch": []}
    for i, reg in enumerate(stalled, 1):
        narrative["issues"].append({
            "id": f"I{i}", "severity": "high",
            "statement": f"{reg} wave has stalled — zero completions in the trailing four weeks "
                         f"(last completion {last_completion[reg]})",
            "action": "Re-engage site scheduling this week; re-baseline the wave or assign surge "
                      "FSE capacity; confirm root cause (scheduling vs the failure cluster)",
            "evidence": [f"src: {src}", "derived: weekly-trend"],
        })
    rn = 0
    for reg, cur_rate, req, ons in need:
        if reg in stalled:
            continue
        rn += 1
        narrative["risks"].append({
            "id": f"R{rn}", "severity": "medium",
            "statement": f"{reg} misses the {close} close at current rate "
                         f"({cur_rate}/wk vs {req}/wk required)",
            "mitigation": f"Convert on-site backlog to remote where connected ({ons} on-site "
                          "remaining), add contract labor for the delta, or slip the close with "
                          "customer notification",
            "evidence": ["derived: required-rate", f"src: {src}", "config: commercial.yml"],
        })
    rn += 1
    narrative["risks"].append({
        "id": f"R{rn}", "severity": "medium",
        "statement": "The hire/contract/slip decision is being made on run-rate projections alone — "
                     "FSE roster, utilization, and visits-per-day are not yet a corpus dataset",
        "mitigation": "Acquire an internal service-roster dataset; until then treat capacity "
                      "conclusions as directional",
        "evidence": ["derived: fse-capacity"],
    })
    narrative["watch"].append({
        "id": "W1",
        "statement": "Completion-rate trend by region (weekly, zero-filled) — a flatline is a stall, "
                     "not missing data",
        "evidence": ["derived: weekly-trend"],
    })

    # expectations vs actuals
    exp_results = {
        "E-26.1": (
            ("; ".join(f"{r}: {c}/wk vs {q} required" for r, c, q, _ in need) or "all regions at/above required rate"),
            "not-met" if need else "met",
            ["derived: required-rate"],
        ),
    }
    exps = evaluate_expectations("BQ-26", exp_results)

    lines = [
        "# BQ-26 — Service capacity outlook for the remaining waves", "", BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [config: commercial.yml]", "",
        "## Required vs current completion rate", "",
        "| Region | Remaining | Of which on-site | Current rate/wk | Required rate/wk | Evidence |",
        "|---|---|---|---|---|---|",
    ]
    for q in pts:
        lines.append(f"| {q['label']} | {q['remaining']} | {q['onsite_remaining']} | "
                     f"{q['current_rate']} | {q['value']} | [derived: required-rate] [src: {src}] |")
    lines += [
        "",
        f"- Weekly completion trend per region is charted (zero-filled) — stalls are visible as "
        f"flatlines [derived: weekly-trend] [src: {src}]",
    ]
    lines += expectations_section(exps)
    lines += narrative_section(narrative)
    lines += [
        "## Data gap (stated, not papered over)", "",
        "- Field-service-engineer roster, utilization, and visits-per-day are NOT yet a corpus",
        "  dataset — the hire/contract/slip decision needs them. This outlook is a run-rate",
        "  projection only [derived: required-rate]; the FSE-capacity series is marked unavailable.",
        "",
        "## Method & provenance", "",
        f"- Remaining counts measured, rates derived from [src: {src}]; close date and expectations "
        f"[config: commercial.yml].",
    ]
    data = {
        "bq": "BQ-26",
        "series": [
            {"id": "weekly-trend", "label": "Completions per week by region", "unit": "devices/week",
             "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": CAMPAIGN_DS, "snapshot": snap}, "lines": trend_lines,
             "points": []},
            {"id": "required-rate", "label": "Required vs current completions/week", "unit": "devices/week",
             "evidence_class": "derived",
             "provenance": {"dataset": CAMPAIGN_DS, "snapshot": snap}, "points": pts},
            {"id": "fse-capacity", "label": "FSE capacity (roster/utilization)", "unit": "FSE-days",
             "evidence_class": "unavailable",
             "provenance": {"note": "no corpus dataset acquired yet — needed for hire/contract/slip"},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    write(out, lines, data)


# ---------------------------------------------------------------- BQ-27 fleet currency

def bq27(corpus_root, out, pins):
    p = params_for("BQ-27")
    rows, snap = load_pin_csv(corpus_root, pins, FLEET_DS)
    src = f"{FLEET_DS}@{snap}"
    behind_map = {k: int(v) for k, v in p["behind_map"].items()}

    pp = [r for r in rows if r["model"] == "PP3500"]
    behind1 = [r for r in pp if behind_map.get(r["firmware_version"], 0) >= 1]
    behind2 = [r for r in pp if behind_map.get(r["firmware_version"], 0) >= 2]
    conn = [r for r in pp if r["connected"] == "yes"]
    conn_current = pct(sum(1 for r in conn if behind_map.get(r["firmware_version"], 0) == 0), len(conn))
    nonconn = [r for r in pp if r["connected"] == "no"]
    nonconn_current = pct(sum(1 for r in nonconn if behind_map.get(r["firmware_version"], 0) == 0), len(nonconn))
    pp3000 = [r for r in rows if r["model"] == "PP3000"]

    regions = sorted({r["region"] for r in pp})
    reg_pts = []
    for reg in regions:
        sub = [r for r in pp if r["region"] == reg]
        b = sum(1 for r in sub if behind_map.get(r["firmware_version"], 0) >= 1)
        reg_pts.append({"label": reg, "value": pct(b, len(sub))})

    headline = (f"{pct(len(behind1), len(pp))}% of the PP3500 fleet is ≥1 firmware version behind "
                f"({pct(len(behind2), len(pp))}% two behind); connected devices are current at "
                f"{conn_current}% vs {nonconn_current}% for unconnected")

    lines = [
        "# BQ-27 — Fleet currency: how far behind is the installed base", "", BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}]", "",
        "## PP3500 version posture", "",
        f"- Fleet size {len(pp)}; ≥1 behind {len(behind1)}; two behind {len(behind2)} [src: {src}]",
        f"- Connected vs unconnected on current version: {conn_current}% vs {nonconn_current}% "
        f"[derived: currency-by-connectivity] [src: {src}]",
        "", "## % behind by region", "",
        "| Region | % ≥1 version behind | Evidence |", "|---|---|---|",
    ]
    for q in reg_pts:
        lines.append(f"| {q['label']} | {q['value']}% | [src: {src}] |")
    lines += [
        "",
        f"- Legacy PP3000 units still in service: {len(pp3000)} (all on 2.9.x line) [src: {src}] — "
        "phase-out drift is a board-tier question (see catalog overflow).",
        "",
        "## Method & provenance", "",
        f"- Version posture measured from [src: {src}]; behind-by mapping [config: commercial.yml].",
        "- An outdated drug-error-reduction library is a patient-safety exposure, not just an ops",
        "  metric — currency lag feeds the risk conversation.",
    ]
    data = {
        "bq": "BQ-27",
        "series": [
            {"id": "behind-by-region", "label": "% ≥1 version behind", "unit": "%",
             "evidence_class": "measured",
             "provenance": {"dataset": FLEET_DS, "snapshot": snap}, "points": reg_pts},
            {"id": "currency-by-connectivity", "label": "Current-version % by connectivity", "unit": "%",
             "evidence_class": "measured",
             "provenance": {"dataset": FLEET_DS, "snapshot": snap},
             "points": [{"label": "connected", "value": conn_current},
                        {"label": "unconnected", "value": nonconn_current}]},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "measured"}],
    }
    write(out, lines, data)


# ---------------------------------------------------------------- BQ-19 MAUDE honesty showcase

def bq19(corpus_root, out, pins):
    p = params_for("BQ-19")
    rows, snap = load_pin_csv(corpus_root, pins, MAUDE_DS)
    src = f"{MAUDE_DS}@{snap}"
    aliases = yaml.safe_load(open(p["aliases"]))["canonical"]

    def canon(name):
        u = name.upper()
        for c in aliases:
            if any(u.startswith(pref.upper()) for pref in c["prefixes"]):
                return c["name"]
        return name.title()

    counts = {}
    for r in rows:
        counts[canon(r["term"])] = counts.get(canon(r["term"]), 0) + int(r["count"])
    top = sorted(counts.items(), key=lambda kv: -kv[1])[: int(p["top_n"])]
    a001 = yaml.safe_load(open(corpus_root / MAUDE_DS / "assumptions" / "A-001.yml"))
    rate_ready = isinstance(a001.get("model"), dict)

    headline = ("MAUDE event COUNTS are comparable with caveats; RATE comparison is BLOCKED — "
                "the installed-base denominator (A-001) is not yet quantified")

    lines = [
        "# BQ-19 — Adverse-event profile vs competitors (the denominator question)", "",
        f"**Verdict**: {headline} [derived: v-main] [assume: A-001]", "",
        "## Event counts by manufacturer (entity-normalized)", "",
        "_Real openFDA MAUDE data; reports received 2024-07 onward; infusion-pump product code "
        "only [src: " + src + "] [config: entity-aliases.yml]._", "",
        "| Manufacturer (canonical) | MAUDE events | Evidence |", "|---|---|---|",
    ]
    for name, n in top:
        lines.append(f"| {name} | {n:,} | [src: {src}] |")
    lines += [
        "",
        "## Why there is no rate chart here", "",
        "- MAUDE counts have NO denominator: FDA's own disclaimer warns event counts cannot",
        "  establish incidence rates. A per-manufacturer rate requires an installed-base estimate —",
        "  that estimate is [assume: A-001], whose model is not yet quantified. Until A-001 carries",
        "  a reviewed model, this analysis publishes counts only — the rate chart is mechanically",
        "  blocked, not merely discouraged.",
        "- Reporting propensity differs across manufacturers (an unmodeled bias even with a",
        "  denominator) [assume: A-001].",
        "- Manufacturer identity is normalized via the versioned alias map",
        "  [config: entity-aliases.yml]; unmatched names stay raw and visible.",
        "",
        "## Method & provenance", "",
        f"- Counts measured from openFDA's count API [src: {src}] (public domain).",
        "- No comparative-safety claim is substantiated by this data alone — see the assumption",
        "  record [assume: A-001] for what would be required.",
    ]
    data = {
        "bq": "BQ-19",
        "series": [
            {"id": "events-by-mfr", "label": "MAUDE events by manufacturer (canonical)", "unit": "events",
             "evidence_class": "measured",
             "provenance": {"dataset": MAUDE_DS, "snapshot": snap},
             "points": [{"label": k, "value": v} for k, v in top]},
            {"id": "rate-by-mfr", "label": "Event rate per installed device", "unit": "events/device",
             "evidence_class": "unavailable" if not rate_ready else "assumed",
             "provenance": {"assumption": "A-001",
                            "note": "blocked until A-001 quantifies installed-base denominators"},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "measured"}],
    }
    write(out, lines, data)


# ---------------------------------------------------------------- BQ-06 clearance cycle time

FDA510K_DS = "commercial/openfda-510k-infusion"


def _median(vals):
    vals = sorted(vals)
    n = len(vals)
    if not n:
        return None
    return vals[n // 2] if n % 2 else round((vals[n // 2 - 1] + vals[n // 2]) / 2, 1)


def bq06(corpus_root, out, pins):
    p = params_for("BQ-06")
    rows, snap = load_pin_csv(corpus_root, pins, FDA510K_DS)
    src = f"{FDA510K_DS}@{snap}"
    ivs = []
    for r in rows:
        if r["decision_date"] and r["date_received"]:
            d = (dt.date.fromisoformat(r["decision_date"]) - dt.date.fromisoformat(r["date_received"])).days
            ivs.append((r["applicant"], d))
    by_app = {}
    for app, d in ivs:
        by_app.setdefault(app, []).append(d)
    top = sorted(by_app.items(), key=lambda kv: -len(kv[1]))[: int(p["top_n"])]
    overall = _median([d for _, d in ivs])
    frequent = [(a, len(ds), _median(ds)) for a, ds in top if len(ds) >= 2]
    fastest = min(frequent, key=lambda t: t[2]) if frequent else None

    headline = (f"Competitor 510(k) review runs a median {overall} days received→decision across "
                f"{len(ivs)} infusion-pump clearances since 2021"
                + (f"; fastest frequent filer is {fastest[0]} at {fastest[2]} days median" if fastest else ""))

    lines = [
        "# BQ-06 — Clearance cycle time: competitors vs our history", "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}]", "",
        "## Review interval by frequent filer (public FDA dates)", "",
        "| Applicant | Clearances | Median days received→decision | Evidence |",
        "|---|---|---|---|",
    ]
    for app, ds in top:
        lines.append(f"| {app} | {len(ds)} | {_median(ds)} | [src: {src}] |")
    lines += [
        "",
        f"- Overall: median {overall} days across {len(ivs)} clearances [derived: cycle-by-applicant] "
        f"[src: {src}]",
        "",
        "## Our own history (stated gap)", "",
        "- Our program's K-numbers are demo-fabricated, so OUR received→decision intervals cannot be",
        "  read from public data — the comparison's left side needs the internal regulatory log as a",
        "  corpus dataset. The series is marked no-data rather than estimated.",
        "- Note the metric's scope: received→decision measures FDA review, not develop-to-market —",
        "  concept-pipeline conversion needs the internal concept register (also a stated gap).",
        "",
        "## Method & provenance", "",
        f"- Intervals computed from public `date_received` / `decision_date` in [src: {src}].",
    ]
    data = {
        "bq": "BQ-06",
        "series": [
            {"id": "cycle-by-applicant", "label": "Median review days (frequent filers)", "unit": "days",
             "evidence_class": "measured",
             "provenance": {"dataset": FDA510K_DS, "snapshot": snap},
             "points": [{"label": a, "value": _median(ds), "clearances": len(ds)} for a, ds in top]},
            {"id": "our-cycle-time", "label": "Our received→decision history", "unit": "days",
             "evidence_class": "unavailable",
             "provenance": {"note": "internal regulatory log not yet a corpus dataset (demo K-numbers are fabricated)"},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "measured"}],
    }
    write(out, lines, data)


# ---------------------------------------------------------------- BQ-12 clearance sweep

def bq12(corpus_root, out, pins):
    p = params_for("BQ-12")
    rows, snap = load_pin_csv(corpus_root, pins, FDA510K_DS)
    src = f"{FDA510K_DS}@{snap}"
    window = int(p["window_days"])
    dated = [r for r in rows if r["decision_date"]]
    as_of = max(r["decision_date"] for r in dated)
    start = (dt.date.fromisoformat(as_of) - dt.timedelta(days=window)).isoformat()
    recent = sorted((r for r in dated if start <= r["decision_date"] <= as_of),
                    key=lambda r: r["decision_date"], reverse=True)

    def flags(name):
        u = name.upper()
        return [lane for lane, kws in p["watch_keywords"].items() if any(k in u for k in kws)]

    flagged = [(r, flags(r["device_name"])) for r in recent]
    flagged = [(r, f) for r, f in flagged if f]
    quarters = {}
    for r in dated:
        y, m = r["decision_date"][:4], int(r["decision_date"][5:7])
        q = f"{y}-Q{(m - 1) // 3 + 1}"
        quarters[q] = quarters.get(q, 0) + 1

    if recent:
        headline = (f"{len(recent)} infusion-pump clearance(s) in the {window}-day window ending {as_of}; "
                    f"{len(flagged)} flag roadmap-relevant keywords — review against the roadmap lanes")
    else:
        headline = f"No new infusion-pump clearances in the {window}-day window ending {as_of}"

    lines = [
        "# BQ-12 — Competitor clearance sweep vs the roadmap", "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [config: commercial.yml]", "",
        f"## Clearances in the window ({start} → {as_of})", "",
    ]
    if recent:
        lines += ["| K-number | Applicant | Device | Decision | Roadmap flags | Evidence |",
                  "|---|---|---|---|---|---|"]
        for r in recent:
            fl = ", ".join(flags(r["device_name"])) or "—"
            lines.append(f"| {r['k_number']} | {r['applicant']} | {r['device_name'][:60]} | "
                         f"{r['decision_date']} | {fl} | [src: {src}] |")
    else:
        lines.append(f"- None in window [src: {src}]")
    lines += [
        "",
        "## Method & provenance", "",
        f"- Window anchored to the newest decision date in the pinned snapshot ({as_of}) so the sweep",
        f"  is deterministic against its pin [src: {src}].",
        "- Roadmap flags are keyword matches on the public device name [config: commercial.yml] —",
        "  a triage aid for analyst review against the roadmap lanes, not a capability judgment.",
        "- Scope: product code FRN only; adjacent SaMD/monitoring codes need a wider corpus dataset",
        "  before concluding no entrant activity (dataset README notes this limitation).",
    ]
    data = {
        "bq": "BQ-12",
        "series": [
            {"id": "clearances-by-quarter", "label": "FRN clearances per quarter", "unit": "clearances",
             "evidence_class": "measured",
             "provenance": {"dataset": FDA510K_DS, "snapshot": snap},
             "points": [{"label": q, "value": n} for q, n in sorted(quarters.items())]},
            {"id": "window-flagged", "label": f"Window clearances ({start} → {as_of})", "unit": "",
             "evidence_class": "measured",
             "provenance": {"dataset": FDA510K_DS, "snapshot": snap},
             "points": [{"label": r["k_number"], "value": f"{r['applicant']} — "
                         + (", ".join(f) if f else "no flags")} for r, f in
                        ([(r, flags(r["device_name"])) for r in recent] or [])]},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "measured"}],
    }
    write(out, lines, data)


# ---------------------------------------------------------------- BQ-18 complaints vs thresholds

COMPLAINTS_DS = "commercial/internal-complaints"


def bq18(corpus_root, out, pins):
    p = params_for("BQ-18")
    rows, snap = load_pin_csv(corpus_root, pins, COMPLAINTS_DS)
    fleet, fsnap = load_pin_csv(corpus_root, pins, FLEET_DS)
    src = f"{COMPLAINTS_DS}@{snap}"
    fsrc = f"{FLEET_DS}@{fsnap}"
    window = int(p["window_days"])
    n_fleet = len(fleet)
    as_of = max(r["date_opened"] for r in rows)
    start = (dt.date.fromisoformat(as_of) - dt.timedelta(days=window)).isoformat()
    prev_start = (dt.date.fromisoformat(start) - dt.timedelta(days=window)).isoformat()

    def counts(a, b):
        out_c = {}
        for r in rows:
            if a <= r["date_opened"] < b:
                out_c[r["category"]] = out_c.get(r["category"], 0) + 1
        return out_c

    cur = counts(start, "9999")
    prev = counts(prev_start, start)
    thr = p["rate_threshold_per_100"]

    def rate(n):
        return round(100.0 * n / n_fleet, 2)

    ranked = sorted(cur.items(), key=lambda kv: -kv[1])
    breaches = []
    for cat, n in ranked:
        t = float(thr.get(cat, thr["default"]))
        if rate(n) > t:
            breaches.append((cat, rate(n), t))
    top3 = ranked[:3]

    if breaches:
        b = "; ".join(f"{c} at {r} per 100 devices vs threshold {t}" for c, r, t in breaches)
        headline = f"CAPA-review trigger: {b} (trailing {window}d ending {as_of})"
    else:
        headline = (f"No complaint category exceeds its rate threshold in the trailing {window}d "
                    f"ending {as_of}; top category is {top3[0][0]} at {rate(top3[0][1])} per 100 devices")

    lines = [
        "# BQ-18 — Complaint categories vs risk-file thresholds", "", BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [config: commercial.yml]", "",
        f"## Trailing window, rate-normalized (stated denominator: {n_fleet} fleet devices "
        f"[src: {fsrc}])", "",
        "| Category | Complaints | Rate per 100 devices | Threshold | Prior window | Evidence |",
        "|---|---|---|---|---|---|",
    ]
    for cat, n in ranked:
        t = float(thr.get(cat, thr["default"]))
        mark = " ⚠️" if rate(n) > t else ""
        lines.append(f"| {cat} | {n} | {rate(n)}{mark} | {t} | {prev.get(cat, 0)} | "
                     f"[src: {src}] [config: commercial.yml] |")
    # monthly trend for the top-3 categories (zero-filled)
    months = sorted({r["date_opened"][:7] for r in rows})
    top3_cats = [c for c, _ in top3]
    trend_lines = []
    for cat in top3_cats:
        by_m = {}
        for r in rows:
            if r["category"] == cat:
                by_m[r["date_opened"][:7]] = by_m.get(r["date_opened"][:7], 0) + 1
        trend_lines.append({"label": cat, "points": [{"x": m + "-01", "y": by_m.get(m, 0)} for m in months]})

    rising = sum(cur.values()) > 1.3 * max(1, sum(prev.values()))
    narrative = {"issues": [], "risks": [], "watch": []}
    for i, (cat, r_, t) in enumerate(breaches, 1):
        narrative["issues"].append({
            "id": f"I{i}", "severity": "high",
            "statement": f"{cat} at {r_} per 100 devices exceeds its threshold of {t} in the "
                         f"trailing {window}d window",
            "action": "Open a CAPA review; stratify by site, firmware version, and device age; "
                      "check correlation with the upgrade campaign's rollback sites",
            "evidence": ["derived: rate-by-category", f"src: {src}", "config: commercial.yml"],
        })
    if rising:
        narrative["risks"].append({
            "id": "R1", "severity": "medium",
            "statement": f"Total complaint volume is rising window-over-window "
                         f"({sum(cur.values())} vs {sum(prev.values())})",
            "mitigation": "Trend-analyze monthly by category; if the rise persists a second "
                          "window, escalate to management review",
            "evidence": ["derived: window-trend"],
        })
    narrative["risks"].append({
        "id": f"R{2 if rising else 1}", "severity": "medium",
        "statement": "The category thresholds are demo stand-ins, not the risk file's documented "
                     "acceptability criteria — a breach verdict is only as good as its threshold",
        "mitigation": "Re-derive thresholds from the risk file and mark the expectation validated",
        "evidence": ["config: commercial.yml"],
    })
    exp_results = {
        "E-18.1": (("; ".join(f"{c} {r_} vs {t}" for c, r_, t in breaches)) if breaches
                   else f"all categories within thresholds; top {top3[0][0]} at {rate(top3[0][1])}",
                   "not-met" if breaches else "met",
                   ["derived: rate-by-category"]),
        "E-18.2": (f"current {sum(cur.values())} vs prior {sum(prev.values())}",
                   "not-met" if rising else "met",
                   ["derived: window-trend"]),
    }
    exps = evaluate_expectations("BQ-18", exp_results)
    lines += expectations_section(exps)
    lines += narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Complaint counts measured from [src: {src}]; denominator is the installed-base registry",
        f"  [src: {fsrc}] — the ONLY sanctioned internal denominator (per the corpus conventions).",
        "- Thresholds are demo stand-ins for risk-file complaint-rate commitments",
        "  [config: commercial.yml]; a breach obligates a CAPA review, not automatically a CAPA.",
    ]
    data = {
        "bq": "BQ-18",
        "series": [
            {"id": "monthly-trend", "label": "Monthly complaints — top 3 categories", "unit": "complaints",
             "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": COMPLAINTS_DS, "snapshot": snap}, "lines": trend_lines,
             "points": []},
            {"id": "rate-by-category", "label": f"Complaints per 100 devices (trailing {window}d)",
             "unit": "per 100 devices", "evidence_class": "measured",
             "provenance": {"dataset": COMPLAINTS_DS, "snapshot": snap},
             "points": [{"label": c, "value": rate(n), "count": n} for c, n in ranked]},
            {"id": "window-trend", "label": "Complaints: current vs prior window", "unit": "complaints",
             "evidence_class": "derived",
             "provenance": {"dataset": COMPLAINTS_DS, "snapshot": snap},
             "points": [{"label": "current", "value": sum(cur.values())},
                        {"label": "prior", "value": sum(prev.values())}]},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "measured"}],
        "narrative": narrative,
        "expectations": exps,
    }
    write(out, lines, data)


# ---------------------------------------------------------------- main

DISPATCH = {"BQ-06": bq06, "BQ-12": bq12, "BQ-18": bq18,
            "BQ-19": bq19, "BQ-23": bq23, "BQ-24": bq24, "BQ-25": bq25, "BQ-26": bq26, "BQ-27": bq27}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("bq")
    p.add_argument("--corpus-root", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    out, corpus_root = Path(a.out), Path(a.corpus_root)
    pins = json.loads((out / "pins.json").read_text())
    if a.bq not in DISPATCH:
        raise SystemExit(f"no computation for {a.bq}")
    DISPATCH[a.bq](corpus_root, out, pins)


if __name__ == "__main__":
    main()
