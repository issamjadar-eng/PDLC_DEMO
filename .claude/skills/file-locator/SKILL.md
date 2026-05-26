---
name: file-locator
description: "Local file-locator MCP — semantic, file-granularity search over a medtech project's docs and registry-distributed regulatory knowledge. Returns ranked `(repo-relative-path, summary, heading_anchor?, score)` tuples for natural-language queries; complementary to `/dhf-manifest`'s canonical-role discovery index (this skill answers semantic queries, that one answers structural queries). Fully local: `fastembed` BGE-small ONNX + SQLite FTS5; no Anthropic API calls during indexing. The index lives at `tools/file-locator-mcp/index.db` and is **committed** (one canonical artifact for the team). Provides `setup`, `rebuild`, `status`, `audit` actions. TRIGGER when a user wants to install, build, refresh, inspect, or troubleshoot semantic file search — phrasings include: 'install the file locator', 'set up local RAG', 'set up semantic search', 'rebuild the locator index', 'audit the locator corpus', 'check what's indexed', 'why isn't <doc> showing up in locator results', 'add the file-locator MCP'."
version: 1
updated: 2026-05-14
---

Base directory for this skill: `${CLAUDE_SKILL_DIR}`

# File Locator

A semantic file-locator MCP for medtech project work. Given a natural-language query, returns ranked `(path, summary, heading_anchor?, score)` tuples so agents (advisors, ad-hoc Claude Code sessions, tooling) can decide which whole files to read.

**Not a chunked-RAG retriever.** This skill returns *file paths and summaries*, not passages. Agents read the whole files they want to read. The locator's job is to surface the right files quickly so agents don't speculatively glob and read.

**Complementary to `/dhf-manifest`'s canonical-role discovery index.** Structural queries ("load the SAD for Pre-Op") go through discovery; semantic queries ("where do we argue MDDS classification?") go through this skill.

## Dependencies

| File / Tool | Required by | Purpose | How to create |
|---|---|---|---|
| `python3` ≥ 3.10 | All actions | Indexer + server runtime | System dependency |
| `pip` packages: `fastembed`, `mcp` | `setup`, `rebuild`, server | Embedding model + MCP protocol | Installed by `setup` action |
| `project.yml` | All actions | Reads `file_locator:` config block | `/medtech-docs init` |
| `tools/file-locator-mcp/index.db` | `server.py`, `status` | The committed index | Built by `rebuild` action |

## Supporting Files

| File | Purpose |
|------|---------|
| `scripts/common.py` | Config loader, glob walker, content hashing, summary extraction utilities |
| `scripts/indexer_docs.py` | Markdown indexer — extracts file-level + sub-summaries, applies all 4 inclusion gates |
| `scripts/rebuild.py` | Orchestrator — initializes DB schema, runs the indexer incrementally |
| `scripts/server.py` | stdio MCP server exposing the `locate()` tool |
| `templates/requirements.txt` | Pinned Python deps |
| `templates/project.yml.snippet` | `file_locator:` config block, merged into project's `project.yml` by `setup` |
| `templates/mcp.json.snippet` | MCP server registration, merged into project's `.mcp.json` by `setup` |
| `templates/github-workflow.yml` | CI rebuild workflow, installed to `.github/workflows/file-locator-rebuild.yml` by `setup` |
| `templates/tool_readme.md` | README installed to `tools/file-locator-mcp/README.md` |
| `README.md` | Design rationale (human reference, not loaded by Claude) |

## Recommended runtime

The locator returns ranked hits with rich summaries; **downstream relevance judgment and the read-count rubric work best when the calling session runs on a current-best model** (latest Claude Opus). Weaker models tend to over-read (treat all hits as equally relevant, blowing the token budget) or under-read (stop at the first hit regardless of confidence cliff). This is a recommendation, not enforcement — no hooks, no gates.

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform.

### `setup`

Install the file-locator MCP into the current project. Idempotent.

1. **Preflight**
   - Verify `python3` ≥ 3.10. If missing: warn and stop.
   - Verify `project.yml` exists. If missing: warn `Run /medtech-docs init first` and stop.

2. **Create the tool directory**
   ```bash
   mkdir -p "${CLAUDE_PROJECT_DIR}/tools/file-locator-mcp"
   ```

3. **Copy templates into the tool directory**
   - `${CLAUDE_SKILL_DIR}/templates/requirements.txt` → `${CLAUDE_PROJECT_DIR}/tools/file-locator-mcp/requirements.txt`
   - `${CLAUDE_SKILL_DIR}/templates/tool_readme.md` → `${CLAUDE_PROJECT_DIR}/tools/file-locator-mcp/README.md`
   - Generate `${CLAUDE_PROJECT_DIR}/tools/file-locator-mcp/rebuild.sh`:
     ```bash
     #!/usr/bin/env bash
     set -euo pipefail

     SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
     PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
     VENV_PY="${SCRIPT_DIR}/.venv/bin/python"

     # Preflight: purge macOS Finder/iCloud `Icon\r` artifacts that silently
     # break MCP load (Claude Code's MCP loader chokes on these inside the venv
     # tree). Repopulates whenever Finder visits the directory, so we scrub on
     # every rebuild. See § Troubleshooting.
     find "${SCRIPT_DIR}/.venv" "${PROJECT_ROOT}/.claude/skills/file-locator" \
       -name $'Icon\r' -delete 2>/dev/null || true

     if [[ ! -x "${VENV_PY}" ]]; then
       echo "✗ venv not found at ${VENV_PY}"
       echo "  Run: uv venv --python 3.12 ${SCRIPT_DIR}/.venv"
       echo "       uv pip install --python ${VENV_PY} -r ${SCRIPT_DIR}/requirements.txt"
       exit 1
     fi

     export CLAUDE_PROJECT_DIR="${PROJECT_ROOT}"
     exec "${VENV_PY}" "${PROJECT_ROOT}/.claude/skills/file-locator/scripts/rebuild.py" "$@"
     ```
   - `chmod +x` the rebuild script.

4. **Merge `file_locator:` block into `project.yml`** if not already present:
   - Read `${CLAUDE_SKILL_DIR}/templates/project.yml.snippet`
   - If `project.yml` has no top-level `file_locator:` key, append the snippet.
   - If it does, skip (preserve user edits).

5. **Merge MCP server registration into `.mcp.json`** at project root:
   - Read `${CLAUDE_SKILL_DIR}/templates/mcp.json.snippet`
   - If `.mcp.json` doesn't exist, create with the snippet content.
   - If it exists, merge the `file-locator` entry into the `mcpServers` object (use `jq`).
   - **Paths in the snippet are project-root-relative on purpose** — `./tools/file-locator-mcp/.venv/bin/python` and `./.claude/skills/file-locator/scripts/server.py`. Claude Code does **not** substitute `${CLAUDE_PROJECT_DIR}` inside the `command`/`args` fields of `.mcp.json` (it passes the literal string to `posix_spawn`, which fails with `ENOENT`). The MCP launcher's cwd is the project root, so relative paths resolve correctly. The `command` must point at the **venv** interpreter, not system `python3` — the deps (`fastembed`, `mcp`) live only in the venv. Do not rewrite these to absolute paths or `${CLAUDE_PROJECT_DIR}` forms.

6. **Install the CI rebuild workflow**
   - Copy `${CLAUDE_SKILL_DIR}/templates/github-workflow.yml` → `${CLAUDE_PROJECT_DIR}/.github/workflows/file-locator-rebuild.yml` (create `.github/workflows/` if absent).
   - The template is **project-agnostic** — every install places the tool and skill at the same fixed paths, so the workflow needs no per-project edits. It triggers on pushes to the default branch that touch indexed content, rebuilds incrementally, and commits the refreshed `index.db`. Incremental rebuilds are content-addressable, so an unrelated change is a genuine no-op (no commit) — the broad `paths:` filter does not cause churn.
   - If the file already exists, skip (preserve user edits).

7. **Install Python dependencies** (best-effort prompt — actual install up to user):
   ```bash
   echo "→ Run: pip install -r tools/file-locator-mcp/requirements.txt"
   ```

8. **Print recommended-runtime reminder**:
   ```
   ⚠  For best results, run agents that call locate() on the latest Claude Opus.
   ```

9. **Print next-step**:
   ```
   ✓ file-locator installed. Next: /file-locator rebuild
   ```

### `rebuild`

Build (or incrementally update) the index at `tools/file-locator-mcp/index.db`.

1. **Preflight**
   - Verify `tools/file-locator-mcp/` exists. If not: warn `Run /file-locator setup first` and stop.
   - Verify `fastembed` is importable. If not: warn `Run: pip install -r tools/file-locator-mcp/requirements.txt` and stop.

2. **Parse args**: `--full` triggers a from-scratch rebuild (ignores prior `indexed_files` state, re-embeds everything). Default is incremental.

3. **Run the rebuild orchestrator**:
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/rebuild.py" [--full]
   ```

4. **Report**: N new, N changed, N unchanged, N removed, total corpus size, index file size, elapsed time.

5. **Recommend commit if running locally**:
   ```
   ℹ  If this was a maintenance rebuild, commit the refreshed index:
      git add tools/file-locator-mcp/index.db && git commit -m "file-locator: rebuild index"
   ```

### `status`

Quick health check of the locator's state. Read-only.

1. Read `tools/file-locator-mcp/index.db` if present. Report indexed file count, index size on disk, last `indexed_at`, embedding model version.
2. Compare current corpus to index — report counts of NEW / CHANGED / REMOVED that would occur on next rebuild.
3. Print summary table.

### `audit`

Detailed report of what each inclusion gate filtered. Use when "why isn't `<doc>` showing up?" needs an answer.

1. Walk the entire project tree.
2. For each file, record which gate (if any) excluded it: `corpus_excludes`, `.gitignore`, `skip_sentinel`, or `not_in_corpus_includes`.
3. Print a per-outcome count table + first 5 file samples per excluded outcome.

## Configuration — `project.yml file_locator:` block

```yaml
file_locator:
  index_path: tools/file-locator-mcp/index.db
  embedding:
    provider: local          # only valid value in v1
    model: BAAI/bge-small-en-v1.5
    dimension: 384
  ranking:
    embedding_weight: 0.6
    bm25_weight: 0.4
    banding:
      high_confidence: 0.70
      partial_match: 0.40
  granularity:
    sub_summary_when_lines_gt: 500
    sub_summary_when_h2_gt: 5
    decision_block_pattern: '^#{2,3}\s+DECISION'
  corpus_includes:
    - "*.md"
    - "project.yml"
    - "docs/**/*.md"
    - ".claude/skills/dhf-manifest/**/*.{md,yml}"
    - ".claude/skills/medtech-docs/**/*.md"
    - ".claude/skills/trace-matrix/**/*.md"
    - ".claude/skills/change-control/**/*.md"
    - ".claude/skills/tracker/**/*.md"
    - ".claude/skills/secops/**/*.md"
    - ".claude/skills/jira-pull/**/*.md"
    - ".claude/skills/docflow/**/*.md"
  corpus_excludes:
    - "**/_scratch/**"
    - "**/.staging/**"
    - "**/.worktrees/**"
    - "**/node_modules/**"
    - "**/__pycache__/**"
    - "**/.git/**"
    - "**/*.lock"
    - "**/assets/**"
    - "**/formal/**"
    - "**/Icon"
    - "**/index.db"
    - "docs/.change-control/**"
    - "docs/confluence-staging/**"
```

Per-project overrides (additions, not replacements) live in the project's own `project.yml`.

## Best Practices
See `README.md` for design rationale and decision history.

## Troubleshooting

### `mcp__file-locator__locate` tool missing after session restart

MCP servers only load at session start, so any fix below requires a Claude Code restart to take effect. Two distinct causes have been seen — diagnose by reading the MCP launch log under `~/Library/Caches/claude-cli-nodejs/<project-slug>/mcp-logs-file-locator/*.jsonl`.

**Cause 1 — `${CLAUDE_PROJECT_DIR}` in `.mcp.json` is not substituted.** If the log shows `ENOENT ... posix_spawn '${CLAUDE_PROJECT_DIR}/...'`, the `.mcp.json` `file-locator` entry is using `${CLAUDE_PROJECT_DIR}` substitution in its `command`/`args`. Claude Code does not expand that variable in those fields — it passes the literal string. Fix: rewrite the entry to project-root-relative paths (see `templates/mcp.json.snippet` — `./tools/file-locator-mcp/.venv/bin/python` + `./.claude/skills/file-locator/scripts/server.py`, empty `env`). The MCP launcher's cwd is the project root, so relative paths resolve.

**Cause 2 — `Icon\r` artifacts inside the venv (macOS).** macOS Finder and iCloud Drive silently create zero-byte `Icon\r` files (literal `Icon` followed by carriage return) inside any directory they visit to hold custom folder icons. When these land inside `tools/file-locator-mcp/.venv/`, the server crashes on import (e.g. `NotADirectoryError` inside `jsonschema_specifications`' directory walk — third-party code with no exclude hook). The generated `rebuild.sh` scrubs them on every rebuild, but they repopulate whenever Finder/iCloud visits the tree. Manual scrub:

```bash
find tools/file-locator-mcp/.venv .claude/skills/file-locator \
  -name $'Icon\r' -delete
```

**Permanent fix for Cause 2: keep the project out of an iCloud-synced tree.** If the project lives under `~/Documents/` (or `~/Desktop/`), iCloud Drive walks and re-poisons the tree continuously — scrubbing only buys you until the next sync pass. Relocate the repo to a non-synced path (e.g. `~/projects/<project>`). Because venv `bin/` scripts hard-code absolute interpreter paths, a move breaks the venv — after relocating, recreate it: `uv venv --python 3.12 tools/file-locator-mcp/.venv && uv pip install --python tools/file-locator-mcp/.venv/bin/python -r tools/file-locator-mcp/requirements.txt`.

If the tool is still missing after both causes are ruled out, manually launch the server to surface the live traceback:

```bash
tools/file-locator-mcp/.venv/bin/python \
  .claude/skills/file-locator/scripts/server.py
```

It should hang on stdin waiting for the MCP protocol — that's success.

## Changelog
See `README.md`.
