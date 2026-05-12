# Action: `discovery-index`

Resolves canonical document roles to project file paths via a three-level
registry pattern. Emits a thin discovery index that advisor agents (and any
other consumer skill) can use as a cheap discovery layer before targeted
reads.

**Script**: `scripts/discovery-index.py`

```bash
python3 .claude/skills/dhf-manifest/scripts/discovery-index.py [PROJECT_ROOT]
```

**Inputs**:

| Layer | Source | Authority |
|---|---|---|
| L1 — canonical role names + scope semantics | `data/canonical-roles.yaml` (skill) | Skill maintainers |
| L2 — ranked alternative pattern conventions per role | `data/canonical-roles.yaml` (skill) | Skill maintainers, append-mostly |
| L3a — durable per-project overrides | `<project>/project.yml` → `evidence_layout.layers[role].{patterns_extra, patterns_exclude, folder_override}` | Project authors (optional) |
| L3b — generated per-project resolution | `<project>/docs/project/dhf-manifest/<slug>-dhf-discovery.json` | This action |

**Outputs**:

```
docs/project/dhf-manifest/<project-slug>-dhf-discovery.json
```

**Output schema** (top-level keys):

| Key | Shape | Purpose |
|---|---|---|
| `schema_version` | `"1.0"` | Index format version |
| `generated` | ISO-8601 timestamp | When the resolver ran |
| `project` | project-name slug | From `project.yml project.name` |
| `project_roles` | `{role: entry}` | Single-file resolutions for project-scoped roles |
| `dhf_roles` | `{dhf_id: {role: entry \| null, role: dhf.role, dhf_organization: mode}}` | Per-DHF resolutions; `role` echoes `project.yml dhfs[].role`, `dhf_organization` echoes the mode this resolution used |
| `submission_roles` | `{submission_id: {role: entry \| null}}` | Per-submission resolutions |
| `external_roles` | `{role: {folder, exists, file_count, patterns_used}}` | External-data role catalogs (no winner concept; just counts) |
| `gaps` | list of `{scope, dhf?, submission?, role, reason, patterns_tried, informational?}` | Unresolved roles. `informational: true` marks legitimate "role not applicable here" — e.g., RMP for an externally-organized item DHF using a Confluence template that bundles risk evidence into the SRA |
| `ambiguity_notes` | list of `{scope, dhf?, role, winning_pattern, winning_path, alternatives: [{pattern, path}]}` | Disambiguation choices the resolver made when multiple patterns produced matches; reviewable by humans |

**Entry shapes** depend on the role's declaration:

- **Single-file entry** (default): `{path, exists, size_bytes, tokens_estimate (bytes//4), matched_pattern}`. Consumers `Read` the path.
- **Folder-pointer entry** (`multi_file: true` in registry, or `external_data` scope): `{folder, exists, file_count, patterns_used}`. No "winner" concept — consumers `Glob` inside the folder when they need per-file specifics. An empty-but-existing folder is a valid 0-count entry, not a gap. Used for artifact families like customer complaints, KOL interview reports, literature search citations, V&V protocols/reports.

## Three-level resolution algorithm

```
For each role in canonical-roles.yaml:

  scope == "project"
    Patterns probed at <project_root>.
    First pattern with exactly-one match wins.

  scope == "per-dhf"
    For each DHF entry in project.yml dhfs[]:

      DHF dhf_organization == "internal":
        Use role.internal.{folder, patterns}.
        Search root: <project_root>/<dhf.path>/<folder>.
        First pattern with exactly-one match wins.

      DHF dhf_organization == "external":
        Use role.external.{taxonomy_folder, patterns}.
        Load <dhf.taxonomy_path> for discovery_root.
        Try nested layout first:
          <dhf.path>/<discovery_root>/<taxonomy_folder>/<patterns>
        Fall back to flat layout:
          <dhf.path>/<discovery_root>/<taxonomy_folder>.md
        Roles without an external block emit an informational gap
        (role not applicable in this DHF's organizational mode).

  scope == "per-submission"
    For each submission_id (from project.yml or inferred from
    docs/project/submissions/<id>/ directories):
      Search root: <project_root>/<folder> with {submission_id} substituted.

  scope == "external_data"
    Enumerate file_count under role.folder; never picks a single winner.
    triage_only — never eagerly loaded.

multi_file: true flag (available on project and per-dhf scopes):
  Override the single-file "winner" semantics:
    - Enumerate ALL matches across ALL patterns.
    - Emit folder-pointer entry {folder, exists, file_count, patterns_used}.
    - Per-dhf multi_file is supported in internal mode; external mode is deferred
      (no taxonomy convention for multi-file artifact families yet).
    - Empty-but-existing folder → exists: True, file_count: 0; not a gap.
```

## Ambiguity handling

When multiple patterns match files for the same `(scope, dhf, role)`, the
resolver picks the **highest-ranked pattern with exactly-one match** as the
winner. All other matches are recorded in `ambiguity_notes[]` for human
review. The pattern ranking in `canonical-roles.yaml` is therefore
load-bearing — most-specific first.

`/best-practices` audit (Recommended tier) flags non-empty `ambiguity_notes[]`
so the reviewer can confirm the resolver picked correctly.

## Cadence

| When | Action | Why |
|---|---|---|
| `/dhf-manifest init` | Regenerate always | Initial bootstrap and manual refresh |
| `/best-practices fix` | Regenerate if any resolved path no longer exists | Drift detection |
| Project commit | Never (no hook) | Avoids churn on changes that don't affect canonical roles |
| Agent runtime | Falls back to dynamic L2 probe per role if a resolved path missing | Stale-index resilience |

## Self-test

```bash
.claude/skills/dhf-manifest/tests/test_discovery_index.sh
```

Six fixture cases exercise: clean multi-convention resolution, ambiguity, L3
override prepending, external_data role enumeration, external-mode nested
sub-convention (`folder/v*.md` + `folder/index.md`), and external-mode flat
sub-convention (`folder.md`). All cases self-contained in `mktemp` directories
— no dependency on any real project's data.

## Consumers

The discovery index is consumed by advisor agents that reference canonical
roles in their `console.context:` / `console.sources:` blocks. The pilot
consumer is `regulatory-affairs`; rollout to other 12 advisor agents is
tracked in a separate task.

Sibling skills that may also consume the index (future):
- `/tracker assess` — could read role → path bindings to seed
  obligation→evidence binding rather than re-probing the filesystem.
- `/best-practices` — adds a check for non-empty `ambiguity_notes[]` and a
  separate check for non-informational `gaps[]` that should be authoring
  follow-ups.
