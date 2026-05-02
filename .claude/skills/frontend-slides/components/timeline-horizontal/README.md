---
name: timeline-horizontal
cluster: time-sequence
purpose: Dated milestones rendered as a horizontal baseline with dot-and-stem markers — temporal sequence as a line, not a list.
favors:
  temporal: 1.0
  enumerative: 0.2
requires: [temporal]
forbids: []
status: new-v0.4
---

## When to use

When bullets or rows carry explicit temporal markers (week N, Q1, 2026-Q2, dates). The line communicates "these happen in order" much more strongly than a bulleted list.

## Source shape

```markdown
### 5. What's Next

- Lock the predicate-comparison table by week 4.
- Submit Q-Sub package by week 8 with FDA pre-feedback target by week 12.
- Begin formative HF testing against the production touchscreen prototype in week 10.
- Open the post-market data plan with the four investigator sites by week 14.
```

## Gotchas

- Sorts items by detected time-token when possible; when no tokens exist on an item, source-order is preserved.
- Up to 6 items per slide; >6 splits into continuation timelines.
