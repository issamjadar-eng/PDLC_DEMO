# 005 — Customer Insights Domain Agent

**ID**: 005
**Created**: 2026-04-12
**Status**: Abandoned
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## Goals

_Build a domain-specific agent that reads the project's customer-facing corpora (KOLs, market, competitive, predicate, clinical, postmarket) and helps derive and validate user needs, design inputs, and architecture decisions for the PP3500 DHF._

- Define the agent's scope, inputs, outputs, and tool surface
- Produce a concrete agent file under `.claude/agents/customer-insights.md`
- Exercise the agent against real PP3500 questions (e.g., _"What customer signals support UN-007 decimal-point legibility?"_, _"Which user needs lack clinical evidence?"_, _"What design input gaps show up across BRAs?"_)
- Populate the `related_user_needs` / `related_design_inputs` YAML frontmatter fields across the 27 customer-insight source documents, using the agent's trace output
- Author `docs/project/input-analysis/insights-index.md` as the agent's single entry-point TOC (deferred decision from task 001 — pending better understanding of the agent's needs)
- Wire the agent into the `/task` and design-controls workflow so teammates can invoke it when authoring UNs/DIs or reviewing changes

## Context (carry-over from task 001)

Task 001 (Project Init) established the customer-insight corpora this agent will consume. All three branches are in place and formatted:

- **`docs/project/input-analysis/`** — 8 KOL profiles, 4 market/competitive PDFs + summary MDs, 5 portfolio device records, 3 concept evaluations
- **`docs/project/dhfs/pca-device/clinical/`** — 5 Clinical Evaluation Plans (CEP), 5 Benefit-Risk Analyses (BRA), 5 Literature Search Strategies (LSS)
- **`docs/project/dhfs/pca-device/postmarket/`** — 5 PMCF plans, 5 PMCF studies, CAPA-2023-001 (synthesized), complaints ledger (synthesized)

All 25 imported clinical MDs and the 2 synthesized postmarket docs carry a common YAML frontmatter schema: `doc_id`, `doc_type`, `device_ids`, `patient_populations`, `care_settings`, `therapy_context`, `evidence_grade`, `primary_endpoints`, `related_user_needs`, `related_design_inputs`, `status`, `last_updated`. The last two fields are intentionally empty for this task to populate.

The downstream docs the agent must be able to trace **to** are:

- `docs/project/dhfs/pca-device/design-controls/user-needs/user-needs.md` — 22 UNs in 9 functional groups (Rev B)
- `docs/project/dhfs/pca-device/design-controls/requirements/design-inputs.md` — 34 DIs in 9 functional groups (Rev B)
- `docs/project/dhfs/pca-device/design-controls/trace-matrix/un-to-di-trace-matrix.md` — existing UN↔DI matrix

The CAPA-2023-001 feedback loop is already wired end-to-end (UN-007 → DI-013 → CAPA → complaints ledger) and makes a good first integration test for the agent.

## Todos

- [ ] Draft an agent spec: scope, non-goals, tool surface (Read/Grep/Glob only? or more?), input conventions, output format
- [ ] Decide the agent's retrieval model: frontmatter filter + keyword grep vs. semantic over raw text; document the tradeoff
- [ ] Write `.claude/agents/customer-insights.md` (the agent definition file) and register it in `project.yml` `security.approved_agents`
- [ ] Define a standard output schema (what the agent returns: evidence rows, trace claims, confidence, gaps)
- [ ] Exercise the agent on three canonical queries:
  - [ ] _"What customer signals support UN-007 (decimal-point legibility)?"_ — should surface CAPA-2023-001, complaints ledger rows, DI-013 remediation arc
  - [ ] _"Which user needs in user-needs.md have no supporting clinical or post-market evidence?"_
  - [ ] _"Summarize KOL sentiment on alarm fatigue across the 8 profiles and link to DIs in G3 Alarms"_
- [ ] Populate `related_user_needs` / `related_design_inputs` frontmatter across 27 customer-insight source files using the agent's own trace output
- [ ] Author `docs/project/input-analysis/insights-index.md` — single entry-point index the agent always reads first (rollup of frontmatter across all 27 files + one-line summary each)
- [ ] Document how to invoke the agent from a task or from `/task find`
- [ ] Add a short "How to query customer insights" section to `docs/project/input-analysis/README.md`
- [ ] Decide whether to add a `related_kols` frontmatter field (not currently on the schema — may help the agent cross-reference KOL profiles)
- [ ] Lessons learned / retrospective on how well the agent derived vs. validated requirements (tag for `/lessons` harvest)

## Open Questions

- Should the agent be read-only, or should it be allowed to **propose** edits to `user-needs.md` / `design-inputs.md` for human review?
- How does this agent interact with the `simplify` / `best-practices` skills? Is it a Skill, an Agent, or both?
- Does the agent need its own MCP resource, or can it work entirely off local markdown?
- Do we need an equivalent "architecture insights" agent later, or does this one cover architecture too? (Task 001 scope mentioned architecture but the current sample corpus has almost no architecture content — this agent may be able to help surface architecture *gaps* rather than validate existing choices.)

## References

| Ref | Description | Location |
|-----|-------------|----------|
| Task 001 | Project init — established the source corpora | `001-project-init.md` |
| Customer-insight corpora | Input-analysis + clinical + postmarket branches | `docs/project/{input-analysis,clinical,postmarket}/` |
| Frontmatter schema | Established in task 001 clinical/postmarket ingestion | See any CEP/BRA/LSS/PMCF/STUDY file header |
| UN / DI / Trace source of truth | PP3500 design controls | `docs/project/dhfs/pca-device/design-controls/{user-needs,requirements,trace-matrix}/` |
| CAPA feedback loop | End-to-end wiring test case for the agent | `UN-007` → `DI-013` → `CAPA-2023-001.md` → `complaints-ledger.md` |
| Skill-creator skill | Used to author the agent file | `.claude/skills/skill-creator/` |
| Project manifest | Where `approved_agents` is maintained | `project.yml` |

## Changelog

- 2026-04-12: Task created. Split out from task 001 after the clinical + postmarket ingestion phase completed, so that agent design and build can proceed as its own scoped effort with clear review gates.
- 2026-06-08: Marked ABANDONED via task-doc audit — never built; single-purpose-agent premise overtaken by the 14-agent advisors framework. Filed under Abandoned in 000-index.md.

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 1,
    "todos": [
      {
        "todo": "Customer-insights domain agent (stale)",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 1,
          "max": 3
        },
        "confidence": "low",
        "basis": "retrospective; stale \u2014 design only, never built"
      }
    ]
  }
}
```
