---
name: secops
description: Security posture for regulated medical device projects — installs session security hooks, the project-secops agent, and a canonical permissions allow list into `.claude/settings.json`. Provides `setup`, `check`, and `attest` actions.
version: 6
updated: 2026-04-23
---

Base directory for this skill: `${CLAUDE_SKILL_DIR}`

# Security Posture (SecOps)

Owns the security-posture side of the Claude Code harness for regulated medical device projects. Packages the SessionStart security assertion, the `project-secops` remediation agent, and the canonical Bash/Read/Edit/Write permissions allow list.

Designed to be invoked automatically by `/medtech-docs init` (Step 5 — auto-discovery of skill `setup` actions), so fresh scaffolds get the full security baseline without manual wiring.

## Dependencies

| File / Tool | Required by | Purpose | How to create |
|-------------|-------------|---------|---------------|
| `jq` | `setup`, hooks | JSON parsing + permissions merge | `brew install jq` |
| `project.yml` | `setup`, `check` | Security policy, allowlists, team roster | `/medtech-docs init` or manual |
| `.claude/hooks/register-hook.sh` | `setup` | Idempotent hook registration helper | Installed by `/task setup` or `/medtech-docs init` |
| Task skill's `session-env.sh` | Hooks that rely on `CLAUDE_SESSION_ID` | Exports session ID as env var | `/task setup` |

`/secops setup` should run **after** `/task setup` has installed `register-hook.sh` and `session-env.sh`. `/medtech-docs init` Step 5 iterates skills in directory order, which is alphabetical — `secops` comes after `task`, so this dependency is satisfied by default.

## Supporting Files

| File | Purpose |
|------|---------|
| `hooks/security-assert.sh` | SessionStart hook — runs 16 security checks against `project.yml` (identity, access, infrastructure, supply chain). Results cached in `tasks/{person}/SECOPS.md` with a 7-day TTL. Symlinked into `.claude/hooks/` by `setup`. |
| `agents/project-secops.md` | Remediation agent — invoked when `security-assert.sh` reports Critical/High failures. Walks the user through fixes. Copied into `.claude/agents/` by `setup` (Claude Code only discovers agents in that location). |
| `templates/permissions.json` | Canonical `permissions` block (allow list of Bash/Read/Edit/Write patterns). Merged into `settings.json` by `setup` — **union** with existing entries, never clobbers. |
| `README.md` | Design documentation for humans. |

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform.

### `setup`

Wire the security posture into the current project. Idempotent — safe to re-run.

1. **Preflight**
   - Verify `jq` is available. If missing: warn `Install jq via brew install jq` and stop.
   - Verify `.claude/hooks/register-hook.sh` exists. If missing: warn `Run /task setup first — it installs the hook registration helper` and stop.
   - Verify `project.yml` exists. If missing: warn `Run /medtech-docs init first` and stop.

2. **Install agent**
   - Ensure `.claude/agents/` exists.
   - Copy `${CLAUDE_SKILL_DIR}/agents/project-secops.md` → `.claude/agents/project-secops.md` (skip if identical). Claude Code discovers subagents from `.claude/agents/` only — a symlink works but copying is safer for portability.

3. **Install hooks**
   - Ensure `.claude/hooks/` exists.
   - Create symlink `.claude/hooks/security-assert.sh` → `../skills/secops/hooks/security-assert.sh` (skip if already exists). Make sure the target is executable.

4. **Register SessionStart hook**
   ```bash
   .claude/hooks/register-hook.sh SessionStart "" command \
     '"$CLAUDE_PROJECT_DIR"/.claude/hooks/security-assert.sh'
   ```
   `register-hook.sh` is idempotent — safe to re-run.

5. **Merge canonical permissions into `settings.json`**

   The canonical allow list lives at `${CLAUDE_SKILL_DIR}/templates/permissions.json`. Merge it **as a union** (dedupe), never clobbering user-added entries:

   ```bash
   SETTINGS=.claude/settings.json
   CANONICAL=${CLAUDE_SKILL_DIR}/templates/permissions.json
   TMP=$(mktemp)

   # Create settings.json if it doesn't exist
   [ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"

   jq --slurpfile c "$CANONICAL" '
     .permissions = (.permissions // {}) |
     .permissions.allow = ((.permissions.allow // []) + ($c[0].allow // []) | unique) |
     .permissions.deny  = ((.permissions.deny  // []) + ($c[0].deny  // []) | unique) |
     if (.permissions.deny | length) == 0 then del(.permissions.deny) else . end
   ' "$SETTINGS" > "$TMP" && mv "$TMP" "$SETTINGS"
   ```

   Report the number of entries added vs. already present.

6. **Align git identity to the project roster** (v3)

   Run the resolver to write repo-local `git config user.email` + `user.name` to match `project.yml` `team.active[]`. This makes the project manifest the source of truth for git identity on this clone, regardless of the user's global `git config` defaults. Only `git config --local` is touched — other projects on the same machine are unaffected.

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/resolve_user.py" --align-git
   ```

   Resolution heuristics (first match wins): exact email match → single-member roster → fuzzy `user.name` substring → `$USER` matches `task_folder` → no-match (then no alignment, guest-clone warning only).

   The output is JSON with a `git_alignment.changes` list. Surface any changes to the user so they can see their repo-local identity was updated.

7. **Validate `project.yml` security block**
   - Read `project.yml`. If it does not have a `security:` key, warn the user:
     `project.yml has no security: block. /medtech-docs init should have created one — please add approved_skills, approved_mcps, approved_plugins, approved_agents lists manually.`
   - Do not fail — this is informational.

8. **Report**
   - Agent installed at `.claude/agents/project-secops.md`
   - Hook registered: SessionStart → `security-assert.sh`
   - Permissions: N entries added, M already present
   - Next: start a new session to trigger the first security check, or run manually: `echo '{}' | bash .claude/hooks/security-assert.sh`

### `check`

Run the security assertion manually (without starting a new session).

```bash
echo '{}' | bash .claude/hooks/security-assert.sh
```

Report whether the check passed, failed, or used cached results. Show the path to the relevant `SECOPS.md`.

### `attest <attestation-name>`

Record a manual attestation in the current user's `tasks/{person}/SECOPS.md`. Valid attestation names:

- `training-opt-out` — Claude training data opt-out confirmed
- `2fa` — Claude account 2FA enabled
- `integrations` — Connected integrations reviewed

1. Look up the current user in `project.yml` (`team.active[]`) — match by `git config user.email` or fall back to asking.
2. Find `tasks/{person}/SECOPS.md`. Create it if missing (use the template in `security-assert.sh` — it writes the file on first run).
3. Update the attestation's date to today (2026-04-12 format).
4. Confirm to the user.

Attestations are on a 30-day cycle — `security-assert.sh` warns when one is stale.

## How this skill integrates with `/medtech-docs init`

`/medtech-docs init` Step 5 iterates `.claude/skills/*/SKILL.md` and invokes `/skill-name setup` for any skill that defines a `setup` action. Because `secops` defines `setup`, it is picked up automatically — no changes to medtech-docs required.

Order matters for dependencies:
1. `/task setup` (installs `register-hook.sh`, `session-env.sh`, `session-cleanup.sh`, task gate)
2. `/secops setup` (installs security-assert, agent, permissions — depends on `register-hook.sh`)

Alphabetical directory iteration (`secops` after `task`) naturally satisfies this ordering. If future skills add ordering requirements, medtech-docs Step 5 may need an explicit dependency mechanism.

## Best Practices
See [README.md](README.md) — consumed by `/best-practices` audit.

## Changelog
See [README.md](README.md) for version history.

