---
name: divider-numeral
cluster: title-openers
purpose: Section divider with massive numeral N and the section title — tonal pause between H2 sections.
favors: {}
requires: []
forbids: []
status: existing
---

## When to use

Auto-emitted before each `## N. Section` body. Acts as a section "chapter break" with a big numeric anchor.

## Source shape

```markdown
## 2. Team & KOL Network
```

## Gotchas

- The numeral comes from the `## N.` prefix; sections without one fall back to a numeric placeholder.
- For tonal-shift sections that are not numbered (e.g., a closing reflection), prefer the v0.4 `divider-quote` or `ambient-divider` components.
