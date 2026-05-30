---
description: Refresh the active task doc to resume-ready state before clearing context, ending the session, or wrapping up for the day
argument-hint: "[<person> <NNN>]  (optional — defaults to the currently-active task)"
---

Invoke the `task` skill's `checkpoint` action on the currently-active task (or on `<person> <NNN>` if provided as arguments).

This is the routine for making the task doc resume-ready per its own PERMANENT RULE 4. A fresh Claude session, given only the task file, must be able to re-enter the work without asking "what were we doing?"

Run through every step of the `checkpoint` action defined in `.claude/skills/task/SKILL.md`:

1. Identify the target task doc (active task if no args; `tasks/<person>/<NNN>-*.md` if args provided)
2. Audit against PERMANENT RULE 4 — what was completed, in-flight state, next steps, open questions, activation command
3. Refresh Todos (tick completed, re-prioritize remaining)
4. Refresh Open Questions (resolve answered ones; don't accumulate stale entries)
5. Refresh Resume → In-flight artifacts (files, git HEADs, PRs, temp files; note commit status explicitly)
6. Refresh Resume → First action on resume (priority steps + anti-patterns to avoid)
7. Refresh Changelog (dated entry naming what shipped this session)
8. Verify the index entry in `tasks/<person>/000-index.md` (Status + Summary current)
9. Do NOT commit to git — the user controls commits
10. Write `.state/last-checkpoint-<person>-<NNN>.txt` and delete any matching `.state/uncheckpointed-<person>-<NNN>-*.txt` markers
11. End with the EXACT text on its own line as the final response:
    ```
    ✅ Resume-ready — safe to /clear or /quit.
    ```

Arguments: $ARGUMENTS
