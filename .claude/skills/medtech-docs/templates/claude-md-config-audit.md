#### Audit existing wiring before adding pointers (HARD RULE)

This project's structural facts — where artifacts live, how DHFs are organized, what each module is classified as, which milestones bind which evidence — are encoded in a **wiring layer** of yamls and config files, not in prose. Before authoring metadata, schema fields, or doc content that describes a structural fact, **audit the wiring layer first**.

**Where the wiring lives**:

| Source | What it encodes |
|---|---|
| `project.yml` `dhfs[]` | DHF roster, paths, classification, scope, taxonomy pointers |
| `project.yml dhfs[].path` | DHF root on disk |
| `project.yml dhfs[].dhf_organization` | Whether the DHF uses internal folder convention or external taxonomy |
| `project.yml dhfs[].taxonomy_path` → `.taxonomy.yml` | Folder-name → canonical_role mapping for externally-organized DHFs |
| `project.yml evidence_layout` | Layer-name → folder mapping for fixed-name artifacts (DTM, threat model, uFMEA) |
| `project.yml dhfs[].evidence:` | Typed pointers to load-bearing artifacts |
| `project.yml tracker:` | Tracker config — status vocabulary, lifecycle plugin, coverage thresholds, row-id schema |
| `project.yml strategy_domains` | Strategy domain registry (regulatory, architecture, development, …) |
| `docs/project/milestones/regulatory.yml` | Per-milestone required/optional posture + cross-domain prerequisites |
| `docs/project/milestones/engineering.yml` | Engineering-prerequisite registry |
| `trace-matrix.yml` | Trace-matrix layer/parser config per DHF |

**How to apply** (before adding any new metadata field, schema entry, or structural prose):

1. **Grep `project.yml`** for the concept you're about to encode. If a field already represents it, use the field — do not redeclare.
2. **Check sibling configs** — milestone yamls, taxonomy yamls referenced by `dhfs[].taxonomy_path`, `evidence_layout` layers.
3. **Read adjacent skills' SKILL.md sections** that describe their config consumption — they often document fields that downstream skills can reuse.
4. **If the answer is in the wiring**, route the new feature through a **lookup against existing config**, not a new field. Example: a tracker resolver doesn't need each catalog obligation to declare its folder — it can compute the folder from `(DHF, canonical_role)` via `.taxonomy.yml` (external) or convention (internal).
5. **If the answer is genuinely missing**, document the gap in the schema/design doc and propose the new field as a project-config addition (with a fallback default), not as per-row metadata.

**Why this matters in regulated projects**: structure changes — new modules, renamed folders, taxonomy migrations, lifecycle-tool swaps. Documents that **reference** the wiring survive structural change. Documents that **redeclare** structural facts silently rot, and the rot surfaces during audit prep when paths no longer match what was claimed three months ago.

**Edge case — appropriate duplication**: Narrative prose explaining *why* a config value is what it is (rationale, history, decision context) belongs in narrative docs (strategies, READMEs, decision blocks) — not in `project.yml`. The rule is "don't duplicate facts," not "don't write narrative." Per-row overrides of a project default are also appropriate when modeled explicitly as `override` semantics (default in config, override field in schema, used only when present).
