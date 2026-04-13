# Frontmatter Template — Source-MD Files

Use this template for all files in `docs/internal/source-md/`. Populate every field. Use `null` for fields that don't apply (e.g., `sheets` for non-XLSX files).

```yaml
---
source_file: "{original filename with extension}"
source_path: "{subfolder/filename relative to docs/internal/source/}"
doc_id: "{DOC-ID, e.g., FORM-000137230}"
doc_type: "{FORM | SOP | POL | WI | QSD}"
title: "{Document title, without doc-id prefix}"
format: "{pdf | docx | doc | xlsx}"
conversion_date: "{YYYY-MM-DD}"
conversion_method: "{pandoc + manual review | pdftotext + manual review | claude-read + manual review | xlsx-skill + manual review | libreoffice + pandoc + manual review}"
conversion_fidelity: "{faithful | summary | partial}"
pages: null        # For PDFs: total page count. null for other formats.
sheets: null       # For XLSX: list of sheet names, e.g., ["Sheet1", "Risk Matrix"]. null for other formats.
has_images: false   # true if non-decorative images were extracted
image_count: 0      # Number of extracted image files
has_tables: false   # true if document contains tables
has_form_fields: false  # true if document contains fillable form fields
references:         # Cross-references to other documents (list)
  - doc_id: null
    title: null
    resolved: false
    match: null
    note: null
conversion_history: # For refreshed docs — list of conversion events
  - date: "{YYYY-MM-DD}"
    source: "v1 — original conversion"
notes: "{Any conversion notes — what was lost, approximated, or needs attention}"
---
```

## Field Definitions

| Field | Required | Description |
|-------|----------|-------------|
| `source_file` | Yes | Original filename with extension |
| `source_path` | Yes | Path relative to `docs/internal/source/` (e.g., `Forms/FORM-000000001 - Design and Development Plan.docx`) |
| `doc_id` | Yes | Corporate document ID assigned by the organization's document control system (e.g., `FORM-000000001`) |
| `doc_type` | Yes | Document type: FORM, SOP, POL, WI, or QSD |
| `title` | Yes | Document title without the doc-id prefix |
| `format` | Yes | Source file format: pdf, docx, doc, or xlsx |
| `conversion_date` | Yes | Date of conversion (or most recent refresh) |
| `conversion_method` | Yes | Tools used for conversion |
| `conversion_fidelity` | Yes | `faithful` = complete reproduction, `summary` = summarized (e.g., copyrighted standards), `partial` = some content could not be converted |
| `pages` | PDF only | Total page count |
| `sheets` | XLSX only | List of sheet names |
| `has_images` | Yes | Whether non-decorative images were extracted |
| `image_count` | Yes | Count of extracted image files |
| `has_tables` | Yes | Whether the document contains tables |
| `has_form_fields` | Yes | Whether the document contains fillable fields |
| `references` | If present | List of cross-references to other documents |
| `conversion_history` | Yes | List of conversion events (grows with each refresh) |
| `notes` | If applicable | Conversion notes — required if `conversion_fidelity` is `partial` |
