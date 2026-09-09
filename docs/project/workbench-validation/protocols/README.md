# Workbench Validation — Protocols

_Demo sample data — not for clinical use._

Protocol test cases for the workbench validation: needs whose outcome is the assistant's
judgment or an agent-mediated integration, validated by an operator against explicit
acceptance criteria rather than by a script. Owned by the `workbench-validation` skill;
authored from its `templates/protocol.md`.

## Structure

| File | Purpose |
|---|---|
| `TC-PROTO-CITATIONS.md` | Citation-verification challenge set (WUN-05) |
| `TC-PROTO-GROUNDING.md` | Advisor grounding challenge set (WUN-25, judgment half) |
| `TC-PROTO-LIVE-MCP.md` | Live Confluence/Jira adopt → publish round trip (WUN-16) — NOT-APPLICABLE here |

## Expected Content

One protocol per `method: protocol` (or `inspection`) test case in `../validation.yml`,
named after its case id. Authored documents only — execution records are generated
output and live at `tools/workbench-validation/protocols/<TC-ID>.result.yml`.

## Conventions

- Every protocol follows the skill template sections (Purpose · Needs · Baseline ·
  Challenge set · Procedure · Acceptance criteria · Repeatability · Execution record ·
  Deviations · Sign-off).
- Expected outcomes cite a **source of truth** (a file and line, a distilled standard,
  a declaration) — never a previous run of the tool.
- Acceptance criteria are numeric and operator-independent.
- A protocol without a result file is **UNEXECUTED**; the runner reports NOT-EXECUTED,
  which counts as FAIL for the mapped need. Never record a result you did not execute.
- Protocols over this project's content are `scope: deployment`; a customer deployment
  re-authors the challenge set from its own documents.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-09-08 | BX / AI Assistant | task 121: folder created with three protocols (citations, grounding, live MCP round trip) under the GxP verdict model. |
| 2026-09-08 | BX / AI Assistant | task 123: TC-PROTO-CITATIONS revised to v2 after its first execution (FAIL) — answer key regrouped S/U/B per the reference-audit v6 deterministic band rule, four wrong expectations corrected, band-repeatability criterion added; v1 record kept under `tools/workbench-validation/protocols/`. |
