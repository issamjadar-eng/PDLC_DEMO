---
name: phase-mapper
description: "Output contract for the regulatory-affairs subagent when invoked by /tracker assess-phases. The agent reads one role-batch context bundle and returns ONE JSON document containing per-file phase_map (which milestones need this artifact and at what version posture), scope (submission vs other/post-market-only), help text (the (?) panel content for each row), and per-batch gap list (catalog obligations not satisfied by any file in the batch's role)."
version: 1
invokes: regulatory-affairs
---

# Phase Mapper — output contract for the regulatory-affairs subagent

This file is the **output contract**, not a separate agent. The
`/tracker assess-phases` action dispatches the existing `regulatory-affairs`
subagent with one role-batch bundle per dispatch; this file specifies the
exact JSON shape the agent must return so the deterministic merger can
write the phase-map / help / gaps sidecars without a second LLM round.

## Input the agent receives (per dispatch)

A YAML bundle (`<bundle_id>.yaml`) containing:

- `batch_role` — the canonical role for this batch (e.g., `risk-management`)
- `output_path` — where to write the result JSON
- `posture_vocabulary` — the 6 allowed `posture` values + their meanings
- `milestone_catalog` — full milestones[] from regulatory.yml (id, name,
  short_label, description, posture)
- `regulatory_strategy_excerpt` — first 4K of regulatory-strategy.md
- `files_to_assess` — list of (file, title, role, members, frontmatter,
  catalog_obligations) for every taxonomy entry in this batch
- `schema_contract.shape` — the expected JSON output shape

## Output: ONE JSON document, no commentary

```json
{
  "batch_role": "<role>",
  "assessments": [
    {
      "file": "<rel-path-from-input>",
      "title": "<friendly title — pass through the bundle's title field unless the agent has reason to refine>",
      "scope": "submission" | "other",
      "scope_rationale": "<1 sentence — why this artifact IS or IS NOT in any submission package>",
      "phase_map": {
        "<milestone_id>": {
          "posture": "<one of posture_vocabulary ids>",
          "version_label": "<short version tag — e.g., v0.1-draft, v1.0, v1.1>",
          "rationale": "<1 sentence — why THIS posture for THIS file at THIS milestone>"
        }
      },
      "help": {
        "description": "<plain-language explainer: what is this artifact, in 1-2 sentences>",
        "why_important_in_project": "<this PROJECT's specific framing — anchor to the device, the filing strategy, the predicate, the AI/ML or cybersecurity profile when relevant>",
        "main_topics": [
          {"name": "<topic name>", "summary": "<1 sentence>"}
        ],
        "regulatory_anchors": ["<FDA/IEC/ISO/QMS citation>", ...]
      }
    }
  ],
  "batch_gaps": [
    {
      "milestone": "<milestone_id>",
      "obligation_id": "<from catalog_obligations>",
      "title": "<obligation title>",
      "expected_role": "<canonical_role>",
      "rationale": "<1 sentence — why this obligation is unsatisfied (no file in any taxonomy maps to it)>"
    }
  ]
}
```

## How to fill `phase_map` per file

Reason about each milestone in `milestone_catalog`. For each:

- **Does this file belong in the milestone's package?** If no: posture =
  `n/a`. (Example: a Complaint Handling Record belongs in NONE of the
  filing milestones — set scope=`other` AND give every milestone n/a.)
- **Is this milestone the FIRST authoritative version?** posture =
  `full-package`. (Example: System SAD at the 510k+PCCP filing — final
  signed version goes in.)
- **Is this milestone an EARLY/incomplete version anchoring the milestone's
  purpose?** posture = `draft-readiness`. (Example: System SAD at QSub —
  draft used to anchor FDA discussion of architecture; not the final
  filing version.)
- **Is this milestone a REVISION of a prior milestone's authoritative
  version?** posture = `update`. (Example: System SAD at LMR1 — same
  logical artifact, post-clearance design refinements; LMR1/LMR2 are
  iteration releases that DON'T trigger a new filing but DO carry their
  own design history.)
- **Is this milestone carrying the artifact UNCHANGED from a prior
  milestone?** posture = `inherited`. (Example: a stable QMS SOP whose
  content didn't change from 510k+PCCP to LMR1.)
- **Does this artifact ONLY exist for this one milestone?** posture =
  `phase-only` for that milestone, `n/a` for all others. (Example: QSub
  Cover Letter exists for QSub only; 510k Cover Letter exists for
  510k+PCCP only.)

Set `version_label` to a short version tag matching the posture:
`v0.1-draft` for draft-readiness; `v1.0` for the full-package milestone;
`v1.1`, `v1.2` for subsequent updates; `v1.0` again on inherited (same
content as the prior milestone). Adjust to the project's actual versioning
convention if the regulatory_strategy_excerpt indicates differently.

## How to fill `scope`

- `scope: submission` — the artifact appears in at least ONE milestone
  with a non-`n/a` posture (it's part of some submission package).
- `scope: other` — the artifact has `n/a` for every milestone (e.g.,
  Complaint Handling Records, internal CAPA records, post-market
  operational artifacts that never appear in a submission).

`scope_rationale` should explain in one sentence (e.g., "Operational
post-market artifact; complaint records are tracked in the QMS but never
included in 510(k), QSub, or LMR submission packages — they feed into
PSUR and CAPA processes which DO appear in submissions").

## How to fill `help`

This populates the (?) row-expansion panel in the dashboard. Audience: a
regulatory reviewer who has 30 seconds. Tone: clear, project-specific.

- `description`: what IS this artifact (plain language, 1-2 sentences).
  NOT a textbook definition — phrase it for THIS file.
- `why_important_in_project`: anchor to THIS project's specifics. Reference
  the device, the predicate, the AI/ML profile, the filing strategy. NOT
  generic.
- `main_topics`: 3-6 topics the artifact must address. Derive from
  catalog_obligations.extracted_requirements when present; otherwise from
  regulatory anchors. Each topic = 1 line.
- `regulatory_anchors`: 2-5 specific citations (FDA guidance section, IEC
  clause, ISO clause, QMS SOP). Same vocabulary the catalog uses.

## How to fill `batch_gaps`

The bundle's `files_to_assess` lists the files we HAVE; the
`catalog_obligations` per file lists the obligations the catalog REQUIRES
under this role. Some obligations may have no file in this batch (or
elsewhere in the taxonomy) satisfying them.

For EACH milestone (per `milestone_catalog`), walk the union of all
`catalog_obligations` across files in this batch. For each obligation:

- If the obligation has a clear satisfying file in `files_to_assess`
  (matching by title, applies_to, or content): NOT a gap. Skip.
- If no file in `files_to_assess` satisfies it AND the obligation belongs
  in this milestone's package per the milestone's posture and the
  obligation's criticality: emit as a gap.
- For QSub: include formal-package gaps (Cover Letter, Presub Questions,
  Meeting Agenda) even when the catalog doesn't have a specific
  obligation for them — they are formally required for any Q-Sub package
  per FDA Q-Sub Program guidance.

Per-batch gaps from this batch are merged with other batches' gaps in the
deterministic merger to produce one consolidated gaps.json sidecar.

## Anti-patterns

- ❌ Wrapping the JSON in markdown fences (` ```json ... ``` `). The
  merger parses RAW JSON only.
- ❌ Adding any text before/after the JSON document. Strict parser.
- ❌ Setting every milestone to `full-package` because "the file looks
  important". The whole point is per-milestone differentiation; use the
  posture vocabulary precisely.
- ❌ Inventing milestone IDs not in `milestone_catalog`. Use only the IDs
  provided.
- ❌ Generic help text that doesn't reference the project. The agent has
  the regulatory_strategy_excerpt for a reason — use it.
