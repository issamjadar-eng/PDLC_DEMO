# Strategy Scanner Agent

Self-contained agent prompt for the `/strategy scan` action. Launched as an Explore subagent (read-only).

## Task

Scan all task documents for `<!-- STRATEGY CONTENT: ... -->` tagged blocks and report what's found.

## Input

The caller may provide an optional domain filter. If provided, only report blocks matching that domain.

**Domain filter**: {{DOMAIN_FILTER}}

## Tag Convention

Strategy content is tagged in task documents with HTML comment blocks:

```
<!-- STRATEGY CONTENT: domain, topic1, topic2 -->
```

- **First value** = domain key (one of: `regulatory`, `commercial`, `architecture`, `development`, `testing`, `risk`, `postmarket`, `operations`)
- **Remaining values** = topics (free-form, comma-separated)
- Tag must appear on a **line by itself** (not inside prose, code blocks, or backticks)

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
   - **Topics**: Remaining comma-separated values
   - **Review status**: Check the line after the tag for review markers (see Review Markers section)
   - **Subsection count**: Number of `### ` headings between the tag and the next `## ` or EOF
   - **Last modified**: Most recent date in the task's `## Changelog` section
4. **Flag issues**:
   - Tags where first value is not a recognized domain key → warn with suggestion
   - Tags with no values at all → warn about empty tag
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

If any issues were flagged, list them after the table under a `### Issues` heading.

Also check: for each domain found, does the assembled strategy document exist? Check these paths:

| Domain | Output Path |
|--------|------------|
| `regulatory` | `docs/project/dhfs/pca-device/design-controls/plans/regulatory-strategy.md` |
| `commercial` | `docs/project/strategies/commercial-strategy.md` |
| `architecture` | `docs/project/dhfs/pca-device/design-controls/architecture/architecture-strategy.md` |
| `development` | `docs/project/dhfs/pca-device/design-controls/plans/development-strategy.md` |
| `testing` | `docs/project/dhfs/pca-device/design-controls/vnv/testing-strategy.md` |
| `risk` | `docs/project/dhfs/pca-device/risk-management/risk-strategy.md` |
| `postmarket` | `docs/project/dhfs/pca-device/design-controls/plans/postmarket-strategy.md` |
| `operations` | `operations-strategy.md` |

If the file exists, read the `<!-- Assembled: YYYY-MM-DD -->` line and report the assembly date. If it doesn't exist, note "not yet assembled".

## Important

- This is a **read-only** scan. Do not create or modify any files.
- Report all findings back in a single, concise response.
- Include the raw data needed for the caller to decide next steps (assemble, update tags, etc.).
