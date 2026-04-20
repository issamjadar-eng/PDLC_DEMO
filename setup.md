# Setup — PDLC_DEMO

Onboarding guide for new contributors. Covers local clone, Claude Code configuration, and the security posture every team member must confirm before working on this repo.

## 1. Clone and install dependencies

```bash
git clone git@github.com:<owner>/<repo>.git PDLC-DEMO
cd PDLC-DEMO
# Optional: install uv for tools that use it (e.g., project-console, advisors)
brew install uv   # macOS
# or:  curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Register as a team member

1. Open `project.yml`.
2. Add yourself to `team.active` — name, GitHub username, task folder (lowercase first name), role, email on an approved domain (see `security.approved_email_domains`), and `added: <YYYY-MM-DD>`.
3. Run `/secops check` (or start a new Claude Code session — the SessionStart hook runs it automatically). The hook writes your `tasks/<person>/SECOPS.md` file with a 7-day freshness cycle and a 30-day attestation cycle.

## 3. Claude Code — required security controls

### 3a. Training opt-out

Anthropic does not train models on Claude Code conversations by default for Pro / Team / Enterprise tiers, but you should still confirm:

1. Go to https://claude.ai/settings/data-privacy-controls
2. Confirm **"Help improve Claude"** (or equivalent training toggle) is **OFF**.
3. Record the attestation by running `/secops attest training-opt-out` — it updates your SECOPS.md.

Attestations refresh every 30 days. The SessionStart hook will warn when yours is stale.

### 3b. GitHub two-factor authentication (2FA)

Required by the security posture check.

1. Enable 2FA on your GitHub account at https://github.com/settings/security. Use an authenticator app (TOTP) or a hardware key — **not SMS**.
2. Generate 2–3 recovery codes and store them in a password manager.
3. If you have a `gh` CLI token, refresh it so the API returns the `two_factor_authentication` field:
   ```bash
   gh auth refresh -s read:user
   gh api /user --jq '.two_factor_authentication'   # should print: true
   ```
4. Record the attestation: `/secops attest 2fa`.

### 3c. Claude account 2FA

1. Go to https://claude.ai/settings/account.
2. Enable 2FA (authenticator app preferred).
3. Record the attestation: `/secops attest 2fa` (same command — the attestation covers both GitHub and Claude account 2FA).

## 4. Conversation hygiene

A few rules to internalize before you start using Claude Code on this repo:

- **Claude conversations are logs.** Treat them like commit messages — don't paste customer PHI, credentials, or anything you wouldn't write in a PR description. `**/PHI/**` and patient-data paths are already gitignored, but that only stops commits, not chat transcripts.
- **The `.claude/` directory is shared.** Skills, agents, hooks, settings, and MEMORY files in `.claude/` are checked into git and loaded across every session for every teammate. A personal reminder belongs in your user memory at `~/.claude/memory/`, not the project's `.claude/memory/`.
- **The task gate is real.** Edits outside the exempt list (`tasks/*`, `.claude/state/*`, `.claude/settings*.json`, `.claude/sync-log.md`, `.claude/MEMORY.md`, `.claude/memory/*`) require an active task. This is a feature — it forces every change to be captured somewhere the team can find it.
- **Strategy and Lessons must be captured inline.** When a non-obvious decision or insight lands, add a `<!-- STRATEGY CONTENT -->` or `<!-- LESSONS LEARNED -->` block to the active task **in the same turn** — not as a deferred cleanup pass. The `/strategy` and `/lessons` skills only surface what was written.

## 5. Integration awareness — MCP servers, plugins, agents

This project uses a security allowlist in `project.yml` (`security.approved_skills`, `approved_mcps`, `approved_plugins`, `approved_agents`). The `project-secops` agent audits what's actually installed against the allowlist at session start.

Before adding a new MCP server, plugin, or agent:

1. Understand what data it accesses. MCP servers run in your shell and can read files, make network requests, and hold credentials. Review the server's source (or at minimum its README) before approving.
2. Add it to the corresponding `approved_*` list in `project.yml` under an active task. This is how the team audits what tools touch project data.
3. If the MCP server requires an API token or OAuth, store secrets in your user-scoped config (`~/.claude/`) — never in the project `.env`. The `.gitignore` blocks `.env` from commits, but user-scoped secrets are the safer default.
4. For MCP servers that bridge to external services (Atlassian Rovo, Gmail, Calendar, Drive, LucidCharts, ICD-10), assume every piece of context you share with Claude during that session may be transmitted to the external service. Do not share PHI or other regulated data through those bridges.

`chrome-devtools` is already approved in this project — it drives a local Chrome for UI validation during `project-console` frontend work. It does not need special handling.

## 6. Running the project console (optional)

If you want the FastAPI dashboards + chat interface:

```bash
./tools/project-console/start.sh   # idempotent launcher (start or restart)
# Visit http://127.0.0.1:8765
```

First launch runs `uv sync` and creates `.venv/`. Port is configurable in `tools/project-console/console.yaml` (`server.port`).

## 7. Confirm everything is wired up

```bash
# Security posture check
/secops check

# Project-wide audit against shared best practices
/best-practices
```

Both should exit with zero Required FAILs after you complete the steps above. If anything fails, the output includes the specific fix for each check.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-20 | Ben Xavier | Initial version — created under task 018 sync-skills to close the four security-posture best-practices FAILs (training opt-out, GitHub 2FA, conversation hygiene, integration awareness). |
