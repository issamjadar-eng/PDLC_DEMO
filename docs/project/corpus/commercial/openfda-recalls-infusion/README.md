# Corpus dataset — `commercial/openfda-recalls-infusion`

Real FDA device-recall records for infusion-pump product code **FRN** posted 2021→present,
acquired from openFDA (`/device/recall.json`). **Real public data** (public domain).

**Consumed by**: BQ-09 (disruption-window win rate), BQ-19 (class safety context),
BQ-21 (exposure framing), competitor-recall response playbook (overflow catalog).

**Known limitation**: recalling-firm names vary across records (e.g. "ICU Medical, Inc."
vs "ICU Medical Inc") — the analysis tier must entity-normalize before per-firm counts.

## Conventions

- Managed by the `corpus` skill (`corpus.py`). Snapshots under `snapshots/` are immutable —
  never hand-edit; re-acquire instead. `dataset.yml` is the config; `latest` points at the
  newest valid snapshot. Assumptions in `assumptions/A-NNN.yml`, waivers in `waivers/W-NNN.yml`.
- Refresh cadence: monthly (`max_age_days: 30`) — recalls are event-driven signals.

## Changelog

- 2026-07-22: Scaffolded; first snapshot acquired (136 recalls, posted 2021→present) — task 108.
