---
report_sha256: fba26892dd746beaac11f47fc5d240d12729b39e066e1d32a2930dcbd1a1262b
data_sha256: 8031b758b2d42db99b1ea535236a5223c8cc2134e504f4dc2bc3f9da092d3ddf
generated_at: '2026-09-08T19:53:32+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

The PP3500's 5-year all-in TCO is $8,900 per pump [derived: v-main] [config: commercial.yml], and $5,100 on the capital-plus-service basis used for competitive comparison [derived: our-tco]. The class-wide competitor range on that same basis is $3,000–$15,000 [assume: A-004], but it excludes consumables and software subscription — both undisclosed — meaning competitor true all-in cost sits strictly above that range; the ranges overlap and no hard cost-leadership claim is supportable [derived: v-main]. The decision this informs is whether to deploy a TCO argument in buyer conversations; the analysis says to hold until finance ratifies the per-pump constants [config: commercial.yml] and the competitor pricing assumption is refreshed [assume: A-004]. The single biggest caveat is structural: the two sides of the comparison are not built the same way, and any buyer-facing presentation that omits that disclosure misleads rather than persuades [assume: A-004] [derived: tco-comparison].

## Our 5-yr TCO per pump (declared constants) [config: commercial.yml]

The all-in 5-year total is $8,900 per pump [derived: our-tco] [config: commercial.yml], with capital the largest single component at $4,200 [config: commercial.yml], followed by Cloud Suite subscription at $2,250 [config: commercial.yml] across five years. Consumables add $1,550 and service adds $900 over the same period [derived: our-tco] [config: commercial.yml], making recurring costs collectively larger than the one-time capital outlay. The $5,100 capital-plus-service subtotal [derived: our-tco] is the only basis that can be placed beside the competitor range without a methodology mismatch; buyer-facing material should use that figure unless competitor consumable and subscription costs become available.

## Competitor side — a RANGE, and why it is one

The class-wide indicative 5-year TCO on a capital-plus-service basis spans $3,000–$15,000 [assume: A-004], a range wide enough that overlap with our $5,100 [derived: our-tco] is real and cannot be dismissed. The breadth reflects negotiated GPO and IDN contract prices that are never published [assume: A-004]; Alaris, Spectrum IQ, and Plum 360 share one combined range because public data does not split by vendor [assume: A-004]. Consumables pricing and software-subscription magnitude are excluded from the competitor side because they are undisclosed, so competitor true all-in TCO is strictly above $3,000–$15,000 [assume: A-004]. The reading changes if a new procurement award, GPO disclosure, or analyst pricing commentary surfaces — any of those events should trigger a refresh of the assumption record [assume: A-004].

## Feature context per competitor (curated matrix; verification status carried)

On battery life, the PP3500 reports 150 hours against 6 hours for Alaris and 7 hours for Plum 360 [src: commercial/external-competitor-features@2026-07-27]; no confirmable Spectrum IQ figure exists. Flow accuracy follows the same direction: PP3500 at 0.35% versus 2.3% for both Alaris and Spectrum IQ [src: commercial/external-competitor-features@2026-07-27], with no confirmable Plum 360 value. Drug library and wireless connectivity are present across all four products, though two Spectrum IQ cells carry a "(verify)" flag indicating the source was named but not independently confirmed [src: commercial/external-competitor-features@2026-07-27]. Predictive monitoring is absent across every product in the matrix [src: commercial/external-competitor-features@2026-07-27], which matters for framing any future roadmap differentiation — no incumbent has established a baseline here.

## Narrative — Risks / Mitigations / Issues

The high-severity risk is structural: the competitor range of $3,000–$15,000 excludes consumables and software subscription that are included in our all-in total of $8,900, so presenting a side-by-side figure without stating that gap understates competitor cost [assume: A-004] [derived: tco-comparison] [config: commercial.yml]. The prescribed fix is to show only the capital-plus-service basis side-by-side and state the exclusions verbatim from the assumption record [assume: A-004] [derived: tco-comparison]. The medium-severity risk sits on our own side: the four per-pump constants are not finance-validated [config: commercial.yml], which means both halves of the buyer spreadsheet are currently unverified; finance ratification is required before any external use [config: commercial.yml].

## Data gap (stated, not papered over)

No TCO trend history exists [derived: tco-history]; this analysis is a single-point-in-time snapshot with no prior dated vintage to compare against. Building a history series requires dated refreshes of the pricing assumption as procurement disclosures emerge [derived: tco-history] — the record explicitly marks this as unavailable rather than filling it with a placeholder. Until those refreshes accumulate, no trend direction can be read and no rate of change is supportable.
