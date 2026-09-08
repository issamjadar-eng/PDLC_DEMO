# multimodel — Design & Architecture

This document describes the design decisions behind the `multimodel` skill. It is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Overview

A thin, standard-library-only wrapper over other vendors' model CLIs (Grok, Codex/OpenAI, Antigravity/Gemini) plus one key-based HTTP path (OpenAI, disabled by default). It returns fail-closed, optionally schema-parsed answers through a CLI (`scripts/multimodel.py`) and a Python `Council` API, so a Claude Code session can get an independent second opinion and other skills can declare an optional dependency on it for cross-model checks.

## Lineage

Ported from a sister project's `multimodel` skill (v1, 2026-08) after a full review. The core — fail-closed `Response.ok`, never-raise fan-out, the `available()` / `probe()` split, `jsonx.best_object` last-substantive-object extraction, and per-provider schema-dialect handling — is carried over intact. Departures, each deliberate:

| Change | Why |
|---|---|
| Config moved from a root `config/models.toml` to a `multimodel:` block in `project.yml` (TOML still accepted via `--config`) | The registry convention is one project manifest read at runtime; skills never carry project data. |
| `local` (on-device MLX) provider dropped | It depended on a `localmodels` skill not in this registry and carried its host's domain rationale. Re-addable as one module + one registry line. |
| OpenAI HTTP adapter rewritten on `urllib` | Removes the only third-party dependency (`httpx`), and with it the `uv` venv, lockfile, and install step. The whole layer is now stdlib. |
| Domain vocabulary removed (roles, incident narratives, named people, host CLAUDE.md section references) | Project-agnostic authoring is a hard rule for registry skills; a portability test pins it. |
| Install instructions point at vendor pages instead of pipe-to-shell one-liners | The secops artifact scanner flags pipe-to-shell in skill docs, rightly. |
| CLI grew `--provider`, `--schema`, `--prompt-file`, `--tag`, `--json`, and a `providers` command | Other skills need a machine-readable contract and a way to send document-sized prompts. |
| Unknown `type:` entries and disabled entries are reported as `skipped` | A typo used to vanish silently. |
| `policy:` block (`external_send`, `never_send`) | A regulated project needs its posture on data leaving the machine written down where an auditor looks. |
| `~/.grok/bin` added to the binary search path | Where the Grok CLI installs by default. |
| Tests moved inside the skill (`tests/`, socket-guarded, CLIs faked) | Registry skills carry their own suite; the sister kept tests at its repo root. |

## Key Design Decisions

### Standard library only

One optional dependency was enough to require a virtual environment, a lockfile, a provenance record of the build, and an installer. Rewriting ~20 lines on `urllib` made all of that unnecessary. The vendor CLIs are global per machine and deliberately not vendored: a copy nobody updates is worse than a recorded version (`tools/multimodel/provenance.json`, refreshed by `setup`, drift reported by `--verify`).

### Fail closed, never raise

`Response.ok=False` means *no answer*. A provider that errors returns a failed Response rather than raising, so one dead backend cannot abort a fan-out — and cannot disappear from the result set either. A caller that needs N independent answers counts `ok=True` and stops if short. The originating project hit the alternative: a parse failure that read as approval.

### `available()` versus `probe()`

Local checks (binary present, token file present) cannot see an expired session or a revoked entitlement. The probe makes a real call *with a schema*, so "answers but only in prose" is reported as a failure — every dependent relies on schema-shaped data. `doctor --quick` never claims more than it checked.

### Config in `project.yml`, posture in `policy:`

The skill reads its roster from the project manifest at runtime and ships only a template. `policy.external_send` is enforced by the CLI; `never_send` is documentation for callers because a content filter that cannot reliably detect PHI would create false confidence.

### Read-only project workspace by default, proven behaviourally

The vendor CLIs are agents with file tools. The first live run watched one read a project's design-history and QMS files to ground a verdict. That grounding is the value of a second opinion, so the default workspace is the project root — with each adapter pinned to read-only by the strongest control its CLI offers (Grok: a `--tools` allowlist of read tools; Codex: `--sandbox read-only`, any other sandbox refused; Antigravity: `--mode plan` behind a standing `permissions.allow` rule, refused otherwise). `isolated` remains available per provider or per call for prompt-only sends, and probes always run isolated.

Flags are claims. The `verify` action plants a marker with a fresh token, asks each agent to read it and to try writing a sibling, and judges from disk. Building it exposed two things a flag-reader would have missed: Grok's `plan` permission mode blocks reads as well as writes, and Antigravity's `--sandbox` does not stop file writes at all once permissions are auto-approved.

### Antigravity stays prompt-only unless the user grants a machine-wide rule

The question "can the Gemini permission live at project level?" was answered empirically on Antigravity CLI 1.1.27, print mode, 2026-09-08:

| Configuration | Reads | Writes | Notes |
|---|---|---|---|
| plain `-p`, no flags | soft-denied | soft-denied | `Print mode: soft-denying tool confirmation "ListDir"` — no tools at all; a clean prompt-only mode |
| `--dangerously-skip-permissions` | allowed | **landed** | `written.txt` created |
| `--sandbox` (+ skip-permissions) | allowed | **landed** | the terminal sandbox does not cover file tools |
| `--sandbox` or `--mode plan` alone | stalled to `--print-timeout` | — | confirmation waits for a terminal that is not there |
| repo `.agents/hooks.json` (PreToolUse allow/deny) | not loaded | not loaded | `loaded 0 named hooks from 0 hooks.json file(s)` in the trusted repo and in scratch repos |
| repo `.agents/plugins/<name>/hooks.json` + `plugin.json` | not loaded | not loaded | same log line, with and without skip-permissions |
| `~/.gemini/antigravity-cli/settings.json` `permissions.allow` | the documented lever | — | user-global; the binary's own message: "Add an allow-rule under permissions.allow in settings.json" |
| `~/.gemini/config/projects/<id>.json` with `projectResources.resources[].folderUri` = workspace, `--project <id>` | **allowed, no rule** | **soft-denied** | the "active project directory" default from the docs. Probes that put `permissionGrants` blocks in this file (with a wrong `file(*)` grammar) were ignored; not needed |

What the vendor docs add (read after the experiments above; earlier probes had used a wrong action name):

- **Rule grammar** (antigravity.google/docs/permissions): `action(target)` in `deny` / `ask` / `allow` lists, precedence deny > ask > allow. Actions: `read_file`, `write_file`, `read_url`, `execute_url`, `command`, `unsandboxed`, `mcp`. `read_file(*)`, `read_file(/abs/or/workspace-relative/path)` (recursive); `write_file` implies `read_file`; "deny read implies deny write". The `file(*)` literals in the binary are not the public grammar — probes using them were invalid.
- **Defaults**: "reading and writing files inside your active project directory is automatically allowed"; shell commands and web default to *ask*, which headless mode soft-denies with a stderr notice (antigravity.google/docs/cli/headless). Measured under the default CLI project, reads were soft-denied too — the default project has no workspace bound, so it is not an "active project directory".
- **Projects** (antigravity.google/docs/cli/projects): `--new-project` creates one; `--project=<id>` attaches to it. The CLI writes `~/.gemini/config/projects/<uuid>.json` as `{"id", "name", "projectResources": {"resources": [{"folderUri": "file:///abs/path"}]}}` — observed by letting it create one for this workspace. Whether an attached workspace-bound project auto-allows reads in print mode is **unverified**: the run that would have tested it fell into an OAuth prompt and timed out, and the sign-in had to be redone.
- **Scopes**: the interactive `/permissions` manager has Project / Shared / Global tabs; the docs do not say where the Project scope is stored, and no non-interactive way to add a rule is documented.
- **Known bug**: google-antigravity/antigravity-cli#548 reports print mode ignoring `permissions.allow` in every scope and hanging instead of soft-denying (Windows, no maintainer response at the time of reading). On this machine the observed behaviour was soft-deny, not hang, except with `--sandbox` / `--mode plan`.

**Confirmed after re-login (1.1.27):** attached with `--project` to a project whose `folderUri` is this workspace, `view_file` ran with no permission rule at all (read probe returned the marker) and `write_to_file` was auto-denied with the notice naming the `write_file` permission — the run ends with no output, and the file is not on disk. `--mode plan` pushed the model onto shell commands (denied), so it is not used. That is the design now implemented: `setup` reuses the workspace-bound project or creates `multimodel-<slug>.json` (own id, create-if-absent, never the default project, never `settings.json`); the adapter resolves the id from `folderUri` (or `project_id:`) and passes `--project`; it refuses project mode when the user's CLI settings hold a `write_file(...)` allow rule covering the repo, because write implies read. `verify` runs a read probe and a separate write probe per provider so a silent post-denial run still yields a verdict from disk. Live result: grok, codex, antigravity all PASS.

Side effect worth knowing: the `--new-project` flag (used once here to learn the schema) started an OAuth consent flow that timed out in headless mode and invalidated the sign-in; the skill never calls it. `setup` writes the project file itself.

So the template ships Antigravity as `isolated`. A user who accepts a machine-wide read-tool rule flips it to `project`; the adapter reads (never writes) that settings file and refuses project mode until the rule is present.

### Trust the CLI's own structured-output verdict

Where a CLI reports `structuredOutput` (and `stopReason` / `structuredOutputError`), the Grok adapter uses those fields exclusively and never falls back to scraping the text stream. A cancelled run leaves well-formed interim objects in the stream; scraping them produced a placeholder verdict in testing. Older CLI versions without the field keep the last-substantive-object fallback.

### Roles are labels, not semantics

`role:` groups providers for callers to filter on (`--role challenger`). This layer never interprets it. What a verdict *means* stays in the calling skill.

## Dependencies

| File | Required by | Purpose |
|------|-------------|---------|
| `project.yml` `multimodel:` | all actions | provider roster + policy |
| `project.yml` `security.approved_skills` | secops posture | `multimodel` must be listed |
| `tools/multimodel/provenance.json` | `setup --verify` | recorded CLI versions and paths |
| `grok`, `codex`, `agy` on the machine | matching providers | global vendor CLIs; absent → provider unavailable |
| PyYAML | `project.yml` reads | present wherever the manifest is read from Python |

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill has SKILL.md | File exists at skill root | Required | shared |
| Frontmatter complete | name, description, version, updated all present | Required | shared |
| README.md exists | Design doc at skill root | Required | shared |
| Changelog current | Latest entry matches version number | Required | shared |
| Config block present | `project.yml` has a top-level `multimodel:` key with `providers:` | Required | local |
| Skill approved | `multimodel` listed in `project.yml` `security.approved_skills` | Required | local |
| Package stays portable | `pytest .claude/skills/multimodel/tests/test_portability.py` passes (stdlib-only, no domain identifiers, no pipe-to-shell docs) | Required | local |
| Suite green | `pytest .claude/skills/multimodel/tests` passes | Recommended | local |
| Workspace posture explicit | every enabled CLI provider in `project.yml multimodel.providers` declares `workspace:` | Recommended | local |
| Read-only access verified | `multimodel.py verify` passes for every provider used in `project` workspace; re-run after any vendor CLI update | Required | local |
| Provenance recorded | `tools/multimodel/provenance.json` exists; `setup.py --verify` reports no drift | Recommended | local |

## Changelog

- 1 (2026-09-08): Initial version — ported from a sister project's multi-model access layer. Providers: grok, codex, antigravity (alias gemini), openai_http (alias openai). Standard-library only; config read from `project.yml multimodel:` or a TOML file; CLI `doctor` / `providers` / `ask` with `--provider`, `--schema`, `--prompt-file`, `--tag`, `--timeout`, `--workspace`, `--json`; per-provider `workspace: isolated | project` (isolated default; probes always isolated); `policy.external_send` gate; skipped-entry reporting; Grok adapter honours `stopReason` / `structuredOutput` / `structuredOutputError` and reports `num_turns` + cost in `usage`; Codex passes `--skip-git-repo-check` so the isolated directory is accepted; Antigravity checks sign-in via `agy models` (no token-path assumption) and aligns `--print-timeout`; default workspace is the project root with read-only enforcement per CLI (Grok `--tools` allowlist + web search off, Codex `--sandbox read-only` enforced, Antigravity `--mode plan` gated on a `permissions.allow` rule); `verify` action + `verify` module run the behavioural read-marker / attempt-write check live (per-provider scratch dirs, bounded read-miss retry, cleanup); Grok `schema_mode: auto | cli | prompt` because the CLI's `--json-schema` constrains the first turn and suppresses tool use; Antigravity project mode attaches to a workspace-bound CLI project (`setup` reuses or creates it; adapter passes `--project`; refuses if CLI settings grant `write_file` over the repo); `verify` makes separate read and write probes and reports isolated-by-config providers as skipped; hermetic test suite inside the skill.
