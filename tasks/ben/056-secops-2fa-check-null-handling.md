# 056 — SecOps 2FA Check — null-handling fix

**ID**: 056
**Created**: 2026-05-13
**Status**: In Progress
**Created By**: Ben (with Claude)
**Owner**: Ben
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work, update this doc: tick the relevant Todo, add a dated Changelog line naming the concrete artifact, update progress counts.
2. **Phase-end batching is OK; drift-batching is not.** Write at the phase boundary, before the next phase starts.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative.
4. **Resume-ready before any session boundary.** Doc must contain: what was completed with concrete artifacts, in-flight status, priority-ordered next steps with file paths, open questions, the exact `/task` activation command.
5. **Capture strategy + lessons as they happen.** Write decisions and corrected assumptions into this doc in-flight.

Success test: a fresh Claude session, given only this file, can re-enter the work without asking "what were we doing?"

## Goals

Fix a false-negative in the `secops` skill's SessionStart check #1 ("GitHub 2FA"). Surfaced during task ben/055's `/secops check` run.

`hooks/security-assert.sh` check #1 calls `gh api /user --jq '.two_factor_authentication // false'`. For `gh` keyring OAuth tokens (scopes: `admin:public_key, gist, read:org, repo, workflow`), GitHub returns `two_factor_authentication: null` — the field is **not exposed to this token type**. The `// false` jq fallback collapses `null` → `false`, so the check records a **FAIL** ("2FA not enabled on GitHub") when the truth is **"cannot determine 2FA status via this token."**

Per Ben: mark the feature as not-available and **SKIP** the check until there is a working method to verify 2FA — don't FAIL on an undeterminable signal.

## Why this matters

A Critical-severity FAIL on an undeterminable signal is noise that erodes trust in the whole 16-check ledger. It also can't be remediated — the user could have 2FA fully enabled and the check would still FAIL. SKIP is the honest state for "no method to verify."

## Design

Distinguish three API outcomes instead of two:

| `gh api /user` `.two_factor_authentication` | Old behavior | New behavior |
|---|---|---|
| `true` | PASS | PASS (unchanged) |
| `false` (a real, exposed value) | FAIL | FAIL (unchanged — genuine signal) |
| `null` / empty (not exposed to this token) | **FAIL** (via `// false`) | **SKIP** — "GitHub API does not expose 2FA status for this token type; verify manually at github.com/settings/security" |
| API call error | SKIP | SKIP (unchanged) |

This is "skip until there is a method" implemented gracefully: drop the `// false` fallback so `null` stays distinct from `false`. If a future token type or API change starts returning a real boolean, the check resumes working automatically — no hard-disable needed.

## Todos

- [x] Read the full check #1 block in `hooks/security-assert.sh` end-to-end
- [x] Dropped `// false`; added `false` → FAIL and `null`/empty → SKIP branches. SKIP note: "2FA status not exposed by this token — verify manually at github.com/settings/security". Added a 6-line comment explaining the tri-state rationale.
- [x] Bumped skill `version: 7 → 8` + `updated: 2026-05-13` in `SKILL.md` frontmatter
- [x] Added `## Changelog` v8 entry in `README.md`; flagged the missing v6/v7 entries inline (not fixed — out of scope)
- [x] Re-ran `/secops check` on PDLC_DEMO: check #1 now **SKIP** ("2FA status not exposed by this token..."). Critical failures 3 → 2. Overall still FAIL (remaining: #3 email domain, #12 roster — both pre-existing/other-task).
- [x] Sister-project validation ([[feedback_sister_project_compat]]): applied v8 hook to `../../projects/arthrex/pccp/`, busted its SECOPS.md cache, ran — check #1 → SKIP with the new note, no errors, no regression (sister still FAILs on its own unrelated 2 criticals). **Backed up + restored BOTH the hook and the sister's `SECOPS.md`** (the hook run rewrites SECOPS.md — learned from the [[task-051]] discovery-JSON revert mistake).
- [ ] Commit; decide on `/sync-skills push` with user

## Open Questions

- README.md `## Changelog` is missing v6 + v7 entries (the `audit` action shipped in those versions per task ben/041) — out of scope for this task, but should be backfilled separately.
- Is there ANY token scope / auth method that *does* expose `two_factor_authentication`? If so, a future task could make `setup` request it. For now: SKIP + manual-verify note.

## Resume Command

```bash
bash .claude/hooks/task-activate.sh add <SESSION_UUID> 056
```

## Strategy + Lessons (inline captures)

<!-- LESSONS LEARNED: skill-resilience, debuggability -->
**A binary check on a tri-state signal manufactures false negatives.** `gh api /user` returns 2FA status as `true` / `false` / `null`, where `null` means "this token can't see it" — a fundamentally different thing from `false`. The `// false` jq fallback erased that distinction, turning "undeterminable" into "Critical FAIL." Rule of thumb for check/assertion code: if the underlying signal has an "unknown" state, the check must have a SKIP state — never collapse unknown into the negative outcome. Same failure shape as the dhf-manifest multi-match-no-winner bug ([[task-051]]): dropping information at a branch.
<!-- /LESSONS -->

## Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-05-13 | Ben (with Claude) | Task created. Surfaced from ben/055's `/secops check`: check #1 FAILs on `two_factor_authentication: null` because `// false` collapses the undeterminable state into `false`. Plan: drop `// false`, add `null` → SKIP branch with manual-verify note, bump v7 → v8. |
| 2026-05-13 | Ben (with Claude) | **Implemented + validated (secops v7 → v8).** `hooks/security-assert.sh` check #1 now branches on three states: `true` → PASS, `false` → FAIL, `null`/empty → SKIP ("verify manually at github.com/settings/security"), error → SKIP. SKILL.md version bumped, README.md v8 changelog added (+ flagged stale missing v6/v7). PDLC_DEMO re-check: #1 SKIPs, criticals 3 → 2. Sister project (arthrex/pccp) validated clean — both sister hook + SECOPS.md backed up and restored. Not yet committed; `/sync-skills push` decision pending user. |
