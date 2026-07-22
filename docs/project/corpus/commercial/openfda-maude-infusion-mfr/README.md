# Corpus dataset — `commercial/openfda-maude-infusion-mfr`

Real MAUDE adverse-event **counts by manufacturer** for product code **FRN** (reports
received 2024-07→present), via openFDA's count API (`/device/event.json?count=`).
Row-level MAUDE is 80k+ events for this window — counts are the tractable, honest shape.

**Consumed by**: BQ-19 (cross-manufacturer comparison — the flagship honesty showcase).

**Hard epistemic constraints** (why A-001 exists):
1. **No denominator** — MAUDE counts cannot become rates without an installed-base
   estimate per manufacturer. That estimate is assumption **A-001** in `assumptions/`;
   any rate chart MUST cite it.
2. **Reporting propensity differs across manufacturers** — an unmodeled bias even with
   a denominator. Comparative claims must carry this caveat.
3. **Manufacturer-name variants** (e.g. two Fresenius spellings, CareFusion SD vs
   CareFusion 303) — the analysis tier must entity-normalize before aggregating.

## Conventions

- Managed by the `corpus` skill (`corpus.py`). Snapshots under `snapshots/` are immutable —
  never hand-edit; re-acquire instead. `dataset.yml` is the config; `latest` points at the
  newest valid snapshot. Assumptions in `assumptions/A-NNN.yml`, waivers in `waivers/W-NNN.yml`.
- Refresh cadence: monthly (`max_age_days: 30`).

## Changelog

- 2026-07-22: Scaffolded; A-001 denominator assumption created; first snapshot acquired
  (99 manufacturer count buckets; 1 empty-term bucket skipped by normalizer) — task 108.
