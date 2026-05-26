---
name: enrich-help
summary: Generate per-row LLM artifact help via parallel help-author agent fan-out
---

# `/tracker enrich-help` — orchestration playbook

This action populates `docs/project/submissions/submission-tracker.help.json`
— the per-row help sidecar consumed by `render.py` when the user clicks the
`(?)` icon on a tracker row. The (i) panel stays deterministic; this action
owns the "what is this artifact, why does it matter in *this* project, what
topics must it address" reviewer-facing content.

The action is **agent-orchestrated**: a deterministic Python script
(`scripts/build-help-context.py`) emits per-row context bundles; you (the
parent) dispatch one `help-author` agent per row in parallel, mirroring the
`/dhf-manifest tier1-enricher` fan-out pattern proven in task ben/158
Phase 2a.

## When to invoke

- User says: `/tracker enrich-help`, `populate help`, `regenerate help`,
  `refresh help content`, `run /tracker help`.
- User asks for help on a single row: `/tracker enrich-help PP1`.
- After a structural change (new milestone binding, catalog re-build,
  significant evidence change): user asks for refresh.

Do NOT invoke automatically as part of `/tracker render` or `/tracker
generate`. Help generation is opt-in (it costs LLM tokens × N rows).

## Flow

### Step 1 — Verify prerequisites

1. Confirm the active task is associated with this session (the
   PreToolUse gate may deny writes otherwise — see `/task` skill).
2. Confirm `docs/project/submissions/submission-tracker.md` exists and
   `/tracker generate` produces a non-empty row inventory. If not, abort
   and ask the user to seed the project first.
3. Confirm `docs/project/dhf-manifest/<project>-dhf-manifest.json` exists
   (catalog binding feeds the obligation context). If missing, the help
   will still generate but with `regulatory_anchors[].role: "inferred"` —
   warn the user and continue.

### Step 2 — Build the row inventory + bundle list

```bash
# Single-row mode
uv --project tools/project-console run python3 \
  .claude/skills/tracker/scripts/build-help-context.py --row <ID>

# Full fan-out — write per-row YAML bundles to a tmp dir
uv --project tools/project-console run python3 \
  .claude/skills/tracker/scripts/build-help-context.py --all \
  --out /tmp/tracker-help-bundles/
```

The bundle YAML files are the agent input — one file per row, named
`<ROW_ID>.yaml`, each carrying:
- row metadata (id, display_name, canonical_role, scope, phase, status)
- `dhf_leaf` (or null for submission rows)
- `evidence_path` + `evidence_hash` (or null when no file resolved)
- `composition_manifest` (entry_text + linked_docs from the manifest table)
- `bound_obligations[]` (slimmed-down catalog entries — id, title,
  reg_source, criticality, extracted_requirements)
- `output_path` — where the agent writes its result

### Step 3 — Cache check (skip rows whose context hasn't changed)

For each bundle, look up the existing `submission-tracker.help.json` entry
for `row.id`. If `entry.context_signature` matches the bundle's current
signature `(canonical_role, obligation_set_hash, evidence_source_hash,
claude_md_hash)`, **skip** that row — its help is fresh.

Compute hashes:
- `obligation_set_hash`: read top-level `obligation_set_hash` from
  the dhf-manifest catalog (already computed there)
- `evidence_source_hash`: from the bundle's `row.evidence_hash`
- `claude_md_hash`: sha256 of the project's `CLAUDE.md`

Report N skipped vs N to-regenerate before fanning out.

### Step 4 — Fan out the help-author agent in parallel

For each row that needs (re)generation:

```
Agent({
  description: "Help: <ROW_ID>",
  subagent_type: "general-purpose",
  prompt: """
    Read .claude/skills/tracker/agents/help-author.md and execute it.

    Your context bundle is at /tmp/tracker-help-bundles/<ROW_ID>.yaml.
    Read it. Then follow the agent's pre-flight (project context loading)
    and writing rules. Append your row's entry into
    docs/project/submissions/submission-tracker.help.json under rows.<ROW_ID>.

    Session UUID: <UUID>  (for the task gate)
    Active task: <task_id>  (so the PreToolUse hook lets you write)
  """
})
```

**Batch sizing**: send 5–10 agents per parallel-tool-call message. With
~140 rows in a typical project this is 14–28 batches. Wait for each
batch to return before launching the next — keeps memory predictable
and lets the cache layer (Step 5) serialize writes.

### Step 5 — Serialize writes to the help.json sidecar

`submission-tracker.help.json` is a single shared file. Parallel agents
writing concurrently will race. **You** (the orchestrator) own the merge:

1. Each agent should return its row's entry via its final response
   (a JSON snippet for `rows.<ROW_ID>`) rather than writing to the
   shared file directly. The agent file documents both modes; prefer
   "return-only" mode for orchestration safety.
2. After each batch returns, merge the new entries into the in-memory
   sidecar and write the file once per batch (not once per agent).

Alternative (slower but simpler): run agents serially, one row at a time,
and let each agent write directly. Use this for small batches (< 10 rows
total) or for development iteration on the agent prompt.

### Step 6 — Re-render the dashboard

After the sidecar is up to date:

```bash
uv --project tools/project-console run python3 \
  .claude/skills/tracker/scripts/render.py
```

`render.py` reads `submission-tracker.help.json` via `load_help_sidecar()`
and emits filled help-rows for every row that has an entry; rows without
entries show the "Generate help" placeholder.

### Step 7 — Report

Tell the user:
- N rows generated (newly populated)
- N rows skipped (cache hit)
- N rows failed (with row IDs + reason)
- File modified: `docs/project/submissions/submission-tracker.help.json`
- Re-rendered HTML: `docs/project/submissions/submission-tracker.html`

## Single-row smoke flow (recommended for first-time use)

Before doing the full fan-out, prove the agent on one row to validate
prompt + output shape:

1. Pick a row with rich obligations — typically an item-DHF
   architecture or risk-management row carries the most catalog binding.
   Example row IDs are project-specific; pick whatever your inventory has.
2. `python3 build-help-context.py --row PP1 --out /tmp/tracker-help-bundles/`
3. Dispatch ONE `help-author` agent against `/tmp/tracker-help-bundles/PP1.yaml`.
4. Inspect the resulting `submission-tracker.help.json` entry: does the
   description anchor to the project? Are main_topics derived from
   `extracted_requirements`? Are regulatory_anchors cited correctly?
5. If quality is good → proceed to full fan-out. If not → tune the agent
   prompt at `.claude/skills/tracker/agents/help-author.md` and re-run
   the single-row test.

## Failure modes

| Situation | Mitigation |
|---|---|
| Bundle script errors (missing project.yml, malformed catalog) | Fix upstream; this action assumes `/tracker generate` runs cleanly |
| Agent returns malformed JSON entry | Discard that row's update; report the failure; let the user re-run for those rows |
| Sidecar file write race (two batches finish at once) | Use the file system lock (`flock` on the sidecar) when writing; or serialize batches |
| Catalog has zero bound obligations for a row's (dhf, role) pair | Agent writes inferred-anchor entry; flag in report |
| Agent exhausts context reading evidence files | Bundle's `evidence_path` is a hint; agent may read frontmatter + headings only (per its own rubric) |

## Cost estimate

Per-row cost ≈ 1 agent run × (project context load + bundle parse +
evidence-file skim + structured-JSON emit). For ~140 rows: comparable to
the 13-file fan-out under task ben/158 Phase 2a (which completed cleanly
in parallel). Re-runs are cache-hit-cheap when project state is stable.
