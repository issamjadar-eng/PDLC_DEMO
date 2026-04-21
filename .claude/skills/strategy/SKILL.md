---
name: strategy
description: "Scan task docs for strategy content tagged by domain and assemble into unified shared strategy documents — regulatory, commercial, architecture, development, testing, risk, post-market, operations; topic-first with per-component callouts"
version: 11
updated: 2026-04-20
---

# Strategy Harvester

Scan task documents for tagged strategy content, route by domain, and assemble into unified strategy documents that inform formal plans. Usage: `/strategy <action> [arguments]`

## Supporting Files

| File | Purpose |
|------|---------|
| `templates/regulatory-strategy.md` | Custom template for the regulatory domain (9 sections) |
| `templates/default-strategy.md` | Generic fallback template for domains without a custom template |
| `templates/strategy-brief.md` | Placeholder brief template for domains awaiting first assembly |
| `agents/scanner.md` | Self-contained subagent prompt for the `scan` action (Explore agent, read-only) |
| `agents/assembler.md` | Self-contained subagent prompt for the `assemble` action (general-purpose agent, needs Write) |
| `../shared/task-content-scanner.md` | Shared scanning algorithm (also used by future `/lessons` skill) |

## Tag Convention

Strategy content is marked in task documents with HTML comment tags:

```
<!-- STRATEGY CONTENT: domain, topic1, topic2 -->
```

**Format rules:**
- **First value is the domain key** (required) — must be one of the recognized domain keys below
- **Remaining values are topics** (optional) — free-form, comma-separated, used for section routing in custom templates
- Tag must appear on a **line by itself** — no surrounding prose on the same line
- Tag must NOT be inside a fenced code block or inline code backticks

**Deprecated scope keys (v10)**: Earlier versions supported `dhf=<leaf-name>` to route per-dhf domain blocks to a specific DHF. As of v10 every strategy domain is `shared` (one output file per domain, project-wide), so the routing is unambiguous and the scope key is no longer needed. Tags that still carry `dhf=<value>` are tolerated — the scanner strips the key and emits a one-line info notice suggesting it be removed on next edit. No error. Per-component nuance now lives as **callout subsections** inside the shared strategy doc (see template shape in `templates/default-strategy.md`).

**Block boundary:**
- A tagged block starts at the tag comment line
- A tagged block ends at the next `## ` heading (level-2 markdown heading) or end of file
- The `## ` heading immediately above the tag is the **section heading** (block title)
- Subsection headings within the block (`### `, `#### `) are part of the content and preserved
- The tag line itself is metadata, not content

**Backward compatibility:** If the first value doesn't match a recognized domain key, the entire tag is treated as topics and routed to an `uncategorized` domain. The `scan` action will flag these for correction.

## Review Markers

When the assembler detects overlapping content between tasks, it prompts the lead to resolve the conflict. The resolution is recorded as a review marker comment in the **source task document**, immediately below the `<!-- STRATEGY CONTENT -->` tag. Review markers survive across assemblies because they live in source tasks, not in the generated output.

### Marker Types

| Marker | Meaning | Effect on Scanner | Effect on Assembler |
|--------|---------|-------------------|---------------------|
| `<!-- STRATEGY REVIEWED: superseded by task NNN -->` | This block has been replaced by newer content in task NNN | Scanner **skips** this block entirely | Block excluded from output |
| `<!-- STRATEGY REVIEWED: coexists with task NNN -->` | Confirmed as complementary to overlapping content in task NNN | Scanner includes, notes the pairing | No conflict prompt for this pair |
| `<!-- STRATEGY REVIEW: pending, conflicts with task NNN -->` | Deferred — lead chose not to resolve yet | Scanner includes, flags as pending | **Re-prompts** the lead on next assembly |

### Marker Placement

Markers are placed on the line immediately after the `<!-- STRATEGY CONTENT -->` tag:

```markdown
## Regulatory Strategy

<!-- STRATEGY CONTENT: regulatory, classification, jurisdiction -->
<!-- STRATEGY REVIEWED: coexists with task 040 -->

### Multi-Jurisdiction Classification
...
```

### Supersession by Tag Deletion

The lightest-weight alternative to marking a block as superseded: simply delete the `<!-- STRATEGY CONTENT -->` tag line from the old task. The content stays in the task document (preserving history) but stops flowing into assembled strategy. The assembly changelog auto-logs the removal.

**Example usage in a task document:**

```markdown
## Regulatory Strategy

<!-- STRATEGY CONTENT: regulatory, classification, jurisdiction, filing-sequence -->

### Multi-Jurisdiction Classification

| Module | US (FDA) | EU (MDR) | Canada |
...

### Filing Sequence Strategy

| Order | Market | Pathway | Rationale |
...
```

## Domain Registry

Each domain has a key, output path, template, and list of formal plans it informs. **All domains are `shared`** (v10) — one output file per domain, project-wide. Strategy is a cross-component story: per-component nuance lives as callout subsections inside the shared doc, not as separate per-DHF files.

**Source of truth**: this table is rendered from `project.yml:strategy_domains[]` via a sentinel block (see `.claude/rules/sentinel-blocks.md`). Edit `project.yml`, then run `python3 .claude/skills/medtech-docs/scripts/render-sentinels.py .claude/skills/strategy/SKILL.md` (or invoke via `/medtech-docs` / `/best-practices fix`).

<!-- AUTO:STRUCTURE kind=strategy-domains source=project.yml:strategy_domains variant=registry -->
| Domain Key | Domain Name | Scope | Output Path | Template | Plans Informed |
|-----------|------------|-------|-------------|----------|----------------|
| `regulatory` | Regulatory | shared | `docs/project/strategies/regulatory-strategy.md` | `regulatory-strategy.md` | 510(k), PCCP, Q-Sub, LMR |
| `commercial` | Commercial | shared | `docs/project/strategies/commercial-strategy.md` | `default-strategy.md` | Go-to-market plan, Business case, Market expansion |
| `architecture` | Architecture | shared | `docs/project/strategies/architecture-strategy.md` | `default-strategy.md` | SAD (per DHF), SRS, cybersecurity plan |
| `development` | Development | shared | `docs/project/strategies/development-strategy.md` | `default-strategy.md` | SDP, Config Mgmt Plan |
| `testing` | Testing & Validation | shared | `docs/project/strategies/testing-strategy.md` | `default-strategy.md` | V&V Plan, test protocols, usability plan |
| `risk` | Risk | shared | `docs/project/strategies/risk-strategy.md` | `default-strategy.md` | Risk Mgmt Plan (per DHF), FMEA, risk-benefit analysis |
| `postmarket` | Post-Market | shared | `docs/project/strategies/postmarket-strategy.md` | `default-strategy.md` | Maintenance Plan, PMS Plan (per DHF), LMR, PCCP tracking |
| `operations` | Operations & Tooling | shared | `docs/project/strategies/operations-strategy.md` | `default-strategy.md` | CI/CD & release pipeline, SBOM/SOUP supply chain, cloud infrastructure, QMS operational posture, PM plan, tooling & agentic-infra roadmap, team onboarding |
<!-- /AUTO:STRUCTURE -->

**Output path resolution**: The path column is literal. One output file per domain, regardless of how many DHFs the project has. Cross-component nuance is carried by **per-component callout subsections** inside each shared doc (see `templates/default-strategy.md`).

**Notes from v10 (all-shared)**:
- Every strategy domain is shared. Strategy is a project-level story that describes how the DHFs relate to each other (filing sequence, platform architecture, one SDLC, integration V&V, platform risk chains, unified PMS program). Splitting it per-DHF fractured that story.
- Formal design-control outputs (SDP, SAD, V&V Plan, Risk Mgmt Plan, PMS Plan, cybersecurity plan) **still live per-DHF** in `dhfs/<dhf>/design-controls/`, `risk-management/`, `postmarket/`, and `cybersecurity/`. Only the upstream strategy **briefs** that inform those formal outputs have moved up to `docs/project/strategies/`.
- The v8 per-dhf output paths (`dhfs/<dhf>/design-controls/plans/regulatory-strategy.md`, etc.) are **not** automatically migrated. For PDLC_DEMO, task 009 P1 executes the `git mv`. For fresh projects, the v10 shared paths apply from init time.

**Incubating subtopics** — start as topics within a parent domain, promote to standalone domain when they outgrow it:
- `clinical` → inside `regulatory` until a clinical study is needed
- `cybersecurity` → inside `architecture` until Section 524B complexity warrants separation

**Adding a new domain:** Add a row to the registry table above, optionally create a custom template in `templates/`. No other changes needed.

### Strategy → Plan Traceability

```
Strategy decisions (in tasks, harvested by /strategy)
    ↓ informs
Formal plans (in design-controls/plans/, vnv/, risk-management/)
    ↓ governs
Execution (design controls, V&V, submissions)
    ↓ produces
Evidence (test reports, risk files, submission packages)
```

Each assembled strategy document includes a "Plans Informed" section linking to the formal plans it feeds.

## Regulatory Domain — Topic-to-Section Mapping

The regulatory domain uses a custom template with 9 sections. Source subsections are routed to output sections by matching topic tags and subsection heading text:

| # | Output Section | Matches (heading or topic contains) |
|---|---------------|--------------------------------------|
| 1 | Device & Submission Overview | "submission", "intended use", "one submission" |
| 2 | Module Classification | "classification", "jurisdiction" (when content includes a classification table) |
| 3 | Jurisdictional Differences | "jurisdictional", "MDDS gap", "PCCP US-only" |
| 4 | Filing Sequence | "filing sequence", "filing order" |
| 5 | DHF & Design Planning | "DHF", "DDP", "design planning", "deliverable" |
| 6 | Document Reuse | "document reuse", "reuse matrix", "reuse across" |
| 7 | Pre-Market Strategy | "prototype", "phased", "pre-op filing", "validation" |
| 8 | Q-Sub Questions | "Q-Sub", "pre-submission", "predicted" |
| 9 | Open Items | (aggregated `[VERIFY]` markers from all sections) |

Subsections that don't match any mapping → `## Uncategorized` at the end (signals the mapping table needs a new row).

Matching is case-insensitive and checks both the `### ` heading text and the topic values from the tag.

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform.

### `init`

Generate placeholder strategy briefs for all domains that don't yet have a strategy document (neither a brief nor an assembled document). Safe to re-run — skips domains that already have a file at their output path.

1. For each domain in the registry:
   a. Check if a file exists at the domain's output path. If yes, skip (already has a brief or assembled document).
   b. Read the brief template from `${CLAUDE_SKILL_DIR}/templates/strategy-brief.md`.
   c. Replace template variables using the domain brief content table below:
      - `{{DOMAIN_NAME}}` — domain display name
      - `{{DOMAIN_KEY}}` — domain key
      - `{{WHAT_BELONGS_HERE}}` — bullet list of what belongs in this domain
      - `{{PLANS_TABLE}}` — table rows for plans this domain informs
   d. Write the brief to the domain's output path.
2. Report which briefs were created and which were skipped.

**Domain brief content** (rendered from `project.yml:strategy_domains[]` — edit the manifest, not this table):

<!-- AUTO:STRUCTURE kind=strategy-domains source=project.yml:strategy_domains variant=init-briefs -->
| Domain | What Belongs Here | Plans Table Rows |
|--------|------------------|-----------------|
| `regulatory` | Filing pathway and classification decisions; Multi-jurisdiction strategy (US, EU, Canada); Predicate device selection rationale; PCCP scope decisions; Q-Sub questions and FDA feedback | 510(k) Submission \| Filing pathway, submission structure; PCCP \| Change categories, module scope; Q-Sub \| Questions for FDA; LMR \| Post-clearance tracking |
| `commercial` | Market entry sequence and timing; Launch phasing (which modules ship first); Pricing and reimbursement strategy; Competitive positioning; Customer segmentation; Geographic expansion plans | Go-to-market plan \| Market entry, launch timing; Business case \| Revenue model, pricing; Market expansion \| New indications, geographies |
| `architecture` | Module boundaries and SaMD/non-SaMD split; Technology and vendor selection rationale; Platform decisions; Data architecture and flow design; Cybersecurity architecture approach (until promoted to own domain) | SAD \| Module boundaries, interfaces; SRS \| Requirements-driven architecture decisions; Cybersecurity plan \| Security architecture approach |
| `development` | Development methodology (agile within design controls); Branching and release strategy; Environment management; SOUP/third-party component strategy; CI/CD approach; Coding standards decisions | SDP \| Development process, lifecycle; Config Mgmt Plan \| Branching, versioning, environments |
| `testing` | Test strategy (bench vs. clinical); Acceptance criteria philosophy; AI/ML validation approach; Usability testing strategy (formative vs. summative); Test infrastructure and dataset management; Regression testing approach | V&V Plan \| Test strategy, protocols; Test protocols \| Acceptance criteria; Usability plan \| Formative/summative approach |
| `risk` | Risk-benefit framing and acceptable risk thresholds; FMEA methodology decisions; Risk-driven architecture decisions; Cross-module risk interactions; Post-market risk monitoring approach | Risk Mgmt Plan \| Risk methodology, thresholds; FMEA \| Hazard analysis approach; Risk-benefit analysis \| Framing for submission |
| `postmarket` | Post-market surveillance strategy; Complaint handling approach; Field safety and corrective action; Maintenance cadence and update strategy; LMR structure and reporting cadence; PCCP change tracking process | Maintenance Plan \| Update cadence, process; PMS Plan \| Surveillance approach; LMR \| Change tracking; PCCP tracking \| Modification reporting |
| `operations` | Build, release, and CI/CD pipeline decisions; Supply chain and SOUP/SBOM management; Cloud infrastructure and hosting posture; QMS operational readiness; Project management approach; Tooling and agentic infrastructure decisions; Skill and automation roadmap; Team workflow, onboarding, and knowledge management | CI/CD & release plan \| Build, release, signing; SBOM/SOUP register \| Supply chain posture; Cloud ops runbook \| Hosting, facility equivalent; QMS operational plan \| Design-controls readiness; PM plan \| Ways of working; Tooling roadmap \| Agentic infra, automation; Team onboarding \| Knowledge transfer |
<!-- /AUTO:STRUCTURE -->

**Note:** The `assemble` action checks for `<!-- Status: awaiting-content -->` in the target file. If present, it replaces the entire file with the assembled document. If not present (already assembled), it regenerates normally.

### `scan [domain]`

Find all `<!-- STRATEGY CONTENT` tagged blocks across task documents. Optionally filter by domain.

1. Read `${CLAUDE_SKILL_DIR}/../shared/task-content-scanner.md` for the scanning algorithm.
2. Glob for `tasks/*/[0-9][0-9][0-9]-*.md` files.
3. For each file, search for lines matching `<!-- STRATEGY CONTENT` that appear on a line by themselves (not inside code blocks).
4. For each tagged block found:
   a. Extract the task ID from the filename (3-digit prefix).
   b. Extract the task title from line 1 (`# NNN — Title`).
   c. Extract the Created date from `**Created**: YYYY-MM-DD`.
   d. Parse the tag values — first value = domain, rest = topics.
   e. Find the `## ` heading immediately above the tag (section heading).
   f. Check for review markers on the line(s) immediately after the tag (see Review Markers section).
   g. Count `### ` subsection headings within the block (tag line → next `## ` or EOF).
   h. Extract the most recent date from the task's `## Changelog` section.
5. If `[domain]` argument provided, filter results to that domain only.
6. **Flag issues:**
   - Tags where the first value is not a recognized domain key → `"⚠ Unrecognized domain 'xyz' in task NNN. Known domains: regulatory, commercial, architecture, development, testing, risk, postmarket, operations"`
   - Tags with no values at all → `"⚠ Empty tag in task NNN. Expected: <!-- STRATEGY CONTENT: domain, topics -->"`
7. Report a summary table:

```
Strategy Content Sources

| Task | Section | Domain | Topics | Subsections | Status | Last Modified |
|------|---------|--------|--------|-------------|--------|---------------|
| 033 — Module Architecture | Regulatory Strategy | regulatory | classification, jurisdiction | 5 | active | 2026-04-07 |
| 032 — Submission Tracker | Regulatory Strategy | regulatory | submission structure, DHF | 6 | pending review (task 040) | 2026-04-08 |

2 tasks, 11 subsections across 1 domain
```

**Status values:**
- `active` — no review marker (default)
- `coexists (task NNN)` — confirmed complementary
- `pending review (task NNN)` — deferred conflict, will re-prompt on next assembly
- `superseded (task NNN)` — excluded from assembly

8. If the assembled document for any found domain already exists, report its assembly date so the user can see if it's stale.

### `assemble [domain]`

Compile tagged content into strategy document(s). If domain specified, assemble one. If omitted, assemble all domains that have content.

1. Run `scan` internally to find all tagged blocks.
   - **Skip** blocks with `<!-- STRATEGY REVIEWED: superseded by task NNN -->` markers.
   - **Include** blocks with `<!-- STRATEGY REVIEWED: coexists with task NNN -->` markers (no conflict prompt for the noted pair).
   - **Include** blocks with `<!-- STRATEGY REVIEW: pending, conflicts with task NNN -->` markers (will re-prompt).
2. Group blocks by domain.
3. For each domain to assemble:
   a. Determine the template: check if `${CLAUDE_SKILL_DIR}/templates/{domain}-strategy.md` exists. If yes, use it. If no, use `default-strategy.md`.
   b. Read the template.
   c. **For custom templates** (e.g., regulatory): Route each source `### ` subsection to the matching output section using the topic-to-section mapping table. Within each output section, arrange subsections **newest-first** (by last-modified date from source task changelog; ties broken by higher task ID first).
   d. **For the default template**: Place all subsections under `## Strategy Decisions`, **newest-first** by last-modified date. Use the source `### ` headings as-is.
   e. For each subsection placed, append a source traceability comment immediately after:
      ```markdown
      <!-- Source: task 033, "Multi-Jurisdiction Classification", last modified 2026-04-07 -->
      ```
   f. **Conflict resolution** — see "Conflict Resolution Flow" below.
   g. Populate the `## Open Items` section with all `[VERIFY]` markers found across the assembled content, with their source task and subsection.
   h. Populate the `## Source Traceability` appendix table.
   i. **Preserve and append to `## Assembly History`** — see "Assembly History" below.
   j. Replace template variables: `{{TIMESTAMP}}` with current date, `{{SOURCE_TASKS}}` with comma-separated task IDs, `{{DOMAIN_KEY}}`, `{{DOMAIN_NAME}}`, `{{PLANS_INFORMED}}` from the domain registry.
   k. Write the assembled document to the output path from the domain registry.
4. Before writing, read the target folder's `README.md` (per project conventions — README Before Write rule).
5. Report:
   - Documents assembled (domain, path, subsection count)
   - Conflicts resolved (and how — superseded, coexists, deferred)
   - Pending reviews re-prompted
   - `[VERIFY]` markers present
   - Subsections that landed in Uncategorized (if any)

#### Conflict Resolution Flow

Conflict detection uses two tiers — heading-based (mechanical) and semantic (reasoned). Both feed into the same resolution prompt.

**Tier 1 — Heading overlap**: Two subsections from different tasks have headings that are identical or substantially similar (>80% word overlap). Example: `### Filing Sequence Strategy` vs `### Filing Sequence Strategy`.

**Tier 2 — Semantic overlap**: Two subsections from different tasks are routed to the **same output section** but have different headings. The assembler reads both contents and assesses whether they address the same strategic decision or genuinely different aspects of the topic.
- **Same decision, different wording** → conflict. Example: `### Filing Sequence Strategy` and `### Submission Order and Timing` both in Section 4, both deciding the order of multi-market filings.
- **Different facets of the same topic** → no conflict. Example: `### Filing Sequence Strategy` (jurisdiction ordering) and `### Pre-Market Evidence Strategy` (test data timing) both in Section 7, addressing different concerns.

Tier 2 only fires for subsections already routed to the same output section (custom templates) or the same `## Strategy Decisions` section (default template). It does not do pairwise comparison across all subsections.

**Resolution flow** (applies to both tiers):

1. **Already resolved**: If the older block has `<!-- STRATEGY REVIEWED: coexists with task NNN -->` matching the newer task, skip — no prompt. Both render normally.
2. **Previously deferred**: If the older block has `<!-- STRATEGY REVIEW: pending, conflicts with task NNN -->` matching the newer task, **re-prompt** (same options as below).
3. **New conflict**: No existing marker. **Prompt the lead**:

```
Overlap detected:
  Newer: task 040 "Filing Sequence v2" (modified 2026-04-08)
  Older: task 033 "Filing Sequence Strategy" (modified 2026-04-01)
  Detection: {heading overlap (100% match) | semantic overlap (same decision in Section N)}

Options:
  (1) Keep newer only — task 033's block excluded from future assemblies
  (2) Keep both — they're complementary, not conflicting
  (3) Defer — mark for review, prompted again next assembly
```

**Resolution actions:**

| Option | Marker written to older task | Assembly effect |
|--------|------------------------------|-----------------|
| (1) Keep newer | `<!-- STRATEGY REVIEWED: superseded by task 040 -->` replaces the `<!-- STRATEGY CONTENT -->` tag line | Older block excluded from this and all future assemblies |
| (2) Keep both | `<!-- STRATEGY REVIEWED: coexists with task 040 -->` added below the tag | Both blocks render, no future prompts for this pair |
| (3) Defer | `<!-- STRATEGY REVIEW: pending, conflicts with task 040 -->` added below the tag | Both blocks render with callout, re-prompted next assembly |

For option (1), the content remains in the source task (preserving history) — only the tag is replaced, stopping the content from flowing into the assembled strategy.

**Multi-subsection warning**: When option (1) is chosen and the older block's tag covers multiple subsections, the assembler warns before applying:
```
⚠ Task 033's tag covers 3 subsections, but only "Filing Sequence Strategy" conflicts.
Superseding will also remove: "Module Classification Overview", "Document Reuse Matrix".
Consider splitting the block first, or choose (2) Keep both / (3) Defer instead.
Proceed with supersession? (y/n)
```
If the lead confirms, the supersession proceeds. If not, the assembler re-prompts with the 3 options.

For deferred conflicts (option 3), the older block renders with a visible callout in the assembled document:
```markdown
> **Pending review**: This section overlaps with task 040 ("Filing Sequence v2", 2026-04-08). Run `/strategy assemble` to resolve.
```

#### Assembly History

Each assembled strategy document includes an `## Assembly History` section. This section is **append-only** — the assembler preserves existing entries and adds a new one for the current assembly.

On each assembly:
1. If the target document already exists, read the existing `## Assembly History` section content.
2. Compare the current assembly's source list to the previous assembly's `<!-- Sources: -->` metadata.
3. Determine the assembler identity: use the git user name (`git config user.name`) to record who ran the assembly.
4. Generate a new entry:

```markdown
### YYYY-MM-DD — assembled by {user name}
- **Added**: Section Name (task NNN), Section Name (task NNN)
- **Modified**: Section Name (task NNN — description of change)
- **Superseded**: Section Name (task NNN) → replaced by task NNN
- **Removed**: Section Name (task NNN) — tag deleted from source
- **Conflicts resolved**: Section Name — kept newer (task NNN supersedes task NNN)
- **Conflicts deferred**: Section Name — pending review (task NNN vs task NNN)
- N subsections, M [VERIFY] markers
```

5. Prepend the new entry (most recent first) to the existing history entries.

For the **first assembly** (no prior document or document contains `<!-- Status: awaiting-content -->`):
```markdown
### YYYY-MM-DD — assembled by {user name}
- **Initial assembly** from tasks NNN, NNN
- N subsections, M [VERIFY] markers
```

Omit categories with no items (e.g., don't include a "Removed" line if nothing was removed).

### `diff [domain]`

Show strategy content captured or changed since the last assembly.

1. For each domain (or the specified domain):
   a. Check if the assembled document exists at the domain's output path. If not: report `"No previous assembly found for {domain}. Run '/strategy assemble {domain}' first."` and skip.
   b. Read the `<!-- Assembled: YYYY-MM-DD -->` date from the assembled document.
   c. Run `scan` for that domain to find all current tagged blocks.
   d. For each tagged block, compare the source task's last changelog date to the assembly date.
2. Report four categories:
   - **New**: Tasks with strategy content for this domain that aren't in the current assembly's `<!-- Sources: -->` list.
   - **Modified**: Tasks in the sources list whose last changelog date is after the assembly date.
   - **Status changed**: Blocks whose review marker changed since last assembly (e.g., newly superseded, newly deferred).
   - **Removed**: Tasks in the sources list whose strategy tag for this domain no longer exists (tag deleted or replaced by superseded marker).
3. If nothing has changed: `"No changes since last assembly (YYYY-MM-DD)."`

### `validate [domain]`

Check assembled strategy documents for completeness and freshness.

1. For each domain with an assembled document (or the specified domain):
   a. Read the assembled document.
   b. Run the following checks:

**Universal checks (all domains):**

| Check | How | Severity |
|-------|-----|----------|
| `[VERIFY]` markers | Count occurrences of `[VERIFY]` in the assembled doc; report each with section and source task | Required |
| Pending reviews | Count `> **Pending review**` callouts in the assembled doc; report each with the conflicting task pair | Required |
| Source freshness | Compare assembly date to each source task's last changelog date; flag if any source was modified after assembly | Recommended |
| Uncategorized content | Check for `## Uncategorized` section with content (means topic mapping needs updating) | Recommended |

**Regulatory domain additional checks:**

| Check | How | Severity |
|-------|-----|----------|
| Filing sequence coverage | Every jurisdiction in the Module Classification table (Section 2) has a corresponding entry in Filing Sequence (Section 4) | Required |
| Document applicability | Every document type in the Document Reuse table (Section 6) has applicability marked for all listed jurisdictions | Required |
| Q-Sub completeness | Section 8 has at least one question | Recommended |

2. Report results per domain:

```
Validation: regulatory-strategy.md (assembled 2026-04-08)

  [PASS] No unresolved conflicts
  [WARN] 3 [VERIFY] markers found:
    - Section 2: Pre-Op EU classification [VERIFY] (source: task 033)
    - Section 2: Canada classification [VERIFY] (source: task 033)
    - Section 2: Device Connectivity Canada [VERIFY] (source: task 033)
  [PASS] Filing sequence covers all jurisdictions (US, EU, Canada)
  [PASS] Document applicability complete
  [PASS] Sources are current

Summary: 4/5 passed | 0 failed | 1 warning
```

### `domains`

List all domains with their current status.

1. Read `project.yml:strategy_domains[]` to get the canonical catalog (fallback: the Domain Registry table above, which is rendered from the same source).
2. Run `scan` to determine which domains have tagged content.
3. Check which domains have assembled documents at their output paths.
4. Report:

```
Strategy Domains

| Domain | Has Content | Has Document | Template | Output Path |
|--------|------------|-------------|----------|-------------|
| regulatory | Yes (2 tasks) | Yes (2026-04-08) | Custom | design-controls/plans/ |
| commercial | No | No | Default | input-analysis/market-research/ |
| architecture | No | No | Default | design-controls/architecture/ |
| development | No | No | Default | design-controls/plans/ |
| testing | No | No | Default | design-controls/vnv/ |
| risk | No | No | Default | design-controls/risk-management/ |
| postmarket | No | No | Default | design-controls/plans/ |

Plans informed by each domain:
  regulatory → 510(k), PCCP, Q-Sub, LMR
  commercial → Go-to-market plan, business case, market expansion
  architecture → SAD, SRS, cybersecurity plan
  development → SDP, Config Mgmt Plan
  testing → V&V Plan, test protocols, usability plan
  risk → Risk Mgmt Plan, FMEA, risk-benefit analysis
  postmarket → Maintenance Plan, PMS Plan, LMR, PCCP tracking
```

### `domains add <key> [flags]`

Append a new strategy domain to `project.yml:strategy_domains[]` and re-render every downstream sentinel so the new domain appears in the Domain Registry, init-briefs, Expected Content, and `readme-strategies.md` template tables.

**Flags:**
- `--name=<display>` — display name (required; e.g. `"Clinical"`)
- `--output=<path>` — absolute output path; default `docs/project/strategies/<key>-strategy.md`
- `--template=<filename>` — template basename in `templates/`; default `default-strategy.md`
- `--scope=<description>` — one-line Expected Content / Purpose description (required)
- `--plans=<csv>` — comma-separated plans informed (e.g. `"Clinical Evaluation Report,PMCF plan"`)

**Steps:**

1. Read `project.yml`. If `strategy_domains[]` is missing, abort with: `"project.yml has no strategy_domains[] block — run /medtech-docs init or seed manually before adding domains"`.
2. Validate: `<key>` must be `[a-z][a-z0-9-]*` and must NOT already exist in `strategy_domains[]`. If duplicate, abort with guidance to use `domains edit` instead.
3. Append a new entry to `strategy_domains[]` using the provided flags. Fill `scope: shared` (all domains are shared in v10+). Include empty `what_belongs_here: []` and `plans_table: []` lists so `/strategy init` can later populate them (the lead is expected to edit those in `project.yml` once the domain stabilizes).
4. Write `project.yml` back.
5. Re-render all 4 downstream sentinel targets:
   ```
   python3 .claude/skills/medtech-docs/scripts/render-sentinels.py \
     project.yml \
     .claude/skills/strategy/SKILL.md \
     docs/project/strategies/README.md \
     .claude/skills/medtech-docs/templates/readme-strategies.md
   ```
   (`project.yml` itself has no sentinels; it's listed for explicitness only. The script no-ops on files without sentinels.)
6. Report: new domain key, output path, which files were updated, and next steps (`/strategy init` to create a placeholder brief at the output path; populate `what_belongs_here[]` + `plans_table[]` in `project.yml` once the domain scope is understood).

### `domains edit <key> [flags]`

Patch fields of an existing domain in `project.yml:strategy_domains[]` and re-render downstream sentinels.

**Flags:** any of `--name`, `--output`, `--template`, `--scope`, `--plans` (semantics same as `domains add`).

**Steps:**

1. Read `project.yml`. Locate the entry where `key == <key>`. Abort if not found.
2. Patch only the fields for which flags were supplied. Leave all other fields (`what_belongs_here`, `plans_table`, `scope`) untouched.
3. **If `--output` is changing**, warn the lead: the old assembled document (if any) at the old path will become orphaned. Prompt to confirm before proceeding; if confirmed, `git mv` the old file to the new path (or leave it and let the lead decide).
4. Write `project.yml` back.
5. Re-render the 4 downstream sentinel targets (same command as `domains add`).
6. Report: which fields changed, old vs new values, which files were updated.

### `domains remove <key>`

Remove a domain from `project.yml:strategy_domains[]` and re-render downstream sentinels. The assembled strategy document at the domain's `output_path` is NOT auto-deleted — removal is a rename from "catalog" to "archive"; the file stays on disk.

**Steps:**

1. Read `project.yml`. Locate the entry where `key == <key>`. Abort if not found.
2. **Guard**: if `<output_path>` file exists, warn: `"An assembled <key>-strategy.md still exists at <path>. Removing this domain from project.yml will orphan it — it won't be regenerated, but existing content will remain on disk. Proceed? (y/n)"`.
3. **Guard**: grep `tasks/*/[0-9][0-9][0-9]-*.md` for `<!-- STRATEGY CONTENT: <key>` tags. If any exist, warn: `"N task(s) still tag content with domain '<key>'. These tags will become 'unrecognized domain' warnings on next /strategy scan. Proceed? (y/n)"`. List the task IDs.
4. On confirmation, remove the entry from `strategy_domains[]`. Write `project.yml` back.
5. Re-render the 4 downstream sentinel targets.
6. Report: which domain was removed, any orphaned files, any orphaned tags in tasks, and the re-rendered files.

### `resolve [domain]`

Address pending review markers without running a full assembly. This lets a lead resolve deferred conflicts on their own schedule. **This action is interactive** — it prompts the lead per conflict and must run in the main session (not delegated to a subagent).

**Phase 1 — Parallel scan** (can be delegated):

1. If `[domain]` specified, scan that domain only. Otherwise, launch scanner agents **in parallel** — one per domain — to find all blocks with `<!-- STRATEGY REVIEW: pending, conflicts with task NNN -->` markers. Each scanner also extracts the **full content** of both the pending block and the conflicting block (needed for the lead to make an informed decision without re-reading source tasks).
2. Merge results from all scanners. Domains with no pending reviews are dropped.
3. If no pending reviews found across any domain: `"No pending reviews. All conflicts are resolved."`

**Phase 2 — Interactive resolution** (main session only):

4. For each pending review, show the conflict context and prompt:

```
Pending review 1 of N:
  Domain: regulatory
  Block: task 033 "Filing Sequence Strategy" (modified 2026-04-01)
  Conflicts with: task 040 "Filing Sequence v2" (modified 2026-04-08)
  Deferred since: [date marker was written, if detectable from task changelog]

Options:
  (1) Keep newer only — task 033's block excluded from future assemblies
  (2) Keep both — they're complementary, not conflicting
  (3) Skip — leave pending, review again later
```

5. For each resolution:
   - **Option 1 (keep newer)**: Replace the `<!-- STRATEGY CONTENT -->` tag in the older task with `<!-- STRATEGY REVIEWED: superseded by task NNN -->`. Apply the multi-subsection warning if the block covers multiple subsections.
   - **Option 2 (keep both)**: Replace the `<!-- STRATEGY REVIEW: pending, conflicts with task NNN -->` marker with `<!-- STRATEGY REVIEWED: coexists with task NNN -->`.
   - **Option 3 (skip)**: Leave the pending marker as-is. It will re-prompt on next `resolve` or `assemble`.

6. After processing all pending reviews, report:

```
Resolved 2 of 3 pending reviews:
  - task 033 "Filing Sequence Strategy" → superseded by task 040
  - task 028 "Initial Classification" → coexists with task 033
  - task 025 "Risk Approach" → skipped (still pending)

Run '/strategy assemble [domain]' to regenerate with resolved conflicts.
```

**Note:** `resolve` only updates review markers in source tasks — it does not regenerate the assembled document. Run `assemble` after resolving to pick up the changes.

## Subagent Delegation

Actions can be delegated to subagents for background execution or parallel processing. Each agent prompt in `agents/` is self-contained — it includes the tag convention, scanning algorithm, domain registry, and template logic so the subagent doesn't need to read SKILL.md.

### When to Delegate

| Scenario | Agent Type | Agent Prompt | Why |
|----------|-----------|-------------|-----|
| Scan while working on something else | Explore | `agents/scanner.md` | Read-only, runs in background |
| Assemble one domain | general-purpose | `agents/assembler.md` | Needs Write; keeps assembly out of main context |
| Assemble multiple domains in parallel | Multiple general-purpose | `agents/assembler.md` (one per domain) | Each domain assembled concurrently |
| Validate (background check) | Explore | Direct — use `scan` agent output + validation logic | Read-only |
| Resolve — scan phase | Multiple Explore | `agents/scanner.md` (one per domain) | Parallel scan across all domains; returns pending reviews with full block content for the interactive phase |

**Actions that must NOT be delegated:**
- `resolve` (Phase 2 — interactive resolution): Requires per-conflict human prompting. The scan phase can run in parallel subagents, but the resolution prompts must run in the main session.
- `assemble` conflict prompts: When the assembler detects a new conflict, it prompts the user inline. If the assembler is running as a subagent, it uses AskUserQuestion to surface the prompt back to the parent session.

### How to Invoke

**Scanner** — launch as an Explore subagent:
```
Read agents/scanner.md, replace {{DOMAIN_FILTER}} with the target domain (or "all"),
then launch via Agent tool with subagent_type=Explore.
```

**Assembler** — launch as a general-purpose subagent:
```
Read agents/assembler.md, replace template variables:
  {{DOMAIN_KEY}}     — e.g., "regulatory"
  {{DOMAIN_NAME}}    — e.g., "Regulatory"
  {{OUTPUT_PATH}}    — from domain registry table
  {{TEMPLATE_TYPE}}  — "custom" if domain has a custom template, "default" otherwise
  {{TASK_ID}}        — current active task ID (for task gate)
  {{SESSION_ID}}     — current session UUID (from printenv CLAUDE_SESSION_ID)
Then launch via Agent tool with subagent_type=general-purpose.
```

**Parallel assembly** — to assemble all domains with content:
1. Run `scan` (or scanner agent) to identify which domains have content
2. For each domain with content, launch an assembler agent in parallel (one Agent tool call per domain, all in the same message)
3. Each agent writes its domain's strategy document independently

### Task Gate Note

Assembler agents write files, which triggers the PreToolUse task gate hook. The agent prompt includes a pre-flight step to check and activate the task gate using the session ID passed via `{{SESSION_ID}}`. Since subagents share the parent session's environment, the same session ID and active task apply.

## Best Practices

<!-- Read by /best-practices skill to audit project setup -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Strategy skill installed | `.claude/skills/strategy/SKILL.md` exists | Required | shared |
| Strategy briefs initialized | Every domain in the registry has a file at its output path (either a brief or assembled document). Run `/strategy init` to create missing briefs. | Required | shared |
| Strategy content exists | At least one task file contains `<!-- STRATEGY CONTENT` on a line by itself | Required | shared |
| All tags have domain key | Every `<!-- STRATEGY CONTENT` tag has a recognized domain key as its first value | Recommended | shared |
| Regulatory strategy assembled | `docs/project/strategies/regulatory-strategy.md` exists and does NOT contain `<!-- Status: awaiting-content -->` (has been assembled from real content) | Required | shared |
| Architecture strategy populated | `docs/project/strategies/architecture-strategy.md` exists and does NOT contain `<!-- Status: awaiting-content -->` | Recommended | shared |
| Development strategy populated | `docs/project/strategies/development-strategy.md` exists and does NOT contain `<!-- Status: awaiting-content -->` | Recommended | shared |
| Testing strategy populated | `docs/project/strategies/testing-strategy.md` exists and does NOT contain `<!-- Status: awaiting-content -->` | Recommended | shared |
| Risk strategy populated | `docs/project/strategies/risk-strategy.md` exists and does NOT contain `<!-- Status: awaiting-content -->` | Recommended | shared |
| Post-market strategy populated | `docs/project/strategies/postmarket-strategy.md` exists and does NOT contain `<!-- Status: awaiting-content -->` | Recommended | shared |
| Commercial strategy populated | `docs/project/strategies/commercial-strategy.md` exists and does NOT contain `<!-- Status: awaiting-content -->` | Recommended | shared |
| Operations strategy populated | `docs/project/strategies/operations-strategy.md` exists and does NOT contain `<!-- Status: awaiting-content -->` | Recommended | shared |
| Strategy docs are current | Assembly date in each assembled strategy document is within 7 days of the most recent source task modification date | Recommended | shared |
| No pending reviews | No assembled strategy documents contain `> **Pending review**` callouts (all conflicts resolved or deferred reviews addressed) | Recommended | shared |
| Domain catalog consistent with `project.yml` | Run `python3 .claude/skills/medtech-docs/scripts/render-sentinels.py --dry-run <file>` on each of these 3 files: `.claude/skills/strategy/SKILL.md`, `docs/project/strategies/README.md`, `.claude/skills/medtech-docs/templates/readme-strategies.md`. The renderer prints the proposed new content to stdout **only when the file would change**; if everything is in sync, stdout is empty. Pass if all 3 dry-runs produce empty stdout. Fail if any produces non-empty output — the fix is to drop `--dry-run` and re-run the renderer on the flagged files. | Required | shared |
| `project.yml` has strategy_domains | `project.yml` contains a top-level `strategy_domains:` block with at least one entry. Required so downstream sentinels have something to render. Fix: run `/strategy domains add <key>` or reseed via `/medtech-docs init`. | Required | shared |

## Notes

- If `$ARGUMENTS` is empty or just "help", show this usage guide
- The assembled documents are **generated artifacts** — do not edit directly. Edits should flow back to the source task documents, then `/strategy assemble` regenerates.
- The scanning algorithm is defined in `${CLAUDE_SKILL_DIR}/../shared/task-content-scanner.md` and shared with the future `/lessons` skill.
- When writing assembled documents, follow the project's README Before Write convention (read the target folder's README.md first).
- Domain templates are in `${CLAUDE_SKILL_DIR}/templates/`. Custom templates override the default for their domain.
- The regulatory domain is the only domain with a custom template in v1. Other domains use the default template. Custom templates can be added as domains mature.

## Changelog

- 11 (2026-04-20): **Domain Registry + init-briefs tables now rendered from `project.yml:strategy_domains[]` via sentinel blocks.** Eliminates the cross-skill domain-catalog drift class surfaced in task 073 (where `operations` was defined four different ways across strategy SKILL.md, strategies/README.md, readme-strategies template, and a stray root placeholder). The canonical source of truth moves to `project.yml`; downstream docs render via `<!-- AUTO:STRUCTURE kind=strategy-domains ... -->` blocks (see `.claude/rules/sentinel-blocks.md`, three variants: `expected-content`, `registry`, `init-briefs`). Renderer extended in `.claude/skills/medtech-docs/scripts/render-sentinels.py`. **Still TODO in task 076 follow-ups**: `/strategy domains add|edit|remove` reshape actions; scanner.md + assembler.md reading domains directly from `project.yml`; `/medtech-docs init` seeding `strategy_domains:`; `/best-practices` check that fails when downstream sentinels drift from `project.yml`. For now, action logic still reads the rendered table in SKILL.md — correctness is maintained as long as the sentinel is re-rendered after `project.yml` edits.
- 10 (2026-04-13): **All strategy domains flipped to `shared` scope + "sub-DHF" → "DHF" terminology rename.** The "sub-DHF" term was a misnomer — top-level entries like `pca-device` are just DHFs, and nested entries like `cloud-suite/dhfs/drug-library-manager` are DHFs too. Renamed throughout the skill + agents + templates + tag grammar. `sub_dhfs` field in project.yml → `dhfs`. The deprecated scope key is now `dhf=<leaf>` (was `sub-dhf=<leaf>`). Description string updated. Best Practices Scope column value `per-dhf` unchanged (still correct; it means "one check per DHF entry"). The six per-dhf domains (`regulatory`, `architecture`, `development`, `testing`, `risk`, `postmarket`) now produce one shared output file under `docs/project/strategies/`, same as `commercial` and `operations`. Per-component nuance is expressed via callout subsections inside each shared doc (topic-first structure with `### PCA Device` / `### Connectivity Adapter` / etc. callouts nested under each topic). `dhf=<leaf>` scope key deprecated — tolerated but ignored. DHF scope resolution section removed from Tag Convention. Best Practices table: all strategy-doc checks now `shared`; the two cross-cutting "Per-dhf tags have dhf scope" and "dhf keys resolve" checks removed. Formal design-control outputs (SDP, SAD, V&V Plan, Risk Mgmt Plan, PMS Plan, cybersecurity plan) still live per-DHF under `dhfs/<dhf>/...` — only the upstream strategy briefs moved up. See `tasks/ben/009-shared-strategy-docs.md`.
- 9 (2026-04-13): **Subagent prompts updated for v8 DHF scope semantics.** Rewrote `agents/scanner.md` and `agents/assembler.md` to implement the DHF scope resolution spec introduced in v8. Scanner now reads `project.yml` `dhfs[]` at start, builds a leaf-name lookup, parses `dhf=<leaf>` scope keys in tags, resolves them against the lookup, and flags per-dhf tags missing required scope keys in multi-DHF projects. Output path table now uses the `<dhf>` placeholder so one scan surfaces assembly status for every (domain, dhf) pair. Assembler accepts new `{{SUB_DHF_SCOPE}}` and `{{SUB_DHF_PATH}}` inputs, filters scanned blocks by matching DHF scope, implicit-scopes single-DHF projects, and reports skipped-by-scope subsections in its output. v8 specified the tag convention and Domain Registry schema; v9 makes the agents actually implement it.
- 8 (2026-04-13): **Unified DHF shape support.** Domain Registry reorganized: each domain has a `Scope` (shared or per-dhf); per-dhf domains use `<dhf>` placeholder in their output path template, resolved at assembly time from the tag's `dhf=<leaf>` scope key. Added DHF scope resolution to the Tag Convention section: tags for per-dhf domains must include `dhf=<leaf-name>` in multi-DHF projects (implicit single-entry resolution in single-DHF projects). Leaf-name uniqueness enforced by `medtech-docs add-dhf` means `dhf=<leaf>` is unambiguous. `commercial` and `operations` moved to shared `docs/project/strategies/`. `risk` and `postmarket` moved to their proper DHF-level homes (`risk-management/`, `postmarket/`) out of `design-controls/`. Scanner and assembler changes are specified but not yet fully implemented — this v8 documents the target behavior; consuming subagents (`agents/scanner.md`, `agents/assembler.md`) still use v7 path semantics and will need follow-up edits. See `tasks/ben/007-sub-dhf-migration.md` P3 for full design.
- 7 (2026-04-08): Added `resolve` action — address pending review markers without full reassembly. Scans for `STRATEGY REVIEW: pending` markers, prompts lead with same 3 options (keep newer/keep both/skip), writes resolution markers to source tasks. Does not regenerate assembled docs — run `assemble` after resolving. See task 035.
- 6 (2026-04-08): Two-tier conflict detection — Tier 1 (heading overlap, mechanical >80% word match) plus Tier 2 (semantic overlap, assembler reads content of subsections in the same output section and assesses whether they address the same decision). Multi-subsection warning when superseding a block whose tag covers multiple subsections but only one conflicts. Assembly history now records assembler identity (`git config user.name`). See task 035.
- 5 (2026-04-08): Strategy evolution support. Temporal ordering (newest-first within sections by last-modified date). Interactive conflict resolution — assembler prompts lead with 3 options (keep newer, keep both, defer) instead of silent `> REVIEW` flags. Review markers in source tasks (`STRATEGY REVIEWED: superseded/coexists`, `STRATEGY REVIEW: pending`) survive across assemblies. Deferred reviews re-prompt on every assembly. Assembly History section (append-only changelog in assembled docs). Scanner reports block status. Validate checks pending reviews. See task 035.
- 4 (2026-04-08): Added `init` action — generates placeholder strategy briefs for all domains. Brief template with "What Belongs Here", "Plans This Informs", and "How to Contribute" sections. `assemble` detects `<!-- Status: awaiting-content -->` and replaces briefs with real content. Added per-domain population checks to Best Practices (regulatory Required, others Recommended). See task 035.
- 3 (2026-04-08): Added `operations` domain (8th domain) for agentic infrastructure, tooling, and ways-of-working strategy. Removed obsolete "Future Skill Concept" from task 033 source and regulatory assembly. See task 035.
- 2 (2026-04-08): Added subagent delegation. Scanner agent (Explore, read-only) and assembler agent (general-purpose, needs Write) in agents/ directory. Self-contained prompts with template variables for domain routing. Supports parallel assembly of multiple domains. See task 035.
- 1 (2026-04-08): Initial version — 7 strategy domains (regulatory, commercial, architecture, development, testing, risk, postmarket) + 2 incubating (clinical, cybersecurity). 5 actions (scan, assemble, diff, validate, domains). Shared scanning infrastructure. Custom regulatory template with 9-section topic mapping. Default template for other domains. Strategy → formal plan traceability chain.
