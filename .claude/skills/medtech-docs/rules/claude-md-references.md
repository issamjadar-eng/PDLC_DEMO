# Rule: Persistent Docs Reference Durable Artifacts, Not Tasks

CLAUDE.md, `project.yml` descriptions, DHF READMEs, strategy docs, architecture docs, and other project-level persistent documents must reference **durable project artifacts**, never task documents.

## What counts as a durable artifact

- Strategy documents under `docs/project/strategies/`
- Architecture documents under `docs/project/dhfs/<dhf>/design-controls/architecture/`
- Input analysis under `docs/project/input-analysis/`
- Submission packages and composition manifests under `docs/project/submissions/`
- DHF deliverables (SRS, SDS, V&V protocols) under `docs/project/dhfs/<dhf>/`
- External references under `docs/external/`
- Standards and SOPs under `docs/internal/`
- Glossary entries in `glossary.md`

## What does NOT count

- Task documents under `tasks/{person}/NNN-*.md`
- Per-person task indexes under `tasks/{person}/000-index.md`
- `_scratch/` artifacts
- Personal memory files

## Why

- **Task numbers are ambiguous across team members.** Task `037` in `ben/` is unrelated to task `037` in `roman/`. A reference to "task 037" in CLAUDE.md is unresolvable without a person prefix, and even with one, the reader may not have access to the same git history.
- **Task docs are transient.** Tasks are created, completed, and superseded. The factual conclusions of a task migrate into durable artifacts; the task doc itself becomes a historical record. A persistent doc that points at task NNN goes stale the moment the task closes and its conclusions get rewritten elsewhere.
- **Audit posture.** External reviewers (FDA, Notified Body) read the durable artifacts, not the task docs. Persistent project documentation should be self-contained against those artifacts.

## How to apply

When writing or editing a persistent doc and you find yourself wanting to reference a task:

1. **Identify the durable artifact** the task produced — the strategy doc, the SRS section, the architecture decision, the input-analysis report, the composition manifest.
2. **Reference that artifact instead.** Use a relative path link to the file (or a section anchor within it).
3. **If the artifact does not yet exist**, that's a signal the task hasn't yet produced its durable output. Either wait for it, or create a stub durable doc whose first version captures the task's working conclusion.
4. **Never** write `see task 037` or `per task ben/037` in CLAUDE.md, project.yml, READMEs, strategy docs, or any other persistent doc.

This rule does not apply to task docs themselves (which routinely cross-reference each other) or to the `tasks/README.md` overview.
