# Risk Strategy

<!-- Status: awaiting-content -->
<!-- Domain: risk -->

> This strategy document is awaiting its first assembly.
> Tag strategy decisions in task documents with:
> `<!-- STRATEGY CONTENT: risk, your-topics-here -->`
> Then run `/strategy assemble risk` to generate this document.

## What Belongs Here

- ISO 14971 risk management approach and acceptability criteria (ALARP)
- Platform-level hazard chains and cross-component risk controls
- Risk/benefit determination approach
- Production and post-production information loop
- How cybersecurity risk (IEC 81001-5-1) feeds into overall risk
- FMEA scoping and granularity choices

Per-component nuance is expressed as level-3 callout subsections under each topic (`### PCA Device`, `### Connectivity Adapter`, `### Cloud Suite`).

## Plans This Informs

| Formal Plan | DHF | Relationship |
|------------|---------|-------------|
| Risk Management Plan | each DHF | Scope, criteria, review cadence |
| Hazard Analysis | each DHF | Identification approach, severity/probability framework |
| FMEA | each DHF | Granularity, functional boundaries |
| Risk-Benefit Report | pca-device (lead) | Overall benefit/risk determination |

## How to Contribute

1. Add `## Risk Strategy` to your task document
2. Tag it: `<!-- STRATEGY CONTENT: risk, your-topics -->`
3. Write decisions with per-component callouts where relevant
4. Run `/strategy assemble risk` when ready to regenerate this document
