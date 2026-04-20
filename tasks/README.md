# Tasks

Per-person task folders. Each active contributor owns a subfolder under `tasks/` containing numbered task documents plus an index.

## Convention — Task-First Workflow

All non-trivial work starts by either **finding** an existing task that covers it or **creating** a new one via the `/task` skill. The active task serves as the single source of truth for:

- Goals, todos, and changelog for the work
- Strategy and Lessons Learned capture (tagged with `<!-- STRATEGY CONTENT -->` / `<!-- LESSONS LEARNED -->` blocks — harvested by `/strategy` and `/lessons`)
- Per-session task gate state (the `PreToolUse` hook at `.claude/hooks/check-active-task.sh` blocks Edit/Write/NotebookEdit when no active task is set — see the `task` skill's `## Task Gate State File` section)

The task doc is **one file per task**. Sub-documents, phase writeups, analysis notes, and drafted content all live as new sections inside the same NNN-*.md file — never as `NNN-task-p1.md` sibling files. See CLAUDE.md `## Working Conventions`.

## Structure

```
tasks/
├── README.md                   # this file
├── lessons-ledger.md           # team-shared staging + audit trail (managed by /lessons)
├── ben/
│   ├── 000-index.md            # Active + Completed tables
│   ├── 001-project-init.md
│   ├── 002-...
│   └── SECOPS.md               # security-assert.sh attestation record
└── <other-person>/
    └── ...
```

## Per-person folder

| File | Purpose |
|------|---------|
| `000-index.md` | Active + Completed tables. Every task has a one-row entry with ID, Name, Status (Active only), Priority, and Summary. The Summary must be descriptive enough for `/task find` to match by topic without opening the task file. |
| `NNN-<short-name>.md` | Individual task document. Created by `/task create <person> <short-name>`. Structure defined in the `task` skill SKILL.md. |
| `SECOPS.md` | Security posture record for this person — updated by `.claude/hooks/security-assert.sh` on each SessionStart. Tracks 7-day check cycle and 30-day attestation cycle. |

## Lessons ledger

`lessons-ledger.md` is a team-shared staging area populated by `/lessons assemble` from `<!-- LESSONS LEARNED -->` blocks in task docs. Only the `## Staged` section is loaded at session start. See the `lessons` skill for the Task → Staged → Promoted lifecycle.

## Conventions

- Task IDs are three-digit zero-padded (`001`, `012`, `107`). Per-person folders have their own numbering — they do not share a global counter.
- Files are `NNN-<short-kebab-name>.md` (lowercase, no spaces).
- Person folders are lowercase first names (`ben`, `sarah`).
- Status values: `Not Started` | `In Progress` | `Blocked` | `Complete`. Completed tasks move from the Active table to the Completed table; the Status column is dropped in the Completed table.
- Priority values: `Low` | `Medium` | `High` | `Critical`.
- Every task has a `## Changelog` section in reverse-chronological order (most recent first).
- Strategy and Lessons Learned content must be tagged inline in the task doc using the required HTML-comment markers so the `/strategy` and `/lessons` harvest skills can find them.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-20 | Ben Xavier | Initial version — created under task 018 sync-skills to close the `tasks/README.md` best-practices FAIL. |
