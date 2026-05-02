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
### 3.2 Quality system anchors

- **ISO 13485 design controls** govern every input → output → V&V → risk trace.
- **IEC 62304 enhanced documentation** required for Class C SaMD.
- **ISO 14971 risk management file** integrated into the trace matrix.
- **21 CFR 820 compliance** carries the QMS evidence chain end-to-end.
```

## Gotchas

- Best when each tile reads as a *principle* (a thing to remember) rather than a *fact* (a thing to look up). For factual cards-grids prefer the parent `card-grid`.
- Icons come from the 144-icon repository (`icons.py`); unmapped labels get hash-keyed fallback so every tile has visual variety.
