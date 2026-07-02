# 009 — Shared Strategy Docs (flip per-dhf domains to shared)

**ID**: 009
**Created**: 2026-04-13
**Status**: Completed
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## Goals

_Collapse the six per-dhf strategy domains (`regulatory`, `architecture`, `development`, `testing`, `risk`, `postmarket`) into shared, project-level documents. Strategy is inherently cross-component — it describes how the DHFs relate to each other, not how each one operates in isolation. Per-component nuance is preserved via topic-level callouts inside each shared strategy doc._

- Flip all six per-dhf domains in the `/strategy` Domain Registry to `shared` scope
- Collapse output paths into `docs/project/strategies/<name>-strategy.md`
- Restructure `default-strategy.md` template so each strategy doc has topic-first sections with per-component callouts nested underneath
- Update `/tracker` Context & Sources to read the shared regulatory strategy
- Update `/medtech-docs` templates: remove per-DHF strategy scaffolding, update `readme-strategies.md` to index the six new shared docs
- Execute the PDLC_DEMO content move: `git mv` existing per-dhf strategy stubs into `docs/project/strategies/`
- Unblock task 006 authoring into the new shared docs

## Design Decisions (2026-04-13)

### Decision 1 — All strategy domains are shared

<!-- STRATEGY CONTENT: architecture, operations -->
<!-- LESSONS LEARNED: skill-design -->

**Decision**: Every domain in the `/strategy` registry has `scope: shared`. No more `per-dhf` scope type for strategy docs.

**Why**: Strategy is a cross-component story. A multi-DHF platform's regulatory filing strategy describes how pca-device, connectivity-adapter, and cloud-suite file together (predicate lineage, PCCP scope, jurisdictional sequence) — splitting it across three files fractures the story that the reviewer most needs to see whole. Same for architecture (platform boundaries span components), development (one SDLC, one CM plan), risk (platform-level hazard chains), testing (integration V&V cuts across modules), and postmarket (field surveillance is one program). The per-component specifics still matter — they live as callouts inside the shared doc, not as separate files.

**Superseded assumption**: Task 007's unified DHF shape correctly pushed design-controls, risk-management, postmarket, and cybersecurity down into `dhfs/<dhf>/`. It incorrectly applied the same logic to *strategy* docs — but strategy is a project-level artifact, not a component-level one. Formal outputs (SDP, SAD, V&V Plan, Risk Mgmt Plan, PMS Plan) still live per-DHF in the dhfs/ tree. Only the strategic **briefs** that inform those formal outputs move up to `docs/project/strategies/`.

### Decision 2 — Topic-first structure with per-component callouts

<!-- STRATEGY CONTENT: architecture -->

**Decision**: Each shared strategy doc is organized by **strategic topic**, with per-component callouts nested under each topic. Not the other way around.

**Why**: Strategy is "one story per topic" — the filing pathway decision is a single decision that happens to express differently for each component, not three independent decisions that happen to share a filename. Topic-first keeps the cross-component tradeoffs adjacent so the reader sees the whole decision surface in one place. Component-first would fracture a single decision across three sections and make comparison impossible.

**Template shape** (applies to `default-strategy.md` and the custom `regulatory-strategy.md`):

```markdown
# <Domain> Strategy

## Scope & Approach
<project-level framing>

## <Strategic Topic 1>
<project-level framing of the topic>

### PCA Device
<component callout: how this topic applies to pca-device>

### Connectivity Adapter
<component callout>

### Cloud Suite
<component callout>

## <Strategic Topic 2>
...
```

Component callouts are optional per topic — some topics apply uniformly and don't need them. The topics themselves are domain-specific (regulatory has "Filing Pathway", "Predicate Lineage", "PCCP Scope", "Jurisdictional Roadmap"; architecture has "Platform Boundaries", "SaMD/SiMD/HW Split", "Interoperability", etc.).

### Decision 3 — `dhf=<leaf>` tag scope key is retired

<!-- STRATEGY CONTENT: architecture -->

**Decision**: The `dhf=<leaf>` scope key in `<!-- STRATEGY CONTENT: domain, dhf=<leaf> -->` tags is deprecated. Scanner no longer requires it for routing (every domain is shared → one file per domain regardless). Existing tags that still carry the key are tolerated (scanner ignores it); tags authored going forward should omit it.

**Why**: Shared scope means there's no ambiguity to resolve — every `architecture` tag lands in the one `architecture-strategy.md`. The key was only ever needed to disambiguate per-dhf routing.

**How to apply**: Scanner implementation drops the per-dhf validation branch. The tag grammar doc notes the key as deprecated-but-tolerated.

## Blast Radius

### Strategy skill (`.claude/skills/strategy/SKILL.md`)

- **Domain Registry table**: 6 domains flip to `shared`; output paths all collapse to `docs/project/strategies/<domain>-strategy.md`
- **DHF scope resolution section**: deleted (no longer needed)
- **Scanner prompt** (`agents/scanner.md`): remove per-dhf routing logic, always emit one output per domain
- **Assembler prompt** (`agents/assembler.md`): remove DHF substitution; output path is literal
- **Best Practices table**: per-dhf strategy checks become shared checks (Scope column flips from `per-dhf` to `shared`)
- **`default-strategy.md` template**: restructure with topic-first + per-component callout shape
- **`regulatory-strategy.md` template**: same restructure, plus the regulatory-specific topic list

### Tracker skill (`.claude/skills/tracker/SKILL.md`)

- **Context & Sources §4 (Regulatory Strategy)**: path changes from `docs/project/dhfs/<dhf>/design-controls/plans/regulatory-strategy.md` → `docs/project/strategies/regulatory-strategy.md`. One file to read, not N.
- **`init` prerequisite check**: drops the per-DHF loop on regulatory strategy existence

### Medtech-docs skill (`.claude/skills/medtech-docs/`)

- **`templates/readme-strategies.md`**: expand index to list all 8 strategy docs (commercial, operations + 6 new shared: regulatory, architecture, development, testing, risk, postmarket)
- **`templates/readme-design-controls.md`**: remove references to `plans/regulatory-strategy.md`, `plans/development-strategy.md`, `architecture/architecture-strategy.md`, `vnv/testing-strategy.md`. Point reader at the shared set under `../../../strategies/`.
- **`templates/readme-risk-management.md`**: remove `risk-strategy.md` reference, point at shared
- **`templates/readme-postmarket.md`**: remove `postmarket-strategy.md` reference, point at shared
- **`add-dhf` action** (SKILL.md): stops scaffolding per-DHF strategy stubs; scaffolds only formal-output placeholders under `design-controls/plans/`, etc.
- **`init` action** (SKILL.md): scaffolds all 8 shared strategy docs under `docs/project/strategies/` at init time, not just commercial + operations

### PDLC_DEMO content

- `git mv docs/project/dhfs/pca-device/design-controls/plans/regulatory-strategy.md → docs/project/strategies/regulatory-strategy.md`
- Same for `development-strategy.md`, `postmarket-strategy.md`
- `git mv docs/project/dhfs/pca-device/design-controls/architecture/architecture-strategy.md → docs/project/strategies/architecture-strategy.md`
- Create stubs for `testing-strategy.md` and `risk-strategy.md` at `docs/project/strategies/` (they didn't exist before — `/strategy init` never populated them because the v8 check only asked for files at per-dhf paths and the task 006 scaffold didn't create them)
- Sweep any cross-links in dhfs/pca-device/ READMEs that point at the old strategy paths
- Keep the now-empty `plans/` and `architecture/` folders — they still hold formal design-control outputs (SDP, SAD, V&V Plans) that are per-DHF

### Task 006

- Status: Blocked → Not Started (unblocked by 009)
- Goals section updated: tagged blocks land in shared docs, not per-dhf paths

## Todos

- [x] Update `strategy/SKILL.md` Domain Registry to all-shared
- [x] Update `strategy/agents/scanner.md` to drop per-dhf routing
- [x] Update `strategy/agents/assembler.md` to drop dhf substitution
- [x] Restructure `strategy/templates/default-strategy.md` with topic-first + callouts
- [x] Restructure `strategy/templates/regulatory-strategy.md` same shape
- [x] Update `strategy/SKILL.md` Best Practices table (Scope flips)
- [x] Update `tracker/SKILL.md` Context & Sources + init prereq
- [x] Update `medtech-docs/templates/readme-strategies.md`
- [x] Update `medtech-docs/templates/readme-{design-controls,risk-management,postmarket}.md`
- [x] Update `medtech-docs/SKILL.md` init + add-dhf actions
- [x] Execute PDLC_DEMO `git mv` of 4 existing strategy files
- [x] Create `testing-strategy.md` + `risk-strategy.md` stubs
- [x] Sweep cross-links in dhfs/pca-device/ READMEs
- [x] Update task 006 goals + unblock it
- [x] Update task 000 index (mark 007 complete, add 009)
- [x] Bump version numbers + changelogs on all touched skills
- [x] Run `/sync-skills check` to verify drift
- [x] Review with user
- [x] `/sync-skills push --merge` to contribute back to hitachi

## Changelog

- 2026-04-13: Task created. Captured the three core decisions (shared scope, topic-first structure, retire dhf scope key) as the design section.
- 2026-04-13: Strategy/tracker/medtech-docs skill edits complete; PDLC_DEMO `git mv` of 4 strategy files done; 2 new stubs (testing, risk) created; task 006 unblocked; task 007 moved to Completed in index.
- 2026-04-13: **Terminology rename — "sub-DHF" → "DHF".** User flagged that "sub-DHF" implied a parent-child relationship but in practice the top-level entries (pca-device, connectivity-adapter, cloud-suite) are just DHFs; the "sub" was misleading. Mechanical rename across 288 live files: `sub-DHF` → `DHF`, `sub-dhf` → `dhf`, `sub_dhfs` → `dhfs`, `add-sub-dhf` → `add-dhf`. Project.yml field renamed. Template file `readme-sub-dhf.md` → `readme-dhf.md`. Historical files preserved (task 007, sync-log). Nested DHFs are now just "nested DHFs" / "child DHFs" when the relational meaning is needed — still one concept.
- 2026-04-13: Upstream push complete — PR #10 merged to hitachi `54cc8ed` (19 files). `/best-practices audit` run against PDLC_DEMO — PR-#10-specific checks all clean (dhfs key recognized, strategy scope all shared, no per-dhf fan-out, renamed template rendered across all 10 DHFs). Pre-existing gaps remain (setup.md, glossary.md, tasks/README.md, lessons-ledger, shared/agent-design-principles.md, strategy content, composition manifests) — to be handled as plumbing pass before resuming task 006.
- 2026-04-13: README review pass across 14 project READMEs + 10 DHF root READMEs. Updated 14 (stale per-DHF strategy references replaced with shared `strategies/` pointers; v10 tag convention refreshed; structure tables corrected). Created missing `docs/project/dhfs/README.md` as an index pointing at `project.yml` `dhfs[]` as source of truth. Open follow-ups: 9 stub DHF READMEs are thin/template and need device-scope content as each DHF's regulatory scope is defined (tracked as DHF-by-DHF backlog, not blocking).
- 2026-04-20: Closed out. All 18 todos checkboxes were stale — prior 2026-04-13 changelog entries already declared the work done (skill edits complete, `git mv` done, stubs created, PR #10 merged `54cc8ed`, tracker v5 + strategy v10 version bumps applied, task 006 unblocked, 007 in Completed table). Spot-checked today: `docs/project/strategies/` contains all 8 shared docs; `.claude/skills/strategy/SKILL.md:98` declares "All domains are shared (v10)"; `.claude/skills/tracker/SKILL.md:28+102` read the shared path; `.claude/sync-log.md:214` records the merge.

