# 033 — dhf-manifest Output Filename Parameterization

**ID**: 033
**Created**: 2026-04-27
**Status**: Not Started
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium
**Blocked by**: ben/032 prose pass (so the readme/changelog references move first)

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

- [x] Design — confirmed naming pattern `<project-slug>-dhf-{manifest.md, manifest.json, by-section.md, dashboard.md}` driven from `project.yml` `project.name`, slugified. Optional `dhf_manifest.output_prefix` override.
- [ ] Add slugifier helper (`scripts/_project_slug.py` or inline in `_linking.py` shared helper) — pure-stdlib, no PyYAML dep.
- [ ] Update `scripts/build-manifest.py` — read `project.name` (with `dhf_manifest.output_prefix` override), slugify, use as prefix for all four output files. Replace the hardcoded `hiplink-intra-op` leaf-name branch with a config-driven flag.
- [ ] Update `scripts/dashboard.py`, `scripts/validate.py`, `scripts/gap-report.py` — same slug-driven path resolution.
- [ ] Update prose docs (`SKILL.md`, `README.md`, `actions/build.md`, `actions/init.md`, `actions/inspect.md`) — replace literal `hiplink-*` filenames with the `<project>-dhf-*` pattern, document the slug derivation rule, document the override knob.
- [ ] Update `dhf-manifest/README.md` best-practice checks (lines 15, 17, 18, 19) so the grep targets the slug-driven filenames.
- [ ] Migration: write the registry changelog entry + `**Post-update:**` block telling existing projects to either rename existing built outputs in-place or rerun `build-manifest` (which will write the new filenames; old ones remain on disk and can be deleted).
- [ ] PDLC_DEMO local: rerun `build-manifest`/`build-qms` after pull to regenerate to the new filenames; verify `pdlc-demo-dhf-manifest.md` etc. appear.
- [ ] arthrex-pccp coordination: their next `/sync-skills pull` will pick up the rename; `hiplink-manifest.md` and friends still on disk can be left in place or deleted by the project owner.
- [ ] Update the `best-practices` "Skill content is anonymized" check from ben/032 Phase 4 — drop the `hiplink-manifest|hiplink-by-section|hiplink-dashboard` exception clause once the rename merges, and tighten the regex.
- [ ] Push to hitachi as a single PR titled `dhf-manifest: parameterize manifest output filenames from project.yml project.name`.
- [ ] Verify build-reference + build-manifest on PDLC_DEMO after pull (114 obligations × 11 dimensions × 19 sources should still rebuild clean).

## Notes

- This is a behavior change for any consumer that has wired up the literal `hiplink-*` filenames. The migration must be opt-out-able (legacy alias) OR explicit, with clear changelog guidance.
- Coordinate timing with the ben/032 prose pass: prose pass references the *new* names so docs and code align after this task lands. If ben/032 ships first, the docs will briefly reference filenames that the code doesn't yet emit — that's acceptable (prose pass calls out the mismatch as a known transient state).

## Changelog

- 2026-04-27: Task created as the structural follow-up to ben/032's prose-only audit. Captured during ben/032 Phase 1 survey when the output filenames were identified as a programmatic leak (raised, not touched). User confirmed the prose-only constraint and the per-recommendation plan.
- 2026-04-27: User locked the design — output prefix is `project.yml` `project.name` slugified, with optional `dhf_manifest.output_prefix` override. Output filename shape: `<project-slug>-dhf-{manifest.md, manifest.json, by-section.md, dashboard.md}`. Each project's manifests will be visually self-identifying, and the registry stays neutral. Implementation plan updated to reflect the slug-driven pattern (script changes, doc updates, migration note, best-practices lint tightening).
