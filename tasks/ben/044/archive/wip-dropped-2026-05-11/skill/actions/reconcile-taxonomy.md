# action: reconcile-taxonomy

Diff disk vs an existing `.taxonomy.yml`. Refreshes `pending:` (newly-discovered
files) and `broken_refs:` (mapped files no longer on disk). Mappings are NEVER
mutated by reconcile — the user authors classification.

## Usage

```bash
# By taxonomy id (from project.yml.taxonomies[])
python3 .claude/skills/tracker/scripts/reconcile_taxonomy.py \
  --project-dir <project-root> --id <taxonomy-id>

# By DHF leaf — finds whichever taxonomy serves this DHF
python3 .claude/skills/tracker/scripts/reconcile_taxonomy.py \
  --project-dir <project-root> --dhf <leaf>

# By taxonomy file path
python3 .claude/skills/tracker/scripts/reconcile_taxonomy.py \
  --project-dir <project-root> --file docs/project/dhfs/pca-device/.taxonomy.yml

# Reconcile every registered taxonomy
python3 .claude/skills/tracker/scripts/reconcile_taxonomy.py \
  --project-dir <project-root> --all

# Report only — print diff without writing
python3 .claude/skills/tracker/scripts/reconcile_taxonomy.py \
  --project-dir <project-root> --all --report-only
```

## What it does

For each target taxonomy:

1. **Resolves all roots the taxonomy serves** — looks up `applies_to_dhfs:`
   (DHF leafs from `project.yml.dhfs[]`) and `applies_to_paths:`. A shared
   taxonomy serving N DHFs reconciles all N roots in one pass and updates the
   single shared file.
2. **Re-scans each root** — walks every `.md` under the discovery root.
3. **Classifies the diff:**
   - **New file on disk, not in `mappings:` or `pending:`** → adds to `pending:`
     with today's `first_seen` and heuristic candidate roles.
   - **In `pending:` and still on disk** → preserves the original `first_seen`
     date; refreshes `candidate_roles` if the heuristic now has new guesses.
   - **In `pending:` but no longer on disk** → removed silently.
   - **In `mappings:` but no longer on disk** → adds to `broken_refs:` with
     `last_seen`. Does NOT remove the mapping — the user decides whether the
     file moved (update path) or was deleted (remove the mapping).
   - **In `mappings:` and present** → unchanged.
4. **Writes the updated taxonomy** — preserves all existing fields. Drops
   `pending:` and `broken_refs:` blocks entirely when empty.
5. **Prints a report** — per-taxonomy line with mapped/on-disk counts, new
   pending, broken refs, still pending. Plus a final tally across all targets.

## Output

```
[pca-device]  mapped=65 on_disk=67 +pending=2 still_pending=0 broken=0
    new pending:
      + design-controls/labeling/ifu-draft.md
      + design-controls/usability/use-error-list.md

Reconciled 1 taxonomy file(s). 2 new pending entries, 0 broken refs.
```

## Flags

| Flag | Effect |
|---|---|
| `--report-only` | Print the report; do NOT write changes to the taxonomy file. CI-friendly. |

## What reconcile does NOT do

- Does not classify `pending:` entries — promoting `pending` → `mappings`
  requires user judgment (or a future `classify` action).
- Does not remove broken-ref mappings — the user decides on each.
- Does not modify `mappings:`, `excluded:`, `vocabulary_source:`, or any other
  user-authored field.

## Pair with

- `init-taxonomy` — cold-start the taxonomy file before reconcile can run.
- `/tracker generate` — re-run after reconcile if newly-classified files
  should be reflected in the row inventory.
