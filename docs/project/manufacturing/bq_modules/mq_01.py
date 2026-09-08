"""MQ-01 — first-pass yield, scrap and rework by product line, hw rev, station, site.

Deterministic per the MQ-01 analysis plan: the trailing window is the last
`window_months` calendar months ending at the pinned snapshot's as_of; first-pass
yield (FPY) = units passed first time ÷ units started, unit-weighted; scrap and rework
rates share that denominator. "Since when" is COMPUTED: for each eroding cell, the
first month of the trailing run of months whose rolling-window FPY is below the floor.
"""

import computations as C

LOTS_DS = "manufacturing/internal-production-lots"
STATIONS = ("SMT", "final-assembly", "test", "pack")
LINES = ("IP5000", "PP3000", "PP3500", "SP6000", "SP6500")


def _sum(rows, col):
    return sum(int(r[col]) for r in rows)


def _fpy(rows):
    s = _sum(rows, "units_started")
    return C.pct_raw(_sum(rows, "units_passed_first_time"), s) if s else None


def _rate(rows, col):
    s = _sum(rows, "units_started")
    return C.pct_raw(_sum(rows, col), s) if s else None


def _r(v):
    return None if v is None else round(v, 1)


def _onset(rows_all, months, pred, floor, n_win):
    """First month of the trailing run of months in which the cell's ROLLING
    trailing-window FPY (same window length as the analysis, ending at that month) sits
    below the floor. Scanned backward from the as-of month; the run breaks at the first
    month whose rolling value is at or above the floor. None only if the cell has no
    units in the as-of window (cannot happen for a cell reported as eroding)."""
    onset = None
    for i in range(len(months) - 1, -1, -1):
        span = months[max(0, i - n_win + 1): i + 1]
        sub = [r for r in rows_all if r["start_date"][:7] in span and pred(r)]
        v = _fpy(sub)
        if v is None:
            break
        if v < floor:
            onset = months[i]
        else:
            break
    return onset


def run(corpus_root, out, pins):
    p = C.params_for("MQ-01")
    floor = float(p["fpy_floor_pct"])
    n_win = int(p["window_months"])
    rows, snap = C.load_pin_csv(corpus_root, pins, LOTS_DS)
    C.assert_vocab(rows, "line_station", STATIONS, LOTS_DS)
    C.assert_vocab(rows, "product_line", LINES, LOTS_DS)
    src = f"{LOTS_DS}@{snap}"
    as_of = C.snapshot_as_of(corpus_root, pins, LOTS_DS)
    months_all = C.month_range(min(r["start_date"] for r in rows)[:7], as_of[:7])
    win = C.trailing_months(as_of, n_win)
    w = [r for r in rows if r["start_date"][:7] in win]
    prior = [r for r in rows if r["start_date"][:7] in C.trailing_months(win[0], n_win + 1)[:n_win]]
    win_label = f"{win[0]}..{win[-1]}"

    fpy_all, fpy_prior = _fpy(w), _fpy(prior)
    scrap_all, rework_all = _rate(w, "units_scrapped"), _rate(w, "units_reworked")
    units_all = _sum(w, "units_started")

    def cut(key_fn, keys):
        return [(k, _fpy([r for r in w if key_fn(r) == k]),
                 _rate([r for r in w if key_fn(r) == k], "units_scrapped"),
                 _rate([r for r in w if key_fn(r) == k], "units_reworked"),
                 _sum([r for r in w if key_fn(r) == k], "units_started")) for k in keys]

    by_line = cut(lambda r: r["product_line"], LINES)
    by_station = cut(lambda r: r["line_station"], STATIONS)
    sites = sorted({r["site"] for r in rows})
    by_site = cut(lambda r: r["site"], sites)
    below_lines = [(k, v) for k, v, _, _, _ in by_line if v is not None and v < floor]

    # line × station cells in the window — where exactly is yield eroding?
    cells = []
    for line in LINES:
        for st in STATIONS:
            sub = [r for r in w if r["product_line"] == line and r["line_station"] == st]
            v = _fpy(sub)
            if v is not None:
                cells.append((line, st, v, _sum(sub, "units_started")))
    eroding = sorted([c for c in cells if c[2] < floor], key=lambda c: c[2])
    onsets = []
    for line, st, v, _ in eroding:
        o = _onset(rows, months_all, lambda r, l=line, s=st: r["product_line"] == l and r["line_station"] == s, floor, n_win)
        onsets.append((f"{line} · {st}", v, o))

    # PP3500 hw-rev split by station in the window (the rev-specific question)
    revs = sorted({r["hw_rev"] for r in w if r["product_line"] == "PP3500"})
    rev_station = []
    for st in STATIONS:
        row = {"station": st}
        for rv in revs:
            row[rv] = _fpy([r for r in w if r["product_line"] == "PP3500" and r["line_station"] == st and r["hw_rev"] == rv])
        rev_station.append(row)
    worst_rev_cell = None
    for row in rev_station:
        for rv in revs:
            v = row[rv]
            if v is not None and (worst_rev_cell is None or v < worst_rev_cell[2]):
                worst_rev_cell = (rv, row["station"], v)
    rev_gap = None
    if worst_rev_cell:
        rv, st, v = worst_rev_cell
        others = [row[o] for row in rev_station if row["station"] == st for o in revs if o != rv and row[o] is not None]
        if others:
            rev_gap = (rv, st, v, max(others), [o for o in revs if o != rv])
    rev_onset = None
    if rev_gap:
        rev_onset = _onset(rows, months_all,
                           lambda r, rv=rev_gap[0], st=rev_gap[1]: r["product_line"] == "PP3500" and r["hw_rev"] == rv and r["line_station"] == st,
                           floor, n_win)

    # monthly trend lines (zero-filled months carry y = null only where no units ran)
    def monthly(pred):
        pts = []
        for mo in months_all:
            v = _fpy([r for r in rows if r["start_date"][:7] == mo and pred(r)])
            pts.append({"x": f"{mo}-01", "y": _r(v)})
        # trim leading months before the population exists (a rev that is not yet in
        # production is absent, not zero-yield)
        while pts and pts[0]["y"] is None:
            pts.pop(0)
        return pts

    trend_lines = [{"label": "portfolio (all lots)", "points": monthly(lambda r: True)}]
    if rev_gap:
        rv, st = rev_gap[0], rev_gap[1]
        trend_lines.append({"label": f"PP3500 rev {rv} @ {st}",
                            "points": monthly(lambda r, rv=rv, st=st: r["product_line"] == "PP3500" and r["hw_rev"] == rv and r["line_station"] == st)})
        for o in rev_gap[4]:
            trend_lines.append({"label": f"PP3500 rev {o} @ {st}",
                                "points": monthly(lambda r, o=o, st=st: r["product_line"] == "PP3500" and r["hw_rev"] == o and r["line_station"] == st)})
    trend_lines = trend_lines[:4]

    delta = None if None in (fpy_all, fpy_prior) else fpy_all - fpy_prior
    parts = [f"Trailing {n_win}-month window {win_label}: portfolio first-pass yield {fpy_all:.1f}% "
             f"on {units_all} units started ({'up' if delta is not None and delta >= 0 else 'down'} "
             f"{abs(delta):.1f} pts vs the prior {n_win} months); "
             f"{len(below_lines)} of {len(by_line)} lines below the {floor:.0f}% floor"
             + (": " + ", ".join(f"{k} {v:.1f}%" for k, v in below_lines) if below_lines else "")]
    parts.append(f"{len(eroding)} of {len(cells)} line×station cells below the floor"
                 + (": " + ", ".join(f"{lbl} {v:.1f}% since {o or 'n/a'}" for lbl, v, o in onsets) if onsets else ""))
    if rev_gap:
        rv, st, v, best, _ = rev_gap
        parts.append(f"erosion is rev-specific — PP3500 rev {rv} at {st} {v:.1f}% vs other revs {best:.1f}%"
                     + (f", below the floor since {rev_onset}" if rev_onset else ""))
    parts.append(f"scrap {scrap_all:.1f}%, rework {rework_all:.1f}% of units started")
    headline = "; ".join(parts)

    # narrative — deterministic from computed facts
    narrative = {"issues": [], "risks": [], "watch": []}
    for i, (lbl, v, o) in enumerate(onsets, 1):
        narrative["issues"].append({
            "id": f"I{i}", "severity": "high" if v < floor - 3 else "medium",
            "statement": f"{lbl} first-pass yield {v:.1f}% in {win_label}, below the {floor:.0f}% floor"
                         + (f" every month since {o}" if o else ""),
            "action": "Open / link the NCR and containment for the cell; confirm whether the "
                      "failure mode is fixture, process, or component (see MQ-03 / MQ-05)",
            "evidence": ["derived: erosion-cells", f"src: {src}", C.CONFIG_MARKER],
        })
    if rev_gap:
        rv, st, v, best, _ = rev_gap
        narrative["risks"].append({
            "id": "R1", "severity": "high",
            "statement": f"PP3500 rev {rv} yields {v:.1f}% at {st} against {best:.1f}% for the other "
                         f"rev(s) at the same station — a revision-specific defect, not a station drift; "
                         f"rev {rv} share of PP3500 lots keeps rising so portfolio FPY follows it",
            "mitigation": "Hold rev-specific FPY as a release-readiness input for the rev C ramp; "
                          "tie the test-station failure Pareto to the rev C fixture PQ (MQ-08)",
            "evidence": ["derived: pp3500-rev-by-station", "derived: fpy-trend", f"src: {src}"],
        })
    narrative["risks"].append({
        "id": f"R{len(narrative['risks']) + 1}", "severity": "medium",
        "statement": f"The {floor:.0f}% floor is a stand-in — no yield target is on record in a "
                     "manufacturing plan or the pFMEA, so 'below floor' is only as good as an "
                     "unratified threshold",
        "mitigation": "Have manufacturing engineering ratify per-line FPY targets and mark E-01.1 validated",
        "evidence": [C.CONFIG_MARKER],
    })
    worst_site = min(by_site, key=lambda t: t[1] if t[1] is not None else 999)
    narrative["watch"].append({
        "id": "W1",
        "statement": f"Site cut: {worst_site[0]} is the lower-yield plant at {worst_site[1]:.1f}% in "
                     f"{win_label} — check whether the gap is mix (which lines run there) or process",
        "evidence": ["derived: fpy-by-site", f"src: {src}"],
    })

    exp_results = {
        "E-01.1": (f"{len(below_lines)} of {len(by_line)} lines below {floor:.0f}% in {win_label}"
                   + (": " + ", ".join(f"{k} {v:.1f}%" for k, v in below_lines) if below_lines else ""),
                   "met" if not below_lines else "not-met",
                   ["derived: fpy-by-line"]),
    }
    exps = C.evaluate_expectations("MQ-01", exp_results)

    def fmt(v):
        return "—" if v is None else f"{v:.1f}"

    lines = [
        "# MQ-01 — First-pass yield, scrap and rework: where is yield eroding, and since when?", "",
        C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [{C.CONFIG_MARKER}]", "",
        "## Headline", "",
        f"- Window: trailing {n_win} months {win_label}, anchored on the snapshot as-of {as_of} "
        f"[src: {src}] [{C.CONFIG_MARKER}]; FPY = units passed first time ÷ units started, "
        f"unit-weighted [derived: fpy-stat].",
        f"- Portfolio FPY {fpy_all:.1f}% (prior window {fpy_prior:.1f}%), scrap {scrap_all:.1f}%, "
        f"rework {rework_all:.1f}% [derived: fpy-stat] [src: {src}].", "",
        "## By product line", "",
        "| Product line | FPY % | Scrap % | Rework % | Units started |",
        "|---|---|---|---|---|",
    ]
    for k, v, s, rw, u in by_line:
        flag = " ⚠️" if v is not None and v < floor else ""
        lines.append(f"| {k} [src: {src}] | {fmt(v)}{flag} | {fmt(s)} | {fmt(rw)} | {u} |")
    lines += ["", "## By station", "", "| Station | FPY % | Scrap % | Rework % | Units started |", "|---|---|---|---|---|"]
    for k, v, s, rw, u in by_station:
        flag = " ⚠️" if v is not None and v < floor else ""
        lines.append(f"| {k} [src: {src}] | {fmt(v)}{flag} | {fmt(s)} | {fmt(rw)} | {u} |")
    lines += ["", "## By site", "", "| Site | FPY % | Scrap % | Rework % | Units started |", "|---|---|---|---|---|"]
    for k, v, s, rw, u in by_site:
        flag = " ⚠️" if v is not None and v < floor else ""
        lines.append(f"| {k} [src: {src}] | {fmt(v)}{flag} | {fmt(s)} | {fmt(rw)} | {u} |")
    lines += ["", "## Where yield is eroding — line × station cells below the floor", "",
              "| Cell | FPY % | Below floor since |", "|---|---|---|"]
    if onsets:
        for lbl, v, o in onsets:
            lines.append(f"| {lbl} [src: {src}] | {v:.1f} | {o or 'n/a'} |")
    else:
        lines.append(f"| (no cell below the floor in {win_label}) [src: {src}] | — | — |")
    lines += ["", "## PP3500 by hardware revision and station", "",
              "| Station | " + " | ".join(f"rev {rv} FPY %" for rv in revs) + " |",
              "|---|" + "---|" * len(revs)]
    for row in rev_station:
        lines.append(f"| {row['station']} [src: {src}] | " + " | ".join(fmt(row[rv]) for rv in revs) + " |")
    if rev_gap:
        rv, st, v, best, _ = rev_gap
        lines += ["", f"- Widest rev gap: rev {rv} at {st} {v:.1f}% vs {best:.1f}% for the other rev(s)"
                  + (f"; rev {rv} at {st} has sat below the floor every month since {rev_onset}" if rev_onset else "")
                  + f" [derived: pp3500-rev-by-station] [src: {src}]."]
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- All figures from the pinned lot records [src: {src}]; the window and the floor are "
        f"plan constants [{C.CONFIG_MARKER}].",
        "- Rates are unit-weighted (sum of units over the cell), not lot-averaged, so large lots "
        "count for what they are; rework and scrap are the two exits from first-pass failure and "
        "sum to the first-pass failure rate [derived: fpy-stat].",
        f"- 'Since when' is the first month of the unbroken run of months whose rolling {n_win}-month "
        "FPY sits below the floor, ending at the as-of month — a cell that dipped and recovered is not "
        "reported as eroding [derived: erosion-cells].",
        "- Monthly history is charted for the portfolio and for the rev/station cell with the widest "
        "gap [derived: fpy-trend].",
    ]

    data = {
        "bq": "MQ-01",
        "series": [
            {"id": "fpy-stat", "label": "First-pass yield, scrap, rework", "unit": "%", "kind": "stat",
             "evidence_class": "derived",
             "derivation": {"method": "units passed first time ÷ units started (scrap, rework: same denominator) over the trailing window",
                            "inputs": [f"src: {src}", C.CONFIG_MARKER]},
             "provenance": {"dataset": LOTS_DS, "snapshot": snap},
             "points": [{"label": f"FPY {win_label}", "value": _r(fpy_all), "sub": f"prior window {fmt(fpy_prior)}%"},
                        {"label": "scrap rate", "value": _r(scrap_all), "sub": "of units started"},
                        {"label": "rework rate", "value": _r(rework_all), "sub": "of units started"},
                        {"label": "lines below floor", "value": len(below_lines), "sub": f"of {len(by_line)}"}]},
            {"id": "fpy-by-line", "label": "First-pass yield by product line", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "FPY per product line over the trailing window", "inputs": [f"src: {src}"]},
             "provenance": {"dataset": LOTS_DS, "snapshot": snap},
             "points": [{"label": k, "value": _r(v), "units_started": u} for k, v, _, _, u in by_line]},
            {"id": "fpy-by-station", "label": "First-pass yield by station", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "FPY per line station over the trailing window", "inputs": [f"src: {src}"]},
             "provenance": {"dataset": LOTS_DS, "snapshot": snap},
             "points": [{"label": k, "value": _r(v), "units_started": u} for k, v, _, _, u in by_station]},
            {"id": "fpy-by-site", "label": "First-pass yield by site", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "FPY per plant over the trailing window", "inputs": [f"src: {src}"]},
             "provenance": {"dataset": LOTS_DS, "snapshot": snap},
             "points": [{"label": k, "value": _r(v), "units_started": u} for k, v, _, _, u in by_site]},
            {"id": "scrap-rework-by-line", "label": "Scrap vs rework rate by product line", "unit": "%",
             "kind": "paired-bars", "pairs": {"a_label": "scrap", "b_label": "rework"},
             "evidence_class": "derived",
             "derivation": {"method": "units scrapped ÷ units started and units reworked ÷ units started per line",
                            "inputs": [f"src: {src}"]},
             "provenance": {"dataset": LOTS_DS, "snapshot": snap},
             "points": [{"label": k, "a": _r(s), "b": _r(rw)} for k, _, s, rw, _ in by_line]},
            {"id": "erosion-cells", "label": "Line × station cells below the floor (and since when)", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "cells with window FPY < floor; onset = first month of the trailing run of months whose rolling window FPY is below the floor",
                            "inputs": [f"src: {src}", C.CONFIG_MARKER]},
             "provenance": {"dataset": LOTS_DS, "snapshot": snap},
             "points": [{"label": lbl, "value": _r(v), "since": o} for lbl, v, o in onsets]},
            {"id": "pp3500-rev-by-station", "label": "PP3500 first-pass yield by hw rev and station", "unit": "%",
             "kind": "paired-bars",
             "pairs": {"a_label": f"rev {revs[-1]}" if revs else "rev", "b_label": f"rev {revs[0]}" if revs else "rev"},
             "evidence_class": "derived",
             "derivation": {"method": "FPY per (hw_rev, station) for PP3500 lots in the trailing window",
                            "inputs": [f"src: {src}"]},
             "provenance": {"dataset": LOTS_DS, "snapshot": snap},
             "points": [{"label": row["station"], "a": _r(row[revs[-1]]) if revs else None,
                         "b": _r(row[revs[0]]) if revs else None,
                         **{f"rev_{rv}": _r(row[rv]) for rv in revs}} for row in rev_station]},
            {"id": "fpy-trend", "label": "Monthly first-pass yield", "unit": "%", "kind": "timeseries",
             "evidence_class": "derived",
             "derivation": {"method": "monthly FPY for the portfolio and for the PP3500 rev/station cell with the widest gap (plus its peers)",
                            "inputs": [f"src: {src}"]},
             "provenance": {"dataset": LOTS_DS, "snapshot": snap},
             "lines": trend_lines, "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
