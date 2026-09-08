---
name: workbench-validation
description: "MedTech-style tool validation of the AI workbench itself — the .claude/ toolchain (skills, agents, hooks, scripts, rules) used to author and manage design-control artifacts. Runs a declarative validation manifest (workbench user needs mapped to executable test cases over existing skill test suites, lints, and audits), records timestamped results JSON with a configuration baseline (git SHA, per-skill versions), and renders a single validation report + console sidecar for the project console's Settings → Workbench Validation sub-section. TRIGGER when the user wants to: validate the workbench / toolchain / skills ('are our skills validated', 'run the workbench validation', 'tool validation report', 'validate our .claude setup', 'is the toolchain fit for use'); refresh or view the validation report or its console view; add/modify workbench user needs (WUN-xx) or validation test cases; or edits files under docs/project/workbench-validation/ or the validation.yml manifest. Also trigger on ISO 13485 QMS-software-validation / CSA-style tool-assurance questions about the project's own tooling. NOT for validating the medical device itself (that's the DHF V&V) and NOT for structural project audits (/best-practices) or content gap analysis (/gap-analysis)."
version: 6
updated: 2026-09-08
dependencies:
  skills:
    - name: project-console
      type: optional
      reason: renders the Settings → Workbench Validation sub-section from this skill's sidecar
---

# Workbench Validation

Risk-based, CSA-style validation of the AI workbench — the `.claude/` toolchain used to
author and manage controlled artifacts. In a MedTech QMS, tools that produce or gate
controlled records require validation for intended use (ISO 13485 QMS-software
validation posture; see the project's own tool-validation work instruction if one
exists under `docs/internal/`). This skill provides the three visible components:

1. **User needs** — a WUN-xx register authored in the project's manifest and plan. Each
   need's verdict is PASS / FAIL / NOT-APPLICABLE, with a stated reason.
   Each need is a **user story composed from structured fields**:
   _As a `role`, I need the workbench to `need`, so that `so_that`._ The outcome is
   what the role can observe, free of implementation detail (the role does not know
   how the workbench meets the need); the purpose is **required** — it is what a
   reviewer judges the evidence against. The renderer composes the sentence (report,
   sidecar `statement`, console); the runner refuses a need missing any of the three
   fields. The mechanism goes in `implemented_by:` (traceability info only).
2. **Tests** — a declarative manifest mapping each need to executable evidence
   (existing skill test suites, lints, audits), run by a deterministic runner. Every
   case's **full execution transcript** (command, cwd, env changes, timestamps, exit
   code, judgment rule, complete output) is persisted as a per-case evidence log —
   the evidence of record, beyond the pass/fail summary.
3. **Validation report** — a single generated report joining needs × tests × results
   into per-need verdicts and a fitness-for-use conclusion, plus a console sidecar.

**Data-first (load-bearing).** The canonical layer is machine-readable — the manifest
(needs + catalog), the run JSON (results + configuration baseline), and the evidence
logs. The markdown report is **one generated projection** of that data; a customer
QMS that requires its own report format gets a new transform over the same canonical
data, never a rewrite of the validation.

**Evidence tiers (load-bearing).** Every test case declares `endpoint: none | mocked |
live` — whether it touched no external system, a fake Jira/Confluence transport with
canned payloads, or a real enterprise endpoint. The manifest's `connections:` block
declares what the deployment has; a `live` case for a connection declared `none` is
reported **NOT-APPLICABLE** (a statement, not a gap) and never lowers a verdict, while
a declared-present but unreachable connection is a real SKIP/FAIL. Each need's verdict
carries a plain-language "strongest evidence" line ("mock-verified; live jira not
applicable in this deployment"). MCP-mediated integration paths cannot be driven from
pytest — those are `exploratory` needs assured by recorded live probes, never a
scripted PASS. The same tier names are pytest markers (`mocked`, `live`, opt-in via
`--live`) in the skills' own suites, whose `conftest.py` socket guard blocks network
access outside the `live` tier.

**Environment record (load-bearing).** The run JSON's `environment` block is the
canonical setup record: configuration under test (commit, dirty-file list, per-skill
versions with frontmatter/VERSION mismatches flagged, hooks, agents, rules), runtime
(Python, OS, harness version, model id), tooling (every required binary's resolved
path and version, test-harness package versions), connections (declared tiers, MCP
servers, reachability probes) and isolation (env vars stripped/set). The report
renders it as a collapsed "Full environment record" in §1 and the console shows an
expandable Environment panel — the verdict stays readable, the record stays complete.

**Verdict model (load-bearing, GxP-style).** Every user need gets **PASS, FAIL or
NOT-APPLICABLE** — nothing else. A need with no applicable executed case **FAILS ("no
evidence")**; an unexecuted protocol FAILS its need; a skipped case (missing binary)
FAILS its need. The evidence **method** is an attribute of the test case, never a
verdict: `scripted` (runner-executed, judged by exit code/pattern), `protocol` or
`inspection` (operator-executed against a written protocol with acceptance criteria,
judged from an execution record at `<protocol_results_dir>/<TC-ID>.result.yml`).
Non-determinism of the assistant is handled by protocols — fixed challenge set, explicit
acceptance thresholds, repeat runs under a pinned model — and stated as a limitation; it
does not create a third verdict. The configuration baseline (git SHA + model identifier)
is recorded per run; a model change is a first-class revalidation trigger and a protocol
result is valid only for the model id in its execution record.

**Capability vs deployment scope (load-bearing).** Every test case declares
`scope: capability` — it ships with a skill and runs against the skill's own fixtures,
portable to any project, proving what the tool can do — or `scope: deployment` — it runs
the deployed workbench against this instance's own content (its QMS documents, taxonomy,
submission packages, corpus, connections), the part a deployment authors for itself from
the skill's guidance and templates. The manifest's `deployment:` block declares what the
instance has; a deployment case whose `requires_deployment:` keys are declared absent is
**NOT-APPLICABLE with that justification** (never a silent skip), and NOT-APPLICABLE never
lowers a verdict. A customer QMS therefore reuses every capability case as-is and adds
deployment cases for its own content.

## Supporting Files

| File | Purpose |
|------|---------|
| `scripts/run_validation.py` | Executes the project's `validation.yml` manifest; writes `results/<run-id>.json` + `latest.json` with config baseline. `--render` chains the renderer. Exit 1 on FAIL/ERROR (CI-friendly). |
| `scripts/render_report.py` | Joins manifest + latest run → `validation-report.md` + console sidecar JSON (`schema_version: 1.0`). |
| `templates/validation-plan.md` | Scaffold for the project's validation plan (intended-use classes, risk tiers, WUN register). |
| `templates/validation.yml` | Scaffold for the project's manifest (user_needs + test_cases schema, `deployment:` declaration, documented inline). |
| `templates/protocol.md` | Scaffold for a written test protocol (method: protocol / inspection): challenge set, procedure, acceptance criteria, repeatability, execution-record pointer, sign-off. |
| `templates/protocol-result.yml` | Execution-record schema for a protocol case — the runner reads `<protocol_results_dir>/<TC-ID>.result.yml` (verdict, executed, operator, model_id, git_sha, runs, evidence, deviations, sign-off). |
| `tests/test_runner_renderer.py` | Regression suite for the runner + renderer (need-format lint, frontmatter parsing, story composition, NOT-APPLICABLE verdicts, strongest-evidence text, end-to-end synthetic manifest). `uv run --no-project --with pytest --with pyyaml -- pytest .claude/skills/workbench-validation/tests -q` |
| `README.md` | Design doc, Best Practices table, Changelog. |
| `VERSION` | Skill version (mirrors frontmatter). |

## Project Artifacts (produced/consumed)

All project-specific content lives in the project tree, never in this skill.
**Authored** sources live under `docs/`; **generated** outputs live under `tools/`
(the tool-output convention — generated data, not authored documentation):

| Artifact | Path (default) | Nature |
|---|---|---|
| Validation plan (roles, user needs, tiers, intended use) | `docs/project/workbench-validation/validation-plan.md` | Authored, durable |
| Validation manifest | `docs/project/workbench-validation/validation.yml` | Authored, declarative |
| Run results | `tools/workbench-validation/results/<run-id>.json` (+ `latest.json`) — schema 1.1 carries `environment`, `warnings`, `connections`, per-case `endpoint` | Generated, append-only |
| Per-case evidence logs | `tools/workbench-validation/results/<run-id>/<TC-ID>.log` | Generated — full execution transcripts, the evidence of record |
| Written protocols | `docs/project/workbench-validation/protocols/<TC-ID>.md` | Authored from `templates/protocol.md` |
| Protocol execution records | `tools/workbench-validation/protocols/<TC-ID>.result.yml` | Recorded by the operator per execution; pinned into the run folder |
| Pinned test artifacts | `tools/workbench-validation/results/<run-id>/pinned/<TC-ID>/` + a pinned copy of `validation.yml` in the run folder | Generated — byte copies (sha256-manifested in the run JSON) of the exact test sources + case definitions this run executed, so each run stays reviewable after the tools evolve |
| Validation report | `tools/workbench-validation/validation-report.md` | Generated — never hand-edit |
| Console sidecar | `tools/workbench-validation/workbench-validation-index.json` | Generated — consumed by project-console Settings |

If the project console is installed, add `tools/workbench-validation` to the
console's `grounding.extra_roots` (in the project-owned `console.yaml`) so the
report and evidence logs resolve in the Documents viewer.

## Actions

Parse the argument string for one of: `init`, `run`, `render`, `validate`, `status`, `help`.

### `init`

Scaffold the project's validation artifacts (first-time setup):

1. Read the target folder's README and its parent's per the project's readme-before-write
   rule; create `docs/project/workbench-validation/README.md` if missing (Structure /
   Expected Content / Conventions / Changelog sections).
2. Instantiate `templates/validation-plan.md` and `templates/validation.yml` into
   `docs/project/workbench-validation/`, then **author the project-specific content**:
   the WUN register (ground user needs in the workbench's actual tool classes), risk
   tiers, and the test-case catalog (survey `.claude/skills/*/tests/`, lint scripts,
   and audit scripts for executable evidence).
3. Ground the model in project sources: prefer the project's own tool-validation
   SOP/WI under `docs/internal/source-md/` for the intended-use / risk / evidence /
   baseline pattern. Anything cited from standards not distilled in-project must be
   flagged `[VERIFY]`.
4. For a demonstration project, stamp the demo banner into the plan and manifest
   `banner:` so every generated report carries it.

### `run`

Execute the manifest and record results. Every run writes a **setup record** into
the results JSON: configuration under test (git SHA + per-skill versions + hooks),
operator (git user/email, OS user, hostname, OS), invocation source
(`--invoked-via cli|console`), and start/finish timestamps — plus pinned copies of
the manifest and each case's test source:

```bash
python3 .claude/skills/workbench-validation/scripts/run_validation.py --root <repo_root> --render \
    --model-id <model identifier>
```

- **Runs of record need a clean tree and a captured model id.** The runner warns
  loudly (and records `warnings[]`) when the working tree is dirty, when the model
  id is not captured (`--model-id`, or `$CLAUDE_MODEL`), when a skill's frontmatter
  and `VERSION` disagree, or when a case has no `endpoint:` tier. A run with
  warnings is a debugging run, not a run of record.
- Full runs only for record-keeping; `--only TC-01,TC-05` for debugging (marked
  `partial: true` and flagged in the report).
- Cases needing pytest use `uv run --no-project --with pytest` (network on first
  resolve, cached after). Cases with `requires:` binaries missing are SKIPPED, not
  failed.
- Review the summary; a FAIL is a finding to triage — **fix the tool at the source**,
  or record the anomaly in `known_anomalies:` **with an owner and the run by which it
  is expected to clear** — never something to silently drop from the manifest, and
  never a parking place: an anomaly entry without an owner is not a disposition.

### `render`

Re-render report + sidecar from the latest recorded run without re-executing tests:

```bash
python3 .claude/skills/workbench-validation/scripts/render_report.py --root <repo_root>
```

Use after editing the plan/manifest prose (needs, anomaly notes) when test results are
still current.

### `validate`

Alias for `run` with `--render` — the periodic end-to-end refresh. Recommend after:
a registry sync (`/sync-skills pull`), a skill/hook change, a model change, or on the
project's audit cadence.

### `status`

Report freshness without running anything: read the sidecar, show run_id / date /
verdict / counts, and compare the recorded `git_sha_short` against current HEAD —
if they differ, recommend a re-run (config baseline moved).

### `help`

Show the action list and the three-component model.

## Manifest schema (summary — full inline docs in `templates/validation.yml`)

```yaml
schema_version: "1.0"
banner: "_Demo sample data — not for clinical use._ ..."   # stamped on the report
plan: docs/project/workbench-validation/validation-plan.md
results_dir: tools/workbench-validation/results
sidecar: tools/workbench-validation/workbench-validation-index.json
report: {title: "...", output: tools/workbench-validation/validation-report.md}
deployment:                        # what THIS instance has — drives NOT-APPLICABLE
  connections: {jira: none, confluence: none, browser: none}
  content: {qms_forms: true, taxonomy: false, submission_package: true, ...}   # free-form dotted keys
protocol_results_dir: tools/workbench-validation/protocols
known_anomalies: ["..."]           # accepted anomalies (owner + expected clearing run) → §4
revalidation_triggers: ["..."]     # optional override of the default set
user_needs:
  - id: WUN-01
    role: "DHF author"             # the human role whose need this is
    class: authoring               # authoring|audit|gates|renderers|console|config-control|cross-cutting
    tier: T1                       # T1 high / T2 medium / T3 low
    need: "outcome the role can observe — follows 'I need the workbench to'"
    so_that: "purpose — required; the renderer composes the user story"
    implemented_by: "mechanism"    # traceability info only — not part of the need
test_cases:
  - id: TC-01
    title: "Plain-language: what is being checked, in everyday words"
    description: "What the case checks and why it matters — written for a reviewer who is not a toolchain specialist."
    approach: "How the check works, plainly."
    wun: [WUN-01]                  # needs this case evidences (the only mapping edge)
    uut: [task]                    # unit(s) under test — the workbench component(s) the
                                   # case actually runs against; multiple allowed; skill
                                   # names resolve to the version exercised (uut_versions);
                                   # sentinel `all-skills` = workbench-wide sweep
    scope: capability              # capability (skill fixtures, portable) | deployment (this instance)
    method: scripted               # scripted | protocol | inspection
    requires_deployment: [content.qms_forms]   # deployment cases — dotted keys into `deployment:`
    endpoint: none                 # none | mocked | live (required)
    connection: jira               # live only — key into deployment.connections
    protocol: docs/.../TC-xx.md    # protocol/inspection cases — result read from protocol_results_dir
    cmd: ["bash", "path/to/test.sh"]
    cwd: .                         # optional, relative to root
    timeout: 600                   # seconds, optional
    requires: [uv]                 # binaries; missing -> SKIPPED
    env_unset: [SOME_VAR]          # strip env vars that leak session state into tests
    env: {KEY: value}              # extra env
    pass_pattern: "ALL TESTS PASSED"   # for suites that exit 0 regardless
    fail_pattern: "FAILED"             # overrides exit 0
```

## Notes

- **The report and sidecar are generated projections** — regenerate, never hand-edit.
  The plan and manifest are the authored sources of truth.
- **Verdict semantics**: need = PASS (every applicable case passed) / FAIL (any
  applicable case FAIL, ERROR, SKIPPED or NOT-EXECUTED — or no case at all: "no evidence")
  / NOT-APPLICABLE (every mapped case depends on something the deployment declares
  absent). Overall: FAIL if any need FAILs, else PASS; NOT-APPLICABLE never lowers it.
  Case statuses: PASS / FAIL / SKIPPED / NOT-APPLICABLE / NOT-EXECUTED / ERROR.
- **Do not validate the device with this skill** — device V&V lives in the DHF. This
  skill validates the toolchain that produces those artifacts.
- The console integration (Settings → Workbench Validation) is owned by the
  project-console skill; this skill only guarantees the sidecar contract above.
