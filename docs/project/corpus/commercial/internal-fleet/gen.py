#!/usr/bin/env python3
"""Demo generator — internal fleet registry. Seeded, deterministic.
Stand-in for a Fleet Management / ERP installed-base export."""
import argparse, csv, json, random, sys

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
        _, fleet = make_fleet(rng)
        for d in fleet:
            d["last_seen"] = "2026-07-21" if d["connected"] == "yes" else "2026-06-30"
        json.dump({"banner": BANNER, "generator": "gen.py", "seed": a.seed, "rows": fleet},
                  open(f"{a.out}/export.json", "w"), indent=1)
    else:
        rows = json.load(open(f"{a.raw}/export.json"))["rows"]
        w = csv.DictWriter(open(f"{a.out}/records.csv", "w", newline=""), fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

main()
