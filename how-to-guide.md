# How-To Guide — PDLC_DEMO Day-to-Day

You've finished setup — everything is installed. This guide is how to actually use PDLC_DEMO day-to-day: opening the project, staying current, launching Claude Code, navigating the file tree, using skills, and the key files to read first.

> **Companion docs**:
> - `setup.md` — new-contributor machine setup (admin → installs → repo → security posture). Read that first if you skipped here directly.
> - `new-project-bootstrap.md` — for team leads standing up a *brand-new* MedTech project from scratch (different audience).

---

## 🤖 Default to plain English with Claude

You don't need to memorize commands, slash skills, or terminal syntax to use PDLC_DEMO. **The recommended path for all roles** — including non-engineers (regulatory affairs, clinical, QE, human factors) — is to launch Claude Code (§5) and talk to it naturally:

- *"Pull the latest changes from GitHub"* → Claude runs `git pull`
- *"What tasks are we working on right now?"* → Claude reads the task indexes
- *"Open the submission tracker"* → Claude points you at the right file or runs `/tracker`
- *"I want to update the predicate analysis"* → Claude creates or finds a task, activates it, and starts work
- *"This document needs internal review"* → Claude runs the `/change-control` workflow
- *"Run the project health check"* → Claude runs `/best-practices`
- *"What changed since yesterday?"* → Claude runs `/digest`

You'll see slash commands like `/task` and `/change-control` throughout this doc. Those are how the skills work *under the hood*. **You almost never need to type them yourself** — they're shown so you can recognize what Claude is doing.

The few exceptions where you do need to copy a command are flagged as **"manual fallback"** — usually because the underlying tool is interactive (e.g., a `bash` launcher that pops a browser window) or because Claude Code isn't running yet.

---

## 1. Opening the Project

### First time

You already opened the project from the terminal during setup. VS Code remembers this.

### Every time after that

You don't need the terminal anymore — just open VS Code like any other app:

- **Mac**: Press `Cmd+Space`, type **Visual Studio Code**, press Enter. Or click it in your Dock.
- **Windows**: Click the **Start button**, type **Visual Studio Code**, press Enter.

VS Code reopens whatever project you had open last. You should see the project files on the left.

> **Windows users**: Check the **bottom-left corner** of VS Code — you should see **"WSL: Ubuntu"**. This means VS Code is connected to your Linux environment where the tools are installed. If you don't see it, press `Ctrl+Shift+P`, run **"Reopen Folder in WSL"**.

If VS Code opens but doesn't show the project, go to **File → Open Recent** and click the `PDLC_DEMO` entry. On Windows, look for the one that says **[WSL: Ubuntu]** next to it.

---

## 2. Staying Up to Date

The project files are shared through GitHub. When someone on the team makes changes — new documents, updated guides, task updates — those changes get pushed to GitHub. To see them on your computer, you **pull** the latest version.

**Make this a habit**: every time you sit down to work on the project, get the latest updates first.

### The easy way (ask Claude)

Launch Claude Code in your VS Code terminal (§5 below) and ask:

- *"Pull the latest changes from GitHub"*
- *"Get the latest updates"*
- *"Sync the project"*

Claude runs the right commands and tells you what changed.

### The manual way (terminal command)

If you're not in Claude Code, in the VS Code terminal:

```
git pull
```

This downloads the latest changes and updates your local files. If you see a list of changed files, your project is now up to date. If it says `Already up to date.`, you already have everything.

> **When to pull**: at the start of each work session, or any time someone tells you they've pushed updates.

---

## 3. Finding Your Way Around VS Code

VS Code has a few main areas:

### The Sidebar (left side)

The sidebar shows different panels. Switch between them using the icons at the very top:

| Icon | Name | What it does |
|------|------|-------------|
| 📄 (two pages) | **Explorer** | Shows all project files and folders — where you browse |
| 🔍 (magnifying glass) | **Search** | Search for text across all files |
| 🧩 (square blocks) | **Extensions** | Manage add-ons (you installed several during setup) |

**Explorer** is where you'll spend most of your time.

### Opening files

- **Single-click** a file to **preview** it — opens in a tab, but single-clicking another file replaces it. Good for quick browsing.
- **Double-click** to **open** it — gets its own tab, stays open.

> **Tip**: A file in preview mode shows its tab name in *italics*. Double-click the tab to keep it open permanently.

### Viewing Markdown files

Most project files are **Markdown** (`.md`) — plain text with simple formatting (headings, bullets, tables). They look nicer in preview mode:

1. Right-click any `.md` file in the Explorer
2. Select **"Open Preview"** (or **"Markdown Preview Enhanced: Open Preview"** if you see that option)
3. A formatted version appears

You can have the raw text and preview open side by side: open the file normally (double-click), then right-click the tab → **"Open Preview to the Side"**.

---

## 4. Using the Terminal Inside VS Code

The **terminal** is a text-based command line built into VS Code. You'll use it to launch Claude Code and occasionally run shell commands.

### Opening the terminal

- **Keyboard shortcut**: Press `` Ctrl+` `` (backtick — next to the `1` key)
- **Menu**: **Terminal → New Terminal**

A panel appears at the bottom of VS Code. On Mac it's your regular shell; on Windows it's your Ubuntu/WSL environment.

### What the terminal looks like

- **Mac**: `yourname@MacBook PDLC_DEMO %`
- **Windows (WSL)**: `yourname@COMPUTER:~/projects/PDLC_DEMO$`

The blinking cursor after the `%` or `$` is where you type commands.

### Closing and reopening the terminal

- **Hide** the panel (without closing): `` Ctrl+` `` again
- **New terminal**: click **+** in the terminal panel's top-right corner
- **Switch between terminals**: click the dropdown next to **+**

---

## 5. Launching Claude Code

Claude Code is an AI assistant that lives in your terminal. It can read and edit project files, answer questions about the project, and help you draft documents.

### Step by step

1. **Open the terminal** in VS Code (§4 above)
2. Type:

```
claude
```

3. Press **Enter**

### First time — login prompts

The first launch will ask you to log in:

- A browser opens (or a URL prints) to authenticate with your Claude account
- Sign in with the account you created during setup
- Come back to VS Code — the terminal will show you're logged in
- **One-time** setup — Claude Code remembers you after.

### What you'll see

The terminal changes from a shell prompt to Claude Code's interface — a welcome message and a text input area.

**This is now a conversation with Claude** — not a regular terminal. Type questions or requests in plain English; Claude responds.

### Talking to Claude Code

Just type naturally:

- `What is this project about?`
- `Show me the active tasks`
- `Help me understand the folder structure`
- `What's in the PCA device DHF?`

Claude reads project files and responds with context-aware answers.

### Exiting Claude Code

- Type `/exit` and press Enter
- Or press `Ctrl+C`

You'll see your normal command prompt again.

> **Important**: While Claude Code is running, the terminal is in conversation mode — it's not a regular command line. If you need to run a shell command (like `git status`), either exit Claude Code first, or open a **second terminal** (the **+** icon).

---

## 6. Project Structure — Quick Reference

You don't need to memorize this. You can always ask Claude *"Where does this go?"* or *"What's in the docs folder?"*. Here's a quick map:

| Folder / file | What's in it |
|---|---|
| `docs/external/` | Reference material — FDA guidance, ISO/IEC standards, industry frameworks |
| `docs/internal/` | Corporate procedures we own — SOPs, work instructions, templates (source → markdown) |
| `docs/project/` | What we're building — input analysis, strategies, per-DHF design controls, submissions |
| `tasks/` | Per-person task documents (`tasks/<person>/NNN-*.md`) + the lessons ledger |
| `tools/project-console/` | Local FastAPI console (agents, documents, dashboards) — start with `./tools/project-console/start.sh` |
| `tools/file-locator-mcp/` | Local semantic-search MCP backing `file-locator` |
| `.claude/` | Skills, agents, hooks, settings (shared via git, applies to every session) |
| `CLAUDE.md` | Project operating rules — Claude reads this at the start of every session |
| `project.yml` | Single source of truth — project identity, DHFs, team roster, security allowlists |
| `glossary.md` | Project-wide term definitions (PCA, PCCP, SaMD, SiMD, 510(k), DHF, …) |
| `setup.md` / `setup.sh` | New-contributor onboarding (you just finished) |
| `how-to-guide.md` | This document |
| `new-project-bootstrap.md` | How to start a brand-new MedTech project from scratch |
| `project-overview.md` | One-page project overview anchor doc |

---

## 7. Things to Try Right Now

A few things to confirm everything works and to get comfortable.

### Preview a document

1. In the VS Code Explorer, open `docs/project/strategies/`
2. Double-click `regulatory-strategy.md`
3. Right-click the file tab → **"Open Preview to the Side"**
4. You see the formatted version alongside the raw text

### Launch Claude Code and ask a question

1. Open the VS Code terminal (`` Ctrl+` ``)
2. Type `claude` and press Enter
3. Type: `What are the active tasks in this project?`
4. Claude reads the task indexes and lists what's in progress
5. Type `/exit` to return to the terminal

### Check the task list

1. In Explorer, go to `tasks/` → your folder (e.g., `tasks/ben/`)
2. Open `000-index.md` — your personal task dashboard
3. Preview it to see the formatted tables

---

## 8. Next Step: Claude Desktop

Once you're comfortable with Claude Code, explore **Claude Desktop** — the standalone app you installed during setup. Visual chat interface that some people find easier than the terminal.

### Why try Claude Desktop?

- **Visual interface** — feels like a messaging app rather than a terminal
- **Integrations** — Gmail, Calendar, GitHub built in
- **Project access (Mac only)** — if you create a project, Claude Desktop can read/edit project files like Claude Code

### Opening Claude Desktop

- **Mac**: `Cmd+Space`, type **Claude**, press Enter
- **Windows**: Start button, type **Claude**, press Enter

### Starting a project conversation (Mac)

1. Open Claude Desktop → **Projects** in the left sidebar
2. **Create Project** (or **+**)
3. Name: **PDLC_DEMO**
4. **Add folder** / **Connect folder** → navigate to `~/projects/PDLC_DEMO/`
   - If the picker opens elsewhere, use `Cmd+Shift+G` → type `~/projects/PDLC_DEMO` → Enter
5. Select the `PDLC_DEMO` folder (not a file inside it)
6. When prompted, select the **Cowork** mode — lets Claude read and edit project files

Once created, **start new conversations from within the project** (not from the main chat) and make sure **Cowork** is selected.

### Windows users

Claude Desktop's Cowork mode **does not work with WSL-hosted files**. Use **Claude Code in VS Code** (§5) for all project file work on Windows.

You can still use Claude Desktop on Windows for:
- General conversations with Claude
- Integrations (Gmail, Calendar, GitHub)
- Anything that doesn't require reading/editing project files

### Using integrations

Your integrations were set up during installation. Claude Desktop uses them automatically when relevant:

- *"What meetings do I have tomorrow?"* — Google Calendar
- *"Summarize my unread emails"* — Gmail
- *"What are the open issues on our repo?"* — GitHub

---

## 9. Key Files to Read

Before diving deeper, open and read these. They give a solid understanding of the project, its terminology, and current status.

### Submission tracker — `docs/project/submissions/submission-tracker.html`

The best place to start — visual dashboard showing every deliverable in the submission package, organized by part (510(k), PCCP, supporting documents). Each item shows status, owner, and readiness.

**How to view it**: In Explorer, navigate to `docs/project/submissions/`. Right-click `submission-tracker.html` → **"Preview in Default Browser"** (Open Browser Preview extension). Opens the full interactive dashboard with collapsible sections.

> **Use your browser, not VS Code preview.** The dashboard has expandable sections and interactive features that don't work in VS Code's built-in HTML viewer.

> The HTML is generated from `submission-tracker.md`. Markdown is the source of truth; Claude updates it and the `/tracker` skill regenerates the HTML. Don't edit the HTML directly.

### Project operating rules — `CLAUDE.md`

The most important file in the repository. Describes:
- Project scope (PDLC_DEMO is a demo project anchored on the PainEase PCA Advanced PP3500)
- Three-tier docs hierarchy and information flow
- Working conventions (one task = one file, capture strategy/lessons inline, etc.)
- Task-first workflow and the task gate
- Auto-loaded rules under `.claude/rules/`

**How to open**: double-click `CLAUDE.md` in the project root. Right-click the tab → **"Open Preview to the Side"** for a formatted view.

> You don't need to memorize it — Claude reads it at the start of every session. But skimming once gives you context.

### Terminology — `glossary.md`

Lots of regulatory and medical-device terminology — PCCP, SaMD, SiMD, 510(k), DHF, PCA, etc. The glossary defines them in plain language.

### Project overview — `project-overview.md`

Single-page anchor doc explaining what PDLC_DEMO is, what the PainEase PP3500 device is, and how the agentic workflows are structured. Includes a "Where things live" table that points to every other key artifact.

### Per-DHF design controls

Three DHFs live under `docs/project/dhfs/`:

| DHF | What it is |
|---|---|
| `pca-device/` | Primary — PainEase PP3500 pump firmware + on-device UI (SaMD + SiMD combination) |
| `connectivity-adapter/` | BLE / Wi-Fi gateway between the pump and the cloud |
| `cloud-suite/` | Cloud services (ingest, clinician portal, drug-library manager) |

Inside each DHF you'll find `design-controls/` (user needs, design inputs, architecture, V&V), `risk-management/`, `cybersecurity/`, and `postmarket/`.

### Your task index — `tasks/<yourname>/000-index.md`

Your personal task dashboard. Active and completed tasks. If you don't have a folder under `tasks/` yet, ask the team lead.

---

## 10. Navigating the Project

PDLC_DEMO has a lot of folders. Here's the tour.

### The three tiers

All documentation lives under `docs/` and is organized into three tiers:

| Tier | Folder | What's in it |
|------|--------|-------------|
| **External** | `docs/external/` | Reference material we consume but don't author — FDA guidance, ISO/IEC standards, industry frameworks, clinical literature |
| **Internal** | `docs/internal/` | Corporate procedures we own — SOPs, work instructions, templates (sourced from the company quality management system) |
| **Project** | `docs/project/` | What we're building — the actual deliverables, design controls, submissions, and input analysis |

You'll spend most of your time in `docs/project/`. The other two tiers are reference material.

### External documents (`docs/external/`)

FDA guidance, ISO/IEC standards, industry frameworks — **distilled summaries**, not raw copies. We can't include full copyrighted standards or 200-page FDA guidance PDFs in the repo. Instead, Claude reads the originals and produces focused summaries extracting requirements, decision criteria, and key sections relevant to our project.

- **`docs/external/fda-guidance/`** — distilled summaries of FDA guidance documents
- **`docs/external/standards/`** — distilled summaries of ISO/IEC standards (IEC 62304, ISO 14971, IEC 62366, IEC 60601-x, etc.)
- **`docs/external/industry-frameworks/`** — IMDRF, AAMI, GMLP frameworks
- **`docs/external/clinical-literature/`** — published studies and clinical evidence

### Internal documents (`docs/internal/`)

Corporate SOPs, work instructions, forms, and templates start as Word files (`.docx`) or PDFs from the QMS. They go through a conversion so Claude can work with them:

```
source/              →    source-md/
Original files            Markdown conversions
(.docx, .pdf)             (faithful, full-content)
```

- **`docs/internal/source/`** — original files exactly as received. Don't edit them.
- **`docs/internal/source-md/`** — markdown conversions, created via the `/docflow` skill. Faithful — same content, different format.

> `docs/internal/source/INDEX.md` lists every internal document by category.

### The `formal/` folders

Deliverables (submission documents, design control records) exist in two forms:

- **Working markdown** — file at the folder root (e.g., `docs/project/submissions/qsub/cover-letter.md`). Where Claude writes and edits. Easy to review and diff.
- **Formal document** — exported Word/PDF in the `formal/` subfolder (e.g., `…/formal/cover-letter.docx`). Submission-ready version with proper formatting, headers, page numbers.

`/docflow export` converts working markdown into formal documents. Claude handles it when a document is ready for formal review.

> **Rule of thumb**: edit the markdown, not the formal document. The formal version is generated output.

### Quick folder map

| Looking for… | Go to… |
|---|---|
| Submission tracker (project status) | `docs/project/submissions/submission-tracker.html` |
| Q-Sub package (pre-submission to FDA) | `docs/project/submissions/qsub/` |
| PCCP document | `docs/project/submissions/pccp/` |
| 510(k) submission package | `docs/project/submissions/510k/` |
| PCA device DHF (primary) | `docs/project/dhfs/pca-device/` |
| Connectivity Adapter DHF | `docs/project/dhfs/connectivity-adapter/` |
| Cloud Suite DHF | `docs/project/dhfs/cloud-suite/` |
| System architecture | inside each DHF: `design-controls/architecture/` |
| Risk management | inside each DHF: `risk-management/` |
| Predicate device research | `docs/project/input-analysis/predicate-analysis/` |
| FDA guidance summaries | `docs/external/fda-guidance/` |
| Corporate SOPs | `docs/internal/source-md/` |
| Your tasks | `tasks/<yourname>/000-index.md` |

### Viewing different file types in VS Code

| File type | How to view |
|---|---|
| `.md` (Markdown) | Double-click. For formatted view: right-click the tab → **"Open Preview to the Side"** |
| `.html` (Dashboards) | Right-click in Explorer → **"Preview in Default Browser"**. Don't use VS Code's built-in viewer — interactive features won't work. |
| `.docx` (Word) | Double-click — opens with the Document Viewer extension |
| `.pdf` | Double-click — opens with the vscode-pdf extension |
| `.xlsx` (Excel) | Double-click — opens with the Document Viewer extension |

### Strategy documents

PDLC_DEMO uses **shared cross-component strategy documents** — one file per domain under `docs/project/strategies/`. Per-component nuance is captured as callout subsections inside each strategy doc.

| Strategy | File |
|---|---|
| **Regulatory** | `docs/project/strategies/regulatory-strategy.md` |
| **Architecture** | `docs/project/strategies/architecture-strategy.md` |
| **Commercial** | `docs/project/strategies/commercial-strategy.md` |
| **Development** | `docs/project/strategies/development-strategy.md` |
| **Testing** | `docs/project/strategies/testing-strategy.md` |
| **Risk** | `docs/project/strategies/risk-strategy.md` |
| **Post-Market** | `docs/project/strategies/postmarket-strategy.md` |
| **Operations** | `docs/project/strategies/operations-strategy.md` |

**Start with `regulatory-strategy.md`** — it covers the filing pathway, module classification, predicate strategy, PCCP scope, and Q-Sub approach. After reading, ask Claude follow-ups to deepen understanding:

- *"Does the PCCP add additional regulatory burdens compared to a standard 510(k)?"*
- *"Why did we choose a single 510(k) submission instead of filing each module separately?"*
- *"What if a competitor gets clearance before us — does that help or hurt our predicate strategy?"*

Claude has access to all strategies, FDA guidance summaries, and full project context — so answers are detailed and project-specific, not generic.

> Decisions made during task work get harvested into these strategy docs by the `/strategy` skill (it reads `<!-- STRATEGY CONTENT: ... -->` blocks from task docs).

---

## 11. Advanced: Skills

Once comfortable with Claude Code, you can use **skills** — custom commands built into the project that teach Claude how to do specific tasks the way our team does them.

### What are skills?

Skills are project-specific. They live in `.claude/skills/`. When you use a skill, Claude reads its instructions and follows a defined process — output is consistent across the team, not dependent on how you phrase your request.

### How to use a skill

In Claude Code, type a **slash command** + skill name:

```
/task list
```

That's it.

### Available skills

| Skill | Command | What it does |
|---|---|---|
| **Task Management** | `/task` | Create, find, list, update, and show tasks. How all work is tracked. |
| **Checkpoint** | `/checkpoint` | Refresh the active task doc to a resume-ready state before `/clear`, session end, or hand-off |
| **MedTech Docs** | `/medtech-docs` | Manage the `docs/` structure, file naming, README conventions, generate compliance dashboard |
| **Strategy** | `/strategy` | Scan task docs for strategy decisions and assemble them into unified strategy documents |
| **Lessons** | `/lessons` | Capture and promote lessons learned from task work to their permanent home |
| **Tracker** | `/tracker` | Build/update the submission tracker, render the HTML dashboard, assess readiness |
| **Trace Matrix** | `/trace-matrix` | Build per-DHF trace matrices (user needs → requirements → architecture → V&V → risk) |
| **DHF Manifest** | `/dhf-manifest` | Check whether each DHF has the documents regulation + QMS require, with gap reports |
| **Jira Pull** | `/jira-pull` | Mirror Jira issues locally and detect drift between Jira and the trace matrix (pull-only) |
| **Best Practices** | `/best-practices` | Audit project setup against the shared skill registry |
| **Gap Analysis** | `/gap-analysis` | Critique the *content* of artifacts against standards (e.g., "is the hazard register per ISO 14971?") |
| **Reference Audit** | `/reference-audit` | Verify references and citations in a document — broken links, stale standards clauses, mismatched anchors |
| **Docflow** | `/docflow` | Convert documents between markdown and formal formats (DOCX, PDF, XLSX) |
| **Docx / Pptx / Xlsx / Pdf** | `/docx` `/pptx` `/xlsx` `/pdf` | Create, read, edit the matching file type |
| **Frontend Slides / md-deck** | `/frontend-slides` `/md-deck` | Build polished HTML slide decks from markdown |
| **File Locator** | `/file-locator` | Semantic file search ("where do we argue MDDS classification?"). Also a background MCP Claude uses automatically. |
| **Change Control** | `/change-control` | Round-trip docs to/from Google Docs (internal review), Confluence (formal review), Windchill, Jira |
| **Knowledge Pack Export** | `/knowledge-pack-export` | Package curated project docs into a shareable knowledge pack for an external assistant (Gemini Gem, custom GPT, NotebookLM) |
| **Web Control** | `/web-control` | Browser-automation infrastructure used by change-control's internal-review tier |
| **Project Console** | `/project-console` | Scaffold and run the local FastAPI project console |
| **Digest** | `/digest` | Daily project briefing and CHANGELOG updates — "what changed since yesterday" |
| **Sync Skills** | `/sync-skills` | Sync this project's skills + agents with the shared registry (Hitachi) — bidirectional |
| **SecOps** | `/secops` | Security posture — session hooks, permissions allow-list, attestations |
| **Skill Creator** | `/skill-creator` | Create, modify, audit, and measure skills (meta-skill) |

### You don't need to memorize commands

The slash commands are how skills work under the hood, but **you don't need to use them directly**. Just talk to Claude naturally and it will figure out the right skill. Examples:

**Everyday workflow**
- *"Let's start a new task on updating the risk analysis for the PCA device"* — Claude uses `/task`
- *"What tasks are we working on right now?"* — pulls up the active task list
- *"Show me the submission tracker"* — uses `/tracker`
- *"Assemble the regulatory strategy from our task docs"* — uses `/strategy`
- *"I'm about to stop for the day — save where we are so I can pick up later"* — uses `/checkpoint`
- *"What changed on the project since yesterday?"* — uses `/digest`

**Documents & conversion**
- *"Convert this markdown to a Word document"* — uses `/docflow`
- *"Can you create a Word document from the predicate analysis?"* — uses `/docx`
- *"I need a PowerPoint summarizing our regulatory strategy"* — uses `/pptx`
- *"Put this data into a spreadsheet"* / *"Merge these PDFs into one"* — uses `/xlsx` / `/pdf`

**Analysis & quality**
- *"Run a project health check"* — `/best-practices`
- *"Is our hazard register actually compliant with ISO 14971?"* — `/gap-analysis`
- *"Check the references in the regulatory strategy doc for broken links"* — `/reference-audit`
- *"What documents are still missing from the connectivity adapter DHF?"* — `/dhf-manifest`
- *"Build the traceability matrix"* / *"Does our trace matrix match Jira?"* — `/trace-matrix` / `/jira-pull`

**Finding things & sharing**
- *"Where do we argue MDDS classification?"* — `/file-locator`
- *"I need this draft reviewed internally before it goes to the customer"* — `/change-control`
- *"Package our strategy docs into a shareable assistant for the external team"* — `/knowledge-pack-export`

The slash commands are there if you want a shortcut, but plain English works just as well.

---

## 12. Task-First Workflow

All non-trivial work in PDLC_DEMO starts with an **active task**. The `/task` skill manages task documents under `tasks/<person>/NNN-<name>.md`. A `PreToolUse` hook denies file edits when no task is active for the current session.

This isn't bureaucracy — it's the recovery point if your session drops or gets compacted. Every change has somewhere the team can find it.

### Starting work

1. In Claude Code, just say what you're doing: *"Let's start updating the predicate analysis"*
2. Claude runs `/task find` to look for a matching active task; if no clear match, it creates a new one and activates it
3. Claude proceeds with the work, updating the task doc as it goes

### If a file edit is denied

The denial message tells you the exact recovery command — the active task hook prints it. Just say "go ahead" and Claude will activate a task and retry. Never bypass the gate.

### Strategy and Lessons Learned

When a non-obvious decision or insight surfaces during task work, Claude adds a tagged block to the active task **in the same turn**:

```markdown
<!-- STRATEGY CONTENT: regulatory, predicate -->
We're picking K190567 as the predicate because...
<!-- /STRATEGY CONTENT -->
```

```markdown
<!-- LESSONS LEARNED: testing -->
The trace-matrix init action prescribes a project adapter — don't hand-edit the yml.
<!-- /LESSONS LEARNED -->
```

The `/strategy` and `/lessons` skills harvest these blocks later — they only surface what was written.

---

## 13. Optional: Internal Review via Google Docs (`change-control`)

Before a doc goes to **formal customer review** (Confluence with Part 11 sign-off), you'll typically want **internal review** by your own team. The `change-control` skill automates the round-trip between your local markdown/docx and a Google Doc reviewers comment on.

This requires the `web-control` browser-automation infrastructure (set up via `setup.sh` if `web-control` is present).

> **✨ Just ask Claude**: *"I need internal review on this doc"* / *"Start an internal review of <path>"*. Claude launches the debug Chrome browser for you if it isn't already running, creates the Google Doc, pastes your content, and adds a tracking section to your active task doc. You only need to sign into Google in the browser window that pops up (once, on first use).

### Pre-flight: `web-control` must be running

**Manual fallback** (only if you'd rather start the browser yourself before talking to Claude):

```
bash .claude/skills/web-control/scripts/launch-debug-chrome.sh
```

A small (~800×700) Chrome window appears. Sign in once with your corporate Google account on first use; session persists across launches.

### The end-to-end flow

```
You write draft locally
        │
        ▼
You: "I need internal review on this doc"
        │
        ▼   /change-control review-start <path>
        │   ├─ Creates a gdoc in Drive
        │   ├─ Pastes content (markdown auto-format)
        │   └─ Adds "## Internal Review — <doc>" section to your task doc
        ▼
[Reviewers comment / suggest / edit in the gdoc]
        │
        ▼ (next day)
You: "Anything I need to address?"
        │
        ▼   /change-control review-status <path>
        │   └─ Refreshes the task-doc section with current open items
        ▼
You + Claude work through each item in chat
        │
        ▼
You: "Update internal review"
        │
        ▼   /change-control review-update <path>
        │   ├─ Posts replies to addressed comments + resolves them
        │   └─ Wholesale-pushes new md to the gdoc body
        ▼
[Loop until "no new feedback since last sync"]
```

### Get help inline

> **✨ Just ask Claude**: *"How does the change-control internal review workflow work?"* / *"What can /change-control do?"* Claude reads the skill manual and explains it in plain language.

**Manual fallback** (if you want the raw help output):

```
python3 .claude/skills/change-control/actions/help.py
python3 .claude/skills/change-control/actions/help.py review-start
```

---

## 14. WSL ↔ Windows Networking

> **Mac users**: skip this section.

If you're on Windows + WSL, here's what you need to know about reaching Linux-hosted services (like `project-console`) from a Windows browser.

> **✨ Just ask Claude if anything below breaks**: *"I can't reach the project console from my Windows browser — can you diagnose?"* Claude walks the troubleshooting matrix below, checks your WSL config, and fixes what it can without you copying any commands.

### The default just works

Modern WSL2 auto-forwards Windows-side `localhost` to the WSL VM. When a Linux service binds to `0.0.0.0:8000` or `127.0.0.1:8000` on a recent WSL build, you can open `http://localhost:8000` in Edge / Chrome / Firefox on Windows and it just works. No `wsl.conf` edits, no port-proxy commands, no firewall rules.

Verify with `cat /etc/wsl.conf` — if no `[network]` block, you're on the default (NAT + auto-forward).

### Troubleshooting matrix — when the default breaks

| Symptom | Likely cause | Fix |
|---|---|---|
| Service is up in WSL (`curl localhost:<port>` works inside Ubuntu) but Windows browser shows "can't be reached" | Service is bound to `127.0.0.1` only on a WSL build that doesn't loopback-forward 127.0.0.1 | Bind the service to `0.0.0.0` instead. For project-console: `/project-console run --host 0.0.0.0` |
| Worked yesterday, doesn't work today, no config changes | WSL VM lost its forwarding state (sleep / hibernation edge case) | In Windows PowerShell: `wsl --shutdown`, then reopen Ubuntu |
| `cat /etc/wsl.conf` shows `[network]` with `networkingMode=mirrored` | Mirrored mode is enabled and may not have forwarded this port | Either revert to default by removing the `[network]` block + `wsl --shutdown`, or keep mirrored mode and bind to `0.0.0.0` |
| `%UserProfile%\.wslconfig` shows `localhostForwarding=false` | Someone explicitly disabled the auto-forward | Set `localhostForwarding=true` (or remove the line) and `wsl --shutdown` |
| Corporate laptop, nothing about config looks wrong | Hyper-V / Defender / corporate firewall blocking the WSL virtual adapter | IT-territory. Workaround: `wsl hostname -I` to get the WSL VM IP, then `http://<that-ip>:<port>` from Windows |

This is about **inbound from Windows → Linux services**. The `web-control` / `change-control` workflow runs entirely Linux-side, so no Windows-to-WSL networking is involved — the only Windows touchpoint is the WSLg display surface.

---

## 15. Getting Help

- **Ask Claude Code** (in VS Code) — your primary tool. Knows the project structure, conventions, and regulatory context. Start here for project work.
- **Ask Claude Desktop** — great for email, calendar, GitHub integrations. On Mac, also useful for project file work if you set up a Cowork project.
- **Ask a team member** — if stuck on something Claude can't help with, reach out.
- **Check `setup.md`** — if a tool stops working or you need to reinstall something, the setup guide has the steps.
- **Check `new-project-bootstrap.md`** — if you're thinking about how to apply this stack to a *different* device program from scratch.

---

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-05-30 | Ben Xavier | Follow-up to the initial rewrite — added a top-banner "🤖 Default to plain English with Claude" section reinforcing that slash commands are shown so readers can recognize what Claude is doing, not for them to memorize. Added inline "✨ Just ask Claude" callouts at §13 (change-control pre-flight + inline help) and §14 (WSL networking troubleshooting). Same non-engineer-first pattern as the setup.md follow-up (see [[feedback_setup_docs_ask_claude_callouts]]). |
| 2026-05-30 | Ben Xavier | Rewrote how-to-guide.md as a day-to-day usage guide modeled on the arthrex-pccp sister project's `getting-started.md` (task ben/069). New audience: post-setup contributor learning to use the project. 15-section structure: opening the project → `git pull` habit → VS Code basics → terminal → launching Claude Code → project structure → things to try → Claude Desktop → key files to read → navigation tour → skills overview → task-first workflow → optional change-control internal review → WSL networking → getting help. Replaces prior content (new-MedTech-project bootstrap) which moved to `new-project-bootstrap.md`. |
