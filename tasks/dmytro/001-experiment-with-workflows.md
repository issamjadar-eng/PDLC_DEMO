# 001 — Experiment With Workflows

**ID**: 001
**Created**: 2026-05-30
**Status**: In Progress
**Created By**: Dmytro Savenkov
**Owner**: Dmytro Savenkov
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
2. **Phase-end batching is OK; drift-batching is not.** Planned phases (e.g., "finish Phase 2, then log the whole phase at once") are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask. By then a crash or context-trim has lost the state. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

_What this task aims to accomplish and why it matters to the project._

- Explore and experiment with the project's agentic workflows (skills, agents, task gating, docflow, etc.)
- Build familiarity with how the PDLC_DEMO toolchain fits together

## Todos

_Actionable work items. Check off as completed._

- [x] Define what specifically to experiment with
- [x] Run through a representative workflow end-to-end (`/strategy assemble regulatory`, `/best-practices`, console-vs-CLI agent comparison)
- [x] Understand the advisor grounding architecture (tier 1/2/3, glob-vs-Read, prompt-as-infrastructure)
- [ ] Work through each skill and agent with real-world scenarios (tomorrow — see Resume plan)
- [ ] _(deferred)_ Rehearse PDLC concepts / map PDLC → SDLC — superseded by the skill-by-skill scenario walk-through

## Session Log

### 2026-05-31 — Orientation & workflow exploration

**What was explored**
- Walked the PDLC_DEMO toolchain end-to-end: how `project.yml` (project identity, team roster, skill/agent registries, security allowlists) acts as the single source of truth that skills, hooks, and automation read from.
- Reviewed the task-first workflow — the `PreToolUse` active-task gate (`.claude/hooks/check-active-task.sh`), the exempt-path list, and the `/task` activation recovery flow.
- Surveyed the installed skill set (medtech-docs, docflow, task, strategy, tracker, lessons, best-practices, trace-matrix, dhf-manifest, secops, …) and the advisor/agent roster, getting a feel for how they compose.
- Inspected `/dhf-manifest` state and the DHF layout, including the nested `--parent` model where item DHFs live under `docs/project/dhfs/cloud-suite/dhfs/<leaf>/`.

**What was understood**
- The three-tier information flow: **external** (FDA/ISO/IEC — read-only upstream truth) → **project** (DHF, design controls, submissions) ← **internal** (corporate SOPs/templates). The project tier is the heart of the DHF and everything converges there.
- The "one task, one file" discipline and the in-flight capture rules for strategy (`<!-- STRATEGY CONTENT -->`) and lessons (`<!-- LESSONS LEARNED -->`) blocks — these are what the harvest skills key off.
- Sentinel blocks (`<!-- AUTO:STRUCTURE -->`) let tools own structural sub-sections of READMEs/CLAUDE.md while humans own the narrative around them.
- The git workflow vocabulary here: "commit" = local only; "push"/"merge"/"save to repo" = full PR-then-auto-merge sequence to `main`.
- DHF count must come from `project.yml dhfs[].path`, not a depth-1 `ls` (captured as a lesson below).

**Project console browser UI (127.0.0.1:8765)**
Explored the local project console UI hands-on, covering:
- **KOL panel** — both round-robin and LLM-moderated modes.
- **Regulatory affairs agent** — ran a PCCP scoping analysis.
- **Risk management agent** — correctly *refused to hallucinate* (declined to fabricate content it had no grounding for — the desired behavior).
- **Core team advisory panel** — 5-way PCCP expansion decision (multi-perspective deliberation).
- **Documents tab** — DHF tree browser.
- **Submission tracker dashboard** — 154 deliverables, 0% complete.
- **Trace matrix (pca-device)** — surfaced orphaned software requirements.
- **Workflows catalog** — reviewed available workflows.
- **B3 strategy reassembler** — ran live; found 27 proposals across 14 task files.

**Next steps (tomorrow)**
1. **Rehearse PDLC concepts** — walk the Product Development Life Cycle phases as represented in this repo (input analysis → design controls → V&V → submissions) to solidify the mental model before mapping.
2. **Switch to SDLC mapping** — once the PDLC rehearsal lands, map PDLC stages onto the Software Development Life Cycle (IEC 62304 activities, software requirements → architecture → implementation → testing) to see how the embedded/SaMD code work threads through the broader product lifecycle.

### 2026-06-04 — `/strategy assemble regulatory` run (workflow experiment)

Exercised the strategy-harvest workflow end-to-end as a representative agentic flow:
- Scanned task docs: 17 `STRATEGY CONTENT: regulatory` candidate hits across 7 files; the prior assembled doc was stale (sourced only `ben/006`, assembled 2026-04-14).
- Delegated assembly to the `strategy/agents/assembler.md` subagent in **non-interactive mode** (a subagent can't cleanly prompt mid-run; non-interactive renders conflicts as reviewable `> **Proposed change**` callouts — data-loss-safe per the agent contract).
- Result: `docs/project/strategies/regulatory-strategy.md` re-assembled — 6 sources (`ben/006, 044, 046, 054, 075, 076`), 12 v15 DECISION blocks (the 8 ben/006 decisions migrated into sentinels with fresh `D-REG-*` IDs), 4,736 words, new History entry under "Dmytro Savenkov".
- **1 proposal** surfaced: §5.2 DHF Filing Composition — `ben/046` (re-parent DHF tree under a "PCA Infusion System" filing-level entity) vs `ben/006` (three peer top-level DHFs). Rendered as a callout; `STRATEGY PROPOSED` marker written into `tasks/ben/046` (line 132). **Awaiting resolution** via `/strategy resolve regulatory` (accept / withdraw / leave).
- 3 subsections landed in `## Uncategorized` (medtech-docs gap + two HIPAA/privacy decisions from ben/075/076) — signal that the regulatory topic→section mapping lacks a privacy/HIPAA row.

<!-- LESSONS LEARNED: tooling -->
**Code-block-embedded tags are scanner false positives.** `tasks/ben/007` contained 8 `STRATEGY CONTENT: regulatory` strings that are *illustrative examples* inside fenced/indented code blocks, not real tagged blocks. A naive `grep` counts them; the assembler correctly excluded all 8 by checking each candidate's context (must be on a line by itself, not inside a code fence or indented as code). When scanning for tagged content, always verify the tag is a standalone line outside code context before treating it as a real block.
<!-- /LESSONS LEARNED -->

### 2026-06-04 — Architecture deep-dive, `/best-practices`, console-vs-CLI agent comparison

**`/best-practices` audit**
- Ran the audit: **3 FAILs, 8 WARNs**.
- Fixed the `project-secops.md` symlink (was the deleted/broken agent symlink showing in `git status`). Remaining FAILs/WARNs not yet triaged — review next session.

**Console vs Claude Code — same regulatory question, two runtimes**
- Asked the **regulatory advisor** the same question in both runtimes.
- **Claude Code** found unfilled `{{...}}` template placeholders (e.g. `{{Populate}}`) in the grounding docs; the **console missed them** because its grounding is truncated at a **~200 KB context cap**, so the placeholder-bearing content fell outside the window.
- Takeaway: the two runtimes are **not equivalent for completeness-critical review** — the console trades context breadth for a bounded budget. For "did we leave anything unfilled?" checks, prefer the Claude Code runtime (or be aware of the cap).

**Advisor grounding — how it actually works (corrected mental model)**
- Tier 1/2/3 grounding is **not enforced infrastructure** — it lives as **instructions inside the advisor's ~18 KB agent prompt**. The tiers are prose the model is *told* to follow, not a hard pipeline.
- Grounding therefore happens through the agent's **own tool calls**: **Glob** to *discover* candidate files (cheap, returns paths), then **Read** to *fetch* the content it decided it needs. Quality depends on the model following the prompt + its tool/context budget — not on a deterministic loader.
- This explains the console-vs-CLI gap above: same prompt instructions, but the console's runtime pre-truncates grounding at 200 KB before the agent reasons, whereas the CLI agent reads on demand.

<!-- LESSONS LEARNED: tooling -->
**Console (200 KB cap) and Claude Code are not equivalent for completeness checks.** The console truncates advisor grounding at ~200 KB; Claude Code reads files on demand. On the same regulatory question, the CLI advisor caught unfilled `{{...}}` template placeholders that the console missed because the relevant content was outside the console's capped window.

**Why:** The advisor's tier 1/2/3 grounding is prompt *instructions*, executed via the agent's own Glob (discover) + Read (fetch) calls — not a deterministic pipeline. A runtime that pre-truncates grounding (console) can starve the agent of content the instructions would otherwise have it read.

**How to apply:** For completeness-critical review ("is anything left as a placeholder / unfilled?"), use the Claude Code runtime, or chunk the question so each console call stays under the cap. Treat console advisor answers as breadth-bounded.
<!-- /LESSONS LEARNED -->

## Resume — pick up here next session

_Refreshed on 2026-06-04 (end of architecture deep-dive session)._

**Tomorrow's theme:** work through each skill and agent with **real-world scenarios** — drive them like a practitioner would, not just survey them.

**First action on resume (priority order):**
1. **`/trace-matrix` on `pca-device`** — build/inspect the bidirectional trace matrix for the PCA device DHF; use it as the first concrete scenario.
2. **`/strategy assemble regulatory`** — re-run now that the §5.2 `ben/046`-vs-`ben/006` proposal exists; decide accept/withdraw/leave via `/strategy resolve regulatory`.
3. **Agent comparisons** — continue the console-vs-Claude-Code advisor comparison on more questions, now that the 200 KB-cap gap is understood (see today's session log + lesson).

**In-flight artifacts / external state:**
- `main` is at `9112240`. **This session's committed-to-disk changes** (not yet committed to git unless noted): re-assembled `docs/project/strategies/regulatory-strategy.md`; `STRATEGY PROPOSED` marker added to `tasks/ben/046` (line 132); **fixed `project-secops.md` symlink** (resolved the broken/deleted agent symlink from skill-sync churn).
- Other **uncommitted, NOT part of task 001**: untracked `tasks/dmytro/002-*.md`, `tasks/dmytro/003-*.md`, `docs/dashboard.html`, `tasks/dmytro/SECOPS.md` (belong to tasks 002/003 + secops), plus type-changed `.claude/agents/*.md` symlinks (skill-sync churn). Claude has **not** committed anything this session.
- `/best-practices` left **3 FAILs + 8 WARNs** — only the `project-secops.md` symlink FAIL was fixed; the rest are untriaged.
- Live worktree exists for task 003: `.worktrees/workflow-strategy-architecture-2026-05-31/` on branch `workflow/strategy-architecture-2026-05-31` — separate task, leave alone.
- Last committed task-001 work: `1913ea9` (2026-05-31, orientation session log, merged via PR #27).
- Live worktree exists for task 003: `.worktrees/workflow-strategy-architecture-2026-05-31/` on branch `workflow/strategy-architecture-2026-05-31` — separate task, leave alone.
- Last committed task-001 work: `1913ea9` (2026-05-31, orientation session log, merged via PR #27).

**Anti-patterns to avoid:**
- Don't redo the 2026-05-31 orientation exploration — it's already logged in the Session Log below.
- Don't commit the unrelated untracked files as part of task 001.

**To resume:** `/task` is already wired — activate with
`bash .claude/hooks/task-activate.sh add <SESSION_ID> 001`

## Open Questions

- None blocking. Next work (PDLC rehearsal → SDLC mapping) is self-directed exploration.

## Lessons Learned

<!-- LESSONS LEARNED: tooling -->
**Count DHFs from `project.yml` paths, not a depth-1 `ls`.** While inspecting `/dhf-manifest` state I reported a false "three-way DHF mismatch" — `ls docs/project/dhfs/*/` showed only 3 DHFs while project.yml declared 10 and the manifest routed 9. I concluded 7 DHFs were missing on disk and nearly scaffolded them. They were not missing: this project uses the nested `--parent` model, so 7 item DHFs live under `docs/project/dhfs/cloud-suite/dhfs/<leaf>/`, invisible to a depth-1 glob. All 10 exist and are fully populated.

**Why:** A depth-1 `docs/project/dhfs/*/` glob silently undercounts DHFs whenever the nested model is in use. Acting on that undercount would have overwritten 7 populated DHFs.

**How to apply:** Treat `project.yml dhfs[].path` as the source of truth for DHF location (per the audit-wiring-before-adding-fields rule). To check existence, iterate those paths — don't infer the roster from a top-level directory listing. The catch that saved this: verifying each declared path against disk *before* writing. `cloud-suite` being excluded from manifest routing is also correct, not drift — it's the `role: system` DHF that synthesizes from its items.
<!-- /LESSONS LEARNED -->

## Changelog
See [README.md](README.md) for version history.

- 2026-05-31 — Logged orientation session: explored the PDLC_DEMO toolchain (project.yml as source of truth, task gate, skill/agent roster, three-tier info flow, sentinel blocks, git workflow) and the project console browser UI at 127.0.0.1:8765 (KOL panel, regulatory/risk agents, core team panel, documents tab, submission tracker, trace matrix, workflows catalog, B3 strategy reassembler). Defined experiment scope. Planned tomorrow: rehearse PDLC concepts, then switch to SDLC mapping.
- 2026-06-04 — Architecture deep-dive session. Ran `/best-practices` (3 FAILs, 8 WARNs); fixed the `project-secops.md` symlink (other findings untriaged). Compared the regulatory advisor across runtimes: Claude Code caught unfilled `{{...}}` template placeholders the console missed due to its ~200 KB grounding cap. Built the mental model that tier 1/2/3 grounding is **prompt instructions in the ~18 KB agent file** (not enforced infra), executed via the agent's own Glob (discover) + Read (fetch) calls — captured as a tooling lesson. Re-pointed tomorrow's plan to a skill-by-skill real-world-scenario walk-through; resume order = `/trace-matrix` (pca-device) → `/strategy assemble regulatory` (resolve §5.2 proposal) → more agent comparisons.
- 2026-06-04 — Ran `/strategy assemble regulatory` as a workflow experiment. Re-assembled `docs/project/strategies/regulatory-strategy.md` (stale → 6 sources, 12 v15 DECISION blocks, 4,736 words) via the assembler subagent in non-interactive mode. 1 proposal surfaced (§5.2 DHF composition, ben/046 vs ben/006 — `STRATEGY PROPOSED` marker written to ben/046:132, awaiting `/strategy resolve`); 3 subsections in Uncategorized (HIPAA/privacy mapping gap). Logged a tooling lesson on code-block tag false positives. No commit made.
- 2026-06-04 — Recovery checkpoint. Previous session ended 2026-06-04 10:02 uncheckpointed; reconstruction from `git log`/working tree found **no new task-001 artifacts** since 2026-05-31 (`1913ea9`) — that session left no git or working-tree trace for this task. Refreshed doc to resume-ready: added Resume + Open Questions sections, captured in-flight working-tree state (unrelated 002/003/secops untracked files, task-003 worktree). Next steps unchanged: PDLC rehearsal → PDLC↔SDLC mapping. Cleared the `uncheckpointed-dmytro-001` recovery marker.
