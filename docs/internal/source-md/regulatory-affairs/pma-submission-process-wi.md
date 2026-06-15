---
source_file: "N/A — authored-in-markdown"
source_path: "regulatory-affairs/pma-submission-process-wi.md"
doc_id: "GL-WI-RA-003"
doc_type: "WI"
title: "PMA Submission Process"
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
  - doc_id: "21 CFR Part 814 Subpart B"
    title: "Premarket approval application content and format"
    resolved: true
    match: null
    note: "Primary anchor (§ 814.20)"
  - doc_id: "FDA Acceptance and Filing Review for PMAs"
    title: "PMA filing-review checklist guidance"
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
    note: "Sibling pathway WI — shared pre-assembly + sign-off pattern"
conversion_history:
  - date: "2026-06-15"
    source: "v1 — added under task ben/089 to fill the PMA-pathway gap GL-WI-RA-001 §2 deferred ('PMA — GL-WI-RA-003 when authored')"
notes: "Step-by-step process for assembling, filing, and tracking a Premarket Approval (PMA) application per 21 CFR Part 814. Demo/representative QMS content."
---

# GL-WI-RA-003 — PMA Submission Process

_Demo sample data — not for clinical use._

**Document ID:** GL-WI-RA-003
**Revision:** 1.0
**Effective Date:** 2026-06-15
**Owner:** Regulatory Affairs Lead, GlobalLogic MedTech

---

## 1. Purpose

Provide the step-by-step process for assembling, filing, and tracking a **Premarket Approval (PMA)** application per 21 CFR Part 814. Operationalizes the PMA pathway under GL-SOP-RA-001. A PMA is required for Class III devices that cannot establish substantial equivalence to a predicate (no 510(k) path); unlike a 510(k), it must independently demonstrate, with valid scientific evidence, a **reasonable assurance of safety and effectiveness**.

## 2. Scope

Applies to every GlobalLogic device pursuing PMA approval, including PMA supplements (§ 814.39) for approved devices. Out of scope: 510(k) (use GL-WI-RA-001), De Novo (GL-WI-RA-002 when authored), Humanitarian Device Exemption (HDE, Subpart H — a future WI when a humanitarian-use program arises), and EU MDR submissions.

## 3. Definitions

- **PMA** — Premarket Approval application under section 515 of the FD&C Act / 21 CFR Part 814; the most stringent device-marketing pathway.
- **Valid scientific evidence** — the evidentiary standard for a PMA (well-controlled investigations, partially controlled studies, etc.) supporting reasonable assurance of safety and effectiveness.
- **SSED** — Summary of Safety and Effectiveness Data; the public benefit-risk summary FDA publishes on PMA approval (the PMA analogue of the § 807.92 510(k) summary). Built from the § 814.20(b)(3) summary content.
- **PMA supplement** — the mechanism (§ 814.39) for a change to an approved PMA device that affects safety or effectiveness (the PMA analogue of a new 510(k) for a significant change).
- **Filing review** — FDA's threshold acceptance check (the PMA analogue of the 510(k) RTA review); a PMA must be *filed* before substantive review begins.
- **Panel review** — FDA may refer a PMA to an advisory committee (panel) for a public recommendation.

## 4. Pre-Assembly Requirements

The following shall be in place **before** PMA assembly begins:

| Requirement | Source |
|---|---|
| Approved Regulatory Strategy citing the PMA pathway (and why 510(k)/De Novo are not viable) | GL-SOP-RA-001 §5.1 |
| Pivotal clinical investigation complete under an approved IDE (21 CFR 812), data locked | GL-SOP-UC-001 + clinical protocol |
| DHF artifacts at design-transfer baseline (per GL-FORM-DC-002) | GL-WI-DC-001 §8 |
| V&V complete for all design inputs traced through GL-WI-DC-002 | GL-SOP-DC-006 + GL-WI-DC-002 |
| Risk Management File approved (RMR signed); benefit-risk determination drafted | GL-SOP-RM-001 |
| Manufacturing information ready for the § 814.20(b)(4) section; QMS in a PMA-pre-approval-inspection-ready state | GL-SOP-SP-* + GL-SOP-QM-001 |
| Cybersecurity / software / usability documentation per applicable FDA guidance | GL-SOP-SW-001 / SW-004 / UC-001 |
| Proposed labeling final (IFU, package label, UDI) | GL-SOP-PM-001 + (labeling SOP) |

If any of the above is incomplete, do not start PMA assembly — escalate to RA Lead. A PMA failing the § 814.42 filing review consumes a full review cycle.

## 5. Procedure

### 5.1 Application Structure (§ 814.20)

Assemble the PMA in the order specified by § 814.20(b) — see the distilled component map in `.claude/skills/medtech-docs/references/regulations/21-cfr-part-814.md` (§ 814.20(b)(1)–(13)). The load-bearing sections:

| § 814.20 component | Content |
|---|---|
| (b)(2) | Table of contents; separate nonclinical-studies and clinical-investigations sections |
| (b)(3) | **Summary** — indications, device description, alternative practices, marketing history, study summaries, **benefit-risk conclusions** (this content feeds the SSED) |
| (b)(4) | **Complete device description** — components, principles of operation, manufacturing & QC methods |
| (b)(5) | Applicable performance standards — compliance or justified deviations |
| (b)(6) | **Technical sections** — nonclinical lab studies (b)(6)(i) + clinical investigations (b)(6)(ii) |
| (b)(8) | Bibliography of safety/effectiveness reports |
| (b)(10) | All proposed labeling |
| (b)(11) | Environmental assessment (or exclusion) |
| (b)(12) | Financial certification/disclosure (Part 54) |
| (b)(13) | Pediatric subpopulation information if available |

### 5.2 Clinical Evidence & Benefit-Risk

Author the clinical-evidence narrative: study design, endpoints, statistical analysis plan and results, adverse events, and the benefit-risk determination supporting reasonable assurance of safety and effectiveness. Ground the benefit-risk framing in the approved Risk Management File. Never fabricate or selectively report clinical data.

### 5.3 Manufacturing & Pre-Approval Inspection Readiness

The § 814.20(b)(4) manufacturing section must reflect the as-built QMS. A PMA approval is gated on a satisfactory **pre-approval inspection (PAI)** of the manufacturing facility — coordinate PAI readiness with Quality before filing.

### 5.4 Internal Review and Sign-Off

Before filing (consistent with the GL-WI-RA-001 §5.4 chain, with a clinical add):

1. **RA Specialist** reviews the PMA for completeness against § 814.20(b).
2. **RA Lead** reviews for accuracy and benefit-risk-argument quality.
3. **Clinical / Biostatistics** signs off that the clinical evidence and statistical analysis are correctly represented.
4. **Quality** signs off that the cited DHF revisions match the DHF Index and that manufacturing is PAI-ready.
5. **VP Regulatory Affairs** approves the PMA for filing.

### 5.5 Filing & Transmittal

Submit via the FDA electronic submission mechanism (eSTAR/eCopy per current PMA mechanics). Capture the PMA number, date/time of transmission, and confirmation. Log in the Regulatory Communications Register (GL-SOP-RA-001 §5.2). FDA conducts a **filing review** (§ 814.42); a refuse-to-file requires correction and re-submission.

### 5.6 Review Tracking

| Event | Action |
|---|---|
| Filing review (§ 814.42) | If refuse-to-file — correct and re-submit |
| Substantive review | Respond promptly to FDA deficiency letters; the review clock pauses pending responses |
| Advisory panel (if convened) | Prepare panel package + presentation; capture panel recommendations |
| Pre-approval inspection | Support the facility inspection; close any findings |
| Decision (§ 814.44) | Approval order / approvable letter / not-approvable letter / denial (§ 814.45) |

PMA review timeframes are substantially longer than 510(k) — track status against the MDUFA PMA goals, not a 90-day clock.

### 5.7 Post-Approval Activities

On approval (§ 814.44 + Subpart E):

1. Comply with all **conditions of approval** (§ 814.82) — e.g., postapproval studies, labeling restrictions.
2. File periodic (annual) reports and adverse-effect reports (§ 814.84).
3. Manage device changes through **PMA supplements** (§ 814.39) — not Letters-to-File.
4. The published **SSED** becomes part of the public record; archive it in the regulatory file.

On not-approvable / denial: escalate to VP RA + VP Quality; decide on additional studies, amendment, or program discontinuation; document in the regulatory strategy memo.

## 6. Common Failure Modes

| Pattern | Why it fails |
|---|---|
| PMA filed before the pivotal clinical data are locked and analyzed | Filing review or early deficiency; consumes a full review cycle |
| Manufacturing section not PAI-ready | Approval gated on a satisfactory pre-approval inspection; an unprepared facility blocks approval after a successful scientific review |
| Benefit-risk conclusion not traceable to the Risk Management File | The § 814.20(b)(3)(vi) conclusion is unsupported; deficiency letter |
| Treating a post-approval change as a Letter-to-File | PMA changes affecting safety/effectiveness require a § 814.39 supplement, not the 510(k)-style change machinery |
| Pursuing PMA when a De Novo or 510(k) path exists | PMA is the most resource-intensive path; pathway selection error is costly |

## 7. Cross-References

- GL-SOP-RA-001 — Regulatory Operations (parent SOP)
- GL-WI-RA-001 — 510(k) Submission Process (sibling pathway WI)
- GL-WI-DC-001 — DHF Process (artifact freeze for submission)
- GL-WI-DC-002 — Design Traceability Matrix (V&V trace cited in submissions)
- GL-SOP-RM-001 — Risk Management (benefit-risk determination)
- GL-SOP-UC-001 — Usability Engineering / clinical evaluation
- GL-SOP-SW-001 / SW-004 — Software lifecycle / cybersecurity
- 21 CFR Part 814 — Premarket Approval (and the distillation at `.claude/skills/medtech-docs/references/regulations/21-cfr-part-814.md`)
- 21 CFR Part 812 — Investigational Device Exemptions (IDE for the pivotal study)
- FDA Acceptance and Filing Review for PMAs guidance

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-06-15 | Ben Xavier (via Claude, task ben/089) | Initial release. PMA pathway WI — fills the GL-WI-RA-001 §2 deferral ("PMA — GL-WI-RA-003 when authored"). |
