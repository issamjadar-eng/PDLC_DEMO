# 076 — Tracker Dashboard frontend-design Refresh (brand-align + depth/motion)

**ID**: 076
**Created**: 2026-06-02
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the session drops, compacts, or ends, the next session must continue from this file alone.

1. Update at every meaningful checkpoint (HARD RULE).
2. Phase-end batching OK; drift-batching not.
3. A commit is not a substitute.
4. Resume-ready before any session boundary.
5. Capture strategy + lessons as they happen.

---

## Goals

Apply the `frontend-design` lens (chosen scope **R1 + R2**) to the **only** externally-generated dashboard the project-console embeds: the **submission tracker**, produced by the `tracker` skill's `scripts/render.py`. Follow-on to ben/073 (which refreshed the console's own `console.css`). The tracker renders in an **iframe**, so it's a separate document the 073 refresh never reached — its look is 100% owned by `render.py`'s embedded CSS.

- **R1 — Brand + font alignment.** Make `render.py` read the active console theme (`console.yaml` `theme:` → theme pack `theme.yaml`, following `extends:`) and inject `primary` (brand accent) + `font_body` into the dashboard `:root`. **Fallback to today's hardcoded slate+sky if no theme/console present** (keeps the skill standalone + project-agnostic per its README's "no external dependencies" stance). Considered remap — preserve hue separation between the new primary, the secondary, and the status colors so badges stay distinct.
- **R2 — Depth + motion + type refresh.** Same pass as 073: layered shadow scale, one `prefers-reduced-motion`-guarded page-load stagger (summary cards + phase sections), tighter heading rhythm.

## Boundary / Out of scope

- **R3 polish** (focus rings, scrollbars, transition cohesion) — deferred unless time permits.
- **No markup/JS contract changes** that would break the tracker's interactive filters / click-row expansion. CSS + `:root` injection only.
- **Project-agnostic**: `tracker` is registry-synced. Changes must generalize; validate against `../../projects/arthrex/pccp/` before any upstream push. The mismatch (dashboard accent = console secondary; system font vs Manrope) is captured below.

<!-- STRATEGY CONTENT: development, architecture; topics: tracker-dashboard-theming, iframe-style-isolation, skill-output-vs-source -->
### Key facts (grounding)

- Console brand (globallogic-dark): `primary #a855f7` (GL purple), `accent #38bdf8` (sky), font **Manrope**. Surfaces slate (from `dark` parent).
- Tracker `render.py` `:root` (line ~882): `--bg #0f172a --surface #1e293b --accent #38bdf8 (sky) --accent2 #818cf8 --eng #a78bfa`; font = `-apple-system` system stack; **no `@keyframes`, no `prefers-reduced-motion`**.
- → Surfaces match; **primary accent + font do not**. Dashboard reads as a sky-blue app inside a purple-brand app.
- The committed `docs/project/submissions/submission-tracker.html` is **regenerated output** — must re-run `/tracker render` to see changes; editing `render.py` alone doesn't update it.
- CSS source of truth: `_CSS_BASE_INNER` in `.claude/skills/tracker/scripts/render.py` (raw CSS, no `<style>` wrapper). Badge colors emitted dynamically (deterministic palette cycle) around lines 860–880.

## Todos

- [x] Read `render.py` `_CSS_BASE_INNER` + theme-resolution surface end-to-end before editing.
- [x] R1: theme-read helpers (`_read_theme_yaml`/`load_brand_theme`/`gen_theme_css`) — console.yaml → theme pack, follow `extends:`, regex-parsed (no YAML dep), `{}` fallback. Injected in both standalone + embed render paths.
- [x] R1: introduced `--brand` token (not a blind `--accent` swap) → repaints chrome only (header, active pills, scale h3, action-btn hover); data colors (status/scope/phase/effort) stay on sky/multi for badge distinction. **Bug caught + fixed**: comment-strip ate hex values (`"#a855f7"`→empty); fixed to strip only whitespace-preceded `#`.
- [x] R2: `--shadow-sm/md` on cards/categories/scale-section + one `prefers-reduced-motion`-guarded `pc-rise` stagger on summary cards (`backwards` fill, opacity:0 only inside no-preference) + tighter header tracking.
- [x] Bumped `tracker` SKILL.md `version: 11 → 13` (README changelog was already at 12; drift resolved forward) + README changelog row 13.
- [x] `/tracker render` regenerated `docs/project/submissions/submission-tracker.html` (524,262 B). Verified in Chrome at `/dashboards/submission-tracker`: active pills = `rgb(168,85,247)` (GL purple), `pc-rise` + shadow on cards, Manrope, **zero console errors**, filters/expansion intact.
- [x] **Pushed to project `main`** via PR #36 (merge `decd1d2`). `/sync-skills push` to the registry held off per user.

## Open Questions

- **Q1**: Push to project `main` after verify (like ben/073)? Skill-registry push held off regardless. (Default: ask after verify.)

## Resume

### In-flight artifacts (2026-06-02)
- Working in the **main repo** (no worktree this round). Branch: `main` (uncommitted). Nothing committed by Claude yet.
- **Files changed (uncommitted)**:
  - `.claude/skills/tracker/scripts/render.py` — R1+R2 (theme helpers, `--brand`/`--font`/shadow tokens, hero repointing, motion, theme injection).
  - `.claude/skills/tracker/SKILL.md` — version 11→13.
  - `.claude/skills/tracker/README.md` — changelog row 13.
  - `docs/project/submissions/submission-tracker.html` — **regenerated output** (524 KB) from the updated renderer.
  - this task doc + `tasks/ben/000-index.md` (076 row).
- Pre-existing unrelated change in tree: `tasks/ben/SECOPS.md` (not mine — leave alone).
- Console running on :8765 (PID from ben/073 restart); serves the regenerated dashboard.

### First action on resume
1. Verify 076 active (gate reads MAIN repo `.state`: `bash /Users/ben.xavier/projects/pdlc_demo/.claude/hooks/task-activate.sh add <UUID> 076`).
2. If pushing: branch, commit the 5 tracker/task files (NOT SECOPS.md), PR → merge to project `main`, delete branch. Hold `/sync-skills push`.
3. Anti-patterns: don't re-run the CSS work; the dashboard HTML is regenerated output (re-run `/tracker render` after any further render.py change, don't hand-edit the .html); don't push to the skill registry.

## Changelog

- 2026-06-02: Status → Complete. Pushed to project `main` via PR #36 (merge `decd1d2`). Registry `/sync-skills push` deferred per user. Note: a concurrent session created a colliding `tasks/ben/076-hipaa-advisor-grounding-gaps.md` + `077-...` (untracked, not mine) — numbering clash flagged to user for reconciliation.
- 2026-06-02: **Shipped R1+R2 in `tracker/scripts/render.py` (skill v13).** R1 brand/font alignment via `load_brand_theme()` reading the active console theme (`--brand` purple + Manrope injected into `:root`, both render paths, slate+sky fallback) — new `--brand` token repaints chrome only, data palette preserved. R2 shadow scale + guarded `pc-rise` page-load stagger + heading tracking. Fixed a hex-eating comment-strip bug in the theme parser. Re-rendered the dashboard; verified in Chrome (`/dashboards/submission-tracker`): GL-purple active pills, elevated+animated cards, Manrope, zero console errors, interactivity intact. Pending: push decision (Q1); `/sync-skills push` held off.
- 2026-06-02: Task created. Scope R1+R2 chosen by user. Grounding captured (console vs tracker palette/font mismatch; iframe isolation; output-vs-source). Follow-on to ben/073.
