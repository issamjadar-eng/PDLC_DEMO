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

The `dhf-manifest` skill writes its outputs as `hiplink-manifest.{md,json}`, `hiplink-by-section.md`, and `hiplink-dashboard.md` — names that hard-code one project's product into the registry skill. This is a structural leak that the prose-only ben/032 audit cannot fix safely. This task is the structural follow-up: rename the registry-default outputs to neutral names, parameterize via `project.yml`, and coordinate the rename across consumers (best-practice checks, planned `tracker` integration, any sister-project consumers).

- Rename registry default to `dhf-manifest-{md,json}`, `dhf-manifest-by-section.md`, `dhf-manifest-dashboard.md` (or similar — confirm naming during design).
- Add an opt-in `dhf_manifest.output_prefix:` knob in `project.yml` so a project can override (any project that wants `<device>-manifest.md` shape can set it).
- Coordinate the rename:
  - `scripts/build-manifest.py:365, 553–556, 746–770` — output filename literals + `hiplink-by-section.md`/`hiplink-dashboard.md` references.
  - `scripts/build-manifest.py:365` — replace `if leaf == "hiplink-intra-op":` hardcoded leaf-name branch with a config-driven flag.
  - `actions/build.md`, `actions/inspect.md` — prose references to output filenames (these are touched in ben/032 prose-only-pass; this task makes the prose match the renamed code).
  - `dhf-manifest/README.md:15–19` — best-practice grep checks that look for `hiplink-manifest.json` mtime/existence.
  - `tracker` skill (if it has shipped the planned integration described at `actions/inspect.md:90`).
  - PDLC_DEMO and any sister projects that already have built outputs — provide a migration path.

## Todos

- [ ] Design — settle on the registry-default name and the override knob shape (config key, fallback, error path).
- [ ] Code change — `scripts/build-manifest.py` reads the prefix from `project.yml`, falls back to `dhf-manifest`. Replace hardcoded `hiplink-intra-op` branch.
- [ ] Doc change — `actions/{build,inspect}.md`, `README.md` best-practice checks, SKILL.md examples.
- [ ] Migration — write the registry changelog entry and a `**Post-update:**` block telling existing projects how to opt-in to the legacy name (if they want continuity) or how to migrate built outputs.
- [ ] Push to hitachi as a single PR titled `dhf-manifest: parameterize manifest output filenames`.
- [ ] Verify on PDLC_DEMO + arthrex-pccp after pull.

## Notes

- This is a behavior change for any consumer that has wired up the literal `hiplink-*` filenames. The migration must be opt-out-able (legacy alias) OR explicit, with clear changelog guidance.
- Coordinate timing with the ben/032 prose pass: prose pass references the *new* names so docs and code align after this task lands. If ben/032 ships first, the docs will briefly reference filenames that the code doesn't yet emit — that's acceptable (prose pass calls out the mismatch as a known transient state).

## Changelog

- 2026-04-27: Task created as the structural follow-up to ben/032's prose-only audit. Captured during ben/032 Phase 1 survey when the output filenames were identified as a programmatic leak (raised, not touched). User confirmed the prose-only constraint and the per-recommendation plan.
