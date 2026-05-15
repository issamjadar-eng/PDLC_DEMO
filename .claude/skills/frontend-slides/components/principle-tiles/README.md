---
name: principle-tiles
cluster: emphasis-atmosphere
purpose: Dense card-grid → low-text icon grid. Each principle becomes an icon + short label tile, dropping the verbose subtitles.
favors:
  factual_density: 0.6
  declarative_short: 0.3
requires: []
forbids: []
status: existing
---

## When to use

When a card-grid has ≥4 dense bullets, this variant strips most of the body text and surfaces icon + short-label tiles — high recognition, low reading load.

## Source shape

Same source as `card-grid` (bold-led bullets) — emitted as a sibling visual variant, especially when the labels are short and self-explanatory.

```markdown
### 3.2 Engineering principles

- **Strong defaults, escape hatches second.** The shipped path solves 80%; advanced flags exist but are quiet.
- **One source of truth per concern.** No config sprawl across env, files, and CLI for the same setting.
- **Observability is product.** Every user-visible action emits a structured event.
- **Reversible deploys.** Anything we ship today must be safe to roll back tomorrow.
```

(Principle-tiles render as a 4–6-tile icon grid, one per principle. Examples in other domains: design tenets for a product team, investment theses for a fund deck, lean-manufacturing pillars, brand pillars for a marketing review, regulated-industry quality-system anchors.)

## Gotchas

- Best when each tile reads as a *principle* (a thing to remember) rather than a *fact* (a thing to look up). For factual cards-grids prefer the parent `card-grid`.
- Icons come from the 144-icon repository (`icons.py`); unmapped labels get hash-keyed fallback so every tile has visual variety.
