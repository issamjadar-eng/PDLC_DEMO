---
name: jira-pull
description: "Jira system-of-record mirror + drift detection for design-controls trace matrices. Pull-only — never pushes to Jira. Sibling to /trace-matrix: /trace-matrix writes the regulated deliverable from doc sources; /jira-pull mirrors Jira's canonical item universe (Epics as Design Inputs, Stories as Software Requirements, Hazards as Risk items, Test Executions as V&V) under `docs/project/_jira/<dhf>/<version>/` and emits drift reports comparing those items against DTM/HTM artifacts (canonical edge universe). Trigger when the user wants to mirror, pull, refresh, audit, or compare Jira issues for design-controls — phrases like 'pull Jira for <DHF>', 'refresh the Jira mirror', 'check drift between Jira and the DTM', 'build the unified trace from Jira', 'audit the trace matrix for drift', 'sync Jira issues to the project'. Also trigger when the user asks why a DI is missing from the trace, why a Story has no V&V, or wants to know which Jira items are not in the DTM. Three categories of drift rule (A: item-universe mismatch, B: edge-universe incompleteness, C: metadata mismatch). Project-agnostic: reads project.yml `change_control.jira` (cloud_id, base_url, project_keys, field_set, cache) and `dhfs[].jira` (project_key, versions[], story_filter) plus `dhfs[].evidence.design_traceability_matrix` (xlsx schema map with sheet/header_row/columns/extractors)."
version: 1
updated: 2026-05-03
---

# Jira Pull Skill

Mirror Jira issues for design-controls traceability and detect drift between Jira (canonical item universe) and the regulated artifacts under `docs/project/_confluence/` (canonical edge universe — DTM xlsx, HTM xlsx).

Usage: `/jira-pull <action> [flags]`

This skill is the **mirror writer + auditor**. It is a sibling to `/trace-matrix` (which writes the regulated trace-matrix deliverable from doc sources). The two skills cooperate — `/trace-matrix` answers "is the controlled trace matrix internally consistent?"; `/jira-pull` answers "does the controlled trace matrix agree with what's in Jira today?"

## Two universes, one comparison

| Universe | Lives in | Held by |
|---|---|---|
| **Item universe** — the set of valid trace nodes | Jira (Epics for Design Inputs, Stories for Software Requirements, Hazards for Risk, Test Executions for V&V) | This skill mirrors it under `docs/project/_jira/` |
| **Edge universe** — the set of trace links UN→DI, DI→SW, DI→Hazard, DI→V&V | DTM xlsx + HTM xlsx + Jira `parent`/`issuelinks` | Per-DHF `evidence:` blocks in `project.yml` declare the schema |
| **Drift** | discrepancy report | `audit` action emits `drift.json` + `drift.md`; project console renders inline badges |

## Pull-only directionality (HARD RULE)

This skill **never writes to Jira**. There is no `push` action by design.

- The `/jira-pull` action surface is `refresh`, `build-trace`, `audit`. None of them write back to the Atlassian site.
- Output files under `docs/project/_jira/` carry **no Confluence frontmatter**, so `/change-control publish` skips them naturally.
- If the user wants to update a Jira issue, they do it in Jira's UI. The next `refresh` brings the change into the mirror.

This stance differs from `/change-control`'s bidirectional Confluence sync. Jira is a system of record (downstream of regulated processes); the project repo is not authoritative over it.

## Drift as first-class output

The `audit` action emits structured drift violations grouped into three rule categories. Each rule has a severity (`error` / `warning` / `info`) and a resolution hint.

| Category | What it covers | Rule signatures (registry) |
|---|---|---|
| **A — Item drift** | universe mismatch: items present in one source but not the other | A1 Jira-only DI, A2 DTM-only DI, A3 Jira-only SW, A4 DTM-only SW, A5 Jira-only Hazard, A6 HTM-only Hazard, A7 Jira-only Test, A8 DTM-only Test |
| **B — Edge drift** | link incompleteness: trace edge missing in either source | B1 DI without UN, B2 DI without SW children, B3 DI without V&V, B4 DI without Hazard, B5 UN without DI, B6 SW without parent DI, B7 Hazard without DI, B8 Hazard without mitigation/V&V |
| **C — Metadata drift** | item attributes differ across sources | C1 status mismatch, C2 summary drift, C3 version/scope mismatch, C4 ID format drift, C5 stale WORKING xlsx |

Rule registry: `lib/drift_rules.py`. Each rule is a pure function `(jira_state, dtm_state, htm_state, cfg) -> [Violation]`. Severities tunable per project via `project.yml` `jira_pull.severity_overrides`. The registry is project-agnostic — DI/UN/PHA prefix regexes come from `project.yml` per-DHF `evidence.*.extractors` blocks.

## Project-agnostic configuration

Every project-specific value comes from `project.yml`. The skill reads:

| Field | Used for |
|---|---|
| `change_control.jira.cloud_id` | Atlassian cloud (passed to MCP) |
| `change_control.jira.base_url` | Browse-link prefix in rendered markdown |
| `change_control.jira.project_keys[]` | JQL project clause |
| `change_control.jira.field_set` | Fields to request from Jira |
| `change_control.jira.cache.root` | Local cache directory |
| `change_control.jira.cache.max_age_hours` | Cache TTL (`--force` overrides) |
| `dhfs[].architecture_name` | Output folder name (lowercased, hyphenated) |
| `dhfs[].jira.project_key` | Per-DHF JQL project clause (usually same as top-level) |
| `dhfs[].jira.versions[].id` | Output version subfolder |
| `dhfs[].jira.versions[].fix_version` | JQL `fixVersion` clause |
| `dhfs[].jira.story_filter.labels` | JQL `labels in (...)` clause |
| `dhfs[].jira.story_filter.statuses` | JQL `status in (...)` clause |
| `dhfs[].evidence.design_traceability_matrix[]` | DTM xlsx schema map (sheet, header_row, columns, extractors, tbd_value) |
| `jira_pull.exempt_filters` (optional) | Drift-exemption rules (label-based or summary-pattern) for tracking Epics that intentionally don't appear in the DTM |
| `jira_pull.severity_overrides` (optional) | Rule severity tuning per project |
| `jira_pull.di_resolution.fallback` (optional) | Fallback DI-resolution for Epics without a `DI-NNNN` summary prefix — `parent_walk`, `custom_field`, or `static_map` |

No Atlassian site, project, or device names live in the skill source. Forking-by-hard-coding is the wrong move; project values belong in `project.yml`.

## Output layout

```
docs/project/_jira/
├── README.md                       ← purpose + pull-only HARD RULE (authored separately)
├── _meta.json                      ← top-level last-refresh metadata
├── _global/
│   └── user-needs.json             ← (future) UN extraction once external source identified
├── <arch-name-lowercased>/         ← e.g. pre-op, intra-op, mgmt-services
│   ├── _meta.json                  ← per-DHF available versions
│   └── <version-id>/               ← e.g. v1.0.0, v2.0.0
│       ├── _meta.json              ← jql, pulled_at, cloud_id, issue_counts
│       ├── epics.json + epics.md   ← Design Inputs (issuetype=Epic)
│       ├── stories.json + stories.md ← Software Requirements (issuetype=Story)
│       ├── hazards.json + hazards.md ← Risk items (issuetype=Hazard)
│       ├── tests.json + tests.md   ← V&V (issuetype=Test Execution; inverse "1 Relates"→Story)
│       ├── unknowns.json           ← items where the resolver could not bind a trace edge
│       ├── unified-trace.md        ← UN→DI→SW→DO/V&V/Risk walk; Unknown placeholders; inline drift badges
│       ├── drift.json              ← structured Category A/B/C violations
│       └── drift.md                ← human-readable drift report (count by severity, by rule)
└── _cache/                         ← request cache (gitignored), TTL = change_control.jira.cache.max_age_hours
```

**Folder naming uses architecture names, not Jira's legacy fixVersion strings.** A DHF's mirror folder is `dhfs[].architecture_name` lowercased and hyphenated — e.g. an architecture name `Management Services` becomes `mgmt-services/`. The mapping from Jira's fixVersion strings to architecture/marketed names lives in `project.yml`.

## Supporting Files

| File | Purpose |
|------|---------|
| `README.md` | Design document — architecture, lineage, dependencies |
| `actions/refresh.py` | Pull Epics / Stories / Hazards / Test Executions per DHF×version; write JSON+MD |
| `actions/build_trace.py` | Walk Epic→Stories→inverse Test Executions; emit `unified-trace.md` |
| `actions/audit.py` | Compare Jira vs DTM/HTM via rule registry; emit `drift.json` + `drift.md` |
| `lib/config.py` | Read `project.yml`; resolve per-DHF Jira + evidence config |
| `lib/jira_client.py` | Wrapper around the Atlassian MCP search tool — pagination, retries, deterministic field ordering |
| `lib/dtm_reader.py` | Parse a DTM xlsx using the `dhfs[].evidence.design_traceability_matrix` schema map; normalize to `{di_rows, un_rows, hazard_rows, …}` |
| `lib/htm_reader.py` | Parse HTM page + xlsx; normalize hazard→DI/SW edges |
| `lib/drift_rules.py` | Rule registry — Category A / B / C signatures + dispatch + severity resolution |
| `lib/render.py` | Markdown renderers — issue tables, unified-trace, drift report |
| `references/drift-rule-catalog.md` | Full prose catalog of every rule (A1–A8, B1–B8, C1–C5) with detection logic + resolution hint examples |
| `tests/test_drift_rules.py` | Unit tests over the drift-rule registry — synthetic in-memory fixtures (no live Jira/Confluence calls); one clean + one drift case per implemented rule, plus a meta-test that locks unimplemented rules to `NotImplementedError`. Run via `python3 .claude/skills/jira-pull/tests/test_drift_rules.py`. |

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action.

### `refresh` — pull Jira state into the local mirror

`/jira-pull refresh --dhf <leaf> --version <id>` pulls one DHF×version snapshot. `--all` walks every DHF×version in `project.yml`. `--check` compares cache vs live and reports diffs without writing. `--force` ignores the cache TTL.

1. **Resolve config.** `lib.config.resolve(dhf, version)` returns the merged config: top-level `change_control.jira`, the DHF's `dhfs[].jira` block, and the version entry. Validate that the version `id` exists in `dhfs[].jira.versions[]`.
2. **Build JQL.** Per layer (Epic / Story / Hazard / Test Execution):
   - `project = "<project_key>" AND fixVersion = "<fix_version>" AND issuetype = "<type>"`
   - For Stories, append `AND labels in (<story_filter.labels>) AND status in (<story_filter.statuses>)` if those filters are configured.
3. **Issue Atlassian MCP search.** Call `mcp__atlassian__searchJiraIssuesUsingJql` with `cloudId`, `jql`, `fields=change_control.jira.field_set.common`, `maxResults=100`. Paginate via `nextPageToken` until `isLast: true`. Stable response handling — record `_meta.mcp_response_size` for provenance.
4. **Cache.** Hash `(jql, field_set)` → write the raw response to `change_control.jira.cache.root/<hash>.json`. On `--check`, read the cache and diff against the new pull instead of writing.
5. **Dedupe on `key`.** Cross-version Epic reuse is real (a single Jira key can appear in multiple `fixVersions`). The per-version mirror file lists the issue under each version; downstream consumers (system-DHF aggregate) dedupe on key, not on `(version, key)`.
6. **Write JSON.** UTF-8, 2-space indent, sorted keys, `_meta` block at top with `{ jql, pulled_at, cloud_id, fix_version, fix_version_id, issue_counts, mcp_response_size }`. Deterministic byte output for clean PR diffs. Files: `epics.json`, `stories.json`, `hazards.json`, `tests.json`.
7. **Render Markdown.** GFM tables — issue key linked to `<base_url>/browse/<KEY>`. Columns per layer:
   - Epics: DI prefix (extracted via `evidence.*.extractors.design_input_id`), Jira key, summary, status, parent count, labels.
   - Stories: Jira key, summary, parent Epic (DI prefix if resolvable), status, fixVersions, labels.
   - Hazards: PHA prefix, Jira key, summary (harm description), status, issuelink count.
   - Tests: Jira key, target Story (browse-linked), result/status, defect-link count.
8. **Write `_meta.json`** at the version level and update the DHF-level `_meta.json` to list this version's `pulled_at`.
9. **Report**: number of issues per type, cache-hit/miss, and any pagination depth.

**No Confluence frontmatter** — the absence is what causes `/change-control publish` to skip the folder.

### `build-trace` — emit the unified-trace markdown

`/jira-pull build-trace --dhf <leaf> --version <id>` produces `unified-trace.md` walking UN → DI → SW → Design Outputs / V&V / Risk. UN data does NOT come from Jira (no UN issuetype) — it comes from the DTM xlsx (column `user_need` per the evidence schema map) or, when present, an external UN-bearing source registered as `dhfs[].evidence.user_needs`.

1. **Load Jira state** from the mirrored JSON (no live calls — the trace is built off the cached snapshot).
2. **Load DTM state** via `lib.dtm_reader` against `dhfs[].evidence.design_traceability_matrix`. Apply the column map; treat the configured `tbd_value` (typically `"TBD"`) and empty cells (when `empty_means_unknown: true`) as Unknown.
3. **Load HTM state** when `dhfs[].evidence.hazard_traceability_matrix` is configured.
4. **Build the trace graph.**
   - **DI nodes**: union of (DTM rows w/ `design_input_id` extracted) ∪ (Jira Epics, joined by extracted DI prefix on `summary`). Where the DI-prefix is missing on a Jira Epic (low coverage on enhancement/research Epics), fall back per `jira_pull.di_resolution.fallback`: walk `parent.key` to a DI-prefixed ancestor, read a configured custom field, or look up a static `project.yml` `key→DI` map.
   - **UN nodes**: from DTM column `user_need` (when populated). Mark `Unknown — UN` for DI rows with no UN populated.
   - **SW nodes**: Jira Stories with `parent.key == DI Epic key`.
   - **V&V nodes**: walk Stories' inverse issuelinks — Test Executions whose `issuelinks[type=="1 Relates"].inwardIssue.key` matches the Story. (Note: Stories carry no outbound test issuelinks — the edge is held by Test Executions inwardly.)
   - **Risk nodes**: DTM column `hazard_refs` (PHA-NN list, comma-separated) ∪ Jira Hazards with matching PHA prefix in `summary` ∪ HTM rows.
5. **Emit Unknown placeholders** with category hints: `Unknown — UN`, `Unknown — DI`, `Unknown — SW`, `Unknown — V&V`, `Unknown — Risk`. Every emit-Unknown call must carry a category.
6. **Inline drift badges.** If `drift.json` exists alongside (from a prior `audit`), annotate each row with `✓` (no drift), `⚠ <rules>` (warnings), or `✗ <rules>` (errors). Add a "Drift Summary" section with counts by severity and rule, plus a "Drift Details" appendix with resolution hints.
7. **Write** `unified-trace.md` deterministically (sorted by DI ID, then by UN ID within DI).

### `audit` — emit drift.json + drift.md

`/jira-pull audit --dhf <leaf> --version <id>` runs the rule registry against the cached Jira state and the live DTM/HTM parse. Emits structured drift artifacts.

1. **Load states**: Jira from mirror JSON; DTM/HTM via the readers (no Jira live calls).
2. **Apply exempt filters** from `project.yml` `jira_pull.exempt_filters` before rule evaluation. Exempt filters are commonly used for tracking-style Epics (e.g., "QMS Documentation" tracking Epics) that intentionally don't have DTM rows. Filter spec is project-agnostic — it's `{ kind: label|summary_regex, value: ... }` — never matches by hardcoded summary text in the skill itself.
3. **Run the registry.** Each rule in `lib.drift_rules.RULES` is a function `(jira_state, dtm_state, htm_state, cfg) -> List[Violation]`. The rule emits zero or more violations. The runner:
   - Honors `jira_pull.severity_overrides` (per-rule severity tuning).
   - Skips rules whose source state is missing (e.g., skip B7 if HTM is not configured).
   - Aggregates violations into Category A / B / C buckets.
4. **Refine A1 (Jira-only DI).** Apply only to Epics that are design-inputs — DI-prefixed OR carrying a configured "design-input" label. Without that, infrastructure / research / tracking Epics flood drift output as false positives.
5. **Write `drift.json`.** Deterministic, sorted by `(category, rule_id, item_id)`. Schema:
   ```json
   {
     "_meta": { "generated_at": "...", "dhf": "<leaf>", "version": "<id>" },
     "summary": { "by_severity": {...}, "by_category": {...}, "by_rule": {...} },
     "violations": [
       { "rule": "A1", "severity": "error", "item_id": "AFAI-...", "message": "...", "resolution_hint": "..." }
     ]
   }
   ```
6. **Write `drift.md`.** Sections: Summary (severity/category/rule counts), then per-rule lists of violations grouped by severity. Each violation links the offending Jira/DTM item.

### `setup`

Wire up any hooks the skill ships. Currently the skill ships no hooks — the `setup` action is reserved for forward compatibility (e.g., a future SessionStart hook to refresh stale caches). Today it is a no-op that prints a friendly status line.

If hooks are added later, this action will follow the conventional pattern: create `.claude/hooks/`, symlink each hook from the skill's `hooks/` directory, and register via `register-hook.sh`. Idempotent — safe to re-run.

## Best Practices

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill installed | `.claude/skills/jira-pull/SKILL.md` exists | Required | shared |
| README.md exists | `.claude/skills/jira-pull/README.md` exists | Required | shared |
| Project-agnostic source | Skill files contain no project-specific names (cloud IDs, project keys, device names, prefix regexes hardcoded) | Required | shared |
| Pull-only directionality | Skill source contains no Jira write/update/transition operations; no `push` action defined | Required | shared |
| Output frontmatter-free | Files written under `docs/project/_jira/` carry no Confluence frontmatter (so `/change-control publish` skips them) | Required | local |
| Folder naming | Output folders use `dhfs[].architecture_name` lowercased-hyphenated, not Jira fixVersion strings | Required | local |
| project.yml shape | `change_control.jira` and per-DHF `dhfs[].jira` blocks present and resolve to live fixVersions | Required | local |
| DTM schema map present | Each item-DHF `evidence.design_traceability_matrix[].columns` declares the column-letter map | Required | local |
| Rule registry signatures | Every rule in `lib/drift_rules.py` is `(jira_state, dtm_state, htm_state, cfg) -> List[Violation]` | Recommended | shared |
| Deterministic JSON | All written JSON files are 2-space indent, sorted keys, with `_meta` block | Recommended | shared |

## Notes

- If `$ARGUMENTS` is empty or just `help`, show this usage guide.
- The skill expects the Atlassian MCP server to be configured. Without it, `refresh` cannot run; `build-trace` and `audit` operate off the cached JSON if present.
- `unified-trace.md` and `drift.md` are deliberately **derivative** — they are regenerated from `*.json` + the rule registry. Hand-edits will be overwritten on the next run.
- DI-resolution fallback strategies are tried in declared order in `jira_pull.di_resolution.fallback`. Recommended chain: `parent_walk` first (cheapest), `static_map` second (deterministic override), `custom_field` only when a configured Jira field carries the DI ID directly.
- The skill is **read-only against Jira but write-capable against the project repo**. Honor `.claude/rules/readme-before-write.md` and `.claude/rules/sentinel-blocks.md` when emitting markdown into `docs/project/_jira/`.

## Changelog

- 1 (2026-05-03): Initial scaffold — defines the contract, action surface, project.yml-driven configuration, drift-rule taxonomy (Categories A / B / C with rule IDs), output layout, and pull-only directionality. No implementation code yet — `actions/`, `lib/`, and `references/` carry stubs and rule signatures.
