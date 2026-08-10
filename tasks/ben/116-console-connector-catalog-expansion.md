# 116 — Console Connector Catalog Expansion

**ID**: 116
**Created**: 2026-08-07
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

Expand the project-console **Settings → Connectors** catalog (`.claude/skills/project-console/console/setup/catalog.py`) so the MedTech toolchain the team actually uses is one click away, and so tools with **no** vendor MCP are visibly marked as such rather than silently absent.

Source list (user-supplied, 2026-08-07): Jira, Confluence, GitLab, Git, Jama Connect, MasterControl, Microsoft Office 365, Miro, Lucid Chart.

**Availability research result** — every entry verified against vendor documentation before being catalogued (no invented endpoints):

| Tool | MCP status | Catalog action |
|---|---|---|
| Jira + Confluence | Official Atlassian remote MCP (`https://mcp.atlassian.com/v1/mcp/authv2`) | Already catalogued as `atlassian` — retitled so Jira/Confluence are findable by name |
| GitLab | Official, `https://<host>/api/v4/mcp`, OAuth 2.0 DCR, http transport | New entry `gitlab` |
| Git | Official MCP reference server `mcp-server-git` (`uvx`) | New entry `git` |
| Jama Connect | Official "Jama Connect MCP™" (GA May 2026, paid add-on). Endpoint is **instance-specific and not publicly documented** — help page is customer-gated | New entry `jama-connect` with an operator-supplied URL + note (no fabricated endpoint) |
| MasterControl | **No vendor MCP.** Only a third-party individual-authored server (`morsm/mastercontrol-mcp`) | New entry `mastercontrol` with `availability: "none"` — visible, not configurable |
| Microsoft 365 | Official Microsoft MCP Server for Enterprise, `https://mcp.svc.cloud.microsoft/enterprise`, http. Covers Graph **tenant/directory** data, not Office file content | New entry `microsoft-365` with an honest scope note |
| Miro | Official, `https://mcp.miro.com`, OAuth 2.1 DCR, http | New entry `miro` |
| Lucid (Lucidchart/Lucidspark) | Official, `https://mcp.lucid.app/mcp`, streamable HTTP, OAuth | New entry `lucid` |

Secondary goal: two small, general capability additions to the catalog contract so the above can be expressed honestly — an optional per-entry `note` and an optional `availability` flag.

<!-- STRATEGY CONTENT: operations, architecture — connector catalog curation policy -->
**Strategy — what earns a place in the console's connector catalog (operations/architecture).** Decision: the skill-shipped catalog lists **vendor-official MCP servers only**. A third-party or individual-authored MCP server is not catalogued as a one-click install, even when one demonstrably exists (MasterControl's `morsm/mastercontrol-mcp` is the concrete case). Rationale: the catalog is a *curated* surface whose Configure button writes `.mcp.json` **and** auto-adds the connector to `project.yml security.approved_mcps` — i.e. clicking it grants an allowlist entry. Handing that one-click path to an unvetted server that would hold credentials to the system of record for controlled DHF documents and approvals inverts the purpose of the allowlist. Users who have vetted such a server can still add it through the existing **Custom stdio / Custom HTTP** forms, which is the deliberate escape hatch: possible, but an explicit act with a named owner rather than a curated recommendation.

Corollary decision: rather than omit MasterControl, catalogue it with `availability: "none"`. An absent card is ambiguous (nobody looked? not supported? forgotten?); a card that says "no vendor MCP" is a researched answer with a date on it, and it stops the question being re-asked every quarter.

Second decision: **never invent an endpoint to fill a form.** Jama Connect's MCP is real and official, but the endpoint is customer-gated. The entry ships with an empty URL, a `url_placeholder` hint, and a note telling the operator where to obtain it — rather than a plausible-looking guessed path, which would be indistinguishable from a verified one once written into `.mcp.json`.
<!-- /STRATEGY -->

## Todos

- [x] Research — verify vendor MCP availability + exact endpoints for all 9 tools against primary vendor docs
- [x] Catalog contract extension — optional `note`, `url_placeholder`, and `availability` fields (`catalog.py` docstring + template rendering)
- [x] Add 7 catalog entries (gitlab, git, jama-connect, microsoft-365, miro, lucid, mastercontrol) + retitle `atlassian`
- [x] Template — render notes, unified http/stdio form branches, "no vendor MCP" card state (`setup_view.html`)
- [x] Verify — offline catalog/template assertions + live `/setup` render + sibling-route regression
- [x] Skill version bump + SKILL.md / README changelog
- [ ] User browser walkthrough of Settings → Connectors
- [ ] Push per git-workflow when the user asks (+ candidate `/sync-skills push` upstream — registry-shared skill)

## Open Questions

- Microsoft 365: the official Enterprise endpoint exposes **Graph tenant/directory** scopes (users, groups, policies, audit logs), not Office document content. If the team wants Outlook/OneDrive/SharePoint **content**, the paths are (a) tenant-scoped Agent 365 endpoints (`https://agent365.svc.cloud.microsoft/agents/tenants/{tenant_id}/servers/mcp_ODSPRemoteServer`, preview) or (b) the community `@softeria/ms-365-mcp-server`. Neither is catalogued yet — the URL field is editable so (a) is reachable today. Decide whether Agent 365 warrants its own catalog entry once out of preview.
- MasterControl: is the third-party `morsm/mastercontrol-mcp` worth a security review? Given MasterControl holds the controlled DHF records and the firmware SOUP references, a vetted read-only connector would be high-value — but that is a security-review task, not a catalog task.
- Jama Connect: does the team's Jama tenant have the MCP add-on licensed? If not, the card is aspirational.

## Resume

### In-flight artifacts

- **Uncommitted**: edits to `.claude/skills/project-console/console/setup/catalog.py`, `console/web/templates/setup_view.html`, `SKILL.md`, `README.md`, `VERSION` (1.59.0 → 1.60.0).
- Console restarted and verified on http://127.0.0.1:8765.
- Pre-existing unrelated dirty files in git status (tasks 114/115 work, journey/doc_pipeline/strategy console modules) — **do not** sweep into this task's commit.

### First action on resume

1. Ask the user to walk Settings → Connectors at http://127.0.0.1:8765/setup — the Configure buttons write real config, so user-driven is safer than curl.
2. On "push": commit only the project-console skill files + this task doc/index, then branch → PR → auto-merge per `.claude/rules/git-workflow.md`.
3. Activation: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 116`

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
        "todo": "Availability research — verify vendor MCP existence + exact endpoints for 9 tools against primary docs",
        "personas": ["rd-lead", "cybersecurity"],
        "manual_hours": {"min": 3, "max": 6},
        "confidence": "high",
        "basis": "9 vendor doc trails, several customer-gated or contradicted by secondary aggregator sites; the work is finding the primary source and refusing the plausible-but-unverified endpoint, which is slow by hand"
      },
      {
        "todo": "Catalog contract extension + 7 entries + atlassian retitle",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 2, "max": 3},
        "confidence": "high",
        "basis": "small declarative data module; low end of the software anchor"
      },
      {
        "todo": "Template rendering — notes, unified form branches, unavailable-card state",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 2, "max": 4},
        "confidence": "med",
        "basis": "Jinja refactor of an existing card block plus a new visual state; internal-tooling UI rate"
      },
      {
        "todo": "Verification + version/docs",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 1, "max": 2},
        "confidence": "high",
        "basis": "assertion script + route smoke + changelog rows"
      }
    ]
  }
}
```

## Changelog

- 2026-08-07: Task created. Availability research completed for all 9 tools against vendor primary docs; catalog contract extended (`note`, `url_placeholder`, `availability`); 7 entries added + `atlassian` retitled to name Jira/Confluence; `setup_view.html` card block reworked (unified http/stdio branches, note line, "no vendor MCP" state); project-console 1.59.0 → **1.60.0**. Verified: 28/28 offline assertions + live `GET /setup` 200 with all 12 catalog cards rendered + 5 sibling routes regression-free. Uncommitted.
