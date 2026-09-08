---
name: tracker
description: "Submission package tracker — milestone-driven readiness dashboard. Builds tracker markdown from milestone catalog + composition manifests + DHF evidence, renders feature-rich HTML dashboard (filters, badges, click-row details, URL-rewriting to project-console Documents tab), assesses readiness. HCLS-portable via project.yml `tracker:` config block + plugin seams for lifecycle-state reading."
version: 15
updated: 2026-09-08
---

# Submission Package Tracker

Build and manage the submission package tracker. Usage: `/tracker <action> [arguments]`

## Source Files

| File | Purpose |
|------|---------|
| `docs/project/submissions/submission-tracker.md` | Source of truth — all deliverables, status, scope, phase, REF, engineering prerequisites, deliverable details |
| `docs/project/submissions/submission-tracker.html` | Generated dashboard — never hand-edit |
| `${CLAUDE_SKILL_DIR}/scripts/render.py` | Python script that generates HTML from markdown |

## Context Required for Building the Tracker

The tracker is a **projection of the milestone catalog onto evidence-on-disk**. Before adding or modifying deliverables, read the **Context & Sources** section at the top of `submission-tracker.md`. Inputs flow through this layered model:

**Plan layer (drives what bindings the tracker tracks):**

1. **Milestone catalog** (`docs/project/milestones/regulatory.yml`) — declares named release milestones (e.g., QSub Release / 510k+PCCP Release / LMR1 Release / LMR2 Release) with per-`{dhf, doc, version}` bindings + posture (`readiness-check | full-package | planning`) + cross-domain `prerequisites:`. **Primary input.**
2. **Project DHF manifest** (`docs/project/dhf-manifest/<project-slug>-dhf-manifest.json`) — Tier 4 obligation catalog projected through scope. Provides obligation grounding for each binding's REF column.

**Snapshot layer (records what's in each filing package):**

3. **Composition manifests** (`docs/project/submissions/<filing>/composition-manifest.md`) — snapshot of pieces actually packaged at filing time, conceptually a projection of one milestone's bindings. **Owned by the `submissions` skill** (template + authoring + section/column schema); tracker is a **read-only consumer** — `generate.py` walks it for `(submission)`-scope rows and must key only on the section/column contract `submissions` declares (`submissions/SKILL.md` → `## Composition-manifest contract`). Never write the manifest from here.

**Architecture + scope:**

4. **Project manifest** (`project.yml` — `dhfs[]`) — list of DHFs. Each entry's `path` points to evidence root. `dhf_organization: external` (with `taxonomy_path`) means the DHF taxonomy is dictated by an external authority (Confluence, SharePoint, Windchill); resolution goes through the per-customer taxonomy file.
5. **System SAD** (one per project at `docs/project/dhfs/<system-dhf>/design-controls/architecture/<device-slug>-system-sad.md`) — module architecture, SaMD boundary, classifications → drives Scope assignments.
6. **Regulatory strategy** (`docs/project/strategies/regulatory-strategy.md`) — filing pathway, predicate lineage, jurisdictional roadmap → informs PCCP-portion readiness framing.

**Reg sources:**

7. **FDA guidance + standards** (`docs/external/fda-guidance/`, distilled into `.claude/skills/dhf-manifest/data/`) — REF column citations.

## Tracker Structure

The tracker markdown is **milestone-driven**: per-Phase sections (one per milestone) with sub-tables grouped by binding source (system DHF, per-item DHFs, submission narrative, etc.).

```
## Phase: <milestone-short-label>      ← one section per milestone (e.g. QSub, 510k+PCCP, LMR1, LMR2)
   ### <subsection>                    ← grouping within phase (Suite, PreOp, IntraOp, MgmtSvc, (submission), …)
      | # | Deliverable | Scope | Phase | REF | Status | Path |   ← 7-column row
…
## Engineering Prerequisites           ← cross-cutting; gates multiple deliverables
   | # | Prerequisite | Scope | Phase | Status | Gates |          ← 6-column row (ENG IDs)
…
## Deliverable Details                 ← per-ID detail entries; surfaced as click-row expansion
   ### <ID> — <name>                   ← one entry per deliverable that needs a full REF list
      - **Phase**: …
      - **Scope**: …
      - **Primary REF**: …
      - **All applicable REFs**: …
      - **Notes**: …
…
## Cross-Milestone Summary             ← rollup table; not parsed as deliverables
## Notable Findings                    ← context; not parsed
## Reviewer Sign-off                   ← QMS roles only (R&D Lead / Regulatory / etc.); no Author row
## Changelog                           ← author/contributor tracking lives here
```

### Overlay precedence — the source of truth for a cell is NOT always the markdown (HARD RULE)

A tracker deliverable's rendered `status` / `path` / `ref` / `effort` / `name` can come from **two** places, and the sidecar **wins**:

| Layer | File | Owns | Applied |
|-------|------|------|---------|
| Canonical markdown | `submission-tracker.md` | structural cells (`scope`, `phase`), and any cell with no overlay override | parsed by `render.py` |
| **Overlay sidecar** | `submission-tracker.overlay.yml` (`rows.<id>`) | **human-curated overrides of `status`, `path`, `ref`, `effort`, `name`** | merged over the markdown at render time (`render.py` `load_human_overlay` / `apply_human_overlay`) — **overlay value overrides the markdown cell** |

**Failure mode this prevents:** you edit a status/path in `submission-tracker.md`, re-render, and the console still shows the old value — because an `overlay.yml` `rows.<id>` entry silently overrode your edit. Editing the `.md` alone is not enough when an overlay override exists; **update the overlay**. The overlay is also the *durable* home — `/tracker generate --write-canonical` regenerates the `.md` from catalog + overlay, so `.md`-only edits to overlay-managed cells are lost, while overlay edits survive.

**Two environment gotchas that make a "correct" render lie:**

1. **PyYAML must be present.** `render.py` reads the YAML overlay only if `import yaml` succeeds. Run with a bare interpreter that lacks PyYAML and the overlay is **skipped** — the render emits raw markdown that looks right but does **not** match what a yaml-enabled environment (the project console venv) serves. Always `/tracker render` in an env with PyYAML (the console's venv, or `pip install pyyaml`). The renderer now prints a loud stderr `WARNING` in this case — do not ignore it.
2. **Verify in the running console, on the right port, not a standalone file open.** The console live-renders the tracker (applying the overlay) and rewrites row paths to clickable `/documents#path=…` links; a browser opened directly on `submission-tracker.html` cannot resolve those links, and a console on a *different project's* port shows a different project's tracker. Confirm the port in that project's `tools/project-console/console.yaml` (`server.port`) before concluding "the link is missing."

**Update recipe when changing a deliverable's status or path:** (1) edit `submission-tracker.md` for readability/audit, (2) **edit the matching `rows.<id>` in `overlay.yml`** (or remove the override if the `.md` should win), (3) `/tracker render` in a PyYAML env, (4) verify in the console.

### Column Definitions

**Deliverable rows (regulatory + submission narrative):**

| Column | Purpose | How to assign |
|--------|---------|---------------|
| **#** | Unique ID, kebab-case allowed (e.g., `Q1`, `PS3`, `PP14`, `PI21`, `PM9`, `PA6`, `PC4`, `L1-PI1`). | Prefix encodes category; suffix encodes module if applicable. |
| **Deliverable** | Document or artifact name. | Match FDA guidance terminology where possible. |
| **Scope** | Project-discovered values. Common: `Suite` (system DHF), per-item-DHF short names (e.g., `PreOp`, `IntraOp`, `MgmtSvc`), `(submission)` for filing-narrative. | Follow what the System SAD calls each module. |
| **Phase** | Milestone short label (e.g., `QSub`, `510k+PCCP`, `LMR1`, `LMR2`). Should match a `milestone.name` in `regulatory.yml`. | Section heading + per-row Phase column should agree. |
| **REF** | Single citation, prioritized **FDA → IEC → other Standards → QMS**. | Pick the highest-priority applicable reference. Full applicable list goes in the Deliverable Details appendix (`### <ID>` entry). |
| **Status** | `Done | Partial | In Progress | Not Started | Inherited | N/A`. | `Done` = evidence file exists at expected path/version. `Inherited` = evidence lives in a different DHF (e.g., privacy/SOUP from platform DHF). `N/A` = binding not applicable to this scope. |
| **Path** | Project-relative path to the evidence file/folder, ideally as a markdown link. | Renderer rewrites to `/documents#path=<virtual-path>` so clicks open in the project-console Documents tab. |

**Engineering Prerequisites rows:**

| Column | Purpose |
|--------|---------|
| **#** | `ENG<N>` |
| **Prerequisite** | Engineering capability name (not a task — e.g., "AI Model Development" not "Train the model") |
| **Scope** | Same vocabulary as deliverable rows; primary scope of gated deliverables |
| **Phase** | Earliest milestone gated |
| **Status** | Same vocabulary as deliverable rows |
| **Gates** | Comma-separated deliverable IDs gated by this prereq |

### Scope and Phase Vocabularies

Both Scope and Phase use **project-discovered values** — the renderer detects whatever values appear in the markdown and generates filter buttons + badge colors dynamically. No values are hardcoded in the skill.

For a typical multi-module medtech project, expect:
- Scope: `Suite | <each item DHF short name> | (submission)`
- Phase: short labels matching `regulatory.yml` milestone IDs

### Deliverable Details (click-row expansion content)

Per-ID entries in the `## Deliverable Details` section surface as inline expansions when a row is clicked in the HTML dashboard. Recommended shape per entry:

```markdown
### Q2 — PCCP qualification framework
- **Phase**: QSub (Required) + 510k+PCCP (PS2) · **Scope**: Suite
- **Primary REF**: FDA AI/ML PCCP Final Guidance (Sept 2023) §V — PCCP description
- **All applicable REFs**:
  - FDA AI/ML PCCP Final Guidance (Sept 2023) §V, §VI, §VII
  - FDA General PCCP Draft Guidance (Aug 2024) §III
  - FDA SE Guidance (2014) §III — modifications under SE
- **Notes**: Decision tree for what qualifies as a PCCP-authorized change.
```

**Do NOT restate the row's `Status` (or a "To be created" path) in the detail block (HARD RULE).** The detail schema is `Phase · Scope · Path · Primary REF · All applicable REFs · Notes` — the same fields the `submission-tracker.details.json` sidecar carries, and it deliberately has **no status field**. Status lives in the row's badge (driven by the `.md` cell + `overlay.yml`); duplicating it here is redundant *and* rots — a status/path change made to the row cell + overlay leaves the hand-authored detail line stale, so an expanded row shows "Not Started / To be created" long after the deliverable is In Review. Keep the detail's `Path` in sync with the row's Path (or omit it and let the row cell carry it); never add a `Status` line.

### Reviewer Sign-off

Roles only — per QMS separation-of-duties (ISO 13485 §7.3). NEVER include an Author row. Author/contributor tracking goes in the Changelog table only. Standard roles: R&D Lead, Regulatory Affairs, Scientific Affairs, Quality Assurance. Add domain leads when document scope requires (Cybersecurity Lead, AI/ML Lead, Clinical Lead, Human Factors Lead).

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform.

### `init`

First-time setup of the submission tracker for a project. Idempotent — safe to re-run.

**Steps**:
1. **Check prerequisites**:
   - `project.yml` has a non-empty `dhfs[]` list (required)
   - `docs/project/milestones/regulatory.yml` exists (required for milestone-driven rows; if missing, suggest scaffolding via `/medtech-docs init` or hand-author per `milestones/README.md`)
   - For each entry in `dhfs[]`, verify `path` resolves
   - Composition manifests at `docs/project/submissions/<filing>/composition-manifest.md` (warn if missing — tracker can run without them but they document what's actually packaged)
2. **Create tracker markdown** (if not present): scaffold `submission-tracker.md` with milestone-driven structure — Context & Sources, Status / Scope / Phase / REF Priority Legends, per-Phase sections (one per milestone in `regulatory.yml`), Engineering Prerequisites, Deliverable Details, Cross-Milestone Summary, Notable Findings, Reviewer Sign-off, Changelog.
3. **Add CLAUDE.md rule** if not present: "Before editing `submission-tracker.md`, load `/tracker` skill."
4. **Verify render script** works.
5. **Report** what was created vs already-present.

### `build [topic]`

Add or extend deliverables in the tracker. Authoring action — proposes changes, doesn't auto-modify.

**Steps**:
1. Read milestone catalog + composition manifests + System SAD + DHF Project Manifest.
2. For the topic (or full review): identify deliverables present in the milestone bindings but absent from the tracker, OR rows in the tracker not backed by a binding.
3. Propose row additions/removals/reclassifications.
4. After user approval, edit the markdown.
5. Run `/tracker render`.

### `render`

Regenerate the HTML dashboard from the markdown source.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/render.py
```

The renderer:
- Parses the milestone-driven markdown (per-Phase sections + Engineering + Deliverable Details)
- Generates HTML with: 5 summary cards (per-Phase + Engineering + Total), per-Phase progress bars, 3-way filter buttons (Status × Scope × Phase), color-coded badges (status / scope / phase — colors discovered from values), collapsible per-subsection categories with click-row help expansion populated from Deliverable Details
- Rewrites relative file links in row paths + detail content to `/documents#path=<virtual-path>` so clicking opens in the project-console Documents tab
- Preserves project-agnostic posture: no project-specific names baked into output; values flow from the markdown

#### Theme coupling (optional)

If the project ships a project-console with an active theme pack, the renderer mirrors its palette into the dashboard's `:root`. This is best-effort and one-directional: with no console, or no theme pack, the dashboard falls back to the slate+sky defaults baked into `_CSS_BASE_INNER` and renders exactly as a standalone file. **The iframe inherits nothing** — the console's CSS variables are not visible inside the dashboard document, which is why the palette is copied in at render time rather than referenced.

| Mirrored | Not mirrored |
|---|---|
| Chrome: `body_bg`, `surface`, `surface_2`, `surface_muted`, `border`, `text`, `text_muted`, `primary` (→ both `--brand` and `--accent`, which are one role by default), `accent` (→ `--accent2`), `font_body` | **Status colours** `--green` / `--yellow` / `--red` / `--orange` / `--cyan` / `--pink`. These encode approved / in-flight / blocked. A row that turns brand-coloured stops communicating, so they never follow the theme |

**Milestone colours come from the pack's `category_colors` ramp** (see the project-console skill for the key's contract). This renderer assigns them:

- Sequential entries → phases, in **document order** — the order the markdown declares them and the order the summary cards appear, so the cool→warm ramp reads as milestone progression. (Badges previously used `sorted()`, so badge colour disagreed with card position.)
- The reserved final entry → `--eng`, the Engineering Prereqs card and divider, which is a parallel workstream rather than a point in the sequence.
- Each milestone's **summary card, phase badge and progress-row label** share one colour so they read as a group. Progress-bar *segments* stay status-coloured.

Generated class names are prefixed (`ph-`, `sc-`) so a value that slugs to a digit-leading token — `510k+PCCP` → `510k-pccp` — cannot produce an invalid CSS selector. An unprefixed digit-leading class makes browsers discard the whole rule silently; that is what left the 510k+PCCP badge uncoloured while every other phase rendered correctly.

### `update <id> <field> <value>`

Update a deliverable row's field **across every layer that can display it**, so the change can't be silently reverted by an overlay override or left stale in a click-row detail. **Fields**: `status`, `phase`, `scope`, `path`, `ref`, `effort`, `name`.

This action is a **coordinated multi-layer write** — a tracker cell can surface from up to three places (see "Overlay precedence"), so a single edit is not enough. Do all applicable steps, in order:

**Step 0 — Resolve the files** (standard project-agnostic locations under the submissions root):
- canonical markdown: `docs/project/submissions/submission-tracker.md`
- overlay sidecar: `docs/project/submissions/submission-tracker.overlay.yml` (`rows.<id>`)
- details sidecar (optional): `docs/project/submissions/submission-tracker.details.json` (`entries[].row_ids`)

**Step 1 — Markdown row cell (always).** Find the row whose first column is `<id>` and set the `<field>` cell to `<value>`. This keeps the human-readable, audit-facing canonical correct.

**Step 2 — Overlay upsert (only for overlay-managed fields: `status`, `path`, `ref`, `effort`, `name`).** The overlay **wins at render time**, so the cell change in Step 1 is invisible unless the overlay agrees. Upsert `rows.<id>.<field>: <value>` in `submission-tracker.overlay.yml` — create the `rows:` map and/or the `<id>:` entry if absent; if an override for this `(id, field)` already existed, overwrite it. (To make the `.md` cell authoritative instead, *remove* the `rows.<id>.<field>` override rather than leaving a stale one.) **`scope` / `phase` are structural / generator-owned — do NOT put them in the overlay; Step 1 alone is correct for those.**

**Step 3 — Click-row detail sync (for `path`; and status-hygiene).** In the `## Deliverable Details` section, if a `### <id> — …` block exists:
- when `<field>` is `path`, update that block's inline `**Path**: …` to match (add it if missing);
- regardless of field, **remove any `**Status**: …` fragment** from the detail line — the detail schema (mirrored by the details sidecar) carries **no status field**; status belongs to the row badge only, and a restated status is exactly what goes stale. Never write a `Status` into a detail block.
- If the id is covered by the details **sidecar** (`submission-tracker.details.json` `entries[].row_ids`), update the matching entry's `path` there too (or re-run `/tracker enrich-details <id>`), because the sidecar overrides the inline block.

**Step 4 — Re-render with PyYAML present.** Run `/tracker render` (below) using an interpreter that has PyYAML — the project console's venv if the console is installed, otherwise a system Python with `pyyaml` installed. If the renderer prints the `overlay.yml … PyYAML is not installed` WARNING, **stop and fix the environment** — that render ignored every overlay override and does not match the console.

**Step 5 — Verify in the running console, not a file open.** Confirm the change in the project console (it live-renders with the overlay applied and rewrites paths to clickable `/documents#path=…`). Find the port in that project's `tools/project-console/console.yaml` (`server.port`); a standalone browser open of `submission-tracker.html` cannot resolve the document links, and a console on another project's port shows a different tracker.

**Step 6 — Report** which layers were touched (md cell / overlay / inline detail / details sidecar) so the operator can see the change is coherent end-to-end.

```
/tracker update PI3 status "In Review"    # → md cell + overlay rows.PI3.status; detail Status stripped
/tracker update PA6 path "submissions/510k/predicate-analysis-v1.md"
                                          # → md cell + overlay rows.PA6.path + detail **Path** synced
/tracker update PI3 phase LMR1            # structural → md cell only (no overlay)
```

### `assess`

Auto-detect status mismatches by walking project paths.

**Steps**:
1. For each row, derive expected evidence path (from Path column or from milestone binding).
2. Resolve external-DHF paths through `taxonomy_path` (when `dhfs[].dhf_organization == external`).
3. For each path: glob expected files; compare to current `Status`.
4. Propose status flips (advisory; doesn't auto-modify):
   - File exists + status `Not Started` → propose `Done` or `Partial`
   - File missing + status `Done` → propose `Not Started` or flag as moved
5. Print proposed changes; user applies via `update` calls or by editing the markdown.

### `status [filter]`

Show summary counts in terminal.

```
/tracker status                # full summary by phase / scope / status
/tracker status QSub           # only QSub-phase rows
/tracker status engineering    # only Engineering Prerequisites
/tracker status not-started    # only Not Started rows
```

### `enrich-help`

Generate per-row LLM artifact help into `submission-tracker.help.json` —
the sidecar consumed by `render.py` when the user clicks the `(?)` icon
on a tracker row. Goal-driven: the agent reads project context (CLAUDE.md,
strategy docs, DHF READMEs, the row's bound obligations from the
dhf-manifest catalog, the resolved evidence file when present, the
composition-manifest entry) and produces structured help (description,
why-important-in-project, main_topics, regulatory_anchors).

Two-step: (a) `scripts/build-help-context.py` emits per-row context
bundles; (b) the parent (Claude) dispatches one `help-author` agent per
row in parallel — same fan-out pattern as `/dhf-manifest tier1-enricher`.

**Full playbook**: see `actions/enrich-help.md`. **Agent rubric**: see
`agents/help-author.md`. **Output sidecar**: cached with a per-row
context_signature so re-runs skip rows whose grounding hasn't changed.

```
/tracker enrich-help                  # all rows (cache-aware)
/tracker enrich-help <row-id>         # one row only (smoke test)
```

### `add-row` / `update-row` / `remove-row` / `list-user-rows` / `validate-rows` / `import-user-rows`

Model D — user-injected row registry. Rows that don't derive from the
milestone catalog × composition manifests × DHF evidence pipeline live in
`docs/project/submissions/tracker-user-rows.yml` and are merged into the
generator's row inventory by `generate.py`. The registry is **machine-managed**
— users edit only via these skill actions, not by hand. The skill enforces
schema conformance (project-adaptive vocabularies for scope / phase / effort /
status, resolved at validate time from `project.yml` + `regulatory.yml`); the
`user-row-author` agent drafts entries from freeform user requests anchored in
project context.

After any registry mutation, the action auto-runs `/tracker generate` so the
canonical markdown stays in sync. `generate.py` also emits a per-row
`submission-tracker.row-source.json` sidecar; `render.py` reads it to add a
small ★ "user-added" badge with hover-tooltip showing each row's `reason`.

```
/tracker add-row "<freeform description>"     # interactive, agent-drafted
/tracker update-row <id> "<change>"           # diff-style review
/tracker remove-row <id>                      # confirms before removing
/tracker list-user-rows                       # read-only summary
/tracker validate-rows [--strict]             # CI-friendly schema check
/tracker import-user-rows [--confirm]         # one-shot bootstrap from canonical
```

**Schema**: `schemas/user-row.schema.yml` (project-agnostic; allowed-value
sets resolved at runtime). **Validator**: `scripts/validate-user-rows.py`.
**Agent**: `agents/user-row-author.md`. **Action playbooks**: `actions/{add,
update, remove, list, validate, import}-*-row*.md`.

**Boundary vs catalog**: catalog-derived rows (`Q-PS125`, `PI16`, etc.) come
from the milestone catalog and are emitted by the generator's existing walks.
User-injected rows (`Q1`, `PA6`, `LMR1`, etc.) come from the registry. Both
appear in the canonical and the dashboard; the `(i)` chrome shows ★ on user
rows so reviewers know which is which.

### `enrich-details`

Generate per-row deterministic Deliverable Details into
`submission-tracker.details.json` — the sidecar consumed by `render.py`
when the user clicks the `(i)` icon on a tracker row. The block lists
Phase, Scope, Path, Primary REF, the full applicable REF list, and
optional Notes; everything is a deterministic projection of the row's
metadata + composition-manifest entry + obligations bound from the
dhf-manifest catalog.

This is the deterministic sibling of `enrich-help` — same fan-out
pattern, different output and lighter context load (no CLAUDE.md / DHF
README reading required, just the bundle + manifest + evidence
frontmatter).

**Multi-row attachment**: the bundle builder detects rows that share
the same artifact (same evidence path or same composition-manifest
entry — e.g., a Pre-Sub readiness row and the Final-Submission row
that both point at one SAD) and groups them. The agent emits one entry
with `row_ids: [<primary>, <linked>, ...]`; `render.py` attaches that
entry's body to every listed row, so authoring is one block per
artifact, not one per row.

Two-step: (a) `scripts/build-detail-context.py` emits per-row context
bundles; (b) the parent (Claude) dispatches one `details-author` agent
per row-group in parallel.

**Boundary vs `enrich-help`**: `help` produces the LLM artifact
explainer ("what is this, why does it matter HERE") for the `(?)`
panel; `details` produces the deterministic Phase/Scope/Path/REF
projection for the `(i)` panel. Run either independently.

**Full playbook**: see `actions/enrich-details.md`. **Agent rubric**:
see `agents/details-author.md`. **Output sidecar**: cached with a
per-row `context_signature` so re-runs skip entries whose grounding
hasn't changed.

```
/tracker enrich-details              # all rows (cache-aware)
/tracker enrich-details <row-id>     # one row only (smoke test)
```

When the sidecar exists, `render.py` overrides the markdown-inline
`## Deliverable Details` section with the sidecar content. When the
sidecar is missing, the legacy inline path is used unchanged.

### `help`

Show this usage guide.

## HCLS Portability — `tracker:` config block in `project.yml`

The `/tracker` skill is project-agnostic; per-project tuning lives in `project.yml`'s `tracker:` block. Every field has skill-shipped defaults — projects override only what their tool chain or vocabulary requires.

**Audit reference**: see `tasks/<person>/154-*` R10 for the portability assessment (10 of 14 design refinements portable as-shipped; 6 require this config block + plugin seams).

**Block schema (all fields optional):**

```yaml
tracker:
  status_vocabulary:                  # R2 — Lifecycle Status values
    states:
      - id: <slug>                    # internal id used in markdown + sidecar
        display_label: <text>         # badge label (supports `:vN` suffix)
        badge_color: --<css-var>      # CSS color var
        version_suffix: true|false    # append :vN at runtime per row's version
        aliases: [<other-strings>]    # values coerced to this state on parse

  lifecycle_plugin: <plugin-name>     # R3 — which plugin reads SoR lifecycle
                                      # default: confluence_comala
                                      # other: sharepoint_velocity, mfiles_approval,
                                      #        polarion, jira_status, windchill_state, none
                                      # plugins live at .claude/skills/tracker/plugins/lifecycle/<name>.py

  coverage_thresholds:                # R8 — obligation-coverage % → status mapping
    in_review_min: <pct>              # ≥ → In Review
    draft_min: <pct>                  # ≥ → Draft
    scaffold_max: <pct>               # < → "scaffold only" rationale

  row_id_schema:                      # R9 — stable row IDs for /tracker generate
    dhf_prefix_strategy: first-2-letters | manual
    dhf_prefix_map: { <leaf>: <prefix> }
    scope_prefixes:
      submission_admin: <prefix>
      submission_narrative: <prefix>
      qsub_specific: <prefix>
      lmr_prefix: '<template-with-{n}>'
    engineering_prefix: ENG

  display:                            # R6.5 — table density preferences
    scope_label_max_chars: <n>        # canonical names > N → shortened
    architecture_short_overrides:
      <leaf>: <short-label>           # explicit per-DHF override

  requirements_tracker_compat:        # R6.2 — forward-rename compat
    accepts: [jira, requirements_tracker]    # read both keys
    default_kind: jira
    # Future kinds: jira | azure_devops | servicenow | controlnet | github_issues | none
```

**Per-DHF tracker fields** (in `dhfs[].<leaf>` blocks, consumed by tracker):

- `architecture_name` — drives Scope vocabulary (skill reads this; falls back to leaf if unset)
- `marketed_name` — surfaced in Deliverable Details as commercial label
- `jira:` (or `requirements_tracker:`) — versions per DHF, drives milestone-binding validation
- `confluence:` — root page for deep-links from tracker rows
- `evidence:` — typed pointers to load-bearing artifacts (DTM xlsx, threat model, uFMEA, etc.) for `/tracker assess`

### Lifecycle plugin interface contract (R3)

A `LifecycleStatePlugin` reads source-of-record metadata and returns a normalized lifecycle state. Skill ships `confluence_comala` as the default; new HCLS contexts add a plugin file rather than fork the skill (mirrors change-control's `lib/review_plugin/` precedent).

**Interface** (`.claude/skills/tracker/plugins/lifecycle/base.py` — to be created in P1):

```python
class LifecycleStatePlugin:
    """Read normalized lifecycle state from a source-of-record metadata file."""
    name: str   # e.g. "confluence_comala", "sharepoint_velocity"

    def can_handle(self, file_path: Path) -> bool:
        """True if this plugin recognizes the file's metadata format."""

    def read_state(self, file_path: Path) -> dict:
        """Return {
          'state': str,        # one of status_vocabulary state ids
          'version': str|None, # e.g. 'v1.0.0' if known
          'signed': bool,      # explicit approval signatures present
          'signers': [str],    # signer identifiers when present
          'last_changed': iso-datetime,
          'source_id': str,    # SoR-specific id (page_id / item_id / etc.)
          'rationale': str,    # human-readable reasoning
        }"""
```

**Shipped plugins** (initial set):

| Plugin | Reads | Maps from |
|---|---|---|
| `confluence_comala` | `<!-- title: ... state: ... confluence: ... -->` frontmatter + `page-signatures` Comala macro | `state: published/draft/review-formal/frozen/released` → vocab states |
| `none` | n/a | Returns empty state; tracker falls back to file-existence heuristic |

**Future plugins (HCLS contexts):**

- `sharepoint_velocity` — SharePoint metadata + Velocity approval state
- `mfiles_approval` — M-Files object metadata + workflow state
- `polarion` — Polarion work-item status
- `jira_status` — Jira issue status as lifecycle state (for projects where Jira IS the doc-state SoR)
- `windchill_state` — Windchill object lifecycle state via PLM API

## Renderer details (project-agnostic)

The renderer (`scripts/render.py`) is **project-agnostic** — discovers Scope and Phase values from the markdown rather than hardcoding any vocabulary. This means a project using `Device | Per-Module | Both` for Scope works just as well as one using `Suite | PreOp | IntraOp | MgmtSvc`.

**Color assignments** are stable per value (deterministic palette cycle), so the same value gets the same badge color across runs. New values get the next color in the cycle.

**URL rewriting** (relative path → `/documents#path=<virtual>`) is the integration with project-console — clicking a path link in the dashboard opens the file in the Documents tab. External URLs (http/https/mailto), absolute paths, and pure anchors pass through unchanged.

## HTML Dashboard Features

- **5+ summary cards**: per-Phase + Engineering Prereqs + Grand Total
- **3-way filtering**: Status × Scope × Phase (AND logic). Empty subsections + phase sections auto-hide.
- **Per-Phase progress bars**: Done (green) / Partial (yellow) / Inherited (cyan) segments
- **Collapsible per-subsection categories**: click header to expand/collapse; Expand All / Collapse All buttons
- **Click-row help expansion**: content from Deliverable Details appendix; "Show All Help" mode toggle
- **Color-coded badges**: Status (6 values: Done/Partial/In Progress/Not Started/Inherited/N/A), Scope + Phase (project-discovered, stable color cycle)
- **Tier dividers**: per-Phase section bands with milestone-name badges; Engineering Prereqs gets its own divider
- **Sticky table headers**: scrollable tables stay headed
- **URL rewriting**: relative path links → console virtual paths
- **Mobile responsive**: tables become scrollable, cards stack 2-up
- **Self-contained**: no external CSS/JS dependencies

## Boundary contract — `tracker` (analysis) vs `dhf-manifest` (catalog)

`/tracker` is the **synthesis layer** for a project's regulatory readiness.
It does NOT author obligations; it consumes the catalog and **owns all
runtime project-state work** — pattern resolution, evidence reads, coverage
analysis, lifecycle verdicts.

| Source | Role |
|---|---|
| `/dhf-manifest` output (`<project>-dhf-manifest.json`) | Static catalog — obligation set per (DHF, canonical_role) with structured `applies_to: [{role, scope, artifact_pattern}]`, `criticality`, `extracted_requirements`, `reg_source`, `qms_grounding`. **Purely declarative** — no project-resolved paths, no status, no coverage. |
| `regulatory.yml` milestone bindings | Per-milestone required/optional posture (readiness-check vs strict vs full-DHF) |
| Project-tactical expectation sources (Q-Sub questions, strategy commitments, predicate findings, KOL feedback) | Row-level expectations not regulatory-cataloged but matter for THIS filing |
| Evidence on disk + Confluence frontmatter + Comala signatures + DTM xlsx | Lifecycle state + content coverage signal |

`/tracker assess` does ALL the runtime resolution:
1. Read dhf-manifest catalog (obligations + patterns + criticality)
2. **Resolve `artifact_pattern` → actual project file paths** (per row's DHF tree). This step is tracker's, not dhf-manifest's — the catalog declares the contract; the tracker resolves it for the project at hand.
3. Read each row's resolved evidence (file content + frontmatter + Comala signatures + DTM xlsx)
4. **Per-obligation coverage check** against `extracted_requirements` — addressed / partial / missing
5. **Required-vs-optional split** — milestone posture × catalog `criticality`
6. **Coverage %** — addressed / required obligations
7. **Lifecycle verdict** — Drafting / Drafted / In Review / Needs Revision / Approved / N/A
8. **Layer in project-tactical expectations** — Q-Sub questions, strategy commitments, predicate findings — tagged by source
9. Write to `submission-tracker.agent.json` (the agent sidecar — mutable analysis state)

Mental model: **dhf-manifest is the syllabus; `/tracker` is the scorecard.**

This skill never modifies `dhf-manifest` output — that's authored upstream by
the dhf-manifest skill. Tracker reads it as a static input. If a
project-tactical expectation surfaces here that should generalize back into
the catalog, that's a `/dhf-manifest` data-side change request (a new
framework distillation or scope-dimension entry) — not a tracker write.

## Best Practices
See [README.md](README.md) — consumed by `/best-practices` audit.

## Changelog
See [README.md](README.md) for version history.
