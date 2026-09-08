#!/usr/bin/env python3
"""Narrative-knob check (corpus asserts.command seam) for finance/internal-ar-inventory.

Proves the seeded working-capital story on the normalized CSV: (1) Northgate's
over-90 AR share in the last period is at least double its first-period share;
(2) PP3000 inventory days rise by >= 30 days across the window while PP3500 stays
within +/-10 days. Aggregation uses the implied-daily-flow convention consumers
use (share = sum(over90)/sum(AR); days = sum(inv)/sum(inv/days)). Non-zero exit
fails acquire/validate.

Usage: python3 check_knobs.py <normalized_dir>/records.csv   (cwd = dataset dir)
"""
import csv, sys

NORTHGATE = "Northgate Purchasing Group"


def days(rows):
    inv = sum(int(r["inventory_usd"]) for r in rows)
    daily = sum(int(r["inventory_usd"]) / float(r["inventory_days"]) for r in rows if float(r["inventory_days"]))
    return inv / daily if daily else 0.0


def main():
    with open(sys.argv[1], newline="") as f:
        rows = list(csv.DictReader(f))
    periods = sorted({r["period"] for r in rows})
    first, last = periods[0], periods[-1]
    fails = []

    def o90(period):
        sub = [r for r in rows if r["period"] == period and r["gpo"] == NORTHGATE]
        ar = sum(int(r["ar_balance_usd"]) for r in sub)
        return sum(int(r["ar_over_90_usd"]) for r in sub) / ar if ar else 0.0
    s0, s1 = o90(first), o90(last)
    if s1 < 2 * s0:
        fails.append(f"Northgate over-90 share {s0:.3f} -> {s1:.3f} did not double")

    def line_days(period, line):
        return days([r for r in rows if r["period"] == period and r["product_line"] == line])
    d0, d1 = line_days(first, "PP3000"), line_days(last, "PP3000")
    if d1 - d0 < 30:
        fails.append(f"PP3000 inventory days {d0:.1f} -> {d1:.1f} rose < 30")
    e0, e1 = line_days(first, "PP3500"), line_days(last, "PP3500")
    if abs(e1 - e0) > 10:
        fails.append(f"PP3500 inventory days {e0:.1f} -> {e1:.1f} moved > 10")
    if fails:
        print("check_knobs FAILED:\n  " + "\n  ".join(fails))
        return 1
    print(f"check_knobs OK: Northgate over-90 {s0:.1%} -> {s1:.1%}; PP3000 days {d0:.0f} -> {d1:.0f}; "
          f"PP3500 days {e0:.0f} -> {e1:.0f} ({len(rows)} rows, {first}..{last})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
