#### Ongoing task discipline
- **Update as you go (HARD RULE — no exceptions)**: The active task doc is the recovery point if a session drops, gets compacted, or is interrupted. If it doesn't reflect what was done, the next session can't pick up. Therefore:
  - **After each meaningful unit of work** (a converted document, a launched batch, a committed/pushed change, a decision, a discovered blocker), **immediately** update the task doc. Check off the relevant todo, add a one-line changelog entry with today's date and the concrete artifact (commit SHA, file path, decision, blocker), and update any progress counts/tables in the Goals section.
  - **Do not batch updates** waiting for "the end of the batch" or "after the push" — by then a crash, context-trim, or interrupt has lost the state.
  - **Do not wait to be reminded.** If the user has to remind you to update the task doc, that is a process failure, not a courtesy ask.
  - **A commit + push is not a substitute** for the task-doc update. Git history is for code; the task doc is for the project narrative — what was done, why, what's left, and what surprised us.
  - **Before ending a session or marking a task Complete**, confirm the task doc reflects: every commit/push from this session, every batch launched (incl. failures + retries), and the current progress count vs. total scope.
- **Keep indexes current**: Each person's `tasks/{person}/000-index.md` must reflect the true state of their tasks.
- **Find current project status**: Check each team member's `000-index.md` under `tasks/` to understand what's active, blocked, or completed.
