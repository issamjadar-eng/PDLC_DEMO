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


def params_for(bq):
    cfg = yaml.safe_load(open("commercial.yml"))
    for q in cfg["questions"]:
        if q["id"] == bq:
            return q.get("params", {})
    return {}


def write(out, report_lines, data):
    (out / "report.md").write_text("\n".join(report_lines) + "\n")
    (out / "data.json").write_text(json.dumps(data, indent=1))


def pct(n, d):
    return round(100.0 * n / d, 1) if d else 0.0


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
        "",
        "## Method & provenance", "",
        f"- Coverage counts measured from [src: {src}] (statuses `completed`, `completed-after-retry`).",
        "- Projected finish is derived: remaining ÷ trailing four-week completion rate — it",
        "  assumes the recent rate holds [derived: projected-finish].",
    ]
    data = {
        "bq": "BQ-23",
        "series": [
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
        "",
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
        "## Data gap (stated, not papered over)", "",
        "- Field-service-engineer roster, utilization, and visits-per-day are NOT yet a corpus",
        "  dataset — the hire/contract/slip decision needs them. This outlook is a run-rate",
        "  projection only [derived: required-rate]; the FSE-capacity series is marked unavailable.",
        "",
        "## Method & provenance", "",
        f"- Remaining counts measured, rates derived from [src: {src}]; close date "
        f"[config: commercial.yml].",
    ]
    data = {
        "bq": "BQ-26",
        "series": [
            {"id": "required-rate", "label": "Required vs current completions/week", "unit": "devices/week",
             "evidence_class": "derived",
             "provenance": {"dataset": CAMPAIGN_DS, "snapshot": snap}, "points": pts},
            {"id": "fse-capacity", "label": "FSE capacity (roster/utilization)", "unit": "FSE-days",
             "evidence_class": "unavailable",
             "provenance": {"note": "no corpus dataset acquired yet — needed for hire/contract/slip"},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
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


# ---------------------------------------------------------------- main

DISPATCH = {"BQ-19": bq19, "BQ-23": bq23, "BQ-24": bq24, "BQ-25": bq25, "BQ-26": bq26, "BQ-27": bq27}


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
