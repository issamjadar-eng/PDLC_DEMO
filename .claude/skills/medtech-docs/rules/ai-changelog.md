# Rule: AI Change Log + Vendor-Neutral Attribution

When an **AI assistant** modifies a controlled markdown document, it records those edits in an **AI Change Log** — a metadata block that is **internal provenance only** and is **never published** to the downstream regulated systems (Confluence/Doc-Control, released vault) and **never part of the controlled record**. Separately, **no document may name the specific AI model, tool, or vendor** anywhere in its content or changelogs — the only sanctioned attribution is the vendor-neutral phrase **"AI assistant(s)."**

The principle in one line: capture *that* an edit was AI-assisted as **non-published metadata**, in **vendor-neutral** terms — so the controlled record stays human-authored and tool-agnostic, while provenance is still recoverable internally.

## Why

- **The controlled record is the regulated artifact.** Reviewers (FDA, Notified Body) read the published page / filed PDF. AI-edit provenance is internal QMS hygiene, not part of the device's design record — it must not leak into the published body.
- **Vendor neutrality survives tooling change.** Projects may use more than one AI assistant over time, or switch vendors. A document that hard-codes a product name (e.g., a specific model or CLI) goes stale or misleads the moment the toolchain changes, and couples a regulated record to a commercial vendor. "AI assistant(s)" is durable.
- **There is already a metadata seam.** The leading `<!-- … -->` comment block at the top of a controlled markdown doc is the tooling-managed metadata zone — held separate from the published body (the export pipeline wraps the publishable body in its own sentinel; the publish step pushes only the body to the downstream system). HTML comments have **no representation** in the downstream rich-text/storage format, so a block placed here is non-published *by construction*.

## The AI Change Log block

Place an HTML-comment block in the leading metadata zone (immediately after the human version-changelog block, before the first rendered heading / page-title sentinel):

```markdown
<!-- AI-CHANGELOG — internal provenance of AI-assisted edits. Metadata only:
     NOT published downstream (Confluence/Doc-Control), NOT part of the controlled
     record, stripped on DOCX/PDF export. Vendor-neutral by convention.
| Date       | Task   | Summary                                                  |
|------------|--------|----------------------------------------------------------|
| YYYY-MM-DD | nnn    | One-line description of what the AI-assisted edit changed |
-->
```

- **Append, don't rewrite.** Each AI-assisted editing pass adds one row. Newest at top or bottom is fine — match the document's existing version-changelog ordering.
- **Columns** are `Date | Task | Summary`. Do **not** add a column that names the model/tool/vendor, and do not record vendor session identifiers.
- **One block per document**, in the leading metadata comment zone. Never inside the rendered body and never inside a `<details>` block (those round-trip downstream as collapsible zones / review comments — see the rationale-block convention — so they are the *wrong* home for never-published content).

## Vendor-neutral attribution (applies everywhere, not just the block)

- In **any** changelog row, author field, commit-referenced doc note, or body prose, refer to the assistant as **"AI assistant"** / **"AI assistant(s)"** — never by model, product, or vendor name.
- Controlled version-changelog **Author** field: use `<initials> / AI Assistant` for a human-directed, AI-assisted change, or the human author alone. Not `<initials>/<product-name>`.
- This is a content rule for documents under the project's controlled trees; it does not govern git commit metadata (commit trailers may follow the project's own git convention).

## Relationship to the controlled version changelog

The human-facing **version changelog** (revision history, version bumps, approvals) is part of the controlled record and is human-authored — keep it concise and vendor-neutral. The **AI Change Log** is the parallel internal ledger of AI-assisted edits. A working-draft pass may be recorded in both (version row + provenance row); a routine AI-assisted touch-up that does not bump the controlled version belongs in the AI Change Log only. When in doubt, the controlled changelog records *what the document now says*; the AI Change Log records *that an AI assistant helped change it*.

## How to apply

1. Editing a controlled markdown doc with AI assistance → ensure an `<!-- AI-CHANGELOG -->` block exists in the leading metadata zone (create it if absent), and append a `Date | Task | Summary` row.
2. Writing any changelog/author/body reference to the assistant → use "AI assistant(s)"; never a product/vendor name.
3. Publishing/exporting → the block is non-published by construction (Confluence) and is stripped on DOCX/PDF export; do not move AI-provenance content into the rendered body or a `<details>` block.

## Interaction with other rules

- **`sentinel-blocks.md`** — the AI Change Log is **not** an `AUTO:STRUCTURE` sentinel: it is append-only provenance, not content rendered from a structural source. It lives in the same leading metadata zone but is hand-appended, not regenerated.
- **`doctype-governance.md`** — unaffected; the block carries no doctype content and changes no FORM/SOP-governed structure.
- **`claude-md-references.md`** — persistent docs still reference durable artifacts, not task numbers; the AI Change Log's `Task` column is internal provenance metadata (a deliberate, scoped exception, mirroring how version changelogs already cite tasks).
