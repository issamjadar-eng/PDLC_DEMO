---
source_file: "N/A — authored-in-markdown"
source_path: "design-controls/design-history-file-process-wi.md"
doc_id: "GL-WI-DC-001"
doc_type: "WI"
title: "Design History File Process"
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
  - doc_id: "ISO 13485:2016 §7.3.10"
    title: "Design and development files"
    resolved: true
    match: null
    note: "Primary anchor"
  - doc_id: "21 CFR 820.30(j)"
    title: "Design history file"
    resolved: true
    match: null
    note: null
  - doc_id: "GL-SOP-DC-001"
    title: "Design Control (Master)"
    resolved: true
    match: null
    note: "Parent SOP"
conversion_history:
  - date: "2026-04-27"
    source: "v1 — added under task ben/036 to operationalize DHF assembly that GL-SOP-DC-001 references at high level"
notes: "Concrete WI for DHF assembly: index, naming, traceability, freeze, transfer to records archive."
---

# GL-WI-DC-001 — Design History File Process

_Demo sample data — not for clinical use._

**Document ID:** GL-WI-DC-001
**Revision:** 1.0
**Effective Date:** 2026-04-27
**Owner:** VP R&D, GlobalLogic MedTech

---

## 1. Purpose

Provide concrete, executable mechanics for assembling, maintaining, and archiving the **Design History File (DHF)** for each device program. Operationalizes GL-SOP-DC-001 §6 — which establishes that a DHF exists per program but does not specify how to build one.

## 2. Scope

Applies to every project producing a controlled medical device design under the GlobalLogic QMS. One DHF per device per regulatory pathway (e.g., one DHF for a device cleared under one 510(k); separate DHFs if the same physical device is filed under multiple regulatory pathways).

## 3. DHF Contents (ISO 13485 §7.3.10 + 21 CFR 820.30(j))

A complete DHF demonstrates that the design was developed in accordance with the approved Design and Development Plan and applicable regulations. Required content:

| Element | Source SOP |
|---|---|
| Design and Development Plan + revisions | GL-SOP-DC-002 |
| User Needs register | GL-SOP-DC-003 |
| Design Inputs | GL-SOP-DC-003 |
| Design Outputs (incl. SAD, software / hardware design specs) | GL-SOP-DC-004 |
| Design Reviews (records of every formal review) | GL-SOP-DC-005 |
| Design Verification protocols + reports | GL-SOP-DC-006 |
| Design Validation protocols + reports | GL-SOP-DC-006 |
| Design Transfer evidence | GL-SOP-DC-007 |
| Design Change records | GL-SOP-DC-008 |
| Risk Management File (cross-reference) | GL-SOP-RM-001 |
| Usability Engineering File (cross-reference) | GL-SOP-UC-001 |
| Trace matrix | GL-WI-DC-002 |

## 4. DHF Index — Required Front Matter

Every DHF starts with a **DHF Index** (one markdown / spreadsheet file at the DHF root) listing every controlled artifact. Required columns:

| Column | Content |
|---|---|
| Doc ID | Project doc ID following project numbering |
| Title | Plain-language title |
| Type | Plan / Spec / Protocol / Report / Record / Form / etc. |
| Phase | Concept / Feasibility / Design / V&V / Transfer / Released |
| Status | Draft / In-Review / Approved / Released / Superseded |
| Revision | Numeric or letter rev |
| Effective Date | YYYY-MM-DD |
| Owner | Functional role |
| Path | Relative location in DHF |
| Trace | Optional — IDs of upstream artifacts this depends on |

The index is the **first thing** an auditor opens. Maintain it contemporaneously.

## 5. Filesystem / Repository Layout

The DHF lives under `docs/project/dhfs/<dhf-name>/` with this canonical layout:

```
docs/project/dhfs/<dhf-name>/
  README.md                           # DHF index (per §4)
  design-controls/
    plans/                            # DDP, V&V plans, transfer plan
    user-needs/                       # User Needs register, use spec
    requirements/                     # Design Input Specification
    architecture/                     # System Architecture Document
    design-outputs/                   # SDS, HW specs, source-code refs
    reviews/                          # Phase-gate review records
    vnv/                              # Verification + Validation
    transfer/                         # Design transfer evidence
    change-control/                   # ECRs, change reviews
  risk-management/                    # RMP, hazard analysis, FMEAs, RMR
  cybersecurity/                      # Security plan, threat model, SBOM, pentests
  usability/                          # UEF, formative + summative reports
  clinical/                           # CEP, CER, PMCF
  postmarket/                         # PMS plan, PSURs, complaints log link
```

Adapt as needed for project-specific shapes — but **deviations from this layout shall be documented** in the DHF README.

## 6. Naming Conventions

- Filenames: `kebab-case.md` (no spaces).
- Phase prefixes optional (e.g., `phase-1-concept-summary.md`); not required.
- Templates and forms keep their `GL-*` ID in the filename when instantiated, e.g., `GL-TMP-DC-001-instantiated-design-and-development-plan.md`.
- Avoid embedding revision numbers in filenames — revision lives in the document frontmatter / header. Otherwise every revision creates a new file and breaks links.

## 7. Cross-File Linking

Within a DHF, every cross-reference uses **markdown links** to the relative path. Avoid `see file X` plain-text references — they don't survive grep. Trace fields in the DHF Index complement (do not replace) inline links.

## 8. Freeze Points

The DHF is **frozen** at three points:

1. **Phase-gate freeze** — at each phase gate (per GL-FORM-DC-002), the artifacts going into the gate review are baselined; further changes require a DCR (per GL-SOP-QM-001).
2. **Submission freeze** — when a regulatory submission package is assembled, the DHF artifacts cited in the submission are frozen at the cited revision. Subsequent changes route through GL-SOP-DC-008 change control.
3. **Release freeze** — at design transfer to manufacturing, the DHF revision in effect at transfer becomes the "as-released" baseline. Field changes route through change control with regulatory impact assessment.

A frozen artifact's frontmatter is updated to record the freeze date and reason; the file content is otherwise unchanged.

## 9. DHF Closure / Retirement

A DHF is retired only when the device is removed from market and the regulatory retention period has elapsed (per GL-SOP-QM-001 §6.5). Until then, the DHF is maintained — even after the last sale — because post-market liability and surveillance obligations continue.

## 10. Auditor View

A productive audit traversal of a DHF proceeds: README index → DDP → User Needs → Design Inputs → trace matrix → V&V records → Risk Management Report → CEP/CER. Test the DHF by walking this sequence yourself before any audit.

## 11. Cross-References

- GL-SOP-DC-001 — Design Control (Master) — parent SOP
- GL-SOP-DC-002 — Design and Development Planning
- GL-SOP-DC-008 — Design Change Control
- GL-SOP-QM-001 — Document and Records Control
- GL-WI-DC-002 — Design Traceability Matrix (sibling WI)
- GL-FORM-DC-002 — Phase-Gate Review Checklist (freeze evidence)

## 12. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-27 | Ben Xavier (via Claude, task ben/036) | Initial release. Operationalizes DHF assembly referenced by GL-SOP-DC-001. |
