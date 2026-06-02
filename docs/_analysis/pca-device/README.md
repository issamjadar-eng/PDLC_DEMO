# `_analysis/pca-device/` — System-Level Analyses

Gap analyses and reference audits scoped to the **`pca-device` system DHF** — the PP3500 system leaf, used for cross-component / system-level / filing-aware critiques (per `project.yml dhfs[]` `role: system`).

## Analyses

| ID | Title | Topic | Status | Owner | Last update |
|----|-------|-------|--------|-------|-------------|
| [hipaa-readiness-profile](hipaa-readiness-profile.md) | HIPAA Readiness Profile — PP3500 System | cybersecurity | draft | benxavier-gl | 2026-06-02 |

## Conventions

- One markdown file per analysis, frontmatter-driven (`topic`, `status`, `recommended_agents`, `grounded_against`). See the parent [`../README.md`](../README.md) for the workspace rules.
- Read-only against canonical content — analyses surface findings; they never amend the source DHF docs.
- System-level scope: analyses here may span multiple item DHFs (e.g., HIPAA readiness across cloud-suite + connectivity-adapter + pca-device telemetry).

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-06-02 | Ben Xavier | Folder created under ben/077. First analysis: `hipaa-readiness-profile` (system-wide HIPAA Security Rule readiness, scaffolded via `/gap-analysis init cybersecurity --component pca-device`). |
