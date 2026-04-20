# Usability Engineering File — pca-device

> _Demo sample data — not for clinical use._

Usability Engineering File (UEF) per IEC 62366-1 for the PainEase PCA Advanced (PP3500). Captures use specification, use-related risk analysis (URRA), formative and summative evaluation reports, and the critical-tasks inventory.

## Expected Content

- `use-specification.md` — intended users, use environment, intended use
- `urra.md` — use-related risk analysis cross-referenced to the risk management file
- `critical-tasks.md` — tasks where use error could cause harm
- `formative-*.md` — formative evaluation reports (multiple rounds during design)
- `summative-report.md` — summative usability evaluation (HF Validation) — required for 510(k)
- `user-interface-spec.md` — UI spec per Clause 5.3
- `formal/` — controlled deliverables (DOCX / XLSX) for submission

## Conventions

- **Naming**: kebab-case filenames. Each evaluation carries a frontmatter `evaluation_type: formative|summative` and `date`.
- Every usability artifact cross-references the originating User Need / Design Input so the trace matrix can resolve it.
- Summative report is the deliverable that lands in the 510(k); formative reports support it but are not typically submitted.
- Linked to: ISO 14971 risk file, IEC 62366-1 standard, FDA Human Factors guidance.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-20 | Ben Xavier | Stub folder — created under task 018 so the 510(k) composition manifest's Usability Engineering File piece resolves. Awaiting content. |
