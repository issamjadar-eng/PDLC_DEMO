---
name: title-cover
cluster: title-openers
purpose: Standard cover slide — H1 title, lead paragraph, and a meta key/value block (Program / Path / Last updated, etc.).
favors:
  declarative_short: 0.3
requires: []
forbids: []
status: existing
---

## When to use

The first slide of a deck. md-deck always emits this for the first H1 + paragraph + `**Foo:** bar` meta lines in a source.

## Source shape

```markdown
# Atlas — Platform Overview

**Program:** Atlas Platform v1.0 — multi-tenant data platform for analytics teams
**Reference release:** Atlas v0.9 (internal preview, 2025-Q4)
**Last updated:** 2026-05-01

This document is the program-level view of the Atlas v1.0 launch…
```

(Title-cover renders your H1 + a small key-value strip + a leading paragraph. Use it for product launches, program kickoffs, board briefings, conference talks, internal training intros — anywhere a deck needs a strong first slide with framing metadata.)

## Gotchas

- A title **without** a lead or meta block falls back to `title-statement` (PR 3 component). Don't author bare H1s expecting this to render gracefully.
- Long lead paragraphs (>60 words) get truncated visually; consider splitting into a follow-up slide instead.
