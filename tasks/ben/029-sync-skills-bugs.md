# 029 — Sync-Skills Bugs (surfaced during 2026-04-22 pull)

**ID**: 029
**Created**: 2026-04-22
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## Goals

_Fix two bugs in `sync-skills` that surfaced during the 2026-04-22 pull and push the fixes upstream to hitachi. Both are real correctness issues: one can silently delete local files; the other produces a perpetual false-positive that desensitizes users to real drift._

- Bug A: `pull-file` reads from stale hitachi working tree
- Bug B: `check` misreports symlinked files as perpetually `UPSTREAM_NEWER`
- Validate fixes against PDLC_DEMO and sister-project `../arthrex-pccp/`
- Push upstream via `/sync-skills push --merge`

## Bug A — `pull-file` reads from stale hitachi working tree (can silently delete local files)

**Observed** (2026-04-22 pull, commit `219d46d`):

Local hitachi checkout was on a stale commit (`e027eba`, 34 commits behind `origin/main`). `sync.sh check` correctly fetched `origin/main` and reported 19 `UPSTREAM_NEWER` files plus 1 `UPSTREAM_ONLY`. When we ran `sync.sh pull-file` on each, 13 of the 20 came back as **`deleted-locally (upstream removed)`** — and the script duly `rm`'d them from the project.

Those files were NOT actually removed in upstream — they still existed at `origin/main`. They were just missing from the stale local working tree.

**Root cause** — in `.claude/skills/sync-skills/scripts/sync.sh`, `cmd_pull_file()` copies from `$HITACHI/$rel` (the working tree). If the working tree is behind `origin/main`, files that were added/restored on `origin/main` but not yet pulled into the hitachi checkout look "missing" to `pull-file`, so it takes the `elif [[ -e "$dst" ]]; then rm "$dst"` branch and deletes the local copy.

**Recovery** — fast-forward hitachi (`git -C <path> pull --ff-only`), then re-run `pull-file` for each affected path.

**Fix options:**
1. **Pull from `origin/main` directly** — `git -C "$HITACHI" show "origin/main:$rel"` and write the blob, avoiding the working-tree read entirely. Symmetric with `cmd_check` which already uses `origin/main`.
2. **Refuse if behind** — detect `_hitachi_behind > 0` at the start of `pull-file` and error out with "hitachi checkout is N commits behind origin/main; fast-forward first or run `/sync-skills sync` which auto-updates".
3. **Auto-fast-forward if clean** — on every `pull-file`, run `git -C <path> pull --ff-only` first when the working tree is clean. Slightly more invasive; surprises users who want the hitachi checkout to stay parked.

**Recommendation:** option 1 (read from `origin/main` blob) — matches `check` behavior and is fully inert to working-tree state. Handle symlinks by detecting `git ls-tree` mode `120000` and writing as symlink rather than regular file.

## Bug B — `check` misreports symlinks as perpetually `UPSTREAM_NEWER`

**Observed** (2026-04-22 pull, after all files pulled cleanly):

`sync.sh check` still reports `UPSTREAM_NEWER agents/project-secops.md` even though both upstream and local versions are identical symlinks (`agents/project-secops.md -> ../skills/secops/agents/project-secops.md`), pointing to identical target files.

**Root cause** — in `_walk_registry_tree()`:

```bash
upstream_blob="$(git -C "$HITACHI" show "$upstream_ref:$f" 2>/dev/null | shasum -a 1 | cut -d' ' -f1)"
local_blob="$(shasum -a 1 "$LOCAL_BASE/$f" | cut -d' ' -f1)"
```

When `$f` is a symlink, `git show` returns the **symlink target path as text** (e.g., the 41-byte string `../skills/secops/agents/project-secops.md`). But `shasum` on the local file **dereferences the symlink** and hashes the pointed-to file's **content** (6.7KB of markdown). The two shasums can never match, so the file is perpetually flagged as drift.

The prior sync-log entry (2026-04-20) already notes this as a "false-positive drift from sync.sh comparing across registries' symlinks" — so the bug has been papered over once already.

**Fix options:**
1. **Mode-aware comparison** — use `git ls-tree` to detect symlink mode (`120000`) on the upstream side, and compare via `readlink` on the local side. If both are symlinks with the same target string → equal.
2. **Hash the resolved file on both sides** — `shasum` following symlinks on both sides. Requires knowing where upstream would resolve to (doable: upstream is symlink in `$HITACHI` so `readlink -f` on the working-tree copy gives the right absolute path).
3. **Git-plumbing blob hash** — compute git's blob hash of the local file (via `git hash-object`) and compare to `git -C "$HITACHI" rev-parse origin/main:$f`. Git's hash-object respects mode (blob vs symlink), so they match iff symlink-vs-symlink and target-vs-target.

**Recommendation:** option 3 (git blob hash on both sides) — also fixes option-1 ambiguity when one side is a symlink and the other is a regular file with identical target text. Matches git's own notion of "same file."

## Todos

- [ ] Reproduce Bug A in a scratch checkout (stash hitachi checkout to older commit, run pull-file on a file that was added in a later commit, observe silent delete)
- [ ] Reproduce Bug B (confirm symlink comparison mechanism)
- [ ] Implement Bug A fix (read from `origin/main` blob, handle symlinks via `ls-tree` mode)
- [ ] Implement Bug B fix (git blob hash on both sides via `git hash-object` + `git rev-parse`)
- [ ] Regression tests — script self-test or scripted scenario that proves both fixes
- [ ] Bump `.claude/skills/sync-skills/VERSION` + changelog entry with `**Post-update:**` note
- [ ] Sister-project validation against `../arthrex-pccp/`
- [ ] `/sync-skills push --merge` to hitachi

## Changelog

- 2026-04-22: Task created after both bugs surfaced during the 2026-04-22 pull. Bug A caused a silent-delete panic that was only caught because the broken docflow hook already had my attention; without that, I'd have committed the deletes. Bug B has existed at least since 2026-04-20 (papered over in that pull's log entry) — treating it as benign was a mistake because it trains users to ignore `check` output.
- 2026-04-28: **Bug B fixed upstream (v6).** Resurfaced during the 2026-04-28 broad pull when `agents/project-secops.md` showed `UPSTREAM_NEWER` immediately after a successful pull. Patched `cmd_check()` to detect local symlinks and hash the link target text. PR #96 merged at hitachi `a45c928`.
- 2026-04-28: **v6 regression caught + fixed via v7.** Once v6 was active, 28 spurious `UPSTREAM_NEWER` entries surfaced on top-level advisor symlinks (`agents/clinical-affairs.md` etc.) that resolve to identical content of upstream regular files. v6's "always hash link text when local is a symlink" branch broke the canonical mixed-mode case (local symlink → upstream regular file). v7 selects the local-side hash strategy by *upstream* mode (read via `git ls-tree`): upstream `120000` AND local symlink → hash link text; otherwise → hash resolved content. Verified zero false positives against PDLC_DEMO. PR #97 merged at hitachi `3586493`.
- 2026-04-28: **Bug A fixed upstream (v8).** `cmd_pull_file()` previously copied from `$HITACHI/$rel` (working tree) and `rm`'d the local copy when missing. With a stale checkout, files added on `origin/main` looked missing → silent local delete. v8 reads via `git ls-tree origin/main` + `git show origin/main:<path>`, fetches origin first, and restores file-mode fidelity (symlinks stay as symlinks via `ln -s`, executable scripts get `chmod +x` based on mode `100755`). Verified against four scenarios including the stale-checkout regression case (file present at `origin/main` but moved out of working tree → pulled successfully, no delete). PR #98 merged at hitachi `a6958a0`. Both bugs now closed.

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 6,
    "todos": [
      {
        "todo": "Sync-skills bugs (stale-delete + symlink)",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 12,
          "max": 30
        },
        "confidence": "low",
        "basis": "fixed 3 sync-skills bugs across PRs v6/v7/v8"
      }
    ]
  }
}
```
