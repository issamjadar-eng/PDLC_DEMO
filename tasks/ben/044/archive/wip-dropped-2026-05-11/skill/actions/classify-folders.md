# action: classify-folders

Tier 2 LLM classifier for taxonomy folders the deterministic Tier 1
heuristic could not decide. Mirrors the `enrich-help` / `enrich-details`
fan-out pattern: a bundle builder emits per-folder context bundles, the
parent dispatches one `folder-classifier` agent per bundle in parallel, a
merger applies verdicts back to the taxonomy file(s).

**When to invoke**: after `init-taxonomy` reports any folders with
`confidence: low` or after `reconcile-taxonomy` adds new folders to
`pending:` that the user wants the agent to triage. NOT auto-run by
`init-taxonomy` (Tier 1 catches the obvious patterns; Tier 2 costs LLM
tokens × N folders).

## Flow

### Step 1 — Enumerate uncertain folders

```bash
python3 .claude/skills/tracker/scripts/build_classify_context.py \
  --project-dir <project-root> --all --dry-run
```

If output is `Uncertain folders: 0`, stop — nothing for Tier 2 to do.

### Step 2 — Build context bundles

```bash
python3 .claude/skills/tracker/scripts/build_classify_context.py \
  --project-dir <project-root> --all --out /tmp/classify-bundles/
```

Writes one `<bundle_id>.yaml` per uncertain folder + a `manifest.json`
listing each (folder, bundle_path, output_path).

### Step 3 — Dispatch agents in parallel

For each bundle in `manifest.json`, dispatch one `folder-classifier` agent.
Use the **single-message multi-tool-call pattern** so they run concurrently.

The agent reads its bundle, judges the folder (aggregate / independent /
primary-with-supplements), and writes a verdict JSON to the path given in
`bundle.output_path`. The agent must NOT print anything else; the merger
parses strictly.

### Step 4 — Merge verdicts back to taxonomies

```bash
python3 .claude/skills/tracker/scripts/merge_classify_results.py \
  --project-dir <project-root> \
  --bundles-dir /tmp/classify-bundles/ \
  --manifest /tmp/classify-bundles/manifest.json
```

For each verdict:

- **aggregate** / **primary-with-supplements**: per-file mappings under the
  folder are removed; one folder mapping (key with trailing slash) is added
  carrying `aggregate: folder`, `primary_member`, `members`, `confidence`,
  `rationale`, `tier2_classifier: true`.
- **independent**: per-file mappings unchanged; an entry is appended to
  `classifier_notes:` in the taxonomy so reviewers see the agent's call
  and rationale.

Add `--dry-run` to preview without writing. Add
`--default-role <role>` if the merger can't recover canonical_role from
removed per-file mappings (rare; only happens when the verdict is applied
without prior per-file mappings present).

### Step 5 — Regenerate the tracker

```bash
uv run --project tools/project-console python \
  .claude/skills/tracker/scripts/generate.py --project-dir <project-root> --md --candidate

uv run --project tools/project-console python \
  .claude/skills/tracker/scripts/render.py --project-dir <project-root> --candidate
```

Reload the candidate dashboard; rows reflect the new aggregations.

## Idempotency

- The bundle builder skips folders already mapped as `aggregate: folder`
  (no re-classification of folders Tier 1 or a prior Tier 2 run already
  decided). Re-runs only target genuinely uncertain folders.
- The merger is destructive on per-file mappings under an aggregated folder
  — by design. Re-run safe because there's nothing to remove the second
  time.
- `tier2_classifier: true` flag on aggregate entries makes Tier 2 verdicts
  distinguishable from Tier 1 verdicts in audit / review.

## Cost / scope guidance

- Agent dispatch is the cost driver — one LLM call per uncertain folder.
- For projects with strong naming conventions (e.g., `PREFIX-NNNN` series
  ubiquitous), Tier 1 catches everything and Tier 2 is unused.
- Expect Tier 2 to be relevant when projects have:
  - Folders with mixed file types where role uniformity is unclear
  - Custom naming conventions Tier 1's regex doesn't recognize
  - Single-file folders with unusual names (heuristic punts to per-file
    by default; agent can re-classify as a one-off aggregate or note the
    file as not-evidence)

## Output artifacts

| Path | Producer | Purpose |
|---|---|---|
| `/tmp/classify-bundles/<id>.yaml` | builder | Agent input |
| `/tmp/classify-bundles/<id>.verdict.json` | agent | Agent output |
| `/tmp/classify-bundles/manifest.json` | builder | Bundle ↔ taxonomy lookup for merger |
| Mutated `.taxonomy.yml` files | merger | Aggregate decisions applied |
| `submission-tracker.aggregates.json` | next `/tracker generate` | Renderer sees the new aggregates |
