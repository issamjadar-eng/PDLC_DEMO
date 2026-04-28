# sync-skills — Design & Architecture

This document is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Best Practices

<!-- Read by /best-practices skill to audit sync hygiene -->

| Check | How to Verify | Severity |
|-------|--------------|----------|
| Sync log exists | `.claude/sync-log.md` exists | Recommended |
| Sync log has a recent entry | Last entry in `.claude/sync-log.md` is within 30 days | Recommended |
| No silent divergence | Running `sync.sh check` returns zero `UPSTREAM_NEWER` entries, OR those entries are documented in the sync log with a rationale (local customization kept intentionally) | Recommended |
| Hitachi path resolves | `sync.sh hitachi-path` exits 0 and points at an existing git repo | Required |
| Script is executable | `.claude/skills/sync-skills/scripts/sync.sh` has the executable bit | Required |
| Allowlist matches installed | Every skill directory under `.claude/skills/` is listed in `project.yml` `security.approved_skills` (and vice versa) | Required |

## Changelog

- 8 (2026-04-28): **`pull-file` now reads from `origin/main`, not the working tree (fixes silent-delete bug).** When the hitachi checkout is behind `origin/main` (e.g., never `git pull`'d after the last `check`-driven `fetch`), the previous `pull-file` implementation looked for the source at `$HITACHI/$rel` in the working tree. Files that had been *added* on `origin/main` but not yet pulled into the local checkout looked "missing" — and the fallback branch `rm`'d the local copy on the assumption the file had been deleted upstream. This silently destroyed local work. Now reads via `git ls-tree origin/main` / `git show origin/main:<path>` (committed state, independent of working-tree freshness) and `fetch`es origin/main first so a standalone `pull-file` invocation doesn't depend on a prior `check`. Also restores file-mode fidelity that the old `cp` provided implicitly: symlinks are recreated as symlinks (not flattened to a regular file containing the link target text), and executable scripts (mode `100755`) get `chmod +x` after content write. Discovered in PDLC_DEMO during the 2026-04-22 pull where 13 of 20 files came back as "deleted-locally" against a stale checkout.
  **Post-update:** No user action. Future `pull-file` invocations are stable against stale hitachi checkouts and preserve symlinks + executable bits.

- 7 (2026-04-28): **Mixed-mode symlink-aware comparison (corrects v6 regression).** v6's "always hash link target text when local is a symlink" branch fixed the symmetric symlink-vs-symlink case but regressed the canonical "local installs an agent as a symlink, registry stores it as a regular file" case (the standard skill-symlink pattern). After v6, every such file showed `UPSTREAM_NEWER` even when fully in sync. Now the local-side hash strategy is selected by *upstream* mode (read via `git ls-tree`), not local symlink-ness alone: upstream `120000` (symlink) → hash local link target text; upstream `100644`/`100755` (regular) → hash local resolved content (`sha1sum`/`shasum` already follows symlinks). This matches what git actually stored on each side and handles all four (symlink/regular × upstream/local) permutations correctly. Verified against PDLC_DEMO post-v6: 28 spurious `UPSTREAM_NEWER` entries on `agents/*.md` (top-level advisor symlinks resolving to identical content) drop to 0; all genuine drift is still flagged.
  **Post-update:** No user action. Next `check` will report only real drift; the v6 regression on mixed-mode symlinks is gone.

- 6 (2026-04-28): **Symlink-aware `check` content compare.** `check` previously hashed upstream blobs via `git show ref:path` (which emits the link target text for symlinks) but hashed local paths with `sha1sum`/`shasum` (which follows symlinks and hashes the resolved file). The asymmetry produced spurious `UPSTREAM_NEWER` flags for every symlinked agent or hook even when the link target was identical — perpetually surfacing files that were actually in sync. Now detects local symlinks with `[[ -L ... ]]` and hashes the link target text (no trailing newline) to mirror how git stores the symlink blob upstream. Hash equality reflects link-target equality for symlinks and file-content equality for regular files. Also factored the hasher choice (`sha1sum` vs `shasum -a 1`) into a single variable so the comparison logic isn't duplicated.
  **Post-update:** No user action. The next `check` will report fewer false-positive `UPSTREAM_NEWER` entries — specifically, top-level agent symlinks that resolve to identical content will now correctly drop out of the diff.

- 5 (2026-04-16): **Portable SHA-1 in `check`.** Script previously used `shasum -a 1` exclusively (a Perl script that ships on macOS and Debian/Ubuntu but is missing from minimal Linux images like Alpine and some slim Docker bases). On systems without Perl or `shasum`, every `UPSTREAM_NEWER` diff would fail and skip silently. Switched to a prefer-`sha1sum` runtime detect (GNU coreutils, always on Linux), falling back to `shasum -a 1` when `sha1sum` is unavailable (covers macOS default + Debian/Ubuntu without coreutils). Content equality is the only property used, so either hash family is equivalent. Discovered during task 067 cross-platform audit.
  **Post-update:** No user action. `check` continues to work byte-for-byte on mac + WSL Ubuntu (same output), and now also works on minimal Linux bases.
- 4 (2026-04-15): Local file walk now uses `git ls-files -co --exclude-standard` instead of raw `find`, so `.gitignore` is honored. Prevents build artifacts (`__pycache__/`, `*.pyc`, `.DS_Store`, virtualenv trees) from polluting the diff report or from sneaking into a `push-stage` copy. Upstream walk was already git-based, so this makes the two walks symmetric. (Backfilled entry — the change landed in the script upstream but wasn't recorded in the changelog at the time.)
  **Post-update:** No user action. The new walk is a strict subset of the old one — anything that showed up before still shows up, but nothing in `.gitignore` will leak through.
- 3 (2026-04-13): `pull` now performs mandatory Project Impact Analysis (new Step 5b) after every successful file pull. For each pulled file, Claude reads the updated changelog and any `**Post-update:**` annotations, then produces a Project Impact Report covering setup re-runs, template regeneration, best-practices table diffs, frontmatter/schema changes, terminology renames, and hook changes. Applies to single-file pulls too — silence is not acceptable. Rationale: previously, a pull could land a new-behavior skill version without Claude surfacing what the project needed to do to align. Now alignment analysis is part of what pull *means*.
  **Post-update:** No user action. The new Step 5b executes automatically on the next `/sync-skills pull` or `/sync-skills sync`.
- 2 (2026-04-12): Added opt-in `--merge` flag to `push`. When passed, the skill calls `gh pr merge --squash --delete-branch` after the PR is created, then `git pull --ff-only` in the local hitachi checkout so it stays in sync. Default remains PR-only — never merge without explicit request.
- 1 (2026-04-12): Initial version. Four actions: `check`, `pull`, `push <files>`, `sync`. Script primitives: `check`, `pull-file`, `push-prep`, `push-stage`, `push-finalize`, `hitachi-path`, `hitachi-head`. Reads `registries[name=hitachi].local_path` from `project.yml` with `../hitachi` fallback. Excludes `sync-skills` from diffs. Push flow always opens a PR.
