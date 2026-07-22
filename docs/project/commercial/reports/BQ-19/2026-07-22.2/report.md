# BQ-19 — Adverse-event profile vs competitors (the denominator question)

**Verdict**: MAUDE event COUNTS are comparable with caveats; RATE comparison is BLOCKED — the installed-base denominator (A-001) is not yet quantified [derived: v-main] [assume: A-001]

## Event counts by manufacturer (entity-normalized)

_Real openFDA MAUDE data; reports received 2024-07 onward; infusion-pump product code only [src: commercial/openfda-maude-infusion-mfr@2026-07-22] [config: entity-aliases.yml]._

| Manufacturer (canonical) | MAUDE events | Evidence |
|---|---|---|
| BD (CareFusion) | 61,390 | [src: commercial/openfda-maude-infusion-mfr@2026-07-22] |
| Baxter | 9,548 | [src: commercial/openfda-maude-infusion-mfr@2026-07-22] |
| Smiths Medical | 9,229 | [src: commercial/openfda-maude-infusion-mfr@2026-07-22] |
| ICU Medical | 8,824 | [src: commercial/openfda-maude-infusion-mfr@2026-07-22] |
| Fresenius Kabi | 6,499 | [src: commercial/openfda-maude-infusion-mfr@2026-07-22] |
| Medtronic | 5,474 | [src: commercial/openfda-maude-infusion-mfr@2026-07-22] |

## Why there is no rate chart here

- MAUDE counts have NO denominator: FDA's own disclaimer warns event counts cannot
  establish incidence rates. A per-manufacturer rate requires an installed-base estimate —
  that estimate is [assume: A-001], whose model is not yet quantified. Until A-001 carries
  a reviewed model, this analysis publishes counts only — the rate chart is mechanically
  blocked, not merely discouraged.
- Reporting propensity differs across manufacturers (an unmodeled bias even with a
  denominator) [assume: A-001].
- Manufacturer identity is normalized via the versioned alias map
  [config: entity-aliases.yml]; unmatched names stay raw and visible.

## Class-wide history

- Monthly class-wide event counts since 2023 are charted [derived: monthly-events] [src: commercial/openfda-maude-infusion-monthly@2026-07-22]; the trailing two months are excluded — MAUDE reporting lag makes them artificially low, and charting them would fake a decline.
- 294,608 events in the charted window [derived: total-events] [src: commercial/openfda-maude-infusion-monthly@2026-07-22].

## Method & provenance

- Counts measured from openFDA's count API [src: commercial/openfda-maude-infusion-mfr@2026-07-22] and [src: commercial/openfda-maude-infusion-monthly@2026-07-22] (public domain).
- No comparative-safety claim is substantiated by this data alone — see the assumption
  record [assume: A-001] for what would be required.
