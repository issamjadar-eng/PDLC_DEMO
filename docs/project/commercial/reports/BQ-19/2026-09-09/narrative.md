---
report_sha256: ab48cd3d48ac1a2f16a01f5b97e861ed23cc56a1a70a28113412df0ba80ba5af
data_sha256: c579ad40d7796411a343f1c36c024871cb47317aef107301fb9b609759b377d9
generated_at: '2026-09-09T00:36:22+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

MAUDE event counts for the infusion-pump device class are available and comparable across manufacturers, but a rate comparison — events per installed device — is mechanically blocked until the installed-base denominator is quantified [derived: v-main] [assume: A-001]. BD (CareFusion) leads all manufacturers with 64,178 events [src: commercial/openfda-maude-infusion-mfr@2026-09-09]; the remaining five manufacturers range from 5,724 to 9,822 events [src: commercial/openfda-maude-infusion-mfr@2026-09-09]. This data informs competitive positioning and post-market surveillance planning, but no comparative-safety claim can be substantiated from counts alone. The single biggest caveat: a large count may simply reflect a large installed fleet rather than elevated risk, so the gap between BD and the rest is uninterpretable as a safety signal until assumption A-001 carries a reviewed model [assume: A-001].

## Event counts by manufacturer (entity-normalized)

BD (CareFusion) carries 64,178 MAUDE events [src: commercial/openfda-maude-infusion-mfr@2026-09-09] — a figure that stands apart from the rest of the field. Baxter, ICU Medical, and Smiths Medical cluster tightly at 9,822, 9,240, and 9,228 events respectively [src: commercial/openfda-maude-infusion-mfr@2026-09-09]; Fresenius Kabi sits at 6,860 and Medtronic at 5,724 [src: commercial/openfda-maude-infusion-mfr@2026-09-09]. Manufacturer names are consolidated through a versioned alias map [config: entity-aliases.yml], so fragmented filings under variant names roll up to a single canonical entity — unmatched names remain visible and do not silently inflate or suppress any total. The count gap between BD and the rest is striking in absolute terms, but without an installed-base denominator it cannot be interpreted as a signal of elevated risk.

## Why there is no rate chart here

The rate series is mechanically blocked — this is a data constraint, not a judgment call [assume: A-001]. FDA explicitly disclaims that MAUDE event counts cannot establish incidence rates; producing a per-manufacturer rate requires an installed-base estimate, and that estimate — assumption A-001 — has not yet been quantified [assume: A-001] [derived: v-main]. A second unresolved factor is reporting propensity: manufacturers differ in how systematically they file adverse events, so even a valid denominator would leave that bias unmodeled [assume: A-001]. The practical decision this section informs is a prerequisite gate: before PP3500's field performance can be positioned against competitors on a rate basis, A-001 must carry a reviewed model with accepted inputs.

## Class-wide history

The monthly trend covers 299,419 events in the charted window [derived: total-events] [src: commercial/openfda-maude-infusion-monthly@2026-09-09], with the trailing two months excluded to avoid the artificial suppression caused by MAUDE reporting lag. The series shows a sharp peak in early 2023 followed by a sustained step-down to a lower baseline that has held relatively steady since mid-2024 [derived: monthly-events] [src: commercial/openfda-maude-infusion-monthly@2026-09-09]. A market-entry analysis that anchors on the 2023 peak overstates the current class-wide event burden. The trend does not reveal cause — it may reflect fleet composition changes, reporting-practice shifts, or device-performance improvements — but it sets the ambient baseline against which PP3500's post-launch event counts will eventually be read.
