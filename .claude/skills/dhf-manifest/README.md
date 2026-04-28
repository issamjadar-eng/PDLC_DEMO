# dhf-manifest — Design & Architecture

This document is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Best Practices

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| `docs/project/dhf-manifest/` exists | Directory present | Required | shared |
| Tier 1 files present | `data/tier1-regulatory/*.md` count ≥ 1 | Required | shared |
| QMS manifest authored | `docs/project/dhf-manifest/qms-manifest.md` exists with ≥ 1 `<!-- QMS-DATA -->` block | Recommended | shared |
| QMS manifest JSON current | `qms-manifest.json` mtime ≥ `qms-manifest.md` mtime | Recommended | shared |
| DHF manifests current | `docs/project/dhf-manifest/hiplink-manifest.{md,json}` mtime ≥ `qms-manifest.json` mtime | Recommended | shared |
| Validate clean | `scripts/validate.py` exits 0 | Required | shared |
| Unbound obligation coverage | Load `hiplink-manifest.json`; compute `status=GAP` count. If ≥ 80% GAP, emit INFO (expected early-stage). If 0% bound AND qms-manifest.md has real content (>5 blocks), emit WARN — obligations present but no artifacts located | Info/Warn | shared |
| No orphan DHF artifacts | For each file path recorded as `location` in `hiplink-manifest.json` (non-null entries), verify the path exists on disk. Report missing paths as WARN per entry | Recommended | shared |
| Manifest ↔ reference drift | Check `hiplink-manifest.json` mtime against `data/tier3-reference/reference-dhf.yml` mtime. If reference-dhf is newer than the manifest, emit WARN: "DHF manifest is older than Reference DHF — run `/dhf-manifest build-manifest` to reproject." | Recommended | shared |

## Changelog

- 5 (2026-04-24): **Title field + hyperlinked `ID · Title` rendering everywhere.** Schema gained required `title` field on all 114 Tier 1 obligations + all 115 QMS records. New `scripts/_linking.py` shared helper exports `render_obl_link` / `render_qms_link` / `find_bare_ids` / `is_valid_title` (canonical shape: `[\`OBL-XXX\` · Title](src.md#OBL-XXX)` — middle-dot separator, backtick-wrapped ID, clickable label). All three builders (`build-reference.py`, `build-manifest.py`, `build-qms.py`) emit linked labels across master table + 11 dimension tables + hiplink-manifest.md + hiplink-by-section.md + qms-manifest.md. `validate.py` gains strict title quality check (non-empty, ≤ 60 chars, no pipe char, no markdown syntax) — 12/12 passed. `build-manifest.py` + `build-qms.py` run post-build bare-ID grep (exit 2 / exit 4) on rendered output to enforce every ID is inside a clickable link. `agents/dhf-distiller.md` + `actions/distill.md` updated so new QMS records carry titles from birth, with worked-example table (good vs bad titles). Three new applicator scripts: `apply-titles.py` (114 Tier 1 titles applied wholesale), `draft-qms-titles.py` (source-title-first heuristic with §-section/topic disambiguation), `apply-qms-titles.py` (115 QMS titles applied into `<!-- QMS-DATA -->` YAML blocks). (task ben/104)
- 4 (2026-04-24): Skill-side data layout restructured to mirror `medtech-docs/references/`: `data/tier1-regulatory/` → `data/{fda-guidance,standards,industry-frameworks}/`; aggregate flattened from `data/tier3-reference/` up to `data/` root. Each source MD now has a sibling JSON sidecar (built by `build-reference.py` — single-source programmatic primitive). Added 5 industry-framework stubs (AAMI TIR57, TIR45, SW96, IMDRF SaMD, GMLP) — empty shells with distill-backlog notes. `build-manifest.py`, `validate.py` updated to walk categories; Reg Source deep links now include category segment. Full pipeline re-ran: 11/11 validate PASS, 114 obligations, 19 sources (fda-guidance=8, standards=6, industry-frameworks=5 stubs), 251 routed Tier 4 entries. (task ben/069 session 6)
- 3 (2026-04-24): Flattened project-side layout (no tier-prefix folders); Tier 2 consolidated into single hand-authored `qms-manifest.md` with hidden `<!-- QMS-DATA -->` blocks + built `qms-manifest.json` sidecar; `hiplink-manifest.md` enriched with `Reg Source` (deep-linked to Tier 1 anchors) and `QMS Grounding` (direct QMS-IDs or topic fallback) columns; new `hiplink-by-section.md` (View 2 — topic-first) and `hiplink-dashboard.md` (View 3 — status/coverage); `gap-report.md` retired. Best-practice checks updated for new paths. New `build-qms` + `dashboard` actions. (task ben/069)
- 2 (2026-04-21): Added 3 new best-practice checks: unbound coverage (GAP % threshold), orphan artifact detection (stale location bindings), Tier 4↔disk drift (manifest older than reference-dhf). (task ben/069)
- 1 (2026-04-21): Initial scaffold. SKILL.md slimmed to router; implementation detail moved to actions/. 4-tier model, project.yml as scope source. (task ben/069)
