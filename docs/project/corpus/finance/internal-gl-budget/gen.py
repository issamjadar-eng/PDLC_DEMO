#!/usr/bin/env python3
"""Demo generator — monthly GL actual vs budget by function x cost center, 2026-01 ..
2026-08. Seeded, deterministic. Stand-in for the general-ledger / FP&A budget export.

Coherence anchors:
- Operating-expense budget ~= $3.55M / month (~$42.6M / year) against the
  commercial/internal-financials FY2025 revenue anchor (~$80.5M) — a plausible
  opex envelope for the demo company.
- Narrative knobs (modeled, not observed):
  * R&D over budget from 2026-03 — the PP3500 firmware 3.4 campaign (cost center
    RD-FW: contractors + test rigs, +3 contract heads).
  * Regulatory/Quality over budget on external consulting (RQ-EXT runs ~1.8x).
  * Sales & Marketing UNDER budget — hiring lag: budgeted heads ramp, actual lags
    by 3-5 heads in SM-NA / SM-INTL, spend follows.
  * Manufacturing, G&A, Service within +/-3%.
- No clocks: literal periods; as_of 2026-08-31.
"""
import argparse, csv, json, random

BANNER = "_Demo sample data - not for clinical use._"

PERIODS = [f"2026-{m:02d}" for m in range(1, 9)]
# function -> [(cost_center, monthly budget usd, headcount budget)]
PLAN = {
    "R&D": [("RD-FW", 380_000, 18), ("RD-SW", 320_000, 15), ("RD-HW", 300_000, 12)],
    "Regulatory/Quality": [("RQ-REG", 130_000, 6), ("RQ-QA", 150_000, 8), ("RQ-EXT", 70_000, 0)],
    "Manufacturing": [("MF-OPS", 320_000, 22), ("MF-SUP", 180_000, 8)],
    "Sales & Marketing": [("SM-NA", 420_000, 20), ("SM-INTL", 280_000, 12), ("SM-MKT", 200_000, 7)],
    "G&A": [("GA-FIN", 250_000, 9), ("GA-IT", 200_000, 7)],
    "Service": [("SV-FIELD", 220_000, 14), ("SV-DEPOT", 130_000, 7)],
}
# per-cost-center actual/budget factor as a function of month index (0 = 2026-01)
def factor(cc, mi):
    if cc == "RD-FW":
        return 1.02 if mi < 2 else 1.18 + 0.015 * (mi - 2)      # firmware 3.4 campaign
    if cc == "RD-SW":
        return 1.03
    if cc == "RD-HW":
        return 0.98
    if cc == "RQ-EXT":
        return 1.6 + 0.05 * mi                                  # external consulting
    if cc in ("RQ-REG", "RQ-QA"):
        return 1.02
    if cc in ("SM-NA", "SM-INTL"):
        return 0.88
    if cc == "SM-MKT":
        return 0.97
    if cc.startswith("MF"):
        return 1.01
    if cc.startswith("GA"):
        return 1.01
    return 1.02                                                 # service


def heads(cc, hc_budget, mi, rng):
    if cc in ("SM-NA", "SM-INTL"):
        budget = hc_budget + mi                                 # hiring plan ramps +1/month
        actual = max(hc_budget - 1, budget - rng.choice([3, 4, 5]))
        return budget, actual
    if cc == "RD-FW":
        return hc_budget, hc_budget + (3 if mi >= 2 else 0)      # contract heads on the campaign
    if cc == "RQ-EXT":
        return 0, 0
    return hc_budget, hc_budget + rng.choice([-1, 0, 0, 0, 1])


def make_rows(rng):
    rows = []
    for mi, period in enumerate(PERIODS):
        for func, ccs in PLAN.items():
            for cc, budget, hc in ccs:
                actual = budget * factor(cc, mi) * (1 + rng.uniform(-0.02, 0.02))
                hb, ha = heads(cc, hc, mi, rng)
                rows.append({
                    "period": period, "function": func, "cost_center": cc,
                    "budget_usd": int(budget), "actual_usd": int(round(actual)),
                    "headcount_budget": hb, "headcount_actual": ha,
                })
    return rows


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("--seed", type=int, default=42); g.add_argument("--out", required=True)
    n = sub.add_parser("normalize"); n.add_argument("raw"); n.add_argument("out")
    a = p.parse_args()
    if a.cmd == "gen":
        rng = random.Random(a.seed)
        rows = make_rows(rng)
        json.dump({"banner": BANNER, "generator": "gen.py", "seed": a.seed,
                   "as_of": "2026-08-31", "rows": rows},
                  open(f"{a.out}/export.json", "w"), indent=1)
    else:
        rows = json.load(open(f"{a.raw}/export.json"))["rows"]
        w = csv.DictWriter(open(f"{a.out}/records.csv", "w", newline=""), fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


main()
