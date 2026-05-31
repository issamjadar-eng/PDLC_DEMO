# PDLC_DEMO — Project Changelog

Plain-English record of significant project activity, newest first. Written for a non-technical reader — a project manager, regulatory reviewer, or someone new to the team. Each entry leads with a readable summary; the task ref, commit SHA, author, and date follow in the muted trace footer for audit and lookup.

Populated by the `/digest log` action of the `digest` skill. On retrospective first-run and when called with `--llm`, a batched `claude -p` call rewrites commit subjects into plain-English summaries; without `--llm` the builder extracts the first paragraph of each commit's body.

**What lands here** (significance filter in `build_changelog.py`):
- Tasks completed or advanced (subject matches `task <person>/NNN:`)
- Skill additions, removals, and version bumps
- Structural changes (CLAUDE.md, project.yml, new DHFs, composition manifests)
- Strategy / standards / submissions documentation changes

**What does NOT land here**: pure chore/lint/typo commits that don't touch a trigger path, individual README stub edits. Use `git log` or `/digest daily` for the full audit trail.

**To rebuild**: `/digest log` — Claude proposes a new section; you approve or edit before it's written. `/digest log --no-llm` for the mechanical-only version. The header timestamp on the latest section is the since-cursor for the next build.

---

<!-- /digest log inserts new sections immediately below this line on each run. -->

## 2026-05-31 06:09 UTC — Skill updates

**39 significant commit(s)** across 4 theme(s).

### Skills

- **Pulled 79 files and 3 new productivity tools from upstream.**
  Includes skills for document analysis and knowledge export.
  _ben/067 · `f7cf778` · Ben Xavier · 2026-05-30_

- **Fixed file corruption affecting Windows users during sync operations.**
  Windows clones now safely download updates without losing agent files.
  _ben/066 · `945d35c` · Ben Xavier · 2026-05-30_

- **Automated cleanup of merged branches in git workflow.**
  Eliminates manual housekeeping; keeps local workspace tidy.
  _ben/063 · `a44878b` · Ben Xavier · 2026-05-16_

- **Unified documentation rules under medtech-docs skill ownership.**
  Rules auto-update from upstream; single canonical form per rule.
  _ben/061 · `ec1a0f4` · Ben Xavier · 2026-05-16_

- **Converted documentation rules to auto-updating symlinks.**
  Rule improvements now propagate automatically to all projects.
  _ben/060 · `3985e0a` · Ben Xavier · 2026-05-15_

- **Established formal convention for temporary files in tasks.**
  Prevents accidental commits of scratch work and build artifacts.
  _ben/059 · `f158f62` · Ben Xavier · 2026-05-15_

- **Added meaning-based file search to advisor agents.**
  Agents now find relevant files by topic, not just filename.
  _ben/058 · `a449d2e` · Ben Xavier · 2026-05-15_

- **Fixed security audit to handle authentication token limits correctly.**
  Two-factor check now distinguishes disabled from unverifiable states.
  _ben/056 · `771f262` · benxavier-gl · 2026-05-13_

- **Improved document discovery with better matching patterns (v9→v12).**
  Documents now found by exact names, wildcards, and metadata tags.
  _ben/051 · `3c06281` · benxavier-gl · 2026-05-13_

- **Upgraded advisors and document discovery with improved matching.**
  Advisors ground decisions in discovered files; expanded role catalog.
  _`2d9ed96` · benxavier-gl · 2026-05-12_

- **Redesigned requirements links to work in both directions.**
  Fixes regression where design-input relationships broke with new layers.
  _ben/050 · `90647d7` · benxavier-gl · 2026-05-12_

- **Added draft-generation workflow and visual polish to console.**
  Users can now auto-generate submission narratives; improved dark theme.
  _`92ba076` · benxavier-gl · 2026-05-11_

- **Approved new Jira integration and document discovery agents.**
  Design controls pull directly from Jira; manifest tools enhanced.
  _ben/035 · `f5affee` · benxavier-gl · 2026-05-05_

- **Upgraded change control with formal review tiers and themes.**
  Change process now structured; console supports multiple visual themes.
  _`887d78b` · Ben Xavier · 2026-05-01_

- **Reinstalled presentation skill with completed security audit.**
  Presentation tool verified safe; no malicious code found.
  _`5c1b503` · Ben Xavier · 2026-05-01_

- **Added automated security scanning for installed tools and agents.**
  Detects 30+ risk patterns; prevents malicious code injection.
  _ben/041 · `6e7e95a` · Ben Xavier · 2026-05-01_

- **Rebuilt deck-building skill with 86 curated SVG icons.**
  Smart icon selection distinguishes tasks from generic entities.
  _ben/039 · `9a73eb9` · Ben Xavier · 2026-05-01_

- **Fixed symlink handling in sync tool across 3 upstream releases.**
  No more file corruption when downloading updates; bugs closed.
  _ben/029 · `790003b` · Ben Xavier · 2026-04-28_

- **Synced 47 files; added two-tier review to change control.**
  Change process now supports formal and internal review tiers.
  _ben/029 · `105855d` · Ben Xavier · 2026-04-28_

- **Made document tool reusable across projects with flexible naming.**
  Tool now works with any project; outputs use project names.
  _ben/033 · `ab0e5f4` · Ben Xavier · 2026-04-27_

- **Merged upstream improvements without regressing local customizations.**
  Synced change-control v0.4 while preserving project-specific changes.
  _ben/032 · `3f76013` · Ben Xavier · 2026-04-27_

- **Installed 6 new skills and completed all post-update setup.**
  Document discovery, change control, and conversion tools now live.
  _ben/030 · `777aa96` · Ben Xavier · 2026-04-27_

- **Applied macOS fix and documented accumulated task work.**
  Bash tool calls now work on macOS; 4 task docs added.
  _`ddf04d1` · benxavier-gl · 2026-04-22_

- **Relocated runtime files and added document-processing safety guard.**
  Sensitive files protected from accidental commits; workflows enforced.
  _`f38b74a` · Ben Xavier · 2026-04-21_

- **Reformatted changelog to lead with readable outcomes.**
  Non-technical readers now understand progress; summaries cached for speed.
  _ben/021 · `44ec233` · Ben Xavier · 2026-04-20_

### Tasks Completed

- **Recorded upstream sync and closed the task.**
  _ben/063 · `b24c833` · Ben Xavier · 2026-05-16_

### Tasks

- **Wrapped up sync work and deferred follow-up work.**
  _ben/050 · `0d10d82` · benxavier-gl · 2026-05-12_

### Project Structure

- **Cleaned up 6 failing configuration checks post-sync.**
  Brings the project to a clean audit baseline.
  _ben/068 · `03d345a` · Ben Xavier · 2026-05-30_

- **Added Dmytro Savenkov to the team roster.**
  _`d89aac1` · Dmytro Savenkov · 2026-05-30_

- **Configured git to ignore Excel temporary lock files.**
  _`7dc6da4` · benxavier-gl · 2026-05-26_

- **Adopted pull-request-then-auto-merge workflow as project policy.**
  All commits now require code review before merging.
  _ben/062 · `d8dd950` · Ben Xavier · 2026-05-16_

- **Added 3 verified collaborators to the project roster.**
  Closes roster gaps; 2 unverified collaborators remain pending.
  _ben/055 · `80a4360` · benxavier-gl · 2026-05-13_

- **Added PDF export for presentation decks and Drive exclusions.**
  Prevents accidental commits of Google Drive temporary files.
  _ben/053 · `e71d3d8` · benxavier-gl · 2026-05-13_

- **Initialized regulatory document mapping for the PCA device.**
  Project now auto-discovers which documents satisfy requirements.
  _`7454063` · benxavier-gl · 2026-05-12_

- **Expanded submission tracker to cover 3 medical devices.**
  Tracker now shows 154 deliverables; improved documentation links.
  _ben/047 · `446497d` · benxavier-gl · 2026-05-12_

- **Restored submission tracker dashboard with 86+ compliance rows.**
  Recovered tracker structure with engineering prerequisites and narratives.
  _ben/047 · `3250202` · benxavier-gl · 2026-05-12_

- **Updated task documentation and established skill-reading requirement.**
  Captures lessons about invisible patterns requiring direct skill review.
  _`a7395fa` · benxavier-gl · 2026-05-11_

- **Documented session loss recovery and rebuild plan.**
  Captures commit-discipline lessons from data loss incident.
  _ben/039 · `ff10e07` · Ben Xavier · 2026-05-01_

- **Initialized regulatory obligation mapping for all project devices.**
  437 requirements routed across 9 devices; ready for gap analysis.
  _ben/035 · `4235e9c` · Ben Xavier · 2026-04-27_

## 2026-04-20 20:58 UTC — Project retrospective

_Retrospective pass covering project history to date._

**35 significant commit(s)** across 4 theme(s).

### Skills

- **Fixed commits attributing to work email instead of personal account.**
  Git config now reads from project roster, ensuring consistent identity across sessions.
  _ben/020 · `09aef1e` · Ben Xavier · 2026-04-20_

- **Standardized task reference format across project documentation.**
  All cross-team task citations now include the person's name, eliminating ambiguity.
  _ben/019 · `58db573` · Ben Xavier · 2026-04-20_

- **Added daily team briefings and automatic project changelog generation.**
  Summarizes code changes grouped by author, highlighting structural and skill updates.
  _ben/019 · `926b2e6` · Ben Xavier · 2026-04-20_

- **Updated project tools and fixed all regulatory compliance documentation gaps.**
  Imported 53 skill updates and backfilled missing documentation stubs across the DHF.
  _ben/018 · `620e15e` · Ben Xavier · 2026-04-20_

- **Fixed unwanted build artifacts in change tracking and improved console launching.**
  Build artifacts now properly ignored, and console can cleanly restart when code changes.
  _`309683c` · Ben Xavier · 2026-04-15_

- **Added requirements traceability visualization and integrated it into project console.**
  Identifies gaps where design inputs lack verification, supporting regulatory evidence gathering.
  _ben/016 · `487879d` · Ben Xavier · 2026-04-15_

- **Designed change management workflow spanning code, documentation, and approval systems.**
  Integrates GitHub, Confluence, and approval tools with freeze enforcement to prevent unapproved changes.
  _ben/017 · `28dfbba` · Ben Xavier · 2026-04-15_

- **Converted custom console into reusable skill and migrated project onto it.**
  Other projects can now initialize with working dashboard, advisors, and document browser.
  _ben/015 · `7a2215d` · Ben Xavier · 2026-04-14_

- **Populated reference library with FDA guidance and industry standards.**
  Teams can now cite authoritative regulatory and technical guidance within design documentation.
  _ben/012 · `3bf76f4` · Ben Xavier · 2026-04-14_

- **Required impact analysis during skill updates and fixed versioning metadata.**
  Sync tool now enforces documentation of changes before import.
  _`d3168b2` · Ben Xavier · 2026-04-13_

- **Reorganized strategy documentation and standardized DHF naming across codebase.**
  Strategy briefs now shared across components; removed "sub-" prefix for consistency.
  _ben/009 · `bfb215c` · Ben Xavier · 2026-04-13_

- **Pre-approved browser automation tool for frontend validation in new projects.**
  Eliminates repeated approval friction for dashboard and UI-heavy projects.
  _`41451ab` · Ben Xavier · 2026-04-13_

- **Implemented parallel compliance checking and updated strategy agents for multi-component topology.**
  Audits now fan out to check each component in parallel; reduced latency and cost.
  _`5184ca4` · Ben Xavier · 2026-04-13_

- **Classified compliance checks by scope to support component-level auditing.**
  Audit framework now distinguishes project-wide checks from component-specific or filing-specific checks.
  _`6493e1f` · Ben Xavier · 2026-04-13_

- **Added automatic enforcement of strategy and lessons documentation in tasks.**
  Tasks now prompt teams to capture decisions and learnings, blocking session close if omitted.
  _`ced3c27` · Ben Xavier · 2026-04-13_

- **Updated compliance and planning tools to support multi-component architecture.**
  Audit framework, strategy documentation, and tracker now work correctly with multiple components.
  _`adf6f4b` · Ben Xavier · 2026-04-13_

- **Standardized project structure to organize docs by component from the start.**
  All projects now use the same component-scoped layout, supporting single or multi-component development.
  _`1100846` · Ben Xavier · 2026-04-13_

- **Created project scaffold with multi-component design control framework.**
  Established structure for managing primary device and multiple cloud and connectivity components.
  _ben/007 · `8493c3c` · Ben Xavier · 2026-04-13_

### Tasks Completed

- **Completed sync of external skills and resolved all required compliance issues.**
  All 16 previously failing compliance checks now pass.
  _ben/018 · `18426c4` · Ben Xavier · 2026-04-20_

### Tasks

- **Added default advisory panels and clarified console's support role.**
  AI assistants now explicitly serve as support, not replacements, for team leads.
  _ben/015 · `6329d00` · Ben Xavier · 2026-04-14_

- **Filtered hidden system files from project document tree view.**
  Prevents macOS and Windows metadata files from cluttering document exploration.
  _ben/015 · `9d90464` · Ben Xavier · 2026-04-14_

- **Contributed project console tool to shared skill library.**
  Established gitignore standards for skill development; ready for other projects to use.
  _ben/015 · `cbb0203` · Ben Xavier · 2026-04-14_

- **Integrated submission status tracker into project console.**
  Submission status now visible in main console interface alongside other tools.
  _ben/008 · `089341e` · Ben Xavier · 2026-04-14_

- **Locked component classification and filing strategy for 510(k) submission.**
  Defined which features are in initial filing scope and which are post-clearance development.
  _ben/006 · `51f3946` · Ben Xavier · 2026-04-14_

- **Required strategy documentation before importing regulatory reference materials.**
  Ensures teams understand their architecture and filing approach before citing external standards.
  _ben/002 · `7b67c7b` · Ben Xavier · 2026-04-14_

- **Identified customization points to make tracker reusable across projects.**
  Tracker currently hard-codes terminology specific to the PCA device; backlog to parameterize it.
  _ben/014 · `ea71e48` · Ben Xavier · 2026-04-14_

- **Built 118-item submission tracker for regulatory filing and approval.**
  Tracker lists all deliverables across Parts 1–4 of the 510(k) submission.
  _ben/013 · `90d7332` · Ben Xavier · 2026-04-14_

- **Created system architecture documents needed for regulatory submission planning.**
  Three system definitions (on-device, connectivity adapter, drug library) unblock tracker population.
  _ben/013 · `e4c6d0e` · Ben Xavier · 2026-04-14_

- **Created project setup guide and standardized DHF terminology.**
  Renamed artifact types for clarity; new guide walks teams through project initialization.
  _ben/002 · `2cc5716` · Ben Xavier · 2026-04-14_

- **Organized compliance audit findings into focused improvement task.**
  Identified setup, glossary, and documentation gaps to address separately from strategy work.
  _ben/010 · `45e0296` · Ben Xavier · 2026-04-13_

- **Documented task completion and updated project task index.**
  Reflected new unified DHF structure and captured 14 commits delivered this session.
  _ben/007 · `c84429a` · Ben Xavier · 2026-04-13_

- **Built advisory panels and document explorer for project console.**
  Advisors stream responses with source tracking; document browser supports PDF, YAML, JSON.
  _ben/003 · `3b9bdd0` · Ben Xavier · 2026-04-13_

- **Scaffolded nine additional product components to project structure.**
  Added connectivity adapter and seven cloud-suite modules; each ready for content authoring.
  _ben/007 · `6e587ec` · Ben Xavier · 2026-04-13_

### Project Structure

- **Reorganized documentation into component-scoped folder structure.**
  Design, clinical, postmarket, and risk docs now under device-level folders.
  _`2f54100` · Ben Xavier · 2026-04-13_

- **Created component-level folder structure for primary device.**
  Scaffolded pca-device as a DHF with design, clinical, and security subfolders.
  _`d5e3bbb` · Ben Xavier · 2026-04-13_

## 2026-04-20 00:00 UTC — Project changelog initialized

CHANGELOG.md seeded from the `medtech-docs` `changelog-project.md` template. The `2026-04-20 20:58 UTC` retrospective above is the first readable section, generated by `/digest log --retrospective` (which auto-enables `--llm` for a polished baseline).
