---
name: validate-rows
summary: Validate tracker-user-rows.yml against the schema (CI-friendly exit code)
---

# `/tracker validate-rows` — schema validation

Run `validate-user-rows.py` and surface the result. Suitable for CI hooks
(exit non-zero on errors).

## When to invoke

User says: `/tracker validate-rows`, `validate the user rows`, `is the
registry conformant?`, before any commit / push that touches the registry.

## Flow

```bash
python3 .claude/skills/tracker/scripts/validate-user-rows.py [--strict]
```

`--strict` (opt-in): warnings count as errors (use in CI to block on stale
paths, unknown vocabularies, etc.).

Surface to the user:

- Errors (always non-zero exit)
- Warnings (informational unless `--strict`)
- Resolution suggestions where obvious (e.g., "scope `Postmarket` not in
  vocabulary; project's resolved scope set is `[...]`. Did you mean `X`?")

## Exit codes

- `0` — all entries conformant (warnings allowed unless `--strict`)
- `1` — at least one error (or warning under `--strict`)

This action is **read-only** — never writes.
