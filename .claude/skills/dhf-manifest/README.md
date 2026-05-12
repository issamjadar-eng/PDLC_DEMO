# dhf-manifest — Design & Architecture

This document is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`. For per-action mechanics, see `actions/<action>.md`.

---

## 1. Skill purpose

`/dhf-manifest` answers two related questions that `/trace-matrix` cannot:

1. **Are the right documents present in the DHF?** (Coverage.)
2. **Which obligations must each document satisfy, and which QMS procedure governs its production?** (Governance.)

It does this through two complementary outputs:

- The **obligation manifest pipeline** (since v1): a 4-tier model that projects regulatory and QMS obligations through a project scope vector into a per-DHF manifest with gap report.
- The **discovery-index pipeline** (since v8): a thin, project-agnostic catalog that resolves canonical document roles to concrete project paths, so consumer skills (advisor agents, the project console, downstream skills) can locate the right files without baking project-specific paths into their templates.

Both pipelines share the same core principle: **the skill is project-agnostic; per-project values come from `project.yml` + the project's filesystem.**

---

## 2. Two pipelines, one skill

```
PIPELINE A — OBLIGATION MANIFEST                       PIPELINE B — DISCOVERY INDEX
────────────────────────────                           ───────────────────────────

SKILL-OWNED                  PROJECT-OWNED             SKILL-OWNED                       PROJECT-OWNED
  data/fda-guidance/*.md       qms-manifest.md           data/canonical-roles.yaml         project.yml
  data/standards/*.md       ┐  + qms-manifest.json       (L1 + L2)                       ┐ (L3 overrides,
  data/industry-           ─┤                            scripts/discovery-index.py      ─┤  optional)
   frameworks/*.md         ┘     (Tier 2)                                                ┘
  reference-dhf.yml          <project>-dhf-manifest.{md,json}                            <project>-dhf-discovery.json
                             <project>-dhf-by-section.md
                             <project>-dhf-dashboard.md
```

The two pipelines are independent — each can be regenerated without touching the other — and consumed by different downstream skills.

---

## 3. Pipeline A: 4-tier obligation manifest

Layers feed one another; each layer's output is the next layer's input. The skill is readable from layer 1 alone — no need to wait for the full stack.

| Tier | What | Owned by |
|---|---|---|
| **Tier 1** (reference) | Curated regulatory + standards + industry-framework source corpus, distilled to obligation atoms with stable IDs. | Skill (`data/{fda-guidance,standards,industry-frameworks}/*.md` + JSON sidecars) |
| **Tier 2** (QMS) | Project's QMS / SOP records — the procedures the program will use to discharge obligations. | Project (`docs/project/dhf-manifest/qms-manifest.md` + JSON sidecar) |
| **Tier 3** (reference DHF) | A reference architecture for "what doc types exist in a generic medtech DHF" — used for projection. | Skill (`data/reference-dhf.yml`) |
| **Tier 4** (project DHF view) | Tier 1 obligations projected through the project's scope vector × Tier 3 doc-type lookup × Tier 2 QMS grounding. | Built artifact (`<project>-dhf-manifest.{md,json}`) |

Three rendered views over Tier 4: master manifest (Tier 1 ID × DHF doc × QMS source), topic-first by-section view, and status dashboard.

Actions: `build-reference`, `build-qms`, `build-manifest`, `dashboard`. All hand-edits are confined to Tier 2; Tier 4 is fully regenerated.

---

## 4. Pipeline B: discovery-index — the canonical-role IoC layer

### 4.1 The problem it solves

Consumer skills (advisor agents, project-console workflows) historically grounded themselves by referencing **literal globs in their own skill files** — e.g., `docs/project/dhfs/**/design-controls/architecture/**/*.md`. Two problems:

- **Token bloat.** Eager-globbing every architecture file across a multi-DHF project loads ~170 K tokens per invocation. Most of that is irrelevant to any given question.
- **Project-shape coupling.** Glob patterns hardwire one folder convention. Projects with different conventions (externally-organized DHFs mirroring Confluence, flat layouts, vendor-specific taxonomies) silently miss files or load the wrong ones.

The discovery-index pattern inverts control: the **skill** declares abstract canonical roles (e.g., `regulatory_strategy`, `system_architecture`, `complaints`), and the **project** provides a resolved role→path mapping via `project.yml` + a generated index. Consumer agents reference roles by name; they read the project-side index at runtime to learn the concrete paths.

### 4.2 The three-level model

| Level | Lives in | Contains | Owned by |
|---|---|---|---|
| **L1 — Canonical role names + scope semantics** | `data/canonical-roles.yaml` (skill) | Role names, scopes (`project` / `per-dhf` / `per-submission` / `external_data`), descriptions, consumer-advisor labels, the `multi_file` flag for artifact families. | Skill maintainers |
| **L2 — Ranked alternatives library** | same file (skill) | Per role: ranked list of filename/glob `patterns` (most-specific first) seen across consuming projects; per-mode `folder` entries for `internal` vs `external` DHF organization. | Skill maintainers (append-mostly as new project conventions surface) |
| **L3 — Project-resolved bindings** | `<project>/project.yml` (durable overrides, optional) + `<project>/docs/project/dhf-manifest/<slug>-dhf-discovery.json` (generated) | Per role, per-DHF: resolved path or folder pointer, ambiguity notes, gap reports. | Project authors (overrides) / `discovery-index` action (generated) |

**The IoC contract:**

- A new project does not author L1 or L2 — it inherits both from the skill.
- A new project authors only `project.yml dhfs[]` and runs `/dhf-manifest discovery-index`. The resolver probes the L2 ranked patterns against the project's filesystem; the result lands in L3 as `<slug>-dhf-discovery.json`.
- Projects with non-standard conventions add minimal `project.yml evidence_layout.layers[role].{patterns_extra, patterns_exclude, folder_override}` blocks. The override block is **empty in the common case.**
- Skill files contain no project-specific paths. Project files contain no skill conventions. The index ties the two together.

### 4.3 Resolution algorithm

```
For each role in canonical-roles.yaml:

  Determine scope semantics from the role's L1 declaration:
    project        — resolve once project-wide
    per-dhf        — resolve once per DHF entry in project.yml
    per-submission — resolve once per submission entry
    external_data  — registry-relative; always folder-pointer (no winner)

  For per-dhf roles, branch on dhf.dhf_organization:
    internal — use role.internal.{folder, patterns}; search under dhf.path/folder
    external — use role.external.{taxonomy_folder, patterns}; resolve folder via
               the DHF's .taxonomy.yml mappings; supports two sub-conventions:
               (a) nested  — <folder>/v*.md + <folder>/index.md
               (b) flat    — <folder>.md

  Compute effective patterns = L3 patterns_extra + L2 patterns − L3 patterns_exclude

  Output shape depends on multi_file flag:

    Single-file role (multi_file absent / false):
      Probe patterns in order; first pattern with EXACTLY ONE match wins.
      Output: { path, exists, size_bytes, tokens_estimate, matched_pattern }
      Multi-match → ambiguity_notes[] (winner picked by rank, alternatives recorded).
      Zero-match → gaps[].

    Multi-file role (multi_file: true):
      Enumerate ALL matches across ALL patterns.
      Output: { folder, exists, file_count, patterns_used }
      No winner concept — downstream consumers Glob the folder as needed.
      Empty-but-existing folder is a valid 0-count entry, NOT a gap.
```

### 4.4 Output shapes the index emits

The index has five top-level resolution buckets plus diagnostics:

```jsonc
{
  "project_roles":     { <role>: <single-file-entry | folder-pointer-entry>, ... },
  "dhf_roles":         { <dhf-leaf>: { "role": "system|item", "dhf_organization": "internal|external",
                                       <role>: <entry | null>, ... }, ... },
  "submission_roles":  { <submission-id>: { <role>: <entry | null>, ... }, ... },
  "external_roles":    { <role>: <folder-pointer-entry>, ... },
  "gaps":              [ { scope, dhf?, submission?, role, reason, patterns_tried, informational? }, ... ],
  "ambiguity_notes":   [ { scope, dhf?, role, winning_pattern, winning_path, alternatives: [...] }, ... ]
}
```

**Single-file entry:** `{ path, exists, size_bytes, tokens_estimate, matched_pattern }`. Consumers `Read` the path.

**Folder-pointer entry:** `{ folder, exists, file_count, patterns_used }`. Consumers `Glob` inside the folder when they need per-file specifics. This shape lets advisor researcher subagents be given "here, N files in this folder" hints rather than enumerating every file in the index. The same shape is used for `external_data` scope and for any role declaring `multi_file: true`.

**Gap classification:**
- **Real gap**: role expected to resolve, didn't. Surfaces an authoring or naming-convention issue worth fixing.
- **Informational gap** (`informational: true`): role legitimately not applicable — e.g., a Confluence-mirror DHF's template doesn't include a standalone Risk Management Plan (RMP), or a new role declares an external-mode mapping the project's taxonomy hasn't yet cataloged. Not a failure.

### 4.5 The `multi_file` flag — why folder pointers matter

A handful of role families don't fit the "exactly one canonical file" model:

| Family | Examples |
|---|---|
| Customer-voice corpora | KOL interview reports, market research, competitive analyses |
| Post-market signal streams | Complaints, CAPA records, adverse-event reports, FSCA artifacts |
| Cumulative evidence sets | Literature search citations, V&V test protocols, V&V execution reports |
| Versioned correspondence | Vulnerability disclosure records, PMCF study reports |

Forcing these into single-file resolution either loses information (one "canonical complaint" doesn't exist) or balloons the index (enumerating 200 complaints inflates every consumer's read budget).

The `multi_file: true` flag tells the resolver to emit a folder-pointer entry — `{folder, file_count}` — same shape as `external_data` roles. Consumers:

- Get cheap "look here" signal from Tier 2 grounding (folder + N).
- `Glob` inside the folder with question keywords when they need specifics.
- Can pass the folder as a `hints:` parameter to a Tier 3 researcher subagent.

Available on `project` and `per-dhf` scopes. Per-DHF multi-file is supported in `internal` mode; external-mode multi-file is deferred until a taxonomy convention is identified.

---

## 5. How consumer skills use the index

### 5.1 Advisor agents — the regulatory-affairs pilot

The `regulatory-affairs` advisor (and the rest of the advisor fleet, as they migrate) uses **three-tier canonical-role grounding** authored in its frontmatter `console.canonical_roles:` block:

```yaml
canonical_roles:
  tier_1:               # required reading on every invocation
    - role: regulatory_strategy
    - role: architecture_strategy
    - role: system_architecture
      dhfs: {role: system}    # yaml-native selector
  tier_2:               # triaged per question
    - role: predicate_analysis
    - role: submission_package
      submissions: all
    - role: kol_feedback        # multi-file role — folder pointer
    # ...
  tier_3:               # researcher subagent for thin-grounding cases
    researcher: advisor-researcher
```

The advisors skill's `scripts/render-grounding.py` reads this frontmatter and the L1+L2 registry's role descriptions, and regenerates the agent body between `<!-- BEGIN GROUNDING -->` / `<!-- END GROUNDING -->` markers. The rendered body references **role names**, not paths — so the skill output stays project-agnostic.

At runtime, the agent:

1. Reads the discovery index (`docs/project/dhf-manifest/<slug>-dhf-discovery.json`).
2. Looks up the resolved path for each Tier 1 role; reads them in full (slicing as needed for files exceeding the per-`Read` token cap).
3. Reads the user's question; picks relevant Tier 2 roles from the index; reads only those.
4. If Tier 1+2 don't yield a confident answer, invokes the researcher subagent via the `Agent` tool (Tier 3).

**Token-cost outcome** measured on the pilot: ~170 K eager tokens → ~20–70 K depending on whether the Tier 1 strategy doc is sliced or read whole. Cross-domain answers consistently land below 100 K combined (Tier 1 + Tier 2 + Tier 3).

### 5.2 Other consumers

Any skill that needs to locate canonical project artifacts can consume the index — for example, the project-console workflows surface "Create Draft" actions that resolve target-output paths from the index, and the tracker uses discovery resolutions to bind catalog rows to evidence paths.

---

## 6. Project-agnostic discipline — what NOT to put where

| Location | Allowed | Forbidden |
|---|---|---|
| `data/canonical-roles.yaml` (skill L1+L2) | Role names, scope semantics, ranked filename/glob patterns, per-mode folder names, consumer-advisor labels | Project names, device names, team-member names, hard-coded `docs/project/dhfs/<leaf>` paths |
| `scripts/discovery-index.py` (skill resolver) | Generic resolution logic; reads `project.yml` and L1+L2 registry only | Any project-specific path literal |
| `project.yml` (project, root) | `dhfs[]` roster, `evidence_layout.layers` overrides, `submissions[]`, scope vector | Skill conventions duplicated from L1+L2 |
| `<project>-dhf-discovery.json` (project, generated) | Project's resolved bindings | Nothing — fully regenerated |
| Advisor agent markdown (`.claude/skills/advisors/agents/*.md`) | Role names + selectors in `canonical_roles:`; abstract Tier 1/2/3 narrative | Project-specific paths or names |

The IoC chain only works if these boundaries are respected. CLAUDE.md's "skills/agents stay project-agnostic" HARD RULE applies to every file in this skill.

---

## 7. Audit findings (2026-05-12) — known role-catalog gaps

The v8 → v9 catalog expansion (43 roles, 13 multi-file) was driven by an audit against the full advisor fleet's needs. Known remaining gaps for future expansion:

- **Human-factors**: no `human_factors_file` role yet (use-related risk analysis, formative/summative studies, task analysis records). Adjacent to the existing `user_needs` role but distinct artifact family.
- **Quality engineering**: no roles for design-history-file index, design review records, traceability-matrix coverage reports. These are partially served by `software_requirements` + `hazard_traceability_matrix` but not directly catalogued.
- **External-mode multi-file**: the `multi_file: true` flag is not yet supported in `external` mode (taxonomy convention for multi-file artifact families not identified). Affects projects mirroring postmarket / clinical evidence from external systems.
- **Tool validation**: no role for `software-tools-validation` or `non-product-software-validation` artifacts (referenced in some taxonomies but absent from canonical-roles).

These are **data authoring** gaps — the schema mechanism supports them. Add as new entries to `data/canonical-roles.yaml` when a consuming agent surfaces the need.

---

## 8. Drift detection

`/best-practices` audit checks (see § 9) include drift signals between the discovery index, the obligation manifest, and the project filesystem. Two failure modes the audit watches for:

- **Stale discovery index**: a resolved path that no longer exists, or a file that exists but has moved. Agents falling back to "path missing" need to regenerate.
- **Non-empty `ambiguity_notes`**: the resolver picked one match where multiple were possible. Review surfaces whether the ranking is wrong or the project has redundant files.

Both are advisory, not blocking — the index is stale-tolerant because the agent's Tier 1 protocol includes a dynamic-globbing fallback if a path is missing.

---

## 9. Best Practices (audit checks)

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| `docs/project/dhf-manifest/` exists | Directory present | Required | shared |
| Tier 1 files present | `data/tier1-regulatory/*.md` count ≥ 1 | Required | shared |
| QMS manifest authored | `docs/project/dhf-manifest/qms-manifest.md` exists with ≥ 1 `<!-- QMS-DATA -->` block | Recommended | shared |
| QMS manifest JSON current | `qms-manifest.json` mtime ≥ `qms-manifest.md` mtime | Recommended | shared |
| DHF manifests current | `docs/project/dhf-manifest/<project>-dhf-manifest.{md,json}` mtime ≥ `qms-manifest.json` mtime | Recommended | shared |
| Validate clean | `scripts/validate.py` exits 0 | Required | shared |
| Unbound obligation coverage | Load `<project>-dhf-manifest.json`; compute `status=GAP` count. If ≥ 80% GAP, emit INFO (expected early-stage). If 0% bound AND qms-manifest.md has real content (>5 blocks), emit WARN — obligations present but no artifacts located | Info/Warn | shared |
| No orphan DHF artifacts | For each file path recorded as `location` in `<project>-dhf-manifest.json` (non-null entries), verify the path exists on disk. Report missing paths as WARN per entry | Recommended | shared |
| Manifest ↔ reference drift | Check `<project>-dhf-manifest.json` mtime against `data/tier3-reference/reference-dhf.yml` mtime. If reference-dhf is newer than the manifest, emit WARN: "DHF manifest is older than Reference DHF — run `/dhf-manifest build-manifest` to reproject." | Recommended | shared |
| Discovery index current | `<project>-dhf-discovery.json` exists and is not older than `data/canonical-roles.yaml` | Recommended | shared |
| Discovery index — non-informational gaps | Load `<project>-dhf-discovery.json`; count `gaps[]` where `informational != true`. If ≥ 1, emit INFO with role + DHF context — these are real authoring gaps worth fixing | Info | shared |
| Discovery index — ambiguity notes | Load `<project>-dhf-discovery.json`; count `ambiguity_notes[]`. If ≥ 1, emit INFO listing each — reviewer should confirm the resolver picked correctly | Info | shared |

---

## Changelog

- 9 (2026-05-12): **Catalog expansion (43 roles total) + `multi_file: true` flag.** Schema gains `multi_file: true` for project-scoped and per-dhf-scoped folder pointers; resolver emits `{folder, exists, file_count, patterns_used}` for these (same shape as `external_data` roles). 27 new roles added covering clinical (clinical_evaluation_plan/report, benefit_risk_analysis, literature_search, pmcf_plan, pmcf_studies), postmarket (complaints, capa, adverse_events, field_safety_corrective_actions, psur), cybersecurity (threat_model, sbom, cybersecurity_plan, vulnerability_management), risk-management additions (fmea, risk_management_report), design-controls additions (user_needs, software_requirements, software_design_specification, verification_plan, verification_protocols, verification_reports), and project-scoped input-analysis subfolders (kol_feedback, market_research, competitive_landscape, filing_strategy). Per-DHF external-mode multi-file is deferred. README.md rewritten with full Design & Architecture section consolidating pipeline architecture, IoC model, resolution algorithm, and project-agnostic discipline. Fixture tests expanded 23 → 36 (added cases 7 + 8 for project-scoped and per-DHF multi-file). (task ben/191 Phase 6)
- 8 (2026-05-12): **New `discovery-index` action for advisor-agent grounding.** Resolves canonical document roles (system_architecture, regulatory_strategy, architecture_strategy, risk_management_plan, software_risk_assessment, hazard_traceability_matrix, predicate_analysis, submission_package, fda_guidance, standards, industry_frameworks, etc.) to project file paths via a three-level registry pattern: L1 canonical role names + L2 ranked alternative pattern conventions live in the skill at `data/canonical-roles.yaml`; L3 resolved bindings emit to `<project>-dhf-discovery.json` plus optional durable overrides in `project.yml evidence_layout.layers[role].{patterns_extra, patterns_exclude, folder_override}`. Handles both `dhf_organization: internal` and `external` DHFs; external mode reads the DHF's `taxonomy_path` and supports both nested (`<folder>/v*.md` + `<folder>/index.md`) and flat (`<folder>.md`) sub-conventions. Ambiguity rule: highest-ranked pattern with exactly-one match wins, alternatives recorded in `ambiguity_notes[]`. Designed for advisor-agent eager-Context-tier reduction (target: ~170K → ~60K tokens on the pilot regulatory-affairs agent). 23 fixture tests pass (`tests/test_discovery_index.sh`); validated against a real 4-DHF project mixing both organizational modes. **Post-update:** Projects pulling this version can run `/dhf-manifest discovery-index` to bootstrap the index — no role-specific authoring required in `project.yml` for the common case. Consumer skills (advisor agents) read the index from `docs/project/dhf-manifest/<slug>-dhf-discovery.json`. New scripts: `scripts/discovery-index.py`, `data/canonical-roles.yaml`, `tests/test_discovery_index.sh`, `actions/discovery-index.md`. (Originated in arthrex-pccp task ben/191.)
- 6 (2026-04-27): **Output filenames parameterized from `project.yml` `project.name`.** The four built artifacts (`-dhf-manifest.{md,json}`, `-dhf-by-section.md`, `-dhf-dashboard.md`) are now prefixed with a project-specific slug derived from `project.name` (slugified — see `scripts/_project_slug.py`), with optional `dhf_manifest.output_prefix` override. Examples: `PDLC_DEMO` → `pdlc-demo-dhf-manifest.md`; `Arthrex PCCP` → `arthrex-pccp-dhf-manifest.md`. The hardcoded leaf-name branch in `build-manifest.py` (`if leaf == "hiplink-intra-op":`) is replaced with a project-supplied `dhfs[].classification.subtitle_extra` field — projects supply their own per-DHF descriptors. New `## Output filename derivation` section in SKILL.md documents the resolution order. **Post-update:** Existing projects rerun `/dhf-manifest build-manifest` after pull to regenerate to the new filenames; old `hiplink-*` outputs remain on disk and can be deleted by the project owner. Projects that previously relied on `if leaf == "hiplink-intra-op":` getting the "tablet / offline-capable" descriptor must add `subtitle_extra: "tablet / offline-capable"` to that DHF's `classification` block. (PDLC_DEMO ben/033)
- 5 (2026-04-24): **Title field + hyperlinked `ID · Title` rendering everywhere.** Schema gained required `title` field on all 114 Tier 1 obligations + all 115 QMS records. New `scripts/_linking.py` shared helper exports `render_obl_link` / `render_qms_link` / `find_bare_ids` / `is_valid_title` (canonical shape: `[\`OBL-XXX\` · Title](src.md#OBL-XXX)` — middle-dot separator, backtick-wrapped ID, clickable label). All three builders (`build-reference.py`, `build-manifest.py`, `build-qms.py`) emit linked labels across master table + 11 dimension tables + <project>-dhf-manifest.md + <project>-dhf-by-section.md + qms-manifest.md. `validate.py` gains strict title quality check (non-empty, ≤ 60 chars, no pipe char, no markdown syntax) — 12/12 passed. `build-manifest.py` + `build-qms.py` run post-build bare-ID grep (exit 2 / exit 4) on rendered output to enforce every ID is inside a clickable link. `agents/dhf-distiller.md` + `actions/distill.md` updated so new QMS records carry titles from birth, with worked-example table (good vs bad titles). Three new applicator scripts: `apply-titles.py` (114 Tier 1 titles applied wholesale), `draft-qms-titles.py` (source-title-first heuristic with §-section/topic disambiguation), `apply-qms-titles.py` (115 QMS titles applied into `<!-- QMS-DATA -->` YAML blocks). (task ben/104)
- 4 (2026-04-24): Skill-side data layout restructured to mirror `medtech-docs/references/`: `data/tier1-regulatory/` → `data/{fda-guidance,standards,industry-frameworks}/`; aggregate flattened from `data/tier3-reference/` up to `data/` root. Each source MD now has a sibling JSON sidecar (built by `build-reference.py` — single-source programmatic primitive). Added 5 industry-framework stubs (AAMI TIR57, TIR45, SW96, IMDRF SaMD, GMLP) — empty shells with distill-backlog notes. `build-manifest.py`, `validate.py` updated to walk categories; Reg Source deep links now include category segment. Full pipeline re-ran: 11/11 validate PASS, 114 obligations, 19 sources (fda-guidance=8, standards=6, industry-frameworks=5 stubs), 251 routed Tier 4 entries. (task ben/069 session 6)
- 3 (2026-04-24): Flattened project-side layout (no tier-prefix folders); Tier 2 consolidated into single hand-authored `qms-manifest.md` with hidden `<!-- QMS-DATA -->` blocks + built `qms-manifest.json` sidecar; `<project>-dhf-manifest.md` enriched with `Reg Source` (deep-linked to Tier 1 anchors) and `QMS Grounding` (direct QMS-IDs or topic fallback) columns; new `<project>-dhf-by-section.md` (View 2 — topic-first) and `<project>-dhf-dashboard.md` (View 3 — status/coverage); `gap-report.md` retired. Best-practice checks updated for new paths. New `build-qms` + `dashboard` actions. (task ben/069)
- 2 (2026-04-21): Added 3 new best-practice checks: unbound coverage (GAP % threshold), orphan artifact detection (stale location bindings), Tier 4↔disk drift (manifest older than reference-dhf). (task ben/069)
- 1 (2026-04-21): Initial scaffold. SKILL.md slimmed to router; implementation detail moved to actions/. 4-tier model, project.yml as scope source. (task ben/069)
