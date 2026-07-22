# Corpus dataset — `commercial/openfda-510k-infusion`

Real 510(k) clearance records for infusion-pump product code **FRN** (decision dates
2021→present), acquired from openFDA (`/device/510k.json`). This is **real public data**
(public domain per the openFDA license) — the authoritative public signal for competitor
pipeline and roadmap questions.

**Consumed by** (business-question catalog, task-tracked): BQ-06 (R&D productivity /
clearance cycle time), BQ-12 (quarterly clearance sweep vs roadmap), BQ-13
(predictive-monitoring runway), BQ-14 (PCA feature parity via clearance summaries).

**Known limitation**: openFDA's 510(k) endpoint reflects FDA's published clearance
records; product-code FRN alone does not capture adjacent SaMD/monitoring clearances —
BQ-13 analyses should widen the search (additional product codes) before concluding
"no entrant activity."

## Conventions

- Managed by the `corpus` skill (`corpus.py`). Snapshots under `snapshots/` are immutable —
  never hand-edit; re-acquire instead. `dataset.yml` is the config; `latest` points at the
  newest valid snapshot. Assumptions in `assumptions/A-NNN.yml`, waivers in `waivers/W-NNN.yml`.
- Refresh cadence: quarterly (`max_age_days: 90`), aligned to the BQ-12 quarterly sweep.

## Changelog

- 2026-07-22: Dataset scaffolded by `corpus.py init`.
- 2026-07-22: First snapshot acquired (29 records, decisions 2021-11-09 → 2026-01-28) via
  `corpus.py acquire` (task 108).
