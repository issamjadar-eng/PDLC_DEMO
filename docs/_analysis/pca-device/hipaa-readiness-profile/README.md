# `hipaa-readiness-profile/` — Analysis Folder

System-wide HIPAA Security Rule readiness gap analysis for the PP3500 (`pca-device` system DHF), spanning the ePHI data path across `cloud-suite`, `connectivity-adapter`, and the device telemetry transport.

_Demo sample data — not for clinical use._

## Reading order

1. **[`hipaa-readiness-profile.md`](hipaa-readiness-profile.md)** — the aggregate / final report. Start here: goal, grounding, assertions, the 14 F-N findings, recommendations, and open questions.
2. Per-discipline detail (`recs-<discipline>.md`) — the three advisors' **full write-ups** (cybersecurity / regulatory-affairs / risk-management), each backing the findings it authored. These surface in the project-console **Advisors tab**.
3. Research substantiation (`research-<topic>.md`) — none yet.

## File inventory

| File | Role | Authored by |
|------|------|-------------|
| `hipaa-readiness-profile.md` | Aggregate / final report (start here) — incl. the `## Assertion positions` per-advisor stances | human + cybersecurity advisor (conductor-merged) |
| `recs-cybersecurity.md` | Full cybersecurity / §164.312 write-up (primary) backing F-1…F-6 | `cybersecurity` advisor |
| `recs-regulatory-affairs.md` | Full HIPAA-posture write-up (BAA, Subpart D, audience) backing F-7…F-10 | `regulatory-affairs` advisor |
| `recs-risk-management.md` | Full security-risk↔safety-bridge write-up backing F-11…F-14 | `risk-management` advisor |
| `hipaa-readiness-profile.gap.json` | Derived JSON sidecar for the project-console Gap Analysis view — **regenerated** by `/gap-analysis render`, never hand-edited | derived |
| `README.md` | This folder meta | human |

## Cross-file conventions

- The aggregate's `id:` frontmatter (`hipaa-readiness-profile`) matches this folder name.
- Detail files (when added) carry `parent_analysis: hipaa-readiness-profile` in frontmatter so a `/gap-analysis list` walk rolls the cluster up as one unit.
- Internal cross-references use short relative paths (e.g., `[recs-cybersecurity.md](recs-cybersecurity.md)`).
- The `.gap.json` sidecar is a regenerated projection of the aggregate — edit the `.md` and re-run `/gap-analysis render`; never edit the JSON.

## How this folder was produced

Scaffolded via `/gap-analysis init cybersecurity --component pca-device` (flat layout, under ben/077), then a 3-advisor fan-out (cybersecurity primary) returned 14 findings the conductor merged into the aggregate. Migrated from the flat `pca-device/hipaa-readiness-profile.md` into this folder-per-analysis layout under ben/077 when the skill converged with upstream gap-analysis v4 (skill v5).

Under ben/081 (2026-06-04), the three advisors were re-run to author their **full per-discipline responses** (`recs-*.md`) — consistent with the findings each had already contributed — and a `## Assertion positions` section was added recording each advisor's Positive/Neutral/Negative stance per assertion. (The original ben/077 fan-out persisted only the merged findings, not the full write-ups; these were regenerated, not retrieved.) This brings the HIPAA analysis to parity with the commercial-roadmap analysis for the console's Advisors-tab + assertion-positions views.
