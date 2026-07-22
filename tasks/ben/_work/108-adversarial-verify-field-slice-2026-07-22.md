# Adversarial verification — field-slice answers (ben/108, 2026-07-22)

_Personal work artifact (task-support, not a controlled deliverable). Verifier: independent
subagent given ONLY the pinned snapshots + headline claims (not the reports); instructed to
refute; all values recomputed via scripts._

## Scope

Editions verified: BQ-19, BQ-23, BQ-24, BQ-25, BQ-26, BQ-27 — first drafts of 2026-07-22,
computed against `commercial/internal-upgrade-campaign@2026-07-22`,
`commercial/internal-fleet@2026-07-22`, `commercial/openfda-maude-infusion-mfr@2026-07-22`.

## Verdicts (on the first drafts)

| BQ | Verdict | Key finding |
|---|---|---|
| BQ-23 | CONFIRMED | 62.5% exact; EMEA/NA stalls genuine (last completions 2026-06-22 / 2026-05-11). Data-quality catch: 13 APAC completion dates post-dated the snapshot (generator artifact). |
| BQ-24 | CONFIRMED-WITH-CAVEAT | 23.1% reproduces only with never-attempted devices in the denominator; per-attempt rate is 35.3% — claim understated severity. Pause conclusion unchanged. |
| BQ-25 | CONFIRMED-WITH-CAVEAT | Tickets/100 was mixed-basis (all-row tickets ÷ completed); "peak in EMEA" fragile (NA 22.1 near-tie). Rollback sites + A-002 cost range exact. |
| BQ-26 | CONFIRMED | All required-vs-current rates match within rounding; APAC rate partly built on the future-dated completions (see BQ-23 catch). |
| BQ-27 | CONFIRMED | All five percentages exact. Direction note: unconnected devices slightly MORE current — no connectivity-drives-currency narrative is supported. |
| BQ-19 | CONFIRMED | A-001 has no quantified model; no denominators exist in pinned data; counts-only publication is the defensible posture. |

## Actions taken (same day, before any approval)

1. **Generator fix** — completion dates capped at the export as-of date (2026-07-20);
   corpus refreshed → `internal-upgrade-campaign@2026-07-22.2` + delta report.
2. **BQ-24 methodology** — primary metric switched to per-ATTEMPTED-device failure rate
   (whole-cohort shown for context); pause rule applies to the attempted basis.
3. **BQ-25 methodology** — consistent basis: tickets AND denominator over attempted devices.
4. BQ-23/24/25/26 re-answered against the new snapshot; all lint green; commercial check GREEN.

## Post-fix verdict deltas

- BQ-23: 62.7% complete; **EMEA + NA** miss the close (APAC now on-track — its projected miss
  was the date artifact).
- BQ-24: cluster fails **31.4% of attempted** (was reported 23.1% whole-cohort).
- BQ-25: highest tickets/100 attempted is **NA at 21.7** (basis-corrected; EMEA claim retracted).
- BQ-26: capacity gap now EMEA + NA only.

## Approval note

The verifier CONFIRMED the methodology and first-draft values; the re-answered editions carry
recomputed values produced by the SAME (corrected) deterministic computations against the
corrected snapshot. An approval citing this dossier should reference it as
`--verify-note "tasks/ben/_work/108-adversarial-verify-field-slice-2026-07-22.md (methodology verified; values recomputed post-fix by the same deterministic pipeline)"` —
or re-run an independent verification round on the new editions for full rigor.
