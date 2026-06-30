---
name: red-team
description: "Adversarial buyer-committee critique of a prose document (whitepaper, blog, one-pager, thought-leadership brief, external memo). Fans out a panel of seven audience-skeptic agents — CEO, CFO, CTO, VP-Eng, RA-VP, QA-VP, PMO — each reading as the hostile decision-maker it represents, grounded by a for/against researcher that gathers real counter-evidence before any objection is raised. Returns one synthesized, advisory report grouped by persona: severity, the passage attacked, the counter-evidence behind the doubt, a suggested fix, and a verdict column the human fills in. TRIGGER when the user wants to pressure-test / red-team / stress-test / critique / poke holes in / find the weak points in / 'see if this survives a skeptical room' / 'what would a CFO (or CTO, regulator, exec) say about' a document or argument; also on 'play devil's advocate', 'adversarial review', 'is this argument defensible', 'where will this get attacked'. Advisory only — never edits the document, never blocks. Project-agnostic; works on any nonfiction markdown. NOT for prose quality/rhythm/clutter (that's writing-well / prose-editor), NOT for citation soundness (that's reference-audit), NOT for authoring or publishing a doc (that's public-doc)."
version: 1
updated: 2026-06-26
---

# Red Team

Pressure-test a prose document the way the room it has to survive actually will. Most review surfaces ask *is this well written* (writing-well) or *are the sources real* (reference-audit). This skill asks the harder question: **does the argument survive a hostile, senior reader who has a reason to say no.**

It fans out a **buyer-committee panel** — seven audience-skeptic agents, each impersonating a specific decision-maker — over a target document. Each skeptic grounds itself first (via the `red-team-researcher`, which gathers both supporting and opposing evidence so objections land with real ammunition instead of invented doubt), then reports where *that reader* stops believing. The skill consolidates all seven into one report the human adjudicates finding-by-finding.

The point is not to be negative. The point is to surface every objection *before* the document meets the room, while there's still time to answer it — and to concede the ground that genuinely holds so the real weak points stand out.

## The panel

Seven personas, grouped by how they push back. The roster is fixed and project-agnostic — these are archetypal enterprise decision-makers, not any one company's staff.

| Group | Persona (agent) | Where this reader stops believing |
|---|---|---|
| **Economic** | CEO (`ceo-skeptic`) | Vision asserted without a mechanism; "transformational" with no proof; upside named, downside hidden; trend-chasing |
| | CFO (`cfo-skeptic`) | Benefit with no number; number with no baseline/method/source; cost (build + ongoing + hidden) omitted; soft "productivity" |
| **Technical** | CTO (`cto-skeptic`) | Outcomes described, mechanism never; no failure modes or limitations; scale/integration/lock-in/security hand-waved; hype words |
| | VP Eng (`vp-eng-skeptic`) | Adoption assumed costless; "just adopt X"; no migration path; ignores the existing org, codebase, and day-2 reality |
| **Compliance** | RA VP (`ra-vp-skeptic`) | Claims a regulator would challenge; implies controls bypassed or human accountability reduced; unsubstantiated compliance language |
| | QA VP (`qa-vp-skeptic`) | Speed/automation claimed without a control or validation story; quality asserted not shown; non-determinism with no reproducibility story |
| **Governance** | PMO (`pmo-skeptic`) | Productivity multiplier with no plan; estimate with no basis; coordination/governance cost ignored; doesn't survive a real schedule |

The full charter for each lives in its agent file under `agents/`.

## Supporting Files

| File | Purpose |
|------|---------|
| `README.md` | Design document — architecture, lineage, dependencies, Best Practices, Changelog |
| `agents/red-team-researcher.md` | For/against grounding researcher. Discovers whatever grounding exists for the target doc (no assumed files), extracts load-bearing claims, gathers supporting AND opposing evidence (internal first, web fallback). Returns a dossier — no persona voice, no verdicts. |
| `agents/ceo-skeptic.md` | Economic buyer — strategic bet |
| `agents/cfo-skeptic.md` | Economic buyer — the money |
| `agents/cto-skeptic.md` | Technical buyer — how it actually works |
| `agents/vp-eng-skeptic.md` | Technical buyer — execution reality |
| `agents/ra-vp-skeptic.md` | Compliance buyer — regulatory defensibility |
| `agents/qa-vp-skeptic.md` | Compliance buyer — quality-system integrity |
| `agents/pmo-skeptic.md` | Governance buyer — delivery & portfolio |
| `templates/red-team-report.md` | Output scaffold for the consolidated report |

## Subagent Delegation

| Scenario | Agent Type | Prompt |
|----------|-----------|--------|
| Critique the doc through one persona's eyes | `<persona>-skeptic` | The `run` action dispatches each skeptic with the doc path + discovered grounding inputs; each returns `findings[]` |
| Gather for/against evidence for a persona's claims | `red-team-researcher` | Invoked by each skeptic itself, not by the skill — the skeptic passes its lens and gets back a dossier |

The researcher is dispatched by the skeptics (mirroring how `citations` dispatches its researchers), not by this skill directly. The skill's job is discovery + fan-out + consolidation.

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform.

### `setup`

Wire the bundled agents into `.claude/agents/` so the Agent tool can discover them. Idempotent — safe to re-run. This skill ships **agents only** — no hooks, no rules.

1. Create `.claude/agents/` if it does not exist.
2. For each agent file in `agents/` (the skill's `agents/` is the source of truth), create symlink `.claude/agents/<agent-name>.md` → `../skills/red-team/agents/<agent-name>.md`:
   - If the symlink already exists and points at the correct target: skip.
   - If it exists but points elsewhere: replace.
   - If a regular file exists at the symlink path (project fork): leave it alone — `/sync-skills` detects forks intentionally.
3. Report what was wired vs already present vs left as a fork.

The eight agents installed: `red-team-researcher`, `ceo-skeptic`, `cfo-skeptic`, `cto-skeptic`, `vp-eng-skeptic`, `ra-vp-skeptic`, `qa-vp-skeptic`, `pmo-skeptic`.

### `run <doc-path> [--personas a,b,c] [--refresh]`

Run the panel over a document and write the consolidated report. This is the main action.

1. **Validate** — confirm `<doc-path>` exists and is a readable text/markdown prose document. If it's a slide deck, code file, or binary, stop and say so (this skill critiques prose arguments, not slides — point the user at the right tool).
2. **Compute doc-slug** — kebab-case basename without extension (e.g., `agentic-pdlc-whitepaper`).
3. **Resolve the report path** — `<doc-dir>/<doc-slug>.red-team.md`, a sibling of the source so it's co-located and discoverable. (A single sibling file, not a new folder — no folder-README ceremony.)
   - If that file exists and `--refresh` was **not** passed: **stop**. Report "a red-team report already exists at <path>; it may hold your verdicts. Re-run with `--refresh` to overwrite, or move/delete it to start clean." Never silently clobber — the Verdict column is the user's adjudication and must not be lost.
4. **Discovery pass (shared grounding map)** — before fanning out, inventory what grounding the panel can stand on, so the seven researchers don't each re-discover it. **Assume no specific file exists.** Look, in order, for:
   - The document's **own inline references** — markdown links, cited paths, footnotes, "see X" pointers inside the doc.
   - **Sibling supporting material** — glob the doc's directory and immediate subdirectories for things like `research/`, `references*`, `claims*`, `sources*`, `evidence*`, `*-register*`, `appendix*`, `data/` (patterns, not required names — match what's actually there).
   - **Related project docs** — a project README in the doc's folder, a parent index, anything the doc clearly derives from.

   Emit a `grounding_inputs[]` list of `{ path, why_relevant }`. An empty list is a valid result — it tells the panel to ground web-only. Do **not** fabricate paths; list only what you confirmed exists.
5. **Select personas** — default to all seven. If `--personas` was passed, run only that subset (accept short names: `ceo,cfo,cto,vp-eng,ra-vp,qa-vp,pmo`).
6. **Fan out** — invoke each selected skeptic agent **in parallel** (emit all Agent tool calls in a single message). Pass each: the `doc_path`, the `grounding_inputs[]` map, and the instruction to ground itself via `red-team-researcher` before critiquing. Each returns a `findings[]` list per the shared contract below.
7. **Consolidate** — read `templates/red-team-report.md` and assemble one report:
   - A short **grounding-discovered** note so the reader sees what evidence base the panel had (and where it had none — an all-web critique is weaker, and the report should say so).
   - Findings **grouped by persona group → persona**, each rendered as a table row: severity · the passage · the objection (in the persona's voice) · counter-evidence · suggested fix · **Verdict** (left blank for the human: agree / disagree / defer).
   - A **summary** count by severity and persona, and a short **"strongest objections"** call-out — the 3–5 findings the panel was most confident and most evidenced on.
8. **Write** the report to the resolved path. **Never modify the source document.**
9. **Report back** — the path, the summary counts, and the strongest-objection call-out, so the user can start adjudicating immediately.

### `help`

Show the action list, the panel roster, and a one-line example (`/red-team run blogs/agentic-pdlc/agentic-pdlc-whitepaper.md`).

## Shared findings contract

Every skeptic returns a `findings[]` list in this shape. The consolidation step depends on these field names.

```yaml
findings:
  - id: cfo-1                      # <persona-short>-<n>
    persona: CFO
    severity: blocker | major | minor
    passage: "<short quoted span, or section heading + anchor, the objection targets>"
    objection: "<where this reader stops believing — in the persona's own voice, one or two sentences>"
    counter_evidence:
      - stance: against | for      # 'for' entries = ground the persona concedes is solid
        source: "<repo path or URL, or 'persona judgment' if unevidenced>"
        excerpt: "<the supporting/opposing detail>"
    suggested_fix: "<one sentence — what would make this objection go away>"
    confidence: evidenced | intuition   # evidenced = backed by the researcher dossier; intuition = persona instinct, no external evidence found
```

- **`severity`** — `blocker`: a senior reader would reject the document's core claim over this. `major`: would significantly erode trust or invite a hard challenge. `minor`: a nitpick that still weakens the case.
- **`confidence`** — the honesty valve against invented objections. `evidenced` findings cite the researcher's dossier; `intuition` findings are flagged as the persona's instinct so the human weighs them accordingly. A skeptic that can't find evidence should mark `intuition`, not dress a guess up as fact.
- **Concede the solid ground.** A panel that only attacks reads as noise. Each persona should include at least the strongest `for` evidence it found — what genuinely holds — so the real weak points are legible.

## Notes

- **Advisory, never blocking, never editing.** The skill writes one report and stops. It does not touch the source document, and it does not gate any pipeline. The human decides what to act on via the Verdict column.
- **Project-agnostic.** No hardcoded paths, no project names. Grounding is *discovered* per document (step 4), never assumed — a doc with a rich `research/` kit and a doc with nothing both work; the second just grounds web-only and the report says so.
- **Distinct from its neighbors.** writing-well / prose-editor judge *how it reads*; reference-audit verifies *whether sources resolve*; public-doc *authors and ships* the doc. This skill attacks *whether the argument holds*. Run it after the prose is clean and before the doc meets the room.
- **The personas are buyers, not the project's own advisors.** A medtech project may also have `regulatory-affairs` / `quality-engineering` advisors grounded in its DHF — those give *project* advice. The RA-VP / QA-VP skeptics here react to *external content* as hostile readers. Different job; do not substitute one for the other.
- If `$ARGUMENTS` is empty or just "help", show the usage guide.
