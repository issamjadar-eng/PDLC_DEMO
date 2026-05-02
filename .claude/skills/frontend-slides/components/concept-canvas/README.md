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
### 1.1 What SP6500 actually is

SP6500 is a large-volume single-channel IV infusion pump…

- 7" capacitive touchscreen
- 5,000-entry on-pump drug library
- Predictive-alarm SaMD module
- Dose-error reduction software
```

## Gotchas

- Fires on title-keyword today. v0.4's `definitional` feature score broadens the trigger.
- Best when the section has 4 supporting facets — fewer leaves blank quadrants, more truncates.
