"""BQ-15 — SOTA currency: is the EU MDR state-of-the-art analysis still current, and
are the headline differentiators still ahead?

Contract: run(corpus_root, out, pins) — see plans/BQ-15.md. The SOTA document is the
config-referenced object under assessment; it is NOT parsed — all evidence comes from
the pinned corpus snapshots. Deterministic refresh rule committed in the plan.
"""

import datetime as dt

import computations as C
from bq_modules.bq_13 import add_months
from bq_modules.bq_14 import parse_numeric

FEAT_DS = "commercial/external-competitor-features"
FDA_DS = "commercial/openfda-510k-infusion"


def run(corpus_root, out, pins):
    p = C.params_for("BQ-15")
    feats, fsnap = C.load_pin_csv(corpus_root, pins, FEAT_DS)
    rows510, snap510 = C.load_pin_csv(corpus_root, pins, FDA_DS)
    srcf = f"{FEAT_DS}@{fsnap}"
    src510 = f"{FDA_DS}@{snap510}"
    diffs = p["differentiators"]
    sota_date = p["sota_doc_date"]

    # --- differentiator comparison (direction per attribute; range = competitor-favorable end)
    def compare(attr, our_val, direction):
        comps = [r for r in feats if r["attribute"] == attr and r["vendor"] != "GlobalLogic"]
        vals = []
        for r in comps:
            v = parse_numeric(r["value"], direction)
            if v is not None:
                vals.append({"label": f"{r['vendor']} {r['product']}", "value": v,
                             "raw": r["value"], "verified": r["verified"]})
        if direction == "lower":
            best = min(vals, key=lambda x: x["value"]) if vals else None
            ahead = all(our_val < v["value"] for v in vals) if vals else None
        else:
            best = max(vals, key=lambda x: x["value"]) if vals else None
            ahead = all(our_val > v["value"] for v in vals) if vals else None
        n_verified = sum(1 for v in vals if v["verified"].strip().lower() == "yes")
        return vals, best, ahead, n_verified

    acc_vals, acc_best, acc_ahead, acc_ver = compare("flow_accuracy_pct", diffs["flow_accuracy_pct"], "lower")
    bat_vals, bat_best, bat_ahead, bat_ver = compare("battery_hours", diffs["battery_hours"], "higher")
    acc_margin = round(acc_best["value"] / diffs["flow_accuracy_pct"], 1) if acc_best else None
    bat_margin = round(diffs["battery_hours"] / bat_best["value"], 1) if bat_best else None
    # RT-15.1 basis disclosure: 0.35 is our LAB-standard spec; competitor cells are
    # nominal/field specs — also compute the margin on our volumetric-basis spec
    acc_vol = p["flow_accuracy_pct_volumetric"]
    acc_margin_vol = round(acc_best["value"] / acc_vol, 1) if acc_best else None
    acc_ahead_vol = all(acc_vol < v["value"] for v in acc_vals) if acc_vals else None

    # products in the matrix with NO value for a compared attribute (stated coverage gap)
    products = sorted({(r["vendor"], r["product"]) for r in feats if r["vendor"] != "GlobalLogic"})
    def missing(attr):
        have = {(r["vendor"], r["product"]) for r in feats if r["attribute"] == attr}
        return [f"{v} {pr}" for v, pr in products if (v, pr) not in have]
    acc_missing, bat_missing = missing("flow_accuracy_pct"), missing("battery_hours")

    # --- predictive premise (refresh trigger b)
    pred_yes = [r for r in feats if r["attribute"] == "predictive_monitoring"
                and r["value"].strip().lower().startswith("yes")]

    # --- clearance currency signal
    anchor = max(r["decision_date"] for r in rows510 if r["decision_date"])
    since_doc = [r for r in rows510 if r["decision_date"] and r["decision_date"] > sota_date]
    ctx_start = (dt.date.fromisoformat(anchor) - dt.timedelta(days=int(p["trailing_context_days"]))).isoformat()
    ctx = [r for r in rows510 if r["decision_date"] and ctx_start <= r["decision_date"] <= anchor]

    # --- deterministic refresh rule (plan-committed; calendar months, not 30-day months)
    acq_date = dt.date.fromisoformat(snap510.split(".")[0])
    doc_age_days = (acq_date - dt.date.fromisoformat(sota_date)).days
    next_review = add_months(dt.date.fromisoformat(sota_date), int(p["review_cadence_months"]))
    reasons = []
    if acc_ahead is False or bat_ahead is False or acc_ahead_vol is False:
        reasons.append("a differentiator margin is eroded")
    if pred_yes:
        reasons.append("a competitor documents shipping predictive monitoring")
    if acq_date > next_review:
        reasons.append("the SOTA doc has passed its review cadence")

    if reasons:
        verdict_txt = "formal refresh WARRANTED now — " + "; ".join(reasons)
    else:
        verdict_txt = (f"ride to scheduled review ({next_review.isoformat()}): both differentiators "
                       f"remain ahead of every documented competitor value and no refresh trigger fired")
    headline = (f"{verdict_txt}. Accuracy margin ~{acc_margin}x vs best documented competitor on our "
                f"LAB-basis spec (~{acc_margin_vol}x on our volumetric-basis spec — ahead on either "
                f"basis; competitor cells are nominal/field specs), battery "
                f"~{bat_margin}x; {len(since_doc)} FRN clearance(s) observed after the SOTA anchor date "
                f"({sota_date}) in a snapshot whose coverage ends {anchor}")

    # --- history: clearances per quarter (context for the currency signal)
    def qk(d):
        return f"{d[:4]}-Q{(int(d[5:7]) - 1) // 3 + 1}"
    dated = [r for r in rows510 if r["decision_date"]]
    qs = sorted({qk(r["decision_date"]) for r in dated})
    def q_iter(first, last):
        y, q = int(first[:4]), int(first[-1])
        while f"{y}-Q{q}" <= last:
            yield f"{y}-Q{q}"
            q += 1
            if q == 5:
                y, q = y + 1, 1
    qsm = {1: "01", 2: "04", 3: "07", 4: "10"}
    counts = {}
    for r in dated:
        counts[qk(r["decision_date"])] = counts.get(qk(r["decision_date"]), 0) + 1
    ts = [{"x": f"{q[:4]}-{qsm[int(q[-1])]}-01", "y": counts.get(q, 0)}
          for q in q_iter(qs[0], qs[-1])]

    lines = [
        "# BQ-15 — SOTA currency: differentiators + refresh verdict", "",
        f"**Verdict**: {headline} [derived: v-refresh] [src: {srcf}] [src: {src510}] "
        f"[config: commercial.yml]", "",
        "## Headline differentiators vs every documented competitor value", "",
        f"_Our values are the config constants matching the SOTA doc's headline claims "
        f"[config: commercial.yml]; the SOTA doc itself "
        f"([config: {p['sota_doc']}]) is referenced, not parsed._", "",
        f"### Flow accuracy (± pct, lower is better) — ours {diffs['flow_accuracy_pct']} "
        f"[config: commercial.yml]", "",
        "| Competitor product | Value | Verified |",
        "|---|---|---|",
    ]
    for v in acc_vals:
        lines.append(f"| {v['label']} [src: {srcf}] | {v['raw']} | {v['verified']} |")
    lines += [
        "",
        f"- {'Ahead of' if acc_ahead else 'NOT ahead of'} all {len(acc_vals)} documented values "
        f"({acc_ver} verified); margin vs best ({acc_best['label']}) ~{acc_margin}x "
        f"[derived: differentiator-margins] [src: {srcf}].",
        f"- Spec-basis disclosure: our {diffs['flow_accuracy_pct']} is the LABORATORY-standard spec, "
        f"while competitor cells are nominal/field specs — a basis-mixed comparison. On our "
        f"volumetric-basis spec ({acc_vol}) the margin is ~{acc_margin_vol}x, and we are "
        f"{'still ahead of' if acc_ahead_vol else 'NOT ahead of'} every documented value — 'ahead' "
        f"survives either basis; the headline multiple is basis-sensitive "
        f"[derived: differentiator-margins] [config: commercial.yml] [src: {srcf}].",
        f"- No documented accuracy value for: {', '.join(acc_missing) if acc_missing else 'none'} "
        f"[src: {srcf}] — the comparison covers only documented cells; superiority over undocumented "
        f"specs is NOT claimed.",
        "",
        f"### Battery (hours, higher is better) — ours {diffs['battery_hours']} "
        f"[config: commercial.yml]", "",
        "| Competitor product | Value | Verified |",
        "|---|---|---|",
    ]
    for v in bat_vals:
        lines.append(f"| {v['label']} [src: {srcf}] | {v['raw']} | {v['verified']} |")
    lines += [
        "",
        f"- {'Ahead of' if bat_ahead else 'NOT ahead of'} all {len(bat_vals)} documented values "
        f"({bat_ver} verified); margin vs best ({bat_best['label']}) ~{bat_margin}x "
        f"[derived: differentiator-margins] [src: {srcf}].",
        f"- No documented battery value for: {', '.join(bat_missing) if bat_missing else 'none'} "
        f"[src: {srcf}].",
        "",
        "## Clearance activity since the SOTA anchor (the currency signal)", "",
        f"- {len(since_doc)} FRN clearance(s) with a decision date after the SOTA anchor "
        f"({sota_date}) [derived: since-doc-count] [src: {src510}] [config: commercial.yml].",
        f"- Publication-lag caveat: the pinned snapshot's coverage ends at its newest decision date "
        f"({anchor}) — a clearance decided after that date is invisible here, so a zero is "
        f"lag-limited, not proof of quiet [src: {src510}].",
        f"- Context: {len(ctx)} clearances in the trailing window {ctx_start} → {anchor} "
        f"[derived: trailing-context] [src: {src510}] [config: commercial.yml] — the segment is "
        f"active; currency erodes by cadence, not by event only.",
        "",
        "## Refresh verdict (deterministic rule, plan-committed)", "",
        f"- Rule: refresh now if a margin erodes, a predictive_monitoring row turns `yes`, or the "
        f"doc exceeds its {p['review_cadence_months']}-month review cadence [config: commercial.yml].",
        f"- Trigger check — margins: accuracy {'ahead' if acc_ahead else 'ERODED'} (lab basis) / "
        f"{'ahead' if acc_ahead_vol else 'ERODED'} (volumetric basis), battery "
        f"{'ahead' if bat_ahead else 'ERODED'} [derived: differentiator-margins]; "
        f"predictive_monitoring rows reading `yes`: {len(pred_yes)} [src: {srcf}]; doc age at "
        f"snapshot acquisition {doc_age_days} days vs cadence [derived: v-refresh] "
        f"[config: commercial.yml].",
        f"- Next scheduled review {next_review.isoformat()} (anchor + {p['review_cadence_months']} "
        f"calendar months) [derived: v-refresh] [config: commercial.yml].",
        f"- The cadence is a config stand-in for the QMS SOTA/PMS review cadence, not a documented "
        f"EU MDR obligation — challengeable [config: commercial.yml]. The anchor is the doc's "
        f"ADOPTION date; if the underlying analysis was authored earlier, currency is overstated "
        f"[config: commercial.yml].",
    ]

    narrative = {"issues": [], "risks": [], "watch": []}
    narrative["risks"].append({
        "id": "R1", "severity": "medium",
        "statement": f"The currency signal is lag-limited: the 510(k) snapshot's coverage ends "
                     f"{anchor}, months before the snapshot's acquisition — a recent clearance may "
                     f"already exist unseen",
        "mitigation": "Refresh the 510(k) dataset on its 90-day cadence and re-answer; treat a "
                      "quiet window as unproven, not proven",
        "evidence": [f"src: {src510}", "derived: since-doc-count"],
    })
    narrative["watch"].append({
        "id": "W1",
        "statement": f"Accuracy comparison rests on {len(acc_vals)} documented cells and battery on "
                     f"{len(bat_vals)} — several competitor products carry no value for these "
                     f"attributes, and undocumented is not beaten",
        "evidence": [f"src: {srcf}", "derived: differentiator-margins"],
    })
    narrative["watch"].append({
        "id": "W2",
        "statement": "Scope: product code FRN only — a SOTA-relevant clearance outside FRN (e.g. a "
                     "monitoring SaMD) is invisible to this currency signal; widen the corpus before "
                     "treating the signal as complete",
        "evidence": [f"src: {src510}"],
    })

    lines += C.expectations_section(C.evaluate_expectations("BQ-15", {}))
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Competitor values measured from the curated matrix [src: {srcf}] (ranges scored at the "
        f"competitor-favorable end); our constants from [config: commercial.yml].",
        f"- Clearance counts measured from [src: {src510}]; refresh rule and cadence from "
        f"[config: commercial.yml].",
        "- Historical view: quarterly FRN clearance counts are charted "
        f"[derived: clearances-by-quarter] [src: {src510}].",
    ]

    data = {
        "bq": "BQ-15",
        "series": [
            {"id": "differentiator-margins", "label": "Differentiator margin vs best documented competitor",
             "unit": "x", "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "accuracy: best competitor value / ours, on both our lab-basis and volumetric-basis specs (lower is better; competitor cells are nominal/field specs — basis stated); battery: ours / best competitor value (higher is better)",
                            "inputs": [f"src: {srcf}", "config: commercial.yml"]},
             "provenance": {"dataset": FEAT_DS, "snapshot": fsnap},
             "points": [{"label": "flow-accuracy advantage vs best documented competitor (our lab-basis spec)",
                         "value": acc_margin},
                        {"label": "flow-accuracy advantage on our volumetric-basis spec",
                         "value": acc_margin_vol},
                        {"label": "battery advantage vs best documented competitor", "value": bat_margin}]},
            {"id": "accuracy-by-product", "label": "Flow accuracy (± pct) by product", "unit": "± pct",
             "evidence_class": "measured",
             "provenance": {"dataset": FEAT_DS, "snapshot": fsnap},
             "points": [{"label": "GlobalLogic PainEase PCA Advanced (PP3500)",
                         "value": diffs["flow_accuracy_pct"]}]
                       + [{"label": v["label"], "value": v["value"]} for v in acc_vals]},
            {"id": "battery-by-product", "label": "Battery (hours) by product", "unit": "hours",
             "evidence_class": "measured",
             "provenance": {"dataset": FEAT_DS, "snapshot": fsnap},
             "points": [{"label": "GlobalLogic PainEase PCA Advanced (PP3500)",
                         "value": diffs["battery_hours"]}]
                       + [{"label": v["label"], "value": v["value"]} for v in bat_vals]},
            {"id": "since-doc-count", "label": "FRN clearances after the SOTA anchor date", "unit": "clearances",
             "evidence_class": "derived",
             "derivation": {"method": "count of pinned FRN records with decision_date > sota_doc_date",
                            "inputs": [f"src: {src510}", "config: commercial.yml"]},
             "provenance": {"dataset": FDA_DS, "snapshot": snap510},
             "points": [{"label": f"decisions after {sota_date} (coverage ends {anchor})",
                         "value": len(since_doc)}]},
            {"id": "trailing-context", "label": "FRN clearances, trailing 12 months of the pin",
             "unit": "clearances", "evidence_class": "derived",
             "derivation": {"method": "count of pinned FRN records in the trailing_context_days window ending at the snapshot's newest decision date",
                            "inputs": [f"src: {src510}", "config: commercial.yml"]},
             "provenance": {"dataset": FDA_DS, "snapshot": snap510},
             "points": [{"label": f"{ctx_start} → {anchor}", "value": len(ctx)}]},
            {"id": "clearances-by-quarter", "label": "FRN clearances per quarter", "unit": "clearances",
             "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": FDA_DS, "snapshot": snap510},
             "lines": [{"label": "FRN clearances", "points": ts}], "points": []},
        ],
        "verdicts": [{"id": "v-refresh", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": C.evaluate_expectations("BQ-15", {}),
    }
    C.write(out, lines, data)
