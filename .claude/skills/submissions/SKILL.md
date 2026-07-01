---
name: submissions
description: |
  Author, scaffold, and render an FDA submission package (Q-Sub / 510(k) / PCCP / PMA-placeholder) for a medtech project — the regulatory-facing document set under `docs/project/submissions/<filing>/` plus the JSON sidecars the project-console **Submission** section consumes. Scaffolding is **filing-type-aware**: each filing type has a template profile that lays down its characteristic document set (Q-Sub questions/PCCP-summary vs 510(k) substantial-equivalence/predicate-comparison/IFU vs PMA SSED/clinical placeholders). Owns the three-tier document model (HTML frontmatter metadata → `🔒 INTERNAL` working apparatus → filed body transmitted to FDA, using the 📤/📝/⏸️/📖 scope labels), the per-doc `_provenance/*.provenance.yml` audit sidecars, and the `composition-manifest.md` package-assembly artifact (Required / Supporting / strengthener-brief / Excluded buckets with transmission-blocking gates) — including its section/column schema, which `/tracker` consumes read-only.

  TRIGGER when the user wants to **scaffold, build, author, seed, generate, assemble, or render** a Q-Submission / pre-submission / 510(k) / PCCP / PMA **content package** — phrasings include: "scaffold the Q-Sub package", "set up the qsub documents", "scaffold the 510(k)", "create the FDA questions doc", "build the cover letter / device description / intended-use / substantial-equivalence / PCCP summary", "seed submission content", "assemble the composition manifest", "render the submission console view", "refresh the submission sidecars", "what's in the Q-Sub package", "is the qsub package ready to transmit". Also fire on any edit/write under `docs/project/submissions/<filing>/` content docs or `_provenance/`.

  Sibling boundaries — this skill owns submission **content** + its console sidecars. It is NOT `/tracker` (deliverable × phase readiness dashboard), NOT `/change-control` (publish to Confluence/Windchill), NOT `/medtech-docs` (DHF scaffolding), NOT `/dhf-manifest` (deliverable-coverage projection). When a fact is canonical elsewhere (regulatory-strategy.md D-REG-* blocks, the system SAD, project.yml), submission docs reference it — they do not redeclare it.
version: 2
updated: 2026-06-15
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
   (e.g. `QK-PCCP-PREOP-AI`) that **never renumbers**. The slug is semantic so it
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

## Supporting Files

| File | Purpose |
|---|---|
| `scripts/render_sidecars.py` | Producer of the console JSON contract (see below). Stdlib only. |
| `templates/_shared/` | Filing-agnostic templates: `composition-manifest.template.md` (the manifest skeleton — its section/column contract is documented below) + `provenance.template.yml`. |
| `templates/qsub/` | Q-Sub profile: cover letter, device description, intended-use, FDA questions, PCCP summary. |
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
| `pccp` | PCCP | `templates/qsub/` (PCCP subset) | PCCP summary + cover letter (the PCCP rides inside a Q-Sub/510(k); a standalone `pccp` filing reuses the Q-Sub profile's PCCP-relevant docs) |
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
2. **Resolve the profile.** Map `<filing>` to its profile via the **Filing-type
   profiles** registry below (`qsub` → `templates/qsub/`, `510k` → `templates/510k/`,
   `pccp` → `templates/qsub/` PCCP-subset, `pma` → `templates/pma/`). If `<filing>`
   is not a known type, stop and report the supported set — do not silently fall
   back to the Q-Sub profile (that's the bug this profile model fixes).
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
    source: "<doc/section>"
open_gaps: ["<placeholder / pending item>"]
notes: ["<implementation note>"]
```

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
