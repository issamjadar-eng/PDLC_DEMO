# 028 — Product Feature Strategy Document

**ID**: 028
**Created**: 2026-04-15
**Status**: Not Started
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## Goals

_Author a **product feature strategy** document that sits alongside the existing shared strategy domains (regulatory, architecture, development, testing, risk, postmarket, commercial) and captures **what the product does and why** — the feature set, differentiation, user-value hierarchy, and the rationale tying features to user needs, market positioning, and roadmap._

- Establish "product feature strategy" as a first-class strategy domain under `docs/project/strategies/` (topic-first shape, per-component callouts for PP3500 + connectivity-adapter + cloud-suite)
- Define the document's scope: feature inventory, feature-to-user-need mapping, differentiation vs predicate/competitors, MVP vs future-release feature tiers, feature deprecation policy
- Clarify boundaries with neighbouring strategies: regulatory (filing scope), architecture (how features map to modules), commercial (pricing/positioning), risk (feature-driven hazards), roadmaps (when features land)
- Update `/strategy` skill to recognize `product-feature` (or chosen domain name) as a harvestable domain, including tag format and harvesting target
- Produce a first-pass PP3500 product feature strategy doc populated from existing input-analysis + strategy content

## Todos

- [ ] Pick the domain name (`product-feature`, `product`, `features`, `product-strategy`) and confirm with user
- [ ] Inventory where feature-level content currently lives (input analysis, strategy docs, README snippets, task notes)
- [ ] Define the document template — sections, frontmatter, tag format for harvesting
- [ ] Map how product feature strategy intersects roadmaps (task 027), regulatory strategy, architecture strategy
- [ ] Update `/strategy` skill (domain list + harvesting logic) and `/medtech-docs` (scaffold)
- [ ] Author the first-pass PP3500 product feature strategy doc at `docs/project/strategies/product-feature-strategy.md`
- [ ] Sister-project validation against `../../projects/arthrex/pccp/`
- [ ] `/sync-skills push` upstream to hitachi

## Changelog

- 2026-04-15: Task created. Adds product feature strategy as a new first-class strategy domain — the "what the product does and why" lens that currently has no dedicated home.
