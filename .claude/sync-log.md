# Sync Log

Append-only record of `/sync-skills` pull/push actions. Most recent entries at the top.

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
