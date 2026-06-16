---
source_file: "N/A — authored-in-markdown"
source_path: "regulatory-affairs/README.md"
doc_id: null
doc_type: "INDEX"
title: "Regulatory Affairs — Folder Index"
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
references: []
conversion_history:
  - date: "2026-04-27"
    source: "v1 — added under task ben/036 to scaffold the new Regulatory Affairs QMS category"
notes: "New top-level category added under task ben/036 to give Regulatory Affairs its own governance surface."
---

# Regulatory Affairs

_Demo sample data — not for clinical use._

GlobalLogic regulatory affairs procedures, work instructions, and templates. This category was added under task ben/036 to give Regulatory Affairs its own governance surface — previously regulatory content was scattered across design-controls (change determinations) and post-market (vigilance reporting), without a top-level home for submission-pathway and Regulatory Operations procedures.

## Conventions

- Documents in this folder follow the standard GL document-control header and revision history convention.
- Regulatory Operations procedures (multi-pathway, multi-jurisdiction) live at the folder root. Pathway-specific work instructions (510(k), De Novo, PMA, MDR, MDSAP) live in `templates/` or in named subfolders if they grow beyond ~5 docs.
- Filing submissions, response letters, and similar **artifacts** live in `docs/project/dhfs/<dhf>/regulatory/` per project — not here. This folder governs the **process**.

## Inventory

| Doc ID | Title | Type | Effective |
|---|---|---|---|
| GL-SOP-RA-001 | Regulatory Operations | SOP | 2026-04-27 |
| GL-WI-RA-001 | 510(k) Submission Process | WI | 2026-04-27 |
| GL-WI-RA-002 | De Novo Submission Process | WI | 2026-06-15 |
| GL-WI-RA-003 | PMA Submission Process | WI | 2026-06-15 |
| GL-FORM-RA-001 | Submission Package Assembly & Sign-off Record (in [`templates/`](templates/README.md)) | Form | 2026-06-15 |

## Cross-References

- GL-SOP-DC-008 — Design Change Control (510(k) change-determination handoff)
- GL-SOP-PM-003 — Adverse Event Reporting (vigilance — adjacent regulatory surface)
- FDA 510(k), De Novo, PMA, PCCP guidance documents under `docs/external/fda-guidance/`
- EU MDR 2017/745

## Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-04-27 | Ben Xavier (via Claude, task ben/036) | Folder created. GL-SOP-RA-001 + GL-WI-RA-001 added. |
| 2026-06-15 | Ben Xavier (via Claude, task ben/089) | Added GL-WI-RA-003 (PMA Submission Process) + the `templates/` subfolder with GL-FORM-RA-001 (Submission Package Assembly & Sign-off Record). Closes gaps surfaced by the submissions-skill template verification. |
| 2026-06-15 | Ben Xavier (via Claude, task ben/090) | Added GL-WI-RA-002 (De Novo Submission Process) — completes the RA pathway set (510(k) + De Novo + PMA). |
