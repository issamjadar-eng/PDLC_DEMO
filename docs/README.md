# Documentation

All project documentation organized by origin and purpose.

## Structure

| Folder | Purpose |
|--------|---------|
| `external/` | Reference material we consume but don't author — FDA guidance, standards, industry frameworks, clinical literature |
| `internal/` | Process artifacts we own — SOPs, procedures, templates (source → markdown → distilled) |
| `project/` | What we're building — input analysis, shared strategies, per-DHF design controls, and submission packages |

## Information Flow

```
external/                  → Reference material informs all project work
project/input-analysis/    → Market research, KOLs, predicate analysis drive design inputs
project/strategies/        → Shared cross-component strategies (one file per domain)
project/dhfs/<dhf>/        → Per-DHF design controls, risk mgmt, cybersecurity, postmarket
project/submissions/       → Packages assembled from per-DHF design controls for regulatory body
internal/                  → SOPs, procedures, and templates govern how we work
```

## Conventions

- Each subfolder contains its own README.md describing its purpose and conventions
- Documents use markdown format unless otherwise specified
- Every README.md includes a changelog tracking modifications

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
| 2026-04-13 | BX | task 009: updated structure description and information flow to reflect unified `dhfs/` shape and shared `strategies/` location. |
