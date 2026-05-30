# Action: `fan-out`

Invoke the primary advisor agent(s) referenced by a gap-analysis file to draft / extend its findings.

## Usage

```
/gap-analysis fan-out <id> [--include-consulting]
```

## Arguments

- **`<id>`** (required, positional) — the `id:` field of an existing gap-analysis file. The skill searches `docs/_analysis/<component>/<id>.md` across all component folders. Error if not found, or if the id matches multiple files (rare; would require `--component` to disambiguate).
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

   Your task:
   1. Read every entry in `grounded_against` before responding.
   2. For each assertion in the table, decide: confirmed | refuted | open.
      Provide evidence by citing the source path + a specific quote or Jira
      key + the relevant standard clause where applicable.
   3. APPEND your findings to the file's `## Findings` section using the
      F-N format already in the template (do NOT replace existing findings;
      the file is shared between human authors and multiple agents).
   4. APPEND any new open questions to `## Open Questions`.
   5. Update the `last_updated:` frontmatter to today's date.
   6. APPEND a row to the `## Changelog` table:
      `| {{ today }} | agent:{{ primary_advisor }} | <one-line summary> |`
   7. Do NOT change `status:` — that's the human author's decision after
      reviewing your findings.
   8. Do NOT overwrite the file's `## Goal`, `## Source`, `## Assertions`
      sections. Those are the human author's framing.

   Project-agnostic discipline: cite paths verbatim from `grounded_against`
   — never invent paths or Jira keys. If a source is missing or empty, log
   that as an open question rather than fabricating data.
   ```
5. **Invoke** the primary advisor via the `Agent` tool. Use the appropriate `subagent_type` from the available agents list (e.g., `risk-management`, `regulatory-affairs`). Pass the prompt as `prompt:`.
6. **If `--include-consulting`**, repeat step 5 for each consulting advisor, with the prompt adjusted to: "the primary advisor has provided its findings; review their findings and add your domain-specific perspective without duplicating their analysis."
7. **Report** to the user:
   - Which advisors were invoked
   - The file path the advisors will append to
   - A reminder to review the file after the agents return (the human owns `status:` transitions and the disposition of each finding)

## Notes

- **The skill does not edit the gap-analysis file itself during fan-out.** Advisors edit the file via their own Write/Edit tool calls per the prompt's instructions. The skill is the conductor; the advisors are the players.
- **Append-only contract** — advisors are explicitly told to append findings, never replace existing content. This protects multi-author shared editorship.
- **Read-first discipline** — the prompt requires the advisor to Read every `grounded_against` entry before responding. This anchors the findings in real source material rather than the advisor's training knowledge.
- **Standards citation requirement** — the prompt requires the advisor to cite specific standard clauses (e.g., `ISO 14971:2019 § 5.4`) alongside evidence. This is what distinguishes gap analysis from generic critique.

## Failure modes

- **Advisor not available** — if the named primary advisor isn't in the current agent registry, suggest the user check `/agents` and route to a fallback advisor manually.
- **Assertions section missing or empty** — surface as a warning; the advisor can still respond against the Goal + Sources, but the analysis will be less structured.
- **No `recommended_agents:`** — happens for `--topic-freeform` analyses. Prompt the user to either run `/gap-analysis route <topic>` to populate it, or to manually edit the frontmatter and re-run.
