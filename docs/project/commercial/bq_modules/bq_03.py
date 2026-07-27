"""BQ-03 — Recurring-revenue mix: actuals vs the Y5 plan, and the FY2030 target decomposed.

Deterministic: computes ONLY from the pinned internal-financials and
internal-revenue-plan snapshots. See plans/BQ-03.md for the committed definitions
(recurring = subscription revenue_type; plan recurring proxied by the cloud-suite
line; contracted / modeled / aspiration defined against regulatory_dependency).
"""

import computations as C

FIN_DS = "commercial/internal-financials"
PLAN_DS = "commercial/internal-revenue-plan"

PLAN_YEARS = ["FY2026", "FY2027", "FY2028", "FY2029", "FY2030"]
DEP_ORDER = ["cleared", "letter-to-file", "pccp-enabled", "new-submission"]


def _musd(v):
    return f"${v / 1e6:,.1f}M"


def _fy_iso(fy):
    return f"{fy[2:6]}-01-01"


def run(corpus_root, out, pins):
    p = C.params_for("BQ-03")
    fin, fsnap = C.load_pin_csv(corpus_root, pins, FIN_DS)
    plan, psnap = C.load_pin_csv(corpus_root, pins, PLAN_DS)
    src = f"{FIN_DS}@{fsnap}"
    psrc = f"{PLAN_DS}@{psnap}"
    y5_target = int(p["y5_target_usd"])
    y5 = p["y5_period"]
    proxy_line = p["plan_recurring_proxy_line"]

    # ---- actual recurring share per fiscal year on file
    periods = sorted({r["period"] for r in fin})
    years = sorted({q[:4] for q in periods})
    last_year = years[-1]
    n_last_q = len([q for q in periods if q.startswith(last_year)])
    actuals = []  # (label, total, recurring, share)
    for y in years:
        yr_rows = [r for r in fin if r["period"].startswith(y)]
        tot = sum(int(r["revenue_usd"]) for r in yr_rows)
        rec = sum(int(r["revenue_usd"]) for r in yr_rows if r["revenue_type"] == "subscription")
        label = f"FY{y}" + ("H1" if y == last_year and n_last_q == 2 else "")
        actuals.append((label, tot, rec, C.pct(rec, tot)))

    # ---- plan recurring-proxy share per plan year
    plan_tot, plan_rec, plan_dep = {y: 0 for y in PLAN_YEARS}, {y: 0 for y in PLAN_YEARS}, {}
    proxy_dep = {}
    for r in plan:
        y = "FY2026" if r["period"].startswith("2026-Q") else r["period"]
        if y not in plan_tot:
            continue
        v = int(r["revenue_usd"])
        plan_tot[y] += v
        if r["product_line"] == proxy_line:
            plan_rec[y] += v
            proxy_dep.setdefault(y, {d: 0 for d in DEP_ORDER})
            proxy_dep[y][r["regulatory_dependency"]] += v
        plan_dep.setdefault(y, {d: 0 for d in DEP_ORDER})
        plan_dep[y][r["regulatory_dependency"]] += v

    # ---- FY2030 decomposition into the three buckets
    d30 = plan_dep[y5]
    contracted = d30["cleared"]
    ltf = d30["letter-to-file"]
    aspiration = d30["pccp-enabled"] + d30["new-submission"]
    t30 = plan_tot[y5]
    target_delta = t30 - y5_target

    today_label, _, _, today_share = actuals[-1]
    y5_share = C.pct(plan_rec[y5], t30)
    asp_share = C.pct(aspiration, t30)

    # ---- recurring-specific decomposition (red-team finding, ben/108): the blended
    # share understates the bet on the very revenue the question is about, so the
    # same buckets are also computed WITHIN the recurring proxy line alone
    r30 = proxy_dep.get(y5, {d: 0 for d in DEP_ORDER})
    rec_total = plan_rec[y5]
    rec_cleared = r30["cleared"]
    rec_ltf = r30["letter-to-file"]
    rec_aspiration = r30["pccp-enabled"] + r30["new-submission"]
    rec_asp_share = C.pct(rec_aspiration, rec_total)
    cleared_nonproxy = contracted - rec_cleared

    # E-03.1: strictly increasing actual share
    shares = [a[3] for a in actuals]
    increasing = all(b > a for a, b in zip(shares, shares[1:]))

    headline = (f"Recurring revenue is {today_share}% of revenue today ({today_label}) vs "
                f"{y5_share}% planned for {y5}; of the {_musd(t30)} target, "
                f"{_musd(contracted)} rides on already-cleared products, {_musd(ltf)} on "
                f"letter-to-file changes, and {_musd(aspiration)} ({asp_share}%) sits behind FDA "
                f"decisions not yet received — and within the {_musd(rec_total)} recurring proxy "
                f"itself, {_musd(rec_aspiration)} ({rec_asp_share}%) is behind those decisions")

    narrative = {"issues": [], "risks": [], "watch": []}
    if not increasing:
        narrative["issues"].append({
            "id": "I1", "severity": "medium",
            "statement": "Recurring share is not strictly increasing across the fiscal years on "
                         f"file ({'; '.join(f'{a[0]} {a[3]}%' for a in actuals)}) — the mix-shift "
                         "story is behind its own trend line",
            "action": "Reconcile subscription-billing actuals against the attach-rate read "
                      "(BQ-29) and bring the variance to the next board review",
            "evidence": ["derived: recurring-share-trend", f"src: {src}"],
        })
    if asp_share > 40:
        narrative["risks"].append({
            "id": "R1", "severity": "high",
            "statement": f"{asp_share}% of the {y5} target ({_musd(aspiration)}) is aspiration — "
                         f"revenue behind pccp-enabled and new-submission FDA decisions not yet "
                         f"received — and the blended figure understates the recurring-specific "
                         f"bet: within the {proxy_line} recurring proxy alone, {rec_asp_share}% "
                         f"({_musd(rec_aspiration)} of {_musd(rec_total)}) sits behind those "
                         f"decisions; the regulatory-exposure and slip arithmetic is BQ-05's answer",
            "mitigation": "Hold the aspiration bucket against BQ-05's exposure threshold and slip "
                          "scenarios; require a contingency line in the plan narrative",
            "evidence": ["derived: y5-decomposition", "derived: y5-recurring-decomposition",
                         f"src: {psrc}"],
        })
    if target_delta != 0:
        narrative["watch"].append({
            "id": "W1",
            "statement": f"The pinned plan's {y5} total ({_musd(t30)}) differs from the catalog's "
                         f"target constant by {_musd(target_delta)} — reported, not smoothed over",
            "evidence": ["derived: y5-decomposition", f"src: {psrc}", "config: commercial.yml"],
        })
    narrative["watch"].append({
        "id": f"W{len(narrative['watch']) + 1}",
        "statement": "Plan-side recurring uses the cloud-suite proxy (the plan carries no revenue "
                     "type) — device-line service contracts that recur are not counted, and any "
                     "non-recurring cloud-suite revenue is; both directions stated",
        "evidence": ["config: commercial.yml", f"src: {psrc}"],
    })

    exp_results = {
        "E-03.1": ("; ".join(f"{a[0]}: {a[3]}%" for a in actuals)
                   + (" — strictly increasing" if increasing else " — NOT strictly increasing"),
                   "met" if increasing else "not-met",
                   ["derived: recurring-share-trend"]),
    }
    exps = C.evaluate_expectations("BQ-03", exp_results)

    rl = [
        "# BQ-03 — Recurring mix today vs the Y5 plan — and what the target is made of",
        "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [src: {psrc}]", "",
        "## Recurring share — actuals by fiscal year", "",
        "_Recurring = subscription revenue only (consumables re-order but are not counted;",
        "conservative, per the analysis plan). The current fiscal year is a half-year of",
        "actuals and is labeled as such, never annualized._", "",
        "| Fiscal year | Total revenue | Subscription revenue | Recurring share |",
        "|---|---|---|---|",
    ]
    for label, tot, rec, share in actuals:
        rl.append(f"| {label} [src: {src}] | {_musd(tot)} | {_musd(rec)} | {share}% |")
    rl += [
        "",
        "## Plan trajectory — recurring proxy per plan year", "",
        f"- Plan recurring is proxied by the {proxy_line} line "
        f"[config: commercial.yml] [src: {psrc}]:",
        "",
        "| Plan year | Plan total | Cloud-suite (recurring proxy) | Share |",
        "|---|---|---|---|",
    ]
    for y in PLAN_YEARS:
        rl.append(f"| {y} [src: {psrc}] | {_musd(plan_tot[y])} | {_musd(plan_rec[y])} | "
                  f"{C.pct(plan_rec[y], plan_tot[y])}% |")
    rl += [
        "",
        f"## The {y5} target decomposed — contracted / modeled / aspiration", "",
        "_Buckets are defined against each plan row's regulatory_dependency (see the analysis",
        "plan): cleared revenue needs no permission; letter-to-file needs execution and internal",
        "documentation only; the rest needs FDA decisions that have not been received._", "",
        "| Bucket | Dependency | Revenue | Share of target |",
        "|---|---|---|---|",
        f"| contracted (upper bound — cleared today, not contractually committed) [src: {psrc}] "
        f"[derived: y5-decomposition] | cleared | {_musd(contracted)} | {C.pct(contracted, t30)}% |",
        f"| modeled [src: {psrc}] [derived: y5-decomposition] | letter-to-file | {_musd(ltf)} | "
        f"{C.pct(ltf, t30)}% |",
        f"| aspiration [src: {psrc}] [derived: y5-decomposition] | pccp-enabled + new-submission | "
        f"{_musd(aspiration)} | {asp_share}% |",
        "",
        f"- Pinned {y5} plan total {_musd(t30)} vs catalog target constant {_musd(y5_target)} "
        f"(delta {_musd(target_delta)}) [derived: y5-decomposition] [config: commercial.yml]",
        "",
        f"### The recurring bet specifically — the same buckets within the {proxy_line} proxy", "",
        "_The blended decomposition above spans all six lines; the question is about recurring",
        "revenue, so the same cut is shown for the recurring proxy line alone — both figures",
        "stand together, neither replaces the other._", "",
        f"- Within the {y5} recurring proxy ({proxy_line}, {_musd(rec_total)}): "
        f"{_musd(rec_aspiration)} ({rec_asp_share}%) sits behind FDA decisions not yet received, "
        f"vs {asp_share}% blended across all lines — {_musd(rec_cleared)} cleared and "
        f"{_musd(rec_ltf)} letter-to-file [derived: y5-recurring-decomposition] [src: {psrc}] "
        f"[config: commercial.yml]",
        f"- Of the blended {_musd(contracted)} cleared bucket, {_musd(cleared_nonproxy)} is "
        f"non-recurring (device) revenue — the cleared cushion mostly sits outside the recurring "
        f"story [derived: y5-recurring-decomposition] [derived: y5-decomposition] [src: {psrc}]",
    ]
    rl += C.expectations_section(exps)
    rl += C.narrative_section(narrative)
    rl += [
        "## Method & provenance", "",
        f"- Actual shares measured from [src: {src}] (revenue_type = subscription ÷ total, per",
        f"  fiscal year on file); plan shares and the decomposition from [src: {psrc}].",
        f"- Bucket definitions and the recurring proxy are committed in the analysis plan and",
        f"  parameterized in [config: commercial.yml].",
        "- No contract/backlog dataset exists — the contracted bucket is an upper bound (stated);",
        "  prior plan versions are not snapshotted, so target-evolution history is a stated gap.",
    ]

    data = {
        "bq": "BQ-03",
        "series": [
            {"id": "recurring-stat", "label": "Recurring share — today vs Y5 plan", "unit": "%",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": "subscription revenue ÷ total revenue (actuals); cloud-suite "
                                      "proxy ÷ plan total (plan)",
                            "inputs": [f"src: {src}", f"src: {psrc}", "config: commercial.yml"]},
             "provenance": {"dataset": FIN_DS, "snapshot": fsnap},
             "points": [
                 {"label": f"recurring share, {today_label} actuals", "value": today_share},
                 {"label": f"planned recurring-proxy share, {y5}", "value": y5_share},
                 {"label": f"share of {y5} target behind FDA decisions not yet received",
                  "value": asp_share},
             ]},
            {"id": "recurring-share-trend", "label": "Recurring share — actuals vs plan trajectory",
             "unit": "%", "kind": "timeseries", "evidence_class": "derived",
             "derivation": {"method": "actual: subscription ÷ total per fiscal year; plan: "
                                      "cloud-suite proxy ÷ plan total per plan year",
                            "inputs": [f"src: {src}", f"src: {psrc}", "config: commercial.yml"]},
             "provenance": {"dataset": FIN_DS, "snapshot": fsnap},
             "lines": [
                 {"label": "actual (current FY = H1)",
                  "points": [{"x": _fy_iso(a[0]), "y": a[3]} for a in actuals]},
                 {"label": "plan (cloud-suite proxy)",
                  "points": [{"x": _fy_iso(y), "y": C.pct(plan_rec[y], plan_tot[y])}
                             for y in PLAN_YEARS]},
             ], "points": []},
            {"id": "plan-by-bucket", "label": "Plan revenue by bucket per plan year ($M)",
             "unit": "$M", "kind": "timeseries", "evidence_class": "derived",
             "derivation": {"method": "per plan year: contracted = cleared; modeled = "
                                      "letter-to-file; aspiration = pccp-enabled + new-submission",
                            "inputs": [f"src: {psrc}", "config: commercial.yml"]},
             "provenance": {"dataset": PLAN_DS, "snapshot": psnap},
             "lines": [
                 {"label": "contracted (cleared)",
                  "points": [{"x": _fy_iso(y), "y": round(plan_dep[y]["cleared"] / 1e6, 1)}
                             for y in PLAN_YEARS]},
                 {"label": "modeled (letter-to-file)",
                  "points": [{"x": _fy_iso(y), "y": round(plan_dep[y]["letter-to-file"] / 1e6, 1)}
                             for y in PLAN_YEARS]},
                 {"label": "aspiration (pccp + new-submission)",
                  "points": [{"x": _fy_iso(y),
                              "y": round((plan_dep[y]["pccp-enabled"]
                                          + plan_dep[y]["new-submission"]) / 1e6, 1)}
                             for y in PLAN_YEARS]},
             ], "points": []},
            {"id": "y5-decomposition", "label": f"{y5} target by bucket ($M)", "unit": "$M",
             "evidence_class": "derived",
             "derivation": {"method": f"{y5} plan revenue summed by regulatory_dependency, grouped "
                                      "into the three plan-defined buckets",
                            "inputs": [f"src: {psrc}", "config: commercial.yml"]},
             "provenance": {"dataset": PLAN_DS, "snapshot": psnap},
             "points": [
                 {"label": "contracted (cleared)", "value": round(contracted / 1e6, 1)},
                 {"label": "modeled (letter-to-file)", "value": round(ltf / 1e6, 1)},
                 {"label": "aspiration (pccp + new-submission)", "value": round(aspiration / 1e6, 1)},
             ]},
            {"id": "y5-recurring-decomposition",
             "label": f"{y5} recurring proxy ({proxy_line}) by bucket ($M)", "unit": "$M",
             "evidence_class": "derived",
             "derivation": {"method": f"{y5} plan revenue of the {proxy_line} line (the recurring "
                                      "proxy) summed by regulatory_dependency, grouped into the "
                                      "three plan-defined buckets; dependent share = (pccp-enabled "
                                      "+ new-submission) ÷ proxy-line total",
                            "inputs": [f"src: {psrc}", "config: commercial.yml",
                                       "derived: y5-decomposition"]},
             "provenance": {"dataset": PLAN_DS, "snapshot": psnap},
             "points": [
                 {"label": "contracted (cleared)", "value": round(rec_cleared / 1e6, 1)},
                 {"label": "modeled (letter-to-file)", "value": round(rec_ltf / 1e6, 1)},
                 {"label": "aspiration (pccp + new-submission)",
                  "value": round(rec_aspiration / 1e6, 1), "share_pct": rec_asp_share},
             ]},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "derived"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, rl, data)
