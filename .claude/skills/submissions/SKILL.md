---
name: submissions
description: |
  Author, scaffold, and render an FDA submission package (Q-Sub / 510(k) / PCCP / PMA-placeholder) for a medtech project — the regulatory-facing document set under `docs/project/submissions/<filing>/` plus the JSON sidecars the project-console **Submission** section consumes. Scaffolding is **filing-type-aware**: each filing type has a template profile that lays down its characteristic document set (Q-Sub questions/PCCP-summary vs 510(k) substantial-equivalence/predicate-comparison/IFU vs PMA SSED/clinical placeholders). Owns the three-tier document model (HTML frontmatter metadata → `🔒 INTERNAL` working apparatus → filed body transmitted to FDA, using the 📤/📝/⏸️/📖 scope labels), the per-doc `_provenance/*.provenance.yml` audit sidecars, and the `composition-manifest.md` package-assembly artifact (Required / Supporting / strengthener-brief / Excluded buckets with transmission-blocking gates) — including its section/column schema, which `/tracker` consumes read-only.

  TRIGGER when the user wants to **scaffold, build, author, seed, generate, assemble, or render** a Q-Submission / pre-submission / 510(k) / PCCP / PMA **content package** — phrasings include: "scaffold the Q-Sub package", "set up the qsub documents", "scaffold the 510(k)", "create the FDA questions doc", "build the cover letter / device description / intended-use / substantial-equivalence / PCCP summary", "seed submission content", "assemble the composition manifest", "render the submission console view", "refresh the submission sidecars", "what's in the Q-Sub package", "is the qsub package ready to transmit". Also fire on any edit/write under `docs/project/submissions/<filing>/` content docs or `_provenance/`.

  Sibling boundaries — this skill owns submission **content** + its console sidecars. It is NOT `/tracker` (deliverable × phase readiness dashboard), NOT `/change-control` (publish to Confluence/Windchill), NOT `/medtech-docs` (DHF scaffolding), NOT `/dhf-manifest` (deliverable-coverage projection). When a fact is canonical elsewhere (regulatory-strategy.md D-REG-* blocks, the system SAD, project.yml), submission docs reference it — they do not redeclare it.
version: 10
updated: 2026-07-08
---

# Submissions

Author and maintain a project's FDA submission package and the JSON sidecars the
project-console **Submission** section renders.

A **filing** is a subfolder of `docs/project/submissions/` (`qsub`, `510k`,
`pccp`) holding a `composition-manifest.md` plus content docs. The console is a
generic consumer — it reads only the sidecars this skill's `render` action
emits; it never parses submission prose.

## Dependencies

| Requirement | Needed for | How to satisfy |
|---|---|---|
| `project.yml` | All actions (device name, pathway) | `/medtech-docs init` |
| `docs/project/submissions/` tree | All actions | `/medtech-docs init` (scaffolds qsub/510k/pccp/pma folders) |
| `docs/project/strategies/regulatory-strategy.md` | `scaffold` content grounding (D-REG-* decisions) | `/strategy` authoring |
| `python3` (stdlib only) | `render` | Already present |

If a required input is missing, report exactly what's missing and stop.

### Skill relationships (producer / consumer)

This skill needs no other skill **to run** (no frontmatter `dependencies:`), but it
sits on two loose-coupled seams — declared here so the boundaries are auditable:

| Direction | Counterpart | Seam | Coupling |
|---|---|---|---|
| **produces →** | `project-console` **Submission** section | `.console/*.json` + `<filing>/<filing>.submission.json` (this skill's `render` is the sole producer) | Console reads only the JSON shape; degrades to "run `/submissions render`" if absent. |
| **produces →** | `/tracker` | `composition-manifest.md` — **owned here** (template + authoring + schema); tracker's `generate.py` reads it as **one of ~7 inputs** and emits `(submission)`-scope rows. | Read-only consumer keyed to the section/column contract above; tracker never writes the manifest. |
| **references ←** | `/strategy`, system SAD, `project.yml`, predicate analysis | Submission docs **reference** canonical facts (classifications, K-numbers, change categories); they do not redeclare them (per `audit-wiring-before-adding-fields` + `claude-md-references`). | One-way grounding. |

Not this skill: `/tracker` (program-wide readiness scoreboard across all DHFs +
engineering + milestones), `/change-control` (publish to Confluence/Windchill),
`/medtech-docs` (DHF scaffolding), `/dhf-manifest` (obligation-coverage projection).

## The three-tier document model (HARD RULE)

Every transmitted content doc is authored in three zones, top to bottom:

1. **Leading metadata** — HTML-comment / YAML frontmatter zone: version changelog,
   the `<!-- AI-CHANGELOG -->` block (per the `ai-changelog` rule — vendor-neutral,
   never published), and optional Confluence/doc-control metadata. Never transmitted.
2. **`🔒 INTERNAL` working apparatus** — a leading container: document-control table,
   reading convention, internal source mapping to `D-REG-*` decisions / task refs,
   open conflicts. Stripped before transmission.
3. **Filed body** — the FDA-facing content, sections tagged with the scope labels
   from the `internal-vs-external-scope-labels` rule (📤 external-bound · 📝 internal
   inline · ⏸️ deferred · 📖 reference). Only 📤/filed-body content goes to FDA.

The `composition-manifest.md` is itself **🔒 INTERNAL — NOT TRANSMITTED**; the
FDA-facing package listing is the cover letter's Attachments section, which must
align 1:1 with the manifest before transmission.

## Stable Question Keys — decouple question identity from the FDA display number (HARD RULE)

A submission's question set (the Q-Sub Specific Questions, and the cover letter's
question enumeration) is **referenced across the whole package** — cover letter,
device description, predicate summary, PCCP summary, strategy docs, briefs. If the
FDA-facing display number (e.g. `Q1.2`) doubles as the question's identity in every
cross-reference and in history, any reorder or trim churns hundreds of references and
floods internal reviewers with noise. Decouple the two:

1. **Each question carries one permanent, unique stable key** — a `QK-<slug>`
   (e.g. `QK-PCCP-ALGO-UPDATE`) that **never renumbers**. The slug is semantic so it
   self-documents in history.
2. **Zone rule.** **FDA-transmitted filed bodies** (what the reviewer reads) show the
   human **display number** (`Q1.1`, `Q2.2`, …; deferred questions live in the deferred
   container with no display number). **Everything internal** — `<!-- -->`
   changelog/history, `🔒 INTERNAL` containers, internal-only docs (strategy, analyses),
   deferred-question provenance — references the **stable `QK`**, so it never churns on a
   renumber.
3. **One master map** (a `QK ↔ display ↔ topic ↔ transmit/defer` table in a 🔒 container
   in the questions doc) is the **single source of truth**. A renumber edits only the
   filed display numbers + this map; internal/history are untouched.

**Renumber procedure (collision-safe).** A package-wide renumber is a scripted,
zone-aware, single-pass remap (each match resolved against the *original* text so the
old/new display-number namespaces cannot cascade), with a **dry-run + integrity checks**
(filed headers contiguous + in order, no duplicate display IDs, `<details>` balance,
master-map ⇄ filed-headers agreement) before apply, and a **QA-conformance pass** after.
Never hand-edit a package-wide renumber.

Why: the display number is for the FDA reader; the stable key is the identity. Keeping
history and internal apparatus on the stable key is what lets the question set be
reordered or trimmed without drift or reviewer noise.

**Grounding rule:** submission docs reference canonical facts (classifications,
predicate K-numbers, change categories) from `regulatory-strategy.md` D-REG-*
blocks, the system SAD, and `project.yml` — they do not restate them as new
facts (per `audit-wiring-before-adding-fields` and `claude-md-references`). Demo
projects banner every doc `_Demo sample data — not for clinical use._`.

**"Reference, don't redeclare" bans redeclaring *facts*, not *explanation* (readability).**
The rule is anti-drift: a fact restated in two docs can diverge (an R8 cross-record
finding). It does **not** require a doc to be a bare pointer-farm. Draw the line by
content type — exactly the `audit-wiring-before-adding-fields` carve-out ("rationale
may duplicate; facts may not"):

- **Facts** (a classification, a K-number, a change-category ID, a quantity) — single-
  sourced; reference the canonical home, never restate. Divergence here is a finding.
- **Rationale, explanation, and enumerations** — *may* be carried inline so the reviewer
  follows the argument without leaving the doc. The *authoritative* wording still lives
  in one place (the referenced source); the inline gist is a readable summary, not a
  second record, so it cannot drift the fact.

> **Citation-bearing submission edits follow the authoring standard's task-close reference-audit gate.** When a submission edit adds/changes a standards clause, guidance example/appendix/§, K-number/precedent, or cross-doc reference, ensure the active task doc carries a **final-stage todo to run an independent `/reference-audit`** over the doc — verifying each citation against the **byte-correct source** (rung 3), not the distilled finding-aid. Batched once per task, run as a subagent. See `regulatory-authoring` SKILL.md (Apply-workflow) + its rule.

So: **reference the fact, restate the gist** — per the authoring standard's **W12.1**
(carry the gist inline; a reference is for depth, not comprehension). A filed section
that is mostly cross-references with little self-contained substance is a readability
defect, not compliance.

## Supporting Files

| File | Purpose |
|---|---|
| `scripts/render_sidecars.py` | Producer of the console JSON contract (see below). Stdlib only. |
| `scripts/provenance_reconcile.py` | `provenance {check,stamp}` — source-drift pinning (git blob SHA) **and** claim↔primary-source grounding (`ungrounded-claim`). PyYAML for read; `pypdf` for PDF quote grounding. |
| `references/claim-grounding.md` | Rule — a factual claim about an external primary source (predicate/cleared filing) must be grounded in that source with a verbatim `quote`, not paraphrased from a sibling summary while the source sits un-consulted. |
| `templates/_shared/` | Filing-agnostic templates: `composition-manifest.template.md` (the manifest skeleton — its section/column contract is documented below) + `provenance.template.yml`. |
| `templates/qsub/` | Q-Sub profile: cover letter, device description, intended-use, FDA questions, PCCP **summary** (abbreviated, for the pre-sub). |
| `templates/pccp/` | Full **filed** PCCP profile: `pccp-plan.md` — the complete 510(k)-embedded PCCP at filing depth (Document Control · Description of Modifications · four-sub-component Modification Protocols w/ worked SAP · required Traceability table · Impact Assessment · ISO 14971 gate · routing · monitoring · reporting). Depth contract in `references/pccp-full-document-structure.md`. |
| `references/pccp-full-document-structure.md` | Finding aid — the structure + depth FDA expects in a **filed** PCCP (§ VI/VII.B(1)–(4)/VII.C/VIII), the Performance-Evaluation **SAP checklist**, the required Traceability table, the Impact-Assessment elements, document-control apparatus, and the methodology-complete-vs-value-locked distinction. Read before scaffolding/authoring a full PCCP. |
| `references/pccp-authorized-exemplars.md` | Finding aid — **empirical** companion to the structure contract: real FDA-**authorized** PCCPs in the public 510(k) record (K250369 Axial3D INSIGHT, K241561 MammoScreen BD, K242807 HeartFocus, K242551 Syngo Auto-EF, K233955 Clarius OB AI, K233030 BoneMRI), the reusable modification-table schema, the Verification/Validation split, quantified acceptance-criteria patterns, scope-fence boilerplate, and the documentation-completeness bar (post-market drift monitoring is the top differentiator). This is our source-of-truth for "what good actually looks like," beyond the hypothetical guidance examples. |
| `templates/510k/` | 510(k) profile: cover letter, indications-for-use (Form FDA 3881), 510(k) summary, substantial-equivalence discussion + predicate comparison, device description, performance-testing summary, truthful-&-accuracy statement. |
| `templates/pma/` | PMA profile — **placeholder stubs only** (cover letter, SSED, device description, nonclinical/clinical studies, manufacturing info, labeling). Marked `🚧 PLACEHOLDER`; scaffolds the folder shape, not built-out content. |
| `README.md` | Design rationale, architecture/boundaries, Best Practices (consumed by `/best-practices`), Changelog. |

`{{PLACEHOLDER}}` tokens (`{{DEVICE}}`, `{{FILING_ID}}`, `{{PATHWAY}}`, `{{PREDICATE}}`, `{{DATE}}`, `{{TASK}}`, `{{D_REG_REFS}}`, …) are filled at scaffold time.

## Filing-type profiles

A **profile** is the template set a filing type scaffolds. The flat one-size set
was a bug — `scaffold 510k` used to drop Q-Sub questions into a 510(k) folder.
Each filing type now maps to a `templates/<profile>/` folder; all profiles also
get `templates/_shared/` (manifest + provenance).

| Filing type | Type label | Profile folder | Characteristic document set |
|---|---|---|---|
| `qsub` | Q-Sub (Pre-Submission) | `templates/qsub/` | cover letter · device description · intended-use · FDA questions · PCCP summary |
| `510k` | 510(k) | `templates/510k/` | cover letter · indications-for-use (FDA 3881) · 510(k) summary · substantial-equivalence + predicate comparison · device description · performance-testing summary · truthful-&-accuracy statement |
| `pccp` | PCCP | `templates/pccp/` (+ `qsub/` cover letter) | **Full filed PCCP** (`pccp-plan.md`) — Document Control header · Description of Modifications (§ VI) · four-sub-component Modification Protocols with a worked SAP (§ VII.B(1)–(4)) · **Traceability table** (§ VII.C, required) · Impact Assessment (§ VIII) · ISO 14971 gate · routing · monitoring · reporting. **Distinct from the Q-Sub `pccp-summary.md`** (the abbreviated PCCP *summary* for a pre-sub); the full profile is the 510(k)-embedded filed document. Depth contract: [`references/pccp-full-document-structure.md`](references/pccp-full-document-structure.md). |
| `pma` | PMA (Premarket Approval) | `templates/pma/` | **🚧 placeholder stubs** — cover letter · SSED · device description · nonclinical studies · clinical investigations · manufacturing info · labeling |

The set is also encoded in `render_sidecars.py` `FILING_META` (type labels) and
`DOC_META` (per-stem console title/kind). Adding a filing type means: a new
`templates/<type>/` profile, a row here, and a `FILING_META` entry.

**DHF-attached exhibits (not templated).** Some required submission elements are
**controlled-record PDFs derived from the DHF**, not documents authored in the
submission folder — typically **proposed labeling** (IFU + instructions + warnings)
and the **consensus-standards list / declarations of conformity**. These are not
profile templates; they are listed in the composition manifest's "Attached from the
DHF" table and in the cover letter's Attachments under "attached from the DHF." Do
not author a `labeling.md` / `standards.md` in the filing folder unless a project
explicitly wants to draft them there.

## Composition-manifest contract (owned here; consumed by `/tracker`)

`submissions` **owns** the `composition-manifest.md` — its template, its authoring,
and its **schema**. `/tracker` is a **read-only consumer**: `generate.py` walks the
manifest to emit `(submission)`-scope rows and two `/best-practices` checks assert
it parses + its pieces resolve. The manifest is **hand-authored from the template**,
not generated from milestones (tracker's "projection of milestone bindings" framing
is conceptual, not mechanical).

Because two parsers read this one file (`render_sidecars.py::parse_manifest` here +
`tracker/scripts/generate.py` there), the **load-bearing skeleton must stay stable**.
Filing-type profiles may vary the *pieces/rows*; they must not rename or drop these
sections/columns:

- **Sections** (H2): `Filing Identification`, `Included Pieces` (with `Required` /
  `Supporting` subsections), `Excluded Pieces`, `Cross-References`, `Reviewer Sign-off`.
- **Included-piece table columns**: `Piece | Path | Purpose | Tracker Row` (or
  `Status` for the strengthener-brief sub-table).
- **Filing Identification rows**: `Filing type`, `Filing ID` (the parser keys on these).

Changing the skeleton is a coordinated change with `/tracker` — not a profile edit.

## Actions

Parse the argument string to pick an action.

### `scaffold <filing> [--device "<name>"]`

Create or fill a filing folder (`qsub` default) under
`docs/project/submissions/<filing>/`. Scaffolding is **filing-type-aware** — the
filing type selects a template **profile** (see the registry below); a `510k`
filing gets the 510(k) document set, not the Q-Sub one.

1. **Read first** (per `readme-before-write`): `docs/project/submissions/README.md`
   and `docs/project/submissions/<filing>/README.md`. Read
   `docs/project/strategies/regulatory-strategy.md` for the D-REG-* decisions the
   content must reference (pathway, predicate, PCCP categories, monitoring).
   **When authoring/scoping PCCP change categories**, read
   [`references/pccp-change-scope-modify-vs-add.md`](references/pccp-change-scope-modify-vs-add.md)
   first — the "modify an existing output vs add a new output" distinction (a new
   output dressed as an improvement of an existing one is a scope over-claim, and
   generally needs its own bounded category + regulator agreement, not an existing
   retrain/refine category). **When scaffolding or authoring a FULL filed PCCP**
   (`pccp` filing, or a `pccp-plan.md` under any filing), also read
   [`references/pccp-full-document-structure.md`](references/pccp-full-document-structure.md)
   first — it is the filing-depth contract (the three components worked *per
   modification*, the required § VII.C Traceability table, the Performance-Evaluation
   **SAP checklist**, and the methodology-complete-vs-value-locked rule that keeps a
   filed PCCP from reading like a Q-Sub summary). **If a Q-Sub was already
   transmitted for this device, the filed PCCP is NOT done until it is reconciled
   against that transmitted Q-Sub** — every Q-Sub commitment (summary position,
   question framing, brief provision) must have a home in the plan, nothing may
   contradict/narrow a transmitted position, and no filed claim may assert an "FDA
   agreement" only requested. The transmitted document sets the floor; the filed one
   may exceed but not fall below it. See the depth-contract reference's **"Reconcile
   the filed PCCP against the transmitted pre-submission"** gate — this is the class
   of defect (under-delivered/contradicted Q-Sub commitments) a per-document lint
   cannot see.
2. **Resolve the profile.** Map `<filing>` to its profile via the **Filing-type
   profiles** registry below (`qsub` → `templates/qsub/`, `510k` → `templates/510k/`,
   `pccp` → `templates/pccp/` (the full filed-PCCP profile — **not** the Q-Sub
   `pccp-summary`; the summary is a Q-Sub-profile doc), `pma` → `templates/pma/`).
   If `<filing>` is not a known type, stop and report the supported set — do not
   silently fall back to the Q-Sub profile (that's the bug this profile model fixes).
   **Altitude choice (PCCP):** a *Q-Sub* wants the abbreviated `pccp-summary.md`
   (+ the worked Modification-Protocol templates); a *filed 510(k)* wants the full
   `pccp-plan.md`. Confirm the intended consumer before building every per-modification
   protocol — see the scope-vs-effort note in the depth-contract reference (the Q-Sub
   questions exist to let FDA prune the category set before full depth is invested).
3. Instantiate the profile's content templates **plus** `templates/_shared/`
   (`composition-manifest.template.md`, `provenance.template.yml`) into the filing
   folder: substitute the `{{PLACEHOLDER}}` tokens from `project.yml` + the strategy
   doc; leave a `[VERIFY]` tag on anything not derivable from a distilled source.
   **Skip files that already exist** (never overwrite authored content).
4. Fill the composition manifest's piece tables from the profile's document set,
   holding the section/column skeleton stable (see **Composition-manifest contract**
   below — `/tracker` parses those sections/columns; varying them breaks it).
5. Create `<filing>/_provenance/` and a `provenance.yml` stub for each content doc
   (schema below). Banner demo projects `_Demo sample data — not for clinical use._`.
6. Author the filed body grounded in the strategy doc and predicate analysis —
   never fabricate K-numbers, FDA contacts, or guidance titles (flag `[VERIFY]`).
   PMA-profile docs are intentionally **placeholder stubs** (`🚧 PLACEHOLDER`); do
   not build them out unless explicitly asked.
7. Run `render` (below) so the console picks the filing up immediately.
8. Report what was created vs skipped, which profile was used, and which
   `[VERIFY]` tags remain.

**Scaffold-time QMS mapping (project-specific — keep out of the registry templates).**
The templates ship project-agnostic defaults; map them to the project's QMS at
scaffold time, never by hard-coding QMS IDs into the templates:

- **Sign-off roster.** The composition-manifest's Reviewer Sign-off ships a generic
  roles-only default (`R&D Lead / Regulatory Affairs / Quality Assurance`, no Author
  row — this matches separation-of-duties and must stay). If the project's QMS
  prescribes a specific submission sign-off chain (e.g. a regulatory-submission WI
  naming RA Specialist → RA Lead → Quality → VP-RA, with Quality attesting the cited
  DHF revisions match the DHF index), populate the roster to that chain when
  scaffolding — and map the manifest doctype to the governing QMS form (if one
  exists) via the project's `.taxonomy.yml` `governing_qms`.
- **Controlled-record transition.** Submission docs are **derived working views**; the
  controlled record is the DHF artifact (and the archived transmitted submission). If
  a project elects to register a submission doc as a controlled record, the scaffold —
  not the template — assigns the doc ID and maps the `version` / `status` frontmatter
  onto the QMS lifecycle vocabulary. `status: placeholder` (PMA stubs) is a skill
  convention, not a QMS status.

### `render [--check]`

Emit the console JSON sidecars from the submission docs.

```bash
python3 .claude/skills/submissions/scripts/render_sidecars.py --root <repo_root>
```

- Writes `docs/project/submissions/.console/submission-index.json` (roll-up) and
  `docs/project/submissions/<filing>/<filing>.submission.json` (per-filing detail).
- `--check` exits non-zero if any sidecar is stale (no writes) — for CI / pre-push.
- Idempotent: re-running with unchanged sources rewrites byte-identical JSON.
- The project-console's **Submission** section has a `POST /submission/render`
  button that shells to this same script.

### `list`

Roll-up of filings + readiness. Read `.console/submission-index.json` (run
`render` first if absent) and print one line per filing: type, status, doc count,
required/supporting/strengthener/excluded counts, and `blocking` (count of
transmission-blocking strengthener briefs not yet ready).

### `scope-lint <qsub-dir> [--transmit-gate]` — Q-Sub scope & reviewer-availability (HARD-RULE check for `qsub` filings)

A Q-Submission is a request for **focused feedback on named questions**, not a full
technical submission. A package assembled from 510(k)-grade DHF artifacts inherits two
defects the leak scrub and the link-based `references` check **cannot** see — regardless
of the source documents:

1. **Reviewer-availability (T1):** filed-body *prose* references to documents the reviewer
   does **not** receive — child SADs, per-module SRAs, threat models, SBOMs, item SRSs,
   internal QMS `SOP-*/FORM-*` IDs. (The `references` lint is link-based; prose references
   are invisible to it.)
2. **🔒-container integrity:** a visible `🔒 END INTERNAL` marker that diverges from its
   `</details>` tag — a marker-keyed or copy-paste strip can then leak deferred/internal
   content (a marker-keyed strip has been observed to nearly ship a batch of deferred questions this way — the check exists to make that failure mode unreachable).

```bash
python3 .claude/skills/submissions/scripts/qsub_scope_lint.py docs/project/submissions/qsub [--transmit-gate] [--json]
```

The linter is **tag-based** (strips 🔒 `<details>…</details>` by *balanced tag*, nesting-safe
— never by the fragile visible marker) and **prose-aware**, and it lints **only what actually
ships** (the transmitted set is read from the cover-letter `## Attachments` list, so a doc
moved to the 510(k) drops off the worklist automatically). Seven checks:

- **C1 container-integrity** (BLOCK) — `<details>`/`</details>` balanced; every `🔒 END INTERNAL` adjacent to a `</details>`.
- **C2 reference-availability** (WARN → BLOCK under `--transmit-gate`) — filed-body prose references to non-transmitted doctypes, minus the forward-reference allowlist ("… part of the 510(k) …", "… on request").
- **C3 blocking-brief-anchor** (BLOCK) — a transmission-blocking brief must anchor an **active** (non-`DQ-*`) question.
- **C4 manifest ⇄ cover-letter reconciliation** (BLOCK / WARN) — section-aware three-state match (`transmitted` / `on-request` / `grounding-only`, via a `### Grounding — not transmitted` manifest sub-bucket) on path-aware doc identity; flags a transmitted manifest piece not attached, an attachment with no manifest entry, or an unmarked grounding row.
- **C5 altitude** (WARN) — a raw controlled DHF doc (a `_confluence/**` path) attached with no Q-Sub scoping note/extract adjacent to its attachment line.
- **C6 effective-ask-count** (WARN; `--ask-ceiling`, default 10) — the FDA Q-Sub guidance heuristic is "no more than **7-10 questions (including sub-questions)**". The failure mode: a deliberate primary-question trim executes, then later scope additions **embed** new asks inside existing question bodies (a bolded `**Question**: Does FDA agree…` paragraph, another conditional follow-up) — the primary count holds while the *effective* ask count silently re-inflates, and nothing watches it. Counts interrogative sentences per transmitted question section of the **filed body**; WARNs on the package total over the ceiling and on any single question packing ≥4 asks (dependent asks invite fragmented FDA feedback — label them as sub-questions so each is individually answerable). Heuristic → always WARN, never BLOCK (the guidance says "typically", and deep-single-topic packages are explicitly sanctioned).
- **C7 ambiguous-commitment-terminology** (WARN) — bare **"IFU"** inside a filed-body **commitment or boundary phrase** ("no IFU change", "IFU unchanged", "within-IFU", "IFU update/change procedure", "existing IFU"). "IFU" has two industry-standard expansions — **Indications for Use** (the cleared-indication statement; changing it routes to a new 510(k) per 21 CFR 807.81(a)(3)) and **Instructions for Use** (the labeling document; its updates routinely accompany UI/software changes and do **not** negate PCCP / letter-to-file eligibility). A commitment written with the bare acronym silently promises the wrong thing to one of the two readers — "no IFU change" on a UI-change category is *unrealistic* under one reading and *load-bearing* under the other. This exact confusion has produced a fix-then-counter-fix cycle in a real package (a reviewer pass corrected the acronym the wrong way before a second pass corrected the correction). Lines that spell out the expansion (or name the labeling document, e.g. DFU) on the same line pass; casual non-commitment mentions ("the proposed IFU") are not flagged.

WARN advisory by default; `--transmit-gate` makes any BLOCK a non-zero exit. **Run before any `qsub` transmit.**

### `gen-sad-extract` — the Q-Sub SAD extract (F-11 tooling)

The canonical System SAD is a full 510(k) technical-file artifact. Rather than attach it raw
(C5) or hand-maintain a divergent copy, **derive** a Q-Sub-scoped projection:

```bash
python3 .claude/skills/submissions/scripts/gen_qsub_sad_extract.py \
  --sad <canonical-SAD.md> --out <qsub-dir>/system-architecture-overview.qsub.md \
  --sections 2,4,5,8.1,8.3,9.3,10.2 --title "System Architecture Overview (Q-Sub extract)" --preface "…"
```

Selects the allowlisted section set, strips 🔒 `<details>` containers (by balanced tag) and
child-SAD tables, **reframes prose child-SAD/SRS references to 510(k)-forward form**, and stamps
a `GENERATED — do not hand-edit` banner + Q-Sub scoping preface. The `--sections` allowlist is a
CLI arg (project-agnostic; the SAD's own numbering). Attach the generated `*.qsub.md` in place of
the raw SAD (cover-letter Attachment; manifest lists the extract as transmitted + the canonical
as grounding-source). Regenerate when the canonical SAD changes.

### `check <filing-dir> [--transmit-gate]` — cross-document "seam" consistency

`scope-lint`, the leak scrub, and the authoring lint each validate one document **in
isolation**. A distinct class of defect survives all of them because it lives in the **seam
between two documents** — a pointer in one document that *describes*, *numbers*, or *reaches
for* another. Each side is internally clean; only the pair is wrong. Full principle + the
predicate/SE tiering model: [`references/pre-sub-package-consistency.md`](references/pre-sub-package-consistency.md).

> **Scope note — S1–S4 are *within-package* seams; the *cross-filing* Q-Sub→PCCP/510(k)
> reconciliation is NOT covered here** (no script yet). A filed PCCP that under-delivers or
> contradicts a commitment made in the already-**transmitted** Q-Sub is a distinct, high-cost
> defect class (deficiency-letter fodder) that this `check` does not catch. Run the manual
> **"Reconcile the filed PCCP against the transmitted pre-submission"** walk from
> [`references/pccp-full-document-structure.md`](references/pccp-full-document-structure.md)
> before any filed PCCP/510(k) is declared done — best executed as a `quality-engineering` +
> `regulatory-affairs` agent pass over (transmitted Q-Sub set) × (filed plan). Automating it as
> an S5 cross-filing check is a tracked future enhancement.

```bash
python3 .claude/skills/submissions/scripts/check_package_consistency.py docs/project/submissions/qsub [--transmit-gate] [--json]
```

Project-agnostic (transmitted set + numbered lists read from the package's own cover letter;
the filed-body scans cover only what ships — internal assembly artifacts are excluded). Six checks:

- **S1 cross-reference accuracy** (WARN) — a filed-body pointer that calls a linked package doc the "full/complete/comprehensive" predicate/SE analysis while that target self-describes as an **abbreviated/summary** treatment (tier confusion). Deferral and contrastive sentences ("the full analysis is a 510(k) deliverable"; "abbreviated … gates full analysis") are exempt.
- **S2 attachment-number consistency** (FAIL / WARN) — a prose "attachment N" whose number matches **none** of the package's numbered lists for the doc it links (FAIL), plus per-list contiguity (gaps/dupes → FAIL); two lists numbering the same doc by a **uniform** offset (one counts the cover letter, the other doesn't) collapse to one WARN, a **non-uniform** offset lists each drift.
- **S3 folder-boundary compliance** (FAIL / WARN) — a **transmitted** attachment whose path escapes the filing folder (`../`) with no on-request/internal/grounding disposition on its line (FAIL); a filed-body `../../` link reaching outside the filing folder (WARN — confirm grounding-only).
- **S4 stable-key liveness** (WARN) — an *anchor/support* declaration (in a transmitted doc or the manifest) that names a stable question key (`QK-*`) which the questions master map has since **deferred or dropped**. This is the **semantic seam** the structural checks (S1–S3) cannot see: a "spine" fact (a question's number or transmit status) changes in its home doc, and sibling docs that declare they anchor/support it are not updated in lockstep — the root cause of recurring "stale reference" drift. Reads the `QK → display → transmitted?` master map from `fda-questions.md`; disposition-guarded (a "QK-X was deferred → DQ-N" note is not flagged) and skips changelog/metadata rows. Prefer stable `QK-*` keys over bare display numbers (`Q1.3`) in apparatus — display numbers churn on every renumber; the master map is the drift-resistant anchor.
- **S5 question↔support matrix** (FAIL / WARN + informational matrix) — mechanizes the sponsor-level question "does each transmitted question have distinct supporting substance, and does every attachment earn its place?" Per transmitted question: which attachments mention/support it (emitted as a matrix in text + JSON — the generated per-question support map, replacing a hand audit). **FAIL** on an attachment that supports no transmitted question AND carries no `background` disposition on its cover-letter row — the guidance's "extraneous information" risk (guidance-**required** content — cover letter, device description, IFU/labeling, predicate comparison — is exempt: it earns its place without anchoring a question). **WARN** on a transmitted question no attachment supports (confirm self-contained by design).
- **S6 enumeration-completeness** (WARN) — a package deliberately restates enumerable label sets (change-category labels, rule sets) across transmitted docs for **reviewer ergonomics**; the cost of that duplication is **lockstep drift, not pages** — the family grows in its home doc (a new category label) and a sibling doc's recap silently stays at the old span (the classic: a cover-letter recap enumerating categories 1..6 after the package grew a 7th). Deliberately narrow to stay high-signal: single-letter label families in a category-context line only (separates category labels from same-letter collisions like a security diagram's interface labels); a line counts as an *enumeration* only with ≥4 separately-written labels (a range like `C1–C7` is ONE token — naming a span is not recapping members); "e.g./such as" partial lists exempt. **Checks consistency between duplicate instances; never asks for deduplication** — reader-serving duplication is a deliberate authoring choice (duplication is fine; drift is not).

WARN advisory by default; `--transmit-gate` makes any FAIL a non-zero (2) exit. **Run before any transmit**, alongside `scope-lint`. This check earned its keep on the seam defects that a per-document lint cannot see: a summary attachment described as the "full" analysis (S1), a prose "attachment N" off-by-one against the contents table (S2), a transmitted piece sourced from an out-of-package folder (S3), a filed/apparatus claim to anchor a since-deferred question (S4 — found in the cyber brief, the cover letter, and the separation argument after a question-set renumber), and a cover-letter question recap that omitted a later-added change category while the questions doc carried it (S6 — regression-verified against that exact historical defect).

### `provenance {check,stamp}` — source-drift reconciliation + claim grounding

The seam checks above catch *reference* drift. A **different** class is **reproduced-content drift**: a filed document keeps a self-contained summary of an upstream source (a device description reproduces the system-architecture module tables; readability requires this — the reviewer must not be sent out to hundreds of pages, per **W12.1**), and the source later changes while the copy silently does not. You cannot fix this by "just referencing the source" — that sacrifices readability and reviewer confidence. You fix it by **pinning the source's git blob SHA** in the document's provenance sidecar and flagging when the source moves on.

A **third** class — the one drift-pinning alone cannot catch — is an **ungrounded claim**: a factual assertion *about an external primary source* (a predicate/cleared-filing PDF, a De Novo/PMA summary) that the source does not actually support, or that was written from a sibling summary while the primary source was never opened. `check` catches this when the claim carries structured grounding (`source_path` + `source_page` + verbatim `quote`) by verifying the quote resolves in the pinned source. See `references/claim-grounding.md`.

```bash
python3 .claude/skills/submissions/scripts/provenance_reconcile.py check docs/project/submissions/qsub [--json] [--transmit-gate]
python3 .claude/skills/submissions/scripts/provenance_reconcile.py stamp <doc-basename>   # after reconciling a doc against its sources
```

- Each `_provenance/<doc>.provenance.yml` already records the upstream sources a doc reproduces/summarizes (`path` + `sections`/`decisions`/`terms` + `how_used`). **`stamp`** pins each *content* source (an entry naming `sections`/`decisions`/`terms`; framing files like a root README/CLAUDE are skipped) to its `git hash-object` SHA in a **generated** `<doc>.sources-lock.json` beside the sidecar — kept separate so the churny hashes never force a fragile edit of the comment-carrying human sidecar.
- **`check`** compares each pinned SHA against the source's current SHA and emits: **drift** (source changed since the doc was last reconciled — re-check the derived content, with the `how_used` note printed so you know *what* to re-check, then re-stamp); **unbaselined** (source not pinned yet); **unresolved-path** (a recorded source path no longer resolves — the source moved or its tree was retired, i.e. the provenance itself has rotted); **malformed-yaml** (sidecar unparseable). It also runs **claim grounding**: **ungrounded-claim** (a `claims_to_source[]` row with `source_path`+`quote` whose quote does not resolve in the source), **unresolved-source** (its `source_path` doesn't resolve), **grounding-skipped** (a NOTE when `pypdf` is absent so PDF quotes can't be verified).
- **Workflow:** after reconciling a document against its sources (or authoring a new version), run `stamp <doc>`. Run `check` before transmit and whenever a canonical source (e.g., the system SAD) changes — `check` is the trigger that turns a silent source edit into an explicit "re-reconcile these documents" worklist. `--transmit-gate` makes **drift** *and* **ungrounded-claim** a non-zero (2) exit.
- This catches two classes a reference check can't — **(a)** the SAD § 4 processing-module cell narrowing to "single-modality input only" while a device-description copy still said "multi-modality input" (drift); **(b)** a predicate-comparison stating a predicate's software level from a sibling `.md` while the cleared-filing PDF that would confirm it sat un-consulted in the repo (ungrounded-claim). Keep the content in the doc (readability); let the hashes watch the source **and** the claims.

## Console JSON contract (`schema_version: "1.0"`)

`render` is the **producer**; the project-console `submission/` package is the
**consumer**. Neither side parses the other's internals — only this shape.

**`.console/submission-index.json`**
```json
{ "schema_version": "1.0",
  "filings": [ { "id": "qsub", "type": "Q-Sub (Pre-Submission)", "title": "...",
                 "status": "drafting", "folder": "...", "manifest": "...",
                 "counts": {"required": N, "supporting": M, "strengtheners": S,
                            "excluded": K, "docs": D, "questions": Q},
                 "blocking": B, "default_advisor": "regulatory-affairs" } ] }
```

**`<filing>/<filing>.submission.json`**
```json
{ "schema_version": "1.0",
  "meta": { "id", "type", "title", "device", "filing_id", "milestone", "dhfs",
            "status", "folder", "manifest_md", "default_advisor" },
  "pieces": { "required": [{name,path,purpose,tracker_row}],
              "supporting": [...],
              "strengtheners": [{name,path,purpose,status,blocking}],
              "excluded": [{name,reason}] },
  "documents": [ {id,title,kind,path,version,status,summary,
                  sections:[{title,label}], provenance:{agent,task,version,claims,open_gaps}} ],
  "questions": [ {id,topic,subject,position,label} ],
  "sign_off": [ {role,name,date,status} ],
  "counts": {...}, "blocking": B }
```

The console renders each document's markdown body inline (via its own renderer)
in a tabbed viewer; pieces / questions / sign-off / counts come from the sidecar;
the Ask-the-advisor drawer defaults to `regulatory-affairs` with the filing's
compact context as grounding.

## provenance sidecar schema (`_provenance/<doc>.provenance.yml`)

```yaml
doc: docs/project/submissions/<filing>/<doc>.md
version: v0.1
date: YYYY-MM-DD
agent: regulatory-affairs
task: <person>/NNN
sources_consulted:
  - path: <repo-relative>
    sections: ["§ ..."]
    how_used: <plain English>
fda_visible_references: [<transmitted docs + guidance titles>]
claims_to_source:
  - claim: "<exact claim>"
    source: "<doc/section>"           # free-text (legacy) OR add structured grounding ↓
    source_path: <repo-relative primary source>   # optional — e.g. a cleared-filing PDF
    source_page: <int>                             # optional — page for PDF sources
    quote: "<verbatim substring of the source supporting the claim>"  # optional
open_gaps: ["<placeholder / pending item>"]
notes: ["<implementation note>"]
```

**Claim grounding (optional, per claim).** When a claim is a factual assertion *about
an external primary source* (a predicate/cleared-filing PDF, a De Novo/PMA summary), pin
it structurally: add `source_path` + `source_page` + a verbatim `quote`. `provenance check`
then verifies the quote resolves in that source snapshot and flags **`ungrounded-claim`**
(transmit-blocking) if not. This is the gate that catches a fact written from a sibling
summary while the primary source sat in `sources_not_consulted` — see the **claim-grounding
rule** (`references/claim-grounding.md`). A factual claim about a primary source belongs in
`sources_consulted` **with a grounding quote**, never only in `sources_not_consulted`.

## eStar format layer

The **format/packaging** counterpart to the content authoring above: it maps the
submission content docs + `composition-manifest.md` onto the FDA **eSTAR**
electronic-submission template — the binding outer structure of a 510(k) (and
De Novo/PMA). This skill owns the eStar *mapping, admissibility linting, and
completion guide*; it does **not** fill the FDA form itself.

**Hard reality (why we don't auto-fill the PDF).** The FDA eSTAR is a **dynamic
XFA + JavaScript Adobe form**, not a plain AcroForm — every section, attachment
slot, and field lives in the XFA `template` packet, and the conditional logic +
"eSTAR Complete" self-check run only inside Acrobat Pro. Open-source PDF
libraries cannot reliably fill or validate it. So the automatable core is:
derive the structure, prepare admissible attachments (via `/docflow`), and emit
a completion guide + linter. Final field entry, the green-banner verify, and
CDRH-Portal transmission stay human-in-Acrobat. (An Acrobat-Pro fill add-on is a
possible future stretch — see the owning task.)

**Version discipline.** eSTAR revs often (build target = **nIVD eSTAR v7.0**,
mandatory 2026-08-03). Everything derived is **version-pinned**; re-derive when a
new template supersedes.

### Setup (this skill is the guide/setup owner)

The eStar tooling needs `pikepdf` (a compiled QPDF binding), which a
PEP-668-managed system Python refuses to install globally. The installation lives
in the project's **`tools/estar/`** (committed `requirements.txt` + `bootstrap.sh`;
gitignored `.venv/`) — same pattern as `tools/file-locator-mcp/`.

```bash
bash tools/estar/bootstrap.sh          # idempotent: builds tools/estar/.venv + installs deps
```

### `extract-sectionmap [<template.pdf>]`

(Re)derive the version-pinned, machine-readable **section-map** from the eSTAR
template's XFA layer — the reference model the crosswalk/linter key on.

```bash
tools/estar/.venv/bin/python .claude/skills/submissions/scripts/estar_extract_sectionmap.py \
  .claude/skills/medtech-docs/references/fda-guidance/templates/nIVD_eSTAR_7-0.pdf \
  --template-id nIVD_eSTAR --version v7.0 \
  --json .claude/skills/submissions/data/estar/sectionmap-nivd-v7.0.json \
  --outline .claude/skills/submissions/data/estar/sectionmap-nivd-v7.0.outline.md
```

- **Section-map** (`data/estar/sectionmap-<template>-<ver>.json` + `.outline.md`)
  is **project-agnostic FDA structure** (sections → subsections → attachment
  slots → fields) and lives in the skill as reference data. It is **not** cited as
  grounding text — the eSTAR *guidance* triplet in `references/fda-guidance/` is.
- **Template binaries** live under
  `.claude/skills/medtech-docs/references/fda-guidance/templates/` (version-pinned).
- **The filled crosswalk** — each eStar section/slot ↔ its manifest piece + repo
  source + structured answer — is the **project instance** and lives under
  `docs/project/submissions/510k/` (never in the skill). The `docs/external`
  applicability report (`fda-guidance/510k-estar.md`) references the section-map
  as its derived source and carries the applicability narrative.

### `lint [--attachments <dir>] [--transmit-gate]`

Pre-flight the package for eSTAR admissibility + coverage — **advisory by
default**, a **hard gate** with `--transmit-gate` (exit non-zero on any BLOCK).
Template-parameterized via `--sectionmap` (defaults to nIVD eSTAR v7.0), so the
same linter serves PreSTAR (Q-Sub) by pointing at a PreSTAR section-map.

```bash
tools/estar/.venv/bin/python .claude/skills/submissions/scripts/estar_lint.py \
  --crosswalk docs/project/submissions/510k/estar-crosswalk.md \
  [--attachments <dir-of-prepared-PDF-exhibits>] [--transmit-gate] [--json]
```

Checks: **structure** (section-map loads, version-pinned) · **attachments**
(each exhibit PDF is admissible — PDF 1.4–1.7/PDF-A, no encryption, no live
form/XFA, bookmarks on long docs, safe filename, ≤1 GB) · **quality**
(per the FDA *PDF Specifications* v4.1 — the project's applicability file under
`docs/external/fda-guidance/` records adoption scope: Letter page size;
**per-font-descriptor embedding**; standard-font-set notice (spec Table 1);
**minimum text size ≥9pt** (spec: 9–12pt, tables 9–10pt) scanned from
content-stream `Tf` operators; **prohibited content** — JavaScript + embedded
files BLOCK, non-link annotations WARN (spec § VERSION); **lowercase filenames**
(spec § NAMING); **no-emoji HARD RULE** — emoji-font detection, WARN advisory /
**BLOCK under `--transmit-gate`**) · **coverage** (in-scope crosswalk sections
have a ready source; applicable slots have a prepared exhibit) · **accuracy**
(the § A structured-answer set is complete + `[VERIFY]`-free — a
technical-screening matcher) · **references** (assembly-manifest hygiene:
resolved cross-refs counted; refs to docs NOT in the package reported for RA
disposition — WARN advisory, **BLOCK under `--transmit-gate`**: zero
undispositioned references at transmit time) · **manifest coverage** (every
REQUIRED composition-manifest piece — formal FDA deliverables + transmission-
blocking briefs — must be in the assembled package or recorded as deliberately
structured-only; the grounding-only "supporting technical architecture" rows
are exempt by design. WARN advisory / **BLOCK under `--transmit-gate`** — the
systematic catch for "the cover letter cites a Required doc that never got
attached") · **gaps** (open § C items). It **cannot** reproduce eSTAR's
in-Acrobat "eSTAR Complete" JS verify — it is the pre-flight *before* a human
opens Acrobat.

> **Regulator format basis** — the eSTAR guidance governs *structure only*;
> typography is NOT mandated. The formatting layer is the FDA **PDF
> Specifications** (Technical Specifications Document v4.1, Sep 2016 —
> nonbinding, eCTD-anchored; adopt via a project applicability file under
> `docs/external/fda-guidance/pdf-specifications.md` and cite the registry
> full text). Its rules (fonts Table 1 / 9–12pt sizes, margins, prohibited
> content, naming, ≥5-page bookmarks) are enforced at the producer by
> `/docflow export`'s house-style pass and verified here. Table geometry
> (margin-to-margin, content-weighted columns, header repeat) is enforced at
> the producer, not re-derived from the PDF.

> **eSTAR vs PreSTAR** — the 510(k)+PCCP is **one eSTAR** (the PCCP is a section
> inside it, not a separate template/submission), governed by the *final* 510(k)
> eSTAR guidance and **mandatory**. The Q-Sub uses the **separate PreSTAR**
> template under a *different, draft* guidance and is **voluntary**. Same XFA
> format family + admissibility rules (so this tooling generalizes); different
> section-map + crosswalk per template.

### `completion-guide`

Since open tooling cannot fill the XFA form, generate the **completion guide** —
the exact structured answers a human types into Acrobat + the attachment→source
mapping — in two forms: a machine-readable JSON (shaped to feed a future
Acrobat-Pro XFA-dataset import) and a human Acrobat-entry checklist (markdown).

```bash
tools/estar/.venv/bin/python .claude/skills/submissions/scripts/estar_completion_guide.py \
  --sectionmap .claude/skills/submissions/data/estar/sectionmap-nivd-v7.0.json \
  --crosswalk  docs/project/submissions/510k/estar-crosswalk.md \
  --out-json   docs/project/submissions/510k/estar-completion-guide.json \
  --out-md     docs/project/submissions/510k/estar-completion-guide.md
```

Reads the crosswalk (§ A answers, § B applicable sections + sources, § C gaps)
and the section-map (actual slot names per section) → emits: **§1 structured
answers to enter**, **§2 attachments to prepare + load** (source → slot(s), via
`/docflow`), **§3 N/A sections** (answer "No", never blank), **§4 `[VERIFY]`
items to resolve**, **§5 open gaps**. The guide is **generated** (project
instance under `docs/project/submissions/<filing>/`) — re-run, don't hand-edit.
Template-parameterized: swap `--sectionmap`/`--crosswalk` for the PreSTAR/Q-Sub.

### `assemble`

One-command package dry-run: gather the crosswalk's attachment sources, strip
internal tiers, render **draft exhibit PDFs**, lint, and emit the completion
guide — all into `<filing>/_estar/`.

```bash
tools/estar/.venv/bin/python .claude/skills/submissions/scripts/estar_assemble.py \
  --crosswalk  docs/project/submissions/qsub/prestar-crosswalk.md \
  --sectionmap .claude/skills/submissions/data/estar/sectionmap-prestar-v3.0.json \
  --header     "<Sponsor legal name> - {title}" \
  --out        docs/project/submissions/qsub/_estar   [--transmit-gate]
```

- **Source selection**: only crosswalk § B rows whose **Mode declares an
  attachment** (`Attachment`/📎) yield exhibits — `Structured`-only rows are
  typed into the form, never attached. The "Supporting briefs" paragraph's
  linked docs attach as Questions context. Internal-not-transmitted docs must
  not be linked as attach sources in the crosswalk.
- **Internal-tier strip** (the filed body is exactly what FDA sees): HTML
  comments, `🔒 INTERNAL` `<details>` containers, and 🔒-marked table columns
  are removed; per-doc strip stats land in `assembly-manifest.json`. The strip
  is **fence-aware end-to-end** — containers can hold fenced code and fenced
  examples can hold container-like text; a naive regex strip eats a fence
  delimiter and the rest of the document renders as one raw-markdown code
  block.
- **Document-reference resolution**: links to docs IN the package become
  textual cross-refs "(Attachment NNN)" (cross-file PDF links break inside
  eSTAR slots; attachment numbers don't); links to repo docs NOT in the
  package are dropped (text kept) and **reported** — assembly manifest +
  the lint `references` check — so RA dispositions each: mark it 🔒 INTERNAL
  in the source md, or add the doc to the package. Same-doc `#anchors` and
  http/mailto links survive; image paths are absolutized so figures embed.
- **View-output check** (after every assemble): `estar_viewcheck.py
  --attachments <dir>` emits a prioritized worklist of pages to eyeball —
  ASCII-art/code pages (mono-font usage), the smallest-text page, first/last
  page per exhibit. Automated lint can't judge how a page *looks*; the
  reviewing agent opens each listed page (PDF page reader) and verifies art
  integrity, table breaks, and layout before the package is called done.
- **Formal-exhibit symbol policy (HARD RULE — filed exhibits never contain
  emoji)**: emoji/dingbats are transliterated (✅→Yes, ⛔→N/A, ⚠→[!], …) or
  dropped — they pull unembeddable bitmap fonts (AppleColorEmoji) into the PDF
  and read as informal. Real typographic characters (→, ≥, ·) are kept —
  common serif fonts carry them. The `lint` `quality` group enforces the rule
  (WARN advisory; **BLOCK under `--transmit-gate`**), so exhibits produced
  outside `assemble` are caught too.
- **Rendering** (`--renderer auto|docflow|fpdf2`, default auto): prefers
  **`/docflow export`** (pandoc → DOCX → LibreOffice → PDF — real typesetting,
  embedded fonts, heading outline as bookmarks) when pandoc+soffice are
  present; falls back to the built-in fpdf2 renderer otherwise. Either way:
  eCopy-style numbered names (`NNN_<Section>_<slug>.pdf`), PDF 1.7 — designed
  to pass the `lint` admissibility checks.
- **DRAFT exhibits**: these renders are for package dry-runs, linting, and
  internal review; the transmission-time conversion of controlled documents
  follows the project's formal-doc/QMS process.
- Output folder contents: `attachments/`, `assembly-manifest.json`,
  `<template>-completion-guide.{json,md}`, `lint-report.json` (+ human lint
  summary on stdout; `--transmit-gate` makes BLOCK findings exit non-zero).

## Notes

- **Never fabricate** standard / clinical / regulatory content. Anything not
  derivable from a distilled source in `docs/external/` or
  `.claude/skills/medtech-docs/references/` is flagged `[VERIFY]` inline.
- Author into the canonical doc; do not create satellite files.
- Demo content carries `_Demo sample data — not for clinical use._` near the top.

## Best Practices
See [README.md](README.md) — consumed by `/best-practices` audit.

## Changelog
See [README.md](README.md) for version history.
