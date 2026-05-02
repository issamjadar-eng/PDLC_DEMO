---
name: table-slide
cluster: composition-breakdown
purpose: Tabular data with header row + body rows — for reference data, comparisons, and parameter lists that must stay tabular.
favors:
  hierarchical: 0.2
  factual_density: 0.5
requires: []
forbids:
  declarative_short
status: existing
---

## When to use

When the source uses an actual GFM table (not a bulleted list of pairs). Tables ≥6 rows trigger automatic catalog-mosaic + catalog-featured variant emission instead.

## Source shape

```markdown
### 4.1 Where the handoff actually happens

| Actor | Stage |
|---|---|
| Human · PM | Drafts the task brief and the success criteria |
| Agent · skill | Executes the structural authoring |
```

## Gotchas

- For 2-column tables that read as "category → value", consider the v0.4 `delta-table` variant.
- Tables with ≥6 rows automatically split into mosaic pagination — no manual handling needed.
