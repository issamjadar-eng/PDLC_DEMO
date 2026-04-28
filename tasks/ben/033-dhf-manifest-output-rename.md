# 033 — dhf-manifest Output Filename Parameterization

**ID**: 033
**Created**: 2026-04-27
**Status**: Complete (pending push)
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work.

1. Update at every meaningful checkpoint (HARD RULE).
2. Phase-end batching is OK; drift-batching is not.
3. A commit is not a substitute.
4. Resume-ready before any session boundary.
5. Capture strategy + lessons as they happen.

## Goals

The `dhf-manifest` skill writes its outputs as `hiplink-manifest.{md,json}`, `hiplink-by-section.md`, and `hiplink-dashboard.md` — names that hard-code one project's product into the registry skill. This is a structural leak that the prose-only ben/032 audit cannot fix safely. This task is the structural follow-up: derive the output filename prefix from `project.yml` `project.name` (slugified) so each project's manifests are visually self-identifying and the registry stays neutral.

- Output filename pattern: `<project-slug>-dhf-manifest.{md,json}`, `<project-slug>-dhf-by-section.md`, `<project-slug>-dhf-dashboard.md`.
- `<project-slug>` derives from `project.yml` `project.name`, slugified: lowercase; whitespace and underscores → hyphens; strip non-alphanumeric except hyphens; collapse repeats; trim leading/trailing hyphens.
  - Examples: `PDLC_DEMO` → `pdlc-demo` → `pdlc-demo-dhf-manifest.md`; `Arthrex PCCP` → `arthrex-pccp` → `arthrex-pccp-dhf-manifest.md`; `MedTech Project` (registry-neutral example) → `medtech-project` → `medtech-project-dhf-manifest.md`.
- Optional override: `dhf_manifest.output_prefix` in `project.yml` for projects that want a custom slug (e.g. a project named "Cardiac Suite" might prefer `cardiac-monitor-dhf-...` instead of `cardiac-suite-dhf-...`). When set, this wins over the slugified `project.name`.
- Replace the hardcoded `if leaf == "hiplink-intra-op":` branch in `build-manifest.py:365` with a project-config-driven flag (likely a `dhfs[].flags.intra_op_special_handling: true` field, or a more generic mechanism — design pass when we get to that line of code).
- Coordinate the rename:
  - `scripts/build-manifest.py:365, 553–556, 746–770` — output filename literals + `hiplink-by-section.md`/`hiplink-dashboard.md` references.
  - `scripts/build-manifest.py:365` — replace `if leaf == "hiplink-intra-op":` hardcoded leaf-name branch with a config-driven flag.
  - `actions/build.md`, `actions/inspect.md` — prose references to output filenames (these are touched in ben/032 prose-only-pass; this task makes the prose match the renamed code).
  - `dhf-manifest/README.md:15–19` — best-practice grep checks that look for `hiplink-manifest.json` mtime/existence.
  - `tracker` skill (if it has shipped the planned integration described at `actions/inspect.md:90`).
  - PDLC_DEMO and any sister projects that already have built outputs — provide a migration path.

## Todos

- [x] Design locked: `<project-slug>-dhf-{manifest.md, manifest.json, by-section.md, dashboard.md}` from `project.yml` `project.name` (slugified), with optional `dhf_manifest.output_prefix` override.
- [x] Added `scripts/_project_slug.py` — pure-stdlib slug helper. Smoke-tested against PDLC_DEMO (→ `pdlc-demo`), arthrex-pccp (→ `arthrex-pccp`), and the no-`project.yml` fallback (→ `dhf`).
- [x] Wired slug into `scripts/build-manifest.py` — all four output filenames now derive from the slug via `manifest_filename()`. Replaced the hardcoded `if leaf == "hiplink-intra-op":` branch with a project-supplied `dhfs[].classification.subtitle_extra` field.
- [x] Wired slug into `scripts/dashboard.py`, `scripts/validate.py`, `scripts/gap-report.py` — paths and module docstrings updated.
- [x] Updated prose docs (`SKILL.md`, `README.md`, `actions/build.md`, `actions/init.md`, `actions/inspect.md`) — literal `hiplink-*` filenames replaced with the `<project>-dhf-*` pattern. New `## Output filename derivation` section in SKILL.md documents the resolution order with PDLC_DEMO + arthrex-pccp examples.
- [x] Updated `dhf-manifest/README.md` best-practice grep checks to target the slug-driven filenames.
- [x] Migration note written into `dhf-manifest/README.md` v6 changelog entry — projects rerun `build-manifest` after pull; old `hiplink-*` outputs remain on disk and can be deleted by the project owner; projects relying on the `hiplink-intra-op` "tablet / offline-capable" descriptor must add `subtitle_extra` to the DHF's classification block.
- [x] Tightened the `best-practices` "Skill content is anonymized" check — dropped the `hiplink-manifest|hiplink-by-section|hiplink-dashboard` filename exception (no longer needed since the rename is in place); added explicit allowed exception for `skill-creator/SKILL.md` glossary section and post-update changelog notes that name what was renamed.
- [x] Bumped dhf-manifest version 5 → 6, dated 2026-04-27.
- [ ] Push to hitachi as a single PR titled `dhf-manifest: parameterize manifest output filenames from project.yml project.name`.
- [ ] PDLC_DEMO local: rerun `build-manifest`/`build-qms` after merge to regenerate to the new filenames (currently blocked by a pre-existing project.yml gap — no `dhfs[]` with `role: system` — out of scope for this task).
- [ ] arthrex-pccp coordination: their next `/sync-skills pull` will pick up the rename; `hiplink-manifest.md` and friends still on disk can be left in place or deleted by the project owner.

## Notes

- This is a behavior change for any consumer that has wired up the literal `hiplink-*` filenames. The migration must be opt-out-able (legacy alias) OR explicit, with clear changelog guidance.
- Coordinate timing with the ben/032 prose pass: prose pass references the *new* names so docs and code align after this task lands. If ben/032 ships first, the docs will briefly reference filenames that the code doesn't yet emit — that's acceptable (prose pass calls out the mismatch as a known transient state).

## Changelog

- 2026-04-27: Task created as the structural follow-up to ben/032's prose-only audit. Captured during ben/032 Phase 1 survey when the output filenames were identified as a programmatic leak (raised, not touched). User confirmed the prose-only constraint and the per-recommendation plan.
- 2026-04-27: User locked the design — output prefix is `project.yml` `project.name` slugified, with optional `dhf_manifest.output_prefix` override. Output filename shape: `<project-slug>-dhf-{manifest.md, manifest.json, by-section.md, dashboard.md}`. Each project's manifests will be visually self-identifying, and the registry stays neutral. Implementation plan updated to reflect the slug-driven pattern (script changes, doc updates, migration note, best-practices lint tightening).
- 2026-04-27: Implementation complete locally. `scripts/_project_slug.py` added (pure-stdlib slugifier with `dhf_manifest.output_prefix` override → `project.name` → `dhf` fallback). All four scripts (`build-manifest.py`, `dashboard.py`, `validate.py`, `gap-report.py`) now derive output filenames from the slug. Hardcoded `if leaf == "hiplink-intra-op":` branch replaced with `dhfs[].classification.subtitle_extra` field. Prose updated across SKILL.md (new `## Output filename derivation` section), README.md (best-practice grep checks retargeted; v6 changelog entry with migration note), and all `actions/*.md`. `best-practices` lint tightened to drop the `hiplink-*` filename exception and document the legitimate glossary-doc + post-update-note exceptions. Skill version bumped 5 → 6. Smoke tests: build-reference clean (114 obl × 11 dim × 19 src); validate passes (1 expected warning about no manifest yet); slug helper resolves correctly across PDLC_DEMO / arthrex-pccp / no-yml fallback.
