# Postmarket

Post-market surveillance for this DHF — PMCF plans and studies, CAPA records, and complaint ledger. Covers the post-clearance obligations under 21 CFR 820.198 (complaints) and 21 CFR 820.100 (CAPA), and MDCG 2020-7 / 2020-8 for EU post-market clinical follow-up.

The upstream **post-market strategy brief** (PMS approach, maintenance cadence, LMR schedule, PCCP change tracking, cross-component surveillance architecture) lives at `docs/project/strategies/postmarket-strategy.md` — shared across the whole project, with per-component callouts. The files in this folder are the formal outputs that the strategy informs.

## Subfolders

| Folder | Purpose |
|--------|---------|
| `pmcf-plans/` | Post-Market Clinical Follow-up plans — prospective studies to confirm clinical performance and safety in real-world use |
| `pmcf-studies/` | Execution records for PMCF studies — protocols, interim reports, final reports |
| `capa/` | Corrective and Preventive Action records — investigations, root-cause analyses, effectiveness checks |
| `complaints/` | Complaint ledger and adjudicated complaint records |

## Relationship to other folders

```
clinical/evaluation-plans/    →  postmarket/pmcf-plans/       (CEP identifies gaps that PMCF must close)
postmarket/complaints/        →  postmarket/capa/             (complaints feed CAPA investigations)
postmarket/capa/              →  risk-management/             (CAPA outcomes may update hazard analysis)
postmarket/capa/              →  design-controls/             (CAPA may drive design changes tracked through design controls)
postmarket/pmcf-studies/      →  clinical/benefit-risk/       (PMCF results feed benefit-risk re-evaluation)
```

## Conventions

- **PMCF-NNNN.md** for PMCF plans; **STUDY-NNNN.md** for study execution records
- **CAPA-YYYY-NNN.md** — year-prefixed so CAPA records naturally sort chronologically
- `complaints-ledger.md` is the master index; individual complaint files use `YYYY-MM-DD-<short-id>.md`
- Every CAPA record must cross-reference the trigger (complaint, internal audit, trend signal)
- When a postmarket finding triggers a design change, link back to the design-controls file(s) that were revised

## For Claude

- Postmarket records are regulated evidence — do not fabricate complaint content or CAPA findings. Use `[VERIFY]` for anything drafted from hypothetical scenarios
- When drafting a CAPA, ensure the root-cause analysis section is distinct from the corrective action — these are often conflated by AI
- Check `docs/internal/source/` for the organization's CAPA SOP before drafting new records
- Flag any postmarket finding that may require a PCCP update or filing-affecting change

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init or add-dhf |
