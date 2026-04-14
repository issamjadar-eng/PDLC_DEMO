# CAPA

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project (anchor product: PP3500 / PainEase PCA Advanced)._

Corrective and Preventive Action records that originated from customer-facing post-market signals for the PP3500. CAPAs are formally QMS records — in production they live in the QMS (Trackwise / Veeva) — and the records in this folder are the customer-facing subset that tie back into design control remediation (a new or amended design input, a risk file update, a software release). Internal CAPAs (supplier nonconformance, manufacturing scrap, etc.) live in the QMS and are not mirrored here.

## Current Contents

| File | Summary |
|---|---|
| `CAPA-2023-001.md` | PP3500 decimal-point entry legibility CAPA; opened 2023-01-10, closed 2023-05-15; permanent fix in software v1.3.0; new design input DI-013 |

## Conventions

- File naming: `CAPA-YYYY-NNN.md`.
- Frontmatter `doc_type: capa` with `related_user_needs` and `related_design_inputs` populated.
- Each CAPA must list complaints, FSN, software releases, design control remediation, effectiveness check, and signoff.
- Demo banner mandatory.

## Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-04-12 | postmarket ingestion | Initial README; CAPA-2023-001 synthesised for the demo. |
