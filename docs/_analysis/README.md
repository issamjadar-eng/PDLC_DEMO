# `docs/_analysis/` — Project Analysis Workspace

Local workspace for **assertions ABOUT the project's own work product** — gap analyses, reference audits, and other structured critiques produced by Claude-driven analysis skills against the canonical DHF content.

Distinct from the four sibling concerns each skill handles:

| Concern | Owner | Output location |
|---------|-------|-----------------|
| Are the right documents present? | `/dhf-manifest` | `docs/project/dhf-manifest/` |
| Do trace edges actually link? | `/trace-matrix` | `docs/project/dhfs/<dhf>/design-controls/trace-matrix/` |
| Is Jira aligned with the DTM/HTM? | `/jira-pull audit` | `docs/project/_jira/<dhf>/<version>/audit.md` |
| Is the folder/file structure correct? | `/best-practices` | (terminal report only) |
| **Is the CONTENT methodologically correct vs standards + internal sources?** | **`/gap-analysis`, `/reference-audit`** | **`docs/_analysis/<component>/`** |

These skills write only here — never to canonical DHF locations, never to mirrors (`_jira/`, `_confluence/`), never to regulated `formal/` folders. The workspace is **assertional**: it captures findings about content quality without modifying the content itself.

## Structure

<!-- AUTO:STRUCTURE kind=subfolder-table source=fs -->
| Folder | Purpose |
|--------|---------|
| `pca-device/` | System-level / cross-component analyses (PP3500 system DHF) — e.g. HIPAA readiness across the ePHI data path |
<!-- /AUTO:STRUCTURE -->

(The table above is empty today — populated by `/gap-analysis init <topic> --component <slug>` or `/reference-audit init <doc-path>`. Each component slug must match an item-DHF `arch_slug:` in `project.yml dhfs[]` or the system DHF's `leaf:` value.)

## Expected Content

Per `<component>/` subfolder:

- `README.md` — one-line per analysis with status, owner, last update
- `<id>/` — **one folder per analysis** (folder-per-analysis convention). Inside: the aggregate `<id>/<id>.md` (start-here final report) + an auto-generated folder `README.md` + the derived `<id>.gap.json` sidecar + any `recs-<discipline>.md` / `research-<topic>.md` detail files. Gap analyses are authored by `/gap-analysis`; reference audits by `/reference-audit` (`<doc-slug>-references-audit/`).

Components are project DHF leaves — for this project: `pca-device`, `connectivity-adapter`, `cloud-suite`, `drug-library-manager`, `fleet-management`, `compliance-reports`, `analytics-dashboard`, `inventory-tracker`, `alerts-engine`, `clinical-interface`.

## Conventions

- **Read-only against canonical content.** Analysis writes go here only. The DHF, mirrors, and `formal/` folders are the **subject** of analysis, never the **destination** of analysis output.
- **One folder per analysis.** Per `/gap-analysis init` and `/reference-audit init`, each analysis is its own `<id>/` folder whose aggregate `<id>/<id>.md` carries the frontmatter (`topic`, `component`, `status`, `recommended_agents`, `grounded_against`, …); detail files (`recs-*.md` / `research-*.md`) and the derived `<id>.gap.json` sidecar live beside it.
- **Frontmatter-driven.** Analysis files declare what they're grounded against (mirror paths, standards refs) — the skills use this metadata for fan-out and validation.
- **Records, not edits.** A gap-analysis surfaces a finding; it does NOT silently amend the source doc. Promotion of findings back into DHF content is a separate human-led step.
- **Component slug = DHF identity.** New subfolders MUST match a `project.yml dhfs[]` entry (`arch_slug` for item DHFs, `leaf` for system DHFs). `/best-practices` flags strays as Required.

## For Claude

- Use `/gap-analysis init <topic> --component <slug>` to scaffold a new analysis; do NOT hand-create files under `docs/_analysis/`.
- Use `/reference-audit init <doc-path>` to scaffold a reference audit.
- When a critique surfaces during task work but doesn't yet warrant a full gap analysis, capture it as a `<!-- LESSONS LEARNED -->` block in the active task doc — the lesson can promote into a formal analysis later if it accrues evidence.
- Never modify a canonical DHF doc to "fix" a finding here without an explicit promotion step. The analysis trail is the audit record; rewriting the source loses it.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-05-30 | Ben Xavier | Initial scaffold under ben/068 — closes the `/best-practices` audit FAIL for the missing gap-analysis v2 `docs/_analysis/` tier. No component subfolders yet; populated by `/gap-analysis init` / `/reference-audit init` on first invocation. |
| 2026-06-02 | Ben Xavier | Expected Content + Conventions updated to the **folder-per-analysis** layout (`<id>/<id>.md` aggregate + folder README + `.gap.json` + detail files) when gap-analysis converged with upstream v4 (skill v5, ben/077). |
