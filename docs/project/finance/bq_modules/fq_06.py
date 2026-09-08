"""FQ-06 — working capital: DSO and over-90 AR by channel / region, inventory days by
line, cash trapped.

Deterministic per the FQ-06 analysis plan: "latest" = the maximum period in the pinned
working-capital cube. Days-type ratios aggregate by implied daily flow (Σ amount ÷
Σ amount ÷ days) — never by averaging ratios. Cash trapped = over-90 AR + inventory
value above the target days of cover, per line. Subscription (cloud-suite) receivables
are not in the cube and are published as an unavailable series.
"""

import computations as C

AR_DS = "finance/internal-ar-inventory"
CHANNELS_MAX = 4      # timeseries cap — channels are exactly four in the cube
TREND_LINES = 3       # lines charted individually; the rest combined


def _fmt_days(v):
    return "n/a" if v is None else f"{v:.1f}"


def _m(v):
    return f"{C.musd(v):.2f}"


def run(corpus_root, out, pins):
    p = C.params_for("FQ-06")
    dso_t = float(p["dso_target_days"])
    o90_t = float(p["over90_share_threshold_pct"])
    inv_t = float(p["inventory_target_days"])
    ar, snap = C.load_pin_csv(corpus_root, pins, AR_DS)
    src = f"{AR_DS}@{snap}"

    periods = sorted({r["period"] for r in ar})
    latest = periods[-1]
    cur = [r for r in ar if r["period"] == latest]
    channels = sorted({r["gpo"] for r in ar})
    regions = sorted({r["region"] for r in ar})
    lines_all = sorted({r["product_line"] for r in ar})

    def ar_sum(rows):
        return sum(int(r["ar_balance_usd"]) for r in rows)

    def o90_sum(rows):
        return sum(int(r["ar_over_90_usd"]) for r in rows)

    def inv_sum(rows):
        return sum(int(r["inventory_usd"]) for r in rows)

    dso_company = C.flow_weighted_days(cur, "ar_balance_usd", "dso_days")
    ar_total, o90_total = ar_sum(cur), o90_sum(cur)
    o90_share_company = C.pct_raw(o90_total, ar_total)

    ch_rows = []
    for g in channels:
        sub = [r for r in cur if r["gpo"] == g]
        ch_rows.append((g, C.flow_weighted_days(sub, "ar_balance_usd", "dso_days"), ar_sum(sub), o90_sum(sub),
                        C.pct_raw(o90_sum(sub), ar_sum(sub))))
    reg_rows = []
    for g in regions:
        sub = [r for r in cur if r["region"] == g]
        reg_rows.append((g, C.flow_weighted_days(sub, "ar_balance_usd", "dso_days"), ar_sum(sub),
                         C.pct_raw(o90_sum(sub), ar_sum(sub))))
    o90_breach = sorted([r for r in ch_rows if r[4] > o90_t], key=lambda r: -r[4])
    worst_ch = max(ch_rows, key=lambda r: r[4])

    inv_rows = []
    for l in lines_all:
        sub = [r for r in cur if r["product_line"] == l]
        days = C.flow_weighted_days(sub, "inventory_usd", "inventory_days")
        inv = inv_sum(sub)
        daily = inv / days if days else 0.0
        excess = max(0.0, inv - daily * inv_t)
        inv_rows.append((l, days, inv, excess))
    inv_over = sorted([r for r in inv_rows if r[1] is not None and r[1] > inv_t], key=lambda r: -r[1])
    excess_total = sum(r[3] for r in inv_rows)
    trapped = o90_total + excess_total

    # ---- trends (full history)
    def o90_line(g):
        pts = []
        for m in periods:
            sub = [r for r in ar if r["period"] == m and r["gpo"] == g]
            pts.append({"x": C.month_iso(m), "y": C.pct(o90_sum(sub), ar_sum(sub))})
        return {"label": g, "points": pts}

    o90_trend = [o90_line(g) for g in channels[:CHANNELS_MAX]]
    inv_by_total = sorted(inv_rows, key=lambda r: (-r[2], r[0]))
    top_lines = [r[0] for r in inv_by_total[:TREND_LINES]]
    rest = [l for l in lines_all if l not in top_lines]

    def inv_line(label, lines_):
        pts = []
        for m in periods:
            sub = [r for r in ar if r["period"] == m and r["product_line"] in lines_]
            d = C.flow_weighted_days(sub, "inventory_usd", "inventory_days")
            pts.append({"x": C.month_iso(m), "y": round(d, 1) if d is not None else None})
        return {"label": label, "points": pts}

    inv_trend = [inv_line(l, [l]) for l in top_lines]
    if rest:
        inv_trend.append(inv_line("+".join(rest), rest))
    first_o90 = next(pt["y"] for pt in o90_line(worst_ch[0])["points"])

    # ---- expectations
    exps = C.evaluate_expectations("FQ-06", {
        "E-06.1": (f"{_fmt_days(dso_company)} days company DSO at {latest}; worst channel {worst_ch[0]} "
                   f"{_fmt_days(worst_ch[1])} days",
                   "met" if dso_company is not None and dso_company <= dso_t else "not-met",
                   ["derived: dso-stat", "derived: dso-by-channel"]),
        "E-06.2": (f"{len(o90_breach)} of {len(ch_rows)} channels over {o90_t:.0f}%"
                   + (": " + ", ".join(f"{g} {s:.1f}%" for g, _, _, _, s in o90_breach) if o90_breach else ""),
                   "met" if not o90_breach else "not-met", ["derived: over90-by-channel"]),
        "E-06.3": (f"{len(inv_over)} of {len(inv_rows)} lines over {inv_t:.0f} days"
                   + (": " + ", ".join(f"{l} {_fmt_days(d)}" for l, d, _, _ in inv_over) if inv_over else ""),
                   "met" if not inv_over else "not-met", ["derived: inventory-days-by-line"]),
    })

    # ---- verdict (rollup-survival)
    parts = [f"As of {latest}: company DSO {_fmt_days(dso_company)} days vs {dso_t:.0f} target "
             f"({'within' if dso_company is not None and dso_company <= dso_t else 'OVER'})",
             f"{worst_ch[0]} DSO {_fmt_days(worst_ch[1])} days with over-90 share {worst_ch[4]:.1f}% "
             f"({len(o90_breach)} of {len(ch_rows)} channels over the {o90_t:.0f}% threshold)",
             f"inventory days over the {inv_t:.0f}-day target on {len(inv_over)} of {len(inv_rows)} lines"
             + (" (" + ", ".join(f"{l} {d:.0f}" for l, d, _, _ in inv_over) + ")" if inv_over else ""),
             f"cash trapped ${_m(trapped)}M = ${_m(o90_total)}M over-90 AR + ${_m(excess_total)}M "
             f"inventory above target cover"]
    headline = "; ".join(parts)

    # ---- narrative
    narrative = {"issues": [], "risks": [], "watch": []}
    for i, (g, d, a, o, s) in enumerate(o90_breach, 1):
        narrative["issues"].append({
            "id": f"I{i}", "severity": "high" if s > 2 * o90_t else "medium",
            "statement": f"{g}: over-90 receivables ${_m(o)}M of ${_m(a)}M ({s:.1f}%) at {latest}, "
                         f"DSO {_fmt_days(d)} days — over-90 share was {first_o90:.1f}% at {periods[0]}",
            "action": "Collections escalation with the channel's contracting lead; hold new shipments against "
                      "a payment plan; assess bad-debt provision",
            "evidence": ["derived: over90-by-channel", "derived: over90-trend", f"src: {src}", C.CONFIG_MARKER],
        })
    for j, (l, d, inv, ex) in enumerate(inv_over, len(narrative["issues"]) + 1):
        narrative["issues"].append({
            "id": f"I{j}", "severity": "medium",
            "statement": f"{l} inventory {_fmt_days(d)} days of cover (${_m(inv)}M held, ${_m(ex)}M above "
                         f"the {inv_t:.0f}-day target) at {latest}",
            "action": "Run-down plan: stop replenishment, redirect demand to the successor line, review "
                      "obsolescence reserve",
            "evidence": ["derived: inventory-days-by-line", "derived: inventory-days-trend", f"src: {src}",
                         C.CONFIG_MARKER],
        })
    narrative["risks"].append({
        "id": "R1", "severity": "medium",
        "statement": f"The DSO target ({dso_t:.0f} days), over-90 threshold ({o90_t:.0f}%) and inventory target "
                     f"({inv_t:.0f} days) are stand-ins — no treasury, credit, or S&OP policy on file names them",
        "mitigation": "Ratify the three targets with treasury / credit / operations and mark E-06.1..E-06.3 validated",
        "evidence": [C.CONFIG_MARKER],
    })
    narrative["watch"].append({
        "id": "W1",
        "statement": f"Company over-90 share {o90_share_company:.1f}% of ${_m(ar_total)}M receivables — "
                     "the channel cut, not the total, is where the exposure sits",
        "evidence": ["derived: over90-by-channel", f"src: {src}"],
    })
    narrative["watch"].append({
        "id": "W2",
        "statement": "Subscription (cloud-suite) receivables are not in the working-capital cube — company DSO "
                     "covers device lines only",
        "evidence": ["derived: subscription-ar", f"src: {src}"],
    })

    lines = [
        "# FQ-06 — Working capital: DSO, over-90 AR, inventory days, cash trapped", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [{C.CONFIG_MARKER}]", "",
        "## Receivables by channel", "",
        f"_Latest period {latest} in the pin (history {periods[0]}..{periods[-1]}) [src: {src}]; DSO aggregated "
        f"as Σ AR ÷ Σ (AR ÷ DSO); targets [{C.CONFIG_MARKER}]._", "",
        "| Channel | AR $M | DSO days | Over-90 $M | Over-90 share |",
        "|---|---|---|---|---|",
    ]
    for g, d, a, o, s in ch_rows:
        flag = " ⚠️" if s > o90_t else ""
        lines.append(f"| {g} [src: {src}] | {_m(a)} | {_fmt_days(d)} | {_m(o)} | {s:.1f}%{flag} |")
    lines += [
        f"| **Company** [src: {src}] | {_m(ar_total)} | {_fmt_days(dso_company)} | {_m(o90_total)} | "
        f"{o90_share_company:.1f}% |",
        "",
        "## Receivables by region", "",
        "| Region | AR $M | DSO days | Over-90 share |",
        "|---|---|---|---|",
    ]
    for g, d, a, s in reg_rows:
        lines.append(f"| {g} [src: {src}] | {_m(a)} | {_fmt_days(d)} | {s:.1f}% |")
    lines += [
        "",
        "## Inventory by product line", "",
        f"_Days aggregated as Σ inventory ÷ Σ (inventory ÷ days); excess = value above {inv_t:.0f} days of cover "
        f"[{C.CONFIG_MARKER}] [src: {src}]._", "",
        "| Product line | Inventory $M | Days of cover | Excess above target $M |",
        "|---|---|---|---|",
    ]
    for l, d, inv, ex in inv_rows:
        flag = " ⚠️" if d is not None and d > inv_t else ""
        lines.append(f"| {l} [src: {src}] | {_m(inv)} | {_fmt_days(d)}{flag} | {_m(ex)} |")
    lines += [
        "",
        "## Cash trapped", "",
        f"- Over-90 receivables ${_m(o90_total)}M + inventory above target cover ${_m(excess_total)}M = "
        f"${_m(trapped)}M at {latest} [derived: cash-trapped] [src: {src}] [{C.CONFIG_MARKER}].",
        "",
        "## Subscription receivables: not in the cube (stated, not approximated)", "",
        f"- The working-capital cube carries the five device lines only [src: {src}]; cloud-suite subscription "
        "billing needs its own AR feed before it joins the company DSO [derived: subscription-ar].",
    ]
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- All figures from [src: {src}] at the latest period; targets [{C.CONFIG_MARKER}]; ratios aggregate by "
        "implied daily flow, never by averaging.",
        f"- Historical view: monthly over-90 share per channel [derived: over90-trend] and inventory days per line "
        f"[derived: inventory-days-trend] are charted over the full history [src: {src}].",
        "- Verdict and expectation actuals carry the channel and line breach counts so a rollup cannot drop them "
        "[derived: v-main].",
    ]

    data = {
        "bq": "FQ-06",
        "series": [
            {"id": "dso-stat", "label": "Company DSO", "unit": "days", "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "Σ AR ÷ Σ (AR ÷ dso_days) over all rows of the latest period",
                            "inputs": [f"src: {src}", C.CONFIG_MARKER]},
             "provenance": {"dataset": AR_DS, "snapshot": snap},
             "points": [{"label": f"DSO at {latest}", "value": round(dso_company, 1) if dso_company is not None else None,
                         "sub": f"target {dso_t:.0f} days; over-90 share {o90_share_company:.1f}%"}]},
            {"id": "cash-trapped", "label": "Cash trapped above target", "unit": "USD M", "kind": "stat",
             "evidence_class": "derived",
             "derivation": {"method": "over-90 AR + Σ per line max(0, inventory − (inventory ÷ days) × target days)",
                            "inputs": [f"src: {src}", C.CONFIG_MARKER]},
             "provenance": {"dataset": AR_DS, "snapshot": snap},
             "points": [{"label": "over-90 receivables", "value": C.musd(o90_total)},
                        {"label": "inventory above target cover", "value": C.musd(excess_total)}]},
            {"id": "dso-by-channel", "label": "DSO by channel (latest)", "unit": "days", "evidence_class": "derived",
             "derivation": {"method": "Σ AR ÷ Σ (AR ÷ dso_days) per channel, latest period", "inputs": [f"src: {src}"]},
             "provenance": {"dataset": AR_DS, "snapshot": snap},
             "points": [{"label": g, "value": round(d, 1) if d is not None else None, "ar_musd": C.musd(a)}
                        for g, d, a, _, _ in ch_rows]},
            {"id": "dso-by-region", "label": "DSO by region (latest)", "unit": "days", "evidence_class": "derived",
             "derivation": {"method": "Σ AR ÷ Σ (AR ÷ dso_days) per region, latest period", "inputs": [f"src: {src}"]},
             "provenance": {"dataset": AR_DS, "snapshot": snap},
             "points": [{"label": g, "value": round(d, 1) if d is not None else None, "ar_musd": C.musd(a)}
                        for g, d, a, _ in reg_rows]},
            {"id": "over90-by-channel", "label": "Over-90 AR share by channel (latest)", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "Σ ar_over_90 ÷ Σ AR per channel, latest period", "inputs": [f"src: {src}", C.CONFIG_MARKER]},
             "provenance": {"dataset": AR_DS, "snapshot": snap},
             "points": [{"label": g, "value": round(s, 1), "over90_musd": C.musd(o)} for g, _, _, o, s in ch_rows]},
            {"id": "over90-trend", "label": "Over-90 AR share by channel, monthly", "unit": "%", "kind": "timeseries",
             "evidence_class": "derived",
             "derivation": {"method": "Σ ar_over_90 ÷ Σ AR per channel per month over the full history", "inputs": [f"src: {src}"]},
             "provenance": {"dataset": AR_DS, "snapshot": snap},
             "lines": o90_trend, "points": []},
            {"id": "inventory-days-by-line", "label": "Inventory days of cover by line (latest)", "unit": "days",
             "evidence_class": "derived",
             "derivation": {"method": "Σ inventory ÷ Σ (inventory ÷ inventory_days) per line, latest period",
                            "inputs": [f"src: {src}", C.CONFIG_MARKER]},
             "provenance": {"dataset": AR_DS, "snapshot": snap},
             "points": [{"label": l, "value": round(d, 1) if d is not None else None, "inventory_musd": C.musd(inv),
                         "excess_musd": C.musd(ex)} for l, d, inv, ex in inv_rows]},
            {"id": "inventory-days-trend", "label": "Inventory days by line, monthly", "unit": "days",
             "kind": "timeseries", "evidence_class": "derived",
             "derivation": {"method": "Σ inventory ÷ Σ (inventory ÷ inventory_days) per line per month; smaller lines combined",
                            "inputs": [f"src: {src}"]},
             "provenance": {"dataset": AR_DS, "snapshot": snap},
             "lines": inv_trend, "points": []},
            {"id": "subscription-ar", "label": "Subscription (cloud-suite) receivables", "unit": "USD M",
             "evidence_class": "unavailable",
             "provenance": {"note": "the working-capital cube (internal-ar-inventory) carries the five device "
                                    "lines only; subscription billing needs its own AR-aging feed."},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
