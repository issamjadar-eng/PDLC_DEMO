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

- Lock the comparison matrix against alternatives by week 4.
- Ship the milestone package by week 8 with stakeholder review target by week 12.
- Begin user-research sessions against the production prototype in week 10.
- Open the post-launch monitoring plan with the partner sites by week 14.
```

## Gotchas

- Sorts items by detected time-token when possible; when no tokens exist on an item, source-order is preserved.
- Up to 6 items per slide; >6 splits into continuation timelines.
