# 048 — Sister-Project Parity + Console Feature Walkthrough

**ID**: 048
**Created**: 2026-05-11
**Status**: Abandoned (superseded)
**Created By**: Ben Xavier
**Owner**: Ben Xavier
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

Compare PDLC_DEMO against the sister project `/Users/ben.xavier/Documents/projects/arthrex/pccp/` to (a) eliminate any bespoke / project-specific content that has leaked into a skill, agent, or piece of shared infrastructure that's supposed to be reusable, and (b) adopt any improvements the sister has made that we haven't picked up. Then walk the project-console UI section by section to confirm feature parity and surface any subtler bespoke leaks.

Mandate (per persistent memory): **skills must generalize.** Anything project-specific lives in `project.yml`, the `docs/project/...` tree, `tools/project-console/console.yaml`, `tools/project-console/themes/<slug>/`, or `tools/project-console/agents/` — never in `.claude/skills/` or `.claude/agents/`.

## Prioritized Backlog (lowest-risk → most-complex)

Work the list top-down. Each row is a single, scoped checkpoint. Update Status as you go.

### Tier 1 — Cheap / Safe (no skill mutations, mostly reads + 1-line fixes)

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1 | **Push `sync-skills` SKILL.md genericization upstream** | ✅ Done 2026-05-11 — hitachi PR #148 squash-merged at `bd753b0`. Local hitachi fast-forwarded. | The 3-site `pdlc-demo`/`PDLC_DEMO` → `acme-demo`/`<project>` substitution we adopted from the sister. Mechanical PR; one file; no behavior change. Closes the regression that bit us today (upstream itself was the leak source). |
| 2 | **Investigate `project-console/.claude/` config-leak folders** | ✅ Done 2026-05-11 — both were 100% empty directory shells (ours had nested empty dirs mirroring the `project-console` skill structure; sister has nested empty dirs mirroring `tracker` plus 4 macOS `Icon` Finder-cruft files). Theory: someone ran a scaffolding tool from the wrong CWD inside a skill folder, creating directory shape without copying content. Deleted ours via `rm -rf .claude/skills/project-console/console/.claude/`. Sister's identical-shape leak flagged in Tier 3 §17 as a heads-up. | Both projects have one; locations differ (ours: `project-console/console/.claude/`; sister: `project-console/.claude/`). Neither is in upstream registry. Goal: identify what's inside, confirm it's local-config artifact, delete from both or move to `tools/project-console/.claude/` if legitimately needed. |
| 3 | **Compare `tools/project-console/console.yaml`** | ✅ Done 2026-05-11 — three fixes applied in one edit: (a) **added** `models:` block (sister had it; we didn't) with explicit `default: claude-sonnet-4-6` matching our code default; (b) **removed** stale `dashboards.patterns: docs/**/*-tracker-candidate.html` (matched nothing post-candidate-archive); (c) **removed** stale `dashboards.overrides.submission-tracker-candidate` (slug no longer exists). Restarted console, verified config parses + all endpoints 200 + `/dashboards` now lists only canonical `submission-tracker`. | Project-local config. Verify no bespoke logic has leaked into the *skill* via this file's contract (e.g., a key only our project uses that would break the sister). Expected outcome: the *contract* matches; the *values* legitimately differ. |
| 4 | **Compare `tools/project-console/agents/` rosters** | ✅ Done 2026-05-11 — `core-team/` group is identical between projects (13 personas: clinical-affairs, core-team-panel, cybersecurity, design-review-panel, human-factors, post-market, program-manager, quality-engineering, rd-lead, regulatory-affairs, risk-management, systems-engineering, vnv-lead + `_group.md`). Our project has a unique `kol/` group (8 KOLs + 2 PP3500 panels) — verified self-contained (no skill-internal references in any kol file; no skill code references kol/). `tools/project-console/agents/` is project-owned per the file-ownership convention, so this is legitimate customization, not a leak. | Each project ships its own persona files at install time. Verify the install-time template (`agents/templates/` inside the skill) is project-agnostic and that the materialized files in `tools/project-console/agents/` differ only in project-specific grounding. |
| 5 | **Inspect uncommitted skill-pulled files for residual local diff** | ✅ Done 2026-05-11 — verified all three files match `origin/main` exactly (the `M` was just "newer pulled content vs last commit"). Surfaced that the entire session's work was uncommitted across ~32 modified + ~19 untracked files. Pushed 4 logical commits to PDLC_DEMO `origin/main` (now at `a7395fa`): (A) `92ba076` sync sweep + sync-skills v8.1 + B6, (B) `564bf95` tracker reset/044 closeout + 047 follow-up, (C) `409ace0` ben/048 #2-#3 console.yaml parity + leak removal, (D) `a7395fa` task housekeeping + CLAUDE.md skill rule. Held back from this commit set: `project.yml` (216+/299− reformat), `trace-matrix.yml` (170+/11−), `trace-matrix.{json,md}.baseline-016`, `trace-matrix.yml.backup-2026-05-05` — all belong to paused task ben/045 (Trace Matrix View Breakage Recovery). | `git status` shows `M` on `.claude/skills/project-console/console/web/static/{assistant.js,tracker_interactive.js}` and `console/workflows/router.py` left over from earlier pulls. Confirm content equals `origin/main` (so the `M` is just an untracked-line-ending artifact) and commit, or revert. |

### Tier 2 — Console UI feature parity walkthrough (browser-based, read-only)

Walk each route in both projects' running consoles via chrome-devtools MCP. For each route: confirm it loads, screenshot, note any layout/feature gap, decide if the gap is skill-side (fix) or project-data-side (defer to project tasks).

| # | Route | Status | Notes |
|---|-------|--------|-------|
| 6 | `/` (landing) | ✅ Done 2026-05-11 — user confirmed works. | |
| 7 | `/overview` (asset card selector) | ✅ Done 2026-05-11 — user confirmed consistent between projects. | Sister may have different cards depending on what their project surfaces. Compare card *kinds*, not card *content*. |
| 8 | `/agents` (chat) | ✅ Done 2026-05-11 — user confirmed consistent and works. | |
| 9 | `/documents` (explorer) | ✅ Done 2026-05-11 — user confirmed good. | Renderer behavior, link rewriter, grounding surface. |
| 10 | `/trace-matrix` (per-DHF view + drift overlay) | ✅ Done 2026-05-11 — user confirmed the route looks correct. Data-architecture comparison: skill behavior identical between projects (both load same code, render available sidecars gracefully). Differences are entirely project-side: sister has 4-DHF config + sidecars built at the **new** `docs/project/console/<dhf>/console_trace_matrix.json` path convention + full Jira mirror under `docs/project/_jira/` with 3-arch × multi-version mirror data (epics/stories/hazards/tests/drift); we have 10-DHF config but only 1 sidecar at the **old** `docs/project/dhfs/<dhf>/design-controls/trace-matrix/trace-matrix.json` path (rename happened in hitachi `f5affee` during ben/035 sync; our rebuild never ran). Rebuild recovery is paused task ben/045's job. No skill leak found. | Sister has `jira-mirror` adapter populated; ours doesn't. Skill behavior should be identical when sidecar is absent. |
| 11 | `/workflows` (catalog + the strategy-reassembly + B6 draft) | ✅ Done 2026-05-11 — user confirmed workflows work. | |
| 12 | `/dashboards` (submission-tracker + others) | ✅ Done 2026-05-11 — skill renders identically on both sides (same 11-column template, same renderer code path). All differences are **project-data input volume**, not skill bespoke-ness: OURS 44 rows / 4 sections / 0 Create Draft buttons / 0 AI Status / 0 (?)(i) panels — SISTER 123 rows / 19 sections / 5 buttons / populated AI Status / rich (?)(i) panels. Specific gaps mapped to inputs missing from our side: `milestones/engineering.yml` (→ ENG1-ENG10 rows + Engineering Prerequisites section), `submissions/qsub/composition-manifest.md` (→ Q1-Q12 narrative rows incl. cover letter / device description / indications / predicate analysis / PCCP summary), `submissions/pccp/composition-manifest.md` (→ richer 510k+PCCP rows), `tracker-user-rows.yml` (→ user-injected Q4-Q8 with disabled Create Draft button placeholders that render.py wires up), `submission-tracker.help.json` (→ "What is X / Why it matters / Main topics" content in (?) info-rows; product of `/tracker enrich-help` action), `submission-tracker.details.json` (→ structured Phase/Scope/Path/REF blocks in (i) info-rows; `/tracker enrich-details` action), `submission-tracker.agent.json` (→ AI Status column data), plus hand-authored structural sections (legends, Cross-Milestone Summary, Notable Findings, Reviewer Sign-off, Changelog — these are author-managed, not generator-emitted). All gaps map to task ben/047 backlog items; this comparison gives ben/047 the concrete sister-side targets to mirror. | We're at 44 rows (task ben/047); sister has a different tracker shape. Verify skill renders both correctly. |

### Tier 3 — Deeper investigations (may spawn follow-up tasks)

| # | Item | Status | Notes |
|---|------|--------|-------|
| 13 | **`docx`/`pptx`/`xlsx` `scripts/office/` folders in sister** | Not Started | Bespoke OOXML helpers/schemas/validators living inside the skill directory. NOT in upstream registry. Decide: are these (a) sister-only leak we tell them about, (b) something the skill should bundle properly, or (c) something that belongs in `tools/` on each project? |
| 14 | **`dhf-manifest/data/tier1-regulatory` + `tier3-reference` in sister** | Not Started | Project-generated data. Confirm our dhf-manifest pipeline produces the same artifact shape under `docs/project/dhf-manifest/` — if so, the sister is just *also* writing it inside the skill folder (leak); if not, we may be missing a pipeline run. |
| 15 | **`medtech-docs/references/fda-guidance/docs/` in sister** | Not Started | Same question — is this a leak into the skill folder of what should live under `docs/external/fda-guidance/`? |
| 16 | **Theme pack hygiene** | Not Started | We use `globallogic` (the corporate parent theme); sister presumably uses `arthrex`. Confirm both are correctly resolved via `console.yaml` `theme:` key and that no theme assets leak into the skill `themes/` shared light/dark base. |
| 17 | **Trace-matrix `jira-pull` adapter** | Not Started | Sister project uses Jira-mirrored items. Confirm `/trace-matrix` skill in *our* project still works correctly with the absent-sidecar code path; verify there is no implicit dependency on Jira mirror being present. |
| 18 | **Sister's other `dhf-manifest` bespoke additions** | Not Started | The sister has `dhf-manifest/data/canonical-roles.yaml`, `dhf-manifest/scripts/discovery-index.py`, and a `dhf-manifest/tests/` folder — none of which is in upstream. Likely their unpushed WIP. Surface to them as a "you have unpushed sister-side work" heads-up; we don't mirror it. |
| 19 | **Sister's empty `project-console/.claude/` shell** | Not Started | Identical leak pattern to our #2 (deleted on our side). Their copy has 4 macOS `Icon` files inside but no real content. Flag for their cleanup; not our project. |

## Working Conventions

- Present items to the user **one at a time** (per the "one decision at a time" memory rule). Drive each through investigation → proposed fix → execute → checkbox tick → move to next.
- For each console route in Tier 2, fire chrome-devtools to load both projects' running consoles in parallel and screenshot for visual comparison. The sister's console will need to be started if it isn't already.
- Any sister-bespoke leak we discover that originated upstream gets a follow-up upstream-push entry under Tier 1.
- Anything that becomes a meaningful workstream of its own (e.g., a pipeline rerun, a multi-skill refactor) gets spun out as its own `tasks/ben/NNN-` task and linked back from this doc.

## Resume Command

```bash
bash .claude/hooks/task-activate.sh add <UUID-from-printenv-or-denial> 048
```

## Changelog

- 2026-05-11: Task created. Backlog captures items surfaced during the initial `.claude/skills` diff between PDLC_DEMO and arthrex/pccp. Sync-skills v8.1 already pulled + leak-fix adopted locally this session; remaining work tracked here. Predecessor sync-log entry: see `.claude/sync-log.md` § "2026-05-11 — pull (visual polish + regulatory-affairs grounding)".
- 2026-05-11: **#1 done.** Pushed sync-skills SKILL.md genericization upstream as hitachi PR #148; squash-merged at `bd753b0`. Local hitachi fast-forwarded. The next pull from any sister project will see SKILL.md as UPSTREAM_NEWER and adopt the clean version; recurrence prevented. Sync log updated.
- 2026-05-11: **#2 done.** Inventoried both `project-console/.claude/` leak folders: ours had **zero files** (just empty nested dir mirror of the project-console skill); sister has 4 macOS `Icon` files inside an equivalent empty `tracker`-shaped dir tree. Confirmed via `git ls-tree origin/main` that nothing matches this pattern in upstream — pure local leak in both projects. Deleted ours; sister's added to Tier-3 as #19 (heads-up only). Re-diff surfaced three additional sister-bespoke items in `dhf-manifest` (canonical-roles.yaml, discovery-index.py, tests/) — added as Tier-3 #18.
- 2026-05-11: **#3 done.** Diffed `tools/project-console/console.yaml` against the sister and surfaced three fixes: (a) we were missing a `models:` block — added with explicit `default: claude-sonnet-4-6` matching our `DEFAULT_MODEL` code default (no behavior change, just discoverability + future-flipping); (b) removed stale `dashboards.patterns: docs/**/*-tracker-candidate.html` and (c) removed stale `dashboards.overrides.submission-tracker-candidate` — both referenced files we archived during the ben/044 reset. Restarted console; config parses, all endpoints 200, `/dashboards` now correctly lists only the canonical `submission-tracker`.
- 2026-05-11: **#4 done.** Compared `tools/project-console/agents/` rosters. `core-team/` (13 personas + group descriptor) is byte-identical between projects — perfect parity. Our project also has a `kol/` group (8 KOLs + 2 PP3500 panels) the sister doesn't carry; verified self-contained (no skill-internal references) and not referenced by skill code — legitimate project-local addition, no leak.
- 2026-05-11: **#5 done + Tier 1 complete.** Resolved the residual M-flagged pulls (assistant.js, tracker_interactive.js, router.py — all exact-match upstream `origin/main`). Found broader uncommitted scope: ~32 modified + ~19 untracked files spanning today's two sync pulls + tracker reset + parity work + 4 new task docs. Bundled into 4 logical commits + pushed to PDLC_DEMO `origin/main` (`92ba076` sync sweep + B6; `564bf95` ben/044 closeout + ben/047 follow-up; `409ace0` ben/048 #2-#3 parity sweep; `a7395fa` task housekeeping + CLAUDE.md skill rule). Held back project.yml + trace-matrix WIP (paused task ben/045 territory). Tier 1 of this task complete — moving to Tier 2 console UI walkthrough.
- 2026-05-11: **Tier 2 progress — 4 of 7 routes greenlit by user visual walkthrough.** `/overview` consistent; `/agents` consistent and works; `/documents` good; `/workflows` work. Remaining: `/` (landing), `/trace-matrix` (the higher-risk one — sister has Jira mirror sidecars + drift overlay, ours doesn't), `/dashboards` (the submission-tracker only has 44 rows post-reset — sister's tracker shape may differ).
- 2026-05-11: **Landing greenlit. `/dashboards/submission-tracker` deep-dive done — skill behavior is identical; all differences are project-data input volume.** Side-by-side comparison: ours 44 rows / 4 sections / 0 Create Draft buttons / empty AI Status / empty (?)(i) panels; sister 123 rows / 19 sections / 5 buttons / populated everywhere. Same 11-column template, same renderer code path on both. Mapped every visible gap to a missing project-side input: `milestones/engineering.yml`, `submissions/{qsub,pccp}/composition-manifest.md`, `tracker-user-rows.yml`, `submission-tracker.{help,details,agent}.json` sidecars (products of `/tracker enrich-help` / `enrich-details` / `assess` actions), plus hand-authored structural sections. All gaps already on ben/047 backlog — this comparison gives ben/047 the concrete sister-side patterns to mirror. Tier 2 now 5 of 7 done; remaining: `/trace-matrix` (#10).
- 2026-06-08: **Closed ABANDONED (superseded) per user.** Tier-3 investigations not pursued as a one-off task — sister-project parity is maintained continuously via the routine `/sync-skills` + `/best-practices` cadence. Moved to Abandoned in 000-index.md.

