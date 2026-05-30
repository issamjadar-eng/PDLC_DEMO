# 067 — Bulk Registry Sync (2026-05-30)

**ID**: 067
**Created**: 2026-05-30
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium
**Spawned from**: ben/066 (G4 — the original `/sync-skills check` after the symlink fix landed)

---

## PERMANENT RULES (do not remove)

Same as standard task doc — keep updated at every checkpoint; phase-end batching OK; resume-ready before any session boundary; capture strategy + lessons in real time.

## Goals

Pull every pending registry change from hitachi into PDLC_DEMO local, per user direction "pull everything (acknowledged risk)". Backlog at start: 38 UPSTREAM_ADVANCE + 13 UNDETERMINED (advisors transitive) + 41 UPSTREAM_ONLY (including 3 entirely new skills) = ~92 files.

- **G1** — Apply all UPSTREAM_ADVANCE pulls (38 files; clean fast-forwards).
- **G2** — Apply all UPSTREAM_ONLY pulls (41 new files; 3 new skills + new content under existing skills).
- **G3** — Resolve the 13 UNDETERMINED `agents/*.md` (transitive — will align once `skills/advisors/agents/*.md` are pulled).
- **G4** — Per sync-skills SKILL.md Step 5: update `project.yml` `security.approved_skills` for the 3 new skills (`gap-analysis`, `knowledge-pack-export`, `reference-audit`); update `approved_agents` for any new agents from `reference-audit` (4 citation-related agents).
- **G5** — Per sync-skills SKILL.md Step 5b (MANDATORY Project Impact Analysis): read each pulled SKILL.md changelog + post-update annotations; surface required project actions (setup re-runs, template regeneration, best-practices re-runs, frontmatter/schema changes, terminology renames, hook changes); offer execution per finding.
- **G6** — Record sync in `.claude/sync-log.md`.
- **G7** — Commit + push to PDLC_DEMO main.

## Notable items requiring attention during analysis

- **`skills/file-locator/scripts/indexer_docs.py`** UPSTREAM_ADVANCE — likely the fix for the open ben/065 bug (CI failing every post-merge with UNIQUE constraint on `summaries.path, summaries.heading_anchor`). Validate post-pull → if fix is in, can close ben/065.
- **3 new auto-loaded medtech-docs rules**: `doctype-governance.md`, `ground-in-contracts-not-assumptions.md`, `internal-vs-external-scope-labels.md`. These auto-load into every session once symlinked. Need to read each before adopting.
- **3 new skills** to evaluate + approve:
  - `gap-analysis` — actions: init, list, route, fan-out (subagent fanout pattern)
  - `knowledge-pack-export` — external LLM knowledge-pack builder
  - `reference-audit` — 4 citation researcher agents + template
- **FDA guidance additions** relevant to ben/046 (PP3500 multi-function classification): `mdds-distilled.md` + source PDFs; `qsub-estar-draft-distilled.md`; `qsub-fr-2025-09615` notice.
- **New `21-cfr-part-{807,880,892}.md`** regulations refs.
- **`task/commands/checkpoint.md` + `task/hooks/checkpoint-recover.sh`** — new task checkpoint workflow.

## Todos

- [x] G1 — pull 38 UPSTREAM_ADVANCE files (done — all "pulled:")
- [x] G2 — pull 41 UPSTREAM_ONLY files (done)
- [x] G3 — verify 13 UNDETERMINED `agents/*.md` reconciled (`check` returns 0 drift after pull)
- [x] G4 — `project.yml`: +3 `approved_skills` (gap-analysis, knowledge-pack-export, reference-audit); +4 `approved_agents` (reference-audit citations + 3 researchers)
- [~] G5 — Project Impact Analysis — **first-pass done**, deeper analysis deferred. Done: installed 3 new medtech-docs rule symlinks (`doctype-governance`, `ground-in-contracts-not-assumptions`, `internal-vs-external-scope-labels`) and listed them in CLAUDE.md Auto-loaded Rules section. **Open:** read each pulled SKILL.md changelog for required setup re-runs (see follow-ups below).
- [x] G6 — sync-log entry recorded
- [ ] G7 — commit + push to PDLC_DEMO main (this turn)

### Follow-ups (G5 deeper analysis)

- [ ] **Verify ben/065 fix** — `file-locator/scripts/indexer_docs.py` UPSTREAM_ADVANCE message at hitachi commit `1ba65ae` was titled "file-locator: fix incremental rebuild crash (FK cascade never fires)". Re-trigger `file-locator-rebuild.yml` CI (or run locally) to confirm. If clean, close ben/065.
- [ ] **`/medtech-docs setup` re-run** — pulled `medtech-docs/hooks/taxonomy-freshness.sh` is NOT wired into `settings.json`. Run setup to register.
- [ ] **`/task setup` re-run** — pulled `task/commands/checkpoint.md` + `task/hooks/checkpoint-recover.sh` (the `checkpoint` action shown in `task` skill SKILL.md description). Need setup to register the hook.
- [ ] **Read each new skill SKILL.md end-to-end before first invocation** (per project rule):
  - `gap-analysis` (v2) — content-gap analysis of medtech artifacts
  - `knowledge-pack-export` (v4) — collate project docs into external LLM knowledge packs (Gemini Gem, Custom GPT, etc.)
  - `reference-audit` (v3) — verify references / citations in project docs
- [ ] **Read updated SKILL.md changelogs** for advisors, dhf-manifest (v13), medtech-docs (v30), task (v27), tracker (v11), frontend-slides (v0.4.1), jira-pull — surface any Post-update annotations and execute as needed.
- [ ] Run `/best-practices` once the above settles — new Required/Recommended checks may have shipped in pulled SKILLs.

## Working Notes

**Check output saved**: `/tmp/sync-check-066.txt`

**Pre-pull state (2026-05-30):**
- PDLC_DEMO main: `7aaa332` (post-PR-#12)
- hitachi origin/main: `8ebe1f2` (post-sync-skills-v8.3)
- Project working tree: clean (task 066 work is committed; only the 066/067 task docs themselves will mutate)
- 0 LOCAL_ONLY → nothing local that needs pushing first

## Changelog
See [README.md](README.md) for version history.

- 2026-05-30: Task created. Pre-pull state captured; pull plan staged.
- 2026-05-30: **G1-G4 + G6 DONE.** 79 files pulled across UPSTREAM_ADVANCE (38) + UPSTREAM_ONLY (41); 13 UNDETERMINED agent symlinks auto-reconciled. project.yml allowlists updated. G5 first-pass complete (3 new medtech-docs rules symlinked + listed in CLAUDE.md). Sync-log entry recorded. Deferred to follow-up: deeper per-SKILL changelog analysis, ben/065 fix validation, `/medtech-docs setup` + `/task setup` re-runs, reading the 3 new skills end-to-end.
