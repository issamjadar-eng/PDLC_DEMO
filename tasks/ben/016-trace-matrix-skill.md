# 016 — Trace Matrix Skill + Console Section

**ID**: 016
**Created**: 2026-04-14
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## Goals

Build a generic **`trace-matrix` skill** that parses the design-controls source docs of any DHF, computes the bidirectional trace graph (User Needs ↔ Design Inputs ↔ Architecture ↔ V&V, with Risk as an overlay), and emits both a controlled DHF deliverable and a structured sidecar. Then add a **Trace Matrix section** to `project-console` that reads the sidecar and renders an interactive view.

The skill is the writer; the console is the reader. The console never computes traces — it only visualizes what the skill produced. This preserves the console's "never modifies docs/" rule from `tools/project-console/ARCHITECTURE.md`.

Success criteria:
1. Running the skill against PP3500 regenerates `design-controls/trace-matrix/trace-matrix.md` as a full bidirectional matrix and writes a parallel `trace-matrix.json` sidecar.
2. The skill reports orphans (UNs without DIs, DIs without verification, etc.) and gaps (broken/unknown trace targets) deterministically.
3. The skill is project-agnostic — no PP3500/PainEase/infusion-pump strings in skill code; project-specific config (ID prefixes, source paths) lives in a per-project `trace-matrix.yml`.
4. The console's new `/trace-matrix` section renders one card per DHF, opens a per-DHF view with layer-by-layer columns and gap highlights, and survives a console restart.
5. Skill validates against sister project (`../../projects/arthrex/pccp/`) without code changes.

## Non-Goals (for v1)

- Not authoring any new DHF content. Skill only parses what's already there.
- Not replacing the trace-matrix README or formal/ DOCX deliverables — only the working markdown + JSON sidecar.
- Not solving cross-DHF traces (e.g., pca-device DI → cloud-suite SR). Single-DHF only in v1.
- Not a chat sidecar on the console section yet (deferred to v2).

---

## System Architecture (revised 2026-04-14)

**Architecture revision** (supersedes the original "two pieces, hard boundary" sketch below):

The original sketch had the console skill knowing about trace matrices natively. The revised design uses **two presence-based discovery rules** so the two skills stay loosely coupled:

1. **Section discovery (data-driven).** The console scans each DHF for `design-controls/trace-matrix/trace-matrix.json`. If any are found, the Trace Matrix section appears. The console knows only the JSON contract — it has zero import-time dependency on the `trace-matrix` skill.
2. **Workflow discovery (skill-plugin-driven).** The console scans `.claude/skills/*/console/workflows/*.py` at startup. The `trace-matrix` skill ships `console/workflows/trace_matrix_build.py`, which surfaces a "Build Trace Matrix" workflow that shells to `scripts/build.py`. Install the skill → the workflow appears. Uninstall it → the workflow vanishes; the section still renders any pre-existing sidecars.

**Demo loop:**
> Workflows → "Build Trace Matrix" → run → SSE streams build output → workflow completes → Trace Matrix section now renders the freshly written sidecars.

**Ownership:**

| Piece | Owns | Imports from the other? |
|---|---|---|
| `trace-matrix` skill | parsers, graph, gap engine, md/json emitters, `trace-matrix.yml` config, **and** a console-plugin workflow file | No |
| `project-console` skill | Trace Matrix section renderer (JSON-shape consumer), skill-plugin discovery scanner | No |
| PDLC_DEMO project | `trace-matrix.yml` at root (per-DHF source map) | n/a |

The console skill's new `skill-plugin discovery` feature is project-agnostic and pushes upstream cleanly with task 015's project-console work — any future skill can ship `console/workflows/*.py` and get auto-registered.

### (Original sketch retained for context — superseded by the discovery model above)

### Two pieces, hard boundary

```
┌──────────────────────────────────┐         ┌──────────────────────────────┐
│   trace-matrix skill (NEW)       │  emits  │   design-controls/           │
│   .claude/skills/trace-matrix/   │ ──────▶ │     trace-matrix/            │
│                                  │         │       trace-matrix.md   ◀── DHF deliverable
│   - parse source docs            │         │       trace-matrix.json ◀── console sidecar
│   - build trace graph            │         └──────────────────────────────┘
│   - compute orphans/gaps         │                          │
│   - emit md + json atomically    │                          │ reads
└──────────────────────────────────┘                          ▼
                                              ┌──────────────────────────────┐
                                              │   project-console            │
                                              │   /trace-matrix section      │
                                              │   - per-DHF index            │
                                              │   - layered render           │
                                              │   - gap highlighting         │
                                              │   PURE READ — never writes   │
                                              └──────────────────────────────┘
```

### Skill: `trace-matrix`

**Layout** (mirrors other skills in `.claude/skills/`):

```
.claude/skills/trace-matrix/
├── SKILL.md
├── VERSION
├── README.md                  # quickstart + Best Practices table
├── scripts/
│   ├── build.py               # main entry — parses + writes outputs
│   ├── check.py               # dry-run, exits non-zero on gaps (CI-friendly)
│   └── parsers/
│       ├── markdown_table.py  # generic md table → list[dict]
│       ├── user_needs.py      # extracts UN-XXX nodes
│       ├── design_inputs.py   # extracts DI-XXX nodes + UN refs
│       ├── architecture.py    # extracts SR/ARCH/MOD nodes + DI refs
│       ├── vnv.py             # extracts VER-XXX nodes + DI refs
│       └── risk.py            # extracts HZ-XXX nodes + DI/VER refs
├── templates/
│   ├── trace-matrix.md.j2     # output md template
│   └── trace-matrix.yml       # per-project config stub (copied on init)
└── references/
    └── id-conventions.md      # how prefix matching works
```

**Project-side config** (`trace-matrix.yml` at project root, generated by `init`):

```yaml
version: 1
dhfs:
  - name: pca-device
    layers:
      user_needs:
        source: docs/project/dhfs/pca-device/design-controls/user-needs/user-needs.md
        id_prefix: UN
      design_inputs:
        source: docs/project/dhfs/pca-device/design-controls/requirements/design-inputs.md
        id_prefix: DI
        traces_from: user_needs
      architecture:
        source: docs/project/dhfs/pca-device/design-controls/architecture/pca-device-system-sad.md
        id_prefix: SR     # placeholder — confirm from doc
        traces_from: design_inputs
      vnv:
        source: docs/project/dhfs/pca-device/design-controls/vnv/testing-strategy.md
        id_prefix: VER
        traces_from: design_inputs
    risk:
      source: docs/project/dhfs/pca-device/risk-management/risk-strategy.md
      id_prefix: HZ
      traces_to: [design_inputs, vnv]
    output_dir: docs/project/dhfs/pca-device/design-controls/trace-matrix/
```

**Actions**:
- `init` — scans `project.yml` DHFs, writes a `trace-matrix.yml` stub with best-guess source paths
- `build` — parses, computes, writes `trace-matrix.md` + `trace-matrix.json` per DHF
- `check` — same as build but writes nothing; exits 1 if any gap found (for hooks/CI)

**Output JSON shape** (the contract the console depends on):

```json
{
  "dhf": "pca-device",
  "generated_at": "2026-04-14T...",
  "layers": [
    {"key": "user_needs",   "title": "User Needs",   "items": [{"id": "UN-001", "summary": "...", "traces": ["DI-001", "DI-002"], "category": "G1"}]},
    {"key": "design_inputs","title": "Design Inputs","items": [...]},
    ...
  ],
  "edges": [{"from": "UN-001", "to": "DI-001"}, ...],
  "gaps": {
    "orphans": {"user_needs": ["UN-022"], "design_inputs": [], "vnv": ["VER-007"]},
    "broken_refs": [{"from": "DI-014", "to": "UN-099", "reason": "unknown_id"}]
  }
}
```

### Console: `/trace-matrix` section

**Files added** to `.claude/skills/project-console/console/`:

```
console/
├── trace_matrix/
│   ├── __init__.py
│   ├── router.py        # /trace-matrix routes
│   ├── loader.py        # finds + loads trace-matrix.json sidecars per DHF
│   └── render.py        # builds the per-DHF HTML view
└── web/templates/
    ├── trace_matrix_index.html
    └── trace_matrix_view.html
```

**Routes**:
```
/trace-matrix                       index — one card per DHF that has a sidecar
/trace-matrix/{dhf}                 layered view with gap highlights
/trace-matrix/{dhf}/raw             raw JSON (debugging)
```

**Loader rule**: scan each `dhf:` from `project.yml`, look for `design-controls/trace-matrix/trace-matrix.json`. Missing → card shows "Not generated yet — run `/trace-matrix build`."

This mirrors the dashboards-section pattern: a fifth top-level section alongside Agents / Documents / Dashboards / Workflows. Nav update in `_base.html`.

---

## Phasing

- [x] **Phase 1 — Source-doc reconnaissance.** Done 2026-04-14. See **Phase 1 Findings** below.
- [x] **Pass 1 — Skill build engine.** Done 2026-04-14. Scaffold, parsers, graph, emitters, CLI, regenerated PP3500 matrix.
- [x] **Pass 2 — Console section.** Done 2026-04-15. `/trace-matrix` + `/trace-matrix/{dhf}` routes, loader, templates, nav, inline Rebuild. Verified in browser.
- [x] **Pass 3 — Compatibility / adapter generation pass.** Done 2026-04-15. `adapter_api.py` contract, default parsers moved to `parsers/defaults/`, project-override resolver, `analyze.py` rational-check CLI, sidecar v1.1 with `source_files`, SKILL.md v2 rewrite, project-side adapter README. PDLC_DEMO passes with zero generated adapters. 6 audit leaks + 1 doc drift all resolved.
- [x] **Pass 4 — UI revision + SE Assistant.** Done 2026-04-15. Full-width tabbed view, folder-tab styling, row-level expand with caret in ID column, SE Assistant drawer (resizable, multi-thread localStorage, inline MD renderer).
- [ ] **Phase 9 — Sister-project (Arthrex PCCP) dry run.** Pending. Copy skill, author sister `trace-matrix.yml`, run `analyze.py`, expect defaults to fail on SRS-shaped docs, exercise the adapter generation flow in SKILL.md `init`.
- [ ] **Phase 10 — Upstream push.** Pending. `/sync-skills push` for `trace-matrix` skill + project-console Trace Matrix section additions. Update `project.yml` `approved_skills`.

## Phase 1 Findings — Source-Doc Reconnaissance (2026-04-14, PP3500)

| Layer | Source file | State | Node IDs | How edges are carried |
|---|---|---|---|---|
| **User Needs** | `design-controls/user-needs/user-needs.md` | ✅ Populated — 22 UNs across 9 functional groups (G1–G9) | `UN-001 … UN-022` | Top of trace; no upstream edges |
| **Design Inputs** | `design-controls/requirements/design-inputs.md` | ✅ Populated — ~30 DIs in 8-col tables | `DI-001 … DI-0nn` | Two trace columns per row: **"Traces to UN"** (comma-separated `UN-001, UN-002`) and **"Verification Method"** (free text, often containing `VER-PP3500-BT-005` / `VER-PP3500-SW-002` style IDs in parens) |
| **Architecture** | `design-controls/architecture/pca-device-system-sad.md` | ⚠️ Module table populated, **trace-to-DI mapping missing** | `M1 … M7` (seven on-device modules) | **No Module ↔ DI table exists.** The SAD describes module responsibilities in prose but never says "M1 implements DI-001, DI-002, …". Architecture→DI edges are unrecoverable from the current doc. |
| **V&V** | `design-controls/vnv/testing-strategy.md` | ❌ Empty placeholder (`awaiting-content`) | none in this doc | The only V&V identifiers in the project today are the `VER-PP3500-*` strings *inside the DI doc's "Verification Method" column*. There is no standalone protocol list. |
| **Risk** | `risk-management/risk-strategy.md` | ❌ Empty placeholder (`awaiting-content`) | none | No hazards exist anywhere in the DHF tree. `formal/` is empty too. |

**Implications for the parser design:**

1. **UN parser** — straightforward markdown-table extraction.
2. **DI parser** — straightforward, *and* it carries double duty: it's the source of both DI nodes and the V&V edge data (via the verification column).
3. **V&V layer source** — for v1, **derive V&V nodes from the DI doc's verification column**, not from `testing-strategy.md`. Each unique `VER-PP3500-*` ID found becomes a V&V node; DI rows with no parseable VER ID produce a "DI without verification reference" gap. When a real `verification-protocols.md` doc lands later, the source swap is a one-line config change in `trace-matrix.yml`.
4. **Architecture layer** — for v1, parse the seven module rows (M1–M7) as nodes but render them with **zero outbound edges** and flag the entire layer as "module ↔ DI mapping not yet captured in SAD." This is the user-requested behavior ("missing should be indicated as missing"). Adding the Module↔DI mapping table to the SAD is a separate authoring task; it is **not in scope for 016**.
5. **Risk overlay** — for v1, render the entire layer as "0 hazards — risk source not yet populated." Same principle as architecture: surface the gap, don't paper over it.

**Note on cross-DHF scope:** PP3500's SAD explicitly excludes the Connectivity Adapter and Cloud Suite (separate DHFs). v1 single-DHF-only stance from the Non-Goals holds — no cross-DHF traces.

## Decisions

- **2026-04-14 — v1 layer scope: full four layers + risk overlay.** UN ↔ DI ↔ Architecture ↔ V&V with Risk (HZ) as an overlay touching DI and V&V. Missing items must be surfaced as gaps in the output, not hidden. Rationale: parser infrastructure cost is identical regardless of layer count; trimming would hide the most interesting gaps (DIs without verification, hazards without controls). V&V layer is expected to be sparse in PP3500 today (only `testing-strategy.md`, no protocol IDs) — the matrix should *show* that gap, not paper over it.

## Open Questions

(captured here as we go — see chat for current open question)

## Changelog

- 2026-06-08: Closed Complete via task-doc audit — trace-matrix skill shipped (487879d), browser-verified, since evolved to v8. Moved to Completed in 000-index.md.
- 2026-04-14: Task created. System architecture drafted (skill + console split, JSON sidecar contract, file layout). Source docs confirmed present for PP3500.
- 2026-04-14: Decision — v1 covers full four layers + risk overlay. Missing items rendered as gaps. Phase 1 source-doc reconnaissance starting.
- 2026-04-14: Phase 1 reconnaissance complete — see Phase 1 Findings. Layers are very uneven (UN/DI populated; SAD has modules but no DI mapping; V&V and risk are empty placeholders). Decision: derive V&V nodes from the DI doc's verification column for v1; render architecture as nodes-without-edges and risk as empty layer; both surface as visible gaps.
- 2026-04-14: Console rendering decision — option #1 + #6: inline `<details>` expanders for IDs (showing summary + traces with labels + criticality + gap warnings) plus an "↗ source" link to the existing documents browser, plus an expand-all/collapse-all button. JSON sidecar carries labels alongside IDs (no second fetch). Side-pane (#3) deferred to v2.
- 2026-04-14: **Architecture revision** — switch from "console knows about trace-matrix natively" to **loose coupling via two presence-based discovery rules**: console scans DHFs for `trace-matrix.json` sidecars (section discovery) and scans `.claude/skills/*/console/workflows/*.py` (skill-plugin discovery). Trace-matrix skill ships its own console workflow file. Neither skill imports from the other. Demo loop: run workflow → workflow shells to skill → section picks up new sidecars.
- 2026-04-15: Filter requirement added — Trace Matrix view must support filtering by criticality (CtS / CtF / CtC / CtP / Supporting / Untagged) plus layer and gap-only. Pure client-side JS toggling `display` based on row `data-criticality` / `data-layer` attributes; no fetch. Parser normalizes DI source values (`CTS`→CtS, `CTF`→CtF, `CTC`→CtC, `S`→Supporting). UNs are Untagged today (task 011 will add criticality to UNs). JSON sidecar carries `criticality` per item. Pass plan: Pass 1 = skill build engine + run against PP3500 (show JSON); Pass 2 = console section + workflow plugin + filters (show end-to-end).
- 2026-04-15: **Pass 1 complete.** Skill scaffolded at `.claude/skills/trace-matrix/` (SKILL.md + Best Practices + scripts/parsers/graph/emit). `trace-matrix.yml` written at repo root for PP3500. `python build.py` ran cleanly: 22 UNs (0 orphan), 34 DIs (4 with parseable VER ID — **30 DIs flagged as missing verification reference**, exactly the gap the matrix should reveal), 7 architecture modules (all orphan, edges-unknown banner), 3 derived V&V nodes, 0 hazards (risk source placeholder). Sidecar = 82 KB; markdown deliverable = 10 KB; both written atomically. Old hand-authored `un-to-di-trace-matrix.md` left untouched alongside the new `trace-matrix.md`.
- 2026-04-15: **Pass 2 architecture pivot** — the console has no Workflows section yet (`_base.html` says "Workflows (soon)"; no router). Skill-plugin workflow discovery requires that section to exist first. Pragmatic v1: add a **Rebuild button** directly on the Trace Matrix page that POSTs to a small endpoint shelling to `python .claude/skills/trace-matrix/scripts/build.py`. Same demo loop (click → build → page reloads with fresh sidecars), no dependency on a not-yet-built workflows section. Capture skill-plugin workflow discovery as **v2 follow-up** once the workflows section ships.
- 2026-04-15: **Pass 2 complete and verified in the browser.** Console restarted, chrome-devtools MCP confirmed `/trace-matrix` (200, pca-device card + 9 empty DHF cards) and `/trace-matrix/pca-device` (200, full layered view with stat strip, filter chips, expand panels). Only browser error is a pre-existing `manrope-latin.woff2` 404 (unrelated theme asset). **Design decision locked:** the Trace Matrix section owns its own build UI (Rebuild / Build-this-DHF buttons inline in the section). This is the v1 design, not a deferral — routing through a future Workflows section would be extra indirection for no gain. Skill-plugin workflow discovery is **dropped from this task entirely** (no longer a v2 follow-up for task 016).
- 2026-04-15: **Compatibility audit** surfaced 6 portability leaks (hardcoded column headers, single-source-file assumption, hardcoded file-path map in console doc-link, hardcoded `M\d+` regex, hardcoded `VER-*` regex, stale `risk.py` call) plus one doc drift (SKILL.md references a `console/workflows/` payload that was dropped in Pass 2). Sister project (Arthrex PCCP `hiplink-suite`) has materially different source shape: no populated `user-needs.md`, two SRS files `hiplink-web-srs.md` + `hiplink-intraop-srs.md`, "SRS" column terminology not "Design Inputs".
- 2026-04-15: **Pass 3 architecture decision — adapter generation, not richer config.** Instead of parameterizing every assumption in YAML (which only handles column renames), the skill ships **default parser adapters** plus an **LLM-powered `init` action** that: (a) reads each source doc, (b) runs a "rational check" — tries the default parser and validates the output — (c) when defaults fail, **generates a per-project Python adapter** tailored to that doc's exact shape, and (d) writes the generated file to `tools/project-console/trace-matrix/adapters/<layer>.py`. **Build is always deterministic** — adapters are imported by file presence; LLM runs only at init/regenerate. Generated adapters are committed, reviewable, and owned by the project, not the skill. Skill contract stays thin (`ParserResult` dataclass). Generated adapters live under `tools/project-console/trace-matrix/adapters/` per explicit user direction — "stored in the console".
- 2026-04-15: **Pass 3 complete.** Skill refactored: `adapter_api.py` with `ParserResult` + `rational_check` + `load_adapter`; five default parsers moved to `parsers/defaults/`; `build.py` uses the override/fallback resolver; `analyze.py` CLI implements the rational check; `emit.py` bumps sidecar to v1.1 adding `source_files` + `warnings` per layer; console `_doc_view_url` now reads `layer.source_files` instead of hardcoding paths; SKILL.md rewritten for the adapter model with the v2 version and updated Best Practices table (9 rules now); `tools/project-console/trace-matrix/README.md` documents the project-side adapter contract. All five default adapters on PDLC_DEMO pass the rational check — no generated adapters needed, all layers tagged `[deflt]`. Counts unchanged (22/34/7/3/0). Console restart confirmed `/trace-matrix` and `/trace-matrix/pca-device` render cleanly, sidecar v1.1 in the wire, first UN source_url resolves correctly. v6 portability leaks from the audit are all addressed.
- 2026-04-15: **Pass 4 — UI revision + SE Assistant.** Trace Matrix per-DHF view rebuilt iteratively based on live feedback:
  - Full-width table layout (no max-width corset); compact single-line header with Rebuild button; stat strip moved into tab labels; filters collapsed to one row.
  - **Tabs** replace the long scroll-through — one per layer (User Needs / Design Inputs / Architecture / V&V / Risk), counts + orphan/flag badges in the tab labels, only the active layer's table is visible.
  - **Folder-tab styling** — each tab is a bordered card with a gap, active tab visually docks into a framed panel below; inactive tabs have grey fill so they read as separate elements.
  - **Requirement column = full text**, no truncation.
  - **Row-level expand** (replaced per-column `<details>`): clicking anywhere in a row toggles all three expandable columns together. Caret (▸/▾) in the ID column rotates 90° on expand. Metadata panel renders in the Requirement column below the text (category, stakeholder, priority, source, acceptance, verification method, IEC class, module name, source-doc link). Forward column gets a labeled trace list on expand; reverse column same.
  - **Systems Engineering Assistant drawer** added next to Rebuild. Right-side slide-out, default 40vw, resizable via drag handle on the left edge (360–85vw range), width persisted to `localStorage["tm-assistant-width"]`. Multi-thread history stored under `localStorage["tm-chats-<dhf>"]` with thread dropdown, + New, and Clear history controls. Backend endpoint `POST /trace-matrix/{dhf}/chat/stream` builds a compact single-line-per-item rendition of the sidecar as system prompt and streams via `chat/sdk_client.stream_response()`. Stateless server — browser sends history with every request.
  - **Inline markdown renderer** (~90 lines of vanilla JS, no library) for assistant bubbles: headers, bold, italic, inline + fenced code, unordered/ordered lists, pipe tables, links. HTML-escaped first so LLM output can't inject raw tags. Runs on every streamed token so formatting emerges live. User bubbles stay plain text.
  - End-to-end validated via chrome-devtools MCP: real question ("Show the 3 alarm DIs as a markdown table…") produced a proper `<table class="tm-md-table">` with bordered cells, `<strong>` headline, and a grounded analysis of the V&V coverage gap. Prior question ("Which CtS DIs have no verification?") returned an exact enumeration of the 10 orphan safety-critical DIs.
- 2026-04-15: **Design docs updated.** `tools/project-console/ARCHITECTURE.md` now lists Trace Matrix as the fifth top-level section with full IA, routes, loose-coupling rules, layout tree, and changelog entries for Pass 2 + Pass 4. `.claude/skills/trace-matrix/SKILL.md` is current at v2 from Pass 3 (adapter model, 9 Best Practices rules, Changelog). `tools/project-console/trace-matrix/README.md` documents the project-side adapter contract.
