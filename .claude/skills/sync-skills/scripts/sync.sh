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

  # List local files under .claude/skills and .claude/agents
  local local_files
  local_files="$(
    { cd "$LOCAL_BASE" 2>/dev/null || exit 0
      find skills agents -type f 2>/dev/null | LC_ALL=C sort
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
    local upstream_blob local_blob
    upstream_blob="$(git -C "$HITACHI" show "$upstream_ref:$f" 2>/dev/null | shasum -a 1 | cut -d' ' -f1)"
    local_blob="$(shasum -a 1 "$LOCAL_BASE/$f" | cut -d' ' -f1)"
    if [[ "$upstream_blob" != "$local_blob" ]]; then
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
  git -C "$HITACHI" add -A skills agents
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
  check)          shift; cmd_check "$@" ;;
  pull-file)      shift; cmd_pull_file "$@" ;;
  push-prep)      shift; cmd_push_prep "$@" ;;
  push-stage)     shift; cmd_push_stage "$@" ;;
  push-finalize)  shift; cmd_push_finalize "$@" ;;
  hitachi-path)   shift; cmd_hitachi_path ;;
  hitachi-head)   shift; cmd_hitachi_head ;;
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

Paths are relative to the registry root: `skills/<name>/...` or `agents/<name>`.
The script refuses anything outside those roots.
USAGE
    exit 64
    ;;
esac
