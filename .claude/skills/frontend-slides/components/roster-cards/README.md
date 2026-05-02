---
name: roster-cards
cluster: catalog-cohort
purpose: Cohorts of *people* rendered as initials-medallion + name + role + one-liner — replaces card-grid for KOL / team / advisor lists.
favors:
  is_person_cohort: 1.0
  homogeneous_cohort: 0.4
requires: [is_catalog_table, is_person_cohort]
forbids: []
status: new-v0.4
---

## When to use

When the catalog represents people: KOL advisors, investigator teams, board, team rosters. The initials medallion + role line reads as a person-card, not a fact-card.

## Source shape

```markdown
### 2.2 KOL persona advisors

| Advisor | Capability |
|---|---|
| `dr-okafor-anesthesia` | PACU & post-op pain anesthesiologist |
| `dr-shah-icu` | Critical-care intensivist |
```

## Gotchas

- Detects "person-ness" via name patterns: `Dr.`, `dr-foo`, `nurse-bar`, two-word capitalized names. False positives on non-person cohorts (e.g., devices) fall back to `catalog-mosaic`.
- Initials are derived from the rightmost capitalized token in the name.
