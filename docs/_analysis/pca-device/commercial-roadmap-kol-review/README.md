# Gap Analysis — Commercial Roadmap KOL Review

> _Demo sample data — not for clinical use._

Folder-per-analysis cluster for the **KOL evaluation of the 5-year commercial roadmap** (`docs/project/strategies/commercial-strategy.md`). Run as **two agent layers**: (1) our **discipline advisors** (clinical, regulatory, program-management, human-factors) and (2) the **8-member KOL persona panel** — one agent per named KOL, each speaking in the first person. Together they critique the roadmap's feature set, sequencing, evidence sufficiency, and home-PCA safety.

> The KOL opinions are **simulated persona responses for this demo**, not real collected feedback (consistent with finding F-1, which notes the project's KOL profiles are "not yet contacted").

## Reading order

1. **`commercial-roadmap-kol-review.md`** — the aggregate / final report. Start here. Carries the assertions, the KOL-panel verdict table, the F-1…F-21 findings, convergence calls, and the cross-discipline open-questions roll-up.
2. **`recs-*.md`** (4) — full per-discipline advisor responses (clinical / regulatory / program-manager / human-factors).
3. **`kol-KOL-*.md`** (8) — each KOL's full individual opinion, in their own voice.

## File inventory

| File | Role | Produced by |
|---|---|---|
| `commercial-roadmap-kol-review.md` | Aggregate / final report (`id:` matches folder) | conductor (main session) merging advisor + KOL findings |
| `recs-clinical-affairs.md` | Discipline advisor — full response (KOL voice, primary) | `clinical-affairs` advisor |
| `recs-regulatory-affairs.md` | Discipline advisor — full response | `regulatory-affairs` advisor |
| `recs-program-manager.md` | Discipline advisor — full response | `program-manager` advisor |
| `recs-human-factors.md` | Discipline advisor — full response | `human-factors` advisor |
| `kol-KOL-0006-paul-james.md` | KOL opinion — PCA / opioid safety (anchor) | `paul-james` KOL agent |
| `kol-KOL-0001-giuliano-kathleen.md` | KOL opinion — smart-pump usability / alarm fatigue | `giuliano-kathleen` KOL agent |
| `kol-KOL-0008-shah-parth.md` | KOL opinion — alert fatigue / optimization | `shah-parth` KOL agent |
| `kol-KOL-0004-kuitunen-sini.md` | KOL opinion — DERS / dose-limit safety | `kuitunen-sini` KOL agent |
| `kol-KOL-0002-kirkendall-evan.md` | KOL opinion — smart-pump safety / CDS / pediatrics | `kirkendall-evan` KOL agent |
| `kol-KOL-0005-pennathur-priyadarshini.md` | KOL opinion — human factors / usability | `pennathur-priyadarshini` KOL agent |
| `kol-KOL-0007-gorski-lisa.md` | KOL opinion — infusion-nursing standards | `gorski-lisa` KOL agent |
| `kol-KOL-0003-braithwaite-susan.md` | KOL opinion — insulin / ambulatory-pump analogy | `braithwaite-susan` KOL agent |
| `commercial-roadmap-kol-review.gap.json` | Machine projection for the console (derived) | `/gap-analysis render` (never hand-edited) |

## Cross-file conventions

- The aggregate's `id:` frontmatter matches this folder name.
- Each `recs-*.md` carries `parent_analysis: commercial-roadmap-kol-review` in frontmatter.
- Internal references use short relative paths (e.g., `[recs-clinical-affairs.md](recs-clinical-affairs.md)`).
- Each F-N finding in the aggregate carries a `**Author:** agent:<name>` line so the console attributes the finding to the advisor who raised it.

## How this folder was produced

`/gap-analysis init clinical --component pca-device --id commercial-roadmap-kol-review`, then `fan-out` spawned the four advisors (clinical-affairs primary; regulatory-affairs, program-manager, human-factors consulting) to evaluate `docs/project/strategies/commercial-strategy.md`. Each advisor returned a full per-discipline prescription (written here verbatim as `recs-*.md`) plus structured F-N findings the conductor merged into the aggregate. `render` then produced the `.gap.json` + refreshed `docs/_analysis/index.json` for the project-console Gap Analysis tab.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-06-03 | Ben Xavier (task ben/080) | Folder scaffolded; 4-advisor fan-out evaluating the 5-year commercial roadmap. |
