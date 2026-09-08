---
name: multimodel
description: "Lightweight, dependency-free access layer to OTHER model vendors — Grok (xAI), OpenAI (Codex CLI on ChatGPT OAuth, or metered HTTP), and Gemini (Antigravity CLI) — returning structured, fail-closed answers. Exists so the session can get an independent second opinion, cross-check an analysis or a set of findings against a differently-trained model, or run a multi-model fan-out; and so other skills can declare an OPTIONAL dependency on it and degrade gracefully when no provider is configured. TRIGGER on: 'ask another model', 'get a second opinion', 'cross-check this with grok/gpt/gemini/codex/openai', 'what do other models say', 'multi-model', 'run this past a different model', 'independent review from another vendor', 'which providers are configured / available', 'multimodel doctor', or any edit to the `multimodel:` block in project.yml. NOT for calling Claude (that is this session), NOT for building knowledge packs for external assistants (that is knowledge-pack-export)."
version: 1
updated: 2026-09-08
---

# multimodel — talking to several models at once

Usage: `/multimodel <action> [arguments]` — or shell out to the CLI documented under **Depending on this skill**.

**This is the general-purpose access layer.** It knows how to reach other vendors' models and return structured answers. It knows nothing about any domain, and it installs nothing: the package is standard-library Python that shells out to vendor CLIs already on the machine.

## Why more than one model

A single model is a single set of priors. Ask it to check its own reasoning and it mostly agrees with itself — the same training producing the same blind spot twice. An independently-trained model is the cheapest available source of genuinely uncorrelated error.

- **Agreement is weak evidence.** Models can share a blind spot, especially on anything widely written about.
- **Disagreement is information.** "The models disagree, and here is the crux" is often the most useful output. Do not average it away into a clean answer.

## Providers

Configured in the host project's `project.yml` under `multimodel: providers:` (template: `templates/models.yml`). The CLI providers use **subscription OAuth, not API keys** — no credential lands on disk for them.

| Provider key | Reaches | Via | Auth | Setup (one-time, per machine) |
|---|---|---|---|---|
| `grok` | xAI Grok | `grok` CLI | xAI account OAuth | install the Grok CLI from xAI, sign in once |
| `codex` | OpenAI | `codex` CLI | **ChatGPT** OAuth | `npm i -g @openai/codex`, then `codex login` → **Sign in with ChatGPT** |
| `antigravity` (alias `gemini`) | Google Gemini lineage | `agy` CLI | Google OAuth | install the Antigravity CLI from Google's page, run `agy` once to sign in |
| `openai_http` (alias `openai`) | OpenAI | HTTPS | API key from an env var | `export OPENAI_API_KEY=…`; ships **disabled** — metered billing |

Two traps recorded so nobody re-learns them:

- **Choose "Sign in with ChatGPT" for Codex, not the API key option.** The key path bills separately at API rates instead of using plan credits.
- **Do not swap the `antigravity` adapter for the older `gemini` CLI.** The sister project that originated this adapter recorded Google withdrawing Gemini CLI OAuth for individual accounts in mid-2026; a `gemini` binary on the machine is not evidence it still answers. If yours does, register it as a custom provider.

Each entry accepts `enabled`, `role` (a free grouping label — the template uses `challenger`; this layer never interprets it), `workspace` (see **What leaves the machine**), `command`, `timeout_seconds`, `description`, plus adapter-specific keys (`model`, `max_turns`, `read_tools`, `web_search` for grok; `model`, `reasoning_effort`, `sandbox` for codex; `model`, `effort` for antigravity; `api_key_env`, `api_url` for the HTTP path). `type:` defaults to the entry name.

## Supporting Files

| File | Purpose |
|------|---------|
| `README.md` | Design document — lineage, design decisions, Best Practices table, Changelog |
| `scripts/multimodel.py` | The CLI: `doctor`, `providers`, `verify`, `ask`. Self-contained (adds `src/` to the path); the contract other skills call |
| `scripts/setup.py` | `setup` action — appends the `multimodel:` block to `project.yml` if absent; records vendor-CLI provenance to `tools/multimodel/provenance.json`; `--verify` reports drift |
| `templates/models.yml` | The `project.yml` block the setup action appends — providers + `policy:` posture |
| `src/multimodel/` | The portable package: `types` (Ask / Response / ProbeResult), `base` (Provider ABC, `run_cli`, probe, workspace), `jsonx` (messy-output JSON extraction), `registry`, `council` (fan-out), `config` (project.yml / TOML loader, policy, project root), `verify` (the behavioural read-only check), `providers/` (one module per vendor) |
| `tests/` | Hermetic pytest suite (socket guard; vendor CLIs faked) — `pytest .claude/skills/multimodel/tests`. Pins the read-only flags each adapter passes and the verifier's verdict logic; the live counterpart is the `verify` action |

## Dependencies

| File | Required by | Purpose |
|------|-------------|---------|
| `project.yml` `multimodel:` block | every action | provider roster + `policy:`; appended by `setup` from the template |
| PyYAML (`import yaml`) | reading `project.yml` | already present in any project that reads its manifest from Python; a `.toml` config via `--config` needs nothing |
| `grok` / `codex` / `agy` binaries | the matching provider | global per-machine installs from the vendors; absent → that provider reports unavailable, nothing else breaks |
| `tools/multimodel/provenance.json` | `setup --verify` | recorded CLI versions/paths; committed |
| `.state/multimodel-verify/` | `verify` | transient marker files for the live read-only check; gitignored, removed after each run |
| `~/.gemini/config/projects/*.json` | antigravity in `project` workspace | the CLI's own project registry: `setup` reuses the project bound to this workspace or creates `multimodel-<slug>.json` (never overwrites); the adapter resolves the id from `folderUri` |
| `~/.gemini/antigravity-cli/settings.json` | antigravity in `project` workspace | read (never written) to refuse project mode if a `write_file(...)` allow rule covers the repo |

## Actions

Parse `$ARGUMENTS` to determine the action. Empty or `help` → show this usage.

### `setup`

Wire the skill into the project. Idempotent. No hooks, agents, or rules ship with this skill, so there is nothing to symlink.

1. Run `python3 .claude/skills/multimodel/scripts/setup.py`. It appends the `multimodel:` block from `templates/models.yml` to `project.yml` when absent (an existing block is never rewritten), records CLI provenance, and — when the antigravity provider is enabled in `project` workspace and `agy` is installed — ensures an Antigravity project is bound to this workspace (reusing one whose `folderUri` matches, so a team that runs Antigravity as its primary agent keeps its own project; else creating `~/.gemini/config/projects/multimodel-<slug>.json`). It never touches the CLI's global `settings.json`.
2. Add `multimodel` to `project.yml` `security.approved_skills` if the project keeps that allowlist — the secops posture check warns on an installed-but-unlisted skill.
3. Report what was appended vs already present, and which vendor CLIs were found. Then suggest `doctor --quick`.

### `doctor [--quick] [--json] [--all] [--timeout N]`

Prove the setup works — or say precisely what does not.

```bash
python3 .claude/skills/multimodel/scripts/multimodel.py doctor            # config + one live call per provider
python3 .claude/skills/multimodel/scripts/multimodel.py doctor --quick    # config only, makes NO calls
python3 .claude/skills/multimodel/scripts/multimodel.py doctor --json     # machine-readable
```

**`available()` and `probe()` are different checks, and the difference matters.** `available()` inspects local state — binary present, `codex login status`, `agy models` — without spending a model call. `probe()` makes a **real call** with a prompt *plus a schema*, so a provider that answers in prose is reported as a failure, not a pass. Only the probe can catch an expired session or a revoked entitlement, because neither changes anything on disk. `--quick` says so explicitly rather than implying everything is fine. Exit code 1 on any problem.

### `providers [--json]`

List every configured provider with `enabled` / `available` / workspace / reason, plus entries that were skipped (disabled, unknown `type:`). Makes no calls. Use this before a fan-out to know how many independent answers you can actually get.

### `verify [--provider NAME ...] [--timeout N] [--json]`

Prove, live and repeatably, that project access is read-only. For every available provider in the `project` workspace, the verifier makes **two** calls: it plants a marker with a fresh random token under `.state/multimodel-verify/<provider>/` and asks the agent to read it back, then asks it to create a sibling file — judging the read from the structured answer and the write from disk (a CLI that ends its run at the denial with no output still counts as blocked, because the file is not there):

| Verdict | Meaning |
|---|---|
| `PASS` | the token came back (the agent can gather project context) and no file appeared (it could not write) |
| `FAIL` | no file appeared, but the marker was not read back — project access is safe but not useful; check directory trust, permissions, or the CLI version |
| `CRITICAL` | a file appeared — that provider is **not** read-only; do not use it in `project` workspace until fixed. The verifier removes the file and exits 1 |

```bash
python3 .claude/skills/multimodel/scripts/multimodel.py verify            # every available provider
python3 .claude/skills/multimodel/scripts/multimodel.py verify --provider grok --json
```

A provider configured `workspace: isolated` is listed as skipped ("no project access to verify") rather than failed; name it with `--provider` to force the check. Run it after `setup`, after any vendor CLI update (`setup.py --verify` reports drift), and before relying on a provider for grounded review. It costs one real call per provider and runs from the project root because the CLIs only execute tools inside a directory they trust. The check is behavioural on purpose: a flag named `--sandbox` or `plan` is a claim, and one of the three CLIs' sandbox turned out not to stop file writes at all.

### `ask [PROMPT] [--prompt-file PATH|-] [--provider NAME ...] [--schema FILE|JSON] [--tag T] [--timeout N] [--workspace isolated|project] [--json]`

Ask every enabled provider (or only `--provider` ones) the same thing.

```bash
python3 .claude/skills/multimodel/scripts/multimodel.py ask "Is this argument sound? <argument>"
python3 .claude/skills/multimodel/scripts/multimodel.py ask --provider grok --provider codex \
    --prompt-file /path/to/prompt.md --schema /path/to/schema.json --json
```

- Long prompts go through `--prompt-file` (or `-` for stdin) — a document-sized prompt on argv can exceed the OS argument limit.
- With `--schema`, each answer is parsed into `data` and printed as JSON; without it, prose.
- A provider that did not answer prints `[NO ANSWER] <reason>` and the exit code is 1, so a partial fan-out is never mistaken for a full one.
- Refuses outright when `policy.external_send` is `forbidden`.
- `--workspace isolated` runs the vendor's agent in an empty directory for that call, so only the prompt leaves; the default `project` lets it read the repository (read-only) to gather context.

When the user asks in natural language ("cross-check this with grok"), build the prompt yourself: state the task, paste the material, ask for a verdict **and the strongest counter-argument**, and pass a small schema (e.g. `{"verdict": string, "crux": string, "confidence": number}`) so the answers are comparable. Report per provider, then the disagreement — not a blended average.

## Depending on this skill

A skill that wants a second opinion declares an **optional** dependency and treats an unavailable provider as *no answer*, never as agreement:

```yaml
dependencies:
  skills:
    - name: multimodel
      type: optional
      reason: independent cross-check of findings by a differently-trained model
```

Contract for dependents:

1. **Check first, cheaply.** `multimodel.py doctor --quick --json` → `providers.<name>.available`; or `providers --json`. If nothing is available, say so in the output ("no independent provider configured — findings are single-model") and continue. Never block on it.
2. **Ask with a schema and a tag.** `ask --provider X --prompt-file P --schema S --json --tag <lens>`. Read `responses[].ok`; count the `ok: true` answers you actually got. If you needed N independent answers and have fewer, report that — do not fill the gap by checking it yourself.
3. **Keep the domain on your side.** Put the meaning of a verdict in *your* skill; this layer only carries prompts and parsed replies.
4. **Give context up front, let the agent look further.** Put the question and the load-bearing excerpts in the prompt file so the answer is anchored and auditable; in the default `project` workspace the agent may then read the repository to check or extend that context. Use `--workspace isolated` when the prompt must be the only thing that leaves.

Python callers get the same through `Council`:

```python
import sys; sys.path.insert(0, ".claude/skills/multimodel/src")
from multimodel import Ask, Council, load_config
council = Council.from_config(load_config(), role="challenger")
for r in council.ask_all(prompt, schema=MY_SCHEMA, tag="risk"):
    print(r.provider, r.ok, r.data or r.error)
```

## Reading a Response — the one rule that matters

```python
Response(provider, ok, text, data, error, raw, tag, usage, at)
```

**`ok is False` means NO ANSWER. It never means a negative answer.** Everything in this layer fails closed to make the opposite reading impossible: a provider that errors, times out, or is unauthenticated returns `ok=False` (it does not raise, so one bad backend cannot abort a fan-out; it does not vanish, so you can see it did not answer); a schema that gets nothing conformant back → `ok=False`, not empty data; a truncated stream yields nothing rather than a salvaged partial answer.

## Structured output

Pass a JSON Schema and read `data`. The layer absorbs per-provider dialect differences: OpenAI needs `additionalProperties: false` and every property in `required` (the codex/HTTP adapters rewrite your schema; the others get it untouched); Antigravity returns an already-parsed `structured_output`; Grok has two modes — its CLI-enforced `--json-schema` constrains the **first** turn, which silences a model that narrates before calling a tool (measured 0 of 2 reads with the flag, 3 of 3 without), so in a `project` workspace the adapter asks for the schema in the prompt and takes the last substantive object carrying your first required key from the text stream, and uses the CLI schema only for `isolated` asks (`schema_mode: auto | cli | prompt`). Put the most identifying field **first** in `required`.

## What leaves the machine

Every prompt goes to a third-party service under that vendor's terms. The `policy:` block in `project.yml` states the project's posture: `external_send: allowed | forbidden` (enforced by the CLI) and a `never_send` list (a reminder for callers — there is no content filter, and a filter that cannot detect PHI reliably would be worse than an honest rule). In a regulated project: no patient-identifiable data, no credentials, and no controlled-document bodies unless the calling skill's own contract says so. Demo content is fine.

**The vendor CLIs are agents with file tools, not endpoints.** Launched in a project directory, they read from it to ground their answer — the first live run of this skill watched Grok spend seven turns reading design-history and QMS files. That is useful when it is what you want and pinned to read-only, so each provider has a `workspace`:

| `workspace` | Where the CLI runs | What the agent can do | When |
|---|---|---|---|
| `project` (default) | the project root (`--cwd` / `--cd` / process cwd) | **read** any file its tools reach to gather context; never write or execute | grounded second opinions — the prompt carries the question and the key excerpts, the agent may look further |
| `isolated` | an empty temporary directory | see the prompt and nothing else | prompts that carry all their own context, or content you do not want browsed around |

How read-only is enforced, per CLI — each mechanism was checked behaviourally on 2026-09-08 with the `verify` action, and it is that action, not this table, that proves it on your machine:

| Provider | Mechanism | What was observed |
|---|---|---|
| grok | `--tools read_file,list_dir,grep` allowlist (nothing else exists for the model) + `--disable-web-search` | read the marker, reported "no write tool available", no file created. The CLI executes tools only in a directory it trusts; `plan` permission mode blocks reads too, so it is not used; `--json-schema` suppresses tool use, so project-mode schemas go in the prompt |
| codex | `--sandbox read-only` (any other sandbox is refused in `project` workspace) + `--cd <root>` | read the marker, write attempt blocked by the sandbox, no file created |
| antigravity | `--project <id>` attaches to an Antigravity CLI project whose `folderUri` is this workspace (`setup` reuses one or creates `~/.gemini/config/projects/multimodel-<slug>.json`; `project_id:` overrides). The permission engine auto-allows reads inside the active project directory and headless mode soft-denies writes; refused if the user's CLI `settings.json` holds a `write_file(...)` allow rule covering the repo. No `--mode`, no `--sandbox`, no skip-permissions, nothing global written | print mode soft-denies every tool confirmation, reads included, so without a rule the agent has no tools; `--dangerously-skip-permissions` and `--sandbox` both let a file write land; repo-level `.agents/hooks.json` and `.agents/plugins/*/hooks.json` were **not loaded** in print mode (agy 1.1.27, six runs, trusted and untrusted workspaces) — see the README for the experiment log |

Probes (`doctor`) always run isolated. Even in `project` workspace, `never_send` still applies to what you paste into the prompt, and the vendor sees whatever the agent reads.

## Notes

- **Cost and latency differ by an order of magnitude** — re-measure with `doctor`. Observed: a trivial isolated probe ~3 s on Grok; on the originating project's machine (2026-08-17) ~5 s on Codex and ~7 s plus ~15–30 k tokens on Antigravity (it loads agent context on every invocation). A document-sized challenger prompt on Grok ran ~50 k tokens single-turn isolated versus ~490 k tokens over seven turns when it could read the project. Before a large fan-out, ask whether every lens needs the heaviest model; a `role:` label lets you keep a cheap subset.
- **A run can end without an answer** — a Grok run that exhausts its output budget inside its own reasoning comes back `stopReason: cancelled` with interim placeholder objects in the text stream, and one that appends prose after its JSON comes back with a `structuredOutputError`. The adapter reports both as `ok=False` (it never scrapes the stream when the CLI has already said no structured output was produced). Observed on a document-sized challenger prompt: Grok answered cleanly on about half of its runs, Codex and Antigravity every time. Retry, shorten the prompt, or lower the ask; do not read the failure as a verdict.
- **Subscription plans have capped throughput** where APIs are uncapped. A burst fan-out can hit a plan limit; the failure comes back as `ok=False` with the CLI's message.
- Entries with an unknown `type:` are listed under `skipped` by `doctor` and `providers` — a typo is visible, not silent.
- To add a vendor: one module under `src/multimodel/providers/`, one line in `registry.py`; or `register("name", cls)` at runtime from a host project.
