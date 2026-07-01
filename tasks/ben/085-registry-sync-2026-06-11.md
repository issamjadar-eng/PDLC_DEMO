# 085 — Registry Sync 2026-06-11 (bulk pull: 65 files, 8 skills advanced)

**ID**: 085
**Created**: 2026-06-11
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. **Update at every meaningful checkpoint (HARD RULE).** Tick the relevant Todo, add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker), update progress counts.
2. **Phase-end batching is OK; drift-batching is not.** Write at the phase boundary, before the next phase starts.
3. **A commit is not a substitute.** Git records code; this doc records the narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

## Goals

_User asked: "pull the latest from our project and skill repo; push once you have the latest."_

- Pull project repo `main` (was 1 commit behind — file-locator index.db refresh).
- `/sync-skills pull`: apply the 65-file auto-pull drift (42 UPSTREAM_ADVANCE + 23 UPSTREAM_ONLY; 0 LOCAL_AHEAD, 0 BOTH_DIVERGED).
- Run the mandatory project-impact analysis and apply the alignment fixes it surfaces.
- Write `.claude/sync-log.md` entry.
- Push everything to project `main` (branch → PR → auto-merge per git-workflow rule).

## Todos

- [x] `git pull --ff-only` project repo → `14f9340` (index.db refresh)
- [x] `check --analyzed` → 42 UPSTREAM_ADVANCE + 23 UPSTREAM_ONLY + 1 LOCAL_ONLY (`change-control/actions/promote.py`)
- [x] Pull all 65 auto-pull files via `sync.sh pull-file`
- [x] Impact analysis (changelog read across 8 advanced skills; 0 `Post-update:` annotations)
- [x] Fix 1: symlink `.claude/rules/ai-changelog.md` → medtech-docs rule (v32 Check 7d) + CLAUDE.md pointer line
- [x] Fix 2: CLAUDE.md `scratch-and-tmp.md` pointer line — add `_work/` sandbox (task skill v29)
- [x] Fix 3: project.yml `file_locator.corpus_excludes` — add `**/_work/**` (file-locator v3)
- [x] Fix 4: delete `.claude/skills/change-control/actions/promote.py` (upstream retired staging→promote in 0.13.1; local blob `954935b` = the exact blob upstream deleted in `ef75911`)
- [x] Write `.claude/sync-log.md` entry (hitachi HEAD `9fb865e`)
- [x] Commit → branch `ben/085-registry-sync-2026-06-11` → PR #52 → merged to main (`de0fd44`) → branch deleted

## Notes — impact analysis findings

- **task v29** — `_work/` committed personal sandbox added to `rules/scratch-and-tmp.md`; CLAUDE.md pointer line is stale (`_scratch/`-only). No new hooks.
- **medtech-docs v32 (and intermediates)** — new auto-loaded rule `rules/ai-changelog.md` (AI-changelog metadata block + vendor-neutrality); needs symlink + CLAUDE.md pointer per init Check 7d. New refs: 8 FDA-guidance distillations + source PDFs/MDs, `templates/readme-dev-spec.md`. Reference-library "escalation contract" pass on category READMEs.
- **file-locator v3** — default corpus excludes `**/_work/**`; project.yml has its own `corpus_excludes` list which must gain the same entry. index.db is CI-rebuilt on PR merge — no local rebuild needed.
- **change-control 0.13.1** — retired the two-step staging→promote inbound model; `actions/promote.py` deleted upstream. Local copy is bit-identical to the deleted blob → mirror the deletion, nothing to push.
- **dhf-manifest** — new `scripts/audit-coverage.py` (taxonomy mapping completeness check) + new best-practices audit row. On-demand script; no setup change.
- **docflow v32–v35** — adopt explicit-location mode + `_confluence` SPLICE mode + faithfulness policy. Guidance-only changes; no setup re-run.
- **advisors 10** — advisor-researcher registry carve-out (Tier-3 researcher may now read `.claude/skills/medtech-docs/references/**`). Agent files pulled; no re-grounding required.
- **reference-audit 4** — `regulations/` category wired into citations stack. Agent prompt files pulled; no setup.
- No new skills, no new agents → no `project.yml` allowlist changes.

## Changelog

- 2026-06-11: Task created mid-sync. Project pull + 65-file registry pull + impact analysis done; alignment fixes pending.
- 2026-06-11: All 4 alignment fixes applied (ai-changelog symlink + CLAUDE.md pointer; scratch-and-tmp pointer; project.yml corpus_excludes; promote.py deleted). Sync-log entry written (hitachi HEAD `9fb865e`). Remaining: commit → PR → merge.
- 2026-06-11: Landed on main via PR #52 (commit `3d2ba9b`, merge `de0fd44`); branch deleted. Post-merge `sync.sh check` drift = 0 (SYNCED). Status → Complete.

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
        "todo": "Registry sync (2026-06-11)",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 6,
          "max": 16
        },
        "confidence": "low",
        "basis": "registry sync 2026-06-11"
      }
    ]
  }
}
```
