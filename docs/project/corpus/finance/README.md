# Corpus domain — `finance/`

_Demo sample data — not for clinical use._

Datasets consumed by the **Finance** business domain (`docs/project/finance/`, the second
domain of the commercial-skill answer engine). Every dataset here is **internal and
demo-fabricated** by a seeded generator (`gen.py`, seed 42, no clocks, as-of 2026-08-31),
standing in for an ERP / GL / service-system export. Each generator's narrative knobs
are listed honestly in the dataset README and **proven at acquire/validate** by a
dataset-local `check_knobs.py` on the corpus `asserts.command` seam, so a knob cannot
drift silently. Finance questions also cite `commercial/*` datasets (financials, fleet,
complaints) — cross-domain reuse is free under the shared corpus root.

## Structure

| Dataset | Grain | Stands in for | Consumers |
|---|---|---|---|
| `internal-standard-costs/` | quarter × line × revenue type | ERP standard-cost roll-up (material / labor / overhead) | FQ-01 (roadmap FQ-02) |
| `internal-warranty-claims/` | per claim | service-management / warranty-claims export | FQ-03 (roadmap FQ-04) |
| `internal-gl-budget/` | month × function × cost center | GL / FP&A budget-vs-actual export | FQ-08 (roadmap FQ-05, FQ-10) |
| `internal-ar-inventory/` | month × region × channel × line | ERP AR-aging + inventory-valuation export | FQ-06 (roadmap FQ-07) |

## Expected Content

- `<dataset>/dataset.yml` — acquisition / normalize / schema / asserts config (hand-edited)
- `<dataset>/gen.py` — seeded deterministic generator (banner-stamped JSON raw export, CSV normalize)
- `<dataset>/check_knobs.py` — narrative-knob assert on the `asserts.command` seam
- `<dataset>/snapshots/YYYY-MM-DD/` — engine-written, **immutable**
- `<dataset>/latest` — pointer file (engine-written)

## Conventions

- **Never hand-edit anything under `snapshots/`** — re-acquire instead
  (`python3 .claude/skills/corpus/scripts/corpus.py acquire finance/<dataset>`; use
  `--dry-run` while iterating on a generator).
- Coherence with `commercial/internal-financials` is a locked anchor: product lines,
  revenue types, unit prices and the FY2025 ~$80.5M revenue model are reused (copied
  blocks are marked "keep in sync"; the standard-costs knob check reads the financials
  snapshot directly and fails on divergence).
- Every generator stamps the demo banner into its raw export; the banner never appears
  as a CSV row.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-09-08 | BX / AI Assistant | task 118: reference-audit fixes — FQ-05 added to gl-budget roadmap consumers |
| 2026-09-08 | BX / AI Assistant | task 118: domain folder created with four internal datasets (standard costs, warranty claims, GL budget, AR/inventory), each with a seeded generator, schema + enum asserts, and a knob-proving command assert. |
