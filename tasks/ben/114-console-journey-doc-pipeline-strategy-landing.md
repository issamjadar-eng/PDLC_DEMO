# 114 — Console: Journey, Document Pipeline & Strategy Landing

**ID**: 114
**Created**: 2026-08-05
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
   - **when you tick a Todo off (or add/restructure Todos), fill/refresh the matching `## Economics` entry in the same edit** — the by-hand person-hours that unit would have taken, ranged + persona-tagged, per the rubric. **Checking the box is the estimate trigger** — don't defer it to a later checkpoint.
2. **Phase-end batching is OK; drift-batching is not.** Planned phases are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head, waiting for "end of the session," "after the push," or the user to ask.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** Option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, and corrected assumptions get written into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.
6. **Estimation provenance.** This doc's `## Economics` block is the by-hand person-hour estimate, built per the effort-estimation rubric at `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (owned by the `usage-metrics` skill). To add or refresh an estimate on resume — even without loading the task skill — read that rubric first for the anchors, personas, and JSON schema.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

Port three console surfaces from the **mega-chibi** sister project (`~/projects/mega-chibi`) into this project's console, adapting rather than copying. Both projects run a **fork** of the `project-console` skill — ours `1.58.0`, theirs `v65` — and the forks have diverged structurally.

| # | Surface | Outcome |
|---|---------|---------|
| A | **Strategy landing page** | `/strategy` becomes an index (roll-up + per-domain cards) with a `/strategy/{slug}` detail route, instead of one flat page that renders every domain at once |
| B | **Document Pipeline tab** | New `/doc-pipeline` — the documentation pipeline rendered live from artifacts owning skills already produce, across four lanes |
| C | **Journey tab** | New `/journey` — two phase groups (project standup + device program) with live artifact probes, driven by a **skill-owned map** |

**Progress**: 3 / 3 phases delivered (A ✅ · B ✅ · C ✅). Remaining: browser walkthrough with Ben, then push.

### Why this matters beyond the three tabs

The most valuable thing in the sister console is not a tab — it is an **ownership line**. Their Journey map lives in a *skill* (`gamedev-docs/registry/journey.yaml`) as declarative `done_when` predicates; the console only evaluates them. A hardcoded phase table in the console would make it the author of semantics it merely renders. Porting that IoC pattern is the point; the tabs are the demonstration.

## Decisions

<!-- STRATEGY CONTENT: architecture, console-surfaces, skill-ownership, tooling -->

**D1 — The Journey map is owned by `medtech-docs`, not the console.** New `.claude/skills/medtech-docs/registry/journey.yaml` carries per-phase `done_when` predicates, `requires` edges, `producer` commands and a binding `rendering:` block. The console evaluates authored predicates and decides nothing. Adding a phase = editing the yaml, never the loader. Mirrors `gamedev-docs/registry/journey.yaml` in the sister project.

**D2 — Artifact language, never completion language.** Journey states render as *artifacts present / partly present / next up / blocked / in the loop*. **No "complete", no "done", no bare ✓.** Every predicate detects an artifact, never its quality: a strategy doc can exist, probe green, and still be empty of real decisions. In a regulated project this matters more than in a game one — a confident checkmark teaches people to produce artifacts instead of decisions.

**D3 — Inverted discovery for Journey.** Every other tab lights only once its producer artifact exists. Journey's `discover()` returns true whenever the *map* exists — i.e. always. A journey tab that hides while the project is immature hides exactly when it is needed.

**D4 — Tab named "Document Pipeline", not "Docs Flow".** "Docs Flow" would collide with our existing `/docflow` skill (document conversion), which owns a different concept. Diverges deliberately from the sister project's name.

**D5 — Journey covers both journeys in one tab.** Group 1 = project standup (parsed from `new-project-bootstrap.md`). Group 2 = device program (from `docs/project/milestones/*.yml`). Different audiences, one surface, separate headers and separate focus markers.

**D6 — The program journey CONSUMES `/tracker`; it never re-derives readiness.** The tracker already computes per-milestone readiness, and per `tracker/SKILL.md:78` the **overlay wins at render time**. A second derivation would silently disagree with the tracker the team actually reads.

**D7 — Regulated-publish lane is built contract-first.** It has no data in this repo (see Findings). Ship the read contract + honest empty state + producer hint (~30 lines); it lights up when the mirror lands.

**D8 — Strategy coverage indicator is deliberately out of scope.** The sister's `console/strategies/coverage.py` reads `strategy/registry/domain-topics.yaml`, which our `strategy` skill does not have. Adding it means authoring a topic registry first — a separate decision.

## Findings from the pre-flight survey

<!-- LESSONS LEARNED: architecture, porting -->

**F1 — A "port" between diverged forks is an adaptation, not a copy.** Their console has `mdlite.py`, `navflags.py`, `tokens.css`/`shell.css` and a `console.manifest.yaml` build contract; ours has none. Only `mdlite.py` (32 lines, generic, no project data) is worth lifting verbatim. Every stage projection in their Docs Flow reads a *game* artifact and must be rewritten.

**F2 — Our strategy docs have a completely different shape from theirs, and we already own the right parser.** Their loader keys on `| D<N> |` ledger rows and status glyphs (✅🟢🟡⏸⤴⊖❓) plus an `## AI Assessment` section. Verified across all 8 `docs/project/strategies/*-strategy.md`: **0 ledger rows, 0 glyphs, 0 AI-Assessment sections.** Ours use `<!-- DECISION:start id=… status=… source=… -->` sentinels and `**Decision**:` prose — and `console/workflows/b3_strategy_reassembly.py` already parses exactly that (`scan()`, `parse_decisions()`, `_parse_proposals()`, `_parse_history()`). Phase A therefore needs **no new parsing**, only aggregation + a route split. Had this not been checked, the port would have shipped a second parser against a document shape we don't use.

**F3 — Two of the four Document Pipeline lanes have little or no data in this repo today.** Surveyed 2026-08-05:

| Lane | Data on disk | Verdict |
|---|---|---|
| Authoring | 8 strategies, 3 DHFs, `trace-matrix.yml` + `console_trace_matrix.json`, `dhf-manifest/*.json`, `submission-index.json`, `_analysis/index.json` | Renders rich |
| Ingestion / conversion | 90 `.md` under `docs/internal/source-md/`, 37 under `docs/external/` — but only **1 real binary** under `docs/internal/source/`, **0** files with a `docflow:` provenance block, **0** `.taxonomy.yml` | Counts render; provenance sub-panel empty |
| Regulated publish | **0** `_confluence/` dirs, **0** docs with `confluence:` frontmatter, **no** `docs/.change-control/state.json` | Empty state only |
| Terms + information flow | `glossary.md` + `CLAUDE.md` present | Renders |

The CLAUDE.md rule set (doctype-governance, ai-changelog, internal-vs-external scope labels) describes a Confluence-mirror world that **does not yet exist on disk here** — those rules are registry-shared and aspirational for this repo. Worth knowing before planning any surface that assumes the mirror.

**F5 — Only 1 of 8 strategy docs has been migrated to the v15 DECISION-block format, and the two decision formats MUST NOT be summed.** Surveyed 2026-08-06:

| Doc | v15 `DECISION:start` blocks | legacy `**Decision**:` lines | header status |
|---|---|---|---|
| commercial | 9 | 9 | assembled |
| regulatory | 0 | 5 | assembled |
| architecture | 0 | 3 | assembled |
| development, operations, postmarket, risk, testing | 0 | 0 | `awaiting-content` |

Two traps here, either of which produces a landing page that lies:

1. **Counting only v15 blocks** reports regulatory and architecture as "0 decided" — false, they carry 5 and 3 real decisions in legacy prose. Those are the two most substantial regulatory documents in the project.
2. **Summing the two** reports commercial as 18. Verified programmatically: **all 9 legacy lines sit *inside* the 9 v15 blocks** — the v15 sentinels wrap the legacy prose rather than replacing it.

Counting rule adopted: **`v15 if v15 > 0 else legacy`**, never a sum — and the card labels which format it counted, because a v15 block carries a lifecycle `status=` and a legacy line carries none. They are different evidence classes and the UI must not imply otherwise (same discipline as D2).

**F6 — The on-disk DHF manifest is a stale pre-v7 artifact, and the fields that look like coverage are retired.** `docs/project/dhf-manifest/pdlc-demo-dhf-manifest.json` was generated **2026-04-27**. Every one of its 437 obligations reads `status: GAP` with `location: null`, which looks like a 0%-coverage signal and is not one.

Per `dhf-manifest/SKILL.md:14` (v7, task ben/158 Phase 1): **`status` and `location` were removed from per-obligation entries**, and "coverage / lifecycle / evidence-binding [are] now exclusively the responsibility of `/tracker assess`". The installed manifest predates that clean break — it has no `obligation_set_hash`, no `canonical_role`, no `criticality`. The v7 coverage sidecar (`submission-tracker.agent.json`) is **absent**.

So the Document Pipeline's manifest stage:
- reports obligation **counts** (that is the catalog's own job — 114 source obligations projected to 437 across 9 DHFs),
- **never** derives coverage from `status`/`location` — that would render a retired contract as though it were live,
- surfaces the staleness (generated date + pre-v7 schema) and points coverage at `/tracker assess`.

Reading the SKILL.md before the JSON is what caught this; the JSON alone reads as a confident, fully-populated coverage dataset.

**F8 — A predicate lifted from the sister map was wrong for this project, and only checking `project.yml` caught it.** The standup Phase 1 predicate started as `yaml_nonempty: {file: project.yml, key: registries.0.repo}` — carried across from the sister map. In this project `registries[0]` is the **`anthropic` builtin entry, which has no `repo` key**; the fetchable `github` registry is `registries[1]`. The probe reported a correctly configured project as unconfigured. Replaced with a `registry_configured` derivation that asks a **set** question ("is there an entry of type `github` with a `repo`?") rather than a positional one. The general lesson: a registry list is a set, and a positional index into a set is an assumption about ordering nobody guaranteed.

**F9 — Binary phase states are wrong for milestones, and the default model made the whole program read as finished.** With the standup group's present/partial/ready/blocked model applied to the device-program group, all four regulatory milestones rendered **"artifacts present"** — because each had ~13 tracker rows in Drafting, which satisfied the predicate. Read literally, the console claimed the 510(k), LMR1 and LMR2 were all done. A regulatory milestone completes when a package is **filed and a regulator responds** — nothing in the repo can observe that. Added `state_model: evidence-gauge` to the map: milestones render **in-motion / next-up / blocked**, never "present", and carry a row-count bar explicitly labelled *not a readiness verdict*. This is the same failure class as D2, one level up: D2 stops a single artifact reading as complete; F9 stops a whole program reading as complete.

**F7 — A data key that shadows a dict method is a template landmine.** The trace stage originally returned a key named `items`. Jinja resolves **attribute access before item lookup**, so `{{ d.items }}` returned the bound `dict.items` method and rendered `<built-in method items of dict object at 0x…>` on the page — while `data.json` and the grounding text (both using subscript access) were perfectly correct. Renamed to `traced_items`. The class to avoid in any loader feeding a Jinja template: `items`, `keys`, `values`, `get`, `update`, `pop`, `copy`.

**F4 — A `discover()` that raises 500s every route.** The nav middleware (`console/app.py:107-123`) has no try/except around the probes. The sister learned this the hard way (`journey/loader.py:73-80` is wrapped for exactly this reason). Every new probe must be wrapped.

**F10 — Adding two nav entries silently evicted a third (found post-delivery, 2026-08-06).** The topnav is priority-ordered with hamburger overflow (`_base.html` L44–46). Journey (position 2) and Pipeline (position 8) landed on the high-priority left; at a ~1640px viewport only **9 of 15** entries fit, so the additions pushed **Metrics** — then 14th, just before Setup — out of the visible bar and into the overflow menu. No route broke, nothing logged, nothing errored; the tab was still reachable under the hamburger. The only signal was a person reporting the Metrics tab "no longer showing", and that report *also* had a genuine second cause (corrupt `usage.json`, ben/112) which masked this one during diagnosis. Fixed by moving Metrics to position 7 beside Dashboards with its own `ic-metrics` symbol. F10 is the nav-level sibling of F4: F4 is one section's failure taking down every route, F10 is one section's *addition* removing another section's entry. **Rule going forward: a nav insertion must name what it displaces, verified in a browser — the template can't show you, only layout can.**

## Todos

### Phase A — Strategy landing page ✅ delivered 2026-08-06
- [x] `console/strategy/loader.py` — per-domain summaries over the existing `b3_strategy_reassembly` parsers. Counting rule `v15 if v15 else legacy` (F5); `_intent_line()` reads `## Scope & Approach` with a preamble fallback. No document rendering.
- [x] `web/templates/strategy_index.html` + `web/static/strategy_index.css` — roll-up strip, per-domain cards, lifecycle bar, format chip, mixed-format advisory
- [x] Split routes in `console/strategy/router.py`: `/strategy` → index, `/strategy/{slug}` → `workflow_b3_index.html` opened on that domain via new `active_slug`; `?domain=` redirects; unknown slug redirects to index. B3 mutation machinery untouched.

### Phase B — Document Pipeline tab ✅ delivered 2026-08-06
- [x] `console/doc_pipeline/{__init__,loader,router}.py` — `discover()` on `docs/README.md`; 15s TTL module cache; all values derived at request time; no mutation or refresh endpoint by design
- [x] Lane 1 (authoring, 7 stages): input-analysis (21) → strategies (17 decisions, **imports Phase A's loader**) → design controls (10 DHFs, 119 docs, paths from `project.yml dhfs[].path`) → trace (302 items, 53 orphans) → obligations (437, **counts only — see F6**) → gaps (3) → submission (2 filings, 1 blocking)
- [x] Lane 2 (ingestion): 1 binary source vs 72 QMS markdown vs 31 distilled references, plus a `docflow:` provenance count that reports **authored-not-converted** rather than a fake ratio
- [x] Lane 3 (regulated publish, contract-first): reads `docs/.change-control/state.json` else `state:` frontmatter; 5-state lifecycle rendered with only populated states lit; currently an honest empty state + `/change-control` hint
- [x] Lane 4 (terms + information flow): 14 terms from `glossary.md`; External→Project←Internal projected from `CLAUDE.md § Information Flow` (parsed, never copied)
- [x] `web/templates/doc_pipeline.html` + `web/static/doc_pipeline.css`; routes `/doc-pipeline`, `/doc-pipeline/data.json`, `/doc-pipeline/grounding`

### Phase C — Journey tab ✅ delivered 2026-08-06
- [x] `.claude/skills/medtech-docs/registry/journey.yaml` — **new skill-owned map**: 11 standup phases + a milestone-expanded program group, full predicate vocabulary, 6 derivations, binding `rendering:` contract. First file in a new `medtech-docs/registry/` directory.
- [x] `console/journey/{__init__,loader,router}.py` — predicate evaluator + guide parser (`^## Phase (\S+) — (.+)$` against `new-project-bootstrap.md`, fence-aware); 2s TTL (deliberately not the pipeline's 15s); wrapped `discover()` with inverted semantics
- [x] Group 2 reads the `/tracker` **published** artifacts (`row-source.json` × `overlay.yml`) and emits **no readiness verdict** — that stays `/tracker assess`'s
- [x] `web/templates/journey.html` + `web/static/journey.css`; routes `/journey`, `/journey/data.json`, `/journey/grounding`

### Shared wiring & close-out
- [x] `console/mdlite.py` lifted verbatim from the sister console
- [x] `console/app.py` — 2 new sections wired + **`_nav_probe()` guard retrofitted across all 8 probes**; `_base.html` nav entries + `ic-journey` / `ic-pipeline` icons
- [x] Version bump `1.58.0` → `1.59.0`; `SKILL.md` section blocks (Journey, Document Pipeline, reshaped Strategy, description, code map) + `README.md` changelog row
- [x] Verification sweep — 22 routes all 200, zero exceptions, artifact-language audit clean, empty-state + missing-map degradation proven
- [x] **Pipeline readability + styling pass (2026-08-10, user-driven).** Type scale collapsed 12 ad-hoc sizes → 5 steps; three ink roles instead of two; tabular figures; dot leaders on every label↔value row; lane rules; card grid rewritten to 6 explicit rows so all 7 metrics share a baseline and footers pin; producer commands demoted from near-black blocks to dashed muted tokens; one `.dp-flag` treatment everywhere; publish states became a connected track; ingestion columns got dividers. **Lane height 406px → 237px, dead space per card 264px → 12–36px.** Icons added to all 7 stage cards, the 3 ingestion columns and the 4 lane headings via a page-local 24-grid sprite (`dp-ic-*`), matching the nav's stroke weight.
- [x] **Fixed an information-flow parser bug found during the styling pass** — see F11 below.
- [ ] Browser walkthrough with Ben
- [ ] Push per `.claude/rules/git-workflow.md`; then consider `/sync-skills push` (registry-shared skill)

## Verification

Run after **each** phase, not only at the end:

1. `bash tools/project-console/start.sh` — restart is required after every skill-code edit (`uvicorn --reload` does **not** watch the skill package).
2. Route smoke — 200 from `/strategy`, `/strategy/regulatory`, `/doc-pipeline`, `/doc-pipeline/data.json`, `/journey`, `/journey/data.json`, both `/grounding` routes.
3. Regression — same check across all 7 existing sections (`/overview`, `/submission`, `/commercial`, `/gap-analysis`, `/tasks`, `/metrics`, `/setup`). A broken `discover()` surfaces here first (F4).
4. Empty-state proof — temporarily rename an input (e.g. `docs/_analysis/index.json`); confirm the stage degrades to a producer hint rather than 500ing. Restore.
5. **Artifact-language audit** — grep rendered `/journey` HTML + `/journey/grounding` for `complete`, `done`, `finished`, `✓`. Any hit is a defect against D2.
6. Cross-check against producers — Strategy roll-up counts must match `/strategy/{slug}`; Journey program group must agree with `submission-tracker.html` rendered in a **PyYAML-enabled** env (per `tracker/SKILL.md:82` a bare interpreter silently skips the overlay, and the two will disagree).
7. Browser walkthrough with Ben before push.

## Open Questions

- None blocking. Scope decisions D1–D8 were settled with Ben at planning time (2026-08-05).

## Resume

### In-flight artifacts

All three phases are **built, live-verified, and uncommitted**. The console is running on http://127.0.0.1:8765 (restarted via `start.sh` during verification).

Uncommitted and belonging to this task:

| State | Path |
|---|---|
| new | `.claude/skills/medtech-docs/registry/journey.yaml` (the map — first file in a new `registry/` dir) |
| new | `.claude/skills/project-console/console/{journey,doc_pipeline}/` (loader + router each) |
| new | `.claude/skills/project-console/console/{mdlite.py,strategy/loader.py}` |
| new | `console/web/templates/{journey,doc_pipeline,strategy_index}.html` |
| new | `console/web/static/{journey,doc_pipeline,strategy_index}.css` |
| new | this task doc |
| modified | `console/app.py` (2 sections wired + `_nav_probe` retrofit), `console/strategy/router.py` (route split), `console/web/templates/{_base.html,workflow_b3_index.html}` |
| modified | `SKILL.md`, `README.md`, `VERSION` (1.59.0) |
| modified | `tasks/ben/103-console-setup-tab-connectors.md` (retroactive close) |

**Already on `main` — committed by another session.** A concurrent session working task 113 swept `tasks/ben/000-index.md` into its own close-out commit (`83f1ced`, merged via PR #177), which carried this task's index edits with it: the 114 row, the 103 Active→Completed move, and both changelog lines. Verified correct on HEAD. Nothing to redo — but **do not re-apply those index edits**, and expect the same when two sessions touch shared files. Task 103's own `.md` status flip is still uncommitted here.

**Do not sweep into this task's commit:** `tasks/ben/_usage-metrics/**`, `tools/usage-metrics/**`, `tasks/ben/SECOPS.md` — all modified by hooks/other work, unrelated to this task.

Reference source for the port: `~/projects/mega-chibi/.claude/skills/project-console/` — `console/journey/{loader,router}.py`, `console/docs_flow/loader.py`, `console/strategies/{loader,router}.py`, `console/mdlite.py`, and `.claude/skills/gamedev-docs/registry/journey.yaml`.

### First action on resume

1. **Browser walkthrough with Ben** — `/journey` (both groups), `/doc-pipeline` (four lanes), `/strategy` + one domain drill-down. This is the only outstanding acceptance step.
2. **Push** per `.claude/rules/git-workflow.md`: commit **only** the paths in the table above, then branch → PR → auto-merge → delete branch.
3. Then consider `/sync-skills push` — `project-console` and `medtech-docs` are both registry-shared, so the sister projects can take the three surfaces (and the journey-map pattern) too.
4. Activation: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 114`

## Economics

_By-hand person-hour estimate, **filled at checkpoint** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated; an empty `todos` list is ignored by the aggregator._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {"min": 3, "max": 4.5},
    "todos": [
      {
        "todo": "Strategy landing loader — per-domain aggregation over existing parsers, incl. the two-format counting rule and scope-section intent extraction",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 4, "max": 7},
        "confidence": "med",
        "basis": "software anchor as a sanity bound (~180 lines incl. comments) but internal-tooling Python sits well below IEC 62304 rates; the real cost here was investigative, not typing — establishing that two decision formats coexist and that the v15 sentinels WRAP the legacy prose (so counts must not be summed) took more effort than the code it produced"
      },
      {
        "todo": "Index template + theme-token CSS (roll-up, cards, lifecycle bar, format chip, mixed-format advisory, empty state)",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 3, "max": 5},
        "confidence": "med",
        "basis": "~195 lines of Jinja + CSS against an existing house idiom (gap_analysis_index.html); model judgment on the low multiplier since the pattern was copied rather than designed"
      },
      {
        "todo": "Route split with backward compatibility (active_slug, ?domain= redirect, unknown-slug redirect, single discover() definition) + verification sweep",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 2, "max": 4},
        "confidence": "high",
        "basis": "small routing change plus a 15-route smoke + regression sweep and a multiline-markup active-pane assertion; judgment, low end"
      },
      {
        "todo": "Document Pipeline lane 1 — seven authoring stage projections over six different producer artifacts (input-analysis tree, strategy loader, project.yml dhfs[], trace sidecars, dhf-manifest, gap index, submission index)",
        "personas": ["rd-lead", "quality-engineering"],
        "manual_hours": {"min": 8, "max": 14},
        "confidence": "med",
        "basis": "seven independent readers each needing its producer's schema established first; the dhf-manifest stage alone required reading the owning SKILL.md to discover that the fields that look like coverage were retired in v7 (F6) — that determination is quality-engineering work, not typing, and is the reason the range is wide"
      },
      {
        "todo": "Document Pipeline lanes 2-4 — ingestion corpus + docflow provenance, contract-first change-control lifecycle, glossary terms + CLAUDE.md information-flow projection",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 5, "max": 8},
        "confidence": "med",
        "basis": "three smaller readers plus two regex projections against canonical files; includes deciding the honest framing for a corpus that was authored rather than converted, and building a lane against a contract with no data behind it yet"
      },
      {
        "todo": "Pipeline template + CSS (7-stage flow, 3 panels, lifecycle strip, terms fold) + app wiring incl. the _nav_probe guard retrofit across all 8 sections",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 5, "max": 9},
        "confidence": "med",
        "basis": "~200 lines Jinja + ~170 CSS with per-stage branching, plus nav/icon wiring; the _nav_probe retrofit is small but removes a whole-console failure mode (F4)"
      },
      {
        "todo": "Phase B verification — 18-route smoke + regression, empty-state proof by removing two inputs and restoring, grounding-text review, Jinja dict-method collision fix (F7)",
        "personas": ["rd-lead", "vnv-lead"],
        "manual_hours": {"min": 3, "max": 5},
        "confidence": "high",
        "basis": "test anchors, low end; the degradation proof (rename inputs → expect dimmed stages + producer hints → restore) is the check that would have caught a 500-on-missing-artifact regression"
      },
      {
        "todo": "Journey map authoring — 11 standup phases with verified predicates, milestone-expanded program group, 6 derivations, and the binding rendering contract",
        "personas": ["rd-lead", "quality-engineering", "regulatory-affairs"],
        "manual_hours": {"min": 8, "max": 14},
        "confidence": "med",
        "basis": "document-authoring anchor is the wrong frame — this is a declarative spec whose cost is per-predicate VERIFICATION against real repo state, not prose volume. Every one of ~15 predicates had to be checked to not lie (F8 is what one unverified lifted predicate costs). The regulatory-affairs persona is on here because deciding that a milestone can never render 'complete' (F9) is a regulatory judgment, not an engineering one"
      },
      {
        "todo": "Journey loader — predicate evaluator, fence-aware guide parser, 6 derivations, two-pass state resolution, evidence-gauge state model",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 7, "max": 12},
        "confidence": "med",
        "basis": "~560 lines incl. comments; the tracker-consumption derivation required establishing the row-source × overlay join and deciding what NOT to compute (readiness), which is design rather than code volume"
      },
      {
        "todo": "Journey template + CSS + wiring, and the artifact-language discipline enforced through all three (page, stylesheet, grounding text)",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 4, "max": 7},
        "confidence": "med",
        "basis": "~150 Jinja + ~160 CSS; the no-checkmark/no-green-done constraint is a real design cost — the usual visual vocabulary for 'this step is satisfied' is exactly what had to be avoided"
      },
      {
        "todo": "Phase C verification + close-out — artifact-language audit, missing-map degradation proof, 22-route final sweep, VERSION bump, SKILL.md sections, README changelog",
        "personas": ["rd-lead", "vnv-lead"],
        "manual_hours": {"min": 4, "max": 7},
        "confidence": "high",
        "basis": "test + document-authoring anchors; the SKILL.md sections are substantial because they carry the four Journey contracts and the two deliberate non-computations, which is the durable record of why the code refuses to do obvious things"
      }
    ]
  }
}
```

## Changelog

- 2026-08-10: **Pipeline readability + styling pass, plus F11 (a real parser bug the restyle surfaced).**

  *Why the page was hard to read.* Three structural causes, none of them decorative. (1) **Twelve font sizes** between .68 and .87rem — differences too small to read as hierarchy, large enough to read as sloppiness. (2) **Two ink colours only** — a row label and its value carried identical emphasis, so the eye had nothing to follow across a gap of up to 120px. (3) **One card set the height of the lane.** Obligations carried a coverage note, a schema flag and a producer command stacked in a 172px column; the other six cards were stretched around ~200px of empty box, which reads as missing data rather than as alignment.

  *What was done.* Five-step type scale and three ink roles as tokens; tabular figures throughout; dot leaders on every label↔value row; lane headings given a rule to the right edge so the four lanes chunk; the stage card rewritten as a 6-row grid with explicit row assignment (head / metric / detail / advisory / command / link) so every metric shares a baseline and every footer pins regardless of how much detail a card carries; the detail zone capped and scrollable; producer commands demoted from near-black filled blocks — previously the visually heaviest thing on the page while being the least important — to dashed muted tokens; one `.dp-flag` treatment replacing two inconsistent amber styles; the publish lane's five detached boxes merged into one connected track; ingestion columns separated by hairlines and the over-long binary filename truncated with a `title`. **Result: lane height 406px → 237px, per-card dead space 264px → 12–36px, no horizontal page scroll at 760px or 1960px.**

  *Icons (user request, mid-pass).* All 7 stage cards, the 3 ingestion columns and the 4 lane headings, from a new page-local `dp-ic-*` sprite on the same 24-grid and 1.75 stroke as the nav, following the `setup_view.html` page-local-sprite precedent. They are `aria-hidden` and set in muted ink, never the accent — they exist to anchor the eye across seven near-identical cards, not to encode anything the label doesn't already say.

  *Advisories moved to a lane footnote strip.* The obligations caveat needed a paragraph; in a 172px card that is six lines and it dragged the whole lane. It now renders once at full width beneath the lane (one line), with an amber `●` marker on the card linking down to it. No wording was cut — the honesty contract in the loader header is preserved, and the text is now more legible than it was in the card.

- 2026-08-10: **F11 — `_lane_information_flow()` leaked raw markdown into the "project" tier.** The section regex terminated on `^##\s`, which requires whitespace after the second `#`. `### Project Manifest` is `##` followed by `#`, so it never matched; the captured body ran on past every subsection until the next level-2 heading. The project tier therefore rendered its own description *plus* a heading, bold markers and a markdown table (`… The heart of the DHF. ### Project Manifest — \`project.yml\` … **single source of truth** … | Section | Purpose | |-----|---`). Fixed by terminating on `^#{2,}\s` (any heading of level 2 or deeper) and, as defence in depth, adding `^#{1,6}\s` to the per-tier lookahead so a future subsection cannot leak into the last tier even if the section regex is loosened again. Verified: project tier 113 chars, no `###` / `**` / table pipes in any tier. **This was invisible until the restyle** — in the old sheet the tier text was one more block of small muted prose, so nobody read far enough to notice it was quoting CLAUDE.md's manifest table.

<!-- LESSONS LEARNED: console, ui, parsing -->
**Lesson — a "styling" complaint can be a correctness signal.** The user asked for professional styling on the Pipeline page. Two of the changes that made the biggest difference were not styling at all: one card's verbose advisory was setting the height of six others (a layout-contract problem), and the information-flow tier text was silently quoting a markdown table out of CLAUDE.md (F11, a parser bug). Both had been on the page since the tab shipped and neither had been reported, because unreadable prose does not get read — the defect was *hidden by* the poor legibility. **How to apply:** when asked to restyle a data view, read the rendered values as a user would before touching the CSS, and treat anything that does not parse as a sentence as a candidate bug rather than a candidate font size. The restyle is also the cheapest moment to find these, since every value gets looked at once anyway.
<!-- /LESSONS -->

<!-- STRATEGY CONTENT: architecture, console-card-layout, long-caveat-placement -->
**Strategy — long advisories belong to the lane, not the card (architecture).** Decision: in a fixed-height card row, any caveat needing more than about two lines renders in a **footnote strip beneath the lane**, with a marker on the originating card linking to it. Rationale: card rows are equal-height by construction, so the most verbose card silently taxes every sibling — one 6-line advisory in a 172px column cost the Pipeline lane 169px of height across seven cards. The alternatives were worse: truncating the text loses the honesty the loader's contract requires; hiding it behind a `<details>` fold makes a load-bearing caveat opt-in; letting cards size independently gives a ragged row that reads as broken. A footnote strip keeps the text verbatim, at full width where it costs one line, and keeps the card dense. Applies to any future console lane built on equal-height cards, not just this page.
<!-- /STRATEGY -->

- 2026-08-06: **Fixed a nav regression this task caused — F10.** The topnav is **priority-ordered** (`_base.html` L44–46: left→right = highest→lowest; whatever doesn't fit is pushed into the far-right hamburger). Phases B and C inserted **Journey at position 2 and Pipeline at position 8**, both on the high-priority left — which displaced ~167px off the right edge and pushed **Metrics** (then 14th of 15) out of the visible bar into the overflow menu. To the team this read as "the Metrics tab disappeared", and it was the *visible* half of a two-cause failure (the other half was corrupt `usage.json` — see ben/112). Verified in-browser: before the fix the bar showed 9 items and the overflow held `Workflows, Agents, Documents, Tasks, Metrics, Setup`. Moved Metrics to position 7, directly beside Dashboards — same class of surface (read the numbers), and far enough left to survive future insertions. Gave it a distinct `ic-metrics` symbol (trending line + rising point); it had been reusing `#ic-dashboards`, which would have rendered two identical icons side by side. **Cost, stated plainly:** at ~1640px viewport only 9 items fit, so `Gap Analysis` took the seat Metrics vacated and is now first in the overflow menu. Nothing was lost — the hamburger still lists everything — but if Gap Analysis should outrank Metrics, that's a one-line reorder.
- 2026-08-06: **Widened the Pipeline page to 98% of viewport.** Two caps were stacked: the console-wide `main { max-width: 1040px }` (Pipeline is not in the `body.<x>-page` break-out list) and `.dp-wrap { max-width: 1320px }` in `doc_pipeline.css`. The inner cap would have silently won any change made only to `main`, so both were addressed: `body.pipeline-page main` joins `body.metrics-body main` at `max-width: 98%`, and `.dp-wrap` drops to `max-width: none; padding: 0` with a comment naming `main` as the owner of width — one cap, one place. All 7 authoring-lane stage cards now sit on a single row instead of wrapping. Verified: main = 98.0% of body width, no horizontal overflow, zero console errors.

<!-- LESSONS LEARNED: console, ui, regression -->

**Adding a tab to a priority-ordered nav silently evicts one from the far end.** Phases B and C each added a nav entry on the left and neither checked what fell off the right. The evicted tab (Metrics) was still reachable via the hamburger, so nothing errored, nothing logged, and no route broke — the only signal was a teammate saying a tab was "no longer showing."

**Why:** The overflow behaviour is *correct* and by design; the failure was treating a nav insertion as additive when the visible set is fixed-capacity. It is a zero-sum list, and the cost lands on whatever sits rightmost — which is by definition the thing nobody was thinking about while adding the new tab.

**How to apply:**
- When adding a nav entry, state where it sits in priority order **and** name what it displaces. If you can't name the displaced item, you haven't checked.
- Verify in a browser at a realistic viewport, not from the template: the template lists 15 items and looks fine; only layout reveals that 9 fit.
- `[...document.querySelectorAll('.nav-more-menu a')].map(a => a.textContent.trim())` is the one-line check for what got pushed into overflow.
- Generalize: any fixed-capacity, priority-ordered surface (nav bars, dashboard card rows, summary strips) turns an addition into a silent removal. Treat "what did this evict?" as part of the definition of done.

- 2026-08-06: **Phase C delivered** — Journey tab at `/journey`, plus close-out. New **skill-owned map** at `.claude/skills/medtech-docs/registry/journey.yaml` (first file in a new `registry/` dir): 11 standup phases with anchors into `new-project-bootstrap.md`, a program group expanded from `docs/project/milestones/regulatory.yml`, 6 derivations, and a binding `rendering:` contract. New `console/journey/{loader,router}.py`, `journey.html`, `journey.css`; wired into `app.py` + `_base.html` with the `ic-journey` icon. Live-verified: standup reads 10 present + 1 looping (focus = Phase 9, the sync loop); program reads 4 in-motion (focus = qsub-release) with per-milestone evidence bars. **Artifact-language audit clean** — zero occurrences of complete/done/finished/✓ in the rendered page, CSS or grounding text apart from the prohibitions themselves. **Missing-map degradation proven**: removing the map hid the nav entry, served an honest empty state at 200, and left every other route working; restoring brought it back. Close-out: `console/mdlite.py` lifted, `_nav_probe()` guard retrofitted across all 8 nav probes, VERSION 1.58.0 → **1.59.0**, SKILL.md gained Journey + Document Pipeline sections and a reshaped Strategy section, README changelog row added. Final sweep: **22 routes all 200, zero server exceptions**. **Uncommitted.**
- 2026-08-06: Phase C caught two more traps, recorded as F8 and F9. **F8**: the Phase 1 predicate carried over from the sister map (`registries.0.repo`) was wrong here — `registries[0]` is the `anthropic` builtin with no `repo` key, so a correctly configured project reported as unconfigured; replaced with a set-question derivation. **F9** (the most consequential of the whole task): under the default binary state model all four regulatory milestones rendered "artifacts present" because each had ~13 rows in Drafting — the console was claiming the 510(k), LMR1 and LMR2 were finished. Added `state_model: evidence-gauge` so milestones read in-motion/next-up/blocked and never "present".
- 2026-08-06: **Phase B delivered** — Document Pipeline tab at `/doc-pipeline`. New `console/doc_pipeline/{loader,router}.py`, `web/templates/doc_pipeline.html`, `web/static/doc_pipeline.css`, `console/mdlite.py` (lifted verbatim from the sister console); `console/app.py` gained the import/nav/router wiring and a new `_nav_probe()` guard **retrofitted across all 8 sections** (F4 — an unguarded probe 500s every route, not just its own tab); `_base.html` gained the `ic-pipeline` icon + nav entry. Live-verified: all 7 authoring stages present (21 input docs · 17 decisions · 10 DHFs/119 docs · 302 traced items/53 orphans · 437 obligations · 3 analyses · 2 filings/1 blocking); ingestion reports authored-not-converted; publish renders its honest empty state; 14 glossary terms + 3 information-flow tiers project correctly. **Empty-state proof passed** — removing `_analysis/index.json` and `submission-index.json` left the page at 200 with exactly 2 dimmed stages showing their producer commands; both restored. 18-route regression all 200, zero server exceptions. **Uncommitted.**
- 2026-08-06: Phase B caught two more traps, recorded as F6 and F7. **F6**: the on-disk DHF manifest is a 2026-04-27 pre-v7 artifact whose 437 wall-to-wall `GAP` statuses are retired-schema residue, not a coverage finding — `dhf-manifest` v7 moved coverage to `/tracker assess` exclusively, so the stage reports catalogued counts and explicitly says coverage is not computed. Reading the owning SKILL.md before the JSON is what caught it. **F7**: a loader key named `items` shadowed `dict.items`, so Jinja rendered `<built-in method items…>` on the page while `data.json` and the grounding text were correct — renamed `traced_items`.
- 2026-08-06: **Phase A delivered** — Strategy landing page. New `console/strategy/loader.py` (counts without rendering), `web/templates/strategy_index.html`, `web/static/strategy_index.css`; `console/strategy/router.py` split into `/strategy` (index) + `/strategy/{slug}` (review surface); `workflow_b3_index.html` gained an `active_slug` that falls back to the old first-tab behaviour when absent. Live-verified on :8765 — roll-up reads 3 domains live / 17 decisions / 5 awaiting content, 8 cards (5 dimmed stubs), format chips 1×blocks + 2×prose, mixed-format advisory shown; `/strategy/{regulatory,commercial,architecture}` each open on exactly one active row + pane; `?domain=` and `/workflows/strategy-reassembly` both redirect correctly; unknown slug falls back to the index. Regression sweep across 10 existing routes all 200, zero server-side exceptions. **Uncommitted.**
- 2026-08-06: Two shape traps found and avoided during Phase A, both recorded as F5 and in `loader.py`'s docstring: (1) only `commercial` uses the v15 DECISION-block format — counting only v15 would report `regulatory` (5) and `architecture` (3) as zero-decision documents; (2) the v15 sentinels **wrap** the legacy `**Decision**:` prose rather than replacing it, so summing the formats double-counts `commercial` as 18. Also corrected an over-broad intent scan that surfaced a `**Decision**:` line as a domain's summary on the card.
- 2026-08-06: Closed out task 103 (retroactive; artifacts had shipped under 104), removed a duplicate 103 row from `tasks/ben/000-index.md`, and cleared the stale uncheckpointed marker that was resurfacing every session start.
- 2026-08-05: Task created. Pre-flight survey of the mega-chibi console completed and plan approved: three surfaces (Strategy landing, Document Pipeline, Journey), phase order A → B → C. Eight scope decisions (D1–D8) and four survey findings (F1–F4) recorded — notably F2 (our strategy docs carry `<!-- DECISION:start -->` sentinels, not the sister's `| D<N> |` ledger rows, so Phase A needs no new parser) and F3 (the regulated-publish lane has zero data in this repo and ships contract-first). Numbering note: 113 was claimed mid-flight by a concurrent session; this work moved to 114.
- 2026-09-08: harvest tags repaired (ben/123) — 1 tags
