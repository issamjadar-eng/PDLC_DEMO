# Build actions: `build-reference`, `build-qms`, `build-manifest`

Three build steps feed one another. Each is idempotent.

```
build-reference   (skill-owned)          data/tier1-regulatory/*.md   ──▶  data/tier3-reference/reference-dhf.{yml,md}
build-qms         (project-owned)        docs/project/dhf-manifest/qms-manifest.md   ──▶  qms-manifest.json
build-manifest    (project-owned)        reference-dhf.yml + qms-manifest.json + project.yml   ──▶  <project>-dhf-manifest.{md,json} + <project>-dhf-by-section.md
dashboard         (project-owned)        <project>-dhf-manifest.json   ──▶  <project>-dhf-dashboard.md
```

---

## `build-reference` (maintainer-only)

Rebuild the skill-owned Reference DHF cache from Tier 1 distillations.

**When to run**: after authoring or updating any `data/tier1-regulatory/*.md` file.

**Script**: `scripts/build-reference.py`

```bash
python3 .claude/skills/dhf-manifest/scripts/build-reference.py [--dry-run]
```

**Inputs**: `data/tier1-regulatory/*.md` — each file is one regulatory source (FDA guidance or standard). Each contains YAML obligation blocks per `templates/tier1-distillation.md.tmpl`. Each YAML block MUST be preceded by an HTML anchor line `<a id="OBL-xxx"></a>` so downstream Reg-Source links resolve.

**Outputs** (under `data/tier3-reference/`): `reference-dhf.{yml,md}`, `scope-schema.yml`, `dimensions/scope-<name>.md`.

**Exit codes**: 0 = success, 1 = YAML parse error, 2 = duplicate `id` field.

---

## `build-qms`

Rebuild the project QMS sidecar JSON from the hand-authored `qms-manifest.md`.

**When to run**: after any edit to `qms-manifest.md` (adding or updating a QMS obligation). Typically invoked indirectly via `build-manifest`.

**Script**: `scripts/build-qms.py`

```bash
python3 .claude/skills/dhf-manifest/scripts/build-qms.py [--dry-run]
```

**Inputs**: `docs/project/dhf-manifest/qms-manifest.md` — one H2 per source SOP/WI/FORM/POL, each followed by a compact table and a single `<!-- QMS-DATA ... -->` HTML comment block that contains the structured YAML records.

**Output**: `docs/project/dhf-manifest/qms-manifest.json` with:

| Key | Shape | Purpose |
|-----|-------|---------|
| `qms_obligations[]` | full records | flattened list across all sources |
| `by_source` | `{SOP-xxx: [QMS-ids]}` | per-source index |
| `by_topic` | `{topic: [QMS-ids]}` | per-topic index (used for topic-fallback rendering) |
| `obl_to_qms` | `{OBL-xxx: [QMS-ids]}` | reverse map — Reg obligation → governing QMS procedures |
| `qms_to_obl` | `{QMS-xxx: [OBL-ids]}` | forward map — QMS procedure → regulatory obligations covered |

**Exit codes**: 0 = success, 1 = `qms-manifest.md` missing, 2 = YAML parse error in a `QMS-DATA` block, 3 = duplicate QMS-ID.

---

## `build-manifest`

Project the skill-owned Reference DHF through `project.yml` scope + per-item classifications, join with QMS grounding, and write three views.

**When to run**: after any scope change, new DHF addition, Tier 1 or Tier 2 update, or simply to refresh after an artifact binding.

**Script**: `scripts/build-manifest.py`

```bash
python3 .claude/skills/dhf-manifest/scripts/build-manifest.py [--dry-run] [--delta] [--scope FLAG=VALUE]
```

**Inputs**:
- `data/tier3-reference/reference-dhf.yml` — scope-filterable source of truth (114+ obligations)
- `docs/project/dhf-manifest/qms-manifest.json` — loaded for the `QMS Grounding` column (if missing, the column renders blank with a console WARNING)
- `data/tier1-regulatory/*.md` — scanned for OBL anchors so `Reg Source` cells can deep-link
- `project.yml` — `scope:` block + `dhfs[].classification` per item

**Routing algorithm**:
1. For each Reference DHF entry, check `scope_flags` against `project.yml scope:` — skip if mismatch.
2. `dhf_owner=system` entries route to the system DHF leaf.
3. `dhf_owner=item` entries route to every item DHF whose `iec62304` class ≥ entry's `min_iec62304_class`, AND whose classification accepts the entry's `ai`/`pccp` flags.
4. `dhf_owner=both` routes to both.
5. Lookup `obl_to_qms[OBL-ID]` for direct QMS grounding; fall back to topic-level QMS count when no direct match.

**Outputs** (all under `docs/project/dhf-manifest/`):

| File | Role |
|------|------|
| `<project>-dhf-manifest.md` | **View 1** — one section per DHF; within each, topic subsections with enriched table (ID · Obligation · Artifact Type · Deliverables · Reg Source · QMS Grounding · Status) |
| `<project>-dhf-manifest.json` | Sidecar — full record per routed entry with `reg_source`, `qms_grounding`, and `status/location` |
| `<project>-dhf-by-section.md` | **View 2** — same data, outer grouping `Topic → DHF → obligations` for domain-SME review |

**Variants**:
- `--delta` — diff the new run's routed IDs against the previously written `<project>-dhf-manifest.json` and print added/dropped IDs.
- `--scope FLAG=VALUE` — apply a hypothetical scope override and render to stdout without writing (PCCP change-impact preview).

**Per-item filtering** applied during routing:
- `ai` scope flag → obligation excluded from any item DHF without `ai_enabled=true`
- `pccp` scope flag → obligation excluded from non-SaMD items
- `min_iec62304_class: C` → obligation excluded from Class B items (e.g., mgmt-services)
