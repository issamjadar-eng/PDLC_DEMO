# Component Library

A library of slide-rendering components organized by **rhetorical cluster** — what the slide is *for*, not what shape its data has. Consumed by both `frontend-slides` (the interactive style-discovery wizard) and `md-deck` (the markdown-pipeline builder, via its 3-variant rational selection in v0.4+).

## Component contract

Every component lives in its own folder: `components/<name>/`.

Required files:

- `README.md` — frontmatter (machine-readable) + body prose (when-to-use, source-shape example, gotchas).

Optional:

- `component.css` — CSS partial scoped to selectors used only by this component. If absent, the component's CSS still lives in the legacy monolithic preset (e.g., `presets/bold-signal.css`); extraction is incremental.
- `examples/` — hand-labeled fixtures: a `<example-name>.md` source snippet plus an `<example-name>.html` that the component would render. Used by md-deck's classifier unit tests.

## Frontmatter schema

```yaml
---
name: <kebab-case unique id, matches folder>
cluster: <one of: title-openers · single-takeaway · time-sequence · comparison ·
                  composition-breakdown · cause-explanation · catalog-cohort ·
                  process-handoff · risk-safety · calls-to-action · long-form-prose ·
                  emphasis-atmosphere>
purpose: <one-sentence "what this slide is for">
favors:
  <feature_name>: <weight 0–1>
  <feature_name>: <weight 0–1>
requires: [<feature_name>, ...]      # if absent feature, component is non-viable
forbids:  [<feature_name>, ...]      # optional veto features
status: <existing | new-v0.4>
---
```

**Features** are 0–1 scores produced per-section by `md-deck/scripts/classify.py` (added in PR 2). Initial feature set: `temporal`, `numeric`, `bipolar`, `enumerative`, `homogeneous_cohort`, `declarative_short`, `definitional`, `hierarchical`, `factual_density`, `ratio_comparison`. New features can be added but require the scorer to publish them.

## Clusters (12)

1. **title-openers** — title and section dividers
2. **single-takeaway** — one-idea slides (mic-drop, big-stat, huge-pull-quote, binary-card)
3. **time-sequence** — timelines, phase stacks, gantt strips, before-after
4. **comparison** — versus splits, delta tables, check-cross grids, dimensions radar
5. **composition-breakdown** — bar charts, donuts, treemaps, sankeys
6. **cause-explanation** — concept canvas, because-therefore, iceberg, bowtie
7. **catalog-cohort** — catalog mosaic, catalog featured, gallery grid, roster cards
8. **process-handoff** — handoff relay, swimlane, loop diagram
9. **risk-safety** — hazard-control chain, threat-mitigation pair (medtech idioms)
10. **calls-to-action** — what's next, ask card, manifesto tiles
11. **long-form-prose** — prose with pullouts, paragraph with figure, dense prose split
12. **emphasis-atmosphere** — kicker card, principle tiles, ambient divider

## Status of v0.4 rollout

| PR | Components added |
|---|---|
| PR 1 (scaffolding) | 15 existing types catalogued: title, agenda, divider, table, card-grid, list, quote, prose, image-feature, catalog-mosaic, catalog-featured, scope-iceberg, concept-canvas, handoff-relay, principle-tiles |
| PR 3 (first wave) | big-stat, mic-drop, timeline-horizontal, phase-stack, before-after, versus-split, bar-chart, roster-cards |
| PR 5 (second wave) | binary-card, because-therefore, delta-table, check-cross-grid, donut, swimlane, whats-next, manifesto-tiles, huge-pull-quote, dense-prose-split, bowtie, threat-mitigation-pair |

Total target: 35 components.
