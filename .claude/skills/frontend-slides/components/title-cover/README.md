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
# SP6500 — Smart Pump Program Overview

**Program:** PainEase Smart Pump SP6500 — large-volume IV infusion pump
**Regulatory path:** 510(k) traditional — predicate SP6000 (K200111)
**Last updated:** 2026-05-01

This document is the program-level view of SP6500…
```

## Gotchas

- A title **without** a lead or meta block falls back to `title-statement` (PR 3 component). Don't author bare H1s expecting this to render gracefully.
- Long lead paragraphs (>60 words) get truncated visually; consider splitting into a follow-up slide instead.
