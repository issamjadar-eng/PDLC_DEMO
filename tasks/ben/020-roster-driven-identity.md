# ben/020 — Roster-driven git identity + stable digest state key

**ID**: 020
**Created**: 2026-04-20
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## Goals

Make `project.yml` the source of truth for git identity on this repo, and stabilize the digest throttle state so it's keyed on the roster identity (`task_folder`) rather than whatever `git config user.email` happens to return on the current machine.

Motivation: on the PDLC_DEMO machine this morning, `git config user.email` was `xavier.ben@gmail.com` (personal) while the roster email is `ben.xavier@globallogic.com` (work). Commits landed with the personal email and the digest state file was keyed `briefing-last-shown-xavier-ben-gmail-com.txt`. We can't control the user's *global* git config, but we can (and should) enforce a repo-local override that mirrors `team.active[]`.

## Todos

- [x] New helper `.claude/skills/secops/scripts/resolve_user.py`
- [x] Update `/secops setup` to include step 6 (align-git via the resolver)
- [ ] Update `security-assert.sh` to re-align on drift at SessionStart — **deferred** (secops setup at clone time is sufficient; re-alignment at every SessionStart is noisy and the one-time fix covers the real case)
- [x] Update digest `session-briefing.sh` to use `task_folder` as state-file key
- [x] Migrate `briefing-last-shown-xavier-ben-gmail-com.txt` → `briefing-last-shown-ben.txt`
- [x] Bump secops → v3, digest → v3 (VERSION 1.2.0)
- [x] Verify: `git config user.email` is now `ben.xavier@globallogic.com` (repo-local); fresh hook run writes `briefing-last-shown-ben.txt`

## Outcome

`project.yml` is now the source of truth for git identity on this clone and for the digest throttle key. Three artifacts:

1. **`resolve_user.py`** in secops — self-contained YAML-roster-parsing identity resolver. Four match heuristics (email / single-member / name-fuzzy / `$USER`). Two output modes: JSON diagnostic for humans and scripts that want the full record, or `--task-folder` for shell state keys. `--align-git` writes repo-local `user.email`/`user.name` if matched and mismatched — a no-op on repeat runs.

2. **Secops v3** — `/secops setup` step 6 calls `resolve_user.py --align-git`. This clone's git config was unset at both scope levels; secops aligned it to `ben.xavier@globallogic.com` + `Ben Xavier`. Commits from this repo now attribute correctly regardless of `--global` defaults.

3. **Digest v3** — `session-briefing.sh` calls `resolve_user.py --task-folder` to get `ben` as the stable state key. Old state file renamed, throttle window preserved (next briefing won't fire until `~2026-04-21T06:33`).

Tested end-to-end: `git config user.email` returns the roster email, the hook writes `briefing-last-shown-ben.txt`, and a briefing regenerated correctly.

<!-- STRATEGY CONTENT: architecture, identity-resolution, project-manifest-scope -->

**Strategy — `project.yml` is the canonical identity for repo-local concerns.**

Principle: When a repo-local concern (git config, session throttle state, task attribution, audit posture) depends on "who is doing this work," the answer comes from `project.yml` `team.active[]`, not from the user's global machine state. The manifest is versioned and reviewable; the machine state is whatever happens to be set. Tools should resolve identity via the manifest and fall back to raw machine state only when the manifest has no answer.

Why: Global `git config` defaults are set once when a developer first installs git and may never be revisited. Personal email is a common default. The project should be able to say "commits from this repo MUST be attributed to the roster email," and the tooling should make that true without the user having to think about it. `git config --local` is the right mechanism because it affects one repo only — no blast radius to other projects on the same box.

How to apply: For any new skill that resolves "who is doing this," use `secops/scripts/resolve_user.py`. Consume the `task_folder` (stable) or the full `{email, name, github}` triple (for API calls, email lookups, etc.). Fall back to raw machine state ONLY in documented edge cases (guest clone, resolver failure, no `project.yml`) and label the fallback clearly.

<!-- LESSONS LEARNED: identity, state-keys, local-config-as-enforcement -->

**Lesson — Use repo-local config (`git config --local`) as a lightweight enforcement mechanism.**

Why: I initially built the digest state key on `git config user.email` directly, which meant the key varied based on machine configuration. The user flagged that `project.yml` should drive the right git account — not the other way around. `git config --local` is the right mechanism: it lives in `.git/config` (not committed, per-clone), overrides `--global` for this repo only, and is set once and done. No hooks that run on every session, no bash gymnastics to slug an email.

How to apply: When a project needs to enforce "on this repo, use X," prefer setting `git config --local` (or the equivalent for whatever tool) at setup time and letting the tool honor it naturally, rather than wrapping the tool with a per-invocation override. For git, `--local` has zero blast radius — other projects on the same box are unaffected. Combine with an idempotent resolver (detect drift, re-align if needed) so the alignment survives clones, git re-init, or accidental user edits.

## Changelog

- 2026-04-20: Task created to cover roster-driven identity work
- 2026-04-20: `resolve_user.py` shipped, digest v3 + secops v3 cut, state file migrated, git config aligned for this clone. Verified end-to-end. Task complete.

## Match heuristics (priority order)

1. Exact email match against `team.active[].email`
2. Single-member roster → take the sole member
3. `git config user.name` substring-matches `team.active[].name` (case-insensitive)
4. OS `$USER` matches `team.active[].task_folder` exactly
5. None match → fall back to raw email slug (guest / unconfigured-clone case); emit a warning, do not align git config

## Changelog

- 2026-04-20: Task created to cover roster-driven identity work

