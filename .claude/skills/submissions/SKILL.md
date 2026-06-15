---
name: submissions
description: |
  Author, scaffold, and render an FDA submission package (Q-Sub / 510(k) / PCCP) for a medtech project — the regulatory-facing document set under `docs/project/submissions/<filing>/` plus the JSON sidecars the project-console **Submission** section consumes. Owns the three-tier document model (HTML frontmatter metadata → `🔒 INTERNAL` working apparatus → filed body transmitted to FDA, using the 📤/📝/⏸️/📖 scope labels), the per-doc `_provenance/*.provenance.yml` audit sidecars, and the `composition-manifest.md` package-assembly artifact (Required / Supporting / strengthener-brief / Excluded buckets with transmission-blocking gates).

  TRIGGER when the user wants to **scaffold, build, author, seed, generate, assemble, or render** a Q-Submission / pre-submission / 510(k) / PCCP **content package** — phrasings include: "scaffold the Q-Sub package", "set up the qsub documents", "create the FDA questions doc", "build the cover letter / device description / intended-use / PCCP summary", "seed submission content", "assemble the composition manifest", "render the submission console view", "refresh the submission sidecars", "what's in the Q-Sub package", "is the qsub package ready to transmit". Also fire on any edit/write under `docs/project/submissions/<filing>/` content docs or `_provenance/`.

  Sibling boundaries — this skill owns submission **content** + its console sidecars. It is NOT `/tracker` (deliverable × phase readiness dashboard), NOT `/change-control` (publish to Confluence/Windchill), NOT `/medtech-docs` (DHF scaffolding), NOT `/dhf-manifest` (deliverable-coverage projection). When a fact is canonical elsewhere (regulatory-strategy.md D-REG-* blocks, the system SAD, project.yml), submission docs reference it — they do not redeclare it.
version: 1
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
| `docs/project/submissions/` tree | All actions | `/medtech-docs init` (scaffolds qsub/510k/pccp) |
| `docs/project/strategies/regulatory-strategy.md` | `scaffold` content grounding (D-REG-* decisions) | `/strategy` authoring |
| `python3` (stdlib only) | `render` | Already present |

If a required input is missing, report exactly what's missing and stop.

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

**Grounding rule:** submission docs reference canonical facts (classifications,
predicate K-numbers, change categories) from `regulatory-strategy.md` D-REG-*
blocks, the system SAD, and `project.yml` — they do not restate them as new
facts (per `audit-wiring-before-adding-fields` and `claude-md-references`). Demo
projects banner every doc `_Demo sample data — not for clinical use._`.

## Supporting Files

| File | Purpose |
|---|---|
| `scripts/render_sidecars.py` | Producer of the console JSON contract (see below). Stdlib only. |
| `templates/` | Starter content docs (`*.md`) + `provenance.template.yml` + `composition-manifest.template.md`, modeled on a real Q-Sub package. `{{PLACEHOLDER}}` tokens are filled at scaffold time. |
| `README.md` | Design rationale, Best Practices (consumed by `/best-practices`), Changelog. |

## Actions

Parse the argument string to pick an action.

### `scaffold <filing> [--device "<name>"]`

Create or fill a filing folder (`qsub` default) under
`docs/project/submissions/<filing>/` from `templates/`.

1. **Read first** (per `readme-before-write`): `docs/project/submissions/README.md`
   and `docs/project/submissions/<filing>/README.md`. Read
   `docs/project/strategies/regulatory-strategy.md` for the D-REG-* decisions the
   content must reference (pathway, predicate, PCCP categories, monitoring).
2. For each template in `templates/` not already present in the filing folder,
   instantiate it: substitute `{{DEVICE}}`, `{{FILING_ID}}`, `{{PATHWAY}}`,
   `{{PREDICATE}}`, `{{DATE}}` from `project.yml` + the strategy doc; leave a
   `[VERIFY]` tag on anything not derivable from a distilled source. **Skip files
   that already exist** (never overwrite authored content).
3. Create `<filing>/_provenance/` and a `provenance.yml` stub for each content doc
   (schema below). Banner demo projects `_Demo sample data — not for clinical use._`.
4. Author the filed body grounded in the strategy doc and predicate analysis —
   never fabricate K-numbers, FDA contacts, or guidance titles (flag `[VERIFY]`).
5. Run `render` (below) so the console picks the filing up immediately.
6. Report what was created vs skipped, and which `[VERIFY]` tags remain.

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
