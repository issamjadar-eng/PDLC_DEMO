# 103 — Console Setup Tab — Connector (MCP) Configuration

**ID**: 103
**Created**: 2026-07-14
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
   - **when you tick a Todo off (or add/restructure Todos), fill/refresh the matching `## Economics` entry in the same edit** — the by-hand person-hours that unit would have taken, ranged + persona-tagged, per the rubric (if `## Economics` is present / usage-metrics is installed). **Checking the box is the estimate trigger** — don't defer it to a later checkpoint.
2. **Phase-end batching is OK; drift-batching is not.** Planned phases (e.g., "finish Phase 2, then log the whole phase at once") are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask. By then a crash or context-trim has lost the state. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.
6. **Estimation provenance (if `## Economics` is present).** This doc's `## Economics` block is the by-hand person-hour estimate, built per the effort-estimation rubric at `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (owned by the `usage-metrics` skill). To **add or refresh** an estimate on resume — even without loading the task skill — read that rubric first for the anchors, personas, and JSON schema; the block also carries a `method_ref` naming it. Skip silently if `usage-metrics` isn't installed. Point to the rubric, never copy it into this doc.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

Add a **Setup** section to the project console that projects the project's connector (MCP) configuration and — for supported connectors — lets users configure them from the browser.

- Surface all connector truth in one read-only view: `.mcp.json` server definitions, `project.yml security.approved_mcps` allowlist status, env-var requirements, and runtime health where cheaply checkable.
- Allow configuration of **supported** connectors via a curated, skill-shipped catalog (company-agnostic), with writes that keep `.mcp.json` and the `project.yml` allowlist in sync.
- Keep the console section a generic consumer per the established pattern (loader + router + template); no project-specific content in the skill package.

## Plan (Phase 0 — agreed design)

**New console section `console/setup/`** following the established loader + router + template pattern (per project-console SKILL.md §Where code lives; metrics section used as reference implementation).

Read model — three sources merged per connector:

| Source | Contributes |
|---|---|
| `.mcp.json` `mcpServers` | definition: type, command/args or url, env **keys** (values always masked) |
| `project.yml security.approved_mcps` | allowlist membership → approved flag |
| skill-shipped catalog (`console/setup/catalog.py`, company-agnostic) | "supported connectors" with config templates for the add/configure flow |

Status derivation: configured+approved → OK · configured-only → warning "not in security allowlist" · approved-only → info "approved but not installed". Plus cheap health probes: repo-relative command → exists/executable stat; bare command → `shutil.which`; env keys with empty values flagged.

Write model (supported-connector configure flow):
- `POST /setup/connectors/{name}` — add/update in `.mcp.json` **and** ensure the name in `project.yml approved_mcps` in the same operation (keeps the security allowlist in lockstep with installs, per project.yml security policy).
- `POST /setup/connectors/{name}/approval` — allowlist toggle only.
- `DELETE /setup/connectors/{name}` — remove from `.mcp.json` (allowlist row reported, not silently dropped).
- `project.yml` is edited **surgically line-wise** (never yaml.dump — would destroy comments); post-edit re-parse validates, restore-on-failure.
- Every write: timestamped backup under `tools/project-console/.data/setup-backups/` + append row to `.data/setup-audit.log`.
- Env var **values are not editable and never rendered** in v1 — keys + set/empty state only (secrets stay out of the browser).

UI (`/setup`): restart-required banner, per-connector cards with badges + probe results, approve/remove actions, "Add connector" panel driven by catalog templates + custom stdio/HTTP forms, masked raw `.mcp.json` drawer. Nav: unconditional Setup item, gear icon added to the sprite.

Out of scope v1 (recorded): editing env secret values from the browser; surfacing skills/agents/plugins allowlists (MCP connectors only); restarting/reloading MCP servers from the console (Claude Code owns the MCP lifecycle — the console only edits config).

<!-- STRATEGY CONTENT: architecture, operations — console Setup tab write-path design -->
**Strategy — connector configuration surface (architecture/operations).** Decision: the console Setup tab is allowed to **write** connector config, but only to the two files that already own that truth (`.mcp.json`, `project.yml security.approved_mcps`), always in lockstep, with per-write backups + an append-only audit log under `tools/project-console/.data/`. Rejected alternatives: (a) read-only projection with copy-paste instructions — fails the user's "configure from the console" goal; (b) console-owned connector store in `console.yaml` — would duplicate wiring that `.mcp.json` already encodes (violates audit-wiring rule); (c) yaml round-trip write to `project.yml` — destroys the file's extensive comments, so surgical line edits + re-parse validation instead. Secrets policy: env values are never rendered nor editable from the browser in v1.
<!-- /STRATEGY -->

## Todos

- [x] Phase 0 — plan drafted + design decisions recorded in this doc
- [x] Phase 1 — read-only Setup view: `console/setup/{loader,router}.py`, `setup_view.html`, nav wiring in `app.py` + `_base.html` (gear icon added to sprite)
- [x] Phase 2 — connector catalog (`console/setup/catalog.py`: chrome-devtools, file-locator, custom-stdio, custom-http) + per-connector status merge (configured/approved/probe/env-set)
- [x] Phase 3 — configure flow (`console/setup/writer.py` + POST/DELETE endpoints; `.mcp.json` + `project.yml approved_mcps` in lockstep; surgical comment-preserving yml edits; backups + audit log; env values never rendered/edited)
- [x] Phase 4 — skill 1.30.8 → 1.31.0 (VERSION, SKILL.md §Setup section, README changelog); 24/24 offline tests PASS; console restarted; `/setup` 200 + live data verified; no regressions on 5 other routes
- [ ] Phase 5 — user browser walkthrough of the Setup tab (approve/remove/add flows) — Claude verified via curl only
- [ ] Phase 6 — commit/push per git-workflow when user asks

## Open Questions

- Should the Setup tab also surface skills/agents/plugins allowlists (full `project.yml security` posture), or connectors (MCP) only for v1? Current plan: MCP-only v1, layout leaves room.
- Write scope: is browser-side editing of `project.yml` acceptable, or should v1 writes be limited to `.mcp.json` + a "pending approval" flag surfaced to the user? (Security-sensitive — see Strategy block.)

## Resume

### In-flight artifacts

- **Uncommitted** (nothing committed by Claude): new `console/setup/{__init__,catalog,loader,writer,router}.py` + `console/web/templates/setup_view.html`; edits to `console/app.py`, `console/web/templates/_base.html`, `SKILL.md`, `README.md`, `VERSION` (1.31.0) — all under `.claude/skills/project-console/`.
- Console left **running** on http://127.0.0.1:8765 (restarted via `start.sh` during verification).
- Offline test script at session scratchpad `test_setup_module.py` (24 assertions, all PASS) — transient, not in repo.
- Pre-existing unrelated dirty files in git status (trace-matrix, task 102 artifacts) — do not sweep into this task's commit.

### First action on resume

1. Ask the user to walk the Setup tab in the browser (http://127.0.0.1:8765/setup) — approve/remove/add flows write real config, so user-driven is safer.
2. On "push": commit **only** the project-console skill files + this task doc/index, then branch → PR → auto-merge per `.claude/rules/git-workflow.md`. Consider `/sync-skills push` upstream afterwards (registry-shared skill).
3. Activation: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 103`

## Economics

_By-hand person-hour estimate, **filled at checkpoint** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated; an empty `todos` list is ignored by the aggregator._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {"min": 0.5, "max": 1},
    "todos": [
      {
        "todo": "Read-only Setup view (loader + router + template + nav wiring)",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 6, "max": 10},
        "confidence": "med",
        "basis": "software anchor as sanity bound (~450 net LOC across loader/router/template) but internal-tooling web UI sits well below IEC 62304 rates — model judgment on the low multiplier"
      },
      {
        "todo": "Connector catalog + status merge model",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 2, "max": 4},
        "confidence": "med",
        "basis": "small data module + merge logic; model judgment"
      },
      {
        "todo": "Write path: lockstep .mcp.json + project.yml surgical edits, validation, backups, audit log",
        "personas": ["rd-lead", "cybersecurity"],
        "manual_hours": {"min": 8, "max": 14},
        "confidence": "med",
        "basis": "security-sensitive write path incl. comment-preserving yml editing + restore-on-failure + a peer security review of the endpoint surface; software anchor + judgment"
      },
      {
        "todo": "Version/docs + verification (24-assertion test script, restart, route smoke)",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 2, "max": 4},
        "confidence": "high",
        "basis": "test authoring + doc updates; software/test anchors, low end"
      }
    ]
  }
}
```

## Changelog

- 2026-07-14: Phases 0–4 delivered in one session. New console Setup section: `console/setup/{catalog,loader,writer,router}.py` + `setup_view.html` + nav/icon wiring (`app.py`, `_base.html`). project-console 1.30.8 → **1.31.0** (SKILL.md §"Topline section: Setup", README changelog). Verified: 24/24 offline assertions (comment-preservation on project.yml, secret masking, env-preserve-on-update, validation rejects, backups+audit) + live `GET /setup` 200 with both real connectors OK'd by probes + 5 sibling routes regression-free. Uncommitted. Remaining: user browser walkthrough, then push (+ candidate `/sync-skills push` upstream).
- 2026-07-14: Task created.

- 2026-07-14: Artifacts from this task (console/setup module, setup_view.html, app.py router mount — project-console 1.31.0) were found uncommitted in the worktree and committed via task 104's push (settings-shell redesign, 1.32.0, which builds directly on them). See tasks/ben/104-console-setup-redesign.md.
