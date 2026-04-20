# ben/021 — Digest CHANGELOG readable format

**ID**: 021
**Created**: 2026-04-20
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## Goals

Make the project `CHANGELOG.md` lead with reader-friendly prose. Relegate the task ref, commit SHA, author, and date to a muted trace footer. Ship both a zero-cost mechanical mode (commit body extraction) and an opt-in `--llm` mode (batched `claude -p` call) for polished summaries on historical jargon-heavy commits.

Motivation: v1 of `/digest log` produced an audit-trail-precise but newcomer-hostile CHANGELOG. User flagged that `task ben/018: sync-skills pull (53 files) + close 16 Required FAILs` reads as release notes for a tool non-team members don't know exists. Should read: "Pulled 53 skill updates from the team's shared registry and cleaned up 16 structural issues in the docs."

## Design decisions

**Format per item:**
```
- **<plain-English headline>**
  <optional plain-English body>
  _<person/NNN> · `<short-sha>` · <author> · <date>_
```

**Source of readable text:**
- Default (zero cost): first paragraph of commit body with trailers stripped (`Co-Authored-By:`, `Signed-off-by:`, etc.); falls back to cleaned-up subject (strip `task NNN:` prefix, capitalize) if no body
- `--llm`: batched `claude -p --model haiku --output-format json` call with ALL commits in one user message — returns a JSON array of `{sha, headline, body}` objects. One cache-creation cost total instead of N. Cache results at `.claude/state/digest-llm-cache.json` keyed on sha so incremental runs don't re-burn tokens.

**When --llm is auto-used:**
- Retrospective first run (`--retrospective`) — polishes the historical baseline
- User-requested via explicit `--llm` on incremental runs

**Why claude -p + haiku:**
- No `anthropic` SDK install needed (auth via existing OAuth on `claude` CLI)
- Haiku 4.5 is cheapest and fast enough for rewriting — small batch of simple rewrites
- Batch-in-one-call amortizes the ~$0.10 session cache-creation cost across all commits

## Todos

- [x] Update `build_changelog.py` with mechanical extraction (commit body + clean subject), batched LLM summarization via `claude -p`, per-SHA cache, new bold-headline/body/trace format, `--llm` and `--no-llm` flags
- [x] Regenerate CHANGELOG.md retrospective with `--llm` (35 commits, one batched call)
- [x] Bump digest to v4, VERSION 1.3.0, post-update annotation in SKILL.md changelog
- [x] Verify format renders correctly

## Outcome

Project CHANGELOG now leads with plain-English readable summaries; task refs / SHAs / dates live in a muted trace footer. Both paths work:

- **Default (mechanical):** extracts the first paragraph of each commit's body, strips trailers (Co-Authored-By, Signed-off-by, etc.), cleans the subject as a fallback when the body is empty. Free, deterministic, good quality for commits with bodies.
- **`--llm` (opt-in, auto on `--retrospective`):** batches all significant commits into one `claude -p --model haiku` call. Returns JSON array of `{sha, headline, body}`. Cached per-SHA at `.claude/state/digest-llm-cache.json` so incremental runs don't re-summarize. ~$0.10 total for a 35-commit retrospective.

Critical discovery: `claude -p` invoked from inside the project picked up CLAUDE.md (62k tokens) and ran Stop hooks (which tried to enforce capture-discipline on the LLM invocation itself — the model "replied" to the hook instead of returning JSON). Fix: run claude with `cwd=/tmp` and `CLAUDE_*` env vars stripped. Keeps the sub-invocation clean.

Before/after example from ben/018:

_Before:_ `task ben/018: sync-skills pull (53 files) + close 16 Required FAILs`

_After:_ **Updated project tools and fixed all regulatory compliance documentation gaps.** — _Imported 53 skill updates and backfilled missing documentation stubs across the DHF._

<!-- STRATEGY CONTENT: architecture, llm-invocation-isolation, cost-control -->

**Strategy — Run LLM sub-invocations outside the project context to keep them predictable.**

Principle: When a skill invokes `claude -p` as a sub-call for text transformation (summarization, rewriting, classification), run it with a neutral working directory (`/tmp`) and strip `CLAUDE_*` env vars. The user's project context — CLAUDE.md, skills, hooks — is for *their* session, not for programmatic sub-invocations. Mixing them contaminates the sub-call's context (huge input tokens) and causes hooks to fire against the sub-invocation (which the LLM then responds to instead of the actual prompt).

Why: Claude Code's CLI discovers context by walking up from `cwd`. A pure text-in / JSON-out invocation doesn't need that context; in fact, loading it wastes tokens (~$0.09 of cache creation per call here) AND creates correctness hazards when hooks try to enforce behavior on the sub-call. Isolating via `cwd=/tmp` + stripped env is a single-line change that fixes both problems.

How to apply: Any skill that shells out to `claude -p` for a programmatic purpose — summarization, classification, structured extraction — should:
1. Set `cwd` to `/tmp` (or any neutral directory)
2. Strip `CLAUDE_*` from the subprocess env (keep PATH, HOME, and other essentials)
3. Always use `--system-prompt` to override the default (which otherwise loads CLAUDE.md from cwd)
4. Use `--no-session-persistence` and `--disable-slash-commands` as belt-and-suspenders

Conversely: if the skill WANTS the user's context (e.g., asking Claude to review the project's current state), invoke from the project dir normally. The two modes are intentionally different.

<!-- LESSONS LEARNED: claude-cli-invocation, context-pollution, hooks-cross-talk -->

**Lesson — `claude -p` from inside the project is not a pure LLM call.**

Why: First attempt ran `claude -p` from the project directory. The CLI loaded CLAUDE.md (62k tokens cached per invocation), ran SessionStart hooks, and at Stop time triggered the capture-check hook which complained about missing strategy/lessons content in the active task. The LLM — which had been asked to return JSON summaries — instead responded to the hook's blocking message: "✓ Updated to exact required phrasing. Task 021 now has a dated 'No strategy/lessons content this session.' line in the changelog." It actually wrote to the task file.

Takeaway: Hooks fire during ALL claude sessions by default, including programmatic `-p` sub-invocations. `--disable-slash-commands` does not disable hooks. `--bare` does, but requires an API key. The cheap general-purpose workaround is `cwd=/tmp` + stripped env, which puts the sub-call outside the project tree so hooks don't register.

## Changelog

- 2026-04-20: Task created
- 2026-04-20: Digest v4 / VERSION 1.3.0 shipped. Retrospective CHANGELOG regenerated with readable format. Strategy + Lessons captured about isolating `claude -p` sub-invocations from project context.
