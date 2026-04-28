# Sync Log

Append-only record of `/sync-skills` pull/push actions. Most recent entries at the top.

---

## 2026-04-22 — pull (docflow hook bash 3.2 fix + accumulated skill updates)

- Hitachi HEAD after sync: `219d46d`
- Pulled: 20 files
  - `agents/project-secops.md` (symlink-follow-through; sync-skills still flags as UPSTREAM_NEWER — known bug: `check` compares upstream symlink-target text vs local resolved-content sha)
  - `skills/digest/{SKILL.md, hooks/session-briefing.sh}` (→ v6 — sync-check on brief builds)
  - `skills/docflow/SKILL.md` + agents (adopter, converter, reviewer), `hooks/block-direct-conversion.sh`, `references/classification-taxonomy.md`, `templates/frontmatter-project.md`, `scripts/splice_hyperlinks.py` (new) — v27 → v29 (hyperlink preservation + link-count validation, F11-CLASSIFY markers Required, **bash 3.2 parser bug workaround in block-direct-conversion.sh — task ben/092**)
  - `skills/medtech-docs/SKILL.md` (→ v22 — `init` invokes `/dhf-manifest init` when installed)
  - `skills/project-console/console/{app.py, trace_matrix/router.py, web/static/console.css, web/templates/_base.html, documents_explorer.html, index.html, trace_matrix_view.html}` (→ v1.4.1)
  - `skills/task/SKILL.md` (v18 → v20 — PERMANENT RULES template + phase-end batching clarification)
- Trigger: after fast-forward pulling 19 commits on PDLC_DEMO `main`, the newly-installed `.claude/hooks/block-direct-conversion.sh` (symlink to the docflow skill hook) had a heredoc-inside-command-substitution pattern that macOS bash 3.2 can't parse — blocked every Bash tool call. Bypassed temporarily via `.state/docflow-active`; removed after the upstream fix landed.
- Caveat: on first pass, `pull-file` copied from the stale hitachi working-tree checkout (`e027eba`) and reported 13 files as "deleted-locally (upstream removed)" when upstream-head actually had them — fast-forwarded the hitachi working copy to `origin/main` (`219d46d`) and re-pulled. Root cause: `check` fetches `origin/main` but `pull-file` reads from the working tree. Logged as a sync-skills bug to file separately.
- project.yml: no changes — all affected skills already in `approved_skills`.
- Follow-ups (offered):
  - `/project-console sync` to regenerate `tools/project-console/start.sh`+`run.sh` against v1.4.1 (new templates, `--reload-exclude` patterns, BSD `xargs` fix)
  - `/task setup` to refresh `.claude/hooks/task-activate.sh` copy against v20 source
  - `/docflow setup` to confirm bypass marker lives at `.state/docflow-active` (already the case)
  - 22 `LOCAL_ONLY` files remain — task 024 (Unified Assistant Drawer) partials + advisor agents not yet pushed. Separate push decision.
- **Outcome note (added 2026-04-22 in the follow-on push session):** The project-console files in this pull were momentarily reverted to v1.4.1 in `origin/main`. A parallel session's `/sync-skills push` (the follow-on entry below) re-landed v1.5.0 on both hitachi and PDLC_DEMO, carrying the Overview section + unified Assistant drawer. Net effect across both entries: hitachi 1.4.1 → 1.5.0; PDLC_DEMO picks up the other pulled skill updates (docflow/task/medtech-docs/digest) AND keeps 1.5.0 project-console.

---

## 2026-04-22 — push (project-console 1.5.0 — Overview + unified Assistant drawer)

- Files: 17
  - `skills/project-console/VERSION` (1.4.1 → 1.5.0)
  - `skills/project-console/SKILL.md` (1.5.0 changelog entry)
  - `skills/project-console/console/overview/{__init__,router}.py` (new module)
  - `skills/project-console/console/assistant/{__init__,router}.py` (new module)
  - `skills/project-console/console/app.py` (wires overview_router + assistant_router + middleware overview_nav flag)
  - `skills/project-console/console/trace_matrix/router.py` (swapped custom drawer endpoint for generic)
  - `skills/project-console/console/web/static/assistant.js` (new — generic drawer JS)
  - `skills/project-console/console/web/static/docs-assistant-glue.js` (new — Documents-page wiring)
  - `skills/project-console/console/web/static/console.css` (new `.overview-*` + `.pc-assistant-*` rules)
  - `skills/project-console/console/web/templates/_assistant_drawer.html` (new)
  - `skills/project-console/console/web/templates/_base.html` (conditional Overview nav)
  - `skills/project-console/console/web/templates/documents_explorer.html` (mounts generic drawer)
  - `skills/project-console/console/web/templates/index.html` (conditional Overview tile)
  - `skills/project-console/console/web/templates/overview.html` (new)
  - `skills/project-console/console/web/templates/trace_matrix_view.html` (swapped to generic drawer)
- Branch: `sync/pdlc-demo-console-overview-assistant-drawer-2026-04-22`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/62
- Status: merged (--merge requested)
- Merge commit: `dd65333`
- Hitachi HEAD after sync: `dd65333`
- Follow-ups: sister project (Arthrex PCCP) can `/sync-skills pull` to receive 1.5.0 and the Overview section will light up if `project-overview.{pdf,pptx,md}` exists at repo root.

---

## 2026-04-20 — pull (bulk sync to pick up `.claude/state/` → `.state/` relocation + docflow tripwire)

- Hitachi HEAD after sync: `7c6e388`
- Pulled: 35 files
  - `agents/project-secops.md` (symlink unchanged — skill-side content identical; false-positive drift from sync.sh comparing across registries' symlinks)
  - `skills/best-practices/SKILL.md` (10 → 12 — new task-auto-create flow for `/best-practices fix`)
  - `skills/digest/{README,SKILL,hooks/session-briefing.sh,scripts/build_changelog.py}` (v4 → v5 — state relocation)
  - `skills/docflow/{README,SKILL,agents/converter,agents/refresher,templates/frontmatter-project,agents/adopter,agents/reviewer,hooks/block-direct-conversion.sh,references/classification-taxonomy.md}` (14 → 27 — new PreToolUse tripwire, T1 composite-table rules, shlex tokenization, state relocation)
  - `skills/lessons/SKILL.md` (1 → 2 — doc-only path update)
  - `skills/medtech-docs/{SKILL,templates/readme-strategies,scripts/render-sentinels.py,templates/claude-md-task-discipline,templates/rule-sentinel-blocks}` (17 → 21 — sentinel-block rendering infrastructure)
  - `skills/skill-creator/{README,SKILL,templates/skill-md}` (2 → 3)
  - `skills/strategy/{SKILL,agents/assembler,agents/scanner}` (10 → 11 — Domain Registry now rendered from `project.yml:strategy_domains[]`)
  - `skills/task/{README,SKILL,hooks/capture-check,hooks/capture-signals,hooks/check-active-task,hooks/session-cleanup,hooks/task-activate,tests/test-task-gate.sh}` (17 → 18 — state relocation, belt-and-suspenders `.state/docflow-active` cleanup)
- Post-update actions performed:
  - Created `.state/` at project root; migrated 3 files from `.claude/state/`: `active-tasks-3c4ade18-b44a-42ca-8fba-83930610b3bc.txt`, `briefing-last-shown-ben.txt`, `digest-llm-cache.json`. Session's active-task tracking survives the migration (verified via `task-activate.sh list`).
  - `.gitignore`: added `.state/` above the existing `.claude/state/` line (kept both).
  - Refreshed `.claude/hooks/task-activate.sh` (copy, not symlink) from v18 source — now reads state from `.state/`.
  - Installed docflow tripwire: `.claude/hooks/block-direct-conversion.sh` symlinked to skill source; registered `PreToolUse "Bash"` in `.claude/settings.json` via `register-hook.sh`. Smoke-tested: `pandoc --version` allowed (exit 0), `pandoc foo.docx -o foo.md` denied (exit 2) with the `/docflow` routing message.
  - 3 `/skill setup` re-runs subsumed by the manual steps above — all hooks already correctly symlinked to skill sources, so no full setup invocation was needed (v18/v5/v27 behavior activates on next tool call).
- project.yml: no changes — all affected skills already in `approved_skills`.
- Follow-ups:
  - 13 `LOCAL_ONLY` agents under `agents/` remain — these are project-console materialized personas (clinical-affairs, cybersecurity, core-team-panel, etc.); project-owned, not pushed upstream.
  - `strategy` v11 sentinel-block rendering is documented but not wired — `/strategy domains add|edit|remove` + `project.yml:strategy_domains[]` seeding + `/best-practices` drift check are all listed as upstream follow-ups in the v11 changelog.

---

## 2026-04-20 — push --merge (ben/020 secops v3 identity alignment)

- Files: `skills/secops/SKILL.md`, `skills/secops/scripts/resolve_user.py`
- Branch: `sync/pdlc-demo-secops-v3-2026-04-20`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/45
- Commit subject: "secops v3: roster-driven git identity alignment"
- Status: merged (`--merge` requested)
- Merge commit: `077d4b4`
- Hitachi HEAD after sync: `077d4b4`
- Notes: Adds `scripts/resolve_user.py` — YAML-roster parser with four-heuristic identity match (email / single-member / name-fuzzy / `$USER`) and `--align-git` to write repo-local git config. Paired with the digest skill (PR #44), which consumes the same helper via `--task-folder` for its SessionStart throttle state key. No upstream regressions; `/secops setup` gains step 6 (align-git) idempotently.

---

## 2026-04-20 — push --merge (ben/019 + ben/021 digest skill + medtech-docs template)

- Files: 7
  - 6 under `skills/digest/` — SKILL.md, README.md, VERSION, hooks/session-briefing.sh, scripts/digest.py, scripts/build_changelog.py
  - 1 under `skills/medtech-docs/templates/` — `changelog-project.md` (CHANGELOG.md seed)
- Branch: `sync/pdlc-demo-digest-skill-2026-04-20`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/44
- Commit subject: "Add digest skill + changelog-project template"
- Status: merged (`--merge` requested)
- Merge commit: `5f5bb9c`
- Hitachi HEAD after sync: `077d4b4` (after the paired PR #45 also merged)
- Notes: New `/digest` skill with two actions (`daily` SessionStart briefing + `log` CHANGELOG.md appender). Readable format: bold headline + optional body line + muted italic trace footer. Hybrid source — mechanical commit-body extraction by default, batched `claude -p` call on `--llm` (auto-on for `--retrospective`) for polished rewrites. Critical: sub-invocation runs with `cwd=/tmp` + stripped `CLAUDE_*` env to isolate from project context/hooks. Per-SHA LLM cache at `.claude/state/digest-llm-cache.json`. Medtech-docs template seeded automatically by `/digest setup`. Built and dogfooded on PDLC_DEMO.

---

## 2026-04-20 — pull (bulk sync, 53 files)

- Hitachi HEAD after sync: `765d3b6` (2 commits ahead of `origin/main` — unpushed docflow v3→v14 work; `sync.sh pull-file` reads working tree, so we picked up the unpushed content intentionally)
- Pulled: 53 files
  - Version bumps: task (14→17), secops (1→2), docflow (2→14), best-practices (9→10), medtech-docs (14→17), skill-creator (1→3), project-console (1.0.2→1.4.1)
  - New skill bundle: `skills/advisors/` (20 files — 12 persona agents + 2 panels + loader lib + render-grounding script + tests + overlay-defaults)
  - New shared references: `skills/shared/agent-design-principles.md`, `skills/shared/task-content-scanner.md`
  - New skill-creator templates: `hook-template.sh`, `readme-skill.md`, `skill-md.md`
  - `agents/project-secops.md` registry-root blob is now a symlink pointing at `skills/secops/agents/` (cp follows the link, so local content matches the skill source)

- Project Impact Analysis (mandatory per sync-skills v3 Step 5b):
  - **task v15 narrows task-gate exempt list.** `.claude/skills/**`, `.claude/agents/*`, `.claude/hooks/*`, CLAUDE.md, and `project.yml` now require an active task for Edit/Write. Exempt: `tasks/*`, `.claude/state/*`, `.claude/settings*.json`, `.claude/sync-log.md`, `.claude/MEMORY.md`, `.claude/memory/*`.
  - **task v16 fixes a silent Linux/WSL bug** where `task-activate.sh remove` was a no-op (GNU sed `-i ''` mismatch). Required a fresh copy of the script into `.claude/hooks/` — ran `/task setup`, which refreshed the copy.
  - **secops v2** no-op on Linux (was a macOS-only fix).
  - **best-practices v10 adds Required check** "Per-skill agents installed as symlinks". `/secops setup` (this run) converted `.claude/agents/project-secops.md` from a regular file into a symlink pointing at `../skills/secops/agents/project-secops.md`. Note: secops SKILL.md v2 still prescribes `cp`; there's a latent contradiction with best-practices v10 that should be resolved in a future secops bump.
  - **medtech-docs v17** adds Required check "Every docs folder has README" and new `update-external-references` action (v15) + rubric-vs-exclusion conflict surfacing (v16). Additive — no regeneration needed, but `/best-practices` may surface new findings for any docs/ folder lacking a README.
  - **project-console 1.4.1** scaffold template updates — ran `/project-console sync`, which regenerated `tools/project-console/run.sh` and `start.sh`. `run.sh` now reads `server.host`/`server.port` from `console.yaml` and passes `--reload-exclude` for `trace-matrix/**`, `.venv/**`, `__pycache__/*`, `.data/*`; `start.sh` is new (idempotent launcher) and no longer uses GNU-only `xargs -r`.
  - **skill-creator v2** codifies agent-symlink mandate. No project-owned files derived from its templates yet — no action.
  - **advisors skill (new)** — not activated. Requires `/advisors init` to install the agent symlinks into `.claude/agents/` and seed an `advisors:` block in `project.yml`. Deferred to user.

- Post-update actions run this session:
  - `/task setup` — refreshed `.claude/hooks/task-activate.sh` (v16 bugfix), all 5 hooks already registered
  - `/secops setup` — converted `project-secops.md` to symlink, hook + permissions already wired
  - `/project-console sync` — updated `run.sh` + `start.sh` to 1.4.1 template

- Post-update follow-ups completed later in the same session (under task 018):
  - Added `advisors`, `change-control`, `trace-matrix` to `project.yml` `security.approved_skills` (closed 3-skill secops drift)
  - `/advisors init` — installed 13 persona-advisor symlinks into `.claude/agents/`, seeded `advisors:` block in `project.yml` (enabled: regulatory-affairs, clinical-affairs, risk-management), regenerated grounding blocks
  - `/project-console start` — skipped, console not running
  - `/best-practices` audit — ran against full multi-DHF (10 DHFs), identified 16 Required FAILs (mostly pre-existing debt exposed by new v17 Required-severity checks)
  - Hygiene pass closed all 16 Required FAILs: CLAUDE.md Project Overview / For Claude / Task-First / Lessons sections, new `setup.md` (security posture), new `tasks/README.md` + `tasks/lessons-ledger.md`, 5 standards files got Verification Checks stubs, 6 missing docs folder READMEs created, 261 stub DHF READMEs got `## Conventions` via scripted pass, `.claude/skills/project-console/console/**` pycache cleaned (local-only, never tracked), 510(k) composition manifest updated to use actual folder names + 5 stub design-control folders created so every referenced piece resolves. Remaining debt is all WARN severity (Recommended). (agents-as-symlinks, docs-folder-has-README)

---

## 2026-04-15 — push --merge (task 017 change-control skill scaffold)

- Files: 20 (`skills/change-control/` — full scaffold)
- Branch: `sync/pdlc-demo-change-control-2026-04-15`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/19
- Commit subject: "Add change-control skill scaffold (design-captured, stubs)"
- Status: merged (`--merge` requested)
- Merge commit: `0588d71`
- Hitachi HEAD after sync: `0588d71`
- Notes: Design-captured scaffold only. Strategy C hybrid freeze-point model (draft → frozen → released), PreToolUse hook consent prompt, 6 extensibility seams + 8 open questions documented in SKILL.md. No live connectors yet.

---

## 2026-04-15 — push --merge (task 016 trace-matrix skill + project-console Trace Matrix section)

- Files: 23
  - 16 new files under `skills/trace-matrix/` — full v2 skill package (adapter_api.py, build.py, analyze.py, emit.py, graph.py, 5 default parsers, markdown_table.py, SKILL.md, .gitignore)
  - 5 new files under `skills/project-console/console/trace_matrix/` + `web/templates/` — loader, router, two Jinja templates, package init
  - 2 modified files in `skills/project-console/` — `console/app.py` (router include) + `console/web/templates/_base.html` (nav link). Both diffs purely additive; no upstream advances to merge.
- Branch: `sync/pdlc-demo-trace-matrix-2026-04-15`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/18
- Commit subject: "Add trace-matrix skill + project-console Trace Matrix section"
- Status: merged (`--merge` requested)
- Merge commit: `fed4644`
- Hitachi HEAD after sync: `fed4644` (→ advanced to `0588d71` by the subsequent change-control push)
- Notes: Adapter-generation model — skill ships sensible defaults plus a `rational_check` at init time; when defaults fail on a source doc, `/trace-matrix init` generates a per-project adapter file into `tools/project-console/trace-matrix/adapters/`. Build is always deterministic. Sidecar bumped to v1.1 with `source_files` + per-layer `warnings`. Console section is loose-coupled: reads JSON sidecars only, never imports from the skill. Includes the Systems Engineering Assistant drawer (resizable, localStorage-persisted threads, inline vanilla-JS markdown renderer with table support).
- Pre-push hygiene: scrubbed `__pycache__` from `skills/project-console/console/`. `sync.sh check` walks the filesystem directly and doesn't honor `.gitignore`, so build artifacts would otherwise have been staged into the hitachi PR. Filed as a follow-up for `sync-skills` v4.

---

## 2026-04-14 — push --merge (project-console 1.0.2 — default panels + assistant-framing rename)

- Files: 17 (13 rewritten persona templates + 2 new panels + SKILL.md + scaffold.py + VERSION)
  - `skills/project-console/agents/templates/` — all 12 persona files + `_group.md` rewritten with assistant framing. Titles suffixed "Assistant" (solo) or "Advisory Panel" (panels). System prompts rewritten from "You are the X lead" to "You are an AI assistant supporting the X team... You help the human X leads by...". STAY IN CHARACTER clauses rewritten to "never claim to BE the lead or commit the program to anything."
  - `skills/project-console/agents/templates/core-team-panel.md` — new, 5 members (PM + RA + Clinical + QE + R&D)
  - `skills/project-console/agents/templates/design-review-panel.md` — new, 6 members (Systems + R&D + V&V + HFE + Risk + QE), with instructions for projects to add cybersecurity if relevant
  - `skills/project-console/scripts/scaffold.py` — extended `sync` action to copy new agent templates into existing installs (previously `sync` only rewrote `run.sh`)
  - `skills/project-console/SKILL.md` — 1.0.2 changelog entry, corrects 1.0.1 uvicorn reload claim
  - `skills/project-console/VERSION` — 1.0.2
- Branch: `sync/pdlc-demo-project-console-1.0.2-default-panels-2026-04-14`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/17
- Commit: "project-console 1.0.2: default Core Team + Design Review panels"
- Status: merged (--merge requested)
- Merge commit: `fca1db9`
- Hitachi HEAD after sync: `fca1db9`
- Context: User feedback during PDLC testing flagged that the original "You are the X lead" framing risked implying the AI was replacing the real team. The 1.0.2 rename makes the support-not-substitute relationship unambiguous at every response. Same version also ships the default panels requested earlier in the session.

---

## 2026-04-14 — push --merge (project-console 1.0.1 — macOS/Windows junk filter)

- Files: 3
  - `skills/project-console/console/documents/tree.py` — new `_is_hidden()` helper centralizing the junk-file filter (dotfiles + `Icon\r` + `Icon` + `Thumbs.db` + `desktop.ini` + `._*` + `__MACOSX`); applied at all three walker sites (`list_children`, `_dir_has_any_children`, `_children`)
  - `skills/project-console/VERSION` — bumped to 1.0.1
  - `skills/project-console/SKILL.md` — 1.0.1 changelog entry with post-update annotation
- Branch: `sync/pdlc-demo-project-console-1.0.1-icon-filter-2026-04-14`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/16
- Commit: "project-console 1.0.1: hide macOS Icon files + Windows junk from docs tree"
- Status: merged (--merge requested)
- Merge commit: `78da92c`
- Hitachi HEAD after sync: `78da92c`
- Context: Bug reported from Arthrex PCCP immediately after pulling v1 — `Icon\r` files at several directory roots were cluttering the documents explorer. Fix landed same day. Project-side action: none (uvicorn `--reload` picks up the updated `tree.py` on next launch).

---

## 2026-04-14 — push --merge (project-console v1 — new reusable FastAPI console skill)

- Files: 54 (first release)
  - `skills/project-console/SKILL.md` — v1.0.0 initial. Actions: init, sync, theme <url>, run, status. Company-agnostic; ships light/dark theme packs + scrape-and-materialize `theme` action + 10 medtech persona templates + glob-scan dashboard discovery. Config in `tools/project-console/console.yaml` (project.yml never touched). PYTHONPATH launcher pattern so sync-skills pull is immediately effective. Three file ownership classes, narrow committed manifest.
  - `skills/project-console/README.md` — human-facing design & architecture doc
  - `skills/project-console/VERSION` — 1.0.0
  - `skills/project-console/.gitignore` — blocks `__pycache__/`, `*.pyc`
  - `skills/project-console/console/` — 18 files: FastAPI app (app.py, config.py, themes.py, auth.py, chat/, documents/, dashboards/ with discovery.py, web/templates/, web/static/)
  - `skills/project-console/themes/{light,dark}/` — 4 files: theme.yaml + footer.html.j2 each
  - `skills/project-console/agents/templates/` — 11 files: _group.md + 10 personas (regulatory, clinical, quality, systems, risk, HFE, R&D, V&V, cybersecurity, post-market)
  - `skills/project-console/scripts/scaffold.py` — init/sync/status implementation
- Branch: `sync/pdlc-demo-add-project-console-2026-04-14`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/15
- Commit: "Add project-console skill — scaffold + theme + dashboards"
- Status: merged (--merge requested)
- Merge commit: `a8e817a`
- Hitachi HEAD after sync: `a8e817a`
- Project context: Built in task 015. PDLC_DEMO's hand-built `tools/project-console/` extracted, genericized, and migrated onto the skill-driven version in the same task. Config contract dry-validated against Arthrex PCCP `project.yml` before push (all required fields present; sister-project compat bar satisfied).

---

## 2026-04-14 — push --merge (medtech-docs v16: rubric-vs-exclusion conflict surfacing)

- Files: 4
  - `skills/medtech-docs/SKILL.md` — bumped 15 → 16; new Step 2.5 in `update-external-references` action that detects rubric-vs-existing-exclusion conflicts and surfaces them with IMPORT / KEEP EXCLUDED / DEFER resolution; new v16 changelog entry
  - `skills/medtech-docs/templates/readme-fda-guidance.md` — added Scope Qualifier column to Evaluated — Not Applicable table
  - `skills/medtech-docs/templates/readme-standards.md` — added Scope Qualifier column to Evaluated — Not Required table
  - `skills/medtech-docs/templates/readme-industry-frameworks.md` — added Scope Qualifier column to Evaluated — Not Required table
- Branch: `sync/pdlc-demo-medtech-docs-v16-2026-04-14`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/14
- Commit: "medtech-docs v16: surface rubric-vs-existing-exclusion conflicts"
- Status: merged (--merge requested)
- Merge commit: `2d88ce6`
- Hitachi HEAD after sync: `2d88ce6`
- Source task: PDLC_DEMO `tasks/ben/012-medtech-docs-update-external-references.md` (closes the rubric-override follow-up captured under v15)

---

## 2026-04-14 — push --merge (medtech-docs v15: update-external-references action)

- Files: 4
  - `skills/medtech-docs/SKILL.md` — bumped 14 → 15; new `update-external-references` action; updated frontmatter description
  - `skills/medtech-docs/templates/readme-fda-guidance.md` — full rewrite from "applicability reports" model to "distilled copies + linked originals" model (model B)
  - `skills/medtech-docs/templates/readme-standards.md` — added Original Source column to Distilled Standards table
  - `skills/medtech-docs/templates/readme-industry-frameworks.md` — added Spec URL column to Active Frameworks table
- Branch: `sync/pdlc-demo-medtech-docs-v15-2026-04-14`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/13
- Commit: "medtech-docs v15: add update-external-references action"
- Status: merged (--merge requested)
- Merge commit: `d30a7f3`
- Hitachi HEAD after sync: `d30a7f3`
- Source task: PDLC_DEMO `tasks/ben/012-medtech-docs-update-external-references.md`
- Known follow-up not in this PR: rubric-vs-existing-exclusion conflict surfacing (IHE Profiles case). Tracked on task 012.

---

## 2026-04-13 — push --merge (sync-skills v3: mandatory project impact analysis on pull)

- Files: 1
  - `skills/sync-skills/SKILL.md` — adds mandatory Step 5b Project Impact Analysis to the `pull` action; new v3 changelog entry with post-update annotation
- Branch: `sync/pdlc-demo-sync-skills-pull-impact-analysis-2026-04-13`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/12
- Commit: "sync-skills v3: mandatory project impact analysis on pull"
- Status: merged (--merge requested)
- Merge commit: `b19debe`
- Hitachi HEAD after sync: `b19debe`

---

## 2026-04-13 — pull

- Hitachi HEAD after sync: `a908aa2`
- Pulled: 1 file
  - `skills/secops/SKILL.md` — adds `version: 1` / `updated: 2026-04-12` YAML frontmatter so `/best-practices` "Skills are versioned" check passes (upstream PR #11, commit `a908aa2`)
- Analysis: trivial, additive, no behavior change. No setup re-run needed. No project action required beyond the pull itself. Next `/best-practices audit` will flip secops "versioned" check FAIL → PASS.
- project.yml: no changes
- Follow-ups: none

---

## 2026-04-13 — push --merge (task 009: shared strategy docs + sub-DHF → DHF rename)

- Files: 19 (18 edited, 1 new via rename, 1 deleted via rename)
  - medtech-docs v14 SKILL.md + 6 readme templates + new `readme-dhf.md` (rename of `readme-sub-dhf.md`)
  - strategy v10 SKILL.md + scanner.md + assembler.md + default-strategy.md + regulatory-strategy.md
  - tracker v5 SKILL.md
  - best-practices v9 SKILL.md (rename pass)
  - task v14 SKILL.md (rename pass)
  - docflow v2 SKILL.md + README.md (rename pass)
  - Deleted: `readme-sub-dhf.md` (replaced by `readme-dhf.md`)
- Branch: `sync/pdlc-demo-shared-strategy-2026-04-13`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/10
- Commit: "Shared strategy docs + sub-DHF → DHF rename"
- Status: merged (--merge requested)
- Merge commit: `54cc8edd76b311cbd331cc3b6a8991ccbd7d340a`
- Hitachi HEAD after sync: `54cc8ed`
- Follow-ups: run `/best-practices audit` on PDLC_DEMO to verify compliance with the updated v9/v10/v14 skills

---

## 2026-04-13 — push --merge (task 007: topology-aware skills)

- Files: 18
  - `agents/project-secops.md`
  - `skills/medtech-docs/SKILL.md` + 7 templates (readme-sub-dhf, readme-clinical, readme-postmarket, readme-risk-management, readme-cybersecurity, readme-strategies, readme-design-controls)
  - `skills/best-practices/SKILL.md`
  - `skills/strategy/SKILL.md` + `agents/scanner.md` + `agents/assembler.md`
  - `skills/tracker/SKILL.md`
  - `skills/task/SKILL.md`
  - `skills/docflow/SKILL.md` + `README.md`
  - `skills/secops/templates/permissions.json`
- Branch: `sync/pdlc-demo-topology-2026-04-13`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/9
- Commit: "Topology-aware skills: unified sub-DHF shape"
- Status: merged (--merge requested)
- Merge commit: `58e601debb2e90f691a03f0dafb96653b97373a4`
- Hitachi HEAD after sync: `58e601d`
- Follow-ups: none — closes task 007

---

## 2026-04-12 — pull (task v11 + new secops skill)

- Hitachi HEAD after sync: `03f5849`
- Pulled: 8 files
  - `skills/manifest.md` — registry index updated for task v11 and new secops skill
  - `skills/task/SKILL.md` — bumped to v11; setup grew from 8 to 12 steps (now symlinks `session-env.sh` + `session-cleanup.sh` and registers SessionStart/SessionEnd hooks)
  - `skills/task/hooks/session-env.sh` — moved into task skill (was previously in `.claude/hooks/`)
  - `skills/task/hooks/session-cleanup.sh` — moved into task skill
  - `skills/secops/SKILL.md` — new skill v1 packaging the security posture
  - `skills/secops/agents/project-secops.md` — agent moved from registry `agents/` to `skills/secops/agents/`
  - `skills/secops/hooks/security-assert.sh` — new SessionStart hook (16 security checks, cached in SECOPS.md)
  - `skills/secops/templates/permissions.json` — canonical 70-entry Bash/Read/Edit/Write allow list
- Setup re-runs:
  - `/task setup` — symlinked `session-env.sh` + `session-cleanup.sh` into `.claude/hooks/`; registered SessionStart and SessionEnd hooks (PreToolUse task gate already registered, was a no-op).
  - `/secops setup` — copied agent into `.claude/agents/project-secops.md` (replaced the orphan at the same path); symlinked `security-assert.sh`; registered SessionStart hook; merged 70 entries into `permissions.allow` (0 already present).
- `project.yml` — added `secops` to `security.approved_skills`. `approved_agents` already contained `project-secops`.
- Note: hitachi local checkout was 1 commit behind `origin/main` at the start of the run; ran `git pull --ff-only` mid-flow because `sync.sh pull-file` reads from the working tree, not `origin/main`. Worth flagging upstream — first attempt silently no-op'd six pulls.
- Follow-ups: start a new session to fire `security-assert.sh` for the first time (or run `/secops check`).

---

## 2026-04-12 — pull

- Hitachi HEAD after sync: `8dacc72` ("Update best-practices and medtech-docs with registry sync improvements (#4)")
- Pulled: 2 files
  - `skills/best-practices/SKILL.md` — `audit` and `sync` actions now prefer `local_path` from `project.yml` before `gh` CLI / raw URL; `sync` also runs `git pull --ff-only` on the local clone first. Pure improvement, benefits us now that we already have `local_path` set.
  - `skills/medtech-docs/SKILL.md` — `init` template evolved: new `device_family` field in `project:` block; `local_path` added to hitachi registry template; `registries.hitachi.skills` list alphabetized and extended with `lessons`, `strategy`, `sync-skills`, `task`, `tracker`; `approved_skills` now auto-populated from registry skills lists; new `{{DEVICE_FAMILY}}` and `{{APPROVED_SKILLS}}` substitutions; CLAUDE.md manifest table row for `registries:` mentions `local_path`.
- Project alignment follow-ups (done):
  - **`project.yml`** — alphabetized `registries.hitachi.skills` and added `sync-skills` (now in the upstream registry after PR #3/#4). Rebuilt `approved_skills` as the union of anthropic builtin + hitachi registry skills (13 entries, alphabetized). Added a comment noting the list should mirror the registries' skills lists.
  - **`CLAUDE.md`** — updated the `registries:` row in the project manifest table to mention `local_path` for clone-based sync (matches new template wording).
- No new `### setup` actions introduced by this pull, no new best-practices checks that would break our audit.
- Upstream commit was authored by this user from another project (`arthrex-pccp` task 047) — same pattern we used in PR #2 (Arthrex genericization).

---

## 2026-04-12 — push --merge

- Files: `skills/sync-skills/SKILL.md`, `skills/sync-skills/scripts/sync.sh`
- Branch: `sync/pdlc-demo-add-sync-skills-2026-04-12`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/3
- Commit subject: "Add sync-skills skill for bidirectional registry sync"
- Status: merged (`--merge` requested)
- Merge commit: `2d5e7c3`
- Hitachi HEAD after sync: `2d5e7c3`
- Notes: First publication of `sync-skills` to the registry. Dogfooded — used `/sync-skills push --merge` to upstream itself.

---

## 2026-04-12 — baseline

- Hitachi HEAD: `4e54855` (post-merge of PR #2 "Genericize project-specific references in skills")
- Local skills installed from hitachi: best-practices, docflow, lessons, medtech-docs, skill-creator, strategy, task, tracker
- Local agents installed from hitachi: project-secops
- Project-local skill (not in hitachi yet): **sync-skills** — added during PDLC_DEMO task 008
- `check` output: clean (zero `UPSTREAM_ONLY`, zero `UPSTREAM_NEWER`; one `LOCAL_ONLY` for `sync-skills` itself, excluded from the diff by design)
- Follow-ups: consider pushing `sync-skills` upstream once exercised in this project

## 2026-04-27 — pull

- Hitachi HEAD after sync: `731b09f`
- Pulled: 284 files (incl. 1 agent symlink restoration)
  - **Modified existing skills:** digest, docflow, lessons, project-console, secops, strategy, task, shared, agents/project-secops
  - **New skills installed:** dhf-manifest, web-control, docx, pdf, pptx, xlsx
  - **New supporting libraries:** skills/shared/scripts/office/* (soffice, pack, unpack, validate, validators, schemas)
  - **Major content additions:** docflow doc-type-packs (24 packs), mermaid + table rule packs, new agents (interpret_image, structure_body, structure_requirement_body)
- Skipped: 3 LOCAL_ONLY (push candidates) — `skills/secops/scripts/resolve_user.py`, `skills/task/hooks/{capture-check,capture-signals}.sh` (the latter two are deprecated by task v23)
- project.yml: needs `dhf-manifest` and `web-control` added to `security.approved_skills`
- Follow-ups required:
  - Run `/task setup` — v23 migration removes orphan `capture-signals.sh` + `capture-check.sh` symlinks and their `settings.json` hook entries
  - Run `/secops setup` — v3+ git-identity alignment via `resolve_user.py`
  - Run `/project-console sync` then `/project-console start` — scaffold is at 1.4.1, skill is at 1.7.6 (Overview section, Unified Assistant drawer, tiered grounding, footnote citations, sticky auto-scroll, configurable grounding roots, browsable skill-library roots)
- Follow-ups optional:
  - `/dhf-manifest init` to bootstrap the new sibling-of-/trace-matrix manifest skill
  - `/web-control setup` if/when a consumer skill needs Chrome automation
