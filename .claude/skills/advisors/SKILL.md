---
name: advisors
description: "Manage and ground a bundle of persona advisor subagents (Regulatory Affairs, Clinical Affairs, Risk Management, Cybersecurity, Quality Engineering, V&V, Human Factors, Post-Market, R&D, Systems Engineering, Program Manager) for a medtech project. Each advisor grounds itself in the project's DHF / strategy / standards / regulation documents via three-tier canonical-role grounding, and serves two runtimes from one source — Claude Code subagent delegation and the project-console browser UI. TRIGGER when the user wants to install, list, add, remove, enable, sync, or re-ground advisors / assistants; edit advisor grounding, overlays, or canonical-role tiers; regenerate the auto-rendered GROUNDING blocks; or wire advisor agents into the project or console. Actions: init, setup, list, add <name>, remove <name>, overlay <name> <op> <glob>, sync, help."
version: 11
updated: 2026-06-11
---

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

See [README.md](README.md) — consumed by `/best-practices` audit.

## Changelog

See [README.md](README.md) for version history.
