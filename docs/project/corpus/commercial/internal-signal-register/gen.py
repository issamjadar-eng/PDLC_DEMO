#!/usr/bin/env python3
"""Demo generator — field-signal disposition register (~40 signals, 2025-01..2026-06).
Seeded, deterministic (seed 42, no clocks; data through 2026-07-25).
Stand-in for the post-market signal-management spreadsheet/register export.

Deterministic knobs (see README):
  - ~40% of signals "died in a spreadsheet": ended no-action (10) or still open
    >90 days at the 2026-07-25 horizon (6) -> 16/40 for BQ-22.
  - 2 over-delivery-related signals DID become upgrade-items (UPG- refs) — the
    counter-beat tying to internal-regulatory-docket / internal-complaints.
"""
import argparse, csv, datetime as dt, json, random

BANNER = "_Demo sample data - not for clinical use._"
DATA_THROUGH = dt.date(2026, 7, 25)   # fixed horizon — no clocks
SOURCES = ["complaint-trend", "maude-screen", "alarm-analytics", "near-miss", "field-service"]
CATEGORIES = ["occlusion-alarm", "battery", "connectivity", "dose-programming",
              "alarm-fatigue", "keypad-wear", "drug-library", "screen-display", "tubing-set"]

# (disposition, count, ref-prefix, opened-window)
W_ALL = (dt.date(2025, 1, 5), dt.date(2026, 6, 25))
W_STALE = (dt.date(2025, 3, 1), dt.date(2026, 3, 31))     # open > 90 days at horizon
W_FRESH = (dt.date(2026, 5, 1), dt.date(2026, 6, 20))     # open, recent
BUCKETS = [
    ("no-action", 10, None, W_ALL),
    ("open", 6, None, W_STALE),
    ("open", 2, None, W_FRESH),
    ("design-input", 5, "DI", W_ALL),
    ("requirement-change", 4, "REQ", W_ALL),
    ("upgrade-item", 4, "UPG", W_ALL),
    ("monitoring", 7, None, W_ALL),
]

def rand_date(rng, lo, hi):
    return lo + dt.timedelta(days=rng.randrange(0, (hi - lo).days + 1))

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("--seed", type=int, default=42); g.add_argument("--out", required=True)
    n = sub.add_parser("normalize"); n.add_argument("raw"); n.add_argument("out")
    a = p.parse_args()
    if a.cmd == "gen":
        rng = random.Random(a.seed)
        rows, refno = [], 40
        for dispo, count, prefix, (lo, hi) in BUCKETS:
            for _ in range(count):
                opened = rand_date(rng, lo, hi)
                ref = ""
                if prefix:
                    refno += 1
                    ref = f"{prefix}-{refno:04d}"
                closed = ""
                if dispo != "open":
                    closed = min(opened + dt.timedelta(days=rng.randrange(30, 181)),
                                 dt.date(2026, 7, 20)).isoformat()
                rows.append({"opened_date": opened,
                             "source": rng.choice(SOURCES), "category": rng.choice(CATEGORIES),
                             "disposition": dispo, "disposition_ref": ref, "closed_date": closed})
        # knob: 2 over-delivery signals that DID become upgrade-items
        rows.append({"opened_date": dt.date(2025, 11, 10), "source": "maude-screen",
                     "category": "over-delivery", "disposition": "upgrade-item",
                     "disposition_ref": "UPG-0051", "closed_date": "2026-02-06"})
        rows.append({"opened_date": dt.date(2026, 2, 17), "source": "complaint-trend",
                     "category": "over-delivery", "disposition": "upgrade-item",
                     "disposition_ref": "UPG-0052", "closed_date": "2026-05-29"})
        rows.sort(key=lambda r: r["opened_date"])
        counters, out = {}, []
        for r in rows:
            y = r["opened_date"].year
            counters[y] = counters.get(y, 0) + 1
            out.append({"signal_id": f"SIG-{y}-{counters[y]:03d}",
                        "opened_date": r["opened_date"].isoformat(), "source": r["source"],
                        "category": r["category"], "disposition": r["disposition"],
                        "disposition_ref": r["disposition_ref"], "closed_date": r["closed_date"]})
        json.dump({"banner": BANNER, "generator": "gen.py", "seed": a.seed,
                   "data_through": DATA_THROUGH.isoformat(), "rows": out},
                  open(f"{a.out}/export.json", "w"), indent=1)
    else:
        rows = json.load(open(f"{a.raw}/export.json"))["rows"]
        w = csv.DictWriter(open(f"{a.out}/records.csv", "w", newline=""), fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

main()
