# Usability Engineering File — drug-library-manager

> _Demo sample data — not for clinical use._

Usability Engineering File (UEF) per IEC 62366-1 for the Drug Library Manager (DLM) — the Class II SaMD component that authors and signs the drug library enforced by PP3500. Captures pharmacist-workflow use specification, URRA, evaluation reports, and critical tasks.

## Expected Content

- `use-specification.md` — pharmacist user, clinical pharmacy environment, intended use
- `urra.md` — use-related risk analysis (miss-click, wrong-formulary, stale-sig) cross-referenced to the DLM risk file
- `critical-tasks.md` — rule edits, rule signing, rule publication
- `formative-*.md` — formative evaluation reports
- `summative-report.md` — summative evaluation demonstrating rule authoring and signing workflows are safe and effective
- `formal/` — controlled deliverables for submission

## Conventions

- **Naming**: kebab-case filenames. Each evaluation carries a frontmatter `evaluation_type` and `date`.
- Every usability artifact cross-references User Needs and Design Inputs for the Validation Engine and Signing Service modules.
- The summative report is the filing-track deliverable; formative reports support the trace matrix but aren't typically submitted standalone.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-20 | Ben Xavier | Stub folder — created under task 018 so the 510(k) composition manifest's DLM UEF piece resolves. Awaiting content. |
