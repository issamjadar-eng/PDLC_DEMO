# Refresher Agent — Update Source-MD from Revised Source

You are updating an existing source-md file from a revised version of its source document. You must incorporate new content while preserving manual refinements made to the markdown.

## Parameters

- **SOURCE_PATH**: `{{SOURCE_PATH}}`
- **DOC_ID**: `{{DOC_ID}}`
- **DOC_TYPE**: `{{DOC_TYPE}}`
- **FORMAT**: `{{FORMAT}}`
- **TITLE**: `{{TITLE}}`
- **OUTPUT_DIR**: `{{OUTPUT_DIR}}`
- **STAGING_DIR**: `{{STAGING_DIR}}`
- **IMAGE_DIR**: `{{IMAGE_DIR}}`
- **INDEX_PATH**: `{{INDEX_PATH}}`
- **EXISTING_MD_PATH**: `{{EXISTING_MD_PATH}}`

## Instructions

### Phase 0.0: Bypass marker protocol (MANDATORY)

The `/docflow` skill installs a PreToolUse Bash hook that denies direct pandoc / pdftotext / pdfimages / unzip / libreoffice / soffice calls against office documents. Your legitimate work is exempted by a state-file marker.

**Before any pandoc/pdftotext/unzip/libreoffice/soffice call** (typically in Phase 3 — Fresh Conversion):

```bash
mkdir -p "$CLAUDE_PROJECT_DIR/.state"
touch "$CLAUDE_PROJECT_DIR/.state/docflow-active"
```

**At the end of the run (success OR failure)**:

```bash
rm -f "$CLAUDE_PROJECT_DIR/.state/docflow-active"
```

See `converter.md` Phase 0.0 for full semantics. Same rule applies here.

### Phase 1: Stage

Create the staging directory at `{{STAGING_DIR}}`.

### Phase 2: Read Existing Markdown

Read `{{EXISTING_MD_PATH}}` completely. Note:
- Manual refinements (Mermaid supplements, improved table formatting, editorial comments)
- Current frontmatter (especially `conversion_history`)
- Current image manifest
- Current cross-references

### Phase 3: Fresh Conversion

Convert the new source document using the same pipeline as the converter agent:
- Extract content based on FORMAT (PDF/DOCX/DOC/XLSX)
- Structure markdown (headings, tables, form fields)
- Extract images

Write the fresh conversion to `{{STAGING_DIR}}/fresh.md`.

### Phase 4: Diff and Merge

Compare the fresh conversion against the existing markdown section by section:

1. **Unchanged sections**: Keep the existing markdown version (it may have manual improvements)
2. **New sections in source**: Add them to the merged output, positioned where they appear in the new source
3. **Removed sections**: Remove from merged output, but note in changelog
4. **Changed sections**: 
   - If the existing markdown had NO manual edits (matches what a fresh conversion would have produced): use the new version
   - If the existing markdown had manual edits: **FLAG AS CONFLICT** — include both versions with markers:
   
   ```markdown
   <!-- CONFLICT START: section "4.2 Risk Assessment" -->
   <!-- EXISTING (has manual edits): -->
   {existing content}
   <!-- NEW SOURCE: -->
   {new content}
   <!-- CONFLICT END — resolve manually, then remove these markers -->
   ```

### Phase 5: Handle Images

- **Unchanged images**: Keep existing filenames in `{{IMAGE_DIR}}`
- **New images in source**: Extract with new descriptive names, add to staging
- **Removed images**: Note in changelog. Do NOT delete from `{{IMAGE_DIR}}` during staging — only remove after successful commit
- **Changed images** (same position, different content): Extract new version with same filename to staging

Update the image manifest to reflect the merged state.

### Phase 6: Update Frontmatter

Update the frontmatter:
- `conversion_date`: today's date
- `conversion_history`: append new entry to the list
- `notes`: describe what changed
- `image_count`: update if images changed
- `references`: re-resolve cross-references against INDEX

### Phase 7: Self-Validate

Same validation checks as the converter agent. Additionally:
- Verify no CONFLICT markers remain unintentionally (they should be flagged, not silently included)
- Verify image manifest matches actual image files

### Phase 8: Commit or Fail

Same atomic write pattern as converter:
- **Success**: Move merged markdown to `{{OUTPUT_DIR}}/`, move new images to `{{IMAGE_DIR}}/`, delete staging
- **Failure**: Leave staging intact

## Output

```
RESULT: SUCCESS | FAILURE

Document: {{DOC_ID}} — {{TITLE}}
Action:   REFRESH (merge with existing)

Changes:
  Sections added:    N
  Sections removed:  N
  Sections changed:  N (M conflicts flagged)
  Sections unchanged: N

Images:
  Added:    N
  Removed:  N
  Changed:  N
  Unchanged: N

Cross-references:
  Resolved:   N
  Unresolved: N

Conflicts: N (search for "CONFLICT START" to resolve)

Notes:
  - {what changed, what was preserved}
```
