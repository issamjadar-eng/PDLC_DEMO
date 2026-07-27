"""BQ-16 — KOL evidence audit per roadmap feature: voices, sentiment, the E-16.1
floor, the wave check — and the META-GAP headline (the register is a simulated panel;
zero real collected KOL evidence exists).

Contract: run(corpus_root, out, pins) — see plans/BQ-16.md for committed definitions.
"""

import computations as C

KOL_DS = "commercial/internal-kol-register"

REAL_TYPES = ("interview", "survey", "publication")


def run(corpus_root, out, pins):
    p = C.params_for("BQ-16")
    rows, snap = C.load_pin_csv(corpus_root, pins, KOL_DS)
    src = f"{KOL_DS}@{snap}"
    universe = p["feature_universe"]
    years = p["feature_years"]
    floor = int(p["min_voices_per_feature"])
    wave_years = tuple(p["wave_check_years"])

    # evidence-type census (the meta-gap)
    by_type = {}
    for r in rows:
        by_type[r["evidence_type"]] = by_type.get(r["evidence_type"], 0) + 1
    real_n = sum(by_type.get(t, 0) for t in REAL_TYPES)
    sim_n = len(rows) - real_n

    # per-feature voices + sentiment
    feat = {}
    names = {}
    for f in universe:
        feat[f] = {"voices": set(), "support": 0, "neutral": 0, "concern": 0, "rows": 0}
    for r in rows:
        f = r["feature_id"]
        if f not in feat:
            feat[f] = {"voices": set(), "support": 0, "neutral": 0, "concern": 0, "rows": 0}
        feat[f]["voices"].add(r["kol_id"])
        feat[f][r["sentiment"]] = feat[f].get(r["sentiment"], 0) + 1
        feat[f]["rows"] += 1
        names[f] = r["feature_name"]

    single = [f for f in universe if len(feat[f]["voices"]) == 1]
    zero = [f for f in universe if len(feat[f]["voices"]) == 0]
    below = [f for f in universe if len(feat[f]["voices"]) < floor]
    concern_major = [f for f in universe
                     if feat[f]["concern"] > feat[f]["support"] + feat[f]["neutral"]]
    wave_flagged = [f for f in concern_major if years[f].startswith(wave_years)]

    headline = (f"META-GAP: all {sim_n} evidence rows are a simulated advisory panel — zero real "
                f"collected KOL evidence exists (no interviews, surveys, or publications). Within "
                f"the simulated register: {', '.join(single) if single else 'no feature'} rides on a "
                f"single voice ({'E-16.1 floor not met' if below else 'E-16.1 floor met'}), and the "
                f"{', '.join(wave_flagged) if wave_flagged else 'no'} wave slots carry concern-majority "
                f"sentiment — read as NO documented endorsement of those slots, not as opposition: the "
                f"register's 3-value vocabulary collapses conditional support into `concern` (stated "
                f"limitation)")

    # E-16.1 evaluation
    detail = "; ".join(f"{f}: {len(feat[f]['voices'])}" for f in universe)
    exp_results = {
        "E-16.1": (f"distinct simulated-panel voices per feature — {detail}; features below the "
                   f"floor: {', '.join(below) if below else 'none'} (and zero REAL voices everywhere "
                   f"— see meta-gap)",
                   "not-met" if below else "met",
                   ["derived: voices-per-feature", f"src: {src}"]),
    }
    exps = C.evaluate_expectations("BQ-16", exp_results)

    lines = [
        "# BQ-16 — KOL evidence per roadmap feature (and the meta-gap)", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [config: commercial.yml]", "",
        "## Epistemic status FIRST — what this register is and is not", "",
        f"- Every row is `evidence_type: advisory-board` from the simulated 8-persona KOL panel "
        f"({sim_n} of {len(rows)} rows) [src: {src}] [derived: evidence-type-census]. These are "
        f"project-authored persona opinions, NOT collected feedback.",
        f"- Real collected evidence on file — interviews: {by_type.get('interview', 0)}, surveys: "
        f"{by_type.get('survey', 0)}, publications: {by_type.get('publication', 0)} "
        f"[derived: evidence-type-census] [src: {src}]. All roster KOLs are 'not yet contacted' "
        f"(dataset README, KOL-review finding F-1) — every per-feature figure below measures the "
        f"simulated panel only.",
        "",
        "## Voices and sentiment per feature (simulated panel)", "",
        "| Feature | Wave | Voices | Support | Neutral | Concern | Flags |",
        "|---|---|---|---|---|---|---|",
    ]
    for f in universe:
        d = feat[f]
        flags = []
        if f in below:
            flags.append("below 2-voice floor")
        if f in concern_major:
            flags.append("concern-majority")
        if f in wave_flagged:
            flags.append("no documented slot endorsement")
        lines.append(f"| {f} {names.get(f, '(no rows)')} [src: {src}] [config: commercial.yml] | "
                     f"{years[f]} | {len(d['voices'])} | {d['support']} | {d['neutral']} | "
                     f"{d['concern']} | {', '.join(flags) if flags else '—'} |")
    lines += [
        "",
        f"- Single-voice features: {', '.join(single) if single else 'none'}; zero-voice features: "
        f"{', '.join(zero) if zero else 'none'} [derived: voices-per-feature] [src: {src}].",
        "",
        "## Wave check — do the committed wave slots have documented endorsement?", "",
        f"- Rule: a concern-majority feature scheduled in a "
        f"{'/'.join(p['wave_check_years'])} slot is flagged [config: commercial.yml].",
        f"- Flagged: {', '.join(f'{f} ({years[f]})' for f in wave_flagged) if wave_flagged else 'none'} "
        f"[derived: sentiment-mix] [src: {src}] [config: commercial.yml] — read the flag as "
        f"EVIDENCE ABSENCE (concern-majority means the slot has no documented endorsement), NOT as "
        f"the panel opposing the slot; advisory only, because the sentiment is simulated (meta-gap).",
        f"- Vocabulary-flattening limitation (stated): the register's 3-value sentiment scale "
        f"(support | neutral | concern) cannot represent conditional support — per the dataset "
        f"README's mapping convention, a 'conditional yes' encodes as `concern` [src: {src}]. "
        f"Source-doc spot checks show flagged-slot concern voices that explicitly endorse the "
        f"sequencing while demanding conditions (Giuliano on F4: conditional support pending a "
        f"pre-specified suppressed-true-alarm bound; Gorski on F7: 'sequencing is right', deferral "
        f"endorsed) [src: {src}] — check the per-KOL source doc before reading any concern row as "
        f"slot opposition.",
    ]

    narrative = {"issues": [], "risks": [], "watch": []}
    narrative["issues"].append({
        "id": "I1", "severity": "high",
        "statement": f"Zero real collected KOL evidence exists behind any of the {len(universe)} "
                     f"committed roadmap features — the entire register ({sim_n} rows) is simulated "
                     f"panel material",
        "action": "Commission actual KOL engagement (interviews/advisory board) before the next "
                  "roadmap commit; re-populate the register from collected evidence and re-answer",
        "evidence": ["derived: evidence-type-census", f"src: {src}"],
    })
    if below:
        narrative["issues"].append({
            "id": "I2", "severity": "medium",
            "statement": f"{', '.join(below)} fails even the simulated-panel two-voice floor "
                         f"(E-16.1) — the weakest-evidenced committed bet(s)",
            "action": "Add voices for the below-floor feature(s) in the next engagement round, or "
                      "surface the thin base at the roadmap council",
            "evidence": ["derived: voices-per-feature", "config: commercial.yml", f"src: {src}"],
        })
    if wave_flagged:
        narrative["risks"].append({
            "id": "R1", "severity": "medium",
            "statement": f"The committed middle-wave slots ({', '.join(wave_flagged)}) carry "
                         f"concern-majority sentiment — no documented endorsement of those slots "
                         f"exists. Caveat: the 3-value vocabulary flattens conditional support into "
                         f"concern (source docs show conditional-yes voices on F4 and F7), so this "
                         f"is an evidence-absence signal, not measured opposition",
            "mitigation": "Feed the flagged features into BQ-17's composite, prioritize them in the "
                          "real-KOL engagement plan, and capture stance + timing direction (not just "
                          "3-value sentiment) when real evidence is collected",
            "evidence": ["derived: sentiment-mix", f"src: {src}", "config: commercial.yml"],
        })
    narrative["watch"].append({
        "id": "W1",
        "statement": "Voice independence is overstated by construction: all voices come from one "
                     "simulated panel session on one date — distinct kol_id is a weaker notion of "
                     "independence than E-16.1 intends",
        "evidence": [f"src: {src}"],
    })

    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Voice counts (distinct kol_id), sentiment mixes, and the evidence-type census are "
        f"measured from [src: {src}]; feature universe and wave slots from [config: commercial.yml].",
        "- Historical view: sentiment-over-time needs dated engagements across time — every current "
        "row carries the single panel date, so the history series is marked unavailable rather than "
        "faked [derived: sentiment-history].",
    ]

    data = {
        "bq": "BQ-16",
        "series": [
            {"id": "evidence-type-census", "label": "Evidence rows by type", "unit": "rows",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "row counts by evidence_type; real = interview + survey + publication",
                            "inputs": [f"src: {src}"]},
             "provenance": {"dataset": KOL_DS, "snapshot": snap},
             "points": [{"label": "real collected KOL evidence rows", "value": real_n},
                        {"label": "simulated advisory-panel rows", "value": sim_n}]},
            {"id": "voices-per-feature", "label": "Distinct voices per feature (simulated panel)",
             "unit": "voices", "evidence_class": "measured",
             "provenance": {"dataset": KOL_DS, "snapshot": snap},
             "points": [{"label": f"{f} {names.get(f, '')}".strip(), "value": len(feat[f]["voices"])}
                        for f in universe]},
            {"id": "sentiment-mix", "label": "Sentiment mix per feature (simulated panel)", "unit": "rows",
             "evidence_class": "measured",
             "provenance": {"dataset": KOL_DS, "snapshot": snap},
             "points": [{"label": f, "value": feat[f]["concern"],
                         "support": feat[f]["support"], "neutral": feat[f]["neutral"],
                         "concern": feat[f]["concern"]} for f in universe]},
            {"id": "sentiment-history", "label": "Sentiment over time", "unit": "rows",
             "kind": "timeseries", "evidence_class": "unavailable",
             "provenance": {"note": "all register rows carry the single simulated-panel date — a "
                                    "history needs dated real engagements, which do not exist yet"},
             "lines": [], "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
