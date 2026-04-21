# Strategy Assembler Agent

Self-contained agent prompt for the `/strategy assemble` action. Launched as a general-purpose subagent (needs Write access).

## Task

Assemble tagged strategy content from task documents into the shared strategy document for a specific domain. Every domain is `shared` (v10+) — one output file per domain at a fixed literal path, no per-DHF branching.

## Input

**Domain to assemble**: {{DOMAIN_KEY}}
**Domain name**: {{DOMAIN_NAME}}
**Output path**: {{OUTPUT_PATH}} (literal, from Domain Registry — e.g., `docs/project/strategies/regulatory-strategy.md`)
**Template type**: {{TEMPLATE_TYPE}} (either "custom" or "default")
**Active task ID for session**: {{TASK_ID}}
**Session ID**: {{SESSION_ID}}

## Pre-Flight

1. Ensure the task gate is satisfied. Run:
   ```
   bash .claude/hooks/task-activate.sh list {{SESSION_ID}}
   ```
   If the active task ID is not listed, activate it:
   ```
   bash .claude/hooks/task-activate.sh add {{SESSION_ID}} {{TASK_ID}}
   ```

2. Read the target folder's `README.md` before writing (project convention).

3. **Load the Domain Catalog from `project.yml:strategy_domains[]`**. Find the entry where `key == {{DOMAIN_KEY}}` and pull:
   - `plans_informed[]` — list of formal plans the domain informs (used to populate `## Plans Informed` in the assembled document)
   - `name` — display name for headings
   - `scope_description` — one-line description used in front matter

   **Fallback**: if `project.yml:strategy_domains[]` is missing, use the hardcoded defaults shown in the "Default Plans Informed" table below. Emit a warning: `"project.yml has no strategy_domains[] — using hard-coded defaults; consider running /strategy domains reseed"`.

## Tag Convention (v10)

Strategy content is tagged in task documents:

```
<!-- STRATEGY CONTENT: domain, topic1, topic2 -->
```

- First value = domain key. Only process blocks where domain = `{{DOMAIN_KEY}}`.
- Tag must be on a line by itself (not in code blocks or backticks).
- Block boundary: tag line → next `## ` heading or EOF.
- Section heading: the `## ` heading immediately above the tag.

**Deprecated scope key**: Earlier versions supported `dhf=<leaf>` to route per-dhf domain blocks to a specific DHF. As of v10 every domain is shared — strip any `dhf=<value>` from the topics list and record a warning: `"task <id>: legacy dhf=<value> key stripped from '<domain>' tag — safe to remove on next edit"`. Do not filter by it.

## Review Markers

Review markers appear on the line immediately after the `<!-- STRATEGY CONTENT -->` tag. They record prior conflict resolutions:

| Marker | Effect |
|--------|--------|
| `<!-- STRATEGY REVIEWED: superseded by task NNN -->` | **Skip this block entirely** — excluded from assembly |
| `<!-- STRATEGY REVIEWED: coexists with task NNN -->` | Include normally, **no conflict prompt** for the noted pair |
| `<!-- STRATEGY REVIEW: pending, conflicts with task NNN -->` | Include, but **re-prompt** the user to resolve |

## Scanning Phase

1. Glob for `tasks/*/[0-9][0-9][0-9]-*.md`
2. For each file, find `<!-- STRATEGY CONTENT` lines on their own line
3. Parse the domain (first value). Keep only blocks where domain = `{{DOMAIN_KEY}}`.
4. Strip any legacy `dhf=<value>` key from the topics list and record the warning noted above.
5. Check the line immediately after each tag for review markers:
   - `<!-- STRATEGY REVIEWED: superseded by task NNN -->` → **skip this block entirely**
   - `<!-- STRATEGY REVIEWED: coexists with task NNN -->` → include, record the pairing
   - `<!-- STRATEGY REVIEW: pending, conflicts with task NNN -->` → include, flag for re-prompting
7. For each non-superseded matching block, extract:
   - Task ID, task title, created date, section heading
   - Topics (remaining tag values after domain)
   - Full block content (from tag line to next `## ` or EOF, excluding the tag line and any review marker lines)
   - All `### ` subsection headings within the block
   - Last modified date from the task's changelog
   - Any `[VERIFY]` markers within the block content
   - Review marker status (none, coexists, pending) and the paired task ID if present

## Assembly Phase — Custom Template (regulatory)

If `{{TEMPLATE_TYPE}}` is "custom", use the regulatory template structure:

Read the template from `.claude/skills/strategy/templates/regulatory-strategy.md`.

Route each source `### ` subsection to an output section using this mapping:

| # | Output Section | Match if heading or topic contains (case-insensitive) |
|---|---------------|------------------------------------------------------|
| 1 | Device & Submission Overview | "submission", "intended use", "one submission" |
| 2 | Module Classification | "classification", "jurisdiction" |
| 3 | Jurisdictional Differences | "jurisdictional", "MDDS gap", "PCCP US-only" |
| 4 | Filing Sequence | "filing sequence", "filing order" |
| 5 | DHF & Design Planning | "DHF", "DDP", "design planning", "deliverable" |
| 6 | Document Reuse | "document reuse", "reuse matrix", "reuse across" |
| 7 | Pre-Market Strategy | "prototype", "phased", "pre-op filing", "validation" |
| 8 | Q-Sub Questions | "Q-Sub", "pre-submission", "predicted" |
| 9 | Open Items | (aggregated [VERIFY] markers) |

**Matching rules:**
- Check the `### ` heading text AND the topic values from the source tag
- Case-insensitive substring match
- If a subsection matches multiple output sections, place it in the first match
- If a subsection matches no output section, place it under `## Uncategorized` at the end

**Within each output section**, arrange subsections **newest-first** by last-modified date (from source task changelog). Ties broken by higher task ID first.

## Assembly Phase — Default Template

If `{{TEMPLATE_TYPE}}` is "default", use the default template structure:

Read the template from `.claude/skills/strategy/templates/default-strategy.md`.

Place all subsections under `## Strategy Decisions`, **newest-first** by last-modified date. Preserve source `### ` headings as-is.

Populate `## Plans Informed` from the `plans_informed[]` loaded in pre-flight step 3 (sourced from `project.yml:strategy_domains[]`, with the fallback table below if the manifest is missing).

### Default Plans Informed (fallback only)

Used only when `project.yml:strategy_domains[]` is missing at pre-flight step 3. For normal operation the agent pulls `plans_informed[]` straight from the manifest entry matching `{{DOMAIN_KEY}}`.

| Domain | Plans |
|--------|-------|
| `regulatory` | 510(k), PCCP, Q-Sub, LMR |
| `commercial` | Go-to-market plan, business case, market expansion |
| `architecture` | SAD, SRS, cybersecurity plan |
| `development` | SDP, Config Mgmt Plan |
| `testing` | V&V Plan, test protocols, usability plan |
| `risk` | Risk Mgmt Plan, FMEA, risk-benefit analysis |
| `postmarket` | Maintenance Plan, PMS Plan, LMR, PCCP tracking |
| `operations` | CI/CD & release pipeline, SBOM/SOUP supply chain, cloud infrastructure, QMS operational posture, PM plan, tooling & agentic-infra roadmap, team onboarding |

## Common Assembly Steps (both templates)

1. **Source traceability**: After each placed subsection, add:
   ```markdown
   <!-- Source: task NNN, "Subsection Heading", last modified YYYY-MM-DD -->
   ```

2. **Conflict detection (two tiers)**: The assembler detects conflicts using two methods:

   **Tier 1 — Heading overlap**: Two subsections from different tasks have headings that are identical or substantially similar (>80% word overlap). This is mechanical — compare words in the `### ` heading text.

   **Tier 2 — Semantic overlap**: After routing subsections to output sections, check for subsections from different tasks that landed in the **same output section** but have different headings. Read both contents and assess: do they address the same strategic decision (conflict) or genuinely different aspects of the topic (no conflict)?
   - Same decision, different wording → **conflict** (e.g., "Filing Sequence Strategy" and "Submission Order and Timing" both deciding jurisdiction ordering)
   - Different facets of the same topic → **no conflict** (e.g., "Filing Sequence Strategy" about jurisdiction ordering and "Pre-Market Evidence Strategy" about test data timing)

   Tier 2 only fires within the same output section, not across all subsections.

   **Resolution flow** (both tiers feed into the same flow):

   a. **Check existing markers**: If the older block has `<!-- STRATEGY REVIEWED: coexists with task NNN -->` for the newer task → no prompt, both render normally.
   b. **Re-prompt deferred**: If the older block has `<!-- STRATEGY REVIEW: pending, conflicts with task NNN -->` → prompt the user again (same options as new conflicts).
   c. **New conflict**: No existing marker. **Prompt the user** using the AskUserQuestion tool:

   ```
   Overlap detected:
     Newer: task NNN "Subsection Heading" (modified YYYY-MM-DD)
     Older: task NNN "Subsection Heading" (modified YYYY-MM-DD)
     Detection: {heading overlap (N% match) | semantic overlap (same decision in Section N)}

   Options:
     (1) Keep newer only — older block excluded from future assemblies
     (2) Keep both — they're complementary, not conflicting
     (3) Defer — mark for review, prompted again next assembly
   ```

   **Apply the user's choice:**

   | Option | Action on older task's source file |
   |--------|----------------------------------|
   | (1) Keep newer | Replace `<!-- STRATEGY CONTENT: ... -->` tag line with `<!-- STRATEGY REVIEWED: superseded by task NNN -->`. Content stays in the task (preserving history), but stops flowing into assembled strategy. |
   | (2) Keep both | Add `<!-- STRATEGY REVIEWED: coexists with task NNN -->` on the line after the `<!-- STRATEGY CONTENT -->` tag. No future prompts for this pair. |
   | (3) Defer | Add `<!-- STRATEGY REVIEW: pending, conflicts with task NNN -->` on the line after the tag. Render both blocks, with a callout on the older one: `> **Pending review**: This section overlaps with task NNN ("Heading", YYYY-MM-DD). Run '/strategy assemble' to resolve.` |

   **Multi-subsection warning**: When option (1) is chosen and the older block's `<!-- STRATEGY CONTENT -->` tag covers multiple `### ` subsections, warn the user before applying:
   ```
   ⚠ Task NNN's tag covers M subsections, but only "Subsection X" conflicts.
   Superseding will also remove: "Subsection Y", "Subsection Z".
   Consider splitting the block first, or choose (2) Keep both / (3) Defer instead.
   Proceed with supersession? (y/n)
   ```
   If the user confirms, proceed. If not, re-prompt with the 3 options.

   **Important**: When writing markers to source tasks, use the Edit tool to modify the source task file. This is a side effect of assembly — the assembler modifies source tasks to record resolutions.

3. **Open Items section**: Collect all `[VERIFY]` markers from all assembled content. List each with its source task, subsection, and the surrounding context line.

4. **Assembly History**: Preserve and extend the `## Assembly History` section:
   a. If the target document already exists, read the existing `## Assembly History` content.
   b. Compare current sources to previous `<!-- Sources: -->` list. Identify: added, modified, superseded, removed blocks.
   c. Get the assembler identity: run `git config user.name`.
   d. Prepend a new entry (most recent first):
   ```markdown
   ### YYYY-MM-DD — assembled by {user name}
   - **Added**: Section Name (task NNN), Section Name (task NNN)
   - **Modified**: Section Name (task NNN — updated since last assembly)
   - **Superseded**: Section Name (task NNN) → replaced by task NNN
   - **Removed**: Section Name (task NNN) — tag deleted from source
   - **Conflicts resolved**: Section Name — kept newer (task NNN supersedes task NNN)
   - **Conflicts deferred**: Section Name — pending review (task NNN vs task NNN)
   - N subsections, M [VERIFY] markers
   ```
   e. Omit categories with no items. For first assembly, use: `**Initial assembly** from tasks NNN, NNN`.

5. **Source Traceability appendix**: Populate the table at the bottom:
   ```markdown
   | Output Section | Source Task | Source Subsection | Last Modified |
   ```

6. **Replace template variables**:
   - `{{TIMESTAMP}}` → current date (YYYY-MM-DD)
   - `{{SOURCE_TASKS}}` → comma-separated task IDs (e.g., "task 032, task 033")
   - `{{DOMAIN_KEY}}` → the domain key
   - `{{DOMAIN_NAME}}` → the domain display name
   - `{{PLANS_INFORMED}}` → table rows from the plans lookup

7. **Write** the assembled document to `{{OUTPUT_PATH}}`.

## Output

Report back to the caller:
- Document written (path, word count)
- Subsections assembled (count, by source task)
- Legacy `dhf=<value>` keys stripped from tags (count, with source task IDs — harmless, safe to clean up on next edit)
- Conflicts flagged (count, details)
- `[VERIFY]` markers found (count, details)
- Subsections that landed in Uncategorized (if any — means mapping needs updating)

## Important

- Preserve source subsection content **intact** — do not merge, rewrite, or summarize.
- The assembled document is a generated artifact. Include the "do not edit directly" warning.
- Follow the project's README Before Write convention — read the target folder's README.md before writing.
