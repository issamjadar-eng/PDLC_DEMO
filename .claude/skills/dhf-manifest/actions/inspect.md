# Actions: `dashboard`, `validate`, `reproject`, `scope diff`

Read-only inspection actions — none mutate the skill-owned caches or project-side hand-authored files.

> The separate obligation trace matrix / gap-report outputs from earlier versions are now subsumed by `hiplink-by-section.md` (topic-first trace) and `hiplink-dashboard.md` (per-module status + QMS-coverage bars). There is no standalone `trace-matrix/` folder anymore — the name also collided with the unrelated intra-DHF trace concept in `/trace-matrix`.

---

## `dashboard`

Per-module summary view — authoring status (GAP vs FOUND) plus QMS-coverage breakdown (direct vs topic-fallback vs none) per topic.

**Script**: `scripts/dashboard.py`

```bash
python3 .claude/skills/dhf-manifest/scripts/dashboard.py
```

**Inputs**: `docs/project/dhf-manifest/hiplink-manifest.json` (must exist — run `build-manifest` first).

**Output**: `docs/project/dhf-manifest/hiplink-dashboard.md` — "what have we authored and what's left?" at a glance.

---

## `validate`

Structural compliance checks — deterministic, no LLM.

**Script**: `scripts/validate.py`

| Check | Pass condition |
|-------|---------------|
| Tier 1 files present | `data/tier1-regulatory/*.md` count ≥ 1 |
| Reference DHF parseable | `data/tier3-reference/reference-dhf.yml` loads cleanly |
| No duplicate OBL IDs | every `id:` in Tier 1 is unique |
| OBL required fields | every OBL record has id, source, topic, artifact_type, dhf_owner |
| Valid topic | `topic` is one of the 16 DHF topics |
| Valid scope flags | all `scope_flags[]` entries are known scope dimensions |
| Min IEC class valid | `min_iec62304_class` ∈ {A, B, C, null} |
| QMS-manifest parseable | every `<!-- QMS-DATA -->` block is valid YAML |
| No duplicate QMS IDs | every `id:` in QMS-DATA blocks is unique |
| Tier 4 ID consistency | every entry in `hiplink-manifest.json` corresponds to an OBL in Reference DHF |
| Anchors present | every Tier 1 OBL has an `<a id="OBL-xxx"></a>` line preceding its YAML block |

Exit 0 only if all checks pass.

---

## `reproject`

Delta view — diff the current routed-obligation set against the previously written manifest.

**Script**: `scripts/build-manifest.py --delta`

Reads the old `hiplink-manifest.json`, recomputes the routing, and reports added/dropped OBL IDs per DHF. Used after editing `project.yml` scope or Tier 1 content to confirm the blast radius.

---

## `scope diff`

Hypothetical scope override — preview the routing impact without writing.

**Script**: `scripts/build-manifest.py --scope FLAG=VALUE`

Runs a full projection with the given flag override applied to the in-memory scope vector, renders the resulting `hiplink-manifest.md` to stdout, and never writes. Useful for PCCP change-impact analysis (e.g., `--scope hardware=true` to see what the manifest would look like if HipLink added a hardware component).

---

## PCCP change-reasoning workflow

`reproject` and `scope diff` are the primary tools for PCCP change-impact analysis.

1. A planned device modification changes the scope — e.g., adding a new imaging modality, extending to EU, enabling hardware sensing.
2. Use `scope diff` to preview impact *before* committing: `/dhf-manifest scope diff geography=[us,eu]` → prints added/dropped obligations.
3. If approved, update `project.yml scope:` and run `reproject` to get the committed delta.
4. The delta report becomes PCCP modification-protocol evidence: "Change X adds obligations Y1–Y12; no obligations dropped; these obligations bind to deliverables A, B, C."

| PCCP Change Type | Scope flag(s) affected | Expected delta |
|-----------------|----------------------|----------------|
| Add EU geography | `geography: [us,eu]` | MDR-equivalent obligations added |
| Add clinical studies | `clinical_evaluation: studies` | Clinical investigation obligations added |
| Add hardware sensing | `hardware: true` | IEC 60601-1 + physical safety obligations added |
| Enable OTA updates | `ota_updates: true` | Cybersecurity patching + update-validation obligations added |
| Add AI model version | `ai_enabled: true` on new item | AI/ML PCCP + lifecycle obligations per new item |

---

## Tracker integration (planned)

`/tracker` currently reads per-filing composition manifests to determine which DHF deliverables are in each filing. Planned integration: filter `hiplink-manifest.json` by filing phase to show obligation coverage per filing.

Pre-conditions not yet met:
- Tier 1 obligations need `filing_phase[]` tags (`qsub`, `510k`, `pccp`, `all`).
- `dashboard.py` needs a `--filing <name>` mode that filters by filing.
- Composition manifests need real artifact lists before coverage numbers are meaningful.

Until then, use `hiplink-dashboard.md` for all-filing coverage and `/tracker build` for filing-specific status.
