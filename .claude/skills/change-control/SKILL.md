---
name: change-control
description: |
  Bidirectional bridge between Claude Code / GitHub authoring and regulated downstream systems — Google Docs (internal review tier), Confluence + Comala/SoftComply (formal Part 11 review), Windchill (released vault), Jira (ECRs).

  TRIGGER for INBOUND (Confluence → repo) — when the user wants to **grab, pull, acquire, import, adopt, mirror, copy, sync, ingest, fetch, snapshot, or bring** a Confluence page (or page tree / subtree / section / space) into the project's markdown tree under `docs/`. Natural-language phrasings that should fire this skill include:
    - "grab the Confluence page(s) at <url>"
    - "pull the Confluence page <title> into our docs"
    - "sync the Confluence page <url> into the project"
    - "import this Confluence subtree into our docs"
    - "mirror the <space> Confluence pages locally"
    - "adopt the existing Confluence content for <topic>"
    - "copy the Confluence pages over to our repo"
    - "acquire the formal Confluence content as markdown"
    - "we already have these pages in Confluence — bring them in"
  Inbound actions: `adopt` (single page), `adopt-tree` (subtree, bulk), `pull` (refresh side-by-side comparison). Adopted content lands at the project-configured `staging_target_root` (`change_control.spaces[].staging_target_root` in `project.yml`) — typically the canonical Confluence-mirror root, so adopt writes content directly into its controlled home.

  TRIGGER for OUTBOUND (repo → Confluence/Windchill) — when the user wants to **publish, push, freeze, release, send-up, hand off, or sign off** local markdown to the regulated stack. Natural-language phrasings:
    - "publish this doc to Confluence"
    - "freeze <path> for formal review"
    - "kick off Part 11 review on <path>"
    - "release this to Windchill / the vault"
    - "send this up for formal sign-off"
  Outbound actions: `publish` (push markdown → Confluence page with divergence detection), `freeze` (lock local + start formal review), `unfreeze` (revert with consent), `release` (Confluence → Windchill ECO).

  TRIGGER for INTERNAL REVIEW (md ↔ Google Docs) — when the user wants pre-formal team review via Google Docs comments before Confluence/Comala. Natural-language phrasings: "send this for team review", "open a review gdoc", "start internal review on <path>", "pull comments back from the gdoc". Actions: `review-start`, `review-status`, `review-update`, `review-abort`.

  Lifecycle: `draft → published → review-formal → frozen → released`. Enforces freeze gate via PreToolUse hook with in-chat consent.

  Other actions: `init`, `status`, `help`, `reindex`, `verify`.
version: 0.14.1
updated: 2026-09-08
status: adopt-publish-probe-validated
---

Base directory for this skill: `${CLAUDE_SKILL_DIR}`

# Change Control

Owns the **change-management bridge** between AI-accelerated authoring (Claude Code + GitHub) and the regulated downstream stack (Confluence + Comala/SoftComply for Part 11 review and sign-off, Windchill as the released vault, Jira for ECRs).

## Two flow directions, one skill

This skill handles **both directions** of the bridge between local markdown and the regulated stack:

**INBOUND — Confluence → repo (`adopt` / `adopt-tree` / `pull`)**

When formal content already exists in Confluence and the team wants to bring it into the project's markdown tree (so Claude Code can author against it, trace tooling can index it, V&V can verify against it). Use this when the user says "grab", "pull", "import", "adopt", "mirror", "sync", "acquire", or "copy" Confluence pages into the repo.

```
Confluence page(s)
        │  -- adopt / adopt-tree (Atlassian MCP fetch, ADF→md, snapshot) --
        ▼
<staging_target_root>/<space>/<path>.md   ← controlled markdown (frontmatter snapshot kept)
```

`staging_target_root` is project-configured (`change_control.spaces[].staging_target_root`). Projects point it at the canonical Confluence-mirror root so adopt lands content directly in its controlled home — there is no separate "stage then promote" step.

**OUTBOUND — repo → Confluence → Windchill (`publish` / `freeze` / `unfreeze` / `release`)**

The original Strategy C hybrid freeze-point lifecycle, now with `published` and `review-formal` as distinct states between `draft` and `frozen`:

```
draft  →  published  →  review-formal  →  frozen  →  released
   │           │              │              │           │
   git      Confluence     Comala /     Confluence    Windchill
authoring  page exists,  SoftComply   page locked,   ECO + signed
           bidirectional  Part 11      git Edit       PDF, BOM
           sync via       e-sign       blocked by     impact
           publish/pull   workflow     PreToolUse     assignments
```

**INTERNAL REVIEW (Google Docs round-trip) — `review-start` / `review-status` / `review-update` / `review-abort`**

Team comments on a gdoc copy of the source before formal Confluence review. Optional pre-formal lane.

The freeze enforcement lives in a **PreToolUse hook** that blocks Edit/Write on any file with `state: frozen` in its frontmatter. The hook emits a structured briefing to the user explaining what will be invalidated (Confluence page state, in-progress reviewer signatures, Jira ticket state) and requires an explicit typed phrase to authorize the unfreeze. **No PR ceremony — consent happens in the chat where the context lives.**

## Implementation status — per-action snapshot

| Action | Status | Notes |
|---|---|---|
| `adopt` | **Probe-validated, agent-orchestrated** | Live MCP fetch, ADF→markdown, frontmatter + snapshot working; per `actions/adopt.md` procedure. Build remains for full pipeline (incl. images, smartlink labels, success-panel preservation). |
| `adopt-tree` | **Probe-validated** | JSON-directive MCP bridge for bulk subtree pulls. Avoids per-page agent turn cost. Per `actions/adopt_tree.md`. |
| `pull` | **Probe-validated** | Refreshes `<doc>.confluence-side.md` next to source. Required by `publish` Merge branch. |
| `publish` | **Probe-validated** | First-publish + update with divergence detection + Confluence Zone preservation. Per `actions/publish.md`. |
| `freeze` / `unfreeze` | **Stub** | Lifecycle transitions; PreToolUse hook design captured but enforcement not yet wired. |
| `release` | **Stub** | Confluence → Windchill ECO handoff. |
| `review-start` / `review-status` / `review-update` / `review-abort` | **v0.1 shipped** | gdoc round-trip via web-control + task-doc metadata block. |
| `init` / `help` / `status` / `reindex` | Mixed (init stub, help v0.1, status stub, reindex stub) | |

Eleven live probes from task 120 validate the v0.6 architecture end-to-end (5-state lifecycle, Confluence Zones via reserved `<details>` titles + ADF splice, divergence detection with Overwrite/Merge/Abort prompt + snapshot cache, image sync via web-control cookie reuse, plugin seam for Document Control / Comala / SoftComply). The `adopt` and `publish` paths are the most mature; build remaining is roughly 50–55 person-hours per task 120's resume-ready block.

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

Parse the user's argument string `$ARGUMENTS` to determine which action to perform. See the per-action **Status snapshot** above; not all are implementation-shipped yet.

### `adopt <page-url-or-id> [--target <repo-path>]`

**STATUS: Probe-validated, agent-orchestrated.** Per `actions/adopt.md`.

Pulls one Confluence page into the repo as markdown. Default target is `<staging_target_root>/<space-key>/<sanitized-page-path>.md`, where `staging_target_root` is read from the configured space in `project.yml` (`change_control.spaces[].staging_target_root`) — projects point it at the canonical Confluence-mirror root. The page's ADF body is fetched via Atlassian MCP, normalized to markdown locally, and written with frontmatter capturing `confluence.page_id`, `confluence.version`, and a content snapshot used by `publish` for divergence detection.

Use when the user says: *"grab/pull/import/adopt/sync/mirror/copy/acquire the Confluence page at <url>"*, *"bring this Confluence page into our docs"*, *"we already have this in Confluence — pull it in"*.

### `adopt-tree <root-page-url-or-id> [--target <root>] [--max-depth N] [--dry-run]`

**STATUS: Probe-validated.** Per `actions/adopt_tree.md`.

Bulk variant of `adopt` — walks a Confluence subtree from the given root and mirrors all descendants. Uses a JSON-directive bridge (fd 3 / fd 4) so a Python loop drives the bulk fetch instead of paying one agent turn per page. Suitable for ~95+ page subtrees.

Use when the user says: *"pull the whole <space> Confluence tree"*, *"import all the pages under <root>"*, *"mirror the Product Overview subtree"*, *"sync this entire Confluence section into the repo"*.

### `pull <doc>`

**STATUS: Probe-validated.** Per `actions/pull.md`.

Reads the current Confluence page body for an already-published doc and writes a side-by-side `<doc>.confluence-side.md` for comparison. Does NOT push, does NOT modify the source. Used in `publish`'s Merge branch and as an explicit "what does Confluence look like right now?" check.

Use when the user says: *"refresh the Confluence side of <doc>"*, *"show me what Confluence has for this page right now"*, *"diff our markdown against Confluence"*.

### `publish <doc>`

**STATUS: Probe-validated.** Per `actions/publish.md`.

Push local markdown to its Confluence page. Either creates a new page (when no `confluence.page_id` in frontmatter) or updates an existing page with **divergence detection** + **Confluence Zone preservation** (reserved `<details>` titles preserved across round-trips via ADF splice).

On divergence (Confluence has been edited since last sync), prompts Overwrite / Merge / Abort. Refuses when `state ∈ {review-formal, frozen, released}`.

**Publish gate — `confluence.publish_body` (default-deny for binary-authoritative records).** If the page's frontmatter has `confluence.publish_body: false` (or `docflow.authoritative: formal` with no explicit `publish_body: true`), do **NOT** push the markdown body as Confluence page content. These pages are *non-canonical derived views* (the docflow `_confluence`-splice convention): the canonical published artifact is the **attachment** (`label=actual`, uploaded via the `confluence-side: attachments` sentinel) **+ the node's `index.md` landing page** — not the version-page body. Publishing the body is opt-in only (`publish_body: true`). When the gate is active, `publish` still reconciles/uploads the attachment + maintains the index page, but skips the body→ADF push for the version page.

**Filed-body-only mode — `--strip-internal` (three-tier docs).** By default the transform *keeps* `🔒 INTERNAL` `<details>` containers so they round-trip to Confluence as collapsed expands. For a three-tier submission doc (leading metadata → `🔒 INTERNAL` working apparatus → filed body) where the Confluence page should carry **only the filed body the regulator sees**, pass `--strip-internal` to `publish_helper` (`precheck` / `body` / `adf-body`). It strips — fence-aware — every HTML-comment metadata block, every `🔒`-headed `<details>` container, and every `🔒`-marked table column (mirrors the eStar `strip_internal` so the Confluence body matches the eStar exhibit). Opt-in per publish; enable it durably for a doc with `confluence.strip_internal: true` in frontmatter (the agent reads it and passes the flag). Report the `internal_zones_stripped` `{comments, containers, columns}` counts to the user.

Use when the user says: *"publish this doc to Confluence"*, *"push our markdown up to Confluence"*, *"update the Confluence page from our local copy"*, *"publish the filed body only / strip the internals"*.

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
                                               frozen    458291 v1   PP3500-1234   —
docs/project/dhfs/pca-device/inputs/audible-alarm.md
                                               released  458292 v3   PP3500-1235   ECO-9981
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

### `verify <kind>`

**STATUS: v0.12 — repeatable smoke tests.** Per `actions/verify.md`.

Runs an end-to-end verification flow against the `test_target` configured in `project.yml` `change_control.test_target` and writes a structured JSON report under `tasks/<person>/_scratch/verify-<kind>-<date>.json`.

Sub-actions:
- `audit` — config-only audit (no live calls).
- `orphan-file` — round-trip a synthetic test PDF + plain-link markdown through publish + re-adopt.
- `cross-page-resolution` — adopt a page known to carry `UNKNOWN_MEDIA_ID` and assert the resolver replaces it.
- `drift-detection` — re-adopt a hand-edited page and assert the structured conflict prompt fires.
- `all` — runs all of the above.

The skill code stays project-agnostic: the `test_target` carries `space_key`, `parent_page_id`, `parent_title`, and `title_prefix` — every project plugs in its own AI_PDLC sandbox parent and `verify` works the same way against it.

## Project config (`project.yml change_control` block)

v0.12.0 introduced project-level defaults so the action helpers don't need their `--cloud-id`, `--base-url`, `--space-key`, or `--target-root` flags spelled out in every invocation. The `change_control:` block in `project.yml` is the single source of truth for project-specific values; the skill code reads it via `lib/config.py`.

Schema (all fields optional; missing block = legacy CLI-required behavior):

```yaml
change_control:
  cloud_id: <atlassian-cloud-uuid>
  base_url: https://<site>.atlassian.net
  spaces:
    - key: <SPACE_KEY>
      name: <human label>
      staging_target_root: docs/project/_confluence
      title_prefixes_to_strip: [...]
  test_target:
    space_key: <SPACE_KEY>
    parent_page_id: "<page id>"
    parent_title: <title>
    title_prefix: <string>
  cross_page_source_map:
    "<page_id>":
      - filename: "<file>"
        source_page_title: "<title>"
```

CLI flags continue to override config values — backward-compatible with v0.11.0 invocations.

## Notes

- **All actions are stubs.** They exist so the skill scaffold is complete and the design is captured in code. Implementation will proceed incrementally per the open questions in `tasks/ben/017-change-control-skill.md`.
- **Cloud-first.** v1 targets Atlassian Cloud. Data Center support is a planned v2 capability — the connector layer is designed so Data Center slots in without action-layer rewrites.
- **MCP is complementary.** If the project also installs the Atlassian MCP server, *interactive* Claude actions ("create me an ECR for this finding") work natively in chat. The skill owns freeze-time automation; MCP owns chat-time convenience. Both can coexist.
- **Read `README.md`** for the full design rationale, the strategy decisions, the connector architecture, and the extensibility seams. The README is the design doc — SKILL.md is the user-facing manual.

## Best Practices
See [README.md](README.md) — consumed by `/best-practices` audit.

## Changelog
See [README.md](README.md) for version history.

