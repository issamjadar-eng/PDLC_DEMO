#!/usr/bin/env python3
"""Demo generator — standard unit costs by product line x revenue type x quarter.
Seeded, deterministic. Stand-in for the ERP standard-cost roll-up (the cost
accounting "standard" each unit is booked at, with its material / labor /
overhead split). Actual unit cost is NOT in this dataset — it is derived by
consumers from commercial/internal-financials (cogs_usd / units); the
standard-vs-actual variance is the join of the two.

Coherence anchors (locked against commercial/internal-financials/gen.py):
- Same product lines (IP5000, PP3000, PP3500, SP6000, SP6500, cloud-suite),
  revenue types (hardware|consumables|service|subscription) and quarters
  (2024-Q1 .. 2026-Q2). Unit prices (ASP) are the financials' constants, so a
  standard expressed as ASP x standard-cost ratio lands in the same per-unit
  dollars the financials' cogs_usd / units produces.
- Narrative knobs (modeled, not observed):
  * PP3000 / IP5000 hardware: the standard starts 2 pts of ASP below the actual
    COGS ratio and is re-set upward only ~0.6 pt/quarter while the financials'
    actual ratio climbs ~1.2 pt/quarter, so the UNFAVORABLE variance widens
    ~1 pt of standard per quarter (~+3% in 2024-Q1 -> ~+11% in 2026-Q2).
  * PP3500 hardware: standard set at 0.535 of ASP vs an actual of 0.52 —
    FAVORABLE every quarter (design-to-cost landed below standard).
  * SP6000 / SP6500 hardware: standard = actual (0.55) — on standard.
  * Consumables, service, subscription: small, stable unfavorable gaps.
- No clocks: literal quarters; as_of 2026-08-31.
"""
import argparse, csv, json, random

BANNER = "_Demo sample data - not for clinical use._"

QUARTERS = ["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4",
            "2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4",
            "2026-Q1", "2026-Q2"]
LINES = ["IP5000", "PP3000", "PP3500", "SP6000", "SP6500", "cloud-suite"]
TYPES = {  # revenue types carried per line (mirrors internal-financials TYPE_SHARE keys)
    "PP3500": ["hardware", "consumables", "service"],
    "PP3000": ["hardware", "consumables", "service"],
    "IP5000": ["hardware", "consumables", "service"],
    "SP6000": ["hardware", "consumables", "service"],
    "SP6500": ["hardware", "consumables", "service"],
    "cloud-suite": ["subscription"],
}
# Unit prices — identical constants to internal-financials/gen.py (ASP_HW / ASP).
ASP_HW = {"PP3500": 8000, "PP3000": 6000, "IP5000": 5500, "SP6000": 4200, "SP6500": 5200}
ASP = {"consumables": 27, "service": 2500, "subscription": 4800}

LEGACY = {"PP3000", "IP5000"}
LEGACY_STD_BASE, LEGACY_STD_SLOPE = 0.60, 0.006   # actual = 0.62 + 0.012/qtr in financials
STD_RATIO = {"PP3500": 0.535, "SP6000": 0.55, "SP6500": 0.55}
STD_RATIO_TYPE = {"consumables": 0.415, "service": 0.592, "subscription": 0.217}
# material / labor / overhead split of the standard, per revenue type
SPLIT = {"hardware": (0.60, 0.15, 0.25), "consumables": (0.70, 0.10, 0.20),
         "service": (0.10, 0.70, 0.20), "subscription": (0.05, 0.40, 0.55)}


def std_unit_cost(line, rtype, qi):
    if rtype == "hardware":
        ratio = (LEGACY_STD_BASE + LEGACY_STD_SLOPE * qi) if line in LEGACY else STD_RATIO[line]
        return ASP_HW[line] * ratio
    return ASP[rtype] * STD_RATIO_TYPE[rtype]


def make_rows(rng):
    rows = []
    for qi, period in enumerate(QUARTERS):
        std_version = f"STD-{period[:4]}.{1 if period.endswith(('Q1', 'Q2')) else 2}"
        for line in LINES:
            for rtype in TYPES[line]:
                unit = std_unit_cost(line, rtype, qi) * (1 + rng.uniform(-0.003, 0.003))
                m, l, o = SPLIT[rtype]
                material = round(unit * m, 2)
                labor = round(unit * l, 2)
                overhead = round(unit - material - labor, 2)
                rows.append({
                    "period": period, "product_line": line, "revenue_type": rtype,
                    "std_version": std_version,
                    "std_unit_cost_usd": round(unit, 2),
                    "material_usd": material, "labor_usd": labor, "overhead_usd": overhead,
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
