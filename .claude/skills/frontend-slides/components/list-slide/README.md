---
name: list-slide
cluster: long-form-prose
purpose: Plain bullet list — items rendered with custom bullet glyphs, optional lead paragraph above.
favors:
  enumerative: 0.3
requires: []
forbids: []
status: existing
---

## When to use

Bullet list where fewer than half the items start with `**bold**`. The "default" list rendering — straightforward enumeration without per-item visual weight.

## Source shape

```markdown
### 5. What's Next

- Lock the predicate-comparison table by week 4.
- Submit Q-Sub package by week 8 with FDA pre-feedback target by week 12.
- Begin formative HF testing against the production touchscreen prototype in week 10.
```

## Gotchas

- Lists with date/quarter prefixes ("week 4", "Q1 2026") often score better as v0.4 `timeline-horizontal` — md-deck's classifier should propose timeline as a candidate.
- Six-item cap; >6 splits into continuation slides per density rules.
