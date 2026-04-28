---
source_file: "N/A — authored-in-markdown"
source_path: "design-controls/templates/phase-gate-checklist.md"
doc_id: "GL-FORM-DC-002"
doc_type: "FORM"
title: "Phase-Gate Review Checklist"
format: "md"
conversion_date: "2026-04-27"
conversion_method: "claude-authored"
conversion_fidelity: "faithful"
pages: null
sheets: null
has_images: false
image_count: 0
has_tables: true
has_form_fields: true
references:
  - doc_id: "GL-SOP-DC-005"
    title: "Design Review"
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "ISO 13485:2016 §7.3.5"
    title: "Design and development review"
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-27"
    source: "v1 — added under task ben/036 to operationalize phase-gate evidence per GL-SOP-DC-005"
notes: "Single template covering all four standard phase gates (Concept-2, 2-3, 3-4, 4-Release). Tailor by completing the Phase header + the per-phase exit criteria section."
---

# GL-FORM-DC-002 — Phase-Gate Review Checklist

_Demo sample data — not for clinical use._

**Form ID:** GL-FORM-DC-002
**Revision:** 1.0
**Effective Date:** 2026-04-27
**Owner:** VP R&D, GlobalLogic MedTech

---

## How to use

This is the canonical phase-gate evidence form. One instance is completed per phase gate per project, attached to the Design Review Record (GL-FORM-DC-001), and stored in the project DHF. The reviewer marks each line **Yes / No / N/A** with a written rationale; gate disposition (Pass / Conditional / Hold) is recorded at the end.

The same form covers all four standard gates. Complete the **Phase Header** to scope which gate this instance covers. Each gate's specific exit criteria are listed in §3 — only complete the section for the active gate.

---

## Phase Header

| Field | Value |
|---|---|
| Project / DHF | _________________________________ |
| Phase Gate | ☐ Gate 1: Concept → Feasibility · ☐ Gate 2: Feasibility → Design · ☐ Gate 3: Design → V&V · ☐ Gate 4: V&V → Transfer · ☐ Gate 5: Transfer → Release |
| Date of Review | _________________________________ |
| Lead Reviewer (Independent) | _________________________________ |
| Functional Reviewers Present | Systems · HW · FW · SW · Quality · Regulatory · Clinical · Usability · Risk · Cyber · Ops |

---

## Section 1 — Universal Pre-Gate Hygiene (every gate)

| # | Check | Y/N/NA | Rationale |
|---|---|:-:|---|
| 1.1 | Design and Development Plan (GL-TMP-DC-001) is current and approved | | |
| 1.2 | DHF index lists all artifacts produced this phase with rev / effective date | | |
| 1.3 | Action items from prior gate are closed or risk-assessed | | |
| 1.4 | Risk Management File (RMF) reflects this phase's design state | | |
| 1.5 | Open deviations (per GL-WI-QM-001) are listed with disposition |  |  |

---

## Section 2 — Universal Phase Outputs (every gate)

| # | Check | Y/N/NA | Rationale |
|---|---|:-:|---|
| 2.1 | Phase deliverables identified in the DDP have been authored | | |
| 2.2 | Each deliverable has been peer-reviewed before this gate | | |
| 2.3 | Functional leads have signed off on their sections | | |
| 2.4 | Open issues have an owner and target close date | | |

---

## Section 3 — Gate-Specific Exit Criteria

### Gate 1: Concept → Feasibility

| # | Check | Y/N/NA | Rationale |
|---|---|:-:|---|
| 3.1.1 | Intended Use, Indications for Use, and target user population are documented | | |
| 3.1.2 | User Needs register exists with at least preliminary entries | | |
| 3.1.3 | Predicate / similar-device landscape has been surveyed | | |
| 3.1.4 | Initial regulatory pathway recommendation made (510(k) / De Novo / PMA) | | |
| 3.1.5 | Top-level hazards identified at the use-case level | | |

### Gate 2: Feasibility → Design

| # | Check | Y/N/NA | Rationale |
|---|---|:-:|---|
| 3.2.1 | Design Inputs (per GL-SOP-DC-003) are baselined and approved | | |
| 3.2.2 | Each Design Input traces to ≥ 1 User Need | | |
| 3.2.3 | System Architecture (high-level) is documented | | |
| 3.2.4 | Risk Management Plan (GL-TMP-RM-001) is approved | | |
| 3.2.5 | Software Safety Class assigned per IEC 62304 §4.3 (if SaMD/SiMD) | | |
| 3.2.6 | Cybersecurity scope and threat model started (per GL-WI-SW-003, if cyber-relevant) | | |

### Gate 3: Design → V&V

| # | Check | Y/N/NA | Rationale |
|---|---|:-:|---|
| 3.3.1 | Design Outputs (per GL-SOP-DC-004) baselined; SAD and software/hardware specs approved | | |
| 3.3.2 | Trace matrix complete: UN ↔ DI ↔ DO (per GL-WI-DC-002) | | |
| 3.3.3 | Hazard Analysis (GL-WI-RM-001) and FMEAs (GL-WI-RM-002) complete; risk controls allocated | | |
| 3.3.4 | V&V protocols (GL-TMP-DC-003 / -004) drafted and reviewed | | |
| 3.3.5 | Usability formative evaluations complete (per GL-SOP-UC-001) | | |
| 3.3.6 | SBOM baseline produced (per GL-WI-SW-002) | | |

### Gate 4: V&V → Transfer

| # | Check | Y/N/NA | Rationale |
|---|---|:-:|---|
| 3.4.1 | Verification protocol executed; report shows all DIs verified | | |
| 3.4.2 | Validation protocol executed in intended-use environment with representative users | | |
| 3.4.3 | Summative usability evaluation passed (per GL-TMP-UC-003, if user interfaces) | | |
| 3.4.4 | Risk Management Report (GL-TMP-RM-002) signed off; benefit-risk acceptable | | |
| 3.4.5 | Cybersecurity testing complete (penetration test, SBOM CVE scan) | | |
| 3.4.6 | Clinical Evaluation Report (GL-TMP-UC-005) issued (if MDR market) | | |

### Gate 5: Transfer → Release

| # | Check | Y/N/NA | Rationale |
|---|---|:-:|---|
| 3.5.1 | Design Transfer evidence complete (DMR / Medical Device File) | | |
| 3.5.2 | Production process validated (per GL-SOP-SP-003) | | |
| 3.5.3 | Suppliers qualified (per GL-SOP-SP-001) | | |
| 3.5.4 | Labeling, IFU, UDI finalized | | |
| 3.5.5 | Regulatory submission cleared (or Letter to File completed for non-significant changes) | | |
| 3.5.6 | PMS Plan (GL-TMP-PM-001) issued; field surveillance pathway active | | |

---

## Disposition

| Field | Value |
|---|---|
| Outcome | ☐ Pass · ☐ Conditional · ☐ Hold |
| Conditions / Actions Required (if Conditional) | _________________________________ |
| Action Owner / Due Date | _________________________________ |
| Re-Review Required by Date | _________________________________ |

## Sign-Off

| Role | Name | Signature | Date |
|---|---|---|---|
| Lead Reviewer (Independent) | | | |
| Project Manager / Design Owner | | | |
| Quality Representative | | | |
| Regulatory Representative | | | |

---

## Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-27 | Ben Xavier (via Claude, task ben/036) | Initial release. Single form covering all five standard phase gates. |
