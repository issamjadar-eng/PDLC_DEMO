# FDA Guidance

Distilled FDA guidance documents that apply to this project. Each file is a copy of the bundled distilled guidance from the `medtech-docs` skill library, imported here so it travels with the project repository and can be edited / annotated in place.

Files are imported via `/medtech-docs update-external-references`. Re-run that action whenever project scope or strategy changes — it adds newly-applicable guidances without overwriting anything you have already edited here.

## Active Guidances

| Topic | File | Title | Original Source (skill library) | Status |
|-------|------|-------|---------------------------------|--------|

- **Original Source** column links to the bundled originals in the skill library:
  - PDF: `.claude/skills/medtech-docs/references/fda-guidance/source/<topic>.pdf`
  - Markdown conversion: `.claude/skills/medtech-docs/references/fda-guidance/source-md/<topic>.md`
  - Distilled (the file copied here): `.claude/skills/medtech-docs/references/fda-guidance/<topic>-distilled.md`

## Evaluated — Not Applicable

Guidances evaluated by `update-external-references` and not currently applicable, with the rubric signal that drove the decision. If a guidance moves from "applicable" to "not applicable" on a re-run, its row is moved here but the file on disk is retained.

| Topic | File | Scope Qualifier | Rationale |
|-------|------|-----------------|-----------|

- **Scope Qualifier** column should name the *specific slice* of the guidance that was evaluated as not applicable (e.g., "imaging-functions only", "cleared-device branch only"). This prevents the failure mode where a rationale framed too broadly silences future applicability when project capabilities change. If the entire guidance is genuinely out of scope, write "(whole guidance)".

## Conventions

- **One file per guidance**, named by short topic (e.g., `qsub.md`, `pccp-aiml.md`). Filename matches the bundled distilled file with the `-distilled` suffix removed.
- Files are imported verbatim from the skill library by `update-external-references`. Edits made here are never overwritten on re-run — the action only creates files that don't yet exist.
- Use `[VERIFY]` markers for any project-specific assertions added on top of the distilled content.
- Note knowledge cutoff — flag if guidance may have been updated since the bundled version.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
