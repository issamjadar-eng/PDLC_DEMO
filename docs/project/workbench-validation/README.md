# Workbench Validation

_Demo sample data — not for clinical use._

MedTech-style tool validation of the **AI workbench itself** — the `.claude/`
toolchain (skills, agents, hooks, scripts, rules) used to author and manage this
project's design-control artifacts. Owned by the `workbench-validation` skill;
rendered in the project console under **Settings → Workbench Validation**.

This folder validates the **toolchain, not the device** — device V&V lives in
`docs/project/dhfs/<dhf>/`. It sits outside the DHF trees deliberately: it is a
QMS-tooling quality record family, not design-history evidence.

## Structure

This folder holds the **authored** sources only. All **generated** outputs (run
results, per-case evidence logs, the validation report, the console sidecar) live at
`tools/workbench-validation/` — the tool-output convention (same pattern as
`tools/usage-metrics/`): generated data, not authored documentation.

| File | Nature | Purpose |
|---|---|---|
| `validation-plan.md` | Authored | Intended-use classes, risk tiers, role-based WUN (workbench user need) register, assurance model, revalidation triggers, data-layer contract |
| `validation.yml` | Authored | Declarative manifest: machine-readable user needs (role + plain-language need + coverage + `implemented_by` traceability) and the test-case catalog (the runner's input) |
| `protocols/` | Written test protocols (method: protocol / inspection) with challenge sets and acceptance criteria; execution records live under `tools/workbench-validation/protocols/` |

## Expected Content

Only the two authored artifacts above. No device DHF content, no per-task working
notes (those go in the owning task doc), and no generated outputs — those belong in
`tools/workbench-validation/`.

## Conventions

- **Authored vs generated**: `validation-plan.md` and `validation.yml` are the sources
  of truth — edit them, then re-run `/workbench-validation validate`. The report,
  results, evidence logs, and sidecar (under `tools/workbench-validation/`) are
  generated projections — **never hand-edit**.
- **Role-based needs**: every WUN is stated from a role's perspective in the role's
  own language — the outcome required, never the implementation. The mechanism lives
  only in `implemented_by` (traceability info).
- **Data-first / customer transforms**: the manifest + run JSON + evidence logs are
  the canonical machine-readable layer; the markdown report is one projection. A
  customer-QMS-formatted validation document is another transform over the same data.
- **Plan ↔ manifest sync**: the WUN register appears in both (prose in the plan,
  machine-readable in the manifest). A change to one is a change to both.
- **Honesty rule**: needs assured by LLM-driven behavior are `process-control` /
  `exploratory` coverage — never mapped to a scripted PASS. Failed test cases are
  triaged (fix the tool or record a known anomaly with rationale), never silently
  dropped from the manifest.
- **[VERIFY] flags**: standards clauses not distilled in `docs/external/` (ISO 13485
  §4.1.6, FDA CSA, 21 CFR Part 11 text) stay flagged until verified against licensed
  source text.
- **Demo posture**: every generated report carries the demo banner; conclusions read
  "would support a fitness-for-use determination" — illustrative of method, not a
  regulatory claim.

## For Claude

- Invoke the `workbench-validation` skill for any work here — do not run or edit these
  artifacts outside its actions.
- Re-run `/workbench-validation validate` after a registry sync, a skill/hook change,
  or a model change; `/workbench-validation status` checks freshness against HEAD.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-07-27 | BX / AI Assistant | task 110: folder created — initial validation plan, manifest, and generated report/sidecar for the .claude workbench. |
| 2026-07-27 | BX / AI Assistant | task 110: WUN register rewritten role-based (plain-language needs + `implemented_by` traceability); generated outputs (results, evidence logs, report, sidecar) relocated to `tools/workbench-validation/` — this folder now holds authored sources only. |
| 2026-09-08 | BX / AI Assistant | task 119: manifest schema 1.1 — `connections:` block, `endpoint:` tier on every case, five new cases (TC-17..21: live Jira/Jira-mirror/browser cases NOT-APPLICABLE here by declaration; secops scanner regression suite; web-control unit suite), WUN-16 exploratory need for MCP-mediated live paths, anomalies re-dispositioned with owner + clearing run, explicit revalidation triggers; plan §6 rewritten + new §7 evidence tiers. |
| 2026-09-08 | BX / AI Assistant | task 120: manifest schema 1.2 — every need carries `role` / `need` / `so_that`; the report composes the user story; plan §4 regenerated. |
| 2026-09-08 | BX / AI Assistant | task 121: manifest schema 2.0 — verdicts PASS/FAIL/NOT-APPLICABLE only, `deployment:` declaration, per-case `scope`/`method`, `protocols/` folder with three written protocols. |
| 2026-09-09 | BX / AI Assistant | task 124: WUN-31 (downloadable Word/PDF record with all evidence sectioned) and WUN-32 (view any recorded run); TC-45 (every run has a rendered revision + index row), TC-46 (package exports in md/docx/pdf with appendices A–F). |
