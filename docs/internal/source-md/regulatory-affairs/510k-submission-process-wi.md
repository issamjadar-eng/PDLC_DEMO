---
source_file: "N/A — authored-in-markdown"
source_path: "regulatory-affairs/510k-submission-process-wi.md"
doc_id: "GL-WI-RA-001"
doc_type: "WI"
title: "510(k) Submission Process"
format: "md"
conversion_date: "2026-04-27"
conversion_method: "claude-authored"
conversion_fidelity: "faithful"
pages: null
sheets: null
has_images: false
image_count: 0
has_tables: true
has_form_fields: false
references:
  - doc_id: "21 CFR 807 Subpart E"
    title: "Premarket notification procedures"
    resolved: true
    match: null
    note: "Primary anchor"
  - doc_id: "FDA Format for Traditional and Abbreviated 510(k)s (2019)"
    title: "Submission format guidance"
    resolved: true
    match: null
    note: null
  - doc_id: "FDA 510(k) Program: Evaluating Substantial Equivalence (2014)"
    title: "Substantial-equivalence framework"
    resolved: true
    match: null
    note: null
  - doc_id: "FDA Deciding When to Submit a 510(k) for a Change to an Existing Device (2017)"
    title: "Change-significance flowcharts"
    resolved: true
    match: null
    note: null
  - doc_id: "GL-SOP-RA-001"
    title: "Regulatory Operations"
    resolved: true
    match: null
    note: "Parent SOP"
conversion_history:
  - date: "2026-04-27"
    source: "v1 — added under task ben/036 as the first pathway-specific WI in the new Regulatory Affairs category"
notes: "Step-by-step process for assembling, transmitting, and tracking a Traditional or Abbreviated 510(k) — including eSTAR mechanics, predicate analysis, and substantial-equivalence argumentation."
---

# GL-WI-RA-001 — 510(k) Submission Process

_Demo sample data — not for clinical use._

**Document ID:** GL-WI-RA-001
**Revision:** 1.0
**Effective Date:** 2026-04-27
**Owner:** Regulatory Affairs Lead, GlobalLogic MedTech

---

## 1. Purpose

Provide the step-by-step process for assembling, transmitting, and tracking a Traditional or Abbreviated 510(k) Premarket Notification per 21 CFR 807 Subpart E and FDA's 2019 Format guidance. Operationalizes the 510(k) pathway under GL-SOP-RA-001.

## 2. Scope

Applies to every GlobalLogic device pursuing a 510(k) clearance — Traditional, Abbreviated, or Special. Out of scope: De Novo (use GL-WI-RA-002 when authored), PMA (GL-WI-RA-003 when authored), and EU MDR submissions.

## 3. Definitions

- **Substantial Equivalence (SE)** — the device has the same intended use as a legally marketed predicate AND the same technological characteristics, OR has different technological characteristics but does not raise different questions of safety / effectiveness.
- **Predicate** — a legally marketed device used as the basis for the SE comparison.
- **Reference device** — a different cleared device that supports the SE argument for performance characteristics not present in the primary predicate.
- **eSTAR** — FDA's electronic submission template; mandatory for 510(k) since October 2023.
- **AI Hold** — initial agency review may be paused for additional information; clock pauses during AI Hold.

## 4. Pre-Assembly Requirements

The following shall be in place **before** submission assembly begins:

| Requirement | Source |
|---|---|
| Approved Regulatory Strategy citing 510(k) pathway and primary predicate | GL-SOP-RA-001 §5.1 |
| DHF artifacts at Gate 4 baseline (per GL-FORM-DC-002) | GL-WI-DC-001 §8 |
| V&V complete for all DIs traced through GL-WI-DC-002 | GL-SOP-DC-006 + GL-WI-DC-002 |
| Risk Management File approved (RMR signed) | GL-SOP-RM-001 |
| Cybersecurity documentation per FDA 2023 guidance (if applicable) | GL-SOP-SW-004 + GL-WI-SW-003 |
| Software documentation per FDA software guidance | GL-SOP-SW-001 |
| Usability validation per FDA HFE/UE 2016 guidance (if user interfaces) | GL-SOP-UC-001 |
| Labeling final (IFU, package label, UDI) | GL-SOP-PM-001 + (TBD labeling SOP) |
| If AI/ML-enabled and pursuing PCCP: cleared PCCP scope draft | GL-SOP-RA-001 §5.1 |

If any of the above is incomplete, do not start eSTAR assembly — escalate to RA Lead.

## 5. Procedure

### 5.1 Predicate Analysis

Produce a **Predicate Comparison Table** showing intended use and technological characteristics of:

- The subject device
- The primary predicate
- (If used) reference devices for performance claims not in the primary predicate

Each row of the table is one characteristic with **same / different** marked. For each "different" row, provide a justification that the difference does not raise different questions of safety / effectiveness — citing performance testing where the difference is bridged by data.

### 5.2 Substantial Equivalence Argument

Author the SE narrative covering:

1. Intended use comparison (subject vs predicate)
2. Indications for use (must be the same general use; specific differences require justification)
3. Technological characteristics — same / different framework
4. Performance testing summary — bench, animal, clinical (as applicable)
5. Conclusion that the subject device is substantially equivalent

For Abbreviated 510(k)s: cite the FDA-recognized consensus standards used and the special controls (if applicable to the device type) in lieu of full performance summaries.

### 5.3 eSTAR Assembly

The eSTAR template (FDA-provided PDF form) is the canonical container. Required sections (typical Traditional 510(k); refer to current FDA template for the authoritative list):

| Section | Content |
|---|---|
| Cover Sheet | Submission type, contact, fee category |
| Indications for Use | Final IFU statement |
| 510(k) Summary or Statement | Summary becomes public on FDA database |
| Standards | List of FDA-recognized consensus standards used |
| Software | If applicable — Documentation Level (Basic / Enhanced), full software docs per Documentation Level |
| Cybersecurity | If applicable — threat model, SBOM, risk assessment, testing |
| Biocompatibility | If applicable — ISO 10993 evaluation |
| Sterilization | If applicable — VDmax / overkill / parametric release validation |
| Performance — Bench | Test reports |
| Performance — Animal | If applicable |
| Performance — Clinical | If applicable |
| Substantial Equivalence Discussion | The SE narrative from §5.2 |
| Labeling | Final IFU + package label PDFs |

Each attached document is a **PDF derived from the controlled DHF artifact**. Do not attach working drafts; the cited revision must match the DHF Index.

### 5.4 Internal Review and Sign-Off

Before transmittal:

1. **RA Specialist** reviews the eSTAR for completeness.
2. **RA Lead** reviews for accuracy and SE-argument quality.
3. **Quality** signs off that the cited DHF revisions match the DHF Index.
4. **VP Regulatory Affairs** signs off on submission.

### 5.5 Transmittal

Transmit via eSTAR to FDA's CDRH portal. Capture:

- Submission ID assigned by FDA
- Date / time of transmission
- Confirmation receipt

Log in the Regulatory Communications Register (per GL-SOP-RA-001 §5.2).

### 5.6 Post-Submission Tracking

| Event | Standard cadence | Action |
|---|---|---|
| Acceptance Review | ~7 calendar days | If RTA letter — revise per RTA, re-submit |
| Substantive Review | ~60 calendar days | RA monitors; ensure prompt response if AI Hold issued |
| Additional Information (AI) Hold | Variable | Clock pauses; respond per request, re-start clock |
| Decision | Target 90 FDA days from acceptance | Clearance letter or NSE letter |

**MDUFA timeframes are targets, not deadlines** — actual review duration varies. RA tracks submission status weekly until decision.

### 5.7 Post-Clearance Activities

On clearance:

1. Update establishment registration / device listing per 21 CFR Part 807.
2. Add device to the Device Master Record / Medical Device File.
3. Activate post-market surveillance per GL-SOP-PM-001.
4. If a PCCP is part of the clearance: begin tracking the change activities permitted under the PCCP scope.
5. File 510(k) Summary in the regulatory archive (it becomes public on FDA's 510(k) database).

On NSE (Not Substantially Equivalent):

1. Escalate to VP RA + VP Quality.
2. Decide: De Novo path, PMA path, or device discontinuation.
3. Document the decision in the program's regulatory strategy memo.

## 6. Common Failure Modes

| Pattern | Why it fails |
|---|---|
| Predicate selected without considering intended-use match | SE argument collapses on intended-use mismatch — the most-cited NSE reason |
| eSTAR cites a working-draft DHF artifact | Inconsistency surfaces in agency review; eats AI Hold cycles |
| Cybersecurity documentation present but threat model missing | FDA 2023 guidance specifically calls out threat model as a required pre-market deliverable |
| Software documentation level mismatched to safety class | Documentation Level (Basic vs Enhanced) drives breadth; mismatched submissions get AI Hold |
| Labeling claims exceed cleared indications | Triggers post-clearance enforcement; correctable but visible |

## 7. Cross-References

- GL-SOP-RA-001 — Regulatory Operations (parent SOP)
- GL-SOP-DC-001 — Design Control (Master)
- GL-SOP-DC-008 — Design Change Control (post-clearance changes)
- GL-WI-DC-001 — DHF Process (artifact freeze for submission)
- GL-WI-DC-002 — Design Traceability Matrix (V&V trace cited in submissions)
- GL-SOP-RM-001 — Risk Management
- GL-SOP-SW-001 — Software Lifecycle (software documentation)
- GL-SOP-SW-004 — Cybersecurity (cybersecurity documentation per FDA 2023)
- GL-WI-SW-002 — SBOM (cybersecurity package)
- GL-WI-SW-003 — Threat Modeling (cybersecurity package)
- GL-SOP-UC-001 — Usability Engineering (HFE for user-interface devices)
- 21 CFR 807 Subpart E
- FDA Format for Traditional and Abbreviated 510(k)s (2019)
- FDA 510(k) Program: Evaluating Substantial Equivalence (2014)
- FDA Cybersecurity in Medical Devices (2023)
- FDA Deciding When to Submit a 510(k) for a Change (2017)

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-27 | Ben Xavier (via Claude, task ben/036) | Initial release. Pathway WI for Traditional / Abbreviated 510(k) submissions. |
