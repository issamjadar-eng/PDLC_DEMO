# Task Index — Ben Xavier

| ID | Task | Status | Priority | Summary |
|----|------|--------|----------|---------|
| 001 | Project Init | In Progress | High | Stand up PDLC_DEMO repo, install skills, run `/medtech-docs init`, populate standards/frameworks, map sample docs, scaffold `src/`. |
| 002 | How-To Guide: Repeating Project Setup | Not Started | Medium | Reproducible how-to for new teams: clone hitachi, copy skills into `.claude/`, run `/medtech-docs init`, verify scaffold, create first task, and use `/sync-skills` for ongoing registry sync (incl. opt-in `--merge`). |
| 003 | Project Console Bootstrap | In Progress | Medium | Stand up `tools/project-console/` — local FastAPI web UI for dashboards and Claude Pro/Max-backed chat personas (KOL twin, etc.). No API keys, no per-call costs. Architecture doc + module plan + scaffold. |
| 004 | Sync Skills Registry (2026-04-12) | In Progress | Medium | Pull latest hitachi skills (task v11, new secops skill), re-run `/task setup` and `/secops setup`, update `project.yml` allowlist, record sync log entry. |
| 005 | Customer Insights Domain Agent | Not Started | Medium | Design and build a domain agent that reads input-analysis, clinical, and postmarket corpora to derive and validate user needs, design inputs, and architecture; populate `related_user_needs`/`related_design_inputs` frontmatter; author insights-index.md as the agent's entry point. Split out from task 001 after clinical/postmarket ingestion. |
| 006 | PP3500 Architecture & Regulatory Strategy | Not Started | High | Establish module boundaries (SaMD/SiMD/HW), platform and cybersecurity approach, and the 510(k)/PCCP/jurisdictional filing strategy for PP3500. Unblocked by task 007 (2026-04-13) — strategy content authors directly into `docs/project/dhfs/pca-device/design-controls/plans/`. |
| 007 | Medtech-docs Topology Support (Unified Sub-DHF Shape) | In Progress | High | **Substantively complete.** Pivoted from dual-topology (`single-dhf`/`multi-sub-dhf`) to a unified sub-DHF shape where every project has at least one sub-DHF from day one — no migration action, no topology flip. medtech-docs v13 scaffolds `docs/project/dhfs/<primary>/...` at init time. `add-sub-dhf` adds more. Consuming skills (strategy v9, tracker v4, best-practices v9 with full subagent dispatch, task v14, docflow v2) all topology-aware. PDLC_DEMO reorganized into `dhfs/pca-device/` (P6 stages A/B/C). 9 additional sub-DHFs stubbed (connectivity-adapter, cloud-suite + 7 children). chrome-devtools MCP pre-approved in project.yml template and secops runtime allowlist. **Remaining**: `/sync-skills push` to contribute changes back to hitachi. Unblocks task 006. |

## Changelog

- 2026-04-12: Created index with tasks 001 (project init) and 002 (setup how-to guide).
- 2026-04-12: Expanded task 002 summary to reference `/sync-skills` (ongoing registry sync with opt-in `--merge`).
- 2026-04-12: Added task 003 (project-console bootstrap).
- 2026-04-12: Added task 004 (sync skills registry).
- 2026-04-12: Added task 005 — customer-insights domain agent. Split out from task 001 after clinical/postmarket ingestion so agent design can proceed as its own scoped effort with clear review gates.
- 2026-04-12: Added task 006 — PP3500 architecture & regulatory strategy (strategy harvesting via tagged blocks).
- 2026-04-13: Added task 007 — sub-DHF scaffold migration (Option A). Task 006 marked Blocked pending completion of 007.
- 2026-04-13: Task 007 substantively complete. Unified-sub-DHF-shape skill redesign landed (medtech-docs v13, best-practices v9 with subagent dispatch, strategy v9 with scope resolution, tracker v4, task v14, docflow v2). PDLC_DEMO reorganized into `dhfs/pca-device/` via P6 stages A/B/C; 9 additional sub-DHFs (connectivity-adapter + cloud-suite + 7 children) scaffolded. chrome-devtools MCP pre-approved end-to-end. Deep integrity scan passed with 0 critical findings after fixing 2 stale-path bugs. Task 006 unblocked. Remaining follow-up: `/sync-skills push` upstream to hitachi.
