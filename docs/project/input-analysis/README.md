# Input Analysis

Upstream investigation and justification that feeds into design controls. This is the evidence base — market research, clinical input, competitive analysis, and predicate device evaluation that drives and validates product direction.

## Subfolders

| Folder | Purpose |
|--------|---------|
| `predicate-analysis/` | Predicate device search, profiles, comparison tables, and substantial equivalence argument |
| `competitive-landscape/` | Competitor portfolios, cleared devices, market positioning |
| `kol-feedback/` | Key Opinion Leader interviews, clinical advisory input, workflow insights |
| `market-research/` | Market landscape, unmet needs analysis, competitive positioning |

## Relationship to Design Controls

Input analysis is **shared across all DHFs** and provides the justification for design control decisions in each per-DHF design history file (`docs/project/dhfs/<dhf>/design-controls/`):
- Market research, competitive landscape, and KOL feedback inform **user and stakeholder needs**
- Predicate analysis informs the **substantial equivalence argument** in submissions
- Competitive landscape analysis informs **product positioning** and PCCP change categories
- All input analysis should be traceable to the per-DHF design inputs it supports
- Strategic decisions derived from input analysis are captured in `docs/project/strategies/<domain>-strategy.md`, not in this folder

## Conventions

- **Naming**: `topic-description.md` (kebab-case)
- Always note the date and source of any data or finding
- Link back to the originating task document
- When analysis matures into a formal deliverable, the polished version goes in `submissions/` or the relevant `dhfs/<dhf>/design-controls/`; keep the analysis file as a reference

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
| 2026-04-13 | BX | task 009: clarified that input-analysis is shared across DHFs; per-DHF design controls live under `dhfs/<dhf>/`. |
