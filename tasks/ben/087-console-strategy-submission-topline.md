# 087 — Console Strategy + Submission Topline Features

**ID**: 087
**Created**: 2026-06-15
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work, update this doc: tick the relevant Todo, add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker), update progress counts in Goals.
2. **Phase-end batching is OK; drift-batching is not.** Write at the phase boundary, before the next phase starts.
3. **A commit is not a substitute.** Git records code; this doc records the narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen** using `<!-- STRATEGY CONTENT: domain, topic -->` / `<!-- LESSONS LEARNED: category -->` blocks.

## Goals

Update the `project-console` skill and its scaffolded outputs to add two topline capabilities, mirroring the sister project `../arthrex-pccp` where it has built submission content:

1. **Strategy as a topline feature** — extracted from Workflows, surfaced as its own top-nav item **right after Overview**. Today strategy lives buried as workflow `B3 / strategy-reassembly` (`/workflows/strategy-reassembly`). Promote it to a first-class section.
2. **Submission as a first-class citizen** — new top-nav section that renders a **pretty view of the Q-Sub documents** plus **Ask-the-advisor** support (mirror the Gap Analysis drawer pattern shipped in ben/086).
3. Support the **content shape used in `../arthrex-pccp`** (do NOT modify the sister project). Possibly author a **new `submissions` skill** that generates Q-Sub content the way arthrex-pccp built it.

### Reference architecture (read 2026-06-15)
- Nav lives in `console/web/templates/_base.html`; gated by `request.state.*_nav` flags set in `app.py` middleware from `discover()` probes.
- **Gold-standard model = Gap Analysis** (ben/086): `gap_analysis/{loader.py,router.py}` + `gap_analysis_index.html` + `gap_analysis_view.html` + shared assistant drawer (`_assistant_drawer.html` / `_assistant_launcher.html`) mounted with an `assistant` config dict (`grounding_source: url:/.../grounding`, `default_agent`, etc.). Loose-coupled JSON sidecar contract under `docs/_analysis/`.
- **Strategy today** = `workflows/b3_strategy_reassembly.py` + `b3_session.py` (worktree sessions) rendered via `workflow_b3_index.html` (2498 lines, heavy JS calling `/workflows/strategy-reassembly/*` endpoints). Catalog entry `strategy-reassembly` (B3) in `workflows/catalog.py`.
- Submission docs in PDLC_DEMO are **scaffold-only** (`docs/project/submissions/qsub/` has READMEs only); real Q-Sub content + a generating pattern live in `../arthrex-pccp` (under investigation).
- Assistant drawer is generic: `data-grounding-source` supports `url:<rel>` mode; `default_agent` + `allowed_agents`. Submission default advisor → `regulatory-affairs`.

## Decisions (user-confirmed 2026-06-15)

1. **Strategy extraction → promote-in-place at `/strategy`.** Add a `Strategy` top-nav item right after Overview pointing to a new `/strategy` landing that **reuses the existing B3 strategy-reassembly view + machinery as-is** (no move of b3_* modules; POST endpoints stay at `/workflows/strategy-reassembly/*`). Remove the B3 card from the Workflows index. `/workflows/strategy-reassembly` GET → redirect to `/strategy`.
2. **Submission → console view + new `submissions` skill (scaffold + render).** Build the console Submission section (generic consumer of a JSON sidecar + Ask-the-advisor drawer mirroring ben/086) AND a new `submissions` skill with `scaffold` (arthrex-shaped qsub folder/doc stubs) + `render` (emit console sidecars). Agent-driven content generation deferred to a follow-up.
3. **Demo content → seed PP3500 Q-Sub content**, learning from `../arthrex-pccp` (esp. its `docs/project/strategies/pccp-qualification-framework.md` as source material). Banner every doc `_Demo sample data — not for clinical use._`.

## arthrex-pccp shape (read 2026-06-15, read-only)

- `docs/project/submissions/qsub/`: `composition-manifest.md` (🔒 INTERNAL — NOT TRANSMITTED; Required / Supporting / **Required-Pre-Meeting strengthener briefs** with transmission-blocking gates / Excluded + Filing Identification + Reviewer Sign-off + Changelog) + ~12 content docs (cover-letter, device-description, intended-use, fda-questions [12 Q's / 4 topics, per-question 🔒 anchors], pccp-summary, cybersecurity-scope-brief, mdds-rationale, postop-administrative-boundary, modification-protocol-{ai,non-ai}-template, separation-argument) + `_provenance/*.provenance.yml`.
- **Three-tier doc model**: HTML frontmatter (Confluence meta + AI-CHANGELOG + VERSION CHANGELOG) → `🔒 INTERNAL` working container → **filed body** (what goes to FDA) using 📤/📝/⏸️/📖 scope labels.
- **provenance.yml schema**: `doc, version, date, agent, task, sources_consulted[], fda_visible_references[], claims_to_source[], sources_not_consulted_but_potentially_relevant[], open_gaps[], notes[]`.
- `pccp-qualification-framework.md` = scoping guide (usage modes → canonical-source map → axioms A1–A9 → decision procedure Q0–Q7 + FDA flowcharts → worked examples → P-rule catalog). Teaches reasoning; decisions canonical in regulatory-strategy.md D-REG-* blocks.

## Console sidecar contract (new — produced by `submissions` skill `render`, consumed by console)

- `docs/project/submissions/.console/submission-index.json` — `{schema_version, generated, filings[]}` (id, type, title, status, folder, manifest, counts{required,supporting,strengtheners,excluded,docs}, blocking, default_advisor).
- `docs/project/submissions/<filing>/<filing>.submission.json` — `{schema_version, meta{id,type,title,device,filing_id,milestone,status,folder,default_advisor}, pieces{required[],supporting[],strengtheners[],excluded[]}, documents[]{id,title,kind,path,version,status,summary,sections[],provenance{}}, questions[]{id,topic,subject,position}, sign_off[]}`.
- Console renders each document's markdown body inline (via `documents/renderer.py`) in a tabbed viewer; pieces/questions/sign-off from sidecar; assistant drawer default `regulatory-affairs`, grounding `url:/submission/<filing>/grounding`. Loose-coupled: no sidecar → degrade to "run /submissions render".

## Build phases

- [x] **P1 — Strategy topline** (done): `console/strategy/{__init__,router}.py` (GET `/strategy` reuses b3 render via `_build_domain_views`; `discover` scans `*-strategy.md`); `_base.html` nav `Strategy` after Overview (+ `Submission` slot, gated); `app.py` import/include/`strategy_nav`; `workflows/router.py` strategy-reassembly GET → 307 redirect `/strategy` (+ `RedirectResponse` import); `catalog.py` `topline` flag on B3 + `grouped()` skips topline; `workflow_b3_index.html` breadcrumb/title topline-aware. py_compile clean.
- [x] **P2 — `submissions` skill** (done): `.claude/skills/submissions/` — `SKILL.md` (actions scaffold/render/list; three-tier doc model; console JSON contract `schema_version 1.0`; provenance schema), `scripts/render_sidecars.py` (stdlib producer; parses composition-manifest tables + content-doc frontmatter/headings + fda-questions + provenance → index.json + per-filing sidecars; tested against existing 510k manifest — parses 26 required pieces + sign-off), `templates/` (composition-manifest + cover-letter + device-description + intended-use + fda-questions + pccp-summary + provenance.template.yml), `README.md`, `VERSION=1`. Added `submissions` to `project.yml` approved_skills. Skill now discoverable.
- [x] **P3 — Seed PP3500 qsub content** (done): `docs/project/submissions/qsub/` — composition-manifest.md, cover-letter.md, device-description.md, intended-use.md, pccp-summary.md, fda-questions.md (6 Q's / 3 topics), 2 strengthener briefs (mdds-rationale, accessory-samd-brief), `_provenance/` README + 5 sidecars. Grounded in regulatory-strategy.md §§1–2 (PCA device alone; adapter MDDS; Drug Library Manager accessory SaMD; Ct* PCCP envelope); demo banners throughout. `render` produces qsub sidecar: 7 required / 2 supporting / 2 strengtheners (1 blocking) / 5 excluded / 7 docs / 6 questions. Fixed `blocking` substring bug ("not transmission-blocking").
- [x] **P4 — Console Submission section** (done): `console/submission/{__init__,loader,router}.py` (loader: discover/load_index/load_filing; router: index/detail/grounding/raw/render; inline doc-body rendering via documents renderer + cross-doc link rewrite to `/documents#path=`); `submission_index.html` + `submission_view.html` (Package/Documents/Questions tabs + assistant drawer, default `regulatory-affairs`, grounding `url:/submission/{id}/grounding`); `submission.css`; `_base.html` nav `Submission`; `app.py` import/include/`submission_nav`. Full app imports clean (88 routes).
- [x] **P5 — render + restart + smoke test** (done): console restarted via `start.sh`; all routes 200 (`/strategy`, `/submission`, `/submission/qsub`, grounding, raw; `/workflows/strategy-reassembly`→307→`/strategy`; B3 card gone from `/workflows`). Browser-verified Submission Package + Documents tabs (pretty inline markdown, scope labels, blocking banner, advisor launcher). Fixed: status `**` de-emphasis, doc reading order (cover-letter first), question-position extraction.
- [x] **P6 — docs + versioning** (done): project-console `VERSION` 1.26.0→**1.27.0**; SKILL.md frontmatter version + "ships" bullet + code-lives tree (`strategy/`, `submission/`) + new "Topline sections: Strategy & Submission" data-contract section; README.md changelog 1.27.0 entry; CLAUDE.md skills table + `submissions` row; `project.yml` approved_skills + `submissions`. Final checks: `render --check` clean (idempotent), app imports (88 routes).
- [x] **P7 — PROJECT PUSH (done)**: PR #56 merged to `main` — merge `c69b821`, work commit `54f753b`, branch deleted. (SECOPS.md left out — unrelated pre-existing change.)
- [x] **P8 — SKILL-REPO PUSH (done)**: cloned `hitachi` → `../hitachi` (was at `9e6a305` / project-console 1.26.0). `/sync-skills check --analyzed` confirmed the 9 modified project-console files were **LOCAL_AHEAD** (clean advance, no divergence); 19 new files LOCAL_ONLY. Pushed project-console (1.17.0→1.27.0) + the net-new `submissions` skill + `manifest.md` update (29 files) via **hitachi PR #217 → squash-merged `e93442f`**; local hitachi ff'd, sync branch deleted. Recorded in `.claude/sync-log.md`. Zsh gotcha: unquoted `$VAR` doesn't word-split — used `while read` to stage the file list.

## Resume / status (2026-06-15)

**All implementation complete and verified; nothing committed (working tree on `main`).** Console restarted via `start.sh` and serving the new sections on :8765. To resume: `bash .claude/hooks/task-activate.sh add <SESSION> 087`.

- **In-flight artifacts (uncommitted):** console pkg (`console/strategy/`, `console/submission/`, `app.py`, `_base.html`, `workflow_b3_index.html`, `workflows/{router,catalog}.py`, `web/static/submission.css`, `web/templates/submission_*.html`), VERSION/SKILL/README; new `.claude/skills/submissions/` skill; seeded `docs/project/submissions/qsub/*` + `_provenance/*` + `.console/*.json` sidecars; `project.yml`, `CLAUDE.md`, this task doc + index.
- **First action on resume:** if user says push → run the 6-step git-workflow sequence. Do NOT re-render or restart unless code changed.
- **Open:** (a) push not yet done (awaiting user); (b) `/sync-skills push` of project-console + the new submissions skill upstream is optional/deferred; (c) agent-driven `submissions generate` action is a deliberate follow-up (this pass shipped scaffold+render only).

## Changelog

- 2026-06-15: Task created. Read project-console SKILL.md + gap_analysis/overview/workflows/assistant architecture end-to-end. Launched Explore of `../arthrex-pccp` submissions shape. Mapped reference architecture (see Goals).
- 2026-06-15: User confirmed 3 decisions (promote-in-place /strategy; console+skill scaffold/render; seed PP3500 learning from arthrex pccp-qualification-framework). Read arthrex exemplars (qualification framework, composition-manifest, provenance schema).
- 2026-06-15: Post-build polish (still uncommitted): (a) topnav simplified — removed the "{project} Console" brand-name label + separator; company logo alone is the home link. (b) Fixed composition-manifest piece paths (relative `./x.md`) → repo-relative in `render_sidecars.py` so Package-tab links open in Documents.
- 2026-06-15: **Responsive priority-overflow nav (replaces the emoji icon-collapse approach).** Per user: monochrome **vector** SVG icons (inline `<symbol>` sprite, Lucide/MIT geometry, `currentColor`) + a far-right **hamburger** holding overflow. `topnav.js` measures on load/resize and moves lowest-priority items into the hamburger dropdown. Priority (left→right): Overview · Strategy · Submission · Dashboards · Trace Matrix · Gap Analysis · Workflows · Agents · Documents (user chose "Submission high, Documents low"). Bugs fixed during build: `justify-content:flex-end` hid right-overflow from `scrollWidth` (→ `flex-start`); `.nav-more-menu` `display:flex` defeated `[hidden]` (→ `[hidden]{display:none}` guard). Browser-verified: 1440 all-fit, 1230 → 7 visible + hamburger{Agents,Documents}, dropdown open/close. _(Note: `chrome-devtools` resize_page pins window.innerWidth so intermediate widths can't be screenshotted — verified via scrollWidth/clientWidth measurements instead; real browsers fire resize normally. Static `console.css`/`_base.html`: hard-refresh to see changes.)_
- 2026-06-15: **P1–P6 all complete in one session.** Built: Strategy topline (`/strategy` reusing B3), new `submissions` skill (scaffold/render/list + render_sidecars.py + templates), seeded PP3500 Q-Sub content (6 docs + 2 briefs + 5 provenance), console Submission section (loader/router/2 templates/submission.css + assistant drawer). Browser-verified Submission Package/Documents/Questions tabs + Strategy topline. Bumped project-console 1.26.0→1.27.0; updated SKILL/README/CLAUDE.md/project.yml. All routes 200; render idempotent; app imports clean. **Not committed — awaiting user push go-ahead.**
