# Rule: Sentinel Blocks for Auto-Rendered Structural Content

Persistent docs (READMEs, CLAUDE.md) often contain sections whose contents are derived from structural sources of truth — the actual folder tree, `project.yml`, or similar. Those sections go stale when the source changes and nothing re-renders the doc.

Sentinel blocks solve this: a fenced region inside the doc that is owned by a tool, while the rest of the file is owned by humans. Tools regenerate the sentinel region on every run; human narrative outside the sentinels is untouched.

## Syntax

```markdown
<!-- AUTO:STRUCTURE kind=<kind> source=<source> -->
... regenerated content ...
<!-- /AUTO:STRUCTURE -->
```

- The opening sentinel carries **attributes** that tell the renderer what to generate and where to source it from.
- The closing sentinel has **no attributes** — it only closes the most recent opening sentinel.
- Everything between the sentinels is **owned by the renderer**. Hand-edits inside will be lost on next render.
- Everything outside the sentinels is **owned by humans**. Tools never touch it.
- Sentinels are HTML comments — invisible in rendered markdown, so READMEs read normally.
- A single file may contain multiple sentinel blocks with different `kind`/`source` pairs.

## Attributes

### `kind=<kind>`

What content gets rendered inside the block. Defined kinds:

| Kind | Rendered content |
|------|------------------|
| `subfolder-table` | Markdown table listing immediate subfolders of the README's folder. Columns: `Folder`, `Purpose`. |
| `dhf-table` | Markdown table listing DHFs from `project.yml` `dhfs[]`. Columns: architecture name, role, classification flags, filing. |
| `team-table` | Markdown table listing active team members from `project.yml` `team.active[]`. Columns: name, role, github. |
| `folder-tree` | Fenced code block showing the top-level folder tree of the project root. |
| `folder-tree-subset` | Fenced code block showing the folder tree under a specific path (used for deep-nested sections of CLAUDE.md). |
| `strategy-domains` | Markdown table listing strategy domains from `project.yml` `strategy_domains[]`. Shape depends on `variant=<name>` attribute (see below). |
| `doc-governance` | Short markdown banner listing the QMS forms / parent SOPs / work instructions / upstream-input forms that govern producing this document. Sourced from the nearest ancestor `.taxonomy.yml` `mappings[<slug>].governing_qms` block. See variant section below. |

Adding a new kind is a convention change — update this rule file and the renderer simultaneously.

### `source=<source>`

Where the renderer reads its data from. Defined sources:

| Source | Meaning |
|--------|---------|
| `fs` | Filesystem scan. For `subfolder-table`, scans the README's folder; for `folder-tree`, scans the project root; for `folder-tree-subset`, scans the path in a `path=<rel>` attribute. |
| `project.yml:dhfs` | Reads `dhfs[]` from `project.yml`. |
| `project.yml:team.active` | Reads `team.active[]` from `project.yml`. |
| `project.yml:strategy_domains` | Reads `strategy_domains[]` from `project.yml`. |
| `project.yml:<path>` | Generic source form — reads a specific YAML path. |
| `taxonomy` | Reads the nearest ancestor `.taxonomy.yml` (walking up from the target file). Used by `kind=doc-governance`. |
| `taxonomy:<slug>` | Same source as `taxonomy` but with an explicit `<slug>` override for the `mappings[]` key. Default slug is the target file's parent folder name (the doctype-folder convention). |

### Optional attributes

| Attribute | Meaning |
|-----------|---------|
| `path=<relpath>` | For `kind=folder-tree-subset` (and `kind=folder-tree` if scoping to a subdirectory). Path relative to project root. |
| `depth=<N>` | For `kind=folder-tree` and `kind=folder-tree-subset`. Levels to recurse. Default: `1` for `folder-tree` (top-level only), `2` for `folder-tree-subset` (one level into subtree). Hard-capped at `4` to prevent runaway output. |
| `exclude=<glob,glob,...>` | Comma-separated glob patterns to omit from the scan. Defaults to `formal,.git,.venv,__pycache__,node_modules,images,.staging,assets`. Applied at every depth for recursive trees. |
| `preserve-column=<column-name>` | For table kinds: when regenerating, preserve the values in the named column from the old table's rows (matched by primary key — first column). Default: `Purpose` for `subfolder-table`; `Marketed Name` for `dhf-table` (or `Purpose` for `dhf-table variant=flat-multi`). Applied as the *last* fallback after reading the project.yml field. |
| `variant=<name>` | For `kind=strategy-domains` and `kind=dhf-table`. Selects which table shape to render (see variant sections below). |

## `dhf-table` variants

The `dhf-table` kind reads `project.yml:dhfs[]` and supports three variants, selected by the `variant=<name>` attribute. All three read `architecture_name`, `marketed_name`, `role`, `classification.{samd,class,iec62304,ai_enabled}`, `filing`, and (for `flat-multi` only) `dhf_purpose` from each entry.

| Variant | Columns | Where it's used |
|---------|---------|-----------------|
| `default` (no variant attr) | Architecture Name \| Marketed Name \| Role \| Classification \| IEC 62304 \| Filing | General-purpose DHF roster |
| `naming` | Architecture Name \| Marketed Name \| Classification \| IEC 62304 | `CLAUDE.md` → Module Naming table — concise device-naming card |
| `flat-multi` | DHF \| `role` \| Classification \| Purpose | `CLAUDE.md` → Flat Multi-DHF Shape table — emphasizes the DHF leaf + role + a one-line purpose |

**Column derivation:**

- `Architecture Name`: backtick-bold `**{architecture_name}**`, falling back to `**{leaf}**` if `architecture_name` is missing.
- `Marketed Name`: `marketed_name` from project.yml, falling back to preserve-column lookup, then `TODO`.
- `Role`: `role` verbatim (`system`, `item`).
- `Classification`: `device-level` for system DHFs; `{SaMD|non-SaMD}, Class {class}, AI-enabled` for item DHFs (AI suffix only when `ai_enabled: true`).
- `IEC 62304`: `n/a` for system DHFs; `Class {iec62304}` for item DHFs.
- `Filing`: `filing` verbatim, e.g. `510k+pccp`.
- `DHF` (flat-multi only): backticked `` `{leaf}` ``.
- `Purpose` (flat-multi only): `dhf_purpose` from project.yml, falling back to preserve-column lookup, then `TODO`.

## `strategy-domains` variants

The `strategy-domains` kind supports three variants, selected by the `variant=<name>` attribute on the opening sentinel. All three read the same source (`project.yml:strategy_domains[]`) — they differ in which columns they render.

| Variant | Columns | Where it's used |
|---------|---------|-----------------|
| `expected-content` | `File` \| `Purpose` | `docs/project/strategies/README.md`, `.claude/skills/medtech-docs/templates/readme-strategies.md` — Expected Content tables |
| `registry` (default) | `Domain Key` \| `Domain Name` \| `Scope` \| `Output Path` \| `Template` \| `Plans Informed` | `.claude/skills/strategy/SKILL.md` — Domain Registry table |
| `init-briefs` | `Domain` \| `What Belongs Here` \| `Plans Table Rows` | `.claude/skills/strategy/SKILL.md` — Domain brief content table (for `/strategy init`) |

**Column derivation:**

- `expected-content`:
  - `File` = backtick-wrapped basename of `output_path` (e.g. `` `regulatory-strategy.md` ``)
  - `Purpose` = `scope_description` verbatim
- `registry`:
  - `Domain Key` = backtick-wrapped `key`
  - `Domain Name` = `name`
  - `Scope` = `scope`
  - `Output Path` = backtick-wrapped `output_path`
  - `Template` = backtick-wrapped `template`
  - `Plans Informed` = `plans_informed[]` joined with `, `
- `init-briefs`:
  - `Domain` = backtick-wrapped `key`
  - `What Belongs Here` = `what_belongs_here[]` joined with `; ` (no trailing period)
  - `Plans Table Rows` = `plans_table[]` rendered as `{name} \| {description}; ...` (escaped pipes)

## `doc-governance` source layout

The `doc-governance` kind reads `<nearest-ancestor>/.taxonomy.yml` and looks up `mappings[<slug>].governing_qms`. The taxonomy schema for `governing_qms` is documented in the taxonomy file's own header comment block (schema v0.3+); the shape is:

```yaml
governing_qms:
  forms: [FORM-NNNNNNNNN, ...]          # Templates the doc instantiates
  sops: [SOP-NNNNNNNNN, ...]            # Parent SOP(s) governing process
  work_instructions: [WI-NNNNNNNNN, ...] # WI(s) refining the SOP for this doctype
  upstream_inputs: [FORM-NNNNNNNNN, ...] # Forms whose output feeds this doctype
  note: |
    Free-text — used as the first line of the rendered banner's blockquote.
```

**Banner shape rendered:**

```markdown
**Governance** _(auto-rendered from `.taxonomy.yml`; edit there to change)_

- **Form(s)**: `FORM-NNNNNNNNN`
- **Parent SOP(s)**: `SOP-NNNNNNNNN`
- **Work Instruction(s)**: `WI-NNNNNNNNN`
- **Upstream input form(s)**: `FORM-NNNNNNNNN`, `FORM-NNNNNNNNN`

> First line of the taxonomy's `note:` field.
```

**Three null cases (each renders a discoverable italic line, not an error):**

1. `.taxonomy.yml` not found → _"no .taxonomy.yml found between this file and the project root."_
2. Slug not in `mappings[]` → _"slug `<slug>` not declared in `<path>/.taxonomy.yml` `mappings[]`."_
3. Mapping present but no `governing_qms` block → _"has no `governing_qms` block — TBD authoring."_

These render as visible markdown so authors notice the gap on re-render; they do not abort the render.

**Bare mapping case** (mapping exists with `governing_qms` but every list is empty): the banner renders the `note:` first line OR a default "No QMS form declared — team-internal convention." line. Distinguishes "intentionally no form" from "TBD" — both stay discoverable in the rendered doc.

## Rendering rules

1. **Idempotent**: running the renderer N times with no source change produces the same byte sequence.
2. **Merge, don't clobber**: for table kinds with `preserve-column`, the renderer looks up the old table (if present) and copies preserved-column values into matching rows of the new table (keyed by first column). New rows with no match get a `TODO` placeholder in the preserved column.
3. **Missing sentinels are not an error**: a doc without sentinels renders to itself — the renderer is a no-op.
4. **Malformed sentinels are an error**: an unclosed opening sentinel, mismatched kind attributes, or unknown `kind`/`source` value → the renderer aborts with a non-zero exit code and leaves the file unchanged.
5. **Sentinels are preserved**: the opening and closing sentinel lines themselves are preserved verbatim — the renderer only replaces content between them.

## Who invokes the renderer

| Skill | When |
|-------|------|
| `/medtech-docs init` | Step 3 and subsequent — after writing each README template, render every sentinel block it contains. |
| `/medtech-docs add-dhf` | Step 3 (scaffold) — render sentinels in newly created READMEs. Step 4 additionally — re-render affected parent-README sentinels to include the new DHF. |
| `/best-practices fix` (Phase 3) | Invoked by the `fix` action after audit flags drift inside a sentinel region — re-renders just the drifted sentinels. |

## Where sentinels are used in this repo

Canonical locations:

| Doc | Sentinel kinds |
|-----|----------------|
| `CLAUDE.md` → Project Structure code block | `folder-tree` |
| `CLAUDE.md` → Module Naming table | `dhf-table` |
| `docs/project/README.md` → Structure table | `subfolder-table` |
| `docs/project/dhfs/README.md` → Structure table | `subfolder-table` |
| `docs/**/README.md` with `## Structure` | `subfolder-table` (via medtech-docs templates) |
| `docs/project/dhfs/<dhf>/README.md` → Structure table | `subfolder-table` (via `readme-dhf.md` template) |
| `docs/project/strategies/README.md` → Expected Content table | `strategy-domains variant=expected-content` |
| `.claude/skills/medtech-docs/templates/readme-strategies.md` → Expected Content table | `strategy-domains variant=expected-content` |
| `.claude/skills/strategy/SKILL.md` → Domain Registry table | `strategy-domains variant=registry` |
| `.claude/skills/strategy/SKILL.md` → Domain brief content table (init action) | `strategy-domains variant=init-briefs` |
| Per-doctype Confluence page (e.g., `_confluence/.../<slug>/v1.0.0.md`, `_confluence/.../<slug>/index.md`) → Governance banner above page body | `doc-governance source=taxonomy` (slug auto-derived from parent folder name) or `doc-governance source=taxonomy:<slug>` for explicit overrides |

New docs with structural tables should wrap those tables in sentinels from the start.

## Interaction with other rules

- **`.claude/rules/readme-before-write.md`**: still applies. Sentinels do not change the "read target + parent README before writing" requirement. They only change what happens to the Structure table once the file exists.
- **Best-practices README section-order check**: sentinels live inside a section heading (`## Structure`), not between sections. They do not affect section ordering.
- **Best-practices changelog-currency check**: when `/best-practices fix` regenerates sentinels, it appends a changelog row to the affected README with today's date.

## Implementation

The renderer lives at `.claude/skills/medtech-docs/scripts/render-sentinels.py`. It is:
- **Idempotent** — multiple runs with unchanged sources yield identical output.
- **Single-file-at-a-time** — invoked once per target file.
- **Non-destructive** — on error, leaves the file unchanged and exits non-zero.
- **Read-only outside sentinels** — never modifies content outside the block boundaries.

Usage: `python3 .claude/skills/medtech-docs/scripts/render-sentinels.py <path-to-file>`. Pass `--dry-run` to print the proposed new content to stdout without writing.
