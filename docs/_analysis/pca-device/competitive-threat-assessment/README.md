# Gap Analysis — Competitive Threat Assessment

> _Demo sample data — not for clinical use._

Folder-per-analysis cluster for the **competitive-threat gap analysis** of the GlobalLogic infusion portfolio (anchor: **PP3500 / PainEase PCA Advanced**). It answers one question: **where is the portfolio actually exposed to competitors, and how much of our own competitive case would survive outside scrutiny?**

## The evidence-grade contract (read this first)

This analysis deliberately mixes two kinds of subject matter, and grades them differently. **Every claim in this cluster carries an explicit grade**:

| Grade | Meaning | Typical subject |
|---|---|---|
| **`SUBSTANTIATED`** | Backed by a citable public/primary source (FDA database, guidance, peer-reviewed literature, company filing). URL + date recorded. | The real competitors — BD, Baxter, ICU Medical, B. Braun, Fresenius Kabi, Insulet, Medtronic |
| **`ARITHMETIC`** | Verifiable by computation from figures stated in the project's own documents. Reproducible, no external source needed. | The market-growth and CAGR claims in the input-analysis docs |
| **`INTERNAL-DEMO`** | Stated only in this repo. Fabricated demo content by construction — **externally unverifiable and must never be presented as evidence**. | Every GlobalLogic device figure (accuracy, battery life, satisfaction, error rates, market share) |
| **`INFERRED`** | Reasoned from substantiated facts. The reasoning chain is stated so a reader can reject it. | Threat trajectories, second-order effects |
| **`OPINION`** | Advisor judgment with no source. Labelled as such, with why no source exists. | Strategic recommendations, prioritisation calls |
| **`UNVERIFIED`** | Claimed somewhere but could not be confirmed against a primary source. What was seen, and what would close it, are recorded. | Third-party statistics quoted without attribution |

The grade is not decoration. A finding built on `INTERNAL-DEMO` evidence cannot support a competitive claim to a customer, a regulator, or an investor — and the analysis says so explicitly wherever that applies.

## Reading order

1. **`competitive-threat-assessment.md`** — the aggregate / final report. Start here. Carries the threat model, the assertions, the F-N findings with visualizations, the risk register with mitigations, and the cross-discipline roll-up.
2. **`research-*.md`** (4) — the public-source evidence base the findings cite. These are the substantiation layer; the aggregate references them rather than restating them.
3. **`recs-*.md`** — full per-discipline advisor prescriptions.

## File inventory

| File | Role | Produced by |
|---|---|---|
| `competitive-threat-assessment.md` | Aggregate / final report (`id:` matches folder) | conductor (main session) |
| `research-competitor-regulatory-record.md` | Public FDA / recall / clearance record of the real competitors | research agent |
| `research-market-data.md` | Independent market sizing; the project's own numbers put under test | research agent |
| `research-ai-connectivity-regulatory.md` | AI/ML clearance reality, interoperability, FDA pathway, cybersecurity gate | research agent |
| `research-pca-clinical-landscape.md` | Is IV PCA itself in structural decline; PCA safety + monitoring expectations | research agent |
| `recs-commercial.md` | Discipline advisor — commercial / competitive positioning (primary) | `commercial` advisor |
| `recs-regulatory-affairs.md` | Discipline advisor — pathway + predicate exposure | `regulatory-affairs` advisor |
| `recs-clinical-affairs.md` | Discipline advisor — clinical-evidence exposure | `clinical-affairs` advisor |
| `recs-risk-management.md` | Discipline advisor — risk register + mitigations | `risk-management` advisor |
| `recs-cybersecurity.md` | Discipline advisor — cyber as a competitive gate | `cybersecurity` advisor |
| `competitive-threat-assessment.gap.json` | Machine projection for the console (derived) | `/gap-analysis render` (never hand-edited) |

## Cross-file conventions

- The aggregate's `id:` frontmatter matches this folder name.
- Each `recs-*.md` and `research-*.md` carries `parent_analysis: competitive-threat-assessment` in frontmatter.
- Internal references use short relative paths (e.g. `[research-market-data.md](research-market-data.md)`).
- Each F-N finding in the aggregate carries a `**Author:** agent:<name>` line so the console attributes it to the advisor who raised it.
- **Every substantive claim carries a grade token** from the table above, inline, in `CODE` form.

## Visualizations

The aggregate embeds **inline SVG** charts inside finding bodies. This works because the console's gap-analysis renderer (`console/gap_analysis/router.py:_md_to_html`) and its documents renderer both pass block-level raw HTML through Python-Markdown untouched — so no console-skill change was needed to get charts into the view.

Chart colors follow the `dataviz` skill's validated palette, re-validated against **this console's actual surfaces** (light `#ffffff`, dark `#1e293b`):

- **Categorical** — `#3987e5` / `#d95926` / `#199e70`. Passes all-pairs CVD and normal-vision floors on *both* surfaces, so one palette serves either theme.
- **Ordered magnitude (severity, exposure)** — the single-hue blue sequential ramp, steps 250–550 (`#86b6ef` → `#1c5cab`). Chosen over a red/amber/green risk palette because red↔green measures **ΔE 4.1 under deuteranopia** — the classic failure — and severity is magnitude, not state.
- Status hues appear only on badges that always carry an icon **and** a word, never as a plot's sole encoding.
- All text/axis strokes use `currentColor` so charts inherit the console's active theme ink.

## How this folder was produced

Scaffolded under `/gap-analysis` conventions with `--topic-freeform competitive` (the skill's `data/topic-advisor-map.yml` carries no competitive/commercial topic — see the aggregate's Open Questions for the proposal to add one). Four research agents built the public-source evidence base first; the discipline advisors then reasoned **against that evidence base** rather than from memory, and the conductor merged their findings into the aggregate. `render` produced the `.gap.json` + refreshed `docs/_analysis/index.json`.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-08-05 | Ben Xavier (task ben/113) | Folder scaffolded; evidence-grade contract defined; 4 research agents + 5 discipline advisors fanned out against the competitive-landscape and market-research input analyses. |
