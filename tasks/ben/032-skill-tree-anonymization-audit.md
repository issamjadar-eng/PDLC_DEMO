# 032 — Skill Tree Anonymization Audit (remove product/customer references)

**ID**: 032
**Created**: 2026-04-27
**Status**: Not Started
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. Update at every meaningful checkpoint (HARD RULE).
2. Phase-end batching is OK; drift-batching is not.
3. A commit is not a substitute.
4. Resume-ready before any session boundary.
5. Capture strategy + lessons as they happen.

## Goals

The skill tree under `.claude/skills/` (and the registry at `hitachi/skills/`) must be **reusable by any project / company**. Skills have leaked project- and customer-specific language — most visibly in `dhf-manifest`, but other skills are suspect too. This task audits the whole skill tree and the agents tree, removes specific names, and replaces them with **anonymized descriptors** that preserve enough context to be useful but never name a real company, product, or customer.

Anonymization rule of thumb (from user):
- ❌ "HipLink" → ✅ "a digital surgery project"
- ❌ "Arthrex" / "GlobalLogic" → ✅ "a sister project" or "an example deployment" or "the originating project" — never the company name
- ❌ "PainEase PCA Advanced" / "PP3500" → ✅ "an infusion pump" or "the example device"
- Even **history/changelog entries** must be sanitized — git history is fine to retain SHAs and dates, but human-readable text should be neutral.

Out-of-scope (these may keep their real names — they're project-local, not skill-local):
- `tasks/` (project-local task docs)
- `docs/` (project-local content)
- `project.yml` (project identity by definition)
- `CLAUDE.md`, `.claude/sync-log.md`, `.claude/MEMORY.md` (project-local meta)

In-scope:
- `.claude/skills/**` (every file: `SKILL.md`, `README.md`, `actions/*.md`, `templates/*`, `references/**`, `scripts/*`, `data/**`)
- `.claude/agents/**` (every agent definition file)
- The same trees on the registry side (`../hitachi/skills/**`, `../hitachi/agents/**`) — fixes pushed back upstream.

## Todos

### Phase 1 — Survey (read-only) — COMPLETE 2026-04-27

- [x] Grep the local skill tree for likely offenders. Anchor terms (case-insensitive): `arthrex`, `globallogic`, `hitachi` (NB: registry repo name; only flag prose hits, not config), `painease`, `pp3500`, `pp3000`, `ip5000`, `sp6000`, `sp6500`, `hiplink`, `pdlc[_-]?demo`, `arthrex-pccp`. Search across `.claude/skills/`, `.claude/agents/`. Hitachi-side paths will be touched as part of Phase 3 (per-skill PR).
- [x] Catalog each hit. **200 lines flagged across 11 skills.** Full hit list saved at `/home/benxavier/.claude/projects/-home-benxavier-project-PDLC-DEMO/d61a7377-63ca-469c-b04a-6d75996cbb50/tool-results/bgbvpziae.txt`. Per-skill counts and high-leverage examples in the Findings section below.
- [x] Triage. Three categories surfaced: (a) prose leaks — must replace; (b) structural leaks — `hiplink-` is hardcoded in script output filenames, requires rename + parameterization; (c) `data/` Context-section leaks — 112 of 147 dhf-manifest hits are HipLink-specific applicability commentary and need a scope decision (see below).
- [x] Draft canonical replacement glossary — see Findings.
  | Real term | Neutral replacement |
  |---|---|
  | Arthrex | "a sister project" / "another deployment" |
  | Arthrex PCCP | "the originating PCCP example project" |
  | GlobalLogic | "the parent company" or "the QMS owner" |
  | hitachi (registry) | "the skill registry" (in prose; keep literal in config + scripts) |
  | PainEase PCA Advanced / PP3500 | "the example infusion pump" |
  | HipLink | "a digital surgery project" |
  | PDLC_DEMO | "this demo project" / "a sample project" |
  Adjust during Phase 1 as findings come in.

### Phase 2 — Targeted fixes (write) — COMPLETE 2026-04-27 (89 files changed)

Substitutions applied via `/tmp/anonymize.py` (ordered, longest-pattern-first; registry URL protected; programmatic filename prefixes preserved). Built artifacts (`data/reference-dhf.yml`, `data/*/*.json`) regenerated from now-anonymized sources via `scripts/build-reference.py`.

- [x] `dhf-manifest` (highest priority) — SKILL.md, README.md, actions/{build,init,distill,inspect}.md, agents/dhf-distiller.md, templates/tier2-topic.md.tmpl, scripts/{build-qms,gap-report,dashboard}.py prose, all 30 files in data/{standards,fda-guidance,industry-frameworks}/, plus reference-dhf.yml + 19 JSON sidecars regenerated
- [x] `medtech-docs` — SKILL.md (DEVICE_FAMILY example list, add-dhf example commands)
- [x] `project-console` — SKILL.md (theme-scrape examples), README.md (changelog/sister-project mentions), console/{trace_matrix/{router,loader},documents/summary,assistant/router,workflows/b1_doc_roundtrip}.py, console/web/templates/_assistant_drawer.html
- [x] `docflow` — SKILL.md, README.md, agents/{adopter,converter,structure_body,structure_requirement_body}.md, references/{doc-type-packs,mermaid-rule-packs}/*.md, templates/frontmatter-project.md, scripts/{validate_phase7,extract_title_version,infer_requirement_metadata}.py
- [x] `change-control` — README.md, SKILL.md, actions/status.py docstring, lib/frontmatter.py docstring, templates/change-control.example.yml
- [x] `best-practices` — SKILL.md (registry-default prose, cost-envelope examples, path examples)
- [x] `strategy` — SKILL.md, README.md (changelog references)
- [x] `sync-skills` — SKILL.md (commit-message + branch-name examples)
- [x] `digest` — README.md (changelog migration note)
- [x] `web-control` — README.md (origin-story note about parent-org workspace policy)
- [x] `trace-matrix` — SKILL.md (changelog validation note)
- [x] `secops` — scripts/resolve_user.py (also fixed in `shared/scripts/resolve_user.py` duplicate)
- [x] `advisors` — SKILL.md line 1 absolute-path header replaced with `${CLAUDE_SKILL_DIR}` token (matches `web-control`/`change-control`/`secops` canonical form)
- [x] `agents/` (top-level project-secops, etc.) — clean per Phase 1 grep, no edits needed

Skills with no hits and not touched: `task`, `tracker`, `skill-creator`, `lessons`, `pdf`, `xlsx`, `pptx`, `docx`, `update-config`, `keybindings-help`, `simplify`, `fewer-permission-prompts`, `loop`, `schedule`, `claude-api`.

### Phase 3 — Push upstream

- [ ] One PR per skill (or one bundled PR if total churn is small) to the hitachi registry. Title pattern: `<skill>: anonymize project/customer references`. Body links back to this task and lists the anonymization mapping used.
- [ ] After merge, fast-forward local hitachi checkout. Re-run `/sync-skills check` and confirm zero `UPSTREAM_NEWER` rows for the touched skills.
- [ ] Spot-check arthrex-pccp post-merge: their next `/sync-skills pull` will pick the cleanup up; we don't need to push from there.

### Phase 4 — Guard rails

- [ ] Add a check to `best-practices` (or a new `skill-creator` rule) that greps skill content for the anonymization vocabulary and FAILs on hits. Severity: Required. Reason: prevent regression — the next time someone authors content inside a skill while looking at a real project, the lint catches the leak.
- [ ] Document the anonymization rule in `skill-creator` SKILL.md so it's load-bearing for any new skill.

## Notes

- **HARD CONSTRAINT — prose only, must not break functionality (added 2026-04-27).** This audit is strictly about administrative documentation, comments, changelog/history prose, agent-instruction text, and **example/illustrative text** inside templates and SKILL.md. We do **NOT** touch:
  - Source code (`*.py`) string literals that drive program behavior — output filenames, dictionary keys, regex patterns, file-existence checks, etc.
  - JSON/YAML *keys* or *structure*. JSON/YAML *string values* are touchable only if they are clearly prose-rendered (e.g., a `description:` field in a frontmatter, a "Context" field that is rendered into markdown). Anything that looks like an identifier, route, schema enum, or filename — leave alone.
  - Hook scripts, registration commands, registry URLs, file paths the skill resolves at runtime.
  - Anything where the change could plausibly affect: a `/sync-skills check` diff against a consumer project, a `/skill setup` re-run, a build script's output, or a downstream parser.
- **If a leak appears in something programmatic, RAISE it.** Add it to the "Raised — programmatic, not touched" subsection of the Findings, with the reason and the safer alternative (e.g., "rename via parameterization in a follow-up task — out of scope for ben/032 prose pass"). Do not silently leave it; do not silently change it.
- **Do not rewrite git history.** Commit history retains the original prose; we only sanitize current file contents. SHAs in changelog entries stay accurate.
- Configuration paths and program names that are intrinsically project-shaped (e.g., `local_path: ../hitachi` in `sync-skills/SKILL.md`) are not leaks — `hitachi` is the registry repo name and changing it would break the script. Keep literal strings in config; change only descriptive prose.
- The `dhf-manifest/data/` tree contains canonical regulatory references (FDA guidance, standards, frameworks). Those names are not leaks — FDA / ISO / IEC are public regulatory bodies. Only flag content that names commercial products / customers.

## Findings (Phase 1 — survey complete 2026-04-27)

### Hit summary (200 lines flagged, 11 skills + 0 agents under `.claude/agents/`)

| Skill | Hits | Severity |
|---|---:|---|
| `dhf-manifest` | 147 | **Critical — structural** |
| `change-control` | 15 | High — example/template |
| `medtech-docs` | 11 | High — examples in `add-dhf` worked examples + registry refs |
| `docflow` | 10 | High — adopter agent burns "Arthrex" / "HipLink" into agent prompts |
| `best-practices` | 7 | Medium — hardcoded registry default + cost-envelope prose |
| `strategy` | 4 | Medium — examples in SKILL.md and README changelog |
| `digest` | 2 | Low — README changelog |
| `web-control` | 1 | Low — README "Origin story" |
| `trace-matrix` | 1 | Low — SKILL.md changelog |
| `secops` | 1 | Low — script docstring |
| `advisors` | 1 | **Critical — wrong base path** (`/Users/ben.xavier/.../arthrex/pccp/.claude/skills/advisors`) |
| `agents/` (project-secops, etc.) | 0 | Clean (per grep) |

### Structural finding (raise scope decision before Phase 2)

`dhf-manifest` is more than a prose problem. It has **three structural leaks**:

1. **Output filenames hardcoded as `hiplink-`.** `scripts/build-manifest.py` writes `hiplink-manifest.{md,json}`, `hiplink-by-section.md`, and `hiplink-dashboard.md`. The action docs (`actions/build.md`, `actions/inspect.md`) reference these names verbatim. README best-practice checks grep for them. Fix requires renaming the outputs (e.g., `dhf-manifest.{md,json}`, or parameterize from `project.yml` `device_family`).
2. **Templates name "Arthrex" as the QMS owner.** `templates/tier2-topic.md.tmpl` says `**Sources**: <list of Arthrex SOPs/WIs/POLs/FORMs scanned>` and `Each record must cite an actual Arthrex source doc`.
3. **`data/` "Context" sections are project-specific commentary.** 112 of the 147 dhf-manifest hits live in `data/standards/*.md`, `data/fda-guidance/*.md`, and the matching `*.json` files. These were authored as HipLink applicability commentary — *not* generic standards summaries. Sample lines: "For HipLink, the UEP covers all three SaMD modules — Pre-Op, Intra-Op, and Management Services" (iec-62366.md:34); "HipLink Pre-Op FAILS criterion 1: it processes CT/MRI images for anatomy segmentation" (fda-cds.json:29). This makes the skill data fundamentally non-portable.

### Replacement glossary (LOCKED 2026-04-27 — user confirmed)

| Real term | Replacement |
|---|---|
| Arthrex (when used as **organization**) | `MedTech Company` |
| GlobalLogic (when used as **organization**) | `MedTech Company` |
| HipLink (project name) | `MedTech Project` |
| Arthrex PCCP / arthrex-pccp (project name) | `MedTech Project` |
| PDLC_DEMO / PDLC-DEMO (project name) | `MedTech Project` |
| HipLink Pre-Op | `MFD A` |
| HipLink Intra-Op | `MFD B` |
| HipLink Management Services | `MFD C` |
| `hiplink-` filename prefix (in scripts/output) | `dhf-manifest-` (registry default; parameterized via `project.yml` if needed) |
| PainEase PCA Advanced / PP3500 / PP3000 / IP5000 / SP6000 / SP6500 | "the example device" — drop the model number if not load-bearing |
| `submissions/510k-pp3500/` (path examples) | `submissions/510k-<device>/` |
| `GlobalLogic-a-Hitachi-Company/hitachi` in **prose** | "the skill registry" |
| `GlobalLogic-a-Hitachi-Company/hitachi` in **code / config defaults** | **leave literal** — load-bearing config string |
| `tasks/<person>/<NNN>` references (e.g. `ben/056`) in changelogs | **leave as-is** — person+number reference, not company |
| FDA / ISO / IEC / AAMI / IMDRF / GMLP / MDCG | leave as-is — public regulatory bodies |

**Scope decision for `data/` Context sections (112 lines):** **Option B — genericize in place.** Replace HipLink-specific examples with `MedTech Project` / `MFD A/B/C` so the applicability commentary still teaches the standard's intent without binding to one product.

**Disambiguation rule:** when a source phrase like "Arthrex" appears in a path slug or repo URL (e.g., `../arthrex-pccp/`), treat it as a project reference → `MedTech Project`. When it appears as a possessive describing process ownership ("Arthrex's QMS", "Arthrex SOPs") it's an organization reference → `MedTech Company`'s QMS / `MedTech Company` SOPs.

### High-leverage examples (one per category)

- **Filename leak (structural):** `.claude/skills/dhf-manifest/scripts/build-manifest.py:768` — `(OUTPUT_DIR / "hiplink-manifest.md").write_text(md_content)`
- **Template leak:** `.claude/skills/dhf-manifest/templates/tier2-topic.md.tmpl:4` — `**Sources**: <list of Arthrex SOPs/WIs/POLs/FORMs scanned>`
- **Agent prompt leak:** `.claude/skills/dhf-manifest/agents/dhf-distiller.md:13` — `you read one or more Arthrex source-md QMS documents`
- **Data body leak:** `.claude/skills/dhf-manifest/data/standards/iec-62366.md:34` — `For HipLink, the UEP covers all three SaMD modules — Pre-Op, Intra-Op, and Management Services...`
- **Cross-skill prose leak (changelog):** `.claude/skills/medtech-docs/SKILL.md:208` — `Examples: hiplink, synergy, vip`
- **Wrong-path leak:** `.claude/skills/advisors/SKILL.md:1` — `Base directory for this skill: /Users/ben.xavier/Documents/projects/arthrex/pccp/.claude/skills/advisors` (this is broken on PDLC_DEMO too — it points at a path that doesn't exist here)
- **Example/sample data leak:** `.claude/skills/change-control/templates/change-control.example.yml:21` — `space_key: PP3500`
- **Adopter-agent burn-in:** `.claude/skills/docflow/agents/adopter.md:108` — `TITLE_STEM = sanitized title (e.g. "HipLink Web - Software Development Plan (SDP) - 1.0.0")`
- **Resolved-config docstring:** `.claude/skills/secops/scripts/resolve_user.py:41` — `project.yml used across PDLC_DEMO + Arthrex PCCP`

### Out-of-scope confirmations (no replacement needed)

- `GlobalLogic-a-Hitachi-Company/hitachi` literal in scripts/config — registry repo URL, real and load-bearing.
- `tasks/ben/...` references inside skill changelogs — task IDs are project-local but currently part of the changelog convention. **Open question**: do we strip these or anonymize to `tasks/<person>/<NNN>`? Recommendation: keep `ben/NNN` as it's a person+number reference, not a company reference, and the convention is documented. Confirm with user.
- FDA / ISO / IEC / AAMI / IMDRF / GMLP / MDCG names in `dhf-manifest/data/` — these are public regulatory bodies; not leaks.
- `arthrex/pccp/.claude/skills/advisors` in `advisors/SKILL.md:1` — this is wrong on its own merits (broken absolute path) and will be fixed regardless.

### Scope decision (LOCKED 2026-04-27)

User selected **Option B — genericize in place** for the 112 Context-section lines in `dhf-manifest/data/`. Use the locked glossary (HipLink → `MedTech Project`; Pre-Op/Intra-Op/Mgmt Services → `MFD A/B/C`).

### Raised — programmatic, NOT touched in this task (decide separately)

Per the prose-only constraint, the following items are leaks but **cannot** be safely changed in a documentation pass. Each gets raised here for a separate decision:

1. **`scripts/build-manifest.py` writes `hiplink-manifest.{md,json}`, `hiplink-by-section.md`, `hiplink-dashboard.md`** (lines 365, 553–556, 746–770). These string literals drive output filenames; renaming them silently breaks every downstream consumer (the `dhf-manifest` README's best-practice checks grep for these filenames; `tracker` skill plans to read the `hiplink-manifest.json` per `actions/inspect.md:90`). **Recommendation:** open a follow-up task (`ben/033 — dhf-manifest output filename parameterization`) that renames to `dhf-manifest-*` registry-default and adds an opt-in `output_prefix` knob in `project.yml`, with a coordinated rename across consumers and a one-line migration in the registry changelog.
2. **`scripts/build-manifest.py:365` — `if leaf == "hiplink-intra-op":`** — a hardcoded branch matching a DHF leaf name. Same follow-up task; depending on what this branch does, may need to be replaced with a project-config-driven flag rather than a string compare.
3. **JSON values that are rendered into markdown but are also keyed structures** — e.g., `data/fda-guidance/fda-cds.json:29` has `"HipLink Pre-Op FAILS criterion 1": "..."` where `HipLink Pre-Op FAILS criterion 1` is a JSON **key** that gets rendered as a heading in the build pipeline. Changing this key changes the rendered output and may break any test or grep that asserts on the heading text. **Decision:** confirm with grep whether anything programmatic asserts on the key strings; if not, the keys are effectively prose and can be genericized in this task. If anything does, raise the specific keys here and defer.
4. **Best-practice grep checks in `dhf-manifest/README.md:15–19`** that check for `hiplink-manifest.json` mtime and existence — these are documented checks, not code, but the `/best-practices` skill subagents may execute them as instructed. Changing the prose without changing the underlying filename in (1) would create a check that doesn't match the actual filename. **Decision:** these stay tied to the (1) decision — touch both together, or neither.
5. **`change-control/templates/change-control.example.yml`** has `space_key: PP3500`, `project_key: PP3500`, `target_space: PP3500` (lines 21, 37, 59, 63, 67). These are illustrative example values, not consumed by skill code (`change-control` actions are stubs at present). **Likely safe** to genericize as prose, but verify by grepping `change-control/{actions,lib}/**/*.py` for any literal `"PP3500"` reference before edits. Raise here if any consumer is found.
6. **`advisors/SKILL.md:1` "Base directory for this skill: /Users/.../arthrex/pccp/.claude/skills/advisors"** — this looks like an auto-generated header line. Need to find what writes this string; if a skill bootstrapper regenerates it on next run, fixing it manually only papers over the source. **Decision:** locate the generator first; if regenerated, the fix belongs in the generator (probably out of scope here). If hand-authored, fix in this task.

## Changelog

- 2026-04-27: Task created. Triggered by user observation that `dhf-manifest` carries product/customer references; agreed audit must cover the whole skill + agent tree, sanitize history-prose too, and push upstream so arthrex-pccp inherits the cleanup. Out-of-scope: project-local trees (`tasks/`, `docs/`, `project.yml`, `CLAUDE.md`).
- 2026-04-27: Phase 1 survey complete. 200 lines flagged across 11 skills (147 in dhf-manifest alone). Three structural problems surfaced in dhf-manifest: hardcoded `hiplink-*` output filenames in scripts, "Arthrex SOPs/WIs/POLs/FORMs" in templates, and 112 HipLink-specific Context sections in `data/` reference docs. Glossary drafted, scope decision raised.
- 2026-04-27: User locked the simplified glossary (Arthrex/GlobalLogic → MedTech Company; HipLink/Arthrex PCCP/PDLC_DEMO → MedTech Project; HipLink Pre-Op/Intra-Op/Mgmt Services → MFD A/B/C; rest as recommended) and selected Option B (genericize Context sections in place). Added a hard prose-only constraint: never touch programmatic strings; raise instead.
- 2026-04-27: Phase 2 prose pass complete. 89 files changed via ordered substitution script. Six items raised as programmatic-and-not-touched: dhf-manifest output filenames + leaf-name branch (deferred to ben/033), JSON keys with embedded HipLink (verified safe + genericized), README best-practice grep checks (coupled to ben/033), change-control example YAML (verified docstring-only), advisors header (fixed to `${CLAUDE_SKILL_DIR}` tokenized form, matching peer skills). Built artifacts (`data/reference-dhf.yml`, `data/*/*.json`) regenerated via `build-reference.py` to project the anonymized sources.
- 2026-04-27: Phase 3 (push to hitachi) and Phase 4 (best-practices regression lint) still to execute.
