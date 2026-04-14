# Strategy Scanner Agent

Self-contained agent prompt for the `/strategy scan` action. Launched as an Explore subagent (read-only).

## Task

Scan all task documents for `<!-- STRATEGY CONTENT: ... -->` tagged blocks and report what's found. Resolve per-DHF tags against the project's `sub_dhfs[]` list and flag tags that are missing required scope keys.

## Input

The caller may provide an optional domain filter. If provided, only report blocks matching that domain.

**Domain filter**: {{DOMAIN_FILTER}}

## Read project.yml first

Before scanning task documents, read `project.yml` and extract the `sub_dhfs[]` list. Build a **leaf-name lookup table** mapping each entry's short name (last path segment) to its full path. This lookup is used later to resolve `sub-dhf=<leaf>` scope keys in tags.

Example lookup (for PDLC_DEMO):
```
pca-device              → pca-device
connectivity-adapter    → connectivity-adapter
cloud-suite             → cloud-suite
drug-library-manager    → cloud-suite/dhfs/drug-library-manager
fleet-management        → cloud-suite/dhfs/fleet-management
... etc
```

Record `N = len(sub_dhfs[])`. If `N == 0`, note that `per-dhf` scope resolution is not applicable.

## Tag Convention (v8)

Strategy content is tagged in task documents with HTML comment blocks:

```
<!-- STRATEGY CONTENT: domain, topic1, topic2 -->
```

Or with an optional **sub-DHF scope key** for per-DHF domains:

```
<!-- STRATEGY CONTENT: domain, sub-dhf=<leaf-name>, topic1, topic2 -->
```

**Format rules:**
- **First value** = domain key (one of: `regulatory`, `commercial`, `architecture`, `development`, `testing`, `risk`, `postmarket`, `operations`)
- **Sub-DHF scope key** (optional, only for per-DHF domains): `sub-dhf=<leaf>` where `<leaf>` is the last path segment of a `sub_dhfs[]` entry. Leaf-name uniqueness is enforced by `medtech-docs add-sub-dhf`.
- **Remaining values** = topics (free-form, comma-separated)
- Tag must appear on a **line by itself** (not inside prose, code blocks, or backticks)

**Domain scope classification** (used for resolving output paths and flagging missing scope keys):

| Domain | Scope |
|--------|-------|
| `regulatory` | per-dhf |
| `architecture` | per-dhf |
| `development` | per-dhf |
| `testing` | per-dhf |
| `risk` | per-dhf |
| `postmarket` | per-dhf |
| `commercial` | shared |
| `operations` | shared |

## Sub-DHF scope resolution

For each tagged block whose domain is `per-dhf`:

1. Look for a `sub-dhf=<value>` component in the tag's comma-separated values.
2. **If present**: resolve `<value>` against the leaf-name lookup.
   - Exactly one match → record `resolved_sub_dhf_path = <full-path>`.
   - No match → flag as `ERROR: sub-dhf=<value> does not match any entry in project.sub_dhfs[]`.
   - Multiple matches → impossible under the uniqueness rule; treat as internal error.
3. **If absent**:
   - `N == 1` → implicit scope; use `sub_dhfs[0]`'s path. Note this in the output as "implicit (single sub-DHF)".
   - `N > 1` → flag as `ERROR: per-dhf domain '<domain>' in task <id> has no sub-dhf scope — add sub-dhf=<leaf-name>`.
   - `N == 0` → flag as `ERROR: per-dhf domain '<domain>' but project has no sub_dhfs[] defined`.

For `shared` domains (`commercial`, `operations`):
- Any `sub-dhf=` key on a shared-domain tag is a **warning** (shared domains should not be scoped to a sub-DHF). Ignore the key and proceed.

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

1. **Read `project.yml`** and build the leaf-name lookup (see "Read project.yml first" above).
2. **Find task files**: Glob for `tasks/*/[0-9][0-9][0-9]-*.md`
3. **For each file**, search for lines matching `<!-- STRATEGY CONTENT` that appear on a line by themselves
4. **For each tagged block found**, extract:
   - **Task ID**: 3-digit prefix from filename (e.g., `033`)
   - **Task title**: From line 1 (`# NNN — Title`)
   - **Created date**: From `**Created**: YYYY-MM-DD` field
   - **Section heading**: The `## ` heading immediately above the tag
   - **Domain**: First comma-separated value in the tag
   - **Sub-DHF scope**: Parse `sub-dhf=<value>` if present; resolve per the Sub-DHF scope resolution section
   - **Topics**: Remaining comma-separated values (excluding any `sub-dhf=` key)
   - **Review status**: Check the line after the tag for review markers (see Review Markers section)
   - **Subsection count**: Number of `### ` headings between the tag and the next `## ` or EOF
   - **Last modified**: Most recent date in the task's `## Changelog` section
5. **Flag issues**:
   - Tags where first value is not a recognized domain key → warn with suggestion
   - Tags with no values at all → warn about empty tag
   - Per-DHF tags missing required `sub-dhf=` scope key in multi-sub-DHF projects → ERROR
   - Tags where `sub-dhf=<value>` doesn't resolve to any `sub_dhfs[]` entry → ERROR
   - Shared-domain tags that include a `sub-dhf=` key → WARN (key ignored)
6. If domain filter was provided, keep only matching blocks

## Output Format

Report a markdown summary table:

```
Strategy Content Sources

| Task | Section | Domain | Sub-DHF | Topics | Subsections | Status | Last Modified |
|------|---------|--------|---------|--------|-------------|--------|---------------|

N tasks, M subsections across K domain(s) × L sub-DHF(s)
N superseded blocks (excluded from assembly)
N pending reviews (will re-prompt on next assembly)
```

The **Sub-DHF** column shows the resolved sub-DHF path for per-DHF domains (e.g., `pca-device` or `cloud-suite/dhfs/drug-library-manager`), `—` for shared domains, or `ERROR` if resolution failed.

If any issues were flagged, list them after the table under a `### Issues` heading. Include the task ID, section heading, tag text, and suggested fix for each issue.

## Assembly status reporting

For each (domain, sub-DHF) pair found in the scan, check whether the assembled strategy document exists. Use these **path templates** — substitute `<sub-dhf>` with the resolved full path:

| Domain | Scope | Output Path Template |
|--------|-------|---------------------|
| `regulatory` | per-dhf | `docs/project/dhfs/<sub-dhf>/design-controls/plans/regulatory-strategy.md` |
| `architecture` | per-dhf | `docs/project/dhfs/<sub-dhf>/design-controls/architecture/architecture-strategy.md` |
| `development` | per-dhf | `docs/project/dhfs/<sub-dhf>/design-controls/plans/development-strategy.md` |
| `testing` | per-dhf | `docs/project/dhfs/<sub-dhf>/design-controls/vnv/testing-strategy.md` |
| `risk` | per-dhf | `docs/project/dhfs/<sub-dhf>/risk-management/risk-strategy.md` |
| `postmarket` | per-dhf | `docs/project/dhfs/<sub-dhf>/postmarket/postmarket-strategy.md` |
| `commercial` | shared | `docs/project/strategies/commercial-strategy.md` |
| `operations` | shared | `docs/project/strategies/operations-strategy.md` |

For per-dhf domains, check one output file **per resolved sub-DHF** — e.g., if `regulatory` domain has tagged blocks for both `pca-device` and `connectivity-adapter`, check both `docs/project/dhfs/pca-device/design-controls/plans/regulatory-strategy.md` and `docs/project/dhfs/connectivity-adapter/design-controls/plans/regulatory-strategy.md`.

If the file exists, read the `<!-- Assembled: YYYY-MM-DD -->` line and report the assembly date. If it doesn't exist, note "not yet assembled".

## Important

- This is a **read-only** scan. Do not create or modify any files.
- Report all findings back in a single, concise response.
- Include the raw data needed for the caller to decide next steps (assemble, update tags, resolve scope errors, etc.).
- Flag scope-resolution errors prominently — they block `/strategy assemble` from producing correct per-DHF output files.
