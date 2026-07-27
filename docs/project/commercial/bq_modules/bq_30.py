"""BQ-30 — cost per update, remote vs on-site, and the remote-first adapter case.

Deterministic per the BQ-30 analysis plan, worked from what the campaign rows actually
carry (status, method, completed_date, duration_min — NO per-attempt timestamps, NO
retry counts, NO travel fields). On-site cost is therefore published as a BOUNDED range
(labor-time floor ↔ full-day ceiling), never a single "fully loaded" number; the true
figure is an unavailable series until FSE travel/roster data exists.
"""

import computations as C

CAMP_DS = "commercial/internal-upgrade-campaign"
FLEET_DS = "commercial/internal-fleet"


def run(corpus_root, out, pins):
    p = C.params_for("BQ-30")
    rate = float(p["fse_day_rate_usd"])
    remote_cost = float(p["remote_session_cost_usd"])
    adapter = float(p["adapter_unit_cost_usd"])
    top_n = int(p["top_n_accounts"])
    day_min = int(p["fse_day_minutes"])
    rows, snap = C.load_pin_csv(corpus_root, pins, CAMP_DS)
    fleet, fsnap = C.load_pin_csv(corpus_root, pins, FLEET_DS)
    src, fsrc = f"{CAMP_DS}@{snap}", f"{FLEET_DS}@{fsnap}"
    conn = {r["device_serial"]: r["connected"] for r in fleet}

    comp = [r for r in rows if r["status"] in C.COMPLETED]
    by_m = {m: [r for r in comp if r["method"] == m] for m in ("remote", "onsite")}
    mean_dur = {m: (round(sum(int(r["duration_min"]) for r in v if r["duration_min"])
                          / len([r for r in v if r["duration_min"]]), 1) if v else 0.0)
                for m, v in by_m.items()}
    retried = {m: sum(1 for r in v if r["status"] == "completed-after-retry")
               for m, v in by_m.items()}
    onsite_floor = round(mean_dur["onsite"] / day_min * rate, 2)
    onsite_ceiling = rate
    ratio_at_floor = C.pct(remote_cost, onsite_floor)      # worst case for the expectation
    ratio_at_ceiling = C.pct(remote_cost, onsite_ceiling)  # best case
    # E-30.1 deterministic bound rule (see the plan)
    if remote_cost <= 0.25 * onsite_floor:
        e301 = "met"
    elif remote_cost > 0.25 * onsite_ceiling:
        e301 = "not-met"
    else:
        e301 = "at-risk"
    saving_floor = round(onsite_floor - remote_cost, 2)
    saving_ceiling = round(onsite_ceiling - remote_cost, 2)
    payback_floor = round(adapter / saving_floor, 1) if saving_floor > 0 else None
    payback_ceiling = round(adapter / saving_ceiling, 1) if saving_ceiling > 0 else None

    # method ↔ connectivity alignment (join check, reported not assumed)
    align = {m: {"total": len(v),
                 "expected": sum(1 for r in v
                                 if conn.get(r["device_serial"]) == ("yes" if m == "remote" else "no"))}
             for m, v in by_m.items()}

    # adapter case: top non-connected accounts (PP3500, fleet registry)
    nc_by_site = {}
    for r in fleet:
        if r["model"] == "PP3500" and r["connected"] == "no":
            nc_by_site[r["site_id"]] = nc_by_site.get(r["site_id"], 0) + 1
    ranked = sorted(nc_by_site.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n]
    top_devices = sum(n for _, n in ranked)
    top_capex = round(top_devices * adapter)
    top_onsite_floor = round(top_devices * onsite_floor)
    top_onsite_ceiling = round(top_devices * onsite_ceiling)
    top_remote = round(top_devices * remote_cost)

    # finishing the CURRENT campaign: on-site remaining vs a converted alternative
    rem = [r for r in rows if r["status"] not in C.COMPLETED]
    onsite_rem = sum(1 for r in rem if r["method"] == "onsite")
    fin_floor = round(onsite_rem * onsite_floor)
    fin_ceiling = round(onsite_rem * onsite_ceiling)
    fin_convert = round(onsite_rem * (adapter + remote_cost))
    # Within-campaign breakeven (red-team finding F30-1): conversion wins wherever the
    # true on-site cost per update exceeds adapter + remote session — state WHERE that
    # point sits in the floor–ceiling bound instead of a directional adverb.
    breakeven = round(adapter + remote_cost)
    # Breakeven position clamped to [0, 100]; the sentence branches when breakeven
    # falls outside the bound or the bound is degenerate — an unclamped position would
    # render negative / >100 "position in the bound" nonsense (review finding F-30-2).
    bound_width = onsite_ceiling - onsite_floor
    be_pos = min(100.0, max(0.0, C.pct(breakeven - onsite_floor, bound_width)))
    if bound_width > 0 and onsite_floor < breakeven < onsite_ceiling:
        be_clause = (f"a point {be_pos}% of the way up the ${onsite_floor:.0f}–"
                     f"${onsite_ceiling:.0f} bound, so conversion wins across the upper "
                     f"{round(100 - be_pos, 1)}% of it")
    elif bound_width > 0 and breakeven <= onsite_floor:
        be_clause = (f"a point at or below the ${onsite_floor:.0f} floor of the bound, so "
                     f"conversion wins across the whole bound")
    elif bound_width > 0:
        be_clause = (f"a point at or above the ${onsite_ceiling:.0f} ceiling of the bound, so "
                     f"conversion wins nowhere in the bound")
    else:
        be_clause = (f"a bound that is degenerate (floor equals ceiling at "
                     f"${onsite_floor:.0f}), so no position within it exists")

    # Payback rendering guarded — with saving ≤ 0 the payback is None and must render
    # as an explicit no-payback clause, never "None–None campaigns" (finding F-30-1).
    if payback_floor is not None:
        payback_clause = (f"a ${adapter:.0f} adapter pays back in "
                          f"{payback_ceiling}–{payback_floor} update campaigns at the top "
                          f"non-connected accounts")
    elif payback_ceiling is not None:
        payback_clause = (f"a ${adapter:.0f} adapter pays back only toward the travel-heavy end "
                          f"of the bound ({payback_ceiling} campaigns at the full-day ceiling; "
                          f"no payback at the labor floor, where remote does not undercut "
                          f"on-site)")
    else:
        payback_clause = (f"a ${adapter:.0f} adapter has NO payback at this bound — the remote "
                          f"session rate does not undercut on-site at either end")

    headline = (f"A remote update costs ${remote_cost:.0f} vs an on-site update between "
                f"${onsite_floor:.0f} (labor-time floor) and ${onsite_ceiling:.0f} (full-day "
                f"ceiling) — remote is {ratio_at_ceiling}–{ratio_at_floor}% of on-site depending "
                f"on unmeasured travel; {payback_clause}")

    # narrative — deterministic from computed facts
    narrative = {"issues": [], "risks": [], "watch": []}
    narrative["risks"].append({
        "id": "R1", "severity": "high",
        "statement": f"The fully-loaded on-site cost is unresolvable from campaign data — the "
                     f"${onsite_floor:.0f}–${onsite_ceiling:.0f} bound spans {ratio_at_ceiling}% "
                     f"to {ratio_at_floor}% on the remote-vs-onsite ratio, and "
                     + (f"the adapter payback spans {payback_ceiling} to {payback_floor} "
                        f"campaigns" if payback_floor is not None else
                        "the adapter payback is undefined across part or all of it (remote does "
                        "not undercut on-site everywhere in the bound)")
                     + " — the remote-first decision flips inside that band",
        "mitigation": "Acquire FSE travel/visit data (the same roster dataset BQ-26 needs) to "
                      "collapse the bound before committing adapter capex",
        "evidence": ["derived: onsite-cost-bounds", "derived: adapter-payback",
                     "derived: fully-loaded-onsite"],
    })
    narrative["risks"].append({
        "id": "R2", "severity": "medium",
        "statement": f"All three cost rates are demo stand-ins, not finance-validated "
                     f"(FSE day ${rate:.0f}, remote session ${remote_cost:.0f}, adapter "
                     f"${adapter:.0f}) — and the remote figure is a floor: "
                     f"{retried['remote']} remote and {retried['onsite']} on-site completions "
                     "needed a retry whose extra sessions the data does not count",
        "mitigation": "Have finance validate the rates and add per-attempt session counts to the "
                      "campaign export; mark E-30.1 validated when done",
        "evidence": ["config: commercial.yml", f"src: {src}"],
    })
    # Remote-convertible share of the on-site backlog computed from THIS module's own
    # pins (same device_serial↔connected join used for completions) instead of quoting
    # BQ-26's number as a literal (review finding F-30-3); the BQ-26 pointer stays.
    rem_convertible = sum(1 for r in rem
                          if r["method"] == "onsite" and conn.get(r["device_serial"]) == "yes")
    conv_word = "zero" if rem_convertible == 0 else str(rem_convertible)
    narrative["watch"].append({
        "id": "W1",
        "statement": f"Finishing the current campaign's {onsite_rem} on-site-remaining devices "
                     f"costs ${fin_floor:,}–${fin_ceiling:,} on-site vs ${fin_convert:,} to "
                     f"adapter-convert and run remote — within this campaign conversion breaks "
                     f"even where on-site cost exceeds ${breakeven}/update (adapter + remote "
                     f"session), {be_clause} — and the adapters persist for every "
                     f"future campaign ({conv_word} of the {onsite_rem} on-site-remaining "
                     f"device(s) are remote-convertible today per this pin — see BQ-26)",
        "evidence": ["derived: finish-current-campaign", "derived: onsite-cost-bounds",
                     f"src: {src}", f"src: {fsrc}", "config: commercial.yml"],
    })

    exp_results = {
        "E-30.1": (f"remote ${remote_cost:.0f} = {ratio_at_floor}% of the on-site labor floor "
                   f"(${onsite_floor:.0f}) but {ratio_at_ceiling}% of the full-day ceiling "
                   f"(${onsite_ceiling:.0f}) — the ≤25% test depends on the unmeasured travel "
                   "component",
                   e301,
                   ["derived: cost-per-update", "derived: onsite-cost-bounds"]),
    }
    exps = C.evaluate_expectations("BQ-30", exp_results)

    lines = [
        "# BQ-30 — Cost per update: remote vs on-site, and the remote-first case", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [src: {fsrc}] "
        f"[config: commercial.yml]", "",
        "## Cost per completed update", "",
        f"_What the campaign rows carry: status, method, completed_date, duration_min, tickets — "
        f"no per-attempt timestamps, no retry counts, no travel fields [src: {src}]. Costing "
        f"works from that; what it cannot support is bounded or marked unavailable, never "
        f"guessed._", "",
        "| Method | Completed | Mean hands-on min | Cost per update | Basis |",
        "|---|---|---|---|---|",
        f"| remote [derived: cost-per-update] [src: {src}] [config: commercial.yml] | "
        f"{len(by_m['remote'])} | {mean_dur['remote']} | ${remote_cost:.0f} | flat session rate "
        f"(floor — retry sessions uncounted) |",
        f"| on-site [derived: cost-per-update] [src: {src}] [config: commercial.yml] | "
        f"{len(by_m['onsite'])} | {mean_dur['onsite']} | ${onsite_floor:.0f}–"
        f"${onsite_ceiling:.0f} | labor-time floor ↔ full-day ceiling (travel unmeasured) |",
        "",
        f"- On-site floor = mean hands-on duration {mean_dur['onsite']} min ÷ {day_min} min/day × "
        f"${rate:.0f}/day; ceiling = one FSE day per visit [derived: onsite-cost-bounds] "
        f"[src: {src}] [config: commercial.yml]",
        f"- Method↔connectivity join check: {align['remote']['expected']} of "
        f"{align['remote']['total']} remote completions are on connected devices and "
        f"{align['onsite']['expected']} of {align['onsite']['total']} on-site completions are on "
        f"unconnected devices [derived: method-connectivity] [src: {src}] [src: {fsrc}]",
        f"- Weekly completions by method are charted [derived: weekly-by-method] [src: {src}]",
        "",
        "## Remote-first business case — adapters at the top non-connected accounts", "",
        f"_Top {len(ranked)} accounts by non-connected PP3500 count (all accounts with any, "
        f"capped at {top_n} [config: commercial.yml]): {top_devices} devices "
        f"[derived: adapter-case] [src: {fsrc}]._", "",
        "| Site | Non-connected PP3500 | Adapter capex | On-site cost per campaign (floor–ceiling) |",
        "|---|---|---|---|",
    ]
    for s, n in ranked[:10]:
        lines.append(f"| {s} [derived: adapter-case] [src: {fsrc}] [config: commercial.yml] | {n} | "
                     f"${round(n * adapter):,} | ${round(n * onsite_floor):,}–"
                     f"${round(n * onsite_ceiling):,} |")
    lines += [
        f"| _…total, top {len(ranked)} accounts_ [derived: adapter-case] [src: {fsrc}] "
        f"[config: commercial.yml] | {top_devices} | ${top_capex:,} | ${top_onsite_floor:,}–"
        f"${top_onsite_ceiling:,} |",
        "",
        ("- Payback per device: ${:.0f} adapter ÷ (on-site − remote per-update saving) = "
         "{} campaigns at the labor floor, {} at the full-day ceiling "
         "[derived: adapter-payback] [config: commercial.yml]"
         .format(adapter, payback_floor, payback_ceiling) if payback_floor is not None else
         (f"- Payback per device: no payback at the labor floor — remote (${remote_cost:.0f}) "
          f"does not undercut the on-site floor (${onsite_floor:.0f})"
          + (f"; at the full-day ceiling the ${adapter:.0f} adapter pays back in "
             f"{payback_ceiling} campaigns" if payback_ceiling is not None else
             f" or the full-day ceiling (${onsite_ceiling:.0f}) — the adapter never pays back "
             f"on update-labor savings alone")
          + " [derived: adapter-payback] [config: commercial.yml]")),
        f"- Once converted, each campaign over the top accounts runs ${top_remote:,} remote vs "
        f"${top_onsite_floor:,}–${top_onsite_ceiling:,} on-site [derived: adapter-case] "
        f"[config: commercial.yml]",
        f"- No campaign-frequency figure exists in any dataset, so payback is stated per update "
        f"campaign — never annualized [derived: adapter-payback]",
    ]
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Data gap (stated, not papered over)", "",
        "- Travel and overhead per on-site visit, FSE roster/day structure, and per-attempt",
        "  session counts are not in any corpus dataset — the true fully-loaded on-site cost is",
        "  published as unavailable [derived: fully-loaded-onsite]; the bounds above are the",
        "  honest envelope, and the remote figure is a floor.",
        "",
        "## Method & provenance", "",
        f"- Durations, methods, statuses measured from [src: {src}]; connectivity joined from "
        f"[src: {fsrc}] by device_serial; all rates are declared plan constants "
        f"[config: commercial.yml] (demo stand-ins, not finance-validated).",
    ]

    # weekly completions by method (zero-filled)
    dated = [r for r in comp if r["completed_date"]]
    weeks = C.week_range(min(r["completed_date"] for r in dated),
                         max(r["completed_date"] for r in dated)) if dated else []
    m_lines = []
    for m in ("remote", "onsite"):
        wk = {}
        for r in dated:
            if r["method"] == m:
                w = C.week_start(r["completed_date"])
                wk[w] = wk.get(w, 0) + 1
        m_lines.append({"label": m, "points": [{"x": w, "y": wk.get(w, 0)} for w in weeks]})

    data = {
        "bq": "BQ-30",
        "series": [
            {"id": "cost-per-update", "label": "Cost per completed update", "unit": "USD",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "remote = flat session rate; on-site floor = mean completed on-site duration_min ÷ fse_day_minutes × fse_day_rate_usd",
                            "inputs": [f"src: {src}", "config: commercial.yml"]},
             "provenance": {"dataset": CAMP_DS, "snapshot": snap},
             "points": [{"label": "per remote update (session rate)", "value": remote_cost},
                        {"label": "per on-site update (labor-time floor)", "value": onsite_floor,
                         "sub": f"full-day ceiling ${onsite_ceiling:.0f}"}]},
            {"id": "weekly-by-method", "label": "Completed updates per week by method",
             "unit": "devices/week", "kind": "timeseries", "evidence_class": "measured",
             "provenance": {"dataset": CAMP_DS, "snapshot": snap}, "lines": m_lines, "points": []},
            {"id": "onsite-cost-bounds", "label": "On-site cost per update — bound envelope",
             "unit": "USD", "evidence_class": "derived",
             "derivation": {"method": "floor = labor time only (mean duration ÷ fse_day_minutes × day rate); ceiling = one full FSE day per visit; travel/overhead unmeasured",
                            "inputs": [f"src: {src}", "config: commercial.yml"]},
             "provenance": {"dataset": CAMP_DS, "snapshot": snap},
             "points": [{"label": "labor-time floor", "value": onsite_floor},
                        {"label": "full-day ceiling", "value": onsite_ceiling}]},
            {"id": "method-connectivity", "label": "Method ↔ connectivity alignment (completions)",
             "unit": "devices", "evidence_class": "derived",
             "derivation": {"method": "completed campaign rows joined to fleet connectivity by device_serial; counts where method matches connectivity (remote↔connected, onsite↔unconnected)",
                            "inputs": [f"src: {src}", f"src: {fsrc}"]},
             "provenance": {"dataset": CAMP_DS, "snapshot": snap},
             "points": [{"label": "remote on connected", "value": align["remote"]["expected"],
                         "of": align["remote"]["total"]},
                        {"label": "on-site on unconnected", "value": align["onsite"]["expected"],
                         "of": align["onsite"]["total"]}]},
            {"id": "adapter-case", "label": f"Adapter capex vs per-campaign on-site cost (top accounts)",
             "unit": "USD", "evidence_class": "derived",
             "derivation": {"method": "per site: non-connected PP3500 count × adapter_unit_cost_usd vs the same count × on-site cost bounds; totals over the ranked top accounts",
                            "inputs": [f"src: {fsrc}", "derived: onsite-cost-bounds", "config: commercial.yml"]},
             "provenance": {"dataset": FLEET_DS, "snapshot": fsnap},
             "points": [{"label": s, "value": round(n * adapter), "devices": n,
                         "onsite_floor": round(n * onsite_floor),
                         "onsite_ceiling": round(n * onsite_ceiling)} for s, n in ranked]},
            {"id": "adapter-payback", "label": "Adapter payback in update campaigns", "unit": "campaigns",
             "evidence_class": "derived",
             "derivation": {"method": "adapter_unit_cost_usd ÷ (on-site cost per update − remote cost per update), at each on-site bound; no campaign-frequency figure exists, so payback is per campaign",
                            "inputs": ["derived: onsite-cost-bounds", "config: commercial.yml"]},
             "provenance": {"dataset": CAMP_DS, "snapshot": snap},
             "points": [{"label": "at on-site labor floor", "value": payback_floor},
                        {"label": "at full-day ceiling", "value": payback_ceiling}]},
            {"id": "finish-current-campaign", "label": "Cost to finish the current on-site backlog",
             "unit": "USD", "evidence_class": "derived",
             "derivation": {"method": "on-site-remaining devices × on-site cost bounds, vs the same devices × (adapter + remote session); breakeven on-site cost = adapter + remote session per update, with its position in the floor–ceiling bound",
                            "inputs": [f"src: {src}", "derived: onsite-cost-bounds", "config: commercial.yml"]},
             "provenance": {"dataset": CAMP_DS, "snapshot": snap},
             "points": [{"label": "on-site (labor floor)", "value": fin_floor},
                        {"label": "on-site (full-day ceiling)", "value": fin_ceiling},
                        {"label": "adapter-convert + remote", "value": fin_convert},
                        {"label": "breakeven on-site cost per update (adapter + remote)",
                         "value": breakeven, "position_in_bound_pct": be_pos}]},
            {"id": "fully-loaded-onsite", "label": "True fully-loaded on-site cost per update",
             "unit": "USD", "evidence_class": "unavailable",
             "provenance": {"note": "travel + overhead per visit and FSE roster/day structure are "
                                    "not in any corpus dataset; the floor–ceiling bound is the "
                                    "honest envelope until the FSE dataset (also needed by BQ-26) "
                                    "is acquired"},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
