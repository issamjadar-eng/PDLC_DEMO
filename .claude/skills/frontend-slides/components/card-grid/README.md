---
name: card-grid
cluster: emphasis-atmosphere
purpose: Bold-led bullet list rendered as 2×3 / 3×2 cards — each tile has a label (bold lead) + a one-line subtitle.
favors:
  factual_density: 0.5
  enumerative: 0.2
requires: []
forbids: []
status: existing
---

## When to use

When ≥half of the bullets begin with `**Bold Lead**`. The bold prefix becomes the card label, the rest becomes the subtitle. Six-tile cap; >6 splits into continuation slides via v0.3 density-split rules.

## Source shape

```markdown
### 1.2 Filing scope at a glance

- **Filing scope = SP6500 pump + DLM.** The Predictive Alarm Module is out of scope…
- **Critical-requirement carve-out (CtS / CtF / CtP).** Every user need and design input is tagged…
- **PCCP envelope.** The PCCP pre-authorizes formulary updates…
```

## Gotchas

- Mixed lists (some bold-led, some not) under the half-threshold collapse to `list-slide` instead.
- For dense lists where the label *is* the whole point, prefer the v0.4 `principle-tiles` (icon-grid) variant — already auto-emitted on cluster-keyword hits.
