# `hipaa-readiness-profile/` — Analysis Folder

System-wide HIPAA Security Rule readiness gap analysis for the PP3500 (`pca-device` system DHF), spanning the ePHI data path across `cloud-suite`, `connectivity-adapter`, and the device telemetry transport.

_Demo sample data — not for clinical use._

## Reading order

1. **[`hipaa-readiness-profile.md`](hipaa-readiness-profile.md)** — the aggregate / final report. Start here: goal, grounding, assertions, the 14 F-N findings, recommendations, and open questions.
2. Per-discipline detail (`recs-<discipline>.md`) — none yet; the fan-out findings were merged into the aggregate by the conductor (the advisor agents are read-only — see the fan-out write-back note in the skill).
3. Research substantiation (`research-<topic>.md`) — none yet.

## File inventory

| File | Role | Authored by |
|------|------|-------------|
| `hipaa-readiness-profile.md` | Aggregate / final report (start here) | human + cybersecurity advisor (conductor-merged) |
| `hipaa-readiness-profile.gap.json` | Derived JSON sidecar for the project-console Gap Analysis view — **regenerated** by `/gap-analysis render`, never hand-edited | derived |
| `README.md` | This folder meta | human |

## Cross-file conventions

- The aggregate's `id:` frontmatter (`hipaa-readiness-profile`) matches this folder name.
- Detail files (when added) carry `parent_analysis: hipaa-readiness-profile` in frontmatter so a `/gap-analysis list` walk rolls the cluster up as one unit.
- Internal cross-references use short relative paths (e.g., `[recs-cybersecurity.md](recs-cybersecurity.md)`).
- The `.gap.json` sidecar is a regenerated projection of the aggregate — edit the `.md` and re-run `/gap-analysis render`; never edit the JSON.

## How this folder was produced

Scaffolded via `/gap-analysis init cybersecurity --component pca-device` (flat layout, under ben/077), then a 3-advisor fan-out (cybersecurity primary) returned 14 findings the conductor merged into the aggregate. Migrated from the flat `pca-device/hipaa-readiness-profile.md` into this folder-per-analysis layout under ben/077 when the skill converged with upstream gap-analysis v4 (skill v5).
