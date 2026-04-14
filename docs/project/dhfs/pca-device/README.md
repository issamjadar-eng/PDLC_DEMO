# pca-device

Sub-DHF root for **pca-device** — the Design History File record for the PainEase PCA Advanced (PP3500) patient-controlled analgesia pump. This is the DHF anchor for PDLC_DEMO's lead product and the first sub-DHF in the project's `sub_dhfs[]` list.

**Regulatory status**: `in-development` — on track for 510(k) filing, predicate PP3000 (K190567), target clearance under K210345.

**Filing rollup**: `510k` — rolls up into `docs/project/submissions/510k/`. Composition manifest (when authored) will list which artifacts from this sub-DHF are included in the PP3500 510(k) submission.

## Structure

| Folder | Purpose |
|--------|---------|
| `design-controls/` | User needs, requirements, architecture, V&V, trace matrix, plans, tool validation — ISO 13485 / 21 CFR 820.30 design control record for PP3500 |
| `clinical/` | Clinical evaluation plans, benefit-risk analyses, literature search results |
| `postmarket/` | PMCF plans and studies, CAPA, complaints — post-market surveillance for PP3500 |
| `risk-management/` | ISO 14971 hazard analysis, FMEA, risk-benefit. Sibling of `design-controls/`, not a child |
| `cybersecurity/` | IEC 81001-5-1 assessment, threat model, SBOM, vulnerability management |

PDLC_DEMO's broader 5-device infusion portfolio (IP5000, PP3000, PP3500, SP6000, SP6500) is retained as **portfolio and predicate context** under the shared `docs/project/input-analysis/predicate-analysis/`, not as separate sub-DHFs. Only PP3500 has its own design controls in this project. When other components (connectivity-adapter, cloud-suite, etc.) need their own DHFs, they will be added via `/medtech-docs add-sub-dhf`.

## Relationship to shared project content

| Shared source | How pca-device uses it |
|---|---|
| `docs/project/input-analysis/predicate-analysis/` | PP3000 predicate evaluation, portfolio positioning |
| `docs/project/input-analysis/kol-feedback/` | KOL input informing user needs |
| `docs/project/input-analysis/market-research/` | Market landscape, unmet needs |
| `docs/project/input-analysis/competitive-landscape/` | Competitive positioning |
| `docs/project/strategies/commercial-strategy.md` | Project-wide commercial posture (cross-component) |
| `docs/project/strategies/operations-strategy.md` | Project-wide operations and QMS posture |
| `docs/external/standards/` | IEC 62304, ISO 14971, IEC 62366-1, IEC 81001-5-1, etc. |
| `docs/external/fda-guidance/` | 510(k) SE, cybersecurity, PCCP, SW changes, SW functions guidances |
| `docs/internal/source/` | Corporate SOPs governing how DHF work is executed |
| `docs/project/submissions/510k/` | Target filing — 510(k) for PP3500 |

## Conventions

- **One sub-DHF = one component = one regulatory story.** Keep per-DHF content narrowly scoped to PP3500. Portfolio-level content (market research, portfolio predicate analysis, cross-component strategy) belongs at `docs/project/` root under `input-analysis/` or `strategies/`, not here.
- **Cross-references** to the broader portfolio live in `design-controls/user-needs/` (traceability back to portfolio-level user needs) and `docs/project/input-analysis/predicate-analysis/` (comparison against PP3000 predicate).
- Use `sub-dhf=pca-device` as the scope tag when capturing strategy content destined for this sub-DHF (per `/strategy` skill tag convention).

## For Claude

- When working inside `dhfs/pca-device/`, treat PP3500 as the device of record. Other devices in the portfolio (IP5000, PP3000, SP6000, SP6500) are context and predicates, not design targets.
- When authoring user needs, requirements, or architecture content, cross-reference the shared `input-analysis/` sources rather than duplicating them.
- `_Demo sample data — not for clinical use._` — PDLC_DEMO is a demonstration project. Fabricated clinical data and placeholder analyses are acceptable but must be marked clearly.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-13 | BX | Initial version — created during task 007 P6 reorg from PDLC_DEMO's original flat layout into `dhfs/pca-device/`. |
