# Post-Market

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project (anchor product: PP3500 / PainEase PCA Advanced)._

The post-market branch is the ongoing customer feedback loop for the PainEase PCA Advanced (PP3500): post-market clinical follow-up plans and studies, CAPAs, and the complaints ledger. Together these artefacts close the loop between the field experience of the device and the upstream design controls and clinical evaluation. The forthcoming **customer-insights agent** ingests this branch, joins it with KOL feedback (`../input-analysis/kol-feedback/`) and market research, and proposes design-input updates and risk-file changes.

## Current Contents

| Path | Purpose |
|---|---|
| `pmcf-plans/` | PMCF plans (PMCF-1001 … PMCF-1005) per MDR Article 83 / Annex XIV Part B |
| `pmcf-studies/` | PMCF study records (STUDY-0001, 0003, 0005, 0007, 0009) |
| `capa/` | Customer-facing CAPA records that tie into design control remediation |
| `complaints/` | PP3500 complaints ledger sourced from the complaint handling system |

## Conventions

- All documents in this branch carry the standard YAML frontmatter (doc_type, device_ids, patient_populations, care_settings, therapy_context, evidence_grade, primary_endpoints, related_user_needs, related_design_inputs, status, last_updated).
- Demo banner on line 3 of every leaf document.
- CAPA records here are the customer-facing subset; internal QMS CAPAs (e.g., supplier nonconformance) live in the QMS, not in this branch.

## Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-04-12 | postmarket ingestion | Initial README; postmarket branch overview, contents and customer-insights agent reference. |
