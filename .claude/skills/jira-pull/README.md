# Jira Pull — Design & Architecture

Design document for the `jira-pull` skill. Not loaded by Claude during normal operation — exists for human understanding and as the skill's index layer.

For skill usage and instructions, see `SKILL.md`.

## Overview

`jira-pull` is the Jira system-of-record mirror + drift-detection writer for design-controls trace matrices. Its job is to:

1. **Mirror** Jira's canonical item universe (Epics for Design Inputs, Stories for Software Requirements, Hazards for Risk, Test Executions for V&V) into a local, frontmatter-free, pull-only `docs/project/_jira/` tree.
2. **Walk** the trace graph (UN → DI → SW → Design Outputs / V&V / Risk) and emit a single `unified-trace.md` per DHF×version with `Unknown` placeholders for every unresolved trace edge.
3. **Audit** drift — compare Jira's canonical items against the regulated artifacts (DTM xlsx, HTM xlsx) which hold the canonical trace edges, and emit `drift.json` + `drift.md` with structured violations grouped into three rule categories.

## Lineage

Original skill, not adapted from a prior version. It is a **sibling to** `/trace-matrix` and `/change-control`, not a replacement:

| Skill | Owns | Reads | Writes |
|---|---|---|---|
| `/trace-matrix` | the regulated trace-matrix deliverable per DHF | doc-source files (markdown, xlsx) under each DHF's `design-controls/` | `design-controls/trace-matrix/trace-matrix.{md,json}` |
| `/change-control` | bidirectional Confluence/Windchill bridge | Confluence pages + Comala/SoftComply state | `docs/project/_confluence/...` + Confluence (publish) |
| `/jira-pull` | Jira mirror + drift detection | Jira (via Atlassian MCP), DTM/HTM xlsx via project.yml `evidence:` blocks | `docs/project/_jira/...` (pull-only — never to Jira) |

## Key Design Decisions

### Pull-only directionality is structural, not procedural

The skill has no `push` action. Not a flag, not an opt-in — it doesn't exist. The action surface is `refresh` / `build-trace` / `audit`, and none of them mutate Jira.

Why structural rather than procedural: a procedural rule ("don't push") is one cleanup PR away from being broken; a structural absence cannot be accidentally invoked. Output files also carry no Confluence frontmatter, so `/change-control publish` skips them naturally — the absence of frontmatter is a load-bearing detail.

### Drift is a first-class output, not an audit overlay

Earlier designs framed drift as an "audit overlay" on top of a Jira-primary trace render. We rejected that framing: in regulated trace-matrix work, **the discrepancies are the value**. Reviewers don't need a polished Jira-only render; they need a list of every place the controlled artifacts and the live system disagree.

Concretely: every row in `unified-trace.md` carries an inline drift badge (`✓` / `⚠ <rules>` / `✗ <rules>`); a Drift Summary block at the top counts violations by severity and rule; a Drift Details appendix lists each violation with a resolution hint. The structured `drift.json` is the contract for project-console's drift visualization layer.

### Project-agnostic by configuration, not abstraction

The skill source contains no project-specific names — no cloud IDs, no project keys, no device names, no DI/UN/PHA prefix regexes. Project specifics live in `project.yml`:

- Top-level `change_control.jira` carries Atlassian site config (cloud_id, base_url, project_keys, field_set, cache).
- Per-DHF `dhfs[].jira` carries the version mapping (fixVersion strings, version IDs, story_filter).
- Per-DHF `dhfs[].evidence.design_traceability_matrix[]` carries the DTM xlsx schema map (sheet, header_row, column-letter map, prefix extractor regexes, tbd_value).
- Optional `jira_pull.exempt_filters`, `jira_pull.severity_overrides`, `jira_pull.di_resolution.fallback` carry project-specific tuning without skill source changes.

This means the same skill serves multiple projects from the registry — each project provides its own `project.yml`. A skill that hard-codes one project's names cannot be reused.

### Drift rule registry as pure functions

Each rule in `lib/drift_rules.py` is a pure function `(jira_state, dtm_state, htm_state, cfg) -> List[Violation]`. No global state, no rule-internal config reads — everything comes through arguments. This makes the registry:

- **Trivially testable** — pass synthetic states, assert on violations.
- **Composable** — the runner can invoke a subset of rules, pass project-specific config, and merge results.
- **Project-agnostic** — DI/UN/PHA prefix regexes come from `cfg.extractors`, not from rule source.
- **Severity-tunable** — runner consults `cfg.severity_overrides` after the rule emits a violation, so projects can downgrade or upgrade per their conventions.

### Folder names use architecture, not Jira's legacy strings

Jira fixVersion strings are system-of-record names that may have inherited legacy naming (e.g., a project's mgmt-services component might ship under a fixVersion that conflates two distinct architecture components, reflecting a prior marketing era). The mirror folder uses the project's canonical `architecture_name` (lowercased and hyphenated), and `project.yml` carries the mapping. This keeps the local tree readable independent of upstream naming churn, without rewriting Jira.

## Dependencies

| File / external | Required by | Purpose |
|---|---|---|
| `project.yml` `change_control.jira` | refresh, audit | Atlassian site + cache config |
| `project.yml` `dhfs[].jira` | refresh, build-trace, audit | Per-DHF Jira binding (project_key, versions[], story_filter) |
| `project.yml` `dhfs[].architecture_name` | refresh | Output folder name |
| `project.yml` `dhfs[].evidence.design_traceability_matrix[]` | build-trace, audit | DTM xlsx schema map |
| `project.yml` `jira_pull.*` (optional) | refresh, build-trace, audit | Per-project tuning |
| Atlassian MCP (`mcp__atlassian__searchJiraIssuesUsingJql`) | refresh | Jira read access |
| `openpyxl` (Python lib) | build-trace, audit | DTM/HTM xlsx parsing |
| `docs/project/_jira/README.md` | (project-authored) | Folder purpose + pull-only HARD RULE for human readers |

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill installed | `.claude/skills/jira-pull/SKILL.md` exists | Required | shared |
| README.md exists | `.claude/skills/jira-pull/README.md` exists | Required | shared |
| Project-agnostic source | Skill source files contain no hardcoded project keys, cloud IDs, device names, or prefix regexes | Required | shared |
| Pull-only directionality | Skill source contains no Jira write/transition operations; no `push` action exists in `actions/` | Required | shared |
| Frontmatter-free output | Files written under `docs/project/_jira/` carry no Confluence frontmatter (so `/change-control publish` skips them) | Required | local |
| Folder naming | Output folders use `dhfs[].architecture_name` lowercased-hyphenated, not Jira fixVersion strings | Required | local |
| project.yml jira config | `change_control.jira` and per-DHF `dhfs[].jira` blocks present and resolve to live fixVersions | Required | local |
| DTM schema map present | Each item-DHF `evidence.design_traceability_matrix[].columns` declares the column-letter map | Required | local |
| Rule registry signature | Every rule in `lib/drift_rules.py` is `(jira_state, dtm_state, htm_state, cfg) -> List[Violation]` | Recommended | shared |
| Deterministic JSON output | All written JSON files are 2-space indent, sorted keys, with `_meta` block | Recommended | shared |

## Changelog

- 2 (2026-09-08): Three evidence tiers in the test suite — `unit` / `mocked` / `live` pytest markers, a `--live` opt-in option, and an autouse socket guard that fails any non-`live` test that opens a network connection (`tests/conftest.py`, `tests/jirapull_testkit.py`). New mocked-tier suite `tests/test_refresh_mocked.py` with canned Atlassian search pages under `tests/fixtures/atlassian/` covering the JQL cursor protocol, every accepted response envelope, multi-page merge + dedupe, normalization, and `_meta` provenance. `actions/refresh.py`: page concatenation + key-dedupe extracted into a pure `merge_pages()` seam (behavior unchanged). `test_drift_rules.py`: the `test_exec` fixture builder is opted out of pytest collection (`__test__ = False`) — it collected as a broken test under pytest. The MCP search call itself is agent-mediated and stays outside pytest; the `live` placeholder can only probe the configured base URL.
- 1 (2026-05-03): Initial scaffold — defines contract + action surface + project.yml-driven configuration + drift-rule taxonomy (Categories A / B / C, rule IDs, severities, resolution hints) + output layout + pull-only directionality. Ships SKILL.md, README.md, drift-rule catalog reference, and stubs for `actions/` and `lib/drift_rules.py`. No implementation code yet — first pull / build-trace / audit runs are deferred to subsequent iterations.
