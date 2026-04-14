# connectivity-adapter

DHF root for **connectivity-adapter** — stub created via task 007 P6 `add-dhf`. Content to be authored as the component's regulatory scope is defined.

**Regulatory status**: `in-development`
**Filing rollup**: `510k`
**Parent DHF**: `top-level`

## Structure

| Folder | Purpose |
|--------|---------|
| `design-controls/` | User needs, requirements, architecture, V&V, trace matrix, plans, tool validation |
| `clinical/` | Clinical evaluation plans, benefit-risk analyses, literature search results |
| `postmarket/` | PMCF plans and studies, CAPA, complaints |
| `risk-management/` | ISO 14971 hazard analysis, FMEA, risk-benefit |
| `cybersecurity/` | IEC 81001-5-1 assessment, threat model, SBOM, vulnerability management |


## Notes

This DHF represents a single regulated component. Design controls, risk management, and cybersecurity are scoped to this component; shared project content (input-analysis, external standards, internal SOPs) lives at `docs/project/`.

**Shared strategy briefs** for all eight domains (regulatory, architecture, development, testing, risk, postmarket, commercial, operations) live at `docs/project/strategies/<domain>-strategy.md` — connectivity-adapter specifics belong as `### Connectivity Adapter` callouts inside those briefs, not as separate per-DHF strategy files.

When tagging strategy content from connectivity-adapter work, use `<!-- STRATEGY CONTENT: <domain>, topics -->`. All strategy domains are `shared` (v10+); the deprecated `dhf=connectivity-adapter` scope key is unnecessary.

_Demo sample data — not for clinical use._

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-13 | BX | Initial stub — created during task 007 P6 bulk add-dhf pass. |
| 2026-04-13 | BX | task 009: pointed at shared `strategies/` location and refreshed strategy-tag convention. |
