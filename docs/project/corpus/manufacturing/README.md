# Corpus domain — `manufacturing/`

_Demo sample data — not for clinical use._

Datasets consumed by the **Manufacturing** business domain (`docs/project/manufacturing/`,
answered by the commercial-skill engine with `--domain manufacturing`). Every dataset here
is `internal: true` — demo-fabricated by a seeded generator (`gen.py`, seed 42, no clocks,
data through 2026-08-31) that stands in for the plant / QMS system exports a real
deployment would acquire (MES lot records, the NCR/CAPA register, the approved-supplier
list + incoming-inspection log, the validation / calibration register).

## Structure

| Dataset | Purpose |
|---------|---------|
| `internal-production-lots/` | One row per production lot 2025-01..2026-08 — product line, hw rev, station, site, units started / passed first time / scrapped / reworked, DHR completeness, release lead days. Consumed by MQ-01 (yield), MQ-08 (release blockers); roadmap MQ-02/04/07/09/10 |
| `internal-ncr-capa/` | Nonconformance + CAPA register 2025-01..2026-08 — type, dates, status, source, severity, root-cause category, effectiveness verification, NCR→CAPA link. Consumed by MQ-03 |
| `internal-suppliers/` | Approved-supplier register × monthly incoming-inspection results 2025-01..2026-08 — component family, single-source flag, approval status, audit dates, lots received / rejected, on-time %, scorecard. Consumed by MQ-05; roadmap MQ-06 |
| `internal-process-validation/` | Validation + calibration status register — IQ/OQ/PQ, calibration, preventive maintenance per asset or process, site, status, due / completed dates, owner function. Consumed by MQ-08; roadmap MQ-10 |

## Expected Content

- `<dataset>/dataset.yml` — acquisition/normalize/schema config (hand-edited)
- `<dataset>/gen.py` — the seeded demo generator (`gen` + `normalize` subcommands)
- `<dataset>/snapshots/YYYY-MM-DD/` — engine-written, **immutable**
- `<dataset>/assumptions/A-NNN.yml`, `waivers/W-NNN.yml` — via `assume` / `waive`
- `<dataset>/latest` — pointer file (engine-written)

## Conventions

- Managed by the `corpus` skill: `python3 .claude/skills/corpus/scripts/corpus.py
  {init|acquire|refresh|validate|diff|check|list|assume|waive} manufacturing/<dataset>`.
  **Never hand-edit anything under `snapshots/`** — re-acquire instead.
- Generators are deterministic (seed 42), carry **no clocks** (literal as-of dates —
  `data_through: 2026-08-31` is recorded as `as_of` in each snapshot's provenance), and
  stamp the demo banner into the raw export.
- Shared vocabulary: `product_line` ∈ {IP5000, PP3000, PP3500, SP6000, SP6500} (the
  portfolio in `project.yml`); `hw_rev` reuses `commercial/internal-fleet`'s letters for
  the fielded revisions (PP3500 A/B); rev C is the 2026 revision in production, defined
  here in `internal-production-lots/gen.py` and not yet present in the fleet registry;
  `-` where a line has no tracked hw rev; `site` ∈ {Eastbrook, Westfield} (two fictional plants).
- Closed vocabularies are pinned by `asserts.enums` in each `dataset.yml`; narrative
  knobs are documented in each dataset README (honest list — modeled, not observed).
- Freshness: each dataset declares `max_age_days`; `check` fails on stale data without
  an unexpired waiver.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-09-08 | BX / AI Assistant | task 118: reference-audit fixes — MQ-10 added to production-lots consumers; hw rev C attributed to this corpus (not present in `commercial/internal-fleet`) |
| 2026-09-08 | BX / AI Assistant | task 118: domain folder created with four internal demo datasets (production lots, NCR/CAPA, suppliers, process validation) for the Manufacturing business domain. |
