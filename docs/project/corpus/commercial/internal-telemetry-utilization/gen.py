#!/usr/bin/env python3
"""Demo generator — monthly infusion-utilization telemetry for Cloud Suite CONNECTED
devices only, months 2026-02..2026-07. Seeded, deterministic (NO clocks — literal
months). Stand-in for the Cloud Suite telemetry warehouse export.
Narrative knob: ~6 specific sites whose devices run <50% of expected hours (the
sold-but-underused early warning for BQ-11); all other connected devices 70-110%."""
import argparse, csv, hashlib, json, random

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

def site_segment(site_id):
    """Segment keyed on a stable hash of site_id — identical function embedded in the
    other internal generators so segments align across datasets without consuming rng."""
    h = int(hashlib.md5(site_id.encode()).hexdigest(), 16) % 10
    return "academic" if h < 3 else "community" if h < 7 else "idn" if h < 9 else "home-infusion"

MONTHS = ["2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07"]
EXPECTED = {"academic": 480, "idn": 450, "community": 400, "home-infusion": 280}  # hrs/device/month

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("--seed", type=int, default=42); g.add_argument("--out", required=True)
    n = sub.add_parser("normalize"); n.add_argument("raw"); n.add_argument("out")
    a = p.parse_args()
    if a.cmd == "gen":
        rng = random.Random(a.seed)
        _, fleet = make_fleet(rng)          # burn identical rng stream so fleet aligns
        rng2 = random.Random(a.seed + 30)   # dataset-local randomness
        devices = [d for d in fleet if d["connected"] == "yes"]
        counts = {}
        for d in devices:
            counts[d["site_id"]] = counts.get(d["site_id"], 0) + 1
        # underused-site knob (BQ-11): 6 sites with >=5 connected devices run <50%
        underused = rng2.sample(sorted(s for s, c in counts.items() if c >= 5), 6)
        rows = []
        for d in devices:
            exp = EXPECTED[site_segment(d["site_id"])]
            for month in MONTHS:
                factor = rng2.uniform(0.25, 0.48) if d["site_id"] in underused \
                    else rng2.uniform(0.70, 1.10)
                rows.append({
                    "device_serial": d["device_serial"], "month": month,
                    "site_id": d["site_id"], "region": d["region"],
                    "infusion_hours": str(int(exp * factor)), "expected_hours": str(exp),
                })
        json.dump({"banner": BANNER, "generator": "gen.py", "seed": a.seed,
                   "underused_sites": underused, "rows": rows},
                  open(f"{a.out}/export.json", "w"), indent=1)
    else:
        rows = json.load(open(f"{a.raw}/export.json"))["rows"]
        w = csv.DictWriter(open(f"{a.out}/records.csv", "w", newline=""), fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

main()
