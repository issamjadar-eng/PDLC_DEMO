# 102 — Risk File Backfill + Trace-Matrix Risk Mapping

**ID**: 102
**Created**: 2026-07-14
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

Backfill the PP3500 (pca-device) risk documentation — hazard analysis + FMEA(s) — as credible ISO 14971-conformant DHF artifacts, and wire them into the project trace matrix so risks show up mapped to design inputs.

- Goal 1: Credible risk file content — hazard analysis (hazard → hazardous situation → harm, severity/probability, risk controls) + FMEA(s) — grounded in the QMS risk-management forms/SOPs and existing design inputs. Demo-banner marked.
- Goal 2: Risk rows appear in the trace matrix mapped to design inputs (per the trace-matrix skill's documented actions/config — not hand-edited sidecars).
- Goal 3: Decide + document the data organization (hazard register vs FMEA split, ID schemes, folder layout per DHF conventions).

## Todos

_Actionable work items. Check off as completed._

- [x] Read contracts: trace-matrix SKILL.md (v8, end-to-end), `trace-matrix.yml`, default risk parser, graph.py risk-overlay handling, project software.py adapter pattern, GL-TMP-RM-003 (hazard analysis FORM), GL-TMP-RM-004 (FMEA FORM), GL-STD-RM-001 (S/P scales + acceptance matrix), pca-device risk-management README, design-inputs.md (34 DIs)
- [x] Survey existing state: pca-device risk layer = 0 items (`source is awaiting-content placeholder` — trace-matrix.yml points at `risk-strategy.md` strategy stub); risk-management/ holds ben/023 placeholder stubs for GL-TMP-RM-002/-003/-004×2
- [x] Decide data organization (see Strategy block below)
- [x] Author hazard analysis `GL-TMP-RM-003-hazard-analysis.md` (agent) — 16 hazards HAZ-001…016, FORM's 15 columns verbatim, GL-STD-RM-001 scoring (pre: 6 Unacceptable/10 ALARP; post: 0 Unacceptable/7 ALARP/9 Acceptable), 27 distinct DIs cited (all exist), 0 [VERIFY] flags
- [x] Author dFMEA + pFMEA `GL-TMP-RM-004-{design,process}-fmea.md` (agent) — dFMEA 21 modes FM-D-001…021 (top RPN 32: air-sensor missed bubble, watchdog failure; 7 open actions), pFMEA 9 modes FM-P-001…009; 1 [VERIFY] per file (O-scale anchors deferred to RM Plan — used GL-STD-RM-001 §4 P anchors as proxy); deterministic cross-check: 0 dangling HAZ/DI refs, banners + AI-CHANGELOG present in all 3 docs
- [x] Write project risk adapter `tools/project-console/trace-matrix/adapters/risk.py` + rationale in `tools/project-console/trace-matrix/analysis-notes.md` (new file; also backfilled a software.py note); `trace-matrix.yml` pca-device risk source → `GL-TMP-RM-003-hazard-analysis.md`, id_prefix `HZ`→`HAZ`
- [x] `/trace-matrix build --dhf pca-device` → sidecar verified: risk layer 16 items ([proj] adapter, 0 warnings), 33 `design_inputs_to_risk` edges, DI orphans 7→1, risk orphans 0; the 3 broken refs (SW→VER) pre-date this change (verified vs HEAD sidecar)
- [x] QA-conformance pass (quality-engineering agent) vs GL-TMP-RM-003/-004: **CONFORMANT** — all 16 HA rows matrix-recomputed clean, RPN arithmetic verified on all 30 FMEA rows, WI/STD citations verified. F9 (minor FAIL: "ALARP rows" mislabel in both FMEA coverage summaries) **fixed** + QA verdict rows appended to all 3 AI-CHANGELOG blocks; F3 + F15 deferred (see Open Questions). Lint on all 3 docs: no hard violations (high-recall candidates + 2 FORM-prescribed bare-enum WARNs, accepted)
- [ ] Final-stage: run `/reference-audit` over the hazard analysis + FMEAs (citation-bearing docs — standards clauses cited)
- [ ] Update task doc + index; commit/push only when user asks

## Strategy

<!-- STRATEGY CONTENT: risk, risk-file-organization, hazard-register-vs-fmea-split, trace-matrix-risk-layer -->
**Decision — risk file organization (2026-07-14):** The PP3500 risk file is organized as a **hazard-analysis spine + FMEA feeders**. The ISO 14971 top-down hazard analysis (`GL-TMP-RM-003-hazard-analysis.md`, HAZ-### IDs) is the integrating artifact and the *only* trace-matrix risk source: each HAZ row carries a `Design Input(s)` column whose DI IDs become `traces_forward_ids` → `design_inputs_to_risk` edges (risk is a parallel overlay in graph.py, exempt from layer-order checks). The bottom-up dFMEA/pFMEA (`GL-TMP-RM-004-*.md`, FM-D-/FM-P- IDs) link into the spine via their `Linked Hazard ID` column and do **not** enter the trace matrix directly — keeps the matrix's risk layer single-sourced and uncluttered while preserving full FMEA→hazard→DI traceability inside the risk file.
**Why:** The trace-matrix skill's risk layer takes one source per DHF; the QMS FORM GL-TMP-RM-003 already prescribes a `Design Input(s)` column, so the hazard worksheet is the natural edge-bearing doc. FMEA rows are failure-mode-granular (3–5× more rows than hazards) and would drown the console risk view.
**How to apply:** New DHFs backfilling risk: fill the GL-TMP-RM-003 instance first, point `trace-matrix.yml` `risk.source` at it with `id_prefix: HAZ`, reuse the project risk adapter.

<!-- STRATEGY CONTENT: risk, id-scheme -->
**Decision — risk ID scheme:** `HAZ-###` per the QMS FORM GL-TMP-RM-003 exemplar row (not the trace-matrix default `HZ`); `trace-matrix.yml` `id_prefix` updated to `HAZ`. FMEA IDs `FM-D-###` (design) / `FM-P-###` (process). The QMS template is the authoring contract (doctype-governance rule); tooling config follows the FORM, not vice versa.

## Open Questions

- **QA F3 (deferred, non-blocking):** Approvals sections were added to the three instances but neither FORM (GL-TMP-RM-003/-004) carries one; roles enumerated in the HA, empty in FMEAs. Reconcile at next FORM revision or standardize roles across instances.
- **QA F15 (team decision):** docflow frontmatter `conversion_method: "claude-authored"` names a vendor; the ai-changelog rule scopes vendor-neutrality to "content and changelogs" — decide whether the docflow schema vocabulary needs a neutral value (project-wide question, not specific to these docs).
- **FMEA O-scale anchors ([VERIFY] in both FMEAs):** GL-WI-RM-002 §4 defers O/D scales to the RM Plan (GL-TMP-RM-001), and no PP3500 RM Plan instance exists yet; GL-STD-RM-001 §4 P anchors used as O proxy. Resolve when the RM Plan is baselined.
- Other DHFs (connectivity-adapter, cloud-suite + children) still have empty risk layers pointing at `risk-strategy.md` placeholders — backfill the same way (adapter is shared; flip source + `id_prefix: HAZ` per DHF).

## Resume

### In-flight artifacts
All uncommitted (Claude has committed nothing; user controls commits):
- `docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-003-hazard-analysis.md` — 16-hazard ISO 14971 worksheet, 0.2 DRAFT
- `docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-004-design-fmea.md` — 21 modes, 0.2 DRAFT
- `docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-004-process-fmea.md` — 9 modes, 0.2 DRAFT
- `tools/project-console/trace-matrix/adapters/risk.py` — new project adapter (GL-TMP-RM-003 FORM parser, HAZ→DI edges)
- `tools/project-console/trace-matrix/analysis-notes.md` — new; adapter rationale (+ software.py backfill note)
- `trace-matrix.yml` — pca-device risk source → hazard-analysis doc, prefix HAZ
- `docs/project/console/pca-device/console_trace_matrix.{md,json}` — rebuilt sidecar (risk: 16 items, 33 design_inputs_to_risk edges)
- `tasks/ben/102-*.md`, `tasks/ben/000-index.md` — this task + index row
- Pre-existing modified files not from this task: `.claude/sync-log.md`, `tasks/ben/101-*.md` (ben/101 leftovers)

### First action on resume
- Activate: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 102`
- Remaining: (1) `/reference-audit` over the 3 risk docs (final-stage, before marking Complete); (2) commit/push per git-workflow **only when user asks**; (3) optionally verify the console Trace Matrix view in-browser.
- Do NOT redo: authoring, adapter, build, QA (all done + verified); do NOT commit unprompted.

## Economics

_By-hand person-hour estimate, **filled at checkpoint** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated; an empty `todos` list is ignored by the aggregator._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {"min": 0.75, "max": 1.5},
    "todos": [
      {
        "todo": "Contracts read + state survey + risk-file organization decision",
        "personas": ["risk-management", "systems-engineering"],
        "manual_hours": {"min": 4, "max": 8},
        "confidence": "med",
        "basis": "requirements/arch decomposition ratio proxy — scoping risk-file structure vs QMS forms + trace tooling; judgment-adjacent"
      },
      {
        "todo": "Author 16-hazard ISO 14971 hazard analysis (GL-TMP-RM-003 instance) grounded in 34 DIs, GL-STD-RM-001 scoring",
        "personas": ["risk-management", "clinical-affairs"],
        "manual_hours": {"min": 12, "max": 24},
        "confidence": "med",
        "basis": "judgment-tier (risk analysis has no published hour norm) — per-page authoring 3-7 hr/pg x ~2 pg + cross-functional HA workshop adder"
      },
      {
        "todo": "Author dFMEA (21 modes) + pFMEA (9 modes) with scoring, actions, hazard linkage",
        "personas": ["risk-management", "rd-lead", "quality-engineering"],
        "manual_hours": {"min": 16, "max": 32},
        "confidence": "med",
        "basis": "judgment-tier — FMEA workshop construction: 30 modes across 2 sessions x 3-4 specialists + worksheet authoring"
      },
      {
        "todo": "Project risk adapter (risk.py ~120 LOC) + trace-matrix.yml rewire + analysis-notes rationale",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 3, "max": 6},
        "confidence": "high",
        "basis": "software anchor 20-25 LOC/day low-end for small parser module incl. understanding adapter_api contract"
      },
      {
        "todo": "Trace-matrix build + sidecar verification (edges, orphans, broken-ref regression vs HEAD)",
        "personas": ["systems-engineering"],
        "manual_hours": {"min": 1, "max": 2},
        "confidence": "high",
        "basis": "judgment — tool run + JSON diff review"
      },
      {
        "todo": "QA-conformance pass (FORM schemas, full matrix recompute, RPN arithmetic, cross-doc integrity) + lint + F9 fix",
        "personas": ["quality-engineering"],
        "manual_hours": {"min": 6, "max": 12},
        "confidence": "med",
        "basis": "rigorous regulated doc review 1-3 pg/hr x ~12 pg across 3 docs (Gilb & Graham) incl. recomputation"
      }
    ]
  }
}
```

## Changelog

- 2026-07-14: Task created.
- 2026-07-14: Contracts read (trace-matrix SKILL.md v8, risk.py default parser, graph.py overlay model, GL-TMP-RM-003/-004 FORMs, GL-STD-RM-001 criteria, 34-DI design-inputs). Organization decided: hazard-analysis spine (HAZ-###, trace-matrix source) + FMEA feeders (FM-D-/FM-P-, Linked Hazard ID). Two authoring agents launched (hazard analysis; dFMEA+pFMEA) with a fixed 16-hazard spine. Wiring landed: `tools/project-console/trace-matrix/adapters/risk.py` (parses GL-TMP-RM-003 FORM columns, authors HAZ→DI edges from `Design Input(s)`), `analysis-notes.md` rationale, `trace-matrix.yml` risk source/prefix update. Next: agents finish → build → verify sidecar → QA pass.
- 2026-07-14: Pushed to main via PR #100 (merge landed at origin/main `7f9a40e`; branch deleted). Remaining before Complete: /reference-audit final-stage pass.
- 2026-07-14: All authoring + wiring shipped this session. HA (16 hazards) + dFMEA (21) + pFMEA (9) written by agents, grounded in GL-WI-RM-001/-002 + GL-STD-RM-001 + design-inputs.md. Build verified: risk layer 16 items / 33 `design_inputs_to_risk` edges / DI orphans 7→1 / no new gaps. QA agent verdict CONFORMANT (F9 wording fixed inline; F3/F15 deferred to Open Questions); lint clean of hard violations; AI-CHANGELOG verdict rows appended; sidecar rebuilt post-fix. Nothing committed. Remaining: /reference-audit (final-stage) + commit/push on user request.
