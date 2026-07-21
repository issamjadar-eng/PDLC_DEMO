# 106 — Client PDLC Deck Refresh (June→July improvements + new screenshots)

**ID**: 106
**Created**: 2026-07-16
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
   - **when you tick a Todo off (or add/restructure Todos), fill/refresh the matching `## Economics` entry in the same edit** — the by-hand person-hours that unit would have taken, ranged + persona-tagged, per the rubric (if `## Economics` is present / usage-metrics is installed). **Checking the box is the estimate trigger** — don't defer it to a later checkpoint.
2. **Phase-end batching is OK; drift-batching is not.** Planned phases (e.g., "finish Phase 2, then log the whole phase at once") are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask. By then a crash or context-trim has lost the state. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.
6. **Estimation provenance (if `## Economics` is present).** This doc's `## Economics` block is the by-hand person-hour estimate, built per the effort-estimation rubric at `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (owned by the `usage-metrics` skill). To **add or refresh** an estimate on resume — even without loading the task skill — read that rubric first for the anchors, personas, and JSON schema; the block also carries a `method_ref` naming it. Skip silently if `usage-metrics` isn't installed. Point to the rubric, never copy it into this doc.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

Refresh the `assets/client-pdlc/` composite client deck so it reflects the ~189 commits of project improvements since its June 12 build (task ben/070 era) — new console sections, new capabilities, and fresh screen captures.

User-confirmed scope (2026-07-16):
- Content source: **`project-overview.md` only** — it carries the console sections, screenshots, and project capabilities; `articles/agentic-delivery-whitepaper.md` stays as-is.
- Curation: **auto-map** — remap the existing `picks.json` keeps to the rebuilt project-overview deck by title match, slot new-section slides in sensible positions, then the user reviews the result.
- PDF: **regenerate** `GlobalLogic_Agentic_PDLC.pdf` from the updated composite.

Pipeline (per md-deck SKILL.md + client-pdlc README):
`project-overview.md` → `python .claude/skills/md-deck/scripts/build.py project-overview.md` → `assets/project-overview/index.html` → `assets/client-pdlc/build.py --candidate/--final` (picks.json = source of truth) → `index.html` → `frontend-slides/scripts/export-pdf.sh`.

Improvements to fold into `project-overview.md` (from git log 2026-06-12..HEAD):
- Console 1.26→1.40: **Submission** section (Q-Sub/510(k)/PCCP package viewer), **Strategy** topline section, **Gap Analysis** view + advisor drawer, **Metrics / Value & ROI** (usage economics), **Setup** rebuilt as full settings surface (Connectors/Skills/Agents/Plugins/Automation/Registries/Environment/Project/Team & Security incl. roster editing + GitHub access audit), Red Team agent group, responsive topnav.
- DHF depth: PP3500 **risk file backfill** (16-hazard HA + dFMEA + pFMEA) + risk layer wired into the trace matrix (ben/102); SRS build-out; reference-registry extension incl. QMSR 21 CFR 820 (ben/105).
- Program tooling: usage-metrics value/ROI story (ben/096–100), submissions skill (Q-Sub/510(k) profiles), regulatory-authoring + red-team + writing-well skills, GitHub-direct registries.

## Todos

_Actionable work items. Check off as completed._

- [x] Capture fresh console screenshots (console on :8765; new sections: Submission, Strategy, Gap Analysis, Metrics/Value & ROI, Setup, plus refreshed Landing/Agents/Documents/Trace-matrix) → `assets/project-overview/console-*.png`
- [x] Update `project-overview.md` — refreshed §1.3 (+risk file), §2.2 (capture hooks retired → real-time rules; +checkpoint recovery, file-locator, usage telemetry), §2.3 (15→35 skills, new table incl. submissions/gap-analysis/red-team/usage-metrics), §2.4 (23→31 advisors + 49 total, Red Team table), §3.2 (current hook set), §3.3 (+contract-grounding, regulatory-authoring, AI-provenance rules), §3.4 (7 properties), §5 full rewrite (11 sections, 15 screenshots), appendix links
- [x] Rebuild `assets/project-overview/index.html` via md-deck build.py — 59 slides (was 52); no image slides by design (screenshots enter via client-pdlc build.py gallery)
- [x] Auto-map `assets/client-pdlc/picks.json`: old→new index map ({0..15}→same, 16→17, {17..50}→+1, 51→58), +N16 (skills mosaic 3/3) added keep:true, N52–57 console text slides left keep:false (gallery covers them); build.py CHAPTERS anchors 21→22/30→31/43→44, SLIDE_APPENDS 51→58, §7 subsections 6→11 gallery slides; 11 fresh screenshots copied to client-pdlc names
- [x] `build.py --final` → new `assets/client-pdlc/index.html` (47 slides, 308KB); browser-verified: agenda 11-item §7 sub-list, Value & ROI + skills-3/3 slides render clean — pending user review
- [x] Regenerate `GlobalLogic_Agentic_PDLC.pdf` — via `client-pdlc/build.py --pdf` (Chrome headless; NOT frontend-slides — that script doesn't exist locally); 8.5MB, pages 36–44 visually verified (all 11 gallery slides crisp)
- [x] Update client-pdlc README (99→106 counts + new Changelog section) + regenerate candidate.html (106 slides, SELECT mode); task doc current
- [x] Corrections Phase A — md-deck 0.6.2 bug fixes (head-slide loss, label truncation, comma strip) + SKILL.md/README
- [x] Corrections Phase B — project-overview.md content fixes (Tasks §5.4, provenance, counts, new §3.4/§3.5, Ct* escapes)
- [x] Corrections Phase C — Tasks screenshots (PO + client copies); landing recapture verified unnecessary
- [x] Corrections Phase D — PO deck rebuild (67 slides) + picks remap/re-curation + build.py anchors/gallery (57-slide composite)
- [x] Corrections Phase E — styling package (leak scrub, WCAG token lift, unclamp, wayfinding, captions) + candidate + PDF (10.3MB)
- [ ] `/sync-skills push` the md-deck 0.6.2 fix upstream — **BLOCKED on user decision**: preflight shows `skills/md-deck/{SKILL.md,scripts/build.py}` are UPSTREAM_NEWER (registry evolved past our baseline; our 0.6.2 fix diverges from it). Per the push contract, do NOT push over it. Recommended path: `/sync-skills pull` md-deck to see the upstream delta, re-apply the 0.6.2 fixes (`--contN` slugs in `_split_dense_slide`, `_split_label_sub`, comma in bold-lead regexes, README) on top of the upstream version, then push. README.md is LOCAL_ONLY (safe to push).
- [x] Gap assessment (2026-07-20): 4 advisory agents launched — (1) skills-framework coverage vs `project-overview.md`, (2) console 1.40→1.41 feature/screenshot drift, (3) narrative completeness + curation, (4) styling/design critique of `assets/client-pdlc/index.html` (frontend-design lens, recommendations expressible as build.py changes). Synthesize findings into recommendations here when they return.
- [ ] User review of the new deck (`assets/client-pdlc/index.html`), then push per git-workflow

<!-- LESSONS LEARNED: verification -->
**Lesson — verify PDF deliverables in the audience's viewer, not just one renderer (2026-07-21).** A Chrome-printed PDF passed page-by-page verification via a poppler-based extractor, yet showed giant translucent orange slabs in macOS Preview: big-blur `box-shadow` glows print as shadow groups that some viewers rasterize as hard-edged rectangles over neighboring content. Poppler renders them softly — so a single-renderer check can pass while the client-facing deliverable is broken. Generalizations: (1) print CSS should strip box/text-shadows (paper needs no glow; borders/backgrounds carry the design) and pin the `@page` box to the authored viewport in inches; (2) any visual deliverable check must use the tool the audience uses — screenshot-based export (frontend-slides `export-pdf.sh`) is immune by construction. Encoded permanently: md-deck 0.6.3 injects `PRINT_HARDENING_CSS` into every generated deck + SKILL.md "PDF export caveats"; the client-pdlc composite's FINAL_CSS carries the same block.

<!-- LESSONS LEARNED: generation-pipelines -->
**Lesson — a "(cont.)" slide with no head slide is a silent-data-loss tell (2026-07-20).** The md-deck deck shipped for weeks with the methodology's headline sections (task-first gate, never-fabricate, 6 of 7 summary properties) missing from every build: density-split continuation parts shared the head part's slug, and the slug-keyed section/picks machinery let the last part overwrite the head — so only orphaned "(cont.)" fragments rendered, twice. Nobody noticed because each slide *individually* looked plausible. Two generalizations: (1) after any generated-artifact build, verify the output inventory against the source section inventory (a title appearing only with a "(cont.)"/"page 2" suffix means its head is gone); (2) when a pipeline splits an item into parts *after* identity minting, every part needs a unique identity — a dict-copy split that inherits the parent's key will silently collapse in any downstream keyed structure. Found by the gap-assessment narrative agent; fixed as md-deck 0.6.2.

<!-- LESSONS LEARNED: grounding -->
**Lesson — the composite deck's screenshots never pass through md-deck (2026-07-16).** Intuition said "refresh the source deck and the screenshots follow." Wrong: md-deck drops the `[![img]](url)` blocks in project-overview.md (they're image+text subsections, not single-image blocks), so neither the 52-slide nor the 59-slide project-overview deck contains a single screenshot. The console screenshots in the client deck are **generated by `client-pdlc/build.py` itself** from `CHAPTERS[-1]["subsections"]` using client-pdlc-local PNG copies. Refreshing deck screenshots therefore means: recapture → copy into `assets/client-pdlc/` under the gallery names → extend `subsections[]` — the source-deck rebuild is only needed for *text* content. Reading build.py before planning (per the ground-in-contracts rule) is what surfaced this; an output-inspection plan would have refreshed `assets/project-overview/*.png` and changed nothing in the client deck.

## Gap Assessment Findings (2026-07-20, advisory agents)

### Agent 1/4 — Console coverage (returned)

Baseline: deck refreshed 07-16 @ console 1.40.0; console now **1.41.0** (only release since: Tasks tab, live in this project since `tasks/task-summary.json` exists + fresh). Nav position: between Documents and Metrics (`_base.html` L54). Landing tiles unaffected — staleness confined to topnav.

- **F1 (High)** `project-overview.md` §5 L363 says "eleven sections" → now **twelve** (add "task activity" to enumeration).
- **F2 (High)** §5.1 L372 nav list missing **Tasks** between Documents and Metrics.
- **F3 (High)** §5 has no Tasks subsection → add §5.x "Tasks — activity summary" (activity summary NOT a task list; rollup stats, narrative + watch, Open-now cards, shipped timeline, effort footnote → Value & ROI, freshness badge, `/task summary` regen hint). Also add `http://127.0.0.1:8765/tasks` row to Appendix quick-links (L511–521).
- **F4 (High)** `build.py` `CHAPTERS[-1]["subsections"]` = 11 gallery slides, no Tasks → add `{"num":"12","title":"Tasks","image":"console-tasks.png"}`, rebuild HTML + PDF. Agenda card auto-updates.
- **F5 (Med)** Recapture `console-landing.png` (+ PO twin `console-01-landing.png`) — topnav now shows Tasks. Other 10 shots: nav one item short, acceptable (F6 Low).
- **F7 (Med, process)** If project-overview.md gains the Tasks subsection, PO deck grows past 59 slides → indices shift → must remap `picks.json` + bump `SLIDE_APPENDS` key (idx 58) in the SAME coordinated pass.
- **F8 (Info)** Setup counts (35 skills / 49 agents etc.) not re-verified; spot-check at recapture.
- Screenshots: ADD `console-tasks.png` (client-pdlc) + `console-18-tasks.png` (project-overview) of `http://127.0.0.1:8765/tasks` @1440×900; RECAPTURE landing pair. Precondition: restart console so 1.41.0 serves.

### Agent 2/4 — Skills-framework coverage (returned)

Ground truth verified: 35 skills (only task v34 + project-console 1.41.0 changed since the 07-16 build), 29 `.claude/agents/` files, 31 console advisors, 49 skill-bundled agents, 12 hooks, 12 rules. Most counts in the doc **survived** (F8-class: 35/49/31/12 all still accurate).

- **S1 (High)** Same as F1–F4: console Tasks tab missing from §5 + deck console slide ("eleven sections", topnav roster, no subsection).
- **S2 (High)** §2.3 `task` skill row says "create / find / update / checkpoint" → v34 added **`summary`** (derives the console Tasks-tab JSON). Extend the row — S1+S2 are one storyline (task summary feeds console Tasks view).
- **S3 (Med)** §2.3 registry provenance is **factually wrong**: says "31 from hitachi + 4 anthropic" → actual is **30 hitachi + 4 anthropic + 1 pinned community registry** (`community-zarazhangrui`, pull-only, pinned SHA, supplies `frontend-slides`). Corrected version is a better supply-chain talking point.
- **S4 (Med)** Header "Last updated: 2026-07-16" → bump on regeneration.
- **S5 (Low/Med)** §3.3 lists 8 of 12 rules; missing highlights worth adding: `articles-not-canonical` (ironic omission — the deck itself derives from articles/) and `git-workflow` (PR-then-auto-merge audit trail). Reframe as "twelve auto-loaded rules, highlights below".
- **S6 (Low)** §3.2 hooks table shows 10 of 12 (omits session-env, skill-creator-cleanup); add "12 registered hooks; highlights:" lead-in so it matches §5.10's count.
- **S7 (Low)** §2.1 structure tree omits `articles/` and `.claude/rules/`.

### Agent 3/4 — Narrative completeness & curation (returned)

**Headline — N1 (HIGH, source defect, not curation):** the md-deck build of `project-overview.md` appears to have **dropped the first page of every paginated multi-bullet section**. Evidence: PO slides #11/#12 ("Operating rules (cont.)") are identical and carry only the last 3 of 9 bullets; #27/#28 ("Rules (cont.)") carry 2 of 8 rules; #29/#30 ("What this adds up to (cont.)") carry only property 7 of 7. Consequence: task-first gate, one-task-one-file, never-fabricate/[VERIFY], contract-grounding, checkpoint recovery, regulatory-authoring standard, and 6 of 7 "adds up to" properties exist in the .md but in **zero slides** — and the client deck kept the orphaned "(cont.)" fragments. No picks.json edit can fix this; needs an md-deck rebuild + index remap. **Verify against md-deck SKILL.md before fixing (ground-in-contracts).**

- **N2 (High)** Ch 05 "Quality & Process" — the differentiation chapter — is 3 slides, one broken. After N1: reinstate rules slide, skills-playbook slide (PO #24), full seven-properties slide.
- **N3 (High)** Until N1 lands, flip PO #30 (and possibly #12) to `keep:false` — a visibly broken "(cont.)"-only slide is worse than absence.
- **N4 (Med)** Lessons loop un-narrated — harvest→stage→promote with ~46 staged ledger entries as evidence; add one slide.
- **N5 (Med)** Regulated-authoring pipeline (lint → copy-edit → QA → independent reference-audit) absent as a story; add one slide.
- **N6 (Med)** Git PR-audit-trail posture missing from `project-overview.md` §3 itself (can't reach the deck until added to source).
- **N7 (Med)** Ch 03 divider promises "deliverables shape" but Key-deliverables slides (PO #7/#8) are both dropped — reinstate #8 or trim the divider lead.
- **N8 (Med)** All operational proof-point slides (AD #19–22, anonymized, client-safe) dropped — deck asserts trust with no evidence slide; reinstate AD #19.
- **N9 (Med)** Value/ROI story is screenshot-only (build.py renders gallery slides with no explanatory body); add a narrative ROI slide with the "modeled, uncalibrated" caveat verbatim.
- **N10 (Low)** AD #13 rewrite overstates Part 11 ("encoded into rules" → actually the change-control publish flow); soften to "Part 11-aware publishing flow".
- **N11 (Low)** Suppress "(cont.)" suffixes in client-facing titles; PO #12 too jargon-heavy to stand alone.
- Curation judged good: dropping GL-internal margin math, language scrub, sp6500 retirement — no action.

**N1 verified by orchestrator (2026-07-20):** manifest.json confirms slides 11/12, 27/28, 29/30 are all `card-grid` "(cont.)" slides with NO head slide; source md §2.2 (9 bullets) / §3.3 / §3.4 are intact. md-deck `scripts/build.py` `_split_dense_slide` (~L2245, card-grid limit 6) correctly keeps the original title on chunk 0 — so the head part is being lost downstream, likely in the density-split × variant-emission interaction (each section emits 2 variants; only the (cont.) part survives, twice). **This is an md-deck skill bug** → fix routes through skill-creator (registry-shared skill) + sync-skills push, then rebuild PO deck + client remap.

### Agent 4/4 — Styling & layout (returned)

Method: frontend-design skill loaded; full CSS/JS read + Chrome render at 1400×900 with 12 screenshots + DOM probes. Verdict: design system is strong (coherent tokens, good bookends, excellent bespoke diagrams); problems concentrate in content defects carried from the PO source deck, top-heavy PO-sourced layouts, and weak wayfinding. All fixes expressible in `assets/client-pdlc/build.py`.

**Three worst offenders:**
- **D1 (High)** Slide 17 (Reg strategy at a glance): markdown-escape leaks (`Ct\<em>-tagged`, stray `*`), a card body starting mid-sentence (", classified as Class II SaMD accessory…"), line-clamp "…" truncation whose full text lives only in a hover overlay (dead in PDF), raw repo paths visible to client. Fix via `SLIDE_PATCHES` (build.py L1038) or upstream in the PO deck.
- **D2 (High)** Slide 33: sixth tile ends mid-sentence — "…whose compliance properties are " (truncated IN the source markup, PO idx 43 — verify at fix time whether this is the same md-deck bug family). Patch the ending + optionally fill empty p-subs.
- **D3 (Med-High)** Slides 20–24 (Skills ×3 / Agents ×2 mosaic run): 12.6–13.6px card text, ~40% dead bottom space, near-universal mid-sentence ellipsis, one card leaks raw `<!-- STRATEGY CONTENT: domain -->` syntax. Fix: unclamp + min-height CSS scoped to `.src-project-overview`, plus optionally collapse to 2 authored slides.

**Systemic:** T1 micro-type below projection floor (11–12px chrome/eyebrows → raise clamp minima); C1 `--text-muted #6b6b7d` on `#0e0e10` ≈ 3.7:1, fails WCAG AA → `#8a8a99` single-token fix; L1 PO-sourced slides top-heavy (30–45% dead bottom) vs frame-filling AD slides → scoped grid flex/min-height overrides (FINAL_FIT_JS is safety net); G1 11 consecutive caption-less screenshot slides → add `caption` field to CHAPTERS §7 + one-line takeaway strip (high value); N1/N2 no progress bar, no chapter crumb, bare "34" counter → wayfinding package (~30 lines); N3 keyboard/scroll desync (2-line fix); P2 Google Fonts is a hard network dep at PDF export (silent Helvetica fallback offline) → self-host base64 woff2 subsets (~150–250KB); L2 Hooks table densest+jargon-heavy (drop `.sh` filenames); L3 agenda card 07 lopsided; L4 closing eyebrow duplicates H1.

**Styling shortlist (agent's priority):** 1) SLIDE_PATCHES defect scrub, 2) token floor lift (contrast + minima), 3) unclamp/de-hover + fill frame, 4) wayfinding package, 5) gallery captions, 6) self-hosted fonts, 7) optional mosaic-collapse restructure.

### Synthesis — recommended change plan (all four agents)

Cross-agent convergence: Tasks tab gap (agents 1+2+3), md-deck head-slide bug (agent 3, orchestrator-verified; likely also behind D2 truncation + several D1 leaks), screenshot recapture set (agents 1+3). Ordering is driven by the dependency chain: **md-deck fix must precede the PO rebuild, which must precede the picks remap.**

- **Phase A — Fix md-deck (upstream skill bug).** Debug `_split_dense_slide` × variant-emission interaction losing head slides of over-limit card-grids (also check D2's truncated sentence + D1's markdown-escape rendering while in there). Registry-shared skill → route via skill-creator, push upstream via sync-skills.
- **Phase B — project-overview.md content edits.** Twelve sections + Tasks subsection + appendix row (F1–F3); task row + `summary` (S2); registry provenance 30+4+1 (S3); rules/hooks "12, highlights" + articles-not-canonical + git-workflow (S5, S6, N6); structure tree + articles/ + rules/ (S7); Part 11 softening upstream if the AD #13 rewrite mirrors source (N10); bump Last-updated (S4).
- **Phase C — Screenshots.** Restart console (1.41.0), capture `/tasks` → `console-18-tasks.png` (PO) + `console-tasks.png` (client), recapture landing pair; spot-check Setup counts (F8).
- **Phase D — Rebuild + re-curate.** md-deck rebuild of PO deck (head slides restored, slide count changes) → title-based picks.json remap + `SLIDE_APPENDS` bump (F7-process); curation: restore rules/operating-rules head slides + seven-properties + skills-playbook #24 (N2), reinstate AD #19 proof slide (N8), ch03 divider vs deliverables (N7), new slides: lessons loop (N4), authoring pipeline (N5), ROI narrative w/ caveat (N9); Tasks gallery entry in CHAPTERS (F4).
- **Phase E — Styling in client build.py.** Agent-4 shortlist 1–6 (defect scrub where not already fixed upstream by Phase A/B, token lift, unclamp, wayfinding, gallery captions, self-hosted fonts); then `--final` rebuild + PDF regeneration + visual verify.

Quick wins independent of the chain: token floor lift, wayfinding, gallery captions, closing-slide eyebrow (all Phase E items that don't depend on A–D).

## Open Questions

- `assets/project-overview/index.pdf` is still the June 12 render (the md-deck HTML deck was rebuilt but md-deck has no local PDF exporter — SKILL.md points to a frontend-slides script that isn't installed in this project). Regenerate or drop the PDF reference? User call.
- md-deck v0.6.1 auto-emitted `assets/project-overview/README.md` + `candidates.html` (new build artifacts, committable per its own README) — included in the change set.

## Resume

### In-flight artifacts
**All uncommitted** (nothing committed this session; user controls push). Change set:
- `project-overview.md` — content refresh (§1.3, §2.2–2.4, §3.2–3.4, §5 full rewrite w/ 11 console sections, appendix)
- `assets/project-overview/` — index.html (59 slides) + manifest.json rebuilt; 9 screenshots refreshed + 7 new (console-11..17); NEW md-deck artifacts README.md + candidates.html; index.pdf STALE (see Open Questions)
- `assets/client-pdlc/` — build.py (anchor remap + 11-slide gallery), picks.json (remapped, 106 entries/32 keeps), index.html (47 slides), GlobalLogic_Agentic_PDLC.pdf (8.5MB), candidate.html (106), README.md (counts + changelog), 6 refreshed + 5 new console-*.png
- Also in tree: ben/104 + 000-index task-doc updates (checkpoint recovery, separate concern), SECOPS.md auto-update (pre-existing), and ben/107 console-tasks-tab changes (task skill v34 + project-console 1.41.0, uncommitted, tracked in its own doc) — take care to keep the two change sets in separate commits at push time

### First action on resume
- Activate: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 106`
- Remaining: user deck review → adjustments if any → push per git-workflow (commit → branch → PR → auto-merge). Decide the stale index.pdf question.
- Do NOT redo: screenshots, project-overview.md rewrite, deck builds, picks remap, PDF — all done and verified.

## Economics

_By-hand person-hour estimate, **filled at checkpoint** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated; an empty `todos` list is ignored by the aggregator._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {"min": 1.0, "max": 1.5},
    "todos": [
      {
        "todo": "Console screenshot recapture — 15 live captures (9 refreshed + 6 new sections) at fixed viewport, each verified",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 1, "max": 2},
        "confidence": "high",
        "basis": "judgment — console navigation, consistent viewport/theming, file naming, spot verification"
      },
      {
        "todo": "project-overview.md content refresh — fact-gather across 189 commits (skills 15→35, agents 23→49, hooks, 11 console sections) + rewrite 7 sections with verified live numbers",
        "personas": ["program-manager", "rd-lead"],
        "manual_hours": {"min": 6, "max": 10},
        "confidence": "med",
        "basis": "doc-authoring anchor — the cost driver is re-deriving current-state facts across console/skills/agents/hooks and writing deck-shaped prose"
      },
      {
        "todo": "Composite re-curation: old→new slide-index mapping (59-slide rebuild), picks.json regeneration, build.py anchor/gallery updates (6→11 screenshot slides), final build + PDF + candidate rebuild + README",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 3, "max": 6},
        "confidence": "med",
        "basis": "software anchor — index-remap correctness across three coupled artifacts (picks.json, CHAPTERS, SLIDE_APPENDS) is fiddly by hand; verification via rendered deck"
      },
      {
        "todo": "ben/104 retroactive checkpoint (recovery audit from git, doc refresh, marker cleanup)",
        "personas": ["program-manager"],
        "manual_hours": {"min": 0.5, "max": 1},
        "confidence": "high",
        "basis": "judgment — small audit + doc refresh"
      }
    ]
  }
}
```

## Changelog

- 2026-07-21: **PDF orange-slab root cause found + fixed** (user screenshot showed the callout's glow rendered as a giant translucent rectangle over the cards in Preview — invisible in the poppler-based extraction used for earlier verification, hence the earlier false "verified"). Cause: 80px-blur `box-shadow` glows; some viewers rasterize Chrome's printed shadow groups as hard slabs. Fix: `@media print` strips box-shadow/text-shadow globally (checked: no kept slide relies on ring-shadows). PDF 8.6→7.3MB. LESSON: verifying PDF output with one renderer is insufficient — viewer-dependent constructs (shadow smasks) need checking in the viewer the audience uses.
- 2026-07-21: **PDF/index formatting parity fixed** (user report: orange blocking larger in PDF pages 4/12/34). Root cause: print box was 1400×900 vs authored 1440×900 — px/rem-capped elements stayed the same absolute size on a smaller canvas → proportionally larger. `@page` → 15in×9.375in + export `--window-size=1440,900` in client build.py; PDF regenerated (8.6MB) and pages 4/12/34 verified to match browser proportions exactly (83.3% card-block width parity).
- 2026-07-21: **User deck-review round 2 applied.** Removed AD-19 proof slide + PO-34 lessons-loop slide; merged Operating-rules pair → one custom 9-rule slide; replaced the 6-skill playbooks mosaic with a full 35-skill catalog slide (five grouped columns); merged "What this adds up to" pair → one 7-property slide with takeaway. Deck 54→50; candidate + PDF (8.7MB) regenerated and page-verified (browser slides 20/24/29 + PDF page 24).
- 2026-07-21: **User deck-review round 1 applied.** Five items: (1) AD6 "Cost of waiting" + (2) AD16 "The invariant" callouts centered/width-matched to their card rows via SLIDE_PATCHES inline-style patches (pixel-verified 120..1320; fixed a duplicate `("agentic-delivery", 16)` dict key that silently ate the first patch list); (3) Key deliverables tile slide replaced with an authored pathway-rail illustration (three filings on the evidence backbone); (4) Skills mosaics ×3 → one grouped overview slide (14 skills, AUTHOR/VERIFY/OPERATE); (5) Agents mosaics ×2 → one four-group overview with the slide-27 takeaway (same agents, two runtimes + secops audit) folded in. New `CUSTOM_REPLACES` + `CUSTOM_RENDERERS` mechanism in client build.py. Deck 57→54 slides; candidate + PDF (9.5MB) regenerated; browser + PDF page spot-verified.
- 2026-07-20: **Phases D+E complete** (commits 2eb5c53, 0fb8997 on `ben/106-corrections`). D: PO deck rebuilt 59→67 slides (heads restored, +authoring/lessons/Tasks sections), picks.json remapped by verified title+type mapping + re-curated (9 adds incl. AD-19 proof slide), client build.py anchors 22→23/31→38/44→51, SLIDE_APPENDS 58→66, 12-slide gallery. E: SLIDE_PATCHES leak scrub (zero docs/-paths + marker sigils in final HTML, verified), Part 11 softening, WCAG muted lift, unclamped PO cards, wayfinding (progress bar / n-of-57 counters / chapter crumbs / keyboard-scroll desync fix), 12 gallery captions (ROI caption carries the modeled-uncalibrated caveat), closing eyebrow. Composite 47→57 slides; candidate 114; PDF 10.3MB spot-verified (page 48). Deferred: self-hosted font subsets (P2, offline-PDF hardening). README changelog rows added.
- 2026-07-20: **Phases B+C complete** (commits 6d3e1bd, 3756402 on `ben/106-corrections`). B: all project-overview.md corrections applied — twelve sections + new §5.4 Tasks (renumber →5.13), registry provenance 30+4+1, task row +summary, hooks/rules true counts + 2 new rule highlights (articles-not-canonical, PR audit trail), tree +articles/+rules/, NEW §3.4 authoring pipeline + §3.5 lessons loop ("44 L-ben mentions" verified ≥40), adds-up-to →§3.6, date bump. C: console-18-tasks.png + client console-tasks.png captured (1440×900, console 1.41.0 live, page renders with real data); landing recapture SKIPPED — verified Tasks sits in the overflow menu at 1440px so the existing landing shot is unchanged (gap-assessment F5 overtaken by evidence); §5.1 wording corrected to match.
- 2026-07-20: **Phase A complete** (commit 14f134e on `ben/106-corrections`, branch pushed to origin as backup — NOT merged yet). md-deck 0.6.2: (1) `_split_dense_slide` continuation parts get unique `--contN` slugs — root cause of the head-slide loss was the slug-keyed section/picks machinery overwriting the head part; (2) new `_split_label_sub()` replaces `text[:60]` hard slice (fixes D2 "compliance properties are " truncation). Verified via scratch rebuild to `/tmp` scratchpad (62 slides, all three head slides restored, full sentence renders). SKILL.md contract + new README.md per skill-creator conventions. TODO end-of-task: `/sync-skills push` the md-deck fix upstream.
- 2026-07-20: **Pushed to main.** PR #118 (ben/107 console Tasks tab, commit c64e8a4) and PR #119 (this task: deck refresh + gap-assessment findings, commit 83884d7, merge f0d3e71) both merged per git-workflow; branches deleted; local main synced. Main now holds the full recovery baseline before corrections begin. Corrections proceed per the phased plan (A: md-deck bug → B: project-overview.md edits → C: screenshots → D: rebuild+re-curate → E: styling), each phase on a branch with PR merge as its recovery point.
- 2026-07-20: 4-agent gap assessment complete; findings captured above (Agents 1–4 + synthesis). Key: confirmed md-deck head-slide bug (N1), console 1.41.0 Tasks tab drift, registry-provenance factual error, styling shortlist.
- 2026-07-20: Retroactive checkpoint (session e929e84c ended 13:56Z without one). Audit: no 106 artifacts changed since the 07-16 checkpoint — that session's work was ben/107 (own doc, current). 106 state unchanged: deck + PDF built and verified, all uncommitted, awaiting user review then push. New this session: gap assessment of client-pdlc content vs updated skills/console starting under this task.
- 2026-07-16: Full pipeline executed end-to-end: project-overview.md rewritten (7 sections; §5 now 12 subsections covering all 11 console sections), deck rebuilt 52→59 slides, picks.json auto-remapped (+ Skills 3/3 kept, console text slides 52–57 left out in favor of the gallery), build.py anchors remapped + §7 gallery 6→11 slides, final composite 41→47 slides, PDF regenerated (8.5MB, visually verified), candidate.html rebuilt (106), README counts + changelog updated. Everything uncommitted pending user review. Residual: stale assets/project-overview/index.pdf (no local md-deck PDF exporter — see Open Questions).
- 2026-07-16: Screenshots captured (chrome-devtools MCP, 1440×900, console live at 1.40.0): refreshed console-01..09 (landing, agents, documents, dashboards, submission-tracker, trace-matrix, agent-chat, trace-matrix-detail, overview) + NEW console-11-strategy, console-12-submission, console-13-gap-analysis, console-14-metrics, console-15-value-roi, console-16-setup, console-17-workflows — all in `assets/project-overview/`. Live facts recorded for the doc rewrite: 31 console agents (incl. Red Team group), Setup sidebar (Skills 35 / Agents 49 / Automation 26 / Registries 3), trace-matrix pca-device UN 22 / DI 34 / SW 32 / Arch 7 / VnV 3 / Risk 16 (all 10 DHFs have sidecars), tracker 154 deliverables, Value & ROI 923–3,052 hrs saved across 104 tasks @ $623 agentic cost, Submission 2 filings (Q-Sub drafting + 510(k) scaffold).
- 2026-07-16: Task created — refresh assets/client-pdlc with June→July improvements; scope confirmed with user (project-overview.md only, auto-map curation, regenerate PDF).
