# Clinical

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project (anchor product: PP3500 / PainEase PCA Advanced)._

The clinical branch holds the clinical evidence portfolio for the PainEase PCA Advanced (PP3500): the plans for clinical evaluation, the literature search strategies that feed those evaluations, and the clinical benefit-risk determinations that are summarised in the Clinical Evaluation Report. These artefacts inform — and are informed by — design controls (`../design-controls/user-needs/`, `../design-controls/requirements/`) and post-market surveillance (`../postmarket/`).

ISO 14971 hazard analysis, FMEA and the risk file live under `../design-controls/risk-management/`. The clinical benefit-risk determinations under `benefit-risk/` here are an input to that risk file: ISO 14971 references the clinical benefit data summarised here when assessing residual-risk acceptability and overall risk-benefit.

## Current Contents

| Path | Purpose |
|---|---|
| `evaluation-plans/` | Clinical Evaluation Plans (CEP-1001 … CEP-1005) per MDR Annex XIV / MEDDEV 2.7/1 Rev 4 |
| `benefit-risk/` | Clinical benefit-risk analyses (BRA-1001 … BRA-1005) feeding ISO 14971 risk file |
| `literature-search/` | PRISMA-style literature search strategies (LSS-1001 … LSS-1005) |

## Conventions

- Every clinical document carries the YAML frontmatter schema defined for the customer-insights agent (doc_id, doc_type, device_ids, patient_populations, care_settings, therapy_context, evidence_grade, primary_endpoints, related_user_needs, related_design_inputs, status, last_updated).
- All content in this branch is illustrative demo material; controlled clinical deliverables would be authored against SOP-CER-001/SOP-PMCF-001 in a production QMS.
- Demo banner appears on line 3 of every leaf document.

## Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-04-12 | clinical ingestion | Initial README — clinical branch overview, contents and cross-links established. |
