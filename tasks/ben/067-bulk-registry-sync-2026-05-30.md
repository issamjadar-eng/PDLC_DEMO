# 067 — Bulk Registry Sync (2026-05-30)

**ID**: 067
**Created**: 2026-05-30
**Status**: Complete (2026-05-30 — all 7 goals + 6 ben/067 follow-ups + /best-practices audit run)
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

### Follow-ups (G5 deeper analysis) — ALL EXECUTED 2026-05-30

- [x] **Validate ben/065 fix** — Confirmed: fix is two-layer (`PRAGMA foreign_keys = ON` in `init_db` + explicit `DELETE FROM summaries WHERE path = ?` before parent delete in `_write_batch`). Post-PR-#13 CI run `26679868135` succeeded in 43s — first green incremental-rebuild after 6+ consecutive failures. **ben/065 closed** (moved to Completed).
- [x] **`/medtech-docs` Check 7c hook install** — Surgical install: `.claude/hooks/taxonomy-freshness.sh` symlink + SessionStart hook registered (rather than full `/medtech-docs init` re-run; the only net-new piece in v28+).
- [x] **`/task setup` new pieces** — Surgical install: `.claude/hooks/checkpoint-recover.sh` symlink + SessionStart hook registered + `.claude/commands/checkpoint.md` slash command symlink. SessionStart hook count went 3 → 5.
- [x] **Read 3 new skills end-to-end** (subagent report captured below):
  - `gap-analysis` (v2) — content-gap critiques under `docs/_analysis/<component>/<id>.md`, cited against standards clauses; advisor fan-out via `topic-advisor-map.yml`. No setup.
  - `knowledge-pack-export` (v4) — bounded knowledge packs for external LLMs (Gemini Gem / Custom GPT / NotebookLM / Claude Projects); deterministic concat + optional LLM condense + git-provenance manifest. Requires `/knowledge-pack-export setup` and (for `freshness` contradiction scanning) a `knowledge_pack.freshness` block in `project.yml` (currently absent — staleness/variants run, contradictions print skip notice).
  - `reference-audit` (v3) — citation verification with 4 researcher subagents producing `sound`/`unverified`/`broken` verdicts under `docs/_analysis/<component>/<doc-slug>-references-audit/`. Requires `/reference-audit setup` to symlink 4 agents into `.claude/agents/`. Pairs with `/gap-analysis` (gap-analysis surfaces issues with citations, reference-audit verifies them).
- [x] **Per-SKILL changelog post-update analysis** (subagent report). Surfaced TWO extra actions beyond the original list, both executed today:
  - **`/dhf-manifest discovery-index`** ran — rebuilt `docs/project/dhf-manifest/pdlc-demo-dhf-discovery.json` with v13 `governing_qms` enrichment + v14 four `registry_*` external_data roles (registry_standards / registry_fda_guidance / registry_regulations / registry_industry_frameworks pointing at `.claude/skills/medtech-docs/references/`). Result: 10 project + 133 per-DHF resolutions; 223 gaps; 7 ambiguity notes.
  - **`/advisors sync`** ran — no-op (all 14 advisors `unchanged`; the regenerated GROUNDING blocks shipped with the v1.5.1 advisor files we already pulled).
- [x] **`/best-practices audit`** — delegated to subagent (see audit report appended below).

### New follow-ups discovered (deferred)

- [ ] **Optional: edit each SME advisor frontmatter `canonical_roles.tier_2`** to add the four new `registry_*` roles per domain relevance (advisors v1.5.0 OPTIONAL post-update). Each advisor pulls in the `medtech-docs/references/<category>/` distillations as Tier-2 grounding once the role is declared. Without this, the new L1a refs are still available but not auto-grounded into the advisor's context. Defer until we actively want one of the advisors to ground in standards / FDA guidance.
- [ ] **Run `/reference-audit setup`** when we want to invoke `/reference-audit` (symlinks the 4 citation agents into `.claude/agents/`).
- [ ] **Run `/knowledge-pack-export setup`** when we want to build a knowledge pack (verifies pyyaml, scaffolds `tools/knowledge-packs/`).
- [ ] **Add `knowledge_pack.freshness` block to `project.yml`** before invoking `/knowledge-pack-export freshness` — contradiction scanning currently no-ops without it.

### First-invocation recommendations (when user is ready)

Per subagent 2's analysis:
1. `/reference-audit init docs/project/strategies/regulatory-strategy.md` — highest immediate ROI; dense citation surface, low-risk write scope.
2. `/gap-analysis init risk --component pca-device --title "PP3500 hazard register conformance vs ISO 14971 § 5.4–5.5"` — highest-leverage methodology critique for a PCA pump; exercises the mirror→standards grounding loop.
3. `/knowledge-pack-export setup` + `init pp3500-program-overview` — only after the above docs are reference-audited.

### `/best-practices audit` results (2026-05-30, subagent run)

**Tally:** 11 FAIL · 12 WARN · 6 INFO across ~75 checks (registry + 19 local skills with `## Best Practices`).

**Health verdict:** Registry fetched cleanly from `../hitachi/skills/manifest.md`; no subagent dispatch errors; no tool-permission prompts. **None of the FAILs are structural blockers** — folder scaffolding is complete across all 10 DHFs, hook wiring is intact, sync log is fresh. But the project is NOT in a clean "ship-ready" audit-pass baseline.

**New categories surfaced by today's pull (medtech-docs v30):**
1. **DHF identity-name gap** — 10/10 DHFs missing `marketed_name`; 7/10 (cloud-suite children) also missing `architecture_name`. Will affect tracker rendering quality downstream.
2. **Taxonomy-freshness check is vacuous** — `.claude/hooks/taxonomy-freshness.sh` now wired (this session) but NO `.taxonomy.yml` files exist anywhere under `docs/`. If the team intends to adopt the taxonomy mechanism for QMS/registry binding, that's a setup gap to address.

**Six FAILs worth a near-term cleanup session** (not today — out of /067 scope):
1. `project.yml strategy_domains:` block missing → blocks sentinel renders + strategy-skill init across multiple files
2. CLAUDE.md `### For Claude` should be H3 (currently H2); also missing `Update as you go (HARD RULE` marker (medtech-docs v30 check)
3. 20 missing `README.md` files: `docs/project/dhf-manifest/`, `docs/project/milestones/`, `docs/project/console/` + 10 per-DHF console subfolders, 7 `docs/internal/source-md/<cat>/templates/`
4. `docs/_analysis/README.md` + at least one component subfolder (gap-analysis v2 Required check)
5. `tasks/lessons-ledger.md` still in bootstrap state + `tasks/README.md` missing `## Lesson Records` section
6. CLAUDE.md `src/` reference in folder tree is stale (directory doesn't exist)

**Auto-fixable via `/best-practices fix`:** zero Tier A auto-applies (no findings live inside `<!-- AUTO:STRUCTURE -->` sentinel blocks). Tier B (CLAUDE.md drift) is flagged but never auto-written. **All 11 FAILs require either human authoring or `/medtech-docs init` re-run.**

**Pre-existing WARNs of note (12 total):** 6 strategy domains still in `awaiting-content` bootstrap state; 25 bare `task NNN` references in regulatory + architecture strategy docs (per-person prefix rule); 154 leaf folders with empty "Expected Content" sections (template gap); `submission-tracker.html` 15 days stale; 4 orphan task files in `tasks/ben/` (043, 036, 055, +1) not listed in `000-index.md`.

These audit findings are **captured here for visibility only** — out of /067 scope. The user can either tackle them in a focused cleanup session (suggested rough order: FAIL 1 → 2 → 6 → 3 → 5 → 4) or treat them as the new audit baseline.

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
- 2026-05-30: **G1-G4 + G6 DONE.** 79 files pulled across UPSTREAM_ADVANCE (38) + UPSTREAM_ONLY (41); 13 UNDETERMINED agent symlinks auto-reconciled. project.yml allowlists updated. G5 first-pass complete (3 new medtech-docs rules symlinked + listed in CLAUDE.md). Sync-log entry recorded.
- 2026-05-30: **All 6 ben/067 follow-ups executed in one pass:** (1) ben/065 fix validated and closed; (2-3) surgical hook installs for /task v27 (checkpoint-recover + /checkpoint slash command) and /medtech-docs v28 (taxonomy-freshness SessionStart hook); (4-5) 3 new skills and 7 pulled-skill changelogs analyzed via parallel subagents — surfaced two extra actions executed today: `/dhf-manifest discovery-index` rebuild (10+133 resolutions, 223 gaps, 7 ambiguity notes) and `/advisors sync` (no-op — regenerated GROUNDING already shipped with v1.5.1); (6) `/best-practices audit` delegated to subagent. SessionStart hook count went 3 → 5. Three new first-invocation recommendations captured for when the user is ready.

