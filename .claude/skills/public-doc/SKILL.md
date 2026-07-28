---
name: public-doc
description: "Author external-facing PROSE documents — white papers, articles, one-pagers, thought-leadership, customer-facing briefs. Use when creating, drafting, linting, or publishing any document meant to leave the building. Manages a draft state with goals/audience/campaign metadata, an INTERNAL-block convention for supporting evidence that NEVER ships, a strip-for-publish step that removes all internal content before producing the public PDF/HTML, and advisory brand/style/written-guideline linting read from the project's own config. Trigger on: 'write a white paper', 'draft an article/one-pager', 'publish this externally', 'strip internal notes', 'lint this doc against our brand/style guidelines', 'turn this into a client-facing PDF'. NOT for slide decks or presentations — for those use md-deck / frontend-slides / pptx (this skill makes prose documents, not slides)."
version: 3
updated: 2026-06-25
---

# Public-Doc — External Document Authoring

Author documents meant for an external audience (white papers, articles, one-pagers, briefs) with a clean separation between what the public sees and the internal evidence that backs it up. The skill is the **mechanism**; the company's brand, style, and lint values live in the **project** under `tools/public-doc/` so the skill stays reusable across projects.

Three ideas carry this skill:

1. **A draft state with metadata.** A draft carries a `public_doc:` frontmatter block declaring its goals, audience, campaign, status, and output name. This metadata is *internal* — it never appears in the published artifact.
2. **INTERNAL blocks.** Supporting evidence, source citations, positioning rationale, and talk-track live inline in `<!-- INTERNAL:BEGIN … INTERNAL:END -->` comment blocks, right next to the prose they substantiate. They are invisible in any rendered view and are removed entirely at publish. They also serve as grounding for a companion conversational agent (e.g., a Gem), so keep them rich.
3. **Strip-for-publish.** Producing the public artifact strips the metadata frontmatter and every INTERNAL block, then (optionally) renders to HTML/PDF. The build refuses to emit output that still contains internal markers — internal content leaking into a public document is the one outcome this skill exists to prevent.

## Supporting Files

| File | Purpose |
|------|---------|
| `README.md` | Design document — decisions, lineage, dependencies, roadmap, Best Practices, Changelog |
| `scripts/strip_internal.py` | Strip metadata frontmatter + all INTERNAL blocks → clean public markdown; verify no internal content survives |
| `scripts/lint_doc.py` | Advisory lint: brand/style/written-guideline checks + internal-leak + `[VERIFY]` flags, read from the project config. Reports by severity; never blocks |
| `scripts/render.py` | `build` renderer: strip → pandoc → PDF/HTML (mermaid pre-rendered). PDF via `cdp_print.js`. Reads `tools/public-doc/brand.yml` `pdf:` (logo, copyright) + frontmatter `author`/`updated` for the title page |
| `scripts/cdp_print.js` | PDF step — drives Chrome via DevTools `Page.printToPDF` (node built-in WebSocket, no npm install): correct pagination + a running logo header and copyright footer with **no file-path stamp**. Falls back to Chrome-CLI (old headless) if node is absent |
| `templates/draft-doc.md` | Scaffold for a new draft: `public_doc:` frontmatter + structure + INTERNAL-block examples |
| `templates/project-config/` | Seed files copied into `tools/public-doc/` by `init` (`brand.yml`, `style.md`, `lint-rules.yml`, `README.md`) |
| `references/internal-blocks.md` | Full spec for the INTERNAL-block + metadata conventions (read when authoring or extending the strip/lint logic) |

## The INTERNAL-block convention (load-bearing — read before authoring)

INTERNAL blocks separate everything that must NOT be published — internal metadata (purpose, audience, goals, campaign), supporting evidence, positioning rationale, planning notes — from the public prose. They are delimited by `INTERNAL:BEGIN [label]` / `INTERNAL:END` sentinels and are removed at `build`. Two forms:

**1. Collapsible block (primary — use for metadata + any multi-line context).** Paired comment sentinels wrap a `<details>` element so the block *folds away* in GitHub/preview and the author sees the public content by default:

```markdown
<!-- INTERNAL:BEGIN metadata -->
<details>
<summary>🔒 INTERNAL — purpose, audience, context (stripped on publish)</summary>

**Purpose:** … **Audience:** … **Goals:** …
Source: FDA Purolea warning letter (2026-04). Strengthens §3. [VERIFY] the date.

</details>
<!-- INTERNAL:END -->
```

- Collapsible in any view that renders `<details>` (GitHub, VS Code preview). Authors fold internal context away and focus on what ships.
- **Everything before the first public section should be a collapsible INTERNAL block** — title stays public, but purpose/audience/goals/key-points/planning go inside it.
- The paired form tolerates `-->` and arbitrary markup in its body (strip anchors on the `INTERNAL:END` sentinel, not on the first `-->`).

**2. Single comment (terse alternative — tiny inline notes).** Both markers inside one HTML comment; fully hidden in every view:

```markdown
<!-- INTERNAL:BEGIN evidence
One-line note or citation, invisible even if strip is skipped.
INTERNAL:END -->
```
- Constraint: its body must not contain `-->` (it would close the comment early). `lint` flags that. Prefer the collapsible form for anything longer than a line.

**Both forms:** `[label]` is optional free-text (`metadata`, `evidence`, `rationale`, `citation`, `talk-track`) and is surfaced by lint. `strip`/`build` remove either form and verify no marker survives. Because the collapsible form keeps content in the HTML DOM until stripped, **always publish via `build`, never the raw file.** Full spec in `references/internal-blocks.md`.

## Actions

Parse the user's argument string `$ARGUMENTS` to determine the action. If empty or "help", show the actions below.

### `init`

Scaffold the project-level config so this project's brand/style/lint values exist for the skill to read. Idempotent.

1. Create `tools/public-doc/` at the project root if missing.
2. For each file in the skill's `templates/project-config/`, copy it to `tools/public-doc/` **only if it does not already exist** (never clobber a project's customized config). Files: `brand.yml`, `style.md`, `lint-rules.yml`, `README.md`.
3. Report which files were created vs. already present, and remind the user to fill `brand.yml` / `style.md` with their real values (the seeds are placeholders unless this project has already populated them).

> The skill never hard-codes company values. Everything company-specific (names, taglines, banned words, required disclaimers) lives in `tools/public-doc/` and is read at `lint`/`build` time. This is what keeps the skill registry-safe and reusable.

### `new <slug>`

Create a new external-doc draft.

1. Choose the destination with the user (e.g., `whitepapers/<series>/<slug>.md`, `marketing-articles/<slug>.md`). Default to the directory under discussion.
2. Copy `templates/draft-doc.md` to the destination, renamed to `<slug>.md`.
3. Fill the `public_doc:` frontmatter from what's known (title, doc_type, audience, campaign, owner, today's date, `public_filename`). Leave `goals` as prompts if unknown.
4. Tell the user the path and point them at the INTERNAL-block examples in the scaffold.

### `lint <file>`

Run the advisory lint and report — **never blocks** (this is the current policy; see README roadmap for the planned hard leak-gate).

```bash
python3 .claude/skills/public-doc/scripts/lint_doc.py <file>
```

The script reads `tools/public-doc/brand.yml`, `style.md`, and `lint-rules.yml` (if present) and reports findings grouped by severity:
- **leak** — internal markers / metadata that would reach the public artifact, malformed INTERNAL blocks, `-->` inside a block.
- **brand** — naming/tagline/disclaimer rules from `brand.yml`.
- **style** — written-guideline patterns from `lint-rules.yml` (banned words, passive-voice flags, etc.).
- **verify** — unresolved `[VERIFY]` flags.

Summarize the findings for the user and offer to fix the high-value ones. Exit code is always 0 — lint is advisory.

### `build <file>`

Produce the public-facing artifact.

1. Run `lint` first and surface any findings (advisory — proceed unless the user stops you).
2. Strip + render:
   ```bash
   python3 .claude/skills/public-doc/scripts/render.py <file> --format pdf
   # or: --format html  (skip Chrome/PDF step), --format md (strip only, no render)
   # structure flags: --brief "…" (title-page brief; else from frontmatter),
   #                  --no-toc, --no-title-page
   # title-page / chrome flags: --author "…", --date "…" (byline + date line;
   #                  author else frontmatter public_doc.author, date else `updated`),
   #                  --logo <png|svg> (running header), --footer "…" (copyright line)
   #                  — logo + footer default from tools/public-doc/brand.yml `pdf:` block.
   ```
   The renderer strips the `public_doc:` frontmatter and every INTERNAL block, **aborts if any internal marker survives the strip**, then renders the clean markdown. The output is structured as **title page → table-of-contents page → content sections**: the title page shows `public_doc.title` + `public_doc.brief` + author + date (centered); the TOC is generated from the section headings (depth 2) and its links are preserved as clickable PDF anchors; then the content. Pipeline = mermaid → SVG, pandoc (`--toc`) → HTML, then **`cdp_print.js`** (Chrome DevTools `Page.printToPDF`) for a running logo header + copyright footer (no file-path stamp). Output name comes from `public_doc.public_filename`; output lands next to the source (or `--out <dir>`). **Author the draft body with NO title H1** — the title page is generated from frontmatter, so a body `# Title` would duplicate it.

   For this to work, author the draft so the **body has no title H1** (the title comes from frontmatter and renders on the title page) — the first body heading is the first content section.
3. External tools the PDF path needs: `pandoc`, `npx`/`@mermaid-js/mermaid-cli` (only if the doc has mermaid), and a Chrome/Chromium binary (auto-detected; override with `--chrome <path>` or `$PUBLIC_DOC_CHROME`). `--format md` and `--format html` (no mermaid) need none of these. The script reports clearly if a tool is missing rather than producing a broken artifact.

## Notes

- The published artifact is a *derived* artifact — the draft markdown is the source of truth. Re-run `build` after edits; don't hand-edit the output.
- INTERNAL content is also the grounding corpus for a companion agent (Gem). Keep it complete and current even though it never ships in the deck/PDF — same philosophy as keeping a content doc complete.
- If `$ARGUMENTS` is empty or "help", show the actions above.
