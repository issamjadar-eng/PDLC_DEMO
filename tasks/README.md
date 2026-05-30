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

## Lesson Records

When a lesson from the ledger gets **applied** in a task (you took the lesson's guidance and acted on it) or **excepted** (you deliberately did the opposite for a reason), record that event inside the task doc where it happened. The records become the evidence trail the `lessons` skill rolls up by lesson ID; mature lessons promote out of the ledger only after their record table shows enough real-world application to justify formalizing.

**Format inside the task doc** (typically near the bottom, before `## Changelog`):

```markdown
## Lesson Records

<!-- LESSON RECORDS -->

### [L-ben-033-01] applied — 2026-05-15
Brief prose describing the context: what the lesson said, how it shaped a decision in this task, and the concrete artifact (commit / file / decision) that resulted. This body is the **evidence** that `/lessons promote` will show when deciding whether the lesson is ready for its permanent home.

### [L-ben-028-02] exception — 2026-05-20
When the lesson doesn't fit, note that too — explain why and what was done instead. Exceptions are first-class records; they refine the lesson's scope.
```

**Rules:**

- Section heading must be `## Lesson Records` (H2). The `<!-- LESSON RECORDS -->` sentinel is recommended but optional.
- Each record is a `### [LESSON-ID] <outcome> — YYYY-MM-DD` heading. Outcome is one of `applied`, `exception`, `superseded`, `discarded`.
- Records are **immutable history**: once written, they stay — even after the lesson is promoted out of the ledger or archived. They're the audit trail for *why* a lesson became canonical.
- `/lessons record <lesson-id> <outcome>` writes the block for you and appends a Changelog line.
- `/lessons assemble` reads these records (Pass 2) and rolls them up by lesson ID into the per-lesson Record table in `tasks/lessons-ledger.md`.

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
| 2026-05-30 | Ben Xavier | Added `## Lesson Records` section documenting the per-task record convention. Closes the lessons-skill audit FAIL for the missing section. (ben/068) |
