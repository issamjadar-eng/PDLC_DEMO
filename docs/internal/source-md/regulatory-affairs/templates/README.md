---
source_file: "N/A — authored-in-markdown"
source_path: "regulatory-affairs/templates/README.md"
doc_id: null
doc_type: "INDEX"
title: "Regulatory Affairs — Templates & Forms Index"
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
references: []
conversion_history:
  - date: "2026-06-15"
    source: "v1 — added under task ben/089 alongside GL-FORM-RA-001"
notes: "Form/template subfolder for the Regulatory Affairs QMS category."
---

# Regulatory Affairs — Templates & Forms

_Demo sample data — not for clinical use._

Controlled form and template instances for the Regulatory Affairs category — instantiated per filing and retained as quality records. Process governance (SOPs, work instructions) lives one level up at `../`.

## Conventions

- Forms follow the GL document-control header + `## Revision History` convention and the `GL-FORM-RA-NNN` numbering scheme.
- Form-field placeholders use `{{...}}`; checkbox options use `☐`.
- A form template here is project-agnostic; per-filing instances are filled and retained in the program's regulatory records (not committed to this QMS source tree).

## Inventory

| Doc ID | Title | Type | Parent | Effective |
|---|---|---|---|---|
| GL-FORM-RA-001 | Submission Package Assembly & Sign-off Record | Form | GL-WI-RA-001 / GL-WI-RA-003 | 2026-06-15 |

## Cross-References

- `../510k-submission-process-wi.md` (GL-WI-RA-001 §5.4) — sign-off chain this form records
- `../pma-submission-process-wi.md` (GL-WI-RA-003 §5.4) — PMA sign-off chain
- The `submissions` skill's `composition-manifest.md` is the authoring-side analogue of this form; the manifest doctype maps to GL-FORM-RA-001 via a project's `.taxonomy.yml` `governing_qms` when the submission folder is mirrored to a regulated vault.

## Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-06-15 | Ben Xavier (via Claude, task ben/089) | Folder created. GL-FORM-RA-001 added. |
