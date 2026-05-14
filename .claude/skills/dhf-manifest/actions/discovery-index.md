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
| L0 — per-document frontmatter opt-in | `canonical_role: <slug>` in a doc's YAML frontmatter | Document authors (optional, **highest precedence**) |
| L1 — canonical role names + scope semantics | `data/canonical-roles.yaml` (skill) | Skill maintainers |
| L2 — ranked alternative pattern conventions per role | `data/canonical-roles.yaml` (skill) | Skill maintainers, append-mostly |
| L3a — durable per-project overrides | `<project>/project.yml` → `evidence_layout.layers[role].{patterns_extra, patterns_exclude, folder_override}` | Project authors (optional) |
| L3b — generated per-project resolution | `<project>/docs/project/dhf-manifest/<slug>-dhf-discovery.json` | This action |

**L0 frontmatter opt-in (v12+):** a document declaring `canonical_role: <slug>`
in its leading YAML frontmatter wins that role slot outright — ahead of every
L2/L3 filename pattern, which are then **not consulted** for that role in that
folder. It is the author's escape hatch for renamed legacy docs or
non-standard filenames, and needs no `project.yml` override. Scope: immediate
`*.md` children of the role's resolved folder, on internal-mode + project +
per-submission scopes (external-mode flat-file and `multi_file` folder-pointer
roles are unaffected). Conflict: if two files in the same folder declare the
same role, there is no winner — the resolver emits an `ambiguity_notes[]` entry
(`winning_pattern: null`) + a paired `gaps[]` entry and does NOT fall through
to filename patterns, because contradictory author intent needs human
resolution rather than a silent pattern pick.

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
| `ambiguity_notes` | list of `{scope, dhf?, role, winning_pattern, winning_path, alternatives: [{pattern, path}]}` | Disambiguation surface: (a) **resolver picked a winner** — `winning_pattern` + `winning_path` are populated, `alternatives[]` lists runner-up matches; (b) **no winner** — `winning_pattern` and `winning_path` are `null`, `alternatives[]` lists all multi-match candidates and a paired entry is added to `gaps[]` whose `reason` references the ambiguity notes. Consumers that read `winning_pattern` must handle the `null` case (v10+). |

**Entry shapes** depend on the role's declaration:

- **Single-file entry** (default): `{path, exists, size_bytes, tokens_estimate (bytes//4), matched_pattern}`. Consumers `Read` the path.
- **Folder-pointer entry** (`multi_file: true` in registry, or `external_data` scope): `{folder, exists, file_count, patterns_used}`. No "winner" concept — consumers `Glob` inside the folder when they need per-file specifics. An empty-but-existing folder is a valid 0-count entry, not a gap. Used for artifact families like customer complaints, KOL interview reports, literature search citations, V&V protocols/reports.

## Three-level resolution algorithm

```
For each role in canonical-roles.yaml:

  L0 frontmatter opt-in (project, per-dhf internal, per-submission scopes):
    Before filename patterns, scan immediate *.md children of the role's
    resolved folder for `canonical_role: <role>` in their frontmatter.
      exactly one declarer  → that file wins; patterns NOT consulted.
      multiple declarers    → no winner; ambiguity_notes[] + paired gaps[].
      zero declarers        → fall through to the pattern steps below.

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

**Multi-match no-winner case (v10+):** If every pattern that matches produces
two or more hits — for example a folder where `*user-needs*.md` matches
both `user-needs.md` and `user-needs-register.md`, and no more-specific
pattern resolves to exactly-one — the resolver emits an `ambiguity_notes[]`
entry with `winning_pattern: null` + `winning_path: null` + the full
`alternatives[]` list, AND a paired `gaps[]` entry whose `reason` references
the ambiguity notes. The role's resolution slot remains `null` until a more
specific pattern (or a project-side `patterns_extra` override) is added.

Before v10 this case was silently swallowed into a misleading "no file
matched any pattern" gap — the multi-match candidates were dropped without
diagnostic breadcrumbs. v10 surfaces both via `ambiguity_notes[]` and via
the paired gap.

`/best-practices` audit (Recommended tier) flags non-empty `ambiguity_notes[]`
so the reviewer can confirm the resolver picked correctly — or, in the
no-winner case, add a more specific pattern.

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

Ten fixture cases exercise: clean multi-convention resolution, ambiguity
(winner picked), L3 override prepending, external_data role enumeration,
external-mode nested sub-convention (`folder/v*.md` + `folder/index.md`),
external-mode flat sub-convention (`folder.md`), project-scoped multi_file
folder pointer, per-DHF multi_file folder pointer (internal mode),
multi-match no-winner (ambiguity_notes + paired gap surface, added in v10),
and frontmatter `canonical_role:` opt-in outranking filename patterns
(added in v12). All cases self-contained in `mktemp` directories — no
dependency on any real project's data.

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
