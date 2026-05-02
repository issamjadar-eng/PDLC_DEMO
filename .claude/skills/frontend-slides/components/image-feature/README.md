---
name: image-feature
cluster: long-form-prose
purpose: Hero image on the right + prose/bullets on the left — the "screenshot tour" pattern.
favors: {}
requires: [has_image]
forbids: []
status: existing
---

## When to use

When a `### N.M Subsection` (or H2 body) contains a single `![alt](path)` image block on its own line, alongside prose or bullets. Ideal for screenshot walkthroughs, architecture diagrams, photo accompanying narrative.

## Source shape

```markdown
## 5. What's Next

![Console landing](assets/project-overview/console-01-landing.png)

The next 90 days focus on closing the Q-Sub package…

- Lock the predicate-comparison table by week 4.
- Submit Q-Sub package by week 8.
```

## Gotchas

- Images with `max-height: min(50vh, 400px)` are the hard ceiling — large diagrams will be downscaled.
- For *galleries* of multiple screenshots, prefer the v0.4 `gallery-grid` variant.
- The `has_image` feature gate is structural, not a feature score — the section either has an image block or it doesn't.
