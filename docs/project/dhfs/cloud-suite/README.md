# cloud-suite

Sub-DHF root for **cloud-suite** — stub created via task 007 P6 `add-sub-dhf`. Content to be authored as the component's regulatory scope is defined.

**Regulatory status**: `mixed`
**Filing rollup**: `TBD (platform — no own filing)`
**Parent sub-DHF**: `top-level`

## Structure

| Folder | Purpose |
|--------|---------|
| `design-controls/` | User needs, requirements, architecture, V&V, trace matrix, plans, tool validation |
| `clinical/` | Clinical evaluation plans, benefit-risk analyses, literature search results |
| `postmarket/` | PMCF plans and studies, CAPA, complaints |
| `risk-management/` | ISO 14971 hazard analysis, FMEA, risk-benefit |
| `cybersecurity/` | IEC 81001-5-1 assessment, threat model, SBOM, vulnerability management |

| `dhfs/` | Nested child sub-DHFs (platform components) |

## Notes

This is a **platform sub-DHF** (`regulatory: mixed`). Its own design controls describe the platform-level architecture, security posture, and cross-cutting concerns. Child sub-DHFs under `dhfs/` carry the component-level regulatory weight and each rolls up into their own filing.

Use `sub-dhf=cloud-suite` as the scope tag when capturing strategy content destined for this sub-DHF (per `/strategy` skill tag convention).

_Demo sample data — not for clinical use._

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-13 | BX | Initial stub — created during task 007 P6 bulk add-sub-dhf pass. |
