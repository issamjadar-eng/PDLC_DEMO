# Quality Management (`quality-management/`)

Top-level QMS documents for **GlobalLogic** MedTech — the Quality Manual plus the core SOPs that govern how the QMS is operated (document control, management review, training, internal audit, CAPA).

_Demo sample data — not for clinical use._

## Contents

| Doc ID | Type | Title | Anchor |
|---|---|---|---|
| GL-MAN-QM-001 | Manual | [Quality Manual](quality-manual.md) | ISO 13485:2016 (all); 21 CFR 820; EU MDR |
| GL-SOP-QM-001 | SOP | [Document and Records Control](document-and-records-control-sop.md) | ISO 13485 §4.2.4, §4.2.5; 21 CFR 820.40; 21 CFR Part 11 |
| GL-SOP-QM-002 | SOP | [Management Review](management-review-sop.md) | ISO 13485 §5.6; 21 CFR 820.20(c) |
| GL-SOP-QM-003 | SOP | [Training and Competence](training-sop.md) | ISO 13485 §6.2; 21 CFR 820.25 |
| GL-SOP-QM-004 | SOP | [Internal Audit](internal-audit-sop.md) | ISO 13485 §8.2.4; 21 CFR 820.22; ISO 19011:2018 |
| GL-SOP-QM-005 | SOP | [Corrective Action / Preventive Action](capa-sop.md) | ISO 13485 §8.5; 21 CFR 820.100 |
| GL-FORM-QM-001 | Form | [CAPA Form](templates/capa-form.md) | Used by GL-SOP-QM-005 |
| GL-FORM-QM-002 | Form | [Management Review Minutes](templates/management-review-minutes.md) | Used by GL-SOP-QM-002 |
| GL-FORM-QM-003 | Form | [Training Record](templates/training-record.md) | Used by GL-SOP-QM-003 |
| GL-FORM-QM-004 | Form | [Internal Audit Plan](templates/audit-plan.md) | Used by GL-SOP-QM-004 |
| GL-FORM-QM-005 | Form | [Document Change Request](templates/document-change-request.md) | Used by GL-SOP-QM-001 |

## Conventions

- Doc IDs follow `GL-<TYPE>-QM-<NNN>`.
- Every SOP references ISO / FDA / EU clauses by clause number in §5.
- Forms/templates under `templates/` are fillable markdown stubs with `{{PLACEHOLDER}}` tokens.
- Every file carries the `_Demo sample data — not for clinical use._` banner.
- Every file has docflow-compatible YAML frontmatter.

## Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial scaffold — Quality Manual, 5 SOPs, 5 Forms. |
