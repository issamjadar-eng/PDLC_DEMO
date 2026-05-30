# Rule: Doctype Governance — read the governing QMS templates before editing a mirrored regulated doc

When you create or modify a document inside a folder whose layout is governed by a `.taxonomy.yml` file (e.g., per-DHF Confluence mirrors, Windchill mirrors, or other regulated-vault mirrors under `dhf_organization: external`), the doctype's authoring contract is the QMS form/SOP/work-instruction declared in the taxonomy — **not** the surrounding markdown, **not** the related ISO/IEC standard, and **not** your prior pattern recognition. Read the governing templates first.

## Why

Mirrored regulated documents instantiate a specific QMS template (FORM-*, SOP-*, WI-*). The template defines column schemas, scoring scales, mandatory sections, sign-off rows, and content boundaries that the document MUST conform to once it returns to the regulated vault. Editing the markdown without referencing the controlling template is the most common path to:

- Adding columns the FORM doesn't carry → forces hand-rework before publish
- Using scoring scales different from those in the project's risk-acceptability QSD → invalidates risk-acceptability comparisons
- Putting clinical-recommendation content into a non-device administrative doctype → silently re-scopes the device classification
- Restating standards text in the doc body when the FORM template's structure already encodes those obligations → bloat without conformance gain

The QMS template is the **authoring contract**. ISO/IEC standards inform the *content* but the *shape* lives in the template. Editing without reading the template makes downstream rework guaranteed.

## How to apply

Before any Edit/Write to a markdown file under a folder governed by a `.taxonomy.yml` `mappings[]` entry:

1. **Walk up from the target file** to find the nearest `.taxonomy.yml`. The file may be at the discovery-root level (e.g., `.../mirror-root/.taxonomy.yml`) or at the DHF root — whichever is closest.
2. **Determine the doctype slug** — the folder name immediately above the target file (for files in `<slug>/v*.md` or `<slug>/index.md` layouts) OR the file basename for flat-file layouts.
3. **Look up `mappings[<slug>]`** in the taxonomy. If present, read its `governing_qms` block:
   - **`forms[]`** — the QMS form templates the doctype instantiates. Read each via `docs/internal/source-md/Forms/FORM-NNNNNNNNN*.md` (or the project's equivalent registry path). The form defines the document's structural contract: columns, scales, required fields, sign-off rows.
   - **`sops[]`** — the parent SOPs governing the process. Read at least the first one to understand procedural obligations.
   - **`work_instructions[]`** — the WIs refining the SOP for this specific doctype. Read the first one for authoring discipline.
   - **`upstream_inputs[]`** — forms whose output feeds this doctype. Skim only if your edit pivots on cross-doctype linkage.
4. **If `governing_qms` is absent or `null`** — the taxonomy mapping is unverified for this doctype. Do NOT invent a governing form. Flag the gap and proceed against ISO/IEC standards alone; surface the unverified-mapping signal in your response so the team can author the mapping later.
5. **If the slug is not in `mappings[]` at all** — the doctype is new or unmapped. Flag this; do not silently treat the absence as "no governance." The taxonomy file is the source of truth; absence means the convention has not yet been authored.
6. **If `governing_qms.forms: []` with a `note:`** — the doctype is intentionally not backed by a QMS form (team-internal convention). The `note:` field explains why. Treat as authoritative; no form-reads required.

The taxonomy file's own header comment block documents its schema; trust it as canonical, not this rule.

## Signals to look for

- A `<!-- AUTO:STRUCTURE kind=doc-governance source=taxonomy -->` sentinel block at the top of a document — its visible-banner rendering already lists the governing IDs. Use this as a shortcut: if the banner is present and current, the IDs are right there.
- A `governing_qms` field in the document's discovery-index entry — when `dhf-manifest discovery-index` resolves a per-DHF role through `.taxonomy.yml`, the resolved entry carries this. Advisor agents see it via the discovery index; main-session reads should walk up to the taxonomy directly when not running through an agent.

## Interaction with other rules

- **`readme-before-write.md`** — still applies. Both rules layer: README defines folder-local conventions; the taxonomy governance rule defines doctype-instance contracts. The README rule is satisfied by reading the folder + parent READMEs; this rule additionally requires reading the QMS template.
- **`audit-wiring-before-adding-fields.md`** — if you are tempted to add a field to a doctype that the FORM template doesn't carry, the wiring-audit rule and this one are aligned: stop, read the FORM first, then decide whether the field belongs in the doc body, in the project config (`project.yml`), or as an extension proposal back to the FORM owner.
- **`sentinel-blocks.md`** — the `doc-governance` sentinel kind is what renders the banner this rule asks readers to look for. The sentinel renderer reads the same taxonomy file.

## When the taxonomy gets out of date

The taxonomy file should carry a `last_updated:` field at top level. Project audit infrastructure (e.g., `/best-practices`) is expected to flag taxonomy files past their `review_cadence_days` threshold. If you notice the taxonomy is stale while applying this rule, surface that to the user — do not silently proceed against possibly-incorrect mappings.
