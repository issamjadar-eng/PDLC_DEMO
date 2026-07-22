# BQ-18 — Complaint categories vs risk-file thresholds

_Demo sample data — not for clinical use._

**Verdict**: CAPA-review trigger: occlusion-alarm at 3.39 per 100 devices vs threshold 3.0; connectivity at 2.26 per 100 devices vs threshold 2.0 (trailing 90d ending 2026-07-17) [derived: v-main] [src: commercial/internal-complaints@2026-07-22] [config: commercial.yml]

## Trailing window, rate-normalized (stated denominator: 884 fleet devices [src: commercial/internal-fleet@2026-07-22])

| Category | Complaints | Rate per 100 devices | Threshold | Prior window | Evidence |
|---|---|---|---|---|---|
| occlusion-alarm | 30 | 3.39 ⚠️ | 3.0 | 13 | [src: commercial/internal-complaints@2026-07-22] [config: commercial.yml] |
| connectivity | 20 | 2.26 ⚠️ | 2.0 | 9 | [src: commercial/internal-complaints@2026-07-22] [config: commercial.yml] |
| battery | 16 | 1.81 | 2.0 | 21 | [src: commercial/internal-complaints@2026-07-22] [config: commercial.yml] |
| screen-display | 13 | 1.47 | 2.0 | 10 | [src: commercial/internal-complaints@2026-07-22] [config: commercial.yml] |
| mechanical | 11 | 1.24 | 2.0 | 9 | [src: commercial/internal-complaints@2026-07-22] [config: commercial.yml] |
| other | 7 | 0.79 | 2.0 | 3 | [src: commercial/internal-complaints@2026-07-22] [config: commercial.yml] |
| dose-programming | 4 | 0.45 | 2.0 | 6 | [src: commercial/internal-complaints@2026-07-22] [config: commercial.yml] |

## Method & provenance

- Complaint counts measured from [src: commercial/internal-complaints@2026-07-22]; denominator is the installed-base registry
  [src: commercial/internal-fleet@2026-07-22] — the ONLY sanctioned internal denominator (per the corpus conventions).
- Thresholds are demo stand-ins for risk-file complaint-rate commitments
  [config: commercial.yml]; a breach obligates a CAPA review, not automatically a CAPA.
