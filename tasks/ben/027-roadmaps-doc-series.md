# 027 — Roadmaps Document Series

**ID**: 027
**Created**: 2026-04-15
**Status**: Not Started
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## Goals

_Add a dedicated **roadmaps** document series to PDLC_DEMO so planned future work is first-class alongside released DHF content. Roadmaps are the anchor that task 026's labelling/contracting versioning (and every other series that needs to represent "planned vs current") points back to._

- Decide scope: product roadmap, regulatory roadmap (filings, PCCPs, jurisdictions), platform/technology roadmap, clinical evidence roadmap, post-market roadmap
- Decide placement: shared `docs/project/roadmaps/` vs per-DHF `dhfs/<name>/roadmap/` vs both (shared program-level + per-DHF component-level)
- Define the canonical "roadmap item" shape — id, title, target release/window, status (idea → planned → committed → in-progress → shipped → deferred), owning DHF(s), linked tasks, linked strategy decisions, linked risks
- Establish the cross-reference contract other series use to point at roadmap items (frontmatter key, id format) so labelling/contracting/design-controls can mark content as "planned for roadmap item X"
- Recommend tooling: whether the tracker skill should surface roadmaps, whether project-console gets a Roadmaps section, whether `/strategy` harvesting should auto-populate roadmap entries from strategy blocks

## Todos

- [ ] Survey how roadmap-type content is currently scattered (strategy docs, task changelogs, PCCP narratives, README "future work" sections)
- [ ] Define roadmap item schema (frontmatter + markdown body)
- [ ] Decide shared vs per-DHF placement and name the folder(s)
- [ ] Specify the cross-reference key other doc series use to link into roadmaps
- [ ] Align with task 026 versioning approach — roadmaps own the timeline, other series reference it
- [ ] Identify which existing strategy content would migrate into roadmap entries vs stay as strategy
- [ ] Decide tooling: tracker integration, console section, harvesting from tagged blocks
- [ ] Draft recommendation + open questions for review

## Changelog

- 2026-04-15: Task created. Spun off from task 026's versioning discussion — roadmaps need to exist as their own series before labelling/contracting (or anything else) can cleanly reference "planned for future release."
