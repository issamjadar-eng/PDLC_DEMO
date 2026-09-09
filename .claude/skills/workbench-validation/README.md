# workbench-validation — Design Doc

## What this is

MedTech-style, risk-based validation of the **AI workbench itself** — the `.claude/`
toolchain (skills, agents, hooks, scripts, rules) a regulated project uses to author
and manage design-control artifacts. In a QMS, software used to produce or gate
controlled records must be validated for intended use (ISO 13485 QMS-software
validation posture; FDA CSA-style risk-based assurance). This skill turns the
validation-shaped assets that accumulate naturally per-skill (test suites, lints,
audit scripts, gate hooks) into a **single periodic validation report** with three
visible components: user needs → tests → report.

## Design decisions

- **One producer skill, console as pure consumer.** The skill owns the runner and
  renderer; the project console renders the sidecar in its Settings section. Same
  loose-coupling contract as the other console-feeding skills (submissions,
  commercial, gap-analysis).
- **All project data lives in the project tree, split authored-vs-generated**:
  authored sources (the plan with the role-based WUN register, the validation.yml
  manifest) in `docs/project/workbench-validation/`; generated outputs (results,
  evidence logs, report, sidecar) in `tools/workbench-validation/` — the tool-output
  convention. The skill ships only generic scripts + templates — registry-shareable,
  per the project-agnostic hard rule.
- **Data-first for portability.** The manifest + run JSON + evidence logs are the
  canonical machine-readable layer; the markdown report is one generated projection.
  A customer QMS needing its own report format gets another transform over the same
  data — the validation never has to be redone for formatting.
- **The manifest is declarative; the mapping edge lives on the test case** (`wun:`),
  so a need's evidence list is derived, never duplicated.
- **Honesty about LLM non-determinism.** Deterministic components get scripted
  evidence; LLM-driven behavior is assured by process controls and labeled
  PROCESS-CONTROL / EXPLORATORY — never a scripted PASS. The report says so
  explicitly, and phrases conclusions as "would support a fitness-for-use
  determination" (demo posture: illustrative of method, not a regulatory claim).
- **Config baseline per run**: git SHA + dirty flag + per-skill versions + installed
  hooks + (when available) model identifier. Model change = revalidation trigger with
  zero repo diff — recorded so the trigger is actionable.
- **Suites that always exit 0 are real** (observed in the wild): the runner supports
  `pass_pattern` / `fail_pattern` so pass/fail is derived from output when exit codes
  lie. `env_unset` exists because gate tests behave differently inside a live agent
  session (e.g. an inherited session ID makes a fake-session DENY test resolve ALLOW).

## Lineage

Grounded in the four-element tool-validation pattern common to MedTech V&V work
instructions (documented intended use → risk question → risk-scaled evidence →
configuration baseline + revalidation triggers), generalized from device-V&V tools to
the whole authoring workbench.

## Dependencies

- `python3` + PyYAML (or `uv run --with pyyaml`); `uv` recommended for pytest-based
  cases (`uv run --no-project --with pytest`).
- `git` for the configuration baseline.
- Optional: `project-console` ≥ 1.58.0 renders the sidecar in Settings → Validation;
  add `tools/workbench-validation` to the console's `grounding.extra_roots` so the
  report and evidence logs resolve in the Documents viewer.

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill has SKILL.md | File exists at skill root | Required | shared |
| Frontmatter complete | name, description, version, updated all present | Required | shared |
| README.md exists | Design doc at skill root | Required | shared |
| Changelog current | Latest entry matches version number | Required | shared |
| Report/sidecar not hand-edited | `validation-report.md` + sidecar carry the generated stamp and match `results/latest.json` run_id | Required | local |
| Validation freshness | Sidecar `baseline.git_sha_short` matches repo HEAD, else re-run recommended | Recommended | local |
| No fake PASS for LLM behavior | Every `coverage: tests` need maps to ≥1 deterministic test case; LLM-assured needs are process-control/exploratory | Required | local |
| Every case declares its evidence tier | `test_cases[].endpoint` is `none`, `mocked`, or `live` on every case; `live` cases carry `connection:` and the manifest has a `connections:` block | Required | local |
| Run of record is clean | Latest run JSON has no `warnings[]` (clean tree, model id captured, no skill version-pin mismatch, no tier-less case) | Recommended | local |
| Verdicts are binary | Sidecar `needs[].verdict` ∈ {PASS, FAIL, NOT-APPLICABLE}; no need carries `coverage:`; every `method: protocol` case has a protocol document and, once executed, a result record | Required | local |
| Every case declares scope and method | `test_cases[].scope` ∈ {capability, deployment}, `method` ∈ {scripted, protocol, inspection}; deployment cases name `requires_deployment` keys that exist in `deployment:` | Required | local |
| Every need is a complete user story | Each `user_needs[]` entry has non-empty `role`, `need` (outcome, no "As a…" prefix) and `so_that` (purpose); the runner refuses otherwise on schema ≥ 1.2 | Required | local |
| Anomalies are dispositioned | Every `known_anomalies[]` entry names an owner and an expected clearing run (or "accepted residual") | Required | local |

## Changelog

- 8 (2026-09-09): **Report revisions + export package.** Every run is rendered as its
  own revision — `results/<run-id>/validation-report.md` + `sidecar.json` (with a
  `revision` block) from that run's **pinned** manifest — and `results/index.json`
  lists every run newest-first for the console's revision drop-down; `render
  --all-runs` backfills historical runs, whose header states they were re-rendered by
  the current renderer from pinned data (or the live manifest where no pin exists).
  New `export_package.py`: one sectioned validation package per run (cover + sign-off
  table, the report, appendices A pinned manifest · B environment and deployment
  declaration · C protocols with execution records and run evidence · D every case's
  full evidence log · E pinned test sources with sha256 · F QMS coverage inventory) as
  Markdown, or DOCX/PDF through docflow's `export_formal.py`. WUN-31/32, TC-45/46.
  Rationale: a validation record leaving the workbench must carry its evidence, not
  links to it, and a reviewer must be able to see what the validation said at any
  recorded point in time.

- 7 (2026-09-08): **QMS template coverage inventory.** Manifest key `qms_coverage:` names a
  JSON inventory a deployment case writes (contract: `templates[]` with
  instances/tested/pass/fail/status, `procedures[]`, `documents_without_template[]`,
  `summary{}`); the report gains §3 "QMS template coverage" (per imported template/form:
  project documents, conformance evidence, pass/fail, covered / covered-failing /
  imported-unused; plus doctypes with no template imported), the sidecar a
  `qms_coverage` block, and the console a collapsed panel. Absent inventory renders as
  an explicit note, never silently. Rationale: validation of a deployed workbench is only
  as complete as the QMS content it ran against — a template imported later must show
  up as untested by itself.

- 6 (2026-09-08): **GxP verdict model + capability/deployment scope (manifest + run/sidecar
  schema 2.0).** Verdicts are **PASS / FAIL / NOT-APPLICABLE** only; PROCESS-CONTROL,
  EXPLORATORY, PARTIAL and NO-EVIDENCE are gone — they were evidence methods standing in
  for verdicts. A need with no applicable executed case FAILS ("no evidence"); an
  unexecuted protocol or a skipped case FAILS its need; each need carries a `reason`.
  `coverage:` on needs is retired (the runner warns). Every test case declares
  `scope: capability` (skill-shipped fixtures, portable) or `scope: deployment` (this
  instance's content) and `method: scripted | protocol | inspection`; a `deployment:`
  declaration (connections + free-form content keys) drives NOT-APPLICABLE with
  justification via `requires_deployment:`; `endpoint: live` + `connection:` resolves
  against `deployment.connections`. Protocol/inspection cases point at a written protocol
  (`templates/protocol.md`) and are judged from an execution record
  (`templates/protocol-result.yml`, read from `protocol_results_dir`, pinned into the run
  folder); no record → NOT-EXECUTED. Report §2 shows Verdict / Why / Strongest evidence /
  cases with scope+method; §3 groups cases by scope and prints the deployment declaration;
  §4 lists failing needs as findings to close and NOT-EXECUTED protocols as open items;
  the non-determinism statement moves to a Limitations subsection. Sidecar carries
  `deployment`, per-need `reason`, per-case `scope`/`method`/`protocol`/`execution_record`,
  `summary.scopes`. Regression suite extended to 25 cases (deployment dependency
  resolution, protocol records, binary verdicts, end-to-end red→green on a synthetic
  manifest). Rationale: a GxP validation report has no third verdict; capability tests
  make the validation portable while deployment tests stay the customer's own.

- 5 (2026-09-08): **Needs are user stories composed from structured fields (manifest
  schema 1.2).** Each need carries `role`, `need` (the outcome the role can observe,
  phrased to follow "I need the workbench to…") and `so_that` (the purpose, now
  required); the renderer composes _As a `role`, I need the workbench to `need`, so
  that `so_that`._ into the report §2 (single Need column), the sidecar (`statement`,
  `so_that`) and the console. The runner lints the contract — missing fields are an
  error on 1.2+ manifests (warning on older), story wording duplicated inside `need`
  or `so_that` is a warning. Templates and SKILL.md updated; Best Practices row
  added. Rationale: the previous register was role-perspective but implicit — only
  one need said "I need" and none carried a purpose, which is what a reviewer needs
  to judge whether the mapped evidence assures the need. Also adds the skill's own
  regression suite, `tests/test_runner_renderer.py` (21 cases) — the validation tool
  had been an untested deterministic checker itself, the very anomaly its report
  flags for other skills.

- 4 (2026-09-08): **Evidence tiers + full environment record (run/sidecar schema 1.1).**
  *Tiers (D7):* every test case declares `endpoint: none | mocked | live`; the manifest
  gains `connections:` (what this deployment has per external system). A `live` case
  whose connection is declared `none` is reported **NOT-APPLICABLE** — never executed,
  never lowering a need or the overall verdict — while a declared-present but
  unreachable connection is a real SKIP/FAIL. New per-need `strongest_evidence` line
  ("mock-verified; live jira not applicable in this deployment"); Endpoint column in the
  report's results table and the sidecar; NOT-APPLICABLE need verdict; the same tier
  names are the pytest markers (`mocked`/`live`, `--live` opt-in, socket guard) the
  skills' own suites now use. *Environment record (D8):* the run JSON `environment`
  block now carries the dirty-file list, agents/rules installed, per-skill frontmatter
  **and** VERSION with `version_mismatch` flagged (D5), Python executable/architecture,
  harness version, model id + `model_captured`, per-binary tooling probe (path +
  `--version`), test-harness package versions resolved by `uv`, MCP servers
  approved/configured, per-connection reachability probes, and an isolation block; the
  report §1 renders it as a collapsed "Full environment record"; the sidecar carries the
  full block plus `warnings` and `summary.tiers`. *Runs of record (D2):* `--model-id`
  flag; loud `warnings[]` on dirty tree / uncaptured model / version-pin mismatch /
  tier-less case, printed to stderr and carried into the report banner. Evidence-log
  headers add `endpoint:` and resolved tooling versions. Template, SKILL.md schema
  summary, verdict semantics, and Best Practices rows updated. Anomaly policy tightened:
  an entry needs an owner and an expected clearing run.

- 3 (2026-07-28): UUT (unit under test) — `test_cases[].uut:` names the workbench
  component(s) a case actually runs against (multiple allowed; sentinel
  `all-skills` for workbench-wide sweeps). The runner pins each named skill to the
  version exercised in that run (`uut_versions`, resolved from the configuration
  baseline captured at run start) and stamps it into the results JSON, each
  evidence-log header, the report's results table, and the console sidecar — so
  "what was tested, at which version" is explicit per case, not just per run.
  Reviewer-friendly test cases — `test_cases[].title/description/approach` are
  written in plain language for non-specialist reviewers; the renderer derives a
  per-case `source` link (first existing repo path in the cmd, falling back to the
  manifest) and a human-readable `judged_by` pass rule, adds a "What each test case
  checks" section to the report, and passes description/approach/cmd/judged_by/
  source through the sidecar for the console's expandable rows; evidence-log
  headers carry purpose + approach. Validation setup record — every run records
  who ran it (git user/email, OS user, hostname, OS), how it was invoked
  (`--invoked-via cli|console`), and when, alongside the configuration under
  test; report §1 is now the full setup record. Test-artifact pinning — the run
  folder receives byte copies of the manifest (`validation.yml`) and of each
  case's test source (`pinned/<TC-ID>/`, `__pycache__` excluded), sha256-manifested
  in the run JSON, so the exact tests executed stay reviewable across runs even
  as the skills under test evolve.
- 2 (2026-07-27): Role-based user needs — `user_needs[]` gains `role:` (the human
  role whose need it is) and `implemented_by:` (mechanism as traceability info,
  never part of the need); needs are authored in the role's plain language,
  implementation-free. Per-case evidence logs — the runner writes each case's full
  execution transcript (command, cwd, env changes, timestamps, exit code, judgment
  rule, complete ANSI-stripped output) to `results/<run-id>/<TC-ID>.log`; the run
  JSON and sidecar carry the `log` path; the report's results table links each log.
  Output-location convention — generated outputs (results, evidence logs, report,
  sidecar) default to `tools/workbench-validation/` (tool output), while authored
  sources (plan, manifest) stay in `docs/`; documented the data-first contract
  (manifest + results + logs are canonical; the markdown report is one projection —
  customer-QMS formats are additional transforms over the same data).
- 1 (2026-07-27): Initial version — declarative validation manifest (user_needs +
  test_cases with pass/fail patterns, env control, requires-gating), runner with
  timestamped results JSON + config baseline (git SHA, per-skill versions, hooks,
  model id), report renderer (needs × tests × results → per-need verdicts +
  fitness-for-use conclusion + known anomalies + LLM non-determinism statement), and
  console sidecar (`schema_version: 1.0`) for the project console Settings
  sub-section.
