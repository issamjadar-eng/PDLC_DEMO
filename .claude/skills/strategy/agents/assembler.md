# Strategy Assembler Agent

Self-contained agent prompt for the `/strategy assemble` action. Launched as a general-purpose subagent (needs Write access).

## Task

Assemble tagged strategy content from task documents into the shared strategy document for a specific domain. Every domain is `shared` (v10+) — one output file per domain at a fixed literal path, no per-DHF branching.

## Decision Block Format (v15+ — REQUIRED)

Every subsection you emit into the strategy doc MUST be wrapped in `<!-- DECISION:start ... -->` / `<!-- DECISION:end id=... -->` sentinels with metadata. This is what makes each decision a stable, addressable, lifecycle-managed element. See `SKILL.md` → `## Decision Block Format (v15+)` for the full spec.

**On every assembly run:**

1. **Preserve existing decision IDs.** Read the target strategy doc first. For every decision block already present, KEEP its `id=` value. Never reassign. Never reuse a retired ID.

2. **Allocate fresh IDs for new decisions.** ID format: `D-<DOMAIN>-<SECTION>.<INDEX>` where `<DOMAIN>` is the prefix from the table in SKILL.md (REG / COMM / ARCH / DEV / TEST / RISK / POSTM / OPS), `<SECTION>` is the H2 leading number (`## 1. Device & Submission Overview` → `1`), and `<INDEX>` is the next-available integer within that section (start at 1; increment past the highest existing index — never reuse).

3. **Set `status=` correctly:**
   - Fresh content with no incoming conflict → `status=active`
   - Newer task content that conflicts with an existing decision (the propose case) → `status=proposed-change` AND `supersedes=D-<existing-id>`
   - Older content that the user has explicitly accepted as superseded → `status=superseded`
   - Withdrawn content → `status=withdrawn` (kept in doc for audit; rendered struck-through downstream)

4. **Always populate `source=<task_folder>/NNN`** (e.g. `source=ben/032`). Use the `<task_folder>/NNN` canonical form per the v14 task-reference convention. If the source task can't be resolved, omit the field rather than guess.

5. **`created=YYYY-MM-DD`** on the first emit of a decision. Preserve this date on every subsequent re-assembly — it's the canonical "when this decision first entered the strategy". Bump `last-edited=YYYY-MM-DD` whenever the body changes.

**Output shape per decision:**

The H3 heading MUST start with the numeric prefix `<sec>.<idx>` matching the decision ID's tail (e.g. `D-REG-1.1` → `### 1.1 One Submission…`). The prefix gives readers a clear visual boundary between decisions and matches the addressable ID.

```markdown
<!-- DECISION:start id=D-REG-1.1 status=active source=ben/032 created=2026-04-09 last-edited=2026-04-15 -->
### 1.1 One Submission, One Intended Use, Multiple Indications

[body content here — paragraphs, tables, lists]

**Why:** ...
**How to apply:** ...
<!-- Source: ben/032, "One Submission, One Intended Use, Multiple Indications", last modified 2026-04-09 -->
<!-- DECISION:end id=D-REG-1.1 -->
```

The legacy `<!-- Source: ... -->` comment is kept inside the block for backward compatibility with un-migrated tooling.

**Conflicts in non-interactive mode (project-console SDK launches):** when a newer task contributes content that overlaps an existing `active` decision, emit a NEW decision block with `status=proposed-change` AND `supersedes=D-<id-of-existing>`, alongside the existing decision. The console renders the side-by-side comparison and lets the user Accept / Reject / Modify / Re-categorize — which the console's mutators turn into the appropriate state transitions on both blocks.

## Interactivity Modes

The agent runs in one of two modes, controlled by the launching context:

- **Interactive** (default, when launched from Claude Code by a human): on every conflict, prompt the user with `supersede / propose / coexists / skip`.
- **Non-interactive** (v14+, when launched by the project-console `/workflows/strategy-reassembly` page via the Agent SDK): do NOT prompt. Every conflict is written as a `> **Proposed change**` blockquote callout in the strategy doc, paired with a `<!-- STRATEGY PROPOSED: vs <older>, section "X" -->` marker. The console surfaces these callouts for per-proposal Accept / Reject / Modify review by the user after the run completes. Equivalent to taking the `propose` branch on every conflict.

Detect non-interactive mode from the system prompt (the console sends "Run in NON-INTERACTIVE mode" in its system prompt) or from the absence of an interactive stdin. When in doubt, prefer non-interactive — a silent `propose` always results in a reviewable callout, never in data loss.

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
| `<!-- STRATEGY REVIEWED: superseded by <task_folder>/NNN -->` | **Skip this block entirely** — excluded from assembly |
| `<!-- STRATEGY REVIEWED: coexists with <task_folder>/NNN -->` | Include normally, **no conflict prompt** for the noted pair |
| `<!-- STRATEGY PROPOSED: vs <task_folder>/NNN, section "X" -->` | Include, **re-prompt with accept / withdraw / leave** (existing proposal in strategy doc) |
| `<!-- STRATEGY WITHDRAWN: vs <task_folder>/NNN -->` | **Skip this block entirely** — proposal was rejected previously |
| `<!-- STRATEGY REVIEW: pending, conflicts with <task_folder>/NNN -->` (v12 legacy) | Treat as equivalent to `STRATEGY PROPOSED`; upgrade the marker on first v13 assembly |

## Scanning Phase

1. Glob for `tasks/*/[0-9][0-9][0-9]-*.md`
2. For each file, find `<!-- STRATEGY CONTENT` lines on their own line
3. Parse the domain (first value). Keep only blocks where domain = `{{DOMAIN_KEY}}`.
4. Strip any legacy `dhf=<value>` key from the topics list and record the warning noted above.
5. Check the line immediately after each tag for review markers:
   - `<!-- STRATEGY REVIEWED: superseded by <task_folder>/NNN -->` → **skip this block entirely**
   - `<!-- STRATEGY WITHDRAWN: vs <task_folder>/NNN -->` → **skip this block entirely**
   - `<!-- STRATEGY REVIEWED: coexists with <task_folder>/NNN -->` → include, record the pairing
   - `<!-- STRATEGY PROPOSED: vs <task_folder>/NNN, section "X" -->` → include, flag as existing proposal (re-prompt with accept / withdraw / leave)
   - `<!-- STRATEGY REVIEW: pending, conflicts with <task_folder>/NNN -->` (v12 legacy) → treat as `STRATEGY PROPOSED`; queue a marker upgrade in the final write-back step
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
   <!-- Source: <task_folder>/NNN, "Subsection Heading", last modified YYYY-MM-DD -->
   ```

2. **Conflict detection (two tiers)**: The assembler detects conflicts using two methods:

   **Tier 1 — Heading overlap**: Two subsections from different tasks have headings that are identical or substantially similar (>80% word overlap). This is mechanical — compare words in the `### ` heading text.

   **Tier 2 — Semantic overlap**: After routing subsections to output sections, check for subsections from different tasks that landed in the **same output section** but have different headings. Read both contents and assess: do they address the same strategic decision (conflict) or genuinely different aspects of the topic (no conflict)?
   - Same decision, different wording → **conflict** (e.g., "Filing Sequence Strategy" and "Submission Order and Timing" both deciding jurisdiction ordering)
   - Different facets of the same topic → **no conflict** (e.g., "Filing Sequence Strategy" about jurisdiction ordering and "Pre-Market Evidence Strategy" about test data timing)

   Tier 2 only fires within the same output section, not across all subsections.

   **Resolution flow** (both tiers feed into the same flow):

   a. **Check existing markers**: If the older block has `<!-- STRATEGY REVIEWED: coexists with <task_folder>/NNN -->` for the newer task → no prompt, both render normally.
   b. **Re-prompt existing proposal**: If the newer block carries `<!-- STRATEGY PROPOSED: vs <task_folder>/NNN -->` (or the legacy v12 `<!-- STRATEGY REVIEW: pending, conflicts with <task_folder>/NNN -->`), the conflict is already surfaced in the strategy doc as a `> **Proposed change**` callout. Prompt with the **proposal-resolution** options (see "Resolving an existing proposal" below) — not the fresh-conflict options.
   c. **New conflict**: No existing marker. **Prompt the user** using the AskUserQuestion tool:

   ```
   Conflict on Section "Subsection Heading":
     Existing in strategy doc: <task_folder>/NNN (modified YYYY-MM-DD)
     New from:                 <task_folder>/NNN (modified YYYY-MM-DD)
     Detection: {heading overlap (N% match) | semantic overlap (same decision in Section N)}

   How would you like to handle it? You can say it in plain English:
     • "supersede"  → older content replaced; older task marked superseded
     • "propose"    → new content lands as > **Proposed change** callout for team review
     • "coexists"   → both kept, marked complementary (no future prompts for this pair)
     • "skip"       → new block not pushed this round; re-prompted next assembly
   ```

   **Natural-language interpretation**: Map the user's free-form response to one of the four canonical actions ("just replace the old one" → supersede; "make it a proposal" → propose; "they're complementary" → coexists; "not this round" → skip). If ambiguous, re-prompt with the four options spelled out.

   **Apply the user's choice:**

   | Option | Action |
   |--------|--------|
   | **supersede** | Replace older task's `<!-- STRATEGY CONTENT: ... -->` tag line with `<!-- STRATEGY REVIEWED: superseded by <task_folder>/NNN -->`. Content stays in the task (preserving history), stops flowing into assembled strategy. |
   | **propose** | Add `<!-- STRATEGY PROPOSED: vs <task_folder>/NNN, section "X" -->` on the line after the newer task's `<!-- STRATEGY CONTENT -->` tag. In the strategy doc, keep the existing (older) section content verbatim; render the newer task's content immediately below as a `> **Proposed change** — <task_folder>/NNN ("Heading", Author, YYYY-MM-DD)` blockquote-indented callout, ending with `> *Resolution: re-run /strategy assemble and pick accept / withdraw / leave.*` |
   | **coexists** | Add `<!-- STRATEGY REVIEWED: coexists with <task_folder>/NNN -->` on the line after the older task's `<!-- STRATEGY CONTENT -->` tag. No future prompts for this pair. |
   | **skip** | No marker change. Neither block is modified. Same conflict re-surfaces next assembly. |

   **Multi-subsection warning**: When **supersede** is chosen and the older block's `<!-- STRATEGY CONTENT -->` tag covers multiple `### ` subsections, warn the user before applying:
   ```
   ⚠ Task NNN's tag covers M subsections, but only "Subsection X" conflicts.
   Superseding will also remove: "Subsection Y", "Subsection Z".
   Consider splitting the block first, or choose propose / coexists / skip instead.
   Proceed with supersession? (y/n)
   ```

   **Resolving an existing proposal**: When step (b) fires — newer block carries `<!-- STRATEGY PROPOSED: -->` — prompt with:
   ```
   Existing proposal in {{DOMAIN_KEY}}-strategy.md, Section "Subsection Heading":
     Original:    <task_folder>/NNN (YYYY-MM-DD)
     Proposed by: <task_folder>/NNN (YYYY-MM-DD)

   How would you like to resolve?
     • "accept proposal" → new task's content becomes the section; older task marked superseded
     • "withdraw"        → drop the proposal callout; newer task's tag marked STRATEGY WITHDRAWN
     • "leave"           → proposal callout stays; revisit next assembly
   ```
   Natural-language accepted. Actions:

   | Option | Action |
   |--------|--------|
   | **accept** | Replace older task's tag with `<!-- STRATEGY REVIEWED: superseded by <task_folder>/NNN -->`; remove the `<!-- STRATEGY PROPOSED -->` marker from the newer task (proposal satisfied — its block becomes authoritative section content). Apply multi-subsection warning as above if older task's tag covers multiple subsections. |
   | **withdraw** | Replace newer task's `<!-- STRATEGY CONTENT -->` tag with `<!-- STRATEGY WITHDRAWN: vs <task_folder>/NNN -->`. Older task's section in the strategy doc is unchanged. |
   | **leave** | No marker changes. Proposal callout re-renders unchanged on next assembly. |
   If the user confirms, proceed. If not, re-prompt with the 3 options.

   **Important**: When writing markers to source tasks, use the Edit tool to modify the source task file. This is a side effect of assembly — the assembler modifies source tasks to record resolutions.

3. **Open Items section**: Collect all `[VERIFY]` markers from all assembled content. List each with its source task, subsection, and the surrounding context line.

4. **History**: Preserve and extend the `## History` section (v14 rename — previously `## Assembly History`; now covers per-proposal accept/reject/modify actions in addition to assembly runs):
   a. If the target document already exists, read the existing `## History` content.
   b. Compare current sources to previous `<!-- Sources: -->` list. Identify: added, modified, superseded, removed blocks.
   c. Get the assembler identity: run `git config user.name`.
   d. Prepend a new entry (most recent first):
   ```markdown
   ### YYYY-MM-DD — assembled by {user name}
   - **Added**: Section Name (<task_folder>/NNN), Section Name (<task_folder>/NNN)
   - **Modified**: Section Name (<task_folder>/NNN — updated since last assembly)
   - **Superseded**: Section Name (<task_folder>/NNN) → replaced by <task_folder>/NNN
   - **Removed**: Section Name (<task_folder>/NNN) — tag deleted from source
   - **Conflicts resolved**: Section Name — kept newer (<task_folder>/NNN supersedes <task_folder>/NNN)
   - **Conflicts deferred**: Section Name — pending review (<task_folder>/NNN vs <task_folder>/NNN)
   - N subsections, M [VERIFY] markers
   ```
   e. Omit categories with no items. For first assembly, use: `**Initial assembly** from tasks NNN, NNN`.

5. **Source Traceability appendix**: Populate the table at the bottom:
   ```markdown
   | Output Section | Source Task | Source Subsection | Last Modified |
   ```

6. **Replace template variables**:
   - `{{TIMESTAMP}}` → current date (YYYY-MM-DD)
   - `{{SOURCE_TASKS}}` → comma-separated task IDs (e.g., "ben/032, ben/033")
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
