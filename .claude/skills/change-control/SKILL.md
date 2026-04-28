---
name: change-control
description: Bridges Claude Code / GitHub authoring with downstream regulated systems — Google Docs (internal review tier), Confluence + Comala/SoftComply (formal Part 11 review), Windchill (released vault). Enforces a hybrid freeze-point lifecycle (draft → [internal-review optional] → frozen → released) via a PreToolUse hook with in-chat consent. Provides `init`, `freeze`, `unfreeze`, `status`, `release`, plus the new task-doc-driven internal-review tier (`review-start`, `review-status`, `review-update`, `review-abort`) and `help`.
version: 0.5.0
updated: 2026-04-27
status: internal-review-v0.5
---

Base directory for this skill: `${CLAUDE_SKILL_DIR}`

# Change Control

Owns the **change-management bridge** between AI-accelerated authoring (Claude Code + GitHub) and the regulated downstream stack (Confluence + Comala/SoftComply for Part 11 review and sign-off, Windchill as the released vault, Jira for ECRs).

Implements **Strategy C** — a hybrid freeze-point lifecycle:

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: DRAFT  (git is authoritative)                     │
│  Claude Code authors freely. Iteration is cheap.            │
└─────────────────────────────────────────────────────────────┘
                   │  -- FREEZE POINT (change-control:freeze) --
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: FORMAL REVIEW  (Confluence is authoritative)      │
│  Comala/SoftComply workflow. Part 11 e-signatures.          │
│  Git path is locked. Edits blocked by PreToolUse hook.      │
└─────────────────────────────────────────────────────────────┘
                   │  -- RELEASE (Comala "Released" webhook) --
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: VAULT  (Windchill is authoritative)               │
│  Signed PDF → ECO → BOM/training assignments                │
└─────────────────────────────────────────────────────────────┘
```

The freeze enforcement lives in a **PreToolUse hook** that blocks Edit/Write on any file with `state: frozen` in its frontmatter. The hook emits a structured briefing to the user explaining what will be invalidated (Confluence page state, in-progress reviewer signatures, Jira ticket state) and requires an explicit typed phrase to authorize the unfreeze. **No PR ceremony — consent happens in the chat where the context lives.**

> ⚠️ **STATUS — SCAFFOLD ONLY.** This skill is design-captured and structurally complete but functionally a stub. All actions print `NOT IMPLEMENTED`. All connectors raise `NotImplementedError`. The scaffold exists so the design lives in code, the extensibility seams are reserved, and implementation can proceed incrementally without rewrites. See `README.md` for the full design rationale and `tasks/ben/017-change-control-skill.md` for the open questions still being worked through.

## Dependencies (planned — none enforced yet)

| File / Tool | Required by | Purpose | How to create |
|---|---|---|---|
| `jq` | `init` (hook registration) | JSON parsing | `brew install jq` |
| `.claude/hooks/register-hook.sh` | `init` | Idempotent hook registration helper | `/task setup` |
| `project.yml` | `init` | Allowlist update + project metadata | `/medtech-docs init` |
| `mark` (kovetskiy/mark) | `freeze` (when implemented) | Markdown → Confluence rendering | `brew install mark` |
| Python `httpx` | All connectors (when implemented) | Async HTTP client | `uv pip install httpx` |
| Python `keyring` | Auth layer (when implemented) | OS keychain credential storage | `uv pip install keyring` |
| `change-control.yml` | `freeze`, `unfreeze`, `release` | Project-supplied config (Confluence space, Jira project, plugin choice, doc-class policy) | Created by `init` from `templates/change-control.example.yml` |

## Supporting Files

| File | Purpose | Status |
|---|---|---|
| `hooks/pre_tool_use_frozen.py` | PreToolUse hook — blocks Edit/Write on frozen docs, emits briefing | **STUB** — exits 0 always; design documented in file |
| `lib/_base.py` | `Connector` base class, `Authenticator` interface, deployment-flavor enum | **STUB** — interfaces only |
| `lib/frontmatter.py` | Read/write the `state:` block on controlled docs | **STUB** |
| `lib/diff_classify.py` | Cosmetic vs substantive edit classification | **STUB** |
| `lib/confluence.py` | Confluence base API (raw httpx) + `mark` shell-out for publish | **STUB** |
| `lib/comala.py` | `ReviewPlugin` interface + `ComalaPlugin` impl + `SoftComplyPlugin` stub | **STUB** |
| `lib/jira.py` | Jira REST v3 client (raw httpx) | **STUB** |
| `lib/windchill.py` | Windchill ECO connector | **STUB** (Phase 3 — last to be implemented) |
| `actions/init.py` | Wire hook into `.claude/settings.json`, create config from template | **STUB** |
| `actions/freeze.py` | Draft → frozen lifecycle transition | **STUB** |
| `actions/unfreeze.py` | Frozen → draft (called by hook on user approval) | **STUB** |
| `actions/status.py` | Traceability spine view across all controlled docs | **STUB** |
| `actions/release.py` | Phase 2 → Phase 3 Windchill handoff | **STUB** |
| `templates/change-control.example.yml` | Project config template | Concrete (example file) |
| `templates/frontmatter_block.md` | Canonical state block for new controlled docs | Concrete (example file) |
| `README.md` | Full design documentation (not loaded by Claude — for humans and future maintainers) | Complete |
| `VERSION` | Skill version | `0.1.0` (scaffold) |

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform. **All actions are currently stubs** — they print what they *would* do and exit 0.

### `init`

**STATUS: STUB** — prints planned setup steps; does not modify project state.

When implemented, will:

1. **Preflight** — verify `jq`, `register-hook.sh`, `project.yml` exist; verify `mark` is installed; verify Python deps.
2. **Install hook** — symlink `hooks/pre_tool_use_frozen.py` → `.claude/hooks/change-control-frozen.py`; ensure executable.
3. **Register hook** via shared helper:
   ```bash
   .claude/hooks/register-hook.sh PreToolUse "Edit|Write|NotebookEdit" command \
     '"$CLAUDE_PROJECT_DIR"/.claude/hooks/change-control-frozen.py'
   ```
4. **Allowlist** — add `change-control` to `project.yml` `security.approved_skills` (warn if user must do it manually based on secops posture).
5. **Project config** — copy `templates/change-control.example.yml` → `change-control.yml` at project root if not present. User edits to fill in Confluence space key, Jira project key, plugin choice, doc-class policy.
6. **State cache** — create `docs/.change-control/state.json` (empty array) for the hook's fast-path lookup.
7. **Credential check** — probe OS keychain for `change-control-bot` credentials. If missing, print one-time setup instructions (do NOT prompt for secrets directly — user runs `keyring set` themselves).
8. **Report** — summarize what was done and what the user still needs to do (edit `change-control.yml`, set keychain entries).

### `freeze <path>`

**STATUS: STUB** — prints `NOT IMPLEMENTED: would freeze <path>`.

When implemented, will:

1. Verify `<path>` is a markdown file with `state: draft` frontmatter.
2. Verify the doc class (per `change-control.yml` policy) requires control. Reject if not.
3. Resolve or create Jira ECR (per Jira-required policy — see task 017 open question #3).
4. Render markdown → Confluence via `mark`; create or update the page.
5. Capture page ID + version into frontmatter.
6. Flip `state: draft` → `state: frozen`.
7. Update `docs/.change-control/state.json` cache.
8. Commit with message `freeze(<jira_ecr>): <doc title>`.

### `unfreeze <path> [--reason <text>]`

**STATUS: STUB** — prints `NOT IMPLEMENTED: would unfreeze <path>`.

When implemented, will:

1. Verify `<path>` has `state: frozen`.
2. Mark Confluence page as Superseded via Comala API.
3. Comment on linked Jira ECR (`Unfrozen by <user>: <reason>`).
4. Flip `state: frozen` → `state: draft`; clear `confluence_version_at_publish`; add `unfrozen_at`.
5. Update state cache.
6. Commit with message `unfreeze(<jira_ecr>): <doc title> — <reason>`.

This action is normally called automatically by the PreToolUse hook on user approval — not directly by the user.

### `status [--filter <state>]`

**STATUS: STUB** — prints a table header with no rows and a `NOT IMPLEMENTED` notice.

When implemented, will list every controlled doc and its phase/IDs:

```
Path                                           State     Confluence  Jira          Windchill
docs/project/dhfs/pca-device/inputs/pump-occlusion.md
                                               frozen    458291 v1   PROJECT-1234   —
docs/project/dhfs/pca-device/inputs/audible-alarm.md
                                               released  458292 v3   PROJECT-1235   ECO-9981
```

Reads from frontmatter (authoritative); validates against `state.json` cache (warns on drift).

### `release <path>`

**STATUS: STUB** — prints `NOT IMPLEMENTED: would release <path> to Windchill`.

When implemented, will be triggered by the Comala "Released" webhook (or run manually). Pulls signed PDF, attaches to a new Windchill ECO referencing the Jira ECR, updates frontmatter with the ECO number, flips `state: frozen` → `state: released`.

### `review-start <path>`

**STATUS: v0.1 — task-doc-driven scaffolding ready; gdoc auto-create deferred to v0.2.**

Kick off internal review for a doc. Prints manual steps to create the
gdoc in your `AI_PDLC/<project.name>/<task_folder>/` folder, share with
your reviewer group, and writes a sentinel-bounded metadata block to
your active task doc.

Args: `<path>` — repo-relative path to source (md / markdown / docx).

The metadata block format and worked example are documented at length
in `tasks/ben/116-change-control-internal-review-tier.md` "Workflow"
section. Read that for the full mental model.

### `review-status <path>`

**STATUS: v0.1 — reads gdoc state via web-control.**

Refresh the task-doc section's "Open" list with current open comments,
suggestions, and body edits from the linked gdoc. Preserves user-edited
"Already Addressed" + "Recently Synced" subsections.

Requires: `/web-control launch` Chrome running + signed in.

### `review-update <path>`

**STATUS: v0.1 — replies + body-replace + state-snapshot.**

Reads "Already Addressed" items from the task-doc section, posts replies
on each addressed comment via web-control, accepts/rejects suggestions,
then wholesale-pastes current source content into the gdoc body.

State snapshots saved to `.state/web-control/<gdoc-id>.{last-sync.json,
last-push.txt}` for body-edit detection on next `review-status`.

### `review-abort <path>`

**STATUS: v0.1 — clean cancellation.**

Removes the task-doc metadata block and deletes state files. Does NOT
delete the gdoc — user can manually clean up in Drive.

### `help [<action>]`

**STATUS: v0.1 — runtime help.**

Prints lifecycle diagram + actions list, or per-action detail (purpose,
args, examples, common errors). Same pattern as `gh help`.

### `reindex`

**STATUS: STUB**

Rebuilds `docs/.change-control/state.json` by walking the doc tree and reading frontmatter. Use if the cache drifts out of sync with frontmatter (shouldn't happen, but escape hatch).

## Notes

- **All actions are stubs.** They exist so the skill scaffold is complete and the design is captured in code. Implementation will proceed incrementally per the open questions in `tasks/ben/017-change-control-skill.md`.
- **Cloud-first.** v1 targets Atlassian Cloud. Data Center support is a planned v2 capability — the connector layer is designed so Data Center slots in without action-layer rewrites.
- **MCP is complementary.** If the project also installs the Atlassian MCP server, *interactive* Claude actions ("create me an ECR for this finding") work natively in chat. The skill owns freeze-time automation; MCP owns chat-time convenience. Both can coexist.
- **Read `README.md`** for the full design rationale, the strategy decisions, the connector architecture, and the extensibility seams. The README is the design doc — SKILL.md is the user-facing manual.

## Best Practices
See [README.md](README.md) — consumed by `/best-practices` audit.

## Changelog
See [README.md](README.md) for version history.

