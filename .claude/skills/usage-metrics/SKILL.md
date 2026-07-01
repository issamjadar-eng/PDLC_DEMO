---
name: usage-metrics
description: "Cross-user Claude Code token-usage + cost telemetry for a team. TRIGGER when the user wants to measure, collect, aggregate, report, or project Claude Code token usage or spend across teammates — e.g. 'how many tokens are we using', 'what's our Claude usage/cost', 'build a usage dashboard', 'project our 30-day cost', 'set up usage tracking', 'who's using the most tokens', 'refresh the usage report', or wants a live token/context/cost **status line** ('show my context usage', 'add a status line with tokens and cost'). Collects each teammate's usage LOCALLY from their session transcripts, uses git as the aggregation bus (no shared server), renders a single self-contained HTML cost dashboard, and installs a team-shared status line. Actions: setup, collect, aggregate, report, status."
version: 8
updated: 2026-06-30
---

Base directory for this skill: `${CLAUDE_SKILL_DIR}`

# Usage Metrics

Measure Claude Code token usage and equivalent cost across a whole team, without any shared server or LLM in the data path. Usage: `/usage-metrics <action>`.

**Design (git-as-aggregator).** Each teammate runs `collect` locally — it parses their own Claude Code session transcripts (`~/.claude/projects/<project>/*.jsonl`) into per-session JSON under their **own task folder** (`tasks/{task_folder}/_usage-metrics/`). Because each person's data lives in their own folder, **the folder path is the identity** — no email or PII is written into committed files, and there are no cross-user collisions (one file per `session.id`). Git/GitHub is the transport that converges everyone's files; `aggregate` rolls them up with a plain script and renders the dashboard. All specifics live in `project.yml usage_metrics` — the skill is project-agnostic.

## Supporting Files

| File | Purpose |
|------|---------|
| `README.md` | Design document — architecture, lineage, decisions |
| `scripts/setup.py` | `setup` action — idempotent self-wiring into a project |
| `scripts/collect.py` | `collect` action — parse local transcripts → per-session usage records |
| `scripts/aggregate.py` | `aggregate`/`report` action — roll up all teammates' records → HTML + markdown + JSON |
| `scripts/publish.py` | publish your own `_usage-metrics/` to the shared branch via an isolated git worktree (working branch untouched) |
| `hooks/usage-metrics-refresh.sh` | SessionStart hook — auto-regenerate the dashboard when >TTL days stale (local-only) |
| `hooks/usage-metrics-publish.sh` | SessionEnd hook — collect the final session + publish your data to the shared branch (gated, best-effort) |
| `statusline.sh` | Team-shared Claude Code status line — `[model] <bar> IN/SIZE ctx · ↑OUT resp · $cost`. `setup` symlinks it to `.claude/statusline.sh` + registers the `statusLine` block. Reads `context_window.*` + `cost.total_cost_usd` from stdin; jq-guarded; degrades gracefully on builds without `context_window.*`. |
| `templates/usage_metrics.config.yml` | The `project.yml usage_metrics:` block `setup` appends |
| `templates/pricing.json` | Seed rate card (USD/MTok per model) `setup` installs to `tools/usage-metrics/` |

## Actions

Parse `$ARGUMENTS` to choose the action. With no argument or `help`, show this usage guide.

### `setup`

Wire the skill into the current project. Idempotent — safe to re-run. Run the bundled script (it does all the work and reports):

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/setup.py"
```

It: symlinks `hooks/usage-metrics-refresh.sh` into `.claude/hooks/` (skill stays the source of truth), registers it as a SessionStart hook via `.claude/hooks/register-hook.sh`, **symlinks `statusline.sh` to `.claude/statusline.sh` and registers the `statusLine` block in `settings.json`** (idempotent; a pre-existing different `statusLine` is treated as a project fork and left alone), appends the `usage_metrics:` block to `project.yml` (from `templates/usage_metrics.config.yml`), adds `**/_usage-metrics/**` to `file_locator.corpus_excludes`, **git-ignores the per-session data (`tasks/*/_usage-metrics/`)** so a generated-but-not-yet-pulled file can't block a fast-forward/merge of the shared branch (publish.py force-adds so it still reaches the branch), seeds `tools/usage-metrics/pricing.json` from the bundled rate card, installs the **daily-aggregate GitHub Actions workflow** (`.github/workflows/usage-metrics-aggregate.yml`), and creates `.state/`. Preconditions: `project.yml` exists and `/task setup` has installed `register-hook.sh`. Report the script's output to the user.

**The full automatic loop (no manual steps):**
1. **SessionStart hook** — keeps each person's *local* dashboard current (local-only, no git).
2. **SessionEnd hook → `publish.py`** — collects the just-finished session and pushes **your own** `tasks/<you>/_usage-metrics/` to the shared branch via an **isolated git worktree** (your working branch/WIP is never touched; concurrency-safe with fetch+retry). Gated by `usage_metrics.publish.enabled`. This is what gets each person's raw data onto the branch.
3. **GitHub Action** — re-aggregates the committed per-user data **daily** (cron `0 6 * * *`) + on push to `tasks/*/_usage-metrics/**`, and commits the refreshed `tools/usage-metrics/` team view.

**CI aggregates, it cannot collect** — runners have no local transcripts, so collection (and the publish in step 2) stays local. Aggregation is deterministic (same inputs → byte-identical output), so unrelated pushes are genuine no-ops. To opt out of auto-publish, set `usage_metrics.publish.enabled: false` (then raw data reaches the branch only via normal commits).

### `collect`

Capture **your own** usage from local session transcripts into `tasks/{your task_folder}/_usage-metrics/YYYY-MM/<session_id>.json`. Pure script, no LLM, idempotent (re-run = byte-identical):

```bash
python3 tools/usage-metrics/collect.py        # add --dry-run to preview
```

(`tools/usage-metrics/*.py` are symlinks to the skill's `scripts/` — the skill is the source; `tools/` is the execution surface so runtime artifacts stay out of `.claude/skills/`.)

It dedupes transcript rows by `message.id`, drops synthetic/zero-token messages, splits cache writes into 5m/1h (for accurate cost), and buckets by month + day + model. Identity comes from the roster (`resolve_user.py`); no email is written.

### `aggregate`  (alias: `report`)

Roll up **all** teammates' committed records and render the dashboard:

```bash
python3 tools/usage-metrics/aggregate.py               # all months
python3 tools/usage-metrics/aggregate.py --month 2026-06
python3 tools/usage-metrics/aggregate.py --pull        # git pull --ff-only first (team-wide)
```

Outputs the **team view** (aggregating everyone) to `tools/usage-metrics/`: a self-contained **`index.html`** (cost projection, daily/by-member/by-model charts, rate card), a consolidated **`usage.json`** (machine-readable; consumed by project-console's Metrics view), and per-month markdown. **Anonymized** — members appear as `Member 1…N` (stable by sorted task_folder); no real names or task_folders are written. Cost is per-model from `tools/usage-metrics/pricing.json` (falls back to the bundled seed). To view: `open tools/usage-metrics/index.html`. Non-canonical (not a controlled record).

### `status`

Report whether the skill is wired and how current the data is. Check, and summarize for the user:
- `grep -A3 '^usage_metrics:' project.yml` — is it configured? what method/scope?
- `.claude/hooks/usage-metrics-refresh.sh` symlink present? registered in `.claude/settings.json` SessionStart?
- newest file mtime under `tasks/*/_usage-metrics/` per teammate — who has reported, and how recently.
- `.state/usage-metrics-last-refresh-<task_folder>.txt` — when this machine last auto-refreshed.

## Best Practices

See `README.md` for the full health-check table consumed by `/best-practices`.

## Notes

- **No LLM in the data path.** `collect`/`aggregate` are deterministic scripts; the skill only orchestrates them. This keeps cross-user metrics cheap and reproducible.
- **Cost is an estimate**, not billing. Subscription (Max/Pro) is a flat fee; the dashboard shows the equivalent API-list-price cost from `pricing.json`. Re-fetch current rates from the source URL in that file when they change.
- **Retention.** Transcript-parse can only see what Claude Code keeps on disk (`cleanupPeriodDays`, default 30). Raise it in `.claude/settings.json` to retain more history going forward.
- If `$ARGUMENTS` is empty or `help`, show this usage guide.
