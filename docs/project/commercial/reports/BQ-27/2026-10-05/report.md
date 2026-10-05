# BQ-27 — Fleet currency: how far behind is the installed base

_Demo sample data — not for clinical use._

**Verdict**: 56.7% of the PP3500 fleet is ≥1 firmware version behind (21.9% two behind); connected devices are current at 42.3% vs 44.2% for unconnected [derived: v-main] [src: commercial/internal-fleet@2026-10-05]

## PP3500 version posture

- Fleet size 686; ≥1 behind 389; two behind 150 [src: commercial/internal-fleet@2026-10-05]
- Connected vs unconnected on current version: 42.3% vs 44.2% [derived: currency-by-connectivity] [src: commercial/internal-fleet@2026-10-05]

## % behind by region

| Region | % ≥1 version behind |
|---|---|
| APAC [src: commercial/internal-fleet@2026-10-05] | 52.1% |
| EMEA [src: commercial/internal-fleet@2026-10-05] | 59.7% |
| NA [src: commercial/internal-fleet@2026-10-05] | 56.9% |

- Legacy PP3000 units still in service: 198 (all on 2.9.x line) [src: commercial/internal-fleet@2026-10-05] — phase-out drift is a board-tier question (see catalog overflow).

## Method & provenance

- Historical view: currency-over-time needs MULTIPLE fleet snapshots — the dataset's 7-day cadence will accumulate them; until then the history series is marked no-data rather than faked [derived: currency-history].
- Version posture measured from [src: commercial/internal-fleet@2026-10-05]; behind-by mapping [config: commercial.yml].
- An outdated drug-error-reduction library is a patient-safety exposure, not just an ops
  metric — currency lag feeds the risk conversation.
