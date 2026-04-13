---
name: best-practices
description: "Audit project setup against best practices from a shared registry and local skills — checks CLAUDE.md, folder structure, standards, tasks"
version: 7
updated: 2026-04-10
---

# Best Practices Audit

Audit this project's setup against best practices. Usage: `/best-practices [action]`

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform. Default action (no arguments) is `audit`.

### `audit`
Run a full audit of the project against all best practices.

**Step 1 — Fetch registry practices**

Determine the registry repo from `project.yml`. Read the file and find the first `registries:` entry with `type: github` — use its `repo:` and `path:` fields. If `project.yml` doesn't exist or has no github registry, fall back to `GlobalLogic-a-Hitachi-Company/hitachi` / `skills/manifest.md`.

Fetch the best practices manifest from the registry. Try methods in order:

1. **Local clone (preferred)**: If the registry entry has a `local_path:` field, resolve it relative to the project root and read `{local_path}/{REGISTRY_PATH}` directly. This is the fastest path and works offline.
2. **gh CLI (fallback)**: `gh api repos/{REGISTRY_REPO}/contents/{REGISTRY_PATH} --jq '.content' | base64 -d`
   - Works for both public and private repos when the user is authenticated with `gh`
3. **Raw URL (last resort)**: `https://raw.githubusercontent.com/{REGISTRY_REPO}/main/{REGISTRY_PATH}`
   - Only works for public repos
4. **If all fail**: Warn the user and continue with local-only checks.

Parse the manifest for practice definitions (see Registry Format below).

**Step 2 — Scan local skills**

Read all `.claude/skills/*/SKILL.md` files in the project. For each file that contains a `## Best Practices` section, parse the table of checks.

**Step 3 — Run checks**

**Tool selection rules (mandatory):** To avoid triggering user approval prompts, use dedicated tools for all checks:
- **File existence**: Use Glob (not `test -f` or `ls`)
- **Content search**: Use Grep (not `grep` or `rg` via Bash)
- **File reading**: Use Read (not `cat` or `head` via Bash)
- **Bash only for**: `gh api` (registry fetch), `bash .claude/hooks/*` (hook scripts), or `python3 -c '...'` (complex logic). These are pre-approved in `settings.json`. Never use bare `for`, `test`, `[`, or `if` as the first command in a Bash call — wrap in `bash -c '...'` or `python3 -c '...'` if shell logic is needed.

For each check from both sources (registry + local skills):

1. **Verify the condition** described in "How to Verify" — use Glob, Read, Grep as needed
2. **For the "Skills are self-contained" check**: Read each `.claude/skills/*/SKILL.md` file and scan for patterns that reference external files as dependencies — e.g., "using the template at `<path>`", "read from `<path>`", or file path references that the skill requires to exist in order to function. A skill may *reference* project files it reads/writes as part of its operation (e.g., a task skill reading `tasks/`), but must not depend on an external file to provide its own templates, structures, or definitions. All scaffolding content the skill generates must be defined inline in `SKILL.md` or in supporting files within the skill's own directory (referenced via `${CLAUDE_SKILL_DIR}`).
3. **For the "Skills are versioned" check**: Read each `.claude/skills/*/SKILL.md` file and verify it has YAML frontmatter with a `version:` field, and a `## Changelog` section. **Exempt externally-sourced skills** — if a skill's SKILL.md has no YAML frontmatter at all (no `---` delimiter in the first 5 lines), it is an external/utility skill and should be reported as INFO (not FAIL): `[INFO] <skill> — external skill, versioning not required`.
4. **Classify the result**: PASS, FAIL, or WARN
   - FAIL for "Required" severity checks that don't pass
   - WARN for "Recommended" severity checks that don't pass
   - PASS for checks that pass

**Step 4 — Report**

Display results grouped by source:

```
Project Audit: <project name from CLAUDE.md or folder name>

## Registry Practices (from GlobalLogic-a-Hitachi-Company/hitachi)
  [PASS] CLAUDE.md exists with project overview
  [PASS] Glossary exists
  [FAIL] No .gitignore found                          (Required)

## Task Management (from .claude/skills/task/SKILL.md)
  [PASS] Task folder exists
  [PASS] Task README exists
  [WARN] Index has 1 orphan task                       (Recommended)

Summary: 8/10 passed | 1 failed | 1 warning
```

After the report, suggest specific fixes for any FAIL or WARN items.

### `check <practice-name>`
Run a single named check and report its result. Useful for verifying a fix.

### `sync`
Fetch the latest skills from the registry and compare against locally installed skills.

1. Fetch the manifest using the same method as `audit` Step 1 (read registry `local_path` first, then gh CLI, then raw URL fallback). When reading from `local_path`, also run `git -C {local_path} pull --ff-only` first to ensure the local clone is current.
2. For each skill listed in the manifest's **Published Skills** table:
   a. Check if a corresponding directory exists in `.claude/skills/` with a `SKILL.md`
   b. If installed, read the local `SKILL.md`'s `version:` frontmatter and compare to the registry version
3. Report for each skill:
   - **Up to date**: local version matches registry version
   - **Update available**: registry version is higher than local version — show the registry changelog entries since the local version
   - **Not installed**: skill exists in registry but not locally
   - **Local only**: skill exists locally but not in registry (custom project skill)

## Registry Format

The shared registry at `GlobalLogic-a-Hitachi-Company/hitachi` uses this structure:

```
hitachi/
├── skills/
│   ├── manifest.md              # Master index of all published skills and project-level practices
│   ├── task/
│   │   └── SKILL.md             # Task management skill
│   ├── best-practices/
│   │   └── SKILL.md             # This skill
│   ├── medtech-docs/
│   │   ├── SKILL.md             # MedTech documentation skill
│   │   └── templates/           # Supporting template files
│   └── ...
```

### manifest.md format

The manifest has three sections:

**Terminology** — definitions of "skill", "command", and "registry"

**Project Practices** — best practices that apply to any project, not tied to a specific skill:

```markdown
## Project Practices

| Check | How to Verify | Severity |
|-------|--------------|----------|
| CLAUDE.md exists | `CLAUDE.md` exists in project root | Required |
| ...
```

**Published Skills** — index of available skills with versions:

```markdown
## Published Skills

| Skill | Directory | Version | Description |
|-------|-----------|---------|-------------|
| Task Management | task/ | 3 | Task-driven workflow with per-person folders |
| Best Practices | best-practices/ | 3 | Project audit against shared best practices |
```

### Skill file format

Every skill is a directory containing `SKILL.md` with:

1. **YAML frontmatter** with `name:`, `description:`, `version:` (integer) and `updated:` (date)
2. **Title and usage** — `# Skill Name` followed by description
3. **Actions** — what the skill does when invoked
4. **Best Practices** (optional) — checks the `/best-practices` audit should run for this skill
5. **Changelog** — reverse-chronological list of changes per version

Skills may include supporting files (templates, scripts, examples) alongside `SKILL.md` in the same directory.

## Best Practices

<!-- Read by the audit action to check project-level privacy and security -->

| Check | How to Verify | Severity |
|-------|--------------|----------|
| Team roster exists | `project.yml` exists in project root with `team:` section containing `active:` and `inactive:` lists | Required |
| Team roster has active members | `project.yml` `team.active` list contains at least one entry with a `github:` field | Required |
| .gitignore blocks secrets | `.gitignore` contains patterns for `.env`, `*.pem`, `*.key`, `credentials.json` | Required |
| .gitignore blocks PHI | `.gitignore` contains patterns for patient/clinical data (e.g., `**/phi/`, `*.hl7`) | Required |
| Setup guide covers training opt-out | `setup.md` contains instructions to disable Claude training on user data | Required |
| Setup guide covers GitHub 2FA | `setup.md` contains instructions to enable GitHub two-factor authentication | Required |
| Setup guide covers conversation hygiene | `setup.md` contains guidance on Claude conversation privacy and data awareness | Recommended |
| Setup guide covers integration awareness | `setup.md` contains guidance on MCP/integration data flow and account usage | Recommended |
| Agent design principles documented | `.claude/skills/shared/agent-design-principles.md` exists | Required |
| Evaluative skills document detection tiers | Every `.claude/skills/*/SKILL.md` that contains agent prompts (has an `agents/` subdirectory) or performs conflict detection / comparison / routing documents both programmatic (Tier 1) and semantic (Tier 2) evaluation approaches, or explicitly states why only one tier applies | Recommended |
| Security hook installed | `.claude/settings.json` SessionStart hooks array contains a command referencing `security-assert.sh` | Required |
| Secops agent exists | `.claude/agents/project-secops.md` exists | Required |
| Project manifest has security policy | `project.yml` contains a `security:` section with `approved_email_domains` and `approved_skills` lists | Required |

## Notes
- The registry repo defaults to `GlobalLogic-a-Hitachi-Company/hitachi` but is read from `project.yml` `registries:` section (first `type: github` entry)
- Fetching prefers `gh api` (works with private repos) over raw URL (public only)
- If the registry is unreachable, the audit still runs using local skill best practices only
- The audit is read-only — it never modifies project files, only reports findings

## Changelog

- 7 (2026-04-10): Added 3 security infrastructure checks — security hook installed, secops agent exists, project manifest has security policy. Part of task 024 completion.
- 6 (2026-04-09): Registry repo/path now read from `project.yml` `registries:` section (first `type: github` entry) instead of hardcoded. Falls back to `GlobalLogic-a-Hitachi-Company/hitachi` if no project.yml. Team roster checks updated from `team.md` to `project.yml`.
- 5 (2026-04-08): Exempt externally-sourced skills (no YAML frontmatter) from versioning check — reported as INFO instead of FAIL.
- 4 (2026-04-02): Added privacy and security best-practice checks — team roster, .gitignore hardening, training opt-out, 2FA, conversation hygiene, integration awareness.
- 3 (2026-03-30): Migrated from .claude/commands/ to .claude/skills/ directory structure. Updated all references from commands to skills. Updated registry format to directory-per-skill. Updated scan logic to read .claude/skills/*/SKILL.md.
- 2 (2026-03-30): Added self-containment and versioning checks. Updated sync action to compare versions via frontmatter. Added terminology section to registry. Added skill file format specification.
- 1 (2026-03-23): Initial version — audit, check, and sync actions against shared registry.
