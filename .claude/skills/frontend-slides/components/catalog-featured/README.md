---
name: catalog-featured
cluster: catalog-cohort
purpose: 3 featured cards from a catalog + chip-cohort of remaining names — "the headliners + the rest" pattern.
favors:
  homogeneous_cohort: 0.7
  factual_density: 0.3
requires: [is_catalog_table]
forbids: []
status: existing
---

## When to use

Auto-emitted alongside `catalog-mosaic` for ≥6-row catalogs. Surfaces the first three rows as detail cards and bundles the remaining rows as a chip cohort below — useful when the cohort has natural headliners (board-roster, top-3 partners, primary-investigator highlight).

## Source shape

Same source as `catalog-mosaic` — both variants are emitted; user picks via candidates UI in v0.4+.

## Gotchas

- The "first three" are taken in source-order. If the source author wants to control the headliners, sort the table accordingly.
- For pure-equality cohorts (no natural headliners), the mosaic is usually the better pick.
