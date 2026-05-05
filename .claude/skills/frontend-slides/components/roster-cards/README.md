---
name: roster-cards
cluster: catalog-cohort
purpose: Cohorts of *people* rendered as initials-medallion + name + role + one-liner — replaces card-grid for team / advisor / panel / cohort lists across any domain.
favors:
  is_person_cohort: 1.0
  homogeneous_cohort: 0.4
requires: [is_catalog_table, is_person_cohort]
forbids: []
status: new-v0.4
---

## When to use

When the catalog represents people: advisor panels, team rosters, board, conference speakers, investigator cohorts, expert reviewers. The initials medallion + role line reads as a person-card, not a fact-card.

## Source shape

```markdown
### 2.2 Founding team

| Member | Role |
|---|---|
| `Aisha Okafor` | Co-founder & CEO — product strategy and partnerships |
| `Marcus Shah` | Co-founder & CTO — distributed systems and platform |
| `Lin Park` | Head of Design — research, IxD, brand systems |
```

## Gotchas

- Detects "person-ness" via name patterns: two-word capitalized names; titled prefixes (e.g. `Dr.`, `Prof.`); slug shapes like `name-role`. False positives on non-person cohorts (e.g., products, locations) fall back to `catalog-mosaic`.
- Initials are derived from the rightmost capitalized token in the name.
