---
name: update-row
summary: Update an existing user-injected tracker row via the user-row-author agent
---

# `/tracker update-row` — orchestration playbook

Update fields on an existing entry in `tracker-user-rows.yml`. Same shape as
`/tracker add-row` but operates on an existing entry.

## When to invoke

User says: `/tracker update-row <id> "<change>"`, `change row X to Y`,
`update the predicate row's status to Drafting`.

## Flow

### Step 1 — Verify prerequisites + locate the entry

- Same prerequisites as `add-row` (Step 1 there).
- Read `docs/project/submissions/tracker-user-rows.yml`. Locate the entry
  by `id`. If not found, surface clearly: "id `<X>` not found in registry.
  Use `/tracker list-user-rows` to see all user rows, or `/tracker add-row`
  to create a new one."

### Step 2 — Dispatch the agent (operation: update)

Pass `operation: update`, the freeform change description, and the
`existing_entry`. The agent returns a draft showing **what changes** —
ideally a unified-diff-style presentation (not just the new full entry).

### Step 3 — Present diff to user, get approval

Show the user before/after for changed fields only. Approve / edit /
reject — same loop as `add-row` Step 3.

### Step 4 — Validate

Run `validate-user-rows.py`. Same handling: errors loop back; warnings
proceed.

### Step 5 — Write

Replace the entry in `tracker-user-rows.yml` with the new shape. Update
`_meta.last_updated_at` to the current ISO 8601 timestamp UTC. Preserve
`_meta.created_by` and `_meta.created_at` from the existing entry.

### Step 6 — Auto-regenerate canonical

`python3 .claude/skills/tracker/scripts/generate.py --write-canonical`

### Step 7 — Report

- Row id updated: `<id>`
- Changed fields: `[field1, field2, ...]`
- Canonical regenerated
- If `id`, `name`, `path`, or `ref` changed: warn that the help/details
  sidecars may now be stale — suggest `/tracker enrich-help <id>` and
  `/tracker enrich-details <id>` to re-author.

## Failure modes

| Situation | Action |
|---|---|
| Entry not found | Don't write; suggest `add-row` or check the id |
| User-attempted change to `_meta` | Reject the change; `_meta` is auto-managed |
| `id` change requested | Warn loudly: changes downstream sidecar keys, breaks help/details cache. Confirm before allowing |
| Validation fails | Roll back; loop to Step 3 |
