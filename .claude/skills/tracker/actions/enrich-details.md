---
name: enrich-details
summary: Generate per-row deterministic Deliverable Details via parallel details-author agent fan-out
---

# `/tracker enrich-details` — orchestration playbook

This action populates `docs/project/submissions/submission-tracker.details.json`
— the per-row info sidecar consumed by `render.py` when the user clicks
the `(i)` icon on a tracker row. The (?) panel is owned by the
`help-author` agent; this action owns the deterministic Phase / Scope /
Path / Primary REF / All applicable REFs / Notes block.

The action mirrors the `enrich-help` architecture: a deterministic
Python script (`scripts/build-detail-context.py`) emits per-row context
bundles; you (the parent) dispatch one `details-author` agent per row
in parallel.

## Boundary vs `enrich-help`

| Layer | `enrich-help` | `enrich-details` |
|---|---|---|
| Click target | `(?)` icon | `(i)` icon |
| Output sidecar | `submission-tracker.help.json` | `submission-tracker.details.json` |
| Content | LLM artifact explainer (what is this, why does it matter HERE) | Deterministic projection (Phase, Scope, Path, REFs) |
| Context load | Heavy — CLAUDE.md, regulatory strategy, DHF READMEs | Light — bundle + manifest + evidence frontmatter only |
| Multi-row attachment | Per-row only | Supported — one entry can attach to multiple row IDs |
| Cost (per row) | High | Low |

The two actions are independent; either can be run alone.

## When to invoke

- User says: `/tracker enrich-details`, `populate details`, `regenerate
  details`, `refresh detail content`.
- After a structural change (new row added to the tracker, composition
  manifest updated, evidence path moved): user asks for refresh.
- Migration step: when a project moves from hand-authored detail
  blocks (in `submission-tracker.md`) to the sidecar — run this once
  to populate the sidecar for every row.

Do NOT invoke automatically as part of `/tracker render` or `/tracker
generate`. Detail enrichment is opt-in (it costs LLM tokens × N rows,
though much less than help generation).

## Flow

### Step 1 — Verify prerequisites

1. Confirm the active task is associated with this session (the
   PreToolUse gate may deny writes otherwise — see `/task` skill).
2. Confirm `docs/project/submissions/submission-tracker.md` exists and
   `/tracker generate` produces a non-empty row inventory. If not,
   abort and ask the user to seed the project first.
3. Confirm `docs/project/dhf-manifest/<project>-dhf-manifest.json`
   exists (catalog provides REF citations). If missing, the agent
   will still emit details with `all_applicable_refs: [primary_ref]`
   only — warn the user and continue.

### Step 2 — Build the row inventory + bundle list

```bash
# Single-row mode
uv --project tools/project-console run python3 \
  .claude/skills/tracker/scripts/build-detail-context.py --row <ID>

# Full fan-out — write per-row YAML bundles to a tmp dir
uv --project tools/project-console run python3 \
  .claude/skills/tracker/scripts/build-detail-context.py --all \
  --out /tmp/tracker-detail-bundles/
```

The bundle YAML files are the agent input — one file per row, named
`<ROW_ID>.yaml`, each carrying:
- row metadata (id, display_name, canonical_role, scope, phase, status,
  path, primary_ref)
- `evidence_path` + `evidence_hash` (or null when no file resolved)
- `linked_row_ids` (other rows that share the same artifact — same
  path or composition-manifest entry; collapses Q-Sub vs final-package
  duplicates into one detail entry)
- `composition_manifest` (entry_text + linked_docs from the manifest
  table)
- `bound_obligations[]` (slim catalog entries — id, title, reg_source,
  criticality)
- `output_path` — where the agent writes its result

### Step 3 — Cache check (skip rows whose context hasn't changed)

For each bundle, look up the existing `submission-tracker.details.json`
entry for the row. If `entry.context_signature` matches the bundle's
current signature `(canonical_role, obligation_ids, evidence_source_hash,
composition_manifest_signature)`, **skip** that row — its detail entry
is fresh.

When a bundle has `linked_row_ids` (multi-row attachment), the cache
check uses the primary row's signature; if any of the linked rows'
metadata changes, regenerate the whole group.

Report N skipped vs N to-regenerate before fanning out.

### Step 4 — De-duplicate the dispatch list

Because `linked_row_ids` collapses multi-row groups into one entry, you
should dispatch the agent **once per group**, not once per row. After
loading bundles:

1. Group bundles by `(linked_row_ids sorted, primary path)` key.
2. For each group, pick a representative bundle (the one whose row id
   is lexically smallest, by convention) and dispatch the agent against
   it. The agent's emitted entry then attaches to every member of the
   group.

Rows without any `linked_row_ids` peers are their own group of one.

### Step 5 — Fan out the details-author agent in parallel

For each group representative that needs (re)generation:

```
Agent({
  description: "Details: <ROW_ID>",
  subagent_type: "general-purpose",
  prompt: """
    Read .claude/skills/tracker/agents/details-author.md and execute it.

    Your context bundle is at /tmp/tracker-detail-bundles/<ROW_ID>.yaml.
    Read it. Then follow the agent's pre-flight (manifest + evidence
    frontmatter only) and writing rules. Append your entry into
    docs/project/submissions/submission-tracker.details.json under
    entries[].

    Session UUID: <UUID>  (for the task gate)
    Active task: <task_id>  (so the PreToolUse hook lets you write)
  """
})
```

**Batch sizing**: send 10–20 agents per parallel-tool-call message.
Detail authoring is ~3× cheaper than help authoring (less context to
load), so larger batches are fine. Wait for each batch to return
before launching the next so the cache layer (Step 6) can serialize
writes.

### Step 6 — Serialize writes to the details.json sidecar

`submission-tracker.details.json` is a single shared file. Parallel
agents writing concurrently will race. **You** (the orchestrator) own
the merge:

1. Each agent should return its entry via its final response (a JSON
   snippet for the new `entries[]` element) rather than writing to
   the shared file directly. The agent file documents both modes;
   prefer "return-only" mode for orchestration safety.
2. After each batch returns, merge the new entries into the in-memory
   sidecar and write the file once per batch (not once per agent).

Merge rule: when a returned entry's `row_ids` set matches an existing
entry's `row_ids` set, replace; otherwise append.

### Step 7 — Re-render the dashboard

After the sidecar is up to date:

```bash
uv --project tools/project-console run python3 \
  .claude/skills/tracker/scripts/render.py
```

`render.py` reads `submission-tracker.details.json` via
`load_details_sidecar()`. When the sidecar is non-empty, **it overrides
the markdown-inline `## Deliverable Details` section** — the sidecar
is the new source of truth. When the sidecar is missing or empty,
`render.py` falls back to parsing the markdown inline (legacy path).

### Step 8 — Report

Tell the user:
- N entries generated (newly populated, accounting for multi-row groups)
- N entries skipped (cache hit)
- N rows covered (entries × row_ids[])
- N rows still uncovered (no entry produced)
- File modified: `docs/project/submissions/submission-tracker.details.json`
- Re-rendered HTML: `docs/project/submissions/submission-tracker.html`

## Single-row smoke flow (recommended for first-time use)

Before doing the full fan-out, prove the agent on one row to validate
prompt + output shape:

1. Pick a row that has rich obligations (e.g., an architecture or
   verification row with multiple bound obligations).
2. `python3 build-detail-context.py --row <ID> --out /tmp/tracker-detail-bundles/`
3. Dispatch ONE `details-author` agent against `/tmp/tracker-detail-bundles/<ID>.yaml`.
4. Inspect the resulting entry: are `all_applicable_refs` correct
   (deduplicated, sorted FDA → IEC → ISO → QMS)? Is `phase_text`
   formatted correctly? Does `linked_row_ids` correctly collapse
   sibling rows that share the artifact?
5. If quality is good → proceed to full fan-out. If not → tune the
   agent prompt at `.claude/skills/tracker/agents/details-author.md`
   and re-run the single-row test.

## Failure modes

| Situation | Mitigation |
|---|---|
| Bundle script errors (missing project.yml, malformed catalog) | Fix upstream; this action assumes `/tracker generate` runs cleanly |
| Agent returns malformed JSON entry | Discard that entry's update; report the failure; let the user re-run for those rows |
| Sidecar file write race (two batches finish at once) | Use the file system lock (`flock` on the sidecar) when writing; or serialize batches |
| Catalog has zero bound obligations for a row's (dhf, role) pair | Agent emits `all_applicable_refs: [primary_ref]`; flag in report |
| Multi-row group spans incompatible scope/phase pairs | Agent emits both values comma-separated in `phase_text` / `scope` fields; orchestrator may want to manually split the group |

## Cost estimate

Per-row cost is roughly 1/3 of the help-author cost (no project-context
load, just the bundle + manifest read + evidence frontmatter skim +
deterministic JSON emit). For ~140 rows: very feasible in a single
session, especially with multi-row attachment collapsing duplicates.
Re-runs are cache-hit-cheap.
