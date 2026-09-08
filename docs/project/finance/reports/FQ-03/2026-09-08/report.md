# FQ-03 — Cost of poor quality: warranty spend, per-unit cost, complaint linkage

_Demo sample data — not for clinical use._

**Verdict**: YTD 2026 (2026-01..2026-08) warranty spend $340K vs $276K same months 2025 (+23.1%); per installed unit: PP3000 $801 (+101.6% YoY), PP3500 $149 (-16.2% YoY; rev A $94 (-48.9%), rev B $242 (+47.0%)); over-indexing revisions: PP3500 rev B 48% of claims vs 37% of fleet (1.31×); not normalizable (registry carries no revision split): SP6000 rev A 88% of claims (21 of 24), PP3000 rev B 64% of claims (67 of 105), IP5000 rev B 52% of claims (21 of 40); 37% of claims link to a complaint (99 of 267); per-unit unavailable for IP5000, SP6000, SP6500 (no fleet denominator) [derived: v-main] [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] [src: commercial/internal-complaints@2026-09-08] [config: finance.yml]

## Warranty spend — YTD vs prior year

_Window: claims dated 2026-01..2026-08 (as-of 2026-08 in the pin) vs 2025-01..2025-08 [src: finance/internal-warranty-claims@2026-09-08]; tolerances [config: finance.yml]._

| Window | Claims | Spend $K | Repair $K | Replace $K | Goodwill $K |
|---|---|---|---|---|---|
| YTD 2026 (2026-01..2026-08) [src: finance/internal-warranty-claims@2026-09-08] | 267 | 340 | 65 | 264 | 11 |
| same months 2025 [src: finance/internal-warranty-claims@2026-09-08] | 216 | 276 | 59 | 213 | 4 |

## Warranty cost per installed unit — by line and hardware revision

_Denominator = devices in the pinned fleet registry per model / hw_rev [src: commercial/internal-fleet@2026-09-08] (point-in-time, applied to both windows); numerator = claim cost in the window [src: finance/internal-warranty-claims@2026-09-08]._

| Line / rev | Installed units | Claims YTD | Spend YTD $K | $ per unit YTD | $ per unit prior | YoY |
|---|---|---|---|---|---|---|
| PP3000 [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] | 198 | 105 | 159 | 801 | 397 | +101.6% ⚠️ |
| PP3500 [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] | 686 | 77 | 102 | 149 | 177 | -16.2% |
| PP3500 rev A [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] | 434 | 40 | 41 | 94 | 185 | -48.9% |
| PP3500 rev B [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] | 252 | 37 | 61 | 242 | 164 | +47.0% |

## Per-unit gaps: not computable (stated, not approximated)

- No fleet registry rows for IP5000, SP6000, SP6500 [src: commercial/internal-fleet@2026-09-08] — their spend is reported in dollars only [derived: per-unit-unavailable].
- The registry records PP3000 hw_rev as unknown [src: commercial/internal-fleet@2026-09-08], while the claims carry a revision [src: finance/internal-warranty-claims@2026-09-08] — per-unit by revision is unavailable for those lines; claim share by revision is reported instead.

## Revision concentration — claim share vs installed share

_Every revision of a line with more than one revision in the window's claims [src: finance/internal-warranty-claims@2026-09-08]. Over-index = claim share ÷ installed share from the registry [src: commercial/internal-fleet@2026-09-08], flagged beyond 1.25×; where the registry carries no revision split the raw claim share is shown and flagged beyond 50% as not normalizable [config: finance.yml]._

| Line / rev | Claims | Line claims | Claim share | Installed share | Over-index |
|---|---|---|---|---|---|
| IP5000 rev A [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] | 19 | 40 | 48% | n/a | n/a |
| IP5000 rev B [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] | 21 | 40 | 52% ⚠️ not normalizable | n/a | n/a |
| PP3000 rev A [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] | 38 | 105 | 36% | n/a | n/a |
| PP3000 rev B [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] | 67 | 105 | 64% ⚠️ not normalizable | n/a | n/a |
| PP3500 rev A [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] | 40 | 77 | 52% | 63% | 0.82× |
| PP3500 rev B [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] | 37 | 77 | 48% | 37% | 1.31× ⚠️ |
| SP6000 rev A [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] | 21 | 24 | 88% ⚠️ not normalizable | n/a | n/a |
| SP6000 rev B [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] | 3 | 24 | 12% | n/a | n/a |

Failure categories for PP3500 rev B (YTD 2026 (2026-01..2026-08)) [src: finance/internal-warranty-claims@2026-09-08]: pump-mechanism 9, occlusion-sensor 6, power-supply 6, screen-display 5, battery 4, keypad 4, other 2, connectivity 1 [derived: revision-failure-categories].

Failure categories for SP6000 rev A (YTD 2026 (2026-01..2026-08)) [src: finance/internal-warranty-claims@2026-09-08]: screen-display 6, power-supply 5, battery 4, occlusion-sensor 2, other 2, pump-mechanism 2 [derived: revision-failure-categories].

Failure categories for PP3000 rev B (YTD 2026 (2026-01..2026-08)) [src: finance/internal-warranty-claims@2026-09-08]: pump-mechanism 22, power-supply 19, occlusion-sensor 7, connectivity 6, battery 5, keypad 3, other 3, screen-display 2 [derived: revision-failure-categories].

Failure categories for IP5000 rev B (YTD 2026 (2026-01..2026-08)) [src: finance/internal-warranty-claims@2026-09-08]: occlusion-sensor 6, power-supply 4, pump-mechanism 3, screen-display 3, connectivity 2, other 2, battery 1 [derived: revision-failure-categories].

## Complaint linkage

| Line | Claims linked to a complaint | Line claims | Linked share |
|---|---|---|---|
| IP5000 [src: finance/internal-warranty-claims@2026-09-08] | 10 | 40 | 25% |
| PP3000 [src: finance/internal-warranty-claims@2026-09-08] | 54 | 105 | 51% |
| PP3500 [src: finance/internal-warranty-claims@2026-09-08] | 21 | 77 | 27% |
| SP6000 [src: finance/internal-warranty-claims@2026-09-08] | 6 | 24 | 25% |
| SP6500 [src: finance/internal-warranty-claims@2026-09-08] | 8 | 21 | 38% |

For the lines the fleet registry carries, complaints logged in the same window [src: commercial/internal-complaints@2026-09-08] vs warranty claims linked to a complaint [src: finance/internal-warranty-claims@2026-09-08]: PP3000 54 linked claims vs 56 complaints; PP3500 21 linked claims vs 137 complaints [derived: complaints-context].

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-03.1 | Warranty cost per installed PP3500 unit does not rise year over year beyond tolerance [derived: cost-per-unit-yoy] [config: finance.yml] | PP3500 per-unit cost YTD <= prior-year same months + 10% | PP3500 $149/unit YTD 2026 (2026-01..2026-08) vs $177 same months 2025 (-16.2%) | met (unvalidated) | quality-plan reliability target carried forward; no approved KPI threshold on file [VERIFY] |
| E-03.2 | No hardware revision over-indexes on warranty claims relative to its installed share [derived: revision-concentration] [derived: cost-per-unit-by-rev] [config: finance.yml] | claim share / installed share <= 1.25x per revision (lines with a revision split in the fleet registry) | 1 revision(s) over 1.25× on 1 normalizable line(s): PP3500 rev B 48% of claims vs 37% of fleet (1.31×); not normalizable (no registry revision split): SP6000 rev A 88% of claims (21 of 24), PP3000 rev B 64% of claims (67 of 105), IP5000 rev B 52% of claims (21 of 40) | not-met (unvalidated) | design-signal over-index guardrail; not a risk-file threshold [VERIFY] |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (medium)** — PP3500 hardware rev B over-indexes on warranty: 48% of the line's YTD 2026 (2026-01..2026-08) claims (37 of 77) vs 37% of the installed fleet (1.31×); $242 per installed unit YTD 2026 (2026-01..2026-08); top failure category pump-mechanism (9 claims) [derived: revision-concentration] [derived: revision-failure-categories] [derived: cost-per-unit-by-rev] [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] [config: finance.yml]
  - _Action_: Open a design-signal review on the revision; decide field action vs revision-specific service bulletin with quality and regulatory [derived: revision-concentration] [derived: revision-failure-categories] [derived: cost-per-unit-by-rev] [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] [config: finance.yml]
- **I2 (medium)** — SP6000 hardware rev A carries 88% of the line's YTD 2026 (2026-01..2026-08) claims (21 of 24); top failure category screen-display (6 claims) — the registry records no SP6000 revision, so this cannot be normalized to the installed mix [derived: revision-concentration] [derived: revision-failure-categories] [derived: per-unit-unavailable] [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] [config: finance.yml]
  - _Action_: Add the hardware revision to the fleet registry export for the line, then re-test the over-index; meanwhile treat the cluster as a design-signal review candidate [derived: revision-concentration] [derived: revision-failure-categories] [derived: per-unit-unavailable] [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] [config: finance.yml]
- **I3 (medium)** — PP3000 hardware rev B carries 64% of the line's YTD 2026 (2026-01..2026-08) claims (67 of 105); top failure category pump-mechanism (22 claims) — the registry records no PP3000 revision, so this cannot be normalized to the installed mix [derived: revision-concentration] [derived: revision-failure-categories] [derived: per-unit-unavailable] [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] [config: finance.yml]
  - _Action_: Add the hardware revision to the fleet registry export for the line, then re-test the over-index; meanwhile treat the cluster as a design-signal review candidate [derived: revision-concentration] [derived: revision-failure-categories] [derived: per-unit-unavailable] [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] [config: finance.yml]
- **I4 (medium)** — IP5000 hardware rev B carries 52% of the line's YTD 2026 (2026-01..2026-08) claims (21 of 40); top failure category occlusion-sensor (6 claims) — the registry records no IP5000 revision, so this cannot be normalized to the installed mix [derived: revision-concentration] [derived: revision-failure-categories] [derived: per-unit-unavailable] [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] [config: finance.yml]
  - _Action_: Add the hardware revision to the fleet registry export for the line, then re-test the over-index; meanwhile treat the cluster as a design-signal review candidate [derived: revision-concentration] [derived: revision-failure-categories] [derived: per-unit-unavailable] [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] [config: finance.yml]
- **I5 (medium)** — PP3000 warranty cost per installed unit $801 YTD 2026 (2026-01..2026-08) vs $397 same months 2025 (+101.6%) — beyond the 10% tolerance [derived: cost-per-unit-yoy] [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] [config: finance.yml]
  - _Action_: Re-test the warranty reserve for the line against the observed per-unit trend (FQ-04) and review end-of-life timing [derived: cost-per-unit-yoy] [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-fleet@2026-09-08] [config: finance.yml]

### Risks (potential — mitigation identified)

- **R1 (medium)** — Per-unit figures use the fleet registry as a point-in-time denominator for both windows — a fleet that grew over the year makes prior-year per-unit costs look lower than they were [src: commercial/internal-fleet@2026-09-08] [derived: cost-per-unit-yoy]
  - _Mitigation_: Pin a fleet snapshot per window once recurring fleet snapshots exist; until then read per-unit YoY as directional [src: commercial/internal-fleet@2026-09-08] [derived: cost-per-unit-yoy]
- **R2 (medium)** — Replacements ($264K) outspend repairs ($65K) YTD 2026 (2026-01..2026-08) — cost per claim is being driven by the replace share [derived: disposition-mix] [src: finance/internal-warranty-claims@2026-09-08]
  - _Mitigation_: Depot-repair capacity review for the lines driving replacements [derived: disposition-mix] [src: finance/internal-warranty-claims@2026-09-08]

### Watch

- **W1 (medium)** — 63% of warranty claims (168 of 267) have no linked complaint — warranty activity the complaint-handling system is not trending [derived: complaint-linkage] [src: finance/internal-warranty-claims@2026-09-08] [src: commercial/internal-complaints@2026-09-08]
- **W2 (medium)** — Per-unit gaps: IP5000, SP6000, SP6500 have no fleet registry rows; PP3000 revision recorded as unknown in the registry [derived: per-unit-unavailable] [src: commercial/internal-fleet@2026-09-08]

## Method & provenance

- Claim cost summed from [src: finance/internal-warranty-claims@2026-09-08]; windows matched month-for-month; per-unit denominators from [src: commercial/internal-fleet@2026-09-08] only; complaint counts from [src: commercial/internal-complaints@2026-09-08]; thresholds [config: finance.yml].
- Historical view: monthly warranty cost by line over the full claims history is charted [derived: monthly-cost-trend] [src: finance/internal-warranty-claims@2026-09-08]; disposition mix [derived: disposition-mix].
- Verdict and expectation actuals carry the per-unit, concentration, and linkage figures so a rollup cannot drop them [derived: v-main].
