# `change-control adopt-tree` — agent procedure (Option B)

This action uses the **JSON-directive MCP bridge** so the Python script
can drive ~95+ pages in a tight loop, instead of paying ~95 agent
turns for what should be one bulk operation.

## Inputs

    /change-control adopt-tree <root-page-url-or-id> [--target <root>] [--max-depth N] [--dry-run]

If `--target` is omitted, default to the configured
`change_control.spaces[].staging_target_root` from `project.yml`:

    <staging_target_root>/<space-key>/

## How the bridge works

The Python script `actions/adopt_tree.py` opens **fd 3** for writing
and **fd 4** for reading. Each MCP call the script needs becomes a
JSON line on fd 3:

    {"id": "<uuid>", "tool": "getConfluencePage", "args": {...}}

The agent (you) reads that line, **calls the tool with those args
verbatim**, and writes one JSON line back to fd 4:

    {"id": "<same uuid>", "ok": true, "result": <tool result>}

…or, on error:

    {"id": "<same uuid>", "ok": false, "error": "<short message>"}

The script blocks until each result arrives. Order is in-flight (one
at a time) — no concurrency. Keep the protocol strict; any malformed
line will abort the run with `BridgeError`.

## Step 1 — Set up the streams

Linux/macOS: invoke the action as

    python3 .claude/skills/change-control/actions/adopt_tree.py \
        --root-page-id <ID> \
        --base-url <base> \
        --space-key <KEY> \
        --target-root <staging_target_root>/<KEY> \
        3>directives.jsonl 4<results.jsonl

…then run a small driver loop that:
  1. tails `directives.jsonl`,
  2. for each new directive, calls the named MCP tool,
  3. writes the result line to `results.jsonl`.

For interactive use, the simpler pattern is **co-process** style:
spawn the script with a pair of pipes and you (the agent) bridge
them in the chat turn loop.

## Step 2 — Service each directive

Loop over directives. For each:

  - `tool == "getAccessibleAtlassianResources"` →
    call `mcp__atlassian__getAccessibleAtlassianResources` (no args)
    and return the result.
  - `tool == "getConfluencePageDescendants"` →
    call `mcp__atlassian__getConfluencePageDescendants` with the args
    forwarded.
  - `tool == "getConfluencePage"` →
    call `mcp__atlassian__getConfluencePage`.

Always pass `args` through verbatim. If a tool isn't in this list,
fail loud — the script should not be inventing tools.

## Step 3 — Final summary

The script prints a summary block to stdout when done:

    adopt-tree summary:
      pages adopted:   95 / 95
      versioned files: 14
      index files:     6
      zones found:     3
      extensions:      27
      media refs:      11
      smart links:     8

If `FAILED:` is non-zero, the script's exit code is non-zero too —
surface the failure list to the user.

## `--refresh` mode (task 130, v0.9.0)

Incremental sync against a previously-adopted tree. Re-discovers the
Confluence subtree from `--root-page-id`, diffs against the existing
manifest at `<target-root>/.manifest.json` (or `--manifest-path`), and
only re-adopts pages whose Confluence version has advanced. Local edits
to staged pages are preserved; real conflicts emit side-by-side files.

Per-page categorization (printed BEFORE any I/O):

  - `in_sync`            — version unchanged, local body matches snapshot
  - `only_yours_pending` — version unchanged, local body diverges
                           (local-only edit; preserved, no Confluence
                           delta to do anything about)
  - `upstream_changed`   — version advanced, local body matches snapshot
                           (will be safely overwritten with v_new)
  - `added`              — page exists in Confluence but not in old
                           manifest (will be adopted fresh)
  - `removed`            — page in old manifest but not in current
                           Confluence subtree (NEVER auto-deleted; the
                           summary lists candidate paths the user might
                           want to `git rm`)
  - `predicted_conflict` — version advanced AND local body diverges
                           from snapshot (both sides changed since
                           v_anc; will go through the conflict prompt)

`--dry-run` exits after printing the summary, no I/O.

`--on-conflict {prompt|overwrite|abort|merge}` controls per-page
conflict handling for `predicted_conflict` pages — same semantics as
`adopt_helper.py write --on-conflict`. Default `prompt` writes side-by-
side files (`<doc>.confluence-side.md`, `<doc>.local-diff.md`) and
exits non-zero. The new manifest is rewritten ONLY on a clean run with
no unresolved conflicts (atomic write via `lib.manifest.write_manifest`).

Removed pages are never auto-deleted — the summary only flags them.
Use `git rm <path>` manually after reviewing.

## Dry-run and fixtures

Pass `--dry-run` to print the planned target paths without writing
anything. Useful before a real run to sanity-check folder layout.

Pass `--fixture <path>` to drive the script from a captured fixture
file (line-delimited JSON records, each `{tool, args, result}`). The
test suite uses this to exercise the full pipeline without an MCP.

## Why a bridge instead of agent-orchestrated?

For 95 pages, doing single-page adopt 95 times costs ~95 agent turns
plus context. The bridge lets the bulk loop live in Python — the agent
turn count is bounded by the number of unique MCP calls made in one
script invocation (typically 2N+1: descendants + N×getConfluencePage,
plus one resource resolution), and the chat context stays clean.
