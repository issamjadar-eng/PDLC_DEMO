# 058 — Registry Sync: advisors file-locator integration + new file-locator skill

**ID**: 058
**Created**: 2026-05-15
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work, update this task doc: tick the relevant Todo checkbox, add a dated Changelog line naming the concrete artifact, update progress counts.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

_Keep the project's installed skills/agents aligned with the `hitachi` registry, and complete the post-pull reconciliation the `/sync-skills pull` flow requires._

- Pull the advisors + file-locator update from hitachi `9d7d6e6` into `.claude/`.
- Reconcile `project.yml` security allowlists with the newly installed skill.
- Install and build the new `file-locator` semantic-search MCP.

## Todos

- [x] Fast-forward local hitachi checkout (25 commits → `9d7d6e6`)
- [x] Pull 28 files (advisors update + new file-locator skill)
- [x] Record the pull in `.claude/sync-log.md`
- [x] Add `file-locator` to `project.yml` `approved_skills` and `approved_mcps`
- [x] Run `/file-locator setup` (tool dir, `.mcp.json`, `file_locator:` block, CI workflow)
- [x] Create the venv + install Python deps (`fastembed`, `mcp`, `PyYAML`)
- [x] Run `/file-locator rebuild` — index built (831 files, 7.7 MB)
- [x] Smoke-test the MCP server (clean stdin-wait, no crash)
- [ ] Commit + push the project repo
- [ ] **Restart Claude Code** so the `file-locator` MCP loads (user will do this)

## Remaining adoption / verification (post-restart)

- [ ] **Verify the `file-locator` MCP loaded** — confirm `mcp__file-locator__locate` appears in the tool set after restart. If missing, see `file-locator/SKILL.md` § Troubleshooting (Cause 1: `${CLAUDE_PROJECT_DIR}` not substituted; Cause 2: macOS `Icon\r` — N/A on this Linux/WSL host).
- [ ] **Functional check** — call `locate()` with a couple of natural-language queries (e.g. "where do we argue MDDS classification?", "PP3500 benefit-risk analysis") and confirm ranked `(path, summary, score)` hits come back sensibly banded.
- [ ] **Advisors integration review** — the advisors v-bump added the `mcp__file-locator__locate` retrieval mode + a "Semantic file locator" section to all 13 advisor agents + the 2 panels. After restart, spot-check one or two advisors (e.g. `regulatory-affairs`, `risk-management`) to confirm they actually reach for the locator on a Tier-2/Tier-3 question and apply the read-count rubric instead of over-/under-reading.
- [ ] **`advisor-researcher` interplay** — confirm advisors prefer `locate()` *before* spinning up the heavier `advisor-researcher` subagent (that is the intended ordering per the new agent text).
- [ ] **CI workflow sanity** — `.github/workflows/file-locator-rebuild.yml` triggers on default-branch pushes touching indexed content and commits a refreshed `index.db`. Watch the first post-merge run to confirm it rebuilds incrementally and doesn't churn.
- [ ] **`/best-practices`** — re-run after restart to confirm the new `file-locator` skill + MCP don't raise unexpected audit findings.

## Changelog

- **2026-05-15** — `/sync-skills pull`: fast-forwarded hitachi 25 commits to `9d7d6e6`; pulled 28 files (16 advisors `UPSTREAM_ADVANCE` + 12 file-locator `UPSTREAM_ONLY`); 13 top-level `.claude/agents/*.md` symlinks auto-resolved. Logged in `.claude/sync-log.md`.
- **2026-05-15** — `project.yml`: added `file-locator` to `approved_skills` + `approved_mcps`.
- **2026-05-15** — `/file-locator setup`: created `tools/file-locator-mcp/` (`requirements.txt`, `README.md`, `rebuild.sh`); registered `file-locator` MCP in `.mcp.json`; appended `file_locator:` block to `project.yml`; installed `.github/workflows/file-locator-rebuild.yml`. Remaining: venv + deps install, `/file-locator rebuild`, Claude Code restart.

## Notes

- Pull buckets: advisors v-bump adds `mcp__file-locator__locate` retrieval mode (degrades gracefully w/o MCP); `file-locator` is a new local semantic-search MCP skill (fastembed + SQLite FTS5).
