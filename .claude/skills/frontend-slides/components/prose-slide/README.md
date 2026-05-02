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
### 1.1 What SP6500 actually is

SP6500 is a large-volume single-channel IV infusion pump with a 7" capacitive
touchscreen, an on-pump drug library, and a predictive-alarm SaMD module…

The closed-loop title earned in early literature is misleading: SP6500 has
dose-error reduction software, but the prescriber loop remains open…
```

## Gotchas

- Long prose (>3 paragraphs) doesn't auto-split today; v0.4 `dense-prose-split` will solve this with running-header continuation.
- Sections with a single oversized one-liner often deserve `mic-drop` (v0.4); md-deck's classifier should propose both.
