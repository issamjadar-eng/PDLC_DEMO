---
name: prose-slide
cluster: long-form-prose
purpose: Paragraph-only section rendered as flowing prose, max-width 80ch, no bullets or cards.
favors: {}
requires: []
forbids:
  enumerative
status: existing
---

## When to use

When a `### N.M Subsection` body has only paragraphs — no bullets, no table, no quote, no image. The "explanatory text" rendering.

## Source shape

```markdown
### 1.1 What Atlas actually is

Atlas is a multi-tenant data platform for analytics teams with a notebook
surface, a connector library, and an at-least-once ingest tier…

The "real-time" framing in early marketing is misleading: Atlas has a
streaming connector path, but the warehouse-side materialization remains
batch on a 5-minute cadence…
```

(Prose-slide is for a section that's genuinely paragraph-shaped — definitional, narrative, or argumentative content that doesn't decompose to bullets cleanly. Use it for an executive summary, a research-finding narrative, a strategy rationale, or any paragraph that needs to read as prose, not a list.)

## Gotchas

- Long prose (>3 paragraphs) doesn't auto-split today; v0.4 `dense-prose-split` will solve this with running-header continuation.
- Sections with a single oversized one-liner often deserve `mic-drop` (v0.4); md-deck's classifier should propose both.
