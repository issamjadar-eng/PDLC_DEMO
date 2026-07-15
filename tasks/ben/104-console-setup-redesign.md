# 104 — Console Setup Section Redesign (beyond MCP servers, professional design)

**ID**: 104
**Created**: 2026-07-14
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

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

Rebuild the project console's **Setup** section from an MCP-connectors-only page into a full, professional project-settings surface, using Claude Desktop's Settings → Connectors page as the design reference (user-provided screenshot 2026-07-14: left settings nav with grouped sections, search, "Popular" card row, clean list with Type/Status columns, Connect buttons, Add menu).

- Goal 1: **Scope** — Setup covers the project's whole tool surface, not just MCP servers: connectors (MCP), skills, agents, plugins, rules/hooks, team & security posture — each cross-checked against `project.yml security.approved_*` allowlists (installed-vs-approved status, like the secops audit).
- Goal 2: **Design** — professional settings IA + visual quality matching the reference: sectioned left nav, status badges, consistent tables/cards, search/filter.
- Goal 3: Skill-conformant delivery — changes land in the `project-console` skill scaffold (registry-shared), synced into `tools/project-console/`, version-bumped, browser-verified.

## Todos

_Actionable work items. Check off as completed._

- [x] Read contracts: `project-console` SKILL.md v1.31.0 end-to-end, `console/setup/{router,loader}.py` (+catalog/writer roles), `_base.html` nav, `project.yml` shapes (security.approved_* lists, registries[], team.active[]); skill-creator + frontend-design skills loaded
- [x] Design the Setup IA (see Strategy block)

## Strategy

<!-- STRATEGY CONTENT: architecture, console-setup-ia, settings-surface -->
**Decision — console Setup IA (2026-07-14):** Setup becomes a settings shell (Claude Desktop Settings reference): an inner left sidebar with six sections — **Connectors** (existing MCP model, keeps all write paths), **Skills**, **Agents**, **Plugins**, **Rules & Hooks**, **Team & Security** — each a read-only installed-vs-approved status view over `project.yml security.approved_*` + the corresponding install surface (`.claude/skills/*/`+VERSION+frontmatter, `.claude/agents/*.md` symlink-owner resolution, `.claude/rules/*.md`, `.claude/settings.json` hooks, `team.active[]`, `registries[]`). Client-side hash routing (`#connectors` … `#team`), per-section search filter, one Jinja template. Only Connectors is editable — skills/agents editing stays in `/sync-skills` domain (console is a config viewer + MCP config editor, not a package manager). Status triad reused everywhere: installed+approved ✓ / installed-unapproved ⚠ (posture check would flag) / approved-not-installed ℹ.
**Why:** project.yml already defines the full tool-surface taxonomy (approved_skills/mcps/plugins/agents); the connectors-only page surfaced 1 of 5 allowlists. Reusing the loader's defensive merged-status pattern per section keeps the security-posture semantics identical across surfaces. Read-only for non-MCP sections avoids duplicating sync-skills' merge logic behind a browser button.
**How to apply:** new sections = new loader function + sidebar entry + section block in `setup_view.html`; keep loaders defensive (missing file → empty + warning, never raise); skill stays project-agnostic — everything read at runtime from project.yml/.claude.
- [x] Implement loaders: `console/setup/loader.py` +5 section loaders (`load_skills/agents/plugins/rules_hooks/team_security`) + `load_setup()` aggregate; router passes aggregate, `/setup/data` returns it; all defensive, exercised against real project (35 skills, 31 agents, 12 rules, 12 hooks, 5 members)
- [x] Redesign `setup_view.html` — settings shell (220px inner sidebar + content pane), hash routing, per-section search, catalog "Popular" cards, list rows Name|Type|Status with expandable connector detail, posture tiles; theme-token-driven, `.setup-body main` widened to 1280px, collapse breakpoint 720px (was hit at user's 150% zoom → 852px viewport); `_base.html` nav title updated
- [x] Restart + browser-verify: all 6 sections render (Chrome, 0 console errors); no `/project-console sync` needed — console imports skill code via PYTHONPATH, `run.sh`/`start.sh` unchanged
- [x] Version bump 1.31.0→1.32.0 (SKILL.md frontmatter + VERSION) + README changelog entry + SKILL.md Setup-section doc rewritten (section table, read-only rationale)
- [x] Row-detail expansion for Skills / Agents / Rules & Hooks (user follow-up): loaders carry full description, paths, symlink targets, skill component-dir surface, agent tools/model, rule title+summary, hook full command; template rows clickable with namespaced ids (cx-/sk-/ag-/ru-/hk-)
- [x] Agents section covers BOTH surfaces: top-level `.claude/agents/` + skill-bundled `.claude/skills/*/agents/` (49 total); bundled agents inherit approval from their owning approved skill (semantic decision — see Strategy); resolved the tier1-enricher/tier1-restructure question (they exist, bundled in dhf-manifest, now displayed as such)
- [x] Backfilled `project.yml security.approved_agents`: +14 `advisors/agents/*` entries (17→31); agents board fully ✓ (49 ok / 0 warning)
- [x] Update task doc + index; push per git-workflow (user requested) — PR #101 (`293895c`)
- [x] Agent summaries (user follow-up): 21 agents had none — two root causes fixed in `_frontmatter`: YAML-hostile prose descriptions (unquoted `: ` → safe_load error → tolerant line-parser fallback) and frontmatter-less prompt files (→ first-body-paragraph fallback). All 49 agents now carry summaries
- [x] Registries section (user follow-up): registry roster + local-clone catalog vs installed (not-installed/update/current/local-ahead), filter, Add + Update buttons. `writer.install_skill` (copy-install + lockstep `approved_skills` allowlist; strictly-newer downgrade guard; whole-dir backup on update; audited) + `POST /setup/skills/{name}/install` (registry resolved by name server-side). Unit-tested all 4 paths in scratch repo. Live data: hitachi 33 current / sync-skills update 8.3→8.4 (button) / project-console local-ahead (no button — downgrade prevented)
- [x] Automation section (user follow-up): renamed from Rules & Hooks; adds GitHub-workflows table — name, humanized `on:` triggers (incl. YAML-1.1 `on`→True quirk), jobs, leading-comment description, owning skill resolved by filename mention in skill trees (both real workflows attribute correctly: file-locator, usage-metrics)
- [x] project-console 1.33.0: VERSION + README changelog + SKILL.md section table; browser-verified (filter, buttons, workflow rows)
- [x] Push follow-up batch — PR #102 (origin/main `7bad421`)
- [x] Agent-description gap round 2 (user report 2026-07-15: "agent view still missing descriptions"): the 1.33.0 body-summary fallback was only wired for top-level agents — 13/49 **bundled** agents (docflow ×8, skill-creator ×3, strategy ×2, all frontmatter-less prompt files) rendered empty. Fixed `load_agents` bundled loop to use the same `fm description → _body_summary` fallback, and `_body_summary` now joins the full first prose paragraph (hard-wrapped lines were cut mid-sentence, e.g. interpret_image "…and produce its"). Verified live: `/setup/data` serves 49/49 with descriptions after `start.sh` restart. project-console 1.33.0→1.33.1 (VERSION, SKILL.md, README changelog w/ Post-update note)
- [x] Adoption verification (user ask): new setup code audited project-agnostic (0 project-name hits); **Post-update** adoption notes added to the 1.31.0/1.32.0/1.33.0 changelog entries per the sync-skills Step-5b convention; pushed upstream to hitachi as PR #267 (squash-merged `6f5464c`, clone ff'd, branch pruned) — sister projects adopt via `/sync-skills pull` + console restart. Anthropic-registry question answered: builtin = docx/pptx/xlsx/pdf; public `anthropics/skills` repo has 17 (11 not yet adapted here). Open pull candidate: sync-skills 8.3→8.4 — **taken 2026-07-14** via the console's own `install_skill` path (first real use: backup + strictly-newer guard + audit all exercised; `sync.sh` excludes itself from check/pull, so the Registries view was the only surface that saw this update — feature validated). 8.4 deps tests 21/21 green; no local action required. Upstream gap flagged: sync-skills README changelog lacks an 8.4 entry — **closed**: backfilled entry pushed as hitachi PR #269 (`ba74d4b`), mirrored locally. Process note: the local mirror commit (`c460946`) accidentally landed directly on main (was on main after the prior merge, `push -u origin HEAD` bypassed the PR flow) — content identical to the reviewed hitachi PR; left in place, deviation recorded.

<!-- STRATEGY CONTENT: architecture, agent-approval-semantics -->
**Decision — bundled-agent approval semantics (2026-07-14):** `security.approved_agents` strictly governs **top-level registered agents** (`.claude/agents/*.md` — the surface Claude Code auto-discovers). **Skill-bundled agents** (`.claude/skills/<skill>/agents/*.md`, spawned by their skill via prompt path, never registered top-level) inherit approval from their owning skill's `approved_skills` entry; explicit `approved_agents` listing is still honored and displayed distinctly.
**Why:** Requiring every skill-internal worker (docflow converters, tracker authors, skill-creator graders — 18 found) in `approved_agents` duplicates the skill approval 1:1 and makes the posture board permanently noisy; the skill IS the audited unit for its internal workers. Top-level agents stay strict because that's the auto-discovery surface.
**How to apply:** when a skill's internal agent gets promoted to a top-level registered agent (symlinked into `.claude/agents/`), add it to `approved_agents` then.

- [x] Team & Security roster editing (user follow-up 2026-07-15): **Add member** + **Deactivate** in the console. `writer.add_team_member` / `deactivate_team_member` — surgical comment-preserving edits on multi-line `- name:` blocks (inline-empty `[]` expansion, `active: []` written back when emptied, backup + audit + re-parse-validate-restore); email-domain guard vs `security.approved_email_domains`, github/task_folder uniqueness vs both rosters, inactive re-add blocked (manual re-activation keeps one history row). Endpoints `POST /setup/team/members` + `POST /setup/team/members/{github}/deactivate`. UI: add form (approved-domain hint), expandable member rows (email/tasks-folder/added + Deactivate w/ reason prompt), Inactive roster table. 9 scratch-repo unit paths green + live add→deactivate roundtrip on real project.yml (restored via git). project-console 1.34.0 (SKILL.md section table row rewritten, README changelog)
- [x] Persistent test suites (user ask 2026-07-15): scratch verification promoted into the skill's `tests/` — `test_setup_team_writer.py` (12 tests) + `test_setup_agents_loader.py` (5 tests, encodes the round-2 description-fallback regression on both surfaces). Writing them caught a real pre-existing bug: `writer._backup()` clobbered same-second backups (same `%H%M%S` filename) — fixed with a uniquifying suffix. All setup + drift + draft-workflow suites green. **Pre-existing failure surfaced then fixed (user: "fix the issues"):** `tests/test_tracker_workflow_e2e.py` had rotted through TWO contract migrations it never followed — (1) legacy status values ("Done"/"In Progress"/"Partial") vs the locked 7-state vocabulary (writer correctly rejects legacy; only render.py `coerce_status` aliases them at parse time), and (2) md-cell mutation assertions vs the overlay-first write path (`write_status_change` writes `submission-tracker.human.json`; md stays generator-owned). Test rewritten to both contracts — canonical statuses, overlay assertions in worktree + main, sidecar in diff summary, cancel discards sidecar, md asserted UNtouched. All 5 skill suites green (30 tests)

<!-- STRATEGY CONTENT: architecture, console-setup-ia, team-roster-write-scope -->
**Decision — Team & Security write scope (2026-07-15):** The Setup section's read-only rule is relaxed for the team roster: add + deactivate edit `project.yml team.*` directly from the console, because the roster's source of truth IS project.yml (unlike skills/agents, whose truth lives in the registry and whose console-side editing would fork the sync tooling's merge logic). Boundaries: (1) console edits the **roster of record only** — GitHub collaborator access is granted/revoked in GitHub, and the posture check (`setup.sh --check`) cross-references the two; (2) **deactivate ≠ delete** — the member block moves to `team.inactive` with `removed:` + required `reason:`, per the manifest's offboarding convention; (3) **re-activation stays manual** — a returning member's history should live on one entry, so the console rejects re-adding an inactive github rather than duplicating the row.
**Why:** same lockstep philosophy as connectors (config + allowlist move together): the onboarding convention (CLAUDE.md "add to team.active / move to team.inactive with removed+reason") is now enforced by validated code instead of prose.
**How to apply:** roster edits from the browser via Setup → Team & Security; audit trail in `.data/setup-audit.log` (`team-add` / `team-deactivate` rows) + timestamped project.yml backups in `.data/setup-backups/`.

- [x] Connectors catalog round (user ask 2026-07-15): **Atlassian** Popular-card (official remote MCP, OAuth endpoint `/v1/mcp/authv2` — verified via web: `/v1/sse` deprecated 2026-06-30, memory had the stale endpoint); template card form now branches on spec shape (prefilled remote/url specs were unrepresentable — always rendered the stdio form); **Command-line tooling** read-only panel (git/gh presence + version + `gh auth status` + origin remote, copy-paste fix commands). User decision: status card only for GitHub — no install/auth buttons (console stays config-edit-only; `gh auth login` is interactive OAuth). New suite `test_setup_cli_catalog.py` (7 tests). Live-verified: git 2.50.1 + gh 2.94.0 authenticated detected; all 6 suites green (37 tests). project-console 1.35.0

<!-- STRATEGY CONTENT: architecture, console-setup-ia, cli-tooling-boundary -->
**Decision — CLI tooling in Connectors is detect-and-guide, never execute (2026-07-15):** GitHub workflow tooling (git, gh) surfaces in the Connectors section as a read-only status panel — presence, version, auth account, origin remote — with copy-paste fix commands, NOT install/login buttons. User chose "status card only" over a GitHub MCP catalog entry and over executable buttons.
**Why:** (1) the console's write doctrine is config-edit-only (it never launches/stops/installs — a localhost web UI executing package installs is an attack surface); (2) `gh auth login` is an interactive browser OAuth flow that cannot run inside the FastAPI process anyway; (3) read-only probes are an established loader pattern (stdio launcher existence probe) — `gh auth status` extends it without crossing the execution line.
**How to apply:** future tooling checks (e.g. uv, pandoc, docker) join `load_cli_tooling` as probe rows with fix commands; anything that *changes* machine state stays in the terminal.

<!-- LESSONS LEARNED: grounding -->
**Lesson — verify vendor endpoints at authoring time; deprecations outrun model memory (2026-07-15).** The Atlassian remote-MCP endpoint recalled from memory (`/v1/sse`) had been deprecated two weeks before this session (2026-06-30) in favor of `/v1/mcp/authv2`. One web search caught it before it shipped into the catalog. Any hardcoded external endpoint/URL added to a skill or config should be verified against the vendor's current docs in the same turn it's written — and where possible pinned by a test that encodes the *deprecation* too (the new catalog test asserts the URL is the authv2 endpoint and NOT sse), so a future revert-from-memory fails loudly.

<!-- LESSONS LEARNED: testing -->
**Lesson — a contract migration must sweep the tests that encode the old contract (2026-07-15).** `test_tracker_workflow_e2e.py` rotted through two separate migrations (status-vocabulary lock and the overlay-first write path): each migration updated the production code and its comments but never ran or updated the skill's own test suite, so the suite failed on committed code for weeks without anyone noticing. Two takeaways: (1) when changing a component's contract, grep the skill's `tests/` for assertions that encode the old contract and migrate them in the same change; (2) suites that no CI runs rot silently — running ALL of a skill's `tests/*.py` whenever any of its code changes (as done this session) is the cheap manual substitute until the suites are wired into CI.

<!-- LESSONS LEARNED: verification -->
**Lesson — a fix for "N items missing X" must be verified per install surface, not per symptom (2026-07-15).** The 1.33.0 agent-summary fix ("all 49 agents now carry summaries") patched the fallback in the top-level-agents loop only; the bundled-agents loop had a separate, duplicated description path that silently kept the bug for 13 agents — and the claim of full coverage was recorded in the task doc. When the same field is computed in more than one code path (here: `load_agents` has two loops over two surfaces), the verification must enumerate the *output* across all paths (`[r for r in rows if not r.description]` over the full aggregate), not spot-check the path that was edited. The one-line live-data assertion that caught it this round should have been the acceptance check last round.

## Open Questions

- Edit capability scope: connectors keep existing add/remove/allowlist editing; other sections launched **read-only status** (editing skills/agents = `/sync-skills` domain). Confirm with user if inline allowlist toggles are wanted for skills/agents/plugins too.
- **Posture finding surfaced by the new view:** 14 installed agents (the `advisors`-owned personas + several researcher agents) are NOT in `project.yml security.approved_agents` (17 entries vs 31 installed) — flagged "not in allowlist" in the Agents section. Either backfill the allowlist or codify an "owned-by-approved-skill = approved" convention. User decision.
- Registry push (`/sync-skills push` of project-console 1.32.0 to hitachi) — pending user's usual cadence.

## Resume

### In-flight artifacts
All uncommitted (Claude commits nothing unprompted). project-console skill files:
- `console/setup/loader.py` (+~260 lines: 5 section loaders + aggregate), `console/setup/router.py` (aggregate wiring)
- `console/web/templates/setup_view.html` (full rewrite — settings shell), `console/web/templates/_base.html` (nav title)
- `SKILL.md` (v1.32.0 + Setup section table), `VERSION`, `README.md` (changelog)
- Task docs: `tasks/ben/104-*.md`, `tasks/ben/000-index.md`
- Console running on :8765 with the new page live (templates auto-reload; python loaded at start)

### First action on resume
- Activate: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 104`
- Remaining: user decisions on the 3 Open Questions; commit/push per git-workflow when asked.
- Do NOT redo: loaders/template/version bump/browser verification (all done).

## Economics

_By-hand person-hour estimate, **filled at checkpoint** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated; an empty `todos` list is ignored by the aggregator._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {"min": 0.5, "max": 1.0},
    "todos": [
      {
        "todo": "Contracts read (project-console SKILL.md, setup module, base template) + settings IA design",
        "personas": ["rd-lead", "systems-engineering"],
        "manual_hours": {"min": 3, "max": 6},
        "confidence": "med",
        "basis": "judgment — codebase orientation + IA design against an existing design system and a visual reference"
      },
      {
        "todo": "Five defensive section loaders + aggregate + router wiring (~280 net LOC python)",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 6, "max": 12},
        "confidence": "high",
        "basis": "software anchor 20-25 LOC/day low-end adjusted up for defensive parsing across 4 config surfaces"
      },
      {
        "todo": "Settings-shell template rewrite (~600 LOC HTML/CSS/JS: hash routing, search, expandable rows, responsive) + browser verification + zoom-breakpoint fix",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 8, "max": 16},
        "confidence": "med",
        "basis": "software anchor + judgment — frontend iteration cost dominated by cross-theme/responsive verification"
      },
      {
        "todo": "Connectors: Atlassian catalog entry (endpoint verified vs vendor docs), remote-spec card form branch, CLI-tooling probe panel (loader + template + 7-test suite)",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 3, "max": 5},
        "confidence": "high",
        "basis": "software anchor — small feature on established patterns; endpoint research + probe parsing variants are the non-trivial parts"
      },
      {
        "todo": "Team roster add/deactivate: surgical multi-line-block YAML writer (2 functions + validation guards), 2 endpoints, roster UI (form + expandable rows + inactive table), live roundtrip + 17 persistent unit tests (2 suites) incl. backup-clobber fix",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 8, "max": 13},
        "confidence": "med",
        "basis": "software anchor — comment-preserving structured-block YAML editing with restore-on-failure is the cost driver; persistent two-suite test authoring adds ~2-3h; UI reuses the established settings-shell patterns"
      },
      {
        "todo": "Bundled-agent description fallback fix (round 2): two-loop diagnosis, loader fix + paragraph-join, per-surface live verification, 1.33.1 conventions",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 1, "max": 2},
        "confidence": "high",
        "basis": "software anchor — small targeted bug fix incl. reproduction, fix, live verification, changelog"
      },
      {
        "todo": "Skill conventions: version bump, README changelog, SKILL.md Setup section rewrite",
        "personas": ["rd-lead", "quality-engineering"],
        "manual_hours": {"min": 1, "max": 2},
        "confidence": "high",
        "basis": "doc authoring anchor, sub-page scale"
      }
    ]
  }
}
```

## Changelog

- 2026-07-14: Task created from user direction: "setup should be more than mcp servers… design should look and be professional" + Claude Desktop Connectors screenshot as reference.
- 2026-07-14: Follow-ups shipped: row-detail expansion for Skills/Agents/Rules & Hooks; Agents section now covers bundled skill-internal agents (49 total) with approval inherited from the owning approved skill; `approved_agents` backfilled +14 advisors entries (board fully green); tier1-enricher/restructure question resolved (bundled in dhf-manifest, legitimately allowlisted). Renumbered 103->104 after the uncommitted pre-existing 103 (Setup tab connectors, 1.31.0) surfaced; its artifacts committed with this task's push.
- 2026-07-15: Connectors round: Atlassian Popular-card (OAuth endpoint verified via web — memory had the deprecated /v1/sse), remote-spec card form branch, read-only CLI-tooling panel (git/gh probes + fix commands; user chose no install/auth buttons). `test_setup_cli_catalog.py` added; 6 suites / 37 tests green. project-console 1.35.0. Strategy block (cli-tooling-boundary) + lessons block (verify vendor endpoints; pin deprecations in tests) added. Uncommitted.
- 2026-07-15: Fixed the flagged tracker e2e failure: test rewritten to the current contracts (7-state canonical statuses + overlay-first writes to `submission-tracker.human.json`, md generator-owned). All 5 project-console suites green (30 tests). Lessons block added (contract migrations must sweep tests encoding the old contract). Folded into the 1.34.0 changelog entry.
- 2026-07-15: Tests persisted into the skill (`tests/test_setup_team_writer.py` 12 + `tests/test_setup_agents_loader.py` 5, all green); found+fixed pre-existing same-second backup clobber in `writer._backup()`; flagged pre-existing `test_tracker_workflow_e2e.py` failure (status-vocabulary drift, out of scope). Economics row updated in place (test-suite authoring folded into the roster-feature estimate).
- 2026-07-15: Team & Security roster editing shipped (add + deactivate): `writer.add_team_member`/`deactivate_team_member` + 2 endpoints + roster UI (add form, expandable member rows, inactive table). Unit-tested 9 paths in scratch repo; live add→deactivate roundtrip on real project.yml verified then restored via git. project-console 1.33.1→1.34.0. Uncommitted. Strategy block added (team-roster-write-scope: roster-of-record-only, deactivate≠delete, manual re-activation).
- 2026-07-15: Resume (uncheckpointed session recovered from doc+git). Round-2 agent-description fix: bundled agents now get the body-summary fallback + `_body_summary` joins the full first paragraph (`console/setup/loader.py`); 49/49 verified via live `/setup/data`; skill bumped 1.33.1. Uncommitted. Lessons block added (per-surface verification).
- 2026-07-14: Shipped end-to-end in one session — project-console 1.31.0→1.32.0: Setup rebuilt as a 6-section settings shell (loaders + router + full template rewrite + nav + SKILL.md/README/VERSION). Browser-verified all sections at 150% zoom (breakpoint fix 860→720px + `.setup-body main` 1280px). New view surfaced a real posture gap: 14/31 installed agents missing from `approved_agents`. Nothing committed; 3 open questions for user (edit scope, allowlist gap, registry push).
