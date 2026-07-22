# Project Documents

What we're building — the deliverables and analysis that make up the regulatory filing and design history.

## Structure

| Folder | Purpose |
|--------|---------|
| `input-analysis/` | Upstream investigation and justification — predicate analysis, KOL feedback, market research |
| `strategies/` | Shared cross-component strategy briefs — one file per domain (regulatory, architecture, development, testing, risk, postmarket, commercial, operations) |
| `dhfs/` | Per-DHF Design History Files — each DHF carries its own `design-controls/`, `risk-management/`, `cybersecurity/`, `clinical/`, `postmarket/` |
| `submissions/` | Packages assembled for regulatory body — Q-Sub, 510(k)/De Novo/PMA, PCCP |
| `corpus/` | Versioned evidence grounding (corpus skill) — immutable provenance-pinned data snapshots (external openFDA + internal exports) + stated assumption records, cited by analyses as `dataset@snapshot` |

## Information Flow

```
input-analysis/        → Drives and justifies design inputs (shared across DHFs)
strategies/            → Cross-component decisions; upstream of per-DHF formal outputs
dhfs/<dhf>/            → Formal design control waterfall per DHF (user needs → requirements → architecture → V&V → risk → postmarket)
submissions/           → Assembled from per-DHF design controls; references input-analysis and strategies for justification
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
| 2026-04-13 | BX | task 009: structure now reflects unified `dhfs/<dhf>/` shape (clinical/postmarket/risk live per-DHF) plus shared `strategies/` location. |
| 2026-07-22 | BX / AI Assistant | task 108: added `corpus/` — versioned evidence-grounding data tier for the commercial analytics suite (immutable snapshots + provenance + assumption records). |
