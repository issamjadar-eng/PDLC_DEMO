---
source_file: "N/A — authored-in-markdown"
source_path: "regulatory-affairs/de-novo-submission-process-wi.md"
doc_id: "GL-WI-RA-002"
doc_type: "WI"
title: "De Novo Submission Process"
format: "md"
conversion_date: "2026-06-15"
conversion_method: "claude-authored"
conversion_fidelity: "faithful"
pages: null
sheets: null
has_images: false
image_count: 0
has_tables: true
has_form_fields: false
references:
  - doc_id: "21 CFR Part 860 Subpart D"
    title: "De Novo classification process"
    resolved: true
    match: null
    note: "Primary anchor (FD&C Act § 513(f)(2))"
  - doc_id: "FDA De Novo Classification Process guidance"
    title: "Evaluation of automatic class III designation"
    resolved: true
    match: null
    note: null
  - doc_id: "GL-SOP-RA-001"
    title: "Regulatory Operations"
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "GL-WI-RA-001"
    title: "510(k) Submission Process"
    resolved: true
    match: null
    note: "Sibling pathway WI — De Novo often follows an NSE 510(k)"
conversion_history:
  - date: "2026-06-15"
    source: "v1 — added under task ben/090 to complete the RA pathway set (GL-WI-RA-001 §2 / GL-WI-RA-003 §2 named GL-WI-RA-002 as reserved)"
notes: "Step-by-step process for a De Novo classification request per FD&C Act § 513(f)(2) / 21 CFR Part 860 Subpart D. Demo/representative QMS content."
---

# GL-WI-RA-002 — De Novo Submission Process

_Demo sample data — not for clinical use._

**Document ID:** GL-WI-RA-002
**Revision:** 1.0
**Effective Date:** 2026-06-15
**Owner:** Regulatory Affairs Lead, GlobalLogic MedTech

---

## 1. Purpose

Provide the step-by-step process for a **De Novo classification request** under FD&C Act § 513(f)(2) / 21 CFR Part 860 Subpart D. Operationalizes the De Novo pathway under GL-SOP-RA-001. De Novo is for a **novel device with no legal predicate** that is nonetheless **low-to-moderate risk**, where general controls (or general + special controls) provide a reasonable assurance of safety and effectiveness — avoiding the automatic Class III designation that would otherwise force a PMA.

## 2. Scope

Applies to every GlobalLogic device pursuing De Novo classification — whether filed directly or after a Not-Substantially-Equivalent (NSE) 510(k) decision. Out of scope: 510(k) (use GL-WI-RA-001), PMA (GL-WI-RA-003), HDE, and EU MDR submissions. A successful De Novo grant **creates a new classification** and the device may then serve as a predicate for subsequent 510(k)s.

## 3. Definitions

- **De Novo request** — a request for classification of a novel device into Class I or Class II under FD&C § 513(f)(2), when no legally marketed predicate exists.
- **Automatic Class III designation** — by statute, a device with no predicate defaults to Class III (PMA); the De Novo process is the mechanism to reclassify it down to I/II when the risk profile supports it.
- **Special controls** — Class II controls (performance standards, labeling, postmarket surveillance, etc.) that, with general controls, provide reasonable assurance of safety and effectiveness. A De Novo grant typically **establishes** the special controls for the new device type.
- **NSE → De Novo** — a 510(k) that receives an NSE decision may pivot to De Novo (often the predicate-less reason for the NSE is itself the De Novo basis).

## 4. Pre-Assembly Requirements

The following shall be in place **before** De Novo assembly begins:

| Requirement | Source |
|---|---|
| Approved Regulatory Strategy citing the De Novo pathway (and confirming no usable predicate exists / NSE received) | GL-SOP-RA-001 §5.1 |
| Risk analysis identifying the probable risks/benefits and supporting low-to-moderate-risk classification | GL-SOP-RM-001 |
| DHF artifacts at design-transfer baseline (per GL-FORM-DC-002) | GL-WI-DC-001 §8 |
| V&V complete for all design inputs traced through GL-WI-DC-002 | GL-SOP-DC-006 + GL-WI-DC-002 |
| Draft **proposed special controls** for the new device type | RA + R&D + Risk |
| Software / cybersecurity / usability documentation per applicable FDA guidance | GL-SOP-SW-001 / SW-004 / UC-001 |
| Proposed labeling final (IFU, package label, UDI) | GL-SOP-PM-001 + (labeling SOP) |

If any of the above is incomplete, do not start assembly — escalate to RA Lead.

## 5. Procedure

### 5.1 Classification Recommendation

Author the **classification recommendation**: the proposed class (I or II), the device type / generic name, the identified probable risks to health and probable benefits, and — for Class II — the **proposed special controls** that mitigate each identified risk. This risk-to-control mapping is the spine of a De Novo and should trace to the Risk Management File.

### 5.2 Supporting Evidence

Assemble the evidence that the proposed general (and special) controls provide a reasonable assurance of safety and effectiveness for the intended use: bench/nonclinical data, and clinical data where the risk profile requires it. De Novo evidence is calibrated to the *risk*, not to a predicate comparison (there is none).

### 5.3 De Novo Request Assembly (eSTAR)

Assemble the request in the FDA De Novo eSTAR. Typical sections (refer to the current FDA template for the authoritative list):

| Section | Content |
|---|---|
| Cover Letter | Submission type (De Novo), contact, prior 510(k) number if NSE-pivot |
| Administrative | Applicant, device name, requested classification |
| Device Description | Function, components, principles of operation |
| Classification Summary | Proposed class + device type + probable risks/benefits |
| Proposed Special Controls | The Class II controls mitigating each identified risk |
| Indications for Use | Final IFU statement |
| Performance Data | Bench / animal / clinical as warranted by risk |
| Software / Cybersecurity / Biocompatibility / Usability | As applicable |
| Labeling | Final IFU + package label PDFs (DHF-derived) |

Each attached document is a **PDF derived from the controlled DHF artifact**; the cited revision must match the DHF Index.

### 5.4 Internal Review and Sign-Off

Before transmittal (consistent with the GL-WI-RA-001 §5.4 chain):

1. **RA Specialist** reviews for completeness.
2. **RA Lead** reviews for accuracy and the risk→special-control mapping quality.
3. **Quality** signs off that the cited DHF revisions match the DHF Index.
4. **VP Regulatory Affairs** signs off on submission.

### 5.5 Transmittal & Tracking

Transmit via the De Novo eSTAR to FDA's CDRH portal; capture the De Novo request number, date/time, and confirmation; log in the Regulatory Communications Register (GL-SOP-RA-001 §5.2).

| Event | Action |
|---|---|
| Acceptance review | If refuse-to-accept — correct and re-submit |
| Substantive review | Respond promptly to FDA deficiency / Additional Information requests; clock pauses pending response |
| Decision | **Grant** (device classified into I/II; classification order + special controls published; device becomes a potential predicate) or **Decline** (device remains Class III → PMA or discontinuation) |

De Novo MDUFA timeframes are longer than a 510(k); track status until decision.

### 5.6 Post-Decision Activities

On grant: update establishment registration/device listing; the granted classification + special controls are published and establish the new device type; activate post-market surveillance (GL-SOP-PM-001); a future device of the same type may now use a 510(k) against this device as predicate.

On decline: escalate to VP RA + VP Quality; decide PMA path or discontinuation; document in the regulatory strategy memo.

## 6. Common Failure Modes

| Pattern | Why it fails |
|---|---|
| Filing De Novo when a usable predicate actually exists | A 510(k) is the correct (faster) path; FDA may redirect |
| Proposed special controls don't map 1:1 to identified risks | The core De Novo argument is incomplete; deficiency letter |
| Risk profile actually high-risk | De Novo is only for low-to-moderate risk; a high-risk device belongs in PMA |
| Evidence calibrated to a (non-existent) predicate instead of to the risk | De Novo is risk-based, not SE-based — the framing must be reasonable-assurance, not equivalence |

## 7. Cross-References

- GL-SOP-RA-001 — Regulatory Operations (parent SOP)
- GL-WI-RA-001 — 510(k) Submission Process (NSE → De Novo pivot)
- GL-WI-RA-003 — PMA Submission Process (the alternative when risk is too high for De Novo)
- GL-WI-DC-001 — DHF Process; GL-WI-DC-002 — Design Traceability Matrix
- GL-SOP-RM-001 — Risk Management (the risk→special-control mapping)
- 21 CFR Part 860 Subpart D — De Novo classification process; FD&C Act § 513(f)(2)
- FDA De Novo Classification Process guidance

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-06-15 | Ben Xavier (via Claude, task ben/090) | Initial release. De Novo pathway WI — completes the RA pathway set (was reserved in GL-WI-RA-001/-003 §2). |
