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
- [x] Exercise 1 — observe advisor tier-architecture via a live risk-management question (2026-06-06)
- [ ] Exercise 2 — console vs Claude Code runtime comparison (tomorrow — see Resume plan)
- [ ] Work through each skill and agent with real-world scenarios (skills walkthrough — see Resume plan)
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

### 2026-06-06 — Exercise 1: advisor tier-architecture observation (risk-management)

**The exercise.** Asked the **risk-management advisor** a single practitioner question — _"what are the top risks for the PP3500 510(k) submission right now?"_ — and watched how it grounds itself before answering.

**What we observed**
- **24 tool calls** executed across the advisor's tiers before it answered — a concrete view of grounding-as-tool-calls (consistent with the 2026-06-04 mental model that tiers are prompt instructions the agent runs itself, not an enforced pipeline).
- The agent **found the empty `{{}}` placeholder stubs in every PP3500 risk file** and **cited exact file paths** — `GL-TMP-RM-001` (risk plan) through `004` (risk management report), the `risk-management/` hazard analysis + design FMEA, plus the DLM accessory's matching empty stub. It distinguished "present but unpopulated" from "absent," which is the audit-relevant nuance.
- It also caught a **discovery-index false-negative**: `pdlc-demo-dhf-discovery.json` resolves the risk roles to `null` for every DHF (pattern-matching gap — the index patterns don't match the `GL-TMP-RM-*` filenames), yet the files exist on disk. The agent verified disk over index.

**Tier architecture understood (today's framing)**
- **Tier 1** — a **small, always-read set** for project orientation (identity, roster, the load-bearing manifests). Cheap, read every time.
- **Tier 2** — a **larger, domain-specific set** the advisor pulls for its lane, **plus semantic search** (file-locator) to discover relevant docs beyond the fixed list.
- **Tier 3** — a **fallback subagent** (advisor-researcher) invoked only when Tier 1 + Tier 2 don't cover the question — walks READMEs / cross-refs / globs for additional grounding.

**Takeaway.** The advisor's answer quality tracks how well the tiers surface the right files — and Tier 1's always-read orientation set is what let it know to go look for the risk files in the first place, even when the discovery index said they were null.

### 2026-06-07 — Exercise 2: console vs Claude Code (existence/completeness)

**The exercise.** Asked the **console** risk-management agent the same PP3500 top-risks question that the **Claude Code** risk-management advisor answered on 2026-06-06, to compare the two runtimes on a completeness-critical question.

**What we observed (the failure is worse than expected).**
- Yesterday's **Claude Code** advisor correctly found the PP3500 risk files **present but empty** — rev-0.1 `{{}}` placeholder stubs (`GL-TMP-RM-001`–`004` + hazard analysis/FMEA), and cited exact paths.
- Today's **console** agent claimed the DHF risk files **don't exist at all**.
- That is not a truncated answer — it's a **factually wrong conclusion**. The ~200 KB grounding cap didn't just shorten the response; it starved the agent of the files entirely, and the agent reported *absence* where the truth is *present-but-unpopulated*. For a risk file, "absent" and "empty stub" are very different findings with different remediation.

<!-- LESSONS LEARNED: tooling -->
**The console's 200 KB cap can flip a conclusion, not just shorten it — don't trust it for existence/completeness questions.** On the same PP3500 risk question, the Claude Code advisor found the risk files present-but-empty (`{{}}` stubs, exact paths cited); the console agent concluded the risk files **don't exist at all**. The cap starved the agent of the files, and it reported *absence* instead of *present-but-unpopulated*.

**Why:** This is a sharper failure mode than the 2026-06-04 lesson (which framed the cap as missing some content). When the capped window excludes a file entirely, the agent doesn't say "I'm not sure" — it asserts a confident negative ("the file doesn't exist"). For a risk file, "absent" vs "empty stub" are materially different findings that drive different remediation, and a false "absent" is the more dangerous error in an audit context.

**How to apply:** Never rely on the console for existence-, presence-, or completeness-of-evidence questions ("do we have X?", "is X filled in?", "what's missing?"). Use the Claude Code runtime, which reads files on demand, for any question whose answer hinges on what is or isn't on disk. Treat a console "X doesn't exist" as "X was outside my grounding window," not as ground truth — confirm against the CLI or the filesystem before acting.
<!-- /LESSONS LEARNED -->

## Resume — pick up here next session

_Refreshed on 2026-06-06 (end of Exercise 1 session)._

**Tomorrow's plan:**
1. **Exercise 2 — console vs Claude Code comparison.** Run the same advisor question in both runtimes and compare; re-confirm the ~200 KB console grounding-cap behavior observed on 2026-06-04 against today's risk-management findings.
2. **Skills walkthrough** — work through each skill with real-world scenarios (the deferred skill-by-skill practitioner walk-through). Candidate concrete scenarios still queued: `/trace-matrix` on `pca-device`; `/strategy resolve regulatory` for the open §5.2 `ben/046`-vs-`ben/006` proposal.

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
- 2026-06-07 — Ran **Exercise 2**: console vs Claude Code on the same PP3500 risk question. Console agent claimed the DHF risk files **don't exist**; the CLI advisor (2026-06-06) correctly found them present-but-empty (`{{}}` stubs). Captured a tooling lesson — the ~200 KB cap can **flip a conclusion** (assert false absence), not just truncate it; console is unreliable for existence/completeness questions. Started the console in the background (ID `b3tyc7wqm`) on http://127.0.0.1:8765. No commit made.
- 2026-06-06 — Ran **Exercise 1**: asked the risk-management advisor for the PP3500 510(k) top risks and observed its grounding behavior. Watched **24 tool calls** across Tier 1/2; agent found empty `{{}}` placeholder stubs in all PP3500 risk files (`GL-TMP-RM-001`–`004` + hazard analysis/FMEA + DLM accessory) and cited exact paths, and caught a discovery-index false-negative (`pdlc-demo-dhf-discovery.json` resolves risk roles to `null` but files exist on disk). Consolidated the tier model: **Tier 1** = small always-read orientation set; **Tier 2** = larger domain-specific set + semantic search; **Tier 3** = fallback researcher subagent. Updated Todos + Resume; tomorrow = Exercise 2 (console vs Claude Code) then skills walkthrough. No commit made. (Recovery markers from prior uncheckpointed sessions cleared at session start per user direction.)

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 2,
    "todos": [
      {
        "todo": "Experiment with workflows",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 4,
          "max": 10
        },
        "confidence": "low",
        "basis": "experiment with workflows"
      }
    ]
  }
}
```
