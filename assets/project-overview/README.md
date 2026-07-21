# project-overview — md-deck output

Auto-generated deck folder. Source: `project-overview.md`.

## Structure

| File | Owner | Purpose |
|---|---|---|
| `index.html` | md-deck | Final single-file slide deck — open in a browser. |
| `candidates.html` | md-deck | 4-up review UI; emitted on first build or with `--review`. |
| `picks.json` | user (curated) | Per-section pick selection. Keyed by section **slug**. |
| `distillation.yml` | md-deck | Deck-wide brief + per-section dossiers. Sections keyed by slug. |
| `manifest.json` | md-deck | Build provenance (slug, source_lines, source_sha256 per slide). |
| `.creative-cache/` | md-deck (committed) | Per-(slug, sha, slot) successful agent HTML. Survives across builds; stale entries swept by `--sweep-cache`. |
| `.debug/` | md-deck (gitignored) | Failure dumps from the creative fan-out. Safe to delete. |

## Iterate

- Refresh one section's creatives only:
  `python3 .claude/skills/md-deck/scripts/build.py project-overview.md --creative --re-roll-creative <slug>`
- Re-distill + re-roll one section in one step:
  `... --re-roll-section <slug>`
- Retire orphan / stale cache:
  `... --sweep-cache`
- Forensic / cache-bypass:
  `... --creative --no-cache`

## Identity model

Sections are identified by **slug** (derived from `### N.M Heading`),
not by source line range. Cache validity is keyed on the section's
content-SHA. Inserting / deleting unrelated sections does not invalidate
this section's cache. See task ben/163 for design notes.
