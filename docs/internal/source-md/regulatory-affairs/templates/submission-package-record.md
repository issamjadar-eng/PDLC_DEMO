---
source_file: "N/A — authored-in-markdown"
source_path: "regulatory-affairs/templates/submission-package-record.md"
doc_id: "GL-FORM-RA-001"
doc_type: "FORM"
title: "Submission Package Assembly & Sign-off Record"
format: "md"
conversion_date: "2026-06-15"
conversion_method: "claude-authored"
conversion_fidelity: "faithful"
pages: null
sheets: null
has_images: false
image_count: 0
has_tables: true
has_form_fields: true
references:
  - doc_id: "GL-WI-RA-001"
    title: "510(k) Submission Process"
    resolved: true
    match: null
    note: "Parent WI (510(k) sign-off chain §5.4)"
  - doc_id: "GL-WI-RA-003"
    title: "PMA Submission Process"
    resolved: true
    match: null
    note: "Parent WI (PMA sign-off chain §5.4)"
  - doc_id: "GL-SOP-RA-001"
    title: "Regulatory Operations"
    resolved: true
    match: null
    note: "Grandparent SOP (§5.4 submission-lifecycle handoff)"
  - doc_id: "21 CFR 807.87"
    title: "Information required in a premarket notification (510(k))"
    resolved: true
    match: null
    note: null
  - doc_id: "21 CFR 814.20"
    title: "PMA application content and format"
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-06-15"
    source: "v1 — added under task ben/089 to give submission package-assembly + sign-off a controlled QMS form (the gap the submissions-skill verification surfaced: SOP + WI existed, no FORM)"
notes: "The controlled record of which pieces a filing includes and the internal sign-off chain that authorizes transmittal. Pathway-agnostic (510(k) / PMA / De Novo). The submissions skill's composition-manifest.md is the authoring-side analogue; this form is its QMS record."
---

# GL-FORM-RA-001 — Submission Package Assembly & Sign-off Record

_Demo sample data — not for clinical use._

**Form ID:** GL-FORM-RA-001 (template)
**Revision:** 1.0
**Parent WI:** GL-WI-RA-001 (510(k)) / GL-WI-RA-003 (PMA)

---

## 1. Filing Identification

| Field | Value |
|---|---|
| Filing type | ☐ Q-Sub ☐ 510(k) ☐ PMA ☐ De Novo ☐ Other: `{{}}` |
| Filing / submission ID | `{{FDA-assigned or internal}}` |
| Device | `{{DEVICE, MODEL}}` |
| Pathway / predicate | `{{predicate K-number (510k) or N/A (PMA)}}` |
| Lead DHF | `{{dhf}}` |
| Target transmittal date | `{{YYYY-MM-DD}}` |

## 2. Package Contents Checklist

One row per piece. The cited revision must match the DHF Index (per GL-WI-RA-001 §5.4 / GL-WI-RA-003 §5.4). The authoring-side list lives in the program's `composition-manifest.md`; this checklist is the controlled record.

| # | Piece | Required? | Present? | Version / DHF rev | Source (authored / DHF-attached) |
|---|---|---|---|---|---|
| 1 | `{{piece}}` | ☐ Required ☐ Supporting | ☐ Yes ☐ N/A | `{{}}` | ☐ Authored ☐ DHF-attached |

> **Cover-letter ↔ manifest alignment check:** the cover letter's Attachments section MUST list the same pieces as this checklist (and the `composition-manifest.md`), 1:1. ☐ Verified aligned.

## 3. Pre-Transmittal Gate

| Gate item | Status |
|---|---|
| All "Required" pieces Present | ☐ Pass ☐ Fail |
| Any transmission-blocking brief at status ≥ draft-v0.1 | ☐ Pass ☐ N/A |
| Cited DHF revisions match the DHF Index | ☐ Pass ☐ Fail |
| Cover-letter / manifest / this record aligned 1:1 | ☐ Pass ☐ Fail |
| (PMA) Manufacturing section pre-approval-inspection ready | ☐ Pass ☐ N/A |

A "Fail" on any gate item blocks transmittal until resolved.

## 4. Internal Review & Sign-off

Roles only — per separation-of-duties (GL-SOP-QM-006 §6; reviewers are not the author of the record). Authorship is tracked in §5 below, not here. Sign-off chain per the governing WI:

| # | Role | Name | Date | Signature |
|---|---|---|---|---|
| 1 | RA Specialist — completeness | | | |
| 2 | RA Lead — accuracy / SE or benefit-risk quality | | | |
| 3 | Clinical / Biostatistics (PMA, or 510(k) with clinical data) | | | |
| 4 | Quality — cited DHF revisions match the DHF Index | | | |
| 5 | VP Regulatory Affairs — authorizes transmittal | | | |

## 5. Authorship / Preparation Log

| Date | Preparer (name, role) | Activity |
|---|---|---|
| `{{YYYY-MM-DD}}` | `{{}}` | `{{assembled / revised section X}}` |

## 6. Transmittal Record

| Field | Value |
|---|---|
| Transmitted via | ☐ eSTAR / CDRH Portal ☐ Other: `{{}}` |
| Date / time transmitted | `{{}}` |
| FDA confirmation / receipt | `{{}}` |
| Logged in Regulatory Communications Register (GL-SOP-RA-001 §5.2) | ☐ Yes |

## 7. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-06-15 | Ben Xavier (via Claude, task ben/089) | Initial form template. Package-assembly + sign-off record for any filing pathway; QMS analogue of the submissions-skill composition manifest. |
