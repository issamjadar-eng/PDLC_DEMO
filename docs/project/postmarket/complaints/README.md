# Complaints

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project (anchor product: PP3500 / PainEase PCA Advanced)._

Customer complaints ledger for the PP3500. In a production QMS the ledger would be a live view sourced from a complaint handling system (Trackwise, Veeva Vault QMS, ServiceNow), with each row backed by a full complaint investigation file. The ledger here is a static demo artefact — it captures the same shape of data so the customer-insights agent can join complaints to CAPAs, PMCF data and KOL feedback.

## Current Contents

| File | Summary |
|---|---|
| `complaints-ledger.md` | PP3500 complaints ledger 2022–2025, 27 rows including 12 decimal-point complaints linked to CAPA-2023-001 |

## Conventions

- File naming: `complaints-ledger.md` (single rolled-up file for the demo).
- Frontmatter `doc_type: complaints-ledger`.
- Severity uses GlobalLogic post-market surveillance scale: `low`, `medium`, `high`, `near-miss`.
- Demo banner mandatory.

## Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-04-12 | postmarket ingestion | Initial README; complaints-ledger.md synthesised for the demo. |
