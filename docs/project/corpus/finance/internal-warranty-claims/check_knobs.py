#!/usr/bin/env python3
"""Narrative-knob check (corpus asserts.command seam) for finance/internal-warranty-claims.

Proves the two seeded knobs on the normalized CSV: (1) PP3000 claims cluster on
hw rev B; (2) legacy warranty cost is rising — PP3000 claim cost in the last six
months of the log exceeds the first six months by a clear margin. Non-zero exit
fails acquire/validate.

Usage: python3 check_knobs.py <normalized_dir>/records.csv   (cwd = dataset dir)
"""
import csv, sys

REV_B_MIN_SHARE = 0.60
RISE_MIN_RATIO = 1.30


def main():
    with open(sys.argv[1], newline="") as f:
        rows = list(csv.DictReader(f))
    pp3000 = [r for r in rows if r["product_line"] == "PP3000"]
    fails = []
    b = sum(1 for r in pp3000 if r["hw_rev"] == "B")
    share = b / len(pp3000) if pp3000 else 0.0
    if share < REV_B_MIN_SHARE:
        fails.append(f"PP3000 rev B share {share:.2f} < {REV_B_MIN_SHARE}")
    months = sorted({r["claim_date"][:7] for r in rows})
    first, last = set(months[:6]), set(months[-6:])
    c_first = sum(int(r["cost_usd"]) for r in pp3000 if r["claim_date"][:7] in first)
    c_last = sum(int(r["cost_usd"]) for r in pp3000 if r["claim_date"][:7] in last)
    if not c_first or c_last / c_first < RISE_MIN_RATIO:
        fails.append(f"PP3000 cost last-6m/first-6m = {c_last}/{c_first} < {RISE_MIN_RATIO}")
    if fails:
        print("check_knobs FAILED:\n  " + "\n  ".join(fails))
        return 1
    print(f"check_knobs OK: PP3000 rev B share {share:.2f}; PP3000 cost last/first 6m "
          f"{c_last / c_first:.2f}x ({len(rows)} claims, {months[0]}..{months[-1]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
