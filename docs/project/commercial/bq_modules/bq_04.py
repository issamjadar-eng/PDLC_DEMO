"""BQ-04 — Cloud Suite unit economics: LTV per connected pump vs cost-to-serve,
site-size profitability, and the hardware-discount (cannibalization) signal.

Deterministic: computes ONLY from the pinned internal-subscriptions and internal-fleet
snapshots. See plans/BQ-04.md for the committed definitions (active-sites basis, the
simple undiscounted LTV model and its stated limits, size bands, discount mean).
"""

import datetime as dt
import math
import sys

import computations as C

SUB_DS = "commercial/internal-subscriptions"
FLEET_DS = "commercial/internal-fleet"


def run(corpus_root, out, pins):
    p = C.params_for("BQ-04")
    subs, ssnap = C.load_pin_csv(corpus_root, pins, SUB_DS)
    fleet, fsnap = C.load_pin_csv(corpus_root, pins, FLEET_DS)
    src = f"{SUB_DS}@{ssnap}"
    fsrc = f"{FLEET_DS}@{fsnap}"
    horizon = int(p["ltv_horizon_years"])
    min_ratio = float(p["min_ltv_cts_ratio"])
    max_disc = float(p["max_asp_erosion_pct"])
    bands_cfg = p["size_bands"]
    small_max, large_min = int(bands_cfg["small_max_pumps"]), int(bands_cfg["large_min_pumps"])

    active = [r for r in subs if r["status"] == "active"]
    churned = [r for r in subs if r["status"] == "churned"]
    # a register status outside {active, churned} must surface loudly, not silently drop
    # from both the rates and the churn count (code-review finding, ben/108)
    other_status = [r for r in subs if r["status"] not in ("active", "churned")]
    other_statuses = sorted({r["status"] for r in other_status})
    if other_status:
        print(f"bq_04: WARNING — {len(other_status)} register rows carry unrecognized "
              f"status value(s) {other_statuses}; they are excluded from the active rates "
              f"and the churn count but still sit in the register-row denominators",
              file=sys.stderr)
    pumps = sum(int(r["pumps_connected"]) for r in active)
    arr = sum(int(r["arr_usd"]) for r in active)
    cts = sum(int(r["cost_to_serve_usd"]) for r in active)
    # compute on raw sums, round only for display (red-team finding, ben/108):
    # rounding intermediates is the pattern that flips verdicts at thresholds
    arr_rate = arr / pumps if pumps else 0.0
    cts_rate = cts / pumps if pumps else 0.0
    arr_pp = round(arr_rate)
    cts_pp = round(cts_rate)
    ltv = round(arr_rate * horizon)
    ltv_cost = round(cts_rate * horizon)
    ratio_raw = arr / cts if cts else 0.0     # raw sums; the horizon cancels
    ratio = round(ratio_raw, 2)
    churn_pct = C.pct(len(churned), len(subs))

    # size bands
    def band(r):
        n = int(r["pumps_connected"])
        if n <= small_max:
            return f"small (<= {small_max} pumps)"
        if n >= large_min:
            return f"large (>= {large_min} pumps)"
        return f"mid ({small_max + 1}-{large_min - 1} pumps)"

    band_order = [f"small (<= {small_max} pumps)", f"mid ({small_max + 1}-{large_min - 1} pumps)",
                  f"large (>= {large_min} pumps)"]
    bstats = {}
    for b in band_order:
        rows_b = [r for r in active if band(r) == b]
        bp = sum(int(r["pumps_connected"]) for r in rows_b)
        ba = sum(int(r["arr_usd"]) for r in rows_b)
        bc = sum(int(r["cost_to_serve_usd"]) for r in rows_b)
        neg = sum(1 for r in rows_b if int(r["arr_usd"]) < int(r["cost_to_serve_usd"]))
        bstats[b] = {"sites": len(rows_b), "pumps": bp,
                     "arr_pp": round(ba / bp) if bp else 0,
                     "cts_pp": round(bc / bp) if bp else 0,
                     # margin on raw sums (not a difference of rounded rates)
                     "margin_pp": round((ba - bc) / bp) if bp else 0,
                     "neg_sites": neg,
                     "disc": round(sum(float(r["hardware_discount_pct"]) for r in rows_b)
                                   / len(rows_b), 1) if rows_b else 0.0}
    neg_sites_total = sum(1 for r in active if int(r["arr_usd"]) < int(r["cost_to_serve_usd"]))
    discounts = [float(r["hardware_discount_pct"]) for r in active]
    disc_raw = sum(discounts) / len(discounts) if discounts else 0.0
    disc_mean = round(disc_raw, 1)
    # near-threshold sensitivity for E-04.2 (red-team finding, ben/108): the verdict
    # rides on a sample mean vs an unvalidated stand-in line — report the standard
    # error and flag a knife-edge when the miss is within 1pp of the threshold or
    # within ~2 SE of it (either signal makes the verdict fragile)
    disc_sd = math.sqrt(sum((x - disc_raw) ** 2 for x in discounts) / (len(discounts) - 1)) \
        if len(discounts) > 1 else 0.0
    disc_se = disc_sd / math.sqrt(len(discounts)) if discounts else 0.0
    disc_margin = disc_raw - max_disc
    # the two knife-edge conditions are tracked separately so the prose can name which
    # fired and the actual SE multiple, instead of asserting "≈2 standard errors"
    # statically (code-review finding, ben/108)
    disc_within_1pp = abs(disc_margin) <= 1.0
    disc_within_2se = disc_se > 0 and abs(disc_margin) <= 2 * disc_se
    disc_knife_edge = disc_within_1pp or disc_within_2se
    disc_conds = (["|miss| ≤ 1pp"] if disc_within_1pp else []) + \
        (["|miss| ≤ 2 SE"] if disc_within_2se else [])
    disc_fired = " and ".join(disc_conds)
    disc_n_se = round(abs(disc_margin) / disc_se, 1) if disc_se > 0 else None

    # fleet context: connected universe + attach gap
    connected = [r for r in fleet if r["connected"] == "yes"]
    conn_sites = {r["site_id"] for r in connected}
    sub_sites = {r["site_id"] for r in subs}  # active + churned
    gap_sites = sorted(conn_sites - sub_sites)

    # ARR build from active-site start dates (survivor-biased; stated). Guard: zero
    # active sites must degrade to an unavailable series, not an IndexError on starts[0]
    # (code-review finding, ben/108)
    starts = sorted((r["start_date"], int(r["arr_usd"])) for r in active)
    arr_pts = []
    if starts:
        months = []
        cur = dt.date.fromisoformat(starts[0][0]).replace(day=1)
        end = dt.date.fromisoformat(starts[-1][0]).replace(day=1)
        while cur <= end:
            months.append(cur.isoformat())
            cur = (cur.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
        run_total, si = 0, 0
        for m in months:
            nxt = (dt.date.fromisoformat(m).replace(day=28) + dt.timedelta(days=4)).replace(day=1)
            while si < len(starts) and starts[si][0] < nxt.isoformat():
                run_total += starts[si][1]
                si += 1
            arr_pts.append({"x": m, "y": round(run_total / 1000, 1)})

    small_label = band_order[0]
    # "concentrated in <band> sites" is computed from the band split of ARR-below-cost
    # sites, not narrated (code-review finding, ben/108): the clause names the band only
    # when it holds a strict majority of the negative sites
    if neg_sites_total:
        worst_neg_band = max(band_order, key=lambda b: bstats[b]["neg_sites"])
        if bstats[worst_neg_band]["neg_sites"] * 2 > neg_sites_total:
            neg_clause = f" — concentrated in {worst_neg_band.split(' ')[0]} sites — "
        else:
            neg_clause = " — spread across the size bands — "
    else:
        neg_clause = " "
    headline = (f"Unit economics fail the guardrail: LTV per connected pump ${ltv:,} vs "
                f"${ltv_cost:,} cost-to-serve over the same {horizon}-year horizon "
                f"(ratio {ratio} vs the {min_ratio} floor); {neg_sites_total} of {len(active)} "
                f"active sites run ARR below cost-to-serve{neg_clause}and the "
                f"mean hardware discount at subscribed sites is {disc_mean}% vs the {max_disc:.0f}% "
                f"tolerance" if ratio_raw < min_ratio else
                f"LTV per connected pump ${ltv:,} covers ${ltv_cost:,} cost-to-serve at "
                f"{ratio}x (floor {min_ratio}); mean hardware discount {disc_mean}% vs the "
                f"{max_disc:.0f}% tolerance")

    narrative = {"issues": [], "risks": [], "watch": []}
    ni = 0
    if bstats[small_label]["margin_pp"] < 0:
        ni += 1
        narrative["issues"].append({
            "id": f"I{ni}", "severity": "high",
            "statement": f"Small sites are negative at unit level: {bstats[small_label]['sites']} "
                         f"sites (<= {small_max} pumps) run ${abs(bstats[small_label]['margin_pp']):,}"
                         f"/pump/yr below water ({bstats[small_label]['neg_sites']} of them "
                         f"ARR-below-cost individually)",
            "action": "Set a minimum-deal-size or platform-fee floor for new subscriptions; "
                      "review the serve model (remote-first) for the existing small-site tail",
            "evidence": ["derived: band-economics", f"src: {src}", "config: commercial.yml"],
        })
    if disc_raw > max_disc:
        ni += 1
        narrative["issues"].append({
            "id": f"I{ni}", "severity": "medium",
            "statement": f"Mean hardware discount at subscribed sites is {disc_mean}%, over the "
                         f"{max_disc:.0f}% tolerance — the subscription may be being bought with "
                         f"hardware price",
            "action": "Pull deal-level pricing for subscribed vs unsubscribed sites; without an "
                      "unsubscribed baseline in the corpus, causality stays unproven either way",
            "evidence": ["derived: discount-by-band", f"src: {src}", "config: commercial.yml"],
        })
    rn = 0
    if ratio_raw < min_ratio:
        rn += 1
        narrative["risks"].append({
            "id": f"R{rn}", "severity": "high",
            "statement": f"Fleet-wide LTV:cost-to-serve is {ratio}, under the {min_ratio} floor — "
                         f"and the LTV side is flattered by the model (no churn decrement, no "
                         f"discounting) while {len(churned)} churned sites already exist",
            "mitigation": "Fix the cost side (serve model) before growing the small-site tail; "
                          "re-underwrite the floor once a churn-adjusted LTV is possible",
            "evidence": ["derived: unit-econ-stat", f"src: {src}", "config: commercial.yml"],
        })
    narrative["watch"].append({
        "id": "W1",
        "statement": f"Attach gap: {len(gap_sites)} connected sites carry no subscription "
                     f"({', '.join(gap_sites)}) — expansion revenue that needs no new hardware",
        "evidence": ["derived: attach-gap", f"src: {fsrc}", f"src: {src}"],
    })
    narrative["watch"].append({
        "id": "W2",
        "statement": f"Churn on file: {len(churned)} of {len(subs)} register rows ({churn_pct}%) — "
                     f"direct evidence that the no-churn {horizon}-year horizon overstates LTV",
        "evidence": ["derived: unit-econ-stat", f"src: {src}"],
    })
    if disc_knife_edge:
        narrative["watch"].append({
            "id": "W3",
            "statement": f"E-04.2 is a knife-edge: the mean hardware discount misses the "
                         f"{max_disc:.0f}% stand-in tolerance by {disc_margin:+.1f}pp on an "
                         f"n={len(active)} mean (SE ≈ {round(disc_se, 1)}pp; the miss is "
                         f"{disc_n_se} standard errors from the line; flagged on {disc_fired}) "
                         f"— the verdict is fragile to the "
                         f"unvalidated stand-in threshold choice; treat it as a watch signal, "
                         f"not a breach finding, until pricing policy sets a real cap",
            "evidence": ["derived: discount-sensitivity", "derived: discount-by-band",
                         "config: commercial.yml", f"src: {src}"],
        })

    exp_results = {
        "E-04.1": (f"ratio {ratio} (ARR ${arr_pp:,}/pump/yr vs cost ${cts_pp:,}/pump/yr, "
                   f"active sites; ratio computed on raw sums, rounded for display)",
                   "met" if ratio_raw >= min_ratio else "not-met",
                   ["derived: unit-econ-stat"]),
        "E-04.2": (f"mean hardware discount {disc_mean}% across {len(active)} active subscribed "
                   f"sites — {disc_margin:+.1f}pp vs the {max_disc:.0f}% stand-in line"
                   + (f"; KNIFE-EDGE on {disc_fired} (miss = {disc_n_se} SE, "
                      f"SE ≈ {round(disc_se, 1)}pp, "
                      f"n={len(active)}) against an unvalidated threshold — verdict fragile to the "
                      f"stand-in choice" if disc_knife_edge else ""),
                   "met" if disc_raw <= max_disc else "not-met",
                   ["derived: discount-by-band", "derived: discount-sensitivity"]),
    }
    exps = C.evaluate_expectations("BQ-04", exp_results)

    rl = [
        "# BQ-04 — Subscription unit economics: LTV vs cost-to-serve, and the discount signal",
        "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [config: commercial.yml]", "",
        "## Fleet-wide unit economics (active subscribed sites)", "",
        "_LTV model (stated, deliberately simple): per-pump ARR × the configured horizon —",
        "undiscounted, no churn decrement, no growth. Churned sites are excluded from the rates",
        "but counted below; their existence means the no-churn horizon OVERSTATES LTV._", "",
        f"- ARR per connected pump: ${arr_pp:,}/yr; cost-to-serve per pump: ${cts_pp:,}/yr "
        f"[derived: unit-econ-stat] [src: {src}]",
        f"- LTV over {horizon} years: ${ltv:,} vs ${ltv_cost:,} cost — ratio {ratio} "
        f"(guardrail {min_ratio}) [derived: unit-econ-stat] [config: commercial.yml]",
        f"- Basis: {len(active)} active sites, {pumps} connected pumps; {len(churned)} churned "
        f"sites ({churn_pct}% of register rows) [src: {src}]",
        *([f"- ⚠ {len(other_status)} register rows carry unrecognized status value(s) "
           f"({', '.join(other_statuses)}) — excluded from the active rates AND the churn "
           f"count while still in the register-row denominators; classify them before "
           f"trusting the basis [src: {src}]"] if other_status else []),
        f"- Fleet context: {len(connected)} connected devices in the installed base; "
        f"{len(gap_sites)} connected sites with no subscription (attach gap) "
        f"[derived: attach-gap] [src: {fsrc}]",
        "",
        "## Site-size profitability split", "",
        f"- Bands on connected-pump count [config: commercial.yml]:", "",
        "| Band | Sites | Pumps | ARR/pump/yr | Cost/pump/yr | Margin/pump/yr | ARR-below-cost sites | Mean hw discount |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for b in band_order:
        s = bstats[b]
        rl.append(f"| {b} [src: {src}] [derived: band-economics] | {s['sites']} | {s['pumps']} | "
                  f"${s['arr_pp']:,} | ${s['cts_pp']:,} | ${s['margin_pp']:,} | {s['neg_sites']} | "
                  f"{s['disc']}% |")
    rl += [
        "",
        f"- {neg_sites_total} of {len(active)} active sites run ARR below annual cost-to-serve "
        f"[derived: band-economics] [src: {src}]",
        "",
        "## Hardware-discount signal (cannibalization)", "",
        f"- Mean hardware discount at active subscribed sites: {disc_mean}% vs the "
        f"{max_disc:.0f}% tolerance [derived: discount-by-band] [config: commercial.yml] "
        f"[src: {src}]",
        f"- Threshold sensitivity (disclosed): the miss is {disc_margin:+.1f}pp on an "
        f"n={len(active)} mean with SE ≈ {round(disc_se, 1)}pp"
        + (f" — a knife-edge flagged on {disc_fired} (the miss is {disc_n_se} standard "
           f"errors from the stand-in tolerance); the "
           "verdict is fragile to the unvalidated threshold choice (see W3)"
           if disc_knife_edge else "")
        + " [derived: discount-sensitivity] [config: commercial.yml]",
        "- No unsubscribed-site discount baseline exists in the corpus, so this is a signal at",
        "  subscribed sites, not a causal cannibalization claim (stated in the analysis plan).",
    ]
    rl += C.expectations_section(exps)
    rl += C.narrative_section(narrative)
    rl += [
        "## Method & provenance", "",
        f"- ARR, cost-to-serve, status, and discounts measured from [src: {src}]; connectivity "
        f"and the attach gap from [src: {fsrc}].",
        f"- LTV, ratios, bands, and means are arithmetic derivations with methods declared per "
        f"series [derived: unit-econ-stat] [derived: band-economics].",
        f"- The ARR-build history is derived from active sites' start dates at current ARR — "
        f"survivor-biased (churned sites' past ARR is absent) and stated as such "
        f"[derived: arr-build] [src: {src}]. True economics history needs recurring register "
        f"snapshots (stated gap).",
    ]

    data = {
        "bq": "BQ-04",
        "series": [
            {"id": "unit-econ-stat", "label": "LTV vs cost-to-serve per connected pump", "unit": "USD",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": f"per-pump ARR and cost rates over active sites × "
                                      f"{horizon}-year undiscounted horizon; ratio = Σ ARR ÷ "
                                      "Σ cost_to_serve on raw sums (horizon cancels), rounded "
                                      "for display only",
                            "inputs": [f"src: {src}", "config: commercial.yml"]},
             "provenance": {"dataset": SUB_DS, "snapshot": ssnap},
             "points": [
                 {"label": f"LTV per connected pump, {horizon}-yr undiscounted", "value": ltv},
                 {"label": f"cost-to-serve per pump over the same horizon", "value": ltv_cost},
                 {"label": "LTV : cost-to-serve ratio", "value": ratio},
             ]},
            {"id": "band-economics", "label": "ARR vs cost-to-serve per pump by site size",
             "unit": "USD/pump/yr", "kind": "paired-bars",
             "pairs": {"a_label": "ARR/pump", "b_label": "cost/pump"},
             "evidence_class": "derived",
             "derivation": {"method": "per size band over active sites: Σ ARR ÷ Σ pumps and "
                                      "Σ cost_to_serve ÷ Σ pumps",
                            "inputs": [f"src: {src}", "config: commercial.yml"]},
             "provenance": {"dataset": SUB_DS, "snapshot": ssnap},
             "points": [{"label": b, "a": bstats[b]["arr_pp"], "b": bstats[b]["cts_pp"],
                         "sites": bstats[b]["sites"]} for b in band_order]},
            {"id": "discount-by-band", "label": "Mean hardware discount by site size", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "simple mean of hardware_discount_pct across active "
                                      "subscribed sites, per band and overall",
                            "inputs": [f"src: {src}", "config: commercial.yml"]},
             "provenance": {"dataset": SUB_DS, "snapshot": ssnap},
             "points": [{"label": b, "value": bstats[b]["disc"]} for b in band_order]
                       + [{"label": "all active sites", "value": disc_mean}]},
            {"id": "discount-sensitivity",
             "label": "E-04.2 threshold sensitivity — miss vs sampling noise", "unit": "pp",
             "evidence_class": "derived",
             "derivation": {"method": "margin = raw mean hardware_discount_pct − tolerance; "
                                      "SE = sample standard deviation (n−1) ÷ √n over active "
                                      "sites; knife-edge flagged when |margin| ≤ 1pp or "
                                      "|margin| ≤ 2 × SE",
                            "inputs": [f"src: {src}", "config: commercial.yml",
                                       "derived: discount-by-band"]},
             "provenance": {"dataset": SUB_DS, "snapshot": ssnap},
             "points": [
                 {"label": "miss vs tolerance (pp)", "value": round(disc_margin, 2)},
                 {"label": "standard error of the mean (pp)", "value": round(disc_se, 2)},
                 {"label": "knife-edge (|miss| <= 1pp or <= 2 SE)",
                  "value": "yes" if disc_knife_edge else "no"},
             ]},
            {"id": "attach-gap", "label": "Connected sites with no subscription", "unit": "sites",
             "evidence_class": "derived",
             "derivation": {"method": "sites with >= 1 connected device in the fleet registry "
                                      "minus sites present in the subscription register",
                            "inputs": [f"src: {fsrc}", f"src: {src}"]},
             "provenance": {"dataset": FLEET_DS, "snapshot": fsnap},
             "points": [{"label": s, "value": 1} for s in gap_sites]},
            ({"id": "arr-build", "label": "ARR build from active-site start dates ($K, survivor-biased)",
              "unit": "$K", "kind": "timeseries", "evidence_class": "derived",
              "derivation": {"method": "cumulative current ARR of active sites by subscription "
                                       "start month — churned sites' past ARR absent (survivor "
                                       "bias stated)",
                             "inputs": [f"src: {src}"]},
              "provenance": {"dataset": SUB_DS, "snapshot": ssnap},
              "lines": [{"label": "cumulative ARR (active sites)", "points": arr_pts}],
              "points": []}
             if arr_pts else
             {"id": "arr-build", "label": "ARR build from active-site start dates ($K, survivor-biased)",
              "unit": "$K", "kind": "timeseries", "evidence_class": "unavailable",
              "provenance": {"note": "no active sites in the pinned register — the ARR-build "
                                     "history cannot be derived from an empty roster"},
              "lines": [], "points": []}),
            {"id": "econ-history", "label": "LTV / cost-to-serve history", "unit": "USD",
             "evidence_class": "unavailable",
             "provenance": {"note": "one register snapshot exists — unit-economics history "
                                    "accumulates as recurring snapshots land; a single point is "
                                    "not a trend"},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, rl, data)
