---
doc_id: complaints-ledger
doc_type: complaints-ledger
device_ids: [DEV-PP3500]
patient_populations: [adult, post-surgical]
care_settings: [hospital, acute-care]
therapy_context: [pca, acute-pain]
evidence_grade: high
primary_endpoints: [use-errors, medication-errors, device-failures, alarm-rate]
related_user_needs: []
related_design_inputs: []
status: active
last_updated: 2026-04-12
---

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project (anchor product: PP3500 / PainEase PCA Advanced)._

# PP3500 Complaints Ledger (2022–2025)

## Document Metadata

| Field | Value |
|---|---|
| Document ID | DHF-PP3500-COMP-001 |
| Revision | A |
| Status | Active |
| Device | DEV-PP3500 (PainEase PCA Advanced) |
| Owner | GlobalLogic Post-Market Surveillance |
| Coverage period | 2022-01-01 to 2025-12-31 |

This ledger consolidates customer complaints for the PainEase PCA Advanced (PP3500) across the post-launch period through 2025. In a production QMS this view would be sourced from the complaint handling system (Trackwise / Veeva Vault QMS); the table below is a static demo extract for use by the customer-insights agent. Severity follows the GlobalLogic post-market surveillance procedure: `low` (no patient impact, cosmetic / nuisance), `medium` (workflow impact, user must intervene), `high` (potential patient harm averted by safeguard), `near-miss` (potential patient harm averted by an external check, not by the device itself).

## Complaints

| Complaint ID | Date | Device ID | SW Ver | Site Type | Category | Severity | Summary | Root Cause | Linked CAPA | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| COMP-2022-014 | 2022-08-12 | DEV-PP3500 | 1.1.3 | Hospital | battery | low | Battery indicator dropped 30% after 4 hours in cold storage room | Cold-temperature capacity drift within spec | — | Closed |
| COMP-2022-019 | 2022-10-03 | DEV-PP3500 | 1.1.4 | Hospital | alarm-false-positive | low | Occlusion alarm at 0.05 mL/hr morphine continuous infusion | Pressure transducer noise at very low flow; within tolerance | — | Closed |
| COMP-2022-022 | 2022-11-18 | DEV-PP3500 | 1.2.0 | Surgery Center | barcode-read | low | Barcode scanner failed to read vial label at >60 deg angle | User scanning technique; addressed by training material | — | Closed |
| COMP-2023-001 | 2023-01-10 | DEV-PP3500 | 1.2.2 | Hospital | decimal-point | near-miss | Nurse read 0.5 mL/hr as 5 mL/hr during independent double-check; intercepted before start | Decimal glyph legibility | CAPA-2023-001 | Closed |
| COMP-2023-002 | 2023-01-11 | DEV-PP3500 | 1.2.2 | Hospital | decimal-point | near-miss | Decimal misread on hydromorphone PCA basal entry | Decimal glyph legibility | CAPA-2023-001 | Closed |
| COMP-2023-003 | 2023-01-13 | DEV-PP3500 | 1.2.1 | Hospital | decimal-point | near-miss | Pharmacy informatics flagged repeat decimal misreads in PACU | Decimal glyph legibility | CAPA-2023-001 | Closed |
| COMP-2023-004 | 2023-01-15 | DEV-PP3500 | 1.2.2 | Hospital | decimal-point | high | Inverse 0.1x near-miss; 5 mL/hr read as 0.5 mL/hr, intercepted | Decimal glyph legibility | CAPA-2023-001 | Closed |
| COMP-2023-005 | 2023-01-16 | DEV-PP3500 | 1.2.2 | Hospital | decimal-point | near-miss | Night-shift double-check decimal misread, low ambient lighting | Decimal glyph legibility, contrast | CAPA-2023-001 | Closed |
| COMP-2023-006 | 2023-01-18 | DEV-PP3500 | 1.2.2 | Hospital | decimal-point | near-miss | Bupivacaine epidural-PCA basal decimal misread | Decimal glyph legibility | CAPA-2023-001 | Closed |
| COMP-2023-007 | 2023-01-19 | DEV-PP3500 | 1.2.0 | Hospital | decimal-point | near-miss | Decimal misread during shift handoff verification | Decimal glyph legibility | CAPA-2023-001 | Closed |
| COMP-2023-008 | 2023-01-22 | DEV-PP3500 | 1.2.2 | Hospital | decimal-point | near-miss | Bedside double-check decimal misread, off-axis viewing | Decimal glyph legibility | CAPA-2023-001 | Closed |
| COMP-2023-009 | 2023-01-24 | DEV-PP3500 | 1.2.2 | Hospital | decimal-point | near-miss | Two near-misses reported by single PACU site within one shift | Decimal glyph legibility | CAPA-2023-001 | Closed |
| COMP-2023-010 | 2023-01-26 | DEV-PP3500 | 1.2.1 | Hospital | decimal-point | near-miss | Morphine PCA decimal misread on confirmation screen | Decimal glyph legibility | CAPA-2023-001 | Closed |
| COMP-2023-011 | 2023-01-29 | DEV-PP3500 | 1.2.2 | Hospital | decimal-point | near-miss | Decimal misread, FSN compliance check in progress at site | Decimal glyph legibility | CAPA-2023-001 | Closed |
| COMP-2023-012 | 2023-01-30 | DEV-PP3500 | 1.2.2 | Hospital | decimal-point | near-miss | Twelfth decimal complaint of January; CAPA opened | Decimal glyph legibility | CAPA-2023-001 | Closed |
| COMP-2023-018 | 2023-03-04 | DEV-PP3500 | 1.2.2 | Hospital | alarm-false-positive | low | Air-in-line alarm triggered by micro-bubble after bag swap | Within spec; user retrained | — | Closed |
| COMP-2023-024 | 2023-04-22 | DEV-PP3500 | 1.2.4 | Hospital | connectivity | medium | Wi-Fi reconnection delayed 90 s after AP roam | Network roaming; firmware tuning planned for v1.3 | — | Closed |
| COMP-2023-031 | 2023-06-11 | DEV-PP3500 | 1.3.0 | Hospital | battery | low | Battery health flag after 9 months of intensive use | Expected wear; replacement under warranty | — | Closed |
| COMP-2023-040 | 2023-09-02 | DEV-PP3500 | 1.3.0 | Surgery Center | touchscreen | low | Touchscreen unresponsive in single corner | Hardware; unit RMA'd | — | Closed |
| COMP-2024-003 | 2024-01-15 | DEV-PP3500 | 1.3.1 | Hospital | barcode-read | low | Scanner intermittent on aged labels | User-training and label-quality issue | — | Closed |
| COMP-2024-011 | 2024-03-08 | DEV-PP3500 | 1.3.1 | Hospital | alarm-false-positive | low | Occlusion alarm at 0.02 mL/hr near sensor floor | Within spec; documented as known limitation | — | Closed |
| COMP-2024-019 | 2024-05-21 | DEV-PP3500 | 1.3.2 | Hospital | connectivity | low | EMR HL7 message timeout during nightly batch | Hospital network maintenance | — | Closed |
| COMP-2024-027 | 2024-08-04 | DEV-PP3500 | 1.3.2 | Hospital | cleaning | low | Lockbox latch stiff after repeated cleaning | Disinfectant compatibility note added to IFU | — | Closed |
| COMP-2024-035 | 2024-11-12 | DEV-PP3500 | 1.3.2 | Hospital | hardware | medium | IV pole clamp loosened during patient transport | Hardware revision in v1.4 mechanical kit | — | Monitoring |
| COMP-2025-006 | 2025-02-19 | DEV-PP3500 | 1.4.0 | Hospital | battery | low | Charging time longer than spec on one unit | Charger circuit; RMA'd | — | Closed |
| COMP-2025-014 | 2025-05-30 | DEV-PP3500 | 1.4.0 | Surgery Center | other | low | IFU clarification request — drug library update workflow | Documentation gap; addressed in IFU rev | — | Closed |
| COMP-2025-022 | 2025-08-17 | DEV-PP3500 | 1.4.1 | Hospital | connectivity | low | Bluetooth pairing flap with bedside monitor | Investigation open with monitor vendor | — | Open |

## Summary Statistics

**By category:**

| Category | Count |
|---|---|
| decimal-point | 12 |
| alarm-false-positive | 3 |
| battery | 3 |
| connectivity | 3 |
| barcode-read | 2 |
| touchscreen | 1 |
| hardware | 1 |
| cleaning | 1 |
| other | 1 |
| **Total** | **27** |

**By severity:**

| Severity | Count |
|---|---|
| near-miss | 11 |
| high | 1 |
| medium | 3 |
| low | 12 |
| **Total** | **27** |

**Status:**

| Status | Count |
|---|---|
| Closed | 25 |
| Monitoring | 1 |
| Open | 1 |

**CAPA linkage:** 12 complaints linked to CAPA-2023-001 (all decimal-point category). No other open CAPAs.

## Trend Notes

- Pre-CAPA period (Jan 2023): 12 decimal-point complaints in 30 days. Post-fix (May 2023 onward): 0 decimal-point complaints in 20+ months, per PMCF monitoring under PMCF-1001.
- Battery-related complaints are within expected wear distribution for the lithium-ion chemistry and have not exceeded the threshold defined in the PMCF plan.
- Connectivity complaints have shifted from device-side (firmware) in 2023 to environment-side (network, peer device) in 2024–2025; no design action triggered.
- Hardware complaint COMP-2024-035 is being monitored pending the v1.4 mechanical kit deployment.
