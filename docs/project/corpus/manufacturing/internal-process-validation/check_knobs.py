#!/usr/bin/env python3
"""Assert seam for internal-process-validation — proves the planted narrative knobs
landed (runs on every acquire AND validate)."""
import csv, sys

rows = list(csv.DictReader(open(sys.argv[1], newline="")))
fails = []

# knob 1: PP3500 rev C test fixture — PQ in-progress at every site it appears at; IQ/OQ validated
revc = [r for r in rows if "rev C" in r["asset_or_process"] and r["product_line"] == "PP3500"
        and r["asset_or_process"].startswith("final functional test fixture")]
pq = [r for r in revc if r["type"] == "PQ"]
if not pq or any(r["status"] != "in-progress" for r in pq):
    fails.append(f"knob1: rev C fixture PQ statuses {[r['status'] for r in pq]} (expected all in-progress)")
if any(r["status"] != "validated" for r in revc if r["type"] in ("IQ", "OQ")):
    fails.append("knob1: rev C fixture IQ/OQ not all validated")

# knob 2: overdue calibrations cluster at Westfield (>= 6) while Eastbrook has <= 2
def overdue_cal(site):
    return sum(1 for r in rows if r["type"] == "calibration" and r["site"] == site and r["status"] == "overdue")

w, e = overdue_cal("Westfield"), overdue_cal("Eastbrook")
if w < 6 or e > 2:
    fails.append(f"knob2: overdue calibrations Westfield={w} Eastbrook={e} (expected >= 6 vs <= 2)")

# integrity: a completed record whose completion is on/after its due date is never 'overdue'
bad = [r["record_id"] for r in rows if r["status"] == "overdue" and r["completed_date"]
       and r["completed_date"] >= r["due_date"]]
if bad:
    fails.append(f"integrity: completed-after-due records marked overdue {bad[:5]}")

if fails:
    print("\n".join(fails)); sys.exit(1)
print(f"knobs OK ({len(rows)} rows; rev C PQ in-progress x{len(pq)}; overdue cal Westfield {w} / Eastbrook {e})")
