---
source_file: "N/A — authored-in-markdown"
source_path: "quality-management/templates/training-record.md"
doc_id: "GL-FORM-QM-003"
doc_type: "FORM"
title: "Training Record"
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
  - doc_id: "GL-SOP-QM-003"
    title: "Training and Competence"
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "ISO 13485:2016 §6.2"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-FORM-QM-003 — Training Record

_Demo sample data — not for clinical use._

**Form ID:** GL-FORM-QM-003 (template)
**Revision:** 1.0
**Parent SOP:** GL-SOP-QM-003

---

## Trainee

| Field | Value |
|---|---|
| Name | `{{FULL NAME}}` |
| Employee ID | `{{ID}}` |
| Role | `{{ROLE}}` |
| Department | `{{DEPARTMENT}}` |

## Training Subject

| Field | Value |
|---|---|
| Document / Training ID | `{{GL-SOP-XX-NNN rev X.X or course code}}` |
| Title | `{{TITLE}}` |
| Method | ☐ Read-and-understand ☐ Classroom / e-learning ☐ Practical / OJT ☐ Regulatory awareness |
| Trainer | `{{NAME, where applicable}}` |
| Date Completed | `{{YYYY-MM-DD}}` |

## Competence Verification

| Method | Pass / Fail | Evidence |
|---|---|---|
| ☐ Read-and-sign | | Signature below |
| ☐ Quiz (pass ≥ 80%) | | Score: `{{}}` |
| ☐ Supervised execution | | Trainer signoff below |
| ☐ Practical assessment | | Observed against checklist `{{ID}}` |

## Signatures

| Role | Name | Date | Signature |
|---|---|---|---|
| Trainee | | | |
| Trainer (if applicable) | | | |
| Line Manager | | | |

## Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial template. |
