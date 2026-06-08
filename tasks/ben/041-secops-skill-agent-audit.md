# 041 — SecOps Skill/Agent Trojan-Horse Audit

**ID**: 041
**Created**: 2026-05-01
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the session-recovery point for this work. Update at every meaningful checkpoint. A commit is not a substitute. Resume-ready before any session boundary. Capture strategy + lessons in-flight.

## Goals

Add a supply-chain / behavioral audit to the `secops` skill that scans installed `.claude/` skills, agents, and hooks for trojan-like behavior the existing 16 SessionStart checks don't cover. The 16 checks today verify *who* is on the project (identity, access, allowlists) but assume the *contents* of approved skills are benign. This task closes that gap with a static-analysis pass.

Detect:

1. Outbound network calls to non-allowlisted hosts (curl/wget/fetch/nc to unknown domains).
2. File operations that escape the project tree (rm/mv/cp targeting `$HOME`, `/etc`, `/usr`, `/var`, system dirs, or absolute paths outside `$PROJECT_DIR`).
3. Silent edits to load-bearing project config from inside skill scripts (`project.yml`, `.git/config`, `CLAUDE.md`, `.gitignore`, `.claude/settings.json` outside the documented setup-merge pattern).
4. Credential / secret reads (`~/.ssh/`, `~/.aws/`, `~/.gnupg/`, `.env`, `GITHUB_TOKEN`, `ANTHROPIC_API_KEY`) — especially when paired with an outbound call.
5. Obfuscated execution (`base64 -d | bash`, `eval $(...)`, hex-escaped shell, `curl ... | sh`).
6. Privilege escalation (`sudo`, `chmod 777`, `chmod +s`, `setuid`).
7. Persistence writes (`~/.bashrc`, `~/.zshrc`, `~/.profile`, `crontab`, `~/.ssh/authorized_keys`, `~/Library/LaunchAgents`, systemd unit dirs).
8. Symlinks under `.claude/` that escape the project tree.
9. MCP server commands in `settings.json` whose binary/URL doesn't match the approved-MCP allowlist semantics.
10. Hooks registered in `settings.json` whose command path resolves outside the project.

Output: a per-finding report (severity, file, line, snippet, why it's flagged), and a summary block compatible with the existing `SECOPS.md` ledger.

## Todos

- [x] Draft new `audit` action in `.claude/skills/secops/SKILL.md`.
- [x] Implement scanner at `.claude/skills/secops/scripts/audit_artifacts.py` (pure-stdlib, no deps).
- [x] Run the scan against this project.
- [x] Triage findings — record true positives vs. expected behavior in this task.
- [ ] Decide whether to wire `audit` into the SessionStart hook on a slower TTL (e.g., 30 days) — deferred; keep on-demand for now.
- [ ] Push upstream to hitachi as a SecOps version bump (deferred until findings are clean).

## Implementation Notes

**Scanner design — `audit_artifacts.py`**

- Pure-stdlib Python 3 (matches the rest of the secops scripts directory style).
- Walks `.claude/skills/`, `.claude/agents/`, `.claude/hooks/`, plus `settings.json` / `settings.local.json`.
- For each text file, runs a battery of regex rules grouped by category. Each rule has `id`, `severity`, `pattern`, `description`, `allow_if` (suppression hints, e.g., setup-step context).
- Skip binary files (chardet not available — heuristic: read first 8 KB, abort if NUL byte present).
- Symlink check: `os.path.islink` + `os.path.realpath` → assert under `$PROJECT_DIR`.
- Settings.json check: parse JSON, walk `hooks`, `mcpServers`, resolve hook command paths.
- Output: human-readable summary on stdout + JSON sidecar in `tasks/{person}/SECOPS.md` Allowlist Warnings table (or a new `## Skill Audit Findings` section if nontrivial).
- Exit nonzero only if Critical findings exist.

**Suppression / context**

Several patterns are legitimate inside this skill's own setup paths (e.g., `secops/scripts/resolve_user.py` writes `git config --local`; `secops/SKILL.md` itself talks about merging into `settings.json`). The scanner needs a small context-aware allowlist:

- `git config --local` is allowed (project-scoped, not global).
- Writes to `.claude/settings.json` are allowed when the surrounding script is one of the registered `setup` or `register-hook.sh` scripts.
- The scanner treats `.md` documentation files differently from executable `.sh`/`.py`: doc files only flag on truly suspicious patterns (e.g., `curl ... | sh`), not on every mention of `~/.ssh`.

**Why not just use `bandit` / `semgrep`?** Those tools are great but bring a heavy dep. The point of a SessionStart-adjacent SecOps check is zero-install friction. The trojan rules here are narrow and shell-flavored, not general SAST.

<!-- STRATEGY CONTENT: development, secops, supply-chain -->
**Strategy — content-of-skills audit, not just allowlist audit.** The existing 16 checks gate *which* skills are approved (`approved_skills` in project.yml). They don't read what those skills *do*. A registry compromise (someone pushes a bad commit to `hitachi/skills/foo`) would pass all 16 today as long as `foo` was previously approved. Adding a static-analysis pass over the actual installed source code closes the loop: even an approved skill is checked for behavioral red flags before it runs. This is the supply-chain weak spot the project's threat model implicitly acknowledged but didn't yet have machinery for.

**How to apply.** When new skills land via `/sync-skills`, the audit gives a fast "does anything in this batch look weird?" answer without us having to read every diff. Run after every pull from hitachi; run before bumping `approved_skills`.
<!-- /STRATEGY -->

## Findings (first run, 2026-05-01)

Summary: 0 Critical · 5 High · 4 Medium · 0 Low. Every match was triaged as **expected behavior** (false positive) — no actual trojan-style red flags in the installed `.claude/` tree.

| File | Rule | Triage |
|------|------|--------|
| `change-control/actions/diagnose.py:120` | `CFG-GIT-CONFIG-GLOBAL` (High) | False positive — string is a remediation message printed to the user when their git identity doesn't match the roster. The script does not itself run `git config --global`. |
| `change-control/lib/path_convention.py:86` | `CFG-GIT-CONFIG-GLOBAL` (High) | False positive — same pattern, embedded in a `RuntimeError` message that tells the user how to fix their config. |
| `change-control/tests/test-internal-review.sh:53,70` | `EXEC-EVAL-VAR` (Medium ×2) | False positive — `eval "$cmd"` inside the test harness's own command runner. Internal test plumbing, not user-input-driven. |
| `project-console/scripts/scaffold.py:391` | `SEC-DOTENV` (High) | False positive — `print("  2. cp .env.example .env  # fill in credentials")` is setup-instruction text printed to the user, not a read of a real `.env`. |
| `secops/scripts/audit_artifacts.py:218` | `EXEC-EVAL-SUBSHELL` (High) | False positive — the rule's own pattern *description* string contains the literal `eval $(`. The scanner self-matches its own rule definitions. Acceptable price for keeping rules as data; could be silenced by reading the file as bytes and skipping the rule definition block, but the cost isn't worth the complexity. |
| `web-control/scripts/install-chrome-wsl.sh:40` | `FS-WRITE-SYSTEM` (High) | Expected behavior — installer for Chrome on WSL writes the apt source list to `/etc/apt/sources.list.d/`. This is the documented purpose of the script and only runs when the user explicitly invokes `web-control setup`. |
| `web-control/tests/test-lifecycle.sh:46,65` | `EXEC-EVAL-VAR` (Medium ×2) | False positive — same test-harness `eval` pattern. |

**Net read.** The scanner is doing its job: every rule that fired surfaces a behavior worth a human eyeball, and a quick eyeball confirmed all of them are legitimate. Future improvements (deferred): per-rule path suppressions for these known-good cases (e.g., suppress `EXEC-EVAL-VAR` inside `*/tests/*` test runners), and a "string-literal vs. live shell" distinction for the Python rules. Both are nice-to-have but not blocking — the current signal-to-noise is acceptable for an on-demand audit.

<!-- LESSONS LEARNED: secops, static-analysis -->
**Lesson — regex SAST self-matches its own rule strings.** Any scanner that stores rules as Python data and lives inside the tree it audits will detect itself. The trade-off is between (a) keeping rules readable and centralized vs. (b) silencing self-matches at the cost of either putting the rule data in a separate file or special-casing the scanner's own path. Chose (a) here and documented the self-match as expected. Worth knowing for any future SAST-style skills.

**How to apply.** When adding new rules to `audit_artifacts.py`, accept that the rule definitions themselves may match. Document expected self-matches inline in the Findings table rather than building suppression machinery for them. If a future rule pattern is too noisy when applied to its own definition, move that rule's pattern to a sidecar file rather than trying to teach the scanner to skip its own rule block.
<!-- /LESSONS -->



## Changelog

- 2026-05-01 — Task created. Scanner spec drafted in Implementation Notes.
- 2026-05-01 — `audit_artifacts.py` implemented and `audit` action added to `secops/SKILL.md`. SecOps version bumped 6 → 7. First run: 0 Critical / 5 High / 4 Medium / 0 Low across the installed `.claude/` tree — all triaged as expected behavior (see Findings).
- 2026-05-01 — Tightened suppressions (option 2):
  - `EXEC-EVAL-VAR` suppressed under `/tests/` paths (test harnesses use `eval "$cmd"` to invoke command-under-test).
  - `EXEC-EVAL-SUBSHELL` suppressed in `secops/scripts/audit_artifacts.py` (the rule self-matches its own pattern string).
  - New `Rule.skip_in_py_string_literals` flag + tokenize-based span detection: matches that fall *inside* a Python string literal or comment are dropped (handles trailing-comma case where the line also has an OP token). Applied to `CFG-GIT-CONFIG-GLOBAL` and `SEC-DOTENV` so user-facing instruction strings don't trip them.
  - `FS-WRITE-SYSTEM` suppressed in `web-control/scripts/install-chrome-wsl.sh` (legitimate Chrome apt-source-list installer, documented purpose, runs only on explicit user-invoked `web-control setup`).
  - Final state: `Skill/agent audit: no findings.` exit 0.
- 2026-05-01 — Pushed locally (`6e7e95a` to PDLC_DEMO main) and upstream as hitachi PR [#109](https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/109) (`secops/v7-skill-audit`). Status: substantively complete pending upstream merge.
- 2026-06-08: Closed Complete via task-doc audit — audit_artifacts.py + audit action shipped (secops v7, 6e7e95a, hitachi PR #109). Moved to Completed in 000-index.md.

## Task Gate State File

Activation:
```bash
bash .claude/hooks/task-activate.sh add c0f539d8-5981-427a-8999-74b2c0485d0d 041
```
