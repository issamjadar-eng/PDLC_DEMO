# 026 — Consider Labelling & Contracting Document Series

**ID**: 026
**Created**: 2026-04-15
**Status**: Not Started
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## Goals

_Evaluate adding two additional document series to the PDLC_DEMO coverage: **labelling** (IFU, package labels, UDI, symbols, translations, regulatory label content) and **contracting** (supplier agreements, quality agreements, licensing, service contracts, clinical trial agreements)._

- Decide whether labelling and contracting belong under an existing DHF area, `docs/project/`, or as new top-level series
- Identify upstream standards/guidance that drive each series (e.g., 21 CFR 801, EU MDR Annex I §23, ISO 15223-1 for labelling; ISO 13485 §7.4 for supplier/purchasing controls)
- Scope how they interact with existing design controls, risk, and regulatory strategy
- Produce a recommendation on structure, ownership, and sequencing

## Todos

- [ ] Survey how labelling is currently (if at all) represented in the PP3500 DHF and adjacent DHFs
- [ ] Survey contracting / supplier-control coverage in existing docs
- [ ] Map labelling requirements to applicable FDA guidance + EU MDR + ISO 15223-1 / IEC 62366 use-related labelling
- [ ] Map contracting requirements to ISO 13485 §7.4 purchasing controls and supplier quality agreements
- [ ] Propose folder structure and naming (per-DHF vs shared)
- [ ] Draft recommendation + open questions for review
- [ ] Define a versioning approach for labelling and contracting docs that cleanly accommodates **future work identified on current roadmaps** — e.g., how to represent "planned for PP3500 v1.2" or "deferred to connectivity-adapter r2" label/contract changes alongside the currently-released revision, without forking the doc tree. Consider: frontmatter `status: current|planned|deferred`, roadmap-anchored change logs, per-revision folders vs single-file changelog, and how PCCP-style pre-approved change plans interact with labelling updates

## Changelog

- 2026-04-15: Task created
