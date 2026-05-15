---
name: remove-row
summary: Remove a user-injected tracker row from the registry
---

# `/tracker remove-row` — orchestration playbook

Remove an entry from `tracker-user-rows.yml` and regenerate the canonical
markdown so the row disappears from the dashboard.

## When to invoke

User says: `/tracker remove-row <id>`, `delete tracker row X`, `the X row
shouldn't exist anymore`.

## Flow

1. Locate the entry by `id`. If not found, report and stop.
2. Show the entry to the user (full YAML block including `_meta`); confirm:
   "Remove `<id>` (`<name>`)? This deletes the registry entry and the row
   from `submission-tracker.md`. Help/details sidecars for this row will be
   orphaned (rows[<id>] will remain in the JSON but render.py won't display
   them since the row is gone). Confirm? [y/N]"
3. On confirm, remove the entry from `rows:` in `tracker-user-rows.yml`.
4. Run `validate-user-rows.py` (sanity check).
5. Run `python3 .claude/skills/tracker/scripts/generate.py
   --write-canonical`.
6. Report:
   - Row removed: `<id>`
   - Registry now has N entries (was N+1)
   - Canonical regenerated
   - Sidecar `submission-tracker.row-source.json` no longer lists `<id>`
   - Note: orphaned help/details entries can be cleaned with
     `/tracker prune-sidecars` (future action) or hand-removed.

## Failure modes

| Situation | Action |
|---|---|
| Entry not found | Report; suggest `/tracker list-user-rows` to find the right id |
| User does not confirm | Stop; no write |
| `--write-canonical` fails | Restore the entry (git checkout the file); surface error |
