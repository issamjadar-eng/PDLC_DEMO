# Action: `render`

Derive machine-readable JSON sidecars from the gap-analysis markdown so downstream consumers (primarily the **project-console** Gap Analysis view) can render analyses natively without parsing prose.

## Usage

```
/gap-analysis render [--check] [--strict-recs]
```

## Arguments

- **`--check`** (optional) — don't write; exit non-zero (2) if any sidecar is missing or stale relative to its markdown. For CI / `/best-practices` drift checks. Exit code reflects **sidecar staleness only** — backward-compatible with existing consumers.
- **`--strict-recs`** (optional) — turn the advisory recs-completeness audit into a hard gate: exit non-zero (3) if any **contributing** agent (one that authored a finding or has an `agent:` changelog row) lacks a matching `recs-<name>.md` writeup beside the aggregate. Combine with `--check` for CI enforcement. Without this flag, missing recs files are still printed as advisory `WARN` lines (stderr) but do not affect the exit code.

## Recs-completeness audit (always runs)

In **every** mode, the renderer audits each analysis for the console advisor-tab requirement: every contributing agent in the sidecar `agents[]` should have a sibling writeup the console can discover (`recs-<name>.md`, matched exactly as `console/gap_analysis/loader.py:load_narratives` does). Any gap prints:

```
  WARN <analysis-id>: contributing agent(s) without a writeup — missing recs-<name>.md
```

This is **advisory by default** (a merely-recommended agent that never contributed is not flagged — that's "fan-out not done yet"). Pass `--strict-recs` to make it a non-zero exit. Rationale for warn-by-default: pre-existing analyses authored before the dual-output fan-out contract (e.g. aggregate-only `qsub-*` analyses) would otherwise turn `/best-practices` red without any new authoring error.

## What it produces

Under `docs/_analysis/`:

- **`<component>/<id>/<id>.gap.json`** — per-analysis structured detail, written beside the aggregate inside the analysis folder (one per analysis).
- **`index.json`** — lightweight roll-up array of every analysis (status / topic / component / agents / stats) for the console's list view.

Both are **derived projections** of the markdown. The `.md` is the single source of truth; the JSON is regenerated and never hand-edited. This mirrors the `trace-matrix` sidecar / `drift.json` contract — the producer emits a stable JSON shape; the consumer (console) knows nothing about how it was produced.

## Steps

1. Run the deterministic renderer (pure standard library — no third-party deps):
   ```bash
   python3 .claude/skills/gap-analysis/scripts/render_sidecars.py
   ```
2. The script walks the folder-per-analysis layout `docs/_analysis/<component>/<id>/<id>.md` (the aggregate file — the one whose stem matches its folder name; `recs-*.md` / `research-*.md` / `README.md` siblings are skipped), skips any aggregate without an `id:` frontmatter, and for each writes `<id>/<id>.gap.json` beside it; then writes the roll-up `index.json`.
3. Report the count written. Re-running with no markdown change is idempotent (byte-identical output → nothing rewritten).

**When to run:** after `/gap-analysis init` (to register the new analysis in the index) and after `/gap-analysis fan-out` (to project the freshly-appended findings). Also any time an analysis markdown is hand-edited. The console reads whatever sidecars exist and degrades gracefully (empty-state hint) when they're absent — exactly like the trace-matrix view.

## JSON schema (`schema_version: "1.0"`)

Per-analysis `<id>.gap.json`:

| Key | Shape | Source |
|-----|-------|--------|
| `schema_version` | string | constant |
| `meta` | `{id,title,status,topic,component,created,last_updated,superseded_by,source_md,source_doc_url}` | frontmatter |
| `authored_by` | `["human:name", "agent:name", …]` | frontmatter `authored_by` |
| `grounding` | `[{type,path,note}]` | frontmatter `grounded_against` (typed pointers) |
| `agents` | `[{name,role,ran,contributed_finding_ids[],changelog_summary}]` | `recommended_agents` (role: first=primary) + finding authorship + `agent:` changelog rows |
| `assertions` | `[{id,assertion,clause,evidence,status,status_label}]` | `## Assertions` table; `status` normalized to confirmed/partial/refuted/verify/open |
| `findings` | `[{id,label,author,body_md}]` | `## Findings` F-N blocks (body kept as markdown — consumer renders it) |
| `recommendations` | `[string]` | `## Recommendations` list |
| `open_questions` | `[string]` | `## Open Questions` list |
| `stats` | `{grounding_count,agent_count,assertion_count,assertion_status_counts,finding_count}` | derived |

Roll-up `index.json`: `{schema_version, analyses:[{id,title,status,topic,component,last_updated,source_md,sidecar,agents[],stats}], counts:{total,by_status,by_topic,by_component}}`.

## Notes

- **Derived, not authored** — never edit the `.gap.json` by hand; edit the `.md` and re-render. The renderer is idempotent.
- **No new project config** — the script discovers the repo root via `project.yml` and walks the fixed `docs/_analysis/` tier. Project-agnostic.
- **Schema versioning** — bump `SCHEMA_VERSION` in `scripts/render_sidecars.py` (and this table + the README changelog) when the shape changes, so consumers can guard on `schema_version`.
- **Findings stay as markdown** — the F-N body is intentionally not decomposed into sub-fields; prose shape varies across authors/advisors, so the consumer renders the markdown chunk. The structured surface (meta / grounding / agents / assertions / stats) is what drives the cards.
