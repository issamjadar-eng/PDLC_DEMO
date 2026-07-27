# Corpus dataset — `commercial/internal-kol-register`

_Demo sample data — not for clinical use._

KOL evidence register for the **F1-F9 commercial-roadmap feature lanes**
(`docs/project/strategies/commercial-strategy.md` D-COMM-1.4), distilled from the
project's KOL documents. One row per (feature x KOL x evidence item) actually
documented — a feature with **no** documented KOL evidence gets **no** rows; the gap
is the finding. `internal: true` — this is project-authored demo material (the
persona opinions are simulated; see integrity note below).

**Curation model**: hand-distilled register in `curated.csv` (next to `dataset.yml`);
snapshots are engine-written copies via `corpus.py acquire`.

**Consumed by**: BQ-16 (documented KOL evidence per roadmap feature; E-16.1 floor of
2 distinct voices), BQ-17 (roadmap bet kill / pull-forward).

## Evidence-base integrity (read before citing)

- **All 38 rows are `evidence_type: advisory-board`** from the simulated 8-member KOL
  persona panel of the ben/080 commercial-roadmap KOL review
  (`docs/_analysis/pca-device/commercial-roadmap-kol-review/kol-KOL-*.md`, dated
  2026-06-04). Those opinions are **simulated persona responses for the demo, not
  real collected feedback** — consistent with review finding F-1: all 8 KOL profiles
  under `docs/project/input-analysis/kol-feedback/` are "not yet contacted".
- **No interview, survey, or publication evidence rows exist for any feature.** The
  "+0.55 / +0.16" sentiment figures in `competitive-product-assessment.md` trace to a
  separate 28-expert market-research panel, not to the named roster KOLs (per F-1),
  so they are not attributable to any `kol_id` and are excluded from this register.
- The commercial-strategy "KOL anchor" column is a **specialty-to-feature mapping**,
  not evidence; it contributes no rows here.
- **Sentiment-flattening limitation** (red-team RT-16.1/RT-17.1): the 3-value
  sentiment vocabulary (`support | neutral | concern`) cannot carry the **direction
  or conditionality** of a position — per the mapping convention, a
  **conditional-support** verdict encodes as `concern` (e.g. Giuliano's F4
  "Conditional — will not endorse until…", Gorski's F7 "Conditional yes — sequencing
  is right", Kuitunen's F9 "too late and too thin — start EU evidence earlier").
  **Consumers must not read `concern` as opposition without checking the per-KOL
  source doc** — a concern row may be a conditional yes, or even a voice for
  *earlier/stronger* investment. Downstream answers (BQ-16/BQ-17) state this
  limitation; a stance (support/conditional/oppose) × timing
  (earlier/as-scheduled/later) split is the planned upgrade when real evidence is
  collected.

## Coverage (2026-07-27 snapshot, 38 rows)

| Feature | Voices | Sentiment mix |
|---|---|---|
| F1 Drug Library Manager | 5 | 2 support / 2 concern / 1 neutral |
| F2 Connectivity Adapter | 3 | 1 support / 1 concern / 1 neutral |
| F3 Fleet Mgmt + Telemetry | 3 | 1 support / 1 concern / 1 neutral |
| F4 Alerts Engine v1 | 6 | 6 concern |
| F5 Clinical Surveillance | 4 | 3 support / 1 neutral |
| F6 Predictive monitoring | 5 | 5 concern |
| F7 Ambulatory / home PCA | 5 | 5 concern |
| F8 Dose personalization | 6 | 6 concern |
| F9 International (EU MDR/Canada) | **1** | 1 concern |

**Gaps**: no feature has zero simulated-panel voices, but **F9 rides on a single
voice** (Kuitunen — fails the E-16.1 two-voice floor), and **every feature has zero
real (collected) KOL evidence** — the register will need full re-population once
actual KOL interviews happen (review finding F-1 resolution).

## Conventions

- Managed by the `corpus` skill (`corpus.py`). Snapshots under `snapshots/` are immutable —
  never hand-edit; re-acquire instead. `dataset.yml` is the config; `latest` points at the
  newest valid snapshot. Assumptions in `assumptions/A-NNN.yml`, waivers in `waivers/W-NNN.yml`.
- Sentiment vocabulary: `support | neutral | concern` (mapped from each persona doc's
  explicit per-feature statements and verdict). Evidence types:
  `interview | advisory-board | publication | survey`.
- Schema key: `[feature_id, kol_id, evidence_type, date]`. `max_age_days: 365`.
  `usage_rights: internal`.

## Changelog

- 2026-07-27: Added the sentiment-flattening limitation to the integrity section
  (red-team findings RT-16.1/RT-17.1, task ben/108): conditional-support voices encode
  as `concern`; consumers must check the source doc before reading concern as
  opposition.
- 2026-07-27: First snapshot (38 rows, 8 KOLs, 9 features; advisory-board evidence only)
  distilled from the ben/080 KOL persona panel — task ben/108.
- 2026-07-27: Dataset scaffolded by `corpus.py init`.
