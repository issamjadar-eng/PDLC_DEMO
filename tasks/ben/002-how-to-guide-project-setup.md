# 002 — How-To Guide: Repeating Project Setup

**ID**: 002
**Created**: 2026-04-12
**Status**: Not Started
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

- [ ] Pick a location for the guide — likely `docs/internal/` or a top-level `HOW-TO.md` (decide when starting)
- [ ] Write step 1: prerequisites (git SSH to `GlobalLogic-a-Hitachi-Company/hitachi`, `jq` installed, Claude Code running)
- [ ] Write step 2: cloning `hitachi` and copying `skills/` + `agents/` into `.claude/`
- [ ] Write step 3: initializing the target repo (git init, remote, gitignore)
- [ ] Write step 4: running `/medtech-docs init` — enumerate the 8 project-context questions with guidance on each answer
- [ ] Write step 5: what the init produces (folder tree, READMEs, project.yml, CLAUDE.md, standards/frameworks selection, hook wiring)
- [ ] Write step 6: post-init verification (`docs/` tree check, `project.yml` inspection, `settings.json` hook check, first `/medtech-docs dashboard` run)
- [ ] Write step 7: **create the first task to capture the setup work itself.** Call out the ordering: `/medtech-docs init` must run *before* any `task` commands, because init is what installs and wires the `task` skill's hooks. Once init completes, create `tasks/<person>/000-index.md` and `tasks/<person>/001-project-init.md` recording the setup that was just performed (so the work is auditable and the task-gate hook has an active task to gate against). Use task 001 in this repo as the reference example.
- [ ] Write step 8: common follow-ups (populating standards, mapping sample docs, adding team members, registering additional skills)
- [ ] Write step 9: **introduce the `/sync-skills` skill as the ongoing registry-sync mechanism.** Cover:
  - Prerequisite: the hitachi checkout must live at the path declared in `project.yml` → `registries[name=hitachi].local_path` (default `../hitachi`). The `sync-skills` script reads this to resolve the registry location.
  - `/sync-skills check` — read-only report of what differs between local `.claude/` and hitachi `origin/main`, in both directions. Safe to run any time.
  - `/sync-skills pull` — fetch upstream and apply approved changes to `.claude/skills` and `.claude/agents`; reconciles `project.yml` allowlists and offers to run new `### setup` actions.
  - `/sync-skills push <files>` — **default is PR-only.** Packages listed local files into a branch on hitachi, commits, pushes, and opens a PR via `gh`. Never merges by default.
  - `/sync-skills push --merge <files>` — **opt-in auto-merge.** When the user explicitly passes `--merge` (or asks for it in natural language like "push and merge"), the skill runs `gh pr merge --squash --delete-branch` after the PR is created and fast-forwards the local hitachi checkout. Document that this bypasses human review and should only be used when the user is confident (e.g., trivial fixes, their own skill authoring).
  - `/sync-skills sync` — full bidirectional flow: pull first, then prompt to push local candidates.
  - How to read `.claude/sync-log.md` and what each entry means.
  - Cover the safety properties: path guard (only `skills/` and `agents/`), `sync-skills` self-excluded from diffs, `push-prep` always branches from fresh `origin/main`, script refuses to push directly to `main`.
- [ ] Add a troubleshooting section (missing `jq`, SSH auth failure, hook registration conflicts, `gh` not authenticated for sync-skills push, dirty hitachi working tree blocking push)
- [ ] Peer review — walk a colleague through it on a fresh directory and capture friction

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

- 2026-04-12: Task created.
- 2026-04-12: Added explicit step for creating the first task post-init to capture the setup work, and called out the init-before-task ordering constraint (init installs the task hooks).
- 2026-04-12: Added step 9 covering the `/sync-skills` skill — `check`, `pull`, `push` (PR-only default), `push --merge` (opt-in auto-merge), and `sync`. Updated Goals and References accordingly. Retired the separate "registry updates later" bullet (absorbed into step 9).
