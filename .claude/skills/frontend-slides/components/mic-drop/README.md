---
name: mic-drop
cluster: single-takeaway
purpose: One short declarative sentence, oversized, centered on the slide with ample whitespace — the "leave them with this" pause.
favors:
  declarative_short: 0.8
requires: []
forbids:
  factual_density
status: new-v0.4
---

## When to use

When the section's content is a short, punchy claim — the joke that lands stronger than an exposition. Strongest for closing slides, transition pauses, and reframings.

## Source shape

A single short paragraph or quote, ≤25 words:

```markdown
### 1.1 What Atlas actually is

Atlas has streaming connectors, but the materialization tier is still batch.
```

## Gotchas

- Picks the shortest sentence in the lead/quote/first paragraph as the hero line. Multiple short sentences → the first one wins.
- Avoid for sections with bullets — the visual contract is "no scaffolding, just one line."
