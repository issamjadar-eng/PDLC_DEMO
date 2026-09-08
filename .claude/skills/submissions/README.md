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
| 10 | 2026-09-08 | **Version pin aligned.** `VERSION` read `6` while the frontmatter had been at `version: 10` since 2026-07-08 — an ambiguous unit-under-test pin flagged by the workbench validation environment record. `VERSION` now reads `10`; no functional change. |
| 10 | 2026-07-08 | **Propagate the Bucket-2 fix to the generating templates (cross-filing handoff guard).** A prior doc-side fix added the public-PCCP-content requirement to a project's PCCP body + its 510(k) manifest — but the **skill's `510k-summary` template had zero mention of PCCP**, so the next project scaffolding a 510(k)-with-PCCP would repeat the miss. Closed the skill layer: `templates/510k/510k-summary.md` gains a conditional **§ 8 Predetermined Change Control Plan** (the receiving-document guard — the public content is *authored* in the PCCP but *delivered* in the 510(k) Summary); `templates/_shared/composition-manifest.template.md` gains a scaffold reminder to track the PCCP-Summary content so it can't fall through at assembly; and `references/pccp-full-document-structure.md` names the **cross-filing handoff** explicitly (a fix to the PCCP body alone leaves the receiving document blind) and sharpens the data-governance anti-tampering control to tie it to the **sequestered test set** (what keeps sequestration real), not a floating control. |
| 9 | 2026-07-08 | **Q-Sub→filed reconciliation gate + commonly-missed guidance elements.** A bidirectional stress test of a filed PCCP against its transmitted Q-Sub found the sharpest defect class the skill had no guard for: a filed PCCP that **under-delivers or contradicts commitments the Q-Sub already made to FDA** (a fabricated "per FDA agreement"; a filed security-patch pathway with no home in the plan; a scope exclusion silently narrowed). Added to `references/pccp-full-document-structure.md` a **"Reconcile the filed PCCP against the transmitted pre-submission"** gate — the transmitted document sets the floor; the filed one may exceed but not fall below it, contradict it, or claim an FDA agreement only requested — plus the guidance elements authors commonly omit from *both* artifacts (data-governance back half: storage/retention/QA/anti-tampering/human-subjects; baseline labeling PCCP+ML disclosure; methods-comparison statement; version display; labeling-review-before-update; reasoned prior-data-rerun N/A). Wired the reconciliation requirement into the SKILL.md scaffold action + a scope note on the `check` action (S1–S4 are within-package; cross-filing reconciliation is a manual agent walk, S5 automation tracked). |
| 8 | 2026-07-08 | **Empirical "what good looks like" grounding for PCCPs.** Prior to this the skill grounded PCCP quality ONLY in FDA guidance text (whose worked examples are hypothetical and, per FDA, "not the complete detail expected") — a multi-agent audit found zero real authorized-PCCP exemplars anywhere in the skill. Added `references/pccp-authorized-exemplars.md`: a catalog of real FDA-authorized PCCPs in the public 510(k) record (K250369 Axial3D INSIGHT — closest archetype to a bone-segmentation planning device; K241561 MammoScreen BD — best-in-class docs + drift monitoring; K242807 HeartFocus — most operationally detailed; K242551 Syngo Auto-EF — conservative/locked archetype; K233955 Clarius OB AI; K233030 BoneMRI), plus the reusable modification-table schema, the Verification/Validation split, quantified acceptance-criteria patterns (κ>0.85, PPA≥96.5%±CI, one-iteration cap), scope-fence boilerplate, and the documentation-completeness bar (post-market drift monitoring is the top exemplary-vs-adequate differentiator — only ~3/34 filings had it). Project-agnostic (public FDA records; K-numbers, not device names). Registered in the SKILL.md Supporting Files table. |
| 7 | 2026-07-07 | **Full filed-PCCP authoring capability.** Prior to this the only PCCP asset was the Q-Sub `pccp-summary` template — the skill could scaffold an abbreviated PCCP *summary* for a pre-sub but had no profile for the **full filed PCCP** that rides inside a 510(k). Added: a `templates/pccp/` profile with `pccp-plan.md` (the complete filing-depth document — Document Control header, Description of Modifications § VI, four-sub-component Modification Protocols with a worked Statistical Analysis Plan § VII.B(1)–(4), the required Traceability table § VII.C, Impact Assessment § VIII, ISO 14971 gate, routing, monitoring, reporting); a `references/pccp-full-document-structure.md` depth-contract finding aid (the SAP checklist, the required traceability table, the IA elements, and the methodology-complete-vs-value-locked distinction that keeps a filed PCCP from reading like a Q-Sub summary); the `pccp` filing-type profile now resolves to `templates/pccp/` (not the Q-Sub PCCP subset); `render_sidecars.py` learns the `pccp-plan` stem (console title "Predetermined Change Control Plan (PCCP)"). Scaffold action gains an altitude-choice note (Q-Sub summary vs filed full PCCP) so the per-modification depth isn't over-built before FDA prunes the category set. |
| 6 | 2026-07-07 | **Claim↔primary-source grounding in `provenance` (+ frontmatter `version` resync 2→6).** `provenance check` now runs a second check class alongside source-drift: a `claims_to_source[]` entry may pin its evidence structurally (`source_path` + `source_page` + verbatim `quote`), and the quote must resolve in that pinned source. New findings: **`ungrounded-claim`** (quote not found — transmit-blocking, like drift), **`unresolved-source`** (the `source_path` doesn't resolve), **`grounding-skipped`** (NOTE when `pypdf` is absent so PDF quotes can't be verified). Catches the class drift-pinning can't: a factual claim asserted *about* an external primary source (a predicate/cleared-filing PDF) that the source doesn't support, or that was written from a sibling summary while the source sat un-consulted. `_norm` folds typographic quotes/dashes so an ASCII-pinned quote matches curly-quote PDF extraction. Grounding is opt-in per claim (legacy free-text `claims_to_source` rows unaffected). New rule `references/claim-grounding.md`; SKILL.md schema + action docs updated; `provenance_reconcile.py` + `references/claim-grounding.md` added to the Supporting Files table. `pypdf` is a soft dependency (hash-only + non-PDF grounding still run without it). |
| 5 | 2026-07-06 | **`provenance {check,stamp}` — source-drift reconciliation.** New `scripts/provenance_reconcile.py` addresses a class the seam checks can't: **reproduced-content drift** — a filed doc keeps a self-contained summary of an upstream source (readability / W12.1 — the reviewer must not be sent out to the source), and the source later changes while the copy silently does not. `stamp` pins each content source in `_provenance/<doc>.provenance.yml` to its `git hash-object` SHA in a generated `<doc>.sources-lock.json`; `check` flags **drift** (source changed since last reconciliation, with the `how_used` note so you know what to re-check), **unresolved-path** (a recorded source path no longer resolves — provenance rot), **unbaselined**, and **malformed-yaml**. The lock is kept separate from the human sidecar so churny hashes never force a fragile edit. Deliberately NOT "reference instead of reproduce" — that would sacrifice reader confidence; keep the content, hash-watch the source. Reference implementation: device-description (3 stale `dhfs/` source paths repointed to `_confluence/`, stamped, clean); `check` immediately surfaced 8 rotted source paths + 2 malformed sidecars across the rest. PyYAML for read; stdlib + git otherwise. Project-agnostic. |
| 4 | 2026-07-06 | **`check` gains S4 (stable-key liveness) — the semantic seam.** Added a fourth check to `check_package_consistency.py`: an *anchor/support* declaration (in a transmitted doc or the manifest) that names a stable question key (`QK-*`) the questions master map has since **deferred or dropped** → WARN. This closes the recurring "stale reference" drift class the structural checks (S1–S3) can't see — the root cause being **non-uniform updates** (a question renumber/deferral in `fda-questions.md` not propagated to the siblings that declare they anchor it). Reads the `QK → display → transmitted?` master map; disposition-guarded (a "QK-X was deferred → DQ-N" note isn't flagged) and skips changelog/metadata rows; scans transmitted docs + the manifest only (a deferred brief sitting in the folder correctly anchors its own deferred question). Immediately found real drift in the cyber brief, the cover letter, and the separation argument after a question-set trim/renumber. Reference doc updated (four seams + the root-cause note that the citation half stays with `/reference-audit`). |
| 3 | 2026-07-06 | **Cross-document seam checks (`check` action).** Added `scripts/check_package_consistency.py` + the `### check` action: three project-agnostic checks for defects that live in the *seam between two documents* and survive every per-document lint — **S1** cross-reference accuracy (a summary attachment described as the "full" predicate/SE analysis; deferral + contrastive phrasings exempt), **S2** attachment-number consistency (prose "attachment N" matching no numbered list; per-list contiguity; a uniform two-list offset collapsed to one WARN vs. non-uniform drift listed per-doc), **S3** folder-boundary compliance (a transmitted attachment sourced outside the filing folder; a filed-body `../../` reach). Reuses `qsub_scope_lint`'s `docid`/`strip_zones`; same exit contract (0 clean / 1 WARN / 2 FAIL under `--transmit-gate`). Companion guidance `references/pre-sub-package-consistency.md` (the three seams + the predicate/SE three-tier model: identity-level → abbreviated summary → full 510(k) analysis). Also registers `references/pccp-change-scope-modify-vs-add.md` (modify-existing-output vs. add-new-output distinction), added earlier this cycle. Motivated by real seam defects a per-doc lint missed on a live Q-Sub package (a summary attachment mislabeled "full", a prose attachment off-by-one, a transmitted piece living in an upstream analysis folder). No console JSON schema change (still `1.0`). |
| 2 | 2026-06-15 | **Filing-type template profiles.** Reorganized `templates/` into per-filing-type profiles (`_shared/` + `qsub/` + `510k/` + `pma/`); `scaffold` now resolves a filing type to its profile instead of instantiating one flat Q-Sub-shaped set for every filing. Added the 510(k) document set (indications-for-use/FDA-3881, 510(k) summary, substantial-equivalence + predicate comparison, performance-testing summary, truthful-&-accuracy statement) and a PMA **placeholder** set. Registered `pma` as a filing type in `render_sidecars.py` `FILING_META` + new `DOC_META`/`DOC_ORDER` stems. Documented the **composition-manifest contract** (sections/columns `/tracker` parses) and affirmed submissions-owns-manifest / tracker-consumes in SKILL.md + README; added a producer/consumer skill-relationships table. No console JSON schema change (still `1.0`). **Post-authoring verification (regulatory + quality review of the new templates) drove fixes folded into this version:** corrected the Truthful-&-Accuracy citation `807.87(k)`→`807.87(l)` ((k) is the Class III cert); genericized the `_shared` composition-manifest Included-Pieces rows so they're profile-neutral (was Q-Sub-shaped, which broke the cover-letter↔manifest 1:1 alignment for other filings); documented proposed-labeling + consensus-standards/DoC as **DHF-attached exhibits** (controlled-record PDFs, not filing-folder templates); updated eCopy/eSTAR wording to the eSTAR-mandatory posture; and added scaffold-time QMS-mapping notes (sign-off-chain + controlled-record transition stay project-specific, never hard-coded in the registry templates). |
| 1 | 2026-06-15 | Initial skill. `scaffold` + `render` + `list` actions; `render_sidecars.py` producer of the console `schema_version: 1.0` contract; templates modeled on a real Q-Sub package shape (three-tier doc model, composition manifest, provenance sidecars). Paired with the project-console Submission section. |
