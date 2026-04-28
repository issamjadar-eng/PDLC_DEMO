# 032 — Skill Tree Anonymization Audit (remove product/customer references)

**ID**: 032
**Created**: 2026-04-27
**Status**: Not Started
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. Update at every meaningful checkpoint (HARD RULE).
2. Phase-end batching is OK; drift-batching is not.
3. A commit is not a substitute.
4. Resume-ready before any session boundary.
5. Capture strategy + lessons as they happen.

## Goals

The skill tree under `.claude/skills/` (and the registry at `hitachi/skills/`) must be **reusable by any project / company**. Skills have leaked project- and customer-specific language — most visibly in `dhf-manifest`, but other skills are suspect too. This task audits the whole skill tree and the agents tree, removes specific names, and replaces them with **anonymized descriptors** that preserve enough context to be useful but never name a real company, product, or customer.

Anonymization rule of thumb (from user):
- ❌ "HipLink" → ✅ "a digital surgery project"
- ❌ "Arthrex" / "GlobalLogic" → ✅ "a sister project" or "an example deployment" or "the originating project" — never the company name
- ❌ "PainEase PCA Advanced" / "PP3500" → ✅ "an infusion pump" or "the example device"
- Even **history/changelog entries** must be sanitized — git history is fine to retain SHAs and dates, but human-readable text should be neutral.

Out-of-scope (these may keep their real names — they're project-local, not skill-local):
- `tasks/` (project-local task docs)
- `docs/` (project-local content)
- `project.yml` (project identity by definition)
- `CLAUDE.md`, `.claude/sync-log.md`, `.claude/MEMORY.md` (project-local meta)

In-scope:
- `.claude/skills/**` (every file: `SKILL.md`, `README.md`, `actions/*.md`, `templates/*`, `references/**`, `scripts/*`, `data/**`)
- `.claude/agents/**` (every agent definition file)
- The same trees on the registry side (`../hitachi/skills/**`, `../hitachi/agents/**`) — fixes pushed back upstream.

## Todos

### Phase 1 — Survey (read-only)

- [ ] Grep the local skill tree for likely offenders. Anchor terms (case-insensitive): `arthrex`, `globallogic`, `hitachi` (NB: registry repo name; only flag prose hits, not config), `painease`, `pp3500`, `pp3000`, `ip5000`, `sp6000`, `sp6500`, `hiplink`, `pdlc[_-]?demo`, `arthrex-pccp`, `painease pca`, `pca pump`, plus any concrete clinical-procedure names tied to a real product (knee/shoulder repair, regional anesthesia, etc.). Search across `.claude/skills/`, `.claude/agents/`, and the matching paths in `../hitachi/`.
- [ ] Catalog each hit: `path:line — verbatim phrase — proposed neutral replacement — file role (skill body / template / changelog / data / reference)`. Track in a Phase-1 findings table inside this task doc (do **not** spawn a sibling file).
- [ ] Triage findings into categories: (a) clear leak — must replace; (b) ambiguous — keep but generalize; (c) false positive — leave alone (e.g., a literal config string like `local_path: ../hitachi` in a SKILL.md is a real reference to the registry layout, not a leak).
- [ ] Decide a **canonical replacement glossary** so phrasing is consistent. Draft proposal:
  | Real term | Neutral replacement |
  |---|---|
  | Arthrex | "a sister project" / "another deployment" |
  | Arthrex PCCP | "the originating PCCP example project" |
  | GlobalLogic | "the parent company" or "the QMS owner" |
  | hitachi (registry) | "the skill registry" (in prose; keep literal in config + scripts) |
  | PainEase PCA Advanced / PP3500 | "the example infusion pump" |
  | HipLink | "a digital surgery project" |
  | PDLC_DEMO | "this demo project" / "a sample project" |
  Adjust during Phase 1 as findings come in.

### Phase 2 — Targeted fixes (write)

Per skill, make a focused edit pass. Group by skill so one PR per skill (or one combined PR if the diff stays small).

- [ ] `dhf-manifest` (highest priority — user flagged explicitly)
- [ ] `medtech-docs`
- [ ] `project-console`
- [ ] `trace-matrix`
- [ ] `tracker`
- [ ] `task`
- [ ] `docflow`
- [ ] `strategy`
- [ ] `lessons`
- [ ] `best-practices`
- [ ] `change-control`
- [ ] `secops`
- [ ] `sync-skills`
- [ ] `digest`
- [ ] `skill-creator`
- [ ] `advisors`
- [ ] `web-control`
- [ ] All agent files under `.claude/agents/**`

### Phase 3 — Push upstream

- [ ] One PR per skill (or one bundled PR if total churn is small) to the hitachi registry. Title pattern: `<skill>: anonymize project/customer references`. Body links back to this task and lists the anonymization mapping used.
- [ ] After merge, fast-forward local hitachi checkout. Re-run `/sync-skills check` and confirm zero `UPSTREAM_NEWER` rows for the touched skills.
- [ ] Spot-check arthrex-pccp post-merge: their next `/sync-skills pull` will pick the cleanup up; we don't need to push from there.

### Phase 4 — Guard rails

- [ ] Add a check to `best-practices` (or a new `skill-creator` rule) that greps skill content for the anonymization vocabulary and FAILs on hits. Severity: Required. Reason: prevent regression — the next time someone authors content inside a skill while looking at a real project, the lint catches the leak.
- [ ] Document the anonymization rule in `skill-creator` SKILL.md so it's load-bearing for any new skill.

## Notes

- **Do not rewrite git history.** Commit history retains the original prose; we only sanitize current file contents. SHAs in changelog entries stay accurate.
- Configuration paths and program names that are intrinsically project-shaped (e.g., `.local_path: ../hitachi` in `sync-skills/SKILL.md`) are not leaks — `hitachi` is the registry repo name and changing it would break the script. Keep literal strings in config; change only descriptive prose.
- README files inside skills sometimes cite the originating project for traceability. Acceptable phrasings: "originating project", "an example MedTech project", "a sister project", "a deployment". Unacceptable: real company / product names.
- The `dhf-manifest/data/` tree contains canonical regulatory references (FDA guidance, standards, frameworks). Those names are not leaks — FDA / ISO / IEC are public regulatory bodies. Only flag content that names commercial products / customers.

## Findings (Phase 1 — to be filled in)

| Path | Line | Phrase | Category | Proposed replacement |
|---|---|---|---|---|

## Changelog

- 2026-04-27: Task created. Triggered by user observation that `dhf-manifest` carries product/customer references; agreed audit must cover the whole skill + agent tree, sanitize history-prose too, and push upstream so arthrex-pccp inherits the cleanup. Out-of-scope: project-local trees (`tasks/`, `docs/`, `project.yml`, `CLAUDE.md`).
