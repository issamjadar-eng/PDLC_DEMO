# Internal Process Documents

SOPs, procedures, and templates that govern how we work. These are not deliverables themselves but define the processes used to produce deliverables. Follows the same three-tier pattern as FDA guidance: original source documents → markdown conversions → distilled actionable files.

## Structure

| Folder / Location | Purpose |
|-------------------|---------|
| `source/` | Original SOP, procedure, and template files (PDF, DOCX, etc.) |
| `source-md/` | Markdown conversions of source documents — faithful reproductions |
| `*.md` (root) | Distilled files — actionable requirements extracted for verification activities |

## Information Flow

```
source/          Original documents (PDF, DOCX, etc.)
   ↓
source-md/       Faithful markdown conversion
   ↓
*.md (root)      Distilled: actionable requirements, checklists, verification criteria
```

Distilled files at the root level are the working reference — what we actually use day-to-day and build verification activities from.

## Conventions

- Source files keep their original filenames in `source/`
- Markdown conversions in `source-md/` use the same base name as the source (e.g., `source/design-control-sop.pdf` → `source-md/design-control-sop.md`)
- Distilled files at the root use short descriptive names (e.g., `design-control-sop.md`)
- All three tiers use the same base name for traceability
- SOPs, procedures, and templates coexist — no separate subfolders by document type
- Correspondence does NOT live here — it belongs with its submission (e.g., `docs/project/submissions/qsub/correspondence/`)

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
