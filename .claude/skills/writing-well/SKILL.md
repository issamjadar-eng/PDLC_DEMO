---
name: writing-well
description: "Improve the PROSE QUALITY of existing nonfiction writing — tighten it, cut the clutter, make it clearer, punchier, more readable. Grounded in Zinsser's *On Writing Well*: simplicity, clarity, brevity, humanity. Use when the user wants to lint / review / copy-edit / tighten / sharpen / proofread / 'make this clearer' / 'cut the fluff' / 'is this well written' / 'too wordy' / 'too passive' / 'remove jargon' / 'edit my writing' on any markdown or text — whitepaper sections, articles, READMEs, docs, emails. Runs a deterministic no-LLM linter for mechanical tells (clutter phrases, hedges, passive voice, nominalizations, -ly adverbs, weak verbs, empty openers, sentence length, clichés) plus a judgment agent for rhythm / voice / lead / ending / structure. Advisory, never blocks; standalone and project-agnostic. NOT for authoring/publishing a new external doc end-to-end, brand/house-style, internal-leak stripping, or PDF rendering — that's public-doc. NOT for slides/decks — that's md-deck / frontend-slides / pptx. This skill sharpens prose; it does not manage documents or produce artifacts."
version: 2
updated: 2026-06-25
---

# Writing Well — Prose Quality

Sharpen nonfiction prose toward William Zinsser's standard: **strip every sentence to its
cleanest components, then trust the reader.** Simplicity, clarity, brevity, humanity.

The skill's architecture follows the book's own split between problems a **machine** can
find and problems only a **reader** can hear:

- **Mechanical layer** — `scripts/lint_prose.py`, a deterministic, no-LLM linter. Cheap,
  fast, reproducible, CI-able. Finds clutter phrases, hedges, passive voice,
  nominalizations, -ly adverbs, weak verb+noun, empty openers, length, clichés.
- **Judgment layer** — the `prose-editor` agent. Reads the linter's output first, then does
  what a script can't: rhythm, voice, the lead and the ending, structure, trust in the reader.
- **Guidance** — `references/zinsser-principles.md`, the operating rules both layers appeal
  to (paraphrased — no verbatim copyrighted text).

**Advisory, never blocks.** Every finding is a prompt to look, not a verdict; the author
always decides. **Standalone and project-agnostic** — works on any markdown, not only
`public-doc` drafts. **Composable** — `public-doc` (brand / house-style / internal-leak)
can call `writing-well lint` for sentence-level quality without duplication.

For the design rationale, see `README.md`.

## Supporting Files

| File | Purpose |
|------|---------|
| `README.md` | Design document — decisions, three-layer rationale, linter rule set, lineage, Best Practices, Changelog |
| `scripts/lint_prose.py` | Deterministic no-LLM linter (mechanical pass). `--json`, `--max-len N`, `--max-para N`, `--strict`, `--only TAG,…`, `--no-color` |
| `references/zinsser-principles.md` | The standard, paraphrased into operating rules — grounds every judgment pass |
| `agents/prose-editor.md` | Judgment-pass subagent; consumes linter output. Symlinked into `.claude/agents/` by `setup` |
| `tests/run_tests.sh` | Self-test of the linter against fixtures (mechanical tells + skip-zones) |

## Actions

Parse the user's argument string `$ARGUMENTS` to determine the action. If empty or "help",
show the actions below. **All commands below assume the current directory is the repo
root** (paths are repo-relative).

### `lint <file>`

Deterministic script only — fast, no LLM, no agent. The cheapest pass.

```bash
python3 .claude/skills/writing-well/scripts/lint_prose.py <file>
# flags: --max-len 25 (stricter length), --only clutter,hedge (subset),
#        --json (machine), --strict (exit non-zero if any finding — opt-in CI gate)
```

The script skips YAML frontmatter, fenced/indented code, inline code, link URLs, and
markdown tables so it only ever sees prose. Summarize the findings for the user grouped by
tag, and offer to fix the high-value ones. **Exit code is 0 by default** — lint is
advisory. Only `--strict` makes it non-zero.

### `review <file>`

Linter pass **+** the `prose-editor` agent's judgment pass → a structured findings report.

1. Run the linter and capture its JSON:
   ```bash
   python3 .claude/skills/writing-well/scripts/lint_prose.py <file> --json --no-color
   ```
2. Hand off to the `prose-editor` judgment pass. **Default path (always works):** read
   `agents/prose-editor.md` and act as that agent. **Optimization (only after `setup` + a
   session reload registers the subagent type):** delegate via the Agent tool with
   `subagent_type: prose-editor`. Either way, give the agent the **file path** and the
   **linter JSON** (embed the JSON in the delegation prompt, or write it to a temp file and
   pass the path) so it doesn't re-flag mechanical tells.
3. Present the agent's report: findings grouped by leverage (Lead / Structure / Rhythm /
   Voice / Trust / Ending), each naming where, what, the fix, and the principle — plus the
   single highest-leverage change and what the piece already does well. **No edits made.**

### `copyedit <file>`

Linter + agent **propose a diff** to tighten the prose, plus a short "what I cut and why" so
the author learns the moves. **Does not apply silently.**

1. Run the linter (the `--json --no-color` command from `review`, step 1).
2. Hand off to `prose-editor` in `copyedit` mode (same default-path / optimization choice as
   `review` step 2) with the file path + linter JSON.
3. Present the proposed before/after edits (each with a one-line *why* that teaches the
   move), the full revised text or a unified diff, and the "what I cut and why" summary.
4. **Apply only on the author's approval** — then write the file. Teaching the cut is the
   point; a silent rewrite hides the lesson.

### `draft <brief>`

Generate new prose from an outline/brief, written to the principles from the start (strong
verbs, no clutter, a real lead, one idea per paragraph). Read
`references/zinsser-principles.md` first, draft, then self-lint with the linter before
handing over. Optionally run one `review`-mode self-check through `prose-editor` (the same
handoff as `review` step 2) to catch rhythm/structure issues the linter can't. Write to a
path agreed with the user.

### `setup`

Symlink the `prose-editor` agent into `.claude/agents/` so Claude Code can delegate to it.
Idempotent.

```bash
mkdir -p .claude/agents
ln -sf ../skills/writing-well/agents/prose-editor.md \
       .claude/agents/prose-editor.md
```

(Use a relative symlink target so the link survives a repo move/clone. Report whether the
link was created or already present; never clobber a real file at that path — if
`.claude/agents/prose-editor.md` exists and is not a symlink to this skill, stop and tell
the user.)

## Composition with `public-doc`

`public-doc` owns brand, house-style, internal-leak, and PDF rendering. `writing-well` owns
sentence-level prose quality. They do not overlap. When authoring a `public-doc` draft and
the user wants the prose itself tightened, run `writing-well lint`/`review`/`copyedit` on
the draft — the two skills compose, neither folds into the other. The cliché / clutter word
lists are shareable rather than duplicated.

## Notes

- If `$ARGUMENTS` is empty or "help", show the actions above.
- The linter is heuristic — every flag is a prompt to look, not a verdict. Say so when
  presenting results, so a flag teaches rather than nags.
- Respect the medium: Marketing wants punch, Engineering wants precision. The principles are
  defaults to reason from, not rules to apply blindly. Never present an edit as mandatory.
