# Strategies

**Shared, cross-cutting strategies** for PDLC_DEMO — project-wide strategies that apply across the whole product portfolio and every sub-DHF. Sub-DHF-specific strategies (regulatory, architecture, development, testing, risk, postmarket) live inside each sub-DHF's own `design-controls/plans/`, `risk-management/`, or `postmarket/` folders.

## Expected Content

| File | Purpose |
|------|---------|
| `commercial-strategy.md` | Pricing, reimbursement, channel, launch sequencing, customer targeting — spans the whole PDLC_DEMO portfolio (PP3500 + future components) |
| `operations-strategy.md` | Manufacturing, supply chain, QMS posture, facility readiness — project-level operational concerns |

Additional project-wide strategies may be added here as the project matures (partnership strategy, intellectual-property strategy, data strategy). **Per-sub-DHF strategies do not belong here.**

## Relationship to per-sub-DHF strategies

| This folder (shared) | Per-sub-DHF (`dhfs/<name>/design-controls/plans/`) |
|---|---|
| `commercial-strategy.md` — whole-project pricing and market posture | `regulatory-strategy.md` — component-specific 510(k) / PCCP / filing approach |
| `operations-strategy.md` — whole-project manufacturing and QMS | `development-strategy.md` — component-specific engineering approach |
| — | `testing-strategy.md` — component-specific V&V plan and test architecture |
| — | `architecture-strategy.md` — component-specific architecture choices |

Sub-DHF-level `risk-strategy.md` lives in `dhfs/<name>/risk-management/` and `postmarket-strategy.md` lives in `dhfs/<name>/postmarket/` (siblings of design-controls, not children) per the unified sub-DHF shape.

**Rule of thumb**: if a decision applies uniformly across every sub-DHF in the project, it belongs here. If it varies by component or is tied to a specific filing, it belongs inside that sub-DHF.

## Relationship to `/strategy` skill

This folder is the destination for `domain=commercial` and `domain=operations` content harvested from task docs by `/strategy scan` and `/strategy assemble`. Per-sub-DHF domains (regulatory, architecture, development, testing, risk, postmarket) assemble into the matching sub-DHF's plans folder, not here.

Tag conventions for scope resolution (from the `/strategy` skill):
- `<!-- STRATEGY CONTENT: commercial, topics -->` → this folder
- `<!-- STRATEGY CONTENT: operations, topics -->` → this folder
- `<!-- STRATEGY CONTENT: regulatory, sub-dhf=pca-device, topics -->` → `dhfs/pca-device/design-controls/plans/regulatory-strategy.md`

## Conventions

- Project-wide strategies are **living documents** — they should be updated at every major milestone and the changelog should reflect it
- Cross-reference sub-DHF strategies when relevant (e.g., commercial-strategy.md links to each sub-DHF's regulatory-strategy.md for filing timeline assumptions)
- Do **not** duplicate sub-DHF-specific content here

## For Claude

- When harvesting strategy content via `/strategy scan`, commercial and operations domain tags come here; other domains go to per-sub-DHF locations
- When the user asks about project-level strategy, read this folder first — single source of truth for commercial and operational posture

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-13 | BX | Initial version — created during task 007 P6 reorg as the new shared strategies location. `operations-strategy.md` moves here from the project root; `commercial-strategy.md` moves here from `input-analysis/market-research/`. |
