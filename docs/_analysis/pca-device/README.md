# `_analysis/pca-device/` — System-Level Analyses

Gap analyses and reference audits scoped to the **`pca-device` system DHF** — the PP3500 system leaf, used for cross-component / system-level / filing-aware critiques (per `project.yml dhfs[]` `role: system`).

## Analyses

| ID | Title | Topic | Status | Owner | Last update |
|----|-------|-------|--------|-------|-------------|
| [hipaa-readiness-profile](hipaa-readiness-profile/hipaa-readiness-profile.md) | HIPAA Readiness Profile — PP3500 System | cybersecurity | draft | benxavier-gl | 2026-06-02 |

## Conventions

- **One folder per analysis** (`<id>/`) holding the aggregate `<id>/<id>.md` (start-here final report), an auto-generated folder `README.md`, the derived `<id>.gap.json` sidecar, and any `recs-<discipline>.md` / `research-<topic>.md` detail files. Frontmatter-driven (`topic`, `status`, `recommended_agents`, `grounded_against`). See the parent [`../README.md`](../README.md) for the workspace rules and the `gap-analysis` skill for the folder-per-analysis convention.
- Read-only against canonical content — analyses surface findings; they never amend the source DHF docs.
- System-level scope: analyses here may span multiple item DHFs (e.g., HIPAA readiness across cloud-suite + connectivity-adapter + pca-device telemetry).

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-06-02 | Ben Xavier | Folder created under ben/077. First analysis: `hipaa-readiness-profile` (system-wide HIPAA Security Rule readiness, scaffolded via `/gap-analysis init cybersecurity --component pca-device`). |
| 2026-06-02 | Ben Xavier | Migrated `hipaa-readiness-profile` from flat `<id>.md` to the folder-per-analysis layout `<id>/<id>.md` (+ folder README, regenerated `.gap.json`) when gap-analysis converged with upstream v4 (skill v5, ben/077). |
