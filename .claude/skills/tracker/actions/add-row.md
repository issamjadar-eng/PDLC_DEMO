---
name: add-row
summary: Add a user-injected row to the tracker registry via the user-row-author agent
---

# `/tracker add-row` — orchestration playbook

Add a row to `docs/project/submissions/tracker-user-rows.yml` from a freeform
user request. The skill is the schema enforcer; Claude (via the
`user-row-author` agent) is the authoring assistant. Hand-editing the
registry yaml is discouraged — go through this action so the skill validates
and the canonical markdown stays in sync.

## When to invoke

User says: `/tracker add-row "<freeform description>"`, `add a tracker row
for X`, `the tracker is missing a row for X`, `register a user row for X`.

## Flow

### Step 1 — Verify prerequisites

- Confirm the active task is associated with this session (the `/task`
  PreToolUse gate may deny writes otherwise).
- Confirm `project.yml`, `docs/project/milestones/regulatory.yml`, and
  `docs/project/submissions/submission-tracker.md` all exist (Model D
  requires all three to resolve project vocabularies).
- The registry file at `docs/project/submissions/tracker-user-rows.yml` may
  or may not exist — both states are valid. If missing, this action
  creates it with the correct shape on first write.

### Step 2 — Dispatch the user-row-author agent

```
Agent({
  description: "Add user row: <one-line summary>",
  subagent_type: "general-purpose",
  prompt: """
    Read .claude/skills/tracker/agents/user-row-author.md and execute it.

    Operation: add
    Freeform request: <user's full description verbatim>
    Project dir: <absolute project path>
    Session UUID: <uuid>

    Return the draft entry as a YAML block, plus per-field justification.
  """
})
```

### Step 3 — Present draft + justification to the user

Show the user the draft entry and the agent's per-field justification.
Possible responses:

- **Approve as-is** → proceed to Step 4
- **Approve with edits** → user dictates the changes; you apply them; proceed
- **Reject** → discard; offer to re-author with new context

Do not skip user review. The whole point of skill-mediated authoring is that
the user owns the final entry.

### Step 4 — Validate against the schema

```bash
# Dry-run: write the proposed entry to a temp registry, validate, then
# decide. The actual write is Step 5.
python3 .claude/skills/tracker/scripts/validate-user-rows.py
```

If validation fails, surface the errors to the user and loop back to Step 3
with the agent's draft + the validator output, asking for corrections. Do
not write a non-conformant row.

If validation produces only warnings (e.g., path doesn't exist on disk
because the artifact is Not Started), proceed to Step 5 — warnings are
informational.

### Step 5 — Write the entry to the registry

Add the entry to `docs/project/submissions/tracker-user-rows.yml`:

- If the file doesn't exist, create it with shape:
  ```yaml
  schema_version: "0.1"
  rows:
    - <new entry>
  ```
- If it does exist, append to `rows:` (preserve existing entries).
- Auto-fill the `_meta` block on the new entry:
  ```yaml
    _meta:
      created_by: <git config user.email or project.yml team roster>
      created_at: <current ISO 8601 timestamp UTC>
      last_updated_at: <same as created_at>
      schema_version: "0.1"
  ```

### Step 6 — Auto-regenerate the canonical markdown

```bash
python3 .claude/skills/tracker/scripts/generate.py --write-canonical
```

This reads the catalog + the (now-updated) registry and rewrites
`submission-tracker.md` so the new row appears in the dashboard. Without
this step the registry is dead data.

### Step 7 — Report

Tell the user:

- Row id added: `<id>`
- Registry now has N entries
- Canonical regenerated: `submission-tracker.md` (M total rows)
- Sidecar `submission-tracker.row-source.json` updated with
  `<id>: source_kind=user`
- Suggest next steps: `/tracker enrich-help <id>` and `/tracker
  enrich-details <id>` to populate the new row's `(?)` and `(i)` panels.

## Failure modes

| Situation | Action |
|---|---|
| Agent returns malformed YAML | Discard; re-dispatch with the validator's parse error; if it fails twice, offer to author manually |
| User rejects the draft three times | Stop; offer to refine the request together before re-dispatching |
| `--write-canonical` fails | Roll back the registry write (git checkout the file); surface the error |
| Schema collision (id already used by generator) | Validator catches this; loop back to Step 3 to pick a different id |

## Notes

- This action is **synchronous** — the user is in the loop on every entry.
  No fan-out / batch logic. For migrating many rows at once (one-time
  bootstrap of the registry), see `/tracker import-user-rows`.
- The `user-row-author` agent is dispatched once per add-row invocation.
  Cost is minimal (single agent run, no large context load beyond the
  schema + project context).
