#!/usr/bin/env bash
# sync.sh — Mechanical primitives for the /sync-skills skill.
#
# Subcommands:
#   check [--analyzed]             Diff hitachi vs local, both directions. Read-only.
#                                  --analyzed enriches each UPSTREAM_NEWER row with a
#                                  recommendation (UPSTREAM_ADVANCE / LOCAL_AHEAD /
#                                  BOTH_DIVERGED / UNDETERMINED) + a one-line summary.
#   analyze <relpath>              For ONE UPSTREAM_NEWER path, run the three-way blob-history
#                                  probe and print a single line:
#                                      STATUS<TAB>PATH<TAB>RECOMMENDATION<TAB>SUMMARY
#                                  Used by `check --analyzed` and the `pull` action.
#   pull-file <relpath>            Copy one file from hitachi → local (or rm if deleted upstream).
#   push-prep <branch>             Reset hitachi checkout to origin/main, checkout new branch.
#   push-stage <relpath>           Copy one file from local → hitachi.
#   push-finalize <commit-msg>     git add + commit in hitachi, push the current branch.
#   hitachi-path                   Print the resolved hitachi path (from project.yml local_path, else ../hitachi).
#   hitachi-head                   Print the current hitachi HEAD commit hash (short).
#   skill-version <skill-path>     Print the `version:` value from a SKILL.md's frontmatter.
#   post-update-actions <skill-path> <from-version> <to-version>
#                                  Read the SKILL.md changelog, find version entries in (from, to],
#                                  and print any `**Post-update:**` blocks they contain. Used by
#                                  `pull` to surface required user actions after applying updates.
#                                  Paths are relative to the local `.claude/` base (e.g., `skills/task`).
#
# All paths passed in are relative to the registry root: `skills/foo/bar.md` or `agents/foo.md`.
# The script refuses to touch anything outside `skills/` and `agents/`.

set -euo pipefail

# ─── Path resolution ───────────────────────────────────────────────────────

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
LOCAL_BASE="$PROJECT_DIR/.claude"

_resolve_hitachi() {
  # Read local_path from project.yml under the hitachi registry entry.
  # Falls back to ../hitachi if absent.
  local path
  path="$(
    awk '
      /^  - name: hitachi$/ { in_block=1; next }
      in_block && /^  - name:/ { in_block=0 }
      in_block && /^    local_path:/ {
        sub(/^    local_path:[[:space:]]*/, "")
        sub(/[[:space:]]*#.*$/, "")
        print
        exit
      }
    ' "$PROJECT_DIR/project.yml" 2>/dev/null || true
  )"
  if [[ -z "$path" ]]; then
    path="../hitachi"
  fi
  if [[ "$path" != /* ]]; then
    path="$PROJECT_DIR/$path"
  fi
  # Normalize
  (cd "$path" 2>/dev/null && pwd) || { echo "ERROR: hitachi path not found: $path" >&2; exit 1; }
}

HITACHI="$(_resolve_hitachi)"

_assert_safe_path() {
  local p="$1"
  case "$p" in
    skills/*|agents/*) : ;;
    *) echo "ERROR: refusing to touch path outside skills/ or agents/: $p" >&2; exit 2 ;;
  esac
  case "$p" in
    *..*) echo "ERROR: refusing path with '..': $p" >&2; exit 2 ;;
  esac
}

_hitachi_clean() {
  [[ -z "$(git -C "$HITACHI" status --porcelain)" ]]
}

# ─── Subcommands ───────────────────────────────────────────────────────────

cmd_hitachi_path() { echo "$HITACHI"; }
cmd_hitachi_head() { git -C "$HITACHI" rev-parse --short HEAD; }

# Print the `version:` value from a SKILL.md frontmatter block.
# Usage: skill-version <skill-path>   where <skill-path> is `skills/<name>`
# If the file is missing or the frontmatter has no `version:` line, prints 0.
cmd_skill_version() {
  local rel="$1"
  _assert_safe_path "$rel/SKILL.md"
  local file="$LOCAL_BASE/$rel/SKILL.md"
  if [[ ! -f "$file" ]]; then
    echo "0"
    return 0
  fi
  awk '
    /^---[[:space:]]*$/ { fm++; next }
    fm == 1 && /^version:/ {
      sub(/^version:[[:space:]]*/, "")
      sub(/[[:space:]]*#.*$/, "")
      print
      exit
    }
    fm >= 2 { exit }
  ' "$file" | tr -d '[:space:]' || echo "0"
}

# Extract post-update action blocks from a skill's changelog for versions in (from, to].
# A post-update block starts at a line beginning with (optionally indented) `**Post-update:**`
# and continues until the next top-level changelog entry (`- N (YYYY-MM-DD):`) or end of file.
# Output format (one block per matched version):
#   ### v<version>
#   <block content, verbatim>
#   <blank line>
# Exits 0 even when nothing matches (so pull can call it unconditionally).
cmd_post_update_actions() {
  local rel="$1"
  local from="${2:-0}"
  local to="${3:-999}"
  _assert_safe_path "$rel/SKILL.md"
  local file="$LOCAL_BASE/$rel/SKILL.md"
  [[ -f "$file" ]] || return 0

  awk -v from="$from" -v to="$to" '
    # Enter the ## Changelog section; leave on next top-level heading.
    /^## Changelog[[:space:]]*$/ { in_cl = 1; next }
    in_cl && /^## / { in_cl = 0 }
    !in_cl { next }

    # New version entry: "- 12 (2026-04-13): ..." or "- 12 (2026-04-13) ..."
    /^- [0-9]+ / {
      # Flush previous entry if it was in range and had a post-update block.
      _flush()
      # Parse the new version number (strip leading "- ", take first word).
      line = $0
      sub(/^- /, "", line)
      split(line, parts, " ")
      cur_ver = parts[1] + 0
      if (cur_ver > from + 0 && cur_ver <= to + 0) {
        collecting = 1
        in_post = 0
        buffer = ""
      } else {
        collecting = 0
        in_post = 0
        buffer = ""
      }
      next
    }

    collecting {
      # Post-update block marker must be at the start of a continuation line
      # (after optional indentation). This prevents accidental matches when
      # an author mentions the marker literal inside prose. Authors who need
      # to *talk about* the marker should use "post-update annotation" or
      # other phrasing in descriptive text.
      if (!in_post && $0 ~ /^[[:space:]]*\*\*Post-update:\*\*/) {
        in_post = 1
        # Strip leading indentation for cleaner output.
        line2 = $0
        sub(/^[[:space:]]+/, "", line2)
        buffer = line2
        next
      }
      if (in_post) {
        # Blank line ends the post-update block — anything after it is
        # prose that belongs to the next entry or is a separator before
        # the next version.
        if ($0 ~ /^[[:space:]]*$/) {
          in_post = 0
          next
        }
        # Still inside the block — accumulate the continuation line with
        # indent stripped.
        line2 = $0
        sub(/^[[:space:]]+/, "", line2)
        buffer = buffer "\n" line2
      }
    }

    END { _flush() }

    function _flush() {
      if (collecting && in_post && buffer != "") {
        print "### v" cur_ver
        print buffer
        print ""
      }
    }
  ' "$file"
}

cmd_check() {
  # Optional flag: --analyzed enriches each UPSTREAM_NEWER row with a
  # three-way merge recommendation (see cmd_analyze).
  local analyzed=0
  case "${1:-}" in
    --analyzed) analyzed=1; shift ;;
  esac

  # Fetch without mutating working tree; if behind, still don't pull — the
  # caller decides whether to advance (via `pull-file` on individual files, or
  # by running `push-prep` which resets to origin/main).
  echo "=== sync.sh check ==="
  echo "hitachi path: $HITACHI"
  git -C "$HITACHI" fetch origin main --quiet

  local behind ahead
  behind="$(git -C "$HITACHI" rev-list HEAD..origin/main --count)"
  ahead="$(git -C "$HITACHI" rev-list origin/main..HEAD --count)"
  echo "hitachi checkout: $behind commits behind origin/main, $ahead commits ahead"
  if ! _hitachi_clean; then
    echo "WARNING: hitachi working tree is dirty — push/pull will refuse until clean"
  fi
  echo ""

  # Compare local .claude/skills and .claude/agents against origin/main tree.
  # Using git's committed view of hitachi avoids mtime noise from working-copy churn.
  echo "=== Changes (local ↔ hitachi@origin/main) ==="
  if [[ $analyzed -eq 1 ]]; then
    echo "Format: STATUS  PATH  RECOMMENDATION  SUMMARY"
    echo "  UPSTREAM_ONLY                            = file exists in hitachi, missing locally (pull candidate)"
    echo "  LOCAL_ONLY                               = file exists locally, missing upstream (push candidate)"
    echo "  UPSTREAM_NEWER  UPSTREAM_ADVANCE        = local matches an old hitachi blob; safe to fast-forward"
    echo "  UPSTREAM_NEWER  LOCAL_AHEAD             = local blob unknown to hitachi; project edited recently — KEEP LOCAL"
    echo "  UPSTREAM_NEWER  BOTH_DIVERGED           = both sides advanced — manual diff review required"
    echo "  UPSTREAM_NEWER  UNDETERMINED            = blob-history probe failed — treat as BOTH_DIVERGED"
  else
    echo "Format: STATUS  PATH"
    echo "  UPSTREAM_ONLY   = file exists in hitachi, missing locally (pull candidate)"
    echo "  LOCAL_ONLY      = file exists locally, missing upstream (push candidate)"
    echo "  UPSTREAM_NEWER  = both exist, content differs — need 3-way check"
  fi
  echo ""

  local tmp
  tmp="$(mktemp)"
  trap "rm -f $tmp" EXIT

  _walk_registry_tree >"$tmp"
  if [[ $analyzed -eq 1 ]]; then
    # Enrich each UPSTREAM_NEWER row with cmd_analyze output; pass others through.
    sort "$tmp" | while IFS=$'\t' read -r status path; do
      [[ -z "$status" ]] && continue
      if [[ "$status" == "UPSTREAM_NEWER" ]]; then
        cmd_analyze "$path" 2>/dev/null || printf 'UPSTREAM_NEWER\t%s\tUNDETERMINED\tanalyze probe failed\n' "$path"
      else
        printf '%s\t%s\n' "$status" "$path"
      fi
    done
  else
    sort "$tmp"
  fi
}

# ─── analyze ───────────────────────────────────────────────────────────────
#
# Three-way merge analysis for ONE UPSTREAM_NEWER path. Uses git blob history
# in the hitachi clone (no state file required) to decide whether the local
# file is at an OLDER hitachi blob (clean fast-forward — UPSTREAM_ADVANCE),
# is unknown to hitachi history but recently edited locally (LOCAL_AHEAD —
# never auto-pull), or has truly diverged (BOTH_DIVERGED — confirm per file).
#
# Output: one line, tab-separated:
#   STATUS<TAB>PATH<TAB>RECOMMENDATION<TAB>SUMMARY
# where RECOMMENDATION ∈ {UPSTREAM_ADVANCE, LOCAL_AHEAD, BOTH_DIVERGED, UNDETERMINED}.
#
# The function never crashes the caller: any git probe failure → UNDETERMINED.
cmd_analyze() {
  local rel="$1"
  _assert_safe_path "$rel"
  local local_path="$LOCAL_BASE/$rel"

  # Always emits the same first 2 columns; recommendation + summary are computed below.
  local status="UPSTREAM_NEWER"

  if [[ ! -f "$local_path" ]]; then
    printf '%s\t%s\t%s\t%s\n' "$status" "$rel" "UNDETERMINED" "local file missing"
    return 0
  fi

  # 1. Local blob hash (git's hash, matches what would be in a hitachi tree).
  #
  # Symlink-aware: a git-tracked symlink's blob content IS its target
  # path string (no trailing newline). `git hash-object <symlink>` would follow
  # the link and hash the resolved file, producing a SHA that never matches a
  # symlink blob in hitachi history. For symlinks, hash the readlink output via
  # --stdin instead.
  local local_blob
  if [[ -L "$local_path" ]]; then
    local_blob="$(printf '%s' "$(readlink "$local_path")" | git -C "$PROJECT_DIR" hash-object --stdin 2>/dev/null || true)"
  else
    local_blob="$(git -C "$PROJECT_DIR" hash-object "$local_path" 2>/dev/null || true)"
  fi
  if [[ -z "$local_blob" ]]; then
    printf '%s\t%s\t%s\t%s\n' "$status" "$rel" "UNDETERMINED" "could not hash local blob"
    return 0
  fi

  # 2. Find the most recent hitachi commit where the file at $rel had this blob.
  #    We walk the commit list for that path on `--all` and ls-tree each one,
  #    matching column-3 SHA. First match wins (most recent).
  local found_commit="" found_ts=""
  local commit_lines
  commit_lines="$(git -C "$HITACHI" log --all --pretty=format:'%H %at' -- "$rel" 2>/dev/null || true)"
  if [[ -n "$commit_lines" ]]; then
    while IFS=' ' read -r c ts; do
      [[ -z "$c" ]] && continue
      local sha
      sha="$(git -C "$HITACHI" ls-tree "$c" -- "$rel" 2>/dev/null | awk '{print $3}')"
      if [[ "$sha" == "$local_blob" ]]; then
        found_commit="$c"
        found_ts="$ts"
        break
      fi
    done <<<"$commit_lines"
  fi

  # 3. Project's last commit touching the local file (epoch seconds).
  local project_last_ts
  project_last_ts="$(git -C "$PROJECT_DIR" log -1 --pretty=format:'%at' -- ".claude/$rel" 2>/dev/null || true)"
  local now
  now="$(date +%s)"

  if [[ -n "$found_commit" ]]; then
    # Local matches an old hitachi blob. Has origin/main advanced past it on this path?
    local newer_count
    newer_count="$(git -C "$HITACHI" rev-list --count "$found_commit..origin/main" -- "$rel" 2>/dev/null || echo 0)"
    if [[ "$newer_count" -gt 0 ]]; then
      local short_c age_days
      short_c="$(git -C "$HITACHI" rev-parse --short "$found_commit" 2>/dev/null || echo "$found_commit")"
      age_days=$(( ( now - found_ts ) / 86400 ))
      printf '%s\t%s\t%s\t%s\n' "$status" "$rel" "UPSTREAM_ADVANCE" \
        "local @blob ${local_blob:0:7} matches hitachi $short_c (${age_days}d ago); upstream advanced ${newer_count} commit(s) since"
      return 0
    fi
    # Found in history but no newer commits → impossible if check said UPSTREAM_NEWER, but be defensive.
    printf '%s\t%s\t%s\t%s\n' "$status" "$rel" "UNDETERMINED" \
      "local blob found in hitachi history but no newer commits — race condition"
    return 0
  fi

  # Local blob NOT in hitachi history. Decide LOCAL_AHEAD vs BOTH_DIVERGED.
  local age_secs="" age_human="unknown"
  if [[ -n "$project_last_ts" ]]; then
    age_secs=$(( now - project_last_ts ))
    if (( age_secs < 3600 )); then
      age_human="$((age_secs / 60))m ago"
    elif (( age_secs < 86400 )); then
      age_human="$((age_secs / 3600))h ago"
    else
      age_human="$((age_secs / 86400))d ago"
    fi
  fi

  # "Recent" threshold: 7 days. Within → LOCAL_AHEAD; older → BOTH_DIVERGED (or UNDETERMINED if no project history).
  local seven_days=$((7 * 86400))
  if [[ -n "$age_secs" && "$age_secs" -le "$seven_days" ]]; then
    printf '%s\t%s\t%s\t%s\n' "$status" "$rel" "LOCAL_AHEAD" \
      "local blob ${local_blob:0:7} not in hitachi; project last touched ${age_human} — keep local, push candidate"
    return 0
  fi

  # Older or unknown — was hitachi advanced past project's last sync touching this path?
  local hitachi_recent
  hitachi_recent="$(git -C "$HITACHI" log -1 --pretty=format:'%h %at' origin/main -- "$rel" 2>/dev/null || true)"
  if [[ -n "$hitachi_recent" ]]; then
    local short_h ts_h
    short_h="$(awk '{print $1}' <<<"$hitachi_recent")"
    ts_h="$(awk '{print $2}' <<<"$hitachi_recent")"
    local hitachi_age_days=$(( ( now - ts_h ) / 86400 ))
    printf '%s\t%s\t%s\t%s\n' "$status" "$rel" "BOTH_DIVERGED" \
      "local blob ${local_blob:0:7} not in hitachi (project edit ${age_human}); upstream $short_h (${hitachi_age_days}d ago) — manual review required"
    return 0
  fi

  printf '%s\t%s\t%s\t%s\n' "$status" "$rel" "UNDETERMINED" \
    "local blob ${local_blob:0:7} not in hitachi history; project edit ${age_human}"
}

# Enumerate every skills/* and agents/* file in both hitachi (origin/main) and
# local (.claude/). Emit one line per distinct path with a status tag.
_walk_registry_tree() {
  local upstream_ref="origin/main"

  # List files under skills/ and agents/ in hitachi@origin/main
  local upstream_files
  upstream_files="$(git -C "$HITACHI" ls-tree -r --name-only "$upstream_ref" -- skills agents 2>/dev/null || true)"

  # List local files under .claude/skills and .claude/agents.
  #
  # Use `git ls-files -co --exclude-standard` so .gitignore is honored:
  #   -c  tracked files
  #   -o  other (untracked) files — so newly-authored skill files still
  #       appear before they're committed
  #   --exclude-standard  applies .gitignore, .git/info/exclude, and the
  #       skill's own .gitignore (so __pycache__, *.pyc, .DS_Store, etc.
  #       never leak into the diff or a push stage)
  #
  # This keeps the local walk symmetric with the upstream walk (both use
  # git), and without honoring gitignore a plain `find` would otherwise
  # drag build artifacts into push-stage copies.
  local local_files
  local_files="$(
    { cd "$PROJECT_DIR" 2>/dev/null || exit 0
      git ls-files -co --exclude-standard -- .claude/skills .claude/agents 2>/dev/null \
        | sed 's|^\.claude/||' \
        | LC_ALL=C sort
    }
  )"

  # Build associative sets via temp files
  local up_list loc_list
  up_list="$(mktemp)"; loc_list="$(mktemp)"
  printf '%s\n' "$upstream_files" | sed '/^$/d' | LC_ALL=C sort >"$up_list"
  printf '%s\n' "$local_files"    | sed '/^$/d' | LC_ALL=C sort >"$loc_list"

  # UPSTREAM_ONLY
  comm -23 "$up_list" "$loc_list" | while read -r f; do
    [[ -z "$f" ]] && continue
    # Skip files we don't sync (e.g., sync-skills itself, non-registry files)
    case "$f" in
      skills/sync-skills/*) continue ;;
    esac
    printf 'UPSTREAM_ONLY\t%s\n' "$f"
  done

  # LOCAL_ONLY
  comm -13 "$up_list" "$loc_list" | while read -r f; do
    [[ -z "$f" ]] && continue
    case "$f" in
      skills/sync-skills/*) continue ;;
    esac
    printf 'LOCAL_ONLY\t%s\n' "$f"
  done

  # In both — compare resolved (dereferenced) content via filesystem reads.
  #
  # Symlink handling: the previous implementation hashed
  # `git show <ref>:<path>` (which for a symlink returns the link target STRING,
  # not its resolved content) against `sha1sum <local-path>` (which follows
  # symlinks and hashes resolved content). This produced perpetual false-
  # positive drift on every git-tracked symlink AND false negatives whenever
  # upstream type ≠ local type but resolved content matched.
  #
  # Fix: read both sides through the filesystem (`< file` redirection, which
  # follows symlinks transparently on both sides) and compare resolved bytes.
  # This unifies all 4 layout combinations (regular↔regular, regular↔symlink,
  # symlink↔regular, symlink↔symlink) under one semantic: "do they have the
  # same effective content?". This matches what users mean by "in sync" and
  # what `pull` (which copies the resolved bytes) would actually produce.
  #
  # Trade-off: the upstream side is now read from the hitachi WORKING TREE
  # rather than `git show <upstream_ref>`. That's already an invariant in this
  # script (push-prep resets to origin/main, pull copies from working tree);
  # if a user manually checks out a different branch in hitachi, comparison
  # reflects that branch, which is consistent with how every other action
  # behaves.
  comm -12 "$up_list" "$loc_list" | while read -r f; do
    [[ -z "$f" ]] && continue
    case "$f" in
      skills/sync-skills/*) continue ;;
    esac
    local upstream_hash local_hash
    # Portable SHA-1: sha1sum (GNU coreutils, always on Linux) preferred over
    # shasum (Perl script, default on macOS and Debian/Ubuntu but not on minimal
    # images like Alpine). Either works for content-equality comparisons.
    # `< file` redirection follows symlinks; `sha1sum file` would too but emits
    # the path on stdout, complicating the cut. The redirection form keeps the
    # output to just the hash.
    if command -v sha1sum >/dev/null 2>&1; then
      upstream_hash="$(sha1sum < "$HITACHI/$f" 2>/dev/null | cut -d' ' -f1)"
      local_hash="$(sha1sum < "$LOCAL_BASE/$f" 2>/dev/null | cut -d' ' -f1)"
    else
      upstream_hash="$(shasum -a 1 < "$HITACHI/$f" 2>/dev/null | cut -d' ' -f1)"
      local_hash="$(shasum -a 1 < "$LOCAL_BASE/$f" 2>/dev/null | cut -d' ' -f1)"
    fi
    if [[ "$upstream_hash" != "$local_hash" ]]; then
      printf 'UPSTREAM_NEWER\t%s\n' "$f"
    fi
  done

  rm -f "$up_list" "$loc_list"
}

cmd_pull_file() {
  local rel="$1"
  _assert_safe_path "$rel"
  local src="$HITACHI/$rel"
  local dst="$LOCAL_BASE/$rel"

  if [[ -e "$src" ]]; then
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
    echo "pulled: $rel"
  elif [[ -e "$dst" ]]; then
    rm "$dst"
    echo "deleted-locally (upstream removed): $rel"
  else
    echo "no-op: $rel (missing both sides)"
  fi
}

cmd_push_prep() {
  local branch="$1"
  if [[ -z "$branch" ]]; then
    echo "ERROR: push-prep requires a branch name" >&2
    exit 2
  fi
  if ! _hitachi_clean; then
    echo "ERROR: hitachi working tree is dirty — commit or reset before push" >&2
    git -C "$HITACHI" status --short >&2
    exit 3
  fi
  git -C "$HITACHI" fetch origin main --quiet
  git -C "$HITACHI" checkout main --quiet
  git -C "$HITACHI" reset --hard origin/main --quiet
  git -C "$HITACHI" checkout -b "$branch" 2>&1
  echo "push-prep: hitachi is on fresh branch $branch (from origin/main)"
}

cmd_push_stage() {
  local rel="$1"
  _assert_safe_path "$rel"
  local src="$LOCAL_BASE/$rel"
  local dst="$HITACHI/$rel"

  if [[ ! -e "$src" ]]; then
    echo "ERROR: local file not found: $rel" >&2
    exit 4
  fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  echo "staged: $rel"
}

cmd_push_finalize() {
  local msg="$1"
  if [[ -z "$msg" ]]; then
    echo "ERROR: push-finalize requires a commit message" >&2
    exit 2
  fi
  # Only include top-level dirs that actually exist in the registry. If the
  # registry has moved agents under skills/ (as happened in hitachi PR #5),
  # passing a missing `agents` pathspec to `git add` crashes with
  # "fatal: pathspec 'agents' did not match any files".
  local add_targets=()
  [[ -d "$HITACHI/skills" ]] && add_targets+=("skills")
  [[ -d "$HITACHI/agents" ]] && add_targets+=("agents")
  if [[ ${#add_targets[@]} -eq 0 ]]; then
    echo "ERROR: neither skills/ nor agents/ exists in hitachi checkout" >&2
    exit 7
  fi
  git -C "$HITACHI" add -A "${add_targets[@]}"
  if [[ -z "$(git -C "$HITACHI" diff --staged --name-only)" ]]; then
    echo "nothing to commit — aborting push"
    exit 5
  fi
  git -C "$HITACHI" commit -m "$msg"
  local branch
  branch="$(git -C "$HITACHI" rev-parse --abbrev-ref HEAD)"
  if [[ "$branch" == "main" ]]; then
    echo "ERROR: refusing to push directly to main — run push-prep first" >&2
    exit 6
  fi
  git -C "$HITACHI" push -u origin "$branch"
  echo "pushed: branch=$branch"
}

# ─── status ────────────────────────────────────────────────────────────────
#
# At-a-glance "are all four places in lockstep" health check.
# Reports five blocks:
#   1. Project repo working tree (clean / dirty)
#   2. Project repo local HEAD vs origin (SYNCED / AHEAD / BEHIND / DIVERGED)
#   3. Registry repo working tree (clean / dirty)
#   4. Registry repo local HEAD vs origin (SYNCED / AHEAD / BEHIND / DIVERGED)
#   5. Skill drift between project .claude/skills + agents and registry skills + agents
#
# Read-only: the only mutation allowed is `git fetch --quiet` to refresh
# remote refs. Working trees and branches are never modified.
#
# Exit code: 0 if every block is SYNCED/clean, 1 otherwise.
#
# Honors STATUS_NO_FETCH=1 to skip the fetch (used by tests with no network).

cmd_status() {
  # Shell convention: 0 = OK, non-zero = problem.
  local first_problem=""
  local rc

  echo "sync-skills status"
  echo "=================="
  echo

  # ─── Block 1+2: Project repo ────────────────────────────────────────────
  rc=0
  _status_repo_block "Project repo (local working tree)" "$PROJECT_DIR" || rc=$?
  if [[ $rc -ne 0 ]]; then
    [[ -z "$first_problem" ]] && first_problem="Project repo"
  fi
  echo

  # ─── Block 3+4: Registry repo (hitachi) ─────────────────────────────────
  if [[ -d "$HITACHI/.git" ]]; then
    rc=0
    _status_repo_block "Registry repo (hitachi)" "$HITACHI" || rc=$?
    if [[ $rc -ne 0 ]]; then
      [[ -z "$first_problem" ]] && first_problem="Registry repo"
    fi
  else
    echo "Registry repo (hitachi):"
    echo "  Path:          $HITACHI"
    echo "  Status:        MISSING (clone https://github.com/GlobalLogic-a-Hitachi-Company/hitachi alongside this repo)"
    [[ -z "$first_problem" ]] && first_problem="Registry repo"
  fi
  echo

  # ─── Block 5: Skill drift ───────────────────────────────────────────────
  rc=0
  _status_drift_block || rc=$?
  if [[ $rc -ne 0 ]]; then
    [[ -z "$first_problem" ]] && first_problem="Skill drift"
  fi
  echo

  # ─── Overall ────────────────────────────────────────────────────────────
  if [[ -z "$first_problem" ]]; then
    echo "Overall: SYNCED — safe to switch machines"
    return 0
  else
    echo "Overall: NOT SYNCED — see $first_problem above"
    return 1
  fi
}

# Render one repo block (working-tree + HEAD-vs-remote).
# Args: <label> <repo-path>
# Returns: 0 if clean+synced, 1 otherwise.
_status_repo_block() {
  local label="$1"
  local repo="$2"
  # Shell convention: 0 = OK, non-zero = problem.
  local rc=0

  echo "$label:"
  echo "  Path:          $repo"

  # Working tree
  local dirty_lines dirty_count
  dirty_lines="$(git -C "$repo" status --porcelain 2>/dev/null || true)"
  dirty_count=$(printf '%s\n' "$dirty_lines" | sed '/^$/d' | wc -l | tr -d ' ')

  if [[ "$dirty_count" -eq 0 ]]; then
    echo "  Working tree:  clean"
  else
    echo "  Working tree:  DIRTY ($dirty_count modifications)"
    printf '%s\n' "$dirty_lines" | sed '/^$/d' | head -10 | sed 's/^/    /'
    if [[ "$dirty_count" -gt 10 ]]; then
      echo "    ... ($((dirty_count - 10)) more)"
    fi
    rc=1
  fi

  # HEAD vs remote — fetch quietly first (unless suppressed)
  if [[ "${STATUS_NO_FETCH:-0}" != "1" ]]; then
    git -C "$repo" fetch --quiet 2>/dev/null || true
  fi

  local local_head remote_head ahead behind upstream
  local_head="$(git -C "$repo" rev-parse --short HEAD 2>/dev/null || echo "(none)")"
  upstream="$(git -C "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || echo "")"

  if [[ -z "$upstream" ]]; then
    echo "  Local  HEAD:   $local_head"
    echo "  Remote HEAD:   (no upstream tracking)"
    echo "  Status:        NO UPSTREAM (set with \`git -C $repo branch --set-upstream-to=origin/<branch>\`)"
    rc=1
  else
    remote_head="$(git -C "$repo" rev-parse --short '@{u}' 2>/dev/null || echo "(none)")"
    ahead="$(git -C "$repo" rev-list --count '@{u}..HEAD' 2>/dev/null || echo 0)"
    behind="$(git -C "$repo" rev-list --count 'HEAD..@{u}' 2>/dev/null || echo 0)"

    echo "  Local  HEAD:   $local_head"
    echo "  Remote HEAD:   $remote_head"

    if [[ "$ahead" -eq 0 && "$behind" -eq 0 ]]; then
      if [[ "$dirty_count" -eq 0 ]]; then
        echo "  Status:        SYNCED"
      else
        echo "  Status:        DIRTY (commit or stash before claiming sync)"
      fi
    elif [[ "$ahead" -gt 0 && "$behind" -eq 0 ]]; then
      echo "  Status:        AHEAD (local is $ahead commit(s) ahead of $upstream; run \`git -C $repo push\`)"
      rc=1
    elif [[ "$ahead" -eq 0 && "$behind" -gt 0 ]]; then
      echo "  Status:        BEHIND (local is $behind commit(s) behind $upstream; run \`git -C $repo pull --ff-only\`)"
      rc=1
    else
      echo "  Status:        DIVERGED (local is $ahead ahead, $behind behind $upstream — manual rebase/merge required)"
      rc=1
    fi
  fi

  return $rc
}

# Render the skill drift block by reusing cmd_check's per-file output.
# Returns: 0 if drift count is 0, 1 otherwise.
_status_drift_block() {
  echo "Skill drift (project .claude/skills/<name> vs registry skills/<name>):"

  if [[ ! -d "$HITACHI/.git" ]]; then
    echo "  Status:          UNKNOWN (registry missing)"
    return 1
  fi

  local drift_lines drift_count
  # cmd_check prints a header + per-file STATUS<TAB>PATH lines. Filter to just
  # the data lines (UPSTREAM_ONLY / LOCAL_ONLY / UPSTREAM_NEWER prefix).
  drift_lines="$(cmd_check 2>/dev/null | grep -E '^(UPSTREAM_ONLY|LOCAL_ONLY|UPSTREAM_NEWER)\b' || true)"
  drift_count=$(printf '%s\n' "$drift_lines" | sed '/^$/d' | wc -l | tr -d ' ')

  if [[ "$drift_count" -eq 0 ]]; then
    echo "  Files differing: 0"
    echo "  Status:          SYNCED"
    return 0
  fi

  echo "  Files differing: $drift_count"
  printf '%s\n' "$drift_lines" | head -10 | sed 's/^/    /'
  if [[ "$drift_count" -gt 10 ]]; then
    echo "    ... ($((drift_count - 10)) more)"
  fi
  echo "  Status:          DRIFT (run \`/sync-skills check\` for details, then \`pull\` or \`push\`)"
  return 1
}

# ─── Dispatch ──────────────────────────────────────────────────────────────

case "${1:-}" in
  check)                shift; cmd_check "$@" ;;
  analyze)              shift; cmd_analyze "$@" ;;
  status)               shift; cmd_status "$@" ;;
  pull-file)            shift; cmd_pull_file "$@" ;;
  push-prep)            shift; cmd_push_prep "$@" ;;
  push-stage)           shift; cmd_push_stage "$@" ;;
  push-finalize)        shift; cmd_push_finalize "$@" ;;
  hitachi-path)         shift; cmd_hitachi_path ;;
  hitachi-head)         shift; cmd_hitachi_head ;;
  skill-version)        shift; cmd_skill_version "$@" ;;
  post-update-actions)  shift; cmd_post_update_actions "$@" ;;
  *)
    cat <<'USAGE' >&2
Usage: sync.sh <command> [args]

Commands:
  check [--analyzed]             Diff hitachi vs local (both directions). Read-only.
                                 With --analyzed, every UPSTREAM_NEWER row is enriched
                                 with a recommendation (UPSTREAM_ADVANCE / LOCAL_AHEAD /
                                 BOTH_DIVERGED / UNDETERMINED) and a one-line summary.
  analyze <relpath>              Three-way merge probe for ONE UPSTREAM_NEWER path.
                                 Emits one TAB-separated line:
                                   STATUS<TAB>PATH<TAB>RECOMMENDATION<TAB>SUMMARY
  status                         At-a-glance health: project + registry working trees,
                                 HEAD-vs-remote for both, skill drift count. Exit 0 if
                                 SYNCED, 1 otherwise. Read-only (only `git fetch`).
  pull-file <relpath>            Copy one file hitachi → local (or rm if upstream deleted).
  push-prep <branch>             Reset hitachi to origin/main, create new branch.
  push-stage <relpath>           Copy one file local → hitachi (on the prepped branch).
  push-finalize <commit-msg>     Commit staged changes in hitachi, push branch.
  hitachi-path                   Print resolved hitachi path.
  hitachi-head                   Print short HEAD hash of hitachi working checkout.
  skill-version <skill-path>     Print version number from a local SKILL.md frontmatter.
  post-update-actions <skill-path> <from> <to>
                                 Print **Post-update:** blocks from a skill's changelog
                                 for version entries in the range (from, to].

Paths are relative to the registry root: `skills/<name>/...` or `agents/<name>`.
The script refuses anything outside those roots.
USAGE
    exit 64
    ;;
esac
