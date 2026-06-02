# 073 — Project Console Visual Refresh via frontend-design

**ID**: 073
**Created**: 2026-06-01
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. Update at every meaningful checkpoint (HARD RULE).
2. Phase-end batching OK; drift-batching not.
3. A commit is not a substitute.
4. Resume-ready before any session boundary.
5. Capture strategy + lessons as they happen.

---

## Goals

Apply the newly-installed Anthropic `frontend-design` skill (PR #29) to lift the visual quality of `tools/project-console/` — the local FastAPI app most users will see first. The skill argues for an intentional aesthetic direction, distinctive typography, cohesive color/theme via CSS variables, motion at high-impact moments, and unexpected spatial composition. Most of the current console reads as competent-but-default; this task closes that gap without breaking the skill's contracts.

- **G1 — Aesthetic direction.** Pick ONE clear conceptual direction the console should commit to (refined-editorial / minimalist-technical / atmospheric-data / brutalist-utility / something else). Capture the rationale here and in the chosen theme pack's README.
- **G2 — Page-by-page audit.** Walk every route (Overview, Agents, Documents, Trace Matrix, Workflows, Dashboards, plus the Unified Assistant drawer) and identify the 3–5 highest-leverage visual improvements per route. Score on aesthetic-impact-vs-implementation-cost. Capture in this doc.
- **G3 — Ship improvements.** Implement the picks within the project-console skill's contracts: Jinja templates under `.claude/skills/project-console/console/web/templates/`, CSS via the theme pack at `tools/project-console/themes/<active>/`, shared partials reused (don't fork). No new top-level routes unless a redesign demands it.
- **G4 — Verify in-browser.** Start the console (`/project-console run` or `start`) and visually verify every changed route against the audit. Capture before/after screenshots into `tasks/ben/_scratch/073/` if helpful.

## Boundary / Out of scope

- **No fork of `project-console`.** Visual improvements stay inside the skill's contracts. If a structural change is genuinely needed, it gets a follow-up skill-modification task (route via `/skill-creator`).
- **No new device-specific content.** This task is about *how* the console looks, not *what* it shows.
- **Sister-project compatibility.** Per memory `feedback_sister_project_compat`, any change inside the skill must work for `../../projects/arthrex/pccp/` as well. Theme-pack work that lives only in this project's `tools/project-console/themes/<active>/` is project-local and safe by construction.

## Todos

### Phase 0 — Read the skill before planning
- [ ] Read `.claude/skills/project-console/SKILL.md` end-to-end (per [[feedback_read_skill_before_planning]] — IoC patterns invisible from output inspection).
- [ ] Read `.claude/skills/frontend-design/SKILL.md` and the Aesthetics Guidelines once more, fresh.
- [ ] Read `.claude/skills/project-console/console/web/templates/` index to know what partials exist.
- [ ] Identify the active theme pack and its CSS variable surface.

### Phase 1 — Aesthetic direction (G1)
- [ ] Capture a short brief here: purpose / audience / tone / differentiation per the skill's Design Thinking prompts.
- [ ] Propose 2–3 directional options as a one-question chat decision (per `feedback_one_decision_at_a_time`). Wait for user pick before drafting CSS.

### Phase 2 — Route audit (G2)
- [ ] Boot console, walk each route, capture screenshots into `_scratch/073/`.
- [ ] For each route, list 3–5 candidate improvements scored High/Med/Low on impact + High/Med/Low on cost.
- [ ] Promote a prioritized punch list here.

### Phase 3 — Ship (G3)
- [ ] Implement picks. One PR per route (or one bundled PR — confirm with user at phase boundary).
- [ ] Each change keeps the skill's Jinja partials, theme-pack surface, route structure intact.

### Phase 4 — Verify (G4)
- [ ] Re-walk routes in browser. Compare against the audit.
- [ ] Document residual gaps as follow-up notes.

### Phase 5 — Close
- [ ] Push final PR(s).
- [ ] Update index, mark Complete.

## Open Questions

- **Q1**: Apply the refresh to the active theme pack only (`globallogic` / `globallogic-dark`) or also propose upstream improvements to the skill-shipped `light` / `dark` defaults? (Default: theme-pack-only; upstream is a follow-up if signal is good.)
- **Q2**: Per-route PRs vs one bundled PR? (Default per task-scope guidance: bundle, since this is one coherent visual effort.)
- **Q3**: Motion appetite. The skill says "one well-orchestrated page load with staggered reveals > scattered micro-interactions." Should the console adopt a single page-load reveal, or stay completely still for a regulated-software feel?

## Resume

### In-flight artifacts
- No code changes yet. Phase 0 not started.

### First action on resume
1. Verify task 073 is active for current session.
2. Phase 0 reads (project-console SKILL.md → frontend-design SKILL.md → templates dir → theme pack).
3. Bring direction brief + Q1/Q2/Q3 to the user as a focused decision.

## Changelog

- 2026-06-01: Task created in continuation of PR #29 (frontend-design skill install). Phases 0–5 sketched, three open questions captured. No code touched.
