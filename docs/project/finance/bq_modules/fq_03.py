"""FQ-03 — cost of poor quality: warranty spend, cost per installed unit by line / hw
rev, complaint linkage, trend.

Deterministic per the FQ-03 analysis plan: YTD window = the months of the configured fy
present in the pinned warranty-claims snapshot; prior = the same months one year
earlier. Denominators for per-unit figures come ONLY from the pinned fleet registry —
lines the registry does not carry, and the PP3000 revision split it records as "-",
are published as an unavailable series, never approximated. The fleet is a
point-in-time registry applied to both windows (stated limitation).
"""

import computations as C

WC_DS = "finance/internal-warranty-claims"
FLEET_DS = "commercial/internal-fleet"
CMP_DS = "commercial/internal-complaints"
DISPOSITIONS = ("repair", "replace", "goodwill", "denied")
LINKED = ("yes", "no")
UNKNOWN_REV = "-"
TREND_LINES = 3   # lines charted individually; the rest aggregate into "other lines"


def _yoy(cur, pri):
    return 100.0 * (cur - pri) / pri if pri else None


def _fmt_yoy(v):
    return "n/a" if v is None else f"{v:+.1f}%"


def run(corpus_root, out, pins):
    p = C.params_for("FQ-03")
    fy = str(p["fy"])
    yoy_tol = float(p["per_unit_yoy_tolerance_pct"])
    conc = float(p["rev_concentration_pct"])
    ratio_t = float(p["rev_overindex_ratio"])
    wc, wsnap = C.load_pin_csv(corpus_root, pins, WC_DS)
    fleet, fsnap = C.load_pin_csv(corpus_root, pins, FLEET_DS)
    cmp_rows, csnap = C.load_pin_csv(corpus_root, pins, CMP_DS)
    wsrc, fsrc, csrc = f"{WC_DS}@{wsnap}", f"{FLEET_DS}@{fsnap}", f"{CMP_DS}@{csnap}"
    C.assert_vocab(wc, "disposition", DISPOSITIONS, WC_DS)
    C.assert_vocab(wc, "linked_complaint", LINKED, WC_DS)

    months_all = sorted({r["claim_date"][:7] for r in wc})
    ytd_months = [m for m in months_all if m.startswith(fy)]
    prior_months = [f"{int(fy) - 1}-{m[5:]}" for m in ytd_months]
    as_of = months_all[-1]
    ytd = [r for r in wc if r["claim_date"][:7] in ytd_months]
    pri = [r for r in wc if r["claim_date"][:7] in prior_months]
    window_name = f"YTD {fy} ({ytd_months[0]}..{ytd_months[-1]})"
    prior_name = f"same months {int(fy) - 1}"
    cost = lambda rows: sum(int(r["cost_usd"]) for r in rows)
    spend_c, spend_p = cost(ytd), cost(pri)
    spend_yoy = _yoy(spend_c, spend_p)
    lines_all = sorted({r["product_line"] for r in wc})

    # ---- fleet denominators (point-in-time registry)
    fleet_units = {}
    for r in fleet:
        fleet_units[(r["model"], r["hw_rev"])] = fleet_units.get((r["model"], r["hw_rev"]), 0) + 1
    fleet_line = {}
    for (m, _), n in fleet_units.items():
        fleet_line[m] = fleet_line.get(m, 0) + n
    # per-unit keys: (line, rev) where the registry carries that rev; line-level otherwise
    per_unit_keys = []
    for l in lines_all:
        if l not in fleet_line:
            continue
        revs = sorted(rv for (m, rv) in fleet_units if m == l and rv != UNKNOWN_REV)
        per_unit_keys.append((l, None))
        per_unit_keys += [(l, rv) for rv in revs]
    no_denominator = [l for l in lines_all if l not in fleet_line]
    unknown_rev_lines = sorted({m for (m, rv) in fleet_units if rv == UNKNOWN_REV})

    def per_unit(rows, line, rev):
        sub = [r for r in rows if r["product_line"] == line and (rev is None or r["hw_rev"] == rev)]
        denom = fleet_line[line] if rev is None else fleet_units[(line, rev)]
        return cost(sub) / denom if denom else None, cost(sub), len(sub), denom

    pu_rows = []
    for l, rv in per_unit_keys:
        c_pu, c_cost, c_n, denom = per_unit(ytd, l, rv)
        p_pu, _, _, _ = per_unit(pri, l, rv)
        pu_rows.append((l, rv, c_pu, p_pu, _yoy(c_pu, p_pu), c_cost, c_n, denom))

    # ---- revision concentration per line (lines with >1 revision in the claims).
    # A dominant revision always "carries" most claims — the finding is claim share vs
    # INSTALLED share (over-index ratio), computable only where the registry carries the
    # line's revision split. Elsewhere the raw share is reported as not normalizable.
    conc_rows = []   # (line, rev, claims_on_rev, line_claims, claim_share, fleet_share|None, ratio|None)
    for l in lines_all:
        sub = [r for r in ytd if r["product_line"] == l]
        revs = sorted({r["hw_rev"] for r in sub})
        if len(revs) < 2 or not sub:
            continue
        counts = {rv: sum(1 for r in sub if r["hw_rev"] == rv) for rv in revs}
        fleet_revs = {rv: n for (m, rv), n in fleet_units.items() if m == l and rv != UNKNOWN_REV}
        for rv in revs:
            share = C.pct_raw(counts[rv], len(sub))
            if fleet_revs and rv in fleet_revs:
                fshare = C.pct_raw(fleet_revs[rv], sum(fleet_revs.values()))
                conc_rows.append((l, rv, counts[rv], len(sub), share, fshare, share / fshare if fshare else None))
            else:
                conc_rows.append((l, rv, counts[rv], len(sub), share, None, None))
    over_index = sorted([r for r in conc_rows if r[6] is not None and r[6] > ratio_t], key=lambda r: -r[6])
    normalizable_lines = sorted({r[0] for r in conc_rows if r[6] is not None})
    unnormalized = sorted([r for r in conc_rows if r[6] is None and r[4] > conc], key=lambda r: -r[4])
    top_conc = over_index[0] if over_index else (unnormalized[0] if unnormalized else None)

    # ---- complaint linkage
    linked = [r for r in ytd if r["linked_complaint"] == "yes"]
    link_share = C.pct_raw(len(linked), len(ytd))
    link_rows = []
    for l in lines_all:
        sub = [r for r in ytd if r["product_line"] == l]
        link_rows.append((l, sum(1 for r in sub if r["linked_complaint"] == "yes"), len(sub)))
    cmp_ytd = [r for r in cmp_rows if r["date_opened"][:7] in ytd_months]
    cmp_ctx = []
    for l in sorted(fleet_line):
        n_cmp = sum(1 for r in cmp_ytd if r["model"] == l)
        n_link = sum(1 for r in linked if r["product_line"] == l)
        cmp_ctx.append((l, n_link, n_cmp))

    # ---- disposition mix + rev-B categories + monthly trend
    disp = {d: cost([r for r in ytd if r["disposition"] == d]) for d in DISPOSITIONS}
    disp_n = {d: sum(1 for r in ytd if r["disposition"] == d) for d in DISPOSITIONS}
    def categories(line, rev):
        sub = [r for r in ytd if r["product_line"] == line and r["hw_rev"] == rev]
        cats = sorted({r["failure_category"] for r in sub})
        return sorted(((c, sum(1 for r in sub if r["failure_category"] == c)) for c in cats),
                      key=lambda t: (-t[1], t[0]))

    cat_rows = categories(top_conc[0], top_conc[1]) if top_conc else []
    focus_revs = over_index + unnormalized   # every concentrated revision gets its categories listed
    line_cost_all = {l: cost([r for r in wc if r["product_line"] == l]) for l in lines_all}
    top_lines = [l for l, _ in sorted(line_cost_all.items(), key=lambda t: (-t[1], t[0]))[:TREND_LINES]]
    other = [l for l in lines_all if l not in top_lines]

    def monthly(lines_):
        return [{"x": C.month_iso(m), "y": C.kusd(cost([r for r in wc if r["product_line"] in lines_ and r["claim_date"][:7] == m]))}
                for m in months_all]

    trend = [{"label": l, "points": monthly([l])} for l in top_lines]
    if other:
        trend.append({"label": "other lines (" + "+".join(other) + ")", "points": monthly(other)})

    # ---- expectations
    pp3500 = next((r for r in pu_rows if r[0] == "PP3500" and r[1] is None), None)
    if pp3500 and pp3500[4] is not None:
        e1 = (f"PP3500 ${pp3500[2]:.0f}/unit {window_name} vs ${pp3500[3]:.0f} {prior_name} ({_fmt_yoy(pp3500[4])})",
              "met" if pp3500[4] <= yoy_tol else "not-met", ["derived: cost-per-unit-yoy"])
    else:
        e1 = ("PP3500 per-unit cost not computable (no fleet denominator or no prior-year claims)",
              "not-evaluable", ["derived: per-unit-unavailable"])
    e2_txt = (f"{len(over_index)} revision(s) over {ratio_t:.2f}× on {len(normalizable_lines)} normalizable line(s)"
              + (": " + ", ".join(f"{l} rev {rv} {s:.0f}% of claims vs {fs:.0f}% of fleet ({ra:.2f}×)"
                                  for l, rv, _, _, s, fs, ra in over_index) if over_index else ""))
    if unnormalized:
        e2_txt += ("; not normalizable (no registry revision split): "
                   + ", ".join(f"{l} rev {rv} {s:.0f}% of claims ({n} of {t})" for l, rv, n, t, s, _, _ in unnormalized))
    e2 = (e2_txt, "met" if not over_index else "not-met",
          ["derived: revision-concentration", "derived: cost-per-unit-by-rev"])
    exps = C.evaluate_expectations("FQ-03", {"E-03.1": e1, "E-03.2": e2})

    # ---- verdict (rollup-survival: spend, per-unit, concentration, linkage all on the headline)
    parts = [f"{window_name} warranty spend ${C.kusd(spend_c)}K vs ${C.kusd(spend_p)}K {prior_name} ({_fmt_yoy(spend_yoy)})"]
    pu_bits = []
    for l, rv, c, _, y, _, _, _ in pu_rows:
        if rv is None and c is not None:
            revs = [f"rev {r2} ${c2:.0f} ({_fmt_yoy(y2)})" for l2, r2, c2, _, y2, _, _, _ in pu_rows if l2 == l and r2 is not None]
            pu_bits.append(f"{l} ${c:.0f} ({_fmt_yoy(y)} YoY" + ("; " + ", ".join(revs) if revs else "") + ")")
    if pu_bits:
        parts.append("per installed unit: " + ", ".join(pu_bits))
    if over_index:
        parts.append("over-indexing revisions: " + ", ".join(
            f"{l} rev {rv} {s:.0f}% of claims vs {fs:.0f}% of fleet ({ra:.2f}×)" for l, rv, _, _, s, fs, ra in over_index))
    else:
        parts.append(f"no revision over-indexes beyond {ratio_t:.2f}× its installed share on the "
                     f"{len(normalizable_lines)} normalizable line(s)")
    if unnormalized:
        parts.append("not normalizable (registry carries no revision split): " + ", ".join(
            f"{l} rev {rv} {s:.0f}% of claims ({n} of {t})" for l, rv, n, t, s, _, _ in unnormalized))
    parts.append(f"{link_share:.0f}% of claims link to a complaint ({len(linked)} of {len(ytd)})")
    if no_denominator:
        parts.append("per-unit unavailable for " + ", ".join(no_denominator) + " (no fleet denominator)")
    headline = "; ".join(parts)

    # ---- narrative
    narrative = {"issues": [], "risks": [], "watch": []}
    n_i = 0
    for l, rv, n, t, s, fs, ra in over_index:
        n_i += 1
        cr = categories(l, rv)
        top_cat = f"; top failure category {cr[0][0]} ({cr[0][1]} claims)" if cr else ""
        pu = next((r for r in pu_rows if r[0] == l and r[1] == rv), None)
        pu_txt = f"; ${pu[2]:.0f} per installed unit {window_name}" if pu else ""
        narrative["issues"].append({
            "id": f"I{n_i}", "severity": "high" if ra > 2 * ratio_t else "medium",
            "statement": f"{l} hardware rev {rv} over-indexes on warranty: {s:.0f}% of the line's {window_name} "
                         f"claims ({n} of {t}) vs {fs:.0f}% of the installed fleet ({ra:.2f}×){pu_txt}{top_cat}",
            "action": "Open a design-signal review on the revision; decide field action vs revision-specific "
                      "service bulletin with quality and regulatory",
            "evidence": ["derived: revision-concentration", "derived: revision-failure-categories",
                         "derived: cost-per-unit-by-rev", f"src: {wsrc}", f"src: {fsrc}", C.CONFIG_MARKER],
        })
    for l, rv, n, t, s, _, _ in unnormalized:
        n_i += 1
        cr = categories(l, rv)
        top_cat = f"; top failure category {cr[0][0]} ({cr[0][1]} claims)" if cr else ""
        narrative["issues"].append({
            "id": f"I{n_i}", "severity": "medium",
            "statement": f"{l} hardware rev {rv} carries {s:.0f}% of the line's {window_name} claims ({n} of {t})"
                         f"{top_cat} — the registry records no {l} revision, so this cannot be normalized to the "
                         "installed mix",
            "action": "Add the hardware revision to the fleet registry export for the line, then re-test the "
                      "over-index; meanwhile treat the cluster as a design-signal review candidate",
            "evidence": ["derived: revision-concentration", "derived: revision-failure-categories",
                         "derived: per-unit-unavailable", f"src: {wsrc}", f"src: {fsrc}", C.CONFIG_MARKER],
        })
    for l, rv, c, pv, y, _, _, _ in pu_rows:
        if rv is None and y is not None and y > yoy_tol:
            n_i += 1
            narrative["issues"].append({
                "id": f"I{n_i}", "severity": "medium",
                "statement": f"{l} warranty cost per installed unit ${c:.0f} {window_name} vs ${pv:.0f} "
                             f"{prior_name} ({_fmt_yoy(y)}) — beyond the {yoy_tol:.0f}% tolerance",
                "action": "Re-test the warranty reserve for the line against the observed per-unit trend (FQ-04) "
                          "and review end-of-life timing",
                "evidence": ["derived: cost-per-unit-yoy", f"src: {wsrc}", f"src: {fsrc}", C.CONFIG_MARKER],
            })
    narrative["risks"].append({
        "id": "R1", "severity": "medium",
        "statement": "Per-unit figures use the fleet registry as a point-in-time denominator for both windows — "
                     "a fleet that grew over the year makes prior-year per-unit costs look lower than they were",
        "mitigation": "Pin a fleet snapshot per window once recurring fleet snapshots exist; until then read "
                      "per-unit YoY as directional",
        "evidence": [f"src: {fsrc}", "derived: cost-per-unit-yoy"],
    })
    if disp["replace"] > disp["repair"]:
        narrative["risks"].append({
            "id": "R2", "severity": "medium",
            "statement": f"Replacements (${C.kusd(disp['replace'])}K) outspend repairs (${C.kusd(disp['repair'])}K) "
                         f"{window_name} — cost per claim is being driven by the replace share",
            "mitigation": "Depot-repair capacity review for the lines driving replacements",
            "evidence": ["derived: disposition-mix", f"src: {wsrc}"],
        })
    narrative["watch"].append({
        "id": "W1",
        "statement": f"{100.0 - link_share:.0f}% of warranty claims ({len(ytd) - len(linked)} of {len(ytd)}) have no "
                     "linked complaint — warranty activity the complaint-handling system is not trending",
        "evidence": ["derived: complaint-linkage", f"src: {wsrc}", f"src: {csrc}"],
    })
    if no_denominator or unknown_rev_lines:
        narrative["watch"].append({
            "id": "W2",
            "statement": "Per-unit gaps: " + ", ".join(no_denominator) + " have no fleet registry rows"
                         + (("; " + ", ".join(unknown_rev_lines) + " revision recorded as unknown in the registry")
                            if unknown_rev_lines else ""),
            "evidence": ["derived: per-unit-unavailable", f"src: {fsrc}"],
        })

    lines = [
        "# FQ-03 — Cost of poor quality: warranty spend, per-unit cost, complaint linkage", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {wsrc}] [src: {fsrc}] [src: {csrc}] [{C.CONFIG_MARKER}]", "",
        "## Warranty spend — YTD vs prior year", "",
        f"_Window: claims dated {ytd_months[0]}..{ytd_months[-1]} (as-of {as_of} in the pin) vs "
        f"{prior_months[0]}..{prior_months[-1]} [src: {wsrc}]; tolerances [{C.CONFIG_MARKER}]._", "",
        "| Window | Claims | Spend $K | Repair $K | Replace $K | Goodwill $K |",
        "|---|---|---|---|---|---|",
        f"| {window_name} [src: {wsrc}] | {len(ytd)} | {C.kusd(spend_c)} | {C.kusd(disp['repair'])} | "
        f"{C.kusd(disp['replace'])} | {C.kusd(disp['goodwill'])} |",
        f"| {prior_name} [src: {wsrc}] | {len(pri)} | {C.kusd(spend_p)} | "
        f"{C.kusd(cost([r for r in pri if r['disposition'] == 'repair']))} | "
        f"{C.kusd(cost([r for r in pri if r['disposition'] == 'replace']))} | "
        f"{C.kusd(cost([r for r in pri if r['disposition'] == 'goodwill']))} |",
        "",
        "## Warranty cost per installed unit — by line and hardware revision", "",
        f"_Denominator = devices in the pinned fleet registry per model / hw_rev [src: {fsrc}] (point-in-time, "
        f"applied to both windows); numerator = claim cost in the window [src: {wsrc}]._", "",
        "| Line / rev | Installed units | Claims YTD | Spend YTD $K | $ per unit YTD | $ per unit prior | YoY |",
        "|---|---|---|---|---|---|---|",
    ]
    for l, rv, c, pv, y, cc, n, denom in pu_rows:
        label = l if rv is None else f"{l} rev {rv}"
        flag = " ⚠️" if (rv is None and y is not None and y > yoy_tol) else ""
        lines.append(f"| {label} [src: {wsrc}] [src: {fsrc}] | {denom} | {n} | {C.kusd(cc)} | "
                     f"{c:.0f} | {'n/a' if pv is None else f'{pv:.0f}'} | {_fmt_yoy(y)}{flag} |")
    lines += [
        "",
        "## Per-unit gaps: not computable (stated, not approximated)", "",
        f"- No fleet registry rows for {', '.join(no_denominator) if no_denominator else 'none'} [src: {fsrc}] — "
        "their spend is reported in dollars only [derived: per-unit-unavailable].",
    ]
    if unknown_rev_lines:
        lines.append(f"- The registry records {', '.join(unknown_rev_lines)} hw_rev as unknown [src: {fsrc}], while "
                     f"the claims carry a revision [src: {wsrc}] — per-unit by revision is unavailable for "
                     "those lines; claim share by revision is reported instead.")
    lines += [
        "",
        "## Revision concentration — claim share vs installed share", "",
        f"_Every revision of a line with more than one revision in the window's claims [src: {wsrc}]. Over-index = "
        f"claim share ÷ installed share from the registry [src: {fsrc}], flagged beyond {ratio_t:.2f}×; where the "
        f"registry carries no revision split the raw claim share is shown and flagged beyond {conc:.0f}% as "
        f"not normalizable [{C.CONFIG_MARKER}]._", "",
        "| Line / rev | Claims | Line claims | Claim share | Installed share | Over-index |",
        "|---|---|---|---|---|---|",
    ]
    for l, rv, n, t, s, fs, ra in conc_rows:
        if ra is not None:
            flag = " ⚠️" if ra > ratio_t else ""
            lines.append(f"| {l} rev {rv} [src: {wsrc}] [src: {fsrc}] | {n} | {t} | {s:.0f}% | {fs:.0f}% | {ra:.2f}×{flag} |")
        else:
            flag = " ⚠️ not normalizable" if s > conc else ""
            lines.append(f"| {l} rev {rv} [src: {wsrc}] [src: {fsrc}] | {n} | {t} | {s:.0f}%{flag} | n/a | n/a |")
    for l, rv, _, _, _, _, _ in focus_revs:
        cr = categories(l, rv)
        if cr:
            lines += ["", f"Failure categories for {l} rev {rv} ({window_name}) [src: {wsrc}]: "
                      + ", ".join(f"{c} {n}" for c, n in cr) + " [derived: revision-failure-categories]."]
    lines += [
        "",
        "## Complaint linkage", "",
        "| Line | Claims linked to a complaint | Line claims | Linked share |",
        "|---|---|---|---|",
    ]
    for l, n, t in link_rows:
        lines.append(f"| {l} [src: {wsrc}] | {n} | {t} | {C.pct(n, t):.0f}% |")
    lines += [
        "",
        f"For the lines the fleet registry carries, complaints logged in the same window [src: {csrc}] vs "
        f"warranty claims linked to a complaint [src: {wsrc}]: "
        + "; ".join(f"{l} {nl} linked claims vs {nc} complaints" for l, nl, nc in cmp_ctx)
        + " [derived: complaints-context].",
    ]
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Claim cost summed from [src: {wsrc}]; windows matched month-for-month; per-unit denominators from "
        f"[src: {fsrc}] only; complaint counts from [src: {csrc}]; thresholds [{C.CONFIG_MARKER}].",
        f"- Historical view: monthly warranty cost by line over the full claims history is charted "
        f"[derived: monthly-cost-trend] [src: {wsrc}]; disposition mix [derived: disposition-mix].",
        "- Verdict and expectation actuals carry the per-unit, concentration, and linkage figures so a rollup "
        "cannot drop them [derived: v-main].",
    ]

    data = {
        "bq": "FQ-03",
        "series": [
            {"id": "warranty-spend-stat", "label": "Warranty spend YTD", "unit": "USD K", "kind": "stat",
             "evidence_class": "derived",
             "derivation": {"method": "Σ cost_usd over claims dated in the fiscal-year months present in the pin; prior = same months one year earlier",
                            "inputs": [f"src: {wsrc}", C.CONFIG_MARKER]},
             "provenance": {"dataset": WC_DS, "snapshot": wsnap},
             "points": [{"label": f"{window_name} spend", "value": C.kusd(spend_c),
                         "sub": f"{prior_name} ${C.kusd(spend_p)}K ({_fmt_yoy(spend_yoy)}); {len(ytd)} claims"}]},
            {"id": "cost-per-unit-by-rev", "label": "Warranty cost per installed unit YTD", "unit": "USD",
             "evidence_class": "derived",
             "derivation": {"method": "Σ claim cost (window) ÷ fleet-registry device count per model / hw_rev",
                            "inputs": [f"src: {wsrc}", f"src: {fsrc}"]},
             "provenance": {"datasets": [{"dataset": WC_DS, "snapshot": wsnap}, {"dataset": FLEET_DS, "snapshot": fsnap}]},
             "points": [{"label": l if rv is None else f"{l} rev {rv}", "value": round(c, 0), "units": denom, "claims": n}
                        for l, rv, c, _, _, _, n, denom in pu_rows]},
            {"id": "cost-per-unit-yoy", "label": "Per-unit warranty cost: YTD vs prior year", "unit": "USD",
             "kind": "paired-bars", "pairs": {"a_label": window_name, "b_label": prior_name},
             "evidence_class": "derived",
             "derivation": {"method": "per-unit cost (as above) for the window and the prior-year months, same denominator",
                            "inputs": [f"src: {wsrc}", f"src: {fsrc}"]},
             "provenance": {"datasets": [{"dataset": WC_DS, "snapshot": wsnap}, {"dataset": FLEET_DS, "snapshot": fsnap}]},
             "points": [{"label": l if rv is None else f"{l} rev {rv}", "a": round(c, 0),
                         "b": round(pv, 0) if pv is not None else None,
                         "yoy_pct": round(y, 1) if y is not None else None} for l, rv, c, pv, y, _, _, _ in pu_rows]},
            {"id": "monthly-cost-trend", "label": "Monthly warranty cost by line", "unit": "USD K",
             "kind": "timeseries", "evidence_class": "derived",
             "derivation": {"method": "Σ cost_usd per claim month per product line over the full log; smaller lines aggregated",
                            "inputs": [f"src: {wsrc}"]},
             "provenance": {"dataset": WC_DS, "snapshot": wsnap},
             "lines": trend, "points": []},
            {"id": "disposition-mix", "label": "Warranty spend by disposition (YTD)", "unit": "USD K",
             "evidence_class": "derived",
             "derivation": {"method": "Σ cost_usd per disposition over the window", "inputs": [f"src: {wsrc}"]},
             "provenance": {"dataset": WC_DS, "snapshot": wsnap},
             "points": [{"label": d, "value": C.kusd(disp[d]), "claims": disp_n[d]} for d in DISPOSITIONS]},
            {"id": "revision-concentration", "label": "Claim share vs installed share by revision (YTD)", "unit": "%",
             "kind": "paired-bars", "pairs": {"a_label": "share of line claims", "b_label": "share of installed fleet"},
             "evidence_class": "derived",
             "derivation": {"method": "per line with >1 revision: claims on the revision ÷ line claims, vs registry devices on the revision ÷ registry devices of the line (null where the registry carries no split)",
                            "inputs": [f"src: {wsrc}", f"src: {fsrc}", C.CONFIG_MARKER]},
             "provenance": {"datasets": [{"dataset": WC_DS, "snapshot": wsnap}, {"dataset": FLEET_DS, "snapshot": fsnap}]},
             "points": [{"label": f"{l} rev {rv}", "a": round(s, 1), "b": round(fs, 1) if fs is not None else None,
                         "over_index": round(ra, 2) if ra is not None else None} for l, rv, _, _, s, fs, ra in conc_rows]},
            {"id": "revision-failure-categories",
             "label": (f"Failure categories — {top_conc[0]} rev {top_conc[1]} (YTD)" if top_conc else "Failure categories — concentrated revision"),
             "unit": "claims", "evidence_class": "derived",
             "derivation": {"method": "claim count per failure_category for the most over-indexed revision (or the largest not-normalizable concentration)",
                            "inputs": [f"src: {wsrc}", f"src: {fsrc}", C.CONFIG_MARKER]},
             "provenance": {"datasets": [{"dataset": WC_DS, "snapshot": wsnap}, {"dataset": FLEET_DS, "snapshot": fsnap}]},
             "points": [{"label": c, "value": n} for c, n in cat_rows]},
            {"id": "complaint-linkage", "label": "Share of claims linked to a complaint (YTD)", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "claims with linked_complaint = yes ÷ claims, per product line, over the window",
                            "inputs": [f"src: {wsrc}"]},
             "provenance": {"dataset": WC_DS, "snapshot": wsnap},
             "points": [{"label": l, "value": C.pct(n, t), "linked": n, "claims": t} for l, n, t in link_rows]},
            {"id": "complaints-context", "label": "Linked claims vs complaints logged (YTD)", "unit": "records",
             "kind": "paired-bars", "pairs": {"a_label": "warranty claims linked to a complaint", "b_label": "complaints logged"},
             "evidence_class": "derived",
             "derivation": {"method": "per fleet model: linked claims in the window vs complaints opened in the same months",
                            "inputs": [f"src: {wsrc}", f"src: {csrc}"]},
             "provenance": {"datasets": [{"dataset": WC_DS, "snapshot": wsnap}, {"dataset": CMP_DS, "snapshot": csnap}]},
             "points": [{"label": l, "a": nl, "b": nc} for l, nl, nc in cmp_ctx]},
            {"id": "per-unit-unavailable", "label": "Per-unit cost — lines / revisions without a fleet denominator",
             "unit": "USD", "evidence_class": "unavailable",
             "provenance": {"note": "the fleet registry (internal-fleet) carries no " + ", ".join(no_denominator)
                                    + " devices and records " + ", ".join(unknown_rev_lines) + " hw_rev as unknown; "
                                    "per-unit figures need those populations in the registry export."},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
