# Corpus dataset — `commercial/openfda-maude-infusion-monthly`

Real MAUDE adverse-event **counts per received date** for product code **FRN**
(2023-01→present) via openFDA's date-count API (`count=date_received`; daily buckets,
`term` = YYYYMMDD). The class-wide **historical trend** input for BQ-19; the analysis
tier aggregates days → months.

**Constraints**: counts only — rates need A-001 (see the manufacturer-count sibling
dataset); MAUDE reporting lag makes the most recent 1–2 months look artificially low —
trend analyses must exclude or caveat the tail.

## Conventions

- Managed by the `corpus` skill (`corpus.py`). Snapshots under `snapshots/` are immutable —
  never hand-edit; re-acquire instead. `dataset.yml` is the config; `latest` points at the
  newest valid snapshot.
- Refresh cadence: monthly (`max_age_days: 30`).

## Changelog

- 2026-07-22: Dataset scaffolded; first snapshot acquired (task 108, historical-views round).
