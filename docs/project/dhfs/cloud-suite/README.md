# cloud-suite

DHF root for **cloud-suite** — stub created via task 007 P6 `add-dhf`. Content to be authored as the component's regulatory scope is defined.

**Regulatory status**: `mixed`
**Filing rollup**: `TBD (platform — no own filing)`
**Parent DHF**: `top-level`

## Structure

| Folder | Purpose |
|--------|---------|
| `design-controls/` | User needs, requirements, architecture, V&V, trace matrix, plans, tool validation |
| `clinical/` | Clinical evaluation plans, benefit-risk analyses, literature search results |
| `postmarket/` | PMCF plans and studies, CAPA, complaints |
| `risk-management/` | ISO 14971 hazard analysis, FMEA, risk-benefit |
| `cybersecurity/` | IEC 81001-5-1 assessment, threat model, SBOM, vulnerability management |

| `dhfs/` | Nested child DHFs (platform components) |

## Notes

This is a **platform DHF** (`regulatory: mixed`). Its own design controls describe the platform-level architecture, security posture, and cross-cutting concerns. Child DHFs under `dhfs/` carry the component-level regulatory weight and each rolls up into their own filing.

**Shared strategy briefs** for all eight domains live at `docs/project/strategies/<domain>-strategy.md` — cloud-suite platform specifics belong as `### Cloud Suite` callouts inside those briefs, not as separate per-DHF strategy files. Each child DHF (drug-library-manager, fleet-management, ...) gets its own callout in the same shared briefs.

When tagging strategy content from cloud-suite work, use `<!-- STRATEGY CONTENT: <domain>, topics -->`. All strategy domains are `shared` (v10+); the deprecated `dhf=cloud-suite` scope key is unnecessary.

_Demo sample data — not for clinical use._

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-13 | BX | Initial stub — created during task 007 P6 bulk add-dhf pass. |
| 2026-04-13 | BX | task 009: pointed at shared `strategies/` location and refreshed strategy-tag convention. |
