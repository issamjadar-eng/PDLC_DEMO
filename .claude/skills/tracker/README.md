# tracker — Design & Architecture

This document is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Best Practices

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Tracker markdown exists | `docs/project/submissions/submission-tracker.md` exists | Required | shared |
| Tracker HTML exists | `docs/project/submissions/submission-tracker.html` exists | Required | shared |
| Render script exists | `.claude/skills/tracker/scripts/render.py` exists | Required | shared |
| Composition manifest parses | `composition-manifest.md` exists in this filing folder and has the required sections (Filing Identification, Included Pieces, Excluded Pieces, Cross-references, Reviewer Sign-off) | Required | per-submission |
| Composition manifest pieces resolve | Every "Included piece" referenced in this filing's composition manifest resolves to an existing file under `docs/project/dhfs/<dhf>/...` | Required | per-submission |

## Changelog

- 5 (2026-04-13): **Regulatory strategy source path flipped to shared.** Aligned with strategy skill v10 (all strategy domains shared). Context & Sources §4 now reads one file at `docs/project/strategies/regulatory-strategy.md` instead of walking per-DHF files under `dhfs/<dhf>/design-controls/plans/`. `init` prerequisite check reduced from per-DHF loop to a single shared-path check. Formal 510(k)/PCCP/LMR outputs still live per-DHF; only the upstream strategy brief moved up. See `tasks/ben/009-shared-strategy-docs.md`.
- 4 (2026-04-13): **Unified DHF shape support.** Context & Sources section updated to read paths under `docs/project/dhfs/<dhf>/...` instead of the old flat `docs/project/design-controls/...` layout. Composition manifest added as the first-read source of truth (task 007 P4.2) — a filing's manifest lists which DHF pieces are included and is read at plan time when `build` produces its output. `init` action prerequisites updated to iterate `project.dhfs[]` and check per-DHF system SAD and regulatory strategy instead of a single flat-layout pair. Added two new per-submission best-practices checks: composition manifest parses, included pieces resolve to existing files. Multi-DHF filing support (one filing spanning multiple DHFs) is specified but full implementation (cross-DHF strategy merging, multi-SAD parsing) is a follow-up. See `tasks/ben/007-sub-dhf-migration.md` P4 for full design.
- 3 (2026-04-08): Added `init` action — first-time setup that scaffolds tracker markdown, adds CLAUDE.md rule, verifies prerequisites. Idempotent.
- 2 (2026-04-08): Added `build` action for authoring/extending the tracker. Added Context Required section pointing to source documents. Added Tracker Structure section (4 Parts, column definitions, naming conventions, adding new deliverables guide). Skill now covers both building the markdown and rendering the HTML.
- 1 (2026-04-08): Initial version — render, update, status, assess actions. Formalized from ad-hoc Python generation scripts used during tracker development (task 032).
