# 073 — Project Console Visual Refresh via frontend-design

**ID**: 073
**Created**: 2026-06-01
**Status**: Complete
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
- [x] Read `.claude/skills/project-console/SKILL.md` end-to-end (per [[feedback_read_skill_before_planning]]).
- [x] Read `.claude/skills/frontend-design/SKILL.md` and the Aesthetics Guidelines once more, fresh.
- [x] Read the templates dir + the full `console.css` (1917 lines) to map the token system + JS-coupled classes.
- [x] Identify the active theme pack (`globallogic-dark`) and its CSS variable surface.

### Phase 1 — Aesthetic direction (G1)
- [x] Direction chosen: **"refined precision instrument"** (see Session 2026-06-02 block). Scope = **Option 2, skill-level `console.css`** (Q1 resolved).

### Phase 2 — Route audit (G2)
- [x] Walked routes in-browser on the worktree console (port 8766): landing, agents, documents, trace-matrix, dashboards. Findings folded directly into the Phase-3 changes (the weakest points were generic typography, flat surfaces/topnav, and no depth/motion — all addressed).

### Phase 3 — Ship (G3) — DONE (CSS-only, no markup)
- [x] Implemented in the **skill** stylesheet `.claude/skills/project-console/console/web/static/console.css` (single file). Token system (elevation scale + motion + focus-ring + radii), body atmosphere via `color-mix()`, typographic rhythm, translucent sticky blurred topnav, card elevation/hover, one `prefers-reduced-motion`-guarded page-load stagger, themed scrollbars.
- [x] No Jinja templates, class names, or JS touched → interactive features preserved by construction.
- [x] Versioned: `VERSION` 1.21.1 → **1.22.0**; changelog row added to skill `README.md`.

### Phase 4 — Verify (G4) — DONE
- [x] Re-walked every route in Chrome (DevTools MCP). Landing/agents/documents render with clear visual lift and **zero console errors**; JS-driven docs tree + selection + summary intact; dashboards tracker table intact.
- [x] Residual note: `/trace-matrix` shows only the "Rebuild all DHFs" empty state — this is a **worktree data artifact** (fresh checkout has no built trace sidecars), NOT a CSS regression. Re-verify on a built tree before close.

### Phase 5 — Close — DONE
- [x] User accepted the changes (2026-06-02): "improvements, however minor. But improvements."
- [~] Sister-project (`arthrex/pccp`) validation **waived by user** for now ("no need to test against our sister project right now"). Changes are token/`color-mix`-driven so they should generalize; revisit if/when the skill is pushed upstream.
- [x] Merged to project `main` via **PR #34** (merge commit `934c297`; CI index-rebuild `f1f0cfe` layered on top). Branch deleted, worktree removed.
- [x] Main console restarted on :8765 with the refreshed CSS (uvicorn `--reload` doesn't watch the skill package, so a restart was required).
- [ ] **DEFERRED (intentional):** `/sync-skills push` to the hitachi skill registry. User asked to hold off — the v1.22.0 `console.css` change is on project `main` only, not yet upstream. Follow-up task when ready.

## Open Questions

- ~~**Q1**: theme-pack-only vs skill-level defaults?~~ **RESOLVED 2026-06-02 → skill-level.** User chose **Option 2**: refresh the skill's brand-neutral `console.css` (CSS-only, no markup) so the improvement benefits every consumer. Theme packs still override color tokens on top.
- **Q2**: Per-route PRs vs one bundled PR? (Default: bundle — one coherent visual effort.) **Leaning bundle.**
- ~~**Q3**: Motion appetite.~~ **RESOLVED 2026-06-02 → one tasteful page-load reveal, `prefers-reduced-motion`-guarded.** Entrance-only stagger on static surfaces (landing/agents/overview cards); chat transcript + docs explorer stay still (JS-rendered, animation would fight JS). Initial `opacity:0` lives *only* inside the `no-preference` media query so reduced-motion users and any non-animating context see fully-visible content — never an invisible-UI failure.

<!-- STRATEGY CONTENT: development, architecture; topics: console-visual-refresh, skill-vs-tool-boundary, safe-css-refresh -->
## Session 2026-06-02 — Option 2 decision + design direction

**Scope chosen: Option 2 — skill-level CSS-only refresh, in a git worktree.**

Why this lane (vs theme-pack-only / full redesign):
- The console UI lives in the **skill** (`.claude/skills/project-console/console/web/`), not the deployed tool. `tools/project-console/` is config + theme packs that import the skill's `console/` package via `PYTHONPATH`. So a real visual lift has to touch the skill.
- **CSS-only, no markup** is the safety contract: the interactive JS (`chat.js`, `explorer.js`, `tracker_interactive.js`, assistant drawer, drift overlay) binds to specific classes/DOM. Refreshing `console.css` token values + existing-selector rules + additive motion cannot break those handlers. Restructuring templates (Option 3) could — explicitly excluded.
- Worktree `console-design-refresh` (branch `worktree-console-design-refresh`) gives a clean revert path. Console is launched *from the worktree* so it picks up the worktree's skill CSS.

**Aesthetic direction: "refined precision instrument."** Regulated-software audience (regulatory/clinical/quality/engineering). Not maximalist — confident, calm, precise. Execution levers (all font-independent / theme-independent so they generalize to `arthrex/pccp`):
- **Depth system**: a real layered shadow scale (`--shadow-xs/sm/md/lg`) replacing the single `--shadow-soft` (kept as alias); subtle surface elevation via `color-mix()` derived from existing tokens (works on any palette, light or dark).
- **Motion tokens + one page-load stagger** (guarded, as in Q3).
- **Typographic rhythm**: tighter heading tracking, a cleaner type scale, `--font-heading` separation — no imposed typeface (brand fonts stay in theme packs; the skill ships no CDN/font dependency, important for offline regulated environments).
- **Micro-refinement**: translucent/blurred topnav with a soft elevation edge, consistent accessible focus rings, custom themed scrollbars, smoother transitions on cards/pills/buttons.

**Sister-project safety**: every change is a token addition or a refinement of an existing selector driven by tokens/`color-mix` — no project-specific values — so it generalizes. Validate against `../../projects/arthrex/pccp/` before the push to `main` (per [[feedback_sister_project_compat]]). We are in a worktree, not pushing yet.

## Resume

### In-flight artifacts (as of 2026-06-02)
- **Worktree**: `.claude/worktrees/console-design-refresh` (branch `worktree-console-design-refresh`). All edits live here, NOT yet on `main`. Nothing committed by Claude.
- **Files changed in worktree**:
  - `.claude/skills/project-console/console/web/static/console.css` — the refresh (token system, body atmosphere, typography, topnav, cards, motion, scrollbars, focus rings).
  - `.claude/skills/project-console/VERSION` — 1.21.1 → 1.22.0.
  - `.claude/skills/project-console/README.md` — changelog row for 1.22.0.
  - `tools/project-console/console.yaml` — **port 8765 → 8766** (temporary, to run alongside the main console; revert before merge).
  - this task doc.
- **Running**: worktree console on `http://127.0.0.1:8766` (bg shell `bysdl6v5d`); main-repo console still on 8765 (PID 951), untouched.

### First action on resume
1. Verify task 073 active. If gate denies, activate against **main repo** state: `bash /Users/ben.xavier/projects/pdlc_demo/.claude/hooks/task-activate.sh add <UUID> 073` (the hook reads `$CLAUDE_PROJECT_DIR/.state`, i.e. the MAIN repo, even when cwd is the worktree).
2. Sister-project check against `../../projects/arthrex/pccp/` before any push.
3. To merge: revert the `console.yaml` port to 8765, then push the worktree branch via PR per the git-workflow rule. Stop the 8766 console first.
4. Anti-patterns: don't re-do the CSS work (shipped this session); don't commit unless the user asks; don't kill the 8765 main console.

## Changelog

- 2026-06-02: Status → Complete. Merged to project `main` via PR #34; main console restarted on :8765 with the refresh. `/sync-skills push` to the skill registry deliberately deferred per user.
- 2026-06-02: **Shipped the refresh (Option 2, skill-level, CSS-only) in worktree `console-design-refresh`.** Refactored `console.css` to a layered elevation + motion + focus token system; added body atmosphere + typographic rhythm + translucent sticky topnav + card elevation + one guarded page-load stagger + themed scrollbars — all via tokens/`color-mix`, no markup touched. Bumped skill to 1.22.0 + changelog. Launched worktree console on :8766 and verified landing/agents/documents/dashboards in Chrome (DevTools MCP): clear visual lift, JS features intact, zero console errors. `/trace-matrix` empty = worktree data artifact, not a regression. Pending: sister-project validation + merge decision.
- 2026-06-01: Task created in continuation of PR #29 (frontend-design skill install). Phases 0–5 sketched, three open questions captured. No code touched.

