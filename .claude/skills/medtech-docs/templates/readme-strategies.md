# Strategies

**Shared, cross-cutting strategies** that apply to the whole project regardless of how many sub-DHFs exist. Sub-DHF-specific strategies (regulatory, architecture, development, testing, risk, postmarket) live inside each sub-DHF's `design-controls/plans/` folder. This folder is for project-level strategies that span components.

## Expected Content

| File | Purpose |
|------|---------|
| `commercial-strategy.md` | Pricing, reimbursement, channel, launch sequencing, customer targeting — spans the whole project portfolio |
| `operations-strategy.md` | Manufacturing, supply chain, quality management system posture, facility readiness — project-level operational concerns |

Additional project-wide strategies may be added here as the project matures (partnership strategy, intellectual-property strategy, data strategy). Per-sub-DHF strategies do **not** belong here.

## Relationship to per-sub-DHF strategies

| This folder (shared) | Per-sub-DHF (`dhfs/<name>/design-controls/plans/`) |
|---|---|
| `commercial-strategy.md` — whole-project pricing and market posture | `regulatory-strategy.md` — component-specific 510(k) / PCCP / filing approach |
| `operations-strategy.md` — whole-project manufacturing and QMS | `development-strategy.md` — component-specific engineering approach |
| — | `testing-strategy.md` — component-specific V&V plan and test architecture |
| — | `risk-strategy.md` — component-specific risk management approach |
| — | `architecture-strategy.md` — component-specific architecture choices |
| — | `postmarket-strategy.md` — component-specific PMS/PMCF plan |

**Rule of thumb**: if a decision applies uniformly across every sub-DHF in the project, it belongs here. If it varies by component or is tied to a specific filing, it belongs inside that sub-DHF.

## Relationship to `/strategy` skill

This folder is the destination for `domain=commercial` and `domain=operations` content harvested from task docs by `/strategy scan` and `/strategy assemble`. Per-sub-DHF domains (regulatory, architecture, development, testing, risk, postmarket) assemble into the matching sub-DHF's `design-controls/plans/` folder, not here.

Tag conventions for scope resolution (from the `/strategy` skill):
- `<!-- STRATEGY CONTENT: commercial, topics -->` → this folder
- `<!-- STRATEGY CONTENT: operations, topics -->` → this folder
- `<!-- STRATEGY CONTENT: regulatory, sub-dhf=<leaf>, topics -->` → that sub-DHF's plans folder

## Conventions

- Project-wide strategies are **living documents** — they should be updated at every major milestone (prototype, V&V start, filing, launch) and the changelog table should reflect it
- Cross-reference sub-DHF strategies when relevant (e.g., commercial-strategy.md should link to each sub-DHF's regulatory-strategy.md for the filing timeline assumptions)
- Do **not** duplicate sub-DHF-specific content here. If you find yourself copying content from a sub-DHF's strategy into this folder, that's a signal the content actually applies cross-project and should be _moved_, not duplicated

## For Claude

- When harvesting strategy content via `/strategy scan`, commercial and operations domain tags come here; other domains go to per-sub-DHF locations
- When the user asks about project-level strategy, read this folder first — it should be the single source of truth for commercial and operational posture
- Flag any per-sub-DHF strategy that contains content that would be better placed at the project level (and vice versa)

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
