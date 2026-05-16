# 061 — claude-md-references + audit-wiring rules into medtech-docs (+ dedup)

**ID**: 061
**Created**: 2026-05-15
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

Session-recovery point for this work. Keep current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE)** — tick todos, add dated Changelog lines naming concrete artifacts.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

## Goals

Third rule-disposition batch (after [[059]] task→scratch-and-tmp, [[060]] medtech-docs→readme-before-write+sentinel-blocks). Make `medtech-docs` own two more rules via the symlink pattern, and remove an existing duplication.

- `claude-md-references` → medtech-docs: new `rules/claude-md-references.md`, symlinked by `init`.
- `audit-wiring-before-adding-fields` → medtech-docs: new `rules/audit-wiring-before-adding-fields.md`, symlinked by `init`. **Tighten the rule + add concrete ✅/❌ examples for the AI** — the source rule had only one (abstract) example.
- **Remove duplication:** medtech-docs `init` Check 6 currently inserts an `audit-wiring` CLAUDE.md *block* from `templates/claude-md-config-audit.md`. The rule now exists as an auto-loaded `.claude/rules/` file — drop Check 6 + delete the template. One canonical form.
- Update medtech-docs README design docs to cover all four owned rules.
- Install in PDLC-DEMO; push upstream.

**Deferred:** `git-workflow` rule (tier-3, project-authored — separate later task). Check 5 (task-discipline CLAUDE.md block) left as-is — different rule, arguably task-skill-owned; out of scope, only renumbered.

<!-- STRATEGY CONTENT: operations, repo-governance -->
**Rule-ownership model, batch 3.** `claude-md-references` + `audit-wiring` → `medtech-docs`. medtech-docs now owns 4 auto-loaded rules. The `audit-wiring` dedup resolves a self-ironic case — the rule existed both as a promoted `.claude/rules/` file *and* a medtech-docs-seeded CLAUDE.md block (duplication is exactly what the rule forbids). Resolution: single `.claude/rules/` symlinked file; CLAUDE.md block dropped. Rule-creation routes observed across the batches: extraction (claude-md-references, from CLAUDE.md slimming), lesson-promotion (audit-wiring), direct authoring (git-workflow).
<!-- END STRATEGY CONTENT -->

## Todos

- [x] Create `rules/claude-md-references.md` (canonical source)
- [x] Create `rules/audit-wiring-before-adding-fields.md` — tightened + ✅/❌ examples
- [x] Delete `templates/claude-md-config-audit.md`; remove `init` Check 6 (CLAUDE.md block)
- [x] Rewire `init` Step 2c Checks — add symlink checks for both rules; renumber task-discipline check
- [x] Update SKILL.md Supporting Files + bump version
- [x] Update medtech-docs README design docs (Auto-Loaded Rules section — now 4 rules)
- [x] Install in PDLC-DEMO: symlink both rules into `.claude/rules/`
- [x] Push upstream to hitachi — hitachi PR #166, merged `69fb6cc`

## Changelog

- 2026-05-15: Task created. Recon: PDLC-DEMO CLAUDE.md has neither the audit-wiring nor task-discipline block; both templates exist in medtech-docs.
- 2026-05-15: **medtech-docs v24 → v25.** Created `rules/claude-md-references.md` (verbatim — already clean) and `rules/audit-wiring-before-adding-fields.md` (tightened: generic opening + new concrete ✅/❌ `## Examples` section — the source had only one abstract example). Deleted `templates/claude-md-config-audit.md` and removed the `init` Check 6 CLAUDE.md-block insertion (dedup — rule is now a single auto-loaded `.claude/rules/` file). Rewired `init` Step 2c: new Check 5 (audit-wiring symlink), Check 6 (claude-md-references symlink), task-discipline block renumbered Check 5 → 7. SKILL.md Supporting Files + closing sentence updated. README "Auto-Loaded Rules" section now covers 4 rules + a "One canonical form per rule" subsection on the dedup; v25 changelog entry added. Verified `/best-practices` has no dependency on the removed CLAUDE.md block (no audit FAIL introduced). Installed in PDLC-DEMO: `.claude/rules/` now holds 5 symlinked rules (all resolve). Pending: upstream push.
