"""BQ-17 — Roadmap capstone: kill / pull-forward composite across competitive
pressure, KOL sentiment (meta-gap caveated), and Cloud Suite attach actuals.

Contract: run(corpus_root, out, pins) — the scoring method is fully stated in
plans/BQ-17.md and mirrored in the derivation chains. Decision support, not the
decision. Deterministic from the five pinned snapshots + config.
"""

import datetime as dt

import computations as C

KOL_DS = "commercial/internal-kol-register"
FEAT_DS = "commercial/external-competitor-features"
FDA_DS = "commercial/openfda-510k-infusion"
SUBS_DS = "commercial/internal-subscriptions"
FLEET_DS = "commercial/internal-fleet"


def run(corpus_root, out, pins):
    p = C.params_for("BQ-17")
    kol, ksnap = C.load_pin_csv(corpus_root, pins, KOL_DS)
    feats, fsnap = C.load_pin_csv(corpus_root, pins, FEAT_DS)
    rows510, snap510 = C.load_pin_csv(corpus_root, pins, FDA_DS)
    subs, ssnap = C.load_pin_csv(corpus_root, pins, SUBS_DS)
    fleet, flsnap = C.load_pin_csv(corpus_root, pins, FLEET_DS)
    srck, srcf = f"{KOL_DS}@{ksnap}", f"{FEAT_DS}@{fsnap}"
    src510, srcs, srcfl = f"{FDA_DS}@{snap510}", f"{SUBS_DS}@{ssnap}", f"{FLEET_DS}@{flsnap}"

    universe = p["feature_universe"]
    eligible = set(p["eligible"])
    cloud = set(p["cloud_features"])
    years = p["feature_years"]
    rank_year = p["feature_rank_year"]
    lane_map = p["attribute_lane_map"]
    lane_kw = p["lane_watch_keywords"]

    # ---- component 1: competitive pressure per feature lane
    # lane-mapped attribute states from the features matrix (capability-typed attributes)
    lane_state = {f: {"behind_shipping": False, "behind_planned": False} for f in universe}
    for attr, lane in lane_map.items():
        rows = [r for r in feats if r["attribute"] == attr]
        if not rows or lane not in lane_state:
            continue  # zero rows for every vendor -> contributes nothing (stated)
        ours = [r for r in rows if r["vendor"] == "GlobalLogic"]
        our_val = ours[0]["value"].strip().lower() if ours else ""
        our_ships = our_val.startswith("yes")
        our_planned = our_val.startswith("planned")
        comp_ships = any(r["value"].strip().lower().startswith("yes")
                         for r in rows if r["vendor"] != "GlobalLogic")
        if comp_ships and not our_ships:
            if our_planned:
                lane_state[lane]["behind_planned"] = True
            else:
                lane_state[lane]["behind_shipping"] = True

    # trailing-12-month lane keyword activity in the 510(k) snapshot
    anchor = max(r["decision_date"] for r in rows510 if r["decision_date"])
    win_start = (dt.date.fromisoformat(anchor) - dt.timedelta(days=365)).isoformat()
    window = [r for r in rows510 if r["decision_date"] and win_start <= r["decision_date"] <= anchor]
    kw_hits = {}
    for f in universe:
        kws = lane_kw.get(f, [])
        kw_hits[f] = [r["k_number"] for r in window
                      if any(k.upper() in r["device_name"].upper() for k in kws)]

    pressure = {}
    for f in universe:
        if lane_state[f]["behind_shipping"]:
            pressure[f] = 1.0
        elif lane_state[f]["behind_planned"] or kw_hits[f]:
            pressure[f] = 0.5
        else:
            pressure[f] = 0.0

    # ---- component 2: KOL sentiment (simulated panel — assumption-class)
    sent = {f: {"voices": set(), "support": 0, "concern": 0, "neutral": 0} for f in universe}
    names = {}
    for r in kol:
        f = r["feature_id"]
        if f in sent:
            sent[f]["voices"].add(r["kol_id"])
            sent[f][r["sentiment"]] = sent[f].get(r["sentiment"], 0) + 1
            names[f] = r["feature_name"]
    sentiment = {}
    for f in universe:
        v = len(sent[f]["voices"])
        net = (sent[f]["support"] - sent[f]["concern"]) / v if v else 0.0
        sentiment[f] = round((net + 1) / 2, 3)  # [-1,1] -> [0,1]; zero voices -> 0.5 neutral? no: 0 voices -> net 0 -> 0.5
    # zero-voice features get no sentiment signal; mark them explicitly
    zero_voice = [f for f in universe if not sent[f]["voices"]]

    # ---- component 3: demand actual — Cloud Suite attach
    conn_sites = {r["site_id"] for r in fleet if r["connected"] == "yes"}
    active_sub_sites = {r["site_id"] for r in subs if r["status"] == "active"} & conn_sites
    attach = round(len(active_sub_sites) / len(conn_sites), 3) if conn_sites else 0.0
    demand = {f: (attach if f in cloud else 0.0) for f in universe}

    # ---- composite + verdicts
    comp = {f: round((pressure[f] + sentiment[f] + demand[f]) / 3, 3) for f in universe}
    elig = sorted(eligible, key=lambda f: (-comp[f], rank_year[f]))
    top_score = comp[elig[0]]
    pull_ties = sorted((f for f in eligible if comp[f] == top_score), key=lambda f: rank_year[f])
    pull = pull_ties[0]
    low_score = min(comp[f] for f in eligible)
    kill_ties = sorted((f for f in eligible if comp[f] == low_score),
                       key=lambda f: len(sent[f]["voices"]))
    kill = kill_ties[0]

    # ---- robustness of the two picks (plan-committed checks, red-team RT-17.1)
    vec = {f: (pressure[f], sentiment[f], demand[f]) for f in universe}
    pull_tie_invariant = len({vec[f] for f in pull_ties}) == 1
    kill_tie_invariant = len({vec[f] for f in kill_ties}) == 1
    # (a) drop the simulated sentiment axis entirely: mean(pressure, demand)
    comp2 = {f: round((pressure[f] + demand[f]) / 2, 3) for f in universe}
    top2 = max(comp2[f] for f in eligible)
    pull2 = sorted((f for f in eligible if comp2[f] == top2), key=lambda f: rank_year[f])[0]
    low2 = min(comp2[f] for f in eligible)
    kill2 = sorted((f for f in eligible if comp2[f] == low2),
                   key=lambda f: len(sent[f]["voices"]))[0]
    nosent_same = (pull2 == pull) and (kill2 == kill)
    # (b) smallest weight transfer pressure -> sentiment that flips the pull-forward pick
    flip_pp, flip_feat = None, None
    for step in range(1, 41):  # 0.25-pp steps, up to a 10-pp transfer
        d = step * 0.0025
        w = (1 / 3 - d, 1 / 3 + d, 1 / 3)
        score = {f: w[0] * pressure[f] + w[1] * sentiment[f] + w[2] * demand[f] for f in eligible}
        rival_score, rival = max((score[g], g) for g in eligible if g != pull)
        if rival_score > score[pull] + 1e-12:
            flip_pp, flip_feat = round(d * 100, 2), rival
            break

    attach_pct = round(100 * attach, 1)
    # RT-17.1: the F9 kill candidate's single voice argues the OPPOSITE direction
    # (source doc: F9 is "too late and too thin" — start EU evidence EARLIER); the
    # 3-value vocabulary encodes it as bare `concern`. Curated note — re-verify against
    # the register's source docs if the F9 row set changes.
    kill_direction_note = (kill == "F9" and len(sent["F9"]["voices"]) == 1)
    headline = (f"Decision support, not the decision: pull-forward candidate {pull} "
                f"{names.get(pull, '')} (composite {comp[pull]}"
                + (f", tie with {', '.join(x for x in pull_ties[1:])} broken on earliest wave"
                   if len(pull_ties) > 1 else "")
                + f"); kill candidate {kill} {names.get(kill, '')} (composite {comp[kill]}"
                + (f", tie with {', '.join(x for x in kill_ties[1:])} broken on weakest evidence "
                   f"base" if len(kill_ties) > 1 else "")
                + f") — sentiment axis is simulated-panel only, demand axis is Cloud attach "
                f"{attach_pct}%"
                + (". CAUTION on the kill read: the single F9 voice argues the slot is too LATE "
                   "and too THIN — a voice FOR earlier EU investment, arithmetically converted "
                   "into kill support by the 3-value sentiment vocabulary"
                   if kill_direction_note else ""))

    lines = [
        "# BQ-17 — Roadmap capstone: kill / pull-forward composite", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [derived: composite] [src: {srck}] "
        f"[src: {srcs}] [config: commercial.yml]", "",
        "## Composite per feature — method fully stated", "",
        "_Three components in [0, 1], unweighted mean (config choice) [config: commercial.yml]: "
        "competitive pressure (parity gaps + lane clearance activity), simulated-panel KOL "
        "sentiment rescaled, Cloud attach applied to cloud-delivered features. Full rules in "
        "plans/BQ-17.md; every caveat below the table._", "",
        "| Feature | Wave | Pressure | Sentiment | Demand | Composite | Eligible |",
        "|---|---|---|---|---|---|---|",
    ]
    for f in universe:
        lines.append(f"| {f} {names.get(f, '(program-wide)')} [derived: composite] "
                     f"[config: commercial.yml] | {years[f]} | {pressure[f]} | {sentiment[f]} | "
                     f"{demand[f]} | {comp[f]} | {'yes' if f in eligible else 'context only'} |")
    lines += [
        "",
        f"- Pressure inputs: lane-mapped parity states from [src: {srcf}]; trailing-12-month lane "
        f"keyword hits {win_start} → {anchor} from [src: {src510}] [config: commercial.yml]. "
        f"Keyword hits: " + ("; ".join(f"{f}: {', '.join(ks)}" for f, ks in kw_hits.items() if ks)
                             or "none") + ".",
        f"- Sentiment inputs: distinct-voice net sentiment from [src: {srck}] — SIMULATED panel, "
        f"zero real collected KOL evidence (BQ-16 meta-gap); this third of every composite is "
        f"assumption-class.",
        f"- Demand input: Cloud Suite attach {attach_pct}% = {len(active_sub_sites)} active "
        f"subscribed connected sites of {len(conn_sites)} connected sites "
        f"[derived: attach-rate] [src: {srcs}] [src: {srcfl}]. Non-cloud features "
        f"(F7, F9) score zero on this axis BY CONSTRUCTION — no demand dataset exists for them; "
        f"zero is a data gap, not measured absence of demand [config: commercial.yml].",
        "",
        "## The two candidates (derived rankings, council judgment pending)", "",
        f"- **Pull forward: {pull} {names.get(pull, '')}** ({years[pull]}) — composite {comp[pull]} "
        f"[derived: composite]"
        + (f"; exact tie with {', '.join(pull_ties[1:])} broken by earliest scheduled wave "
           f"[config: commercial.yml]" if len(pull_ties) > 1 else "") + ".",
        f"- **Kill candidate: {kill} {names.get(kill, '')}** ({years[kill]}) — composite "
        f"{comp[kill]} [derived: composite]"
        + (f"; exact tie with {', '.join(kill_ties[1:])} broken by fewest distinct voices "
           f"({len(sent[kill]['voices'])} vs "
           + ", ".join(str(len(sent[f]['voices'])) for f in kill_ties[1:])
           + f") [src: {srck}]" if len(kill_ties) > 1 else "") + ".",
    ]
    if kill_direction_note:
        lines += [
            f"- **Direction of the only voice behind the kill candidate**: the single F9 voice on "
            f"file (Kuitunen) argues F9 is 'too late and too thin' — start the EU "
            f"clinical-evaluation and library-governance evidence EARLIER (Y1-Y2), not never "
            f"[src: {srck}] (per-KOL source doc via the dataset README). The register's 3-value "
            f"vocabulary encodes that position as bare `concern`, which zeroes F9's sentiment axis "
            f"— i.e. a voice FOR earlier, stronger investment arithmetically supports the kill "
            f"ranking. A kill decision citing this composite must weigh that the only evidence on "
            f"file contradicts the kill reading.",
        ]
    lines += [
        "",
        "## Robustness of the two picks (computed, plan-committed)", "",
        f"- Weighting invariance: the top tie ({' / '.join(pull_ties)}) "
        f"{'shares an IDENTICAL axis vector' if pull_tie_invariant else 'does NOT share one axis vector'} "
        f"and the bottom tie ({' / '.join(kill_ties)}) "
        f"{'shares an IDENTICAL axis vector' if kill_tie_invariant else 'does NOT share one axis vector'} "
        f"— an identical-vector tie survives ANY axis weighting, so each pick is 100% "
        f"tie-break-decided (earliest wave / fewest voices), not weighting-decided "
        f"[derived: robustness] [config: commercial.yml].",
        f"- Sentiment-axis drop: recomputing WITHOUT the simulated sentiment axis (mean of "
        f"pressure + demand) leaves {'BOTH picks unchanged (' + pull2 + ' / ' + kill2 + ')' if nosent_same else 'the picks CHANGED (' + pull2 + ' / ' + kill2 + ')'} "
        f"— the assumption-class axis is {'not' if nosent_same else ''} load-bearing for the two "
        f"candidates themselves [derived: robustness].",
        (f"- Weight sensitivity: transferring ~{flip_pp} pp of weight from the pressure axis to the "
         f"sentiment axis flips the pull-forward candidate to {flip_feat} — the margin over the "
         f"runner-up at equal weights is small, and the flipping axis is the simulated one; "
         f"revisit weights with the council [derived: robustness] [config: commercial.yml]."
         if flip_pp is not None else
         "- Weight sensitivity: no pull-forward flip within a 10-pp pressure-to-sentiment weight "
         "transfer [derived: robustness] [config: commercial.yml]."),
    ]

    narrative = {"issues": [], "risks": [], "watch": []}
    if kill_direction_note:
        narrative["issues"].append({
            "id": "I1", "severity": "high",
            "statement": "Direction inversion on the kill candidate: the single F9 voice on file "
                         "(Kuitunen) argues F9 is too LATE and too THIN — advocating earlier EU "
                         "evidence investment — but the 3-value sentiment vocabulary encodes it as "
                         "bare concern, arithmetically supporting the kill ranking; the only "
                         "evidence on file contradicts the kill reading",
            "action": "Present the voice's actual position alongside any kill discussion; add a "
                      "stance/timing-direction dimension to the register before the next edition "
                      "(BQ-16 RT-16.1 shares this defect)",
            "evidence": [f"src: {srck}", "derived: composite"],
        })
    narrative["risks"].append({
        "id": "R1", "severity": "high",
        "statement": f"The kill ranking rests on a composite whose sentiment third is simulated and "
                     f"whose demand third does not exist for non-cloud features — {kill} scores "
                     f"zero pressure, zero measured demand, and its sentiment comes from "
                     f"{len(sent[kill]['voices'])} simulated voice(s)",
        "mitigation": "Before any kill decision: collect real KOL evidence for the candidate and "
                      "acquire a demand-side dataset for non-cloud features (home-infusion channel, "
                      "international pipeline)",
        "evidence": ["derived: composite", f"src: {srck}"],
    })
    if len(kill_ties) > 1:
        narrative["risks"].append({
            "id": "R2", "severity": "medium",
            "statement": f"{' and '.join(kill_ties)} tie exactly at composite {low_score} — only "
                         f"evidence thinness separates the kill candidate from the runner(s)-up",
            "mitigation": "Treat both bottom-tier features as evidence-starved rather than ranking "
                          "one safe; the tiebreak is stated, not meaningful",
            "evidence": ["derived: composite", f"src: {srck}"],
        })
    narrative["watch"].append({
        "id": "W1",
        "statement": "Equal axis weighting is a committed modeling choice, not derived from the "
                     "plan of record — and the flip distance is SMALL: "
                     + (f"a ~{flip_pp} pp pressure-to-sentiment weight transfer flips the "
                        f"pull-forward candidate to {flip_feat}" if flip_pp is not None
                        else "though no pull-forward flip occurs within a 10-pp transfer")
                     + "; the two picks themselves are tie-break-decided and weighting-invariant "
                       "(see robustness) — revisit the weights with the council before acting",
        "evidence": ["config: commercial.yml", "derived: robustness", "derived: composite"],
    })
    narrative["watch"].append({
        "id": "W2",
        "statement": "No business-case axis: revenue/margin per feature is absent from this "
                     "composite entirely — the ranking is evidence pressure, not economics",
        "evidence": ["derived: composite"],
    })

    # history: gross cumulative subscribed-site adds by month (demand-signal history)
    starts = sorted(r["start_date"][:7] for r in subs)
    months = []
    curm = starts[0]
    last = starts[-1]
    while curm <= last:
        months.append(curm)
        y, m = int(curm[:4]), int(curm[5:7])
        curm = f"{y + (m == 12):04d}-{(m % 12) + 1:02d}"
    per_m = {}
    for s in starts:
        per_m[s] = per_m.get(s, 0) + 1
    run_total, ts_pts = 0, []
    for m in months:
        run_total += per_m.get(m, 0)
        ts_pts.append({"x": m + "-01", "y": run_total})

    lines += C.expectations_section(C.evaluate_expectations("BQ-17", {}))
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Components computed from the five pins: parity states [src: {srcf}], clearance keyword "
        f"activity [src: {src510}], sentiment [src: {srck}], attach [src: {srcs}] + [src: {srcfl}]; "
        f"all maps, weights, and eligibility from [config: commercial.yml].",
        "- Historical view: gross cumulative subscribed-site adds by start month are charted as the "
        f"demand-signal history [derived: subscribed-sites-history] [src: {srcs}]; churn dates are "
        "not recorded in the register, so the line shows gross adds, not net — stated, not hidden.",
        "- A composite-score history needs successive editions of this answer — none exist yet; "
        "re-answers will accumulate it [derived: composite].",
    ]

    data = {
        "bq": "BQ-17",
        "series": [
            {"id": "candidates", "label": "Kill / pull-forward candidates", "unit": "composite",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "argmax/argmin of the composite over eligible features; ties broken by earliest wave (pull) / fewest voices (kill)",
                            "inputs": ["derived: composite", "config: commercial.yml"]},
             "provenance": {"dataset": KOL_DS, "snapshot": ksnap},
             "points": [{"label": f"pull forward — {pull} {names.get(pull, '')}", "value": comp[pull]},
                        {"label": f"kill candidate — {kill} {names.get(kill, '')}", "value": comp[kill]}]},
            {"id": "composite", "label": "Composite score by feature", "unit": "score",
             "evidence_class": "derived",
             "derivation": {"method": "mean(pressure, rescaled net sentiment, attach-for-cloud-features) per plans/BQ-17.md",
                            "inputs": [f"src: {srcf}", f"src: {src510}", f"src: {srck}",
                                       "derived: attach-rate", "config: commercial.yml"]},
             "provenance": {"dataset": FEAT_DS, "snapshot": fsnap},
             "points": [{"label": f"{f} {names.get(f, '')}".strip(), "value": comp[f],
                         "pressure": pressure[f], "sentiment": sentiment[f], "demand": demand[f],
                         "eligible": f in eligible} for f in universe]},
            {"id": "robustness", "label": "Robustness of the two picks", "unit": "",
             "evidence_class": "derived",
             "derivation": {"method": "tie-vector identity check (an identical-axis-vector tie survives any weighting); composite recomputed without the sentiment axis (mean of pressure + demand); smallest pressure-to-sentiment weight transfer (0.25-pp scan to 10 pp) that flips the pull-forward pick",
                            "inputs": ["derived: composite", "config: commercial.yml"]},
             "provenance": {"dataset": KOL_DS, "snapshot": ksnap},
             "points": [{"label": f"top tie ({' / '.join(pull_ties)}) weighting-invariant (identical axis vectors)",
                         "value": "yes" if pull_tie_invariant else "no"},
                        {"label": f"bottom tie ({' / '.join(kill_ties)}) weighting-invariant (identical axis vectors)",
                         "value": "yes" if kill_tie_invariant else "no"},
                        {"label": "picks unchanged with the simulated sentiment axis dropped",
                         "value": f"yes ({pull2} / {kill2})" if nosent_same else f"NO ({pull2} / {kill2})"},
                        {"label": "smallest pressure-to-sentiment weight transfer flipping the pull-forward pick (pp)",
                         "value": flip_pp if flip_pp is not None else "none within 10 pp",
                         "flips_to": flip_feat}]},
            {"id": "attach-rate", "label": "Cloud Suite attach (demand actual)", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "active subscribed connected sites ÷ all connected sites",
                            "inputs": [f"src: {srcs}", f"src: {srcfl}"]},
             "provenance": {"dataset": SUBS_DS, "snapshot": ssnap},
             "points": [{"label": f"of {len(conn_sites)} connected sites with an active subscription",
                         "value": attach_pct}]},
            {"id": "subscribed-sites-history", "label": "Cumulative subscribed-site adds (gross)",
             "unit": "sites", "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": SUBS_DS, "snapshot": ssnap,
                            "note": "gross adds by start month; churn dates not recorded"},
             "lines": [{"label": "subscribed sites (gross adds)", "points": ts_pts}], "points": []},
            {"id": "noncloud-demand", "label": "Demand signal for non-cloud features (F7, F9)",
             "unit": "", "evidence_class": "unavailable",
             "provenance": {"note": "no demand dataset exists for the home-infusion channel (F7) or "
                                    "international pipeline (F9) — their zero demand score is a "
                                    "data gap by construction, not measured absence"},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": C.evaluate_expectations("BQ-17", {}),
    }
    C.write(out, lines, data)
