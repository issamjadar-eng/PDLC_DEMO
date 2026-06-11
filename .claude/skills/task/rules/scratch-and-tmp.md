# Rule: Personal Work, Personal Scratch & System tmp

Three distinct sandboxes exist for personal/transient work, and only those three. Anything else (a project-root `_scratch/`, a project-root `_work/`, a project-tree `tmp/`) is drift.

The two personal sandboxes are distinguished by **one axis only — does it go into git?** `_work/` is committed and reviewable by teammates; `_scratch/` is gitignored and local-only. Same owner, same per-person location; different visibility.

## Sandboxes

| Folder | Purpose | Lifetime | Git | Owner |
|--------|---------|----------|-----|-------|
| `tasks/{person}/_work/` | Personal **committed** sandbox — task-support artifacts the person wants in git and reviewable by teammates (data files `.xlsx`/`.csv`, generated reports, supporting outputs attached to a task) that are **not** themselves a task doc and **not** a controlled `docs/` deliverable | Indefinite, user-managed | **Committed & tracked** | The person whose task folder it lives in |
| `tasks/{person}/_scratch/` | Personal sandbox — ideas, drafts, work outputs the person wants to keep around locally during a task | Indefinite, user-managed | **Gitignored, never committed** | The person whose task folder it lives in |
| System `/tmp/` (OS-provided) | Claude's intermediary files during a single activity (extracted text, partial conversions, throwaway exports) | Single activity, deleted on completion | N/A — outside the repo | Claude — must clean up |

## Rules

- **Both personal sandboxes are per-person only.** No project-root `_work/` or `_scratch/` — anything cross-cutting belongs in a real `docs/` doc, not a personal sandbox.
- **`_work/` is committed and reviewable.** It is the sanctioned home for personal task-support files a person wants in git and visible to teammates — so they stop landing loose in the task-folder root. A task folder's root is for `NNN-*.md` task docs + `000-index.md`; companion data files (`.xlsx`, `.csv`, generated reports) go in that task owner's `_work/`.
- **`_work/` is not a controlled record.** It holds personal working output, not a controlled DHF deliverable. If an artifact becomes load-bearing / controlled, **promote it out of `_work/`** into its proper `docs/` home; committed docs must not depend on `_work/` paths (the file may move or be cleaned up by its owner).
- **`_work/` is never a grounding or citation source.** Being committed makes it *visible*, not *authoritative*. Agents must not ground project claims on, cite, or treat `_work/` content as canonical — it is one person's working output, unreviewed against the controlled record. Semantic search / file-discovery indexes (e.g., a file-locator corpus) must exclude `**/_work/**` so `_work/` files never surface as search results. Anything worth grounding on belongs in `docs/`.
- **No references from committed content into `_scratch/`.** Files under `_scratch/` are never referenced by committed docs or scripts (they don't exist for other collaborators). If a `_scratch/` artifact becomes worth sharing, move it to `_work/` (reviewable) or promote it to a real `docs/` doc (controlled) — don't link to scratch.
- **Claude uses the OS-provided system `/tmp`** for transient intermediates. There is no project-tree `tmp/` directory.
- **Gitignore is project-wide.** The `_scratch/` and `**/_scratch/` patterns are gitignored project-wide; the `/best-practices` audit warns if anything is tracked under a `_scratch/` path. `_work/` is deliberately **not** ignored — it is meant to be committed.

## How to apply

Decide by **who needs to see it** and **whether it's controlled**:

- Teammates should see it / you want it in git, but it isn't a controlled `docs/` deliverable (a data workbook, a generated report attached to a task) → `tasks/{person}/_work/`.
- Exploratory output you want to keep locally but not commit (a draft being iterated, a test fixture, a scratch script) → `tasks/{person}/_scratch/`.
- A transient intermediate consumed within the same activity (extracted text from a PDF that will be parsed and discarded) → OS `/tmp/`.
- It's a controlled record / load-bearing deliverable → none of these; write it to its proper `docs/` home.

Never create a top-level `_work/`, `_scratch/`, or `tmp/` in the project root.
