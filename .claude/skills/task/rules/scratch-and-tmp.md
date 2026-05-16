# Rule: Personal Scratch & System tmp

Two distinct sandboxes exist for transient work, and only those two. Anything else (a project-root `_scratch/`, a project-tree `tmp/`) is drift.

## Sandboxes

| Folder | Purpose | Lifetime | Git | Owner |
|--------|---------|----------|-----|-------|
| `tasks/{person}/_scratch/` | Personal sandbox — ideas, drafts, work outputs the person wants to keep around locally during a task | Indefinite, user-managed | **Gitignored, never committed** | The person whose task folder it lives in |
| System `/tmp/` (OS-provided) | Claude's intermediary files during a single activity (extracted text, partial conversions, throwaway exports) | Single activity, deleted on completion | N/A — outside the repo | Claude — must clean up |

## Rules

- **Only `tasks/{person}/_scratch/` is sanctioned.** No project-root `_scratch/` — anything cross-cutting belongs in a real doc, not scratch.
- **No references from committed content.** Files under `_scratch/` are never referenced by committed docs or scripts (they don't exist for other collaborators). If an artifact becomes load-bearing, promote it to a properly-named, committed doc — don't link to scratch.
- **Claude uses the OS-provided system `/tmp`** for transient intermediates. There is no project-tree `tmp/` directory.
- **Gitignore is project-wide.** The `_scratch/` and `**/_scratch/` patterns are gitignored project-wide; the `/best-practices` audit warns if anything is tracked under a `_scratch/` path.

## How to apply

When an in-progress task generates exploratory output the person wants to keep around but isn't ready to commit (a draft document being iterated on, a test fixture, a scratch script), write it under `tasks/{person}/_scratch/`. When generating a transient intermediate that will be consumed within the same activity (extracted text from a PDF that will be parsed and discarded), write it under the OS `/tmp/`. Never create a top-level `_scratch/` or `tmp/` in the project root.
