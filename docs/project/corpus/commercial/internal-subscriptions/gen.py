#!/usr/bin/env python3
"""Demo generator — Cloud Suite subscription register (one row per subscribed site).
Seeded, deterministic (NO clocks — all dates literal). Stand-in for the subscription
billing / entitlement export.
Narrative knobs: pumps_connected equals the shared fleet model's connected count per
site; ARR ~$450/connected pump/yr; small sites disproportionately expensive to serve
(fixed per-site cost floor); subscribed sites average ~6% hardware discount (the
cannibalization signal); 3 churned sites; a few connected sites deliberately have NO
subscription row (attach gap for BQ-29)."""
import argparse, csv, json, random

BANNER = "_Demo sample data - not for clinical use._"
REGIONS = {"NA": 24, "EMEA": 16, "APAC": 8}   # sites per region

def make_fleet(rng):
    """Deterministic demo fleet. Identical function is embedded in every internal
    generator so device serials/sites align across datasets (seed 42)."""
    sites, fleet, serial = [], [], 1
    for region, n in REGIONS.items():
        for i in range(n):
            sites.append({"site_id": f"S-{region}-{i+1:02d}", "region": region,
                          "beds": rng.choice([80, 120, 200, 350, 500])})
    for s in sites:
        n_dev = max(4, s["beds"] // 12)
        attach_p = {"NA": 0.60, "EMEA": 0.40, "APAC": 0.30}[s["region"]]
        for _ in range(n_dev):
            model = "PP3500" if rng.random() < 0.78 else "PP3000"
            hw = rng.choice(["A", "A", "B"]) if model == "PP3500" else "-"
            if model == "PP3500":
                fw = rng.choices(["3.4.0", "3.2.0", "3.1.2"], weights=[45, 35, 20])[0]
            else:
                fw = rng.choice(["2.9.1", "2.9.3"])
            fleet.append({
                "device_serial": f"PE-{serial:05d}", "model": model,
                "site_id": s["site_id"], "region": s["region"], "hw_rev": hw,
                "firmware_version": fw,
                "connected": "yes" if (model == "PP3500" and rng.random() < attach_p) else "no",
            })
            serial += 1
    return sites, fleet

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("--seed", type=int, default=42); g.add_argument("--out", required=True)
    n = sub.add_parser("normalize"); n.add_argument("raw"); n.add_argument("out")
    a = p.parse_args()
    if a.cmd == "gen":
        rng = random.Random(a.seed)
        _, fleet = make_fleet(rng)          # burn identical rng stream so fleet aligns
        rng2 = random.Random(a.seed + 20)   # dataset-local randomness
        connected = {}
        for d in fleet:
            if d["connected"] == "yes":
                connected[d["site_id"]] = connected.get(d["site_id"], 0) + 1
        eligible = sorted(connected)        # only sites with >=1 connected device
        # attach gap (BQ-29): connected sites with NO subscription row — deliberate
        gap_sites = rng2.sample([s for s in eligible if connected[s] >= 3], 4)
        subscribed = [s for s in eligible if s not in gap_sites]
        churned = rng2.sample(subscribed, 3)
        rows = []
        for s in subscribed:
            pumps = connected[s]
            ym = (2024 + (0 if rng2.random() < 0.45 else 1), rng2.randint(1, 12)) \
                if s not in churned else (2024, rng2.randint(1, 6))
            start_date = f"{ym[0]}-{ym[1]:02d}-{rng2.randint(1, 28):02d}"
            rate = rng2.randint(430, 470)           # ~$450 per connected pump per year
            arr = rate * pumps
            # cost-to-serve: fixed per-site floor + per-pump — small sites are
            # disproportionately expensive (floor dominates; breakeven ~9-10 connected
            # pumps, so sub-scale sites run negative margin while large sites clear it)
            cost = 2800 + 150 * pumps + rng2.randint(-400, 800)
            discount = max(0.0, round(rng2.gauss(6.0, 2.5), 1))  # avg ~6% hw discount
            rows.append({
                "site_id": s, "start_date": start_date, "pumps_connected": str(pumps),
                "arr_usd": str(arr), "cost_to_serve_usd": str(cost),
                "status": "churned" if s in churned else "active",
                "hardware_discount_pct": str(discount),
            })
        json.dump({"banner": BANNER, "generator": "gen.py", "seed": a.seed,
                   "attach_gap_sites": gap_sites, "rows": rows},
                  open(f"{a.out}/export.json", "w"), indent=1)
    else:
        rows = json.load(open(f"{a.raw}/export.json"))["rows"]
        w = csv.DictWriter(open(f"{a.out}/records.csv", "w", newline=""), fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

main()
