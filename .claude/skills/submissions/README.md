# submissions — design & best practices

Authors and maintains a medtech project's FDA submission **content package**
(`docs/project/submissions/<filing>/`) and the JSON sidecars the project-console
**Submission** section renders. See [SKILL.md](SKILL.md) for actions and the
console JSON contract.

## Why this skill exists

Submission content has a distinctive shape that no other skill owns:

- A **three-tier document model** (leading metadata → `🔒 INTERNAL` working
  apparatus → FDA-facing filed body) so one markdown file serves both internal
  review and external transmission, with the 📤/📝/⏸️/📖 scope labels marking
  which content routes where.
- A **`composition-manifest.md`** package-assembly artifact (Required /
  Supporting / strengthener-brief / Excluded buckets, transmission-blocking
  gates, reviewer sign-off) that is itself internal-not-transmitted.
- Per-doc **`_provenance/*.provenance.yml`** audit sidecars mapping every claim
  to its source.

`/tracker` answers *deliverable × phase readiness*; `/dhf-manifest` answers
*are the right documents present per regulation+QMS*; `/change-control` *publishes*
to Confluence/Windchill; `/medtech-docs` *scaffolds the DHF*. None of them author
the FDA-facing Q-Sub narrative or render it for the console. This skill does.

## Producer / consumer split

`render` is the **producer** of the console contract; the project-console
`submission/` package is the **consumer**. The two are loose-coupled exactly like
the gap-analysis and trace-matrix sidecars: the console reads only the JSON; if
the JSON is missing it degrades to "run `/submissions render`". This keeps the
console company-agnostic and lets any producer that emits the same shape light up
the view.

## Architecture & boundaries

### Filing-type profiles

Scaffolding is **filing-type-aware**. `templates/` is organized as one folder per
filing type plus a shared folder:

```
templates/
├── _shared/   composition-manifest.template.md + provenance.template.yml
├── qsub/      cover-letter · device-description · intended-use · fda-questions · pccp-summary
├── 510k/      cover-letter · indications-for-use · 510k-summary · substantial-equivalence · device-description · performance-testing · truthful-accuracy-statement
└── pma/       🚧 placeholder stubs (cover-letter · ssed-summary · device-description · nonclinical-studies · clinical-studies · manufacturing-information · labeling)
```

`scaffold <filing>` resolves the filing type to its profile and lays down that
document set (+ `_shared/`). This fixes the v1 bug where a single flat Q-Sub-shaped
set was instantiated for *any* filing — `scaffold 510k` would drop an FDA-questions
doc into a 510(k) folder. The PMA profile is a **placeholder** (folder shape only);
PMA (21 CFR Part 814) is far heavier than a 510(k) and is not built out in this
version. The registry lives in SKILL.md (`## Filing-type profiles`) and is mirrored
in `render_sidecars.py` (`FILING_META` / `DOC_META`).

### submissions ↔ tracker — who owns what

The only seam between this skill and `/tracker` is the **composition-manifest**, and
the boundary is deliberate:

- **`submissions` owns the manifest** — its template, its authoring, and its
  **section/column schema**. The manifest is hand-authored from the template; it is
  *not* generated from `regulatory.yml` milestones (tracker's SKILL.md calls it a
  "projection of milestone bindings" — that is conceptual framing, not a code path).
- **`/tracker` is a read-only consumer.** `tracker/scripts/generate.py` walks the
  manifest as **one of ~7 inputs** (alongside the milestone catalog, the dhf-manifest
  JSON, the system SAD, `project.yml`, FDA guidance…) to emit `(submission)`-scope
  rows; two `/best-practices` checks assert the manifest parses and its pieces resolve.

Two parsers therefore read one file (`render_sidecars.py::parse_manifest` here +
`generate.py` there). They are kept **independent but governed by one declared
schema** (the `## Composition-manifest contract` in SKILL.md) — the loose-coupled
sidecar pattern, not a shared import. Collapsing them into a single shared parser is
a possible future refinement, not a requirement.

**Why not merge the two skills:** they sit at different layers. `submissions` =
FDA-facing **content authoring + packaging** for one filing. `/tracker` = a
**program-wide readiness scoreboard** across all DHFs, engineering prerequisites, and
every milestone (QSub → 510k+PCCP → LMR1 → LMR2), with obligation-coverage analysis
against the dhf-manifest catalog and lifecycle-state plugins (Confluence/Comala,
SharePoint, Jira, Windchill). Submissions consumes none of that. Mental model:
**dhf-manifest = syllabus · tracker = scorecard · submissions = one of the things
being scored (and the only one it also authors).**

## Design rules followed

- **Ground, don't redeclare.** Submission docs reference canonical facts
  (classifications, predicate K-numbers, PCCP categories) from
  `regulatory-strategy.md` D-REG-* blocks, the system SAD, and `project.yml` —
  per `audit-wiring-before-adding-fields` and `claude-md-references`.
- **Never fabricate** standard / clinical / regulatory content; flag `[VERIFY]`.
- **Vendor-neutral AI provenance** per the `ai-changelog` rule.
- **Demo banners** — every demo doc carries `_Demo sample data — not for clinical use._`.
- **Read READMEs before writing** under `docs/` per `readme-before-write`.

## Best Practices (consumed by `/best-practices`)

- Every filing folder with content has a `composition-manifest.md` and a
  `_provenance/` sidecar per content doc.
- `.console/*.json` is regenerable from the docs via `render` (run `render --check`
  in CI to catch drift).
- Content docs follow the three-tier model; the filed body uses scope labels.
- No fabricated K-numbers, FDA contacts, or guidance titles.
- A scaffolded filing matches its **filing-type profile** (a `510k` folder carries
  the 510(k) doc set, not Q-Sub docs); every filing type in `FILING_META` has a
  `templates/<type>/` profile.
- The composition manifest keeps the section/column **contract** (`## Composition-
  manifest contract` in SKILL.md) so `/tracker`'s parser + its two manifest checks
  keep working.

## Changelog

| Version | Date | Summary |
|---------|------|---------|
| 2 | 2026-06-15 | **Filing-type template profiles.** Reorganized `templates/` into per-filing-type profiles (`_shared/` + `qsub/` + `510k/` + `pma/`); `scaffold` now resolves a filing type to its profile instead of instantiating one flat Q-Sub-shaped set for every filing. Added the 510(k) document set (indications-for-use/FDA-3881, 510(k) summary, substantial-equivalence + predicate comparison, performance-testing summary, truthful-&-accuracy statement) and a PMA **placeholder** set. Registered `pma` as a filing type in `render_sidecars.py` `FILING_META` + new `DOC_META`/`DOC_ORDER` stems. Documented the **composition-manifest contract** (sections/columns `/tracker` parses) and affirmed submissions-owns-manifest / tracker-consumes in SKILL.md + README; added a producer/consumer skill-relationships table. No console JSON schema change (still `1.0`). **Post-authoring verification (regulatory + quality review of the new templates) drove fixes folded into this version:** corrected the Truthful-&-Accuracy citation `807.87(k)`→`807.87(l)` ((k) is the Class III cert); genericized the `_shared` composition-manifest Included-Pieces rows so they're profile-neutral (was Q-Sub-shaped, which broke the cover-letter↔manifest 1:1 alignment for other filings); documented proposed-labeling + consensus-standards/DoC as **DHF-attached exhibits** (controlled-record PDFs, not filing-folder templates); updated eCopy/eSTAR wording to the eSTAR-mandatory posture; and added scaffold-time QMS-mapping notes (sign-off-chain + controlled-record transition stay project-specific, never hard-coded in the registry templates). |
| 1 | 2026-06-15 | Initial skill. `scaffold` + `render` + `list` actions; `render_sidecars.py` producer of the console `schema_version: 1.0` contract; templates modeled on a real Q-Sub package shape (three-tier doc model, composition manifest, provenance sidecars). Paired with the project-console Submission section. |
