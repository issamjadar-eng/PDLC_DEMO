# Drift Rule Catalog

Full prose reference for every drift rule in `lib/drift_rules.py`. Loaded as needed — not bundled into SKILL.md to keep the per-trigger context lean.

Each rule has: rule ID, description, natural severity, detection logic, resolution hint. Severity is tunable per project via `project.yml` `jira_pull.severity_overrides`. Detection references project.yml-driven extractors and column maps; nothing is hardcoded against a particular project's prefix conventions.

## Category A — Item drift (universe mismatch)

The set of valid trace nodes. Items present in one source (Jira / DTM / HTM) but missing in another.

### A1 — Jira-only DI

**Severity:** error.
**Detection:** for each Jira Epic in scope (`fixVersion = <version>`):
1. Determine if it is a design-input — has a `design_input_id` extracted from its summary, OR carries a configured `cfg.design_input_label`. Skip if neither.
2. Check whether any DTM row's `design_input` column resolves to the same DI.
3. If no DTM row matches and no exempt filter applies, emit a violation.

**Resolution hint:** add a row to the DTM, or remove the Epic from this fixVersion if obsolete.

**Why the design-input check matters:** without it, every infrastructure / research / tracking Epic in Jira floods the drift output. The check is what makes A1 useful in real projects where Jira holds many non-DI Epics.

### A2 — DTM-only DI

**Severity:** error.
**Detection:** for each DTM row with an extractable `design_input_id`, check that some Jira Epic has the same ID extracted from its summary (or a configured custom field).
**Resolution hint:** Jira Epic was deleted (update DTM) or DTM has a typo.

### A3 — Jira-only SW (Story)

**Severity:** warning.
**Detection:** for each Story in scope, check the DTM has a row referencing it (by Jira key or extracted SW ID — depends on project convention).
**Resolution hint:** add an SW row to the DTM.

### A4 — DTM-only SW

**Severity:** warning.
**Detection:** symmetric to A2 for SW IDs.
**Resolution hint:** restore the Jira Story or update the DTM.

### A5 — Jira-only Hazard

**Severity:** warning.
**Detection:** for each Jira Hazard in scope:
1. Extract its hazard ID (e.g., PHA-NN) via `cfg.extractors.hazard_id`.
2. Check the HTM xlsx has a row referencing it, OR the DTM column `hazard_refs` (when present) lists it.
**Resolution hint:** add the Hazard to the HTM.

### A6 — HTM-only Hazard

**Severity:** warning.
**Detection:** symmetric to A2 for Hazard IDs.
**Resolution hint:** restore Jira Hazard or update HTM.

### A7 — Jira-only Test Execution

**Severity:** info.
**Detection:** for each Test Execution in scope, check the DTM and STR (Software Test Results) cite its key.
**Resolution hint:** may be exploratory test, not always required in DTM. Info-level reflects that.

### A8 — DTM-only Test

**Severity:** warning.
**Detection:** symmetric — DTM cites a test that has no Jira Test Execution.
**Resolution hint:** DTM may reference offline/manual test; investigate.

## Category B — Edge drift (link incompleteness)

The set of trace links. Edges missing in one or both sources.

### B1 — DI without UN

**Severity:** error.
**Detection:** for each DI Epic (post-A1 filtering), check at least one DTM UN row references it through the DTM's `design_input` column.
**Resolution hint:** add UN→DI mapping in DTM, OR confirm DI is intentionally unrelated to a User Need.

### B2 — DI without SW children

**Severity:** warning.
**Detection:** for each DI Epic, query `parent.key == epic.key` against Jira Stories. If empty, emit.
**Resolution hint:** decompose DI into Stories, OR DI may be reqs-only (e.g., performance budget).

### B3 — DI without V&V

**Severity:** error (with info-downgrade clause).
**Detection:**
1. Walk DI → child Stories.
2. For each Story, walk inverse `issuelinks[type == "1 Relates"]` to find Test Executions.
3. If no Test Executions resolve, the DI has no Jira-side V&V.
4. If the DTM column `verification` is also TBD/empty, emit `error`.
5. If Jira Test Executions DO exist but the DTM column `verification` is TBD, emit `info` with message "DTM-not-yet-populated; Jira coverage = N tests" — distinguishes "no V&V" from "V&V exists, DTM lags".

**Resolution hint:** add V&V coverage, OR document why DI is exempt.

### B4 — DI without Hazard

**Severity:** info.
**Detection:** for each DI, check HTM has at least one Hazard→DI row. Often intentional for non-safety-critical DI; info-level reflects this.
**Resolution hint:** review for completeness; may be acceptable.

### B5 — UN without DI

**Severity:** error.
**Detection:** for each DTM UN row, check the `design_input` column has an extractable DI ID (not blank, not the configured `tbd_value`).
**Resolution hint:** add DI mapping, OR remove orphan UN.

### B6 — SW without parent DI

**Severity:** warning.
**Detection:** for each Jira Story, check `parent` field is non-empty and `parent.issuetype` is Epic.
**Resolution hint:** set Epic parent in Jira.

### B7 — Hazard without DI

**Severity:** error.
**Detection:** for each Jira Hazard or HTM row, check at least one DI is linked (either via `issuelinks` to a DI Epic, via DTM column `hazard_refs`, or via HTM hazard→DI column).
**Resolution hint:** add Hazard→DI in HTM (or wherever the project records the link).

### B8 — Hazard without mitigation or V&V

**Severity:** error.
**Detection:** per ISO 14971 — for each Hazard, check it has at least one SW (control measure) and at least one V&V evidence (test execution or doc reference).
**Resolution hint:** add control measure and verification.

## Category C — Metadata drift (item attributes)

Items exist in both universes; their attributes diverge.

### C1 — Status mismatch

**Severity:** warning.
**Detection:** per matched item, compare Jira `status.name` against the DTM/HTM status column (when present). Emit on mismatch.
**Resolution hint:** sync DTM/HTM status from Jira (Jira is the live source).

### C2 — Summary drift

**Severity:** info.
**Detection:** string-similarity (e.g., Jaccard or normalized edit distance) between the DTM DI description and the Jira Epic summary. Threshold from `cfg` (default `0.8`).
**Resolution hint:** investigate intentional rewording vs stale DTM.

### C3 — Version/scope mismatch

**Severity:** warning.
**Detection:** Jira Epic in `fixVersion = vN.0.0` but appears in `vM.0.0` DTM (or vice-versa).
**Resolution hint:** one of the two has wrong scope tagging.

### C4 — ID format drift

**Severity:** error.
**Detection:** when both Jira summary and DTM DI column have an extractable ID and they differ.
**Resolution hint:** fix the typo. Note: rule does NOT fire when one side is missing an ID — that's A1 or A2 territory, not C4.

### C5 — Stale WORKING xlsx

**Severity:** info.
**Detection:** filename heuristic on the configured DTM xlsx path — `WORKING_*.xlsx` siblings exist alongside the actual file.
**Resolution hint:** confirm the actual file is the primary; consider archiving WORKING copies.

## Severity overrides

Projects can downgrade noisy rules or upgrade lax ones via `project.yml`:

```yaml
jira_pull:
  severity_overrides:
    A3: info        # downgrade Jira-only SW to info during early development
    B3: warning     # cap V&V missing at warning while DTM verification columns are being filled in
```

The runner consults the override map after each rule emits at its natural severity.

## Exempt filters

Some Jira items are intentionally not in the DTM (e.g., tracking Epics for documentation deliverables, infrastructure Epics). Exempt them via:

```yaml
jira_pull:
  exempt_filters:
    - { kind: label, value: tracking-epic }
    - { kind: summary_regex, value: '^.*QMS Documentation.*$' }
    - { kind: issuetype_summary, issuetype: Epic, summary_regex: 'Infrastructure' }
```

Filters apply BEFORE rule evaluation, so exempt items never produce A1/A3/A5 violations.
