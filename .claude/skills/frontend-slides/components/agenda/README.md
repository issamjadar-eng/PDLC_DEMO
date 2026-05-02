---
name: agenda
cluster: title-openers
purpose: Auto-generated agenda computed from the source's H2 section headings — N labelled tiles in a grid.
favors:
  enumerative: 0.4
requires: []
forbids: []
status: existing
---

## When to use

The second slide of a deck. md-deck always emits this when the source has 2+ `## N. Section Name` H2 headings.

## Source shape

Implicit — built from H2s. Authors do not write this slide directly.

```markdown
## 1. Program at a Glance
...
## 2. Team & KOL Network
...
## 3. Risk & Quality Posture
```

## Gotchas

- Sections without a leading numeral (`## Foo` instead of `## 1. Foo`) are skipped.
- Decks with only one H2 still emit an agenda; consider hiding it for short decks (deferred to v0.4 polish).
