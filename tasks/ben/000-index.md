# Task Index — Ben Xavier

| ID | Task | Status | Priority | Summary |
|----|------|--------|----------|---------|
| 001 | Project Init | In Progress | High | Stand up PDLC_DEMO repo, install skills, run `/medtech-docs init`, populate standards/frameworks, map sample docs, scaffold `src/`. |
| 002 | How-To Guide: Repeating Project Setup | Not Started | Medium | Reproducible how-to for new teams: clone hitachi, copy skills into `.claude/`, run `/medtech-docs init`, verify scaffold, create first task, and use `/sync-skills` for ongoing registry sync (incl. opt-in `--merge`). |
| 003 | Project Console Bootstrap | In Progress | Medium | Stand up `tools/project-console/` — local FastAPI web UI for dashboards and Claude Pro/Max-backed chat personas (KOL twin, etc.). No API keys, no per-call costs. Architecture doc + module plan + scaffold. |
| 004 | Sync Skills Registry (2026-04-12) | In Progress | Medium | Pull latest hitachi skills (task v11, new secops skill), re-run `/task setup` and `/secops setup`, update `project.yml` allowlist, record sync log entry. |
| 005 | Customer Insights Domain Agent | Not Started | Medium | Design and build a domain agent that reads input-analysis, clinical, and postmarket corpora to derive and validate user needs, design inputs, and architecture; populate `related_user_needs`/`related_design_inputs` frontmatter; author insights-index.md as the agent's entry point. Split out from task 001 after clinical/postmarket ingestion. |
| 006 | PP3500 Architecture & Regulatory Strategy | Blocked | High | Establish module boundaries (SaMD/SiMD/HW), platform and cybersecurity approach, and the 510(k)/PCCP/jurisdictional filing strategy for PP3500. **Blocked on task 007** (sub-DHF scaffold migration) — strategy content can resume once the new folder shape exists. |
| 007 | Medtech-docs Topology Support (Single-DHF, Multi-Sub-DHF) | In Progress | High | Evolve the `medtech-docs` skill from single-DHF-only to topology-aware (`single-dhf`, `multi-sub-dhf`). Add `init --topology`, `add-sub-dhf`, and `migrate-to-multi-dhf` actions. PDLC_DEMO migration is the first consumer / test case, not the goal. Unblocks task 006. |

## Changelog

- 2026-04-12: Created index with tasks 001 (project init) and 002 (setup how-to guide).
- 2026-04-12: Expanded task 002 summary to reference `/sync-skills` (ongoing registry sync with opt-in `--merge`).
- 2026-04-12: Added task 003 (project-console bootstrap).
- 2026-04-12: Added task 004 (sync skills registry).
- 2026-04-12: Added task 005 — customer-insights domain agent. Split out from task 001 after clinical/postmarket ingestion so agent design can proceed as its own scoped effort with clear review gates.
- 2026-04-12: Added task 006 — PP3500 architecture & regulatory strategy (strategy harvesting via tagged blocks).
- 2026-04-13: Added task 007 — sub-DHF scaffold migration (Option A). Task 006 marked Blocked pending completion of 007.
