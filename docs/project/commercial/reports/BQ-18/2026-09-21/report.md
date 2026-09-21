# BQ-18 — Complaint categories vs risk-file thresholds

_Demo sample data — not for clinical use._

**Verdict**: CAPA-review trigger: occlusion-alarm at 3.17 per 100 devices vs threshold 3.0; connectivity at 2.26 per 100 devices vs threshold 2.0 (trailing 90d ending 2026-07-17) [derived: v-main] [src: commercial/internal-complaints@2026-09-21] [config: commercial.yml]

## Trailing window, rate-normalized (stated denominator: 884 fleet devices [src: commercial/internal-fleet@2026-09-21])

| Category | Complaints | Rate per 100 devices | Threshold | Prior window |
|---|---|---|---|---|
| occlusion-alarm [src: commercial/internal-complaints@2026-09-21] [config: commercial.yml] | 28 | 3.17 ⚠️ | 3.0 | 15 |
| connectivity [src: commercial/internal-complaints@2026-09-21] [config: commercial.yml] | 20 | 2.26 ⚠️ | 2.0 | 9 |
| battery [src: commercial/internal-complaints@2026-09-21] [config: commercial.yml] | 16 | 1.81 | 2.0 | 21 |
| screen-display [src: commercial/internal-complaints@2026-09-21] [config: commercial.yml] | 13 | 1.47 | 2.0 | 10 |
| mechanical [src: commercial/internal-complaints@2026-09-21] [config: commercial.yml] | 11 | 1.24 | 2.0 | 9 |
| other [src: commercial/internal-complaints@2026-09-21] [config: commercial.yml] | 7 | 0.79 | 2.0 | 3 |
| dose-programming [src: commercial/internal-complaints@2026-09-21] [config: commercial.yml] | 4 | 0.45 | 2.0 | 6 |
| pca-by-proxy-suspected [src: commercial/internal-complaints@2026-09-21] [config: commercial.yml] | 1 | 0.11 | 2.0 | 0 |
| over-delivery [src: commercial/internal-complaints@2026-09-21] [config: commercial.yml] | 1 | 0.11 | 2.0 | 1 |

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-18.1 | Complaint rates stay within the per-category thresholds [derived: rate-by-category] [config: commercial.yml] | <= 2.0 per 100 devices per 90d (occlusion-alarm <= 3.0) | occlusion-alarm 3.17 vs 3.0; connectivity 2.26 vs 2.0 | not-met (unvalidated) | demo stand-ins [VERIFY] — must be re-derived from the risk file's acceptability criteria before real use |
| E-18.2 | Complaint volume is not trending upward window-over-window [derived: window-trend] [config: commercial.yml] | current 90d window <= 130% of prior window | current 101 vs prior 74 | not-met (unvalidated) | generic trend heuristic; no documented commitment |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — occlusion-alarm at 3.17 per 100 devices exceeds its threshold of 3.0 in the trailing 90d window [derived: rate-by-category] [src: commercial/internal-complaints@2026-09-21] [config: commercial.yml]
  - _Action_: Open a CAPA review; stratify by site, firmware version, and device age; check correlation with the upgrade campaign's rollback sites [derived: rate-by-category] [src: commercial/internal-complaints@2026-09-21] [config: commercial.yml]
- **I2 (high)** — connectivity at 2.26 per 100 devices exceeds its threshold of 2.0 in the trailing 90d window [derived: rate-by-category] [src: commercial/internal-complaints@2026-09-21] [config: commercial.yml]
  - _Action_: Open a CAPA review; stratify by site, firmware version, and device age; check correlation with the upgrade campaign's rollback sites [derived: rate-by-category] [src: commercial/internal-complaints@2026-09-21] [config: commercial.yml]

### Risks (potential — mitigation identified)

- **R1 (medium)** — Total complaint volume is rising window-over-window (101 vs 74) [derived: window-trend]
  - _Mitigation_: Trend-analyze monthly by category; if the rise persists a second window, escalate to management review [derived: window-trend]
- **R2 (medium)** — The category thresholds are demo stand-ins, not the risk file's documented acceptability criteria — a breach verdict is only as good as its threshold [config: commercial.yml]
  - _Mitigation_: Re-derive thresholds from the risk file and mark the expectation validated [config: commercial.yml]

## Method & provenance

- Complaint counts measured from [src: commercial/internal-complaints@2026-09-21]; denominator is the installed-base registry
  [src: commercial/internal-fleet@2026-09-21] — the ONLY sanctioned internal denominator (per the corpus conventions).
- Thresholds are demo stand-ins for risk-file complaint-rate commitments
  [config: commercial.yml]; a breach obligates a CAPA review, not automatically a CAPA.
