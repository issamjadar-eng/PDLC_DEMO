# Task Content Scanner

Shared scanning logic for skills that harvest tagged content from task documents. Referenced by `/strategy` and `/lessons` skills.

## Supported Tag Types

| Tag Pattern | Used By | Domain Routing |
|-------------|---------|----------------|
| `<!-- STRATEGY CONTENT: domain, topic1, topic2 -->` | `/strategy` | First value = domain key |
| `<!-- LESSONS LEARNED: category1, category2 -->` | `/lessons` | First value = category |

## Scanning Algorithm

### Step 1 — Find Task Files

Glob pattern: `tasks/*/[0-9][0-9][0-9]-*.md`

This matches the task naming convention (`NNN-short-name.md`) across all team member folders.

### Step 2 — Find Tagged Blocks

For each task file, search for lines matching the tag pattern: `<!-- TAG_TYPE` (where TAG_TYPE is `STRATEGY CONTENT` or `LESSONS LEARNED`).

**Tag line requirements** (all must be true for a line to be a block marker):
- Line contains `<!-- TAG_TYPE`
- Line contains only the HTML comment (after trimming whitespace) — no surrounding prose
- Line is NOT inside a fenced code block (``` or ~~~)
- Line is NOT inside inline code (backticks)

This distinguishes block markers from inline references to the tag convention.

### Step 3 — Extract Block Content

A tagged block spans from the tag line to the **next `## ` heading** (level-2 markdown heading) or **end of file**, whichever comes first.

- The tag comment line itself is **metadata**, not content
- The `## ` heading immediately above the tag is the **section heading** (block title)
- Subsection headings within the block (`### `, `#### `, etc.) are part of the content
- Blank lines between the tag and the first content line are stripped

### Step 4 — Extract Metadata

For each tagged block, extract:

| Field | Source | Example |
|-------|--------|---------|
| Task ID | Filename (3-digit prefix) | `033` |
| Task title | First line: `# NNN — Title` | `Module Architecture & Classification` |
| Task owner | Field: `**Owner**: Name` | `Ben Xavier` |
| Created date | Field: `**Created**: YYYY-MM-DD` | `2026-04-07` |
| Section heading | `## ` heading above the tag | `Regulatory Strategy` |
| Tag values | Comma-separated between `: ` and ` -->` | `regulatory, classification, jurisdiction` |
| Domain/category | First tag value (for STRATEGY CONTENT) | `regulatory` |
| Topics/categories | Remaining tag values | `classification, jurisdiction` |
| Review status | Review marker on line after tag (see below) | `active`, `superseded (task 040)` |
| Last modified | Most recent date in `## Changelog` | `2026-04-08` |
| Subsections | All `### ` headings within the block | `["Multi-Jurisdiction Classification", "Filing Sequence Strategy"]` |

### Step 4a — Check Review Markers (STRATEGY CONTENT only)

For `STRATEGY CONTENT` tags, check the line immediately after the tag for a review marker comment. These markers record prior conflict resolutions from `/strategy assemble`:

| Pattern | Status |
|---------|--------|
| `<!-- STRATEGY REVIEWED: superseded by task NNN -->` | `superseded (task NNN)` — block excluded from assembly |
| `<!-- STRATEGY REVIEWED: coexists with task NNN -->` | `coexists (task NNN)` — confirmed complementary |
| `<!-- STRATEGY REVIEW: pending, conflicts with task NNN -->` | `pending review (task NNN)` — deferred, re-prompts next assembly |
| (no marker) | `active` — normal block |

### Step 5 — Report

Output a summary table:

```
| Task | Section | Domain | Topics | Subsections | Last Modified |
|------|---------|--------|--------|-------------|---------------|
```

## Domain Validation (Strategy Content Only)

When scanning for `STRATEGY CONTENT`, check the first tag value against recognized domain keys. If it doesn't match:
- Flag the tag: `"Tag in task NNN has unrecognized domain 'xyz'. Known domains: regulatory, commercial, architecture, development, testing, risk, postmarket"`
- Route to `uncategorized` domain for backward compatibility

## Notes

- This document defines the algorithm. Each consuming skill (strategy, lessons) implements it using Glob, Grep, and Read tools.
- The block boundary rule (`## ` heading) means tagged sections should be self-contained under a level-2 heading. Content under the same `## ` heading but ABOVE the tag is NOT included in the block.
- Multiple tags can exist in the same task file (different sections, potentially different domains).
