# Red Team — Design & Architecture

This document describes the design behind the `red-team` skill. It is not loaded by Claude during normal operation — it exists for human understanding. For usage, see `SKILL.md`.

## Overview

`red-team` runs an **adversarial buyer-committee critique panel** over a prose document (whitepaper, blog, one-pager, thought-leadership brief). One skill fans out seven audience-skeptic agents — CEO, CFO, CTO, VP-Eng, RA-VP, QA-VP, PMO — each impersonating a senior decision-maker who has a reason to say no. Each skeptic grounds itself first via a for/against researcher, then reports where *that reader* stops believing. The skill consolidates all seven into one advisory report the human adjudicates finding-by-finding.

It answers a question no neighboring skill answers: **does the argument survive a hostile, senior reader.** Not *is it well written* (writing-well / prose-editor) and not *do the sources resolve* (reference-audit) — does the case hold.

## Lineage

Modeled structurally on the **`reference-audit`** skill: a thin orchestrator skill that owns an "engine" plus researcher subagents, fans out per-item, and consolidates findings into a report. Where reference-audit owns `citations` + three researchers and verifies *sources*, red-team owns seven persona skeptics + one researcher and critiques the *argument*.

The persona-grounded-by-researcher shape echoes the **`advisors`** skill (persona + grounding + structured findings), but red-team deliberately lives *outside* advisors: advisors are medtech-domain personas grounded in a project's DHF via three-tier canonical grounding; red-team's personas are archetypal enterprise *buyers* reacting to external content, with grounding *discovered per document*, not configured per project. Different grounding model, different runtime — hence a separate skill.

The advisory, never-blocking, "consume upstream first, then judge, propose-don't-impose" posture is shared with **`prose-editor`** (the `writing-well` judgment agent). red-team is the substance-analog of that prose-analog.

## Key Design Decisions

### Seven personas = the real buying committee, not the three content audiences

The project's content audiences (GTM/Sales, Marketing, Engineering) are *categories of reader*. The panel instead impersonates the *people who actually decide* on an enterprise/medtech purchase or sponsorship: economic buyers (CEO, CFO), technical buyers (CTO, VP-Eng), compliance buyers (RA-VP, QA-VP), and governance (PMO). Each has a distinct, predictable failure point — the value of the panel is that a CFO's objection is reliably different from a CTO's. The roster is fixed (not per-project) to keep the skill project-agnostic; `--personas` runs a subset.

### For/against grounding kills the hallucinated-objection failure mode

The central risk of any "critic" agent is inventing plausible-sounding objections to look busy. The `red-team-researcher` defends against this by gathering **both** supporting and opposing evidence before the skeptic forms an opinion. The skeptic concedes the ground the for-evidence covers and attacks only where the against-evidence (or an honest `intuition` flag) supports it. The `confidence: evidenced | intuition` field on every finding makes the distinction visible to the human.

### Grounding is discovered, never assumed

Documents vary: some ship with a `research/` kit, a claims register, and a references file; many are a bare markdown draft. The researcher's discovery step (Step 1) looks for grounding by *pattern* — the doc's own links, sibling `research`/`references`/`claims`/`evidence` material — and treats an empty result as valid, degrading to web-only and **saying so** in the report's "Grounding discovered" section. No filename is hardcoded; nothing is assumed to exist. This is what makes the skill work on any document, in any project.

### Shared discovery, per-persona evidence

The skill runs **one** discovery pass and hands the resulting `grounding_inputs[]` map to all seven skeptics, so the researchers don't each re-walk the filesystem. Each skeptic's researcher invocation then focuses on persona-tuned evidence-gathering (cost counter-data for the CFO, failure modes for the CTO) over that shared map plus the web. Cost scales with personas-run, not personas² .

### Report co-located with the source, never clobbered

Output lands at `<doc-dir>/<doc-slug>.red-team.md` — a sibling of the source, so it's discoverable next to the thing it critiques, and a single file (no folder, no folder-README ceremony). Because the **Verdict** column is the human's adjudication, `run` refuses to overwrite an existing report unless `--refresh` is passed — the same non-destructive posture reference-audit's `init` uses.

### Advisory, never editing, never blocking

The skill writes one report and stops. It never modifies the source document and registers no hooks — there is no "red-team on commit" gate, because an adversarial panel is inherently judgment-laden and noisy-by-design; forcing it into a blocking position would train people to ignore it. Run it on demand, after the prose is clean and before the doc meets the room.

## Dependencies

| File / dir | Required by | Purpose |
|------------|-------------|---------|
| `.claude/agents/` | `setup`, `run` | Install target for the 8 agent symlinks so the Agent tool can discover them |
| `agents/*.md` | `run` | The researcher + 7 persona skeptics (source of truth; symlinked into `.claude/agents/`) |
| `templates/red-team-report.md` | `run` | Output scaffold for the consolidated report |
| The target document | `run` | The prose doc being critiqued (read-only; never modified) |

No `project.yml` dependency, no hooks, no rules — the skill is fully project-agnostic and ships agents + one template only.

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill has SKILL.md | File exists at skill root | Required | shared |
| Frontmatter complete | name, description, version, updated all present | Required | shared |
| README.md exists | Design doc at skill root | Required | shared |
| Changelog current | Latest README changelog entry matches SKILL.md `version` | Required | shared |
| Agents symlinked | All 8 `agents/*.md` resolve from `.claude/agents/` after `setup` | Required | local |
| Project-agnostic | No project names / hardcoded grounding paths in SKILL.md or any agent | Required | shared |
| Personas are buyers, not advisors | RA-VP / QA-VP agents declare they are not the DHF-grounded project advisors | Recommended | local |
| Report is non-destructive | `run` refuses to overwrite an existing report without `--refresh` | Recommended | local |
| Advisory only | Skill registers no hooks and never edits the source document | Required | local |

## Changelog

- 1 (2026-06-25): Initial version — adversarial buyer-committee critique panel. One skill (`setup` / `run` / `help`) fans out 7 audience-skeptic agents (CEO, CFO, CTO, VP-Eng, RA-VP, QA-VP, PMO), each grounded by a `red-team-researcher` that discovers grounding inputs per-document (no assumed files, web fallback) and gathers for/against evidence. Consolidated advisory report grouped by persona with severity / passage / counter-evidence / suggested-fix / verdict columns and a confidence (evidenced|intuition) honesty flag. Advisory only, never edits the source, never blocks. Project-agnostic; reference-audit lineage.
