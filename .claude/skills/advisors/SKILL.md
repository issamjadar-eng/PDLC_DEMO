Base directory for this skill: `${CLAUDE_SKILL_DIR}`

# Advisors — Persona Subagents for Medtech Projects

Manage a bundle of persona advisors (Regulatory Affairs, Clinical Affairs, Risk Management, etc.) that serve two runtimes from one source:

1. **Claude Code main thread** — delegate strategy questions to a grounded, cited subagent via `Agent(subagent_type: "<name>", prompt: ...)`.
2. **project-console FastAPI app** — chat with the same advisors in a browser UI with the same grounding.

Usage: `/advisors <action> [arguments]`

> **Naming note:** internal skill code name is `advisors` to avoid overloading the word "assistant" inside Claude Code. User-facing copy in the project-console calls them **"Assistants"** via each agent's `console.title` field. Same agents, two labels.

## Grounding model

Every advisor's frontmatter declares **how** it grounds itself. There are two grounding modes the loader + renderer understand. **Canonical-role is the default and the one to use for any new advisor.** Literal-glob is kept as a parsing fallback for downstream project forks that haven't migrated yet.

Agent bodies stay **device-agnostic** in either mode — no project-specific names appear in registry-shipped agent files. Project-specific resolution happens via either the per-project discovery index (canonical-role mode) or `project.yml` overlay globs (literal-glob mode).

### Canonical-role mode (default — v1.2.0+)

Each advisor declares grounding via a `console.canonical_roles:` frontmatter block referring to roles in the sibling `/dhf-manifest` skill's catalog (`data/canonical-roles.yaml`). At runtime, the agent reads the per-project discovery index (`docs/project/dhf-manifest/<slug>-dhf-discovery.json`) to resolve role names → concrete file paths.

Three-tier reading discipline:

| Tier | What it is | Author-time picks |
|------|-----------|-------------------|
| **tier_1** | Required reading. Read in full on every invocation. | 2–3 foundational roles. Typically: the discipline's primary strategy doc + `architecture_strategy` + `system_architecture` for the system DHF (selector: `dhfs: {role: system}`). Keep total Tier 1 budget under ~80 K tokens. |
| **tier_2** | Index-triaged per question. Read only the subset the question touches. | All other roles relevant to the discipline. Find them by matching the agent name against each role's `consumers:` field in `dhf-manifest/data/canonical-roles.yaml`. |
| **tier_3** | Independent search via the `advisor-researcher` helper subagent. Fires only when Tier 1 + Tier 2 leave the answer thin. | `tier_3.researcher: advisor-researcher`. |

Selectors narrow scope inline: `dhfs: {role: system}`, `dhfs: {role: item}`, `submissions: all`. See `agents/regulatory-affairs.md` for a worked example.

**Tier 3 requires `Agent` in the agent's `tools:` frontmatter line.** Every solo advisor that declares a `tier_3.researcher` must list `Agent` alongside `Read, Glob, Grep, WebFetch`. The renderer does not enforce this; missing `Agent` produces a silent runtime failure where the agent can't fire Tier 3.

**Nested-subagent caveat (platform limitation).** When an advisor is invoked as a *nested* subagent (e.g., from another `Agent` call inside a Claude Code session), Claude Code disables the `Agent` tool to prevent subagent-to-subagent recursion. The agent body instructs the advisor to self-substitute the researcher's Read/Glob/Grep workflow inline in that case. In normal top-level invocation (project-console, `/console`, direct user request), Tier 3 fires as designed.

**Authoring a new advisor (canonical-role).** (a) Draft the agent file with `tools: Read, Glob, Grep, WebFetch, Agent` and a `console.canonical_roles:` block — copy from `regulatory-affairs.md`. (b) For tier_1 pick 2–3 foundational roles per the table above. (c) For tier_2 grep `consumers:` in `dhf-manifest/data/canonical-roles.yaml` for the agent's name and pick the matches. (d) Set `tier_3.researcher: advisor-researcher` unless the discipline truly never needs independent search. (e) Run `/advisors sync` to regenerate the body. (f) If a needed role is missing from the canonical catalog, the gap belongs in `/dhf-manifest` (extend `canonical-roles.yaml`) — never paper over it with literal globs.

### Literal-glob mode (legacy)

Original mode shipped in v1.0–v1.1. Frontmatter declares grounding as literal glob patterns:

| Field | What it is |
|------|------------|
| `console.context:` | Always-read foundational paths (globs). |
| `console.sources:` | Per-question triage paths (globs). |
| `project.yml advisors.overlays.<name>.{add,exclude}` | Project-specific glob overrides, merged at load time. |

Resolution: agent-file baseline (`context` + `sources`) → `project.yml` overlay (`add`/`exclude` filters).

**Status:** all bundled advisors in this registry migrated to canonical-role mode in v1.2.0+. Literal-glob mode is retained as a parser fallback for: (a) project forks of `.claude/agents/<name>.md` that haven't migrated; (b) downstream projects pulling older bundles. Do not author new advisors in literal-glob mode — extend `canonical-roles.yaml` instead if a needed role is missing.

## Dependencies

| File / Tool | Required by | Purpose |
|-------------|-------------|---------|
| `.claude/agents/` dir | `init`, `add`, `remove`, `sync` | CC's subagent discovery directory — the installed home of each advisor |
| `project.yml` | `init`, `overlay`, `list`, `sync` | Overlay storage and enabled-advisors curation list |
| `uv` (CLI) | `sync`, `render-grounding.py` | Python runner for the grounding renderer (PEP 723 inline deps) |

## Supporting files

| File | Purpose |
|------|---------|
| `agents/*.md` | Bundled advisor agent files (CC-native frontmatter + `console:` extension block). Source of truth for every advisor the skill ships. Includes 11 domain advisors, 2 panels, and the `advisor-researcher` helper subagent. |
| `agents/advisor-researcher.md` | Helper subagent (Read/Glob/Grep only) invoked by domain advisors as the Tier 3 escape hatch when Tier 1 + Tier 2 grounding leaves the answer thin. No `console:` block — not user-facing; render-grounding skips it. |
| `overlay-defaults.yml` | Seed `advisors:` section written into `project.yml` on `init`. Carries literal-glob-mode `overlays` for backward compat; new agents use canonical-role mode and ignore this file. |
| `scripts/render-grounding.py` | CLI that regenerates the `<!-- BEGIN GROUNDING -->` block in each agent file from its frontmatter. Dispatches on grounding mode: canonical-role (reads role descriptions from `/dhf-manifest data/canonical-roles.yaml`) vs literal-glob (reads `context`/`sources` + project.yml overlay). Idempotent. PEP 723 inline deps (uv-managed). |
| `lib/loader.py` | Shared Python loader module: reads agent files, parses `console:` extension block (both `canonical_roles` and legacy `context`/`sources` shapes), applies project.yml overlays for literal-glob agents, returns `DomainAgent` objects. Consumed by both the skill's actions and project-console via symlink. |
| `lib/__init__.py` | Package init re-exporting the public API. |
| `tests/` | Unit tests for the loader, grounding renderer, and file-locator wiring. |
| `tests/run.sh` | Test runner — runs the suite under `pytest`, pulling `pytest` + `PyYAML` ephemerally via `uv run --no-project` (no repo-installed dev deps). Extra args pass through to `pytest`. |
| `README.md` | Design documentation for humans (not loaded by Claude). |

## Actions

Parse the user's argument string to determine which action to perform:

### `init`

Install the advisor bundle into this project and seed the overlay.

1. Create `.claude/agents/` if it doesn't exist.
2. For each `*.md` in the skill's `agents/` directory, install as a **symlink**: `.claude/agents/<name>.md` → `../skills/advisors/agents/<name>.md`. Rules:
   - If `.claude/agents/<name>.md` does not exist → create the symlink.
   - If it exists and is already a symlink pointing at the correct target → skip (idempotent).
   - If it exists and is a symlink pointing at a different target → replace it (stale link from a previous install).
   - If it exists and is a **regular file** → treat as a project fork. Do not overwrite. Report the fork so the user can either keep it or delete and re-run to re-symlink.
3. Read `project.yml`. If no `advisors:` section exists, merge the contents of `overlay-defaults.yml` into it. Preserve any existing customizations on re-run.
4. Run `bash -c ".claude/skills/advisors/scripts/render-grounding.py --all"` to ensure grounding blocks are fresh.
5. If `tools/project-console/console/` exists, run the `setup` action to create the loader symlink.
6. Report: which advisors were linked (new / already-correct / forks-preserved), where the overlay lives, next step ("run `/advisors list` to verify").

### `setup`

Wire the skill into any consumers. Idempotent.

1. Ensure `.claude/agents/` exists.
2. If `tools/project-console/console/` exists, create the symlink `tools/project-console/console/advisors_lib` → `../../../.claude/skills/advisors/lib` (skip if already correct).
3. Report what was done.

### `list`

Show installed advisors + their effective sources.

1. Load advisors via `lib.loader.load_all(Path(".claude/agents"), Path("project.yml"))`.
2. For each advisor in the returned dict, print: name, title (from `console.title`), group, kind, effective source count, and a one-line excerpt of `description`.
3. Group output by `console.group`.
4. Flag any advisor whose overlay globs match zero files (via a quick `glob()` against the repo root) as a warning.

### `add <name>`

Install a single advisor from the skill bundle.

1. Verify `agents/<name>.md` exists in the skill bundle. If not, list available advisors and stop.
2. Install as a symlink: `.claude/agents/<name>.md` → `../skills/advisors/agents/<name>.md`. Apply the same rules as `init` step 2 (skip if already correct; replace stale link; preserve regular-file forks).
3. Ensure an overlay stub for `<name>` exists in `project.yml.advisors.overlays` (empty `add: []` / `exclude: []`).
4. Ensure `<name>` is in `project.yml.advisors.enabled`.
5. Run `render-grounding.py --agent <name>`.
6. Report.

### `remove <name>`

Uninstall an advisor from this project.

1. Delete `.claude/agents/<name>.md`:
   - If it is a symlink into `skills/advisors/agents/` → remove the symlink.
   - If it is a regular file (project fork) → warn about local edits and require `--force` to remove.
2. Remove `<name>` from `project.yml.advisors.enabled` and `project.yml.advisors.overlays`.
3. Report.

### `overlay <name> <op> <glob>`

Manage project-specific overlay globs for one advisor.

- `overlay <name> add-source <glob>` — append a glob to `project.yml.advisors.overlays.<name>.add`
- `overlay <name> add-exclude <glob>` — append a glob to `...exclude`
- `overlay <name> remove-source <glob>` — remove from `...add`
- `overlay <name> remove-exclude <glob>` — remove from `...exclude`

After any mutation, re-run `render-grounding.py --agent <name>` so the agent's grounding block reflects the new effective sources.

### `sync`

Re-read overlays and regenerate all grounding blocks. Run after editing `project.yml` by hand or after pulling a skill update that changed universal sources.

1. Run `render-grounding.py --all`.
2. Report which files were updated, unchanged, or skipped (plain CC agents without frontmatter are skipped, not errors).

### `help`

Show this usage guide.

## For Claude

**When to delegate to an advisor vs. answer directly:**

Delegate to a subagent (via `Agent(subagent_type: "<name>", ...)`) when:
- The question falls squarely inside one advisor's scope (regulatory pathway, clinical strategy, risk analysis, etc.)
- The answer would benefit from reading 3–10 grounding files that the main thread hasn't loaded
- The user is explicitly asking for an advisor's perspective ("what would regulatory affairs say?")
- The research would balloon the main thread's context window

Answer directly when:
- The question is conversational, meta, or about project state
- You've already read the relevant files in this session
- The answer is a short factual lookup

**Caution — subagent discovery is session-scoped.** Claude Code reads `.claude/agents/` at session start. Newly installed advisors are not invocable until the user starts a fresh session. After running `/advisors init` or `/advisors add`, tell the user to restart their session to use the new advisors.

**When to run `/advisors sync`** — after editing `project.yml` overlays by hand, after pulling a skill update, or when `/best-practices` flags a grounding drift.

## Best Practices

<!-- Read by /best-practices skill to audit project setup -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill installed | `.claude/skills/advisors/SKILL.md` exists | Required | shared |
| Agents dir exists | `.claude/agents/` directory exists | Required | shared |
| Advisor agents installed as symlinks | For each advisor `<name>` in `project.yml.advisors.enabled`, `.claude/agents/<name>.md` is either a symlink into `.claude/skills/advisors/agents/` or a regular file explicitly documented as a fork in `.claude/sync-log.md`. Pairs with the skill-creator v2 symlink convention and the best-practices v10 audit. | Required | shared |
| At least one advisor enabled | `project.yml` has `advisors.enabled` with ≥1 entry | Recommended | shared |
| Overlay schema valid | Every entry in `project.yml.advisors.overlays` has `add` and `exclude` as lists | Required | shared |
| Grounding blocks in sync | `render-grounding.py --all --dry-run` exits 0 (no changes needed) | Recommended | shared |
| Console symlink (if console installed) | If `tools/project-console/console/` exists, `tools/project-console/console/advisors_lib` is a symlink to `.claude/skills/advisors/lib` | Recommended | shared |
| Agent bodies device-agnostic | No device-specific names in bundled `agents/*.md` persona prose (use overlays for device context) | Recommended | shared |

## Changelog

- 1.5.1 (2026-05-29): **Step 8 explicit Mode-A / Mode-B fallback.** `render-grounding.py` Step 8 ("Citation verification pass") is now split into two named modes: **Mode A — `citations` advisor dispatch** (used when the `Agent` tool is in the agent's runtime toolset) and **Mode B — Inline verification fallback** (REQUIRED when `Agent` is not in the toolset because Claude Code's runtime strips it from subagent invocations as a recursion guard, regardless of frontmatter declarations). Mode B instructs explicit step-by-step inline verification: `Read` the L1a registry distillation file → `Read` the L1b project applicability file → compare the cited claim's predicate against both → verdict band per same semantics as the citations advisor itself (predicate match = `sound`; same clause number, different topic = `broken, stale-citation`; source silent / paywalled = `unverified`). Both modes feed the same `sound | unverified | broken` verdict semantics, and both must cite L1a + L1b transparently per the existing Hard Rule. **Why this matters:** ben/204 Phase D validation confirmed that SMEs invoked as subagents from another agent's `Agent` call have `Agent` stripped from their toolset, making Mode A unreachable — but all three sampled SMEs honored the cite-both Hard Rule and successfully performed inline verification, surfacing 3 real defects. Making Mode B explicit removes interpretation risk for the SME and signals that the runtime restriction is platform-level (not a configuration we can override). (task ben/204)
- 1.5.0 (2026-05-29): **Cite-both Hard Rule + citations-advisor invocation step + AI-friendly federal endpoints guidance.** `render-grounding.py` template gains three additions to the canonical-role-mode GROUNDING block: (1) new Hard Rule "Cite both layers for external citations" requiring footnote citation of BOTH the L1a registry distillation (`.claude/skills/medtech-docs/references/<category>/`) AND the L1b project applicability (`docs/external/<category>/`) for any external citation — the registry distillation carries authoritative source text, the project applicability carries the program's decisions about it; citing only one layer masks a verification gap. (2) New workflow step 8 "Citation verification pass" instructing advisors to invoke the `citations` advisor (Agent tool) with each standards-clause / CFR / K-number / FDA-guidance reference before vouching, surfacing `broken` defects, treating `unverified` honestly without silently upgrading to `sound`, and skipping for cheap cross-references (intra-doc anchors, glossary terms). (3) Expanded workflow step 7 (External lookup pass) with an "AI-friendly federal endpoints" subsection naming **eCFR API** (`ecfr.gov/api/versioner/v1/...`), **Federal Register API**, **openFDA**, and **govinfo PDFs** as preferred over the bot-blocked `fda.gov` HTML site / direct media downloads; blocked-endpoint cases route to `/web-control` browser fallback or user-mediated PDF placement. Workflow step 9 (under-answering acknowledgment) renumbered to step 10. Pairs with `/dhf-manifest` v14 which registers the four new `registry_*` canonical roles surfacing L1a paths into Tier 2 of any advisor that declares them. Existing Tier 1/2/3 structure unchanged; existing per-advisor frontmatter unchanged (advisors opt into L1a coverage by adding `registry_*` to their `tier_2`). **Post-update:** Run `/advisors sync` in consuming projects to regenerate every advisor's GROUNDING section. Optionally edit each SME advisor's frontmatter `canonical_roles.tier_2` to add the four `registry_*` roles per domain relevance. (task ben/204)
  **Pairs with:** `/dhf-manifest` v14 (the canonical-role registry side).
- 1.4.0 (2026-05-28): **QMS-governance grounding section in canonical-role mode.** `render-grounding.py` emits a new `### QMS governance check` section above Tier 2 in the GROUNDING block. Tells advisor agents that when a document's discovery-index entry carries `governing_qms` (added by `/dhf-manifest` v13 from `.taxonomy.yml` v0.3+), they MUST `Read` the governing FORM-* templates and (first) parent SOP / WI before finalizing any recommendation that modifies that document. Captures the rule that authoring contracts live in QMS templates, not in ISO/IEC standards alone — a recommendation that contradicts the FORM's column schema, scoring scales, or section structure cannot be safely executed. Also covers the internal-mode fallback (read `qms-manifest.json` for non-`.taxonomy.yml` projects) and the unverified-mapping case (flag in answer rather than invent). Purely additive — does NOT change agent frontmatter or advisor invocation contract. (task ben/203)
  **Post-update:** Re-run `/advisors sync` (or `render-grounding.py --all`) to regenerate every grounding block with the new section. Requires sibling `/dhf-manifest` v13+ so discovery-index entries carry `governing_qms`; falls through harmlessly when older `/dhf-manifest` is installed (the section instructs agents on how to handle absence).
- 1.3.1 (2026-05-15): **Test runner.** Added `tests/run.sh` — a project-agnostic wrapper that runs the suite under `pytest`, resolving `pytest` + `PyYAML` ephemerally via `uv run --no-project` so no dev dependencies are installed into the repo and uv ignores any pyproject / PEP 723 script environment. Extra arguments pass straight through to `pytest` (`tests/run.sh -k locator -v`). Added a skill-local `.gitignore` excluding `__pycache__/`, `*.pyc`, and `.pytest_cache/` so test-run build artifacts are never committed. Bumped `VERSION` to track the 1.3.0 file-locator-wiring release, which shipped without a `VERSION` update.
- 1.3.0 (2026-05-14): **Semantic file-locator wiring for canonical-role advisors.** `render-grounding.py`'s `tier_3_section` template now emits a self-gated `### Semantic file locator` subsection (between Tier 2 and the Tier 3 researcher section) for every agent that declares a `tier_3.researcher`. It frames `mcp__file-locator__locate` as a fourth retrieval mode — a Tier-2 accelerator / Tier-3 fast path to reach for *before* the heavier researcher subagent — and carries the read-count rubric (read top hit, stop at 3 unless multi-source). The section is gated in-text on the tool's presence (`If mcp__file-locator__locate is not in your tool set, skip this`), so it is safe to ship to projects without the locator installed. All 11 solo canonical-role advisors gained `mcp__file-locator__locate` on their `tools:` line; the 2 console panels run all-tools and need no grant. New `tests/test_file_locator_wiring.py` — project-agnostic renderer-level + per-agent structural coverage. Tests: 40 → 85. Behavioral A/B on the `regulatory-affairs` advisor: locator-enabled discovery was ~23 % cheaper in tokens and more complete than glob/grep on a semantic query. (task ben/193)
  **Post-update:** Re-run `/advisors sync` (or `render-grounding.py --all`) to regenerate every grounding block with the new section — purely additive, no agent-frontmatter migration required. The locator section is self-gating, so projects that have not installed the `file-locator` skill see it but advisors correctly skip it. To actually exercise it, install the sibling `file-locator` skill (`/file-locator setup` + `rebuild`); the MCP tool grant on each advisor's `tools:` line goes live on the next session restart.
- 1.2.0 (2026-05-12): **Canonical-role grounding mode + advisor-researcher subagent.** `render-grounding.py` and `lib/loader.py` extended with a third grounding mode (alongside legacy literal-glob): `console.canonical_roles:` frontmatter declaring `tier_1`, `tier_2`, `tier_3.researcher` lists. The renderer dispatches on this block, fetching role descriptions from the sibling `/dhf-manifest` skill's `data/canonical-roles.yaml` (L1+L2 registry) and emitting a 3-tier grounding body. Helper subagents (no `console:` block) are now skipped by `--all` rendering. New `advisor-researcher` subagent shipped — Read/Glob/Grep-only helper that domain advisors invoke via the `Agent` tool when Tier 1 + Tier 2 grounding doesn't cover the question (PR #151, v1.1.0 → v1.2.0 transition). `regulatory-affairs` agent migrated from PILOT sentinel to fully auto-rendered canonical-role mode — `/advisors sync` is safe to run against it again. Selectors (`dhfs: {role: system}`, `submissions: all`) render inline with role descriptions in the auto-generated body. Tests: 24 → 40 (13 new canonical-role-mode cases, 4 helper-skip cases). Token-cost validation on the pilot agent: 170 K eager → 20–70 K depending on Tier 1 slicing. (task ben/191 Phase 6)
  **Post-update:** Existing advisor agents stay on legacy literal-glob mode — no migration required. To opt an agent into canonical-role mode, replace `console.context:` + `console.sources:` with a `console.canonical_roles:` block (see `regulatory-affairs.md` for the template) and run `/advisors sync`. Requires sibling `/dhf-manifest` skill at version 9+ (canonical-roles.yaml schema 1.2 with `multi_file:` flag support).
- 1.1.0 (2026-04-16): **Install agents as symlinks instead of copies.** `init` and `add` now create `.claude/agents/<name>.md` → `../skills/advisors/agents/<name>.md` symlinks rather than copying the file. `remove` distinguishes symlinks (delete freely) from regular-file forks (require `--force`). Added Required Best-Practices row `Advisor agents installed as symlinks`. Rationale: copies drifted silently whenever `/sync-skills pull` updated the skill-owned source — symlinks propagate updates automatically. Pairs with skill-creator v2 (agent-symlink convention) and best-practices v10 (audit check).
  **Post-update:** Existing projects must delete copies in `.claude/agents/<advisor>.md` and re-run `/advisors init` (or `/advisors add <name>` per advisor) to recreate them as symlinks. `/best-practices` v10 will FAIL on the new check until converted. Project forks are preserved — regular files in `.claude/agents/` are left alone and should be documented in `.claude/sync-log.md` to pass audit.
- 1.0.0 (2026-04-15): Initial skill scaffold. Ships first advisor (`regulatory-affairs`) end-to-end: CC-native frontmatter with `console:` extension block, shared `lib/loader.py` consumed by the skill and (via symlink) by project-console, PEP 723 `render-grounding.py` idempotent CLI, `overlay-defaults.yml` seed, and 7 actions (init, list, add, remove, overlay, sync, setup). Three-tier sourcing model documented. Pending: remaining 11 core-team agents migrate under task 059; project-console refactor to consume `advisors_lib` under task 060. See task 058 for spike rationale and task 057 for analysis-of-record.
