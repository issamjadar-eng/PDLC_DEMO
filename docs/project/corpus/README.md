# Corpus — versioned evidence grounding

This tree is the project's **grounding data tier**, managed by the `corpus` skill.
Datasets live at `<domain>/<dataset>/` as **immutable dated snapshots** — raw byte-pinned
payloads, schema-validated normalized CSV, and a `provenance.yml` hash chain from every
normalized value back to its source. Where needed data does not exist, a first-class
assumption record (`assumptions/A-NNN.yml`) states the estimate and its method — analyses
cite either a `dataset@snapshot` or an `A-NNN`, never an unsourced figure.

## Structure

| Folder | Purpose |
|--------|---------|
| `commercial/` | Datasets consumed by the commercial analytics tier — external real data (openFDA 510(k)/recalls/MAUDE incl. PCA-scoped, curated competitor feature matrix) + internal demo-fabricated operations data (fleet, complaints, upgrade campaign, financials, revenue plan, accounts, win/loss, subscriptions, telemetry, regulatory docket, signal register, KOL register). Roster + freshness: `corpus.py list` |

## Expected Content

- `<domain>/<dataset>/dataset.yml` — acquisition/normalize/schema config (hand-edited)
- `<domain>/<dataset>/snapshots/YYYY-MM-DD/` — engine-written, **immutable**
- `<domain>/<dataset>/assumptions/A-NNN.yml`, `waivers/W-NNN.yml` — scaffolded via the
  skill's `assume` / `waive` actions, then hand-completed
- `<domain>/<dataset>/latest` — pointer file (engine-written)

## Conventions

- **Never hand-edit anything under `snapshots/`** — hashes are pinned in
  `provenance.yml`; `validate` treats a mismatch as tampering. Re-acquire instead.
- All operations go through the skill: `python3 .claude/skills/corpus/scripts/corpus.py
  {init|acquire|refresh|validate|diff|check|list|assume|waive}`.
- External datasets hold **real acquired data** (e.g. openFDA — public domain). Internal
  datasets (`internal: true`) are demo-fabricated by seeded generators and must carry the
  `_Demo sample data — not for clinical use._` banner in their outputs.
- Respect `usage_rights` recorded in provenance: licensed payloads are not redistributed.
- Freshness: each dataset declares `max_age_days`; `check` fails on stale data without an
  unexpired waiver.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-07-27 | BX / AI Assistant | task 108 full-catalog run: +10 datasets (7 internal generators, 1 real openFDA PCA-MAUDE, curated competitor features, KOL register); complaints extended with over-delivery / pca-by-proxy signal categories (severity convention corrected to 3=severe same day); Structure row updated to point at `corpus.py list` as the roster. |
| 2026-07-22 | BX / AI Assistant | task 108: corpus root scaffolded (corpus skill v1) — data tier for the commercial analytics suite; no datasets yet. |
