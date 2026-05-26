---
name: before-after
cluster: time-sequence
purpose: Exactly two states rendered side-by-side with a delta marker between — "then vs now", "without vs with", baseline vs improved.
favors:
  bipolar: 0.6
  ratio_comparison: 0.4
  numeric: 0.3
requires: []
forbids: []
status: new-v0.4
---

## When to use

When the section reads as a transformation: a baseline, a change, an outcome. Strongest when there's a quantified delta between the two states.

## Source shape

```markdown
### 4.2 What we measured

> equivalent compliance documentation in 38% of the calendar time of the
> previous baseline, with reviewer-flagged correctness defects down 21%.
```

The renderer extracts the two states from the prose (baseline vs agentic-console run) and the delta from the percentage.

## Gotchas

- Falls back to splitting the lead paragraph in half when no clear two-state structure is detectable. For ambiguous content, the user is better served by `versus-split` (also bipolar but no temporal arrow).
