# 065 — file-locator: incremental rebuild fails (UNIQUE constraint)

**ID**: 065
**Created**: 2026-05-16
**Status**: Complete (2026-05-30 — fix landed via ben/067 bulk pull)
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

Session-recovery point. Keep current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).**
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

## Goals

Fix the `file-locator` skill's incremental indexer — the `file-locator-rebuild.yml` CI workflow **fails on every post-merge run**. Surfaced by the ben/058 CI-sanity checklist item (2026-05-16).

## The bug

CI job `file-locator index rebuild` (`.github/workflows/file-locator-rebuild.yml`) → `tools/file-locator-mcp/rebuild.sh` → `rebuild.py` → `indexer_docs.py`:

```
mode: incremental
Traceback (most recent call last):
  File ".claude/skills/file-locator/scripts/rebuild.py", line 66, in <module>
  File ".claude/skills/file-locator/scripts/rebuild.py", line 44, in main
    stats = index(cfg, full=args.full)
  File ".claude/skills/file-locator/scripts/indexer_docs.py", line 156, in index
    _write_batch(conn, cfg, work, current_hashes, embeddings)
  File ".claude/skills/file-locator/scripts/indexer_docs.py", line 251, in _write_batch
    conn.execute(...)
sqlite3.IntegrityError: UNIQUE constraint failed: summaries.path, summaries.heading_anchor
```

**Diagnosis (preliminary):** `_write_batch` does a plain `INSERT` into `summaries` for re-indexed files. On an *incremental* rebuild of a changed file, the prior `(path, heading_anchor)` row is not deleted first (or the write is not an upsert), so the unique constraint collides. The **full** rebuild path works — `/file-locator rebuild` built 831 files locally (ben/058) — so the defect is specific to the incremental path.

**Likely fix:** in `_write_batch`, delete existing `summaries` rows for the batch's paths before insert, or switch to `INSERT ... ON CONFLICT(path, heading_anchor) DO UPDATE` / `INSERT OR REPLACE`. Confirm against the FTS5 sidecar table too (keep `summaries` and the FTS index consistent).

## Impact

- Every push to `main` touching indexed content re-runs the workflow → fails (~20s). 6+ consecutive failures observed (PRs #1–#4 + earlier).
- The committed `tools/file-locator-mcp/index.db` goes stale — CI can't refresh it. Not harmful (local search still works off the committed DB) but the index drifts from the corpus.

## Scope

`file-locator` is a **registry skill** (v1, from hitachi). Fix goes through `/skill-creator`: edit `indexer_docs.py`, add an incremental-rebuild regression test, bump version, then push to hitachi.

## Todos

- [ ] Read `file-locator/SKILL.md` + `scripts/indexer_docs.py` (`_write_batch`, `index`)
- [ ] Reproduce the incremental-rebuild failure locally
- [ ] Fix `_write_batch` (upsert / delete-before-insert; keep FTS sidecar consistent)
- [ ] Add a regression test for incremental rebuild of a changed file
- [ ] Version bump + README; push to hitachi
- [ ] Verify the CI workflow goes green on the next post-merge run

## Changelog

- 2026-05-16: Task created. Defect found by ben/058's CI-sanity check — `file-locator-rebuild.yml` fails every run on `sqlite3.IntegrityError: UNIQUE constraint failed: summaries.path, summaries.heading_anchor`.
- 2026-05-30: **Closed.** Fix landed upstream as hitachi commit `1ba65ae` ("file-locator: fix incremental rebuild crash (FK cascade never fires)") and pulled into PDLC_DEMO today via ben/067 PR #13. Root-cause matched the diagnosis: `_write_batch` was doing plain INSERTs on re-indexed files; SQLite disables foreign keys per-connection by default so the schema's `ON DELETE CASCADE` on the `summaries → indexed_files` FK was inert; orphan `summaries` rows collided on re-insert. Fix is two layers: (1) `init_db` now runs `PRAGMA foreign_keys = ON` after connecting; (2) `_write_batch` explicitly `DELETE FROM summaries WHERE path = ?` before `DELETE FROM indexed_files` as belt-and-suspenders. FTS sidecar stays consistent via the existing `summaries_ad` AFTER DELETE trigger. **CI verification**: GitHub Actions run `26679868135` (post-PR-#13 merge, 2026-05-30T09:00:58Z) succeeded in 43s — first green incremental-rebuild run after 6+ consecutive failures. No further action needed; the Todos above were all addressed at the registry by the hitachi commit author.

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 3,
    "todos": [
      {
        "todo": "file-locator incremental rebuild bug",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 4,
          "max": 12
        },
        "confidence": "low",
        "basis": "file-locator incremental rebuild FK-cascade fix"
      }
    ]
  }
}
```
