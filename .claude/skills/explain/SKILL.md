---
name: explain
description: |
  Answer a question about the project as a self-contained, visualization-rich HTML
  document (tables, diagrams, badges, timelines) saved to the user's personal scratch
  folder, then print a clickable link to open it. Built for onboarding — helps both
  technical and non-technical people get oriented in an AI-driven project.

  ONLY trigger on an explicit slash-command invocation: `/explain <question>` (or
  `/explain --simple <question>`, `/explain list`, `/explain help`).

  Do NOT trigger on ordinary questions asked in conversation — even questions about
  the project, its structure, status, history, or content. Those are answered normally
  in chat. The HTML document is wanted ONLY when the user explicitly typed `/explain`.
  No exceptions: if the user did not type `/explain`, this skill is not what they want.
version: 3
updated: 2026-06-03
---

# Explain

Turn a question about the project into a **self-contained, visual HTML document** the user can open, read, keep, and share — then hand them a clickable link.

The skill's job is to **aggregate and visualize**, not to search or to be a domain expert. Searching and domain knowledge come from whatever the project already provides (specialized skills, expert agents, search tools); this skill discovers and uses them at runtime, and falls back to built-in file tools when the project provides nothing. Think of it as the presentation layer on top of the project's existing knowledge.

## When this runs

Only on an explicit `/explain` invocation. The skill deliberately does **not** fire on ordinary project questions in conversation — that prevents surprise HTML generation mid-chat and keeps the skill out of the way until the user actually wants a document. If you are reading this because a user asked a project question *without* typing `/explain`, answer them normally in chat instead.

## Supporting Files

| File | Purpose |
|------|---------|
| `README.md` | Design document — rationale, decisions, lineage (not loaded at runtime) |
| `templates/explainer.html` | The generic HTML template — design system (canonical CSS) + a lean set of core/common component blocks |
| `references/visuals/` | Gallery of richer, fit-for-purpose visuals (11 SVG diagrams + 8 CSS components), one self-contained file each. Read only the file(s) you pick. |
| `references/visuals/README.md` | Thin catalog of the gallery files. Choose visuals from the selection table in this SKILL.md (§ Render), not from here. |
| `evals/evals.json` | Functional + trigger test cases (used by `/skill-creator`) |

## Actions

Parse the user's argument string `$ARGUMENTS`:

- empty or `help` → show the usage guide (see **Usage** below) and stop.
- `list` → run the **list** action.
- anything else → run the **explain** action (the default). A leading `--simple` flag selects the simplified-audience variant; the rest of the string is the question.

### explain (default) — `/explain [--simple] <question>`

Produce one HTML document answering `<question>`, then deliver a short chat reply with a link. Work through the six steps in order.

#### 1. Resolve the output location

Decide where the file goes. Output always lands in a personal scratch folder so it stays local, private, and exempt from the task gate (writes under `tasks/` need no active task).

1. If the project has a manifest (`project.yml`) with a team roster: read `git config user.email`, match it against `team.active[].email`, and use that member's `task_folder`. Output dir = `tasks/{task_folder}/_scratch/explain/`.
2. If there is no manifest, no roster, or no email match: ask the user **once** for a short folder name, then use `tasks/{name}/_scratch/explain/`. (Keep the skill usable in projects that don't follow this toolkit's conventions.)
3. `mkdir -p` the output dir if it doesn't exist.
4. If the invocation explicitly passes an output-path override (used by automated test runs), use that path instead of the above.

#### 2. Classify the question

Identify the kind of question — it drives which visuals fit:

| Kind | Example shape | Visuals that usually fit |
|------|---------------|--------------------------|
| structural | "how is X organized?", "what lives where?" | folder/inventory tables, relationship diagrams |
| process | "how do I do X here?", "what's the workflow for Y?" | numbered phase timeline, flow diagram |
| status | "what's the current state of X?" | summary table, badges, callouts |
| conceptual | "what is X and why does it exist?" | definition cards, diagram, comparison table |

Also pick the **audience level**: `--simple` forces jargon-free output; otherwise assume a technical reader, but lean simpler if the user's own tone and vocabulary in this conversation suggest a non-technical reader. The document's two-layer structure (plain summary first, details after) serves both regardless.

#### 3. Ground the answer

Never answer from memory alone — gather evidence from the project. The skill is an aggregator: prefer the project's own knowledge tools over doing the research yourself.

1. **Survey what the project provides.** Look at the available skills, the available agents, and any search tools (e.g. a file-locator MCP). Each component's own description states when it should be used — that description is the contract.
2. **Use a provided component when its stated trigger conditions match the question.** A semantic-search tool for finding relevant files; an expert agent for a question squarely in its declared domain. Respect that component's own usage rules, and collect its findings as input. Delegate the *research*; you still do the *aggregation and rendering*.
3. **Always read the project's orientation files when present**, regardless of step 2: the project instructions file (e.g. `CLAUDE.md`), the project manifest (`project.yml`), the glossary, and the `README.md` files along the relevant folder paths. These are how a documentation tree describes itself.
4. **Fall back to built-in tools** — Glob, Grep, Read, and walking the docs tree — when no specialized component matches, or to fill gaps the components left.

Record every file you read and every component you consulted. This is the raw material for the source citations and the provenance footer.

#### 4. Synthesize before rendering

Structure the answer first, then render. Aim for a document that rewards reading top-to-bottom:

- **Plain-language summary** — 3–5 sentences, no jargon, always the first content block. A non-technical reader should understand the gist from this alone.
- **Detailed sections** — each with the visual that fits its content (table, diagram, timeline, badges, callout). **Pick the 1–3 visuals that genuinely clarify the answer — not one of each.** Prefer a clean table or plain prose when a diagram wouldn't add understanding; never add a visual just because it is available. Match the visual to the shape of the content (a process → a flow or timeline; a comparison → a comparison table or A↔B mapping; a structure → a tree or layered diagram; figures → stat tiles). Don't dump raw data — summarize large sets into tables.
- **Source citations** — attach evidence to claims, but keep it readable: **one collapsible citation per logical block**, not per sentence. A logical block is a table, a wordy table row, a paragraph, or a connected run of paragraphs a single source explains. See the citation widget in the template.
- **Related topics** — a short closing list of adjacent topics the document touched but didn't fully cover. Plain text, not suggested commands.

#### 5. Render the HTML

Fill `templates/explainer.html` with the synthesized content. The template carries the canonical CSS plus a lean set of core/common blocks. For any richer visual, pull it from the gallery.

**Choosing visuals from the gallery (`references/visuals/`):**

1. From the table below, pick the file(s) for the 1–3 visuals you decided on in step 4. Don't read the whole gallery — read only the file(s) you pick (read `references/visuals/README.md` if you need the fuller index).
2. In each chosen file, copy **only** the markup between `<!-- BEGIN SNIPPET -->` and `<!-- END SNIPPET -->` into the document. Ignore that file's `<head>`/`<style>` — it is preview-only; the styling comes from the template's CSS, which already covers every gallery snippet.
3. Replace the snippet's `{{placeholders}}` with real content.

| When to use | Visual | File |
|-------------|--------|------|
| Parts of a system stacked in horizontal layers; what the layers are and what depends on what | layered architecture | `diagram-layered-architecture.html` |
| A straight-through process / pipeline — A → B → C, no branching | linear flow | `diagram-linear-flow.html` |
| An iterative process — steps run, then loop back to repeat until an exit condition | feedback loop | `diagram-feedback-loop.html` |
| A test with two or more outcomes ("if X then Y, else Z") | decision flow | `diagram-decision-flow.html` |
| Something moves between named states via labeled transitions (e.g. Not Started → In Progress → Complete) | lifecycle | `diagram-lifecycle.html` |
| Two or three actors exchange messages over time (a protocol / handshake), optionally across a boundary | sequence / handshake | `diagram-sequence-handshake.html` |
| Several independent inputs feed into one combined output / artifact | convergence / fan-in | `diagram-convergence-fanin.html` |
| A parent-and-children hierarchy — folder trees, module/org breakdowns, "X contains Y and Z" | tree / hierarchy | `diagram-tree-hierarchy.html` |
| Map one set against another — A-side ↔ B-side (before/after, this-vs-that, source ↔ target) | comparison / mapping | `diagram-comparison-mapping.html` |
| Position items along two axes — e.g. impact vs effort, likelihood vs severity | 2×2 matrix | `diagram-matrix-quadrant.html` |
| Who does what across stages — rows are actors, columns are stages | swimlane | `diagram-swimlane.html` |
| Explain a colour/category scheme — a key with a short description per category | legend cards | `component-legend-cards.html` |
| Headline numbers at a glance — counts, totals, key figures (keep to 3–5) | stat tiles | `component-stat-tiles.html` |
| Compare options/features in a grid where each cell is has-it / doesn't / partial | comparison table (✓/✗) | `component-comparison-table.html` |
| Show completion / readiness / proportion per item | progress bars | `component-progress-bars.html` |
| A compact "facts at a glance" panel — label → value pairs | spec-sheet panel | `component-spec-sheet.html` |
| Contrast two lists — do/don't, pros/cons, recommended/avoid | do / don't | `component-do-dont.html` |
| Dated milestones along time (left→right) — for unordered steps use the vertical phase timeline instead | horizontal timeline | `component-horizontal-timeline.html` |
| Spotlight one key statement — a definition, principle, or line worth emphasis; use sparingly | pull-quote | `component-pull-quote.html` |

- **Self-contained**: inline CSS, inline SVG, no external scripts/stylesheets/fonts/CDNs. The file must open offline in any browser, now and years from now. (Gallery snippets are markup-only; the template CSS styles them — never link the gallery files from the output.)
- **Filename**: `YYYY-MM-DD-hh-mm-ss-<short-title>.html`. The timestamp is the current local date-time; `<short-title>` is 2–4 kebab-case words derived from the question. If the question is not in English, translate the short-title to English kebab-case (the document body stays in the question's language).
- **Never overwrite**: each invocation writes a new file. The timestamp makes collisions impossible, even for identical repeated questions — this preserves the history of what was asked when.
- Get the timestamp from the system clock, e.g. `date +%Y-%m-%d-%H-%M-%S`.

#### 6. Deliver

Reply in chat — short, the document is the deliverable:

- A **one-paragraph** answer to the question (so the chat alone is still useful).
- A **clickable link** to the file: print the absolute path (clickable in the VS Code integrated terminal) and a `vscode://file/<absolute-path>` URI so the user can open it directly in the editor.

### list — `/explain list`

Show the current user's past explainers so they can find earlier documents.

1. Resolve the output dir using step 1 of the explain action (roster match, or ask once).
2. List `*.html` files in that dir. For each, parse the date-time from the filename and the `<title>` from the file.
3. Print a small table in chat: Date · Title · Filename. If the folder is empty or missing, say so plainly.

## Usage

```
/explain <question>            Generate a visual HTML explainer answering the question.
/explain --simple <question>   Same, written jargon-free for a non-technical reader.
/explain list                  List your past explainers.
/explain help                  Show this guide.
```

The document is saved to your personal scratch folder (`tasks/<you>/_scratch/explain/`), is local-only (gitignored), and opens offline in any browser. Each run creates a new timestamped file.

## Notes

- **Aggregator, not oracle.** If the project has expert agents or search tools, lean on them for the facts; this skill owns the structure and the visuals. In a bare project with no such tools, it still works using file reads alone.
- **Not a canonical source.** Every generated document carries a banner saying so and lists its sources — a generated explainer is a point-in-time snapshot, and the linked source files are the truth. Don't let a stale explainer be quoted as authoritative later.
- **Project-agnostic.** This skill hard-codes no project names, paths, or domain terms. Everything specific is read from the project at runtime. The generated *content* is project-specific; the skill is not.
- If `$ARGUMENTS` is empty or just "help", show the Usage guide.

## Changelog

See [README.md](README.md) for version history.
