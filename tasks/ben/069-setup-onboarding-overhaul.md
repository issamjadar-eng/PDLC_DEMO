# 069 — Setup Onboarding Overhaul (Arthrex Three-File Model)

**ID**: 069
**Created**: 2026-05-30
**Status**: Complete
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
2. **Phase-end batching is OK; drift-batching is not.** Planned phases (e.g., "finish Phase 2, then log the whole phase at once") are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask. By then a crash or context-trim has lost the state. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

Overhaul PDLC-DEMO's contributor onboarding to match the **arthrex-pccp three-file model**, because the current `setup.md` (101 lines, security-posture only) doesn't actually onboard anyone — it assumes the contributor has already installed Claude Code, cloned the repo, and configured everything. The arthrex sister project at `/home/benxavier/project/arthrex-pccp/` has a mature pattern that this project should mirror.

**Target structure:**

| File | Audience | Purpose |
|------|----------|---------|
| `setup.md` | New contributor joining the repo | Walks from zero (admin privs, terminal, WSL) through accounts, installs, repo clone, security posture |
| `setup.sh` | Same — automated path | Idempotent installer with `--check` mode (mac/wsl/linux); ports arthrex's script and adapts to PDLC-DEMO |
| `how-to-guide.md` | Onboarded contributor — day-to-day use | Replaces the current "bootstrap a new MedTech project from scratch" content with "use this repo day-to-day" (open VS Code, `git pull`, launch Claude Code, project tour, skills) |
| `docs/new-project-bootstrap.md` | Team lead starting a new device program | Current `how-to-guide.md` content (Phase 0–10) moved here, preserved verbatim — this is genuinely useful content that just isn't contributor onboarding |

**Three pinned design decisions (user-confirmed 2026-05-30):**
1. Mirror arthrex three-file model.
2. Fold security-posture content (training opt-out, GitHub 2FA, Claude 2FA, `/secops attest`) into the new `setup.md` as a section — it IS contributor onboarding.
3. Port arthrex `setup.sh` as the base; adapt to PDLC-DEMO (drop arthrex-specific atlassian MCP onboarding if PDLC-DEMO doesn't ship change-control formal tier; adjust project name strings, repo, VS Code extension list, skill-specific setup functions).

## Todos

- [x] Read both projects' setup docs end-to-end
- [x] Confirm scope with user (three answers locked in)
- [x] Create this task doc
- [x] **Phase 1** — Renamed `how-to-guide.md` → `new-project-bootstrap.md` at project root (not under `docs/` — honored the existing "Doc home" resolution that says peer entry-point guides belong at root, not in docs/ which is the *output* of the medtech process). Used `git mv` for rename tracking. Updated top banner + "Resolved decisions" section + changelog. Updated cross-references in `README.md` (file tree) and `project-overview.md` (file tree + "Where things live" table).
- [x] **Phase 2** — Wrote `setup.sh` (1385 lines, executable, syntax-valid) ported from `/home/benxavier/project/arthrex-pccp/setup.sh`. Adaptations: project name strings → `PDLC_DEMO`; repo → `GlobalLogic-a-Hitachi-Company/PDLC_DEMO`; dropped `setup_atlassian_mcp` function and its call in `main` (confirmed via `project.yml` `approved_mcps` that PDLC-DEMO does not use the atlassian MCP); rewrote the print_summary "Next steps" block to point at `/secops check` and `how-to-guide.md` instead of arthrex's step-15 Cowork project reference. Kept: OS detect (mac/wsl/linux), admin check, Homebrew, install_brew_packages (node/git/gh/jq + pandoc/poppler/qpdf/LibreOffice with headless smoke test + python3/uv), install_python_packages (10 pip packages incl. pypdf/pdf2image/pdfplumber/reportlab/pandas/openpyxl/python-docx/lxml/defusedxml/Pillow), setup_web_control (gated on `.claude/skills/web-control/` presence), setup_file_locator (gated on `tools/file-locator-mcp/` presence), configure_git, setup_ssh_key (with GitHub upload via `gh ssh-key add` when authenticated), install_claude_cli, install_vscode_extensions (5 extensions + WSL on Windows), audit_team_access (--check, cross-references `project.yml` `team.active[].github` vs `gh api repos/$repo/collaborators`).
- [x] **Phase 3** — Rewrote `setup.md` as 18-section full new-contributor onboarding guide (771 lines, modeled on arthrex `setup.md`). Sections: admin privileges → terminal → VS Code → WSL (windows) → GitHub account → Claude account → Google Drive → Claude Desktop → Choose Your Path (automated / manual) → Homebrew (manual) → Node + core utils → document processing tools → Git + SSH → VS Code extensions → Claude Code CLI → repo clone → §15 **Security Posture** (15a training opt-out / 15b GitHub 2FA / 15c Claude 2FA / 15d conversation hygiene / 15e integration awareness / 15f team registration) → §16 web-control optional → §17 file-locator optional → §18 confirmation `/secops check` + `/best-practices`. Folded prior security-posture content (training opt-out, 2FA, conversation hygiene, integration awareness) into §15 rather than keeping it as a separate doc.
- [x] **Phase 4** — Rewrote `how-to-guide.md` as 15-section day-to-day usage guide (645 lines, modeled on arthrex `getting-started.md`). Sections: opening the project → `git pull` habit → VS Code basics → terminal in VS Code → launching Claude Code → project structure quick reference → things to try → Claude Desktop (incl. Mac Cowork project setup) → key files to read (submission-tracker.html + CLAUDE.md + glossary.md + project-overview.md + the three DHFs) → navigating the project (three-tier convention + folder map + viewing different file types + 8 strategy domains) → advanced skills (full skill table grouped by use) → task-first workflow → optional change-control internal review → WSL ↔ Windows networking troubleshooting matrix → getting help. Adapted from arthrex specifics: replaced `arthrex-pccp` → `PDLC_DEMO`; replaced "Arthrex hip surgery digital tools" framing → PainEase PCA Advanced PP3500 framing; updated DHF list to `pca-device` / `connectivity-adapter` / `cloud-suite`; updated submission tracker path; updated key files list to match what's actually committed.
- [x] **Phase 5** — Wire-up audit: cross-references in `CLAUDE.md` (one mention of `setup.sh --check` — previously aspirational, now real ✓), `README.md` (file tree updated), `project-overview.md` (file tree + "Where things live" table updated). Found nothing in `tasks/README.md` referencing the renamed file. Sync log + skill docs unchanged (correct — they're upstream content).
- [x] **Phase 6** — Verified: `bash setup.sh --check` runs end-to-end on the live WSL machine without errors. OS detected (wsl), admin check passed, Homebrew/Node/Git/gh/jq detected as installed, doc tools mostly present (qpdf missing — true finding), web-control fully set up, file-locator venv ready, Git configured, SSH key absent (true finding), Claude CLI installed, VS Code extensions mostly installed (Document Viewer + Open Browser Preview + WSL extension not — true findings). Script behavior verified; pending: `/best-practices` re-audit confirmation; commit + push per user instruction.

## Strategy Content

<!-- STRATEGY CONTENT: development, operations -->
**Pinned design decision (2026-05-30):** PDLC-DEMO adopts the arthrex three-file onboarding model (`setup.md` + `setup.sh` + `how-to-guide.md`), with current `how-to-guide.md` content relocated to `docs/new-project-bootstrap.md`. Security-posture content (training opt-out, 2FA, `/secops attest`) folds into the new `setup.md` rather than a separate `SECURITY.md`. Rationale: the audience for security-posture confirmation IS the new contributor, so co-locating it in their primary onboarding doc reduces the doc surface they have to discover. Separating it would optimize for the maintenance case (re-attesting every 30 days) at the cost of the onboarding case (one-time read-through).

**Why arthrex's model:** the sister project's `setup.md` + `setup.sh` + `getting-started.md` shape is battle-tested with non-engineer contributors (regulatory affairs, clinical, QE roles). The structure walks zero-state users through admin → terminal → accounts → installs → first project open without assuming prior knowledge. PDLC-DEMO's current `setup.md` assumed too much; that's the gap.
<!-- /STRATEGY CONTENT -->

<!-- STRATEGY CONTENT: development, operations -->
**Non-engineer-first writing convention for setup/onboarding docs (2026-05-30):** when authoring contributor-facing documentation for a project where Claude Code is part of the standard tooling, every step that Claude can drive should explicitly say so via an "✨ Or just ask Claude" callout with a concrete example prompt. The manual commands stay in the doc (engineers want to see them; auditors need them; recovery from "Claude is unavailable" needs them) — but the *primary* path surfaced to the reader is the natural-language one. Reason: many MedTech contributors (regulatory affairs, clinical evaluators, QE, human factors) have non-engineering backgrounds. A doc that defaults to "copy these commands" assumes a competence they shouldn't need to acquire to do regulated documentation work. Apply this rule everywhere a non-engineer onboards: `setup.md`, `how-to-guide.md`, `new-project-bootstrap.md`, any future role-specific onboarding doc.
<!-- /STRATEGY CONTENT -->

<!-- LESSONS LEARNED: writing -->
**Lesson — "ask Claude" callouts must be standard in setup/onboarding docs.** Initial setup.md rewrite (Phase 3 this task) followed arthrex's structure but missed the natural-language layer non-engineers need. User feedback: *"setup.md has a lot of manual steps, it should include 'ask Claude' instructions where Claude does the heavy lifting. Some users are not engineers."* The fix is a top banner explaining the pattern + inline callouts at every Claude-drivable step + a third "Claude-assisted" path in the path-selection table. Engineers don't lose anything (manual commands remain); non-engineers gain a primary path that doesn't require terminal fluency. Future setup-doc reviews should grep for sections that show commands without an "✨ Or just ask Claude" alternative — if Claude can do the step, the callout is mandatory.
<!-- /LESSONS LEARNED -->

## Resume

### In-flight artifacts (uncommitted)
- `setup.md` — rewritten (771 lines)
- `setup.sh` — new file, executable, syntax-valid (1385 lines)
- `how-to-guide.md` — rewritten (645 lines, replacing the file that was `git mv`-d to `new-project-bootstrap.md`)
- `new-project-bootstrap.md` — renamed from old `how-to-guide.md` with banner + Resolved-decisions + changelog updates (283 lines)
- `README.md` — file tree updated
- `project-overview.md` — file tree + "Where things live" table updated
- `tasks/ben/000-index.md` — task 069 added to Active table
- `tasks/ben/069-setup-onboarding-overhaul.md` — this doc

**Nothing has been committed by Claude.** User controls commits.

### First action on resume
1. If picking up to verify: `bash setup.sh --check` (smoke-tested clean on WSL this session).
2. If picking up to commit + push: PR-then-auto-merge per `.claude/rules/git-workflow.md`. Suggested commit/PR title: `ben/069: arthrex three-file onboarding model (setup.md + setup.sh + how-to-guide.md + new-project-bootstrap.md)`.
3. Activation command if resuming in a fresh session:
   ```bash
   bash .claude/hooks/task-activate.sh add <SESSION_UUID> 069
   ```

## Open Questions

### Resolved this session
- ~~Does PDLC-DEMO ship the `change-control` formal Confluence tier?~~ **Resolved**: change-control skill IS installed but `project.yml` `approved_mcps` does NOT list `atlassian` — so the formal Confluence tier is not active. Dropped `setup_atlassian_mcp` from the port.
- ~~Does PDLC-DEMO have a `web-control` skill installed?~~ **Resolved**: yes — `.claude/skills/web-control/` present. `setup_web_control` kept in `setup.sh`.
- ~~Does PDLC-DEMO have a `file-locator` tool at `tools/file-locator-mcp/`?~~ **Resolved**: yes. `setup_file_locator` kept in `setup.sh`.
- ~~Does the team use Google Drive Desktop + Claude Desktop the way arthrex does?~~ **Resolved**: kept both as optional sections in `setup.md` — they're broadly useful corporate tooling whether or not specific skills depend on them.

## Changelog

- 2026-05-30: Task created. Read all five source files (PDLC-DEMO `setup.md` + `how-to-guide.md`, arthrex `setup.md` + `setup.sh` + `getting-started.md`). User confirmed three design decisions via AskUserQuestion: three-file model + fold security into setup.md + port arthrex setup.sh.
- 2026-05-30: Phase 1 done. `git mv how-to-guide.md new-project-bootstrap.md` (preserves rename history). Top banner rewrites the audience framing; old "Doc home" resolution updated to describe the four-file root layout. Cross-references updated in `README.md` (file tree) and `project-overview.md` (file tree + Where-things-live table). Deviation from preview: placed at root rather than `docs/new-project-bootstrap.md` per the existing project convention (peer entry-point guides are not docs/ output).
- 2026-05-30: Confirmed installed skills before scoping Phase 2: `change-control` + `web-control` + `file-locator` skills present; `tools/file-locator-mcp/` exists; `project.yml` `approved_mcps` lists `chrome-devtools` + `file-locator` but NOT `atlassian` → drop `setup_atlassian_mcp` from the port.
- 2026-05-30: Phases 2 + 3 + 4 done in one session (user picked "heads-down all three" pacing). Wrote `setup.sh` (1385 lines, executable, `bash -n` syntax-valid, ported from arthrex with adaptations); rewrote `setup.md` (771 lines, 18 sections, security posture folded in as §15); rewrote `how-to-guide.md` (645 lines, 15 sections, day-to-day usage modeled on arthrex `getting-started.md`).
- 2026-05-30: Phase 5 wire-up audit done. CLAUDE.md's previously-aspirational `setup.sh --check` reference is now real ✓. README.md + project-overview.md file trees + Where-things-live table updated. No other stale references found outside `.claude/skills/` and `tasks/` (correctly excluded).
- 2026-05-30: Phase 6 verification done. `bash setup.sh --check` runs cleanly end-to-end on the WSL host. Detected OS, all installed tools, missing tools (qpdf, some pip packages, some VS Code extensions, no SSH key) flagged as warnings correctly — no script errors. **Nothing committed by Claude — awaiting user instruction to commit + push.**
- 2026-05-30: Committed and merged via PR #17 (commit 0d2977f → merge 734ce64). Branch `ben/069-setup-onboarding-overhaul` deleted local + remote.
- 2026-05-30: User feedback: setup.md still had too many manual steps — for non-engineer users (regulatory affairs, clinical, QE), the doc should explicitly tell them they can ask Claude to do the work instead. Added "🤖 You don't have to do this alone" top banner + 8 inline "✨ Or just ask Claude" callouts at steps 11 / 12 / 14 / 15 banner / 15f / 16 / 17 / 18 + a third "Claude-assisted" row in the "Choose Your Path" table. Under-the-hood manual commands kept so engineers still see what's happening. Captured as a lesson — see strategy + lessons content blocks below. PR #18 merged (commit 24722a2 → merge ee9b879).
- 2026-05-30: Applied same pattern to `how-to-guide.md` and `new-project-bootstrap.md` after user picked option 2. how-to-guide.md: added "🤖 Default to plain English with Claude" top banner reinforcing that slash commands are shown for recognition, not memorization; added "✨ Just ask Claude" callouts at §13 (change-control pre-flight + inline help) and §14 (WSL networking troubleshooting). new-project-bootstrap.md: added "🤖 You can drive most of this bootstrap by talking to Claude" top banner with 6 example prompts mapped to phases + inline callouts at Phase 1 (clone hitachi + install skills), Phase 2 (git init + gitignore), Phase 4 (personalize CLAUDE.md). Manual commands kept everywhere. PR #19 merged (commit eccabd8 → merge 12faf76).
- 2026-05-30: User raised confusion: "I don't understand the difference between setup.md and new-project-bootstrap.md." Diagnosed root cause: both use the word "setup" in different ways (set up *your machine* vs set up *a new repo*); new-project-bootstrap.md's Phase 0 IS the output of setup.md but that dependency wasn't called out; PDLC_DEMO shipping a "how to make your own demo" doc is meta and reads as ambiguous without strong framing. User picked option 1 ("keep both, sharpen the framing") from AskUserQuestion. Added "📍 You are here" three-row decision banner at the top of all three root onboarding docs (setup.md / how-to-guide.md / new-project-bootstrap.md). new-project-bootstrap.md gets an additional "⚠️ This is the doc most often read by mistake" callout + concrete GlobalLogic-hip-implant example. Phase 0 strengthened with explicit "Phase 0 is the *output* of setup.md" dependency callout. PR #20 merged (commit 6bd0cae → merge 58a9ab3).
- 2026-05-30: User noted README is most readers' actual entry point — surface the three onboarding docs there too. Split README.md "Where to start" into "🧑‍💻 New to PDLC_DEMO? Pick your onboarding path" (3-row table mirroring the in-doc banners) + "📖 Looking for specific content?" (the prior content rows). Same "replicators not contributors" warning under the new table. PR #21 merged (commit a8f17dd → merge 5e4e326).
- 2026-05-30: **Status changed to Complete.** All five PRs (#17 #18 #19 #20 #21) merged to main. Task scope fully delivered: arthrex three-file onboarding model adopted (setup.md / setup.sh / how-to-guide.md), prior how-to-guide content preserved as new-project-bootstrap.md, "ask Claude" non-engineer-first pattern applied across all three onboarding docs, "📍 You are here" decision banners installed for cross-doc disambiguation, README "Where to start" updated to surface the onboarding paths.

