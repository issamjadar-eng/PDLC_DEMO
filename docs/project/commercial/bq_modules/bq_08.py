"""BQ-08 — Win/loss drivers and the predictive-monitoring-gap losses.

Contract: run(corpus_root, out, pins) per computations.py module dispatch.
Deterministic; trailing-365d window anchored at the pinned snapshot's newest
close_date. Definitions committed in plans/BQ-08.md.
"""

import datetime as dt

import computations as C

WINLOSS_DS = "commercial/internal-winloss"


def month_range(a, b):
    """Every month (YYYY-MM) from a to b inclusive — zero-filled trend axes."""
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
    p = C.params_for("BQ-08")
    rows, snap = C.load_pin_csv(corpus_root, pins, WINLOSS_DS)
    src = f"{WINLOSS_DS}@{snap}"
    window = int(p["window_days"])

    anchor = max(r["close_date"] for r in rows)
    start = (dt.date.fromisoformat(anchor) - dt.timedelta(days=window)).isoformat()
    in_win = [r for r in rows if start < r["close_date"] <= anchor]
    won = [r for r in in_win if r["outcome"] == "won"]
    lost = [r for r in in_win if r["outcome"] == "lost"]
    nodec = [r for r in in_win if r["outcome"] == "no-decision"]
    rate = C.pct(len(won), len(won) + len(lost))
    rate_nd = C.pct(len(won), len(won) + len(lost) + len(nodec))  # ND-as-losses sensitivity
    won_val = sum(int(r["value_usd"]) for r in won)
    lost_val = sum(int(r["value_usd"]) for r in lost)
    val_rate = C.pct(won_val, won_val + lost_val)
    val_note = ("we lose bigger deals than we win" if val_rate < rate else
                "we win bigger deals than we lose" if val_rate > rate else
                "the value mix mirrors the count mix")

    reasons = {}
    for r in lost:
        reasons[r["primary_reason"]] = reasons.get(r["primary_reason"], 0) + 1
    ranked = sorted(reasons.items(), key=lambda kv: (-kv[1], kv[0]))

    pm = [r for r in lost if r["primary_reason"] == "predictive-monitoring-gap"
          or r["cites_predictive_monitoring"] == "yes"]
    pm_primary = [r for r in lost if r["primary_reason"] == "predictive-monitoring-gap"]
    pm_share = C.pct(len(pm), len(lost))
    pm_value = sum(int(r["value_usd"]) for r in pm)
    win_reasons = {}
    for r in won:
        win_reasons[r["primary_reason"]] = win_reasons.get(r["primary_reason"], 0) + 1
    win_ranked = sorted(win_reasons.items(), key=lambda kv: (-kv[1], kv[0]))

    target = 50.0  # E-08.1 expected floor (config expectation, cited [config: commercial.yml])
    headline = (f"Trailing-365d win rate is {rate}% of decided opportunities "
                f"({len(won)} won / {len(lost)} lost; {len(nodec)} no-decision excluded) vs the "
                f"{target:.0f}% stand-in target; dollar-weighted we win {val_rate}% of decided CRM "
                f"value (${won_val:,} won vs ${lost_val:,} lost — {val_note}); {len(pm)} of "
                f"{len(lost)} losses ({pm_share}%) have the predictive-monitoring gap primary or "
                f"cited — ${pm_value:,} in CRM value")

    # expectations
    exp_results = {
        "E-08.1": (f"{rate}% of decided ({len(won)}W/{len(lost)}L, window {start} → {anchor}); "
                   f"sensitivity: {rate_nd}% if the {len(nodec)} no-decisions count as losses — "
                   f"the verdict is denominator-sensitive, not just sample-sensitive",
                   "met" if rate >= target else ("at-risk" if rate >= target - 2 else "not-met"),
                   ["derived: win-rate", f"src: {src}"]),
    }
    exps = C.evaluate_expectations("BQ-08", exp_results)

    # narrative — deterministic from computed facts
    narrative = {"issues": [], "risks": [], "watch": []}
    if rate < target:
        narrative["issues"].append({
            "id": "I1", "severity": "high",
            "statement": f"Win rate {rate}% is below the {target:.0f}% stand-in target",
            "action": "Review the top loss reasons with sales leadership; confirm the target "
                      "itself against a plan of record (it is an unvalidated stand-in)",
            "evidence": ["derived: win-rate", "config: commercial.yml"]})
    elif rate < target + 2:
        narrative["watch"].append({
            "id": f"W{len(narrative['watch']) + 1}",
            "statement": f"Win rate {rate}% clears the {target:.0f}% target by under two points — "
                         f"a handful of deals swings the verdict, and so does the denominator "
                         f"choice: with the {len(nodec)} no-decisions counted as losses the rate "
                         f"is {rate_nd}%, below the target",
            "evidence": ["derived: win-rate", "config: commercial.yml"]})
    narrative["watch"].append({
        "id": f"W{len(narrative['watch']) + 1}",
        "statement": f"Dollar-weighted win rate is {val_rate}% of decided CRM value "
                     f"(${won_val:,} won vs ${lost_val:,} lost) vs {rate}% by count — {val_note}; "
                     "read the count-based headline next to the value-based one",
        "evidence": ["derived: value-win-rate", f"src: {src}"]})
    narrative["risks"].append({
        "id": "R1", "severity": "high",
        "statement": f"Predictive-monitoring gap touches {pm_share}% of in-window losses "
                     f"({len(pm)} deals, ${pm_value:,} CRM value; primary reason in "
                     f"{len(pm_primary)} of them) — the largest addressable feature-driven loss pool",
        "mitigation": "Feed this value into the predictive-monitoring investment case (Y3 roadmap "
                      "bet); equip sales with the roadmap position for deals where the gap is cited "
                      "but not primary",
        "evidence": ["derived: pm-gap-losses", f"src: {src}"]})
    if ranked:
        top_reason, top_n = ranked[0]
        narrative["watch"].append({
            "id": f"W{len(narrative['watch']) + 1}",
            "statement": f"Top loss reason in the window is {top_reason} ({top_n} of {len(lost)} "
                         "losses) — competitive-selling coaching target",
            "evidence": ["derived: loss-reasons", f"src: {src}"]})
    narrative["risks"].append({
        "id": "R2", "severity": "medium",
        "statement": "Loss attribution is the CRM's single primary_reason per opportunity — a "
                     "recorded citation is not proof the gap decided the deal",
        "mitigation": "Treat reason mix as directional; validate the big-ticket PM-gap losses with "
                      "deal debriefs before funding decisions ride on them",
        "evidence": [f"src: {src}"]})

    lines = [
        "# BQ-08 — What we win and lose on (trailing 365 days)", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [config: commercial.yml]", "",
        f"## Decided outcomes in the window ({start} → {anchor})", "",
        f"_Window: trailing {window} days anchored at the newest close_date in the pinned snapshot;"
        f" decided = won + lost; no-decision reported separately, per plans/BQ-08.md"
        f" [config: commercial.yml]._", "",
        f"- Win rate: {rate}% ({len(won)} won / {len(lost)} lost) [derived: win-rate] [src: {src}]",
        f"- Dollar-weighted: we win {val_rate}% of decided CRM value (${won_val:,} won vs "
        f"${lost_val:,} lost — {val_note}) [derived: value-win-rate] [src: {src}]",
        f"- No-decision outcomes excluded from the denominator: {len(nodec)} [src: {src}]; counted "
        f"as losses the win rate would be {rate_nd}% [derived: win-rate] [src: {src}]",
        "",
        "## Loss reasons (primary, in-window)", "",
        "| Primary reason | Losses | % of losses |",
        "|---|---|---|",
    ]
    for reason, n in ranked:
        lines.append(f"| {reason} [src: {src}] | {n} | {C.pct(n, len(lost))}% |")
    lines += [
        "",
        "## The predictive-monitoring gap in losses", "",
        f"- Primary OR cited: {len(pm)} of {len(lost)} in-window losses ({pm_share}%) "
        f"[derived: pm-gap-losses] [src: {src}]",
        f"- Primary reason only: {len(pm_primary)} losses [derived: pm-gap-losses] [src: {src}]",
        f"- CRM opportunity value of those losses: ${pm_value:,} (recorded value, not "
        f"win-probability-weighted) [derived: pm-gap-losses] [src: {src}]",
        "",
        "## What we win on (primary reason of in-window wins)", "",
        "| Primary reason | Wins |",
        "|---|---|",
    ]
    for reason, n in win_ranked:
        lines.append(f"| {reason} [src: {src}] | {n} |")
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- All counts measured from [src: {src}] (demo-fabricated CRM log; real competitor names",
        "  inside fabricated records).",
        f"- Monthly won/lost/PM-gap-loss history charted across the full snapshot span, zero-filled "
        f"[derived: monthly-outcomes] [src: {src}].",
        "- The win-rate target is a stand-in expectation, not a documented sales-plan number",
        "  [config: commercial.yml].",
    ]

    months = month_range(min(r["close_date"] for r in rows)[:7], anchor[:7])
    def mline(label, pred):
        by_m = {}
        for r in rows:
            if pred(r):
                by_m[r["close_date"][:7]] = by_m.get(r["close_date"][:7], 0) + 1
        return {"label": label, "points": [{"x": m + "-01", "y": by_m.get(m, 0)} for m in months]}

    trend = [
        mline("won", lambda r: r["outcome"] == "won"),
        mline("lost", lambda r: r["outcome"] == "lost"),
        mline("lost citing PM gap", lambda r: r["outcome"] == "lost" and (
            r["primary_reason"] == "predictive-monitoring-gap" or r["cites_predictive_monitoring"] == "yes")),
    ]

    data = {
        "bq": "BQ-08",
        "series": [
            {"id": "win-rate", "label": "Trailing-365d win rate", "unit": "%",
             "kind": "stat", "evidence_class": "measured",
             "provenance": {"dataset": WINLOSS_DS, "snapshot": snap},
             "points": [{"label": f"of decided opportunities, {start} → {anchor}", "value": rate}]},
            {"id": "value-win-rate", "label": "Trailing-365d dollar-weighted win rate", "unit": "%",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "Σ value_usd over in-window wins ÷ Σ value_usd over "
                                      "in-window decided (won + lost)",
                            "inputs": [f"src: {src}"]},
             "provenance": {"dataset": WINLOSS_DS, "snapshot": snap},
             "points": [{"label": f"of decided CRM value, {start} → {anchor}", "value": val_rate},
                        {"label": "CRM value won (USD)", "value": won_val},
                        {"label": "CRM value lost (USD)", "value": lost_val}]},
            {"id": "pm-gap-losses", "label": "Predictive-monitoring-gap losses (in-window)",
             "unit": "", "kind": "stat", "evidence_class": "measured",
             "provenance": {"dataset": WINLOSS_DS, "snapshot": snap},
             "points": [{"label": "losses with PM gap primary or cited", "value": len(pm)},
                        {"label": "% of in-window losses", "value": pm_share},
                        {"label": "CRM value at loss (USD)", "value": pm_value}]},
            {"id": "loss-reasons", "label": "In-window losses by primary reason", "unit": "losses",
             "evidence_class": "measured",
             "provenance": {"dataset": WINLOSS_DS, "snapshot": snap},
             "points": [{"label": reason, "value": n} for reason, n in ranked]},
            {"id": "win-reasons", "label": "In-window wins by primary reason", "unit": "wins",
             "evidence_class": "measured",
             "provenance": {"dataset": WINLOSS_DS, "snapshot": snap},
             "points": [{"label": reason, "value": n} for reason, n in win_ranked]},
            {"id": "monthly-outcomes", "label": "Monthly decided outcomes (full snapshot span)",
             "unit": "opportunities/month", "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": WINLOSS_DS, "snapshot": snap},
             "lines": trend, "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "measured"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
