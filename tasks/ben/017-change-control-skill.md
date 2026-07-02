# 017 — Change Control Skill (GitHub ↔ Confluence ↔ Windchill)

**ID**: 017
**Created**: 2026-04-14
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## Goals

Design and build a `change-control` skill that bridges Claude Code / GitHub authoring with downstream regulated systems (Confluence + Comala/SoftComply for Part 11 review and sign-off, Windchill as the released vault). The skill must enforce a clean **freeze point** between the AI-accelerated drafting phase and the human-controlled formal-review phase, using an in-context Claude Code hook rather than CODEOWNERS / PR ceremony.

This task captures the design discussion, decisions made so far, and the open questions that still need to be worked through before implementation.

- Define the lifecycle: draft (git) → frozen (Confluence + Comala) → released (Windchill)
- Specify the freeze enforcement mechanism (PreToolUse hook, in-chat consent)
- Define the skill package structure and `init` wiring (matches `secops` / `medtech-docs` pattern)
- Resolve open integration questions: Jira/Confluence connectivity, when Jira is required, task-doc ↔ ECR linking
- Validate against sister project (`../../projects/arthrex/pccp/`) before marking complete

## Todos

- [ ] Resolve open questions (see below) with user
- [ ] Decide skill name (`change-control` vs `freeze` vs `pdlc-change-control`)
- [ ] Pick Confluence connector approach (REST + token, Atlassian Forge, mark, custom)
- [ ] Pick Jira connector approach + auth model
- [ ] Decide Jira-required policy (always vs conditional)
- [ ] Decide task-doc ↔ Jira ECR linking convention
- [ ] Draft skill scaffold (SKILL.md, VERSION, README, hooks/, lib/, actions/)
- [ ] Implement `init` action (settings.json wiring, project.yml allowlist update)
- [ ] Implement PreToolUse hook (`pre_tool_use_frozen.py`)
- [ ] Implement `freeze` / `unfreeze` actions
- [ ] Implement `status` action (traceability spine view)
- [ ] Stub `release` action (Phase 2 → Phase 3 Windchill handoff)
- [ ] Generalization check against arthrex/pccp
- [ ] `/sync-skills push` upstream to hitachi

## Analysis

### Context: the three-system stack

The target deployment is a medtech program where:

- **GitHub + Claude Code** is the authoring workbench (markdown drafts, source code, task docs, AI-accelerated iteration).
- **Confluence + a Part 11 plugin** (Comala Document Management, SoftComply eQMS Express, or similar) is the formal-review and electronic-signature environment. The plugin adds controlled states, reviewer assignment, and 21 CFR Part 11 e-signatures on top of native Confluence pages.
- **Windchill (PTC)** is the released vault — system of record for BOM/CAD master, ECOs, training assignments, and the legally binding released artifact.

Each system does exactly one job:

| System | Role | What lives here |
|---|---|---|
| GitHub | Authoring + collaboration + AI workbench | Working markdown, source code, task docs, draft DHF artifacts, PR review history |
| Confluence + Comala/SoftComply | Formal review + Part 11 sign-off | Published page versions, reviewer comments, Comala workflow state, e-signatures |
| Windchill | Released vault | Signed PDF + metadata, ECO records, BOM deltas, training assignments |
| Jira | Work tracking + change request workflow | ECRs, tasks, defects, cross-system links |

### Strategy decision: Strategy C (hybrid with freeze point)

<!-- STRATEGY CONTENT: development, change-control, document-lifecycle, ai-authoring -->

We considered three strategies for handling the GitHub ↔ Confluence boundary:

- **Strategy A** — Confluence pages are read-only mirrors of git; reviewers can only comment, every change is a new PR.
- **Strategy B** — Confluence becomes authoritative once a doc enters review; final content is exported back to git.
- **Strategy C** — Hybrid. Git is authoritative through draft and technical review. At a defined milestone, the doc is **frozen** in git and **published once** to Confluence; from that point Confluence + Comala owns the artifact until sign-off, then Windchill takes over.

**Decision: Strategy C.** Rationale: Claude Code is the right tool for drafting (AI-accelerated, branch-friendly, diff-native). Confluence is the right tool for human refinement, polish, and Part 11 sign-off. Forcing reviewers into PR workflows for wording changes is the kind of "elegant on a whiteboard, abandoned in week six" decision we want to avoid. Strategy C plays to each system's strengths and gives Claude Code a bounded blast radius.

**Why:** The user explicitly chose Strategy C and rejected the PR-based enforcement model: "Claude Code is meant as the drafting tool, AI powered; when refinement and human editing is needed, Confluence is better."

**How to apply:** Any future change-control design discussion defaults to Strategy C semantics. Don't reopen the A/B/C debate without new information.

### Strategy decision: agent-mediated freeze enforcement (no PRs)

<!-- STRATEGY CONTENT: development, change-control, hook-design, claude-code -->

The freeze enforcement lives in a **Claude Code PreToolUse hook**, not in CODEOWNERS / branch protection / PR approval. When Claude is about to edit a file with `state: frozen` in its frontmatter, the hook blocks the edit and emits a structured briefing to the user — explaining what will be invalidated (Confluence page state, in-progress reviewer signatures, Jira ticket state) and requiring an explicit typed phrase to authorize the unfreeze.

**Why:** The decision should happen where the context lives. A PR-based gate puts the decision in front of a QA reviewer who has none of the context (what Claude was trying to do, why, whether it's worth disrupting the review). The user — sitting in the Claude Code chat — has all of it. Hooks are also enforceable without ceremony: they fire on every Edit/Write tool call, no exceptions, no "I'll just commit this small fix directly" escape hatch.

**How to apply:** Future changes to enforcement should preserve the in-chat consent model. If the briefing becomes too noisy (hook fatigue), the answer is smarter diff classification, not weaker enforcement. Cosmetic/changelog/comment-only edits get a lighter prompt; substantive edits require a typed confirmation phrase including the document name (mirrors how Claude Code handles destructive operations).

### The lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: DRAFT  (git is authoritative)                     │
│  - Claude Code authors in markdown                          │
│  - Task doc captures decisions, strategy, lessons inline    │
│  - PRs for technical review by engineering peers            │
│  - Iteration is cheap; AI does the heavy lifting            │
└─────────────────────────────────────────────────────────────┘
                          │
                          │  -- FREEZE POINT --
                          │  Triggered by: `change-control:freeze <path>`
                          │  CI action: publish to Confluence, lock git path
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: FORMAL REVIEW  (Confluence is authoritative)      │
│  - Comala workflow: Draft → In Review → Approved → Released │
│  - Reviewers edit inline, comment, request changes          │
│  - Part 11 e-signatures captured at "Approved" transition   │
│  - Git path is read-only; any "fix" requires unfreezing     │
└─────────────────────────────────────────────────────────────┘
                          │
                          │  Comala "Released" state fires webhook
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: VAULT  (Windchill is authoritative)               │
│  - Signed PDF + metadata exported from Confluence           │
│  - Attached to Windchill ECO referencing Jira ECR           │
│  - Promoted to "Released" state in Windchill                │
│  - Training assignments fire                                │
│  - Git gets a back-reference: confluence page ID + ECO #    │
└─────────────────────────────────────────────────────────────┘
```

### Frontmatter contract

Every controlled doc carries a state block in its frontmatter:

```yaml
---
title: PP3500 Pump Occlusion Detection — Design Input
state: draft | frozen | released
frozen_at: 2026-04-14
frozen_commit: a3f9c21
confluence_page_id: 458291
confluence_version_at_publish: 1
jira_ecr: PP3500-1234
windchill_eco: null  # populated when Phase 3 completes
---
```

`state` is the field the hook checks. The other fields form the traceability spine across systems. After Phase 3, the file is a permanent record of the handoff chain — git → Confluence → Windchill, all linked by IDs.

### Skill package structure

Follows the convention of `secops`, `medtech-docs`, and the other skills in `.claude/skills/`:

```
.claude/skills/change-control/
├── SKILL.md
├── VERSION
├── README.md                   # ## Conventions, ## Changelog, ## Best Practices
├── .gitignore                  # blocks __pycache__, *.pyc per skill_no_build_artifacts rule
├── hooks/
│   └── pre_tool_use_frozen.py
├── lib/
│   ├── frontmatter.py
│   ├── diff_classify.py
│   ├── confluence.py           # Comala / SoftComply API
│   ├── jira.py
│   └── windchill.py            # Phase 3 stub initially
├── actions/
│   ├── init.py
│   ├── freeze.py
│   ├── unfreeze.py
│   ├── status.py
│   └── release.py
└── templates/
    └── frontmatter_block.md
```

### Actions

| Action | Purpose |
|---|---|
| `init` | Idempotent setup. Symlinks `hooks/pre_tool_use_frozen.py` into `.claude/hooks/`, registers via `register-hook.sh` under `PreToolUse` matching `Edit\|Write\|NotebookEdit`, adds `change-control` to `project.yml` `security.approved_skills`, creates `docs/.change-control/state.json` cache, checks for Confluence/Jira credentials. |
| `freeze <path>` | Draft → frozen. Updates frontmatter, publishes to Confluence via Comala API, captures page ID + version, links Jira ECR (creating one if needed), commits. |
| `unfreeze <path>` | Frozen → draft. Marks Confluence page Superseded, comments on Jira, updates frontmatter, commits. Triggered automatically by the hook on user approval. |
| `status` | Lists every controlled doc with its phase, Confluence page ID, Jira ECR, Windchill ECO. The traceability spine view. |
| `release <path>` | Phase 2 → Phase 3. Fired by Comala webhook on "Released" state. Pulls signed PDF, attaches to a new Windchill ECO referencing the Jira ECR, updates frontmatter. |

### Hook execution path

The hook runs on **every** Edit/Write/NotebookEdit call, so the fast path matters:

1. Parse tool input JSON from stdin → target file path.
2. Lookup in `docs/.change-control/state.json` — if not a controlled doc, exit 0 immediately. (99% of edits hit this.)
3. If controlled, read frontmatter. If `state != frozen`, exit 0.
4. If frozen, classify the proposed edit (`lib/diff_classify.py`) — cosmetic vs substantive.
5. Emit a structured block message to stderr per Claude Code hook protocol; exit non-zero to block the tool call.

The blocking message is a **briefing** — it tells the user exactly what will be invalidated and what phrase to type to authorize the unfreeze.

### `init` wiring

`init` reuses the project's existing `register-hook.sh` infrastructure so `change-control` plays nicely with `task`, `secops`, and any other skills that register hooks. Concretely:

```bash
.claude/hooks/register-hook.sh PreToolUse "Edit|Write|NotebookEdit" command \
  '"$CLAUDE_PROJECT_DIR"/.claude/skills/change-control/hooks/pre_tool_use_frozen.py'
```

The hook script lives inside the skill package, gets versioned with the skill, and travels via `/sync-skills`. Removing the skill cleanly unwires it.

## Connectivity Options Analysis (Confluence + Jira)

This section captures the full landscape of options for connecting the skill to Confluence (with Comala / SoftComply review plugins) and Jira, plus the chosen approach and the reasoning behind it. It exists so future maintainers can revisit the decision when adding new capabilities (e.g., Data Center support, OAuth, MCP-driven chat workflows) without re-deriving the analysis.

### Deployment dimension comes first

The Atlassian ecosystem split years ago, and the deployment flavor dictates everything downstream:

| Flavor | Status | Auth | Implications |
|---|---|---|---|
| **Atlassian Cloud** | Active, strategic | API tokens (email + token), OAuth 2.0 (3LO) for apps, OAuth 2.0 client credentials | REST v2/v3, rate limits, hosted by Atlassian |
| **Server** | EOL Feb 2024 | PAT or basic auth | Officially unsupported. Don't design around it. |
| **Data Center** | Active, self-hosted enterprise | PAT, OAuth 2.0, SAML/SSO upstream | Common in big regulated medtech. REST API mostly Cloud-compatible with quirks. VPN/network reachability matters. |

**First target: Atlassian Cloud.** Decision rationale captured in the Strategy block below. Data Center support is a planned v2 capability — the skill is designed so the connector layer can grow a Data Center backend without touching the action layer.

### Confluence connectivity — five options considered

#### Option 1 — `atlassian-python-api` (the default Python wrapper)

Single library covering both Confluence and Jira. Mature, MIT-licensed, supports Cloud and DC.

- ✅ One dependency for both products
- ✅ Pagination, retries, error mapping included
- ✅ Confluence-specific helpers (page CRUD, attachments, labels, spaces)
- ❌ Heavy dependency footprint (`requests`, `urllib3`, `six`)
- ❌ Sometimes lags behind Cloud API v2 changes
- ❌ No first-class Comala / SoftComply support — plugin endpoints called raw anyway
- ❌ Sync only, no async story

**Verdict:** safe, boring, "ship it" choice. Rejected in favor of Option 2 because the skill's API surface is narrow enough that the wrapper convenience doesn't justify the dependency weight.

#### Option 2 — Raw `httpx` against the REST API ✅ CHOSEN (base layer)

Talk directly to `/wiki/rest/api/content` and `/rest/api/3/issue`.

- ✅ Lightest dependency footprint
- ✅ Async-native (matters if `project-console` later grows a Confluence panel)
- ✅ Full control over headers, retries, error handling
- ✅ No library lag — implement against current API spec
- ❌ Pagination / auth / error mapping written by us
- ❌ More code to maintain in `lib/confluence.py` and `lib/jira.py`
- ❌ Easier to subtly mis-implement OAuth 2.0

**Verdict:** chosen for the base API layer. The skill needs roughly six Confluence endpoints and five Jira endpoints — well within the budget where raw is cheaper than wrapping.

#### Option 3 — Atlassian MCP server

Atlassian ships an official MCP server (Cloud-only currently); community MCP servers exist for Data Center.

- ✅ Claude Code talks to it natively — no Python connector code at all
- ✅ Auth handled by the MCP server, not the skill
- ✅ Tools first-class for Claude (read/write pages, create/transition issues from chat)
- ✅ Fits existing MCP posture (chrome-devtools is already pre-approved)
- ❌ Cloud-only for the official server
- ❌ The freeze hook runs as a standalone script outside Claude's tool-use loop — **MCP tools are not callable from a hook**
- ❌ Comala / SoftComply still require raw REST — MCP doesn't cover plugins
- ❌ Adds an MCP dependency to the project's secops allowlist

**Verdict:** complementary, not a replacement. Documented as a planned **complementary capability** — when a project also installs the Atlassian MCP, *interactive* Claude actions ("create me an ECR for this finding") work natively in chat without going through the skill at all. The skill owns freeze-time automation; MCP owns chat-time convenience. The two coexist cleanly.

#### Option 4 — `mark` (kovetskiy/mark) for markdown→Confluence rendering ✅ CHOSEN (publish layer)

A mature Go binary purpose-built for publishing markdown files as Confluence pages. Used in production by lots of teams. Handles mermaid, drawio, attachments, frontmatter-driven page metadata. Supports Cloud and DC.

- ✅ Solves the markdown→Confluence fidelity problem out of the box
- ✅ Battle-tested for the exact use case
- ✅ Frontmatter-driven (reads YAML frontmatter for space, parent, labels)
- ❌ External binary — additional install step (not pip)
- ❌ Doesn't know about Comala state transitions — raw REST still needed for that
- ❌ Wraps publish only; no help for read-back / supersede / comment

**Verdict:** chosen specifically for the publish step. `lib/confluence.py` shells out to `mark` for "render markdown and push to Confluence as a new page version," and uses raw `httpx` for everything else (read state, list comments, attach files). Alternative `md_to_confluence` (Python) considered and rejected — less mature, lossier rendering of medtech-relevant content (tables, mermaid diagrams).

#### Option 5 — Atlassian Forge (cloud apps)

Build a Forge app inside Confluence Cloud that exposes endpoints to the skill.

- ✅ Most powerful integration; can render custom UI inside Confluence pages
- ❌ Cloud-only; requires Atlassian developer account and app review for production
- ❌ Massive overkill for the freeze use case
- ❌ TypeScript/JS, not Python

**Verdict:** rejected. Documented for completeness so future maintainers don't re-litigate.

#### Comala / SoftComply specifically

Both are Confluence add-ons with their own REST surfaces:

- **Comala Document Management** — `/rest/cw/1/content/{pageId}/state`, `/rest/cw/1/workflow/{pageId}`, etc. Read state, transition state, list approvers, check signatures.
- **SoftComply eQMS** — `/rest/eqms/1.0/...`, similar shape but more opinionated workflow stages.

Neither has a Python wrapper. Both require raw `httpx`, regardless of which library handles base Confluence. The skill therefore exposes two side-by-side clients in `lib/`:

- `lib/confluence.py` — base Confluence (Option 2 + Option 4)
- `lib/comala.py` — Comala plugin REST (raw httpx, abstracted behind a `ReviewPlugin` interface)

The `ReviewPlugin` interface lets the project pick `comala` or `softcomply` in `change-control.yml`. Initial implementation targets Comala; a `SoftComplyPlugin` class is stubbed but unimplemented.

### Jira connectivity — four options considered

#### Option A — `atlassian-python-api`

Same library as Confluence Option 1; same tradeoffs. Rejected for the same reasons — narrow API surface doesn't justify wrapper weight.

#### Option B — `jira` (the older `jira-python` library)

Long-standing dedicated Jira library.

- ✅ Mature, stable, Jira-native abstractions
- ❌ Two libraries to maintain (one for Confluence, one for Jira)
- ❌ Same sync-only limitation

**Verdict:** rejected — the split-brain dependency tax outweighs the better idioms.

#### Option C — Raw `httpx` against `/rest/api/3/` ✅ CHOSEN

Same calculus as Confluence Option 2. Five endpoints total: create issue, get issue, transition, comment, link.

**Verdict:** chosen. Symmetric with Confluence so `lib/` stays consistent.

#### Option D — Atlassian MCP server

Same caveats as Confluence Option 3. Complementary, not a replacement for the skill's freeze-hook needs.

### Auth + credential storage

#### Pattern 1 — `.env` per developer

`CONFLUENCE_BASE_URL`, `CONFLUENCE_USER`, `CONFLUENCE_TOKEN`, `JIRA_*` in a gitignored `.env`. Every developer creates their own API token.

- ✅ Simple, audit-friendly per-user
- ❌ Every developer needs Atlassian permissions
- ❌ Confluence/Jira audit trail mixes human and automated actions under the same user

**Verdict:** supported as a **fallback** for projects where keychain isn't viable.

#### Pattern 2 — Service account + OS keychain ✅ CHOSEN (default)

One shared service account (`change-control-bot`); credentials in macOS Keychain / Linux secret-tool, accessed via Python `keyring`.

- ✅ No secrets on disk
- ✅ Confluence/Jira audit trail clearly shows `change-control-bot acting on behalf of <user> at <time>` rather than mixing human and automated actions in a single user's history — what regulated medtech shops actually want
- ❌ Higher setup cost (one-time)
- ❌ Requires distributing the service account token securely

**Verdict:** chosen as default. `init` action checks for keychain credentials and walks the user through one-time setup if missing. Falls back to `.env` with a warning if keychain is unavailable.

#### Pattern 3 — OAuth 2.0 (3LO)

User authorizes the skill once via browser; refresh token in keychain. Most aligned with Atlassian's modern app guidance.

- ✅ Most secure
- ❌ Highest setup cost
- ❌ Overkill for an internal skill

**Verdict:** documented as a **planned v2 capability** — the auth layer is abstracted so a future `OAuth2Authenticator` slots in alongside `TokenAuthenticator` without touching the connectors.

### Chosen stack — summary

| Concern | Choice | Rationale |
|---|---|---|
| Confluence base API | Raw `httpx` (REST v2) | Narrow surface; async-ready; no wrapper lag |
| Markdown → Confluence rendering | `mark` external binary | Solves the fidelity problem; battle-tested |
| Comala / SoftComply | Raw `httpx` behind `ReviewPlugin` interface | No wrapper exists; abstraction lets projects pick plugin |
| Jira API | Raw `httpx` (REST v3) | Symmetric with Confluence; five endpoints |
| Auth (default) | Service account + OS keychain via `keyring` | Clean audit trail; no on-disk secrets |
| Auth (fallback) | `.env` per developer | Works where keychain isn't viable |
| Deployment target (v1) | Atlassian Cloud | Strategic, simpler auth, MCP available for chat-side |
| Deployment target (v2 planned) | Atlassian Data Center | Connector layer abstracted to support both |
| Chat-side complementary capability | Atlassian MCP server (when project installs it) | Skill owns freeze-time automation; MCP owns chat-time convenience |

### Extensibility points (designed in, not implemented)

The skill scaffold reserves these extension seams so capabilities can be added without rewrites:

1. **`Connector` base class** in `lib/_base.py` — every connector (`ConfluenceConnector`, `JiraConnector`, `WindchillConnector`) inherits common httpx client setup, retry/backoff, and auth injection.
2. **`Authenticator` interface** — `TokenAuthenticator` (v1) and `OAuth2Authenticator` (planned) both implement `inject(request)`.
3. **`ReviewPlugin` interface** — `ComalaPlugin` (v1) and `SoftComplyPlugin` (stub) both implement `get_state(page_id)`, `transition(page_id, state)`, `supersede(page_id)`, `list_approvals(page_id)`.
4. **Deployment flavor enum** — `Cloud` (v1) and `DataCenter` (planned). Connectors branch on this for endpoint paths and auth specifics.
5. **`lib/windchill.py`** — entire Phase 3 vault layer is stubbed; the action exists, the connector signature exists, the implementation does not.
6. **`change-control.yml`** — project-supplied config declares deployment flavor, Confluence space key, Jira project key, doc-class policy, review plugin choice. Nothing project-specific is hard-coded.

## Open Questions

These are the questions the user explicitly flagged as "still lots to figure out." They need resolution before implementation begins.

### 1. Confluence + Comala/SoftComply connectivity

- **Auth model** — Atlassian Cloud uses API tokens (user + token); Server/Data Center uses PAT or OAuth. Which environments are in scope? Cloud-only? Both?
- **Library** — `atlassian-python-api` is the obvious default but is heavy and sometimes lags Cloud changes. Alternatives: raw `httpx` against the REST v2 API; Atlassian Forge (cloud apps); existing publishers like `mark` (Go) or `md_to_confluence`.
- **Comala vs SoftComply** — Comala has a flexible workflow engine (custom states, parallel reviewers, conditional transitions); SoftComply is more opinionated. The skill needs an abstraction layer so a project picks one in `change-control.yml`. Which do we target first?
- **Markdown → Confluence fidelity** — images, diagrams (mermaid? PlantUML?), tables, cross-references, code blocks. What's the lossiness budget? Where do images get hosted?
- **Page templates** — does the published page use a Confluence template, or is the entire body machine-rendered from markdown?
- **Credential storage** — `.env` (per-developer) vs `project.yml` (shared, no secrets) vs OS keychain. Aligns with secops posture.

### 2. Jira connectivity

- **Auth model** — same shape as Confluence (API token vs PAT vs OAuth). Cloud or Server?
- **Library** — `jira` (atlassian-python) vs raw REST.
- **Project mapping** — which Jira project corresponds to which DHF? Lives in `project.yml`?
- **Issue type** — does a freeze create an "ECR" issue type, or use a generic "Task" with a label? Depends on the client's Jira config.

### 3. When is Jira required?

This is a real design question. Possible answers:

- **Always** — every freeze creates or links a Jira ECR. Simplest mental model, strongest audit trail, but ceremonial for early-stage drafts.
- **Required at freeze time only** — drafts can churn without Jira; the ECR is created (or must already exist) when `freeze` is called. Matches the "freeze = handoff to formal process" framing.
- **Conditional on doc class** — design inputs, V&V protocols, and risk files always require an ECR; working analysis docs and task docs do not. Driven by frontmatter or path.
- **Configurable per project** — `change-control.yml` declares the policy.

Recommendation to discuss: **required at freeze time, conditional on doc class** — i.e., only documents declared as "controlled deliverables" in `change-control.yml` need a Jira ECR at freeze. Task docs and exploratory analysis never freeze, so never need Jira.

### 4. Task docs and Jira

The user asked: should task docs reference the Jira ticket for the work?

Sub-questions:

- Is a task doc 1:1 with a Jira ticket, 1:N (one task → many tickets), or N:1 (many tasks → one epic)?
- If a task is bigger than a ticket, do we link the epic instead?
- Does the link live in the task frontmatter (machine-readable) or the body (human-readable) or both?
- Does `/task create` prompt for a Jira ticket / epic key? Optional or required?
- For projects without Jira, the link is just absent — the task skill must stay Jira-agnostic.

Current instinct (to validate with user): **task docs reference an optional Jira ticket or epic in frontmatter** (`jira: PP3500-EPIC-42` or `jira: null`); the `task` skill stays Jira-agnostic; `change-control` is the skill that actually integrates with Jira at freeze time, reading the linked task doc to find the ECR if one is set, prompting to create one if not.

### 5. The freeze direction trigger

What initiates a freeze? Options:

- Explicit user command in chat (`change-control:freeze <path>`)
- Jira state transition (ticket moves to "Ready for Formal Review")
- Frontmatter flag flip in a normal commit
- A `ready-for-formal-review` label on a PR

Likely answer: **explicit chat command first**, with optional Jira-driven trigger as a v2 enhancement once the connector is mature.

### 6. Diff classification rules

What counts as "cosmetic" vs "substantive" for the lighter-prompt path?

- Frontmatter-only changes
- Comment-only changes (HTML comments in markdown)
- Changelog row appends
- Whitespace / formatting only
- Typo fixes (hard to detect automatically)

Substantive = anything else. The classifier needs to be conservative — false-positive (treat substantive as cosmetic) is much worse than false-negative.

### 7. State cache vs frontmatter

`docs/.change-control/state.json` is a fast lookup for the hook (avoid walking the doc tree on every Edit). Frontmatter is authoritative. How do they stay in sync?

- Regenerated by `freeze` / `unfreeze` actions
- Rebuilt by a `change-control:reindex` action if it drifts
- Validated by `change-control:status` (warn on drift)

### 8. Generalization to sister project

Per the standing rule, this skill must work for `../../projects/arthrex/pccp/` as well as PDLC_DEMO. Specifically:

- Project-specific config (Confluence space key, Jira project key, Windchill instance URL, doc-class policy) must live in `project.yml` or a skill-local `change-control.yml`, never hard-coded.
- The hook script must be project-agnostic.
- `init` must work on a project that doesn't yet have any controlled docs.

## References

| Ref | Description | Location |
|---|---|---|
| Strategy decision | Strategy C: hybrid freeze-point model | This task, Analysis section |
| Existing hook pattern | `register-hook.sh` shared infrastructure | `.claude/skills/task/hooks/register-hook.sh` |
| Sister project | Arthrex PCCP project for compatibility validation | `../../projects/arthrex/pccp/` |
| FDA change guidance | "Deciding When to Submit a 510(k) for a Change to an Existing Device" | (to import via `medtech-docs update-external-references`) |
| 21 CFR Part 11 | Electronic records and signatures | (already in `docs/external/`) |

## Lessons Learned

<!-- LESSONS LEARNED: ai-tooling, change-control, regulated-workflows -->

**AI authoring tools need a bounded blast radius, not a banned blast radius.** The temptation with AI-driven authoring of regulated docs is to wall the AI off from anything signed. That preserves compliance but throws away most of the value. The better pattern is to let the AI work freely in a clearly-bounded "draft" zone and enforce the boundary with tooling (a hook), not policy (a CLAUDE.md rule that the model might forget). The freeze point is the boundary; the hook is the enforcement; the in-chat briefing is the handoff to the human.

**Why:** Came out of the design discussion when the user rejected the PR-based enforcement model. The insight is that "the agent is the right place to enforce the rule, because the agent is where the edit is about to happen and where the human context lives." Moving the gate downstream loses the context.

**How to apply:** When designing future skills that touch regulated artifacts (V&V records, risk files, signed protocols), prefer in-chat consent gates over downstream PR / approval gates. Reserve PR gates for things that genuinely need a different reviewer than the one in the chat.

**Strategy C is the realistic answer for AI-authored regulated docs.** Pure git-as-source-of-truth (Strategy A) is elegant but breaks down the moment a reviewer wants to fix a typo. Pure Confluence-as-source-of-truth (Strategy B) loses everything Claude Code gives you. The hybrid — git owns drafting, Confluence owns review + sign-off, Windchill owns release — respects what each tool is actually good at and what humans are actually willing to do.

**Why:** Real-world rollout consideration, not a theoretical preference. The user's framing: "Claude Code is meant as the drafting tool, AI powered; when refinement and human editing is needed, Confluence is better."

**How to apply:** Default to Strategy C semantics for any future change-control discussion in this or sister projects.

## Changelog

- 2026-06-08: Closed Complete via task-doc audit — scaffold + design delivered (28dfbba); built out to full skill via upstream sync + ben/032. Moved to Completed in 000-index.md.
- 2026-04-14: Added Connectivity Options Analysis section — full landscape of Confluence (5 options), Jira (4 options), and auth (3 patterns) considered, plus chosen stack and rationale. Decision: Atlassian Cloud first; raw `httpx` for base APIs; `mark` for markdown→Confluence rendering; raw `httpx` behind a `ReviewPlugin` interface for Comala/SoftComply; service-account + OS keychain for credentials; Atlassian MCP documented as a complementary chat-side capability. Six extensibility seams enumerated. Scaffolded `.claude/skills/change-control/` with all design captured in-skill (SKILL.md + README.md), every action and connector marked STUB / NOT IMPLEMENTED.
- 2026-04-14: Task created. Captured the full design discussion: three-system stack (GitHub + Confluence/Comala + Windchill), Strategy C decision, agent-mediated freeze enforcement, lifecycle phases, frontmatter contract, skill package structure, action list, hook execution path, `init` wiring. Listed eight open questions for follow-up: Confluence/Comala connectivity, Jira connectivity, Jira-required policy, task-doc ↔ Jira linking, freeze trigger, diff classification, state cache vs frontmatter sync, sister-project generalization. Tagged two strategy blocks (development domain) and one lessons block (ai-tooling, change-control, regulated-workflows).

