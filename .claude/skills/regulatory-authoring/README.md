# Regulatory Authoring — design document

The writing-quality layer for controlled documents that face a regulator (FDA, EU Notified Body) or an auditor (ISO 13485 / 21 CFR 820 QMSR, Notified Body QMS audit). It owns a **standard** (rules + writing guidelines), a **lint**, a **copy-editor agent**, and a **binding rule** — and it composes with structure/scaffolding (`medtech-docs`), package-assembly (`submissions`), and the QA-conformance pass rather than absorbing them.

## Architecture (progressive disclosure)

The skill is deliberately split so an agent loads only what a task needs:

| Artifact | Role | Loaded |
|----------|------|--------|
| `SKILL.md` | trigger surface + one-line rule index + the 3-stage apply-workflow + actions | default (every trigger) |
| `references/authoring-standard.md` | the full standard — W/R/D rules, rationale, examples, corollaries, crosswalk | on demand, per rule in play |
| `references/rule-interactions.md` | precedence pairs + adjective/claim routing + tier-scope quick ref | when two rules collide on one span |
| `references/lint-signals.yml` | single source for every lint pattern (`id, rule, kind, pattern, zone, jurisdiction, severity`) | by the lint script only |
| `scripts/authoring_lint.py` | runs `regex`/`regex,partial`/`filesystem` signals over filed zones; reads `lint-signals.yml` + `project.yml` | `lint`/`check` actions |
| `agents/regulatory-copy-editor.md` | redline-first prose editor; never touches substance | `copy-edit`/`check` actions |
| `rules/regulatory-authoring.md` | auto-loaded binding rule (symlinked into `.claude/rules/`) | every session |

The standard is organized in **three layers** (the extraction seam): L1 `W` universal writing craft · L2 `R` regulated-document register · L3 `D` medtech DHF/submission specifics. If a general writing skill is ever warranted, L1+L2 lift out and this skill keeps L3 + a dependency.

## The 3-stage workflow

`lint` (mechanical, deterministic) → `regulatory-copy-editor` (prose judgment, redline, never substance) → `quality-engineering` QA-conformance (structure vs. the governing FORM). Each is a different *kind* of check; a clean lint is necessary, not sufficient.

## Lineage

Promoted from a project-local defect-derived capture (`dhf-authoring-guidances.md`, rules G-0…G-12) that was hardened across multiple SAD/DTM correction cycles, then restructured into the three-layer standard and refined through three agent-review rounds (clarity/ambiguity, example-sufficiency, dogfood-application + regression + domain-soundness). The G→W/R/D crosswalk is in `references/authoring-standard.md`. The temporary binding rule `.claude/rules/dhf-authoring-guidance.md` is retired by this skill's `setup` (its stated removal condition was promotion to a registry skill/rule).

## Project-agnostic boundary

Everything shipped here is project-agnostic (no company/device/codename/task IDs). Project-specific material — war-story examples, ID schemes, QMS-mirror tooling corollaries, the confirmation-token vocabulary — lives in a **project-local appendix** (`docs/internal/…`), never in this skill. The lint reads project-specific tokens (`{{task_folders}}`, `{{jira_keys}}`, `{{confirm_token}}`, `{{retired_tree}}`) from `project.yml` at runtime; a token that isn't configured causes its signal to be skipped (reported), never hard-coded.

## Composition with `writing-well` (kept separate by design)

The registry's `writing-well` skill is the **general nonfiction-prose** skill (Zinsser: simplicity, clarity, brevity, *humanity* — voice, warmth, the lead and ending, punch). It is tuned for blogs, articles, marketing, READMEs, emails — and its judgment layer is deliberately the **inverse** of the regulated register (it prizes voice and variety; regulatory writing prizes a voiceless, verbatim-consistent, evidence-anchored register). The two skills are therefore **kept separate**, not merged.

`regulatory-authoring` reuses exactly one thing from `writing-well`: its deterministic `lint_prose.py`, and only the **conflict-free subset of tags** (`clutter,nominalization,opener,length`). This was established empirically by running `lint_prose.py` against deliberately reg-correct prose:

| writing-well tag | On regulatory prose | Decision |
|---|---|---|
| `clutter`, `nominalization`, `opener`, `length` | Aligned — catches "In order to", buried verbs, "there is", over-long sentences; "It should be noted that"→cut even reinforces R1.3 | **USE** (subset regulatory's own signals don't cover) |
| `cliche` | Flags **"state of the art"** — a *required* EU MDR term (D15.2), not a cliché; also duplicates W11 | **EXCLUDE** |
| `passive` | Flags "is validated / is rejected / is performed" — correct device-as-actor passives (R2/R3/W3) | **EXCLUDE** |
| `adverb` | Flags "automatically", "generally" — load-bearing technical qualifiers | **EXCLUDE** |
| `hedge` | Duplicates R5 | **EXCLUDE** |

`regulatory-authoring` does **not** adopt `writing-well`'s judgment layer or its `prose-editor` agent — `prose-editor`'s voice/warmth/lead/ending mandate must never run on a filed regulatory document. `regulatory-authoring` keeps its own `regulatory-copy-editor` (register + substance guardrail). `writing-well` is declared an **optional** dependency: the supplementary lint pass degrades gracefully when it is absent.

## Known gaps / future work

- **`[EU-NB]` / `[AUDIT]` clause-grounding is placeholder** (`⟦ground later⟧`). The authoring *behaviors* are in force (grounded in design-controls/audit practice); only the clause *citations* are deferred because ISO 13485 / 21 CFR 820 (QMSR) / EU MDR are not yet in the reference registry. Import those distillations, then resolve the stubs (never from memory). The lint gates `⟦ground later⟧` so a stub cannot reach a transmitted filed body.
- **Lint dependency sets** (R7 stop-word/defined-term/brand exclusion lists; W8 synonym map) are not yet packaged — those signals run as `dependency_gated`/high-recall candidates until the sets are added.
- **PyYAML** is required by `authoring_lint.py` (consistent with the other project scripts); the operational/CI environment provides it.

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill has SKILL.md | File exists at skill root | Required | shared |
| Frontmatter complete | name, description, version, updated all present | Required | shared |
| README.md exists | Design doc at skill root | Required | shared |
| Changelog current | Latest entry matches frontmatter version | Required | shared |
| Standard present | `references/authoring-standard.md` exists | Required | local |
| Lint single-sourced | `references/lint-signals.yml` exists; `authoring_lint.py` reads it (no inline patterns) | Required | local |
| Rule installed | `.claude/rules/regulatory-authoring.md` symlinks to `rules/regulatory-authoring.md` | Required | local |
| Copy-editor agent installed | `.claude/agents/regulatory-copy-editor.md` symlinks to `agents/regulatory-copy-editor.md` | Required | local |
| Temp wrapper retired | `.claude/rules/dhf-authoring-guidance.md` no longer present after `setup` | Recommended | local |
| Project-agnostic | No company/device/codename/task-ID strings under the skill dir | Required | shared |
| Lint runs | `authoring_lint.py <a known-flawed fixture>` exits 1 with the seeded errors | Recommended | local |

## Changelog

- 1 (2026-06-25): Initial version. Three-layer authoring standard (W/R/D) + one-line rule index + 3-stage apply-workflow; `lint-signals.yml` single source + `authoring_lint.py` (zone-aware, project-parameterized, case-insensitive by default with `case_sensitive` opt-in); `regulatory-copy-editor` agent (redline-first, substance guardrail); consolidated `rule-interactions.md`; binding rule that retires the temporary `dhf-authoring-guidance` wrapper. Promoted from the G-0…G-12 defect capture after three agent-review rounds. Composition with `writing-well` established (kept separate; reuse only the conflict-free `lint_prose.py` subset `clutter,nominalization,opener,length`, verified empirically; optional dependency).
