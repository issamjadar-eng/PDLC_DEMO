# Shared Skill Resources

Cross-skill assets that are used by two or more skills. Keeping them here instead of inside one owning skill prevents duplication and eliminates ownership ambiguity.

## Structure

| Path | Purpose |
|------|---------|
| `scripts/` | Python modules and standalone scripts used by 2+ skills (e.g., `office/` library, `resolve_user.py`) |
| `*.md` files at the root | Reference documents consumed by LLM subagents or by multiple skills' `@`-references (e.g., `agent-design-principles.md`, `task-content-scanner.md`) |

## When to add something here

**Add to `shared/scripts/`** when:
- 2+ skills need the same Python/shell logic
- The logic is project-plumbing (user identity, file I/O, registry parsing) rather than domain-specific to one skill
- Keeping copies in each skill would create a "fix-in-one-place-bug-in-the-other" drift risk

**Leave inside the owning skill** when:
- Only one skill uses it
- The code is intrinsic to that skill's domain and would make no sense in any other context

## How to import from `shared/scripts/` (Python)

Scripts that live inside a skill's `scripts/` directory (one level deep under `.claude/skills/`) reach `shared/scripts/` via two directory hops:

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "shared", "scripts"))

from office.soffice import get_soffice_env  # noqa: E402
```

The `noqa: E402` suppresses the "module-level import not at top of file" lint warning — it's intentional because the `sys.path` mutation must happen before the import.

Add a comment explaining why the `sys.path` line is there so future maintainers don't "clean it up."

## How to call a `shared/scripts/` script from a shell hook

Use an absolute path built from `$CLAUDE_PROJECT_DIR`:

```bash
RESOLVER="$CLAUDE_PROJECT_DIR/.claude/skills/shared/scripts/resolve_user.py"
if [[ -f "$RESOLVER" ]]; then
    python3 "$RESOLVER" --task-folder
fi
```

Always gate on file-existence (`[[ -f "$RESOLVER" ]]`) — a pull from upstream may not have the file yet during a partial sync.

## Current inventory

### `scripts/office/` — Office document XML library
Shared across `docx/`, `pptx/`, `xlsx/` skills. Pack/unpack/validate DOCX/PPTX/XLSX files via OOXML manipulation; includes LibreOffice subprocess wrapper and schema validators. Relocated from triplicated per-skill copies in task ben/098.

### `scripts/resolve_user.py` — Roster-driven user identity
Maps `git config user.email` (and related signals) → `project.yml team.active[]` entry. Emits the matched `task_folder` (for session state keys) or a stable email-slug fallback. Used by:
- `digest/hooks/session-briefing.sh` — keys the daily-briefing throttle file per user
- `secops/hooks/security-assert.sh` — populates `FULL_NAME` and `TASK_FOLDER` for SECOPS.md

Relocated from `secops/scripts/` in task ben/098 once the second cross-skill caller landed.

### `agent-design-principles.md`
Design principles for crafting subagent prompts. Referenced by `skill-creator`, `advisors`, and others when they scaffold or audit agent files.

### `task-content-scanner.md`
Shared algorithm for scanning task docs for tagged content blocks. Used by `strategy` and `lessons` skills' scanner/assembler subagents.

## Changelog

- 2026-04-23: README created. Documented `scripts/` convention + sys.path import pattern + shell-hook invocation pattern. Initial inventory of 4 shared resources. (Task ben/098 closeout.)
