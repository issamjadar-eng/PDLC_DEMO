---
name: bar-chart
cluster: composition-breakdown
purpose: Categories with values rendered as drawn CSS bars — no chart library, just labels + percent-width bars + value labels.
favors:
  numeric: 0.7
  ratio_comparison: 0.4
requires: []
forbids: []
status: new-v0.4
---

## When to use

When the section's bullets each contain a numeric value (`%`, `$N`, `Nx`). Inspired by agentic-delivery's `bar-col`/`workmix-bar` treatment.

## Source shape

```markdown
### 4.2 What we measured

- v1 baseline · 100%
- v2 with agents · 38%
- Defect rate · 79% (down 21%)
```

## Gotchas

- Values are auto-normalized so the largest fills the bar; smaller bars proportional. If the source doesn't carry numbers, the component is non-viable (drops out of candidate scoring).
- Best for 3–6 bars; >6 splits.
