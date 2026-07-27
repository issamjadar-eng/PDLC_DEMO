#!/usr/bin/env python3
"""Shared-model identity check (corpus asserts.command seam).

Verifies every generator embedding this dataset's canonical shared blocks
(make_fleet + REGIONS) carries a byte-identical copy — the honor-system
convention the code review flagged (F-FL-1). Non-zero exit fails
acquire/validate for internal-fleet, surfacing silent cross-dataset drift.
"""
import re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMMERCIAL = HERE.parent


def extract(path, name):
    text = Path(path).read_text()
    m = re.search(rf"^def {name}\(.*?(?=^\S)", text, re.M | re.S)
    return m.group(0).rstrip() if m else None


def extract_regions(path):
    m = re.search(r"^REGIONS = .*$", Path(path).read_text(), re.M)
    return m.group(0) if m else None


def main():
    canonical_gen = HERE / "gen.py"
    canon_fleet = extract(canonical_gen, "make_fleet")
    canon_regions = extract_regions(canonical_gen)
    if not canon_fleet or not canon_regions:
        print("cannot extract canonical make_fleet/REGIONS from internal-fleet/gen.py")
        return 1
    failures = []
    checked = 0
    for gen in sorted(COMMERCIAL.glob("*/gen.py")):
        if gen == canonical_gen:
            continue
        body = gen.read_text()
        if "def make_fleet(" not in body:
            continue
        checked += 1
        ds = gen.parent.name
        if extract(gen, "make_fleet") != canon_fleet:
            failures.append(f"{ds}: make_fleet drifted from canonical")
        if extract_regions(gen) != canon_regions:
            failures.append(f"{ds}: REGIONS drifted from canonical")
    for f in failures:
        print(f"SHARED-MODEL DRIFT: {f}")
    print(f"shared-model check: {checked} embedding generator(s), {len(failures)} drift(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
