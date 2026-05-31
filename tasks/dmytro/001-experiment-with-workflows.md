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
- [ ] Run through a representative workflow end-to-end
- [ ] Rehearse PDLC concepts (tomorrow)
- [ ] Map PDLC → SDLC (tomorrow, after PDLC rehearsal)

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

## Lessons Learned

<!-- LESSONS LEARNED: tooling -->
**Count DHFs from `project.yml` paths, not a depth-1 `ls`.** While inspecting `/dhf-manifest` state I reported a false "three-way DHF mismatch" — `ls docs/project/dhfs/*/` showed only 3 DHFs while project.yml declared 10 and the manifest routed 9. I concluded 7 DHFs were missing on disk and nearly scaffolded them. They were not missing: this project uses the nested `--parent` model, so 7 item DHFs live under `docs/project/dhfs/cloud-suite/dhfs/<leaf>/`, invisible to a depth-1 glob. All 10 exist and are fully populated.

**Why:** A depth-1 `docs/project/dhfs/*/` glob silently undercounts DHFs whenever the nested model is in use. Acting on that undercount would have overwritten 7 populated DHFs.

**How to apply:** Treat `project.yml dhfs[].path` as the source of truth for DHF location (per the audit-wiring-before-adding-fields rule). To check existence, iterate those paths — don't infer the roster from a top-level directory listing. The catch that saved this: verifying each declared path against disk *before* writing. `cloud-suite` being excluded from manifest routing is also correct, not drift — it's the `role: system` DHF that synthesizes from its items.
<!-- /LESSONS LEARNED -->

## Changelog
See [README.md](README.md) for version history.

- 2026-05-31 — Logged orientation session: explored the PDLC_DEMO toolchain (project.yml as source of truth, task gate, skill/agent roster, three-tier info flow, sentinel blocks, git workflow) and the project console browser UI at 127.0.0.1:8765 (KOL panel, regulatory/risk agents, core team panel, documents tab, submission tracker, trace matrix, workflows catalog, B3 strategy reassembler). Defined experiment scope. Planned tomorrow: rehearse PDLC concepts, then switch to SDLC mapping.
