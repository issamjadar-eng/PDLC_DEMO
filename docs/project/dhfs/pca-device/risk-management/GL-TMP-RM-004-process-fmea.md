---
source_file: "N/A — authored-in-markdown"
source_path: "pca-device/risk-management/GL-TMP-RM-004-process-fmea.md"
doc_id: "PCA-DEVICE-GL-TMP-RM-004-process-fmea"
doc_type: "QSD"
title: "Process FMEA (pFMEA) — pca-device"
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
  - doc_id: "GL-TMP-RM-004"
    title: "Parent QMS template"
    resolved: true
    match: null
    note: "IEC 60812; 21 CFR 820.75"
conversion_history:
  - date: "2026-04-21"
    source: "v0.1 DRAFT — placeholder stub via task ben/023"
  - date: "2026-07-14"
    source: "v0.2 DRAFT — FMEA backfilled under task ben/102"
notes: "pFMEA for PP3500 manufacturing/production per GL-WI-RM-002 and GL-TMP-RM-004. 9 process failure modes; S per GL-STD-RM-001 §3; Linked Hazard IDs reference the GL-TMP-RM-003 hazard analysis spine where the escaped defect manifests as that hazard."
---

<!-- AI-CHANGELOG — internal provenance of AI-assisted edits. Metadata only:
     NOT published downstream, NOT part of the controlled record.
| Date       | Task | Summary |
|------------|------|---------|
| 2026-07-14 | 102  | FMEA backfilled: failure modes, GL-STD-RM-001 S scale, Linked Hazard IDs to GL-TMP-RM-003 spine. |
| 2026-07-14 | 102  | QA-conformance pass: CONFORMANT; coverage-summary region wording corrected (action rows split ALARP/Acceptable). |
-->

# PCA-DEVICE-GL-TMP-RM-004-process-fmea — Process FMEA (pFMEA)

_Demo sample data — not for clinical use._

**DHF:** `pca-device`
**Parent QMS Template:** [`GL-TMP-RM-004`](../../../../internal/source-md/qms-index.md)
**Standards Anchor:** IEC 60812; 21 CFR 820.75
**Revision:** 0.2 DRAFT
**Effective Date:** — (not released)

> Bottom-up failure analysis of the PainEase PCA Advanced (PP-3500) manufacturing and production processes per GL-WI-RM-002, methodology anchored in IEC 60812:2018, performed ahead of the pre-Transfer review (GL-SOP-DC-007). Each process failure mode is analyzed to the end effect an escaped defect would have on the patient/user, and modes with patient-harm potential link upward into the top-down hazard analysis (GL-TMP-RM-003) via the `Linked Hazard ID` column. Implementing design inputs (DHF-PP3500-DI-001) are cited in parentheses where they exist.

---

## Identification

| Field | Value |
|---|---|
| FMEA Type | ☐ dFMEA ☒ pFMEA |
| Product / Process | PainEase PCA Advanced (PP-3500) — assembly, calibration, test, labeling, and packaging processes |
| Revision | 0.2 DRAFT |
| Team | BX (Risk Management lead), Manufacturing Engineering, Test Engineering, Quality Engineering, R&D Firmware |

## Scoring Basis

- **Severity (S)** — GL-STD-RM-001 §3 five-level clinical-outcome scale, scored at the end effect of the escaped defect (5 Catastrophic → 1 Negligible).
- **Occurrence (O)** — 1–5, using the GL-STD-RM-001 §4 probability anchors applied to process-defect escape occurrence as a proxy. GL-WI-RM-002 §4 defers O/D scale definition to the product Risk Management Plan (GL-TMP-RM-001), which does not yet define FMEA-specific O anchors for this DHF [VERIFY — confirm O anchors when the PP3500 RM Plan is baselined].
- **Detection (D)** — GL-STD-RM-001 §9: D=1 (detected before harm) → D=5 (undetectable until harm occurs). For a pFMEA, detection is assessed against in-process and end-of-line controls that catch the defect before shipment.

## FMEA Table

| FM ID | Item / Function | Failure Mode | Local Effect | Next-Higher Effect | End Effect (patient/user) | Cause(s) | Existing Prevention Controls | Existing Detection Controls | S | O | D | Linked Hazard ID | Recommended Action | Action Owner | Action Due | S' | O' | D' | Action Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FM-P-001 | PCB reflow soldering — motor-driver and control PCBs | Solder joint voids / cold joints | Intermittent or high-resistance joint on driver stage | Erratic motor drive or in-service board failure | Uncontrolled delivery behavior or pump stop — overdose potential or untreated pain | Reflow thermal profile drift; paste volume variation; component coplanarity | Qualified reflow profile with periodic profiling; solder-paste inspection (SPI); process control per 21 CFR 820.75 process validation | Automated optical inspection (AOI) + X-ray on BGA/driver joints; in-circuit test; end-of-line functional test incl. delivery supervision check (DI-009) | 4 | 2 | 2 | HAZ-001 | — | — | — | — | — | — | — |
| FM-P-002 | Occlusion-sensor calibration at final test | Calibration error (wrong reference pressure / fixture drift) | Sensor threshold offset from true 3–15 psi range | Shipped unit alarms late or not at all on occlusion | Undetected occlusion in field — untreated pain; post-occlusion bolus on release | Calibration fixture reference drift; wrong calibration recipe selected; operator setup error | Calibrated fixtures under metrology control; calibration recipe locked per station; occlusion spec per DI-007 | End-of-line occlusion alarm challenge at one flow rate; calibration record review in DHR | 3 | 2 | 3 | HAZ-006 | Add daily fixture verification against certified reference gauge; challenge occlusion alarm at low and high flow rates at end-of-line (DI-007) | Test Eng | 2026-Q3 | 3 | 1 | 2 | Open |
| FM-P-003 | Pump mechanism assembly — cam/rotor fastening | Assembly torque out of spec (under/over-torque) | Fastener loosens or cam preload incorrect | Premature drive-train wear; delivery accuracy degrades in service | Gradual under-delivery — inadequate analgesia | Torque driver out of calibration; operator skips torque step; wrong torque program | Calibrated DC electric torque drivers with per-joint programs; torque values recorded to DHR | Torque-driver OK/NOK interlock; end-of-line delivery-accuracy test (DI-001) | 3 | 2 | 3 | HAZ-006 | — | — | — | — | — | — | — |
| FM-P-004 | Air-in-line sensor assembly — acoustic coupling | Coupling gel missed or insufficiently applied | Poor acoustic coupling between transducer and tubing channel | Air-detection sensitivity below 50 µL spec on shipped unit | Missed air bolus in field — air embolism, life-threatening event | Manual gel application step skipped; wrong gel quantity; gel migration before cure | Work instruction with gel-application step; gel dispensing tooling | End-of-line single-bubble air-detection challenge (DI-008) — marginal coupling can pass a single-point challenge | 4 | 2 | 3 | HAZ-005 | Introduce metered gel dispenser with dispense-weight verification (poka-yoke); add multi-bubble sensitivity challenge at end-of-line (DI-008) | Mfg Eng | 2026-Q3 | 4 | 1 | 2 | Open |
| FM-P-005 | Firmware flashing at production | Wrong or obsolete firmware version flashed | Unit carries unvalidated or superseded code image | Device behavior diverges from released design; drug-library compatibility mismatch | Incorrect delivery behavior or exploitable outdated code — overdose potential; unauthorized-modification exposure | Wrong image selected on flashing station; release-package mix-up during changeover | Signed firmware — station rejects unsigned images (DI-024); flashing station serves only the released image per MES routing | Automated version + signature readback at final test; firmware version recorded in DHR and audit log (DI-034) | 4 | 2 | 2 | HAZ-001, HAZ-012 | — | — | — | — | — | — | — |
| FM-P-006 | Final functional test — end-of-line verification | Test skipped or passed-in-error | Unit ships without valid functional-test evidence | Defective unit (any latent defect class) reaches the field | Field failure of an unverified safety function — overdose or missed alarm | Test-station software fault; operator bypass under schedule pressure; wrong test recipe revision | Test recipes under revision control; station access control | DHR completeness review before release; no electronic interlock preventing ship of untested serials | 4 | 2 | 3 | HAZ-001, HAZ-008 | Add MES electronic interlock — serial number cannot advance to packaging without passed test record; periodic test-station challenge with known-defect golden units | Quality Eng | 2026-Q3 | 4 | 1 | 2 | Open |
| FM-P-007 | Lockbox latch assembly | Latch/strike misalignment | Latch does not fully engage or tamper evidence not armed | Cassette compartment openable without key/PIN or without visible evidence | Opioid diversion; patient receives tampered drug supply | Fixture wear shifting strike position; missing shim; over-driven fastener distorting latch frame | Assembly fixture under PM program; latch design per DI-032 | Latch engagement-force check and tamper-evidence functional check at final inspection (DI-032) | 4 | 2 | 2 | HAZ-013 | — | — | — | — | — | — | — |
| FM-P-008 | Labeling — UDI print and apply | Label/UDI misprint (wrong or unscannable UDI, illegible text) | Unit carries wrong or unreadable device identification | Traceability/recall effectiveness degraded; GUDID record mismatch | No direct patient harm; compliance and field-action-traceability impact | Printer ribbon fault; wrong label template revision; print-and-apply misfeed | Label templates under revision control; UDI content per DI-028 | In-line vision verification of print quality + UDI barcode grade scan on every unit (DI-028) | 2 | 2 | 2 | — | — | — | — | — | — | — | — |
| FM-P-009 | Packaging — administration-set pouch sealing | Seal incomplete (channel/weak seal in sterile barrier) | Pouch sterile barrier breached | Administration-set fluid path exposed to contamination before use | Infusion-site or bloodstream infection — reversible injury requiring intervention | Sealer temperature/pressure/dwell drift; wrinkled pouch material in seal area | Validated sealing process (parameters qualified per 21 CFR 820.75); sealer parameter monitoring; fluid-path material controls per DI-011 | Periodic seal peel/burst and dye-penetration sampling; visual seal inspection on every pouch | 3 | 2 | 3 | HAZ-011 | — | — | — | — | — | — | — |

**RPN consistency note:** RPN = S×O×D is used for prioritization only, per GL-STD-RM-001 §9 — final residual-risk acceptability is judged against the GL-STD-RM-001 §5 acceptance matrix (S and O used as the S,P proxy), not the RPN. Per GL-WI-RM-002 §4, D prioritizes mitigation effort and is never used to discount an unacceptable risk.

## Coverage Summary

| Metric | Value |
|---|---|
| Total failure modes | 9 |
| Modes with harm potential (end-effect S ≥ 3) | 8 |
| Modes linked to Hazard Analysis | 8 (all except FM-P-008; every S ≥ 3 mode is linked per GL-WI-RM-002 §5 step 7) |
| Unacceptable (per RM Plan criteria) — open | 0 (no (S, O) pair falls in the GL-STD-RM-001 §5 Unacceptable region) |
| Unacceptable — closed with evidence | 0 (none entered the Unacceptable region; 3 rows carry open recommended actions (RPN/detection-driven; 2 ALARP-region, 1 Acceptable-region)) |

## Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| | | | |

## Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 0.1 DRAFT | 2026-04-21 | Placeholder (task ben/023) | Stub created from QMS template. |
| 0.2 DRAFT | 2026-07-14 | BX / AI Assistant | pFMEA backfilled: 9 process failure modes across soldering, calibration, assembly, firmware flashing, test, labeling, and packaging; scored per GL-STD-RM-001; linked to GL-TMP-RM-003 hazard spine; 3 recommended actions opened. |
