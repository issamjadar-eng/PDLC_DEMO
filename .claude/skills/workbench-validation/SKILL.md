---
name: workbench-validation
description: "MedTech-style tool validation of the AI workbench itself — the .claude/ toolchain (skills, agents, hooks, scripts, rules) used to author and manage design-control artifacts. Runs a declarative validation manifest (workbench user needs mapped to executable test cases over existing skill test suites, lints, and audits), records timestamped results JSON with a configuration baseline (git SHA, per-skill versions), and renders a single validation report + console sidecar for the project console's Settings → Workbench Validation sub-section. TRIGGER when the user wants to: validate the workbench / toolchain / skills ('are our skills validated', 'run the workbench validation', 'tool validation report', 'validate our .claude setup', 'is the toolchain fit for use'); refresh or view the validation report or its console view; add/modify workbench user needs (WUN-xx) or validation test cases; or edits files under docs/project/workbench-validation/ or the validation.yml manifest. Also trigger on ISO 13485 QMS-software-validation / CSA-style tool-assurance questions about the project's own tooling. NOT for validating the medical device itself (that's the DHF V&V) and NOT for structural project audits (/best-practices) or content gap analysis (/gap-analysis)."
version: 3
updated: 2026-07-28
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

1. **User needs** — a WUN-xx register authored in the project's validation plan.
   Each need is stated **from a role's perspective, in the role's own language** —
   the outcome the role requires, free of implementation detail (the role does not
   know how the workbench meets the need). The mechanism goes in `implemented_by:`
   (traceability info only).
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

**Honesty model (load-bearing).** Deterministic components (hooks, scripts, lints,
renderers) get scripted, repeatable test evidence. LLM-driven behavior is *not*
repeatably testable: needs assured by human review + deterministic gates + audit trail
are declared `coverage: process-control` (or `exploratory`) and reported as such —
never as a scripted PASS. The configuration baseline (git SHA + model identifier) is
recorded per run; a model change is a first-class revalidation trigger.

## Supporting Files

| File | Purpose |
|------|---------|
| `scripts/run_validation.py` | Executes the project's `validation.yml` manifest; writes `results/<run-id>.json` + `latest.json` with config baseline. `--render` chains the renderer. Exit 1 on FAIL/ERROR (CI-friendly). |
| `scripts/render_report.py` | Joins manifest + latest run → `validation-report.md` + console sidecar JSON (`schema_version: 1.0`). |
| `templates/validation-plan.md` | Scaffold for the project's validation plan (intended-use classes, risk tiers, WUN register). |
| `templates/validation.yml` | Scaffold for the project's manifest (user_needs + test_cases schema, documented inline). |
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
| Run results | `tools/workbench-validation/results/<run-id>.json` (+ `latest.json`) | Generated, append-only |
| Per-case evidence logs | `tools/workbench-validation/results/<run-id>/<TC-ID>.log` | Generated — full execution transcripts, the evidence of record |
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
python3 .claude/skills/workbench-validation/scripts/run_validation.py --root <repo_root> --render
```

- Full runs only for record-keeping; `--only TC-01,TC-05` for debugging (marked
  `partial: true` and flagged in the report).
- Cases needing pytest use `uv run --no-project --with pytest` (network on first
  resolve, cached after). Cases with `requires:` binaries missing are SKIPPED, not
  failed.
- Review the summary; a FAIL is a finding to triage (fix the tool, or record the
  anomaly in the manifest `known_anomalies:` with rationale), never something to
  silently drop from the manifest.

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
known_anomalies: ["..."]           # accepted/triaged anomalies carried into §4
revalidation_triggers: ["..."]     # optional override of the default set
user_needs:
  - id: WUN-01
    role: "DHF author"             # the human role whose need this is
    class: authoring               # authoring|audit|gates|renderers|console|config-control|cross-cutting
    tier: T1                       # T1 high / T2 medium / T3 low
    need: "Plain-language outcome the role requires — no implementation detail."
    coverage: tests                # tests | process-control | exploratory
    implemented_by: "mechanism"    # traceability info only — not part of the need
    process_controls: ["..."]      # required when coverage != tests
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
- **Verdict semantics**: PASS / FAIL / PARTIAL (skips) / NO-EVIDENCE (tests-coverage
  need with no mapped case — a manifest gap, fix the manifest) / PROCESS-CONTROL /
  EXPLORATORY. Overall verdict: FAIL > PARTIAL > PASS.
- **Do not validate the device with this skill** — device V&V lives in the DHF. This
  skill validates the toolchain that produces those artifacts.
- The console integration (Settings → Workbench Validation) is owned by the
  project-console skill; this skill only guarantees the sidecar contract above.
