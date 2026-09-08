---
report_sha256: 84eff2fd00c1ed5a6722f452326e7cb7854cdfb56556a64090ea454439fcd79e
data_sha256: 3c751960d898c136990cd7b103f5e41c0c6f1db4cf1e108ece13b0681474c3b7
generated_at: '2026-09-08T19:54:40+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

BD (CareFusion) dominates MAUDE adverse-event reports for infusion pumps with 61,417 events [src: commercial/openfda-maude-infusion-mfr@2026-07-22], while the next four competitors cluster between 5,474 and 9,548 events [src: commercial/openfda-maude-infusion-mfr@2026-07-22] — a count-level gap that looks meaningful but cannot yet be interpreted as a safety-rate advantage. The key decision this analysis informs is competitive safety positioning: whether PP3500 can claim a favorable adverse-event profile versus field peers. That claim is currently blocked because no manufacturer-level event rate can be computed without an installed-base denominator, and that denominator remains unquantified [derived: v-main] [assume: A-001]. Counts alone are insufficient for a rate claim; the single biggest caveat is that [assume: A-001] must be resolved before any rate-based safety comparison is defensible.

## Event counts by manufacturer (entity-normalized)

BD (CareFusion) accounts for 61,417 MAUDE events [src: commercial/openfda-maude-infusion-mfr@2026-07-22] — roughly six times the next closest competitor — which likely reflects its larger installed base rather than a worse safety profile. Baxter, Smiths Medical, ICU Medical, Fresenius Kabi, and Medtronic report between 5,474 and 9,548 events each [src: commercial/openfda-maude-infusion-mfr@2026-07-22], a band narrow enough that count differences among them carry little competitive weight without a denominator. Manufacturer names are normalized through a versioned alias map [config: entity-aliases.yml], so the table reflects canonical entities, not raw FDA strings. What would change this reading: a quantified installed-base model [assume: A-001] that converts these counts into rates, or a change in the alias mapping that shifts events between canonical entities.

## Why there is no rate chart here

The rate series is mechanically blocked, not a judgment call: the data record for event rate per installed device carries an evidence class of "unavailable" and zero data points [assume: A-001]. FDA's own disclaimer states that MAUDE counts cannot establish incidence rates, and the installed-base denominator required to compute them has not yet been quantified [derived: v-main] [assume: A-001]. A secondary bias compounds the problem: reporting propensity differs across manufacturers in ways that no denominator alone can correct [assume: A-001]. This section should be read as a gate condition — the rate chart will appear in a future edition once [assume: A-001] carries a reviewed model.

## Class-wide history

The class-wide monthly series totals 294,608 events in the charted window [derived: total-events] [src: commercial/openfda-maude-infusion-monthly@2026-07-22], with the trailing two months excluded to avoid the artificial decline that MAUDE's reporting lag creates [derived: monthly-events] [src: commercial/openfda-maude-infusion-monthly@2026-07-22]. The monthly pattern across the window shows a high early period — peaking at 19,945 events in 2023-03 [derived: monthly-events] [src: commercial/openfda-maude-infusion-monthly@2026-07-22] — followed by a sustained step down into the 3,600–5,200 range that persists through 2026-04 [derived: monthly-events] [src: commercial/openfda-maude-infusion-monthly@2026-07-22]. That step-change warrants investigation: it may reflect a real reduction in field incidents, a shift in manufacturer reporting behavior, or a data artifact. Any trend interpretation should hold open all three explanations until the installed-base context from [assume: A-001] is available.
