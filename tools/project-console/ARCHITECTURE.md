# project-console — Architecture & Rules

**Status:** Definitive architecture for `tools/project-console/`. Changes to anything in this document require an explicit decision recorded in the Changelog at the bottom.

`project-console` is the local web UI for exploring this PDLC demo project. It hosts **agents** (single or panel domain agents) for interactive exploration, a **documents** explorer that browses the project tree with auto-generated summaries, **dashboards** over project artifacts, and **workflows** (parameterized jobs that analyze inputs against project data). All LLM calls flow through a Claude Pro/Max subscription — no API keys, no per-call costs.

It is project tooling, not device code. It does not ship with the device, is not part of the DHF, and never appears in a regulatory submission.

---

## 1. Goals & non-goals

### Goals
- Single local web app that surfaces project state to humans (and demo audiences).
- Chat with project-grounded domain agents — solo or as panels — using a Claude Pro/Max subscription.
- Run parameterized workflows (e.g., "analyze this roadmap against our internal docs") with streaming progress.
- Ask questions *about a dashboard* using an embedded chat sidecar scoped to that dashboard's data.
- Add a new dashboard, domain agent, or workflow by dropping in a single file. No framework changes.
- Run identically on macOS and WSL with one command.
- Reviewable end-to-end: every file readable without a build step or bundler.

### Non-goals
- Not a production app. No auth, no multi-user, no deployment story.
- Not a data store. No database, no Redis, no background workers.
- Not a writer into project state. The console never modifies `docs/`, `project.yml`, `src/`, or any DHF artifact.
- Not a substitute for the device firmware, DHF, or submission packages.

---

## 2. Stack

| Layer | Choice | Why |
|---|---|---|
| Language | **Python 3.12+** | Agent SDK has a first-class Python path; matches the rest of the project's tooling. |
| Env / deps | **uv** | Single static binary; identical lockfile behavior on macOS and WSL; no native-module surprises. |
| Web framework | **FastAPI** | Native SSE for chat and workflow streaming; auto-reload in dev; minimal boilerplate. |
| Templates | **Jinja2** | Reloads on every request in dev — edit HTML, refresh, done. No bundler. |
| Frontend | **Vanilla JS + EventSource** | Zero build step. Optional Alpine.js for sprinkles. No CDN-loaded assets — everything vendored under `console/web/static/`. |
| LLM client | **claude-agent-sdk** (Python) | Authenticates via Claude Code's OAuth session — bills against Pro/Max, not an API key. |

---

## 3. Authentication model — Claude Pro/Max only

This is the central rule that makes the whole tool free to run.

- The console authenticates **only** via the Claude Code OAuth session on the host machine.
- The Agent SDK picks up that session automatically when no `ANTHROPIC_API_KEY` is set in the environment.
- On startup the console **must**:
  1. Verify a Claude Code session exists. If not, hard-fail with setup instructions (`claude login` or equivalent).
  2. If `ANTHROPIC_API_KEY` is set in the environment, **refuse to start** and tell the user to unset it. The console does not support API-key auth — not as a fallback, not behind a flag.
- Rationale: the entire point of this tool is to demonstrate Claude-powered workflows at zero marginal cost. Allowing an API-key fallback would silently undermine that guarantee.

---

## 4. Information architecture

The console has **four top-level sections**, plus a landing page:

| Section | What it is | LLM? |
|---|---|---|
| **Agents** | Chat with domain agents — either solo or as panels (teams of domain agents). | Yes, streaming. |
| **Documents** | Browse the project document tree (`docs/`, `tasks/`, pinned files). View files in a format-aware renderer; Claude auto-summarizes text-like files on view. | Rendering: no. Auto-summary: yes, streaming. |
| **Dashboards** | Deterministic HTML views over project data, optionally with a chat sidecar that understands the dashboard's data. | Rendering: no. Sidecar: yes. |
| **Workflows** | Parameterized jobs with inputs (file upload, text, select) → streaming progress → result view. | Yes, streaming. |

The landing page (`/`) shows project identity (name, device, regulatory pathway — pulled from `project.yml`) and cards for each installed section. The shell template `_base.html` carries a top nav linking to each section.

### Routes

```
/                                       landing page
/dashboards                              index of dashboards
/dashboards/{name}                       render one dashboard (HTML)
/dashboards/{name}/chat/stream           SSE sidecar (only if CHAT_ENABLED)
/agents                                  index of domain agents (solo + panels, badged)
/agents/{name}                           chat UI
/agents/{name}/stream                    SSE chat endpoint
/documents                               document tree root (docs/, tasks/, pinned files)
/documents/browse/{virtual_path}         directory listing at a virtual path
/documents/view/{virtual_path}           format-aware file view
/documents/raw/{virtual_path}            raw file bytes (downloads, PDF embeds, images)
/documents/summary/{virtual_path}        SSE — Claude-generated summary of a text file
/workflows                               index of workflows
/workflows/{name}                        input form
/workflows/{name}/runs/{run_id}          result view; SSE stream while running
```

---

## 5. Layout

```
tools/project-console/
├── ARCHITECTURE.md              # this file — definitive rules
├── README.md                    # quickstart + how to add dashboards/agents/workflows
├── pyproject.toml               # uv-managed
├── uv.lock
├── run.sh                       # one-command launcher (uv sync + uvicorn --reload)
├── .gitignore                   # ignores data/, __pycache__/, .venv/
├── console/
│   ├── __init__.py
│   ├── __main__.py              # `python -m console serve`
│   ├── app.py                   # FastAPI app factory + lifespan (auth check)
│   ├── config.py                # loads project.yml, resolves repo root
│   ├── auth.py                  # Pro/Max session check; refuses API key
│   ├── dashboards/
│   │   ├── __init__.py
│   │   ├── registry.py          # auto-discovers dashboard modules
│   │   ├── _context.py          # ctx object passed to render() / chat_context()
│   │   ├── sidecar.py           # dashboard-chat glue (uses _dashboard_analyst)
│   │   ├── tracker.py           # example dashboard
│   │   └── compliance.py        # example dashboard
│   ├── chat/
│   │   ├── __init__.py
│   │   ├── router.py            # /agents/* routes
│   │   ├── domain_agents.py     # loads + validates domain_agents/*.md
│   │   ├── panels.py            # panel orchestration (round-robin v1)
│   │   ├── sources.py           # resolves source globs → live context
│   │   └── sdk_client.py        # Agent SDK wrapper
│   ├── documents/
│   │   ├── __init__.py
│   │   ├── router.py            # /documents/* routes
│   │   ├── tree.py              # dir walk, path resolver, breadcrumbs, excerpts
│   │   ├── renderer.py          # format dispatch: md → html, pdf, text, image, …
│   │   └── summary.py           # Claude-backed summary streaming
│   ├── workflows/
│   │   ├── __init__.py
│   │   ├── registry.py          # auto-discovers workflow modules
│   │   ├── types.py             # FileInput, TextInput, SelectInput, ProgressEvent, ResultEvent
│   │   ├── runner.py            # run lifecycle, run IDs, SSE plumbing
│   │   ├── router.py            # /workflows/* routes
│   │   ├── roadmap_gap_scan.py  # example workflow
│   │   └── predicate_comparison.py
│   └── web/
│       ├── static/              # css, js (vendored, no CDN)
│       │   ├── console.css
│       │   └── chat.js          # shared SSE client (agents + dashboard sidecars)
│       └── templates/
│           ├── _base.html       # shell: nav + layout
│           ├── index.html       # landing with three section cards
│           ├── dashboards_index.html
│           ├── dashboard.html   # dashboard view with optional chat panel
│           ├── agents_index.html
│           ├── chat.html        # full-page chat UI (solo or panel)
│           ├── workflows_index.html
│           ├── workflow_form.html
│           └── workflow_run.html
├── domain_agents/
│   ├── kol/                     # group: Key Opinion Leaders
│   │   ├── _group.md            # group metadata (title, description, order)
│   │   ├── kol-paul.md          # solo example
│   │   └── kol-panel-pp3500.md  # panel (members: [kol-paul, ...])
│   ├── core-team/               # group: Core Team
│   │   ├── _group.md
│   │   ├── program-manager.md
│   │   ├── regulatory-affairs.md
│   │   ├── clinical-affairs.md
│   │   └── core-team-panel.md   # panel over the three above
│   └── _dashboard_analyst.md    # system agent (future), used by dashboard sidecars
└── data/                        # generated artifacts — gitignored
    ├── uploads/{run_id}/        # workflow input files
    └── runs/{run_id}/           # workflow output artifacts
```

---

## 6. App models

### 6.1 Dashboards

A dashboard is a Python module under `console/dashboards/` exposing:

```python
NAME = "tracker"
TITLE = "Submission Tracker"
DESCRIPTION = "DHF deliverable status across the program."

CHAT_ENABLED = True   # optional; default False

def render(ctx) -> str:
    """Pure function: project context → HTML string."""

def chat_context(ctx) -> dict:
    """Optional. Structured data handed to the chat sidecar on every turn.
    Only called if CHAT_ENABLED is True."""
    return {"deliverables": [...], "summary": "...", "source_files": [...]}
```

Rules:
- **Pure read.** `render()` reads from `ctx` and must not write outside `tools/project-console/data/`.
- **`render()` never calls the LLM.** Dashboards are deterministic visualizations of existing data. LLM behavior lives in the chat sidecar (if enabled) or in a workflow.
- **Auto-discovery.** `registry.py` imports every module in `console/dashboards/` at startup. Adding a dashboard = adding one file.
- **HTML only.** No JSON APIs, no client-side rendering frameworks. Server renders, browser displays.
- **Chat sidecar** is opt-in. When `CHAT_ENABLED = True`, the dashboard page embeds a collapsible chat panel (collapsed by default, with an "Ask about this dashboard" button to expand). The panel is powered by the built-in `_dashboard_analyst` domain agent, which receives the dashboard's title, description, and `chat_context()` output on every turn.
- **Context cap.** `chat_context()` output is serialized to JSON and capped at **50 KB**. If a dashboard exceeds the cap, `sidecar.py` logs a warning and truncates. Dashboards that want to expose more data should summarize, aggregate, or point at source files by path.

### 6.2 Agents — domain agents (solo + panel, grouped)

A **domain agent** is a markdown file under `domain_agents/{group}/` with YAML frontmatter. Agents are organized into **groups** — each group is a subdirectory, optionally containing a `_group.md` metadata file.

**Group metadata (`_group.md`):**
```markdown
---
title: Key Opinion Leaders
description: Clinical and technical thought leaders informing PP3500 design inputs.
order: 1
---
```

If `_group.md` is absent, the group title is derived from the directory name. Groups are sorted by `order`, then title. The agents index page renders one section per group, with panels highlighted above individual agents.

Agent files within a group come in two kinds:

**Solo domain agent:**
```markdown
---
name: kol-panelist
title: KOL Panelist
kind: solo               # default if omitted
model: claude-opus-4-6
sources:
  - docs/project/input-analysis/**/*.md
  - docs/external/clinical/**/*.md
description: Simulated key opinion leader for PCA infusion devices.
---

You are a digital twin of a key opinion leader in patient-controlled analgesia...
(full system prompt continues)
```

**Panel domain agent:**
```markdown
---
name: kol-panel
title: KOL Advisory Panel
kind: panel
members:
  - pain-physician          # references other domain agents by name
  - hospital-pharmacist
  - biomedical-engineer
moderator: round-robin      # v1 only supports round-robin
sources:                    # shared across members, merged with each member's sources
  - docs/project/input-analysis/**/*.md
description: Three-voice KOL panel covering clinical, pharmacy, and engineering perspectives.
---

Panel framing: You are participating in an advisory panel reviewing a PCA infusion
device. Speak in your role. (This framing is prepended to each member's own system prompt.)
```

Rules:
- **Drop-in.** Adding a domain agent = adding one markdown file to a group directory. Adding a group = creating a new subdirectory (optionally with `_group.md`). No code change.
- **Unique names across groups.** The `name:` field must be globally unique so panels can reference members by name regardless of group. Panels may reference members in any group.
- **Live source pulls.** On every turn, `sources.py` re-reads files matching the domain agent's `sources` globs and injects them as context. No caching yet.
- **Streaming.** Responses stream over SSE so the UI feels responsive.
- **Stateless across sessions.** Conversation state lives in browser memory only. No server-side persistence of chat history.
- **Panel orchestration (v1).** Round-robin only: on each user message, each member responds in turn, streamed one after the other. The panel's framing is prepended to each member's system prompt. Auto-moderator panels (LLM picks the next speaker) are deferred.
- **System agents.** Names beginning with `_` (e.g., `_dashboard_analyst`) are system agents — they power dashboard sidecars and do not appear in the `/agents` index.
- **Scope is advisory, not enforced.** System prompts tell the model what it is; we don't sandbox tool access beyond that. This is a demo, not a security boundary.

### 6.3 Documents

The Documents section is a read-only file browser over selected project roots. Its purpose is to let a demo audience see *what's in the project* without needing shell access, and to get a fast Claude-generated summary of any text file they open.

**Roots exposed (v1):**
- `docs/` — DHF artifacts, standards, external frameworks, project documentation
- `tasks/` — team task tracking
- `project.yml` — pinned as a top-level file

**Not exposed:** `src/` (device code — console is blind to it by architecture rule), `.claude/` (internal tooling), anything outside the repo.

**Virtual paths.** The browser uses "virtual paths" of the form `docs/project/input-analysis/kol-feedback/KOL-0001-…md`. The first segment selects the root; everything after is relative to that root. The path resolver in `tree.py` uses `Path.resolve()` + `relative_to()` to reject any path that escapes its declared root (defense against traversal).

**File rendering (v1):**

| Format | Treatment |
|---|---|
| `.md` | YAML frontmatter parsed into a collapsible metadata panel; body rendered to HTML via `python-markdown` (tables, fenced_code, toc, sane_lists extensions). |
| `.html` / `.htm` | Displayed in a sandboxed `<iframe src="/documents/raw/…">` (no JS execution). |
| `.txt` / `.yml` / `.yaml` / `.json` / `.csv` / `.toml` / source code | Monospace block. |
| `.pdf` | Embedded via `<object>` using browser's native PDF viewer. |
| `.png` / `.jpg` / `.gif` / `.svg` / `.webp` | Inline `<img>`. |
| Anything else (including `.docx`, `.xlsx`) | "Preview not available" placeholder with a Download button. DOCX inline rendering is deferred. |

All file types expose a **Download** button that serves the raw bytes via `/documents/raw/{virtual_path}`.

**Auto-summary.** When a user opens a view page for a `.md`, `.html`, or text file, the page automatically fires a `POST /documents/summary/{virtual_path}` which streams a Claude-generated summary back via SSE. A spinner is shown while the first token is pending, and tokens stream into a dedicated summary panel above the file body. The summary is generated fresh on every view — not cached. Binary formats (PDF, images) do not auto-summarize in v1.

Rules:
- **No modification.** The console never writes to `docs/`, `tasks/`, or `project.yml`. Raw file responses are read-only.
- **Path traversal containment.** Every incoming virtual path is resolved against an explicit allowlisted root and verified with `relative_to()`. Any path that escapes is returned as 404.
- **Summary size cap.** Documents larger than **80 KB** are truncated before being sent to the model (with a truncation marker appended). Prevents accidental context-window overflow on large docs.
- **Summary only for text.** Auto-summary endpoint refuses (400) for non-text file kinds.

### 6.4 Workflows

A workflow is a Python module under `console/workflows/` exposing:

```python
from console.workflows.types import FileInput, SelectInput, ProgressEvent, ResultEvent

NAME = "roadmap-gap-scan"
TITLE = "Roadmap vs. Internal Docs Gap Scan"
DESCRIPTION = "Upload a product roadmap; get a gap analysis against DHF/SOP coverage."

INPUTS = [
    FileInput("roadmap", accept=[".md"]),
    SelectInput("scope", options=["regulatory", "architecture", "testing"]),
]

async def run(ctx, inputs):
    yield ProgressEvent("Loading internal docs...")
    # ... reads docs/, calls SDK, streams intermediate findings ...
    yield ResultEvent(html=rendered_report_html)
```

Rules:
- **Workflows may call the Agent SDK.** Unlike dashboards, workflows are where LLM-driven analysis lives.
- **Auto-discovery.** `registry.py` imports every module in `console/workflows/` at startup.
- **Inputs are declarative.** `INPUTS` lists input descriptors. `router.py` renders the form from them. Each run gets a UUID.
- **Uploads.** Input files land in `tools/project-console/data/uploads/{run_id}/`. Uploads are capped at **10 MB** per file. Only files listed in the workflow's `FileInput.accept` are allowed.
- **Markdown-only in v1.** `FileInput.accept` only supports `.md` for now. PDF/DOCX parsing is deferred — users can convert via the `docflow` skill first.
- **Streaming run view.** `run()` is an async generator yielding `ProgressEvent`s and a terminal `ResultEvent`. The run view consumes these over SSE and renders progress live, then swaps in the final HTML result.
- **Run artifacts.** Any files the workflow produces land in `tools/project-console/data/runs/{run_id}/`. These persist across console restarts (not cleaned on startup) so result URLs remain valid within a session.
- **No writes outside `data/`.** Workflows must never modify `docs/`, `project.yml`, `src/`, or anything outside `tools/project-console/data/`.

---

## 7. Hard rules (what the console must and must not do)

These are the rules a reviewer can grep for. Violations should be caught in code review.

### Must
1. Authenticate **only** via Claude Pro/Max OAuth (Claude Code session).
2. Refuse to start if `ANTHROPIC_API_KEY` is set in the environment.
3. Run with one command (`./run.sh` or `uv run python -m console serve`) and zero external services.
4. Work fully offline except for calls to Claude.
5. Vendor all frontend assets under `console/web/static/`. No CDN links.
6. Auto-discover dashboards, domain agents, and workflows — no central registration list to edit.
7. Keep generated artifacts under `tools/project-console/data/` and gitignore that directory.
8. Cap `chat_context()` output at 50 KB (truncate + log warning).
9. Cap workflow uploads at 10 MB per file; reject files outside the declared `accept` list.
10. Contain document path traversal: every virtual path in `/documents/*` must resolve under an allowlisted root; anything else returns 404.
11. Cap document summary input at 80 KB; truncate with a marker if exceeded.

### Must not
1. Import anything from `src/`. The console is unaware of device code.
2. Modify `docs/`, `project.yml`, `src/`, or any file outside `tools/project-console/`.
3. Embed, accept, or fall back to an Anthropic API key — not via env var, not via config, not via flag.
4. Call the LLM from a dashboard's `render()` function. (Sidecars and workflows may; `render()` may not.)
5. Persist chat history server-side.
6. Introduce a build step (no webpack, vite, tsc, babel, etc.).
7. Add a database, queue, cache server, or any background service.
8. Pull frontend assets from a CDN at runtime.
9. Ship with the device or be referenced from any DHF deliverable.

---

## 8. Run model

```bash
cd tools/project-console
./run.sh            # uv sync && uvicorn console.app:app --reload --port 8765
```

- Default port: **8765** (arbitrary, avoids common collisions).
- `--reload` watches `console/` for Python changes; Jinja2 reloads templates per-request.
- Editing a domain agent markdown file takes effect on the next request (no restart).
- Editing a dashboard or workflow Python file triggers a reload.

---

## 9. Deferred optimizations

Things we are deliberately **not** doing yet, but may revisit:

- **Source bundling / caching.** Domain agents re-read source files on every turn. Fine for a demo with small docs. If turns get slow, add a simple mtime-keyed cache in `sources.py`.
- **Embeddings / retrieval.** None. If a domain agent's context exceeds the model window, we'll add naive top-k file selection before reaching for a vector store.
- **Auto-moderator panels.** v1 is round-robin only. An LLM-driven moderator that picks the next speaker based on conversation state is a later addition.
- **Binary file parsing.** Workflows accept markdown only in v1. PDF and DOCX go through the `docflow` skill first.
- **Run cleanup.** Workflow runs in `data/runs/` and `data/uploads/` are not garbage-collected. Add a retention policy later if the directory grows.
- **Auth hardening.** None. Local-only, single user.
- **Tests.** Smoke tests for app startup, dashboard/domain-agent/workflow discovery, and one end-to-end SSE chat roundtrip are sufficient at this stage.

---

## 10. Relationship to the rest of the repo

- `docs/` — read-only input. The console renders views and runs workflows over it.
- `project.yml` — read at startup for project identity, team, registries.
- `src/` — invisible to the console. Strict boundary.
- `.claude/skills/` — the console does not invoke skills directly. If a skill produces an artifact (e.g., `tracker` skill output, `docflow` markdown conversions), the console reads that artifact from `docs/` like any other file.
- `tools/` — the console is one tool among potentially several. Future tools live as siblings under `tools/`, not nested inside `project-console/`.

---

## 11. Changelog

| Date | Change | Rationale |
|---|---|---|
| 2026-04-12 | Initial architecture. | Establishes `tools/project-console/` as the local web UI for dashboards + Claude Pro/Max-backed chat. |
| 2026-04-12 | Expanded to three sections (Dashboards, Agents, Workflows) with a shell nav and landing page; added dashboard chat sidecars (opt-in `CHAT_ENABLED` + `chat_context()`); added panel domain agents (round-robin orchestration); renamed `personas/` → `domain_agents/` with `DomainAgent` type; added workflow model with file uploads, streaming runs, and `data/runs/{run_id}/` artifacts. Set 50 KB cap on dashboard chat context and 10 MB cap on workflow uploads. v1 is markdown-only for uploads; PDF/DOCX deferred to `docflow`. | Captures the full scope agreed in the architecture conversation. |
| 2026-04-12 | Added Documents section as fourth top-level section (Agents · Documents · Dashboards · Workflows). File tree browser over `docs/`, `tasks/`, and pinned `project.yml`; `src/` and `.claude/` explicitly excluded. Format-aware rendering (markdown, HTML, text, PDF, images) with Download fallback for unsupported types. Auto-summary on view for text files via SSE, 80 KB input cap. Path traversal containment rule added. | Gives demo audiences a first-class way to explore the project tree and get instant Claude summaries of DHF artifacts. |
