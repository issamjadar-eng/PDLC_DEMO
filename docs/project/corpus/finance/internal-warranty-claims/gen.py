#!/usr/bin/env python3
"""Demo generator — per-claim warranty log, 2025-01 .. 2026-08. Seeded, deterministic.
Stand-in for the service-management / warranty-claims system export.

Coherence anchors:
- Product lines are the five device lines of commercial/internal-financials; regions
  NA / EMEA / APAC with the fleet's 55/30/15 weighting. Replacement costs sit near
  each line's hardware unit cost (financials ASP x COGS ratio).
- hw_rev is the SERVICE system's view: PP3000 claims carry rev A / B even though the
  fleet registry (commercial/internal-fleet) records PP3000 hw_rev as "-" — consumers
  must treat per-unit-by-rev for PP3000 as a stated denominator gap.
- Narrative knobs (modeled, not observed):
  * PP3000 claims cluster on hw rev B (~70% of PP3000 claims) with pump-mechanism /
    power-supply failures dominating that cluster.
  * Warranty cost per unit rises for legacy lines: PP3000 monthly claim volume
    roughly doubles across the window and its replace share climbs; IP5000 drifts up.
  * PP3500 steady; SP lines low and flat.
- No clocks: literal dates; as_of 2026-08-31.
"""
import argparse, csv, json, random

BANNER = "_Demo sample data - not for clinical use._"

MONTHS = [f"{y}-{m:02d}" for y in (2025, 2026) for m in range(1, 13)][:20]  # 2025-01..2026-08
DAYS_IN = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
REGIONS = [("NA", 0.55), ("EMEA", 0.30), ("APAC", 0.15)]
# monthly claim rate: (start, end) interpolated linearly across the 20 months
RATE = {"PP3500": (9.0, 9.5), "PP3000": (7.0, 15.0), "IP5000": (3.5, 5.5),
        "SP6000": (3.0, 3.0), "SP6500": (2.5, 2.5)}
HW_REV = {"PP3500": [("A", 0.63), ("B", 0.37)], "PP3000": [("A", 0.30), ("B", 0.70)],
          "IP5000": [("A", 0.50), ("B", 0.50)], "SP6000": [("A", 0.80), ("B", 0.20)],
          "SP6500": [("A", 1.00)]}
CATS = ["battery", "pump-mechanism", "occlusion-sensor", "screen-display", "connectivity",
        "power-supply", "keypad", "other"]
CAT_W = {"default": [22, 14, 16, 14, 10, 8, 8, 8],
         "PP3000-B": [8, 34, 8, 8, 4, 26, 6, 6],
         "PP3500": [24, 8, 18, 14, 18, 6, 6, 6]}
REPLACE_COST = {"PP3500": (3200, 4800), "PP3000": (2600, 3800), "IP5000": (2300, 3400),
                "SP6000": (1800, 2600), "SP6500": (2100, 2900)}


def lerp(a, b, t):
    return a + (b - a) * t


def weighted(rng, pairs):
    return rng.choices([p[0] for p in pairs], weights=[p[1] for p in pairs])[0]


def make_rows(rng):
    rows = []
    for mi, month in enumerate(MONTHS):
        t = mi / (len(MONTHS) - 1)
        y, m = int(month[:4]), int(month[5:])
        for line, (r0, r1) in RATE.items():
            n = max(0, int(round(lerp(r0, r1, t) + rng.uniform(-1.5, 1.5))))
            for _ in range(n):
                region = weighted(rng, REGIONS)
                rev = weighted(rng, HW_REV[line])
                w = CAT_W["PP3000-B"] if (line, rev) == ("PP3000", "B") else CAT_W.get(line, CAT_W["default"])
                cat = rng.choices(CATS, weights=w)[0]
                replace_p = lerp(0.25, 0.40, t) if line in ("PP3000", "IP5000") else 0.22
                disp = rng.choices(["repair", "replace", "goodwill", "denied"],
                                   weights=[1 - replace_p - 0.20, replace_p, 0.10, 0.10])[0]
                if disp == "repair":
                    cost = rng.uniform(180, 850)
                elif disp == "replace":
                    cost = rng.uniform(*REPLACE_COST[line])
                elif disp == "goodwill":
                    cost = rng.uniform(100, 600)
                else:
                    cost = 0.0
                linked_p = 0.45 if (line, rev) == ("PP3000", "B") else 0.33
                rows.append({
                    "product_line": line, "region": region, "hw_rev": rev,
                    "claim_date": f"{y}-{m:02d}-{rng.randint(1, DAYS_IN[m]):02d}",
                    "failure_category": cat, "cost_usd": int(round(cost)),
                    "disposition": disp,
                    "linked_complaint": "yes" if rng.random() < linked_p else "no",
                })
    rows.sort(key=lambda r: (r["claim_date"], r["product_line"], r["region"], r["hw_rev"],
                             r["failure_category"], r["cost_usd"]))
    for i, r in enumerate(rows, 1):
        r["claim_id"] = f"WC-{i:05d}"
    cols = ["claim_id", "product_line", "region", "hw_rev", "claim_date", "failure_category",
            "cost_usd", "disposition", "linked_complaint"]
    return [{c: r[c] for c in cols} for r in rows]


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
