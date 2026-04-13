# Clinical Benefit-Risk Analyses

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project (anchor product: PP3500 / PainEase PCA Advanced)._

Clinical benefit-risk analyses (BRAs) document the clinical determination of whether the benefits of the PP3500 outweigh its residual risks for the intended use and patient population. These are **clinical** determinations and feed the ISO 14971 risk file rather than replacing it: the ISO 14971 hazard analysis, FMEA and risk-management report live in `../../design-controls/risk-management/` and reference the BRAs in this folder when establishing overall residual-risk acceptability.

## Current Contents

| File | Summary |
|---|---|
| `BRA-1001.md` | Comprehensive BRA — Level 1 RCT evidence, 12 risks, 0 unacceptable |
| `BRA-1002.md` | Initial BRA for new device version, pivotal-trial-substantiated |
| `BRA-1003.md` | Comprehensive BRA emphasising battery and alarm hazards |
| `BRA-1004.md` | PMA-style BRA with mechanical and software risk emphasis |
| `BRA-1005.md` | Periodic update BRA, post-market data integrated |

## Conventions

- File naming: `BRA-NNNN.md`.
- All BRAs use frontmatter `doc_type: benefit-risk-analysis`.
- Each BRA cites the ISO 14971 risk file row(s) it depends on.
- Demo banner mandatory.

## Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-04-12 | clinical ingestion | Initial README; 5 BRAs ingested with frontmatter and demo banner. |
