# Source Document Index

Authoritative list of original (non-markdown) source documents held under `docs/internal/source/` and the markdown conversions tracked against them under `docs/internal/source-md/`. Docflow uses this file to discover sources and verify round-trip coverage.

## Conventions

- One row per original file. Grouped by topic folder.
- `Source` column — path relative to `docs/internal/source/`.
- `Markdown` column — path relative to `docs/internal/source-md/`. Empty if no conversion exists yet.
- `Status` — one of `converted` (round-trip verified), `draft` (conversion present, not yet verified), `source-only` (no conversion), `external` (reference material not intended for conversion).
- Add a row when a new source is dropped in. Update the status column when the pair reaches a new state. Run `/docflow check` to validate the table against disk.

## Index

| Topic | Source | Markdown | Status | Notes |
|-------|--------|----------|--------|-------|
| kol-methodology | `kol-methodology/AI KOL Personality and Preference Assessment Framework for Role-Playing Language Agents.pdf` | — | source-only | Reference literature for the KOL persona corpus under `tools/project-console/agents/kol/`. No conversion planned — read in place. |

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-20 | Ben Xavier | Initial stub — indexed the one source file present under `kol-methodology/`. Closes task ben/010 audit finding #10 (`INDEX.md` missing). |
