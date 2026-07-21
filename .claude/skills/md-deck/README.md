# md-deck — Design Notes

Builder sibling to `frontend-slides`: non-interactive markdown → single-file HTML slide deck pipeline. See `SKILL.md` for the operating contract (heuristic registry, content-split rules, variant detection, provenance). This README carries maintainer metadata that doesn't belong in runtime context.

## Design lineage

- v0.1–v0.3 built under the deck-build improvement tasks; v0.3 extracted the shared infrastructure layer (viewport CSS, presets, PDF/deploy scripts) into `frontend-slides`.
- v0.4+ added the section/candidates/picks machinery (`picks.json` curation, `candidates.html` review page, creative-slot fan-out with per-section SHA cache).

## Dependencies

| Dependency | Purpose |
|---|---|
| `frontend-slides` skill | viewport-base.css, preset registry, export-pdf.sh, deploy.sh |
| `scripts/icons.py` | icon repository imported by `build.py` |
| `runtime/deck-runtime.js` | chrome auto-numbering, provenance modal, key nav |

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill has SKILL.md | File exists at skill root | Required | shared |
| Frontmatter complete | name, description, version, updated all present | Required | shared |
| README.md exists | Design doc at skill root | Required | shared |
| Changelog current | Latest entry matches version number | Required | shared |
| Split parts have unique slugs | `_split_dense_slide` suffixes continuation slugs `--contN` | Required | local |
| Output convention | Decks land at `<root>/assets/<source-slug>/` with manifest.json | Required | local |

## Changelog

- 0.6.2 (2026-07-20): Two build.py bug fixes. (1) Density-split continuation parts now get unique `--contN` slug suffixes — previously all parts shared the head slide's slug, so the slug-keyed section/candidates/picks machinery let the last part overwrite the head: the head slide was silently dropped from the built deck and the "(cont.)" part emitted once per plan entry (visible as duplicate "(cont.)" slides with no head). Head part keeps the unsuffixed slug so existing picks.json entries stay bound. (2) Non-bold-led bullets converted to card-grid/principle tiles were labeled via a hard `text[:60]` slice (no ellipsis, tail silently dropped, could cut mid-word). New `_split_label_sub()` helper splits at a sentence/em-dash boundary into label + subtitle, keeps short bullets whole, and word-boundary-truncates long ones with a visible ellipsis and the tail preserved in the subtitle; applied at all three tile-construction sites.
- 0.6.1: Auto-emitted per-deck README.md + candidates.html build artifacts (folder-README rule compliance).
- 0.6.0 (2026-05-02): Domain-neutral trunk + opt-in icon vocabulary packs; picks.json relocated into the assets output folder.
