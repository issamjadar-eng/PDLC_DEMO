# action: assess-phases

LLM-driven per-(file × milestone) assessment + gap detection + help-text
generation. Combines what was previously three separate concerns (phase
mapping, help authoring, gap analysis) into ONE batched agent call per
canonical role — minimizes token cost and round-trips.

**Agent**: existing `regulatory-affairs` subagent.
**Output contract**: `agents/phase-mapper.md`.
**Bundle builder**: `scripts/build_phase_map_context.py`.
**Merger**: `scripts/merge_phase_map_results.py`.

## When to invoke

After taxonomy is built (`/tracker init-taxonomy`) and validated. Re-run
when:
- Milestone catalog changes (new release added to `regulatory.yml`)
- A significant set of new files is added to the taxonomy
- The dhf-manifest catalog is rebuilt
- Regulatory strategy is updated

NOT auto-run by `/tracker init-taxonomy` or `/tracker generate` — costs
LLM tokens × N batches. Opt-in.

## Cost model

Per-batch budget:
- ~8-10K shared context (milestone catalog, regulatory strategy excerpt,
  posture vocabulary, output schema)
- ~500-1K per file (frontmatter, role, applicable obligations)
- ~700 tokens per file output (phase_map across milestones + help block)
- Comfortable: 5-10 files per batch

For PDLC_DEMO `pca-device` (~45 mappings across ~14 canonical roles):
roughly 14 batches, ~30-40K tokens per batch, ~500K tokens total. One
focused regulatory-affairs subagent dispatch per batch in parallel.

## Flow

### Step 1 — Build context bundles (deterministic, no LLM)

```bash
# Preview: see how the work will be batched
python3 .claude/skills/tracker/scripts/build_phase_map_context.py \
  --project-dir <project-root> --all --dry-run

# Build the bundles
python3 .claude/skills/tracker/scripts/build_phase_map_context.py \
  --project-dir <project-root> --all --out /tmp/phase-map-bundles/

# Or limit to one role for smoke testing
python3 .claude/skills/tracker/scripts/build_phase_map_context.py \
  --project-dir <project-root> --role risk-management \
  --out /tmp/phase-map-smoke/
```

Each bundle includes: posture vocabulary, milestone catalog, regulatory-
strategy excerpt, and per-file context (frontmatter excerpt + applicable
catalog obligations). Manifest.json lists each (bundle_id, bundle_path,
output_path).

### Step 2 — Dispatch regulatory-affairs subagents in PARALLEL

For each bundle in `manifest.json`, dispatch ONE `regulatory-affairs`
subagent with the bundle as input. **Use the single-message multi-tool-
call pattern** so they run concurrently (one round trip total, N parallel
agent runs).

The dispatch prompt to the regulatory-affairs subagent:

```
You are the phase-mapper for /tracker assess-phases. Read your bundle at:
  <bundle_path>

Your output contract is documented at:
  .claude/skills/tracker/agents/phase-mapper.md

Read the bundle. For each file in `files_to_assess`, produce a phase_map
entry per milestone, a scope verdict, and a help block. Identify gaps
where the catalog requires an artifact under this batch's role and no
file in any taxonomy satisfies it.

Write EXACTLY ONE JSON document — no commentary, no markdown fences —
to:
  <output_path>

Strict JSON only. The deterministic merger parses without tolerance.
```

### Step 3 — Merge agent outputs (deterministic, no LLM)

```bash
python3 .claude/skills/tracker/scripts/merge_phase_map_results.py \
  --project-dir <project-root> \
  --bundles-dir /tmp/phase-map-bundles/

# Or preview without writing
python3 .claude/skills/tracker/scripts/merge_phase_map_results.py \
  --project-dir <project-root> \
  --bundles-dir /tmp/phase-map-bundles/ --dry-run
```

Writes three sidecars:
- `docs/project/submissions/submission-tracker.phase-map.json`
- `docs/project/submissions/submission-tracker.help.json`
- `docs/project/submissions/submission-tracker.gaps.json`

Plus a stdout summary: file count, scope split (submission vs other),
posture totals, gap count per milestone, help block count.

### Step 4 — Regenerate the tracker

```bash
uv run --project tools/project-console python \
  .claude/skills/tracker/scripts/generate.py --project-dir <project-root> --md --candidate

uv run --project tools/project-console python \
  .claude/skills/tracker/scripts/render.py --project-dir <project-root> --candidate
```

Generator behavior changes when phase-map sidecar is present:
- Stops the cartesian (file × milestone) explosion. Emits ONE row per
  (file, milestone) where posture is non-`n/a`.
- Skips rows for `scope: other` files; surfaces them in a separate
  "Out of Scope" / "Other" section instead.
- Uses `version_label` from the phase-map for the row's version field.

Renderer behavior:
- Adds a per-milestone "Gaps" band listing missing required artifacts.
- Adds an "Other / Out of Scope" section.
- Help block ((?) panel) populated from the new help.json.

## Cost / scope guidance

- Typical project: ~10-20 batches, ~30-40K tokens each, ~500K-800K total.
  One pass per significant taxonomy change.
- Per-batch budget targets a single Sonnet/Opus call; output is bounded
  (per-file ~700 tokens × max 10 files = ~7K).
- Re-run incrementally by passing `--role <X>` to limit the bundle build
  to one role's worth of work.
- The merger is idempotent — overwrites the sidecars on each run. Older
  agent runs whose result.json files are still in the bundles dir will
  be re-merged.

## Idempotency

- Bundle builder reads taxonomy + project.yml + dhf-manifest at build
  time. Re-running rebuilds bundles; old bundles in the same `--out`
  directory are overwritten.
- Merger replaces all three sidecars atomically on each run.
- Per-batch cache: bundle paths are deterministic per (taxonomy_id,
  batch_index, role); re-runs against the same project state produce
  identical bundle paths.

## Output artifacts

| Path | Producer | Purpose |
|---|---|---|
| `/tmp/phase-map-bundles/<id>.yaml` | builder | Agent input |
| `/tmp/phase-map-bundles/<id>.result.json` | regulatory-affairs subagent | Agent output (one per batch) |
| `/tmp/phase-map-bundles/manifest.json` | builder | Bundle ↔ taxonomy lookup for merger |
| `submission-tracker.phase-map.json` | merger | Per-file × milestone posture + scope |
| `submission-tracker.help.json` | merger | Per-file (?) help blocks (extends prior shape) |
| `submission-tracker.gaps.json` | merger | Per-milestone consolidated gap list |

## Boundary vs `enrich-help` and `classify-folders`

- `enrich-help` (existing): help-only. Single-purpose, called when only
  help text needs refresh.
- `classify-folders` (existing): folder-aggregation only (Tier 2).
- `assess-phases` (this action): combined phase-map + help + gap detection
  in ONE agent dispatch per role-batch. Replaces `enrich-help` for
  projects that have run `assess-phases` (the help.json shape from this
  action is a superset of `enrich-help`'s).
