#!/usr/bin/env python3
"""Assert seam for internal-production-lots — proves the planted narrative knobs
landed in the normalized CSV (runs on every acquire AND validate)."""
import csv, sys

rows = list(csv.DictReader(open(sys.argv[1], newline="")))
fails = []


def fpy(sub):
    s = sum(int(r["units_started"]) for r in sub)
    return sum(int(r["units_passed_first_time"]) for r in sub) / s if s else None


# knob 1: PP3500 rev C test-station FPY in 2026-Q2 is below 92%, rev B same station same
# quarter is above 94% (the dip is rev-specific, not station-wide)
q2 = [r for r in rows if r["product_line"] == "PP3500" and r["line_station"] == "test"
      and "2026-04" <= r["start_date"][:7] <= "2026-06"]
c, b = fpy([r for r in q2 if r["hw_rev"] == "C"]), fpy([r for r in q2 if r["hw_rev"] == "B"])
if c is None or c >= 0.92:
    fails.append(f"knob1: PP3500 rev C test FPY 2026-Q2 = {c} (expected < 0.92)")
if b is None or b <= 0.94:
    fails.append(f"knob1: PP3500 rev B test FPY 2026-Q2 = {b} (expected > 0.94)")

# knob 2: Westfield release lead days rise: 2026 mean exceeds 2025 mean by >= 3 days;
# Eastbrook stays within 1 day
def mean_lead(site, year):
    v = [int(r["release_lead_days"]) for r in rows
         if r["site"] == site and r["release_lead_days"] and r["start_date"].startswith(year)]
    return sum(v) / len(v) if v else None

w25, w26 = mean_lead("Westfield", "2025"), mean_lead("Westfield", "2026")
e25, e26 = mean_lead("Eastbrook", "2025"), mean_lead("Eastbrook", "2026")
if None in (w25, w26) or w26 - w25 < 3:
    fails.append(f"knob2: Westfield lead 2025={w25} 2026={w26} (expected +3d or more)")
if None in (e25, e26) or abs(e26 - e25) > 1:
    fails.append(f"knob2: Eastbrook lead 2025={e25} 2026={e26} (expected flat within 1d)")

# knob 3: between 3 and 15 lots have dhr_complete=false, and every one of them is unreleased
blocked = [r for r in rows if r["dhr_complete"] == "false"]
if not 3 <= len(blocked) <= 15:
    fails.append(f"knob3: {len(blocked)} dhr_complete=false lots (expected 3..15)")
if any(r["release_date"] for r in blocked):
    fails.append("knob3: a dhr_complete=false lot carries a release_date")

if fails:
    print("\n".join(fails)); sys.exit(1)
print(f"knobs OK ({len(rows)} rows; rev C test FPY Q2 {c:.3f} vs rev B {b:.3f}; "
      f"Westfield lead {w25:.1f}->{w26:.1f}; {len(blocked)} DHR-blocked lots)")
