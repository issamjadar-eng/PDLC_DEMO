# Clinical

Clinical evidence for this sub-DHF — evaluation plans, benefit-risk analyses, and literature search results that establish and maintain the clinical basis for the device's intended use. Per MDCG 2020-6 / 2020-13 for EU and FDA guidance on clinical evaluation and benefit-risk determinations.

## Subfolders

| Folder | Purpose |
|--------|---------|
| `evaluation-plans/` | Clinical evaluation plans (CEPs) — the prospective plan for gathering and appraising clinical evidence for this device and its intended use |
| `benefit-risk/` | Benefit-risk analyses (BRAs) tying the clinical evidence to the device's risk profile and intended use. Feeds into risk-management and submission content |
| `literature-search/` | Systematic literature search strategies, PRISMA diagrams, evidence tables, inclusion/exclusion rationale |

## Relationship to other folders

```
design-controls/user-needs/  →  clinical/evaluation-plans/   (user needs motivate what clinical evidence is needed)
clinical/literature-search/   →  clinical/benefit-risk/       (evidence feeds the BRA)
clinical/benefit-risk/        →  risk-management/             (BRA informs risk acceptability decisions)
clinical/evaluation-plans/    →  postmarket/pmcf-plans/       (CEP identifies which questions remain for PMCF)
```

## Conventions

- **CEP-NNNN.md** for evaluation plans (e.g., `CEP-1001.md`)
- **BRA-NNNN.md** for benefit-risk analyses
- **LSS-NNNN.md** for literature search strategies/results
- Each document should cite the source: FDA guidance, MDCG guidance, or internal SOP that governs its structure
- When a CEP is updated, the BRA that depends on it should be revisited and the changelog should note whether conclusions change

## For Claude

- When drafting clinical content, check `docs/external/fda-guidance/` for applicable clinical evaluation guidances first
- Cross-reference user needs in `design-controls/user-needs/` — the CEP should address evidence for each claimed use
- Flag any clinical evidence gap that would affect a 510(k) substantial equivalence argument or a BRA conclusion
- Do not fabricate clinical data or literature citations. Use `[VERIFY]` markers for content that needs source validation

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init or add-sub-dhf |
