# `/digest` Skill — Design & Architecture

> Human-facing design document. Claude reads `SKILL.md` for action definitions and `scripts/*.py` for behavior — this file exists so a human reader can understand why the skill is shaped the way it is.

## Purpose

Two related artifacts from one git-log-driven core:

1. **Ephemeral daily briefing** — pushed into each user's session context at SessionStart, throttled to once per 12 hours per user. Helps team members start the day with an answer to "what happened since I was last here?" without having to read the whole git log.
2. **Persistent project `CHANGELOG.md`** — a curated reverse-chronological record of significant project activity, filed at repo root, written on demand.

## Design rationale

**Why two surfaces, one skill?**
The core work — reading `git log` since a cutoff, filtering by path + subject heuristics, grouping — is identical for both. Splitting them into two skills would duplicate the aggregation code and create two approval surfaces in `project.yml`. One skill with two actions keeps the code DRY and the namespace clean. See `SKILL.md` for the action definitions.

**Why mechanical and not LLM-summarized?**
Initial v1 runs at SessionStart on every session for every user, possibly multiple times per day per user. LLM summarization at that cadence would be wasteful. Path-based filtering and fixed-theme grouping produce a "good enough" digest at zero token cost. If it proves too dull in practice, a `--smart` flag can feed the same raw data into a subagent later without redesigning the skill.

**Why 12h throttle and not 24h?**
12h supports a mid-day check-in for someone who works off hours. The window is cheap to change — just edit the constant in `hooks/session-briefing.sh`.

**Why per-user (email-keyed) state instead of per-session?**
A 12h throttle tied to sessions would reset too often (every new terminal = new briefing). Tying it to email means each teammate sees the briefing once per window regardless of how they open sessions. The state file is `.claude/state/briefing-last-shown-<email-slug>.txt` — per-project, gitignored (per the existing `.claude/state/` convention).

**Why include the current user's own commits in the briefing?**
Self-recall of yesterday's work is useful, and filtering them out adds surprise ("why did my commits disappear?"). The explicit design call (from task 019) is to show everyone, including you.

**Why `CHANGELOG.md` at repo root?**
Standard convention, well-understood by humans and tools. The reverse-chronological structure (newest first) is also well-understood, and finding the most recent `## YYYY-MM-DD HH:MM` header gives us a trivial since-cursor for incremental runs.

**Why a `medtech-docs`-owned template rather than a digest-owned one?**
`medtech-docs` already owns the full project-scaffold template library (`readme-*.md`, `standard-file.md`, etc.). Adding one more template next to them keeps the scaffold responsibility in one place. The digest skill references it by path but doesn't own it — consistent with `docflow` referencing `medtech-docs` templates during conversion flows.

## Architecture

```
.claude/skills/digest/
├── SKILL.md                     # action contracts, best-practices checks
├── README.md                    # this file
├── VERSION                      # semver
├── hooks/
│   └── session-briefing.sh      # SessionStart; resolves user, checks throttle,
│                                #   calls digest.py, writes state file
└── scripts/
    ├── digest.py                # daily-briefing aggregator (stateless; state
    │                            #   file is owned by the hook)
    └── build_changelog.py       # CHANGELOG.md builder; finds since-cursor
                                 #   from last dated header
.claude/skills/medtech-docs/templates/
└── changelog-project.md         # seed template used by /digest setup

.claude/state/                   # gitignored
└── briefing-last-shown-<slug>.txt
```

**State** is minimal:
- One per-user throttle file (`briefing-last-shown-<slug>.txt`) — contents are the last-emitted ISO timestamp, also used as `--since` for the next digest
- The `CHANGELOG.md` itself is its own state — the latest `## YYYY-MM-DD HH:MM` header is the since-cursor for the next `/digest log`

**No `digest.yml`** in v1. Significance rules live in `build_changelog.py` as a constant. Keeping them in-code avoids the drift surface a config file would introduce; if per-project overrides become a frequent ask, v2 introduces the config.

## Future directions (not in v1)

- `--smart` flag on `daily` to feed the raw digest through a subagent for an LLM-polished briefing (opt-in, token cost acknowledged)
- `digest.yml` project config for overriding significance rules and "pay attention" paths
- Optional team email summary pushed via a Stop hook on specific days (weekly rollup)
- `/digest status` reporting per-user throttle timestamps (helps debugging why a briefing didn't fire)
- Push to hitachi medtech-docs as v18 for the `changelog-project.md` template (and potentially the digest skill itself as its own registry entry — task 019 follow-up)

## Related

- `tasks/ben/019-digest-skill.md` — the task that designed and built this skill
- `medtech-docs` skill — owns the `changelog-project.md` template file
- `task` skill — the `/task setup` helper installs `register-hook.sh` which `/digest setup` reuses
