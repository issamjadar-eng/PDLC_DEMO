---
name: import-user-rows
summary: Bulk-import existing hand-authored rows from submission-tracker.md into the registry
---

# `/tracker import-user-rows` — one-shot migration

Extract rows present in the canonical `submission-tracker.md` but absent
from the generator's row inventory, draft registry entries for them, and
present a batch-review surface for the user. Used once per project to
bootstrap the registry from a hand-curated tracker.

## When to invoke

User says: `/tracker import-user-rows`, `bootstrap the user-row registry`,
`migrate the hand-authored rows into the registry`.

This action is **idempotent**: rows already in the registry are skipped;
only new (absent-from-registry) rows are proposed.

## Flow

### Step 1 — Diff canonical against generator output

```bash
python3 -c "
import importlib.util, re
from pathlib import Path
g = importlib.util.spec_from_file_location('g', '.claude/skills/tracker/scripts/generate.py')
m = importlib.util.module_from_spec(g); g.loader.exec_module(m)
project_dir = m.find_project_dir()
gen_rows, _, _ = m.generate_rows(project_dir)
gen_ids = {r['id'] for r in gen_rows}
md = (project_dir / 'docs/project/submissions/submission-tracker.md').read_text()
body, _, _ = md.partition('## Deliverable Details')
md_ids = set(re.findall(r'^\\| ([A-Z][A-Z0-9-]+) \\|', body, re.MULTILINE))
print('|'.join(sorted(md_ids - gen_ids)))
"
```

### Step 2 — Parse each missing row from the markdown table

For each row id absent from the generator, parse its row in the canonical
markdown to extract: name, scope, phase, ref, effort, status, path.
Generate a draft registry entry with `reason: "TODO — bootstrap import,
fill in why this row is user-injected vs catalog-derived"`.

### Step 3 — Write a draft registry + per-row review markdown

- `docs/project/submissions/tracker-user-rows.yml` (draft)
- `docs/project/submissions/tracker-user-rows.review.md` (review surface
  with each entry + open-question prompts: "Why is this row user-injected?
  Confirm scope/phase/path values.")

### Step 4 — User reviews

User opens the `.review.md`, fills in `reason` for each entry, edits any
proposed values that are wrong. Then runs:

```
/tracker import-user-rows --confirm
```

### Step 5 — On `--confirm`: validate + finalize

- Strip the review markdown (delete it)
- Run `/tracker validate-rows` against the now-final registry
- If clean: report success and suggest `/tracker generate --write-canonical`
  as the next step
- If errors: surface them; user fixes; re-run `--confirm`

### Step 6 — Smoke test

After a successful import + regenerate, byte-diff the new canonical
against the pre-import canonical (use git):

```bash
git diff docs/project/submissions/submission-tracker.md
```

Expect: zero functional change (same 117 rows, same order, same content).
Any non-trivial diff means the schema/generator missed something — surface
to the user before committing.

## Failure modes

| Situation | Action |
|---|---|
| Generator can't be imported | Report; user must fix `generate.py` first |
| Canonical markdown not parseable | Report; user must fix the markdown formatting first |
| `--confirm` finds validation errors | Don't write canonical; surface errors; loop |
| Byte-diff after import is large | Surface the diff; ask user to inspect before committing |
