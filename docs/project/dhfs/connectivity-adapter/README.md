# connectivity-adapter

Sub-DHF root for **connectivity-adapter** — stub created via task 007 P6 `add-sub-dhf`. Content to be authored as the component's regulatory scope is defined.

**Regulatory status**: `in-development`
**Filing rollup**: `510k`
**Parent sub-DHF**: `top-level`

## Structure

| Folder | Purpose |
|--------|---------|
| `design-controls/` | User needs, requirements, architecture, V&V, trace matrix, plans, tool validation |
| `clinical/` | Clinical evaluation plans, benefit-risk analyses, literature search results |
| `postmarket/` | PMCF plans and studies, CAPA, complaints |
| `risk-management/` | ISO 14971 hazard analysis, FMEA, risk-benefit |
| `cybersecurity/` | IEC 81001-5-1 assessment, threat model, SBOM, vulnerability management |


## Notes

This sub-DHF represents a single regulated component. Design controls, risk management, and cybersecurity are scoped to this component; shared project content (input-analysis, external standards, internal SOPs) lives at `docs/project/`.

Use `sub-dhf=connectivity-adapter` as the scope tag when capturing strategy content destined for this sub-DHF (per `/strategy` skill tag convention).

_Demo sample data — not for clinical use._

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-13 | BX | Initial stub — created during task 007 P6 bulk add-sub-dhf pass. |
