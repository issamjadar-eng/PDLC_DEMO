---
name: list-user-rows
summary: List all user-injected tracker rows in the registry
---

# `/tracker list-user-rows` — read-only summary

Show every entry in `tracker-user-rows.yml` as a compact table.

## When to invoke

User says: `/tracker list-user-rows`, `show me the user rows`, `which rows
are user-injected?`, `which rows are not catalog-derived?`.

## Flow

1. Read `docs/project/submissions/tracker-user-rows.yml`.
2. Render as a markdown table:

   | ID | Name | Scope | Phase | Status | Reason (truncated) | Created |
   |----|------|-------|-------|--------|--------------------|---------|

   Truncate `reason` to 60 chars + `…` if longer. Show `_meta.created_at` in
   short form (`YYYY-MM-DD`).

3. Footer: total count, breakdown by `kind` (deliverable / header /
   gap-tracker), breakdown by phase.

4. Optional: surface any rows whose `path` doesn't resolve on disk (link
   to `/tracker validate-rows` for the full audit).

This action is **read-only** — never modifies the registry or canonical.
