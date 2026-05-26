---
name: quote-slide
cluster: emphasis-atmosphere
purpose: Single short blockquote rendered as the slide's hero element, optional attribution line.
favors:
  declarative_short: 0.6
requires: []
forbids: []
status: existing
---

## When to use

When a `### N.M Subsection` body is dominated by a `> blockquote`. Restrained type, no surrounding bullets — the quote *is* the slide.

## Source shape

```markdown
### 4.2 What we measured

> The 12 weeks of structured authoring with the agentic console produced
> equivalent compliance documentation in 38% of the calendar time of the
> previous baseline, with reviewer-flagged correctness defects down 21%.

We attribute the speed gain to template execution…
```

## Gotchas

- Long quotes (>3 lines on viewport) feel cramped. For oversized "this is the takeaway" quotes consider the v0.4 `huge-pull-quote` (oversized type, no scaffolding) or `big-stat` (when the quote *contains* a single dominant number).
- The trailing prose after the quote becomes a small lead caption; ≥2 paragraphs of prose after the quote should split into a continuation slide.
