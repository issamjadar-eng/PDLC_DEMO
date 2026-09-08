# 122 — Port the `multimodel` Provider Skill (OpenAI / Gemini / Grok Access Layer)

**ID**: 122
**Created**: 2026-09-08
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. **Update at every meaningful checkpoint (HARD RULE).** Tick the Todo, add a dated Changelog line naming the concrete artifact, refresh progress and the matching `## Economics` entry in the same edit.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**
6. **Estimation provenance.** `## Economics` follows `.claude/skills/usage-metrics/references/effort-estimation-rubric.md`.

**Resume command**: `bash .claude/hooks/task-activate.sh add <SESSION_ID> ben/122`

## Goals

The user asked (2026-09-08) to review a sister project's skill that exposes other model providers (OpenAI, Gemini, Grok) and port it here as a **lightweight, registry-shareable wrapper** so that (a) the user can make ad-hoc cross-model calls and (b) other skills can declare an optional dependency on it for cross-checking analysis and multi-model workflows. Then run and test it.

- **Source reviewed**: `../investments/.claude/skills/multimodel/` (v1, 2026-08-17; ~1,950 lines: `src/multimodel/` package + `scripts/setup.py` + 5 provider adapters; tests live at the sister repo root under `tests/test_multimodel_*.py` and `tests/test_layer_separation.py`; config at `config/models.toml`).
- **Target**: `.claude/skills/multimodel/` conforming to the skill-creator conventions (frontmatter, `## Supporting Files`, `## Actions`, README with `## Best Practices` + `## Changelog`, project-agnostic, self-contained, skill-local hermetic tests), wired into `project.yml` (`multimodel:` config block + `security.approved_skills`).

### Review findings on the source (what to keep, what to change)

| # | Finding | Disposition |
|---|---------|-------------|
| R1 | Core design is sound and worth keeping verbatim in spirit: fail-closed `Response.ok`, never-raise fan-out, `available()` vs `probe()` split, `jsonx.best_object` last-substantive-object extraction, per-provider schema dialect handling (`strict_schema` for OpenAI). | Keep |
| R2 | Config is a root `config/models.toml`; this project's wiring convention is `project.yml` blocks read at runtime. | Read a `multimodel:` block from `project.yml` (TOML still accepted for portability). |
| R3 | `local` provider depends on a `localmodels` skill that does not exist here and carries investing-specific rationale. | Drop from the port; note in README as re-addable. |
| R4 | Investing vocabulary leaks into docs/config (`redteam` role, "thesis", "trade", CLAUDE.md §4/§6.2 references, a named person). | Strip; roles become caller-defined labels (`challenger` / `worker` in the template). |
| R5 | `openai_http` needs `httpx` → a `uv` venv under `tools/multimodel/`. | Rewrite on stdlib `urllib` → zero dependencies, no venv, no lockfile. `setup` only writes the config block + CLI provenance. |
| R6 | Install docs use `curl … \| bash`; the project's secops scanner flags pipe-to-shell in `.md`. | Point at vendor install pages instead. |
| R7 | CLI `ask` only broadcasts to all providers; no `--provider`, `--schema`, `--prompt-file`, `--json` — needed for other skills to depend on it. | Add them; document the CLI + Python contract for dependents. |
| R8 | Unknown provider `type` is silently skipped by `build_provider`. | `doctor` now reports skipped entries. |
| R9 | Data-governance: nothing says what may be sent off-machine. | Add a "What leaves the machine" section + `policy:` block in config (documented, caller-enforced). |
| R10 | `EXTRA_BIN_DIRS` lacks `~/.grok/bin` (where the Grok CLI installs on this machine). | Add. |

## Todos

- [x] Task 122 created; source reviewed; findings R1–R10 recorded
- [x] Skill scaffolded: `SKILL.md`, `README.md`, `src/multimodel/` (types, base, jsonx, registry, council, config, providers: grok / codex / antigravity / openai_http), `scripts/multimodel.py` CLI, `scripts/setup.py`, `templates/models.yml`
- [x] Tests ported + extended under `.claude/skills/multimodel/tests/` (hermetic; socket guard) — 72 pass
- [x] `project.yml`: `multimodel:` block appended by `setup.py` + `approved_skills` entry; `tools/multimodel/provenance.json` + README recorded
- [x] Run: unit tests (72/72), `doctor --quick`, live `doctor`, one live structured `ask` on grok; secops artifact scan (one Critical on a test docstring literal — reworded)
- [x] **R11 (found by the live run)**: vendor CLIs are agents with tools — Grok read the project's DHF/QMS files during the ask (7 turns, ~487k tokens, $0.07). Added per-provider `workspace: isolated | project` (default isolated: CLI runs in an empty temp dir via `--cwd` / `--cd` / process cwd), probes always isolated, CLI `--workspace` override, "What leaves the machine" table; grok adapter reports `num_turns` + cost in `usage`.
- [x] **R12 (found by the isolated live run)**: a Grok run that exhausted its output budget mid-reasoning returned `stopReason: cancelled`, `structuredOutput: null`, and five interim "placeholder" objects in `text` — the text-scraping fallback accepted a placeholder as the verdict (fail-open). Adapter now trusts the CLI's `structuredOutput` / `stopReason` / `structuredOutputError` exclusively when present; text scraping only for old CLIs without the field. 4 regression tests.
- [x] Report back to the user (2026-09-08)
- [x] Commit → PR → merge — PR #192 (skill, tools/multimodel, project.yml hunk, this task doc; committed from a separate worktree so the concurrent session's branch was untouched). Was: (only when the user asks; the working tree also carries unrelated uncommitted changes from ben/118 — scope the commit to `.claude/skills/multimodel/`, `tools/multimodel/`, `project.yml`, `tasks/ben/122-*.md`, `tasks/ben/000-index.md`)
- [x] User signed in to codex + agy (agy now 1.1.27). **R13**: Codex refused the isolated temp dir ("Not inside a trusted directory") → adapter passes `--skip-git-repo-check`. **R14**: agy 1.1.27 keeps no token at the sister's path → `available()` now asks the tool (`agy models`, which says "Please sign in" when unauthenticated), and `--print-timeout` is aligned to the provider timeout. Live doctor: all three providers answered with structured output (grok 3.0 s, codex 6.4 s, antigravity 7.7 s / 10.9k tokens).
- [x] **Direction change (user, 2026-09-08 afternoon)**: default workspace flipped from `isolated` to `project` with READ-ONLY enforcement — the agent may browse the repo for context, never write/execute; prompts still carry the question + key excerpts. Behavioural proof, per CLI (R15–R18):
  - R15 grok: `--permission-mode plan` blocks reads as well as writes (unusable); `--tools read_file,list_dir,grep` allowlist + `--disable-web-search` reads and cannot write (model itself reported "no write tool"). Reads execute only in a directory the CLI trusts (the project root is; a temp dir is not). Grok sometimes answers in one turn WITHOUT calling its read tool (seen on 2 of 5 runs) — model behaviour, handled by a bounded read-miss retry in `verify`.
  - R16 codex: `--sandbox read-only` + `--cd <root>` reads the marker, write blocked. Adapter refuses `project` workspace with any other sandbox.
  - R17 antigravity: `--sandbox` does NOT stop file writes when permissions are auto-approved (it wrote `written.txt`), so `--dangerously-skip-permissions` is never passed. Print mode routes every tool call to interactive review (`toolPermission=request-review`) and stalls to the print timeout — reads too; `--mode plan` alone stalls the same way. Project mode therefore requires `view_file, list_dir, grep_search, find_by_name` in the CLI's own `~/.gemini/antigravity-cli/settings.json permissions.allow` ([VERIFY] rule syntax — the shipped example is `command(which)`); adapter reads (never writes) that file and refuses project mode with the exact instruction otherwise; runs with `--mode plan` when allowed.
  - R18 verify bug found by its own tests: parallel providers shared one marker path (race) → per-provider subfolders under `.state/multimodel-verify/<provider>/`, removed after the run.
- [x] **R19**: Grok's `--json-schema` constrains the FIRST turn, so a model that narrates ("I'll read the file first…") is forced into the JSON shape and the run ends before any tool call — measured 0/2 reads with the flag vs 3/3 without, same prompt. Adapter now has `schema_mode: auto | cli | prompt` (auto = schema in the prompt + `jsonx` parse of the text stream in `project` workspace; CLI-enforced schema in `isolated`). After this, live `verify`: grok PASS (2 turns), codex PASS, antigravity refused pending the settings rule; grounded ask on grok via the prompt-schema path: 8 turns, 11 files, `class_c_correct` 0.88.
- [x] `verify` action + `src/multimodel/verify.py` (behavioural: fresh-token marker read + write attempt, PASS / FAIL / CRITICAL, `--attempts` read-miss retry, never retries a landed write). Live: codex PASS; grok FAIL(read) on that run (write blocked) — tool-skipping, see R15; antigravity refused (needs the settings rule). Grounded project-mode ask (grok 9 turns / 11 files, codex 9 files): both `class_c_correct` citing the project's own WI + HAZ-001, no repo writes (files modified in the tree during the run belong to concurrent session bd335db9 / task 123).
- [x] **R20 — user: "I don't want it global; can gemini settings be project level?"** Answered empirically (agy 1.1.27, print mode, 13 runs): plain `-p` soft-denies EVERY tool confirmation incl. `ListDir`/`ViewFile` (no tools → clean prompt-only); `--dangerously-skip-permissions` and `--sandbox` both let `write_to_file`/`RunCommand` writes land; `--sandbox`/`--mode plan` alone stall to the print timeout; repo-level `.agents/hooks.json` and `.agents/plugins/<name>/{plugin.json,hooks.json}` PreToolUse gates were NOT loaded ("loaded 0 named hooks from 0 hooks.json file(s)") in trusted (PDLC_DEMO) and untrusted scratch repos, with and without skip-permissions; the CLI's project-scoped grants live at `~/.gemini/config/projects/<id>.json` (home dir, schema undocumented, [VERIFY]). Decision: antigravity ships `workspace: isolated` (template + project.yml); project mode remains opt-in behind the user-global rule; `verify` reports isolated-by-config providers as skipped, `--provider` forces. Experiment table in the skill README. No global settings were modified.
- [x] **R21 — user's proposal: skill setup auto-populates a project-scoped Antigravity grants file (create-if-absent, never overwrite; mindful that some projects run Gemini as their primary agent).** Known: read tools `view_file, list_dir, grep_search, find_by_name`; grant grammar `<kind>(<target>)`, kinds `file|command|url|mcp`, `*` wildcard (headless denial message + binary literals); `--project <id>` selects `~/.gemini/config/projects/<id>.json` by its `id` (verified in the log). Unknown: where project grants persist — three schema placements in that file were ignored ("no grants for project"); the `PermissionGrantStore` location was not found in strings or on disk; whether `file(*)` also permits writes. Throwaway probe files (`multimodel-probe`, `mm-probe-a/b/c`) were created under `~/.gemini/config/projects/` and removed by the same commands; no existing file was modified. Decision: do NOT implement a blind write; the setup design (own project id `multimodel-<slug>`, create-if-absent, adapter passes `--project`) is recorded in the README pending the schema. Next step needs the user: one interactive `agy` session in the repo to let the CLI persist a project grant, then diff `~/.gemini`.
- [x] **R22 — user: "can you not find the docs?"** Found and read: antigravity.google/docs/permissions, /docs/cli/headless, /docs/cli/projects, /docs/cli/settings, /docs/cli/commands/permissions, GitHub issue antigravity-cli#548, a public settings gist. Corrections: rule grammar is `read_file(...)` / `write_file(...)` (not `file(...)` — probes A–C in R21 were invalid); docs say reads+writes inside the *active project directory* are auto-allowed and shell/web default to ask (soft-denied headless); `/permissions` has Project/Shared/Global scopes with undocumented storage; #548 reports headless ignoring `permissions.allow`. `--new-project` made the CLI write `~/.gemini/config/projects/ad937ff8-d843-43f6-be3f-d8b63847e6e2.json` ("PDLC_DEMO", `projectResources.resources[].folderUri` = this repo) — the schema sample the user asked for. **Incident**: that run and the follow-up `--project` run each opened an OAuth flow that timed out; `agy models` now says sign in — the user must re-login. Adapter gate rewritten to the documented grammar (+ write-implies-read refusal); 3 tests added. The workspace-bound project file was left in place (harmless; CLI-authored) — user to keep or delete.
- [x] **R23 — after re-login, the decisive probes**: under `--project <workspace-bound>`: read-only prompt → marker returned, no rule, no denial (reads auto-allowed inside the active project directory, as documented); write attempt → `WriteToFile` soft-denied, CLI ends the run with no output, no file on disk; `--mode plan` → model fell back to `RunCommand`, denied (dropped from the adapter). **Implemented the user's design**: `setup` reuses the project bound to the workspace (found the CLI-created `ad937ff8-…` file by `folderUri`) or creates `~/.gemini/config/projects/multimodel-<slug>.json` (create-if-absent, own id, `FileExistsError` on an id clash, never `settings.json`, never the default project); adapter resolves the id from `folderUri` or `project_id:` and passes `--project`; refuses project mode when CLI settings hold a `write_file(...)` allow rule over the repo; names the denied permission from stderr. `verify` split into a read probe + a write probe (silent post-denial run still judged from disk). Template + project.yml: antigravity back to `workspace: project`. 114 tests. Live `verify`: grok PASS, codex PASS, antigravity PASS. Docs (SKILL.md, README table + decision) updated.
- [ ] Follow-ups (user's call): optionally add a workbench-validation test case for the skill's suite; push the skill to the hitachi registry via `/sync-skills push`

## Strategy

<!-- STRATEGY CONTENT: architecture, multi-model access layer -->
**Multi-model access is a thin, dependency-free wrapper, not a framework.** The skill exposes two contracts — a CLI (`scripts/multimodel.py ask|doctor`) and a Python `Council` API — and nothing else. Provider adapters shell out to vendor CLIs on subscription OAuth (no keys on disk); the one API-key path (OpenAI HTTP) is stdlib `urllib` and disabled by default. Consumers declare `dependencies.skills: [{name: multimodel, type: optional}]` and must degrade gracefully when `doctor --quick --json` says a provider is unavailable. Config lives in `project.yml multimodel:` (project wiring convention), never in the skill.
<!-- /STRATEGY CONTENT -->

<!-- STRATEGY CONTENT: operations, data governance for external models -->
**Vendor CLIs are agents, not endpoints — give them read-only project access by default, and prove it.** (Supersedes the earlier isolate-by-default decision, same day, on the user's direction.) A grounded second opinion is the point: the prompt carries the question and the load-bearing excerpts, and the agent may read the repository to check or extend that context. Each adapter pins its CLI to read-only with the strongest control the CLI offers (Grok tool allowlist, Codex read-only sandbox, Antigravity plan mode behind a standing permission rule), `isolated` stays available per provider or per call for prompt-only sends, probes always run isolated, and the `verify` action re-proves read + no-write behaviourally after any CLI update. Flags are claims; the verifier is the evidence.

**What leaves the machine is the caller's decision, recorded in config.** Every prompt sent through this skill goes to a third-party service. The `multimodel.policy` block in `project.yml` states the project's posture (demo project: external sends allowed; no PHI, no credentials, no controlled-doc bodies unless the calling skill says so). Enforcement stays with the caller for now — a hard filter would need a real PHI/secret detector to be worth trusting.
<!-- /STRATEGY CONTENT -->

## Lessons Learned

<!-- LESSONS LEARNED: tooling -->
**"Project-level" in a vendor CLI's docs may mean its own project registry, not your repo.** Antigravity documents workspace `.agents/` customizations and per-project permission grants, but in print mode the hooks never loaded and the grants live under the home directory keyed by a project id. Read the load line in the CLI's log (`loaded N named hooks`) before designing around a documented feature.
<!-- /LESSONS LEARNED -->

<!-- LESSONS LEARNED: tooling -->
**A sandbox flag is not a read-only guarantee; test the behaviour.** Antigravity's `--sandbox` wrote a file once permissions were auto-approved; Grok's `plan` mode blocked reads along with writes. Only the marker-read / attempt-write check on disk told the truth for each CLI, and it belongs in the skill as a repeatable action, not in a chat transcript.
<!-- /LESSONS LEARNED -->

<!-- LESSONS LEARNED: tooling -->
**When a CLI reports its own structured-output verdict, never second-guess it by scraping.** The Grok envelope said `structuredOutput: null`, `stopReason: cancelled`; the adapter's fallback still scraped the text stream and found well-formed placeholder objects. A fail-closed layer must treat the tool's own "no" as final. Parsing heuristics belong only where the tool offers no verdict at all.
<!-- /LESSONS LEARNED -->

<!-- LESSONS LEARNED: tooling -->
**Read the agent's `thought` trace, not just its answer.** The structured answer looked perfect; only the raw envelope's reasoning trace revealed the CLI had spent 7 turns reading repository files. A wrapper around an agentic CLI must decide where that agent runs and what it may touch — "the prompt is all that leaves" was an assumption, not a fact, until the raw output was read.
<!-- /LESSONS LEARNED -->

<!-- LESSONS LEARNED: porting -->
**Porting a sister skill is a review, not a copy.** The sister's code was clean, but its docs and config carried its domain (investing roles, incident dates, a named person, a CLAUDE.md section number) and its tooling choices (uv venv for one optional dependency). Listing findings R1–R10 before touching files made each departure deliberate and reportable.
<!-- /LESSONS LEARNED -->

## Economics

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {"min": 4.5, "max": 6},
    "todos": [
      {
        "todo": "Review the sister skill (SKILL.md, 14 modules, config, 4 test files) and record findings R1-R10",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 2, "max": 4},
        "confidence": "med",
        "basis": "judgment - ~2,000 LOC read-through plus a written disposition table"
      },
      {
        "todo": "Port and rework the package: config loader, urllib HTTP adapter, CLI with provider/schema/prompt-file/json flags, setup script, template, docs",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 14, "max": 24},
        "confidence": "med",
        "basis": "software LOC-norm on ~1,700 non-test LOC, mid range - mostly adaptation of working code plus two new modules and two documents"
      },
      {
        "todo": "Hermetic test suite (86 tests across 8 files, CLIs faked, socket guard)",
        "personas": ["rd-lead", "vnv-lead"],
        "manual_hours": {"min": 6, "max": 10},
        "confidence": "med",
        "basis": "testing ~40% of dev effort (Boehm/Jones) on the port hours"
      },
      {
        "todo": "Wire into project.yml (config block, approved_skills), provenance, secops scan, live doctor/ask runs",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 2, "max": 4},
        "confidence": "high",
        "basis": "judgment - configuration and manual verification"
      },
      {
        "todo": "Read-only project workspace as default: per-CLI enforcement research (11 live experiments), grok allowlist + schema_mode, codex sandbox enforcement, antigravity permission gate, verify module + action, tests, docs",
        "personas": ["rd-lead", "cybersecurity", "vnv-lead"],
        "manual_hours": {"min": 8, "max": 14},
        "confidence": "med",
        "basis": "judgment - three vendor CLIs characterised empirically, ~500 LOC incl. 30 tests, security-relevant behaviour verified on disk"
      },
      {
        "todo": "Antigravity project-level permission investigation (13 live runs across flags, hook layouts, trusted/untrusted repos), decision, docs table, verify skip semantics",
        "personas": ["rd-lead", "cybersecurity"],
        "manual_hours": {"min": 3, "max": 6},
        "confidence": "med",
        "basis": "judgment - undocumented CLI behaviour characterised from logs and binary strings; small code change"
      },
      {
        "todo": "Investigate and fix R11 (agent read repo files) and R12 (cancelled run accepted placeholder) with regression tests and doc updates",
        "personas": ["rd-lead", "cybersecurity"],
        "manual_hours": {"min": 4, "max": 8},
        "confidence": "med",
        "basis": "judgment - two live-run root causes, three adapters touched, 14 tests, data-governance section"
      }
    ]
  }
}
```

## Changelog

- 2026-09-08: Skill written (`.claude/skills/multimodel/`: 4 providers, config loader, CLI, setup, template, 7 test files). `setup.py` appended the `multimodel:` block to `project.yml` and recorded `tools/multimodel/provenance.json` (grok 0.2.118, codex-cli 0.148.0, agy 1.0.16). `multimodel` added to `security.approved_skills`.
- 2026-09-08: Test run: first pass 68/71 (3 test-side bugs: a lambda signature, a 1-char test key that the scrubber redacted inside "network", a pipe-to-shell literal in a docstring that the secops scanner also flagged as Critical) → fixed; `_scrub` now ignores keys shorter than 8 chars; 72/72 green.
- 2026-09-08: Live `doctor`: grok answered with structured output (9.1 s); codex FAIL — ChatGPT refresh token revoked (user must `codex login` again); antigravity FAIL — `agy` 1.0.16 on this machine is not signed in and its `--help` shows none of the `--output-format json` / `--json-schema` flags the adapter (verified upstream against agy 1.1.13) relies on → needs `agy update` + sign-in.
- 2026-09-08: Live structured `ask` on grok (IEC 62304 class-C challenger prompt, demo content): exit 0, `data` parsed to the final answer object past five interim placeholder objects (the jsonx last-substantive rule doing its job). Finding R11 recorded — the Grok agent read repo files during the call.
- 2026-09-08: R11 implemented (`base.py` workspace + `workdir()`, all three CLI adapters, CLI `--workspace`, template + `project.yml` `workspace: isolated` on grok/codex/antigravity); `tests/test_workspace.py` added. Isolated live grok ask: 1 turn, ~51k tokens, $0.04, no repo reads (vs 7 turns / ~487k / $0.07) — but the run ended `cancelled` and the adapter accepted placeholder objects → R12.
- 2026-09-08: R12 implemented (grok fail-closed on `stopReason` / null `structuredOutput`); direct probes confirmed isolation itself is fine (`--cwd <empty>` and process-cwd both `end_turn` with structured output in ~3 s). secops artifact scan: 0 multimodel findings after rewording the docstring literal.
- 2026-09-08 (night): Pushed — PR #192 → main. Scope: `.claude/skills/multimodel/`, `tools/multimodel/`, `project.yml` (multimodel block + approved_skills), this task doc. The 000-index row for 122 was already on main via another session's commit.
- 2026-09-08 (night, later): R23 — Antigravity project mode works via a workspace-bound project; implemented + verified live (3/3 PASS); the CLI-authored project file is now the one `setup` reuses.
- 2026-09-08 (night): R22 — vendor docs read (5 pages + issue + gist); grammar corrected in the adapter; project-file schema captured from a CLI-authored file; Antigravity sign-in broken by the `--new-project` probe (needs user re-login). Sources: https://antigravity.google/docs/permissions , https://antigravity.google/docs/cli/headless/ , https://antigravity.google/docs/cli/projects/ , https://antigravity.google/docs/cli/commands/permissions , https://antigravity.google/docs/cli/settings/ , https://github.com/google-antigravity/antigravity-cli/issues/548
- 2026-09-08 (evening, later): R21 — project-scoped grants investigation (4 more live probes via `--project`, ~10 binary/log lookups). Schema for the grant store not found; README table + design note updated; no code change; all probe files removed.
- 2026-09-08 (evening): R20 — Antigravity project-level permissions investigated (temporary `.agents/` in the repo, removed by the same command; scratch repos under the session scratchpad). Antigravity → `isolated` in template + project.yml; `verify` skip semantics; README experiment table; test added. Corrects R17's wording: print mode *soft-denies* rather than stalls when no `--sandbox`/`--mode` flag is passed.
- 2026-09-08 (pm, later): R19 found by measuring Grok's tool-skipping (5 extra probes); `schema_mode` implemented with 4 tests; 108/108 green; secops 0 findings; live verify grok + codex PASS. `.state/multimodel-verify/` is removed after each run. Files modified in the working tree during the runs (`tasks/ben/053/054/080/114`, new `123`) belong to concurrent session `bd335db9` (its `.state/active-tasks-*` lists ben/123) — not vendor writes; codex ran read-only-sandboxed and grok had no write tool.
- 2026-09-08 (pm): User direction: read-only project access by default + repeatable proof. Six live experiments (grok plan / allowlist / allow-rules / dontAsk / trusted-dir; codex read-only; agy sandbox ± skip-permissions, plan) → R15–R17. Implemented: `base.py` default `project` at `project_root()`, grok `--tools` allowlist + web off, codex sandbox enforcement, agy `read_tools_allowed()` gate + `--mode plan`, `verify.py` + CLI `verify` (per-provider dirs, retry, cleanup), template/project.yml `workspace: project`, docs rewritten; 105 tests green; secops 0 findings. Live: doctor all green; verify codex PASS / grok read-miss / agy refused-with-instruction; grounded ask on grok + codex both cite the project's own classification WI and hazard analysis.
- 2026-09-08: After user sign-in: R13 (codex `--skip-git-repo-check`) and R14 (antigravity auth via `agy models`) implemented with tests; 88/88 green; secops 0 findings. Live doctor all green. Live isolated fan-out on the IEC 62304 challenger prompt: 2/3 answered — codex `class_c_correct` 0.97, antigravity `class_c_correct` 0.98 (both name the same crux: whether a control external to the software bounds over-delivery below serious injury); grok returned invalid JSON (CLI `structuredOutputError`) and the adapter reported NO ANSWER, exit 1. Across four Grok runs on this prompt, two clean answers — noted in SKILL.md.
- 2026-09-08: Final state — 86/86 tests; secops artifact scan 0 findings for the skill; `doctor --quick`: grok + codex available, antigravity not signed in, openai disabled; live: grok probe ok, codex refresh token revoked, agy needs update + sign-in. Retry of the isolated live ask succeeded: 1 turn, 15k tokens, $0.006, verdict `class_c_correct` (0.82) with a substantive Class B counter-argument. Reported to the user. NOT committed (no instruction to commit/push).

**Resume state**: all skill files under `.claude/skills/multimodel/` (+ `tools/multimodel/`, `project.yml` block + approved_skills, index row) are complete and uncommitted. Next step is the scoped commit → PR → merge when asked, then the follow-ups above.
- 2026-09-08: Task created. Source located at `../investments/.claude/skills/multimodel/`; full read of SKILL.md, all modules, config, and the four sister test files; findings R1–R10 recorded above.
