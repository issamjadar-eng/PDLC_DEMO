---
name: gap-analysis
description: "Substantive content-gap analysis of medtech project artifacts — scaffolds and tracks structured gap-assessment markdown under `docs/_analysis/<component>/` that critiques the project's own work product (hazard-register conformance vs ISO 14971, FMEA scoring consistency, SRA / SAD / SRS adequacy vs IEC 62304, predicate-analysis sufficiency, V&V coverage holes, cybersecurity threat-model rigor, human-factors usability-engineering completeness, post-market surveillance loop integrity, filing-readiness arguments). Distinct from `/best-practices` (structural folder/file checks), `/dhf-manifest` (manifest coverage of regulatory obligations), `/jira-pull audit` (Jira-vs-DTM/HTM drift), and `/trace-matrix` (trace-edge integrity) — this skill answers 'is the CONTENT methodologically correct against standards and internal sources?'. Provides actions: `init` (scaffold a new gap-analysis from the template), `list` (roll-up open analyses by status / topic / component), `route` (which advisor agents to consult for a topic), `fan-out` (spawn advisor agents with grounding paths pre-loaded). Topic→advisor routing is advisory (soft suggestions), not gated. TRIGGER when the user asks for a 'gap analysis of <topic>', 'analyze our <document>', 'critique the hazard register', 'find issues with our <artifact>', 'compare our <X> against <standard>', 'are our <artifacts> per standards', 'audit the content of <doc>', or wants to assert findings about project content."
version: 2
updated: 2026-05-27
---

# Gap Analysis Skill

Codifies the **substantive content-gap analysis** workflow for regulated medtech projects: structured-markdown findings about the project's own work product, anchored against internal mirrors / regulated artifacts and external standards, with advisory routing to the right domain agent(s).

Usage: `/gap-analysis <action> [arguments]`

## Where this skill fits (and where it does NOT)

The project already has several gap-checking surfaces. This skill closes the gap at the **content** dimension:

| Skill | Question it answers | Output |
|---|---|---|
| `/best-practices` | Is the folder/README/file structure correct? | YES/NO checklist |
| `/dhf-manifest` | Are all required regulatory obligations covered by delivered artifacts? | Gap report JSON |
| `/jira-pull audit` | Does Jira's item universe agree with the DTM/HTM edge universe? | Category A/B/C drift |
| `/trace-matrix` | Are the trace edges UN→DI→SW→V&V→Risk internally consistent? | Trace deliverable |
| **`/gap-analysis`** | **Is the CONTENT methodologically correct against standards and internal sources?** | **Structured markdown findings** |

The other audit-y skills answer mechanical questions with rule-based pass/fail logic. This skill answers open-ended substantive questions ("is the FMEA severity score consistent with the described harm?", "does the SRA's Class B argument satisfy IEC 62304 § 4.3.c?") that require expert reasoning and citation against external standards. It hosts the **template + routing convention** for that work.

## What goes here vs. elsewhere — hard distinction

| Work type | Home | Why |
|---|---|---|
| **Gap analysis** (this skill) | `docs/_analysis/<component>/<id>.md` | Assertions against sources + standards; structured-markdown findings |
| Research INPUT analysis (predicate / KOL / market / competitive) | `docs/project/input-analysis/<subtopic>/` | Feeds design inputs; not critique of output |
| Strategy (long-lived decisions + rationale) | `docs/project/strategies/<topic>-strategy.md` | Strategic intent, not gap critique |
| Working investigation (in-progress, transient) | `tasks/<person>/<NNN>-*.md` + `_scratch/` | Not yet stable findings |
| Formal controlled deliverables | `<dhf>/<area>/formal/` | Audit-grade signed documents |
| Structural project audit | `/best-practices` (no file output by default) | Folder/file/README checks |
| Regulatory-obligation coverage | `/dhf-manifest` (`<slug>-gap-report.json`) | Manifest-level coverage gap |
| Jira-vs-trace drift | `/jira-pull audit` (`drift.json`) | Mechanical edge-universe comparison |

When in doubt: **if the work involves citing a standard clause (`ISO 14971 § 5.4`, `IEC 62304 § 4.3.c`, `21 CFR 820.30(g)`) to assert that a project artifact is or isn't methodologically correct**, it belongs here.

## Project structure consumed

The skill reads:
- `project.yml dhfs[].arch_slug` — component slugs for the `<component>` segmentation under `docs/_analysis/<component>/`
- `project.yml dhfs[].leaf` + `architecture_name` + `marketed_name` — for display in init prompts and listings
- The system DHF's leaf (whatever the project declares for `dhfs[].role: system`) is reserved for cross-component / system-level / filing-aware analyses

The skill writes only to `docs/_analysis/` — never to the canonical DHF locations, the mirrors (`_jira/`, `_confluence/`), or the regulated `formal/` folders.

## Supporting Files

| File | Purpose |
|------|---------|
| `templates/gap-analysis.md` | Canonical structured template for every new analysis (goal, source, assertions, findings, recommendations, open questions, references, changelog) |
| `data/topic-advisor-map.yml` | Soft routing: topic → recommended advisor agents (primary + consulting). Project-agnostic medtech topic vocabulary. |
| `actions/init.md` | Action doc — scaffold a new gap-analysis from the template |
| `actions/list.md` | Action doc — roll up open analyses by status / topic / component |
| `actions/route.md` | Action doc — print recommended advisors for a topic |
| `actions/fan-out.md` | Action doc — spawn advisor agents with grounding paths from a gap-analysis file's frontmatter |
| `README.md` | Design doc — not loaded by Claude; for human reference |

## Actions

Parse the user's argument string to determine which action.

### `init <topic> --component <slug> [--id <kebab>] [--title "..."]`

Scaffold a new gap-analysis markdown file from `templates/gap-analysis.md` into `docs/_analysis/<component>/<id>.md`.

1. **Validate inputs.**
   - `<topic>` must match a key in `data/topic-advisor-map.yml` (or the user must explicitly opt out via `--topic-freeform`).
   - `<component>` must match an item-DHF `arch_slug:` in `project.yml dhfs[]` OR the system DHF's `leaf:` value.
   - If `--id` is omitted, generate from `<topic>-<short-title-kebab>`.
   - Reject (with helpful error) if `docs/_analysis/<component>/<id>.md` already exists.
2. **Read advisor routing** from `data/topic-advisor-map.yml`. Pull `primary[]` and `consulting[]` advisor lists for the chosen topic. Merge into `recommended_agents:` frontmatter (primary first).
3. **Read project.yml** for the DHF block matching `<component>` so the template can populate `grounded_against:` with default mirror paths (e.g., `_jira/<component>/<latest-version>/hazards.md`, `_confluence/<arch>/...`). Skip defaults if the user is targeting the system DHF (which has no per-component Jira mirror — system DHFs typically aggregate the item-DHF mirrors).
4. **Render the template**, substituting:
   - `{{ id }}`, `{{ title }}`, `{{ topic }}`, `{{ component }}`
   - `{{ today }}` for `created:` and `last_updated:`
   - `{{ recommended_agents }}` for the frontmatter list
   - `{{ grounded_against_defaults }}` for the default sources block
   - `{{ author }}` — read from `tasks/` active task owner if a `_scratch` sentinel marks one; otherwise prompt or default to `human:<git user.name>`
5. **Write** `docs/_analysis/<component>/<id>.md`.
6. **Report**:
   - The path written
   - The recommended advisors (primary + consulting)
   - A reminder that this file is human/agent-authored — the gap-analysis skill never auto-overwrites it; only the author updates it
   - Suggest `/gap-analysis fan-out <id>` to spawn the primary advisor with the file's context.

### `list [--status <s>] [--component <slug>] [--topic <t>]`

Roll-up table of all gap analyses across components.

1. Walk `docs/_analysis/<component>/*.md` (excluding each component's `README.md`).
2. Read frontmatter from each file. Skip files without an `id:` field (they're not gap analyses per this skill — likely component READMEs or unrelated docs).
3. Filter by `--status` / `--component` / `--topic` if provided.
4. Print a table: `component | id | title | topic | status | last_updated | recommended_agents`.
5. Summary footer: counts by status (draft / review / accepted / superseded).

### `route <topic>`

Print recommended advisor agents for a topic.

1. Read `data/topic-advisor-map.yml`.
2. If `<topic>` is in the map, print `primary[]` and `consulting[]` agents with a one-line description for each (pulled from the advisor's own `name`/`description` if available, otherwise from the map).
3. If not in the map, list all known topics with a "did you mean?" suggestion based on string similarity.

### `fan-out <id>`

Spawn the recommended advisor agent(s) to draft / extend the analysis file.

1. Locate the file by `<id>` across all `_analysis/<component>/` folders. Error if not unique.
2. Read its frontmatter — extract `recommended_agents`, `grounded_against`, `topic`, `component`, and the Goal + Source + Assertions sections.
3. Construct a prompt block for the primary advisor that:
   - States the goal verbatim
   - Lists the grounded-against paths (so the advisor reads them with Read first)
   - Lists the assertions and asks the advisor to confirm / refute / extend each with evidence + standard-clause citations
   - Asks the advisor to **append** findings to the existing file's `## Findings` section (NEVER replace existing content; the file is human/agent shared authorship)
   - Reminds the advisor of the structured F-N finding format
4. Use the `Agent` tool to invoke the primary advisor with this prompt. If `consulting[]` advisors are present, surface them as suggested next-step invocations rather than auto-spawning.

The skill never edits the gap-analysis file directly during fan-out — advisors do that, with the human's review.

## Notes

- If `<arguments>` is empty or `help`, show this usage guide.
- The skill is **read-only against the mirror** — every `init` / `fan-out` / `list` operation reads `docs/project/_jira/`, `docs/project/_confluence/`, `docs/external/standards/`, and `project.yml` but writes only to `docs/_analysis/`.
- Gap-analysis files are **human/agent-authored** — once written, the skill never overwrites them. The skill's lifecycle is creation + listing + agent routing; the file's content evolves via the author(s).
- The topic vocabulary in `data/topic-advisor-map.yml` is medtech-generic (risk / regulatory / vnv / cybersecurity / clinical / human-factors / filing / postmarket / quality / software-architecture / systems-engineering). Projects may add topics by adding rows; project-specific topic names should land in `project.yml` `gap_analysis.topics_extra` (planned, not yet wired) rather than the skill data file — keep the skill project-agnostic.

## Best Practices
See `README.md` — consumed by `/best-practices` audit.

(Changelog lives in `README.md` per project skill conventions — SKILL.md is loaded on every trigger, so version metadata stays in the design doc.)
