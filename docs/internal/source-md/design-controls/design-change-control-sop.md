---
source_file: "N/A — authored-in-markdown"
source_path: "design-controls/design-change-control-sop.md"
doc_id: "GL-SOP-DC-008"
doc_type: "SOP"
title: "Design Change Control"
format: "md"
conversion_date: "2026-04-21"
conversion_method: "claude-authored"
conversion_fidelity: "faithful"
pages: null
sheets: null
has_images: false
image_count: 0
has_tables: true
has_form_fields: false
references:
  - doc_id: "ISO 13485:2016 §7.3.9"
    title: "Control of design and development changes"
    resolved: true
    match: null
    note: null
  - doc_id: "21 CFR 820.30(i)"
    title: "Design changes"
    resolved: true
    match: null
    note: null
  - doc_id: "FDA — Deciding When to Submit a 510(k) for a Change to an Existing Device (2017)"
    title: null
    resolved: true
    match: null
    note: "Applied for regulatory-notification decision"
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-DC-008 — Design Change Control

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-DC-008
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** VP R&D, GlobalLogic MedTech

---

## 1. Purpose

Control changes to a design throughout the product lifecycle — before and after Design Transfer — per ISO 13485:2016 §7.3.9 and 21 CFR 820.30(i).

## 2. Scope

All proposed changes to Design Inputs, Design Outputs, released DMR items, or the Risk Management File for products covered by the GlobalLogic QMS.

## 3. Responsibilities

- **Change Initiator** — author of Engineering Change Order (ECO)
- **Design Owner** — technical assessment
- **Risk Management** — re-assess risks
- **Regulatory Affairs** — determine regulatory notification / new submission needs (see §6.4)
- **Quality Engineering** — process and approval compliance
- **Manufacturing / Supplier Quality** — production impact and supplier notifications

## 4. Definitions

- **ECO (Engineering Change Order)** — The primary record for a design change.
- **Significant change** — A change that could significantly affect safety or effectiveness of a device (drives 510(k) submission decision per FDA 2017 guidance; Article 120 considerations under EU MDR).

## 5. References

- ISO 13485:2016 §7.3.9
- 21 CFR 820.30(i), §820.70(b), §820.100
- FDA — "Deciding When to Submit a 510(k) for a Change to an Existing Device" (2017)
- FDA — "Deciding When to Submit a 510(k) for a Software Change to an Existing Device" (2017)
- EU MDR 2017/745 Art. 120; Annex IX §2.4

## 6. Procedure

### 6.1 Change Initiation

Any employee or supplier may propose a change via an **ECO** (record form — GL-FORM-DC-002, _forthcoming in follow-on task_; for this demo, ECOs may be processed via a Design Review Record with Change Control subject). The ECO states:

- What is changing (current vs. proposed)
- Reason (customer feedback, CAPA, obsolescence, improvement, regulatory)
- Affected Design Inputs / Outputs / DMR items / RMF entries / Trace Matrix entries
- Build / SN / lot boundary

### 6.2 Impact Assessment

Cross-functional assessment:

| Area | Assessment |
|---|---|
| Safety / Risk | Re-run relevant risk analysis (GL-SOP-RM-001); update RMF |
| Verification / Validation | Determine re-verification / re-validation scope |
| Usability | Determine whether summative re-evaluation is needed (GL-SOP-UC-001) |
| Software | Determine whether re-integration / re-regression testing is needed (GL-SOP-SW-001) |
| Cybersecurity | Re-analyze threat model / SBOM impact (GL-SOP-SW-004, GL-SOP-SW-005) |
| Labeling / IFU | Determine if updates are required |
| Supplier | Notify suppliers for DMR-affecting changes |
| Production | Process re-qualification required? |

### 6.3 Review and Approval

ECOs are reviewed at a formal Design Review (GL-SOP-DC-005) — the ECO is the subject. Approval authorities are the same as the original approval authority for the affected documents (Document Control — GL-SOP-QM-001).

### 6.4 Regulatory Notification / Submission

Regulatory Affairs runs the "**significance assessment**":

- **US (FDA)** — Apply FDA "Deciding When to Submit a 510(k) for a Change" (2017) flowchart; and the software-change guidance where applicable. Document the decision (new 510(k), Special 510(k), letter-to-file).
- **EU (MDR)** — Per Annex IX §2.4 and Art. 120, determine whether a substantial change requires notified-body involvement.
- **Other markets** — Per the product's regulatory matrix.

Decision and rationale are captured with the ECO.

### 6.5 Implementation

Upon approval, affected documents enter Document Change Control (GL-SOP-QM-001). Effectivity defines the boundary (SN, lot, build). Training is conducted as required before effectivity (GL-SOP-QM-003).

### 6.6 Verification of Effectiveness

For changes driven by CAPA (GL-SOP-QM-005) or PMS signals (GL-SOP-PM-001), effectiveness monitoring is defined in the ECO and tracked through CAPA closure.

## 7. Records Generated

| Record | Retained by | Retention |
|---|---|---|
| ECO (each change) | DHF | Per GL-SOP-QM-001 |
| Regulatory-significance decision | DHF + RA file | Per GL-SOP-QM-001 |
| Post-change V&V records | DHF | Per GL-SOP-QM-001 |

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
