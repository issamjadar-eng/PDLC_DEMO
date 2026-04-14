# Sync Log

Append-only record of `/sync-skills` pull/push actions. Most recent entries at the top.

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
