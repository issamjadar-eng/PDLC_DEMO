# 035 — DHF Manifest Pipeline Bring-up on PDLC_DEMO

**ID**: 035
**Created**: 2026-04-27
**Status**: In Progress
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

End-to-end exercise of the `dhf-manifest` skill on PDLC_DEMO so the four manifest layers exist on disk and the slug-driven filenames from ben/033 are validated against a real build.

PDLC_DEMO `project.yml` `dhfs[]` is missing the schema fields that `dhf-manifest/scripts/build-manifest.py` needs (`leaf`, `role`, `classification`). Today the entries only carry `path`, `regulatory`, `filing`, `parent`. The build aborts at "No system DHF (role: system) found in project.yml dhfs[]". This task fills the gap and runs the pipeline.

- Add the missing schema fields to each `dhfs[]` entry — `leaf`, `role`, `classification` (with `samd`, `iec62304`, `ai_enabled`), and (for the system DHF) `composes`.
- Run the pipeline: `init` (already scaffolded by prior runs) → `build-qms` → `build-manifest` → `dashboard`.
- Verify filenames land as `pdlc-demo-dhf-{manifest.md, manifest.json, by-section.md, dashboard.md}` per ben/033.
- Commit the new manifests + project.yml updates.

## Decisions

- **Lead system DHF:** `pca-device` (PP3500 lead product per CLAUDE.md). `role: system`, composes any item DHFs that compose into the device. For PDLC_DEMO, no item-level decomposition exists today inside pca-device (it's currently authored as a single DHF), so `composes: []` initially — refine later if architecture grows.
- **Connectivity adapter:** standalone `role: item` for now. Filed under its own 510k.
- **Cloud-suite parent:** `regulatory: mixed` is the existing convention for "platform DHF, children carry the regulatory weight." Mark as `role: system` so it can act as its own system root for the cloud-suite filings. `composes:` lists the seven cloud-suite children.
- **Cloud-suite children:** `role: item`, with conservative classifications (samd: true, iec62304: B for non-safety-critical analytics; C for clinical-interface and alerts-engine).
- **Classifications are first-pass demo placeholders** — they're plausible enough to drive the build but should be reviewed by a real systems engineer before relying on the manifest as evidence. Demo banner stays applicable.

## Todos

- [ ] Add `leaf`, `role`, `classification`, `composes` fields to all 10 entries in `project.yml` `dhfs[]`.
- [ ] Run `python3 .claude/skills/dhf-manifest/scripts/build-qms.py` (depends on `qms-manifest.md` existing under `docs/project/dhf-manifest/`).
- [ ] If `qms-manifest.md` doesn't exist yet, run `/dhf-manifest init` to scaffold it (or hand-author a stub). The skill expects `<!-- QMS-DATA -->` blocks for real obligations; an empty stub is fine for a first pipeline run.
- [ ] Run `python3 .claude/skills/dhf-manifest/scripts/build-manifest.py`. Confirm it writes `pdlc-demo-dhf-manifest.{md,json}` and `pdlc-demo-dhf-by-section.md`.
- [ ] Run `python3 .claude/skills/dhf-manifest/scripts/dashboard.py`. Confirm it writes `pdlc-demo-dhf-dashboard.md`.
- [ ] Run `python3 .claude/skills/dhf-manifest/scripts/validate.py`. Confirm zero failures.
- [ ] Commit `project.yml` + the four new manifest files + this task doc.

## Notes

- The four built artifacts go under `docs/project/dhf-manifest/` (project-side, gitignored or committed depending on project policy — PDLC_DEMO commits them as part of the demo evidence).
- Output filenames will be `pdlc-demo-dhf-*` per ben/033's slug logic.
- This is a **first pass**. The classifications I'm adding are plausible demo defaults; they're not signed off by a real systems engineer.

## Changelog

- 2026-04-27: Task created. Triggered by user request to run the dhf-manifest pipeline end-to-end after ben/033 landed the slug-driven output filenames. PDLC_DEMO `project.yml` lacks the `leaf`/`role`/`classification` schema fields the build script needs; this task fills the gap and exercises the pipeline.
