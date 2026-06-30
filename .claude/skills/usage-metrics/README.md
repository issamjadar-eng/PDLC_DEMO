# Usage Metrics — Design & Architecture

Design notes for the `usage-metrics` skill. Not loaded during normal operation — see `SKILL.md` for usage.

## Overview

Measures Claude Code token usage and equivalent cost across a team, with **no shared server and no LLM in the data path**. Each teammate collects their own usage locally from session transcripts; git is the aggregation transport; a script renders a single self-contained HTML cost dashboard.

## Lineage

Original skill. The collection mechanism (transcript parsing) and the git-as-aggregator pattern were validated against real Claude Code session files before the skill was scaffolded.

## Key Design Decisions

### git-as-aggregator (no shared collector)
The only thing a central OTel collector would buy is "everyone's data in one place" — git already does that. Each teammate's `collect` writes per-session JSON under their **own** `tasks/{task_folder}/_usage-metrics/`; normal commits converge the data; `aggregate` rolls it up. No server to stand up, no VPN, no egress decision.

### The folder is the identity (no PII)
Because each person's data lives under their own task folder, the folder path identifies the person. No email/account id is written into committed records (transcripts carry none anyway). One file per `session.id` makes concurrent sessions and multi-machine use **collision-free** — distinct filenames never conflict in git.

### Source in the skill, execution in `tools/`
The skill directory is the **source of truth** (real `scripts/`). `tools/usage-metrics/` holds **symlinks** to those scripts and is the **execution surface**, so any runtime artifacts (`__pycache__`, a future venv, pip deps) land in `tools/` — never in `.claude/skills/`. Scripts also set `sys.dont_write_bytecode = True` as belt-and-suspenders.

### Cost is computed, clearly-labelled estimate
Transcripts carry no cost field, so cost = measured tokens × a per-model rate card (`tools/usage-metrics/pricing.json`, seeded from the bundled template, fetched from Anthropic's published pricing). Cache writes are split 5m/1h for accuracy. Subscription billing is a flat fee — the dashboard shows the equivalent API-list-price cost and says so.

### Auto-refresh via staleness-gated SessionStart hook
Mirrors the SECOPS 7-day TTL pattern: on session start, if the local dashboard is older than `refresh_ttl_days`, regenerate it in the background, **local-only** (no git pull/commit/network). Silent fast-exit when fresh.

## Dependencies

| File | Required by | Purpose |
|------|-------------|---------|
| `project.yml` `usage_metrics` block | all actions | method/identity/storage/refresh config |
| `project.yml` `team.active[].task_folder` | collect, aggregate | per-person identity + labels |
| `.claude/skills/shared/scripts/resolve_user.py` | collect, aggregate | canonical roster resolver |
| `.claude/hooks/register-hook.sh` | setup | idempotent SessionStart registration (installed by `/task setup`) |
| `tools/usage-metrics/pricing.json` | aggregate | per-model rate card (project-local; seed in `templates/`) |
| `~/.claude/projects/<project>/*.jsonl` | collect | source session transcripts (read-only) |

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill has SKILL.md | `.claude/skills/usage-metrics/SKILL.md` exists | Required | shared |
| Frontmatter complete | name, description, version, updated all present | Required | shared |
| README.md exists | Design doc at skill root | Required | shared |
| Changelog current | Latest entry matches frontmatter version | Required | shared |
| Hook symlinked, not copied | `.claude/hooks/usage-metrics-refresh.sh` is a symlink into the skill | Required | shared |
| Execution via tools symlinks | `tools/usage-metrics/{collect,aggregate}.py` are symlinks to skill scripts | Recommended | local |
| Project-agnostic | No company/device/team/task names in any skill file | Required | shared |
| No PII in records | committed `_usage-metrics/*.json` contain no email/account id | Required | local |
| Config present | `project.yml` has a `usage_metrics:` block | Recommended | local |
| Daily-aggregate workflow | `.github/workflows/usage-metrics-aggregate.yml` exists | Recommended | local |
| Aggregation deterministic | re-running `aggregate.py` on unchanged inputs is byte-identical | Required | shared |

## Changelog

- 3 (2026-06-22): Added `publish.py` + a SessionEnd hook — each teammate's own `_usage-metrics/` data is pushed to the shared branch via an **isolated git worktree** (working branch untouched; fetch+retry for concurrency), closing the loop so the daily-aggregate workflow always has current data. Gated by `usage_metrics.publish.enabled`. `setup` now installs/registers both hooks (SessionStart refresh + SessionEnd publish).
- 2 (2026-06-22): Team dashboard output moved to `tools/usage-metrics/` (anonymized `Member N`; `index.html` + consolidated `usage.json` consumed by project-console's Metrics view). Token quantities normalized to MTok; rate card collapsed to a single Write column (1h rate). `setup` now installs a daily-aggregate GitHub Actions workflow (CI re-aggregates committed per-user data; collection stays local). Aggregation is deterministic (byte-identical re-runs).
- 1 (2026-06-22): Initial version — local transcript-parse collection, git-as-aggregator roll-up, self-contained HTML dashboard (cost projection + daily/by-member/by-model charts + rate card), per-model cost from an editable rate card, and a staleness-gated SessionStart auto-refresh hook. `setup` self-wires into a project (hook symlink + registration, `project.yml` block, file-locator exclude, pricing seed, `tools/` execution symlinks).
