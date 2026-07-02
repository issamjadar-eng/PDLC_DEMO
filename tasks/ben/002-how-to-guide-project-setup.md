# 002 — How-To Guide: Repeating Project Setup

**ID**: 002
**Created**: 2026-04-12
**Status**: Complete (superseded by ben/069)
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## Goals

_Produce a concise, reproducible how-to guide that walks a new user through standing up a MedTech PDLC project from scratch: pulling the Hitachi skill registry, installing skills into `.claude/`, running `/medtech-docs init` to scaffold the docs tree, and using `/sync-skills` as the ongoing registry-sync mechanism._

- Lower the barrier for new teams to spin up a PDLC project the same way we did
- Document the exact sequence (clone → copy skills → answer init prompts → verify scaffold → create first task → ongoing sync)
- Capture the decisions the init skill asks about (device type, pathway, AI/ML, EHR, imaging, navigation, existing docs) and how answers affect the generated structure
- Teach the opt-in vs. default behaviors of `/sync-skills push` (PR-only by default, `--merge` is opt-in)
- Make the guide copy-pasteable — every command runnable without further interpretation

## Todos

- [x] Pick a location for the guide — **resolved: stays at repo root `how-to-guide.md`, sibling of `setup.md`**
- [x] Write step 1: prerequisites (git SSH to `GlobalLogic-a-Hitachi-Company/hitachi`, `jq` installed, Claude Code running)
- [x] Write step 2: cloning `hitachi` and copying `skills/` + `agents/` into `.claude/` (directory-based install; README curl model is stale)
- [x] Write step 3: initializing the target repo (git init, remote, gitignore)
- [x] Write step 4: running `/medtech-docs init` — **corrected to 9 questions** (added Modules/functions Q3 + Primary DHF name Q9)
- [x] Write step 5: what the init produces — covered in Phase 3 ("After the questions, `init` creates project.yml, the docs/ tree, READMEs, CLAUDE.md, wires task-gate hooks").
- [x] Write step 6: post-init verification — added the **"Verify the scaffold"** subsection under Phase 3 (`docs/` tree + README check, `jq` inspection of `project.yml` DHF path, `settings.json` PreToolUse hook check, sentinel-render check, first `/medtech-docs dashboard` run; re-run init rather than hand-patch on failure). Flow-at-a-glance updated.
- [x] Write step 7: **create the first task to capture the setup work itself** — covered as Phase 5 (`001-project-init`), with the init-before-task ordering constraint called out in Phase 3 and the troubleshooting table. Call out the ordering: `/medtech-docs init` must run *before* any `task` commands, because init is what installs and wires the `task` skill's hooks. Once init completes, create `tasks/<person>/000-index.md` and `tasks/<person>/001-project-init.md` recording the setup that was just performed (so the work is auditable and the task-gate hook has an active task to gate against). Use task 001 in this repo as the reference example.
- [x] Write step 8: common follow-ups (docflow adopt, first design inputs, trace-matrix init, dhf-manifest, dashboards)
- [x] Write step 9: `/sync-skills` ongoing registry-sync — **expanded to v8.2**: `status`, `check`, `pull` (three-way bucketing + mandatory impact analysis), `push`/`--merge`, `sync`, `prune`, sync-log, safety properties. Cover:
  - Prerequisite: the hitachi checkout must live at the path declared in `project.yml` → `registries[name=hitachi].local_path` (default `../hitachi`). The `sync-skills` script reads this to resolve the registry location.
  - `/sync-skills check` — read-only report of what differs between local `.claude/` and hitachi `origin/main`, in both directions. Safe to run any time.
  - `/sync-skills pull` — fetch upstream and apply approved changes to `.claude/skills` and `.claude/agents`; reconciles `project.yml` allowlists and offers to run new `### setup` actions.
  - `/sync-skills push <files>` — **default is PR-only.** Packages listed local files into a branch on hitachi, commits, pushes, and opens a PR via `gh`. Never merges by default.
  - `/sync-skills push --merge <files>` — **opt-in auto-merge.** When the user explicitly passes `--merge` (or asks for it in natural language like "push and merge"), the skill runs `gh pr merge --squash --delete-branch` after the PR is created and fast-forwards the local hitachi checkout. Document that this bypasses human review and should only be used when the user is confident (e.g., trivial fixes, their own skill authoring).
  - `/sync-skills sync` — full bidirectional flow: pull first, then prompt to push local candidates.
  - How to read `.claude/sync-log.md` and what each entry means.
  - Cover the safety properties: path guard (only `skills/` and `agents/`), `sync-skills` self-excluded from diffs, `push-prep` always branches from fresh `origin/main`, script refuses to push directly to `main`.
- [x] Add a troubleshooting section — table covering jq, SSH auth, task-gate-before-init ordering, the `import-guidance` non-action, `gh` auth, dirty hitachi tree, missing `shared/` dependency, stale sentinels
- [ ] Peer review — walk a colleague through it on a fresh directory and capture friction (only remaining open item)
- [ ] **Scope expansion (2026-04-13):** guide now covers more than mechanical setup. Fill in:
  - Phase 4 — personalize `CLAUDE.md` post-init (device identity, goals, scope statement, demo-vs-real disclaimer) before any task work
  - Phase 6 — an "architecture & component strategy" task the user opens *after* 001 but *before* DHF scaffolding: sketch the system as-deployed, enumerate deployable components, decide DHF topology (top-level vs parent→child), capture decisions as tagged strategy blocks
  - Phase 6.5 — **import applicable references once minimum strategy docs exist.** Gate: architecture and regulatory strategy docs must be populated (at minimum) before this phase runs, because those docs are what identify *which* standards and guidances apply. Then instruct the user to use the `medtech-docs` skill to import references: standards (e.g., `/medtech-docs add-standard IEC 62304`) and FDA guidances (e.g., `/medtech-docs import-guidance <title>`) called out in the regulatory strategy, plus any industry frameworks named in the architecture strategy. Verify each import lands under `docs/external/` with a distilled markdown summary and `[VERIFY]` flags where applicable.
  - Phase 7 — run `/medtech-docs add-dhf` per component derived in Phase 6; verify with dashboard + `/best-practices`
- [x] Resolve open questions — doc location **resolved** (root, sibling of setup.md); Phase-6-as-skill and init-prompts-Phase-4 left explicitly open in-guide

## Draft

Root skeleton lives at `how-to-guide.md` (repo root) as of 2026-04-13. All further authoring happens there; this task tracks the plan and open questions only.

## Authoring session 2026-05-21 — source-of-truth verification + fill-in

Read the two skills the guide documents end-to-end before authoring (per CLAUDE.md "read the skill before planning around it"): `medtech-docs/SKILL.md` and `sync-skills/SKILL.md` (v8.2). Also inspected the live `../hitachi` registry layout. Three skeleton sections were not just empty but **inaccurate** — corrected during fill-in:

<!-- LESSONS LEARNED: documentation-accuracy -->
**Lesson — a how-to guide that documents skill behavior drifts the moment a skill version bumps; verify against `SKILL.md`, never from memory or the skeleton's own prose.**

Three drift findings caught only by reading the SKILLs:
1. **`/medtech-docs init` asks 9 questions, not "~8".** The skeleton's mapping table omitted Q3 *Modules/functions* and Q9 *Primary DHF name* (Q9 is effectively required — "No default"). Both shape the scaffold (modules → design-controls subfolders; DHF name → first `dhfs[]` entry + `docs/project/dhfs/<name>/`).
2. **`/medtech-docs import-guidance <title>` does not exist.** The skeleton's Phase 6.5 invented it. The real surface for pulling FDA guidance is the **`update-external-references`** action (aliases: "import fda guidance", "pull reference guidances") — rubric-driven, copies bundled distilled files from the skill's `references/` into `docs/external/{fda-guidance,standards,industry-frameworks}/`, idempotent, never overwrites. Standards use **`add-standard <name>`**; the **`evaluate <name> required|not-required <rationale>`** action records a not-required decision trail without creating a file.
3. **sync-skills is v8.2** with two actions the skeleton never mentioned — **`status`** (four-surface "are we synced?" health check) and **`prune`** (clears merged `sync/*` branches that accumulate from PR-only pushes). `pull` now runs mandatory three-way blob-history bucketing (UPSTREAM_ADVANCE / LOCAL_AHEAD / BOTH_DIVERGED) so LOCAL_AHEAD files are surfaced as push candidates instead of clobbered — the v8 fix for a 1131-line overwrite incident. Phase 9 must teach the bucketing, not just list the verbs.

**Why:** these are the exact sections a new team will copy-paste verbatim. A wrong action name (`import-guidance`) fails silently as "skill doesn't recognize that"; an undercount of init questions leaves a half-scaffolded tree. **How to apply:** when authoring/refreshing any doc that names a skill action, open that skill's `SKILL.md` Actions section in the same session and reconcile every command string and option against it.
<!-- /LESSONS LEARNED -->

<!-- STRATEGY CONTENT: operations, onboarding-docs -->
**Decision — `how-to-guide.md` stays at repo root, as a sibling of `setup.md`, with a one-line cross-reference between them.** The two docs answer different questions for different audiences: `setup.md` = "I'm joining *this* repo, get me wired up safely" (contributor onboarding + security posture); `how-to-guide.md` = "I have a *new* device program, stand it up the way PDLC_DEMO was built" (project bootstrap using the skills). Keeping both at root mirrors that they're peer entry points; neither belongs under `docs/` (which is the *output* of the process the guide describes, not meta-documentation about it). Resolves the open question in the skeleton. The "should Phase 6 become its own skill" question stays open — flagged in-guide as a future capability, deferred until the prose flow is exercised on a second project.
<!-- /STRATEGY CONTENT: operations -->

This authoring session fills Phases 1, 2, 3 (transcript + table fix), 8, 9 (status/prune/bucketing), 10 (troubleshooting), and resolves the doc-location open question.

## References

| Ref | Description | Location |
|-----|-------------|----------|
| Live example | This project, built by running the same steps | Project root |
| medtech-docs init spec | Canonical behavior of the init action | `.claude/skills/medtech-docs/SKILL.md` |
| Hitachi registry README | Skill install instructions from the source repo | `../hitachi/README.md` |
| Task 001 | Project init task — the work this guide documents | `tasks/ben/001-project-init.md` |
| sync-skills SKILL.md | Spec for the bidirectional registry-sync skill (referenced in step 9) | `.claude/skills/sync-skills/SKILL.md` |
| Sync log | Example of the log format `/sync-skills` writes to | `.claude/sync-log.md` |

## Changelog

- 2026-06-08: Closed Complete via task-doc audit — superseded by ben/069 — setup-guide content overhauled + split into how-to-guide.md / new-project-bootstrap.md / setup.md. Moved to Completed in 000-index.md.
- 2026-05-21 (cont.): Added the missing **post-init verification** content (old step 6) as a "Verify the scaffold" subsection under Phase 3 — five read-only checks (docs/ tree + READMEs, `jq` on `project.yml` DHF path, `settings.json` PreToolUse hook wiring, sentinel render, first dashboard run) plus the "re-run init, don't hand-patch" guidance; updated Flow-at-a-glance. Closed the step 5 / 6 / 7 todos (5 and 7 were already covered by Phases 3 and 5). Remaining open: peer review (needs a colleague on a fresh dir) + the two in-guide open questions (Phase-6-as-skill, init-prompted Phase-4).
- 2026-05-21: Authoring session — filled all skeleton TODOs in `how-to-guide.md` (Phases 1, 2, 8, 9, 10). Verified the documented skills against their live `SKILL.md` and corrected three drift findings (init 9 questions; `import-guidance`→`update-external-references`; sync-skills v8.2 `status`/`prune`/three-way pull). Resolved doc-home open question. Captured a documentation-accuracy lesson and an onboarding-docs strategy decision inline. Status → In Progress; only peer-review todo remains.
- 2026-04-12: Task created.
- 2026-04-12: Added explicit step for creating the first task post-init to capture the setup work, and called out the init-before-task ordering constraint (init installs the task hooks).
- 2026-04-14: Terminology sweep — "sub-DHF" → "DHF" (with top-level vs parent→child) and `add-sub-dhf` → `add-dhf` throughout guide and this task.
- 2026-04-14: Added Phase 6.5 — gate reference import on minimum strategy docs (architecture + regulatory) existing, then instruct user to use `medtech-docs` skill to import applicable standards and FDA guidances called out by those strategy docs.
- 2026-04-13: Scope expanded beyond mechanical setup. Root `how-to-guide.md` skeleton created with 10 phases; added Phase 4 (CLAUDE.md personalization), Phase 6 (architecture/component strategy → drives DHF topology), Phase 7 (add-dhf per component). Open questions captured in the guide.
- 2026-04-12: Added step 9 covering the `/sync-skills` skill — `check`, `pull`, `push` (PR-only default), `push --merge` (opt-in auto-merge), and `sync`. Updated Goals and References accordingly. Retired the separate "registry updates later" bullet (absorbed into step 9).

