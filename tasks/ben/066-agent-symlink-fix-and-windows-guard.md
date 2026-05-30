# 066 — Agent Symlink Fix + sync-skills Windows Guard + Rule

**ID**: 066
**Created**: 2026-05-30
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — converted/adopted doc, committed change, launched batch, completed phase, decision, discovered blocker, design pivot — update this task doc: tick the relevant Todo checkbox, add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker), update any progress counts/tables in Goals.
2. **Phase-end batching is OK; drift-batching is not.** Write at phase boundaries, not "later."
3. **A commit is not a substitute.** Git records code; this doc records the project narrative.
4. **Resume-ready before any session boundary.** Doc must contain: (a) what was completed this session with concrete artifacts, (b) status of in-flight work, (c) priority-ordered next steps with file paths, (d) open questions, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** Use the inline HTML-comment markers.

## Goals

Three discrete, related deliverables triggered by upstream commit `07574e9 "vlad's best commit"` (author `gitneod-source <gitneod@gmail.com>`, 2026-05-26) which corrupted 14 `.claude/agents/*.md` symlinks on `origin/main` by replacing the short relative-path targets with the full agent markdown content while preserving filemode 120000 — making `git pull --ff-only` fail on Linux/macOS because the OS refuses to create a 5KB-target symlink.

- **G1 — Restore the symlinks on `origin/main`** via a corrective PR so teammates can pull cleanly. Rewrite the 14 agent index entries to use the pre-vlad blobs (from `71a5ef7`), keeping mode 120000 + short relative-path targets.
- **G2 — Fix the `sync-skills` Windows blind spot at the source.** `sync.sh:292` uses `[[ -L "$path" ]]` to detect symlinks; on Windows clones (`core.symlinks=false`) git-tracked symlinks appear as plain text files containing the path string, so `-L` returns false. The script then takes the regular-file branch and happily overwrites the "fake symlink" with upstream content. Push the fix upstream to the hitachi registry.
- **G3 — Document the Windows / `core.symlinks=false` trap as a project rule** so teammates working directly against the hitachi registry repo (or any sister project) on Windows know to set `core.symlinks=true` before cloning, OR avoid editing 120000-mode entries. Add a CLAUDE.md / `.claude/rules/` pointer.

<!-- STRATEGY CONTENT: architecture, operations -->
**Architecture decision — agents stay as registry-owned symlinks.** Vlad's commit replaced 14 symlinked agents with embedded older-version copies, which would have (a) disconnected them from the skill registry source-of-truth and (b) regressed them to a pre-`canonical_roles`, pre-`file-locator` MCP capability set. The reversion to symlinks is not just a Windows-OS workaround — it preserves the design that lets `/sync-skills` updates to a skill (e.g., `advisors`) propagate to every advisor agent without separately committing N copies. The lesson generalizes: any file in `.claude/agents/` whose content lives in a skill should be a symlink, not a copy, and the `sync-skills` precheck must enforce that.
<!-- /STRATEGY CONTENT -->

<!-- LESSONS LEARNED: tooling, cross-platform -->
**Windows `core.symlinks=false` is a silent corruption vector for any cross-OS shared repo with git-tracked symlinks.** Git on Windows defaults to storing symlinks as plain text files containing the target path string, but **keeps the index mode at 120000**. Any tool that (a) reads the file as text and (b) writes new content to that path will commit the new content under the preserved 120000 mode — producing a "symlink" whose target string is arbitrary bytes. Receiving systems (Linux/macOS) then refuse to check it out. The bug is invisible on the Windows side (file looks fine, commit succeeds, push succeeds) and only surfaces downstream. Tools operating on shared repos with symlinks must precheck `core.symlinks` + scan for tracked 120000 entries and refuse / warn when both conditions hold.
<!-- /LESSONS LEARNED -->

## Todos

### G1 — Restore agent symlinks on origin/main — DONE 2026-05-30
- [x] Capture pre-vlad blob SHAs from `71a5ef7` for all 14 agent paths
- [x] Build fix commit via plumbing (`read-tree origin/main` → `update-index --cacheinfo 120000,<blob>,<path>` × 14 → `write-tree` → `commit-tree -p origin/main`) — never touches WT
- [x] Push fix commit `bc2f698` as branch `fix/restore-agent-symlinks`
- [x] Open PR #11 with full root-cause body
- [x] Auto-merge (`gh pr merge 11 --merge --delete-branch`) — merge commit `54d7741`
- [x] Local `git pull --ff-only` to `54d7741` succeeded
- [x] Restore 14 agent symlinks in WT (`git checkout -- .claude/agents/`) — all `readlink` correctly, files resolve
- [x] Resolve `tasks/ben/SECOPS.md` stash conflict — kept both 2026-05-22 and 2026-05-26 history entries; Last Check shows 2026-05-26 (latest)

### G2 — Fix sync-skills Windows blind spot upstream — DONE 2026-05-30
- [x] Read `sync-skills/SKILL.md` end-to-end per the project's "read the skill before planning" rule
- [x] Add `_is_tracked_symlink` helper (consults git index mode, not filesystem `-L`)
- [x] Add `_read_symlink_target` helper (handles real symlinks + Windows-style materialization; refuses multiline / >4096 bytes)
- [x] Add `_smart_content_hash` helper (preserves v8.1 resolved-content semantics; resolves Windows-materialized symlink targets manually)
- [x] Add `_sha1_stdin` helper (portable sha1sum/shasum)
- [x] Fix `cmd_analyze` to use `_is_tracked_symlink` instead of `[[ -L ]]`
- [x] Fix `_walk_registry_tree` to use `_smart_content_hash` for resolved-content compare
- [x] Add `cmd_push_stage` hard guard — refuses to stage corrupt-symlink content with exit 8 and remediation message
- [x] New `tests/test_windows_symlink_guard.sh` — 4 cases, all pass
- [x] Re-run all existing test suites — 4 v8.1 symlinks + 11 status + 10 three_way_pull + 15 prune = 40 prior assertions all still green (44 total)
- [x] Bump SKILL.md version 8.2 → 8.3; add changelog entry in README
- [x] Push to hitachi via `sync.sh push-prep`/`push-stage`/`push-finalize` + `gh pr create`; PR #185 squash-merged at `8ebe1f2`
- [x] Append sync-log entry — local is already at v8.3 (authored against local first), no pull-back needed

### G3 — Add Windows-symlink rule — DEFERRED 2026-05-30
- [~] User scope decision: skip the rule. Reasoning: G1 restored the corrupted state, G2 hard-blocks the bug at the source via `cmd_push_stage` exit-8 refusal — a CLAUDE.md rule would add another context layer without changing the failure surface, since corrupted symlinks now cannot leave a Windows clone via `/sync-skills push` regardless of whether the user has seen the rule. Re-open if Windows-cloner teammates report friction the `cmd_push_stage` error message doesn't address.

### G4 — Resume original ask
- [ ] Run `/sync-skills check` to perform the originally requested skill sync assessment
- [ ] Determine what action is needed for any pending skill updates

## Working Notes

**Root-cause diagnosis (2026-05-30, in chat):**
- Vlad's commit `07574e9` diff on `.claude/agents/clinical-affairs.md`: blob `d0f048d` (path string) → blob `d2ec8e7` (5KB markdown), mode unchanged 120000.
- All 14 agent paths follow the same pattern. 13 pointed at `../skills/advisors/agents/<name>.md`; `project-secops.md` pointed at `../skills/secops/agents/project-secops.md`.
- Vlad's blob content is an **older** version of the advisors agents (pre-`canonical_roles` tier model, missing `Agent` + `mcp__file-locator__locate` tools). Compared blob `d2ec8e7` vs current `.claude/skills/advisors/agents/clinical-affairs.md`: 383 diff lines.
- `sync-skills/scripts/sync.sh:292` uses `[[ -L "$path" ]]` to branch symlink vs regular file. On Windows with `core.symlinks=false`, `-L` returns false because git stored the symlink as a text file. The regular-file branch runs `git hash-object` on the file (containing the path string), sees it differs from the upstream agent markdown, marks UPSTREAM_NEWER, and applies the overwrite. Index mode 120000 is preserved.

**Local pre-fix state (2026-05-30):**
- Branch: `main` at `71a5ef7`; `origin/main` at `9c87667` (10 commits ahead).
- Working tree: 4 files (`.gitignore`, `how-to-guide.md`, `project.yml`, `tasks/ben/002-how-to-guide-project-setup.md`) already match `origin/main` content — partial pull artifact from before this session.
- Untracked `GEMINI.md`, `assets/client-pdlc/client-pdlc-presentation-v1.html`, `claude-capabilities.xlsx` all match `origin/main` blobs.
- `tasks/ben/SECOPS.md` change (secops check log 2026-05-26) stashed as `stash@{0}`.

## Changelog
See [README.md](README.md) for version history.

- 2026-05-30: Task created. Diagnosis captured. G1–G4 plan staged. Activating gate.
- 2026-05-30: **G1 DONE.** Fix commit `bc2f698` built via plumbing; PR #11 merged at `54d7741`; local `main` pulled cleanly; 14 agent symlinks restored and resolving; SECOPS conflict resolved preserving both 2026-05-22 and 2026-05-26 history entries.
- 2026-05-30: **G2 DONE.** sync-skills v8.2 → v8.3 — three new helpers (`_is_tracked_symlink`, `_read_symlink_target`, `_smart_content_hash`) + `_sha1_stdin`; `cmd_analyze` and `_walk_registry_tree` use index-based detection; `cmd_push_stage` hard-guards corrupt-symlink content with exit 8 + remediation message. New `tests/test_windows_symlink_guard.sh` (4 cases, all pass). All 40 prior assertions still green. Pushed to hitachi as PR #185, squash-merged at `8ebe1f2`. Sync-log entry recorded.
- 2026-05-30: **G3 DEFERRED** per user scope decision — G2's push-stage hard refusal closes the failure surface regardless of whether a Windows cloner has seen a CLAUDE.md rule, so an additional rule was deemed redundant context. Re-open if user-friction reports surface that the inline `cmd_push_stage` error message doesn't address.
