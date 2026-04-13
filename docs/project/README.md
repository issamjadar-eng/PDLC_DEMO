# Project Documents

What we're building — the deliverables and analysis that make up the regulatory filing and design history.

## Structure

| Folder | Purpose |
|--------|---------|
| `input-analysis/` | Upstream investigation and justification — predicate analysis, KOL feedback, market research |
| `design-controls/` | Design History File core — plans, user/stakeholder needs, requirements, architecture, risk management, V&V |
| `submissions/` | Packages assembled for regulatory body — Q-Sub, 510(k)/De Novo/PMA, PCCP |
| `clinical/` | Clinical evidence portfolio — clinical evaluation plans, benefit-risk analyses, literature search strategies |
| `postmarket/` | Ongoing customer feedback loop — PMCF plans and studies, CAPAs, complaints ledger |

## Information Flow

```
input-analysis/     → Drives and justifies design inputs
design-controls/    → Formal design control waterfall (user needs → requirements → architecture → V&V)
submissions/        → Assembled from design controls; references input-analysis for justification
```

## Conventions

- **Language**: Formal, precise, regulatory-appropriate in all deliverables
- **Versioning**: Each document maintains a changelog header:
  <!-- Changelog
  | Version | Date | Author | Summary |
  |---------|------|--------|---------|
  | 0.1 | YYYY-MM-DD | XX | Initial draft |
  -->
- Versions use 0.x for drafts, 1.0+ for submission-ready
- Flag uncertain content with [VERIFY] inline markers
- Never fabricate regulatory precedent, clearance numbers, or guidance citations

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
| 2026-04-12 | clinical/postmarket ingestion | Added `clinical/` and `postmarket/` branches to the project structure. |
