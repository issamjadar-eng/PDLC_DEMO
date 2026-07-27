"""BQ-14 — PCA feature parity, line by line: roadmap-covered vs silently unaddressed.

Contract: run(corpus_root, out, pins) — see plans/BQ-14.md for the committed
definitions (attribute typing, our-status vocabulary, verdict + routing rules,
provisional flags). Deterministic from the pinned features snapshot + config.
"""

import re

import computations as C

FEAT_DS = "commercial/external-competitor-features"

CAP_PREFIXES = ("yes", "no", "planned")

DISPLAY_MAX = 80


def display_value(v):
    """Ellipsize a long cell value instead of a mid-word hard cut (F14-4)."""
    return v if len(v) <= DISPLAY_MAX else v[:DISPLAY_MAX - 1].rstrip() + "…"


def parse_numeric(value, direction, favorable=True):
    """Parse a numeric cell; a range a-b scores as the end most favorable to the
    row's owner given the direction (higher|lower). With favorable=False the
    OWNER-UNFAVORABLE end is taken instead — used for our own rows, which the
    plan commits to the competitor-favorable (conservative-against-us) end (F14-2)."""
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", value)[:2]]
    if not nums:
        return None
    take_max = (direction == "higher") if favorable else (direction != "higher")
    return max(nums) if take_max else min(nums)


def classify(feats, our_vendor, numeric_directions):
    """Per-attribute parity classification. Returns list of dicts:
    attribute, our_state, our_display, best_comp, verdict, provisional, comp_ship[]."""
    attrs = sorted({r["attribute"] for r in feats})
    out = []
    for attr in attrs:
        rows = [r for r in feats if r["attribute"] == attr]
        ours = [r for r in rows if r["vendor"] == our_vendor]
        comps = [r for r in rows if r["vendor"] != our_vendor]
        capability = any(r["value"].strip().lower().startswith(CAP_PREFIXES) for r in rows)
        provisional = any(r["verified"].strip().lower() == "verify" for r in rows)
        if capability:
            our_val = ours[0]["value"].strip().lower() if ours else None
            our_state = ("shipping" if our_val and our_val.startswith("yes")
                         else "planned" if our_val and our_val.startswith("planned")
                         else "lacking" if our_val else "undocumented")
            comp_ship = [f"{r['vendor']} {r['product']}" for r in comps
                         if r["value"].strip().lower().startswith("yes")]
            if our_state == "shipping":
                verdict = "parity" if comp_ship else "ahead"
            else:
                verdict = "behind" if comp_ship else "parity"
            best_comp = f"{len(comp_ship)} competitor product(s) shipping"
            our_display = display_value(ours[0]["value"]) if ours else "(no row — undocumented)"
        else:
            direction = numeric_directions.get(attr)
            if direction is None:
                # F14-1: a numeric attribute absent from numeric_directions must NOT
                # silently default to higher-is-better — an unmapped direction can
                # invert a verdict, so the row is surfaced unscored instead
                out.append({"attribute": attr, "our_state": "not-scored",
                            "our_display": display_value(ours[0]["value"]) if ours
                            else "(no row — undocumented)",
                            "best_comp": "not scored — direction unconfigured",
                            "verdict": "direction-unconfigured",
                            "provisional": provisional, "n_rows": len(rows)})
                continue
            # F14-2: our own rows score a range at the direction-UNFAVORABLE end
            # (competitor-favorable, per the plan); competitor rows keep their
            # owner-favorable end
            our_num = parse_numeric(ours[0]["value"], direction, favorable=False) if ours else None
            comp_nums = [(parse_numeric(r["value"], direction), r) for r in comps]
            comp_nums = [(v, r) for v, r in comp_nums if v is not None]
            if comp_nums:
                bv, br = (max(comp_nums, key=lambda t: t[0]) if direction == "higher"
                          else min(comp_nums, key=lambda t: t[0]))
            else:
                bv, br = None, None
            our_state = "documented" if our_num is not None else "undocumented"
            if our_num is None or bv is None:
                verdict = "no-comparison"
            elif (our_num > bv if direction == "higher" else our_num < bv):
                verdict = "ahead"
            elif our_num == bv:
                verdict = "parity"
            else:
                verdict = "behind"
            best_comp = (f"{br['vendor']} {br['product']} at {br['value']}" if br else "none documented")
            our_display = ours[0]["value"] if ours else "(no row — undocumented)"
        out.append({"attribute": attr, "our_state": our_state, "our_display": our_display,
                    "best_comp": best_comp, "verdict": verdict, "provisional": provisional,
                    "n_rows": len(rows)})
    return out


def run(corpus_root, out, pins):
    p = C.params_for("BQ-14")
    feats, fsnap = C.load_pin_csv(corpus_root, pins, FEAT_DS)
    src = f"{FEAT_DS}@{fsnap}"
    lane_map, lane_years = p["attribute_lane_map"], p["lane_years"]
    lane_rel = p["attribute_lane_relation"]
    results = classify(feats, p["our_vendor"], p["numeric_directions"])

    # routing of "behind" — a lane assignment is CLOSURE only when the lane ships the
    # missing capability itself (config attribute_lane_relation); otherwise it is
    # ADJACENCY: the nearest roadmap lane responds via a different mechanism (RT-14.1)
    for r in results:
        r["relation"] = None
        if r["verdict"] == "behind":
            lane = lane_map.get(r["attribute"])
            if lane:
                tag = "roadmap-committed (planned)" if r["our_state"] == "planned" else "gap on roadmap"
                rel = lane_rel.get(r["attribute"], "adjacent")
                r["relation"] = rel
                rel_txt = ("lane closes the gap" if rel == "closes"
                           else "ADJACENCY, not closure — nearest lane responds via a different mechanism")
                r["routing"] = f"{tag} — {lane}, {lane_years[lane]} ({rel_txt})"
            else:
                r["routing"] = "SILENTLY UNADDRESSED — no roadmap lane owns this gap"
        elif r["verdict"] == "direction-unconfigured":
            r["routing"] = "NOT SCORED — add the attribute to numeric_directions [config: commercial.yml]"
        else:
            r["routing"] = "—"

    # lane-mapped attributes with zero rows for anyone = matrix no-data (stated)
    present = {r["attribute"] for r in results}
    nodata = sorted(a for a in lane_map if a not in present)

    behind = [r for r in results if r["verdict"] == "behind"]
    silent = [r for r in behind if lane_map.get(r["attribute"]) is None]
    covered = [r for r in behind if lane_map.get(r["attribute"]) is not None]
    adjacent = [r for r in covered if r["relation"] != "closes"]
    ahead = [r for r in results if r["verdict"] == "ahead"]
    parity = [r for r in results if r["verdict"] == "parity"]
    provisional = [r for r in results if r["provisional"]]
    unconfigured = [r for r in results if r["verdict"] == "direction-unconfigured"]

    headline = (f"{len(results)} attributes compared: {len(ahead)} ahead, {len(parity)} parity, "
                f"{len(behind)} behind — {len(covered)} behind-gaps have a roadmap lane"
                + (f" (of which {len(adjacent)} adjacency-only: "
                   f"{', '.join(r['attribute'] for r in adjacent)} — the lane responds but does not "
                   f"mechanically close the gap)" if adjacent else "")
                + f", {len(silent)} SILENTLY UNADDRESSED"
                + (f" ({', '.join(r['attribute'] for r in silent)})" if silent else "")
                # F14-1: an unscored numeric attribute is loud, never silent
                + (f"; {len(unconfigured)} numeric attribute(s) NOT SCORED — direction unconfigured "
                   f"({', '.join(r['attribute'] for r in unconfigured)})" if unconfigured else ""))

    lines = [
        "# BQ-14 — PCA feature parity: roadmap-covered vs silently unaddressed", "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [config: commercial.yml]", "",
        "## Parity matrix (line by line)", "",
        "_Verdict rules, our-status vocabulary, and numeric directions per plans/BQ-14.md; "
        "lane routing per the attribute-lane map [config: commercial.yml]. A routed gap is labeled "
        "**closure** (the lane ships the missing capability itself) or **ADJACENCY** (the nearest "
        "lane responds via a different mechanism — the competitor's shipped capability may remain "
        "unanswered even after the lane lands), per the attribute-lane-relation config "
        "[config: commercial.yml]. `undocumented` = no "
        f"row for us in the matrix, scored conservatively as not-shipping [src: {src}]._", "",
        "| Attribute | Us | Best competitor | Verdict | Routing |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        prov = " (provisional)" if r["provisional"] else ""
        lines.append(f"| {r['attribute']} [src: {src}] [config: commercial.yml] | "
                     f"{r['our_display']} | {r['best_comp']} | {r['verdict']}{prov} | {r['routing']} |")
    lines += [
        "",
        f"- Provisional verdicts (a `verify`-flagged source cell is involved): "
        f"{', '.join(r['attribute'] for r in provisional) if provisional else 'none'} "
        f"[src: {src}] — re-confirm before any external-facing use.",
        f"- Matrix no-data: {', '.join(nodata) if nodata else 'none'} — lane-mapped but zero rows "
        f"for every vendor [src: {src}] [config: commercial.yml]; no vendor is scored on it.",
        f"- Adjacency-routed gaps ({', '.join(r['attribute'] for r in adjacent) if adjacent else 'none'}) "
        f"are NOT closed by their lanes [config: commercial.yml] [derived: parity-matrix]: the lane is "
        f"the nearest roadmap response, not a mechanical answer — treat 'gap on roadmap' for these as "
        f"'gap acknowledged', and keep them on the roadmap-council agenda alongside the silently "
        f"unaddressed one(s).",
    ]

    narrative = {"issues": [], "risks": [], "watch": []}
    for i, r in enumerate(silent, 1):
        narrative["issues"].append({
            "id": f"I{i}", "severity": "high",
            "statement": f"{r['attribute']} is behind ({r['our_display']} vs {r['best_comp']}) and NO "
                         f"roadmap lane owns the gap — silently unaddressed, nobody has decided about it",
            "action": "Put the gap on the roadmap-council agenda: accept it explicitly (documented "
                      "trade-off) or assign it a lane — silence is the only wrong state",
            "evidence": [f"src: {src}", "derived: parity-matrix", "config: commercial.yml"],
        })
    pause = next((r for r in results if r["attribute"] == "pca_pause_or_etco2"), None)
    etco2 = next((r for r in results if r["attribute"] == "integrated_etco2"), None)
    if pause and pause["verdict"] == "behind" and etco2 and etco2["verdict"] == "behind":
        narrative["risks"].append({
            "id": "R1", "severity": "high",
            "statement": f"BD ships PCA Pause and integrated EtCO2 today while our nearest roadmap "
                         f"answers sit in the F4 ({lane_years['F4']}) and F6 ({lane_years['F6']}) "
                         f"slots — and BOTH lane assignments are adjacency, not closure: F4 is smart "
                         f"alarm filtering and F6 is predictive monitoring, neither a hardware "
                         f"PCA-pause response nor a capnography module, so BD's shipped capability "
                         f"may remain unanswered even after F4/F6 land",
            "mitigation": "Feed this gap into the BQ-17 kill/pull-forward composite and the "
                          "positioning guidance: sell the connected-safety story, do not contest "
                          "PCA-pause head-to-head, and have the roadmap council decide explicitly "
                          "whether the adjacency answer is the committed answer",
            "evidence": [f"src: {src}", "derived: parity-matrix", "config: commercial.yml"],
        })
    narrative["watch"].append({
        "id": "W1",
        "statement": "Deliberate matrix absences (dataset README): our PCA-pause/EtCO2 rows, several "
                     "competitor accuracy specs, Plum Duo and Perfusor Space products — absences are "
                     "under-coverage, not verdicts; curate before the next edition",
        "evidence": [f"src: {src}"],
    })

    lines += C.expectations_section(C.evaluate_expectations("BQ-14", {}))
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- All cells measured from the curated matrix [src: {src}]; every row carries its own "
        f"source and verification flag.",
        "- Verdicts derived per the committed rules (capability vs numeric typing, range scored "
        "at the competitor-favorable end, absence scored conservatively) "
        "[derived: parity-matrix] [config: commercial.yml].",
        "- Historical view: parity-over-time needs successive curated snapshots — one snapshot "
        "exists, so the history series is marked unavailable rather than faked "
        "[derived: parity-history].",
    ]

    data = {
        "bq": "BQ-14",
        "series": [
            {"id": "parity-stat", "label": "Parity position", "unit": "attributes",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "count of per-attribute verdicts (ahead/parity/behind) and routing of behind-gaps through the attribute-lane map + attribute-lane-relation (closes vs adjacent)",
                            "inputs": [f"src: {src}", "config: commercial.yml"]},
             "provenance": {"dataset": FEAT_DS, "snapshot": fsnap},
             "points": [{"label": "attributes behind", "value": len(behind)},
                        {"label": "lane-routed but adjacency-only (lane does not close the gap)",
                         "value": len(adjacent)},
                        {"label": "silently unaddressed", "value": len(silent)}]},
            {"id": "parity-matrix", "label": "Verdict by attribute", "unit": "",
             "evidence_class": "derived",
             "derivation": {"method": "per-attribute verdict per the committed classification rules (plans/BQ-14.md)",
                            "inputs": [f"src: {src}", "config: commercial.yml"]},
             "provenance": {"dataset": FEAT_DS, "snapshot": fsnap},
             "points": [{"label": r["attribute"],
                         "value": f"{r['verdict']}{' (provisional)' if r['provisional'] else ''} — {r['routing']}"}
                        for r in results]},
            {"id": "parity-history", "label": "Parity position over time", "unit": "attributes",
             "kind": "timeseries", "evidence_class": "unavailable",
             "provenance": {"note": "one curated snapshot exists; history accumulates as the matrix "
                                    "is re-curated (180-day cadence) — a single point is not a trend"},
             "lines": [], "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": C.evaluate_expectations("BQ-14", {}),
    }
    C.write(out, lines, data)
