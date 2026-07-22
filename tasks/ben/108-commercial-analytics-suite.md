# 108 — Commercial Analytics Suite (skills + demo assets)

**ID**: 108
**Created**: 2026-07-22
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
   - **when you tick a Todo off (or add/restructure Todos), fill/refresh the matching `## Economics` entry in the same edit** — the by-hand person-hours that unit would have taken, ranged + persona-tagged, per the rubric (if `## Economics` is present / usage-metrics is installed). **Checking the box is the estimate trigger** — don't defer it to a later checkpoint.
2. **Phase-end batching is OK; drift-batching is not.** Planned phases (e.g., "finish Phase 2, then log the whole phase at once") are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask. By then a crash or context-trim has lost the state. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.
6. **Estimation provenance (if `## Economics` is present).** This doc's `## Economics` block is the by-hand person-hour estimate, built per the effort-estimation rubric at `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (owned by the `usage-metrics` skill). To **add or refresh** an estimate on resume — even without loading the task skill — read that rubric first for the anchors, personas, and JSON schema; the block also carries a `method_ref` naming it. Skip silently if `usage-metrics` isn't installed. Point to the rubric, never copy it into this doc.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

Extend the PDLC demo from "are we compliant and ready to file?" to "are we winning?" — build a **commercial analytics layer**: skills and demo assets that answer business questions with data, for commercial audiences (execs, product, service ops).

The business-question catalog (from the 2026-07-22 ideation with Ben) clusters into three pillars:

1. **Market & competitive performance** — How do we perform vs competitors? Sales vs adoption, market penetration across regions, cost/feature competitiveness.
2. **Roadmap & state-of-the-art comparison** — Are we building the right thing? Roadmap vs competitor roadmaps, are we state of the art (also feeds the EU MDR SOTA obligation).
3. **Field performance & upgrade operations** — How are products doing in the field? Complaints, clinical safety signals, field-update campaign performance (coverage vs plan, customer struggle, service capacity, cost per upgrade — ours and the customer's), regulatory field issues (recalls/FSCAs), plan-vs-actual verdicts.

**Scoping decisions (locked with Ben, 2026-07-22, refined in discussion rounds 2–4):**

- **Build order**: Pillar 3 (field performance & upgrades) first, as a full vertical slice — data + skill + dashboard. Then pillars 1 and 2.
- **Two-skill split**: a **`corpus` skill** (the grounding engine — acquire / snapshot / validate / refresh / diff / assumption management) + a **`commercial` skill** (the consumer — per-pillar analysis actions `field` / `market` / `roadmap` + computation library + claim lint). Corpus is cross-cutting: regulatory/post-market skills can adopt it later. Both authored via `/skill-creator`, registered in `project.yml security.approved_skills`.
- **Corpus home**: `docs/project/corpus/<domain>/<dataset>/` — shared project-tier tree (commercial datasets are the first tenants, not the owners).
- **Real external data, acquired by research** — NOT fabricated: openFDA (510(k) clearances, MAUDE adverse events, recalls/enforcement — public domain, queryable by competitor), competitor spec sheets, market reports. Real competitor names stay (BD Alaris, Baxter Spectrum IQ) because the data behind them is real. **Internal data** (our sales, fleet telemetry, complaints) is fabricated for the demo (PainEase is fictional) but flows through the SAME snapshot machinery — in a real deployment that's where client ERP/CRM/service exports plug in. Fabricated internal data keeps the `_Demo sample data — not for clinical use._` banner.
- **Assumption records are first-class**: where data doesn't exist (e.g., competitor sales figures), the skill records A-NNN — what was needed, why unavailable, estimation method, confidence, refresh trigger. Derived answers trace to their assumptions.
- **Snapshot architecture**: immutable dated snapshots (`snapshots/YYYY-MM-DD/` with `raw/` byte-pinned payloads + `normalized/` schema-validated CSV + `provenance.yml`), `latest` pointer, `assumptions/` per dataset. Provenance tree: source (URL/query/retrieved-at/hash for external; system-of-record/export method for internal), parent-by-hash, transformation, usage-rights field (licensing — never republish licensed data). Raw layer committed by default; per-dataset opt-out to hash-reference-only for huge payloads. Refresh produces a new snapshot + a **delta report** (the "what changed in our competitive world" briefing — key demo output).
- **Anti-hallucination check stack** (verification is the third leg alongside acquisition + analysis):
  1. Core boundary: **the LLM orchestrates and interprets; scripts compute** — no model-typed numbers, ever.
  2. Acquisition-time asserts + normalized-schema validation (snapshot doesn't write if it doesn't validate).
  3. Provenance completeness checker (every file has a parent, hashes resolve, referenced A-NNNs exist).
  4. Semantic guards as asserts (e.g., MAUDE counts can't become *rates* without an attached installed-base assumption record — no denominator, no rate).
  5. Claim lint over authored narrative: every numeric claim carries a `dataset@snapshot` citation; linter re-looks-up/recomputes each (number, citation) pair; uncited or mismatched numbers = error; estimation language without an A-NNN = error. (Reference-audit logic applied to figures.)
  6. Adversarial re-derivation: independent subagent re-derives headline claims from the corpus alone (confirm/refute) — for net-new analyses and refresh deltas.
  7. Honesty labels on every published figure: **measured / derived / assumed / unavailable**.
  8. **Freshness enforcement** (locked round 4): per-dataset `max_age_days`; `check` flags stale snapshots; claim lint BLOCKS current-state claims citing a stale snapshot unless explicitly waived with a visible stale-data acknowledgment. Checks 2–4 + 8 live in `corpus`; 5–6 in `commercial`; both expose a `check` action so one command proves the whole grounding chain green.

**Existing assets to build on (not duplicate):**

- `docs/project/strategies/commercial-strategy.md` — D-COMM decisions: positioning, segmentation, Y1–Y5 launch waves.
- `docs/project/input-analysis/competitive-landscape/` — `competitive-product-assessment.md`, `state-of-the-art-analysis.md`.
- `docs/project/input-analysis/market-research/` — market sizing, user-needs traceability of released products.
- `docs/project/strategies/postmarket-strategy.md` + `post-market` advisor — surveillance loop framing.
- Cloud Suite `fleet-management` DHF component — the PP3500 program's own fleet product; the field-performance demo "eats its own dog food."
- `project-console` (Market/Field views to be added), `dataviz` + `frontend-design` skills for dashboards, `advisors` skill for new commercial personas.

## Plan (phases)

**Phase 1 — Design** (next up)
- Business-question catalog: each question → dataset(s) needed → computation → qualitative grounding doc → output surface (console view / HTML dashboard / markdown report) → evidence class expected (measured/derived/assumed).
- Corpus architecture spec: snapshot layout + `provenance.yml` schema + assumption-record (A-NNN) schema + freshness policy (`max_age_days` per dataset) + check-stack contracts (which check lives in which skill) + usage-rights/licensing field semantics.
- Skill contracts for BOTH skills: `corpus` (acquire / validate / refresh / diff / check / list) and `commercial` (field / market / roadmap / lint / check), incl. how commercial declares corpus dependencies and the console sidecar JSON contract.

**Phase 2 — `corpus` skill v1 (the engine)**
- Scaffold `docs/project/corpus/` (README-governed; update `docs/project/README.md` structure sentinel).
- Build the engine: acquisition framework + snapshot writer + schema validation + provenance checker + semantic-guard asserts + freshness check + delta reports.
- First corpora through the machinery: EXTERNAL — openFDA competitor data (510(k) clearances, recalls, MAUDE events for BD/Baxter/ICU Medical et al.); INTERNAL — fabricated fleet/complaints/upgrade-telemetry generated then snapshotted like any other source.
- Prove `corpus check` green end-to-end.

**Phase 3 — `commercial` skill v1 + field-performance vertical slice**
- Computation library (deterministic scripts; model never computes) + `field` action: campaign health, complaint/safety trend signals, plan-vs-actual verdicts, capacity outlook.
- Claim lint + adversarial re-derivation pass wired in.
- Field dashboard (dataviz/frontend-design) + console sidecar; honesty labels + freshness badges visible in the UI.
- Demo narrative tuning via internal-data generator knobs (e.g., EMEA behind plan, capacity crunch); MAUDE-denominator assumption record as the built-in honesty showcase.

**Phase 4 — Pillar 1: market & competitive performance**
- Corpora: internal quarterly sales/adoption by region+segment; external competitor price/feature matrix (spec sheets + competitive-product-assessment grounding); assumption records for non-public competitor figures.
- `market` action: penetration, share, sales-vs-adoption divergence, cost/feature competitiveness scoring; dashboard.

**Phase 5 — Pillar 2: roadmap comparison / SOTA**
- Corpus: competitor roadmap register from REAL public signals (510(k) clearance pipeline via openFDA, announced products) + assumptions for unannounced direction.
- `roadmap` action: parity/gap matrix vs our Y1–Y5 waves (ahead / parity / behind / not-pursuing per capability), SOTA verdict feeding the MDR state-of-the-art angle.

**Phase 6 — Integration & personas**
- Console Market + Field views (project-console sync pattern).
- Commercial advisor personas (e.g., commercial-lead / market-analyst, field-service-ops) via `/advisors add`.
- `project.yml` registration (approved_skills, approved_agents), CLAUDE.md skills-table rows, push to hitachi registry if the skills prove generic (corpus very likely will).

Each phase lands via the project git workflow (branch → PR → auto-merge). Phases 4–6 may reorder based on demo priorities.

## Todos

_Phase 1 (active):_

- [x] Author the business-question catalog — DONE 2026-07-22: 6-agent persona fan-out (CCO, Product, Field Service, Post-Market, CFO, Board) → 72 candidates → top 30 + ~25 parked overflow, in `## Business-Question Catalog` above; v1 awaiting Ben's review (per-question data→computation→output mapping happens in the corpus/skill spec step)
- [x] Spec the corpus architecture — DONE 2026-07-22: dataset layout, provenance.yml + A-NNN + W-NNN schemas, freshness policy, usage-rights field, in `## Skill Contracts` + `## Visualization & Skills Architecture`
- [x] Sketch BOTH skill contracts — DONE 2026-07-22: `corpus` (init/acquire/refresh/validate/diff/assume/waive/check/list) + `commercial` (answer/pillars/lint/verify/approve/render/check/catalog) + sidecar schema + editions model + end-to-end provenance layer, in `## Skill Contracts`
- [ ] Review Phase-1 design with Ben (viz architecture ✅ confirmed 2026-07-22 incl. editions + provenance mandate; catalog + contracts pending final look) → green-light Phase 2

_Phase 2 (`corpus` skill v1):_

- [x] Scaffold `docs/project/corpus/` — DONE 2026-07-22: root README (conventions incl. never-hand-edit-snapshots, demo banner for internal datasets); `docs/project/README.md` structure table + changelog updated (hand table, no sentinel present)
- [x] Build the corpus engine via /skill-creator — DONE 2026-07-22: `.claude/skills/corpus/` v1 (SKILL.md + README + `scripts/corpus.py` ~600 LOC + 3 templates). Actions: init/acquire/refresh/validate/diff/check/list/assume/waive. Acquisition: openfda (paginated) / command / file; normalize: openfda-flatten / command; staging-then-rename (nothing lands on failure); immutable snapshots (same-day → .2 suffix); hash-chained provenance.yml; mandatory schema validation; A-NNN + expiring W-NNN; freshness banding; refresh delta reports w/ assumption-review footer. Smoke-tested end-to-end in scratchpad incl. tamper detection (mutated file → validate fails). Registered in `project.yml approved_skills`.
- [ ] First external corpora: openFDA competitor data (510(k)s, recalls, MAUDE) snapshotted with full provenance
  - [x] `commercial/openfda-510k-infusion` — DONE 2026-07-22: first REAL snapshot acquired live (29 FRN clearances 2021-11-09→2026-01-28; Baxter 9, ICU Medical 3, CareFusion/BD 2); check GREEN; dataset README written (consumers BQ-06/12/13/14 + FRN-scope limitation noted)
  - [x] `commercial/openfda-recalls-infusion` — DONE 2026-07-22: 136 real FRN recalls posted 2021→present (Baxter 27, Fresenius 21, Smiths 16, CareFusion 16, ICU 13+8); README notes firm-name-variant normalization requirement
  - [x] `commercial/openfda-maude-infusion-mfr` — DONE 2026-07-22: count-mode acquisition (row-level MAUDE = 80k+ events for the window → added openFDA `count:` aggregation + `openfda-count` normalizer to the engine); 99 manufacturer count buckets (CareFusion 56k+5k, Baxter 8k, ICU 7.3k, Smiths 7.3k); **A-001 denominator assumption created FIRST** (dataset declares `assumptions_referenced: [A-001]` — acquire refuses to land without it); README documents the 3 epistemic constraints (no denominator / reporting propensity / name variants)
- [x] First internal corpora — DONE 2026-07-22: three demo-fabricated datasets through the same machinery (seeded gen.py per dataset, shared embedded fleet model so serials align, banner-stamped raw exports): `internal-fleet` (884 devices, 48 sites, 3 regions), `internal-complaints` (430 records, 18 months), `internal-upgrade-campaign` (389 rows, campaign C-2026-02 with narrative knobs verified in data: EMEA 50% vs NA 77% completion; hw_rev B/3.1.2 failure cluster 23% vs 4% baseline)
- [x] `corpus check` GREEN end-to-end — DONE 2026-07-22: all 6 datasets fresh, validated, hash-chains intact. Two engine fixes from real use: relative-root path doubling in command acquisition (absolutize before substitution) and empty-term openFDA count buckets (skipped with log, caught by schema key validation exactly as designed)
- [x] Push Phase-2 via PR — DONE 2026-07-22: PR #128 merged to main (branch commit `8bd892d`, merge `9ed0a7c`); remote + local branch deleted; local main fast-forwarded to `98cb626` after stashing tool-managed usage-metrics locals (stash retains them; pre-session sync-log/SECOPS edits restored to worktree). `corpus check` GREEN on main.

_Phase 3 (`commercial` skill v1 + field slice):_

- [x] Build the `commercial` skill via /skill-creator — DONE 2026-07-22: `.claude/skills/commercial/` v1 (SKILL.md w/ corpus dependency frontmatter, README, `scripts/commercial.py` ~450 LOC, 2 templates). Actions: answer/lint/approve/render/check/catalog. Editions lifecycle (draft→approved→superseded, same-day .2 suffix, drafts re-generable, approved hash-pinned via approval.yml); claim lint (marker resolution [src|assume|derived|config|waived], numeric-claim rule w/ exempt tokens + table-header detection, estimation-language rule, pin freshness vs max_age_days, data.json evidence-class hygiene); sidecar render (schema_version 1.0); check chains to corpus check. Registered in project.yml approved_skills.
- [x] Project-side catalog + computations — DONE 2026-07-22: `docs/project/commercial/` (README, `commercial.yml` all 30 BQs — 6 implemented, 24 visible as not-implemented, `entity-aliases.yml` per the normalization lesson, `computations.py` ~430 LOC deterministic: as-of dates derive from data, no clocks). A-002 customer-cost assumption created (structured model block); corpus engine fixed to allocate GLOBALLY unique A/W ids (collision found when campaign dataset minted a second A-001).
- [x] Six draft editions computed + linted GREEN — DONE 2026-07-22: BQ-23 (62.5% complete; all regions miss 2026-09-30 close at run-rate), BQ-24 (PAUSE TRIGGER: hw B/3.1.2 at 23.1% vs 15% threshold), BQ-25 (EMEA 23.0 tickets/100; 4 rollback sites; customer cost $7.2k–$16.3k on A-002), BQ-26 (capacity gap all regions; FSE-roster data gap stated as `unavailable` series), BQ-27 (56.7% of PP3500 fleet ≥1 version behind), BQ-19 (MAUDE counts published, RATE CHART MECHANICALLY BLOCKED pending A-001 quantification — the honesty showcase working). Lint caught 3 real defects in first-pass reports (header-row false positives → lint improved; prose digit → reworded). Sidecar rendered; `commercial check` GREEN.
- [x] Adversarial verification — DONE 2026-07-22: independent agent (pins-only, no reports) recomputed all six; 4 CONFIRMED + 2 CONFIRMED-WITH-CAVEAT. Dossier: `tasks/ben/_work/108-adversarial-verify-field-slice-2026-07-22.md`. **All three findings actioned same day**: (1) generator date artifact fixed → corpus refreshed to `internal-upgrade-campaign@2026-07-22.2` w/ delta report; (2) BQ-24 switched to per-attempted-device basis (31.4%, was understating at 23.1%); (3) BQ-25 basis made consistent → hotspot is actually NA 21.7 tickets/100 attempted (EMEA claim retracted). BQ-23/26 re-answered: APAC now on-track, EMEA+NA miss. All lint green; commercial check GREEN.
- [x] Approvals — DONE 2026-07-22 on Ben's "go ahead": all six verified editions approved (`--by "Ben Xavier"`, verify-note → the `_work/` dossier); gate passed (lint + freshness green), content hash-pinned; prior states superseded n/a (first approvals). Console now shows Approved chips, watermark removed, approval record in provenance panel (browser-verified on BQ-24).
- [x] Second answer tranche — DONE 2026-07-22: three new computations from EXISTING corpora, spreading answers across 5 of 6 categories: **BQ-06** (board — competitor 510(k) cycle time from public dates: median 213 days across 29 clearances; Baxter fastest frequent filer at 74 days median; our-history series honestly `unavailable` pending an internal regulatory-log dataset), **BQ-12** (roadmap — 90-day clearance sweep anchored to pin: 1 clearance in window ending 2026-01-28, 0 roadmap-keyword flags; keyword triage map in commercial.yml), **BQ-18** (field-safety — complaints per 100 devices w/ the fleet registry as STATED denominator: CAPA-review trigger on occlusion-alarm 3.39 vs 3.0 and connectivity 2.26 vs 2.0). All lint green (1 benign warning); sidecar 6 answered + 3 draft-only; commercial check GREEN; console restarted + browser-verified.
- [x] Console Commercial section (viz tier) — DONE 2026-07-22 (project-console 1.41.0→1.42.0): new `console/commercial/{loader,router}.py` + `commercial_index.html`/`commercial_view.html`/`commercial.css`; discovery-gated topnav item (`ic-commercial`); question-centric catalog (category rail, rollup, cards w/ verdict + status/evidence/freshness badges + assumption chips, Planned cards visible); answer view (verdict banner, in-console single-hue bar charts plotted verbatim from sidecar series w/ per-series evidence badge + provenance link, `unavailable` series as designed-absence cards, DRAFT watermark, pins+approval panel, edition history via ?edition=, full marker-cited report via documents renderer, assistant drawer grounded in /commercial/{bq}/grounding). Dataviz skill loaded first (palette slot-1 single hue, direct labels, icon+label badges). Tested: TestClient 7 routes 200 + all probes; live console restarted + browser-verified (catalog, BQ-24 pause-trigger page w/ watermark, BQ-19 honesty page w/ blocked-rate card sourced to A-001). SKILL.md topline docs + README 1.42.0 changelog updated.
- [x] Push Phase-3 via PR — DONE 2026-07-22: PR #129 merged (`164b02f`); branches deleted; local main synced; commercial check GREEN on main. Note: Ben's pre-session edits to `.claude/sync-log.md` + `tasks/ben/SECOPS.md` rode along in this commit (they were index-staged by the Phase-2 stash-restore; content is Ben's own, now preserved on main).

_Ben's BQ-26 review round (2026-07-22):_

- [x] Trend graphs — DONE: `kind: timeseries` series contract (commercial v2) + console SVG line charts (server-computed geometry, ≤4 validated hues, legend + end labels, hover tips, zero-filled so stalls flatline). Added: BQ-26 weekly completions by region, BQ-23 cumulative coverage %, BQ-18 monthly complaints top-3.
- [x] Narrative (Risks/Mitigations/Issues) — DONE: deterministic narrative blocks from computed facts, marker-cited in the linted report, mirrored in data.json, rendered as a color-railed console panel w/ severity chips. BQ-23/24/26/18.
- [x] First-class plan expectations — DONE (Ben's mid-review addition): `expectations:` per BQ in commercial.yml (basis, set_by, validated flag), evaluated per edition → verdicts, console table w/ Not-met + unvalidated chips. All current demo thresholds honestly flagged unvalidated stand-ins. E-23.1/2, E-24.1, E-26.1, E-18.1/2.
- [x] New draft editions (.2/.3) computed lint-green; approved editions untouched (newer-draft banner links from approved view); lint caught + fixed a narrative-mitigation uncited figure; Jinja g.items→entries fix; project-console 1.42.0→1.43.0; browser-verified full BQ-26 page.
- [x] Editions tree as left rail (Ben mid-review) — DONE: Setup-shell-style sticky rail replacing the history drawer; status chips per edition, active highlighted, immutability hint; responsive collapse. Browser-verified.
- [x] Ask-the-Advisor on the catalog (Ben mid-review) — DONE: detail pages already had the drawer; added board-level drawer on /commercial grounded in new `/commercial/catalog/grounding` (whole-board roll-up incl. verdicts, assumptions, freshness; route declared before /{bq} to win matching). Example prompt: "Which current verdicts are judged against unvalidated expectations?"
- [x] Push review-round via PR — DONE 2026-07-22: PR #132 (`0342e1e`) + width fix PR #133 (`ef2e669`).
- [x] All nine plans authored (Ben) — DONE 2026-07-22: BQ-06/12/18/19/23/24/25/27 written to the BQ-26 standard — each codifies its computation's ACTUAL commitments (definitions, anchors, denominators — incl. the verification-driven ones: per-attempted basis in 24, consistent tickets basis in 25, no-causal-connectivity in 27, lag-trimmed history + blocked rate in 19, deterministic pin-anchored window + publication-lag statement in 12), states data have-vs-need, and draws assertion limits. All 8 re-answered to pin; 9/9 plan-currency in-sync; check GREEN.
- [x] Analysis plans + intent check (Ben decision: Option A + intent verification) — DONE 2026-07-22 (commercial v8, project-console 1.52.0): `plan-init` scaffolds user-owned `plans/BQ-NN.md` (templated w/ category hints, never clobbered); `answer` pins plan hash; `plan-currency` lint check (missing/unpinned/drifted → callouts); `intent-check` verification type. Console Plan tab (4th) w/ currency chip + rendered contract + edit hint. Seeded: 9 plans scaffolded; BQ-26's plan authored for real (codifies the red-team's stall rule + anchor optimism + gaps + limits), pinned into edition .6; REAL intent-check agent run: **HONORED-WITH-NOTES** (8/9 clauses honored incl. stall-as-Issue rule applied as written; 1 note — connectivity gap honored in effect, not explicitly listed; dossier `_work/108-intent-check-BQ-26-2026-07-22.6.md`). Check GREEN.
- [x] Itemized lint + data availability + derivation chains + Data tab (Ben review round) — DONE 2026-07-22 (commercial v7, project-console 1.51.0): lint itemized into 7 named checks (pass/warn/fail chips + expandable findings; summary kept); quality.json gains `data_availability` (have / via-assumption / missing — Ben: "be clear on what data we have and what we don't"); NEW `derivation-chain` lint check — derived series must state {method, inputs[]} (Ben: "what did we derive it from?"), inputs in marker vocabulary so the chain walks through corpus provenance; approved editions grandfathered from post-approval rules in `check` (immutability vs evolving lint resolved); answer views gain a **Data** tab — collapsible structured tables w/ shared paginated table engine (50/page) + unstructured artifact inventory per pinned dataset (raw payloads, provenance, config, A/W records w/ sizes + links). All 9 re-answered lint-green; two more Jinja dict-method traps fixed (g.items). Browser-verified.
- [x] Catalog scale controls (Ben) — DONE 2026-07-22 (project-console 1.50.0): search + answered-within 30/60/90d recency filter (keyed on latest-edition date; unanswered drop out) + cards/rows view toggle (compact one-liners, localStorage-persisted) composing with the category rail; live showing-X-of-Y count; empty categories hide. Jinja gotcha fixed en route (Markup `~` concat escaping attribute quotes → plain attribute interpolation). Browser-verified (rows + 30d = 9 of 30).
- [x] Quality & audit tab (Ben idea) — DONE 2026-07-22 (commercial v6, project-console 1.49.0): per-edition `quality.json` (lint status + resolved-reference inventory + per-pin freshness; machine-written by answer/lint/approve, refreshable via new `audit` action) + new `record-verification` action filing agent verdicts (adversarial-verify/red-team/reference-audit/human-review; preserved across machine rewrites). Console answer view split into **Report | Quality & audit** tabs (lint badge on tab; lint card, reference table ✓/✗, freshness table, verification section w/ verdict chips + dossier links + honest empty state). Seeded with a REAL run: fresh independent agent on BQ-26@2026-07-22.3 → adversarial-verify CONFIRMED (all figures reproduce) + red-team CONFIRMED-WITH-CAVEAT (4 findings; dossier `tasks/ben/_work/108-redteam-BQ-26-2026-07-22.3.md`). Browser-verified.
- [ ] Action the BQ-26 red-team findings (computation refinements): uniform stall criterion (EMEA=Issue), run-rate anchor = snapshot as-of + sensitivity row, APAC thin-margin watch item in verdict, duration-based FSE-days sizing + connectivity join with internal-fleet for the remote-conversion mitigation
- [x] Ruled report tables + inline citations (Ben review) — DONE 2026-07-22 (commercial v5, project-console 1.48.2): report-body markdown tables get visible structure (bordered cells, distinct headers, zebra, hover); Evidence columns eliminated across all 9 report tables + expectations table — citation markers now ride inline on the row label (SKILL.md convention added; lint is line-based so per-row coverage unchanged). All 9 BQs re-answered lint-green; sidecar 7 answered + 2 drafts; browser-verified BQ-06 table.
- [x] Approve as button + modal (Ben refinement) — DONE 2026-07-22 (1.48.1): inline panel → compact ✓ Approve… button in the badge row opening a native dialog modal (gate explanation, roster select, note, actions, help fold-out). Browser-verified with the dialog open.
- [x] UI Approve & push button (Ben) — DONE 2026-07-22 (project-console 1.48.0): draft banner replaced by an approve panel (roster select from project.yml team.active — RESOLVES the who-may-approve sub-decision: any rostered member, recorded; optional verify note; CLI instructions demoted to help fold-out). POST /commercial/{bq}/approve runs the gated skill approve (lint/freshness failures surface as blocked-banner w/ output), re-renders sidecar, then the full push sequence server-side (branch→surgical stage→commit→PR→auto-merge→main). Exercised for real: BQ-18@2026-07-22 approved by Ben via the endpoint → PR #140 MERGED; approval.yml + status verified; check GREEN.
- [x] Header-in-column layout (Ben review, annotated screenshot) — DONE 2026-07-22 (project-console 1.47.1): question header (crumb/eyebrow/title/badges) moved inside the content column — left edge aligned with verdict/content, only the editions tree in the left rail; title spans to the right margin (root cause of persistent early wrap: global heading `text-wrap: balance` — overridden with `pretty` on wide pages, found by measuring computed styles in-browser). Reference-link behavior confirmed as-intended by Ben (direct-open experiment reverted). Browser-verified.
- [x] Latest-edition default + edition-ordering fix + title alignment (Ben review) — DONE 2026-07-22 (commercial v4, project-console 1.47.0): Ben's screenshot exposed that suffix REUSE after a discarded draft made lexicographic order lie (BQ-26's newest content sorted older, so the default approved view hid all the new charts). Fixed: suffix allocation = max+1 (never reuse), edition recency = created_at everywhere, sidecar gains `latest_edition`, console + cards default to the newest edition (draft chipped + watermarked; approved one click away in the rail) — per Ben: "we're defaulting to approved editions, let's default to the latest." BQ-26 stale drafts discarded + recomputed clean. Wide pages uncap the title/subtitle so the header spans to the content margins. Browser-verified.
- [x] Historical data views + right-diagram-forms round (Ben) — DONE 2026-07-22 (commercial v3, corpus v2, project-console 1.46.0): (1) NEW real corpus dataset `openfda-maude-infusion-monthly` (1,183 daily count buckets since 2023; corpus engine now accepts openFDA date-count `time` buckets; learned: no `limit` param on date counts → 403); (2) form-selection guidance encoded in commercial SKILL.md (stat/bars/paired-bars/timeseries/kv/unavailable — diagram follows the data's job; every answer carries a history or says why not); (3) console renders `stat` hero tiles + `paired-bars` grouped comparisons; (4) all 8 computed BQs re-answered with historical views: BQ-19 monthly MAUDE trend (real, lag-tail excluded) + 294,608-event stat; BQ-06 median-review-days-by-year line + 213d stat; BQ-12 quarterly clearance line + window stat; BQ-23 coverage stat; BQ-24 weekly completions-vs-retried lines + worst-cohort stat; BQ-25 weekly tickets by region + rollback stat; BQ-26 current-vs-required paired bars; BQ-27 currency stat + honest `unavailable` history (single snapshot ≠ trend; 7-day cadence will accumulate). All lint green; check GREEN; browser-verified BQ-19. — DONE 2026-07-22 (project-console 1.45.0): `/commercial/{bq}/data` — pinned snapshot rows + series table forms, one tab per table; sortable headers, per-column filters (select ≤14 uniques / text otherwise), global search, row count; verbatim rows, console computes nothing; "▦ Data view" chip on answers. Doubles as the dataviz-required chart table form. Browser-verified (BQ-26: 389-row campaign table w/ filters).
- [x] Formal reference layer (Ben follow-up) — DONE 2026-07-22 (project-console 1.44.0): citation markers render as numbered superscripts + a formal References section (typed entries w/ links + detail; first-appearance numbering; :target highlight); chart source lines + narrative statements carry the numbers. Display-only — raw report keeps machine-checkable markers (lint contract unchanged). `RefBook` in console/commercial/router.py. Verified: 38 superscripts, 0 raw markers in display, all ref kinds present; browser-checked full page.

_Later phases (4–6): see Plan (expand into todos when reached)._

## Business-Question Catalog (Phase 1 deliverable — v1 for review)

**Method**: 6 parallel agents, one per persona lens — CCO/Sales, VP Product, VP Field Service, VP Quality/Post-Market, CFO, Board/Corporate (added at Ben's request to span the whole 5-device portfolio, not just PP3500). 12 questions each = 72 candidates, grounded in `commercial-strategy.md`, `competitive-product-assessment.md`, `state-of-the-art-analysis.md`, market research, `postmarket-strategy.md`, and the portfolio device catalog. Deduped (questions surfacing independently from 2–3 lenses were merged — convergence was treated as a ranking signal), then top 30 selected for: decision-impact (the answer changes a real decision), pillar + cadence balance, demo-ability (data acquirable via openFDA or fabricated-internal), and deliberate preservation of HIGH-assumption questions (the honesty showcase). ~25 distinct second-tier questions parked in the overflow below.

Legend: ⚠️ = HIGH assumption risk (answer requires explicit A-NNN assumption records). Source lens in parens.

### A. Board & Portfolio (corporate-wide)

- **BQ-01 — Portfolio funding map.** Which of the five device lines (IP5000, PP3000, PP3500, SP6000, SP6500) fund the company and which consume it — revenue/margin/trajectory by line, and what pays for the Cloud Suite and concept bets? (Board; quarterly; internal ERP + allocation methodology; absorbs CFO gross-margin-by-SKU)
- **BQ-02 ⚠️ — Concentration risk.** Revenue dependence on the PCA franchise, top-3 GPO/IDN contracts, single hospital systems — and the 5-year-plan impact of losing one anchor GPO award. (Board; annual; GPO attribution + loss-scenario model need explicit assumptions)
- **BQ-03 ⚠️ — Business-model transition: evidence vs hope.** Recurring revenue % today vs the Y5 plan; which parts of the ~$350M target are contracted, modeled, or aspiration. (Board + CFO mix-trend merged; annual; the plan's own [VERIFY]-flagged figures make the assumption set explicit)
- **BQ-04 ⚠️ — Subscription unit economics.** LTV per connected pump vs cost-to-serve (incl. regulated-SaMD maintenance: PCCP retraining, cyber patching) — and is Cloud Suite pricing cannibalizing the hardware ASP? (Board + CCO discount-subsidy merged; quarterly; churn/cost-to-serve have no operating history)
- **BQ-05 ⚠️ — Revenue by regulatory dependency.** Plan revenue split by cleared / letter-to-file / PCCP-enabled / new-submission-required, with slip scenarios and the pre-computed reforecast trigger. (Board audit + CFO slip-scenario merged; annual; openFDA review-time benchmarks + revenue-attribution assumptions)
- **BQ-06 — R&D productivity & pipeline health.** Concept→development conversion (AI7000, AMB2500, NEO1200), and clearance-to-clearance cycle time vs our own K-history and vs BD/Baxter — public openFDA 510(k) dates make competitor speed computable, not guessed. (Board; annual)

### B. Market & Competitive Performance

- **BQ-07 ⚠️ — Segment share.** Our actual share of the US PCA/smart-pump segment — taking share from BD/Baxter or just growing with the market? (CCO; quarterly; competitor unit sales not public → share estimated from analyst/GPO/win-loss with stated assumptions)
- **BQ-08 ⚠️ — Win/loss vs the predictive gap.** What are we winning/losing on, and how many recent losses cite predictive monitoring we don't have — the revenue cost of the gap today. (CCO; quarterly; self-reported loss reasons are unreliable → assumption-flagged)
- **BQ-09 — Disruption-window win rate.** Are we winning displaced accounts where an incumbent has an open recall or M&A integration turmoil (ICU/Smiths), and how long does the window stay open? (Board + CCO; quarterly; openFDA recalls + CRM win/loss)
- **BQ-10 ⚠️ — TCO competitiveness.** 5-year total cost of ownership per pump vs Alaris/Spectrum IQ/Plum 360 — the buyer's spreadsheet. (CCO + CFO merged; quarterly + pre-GPO-negotiation; competitor realized pricing is confidential → explicit assumption set)
- **BQ-11 — Adoption-vs-sales divergence.** Accounts where pumps were sold but telemetry/utilization diverges from what they bought — the churn and reference-site early warning. (CCO; monthly; telemetry + proxy for unconnected accounts)

### C. Roadmap & State of the Art

- **BQ-12 — Clearance-sweep vs roadmap.** Quarterly: every new competitor 510(k) clearance laid against our F1–F9 roadmap — anything cleared that lands on a feature we scheduled two years out? (Product; quarterly; openFDA is the authoritative public signal)
- **BQ-13 ⚠️ — Predictive-monitoring runway.** How long before an entrant or incumbent (incl. by acquiring an AI entrant) closes the gap the whole plan bets on — is Y3 timing still defensible, and what's our move if BD/Baxter buys? (Product + Board M&A-threat merged; quarterly; unannounced programs → develop-to-clear lead-time assumptions)
- **BQ-14 — PCA feature parity, line by line.** BD ships PCA Pause + EtCO2 today — where exactly do we sit, and which gaps are on the roadmap vs silently unaddressed? (Product; quarterly; 510(k) summaries + IFUs are public)
- **BQ-15 — SOTA currency.** Is the state-of-the-art analysis still true (EU MDR obligation), and are the two headline differentiators (±0.5% accuracy, 150+ hr battery) still ahead of anyone's current generation? (Product spec-erosion merged; annual + event-driven on competitor launch)
- **BQ-16 ⚠️ — KOL evidence audit.** For each F1–F9 feature: documented, attributable KOL evidence on file? Which ride on a single voice (F3 has none)? Does re-scoring vs *current* sentiment still order the Y4 slot? (Product ×2 merged; annual; pre-wave sentiment staleness is an explicit assumption until re-measured)
- **BQ-17 ⚠️ — The kill/accelerate capstone.** Stacked against the clearance pipeline, KOL data, and attach actuals — which single roadmap bet looks most wrong: the one to kill, and the one to pull forward a year? (Product; annual strategy refresh; blends hard data with declared assumptions)

### D. Field Performance: Complaints, Safety & Regulatory Issues

- **BQ-18 — Complaints vs thresholds.** Top three complaint categories this quarter, rate-normalized with a *stated* denominator — any trending above the risk-file commitment (→ CAPA trigger)? (Quality/CEO; quarterly)
- **BQ-19 ⚠️ — The MAUDE denominator question.** How does our adverse-event profile compare to Alaris/Spectrum IQ — "and before you show me the chart, what denominator did you use, because MAUDE doesn't have one." Can a "most reliable in class" claim ever be substantiated? (CEO + Quality claims-dossier merged; quarterly; **the flagship honesty showcase** — installed-base + reporting-propensity assumptions are unavoidable and must be A-NNN'd)
- **BQ-20 — Franchise-killer signal watch.** Any field signal — complaints, near-misses, alarm analytics, class-wide MAUDE — around opioid over-delivery or PCA-by-proxy? (CMO; monthly; the highest-stakes standing query)
- **BQ-21 — Regulatory field exposure.** What's open on the field-action/FSCA docket, MDR timeliness (late filings, reportability under-calls), and the exposure if FDA walks in tomorrow? (CEO/audit committee + MDR-timeliness merged; monthly)
- **BQ-22 — The closed loop.** Of last year's field signals, how many landed as a design input, requirement change, or upgrade-pipeline item — and how many died in a spreadsheet? (Quality; quarterly; ISO 13485 obligation AND the installed-base retention argument)

### E. Field Performance: Upgrade Campaigns & Service Ops

- **BQ-23 — Campaign plan-vs-actual.** Current field-update campaign coverage, planned vs actual by region and site — do we hit the close date, or re-plan and notify accounts? (Field Service; weekly)
- **BQ-24 — Failure clusters & the pause trigger.** Update failure/retry rates by hardware rev, firmware baseline, site profile — is any cohort failing at a rate that says stop the wave and escalate to engineering? (Field Service; weekly, daily mid-wave)
- **BQ-25 ⚠️ — Customer struggle & customer cost.** Tickets per 100 upgraded pumps, rollback clusters, before/after complaints — plus what an upgrade costs the *customer* (downtime, biomed hours) and whether that friction predicts slow completion by segment. (Customer Success + CFO customer-cost merged; weekly during campaigns; customer-side labor is not in our systems → modeled with reference-account validation)
- **BQ-26 — Service capacity & crowd-out.** Can we execute the next two waves on schedule (hire/contract/slip decision) — and is campaign work silently borrowing from PM completion and SLA performance? (Field Service ×2 merged; monthly)
- **BQ-27 — Fleet currency.** % of installed pumps >1 firmware or drug-library revision behind, by account; release→90%-adoption lag — outdated DERS is a patient-safety exposure, not just an ops metric. (Customer Success; quarterly)

### F. Commercial Economics & Plan-vs-Actual

- **BQ-28 — Revenue vs plan.** By product line and region, decomposed volume vs price vs timing — reforecast decision input. (CFO; monthly)
- **BQ-29 — The attach-rate stage-gate.** Cloud Suite attach on the installed base vs the gate that releases the $24M predictive-monitoring spend — is the gate a real control or a narrative device? Upsell-to-existing vs net-new split. (CFO + Board + CCO — the single most-converged question across all lenses; quarterly)
- **BQ-30 ⚠️ — Upgrade economics & the remote-first case.** Fully-loaded cost per completed update, remote vs on-site — and the capital case for subsidizing Connectivity Adapter deployment at the top-50 non-connected accounts vs three more years of truck rolls. (Field Service ×3 + CFO merged; monthly + annual campaign scoping; future update cadence + customer IT readiness are assumptions)

### Overflow — parked, add as time permits (distinct questions that didn't make the 30)

Portfolio/board: PP3000 phase-out drift (conversion rate + dual-generation cost); talent/capacity to execute SaMD+AI+cyber at cadence; aggregate cross-fleet quality exposure + systemic-QMS-weakness screen (partially covered by BQ-19/21). CCO: $350M trajectory by launch wave (largely BQ-03/28); segment-2 pharmacy/biomed motion vs plan; installed-base retention calendar + at-risk ranking; territory performance vs GPO pull-through; home-infusion channel landscape pre-Y3; per-account cost-avoidance dossier (alarm hours, avoided events). CFO: cost-avoidance monetization (renewal of value-sold cohort); Y1 wave payback IRR re-run; service cost per installed device; warranty + complaint-handling cost trend; home-channel cost-to-book. Product: time-to-market asymmetry (our vs competitor submission→launch intervals — public openFDA dates); competitor PCCP-authorization accumulation; ambulatory 2028 SOTA projection for the F7 spec-lock; alarm-fatigue 35% claim vs own field data. Quality/Field: competitor-recall response playbook (same-failure-mode screen + sales-brief speed — overlaps BQ-09); battery-claim erosion watch; ambulatory enforcement history (Smiths CADD) as design input; pre/post-update fleet health (did the update deliver its claimed benefit); quality dividend (complaint rates, attached vs unattached cohorts — selection-bias caveat).

**Assumption-risk profile of the top 30**: 13 of 30 are HIGH — deliberate. Those are the questions where the corpus skill's A-NNN assumption machinery earns its keep; a catalog of only clean-data questions would hide exactly the epistemics this demo is built to expose.

## Visualization & Skills Architecture (Phase 1 design — v1 for review)

**Constraint from Ben (2026-07-22)**: skills generate the reports/data; the visualization tier is separate; final display in the project console.

**Console grounding** (per project-console SKILL.md, read 2026-07-22): the console's established pattern is *generic consumer of skill-emitted JSON sidecars* — Submission reads `docs/project/submissions/.console/submission-index.json` + per-filing JSON (`schema_version: 1.0`), Tasks reads `tasks/task-summary.json` with freshness bands (fresh/aging/stale), sections degrade to an empty state with a "run /<skill> render" hint, and a POST render button shells to the owning skill's render script. The commercial tier adopts this contract verbatim.

### Four-layer architecture

```
1. DATA        corpus skill        docs/project/corpus/<domain>/<dataset>/     snapshots + provenance + A-NNN
2. ANALYSIS    commercial skill    docs/project/commercial/reports/BQ-NN-*.md  claim-linted markdown answers
                                   docs/project/commercial/.console/*.json     schema-versioned sidecars
3. VIZ         project-console     console/commercial/ section                 generic consumer, renders charts
4. DISPLAY     browser             /commercial                                 question-centric UI
```

- **Layer 2 outputs, per business question**: (a) a **markdown report** — the narrative answer with `dataset@snapshot` citations, honesty labels, A-NNN references — under `docs/project/commercial/reports/`; (b) **JSON sidecars** — `commercial-index.json` (one row per BQ: id, question, category, status answered/stale/blocked/not-implemented, verdict headline, evidence-class, freshness, assumptions[], report_path) + per-pillar detail JSON carrying the **computed data series for charts**. The sidecar carries data, never presentation.
- **Layer 3**: new topline **Commercial** section (`console/commercial/` in the project-console skill, synced to `tools/project-console/`) — pure consumer. Renders charts client-side from sidecar data series (dataviz-skill guidance), so visualization logic lives entirely in the console tier and analysis stays presentation-free — the separation Ben asked for. Report bodies render inline via the existing documents renderer (same as Submission does). Advisor drawer attaches (ask commercial-lead / post-market about an answer). POST /commercial/render shells to the commercial skill's render script.

### UI concept — the question IS the navigation

The BQ catalog is the section's spine: an inner-nav shell (pattern: Setup's settings shell) with the six categories (Board / Market / Roadmap / Field-Safety / Field-Ops / Economics); each BQ renders as an answer card — the question as asked, the verdict headline, evidence-class badge (measured/derived/assumed/unavailable), freshness badge (per-dataset max_age_days bands), assumption chips linking to A-NNN records, a chart, drill-down to the full report. Demo beat: a board member's literal question on screen, answered with cited data, with the epistemics visible.

### Report lifecycle — editions with draft/approved states (added 2026-07-22 per Ben)

Reports and their visualizations need **history**: a draft can coexist with a previously approved answer, and past approved answers remain retrievable. Model: each BQ answer is an **edition series**, not a single mutable file.

- **An edition** = `report.md` + `data.json` (the chart series frozen for that edition) + the corpus snapshot pins + the check results at publication. Layout: `docs/project/commercial/reports/BQ-NN/<edition>/` (edition key = date or period, e.g. `2026-Q3`).
- **States**: `draft → approved → superseded` (frontmatter `status:` + approval record: who, when, which checks were green). A refresh NEVER mutates an approved edition — it opens a new draft. Approving a draft supersedes the prior approved edition (which stays on disk, immutable, reproducible against its pinned snapshots).
- **Approval gate**: a draft cannot be approved unless the check stack is green — claim lint pass, freshness pass (or a visible W-NNN waiver), adversarial verification verdict where required. The approval record captures the evidence. Approved-edition immutability is itself a check (content hash recorded at approval; provenance checker verifies).
- **Console**: answer cards show the **approved** edition by default with a "draft available" chip; toggle to draft view (draft-watermarked charts so a screenshot can't silently masquerade as approved); history drawer lists all editions with edition-to-edition deltas (the "what changed since last quarter" briefing). Sidecar contract gains per-BQ `editions[]` (key, status, approved_by/date, data ref, report ref).
- **Relation to change-control**: this is the lightweight internal tier, owned by the `commercial` skill (`/commercial approve BQ-NN`). If a package ever needs formal Part 11 review (e.g., a board pack treated as a controlled record), the existing `change-control` skill is the escalation path — not rebuilt here.

### Decisions — CONFIRMED by Ben 2026-07-22

1. ✅ One topline **Commercial** section with inner category nav.
2. ✅ Charts rendered **in-console from sidecar JSON data series**; standalone HTML dashboards remain an escape hatch via the console's dashboards discovery.
3. ✅ Reports home: `docs/project/commercial/` (reports/ + .console/), sibling to `docs/project/corpus/`.
4. ✅ **Editions model** as specced (draft/approved/superseded, per-edition frozen data, approval gated on green checks). Sub-decisions still open for Phase-2: edition key granularity (date vs quarter) and who may approve.
5. ✅ **Provenance layer is mandatory and end-to-end** (Ben, same round): everything substantiated — every figure traces report → data series → normalized file → raw source; where data doesn't exist, the assumption is STATED AS SUCH (A-NNN), never silently absorbed. The console renders the chain (click a figure → provenance panel). An unsubstantiated claim (no snapshot citation AND no A-NNN reference) is a lint ERROR — nothing ships unsubstantiated.

## Skill Contracts (Phase 1 deliverable — v1)

### `corpus` skill — the grounding engine

**Dataset layout** (`docs/project/corpus/<domain>/<dataset>/`):

```
dataset.yml                 # config: normalized schema (columns/types/units/keys), sources,
                            #   acquisition method, max_age_days, usage_rights, semantic guards
snapshots/YYYY-MM-DD/
  raw/                      # byte-pinned payloads (openFDA JSON, fetched pages, internal exports)
  normalized/               # schema-validated CSV
  provenance.yml            # this snapshot's provenance tree
assumptions/A-NNN.yml       # first-class assumption records
waivers/W-NNN.yml           # freshness waivers (owner + expiry — waivers expire too)
latest                      # pointer to newest valid snapshot
```

**`provenance.yml` schema**: `snapshot`, `dataset`, `retrieved_at`; `sources[]` — {type: api|web|internal-export|generator, url/query or system-of-record, retrieved_at, content_hash, usage_rights, notes}; `transforms[]` — {input_hash, output_hash, script, description}; `assumptions_referenced[]`; `checks` — {schema_valid, asserts_passed, row_counts}. Every normalized file names its raw parent by hash — the substantiation chain's bottom half.

**`A-NNN.yml` schema**: id, title, needed_for (BQ ids / datasets), why_unavailable, estimation_method, value_or_range, confidence, sources_consulted, refresh_trigger, created, status (active | contradicted | retired). A refresh that surfaces contradicting public data flips status to `contradicted` in the delta report.

**Actions**: `init <domain>/<dataset>` (scaffold config + README) · `acquire <dataset>` (run acquisition → new snapshot; acquisition-time asserts + schema validation; nothing writes on failure) · `refresh <dataset>|--all` (re-acquire + delta report vs latest, incl. assumption-contradiction sweep) · `validate <dataset>` (schema + provenance completeness: parents resolve, hashes verify, referenced A-NNNs exist) · `diff <dataset> <a> <b>` · `assume` / `waive` (create A-NNN / W-NNN) · `check [--all]` (validate + freshness bands vs max_age_days + assumption/waiver status roll-up) · `list`.

### `commercial` skill — the analysis consumer

**Actions**: `answer <BQ-NN>` (deterministic computation → NEW DRAFT edition: report.md + data.json + snapshot pins; never touches an approved edition) · `field|market|roadmap|board` (pillar bundles) · `lint <BQ-NN>` (claim lint: every numeric claim carries `dataset@snapshot` or `A-NNN`; recompute/re-lookup each pair; estimation language without A-NNN = error; current-state claim on stale snapshot = error unless W-NNN) · `verify <BQ-NN>` (independent adversarial re-derivation subagent → verdict) · `approve <BQ-NN>` (gate: lint + freshness + verify green → approval.yml {who, when, checks-evidence, content hashes}, supersedes prior approved) · `render` (write `.console/` sidecars) · `check` (whole chain: corpus check + approved-edition hash integrity + sidecar consistency) · `catalog` (BQ roster + status).

**Sidecar contract** (`schema_version: 1.0`, mirrors submissions-skill pattern):
- `docs/project/commercial/.console/commercial-index.json` — one row per BQ: {id, question, category, personas, cadence, status: answered|draft-only|stale|blocked|not-implemented, approved_edition, draft_edition, editions[], verdict_headline, evidence_class, freshness, assumptions[], report_path}.
- Per-edition `data.json` — {bq, edition, status, series[] — each {id, label, unit, points, **provenance: {dataset, snapshot, transform}**, evidence_class}, verdicts[], assumptions[]}. The console plots series verbatim and renders the provenance panel from the series' provenance refs — it computes nothing, invents nothing.

**Provenance layer (end-to-end)**: report claim `[dataset@snapshot]` → data.json series provenance → normalized file hash → raw source URL + retrieved_at (or → A-NNN record). Substantiation is machine-walkable at every hop; the claim lint enforces presence, the provenance checker enforces resolvability, the console renders the walk.

## Strategy & Lessons capture

<!-- STRATEGY CONTENT: operations, commercial analytics tooling architecture -->
**Decision (2026-07-22, ben/108): Commercial analytics layer = `corpus` grounding engine + `commercial` analysis skill + versioned snapshot corpus + verification stack.**

- **Two skills, not one**: `corpus` (cross-cutting grounding engine — acquire / snapshot / validate / refresh / diff / assumptions / freshness) + `commercial` (analysis consumer — `field` / `market` / `roadmap` actions + deterministic computation library + claim lint). Mirrors the docflow pattern: an engine other skills can adopt (regulatory guidance-monitoring, post-market MAUDE trends are future tenants). Rejected: folding snapshot machinery into `commercial` (would trap a general capability in one consumer).
- **Corpus lives at `docs/project/corpus/<domain>/<dataset>/`** — shared project tree; immutable dated snapshots (`raw/` byte-pinned + `normalized/` schema-validated + `provenance.yml` with parent-by-hash + usage-rights), `latest` pointer, first-class A-NNN assumption records, delta reports on refresh. Extends the existing `docs/external/` document-provenance discipline (md5-pinned source → source-md → distilled) to structured data.
- **Real external data over fabrication**: acquire from public sources (openFDA 510(k)/MAUDE/recalls — public domain; competitor spec sheets; market reports) with real competitor names; fabricate only OUR internal data (fictional company), routed through the same snapshot machinery so it's swappable for real ERP/CRM/service exports in a client deployment. Where data doesn't exist, record an assumption — never silently invent.
- **Anti-hallucination architecture**: (a) the LLM orchestrates and interprets, scripts compute — no model-typed numbers; (b) asserts + schema validation at acquisition; (c) provenance completeness checks; (d) semantic guards as asserts (no MAUDE rate without a denominator assumption); (e) claim lint — every numeric claim in narrative carries a `dataset@snapshot` citation, mechanically recomputed; (f) adversarial re-derivation of headline claims by an independent subagent; (g) honesty labels measured/derived/assumed/unavailable; (h) freshness enforcement — per-dataset `max_age_days`, stale snapshots block current-state claims unless visibly waived.
- **Build order: field performance first** — most novel demo story, reuses post-market + fleet-management assets, and "are we to plan?" resonates with every commercial audience.
- **Visualization tier fully separated (confirmed 2026-07-22)**: analysis skills emit only data (markdown reports + schema-versioned JSON sidecars with chart series); the project console is a pure consumer rendering charts client-side — the same loose-coupling contract Submission/Tasks already use. One topline Commercial section, question-centric UI (the BQ catalog is the navigation spine).
- **Editions lifecycle for answers (confirmed 2026-07-22)**: each BQ answer is an immutable edition series (draft → approved → superseded); refresh opens a new draft, never mutates approved; approval is GATED on green checks (claim lint + freshness/waiver + adversarial verify) and hash-pins content; console shows approved by default with draft watermarking and per-question history + deltas. Formal Part 11 escalation stays with `change-control`, not rebuilt.
- **Plan expectations are first-class records (Ben review feedback 2026-07-22)**: actuals come from data, but the EXPECTATIONS they're judged against (close dates, targets, thresholds) must themselves be stated objects — id, statement, expected, basis, set_by, `validated:` flag — evaluated every edition (met / at-risk / not-met / not-evaluable) and rendered with an `unvalidated` chip when the expectation is a stand-in never grounded in a plan of record or the risk file. "Are the assumptions correct?" becomes an on-screen question, not an implicit trust. Companion additions from the same review: deterministic Risks/Mitigations/Issues narrative blocks (marker-cited, mirrored in the linted report) and timeseries trend charts (zero-filled so stalls render as flatlines).
- **Provenance layer is end-to-end and mandatory (confirmed 2026-07-22)**: every figure machine-walkably traces report claim → data series → normalized hash → raw source (or → stated A-NNN assumption); an unsubstantiated claim is a lint ERROR; the console renders the chain as a click-through panel.

**Why**: Commercial buyers ask "are we winning?" — the answers must be data-backed, reproducible, and honest about what's measured vs assumed; exposed epistemics are the differentiator over standard BI demos, and non-negotiable in a regulated industry.
**How to apply**: New analytics capabilities = new `commercial` actions + new corpora under `docs/project/corpus/`; any skill needing versioned external grounding should consume `corpus`, not roll its own snapshotting; every published figure must be script-computed and citation-carrying.
<!-- /STRATEGY CONTENT -->

<!-- LESSONS LEARNED: verification -->
**Lesson (2026-07-22, ben/108): pins-only adversarial verification catches what claim-lint structurally cannot — denominator choices.**
The claim lint proves every figure resolves to a source; it cannot ask "is this the RIGHT denominator?" The independent verifier (given pinned data + headlines, NOT the reports) caught two denominator defects the lint passed clean: a failure rate diluted by never-attempted devices (23.1% reported vs 35.3% per-attempt) and a mixed-basis ratio that flipped which region looked worst. Both numbers were arithmetically correct and fully cited — and still misleading. **How to apply**: the verify pass is not optional ceremony for substantive answers; prompt verifiers to recompute under alternative reasonable denominators/bases, not just reproduce the claimed one. Report basis choices explicitly in the report body.
<!-- /LESSONS LEARNED -->

<!-- LESSONS LEARNED: external-data-quality -->
**Lesson (2026-07-22, ben/108): openFDA identity fields are not normalized — plan entity resolution into the analysis tier from day one.**
Real acquisition immediately surfaced manufacturer/firm-name variants ("Fresenius Kabi USA, LLC" vs "USA LLC"; "ICU Medical, Inc." vs "Inc"; CareFusion split across "SD" and "303, Inc."), plus empty-term count buckets. Any per-firm aggregation over openFDA data without an entity-normalization map silently splits one company's totals across variants — the numbers look precise and are wrong. **How to apply**: the commercial skill's computation layer must carry an explicit firm-alias map (itself corpus-versioned, so normalization choices are provenance-tracked), and cross-checks like "top-N firms" should be run pre- and post-normalization during development.
<!-- /LESSONS LEARNED -->

<!-- LESSONS LEARNED: testing -->
**Lesson (2026-07-22, ben/108): smoke tests must vary invocation shape, not just the happy path.**
The corpus engine's command-acquisition path doubled paths when invoked with a relative `--root` (subprocess cwd = dataset dir + relative substitution), but the smoke test used an absolute scratchpad root and passed. First real project-tree use failed. **How to apply**: when a tool substitutes paths into subprocesses, test matrix must include relative-root/cwd-varied invocation, not just the convenient absolute form.
<!-- /LESSONS LEARNED -->

## Open Questions

- ~~Fictionalize competitors vs real names?~~ **Resolved 2026-07-22**: real names + real acquired public data; only OUR internal data is fabricated (banner-marked). Real-name claims must trace to real snapshots or A-NNN assumptions — the claim lint enforces this.
- Console integration depth for v1: full new console sections (like Submission) vs standalone HTML dashboards linked from the console Documents tab? → decide at Phase 3 dashboard step.
- Freshness waiver UX: who can waive a stale-snapshot block and how is the waiver recorded (inline marker vs assumptions-adjacent record)? → settle in Phase 1 spec.
- Registry destiny: `corpus` looks registry-bound (generic engine); `commercial` may stay project-local until proven. → defer to Phase 6.

## Resume

**Activation**: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 108`

**First action on resume**: Phase 1 — author the business-question catalog + corpus architecture spec sections in this doc (see Todos). No files outside `tasks/` touched yet; nothing committed.

## Economics

_By-hand person-hour estimate, **filled at checkpoint** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated; an empty `todos` list is ignored by the aggregator._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {"min": 1, "max": 2},
    "todos": [
      {
        "todo": "Business-question catalog: 6-persona fan-out, 72 candidates, top-30 + overflow",
        "personas": ["program-manager", "post-market"],
        "manual_hours": {"min": 12, "max": 24},
        "confidence": "low",
        "basis": "judgment — no external norm; by-hand equivalent = 6 exec-stakeholder interview sessions (prep + 1h + notes each) + cross-functional synthesis of a vetted 30-question catalog (~8-page doc at 1-2 hr/page, low end of TechScribe authoring anchor)"
      },
      {
        "todo": "Corpus + commercial architecture and skill contracts (viz tiers, editions lifecycle, provenance layer, sidecar schema)",
        "personas": ["systems-engineering", "rd-lead"],
        "manual_hours": {"min": 16, "max": 32},
        "confidence": "med",
        "basis": "requirements/arch-decomposition anchor (Wiegers 10-18% of project effort applied qualitatively) — by-hand equivalent: multi-stakeholder architecture spec for a 4-tier data/analysis/viz system w/ lifecycle + provenance model, ~10-page design doc + schema definitions + 2-3 review rounds"
      },
      {
        "todo": "Corpus engine skill v1 (~600 LOC CLI: acquisition/snapshot/provenance/validation/freshness/delta) + templates + docs scaffold + smoke test",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 24, "max": 48},
        "confidence": "med",
        "basis": "software anchor (325-750 LOC/dev-month =~ 20-25 LOC/day): ~600 net LOC data-integrity tooling w/ hash-chain provenance + 9 subcommands + smoke suite -> ~3-6 dev-days; internal tooling (not IEC 62304), mid-range"
      },
      {
        "todo": "Six first corpora: 3 real openFDA acquisitions (incl. count-mode engine extension + 2 bug fixes + A-001 assumption) + 3 seeded internal generators with aligned fleet model + dataset READMEs",
        "personas": ["rd-lead", "post-market"],
        "manual_hours": {"min": 16, "max": 32},
        "confidence": "med",
        "basis": "software anchor for ~400 LOC generators/configs (~2-3 dev-days) + judgment for openFDA endpoint research, schema design against real payload shapes, and MAUDE epistemics documentation (post-market specialist input, no external norm)"
      },
      {
        "todo": "Commercial skill v1: editions/lint/approve/render engine (~450 LOC) + skill docs + templates",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 20, "max": 40},
        "confidence": "med",
        "basis": "software anchor (20-25 LOC/day): ~450 LOC engine with lifecycle state machine, claim-lint parser, hash-pinned approvals, sidecar serialization -> ~2.5-5 dev-days; internal tooling"
      },
      {
        "todo": "Approvals ceremony (6 editions, gated) + 3 new computations (BQ-06/12/18) answered + rendered + browser-verified",
        "personas": ["rd-lead", "quality-engineering"],
        "manual_hours": {"min": 8, "max": 16},
        "confidence": "med",
        "basis": "software anchor for ~250 LOC new computations (~1-1.5 dev-days) + judgment for threshold/keyword-map design and an approval review pass per edition (QE reviewer at rigorous doc-review rate, 6 short reports)"
      },
      {
        "todo": "Console Commercial section: loader/router + 2 templates + CSS + nav wiring + docs (project-console 1.42.0), TestClient + live-browser verified",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 16, "max": 30},
        "confidence": "med",
        "basis": "software anchor (20-25 LOC/day): ~700 LOC across loader/router/templates/CSS in an existing FastAPI codebase incl. chart rendering + lifecycle UI states -> ~2-4 dev-days; frontend iteration typically mid-range"
      },
      {
        "todo": "Project catalog + six deterministic computations + entity aliases + A-002 + six lint-green draft editions",
        "personas": ["rd-lead", "program-manager"],
        "manual_hours": {"min": 20, "max": 36},
        "confidence": "med",
        "basis": "software anchor for ~430 LOC computations + ~250-line catalog config (~2-3 dev-days) + judgment for analytical design of six answers w/ evidence-classing and assumption modeling (BI-analyst work, no external norm)"
      }
    ]
  }
}
```

## Changelog

- 2026-07-22: Ben's BQ-26 review round shipped (commercial v2 + project-console 1.43.0): first-class plan expectations (basis/set_by/validated, per-edition met/not-met verdicts, unvalidated chips), deterministic Risks/Mitigations/Issues narrative, zero-filled timeseries trend charts, editions left-rail tree, catalog-level advisor drawer. BQ-23/24/26/18 re-answered as new drafts (approved editions untouched, newer-draft banners). Browser-verified. PR next.
- 2026-07-22: Approvals + second tranche live in console: six editions APPROVED (Ben-authorized, dossier-cited, hash-pinned); BQ-06/12/18 computed from existing corpora (competitor cycle time 213d median / clearance sweep / CAPA trigger on occlusion-alarm); sidecar 6 answered + 3 drafts; console restarted + verified (Approved chips, watermark gone). PR next.
- 2026-07-22: Console section MERGED: PR #130 (`e8eea09`); the live console (restarted during verification) serves /commercial now. Phases 1–3 + viz tier complete; remaining in-plan: pillar 2 (market), pillar 3 roadmap computations, advisors personas, registry decisions, Ben's approvals of the six drafts.
- 2026-07-22: Console Commercial section built + verified live (project-console 1.42.0): catalog + answer views consuming the sidecar, draft watermarks, evidence/freshness badges, provenance panels, edition history, advisor drawer. Browser-verified on the running console (BQ-24 + BQ-19 pages). Not yet committed; PR next.
- 2026-07-22: Adversarial verification round complete + all findings actioned (dossier in `_work/`); campaign corpus refreshed to 2026-07-22.2; BQ-23/24/25/26 re-answered with corrected bases; verification lesson captured. Ready to push Phase 3 (dashboard/console view deferred to next chunk).
- 2026-07-22: Phase 3 GREEN-LIT and largely built same day: commercial skill v1 + docs/project/commercial/ (catalog 30 BQs, 6 computations, entity aliases, A-002) + six lint-green draft editions + sidecar + commercial check GREEN. Corpus engine fix: globally-unique A/W record ids (collision caught in real use). Adversarial verify agent in flight; approvals deliberately left to Ben; dashboard + PR pending. Nothing committed yet this phase.
- 2026-07-22: **Phase 2 COMPLETE** — PR #128 merged (`9ed0a7c`); corpus skill + 6 corpora on main; corpus check GREEN post-merge. Next: Phase 3 — `commercial` skill v1 + field-performance vertical slice (computation library, `field` action, claim lint, dashboard + console sidecar).
- 2026-07-22: All six first corpora landed; corpus check GREEN. External (real): recalls (136 since 2021) + MAUDE manufacturer counts (99 buckets; engine gained openFDA count-mode + openfda-count normalizer; A-001 denominator assumption gated the acquire). Internal (fabricated, seeded, banner-stamped): fleet (884 devices) / complaints (430) / upgrade-campaign (389; EMEA-behind + hw_rev-B failure-cluster narrative verified in data). Engine fixes: absolute-path substitution for command acquisition; empty-term count buckets skipped w/ log. 2 lessons captured (entity normalization; invocation-shape testing). 5 dataset READMEs written. Nothing committed yet; PR next.
- 2026-07-22: First REAL corpus acquired: `commercial/openfda-510k-infusion` snapshot 2026-07-22 (29 FRN 510(k) records live from api.fda.gov, hash-pinned provenance, corpus check GREEN). Nothing committed to git yet.
- 2026-07-22: Phase 2 GREEN-LIT by Ben; corpus skill v1 BUILT: `.claude/skills/corpus/` (SKILL.md, README, `scripts/corpus.py`, 3 templates) via /skill-creator conventions; smoke-tested full lifecycle (init→acquire→validate→check→refresh w/ .2-suffix immutable snapshot + delta report→assume/waive→tamper-detection fail); `docs/project/corpus/` scaffolded (README + parent README row/changelog); `corpus` added to `project.yml approved_skills`. NOT yet committed. Next: first corpora (openFDA external + fabricated internal generators).
- 2026-07-22: Phase-1 design completed: viz & skills architecture (4-tier, console-sidecar pattern per project-console SKILL.md) + editions lifecycle (draft/approved/superseded, gated approval) + end-to-end provenance mandate — all CONFIRMED by Ben; both skill contracts written (`## Skill Contracts`: corpus engine + commercial consumer + sidecar schema v1.0). Remaining Phase-1 item: Ben's final look at catalog + contracts → Phase-2 green light.
- 2026-07-22: Business-question catalog v1 authored (`## Business-Question Catalog`): 6 parallel persona agents (CCO, Product, Field Service, Post-Market, CFO, + Board/corporate lens added mid-flight at Ben's request to span the 5-device portfolio) produced 72 grounded candidates; merged 13 cross-lens convergences; top 30 selected (13 HIGH-assumption by design), ~25 parked in overflow. Awaiting Ben's review before the corpus-architecture spec step.
- 2026-07-22: Discussion rounds 2–4 reshaped the architecture: real acquired external data (openFDA et al.) + fabricated internal data through one snapshot machinery; first-class A-NNN assumption records; separate `corpus` grounding-engine skill at `docs/project/corpus/` + `commercial` consumer skill; 8-layer anti-hallucination check stack incl. freshness enforcement (`max_age_days`, stale blocks current-state claims unless waived). Plan restructured to 6 phases (corpus engine is now Phase 2). Strategy block updated; real-names question resolved.
- 2026-07-22: Task created. Ideation session with Ben produced the three-pillar commercial analytics framing; scoping decisions locked (field-first, one suite skill, `docs/project/commercial/` data home — superseded same day by the corpus split above); 5-phase plan captured.
