---
name: gap-analysis
description: "Substantive content-gap analysis of medtech project artifacts — scaffolds and tracks structured gap-assessment markdown under `docs/_analysis/<component>/` that critiques the project's own work product (hazard-register conformance vs ISO 14971, FMEA scoring consistency, SRA / SAD / SRS adequacy vs IEC 62304, predicate-analysis sufficiency, V&V coverage holes, cybersecurity threat-model rigor, human-factors usability-engineering completeness, post-market surveillance loop integrity, filing-readiness arguments). Distinct from `/best-practices` (structural folder/file checks), `/dhf-manifest` (manifest coverage of regulatory obligations), `/jira-pull audit` (Jira-vs-DTM/HTM drift), and `/trace-matrix` (trace-edge integrity) — this skill answers 'is the CONTENT methodologically correct against standards and internal sources?'. Provides actions: `init` (scaffold a new gap-analysis from the template), `list` (roll-up open analyses by status / topic / component), `route` (which advisor agents to consult for a topic), `fan-out` (spawn advisor agents with grounding paths pre-loaded), `render` (derive JSON sidecars for the project-console Gap Analysis view). Topic→advisor routing is advisory (soft suggestions), not gated. TRIGGER when the user asks for a 'gap analysis of <topic>', 'analyze our <document>', 'critique the hazard register', 'find issues with our <artifact>', 'compare our <X> against <standard>', 'are our <artifacts> per standards', 'audit the content of <doc>', or wants to assert findings about project content."
version: 7
updated: 2026-06-05
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
| **Gap analysis** (this skill) | `docs/_analysis/<component>/<id>/<id>.md` | Assertions against sources + standards; structured-markdown findings |
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

## Folder-per-analysis convention (HARD RULE)

**Each gap analysis is one folder, not one file.** The aggregate file inside has the same name as the folder and is the "if you read one file, read this" entry point.

```
docs/_analysis/<component>/<id>/
├── README.md                       ← folder meta + reading order + file inventory
├── <id>.md                         ← aggregate / final-report (start here)
├── <id>.yml                        ← optional structured-data sidecar (dashboard-consumable)
├── recs-<advisor>.md               ← per-advisor prescription detail (REQUIRED, one per fan-out advisor; filename = advisor/subagent name verbatim — console advisor-tab contract)
├── research-<topic>.md             ← public-precedent + published-methodology research substantiation
└── <named-sidecar>.md              ← analysis-specific extras (e.g., qsub-questions.md)
```

Rationale:

- The aggregate file's `id:` frontmatter matches the folder name. Internal cross-references inside the folder use short relative paths (e.g., `[recs-risk-management.md](recs-risk-management.md)`), not legacy long-prefix forms.
- Each detail file's frontmatter carries `parent_analysis: <id>` so a `list` walk can roll up the cluster as a unit.
- The aggregate is **comprehensive enough to make decisions from**, but defers full step-by-step prescriptions, complete evidence base, and verbatim worked examples to the linked detail files. It is not an executive summary; it is a final report with deep references.
- **Worked examples (before / after) live in the aggregate's per-finding sections** — they are the most teachable content the analysis produces and must not be pushed out into appendix files. Per-finding detail prescriptions (owner roles, artifacts-touched, acceptance criteria, full evidence base, references) live in the `recs-<advisor>.md` files.
- **`recs-<advisor>.md` is a REQUIRED fan-out output, and its filename is a load-bearing contract.** It must equal `recs-<recommended_agents value>.md` (the advisor / subagent name verbatim, e.g. `recs-regulatory-affairs.md`). The project console matches the sidecar `agents[]` `name` against a sibling whose stem is `recs-<name>` to populate its advisor tab; a mismatched name leaves the tab empty. `/gap-analysis render --check` flags any recommended/contributing agent missing its `recs-<name>.md`.

The `init` action scaffolds the folder + README + aggregate file. The `fan-out` action writes **two outputs per advisor** to the same folder: the required `recs-<advisor>.md` writeup plus condensed F-N findings appended to the aggregate. The `list` action walks subdirectories rather than individual files.

## Supporting Files

| File | Purpose |
|------|---------|
| `templates/gap-analysis.md` | Canonical structured template for every new analysis (goal, source, assertions, findings, recommendations, open questions, references, changelog) |
| `data/topic-advisor-map.yml` | Soft routing: topic → recommended advisor agents (primary + consulting). Project-agnostic medtech topic vocabulary. |
| `actions/init.md` | Action doc — scaffold a new gap-analysis from the template |
| `actions/list.md` | Action doc — roll up open analyses by status / topic / component |
| `actions/route.md` | Action doc — print recommended advisors for a topic |
| `actions/fan-out.md` | Action doc — spawn advisor agents with grounding paths from a gap-analysis file's frontmatter |
| `actions/render.md` | Action doc — derive JSON sidecars (`<id>.gap.json` + `index.json`) for the project-console Gap Analysis view |
| `scripts/render_sidecars.py` | Pure-stdlib renderer behind `render` — parses analysis markdown → structured JSON contract (`schema_version: 1.0`) |
| `README.md` | Design doc — not loaded by Claude; for human reference |

## Actions

Parse the user's argument string to determine which action.

### `init <topic> --component <slug> [--id <kebab>] [--title "..."]`

Scaffold a new gap-analysis folder + aggregate file + folder README from `templates/gap-analysis.md` into `docs/_analysis/<component>/<id>/`. Per the folder-per-analysis convention above.

1. **Validate inputs.**
   - `<topic>` must match a key in `data/topic-advisor-map.yml` (or the user must explicitly opt out via `--topic-freeform`).
   - `<component>` must match an item-DHF `arch_slug:` in `project.yml dhfs[]` OR the system DHF's `leaf:` value.
   - If `--id` is omitted, generate from `<topic>-<short-title-kebab>`.
   - Reject (with helpful error) if `docs/_analysis/<component>/<id>/` already exists.
2. **Read advisor routing** from `data/topic-advisor-map.yml`. Pull `primary[]` and `consulting[]` advisor lists for the chosen topic. Merge into `recommended_agents:` frontmatter (primary first).
3. **Read project.yml** for the DHF block matching `<component>` so the template can populate `grounded_against:` with default mirror paths (e.g., `_jira/<component>/<latest-version>/hazards.md`, `_confluence/<arch>/...`). Skip defaults if the user is targeting the system DHF (which has no per-component Jira mirror — system DHFs typically aggregate the item-DHF mirrors).
4. **Create folder** `docs/_analysis/<component>/<id>/` and write two files into it:
   - **`<id>.md`** — the aggregate / final-report, rendered from `templates/gap-analysis.md`. Substitutions: `{{ id }}`, `{{ title }}`, `{{ topic }}`, `{{ component }}`, `{{ today }}` (for `created:` and `last_updated:`), `{{ recommended_agents }}`, `{{ grounded_against_defaults }}`, `{{ author }}` (read from `tasks/` active task owner if a `_scratch` sentinel marks one; otherwise prompt or default to `human:<git user.name>`).
   - **`README.md`** — folder meta. Reading order, file inventory table, cross-file conventions (frontmatter `id:` matches folder name; detail files carry `parent_analysis: <id>`; internal refs use short relative paths), and a how-this-folder-was-produced section that the author maintains.
5. **Report**:
   - The folder path created + the two files inside it
   - The recommended advisors (primary + consulting)
   - A reminder that the aggregate is human/agent-authored — the gap-analysis skill never auto-overwrites it; only the author updates it
   - Suggest `/gap-analysis fan-out <id>` to spawn the primary advisor (writes to `recs-<advisor>.md` inside the same folder).

### `list [--status <s>] [--component <slug>] [--topic <t>]`

Roll-up table of all gap analyses across components.

1. Walk `docs/_analysis/<component>/*/` (subdirectories) and read each subdirectory's aggregate file `<id>/<id>.md`. Skip subdirectories without a matching-named aggregate file (they aren't gap analyses per this skill).
2. Read frontmatter from each aggregate file. Skip files without an `id:` field.
3. Filter by `--status` / `--component` / `--topic` if provided.
4. Print a table: `component | id | title | topic | status | last_updated | recommended_agents | detail_files_count`. The detail-files count is the number of `recs-*.md` + `research-*.md` siblings in the folder.
5. Summary footer: counts by status (draft / review / accepted / superseded).

### `route <topic>`

Print recommended advisor agents for a topic.

1. Read `data/topic-advisor-map.yml`.
2. If `<topic>` is in the map, print `primary[]` and `consulting[]` agents with a one-line description for each (pulled from the advisor's own `name`/`description` if available, otherwise from the map).
3. If not in the map, list all known topics with a "did you mean?" suggestion based on string similarity.

### `fan-out <id>`

Spawn the recommended advisor agent(s) to produce **two required outputs per advisor** (HARD RULE), then (when multiple advisors return) aggregate convergence signals into the aggregate file.

**Two required outputs per advisor:**

1. **`recs-<advisor>.md`** — the advisor's full per-discipline writeup, written into the analysis folder. This is the **required** primary deliverable. The project-console advisor tab (`console/gap_analysis/loader.py:load_narratives`) reads these files directly off disk and renders each in its own advisor tab.
2. **Aggregate contributions** — condensed F-N findings appended to the aggregate's `## Findings` + a `## Changelog` `agent:<name>` row. These feed the structured findings cards and the sidecar `agents[]` array.

A fan-out that produced findings but no `recs-<advisor>.md` is **incomplete** — `/gap-analysis render --check` flags it.

> **Console naming contract (HARD RULE).** The `recs-` filename must be exactly `recs-<recommended_agents value>.md` — the advisor / subagent name verbatim (e.g. `recs-regulatory-affairs.md`, `recs-vnv-lead.md`). The console matches the sidecar `agents[]` `name` (derived from `recommended_agents` / F-N `Author: agent:<name>` / the `agent:<name>` changelog row) against a sibling whose stem is `recs-<name>`. A mismatched filename leaves the advisor tab empty even though the file exists.

1. Locate the folder by `<id>` across all `_analysis/<component>/` subdirectories. Error if not unique. The aggregate file is at `<folder>/<id>.md`.
2. Read the aggregate file's frontmatter — extract `recommended_agents`, `grounded_against`, `topic`, `component`, and the Goal + Source + Findings + Methodology sections.
3. For each advisor in `recommended_agents` (primary first), construct a prompt block that:
   - States the goal verbatim
   - Lists the grounded-against paths plus sibling `recs-*.md` and `research-*.md` files already in the folder (so the advisor reads them with Read first and references rather than duplicates)
   - Lists the F-N findings the advisor owns (per the topic-to-advisor mapping in `data/topic-advisor-map.yml`)
   - Asks the advisor to write its full writeup to `recs-<advisor>.md` (named exactly per the console naming contract above), structured as: what-the-standard-says → what-we-do-instead → walk-through → worked example (before/after) → why-this-project-specifically → step-by-step prescription with owners + acceptance criteria → evidence base → cross-discipline open questions — AND to contribute condensed F-N findings + a changelog row to the aggregate
   - Reminds the advisor that worked examples in their detail file are extended versions of the aggregate's per-finding worked example, not duplicates — the aggregate's example is the teaching summary; the detail file goes deeper with multiple cases
4. Use the `Agent` tool to invoke each advisor. Research-substantiation agents (general-purpose) write `research-<topic>.md` files in the same folder, providing the citation base the advisors reference.
5. **Convergence detection (when ≥2 advisor files return).** After siblings return, scan their `## Findings` / `## Recommendations` sections for findings that appear in ≥2 advisor files with different framings (e.g., Clinical, HF, and Cyber independently identifying "surgeon-in-the-loop ceiling" from different anchors). Surface these as `convergence:` items in the aggregate's "Top actions + execution roadmap" section — these are high-confidence calls because three disciplines reached the same root cause from different evidence bases.
6. **Open-questions aggregation.** Roll up `Cross-discipline open questions` sections across all returned advisor files into the aggregate's section, with the owning-discipline column preserved. Deduplicate where multiple advisors raised the same cross-discipline question.

The skill never edits an advisor's detail file directly during fan-out — advisors author their own. The skill DOES update the aggregate file to incorporate convergence findings + the open-questions roll-up (which is the synthesis layer the aggregate exists to carry).

> **Advisor write-back note.** The registry advisor agents are read-only (`Read/Glob/Grep/WebFetch/file-locator`), and a subagent does not hold the parent session's task-gate. In practice the fan-out **conductor** (the task-active main session) is responsible for **both** outputs: it collects each advisor's returned writeup and writes it to `recs-<advisor>.md` (named exactly per the console naming contract), and it appends the condensed F-N findings + changelog row to the aggregate. The advisors return content; the conductor lands it. Either way the files are the human-reviewed merge point.

After fan-out lands the `recs-*` files + aggregate findings, run **`/gap-analysis render`** to refresh the JSON sidecars the console consumes, then **`/gap-analysis render --check`** to confirm every recommended/contributing agent has its matching `recs-<name>.md`.

### `render [--check] [--strict-recs]`

Derive JSON sidecars from the analysis markdown for the project-console Gap Analysis view (and any other machine consumer). See `actions/render.md` for the full schema.

1. Run the deterministic renderer:
   ```bash
   python3 .claude/skills/gap-analysis/scripts/render_sidecars.py
   ```
2. It writes `docs/_analysis/<component>/<id>/<id>.gap.json` (per-analysis detail) + `docs/_analysis/index.json` (roll-up). The markdown stays the single source of truth; the JSON is a regenerated projection (idempotent; never hand-edited).
3. `--check` writes nothing and exits non-zero (2) on missing/stale sidecars — for CI / `/best-practices` drift checks (sidecar staleness only).
4. **Recs-completeness audit (always runs).** Every contributing agent should have a matching `recs-<name>.md` writeup the console advisor tab can discover; any gap prints a `WARN <id>: missing recs-<name>.md` line. This is advisory by default; pass `--strict-recs` to make a gap a non-zero exit (3) — warn-by-default avoids turning `/best-practices` red on pre-dual-output analyses.

Run after `init` (register the new analysis in the index) and after `fan-out` (project the appended findings), or whenever an analysis markdown is hand-edited. The console degrades gracefully when sidecars are absent (empty-state hint), mirroring the trace-matrix view.

## Notes

- If `<arguments>` is empty or `help`, show this usage guide.
- The skill is **read-only against the mirror** — every `init` / `fan-out` / `list` operation reads `docs/project/_jira/`, `docs/project/_confluence/`, `docs/external/standards/`, and `project.yml` but writes only to `docs/_analysis/`.
- Gap-analysis files are **human/agent-authored** — once written, the skill never overwrites them. The skill's lifecycle is creation + listing + agent routing; the file's content evolves via the author(s).
- The topic vocabulary in `data/topic-advisor-map.yml` is medtech-generic (risk / regulatory / vnv / cybersecurity / clinical / human-factors / filing / postmarket / quality / software-architecture / systems-engineering). Projects may add topics by adding rows; project-specific topic names should land in `project.yml` `gap_analysis.topics_extra` (planned, not yet wired) rather than the skill data file — keep the skill project-agnostic.

## Best Practices
See `README.md` — consumed by `/best-practices` audit.

(Changelog lives in `README.md` per project skill conventions — SKILL.md is loaded on every trigger, so version metadata stays in the design doc.)
