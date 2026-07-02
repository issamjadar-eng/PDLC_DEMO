# 045 — Trace Matrix View Breakage — Analysis & Recovery Plan

**ID**: 045
**Created**: 2026-05-05
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
2. **Phase-end batching is OK; drift-batching is not.** Planned phases are a legitimate checkpoint — write at the boundary, before the next phase starts. Don't accumulate updates in your head.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative.
4. **Resume-ready before any session boundary.** Doc must contain: (a) what was done with concrete artifacts, (b) status of in-flight work, (c) priority-ordered next steps, (d) open questions, (e) the exact `/task` activation command.
5. **Capture strategy + lessons as they happen.** Use `<!-- STRATEGY CONTENT: ... -->` and `<!-- LESSONS LEARNED: ... -->` blocks in real time.

Resume command:
```bash
bash .claude/hooks/task-activate.sh add <SESSION_UUID> 045
```

---

## Goals

The `/trace-matrix` view in the project-console dashboard is broken following a wave of skill updates. This task **analyzes the root cause** and **proposes a remediation plan** before any code changes land.

- Identify which recent skill / console / project-yml change(s) broke the Trace Matrix view (originally shipped in task 016).
- Map the contract surface between `trace-matrix` skill (producer) and `project-console` (consumer): JSON sidecar shape, file paths, route handlers, templates, static assets.
- Determine whether the breakage is in the producer (skill build output) or the consumer (console rendering) — or both.
- Produce a prioritized remediation plan with concrete file paths and verification steps; **do not implement** until the user signs off.

## Context

**The Trace Matrix view originally worked.** Task 016 (In Progress, High) shipped v1: skill emits `trace-matrix.md` + `trace-matrix.json` per DHF; `/trace-matrix` console section reads sidecars, renders layered UN ↔ DI ↔ Architecture ↔ V&V view with criticality / layer / orphan filters, plus inline Rebuild / Build-this-DHF buttons.

**Recent skill activity that could plausibly have broken it:**

| Task | Skill / Area | Risk to trace-matrix view |
|------|--------------|---------------------------|
| 030 | Sync-Skills Pull 2026-04-27 (project-console 1.4.1 → 1.7.6, plus 6 new skills incl. dhf-manifest, web-control, docx/pdf/pptx/xlsx; task v23; secops v5; digest v8) | **High** — bulk console upgrade across 4 minors. Likely culprit. |
| 031 | Console relative-link rewriter (renderer.py post-pass) + extra grounding roots in `console.yaml` | **Medium** — touches `renderer.py`; could have side-effected the trace-matrix template's anchors / data-* attributes. |
| 033 | dhf-manifest output filename parameterization (project-slug prefix) | **Medium** — if trace-matrix sidecar was renamed analogously, the console loader may be looking for the old path. |
| 035 | DHF Manifest Pipeline bring-up — added `leaf` / `role` / `classification` / `composes` + project-level `scope:` block to `project.yml` `dhfs[]` schema | **Medium** — if the trace-matrix loader keys off `dhfs[]` entries, the new required fields could be filtering DHFs out. |
| 042 | md-deck ↔ frontend-slides shared layer | Low — unrelated CSS lineage. |
| 043 | (Per recent commits) consolidate buttons / `/overview` redesign | **Medium** — touches console UI shell + base template; could have broken header / nav / shared sidebar that `/trace-matrix` extends. |
| 044 | tracker console redesign recovery | **Medium** — the active git status shows tracker skill churn (`scripts/generate.py`, `render.py`, new `taxonomy.py`, etc.); if shared console infra was refactored for tracker, trace-matrix may share that infra. |

The `submission-tracker.html` work in the git status (uncommitted) is the most recent surface area — if a shared dashboard scaffold was modified, trace-matrix could be collateral damage.

## Plan of Investigation

Phased — phase 1 produces evidence, phase 2 produces the remediation plan, phase 3 (gated on user approval) is execution.

### Phase 1 — Evidence gathering (read-only)

- [ ] **1a — Reproduce the failure.** Start the project-console (`/project-console start`), load `/trace-matrix`, capture exactly how it fails (blank page, 500, missing data, broken filters, JS error). Record the failure mode in this doc — without it the rest is guesswork.
- [ ] **1b — Locate the consumer code.** Find the `/trace-matrix` route handler, template, and static JS in `tools/project-console/`. Note their last-modified commits (`git log --follow`).
- [ ] **1c — Locate the producer output.** Find the trace-matrix sidecar JSON files emitted into the DHF tree. Confirm they exist, are recent, and parse as valid JSON. Compare current schema against what the consumer expects.
- [ ] **1d — Diff the consumer over the suspect window.** `git log` the project-console trace-matrix files since just before task 030 (~2026-04-26). Single-author diffs are cheap; this is the highest-yield search.
- [ ] **1e — Diff the producer over the suspect window.** Same for `.claude/skills/trace-matrix/`. Was the JSON shape changed upstream during bulk pull?
- [ ] **1f — Check `project.yml` dhfs[] entries** for the new required fields (ben/035) and confirm whether the trace-matrix loader tolerates DHFs missing them.
- [ ] **1g — Browser console check.** With the page loaded, list JS console errors and failed network requests via chrome-devtools MCP — distinguishes server-side render failure from client-side hydration / fetch failure.

### Phase 2 — Synthesis & remediation plan

- [ ] **2a — Categorize the root cause** as one of: (i) producer schema drift, (ii) consumer template/route regression, (iii) config/path mismatch, (iv) shared-infra breakage from tracker / overview redesign, (v) multiple.
- [ ] **2b — Author the fix plan** in this doc — file-path-level, with ordering and verification steps. Sister-project (`../arthrex-pccp/`) compatibility check included per repeated guidance.
- [ ] **2c — Decide upstream-vs-local.** Is the fix a local console patch, a skill bug to push upstream to `hitachi`, or both?
- [ ] **2d — Present plan to user, await sign-off** before any edits.

### Phase 3 — Execution (gated)

- [ ] **3a — Apply the fix** under user direction.
- [ ] **3b — Verify in browser** end-to-end against PP3500 DHF.
- [ ] **3c — Validate against sister project** (`../arthrex-pccp/`) per standing rule.
- [ ] **3d — Commit + (if applicable) `/sync-skills push` upstream.**

## Todos

### Phase 1 — Forensics ✅
- [x] 1a — Failure mode: silent empty-state at `/trace-matrix` (not HTTP 500)
- [x] 1b — Consumer code located (`loader.py:38-39, 94`; `router.py:91-298, 403-414`)
- [x] 1c — Producer output schema validated (v1.1; matches consumer expectations exactly)
- [x] 1d — Diffed console since 2026-04-26 — only relevant change is `f5affee` (path rename)
- [x] 1e — Diffed trace-matrix skill — symmetric path rename, no schema drift
- [x] 1f — `project.yml dhfs[]` schema OK (loader handles new `leaf`/`role`/`classification` fields)
- [x] 1g — Browser console check skipped (root cause already identified at code level)

### Phase 1b — Pipeline reconstruction ✅
- [x] Mapped 5-step build chain (sources → trace-matrix.yml → adapters → build.py → console loader)
- [x] Ruled out `jira-pull`, `dhf-manifest`, `tracker`/`.taxonomy.yml`, `renderer.py` as upstream deps for pca-device
- [x] Re-read SKILL.md end-to-end and identified `/trace-matrix init` IoC pattern as the prescribed fix

### Phase 2 — Remediation (in progress, RESUME HERE)
- [x] 2a — Root cause: (iii) config/path mismatch — `f5affee` rename + stale `output_dir` in yml + structural bug in old yml (`risk:` and `output_dir:` dedented out of `layers:`)
- [x] 2b — Fix plan: `/trace-matrix init` (skill-prescribed, IoC) instead of hand-edit
- [x] 2c — Local fix only (skill code is correct post-`f5affee`; project artifacts need rebuild). No upstream push.
- [x] 2d — Plan presented, user signed off on full unscoped init + pause-checkpoint between step 4 and step 5

### Phase 3 — Execution (in progress)
- [x] 3.0 — Backups created (see "Files in flight" below)
- [x] 3.1 — Step 1: `project.yml dhfs[]` enumerated (9 DHFs)
- [x] 3.2 — Step 2: fresh `trace-matrix.yml` written at repo root (all 9 DHFs, no `output_dir` override, structural bug fixed)
- [x] 3.3 — Step 3: `analyze.py` ran clean — verdicts captured at `/tmp/tm-analyze.json` (NOT preserved across sessions; re-run to refresh)
- [ ] **3.4 — Step 4 DECISION PENDING (user input required) — see "Decision points" below**
- [ ] 3.5 — Step 5: `python3 .claude/skills/trace-matrix/scripts/build.py --repo . --dhf pca-device` (or omit `--dhf` for all 9)
- [ ] 3.6 — Verify in browser at `/trace-matrix/pca-device` — confirm empty-state replaced with populated layered view (22 UNs, 34 DIs, 7 modules, V&V derived, risk source_empty)
- [ ] 3.7 — Diff new sidecar against `trace-matrix.json.baseline-016` for semantic continuity
- [ ] 3.8 — Sister-project (`../arthrex-pccp/`) compatibility note in sync-log
- [ ] 3.9 — Commit (decide branch policy first — see Open Question #4)

### Phase 4 — Follow-up tasks (out of scope; spin off)
- [ ] 4a — **Architecture parser gap.** Defaults parse 0 nodes from `connectivity-adapter-system-sad.md` and `drug-library-manager-system-sad.md` despite both being non-empty. Project adapter generation is non-trivial because adapters key by **layer not by DHF** — a project `architecture.py` must continue producing 7 nodes for pca-device while also handling the other 2 SAD shapes. Spin off as a dedicated task.
- [ ] 4b — **Source-content authoring.** 7 of 9 DHFs have no UN / no DI / no risk content. Adapter generation cannot fix this — content authoring task, not parser task.
- [ ] 4c — **Filing-entity + system architecture gap → spun off as ben/046.** During Step-4 decision review the user identified that the project is missing the top-level **PCA Infusion System** filing entity (the device of record for the 510(k)). The single system SAD has no home; the per-DHF "*-system-sad.md" docs are scope-mislabeled (they are component-level **software** SADs). Multi-function device regulatory strategy also needs authoring/update for the 3 classifications (Medical Device / MDDS / non-medical). Captured at `tasks/ben/046-pca-infusion-system-architecture-gap.md`. ben/045 stays surgical (restore trace-matrix view against existing DHF set); 046 owns the structural restructuring.

## Files in flight (RESUME-CRITICAL)

### Backups created 2026-05-05 (do NOT delete on resume)
- `/Users/ben.xavier/Documents/demos/pdlc_demo/trace-matrix.yml.backup-2026-05-05` — original yml (had structural bug + stale `output_dir`)
- `/Users/ben.xavier/Documents/demos/pdlc_demo/docs/project/dhfs/pca-device/design-controls/trace-matrix/trace-matrix.json.baseline-016` — 83 KB sidecar from ben/016 (Apr 14 build) — keep as semantic-continuity reference
- `/Users/ben.xavier/Documents/demos/pdlc_demo/docs/project/dhfs/pca-device/design-controls/trace-matrix/trace-matrix.md.baseline-016` — companion markdown

### Files modified this session
- `/Users/ben.xavier/Documents/demos/pdlc_demo/trace-matrix.yml` — **rewritten clean**, all 9 DHFs at conventional source paths, no `output_dir` override, structural bug fixed
- `/Users/ben.xavier/Documents/demos/pdlc_demo/CLAUDE.md` — added "Read the skill before synthesizing a plan around it" rule under § For Claude
- `/Users/ben.xavier/.claude/projects/-Users-ben-xavier-Documents-demos-pdlc-demo/memory/feedback_read_skill_before_planning.md` — new feedback memory + index entry in `MEMORY.md`

### Files NOT yet created (will be produced by step 3.5 build)
- `docs/project/console/pca-device/console_trace_matrix.json` — the file the console loader looks for (currently absent → empty-state UI)
- `docs/project/console/pca-device/console_trace_matrix.md`
- (Plus equivalent pairs for the other 8 DHFs if build runs unscoped — most will be sparse / source_empty)

## Resume command (paste into a fresh session)

```bash
bash .claude/hooks/task-activate.sh add <SESSION_UUID> 045
```

(Where `<SESSION_UUID>` comes from `printenv CLAUDE_SESSION_ID` or the task-gate denial message — see CLAUDE.md.)

### What to do first on resume (priority-ordered)

1. **Re-read this doc end-to-end** — especially "Files in flight" and "Decision points" — and confirm the 3 backup files still exist on disk:
   - `trace-matrix.yml.backup-2026-05-05`
   - `docs/project/dhfs/pca-device/design-controls/trace-matrix/trace-matrix.json.baseline-016`
   - `docs/project/dhfs/pca-device/design-controls/trace-matrix/trace-matrix.md.baseline-016`
2. **Re-run** `python3 .claude/skills/trace-matrix/scripts/analyze.py --repo . --json > /tmp/tm-analyze.json` to refresh the analyze snapshot (lost across sessions). Confirm pca-device still 22 UN / 34 DI / 7 modules.
3. **Open ben/046** (`tasks/ben/046-pca-infusion-system-architecture-gap.md`) and skim — its existence affects Decision 1 + Decision 2 (see notes below in "Decision points").
4. **Re-present the 3 decisions to the user** with current recommendations:
   - D1: defer adapter generation (now reinforced by ben/046's pending file renames)
   - D2: build pca-device only (now reinforced — building 9 will need redoing post-046)
   - D3: branch policy — uncommitted tracker work in git status must still be addressed
5. **On user sign-off,** run `python3 .claude/skills/trace-matrix/scripts/build.py --repo . --dhf pca-device` (Step 3.5).
6. **Verify in browser** at `/trace-matrix/pca-device` (Step 3.6).
7. **Diff** new sidecar against `trace-matrix.json.baseline-016` (Step 3.7).
8. **Sister-project + commit** (Steps 3.8, 3.9).

## Decision points (USER INPUT REQUIRED before step 3.5)

### Decision 1 — Step 4 adapter generation: defer or do now?

**Current recommendation: defer to follow-up task 4a.**

Two layers parse 0 nodes from non-empty SAD docs (connectivity-adapter, drug-library-manager). SKILL.md `init` step 4 says generate a project adapter for these. **But:**

- Project adapters key by `<layer>.py`, not `<dhf>-<layer>.py` → one architecture.py would override the default for ALL 9 DHFs
- pca-device's architecture currently parses 7 nodes correctly on the default; any project adapter must preserve that
- The 2 affected DHFs have NO UN / NO DI / NO risk → even if architecture parsed, the trace graph has nothing to connect to
- Generating a project adapter that handles 3 distinct SAD shapes deserves its own task with proper review
- **NEW (2026-05-06):** the 2 affected SAD files are exactly the ones ben/046 will rename / relocate (they're misnamed component software SADs, not system SADs). An adapter written now would need to be redone after 046's restructure. Strong argument for deferring until ben/046 settles the file shapes.

**Open question: defer (recommended), or generate now?**

### Decision 2 — Step 5 build scope: all 9 DHFs or just pca-device?

- All 9: full project portrait, but 7 of 8 non-pca DHFs render mostly empty (cosmetic noise in console index)
- pca-device only: surgical, restores the broken view, leaves other DHFs blank (which they currently are anyway)
- **NEW (2026-05-06):** ben/046 will add a 10th DHF (`pca-infusion-system`) and may re-parent / rename existing ones. Building all 9 now means rebuilding all 10+ later. Reinforces the "pca-device only" option as the cheapest restore.

**Open question: scope the rebuild?**

### Decision 3 — Branch policy

Uncommitted tracker work in git status (`tracker/scripts/generate.py`, `submission-tracker.html`, taxonomy files). Trace-matrix recovery should land:

- (a) on `main` alongside the tracker work (one commit, mixed scope), or
- (b) clean branch (stash tracker work first), or
- (c) commit trace-matrix recovery first (separable scope: only `trace-matrix.yml` + new `docs/project/console/pca-device/*` files), then return to tracker

**Open question: branch policy?**

## Snapshot of analyze.py output (for resume context)

`pca-device` is fully OK on defaults — confirms the rebuild will produce a valid sidecar:

| Layer | Nodes | OK | Adapter |
|-------|-------|----|---------|
| user_needs | 22 | ✓ | default |
| design_inputs | 34 | ✓ | default |
| architecture | 7 (M1–M7) | ✓ | default |
| vnv | derived | ✓ | default (DI verification column) |
| risk | 0 | ✓ (source_empty placeholder — known content gap) | default |

Other DHFs almost entirely `source_empty`; 2 architecture parser failures (see Decision 1).

To regenerate analyze output on resume:
```bash
python3 .claude/skills/trace-matrix/scripts/analyze.py --repo . --json > /tmp/tm-analyze.json
```

## Open Questions

1. Has the user already seen the failure mode, or do we need to reproduce it from scratch? (Affects Phase 1a urgency.)
2. Does the user want the fix landed on the current branch alongside the in-flight tracker work (uncommitted in git status), or on a clean branch?
3. Is the broken view blocking demo prep, or is this triage in slow time?

## Strategy & Lessons (real-time capture)

<!-- STRATEGY CONTENT: development, incident-triage -->
**Decision:** Treat this as a triage task with a hard read-only Phase 1, not a "fix it now" task. Reason: skill bulk-pulls (ben/030) and overlapping in-flight work (ben/043 overview, ben/044 tracker, uncommitted tracker churn in git status) make the suspect window wide. Diagnosing first is cheaper than guessing — and the user explicitly asked for analysis + plan, not a fix.
**How to apply:** Don't edit any console / skill code in this task before Phase 2d sign-off. The investigation output (root cause + file-path-level plan) is the deliverable of phases 1–2.
<!-- /STRATEGY CONTENT -->

## Phase 1 — Findings (2026-05-05, read-only forensics)

### Root cause (high confidence ~85%)

**Path-rename without sidecar regeneration.** The `ben/035` sync-skills pull (commit `f5affee`, 2026-04-27) renamed the trace-matrix sidecar contract on both sides:

| | Old path (baseline-016, commit `487879d`) | New path (post `f5affee`) |
|--|--|--|
| Consumer expects | `docs/project/dhfs/<leaf>/design-controls/trace-matrix/trace-matrix.json` | `docs/project/console/<leaf>/console_trace_matrix.json` |
| Producer default writes | same | `docs/project/console/<leaf>/console_trace_matrix.json` |

But:
1. `docs/project/console/` **does not exist** — no rebuild has run since the rename.
2. The pre-existing 83 KB sidecar still sits at the OLD path (mtime Apr 14, baseline-016 build).
3. The repo-root `trace-matrix.yml` still pins `output_dir: docs/project/dhfs/pca-device/design-controls/trace-matrix` — so even pressing **Build this DHF now** in the console would write back to the OLD location and the view would still be empty.

**User-visible symptom:** `/trace-matrix` index lists every DHF as "no sidecar" empty-state. `/trace-matrix/pca-device` shows the "Initialize with Claude / Build this DHF" panel. **Silent breakage, not an HTTP 500** — templates defend against `sidecar is None`.

### Evidence (file:line citations)

- Consumer path constants: `.claude/skills/project-console/console/trace_matrix/loader.py:38-39`, assembled at `loader.py:94`.
- Producer default output: `.claude/skills/trace-matrix/scripts/build.py:269-272`, written at `build.py:306-307`.
- Schema match (consumer ↔ producer): both use `version: 1.1`, `layers[].items[]`, `traces_forward/_reverse`, `gaps.orphans`, `stats`, `source_files` — `emit.py:23-77` ↔ `router.py:91-298`. **No schema drift.**
- Sidecar files on disk: only the OLD-path file at `docs/project/dhfs/pca-device/design-controls/trace-matrix/trace-matrix.json`; `find docs -name 'console_trace_matrix*'` → zero results.
- Path rename commit: `f5affee` (ben/035 sync pull, 2026-04-27) — only loader change in suspect window.
- `project.yml` `dhfs[]` schema additions (ben/035 `leaf`/`role`/`classification`/`composes`) — loader handles them correctly via `_resolve_dhf_root` (`loader.py:42-66`). **Not a contributor.**
- Templates fine: `trace_matrix_index.html` + `trace_matrix_view.html` both extend `_base.html`; only reference context vars the router always sets. ben/043 overview + ben/044 tracker churn do **not** touch any template the trace-matrix view inherits from.
- `console.yaml` diff: only adds a tracker-candidate dashboard pattern. Unrelated.
- `project.yml` diff: cosmetic (comments stripped, list formatting). No fields the trace-matrix loader reads were removed.

### Causes ruled out

- ben/031 link-rewriter — touches `renderer.py` only; trace-matrix view does not flow through it.
- ben/033 dhf-manifest filename slug — only affects manifest outputs, not trace-matrix.
- ben/043 overview redesign — touches `index.html`/`overview.html`, not `_base.html` or trace-matrix templates.
- ben/044 tracker recovery — orthogonal scaffold.
- Schema drift between producer + consumer — keys match exactly.
- Template / context-var regression — none.

## Phase 1b — Pipeline reconstruction (backwards trace, 2026-05-05)

The user asked for the full multi-skill chain that produces what the console reads. Map below.

### Canonical build graph for `pca-device`

```
[Step 1: source docs (hand-authored under medtech-docs scaffold)]
       │                    [Step 2: trace-matrix.yml (per-DHF source map)]
       └──────────┬─────────────────────┘
                  ▼
       [Step 3: project adapters (optional, none today)]
                  ▼
       [Step 4: build.py → console_trace_matrix.{json,md}]
                  ▼
       [Step 5: console loader.py reads sidecar → /trace-matrix view]
```

| Step | Artifact | Producer | Inputs | Pre-existing? |
|------|----------|----------|--------|---------------|
| 1 | Source docs (UNs, DIs, architecture, V&V, risk) | hand-authored, `medtech-docs` scaffolding | — | yes (Apr 12–14); risk = placeholder |
| 2 | `trace-matrix.yml` (root) | `/trace-matrix init` (LLM) **or** hand-edit | `project.yml dhfs[]`, source-doc paths | **yes — stale** (line 31 pins OLD output_dir; only declares pca-device) |
| 3 | Project adapter overrides | `/trace-matrix init` analyze phase | source-doc shape + adapter_api contract | no — `tools/project-console/trace-matrix/` has only README. **Defaults must work.** |
| 4 | `console_trace_matrix.{json,md}` at `docs/project/console/<leaf>/` | `python3 .claude/skills/trace-matrix/scripts/build.py --repo . --dhf pca-device` (also wrapped by console "Rebuild" button — `router.py:403-414`, 120 s subprocess) | trace-matrix.yml + source docs + adapters | **no at NEW path** (`docs/project/console/` doesn't exist); old-named `trace-matrix.{json,md}` exists at OLD DHF-tree path (Apr 14) |
| 5 | `/trace-matrix` view | `loader.py:69-104` (read-only) | `project.yml dhfs[]` + sidecar at new path | broken — empty state |

### Skills explicitly NOT in this chain (verified ruled out)

- **`jira-pull`** — `pca-device` has no `jira:` block in `project.yml` or `trace-matrix.yml`; `docs/project/_jira/` does not exist. Sibling pipeline.
- **`dhf-manifest`** — `grep -rn "dhf-manifest" .claude/skills/trace-matrix/ .claude/skills/project-console/console/trace_matrix/` → zero hits. Sibling pipeline.
- **`tracker` / `.taxonomy.yml`** — `grep taxonomy` in trace-matrix consumer code → zero hits. Tracker churn in git status is orthogonal.
- **`renderer.py` link rewriter (ben/031)** — trace-matrix view does not flow through it.

### Source-doc inventory (Step 1) — already on disk

- `docs/project/dhfs/pca-device/design-controls/user-needs/user-needs.md` (13.6 KB, Apr 12)
- `docs/project/dhfs/pca-device/design-controls/requirements/design-inputs.md` (22.7 KB, Apr 12)
- `docs/project/dhfs/pca-device/design-controls/architecture/pca-device-system-sad.md` (8.8 KB, Apr 14)
- `docs/project/dhfs/pca-device/risk-management/risk-strategy.md` (1.1 KB, Apr 12 — `awaiting-content` placeholder; risk layer will render `source_empty`)

### Minimum rebuild path (3 actions, no deletes)

1. **Edit `trace-matrix.yml`** — remove the stale `output_dir:` line (line 31) so `build.py` defaults to `docs/project/console/pca-device/`.
2. **Run** `python3 .claude/skills/trace-matrix/scripts/build.py --repo . --dhf pca-device`.
3. **Verify** in browser at `/trace-matrix/pca-device`. Loader picks up the new path immediately.

### Backup-before-overwrite plan (per user instruction)

Only Step 2 actually overwrites a file. Step 4 writes into a directory that **does not exist yet** — no overwrite there. The OLD DHF-tree sidecar pair would not be touched by the rebuild (different filenames: `trace-matrix.*` vs `console_trace_matrix.*`) but should still be archived as a baseline-016 reference.

```bash
# Backup #1 — yml we're about to edit:
cp trace-matrix.yml trace-matrix.yml.backup-2026-05-05

# Backup #2 — old DHF-tree sidecar (governance: SKILL.md line 17 calls
# the DHF-tree copy a "controlled deliverable" — keep as frozen mirror):
cp docs/project/dhfs/pca-device/design-controls/trace-matrix/trace-matrix.json \
   docs/project/dhfs/pca-device/design-controls/trace-matrix/trace-matrix.json.baseline-016
cp docs/project/dhfs/pca-device/design-controls/trace-matrix/trace-matrix.md \
   docs/project/dhfs/pca-device/design-controls/trace-matrix/trace-matrix.md.baseline-016
```

No `git rm` anywhere — Phase 2 Fix 3 (delete old sidecar) is **withdrawn** at user instruction.

### `/trace-matrix init` — should we run it?

`init` would regenerate `trace-matrix.yml` from `project.yml dhfs[]` — adding the other 8 DHFs. Trade-off:

- **Hand-edit (delete line 31 only):** surgical, minimum change, works for `pca-device`. The other 8 DHFs remain undeclared.
- **Re-run `/trace-matrix init`:** picks up all 9 DHFs from `project.yml`, but **overwrites the current yml** (back up first; see above) and most of the 8 new DHFs have no source files yet — will render `source_missing`/`source_empty`.

**Recommendation:** hand-edit for this pass (preserves the working yml exactly). Re-run `init` later as a separate task if/when the other 8 DHFs get source content.

## Phase 2 — Remediation Plan (proposed, gated on user sign-off)

Three fixes, ordered. Cheapest first.

### Fix 1 — Update `trace-matrix.yml` to remove the stale `output_dir` override (or repoint it)

File: `/Users/ben.xavier/Documents/demos/pdlc_demo/trace-matrix.yml`

Option A (cleanest): delete the `output_dir:` line for `pca-device`. `build.py` will then default to the new `docs/project/console/pca-device/`.
Option B (explicit): set `output_dir: docs/project/console/pca-device`.

### Fix 2 — Rebuild the sidecar at the new location

```bash
python3 .claude/skills/trace-matrix/scripts/build.py --repo . --dhf pca-device
```

Verifies: produces `docs/project/console/pca-device/console_trace_matrix.json` + `console_trace_matrix.md`.

### Fix 3 — ~~Decommission the OLD sidecar~~ → **Archive as baseline-016 mirror** (per user instruction: no deletes)

Rename in place to `trace-matrix.{md,json}.baseline-016` (see backup commands in Phase 1b). Keeps the controlled DHF-tree deliverable as a frozen reference for later comparison against the rebuilt console sidecar.

### Sister-project compatibility check (per standing rule)

Before pushing any skill change upstream, verify against `../arthrex-pccp/` — but **fixes 1–3 are project-data fixes, not skill changes**, so no upstream push is needed. The skill itself is already correct on both sides post-`f5affee`. The arthrex-pccp project will need the same `trace-matrix.yml` migration when its sidecar is regenerated; worth flagging in the sync-log but not blocking on this task.

### Verification

- [ ] `/trace-matrix` index page shows pca-device with populated stats (22 UNs, 34 DIs, etc.).
- [ ] `/trace-matrix/pca-device` renders the layered view with filters working.
- [ ] No console errors / 404s in chrome-devtools network log.

## Open Questions (for user sign-off)

1. **Old sidecar disposition.** Do you want the old `docs/project/dhfs/pca-device/design-controls/trace-matrix/trace-matrix.json` deleted (Fix 3), or left in place as a DHF-leaf controlled-deliverable mirror? (The post-`f5affee` design intentionally moves the *console-consumed* sidecar out of the DHF tree into `docs/project/console/`. Whether the DHF tree should also keep a copy is a doc-controls question.)
2. **`trace-matrix.yml` migration scope.** Should this task also update the yml to declare the other 8 DHFs from `project.yml`, or keep that out of scope?
3. **Was this a known migration TODO from ben/035 that fell through, or genuinely silent?** Want me to grep the ben/035 task doc for residual TODOs before executing?
4. **Branch question.** Land on current `main` alongside the in-flight tracker work (uncommitted in git status), or stash + clean branch?

## Strategy & Lessons

<!-- STRATEGY CONTENT: development, incident-triage -->
**Decision:** Treat skill-pull breakage as triage-first, not fix-first. Read-only forensics located the bug in ~25 minutes; guess-and-fix would have wasted hours on the wrong cause.
**How to apply:** When a sync-skills pull breaks a downstream view, diff the consumer's path/schema constants over the pull SHA window before assuming schema drift.
<!-- /STRATEGY CONTENT -->

<!-- LESSONS LEARNED: skill-pulls -->
**Lesson:** Sync-skill pulls that change consumer-side path constants (e.g., where the loader looks for sidecars) require a coordinated **producer-side rebuild** as a post-update migration step. The `ben/030`/`ben/035` migration checklists need to include "regenerate any sidecars whose output paths moved."
**Why:** Path rename was applied symmetrically in producer + consumer code, but **on-disk sidecar files don't move automatically**. Stale `trace-matrix.yml` `output_dir` overrides further mask the rename — even pressing the in-app Build button writes to the old path.
**How to apply:** Add a check to `/sync-skills pull` post-update flow: after pulling skills, scan project for `trace-matrix.yml` (and analogous skill config files) for path overrides that no longer match the skill's default; surface as drift.
<!-- /LESSONS LEARNED -->

## Changelog

- 2026-05-05: Task created. Suspect window: tasks 030, 031, 033, 035, 043, 044.
- 2026-05-05: **Phase 1 complete.** Root cause identified at high confidence (~85%): commit `f5affee` (ben/035 sync pull, 2026-04-27) renamed the trace-matrix sidecar contract from `docs/project/dhfs/<leaf>/design-controls/trace-matrix/trace-matrix.json` → `docs/project/console/<leaf>/console_trace_matrix.json` symmetrically in producer + consumer code, but no rebuild was run and `trace-matrix.yml` still pins the OLD `output_dir`. Templates / schema / project.yml schema additions ruled out as contributors. Three-step remediation plan documented below; **execution gated on user sign-off** of the four open questions.
- 2026-05-05: **Phase 1b — pipeline reconstruction.** Forensics agent walked backwards from the broken view through the full skill chain. 5-step build graph mapped: source docs → trace-matrix.yml → adapters → build.py → console loader. Confirmed `jira-pull`, `dhf-manifest`, `tracker`, `renderer.py` are NOT in the chain for pca-device (sibling pipelines). Adapter dir `tools/project-console/trace-matrix/adapters/` empty (only README); defaults must work.
- 2026-05-05: **User correction — read the skill first.** I initially proposed "hand-edit `trace-matrix.yml` line 31" as the fix. User caught it: "didn't you read the skill?" Re-read SKILL.md end-to-end and identified `/trace-matrix init` as the prescribed first-time-setup IoC pattern (skill owns the contract; LLM provides parsing intelligence at init time only; builds remain deterministic). Permanent fix installed: new rule in `CLAUDE.md` § For Claude ("Read the skill before synthesizing a plan around it") + cross-session feedback memory `feedback_read_skill_before_planning.md`. **Lesson:** when a skill is in scope, Read SKILL.md end-to-end before any plan; don't infer behavior from filenames or code skim — IoC patterns are invisible from outputs.
- 2026-05-05: **Phase 3 — execution started.** Backups created: `trace-matrix.yml.backup-2026-05-05`, `trace-matrix.{json,md}.baseline-016` for pca-device. Step 1 (read project.yml: 9 DHFs) ✅. Step 2 (write fresh `trace-matrix.yml` covering all 9 DHFs at conventional source paths, no `output_dir` override; also fixed structural bug in old yml — `risk:` and `output_dir:` were dedented out of `layers:` for pca-device) ✅. Step 3 (`analyze.py --json`) ran clean: pca-device fully OK on defaults (UN=22, DI=34, Arch=7 modules, V&V derived, Risk source_empty). 2 of 9 DHFs hit a parser-zero on architecture (connectivity-adapter, drug-library-manager); rest are source_empty data gaps.
- 2026-05-05: **Paused at Step 4 decision point** per pre-agreed scope-2 (pause-checkpoint between adapter-generation and build). Three decisions deferred to user: (1) defer architecture adapter generation to follow-up task 4a or generate now, (2) build scope all-9-DHFs vs just pca-device, (3) branch policy with uncommitted tracker work present. Task doc made resume-ready: explicit phase-3 todos, files-in-flight inventory (backups + modified + not-yet-created), resume command, snapshot of analyze.py output for context recovery.
- 2026-05-06: **Resumed.** Presented Decision 1 (defer adapter generation vs do now). User pushed back on my framing — "the files reference doesn't make sense; we have 1 system SAD, and major components can have a software SAD." Surfaced a deeper structural gap: project lacks a top-level **PCA Infusion System** filing entity that owns the single system SAD, and the per-DHF "*-system-sad.md" docs are scope-mislabeled (they are component-level **software** SADs). Multi-function device regulatory strategy also needs authoring/update (Medical Device / MDDS / non-medical). **Spun off as ben/046** (`tasks/ben/046-pca-infusion-system-architecture-gap.md`) with 6-phase plan and 5 open questions; added to active task index. ben/045 stays surgical. Returning to Decision 1 with the same recommendation (defer adapter generation to follow-up 4a, build the rest).
- 2026-05-06: **Paused for the day.** All 3 Decision-points still open (no user response yet on D1). Updated D1 + D2 with new context: ben/046's pending file renames + the eventual 10th DHF strengthen the "defer + pca-device only" path. Doc made fully resume-ready: explicit "What to do first on resume" priority-ordered checklist added under Resume command. Backups confirmed in place. No code/data changes this session.
- 2026-06-08: Closed Complete via task-doc audit — missing sidecar console_trace_matrix.json restored (817de86) + consumed by ben/049/050; the 3 open decisions mooted by execution; residual gaps spun to ben/046. Moved to Completed in 000-index.md.

