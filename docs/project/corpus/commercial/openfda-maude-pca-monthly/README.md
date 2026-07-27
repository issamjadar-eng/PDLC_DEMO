# Corpus dataset — `commercial/openfda-maude-pca-monthly`

**Real openFDA data** (public domain). MAUDE adverse-event counts per received-date for
**patient-controlled analgesia (PCA) pumps**, 2023-01 → present, via openFDA's
date-count aggregation API (`count: date_received` — daily buckets, aggregated to
months by the analysis tier). First snapshot: 915 daily buckets, 13,359 events
(2023-01-01 → 2026-06-30).

**Consumed by**: BQ-20 (franchise-killer signal watch — the PCA-class-wide external
baseline against which the internal over-delivery / PCA-by-proxy signals are read).

## Scope and search-string rationale

```
device.device_report_product_code:MEA AND date_received:[20230101 TO 20301231]
```

- **Product code `MEA`** = "Pump, Infusion, PCA" (21 CFR 880.5725, Class II) — the FDA
  product code specific to patient-controlled analgesia pumps, and PP3500's own code
  class. Probed alternatives before committing: a `device.generic_name:"patient
  controlled analgesia"` phrase search returns only 41 events total (free-text
  generic names are inconsistently populated), and those 41 events map predominantly
  to `MEA` anyway (32/41; the rest scatter across LKK/BSZ/FIH/FRN/LDR/MEB/MFA). The
  product code is the reliable scoping; `MEA` has 32,392 MAUDE events all-time,
  13,359 in the 2023-01+ window at first acquisition.
- **Not `FRN`** (general-purpose infusion pump) — that class-wide view is the sibling
  `openfda-maude-infusion-monthly`; this dataset isolates the PCA segment.
- **Date window open-ended** (`TO 20301231`) so refreshes extend forward without a
  config edit.
- **No `limit` param**: openFDA date-field count queries reject `limit` — same as the
  sibling monthly dataset (omit `count_limit`).

## Epistemic constraints

- **Counts, never rates.** MAUDE carries no denominator (installed base / therapy
  volume). Any rate use requires an installed-base assumption per the A-001 pattern
  (`openfda-maude-infusion-mfr/assumptions/A-001.yml`); none is declared here — this
  dataset supports trend/shape claims only.
- **Reporting lag tail.** Events are bucketed by `date_received`; recent months are
  systematically incomplete, so apparent declines in the last ~3–6 months are
  reporting lag, not signal. Analyses must truncate or flag the tail.
- Reporting propensity shifts (recalls, publicity, e-reporting adoption) move counts
  independently of true event rates.

## Conventions

- Managed by the `corpus` skill (`corpus.py`). Snapshots under `snapshots/` are immutable —
  never hand-edit; re-acquire instead. `dataset.yml` is the config; `latest` points at the
  newest valid snapshot. Assumptions in `assumptions/A-NNN.yml`, waivers in `waivers/W-NNN.yml`.
- `max_age_days: 30` — matches the sibling MAUDE count datasets' cadence.
- Usage rights: public domain (openFDA — https://open.fda.gov/license/).

## Changelog

- 2026-07-27: Scaffolded; first snapshot (915 daily buckets, 13,359 events) — task 108.
