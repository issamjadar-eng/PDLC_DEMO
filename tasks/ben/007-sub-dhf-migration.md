# 007 — Medtech-docs Topology Support (Single-DHF, Multi-Sub-DHF)

**ID**: 007
**Created**: 2026-04-13
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## Goals

_Evolve the `medtech-docs` skill from a single-DHF scaffolder into a topology-aware scaffolder that can be reused across MedTech projects with different product shapes. PDLC_DEMO is the first consumer and test case — but the work is the skill, not the project-specific migration._

- Introduce an explicit **project topology** concept into the skill: at minimum `single-dhf` and `multi-sub-dhf`; extensible for future topologies
- Codify the **shared-vs-per-DHF** split as a skill convention, not an ad-hoc project decision
- Update `/medtech-docs init` to prompt for topology and scaffold accordingly
- Add a new `/medtech-docs add-sub-dhf <name>` action that scaffolds a new sub-DHF into an existing multi-DHF project
- Provide a **migration path** from an already-initialized single-DHF project to a multi-sub-DHF project (PDLC_DEMO is the first to use it)
- Update `medtech-docs` best-practices checks to be topology-aware
- Update the skill's README + SKILL.md to document topology as a first-class concept
- PDLC_DEMO migration runs as a downstream execution of the upgraded skill, not as bespoke file moves

## Architectural Pivot — unified shape (2026-04-13, supersedes dual-topology design below)

**Decision**: Drop the dual-topology model entirely. Every MedTech project scaffolded by `medtech-docs` uses **one shape**: `docs/project/dhfs/<primary>/...` — from day one, even if the project has only one sub-DHF. Growth from N=1 to N>1 is a plain `add-sub-dhf` call with no migration, no cross-link sweep, no topology flip. There is no `project.topology` field. There is no `single-dhf` vs `multi-sub-dhf` distinction. Single is just multi with N=1.

### Why the pivot

The original task 007 spent most of its design surface (P1 topology model, P2 `migrate-to-multi-dhf`, P3–P5 consuming-skill mode branching, ambiguities 1/2/4/9) on supporting two shapes and the migration between them. On review, every piece of that complexity traces back to three wrong assumptions:

| Assumption | Reality |
|---|---|
| "Small projects shouldn't carry the `dhfs/<name>/` overhead." | Two extra path segments. Trivial cost. |
| "Existing flat-shape projects must be migrate-able without forcing a reorg." | The set of existing flat-shape projects is exactly one (PDLC_DEMO), and that reorg is a one-time task-007 step either way — not a skill feature. |
| "Single-dhf and multi-sub-dhf are fundamentally different shapes." | Single is multi with N=1. Treating them differently created every major P5 ambiguity. |

### The unified shape

```
docs/project/
├── external/                   (shared)
├── internal/                   (shared)
├── input-analysis/             (shared)
├── strategies/                 (shared — commercial, operations)
├── dhfs/
│   └── <primary>/              always at least one entry; `sub_dhfs[]` in project.yml is single source of truth
│       ├── README.md
│       ├── design-controls/
│       ├── clinical/
│       ├── postmarket/
│       ├── risk-management/
│       └── cybersecurity/
└── submissions/                (shared; composition manifests reference dhfs/*)
```

Multi-component projects just have more entries under `dhfs/`, optionally with nested `dhfs/` folders inside a parent sub-DHF (recursion is unchanged from the earlier design; cap of 2 levels at init time is unchanged). `project.yml` has a `sub_dhfs[]` list; one entry for simple projects, many for ecosystems.

### Init-time naming (decision: option 1)

`/medtech-docs init` prompts **"short name for your primary sub-DHF (e.g., pca-device, ecg-monitor)"** with **no default**. The user must name it. Rationale: forces intentional naming at init so the team thinks of their product as a component in a potential ecosystem from day one, which is the mental model the unified shape is meant to teach. Renames later are handled as a manual `git mv` + link-sweep (future follow-up: a dedicated `rename-sub-dhf` skill action).

### What this invalidates in the rest of task 007

The sections below — "Why this shape" (original dual-topology rationale), "Topology model (proposed)", P2 `init --topology` / `migrate-to-multi-dhf`, P3/P4/P5 mode branching, ambiguity #2 — were written against the dual-topology design. They are **retained for historical context** so the reasoning trail stays visible, but are **superseded**. Each now-moot section should be understood as "we considered this, and the pivot eliminated it."

| Section | Status under pivot |
|---|---|
| "Why this shape" (below) | Historical rationale for the original dual-topology scope. Superseded. |
| "Topology model (proposed)" table | Moot — there is only one topology. The shared-vs-per-DHF split and recursive `dhfs/` shape are still correct and carry forward. |
| P2.1 `init --topology` flow | Moot — init always creates `dhfs/<primary>/`. No `--topology` flag. |
| P2.3 `migrate-to-multi-dhf` action | **Deleted.** No migration action in the new shape. The PDLC_DEMO one-time reorg becomes a P6 execution step, not a skill feature. |
| P2.4 Post-migration validator | Deleted — no migration, no validator. |
| P2.7 Dry-run gate for PDLC_DEMO | Deleted as a skill feature; becomes a manual reviewer checklist for P6's one-time reorg. |
| P3 `/strategy` topology awareness | Simplified — no mode branching. `/strategy` always writes to `dhfs/<name>/design-controls/plans/`. Domain registry, tag conventions, scan/assemble changes all stay. |
| P4 `/tracker` topology awareness | Simplified — no mode branching. Always reads `dhfs/<name>/...`. Composition-manifest-as-source-of-truth stays. |
| P5 `/best-practices` topology awareness | Simplified — per-dhf checks always iterate `sub_dhfs[]`. Scope column stays. Subagent dispatch (P5.5a) stays and runs uniformly — the `if multi-sub-dhf then fan out` branch disappears. N=1 optimization (skip subagent spawn when `sub_dhfs[]` has one entry) is a pure performance knob, not semantic. |
| Ambiguity #2 (per-dhf behavior in single-dhf mode) | **Moot.** Per-dhf checks always iterate `sub_dhfs[]`; there is no "flat layout" to run against. |
| Ambiguities #1, #3, #4, #5, #6, #7, #8, #9 | Still valid. |
| P6 (PDLC_DEMO live-fire) | Reshaped — becomes a one-time reorg of PDLC_DEMO's current flat shape into `dhfs/pca-device/`, followed by `add-sub-dhf` calls for the other components. No `migrate-to-multi-dhf` action to invoke. Prereq 1 (atomic `project.yml` write) is moot because there is no `topology` field to flip. Prereqs 2/3/4 still apply. |

### What the pivot costs

- Every project has `dhfs/<primary>/` — two path segments deeper than the old flat shape for single-component projects.
- Init requires naming the primary component (no default; friction ≈ 5 seconds).
- PDLC_DEMO still needs its one-time reorg from the existing flat shape into `dhfs/pca-device/`. This happens once, in P6, as a manual `git mv` + link-sweep. It is not a generalizable skill feature because no future project will ever be in the flat shape.

### What stays from the original design

- The shared-vs-per-DHF content rule (external/internal/input-analysis/strategies/submissions are shared; design-controls/clinical/postmarket/risk-management/cybersecurity are per-DHF).
- Recursive `dhfs/` nesting for platform+child sub-DHFs, with the 2-level init-time cap.
- `add-sub-dhf <name> [--parent <path>]` action.
- `project.yml` `sub_dhfs[]` schema with `path`, `regulatory`, `filing`, `parent` fields.
- Composition manifest as the source of truth for submissions (P4.2).
- Subagent dispatch model for per-sub-DHF and per-submission checks (P5.5a).
- All sign-offs on ambiguities #1, #3–#9.
- All resolved P3 prerequisites (Q1/Q2/Q3).

## Why this shape

_Historical — this section describes the rationale for the **original** dual-topology design. Superseded by the Architectural Pivot above. Retained for reasoning trail._

The first version of task 007 was scoped as a one-off migration of PDLC_DEMO into `dhfs/pca-device/`. User correction (2026-04-13): _"The task needs to be about how we build the medtech-doc in a way that can be used repeated, by different structures."_ The migration is a consequence of the skill gap; the real work is closing the skill gap so the next project doesn't need the same bespoke migration.

## Topology model (proposed)

### Supported topologies (v1)

| Topology | When to use | Scaffold shape |
|---|---|---|
| **`single-dhf`** | One product, one DHF, one primary filing path. Small devices, SaMD-only products, early-stage projects. | Current shape: `docs/project/{design-controls, clinical, postmarket, submissions, input-analysis, external, internal}/` |
| **`multi-sub-dhf`** | Product ecosystem where multiple components have separate regulatory paths (device + adapter + cloud suite). Filings compose from sub-DHFs. | New shape: `docs/project/dhfs/<component>/{design-controls, clinical, postmarket, cybersecurity, risk-management}/` + shared `{input-analysis, external, internal}/` + top-level `submissions/` with composition manifests |

Future topologies to leave room for (not v1): `platform-plus-apps` (one shared platform DHF + N app sub-DHFs inheriting from it), `combination-product` (drug + device + SW split).

### Shared-vs-per-DHF rule (codified)

| Content | Location | Reasoning |
|---|---|---|
| `external/` (FDA guidance, standards, frameworks) | **Shared** | Upstream truth, not tied to any one product |
| `internal/` (corp SOPs, templates) | **Shared** | Corporate-level, applies to all products |
| `input-analysis/` (KOL, market, competitive, predicate analysis) | **Shared** | Customer intelligence spans the whole portfolio |
| `design-controls/` | **Per-DHF** | User needs, requirements, architecture, trace matrix are component-specific |
| `clinical/` | **Per-DHF** | Clinical evaluation is tied to the specific device and indication |
| `postmarket/` | **Per-DHF** | PMS, PMCF, CAPA, complaints are per-component |
| `risk-management/` | **Per-DHF** | ISO 14971 hazard analysis is per-device |
| `cybersecurity/` | **Per-DHF** | IEC 81001-5-1 assessment is per-component (but cross-linked between them at filing time) |
| `submissions/` | **Top-level** | Filings are shared scaffolding; each filing's composition manifest lists which sub-DHF pieces it pulls in |

### Multi-sub-DHF scaffold shape (target for PDLC_DEMO and future projects)

**Rule: recursive `dhfs/`**. Any sub-DHF can contain its own nested `dhfs/` folder for children. A sub-DHF is **first and foremost a sub-DHF in its own right** — it has its own design-controls, risk-management, cybersecurity, etc. A parent sub-DHF with children is a platform that hosts child sub-DHFs; the parent's content describes the platform, the children describe hosted components.

```
docs/project/
├── external/                                 (shared)
├── internal/                                 (shared)
├── input-analysis/                           (shared)
├── strategies/                               (shared cross-cutting strategies — commercial, operations)
├── dhfs/
│   ├── <sub-dhf-1>/                          e.g., pca-device
│   │   ├── README.md
│   │   ├── design-controls/                  (user-needs, requirements, architecture, trace-matrix, plans, vnv, tool-validation)
│   │   ├── clinical/                         (evaluation-plans, benefit-risk, literature-search)
│   │   ├── postmarket/                       (pmcf-plans, pmcf-studies, capa, complaints)
│   │   ├── risk-management/
│   │   └── cybersecurity/
│   ├── <sub-dhf-2>/                          e.g., connectivity-adapter (leaf sub-DHF, no children)
│   │   └── (same structure, some folders optional)
│   └── <parent-sub-dhf>/                     e.g., cloud-suite (platform + children)
│       ├── README.md
│       ├── design-controls/                  ← platform-level design controls
│       │   └── architecture/                 ← the platform/system architecture doc
│       ├── risk-management/                  ← platform-wide hazards
│       ├── cybersecurity/                    ← shared platform security posture
│       └── dhfs/                             ← nested sub-DHF container
│           ├── <child-1>/                    e.g., drug-library-manager
│           │   ├── design-controls/
│           │   ├── risk-management/
│           │   └── cybersecurity/
│           └── <child-2>/                    e.g., fleet-management
└── submissions/
    ├── README.md
    └── <filing>/
        ├── composition-manifest.md           ← lists which dhfs/*/... pieces are in this filing
        └── ...
```

**Recursion depth is unbounded in the data model, capped at 2 levels in the v1 UI (2026-04-13 decision).** A child can itself have `dhfs/` for grandchildren. In practice, two levels deep (top-level + one nested level) covers the platform-plus-apps pattern including PDLC_DEMO's cloud-suite.

- `/medtech-docs init --topology multi-sub-dhf` prompts for top-level sub-DHFs, and for each, optionally prompts for its children — but stops there. No grandchildren in the interactive init flow.
- `/medtech-docs add-sub-dhf` accepts any `--parent <path>` depth, including nested paths like `cloud-suite/dhfs/drug-library-manager`, so deeper hierarchies are still reachable — just not at init time.
- When a user asks about depth > 2 during init, the skill responds with: _"v1 init supports 2 levels of sub-DHF nesting. For deeper structures, complete init with 2 levels and then run `/medtech-docs add-sub-dhf <name> --parent <path>` to add grandchildren."_

**Why the cap**: depth > 2 is rare, and interactive init prompts get hard to reason about beyond 2 levels. Keeping init simple while leaving the underlying model open means we don't have to re-architect when someone eventually needs 3 levels.

**Key rule for distinguishing platform content from children**: at any sub-DHF level, platform content lives in the per-DHF folders (`design-controls/`, `clinical/`, `postmarket/`, `risk-management/`, `cybersecurity/`). Child sub-DHFs live under a dedicated `dhfs/` folder. There is no naming collision because `dhfs/` is never also a per-DHF folder name.

**Implication for `add-sub-dhf`**: the action takes a `--parent <path>` argument (path relative to `docs/project/dhfs/`), not a `--parent <name>`. This supports nesting at any depth.

```
# Add a top-level sub-DHF
/medtech-docs add-sub-dhf pca-device

# Add a child of cloud-suite
/medtech-docs add-sub-dhf drug-library-manager --parent cloud-suite

# Add a grandchild (hypothetical)
/medtech-docs add-sub-dhf some-module --parent cloud-suite/dhfs/drug-library-manager
```

**Implication for `project.yml`**: the `sub_dhfs:` manifest uses **`path`** (relative to `docs/project/dhfs/`), not just `name`. Path encodes the full location including parent chain:

```yaml
sub_dhfs:
  - path: pca-device
    regulatory: cleared
    filing: K210345
  - path: connectivity-adapter
    regulatory: in-development
  - path: cloud-suite
    regulatory: mixed                        # platform itself has MDDS + non-device mix
  - path: cloud-suite/dhfs/drug-library-manager
    regulatory: in-development               # SaMD child
  - path: cloud-suite/dhfs/fleet-management
    regulatory: in-development               # likely MDDS
  # ... etc ...
```

Skills that want to walk the tree can do so via `project.yml` alone, without glob-scanning the filesystem.

## Skill changes required

### `medtech-docs` SKILL.md updates

- Add a **"Project Topology"** section before the init-action spec, describing the two topologies and the shared-vs-per-DHF rule
- Update the `init` action to accept a `--topology <single-dhf|multi-sub-dhf>` flag, defaulting to `single-dhf` for backward compatibility
- When `--topology multi-sub-dhf`, `init` prompts for the first sub-DHF name and scaffolds it into `dhfs/<name>/`
- Add new action `add-sub-dhf <name> [--parent <parent-name>]` that scaffolds a new sub-DHF in an existing multi-DHF project
  - Without `--parent`: creates a top-level sub-DHF under `dhfs/<name>/`
  - With `--parent`: creates a nested sub-DHF under `dhfs/<parent>/<name>/`
- Add new action `migrate-to-multi-dhf <first-sub-dhf-name>` that moves a single-DHF project's per-DHF content into `dhfs/<first-sub-dhf-name>/` and sweeps internal cross-links
  - This is the action PDLC_DEMO will use to migrate PP3500's existing content
- Update `dashboard` and `status` actions to be topology-aware (rollup per sub-DHF)

### `medtech-docs` README.md updates

- New "Project Topology" section up front explaining the two topologies with diagrams
- Update any single-DHF assumptions in existing docs

### Templates to add or refactor

- Per-sub-DHF README template (new)
- Composition-manifest template for submissions (new)
- Shared-root README template updates (mention that `dhfs/` exists in multi-DHF mode)

### Best-practices checks

- Detect project topology by presence/absence of `docs/project/dhfs/`
- If single-DHF: run existing checks as-is
- If multi-sub-dhf: run checks **per sub-DHF** and roll up, plus verify every `submissions/<filing>/` has a `composition-manifest.md`

## Todos

_Rewritten 2026-04-13 after the Architectural Pivot to the unified shape. Historical Todos for the dual-topology design are captured in git history of this file if needed._

**Design phase (mostly complete, reviewed under unified shape):**
- [x] Confirm shape — unified `dhfs/<primary>/...` for all projects, no topology branching. _Signed off 2026-04-13._
- [x] Shared-vs-per-DHF content rule. _Carries forward from original design._
- [x] Sign off all 9 P5 ambiguities (one marked moot under the pivot).
- [x] Resolve P3 prerequisites Q1/Q2/Q3.
- [x] Design subagent dispatch model (P5.5a).
- [ ] Close out remaining P6 prerequisites (baseline audit, stub composition manifest, Scope-column rollout sequencing).
- [ ] Define Phase P6 (PDLC_DEMO one-time reorg + add-sub-dhf sequence) as a concrete execution plan.

**Implementation phase (not yet started):**
- [ ] Update `medtech-docs` SKILL.md: remove any `--topology` flag, remove `migrate-to-multi-dhf` action spec, specify unified `init` flow (prompts for primary sub-DHF name with no default), specify `add-sub-dhf` action.
- [ ] Add per-sub-DHF README template and composition-manifest template to `.claude/skills/medtech-docs/templates/`.
- [ ] Update `medtech-docs` best-practices checks to reflect the unified shape (no dual-mode branching).
- [ ] Update `/strategy` SKILL.md: always write to `dhfs/<name>/design-controls/plans/`; implement tag-scope resolution per P3 Q1; update scan/assemble per P3.3/P3.4.
- [ ] Update `/tracker` SKILL.md: always read `dhfs/<name>/...`; implement composition-manifest-as-source-of-truth per P4.2; plan-time composition manifest read per P3 Q2.
- [ ] Update `/best-practices` SKILL.md: add Scope column to check table schema per P5.7; implement subagent dispatch per P5.5a (two pools, parent dispatcher, error isolation); implement stale-manifest and unreferenced-sub-DHF checks; implement git-then-fs mtime resolution; implement stale-ack comment parser (bare + files-scoped).
- [ ] Add `Scope` column to every consuming skill's Best Practices table (`task/`, `medtech-docs/`, `strategy/`, `tracker/`, `docflow/`) — sequencing decision pending (P6 prereq 4).
- [ ] Run pre-reorg baseline `/best-practices audit` of PDLC_DEMO (P6 prereq 2).
- [ ] Execute PDLC_DEMO one-time reorg: `git mv` current flat layout into `dhfs/pca-device/`, sweep cross-links, update `project.yml` `sub_dhfs[]`, commit atomically.
- [ ] Run `add-sub-dhf connectivity-adapter`, `add-sub-dhf cloud-suite`, and nested `add-sub-dhf <app> --parent cloud-suite` for each cloud-suite child.
- [ ] Update PDLC_DEMO's cross-links, strategy briefs, and task 001 changelog to reflect the new shape.
- [ ] Seed at least one stub composition manifest for the primary 510(k) filing (P6 prereq 3).
- [ ] Post-reorg `/best-practices audit` against the new shape; diff against the baseline; fix regressions.
- [ ] Unblock task 006 — architecture & regulatory strategy content resumes authoring into `dhfs/pca-device/design-controls/plans/`.
- [ ] Capture lessons learned from the reorg (what the link-sweep missed, how the subagent dispatch performed on a real project, any surprises).
- [ ] Upstream PR to the hitachi skill registry so other projects inherit the unified-shape design.

## Evolution path — single-dhf → multi-sub-dhf

This is the most important capability the skill has to get right. A team can reasonably start a project in `single-dhf` mode (because that's what they understood they needed) and only later discover they have a multi-component ecosystem. The skill must support graceful, low-friction evolution from single-dhf into multi-sub-dhf **without requiring the team to know up front**. PDLC_DEMO itself is the canonical example.

### Requirements for the evolution path

1. **Detection & recommendation.** The skill should be able to tell a team _"you look like you're outgrowing single-dhf"_ rather than making them realize it on their own. Candidate signals:
   - `project.yml` now lists multiple products or multiple 510(k) numbers
   - Tasks mention multiple device IDs across different product lines
   - The project has accumulated SaMD components that are clearly distinct from the primary device
   - Files exist that describe "adapter", "cloud", "platform", or other cross-component infrastructure
   
   Implemented as a new check: `/medtech-docs check-topology` reports current topology, inferred topology from signals, and the delta. Non-destructive; just advice.

2. **One-way migration via a skill action, not manual file moves.** `/medtech-docs migrate-to-multi-dhf <first-sub-dhf-name>` performs the full migration. Must be:
   - **Dry-run first (required).** Default behavior is plan-only — prints the file-move plan, the cross-link rewrites that will happen, and the estimated blast radius. Requires explicit `--apply` flag to actually move files.
   - **Idempotent under re-run.** If the project is already multi-dhf, `migrate-to-multi-dhf` detects that and is a no-op (or adds only the missing pieces).
   - **Cross-link aware.** The skill rewrites internal markdown links that cross the `design-controls/`, `clinical/`, `postmarket/`, `risk-management/`, `cybersecurity/` boundaries. Relative paths deepen by one `../` layer as those folders move into `dhfs/<name>/`.
   - **Preserves history.** Uses `git mv` internally so git history follows each file; fails loudly if the project isn't a git repo.
   - **Updates `project.yml`** — sets `project.topology: multi-sub-dhf` and records the first sub-DHF name.
   - **Updates consuming skills** where their config is known — e.g., `/strategy` output paths currently hardcoded to `design-controls/plans/` need to become `dhfs/<name>/design-controls/plans/`. The skill either edits the strategy registry in place or emits a checklist of follow-ups for the team.
   - **Writes a migration report** to `docs/project/dhfs/<name>/README.md` describing what was moved, from where, and when.

3. **Partial-migration safety.** If the migration fails mid-way (filesystem error, git conflict), the action must leave the project in a recoverable state. Options: wrap the whole operation in a single git commit at the end; or checkpoint with intermediate commits that can be reverted.

4. **Post-migration "add the rest".** After the initial migration, the team uses `/medtech-docs add-sub-dhf` to add the other sub-DHFs one at a time. For PDLC_DEMO: first migrate PP3500 into `dhfs/pca-device/`, then `add-sub-dhf connectivity-adapter`, then `add-sub-dhf cloud-suite` + 7 `add-sub-dhf <app> --parent cloud-suite` calls.

5. **Back-compat for consuming skills.** Other skills (`/strategy`, `/tracker`, `/best-practices`, `/task`) read paths that the migration changes. Options:
   - **Skill-level topology read.** Skills consult `project.yml` `topology` field and adapt path resolution automatically. Cleanest long-term; biggest one-time effort.
   - **Per-skill path config.** Each skill accepts a path override; migration emits a checklist of overrides to set.
   - **Symlink fallback.** Not recommended — confusing and breaks on some filesystems.
   
   Recommendation: **topology read from `project.yml`** as the target, with per-skill path overrides as a short-term bridge if time is tight.

6. **Documentation & user flow.** The skill's README should make the evolution path obvious:
   - "Start with `init --topology single-dhf` (default) if you have one product."
   - "If your project grows into multiple components with separate regulatory paths, run `check-topology` to confirm the need, then `migrate-to-multi-dhf <first-component-name>` to evolve."
   - "Add more sub-DHFs over time with `add-sub-dhf`."

### Can the skill handle it? — Answer

**Yes, if `migrate-to-multi-dhf` is built to the spec above.** The hard parts are (a) cross-link sweeping, (b) updating consuming skills' hardcoded paths, and (c) dry-run safety. All three are solvable in one skill action.

**Risk**: cross-link sweeping is the single highest-risk piece — if the regex/link-rewriter misses a link or mangles one, users debug a broken DHF. Mitigation: mandatory dry-run showing every proposed rewrite, and a post-migration validator that scans for broken relative links.

**PDLC_DEMO as the live fire test.** PDLC_DEMO has non-trivial cross-link density (UN ↔ DI ↔ trace matrix ↔ CAPA ↔ predicate ↔ KOL references, plus 10 READMEs with cross-folder pointers, plus 25 clinical MDs with frontmatter and synthesized postmarket docs). If `migrate-to-multi-dhf` survives PDLC_DEMO, it's production-ready.

## Cross-Skill Topology Awareness (in scope for this task)

<!-- STRATEGY CONTENT: operations, skill-design, topology, migration -->

### Decision: all consuming skills become topology-aware in task 007

**Decision**: The four skills that read project-scoped paths — `/strategy`, `/tracker`, `/best-practices`, `/task` — will be updated **as part of task 007**, not as a follow-up. The migration action is not considered done until every consuming skill handles both `single-dhf` and `multi-sub-dhf` topologies correctly.

**Why**: A half-migrated ecosystem where the folder structure is multi-sub-DHF but `/strategy assemble` writes to the wrong (pre-migration) path, or `/best-practices` audits a nonexistent `docs/project/design-controls/` — is worse than no migration at all. Partial readiness becomes silent breakage the team debugs later. Folding the skill updates into the same task guarantees a coherent cutover.

**How to apply**: Task 007's "Done" definition includes the skill updates below. No skill is allowed to keep hardcoded `docs/project/design-controls/...` paths after this task completes.

### Per-skill updates required

| Skill | What reads a project path today | Topology-aware behavior |
|---|---|---|
| **`medtech-docs`** | `init` writes to `docs/project/{design-controls,clinical,postmarket,...}/` | Branches on topology; in multi-sub-dhf mode writes under `docs/project/dhfs/<name>/`. Also gains `check-topology`, `add-sub-dhf`, `migrate-to-multi-dhf` actions. |
| **`strategy`** | SKILL.md domain registry hardcodes output paths like `docs/project/design-controls/plans/regulatory-strategy.md` | Reads `project.topology` from `project.yml`. In multi-sub-dhf mode, each sub-DHF gets its own strategy instance (e.g., `dhfs/pca-device/design-controls/plans/regulatory-strategy.md`). Scope tag in strategy content tags (`<!-- STRATEGY CONTENT: regulatory, sub-dhf=pca-device, ... -->`) routes content to the correct sub-DHF's strategy doc. Shared `external/internal/input-analysis` stay at the top level. |
| **`tracker`** | Renders dashboards from folder trees under `docs/project/` | In multi-sub-dhf mode, renders one dashboard per sub-DHF plus a roll-up across sub-DHFs. Composition manifests in `submissions/` show which sub-DHF pieces are in each filing. |
| **`best-practices`** | Audits well-known paths; current checks assume single-dhf | Reads topology from `project.yml`. In multi-sub-dhf mode, runs per-DHF checks and rolls up; verifies every `submissions/<filing>/` has a `composition-manifest.md`. |
| **`task`** | Does not read project-scoped paths directly | No changes required, but task template may gain an optional `sub-dhf:` field for tagging which sub-DHF a task targets. |

### `project.yml` additions

To support topology-aware skills:

```yaml
project:
  # ... existing fields ...
  topology: multi-sub-dhf          # or "single-dhf"
  sub_dhfs:                        # present only when topology == multi-sub-dhf
    - name: pca-device
      parent: null
      regulatory: cleared          # cleared | in-development | concept
      filing: K210345
    - name: connectivity-adapter
      parent: null
      regulatory: in-development
      filing: null
    - name: cloud-suite
      parent: null
      regulatory: mixed
      filing: null
    - name: drug-library-manager
      parent: cloud-suite
      regulatory: in-development
      filing: null
    # ... etc ...
```

Skills read this manifest to discover the topology and enumerate sub-DHFs. It becomes the single source of truth for "what does this project contain."

### Strategy content tag extension — sub-DHF scoping

The `/strategy` skill currently uses tags like `<!-- STRATEGY CONTENT: regulatory, topic1, topic2 -->`. In a multi-sub-dhf project, the same task might contain strategy decisions for multiple sub-DHFs (e.g., a cross-cutting cybersecurity decision affecting both PCA and Cloud Suite). To route correctly, the tag grows an optional scope:

```markdown
<!-- STRATEGY CONTENT: regulatory, sub-dhf=pca-device, classification, filing -->
```

- No `sub-dhf=` key → shared strategy (routes to a top-level strategy doc, or applies to all sub-DHFs depending on the domain)
- `sub-dhf=<name>` → routes to that sub-DHF's strategy doc
- `sub-dhf=<name1>,<name2>` → routes to multiple sub-DHFs' strategy docs (rare; cross-cutting concerns)

The `assemble` action picks up the scope, finds the right output path via `project.yml`, and writes accordingly.

### Execution phasing inside task 007

Given the scope expansion, task 007 runs in phases:

| Phase | What ships | Gate |
|---|---|---|
| **P1. `medtech-docs` topology foundation** | Topology model in SKILL.md, `project.yml` schema, `check-topology` action, brief template updates | Design review before coding |
| **P2. `medtech-docs` migration action** | `migrate-to-multi-dhf` (dry-run + apply), `add-sub-dhf`, cross-link sweeper | Dry-run on PDLC_DEMO clean |
| **P3. `strategy` topology awareness** | Reads `project.yml` topology, per-sub-DHF output paths, `sub-dhf=` scope key in tags | `/strategy scan` and `assemble` work in both topologies |
| **P4. `tracker` topology awareness** | Per-sub-DHF dashboards and roll-up | Renders PDLC_DEMO in multi-sub-dhf mode |
| **P5. `best-practices` topology awareness** | Per-sub-DHF checks, composition-manifest validation | Audit PDLC_DEMO in multi-sub-dhf mode clean |
| **P6. PDLC_DEMO migration (live fire)** | Run the upgraded skill on PDLC_DEMO end to end | Full validation suite passes post-migration |
| **P7. Upstream contribution** | PR to hitachi registry | Merged or queued |

Phases P3–P5 can run in parallel once P1 and P2 land.

## Phase P1 — Design Deliverable

**Status**: Draft — under review. Three open flags resolved by user 2026-04-13: (1) `--verbose` is read-only, never prompts; (2) 2-level init cap + unbounded `add-sub-dhf` confirmed; (3) best-practices integration at Recommended severity in v1, promote mismatches to Required after `migrate-to-multi-dhf` stabilizes.

### Ambiguities resolved during drafting

Task 007's schema sketch (earlier in this doc) shows `sub_dhfs` entries using `name:` + `parent:` fields. Later narrative explicitly supersedes this with `path:` (relative to `docs/project/dhfs/`) as the canonical identifier, because `path` encodes nesting and avoids ambiguity across non-unique leaf names. This draft uses **`path`** as the primary key, keeps `parent` as an optional convenience field (derived-but-persisted for readability), and drops `name` — the last segment of `path` is the name.

The `regulatory` enum is **four values**: `cleared | in-development | concept | mixed`. `mixed` is required because `cloud-suite` hosts children of heterogeneous regulatory state.

`strategies/` as a shared top-level folder is preserved verbatim in the topology trees below but is not gated by topology — it exists in both `single-dhf` and `multi-sub-dhf` shapes and is out of scope for P1 decisions.

### P1.1 — Topology model (drafted SKILL.md section)

> The content below is the exact markdown to insert into `.claude/skills/medtech-docs/SKILL.md` immediately before the `### init` action definition, as a new top-level section `## Project Topology`.

#### Project Topology

**Topology** is the shape of a project's Design History File (DHF): is this one product with one DHF, or a multi-component ecosystem where several components each carry their own DHF and compose into shared filings? Topology is as fundamental as regulatory pathway — the scaffolder has to branch on it, consuming skills have to read it, and the project's `project.yml` records it. Skills that hardcode a single shape cannot be reused across real product ecosystems, and teams that start in the wrong shape pay for it later in migrations.

#### Supported topologies (v1)

| Topology | When to use | Recorded as |
|---|---|---|
| `single-dhf` | One product, one DHF, one primary filing path. Small devices, SaMD-only products, early-stage projects, or any project where a single DHF is the obviously-right shape. | `project.topology: single-dhf` |
| `multi-sub-dhf` | Product ecosystem where multiple components have separate regulatory paths and each component needs its own DHF (e.g., device + connectivity adapter + cloud suite). Filings compose from sub-DHFs. | `project.topology: multi-sub-dhf` |

**Default**: If `project.topology` is absent from `project.yml`, skills must treat the project as `single-dhf` for backward compatibility with projects initialized before topology existed.

#### Topology 1: `single-dhf`

Used for one-product projects. This is the current shape of `medtech-docs init` output.

```
docs/project/
├── external/                    (shared — FDA guidance, standards, frameworks)
├── internal/                    (shared — corp SOPs, templates)
├── input-analysis/              (shared — KOL, market, competitive, predicate)
├── strategies/                  (shared — commercial, operations)
├── design-controls/
│   ├── plans/
│   ├── user-needs/
│   ├── requirements/
│   ├── architecture/
│   ├── risk-management/
│   ├── vnv/
│   ├── tool-validation/
│   └── trace-matrix/
├── clinical/
├── postmarket/
├── cybersecurity/
└── submissions/
    └── <filing>/
```

**Constraints**:
- Exactly one DHF root.
- No `dhfs/` folder is created. Presence of `dhfs/` in a `single-dhf` project is a best-practices violation — either the project needs to migrate or the folder is stale.

#### Topology 2: `multi-sub-dhf`

Used for multi-component ecosystems. Each sub-DHF lives under `docs/project/dhfs/<component>/` and carries its own per-DHF content. Shared content (external, internal, input-analysis, strategies, submissions) stays at the top level.

```
docs/project/
├── external/                    (shared)
├── internal/                    (shared)
├── input-analysis/              (shared)
├── strategies/                  (shared — cross-cutting)
├── dhfs/
│   ├── <sub-dhf-1>/             e.g., pca-device   (leaf sub-DHF)
│   │   ├── README.md
│   │   ├── design-controls/
│   │   ├── clinical/
│   │   ├── postmarket/
│   │   ├── risk-management/
│   │   └── cybersecurity/
│   ├── <sub-dhf-2>/             e.g., connectivity-adapter (leaf)
│   │   └── ... (same shape)
│   └── <parent-sub-dhf>/        e.g., cloud-suite (platform with children)
│       ├── README.md
│       ├── design-controls/     ← platform-level
│       ├── risk-management/     ← platform-wide hazards
│       ├── cybersecurity/       ← shared platform posture
│       └── dhfs/                ← nested sub-DHF container
│           ├── <child-1>/       e.g., drug-library-manager
│           │   ├── design-controls/
│           │   ├── risk-management/
│           │   └── cybersecurity/
│           └── <child-2>/       e.g., fleet-management
│               └── ...
└── submissions/
    └── <filing>/
        ├── composition-manifest.md  ← lists the dhfs/*/... pieces in this filing
        └── ...
```

**Constraints**:
- The `dhfs/` folder is mandatory at the top level when `topology: multi-sub-dhf`.
- Every sub-DHF has at minimum a `README.md` and a `design-controls/` folder. Other per-DHF folders (`clinical/`, `postmarket/`, `risk-management/`, `cybersecurity/`) are created on-demand but recommended.
- Every `submissions/<filing>/` must have a `composition-manifest.md` listing which sub-DHF pieces are included in the filing. `best-practices` enforces this.

#### Shared-vs-per-DHF rule

The following table is the binding rule for where content lives in a `multi-sub-dhf` project. Skills use this table to route content to the correct path.

| Content | Location | Reasoning |
|---|---|---|
| `external/` (FDA guidance, standards, frameworks, clinical literature) | Shared — top-level | Upstream truth, not tied to any one product. Applies across the portfolio. |
| `internal/` (corporate SOPs, templates, procedures) | Shared — top-level | Corporate-level, applies to all products. |
| `input-analysis/` (KOL, market, competitive, predicate analysis) | Shared — top-level | Customer intelligence spans the whole portfolio; predicate reasoning often spans sub-DHFs. |
| `strategies/` (commercial, operations, cross-cutting strategies) | Shared — top-level | Cross-cutting by definition. Per-sub-DHF strategies (regulatory, clinical) live inside each sub-DHF. |
| `design-controls/` | Per-DHF | User needs, requirements, architecture, trace matrix are component-specific. |
| `clinical/` | Per-DHF | Clinical evaluation is tied to a specific device and indication. |
| `postmarket/` | Per-DHF | PMS, PMCF, CAPA, complaints are per-component. |
| `risk-management/` | Per-DHF | ISO 14971 hazard analysis is per-device. |
| `cybersecurity/` | Per-DHF | IEC 81001-5-1 assessment is per-component (but cross-linked at filing time). |
| `submissions/` | Top-level | Filings are shared scaffolding; each filing's `composition-manifest.md` lists which sub-DHF pieces it pulls in. |

#### Recursive `dhfs/` rule

Any sub-DHF can contain its own nested `dhfs/` folder for children. A parent sub-DHF is **first and foremost a sub-DHF in its own right** — it has its own `design-controls/`, `risk-management/`, `cybersecurity/`, etc., which describe the platform itself. Its `dhfs/` folder hosts child sub-DHFs, each of which repeats the pattern.

**Key rule**: at any sub-DHF level, platform content lives in the per-DHF folders. Child sub-DHFs live under a dedicated `dhfs/` folder. There is no naming collision because **`dhfs/` is never also a valid per-DHF folder name** — it is a reserved container name at every level of the tree.

Recursion depth is unbounded in the data model. `project.yml` encodes the full tree via `path` strings like `cloud-suite/dhfs/drug-library-manager`, and `add-sub-dhf` accepts any `--parent <path>` depth.

#### v1 2-level cap at init time

**`init` supports at most 2 levels of sub-DHF nesting in its interactive flow.** That is: top-level sub-DHFs, and one level of children beneath each. `add-sub-dhf` supports arbitrary depth, so deeper hierarchies remain reachable — just not at init time.

| Action | Max nesting at invocation |
|---|---|
| `/medtech-docs init --topology multi-sub-dhf` | 2 levels (top-level + one nested level) |
| `/medtech-docs add-sub-dhf <name>` | Unbounded (via `--parent <path>`) |

**Why the cap**: depth > 2 is rare, and interactive init prompts get hard to reason about beyond 2 levels. Keeping init simple while leaving the underlying model open means we don't have to re-architect when someone eventually needs 3 levels.

If a user asks about depth > 2 during init, the skill responds with:

> _"v1 init supports 2 levels of sub-DHF nesting. For deeper structures, complete init with 2 levels and then run `/medtech-docs add-sub-dhf <name> --parent <path>` to add grandchildren."_

#### Future topologies (out of scope for v1)

Topology is extensible. Future values for `project.topology` under consideration:

- **`platform-plus-apps`** — one shared platform DHF plus N app sub-DHFs that explicitly inherit design controls, risk, and cybersecurity from the platform. Today this pattern is approximated as nested `multi-sub-dhf` (e.g., `cloud-suite` with children), but a first-class topology would let the skill codify inheritance rules. Out of scope for v1.
- **`combination-product`** — drug + device + software split, with separate regulatory pathways per constituent part and coordinated filings. Out of scope for v1; teams in this shape should use `multi-sub-dhf` as a manual approximation until this topology lands.

### P1.2 — `project.yml` schema additions

> The content below is the exact YAML and documentation to add to a PDLC_DEMO-style `project.yml`. Additions are non-breaking; absence of `topology` means `single-dhf`.

#### New fields under `project:`

**`project.topology`**

```yaml
project:
  # ... existing fields (name, repo, type, regulatory_pathway, device_class, device_family) ...
  topology: multi-sub-dhf          # single-dhf | multi-sub-dhf
```

**`project.sub_dhfs`** — present only when `topology: multi-sub-dhf`. A flat list of sub-DHFs, each identified by its `path` relative to `docs/project/dhfs/`. Path encodes the full parent chain — nested sub-DHFs have paths like `cloud-suite/dhfs/drug-library-manager`.

```yaml
project:
  topology: multi-sub-dhf
  sub_dhfs:
    - path: <relative-path-under-docs/project/dhfs/>
      regulatory: <cleared|in-development|concept|mixed>
      filing: <510(k) number or null>
      parent: <parent path or null>   # optional, derived from `path`
```

#### Field reference

| Field | Type | Required | Description |
|---|---|---|---|
| `project.topology` | enum | No (default `single-dhf`) | Project shape. Allowed values: `single-dhf`, `multi-sub-dhf`. Absence means `single-dhf` for backward compatibility. |
| `project.sub_dhfs` | list | Required iff `topology: multi-sub-dhf` | List of sub-DHF manifest entries. Must be present and non-empty when topology is `multi-sub-dhf`. Must be absent or empty when topology is `single-dhf`. |
| `project.sub_dhfs[].path` | string | Yes | Path relative to `docs/project/dhfs/`. Top-level sub-DHFs are a single segment (e.g., `pca-device`). Nested sub-DHFs use the full chain with `dhfs/` segments (e.g., `cloud-suite/dhfs/drug-library-manager`). Must be unique within `sub_dhfs`. |
| `project.sub_dhfs[].regulatory` | enum | Yes | Regulatory status of this sub-DHF. Allowed values: `cleared`, `in-development`, `concept`, `mixed`. Use `mixed` for platform sub-DHFs whose children have heterogeneous regulatory states. |
| `project.sub_dhfs[].filing` | string or null | Yes | 510(k) number (or other filing identifier) if this sub-DHF is cleared; otherwise `null`. |
| `project.sub_dhfs[].parent` | string or null | No | Path of the parent sub-DHF, or `null` for top-level. This is derived from `path` (by stripping the trailing `/dhfs/<name>` segment) but may be explicitly recorded for readability. Skills must tolerate absence and compute parent from `path` when needed. |

#### Fully filled-in example — PDLC_DEMO

```yaml
project:
  name: pdlc_demo
  repo: GlobalLogic-a-Hitachi-Company/pdlc_demo
  type: medtech
  regulatory_pathway: 510k
  device_class: II
  device_family: pp3500
  topology: multi-sub-dhf
  sub_dhfs:
    # ─── Top-level sub-DHFs ───
    - path: pca-device
      regulatory: cleared
      filing: K210345
      parent: null

    - path: connectivity-adapter
      regulatory: in-development
      filing: null
      parent: null

    - path: cloud-suite
      regulatory: mixed              # platform hosts cleared + in-dev + MDDS children
      filing: null
      parent: null

    # ─── Cloud Suite children ───
    - path: cloud-suite/dhfs/drug-library-manager
      regulatory: in-development
      filing: null
      parent: cloud-suite

    - path: cloud-suite/dhfs/fleet-management
      regulatory: in-development
      filing: null
      parent: cloud-suite

    - path: cloud-suite/dhfs/telemetry-dashboards
      regulatory: in-development
      filing: null
      parent: cloud-suite

    - path: cloud-suite/dhfs/clinical-surveillance
      regulatory: concept
      filing: null
      parent: cloud-suite

    - path: cloud-suite/dhfs/software-update-distribution
      regulatory: in-development
      filing: null
      parent: cloud-suite

    - path: cloud-suite/dhfs/regulatory-data-pipelines
      regulatory: concept
      filing: null
      parent: cloud-suite

    - path: cloud-suite/dhfs/customer-portals
      regulatory: concept
      filing: null
      parent: cloud-suite
```

#### How consuming skills read this manifest

`project.yml` is the single source of truth for topology — skills must not discover sub-DHFs by glob-scanning the filesystem. Specifically:

- **`/strategy`** reads `project.topology` and, in multi-sub-dhf mode, resolves its output paths via `project.sub_dhfs[].path`. The `sub-dhf=<name>` scope key in `<!-- STRATEGY CONTENT: ... -->` tags maps to the last segment of a sub-DHF path (or to the full path in case of ambiguity). Shared strategies route to `docs/project/strategies/`.
- **`/tracker`** walks `project.sub_dhfs` to render one dashboard per sub-DHF plus a roll-up, and reads each `submissions/<filing>/composition-manifest.md` to show which sub-DHF pieces are in each filing.
- **`/best-practices`** reads `project.topology` to select the audit ruleset. In `multi-sub-dhf` mode it iterates `project.sub_dhfs[]` and runs per-DHF checks, then runs top-level checks for shared content and composition manifests.
- **`/medtech-docs`** itself reads the manifest for `dashboard`, `status`, `add-sub-dhf`, and `check-topology` actions.

#### Backward compatibility

- If `project.topology` is absent, skills must behave as if `topology: single-dhf` is set. No warning is emitted for absence — this is the backward-compatible default.
- If `project.topology: single-dhf`, `project.sub_dhfs` must be absent or empty. Skills emit a warning if the field is populated under single-dhf topology.
- If `project.topology: multi-sub-dhf`, `project.sub_dhfs` must be present and non-empty. Skills emit an error if the field is missing or empty under multi-sub-dhf topology.

### P1.3 — `check-topology` action spec

> The content below is the exact new action definition to add to `medtech-docs` SKILL.md under `## Actions`, placed after `dashboard` (as another advisory, non-mutating action).

#### `check-topology`

Advisory check that compares a project's declared topology against signals in the project and recommends whether to stay put or evolve. Non-destructive — reports only, never edits files.

**Usage**: `/medtech-docs check-topology [--verbose] [--json]`

**When to use**: Run this when you suspect your project is outgrowing its current topology — for example, when architecture discussions start naming multiple components with their own regulatory paths, when tasks reference multiple device IDs, or periodically as part of a best-practices sweep. The action is safe to run at any time; it never modifies files.

**Step 1 — Read current topology.** Read `project.yml`. Record:
- `project.topology` (default `single-dhf` if absent)
- `project.sub_dhfs` (empty if absent)
- `project.device_family`, `project.regulatory_pathway`

If `project.yml` is missing, report _"no project manifest found"_ and exit with an advisory to run `/medtech-docs init`.

**Step 2 — Scan signals.** Scan the project for signals that suggest a multi-component ecosystem. Each signal category is independent and contributes to the inferred topology.

| Signal | How to detect | Contribution |
|---|---|---|
| Multiple products in manifest | `project.yml` mentions more than one product name, or `project.sub_dhfs` has more than one entry | Strong |
| Multiple 510(k) numbers | `project.yml` and `CLAUDE.md` collectively reference more than one `K\d{6,}` filing identifier | Strong |
| Multiple device IDs across tasks | `tasks/**/*.md` reference more than one distinct device/product ID in frontmatter or prose | Medium |
| Cross-component infrastructure names | Any file or folder under `docs/` or `src/` whose name contains one of: `adapter`, `cloud`, `platform`, `suite`, `gateway`, `server`, `portal`, `fleet`, `telemetry` | Medium |
| Task content naming sub-DHFs | Task files explicitly discuss multiple components or sub-DHFs (match on `sub-dhf`, `sub-DHF`, `multi-component`, `ecosystem`) | Medium |
| SaMD components distinct from primary device | `src/` contains subdirectories that clearly correspond to separate SaMD products (e.g., `cloud-*`, `*-portal`, `*-app`) | Medium |
| Existing `dhfs/` folder | `docs/project/dhfs/` exists on disk | Strong (immediate mismatch if topology is `single-dhf`) |

**Step 3 — Score the signals.** Classify the overall signal strength as `strong`, `weak`, or `none`:

- **Strong**: any Strong-class signal fires, or three or more Medium-class signals fire
- **Weak**: one or two Medium-class signals fire, no Strong signals
- **None**: no signals fire

**Step 4 — Infer topology and produce recommendation.**

| Current | Signals | Inferred | Recommendation |
|---|---|---|---|
| `single-dhf` | none | `single-dhf` | OK — topology matches project |
| `single-dhf` | weak | `single-dhf` | OK with note — monitor; some multi-component hints exist but not enough to act |
| `single-dhf` | strong | `multi-sub-dhf` | Evolve — run `check-topology --verbose` to see signals, then plan migration via `migrate-to-multi-dhf` |
| `multi-sub-dhf` | any | `multi-sub-dhf` | OK — topology matches project |
| `multi-sub-dhf` (but no `dhfs/` folder on disk) | any | mismatch | Error — manifest says multi-sub-dhf but scaffold missing; run `/medtech-docs init` to create missing folders |

**Step 5 — Write the report.** Print a report to stdout. Do not write to disk. The report has five sections: Current Topology, Signals Detected, Inferred Topology, Recommendation, Next Steps.

**Flags**:

| Flag | Effect |
|---|---|
| `--verbose` | For every signal that fires, list the matched file path(s) and the exact text/name that triggered the match. No other behavior change. |
| `--json` | Emit the full report as a JSON object to stdout (for programmatic consumption). Suppresses human-readable output. |

**Exit behavior**: Always non-destructive. The action never writes files, never prompts the user (even in `--verbose` mode), and never modifies `project.yml`. Exit code is `0` on `OK`, `0` on `OK with note` and `Evolve` (advisory only), `1` on hard `Error` (mismatch between manifest and scaffold).

#### Example — passing `single-dhf` project

```
$ /medtech-docs check-topology

Current Topology
  Declared: single-dhf (from project.yml)

Signals Detected
  none

Inferred Topology
  single-dhf

Recommendation
  OK — topology matches project shape.

Next Steps
  (none)
```

#### Example — PDLC_DEMO-style project that should migrate

```
$ /medtech-docs check-topology

Current Topology
  Declared: single-dhf (default — no topology field in project.yml)

Signals Detected
  STRONG
    - Multiple 510(k) numbers referenced: K210345 (project.yml), K194512 (docs/project/submissions/510k/predicate-analysis.md)
    - Cross-component infrastructure names: "connectivity-adapter", "cloud-suite", "drug-library-manager" (7 matches under docs/project/ and tasks/)
  MEDIUM
    - Task content naming sub-DHFs: tasks/ben/006-architecture-regulatory-strategy.md, tasks/ben/007-sub-dhf-migration.md
    - SaMD components distinct from primary device: src/cloud-suite/, src/connectivity-adapter/

Inferred Topology
  multi-sub-dhf

Recommendation
  EVOLVE — this project shows strong multi-component signals but is still declared as single-dhf.
  The current scaffold will not cleanly hold the content the project is accumulating.

Next Steps
  1. Review signals with: /medtech-docs check-topology --verbose
  2. Dry-run the migration:   /medtech-docs migrate-to-multi-dhf pca-device
  3. Apply the migration:     /medtech-docs migrate-to-multi-dhf pca-device --apply
  4. Add remaining sub-DHFs:  /medtech-docs add-sub-dhf connectivity-adapter
                              /medtech-docs add-sub-dhf cloud-suite
                              /medtech-docs add-sub-dhf drug-library-manager --parent cloud-suite
                              ... (repeat for each Cloud Suite child)
```

#### Best-practices integration

This check should be registered in the `medtech-docs` Best Practices table as a **Recommended** severity check:

| Check | How to Verify | Severity |
|---|---|---|
| Topology matches project signals | `/medtech-docs check-topology` exits `0` with recommendation `OK` or `OK with note`. A recommendation of `Evolve` or an `Error` exit is a finding. | Recommended |

Recommended (not Required) because a team may legitimately defer migration while they finish current work — the check's job is to surface the gap, not to block commits. A hard Error (manifest says `multi-sub-dhf` but scaffold missing) should be promoted to Required in a future pass once `migrate-to-multi-dhf` is stable.

## Phase P2 — Migration Action Design

> **⚠️ Phase status under Architectural Pivot (2026-04-13):** Most of P2 is superseded. The `migrate-to-multi-dhf` action is **deleted** — there is no migration in the unified shape. `init --topology` is **deleted** — init always creates `dhfs/<primary>/`. P2.1 (init flow), P2.3 (migrate action), P2.4 (validator), P2.7 (dry-run gate) are **historical**. What survives into implementation: **P2.2 `add-sub-dhf`** (still the only way to add a sub-DHF), and **P2.5 Templates** (README template + composition-manifest template). The PDLC_DEMO reorg moves out of "skill feature" into "one-time P6 execution step." Historical content retained below for reasoning trail.


**Status**: Draft — pending review.

### P2.0 — Overview

Phase P2 designs the `medtech-docs` skill actions that **implement** the contract P1 locked in: `init --topology`, `add-sub-dhf`, and the highest-risk piece, `migrate-to-multi-dhf` with its dry-run machinery and cross-link sweeper. P1 defined _what_ the topology model is (the shapes, the `project.yml` schema, the shared-vs-per-DHF rule, and the advisory `check-topology` action). P2 defines _how_ the skill gets a project into and between those shapes without losing content, history, or cross-links.

P2 is **design-only**. No real file moves happen until Phase P6 runs the live migration on PDLC_DEMO. The P2 exit gate is a successful **dry-run** on a clean PDLC_DEMO working tree: `/medtech-docs migrate-to-multi-dhf pca-device` must produce a valid plan, zero errors, zero unresolved post-rewrite cross-links, a blast radius that matches expectation, and a report a human can review in under five minutes. When that passes, P2 is done.

P2 depends entirely on P1: the topology values (`single-dhf`, `multi-sub-dhf`), the `sub_dhfs[].path` schema, the shared-vs-per-DHF routing table, and the 2-level init cap are all locked upstream and this phase must not contradict them. Where this phase introduces new details (dry-run output format, cross-link rewrite rules, validator, templates), those details slot under the P1 contract — they do not alter it.

P2 sets up P3–P5 (topology awareness for `/strategy`, `/tracker`, `/best-practices`) by guaranteeing that after migration, every consuming skill sees the layout P1 promised: a populated `project.yml` with `topology: multi-sub-dhf`, a `docs/project/dhfs/<name>/` scaffold, and every cross-link resolving cleanly from its new location. Consuming skills do not have to reason about partial migrations — P2's apply phase either commits a coherent cutover or aborts.

The four deliverables of P2 are: (a) drafted SKILL.md additions for `init --topology`, `add-sub-dhf`, and `migrate-to-multi-dhf` in the exact voice of the existing SKILL.md; (b) a drafted post-migration link validator; (c) two new templates (per-sub-DHF README, composition manifest); and (d) best-practices table additions.

### P2.1 — `init --topology` flow (drafted SKILL.md addition)

> The content below is the exact markdown to splice into the existing `### init` action spec in `medtech-docs` SKILL.md. It extends Step 1 (context gathering), Step 2 (project.yml creation), and Step 3 (folder structure) with topology-aware branching. It does not remove any existing behavior.

#### `init` — topology extension

**New flag**: `--topology <single-dhf|multi-sub-dhf>`

| Flag | Default | Effect |
|---|---|---|
| `--topology single-dhf` | yes (default) | Existing behavior. Scaffolds `docs/project/{design-controls,clinical,postmarket,submissions,...}/`. No `project.yml` topology field is written (absence means `single-dhf` per P1 backward-compat rule). |
| `--topology multi-sub-dhf` | no | Enters the multi-sub-DHF interactive flow (below). Writes `project.topology: multi-sub-dhf` and a populated `project.sub_dhfs` list to `project.yml`. |

If `--topology` is omitted, `init` behaves **exactly as today** — same prompts, same scaffold, same `project.yml`. Backward compatibility is non-negotiable: existing projects and existing docs walk-throughs must not break.

If `--topology` is passed any value other than `single-dhf` or `multi-sub-dhf`, `init` prints `error: unknown topology '<value>'. Allowed values: single-dhf, multi-sub-dhf.` and exits non-zero before creating any files.

#### Step 1b — Topology prompts (only when `--topology multi-sub-dhf`)

Inserted between Step 1 (project context) and Step 2 (`project.yml`). Runs only in multi-sub-dhf mode.

1. **Top-level sub-DHF names.** Prompt: _"Enter the top-level sub-DHF names, one per line. Leave blank and press enter when done. Names must be lowercase kebab-case (letters, digits, hyphens)."_  Validate each name; reject if it contains slashes, whitespace, uppercase, or characters outside `[a-z0-9-]`. Require at least one name.

2. **Per-sub-DHF children.** For each top-level name entered, prompt: _"Does `<name>` contain nested child sub-DHFs? (y/N)"_  If `N` (default), move on. If `y`, prompt: _"Enter child sub-DHF names for `<name>`, one per line. Leave blank and press enter when done."_  Validate names the same way. After children are entered, **stop** — do not recurse into grandchildren.

3. **Depth > 2 guard.** If the user asks to go deeper than 2 levels (e.g., tries to enter `child/grandchild` as a child name, or asks a follow-up about grandchildren), print verbatim: _"v1 init supports 2 levels of sub-DHF nesting. For deeper structures, complete init with 2 levels and then run `/medtech-docs add-sub-dhf <name> --parent <path>` to add grandchildren."_  Then return to the child prompt.

4. **Regulatory status per sub-DHF.** For every sub-DHF entered (top-level and children), prompt: _"Regulatory status for `<path>`? (cleared | in-development | concept | mixed) [default: in-development]"_  Validate against the P1 enum.

5. **Filing per sub-DHF.** Prompt: _"510(k) number for `<path>`? (blank for none)"_  Accept a filing identifier or blank (stored as `null`).

All answers are collected and held in memory until Step 2 writes `project.yml` and Step 3 scaffolds the tree.

#### Step 2 extension — `project.yml` topology fields

When multi-sub-dhf mode is active, add two fields under `project:` in the generated `project.yml`:

```yaml
project:
  # ... existing identity fields ...
  topology: multi-sub-dhf
  sub_dhfs:
    - path: <segment or parent/dhfs/child>
      regulatory: <cleared|in-development|concept|mixed>
      filing: <id or null>
      parent: <parent path or null>
```

Entries are written in the order collected (top-level first, then each top-level's children immediately after the parent). The schema matches P1.2 verbatim.

In single-dhf mode, `project.topology` and `project.sub_dhfs` are **not** written. Absence is the backward-compatible signal for `single-dhf`.

#### Step 3 extension — Folder scaffold in multi-sub-dhf mode

In multi-sub-dhf mode, Step 3 creates the shared-content folders at the top level (`external/`, `internal/`, `input-analysis/`, `strategies/`, `submissions/`) exactly as in single-dhf mode, but **does not** create `docs/project/design-controls/`, `clinical/`, `postmarket/`, `risk-management/`, or `cybersecurity/` at the top level. Instead, for every sub-DHF entry it creates:

```
docs/project/dhfs/<path>/
├── README.md              ← from per-sub-DHF README template (see P2.5)
└── design-controls/
    └── README.md
```

A parent sub-DHF that has children gets an additional empty `dhfs/` folder ready to hold its children, and each child is scaffolded underneath it at `docs/project/dhfs/<parent>/dhfs/<child>/`.

The per-DHF folders `clinical/`, `postmarket/`, `risk-management/`, and `cybersecurity/` are **not** auto-created by `init` — they are created on-demand by `add-sub-dhf` or by the user when content is authored. This keeps the scaffold minimal and matches the P1 rule that only `README.md` and `design-controls/` are required at minimum.

#### Example session — `init --topology multi-sub-dhf`

```
$ /medtech-docs init --topology multi-sub-dhf

[Step 1 — project context: device type, pathway, modules, ...]
...

[Step 1b — topology]
Enter the top-level sub-DHF names, one per line. (blank to finish)
> pca-device
> connectivity-adapter
> cloud-suite
>

Does `pca-device` contain nested child sub-DHFs? (y/N) N
Does `connectivity-adapter` contain nested child sub-DHFs? (y/N) N
Does `cloud-suite` contain nested child sub-DHFs? (y/N) y
Enter child sub-DHF names for `cloud-suite`, one per line. (blank to finish)
> drug-library-manager
> fleet-management
>

Regulatory status for `pca-device`? [in-development] cleared
510(k) number for `pca-device`? K210345
Regulatory status for `connectivity-adapter`? [in-development]
510(k) number for `connectivity-adapter`?
Regulatory status for `cloud-suite`? [in-development] mixed
510(k) number for `cloud-suite`?
Regulatory status for `cloud-suite/dhfs/drug-library-manager`? [in-development]
510(k) number for `cloud-suite/dhfs/drug-library-manager`?
Regulatory status for `cloud-suite/dhfs/fleet-management`? [in-development]
510(k) number for `cloud-suite/dhfs/fleet-management`?

[Step 2 — writing project.yml with topology: multi-sub-dhf and 5 sub_dhfs entries]
[Step 3 — scaffolding docs/project/ + dhfs/ tree]
 created docs/project/dhfs/pca-device/README.md
 created docs/project/dhfs/pca-device/design-controls/README.md
 created docs/project/dhfs/connectivity-adapter/README.md
 created docs/project/dhfs/connectivity-adapter/design-controls/README.md
 created docs/project/dhfs/cloud-suite/README.md
 created docs/project/dhfs/cloud-suite/design-controls/README.md
 created docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/README.md
 created docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/design-controls/README.md
 created docs/project/dhfs/cloud-suite/dhfs/fleet-management/README.md
 created docs/project/dhfs/cloud-suite/dhfs/fleet-management/design-controls/README.md
...
Done. Next steps:
  - populate FDA guidance under docs/external/fda-guidance/
  - begin design controls in docs/project/dhfs/pca-device/design-controls/
  - run /medtech-docs add-sub-dhf <name> [--parent <path>] for additional components
```

#### Error cases

| Condition | Behavior |
|---|---|
| `--topology <unknown>` | Print error listing allowed values, exit non-zero, no files created |
| Interactive cancel (Ctrl-C during prompts) | Abort; do not write partial `project.yml`; do not scaffold any `dhfs/` folders |
| `docs/project/` already exists and is non-empty | Warn, list existing top-level children, ask _"Proceed? (y/N)"_  — same behavior as today; do not clobber existing folders |
| `project.yml` already exists with `topology: single-dhf` | Error: _"This project is already initialized as single-dhf. To convert, run `/medtech-docs migrate-to-multi-dhf <first-sub-dhf-name>`."_ |
| Duplicate sub-DHF name entered in prompts | Reject the second occurrence, re-prompt |
| Invalid name (uppercase, slash, space) | Reject, re-prompt with the validation rule |

#### Backward compatibility

- `init` with no flag or `--topology single-dhf` produces byte-identical output to today's `init` (modulo the existing init's own nondeterminism) — no topology field is written to `project.yml`, no `dhfs/` folder is created, no prompts change.
- A project initialized under v11 (pre-topology) can run `migrate-to-multi-dhf` (P2.3) at any time without first re-running `init`.

### P2.2 — `add-sub-dhf` action (drafted SKILL.md addition)

> The content below is the exact new action definition to add to `medtech-docs` SKILL.md under `## Actions`, placed after `check-topology` (P1.3).

#### `add-sub-dhf <name>`

Scaffold a new sub-DHF into an existing `multi-sub-dhf` project. Creates the folder tree, writes a starter README, and appends the new entry to `project.yml` `sub_dhfs`. Atomic — either all writes succeed or none do.

**Usage**: `/medtech-docs add-sub-dhf <name> [--parent <path>] [--regulatory <status>] [--filing <number>]`

**When to use**: After a `multi-sub-dhf` project needs a new component added — either a new top-level sub-DHF (e.g., adding `connectivity-adapter` after the project initially shipped with just `pca-device`), or a new child under an existing platform sub-DHF (e.g., adding `drug-library-manager` under `cloud-suite`). This is also how you extend the tree beyond the 2-level init cap — pass a `--parent` path of any depth.

**Precondition**: `project.yml` must have `topology: multi-sub-dhf`. If `project.topology` is absent or `single-dhf`, the action refuses to run with:

> _"This project is in single-dhf topology. To add sub-DHFs, first convert the project with `/medtech-docs check-topology` and then `/medtech-docs migrate-to-multi-dhf <first-sub-dhf-name>`."_

**Step 1 — Parse and validate arguments**

| Argument | Required | Validation |
|---|---|---|
| `<name>` | Yes | Lowercase kebab-case: matches `^[a-z0-9][a-z0-9-]*$`. No slashes, no whitespace, no uppercase. |
| `--parent <path>` | No | Path relative to `docs/project/dhfs/`. Must identify an existing sub-DHF directory. May be any depth (e.g., `cloud-suite` or `cloud-suite/dhfs/drug-library-manager`). |
| `--regulatory <status>` | No | One of `cleared`, `in-development`, `concept`, `mixed`. Default: `in-development`. |
| `--filing <number>` | No | Free-form filing identifier string, or omitted (stored as `null`). |

**Step 2 — Resolve the target path**

- Without `--parent`: target = `docs/project/dhfs/<name>/`; manifest path = `<name>`.
- With `--parent <p>`: target = `docs/project/dhfs/<p>/dhfs/<name>/`; manifest path = `<p>/dhfs/<name>`.

**Step 3 — Validate target state**

- Target directory must **not** already exist. If it does, exit with `error: target already exists at <path>`.
- The manifest path must **not** already appear in `project.sub_dhfs[].path`. If it does, exit with `error: sub-DHF '<manifest-path>' already registered in project.yml`.
- With `--parent`: `docs/project/dhfs/<parent>/` must exist on disk _and_ must already appear in `project.sub_dhfs`. If either fails, exit with `error: parent sub-DHF '<parent>' not found`.

**Step 4 — Scaffold the folder tree**

Create the target directory plus the following leaf structure:

```
docs/project/dhfs/<manifest-path>/
├── README.md                ← from per-sub-DHF README template (P2.5)
├── design-controls/
│   └── README.md
├── clinical/
│   └── README.md
├── postmarket/
│   └── README.md
├── risk-management/
│   └── README.md
└── cybersecurity/
    └── README.md
```

A nested `dhfs/` folder is **not** pre-created. It will be created on demand the first time a child is added via another `add-sub-dhf` call. This avoids empty container folders.

**Step 5 — Write the starter README**

Render the per-sub-DHF README template (P2.5) with placeholders filled from the CLI args: `{{NAME}}`, `{{PATH}}`, `{{PARENT}}` (or `null`), `{{REGULATORY}}`, `{{FILING}}` (or blank). The starter README includes cross-links to the parent sub-DHF's README (if any) and to the shared `../../../../input-analysis/` and `../../../../external/` folders, computed from the actual target depth.

**Step 6 — Update `project.yml` atomically**

Append a new entry to `project.sub_dhfs`:

```yaml
- path: <manifest-path>
  regulatory: <status>
  filing: <number or null>
  parent: <parent-path or null>
```

Write `project.yml` using an atomic rewrite (write to `project.yml.tmp`, then rename). If the rewrite fails for any reason, roll back any folders created in Step 4 (`git clean -fd` on the newly-created target, or plain `rm -rf` if not yet in git) so the project is not left half-changed.

**Step 7 — Report**

Print a summary:

```
Created sub-DHF `drug-library-manager` under `cloud-suite`
  path:        docs/project/dhfs/cloud-suite/dhfs/drug-library-manager/
  regulatory:  in-development
  filing:      (none)
  files:       README.md + 5 per-DHF folders (each with README.md)
  project.yml: sub_dhfs[] now has 6 entries
```

#### Examples

```
# Add a top-level sub-DHF
/medtech-docs add-sub-dhf connectivity-adapter

# Add a child under an existing platform sub-DHF
/medtech-docs add-sub-dhf drug-library-manager --parent cloud-suite

# Add with explicit regulatory status and filing
/medtech-docs add-sub-dhf pca-device --regulatory cleared --filing K210345

# Add a grandchild (post-init, any depth)
/medtech-docs add-sub-dhf telemetry-adapter \
  --parent cloud-suite/dhfs/drug-library-manager
```

#### Error cases and messages

| Condition | Message |
|---|---|
| Topology is `single-dhf` or missing | _"This project is in single-dhf topology. Run `/medtech-docs check-topology` then `/medtech-docs migrate-to-multi-dhf <name>` first."_ |
| Invalid `<name>` | _"error: invalid name '<name>' — must match [a-z0-9][a-z0-9-]*"_ |
| Target already exists | _"error: target already exists at docs/project/dhfs/<path>/"_ |
| Parent path missing on disk | _"error: parent sub-DHF '<parent>' not found on disk"_ |
| Parent not in `project.yml` | _"error: parent sub-DHF '<parent>' not registered in project.sub_dhfs"_ |
| Invalid `--regulatory` value | _"error: regulatory must be one of: cleared, in-development, concept, mixed"_ |
| `project.yml` write fails | _"error: failed to update project.yml — rolling back filesystem changes"_  + rollback |

#### Best-practices implications

- All writes are atomic within a single action invocation. If any step fails, the project is left in its pre-action state.
- The action does not commit to git; the user is expected to review and commit manually. The action may print a suggested commit message: `"add-sub-dhf: scaffold <path> under dhfs/"`.
- `project.yml` `sub_dhfs` must never be left out of sync with the on-disk `dhfs/` tree. A post-action sanity check walks `project.sub_dhfs` and verifies each `path` exists on disk; any mismatch is reported as a warning (the action still exits zero, but surfaces the problem).

### P2.3 — `migrate-to-multi-dhf` action (drafted SKILL.md addition)

> The content below is the exact new action definition to add to `medtech-docs` SKILL.md under `## Actions`, placed after `add-sub-dhf`. This is the highest-risk action in the skill and is drafted in maximum detail.

#### `migrate-to-multi-dhf <first-sub-dhf-name>`

Evolve a `single-dhf` project into a `multi-sub-dhf` project by moving the existing per-DHF content under `docs/project/dhfs/<first-sub-dhf-name>/`, rewriting internal cross-links, and updating `project.yml`. **Dry-run is the default** — `--apply` is required to actually move files. This is the critical safety rail.

**Usage**: `/medtech-docs migrate-to-multi-dhf <first-sub-dhf-name> [--apply] [--verbose] [--regulatory <status>] [--filing <number>]`

**When to use**: After `/medtech-docs check-topology` recommends `Evolve` — the project has outgrown `single-dhf` and needs to become `multi-sub-dhf`. Run this first in dry-run mode to review the plan, then run with `--apply` to execute.

#### Flags

| Flag | Default | Effect |
|---|---|---|
| `--apply` | off | Execute the migration. Without this flag, the action is a dry-run and makes no changes. |
| `--verbose` | off | In dry-run, list every cross-link rewrite individually instead of aggregating. Read-only — never prompts even in verbose mode. |
| `--regulatory <status>` | `in-development` | Passed through to the new `sub_dhfs` entry. One of `cleared`, `in-development`, `concept`, `mixed`. |
| `--filing <number>` | (inherit or null) | Passed through to the new `sub_dhfs` entry. If omitted and `project.yml` has a pre-existing `filing` field, that value is inherited; otherwise `null`. |

#### Preconditions (checked before dry-run and again before apply)

1. **Project must currently be `single-dhf`.** If `project.topology: multi-sub-dhf`, exit with _"project is already in multi-sub-dhf topology; use `add-sub-dhf` to add components"_.
2. **Project must be a git repository** with a **clean working tree** (no staged, unstaged, or untracked changes under `docs/project/`). If dirty, exit with _"working tree not clean; commit or stash changes before migrating"_  and list the offending files.
3. **`<first-sub-dhf-name>` must be a valid folder name** (same rule as `add-sub-dhf`: `^[a-z0-9][a-z0-9-]*$`).
4. **Target `docs/project/dhfs/<first-sub-dhf-name>/` must not already exist.** If it does and its contents already match the planned migration output, this is the idempotency case — exit zero with _"migration already applied; no changes needed"_. Otherwise exit non-zero with _"target exists; refusing to overwrite"_.
5. **Not a git repo**: exit with _"not a git repo; migrate-to-multi-dhf requires git to preserve history. Run `git init` first."_

#### Algorithm — dry-run phase

1. **Read current state.** Load `project.yml`. Record the current `filing` field (if any), device family, and existing top-level folder list.
2. **Compute the file-move plan.** For each per-DHF folder that exists at `docs/project/` top level — `design-controls/`, `clinical/`, `postmarket/`, `risk-management/`, `cybersecurity/` — the destination is `docs/project/dhfs/<first-sub-dhf-name>/<folder>/`. Shared folders (`external/`, `internal/`, `input-analysis/`, `strategies/`, `submissions/`) do **not** move. Walk each moving folder recursively and enumerate every file; the set of enumerated files is the move manifest.
3. **Compute the cross-link rewrite plan.** For every `*.md` file in the move manifest, plus every `*.md` file in the shared folders that might link into a moving folder, parse markdown links and classify each one (see the sweeper spec below). Build a per-file rewrite table mapping old link → new link. Links that do not need rewriting are not in the table.
4. **Compute the `project.yml` diff.** The additions are:
   - Add `topology: multi-sub-dhf` under `project:`.
   - Add a `sub_dhfs:` list with one entry:
     ```yaml
     sub_dhfs:
       - path: <first-sub-dhf-name>
         regulatory: <--regulatory value, default in-development>
         filing: <--filing value, or inherited, or null>
         parent: null
     ```
   - If the project previously carried a `filing` field at `project.filing`, it is left in place (the new one is per-sub-DHF). A `[VERIFY]` note is added to the dry-run report recommending the user remove the top-level `filing` field post-migration.
5. **Print the dry-run report** (format below).
6. **Exit zero without touching any files.**

#### Algorithm — apply phase (only with `--apply`)

1. **Re-run the dry-run internally** to produce a fresh plan (the working tree might have changed between invocations). Abort if preconditions now fail.
2. **Remain on the current branch.** The migration produces a single commit on the current branch for recoverability. Do not create a new branch; the user can do that before invoking if they want isolation.
3. **Execute the file moves** via `git mv <old> <new>` for every entry in the move manifest. This preserves git history. `git mv` handles the intermediate directory creation. If any `git mv` fails, abort with the error and the partial state intact (the user can `git reset --hard HEAD` to recover).
4. **Execute the cross-link rewrites.** For each file in the rewrite plan, open it, apply every rewrite in the per-file table, and write the file back. Use exact-substring replacement on the pre-computed link strings — not a live regex rescan — so the rewrites are deterministic and match the dry-run report.
5. **Update `project.yml`** with the additions from Step 4 of the dry-run.
6. **Run the post-migration validator** (P2.4) on the rewritten tree. If any broken link is found, abort **before committing**, print the validator failures, and leave the working tree modified so the user can inspect. Exit non-zero.
7. **If validation passes**, `git add -A && git commit -m "migrate-to-multi-dhf: wrap <device-family> content under dhfs/<first-sub-dhf-name>/"`. Include a longer commit body listing the move count, rewrite count, and blast radius.
8. **Print an apply summary** showing what was moved, what was rewritten, and the commit SHA. Exit zero.
9. **If any step between 3 and 7 fails**, the working tree is left modified (no auto-rollback — the user needs to see what happened). The action prints `"migration aborted; run 'git status' to inspect, 'git reset --hard HEAD' to roll back"` and exits non-zero.

#### Dry-run report — output format

The report has six sections, printed in this order:

**1. Preconditions**

```
Preconditions
  git repo:             yes
  working tree clean:   yes
  current topology:     single-dhf
  target name valid:    yes (pca-device)
  target not existing:  yes (docs/project/dhfs/pca-device/)
```

**2. File moves**

A table with columns `old path`, `new path`, `file count`. Aggregated per top-level moving folder in non-verbose mode, one row per file in `--verbose` mode.

```
File moves
  docs/project/design-controls/   → docs/project/dhfs/pca-device/design-controls/   (47 files)
  docs/project/clinical/          → docs/project/dhfs/pca-device/clinical/          (19 files)
  docs/project/postmarket/        → docs/project/dhfs/pca-device/postmarket/        (12 files)
  docs/project/risk-management/   → docs/project/dhfs/pca-device/risk-management/   (6 files)
  docs/project/cybersecurity/     → docs/project/dhfs/pca-device/cybersecurity/     (4 files)
  ──────────────────────────────────────────────────────────────────────────────────
  Total: 88 files moved
```

**3. Cross-link rewrites**

Per-file tables. Non-verbose aggregates by source file: `<path>: <N> links rewritten`. Verbose lists every `old → new` pair.

```
Cross-link rewrites (verbose)
  docs/project/design-controls/user-needs/user-needs.md
    ../../input-analysis/kol-feedback/KOL-0006-paul-james.md
      → ../../../../input-analysis/kol-feedback/KOL-0006-paul-james.md
    ../requirements/design-inputs.md
      → ../requirements/design-inputs.md   (unchanged — sibling inside design-controls/)
  docs/project/clinical/benefit-risk/BRA-1001.md
    ../../postmarket/capa/CAPA-2023-001.md
      → ../../postmarket/capa/CAPA-2023-001.md   (unchanged — both moved together, same relative depth)
    ../../external/standards/iso-14971.md
      → ../../../../external/standards/iso-14971.md
  ...
  ──────────────────────────────────────────────────────────────────────────────────
  Total: 42 links rewritten across 31 files
```

**4. `project.yml` diff**

```
project.yml diff
+ topology: multi-sub-dhf
+ sub_dhfs:
+   - path: pca-device
+     regulatory: in-development
+     filing: K210345                 # [VERIFY] inherited from project.filing
+     parent: null
```

**5. Blast radius**

```
Blast radius
  files moved:            88
  links rewritten:        42
  files modified:         31
  project.yml lines:      +6
  estimated review time:  < 5 minutes
```

**6. Next step hint**

```
Next step
  This was a dry-run. No changes have been made.
  To execute:   /medtech-docs migrate-to-multi-dhf pca-device --apply
```

#### Idempotency

Running `migrate-to-multi-dhf <name>` a second time with the same `<name>` after a successful apply detects that `docs/project/dhfs/<name>/` already exists and that `project.topology` is already `multi-sub-dhf`. The action exits zero with:

> _"migration already applied for sub-DHF `<name>`. Use `add-sub-dhf` to add more components."_

It does **not** attempt to re-process or "top off" the migration. This keeps the action's semantics simple: migrate once, then use `add-sub-dhf`.

#### Error cases

| Condition | Behavior |
|---|---|
| Dirty git tree | Refuse; print offending files under `docs/project/`; exit non-zero |
| Not a git repo | Refuse; suggest `git init` |
| Target `dhfs/<name>/` exists and mismatches plan | Refuse; exit non-zero |
| Target `dhfs/<name>/` exists and matches plan | Idempotency case; exit zero with note |
| Topology already `multi-sub-dhf` | Refuse; suggest `add-sub-dhf` |
| Invalid `<first-sub-dhf-name>` | Refuse with validation message |
| `git mv` fails mid-apply | Abort; leave partial state; print recovery command |
| Validator finds broken links post-rewrite | Abort before commit; print failures; leave tree modified |

#### Cross-link sweeper — specification

This is the single highest-risk piece of the action. It governs how the sweeper identifies, classifies, and rewrites internal markdown links.

**Scope**: only `*.md` files. Non-markdown files (images, PDFs, DOCX, YAML) are never rewritten. Code blocks inside markdown are skipped — the sweeper does not rewrite links inside fenced `\`\`\`` blocks to avoid corrupting code examples.

**Link regex**: `\[([^\]]*)\]\(([^)]+)\)`  — captures link text and target.

**Skip rules**: any link whose target matches one of the following is left untouched:

- Absolute URL: starts with `http://`, `https://`, `mailto:`, `ftp://`, or `file://`
- Anchor-only: starts with `#`
- Absolute filesystem path: starts with `/`

**Classify each relative link**: resolve the target from the source file's **current** location on disk. Compare the resolved target to the move manifest. Four cases:

| Case | Definition | Rewrite rule |
|---|---|---|
| (a) **Shared destination** | Target resolves into a shared folder (`external/`, `internal/`, `input-analysis/`, `strategies/`, `submissions/`, or `docs/`) | Recompute the relative path from the file's **new** location (one level deeper inside `dhfs/<name>/<per-DHF>/...`). In practice this adds one more `../` segment for every level the source file descended. |
| (b) **Cross per-DHF destination** | Target resolves into a different per-DHF folder that is also moving (e.g., `design-controls/...` → `clinical/...`) | Both source and destination move together into the same `dhfs/<name>/`. The relative path between them is **unchanged**. |
| (c) **Same per-DHF destination** | Target resolves into the same per-DHF folder as the source (`../user-needs/foo.md` from inside `design-controls/trace-matrix/`) | Unchanged — internal to a subtree that moves as a unit. |
| (d) **Destination not in move manifest and not shared** | Target resolves to something outside the project docs (e.g., `../../src/...`) or to a nonexistent path | Flag as a **pre-existing broken link** in the dry-run report. The sweeper does not rewrite it. The validator (P2.4) will also flag it post-migration. |

**Preserve suffixes**: query strings (`?foo=bar`) and anchors (`#section`) on the target are preserved verbatim during rewrite.

**Preserve link text**: the `[text]` portion is never touched.

**Deterministic rewrite**: the rewrite plan is computed once in the dry-run phase and applied as exact-substring replacements during apply. Live re-scanning during apply is forbidden — it would introduce nondeterminism between the dry-run report and the actual changes.

**Verbose logging**: in `--verbose` mode, every classification decision is logged, including links in category (c) that were not rewritten. This gives the reviewer full confidence that nothing was silently skipped.

#### Example transformations

The following examples are drawn from the current PDLC_DEMO layout and illustrate each sweeper classification. `pca-device` is the `<first-sub-dhf-name>` in the examples.

1. **Shared destination — link deepens by four segments.**

   Source: `docs/project/design-controls/user-needs/user-needs.md` → moves to `docs/project/dhfs/pca-device/design-controls/user-needs/user-needs.md`.

   Old link: `[KOL interview](../../input-analysis/kol-feedback/KOL-0006-paul-james.md)`
   New link: `[KOL interview](../../../../input-analysis/kol-feedback/KOL-0006-paul-james.md)`

2. **Shared destination — one-level source file.**

   Source: `docs/project/design-controls/trace-matrix/un-to-di-trace-matrix.md` → moves to `docs/project/dhfs/pca-device/design-controls/trace-matrix/un-to-di-trace-matrix.md`.

   Old link: `[Predicate analysis](../../input-analysis/predicate-analysis/K194512.md)`
   New link: `[Predicate analysis](../../../../input-analysis/predicate-analysis/K194512.md)`

3. **Cross per-DHF destination — unchanged.**

   Source: `docs/project/clinical/benefit-risk/BRA-1001.md` → moves to `docs/project/dhfs/pca-device/clinical/benefit-risk/BRA-1001.md`.

   Old link: `[CAPA-2023-001](../../postmarket/capa/CAPA-2023-001.md)`
   New link: `[CAPA-2023-001](../../postmarket/capa/CAPA-2023-001.md)`  _(unchanged — both `clinical/` and `postmarket/` move together into `dhfs/pca-device/`, same relative depth)_

4. **Same per-DHF destination — unchanged.**

   Source: `docs/project/design-controls/trace-matrix/un-to-di-trace-matrix.md`
   Old link: `[User needs](../user-needs/user-needs.md)`
   New link: `[User needs](../user-needs/user-needs.md)`  _(unchanged — sibling inside design-controls/, which moves as a unit)_

5. **Cross per-DHF destination, reverse direction.**

   Source: `docs/project/postmarket/capa/CAPA-2023-001.md` → moves to `docs/project/dhfs/pca-device/postmarket/capa/CAPA-2023-001.md`.

   Old link: `[Hazard analysis](../../risk-management/hazard-analysis.md)`
   New link: `[Hazard analysis](../../risk-management/hazard-analysis.md)`  _(unchanged — both per-DHF folders move together)_

6. **Shared destination from deeper nesting.**

   Source: `docs/project/design-controls/vnv/system-test/st-0002.md` → moves to `docs/project/dhfs/pca-device/design-controls/vnv/system-test/st-0002.md`.

   Old link: `[IEC 62304](../../../external/standards/iec-62304.md)`
   New link: `[IEC 62304](../../../../../external/standards/iec-62304.md)`

### P2.4 — Post-migration validator (internal sub-action)

**Purpose**: catch broken cross-links before the apply phase commits. This is the last line of defense against the sweeper silently mangling a link. If this validator passes, the commit lands; if it fails, the commit is aborted and the user inspects.

**Invocation**: not a standalone user-facing action in v1. It is called internally by `migrate-to-multi-dhf --apply` between the rewrite step and the commit step. It may be promoted to a top-level `/medtech-docs validate-links` action in a later version if teams want to run it manually (e.g., after hand-edits).

**Algorithm**:

1. Walk every `*.md` file under `docs/project/` (including the newly relocated `dhfs/<name>/...` tree and all shared folders).
2. For each file, parse markdown links using the same regex and skip rules as the sweeper (`[text](target)`, skipping absolute URLs, anchor-only links, and links inside fenced code blocks).
3. For every relative link, resolve the target from the file's current location. If the resolved path does not exist on disk as a file, record the link as `broken`.
4. Collect the broken-link list, grouped by source file.

**Output**:

- On success (zero broken links): print `"link validator: OK (<N> files scanned, <M> links resolved)"` and return exit code 0 to the caller.
- On failure: print a per-file report listing every broken link with its resolved path, and return non-zero.

**Exit behavior inside `migrate-to-multi-dhf --apply`**: any validator failure is treated as a migration failure. The commit is **not** created; the working tree is left in its rewritten state so the user can inspect; `migrate-to-multi-dhf` exits non-zero with instructions.

**Scope exclusions**: the validator does not validate external URLs (no network calls), anchor targets within a file (no heading parsing), or image references. Those are out of scope for v1.

**Pre-existing broken links**: the validator reports pre-existing broken links too (links that were broken before migration). To avoid blocking migrations on pre-existing rot, the validator distinguishes `pre-existing` (broken in the starting state of the repo, determined by running a baseline scan during the dry-run phase) from `newly-broken` (broken only after rewrite). The apply phase aborts on `newly-broken` findings but only warns on `pre-existing` findings. Both are listed in the report.

### P2.5 — Templates (drafted as skill assets)

Two new template files to install under `.claude/skills/medtech-docs/templates/` when P2 lands. Full verbatim content below.

#### Template 1 — `readme-sub-dhf.md` (per-sub-DHF README)

Used by `init --topology multi-sub-dhf` and `add-sub-dhf` as the starter `README.md` for every new sub-DHF folder. Placeholders: `{{NAME}}`, `{{PATH}}`, `{{PARENT}}`, `{{REGULATORY}}`, `{{FILING}}`, `{{CLASSIFICATION}}`, `{{DEPTH_UP_TO_SHARED}}` (number of `../` segments needed to reach `docs/project/` from this sub-DHF).

```markdown
# {{NAME}} — Sub-DHF

_Design History File for the `{{NAME}}` component. Part of a `multi-sub-dhf` project._

## Identity

| Field | Value |
|---|---|
| Sub-DHF path | `{{PATH}}` |
| Parent sub-DHF | `{{PARENT}}` |
| Regulatory status | `{{REGULATORY}}` |
| Filing | `{{FILING}}` |
| Intended classification | `{{CLASSIFICATION}}` |

## Purpose

_One-to-two paragraph description of what this sub-DHF covers: the component, its role in the ecosystem, its regulatory boundary, and how it relates to its parent (if any) and sibling sub-DHFs._

## Structure

| Folder | Purpose |
|---|---|
| `design-controls/` | User needs, requirements, architecture, trace matrix, plans, V&V, tool validation for this component |
| `clinical/` | Clinical evaluation, benefit-risk, literature search scoped to this component |
| `postmarket/` | PMS, PMCF, CAPA, complaints specific to this component |
| `risk-management/` | ISO 14971 hazard analysis for this component |
| `cybersecurity/` | IEC 81001-5-1 security assessment for this component |
| `dhfs/` | _(only if this sub-DHF hosts nested child sub-DHFs)_ Child sub-DHFs |

## Shared content

Shared content lives at the top of the project, not inside this sub-DHF:

- `{{DEPTH_UP_TO_SHARED}}external/` — FDA guidance, standards, frameworks, clinical literature
- `{{DEPTH_UP_TO_SHARED}}internal/` — corporate SOPs, templates
- `{{DEPTH_UP_TO_SHARED}}input-analysis/` — KOL, market, competitive, predicate analysis
- `{{DEPTH_UP_TO_SHARED}}strategies/` — cross-cutting commercial/operations strategies
- `{{DEPTH_UP_TO_SHARED}}submissions/` — filings, each with a composition-manifest.md pointing back to this sub-DHF's pieces

## Conventions

- Working markdown at the root of each leaf folder; controlled deliverables in `formal/`.
- Cross-links to shared content use relative paths up and over through `{{DEPTH_UP_TO_SHARED}}`.
- Cross-links to sibling sub-DHFs use the full `dhfs/<sibling-path>/...` route.

## Changelog

| Date | Author | Summary |
|---|---|---|
| YYYY-MM-DD | init | Created sub-DHF scaffold |
```

#### Template 2 — `composition-manifest.md` (per-filing composition manifest)

Used by every `submissions/<filing>/` folder in a `multi-sub-dhf` project to record which sub-DHF pieces are included in the filing. Placeholders: `{{FILING_ID}}`, `{{FILING_TYPE}}`, `{{TARGET_CLASS}}`, `{{DATE}}`, `{{DEVICE_FAMILY}}`.

```markdown
# Composition Manifest — {{FILING_ID}}

_Lists which sub-DHF pieces are included in this filing, which are excluded, and why._

## Filing identification

| Field | Value |
|---|---|
| Filing type | {{FILING_TYPE}}   _(510(k), De Novo, PMA, Q-Sub, PCCP)_ |
| Filing ID | {{FILING_ID}}     _(510(k) number once assigned)_ |
| Target classification | {{TARGET_CLASS}} |
| Device family | {{DEVICE_FAMILY}} |
| Target submission date | {{DATE}} |
| Prepared by | _(name)_ |

## Included pieces

The following sub-DHF content is pulled into this filing. Every row cites a concrete path under `docs/project/dhfs/<sub-dhf>/...`.

| Sub-DHF path | Content type | Source path | Reason for inclusion |
|---|---|---|---|
| `pca-device` | Design controls | `dhfs/pca-device/design-controls/` | Primary device under filing |
| `pca-device` | Clinical evaluation | `dhfs/pca-device/clinical/` | Benefit-risk and literature for primary device |
| `pca-device` | Risk management | `dhfs/pca-device/risk-management/` | ISO 14971 hazard analysis for primary device |
| `pca-device` | Cybersecurity | `dhfs/pca-device/cybersecurity/` | IEC 81001-5-1 assessment for primary device |
| `connectivity-adapter` | Cybersecurity (excerpt) | `dhfs/connectivity-adapter/cybersecurity/` | Adapter is an interface surface; security assessment relevant to filing |

## Excluded pieces

Sub-DHF content **deliberately not** pulled into this filing, with rationale. This section exists so a reviewer can confirm that omission was intentional, not accidental.

| Sub-DHF path | Content type | Reason for exclusion |
|---|---|---|
| `connectivity-adapter` | Full design controls | Adapter is a separate filing path; only cybersecurity assessment is cross-referenced here |
| `cloud-suite/**` | All content | Cloud Suite is non-device / MDDS; not in scope of this device filing |

## Cross-references to source sub-DHFs

Every included piece above is a live pointer to the sub-DHF source of truth. Do not duplicate content — the filing package is built by `/medtech-docs` or `/tracker` from these references at filing-assembly time.

## Reviewer sign-off

| Role | Name | Date | Signature |
|---|---|---|---|
| Regulatory Affairs | | | |
| Quality | | | |
| Clinical | | | |
| Cybersecurity | | | |
| Project Lead | | | |

## Conventions

- Every filing folder has exactly one composition-manifest.md at its root.
- Paths always use forward slashes and are relative to `docs/project/`.
- Update this manifest whenever a new piece is added to or removed from the filing scope.

## Changelog

| Date | Author | Summary |
|---|---|---|
| YYYY-MM-DD | init | Created composition manifest |
```

### P2.6 — Best-practices updates (drafted SKILL.md additions)

The following rows extend the existing `## Best Practices` table in `medtech-docs` SKILL.md. They slot in after the existing topology row added in P1.3.

| Check | How to Verify | Severity |
|---|---|---|
| Topology matches project signals | `/medtech-docs check-topology` exits `0` with recommendation `OK` or `OK with note`. A recommendation of `Evolve` or an `Error` exit is a finding. | Recommended |
| `sub_dhfs` manifest matches on-disk tree | When `project.topology: multi-sub-dhf`, every entry in `project.sub_dhfs[].path` resolves to an existing directory under `docs/project/dhfs/`, and every directory under `docs/project/dhfs/**/` whose parent is either `dhfs/` or `.../dhfs/` is listed in `project.sub_dhfs[]`. No orphans in either direction. | Required (when `topology: multi-sub-dhf`) |
| Every sub-DHF has minimum content | When `project.topology: multi-sub-dhf`, every directory in `docs/project/dhfs/**/` that corresponds to a `sub_dhfs[]` entry contains at least a `README.md` and a `design-controls/` subfolder. | Required (when `topology: multi-sub-dhf`) |
| Every filing has a composition manifest | When `project.topology: multi-sub-dhf`, every `docs/project/submissions/<filing>/` contains a `composition-manifest.md` at its root. | Recommended |
| No broken relative links post-migration | Immediately after any `migrate-to-multi-dhf --apply`, a repo-wide link validator (P2.4) reports zero `newly-broken` relative links. Otherwise the check runs at Recommended severity and surfaces pre-existing rot. | Required immediately after migration; Recommended otherwise |
| Migration blast radius logged | The task doc or PR description for any migration records the blast radius (files moved, links rewritten, project.yml diff summary) from the dry-run report. | Recommended |

Per the P1 decision, all best-practices checks added in this task are at **Recommended** severity in v1 except the two `sub_dhfs` consistency rules and the post-migration link check (which is Required only in the immediate aftermath of a migration). Promote others to Required after `migrate-to-multi-dhf` has been exercised on at least one additional project beyond PDLC_DEMO.

### P2.7 — Dry-run gate for PDLC_DEMO

P2's exit criterion is **a passing dry-run** of the migration action on a clean PDLC_DEMO working tree. Concretely:

1. The user checks out the PDLC_DEMO branch that will host task 007's P2 output. Working tree is clean (`git status` shows no changes).
2. The user runs:
   ```
   /medtech-docs migrate-to-multi-dhf pca-device
   ```
   with no `--apply` flag.
3. The action prints a dry-run report that must satisfy every gate below:

| Gate | Target |
|---|---|
| Preconditions section | All lines report `yes` / valid |
| File moves section | Total files moved is in the range **60–90** (PDLC_DEMO currently has an estimated 70-something files under the five per-DHF top-level folders; outside this range indicates either a scan bug or unexpected content drift) |
| Cross-link rewrites section | Total rewrites in the range **30–60**; zero `newly-broken` links in the post-rewrite simulation |
| `project.yml` diff section | Exactly one new `sub_dhfs` entry with `path: pca-device`; `topology: multi-sub-dhf` added under `project:` |
| Blast radius section | Numbers consistent with the file-moves and rewrites tables above; `estimated review time` is `< 5 minutes` |
| Errors | Zero hard errors; warnings are acceptable only if flagged as `pre-existing` |
| Next step hint | Prints the `--apply` command verbatim |

4. A human reviews the report in under five minutes and either approves it (P2 done, move on to P3) or files a finding against the sweeper / validator / action logic (P2 stays open).

When the gate passes, P2 is **done** and task 007 advances to **P3 — `/strategy` topology awareness**. The actual migration does **not** happen at this point; it runs in **P6 — PDLC_DEMO migration (live fire)** after P3, P4, and P5 have landed topology-awareness in the consuming skills.

## Phase P3 — /strategy Topology Awareness

> **⚠️ Phase status under Architectural Pivot (2026-04-13):** Simplified. There is no topology branching in `/strategy` — it always writes to `dhfs/<name>/design-controls/plans/`. What survives: **domain registry changes (P3.1), tag-scope convention (P3.2) including `sub-dhf=<leaf>` resolution from Q1, scan/assemble sub-DHF iteration (P3.3/P3.4), transition of existing task 006 tag blocks (P3.8), best-practices updates (P3.9), exit gate (P3.10)**. What's moot: any section discussing "in `single-dhf` mode, do X / in `multi-sub-dhf` mode, do Y" — the single-dhf branch is deleted; the multi-sub-dhf branch is the only path and runs uniformly with N=1 or N>1.


**Status**: Draft — pending review.

### P3.0 — Overview

Phase P3 designs the changes required to make the `/strategy` skill topology-aware. Today, the strategy skill's Domain Registry hardcodes eight output paths under `docs/project/design-controls/...` (plus one at the repo root). Those paths are correct for a `single-dhf` project but wrong for `multi-sub-dhf`: a multi-component ecosystem needs a regulatory strategy **per sub-DHF** (different pathways, different predicates, different 510(k)s) and an architecture strategy **per sub-DHF** (different platforms). P3 defines how the skill resolves output paths through `project.yml`, how the `<!-- STRATEGY CONTENT -->` tag grows an optional `sub-dhf=<name>` scope key, and how existing strategy briefs transition to per-sub-DHF homes.

P3 is **design-only**. No edits land in the real `.claude/skills/strategy/SKILL.md` or its `agents/` prompts during this phase — the drafts below are embedded in this task doc as the authoritative specification, ready to be applied in a later implementation phase. Phase P3 depends strictly on P1 (topology model, `sub_dhfs[].path` schema, shared-vs-per-DHF rule) and P2 (the `migrate-to-multi-dhf` action that moves the existing strategy briefs into their new homes). P3 does not contradict either and does not move files itself — it specifies how `/strategy` consumes the post-migration layout.

P3 operationalizes the three prerequisite decisions from the "Phase P3 Prerequisites" block below: **Q1** (short-form `sub-dhf=<value>` resolution via last-segment lookup), **Q2** (plan-time read for `/tracker`, consumed indirectly here via the `migrate-to-multi-dhf` dry-run), and **Q3** (each skill re-parses `project.yml` independently — no cross-skill helpers). Every action spec below assumes direct `project.yml` reads.

Backward compatibility is non-negotiable: in `single-dhf` mode, the strategy skill must behave exactly as it does today — same output paths, same tag format, same scan report, same assemble behavior. Topology-awareness is purely additive; `sub-dhf=<name>` in a tag on a `single-dhf` project is silently ignored.

The P3 exit gate is that `/strategy scan`, `/strategy assemble <domain>`, and `/strategy domains` would produce correct reports on PDLC_DEMO in both the current `single-dhf` state and in a **simulated** `multi-sub-dhf` state (derived from the P2 dry-run output), without requiring the real migration to have run yet. Exit detail is in P3.10.

### P3.1 — Domain Registry changes (drafted SKILL.md edit)

The existing Domain Registry table in strategy SKILL.md has a single `Output Path` column. Replacement:

```markdown
## Domain Registry

Each domain has a key, scope, shared/per-DHF output location, template, and list of formal plans it informs. **Scope** determines routing in `multi-sub-dhf` topology:

- `shared` — one strategy doc for the entire project, at the shared strategies location, in both topologies
- `per-dhf` — in `single-dhf` mode, one strategy doc at the legacy path (backward-compatible); in `multi-sub-dhf` mode, one strategy doc per sub-DHF that has tagged content, under `docs/project/dhfs/<path>/...`

| Domain Key | Domain Name | Scope | Shared Location (single-dhf legacy path) | Per-DHF Location (relative to `dhfs/<path>/`) | Template | Plans Informed |
|-----------|-------------|-------|-------------------------------------------|------------------------------------------------|----------|----------------|
| `regulatory` | Regulatory | per-dhf | `docs/project/design-controls/plans/regulatory-strategy.md` | `design-controls/plans/regulatory-strategy.md` | `regulatory-strategy.md` | 510(k), PCCP, Q-Sub, LMR |
| `architecture` | Architecture | per-dhf | `docs/project/design-controls/architecture/architecture-strategy.md` | `design-controls/architecture/architecture-strategy.md` | `default-strategy.md` | SAD, SRS, cybersecurity plan |
| `development` | Development | per-dhf | `docs/project/design-controls/plans/development-strategy.md` | `design-controls/plans/development-strategy.md` | `default-strategy.md` | SDP, Config Mgmt Plan |
| `testing` | Testing & Validation | per-dhf | `docs/project/design-controls/vnv/testing-strategy.md` | `design-controls/vnv/testing-strategy.md` | `default-strategy.md` | V&V Plan, test protocols, usability plan |
| `risk` | Risk | per-dhf | `docs/project/design-controls/risk-management/risk-strategy.md` | `design-controls/risk-management/risk-strategy.md` | `default-strategy.md` | Risk Mgmt Plan, FMEA, risk-benefit analysis |
| `postmarket` | Post-Market | per-dhf | `docs/project/design-controls/plans/postmarket-strategy.md` | `design-controls/plans/postmarket-strategy.md` | `default-strategy.md` | Maintenance Plan, PMS Plan, LMR, PCCP tracking |
| `commercial` | Commercial | shared | `docs/project/strategies/commercial-strategy.md` | — (shared only) | `default-strategy.md` | Go-to-market plan, business case, market expansion |
| `operations` | Operations & Tooling | shared | `docs/project/strategies/operations-strategy.md` | — (shared only) | `default-strategy.md` | Project management plan, skill roadmap, team onboarding |

**Scope rationale:**

- `regulatory`, `architecture`, `development`, `testing`, `risk`, `postmarket` → **per-dhf**. Each sub-DHF has its own filing, its own platform, its own V&V plan, its own ISO 14971 risk file, its own PMS plan. A platform-level sub-DHF like `cloud-suite` also carries its own per-DHF strategies (distinct from its child sub-DHFs).
- `commercial`, `operations` → **shared**. Commercial strategy spans the portfolio (a company decides go-to-market across products, not per component). Operations strategy is the team's tooling and ways-of-working — project-wide by definition.

**Shared location in both topologies**: shared-scope strategy docs live at `docs/project/strategies/<domain>-strategy.md` in both `single-dhf` and `multi-sub-dhf` projects. In v1, this means `commercial-strategy.md` relocates from `docs/project/input-analysis/market-research/` to `docs/project/strategies/`, and `operations-strategy.md` relocates from the repo root to `docs/project/strategies/`. The relocation is handled by `medtech-docs migrate-to-multi-dhf` (P2) consulting this registry — the strategy skill itself never moves files.

**Output path resolution algorithm** (used by `assemble`, `init`, `domains`, `validate`, `diff`):

1. Read `project.topology` from `project.yml`. If absent, treat as `single-dhf`.
2. If `topology == single-dhf`: output path = `Shared Location` column value (legacy path). Unchanged behavior.
3. If `topology == multi-sub-dhf` and scope is `shared`: output path = `Shared Location` column value.
4. If `topology == multi-sub-dhf` and scope is `per-dhf`: one output path per sub-DHF that has tagged content for this domain, at `docs/project/dhfs/<sub_dhfs[i].path>/<Per-DHF Location>`.

**Backward compatibility**: on a `single-dhf` project (the common case today), the resolution returns the legacy path for every domain — every existing path is preserved verbatim. No project needs to migrate to benefit from P3.

### P3.2 — Tag convention update (drafted SKILL.md edit)

The existing Tag Convention section is extended. Replacement insert (added beneath the current "Format rules" list, before "Block boundary"):

```markdown
**Sub-DHF scoping (multi-sub-dhf topology):**

In a `multi-sub-dhf` project, the tag may include an optional `sub-dhf=<name>` key to route the block to a specific sub-DHF's strategy doc:

    <!-- STRATEGY CONTENT: regulatory, sub-dhf=pca-device, classification, jurisdiction -->

**Parsing rule**: after splitting the tag values on commas and trimming whitespace, any value containing `=` is parsed as a `key=value` pair; all other values are topics. The only recognized key in v1 is `sub-dhf`. Unknown keys are flagged as warnings by the scanner and ignored.

**Resolution (Q1 decision, 2026-04-13)**: `<name>` is the **short form** — the last path segment of a `sub_dhfs[].path` entry. The scanner resolves `<name>` by scanning `project.sub_dhfs[]` for a single entry whose `path` equals `<name>` (top-level sub-DHFs) or ends in `/<name>` (nested sub-DHFs). Uniqueness is enforced upstream by `medtech-docs add-sub-dhf`, so a successful resolution is always unambiguous.

**Multi-target routing**: the value may be comma-free but internally multi-valued by using a `|`-separated list inside the value, e.g., `sub-dhf=pca-device|drug-library-manager`. The block is copied (not split) to each resolved sub-DHF's strategy doc. Use case: a cross-cutting decision (e.g., a cybersecurity architecture call) that applies to two components. Whitespace around names is tolerated.

**Scope defaulting** (when `sub-dhf=` is absent):

| Topology | Domain scope | Default routing |
|---|---|---|
| `single-dhf` | any | Legacy single output path — `sub-dhf=` key (if present at all) is silently ignored. |
| `multi-sub-dhf` | `shared` | Shared output path. The `sub-dhf=` key is **forbidden** on shared domains; scanner warns `"shared domain '<domain>' cannot be scoped to a sub-DHF; ignoring sub-dhf=<name>"` and routes to shared anyway. |
| `multi-sub-dhf` | `per-dhf` | Routes to the **primary sub-DHF** — defined as the **first entry** in `project.sub_dhfs[]` (see P3.8 for the rationale). Scanner flags the implicit routing in its report so authors can add explicit scope if they meant a different sub-DHF. |

**Validation errors**:

| Condition | Severity | Message |
|---|---|---|
| `sub-dhf=<name>` where `<name>` matches zero entries in `project.sub_dhfs[]` | error | `"unknown sub-dhf '<name>' in task NNN. Valid short names:\n  <name1>\n  <name2>\n  ..."` (alphabetical) |
| `sub-dhf=<name>` resolves to multiple entries | internal error | `"short name '<name>' resolves to multiple sub-DHFs — project.yml is invariant-violating; add-sub-dhf should have prevented this"` |
| `sub-dhf=<name>` on a shared-scope domain | warning | see above, routed to shared |
| Unknown key=value pair (e.g., `foo=bar`) | warning | `"unknown tag key 'foo' in task NNN; ignoring"` |
```

**Before/after examples** (drawn from task 006, which currently holds the only STRATEGY CONTENT blocks in the project):

Before (task 006, today — single-dhf world):

    <!-- STRATEGY CONTENT: architecture, modules, samd-split, platform -->
    <!-- STRATEGY CONTENT: regulatory, classification, jurisdiction, filing-sequence -->

After (post-migration, multi-sub-dhf world — explicit scope):

    <!-- STRATEGY CONTENT: architecture, sub-dhf=pca-device, modules, samd-split, platform -->
    <!-- STRATEGY CONTENT: regulatory, sub-dhf=pca-device, classification, jurisdiction, filing-sequence -->

After (post-migration, relying on default routing — also valid, because `pca-device` is the primary sub-DHF per P3.8):

    <!-- STRATEGY CONTENT: architecture, modules, samd-split, platform -->
    <!-- STRATEGY CONTENT: regulatory, classification, jurisdiction, filing-sequence -->

Cross-cutting example (a hypothetical cybersecurity block affecting two sub-DHFs):

    <!-- STRATEGY CONTENT: architecture, sub-dhf=pca-device|drug-library-manager, cybersecurity, shared-secrets -->

### P3.3 — `scan` action changes (drafted SKILL.md edit)

The existing `scan` action spec is amended. Changes:

**New Step 0 — Topology read** (inserted before the current Step 1):

```markdown
0. Read `project.yml`. Record:
   - `project.topology` (default `single-dhf` if absent)
   - `project.sub_dhfs[]` as a list of `{path, short_name}` pairs, where `short_name` is the last path segment
   If topology is `multi-sub-dhf` and `sub_dhfs` is empty or missing, fail with: _"project.yml declares topology: multi-sub-dhf but has no sub_dhfs entries; run /medtech-docs add-sub-dhf first"_.
```

**Step 4d — extended tag parsing** (replaces current Step 4d):

```markdown
d. Parse the tag values. Split on commas, trim whitespace. First value = domain key. For each remaining value: if it contains `=`, parse as `key=value` and place into a scope map (only `sub-dhf` is recognized in v1); otherwise append to the topics list. Resolve `sub-dhf=<name>` against `project.sub_dhfs[]` per the rules in the Tag Convention section. Record the resolved list of target sub-DHFs (or `shared`, or `implicit-primary`).
```

**Step 6 — extended validation** (extends current Step 6):

```markdown
6. Flag issues:
   - (existing) unrecognized domain, empty tag
   - `sub-dhf=<unknown>` → error with alphabetical list of valid short names
   - `sub-dhf=` on a shared-scope domain → warning, route to shared
   - Unknown `key=value` tag value → warning, ignore
   - In `single-dhf` mode, presence of `sub-dhf=` → info (ignored, but mention so authors aren't surprised later)
```

**Step 7 — report format changes**:

- Add a new column **`Scoped To`** to the Strategy Content Sources table. Values: `shared`, `<short-name>`, `<short1>|<short2>` for multi-target, `implicit (primary: <short-name>)` for per-dhf domains missing an explicit scope, or `—` for shared domains.
- In `multi-sub-dhf` mode, the table is followed by a **per-sub-DHF grouping** — a secondary breakdown listing, for each sub-DHF, which domains and tasks contribute to it. Shared-scope content is listed under a `(shared)` pseudo-group at the end.

**Report format — single-dhf** (unchanged from today, except the new `Scoped To` column which shows `—` for all rows):

```
Strategy Content Sources

| Task | Section | Domain | Scoped To | Topics | Subsections | Status | Last Modified |
|------|---------|--------|-----------|--------|-------------|--------|---------------|
| 006 — Architecture & Regulatory | Regulatory Strategy | regulatory | — | classification, jurisdiction | 4 | active | 2026-04-12 |
| 006 — Architecture & Regulatory | Architecture Strategy | architecture | — | modules, samd-split | 3 | active | 2026-04-12 |

1 task, 7 subsections across 2 domains
```

**Report format — multi-sub-dhf** (new):

```
Strategy Content Sources

| Task | Section | Domain | Scoped To | Topics | Subsections | Status | Last Modified |
|------|---------|--------|-----------|--------|-------------|--------|---------------|
| 006 — Architecture & Regulatory | Regulatory Strategy | regulatory | implicit (primary: pca-device) | classification, jurisdiction | 4 | active | 2026-04-12 |
| 006 — Architecture & Regulatory | Architecture Strategy | architecture | implicit (primary: pca-device) | modules, samd-split | 3 | active | 2026-04-12 |

Per-sub-DHF breakdown:
  pca-device (2 blocks, 7 subsections):
    - regulatory: task 006 (implicit primary routing)
    - architecture: task 006 (implicit primary routing)
  connectivity-adapter: (no content)
  cloud-suite: (no content)
  cloud-suite/dhfs/drug-library-manager: (no content)
  cloud-suite/dhfs/fleet-management: (no content)
  (shared): (no content)

1 task, 7 subsections, 2 domains, 1 of 5 sub-DHFs covered
```

**Backward compatibility**: a task file with no `sub-dhf=` keys continues to scan cleanly in both topologies; in multi-sub-dhf mode it routes via the implicit-primary rule.

### P3.4 — `assemble` action changes (drafted SKILL.md edit)

The existing `assemble` action spec is amended. Changes (numbered against the existing step list):

**New Step 0 — Topology read** (inserted before current Step 1):

```markdown
0. Read `project.yml` for `topology` and `sub_dhfs[]` (same as scan Step 0). Additionally, verify that for every entry in `sub_dhfs[]` the corresponding directory `docs/project/dhfs/<path>/` exists on disk. If any is missing, fail with:
   _"scaffold missing for sub-DHF '<path>'; run `/medtech-docs migrate-to-multi-dhf` or `/medtech-docs add-sub-dhf` first"_.
```

**Step 2 extension — scope-aware grouping**:

```markdown
2. Group blocks by `(domain, scope)` where scope is one of:
   - `shared` — for shared-scope domains and for shared routing
   - `<short-name>` — for per-dhf domains routed (explicitly or implicitly) to that sub-DHF
   Blocks with multi-target scope (`sub-dhf=A|B`) expand into one `(domain, A)` group entry and one `(domain, B)` entry — same content appearing under both scopes.
```

**Step 3 extension — output-path resolution and multi-file writes**:

```markdown
3. For each `(domain, scope)` bucket:
   a. Look up the domain in the registry. Determine the output path via the resolution algorithm in P3.1:
      - `single-dhf` → legacy path, scope is ignored.
      - `multi-sub-dhf` + shared-scope domain → shared output path under `docs/project/strategies/`.
      - `multi-sub-dhf` + per-dhf domain + `scope == <short>` → `docs/project/dhfs/<resolved full path>/<Per-DHF Location>`.
   b. Proceed with the existing template-loading, routing, conflict, VERIFY, and history logic.
   c. **Multi-target metadata**: if the bucket originated from a `sub-dhf=A|B` tag, each output file gets a metadata comment alongside the existing source-traceability comment:
      `<!-- Source: task NNN, multi-target sub-dhf=A|B -->`
      so future readers can see that the same content appears in the peer sub-DHF's strategy.
```

**Step 3f extension — scope-local conflict detection**:

Tier-1 (heading overlap) and Tier-2 (semantic overlap) continue to apply, but only **within a single `(domain, scope)` bucket**. Blocks from the same domain scoped to different sub-DHFs do not conflict — they are intentionally separate documents. The assembler skips cross-bucket pair comparison entirely.

**Assembly History per output file**: each output file maintains its own `## Assembly History` (existing behavior). For multi-target outputs (same content written to two sub-DHFs), both histories receive an entry of the form:

```markdown
### YYYY-MM-DD — assembled by {user name}
- **Added**: Section Name (task NNN, multi-target sub-dhf=A|B)
- ...
```

**Invocation shapes** (extends the current implicit `/strategy assemble [domain]`):

| Invocation | Behavior |
|---|---|
| `/strategy assemble` | Assemble every `(domain, scope)` bucket that has content. In multi-sub-dhf mode this may produce many output files in one run. |
| `/strategy assemble <domain>` | Assemble `<domain>` across every sub-DHF that has content for it (plus the shared bucket if `<domain>` is shared-scope). |
| `/strategy assemble <domain> --sub-dhf <name>` | Assemble `<domain>` for exactly one sub-DHF. Error if `<domain>` is shared-scope. Error if `<name>` is unknown. Convenience shape for targeted regeneration. |

**Error cases** (added to existing error list):

| Condition | Behavior |
|---|---|
| Tag references `sub-dhf=<name>` that is not in `project.sub_dhfs[]` | Abort with the scanner's resolution error message; no files written. |
| `project.topology: multi-sub-dhf` but target sub-DHF directory missing | Abort per Step 0 with scaffold-missing message. |
| `--sub-dhf <name>` passed for a shared-scope domain | `"error: domain '<domain>' is shared-scope; --sub-dhf is not applicable"` |
| `--sub-dhf <name>` passed on a `single-dhf` project | `"error: --sub-dhf requires multi-sub-dhf topology"` |

**Backward compatibility**: in single-dhf mode, the grouping collapses to `(domain, legacy)` and every bucket writes to the legacy Shared Location path — byte-identical to today's behavior for today's projects.

### P3.5 — Other action changes (diff, validate, domains, init, resolve)

These actions all need small topology-aware updates. Bullet-level change list (full redrafts deferred to implementation phase since the edits are mechanical):

- **`diff [domain]`** —
  - Step 0 reads topology (same as scan/assemble).
  - In multi-sub-dhf mode, diff iterates per `(domain, sub-dhf)` bucket and reports New/Modified/Status-changed/Removed per bucket rather than per domain.
  - Output gains a `sub-dhf` column in the per-category lists; the single-dhf output format is unchanged.

- **`validate [domain]`** —
  - Step 0 reads topology.
  - In multi-sub-dhf mode, validation runs per assembled document — one pass per `(domain, sub-dhf)` bucket plus one per shared domain.
  - The universal checks (VERIFY markers, pending reviews, source freshness, Uncategorized) run unchanged per document.
  - The regulatory-specific checks (filing sequence coverage, document applicability, Q-Sub completeness) run once **per sub-DHF's regulatory-strategy.md**.
  - Summary rollup adds a per-sub-DHF pass/fail/warn counter.

- **`domains`** —
  - Step 0 reads topology.
  - In multi-sub-dhf mode, the Strategy Domains table gains a `Sub-DHFs covered` column showing `N of M` (how many sub-DHFs have content for per-dhf domains) and a nested per-sub-DHF status rollup below the table (like the scan per-sub-DHF breakdown).
  - In single-dhf mode the output is unchanged.

- **`init`** —
  - Step 0 reads topology.
  - In multi-sub-dhf mode, `init` creates placeholder briefs for **every `(domain, scope)` combination**:
    - Every shared-scope domain → one brief at the shared strategies path.
    - Every per-dhf domain → one brief **per sub-DHF** at that sub-DHF's per-DHF location.
  - Brief content is unchanged except the brief template gains a short note explaining the `sub-dhf=<name>` scope key and pointing to the Tag Convention section.
  - Idempotency: per-file skip logic unchanged — a brief that already exists at its resolved path is skipped.

- **`resolve [domain]`** —
  - Step 0 reads topology.
  - Phase-1 parallel scan agents are launched **per domain per sub-DHF** in multi-sub-dhf mode (small fan-out increase). Phase 2 (interactive) is unchanged except the per-conflict prompt includes the sub-DHF name in the context block.

### P3.6 — Scanner & assembler subagent prompt updates

The two agent prompts in `.claude/skills/strategy/agents/` need surgical edits. No full rewrites; specified as insert/replace directives for the implementation phase.

**`agents/scanner.md`:**

- **Insert** near the top of the prompt (just after the "Algorithm" or "Scanning logic" section opening) a new paragraph:
  > _"Before scanning task files, read `project.yml` from the repository root. Extract `project.topology` (default `single-dhf`) and `project.sub_dhfs[]`. Build a short-name lookup table mapping each entry's last path segment to its full `path`. The scanner needs this table to resolve `sub-dhf=<name>` keys in tag values."_

- **Replace** the tag-parsing paragraph (currently splits values into domain + topics) with a version that recognizes `key=value` pairs:
  > _"Split tag values on commas and trim whitespace. The first value is the domain key. For each remaining value, if it contains `=`, treat it as `key=value`; otherwise as a topic. In v1, the only recognized key is `sub-dhf`, whose value is a `|`-separated list of short names. Resolve each short name against the lookup table; flag unknown names per the validation rules."_

- **Insert** a new paragraph after the return-format description:
  > _"When returning blocks, each block entry includes a `scoped_to` field: one of `shared`, `<full-path>`, or a list of full paths for multi-target. For per-dhf-scope domains in multi-sub-dhf mode with no explicit `sub-dhf=` key, set `scoped_to` to the first entry's path in `sub_dhfs[]` and mark the block as `implicit_primary: true`."_

**`agents/assembler.md`:**

- **Insert** after the existing preflight (task-gate check, session ID) a new preflight step:
  > _"Read `project.yml`. Extract `project.topology` and `project.sub_dhfs[]`. Abort with a clear error if `topology: multi-sub-dhf` but any listed sub-DHF directory is missing on disk."_

- **Replace** the output-path resolution paragraph (currently reads `{{OUTPUT_PATH}}` template variable) with:
  > _"Resolve the output path via the Domain Registry algorithm. The agent receives `{{DOMAIN_KEY}}`, `{{DOMAIN_NAME}}`, `{{SCOPE}}` (one of `shared`, `<full-sub-dhf-path>`), `{{TEMPLATE_TYPE}}`, `{{TASK_ID}}`, `{{SESSION_ID}}` as template variables. The parent session pre-computes `{{SCOPE}}` and invokes one assembler per `(domain, scope)` bucket — the agent itself never enumerates sub-DHFs."_

- **Insert** after the conflict-detection paragraph:
  > _"Conflict detection compares blocks only within the current `(domain, scope)` bucket. Blocks from the same domain scoped to a different sub-DHF are out of scope for this agent invocation and are never compared."_

- **Insert** in the traceability-comment section:
  > _"If the block carries a multi-target origin (`scoped_to` is a list), the source-traceability comment gains a `, multi-target sub-dhf=<a>|<b>` suffix so the multi-target origin is visible in both peer output files."_

### P3.7 — Handling the transition from existing strategy briefs

PDLC_DEMO already has eight strategy briefs at the legacy paths (generated by `/strategy init` earlier). When `migrate-to-multi-dhf pca-device` runs, those briefs need to land in the right place per the P3.1 scope column. This is a **P2 responsibility** (P2 moves files) but **P3 dictates the destinations**.

- `medtech-docs migrate-to-multi-dhf` consults the strategy skill's Domain Registry (parsing the table in `.claude/skills/strategy/SKILL.md`) to determine which domains are `per-dhf` vs `shared`. Per-dhf briefs are moved into `docs/project/dhfs/pca-device/...` alongside the rest of the single-DHF content. Shared briefs are relocated to `docs/project/strategies/`.
- `docs/project/strategies/` may not yet exist at migration time. Migration creates it as part of the file moves.
- The strategy skill itself never moves files. The shared location `docs/project/strategies/` is **hardcoded in the Domain Registry as the shared location** — it is a convention, not a per-project config, so no new `project.yml` field is needed.

**PDLC_DEMO strategy brief move list** (assuming `migrate-to-multi-dhf pca-device`):

| Current path | Scope | New path |
|---|---|---|
| `docs/project/design-controls/plans/regulatory-strategy.md` | per-dhf | `docs/project/dhfs/pca-device/design-controls/plans/regulatory-strategy.md` |
| `docs/project/design-controls/architecture/architecture-strategy.md` | per-dhf | `docs/project/dhfs/pca-device/design-controls/architecture/architecture-strategy.md` |
| `docs/project/design-controls/plans/development-strategy.md` | per-dhf | `docs/project/dhfs/pca-device/design-controls/plans/development-strategy.md` |
| `docs/project/design-controls/vnv/testing-strategy.md` | per-dhf | `docs/project/dhfs/pca-device/design-controls/vnv/testing-strategy.md` |
| `docs/project/design-controls/risk-management/risk-strategy.md` | per-dhf | `docs/project/dhfs/pca-device/design-controls/risk-management/risk-strategy.md` |
| `docs/project/design-controls/plans/postmarket-strategy.md` | per-dhf | `docs/project/dhfs/pca-device/design-controls/plans/postmarket-strategy.md` |
| `docs/project/input-analysis/market-research/commercial-strategy.md` | shared | `docs/project/strategies/commercial-strategy.md` |
| `operations-strategy.md` (repo root — odd location) | shared | `docs/project/strategies/operations-strategy.md` |

Two of these (commercial, operations) are **not co-located with the other per-DHF content moving into `dhfs/pca-device/`**. P2's file-mover needs a special case (or a generalized scope-lookup) to route them to `docs/project/strategies/` instead of the default `dhfs/pca-device/<same-relative-path>` destination. This is captured here so P2 can pick it up without re-deriving the rule.

After the move, `/strategy scan` and `/strategy assemble` continue to work because the strategy skill resolves paths through the Domain Registry algorithm — the skill never cached the old locations.

### P3.8 — Migration of task 006 tag blocks

Task 006 currently contains two tagged blocks:

    <!-- STRATEGY CONTENT: architecture, modules, samd-split, platform -->
    <!-- STRATEGY CONTENT: regulatory, classification, jurisdiction, filing-sequence -->

Neither carries a `sub-dhf=` scope key. After the migration, should these tags be rewritten to add `sub-dhf=pca-device`?

**Recommendation: do NOT auto-rewrite task tags during migration.** The default-routing rule from P3.2 handles the current task 006 tags cleanly — in multi-sub-dhf mode, per-dhf domains with no explicit scope route to the **primary sub-DHF**, and the primary is `pca-device` because it's the first entry in `project.sub_dhfs[]`. Task 006's blocks continue to flow into `dhfs/pca-device/design-controls/...` without any tag edit. Task authors can optionally add explicit `sub-dhf=<name>` later when they need to target a non-primary sub-DHF.

**Hard rule for "primary sub-DHF"**: **the first entry in `project.sub_dhfs[]`.** This rule is:

- **Deterministic** — array order is stable and author-controlled.
- **Author-controlled** — teams decide the order when they write the manifest (or when `init --topology multi-sub-dhf` collects names), so "primary" is an intentional decision rather than a derived one.
- **Independent of `regulatory` status** — a project may have zero `cleared` sub-DHFs (all in-development) and still need a primary. Using `regulatory: cleared` as the primary selector breaks in that case.
- **Stable across regulatory transitions** — sub-DHFs flip from `in-development` to `cleared` over time; using regulatory status as primary would make primary shift without an explicit author decision.

Rejected alternatives:

- _"Primary is the one with `regulatory: cleared`"_ — fails when no sub-DHF is cleared yet (early projects).
- _"Primary is the largest sub-DHF by file count"_ — non-deterministic and surprising.
- _"No default; require explicit `sub-dhf=` in multi-sub-dhf mode"_ — too heavy a migration cost for projects with many tagged blocks.

This rule is documented in the Tag Convention section of the P3.2 draft.

### P3.9 — Best-practices updates (drafted SKILL.md additions)

New rows added to the strategy skill's Best Practices table. (Existing rows remain; these are additive.)

| Check | How to Verify | Severity |
|-------|--------------|----------|
| Topology-aware assembly | In `multi-sub-dhf` mode, every per-dhf domain with tagged content has at least one assembled strategy doc at a per-sub-DHF output path (i.e., no per-dhf domain content is stranded in the legacy single-dhf location). | Recommended |
| Sub-DHF scope values resolve | Every `sub-dhf=<name>` value in STRATEGY CONTENT tags across all task files resolves to exactly one entry in `project.sub_dhfs[]` (checked via scanner). | Required |
| No scope key on shared domains | No STRATEGY CONTENT tag for a shared-scope domain (`commercial`, `operations`) carries a `sub-dhf=` key. | Required |
| Shared strategies in shared location | In `multi-sub-dhf` mode, `docs/project/strategies/commercial-strategy.md` and `docs/project/strategies/operations-strategy.md` exist and are not `<!-- Status: awaiting-content -->`. | Required if any shared brief exists |
| Shared strategies folder exists | `docs/project/strategies/` directory exists in both topologies. | Recommended |
| Primary sub-DHF documented | When any per-dhf domain relies on implicit primary-sub-DHF routing, the project README or `project.yml` comment block explicitly calls out which sub-DHF is primary. | Recommended |

Existing per-domain "populated" rows are extended to read the output path through the resolution algorithm, so in `multi-sub-dhf` mode the check runs per-sub-DHF rather than at the single legacy location. The check descriptions in the table stay the same wording; only the path lookup changes under the hood.

### P3.10 — Exit gate for P3

P3 is **done** when all of the following hold:

1. **Design drafts complete in this task doc.** Sections P3.0 through P3.10 are drafted and reviewed by the task owner. No real SKILL.md edits have been applied to `.claude/skills/strategy/SKILL.md`, and no real agent-prompt edits have been applied to `agents/scanner.md` or `agents/assembler.md`. All edits are specified in P3.1–P3.6 as ready-to-apply drafts.
2. **Simulated dry-run on PDLC_DEMO (single-dhf).** Running `/strategy scan` and `/strategy assemble architecture` + `/strategy assemble regulatory` on the current (pre-migration) PDLC_DEMO would produce correct output against task 006's existing tags, unchanged from current behavior. This proves backward compatibility.
3. **Simulated dry-run on PDLC_DEMO (multi-sub-dhf).** With a mocked `project.yml` containing `topology: multi-sub-dhf` and the five sub-DHFs from P1.2, `/strategy scan` would produce the per-sub-DHF breakdown report from P3.3 showing task 006's blocks routed to `pca-device` via implicit primary. `/strategy assemble architecture` and `/strategy assemble regulatory` would resolve output paths to `docs/project/dhfs/pca-device/design-controls/architecture/architecture-strategy.md` and `.../plans/regulatory-strategy.md` respectively.
4. **Strategy brief move list (P3.7) aligns with the P2 dry-run output.** Running `medtech-docs migrate-to-multi-dhf pca-device` (dry-run) produces a move plan whose strategy-brief destinations match the P3.7 table verbatim — including the two shared briefs relocating to `docs/project/strategies/`.
5. **No contradictions with P1 or P2.** The P3 draft has been cross-checked against the Topology model (P1.1), the `project.yml` schema (P1.2), and the migration action (P2.3). Any ambiguities discovered are resolved and captured in the "Ambiguities resolved" block below.

When the above hold, **P4 (`/tracker` topology awareness) can start in parallel with P5 (`/best-practices` topology awareness).** Neither P4 nor P5 depends on any real edit to the strategy skill landing first — they depend only on the P3 design being locked so consuming-skill contracts are stable.

### Ambiguities resolved

- **Scope of `architecture` for platform sub-DHFs.** Per P1.1's "Key rule for distinguishing platform content from children," a platform sub-DHF like `cloud-suite` has its own per-DHF `design-controls/architecture/` describing the platform, while each child (e.g., `drug-library-manager`) has its own `design-controls/architecture/` describing the hosted SaMD. P3 treats `architecture` as **per-dhf** for both parent and child — the parent gets its own architecture-strategy.md at `dhfs/cloud-suite/design-controls/architecture/architecture-strategy.md`, and each child gets one at `dhfs/cloud-suite/dhfs/<child>/design-controls/architecture/architecture-strategy.md`. No sharing, no inheritance in v1.
- **Multi-target tag value separator.** Spec'd as `|` (pipe) inside the `sub-dhf=` value rather than comma, because the outer tag is already comma-separated. Using `sub-dhf=A,B` would be ambiguous (is `B` another topic?). `|` is unambiguous and matches common query-string / shell idioms.
- **Shared strategies folder as a convention, not configuration.** `docs/project/strategies/` is hardcoded in the Domain Registry's Shared Location column rather than added as a new `project.yml` field. Rationale: the path is identical across projects, a new config field buys nothing, and Q3 (each skill re-parses `project.yml`) would require every consuming skill to also read a new field. Keeping it as a convention keeps `project.yml` minimal.
- **Primary sub-DHF rule.** Fixed as "first entry in `project.sub_dhfs[]`" per P3.8. Flagged for user review in the next design pass.
- **`sub-dhf=` key on single-dhf projects.** Silently ignored (not warned) in single-dhf mode. Rationale: a project can be authored with explicit scope keys in anticipation of a future migration, and those tags should not produce warnings before migration.

### P4 prerequisite decisions (landed 2026-04-13)

- **`/tracker` does NOT parse strategy's Domain Registry, but DOES read assembled strategy content documents.** _Resolved (refined 2026-04-13)._ Two different reads, don't conflate:
  - **Metadata read (forbidden)**: parsing strategy SKILL.md's Domain Registry table to learn which domains are per-dhf vs shared. The tracker has no need for this.
  - **Content read (expected)**: reading the assembled strategy documents themselves — `dhfs/<name>/design-controls/plans/regulatory-strategy.md`, `dhfs/<name>/design-controls/architecture/architecture-strategy.md`, `docs/project/strategies/commercial-strategy.md`, etc. — to inform what a submission needs. If the regulatory strategy declares "K210345 filing includes PCCP for drug library + UI fixes + cyber patches," the tracker uses that to verify the composition manifest actually pulls in those pieces. Similarly for architecture strategy (system architecture doc tells tracker which sub-DHFs need cyber evidence pulled in for a filing).
  - The tracker's job per the SKILL.md description is "Submission package tracker — build tracker markdown from architecture and regulatory context, render HTML dashboard, update status, assess readiness." The "architecture and regulatory context" is **exactly** the assembled strategy documents. P4 extends this to read those docs from the topology-aware locations (per-sub-DHF in multi-sub-dhf mode, legacy paths in single-dhf mode).
  - Strategy documents are **advisory input** to the tracker; composition manifests are **authoritative**. If they conflict, the composition manifest wins and the tracker flags the gap ("strategy says X, composition says Y, review needed").
- **`/strategy assemble` does NOT trigger `/tracker` refresh.** _Resolved: no._ The two skills stay decoupled. Assemble writes strategy files and returns; tracker reads on next render. Users invoke `/tracker` explicitly when they want a fresh view.
- **Primary sub-DHF rule is a soft convention, not hard-enforced.** _Resolved._ No best-practices rule requiring explicit `sub-dhf=<name>` past a certain sub-DHF count. The convention of "primary = first entry in `project.sub_dhfs[]`" stays as the implicit default, but the agent/skill is allowed to resolve ambiguity using project-specific context. Teams that want a stricter rule document it in their project's `CLAUDE.md` — e.g., "all per-dhf strategy tags must carry explicit `sub-dhf=<name>` once this project has more than two sub-DHFs." This moves the policy from the skill layer to the project layer where it belongs.
- **Is the "primary sub-DHF" rule durable as the project grows past two sub-DHFs?** If PDLC_DEMO later decides `cloud-suite` is the primary, reordering `project.sub_dhfs[]` is a one-line `project.yml` edit but quietly reroutes every implicit-scope block. Consider whether best-practices should require explicit scope on every per-dhf tag once `len(sub_dhfs) > 2` — flag for P5.

## P5 prerequisite decisions (landed 2026-04-13)

- **Stale-manifest detection.** _Resolved: yes._ P5's audit cross-checks composition-manifest mtime against the mtime of each referenced strategy document. If a composition manifest is older than any strategy doc it depends on, the audit flags it as stale. Catches the case where regulatory/architecture strategy was updated but the filing's composition manifest wasn't refreshed to match.
- **P5 audit does NOT call `/tracker assess`.** _Resolved: decoupled._ Best-practices runs its own checks on composition manifests and tracker state without invoking `/tracker` internally. Avoids a dependency loop and lets each skill's checks evolve independently.
- **Unreferenced-sub-DHF check.** _Resolved: Smart Recommended._ Best-practices flags a sub-DHF as unreferenced only if it is missing from every `submissions/<filing>/composition-manifest.md` **and** its `regulatory` status is `in-development` or `cleared`. Sub-DHFs with `regulatory: concept` are skipped because they are explicitly pre-filing. Sub-DHFs with `regulatory: mixed` (platforms like `cloud-suite`) are also skipped at the parent level — the check runs on children individually. Emitted as a Recommended finding, not Required — teams can acknowledge and move on, but the audit surfaces the gap for review.

## Phase P4 — /tracker Topology Awareness

> **⚠️ Phase status under Architectural Pivot (2026-04-13):** Simplified. `/tracker` always reads `dhfs/<name>/...`. No mode branching. What survives: **composition-manifest-as-source-of-truth (P4.2), strategy docs as advisory input (P4.3), action changes (P4.4), tracker markdown schema changes (P4.5), HTML dashboard changes (P4.6), best-practices updates (P4.7), exit gate (P4.8)**. What's moot: any discussion of "how tracker behaves in single-dhf vs multi-sub-dhf mode" — there is only one mode.


**Status**: Draft — pending review.

### P4.0 — Overview

The `/tracker` skill is framed in its SKILL.md as a _submission package tracker_ — its purpose is to build tracker markdown from architecture and regulatory context, render an HTML dashboard, update deliverable status, and assess readiness. Today that framing assumes one DHF and one submission: a single `docs/project/submissions/submission-tracker.md` derived from one System SAD and one regulatory strategy. P4 re-grounds the skill so it can track **multiple submissions**, each composed from **multiple sub-DHFs**, without breaking the single-dhf path.

Topology matters for submission tracking because in a multi-sub-dhf project the question "what deliverables belong in this filing?" is no longer answered by a single DHF's contents. It is answered by a **composition manifest** — the P2.5 template living at `docs/project/submissions/<filing>/composition-manifest.md` — which enumerates which pieces from which sub-DHFs are pulled into the filing. P4 makes composition manifests the tracker's authoritative source of truth in multi-sub-dhf mode. Manifests are the only input that decides what's _in_ a filing.

Strategy documents (produced by the topology-aware `/strategy` skill in P3) feed in as **advisory input**. Regulatory strategy tells the tracker what the filing _should_ contain (PCCP scope, cybersecurity posture, reuse decisions); architecture strategy tells it which sub-DHFs need cybersecurity/interface/risk evidence pulled in. The tracker mines these for implied deliverables and uses them to enrich the `assess` readiness check — but never to override or rewrite a composition manifest. If strategy and manifest disagree, composition wins and the tracker flags the gap.

The tracker also grows a new dimensional axis: **one view per sub-DHF** (what each sub-DHF has produced, across all filings it contributes to) plus a **roll-up view per filing** (composition across sub-DHFs, with readiness per sub-DHF). A project can have multiple submissions in flight simultaneously — e.g., `K210345-pca-device` (already cleared), `pccp-pp3500-2026` (future PCCP for drug-library-manager plus UI fixes), and `qsub-pp3500-2026` (pre-sub questions). The new dashboard treats submissions as first-class.

**P4 is design-only.** No edits land in `.claude/skills/tracker/SKILL.md` or `scripts/render.py` in this phase — the output of P4 is drafted SKILL.md content and a scoped list of render.py changes, both captured inside this task doc. **Exit gate**: a reviewer can read P4.0–P4.8 and sign off that the tracker's topology-aware behavior is fully specified before implementation begins. P4 can run in parallel with P5 (best-practices) since they have no dependency on each other; both feed P6 (PDLC_DEMO live-fire migration).

### P4.1 — Topology-aware tracker concept model

**Before (single-dhf).** One DHF, one submission, one `submission-tracker.md`. Columns describe deliverables from that single DHF. `build` reads a flat set of inputs: the System SAD under `docs/project/design-controls/architecture/`, the regulatory strategy under `docs/project/design-controls/plans/regulatory-strategy.md`, and FDA guidances under `docs/external/fda-guidance/`. The tracker has no concept of "which DHF does this deliverable come from" because the answer is always the same.

**After (multi-sub-dhf).** N sub-DHFs, M submissions (filings), and one composition manifest per filing. The authoritative list of tracked deliverables is computed by **walking composition manifests**. A deliverable is defined by a triple: the submission it belongs to, the source sub-DHF it lives in, and the deliverable type. The tracker markdown table becomes a flattened view of this map, with one row per (submission, source sub-DHF, deliverable) tuple.

**Submissions become first-class.** The tracker in multi-sub-dhf mode owns a _set_ of submissions, not just one. PDLC_DEMO's near-term shape is three in-flight submissions: `K210345-pca-device` (cleared; tracker shows as reference/baseline), `pccp-pp3500-2026` (upcoming PCCP for drug-library-manager + UI fixes + cyber patches), `qsub-pp3500-2026` (pre-sub questions). Each has its own composition manifest and its own readiness state.

**Column layout before/after.**

Before (Parts 1–3):

```
| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
```

After (Parts 1–3, multi-sub-dhf mode):

```
| # | Submission | Source Sub-DHF | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence | Provenance |
```

In single-dhf mode the `Submission`, `Source Sub-DHF`, and `Provenance` columns are omitted and the layout is exactly as today. Existing columns (`Deliverable`, `Owner` via Scope/Effort/Phase, `Status`, `Evidence`, etc.) are preserved verbatim. Part 4 (engineering prerequisites) gains `Source Sub-DHF` in multi-sub-dhf mode; all other columns unchanged.

### P4.2 — Composition manifest as source of truth

In multi-sub-dhf mode, `/tracker build` and `/tracker render` derive the set of tracked deliverables from composition manifests. The algorithm:

1. **Read topology from `project.yml`.** If `project.topology` is unset or `single-dhf`, behave exactly as today (backward compatible path; skip the rest of this section).
2. **Enumerate submissions.** Glob `docs/project/submissions/*/composition-manifest.md`. Each match is one submission; the folder name is the filing ID. Cross-check against `project.sub_dhfs[].filing` entries — missing folders are flagged as warnings by `assess`, extra folders are tracked without warning (manual pre-sub folders are allowed).
3. **Parse each manifest.** Use the P2.5 template contract. Extract:
   - The filing ID and type from the `## Filing identification` section.
   - Every row of the `## Included pieces` table as a `(sub_dhf_path, content_type, rationale, status)` tuple.
   - Every row of `## Excluded pieces` (for provenance tracking — excluded pieces appear in `status --include-untracked`).
   - Every entry in `## Cross-references to source sub-DHFs` (for dependency walking).
4. **Build the internal deliverables map.** Keyed by `(submission, sub_dhf, deliverable_type)`, each entry records provenance (`C` = composition manifest), source sub-DHF path, and the expected project location (derived from the sub-DHF path + the standard folder convention).
5. **Flatten to markdown rows.** One row per map entry, grouped by submission (H2), then by source sub-DHF (H3). Part 4 engineering prerequisites are grouped the same way — per submission, per sub-DHF — because an engineering capability can gate deliverables in more than one filing.
6. **Write `submission-tracker.md`.** The file's structure becomes: Context & Sources (now listing the set of composition manifests and the set of strategy docs read), then one H2 section per submission (`## Submission: <filing-id>`) containing the usual Part 1–4 tables, then a final `## Roll-up` section with the cross-submission summary.

**Un-tracked sub-DHFs.** A sub-DHF that exists in `project.sub_dhfs[]` but is not referenced by any composition manifest's `Included pieces` table is **un-tracked** by default — its deliverables do not appear in the tracker markdown at all. This is intentional: the tracker's job is submission packaging, not DHF inventory. `/tracker status --include-untracked` (new filter) surfaces un-tracked sub-DHFs for visibility with a one-line note per sub-DHF: _"<name>: not referenced by any composition manifest."_

**Authoritative vs advisory precedence.** When a strategy document implies a deliverable that the composition manifest does not list, the tracker **does not** add a row — strategy never writes to the deliverables map. Instead `assess` emits a warning (P4.3). The composition manifest is the only input allowed to mutate the deliverables map.

**Error handling.**

| Condition | Tracker behavior |
|-----------|------------------|
| Manifest file missing for a `project.sub_dhfs[].filing` entry | `build` warns, `assess` flags as Required gap. Tracker still renders other submissions. |
| Manifest parses but `## Included pieces` table is empty | `build` warns; submission renders with zero deliverables and an explicit "empty composition" badge in the HTML. |
| Manifest references a sub-DHF path not in `project.sub_dhfs[]` | `build` errors for that row (skipped from the map), `assess` flags as Required gap. Other rows from the same manifest still process. |
| Two manifests claim the same (sub-DHF, deliverable) tuple with contradictory status | `build` keeps both rows (one per submission — they are different rows by submission key), no error. Contradictions are allowed: the same deliverable may legitimately participate in two filings. |
| Malformed markdown table (column count mismatch) | `build` errors loudly, names the file and line, refuses to write the tracker to avoid partial state. |

### P4.3 — Strategy documents as advisory input

The tracker reads assembled strategy documents at the locations produced by P3's topology-aware strategy skill. In multi-sub-dhf mode those locations are:

- **Per-dhf domains** (regulatory, architecture, vnv, risk-management, development where per-dhf): `dhfs/<path>/design-controls/plans/regulatory-strategy.md`, `dhfs/<path>/design-controls/architecture/architecture-strategy.md`, `dhfs/<path>/design-controls/vnv/testing-strategy.md`, `dhfs/<path>/design-controls/risk-management/risk-strategy.md`.
- **Shared domains** (commercial, operations, and the cross-cutting post-market strategy per the P3 Domain Registry): `docs/project/strategies/commercial-strategy.md`, `docs/project/strategies/operations-strategy.md`, `docs/project/strategies/post-market-strategy.md`.

For each submission in the tracker, the tracker looks up the relevant strategy docs and extracts advisory signals:

| Submission lookup | Strategy doc read | Signals extracted |
|-------------------|-------------------|-------------------|
| Regulatory scope for a filing | Lead sub-DHF's `design-controls/plans/regulatory-strategy.md` (lead = the sub-DHF whose `filing` matches the submission ID) | PCCP inclusion flag, cybersecurity framework (e.g., IEC 81001-5-1 + SBOM), reuse of prior 510(k), predicate device, pre-sub questions |
| Architecture coverage | Every referenced sub-DHF's `design-controls/architecture/architecture-strategy.md` | Interfaces (HL7/FHIR/DICOM), module boundaries, cybersecurity attack surface, AI/ML components |
| Risk coverage | Every referenced sub-DHF's `design-controls/risk-management/risk-strategy.md` | Hazard analysis scope, RMF, residual-risk policy |
| VnV coverage | Every referenced sub-DHF's `design-controls/vnv/testing-strategy.md` | Test strategies implying specific V&V deliverables (e.g., clinical usability test → HFE report) |
| Cross-cutting (commercial, operations, post-market) | Shared-location strategies under `docs/project/strategies/` | Post-market surveillance plan required, distribution plan, labeling strategy |

**From signals to implied deliverables.** Each extracted signal maps to an expected deliverable type. Examples:

- Regulatory strategy declares _"K210345 filing includes PCCP for drug library updates"_ → tracker expects a **PCCP narrative** deliverable in that filing's Part 2.
- Regulatory strategy declares _"cybersecurity per IEC 81001-5-1 plus SBOM plus signed updates"_ → tracker expects a **cybersecurity assessment**, **SBOM**, and **software update authentication statement** from each sub-DHF referenced by the composition manifest.
- Architecture strategy declares _"HL7 v2.5 inbound plus optional FHIR R4"_ → tracker expects **interface specification** deliverables (one per protocol) in the contributing sub-DHF.
- Post-market strategy declares _"active device registry for first 100 deployments"_ → tracker expects a **post-market surveillance plan** deliverable at the shared project level.

The signal-to-deliverable mapping table lives in the tracker SKILL.md (drafted here in P4.7) so reviewers can audit it and so it can evolve without code changes.

**`assess` gap check.** After building the deliverables map from manifests, `assess` compares the map against the strategy-implied set. For each implied deliverable that is **not** present in the map, it emits a warning of the form:

```
[advisory] <submission>: strategy implies <deliverable> (source: <strategy-doc>#<section>), composition manifest does not include it.
```

Warnings are non-blocking — they are advisory and the project may have legitimate reasons to exclude a deliverable (e.g., reuse from a prior filing). Warnings appear in `/tracker assess` output, in the HTML dashboard as yellow badges next to the submission, and are counted in the readiness summary.

**Never rewrites manifests.** The tracker's strategy read is strictly read-only. Authoring composition manifests stays a human decision in all cases. The tracker will suggest additions via `assess` but will not edit `composition-manifest.md` files.

**Best-effort reads.** If a strategy doc is missing, or is still the `<!-- Status: awaiting-content -->` placeholder produced by `/strategy assemble` on an empty domain, the tracker **skips silently** and emits an informational note in `assess`:

```
[info] <submission>: no advisory signals extracted from <strategy-doc> (file missing or awaiting content).
```

This avoids coupling the tracker's usefulness to the completeness of every strategy doc. The tracker always renders — even on a project with zero strategy content — using whatever composition manifests exist.

### P4.4 — Action changes

For each tracker action, only the delta in multi-sub-dhf mode is specified. Single-dhf behavior is unchanged unless noted.

- **`init`**
  - Single-dhf: unchanged.
  - Multi-sub-dhf: detects `project.topology: multi-sub-dhf` and scaffolds the `docs/project/submissions/` layout with one subfolder per `project.sub_dhfs[].filing` entry (where `filing` is defined). Creates a `composition-manifest.md` stub in each — populated from the P2.5 template — with the filing identification block pre-filled and the `## Included pieces` table empty. Does **not** create deliverable rows yet (that is `build`'s job). Does **not** overwrite existing manifests. Adds the multi-sub-dhf CLAUDE.md rule (a second paragraph noting that manifests, not the tracker, define what is in a filing). Idempotent.
- **`build [topic]`**
  - Single-dhf: unchanged.
  - Multi-sub-dhf: reads `project.yml` topology. For each submission folder, walks the composition manifest per P4.2 to enumerate deliverables, then reads the advisory strategy docs per P4.3 to enrich the expected deliverable list. Writes the tracker markdown grouped by submission. Composition-sourced rows are marked `C` in the `Provenance` column; strategy-advisory rows (if ever materialized — normally they stay as warnings) would be marked `S`; rows present in both are marked `B`. By default only `C` rows appear in the table; `S` rows surface only in `assess` output.
  - `[topic]` arg still filters by category (e.g., `cybersecurity`) within each submission.
  - On conflict between existing tracker rows and freshly computed ones (e.g., user edited `Status` manually), `build` preserves user-set `Status` and `Evidence` values keyed by the row ID and reports preserved fields in its summary.
- **`render`**
  - Single-dhf: unchanged.
  - Multi-sub-dhf: the HTML dashboard gains a **Submission selector** dropdown at the top. Default view is the cross-submission roll-up (see P4.6). Drill-in views per submission and per sub-DHF are new. `render.py` changes are scoped in P4.6 — no Python drafted here.
- **`update <id> <field> <value>`**
  - Mechanically unchanged. IDs in multi-sub-dhf mode are prefixed with the submission ID to avoid collisions across filings: e.g., `K210345-C1a` instead of `C1a`, `pccp-pp3500-2026-SW3b` instead of `SW3b`. Single-dhf IDs stay bare. `update` accepts either form in single-dhf mode; in multi-sub-dhf mode, bare IDs are rejected with an error naming the set of matching prefixed IDs so the user can disambiguate.
- **`status [filter]`**
  - New filter dimensions: `--submission <filing>` (restrict to one filing), `--sub-dhf <name>` (restrict to deliverables sourced from one sub-DHF; short name per P3.Q1), `--include-untracked` (show un-tracked sub-DHFs as one line per sub-DHF).
  - Existing filters (`filing`, `engineering`) continue to work across all submissions unless combined with `--submission`.
  - Output format gains a per-submission section when multi-sub-dhf, falling back to the current single-section format in single-dhf mode.
- **`assess`**
  - Gains the strategy-vs-composition gap check from P4.3.
  - Gains per-submission readiness scoring: `complete` / `in-progress` / `blocked`, with a per-sub-DHF breakdown (which sub-DHFs contribute `Done` vs `Not Started` evidence to this filing).
  - Output format: one readiness block per submission, strategy-advisory gaps listed as warnings, composition-level errors (missing manifest, bad references) listed as Required gaps. Keeps the current "files exist but status says Not Started" check unchanged.

### P4.5 — Tracker markdown schema changes

The current Parts 1–3 table header (from the SKILL.md Markdown Table Structure section) is:

```
| # | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence |
```

In multi-sub-dhf mode it becomes:

```
| # | Submission | Source Sub-DHF | Deliverable | Scope | Effort | Phase | FDA Reference | Project Location | Status | Evidence | Provenance |
```

The current Part 4 header is:

```
| # | Prerequisite | Scope | Effort | Phase | Status | Gates |
```

In multi-sub-dhf mode it becomes:

```
| # | Submission | Source Sub-DHF | Prerequisite | Scope | Effort | Phase | Status | Gates |
```

**New column definitions (drafted to match the SKILL.md Column Definitions voice).**

| Column | Purpose | How to assign |
|--------|---------|---------------|
| **Submission** | Which filing this deliverable belongs to. Matches a folder under `docs/project/submissions/` and the filing ID in the composition manifest's `## Filing identification` section. | Populated by `/tracker build` from the composition manifest path. Values: filing IDs like `K210345-pca-device`, `pccp-pp3500-2026`, `qsub-pp3500-2026`. Nullable only in single-dhf mode (column absent). |
| **Source Sub-DHF** | Short name of the sub-DHF the deliverable lives in. Matches the leaf segment of a `project.sub_dhfs[].path`. | Populated by `/tracker build` from the `## Included pieces` table's sub-DHF column. Values: short names like `pca-device`, `drug-library-manager`, `cloud-suite`. Nullable only in single-dhf mode (column absent). |
| **Provenance** | Whether the deliverable was derived from the composition manifest (`C`), from strategy advisory signals (`S`), or from both (`B`). Default is `C` since strategy-only deliverables live in `assess` warnings, not the table. | Populated by `/tracker build`. Shown as a one-letter badge in the HTML. |

**Preserved columns.** `#`, `Deliverable`, `Scope`, `Effort`, `Phase`, `FDA Reference`, `Project Location`, `Status`, `Evidence` retain their exact meanings from the current SKILL.md. Per-module letter suffixes (`a`/`b`/`c`) remain valid but become redundant once `Source Sub-DHF` is present — new rows in multi-sub-dhf mode prefer the explicit `Source Sub-DHF` column and drop the letter suffix; legacy rows keep their suffixes for historical traceability.

**Valid values (additions).**

- `Submission`: any filing ID that corresponds to a folder under `docs/project/submissions/`. No closed list.
- `Source Sub-DHF`: any short name whose leaf matches a `project.sub_dhfs[].path` leaf. No closed list.
- `Provenance`: `C`, `S`, `B`.

### P4.6 — HTML dashboard changes

Conceptual UI changes needed in `render.py` (no Python drafted — listed as function/section scope only for implementation):

- **Submission selector dropdown** at the top of the page. Options: _Roll-up (all submissions)_ (default), one entry per submission, one entry per sub-DHF (prefixed `Sub-DHF: `). State persists in a URL hash so deep links work.
- **Roll-up view** (default in multi-sub-dhf mode): one card per submission showing filing ID, filing type, per-sub-DHF readiness bars (stacked horizontal bar: Done/Partial/In Progress/Not Started counts), and a badge count of advisory gaps. Clicking a card drills into that submission's detailed table.
- **Per-submission drill-in**: the current Parts 1–4 tables, scoped to that submission, with the new `Source Sub-DHF` and `Provenance` columns visible. Existing 4-way filter (Status × Scope × Phase × Part) continues to work within the scope of the selected submission.
- **Per-sub-DHF drill-in**: all deliverables sourced from that sub-DHF, across every submission it contributes to, with the `Submission` column visible. Useful for DHF owners who want to see "what has my sub-DHF actually shipped."
- **Sub-DHF filter**: a multi-select control in the filter bar that restricts the currently visible table to rows sourced from selected sub-DHFs. Only appears in multi-sub-dhf mode.
- **Readiness indicators per row**: in addition to the existing status badge, composition-vs-strategy gaps shown as a small yellow chip (`advisory gap`) when the row's submission has unresolved advisory warnings relevant to this row's sub-DHF.
- **Advisory gaps panel**: a collapsible section below each submission drill-in listing the `assess` warnings for that filing, one line per warning, with the source strategy doc linked.
- **Backward compatibility**: in single-dhf mode the dashboard renders exactly as today — no submission selector, no new columns, no per-sub-DHF view. The topology check is a single conditional at the top of the render pipeline.

**`render.py` scope of change (by function/section, not code).** The following parts of `render.py` assume single-dhf paths and will need topology-aware logic:

| Area | Change needed |
|------|---------------|
| Markdown parser entry point | Branch on `project.topology`. In multi-sub-dhf, parse H2 submission sections first, then H3 sub-DHF sections, then Part tables within each. |
| Row data class / dict | Add `submission`, `source_sub_dhf`, `provenance` fields. Fields are `None` in single-dhf mode. |
| Summary card builder | In multi-sub-dhf, produce one row of cards per submission (plus a grand total row). |
| Filter bar HTML generator | Add submission selector and sub-DHF multi-select; guard with topology check. |
| Table renderer | Emit the two new columns when topology is multi-sub-dhf. |
| Help row lookup | Key help content by `(submission, id)` instead of just `id` to prevent collisions across filings. |
| Assess-warnings injector (new) | Read an `assess`-produced JSON side-file (or compute inline) and attach advisory gaps to submissions and rows. |
| Output path | Unchanged: `docs/project/submissions/submission-tracker.html`. Single file; the topology-aware views are all client-side. |

### P4.7 — Best-practices updates (drafted SKILL.md additions)

Additions to the `/tracker` SKILL.md Best Practices table (drafted to match the existing severity levels: Required / Recommended).

| Check | How to Verify | Severity |
|-------|--------------|----------|
| Every `project.sub_dhfs[].filing` value has a corresponding `docs/project/submissions/<filing>/composition-manifest.md` file | Glob and cross-check | Required when topology is multi-sub-dhf |
| Every composition manifest parses cleanly (no malformed `## Included pieces` rows, valid filing identification block) | Tracker parser returns no errors | Required |
| Every composition manifest's `## Included pieces` table references sub-DHF paths that exist in `project.sub_dhfs[]` | Cross-check against `project.yml` | Required |
| Every composition manifest's referenced sub-DHFs also exist on disk under their `path` | Filesystem check | Required |
| `/tracker assess` runs without errors (warnings allowed) | Exit code 0 | Recommended |
| Strategy-advisory gaps are either resolved or acknowledged in the manifest's `## Excluded pieces` table with a rationale | Compare `assess` warnings against `## Excluded pieces` entries | Recommended — warnings only, not blockers |
| Submission IDs in the tracker markdown match the `submissions/` folder names exactly | String compare | Recommended |
| Tracker markdown regrouped under `## Submission:` H2 headers in multi-sub-dhf mode (no bare Part 1–4 at the top level) | Structural check in parser | Required when topology is multi-sub-dhf |

Drafted addition to the SKILL.md Context Required section (to replace the current "Key sources" list in multi-sub-dhf mode):

> **In multi-sub-dhf mode the context set is per-submission.** For each filing under `docs/project/submissions/<filing>/`, read:
> 1. **Composition manifest** (`composition-manifest.md`) — authoritative list of pieces pulled into this filing from which sub-DHFs.
> 2. **Regulatory strategy** for the lead sub-DHF (`dhfs/<path>/design-controls/plans/regulatory-strategy.md`) — advisory. Drives PCCP scope, cybersecurity framework, reuse decisions.
> 3. **Architecture strategy** for every referenced sub-DHF (`dhfs/<path>/design-controls/architecture/architecture-strategy.md`) — advisory. Drives interface and module deliverables.
> 4. **Risk and VnV strategies** for every referenced sub-DHF — advisory. Drive risk and verification deliverables.
> 5. **Shared strategies** (`docs/project/strategies/<domain>-strategy.md`) — advisory. Drive cross-cutting post-market, commercial, and operations deliverables.
> 6. **FDA guidance documents** (`docs/external/fda-guidance/`) — unchanged.

### P4.8 — Exit gate for P4

P4 is considered "done" when the following validations all pass on PDLC_DEMO:

- **Dual-topology build**: `/tracker build` runs cleanly in both topologies —
  - Current single-dhf state: produces the same `submission-tracker.md` as today (bit-for-bit except for the tracker's own timestamp/changelog row).
  - Simulated multi-sub-dhf state (PDLC_DEMO with `project.topology: multi-sub-dhf` and stub `project.sub_dhfs[]` for `pca-device`, `drug-library-manager`, `cloud-suite`): produces a tracker markdown with H2 sections for `K210345-pca-device`, `pccp-pp3500-2026`, `qsub-pp3500-2026`, each populated from its stub composition manifest.
- **Manifest walk works**: the three submission folders exist (created by `init`), each has a composition manifest, and `/tracker build` walks all three without errors.
- **Strategy advisory reads work**: the tracker reads advisory strategy docs from their per-sub-DHF locations (stubbed during P4 testing, real in P6) and extracts at least two distinct signal types (PCCP flag, cybersecurity framework).
- **New columns populated**: in the multi-sub-dhf output, every row has `Submission`, `Source Sub-DHF`, and `Provenance` columns filled — no blank values except where the schema allows.
- **Dashboard renders**: `/tracker render` produces a valid `submission-tracker.html` with the submission selector dropdown, the roll-up view, and at least one drill-in view. Single-dhf fallback render continues to work.
- **Assess flags a synthetic gap**: a deliberately incomplete composition manifest (e.g., regulatory strategy says PCCP is included for `pccp-pp3500-2026` but the manifest omits the PCCP narrative deliverable) triggers exactly the expected advisory warning from `/tracker assess`.
- **SKILL.md edits drafted, not applied**: all SKILL.md additions for `/tracker` exist inside this task doc (P4.1–P4.7) and have not been written to `.claude/skills/tracker/SKILL.md`. Implementation is a follow-on task.
- **`render.py` changes scoped out**: the function/section table in P4.6 is the sole record of render.py changes. No Python drafted.

P4 can proceed in parallel with P5 (best-practices). Both feed into P6 (PDLC_DEMO live-fire migration), where the drafted changes are actually applied to the real SKILL.md and render.py files and the tracker is re-run against live sub-DHF content.

### Ambiguities resolved

- **Un-tracked sub-DHFs are hidden by default.** _Chosen default._ Sub-DHFs that no composition manifest references are omitted from the tracker markdown entirely and surfaced only via `status --include-untracked`. Rationale: the tracker is a submission packaging tool, not a DHF inventory. The alternative (always showing every sub-DHF, even orphaned ones) clutters the dashboard for the common case. _Flagged for user review — the opposite default (always show, hide via flag) is also defensible._
- **Submission-prefixed IDs.** _Chosen default._ In multi-sub-dhf mode, deliverable IDs are prefixed with the submission ID (`K210345-C1a`) to avoid collisions across filings. Rationale: the same deliverable type (e.g., cybersecurity assessment) can legitimately appear in two filings with different evidence and status. The alternative (requiring globally unique bare IDs) forces authors to invent differentiators. _Flagged for user review — prefixing makes row IDs longer in the HTML._
- **Strategy-only rows do not appear in the table.** _Chosen default._ Strategy-implied deliverables that are not in a composition manifest stay as `assess` warnings; they do not materialize as table rows with `Provenance: S`. Rationale: the table is a commitment register ("this will be delivered"); strategy signals are a planning input, not a commitment. Leaving them in `assess` keeps the table honest. _Flagged for user review — a future `/tracker promote` action could optionally write strategy-advisory rows into the table with explicit user approval._
- **Tracker markdown stays a single file.** _Chosen default._ `submission-tracker.md` remains one file with per-submission H2 sections, not split into `submission-tracker-<filing>.md` per submission. Rationale: single-file round-trip is simpler for git diffs, render, and best-practices scanning; submissions share too much structural scaffolding to split cleanly. _Flagged for user review — if a project ever has 10+ submissions, splitting may become preferable._
- **Composition manifest is parsed via the P2.5 template contract, not a separate schema.** _Chosen default._ The tracker parses manifests using the section headers and table structure defined in the P2.5 template; no separate `composition-manifest.schema.json` is introduced. Rationale: avoids duplicating the contract in two places and keeps manifests human-authorable. _Flagged for user review — a JSON schema would make the parser stricter and enable pre-commit validation._
- **`render.py` stays one Python file.** _Chosen default._ Topology-aware logic is added as conditionals inside the existing `render.py` rather than split into `render_single.py` / `render_multi.py`. Rationale: the majority of rendering logic is shared; splitting doubles maintenance cost. _Flagged for user review._

### Open questions for P5 prerequisites

- Should P5's best-practices audit check **that every composition manifest has been refreshed since the last relevant strategy doc edit** (timestamp cross-check)? This would catch stale manifests in a multi-sub-dhf project but adds filesystem mtime reads to the audit.
- Does P5's audit call `/tracker assess` and fold its warnings into the project-level readiness report, or does it stay a separate command? Decoupled is simpler but means users run two commands.
- Should un-tracked sub-DHFs be a P5 Required check ("every sub-DHF must be referenced by at least one composition manifest") or a Recommended check? Current P4.2 default (hidden by default) argues for Recommended; a stricter project might want Required.

## Phase P5 — /best-practices Topology Awareness

> **⚠️ Phase status under Architectural Pivot (2026-04-13):** Simplified but mostly intact. `/best-practices` always iterates `sub_dhfs[]` for per-dhf checks — no flat-layout fallback. All checks, Scope column schema, subagent dispatch (P5.5a), stale-manifest check, unreferenced-sub-DHF check carry forward unchanged. What's moot: **ambiguity #2** (per-dhf behavior in single-dhf mode) and any "in single-dhf mode, skip this" language. The dispatcher still has a performance optimization available — when `sub_dhfs[]` has exactly one entry, it can short-circuit subagent fan-out and run per-dhf checks in the parent context directly. That's a performance knob, not a semantic difference.


**Status**: Draft — pending review.

### P5.0 — Overview

`/best-practices` is an aggregation/audit skill: it fetches a shared registry manifest, scans every local `.claude/skills/*/SKILL.md` for a `## Best Practices` table, and runs the union of those checks against the project. Today it treats the project as a flat object — each check runs exactly once at the project root. That works for `single-dhf` topology but breaks the moment a project declares `multi-sub-dhf`, where "is the scaffold present?" has to be answered N times (once per sub-DHF) and new class-level checks appear that only make sense across sub-DHFs.

P5 teaches `/best-practices` a single organizing idea: every check has a **scope**. Most checks remain `shared` (run once at project root) and stay backward-compatible. Some become `per-dhf` (iterate `project.sub_dhfs[]`), some become `per-submission` (iterate `submissions/<filing>/`), and a small number become `cross-cutting` (run once but read across all sub-DHFs — e.g., "no orphan sub-DHFs"). The topology in `project.yml` selects which scopes are applicable; in `single-dhf` mode, `per-dhf` and `cross-cutting` checks are skipped with an INFO line.

P5 also introduces a new check family: **composition manifest validation**. Every `submissions/<filing>/composition-manifest.md` produced against the P2.5 template is parsed, its Included Pieces rows are resolved against `project.sub_dhfs[]` and the filesystem, and reviewer signoff presence is verified. This family is the audit counterpart to the P2.5 template — the template defines the contract, P5 enforces it.

Two cross-cutting checks land with P5: **stale-manifest detection** (cross-check composition manifest mtime against the strategy docs it depends on, per the landed P5 decision) and **unreferenced-sub-DHF detection** (Smart Recommended per the landed decision: only flag sub-DHFs whose `regulatory` status is `in-development` or `cleared` and which appear in zero composition manifests; skip `concept` and `mixed`).

P5 is **design-only** — it drafts SKILL.md deltas inside this task doc; no real skill files are edited. P5 runs **independently of P4** (decoupled per the landed decision: P5 does not call `/tracker assess`) and can proceed in parallel. Both P4 and P5 feed into P6 (PDLC_DEMO live-fire migration), where `/best-practices` will verify the migration's output post-apply.

### P5.1 — Topology-aware check classification

Every best-practices check is assigned exactly one **Scope**. The scope drives iteration and applicability:

| Scope | Runs | Applicable topologies | Notes |
|---|---|---|---|
| `shared` | Once at project root | both | Default for backward compatibility — a check with no Scope column is treated as `shared` |
| `per-dhf` | Once per entry in `project.sub_dhfs[]` | multi-sub-dhf only | In `single-dhf` mode, runs once against the flat layout (same as today) |
| `per-submission` | Once per `submissions/<filing>/` folder | both | Uses `submissions/` as the iteration root regardless of topology |
| `cross-cutting` | Once at project root, reads across multiple sub-DHFs | multi-sub-dhf only | Skipped with INFO in single-dhf mode |

**Classification algorithm (Step 2a, inserted after existing Step 2 "Scan local skills")**:

1. For each skill's Best Practices table, read the `Scope` column if present; otherwise default to `shared`.
2. Read `project.topology` from `project.yml`. If `single-dhf`:
   - Run all `shared` and `per-submission` checks.
   - Run `per-dhf` checks once against the flat layout (treating `docs/project/` as the single implicit sub-DHF root).
   - Skip `cross-cutting` checks; log `[INFO] <check> — cross-cutting, skipped in single-dhf mode`.
3. If `multi-sub-dhf`:
   - Run `shared` checks once at project root.
   - Run `per-dhf` checks N times, once per `project.sub_dhfs[]` entry.
   - Run `per-submission` checks once per `submissions/<filing>/` folder.
   - Run `cross-cutting` checks once at project root.

**Retroactive classification of existing checks**:

| Source skill | Check | Proposed Scope |
|---|---|---|
| best-practices (self) | Team roster exists / has active members | `shared` |
| best-practices (self) | .gitignore blocks secrets / PHI | `shared` |
| best-practices (self) | Setup guide covers training opt-out / 2FA / hygiene / integration | `shared` |
| best-practices (self) | Agent design principles documented | `shared` |
| best-practices (self) | Security hook installed / Secops agent exists / Manifest has security policy | `shared` |
| best-practices (self) | Evaluative skills document detection tiers | `shared` |
| task | Task folder exists / README exists / index consistent / hooks registered | `shared` |
| medtech-docs | Scaffold present | `shared` |
| medtech-docs | Topology matches project signals | `cross-cutting` |
| medtech-docs | `project.sub_dhfs[]` matches `dhfs/` folder tree | `cross-cutting` (multi-sub-dhf only) |
| medtech-docs | Every sub-DHF has README + design-controls scaffold | `per-dhf` |
| medtech-docs | Every `submissions/<filing>/` has a composition manifest | `per-submission` |
| medtech-docs | Applicable standards populated | `shared` |
| strategy | Strategy briefs initialized | `per-dhf` (multi), `shared` (single) |
| strategy | Strategy content exists | `shared` |
| strategy | Active domains have documents | per-domain: `per-dhf` for per-dhf domains, `shared` for shared domains |
| strategy | Topology-aware assembly (P3) | `cross-cutting` |
| strategy | `sub-dhf=<value>` tags resolve | `cross-cutting` |
| strategy | No pending reviews | per-domain: `per-dhf` or `shared` |
| tracker | Every filing has composition manifest | `per-submission` |
| tracker | Composition manifests parse | `per-submission` |
| tracker | Readiness assessment runs | `per-submission` |
| tracker | Strategy alignment advisory | `per-submission` |
| docflow | (no checks currently published) | — |
| P5 new | Composition manifest validation family | `per-submission` |
| P5 new | Stale-manifest detection | `cross-cutting` |
| P5 new | Unreferenced-sub-DHF | `cross-cutting` |

### P5.2 — Composition manifest validation (drafted SKILL.md additions)

New check family, drafted for insertion into `best-practices/SKILL.md` under a new sub-heading within `## Best Practices`:

| Check | How to Verify | Severity | Scope |
|---|---|---|---|
| Composition manifest parses | For each `submissions/<filing>/composition-manifest.md`, verify presence of top-level sections required by the P2.5 template: `## Identity`, `## Filing identification`, `## Included pieces`, `## Excluded pieces`, `## Cross-references to source sub-DHFs`, `## Reviewer sign-off`. Use Read on the file, regex-match `^## <Section>$` anchored at line start. Report FAIL with the first missing header if any section is absent. | Required | per-submission |
| Included pieces paths exist on disk | Parse the Included Pieces table (markdown table under `## Included pieces`). For each row, read the `path` column (relative to `docs/project/dhfs/`), resolve to absolute path, and use Glob to verify the folder exists. FAIL with the offending row if missing. | Required | per-submission |
| Included pieces paths appear in `project.sub_dhfs[]` | For each Included Pieces row's path, search `project.sub_dhfs[].path` for an exact match. FAIL with the offending row if no match — indicates a manifest referencing a sub-DHF that was deleted or renamed without manifest update. | Required | per-submission |
| Excluded pieces rationale present | Parse the Excluded Pieces table. For each row, verify the `reason` column is non-empty (trim whitespace). WARN per offending row. | Recommended | per-submission |
| Reviewer signoff block present | Verify `## Reviewer sign-off` section exists and contains at least one bullet or row. Empty content is acceptable (reviewer may not have signed yet) — the section must merely exist. | Recommended | per-submission |

**Parsing notes for implementers**: The "How to verify" algorithms assume a simple markdown table parser. Reuse the same parser `/tracker` uses in P4 to keep behavior consistent. If `/tracker`'s parser ships a Python helper (`render.py` in the tracker skill), best-practices should shell out to that module via `python3 -c "from tracker.render import parse_composition_manifest; ..."` rather than re-implementing. The parser must tolerate:
- Blank lines between sections.
- Trailing whitespace in table cells.
- Tables with fewer columns than the canonical template (report FAIL with "malformed table").

### P5.3 — Stale-manifest detection (drafted SKILL.md addition)

Drafted check, inserted into the same new sub-section of `## Best Practices`:

| Check | How to Verify | Severity | Scope |
|---|---|---|---|
| Composition manifest is fresh relative to referenced strategy docs | Compute the manifest's mtime and compare against every strategy document it implicitly depends on. Flag WARN with the list of newer dependencies. Suppressed if a stale-ack comment is present. | Recommended | cross-cutting |

**Algorithm**:

1. Enumerate all `submissions/<filing>/composition-manifest.md` files via Glob.
2. For each manifest M:
   a. Determine M's **reference mtime**: prefer `git log -1 --format=%ct -- <path>` (git commit time of last touch); fall back to filesystem `stat -f %m` (macOS) / `stat -c %Y` (Linux) if the project is not a git repo.
   b. Parse M's Included Pieces table to get the set of referenced sub-DHFs `S = {sub-dhf-1, sub-dhf-2, ...}`.
   c. Construct the **dependency set** D:
      - For each sub-DHF in S, include every per-dhf strategy document under `docs/project/dhfs/<path>/strategy/*.md` (per the P1 per-dhf strategy convention — regulatory, architecture, risk, testing).
      - Always include the shared strategies at `docs/project/strategy/*.md` for shared domains (commercial, operations) — these can affect submission planning regardless of which sub-DHFs are in the filing.
   d. For each dependency document d in D, compute d's mtime using the same git-first, fs-fallback rule.
   e. Collect `newer = { d in D : mtime(d) > mtime(M) }`.
   f. If `newer` is non-empty, check M's file content for a stale-ack marker: a line matching `<!-- stale-ack: verified YYYY-MM-DD by <author> -->`. If present, compare the ack date against `max(mtime(d) for d in newer)`:
      - Ack date ≥ newest dependency mtime → PASS (suppressed).
      - Ack date < newest dependency mtime → WARN (ack is itself stale).
   g. If `newer` is non-empty and no ack is present, WARN with the list of newer dependencies and their mtimes.

**Severity rationale** (Recommended, not Required): not every strategy update actually invalidates a composition manifest — a typo fix in the architecture brief doesn't change what's in the filing. The check surfaces candidates for human review rather than gating.

**Report format**:

```
[WARN] submissions/510k-infusion-pump/composition-manifest.md — stale
       newer dependencies:
         docs/project/dhfs/pump-firmware/strategy/regulatory.md (2026-04-11)
         docs/project/strategy/commercial.md (2026-04-10)
       manifest mtime: 2026-04-05
       fix: review the above and either update the manifest or add
            `<!-- stale-ack: verified 2026-04-12 by <your-name> -->`
            inside the manifest to suppress until the next change.
```

**Backward compatibility**: in `single-dhf` mode, if `submissions/<filing>/composition-manifest.md` files do not yet exist, the check is a no-op (iteration set is empty). If a single-dhf project adopts composition manifests as a convention, the check runs against whatever is present.

**git mtime vs fs mtime**: git mtime is preferred because branch switches, rebases, and worktree operations reset fs mtimes to checkout time — which would produce false "fresh" signals after every `git checkout`. git mtime is stable across these operations. Document this preference in SKILL.md under the check's notes.

### P5.4 — Unreferenced-sub-DHF check (drafted SKILL.md addition)

Drafted Smart Recommended check per the landed P5 decision:

| Check | How to Verify | Severity | Scope |
|---|---|---|---|
| Every active sub-DHF is referenced by at least one composition manifest | Enumerate `project.sub_dhfs[]`, filter by regulatory status, cross-check against all manifests' Included Pieces tables. WARN on unreferenced active sub-DHFs. | Recommended | cross-cutting |

**Algorithm**:

1. Read `project.sub_dhfs[]` from `project.yml`.
2. Enumerate all `submissions/**/composition-manifest.md` via Glob.
3. Build `referenced = { path : path appears in at least one manifest's Included Pieces table }`.
4. Filter `project.sub_dhfs[]` to `active = { sd : sd.regulatory ∈ {"in-development", "cleared"} }`.
   - `concept` status is skipped because such sub-DHFs are explicitly pre-filing.
   - `mixed` status is skipped because it denotes a platform sub-DHF (e.g., `cloud-suite`) whose children carry the regulatory weight; the parent itself isn't directly filed.
5. Compute `unreferenced = active \ referenced`.
6. For each entry in `unreferenced`, emit WARN.

**Report format**:

```
[WARN] sub-DHF drug-library-manager — unreferenced
       path: cloud-suite/dhfs/drug-library-manager
       regulatory status: in-development
       fix: add this sub-DHF to the Included Pieces table of the
            appropriate submissions/<filing>/composition-manifest.md,
            OR change regulatory status to `concept` in project.yml if
            it is not yet intended for any filing.
```

**Backward compatibility**: skipped entirely in `single-dhf` mode (no `sub_dhfs[]` to iterate). Logged as `[INFO] unreferenced-sub-DHF check — skipped in single-dhf mode`.

### P5.5 — Per-sub-DHF check iteration logic (drafted SKILL.md addition)

This section drafts how P5 actually runs `per-dhf`-scoped checks when topology is `multi-sub-dhf`. Inserted as a new numbered sub-step under Step 3 of the `audit` action.

**Step 3 expansion (replaces current Step 3 intro)**:

For each check from both sources (registry + local skills):

1. Determine the check's Scope (default `shared` if omitted).
2. Determine applicability given the current topology (see P5.1 matrix).
3. **Dispatch by Scope**:
   - `shared` → run once at project root, record result with no label.
   - `per-dhf`:
     - If `single-dhf`: run once at project root against the flat layout (identical to legacy behavior).
     - If `multi-sub-dhf`: iterate `project.sub_dhfs[]`. For each entry E:
       - Resolve `root = docs/project/dhfs/<E.path>`.
       - Run the check with `root` as the implicit working directory. The check's "How to verify" algorithm sees paths relative to `root` the same way a single-dhf check sees paths relative to `docs/project/`.
       - Record the result with label `sub-dhf=<E.short-name>`.
   - `per-submission` → iterate `submissions/<filing>/` folders via Glob. Record each result with label `filing=<name>`.
   - `cross-cutting` → run once at project root; the check itself enumerates `project.sub_dhfs[]` and reads across them. Record with no label.
4. Classify the result (PASS / FAIL / WARN / INFO) as before.

**Shim for non-topology-aware skills**: a check table row may be labeled `Scope: per-dhf` even when the host skill's "How to verify" prose hard-codes paths like `docs/project/design-controls/...`. P5 handles this transparently: when running the check in a sub-DHF context, it sets the process working directory to the sub-DHF root and lets the existing path logic resolve relative to that root. Skills adopt topology awareness by (a) adding the Scope column and (b) optionally refactoring their prose to be root-agnostic. The shim means (a) can ship before (b).

**Report format — single-dhf mode** (unchanged from today, backward compatibility):

```
Project Audit: PDLC_DEMO

## Registry Practices (from GlobalLogic-a-Hitachi-Company/hitachi)
  [PASS] CLAUDE.md exists with project overview
  ...

## Task Management (from .claude/skills/task/SKILL.md)
  [PASS] Task folder exists
  ...

Summary: 18/20 passed | 1 failed | 1 warning
```

**Report format — multi-sub-dhf mode** (new grouped format):

```
Project Audit: PDLC_DEMO (multi-sub-dhf, 4 sub-DHFs)

## Shared Checks
  [PASS] CLAUDE.md exists with project overview
  [PASS] Team roster has active members
  [PASS] Scaffold present
  ...

## Per-sub-DHF Checks
  ### pump-firmware
    [PASS] README + design-controls scaffold present
    [PASS] Strategy briefs initialized
    [WARN] No pending reviews — 2 pending in strategy/regulatory.md
  ### drug-library-manager
    [PASS] README + design-controls scaffold present
    [FAIL] Strategy briefs initialized — strategy/architecture.md missing
  ### cloud-suite
    [PASS] README present
    [INFO] platform sub-DHF (regulatory=mixed) — per-dhf strategy checks skipped
  ### infusion-app
    [PASS] README + design-controls scaffold present
    [PASS] Strategy briefs initialized

## Per-Submission Checks
  ### submissions/510k-infusion-pump/
    [PASS] composition-manifest.md parses
    [PASS] Included pieces resolve to existing sub-DHFs
    [WARN] Excluded pieces rationale missing on row 2

## Cross-Cutting Checks
  [PASS] project.sub_dhfs[] matches dhfs/ folder tree
  [WARN] Composition manifest stale — submissions/510k-infusion-pump/
  [WARN] Unreferenced sub-DHF — drug-library-manager (in-development)

Summary: 22 passed | 1 failed | 4 warnings | 1 info
```

### P5.5a — Subagent dispatch model (new, ambiguity 9 resolution)

**Decision (2026-04-13)**: In `multi-sub-dhf` mode, `per-dhf` and `per-submission` checks run in LLM subagents spawned in parallel, not in the dispatcher's own context and not via subprocess fan-out. Rationale captured in ambiguity 9 above.

**Why LLM subagents, not subprocess fan-out.** `/best-practices` is a dispatcher that reads checks from other skills' `Best Practices` tables. The owning skill writes the "How to Verify" column, and that column can be a scripted test (bash one-liner) or a reasoning-based criterion ("every user need traces to at least one measurable acceptance criterion"). The dispatcher has no control over the mix, and the mix will shift over time as skills evolve. Subprocess fan-out can only run scripted checks — it would silently skip or crash on reasoning-based ones. LLM subagents handle both kinds uniformly: each subagent runs shell commands for scripted checks and reasons through judgment for the others.

**Subagent pools (two separate pools, no mixing)**:

| Pool | Cardinality | Input per subagent | Output |
|---|---|---|---|
| **Per-sub-DHF** | One subagent per entry in `project.sub_dhfs[]` (except those filtered out — see below) | (a) sub-DHF path, (b) list of `per-dhf` checks extracted from consuming skills' SKILL.md Best Practices tables, (c) structured output schema | Structured findings list (one entry per check: id, status, message) |
| **Per-submission** | One subagent per composition manifest under `submissions/` | (a) manifest path, (b) list of `per-submission` checks, (c) structured output schema | Structured findings list |

Per-sub-DHF and per-submission pools are **disjoint**. A composition manifest typically belongs to a single submission but references artifacts across multiple sub-DHFs; scoping per-submission work to one subagent per manifest keeps cross-DHF reference checks in a single context and avoids duplicating work across multiple per-sub-DHF subagents that would each see only their own slice.

**Dispatcher responsibilities (run in parent context)**:
1. Read `project.yml` to get `topology` and `sub_dhfs[]`.
2. Read every consuming skill's SKILL.md `Best Practices` section; parse the Scope column; partition checks into `shared`, `per-dhf`, `per-submission`, `cross-cutting` buckets.
3. Run `shared` and `cross-cutting` checks in the parent context directly.
4. Fan out `per-dhf` checks — spawn one Agent per eligible sub-DHF in parallel (single message with N Agent tool calls). Skip sub-DHFs filtered by `--sub-dhf=<name>` or by regulatory status (`concept` is skipped today, `mixed` participates but some checks self-skip per ambiguity 3).
5. Fan out `per-submission` checks — spawn one Agent per composition manifest in parallel.
6. Collect all subagent results. Merge into the grouped report format (P5.5). Render.

**Subagent prompt contract (fixed template, versioned in SKILL.md)**:

```
You are a best-practices audit worker for sub-DHF `<name>` at path `docs/project/dhfs/<path>`.

Run the following checks against this sub-DHF and return a structured findings list.

Checks to run:
1. <check-id> (from <skill>): <check name>
   How to verify: <verbatim from skill's SKILL.md>
   Severity: <Required|Recommended>
2. ...

For each check:
- If the "How to verify" is a shell command, run it via Bash and interpret exit code (0 = PASS, non-zero = FAIL).
- If the "How to verify" is a natural-language criterion, read the relevant files and reason through it. Err toward FAIL when uncertain — audit results must be conservative.
- Do NOT modify any files. Read-only.
- Do NOT invoke any tool outside Read, Glob, Grep, Bash (read-only commands).

Return a single JSON block with this schema:
{
  "sub_dhf": "<name>",
  "findings": [
    {"check_id": "...", "skill": "...", "status": "PASS|FAIL|WARN|INFO", "message": "..."},
    ...
  ]
}
```

A parallel template exists for the per-submission pool; same shape, with `submission` replacing `sub_dhf` and manifest path replacing DHF path.

**Error isolation**. If a subagent crashes, times out, returns malformed JSON, or exits without a findings block, the dispatcher emits a synthetic `[FAIL] dispatch error` finding for that sub-DHF / submission and continues. One bad subagent does not kill the audit.

**Determinism**. Scripted checks remain deterministic regardless of which subagent runs them. Reasoning-based checks are inherently LLM-graded with some variance — same property as asking a reviewer to judge a fuzzy criterion. Mitigations:
- Owning skills should write reasoning-based "How to verify" criteria as tightly as possible (explicit PASS/FAIL conditions, examples of both) to minimize variance.
- The subagent prompt includes "err toward FAIL when uncertain" to bias toward conservative results.
- A future follow-up (not P5) could add a `--seed` or `--strict` flag that runs each reasoning check twice and flags disagreement.

**Cost model**. A PDLC_DEMO-sized project has ~10 sub-DHFs (pca-device, connectivity-adapter, cloud-suite + 7 children). An audit run spawns ~11 subagents (10 per-dhf + 1 per-submission for the single 510(k) manifest). Each subagent reads a bounded slice of the tree and executes a known list of checks. Rough envelope: each subagent ~5–15k input tokens, ~1–3k output tokens; per-audit ~100–200k total tokens. This is a deliberate action, not a hot path — operators run it before commits or PR, not on every save. Knobs to control cost: `--sub-dhf=<name>` narrows the per-dhf pool; per-submission pool is naturally bounded by manifest count.

**Backward compatibility with single-dhf mode**. In `single-dhf` mode, the dispatcher runs _everything_ in its own context — no subagent pools, no fan-out. The subagent machinery is dead code until topology flips. This preserves today's audit behavior byte-for-byte for single-dhf projects (required by P5 exit gate criterion 2).

**Implications for P5 exit gate**. The "traced against hypothetical topology" criterion (P5.9 item 3) now also requires a traced example of (a) a sample per-sub-DHF subagent prompt, (b) a sample subagent JSON response, (c) the merged report. These become part of the P5 deliverable, not P6.

**Implications for consuming skills**. Consuming skills that add `per-dhf` or `per-submission` checks must write their "How to verify" column to work standalone — i.e., given only the sub-DHF root path, the check should be evaluable without knowing about sibling sub-DHFs. This is a style rule added to the Scope-column specification in P5.7.

### P5.6 — Other check scope updates across existing skills

Summary of the one-time **Scope column addition** required in every consuming skill's Best Practices table. No check wording changes — just a new rightmost column. Implementation happens during P6 (or a follow-up task); P5 specifies the target state.

| Skill | Check | New Scope column value | SKILL.md edit required? |
|---|---|---|---|
| task | Task folder exists | `shared` | Yes (add column) |
| task | Task README exists | `shared` | Yes |
| task | Index consistent / hooks registered | `shared` | Yes |
| medtech-docs | Scaffold present | `shared` | Yes |
| medtech-docs | Topology matches project signals | `cross-cutting` | Yes |
| medtech-docs | `project.sub_dhfs[]` matches `dhfs/` folder tree | `cross-cutting` | Yes |
| medtech-docs | Every sub-DHF has README + design-controls | `per-dhf` | Yes |
| medtech-docs | Every filing has composition-manifest.md | `per-submission` | Yes |
| medtech-docs | Applicable standards populated | `shared` (default; project may override to `per-dhf` if they split standards per component) | Yes |
| strategy | Strategy briefs initialized | `per-dhf` | Yes |
| strategy | Strategy content exists | `shared` | Yes |
| strategy | Active domains have documents | `per-dhf` (per-dhf domains) / `shared` (shared domains) | Yes — may need two rows, one per domain class |
| strategy | Topology-aware assembly | `cross-cutting` | Yes (new check from P3) |
| strategy | `sub-dhf=<value>` tags resolve | `cross-cutting` | Yes (new check from P3) |
| strategy | No pending reviews | `per-dhf` / `shared` by domain class | Yes |
| tracker | Every filing has composition manifest | `per-submission` | Yes |
| tracker | Composition manifests parse | `per-submission` | Yes |
| tracker | Readiness assessment runs | `per-submission` | Yes |
| tracker | Strategy alignment advisory | `per-submission` | Yes |
| docflow | (none currently) | — | — |
| best-practices | All existing self-checks | `shared` | Yes |

All edits are mechanical (add column header + per-row value). No check semantics change.

### P5.7 — SKILL.md check-table schema change

P5 introduces a **one-time schema change** to every skill's `## Best Practices` table: a new rightmost **Scope** column.

**Before** (representative — task skill):

```markdown
## Best Practices

| Check | How to Verify | Severity |
|-------|--------------|----------|
| Task folder exists | `tasks/` directory exists at project root | Required |
| Task README exists | `tasks/README.md` exists | Required |
```

**After**:

```markdown
## Best Practices

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Task folder exists | `tasks/` directory exists at project root | Required | shared |
| Task README exists | `tasks/README.md` exists | Required | shared |
```

**Schema rule**: `| Check | How to Verify | Severity | Scope |`. Scope is the rightmost column. Valid values: `shared`, `per-dhf`, `per-submission`, `cross-cutting`.

**Backward compatibility**: `/best-practices` treats a check with no Scope column as `shared`. This lets skills adopt the new schema incrementally without breaking the audit in the interim. Document this default explicitly in `best-practices/SKILL.md` under Registry Format:

> **Scope column (optional)**: If present, must be one of `shared`, `per-dhf`, `per-submission`, `cross-cutting`. If omitted, P5 treats the check as `shared` — preserving pre-P5 behavior.

**Migration path**: the actual column-addition edits to every consuming skill's SKILL.md are **out of P5 scope** (design-only). They happen during P6 or as follow-up per-skill housekeeping tasks. The only skill that must have the column on P5-complete day is `best-practices` itself (for its own self-checks) and any brand-new checks P5 adds inline.

### P5.8 — Best-practices action changes (drafted SKILL.md updates)

Delta for each `/best-practices` action. Matches the real action names (`audit`, `check`, `sync`) from the current SKILL.md.

#### `audit` — topology-aware expansion

Replace current Steps 1–4 with:

**Step 0 — Read topology** (new)
Read `project.yml` from project root. Extract `project.topology` (one of `single-dhf`, `multi-sub-dhf`; default `single-dhf` if absent). Extract `project.sub_dhfs[]` if `multi-sub-dhf`.

**Step 1 — Fetch registry practices** (unchanged)

**Step 2 — Scan local skills** (unchanged)

**Step 2a — Classify checks by Scope** (new)
For each check from Steps 1 and 2, read the `Scope` column if present (default `shared`). Filter out checks whose Scope is not applicable to the current topology (see P5.1 matrix).

**Step 3 — Run checks** (expanded per P5.5)
Dispatch each check by its Scope — `shared` once, `per-dhf` iterated over `project.sub_dhfs[]` in multi-sub-dhf mode, `per-submission` iterated over `submissions/<filing>/`, `cross-cutting` once at project root.

**Step 4 — Report** (expanded per P5.5 report format)
Single-dhf mode: same grouping as today. Multi-sub-dhf mode: four sections — Shared Checks, Per-sub-DHF Checks (grouped by sub-DHF short name), Per-Submission Checks (grouped by filing), Cross-Cutting Checks.

#### `check <practice-name>` — topology-aware single-check execution

Extend the argument parser to accept an optional `--sub-dhf=<short-name>` flag. Semantics:

- No flag, check is `shared` → run once as today.
- No flag, check is `per-dhf`, topology multi-sub-dhf → iterate all sub-DHFs and report each.
- `--sub-dhf=X`, check is `per-dhf` → run once scoped to sub-DHF X. Error if X is not in `project.sub_dhfs[]`.
- `--sub-dhf=X`, check is `shared` → error: "check <name> is shared-scope; --sub-dhf is not applicable."
- No flag, check is `cross-cutting` → run once at project root.

#### `sync` — unchanged

The `sync` action compares registry and local skill versions; it is topology-independent. P5 makes no changes to sync.

#### No `fix` / `validate` / `dry-run` actions today

The current SKILL.md only defines `audit`, `check`, and `sync`. P5 does not introduce new actions — keeping the surface area stable. If a `fix` action is added later, it must ask confirmation before applying fixes across multiple sub-DHFs (one prompt per sub-DHF, or a batch "apply to all N sub-DHFs?" prompt).

### P5.9 — Exit gate for P5

P5 is "done" when:

1. **Design is captured in this task doc.** All sub-sections P5.0–P5.8 are written, reviewed, and approved. No real skill files edited.
2. **Backward compatibility is demonstrated on paper.** The drafted logic, when traced against PDLC_DEMO's current `single-dhf` topology, produces an audit report byte-identical to today's output (same checks, same order, same grouping).
3. **Multi-sub-dhf trace is demonstrated on paper.** The drafted logic, when traced against the **P1 hypothetical topology** (4 sub-DHFs: pump-firmware, drug-library-manager, cloud-suite, infusion-app), produces a multi-section report matching the P5.5 example format, with:
   - One Per-sub-DHF block per sub-DHF.
   - At least one `per-submission` check run against the hypothetical `submissions/510k-infusion-pump/composition-manifest.md`.
   - Stale-manifest check surfaces the synthetic stale example (manually-touched strategy doc newer than manifest).
   - Unreferenced-sub-DHF check reports `concept`-status sub-DHFs as filtered (skipped line) and any `in-development`/`cleared` sub-DHFs absent from every manifest as WARN findings.
4. **Schema change is specified, not applied.** The Scope column schema is documented in P5.7. Actual edits to `task/SKILL.md`, `medtech-docs/SKILL.md`, `strategy/SKILL.md`, `tracker/SKILL.md`, and `docflow/SKILL.md` are **not** part of P5 — they are P6 or follow-up tasks.
5. **P5 unblocks P6.** P6 (PDLC_DEMO live-fire migration) can proceed with confidence that post-apply `/best-practices audit` will catch regressions in the new multi-sub-dhf layout — missing sub-DHFs, stale composition manifests, orphan filings, unreferenced sub-DHFs.
6. **No crashes on edge cases** (verified by trace, not by running):
   - `multi-sub-dhf` project with zero composition manifests → per-submission checks iterate zero items, no errors.
   - Sub-DHF with minimal content (README only, no strategy docs) → per-dhf strategy checks WARN cleanly, do not crash.
   - Sub-DHF listed in `project.sub_dhfs[]` but missing on disk → cross-cutting manifest-vs-tree check FAIL, downstream per-dhf iteration for that entry is skipped with an error line.
   - Composition manifest present but malformed (missing header) → parses check FAILs and downstream per-submission checks for that manifest are skipped (do not cascade-fail).

### Ambiguities resolved

The following ambiguities were resolved with defaults — flagged for user review.

- **Default Scope when column omitted**: chosen `shared`. _Signed off 2026-04-13 by Ben._ Rationale: preserves every existing check's behavior on day one, so P5 can ship without gating on every consuming skill's SKILL.md edit. Alternative (`per-dhf` default) would force a coordinated rollout. **Follow-up**: P5 exit gate must include a one-time inventory of every existing check with a proposed Scope classification, even if actual SKILL.md edits are deferred to housekeeping — mitigates the risk that a check which _should_ be `per-dhf` silently stays `shared` and under-covers multi-DHF projects.
- **`per-dhf` check behavior in `single-dhf` mode**: ~~chosen "run once against the flat layout."~~ **MOOT under Architectural Pivot (2026-04-13).** There is no `single-dhf` mode under the unified shape — every project has a `dhfs/` folder and `per-dhf` checks always iterate `project.sub_dhfs[]`. The N=1 case is handled uniformly: one entry in `sub_dhfs[]` means the per-dhf check runs once, against `dhfs/<primary>/`. No flat-layout fallback exists.
- **`mixed` regulatory status skipped in unreferenced-sub-DHF check**: chosen "skip." _Signed off 2026-04-13 by Ben._ Rationale: `mixed` denotes platform sub-DHFs whose children carry the regulatory weight; flagging the parent as unreferenced would produce noise every audit run (e.g., PDLC_DEMO's `cloud-suite`). **Abuse mitigation**: add a sibling check "platform sub-DHFs (regulatory=mixed) must have at least one child sub-DHF" so the `mixed` tag can't be used to silence the check on an unplanned leaf component. Tracked in P5 follow-ups.
- **Stale-manifest dependency set includes shared strategies**: chosen "yes." _Signed off 2026-04-13 by Ben — kept despite noise concern._ Rationale: commercial and operations strategy changes can genuinely affect submission planning (pricing, reimbursement narrative, rollout sequencing); excluding them would miss a real stale case. **Noise mitigation**: the stale-ack comment mechanism (see ambiguity 6) is the escape hatch — when a shared-strategy edit is cosmetic, teams ack the manifest and the check clears. If noise becomes unmanageable in practice, revisit with a configurable exclusion list in `project.yml`.
- **git mtime over fs mtime**: chosen "prefer git, fallback fs." _Signed off 2026-04-13 by Ben._ Rationale: fs mtime is reset by `git checkout` and produces false-fresh after every branch switch. git mtime is stable across checkouts. fs fallback handles the "new untracked file" edge case cleanly without a special-case branch; the inconsistency (file switches timestamp source when committed) is benign because commits move time forward, not backward.
- **Stale-ack comment syntax**: chosen HTML comment with optional file-scope list. _Signed off 2026-04-13 by Ben._ Base form: `<!-- stale-ack: YYYY-MM-DD <author> -->` acks everything as of that date (coarse, matches original drafted semantics). Extended form: `<!-- stale-ack: YYYY-MM-DD <author> — files: path/a.md, path/b.md -->` acks only the listed files — parser reads the `files:` list and only clears staleness for those specific paths. A bare ack (no `files:`) is treated as ack-everything for backward compatibility. Multiple acks stack as multiple comments for successive reviews. HTML comment stays invisible in rendered markdown; date + author gives an audit trail without a separate ack file.
- **Composition manifest parser reuse from `/tracker`**: chosen "no — each skill ships its own independent parser." _Signed off 2026-04-13 by Ben — flipped from drafted default for consistency with P3 prerequisite Q3._ Rationale: same reasoning as Q3 (each skill re-parses `project.yml` directly) — schema is stable, parsing is cheap, skill independence avoids operational coupling. Cross-skill Python imports in a skill registry create real upgrade pain (can't ship `/best-practices` without version-pinning `/tracker`). **Drift mitigation**: both skills' SKILL.md reference a canonical schema definition owned by `medtech-docs` (which ships the composition manifest template); both tracker and best-practices _re-parse_ against that schema rather than calling each other.
- **No new `/best-practices fix` action**: chosen "do not add." _Signed off 2026-04-13 by Ben._ Rationale: P5 is scope-limited to making existing audit infrastructure topology-aware. `fix` is a write action with its own dry-run semantics, safety rails around destructive fixes, and test story — bundling it into P5 would triple scope and delay the read-only checks that unblock P6. **Follow-up**: file a future task for `/best-practices fix` targeting mechanical auto-remediation (generate stub composition manifest, generate missing README scaffold, add missing Scope column with default). Out of scope for 007.
- **`--sub-dhf=` flag and per-sub-DHF execution model**: _Signed off 2026-04-13 by Ben — resolution substantially revised from drafted default._ The original draft added a `--sub-dhf=<name>` flag as a simple serial-iteration filter. On review, this missed a fundamental architectural point: **`/best-practices` is a dispatcher, not a check author** — it discovers checks by reading the "Best Practices" section in each consuming skill's SKILL.md, and each owning skill writes its own "How to Verify" column. That column can be a scripted test (`test -f docs/...`) or a reasoning-based criterion ("every user need traces to at least one measurable acceptance criterion"). The dispatcher cannot know the mix in advance, and it has no control over what future skills add. Therefore subprocess fan-out (shell parallelism) cannot work — it can only run scripted checks and would silently skip or crash on reasoning-based ones. The dispatcher needs a mechanism that works for _both_ kinds uniformly.

  **Resolution: LLM subagent fan-out is the dispatch model for per-sub-DHF and per-submission checks in multi-sub-dhf mode.** Full design in new sub-section **P5.5a — Subagent dispatch model** (added below). Key points:
  - **Per-sub-DHF subagents**: one Claude subagent per sub-DHF, spawned in parallel. Each runs all `per-dhf` checks against its assigned sub-DHF.
  - **Per-submission subagents**: separate pool, one per composition manifest — _not_ folded into per-sub-DHF subagents. Rationale: a submission typically has one manifest but its artifacts span multiple sub-DHFs; scoping per-submission work to one subagent per manifest keeps filing-level cross-references in a single context, and avoids duplicating work across multiple per-sub-DHF subagents that would each see only their own slice.
  - **Shared checks**: run in the dispatcher's own context, no fan-out needed.
  - **Single-dhf mode**: no fan-out at all; dispatcher runs everything in its own context (same as today). The subagent machinery is dead code for single-dhf projects.
  - **`--sub-dhf=<name>` flag**: still exists but now means "only spawn subagents for these sub-DHFs." Shared checks still run. Enables tight-loop debug on one sub-DHF.

### Open questions for P6 prerequisites

P6 is the live-fire migration of PDLC_DEMO. Most P6 work is execution, but a few interactions with best-practices need pre-commit decisions:

- **Who flips `project.topology` from `single-dhf` to `multi-sub-dhf`?** The migration action (from P2) writes the new value; `/best-practices` reads it. Is there a sequencing risk if the migration is half-applied (topology flipped but sub_dhfs[] not yet populated)? Suggest P6 make the topology+sub_dhfs write atomic in one `project.yml` edit.
- **Should P6 run `/best-practices audit` as a pre-migration baseline** so we have a clean diff post-migration? _Resolved 2026-04-13 by Ben: **skip the baseline.**_ Rationale: PDLC_DEMO is a single-developer project with a rebasable history; the cost of a pre-reorg snapshot isn't justified when the post-reorg audit is what actually matters for correctness. Additional wrinkle under the unified shape: the pre-reorg flat layout wouldn't be intelligible to the new `/best-practices` anyway (no more single-dhf mode), so the diff would be noisy across shape differences. P6 goes straight to the reorg and validates with the post-reorg audit only. Correctness of the reorg itself is verified by git diff review.
- **Does P6 need to seed at least one composition manifest** before the reorg so `per-submission` checks have something to run against? _Resolved 2026-04-13 by Ben: **no stub manifest; add a structural cross-cutting check instead.**_ P6 ships with zero composition manifests. To prevent silent-pass on per-submission checks, P5 adds a new cross-cutting check: _"if `project.sub_dhfs[]` is non-empty AND `submissions/*/composition-manifest.md` glob returns zero matches, emit project-level WARN: 'No composition manifests authored — per-submission checks will not run until at least one exists.'"_ Rationale: stub manifests rot into noise within days; a structural check surfaces the "nothing authored yet" state on _any_ project (not just PDLC_DEMO) without requiring placeholder content. The check runs in the dispatcher context (no subagent fan-out needed), is cheap (one glob call), and fits cleanly into P5's cross-cutting check list. **Implication for P5 scope**: add this check to P5.3 / P5.4 neighborhood under a new sub-section "P5.4a — Empty-manifest-set check" (to be drafted when P5 is revisited for implementation).
- **Scope column rollout sequencing**: _Resolved 2026-04-13 by Ben: **inside P6, batched as separate commits per skill.**_ P6 updates all five consuming SKILL.md files (`task/`, `medtech-docs/`, `strategy/`, `tracker/`, `docflow/`) to add the Scope column as part of its work. **Why not defer**: after the reorg, `docs/project/design-controls/` no longer exists (it moved into `dhfs/pca-device/design-controls/`), so any check still classified `shared` that grep'd for `docs/project/design-controls/...` would break immediately. Deferring the Scope rollout would produce an audit blackout — _most_ existing per-dhf-type checks would fail on day one of the reorg and stay broken until housekeeping landed. **Mechanical classification rule** (to reduce review burden): for each Best Practices row, ask _"does the How-to-Verify reference a path under `design-controls/`, `clinical/`, `postmarket/`, `risk-management/`, or `cybersecurity/`?"_ If yes → `per-dhf`. If it references `submissions/` → `per-submission`. If it references `project.yml` sub-DHF enumeration or reads across sub-DHFs → `cross-cutting`. Otherwise → `shared`. **Commit hygiene**: Scope column edits land in their own commit(s), one per skill, separate from the `git mv` reorg commits. This lets a bad classification be reverted independently of the reorg itself.
- **Stale-ack date format**: confirm `YYYY-MM-DD` is acceptable to the team, or switch to ISO 8601 with timezone (`YYYY-MM-DDTHH:MM:SSZ`). Affects P5.3's parser and the documentation shipped with the check.

## Phase P3 Prerequisites (decisions landed 2026-04-13)

- **Q2 — `/tracker` reads composition manifests at plan time.** _Resolved: plan time._ When `migrate-to-multi-dhf` produces a dry-run plan, `/tracker` reads composition manifests as part of rendering the plan preview. Reviewers see the full filing impact before any commit, not after. Apply-time rendering is a follow-up refresh, not the primary read.
- **Q1 — `sub-dhf=<value>` scope key resolution.** _Resolved: short form (last segment of `path`) with uniqueness enforcement._ Tag authors write `sub-dhf=drug-library-manager`, never the full `cloud-suite/dhfs/drug-library-manager`. `medtech-docs add-sub-dhf` refuses to create a sub-DHF whose leaf name collides with any existing one in `project.sub_dhfs[]`, with the error: _"name `<name>` is already used by `<full-path>`; pick a unique name."_ `/strategy` resolves `sub-dhf=<value>` by scanning `project.sub_dhfs[]` for a single entry whose `path` ends in `/<value>` (or equals `<value>` for top-level sub-DHFs); zero matches → error, multiple matches → impossible under the uniqueness rule so treated as internal error.
- **Q3 — `/best-practices` sub-DHF enumeration.** _Resolved: each skill re-parses `project.yml` directly._ No cross-skill helper function. `project.yml` is the single source of truth; each skill reads `project.sub_dhfs[]` independently. Rationale: schema is stable (path, regulatory, filing, parent), re-parsing is cheap, and independence avoids cross-skill coupling. If the schema ever changes in a breaking way, every consuming skill gets updated in the same task along with the schema change — tracked as a project-wide rule in the skill registry sync process.

## Open design questions

- Does `migrate-to-multi-dhf` sweep cross-links automatically, or just move files and leave link-fixing as a manual pass?
- Should topology be recorded in `project.yml` (`project.topology: multi-sub-dhf`) so other skills can query it? I think yes — `/strategy`, `/tracker`, `/best-practices` all need to know.
- What happens to `/strategy`'s hardcoded output paths (`docs/project/design-controls/plans/regulatory-strategy.md`) in a multi-DHF project? Each sub-DHF needs its own strategy, or strategies live at the shared root with scope tags?
- Who owns the composition manifest — regulatory affairs at filing time, or is it a live doc in the DHF?
- Should we introduce a third `topology: platform-plus-apps` now, since Cloud Suite is effectively that shape (shared platform + N apps), or treat it as nested multi-sub-DHF for v1?

## References

| Ref | Description | Location |
|-----|-------------|----------|
| Task 006 | Where sub-DHF need was identified; blocked on this task | `006-architecture-regulatory-strategy.md` |
| Sub-DHF filing composition decision | Motivating regulatory strategy decision | `006-architecture-regulatory-strategy.md` → Regulatory Strategy |
| Medtech-docs skill | The subject of this task | `.claude/skills/medtech-docs/` |
| Current PDLC_DEMO scaffold | Single-DHF layout to be migrated as the first consumer of the upgraded skill | `docs/project/{design-controls,clinical,postmarket,submissions}/` |
| Hitachi skills registry | Upstream home; final changes should be contributed back | `../hitachi/skills/medtech-docs/` |

## Lessons Learned

<!-- LESSONS LEARNED: skill-design, scaffold-evolution, topology-awareness -->

### Scaffold skills must be topology-aware from day one

**Lesson**: A MedTech project-init skill that hardcodes a single-DHF structure cannot be reused across real product ecosystems. Topology — _is this one product or a multi-component ecosystem?_ — is as fundamental a decision as regulatory pathway or device class, and the scaffolding must branch on it.

**Why it matters**: The first version of `medtech-docs init` assumed one DHF and one filing. PDLC_DEMO is a multi-component ecosystem (PCA device, on-prem adapter, cloud suite with 7 apps + future SaMDs). The mismatch only surfaced during architecture strategy discussion, requiring a migration after content was already in place. Future projects will hit the same wall if the skill isn't fixed.

**Applied fix**: Task 007 rescoped from "migrate PDLC_DEMO" to "teach the `medtech-docs` skill about project topology and then use the upgraded skill to migrate PDLC_DEMO." The migration becomes the first real test case of the new capability — if it works for PDLC_DEMO, it'll work for the next project.

**Generalizable rule**: When authoring or reviewing a scaffold/generator skill, ask _"What are the distinct project shapes this skill must serve?"_ before writing the templates. Use an explicit topology parameter instead of hardcoding one shape.

### Design deliverables live inside the task doc, not as sibling files

**Lesson**: When a task spawns a design deliverable — a phase output, a draft spec, a review artifact — it must live **inside the task document** as a new section, not as a separate sibling file. One task, one file. This should be the default unless explicitly told otherwise.

**How it surfaced**: Task 007's Phase P1 design deliverable was initially written to `tasks/ben/007-p1-design.md` as a sibling of `007-sub-dhf-migration.md`. This left the project with two "007" files and fragmented the task's story. The user corrected: _"we did the design, but you created another doc, it should have been in the task doc, not a separate doc. So we have two 007s."_ Then followed up: _"Doesn't our task doc skill guide you to capture our design/analysis in the task doc when doing our thinking planning?"_ — pointing out that this should have been built-in behavior, not something the user had to ask for.

**Root cause**: The task skill's SKILL.md lists `## Analysis` as an _optional_ section alongside Strategy and Lessons Learned. That framing let me default to "maybe spin off a separate file." The guidance needed to be stronger: **capture-in-task is the default, always**, unless the artifact is explicitly meant to live elsewhere permanently.

**Applied fix**:
1. Merged `007-p1-design.md` back into this task doc as `## Phase P1 — Design Deliverable` with subsections P1.1 / P1.2 / P1.3, then deleted the sibling file.
2. Added a feedback memory: `feedback_design_in_task_doc.md` + indexed it in `MEMORY.md`.
3. Added a rule to `CLAUDE.md` Working Conventions: _"One task, one file. All design work, analysis, planning, phase deliverables, and drafted content produced under a task belong inside that task's numbered markdown file as new sections — never as sibling files."_
4. Subagents spawned from task work must now be explicitly told to write into the task doc (or return content for the main agent to insert), not create satellite files.

**Generalizable rule**: Task skill SKILL.md should be updated upstream to make "capture-in-task" the default explicitly, promoting `## Analysis` and phase-output sections from "optional" to "default." Flagged as a follow-up for the hitachi skill-registry sync.

### One-off migrations hide skill gaps — turn them into skill features

**Lesson**: When a project needs a "one-off migration" to change its structure, the migration is usually a missing skill action in disguise. Doing the migration manually is faster in the short term but leaves the skill broken for the next project that needs the same change.

**Why it matters**: The original task 007 would have moved PDLC_DEMO's files and called it done. The underlying `medtech-docs` skill gap would have remained, so the next project hitting the same situation would have had to rediscover and re-solve it.

**Applied fix**: Rescoped as above — the migration is framed as a first use of `/medtech-docs migrate-to-multi-dhf`, not a bespoke one-time operation.

**Generalizable rule**: Before writing a "migration" script, ask whether it should be a skill action. If yes, build the action and use it. The project pays a modest up-front cost and gets a reusable capability; the next project pays zero cost and inherits the capability.

## Changelog

- 2026-04-13: Task created as "Sub-DHF Scaffold Migration (Option A)". User immediately rescoped it: _"The task needs to be about how we build the medtech-doc in a way that can be used repeated, by different structures."_ Task rewritten to target the `medtech-docs` skill itself. The PDLC_DEMO migration becomes the first consumer of the upgraded skill, not the goal. Added topology model (`single-dhf`, `multi-sub-dhf`), shared-vs-per-DHF rule, three new skill actions (`init --topology`, `add-sub-dhf`, `migrate-to-multi-dhf`), open design questions, and two lessons learned about scaffold-skill design.
- 2026-04-13: Walked all 9 P5 ambiguities one at a time; signed off #1, #2, #3, #4, #5, #6, #7, #8 with minor refinements. Flipped #7 (parser reuse) from "reuse tracker's parser" to "independent parsers" for consistency with P3 Q3. Replaced #9 (`--sub-dhf=` flag) with a full subagent-dispatch model after the user identified that `/best-practices` is a dispatcher into other skills' checks — scripted-vs-reasoning check mix is outside our control, so LLM subagent fan-out is the only mechanism that handles both uniformly. Added new P5.5a — Subagent dispatch model: two disjoint subagent pools (per-sub-DHF and per-submission), parent-context dispatcher, fixed subagent prompt contract, error-isolation, determinism mitigations, cost envelope, single-dhf backward compat.
- 2026-04-13: Resolved all 4 P6 prerequisites. #1 (atomic `project.yml` write) signed off as "write in final commit" then marked moot under the Architectural Pivot (no topology field to flip). #2 (pre-reorg baseline audit) resolved "skip — solo developer, rebasable history, and the flat shape wouldn't be intelligible to the new `/best-practices` anyway." #3 (stub composition manifest) resolved "no stub; add a structural cross-cutting check (new P5.4a) that WARNs when `sub_dhfs[]` is non-empty but zero composition manifests exist." #4 (Scope column rollout sequencing) resolved "inside P6, batched as separate commits per skill, using a mechanical classification rule based on which folder each check references." Reasoning: deferring would produce an audit blackout because post-reorg `docs/project/design-controls/` no longer exists.
- 2026-04-13: **Architectural Pivot — dropped the dual-topology model entirely.** User proposed: what if single-dhf and multi-sub-dhf use the same shape from day one? On review, every piece of dual-topology complexity (P1 topology model, P2 `migrate-to-multi-dhf`, P3/P4/P5 mode branching, ambiguities #1/#2/#4/#9) traced back to three wrong assumptions (small projects carrying `dhfs/` overhead, existing flat projects needing a migration-able path, single and multi being fundamentally different). The set of "existing flat projects" is exactly one (PDLC_DEMO). Adopted the unified shape: every project is `docs/project/dhfs/<primary>/...` from init, N=1 is just a degenerate case of N>1, growth is a plain `add-sub-dhf` call. Deleted `migrate-to-multi-dhf` action. Deleted `init --topology` flag. Deleted `project.topology` field. Ambiguity #2 marked moot. P2/P3/P4/P5 dramatically simplified; subagent dispatch (P5.5a) stays and runs uniformly. PDLC_DEMO's one-time reorg from flat → `dhfs/pca-device/` becomes a P6 execution step, not a skill feature. Init prompts for the primary sub-DHF name with no default (option 1). Architectural Pivot section added near the top; "Why this shape" and "Topology model (proposed)" marked historical.
