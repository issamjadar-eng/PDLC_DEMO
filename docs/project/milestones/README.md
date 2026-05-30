# `docs/project/milestones/` — Milestone Catalog

YAML catalog of program milestones consumed by `/tracker` (`engineering.yml`, `regulatory.yml`) and indirectly by `/dhf-manifest` for filing-scope context. Hand-edited; one entry per milestone.

## Structure

| File | Purpose |
|------|---------|
| `engineering.yml` | Engineering milestones (sprint/release cuts, V&V dry-runs, design-transfer checkpoints). |
| `regulatory.yml` | Regulatory milestones (Q-Sub, 510(k), PCCP cuts, LMR cycles, jurisdictional submissions). |

## Conventions

- One YAML doc per milestone. Required fields: `id`, `name`, `target_date`, `composition` (list of DHFs in scope), `status`, `description`.
- `id` is the stable key used by `/tracker` and `/dhf-manifest` cross-references — do not rename without updating consumers.
- `target_date` uses `YYYY-MM-DD` (absolute, not relative).
- `composition` lists DHF leaf names from `project.yml dhfs[].leaf`. Empty list = system-wide.
- `status` ∈ `planned` | `active` | `complete` | `slipped` | `cancelled`.
- New milestone categories (clinical, business, etc.) get their own yml file alongside the two existing ones; `/tracker generate` enumerates `*.yml` here.

## For Claude

- Adding a new milestone: edit the relevant yml; re-run `/tracker generate` then `/tracker render` so the dashboard reflects it.
- A milestone slip without a phase change is a `status: slipped` + updated `target_date`, NOT a delete + recreate (history matters).
- Read `.claude/skills/tracker/SKILL.md` for the full schema and how composition rows are derived from `composition[]`.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-05-30 | Ben Xavier | Initial scaffold under ben/068 — closes the `/best-practices` audit FAIL for the missing folder README. |
