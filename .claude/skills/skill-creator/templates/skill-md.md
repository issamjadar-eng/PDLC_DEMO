---
name: {{SKILL_NAME}}
description: "{{SKILL_DESCRIPTION}}"
version: 1
updated: {{DATE}}
---

# {{SKILL_TITLE}}

{{SKILL_OVERVIEW}}

## Supporting Files

| File | Purpose |
|------|---------|
| `README.md` | Design document — architecture, lineage, dependencies |

<!-- Add rows for each bundled file: hooks, agents, templates, references, scripts -->

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform.

### `setup`

Wire up hooks and agents for this skill. Idempotent — safe to re-run.

1. Create `.claude/hooks/`, `.claude/agents/`, and `.state/` (at project root) directories if they don't exist.
2. For each hook script in `hooks/`, create symlink `.claude/hooks/{{HOOK_NAME}}.sh` → `../skills/{{SKILL_NAME}}/hooks/{{HOOK_NAME}}.sh` (skip if already correct; replace if target moved).
3. For each agent file in `agents/`, create symlink `.claude/agents/{{AGENT_NAME}}.md` → `../skills/{{SKILL_NAME}}/agents/{{AGENT_NAME}}.md` (skip if already correct; leave forks — regular files — alone).
4. Register each hook:
   ```bash
   .claude/hooks/register-hook.sh {{EVENT}} "{{MATCHER}}" command \
     '"$CLAUDE_PROJECT_DIR"/.claude/hooks/{{HOOK_NAME}}.sh'
   ```
5. Report what was done (symlinks created / already-present / forks skipped / hooks registered).

<!-- Add more actions as needed -->

## Best Practices

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill installed | `.claude/skills/{{SKILL_NAME}}/SKILL.md` exists | Required | shared |

<!-- Add skill-specific health checks -->

## Notes

- If `$ARGUMENTS` is empty or just "help", show usage guide

## Changelog

- 1 ({{DATE}}): Initial version — {{INITIAL_DESCRIPTION}}.
