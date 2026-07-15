---
source_file: "N/A — authored-in-markdown"
source_path: "pca-device/risk-management/GL-TMP-RM-003-hazard-analysis.md"
doc_id: "PCA-DEVICE-GL-TMP-RM-003-hazard-analysis"
doc_type: "QSD"
title: "Hazard Analysis — pca-device"
format: "md"
conversion_date: "2026-04-21"
conversion_method: "claude-authored"
conversion_fidelity: "faithful"
pages: null
sheets: null
has_images: false
image_count: 0
has_tables: true
has_form_fields: true
references:
  - doc_id: "GL-TMP-RM-003"
    title: "Parent QMS template"
    resolved: true
    match: null
    note: "ISO 14971 §5"
conversion_history:
  - date: "2026-04-21"
    source: "v0.1 DRAFT — placeholder stub via task ben/023"
  - date: "2026-07-14"
    source: "v0.2 DRAFT — hazard analysis backfilled under task ben/102"
notes: "Populated hazard analysis for PP3500 — 16 hazards scored per GL-STD-RM-001, DI trace column aligned to DHF-PP3500-DI-001. Transition to 1.0 via GL-SOP-QM-001 when ready."
---

<!-- AI-CHANGELOG — internal provenance of AI-assisted edits. Metadata only:
     NOT published downstream, NOT part of the controlled record.
| Date       | Task | Summary |
|------------|------|---------|
| 2026-07-14 | 102  | Hazard analysis backfilled: 16 hazards, GL-STD-RM-001 scoring, DI trace column populated. |
| 2026-07-14 | 102  | QA-conformance pass (quality-engineering): CONFORMANT — all 16 rows matrix-recomputed clean; no changes required. |
| 2026-07-14 | 102  | Reference audit (RA-gl-tmp-rm-003-hazard-analysis-001): fixed stale clause cite 81001-5-1 §5→§7.1 (threat modeling); RMR disposition claim softened to forward tense; Annex C taxonomy [VERIFY] added. |
-->

# PCA-DEVICE-GL-TMP-RM-003-hazard-analysis — Hazard Analysis

_Demo sample data — not for clinical use._

**DHF:** `pca-device`
**Parent QMS Template:** [`GL-TMP-RM-003`](../../../../internal/source-md/qms-index.md)
**Standards Anchor:** ISO 14971 §5
**Revision:** 0.2 DRAFT
**Effective Date:** — (not released)

This document records the ISO 14971 §5 hazard analysis for the PainEase PCA Advanced (PP-3500) patient-controlled analgesia infusion pump. Hazards were identified per GL-WI-RM-001 using the ISO 14971 Annex C stimulus classes (energy, biological & chemical, operational, information, environmental) [VERIFY — confirm the class taxonomy against the ISO 14971:2019 original; the registry distillation characterizes Annex C as safety-characteristic questions], the IEC 60601-1 hazard clauses, IEC 81001-5-1 §7.1 threat modeling for the connected functions, and predicate history (including the decimal-point misread heritage of predicate CAPA-2023-001). Severity (S), Probability (P), and the risk-acceptance regions are taken exclusively from GL-STD-RM-001 §3, §4, and the §5 acceptance matrix. Each hazard traces to the implementing design inputs in DHF-PP3500-DI-001 (`../design-controls/requirements/design-inputs.md`). Bottom-up dFMEA/pFMEA analyses in the sibling GL-TMP-RM-004 documents link back to these HAZ IDs via their Linked Hazard ID column.

---

## Identification

| Field | Value |
|---|---|
| Product | PainEase PCA Advanced PP-3500 |
| Revision | 0.2 DRAFT |
| Date | 2026-07-14 |
| Team | Cross-functional demo team (systems, SW, risk, clinical, HF, cybersecurity, quality) |

## Hazard Analysis Table

| HAZ ID | Hazard (ISO 14971 Annex C class) | Hazardous Situation | Foreseeable Sequence of Events | Harm | S (pre) | P (pre) | Risk (pre) | Controls (design / protective / info) | Design Input(s) | Verification(s) | S (post) | P (post) | Residual Risk | New Hazards Introduced? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HAZ-001 | Over-infusion — pump mechanism/motor runaway (Operational) | Patient receives opioid at a rate exceeding the programmed rate | Motor drive or control electronics fault (single fault) → pump delivers above programmed rate → excess opioid infused before detection → respiratory depression | Opioid overdose; respiratory arrest / death | 5 | 3 | Unacceptable | Flow-rate accuracy design ±5% across operating range (DI-001, design); independent volume-tracking over-infusion watchdog with high-priority alarm and motor halt (DI-009, protective); 1-hr/4-hr cumulative dose limits blocking excess delivery (DI-004, protective) | DI-001, DI-009, DI-004 | VER-PP3500-BT-005 (gravimetric bench test per IEC 60601-2-24 §201.12.1.101); software-in-the-loop fault-injection test with motor-halt verification; VER-PP3500-SW-002 | 5 | 1 | ALARP | No |
| HAZ-002 | Over-infusion — programming error, decimal-point misread (Operational / use-related) | Pump programmed at ~10× the intended rate or bolus dose | Nurse misreads decimal point on numeric entry (heritage of predicate CAPA-2023-001) → 10× value programmed → confirmation step missed → overdose delivered | Severe respiratory depression requiring rescue | 4 | 4 | Unacceptable | Unambiguous decimal-point display with explicit decimal-placement confirmation (DI-013, design); drug-library hard limits blocking out-of-range values on every entry path (DI-005, design); 1-hr/4-hr cumulative dose limits (DI-004, protective); validated programming task flow with zero harmful use errors (DI-020, design) | DI-013, DI-020, DI-005, DI-004 | Summative usability test per IEC 62366-1 (n≥15 nurses, zero decimal misreads); VER-PP3500-SW-006; VER-PP3500-SW-002 | 4 | 2 | ALARP | No |
| HAZ-003 | Wrong drug / wrong concentration administered (Operational) | Patient infused with a medication or concentration other than prescribed | Wrong cassette loaded or concentration mismatch vs order → mismatch not detected before therapy start → patient receives unintended drug/concentration | Overdose with severe respiratory depression, or under-treatment of pain | 4 | 4 | Unacceptable | Integrated 1D/2D barcode scan matched against active drug library with blocking mismatch alert (DI-016, protective); on-board drug library ≥200 medications with version banner at therapy start (DI-015, design); drug-library hard limits (DI-005, design) | DI-016, DI-015, DI-005 | Barcode bench test (50-medication reference set, ≥98% first-read, mismatch blocking alert); software test of library count/version banner; VER-PP3500-SW-006 | 4 | 2 | ALARP | No |
| HAZ-004 | Free-flow delivery with administration set removed (Operational) | Uncontrolled gravity flow of opioid into the patient | Administration set removed from pumping mechanism or door opened under head pressure → no flow restriction → container contents free-flow into patient | Massive opioid overdose; death | 5 | 4 | Unacceptable | Integral anti-siphon / anti-free-flow mechanism on the dedicated administration set (DI-006, inherently safe design) | DI-006 | Bench test per IEC 60601-2-24 §201.12.1.103 (door-open under ±1 m head pressure, free-flow ≤0.1 mL/60 s, n=10 sets) | 5 | 1 | ALARP | No |
| HAZ-005 | Air embolism — air-in-line infused (Operational) | Air infused into the patient's vein | Air enters line (emptied container, loose fitting, inadequate priming) → bubbles pass undetected to patient → venous air embolism | Life-threatening air embolism | 4 | 3 | ALARP | Air-in-line detection ≥50 µL single bubble / ≥1 mL cumulative per 15 min, with high-priority alarm and delivery stop (DI-008, protective) | DI-008 | Bench test with calibrated air injector (0.05/0.1/0.5 mL boluses, 100% detection, n=20 per condition) | 4 | 1 | Acceptable | No |
| HAZ-006 | Undetected downstream occlusion — therapy interruption + post-occlusion bolus (Operational) | Delivery silently stops; on release, accumulated volume delivered as an unintended bolus | Line kinked or clamp left closed → delivery stops without annunciation → analgesia gap; occlusion release discharges accumulated pressure as bolus | Uncontrolled pain requiring intervention; transient over-delivery on release | 3 | 4 | ALARP | Downstream occlusion detection 3–15 psi with high-priority alarm within the IEC 60601-2-24 response time (DI-007, protective) | DI-007 | Bench test per IEC 60601-2-24 §201.12.4.4.103 (3 flow rates, alarm time within standard limits, n=10) | 3 | 2 | Acceptable | No |
| HAZ-007 | Therapy interruption — battery depletion / power loss (Energy) | Infusion stops while patient depends on continuous analgesia | Device unplugged for transport / ambulation → battery depletes → pump stops → analgesia gap until noticed | Uncontrolled pain requiring medical intervention | 3 | 4 | ALARP | ≥150 h battery endurance under nominal therapy (DI-017, design); ≤4 h full recharge (DI-018, design); remaining-battery-life presentation on home screen readable at 1 m (DI-021, protective/info) | DI-017, DI-018, DI-021 | Battery endurance bench test (n=5, mean ≥150 hr); charge-time bench test (n=5, ≤4 hr); formative usability evaluation of home-screen legibility | 3 | 2 | Acceptable | No |
| HAZ-008 | Alarm failure — not annunciated or not heard (Information) | An alarm condition exists but clinical staff are not alerted | Alarm condition occurs (e.g., occlusion, air-in-line) → speaker fault, or SPL inadequate for ward noise → staff unaware → underlying hazardous situation persists | Delayed intervention; serious patient deterioration requiring rescue | 4 | 3 | ALARP | IEC 60601-1-8-compliant high/medium/low-priority audible alarm scheme with SPL adjustable 45–80 dB(A) at 1 m (DI-019, protective); electrical-safety and essential-performance compliance per IEC 60601-1 and IEC 60601-2-24 covering alarm-function integrity (DI-010, design) | DI-019, DI-010 | Acoustic measurement in anechoic chamber (SPL range + alarm melody compliance, all categories); third-party safety testing report per IEC 60601-1 / IEC 60601-2-24 | 4 | 2 | ALARP | Yes — high SPL settings contribute to alarm fatigue; assessed S2/P3 = Acceptable per GL-STD-RM-001 §5 |
| HAZ-009 | Electrical shock (Energy) | Patient or operator contacts hazardous leakage current | Insulation or protective-earth fault (single fault) → enclosure or applied part becomes live → patient/operator contact | Electrical burn; cardiac arrhythmia; life-threatening injury | 4 | 3 | ALARP | Electrical-safety design per IEC 60601-1 (3rd edition + A1) and IEC 60601-2-24 — insulation, leakage-current limits, applied-part isolation (DI-010, design) | DI-010 | Third-party electrical safety test report (all applicable IEC 60601-1 / 60601-2-24 clauses, no deviations) | 4 | 1 | Acceptable | No |
| HAZ-010 | EMC disturbance disrupting delivery (Energy — electromagnetic) | Delivery deviates or halts under electromagnetic disturbance | RF source near pump (electrosurgery, RFID, telemetry) → disturbance couples into pump electronics → delivery error or unintended stop | Over- or under-delivery; serious injury requiring intervention | 4 | 3 | ALARP | EMC immunity and emissions design per IEC 60601-1-2 (4th edition) for professional healthcare facility environments, with essential performance maintained during immunity exposure (DI-012, design) | DI-012 | Third-party EMC test report (all immunity tests pass with essential performance maintained; emissions within Class B limits) | 4 | 1 | Acceptable | No |
| HAZ-011 | Biological contamination / material incompatibility — fluid path and patient-contact surfaces (Biological & chemical) | Patient exposed to leachables, degraded materials, or bioburden | Non-biocompatible or cleaning-degraded material in fluid path / patient-contact surface → leachables or contamination reach patient over therapy duration | Local infection, irritation, or sensitization requiring medical treatment | 3 | 3 | ALARP | Biocompatible patient-contacting materials per ISO 10993-1 for the intended contact category (DI-011, design); housing/touchscreen/lockbox materials compatible with hospital disinfection agents for the service life (DI-030, design) | DI-011, DI-030 | Biocompatibility evaluation per ISO 10993-1 with cytotoxicity/sensitization/irritation testing per ISO 10993-5/-10; 1000-cycle wipe-compatibility bench test | 3 | 2 | Acceptable | No |
| HAZ-012 | Cybersecurity — unauthorized modification of therapy parameters or firmware (Information) | Pump operates on attacker-modified therapy settings or firmware | Attacker gains network or physical access → modifies therapy parameters or loads unauthorized firmware → pump delivers unsafe therapy | Opioid overdose; death | 5 | 3 | Unacceptable | Authenticated/signed firmware update, role-based access control, TLS 1.2+ encrypted communications (DI-024, design); tamper-evident audit logging of all programming and security events (DI-034, protective/detective); SBOM with vulnerability monitoring for fielded firmware (DI-025, protective) | DI-024, DI-034, DI-025 | Cybersecurity testing per IEC 81001-5-1 and FDA premarket cybersecurity guidance incl. penetration test (zero exploitable critical findings); software test of 10,000-event audit-log retention/integrity/export; SBOM inspection vs build manifest | 5 | 1 | ALARP | No |
| HAZ-013 | Opioid diversion — unauthorized access to drug cassette (Operational) | Patient's analgesic supply removed or tampered with; drug diverted | Unauthorized person opens cassette compartment → removes or substitutes opioid → patient under-dosed and therapy interrupted | Untreated pain requiring intervention; therapy interruption | 3 | 4 | ALARP | Key/PIN-released drug-cassette lockbox with tamper-evident indication of unauthorized opening (DI-032, protective) | DI-032 | Mechanical inspection and 50-cycle tamper-attempt test (n=5 lockboxes, all unauthorized entries leave visible evidence) | 3 | 2 | Acceptable | Yes — lockbox can delay legitimate access during urgent cassette change; mitigated by PIN-released latch (DI-032); assessed S2/P3 = Acceptable per GL-STD-RM-001 §5 |
| HAZ-014 | PCA-by-proxy — bolus activation by someone other than the patient (Operational — foreseeable misuse) | Boluses delivered while the patient is too sedated to self-limit dosing | Family member or caregiver presses bolus button "to help" → the inherent PCA safety feedback (a sedated patient stops pressing) is defeated → doses stack | Severe respiratory depression requiring rescue | 4 | 4 | Unacceptable | Programmable 1–99 min lockout interval between boluses (DI-003, design); 1-hr/4-hr cumulative dose limits blocking over-limit boluses from any path (DI-004, design/protective); IFU and labeling opioid warnings incl. patient-only-activation instruction (DI-029, info) | DI-003, DI-004, DI-029 | VER-PP3500-SW-002 (lockout and cumulative-limit software tests); regulatory labeling review checklist per 21 CFR 801 | 4 | 2 | ALARP | No |
| HAZ-015 | Misleading remote data — EHR event-message loss or corruption (Information) | Clinician acts on stale or incorrect remote therapy/alarm data | Therapy or alarm event message lost/corrupted en route to EHR → remote record diverges from device state → remote clinician decision made on wrong data → delayed intervention | Delayed treatment; reversible injury requiring medical intervention | 3 | 3 | ALARP | Validated HL7 v2.5 / FHIR R4 event publication with protocol-conformant messaging (DI-023, design); tamper-evident on-device audit log with integrity hash as the authoritative event record (DI-034, protective) | DI-023, DI-034 | Interface protocol test against reference HL7 listener (zero validation errors over 1000-event run); software test of audit-log integrity and export | 3 | 2 | Acceptable | No |
| HAZ-016 | Mechanical failure — drop or mount detachment during transport (Energy — mechanical) | Pump falls onto patient/floor; therapy interrupted or device damaged | Pump inadequately mounted or dropped during patient transport/ambulation → impact damages device or strikes patient → therapy interruption or impact injury | Contusion/laceration; therapy interruption requiring intervention | 3 | 4 | ALARP | ≤0.85 kg device mass with dedicated IV-pole clamp and belt-clip mounting interfaces (DI-033, design); enclosure and mechanical robustness per IEC 60601-1 (DI-010, design) | DI-033, DI-010 | Mass measurement (n=10) and mechanical fit-check on standard IV pole and belt clip; third-party safety testing report per IEC 60601-1 | 3 | 2 | Acceptable | No |

## Summary

| Region (post) | Count |
|---|---|
| Unacceptable | 0 |
| ALARP | 7 |
| Broadly acceptable | 9 |

Pre-control distribution for reference: 6 Unacceptable (HAZ-001, HAZ-002, HAZ-003, HAZ-004, HAZ-012, HAZ-014), 10 ALARP, 0 Acceptable. Every pre-control Unacceptable risk is reduced by design or protective measures (not information for safety alone), per GL-STD-RM-001 §6. Residual ALARP risks (HAZ-001, HAZ-002, HAZ-003, HAZ-004, HAZ-008, HAZ-012, HAZ-014) will be dispositioned in the Risk Management Report (GL-TMP-RM-002 instance — not yet authored); the S5 hazards remain ALARP by matrix construction (S5 rows cannot reach Acceptable per GL-STD-RM-001 §5) and feed the benefit-risk considerations of GL-STD-RM-001 §7.

## Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| Risk Manager | | | |
| Systems Engineering Lead | | | |
| Quality Engineering | | | |
| Clinical Affairs | | | |

## Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 0.1 DRAFT | 2026-04-21 | Placeholder (task ben/023) | Stub created from QMS template. |
| 0.2 DRAFT | 2026-07-14 | BX / AI Assistant | Hazard analysis backfilled: 16 hazards identified per GL-WI-RM-001 (Annex C classes, predicate history incl. CAPA-2023-001), scored per GL-STD-RM-001 §3/§4/§5, controls traced to DHF-PP3500-DI-001 design inputs, post-control summary added. |
