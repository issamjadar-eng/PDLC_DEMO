# {{SUB_DHF_NAME}}

Sub-DHF root for **{{SUB_DHF_NAME}}** — the Design History File record for this component. A sub-DHF groups all per-component regulated content: design controls, clinical, postmarket, risk management, and cybersecurity. Shared project content (input analysis, submissions, external standards, internal SOPs) lives at the project level.

**Regulatory status**: `{{REGULATORY_STATUS}}` — one of `concept | in-development | cleared | mixed`. `mixed` denotes a platform sub-DHF whose children carry the regulatory weight (the platform itself does not ship separately).

**Filing rollup**: `{{FILING}}` — the submission folder under `docs/project/submissions/<filing>/` that this sub-DHF rolls up into (`null` or `TBD` if not yet scoped).

## Structure

| Folder | Purpose |
|--------|---------|
| `design-controls/` | User needs, requirements, architecture, V&V, trace matrix, plans, tool validation — ISO 13485 / 21 CFR 820.30 design control record for this component |
| `clinical/` | Clinical evaluation plans, benefit-risk analyses, literature search results |
| `postmarket/` | Post-market clinical follow-up (PMCF) plans and studies, CAPA, complaints |
| `risk-management/` | ISO 14971 risk analysis, hazard analysis, FMEA, risk-benefit. Sibling of `design-controls/`, not a child — risk management is device-level, not design-controls-process-level |
| `cybersecurity/` | IEC 81001-5-1 assessment, threat model, SBOM, vulnerability management |

Nested sub-DHFs (children of a platform sub-DHF) live under a `dhfs/` subfolder here. If this sub-DHF is itself a platform (`regulatory: mixed`), children are added via `/medtech-docs add-sub-dhf <name> --parent {{SUB_DHF_NAME}}`.

## Relationship to shared project content

| Shared source | How this sub-DHF uses it |
|---|---|
| `docs/project/input-analysis/` | Source of user needs, predicate analysis, competitive intelligence — scoped down to this component |
| `docs/project/strategies/` | Cross-cutting commercial and operations strategies that apply to the whole project |
| `docs/external/standards/` | Referenced standards (IEC 62304, ISO 14971, IEC 62366-1, etc.) — the same standards apply across all sub-DHFs |
| `docs/internal/source/` | Corporate SOPs that govern how this sub-DHF's design controls are executed |
| `docs/project/submissions/{{FILING}}/` | The filing this sub-DHF rolls up into. Composition manifest inside the filing folder lists which pieces of this sub-DHF are included |

## Conventions

- **One sub-DHF = one component = one regulatory story.** Keep per-DHF content narrowly scoped. Project-wide content (market research, cross-component architecture, portfolio-level strategy) belongs at `docs/project/` root, not here.
- **Cross-references** between sub-DHFs (e.g., this sub-DHF's interface to another component) should live in `design-controls/architecture/` as interface specs, not in `cybersecurity/` or `risk-management/`.
- **Filing rollup**: when the composition manifest for `{{FILING}}` is authored, it references specific files here as "Included pieces." Keep file paths stable to avoid manifest churn.

## For Claude

- When working inside this sub-DHF, default to treating `design-controls/`, `clinical/`, `postmarket/`, `risk-management/`, and `cybersecurity/` as the only per-DHF content. Do not create sibling folders without a design decision captured in a task.
- When authoring user needs or requirements, cross-reference the shared `input-analysis/` sources — do not duplicate content.
- Use `sub-dhf={{SUB_DHF_NAME}}` as the scope tag when capturing strategy content destined for this sub-DHF (per `/strategy` skill tag convention).

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init or add-sub-dhf |
