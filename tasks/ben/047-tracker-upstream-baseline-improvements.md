# 047 — Tracker Upstream-Baseline Improvements

**ID**: 047
**Created**: 2026-05-11
**Status**: Not Started
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
2. **Phase-end batching is OK; drift-batching is not.** Planned phases (e.g., "finish Phase 2, then log the whole phase at once") are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask. By then a crash or context-trim has lost the state. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

Now that the tracker skill and submission tracker artifacts are reset to the upstream baseline (hitachi `origin/main` v11 — see `tasks/ben/044/archive/wip-dropped-2026-05-11/` for the dropped v16/v17 WIP), drive a series of focused improvements on top of this clean foundation. The goal is to get the dashboard from the current 44-row baseline back to something with the depth of the legacy 118-row tracker (`tasks/ben/044/archive/wip-dropped-2026-05-11/project-artifacts/submission-tracker.md.backup-2026-05-05`) — but built on the **milestone-driven generator model** that upstream supports, not the legacy hand-curated FDA-TOC structure.

- Make the live dashboard at `/dashboards/submission-tracker` materially useful for demoing the PP3500 program (not just a 44-row stub)
- Stay on the upstream tracker skill — improvements land as project-data changes (project.yml, milestones catalog, composition manifests, DHF evidence) or as upstream-pushable skill changes, not as a local fork
- Preserve B6 Create Draft button surface — every improvement should keep or grow the set of rows that can drive a draft workflow

## Starting State (2026-05-11)

**Skill side** — upstream `origin/main` `tracker` v11 + `project-console` 1.17.0 + `md-deck` build.py 3.9 fix + new B6 Create Draft pieces (`tracker/agents/draft-author.md`, `tracker/scripts/build-draft-context.py`, `project-console/workflows/draft_*.py`, etc.). Clean — no local edits to skill files.

**Project side** — submission tracker regenerated via upstream v11 generator:
- `docs/project/submissions/submission-tracker.md` — 52-table-row, 5.8KB markdown (`## Phase: <milestone>` × DHF structure)
- `docs/project/submissions/submission-tracker.html` — 24.7KB rendered dashboard, **44 item rows + 6 Create Draft buttons**
- `docs/project/milestones/regulatory.yml` — 4 milestones (qsub-release, pccp-release, lmr1-release, lmr2-release) bound to pca-device DHF
- `docs/project/submissions/510k/composition-manifest.md` — single composition manifest present
- Console at http://127.0.0.1:8765 — boots clean, serves dashboard with rows visible

**Archived / not deleted** — `tasks/ben/044/archive/wip-dropped-2026-05-11/`:
- All v16/v17 skill WIP (assess-phases, classify-folders, init-taxonomy, reconcile-taxonomy actions; folder-classifier + phase-mapper agents; taxonomy.schema.yml; 7 scripts including taxonomy.py)
- Generator output sidecars (aggregates.json, gaps.json, help.json, phase-map.json, row-source.json) and `tracker-user-rows.yml`
- Legacy canonical (`submission-tracker.md.backup-2026-05-05` = 28.8KB / 118 rows / Part 1–4 FDA-TOC structure) and `.preinit` twin
- `pca-device.taxonomy.yml` (the DHF-scoped taxonomy file written by `init-taxonomy`)
- HTML for the candidate dashboard

## Known Gaps vs. Legacy 118-Row Demo Depth

Documented in task ben/044 (`### Generator output gap vs. original tracker`) and confirmed against the current generator dry-run:

| Gap | Current state | What it needs |
|---|---|---|
| Only QSub milestone rows have resolved paths | 11 rows have paths, 33 are blank | Either change all milestone bindings to `version: current` OR extend `version: v1.0/v1.1/v1.2` matching logic in `generate.py`. Hitting the version-matching logic is more correct long-term but pushes into upstream. |
| Scope renders as `pca-device` instead of `Suite` | All 44 rows show scope `pca-device` | Add `architecture_name: Suite` to the pca-device DHF entry in `project.yml`. Project-data fix; no skill change. |
| Engineering Prerequisites section missing entirely | 0 rows | Author `docs/project/milestones/engineering.yml` (the upstream skill reads this — see `tracker/SKILL.md` "Plan layer"). Project-data fix. |
| (submission)-scope rows missing — no cover letter, narrative, predicate analysis, PCCP narrative | 0 rows of `scope: (submission)` | Expand `docs/project/submissions/510k/composition-manifest.md` (and any other phase composition manifests) with submission-narrative entries. Project-data fix. |
| Other DHFs (connectivity-adapter, cloud-suite + 7 children) not represented | 0 non-pca-device rows | Either extend milestone bindings to target additional DHFs OR accept pca-device-as-headline framing. Project-data fix; design decision. |
| Per-row REF citations are empty `—` | Generator doesn't populate REF | Upstream improvement to generator — either author REF in source markdown convention or wire REF resolution into the milestone catalog. Skill change candidate. |
| No legends, Cross-Milestone Summary, Reviewer Sign-off, Changelog | Generator emits only row tables | Upstream improvement to generator. Skill change candidate. |

## Todos

Phase 1 — Cheap project-data wins (no skill changes; can ship to demo today)
- [ ] Add `architecture_name: Suite` to pca-device entry in `project.yml`; regenerate tracker; confirm scope column reads `Suite`
- [ ] Decide milestone-binding strategy (uniform `version: current` vs. per-version) and update `regulatory.yml`; regenerate; confirm all 44 rows have paths
- [ ] Author `docs/project/milestones/engineering.yml` with the Engineering Prerequisites the legacy tracker had (~20 rows); regenerate; confirm Engineering Prereqs section appears
- [ ] Expand `docs/project/submissions/510k/composition-manifest.md` with cover-letter / narrative / predicate-analysis / PCCP narrative entries to drive (submission)-scope rows
- [ ] (Optional) Add a QSub composition manifest at `docs/project/submissions/qsub/composition-manifest.md` if QSub bindings need their own snapshot

Phase 2 — B6 Create Draft surface validation
- [ ] Identify which rows the upstream renderer marks Create Draft–eligible and exercise the workflow end-to-end on at least one (`/workflows/tracker-draft/<row_id>` → propose → synthesize → save)
- [ ] Confirm the worktree lifecycle (`draft_session.py` / `draft_writer.py`) works inside this repo's git layout
- [ ] If the per-row eligibility rule is too narrow, broaden via project-data or open an upstream issue

Phase 3 — Upstream-pushable skill improvements (post-Phase-1 baseline)
- [ ] REF-column population: design a project-data convention (REF declared in milestone catalog? in composition manifest? in DHF frontmatter?) and prototype generator support; push upstream if generic enough
- [ ] Structural sections (legends, Cross-Milestone Summary, Reviewer Sign-off, Changelog) — append-only emitter additions in generate.py; push upstream
- [ ] (Stretch) Revisit the v16/v17 taxonomy work in the archive — anything still worth resurrecting on the new baseline?

## Background / Why This Task Exists

Task ben/044 attempted a tracker recovery via a three-layer taxonomy refactor that grew into substantial skill modifications (v16, v17 — `init-taxonomy`, `classify-folders`, `assess-phases`, `reconcile-taxonomy`, plus a TIER-2 agent fan-out pattern). The work diverged from the upstream skill registry and produced a candidate dashboard with only 44 rows vs. the 118-row legacy canonical — substantially less demo depth.

On 2026-05-11, during a routine `/sync-skills pull`, upstream landed the B6 Create Draft workflow (hitachi PR #143) which touched `tracker/scripts/render.py` and added significant new project-console + tracker pieces. Merging upstream's B6 against the local v17 fork was tractable for `render.py` (one helper + one CSS block + one call-site wire-up) but the broader divergence meant the local fork would only grow and never push back upstream cleanly.

User decision: reset to upstream baseline, archive the local WIP for reference, drive improvements from project-data and small upstream-pushable changes instead of carrying a local skill fork.

## Resume Command

```bash
bash .claude/hooks/task-activate.sh add <UUID-from-printenv-or-denial> 047
```

## Changelog

- 2026-05-11: Task created. Captures the reset-to-upstream decision and the priority-ordered improvement backlog. Predecessor task 044 (Tracker Console Redesign Recovery) closed out; v16/v17 skill WIP + sidecars + legacy canonical archived to `tasks/ben/044/archive/wip-dropped-2026-05-11/`.
