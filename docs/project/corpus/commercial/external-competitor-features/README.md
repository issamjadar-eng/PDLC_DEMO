# Corpus dataset — `commercial/external-competitor-features`

Curated competitor feature / spec matrix (**real, compiled public + project-doc data**)
for the PCA / smart-pump competitive set: BD Alaris (incl. PCA Module), Baxter
(Spectrum IQ, Sigma Spectrum, Novum IQ), ICU Medical (Plum 360), Smiths Medical / ICU
Medical (CADD-Solis, CADD Legacy), B.Braun (Infusomat Space), plus PainEase PP3500 rows
from the project's own competitive-landscape docs. One row per (vendor, product,
attribute); every value carries a source (`source_ref` = project doc path or public
URL). **Attributes with no source are omitted, never guessed**; rows the curator could
not confirm against a fetched source are marked `verified: verify`.

**Curation model**: the hand-maintained matrix is `curated.csv` (next to `dataset.yml`).
Snapshots are engine-written copies — edit `curated.csv`, then `corpus.py acquire`;
never touch `snapshots/`.

**Consumed by**: BQ-10 (5-yr TCO vs Alaris/Spectrum IQ/Plum 360), BQ-13
(predictive-monitoring runway, with A-005), BQ-14 (line-by-line PCA feature parity),
BQ-15 (SOTA currency of headline differentiators).

**Assumptions**: A-003 (US smart-pump segment size, BQ-07), A-004 (competitor
pricing / 5-yr TCO inputs, BQ-10), A-005 (develop-to-clear lead time for
predictive-monitoring entrants, BQ-13).

## Coverage notes (2026-07-27 snapshot, 42 rows)

- **Filled from project docs** (source_type `project-doc`, all `verified: yes`):
  PP3500 full row set (accuracy 0.35%, battery 150 h, weight 0.75 kg, DERS,
  predictive_monitoring=no, connectivity roadmap rows); Alaris full row set incl.
  PCA Pause + EtCO2; Spectrum IQ accuracy/predictive; Sigma Spectrum DERS/battery;
  Plum 360 battery + predictive; CADD Legacy weight/battery/PCA.
- **Filled from public web** (`public-web`, `verified: yes`): CADD-Solis (PCA modes,
  PharmGuard, wireless, ±6% accuracy, 0.595 kg), Plum 360 (MedNet library, 802.11
  wireless), Novum IQ (Dose IQ, IQ Enterprise Connectivity), Infusomat Space (±5%
  accuracy, 3.5-13 h battery, 1200-drug library, 1.4 kg).
- **`verified: verify` (source named, not independently fetched)**: Spectrum IQ
  ders_drug_library + wireless_connectivity; Infusomat Space wireless_connectivity.
- **Deliberately absent (no confirmable source found — the gap is visible, not
  guessed)**: PP3500 `pca_pause_or_etco2` / `integrated_etco2` (not documented in
  project docs); CADD-Solis battery_hours (runs on replaceable 4x AA — no fixed
  hours spec); Plum 360 / Novum IQ flow accuracy (Spectrum IQ flow accuracy IS
  present — ±2.3% from the competitive-product-assessment; an earlier draft of this
  list wrongly named it absent, corrected 2026-07-27); ICU Medical Plum Duo
  (no rows — not yet curated); B.Braun Perfusor Space (no rows); Alaris
  remote_update_capability; all vendors `dose_personalization`.
- **Known source tension**: `strategic-market-ai-infusion.md` claims ±0.1% accuracy
  for B.Braun Space — contradicted by the vendor IFU-derived public spec (±5% per
  IEC 60601-2-24); the public value is used and the project-doc claim is not carried.
  Comp-assessment gives PP3500 ±0.5% volumetric; the SOTA-doc laboratory figure
  (±0.35%, matching BQ-15's differentiator config) is carried instead.

## Conventions

- Managed by the `corpus` skill (`corpus.py`). Snapshots under `snapshots/` are immutable —
  never hand-edit; re-acquire instead. `dataset.yml` is the config; `latest` points at the
  newest valid snapshot. Assumptions in `assumptions/A-NNN.yml`, waivers in `waivers/W-NNN.yml`.
- `usage_rights: public information, compiled — verify before external use`. Rows marked
  `verify` must be independently confirmed before any external-facing claim.
- Schema key: `[vendor, product, attribute]`. `max_age_days: 180`.

## Changelog

- 2026-07-27: First snapshot (42 rows, 9 products, 10 attribute kinds); A-003/A-004/A-005
  assumption records created — task ben/108.
- 2026-07-27: Dataset scaffolded by `corpus.py init`.
