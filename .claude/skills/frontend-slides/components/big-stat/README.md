---
name: big-stat
cluster: single-takeaway
purpose: One number + one label + one supporting line — oversized number as the slide hero, restrained surrounding type.
favors:
  numeric: 0.5
  ratio_comparison: 0.6
  declarative_short: 0.4
requires: []
forbids: []
status: new-v0.4
---

## When to use

When a section's punchline *is* a number ("38% reduction in nuisance alarms") and everything else on the slide is supporting context. Most powerful for results / measurements / key metric reveals.

## Source shape

A short paragraph or quote where one number dominates:

```markdown
### 4.2 What we measured

> The 12 weeks of SP6500 design-input authoring with the agentic console produced
> equivalent IEC 62304 documentation in 38% of the calendar time of SP6000's
> equivalent phase.
```

## Gotchas

- Picks the first percentage / `$X` / `Nx` token from the lead/quote/first paragraph as the hero number. Authors who want a specific number to be the hero should put it first.
- Falls back gracefully when no extractable number is present (renders as oversized declarative).
