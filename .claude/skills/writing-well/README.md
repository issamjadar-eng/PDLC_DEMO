# Writing Well — Design & Architecture

This document describes the design decisions behind the `writing-well` skill. It is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Overview

`writing-well` is an opinionated prose-quality skill grounded in William Zinsser's *On Writing Well*. It helps a writer **draft**, **review**, and **copy-edit** nonfiction prose (markdown docs, whitepapers, articles, READMEs) toward Zinsser's standard: simplicity, clarity, brevity, and humanity. Strip every sentence to its cleanest components; clutter is the disease; rewriting is the cure.

The skill's central design insight comes straight from the book: prose problems split cleanly into **mechanical** (a machine can find them) and **judgment** (only a reader can). That split *is* the architecture — a deterministic linter handles the mechanical layer, an LLM agent handles the judgment layer, and a shared reference doc grounds both.

It is **standalone and project-agnostic** — it works on any markdown, not only `public-doc` drafts — and **composable**: `public-doc` (which owns brand / house-style / internal-leak checks) can call `writing-well` for sentence-level prose quality without duplication.

## Three layers

| Layer | Mechanism | Catches | Cost |
|-------|-----------|---------|------|
| **Guidance** | `references/zinsser-principles.md` | The standard itself — what good prose is, and why | Loaded as needed |
| **Linter** | `scripts/lint_prose.py` (deterministic, no LLM) | Mechanical tells: clutter phrases, qualifiers/hedges, passive voice, nominalizations, `-ly` adverbs, weak verb+noun, `there is/it is` openers, sentence/paragraph length, clichés | Cheap, fast, CI-able |
| **Judgment** | `prose-editor` subagent | What a script can't: rhythm (read-aloud), voice/warmth, the lead and the ending, structure, one-idea-per-paragraph, "does this trust the reader" | LLM pass |

The linter is the cheap first pass; the agent consumes the linter's output, then does the human-judgment pass on top. Neither is sufficient alone — that's why the linter is **script + agent**, not one or the other.

## Actions

| Action | What it does | Edits the file? |
|--------|--------------|-----------------|
| `lint <file>` | Deterministic script only — fast, no LLM. Flags + suggestions + severity. **Advisory, never blocks.** | No |
| `review <file>` | Linter pass + agent critique → structured findings report (cut-this-and-why). | No |
| `copyedit <file>` | Linter + agent revise the prose → **propose a diff plus a short "what I cut and why"** so the author learns the moves. Author applies once happy. | Proposes; applies on approval |
| `draft <brief>` | Generate new prose from an outline/brief, written to the principles from the start. | Writes a new file |
| `setup` | Symlink the `prose-editor` agent into `.claude/agents/`. Idempotent. | n/a |

## Key Design Decisions

### Linter = deterministic script *and* judgment agent (not one or the other)

A pure script is reproducible and CI-friendly but deaf to rhythm, voice, and structure — the things Zinsser cares about most. A pure agent catches nuance but is non-deterministic, slow, and useless in CI. Splitting along the mechanical/judgment seam gives both: a cheap reproducible pass for the clutter that's mechanical, and a reader's-ear pass for what's judgment. The agent reads the script's output first so it never re-flags the mechanical stuff and spends its budget on what only it can see.

### Advisory, never blocking

Zinsser is opinionated toward plain nonfiction, but this repo's content spans Marketing (wants punch), Engineering (wants precision), and GTM. A linter that *blocks* would be wrong for half of it. Every finding is a suggestion with a severity; the author decides. This matches `public-doc`'s "advisory, never blocks" stance so the two feel like one body of work. (CI-strict mode is opt-in via `--strict`.)

### Copyedit proposes a diff + rationale, instead of rewriting silently

The point of the book is to *teach* the writer to self-edit. A silent rewrite hides the lesson. Proposing a diff with a one-line "cut 'at this point in time' → 'now' (clutter)" turns every edit into a worked example, so the author internalizes the moves and needs the skill less over time.

### Standalone + composable with `public-doc` (no fold-in, no duplication)

`public-doc`'s `lint_doc.py` covers brand / house-style / internal-leak — a project-config word list, not prose analysis. Folding Zinsser into it would (a) lock prose-quality to `public-doc` drafts only, and (b) bloat a skill with a different job. Instead `writing-well` stands alone and works on any markdown; `public-doc` can shell out to `writing-well lint` for sentence-level quality while keeping its own checks. The cliché / banned-word list can be shared rather than copied.

### Project-agnostic

No project names, devices, or task IDs in the skill or the bundled agent. The principles and the linter rules are universal; any project from the registry can use it unchanged.

### No verbatim copyrighted text

The reference doc paraphrases Zinsser's principles into operating rules in our own words. It does not bundle quoted passages from the book. The ideas (simplicity, clutter, the audience, active verbs) are not copyrightable; the expression is — so we re-express.

## Linter rule set (v1)

Each rule emits `file:line:col`, the matched text, a suggested fix, and a severity tag (`clutter` / `hedge` / `passive` / `nominalization` / `adverb` / `weak-verb` / `opener` / `length` / `cliche`). Output is human-readable by default, `--json` for machines, `--max-len N` to tune the sentence-length flag. Exit code is non-zero only with `--strict` (for opt-in CI); default exit 0 (advisory).

- **Clutter dictionary** — curated phrase→replacement map ("in order to"→"to", "due to the fact that"→"because", "at this point in time"→"now", "in the event that"→"if", "a large number of"→"many").
- **Qualifiers / hedges** — `very, rather, quite, sort of, kind of, a bit, pretty, really, somewhat, I think, it seems, in a sense`.
- **Passive voice** — be-verb + past participle heuristic (`was decided`, `is being reviewed`).
- **Nominalizations** — a curated phrase dictionary of verb-hidden-in-noun patterns ("make a decision"→"decide", "provide assistance"→"help", "has a dependency on"→"depends on"). (Dictionary-based, not a `-tion/-ment` density metric — bare suffixes are too common to flag without false positives.)
- **Adverbs** — `-ly` adverbs, especially adjacent to strong verbs ("shouted loudly").
- **Weak verb + abstract noun** — `is/are/has/make/give/provide` + noun where a verb exists.
- **Empty openers** — `There is/are…`, `It is … that…`.
- **Length** — sentences over N words (default 30); very long paragraphs.
- **Clichés** — configurable list (shareable with `public-doc`).

These are heuristics, not truth — every flag is a prompt to look, not a verdict. The reference doc explains the *why* so a flag teaches rather than nags. Code fences, YAML frontmatter, inline code, and link URLs are skipped so the linter only sees prose.

## Dependencies

| File | Required by | Purpose |
|------|-------------|---------|
| `references/zinsser-principles.md` | `review`, `copyedit`, `draft`, the agent | The standard — grounds every judgment pass |
| `scripts/lint_prose.py` | `lint`, `review`, `copyedit` | Deterministic mechanical pass |
| `agents/prose-editor.md` | `review`, `copyedit`, `draft` | Judgment pass; symlinked into `.claude/agents/` by `setup` |
| `.claude/agents/prose-editor.md` (symlink) | Claude Code subagent discovery | Lets the agent be delegated to from the main loop |

Optional composition: `public-doc`'s `lint_doc.py` may invoke `scripts/lint_prose.py` for sentence-level quality. No hard dependency in either direction.

## Lineage

Original skill, not adapted from a prior version. Principles distilled from William Zinsser, *On Writing Well* (paraphrased into operating rules — no verbatim copyrighted text is bundled). Structurally it follows this repo's conventions and borrows the "advisory, config-driven, never-blocks" linter posture from the `public-doc` skill.

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill has SKILL.md | File exists at skill root | Required | shared |
| Frontmatter complete | name, description, version, updated all present | Required | shared |
| README.md exists | Design doc at skill root | Required | shared |
| Changelog current | Latest entry matches version number | Required | shared |
| Linter runs standalone | `python scripts/lint_prose.py <file>` exits cleanly with no LLM | Required | local |
| Linter is advisory by default | Default exit code 0; non-zero only under `--strict` | Required | local |
| Agent symlinked | `setup` creates `.claude/agents/prose-editor.md` → skill source | Recommended | local |
| No verbatim Zinsser text | `references/zinsser-principles.md` paraphrases; no quoted passages | Required | local |
| Project-agnostic | No project names / device codenames / task IDs in skill or agent | Required | shared |

## Changelog

- 3 (2026-06-25): Added an **AI-tells / "slop" detector** — `scripts/lint_slop.py` + the `slop` action. A second deterministic, no-LLM linter that flags fingerprints of un-edited LLM output: **em-dash density** (per 1k words; human norm ~3.2, flag >7), **academic excess-vocabulary** (delve/underscore/meticulous/tapestry…, density-gated so single words don't fire), **puffery & antithesis constructions** ("serves as a testament to", "it's not just X — it's Y"), **stock openers**, **clustered signposts**, **`**Bold:**` colon-lists**, smart-quotes, emoji headers, and sentence-length burstiness. Grounded in the Kobak/Liang excess-word studies + the em-dash-density preprint; `--folklore` opt-in for the unvalidated vendor-blog word tier. Built-in caveats (probabilistic, combinatorial, non-native-writer false-positive bias) printed on every run; advisory only. Skips frontmatter/code/links/tables + a trailing References section. Self-tests added (`tests/test_slop.py`, wired into `run_tests.sh`).
- 2 (2026-06-25): Linter precision pass. Expanded `PASSIVE_FALSE` with emotive/stative participles ("thrilled", "married", "satisfied", …) and color/material adjectives ("golden", "wooden", "green", …) so predicate adjectives after a be-verb stop mis-flagging as passive — the highest-volume tag, where false positives were training readers to ignore it. Implemented the long-advertised "has a dependency on → depends on" catch (added to the nominalization dictionary). Corrected the README nominalization claim to describe the actual dictionary approach rather than a non-existent `-tion/-ment` density metric (spec now matches code). Added `lively`/`unwieldy`/`measly`/`homely` to `ADVERB_FALSE`. Self-tests extended + passing.
- 1 (2026-06-25): Initial design — three-layer prose-quality skill (guidance reference + deterministic `lint_prose.py` + `prose-editor` judgment agent); actions `lint` / `review` / `copyedit` / `draft` / `setup`; copyedit proposes a diff + rationale; standalone and composable with `public-doc`.
