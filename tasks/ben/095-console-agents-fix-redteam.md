# 095 — Project Console: Fix Cybersecurity Agent Error + Verify All Agents + Evaluate Red-Team Group

**ID**: 095
**Created**: 2026-06-29
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc: tick the relevant Todo checkbox, add a dated Changelog line naming the concrete artifact, update progress counts in Goals.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

_What this task aims to accomplish and why it matters to the project._

- **Fix the cybersecurity agent internal error** in the project console chat — it currently returns an internal error when selected.
- **Verify every agent in the console works** — enumerate the console's agent roster and confirm each loads + responds without error.
- **Evaluate adding the red-team agents as a group** — the `red-team` skill (pulled in ben/094) ships 7 skeptic personas + a researcher. Decide whether/how to surface them as a console agent group (panel), and wire it if approved.

## Todos

_Actionable work items. Check off as completed._

- [x] Read the console chat agent-loader contract (how console discovers + loads agents)
- [x] Reproduce / diagnose the cybersecurity agent internal error
- [x] Root-cause the cybersecurity failure
- [x] Verify all other console agents load without error — **found 2 more broken (human-factors, post-market)**
- [x] Fix the cybersecurity agent (+ the other two) — project files + skill templates
- [x] Harden `resolve_files` so a malformed glob can't 500 an agent
- [x] Evaluate red-team agents as a console group — recommendation captured; user directed to add them as first-class console agents + a new panel group
- [x] Wire the red-team group into the console — new `red-team/` group: 7 first-class skeptics + `red-team-panel`
- [x] Restart console + smoke-test (glob fix AND new group) — all green, no regression
- [x] Give all console agents the file-locator MCP tool (semantic search) — global, project-configurable
- [x] Give the red-team personas the `red-team-researcher` subagent (Task tool) — declarative, red-team-only
- [ ] Live-verify in browser: an agent calls file-locator; a red-team skeptic calls the researcher (needs OAuth chat turn — user to confirm)
- [ ] Push: project files + project-console skill changes (sources.py hardening, template glob fix, tool wiring) upstream via /sync-skills — pending user "push"
- [x] Fix `panels.py` PANEL_FRAMING — removed the hardcoded KOL/"clinical advisory panel"/PCA text; framing is now generic + each panel's own body is injected
- [x] Ship the red-team console group as skill *templates* (grouped template library) so every new project console gets it on init
- [x] Make init/sync group-aware, idempotent, non-clobbering, and guidance-emitting (so existing projects get fixes/new groups surfaced, not silently overwritten)

## Findings & Diagnosis

<!-- LESSONS LEARNED: tooling, glob-robustness -->
**Root cause.** Console domain agents declare grounding via `sources:` globs in their
frontmatter. `console/chat/sources.py::resolve_files` passes each pattern straight to
`pathlib.Path.glob()`. The cybersecurity agent's pattern
`docs/external/fda-guidance/**cybersecurity**.md` is invalid in pathlib — `**` must be
an *entire* path component, never adjacent to other characters — so `Path.glob()` raises
`ValueError: Invalid pattern: '**' can only be an entire path component`. The router's
`agent_stream` catches it into an SSE `error` event (the visible "internal error"), and
the chat-page render (`_agent_detail` → `resolve_files`) 500s outright. Reproduced in the
console's own venv (cpython-3.12.13).

**Scope was wider than reported.** A whole-roster resolve sweep (all 23 agents) found the
SAME bug in **three** agents — `cybersecurity`, `human-factors`, `post-market` — each with
a `docs/external/fda-guidance/**<topic>**.md` glob. Only cybersecurity had been noticed.
The bug also lived in the skill's agent **templates**
(`.claude/skills/project-console/agents/templates/{cybersecurity,human-factors,post-market}.md`),
so every new project `init` would reintroduce it.

**Fix (two layers).**
1. *Data* — replaced `**topic**` → `*topic*` (valid single-component glob) in all 3 project
   agent files AND all 3 skill templates. `fda-guidance/` is flat and holds only
   `cybersecurity.md`, so cybersecurity regains that file; human-factors/post-market match 0
   guidance files (harmless — they keep their other sources).
2. *Hardening* — `resolve_files` now wraps each `glob()` in `try/except ValueError`, skips a
   malformed pattern (stderr log), and grounds on the remaining valid patterns. One agent's
   glob typo can never again 500 the agent.

**Verification.** Post-fix roster sweep: all 23 agents resolve, FAILING: none. cybersecurity
3 files, human-factors 1, post-market 85. Synthetic-bad-glob hardening check passes.

**Why:** pathlib's `**`-must-be-a-whole-component rule is an easy trap when authoring
recursive-looking globs; a single bad pattern in declarative config should degrade
gracefully, not take down a feature.
**How to apply:** when a tool fans user/config-supplied glob strings into `Path.glob()`,
guard each pattern — a typo in data shouldn't crash the consumer.

## Strategy & Decisions

<!-- STRATEGY CONTENT: architecture, console-agent-roster vs red-team-workflow -->
**Red-team-as-console-group evaluation (grounded in `.claude/skills/red-team/SKILL.md`).**
Recommendation: **do NOT surface the red-team skeptics as a console chat-agent group.**
It's both a semantic and a runtime mismatch:

1. *Buyers, not advisors* (red-team SKILL.md L128). The console roster is **DHF-grounded
   program advisors** (RA/Clinical/Risk/QE/…) + KOLs. The red-team personas are **hostile
   external buyers** (CEO/CFO/CTO/VP-Eng/RA-VP/QA-VP/PMO) reacting to outward-facing prose.
   The skill explicitly warns the RA-VP/QA-VP skeptics are NOT the project's RA/QA advisors
   and must not be substituted.
2. *Different runtime.* Each skeptic (a) takes a **target document path** and critiques THAT
   doc, (b) grounds itself by dispatching the `red-team-researcher` **subagent** (Agent-tool
   fan-out) for for/against evidence, and (c) returns a structured `findings[]` contract that
   the skill consolidates into one report with a human **Verdict** column. The console chat
   runtime (`sdk_client.stream_response`) is single-shot streaming with **static file-glob
   grounding injected into the system prompt** — no Agent tool, no target-doc parameter, no
   structured-findings consolidation. Porting the personas to console chat would strip exactly
   what makes red-team valuable (researcher-grounded evidence) and reduce them to intuition-
   only free-association — the precise failure the skill's `confidence: evidenced|intuition`
   valve exists to prevent.

The faithful way to surface red-team in the console (if wanted) is **not** a chat group but a
**document-level action** — a button in the Documents/Submission view that triggers
`/red-team run <selected-doc>` and renders the resulting `<doc>.red-team.md` report. That
preserves the skill's workflow instead of faking its agents. Pending user direction (see Open
Questions) before building anything.

## Open Questions

- Should the red-team group be added to the console at all, given the red-team personas are **external-audience skeptics** (CEO/CFO/CTO/VP-Eng/etc. reacting to outward-facing prose), not DHF-grounded advisors like the existing console roster? Confirm intent with user.

## Red-Team Console Group (built per user direction)

User directed: add the red-team skeptics as **first-class console agents** (like R&D Lead / V&V Lead) **plus a new panel group** in the Agent view. Built under `tools/project-console/agents/red-team/`:

- `_group.md` — "Red Team", order 3 (after KOL=1, Core Team=2).
- 7 solo skeptics — `ceo/cfo/cto/vp-eng/ra-vp/qa-vp/pmo-skeptic.md`, console-shaped persona prompts adapted faithfully from `.claude/skills/red-team/agents/*.md` (kept each persona's *cares-about / stops-believing / voice*; replaced the CC-subagent runtime mechanics — researcher fan-out + `findings[]` contract — with console-chat behavior).
- `red-team-panel.md` — `kind: panel`, round-robin over all 7.
- Grounding: persona-appropriate **outward-facing narrative** (`project-overview.md` + the relevant `docs/project/strategies/*-strategy.md`) — what a hostile exec actually reads. Each persona file is explicit that the console has no for/against researcher, so it flags instinct-vs-evidence and points to `/red-team run <doc>` for an evidence-grounded, adjudicable findings report. RA-VP/QA-VP files explicitly disclaim being the project's RA/QA advisors (per red-team SKILL.md L128).

Verified live: `/agents` renders the Red Team group; all 8 pages HTTP 200; roster 23→31 agents.

## Console Agent Tooling (file-locator + researcher)

<!-- STRATEGY CONTENT: architecture, console-agent-tools -->
Before this work, console chat agents had exactly **one** tool: the in-process `read_files`
MCP tool (`sdk_client.py`), scoped to the docs grounding-roots. Per user direction, added two
capability seams, both **governed by the agent definition / project config** (not hardcoded —
keeps the `project-console` skill project-agnostic):

1. **file-locator MCP — every agent.** `sdk_client._external_mcp_servers()` reads the project's
   `.mcp.json`, resolves the server(s) named in `config.chat_mcp_servers` (console.yaml
   `chat.mcp_servers`, default `["file-locator"]`), absolutizes the launch command/args, and
   registers them with the SDK; `allowed_tools` gets `mcp__<server>` (all tools). Also set
   `ClaudeAgentOptions.cwd = repo_root` (the console runs from `tools/project-console/`, but the
   `.mcp.json` command is repo-root-relative). Absent server → silently skipped.
2. **red-team-researcher subagent — red-team only.** New `subagents:` field on the agent
   definition (`domain_agents.DomainAgent`). The 7 skeptics declare `subagents:
   [red-team-researcher]`; `sdk_client._load_subagent()` loads `.claude/agents/<name>.md` into an
   SDK `AgentDefinition` (carrying the researcher's own tools: Read/Glob/Grep/WebFetch/WebSearch),
   and the persona gets the `Task` tool to invoke it. Threaded through both the solo path
   (`router.py`) and the panel-member path (`panels.py`); the panel moderator pick runs lean
   (`enable_read_files=False, enable_file_locator=False`). Skeptic prompts updated: the
   "Be honest about evidence" bullet now says they CAN call the researcher.

Files changed: `console/chat/{sdk_client,domain_agents,router,panels}.py`, `console/config.py`,
+ the 7 red-team skeptic files (frontmatter `subagents` + prose) + `red-team-panel.md` (prose).

**Validated (no live API):** all wiring resolves; `ClaudeAgentOptions` constructs with the real
external-server config + `agents` + `Task`; file-locator command path exists; missing subagent →
`None`; console restarts clean; all pages 200; no regression. **NOT yet live-verified:** that an
agent actually *calls* file-locator / a skeptic actually *invokes* the researcher mid-chat —
needs an OAuth browser chat turn (will also spawn the file-locator server per turn — a few
seconds + memory each message; acceptable, note for later optimization).

## Templating + Idempotent Sync (propagation to sister projects)

Per user: ship the red-team group as skill **templates** so it propagates, and make `init`
idempotent + non-clobbering + **guiding** for existing projects. Done (project-console v1.28→1.29):

- **Grouped template library.** `agents/templates/` is now group-aware: each `templates/<group>/`
  dir → `agents/<group>/`; flat `*.md` still → `core-team` (back-compat). Added
  `agents/templates/red-team/` (9 files, copied from the project group). `scaffold.py`:
  `_iter_template_groups()` + `_materialize_agent_templates()`; `init` records a per-file baseline
  SHA in `manifest.agent_templates`.
- **Sync = 4-bucket guidance, never clobbers.** New → materialized; Update-available (project copy
  == recorded baseline, but template advanced) → reported, applied only with new
  `--apply-agent-updates`; Review-drift (customized OR pre-baseline & differs) → reported only,
  never overwritten; In-sync → silent. This is how the glob fix / new groups reach existing sister
  projects without trampling customizations.
- **Validated** in a temp project across 5 scenarios (fresh init, idempotent re-sync,
  pristine-outdated→update-available→apply, customized→never-clobbered-even-with-apply, missing
  group re-materialized). Ran live `sync` on THIS project: clean "No changes", 23 baselines
  recorded. All changed Python compiles.
- Docs: SKILL.md (template-library bullet, `init` grouped-template note, `sync` 4-bucket + flag,
  code-tree), README changelog 1.29.0, VERSION 1.29.0.

**Propagation summary (what a sister-project `/sync-skills pull` + `/project-console sync` yields):**
skill code fixes (hardening, panels, tooling) are live immediately; the **red-team group is
materialized as a new group**; the 3 corrected agent templates surface as *update-available* (their
existing copies are pristine-old) → apply with `--apply-agent-updates`, or leave customized ones for
manual review. Nothing project-owned is clobbered.

## Resume

**Activation command:** `bash .claude/hooks/task-activate.sh add <SESSION_ID> 095`

**Shipped + merged this session:**
- **Project** → PDLC_DEMO PR #70 merged to `main` (merge `5898c1c`; local main now at `f84fc23` after a CI index-rebuild commit).
- **Registry** → hitachi PR #238 squash-merged to registry `main` (`080ee9d`); project-console **v1.29.0** on hitachi. Local hitachi checkout reconciled; sync branch deleted. Recorded in `.claude/sync-log.md`.
- Console running on :8765 with all changes loaded.

**Only residual (user-side, not a blocker):** live in-browser smoke test that an agent actually *invokes* the file-locator tool and a red-team skeptic actually *calls* the researcher mid-chat — needs an authenticated chat turn, which can't be driven headless. Everything else is verified + merged.

**First action on resume:** nothing required — task is Complete. If the live smoke test surfaces an issue, reopen with `bash .claude/hooks/task-activate.sh add <SESSION_ID> 095`.

## Changelog

- 2026-06-29: Task created — fix console cybersecurity agent error, verify all console agents, evaluate red-team group.
- 2026-06-29: Root-caused the cybersecurity "internal error" — invalid pathlib glob `fda-guidance/**topic**.md` in the agent's `sources:`; reproduced `ValueError` in the console venv. Whole-roster sweep found 2 more broken the same way (human-factors, post-market). Fixed all 3 project agent files + 3 skill templates (`**topic**`→`*topic*`); hardened `console/chat/sources.py::resolve_files` to skip malformed globs. Post-fix: all 23 agents resolve; the 3 pages return HTTP 200 live. Console restarted on :8765.
- 2026-06-29: Per user direction, added the red-team skeptics as first-class console agents + a new **Red Team** panel group (`tools/project-console/agents/red-team/`: `_group.md` + 7 skeptics + `red-team-panel`). Faithful adaptation from the red-team skill agents into console-chat form; persona-appropriate outward-facing grounding. Verified: Red Team group renders in `/agents`, all 8 pages HTTP 200, roster 23→31, no regression. Nothing committed (awaiting user "push").
- 2026-06-29: Shipped the red-team group as skill **templates** + made init/sync group-aware, idempotent, non-clobbering, and guidance-emitting (project-console v1.28→v1.29). New `agents/templates/red-team/` group; `scaffold.py` group materialization + per-file baseline hashes in the manifest; `sync` 4-bucket classification (new/update-available/review-drift/in-sync) + `--apply-agent-updates` flag. Validated across 5 temp-project scenarios; live `sync` on this project clean (23 baselines). SKILL.md + README + VERSION updated. This is the propagation mechanism: sister projects get the new group materialized and the agent glob fixes surfaced as update-available, without clobbering customizations.
- 2026-06-29: Fixed `panels.py` panel-member framing bug. The hardcoded `PANEL_FRAMING` told **every** panel member they were on a "clinical advisory panel reviewing a PCA infusion device ... stay in character as the KOL below" — wrong for core-team + red-team, and project-specific (registry-guardrail violation). Replaced with a generic, project-agnostic `_panel_framing(panel)` wrapper (mechanics only) + injection of each panel's **own body** (`THIS PANEL: <title>`) + the member's persona (`YOUR ROLE`). Verified: red-team members get buyer-committee framing with zero clinical/KOL/PCA leakage; KOL members still get clinical framing (now from the KOL panel body); core-team gets its own. All 5 panel pages HTTP 200.
- 2026-06-29: Per user direction, gave console agents two new tools. (1) **file-locator MCP** for every agent — resolved from `.mcp.json` via `config.chat_mcp_servers`, command absolutized, `cwd=repo_root`; `mcp__<server>` allowed. (2) **red-team-researcher subagent** for the 7 skeptics only — new `subagents:` agent-def field → loaded into an SDK `AgentDefinition` + `Task` tool; threaded through router + panels. Skeptic/panel prose updated to reflect researcher access. Validated structurally (options construct, paths resolve, no regression, pages 200); live tool-use to be confirmed in-browser. Files: `console/chat/{sdk_client,domain_agents,router,panels}.py`, `console/config.py`, 7 skeptics + panel.
- 2026-06-30: **Pushed + skill-synced; task Complete.** Project work merged via PDLC_DEMO PR #70 (`5898c1c`). project-console skill (22 files, v1.28.0→v1.29.0) pushed to hitachi as PR #238, squash-merged (`080ee9d`); `check --analyzed` confirmed all 22 as clean push candidates (9 LOCAL_ONLY red-team templates + 13 LOCAL_AHEAD), no divergence. Hitachi checkout reconciled, sync branch deleted, `.claude/sync-log.md` updated. (Recovered cleanly from a post-merge hiccup: `gh pr merge --delete-branch` left local `main` stale because an auto-published untracked usage-metrics JSON blocked the fast-forward; moved it aside and ff'd main.) Residual: user-side live in-browser smoke test of tool-use.

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 10,
    "todos": [
      {
        "todo": "Console agents fix + Red-Team group",
        "personas": [
          "rd-lead",
          "cybersecurity"
        ],
        "manual_hours": {
          "min": 24,
          "max": 60
        },
        "confidence": "low",
        "basis": "cybersecurity-agent fix + Red-Team group + tooling + panels + templates"
      }
    ]
  }
}
```
