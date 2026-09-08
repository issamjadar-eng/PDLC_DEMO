# 119 — Workbench Validation: Assess Failures and Drive to a Correct PASS

**ID**: 119
**Created**: 2026-09-08
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
   - **when you tick a Todo off (or add/restructure Todos), fill/refresh the matching `## Economics` entry in the same edit** — the by-hand person-hours that unit would have taken, ranged + persona-tagged, per the rubric (if `## Economics` is present / usage-metrics is installed). **Checking the box is the estimate trigger** — don't defer it to a later checkpoint.
2. **Phase-end batching is OK; drift-batching is not.** Planned phases are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** Option comparisons, scope decisions, pivots, corrected assumptions go into the appropriate section **in-flight** — not just in chat.
6. **Estimation provenance (if `## Economics` is present).** `## Economics` follows `.claude/skills/usage-metrics/references/effort-estimation-rubric.md`; the block carries a `method_ref` naming it. Point to the rubric, never copy it.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

**Resume command**: `bash .claude/hooks/task-activate.sh add <SESSION_ID> ben/119`

## Goals

The project console's **Settings → Validation** tab shows the workbench validation at **FAIL** (13 PASS / 3 FAIL, run `run-20260728T071407Z`). This task assesses each failure to root cause and drives the workbench to a **correct** PASS — one where the tools, the tests, the validation design, and the console view are all genuinely right. A PASS obtained by weakening tests, suppressing findings, or hiding cases in `known_anomalies` is out of scope by definition.

Scope (contracts read this session: `workbench-validation/SKILL.md`, `secops/SKILL.md` § audit, `project-console` `setup/loader.py` + `setup/router.py`, the three evidence logs, the manifest):

- Triage TC-08 (tracker), TC-10 (change-control), TC-15 (secops) to root cause; fix at the source (tool, test, or scanner), never at the manifest.
- Close the validation-design gaps the triage exposed (stale baseline, un-capturable model id, dirty-tree run of record, non-hermetic tests, version-pin ambiguity, untested scanner).
- Re-run the full validation at HEAD via **both** invocation paths (CLI and console `POST /setup/workbench/render`), confirm the console tab renders PASS with a current baseline, and prune `known_anomalies` to what is still true.
- Push upstream-owned fixes (tracker, change-control, secops are registry-tracked skills) via `/sync-skills`.

**Progress**: Phase 0 done · Phase 1 fixes 3/3 · Phase 2 (D2–D8) done except the deferred environment-diff persistence · Phase 3: debug run PASS (18/21 + 3 NOT-APPLICABLE, 0 FAIL); run of record + console-invoked run pending on a clean tree · Phase 4 done: PDLC_DEMO PR #182 merged (`2662b4e`), registry PR #301 awaiting review.

## Phase 0 — Ground truth (done 2026-09-08)

| Fact | Value | Why it matters |
|---|---|---|
| Last run of record | `run-20260728T071407Z`, verdict FAIL, 13/16 PASS | The console tab reflects this run |
| Baseline SHA at run | `1e2e6d4`, **working tree dirty**, branch `main` | A dirty-tree run is not a clean configuration baseline |
| HEAD today | `56ed683` | Console `stale` flag is true; project-console moved 1.58.0 → 1.62.0 since |
| `model_id` in baseline | `null` | Runner reads `$CLAUDE_MODEL`, which is never set — the "model change is a revalidation trigger" promise is currently unenforceable |
| Failures reproduce at HEAD? | TC-08 yes · TC-15 yes (14 High, same files) · TC-10 yes in full suite, **passes in isolation** | TC-10 is test-order pollution, not a tool defect |
| Prior triage | All three already in `validation.yml known_anomalies` (2026-07-27) as "upstream fix candidates" | Nothing has been fixed since; anomalies were parked, not driven |

## Phase 1 — Triage to root cause

### TC-08 — tracker (WUN-06 "status shown to the team reflects the real state")

**Symptom.** `test_script_emits_bundle_for_existing_row` → `ERROR: row 'DHF' not found in inventory`.

**Root cause (corrected 2026-09-08 after set comparison — the first read overstated it as "id-scheme drift").** The generator and the dashboard share one row-id scheme: all 152 generator rows are present in `submission-tracker.md`, and the overlay's 132 keys all resolve. The dashboard additionally carries **24 md-only rows** hand-added to the markdown (`AI1…AI6`, `PCCP1…PCCP6`, `PS1…PS5`, `Q4…Q8`, `LMR1/2`). The tracker design handles this: `generate.merge_md_only_rows()` widens the read universe ("if it renders, it can be enriched") and the help/detail builders call it — but **`build-draft-context.py` did not**. Since **all 22 rows that render with a live Create Draft button are md-only rows**, every Create Draft click from the console's create-draft route (`workflows/router.py:_build_draft_context_for_row`) failed with "row not found in inventory". A real wiring defect in production, masked by a test that failed earlier for a different reason: its row-selection regex matched the `DHF` column header of the DHF-roster table.

**Fix (done, tracker 14 → 15).** `build_draft_bundle` now calls `merge_md_only_rows` like its siblings. The test selects draft-eligible rows through `render.parse_markdown` (not a regex), is declared a *project-instance* check per D3 (skips cleanly in a bare checkout), and a second test asserts **every** draft-eligible row builds a bundle. Suite: 12/12 PASS; verified by hand that the console-called script now succeeds for `Q4` and all 21 other button rows.

### TC-10 — change-control (WUN-15 "document transfer is faithful")

**Symptom.** `test_c_jira_renderer_graceful_degrades_on_auth_failure` expects a "cookie bridge failed" warning, gets `HTTP Error 404: Not Found`. 1 of 139 fails; the same test **passes alone** and passes when only `test_v010_bundle.py` runs.

**Root cause — `sys.modules` pollution across test files.** `test_attachments_macro.py:177` installs a fake `lib.attachments` (`extract_confluence_cookies = lambda url: "fake=cookie"`) into `sys.modules` and **never restores it**. Later, `test_v010_bundle.py:229` does `import lib.attachments as attachments_mod`, which resolves through the `lib` package attribute to the **real** module and patches that; but `adopt_helper._expand_jira_macros` does `from lib.attachments import extract_confluence_cookies`, which resolves through `sys.modules` to the **fake**. Result: the fake returns a cookie, the code proceeds to a **live `urlopen` against `https://example.atlassian.net`**, and the 404 is reported instead of the cookie-bridge warning.

**What this says about the tool.** The tool is behaving correctly in both branches (cookie failure → deferred comment; HTTP failure → deferred comment). The defect is entirely in test hygiene — and the validation suite currently **can reach the network**, which makes its evidence non-hermetic.

**Fix plan.** (a) `test_attachments_macro.py`: use pytest `monkeypatch.setitem(sys.modules, ...)` so the fake is restored. (b) `test_v010_bundle.py`: patch via `sys.modules["lib.attachments"]` consistently with how the code under test resolves it. (c) Add a `conftest.py` autouse guard that fails any test opening a socket (no network in validation evidence — Phase 2 D3). (d) Side finding: `change-control/SKILL.md` frontmatter says `version: 0.13.1` while `VERSION` says `0.14.0` — the UUT pin in the evidence log is ambiguous; align them.

### TC-15 — secops (WUN-12 "installed tools pass the security screen")

**Symptom.** `audit_artifacts.py --json` exits 1: 0 Critical / **14 High**. All 14 are false positives in three precision classes:

| Class | Count | Where | Why it fires | Precise fix (not suppression) |
|---|---|---|---|---|
| `CFG-PROJECT-YML` regex `(?:>|>>|tee\b|sed -i|yq -i)\s+…project\.yml` matches the `>` inside `->` in a comment/docstring | 2 | `jira-pull/lib/drift_rules.py:103`, `usage-metrics/scripts/aggregate.py:159` | No redirect-operator context; rule lacks `skip_in_py_string_literals` and any comment awareness | Require a real redirect (`(?<![-=])>{1,2}\s`), set `skip_in_py_string_literals=True`, skip `#` comment text |
| Same rule matches `cat > "$TMP/project.yml"` in a **test fixture** under a temp dir | 11 | `dhf-manifest/tests/test_discovery_index.sh` (11 lines) | Rule can't tell the project's `project.yml` from a same-named fixture under `$TMP` | Downgrade to Medium/informational when the target path is under `$TMP`/`$TMPDIR`/`/tmp`/`mktemp`; keep High for bare `project.yml` |
| `CFG-GIT-CONFIG-GLOBAL` matches a **numbered remediation instruction inside a heredoc** | 1 | `sync-skills/scripts/sync.sh:727` ("1. git config --global core.symlinks true" in a help message) | `skip_in_py_string_literals` exists for `.py` but there is no heredoc/string awareness for `.sh` | Add heredoc-span detection for `sh` files (mirror of the py string-literal skip) |

**Design gap behind the symptoms.** The scanner has **no regression tests** (`secops/tests/` does not exist) and **no disposition mechanism** beyond `suppress_if_path_contains`. A validated security screen needs both: fixtures that prove each rule still catches the real thing after a precision change (the case's own purpose says "the scanner itself fails loudly"), and a documented path to accept a residual false positive with rationale and expiry. Precision fixes first; a disposition file only if precision cannot close it.

## Phase 2 — Validation-design gaps (decisions)

<!-- STRATEGY CONTENT: testing, tool-validation, workbench-validation, evidence-quality -->

### D1 — A FAIL is driven to closure, not parked

**Decision.** `known_anomalies` is for **accepted** residuals with a rationale and an owner, not a holding pen. The three entries dated 2026-07-27 have sat six weeks with no fix; this task closes them at the source and deletes the entries. Going forward, an anomaly entry must name the fix owner and the run by which it is expected to clear.

**Why.** The skill's `run` action already says a FAIL is "a finding to triage (fix the tool, or record the anomaly with rationale)"; in practice the second branch was taken three times and the first never. A report that stays FAIL for weeks with "triaged" annotations tells a reviewer the validation is not being run as a control.

### D2 — Runs of record require a clean tree and a captured model id

**Decision.** A validation run that becomes the run of record must execute on a **clean working tree** at a committed SHA, and the runner must capture the model identifier. Until `$CLAUDE_MODEL` is reliably available, the runner takes `--model-id` explicitly and the report shows "model: not captured" as a visible gap rather than a silent `null`.

**Why.** The last run of record was on a dirty tree with `model_id: null`. Neither the configuration under test nor the model that operated it is reproducible from the record — which defeats the purpose of a configuration baseline and makes the "model change triggers revalidation" rule unenforceable.

### D3 — Validation evidence must be hermetic

**Decision.** A `coverage: tests` case may not depend on the live network, live browser cookies, or **unpinned live project content**. Suites get a socket guard in `conftest.py`; tests that need project data use fixtures or the tool's own inventory API. Where a case deliberately checks a project-instance property (TC-08's "does the dashboard match the inventory?"), it is declared as such in the manifest `approach:` and its dependency on project state is explicit.

**Why.** TC-10 reached `example.atlassian.net` from inside the validation suite; TC-08 depended on the byte layout of a markdown table. Both produce evidence that changes without any tool change, which is the definition of non-repeatable.

### D4 — Precision over suppression in the security screen

**Decision.** False positives in `audit_artifacts.py` are fixed by making the rule more precise (operator context, string/comment/heredoc awareness, temp-path severity downgrade), each precision change paired with a fixture test proving the rule still fires on the real pattern. Path-substring suppression is the last resort.

**Why.** Every suppression widens a blind spot for exactly the file classes (tests, scripts) an attacker would use. Precision keeps the screen honest; fixtures keep the precision from silently eroding.

### D5 — UUT version pins must be unambiguous

**Decision.** The runner records a per-skill version from frontmatter **and** `VERSION` and flags a mismatch in the baseline; the best-practices "changelog current" check already covers the drift, so the fix is to align `change-control` now and have the runner surface the condition.

### D6 — Console tab must show staleness and dirty-tree state, not just the verdict

**Decision.** The Settings → Validation view already computes `stale` (recorded SHA vs HEAD). It should also surface `git_dirty` and `model_id: null` from the baseline so a reader sees a FAIL/PASS in context: "PASS, but on a dirty tree six weeks ago" is not a PASS a reviewer should trust.

### D7 — Three evidence tiers, visible end to end: unit → mocked endpoint → live endpoint

<!-- STRATEGY CONTENT: testing, tool-validation, test-tiers, enterprise-endpoints, mocks -->

**Context.** Several skills need enterprise endpoints (Jira, Confluence via change-control, jira-pull, web-control) that this project never connects to. Today nothing in the test suites or the validation manifest says whether a case exercised a real endpoint, a mock, or nothing — and the one case that accidentally reached the network (TC-10) did so invisibly. Grounding: no pytest markers, `--live` flag, or endpoint env vars exist in any skill's tests; change-control adopts pages via the Atlassian **MCP** (agent-orchestrated) and fetches images/Jira tables via a **REST + cookie bridge** (pure Python); jira-pull's `lib/jira_client.py` wraps an MCP search call; `project.yml` carries `approved_mcps` and `change_control.jira.{cloud_id,base_url}`.

**Decision.** Every test that touches an external system is placed in one of three tiers, and the tier is named the same way in pytest, in the manifest, in the report, and in the console:

| Tier | pytest marker | Endpoint | Hermetic | Runs in validation by default | What it proves |
|---|---|---|---|---|---|
| `unit` | (none — default) | none | yes — socket guard on | yes | Pure logic: ADF→markdown, drift rules, normalizers |
| `mocked` | `@pytest.mark.mocked` | **fake** Jira/Confluence — canned REST/MCP payloads under `<skill>/tests/fixtures/atlassian/`, served by a local fake transport | yes — socket guard on | yes | The real client code paths (pagination, auth failure, graceful degradation, ADF splice) behave correctly against realistic responses |
| `live` | `@pytest.mark.live` | **real** endpoint from `project.yml change_control.jira` + credentials / reachable MCP | no | **only when the deployment declares a connection** | The integration actually works against the enterprise system |

**Manifest contract.** `test_cases[].endpoint: none | mocked | live` (required, no default — a case must say). A manifest-level `connections:` block declares what this deployment has, e.g. `jira: none`, `confluence: none`. A `live` case whose connection is declared `none` is reported **NOT-APPLICABLE — no live connection in this deployment**, not SKIPPED — so the overall verdict is not dragged to PARTIAL by something the project deliberately does not have, while a *declared* connection that is unreachable stays a real SKIP/FAIL. The report's results table and the console's Validation tab gain an **Endpoint** column; each need's verdict states its strongest evidence explicitly ("mock-verified; live not applicable in this deployment").

**MCP-mediated paths cannot be pytest-live.** Where the integration runs through the MCP server, the agent makes the call, not Python. Those paths are validated by **recorded live probes** (scripted transcript + expected outcome, the pattern change-control already used for its eleven v0.6 probes), declared `coverage: exploratory` with `endpoint: live`, and run manually when a connection exists. The report says so rather than implying a scripted PASS — this is the honesty model applied to connectivity.

**Why.** A reviewer reading "change-control 139/139 PASS" today cannot tell that none of it touched Confluence. Naming the tier makes the claim precise: logic proven, integration mocked, live not exercised here. It also makes the hermeticity rule (D3) enforceable — a `unit`/`mocked` test that opens a socket is a defect, a `live` test that does is expected.

**What this commits us to.** (1) A socket guard in each affected skill's `conftest.py` that allows sockets only under the `live` marker. (2) Fixture packs per skill (project-agnostic — skills are registry-tracked; no shared cross-skill fixture root for now). (3) Workbench-validation schema bump (`endpoint`, `connections`, NOT-APPLICABLE verdict) with renderer, sidecar, and console changes. (4) The existing TC-10 test moves to `mocked` with a proper fake, which is the real fix for its network leak.

**Open questions.** Whether a shared fake-Atlassian transport should live in one place (a `testing` helper skill) once two skills carry near-identical fixtures; whether `live` runs, when a connection exists, should write to a separate results folder so a live run never overwrites the hermetic run of record.

### D8 — The test environment is a first-class, expandable section of the validation record

<!-- STRATEGY CONTENT: testing, tool-validation, configuration-baseline, environment-record -->

**Context.** The runner already writes a setup record into every run JSON (`environment:` — git SHA/branch/dirty, Python, platform, operator, `model_id`, `hooks_installed[]`, per-skill `skills{}` versions). But the record is split across three surfaces with decreasing fidelity: the run JSON has everything; the report's § 1 setup-record table shows SHA, counts, operator, host/OS, Python, model; the console tile shows only SHA, skill/hook counts, and operator. A reviewer asking "what exactly did this run execute against?" has to open the JSON. And several things that materially define the environment are **not captured at all**: tool binaries and versions the cases depend on (`uv`, `pytest`, `pyyaml`, `pandoc`, `soffice`, `git`), which `requires:` resolved and which were missing, which env vars were stripped, the harness (Claude Code) version, which MCP servers were configured and reachable, and — once D7 lands — which connection tier each endpoint was in.

**Decision.** The environment record becomes a **complete, structured, expandable section** on every surface, rendered from one canonical block in the run JSON:

| Group | Fields (canonical `environment:` block) |
|---|---|
| Configuration under test | git SHA (full + short), branch, dirty flag **plus the dirty file list**, per-skill version (frontmatter + `VERSION`, mismatch flagged per D5), hooks installed, rules loaded, agents installed |
| Runtime | Python version + executable path, OS/platform, architecture, hostname, OS user, harness version (`claude --version` when available), model id (D2) |
| Tooling | every binary any case `requires:` — resolved path + `--version` output, or **missing** (which is what produced any SKIPPED) — plus the pytest/pyyaml versions `uv` actually resolved |
| Connections (D7) | the manifest `connections:` declaration, MCP servers configured in `project.yml approved_mcps` / settings, and per-endpoint reachability probed at run start (`declared none` / `reachable` / `unreachable`) |
| Isolation | env vars stripped (`env_unset`) and set (`env`) per case; socket guard state (on/off) per tier; working directory |
| Operator + invocation | git user/email, `invoked_via` (cli/console), start/finish, duration, `partial` |

**Surfaces.** Report § 1 keeps the short table and gains a collapsed `<details>` block "Full environment record" with the groups above. The console Validation tab gets an expandable **Environment** panel beside the verdict (collapsed by default, badge shows SHA ± dirty, model, and connection tiers) rendered from the sidecar, which carries the full block rather than the six-field summary it has now. The evidence-log header of every case already carries the per-case slice (cwd, env changes, requires); it gains the resolved binary versions.

**Why.** A validation result is only interpretable together with the environment that produced it — the whole point of a configuration baseline. Today a PASS on a dirty tree with an unknown model and unknown tool versions looks identical to a clean one at a glance. Making the environment expandable keeps the verdict readable while making the record complete for a reviewer, and it turns "re-run needed" from a hunch into a diff: two environment blocks compared field by field.

**What this commits us to.** Runner captures the extra groups (binary probing is cheap; MCP reachability is a bounded probe with a short timeout and never fails the run by itself). Sidecar `schema_version` bump (shared with D7). Renderer emits the `<details>` block. Console template renders the panel; the `stale` check extends from "SHA moved" to "SHA moved **or** any tooling/connection field changed vs the current probe", each shown as a named difference.

**Open questions.** Whether to persist an `environment-diff` between consecutive runs into the results folder so revalidation triggers (model change, skill sync, tool upgrade) are detected mechanically rather than by reading two reports. Whether the harness exposes its version/model to scripts at all (same question as D2).

## Phase 3 — Re-run and verify

1. Full run (never `--only`) from CLI on a clean tree at HEAD: `python3 .claude/skills/workbench-validation/scripts/run_validation.py --root . --render`.
2. Full run from the console (`POST /setup/workbench/render`, `invoked_via: console`) — proves the console path, not just the CLI.
3. Read every evidence log for the three formerly-failing cases; confirm the judgment rule, not just the exit code.
4. Confirm the console tab shows PASS, current SHA, clean tree, captured model id, and no `partial`.
5. Prune `known_anomalies`: delete the three fixed entries; re-examine the remaining four (inert frozen-doc hook, untested checkers, exit-code masking, env sensitivity) and either drive or re-accept each with owner + expected clearing run.

## Phase 4 — Close-out

- `/sync-skills push` for tracker, change-control, secops, workbench-validation, project-console changes (registry-tracked).
- Validation plan: add the hermeticity and clean-tree criteria; refresh revalidation triggers.
- Commit → PR → merge per `git-workflow.md`; record SHAs here.
- Lessons harvested; index updated; task marked Complete.

## Todos

### Phase 1 — fixes at the source
- [x] TC-08a: `build-draft-context.py` — merge md-only rows like the help/detail builders (the real defect; no regeneration of the dashboard was needed — the id schemes already agree)
- [x] TC-08b: test selects draft-eligible rows via `render.parse_markdown`; new test asserts every button row resolves; tracker 14→15 + README changelog
- [x] TC-10a: `test_attachments_macro.py` — restore `sys.modules` via `monkeypatch.setitem`
- [x] TC-10b: `test_v010_bundle.py` — patch through `sys.modules["lib.attachments"]`
- [x] TC-10c: `change-control/tests/conftest.py` — autouse socket guard (no network); `mocked`/`live` markers + `--live`
- [x] TC-10d: `change-control` SKILL.md + VERSION both `0.14.1`; README changelog row
- [x] TC-15a: shared `_EDIT_OP` operator fragment (no `->`/`=>`), `skip_in_comments`, `skip_in_string_literals` (py tokens + sh heredocs) on all `CFG-*` rules
- [x] TC-15b: `downgrade_if_temp_target` → Medium, with transitive `VAR=$(mktemp…)` resolution; 16 Medium fixture writes remain visible (11 dhf-manifest + 5 sync-skills — the latter previously **missed** by the loose pattern)
- [x] TC-15c: heredoc-aware skip for `sh` (plain / `<<-` / quoted terminators)
- [x] TC-15d: `secops/tests/test_audit_rules.py` — 30 cases (positives incl. `>project.yml` no-space, `sed -i`, `tee`, `yq -i`, top-level `git config --global`, curl-pipe Critical; negatives for comments/docstrings/heredocs/temp paths; exit-code contract). Audit now 0 High / 16 Medium, exit 0. secops 8→9

### Phase 2 — validation design
- [x] D2: runner `--model-id`; `warnings[]` (dirty tree, model uncaptured, pin mismatch, tier-less case) to stderr + run JSON + report banner + console banner
- [x] D5: runner records both + `version_mismatch`; found and aligned `digest` (VERSION 1.3.0→9) and `submissions` (VERSION 6→10); `change-control` aligned by fork
- [x] D6: console tiles show dirty tree + model/harness; stale banner lists named differences (commit, per-skill version changes, hooks added/removed); warnings banner
- [x] D3: TC-08 test docstring + tracker changelog declare the project-instance check; hermeticity rule in plan §7
- [x] Validation plan §6 rewritten (environment record, run-of-record rule, triggers) + new §7 evidence tiers
- [x] `known_anomalies`: three fixed entries deleted; four re-dispositioned with owner + clearing run; two new accepted residuals (model id depends on operator; live cases NOT-APPLICABLE by declaration)

### Phase 2b — evidence tiers (D7)
- [x] change-control + jira-pull + web-control `conftest.py`: `mocked`/`live` markers, socket guard, `--live` (identical design, per-skill testkits)
- [x] change-control: `tests/fakes.py` fake urlopen + cookie bridge, `tests/fixtures/atlassian/` (2-issue, empty, 401), `test_jira_mocked.py` (4 mocked + 1 live smoke, skips "no live connection configured"); Jira-renderer + attachments tests marked `mocked`. Suite 143 passed / 1 skipped, order-independent
- [x] jira-pull: `merge_pages()` pure seam extracted from `refresh.py`; fixtures (page1/page2/empty/wrapped); 17 mocked tests + 1 live placeholder; suite now collects under pytest (86 passed) — jira-pull 1→2. web-control: 14 unit tests + live placeholder, 0.3.0→0.3.1
- [x] workbench-validation 3→4: `endpoint:` + `connections:`; NOT-APPLICABLE status/verdict; Endpoint column; `strongest_evidence` per need; schema 1.1; template + SKILL + README updated
- [x] project-console 1.64.0: Endpoint column, `n/a here` badges, per-need evidence line, tier/connections tile
- [x] validation.yml: `connections: {jira, confluence, browser: none}`; `endpoint:` on all cases; TC-17/18/21 live (NOT-APPLICABLE here), TC-19 scanner suite, TC-20 web-control unit; WUN-16 exploratory need for MCP-mediated paths
- [x] validation-plan.md §7

### Phase 2c — environment record (D8)
- [x] runner captures dirty file list, agents/rules, harness version (captured: Claude Code CLI version string), binary probes, uv-resolved pytest/pyyaml, MCP servers approved/configured, per-connection reachability, isolation block
- [x] run JSON + sidecar schema 1.1: full `environment` block (the `baseline` summary kept for compatibility, extended with model_captured/harness/mismatches)
- [x] renderer §1 `<details>` full environment record; evidence-log headers carry `endpoint:` + resolved tooling versions
- [x] console expandable Environment panel (badge: commit ± dirty count · model · python/arch · connection tiers); stale = named differences
- [ ] decide: persist `environment-diff` between consecutive runs — deferred; the console now computes the live diff on view, which covers the reviewer need; a persisted diff is a follow-up if audit wants it in the record

### Phase 3 — re-run
- [x] Full CLI run of record `run-20260908T180259Z` on a clean worktree at `8f266ff`, model captured, no warnings → PASS 18/21 + 3 NOT-APPLICABLE
- [x] Console-invoked run of record `run-20260908T180329Z` via `POST /setup/workbench/render` with model id → PASS; `/setup` renders the new panel/columns

### Phase 4 — close-out
- [x] `/sync-skills push` (PR-only, per the contract default): hitachi PR #301 (`f72dedb`) — 46 files, all LOCAL_ONLY/LOCAL_AHEAD; project-console excluded (diverged fork, manual port needed) and `tracker/scripts/render.py` excluded (BOTH_DIVERGED, untouched). Drift returns to 0 once #301 merges and is pulled
- [x] Commits `8f266ff` (fixes + design) · `f79e6bc` (cli run of record) · `bea9269` (console run of record) → PR #182 merged to `main` as `2662b4e`

## Open questions

- Which tracker row-id scheme is canonical (`Q4` in the committed markdown vs `Q-PC1` from the generator)? Needs `tracker/SKILL.md` § render + `project.yml tracker:` read before deciding — do not guess.
- Does the harness ever export a model identifier to hooks/scripts? If not, D2's `--model-id` stays manual and the plan must say so.
- Should the temp-path `project.yml` fixture writes be Medium (visible) or Low? Leaning Medium so they stay on the report without failing the gate.

<!-- LESSONS LEARNED: validation, process -->
- **A fixed head window is a silent lie in a version scan.** Reading `SKILL.md[:2000]` for `version:` dropped the pin for any skill with a long description — and long descriptions are what the skill-creator asks for. The runner recorded an empty UUT version for a case for six weeks and nothing complained. Parse the fenced frontmatter block; never a byte window.
- **Re-running the validation is itself a detector.** Two regressions (a test that never learned a later design rule; the head-window bug) were invisible until the suite ran again after the workbench moved. A validation that is not re-run on every skill change is not a control.
- **A hostile literal in a test fixture is itself a finding.** The secops regression test that proves `curl … | sh` is caught tripped the scanner when the repo was scanned; the fix is to assemble the literal at runtime, not to suppress the test path. Applies to any scanner whose test suite lives inside the tree it scans.
- **"Triaged" is not "closed".** All three FAILs were annotated as upstream fix candidates on 2026-07-27 and then left for six weeks; the report stayed FAIL and nobody was driving it. An anomaly entry without an owner and an expected clearing run is a parking ticket, not a disposition.
- **A test failing for the wrong reason can hide a real finding.** TC-08's regex bug masked a genuine dashboard-vs-inventory drift; fixing only the regex would have produced a PASS on a still-wrong dashboard. Always reproduce the underlying tool call by hand (`build-draft-context.py --row Q4`) before fixing the test.
- **Order-dependent test failures point at global state.** "Passes alone, fails in the suite" resolved in minutes once `sys.modules` was checked; the six-week-old anomaly note said only "does not behave as the test expects in this environment".

## Economics

_By-hand person-hour estimate, **filled at checkpoint** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated; an empty `todos` list is ignored by the aggregator._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": null,
    "todos": [
      {"id": "TC-08", "title": "Tracker Create Draft wiring: root cause via row-set comparison, merge fix, test rework, version/changelog", "hours_low": 3, "hours_high": 6, "persona": "senior-engineer"},
      {"id": "TC-10", "title": "change-control: sys.modules pollution root cause, order-independent patching, socket guard + tiers, fake Atlassian transport + fixtures + 5 tests, version alignment", "hours_low": 5, "hours_high": 9, "persona": "senior-engineer"},
      {"id": "TC-15", "title": "secops: rule precision (operator context, comment/string/heredoc awareness, temp-path downgrade) + 30-case regression suite + docs", "hours_low": 6, "hours_high": 10, "persona": "senior-engineer"},
      {"id": "D2-D8", "title": "workbench-validation 4 + project-console 1.64.0: endpoint tiers, connections, NOT-APPLICABLE, strongest-evidence, full environment record (runner/renderer/sidecar/report/console), plan §6-7, manifest 21 cases + WUN-16, anomaly re-disposition", "hours_low": 14, "hours_high": 24, "persona": "senior-engineer"},
      {"id": "D7-tiers", "title": "jira-pull + web-control tiers: conftests, testkits, merge_pages seam, fixtures, 31 new tests", "hours_low": 5, "hours_high": 8, "persona": "senior-engineer"},
      {"id": "regressions", "title": "Two new regressions found by the re-run and fixed: frontmatter head-window bug (sweep + runner), console catalog test vs task-116 curation rule; two more pin mismatches aligned", "hours_low": 2, "hours_high": 4, "persona": "senior-engineer"}
    ]
  }
}
```

## Changelog

- 2026-09-08: Task created. Phase 0 ground truth and Phase 1 root-cause triage completed from the evidence logs at `tools/workbench-validation/results/run-20260728T071407Z/` and live reproduction at HEAD `56ed683`: TC-08 = loose test regex **plus** real dashboard/inventory drift (markdown ids `Q4…` vs generator `Q-PC1…`); TC-10 = `sys.modules` pollution from `test_attachments_macro.py:177` causing a live HTTP call; TC-15 = 14 scanner false positives in three precision classes, scanner has no tests. Six design decisions (D1–D6) recorded. No fixes applied yet.
- 2026-09-08: D7 recorded — three evidence tiers (unit / mocked / live) named identically in pytest markers, the manifest (`endpoint:` + `connections:`), the report, and the console; MCP-mediated paths validated by recorded live probes (`exploratory`), never a scripted PASS. Phase 2b todos added. Progress line unchanged (no fixes yet).
- 2026-09-08: D8 recorded — environment record becomes a complete, expandable section on report + console, rendered from one canonical block in the run JSON; new captures (tool binaries/versions, MCP reachability, harness version, dirty file list, isolation state). Phase 2c todos added.
- 2026-09-08: TC-08 fixed at the source — `tracker/scripts/build-draft-context.py` now merges md-only rows (all 22 Create-Draft rows were md-only and failed in production); test reworked (parser-based selection + all-rows check); tracker 14→15. Finding corrected: not id-scheme drift, a missing merge call. Forks running for change-control (TC-10 + D7 tiers), secops (TC-15 precision + tests), jira-pull/web-control (D7 tiers).
- 2026-09-08: TC-10 fixed + change-control D7 tiers landed (0.14.1): `tests/conftest.py` markers/guard/`--live`, `tests/fakes.py`, `tests/fixtures/atlassian/`, `test_jira_mocked.py`; 143 passed / 1 live-skipped; guard never trips. Note: `project.yml` has no `change_control` block → manifest `connections:` will declare jira/confluence `none`.
- 2026-09-08: TC-15 fixed at the source (secops 9): 14 High → 0 High / 16 Medium, exit 0; 30 scanner tests. Lesson: a hostile literal inside a test fixture trips the scanner on the repo itself — assemble it at runtime, don't suppress the path. Phase 1 complete (3/3). Runner patched for D2/D5/D7/D8 (schema 1.1: `--model-id`, dirty-file list, version-mismatch flag, tooling/connection probes, `endpoint:` tiers + NOT-APPLICABLE); renderer next.
- 2026-09-08: D2/D5/D6/D7/D8 implemented — workbench-validation 4 (schema 1.1), project-console 1.64.0, manifest 21 cases / 16 needs, plan §6–7. Debug run `run-20260908T175939Z`: **PASS**, 18/21 + 3 NOT-APPLICABLE, 0 FAIL. The re-run also surfaced two regressions the July run predated, both fixed at the source: (a) `writing-well` reported "no version" because both the TC-16 sweep and the runner's own version scan read a fixed 2000-char head window that a long frontmatter description overran — the runner had been recording an **empty UUT pin** for writing-well (TC-05) since July; both now parse the fenced frontmatter block; (b) project-console `test_setup_cli_catalog` never learned the task-116 curation rule (customer-gated `jama-connect` ships a blank editable url + note) — test updated. Version-pin mismatches found by the new environment record and aligned: digest (VERSION 1.3.0→9), submissions (6→10). Settings page renders through the app (`/setup` 200; panel, badges, columns present). Next: commit on a branch, run of record in a clean worktree (CLI + console-invoked), commit results, sync upstream, PR.
- 2026-09-08: Landed on `main` via PR #182 (`2662b4e`): `8f266ff` fixes + D2–D8, `f79e6bc` cli run of record, `bea9269` console-invoked run of record — both clean-tree, model captured, no warnings, PASS 18/21 + 3 NOT-APPLICABLE. Remaining: `/sync-skills push` (PR-only) for the touched registry skills, index refresh, checkpoint.
- 2026-09-08: Registry push — hitachi PR #301 (`f72dedb`), PR-only, 46 files; sync-log entry recorded. project-console 1.64.0 not pushed (the forks have diverged; the Settings → Validation changes need a manual port — follow-up). Task marked Complete; open follow-ups: merge #301 then `/sync-skills pull`; port console changes to the registry fork; decide on persisting an environment-diff between runs; the seven earlier uncheckpointed tasks (111–117) still carry markers.

## Resume / follow-up

Everything is on `main`. To pick up the follow-ups: `bash .claude/hooks/task-activate.sh add <SESSION_ID> ben/119`, then (1) after hitachi #301 merges, `/sync-skills pull` and confirm drift 0; (2) port project-console 1.64.0 Settings → Validation changes to the registry fork; (3) re-run `/workbench-validation validate --model-id <model>` after any skill change — the Settings → Validation tab now lists named differences when the recorded environment no longer matches the checkout.
