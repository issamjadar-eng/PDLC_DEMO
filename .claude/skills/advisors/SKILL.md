Base directory for this skill: `${CLAUDE_SKILL_DIR}`

# Advisors — Persona Subagents for Medtech Projects

Manage a bundle of persona advisors (Regulatory Affairs, Clinical Affairs, Risk Management, etc.) that serve two runtimes from one source:

1. **Claude Code main thread** — delegate strategy questions to a grounded, cited subagent via `Agent(subagent_type: "<name>", prompt: ...)`.
2. **project-console FastAPI app** — chat with the same advisors in a browser UI with the same grounding.

Usage: `/advisors <action> [arguments]`

> **Naming note:** internal skill code name is `advisors` to avoid overloading the word "assistant" inside Claude Code. User-facing copy in the project-console calls them **"Assistants"** via each agent's `console.title` field. Same agents, two labels.

## The three-tier sourcing model

Every advisor has grounding sources layered from most-portable to most-specific:

1. **Universal** — FDA guidance, ISO/IEC standards, industry frameworks. Identical across every medtech project scaffolded by `/medtech-docs init`. Baked into the agent file's `console.sources`.
2. **Shape-stable** — paths guaranteed by medtech-docs conventions (`docs/project/dhfs/**/design-controls/architecture/**`, `docs/project/submissions/**/*.md`, etc.). Only filenames differ across projects. Also baked into the agent file.
3. **Project-specific overlay** — selection, not shape. Narrowing to a specific DHF, excluding dormant devices, adding a project-unique directory. Lives in `project.yml` under `advisors.overlays.<name>` and merges at load time.

Resolution order: agent file baseline (tiers 1+2) → `project.yml` overlay (tier 3). `/advisors init` produces a working configuration with zero editing — tiers 1+2 are enough for useful answers on day one.

Agent bodies stay **device-agnostic**. Any device-specific framing enters via tier-3 overlay globs pointing at project strategy / architecture docs, never via edits to the persona prose.

## Dependencies

| File / Tool | Required by | Purpose |
|-------------|-------------|---------|
| `.claude/agents/` dir | `init`, `add`, `remove`, `sync` | CC's subagent discovery directory — the installed home of each advisor |
| `project.yml` | `init`, `overlay`, `list`, `sync` | Overlay storage and enabled-advisors curation list |
| `uv` (CLI) | `sync`, `render-grounding.py` | Python runner for the grounding renderer (PEP 723 inline deps) |

## Supporting files

| File | Purpose |
|------|---------|
| `agents/*.md` | Bundled advisor agent files (CC-native frontmatter + `console:` extension block). Source of truth for every advisor the skill ships. |
| `overlay-defaults.yml` | Seed `advisors:` section written into `project.yml` on `init`. |
| `scripts/render-grounding.py` | CLI that regenerates the `<!-- BEGIN GROUNDING -->` block in each agent file from its effective sources. Idempotent. PEP 723 inline deps (uv-managed). |
| `lib/loader.py` | Shared Python loader module: reads agent files, parses `console:` extension block, applies project.yml overlays, returns `DomainAgent` objects. Consumed by both the skill's actions and project-console via symlink. |
| `lib/__init__.py` | Package init re-exporting the public API. |
| `tests/` | Unit tests for the loader and grounding renderer. |
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

- 1.1.0 (2026-04-16): **Install agents as symlinks instead of copies.** `init` and `add` now create `.claude/agents/<name>.md` → `../skills/advisors/agents/<name>.md` symlinks rather than copying the file. `remove` distinguishes symlinks (delete freely) from regular-file forks (require `--force`). Added Required Best-Practices row `Advisor agents installed as symlinks`. Rationale: copies drifted silently whenever `/sync-skills pull` updated the skill-owned source — symlinks propagate updates automatically. Pairs with skill-creator v2 (agent-symlink convention) and best-practices v10 (audit check).
  **Post-update:** Existing projects must delete copies in `.claude/agents/<advisor>.md` and re-run `/advisors init` (or `/advisors add <name>` per advisor) to recreate them as symlinks. `/best-practices` v10 will FAIL on the new check until converted. Project forks are preserved — regular files in `.claude/agents/` are left alone and should be documented in `.claude/sync-log.md` to pass audit.
- 1.0.0 (2026-04-15): Initial skill scaffold. Ships first advisor (`regulatory-affairs`) end-to-end: CC-native frontmatter with `console:` extension block, shared `lib/loader.py` consumed by the skill and (via symlink) by project-console, PEP 723 `render-grounding.py` idempotent CLI, `overlay-defaults.yml` seed, and 7 actions (init, list, add, remove, overlay, sync, setup). Three-tier sourcing model documented. Pending: remaining 11 core-team agents migrate under task 059; project-console refactor to consume `advisors_lib` under task 060. See task 058 for spike rationale and task 057 for analysis-of-record.
