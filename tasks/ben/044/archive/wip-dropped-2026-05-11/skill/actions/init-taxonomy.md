# action: init-taxonomy

Cold-start scaffolding for a `.taxonomy.yml` file. Walks a root, classifies
`.md` files via heuristics, writes a starter taxonomy, registers it in
`project.yml.taxonomies[]`.

## Usage

```bash
# One DHF (auto-resolves path from project.yml dhfs[<leaf>].path)
python3 .claude/skills/tracker/scripts/init_taxonomy.py \
  --project-dir <project-root> --dhf <leaf>

# Arbitrary folder root (predicate-analysis, submission folder, etc.)
python3 .claude/skills/tracker/scripts/init_taxonomy.py \
  --project-dir <project-root> --path docs/project/input-analysis/predicate-analysis

# Bulk: every DHF in project.yml that doesn't already resolve to a taxonomy
python3 .claude/skills/tracker/scripts/init_taxonomy.py \
  --project-dir <project-root> --all-dhfs
```

If `pyyaml` isn't on PATH, prefix with `uv run --project tools/project-console`.

## What it does

1. **Resolves the root** — `<project_root>/dhfs[leaf].path` for `--dhf`,
   `<project_root>/<rel>` for `--path`.
2. **Scans recursively** — walks every `.md` file under the root (excluding
   `README.md`, `Icon`, `__pycache__/**`).
3. **Classifies via heuristics** — filename + path patterns map to canonical
   roles (architecture, requirements, vnv, risk-management, …). High-confidence
   matches go to `mappings:`; ambiguous matches go to `pending:` with their
   candidate roles.
4. **Marks primary file per (folder, role)** — when multiple files in the same
   folder share a canonical role, the alphabetically-first is `primary: true`
   so downstream consumers (tracker rendering, AI Status) have a deterministic
   "the" file for that role.
5. **Writes `<root>/.taxonomy.yml`** — schema v0.3, additive over Arthrex v0.2.
6. **Registers in `project.yml.taxonomies[]`** — adds an entry with
   `applies_to_dhfs:` (DHF mode) or `applies_to_paths:` (path mode).

## Flags

| Flag | Effect |
|---|---|
| `--force` | Overwrite an existing `.taxonomy.yml` at the target path |
| `--no-register` | Skip the `project.yml.taxonomies[]` entry (rare; useful for shared taxonomies registered manually) |

## Output guarantees

- **Idempotent on re-run with `--force`** — produces the same taxonomy for the
  same input tree.
- **Never silently drops files** — every `.md` ends up in `mappings:` or
  `pending:` (or matches `excluded:`).
- **`pending:` entries carry `first_seen` dates** — set to today on first scan;
  preserved by `reconcile-taxonomy` on subsequent runs.

## Caveats

- **Round-tripping `project.yml` strips comments** — pyyaml dump rewrites the
  file. The first `--all-dhfs` run on a heavily-commented project.yml is the
  expensive one; subsequent runs are no-ops if entries are already present.
  Mitigation: hand-author the `taxonomies:` block first, then run with
  `--no-register` so the action only writes the taxonomy file.
- **Heuristics are deliberately conservative** — better to surface a file in
  `pending:` than to mis-classify it. Tune `HEURISTICS` in
  `scripts/taxonomy.py` to add project-specific patterns.

## Pair with

- `reconcile-taxonomy` — keep the file in sync with disk over time.
- `/tracker generate` — automatically picks up the new taxonomy via the
  resolver; falls back to the hardcoded folder layout when no taxonomy exists.
