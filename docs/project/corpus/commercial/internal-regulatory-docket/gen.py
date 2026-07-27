#!/usr/bin/env python3
"""Demo generator — regulatory docket: MDR + field-action log (2025-01..2026-07).
Seeded, deterministic (seed 42, no clocks; data through 2026-07-25).
Stand-in for the regulatory-affairs tracking system export.

Deterministic knobs (see README):
  - 30 MDRs, of which EXACTLY 2 filed late (filed_date > regulatory_deadline)
    and 1 currently open near its deadline (over-delivery, opened 2026-06-29,
    deadline 2026-07-29 vs data-through 2026-07-25).
  - 1 open FSCA: drug-library correction opened 2026-05, region rollout status
    carried in the description.
  - 2 closed corrections (2025), 0 removals.
"""
import argparse, csv, datetime as dt, json, random

BANNER = "_Demo sample data - not for clinical use._"
DATA_THROUGH = dt.date(2026, 7, 25)   # fixed horizon — no clocks
REGIONS = ["NA", "NA", "NA", "EMEA", "EMEA", "APAC"]   # weighted draw
CATEGORIES = [("occlusion-alarm", 8), ("battery", 5), ("dose-programming", 6),
              ("software", 4), ("mechanical", 4), ("over-delivery", 2), ("other", 1)]
DESC = {
    "occlusion-alarm": "Occlusion alarm failure-to-annunciate reported during PCA therapy",
    "battery": "Unexpected battery depletion / shutdown during infusion",
    "dose-programming": "Dose programming discrepancy identified at pump review",
    "software": "Software anomaly observed on pump UI during therapy",
    "mechanical": "Mechanical fault (door latch / keypad) reported from field",
    "over-delivery": "Suspected over-delivery event during PCA therapy",
    "other": "Miscellaneous reportable field event",
}

def make_mdrs(rng):
    rows = []
    for _ in range(30):
        opened = dt.date(2025, 1, 5) + dt.timedelta(days=rng.randrange(0, 540))
        cat = rng.choices([c for c, _ in CATEGORIES], weights=[w for _, w in CATEGORIES])[0]
        deadline = opened + dt.timedelta(days=30)
        filed = deadline - dt.timedelta(days=rng.randrange(3, 13))
        status = "closed" if opened < dt.date(2026, 1, 1) else "filed"
        rows.append({"type": "mdr", "opened_date": opened, "regulatory_deadline": deadline,
                     "filed_date": filed, "status": status, "category": cat,
                     "region": rng.choice(REGIONS), "description": DESC[cat]})
    rows.sort(key=lambda r: r["opened_date"])
    # knob: exactly 2 late filings (filed_date > regulatory_deadline)
    for idx, late_by in ((6, 4), (17, 9)):
        rows[idx]["filed_date"] = rows[idx]["regulatory_deadline"] + dt.timedelta(days=late_by)
    # knob: 1 currently-open MDR near deadline — the over-delivery beat (BQ-20/BQ-21)
    rows[-1].update({"opened_date": dt.date(2026, 6, 29),
                     "regulatory_deadline": dt.date(2026, 7, 29),
                     "filed_date": None, "status": "open", "category": "over-delivery",
                     "region": "NA",
                     "description": DESC["over-delivery"] + "; investigation ongoing, MDR in preparation"})
    rows.sort(key=lambda r: r["opened_date"])
    # assign ids per year, in date order
    counters = {}
    for r in rows:
        y = r["opened_date"].year
        counters[y] = counters.get(y, 0) + 1
        r["record_id"] = f"MDR-{y}-{counters[y]:04d}"
    return rows

def make_field_actions():
    return [
        {"record_id": "CORR-2025-001", "type": "correction",
         "opened_date": dt.date(2025, 3, 10), "regulatory_deadline": dt.date(2025, 3, 24),
         "filed_date": dt.date(2025, 3, 18), "status": "closed", "category": "labeling-correction",
         "region": "NA", "description": "IFU clarification on bolus lockout labeling; closed 2025-06"},
        {"record_id": "CORR-2025-002", "type": "correction",
         "opened_date": dt.date(2025, 9, 2), "regulatory_deadline": dt.date(2025, 9, 16),
         "filed_date": dt.date(2025, 9, 11), "status": "closed", "category": "software-patch",
         "region": "EMEA", "description": "Firmware 3.2.1 display-timeout patch; closed 2025-12"},
        # knob: the one OPEN FSCA — drug-library correction, opened 2026-05, rollout in flight
        {"record_id": "FSCA-2026-001", "type": "fsca",
         "opened_date": dt.date(2026, 5, 12), "regulatory_deadline": dt.date(2026, 5, 26),
         "filed_date": dt.date(2026, 5, 20), "status": "open", "category": "drug-library-correction",
         "region": "ALL", "description": ("Field correction: PCA drug library v3.4.1 hard-limit update. "
                                          "Rollout status: NA complete 2026-06, EMEA in progress (~60% sites), "
                                          "APAC pending")},
    ]

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("--seed", type=int, default=42); g.add_argument("--out", required=True)
    n = sub.add_parser("normalize"); n.add_argument("raw"); n.add_argument("out")
    a = p.parse_args()
    if a.cmd == "gen":
        rng = random.Random(a.seed)
        rows = make_mdrs(rng) + make_field_actions()
        rows.sort(key=lambda r: (r["opened_date"], r["record_id"]))
        out = []
        for r in rows:
            out.append({
                "record_id": r["record_id"], "type": r["type"],
                "opened_date": r["opened_date"].isoformat(),
                "regulatory_deadline": r["regulatory_deadline"].isoformat(),
                "filed_date": r["filed_date"].isoformat() if r["filed_date"] else "",
                "status": r["status"], "category": r["category"],
                "region": r["region"], "description": r["description"],
            })
        json.dump({"banner": BANNER, "generator": "gen.py", "seed": a.seed,
                   "data_through": DATA_THROUGH.isoformat(), "rows": out},
                  open(f"{a.out}/export.json", "w"), indent=1)
    else:
        rows = json.load(open(f"{a.raw}/export.json"))["rows"]
        w = csv.DictWriter(open(f"{a.out}/records.csv", "w", newline=""), fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

main()
