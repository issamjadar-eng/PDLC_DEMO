# 058 — Registry Sync: advisors file-locator integration + new file-locator skill

**ID**: 058
**Created**: 2026-05-15
**Status**: Complete
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
- [x] Commit + push the project repo — `a449d2e` pushed to `origin/main`
- [x] **Restart Claude Code** so the `file-locator` MCP loads

## Remaining adoption / verification (post-restart)

- [x] **Verify the `file-locator` MCP loaded** — `mcp__file-locator__locate` is in the tool set after restart.
- [x] **Functional check** — `locate()` called for "where do we argue MDDS classification" and "PP3500 benefit-risk analysis"; both returned sensibly banded ranked hits (831-file corpus).
- [x] **Advisors integration review** — advisors test suite (`uv run --with pytest python -m pytest .claude/skills/advisors/tests/`) all green: **85 passed**, incl. **45** in `test_file_locator_wiring.py` covering 13 advisors + 2 panels (locator tool granted + "Semantic file locator" section rendered). Live spot-check: `regulatory-affairs` advisor invoked on an MDDS-classification question called `mcp__file-locator__locate` first, then resolved paths and read 4 files — applied the read-count rubric correctly. Confirmed 13/13 installed `.claude/agents/*.md` advisor files carry the tool grant + section.
- [x] **`advisor-researcher` interplay** — confirmed: in the live spot-check the `regulatory-affairs` advisor preferred `locate()` and explicitly did **not** spin up `advisor-researcher` because the locator + Tier-1 strategy doc covered the question — the intended ordering.
- [x] **CI workflow sanity** — watched: `file-locator-rebuild.yml` **FAILS on every post-merge run** (`sqlite3.IntegrityError: UNIQUE constraint failed: summaries.path, summaries.heading_anchor` — incremental indexer bug). Real defect — captured + spun out as **ben/065** to fix.
- [x] **`/best-practices`** — re-run: `file-locator` skill is clean — versioned (`v1` + README Changelog), self-contained, in `approved_skills`, MCP in `approved_mcps`. No unexpected audit findings from file-locator. (Minor upstream nit: file-locator README has no `## Best Practices` table — not a project issue.)

## Changelog

- **2026-05-15** — `/sync-skills pull`: fast-forwarded hitachi 25 commits to `9d7d6e6`; pulled 28 files (16 advisors `UPSTREAM_ADVANCE` + 12 file-locator `UPSTREAM_ONLY`); 13 top-level `.claude/agents/*.md` symlinks auto-resolved. Logged in `.claude/sync-log.md`.
- **2026-05-15** — `project.yml`: added `file-locator` to `approved_skills` + `approved_mcps`.
- **2026-05-15** — `/file-locator setup`: created `tools/file-locator-mcp/` (`requirements.txt`, `README.md`, `rebuild.sh`); registered `file-locator` MCP in `.mcp.json`; appended `file_locator:` block to `project.yml`; installed `.github/workflows/file-locator-rebuild.yml`.
- **2026-05-15** — venv created (`uv venv --python 3.12`, CPython 3.12.11); deps installed (`fastembed`, `mcp`, `PyYAML`); imports verified.
- **2026-05-15** — `/file-locator rebuild`: index built — 831 files indexed, 7.7 MB at `tools/file-locator-mcp/index.db`. MCP server smoke-tested (clean stdin-wait exit, no traceback).
- **2026-05-15** — Committed `a449d2e` (38 files) and pushed to `origin/main`. **Pending: Claude Code restart** to load the `file-locator` MCP, then the post-restart verification checklist (locator functional check, advisors integration review, CI sanity, `/best-practices`).
- **2026-05-15** — `advisors` skill v1.3.1: added `tests/run.sh` (pytest runner — pulls `pytest`+`PyYAML` ephemerally via `uv run --no-project`, no repo-installed dev deps) + skill-local `.gitignore` for `__pycache__/`/`*.pyc`/`.pytest_cache/`; added `.pytest_cache/` to root `.gitignore`; bumped `VERSION` 1.2.0→1.3.1 (was stale, 1.3.0 shipped without a bump). Suite green via runner — 85 passed. All test-run cache dirs confirmed git-ignored.
- **2026-05-15** — Post-restart verification: `file-locator` MCP loaded (`mcp__file-locator__locate` present); functional check on 2 NL queries returned well-banded hits. Advisors suite green — 85 passed (45 in `test_file_locator_wiring.py`). Live `regulatory-affairs` advisor spot-check confirmed locator-first grounding and correct `advisor-researcher` deferral. Remaining: CI workflow sanity (first post-merge run) + `/best-practices` re-run.
- **2026-05-16** — Pushed the local advisors v1.3.1 work upstream. `/sync-skills check` flagged `advisors/{SKILL.md,README.md,VERSION}` `UPSTREAM_NEWER`; `--analyzed` refined to `LOCAL_AHEAD` (local v1.3.1 ahead of hitachi v1.2.0 — diff confirmed local = hitachi `9d7d6e6` + the local v1.3.1 additions). Pushed 5 files to hitachi PR #169, squash-merged `95dde22`. hitachi advisors now matches local.
- **2026-05-16** — Closed out the two post-restart checklist items. `/best-practices`: `file-locator` skill clean (versioned, self-contained, in both allowlists) — no unexpected findings. CI sanity: `file-locator-rebuild.yml` **fails every run** — incremental-indexer `UNIQUE constraint` bug; captured as **ben/065**. The registry-sync task itself is complete (advisors + file-locator integrated, verified, pushed); the CI bug is a separate file-locator-skill defect tracked under ben/065. **Task complete.**

## Notes

- Pull buckets: advisors v-bump adds `mcp__file-locator__locate` retrieval mode (degrades gracefully w/o MCP); `file-locator` is a new local semantic-search MCP skill (fastembed + SQLite FTS5).

