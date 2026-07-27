"""BQ-02 — Concentration: GPOs, accounts, PCA franchise, and the anchor-GPO loss scenario.

Deterministic: computes ONLY from the pinned internal-sales-accounts,
internal-revenue-plan, and internal-financials snapshots. See plans/BQ-02.md for the
committed definitions (direct-book basis + the basis-sensitivity disclosure against
total revenue, anchor-GPO selection, constant-dent loss-scenario method).
"""

import sys

import computations as C

ACC_DS = "commercial/internal-sales-accounts"
PLAN_DS = "commercial/internal-revenue-plan"
FIN_DS = "commercial/internal-financials"

PLAN_YEARS = ["FY2026", "FY2027", "FY2028", "FY2029", "FY2030"]


def _musd(v):
    return f"${v / 1e6:,.1f}M"


def _fy_iso(fy):
    return f"{fy[2:]}-01-01"


def _plan_year_totals(plan_rows):
    """Per-year plan totals; FY2026 = sum of its quarterly rows. Also counts rows whose
    period falls outside the configured plan window — silent drops rot the scenario
    table on a refreshed plan (code-review finding, ben/108)."""
    tot = {y: 0 for y in PLAN_YEARS}
    unmatched = 0
    for r in plan_rows:
        y = "FY2026" if r["period"].startswith("2026-Q") else r["period"]
        if y in tot:
            tot[y] += int(r["revenue_usd"])
        else:
            unmatched += 1
    return tot, unmatched


def run(corpus_root, out, pins):
    p = C.params_for("BQ-02")
    acc, asnap = C.load_pin_csv(corpus_root, pins, ACC_DS)
    plan, psnap = C.load_pin_csv(corpus_root, pins, PLAN_DS)
    fin, fsnap = C.load_pin_csv(corpus_root, pins, FIN_DS)
    src = f"{ACC_DS}@{asnap}"
    psrc = f"{PLAN_DS}@{psnap}"
    fin_src = f"{FIN_DS}@{fsnap}"
    fy = p["fy"]
    thr = float(p["concentration_threshold_pct"])
    pca_lines = list(p["pca_franchise_lines"])
    pump_lines = list(p["pca_pump_lines"])
    top3_gate = float(p["top3_narrative_gate_pct"])

    fy_rows = [r for r in acc if r["fy"] == fy]
    total = sum(int(r["revenue_usd"]) for r in fy_rows)

    # GPO shares (basis year)
    by_gpo = {}
    for r in fy_rows:
        by_gpo[r["gpo"]] = by_gpo.get(r["gpo"], 0) + int(r["revenue_usd"])
    gpos_only = {g: v for g, v in by_gpo.items() if g != "independent"}
    anchor = max(gpos_only, key=gpos_only.get)
    anchor_rev = gpos_only[anchor]
    anchor_share = C.pct(anchor_rev, total)
    # guardrail comparisons run on raw fractions; C.pct is display-only (code-review
    # finding, ben/108: rounded compares are the knife-edge class at 30.0x)
    def _raw_share(v):
        return 100.0 * v / total if total else 0.0
    anchor_share_raw = _raw_share(anchor_rev)
    direct_breaches = anchor_share_raw > thr
    over = [(g, C.pct(v, total)) for g, v in sorted(gpos_only.items(), key=lambda kv: -kv[1])
            if _raw_share(v) > thr]

    # top-3 accounts
    by_acct = {}
    for r in fy_rows:
        by_acct[r["account_name"]] = by_acct.get(r["account_name"], 0) + int(r["revenue_usd"])
    top3 = sorted(by_acct.items(), key=lambda kv: -kv[1])[:3]
    # share of the summed top-3 revenue, rounded once at render — not a sum of rounded shares
    top3_rev = sum(v for _, v in top3)
    top3_share_raw = _raw_share(top3_rev)
    top3_share = C.pct(top3_rev, total)

    # PCA franchise share (franchise and pumps-only rosters both from config)
    pca_rev = sum(int(r["revenue_usd"]) for r in fy_rows if r["product_line"] in pca_lines)
    pumps_rev = sum(int(r["revenue_usd"]) for r in fy_rows
                    if r["product_line"] in pump_lines)
    pca_share = C.pct(pca_rev, total)
    pumps_share = C.pct(pumps_rev, total)

    # GPO-share history across the fiscal years on file
    fys = sorted({r["fy"] for r in acc})
    gpo_hist = []
    for g in sorted(gpos_only):
        pts = []
        for f in fys:
            frows = [r for r in acc if r["fy"] == f]
            ftot = sum(int(r["revenue_usd"]) for r in frows)
            gv = sum(int(r["revenue_usd"]) for r in frows if r["gpo"] == g)
            pts.append({"x": _fy_iso(f), "y": C.pct(gv, ftot)})
        gpo_hist.append({"label": g, "points": pts})

    # basis sensitivity: the direct book vs total revenue (red-team finding, ben/108).
    # The account book is fiscal-year keyed; the financial ledger is calendar-quarter
    # keyed — FY maps to the same calendar year by dataset construction.
    cy = fy[2:]
    total_rev_cy = sum(int(r["revenue_usd"]) for r in fin if r["period"].startswith(cy))
    coverage_pct = C.pct(total, total_rev_cy)
    anchor_floor_pct = C.pct(anchor_rev, total_rev_cy)
    floor_breaches = (100.0 * anchor_rev / total_rev_cy > thr) if total_rev_cy else False

    # anchor-loss scenario: constant FY-basis dent off each plan year
    plan_tot, plan_unmatched = _plan_year_totals(plan)
    if plan_unmatched:
        print(f"bq_02: WARNING — {plan_unmatched} plan rows fall outside the configured "
              f"plan window {PLAN_YEARS[0]}..{PLAN_YEARS[-1]} and are excluded from the "
              f"loss-scenario table", file=sys.stderr)
    scenario = [{"x": _fy_iso(y), "y": round((plan_tot[y] - anchor_rev) / 1e6, 1)} for y in PLAN_YEARS]
    baseline = [{"x": _fy_iso(y), "y": round(plan_tot[y] / 1e6, 1)} for y in PLAN_YEARS]
    dent_fy26_pct = C.pct(anchor_rev, plan_tot["FY2026"])

    headline = (f"{anchor} carries {anchor_share}% of {fy} direct-book revenue — "
                + ("above" if direct_breaches else "under")
                + f" the "
                f"{thr:.0f}% guardrail on the direct-book basis, and basis-sensitive: the direct "
                f"book covers {coverage_pct}% of total {fy} revenue, and {anchor}'s floor share "
                f"of TOTAL revenue is {anchor_floor_pct}%"
                + ("" if floor_breaches else " (under the guardrail)")
                + f"; top-3 accounts {top3_share}%, PCA franchise {pca_share}%; "
                f"losing the anchor GPO dents every plan year by {_musd(anchor_rev)} "
                f"({dent_fy26_pct}% of the FY2026 plan) under the stated constant-dent scenario")

    narrative = {"issues": [], "risks": [], "watch": []}
    ni = 0
    for g, share in over:
        ni += 1
        narrative["issues"].append({
            "id": f"I{ni}", "severity": "high",
            "statement": f"{g} holds {share}% of {fy} direct-book revenue — over the {thr:.0f}% "
                         f"concentration guardrail",
            "action": "Bring contract-renewal timeline and diversification options to the board; "
                      "acquire GPO contract terms as a corpus dataset so exposure gets a date",
            "evidence": ["derived: share-by-gpo", f"src: {src}", "config: commercial.yml"],
        })
    rn = 0
    if top3_share_raw > top3_gate:
        rn += 1
        narrative["risks"].append({
            "id": f"R{rn}", "severity": "medium",
            "statement": f"Top-3 accounts hold {top3_share}% of {fy} direct-book revenue — "
                         f"account-level concentration compounds the GPO concentration "
                         f"(largest: {top3[0][0]} at {C.pct(top3[0][1], total)}%)",
            "mitigation": "Named-account retention plans for the top accounts; monitor share "
                          "annually alongside the GPO read",
            "evidence": ["derived: top-accounts", f"src: {src}"],
        })
    rn += 1
    narrative["risks"].append({
        "id": f"R{rn}", "severity": "medium",
        "statement": f"The loss scenario is a floor, not a forecast: the dent is held constant at the "
                     f"{fy} anchor book ({_musd(anchor_rev)}) while the plan grows, and it covers the "
                     f"direct book only — the true dent of losing {anchor} grows with the plan",
        "mitigation": "Re-run with anchor-share-of-plan scaling once GPO-level plan attribution "
                      "exists; treat the charted scenario as the minimum impact",
        "evidence": ["derived: plan-loss-scenario", f"src: {psrc}"],
    })
    rn += 1
    narrative["risks"].append({
        "id": f"R{rn}", "severity": "medium",
        "statement": f"The E-02.1 verdict is basis-sensitive: the guardrail is worded against "
                     f"annual revenue but tested on the direct book, which covers {coverage_pct}% "
                     f"of total {fy} revenue — {anchor} "
                     + ("breaches" if direct_breaches else "does not breach")
                     + f" on the direct book "
                     f"({anchor_share}%) while its floor share of total revenue "
                     f"({anchor_floor_pct}%) "
                     + (("also breaches" if floor_breaches else "does not breach")
                        if direct_breaches else
                        ("breaches" if floor_breaches else "also does not breach")),
        "mitigation": "Acquire account-attributed consumables/service revenue (or GPO attribution "
                      "on the distributor book) to close the denominator gap; until then read the "
                      "verdict on both bases, not one",
        "evidence": ["derived: basis-sensitivity", f"src: {src}", f"src: {fin_src}"],
    })
    narrative["watch"].append({
        "id": "W1",
        "statement": f"PCA-franchise dependence ({pca_share}% of {fy} direct book incl. Cloud Suite; "
                     f"pumps alone {pumps_share}%) — single-franchise exposure rides on top of the "
                     f"customer concentration",
        "evidence": ["derived: franchise-share", f"src: {src}"],
    })

    exp_results = {
        "E-02.1": (f"{anchor} at {anchor_share}% of {fy} direct-book revenue"
                   + (f"; all other GPOs within the guardrail" if len(over) <= 1 else "")
                   + f" — BASIS-SENSITIVE: the expectation says annual revenue, but the test "
                     f"denominator is the direct book ({coverage_pct}% of total {fy} revenue); "
                     f"{anchor}'s floor share of total revenue is {anchor_floor_pct}%, which "
                   + ("also breaches" if floor_breaches else "does NOT breach")
                   + " the guardrail (distributor-routed revenue unattributed)",
                   "not-met" if over else "met",
                   ["derived: share-by-gpo", "derived: basis-sensitivity"]),
    }
    exps = C.evaluate_expectations("BQ-02", exp_results)

    rl = [
        "# BQ-02 — Concentration: GPOs, accounts, franchise — and the anchor-GPO loss scenario",
        "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [src: {psrc}] "
        f"[config: commercial.yml]", "",
        f"## {fy} direct-book revenue by GPO [src: {src}]", "",
        "_Basis: the account-attributed direct book (hardware + subscription) — consumables and",
        "service flow through distributors and are not in these shares (see the analysis plan)._", "",
        "| GPO | Revenue | Share |",
        "|---|---|---|",
    ]
    for g, v in sorted(by_gpo.items(), key=lambda kv: -kv[1]):
        flag = " ⚠️" if g != "independent" and _raw_share(v) > thr else ""
        rl.append(f"| {g} [src: {src}] | {_musd(v)} | {C.pct(v, total)}%{flag} |")
    rl += [
        "",
        f"- Guardrail: no GPO above {thr:.0f}% of annual revenue [config: commercial.yml]",
        f"- {fy} direct-book total: {_musd(total)} [src: {src}]",
        "",
        "## Basis sensitivity (disclosed, not absorbed)", "",
        "_The E-02.1 guardrail is worded against **annual revenue**, but the only "
        "account-attributed denominator is the direct book — the verdict is basis-dependent "
        "and both bases are shown [derived: basis-sensitivity]._", "",
        f"- The direct book ({_musd(total)}) covers {coverage_pct}% of total {fy} revenue "
        f"({_musd(total_rev_cy)}) [derived: basis-sensitivity] [src: {src}] [src: {fin_src}]",
        f"- {anchor}'s floor share of TOTAL {fy} revenue is {anchor_floor_pct}% — a lower bound: "
        f"it takes none of the distributor-routed consumables/service book, whose account "
        f"attribution does not exist in the corpus; the true share is unknowable above that floor "
        f"[derived: basis-sensitivity] [src: {fin_src}]",
        f"- Verdict by basis: direct book {anchor_share}% — "
        + ("BREACHES" if direct_breaches else "within")
        + f" the {thr:.0f}% guardrail; floor-of-total {anchor_floor_pct}% — "
        + ("BREACHES" if floor_breaches else "does NOT breach")
        + " it [derived: basis-sensitivity] [config: commercial.yml]",
        "",
        f"## Top-3 accounts ({fy}) [src: {src}]", "",
        "| Account | Revenue | Share |",
        "|---|---|---|",
    ]
    for name, v in top3:
        rl.append(f"| {name} [src: {src}] | {_musd(v)} | {C.pct(v, total)}% |")
    rl += [
        "",
        f"- Top-3 combined: {top3_share}% of {fy} direct-book revenue [derived: top-accounts]",
        "",
        "## Franchise concentration", "",
        f"- PCA franchise ({' + '.join(pca_lines)} per [config: commercial.yml]): "
        f"{pca_share}% of {fy} direct book; pumps alone ({' + '.join(pump_lines)}) {pumps_share}% "
        f"[derived: franchise-share] [src: {src}]",
        "",
        "## Anchor-GPO loss scenario vs the plan trajectory", "",
        f"- Method (stated): subtract {anchor}'s {fy} direct-book revenue ({_musd(anchor_rev)}), held "
        f"constant, from each plan year — a deliberate floor: the dent is not grown with the plan "
        f"and covers the direct book only [derived: plan-loss-scenario] [src: {psrc}] [src: {src}]",
        "",
        "| Plan year | Plan of record | Minus anchor GPO | Dent |",
        "|---|---|---|---|",
    ]
    for y in PLAN_YEARS:
        rl.append(f"| {y} [src: {psrc}] [derived: plan-loss-scenario] | {_musd(plan_tot[y])} | "
                  f"{_musd(plan_tot[y] - anchor_rev)} | {C.pct(anchor_rev, plan_tot[y])}% |")
    if plan_unmatched:
        rl += [
            "",
            f"- ⚠ {plan_unmatched} plan rows fall outside the configured plan window "
            f"{PLAN_YEARS[0]}..{PLAN_YEARS[-1]} and are NOT in the table above — extend the "
            f"window before trusting the scenario on a refreshed plan [src: {psrc}]",
        ]
    rl += C.expectations_section(exps)
    rl += C.narrative_section(narrative)
    rl += [
        "## Method & provenance", "",
        f"- Shares measured from the account book [src: {src}]; plan trajectory from the plan of "
        f"record [src: {psrc}]; guardrail and franchise definition in [config: commercial.yml].",
        f"- GPO-share history across the fiscal years on file is charted "
        f"[derived: gpo-share-trend] [src: {src}].",
        "- Contract terms, renewal dates, and total-P&L (consumables/service) concentration are",
        "  stated data gaps — no series is faked for them (see the analysis plan).",
    ]

    data = {
        "bq": "BQ-02",
        "series": [
            {"id": "concentration-stat", "label": "Concentration headline", "unit": "%",
             "kind": "stat", "evidence_class": "measured",
             "provenance": {"dataset": ACC_DS, "snapshot": asnap},
             "points": [
                 {"label": f"{anchor} share of {fy} direct-book revenue", "value": anchor_share},
                 {"label": "top-3 accounts share", "value": top3_share},
                 {"label": "PCA-franchise share (incl. Cloud Suite)", "value": pca_share},
             ]},
            {"id": "share-by-gpo", "label": f"{fy} direct-book revenue share by GPO", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "GPO revenue ÷ total direct-book revenue in the basis year",
                            "inputs": [f"src: {src}"]},
             "provenance": {"dataset": ACC_DS, "snapshot": asnap},
             "points": [{"label": g, "value": C.pct(v, total)}
                        for g, v in sorted(by_gpo.items(), key=lambda kv: -kv[1])]},
            {"id": "top-accounts", "label": f"Top-3 accounts, {fy} direct book ($M)", "unit": "$M",
             "evidence_class": "measured",
             "provenance": {"dataset": ACC_DS, "snapshot": asnap},
             "points": [{"label": n, "value": round(v / 1e6, 2), "share_pct": C.pct(v, total)}
                        for n, v in top3]},
            {"id": "franchise-share", "label": f"{fy} direct-book share by franchise cut", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "revenue of the configured franchise lines ÷ total direct-book "
                                      "revenue in the basis year",
                            "inputs": [f"src: {src}", "config: commercial.yml"]},
             "provenance": {"dataset": ACC_DS, "snapshot": asnap},
             "points": [{"label": "PCA franchise incl. Cloud Suite", "value": pca_share},
                        {"label": "PCA pumps only", "value": pumps_share}]},
            {"id": "basis-sensitivity", "label": f"E-02.1 basis sensitivity — direct book vs total "
                                                 f"{fy} revenue", "unit": "%",
             "evidence_class": "derived",
             "derivation": {"method": "direct-book coverage = direct-book total ÷ total calendar-"
                                      "year revenue from the financial ledger; anchor floor-of-"
                                      "total = anchor GPO direct-book revenue ÷ total revenue "
                                      "(lower bound — distributor-routed book unattributed)",
                            "inputs": [f"src: {src}", f"src: {fin_src}", "derived: share-by-gpo"]},
             "provenance": {"dataset": FIN_DS, "snapshot": fsnap},
             "points": [
                 {"label": f"direct-book coverage of total {fy} revenue", "value": coverage_pct},
                 {"label": f"{anchor} share of direct book (tested basis)", "value": anchor_share},
                 {"label": f"{anchor} floor share of total revenue (alternative basis)",
                  "value": anchor_floor_pct},
             ]},
            {"id": "gpo-share-trend", "label": "GPO share of direct-book revenue by FY", "unit": "%",
             "kind": "timeseries", "evidence_class": "derived",
             "derivation": {"method": "per fiscal year on file: GPO revenue ÷ that year's total "
                                      "direct-book revenue",
                            "inputs": [f"src: {src}"]},
             "provenance": {"dataset": ACC_DS, "snapshot": asnap},
             "lines": gpo_hist, "points": []},
            {"id": "plan-loss-scenario", "label": "Plan of record vs minus-anchor-GPO scenario ($M)",
             "unit": "$M", "kind": "timeseries", "evidence_class": "derived",
             "derivation": {"method": f"plan-year total minus the anchor GPO's {fy} direct-book "
                                      "revenue held constant (stated floor scenario)",
                            "inputs": [f"src: {psrc}", f"src: {src}", "derived: share-by-gpo"]},
             "provenance": {"dataset": PLAN_DS, "snapshot": psnap},
             "lines": [{"label": "plan of record", "points": baseline},
                       {"label": "minus anchor GPO", "points": scenario}],
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, rl, data)
