# Action: `list`

Roll-up table of all gap analyses across components, with status / topic filtering. Walks `docs/_analysis/<component>/*/` (subdirectories) and reads each subdirectory's aggregate file `<id>/<id>.md`. Per the folder-per-analysis convention in [`../SKILL.md`](../SKILL.md). Subdirectories without a matching-named aggregate are not gap-analysis folders (skip).

## Usage

```
/gap-analysis list [--status <s>] [--component <slug>] [--topic <t>]
```

## Arguments

- **`--status <s>`** (optional, repeatable) — filter by `draft | review | accepted | superseded`. Multiple flags act as OR.
- **`--component <slug>`** (optional, repeatable) — filter by component slug.
- **`--topic <t>`** (optional, repeatable) — filter by canonical topic key (aliases resolved at parse time).

## Steps

1. **Discover analyses.** For each component subfolder under `docs/_analysis/<component>/`, walk its analysis subdirectories and read each one's aggregate `<id>/<id>.md` (the file whose stem matches its folder name; skip `README.md`, `recs-*.md`, and `research-*.md`).
2. **Parse frontmatter.** Read the YAML between the `---` fences. Skip files that lack an `id:` field — they're not gap analyses per this skill (likely stray docs that shouldn't be in `_analysis/`; surface them as warnings).
3. **Apply filters.** Drop entries that don't match any of the provided `--status` / `--component` / `--topic` filters. No filters = include all.
4. **Sort** by `(component, status_rank, last_updated desc)`. Status rank order: `draft → review → accepted → superseded` (newest editorial state surfaced first within a component).
5. **Render table** to stdout:
   ```
   COMPONENT      ID                                 TOPIC          STATUS    LAST_UPDATED  AGENTS
   ─────────────  ─────────────────────────────────  ─────────────  ────────  ────────────  ──────────────────────────────
   <arch-A>       risk-hazard-misscoring-catalog     risk           draft     <date>        risk-management, regulatory-affairs
   <system-leaf>  filing-modification-protocol-scope filing         review    <date>        regulatory-affairs, program-manager
   ...
   ```
6. **Summary footer** — counts per status overall, plus warnings:
   ```
   Summary: N analyses (X draft / Y review / Z accepted / W superseded)
   Warnings: 1 file in _analysis/<component>/ has no `id:` frontmatter — see _analysis/<component>/<file>.md
   ```

## Notes

- This action is read-only; never modifies files.
- The `--component` filter accepts both arch_slugs (item DHFs) and the system DHF leaf.
- `--topic` filtering resolves aliases via `data/topic-advisor-map.yml aliases:` before comparison.
- For a single-component overview, `/gap-analysis list --component <arch>` shows just that DHF's gap-analysis backlog and status mix — useful for the recommended_agents to start a session with current context.

## Output format options

Future extension: `--format json` for machine-readable output (e.g., feeding the project console's Findings page). v1 ships text-table only.
