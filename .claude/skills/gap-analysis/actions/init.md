# Action: `init`

Scaffold a new gap-analysis markdown file from `templates/gap-analysis.md`.

## Usage

```
/gap-analysis init <topic> --component <slug> [--id <kebab>] [--title "..."] [--topic-freeform]
```

## Arguments

- **`<topic>`** (required, positional) — one of the keys in `data/topic-advisor-map.yml` (or its `aliases`). Examples: `risk`, `regulatory`, `vnv`, `cybersecurity`, `clinical`, `human-factors`, `filing`, `postmarket`, `quality`, `software-architecture`, `systems-engineering`. Aliases like `fmea` → `risk`, `pccp` → `filing` are resolved at lookup time.
- **`--component <slug>`** (required) — one of the `arch_slug:` values in `project.yml dhfs[]` (typically the item-DHF slugs) OR the system DHF's `leaf:` value (for cross-component / system-level / filing-aware analyses).
- **`--id <kebab>`** (optional) — short kebab-case identifier; becomes the filename. If omitted, generated from `<topic>-<title-kebabbed>` (e.g., `risk-hazard-misscoring-catalog`).
- **`--title "..."`** (optional) — human-readable title. If omitted, the skill prompts for one.
- **`--topic-freeform`** (optional) — accept a topic name that isn't in the map; will leave `recommended_agents:` empty so the author can populate manually.

## Steps

1. **Validate `<component>`** against `project.yml`:
   - Walk `dhfs[]`. Match `<component>` against `arch_slug:` (item DHFs) or `leaf:` (system DHF). Error if no match — list the valid component slugs.
2. **Resolve `<topic>`** against `data/topic-advisor-map.yml`:
   - Look in `topics:` first, then `aliases:` (which resolve to a canonical topic key).
   - If not found and `--topic-freeform` not passed, error with the list of known topics.
3. **Generate `<id>`** if not passed:
   - Combine `<topic>` + kebab-case of `<title>` (or prompt for `<title>` first).
   - Ensure uniqueness against existing `docs/_analysis/<component>/*.md` files.
4. **Refuse to overwrite**: if `docs/_analysis/<component>/<id>.md` already exists, error with a pointer to use `--id` to disambiguate or to update the existing file directly.
5. **Build the frontmatter blocks**:
   - `recommended_agents:` — concatenate `primary[]` + `consulting[]` from the topic-advisor map. Primary first. Empty list if `--topic-freeform`.
   - `grounded_against:` — pre-populate component-relevant defaults by walking `project.yml dhfs[]` for the matched component:
     - For an item DHF, default to:
       ```yaml
       - jira_mirror: docs/project/_jira/<arch_slug>/<latest_version>/hazards.md
       - jira_mirror: docs/project/_jira/<arch_slug>/<latest_version>/hazard-causes.md
       - confluence: docs/project/_confluence/<arch_slug>/   # walk to specific artifact during authoring
       ```
     - For the system DHF, default to:
       ```yaml
       - dhf: docs/project/dhfs/<leaf>/
       - submissions: docs/project/submissions/   # walk to specific filing during authoring
       ```
     - Always include a standards default based on `<topic>` (the topic-advisor map's `typical_sources` is a starting list; the author refines).
   - `authored_by:` — start with `- human:<git user.name>` (read via `git config user.name`). If invoked from an agent context, the agent appends itself when it writes.
6. **Render** `templates/gap-analysis.md` substituting:
   - `{{ id }}`, `{{ title }}`, `{{ topic }}`, `{{ component }}`
   - `{{ today }}` (ISO-8601 date)
   - `{{ author }}` (the git user.name)
   - `{{ authored_by_block }}`, `{{ grounded_against_block }}`, `{{ recommended_agents_block }}` — pre-formatted YAML-list strings (indented two spaces, ready to drop into frontmatter)
7. **Write** to `docs/_analysis/<component>/<id>.md`. Create the component folder if missing (rare — existing `_analysis/` already has the four standard component folders).
8. **Report**:
   - Path written
   - `recommended_agents:` (primary first, then consulting)
   - Reminder: this file is author-owned; `/gap-analysis` never auto-overwrites it
   - Suggest the next action — typically `/gap-analysis fan-out <id>` to invoke the primary advisor for an initial pass, or open the file in your editor to fill in `## Goal of this analysis` and `## Assertions` by hand first
8. **Refresh sidecars.** Run `/gap-analysis render` so the new analysis appears in `docs/_analysis/index.json` (the project-console roll-up). Re-run after fan-out / hand-edits.

## Example

Assuming `project.yml` declares an item DHF with `arch_slug: <arch>` and a Jira version `<version>`:

```
/gap-analysis init risk --component <arch> --title "Hazard misscoring catalog vs ISO 14971 § 5.5"
```

Produces `docs/_analysis/<arch>/risk-hazard-misscoring-catalog-vs-iso-14971-5-5.md` with frontmatter:

```yaml
---
id: risk-hazard-misscoring-catalog-vs-iso-14971-5-5
title: Hazard misscoring catalog vs ISO 14971 § 5.5
status: draft
component: <arch>
topic: risk
created: <today>
last_updated: <today>
authored_by:
  - human:<git user.name>
grounded_against:
  - jira_mirror: docs/project/_jira/<arch>/<version>/hazards.md
  - jira_mirror: docs/project/_jira/<arch>/<version>/hazard-causes.md
  - confluence: docs/project/_confluence/<arch>/product-overview/software-risk-assessment-sra/
  - standard: ISO 14971:2019 § 5.4 & § 5.5
recommended_agents:
  - risk-management         # primary
  - regulatory-affairs      # consulting
  - clinical-affairs        # consulting
superseded_by: null
---
```
