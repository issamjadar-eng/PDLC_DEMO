# `software-cybersecurity/templates/` — Software & Cybersecurity Templates

Fillable markdown stubs paired with the SOPs in [`../`](../). Each template is referenced by its parent SOP via the doc-ID table.

_Demo sample data — not for clinical use._

## Structure

Templates here implement specific clauses of the SOPs in the parent folder. See [`../README.md`](../README.md) for the full `GL-<TYPE>-SOFTWARE_CYBERSECURITY-<NNN>` ID table — template rows are tagged `GL-TMP-`, form rows are `GL-FORM-`, work-instruction rows are `GL-WI-`.

## Expected Content

| Pattern | Doc Type | Purpose |
|---------|----------|---------|
| `<topic>-<artifact>.md` | Template | Fillable markdown stub with `{{PLACEHOLDER}}` tokens. Cloned per use; the populated copy lives in the relevant DHF `formal/` folder. |

## Conventions

- **One template per markdown file.** No multi-template combined documents.
- **Tokens use `{{UPPER_SNAKE}}` format.** Document the token semantics in the file's frontmatter or a top-of-file table.
- **No project-specific content.** Templates are SOP-level — they reference clauses generically and rely on the consumer to inject project-specific values via tokens.
- **References to parent SOP at the top.** Every template states which SOP it implements and which clause(s) it satisfies.
- **Mirror status.** This folder is part of `docs/internal/source-md/` — the markdown mirror of `docs/internal/source/` formal documents. See the parent `source-md` README for the mirror-management rules.

## For Claude

- Do NOT edit template content casually — templates are SOP-controlled. Changes go through the QMS change-control process documented in [`../`](../) (or in `quality-management/` SOPs for cross-category templates).
- To populate a template for use in a DHF: copy the file to the target DHF's `formal/` folder, rename per the DHF naming convention, fill in tokens.
- Read `docs/internal/source-md/software-cybersecurity/README.md` for the full SOP / Template / Form ID table.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-05-30 | Ben Xavier | Initial scaffold under ben/068 — closes the `/best-practices` audit FAIL for the missing folder README. |
