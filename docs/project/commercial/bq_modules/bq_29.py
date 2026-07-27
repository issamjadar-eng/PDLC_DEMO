"""BQ-29 — Cloud Suite attach-rate stage-gate (the $24M release gate).

Deterministic per the BQ-29 analysis plan: attach = pumps under an ACTIVE subscription
(internal-subscriptions) ÷ PP3500 installed base (internal-fleet). Churned counts zero.
The gate number itself is a stand-in — commercial-strategy.md gates the spend on
"traction" with no number — and the report says so plainly.
"""

import computations as C

SUBS_DS = "commercial/internal-subscriptions"
FLEET_DS = "commercial/internal-fleet"


def run(corpus_root, out, pins):
    p = C.params_for("BQ-29")
    gate = float(p["gate_attach_pct"])
    spend_m = round(int(p["gated_spend_usd"]) / 1e6)
    subs, ssnap = C.load_pin_csv(corpus_root, pins, SUBS_DS)
    fleet, fsnap = C.load_pin_csv(corpus_root, pins, FLEET_DS)
    ssrc, fsrc = f"{SUBS_DS}@{ssnap}", f"{FLEET_DS}@{fsnap}"

    pp = [r for r in fleet if r["model"] == "PP3500"]
    site_region = {r["site_id"]: r["region"] for r in fleet}
    active = [r for r in subs if r["status"] == "active"]
    churned_sites = sorted({r["site_id"] for r in subs if r["status"] == "churned"})
    attached = sum(int(r["pumps_connected"]) for r in active)
    attach_pct = C.pct(attached, len(pp))
    gate_met = attach_pct >= gate
    margin = round(attach_pct - gate, 1)

    # Denominator sensitivity (red-team finding F29-1): the whole-PCA installed base
    # (PP3500 + PP3000) is the one reasonable alternative denominator — Cloud Suite
    # rides on the PCA installed base — and it can move the reading across the gate.
    pp3000 = [r for r in fleet if r["model"] == "PP3000"]
    pca_base = len(pp) + len(pp3000)
    pp3000_conn = sum(1 for r in pp3000 if r["connected"] == "yes")
    attach_pca_pct = C.pct(attached, pca_base)
    pca_gate_met = attach_pca_pct >= gate

    active_sites = {r["site_id"] for r in active}
    conn_pp = [r for r in pp if r["connected"] == "yes"]
    gap_rows = [r for r in conn_pp if r["site_id"] not in active_sites]
    gap_by_site = {}
    for r in gap_rows:
        gap_by_site[r["site_id"]] = gap_by_site.get(r["site_id"], 0) + 1
    gap_sites = sorted(gap_by_site.items(), key=lambda kv: (-kv[1], kv[0]))
    not_connected = len(pp) - len(conn_pp)

    regions = sorted({r["region"] for r in pp})
    reg_pts = []
    for reg in regions:
        denom = sum(1 for r in pp if r["region"] == reg)
        num = sum(int(r["pumps_connected"]) for r in active
                  if site_region.get(r["site_id"]) == reg)
        reg_pts.append({"label": reg, "value": C.pct(num, denom),
                        "attached": num, "installed": denom})

    # history: cumulative pumps under currently-active subscriptions by start month
    months = sorted({r["start_date"][:7] for r in active})
    span = []
    if months:
        y, m = map(int, months[0].split("-"))
        ye, me = map(int, max(months).split("-"))
        while (y, m) <= (ye, me):
            span.append(f"{y:04d}-{m:02d}")
            m += 1
            if m == 13:
                y, m = y + 1, 1
    run_total, hist_pts = 0, []
    adds = {}
    for r in active:
        adds[r["start_date"][:7]] = adds.get(r["start_date"][:7], 0) + int(r["pumps_connected"])
    for mo in span:
        run_total += adds.get(mo, 0)
        hist_pts.append({"x": mo + "-01", "y": run_total})

    verdict_word = "HOLDS" if gate_met else "IS NOT HOLDING"
    headline = (f"The attach stage-gate {verdict_word} at the stand-in level: {attach_pct}% of the "
                f"PP3500 installed base ({attached} of {len(pp)} pumps) vs the {gate:.0f}% gate — "
                f"but the ${spend_m}M releases on a gate NUMBER nobody has ratified; the strategy "
                f"of record says 'traction' and sets no threshold — and the verdict is "
                f"denominator-definition-sensitive: under a whole-PCA denominator "
                f"({pca_base} pumps incl. {len(pp3000)} unconnectable PP3000) attach reads "
                f"{attach_pca_pct}%, {'above' if pca_gate_met else 'BELOW'} the stand-in gate; "
                f"the metric definition is as unratified as the gate number")

    # narrative — deterministic from computed facts
    narrative = {"issues": [], "risks": [], "watch": []}
    narrative["risks"].append({
        "id": "R1", "severity": "high",
        "statement": f"The ${spend_m}M release decision references a gate with no number of "
                     f"record — the {gate:.0f}% is a stand-in, and at {attach_pct}% attach the "
                     f"reading sits {margin} points from it; any ratified threshold in that "
                     "neighborhood flips the verdict — and the metric DEFINITION is equally "
                     f"unratified: the whole-PCA denominator reads {attach_pca_pct}%, "
                     f"{'above' if pca_gate_met else 'below'} the gate, so the denominator "
                     "choice alone spans the gate",
        "mitigation": "Have the board/CFO ratify a numeric gate AND the metric definition "
                      "(denominator basis) in the commercial strategy or plan of record and "
                      "mark E-29.1 validated before the spend decision",
        "evidence": ["derived: attach-stat", "derived: denominator-sensitivity",
                     "config: commercial.yml"],
    })
    if not gate_met:
        narrative["issues"].append({
            "id": "I1", "severity": "high",
            "statement": f"Attach at {attach_pct}% is below the {gate:.0f}% stand-in gate",
            "action": "Hold the gated spend pending the ratified-threshold conversation; direct "
                      "commercial effort at the connected-but-unsubscribed sites",
            "evidence": ["derived: attach-stat", "config: commercial.yml"],
        })
    narrative["watch"].append({
        "id": "W1",
        "statement": f"Go-get gap: {len(gap_rows)} connected-but-unsubscribed pumps across "
                     f"{len(gap_sites)} sites (" + ", ".join(s for s, _ in gap_sites) + ") — "
                     f"{len(churned_sites)} of those sites are churn-losses "
                     f"(" + ", ".join(churned_sites) + "), the rest never subscribed; this is the "
                     "nearest-term attach growth and winback territory",
        "evidence": ["derived: gap-sites", f"src: {ssrc}", f"src: {fsrc}"],
    })
    narrative["watch"].append({
        "id": "W2",
        "statement": f"{not_connected} of {len(pp)} PP3500 pumps are not connected at all — attach "
                     "beyond the connected base runs through the connectivity/adapter path (the "
                     "BQ-30 business case), not sales motion alone",
        "evidence": ["derived: attach-breakdown", f"src: {fsrc}"],
    })

    exp_results = {
        "E-29.1": (f"{attach_pct}% attach vs the {gate:.0f}% stand-in ({margin:+.1f} points); "
                   "no gate number is ratified in the strategy of record; "
                   f"denominator-sensitive — the whole-PCA basis reads {attach_pca_pct}%, "
                   f"{'above' if pca_gate_met else 'below'} the gate",
                   "met" if gate_met else "not-met",
                   ["derived: attach-stat", "derived: denominator-sensitivity"]),
    }
    exps = C.evaluate_expectations("BQ-29", exp_results)

    lines = [
        "# BQ-29 — Cloud Suite attach-rate stage-gate", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {ssrc}] [src: {fsrc}] "
        f"[config: commercial.yml]", "",
        "## The gate reading", "",
        f"- Attach = pumps under an ACTIVE subscription ÷ PP3500 installed base: {attached} ÷ "
        f"{len(pp)} = {attach_pct}% [derived: attach-stat] [src: {ssrc}] [src: {fsrc}]",
        f"- Gate level: {gate:.0f}% releases the ${spend_m}M predictive-monitoring spend "
        f"[config: commercial.yml] — a numeric stand-in; commercial-strategy.md conditions the "
        f"spend on 'Y1/Y2 Cloud Suite traction' and sets NO number [config: commercial.yml]",
        f"- Churned subscriptions count zero: {len(churned_sites)} churned sites are in the gap "
        f"pool, not the numerator [src: {ssrc}]",
        "",
        "## Denominator sensitivity (disclosed, not absorbed)", "",
        "_The gate metric's denominator is a definition choice no one has ratified — with the "
        "gate number itself a stand-in, the metric definition is equally unratified, so the "
        "reading is shown under both bases [derived: denominator-sensitivity]._", "",
        f"| Basis | Attached | Denominator | Attach % | vs the {gate:.0f}% stand-in gate |",
        "|---|---|---|---|---|",
        f"| PP3500 installed base (primary) [derived: denominator-sensitivity] [src: {fsrc}] | "
        f"{attached} | {len(pp)} | {attach_pct}% | {'holds' if gate_met else 'BELOW'} |",
        f"| Whole PCA installed base (PP3500 + PP3000) [derived: denominator-sensitivity] "
        f"[src: {fsrc}] | {attached} | {pca_base} | {attach_pca_pct}% | "
        f"{'holds' if pca_gate_met else 'BELOW'} |",
        "",
        f"- Basis defense: the primary excludes PP3000 because {pp3000_conn} of {len(pp3000)} "
        f"PP3000 devices are connected and no PP3000 adapter path exists in the corpus — Cloud "
        f"Suite sells on the PP3500 base [src: {fsrc}]. The denominator choice alone moves the "
        f"reading across the gate ({attach_pct}% vs {attach_pca_pct}%): ratify the metric "
        f"definition together with the gate number [derived: denominator-sensitivity] "
        f"[config: commercial.yml].",
        "",
        "## Where the rest of the base sits", "",
        "| Segment | PP3500 pumps | Share of installed base |",
        "|---|---|---|",
        f"| Under active subscription [derived: attach-breakdown] [src: {ssrc}] | {attached} | "
        f"{attach_pct}% |",
        f"| Connected, no active subscription (go-get) [derived: attach-breakdown] [src: {fsrc}] | "
        f"{len(gap_rows)} | {C.pct(len(gap_rows), len(pp))}% |",
        f"| Not connected [derived: attach-breakdown] [src: {fsrc}] | {not_connected} | "
        f"{C.pct(not_connected, len(pp))}% |",
        "",
        "## Attach by region", "",
        "| Region | Attached pumps | PP3500 installed | Attach % |",
        "|---|---|---|---|",
    ]
    for q in reg_pts:
        lines.append(f"| {q['label']} [derived: attach-by-region] [src: {ssrc}] [src: {fsrc}] | "
                     f"{q['attached']} | {q['installed']} | {q['value']}% |")
    lines += [
        "",
        "## Go-get gap by site", "",
        "| Site | Connected, unsubscribed pumps | History |",
        "|---|---|---|",
    ]
    for s, n in gap_sites:
        hist = "churned subscription" if s in churned_sites else "never subscribed"
        lines.append(f"| {s} [derived: gap-sites] [src: {fsrc}] | {n} | {hist} |")
    lines += [
        "",
        f"- Cumulative pumps under currently-active subscriptions are charted by start month "
        f"[derived: cumulative-attach] [src: {ssrc}]; a true attach-% history needs historical "
        f"fleet snapshots and churn end-dates — published as unavailable, not faked "
        f"[derived: attach-history].",
    ]
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Numerator summed from active rows of [src: {ssrc}]; denominator is the PP3500 count in "
        f"[src: {fsrc}] — the project's installed-base registry. PP3000 is excluded from the "
        f"primary basis (zero connected devices; Cloud Suite sells on the PP3500 base), and the "
        f"whole-PCA alternative is printed in the denominator-sensitivity section rather than "
        f"absorbed [src: {fsrc}] [derived: denominator-sensitivity].",
        f"- Gate level and gated spend are declared constants [config: commercial.yml]; the gate's "
        "lack of a ratified number — and of a ratified metric definition — is the report's "
        "central caveat, stated in the verdict.",
    ]

    data = {
        "bq": "BQ-29",
        "series": [
            {"id": "attach-stat", "label": "Cloud Suite attach", "unit": "%",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "sum(pumps_connected) over active subscription rows ÷ count of PP3500 devices in the fleet registry",
                            "inputs": [f"src: {ssrc}", f"src: {fsrc}"]},
             "provenance": {"dataset": SUBS_DS, "snapshot": ssnap},
             "points": [{"label": "of PP3500 installed base under active subscription",
                         "value": attach_pct,
                         "sub": f"{attached} of {len(pp)} pumps; gate {gate:.0f}% (stand-in)"}]},
            {"id": "denominator-sensitivity", "label": "Attach % under alternative denominator bases",
             "unit": "%", "evidence_class": "derived",
             "derivation": {"method": "attached = sum(pumps_connected) over active subscription rows; attach % computed under two denominator bases from the fleet registry: PP3500-only count (primary) vs whole-PCA count (PP3500 + PP3000)",
                            "inputs": [f"src: {ssrc}", f"src: {fsrc}"]},
             "provenance": {"dataset": FLEET_DS, "snapshot": fsnap},
             "points": [{"label": "PP3500 installed base (primary)", "value": attach_pct,
                         "denominator": len(pp)},
                        {"label": "whole PCA installed base (PP3500 + PP3000)",
                         "value": attach_pca_pct, "denominator": pca_base,
                         "pp3000_connected": pp3000_conn}]},
            {"id": "cumulative-attach", "label": "Pumps under currently-active subscriptions",
             "unit": "pumps", "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": SUBS_DS, "snapshot": ssnap},
             "lines": [{"label": "cumulative by start month", "points": hist_pts}], "points": []},
            {"id": "attach-breakdown", "label": "PP3500 base by subscription segment", "unit": "pumps",
             "evidence_class": "derived",
             "derivation": {"method": "PP3500 devices split into active-subscription / connected-without-active-subscription / not-connected via the site-level subscription join",
                            "inputs": [f"src: {ssrc}", f"src: {fsrc}"]},
             "provenance": {"dataset": FLEET_DS, "snapshot": fsnap},
             "points": [{"label": "under active subscription", "value": attached},
                        {"label": "connected, no active subscription", "value": len(gap_rows)},
                        {"label": "not connected", "value": not_connected}]},
            {"id": "attach-by-region", "label": "Attach % by region", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "active-subscription pumps (site mapped to region via the fleet registry) ÷ PP3500 installed per region",
                            "inputs": [f"src: {ssrc}", f"src: {fsrc}"]},
             "provenance": {"dataset": FLEET_DS, "snapshot": fsnap}, "points": reg_pts},
            {"id": "gap-sites", "label": "Connected-but-unsubscribed pumps by site", "unit": "pumps",
             "evidence_class": "derived",
             "derivation": {"method": "connected PP3500 devices at sites with no active subscription row, counted per site",
                            "inputs": [f"src: {ssrc}", f"src: {fsrc}"]},
             "provenance": {"dataset": FLEET_DS, "snapshot": fsnap},
             "points": [{"label": s, "value": n,
                         "history": "churned" if s in churned_sites else "never-subscribed"}
                        for s, n in gap_sites]},
            {"id": "attach-history", "label": "Attach % over time", "unit": "%",
             "kind": "timeseries", "evidence_class": "unavailable",
             "provenance": {"note": "attach-% history needs historical fleet snapshots (denominator "
                                    "over time) and churn end-dates (numerator over time) — neither "
                                    "exists yet; today's denominator must not be projected backward"},
             "lines": [], "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
