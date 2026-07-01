# 081 — Console Gap-Analysis: Agent-Response Panels + Goals Banner

**ID**: 081
**Created**: 2026-06-04
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

Session-recovery point. Update at every checkpoint; capture strategy/lessons inline; resume-ready before any boundary.

## Goals

Enhance the **project-console** skill's Gap-Analysis detail view (built by ben/077) with two features the user asked for:

- **G1 — Agent-response visualization.** When an analysis exists, let a viewer read each agent's **full response** (the `recs-*.md` discipline-advisor docs + `kol-*.md` KOL-persona docs) inline as activatable **tabs/panels** — not just the one-line "what they contributed" summary. Design via `/frontend-design`.
- **G2 — Goals banner.** Show the analysis **Goal** (motivating question / decision it informs / stakeholders) at the **top** of the detail page.

Constraints:
- **project-console is company-agnostic** — discovery must be generic (sibling `recs-*.md`/`kol-*.md` + the `## Goal` section), no PCA/KOL hardcoding.
- Skill-versioning discipline: VERSION bump + README `## Changelog` + `## Best Practices` row.
- Sync into `tools/project-console/` (scaffold.py sync) + restart; `uvicorn --reload` does NOT watch the skill package ([[feedback_uvicorn_reload_scope]]).
- Read the skill before planning ([[feedback_read_skill_before_planning]]) — DONE (loader/router/view/CSS read end-to-end).

## Design decision (architecture)

Console-side discovery (no gap-analysis re-render needed), mirroring the existing `drift.json` sibling-discovery loose-coupling:
- `loader.py` resolves the analysis folder from `meta.source_md`, globs sibling `recs-*.md` / `kol-*.md`, matches each file to an agent by name-suffix, strips frontmatter, returns raw markdown per agent + the extracted `## Goal of this analysis` section markdown.
- `router._decorate_detail` renders those markdown chunks → HTML via existing `_md_to_html` (display-only; consistent with how findings `body_md` is already rendered).
- `gap_analysis_view.html` + `gap_analysis.css` render the Goals banner (top) + the agent-response tab/panel viewer.

## Todos

- [x] Read project-console SKILL.md + loader/router/view/CSS end-to-end
- [x] `/frontend-design` — designed the agent-response viewer (roster rail + reading pane) + goals "brief" banner, consistent with console aesthetic
- [x] loader: discover agent docs + goal section (`load_narratives`)
- [x] router: render markdown → HTML, group agents, pass to template
- [x] template + CSS: goals banner + agent-response viewer (+ JS for tab activation)
- [x] VERSION bump (1.23.2 → 1.24.0) + README changelog + Best Practices row
- [x] scaffold.py sync into tools/project-console + restart
- [x] Verify in Chrome (goals banner renders; each agent panel shows full response; tab-switch works)
- [x] Sister-project genericity sanity check (zero project-specific strings); checkpoint

## Outcome (2026-06-04 — complete)

**G1 — Agent-response viewer.** New "📄 Agent responses · read in full" section on the gap-analysis detail view: a **roster rail (vertical tabs) + reading pane** master-detail. Rail groups agents into **Discipline advisors** / **KOL panel**; clicking an agent activates their **full rendered write-up** in the pane (sibling `recs-*.md` / `kol-*.md`, frontmatter stripped, markdown→HTML). Vanilla-JS activation with roving-tabindex arrow-key nav + `#agent=<name>` deep-link. KOL `contributor` role got a new amber `.ga-role-badge.is-contributor`. Verified in Chrome: 12 agents (4 advisors + 8 KOLs), clicking Braithwaite swapped the pane to her full opinion.

**G2 — Goals banner.** Framed "Why this analysis exists" callout at the top: motivating question as a pull-quote, decision + stakeholders (as chips). Parsed generically from the aggregate's `## Goal` `- **Label:**` bullets.

**Architecture.** Console-side sibling-discovery (`loader.load_narratives`) + display-only markdown rendering in `router._decorate_detail` — **no gap-analysis re-render, no JSON-contract change**. Mirrors the trace-matrix `drift.json` loose-coupling. Files (4): `console/gap_analysis/loader.py`, `console/gap_analysis/router.py`, `console/web/templates/gap_analysis_view.html`, `console/web/static/gap_analysis.css`.

**Graceful degradation verified.** The HIPAA analysis has **no** `recs-*`/`kol-*` sibling docs → the agent viewer + its `<script>` are **omitted** entirely, while the goals banner still renders (it has a `## Goal` section). Both the goals parse and the agent discovery are **fully project-agnostic** (key off the gap-analysis skill's folder conventions + theme tokens; grep confirmed zero PCA/KOL-name/PP3500 hardcoding).

Screenshots in `_scratch/`: `081-goals-banner.png`, `081-agent-viewer-kol-active.png`, `081-detail-top-goals-and-viewer.png`, `081-hipaa-goals-no-viewer.png`.

<!-- LESSONS LEARNED: process -->
**Lesson (2026-06-04): adding a console feature ≠ changing the data contract.** Both features needed data the gap.json sidecar doesn't carry (the Goal section; the full agent docs). The tempting move was to enrich the gap-analysis renderer (producer) — but the console already had what it needed: `meta.source_md` gives the analysis folder, and the folder-per-analysis convention names the sibling docs. So I kept the entire change **console-side** (one skill, no re-render, no schema bump), discovering siblings the same way the console already discovers `drift.json`. **Why:** a contract change ripples (re-render every analysis, version both skills, risk consumers on old schema); sibling-discovery is additive and reversible. **How to apply:** before extending a producer's contract to feed a consumer feature, check whether the consumer can derive it from a path it already holds + an existing on-disk convention. [[feedback_uvicorn_reload_scope]]

## Iteration 2 (2026-06-04 — user follow-up)

User asked for two more refinements: (a) **Report / Advisors tabs** with the advisor full-responses moved into the Advisors tab (not inline); (b) **click an assertion → detailed view** with Positive/Neutral/Negative icons per advisor + a few-words summary.

**Cross-skill this time** (the per-advisor stance data didn't exist):
- **gap-analysis v6** (producer): optional `## Assertion positions` section (`### A<n>` → `- <stance> — <advisor>: <note>`), parsed by `attach_positions` in `render_sidecars.py` → additive `assertions[].positions[]` in the sidecar (`schema_version` stays 1.0). Authored the 37-position matrix for the commercial analysis (derived from the advisor/KOL responses). Template documents the convention (+ fixed a latent 4-vs-5-column mismatch in the template's assertions table example). SKILL.md v5→v6, README changelog.
- **project-console 1.25.0** (consumer): Report/Advisors top-level tabs (goals banner stays above, context for both; tab-less when no agent docs); agent viewer moved into the Advisors view; assertions became an accordion — expanding shows safeguard/evidence + a per-advisor positions list (avatar + Positive ▲/Neutral ◆/Negative ▼ chip + note) with a stance-dot strip on the collapsed summary. Cross-tab anchor handler (finding/assertion links from the Advisors tab switch back to Report, open the target, scroll). `router.STANCE_META` + position decoration; new `.ga-toptab*`/`.ga-view`/`.ga-assertion*`/`.ga-pos`/`.ga-stance*`/`.ga-sdot` CSS.

**Verified in Chrome**: A2 expands to 4 ▼ Negative advisor rows; tab-switch shows the Advisors viewer; HIPAA (no positions) degrades — tab-less, assertions expand to "no positions recorded".

<!-- LESSONS LEARNED: process -->
**Lesson (2026-06-04): grep the stylesheet for a class name before introducing it.** My stance dots were first named `.ga-dot` — which already existed as the index-card "·" separator (`opacity:.5`). The collision would have restyled the separator into a colored box AND washed out the new dots. Caught it by reading the linter-surfaced CSS before shipping; renamed to `.ga-sdot`. **Why:** a single shared stylesheet means class names are a global namespace; a "new" class that collides silently corrupts an unrelated component. **How to apply:** before adding a CSS class, `grep` the stylesheet for the bare name; prefer a section-scoped prefix when in doubt.

## Iteration 3 (2026-06-04 — HIPAA parity)

User asked to bring the **HIPAA analysis** up to parity (it had no agent full-responses, so the Advisors tab + assertion positions were empty/absent). Honest note: the HIPAA fan-out was a **prior session** (ben/077) that persisted only the merged findings — the advisors' full write-ups were never saved and are **not in this session's history**, so they couldn't be "retrieved." Instead I **regenerated** them: re-ran the 3 advisors (cybersecurity / regulatory-affairs / risk-management), each reading the existing aggregate and authoring a full `recs-*.md` **consistent with the findings it already contributed** (F-1…F-6 / F-7…F-10 / F-11…F-14), plus per-assertion stances. Authored the `## Assertion positions` section (25 positions across all 12 assertions) in the HIPAA aggregate; re-rendered. No skill-code change — purely analysis content the existing 1.25.0 console consumes. Verified in Chrome: HIPAA now shows Report/Advisors tabs (3 advisors), A8 expands to 3 mixed-stance advisor rows, the Advisors tab renders each full write-up. **Parity:** commercial = 12 agents / 37 positions / 12 full docs; HIPAA = 3 agents / 25 positions / 3 full docs.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-06-04 | Ben Xavier | Task created. Read console gap_analysis loader/router/view/CSS end-to-end; chose console-side sibling-discovery architecture (no gap-analysis re-render). Predecessor: the gap-analysis tab built under ben/077. |
| 2026-06-04 | Ben Xavier | **Iteration 3** — brought the HIPAA analysis to parity. Re-ran (regenerated, not retrieved — original fan-out was a prior session) the 3 advisors → `recs-cybersecurity.md` / `recs-regulatory-affairs.md` / `recs-risk-management.md` (full write-ups consistent with F-1…F-14); authored `## Assertion positions` (25 positions / 12 assertions); re-rendered; updated HIPAA folder README. No skill change. Verified in Chrome (Report/Advisors tabs, 3 advisors, A8 → 3 mixed-stance rows). Both analyses now at parity. |
| 2026-06-04 | Ben Xavier | **Iteration 2** — shipped gap-analysis **v6** (optional `## Assertion positions` → additive `assertions[].positions[]`) + project-console **1.25.0** (Report/Advisors top-level tabs with the agent viewer moved into the Advisors tab; assertion accordion with per-advisor Positive/Neutral/Negative + notes; cross-tab anchor handler; `.ga-sdot` rename to avoid `.ga-dot` collision). Authored the 37-position matrix in the commercial analysis; re-rendered. Synced console 1.24.0→1.25.0, restarted. Verified in Chrome (assertion A2 → 4 Negative advisor rows; Advisors tab viewer; HIPAA degrades tab-less + "no positions"). Both producer + consumer versioned with changelogs. |
| 2026-06-04 | Ben Xavier | Shipped project-console **1.24.0**: Goals "brief" banner + agent-response roster-rail/reading-pane viewer (designed via `/frontend-design`). `loader.load_narratives` (sibling `recs-*`/`kol-*` discovery + `## Goal` parse), `router._decorate_detail` (goal items + grouped agent docs + `_md_inline`/`_role_cls`), view template (banner + viewer + roving-tabindex script, guarded), `gap_analysis.css` (`.ga-goals*`/`.ga-av*`/`.is-contributor`). VERSION + README changelog + Best Practices row. Synced scaffold (1.21.1→1.24.0), restarted console. **Verified in Chrome**: commercial analysis shows goals banner + 12-agent viewer with working tab-switch; HIPAA analysis (no agent docs) shows goals banner + viewer correctly omitted. Zero project-specific leakage. Task complete. |
| 2026-06-08 | Ben Xavier | 2026-06-08: Confirmed Complete via task-doc audit — 3 iterations (console 1.24/1.25, gap-analysis v6); PR #45. Filed under Completed in 000-index.md. |

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 6,
    "todos": [
      {
        "todo": "Console gap-analysis agent panels",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 16,
          "max": 40
        },
        "confidence": "low",
        "basis": "console gap-analysis agent panels + goals banner"
      }
    ]
  }
}
```
