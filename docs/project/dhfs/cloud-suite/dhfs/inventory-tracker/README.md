# inventory-tracker

DHF root for **inventory-tracker** — stub created via task 007 P6 `add-dhf`. Content to be authored as the component's regulatory scope is defined.

**Regulatory status**: `in-development`
**Filing rollup**: `510k`
**Parent DHF**: `cloud-suite`

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

**Shared strategy briefs** for all eight domains live at `docs/project/strategies/<domain>-strategy.md` — inventory-tracker specifics belong as `### Inventory Tracker` callouts inside those briefs, not as separate per-DHF strategy files.

When tagging strategy content from this DHF, use `<!-- STRATEGY CONTENT: <domain>, topics -->`. All strategy domains are `shared` (v10+); the deprecated `dhf=inventory-tracker` scope key is unnecessary.

_Demo sample data — not for clinical use._

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-13 | BX | Initial stub — created during task 007 P6 bulk add-dhf pass. |
| 2026-04-13 | BX | task 009: pointed at shared `strategies/` location and refreshed strategy-tag convention. |
