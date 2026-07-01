# Usage Metrics — Design & Architecture

Design notes for the `usage-metrics` skill. Not loaded during normal operation — see `SKILL.md` for usage.

## Overview

Measures Claude Code token usage and equivalent cost across a team, with **no shared server and no LLM in the data path**. Each teammate collects their own usage locally from session transcripts; git is the aggregation transport; a script renders a single self-contained HTML cost dashboard.

## Lineage

Original skill. The collection mechanism (transcript parsing) and the git-as-aggregator pattern were validated against real Claude Code session files before the skill was scaffolded.

## Key Design Decisions

### git-as-aggregator (no shared collector)
The only thing a central OTel collector would buy is "everyone's data in one place" — git already does that. Each teammate's `collect` writes per-session JSON under their **own** `tasks/{task_folder}/_usage-metrics/`; normal commits converge the data; `aggregate` rolls it up. No server to stand up, no VPN, no egress decision.

### The folder is the identity (no PII)
Because each person's data lives under their own task folder, the folder path identifies the person. No email/account id is written into committed records (transcripts carry none anyway). One file per `session.id` makes concurrent sessions and multi-machine use **collision-free** — distinct filenames never conflict in git.

### Source in the skill, execution in `tools/`
The skill directory is the **source of truth** (real `scripts/`). `tools/usage-metrics/` holds **symlinks** to those scripts and is the **execution surface**, so any runtime artifacts (`__pycache__`, a future venv, pip deps) land in `tools/` — never in `.claude/skills/`. Scripts also set `sys.dont_write_bytecode = True` as belt-and-suspenders.

### Cost is computed, clearly-labelled estimate
Transcripts carry no cost field, so cost = measured tokens × a per-model rate card (`tools/usage-metrics/pricing.json`, seeded from the bundled template, fetched from Anthropic's published pricing). Cache writes are split 5m/1h for accuracy. Subscription billing is a flat fee — the dashboard shows the equivalent API-list-price cost and says so.

### Auto-refresh via staleness-gated SessionStart hook
Mirrors the SECOPS 7-day TTL pattern: on session start, if the local dashboard is older than `refresh_ttl_days`, regenerate it in the background, **local-only** (no git pull/commit/network). Silent fast-exit when fresh.

## Effort-Estimation Research Basis

The by-hand person-hour anchors in [`references/effort-estimation-rubric.md`](references/effort-estimation-rubric.md) are grounded in published software-engineering and audit/security literature where a real norm exists, and explicitly flagged **judgment-tier** where none does. This is the audit trail for why each anchor row carries the number it does — the honesty of the aggregate depends on distinguishing "cited" from "constructed." Summaries below; the rubric table carries the one-line operational form (and renders live in the project console's Value & ROI methodology section).

Two credibility tiers are used throughout: **anchored** (a real published figure — cite it) vs **judgment-tier** (no external hour-norm exists — a defensible construction is given and must be labelled as such). Several personas legitimately fall in the second tier; saying so is what makes the total survive a skeptic.

### Test engineering (writing tests)
**Adopted anchor:** testing ≈ **30–50% of development effort** (or FP × 1.2 test cases), **× 1.3–3 for IEC 62304 Class C**.
The "testing is roughly a third to a half of development effort" result is the most durable finding in the field (Boehm's COCOMO II phase-distribution tables; Capers Jones' lifecycle framing that ~half of full-lifecycle cost goes to finding/fixing defects). Don't quote Jones' 50% as "hours authoring tests" — it's a defect-removal-lifecycle figure. The strongest support for the **regulated adder** is DO-178C avionics data: formal verification adds 25–150% to software cost, and the highest assurance level (DAL A ≈ IEC 62304 Class C) runs ~3× DAL B/C — so anchoring Class C test authoring high (2–3×) is defensible. The per-test-case rate (~15–24 cases/person-day) is weak/anecdotal — a "test case" isn't a standardized unit; use only as a sanity ceiling.
- Boehm, *Software Cost Estimation with COCOMO II* (2000), USC-CSE — https://athena.ecs.csus.edu/~buckley/CSc231_files/Cocomo_II_Manual.pdf
- Capers Jones — https://reworkcost.com/testing-defect-removal-effort ; Jones FP×1.2 rule — https://www.tutorialspoint.com/estimation_techniques/estimation_techniques_testing.htm
- Test/production code co-evolution (Zaidman et al., *Empirical Software Engineering* 2011) — https://link.springer.com/article/10.1007/s10664-010-9143-7 ; Miranda et al. 2025 (500+ repos) — https://onlinelibrary.wiley.com/doi/full/10.1002/smr.70035
- DO-178C verification uplift / DAL A ≈ 3× — https://www.rapitasystems.com/do178 , https://afuzion.com/do-178-introduction/ , https://en.wikipedia.org/wiki/DO-178C

### Defect fixing
**Adopted anchor:** **~4–6 focused person-hours/defect** baseline · **× 2–4 regulated re-verification** (judgment).
Capers Jones' blended average is ~5 h/defect; modern empirical medians bracket it (~1.5 h documentation bugs → ~14 h security/algorithm bugs). Size by **defect count, not severity** — several studies find higher-severity bugs are fixed *faster* (prioritization), so severity is not a linear effort multiplier. Jones' **rework ≈ 40–50% of total project effort** is a useful independent top-down cross-check. **Two cautions baked into the rubric:** (1) never cite "100× cost to fix in production" as fact — the phase-escalation curve is directionally sound but its headline multipliers are contested (Bossavit, *The Leprechauns of Software Engineering*, 2015, traced them to mis-cited secondary sources); (2) the regulated re-verification multiplier (~2–4×) has **no published per-defect hour norm** — it's engineering judgment grounded in the IEC 62304 §6/§8 obligation to re-run V&V, update traceability, and change-control the fix.
- McConnell, "An Ounce of Prevention" (synthesis of Jones/Boehm/Gilb/Hughes) — https://stevemcconnell.com/articles/an-ounce-of-prevention/
- Capers Jones rework % — https://reworkcost.com/testing-defect-removal-effort ; defect-removal efficiency — https://www.ppi-int.com/wp-content/uploads/2021/01/Software-Defect-Removal-Efficiency.pdf
- NIST/Tassey, *Economic Impacts of Inadequate Infrastructure for Software Testing* (2002) — https://www.nist.gov/document/report02-3pdf
- Empirical fix-time studies — https://arxiv.org/pdf/2103.11518 (OSS-Fuzz), https://arxiv.org/pdf/2411.02091 (Linux-kernel regressions)
- Contested phase-cost curve (Bossavit) — https://squidarth.com/software-engineering/2021/09/27/leprechauns.html

### Code review
**Adopted anchor:** **150–400 LOC/hour/inspector** (thorough 150–200; effectiveness cliff ~400–500); formal **Fagan floor ~125–150 LOC/hr**.
Two independent primary sources converge, which is the strength here. The **Cisco/SmartBear** study (2,500 reviews / 3.2M LOC) found defect-finding collapses above ~400–500 LOC/hr and reviewers wear out after ~60 min / ~300–400 LOC — an *effectiveness ceiling*, the fast bound. **Wiegers** recommends 150–200 LOC/hr for thorough review (up to 300–400 upper), with shop data of ~200 LOC/hr and 3.6 defects/person-hour. **Fagan** formal inspection (~125–150 LOC/hr/inspector + separate prep + capped meeting) is the regulated/Class-C tier and finds 80–90% of defects. Multiply per-inspector hours by N participants for a formal inspection. The Cisco numbers are a vendor study (frame as a ceiling, not academic result).
- Cohen et al. (SmartBear), *Best Kept Secrets of Peer Code Review* — Cisco case study — https://static0.smartbear.co/support/media/resources/cc/book/code-review-cisco-case-study.pdf ; summary — https://mikeconley.ca/blog/2009/09/14/smart-bear-cisco-and-the-largest-study-on-code-review-ever/
- Wiegers, *Improving Quality Through Software Inspections* (ProcessImpact, 2002) — https://www.processimpact.com/articles/inspects.pdf
- Fagan inspection (IBM Systems Journal, 1976) — https://en.wikipedia.org/wiki/Fagan_inspection

### Document / design review (inspection)
**Adopted anchor:** **8–12 pages/hour** ordinary (Wiegers) · **1–3 pages/hour** rigorous/regulated (Gilb & Graham).
Wiegers' 8–12 pg/hr is the mainstream pace for normal technical docs. Gilb & Graham's optimum checking rate is ≈ **one logical page (300 non-comment words) per hour** — for critical documents, rates as slow as 0.1 page/hr can still be cost-justified (requirements specs carry ~20–80 defects/page, most latent). The two aren't contradictory — Gilb's "logical page" is a fixed 300-word block, so his ~1 pg/hr and Wiegers' 8–12 physical-pages/hr anchor opposite ends of rigor. **State the page unit** (physical vs 300-word logical) or the estimate is ambiguous. Regulated DHF deliverables / V&V protocols / risk files → the slow (1–3 pg/hr) end. Review overall runs 5–15% of project budget (sanity cross-check). **Traceability-matrix / DHF cross-reference review has no clean pages/hour norm** (a reviewer chases links across documents — not linear in pages): judgment-tier, use the Gilb floor + an explicit link-verification adder.
- Wiegers, *Improving Quality Through Software Inspections* (2002) — https://www.processimpact.com/articles/inspects.pdf
- Gilb & Graham, *Software Inspection* (Addison-Wesley, 1993) — optimum checking rate (corroborated via gilb.com / NASA JPL formal-inspection data at ntrs.nasa.gov)

### Audit / gap assessment
**Adopted anchor:** **QMS audit ~3–5 auditor-days (24–40 h)** for a 25–65-person scope; single-standard/gap **~1–3 days + reporting**.
The one authoritative auditor-days norm that exists: **IAF MD 5:2023** Table QMS 1 is a globally binding accreditation mandatory document — every ISO 13485 / 9001 certification body must staff audits from it (surveillance ≈ 1/3, recertification ≈ 2/3 of the initial figure). It sizes a *certification* audit against a QMS; a focused single-standard internal audit or gap assessment is a fraction (~1–3 consultant-days + ~0.5–1 day reporting). **ISO 19011:2018** governs the *method* (audit program, planning, reporting) but publishes no time table — cite it for what work exists, IAF MD 5 for how many days.
- IAF MD 5:2023, *Determination of Audit Time* — https://www.iaf.nu/iaf_system/uploads/documents/IAF_MD5_Issue_4_Version_3_14062023.pdf ; Table QMS 1 numbers reproduced — https://auva.com/2021/01/14/audit-time-calculation-for-iso-9001/
- ISO 19011:2018 (method, no durations)

### Security red-teaming / penetration testing
**Adopted anchor:** **5–10 tester-days (40–80 h) + 1–2 days reporting** per web-app/SaMD-interface test; full red-team = several weeks.
**CREST** (the recognized pentest-firm accreditation body) scoping guidance is the de-facto industry standard: external network 2–5 days, web-app 5–15 days, internal infra 5–15 days; drivers are roles/APIs/endpoints. Corroborated by OWASP WSTG method and SANS scoping. **NIST SP 800-115** and **PTES** define the phases but explicitly prescribe no durations — cite them for method, CREST for effort. Frame as vendor/scoping ranges, not peer-reviewed research.
- CREST 2025 guidance — https://securityboulevard.com/2025/03/crest-penetration-testing-what-you-need-to-know-2025-guide/ , https://www.precursorsecurity.com/blog/crest-penetration-testing-guide
- NIST SP 800-115 (method) — https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-115.pdf ; OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/ ; SANS scoping — https://isc.sans.edu/diary/26448

### RCA / CAPA investigation — judgment-tier (no external norm)
**No rigorous published person-hour norm exists.** FDA 21 CFR 820.100 and ISO 13485 §8.5 mandate that RCA/CAPA happen and be documented; RCA-tool references (5-Whys, fishbone, FTA) publish no effort figure. Industry practice bounds CAPA by *calendar* (e.g., a 30/60/90-day closure clock), not effort. A moderate facilitated RCA (team of 3–5, one or two working sessions + data pull + write-up) is realistically ~16–60 person-hours — but this is an **internal engineering estimate**, flagged as such, scaling with severity/evidence depth.
- Method references (confirmed no hour-norm) — https://www.greenlight.guru/blog/capa-root-cause-analysis , https://medicaldeviceacademy.com/root-cause-analysis/

### Document red-teaming (adversarial review) — judgment-tier (no external norm)
**No standards body, accreditation document, or peer-reviewed figure exists** for adversarially reviewing a document. The rubric uses a **constructed proxy** from inspection-rate literature: effort ≈ (document pages ÷ ~1–2 pg/hr/reviewer) × (number of adversarial lenses) × (passes) — e.g., a 40-page narrative × 3 lenses × 1 pass ≈ ~80 reviewer-hours. This must be labelled as a constructed proxy, not a cited standard. (Basis borrowed from the Fagan/Wiegers/Gilb inspection rates above.)

## Dependencies

| File | Required by | Purpose |
|------|-------------|---------|
| `project.yml` `usage_metrics` block | all actions | method/identity/storage/refresh config |
| `project.yml` `team.active[].task_folder` | collect, aggregate | per-person identity + labels |
| `.claude/skills/shared/scripts/resolve_user.py` | collect, aggregate | canonical roster resolver |
| `.claude/hooks/register-hook.sh` | setup | idempotent SessionStart registration (installed by `/task setup`) |
| `tools/usage-metrics/pricing.json` | aggregate | per-model rate card (project-local; seed in `templates/`) |
| `~/.claude/projects/<project>/*.jsonl` | collect | source session transcripts (read-only) |

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill has SKILL.md | `.claude/skills/usage-metrics/SKILL.md` exists | Required | shared |
| Frontmatter complete | name, description, version, updated all present | Required | shared |
| README.md exists | Design doc at skill root | Required | shared |
| Changelog current | Latest entry matches frontmatter version | Required | shared |
| Hook symlinked, not copied | `.claude/hooks/usage-metrics-refresh.sh` is a symlink into the skill | Required | shared |
| Status line symlinked, not copied | `.claude/statusline.sh` is a symlink into the skill (or a deliberate project fork) | Recommended | shared |
| Execution via tools symlinks | `tools/usage-metrics/{collect,aggregate}.py` are symlinks to skill scripts | Recommended | local |
| Project-agnostic | No company/device/team/task names in any skill file | Required | shared |
| No PII in records | committed `_usage-metrics/*.json` contain no email/account id | Required | local |
| Config present | `project.yml` has a `usage_metrics:` block | Recommended | local |
| Daily-aggregate workflow | `.github/workflows/usage-metrics-aggregate.yml` exists | Recommended | local |
| Aggregation deterministic | re-running `aggregate.py` on unchanged inputs is byte-identical | Required | shared |

## Changelog

- 8 (2026-06-30): **`## Economics` block is now self-describing (`method_ref`).** The economics schema gains an optional `method_ref` field naming this rubric's path, and `parse_task_economics` tolerates it (unknown keys ignored — no parser change). Paired with the `task` skill v30 change: the task-doc PERMANENT RULES block now points at the rubric, so a session resuming from a task doc **alone** — without loading either skill — can follow `method_ref` (or the doc's rule 6) back to the anchors/schema to add or refresh an estimate. Closes a resume-correctness gap where "read the rubric" lived only in the task checkpoint action. Pointer only — the rubric is never copied into task docs.
- 7 (2026-06-30): **Effort-estimation anchor set expanded + research basis documented.** The rubric's Anchors table gains published-norm rows for **test engineering** (30–50% of dev effort; ×1.3–3 for IEC 62304 Class C, per DO-178C), **defect fixing** (~4–6 h/defect; ×2–4 regulated re-verify; never cite the contested "100×"), **code review** (150–400 LOC/hr; Fagan floor for Class C), **document/design review** (8–12 pg/hr ordinary, 1–3 pg/hr regulated), **audit/gap assessment** (IAF MD 5:2023 auditor-days), and **security red-team/pentest** (CREST tester-days), plus explicit **judgment-tier** rows for **RCA/CAPA** and **document red-teaming** (no external norm — constructed proxy given). New `## Effort-Estimation Research Basis` section here carries the per-cluster summaries, credibility caveats, and source links; the rubric table stays concise and renders live in the console's Value & ROI methodology section. Method mechanics unchanged (`method_version: 1` still valid) — this refines the reference anchors, not the estimation procedure.
- 6 (2026-06-30): **Economics gains `agentic_hours` → per-task `hours_saved`.** `parse_task_economics` now reads an `agentic_hours` field (your estimate of how long the task actually took) and emits per-task `hours_saved` = by-hand `manual_hours` (ranged) − `agentic_hours`, plus `personas` (the task category) ranked by hours; `value_summary` headlines total **hours saved** + total agentic hours. Rubric updated. Person-hours stays the primary metric.

- 5 (2026-06-30): **Fix recurring fast-forward/merge abort caused by per-session data.** `collect.py` writes each session's `tasks/<tf>/_usage-metrics/YYYY-MM/<id>.json` into the working tree; `publish.py` then commits the same file to the shared branch via an isolated worktree. The file therefore became **tracked on the branch but untracked in the working tree** — so any later `git pull --ff-only` / `gh pr merge` that updated the branch aborted with "untracked working tree files would be overwritten" (recurred every session). Fix: `setup` now **git-ignores** the per-session data (`tasks/*/_usage-metrics/` + `**/_usage-metrics/`), and `publish.py` **force-adds** (`git add -f`) so it still reaches the branch. Ignored files are silently superseded by the tracked version on pull — the abort can't happen. Already-tracked files stay tracked (gitignore never untracks); only fresh local copies are ignored. The isolated-worktree publish still never touches the working tree. **Post-update:** sister projects must re-run `/usage-metrics setup` after pulling (to get the `.gitignore` entry) — the `publish.py` change alone rides the sync, but the gitignore line is installed by `setup`.
- 4 (2026-06-25): Added a team-shared **status line**. `statusline.sh` (skill-owned) renders `[model] <bar> IN/SIZE ctx · ↑OUT resp · $cost` from the Claude Code statusLine stdin (`context_window.*` + `cost.total_cost_usd`); jq-guarded with graceful degradation on builds that omit `context_window.*`. `setup` now symlinks it to `.claude/statusline.sh` and registers the `statusLine` block in `settings.json` — idempotent, and a pre-existing different `statusLine` is treated as a project fork and left alone. Same self-contained symlink model as the hooks (a `/sync-skills pull` auto-updates the installed line).
- 3 (2026-06-22): Added `publish.py` + a SessionEnd hook — each teammate's own `_usage-metrics/` data is pushed to the shared branch via an **isolated git worktree** (working branch untouched; fetch+retry for concurrency), closing the loop so the daily-aggregate workflow always has current data. Gated by `usage_metrics.publish.enabled`. `setup` now installs/registers both hooks (SessionStart refresh + SessionEnd publish).
- 2 (2026-06-22): Team dashboard output moved to `tools/usage-metrics/` (anonymized `Member N`; `index.html` + consolidated `usage.json` consumed by project-console's Metrics view). Token quantities normalized to MTok; rate card collapsed to a single Write column (1h rate). `setup` now installs a daily-aggregate GitHub Actions workflow (CI re-aggregates committed per-user data; collection stays local). Aggregation is deterministic (byte-identical re-runs).
- 1 (2026-06-22): Initial version — local transcript-parse collection, git-as-aggregator roll-up, self-contained HTML dashboard (cost projection + daily/by-member/by-model charts + rate card), per-model cost from an editable rate card, and a staleness-gated SessionStart auto-refresh hook. `setup` self-wires into a project (hook symlink + registration, `project.yml` block, file-locator exclude, pricing seed, `tools/` execution symlinks).
