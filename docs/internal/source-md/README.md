# Source — Markdown Conversions & Authored QMS Content

Markdown content under `docs/internal/` that governs how GlobalLogic MedTech works. Two kinds of files live here:

1. **Conversions** of original source documents from `../source/` — machine-readable copies used for AI-assisted analysis, cross-referencing, and distillation.
2. **Authored QMS content** (Quality Manual, SOPs, Work Instructions, Templates, Forms) drafted directly in markdown and organized by functional category (QMS, Design Controls, Risk, Software/Cyber, Usability/Clinical, Supplier/Production, Post-Market).

See [`qms-index.md`](qms-index.md) for the master index of all authored QMS documents by category, with ISO / IEC / FDA clause anchors.

## Expected Content

- **Authored QMS content** (markdown-native): organized by category folder
  - [`quality-management/`](quality-management/) — Quality Manual, Doc Control, Mgmt Review, Training, Audit, CAPA
  - [`design-controls/`](design-controls/) — §7.3 / 820.30 SOPs + templates
  - [`risk-management/`](risk-management/) — ISO 14971:2019 SOPs + templates
  - [`software-cybersecurity/`](software-cybersecurity/) — IEC 62304 + IEC 81001-5-1 SOPs + templates
  - [`usability-clinical/`](usability-clinical/) — IEC 62366-1 + MDR clinical evaluation SOPs + templates
  - [`supplier-production/`](supplier-production/) — §7.4 / §7.5 SOPs + NCR / incoming inspection
  - [`post-market/`](post-market/) — PMS, complaints, vigilance SOPs + templates
  - [`qms-index.md`](qms-index.md) — Master index (GL-IDX-QM-001)
- **Conversions** of originals under `../source/`:
  - One `.md` file per source document

## Conventions

- **Authored QMS docs** follow the numbering scheme `GL-<TYPE>-<AREA>-<NNN>` (TYPE ∈ MAN/POL/SOP/WI/FORM/TMP; AREA ∈ QM/DC/RM/SW/UC/SP/PM).
- Every authored doc has **docflow-compatible YAML frontmatter** and the banner `_Demo sample data — not for clinical use._`.
- Every SOP section order: Purpose · Scope · Responsibilities · Definitions · References · Procedure · Records · Revision History.
- **Converted docs** (from `../source/`) match the original filename, preserve structure, carry conversion method + date, and flag unrecoverable content with `[VERIFY]`.
- **Category READMEs** have `## Conventions` and `## Changelog` sections.

## Changelog

| Date | Author | Summary |
|---|---|---|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
| 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Added GlobalLogic QMS scaffold — 7 category folders + qms-index.md; 55 authored documents across P1–P6. |
