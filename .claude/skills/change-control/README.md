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
Jira ECR:    PROJECT-1234
Windchill:   not yet released

Editing this file will UNFREEZE it, which means:

  1. The current Confluence page (458291) will be marked SUPERSEDED.
     Any in-progress reviewer comments or partial approvals will be lost.
  2. The Comala workflow will reset. Reviewers who already signed will
     need to sign again on the next freeze cycle.
  3. A new Confluence page version will be created on the next freeze.
  4. Jira ticket PROJECT-1234 will be re-opened with a comment.

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
title: PROJECT Pump Occlusion Detection — Design Input
state: draft | frozen | released
doc_class: design-input          # determines whether ECR is required
frozen_at: 2026-04-14
frozen_commit: a3f9c21
confluence_page_id: 458291
confluence_version_at_publish: 1
jira_ecr: PROJECT-1234
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
10. **Generalization pass** — validate against `../../projects/medtech-project/`.
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
