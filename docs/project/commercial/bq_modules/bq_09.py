"""BQ-09 — Disruption-window win rate: our CRM joined to REAL openFDA recall postings.

Contract: run(corpus_root, out, pins) per computations.py module dispatch.
Deterministic. The opportunity rows are demo-fabricated; the recall dates are real —
the join method is the demonstration, not the market effect size. Definitions
committed in plans/BQ-09.md.
"""

import datetime as dt

import yaml

import computations as C

WINLOSS_DS = "commercial/internal-winloss"
RECALLS_DS = "commercial/openfda-recalls-infusion"
NON_COMPETITOR = ("PainEase", "none")
BUCKETS = [("0-3 months", 0, 3), ("3-6 months", 3, 6), ("6-12 months", 6, 12)]


def quarter(iso_date):
    return f"{iso_date[:4]}-Q{(int(iso_date[5:7]) - 1) // 3 + 1}"


def quarter_range(a, b):
    """Every quarter from quarter(a) to quarter(b) inclusive."""
    y, q = int(a[:4]), (int(a[5:7]) - 1) // 3 + 1
    yb, qb = int(b[:4]), (int(b[5:7]) - 1) // 3 + 1
    out = []
    while (y, q) <= (yb, qb):
        out.append(f"{y}-Q{q}")
        q += 1
        if q == 5:
            y, q = y + 1, 1
    return out


QSTART = {"1": "01", "2": "04", "3": "07", "4": "10"}


def run(corpus_root, out, pins):
    p = C.params_for("BQ-09")
    rows, snap = C.load_pin_csv(corpus_root, pins, WINLOSS_DS)
    recalls, rsnap = C.load_pin_csv(corpus_root, pins, RECALLS_DS)
    src = f"{WINLOSS_DS}@{snap}"
    rsrc = f"{RECALLS_DS}@{rsnap}"
    window = int(p["disruption_window_days"])
    aliases = yaml.safe_load(open(p["aliases"]))["canonical"]

    def canon(name):
        u = name.upper()
        for c in aliases:
            if any(u.startswith(pref.upper()) for pref in c["prefixes"]):
                return c["name"]
        return name

    recall_dates = {}
    undated = 0
    for r in recalls:
        if r["event_date_posted"]:
            recall_dates.setdefault(canon(r["recalling_firm"]), []).append(r["event_date_posted"])
        else:
            undated += 1

    decided = [r for r in rows if r["outcome"] in ("won", "lost")
               and r["incumbent_vendor"] not in NON_COMPETITOR]
    excluded_nodec = sum(1 for r in rows if r["outcome"] == "no-decision"
                         and r["incumbent_vendor"] not in NON_COMPETITOR)

    def days_since_recall(r):
        """Days from the incumbent's most recent prior recall posting to close (None = no prior)."""
        cd = dt.date.fromisoformat(r["close_date"])
        gaps = [(cd - dt.date.fromisoformat(d)).days
                for d in recall_dates.get(canon(r["incumbent_vendor"]), [])
                if (cd - dt.date.fromisoformat(d)).days >= 0]
        return min(gaps) if gaps else None

    for r in decided:
        r["_days"] = days_since_recall(r)
        r["_inwin"] = r["_days"] is not None and r["_days"] <= window

    inw = [r for r in decided if r["_inwin"]]
    outw = [r for r in decided if not r["_inwin"]]

    # committed window-sensitivity check (plans/BQ-09.md): same join at a narrower window
    sens = int(p["sensitivity_window_days"])
    inw_s = [r for r in decided if r["_days"] is not None and r["_days"] <= sens]
    outw_s = [r for r in decided if r["_days"] is None or r["_days"] > sens]

    def wr(sub):
        return C.pct(sum(1 for r in sub if r["outcome"] == "won"), len(sub))

    # decay buckets on months since most recent prior recall
    bucket_rows = []
    for label, lo, hi in BUCKETS:
        sub = [r for r in decided if r["_days"] is not None and lo * 30.44 <= r["_days"] < hi * 30.44]
        bucket_rows.append((label, sub))
    bucket_rows.append((">12 months / no prior recall",
                        [r for r in decided if r["_days"] is None or r["_days"] >= 12 * 30.44]))

    # Verdict phrase DERIVED from the computed bucket shape (plans/BQ-09.md commitment):
    # never hardcode a data-shape claim like "decays".
    bstats = [(label, wr(sub), len(sub)) for label, sub in bucket_rows]
    inner, tail = bstats[:-1], bstats[-1]
    ir = [r for _, r, _n in inner]
    if all(ir[i] - ir[i + 1] > 1.0 for i in range(len(ir) - 1)):
        shape = ("the win rate decays across the months-since-recall buckets ("
                 + " → ".join(f"{r}%" for r in ir) + ")")
    elif ir[0] > max(ir[1:]) and max(ir[1:]) - min(ir[1:]) <= 2.0:
        shape = (f"the {inner[0][0]} bucket wins at the highest rate ({ir[0]}%) while the "
                 f"interior buckets are flat (~{ir[1]}%) — not a smooth decay")
    else:
        shape = ("the bucket profile is not a monotone decay ("
                 + " → ".join(f"{r}%" for r in ir) + " across the interior buckets)")
    if tail[1] < min(ir):
        shape += f"; the {tail[0]} tail is far lower ({tail[1]}%, n={tail[2]} — small n)"
    else:
        shape += f"; the {tail[0]} tail sits at {tail[1]}% (n={tail[2]})"

    headline = (f"Method demo (fabricated CRM joined to REAL FDA recall dates): we win {wr(inw)}% of "
                f"decided opportunities where the incumbent had an FRN recall posted within {window} "
                f"days of close (n={len(inw)}) vs {wr(outw)}% outside the window (n={len(outw)}); "
                f"{shape}")

    exps = C.evaluate_expectations("BQ-09", {})

    narrative = {"issues": [], "risks": [], "watch": []}
    narrative["risks"].append({
        "id": "R1", "severity": "high",
        "statement": "The effect size is NOT market evidence: opportunity records are "
                     "demo-fabricated and their seeded disruption windows were set independently of "
                     "the real recall calendar — only the join method generalizes",
        "mitigation": "Re-run against the real CRM export before any strategy decision; keep the "
                      "recall join and decay buckets as the reusable method",
        "evidence": [f"src: {src}", f"src: {rsrc}"]})
    narrative["risks"].append({
        "id": "R2", "severity": "medium",
        "statement": f"Large incumbents recall so often that {len(inw)} of {len(decided)} decided "
                     f"incumbent-held opportunities fall in-window — the out-of-window control group "
                     f"(n={len(outw)}) is too small to carry weight on its own",
        "mitigation": "Read the months-since-recall decay buckets, not the binary in/out split; "
                      "grow the control by extending history or narrowing the window definition",
        "evidence": ["derived: decay-buckets", f"src: {rsrc}"]})
    narrative["watch"].append({
        "id": "W1",
        "statement": "Recall severity/scope carries no weighting (any FRN posting counts) and "
                     "non-recall integration disruptions have no dataset — both widen what "
                     "'disruption' means vs what is measured",
        "evidence": ["derived: window-split"]})

    lines = [
        "# BQ-09 — Winning displaced accounts: the recall disruption window", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [src: {rsrc}] "
        f"[config: commercial.yml]", "",
        "## Honesty box — what is real here and what is not", "",
        f"- REAL: FDA recall postings for product code FRN, 2021→present, from openFDA "
        f"[src: {rsrc}].",
        f"- FABRICATED: every opportunity row (accounts, outcomes, dates) — demo-seeded CRM "
        f"[src: {src}].",
        "- Firm names on both sides are canonicalized through the versioned alias map",
        "  [config: entity-aliases.yml]; unmatched firms keep their raw name.",
        "",
        f"## Win rate in vs out of the {window}-day post-recall window [config: commercial.yml]", "",
        "| Population | Decided opps | Won | Win rate |",
        "|---|---|---|---|",
        f"| Incumbent recall posted ≤{window}d before close [derived: window-split] [src: {src}] | "
        f"{len(inw)} | {sum(1 for r in inw if r['outcome'] == 'won')} | {wr(inw)}% |",
        f"| No recall in window [derived: window-split] [src: {src}] | {len(outw)} | "
        f"{sum(1 for r in outw if r['outcome'] == 'won')} | {wr(outw)}% |",
        "",
        f"- Window sensitivity: at a {sens}-day window the split is {wr(inw_s)}% in (n={len(inw_s)}) "
        f"vs {wr(outw_s)}% out (n={len(outw_s)}) — the size of the binary contrast at {window} days "
        f"is partly an artifact of the window definition [derived: window-sensitivity] "
        f"[config: commercial.yml] [src: {src}].",
        f"- Population: decided (won/lost) opportunities where the incumbent is a competitor; "
        f"{excluded_nodec} no-decision opportunities excluded [src: {src}].",
        f"- Recall postings without an event_date_posted are excluded from the join: {undated} "
        f"record(s) [src: {rsrc}].",
        "",
        "## How long does the window stay open? (win rate by months since the incumbent's most recent recall)", "",
        "| Months since recall at close | Decided opps | Won | Win rate |",
        "|---|---|---|---|",
    ]
    for label, sub in bucket_rows:
        wins = sum(1 for r in sub if r["outcome"] == "won")
        small = " (small n — indicative only)" if 0 < len(sub) < 10 else ""
        lines.append(f"| {label} [derived: decay-buckets] [src: {src}] | {len(sub)}{small} | "
                     f"{wins} | {wr(sub)}% |")
    lines += [
        "",
        "## Recall pressure by incumbent (canonicalized)", "",
        "| Firm (canonical) | FRN recalls posted since 2021 |",
        "|---|---|",
    ]
    incumbent_firms = sorted({canon(r["incumbent_vendor"]) for r in decided})
    for firm in incumbent_firms:
        lines.append(f"| {firm} [src: {rsrc}] [config: entity-aliases.yml] | "
                     f"{len(recall_dates.get(firm, []))} |")
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- In-window = at least one recall by the (canonical) incumbent posted in the {window} days "
        f"ending at close_date [derived: window-split] [config: commercial.yml].",
        f"- Quarterly won/lost history, split in/out of window, charted zero-filled "
        f"[derived: quarterly-outcomes] [src: {src}].",
        "- No catalog expectations are declared for this question — none are invented.",
        "- The verdict's window-duration language is derived from the computed bucket shape —",
        "  a decay is claimed only when the bucket win rates actually decrease",
        "  [derived: decay-buckets].",
        "- Causality is not asserted: a recall near a close date does not prove the recall drove",
        "  the outcome [derived: window-split].",
    ]

    quarters = quarter_range(min(r["close_date"] for r in decided),
                             max(r["close_date"] for r in decided))

    def qline(label, pred):
        by_q = {}
        for r in decided:
            if pred(r):
                q = quarter(r["close_date"])
                by_q[q] = by_q.get(q, 0) + 1
        return {"label": label,
                "points": [{"x": f"{q[:4]}-{QSTART[q[-1]]}-01", "y": by_q.get(q, 0)}
                           for q in quarters]}

    trend = [
        qline("in-window won", lambda r: r["_inwin"] and r["outcome"] == "won"),
        qline("in-window lost", lambda r: r["_inwin"] and r["outcome"] == "lost"),
        qline("out-of-window won", lambda r: not r["_inwin"] and r["outcome"] == "won"),
        qline("out-of-window lost", lambda r: not r["_inwin"] and r["outcome"] == "lost"),
    ]

    join_inputs = [f"src: {src}", f"src: {rsrc}", "config: commercial.yml",
                   "config: entity-aliases.yml"]
    data = {
        "bq": "BQ-09",
        "series": [
            {"id": "inwindow-rate", "label": "In-window win rate", "unit": "%",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": f"won ÷ decided over opportunities whose canonical incumbent "
                                      f"had an FRN recall posted within {window}d before close",
                            "inputs": join_inputs},
             "provenance": {"dataset": WINLOSS_DS, "snapshot": snap},
             "points": [{"label": f"decided incumbent-held opps in the {window}d window "
                                  f"(n={len(inw)})", "value": wr(inw)}]},
            {"id": "window-split", "label": "Win rate in vs out of the disruption window", "unit": "%",
             "kind": "paired-bars", "pairs": {"a_label": "in-window", "b_label": "out-of-window"},
             "evidence_class": "derived",
             "derivation": {"method": "win rate per population; in-window per the recall join above",
                            "inputs": join_inputs},
             "provenance": {"dataset": WINLOSS_DS, "snapshot": snap},
             "points": [{"label": "win rate %", "a": wr(inw), "b": wr(outw)}]},
            {"id": "window-sensitivity",
             "label": f"Win rate split at the {sens}-day sensitivity window", "unit": "%",
             "kind": "paired-bars", "pairs": {"a_label": "in-window", "b_label": "out-of-window"},
             "evidence_class": "derived",
             "derivation": {"method": f"the same recall join recomputed with a {sens}-day window — "
                                      "committed sensitivity check on the window definition",
                            "inputs": join_inputs},
             "provenance": {"dataset": WINLOSS_DS, "snapshot": snap},
             "points": [{"label": "win rate %", "a": wr(inw_s), "b": wr(outw_s)}]},
            {"id": "decay-buckets", "label": "Win rate by months since incumbent's most recent recall",
             "unit": "%", "evidence_class": "derived",
             "derivation": {"method": "decided opps bucketed by days since the most recent prior "
                                      "recall posting ÷ 30.44; win rate per bucket",
                            "inputs": join_inputs},
             "provenance": {"dataset": WINLOSS_DS, "snapshot": snap},
             "points": [{"label": label, "value": wr(sub), "n": len(sub)}
                        for label, sub in bucket_rows]},
            {"id": "recalls-by-incumbent", "label": "FRN recalls posted since 2021, by canonical firm",
             "unit": "recalls", "evidence_class": "measured",
             "provenance": {"dataset": RECALLS_DS, "snapshot": rsnap},
             "points": [{"label": firm, "value": len(recall_dates.get(firm, []))}
                        for firm in incumbent_firms]},
            {"id": "quarterly-outcomes", "label": "Quarterly decided outcomes, in vs out of window",
             "unit": "opportunities/quarter", "kind": "timeseries", "evidence_class": "derived",
             "derivation": {"method": "decided opps per close-quarter, split by the recall join",
                            "inputs": join_inputs},
             "provenance": {"dataset": WINLOSS_DS, "snapshot": snap},
             "lines": trend, "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
