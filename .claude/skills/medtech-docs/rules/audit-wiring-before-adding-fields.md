# Rule: Audit Existing Wiring Before Adding Pointers (HARD RULE)

A medtech project's structural facts — where artifacts live, how DHFs are organized, what each module is classified as, which milestones bind which evidence — are encoded in a **wiring layer** of yaml/config files, not in prose. Before authoring a metadata field, a schema entry, or doc content that states a structural fact, **audit the wiring layer first** and reference what is already there.

The principle in one line: a doc that **references** the wiring survives structural change; a doc that **redeclares** a structural fact silently rots when the structure moves — and the rot surfaces during audit prep, when paths no longer match what was claimed months ago.

## Where the wiring lives

| Source | What it encodes |
|---|---|
| `project.yml` `dhfs[]` | DHF roster, paths, `role`, `classification`, scope |
| `project.yml dhfs[].path` | DHF root on disk |
| `project.yml dhfs[].evidence:` | Typed pointers to load-bearing artifacts |
| `project.yml evidence_layout` | Layer-name → folder mapping for fixed-name artifacts (DTM, threat model, uFMEA) |
| `project.yml strategy_domains` | Strategy domain registry |
| `project.yml tracker:` | Tracker config — status vocabulary, coverage thresholds, row-id schema |
| milestone yamls / taxonomy yamls / `trace-matrix.yml` | Per-milestone posture, folder-name → role maps, trace-matrix layer config (when present) |

Not every project has every file — but the rule is the same: if a config field already encodes the fact, **that field is the source of truth.**

## How to apply

Before adding any new metadata field, schema entry, or structural prose:

1. **Grep `project.yml`** for the concept you are about to encode. If a field already represents it, use the field — do not redeclare.
2. **Check sibling configs** — milestone yamls, taxonomy yamls, `evidence_layout` layers.
3. **Read adjacent skills' SKILL.md** config sections — they document fields downstream skills can reuse.
4. **If the fact is in the wiring**, route the feature through a *lookup* against existing config, not a new field.
5. **If the fact is genuinely missing**, add it *once* — as a project-config field with a sane default — never as repeated per-row metadata.

## Examples

❌ **Redeclaring a path in prose.** Writing in a doc: "the PCA device DHF lives at `docs/project/dhfs/pca-device/`."
✅ `project.yml dhfs[].path` already holds it — link or derive it. A folder rename turns the sentence into a silent lie nobody catches until audit.

❌ **A field on every row.** Adding `dhf_folder: docs/.../design-controls` to every tracker obligation row.
✅ The folder is computable from `(DHF, role)` plus existing config. Add **one lookup**, not the same path copied onto every row.

❌ **A classification restated in narrative.** Writing "Module X is Class II, IEC 62304 Class C, non-SaMD" as a hard statement in a doc.
✅ `project.yml dhfs[].classification` holds `class` / `iec62304` / `samd`. Reference the manifest — a reclassification leaves every restated copy wrong.

✅ **Appropriate — rationale, not fact.** A strategy doc explaining *why* a module is IEC 62304 Class C ("a software fault can drive a hazardous condition") is narrative reasoning, not a duplicated fact. Narrative belongs in narrative docs.

## Edge case — appropriate duplication

Two things are **not** violations of this rule:

1. **Rationale** — prose explaining *why* a config value is what it is (history, decision context) belongs in narrative docs (strategies, READMEs, decision blocks). The rule forbids duplicating *facts*, not writing narrative.
2. **Explicit overrides** — a per-row override of a project default is fine when modeled as `override` semantics: default lives in config, an `override` field lives in the schema and is consulted only when present.
