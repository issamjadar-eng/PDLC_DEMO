# Strategy Scanner Agent

Self-contained agent prompt for the `/strategy scan` action. Launched as an Explore subagent (read-only).

## Task

Scan all task documents for `<!-- STRATEGY CONTENT: ... -->` tagged blocks and report what's found. Every strategy domain is `shared` (v10+), so there is no per-DHF routing to resolve — one output file per domain, project-wide.

## Input

The caller may provide an optional domain filter. If provided, only report blocks matching that domain.

**Domain filter**: {{DOMAIN_FILTER}}

## Domain Catalog

**Read the canonical domain catalog from `project.yml:strategy_domains[]` at startup.** Each entry has `key`, `name`, `scope`, `output_path`, `template`, `scope_description`, `plans_informed[]`.

Build a set of recognized domain keys from `key` values. Build a lookup `key → output_path` for assembly-status reporting.

**Fallback (graceful degradation)**: if `project.yml:strategy_domains[]` is missing, emit an INFO notice (`"project.yml has no strategy_domains[] block — falling back to hard-coded defaults; consider running /strategy domains reseed"`) and use this default set: `regulatory`, `commercial`, `architecture`, `development`, `testing`, `risk`, `postmarket`, `operations`.

## Tag Convention (v10)

Strategy content is tagged in task documents with HTML comment blocks:

```
<!-- STRATEGY CONTENT: domain, topic1, topic2 -->
```

**Format rules:**
- **First value** = domain key (must match one of the keys from the Domain Catalog above)
- **Remaining values** = topics (free-form, comma-separated)
- Tag must appear on a **line by itself** (not inside prose, code blocks, or backticks)

**Deprecated scope key**: Earlier versions supported `dhf=<leaf>` to route per-dhf domain blocks to a specific DHF. As of v10 every domain is `shared`, so the key is unnecessary. If present, strip it from the topics list and emit a one-line info notice: `INFO: task <id> section '<heading>' has a legacy dhf=<value> key — safe to remove on next edit`. No error.

## Block Boundary Rules

- A tagged block **starts** at the tag comment line
- A tagged block **ends** at the next `## ` heading (level-2 markdown heading) or end of file
- The `## ` heading immediately **above** the tag is the **section heading** (block title)
- Subsection headings within the block (`### `, `#### `) are content — count them

## Review Markers

The line immediately after a `<!-- STRATEGY CONTENT -->` tag may contain a review marker recording a prior conflict resolution. Check for these patterns:

| Marker | Status to report |
|--------|-----------------|
| `<!-- STRATEGY REVIEWED: superseded by task NNN -->` | `superseded (task NNN)` |
| `<!-- STRATEGY REVIEWED: coexists with task NNN -->` | `coexists (task NNN)` |
| `<!-- STRATEGY REVIEW: pending, conflicts with task NNN -->` | `pending review (task NNN)` |
| (no marker) | `active` |

## Scanning Algorithm

1. **Find task files**: Glob for `tasks/*/[0-9][0-9][0-9]-*.md`
2. **For each file**, search for lines matching `<!-- STRATEGY CONTENT` that appear on a line by themselves
3. **For each tagged block found**, extract:
   - **Task ID**: 3-digit prefix from filename (e.g., `033`)
   - **Task title**: From line 1 (`# NNN — Title`)
   - **Created date**: From `**Created**: YYYY-MM-DD` field
   - **Section heading**: The `## ` heading immediately above the tag
   - **Domain**: First comma-separated value in the tag
   - **Topics**: Remaining comma-separated values (excluding any deprecated `dhf=` key)
   - **Review status**: Check the line after the tag for review markers (see Review Markers section)
   - **Subsection count**: Number of `### ` headings between the tag and the next `## ` or EOF
   - **Last modified**: Most recent date in the task's `## Changelog` section
4. **Flag issues**:
   - Tags where first value is not in the Domain Catalog keys → warn with suggestion, listing the known keys from the catalog
   - Tags with no values at all → warn about empty tag
   - Tags carrying a legacy `dhf=<value>` key → INFO (safe to remove)
5. If domain filter was provided, keep only matching blocks

## Output Format

Report a markdown summary table:

```
Strategy Content Sources

| Task | Section | Domain | Topics | Subsections | Status | Last Modified |
|------|---------|--------|--------|-------------|--------|---------------|

N tasks, M subsections across K domain(s)
N superseded blocks (excluded from assembly)
N pending reviews (will re-prompt on next assembly)
```

If any issues were flagged, list them after the table under a `### Issues` heading. Include the task ID, section heading, tag text, and suggested fix for each issue.

## Assembly status reporting

For each domain found in the scan, look up its `output_path` from the Domain Catalog (loaded at startup from `project.yml:strategy_domains[]`). Check whether the assembled strategy document exists at that path.

One output file per domain, regardless of how many DHFs the project has. Per-component nuance is carried by callout subsections inside each shared doc (see `templates/default-strategy.md` and `templates/regulatory-strategy.md`).

If the file exists, read the `<!-- Assembled: YYYY-MM-DD -->` line and report the assembly date. If it doesn't exist, note "not yet assembled".

## Important

- This is a **read-only** scan. Do not create or modify any files.
- Report all findings back in a single, concise response.
- Include the raw data needed for the caller to decide next steps (assemble, update tags, resolve legacy scope keys, etc.).
