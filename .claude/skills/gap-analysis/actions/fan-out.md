# Action: `fan-out`

Invoke the recommended advisor agent(s) to draft per-discipline prescription files inside the analysis folder, then aggregate convergence signals + cross-discipline open questions into the aggregate file.

Per the folder-per-analysis convention in [`../SKILL.md`](../SKILL.md), fan-out produces **two outputs per advisor** (HARD RULE — both are required, not either/or):

1. **A per-advisor `recs-<advisor>.md` file** inside `docs/_analysis/<component>/<id>/` — the advisor's full per-discipline writeup. This is the **required** primary deliverable of fan-out; the project-console advisor tab reads these files directly off disk.
2. **Aggregate contributions** — condensed F-N findings appended to the aggregate's `## Findings` section + a `## Changelog` row. These feed the structured findings cards and the sidecar `agents[]` array.

Research-substantiation agents write `research-<topic>.md` in the same folder. After advisors return, the aggregate file additionally rolls up **convergence findings** (the same root cause surfaced by ≥2 advisors from different anchors — high-confidence calls) and the **cross-discipline open questions** aggregated across siblings.

### Console naming contract (load-bearing — get the filename exactly right)

The console's advisor tab (`project-console` `console/gap_analysis/loader.py:load_narratives`) discovers an advisor's writeup by matching the sidecar `agents[]` array against sibling files on disk: for each agent `name` it looks for a file whose stem is **exactly** `recs-<name>` (or ends with `-<name>`). The `agents[]` `name` comes from the aggregate's `recommended_agents:` frontmatter value (which `/gap-analysis init` populates from `data/topic-advisor-map.yml`) / the F-N `Author: agent:<name>` / the `agent:<name>` changelog row. **Therefore the recs filename MUST equal `recs-<recommended_agents value>.md`** — e.g. `recs-regulatory-affairs.md`, `recs-vnv-lead.md`, `recs-systems-engineering.md`, matching the subagent type verbatim. A mismatched filename (`recs-reg-affairs.md`, `recs-RegulatoryAffairs.md`) leaves the advisor tab empty even though the file exists. `/gap-analysis render --check` flags any recommended/contributing agent that has no matching `recs-<name>.md` sibling.

## Usage

```
/gap-analysis fan-out <id> [--include-consulting]
```

## Arguments

- **`<id>`** (required, positional) — the `id:` field of an existing gap-analysis file. The skill searches for the aggregate `docs/_analysis/<component>/<id>/<id>.md` across all component folders. Error if not found, or if the id matches multiple files (rare; would require `--component` to disambiguate).
- **`--include-consulting`** (optional) — also spawn the `consulting[]` advisors in addition to `primary[]`. Default is primary-only; consulting advisors are surfaced as suggested next steps.

## Steps

1. **Locate the file.** Walk `docs/_analysis/<component>/*.md` looking for the `id:` match in frontmatter. If multiple, error and ask for `--component <slug>` qualifier.
2. **Parse frontmatter.** Extract:
   - `recommended_agents:` — primary + consulting list
   - `grounded_against:` — typed pointers to mirror / standard / Confluence paths
   - `topic:`, `component:`, `title:`, `status:`
3. **Parse body sections.** Read these specific section blocks verbatim:
   - `## Goal of this analysis`
   - `## Source being analyzed`
   - `## Assertions` (the table — each row carries an A-N identifier the advisor will reference)
   - `## Open Questions` (if any)
4. **Build the advisor invocation prompt**. Template:
   ```
   You are the {{ primary_advisor }} agent. The user has authored a gap-analysis
   file at {{ path }} and asked you to extend it.

   Goal (verbatim from the file):
   {{ goal_section }}

   Sources to ground against (read these first via Read tool):
   {{ grounded_against_list }}

   Assertions to evaluate (confirm / refute / extend each with evidence and
   standard-clause citations):
   {{ assertions_table }}

   Your task produces TWO outputs (both required):

   OUTPUT A — your full per-discipline writeup, as a NEW file
   `recs-{{ primary_advisor }}.md` in the same folder as {{ path }}.
   The filename MUST be exactly `recs-{{ primary_advisor }}.md` (matching
   your advisor name verbatim) — the project console matches it against the
   analysis's agent list to render your response in its advisor tab; a
   mismatched name leaves the tab empty. Structure the file as:
     - frontmatter: `parent_analysis: {{ id }}`, `title:`, `specialty:`,
       `advisor: {{ primary_advisor }}`, `last_updated: {{ today }}`
     - what-the-standard-says → what-we-do-instead → walk-through →
       worked example (before/after) → why-this-project-specifically →
       step-by-step prescription with owners + acceptance criteria →
       evidence base → cross-discipline open questions
   Do NOT overwrite an existing `recs-{{ primary_advisor }}.md`; if one
   exists you are revising — read it first and extend in place.

   OUTPUT B — condensed contributions to the aggregate {{ path }}:
   1. Read every entry in `grounded_against` before responding.
   2. For each assertion in the table, decide: confirmed | refuted | open.
      Provide evidence by citing the source path + a specific quote or Jira
      key + the relevant standard clause where applicable.
   3. APPEND a condensed F-N entry per finding to the aggregate's
      `## Findings` section using the F-N format already in the template
      (do NOT replace existing findings; the file is shared between human
      authors and multiple agents). Each F-N is the teaching-summary version
      of a section in your `recs-` file — keep the full prescription in the
      recs file, not duplicated here.
      Each F-N entry must include a **Category** field tagged from the
      template's Category taxonomy (Drift / Manifest / Substantiation /
      Coverage / Methodology / Probe-preempt / Format-Tone) plus
      **Severity**, **Effort**, and **Depends-on** fields — these populate
      the Findings summary table.
   4. APPEND any new open questions to the aggregate's `## Open Questions`.
   5. Update the aggregate's `last_updated:` frontmatter to today's date.
   6. APPEND a row to the aggregate's `## Changelog` table:
      `| {{ today }} | agent:{{ primary_advisor }} | <one-line summary> |`
      (the `agent:{{ primary_advisor }}` cell is what links your `recs-`
      file to the sidecar `agents[]` array — keep the name exact.)
   7. Do NOT change `status:` — that's the human author's decision after
      reviewing your findings.
   8. Do NOT overwrite the aggregate's `## Goal`, `## Source`,
      `## Assertions` sections. Those are the human author's framing.
   9. If `## Findings` already contains a `### Summary table`, append a
      single row to it per F-N you authored. If the table does not exist
      yet, leave a marker comment `<!-- TODO: human/aggregator to render
      summary table from F-N entries -->` so the aggregator (or a follow-up
      pass) can build it after all fan-out advisors return.

   Project-agnostic discipline: cite paths verbatim from `grounded_against`
   — never invent paths or Jira keys. If a source is missing or empty, log
   that as an open question rather than fabricating data.
   ```
5. **Invoke** the primary advisor via the `Agent` tool. Use the appropriate `subagent_type` from the available agents list (e.g., `risk-management`, `regulatory-affairs`). Pass the prompt as `prompt:`.
6. **If `--include-consulting`**, repeat step 5 for each consulting advisor, with the prompt adjusted to: "the primary advisor has provided its findings; review their findings and add your domain-specific perspective without duplicating their analysis."
7. **Report** to the user:
   - Which advisors were invoked
   - The `recs-<advisor>.md` file path each advisor wrote + the aggregate it contributed F-N findings to
   - A reminder to review the files after the agents return (the human owns `status:` transitions and the disposition of each finding)
8. **Refresh sidecars.** Once the `recs-*` files + aggregate findings have landed, run `/gap-analysis render` so the project-console view reflects the new findings + agent contributions. Run `/gap-analysis render --check` to confirm every recommended/contributing agent has its matching `recs-<name>.md` (the console advisor-tab requirement).

> **Read-only advisor note.** Registry advisor agents ship without Edit/Write, and a subagent does not hold the parent session's task-gate, so they cannot write to the folder directly. In practice the conductor (the task-active main session) passes the grounding + assertions to each advisor, collects the advisor's returned writeup + F-N findings, and is responsible for **both** outputs: it writes the advisor's full response to `recs-<advisor>.md` (named exactly per the console naming contract above) and appends the condensed F-N findings + changelog row to the aggregate. The files stay the human-reviewed merge point. Use the advisor-writes-directly flow only where the advisors are write-capable and gate-exempt — and even then the recs filename must match `recs-<recommended_agents value>.md`.

## Notes

- **Two required outputs per advisor (HARD RULE).** Every fan-out advisor yields a `recs-<advisor>.md` writeup **and** condensed F-N contributions to the aggregate — never just one. The recs file feeds the console advisor tab; the aggregate findings feed the structured cards + sidecar `agents[]`. An advisor that produced no `recs-<advisor>.md` is an incomplete fan-out; `/gap-analysis render --check` will flag it.
- **Console naming contract is load-bearing.** `recs-<advisor>.md` must equal `recs-<recommended_agents value>.md` (the subagent type verbatim). See the contract callout at the top of this action — a mismatched filename leaves the advisor tab empty.
- **The skill does not edit the gap-analysis files itself during fan-out** beyond conductor write-back. Advisors author content (or return it for the conductor to land) per the prompt's instructions. The skill is the conductor; the advisors are the players.
- **Append-only contract** — advisor contributions to the aggregate are appended, never replacing existing content. This protects multi-author shared editorship. The exception is an advisor's own `recs-<advisor>.md`, which it may revise in place.
- **Read-first discipline** — the prompt requires the advisor to Read every `grounded_against` entry before responding. This anchors the findings in real source material rather than the advisor's training knowledge.
- **Standards citation requirement** — the prompt requires the advisor to cite specific standard clauses (e.g., `ISO 14971:2019 § 5.4`) alongside evidence. This is what distinguishes gap analysis from generic critique.

## Failure modes

- **Advisor not available** — if the named primary advisor isn't in the current agent registry, suggest the user check `/agents` and route to a fallback advisor manually.
- **Assertions section missing or empty** — surface as a warning; the advisor can still respond against the Goal + Sources, but the analysis will be less structured.
- **No `recommended_agents:`** — happens for `--topic-freeform` analyses. Prompt the user to either run `/gap-analysis route <topic>` to populate it, or to manually edit the frontmatter and re-run.
- **Advisor returned findings but no `recs-<advisor>.md`** — incomplete fan-out. The conductor must write the advisor's full response to `recs-<advisor>.md` before reporting done; `/gap-analysis render --check` flags the gap (an agent in `agents[]` with no matching recs sibling).
- **`recs-` filename ≠ advisor name** — the console advisor tab will be empty even though the file exists. Rename to `recs-<recommended_agents value>.md` and re-run `render`.
