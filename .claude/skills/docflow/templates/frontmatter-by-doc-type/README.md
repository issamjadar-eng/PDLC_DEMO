# Doc-Type Frontmatter Overlays

**Status (2026-04-21)**: Phase A scaffold under task ben/089. Stubs only — populated in Phase E.

## Purpose

Each overlay extends the base `frontmatter-project.md` schema with type-specific aggregate fields. The orchestrator (`scripts/adopt.py`, written in Phase F) merges the overlay into the base frontmatter at adopt time based on the doc-type classifier's output.

This is what makes downstream tooling (tracker, dashboard, advisors, lessons, strategy) able to query across the DHF without parsing per-document structure. The aggregates are populated from the per-document content during Phase 6 frontmatter build.

## Overlay registry

| Overlay | Doc Type | Aggregate fields added | Populated from |
|---------|----------|------------------------|----------------|
| `requirement.yml` | requirement | `requirements:` (count, epics map, classification distribution, target_releases, traces_to resolved/unresolved, status distribution, criticality distribution) | R1 per-requirement attributes table parsing |
| `trace-matrix.yml` | trace-matrix | `trace_targets:` (count, source-type/target-type matrix, coverage stats, unresolved edges) | Trace-matrix table parsing |
| `risk-doc.yml` | risk-doc | `hazards:` (count, severity distribution, probability distribution, risk-control coverage, residual-risk acceptability) | Risk matrix table parsing |
| `cybersec-doc.yml` | cybersec-doc | `threats:` (count by category, mitigation coverage), `sbom:` (component count, CVE count, license summary) — only one populated based on doc subtype | Threat-model + SBOM table parsing |
| `vnv-doc.yml` | vnv-doc | `tests:` (count, pass/fail/blocked distribution, requirements coverage, automated/manual ratio) | Test-protocol table parsing |

## Conventions

- Overlay files are YAML fragments (not full frontmatter blocks). The orchestrator deep-merges them into the base.
- Each overlay declares its own `version:` so future schema changes can be tracked independently.
- Doc types not listed here use the base `frontmatter-project.md` schema unmodified.
- Overlay aggregates are computed deterministically from MD content — no LLM needed for aggregation. The agents only emit the structured content; the script does the rollup.

## Changelog

- 2026-04-21: README created during task ben/089 Phase A scaffolding.
