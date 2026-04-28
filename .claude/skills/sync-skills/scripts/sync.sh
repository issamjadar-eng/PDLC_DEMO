#!/usr/bin/env bash
# sync.sh — Mechanical primitives for the /sync-skills skill.
#
# Subcommands:
#   check                          Diff hitachi vs local, both directions. Read-only.
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
  echo "Format: STATUS  PATH"
  echo "  UPSTREAM_ONLY   = file exists in hitachi, missing locally (pull candidate)"
  echo "  LOCAL_ONLY      = file exists locally, missing upstream (push candidate)"
  echo "  UPSTREAM_NEWER  = both exist, content differs — need 3-way check"
  echo ""

  local tmp
  tmp="$(mktemp)"
  trap "rm -f $tmp" EXIT

  _walk_registry_tree >"$tmp"
  sort "$tmp"
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

  # In both — compare contents
  comm -12 "$up_list" "$loc_list" | while read -r f; do
    [[ -z "$f" ]] && continue
    case "$f" in
      skills/sync-skills/*) continue ;;
    esac
    local upstream_blob local_blob upstream_mode hasher
    # Portable SHA-1: sha1sum (GNU coreutils, always on Linux) preferred over
    # shasum (Perl script, default on macOS and Debian/Ubuntu but not on minimal
    # images like Alpine). Either works for content-equality comparisons.
    if command -v sha1sum >/dev/null 2>&1; then
      hasher="sha1sum"
    else
      hasher="shasum -a 1"
    fi
    # Mixed-mode symlink-aware comparison. `git show ref:path` of a
    # symlink-mode blob (100644 mode 120000) emits the link target text;
    # of a regular file blob (100644) emits the file content. Locally,
    # `sha1sum`/`shasum` always *follows* symlinks and hashes the
    # resolved file. Without compensation, we get false-positives in
    # two scenarios:
    #
    #   (a) Both sides symlink to the same target — upstream hashes
    #       link text, local hashes resolved content. NEVER MATCH
    #       even when fully in sync.
    #   (b) Local symlink → upstream regular file with identical
    #       resolved content (the canonical "skill installs an agent
    #       via symlink, registry stores it as a regular file" pattern)
    #       — the v6 fix that hashed link text for any local symlink
    #       broke this case.
    #
    # Pick the local hash strategy based on the *upstream* mode so it
    # matches what git stored on that side:
    #   - upstream mode 120000 (symlink) → hash local link text
    #     (requires local to also be a symlink; otherwise it's a real
    #     drift and should be flagged).
    #   - upstream mode 100644/100755 (regular) → hash local resolved
    #     content (sha1sum/shasum already follows symlinks).
    upstream_mode="$(git -C "$HITACHI" ls-tree "$upstream_ref" "$f" 2>/dev/null | awk '{print $1}')"
    upstream_blob="$(git -C "$HITACHI" show "$upstream_ref:$f" 2>/dev/null | $hasher | cut -d' ' -f1)"
    if [[ "$upstream_mode" == "120000" ]] && [[ -L "$LOCAL_BASE/$f" ]]; then
      local_blob="$(printf '%s' "$(readlink "$LOCAL_BASE/$f")" | $hasher | cut -d' ' -f1)"
    else
      local_blob="$($hasher "$LOCAL_BASE/$f" | cut -d' ' -f1)"
    fi
    if [[ "$upstream_blob" != "$local_blob" ]]; then
      printf 'UPSTREAM_NEWER\t%s\n' "$f"
    fi
  done

  rm -f "$up_list" "$loc_list"
}

cmd_pull_file() {
  local rel="$1"
  _assert_safe_path "$rel"
  local upstream_ref="origin/main"
  local dst="$LOCAL_BASE/$rel"

  # Bug-A fix (task ben/029): the previous implementation used the hitachi
  # working tree (`$HITACHI/$rel`) as the source of truth. If the working
  # tree was on a stale commit, files that existed on origin/main but not
  # in the working copy looked "missing" and got silently `rm`'d locally.
  # Read from origin/main via git plumbing instead — independent of working
  # tree state.
  #
  # Refresh origin/main first so a standalone `pull-file` invocation
  # doesn't rely on a prior `check` to have done the fetch. Cheap when
  # already up to date.
  git -C "$HITACHI" fetch origin main --quiet 2>/dev/null || true

  # Read the tree entry at origin/main: mode + blob + name. Empty output
  # means the path is genuinely absent upstream (deletion is real).
  local tree_entry mode
  tree_entry="$(git -C "$HITACHI" ls-tree "$upstream_ref" -- "$rel" 2>/dev/null)"

  if [[ -n "$tree_entry" ]]; then
    mode="$(printf '%s' "$tree_entry" | awk '{print $1}')"
    mkdir -p "$(dirname "$dst")"
    if [[ "$mode" == "120000" ]]; then
      # Symlink — write the link target as a real symlink locally.
      # `git show ref:path` of a symlink blob emits the link target text
      # (no trailing newline); recreate the symlink so it stays a symlink
      # and doesn't degrade into a regular file holding the link string.
      local target
      target="$(git -C "$HITACHI" show "$upstream_ref:$rel")"
      [[ -e "$dst" || -L "$dst" ]] && rm -f "$dst"
      ln -s "$target" "$dst"
    else
      # Regular file — write content; restore +x bit if upstream was 100755.
      git -C "$HITACHI" show "$upstream_ref:$rel" > "$dst"
      if [[ "$mode" == "100755" ]]; then
        chmod +x "$dst"
      fi
    fi
    echo "pulled: $rel"
  elif [[ -e "$dst" || -L "$dst" ]]; then
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

# ─── Dispatch ──────────────────────────────────────────────────────────────

case "${1:-}" in
  check)                shift; cmd_check "$@" ;;
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
  check                          Diff hitachi vs local (both directions). Read-only.
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
