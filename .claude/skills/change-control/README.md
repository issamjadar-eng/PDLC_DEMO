# Change Control Skill — Design & Architecture

This document describes the design behind the `change-control` skill. It is **not loaded by Claude during normal skill operation** — it exists for human understanding and for future maintainers adding capabilities.

For skill usage, see `SKILL.md`. For the project-side conversation that drove this design (and the open questions still to resolve), see `tasks/ben/017-change-control-skill.md` in any project that has installed the skill.

> ⚠️ **STATUS: SCAFFOLD.** This skill is design-captured and structurally complete. All actions and connectors are stubs that print `NOT IMPLEMENTED`. The scaffold exists so the design lives in code, the extensibility seams are reserved, and implementation can proceed incrementally without rewrites.

---

## Role in the Ecosystem

`change-control` sits at the boundary between Claude Code's authoring environment (git-native, AI-accelerated, branch-friendly) and the regulated downstream stack (Confluence + Part 11 review plugin + Windchill). It owns the **freeze point** between the two — the moment when authority over a document transfers from git to Confluence.

```
┌──────────────────────┐    freeze     ┌──────────────────────┐    release    ┌──────────────────────┐
│  GitHub (drafting)   │ ────────────▶ │ Confluence + Comala  │ ────────────▶ │  Windchill (vault)   │
│  Claude Code authors │               │  Reviewers + Part 11 │               │  ECO + BOM + signed  │
│  PRs for tech review │               │  e-signatures        │               │  PDF + training      │
└──────────────────────┘               └──────────────────────┘               └──────────────────────┘
        ▲                                       ▲                                       │
        │                                       │                                       │
        │            unfreeze (in-chat)         │            (back-reference)           │
        └───────────────────────────────────────┴───────────────────────────────────────┘
```

The skill writes nothing in the user's source tree except the `state:` block on controlled docs and the `docs/.change-control/state.json` cache. It reads `change-control.yml` (project config), `project.yml` (deployment metadata), and the OS keychain (credentials). It owns one hook (`pre_tool_use_frozen.py`) and five actions (`init`, `freeze`, `unfreeze`, `status`, `release`).

---

## The Strategy Decision: Strategy C

Three strategies were considered for handling the GitHub ↔ Confluence boundary. Full discussion lives in task 017; the short version:

| Strategy | Authority model | Verdict |
|---|---|---|
| **A — Confluence is read-only mirror** | git always authoritative; reviewers comment only; every edit is a new PR | Rejected. Wordsmithing-as-PR doesn't survive contact with real reviewers. |
| **B — Confluence is final-mile editor** | git owns draft; Confluence owns review; final content exported back to git | Rejected. Lossy export, dual sources of truth at different lifecycle stages. |
| **C — Hybrid with freeze point** | git owns draft; at a defined milestone, doc freezes in git and publishes once to Confluence; Confluence owns review + sign-off; Windchill owns release | **Chosen.** |

**Why C wins:** it plays to each system's strengths. Claude Code is the right tool for drafting (AI-accelerated, branch-friendly, diff-native). Confluence is the right tool for human refinement, polish, and Part 11 sign-off. Windchill is the right tool for the released vault. Each system does one job; handoffs are unidirectional; the boundary between them is enforced by tooling (the PreToolUse hook), not by hoping the model behaves.

---

## The Freeze Enforcement Mechanism

The freeze point is enforced by a **PreToolUse hook** registered in `.claude/settings.json`. The hook fires before every Edit/Write/NotebookEdit call. Its execution path is:

1. Parse tool input JSON from stdin → target file path.
2. Lookup in `docs/.change-control/state.json` — if not a controlled doc, exit 0 immediately. **(Fast path; 99% of edits hit this.)**
3. If controlled, read frontmatter. If `state != frozen`, exit 0.
4. If frozen, classify the proposed edit (`lib/diff_classify.py`) — cosmetic vs substantive.
5. Emit a structured block message to stderr per Claude Code hook protocol; exit non-zero to block the tool call.

The block message is a **briefing** — not a generic "permission denied." It tells the user exactly what will be invalidated:

```
⚠️  FROZEN DOCUMENT — edit blocked

File:        docs/project/dhfs/pca-device/inputs/pump-occlusion.md
State:       frozen (Phase 2 — formal review in Confluence)
Frozen at:   2026-04-14 (commit a3f9c21)
Confluence:  page 458291, version 1
Jira ECR:    PP3500-1234
Windchill:   not yet released

Editing this file will UNFREEZE it, which means:

  1. The current Confluence page (458291) will be marked SUPERSEDED.
     Any in-progress reviewer comments or partial approvals will be lost.
  2. The Comala workflow will reset. Reviewers who already signed will
     need to sign again on the next freeze cycle.
  3. A new Confluence page version will be created on the next freeze.
  4. Jira ticket PP3500-1234 will be re-opened with a comment.

Proposed change:
  [diff or summary of what Claude was about to do]

To proceed, reply: "unfreeze pump-occlusion and apply"
To cancel,  reply: "cancel"
```

**Why in-chat consent rather than PR approval:** the decision should happen where the context lives. A PR-based gate puts the decision in front of a QA reviewer who has none of the context. The user, sitting in the Claude Code chat, has all of it. Hooks are also enforceable without ceremony: they fire on every edit, no exceptions, no escape hatch.

**Hook fatigue mitigation:** cosmetic edits (frontmatter-only, comment-only, changelog row appends, whitespace) get a lighter prompt. Substantive edits require typing a phrase that includes the document name (mirrors how Claude Code already handles destructive operations). The classifier is conservative — false positives (treating substantive as cosmetic) are much worse than false negatives.

---

## The Frontmatter Contract

Every controlled doc carries a `state:` block in its frontmatter:

```yaml
---
title: PP3500 Pump Occlusion Detection — Design Input
state: draft | frozen | released
doc_class: design-input          # determines whether ECR is required
frozen_at: 2026-04-14
frozen_commit: a3f9c21
confluence_page_id: 458291
confluence_version_at_publish: 1
jira_ecr: PP3500-1234
windchill_eco: null              # populated when Phase 3 completes
---
```

`state` is the field the hook checks. The other fields form the **traceability spine** across systems. After Phase 3 completes, the file is a permanent record of the handoff chain — git → Confluence → Windchill, all linked by IDs.

`doc_class` is keyed to the project's `change-control.yml` policy table. This is what enables the "Jira required only for certain doc classes" model (see open question #3 in task 017).

---

## Connectivity Architecture

The full options analysis lives in `tasks/ben/017-change-control-skill.md` under "Connectivity Options Analysis." This section captures only the **chosen stack** and the **extensibility seams**.

### Chosen stack (v1)

| Concern | Choice | Rationale |
|---|---|---|
| Confluence base API | Raw `httpx` (REST v2) | Narrow surface (~6 endpoints); async-ready; no wrapper lag |
| Markdown → Confluence rendering | `mark` (kovetskiy/mark) external binary | Battle-tested for the fidelity problem; frontmatter-driven |
| Comala / SoftComply | Raw `httpx` behind `ReviewPlugin` interface | No wrapper exists; abstraction lets project pick plugin |
| Jira API | Raw `httpx` (REST v3) | Symmetric with Confluence; ~5 endpoints |
| Auth (default) | Service account + OS keychain via `keyring` | Clean audit trail; no on-disk secrets |
| Auth (fallback) | `.env` per developer | For environments where keychain isn't viable |
| Deployment target (v1) | Atlassian Cloud | Strategic, simpler auth, MCP available chat-side |

### Connector layer

```
                    ┌──────────────────┐
                    │   Connector      │   <-- lib/_base.py
                    │  (httpx client + │       common base class
                    │   auth + retry)  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┬──────────────┐
              ▼              ▼              ▼              ▼
       ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
       │ Confluence │ │   Jira     │ │  Comala    │ │ Windchill  │
       │ Connector  │ │ Connector  │ │ Connector  │ │ Connector  │
       │ lib/       │ │ lib/       │ │ lib/       │ │ lib/       │
       │ confluence │ │ jira.py    │ │ comala.py  │ │ windchill  │
       │   .py      │ │            │ │            │ │   .py      │
       └─────┬──────┘ └────────────┘ └─────┬──────┘ └────────────┘
             │                             │
             │ shells out to               │ implements
             ▼                             ▼
       ┌────────────┐               ┌──────────────────┐
       │   mark     │               │  ReviewPlugin    │
       │  (binary)  │               │    interface     │
       └────────────┘               │  ┌────────────┐  │
                                    │  │  Comala    │  │
                                    │  │  Plugin    │  │
                                    │  ├────────────┤  │
                                    │  │ SoftComply │  │
                                    │  │ Plugin     │  │
                                    │  │  (stub)    │  │
                                    │  └────────────┘  │
                                    └──────────────────┘
```

### Extensibility seams (designed in, not implemented)

The scaffold reserves these seams so capabilities can be added without rewrites:

1. **`Connector` base class** (`lib/_base.py`) — every connector inherits common httpx client setup, retry/backoff, auth injection. Adding a new system (e.g., a different PLM) = subclassing this.
2. **`Authenticator` interface** (`lib/_base.py`) — `TokenAuthenticator` (v1) and `OAuth2Authenticator` (planned). Both implement `inject(request)`. Switching auth modes touches only the auth layer.
3. **`ReviewPlugin` interface** (`lib/comala.py`) — `ComalaPlugin` (v1) and `SoftComplyPlugin` (stub). Both implement `get_state`, `transition`, `supersede`, `list_approvals`. The action layer never knows which plugin is in use.
4. **Deployment flavor enum** (`lib/_base.py`) — `Cloud` (v1) and `DataCenter` (planned). Connectors branch on this for endpoint paths and auth specifics. A project picks its flavor in `change-control.yml`.
5. **Doc-class policy table** (`change-control.yml`) — declarative mapping of `doc_class` → `requires_jira_ecr` / `requires_part11_signature` / `target_confluence_space`. Adding new doc classes = editing the table, no code changes.
6. **Phase 3 (Windchill) is a stub** — `lib/windchill.py` and `actions/release.py` exist with the right signatures. The implementation is intentionally deferred until Phase 1 and 2 are working end-to-end.

### Complementary capability — Atlassian MCP

If the project also installs the official Atlassian MCP server, *interactive* Claude actions ("create me an ECR for this finding," "show me the Confluence page for pump-occlusion") work natively in chat without going through the skill. The skill's hook still owns freeze-time enforcement (because hooks run as standalone scripts outside Claude's tool-use loop, and MCP tools are not callable from a hook). The two coexist cleanly:

- **Skill owns:** freeze enforcement, freeze/unfreeze/release actions, traceability spine, audit trail
- **MCP owns:** ad-hoc chat-time queries, ticket creation from chat, page lookups

There is no double-coverage to resolve — the responsibilities don't overlap.

---

## What the Skill Does Not Do

Explicitly out of scope, to keep the boundary clean:

- **Markdown authoring.** That's Claude Code's job. The skill operates on files Claude wrote.
- **Confluence authoring.** Once a doc is in Phase 2, reviewers edit in Confluence. The skill is hands-off until release.
- **CAD / BOM management.** That's Windchill's job. The skill creates ECOs and attaches PDFs; it does not touch parts.
- **PR review workflow.** Technical review of drafts happens in GitHub PRs as normal. The skill enters the picture only when a doc enters formal review.
- **Risk file or trace matrix authoring.** Those are owned by the `medtech-docs` and (planned) `trace-matrix` skills. `change-control` only freezes their outputs.
- **Standards or guidance import.** That's `medtech-docs update-external-references`.

---

## Implementation Roadmap

Order of operations when implementation begins:

1. **`lib/_base.py`** — `Connector`, `Authenticator`, `DeploymentFlavor`. Pure interfaces.
2. **`lib/frontmatter.py`** — read/write `state:` blocks; trivial but foundational.
3. **`lib/diff_classify.py`** — cosmetic vs substantive classifier.
4. **`hooks/pre_tool_use_frozen.py`** — wire the hook end-to-end against a synthetic frozen doc; no real Confluence integration yet. Validate the briefing UX in real chats.
5. **`actions/init.py`** — install hook, create config, allowlist, state cache.
6. **`lib/jira.py` + `lib/confluence.py`** — Cloud connectors, raw httpx, token auth via keyring.
7. **`lib/comala.py`** — `ComalaPlugin` against a real Comala instance.
8. **`actions/freeze.py` + `actions/unfreeze.py`** — wire the connectors together.
9. **`actions/status.py`** — read-only spine view; useful for debugging by this point.
10. **Generalization pass** — validate against a second consumer project to confirm no project-specific assumptions leaked into the skill.
11. **`/sync-skills push`** — upstream to hitachi.
12. **Phase 3 (`lib/windchill.py` + `actions/release.py`)** — separate task, after Phase 2 is solid.
13. **v2 capabilities** — Data Center backend, OAuth 2.0 authenticator, SoftComply plugin.

---

## Best Practices for Future Maintainers

- **Never hard-code project specifics.** Confluence space keys, Jira project keys, doc-class policy — all in `change-control.yml`. The skill must work for any project that installs it.
- **Never weaken the hook to reduce friction.** If the hook is too noisy, the answer is smarter diff classification, not weaker enforcement. The hook is the only thing standing between AI authoring and accidentally invalidating a Part 11 signature.
- **Never add an action that operates on `released` docs.** Once a doc is in Phase 3, the skill is hands-off. Changes go through Windchill's own ECO process — not through the skill.
- **Keep the connector layer dependency-light.** Raw `httpx` is the choice precisely because the dependency surface is small and the action layer doesn't need to know about library quirks. Resist the urge to add convenience wrappers.
- **`README.md` is the design doc; `SKILL.md` is the manual.** When adding capabilities, update both — but keep the rationale in README, not SKILL.

## Changelog

- **0.14.1 (2026-09-08)**: **Test-suite hygiene + evidence tiers.** (1) `tests/test_attachments_macro.py` installed a fake `lib.attachments` into `sys.modules` and never restored it; the leak made `test_v010_bundle.py`'s Jira-renderer test patch one module object while `adopt_helper` resolved the other, so the suite made a **live HTTP request** to the placeholder host and failed on a 404 (order-dependent: passed alone, failed in the full run). Both tests now patch through `monkeypatch.setitem(sys.modules, "lib.attachments", ...)` — the seam the code under test actually resolves — so they are order-independent and restored after each test; the files' `__main__` runners delegate to `pytest.main` so fixture-taking tests still run directly. (2) **Three evidence tiers**, named the same way here and in the workbench-validation manifest: `unit` (no marker), `mocked` (`@pytest.mark.mocked`, hermetic run against a fake Jira/Confluence transport), `live` (`@pytest.mark.live`, opt-in via `--live`, needs `project.yml change_control.jira.base_url`; skipped with a stated reason otherwise). New `tests/conftest.py` registers the markers, adds the `--live` option, and installs an **autouse socket guard** that raises `NetworkAccessBlocked` from any non-`live` test that tries to open a connection — the hermeticity rule is now enforced, not assumed. (3) `tests/fakes.py` (fake `urlopen` response queue + fake cookie-bridge module) and `tests/fixtures/atlassian/` (two-issue search, empty search, 401 body) back a new `tests/test_jira_mocked.py`: table rendering incl. pipe escaping and the cookie header actually sent, empty-result placeholder, HTTP 401 → deferred-render comment + warning, cookie-bridge failure → no request made, plus one `live` smoke test. (4) Version pin aligned — SKILL.md frontmatter said 0.13.1 while `VERSION` said 0.14.0, which made the workbench-validation UUT pin ambiguous; both now 0.14.1. 143 passed / 1 skipped (live).
- **0.14.0 (2026-07-07)**: **Filed-body-only publish mode — `--strip-internal`.** `publish_helper` (`precheck` / `body` / `adf-body` / `html-body`) gained a `--strip-internal` flag and `TransformOptions.strip_internal`; when set, `transform_markdown` runs a new `strip_internal_zones()` step (`lib/markdown_transform.py`) that removes — **fence-aware** — every HTML-comment metadata block, every `🔒`-headed `<details>` container, and every `🔒`-marked table column, so the published Confluence body carries **only the filed body** transmitted to the regulator. Default (flag absent) is unchanged: `🔒` blocks round-trip as collapsed Confluence expands. Mirrors the submissions eStar `strip_internal` so the Confluence filed body matches the eStar exhibit; report surfaces `internal_zones_stripped {comments, containers, columns}`. Motivation: three-tier submission docs (metadata → `🔒 INTERNAL` apparatus → filed body) whose Confluence page should be the FDA-facing view. Project-agnostic — the only marker is the `🔒` three-tier sentinel.
- **0.13.1 (2026-06-08)**: Inbound-model cleanup — retired the superseded two-step `staging → promote` pattern. The `staging_target_root` config field (added in 0.12.0) already generalizes "where adopt lands," and projects now point it directly at their canonical Confluence-mirror root, so adopt writes content into its controlled home with no separate promote step. Removed the `promote` action (never-built stub `actions/promote.py` whose target prefix hardcoded a `docs/project/dhfs/` layout) plus its test block; reframed all `adopt` / `adopt-tree` docs (SKILL.md + `actions/adopt*.md` + helper docstrings) around `<staging_target_root>` instead of the hardcoded `docs/confluence-staging/` literal. No behavior change to `adopt` / `publish` / divergence detection — purely retires a dead path and the stale literals that advertised it. Skill stays project-agnostic (the only path is the project-configured `staging_target_root`).
- **0.13.0 (2026-04-29)**: Two coupled AUTO-rendered chrome blocks shipped together — every adopted Confluence page now mirrors Confluence's UI chrome locally, round-trip-safe (task 140).
  - **AUTO:PAGE-TITLE**: Adopt-side emits the page title (sourced from frontmatter `title:`, populated from the `getConfluencePage` response) as a visible H1 between sentinels at the top of the markdown body, mirroring Confluence's title bar. Suppressed when the body's first content block is already `# <page_title>` so markdown viewers don't double-render. New helper `_synthesize_page_title(body_md, page_title)` in `actions/adopt_helper.py` runs immediately after `normalize` and BEFORE every other expander, so subsequent passes (TOC walk, drift detection) see this as a stable AUTO region. Publish-side strip in `actions/publish_helper.py:_md_to_adf` recognizes the OPEN sentinel, walks to CLOSE, and emits NOTHING — Confluence renders its own title chrome from the API's `title` argument, not the body. No double title on round-trip.
  - **AUTO:TOC**: Adopt-side recognizes `extension key="toc"` in the body ADF (replacing the old solo `<!-- confluence-side: toc -->` zone marker for the toc key only — other extension keys keep their existing behavior). Normalizer (`lib/normalizer.py`) captures macroParams (`minLevel`, `maxLevel`, `style`, `outline`, `printable`, `include`, `exclude`) into a new `report.toc_macros` field and emits OPEN+CLOSE sentinels: `<!-- AUTO:TOC source=toc minLevel=N maxLevel=M position=P -->` ... `<!-- /AUTO:TOC position=P -->`. Action-layer expander `_expand_toc_macros(md, report)` runs LAST in `cmd_write` (after attachment-macro, child-index, stub-container, jira expanders) so the heading hierarchy reflects the fully-resolved body. Walks all ATX headings outside any AUTO region (skips CHILD-INDEX, JIRA-LIST, PAGE-TITLE, fenced code blocks) via `_walk_headings_outside_auto`, filters by `minLevel` / `maxLevel`, and renders an anchored bullet list with GitHub-style slugs (lowercase; spaces to hyphens; non-alphanumeric stripped except `-`/`_`; runs of `-` collapsed; duplicate-slug disambiguation `-1`, `-2` matching GitHub). Publish-side strip recognizes the OPEN sentinel and emits a single ADF `extension` node with `extensionKey="toc"` and `parameters.macroParams` reconstructed from the sentinel attrs — round-trips back to a single Confluence TOC macro on republish, no inline list duplication.
  - **Drift-detection passthrough**: Both AUTO:PAGE-TITLE and AUTO:TOC ride the existing `lib/divergence.py:strip_auto_regions` from v0.10.0 — that function pattern-matches `AUTO:[A-Z][A-Z0-9-]*` generically and was already kind-agnostic, so re-rendering chrome cannot trigger spurious conflicts in `classify_adopt` / `detect_divergence`. No change required to divergence.py.
  - **Tests**: 14 new in `tests/test_auto_chrome.py` covering both blocks: 5 PAGE-TITLE (emit when no matching H1, suppress when matching, emit when differing, `_md_to_adf` strip emits no H1, end-to-end roundtrip no double H1), 6 TOC (sentinel pair + rendered headings, no toc macro = no AUTO block, `minLevel` filter, headings inside other AUTO regions skipped, `_md_to_adf` strip emits single extension node, full roundtrip with no double TOC), 2 shared (`strip_auto_regions` removes both blocks, in-sync drift detection across re-rendered chrome), 1 slug helper sanity. 120/120 pre-existing tests still pass.
  - **Project-agnostic**: 0 hits for project-specific names across all touched files (normalizer.py, adopt_helper.py, publish_helper.py, test_auto_chrome.py).
- **0.12.0 (2026-04-29)**: Project-level config + repeatable verification + portability story (task 139).
  - **Phase A — `project.yml change_control` block**: New top-level config block carries cloud_id, base_url, configured spaces (key + name + staging_target_root + title_prefixes_to_strip), the canonical roundtrip `test_target` (space_key, parent_page_id, parent_title, title_prefix), and the cross_page_source_map (per-page-id list of `(filename, source_page_title)` hints). New `lib/config.py` exposes typed dataclasses (`ChangeControlConfig`, `SpaceConfig`, `TestTarget`, `CrossPageSourceEntry`) plus `read_change_control_config(project_root)`. Three action helpers wired to consult config defaults when CLI flags are blank: `actions/adopt_helper.py` (--base-url, --space-key + cross-page source-map fallback via `lib/cross_page_resolve.project_config_source_map`), `actions/adopt_tree.py` (--base-url, --space-key, --target-root from the configured space's `staging_target_root`), `actions/publish_helper.py upload-images` (--base-url). CLI flags continue to override — backward-compatible. Skill code stays project-agnostic; the only project names live in `project.yml`.
  - **Phase B — `verify` action**: New `actions/verify.py` + `actions/verify.md` — repeatable smoke tests that prove the skill works against the configured `test_target`. Sub-actions: `audit` (config-only, no live calls), `orphan-file`, `cross-page-resolution`, `drift-detection`, `all`. Each writes a structured JSON report to `tasks/<person>/_scratch/verify-<kind>-<date>.json` (gitignored personal scratch) with shape `{kind, date, config, steps[{name, ok, details}], ok}`. The agent procedure in `verify.md` orchestrates the live MCP/cookie-bridge calls; the Python helper handles config audit + report writing. The `verify` action is the canonical "is the skill working" smoke test for any consumer project — same code, different `test_target` per project.
  - **Tests**: 109/109 pass (91 baseline + 10 new in `tests/test_config.py` covering the loader + dataclass coercion + repo project.yml live load + 8 new in `tests/test_verify.py` covering report shape + scratch-path resolution + live audit). Live `verify audit` against this repo's project.yml passes — config-loaded, test-target-configured, cross-page-source-map-present (3 entries) all true.
  - **Live work deferred**: Phases 1 (cross_page_source_map population for IntraOp DTM/DDP/Phase1), 2 (live IntraOp cleanup), 3 (Pre-Op pass-2 re-adopt of 51 pages), 4 (Mgmt Services pass-2 re-adopt of 36 pages), 5 (orphan-file verify against AI_PDLC_INT_TEST) all require Chrome/web-control to be up. Chrome was offline on session start; deferred to next session — every code path is in place and `/web-control launch` followed by `/change-control verify orphan-file` will exercise the canonical smoke test end-to-end.
  - **Portability story**: A new project adopting this skill simply (1) installs the skill from the registry, (2) adds a `change_control:` block to its own `project.yml` with its cloud_id / base_url / spaces / test_target, (3) runs `/change-control verify audit` to confirm the wiring, then `/change-control verify all` to exercise every flow. No fork of the skill code required.
- **0.11.0 (2026-04-29)**: Two coupled fixes that close the round-trip contract for attachments (task 134).
  - **Phase A — Inbound: cross-page UNKNOWN_MEDIA_ID resolution**: The Atlassian REST `body.atlas_doc_format` endpoint emits the literal string `"UNKNOWN_MEDIA_ID"` for media nodes whose attachment lives on a different page than the one being fetched. Storage XHTML preserves the original `<ri:attachment ri:filename="X.docx" ri:content-title="Source Page Title">`. Normalizer (`lib/normalizer.py`) now detects these and tracks them in `NormalizationReport.cross_page_unknowns` with structural position. New `lib/cross_page_resolve.py` provides pure functions to parse Storage XHTML, pair ADF unknowns to `<ri:attachment>` elements by traversal order, build resolved file-card markdown with full round-trip markers (`source-page=<id>`), and build graceful warning blockquotes when the source is unavailable. Action-layer resolver (`actions/adopt_helper.py:_resolve_cross_page_attachments`) dual-fetches Storage XHTML via the cookie bridge, looks up source-page-ids from a `--cross-page-source-map` JSON file, lists attachments on the source page by filename (new `lib/attachments.py:list_attachments_by_filename`), downloads binaries into THIS page's `images/`, and rewrites markdown placeholders. New flags on `adopt write`: `--storage-xhtml-input`, `--cross-page-source-map`. Graceful degradation: if cookies / search / download fail, emits `> ⚠️ Cross-page attachment: ... lives on Confluence page [...](...)` blockquote — NO `UNKNOWN_MEDIA_ID` literal in committed markdown.
  - **Phase B — Outbound: orphan-file (no-marker) round-trip**: Users can now drop a file in `<page>/images/` and reference it from markdown with a plain `[label](images/X.pdf)` link (NO `<!-- media -->` marker required) — `publish` will upload the file and Confluence will render it correctly. `_md_to_adf` (`actions/publish_helper.py`) recognizes both inline plain links and standalone-paragraph plain links to `images/` and emits `mediaSingle`/`mediaInline` with `PLACEHOLDER:images/<file>` ids. Image vs file decision via new `lib/mime.py` (`is_image_extension`, `decide_card_kind`). After publish + re-adopt, the markdown gets a proper round-trip marker — symmetric, no manual marker bookkeeping. Sidecar (`--emit-images-sidecar`) collects orphan files alongside marker-tagged ones, so `upload-images` picks them all up uniformly.
  - **Phase C — Tests**: 11 new tests in `tests/test_cross_page_and_orphan.py` covering: normalizer detection of UNKNOWN_MEDIA_ID, Storage XHTML parsing, position-based pairing, resolved markdown shape, graceful warning shape, plain link → mediaInline file-card emission, plain image link → mediaSingle image emission, marker-present no-double-handling, sidecar capture for plain links, mime decision, and a mocked end-to-end round-trip that covers ADF UNKNOWN → resolved markdown → publish ADF → standard re-adopt marker. 91/91 tests pass (80 baseline + 11 new).
  - **Re-adopt of 3 IntraOp pages (DTM `5619318892`, DDP `5622562963`, Phase1 `5734596655`)**: Cookie bridge offline; all three now show `> ⚠️ Cross-page attachment: ...` graceful warning instead of `<<file:UNKNOWN_MEDIA_ID>>`. Phase1's same-page media reference (`1441de9a-...`) preserved. Live cross-page resolution will populate filename + source-page when Chrome debug profile is up.
- **0.10.0 (2026-04-29)**: Five-phase v0.10.0 bundle (task 131) — child-index TOC + macro expanders + sentinel-aware diff. Every container page now shows a clickable bullet list of its children, both for pages with a `children`/`pagetree` body macro AND for stub-container pages whose Confluence body has no macro at all. Auto-rendered regions live between OPEN+CLOSE sentinel pairs and are stripped from `normalize_for_diff` so they never trigger spurious conflicts in `classify_adopt` / `detect_divergence`.
  - **Phase A — children/pagetree expander**: Normalizer (`lib/normalizer.py`) detects `extensionKey ∈ {children, pagetree}`, captures macro params (`depth`, `sort`, `excerpt`, `root`, `style`) into a new `report.child_index_macros` field, and emits OPEN+CLOSE sentinels: `<!-- AUTO:CHILD-INDEX source=<kind> depth=<n> position=<n> -->` ... `<!-- /AUTO:CHILD-INDEX position=<n> -->`. Action layer (`actions/adopt_helper.py:_expand_child_index_macros`) reads the manifest (new `--manifest-path` + `--repo-root` flags on `write`), filters pages by `parent_id == this.page_id`, sorts by manifest order (Confluence child_position), computes relpaths from the current file's target_path, and splices `- [<title>](<rel-target-path>)` bullets between the sentinels.
  - **Phase B — stub-container synthesis (Q5b)**: When the manifest says `is_container == True` AND the body has no child-index macro, action layer appends a synthesized `## Child pages\n\n<!-- AUTO:CHILD-INDEX source=stub-container position=0 -->` ... `<!-- /AUTO:CHILD-INDEX position=0 -->` block at end-of-body. Source attribute = `stub-container` distinguishes from real macros so publish-side fully strips it (no extension node emitted on round-trip).
  - **Phase C — jira macro expander**: Normalizer detects `extensionKey == "jira"`, captures `jqlQuery` / `columns` / `count` / `serverId` / `maximumIssues` into new `report.jira_macros`, emits OPEN+CLOSE: `<!-- AUTO:JIRA-LIST source=jira jql=<encoded> position=<n> -->` ... `<!-- /AUTO:JIRA-LIST position=<n> -->`. Action layer (`_expand_jira_macros`) issues a cookie-bridge GET against `/wiki/rest/api/3/search` and renders a `| Key | Summary | Status | Updated |` markdown table; on auth/endpoint failure falls back to `<!-- jira-list render deferred: <reason> -->` (never fails the adopt). Publish-side reconstructs the `jira` extension with the original JQL.
  - **Phase D — underline preservation**: ADF `mark.type == "underline"` round-trips via `<u>...</u>` HTML inline (CommonMark+GFM-compatible). Already wired in 0.9.0; verified on IntraOp Threat Model + SDP pages.
  - **Phase E — sentinel-aware diff (the keystone)**: New `lib/divergence.py:strip_auto_regions(md)` strips every `AUTO:<KIND>` ... `/AUTO:<KIND>` region (open through close inclusive), every paired `confluence-side: <kind>` zone region, and every solo `confluence-side` comment line. `normalize_for_diff` now wraps the raw normalizer with this strip. `lib/adopt_sync.py:classify_adopt` runs both `local_md` and `their_md` through `strip_auto_regions` before comparing, so re-rendering an AUTO region cannot trigger drift. Same change automatically benefits publish-side `detect_divergence`.
  - **AUTO-sentinel schema (permanent convention)**:
    - **Uppercase, dashed kinds** (this release): `CHILD-INDEX`, `JIRA-LIST`. Open form: `<!-- AUTO:<KIND> source=<source> [attr=val ...] position=<n> -->`. Close form: `<!-- /AUTO:<KIND> position=<n> -->`. The position counter is per-page, per-kind, monotonic from 0 — paired by exact match.
    - **Lowercase paired form** (0.7.0 / 0.8.0, retained): `<!-- confluence-side: attachments labels=<x> position=<n> -->` ... `<!-- /confluence-side: attachments position=<n> -->`. DO NOT rename.
    - **Lowercase solo form** (0.7.0): `<!-- confluence-side: <key> -->` for unrendered zone markers (toc, page-signatures). Single line, no close.
    - **Strip-vs-preserve rule**: `strip_auto_regions` removes every recognized AUTO/zone region (paired or solo) before diffing. Outside regions: byte-for-byte preserved. **Authors edit outside the AUTO region; the action layer regenerates inside on every adopt.**
  - **Tests**: 80/80 pass — 18 new in `test_v010_bundle.py` covering all five phases (children + pagetree capture, manifest-driven relpath rendering at multiple tree depths, stub-container synthesis trigger + suppression, jira capture + graceful-degrade, underline both directions, `strip_auto_regions` for child-index + paired attachments + solo legacy zone, classify_adopt `in_sync` keystone, classify_adopt still flags real conflict, publish-side reconstructs children/jira extension nodes, publish-side fully drops stub-container). All 62 prior tests green (attachments-macro 6/6, depth-and-manifest 10/10, file-cards 13/13, image-roundtrip 8/8, incremental-sync 13/13, url-encoding 12/12).
  - **Field validation**: re-adopted all 108 IntraOp pages with `--manifest-path` + `--repo-root`. Every depth-0 / depth-1 container shows the child TOC: the root `intra-op/product-overview/index.md` renders 22 children from its explicit `children` macro; stub containers like `software-documentation-level/index.md` get a synthesized TOC pointing at `v1.0.0.md` and `v2.0.0.md`. 6 IntraOp pages carry jira macros (SRA, STC, SOD, etc.) — all gracefully degraded to `<!-- jira-list render deferred: ... -->` since the local cookie bridge isn't connected this session; sentinels carry the original JQL for round-trip. Underline preservation verified on `software-development-plan-sdp/v1.0.0.md` (3 occurrences). **Keystone test passes**: re-running `adopt write` on an unmodified file (with no `--force`) returns `(in_sync, no-op): local body equals current Confluence body (auto regions ignored)` — exit 0, no conflict-prompt fires.
- **0.9.0 (2026-04-29)**: Incremental sync — adopt-direction drift detection + `adopt-tree --refresh` (task 130). Re-pulling Confluence is now non-destructive by default: local edits to staged pages are preserved, and real conflicts surface with side-by-side reconciliation files.
  - **New module** (`lib/adopt_sync.py`): `classify_adopt(target, page_id, their_md, ...)` returns one of `fresh / in_sync / only_theirs / only_yours / conflict` based on the three-way comparison `(snapshot at v_anc) vs local-current vs their_md`. Pure function — fully testable without filesystem state. Conflict-file emission helpers: `write_conflict_files()` writes `<doc>.confluence-side.md` (their body verbatim) + `<doc>.local-diff.md` (unified diff snapshot vs local); `render_conflict_prompt()` renders the structured stderr prompt with a machine-parseable `CHANGE_CONTROL_ADOPT_CONFLICT page_id=<id> target=<path>` header line.
  - **`adopt_helper.py write` drift detection**: before any write, the helper classifies; `in_sync` no-ops; `only_yours` preserves the local file and only bumps the frontmatter `adopted_from_version` pointer; `only_theirs` does the legacy overwrite + snapshot refresh; `conflict` writes the side-by-side files and exits 3 (or 2 on `--on-conflict abort`). New flags: `--on-conflict {prompt|overwrite|abort|merge}` (default `prompt`) and `--force` to skip the whole mechanism for explicit destructive re-pulls.
  - **`adopt_tree.py --refresh`**: incremental sync mode. Reads existing `<target-root>/.manifest.json`, re-discovers via `get_descendants_paginated(depth=10)`, and categorizes each page across six buckets: `in_sync`, `only_yours_pending` (local edits, no upstream change — preserved), `upstream_changed`, `added`, `removed` (NEVER auto-deleted; flagged for `git rm`), `predicted_conflict` (both sides changed). Summary printed BEFORE any I/O. New flags: `--refresh`, `--on-conflict`, `--manifest-path`. `--dry-run` works with `--refresh` for plan-only output. Manifest atomically rewritten ONLY on a clean run with no unresolved conflicts.
  - **Tests**: 62/62 pass — 13 new in `test_incremental_sync.py` covering all 5 classify_adopt branches, missing-snapshot fallback, `--force` override, refresh categorization (empty-delta + mixed add/remove/upstream/conflict), pure-categorize-no-IO invariant, and snapshot-integrity (only_theirs advances; conflict does NOT advance). All 49 prior tests green.
  - **Field validation**: dry-run refresh against the IntraOp 108-page tree categorized all pages correctly (in_sync for unchanged + upstream_changed for the version-1→2 simulation; predicted_conflict surfaces when local body diverges from snapshot).
- **0.8.1 (2026-04-29)**: URL-encode link destinations (task 129). CommonMark + GFM require percent-encoded characters (or angle-bracket-wrapped URLs) for markdown link destinations containing spaces, parens, ampersands, or non-ASCII; literal spaces inside `(...)` break the parser and the link renders as plain text. Surfaced on the IntraOp DTM page where 0.8.0's attachments-macro expander emitted file-list rows with literal-space URLs.
  - **Helpers** (`lib/markdown_transform.py`): new `md_link_dest(path)` (encodes via `urllib.parse.quote(path, safe="/_-.")`) + inverse `md_link_dest_decode(dest)`. Single source of truth for the encoding contract.
  - **Adopt-side encoding**: `_render_media` (image / file-card / mediaInline branches in `lib/normalizer.py`), `_render_attachment_table` (attachments-macro file-list rows), and `_download_images` post-resolve placeholder rewrite (file-card + image paths) all run the URL slot through `md_link_dest`. Bracketed link text stays human-readable; only the `(...)` slot is encoded.
  - **Publish-side decoding** (`actions/publish_helper.py`): `_md_to_adf:_emit_media_node` decodes the URL slot via `md_link_dest_decode` before deriving the `PLACEHOLDER:<relpath>` id and the `source_relpath` sidecar entry, so `upload-images` finds the on-disk file under its actual (un-encoded) name.
  - **Tests**: 49/49 pass — 12 new in `test_url_encoding.py` (helper unit tests for spaces / parens / ampersands / non-ASCII / no-op + roundtrip; normalizer encoding for image and file-card branches; full ADF→md→ADF roundtrip with spaces decoding back to original relpath; no double-encoding on safe filenames), 1 existing test in `test_attachments_macro.py` updated to assert encoded form, all other 36 prior tests green.
  - **Field validation**: re-adopted IntraOp 108-page tree; DTM page now renders `[FORM-000105316 - DTM - Design Traceability Matrix.xlsx](images/FORM-000105316%20-%20DTM%20-%20Design%20Traceability%20Matrix.xlsx)` — clickable in GitHub markdown preview.
- **0.8.0 (2026-04-29)**: Attachments-macro expander (task 128). Confluence's `attachments` macro extension is now expanded inline at adopt time with the live attachment list, while still round-tripping correctly through publish:
  - **Normalizer** (`lib/normalizer.py`): new `attachment_macros: list[dict]` field on `NormalizationReport`. When the walker encounters an `extension` node with `extensionKey="attachments"`, it captures the macro's `labels` / `name` / `pageSize` / `_parentId` parameters and emits an OPEN+CLOSE sentinel pair carrying a position marker — `<!-- confluence-side: attachments labels=<x> position=<n> -->` ... `<!-- /confluence-side: attachments position=<n> -->`. Other extension keys retain the prior single-sentinel shape (back-compat).
  - **Attachments lib** (`lib/attachments.py`): `list_attachments(...)` accepts `expand_labels=True` to also pull `metadata.labels.results[]` — required by the expander to filter by macro label.
  - **Adopt helper** (`actions/adopt_helper.py`): new `_expand_attachment_macros(...)` runs after `normalize()` and before `write_snapshot()`. Fetches the page's attachment list once (with labels), filters per-macro by labels (comma-separated → OR semantics), renders a `| Filename | Size | Modified | Labels |` markdown table inside the sentinels, and feeds unique attachment filenames into the existing `_download_images` infrastructure as synthetic image refs. Failure modes (cookie/auth/HTTP) degrade gracefully — sentinels stay in place for re-adopt.
  - **Publish helper** (`actions/publish_helper.py`): both `_md_to_storage_html` and `_md_to_adf` recognize the OPEN-form `<!-- confluence-side: attachments [labels=...] [position=...] -->`, skip everything until the matching CLOSE sentinel (paired by position marker), and emit a single `extension` ADF node with `extensionKey="attachments"` and `parameters.macroParams` reconstructed from sentinel attrs (`labels`, `name`).
  - **Markdown transform fix** (`lib/markdown_transform.py`): `strip_leading_html_comment` now skips single-line comments and explicit `confluence-side` sentinels — it previously could eat a leading attachments OPEN sentinel (a real bug surfaced by the round-trip flow).
  - **Tests**: 37/37 pass — 6 new in `test_attachments_macro.py` (normalizer capture, distinct positions, label-OR filter, splice rendering, publish strip, ADF→md→ADF round-trip), 31 prior all green.
  - **Field validation**: re-adopted IntraOp 108-page tree (21 pages carry attachments macros); spot-checked DTM (`v1.0.0`) — actual + outdated XLSX/DOCX file lists rendered correctly with download links. Roundtrip: published two macros to AI_PDLC_INT_TEST page `6783860744` (parent folder `6768394270`) and confirmed via DOM eval that Confluence renders the file-list chrome natively for both `actual` and `outdated` filters.
- **0.7.0 (2026-04-29)**: Confluence-pull production hardening. Three coupled fixes shipped during a real 195-page pull (tasks 124, 125, 126):
  - **Image roundtrip** (`lib/normalizer.py`, `actions/{adopt_helper,publish_helper}.py`): media-node metadata capture (`id`, `collection`, dimensions, `fileName`); `--download-images` flag on adopt; `_md_to_adf` emits `mediaSingle`/`mediaInline` placeholders with `PLACEHOLDER:<relpath>` ids; new `publish_helper.py upload-images` and `patch-adf` subcommands close the chicken-and-egg with cookie-bridge upload + ADF id swap + `updateConfluencePage`. Cookie-bridge package-collision fix in `lib/attachments.py` (broken since 0.6.0; never hit in production).
  - **Depth-unbounded discovery + manifest as first-class artifact** (`lib/confluence_mcp.py`, new `lib/manifest.py`): `getConfluencePageDescendants` with no explicit depth silently truncates at depth=2 — fixed via `get_descendants_paginated(page_id, depth=10, page_limit=250)` with cursor pagination + silent-truncation guard. New `lib/manifest.py` with `Manifest` + `ManifestPage` dataclasses, atomic read/write, pure `plan_paths()` planner that becomes the canonical path-derivation function. Manifests land at `<staging-root>/<topic-root>/.manifest.json` — committed artifacts, co-located with data.
  - **File-card rendering + filename fallback** (`lib/normalizer.py`, `lib/attachments.py`, `actions/adopt_helper.py`): `mediaInline` branch added (was silently dropped); `_render_media` decides image vs file-card by `attrs.type`+extension and emits link-syntax `[<<file:UUID>>](images/UUID.bin)<!-- media [inline ]id=... -->` placeholder for filename-less file-cards; new `list_attachments_by_uuid()` looks up real filenames + correct extensions via Confluence v1 REST `child/attachment?expand=extensions`; `_download_images` batches per-page lookup, resolves titles, post-rewrites markdown placeholders. Plus fuzzy parent-IS-topic collapse in `plan_paths` (longer slug starts-with shorter + `-`) eliminates redundant nested folders when parent has a parenthetical-disambiguator suffix the child topic doesn't.
  - **Tests**: 31/31 pass — 10 manifest, 8 image-roundtrip, 13 file-cards.
- 0.1.0 (2026-04-14): Initial scaffold. Design captured in SKILL.md and README.md. All actions and connectors are stubs that print `NOT IMPLEMENTED`. Extensibility seams reserved: `Connector` base class, `Authenticator` interface, `ReviewPlugin` interface, deployment-flavor enum. Targets Atlassian Cloud first; Data Center planned for v2. Created under task 017.
