# Best Practices Skill — Design & Architecture

This document describes the design decisions behind the best-practices skill. It is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Overview

The best-practices skill audits project setup against a two-tier check system: shared practices from a remote registry and local practices defined by each installed skill. It also syncs skill versions against the registry.

## Role in the Ecosystem

best-practices is the **project auditor** — it validates that the project is set up correctly without modifying anything.

```
/best-practices audit
  ├─ Fetch registry manifest → project-level checks
  ├─ Scan local skills → skill-specific checks
  └─ Report: PASS / FAIL / WARN per check
```

## Dependencies

| File | Required by | Purpose | How to create |
|------|-------------|---------|---------------|
| `project.yml` | Privacy/security checks | Team roster, gitignore patterns | `/medtech-docs init` or create manually |
| `.gitignore` | Security checks | Verify secret/PHI patterns | Create manually |
| `setup.md` | Onboarding checks | Verify training opt-out, 2FA docs | `/medtech-docs init` or create manually |
| `CLAUDE.md` | Project checks | Verify task-first workflow, skill loading | Create manually |

When a dependency is missing, the audit reports it as a FAIL with guidance on how to create it.

## Key Design Decisions

### Two-Tier Check System

```
Registry (remote)              Local skills (project)
  ├─ Project-level checks        ├─ task skill checks
  ├─ CLAUDE.md exists            ├─ medtech-docs checks
  ├─ Glossary exists             ├─ best-practices own checks
  └─ ...                         └─ (any skill with ## Best Practices)
```

**Registry checks** are universal — they apply to any project using our skill ecosystem. **Local checks** are skill-specific — each skill defines its own in a `## Best Practices` table.

This means adding a new skill with checks automatically extends the audit without modifying best-practices itself.

### Registry Location

The registry repo is configured in `project.yml → registries[]`. Previously it was hardcoded in the skill — this was refactored in task 024 to make skills portable across organizations.

Fallback behavior: if the registry is unreachable, the audit runs using local checks only.

### Sync Action

`/best-practices sync` compares installed skill versions against the registry manifest. Reports: up to date, update available, not installed, local only. This is the skill update discovery mechanism — it doesn't auto-update, just informs.

## Changelog Context

- v1: Initial audit, check, sync against shared registry
- v2: Self-containment and versioning checks
- v3: Migrated to skills/ directory
- v4: Added privacy and security checks (team roster, gitignore, 2FA, training opt-out)
