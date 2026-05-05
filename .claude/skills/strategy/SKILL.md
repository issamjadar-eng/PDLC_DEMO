---
name: strategy
description: "Scan task docs for strategy content tagged by domain and assemble into unified shared strategy documents — regulatory, commercial, architecture, development, testing, risk, post-market, operations; topic-first with per-component callouts"
version: 19
updated: 2026-05-03
# v19: Added Q-Sub Authoring Guardrails section — HARD RULE that authors must load current regulator Q-Sub guidance into context before drafting Q-Sub strategy content; codifies the agreement-seeking pattern and the patterns-to-avoid list per FDA Q-Submission Program guidance.
# v18: Added Design Philosophy + Agent Contract sections making narrative-first explicit. Schema unchanged from v16 (the v17 metadata-field additions were reverted — see Design Philosophy for why).
---

# Strategy Harvester

Scan task documents for tagged strategy content, route by domain, and assemble into unified strategy documents that inform formal plans. Usage: `/strategy <action> [arguments]`

## Design Philosophy — narrative is the contract

Strategy documents are **narrative artifacts**. The narrative IS the contract. The schema's only job is to give each decision a stable address, a lifecycle state, and source attribution — nothing more.

**Why narrative-first, not metadata-first.** Strategy authors write the way humans actually think about strategy: in plain language with rich, ambiguous, context-laden phrasing. *"We commit to addressing MDDS classification in the Q-Sub response. This will need to be reflected in the system architecture, and FDA will likely ask us to enumerate which Mgmt Services operations are clinical-scope vs. transfer-only."* That sentence carries a Q-Sub commitment, an architecture obligation, and a hint about what FDA acceptance might look like — all in prose. Coercing it into typed fields (`obligation-type=qsub-commitment, dhf-targets=..., canonical-role=architecture, acceptance=...`) over-specifies the decision and burdens the author with classification work that downstream agents should be doing themselves.

**Strategy is upstream of everything.** A strategy decision can be made before `project.yml` `dhfs[]` is populated, before any DHF folder structure exists, before any concrete artifact has been authored, and before any catalog vocabulary has been chosen. Strategy is what *justifies creating those layers in the first place*. Therefore the strategy schema cannot reference any of those layers — that would be a chicken-and-egg violation.

**The decision schema in one sentence.** Every DECISION block carries `id` (stable address), `status` (lifecycle), `source` (provenance), and timestamps. **That is the entire schema.** Everything else lives in the **prose body** of the decision and is inferred by downstream readers.

**What lives in the prose, not in metadata:**

- What kind of commitment this is (Q-Sub commitment, predicate finding, classification choice, PCCP scope, structural decision, …)
- What downstream artifacts it might generate or constrain
- Which DHFs, modules, or jurisdictions it touches
- What acceptance criteria might eventually look like
- What FDA / Notified Body / regulatory body might ask
- What this decision commits us to

**Author convention (suggested, not enforced).** To help downstream agents infer richly, decision bodies often include subsections like:

- **Decision** — one paragraph stating the commitment in plain language
- **Why** — the rationale, including alternatives considered and rejected
- **What this commits us to** — what work this decision generates downstream (in prose, not bullet-point IDs)
- **Downstream implications** — which workstreams, modules, or filings this affects (in prose)
- **Open questions** — what remains unresolved, what FDA / NB feedback we're still waiting on
- **Q-Sub framing** *(when relevant)* — how we'd phrase this as a question to FDA, what response we'd predict

These are author hints to write inference-friendly prose. They are NOT enforced structure and they are NOT metadata. A decision body can be a single well-crafted paragraph; structure as the content demands.

**Rule of thumb for any future schema proposal.** If a proposed field would let a downstream skill answer its question by **looking at metadata instead of reading the prose**, that field is a layering violation. The right answer is to teach the downstream skill to read prose richly (e.g., LLM-driven inference over decision bodies), not to push classification work upstream into the schema.

## Agent Contract — how downstream skills consume strategy

Downstream skills (`/dhf-manifest`, `/medtech-docs`, `/tracker`, `/trace-matrix`, `/jira-pull`, the project-console, R&D agents, clinical agents, post-market agents) consume strategy decisions by **reading the prose body of each `<DECISION:start ... ><DECISION:end>` block and applying their own inference logic in their own vocabulary**.

**The contract:**

- Strategy provides **stable addresses** (`id`) and **stable provenance** (source task, lifecycle state). Downstream skills can cite a decision by ID with confidence that the address is durable.
- Strategy provides **rich narrative** in each decision body. Downstream skills are expected to read it (with LLM-driven inference if they're agentic, or with a human in the loop if they're not).
- Strategy makes **no commitments** about taxonomy, classification, routing, or artifact mapping. Different downstream skills derive different things from the same decision body and that is expected.
- A downstream skill that needs to filter or classify decisions does so against the prose, not against metadata. Example: `/dhf-manifest harvest-decisions` (when implemented) reads each decision body, infers Q-Sub-vs-classification-vs-structural intent from language cues, projects through the project's scope vector, and emits obligations in dhf-manifest's own vocabulary. Strategy itself never touches that vocabulary.
- This is **deliberately inefficient at the metadata layer** — that inefficiency is the price of keeping strategy reusable across projects with different downstream conventions and keeping authors free to write strategy as strategy, not as a typed form.

**Implication for skill builders.** When you build a downstream skill that consumes strategy, the right interface is "give me a decision body as prose, I'll infer what I need" — not "give me a row in a typed table." Resist the urge to add a `obligation-type` field "just to make filtering easier." The filtering belongs in the consumer, against the prose.

## Q-Sub Authoring Guardrails (HARD RULE)

When a strategy decision is being authored as a **Q-Submission (Pre-Submission) question** — a question to a regulator (FDA, Notified Body, Health Canada, MHRA, etc.) about a specific submitter proposal — the author MUST review the relevant regulator's Q-Submission / Pre-Submission guidance **before** drafting the decision body. Q-Sub authoring without grounding in current guidance reliably produces open-ended question framings that regulators decline to answer; this is the highest-leverage authoring failure mode the strategy skill encounters and must be guarded against by skill design, not by author discipline alone.

**Pre-flight requirement.** Before authoring any decision that will become Q-Sub content (any decision whose prose body proposes asking a regulator for feedback — e.g., contains phrasing like "Question to FDA", "Q-Sub question", "Pre-Sub topic", "we will ask the Notified Body"), load the **current** regulator guidance on Q-Sub / Pre-Sub framing into the working context. The guidance is what tells the author whether their proposed framing matches the agreement-seeking pattern the regulator expects.

**Where to load the guidance from (in order of preference):**

1. **Project-local distillation** under `docs/external/<regulator>-guidance/q-submission/` if the project has imported the guidance via `/medtech-docs import-guidance` or equivalent.
2. **Live regulator publication** via WebFetch (e.g., the FDA Q-Submission Program guidance page on fda.gov). Use this when no project-local copy exists.
3. **Skill-registry summary** if a downstream skill wraps the guidance with a current-version pointer.

If no copy is available and live fetch is unavailable, **stop authoring** and surface the gap to the lead before proceeding. Do not proceed by inference from training-data memory of an older guidance version — Q-Sub guidance evolves and the current version may have refined acceptable phrasings.

**Why this rule exists.** Q-Sub questions framed without grounding in current guidance reliably default to open-ended patterns ("What does FDA expect?", "What boundary does FDA draw?", "Does FDA have any concerns?", "At what point would X cross into Y?", "How should we approach X?") that regulator guidance explicitly warns against. These framings are routinely declined or answered with vague non-committal feedback — the regulator will not design the submission for the submitter; they react to specific proposals. The cost of this mistake is significant: Q-Sub air is limited (FDA recommends ≤ 4 primary topics per submission), reviewer credibility is finite, and re-asking a reframed question typically costs another submission cycle.

**The agreement-seeking pattern (canonical for regulator Q-Subs):**

1. **Specific submitter proposal** — what we plan to do, with rationale.
2. **Reference to applicable guidance** — which regulator guidance / standard supports the proposal.
3. **Agreement-seeking question** — *"Does \[regulator\] agree with the proposed \[X\]?"* or *"Is the proposed \[X\] appropriate?"*
4. **Optional refinement-seeking follow-up (conditional)** — *"If \[regulator\] does not agree with \[X\], which specific elements would \[regulator\] modify?"*

This pattern is the canonical effective Q-Sub shape and is recommended explicitly in current FDA Q-Submission Program guidance. Equivalent regulator guidance for Notified Body scientific advice, MHRA Pre-Application meetings, and Health Canada Meeting Requests favours the same agreement-seeking shape.

**Patterns to avoid (per regulator guidance):**

- Open-ended exploratory: *"What does \[regulator\] think about...?"*, *"What does \[regulator\] expect for...?"*
- Boundary-definition delegation: *"What boundary does \[regulator\] draw...?"*, *"At what point would X cross into Y?"*
- Concern-elicitation without proposal: *"Does \[regulator\] have any concerns?"*, *"Are there any issues?"*
- Outcome-prediction: *"Will an IDE / 510(k) / PMA / CE mark be approved if...?"*
- Design delegation: *"How should we approach X?"*, *"What study design should we use?"*
- Data-heavy without targeted proposal: dumping evidence without asking a specific question.

If a draft Q-Sub question matches any of these patterns, the question must be reframed to the agreement-seeking pattern before it lands in the strategy doc.

**How this guardrail applies in practice:**

- The lead (or Claude assisting the lead) identifies that a strategy decision will become a Q-Sub question. **Stop authoring.** Load the relevant regulator's Q-Sub guidance into context.
- After loading, draft the Q-Sub decision using all four canonical components: proposal → guidance reference → agreement-seeking question → optional refinement question.
- Cite the regulator guidance reference inline in the decision body (e.g., "*Per the FDA Q-Submission Program guidance (2025 final), recommended question pattern...*") so a downstream reader can verify framing alignment without re-checking the source.
- After drafting, audit the decision against the patterns-to-avoid list. If any pattern is matched, reframe before persisting.
- If the project has not imported the relevant guidance into `docs/external/`, surface that as a gap to the lead and offer to import via `/medtech-docs import-guidance` (or equivalent) before continuing.

**Why this guardrail lives in the strategy skill (not CLAUDE.md or a separate rule).** Q-Sub authoring is one of the highest-leverage activities the strategy skill supports — Q-Sub questions in regulatory-domain strategy decisions directly drive regulator correspondence and shape pre-market submission scope. Placing the guardrail in the skill keeps it co-located with the activity it governs and makes it project-agnostic (any project using the strategy skill for Q-Sub content benefits, regardless of device, jurisdiction, or QMS). For non-FDA regulators (Notified Bodies, Health Canada, MHRA), the same pattern applies — load the relevant regulator's pre-submission guidance first; the canonical agreement-seeking shape transfers.

**Audit trail.** When a Q-Sub decision is reframed in response to this guardrail (e.g., an open-ended draft is replaced with an agreement-seeking version), the decision's source-attribution comment should note the reframe, e.g., *"Reframed YYYY-MM-DD from open-ended to agreement-seeking per FDA Q-Submission Program guidance recommended question pattern."* This preserves the audit trail of when and why the framing was corrected.

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

## Decision Block Format (v15+)

Every decision in an assembled strategy doc is wrapped in sentinel comments that give it a stable ID, a lifecycle state, and a precise boundary the parser can trust. Decision IDs are stable across renames and never reused — they're the addressable element that downstream tooling (project-console, audit, cross-strategy references) operates on.

### Syntax

```markdown
<!-- DECISION:start id=D-REG-1.1 status=active source=ben/032 created=2026-04-09 last-edited=2026-04-15 supersedes=D-REG-1.0 -->
### One Submission, One Intended Use, Multiple Indications

MedTech Project files as **one 510(k) submission**…

**Why:** Three modules, but one product…
<!-- Source: ben/032, "One Submission, ...", last modified 2026-04-09 -->
<!-- DECISION:end id=D-REG-1.1 -->
```

### Metadata fields

| Field | Required | Values |
|-------|----------|--------|
| `id` | yes | `D-<DOMAIN>-<SECTION>.<INDEX>` — e.g. `D-REG-1.1`, `D-OPS-2.3`. Stable forever once allocated. |
| `status` | yes | `active`, `proposed-change`, `superseded`, `withdrawn` |
| `source` | recommended | `<task_folder>/NNN` of the source task that introduced this decision |
| `created` | recommended | `YYYY-MM-DD` — first authored |
| `last-edited` | optional | `YYYY-MM-DD` |
| `supersedes` | optional | another decision's ID — used by `proposed-change` and `superseded` states |
| `withdrawn-date` | optional | `YYYY-MM-DD` — when status flipped to `withdrawn` |
| `withdrawn-by` | optional | actor name |
**The schema deliberately stops at identity, lifecycle, and provenance — see "Design Philosophy" and "Agent Contract" sections.** Strategy decision blocks never carry taxonomy fields (obligation-type, decision-kind, classification), routing fields (drives-requirements, dhf-targets, scope-vector), artifact fields (evidence-target, paths, globs), or acceptance fields (canonical-role, acceptance criteria, requirement IDs). Every one of those is downstream inference work performed by the consuming skill against the **prose body** of the decision, not a metadata coercion. If a proposed schema addition would let a downstream skill skip reading the decision body, that's the wrong direction — it shifts inference cost to the strategy author and locks strategy into a downstream vocabulary.

### Lifecycle states

- **`active`** — current authoritative content. Default for newly-assembled decisions.
- **`proposed-change`** — incoming proposal alongside an existing `active` decision (carries `supersedes=<id>`). Renders side-by-side in the project-console.
- **`superseded`** — replaced by another decision; kept in doc for audit, rendered struck-through.
- **`withdrawn`** — explicitly retired; kept for audit, rendered struck-through with date/actor.

### ID scheme

Format: `D-<DOMAIN_PREFIX>-<SECTION_INDEX>.<DECISION_INDEX>`

Domain prefixes:

| Domain | Prefix |
|--------|--------|
| regulatory | `REG` |
| commercial | `COMM` |
| architecture | `ARCH` |
| development | `DEV` |
| testing | `TEST` |
| risk | `RISK` |
| postmarket | `POSTM` |
| operations | `OPS` |

Section index is the H2's leading number (`## 1. Device & Submission Overview` → `1`); fallback is sequential 1, 2, 3 by H2 order. Decision index is sequential 1, 2, 3 within each H2 by appearance order. New decisions added later get the next-available index — old IDs never reused.

### Backward compatibility

Strategy docs without `DECISION:start/end` sentinels still parse correctly under the legacy "find by H3 heading" path. Run `/strategy migrate <domain>` (or `--all`) to retrofit existing docs — the migrator preserves content verbatim and inserts sentinels with allocated IDs. Reversible.

### Why the strategy doc became system-of-record

In v14 and earlier, task docs were the source of every decision and the strategy doc was a derivative re-rendered by `/strategy assemble`. From v15+, the strategy doc is the canonical record (decisions can be added/edited/removed in the project-console without going through a task doc), with optional back-port to the source task on save. Task-doc-tagged content remains the primary authoring path for distributed team contributions; the assembler still pulls those in.

## Task-Reference Format (REQUIRED)

Every reference to a task — in prose, tables, headings, HTML comment markers, `<!-- Source: ... -->` lines, `> **Proposed change**` callout headers, Assembly-History entries — must use the **`<task_folder>/NNN`** format (e.g. `ben/056`, `maryna/042`). Bare `task NNN` is ambiguous because task numbers are per-team-member and collide across folders (Ben's 032 and Maryna's 032 are different tasks).

**In strategy docs (user-visible prose/tables/headings):** render as a markdown hyperlink so the reference is navigable:

```
[ben/056](../../../tasks/ben/056-medtech-project-suite-parent-sub-dhf-structure.md)
```

The relative path depth is `../../../tasks/<task_folder>/<full-filename>.md` from a strategy doc (which lives at `docs/project/strategies/`). The assembler resolves the full filename by globbing `tasks/<task_folder>/<NNN>-*.md` at assembly time.

**In HTML comment markers (machine-read):** plain `<task_folder>/NNN`, no hyperlink:

```
<!-- Source: ben/032, "One Submission, One Intended Use, Multiple Indications", last modified 2026-04-09 -->
<!-- STRATEGY PROPOSED: vs ben/032, section "X" -->
<!-- STRATEGY REVIEWED: superseded by ben/056 -->
<!-- STRATEGY WITHDRAWN: vs ben/032 -->
```

**In proposal callout headers:**

```
> **Proposed change** — ben/999 ("Heading", Author, YYYY-MM-DD)
```

**Unknown / placeholder IDs** (e.g. an injected test reference to a non-existent task): use plain `ben/NNN` (no hyperlink), so broken links don't ship.

## Review Markers

When the assembler detects overlapping content between tasks, it prompts the lead to resolve the conflict. The resolution is recorded as a review marker comment in the **source task document**, immediately below the `<!-- STRATEGY CONTENT -->` tag. Review markers survive across assemblies because they live in source tasks, not in the generated output.

### Marker Types

| Marker | Meaning | Effect on Scanner | Effect on Assembler |
|--------|---------|-------------------|---------------------|
| `<!-- STRATEGY REVIEWED: superseded by <task_folder>/NNN -->` | This block has been replaced by newer content in <task_folder>/NNN | Scanner **skips** this block entirely | Block excluded from output |
| `<!-- STRATEGY REVIEWED: coexists with <task_folder>/NNN -->` | Confirmed as complementary to overlapping content in <task_folder>/NNN | Scanner includes, notes the pairing | No conflict prompt for this pair |
| `<!-- STRATEGY PROPOSED: vs <task_folder>/NNN, section "X" -->` | Proposal pending in the strategy doc — content is rendered as a `> **Proposed change**` callout alongside the existing section | Scanner includes, flags as proposal | **Re-prompts** the lead on next assembly with accept / withdraw / leave options |
| `<!-- STRATEGY WITHDRAWN: vs <task_folder>/NNN -->` | Proposal was rejected during a previous assembly — lead chose not to supersede | Scanner **skips** this block (same effect as superseded — content stays in source task but stops flowing) | Block excluded from output |

**Backward compatibility (v12 → v13):** The older `<!-- STRATEGY REVIEW: pending, conflicts with <task_folder>/NNN -->` marker is treated as equivalent to `<!-- STRATEGY PROPOSED: vs <task_folder>/NNN -->` during assembly. The first assembly under v13 rewrites the marker and upgrades the callout to the new proposal format.

### Marker Placement

Markers are placed on the line immediately after the `<!-- STRATEGY CONTENT -->` tag:

```markdown
## Regulatory Strategy

<!-- STRATEGY CONTENT: regulatory, classification, jurisdiction -->
<!-- STRATEGY REVIEWED: coexists with ben/040 -->

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
- The v8 per-dhf output paths (`dhfs/<dhf>/design-controls/plans/regulatory-strategy.md`, etc.) are **not** automatically migrated. For MedTech Project, ben/009 P1 executes the `git mv`. For fresh projects, the v10 shared paths apply from init time.

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
   - Tags where the first value is not a recognized domain key → `"⚠ Unrecognized domain 'xyz' in <task_folder>/NNN. Known domains: regulatory, commercial, architecture, development, testing, risk, postmarket, operations"`
   - Tags with no values at all → `"⚠ Empty tag in <task_folder>/NNN. Expected: <!-- STRATEGY CONTENT: domain, topics -->"`
7. Report a summary table:

```
Strategy Content Sources

| Task | Section | Domain | Topics | Subsections | Status | Last Modified |
|------|---------|--------|--------|-------------|--------|---------------|
| 033 — Module Architecture | Regulatory Strategy | regulatory | classification, jurisdiction | 5 | active | 2026-04-07 |
| 032 — Submission Tracker | Regulatory Strategy | regulatory | submission structure, DHF | 6 | pending review (ben/040) | 2026-04-08 |

2 tasks, 11 subsections across 1 domain
```

**Status values:**
- `active` — no review marker (default)
- `coexists (<task_folder>/NNN)` — confirmed complementary
- `pending review (<task_folder>/NNN)` — deferred conflict, will re-prompt on next assembly
- `superseded (<task_folder>/NNN)` — excluded from assembly

8. If the assembled document for any found domain already exists, report its assembly date so the user can see if it's stale.

### `assemble [domain]`

Compile tagged content into strategy document(s). If domain specified, assemble one. If omitted, assemble all domains that have content.

1. Run `scan` internally to find all tagged blocks.
   - **Skip** blocks with `<!-- STRATEGY REVIEWED: superseded by <task_folder>/NNN -->` or `<!-- STRATEGY WITHDRAWN: vs <task_folder>/NNN -->` markers.
   - **Include** blocks with `<!-- STRATEGY REVIEWED: coexists with <task_folder>/NNN -->` markers (no conflict prompt for the noted pair).
   - **Include** blocks with `<!-- STRATEGY PROPOSED: vs <task_folder>/NNN -->` markers (existing proposal — will re-prompt with accept / withdraw / leave).
   - **Legacy**: `<!-- STRATEGY REVIEW: pending, conflicts with <task_folder>/NNN -->` is treated as equivalent to `<!-- STRATEGY PROPOSED: vs <task_folder>/NNN -->` and upgraded on the first v13 assembly.
2. Group blocks by domain.
3. For each domain to assemble:
   a. Determine the template: check if `${CLAUDE_SKILL_DIR}/templates/{domain}-strategy.md` exists. If yes, use it. If no, use `default-strategy.md`.
   b. Read the template.
   c. **For custom templates** (e.g., regulatory): Route each source `### ` subsection to the matching output section using the topic-to-section mapping table. Within each output section, arrange subsections **newest-first** (by last-modified date from source task changelog; ties broken by higher task ID first).
   d. **For the default template**: Place all subsections under `## Strategy Decisions`, **newest-first** by last-modified date. Use the source `### ` headings as-is.
   e. For each subsection placed, append a source traceability comment immediately after:
      ```markdown
      <!-- Source: ben/033, "Multi-Jurisdiction Classification", last modified 2026-04-07 -->
      ```
   f. **Conflict resolution** — see "Conflict Resolution Flow" below.
   g. Populate the `## Open Items` section with all `[VERIFY]` markers found across the assembled content, with their source task and subsection.
   h. Populate the `## Source Traceability` appendix table.
   i. **Preserve and append to `## History`** — see "History" below.
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

1. **Already resolved**: If the older block has `<!-- STRATEGY REVIEWED: coexists with <task_folder>/NNN -->` matching the newer task, skip — no prompt. Both render normally.
2. **Proposal pending**: If either block has `<!-- STRATEGY PROPOSED: vs <task_folder>/NNN -->` pointing at the other, the conflict is already surfaced in the strategy doc as a `> **Proposed change**` callout. **Re-prompt** with the proposal-resolution options (see "Resolving an existing proposal" below) — not the fresh-conflict options.
3. **New conflict**: No existing marker. **Prompt the lead**:

```
Conflict on Section "Filing Sequence Strategy":
  Existing in strategy doc: ben/033 (modified 2026-04-01)
  New from:                 ben/040 (modified 2026-04-23)
  Detection: {heading overlap (100% match) | semantic overlap (same decision in Section N)}

How would you like to handle it? You can say it in plain English:
  • "supersede"  → ben/033's content is replaced; ben/033 marked superseded by ben/040
  • "propose"    → ben/040's content lands as a > **Proposed change** callout for team review
  • "coexists"   → both kept, marked as complementary (no future prompts for this pair)
  • "skip"       → ben/040's block isn't pushed this round; re-prompted next assembly
```

**Natural-language interpretation**: The lead replies free-form. Map their response to one of the four canonical actions below. If the response is ambiguous ("keep it", "maybe", "hmm"), re-prompt with the four options spelled out. If the response is unambiguous but unconventionally phrased ("just replace the old one", "make it a proposal for now", "they're complementary", "not this round"), proceed without re-prompting.

**Resolution actions:**

| Option | Marker written | Assembly effect |
|--------|---------------|-----------------|
| **supersede** | `<!-- STRATEGY REVIEWED: superseded by ben/040 -->` replaces the `<!-- STRATEGY CONTENT -->` tag in ben/033 | Older block excluded from this and all future assemblies |
| **propose** | `<!-- STRATEGY PROPOSED: vs ben/033, section "Filing Sequence Strategy" -->` added below the tag in ben/040 | Existing section 033 renders unchanged; ben/040's content lands **alongside** as a `> **Proposed change**` callout (see format below) |
| **coexists** | `<!-- STRATEGY REVIEWED: coexists with ben/040 -->` added below the tag in ben/033 | Both blocks render, no future prompts for this pair |
| **skip** | No marker written | Neither block is affected this round; same conflict re-surfaces next assembly |

For **supersede**, the content remains in the source task (preserving history) — only the tag is replaced, stopping the content from flowing into the assembled strategy.

**Multi-subsection warning**: When **supersede** is chosen and the older block's tag covers multiple subsections, the assembler warns before applying:
```
⚠ ben/033's tag covers 3 subsections, but only "Filing Sequence Strategy" conflicts.
Superseding will also remove: "Module Classification Overview", "Document Reuse Matrix".
Consider splitting the block first, or choose propose / coexists / skip instead.
Proceed with supersession? (y/n)
```
If the lead confirms, the supersession proceeds. If not, the assembler re-prompts with the four options.

**Proposal callout format** — when **propose** is chosen, the assembler renders the proposing task's content in the strategy doc as:

```markdown
### Filing Sequence Strategy
<!-- Source: ben/033, "Filing Sequence Strategy", last modified 2026-04-01 -->

[existing accepted content from ben/033 stays here verbatim]

> **Proposed change** — ben/040 ("Filing Sequence v2", Ben Xavier, 2026-04-23)
>
> [the full content of ben/040's block, blockquote-indented]
>
> *Resolution: re-run `/strategy assemble` and pick accept / withdraw / leave.*
```

The callout is the **team review surface** — team members read the strategy doc, see proposals inline, and decide at the next assembly whether to accept, withdraw, or leave them.

#### Resolving an existing proposal

When the assembler detects a task block with `<!-- STRATEGY PROPOSED: vs <task_folder>/NNN -->`, it knows a proposal callout already exists in the strategy doc for this pair. Surfaces the proposal to the lead:

```
Existing proposal in regulatory-strategy.md, Section "Filing Sequence Strategy":
  Original:    ben/033 (2026-04-01)
  Proposed by: ben/040 (2026-04-23) — proposed {proposal-date-from-task-040-changelog}

How would you like to resolve?
  • "accept proposal" → ben/040 becomes the section content; ben/033 marked superseded
  • "withdraw"        → drop the proposal callout; ben/040's tag marked withdrawn
  • "leave"           → proposal callout stays; revisit next assembly
```

Natural-language interpretation applies — "just accept it", "withdraw it", "leave for now" map to the canonical actions.

**Resolution actions for existing proposals:**

| Option | Markers written | Assembly effect |
|--------|----------------|-----------------|
| **accept** | ben/033 gets `<!-- STRATEGY REVIEWED: superseded by ben/040 -->` replacing its tag; ben/040's `<!-- STRATEGY PROPOSED -->` marker removed (proposal satisfied) | Section content becomes ben/040's block; callout removed; ben/033 excluded from future assemblies |
| **withdraw** | ben/040's tag replaced with `<!-- STRATEGY WITHDRAWN: vs ben/033 -->` | Callout removed; ben/033 stays as-is; ben/040's block excluded from future assemblies |
| **leave** | No marker change | Callout re-renders unchanged; same prompt next assembly |

#### History

Each assembled strategy document includes an `## History` section. This section is **append-only** — the assembler preserves existing entries and adds a new one for the current assembly.

On each assembly:
1. If the target document already exists, read the existing `## History` section content.
2. Compare the current assembly's source list to the previous assembly's `<!-- Sources: -->` metadata.
3. Determine the assembler identity: use the git user name (`git config user.name`) to record who ran the assembly.
4. Generate a new entry:

```markdown
### YYYY-MM-DD — assembled by {user name}
- **Added**: Section Name (<task_folder>/NNN), Section Name (<task_folder>/NNN)
- **Modified**: Section Name (<task_folder>/NNN — description of change)
- **Superseded**: Section Name (<task_folder>/NNN) → replaced by <task_folder>/NNN
- **Removed**: Section Name (<task_folder>/NNN) — tag deleted from source
- **Conflicts resolved**: Section Name — kept newer (<task_folder>/NNN supersedes <task_folder>/NNN)
- **Conflicts deferred**: Section Name — pending review (<task_folder>/NNN vs <task_folder>/NNN)
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
    - Section 2: Pre-Op EU classification [VERIFY] (source: ben/033)
    - Section 2: Canada classification [VERIFY] (source: ben/033)
    - Section 2: Device Connectivity Canada [VERIFY] (source: ben/033)
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

Address pending proposals without running a full assembly. This lets a lead resolve proposal callouts on their own schedule. **This action is interactive** — it prompts the lead per proposal and must run in the main session (not delegated to a subagent).

**Phase 1 — Parallel scan** (can be delegated):

1. If `[domain]` specified, scan that domain only. Otherwise, launch scanner agents **in parallel** — one per domain — to find all blocks with `<!-- STRATEGY PROPOSED: vs <task_folder>/NNN -->` markers (or the legacy `<!-- STRATEGY REVIEW: pending, conflicts with <task_folder>/NNN -->`). Each scanner also extracts the **full content** of both the proposing block and the existing strategy-doc section (needed for the lead to make an informed decision without re-reading source tasks).
2. Merge results from all scanners. Domains with no pending proposals are dropped.
3. If no pending proposals found across any domain: `"No pending proposals. All conflicts are resolved."`

**Phase 2 — Interactive resolution** (main session only):

4. For each pending proposal, show the conflict context and prompt (same shape as the `assemble` re-prompt for existing proposals):

```
Pending proposal 1 of N:
  Domain: regulatory
  Section: "Filing Sequence Strategy"
  Existing: ben/033 (modified 2026-04-01)
  Proposed by: ben/040 "Filing Sequence v2" (modified 2026-04-23)
  Proposed since: [date marker was written, if detectable from task changelog]

How would you like to resolve?
  • "accept proposal" → ben/040 becomes the section content; ben/033 marked superseded
  • "withdraw"        → drop the proposal callout; ben/040's tag marked withdrawn
  • "leave"           → proposal callout stays; revisit next assembly
```

5. For each resolution:
   - **accept**: Replace ben/033's `<!-- STRATEGY CONTENT -->` tag with `<!-- STRATEGY REVIEWED: superseded by ben/040 -->`. Remove ben/040's `<!-- STRATEGY PROPOSED -->` marker (proposal satisfied — block becomes authoritative). Apply the multi-subsection warning if ben/033's block covers multiple subsections.
   - **withdraw**: Replace ben/040's `<!-- STRATEGY CONTENT -->` tag with `<!-- STRATEGY WITHDRAWN: vs ben/033 -->`. ben/033's section in the strategy doc stays unchanged.
   - **leave**: No marker changes. The proposal callout re-renders unchanged on the next assembly.

Natural-language responses ("just accept it", "withdraw it", "leave for now") map to the canonical actions.

6. After processing all pending reviews, report:

```
Resolved 2 of 3 pending reviews:
  - ben/033 "Filing Sequence Strategy" → superseded by ben/040
  - ben/028 "Initial Classification" → coexists with ben/033
  - ben/025 "Risk Approach" → skipped (still pending)

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
See [README.md](README.md) — consumed by `/best-practices` audit.

## Notes

- If `$ARGUMENTS` is empty or just "help", show this usage guide
- The assembled documents are **generated artifacts** — do not edit directly. Edits should flow back to the source task documents, then `/strategy assemble` regenerates.
- The scanning algorithm is defined in `${CLAUDE_SKILL_DIR}/../shared/task-content-scanner.md` and shared with the future `/lessons` skill.
- When writing assembled documents, follow the project's README Before Write convention (read the target folder's README.md first).
- Domain templates are in `${CLAUDE_SKILL_DIR}/templates/`. Custom templates override the default for their domain.
- The regulatory domain is the only domain with a custom template in v1. Other domains use the default template. Custom templates can be added as domains mature.

## Changelog
See [README.md](README.md) for version history.

