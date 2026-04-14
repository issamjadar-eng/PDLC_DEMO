# Strategies

**All project strategy documents live here.** Strategy is a cross-component story — it describes how the DHFs relate to each other (filing sequence, platform architecture, one SDLC, integration V&V, platform risk chains, unified post-market program), not how each one operates in isolation. Per-component nuance is carried as **callout subsections** inside each strategy doc, not as separate per-DHF files.

## Expected Content

| File | Purpose |
|------|---------|
| `regulatory-strategy.md` | Filing pathway, predicate lineage, PCCP scope, jurisdictional roadmap, Q-Sub questions — cross-filing story across all DHFs |
| `architecture-strategy.md` | Platform boundaries, SaMD/SiMD/HW split, interoperability, cybersecurity approach, shared platform choices |
| `development-strategy.md` | SDLC, configuration management, tool chain, branching model, review gates — one process, all components |
| `testing-strategy.md` | V&V approach, integration test architecture, usability engineering, shared test infrastructure |
| `risk-strategy.md` | Risk management approach per ISO 14971, platform-level hazard chains, cross-component risk controls |
| `postmarket-strategy.md` | Post-market surveillance, maintenance plan, LMR cadence, PCCP change tracking — one PMS program |
| `commercial-strategy.md` | Pricing, reimbursement, channel, launch sequencing, customer targeting |
| `operations-strategy.md` | Manufacturing, supply chain, QMS posture, facility readiness |

## Topic-first structure with per-component callouts

Each strategy doc is organized by **strategic topic** (level-2 sections), with per-component callouts (`### PCA Device`, `### Connectivity Adapter`, `### Cloud Suite`, ...) nested as level-3 subsections under each topic. Callouts are optional — a topic that applies uniformly across all DHFs doesn't need them.

```markdown
## <Strategic Topic>

<project-level framing — the one decision, stated once>

### PCA Device
<how it applies to pca-device>

### Connectivity Adapter
<connectivity-adapter specifics — or omit if uniform>
```

This shape keeps the cross-component tradeoffs adjacent so reviewers see the whole decision surface in one place.

## Relationship to per-DHF formal plans

Strategy briefs (in this folder) are **upstream** of formal design-control outputs. The formal outputs still live per-DHF under `dhfs/<dhf>/`:

| Strategy brief (this folder) | Formal outputs it informs (per DHF) |
|---|---|
| `regulatory-strategy.md` | `dhfs/<dhf>/design-controls/plans/` 510(k) submission, PCCP protocol, LMR |
| `architecture-strategy.md` | `dhfs/<dhf>/design-controls/architecture/` SAD, SRS, cybersecurity plan |
| `development-strategy.md` | `dhfs/<dhf>/design-controls/plans/` SDP, Config Mgmt Plan |
| `testing-strategy.md` | `dhfs/<dhf>/design-controls/vnv/` V&V Plan, test protocols |
| `risk-strategy.md` | `dhfs/<dhf>/risk-management/` Risk Mgmt Plan, FMEA |
| `postmarket-strategy.md` | `dhfs/<dhf>/postmarket/` Maintenance Plan, PMS Plan |

**Rule of thumb**: if it's a *decision* (what pathway, what architecture, what approach), it belongs in the strategy brief here. If it's a *formal deliverable* required by a standard (ISO 14971, IEC 62304, 21 CFR 820.30), it belongs in the per-DHF formal folder.

## Relationship to `/strategy` skill

This folder is the destination for every strategy domain harvested from task docs by `/strategy scan` and `/strategy assemble`. Every domain is `shared` (v10+) — one output file per domain regardless of how many DHFs the project has.

Tag conventions:
- `<!-- STRATEGY CONTENT: regulatory, topics -->` → `regulatory-strategy.md`
- `<!-- STRATEGY CONTENT: architecture, topics -->` → `architecture-strategy.md`
- `<!-- STRATEGY CONTENT: commercial, topics -->` → `commercial-strategy.md`
- (and so on for every domain)

The deprecated `dhf=<leaf>` scope key is tolerated but unnecessary — if present, the scanner strips it and emits an info notice.

## Conventions

- Strategy docs are **living documents** — update at every major milestone (prototype, V&V start, filing, launch) and keep the changelog table current
- Authors should use the topic-first + per-component callout shape when writing tagged content in task docs, so assembly preserves the structure cleanly
- Do **not** copy content between strategy docs. If two docs need the same decision, promote it to a topic they both reference by link
- Do **not** duplicate per-DHF formal output content here. This folder holds the upstream *briefs* that inform those formal outputs

## For Claude

- When harvesting strategy content via `/strategy scan`, every domain lands here
- When the user asks about any strategic decision, read this folder first — it is the single source of truth
- Flag content in a formal per-DHF output (e.g., a 510(k) section) that is really a strategic decision — it should be moved upstream into a strategy doc here

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
