---
name: concept-canvas
cluster: cause-explanation
purpose: Teaching layout — central concept anchored on the slide with 4 supporting facets surrounding it.
favors:
  definitional: 0.7
requires: []
forbids: []
status: existing
---

## When to use

When the title contains teach-keywords: "what an", "what is", "what are", "where the", "how it works", "actually is". Reframes a definition / mental-model section into a center-and-spokes diagram.

## Source shape

```markdown
### 1.1 What Atlas actually is

Atlas is a multi-tenant data platform for analytics teams…

- Self-service warehouse with row-level access policies
- Connectors for 40+ SaaS sources, ingest tier with at-least-once semantics
- Notebook + dashboard surface, sharable with row-level filters
- Lineage and audit log across every transformation
```

(Concept-canvas is a 2x2 quadrant layout with the lead paragraph + 4 supporting facets. Use it to define a product, a methodology, a strategy, a research finding — anywhere a single concept benefits from "here's the headline + four supporting properties.")

## Gotchas

- Fires on title-keyword today. v0.4's `definitional` feature score broadens the trigger.
- Best when the section has 4 supporting facets — fewer leaves blank quadrants, more truncates.
