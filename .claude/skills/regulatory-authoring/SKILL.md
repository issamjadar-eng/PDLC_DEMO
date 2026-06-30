---
name: regulatory-authoring
description: |
  Authoring rules + writing guidelines for controlled documents that face a regulator (FDA, EU Notified Body) or an auditor — DHF deliverables, submission narratives, and other controlled records. Owns the writing-quality layer of a filed document: lint, copy-edit/redline, and the canonical authoring standard. Composes with structure/scaffolding and package-assembly skills; it does not absorb them.

  TRIGGER when the user wants to:
    - **Lint / check a filed document** — "lint this filed doc", "run the authoring lint on <file>", "is the filed body of this <SAD/SRS/device-description/Q-Sub/risk> clean?", "check this submission section for internal leaks", "did I leave any task IDs / repo paths / hedge words / undefined acronyms in the filed body?"
    - **Copy-edit / tighten regulated prose** — "copy-edit this filed section", "tighten the prose in this device description", "redline this for clarity/consistency", "make this read like a regulated document, not marketing"
    - **Apply the authoring standard** — "apply the regulatory authoring standard to <file>", "three-tier 🔒 container check", "is this intended-use statement consistent?", "are the claims paired to evidence?"
    - Path-based — ANY edit to a controlled DHF/submission document body (e.g., `_confluence/<dhf>/**`, `submissions/{qsub,510k,pccp}/**`).

  Actions: `setup`, `lint <file>`, `check <file>`, `copy-edit <file>`, `help`.
version: 1
updated: 2026-06-25
dependencies:
  skills:
    - name: medtech-docs
      type: required
      reason: reuses the symlink-from-skill rule-install pattern + the taxonomy `governing_qms` resolution the QA pass reads
    - name: writing-well
      type: optional
      reason: the `lint` action runs its lint_prose.py for universal prose tells (conflict-free subset only); degrades gracefully if absent
  agents:
    - regulatory-copy-editor
    - quality-engineering
---

# Regulatory Authoring

Author and edit **controlled documents that a regulator or auditor reads** so they survive an adversarial reading. The skill carries two halves that work together — **positive writing guidelines** (how to write well in the regulated register) and **defensive authoring rules** (what must not appear, with greppable lint signals). A clean lint is **necessary, not sufficient**: substance is verified by the QA-conformance pass, never by the lint alone.

**Progressive disclosure (read only what the task needs):**
- This SKILL.md carries the **one-line rule index** (below) + the apply-workflow — the default load.
- `references/authoring-standard.md` carries the **full** rule + rationale + examples + corollaries — load it **on demand** for the specific rule in play, not all at once.
- `references/rule-interactions.md` carries the precedence + routing map — load it when two rules touch one span.
- `references/lint-signals.yml` is read by the **lint script**, never into your reasoning context.

## Supporting Files

| File | Purpose |
|------|---------|
| `README.md` | Design document — architecture, lineage, dependencies (not loaded at runtime) |
| `references/authoring-standard.md` | The canonical standard — full rules (W/R/D), rationale, examples, corollaries. Loaded on demand |
| `references/rule-interactions.md` | Consolidated precedence pairs + adjective/claim routing — load when rules collide on one span |
| `references/lint-signals.yml` | Single-source machine-lint patterns (`id, rule, kind, pattern, zone, jurisdiction, severity, message`). Read by the script |
| `rules/regulatory-authoring.md` | The auto-loaded binding rule (symlinked into `.claude/rules/`). Makes the standard mandatory for DHF/submission edits |
| `agents/regulatory-copy-editor.md` | Redline-first copy-editor subagent — applies prose/clarity/consistency edits, never substance |
| `scripts/authoring_lint.py` | Runs the `regex`/`regex, partial`/`filesystem` lint signals over a file's filed zones; reads `lint-signals.yml` + `project.yml` (no hard-coded names) |

## The three-layer model + audience tags

Rules live in three layers (the extraction seam): **L1 `W` — universal writing craft** · **L2 `R` — regulated-document register** · **L3 `D` — medtech DHF/submission specifics**. L3 rules carry audience tags: `[PORTABLE]` / `[FDA]` / `[EU-NB]` / `[AUDIT]`. **Before applying D14/D15/D-ARB, determine the filing route** from `project.yml` (`dhfs[].filing`) or the doc front-matter; absent a signal, treat as FDA-routed and flag the assumption. Full tier/scope rules + `[filed-only]` list are in `references/authoring-standard.md`.

## Rule index (one line each — load the standard for the full rule + example)

**L1 — Writing craft (`W`)**
- **W1** one verifiable claim per sentence (W1.1: don't coordinate device-actor + human-actor claims)
- **W2** `[filed-only]` quantify — number+unit+tolerance, or a managed-TBD placeholder; never a bare or invented adjective
- **W3** active voice by default; passive only when the system is the actor
- **W4** no orphan "it/this/these" — antecedent in the same/prior sentence
- **W5** topic sentence first · **W6** given-then-new flow · **W7** parallel lists/tables
- **W8** one term per concept, one concept per term (W8.1: verification ≠ validation)
- **W9** house conventions (ISO dates, SI units, semantic versions, explicit ranges)
- **W10** modal precision — shall/should/may; no `will` in the filed body (→ R1)
- **W11** `[filed-only]` no marketing register · **W12** cross-refs name target + relationship · **W13** definition = genus + differentia

**L2 — Regulated register (`R`)** — most are `[filed-only]`
- **R1** declarative, as-delivered, present tense; no promissory (R1.1 scope negatives to the device function; R1.2 approach-statements internal; R1.3 perform obligations, don't recite; R1.4 process status is always internal)
- **R2** requirement form — one testable behavior + acceptance criterion
- **R3** claim ↔ evidence pairing ("show me, don't tell me")
- **R4** rationale = claim → named basis → consequence/fallback
- **R5** limitations stated flatly; no hedging ("we believe", "it appears")
- **R6** dated/attributable — pin "currently/now" to a date or version
- **R7** every acronym defined + one consistent definition (consistency applies all tiers; Terms-completeness is filed-only)
- **R8** cross-record consistency — don't contradict the parent/sibling controlled record
- **R9** unevidenced **property** claims are removed or TBD-gated, never re-voiced into confident prose — **requirements (R2) are kept**

**L3 — Medtech DHF/submission (`D`)**
- **D1** `[PORTABLE]` pre-flight: read the governing FORM → schema-map → three-tier skeleton → quote-verify citations
- **D2** `[PORTABLE]` three-tier 🔒 model — internal in bounded `🔒 INTERNAL`/`🔒 END INTERNAL` containers; **doc-control header is visible controlled metadata, never 🔒-wrapped**
- **D3** `[PORTABLE,AUDIT]` document-control header complete (ID/version/status/effective-date/approvals/change-history)
- **D4** `[PORTABLE,AUDIT]` change-history says what changed and why · **D5** `[PORTABLE]` contiguous filed numbering · **D6** `[PORTABLE]` markdown/diagram hygiene
- **D7** `[PORTABLE,AUDIT]` conform to the governing QMS template; document any deviation
- **D8** `[PORTABLE]` title-based citations; no repo paths/task IDs/finding IDs/config refs in the filed body
- **D9** `[PORTABLE,AUDIT]` trace to controlled DHF artifacts (TBD allowed), never proposals/analyses; resolvable, ID-anchored
- **D10** `[PORTABLE,AUDIT]` managed TBDs — owner + closure gate
- **D11** `[FDA]` non-device 62304 class = QMS lifecycle policy, orthogonal to device status; determination-first needs basis + fallback
- **D12** `[PORTABLE]` two-layer specificity — modality/function specific, swappable instance generic-with-`e.g.` (D12.1 COTS sourcing; D12.2 compatibility homes; D12.3 no brand prefix; D12.4 platform-by-function; D12.5 cloud/infra)
- **D13** `[PORTABLE]` intended-use canonical form (who/what/input/purpose/setting), reused verbatim; unknown slots → TBD; "clinical" never on an admin function
- **D-ARB** `[FDA,EU-NB]` dual-audience arbitration — neutral default; intended-purpose governs when forced
- **D14** `[FDA]` FDA framing — PCCP boundary, SE tone, predicate narrative, confirmation token
- **D15** `[EU-NB]` ⟦clause-grounding placeholder⟧ EU framing — intended-purpose, state-of-the-art, AFAP, GSPR trace, Rule 11, zero PCCP, CER, EU label particulars

## Apply-workflow (the 3 stages)

A controlled document goes through three checks, each a different *kind* of check. Run them in order — lint clears mechanical noise first, the copy-editor improves prose, QA verifies the result still conforms to the FORM:

1. **Lint (mechanical)** — `authoring_lint.py` runs the `regex` / `regex, partial` / `filesystem` signals over the filed zones. Deterministic, no judgment. `dependency-gated` signals run only if their data (glossary, discovery index, `project.yml` field) is loaded, else flag unverified. `judgment` signals are surfaced as candidates, never auto-verdicts.
2. **Copy-edit (prose judgment)** — the `regulatory-copy-editor` agent applies the W/R rules as a redline (per-change rule + rationale), within a hard guardrail: **edits prose/clarity/consistency/register only, never substance** (claims, classifications, numbers, citations, tier placement). When clarity and a claim conflict, it flags rather than resolves.
3. **QA-conformance (structure)** — the `quality-engineering` agent asserts the edited document still conforms to its governing FORM (columns/sections/sign-offs) and the three-tier structure. This is the substance gate the lint cannot be.

## Actions

Parse `$ARGUMENTS` to pick an action.

### `setup`
Wire the binding rule + the copy-editor agent. Idempotent (skip / repoint / leave-fork).
1. Ensure `.claude/rules/`, `.claude/agents/` exist.
2. Symlink `.claude/rules/regulatory-authoring.md` → `../skills/regulatory-authoring/rules/regulatory-authoring.md` (skip if it already points there; repoint if moved; leave a project fork alone).
3. Symlink `.claude/agents/regulatory-copy-editor.md` → `../skills/regulatory-authoring/agents/regulatory-copy-editor.md` (same idempotency).
4. Append a one-line pointer to CLAUDE.md's "Auto-loaded rules" list (`- regulatory-authoring.md — …`) if not present.
5. Add `regulatory-authoring` to `project.yml` `security.approved_skills` and `regulatory-copy-editor` to `approved_agents` if absent.
6. If a **prior temporary rule** (`.claude/rules/dhf-authoring-guidance.md`) exists, this skill's rule supersedes it — remove the temporary file and its CLAUDE.md pointer (its stated removal condition is "promotion to a registry skill/rule").
7. Report what was wired vs already present.

### `lint <file>`
Run `python3 .claude/skills/regulatory-authoring/scripts/authoring_lint.py <file> [--jurisdiction fda|eu|all]`. The script reads `references/lint-signals.yml` + `project.yml`, evaluates the runnable signals over the file's filed zones (outside metadata comments and `🔒` containers), and reports findings grouped by lint `kind` — clearly marking `regex, partial` matches as **candidates** and `dependency-gated`/`judgment` signals as **flag-only**. Summarize; do not treat a clean lint as sufficient.

**Supplementary universal-prose pass (writing-well — conflict-free subset only).** If the sibling `writing-well` skill is installed, also run its deterministic linter for universal mechanical tells the regulatory signals don't cover — **but only the subset that is empirically conflict-free for the regulated register**:
```
python3 .claude/skills/writing-well/scripts/lint_prose.py <file> --only clutter,nominalization,opener,length
```
This adds clutter-phrase / buried-verb / empty-opener / long-sentence catches ("In order to" → "to"; "It should be noted that" → cut — which reinforces R1.3). **Do NOT enable writing-well's `passive`, `cliche`, `adverb`, or `hedge` tags on a regulatory document** — they fight the register: device-as-actor passive is correct (R2/R3/W3); **"state of the art" is a required EU term (D15.2), not a cliché**; technical adverbs ("automatically", "manually") are load-bearing; and `hedge`/`cliche` would double-report R5/W11. This pass is supplementary, advisory, and never gates; skip it silently if `writing-well` is absent. **Never run the `prose-editor` agent on a filed regulatory document** — its voice/warmth/lead/ending mandate is the opposite of the regulated register (use `regulatory-copy-editor`).

### `check <file>`
Run the full 3-stage workflow: (1) `lint`, then (2) spawn `regulatory-copy-editor` on the file with the lint output, then (3) spawn `quality-engineering` for the QA-conformance pass. Consolidate into one report with each stage's findings and a pass / pass-with-findings / fail verdict. For a **substantive** edit to a DHF/submission document, the QA stage is mandatory (per the binding rule).

### `copy-edit <file>`
Just stage 2 — spawn `regulatory-copy-editor` for a redline (no auto-apply; the agent returns proposed changes + a held-back list of edits that would touch substance).

### `help`
Show this usage guide.

## Subagent Delegation

| Scenario | Agent | Prompt file |
|----------|-------|-------------|
| Prose/clarity/consistency redline of a filed document | `regulatory-copy-editor` | `agents/regulatory-copy-editor.md` |
| QA-conformance of the edited document vs. its governing FORM | `quality-engineering` | (owned by `advisors`) |

## Dependencies

| File / tool | Required by | Purpose |
|-------------|-------------|---------|
| `project.yml` | `lint`, `setup` | filing-route signal (`dhfs[].filing`), team/ID patterns for lint parameterization, approved-skill/agent lists |
| `.taxonomy.yml` `governing_qms` | `check` (QA stage) | resolves the governing FORM/SOP/WI for the doctype |
| `python3` | `lint` | runs `authoring_lint.py` |
| project glossary / discovery index | `dependency-gated` lints | term-consistency (W8), trace-existence (D9) — flagged unverified when absent |

## Notes
- This skill owns **authoring quality only**. It composes with structure/scaffolding (`medtech-docs`), package assembly (`submissions`), and the QA-conformance pass — it never absorbs them.
- **Relationship to `writing-well`** (kept separate, not merged): `writing-well` is the general nonfiction-prose skill (Zinsser — voice, warmth, lead/ending, punch), tuned for blogs/articles/marketing/READMEs; its judgment layer is deliberately the *inverse* of the regulated register. `regulatory-authoring` reuses only `writing-well`'s mechanical `lint_prose.py` for the conflict-free universal tells (`clutter,nominalization,opener,length`) and keeps its own register/structure rules + `regulatory-copy-editor`. It does **not** adopt `writing-well`'s judgment layer or `prose-editor`.
- The standard is project-agnostic; project-specific examples, ID schemes, and QMS-mirror tooling live in a project-local appendix, never in this skill.
- If `$ARGUMENTS` is empty or "help", show the usage guide.
