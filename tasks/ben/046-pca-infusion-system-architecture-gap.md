# 046 — PCA Infusion System filing-entity + multi-function device architecture/regulatory gap

**ID**: 046
**Created**: 2026-05-06
**Status**: Not Started — captured during ben/045 trace-matrix recovery, deferred for proper scoping
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High (architecturally load-bearing for the filing)

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a decision, a converted/adopted doc, a committed change, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision)
   - update any progress counts/tables in Goals
2. **Phase-end batching is OK; drift-batching is not.** Write at phase boundaries before the next phase starts.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative.
4. **Resume-ready before any session boundary.** Doc must contain: (a) what was done with concrete artifacts, (b) status of in-flight work, (c) priority-ordered next steps with file paths, (d) open questions, (e) the exact `/task` activation command.
5. **Capture strategy + lessons as they happen** with `<!-- STRATEGY CONTENT: ... -->` and `<!-- LESSONS LEARNED: ... -->` blocks.

Resume command:
```bash
bash .claude/hooks/task-activate.sh add <SESSION_UUID> 046
```

---

## Origin

Surfaced during ben/045 (trace-matrix view recovery), 2026-05-06. While reviewing the per-DHF trace-matrix layer mapping, the user identified that the project's DHF set is missing the **top-level filing entity** and that several component-level architecture documents are misnamed and mislocated. This is a structural gap, not a trace-matrix-tool gap — the trace-matrix view will render whatever it's pointed at; the underlying DHF / architecture / regulatory-strategy story is what's incomplete.

ben/045 captures this only as Phase-4 follow-up bullets; deeper work belongs here.

## Goals

Establish the correct top-level filing structure and the architecture / regulatory artifacts that go with it.

- **G1.** Create the **PCA Infusion System** as a new top-level DHF (the filing entity for the 510(k)). Houses the single **system architecture** (system SAD).
- **G2.** Restructure `project.yml dhfs[]` so that **PCA Infusion System** is the parent of the three current top-level DHFs:
  - `pca-device` (Medical Device, class II)
  - `connectivity-adapter` (MDDS)
  - `cloud-suite` (non-medical container; itself parent of 7 cloud-item DHFs)
- **G3.** Author / locate the **system SAD** under PCA Infusion System (currently no doc owns the system-level architecture).
- **G4.** Rename and relocate component-level "*-system-sad.md" docs to **software SADs** at the component level (their actual scope). Today: `pca-device-system-sad.md`, `connectivity-adapter-system-sad.md`, `drug-library-manager-system-sad.md` are all named "system" but are component-scoped.
- **G5.** Update the **regulatory strategy** to reflect a multi-function device with three classifications (Medical Device / MDDS / non-medical) under one filing.
- **G6.** Sweep downstream artifacts that key off DHF identity: `trace-matrix.yml`, `dhf-manifest`, `tracker`, console index, submission tracker.

## Current state (as recorded in `project.yml`, 2026-05-06)

3 top-level DHFs, no parent above them:

| DHF | role | parent | classification | filing |
|---|---|---|---|---|
| `pca-device` | system | null | class II medical, 62304 C | 510k |
| `connectivity-adapter` | item | null | MDDS, samd, class II, 62304 B | 510k |
| `cloud-suite` | system | null | mixed regulatory; composes 7 children | (null) |

`project.yml scope.multi_function_device: true` is set, but no top-level filing entity composes the three above.

## Target state

```
PCA Infusion System  (NEW top-level DHF — filing entity)
│   • Owns the single SYSTEM SAD
│   • Owns the multi-function-device regulatory strategy
│   • role: system, parent: null, composes: [pca-device, connectivity-adapter, cloud-suite]
│   • filing: 510k
│
├── pca-device              (Medical Device, class II) — software SAD
├── connectivity-adapter    (MDDS)                    — software SAD
└── cloud-suite             (non-medical; mixed)      — software SAD (or none — TBD)
    ├── drug-library-manager  (samd, class II)        — software SAD
    ├── alerts-engine         (samd, class II)        — software SAD
    ├── clinical-interface    ...
    ├── inventory-tracker     ...
    ├── fleet-management      ...
    ├── compliance-reports    ...
    └── analytics-dashboard   ...
```

## Open Questions (for scoping pass)

1. **Where does PCA Infusion System live on disk?** Candidates:
   - `docs/project/dhfs/pca-infusion-system/` as a new top-level DHF folder, with the existing 3 DHFs **moved** under it (mirroring `cloud-suite/dhfs/<child>/` pattern)
   - `docs/project/dhfs/pca-infusion-system/` as a new sibling that *references* the existing 3 (composition without physical re-parenting)
   - The latter is less disruptive; the former is cleaner. Decision affects every existing path in `trace-matrix.yml`, `dhf-manifest`, `tracker`, etc.
2. **Where does the system SAD content come from?** Author from scratch, or harvest from the existing `pca-device-system-sad.md` (which conflates system + component scope today)?
3. **Component SAD renames** — do we rename files (`<dhf>-system-sad.md` → `<dhf>-software-sad.md`) or leave names alone and only fix the labeling inside? Renaming has cascade effects through `trace-matrix.yml`, the trace-matrix builder's path conventions, and any external links.
4. **Regulatory strategy doc** — already present at `docs/project/regulatory-strategy/` (or wherever)? Needs an update vs. a new doc?
5. **Order of operations** — which dominoes to tip first? Suggest: regulatory strategy → top-level DHF skeleton → system SAD draft → project.yml restructure → downstream sweep. Each is a phase.

## Plan (high-level — to be refined in a scoping pass)

### Phase 1 — Scoping & alignment
- [ ] Walk the open questions above with the user; lock answers.
- [ ] Inventory every artifact that keys off DHF identity (`trace-matrix.yml`, `dhf-manifest` per-DHF outputs, `tracker` lifecycle data, `submission-tracker.html`, console index, any cross-DHF README references).
- [ ] Check sister project `../arthrex-pccp/` for analogous structure — does it already model a top-level filing entity over component DHFs? (Per standing rule: validate skill changes / structural changes against the sister project.)

### Phase 2 — Regulatory strategy
- [ ] Update / author regulatory strategy doc reflecting multi-function device with 3 classifications under one filing.
- [ ] Cross-link to FDA guidance on multi-function device products (FDA 2020 guidance) and 21 CFR 880 / 870 as applicable.
- [ ] Verify with `regulatory-affairs` agent before structural changes ripple downstream.

### Phase 3 — Top-level DHF skeleton
- [ ] Scaffold `docs/project/dhfs/pca-infusion-system/` (or chosen path) using `medtech-docs` skill.
- [ ] Add `pca-infusion-system` entry to `project.yml dhfs[]` with `role: system`, `composes: [pca-device, connectivity-adapter, cloud-suite]`.
- [ ] Update `parent:` fields on the three child DHFs to point to `pca-infusion-system`.

### Phase 4 — System SAD (vs. component software SADs)
- [ ] Author / harvest the **system SAD** under PCA Infusion System.
- [ ] Rename / relabel component "*-system-sad.md" → "*-software-sad.md" with appropriate scope statement at the top of each.
- [ ] Update `trace-matrix.yml` architecture-layer source paths to match.

### Phase 5 — Downstream sweep
- [ ] Re-run `/trace-matrix init` (or hand-edit `trace-matrix.yml`) to add the new DHF and adjust paths.
- [ ] Re-run `/dhf-manifest` to refresh manifests for all DHFs (parent / role changes affect manifest content).
- [ ] Re-run `/tracker` to refresh the submission tracker.
- [ ] Console index check — confirm `/trace-matrix` index lists the new DHF correctly and the existing three render with the new parent annotation.
- [ ] Sister-project compatibility check at `../arthrex-pccp/`.

### Phase 6 — Commit
- [ ] One commit (or a small phase-bounded series) with the structural change.
- [ ] No `/sync-skills push` — this is a project-content change, not a skill change.

## Strategy & Lessons (real-time capture)

<!-- STRATEGY CONTENT: regulatory, architecture -->
**Decision (proposed, pending Phase-1 sign-off):** Treat the PCA Infusion System as the filing-level entity that owns the **single system architecture** and the **multi-function-device regulatory strategy**. The three current top-level DHFs (`pca-device`, `connectivity-adapter`, `cloud-suite`) become its components. This re-parents the DHF tree but does not invalidate any existing component content.
**Why:** A 510(k) for a multi-function device needs one **system** view that ties medical / MDDS / non-medical components into a single device of record. Today the three "top-level" DHFs each carry their own "*-system-sad.md" — that nomenclature conflates system and component scope, which an FDA reviewer would flag. The single point of truth for system architecture must live above the components.
**How to apply:** When editing any architecture, regulatory-strategy, or DHF-manifest artifact, ensure the system-level statement lives at the **PCA Infusion System** layer, and component-scope statements live at the **component DHF** layer. Don't push system-level claims down into component SADs.
<!-- /STRATEGY CONTENT -->

<!-- STRATEGY CONTENT: development, scope-discipline -->
**Decision:** Defer this restructuring out of ben/045 (trace-matrix recovery) and into this dedicated task. ben/045 stays surgical — restore the trace-matrix view against the existing DHF set. This restructuring is much larger and has its own regulatory + architecture dependencies.
**Why:** Mixing structural restructuring into a tooling-recovery task would (a) bloat 045 well past its scope, (b) couple two unrelated review surfaces (tooling fix vs. regulatory architecture), and (c) push the trace-matrix view fix off until the larger story lands. Two separable scopes → two tasks.
**How to apply:** When a structural gap is discovered during recovery work, capture it as its own task immediately and keep the recovery surgical. Don't widen scope mid-recovery.
<!-- /STRATEGY CONTENT -->

## Changelog

- 2026-05-06: Task created. Captures structural gap surfaced during ben/045 trace-matrix recovery work — namely (a) missing top-level "PCA Infusion System" filing entity, (b) the single system SAD has no home, (c) component "*-system-sad.md" docs are misnamed (they are software SADs by scope), (d) multi-function device regulatory strategy needs to be authored / updated. Phase 1 scoping not yet started; ben/045 trace-matrix recovery resumes ahead of this task.

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 2,
    "todos": [
      {
        "todo": "PCA filing-entity architecture gap (planning)",
        "personas": [
          "systems-engineering",
          "regulatory-affairs"
        ],
        "manual_hours": {
          "min": 2,
          "max": 5
        },
        "confidence": "low",
        "basis": "not started \u2014 captured plan + open questions"
      }
    ]
  }
}
```
