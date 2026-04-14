# pca-device

DHF root for **pca-device** — the Design History File record for the PainEase PCA Advanced (PP3500) patient-controlled analgesia pump. This is the DHF anchor for PDLC_DEMO's lead product and the first DHF in the project's `dhfs[]` list.

**Regulatory status**: `in-development` — on track for 510(k) filing, predicate PP3000 (K190567), target clearance under K210345.

**Filing rollup**: `510k` — rolls up into `docs/project/submissions/510k/`. Composition manifest (when authored) will list which artifacts from this DHF are included in the PP3500 510(k) submission.

## Structure

| Folder | Purpose |
|--------|---------|
| `design-controls/` | User needs, requirements, architecture, V&V, trace matrix, plans, tool validation — ISO 13485 / 21 CFR 820.30 design control record for PP3500 |
| `clinical/` | Clinical evaluation plans, benefit-risk analyses, literature search results |
| `postmarket/` | PMCF plans and studies, CAPA, complaints — post-market surveillance for PP3500 |
| `risk-management/` | ISO 14971 hazard analysis, FMEA, risk-benefit. Sibling of `design-controls/`, not a child |
| `cybersecurity/` | IEC 81001-5-1 assessment, threat model, SBOM, vulnerability management |

PDLC_DEMO's broader 5-device infusion portfolio (IP5000, PP3000, PP3500, SP6000, SP6500) is retained as **portfolio and predicate context** under the shared `docs/project/input-analysis/predicate-analysis/`, not as separate DHFs. Companion DHFs in this project (`connectivity-adapter`, `cloud-suite` and its child platform DHFs) live as siblings under `docs/project/dhfs/`; they share strategies, input analysis, and submissions plumbing with `pca-device`.

## Relationship to shared project content

| Shared source | How pca-device uses it |
|---|---|
| `docs/project/input-analysis/predicate-analysis/` | PP3000 predicate evaluation, portfolio positioning |
| `docs/project/input-analysis/kol-feedback/` | KOL input informing user needs |
| `docs/project/input-analysis/market-research/` | Market landscape, unmet needs |
| `docs/project/input-analysis/competitive-landscape/` | Competitive positioning |
| `docs/project/strategies/` | All eight shared strategy briefs (regulatory, architecture, development, testing, risk, postmarket, commercial, operations) — upstream of every per-DHF formal output. PCA-specific nuance lives as `### PCA Device` callouts inside each brief. |
| `docs/external/standards/` | IEC 62304, ISO 14971, IEC 62366-1, IEC 81001-5-1, etc. |
| `docs/external/fda-guidance/` | 510(k) SE, cybersecurity, PCCP, SW changes, SW functions guidances |
| `docs/internal/source/` | Corporate SOPs governing how DHF work is executed |
| `docs/project/submissions/510k/` | Target filing — 510(k) for PP3500 |

## Conventions

- **One DHF = one component = one regulatory story.** Keep per-DHF content narrowly scoped to PP3500. Portfolio-level content (market research, portfolio predicate analysis, cross-component strategy) belongs at `docs/project/` root under `input-analysis/` or `strategies/`, not here.
- **Cross-references** to the broader portfolio live in `design-controls/user-needs/` (traceability back to portfolio-level user needs) and `docs/project/input-analysis/predicate-analysis/` (comparison against PP3000 predicate).
- When capturing strategy content from PCA work, tag with `<!-- STRATEGY CONTENT: <domain>, topics -->` and write a `### PCA Device` callout under the relevant topic. All strategy domains are `shared` (v10+); the deprecated `dhf=pca-device` scope key is unnecessary.

## For Claude

- When working inside `dhfs/pca-device/`, treat PP3500 as the device of record. Other devices in the portfolio (IP5000, PP3000, SP6000, SP6500) are context and predicates, not design targets.
- When authoring user needs, requirements, or architecture content, cross-reference the shared `input-analysis/` sources rather than duplicating them.
- `_Demo sample data — not for clinical use._` — PDLC_DEMO is a demonstration project. Fabricated clinical data and placeholder analyses are acceptable but must be marked clearly.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-13 | BX | Initial version — created during task 007 P6 reorg from PDLC_DEMO's original flat layout into `dhfs/pca-device/`. |
| 2026-04-13 | BX | task 009: pointed at full shared `strategies/` set, dropped stale "future DHFs" note, refreshed strategy-tag convention to v10 shared form. |
