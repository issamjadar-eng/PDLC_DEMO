#!/usr/bin/env python3
"""Example computation script — the contract a project's computations must follow.

Invoked by the commercial engine as (cwd = the commercial root):
    python3 computations.py BQ-NN --corpus-root <abs> --out <abs-edition-dir>

Contract:
  1. Read {out}/pins.json — compute ONLY from those dataset@snapshot paths.
  2. Write {out}/data.json — {"bq", "edition_generated_at", "series": [...], "verdicts": [...]}
     Every series: id, label, unit, evidence_class (measured|derived|assumed|unavailable),
     provenance ({"dataset","snapshot"} or {"assumption": "A-NNN"}), points.
  3. Write {out}/report.md — every numeric claim carries a marker on its line:
     [src: dataset@snapshot] | [assume: A-NNN] | [derived: series-or-verdict-id] | [config: path]
  4. Deterministic: same pins -> byte-identical outputs. No network, no clock-dependent logic
     beyond what the engine passes in.
  5. If the underlying data is fabricated/internal, stamp the project's demo banner at the top.
"""

import argparse
import csv
import json
from pathlib import Path


def load_pin_csv(corpus_root: Path, pins: dict, dataset: str):
    snap = pins[dataset]
    path = corpus_root / dataset / "snapshots" / snap / "normalized" / "records.csv"
    with open(path, newline="") as f:
        return list(csv.DictReader(f)), snap


def main():
    p = argparse.ArgumentParser()
    p.add_argument("bq")
    p.add_argument("--corpus-root", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    out, corpus_root = Path(a.out), Path(a.corpus_root)
    pins = json.loads((out / "pins.json").read_text())

    rows, snap = load_pin_csv(corpus_root, pins, "<domain>/<dataset>")
    total = len(rows)
    src = f"<domain>/<dataset>@{snap}"

    data = {
        "bq": a.bq,
        "series": [{
            "id": "total-rows", "label": "Total records", "unit": "count",
            "evidence_class": "measured",
            "provenance": {"dataset": "<domain>/<dataset>", "snapshot": snap},
            "points": [{"label": "total", "value": total}],
        }],
        "verdicts": [{"id": "v-main", "headline": f"{total} records in scope",
                      "evidence_class": "measured"}],
    }
    (out / "data.json").write_text(json.dumps(data, indent=1))
    (out / "report.md").write_text(
        f"# {a.bq} — example answer\n\n"
        f"**Verdict**: {total} records in scope [derived: v-main] [src: {src}]\n"
    )


if __name__ == "__main__":
    main()
