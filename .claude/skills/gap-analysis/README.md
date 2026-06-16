# `/gap-analysis` — Skill Design Doc

Not loaded by Claude — for human reference. The trigger surface + action contract lives in [`SKILL.md`](SKILL.md).

## Why this skill exists

Medtech projects accumulate three categories of audit-y work:

1. **Structural audits** — does the right folder / README / file exist? Owned by `/best-practices`.
2. **Coverage audits** — are all regulatory obligations covered by delivered artifacts? Owned by `/dhf-manifest` (4-tier deliverable catalog with gap reports).
3. **Mechanical drift audits** — do the system-of-record mirrors agree with the trace artifacts? Owned by `/jira-pull audit` and `/trace-matrix`.

Missing from the three above is a fourth dimension that medtech submissions live and die by:

4. **Content / methodology audits** — given that the right doc exists in the right folder and the right Jira items are present, **is the content methodologically correct against the standard?** E.g.:
   - Are the Hazard severity scores consistent with the described harms per ISO 14971 § 5.5?
   - Does the SRA's Class B determination satisfy IEC 62304 § 4.3.c?
   - Is the predicate-device analysis sufficient to support substantial equivalence?
   - Are the V&V test protocols traceable to specific design inputs and risk controls?
   - Does the threat model's residual risk argument hold up against IEC 81001-5-1's expectations?

These questions require expert domain reasoning — they cannot be answered by a rule-based checker. They need an advisor agent (`risk-management`, `regulatory-affairs`, `vnv-lead`, `cybersecurity`, `clinical-affairs`, `human-factors`, etc.) with access to the project's structured mirrors AND the relevant external standards.

This skill is the **convention layer** for that work:
- A canonical structured template for findings
- A first-class home for them (`docs/_analysis/<component>/`)
- A soft topic→advisor routing map
- Lifecycle actions (init / list / route / fan-out)

## Architecture

```
                                  reads
   project.yml ──────────────────────────────────────────┐
       dhfs[].arch_slug                                  │
       dhfs[].leaf                                       ▼
                                              ┌──────────────────────┐
   data/topic-advisor-map.yml ───────reads───►│  /gap-analysis init  │
       topics: {primary, consulting, ...}     └──────────────────────┘
                                                          │
                                                          │ writes
                                                          ▼
                                              docs/_analysis/<component>/<id>/<id>.md
                                                  (aggregate in its folder;
                                                   never overwritten by skill)
                                                          │
                                                          │ read by
                                                          ▼
                                              ┌──────────────────────┐
                                              │ /gap-analysis list   │
                                              │ /gap-analysis fan-out│ ─── invokes advisor agents ───►
                                              └──────────────────────┘                                  Agent tool
                                                                                                            │
                                                                                                            │ appends findings
                                                                                                            ▼
                                                                                              docs/_analysis/<component>/<id>/<id>.md
                                                                                                  (same aggregate, shared editorship)
```

## Key design choices

### 1. First-class doc tier under `docs/_analysis/`, not under any DHF

The `_analysis/` tier exists at the top level of `docs/` specifically because:
- Analysis spans multiple regulated topics (risk, regulatory, V&V, cybersecurity, …), not just the per-DHF risk-management folder.
- Item-DHF canonical paths in `project.yml` are not uniform (Confluence-canonical for items, `dhfs/` for system); tying analysis to any one path was wrong.
- Findings need visibility — top-level placement signals first-class status.

The skill consumes this tier; it does not own it. The tier is documented in [`docs/_analysis/README.md`](../../docs/_analysis/README.md).

### 2. Component segmentation matches `project.yml dhfs[].arch_slug`

The component segmentation reuses the project's existing DHF roster. No new vocabulary; no place for project-specific names to leak into the skill. The skill validates the component slug at `init` time against `project.yml`.

### 3. Topic vocabulary is medtech-generic

The topics in `data/topic-advisor-map.yml` (risk, regulatory, vnv, cybersecurity, clinical, human-factors, filing, postmarket, quality, software-architecture, systems-engineering) map to the standard regulatory framework (ISO 14971, IEC 62304, IEC 62366, IEC 81001-5-1, ISO 13485, FDA 510(k) / De Novo / PMA / pre-authorized change-control frameworks / MDR). Aliases (`fmea`, `qsub`, `usability`, `pccp`, …) resolve to canonical topics so authors can use natural terms users actually type.

### 4. Advisor routing is advisory, not gated

`/gap-analysis init` pre-populates `recommended_agents:` in frontmatter, but the author can override at any time. `/gap-analysis fan-out` only spawns the listed agents — it doesn't require them. This supports ad-hoc / multi-disciplinary analyses without forcing topic taxonomy on every finding.

### 5. Append-only multi-author contract

The file is shared between the human author and any agents invoked via `fan-out`. The skill never edits the file after `init`. Agents are explicitly instructed (in the fan-out prompt) to append to `## Findings` and `## Open Questions` — never replace. `## Goal`, `## Source`, `## Assertions` are framing the human owns. `status:` transitions are the human's call after reviewing agent findings.

### 6. Standards-citation requirement

The fan-out prompt requires advisors to cite specific standard clauses (`ISO 14971:2019 § 5.4`, `IEC 62304 § 4.3.c`, `21 CFR 820.30(g)`) alongside evidence. This is what distinguishes gap analysis from generic critique. Without it, the artifact has no regulatory leverage.

### 7. Derived JSON contract for machine consumers (v3)

Gap-analysis markdown is human/agent-shared prose, but downstream tools — the **project-console** Gap Analysis view first — need it machine-readable. The `render` action emits a derived JSON projection (`<id>.gap.json` + roll-up `index.json`) via `scripts/render_sidecars.py`.

This deliberately follows the `trace-matrix` loose-coupling contract: the **producer emits a stable JSON shape; the consumer knows nothing about how it was produced**. Two properties make it safe:
- **Derived, never authored.** The `.md` is the single source of truth; the JSON is regenerated (idempotent) and never hand-edited — so there is no double-authoring / drift-by-construction. (Contrast trace-matrix, which regenerates from *source docs*; here we regenerate from the *one* analysis markdown.)
- **Structured surface vs. prose body.** Frontmatter (meta, grounding, recommended agents) + the assertions table decompose fully into JSON fields; the F-N finding *bodies* stay as markdown strings (prose shape varies across authors/advisors), so the consumer renders them. The structured surface drives cards; the bodies render on expand.

The consumer (console) degrades gracefully when sidecars are absent — exactly like the trace-matrix view with no sidecar.

## Best Practices

Consumed by `/best-practices` audit.

| Check | How to verify | Severity | Scope |
|---|---|---|---|
| Skill installed | `.claude/skills/gap-analysis/SKILL.md` exists | Required | shared |
| README.md exists | `.claude/skills/gap-analysis/README.md` exists | Required | shared |
| Template present | `templates/gap-analysis.md` exists | Required | shared |
| Renderer present | `scripts/render_sidecars.py` exists and `--check` runs clean | Required | shared |
| Sidecars current | `python3 scripts/render_sidecars.py --check` exits 0 (no stale/missing `.gap.json` vs `.md`) | Recommended | local |
| Topic-advisor map present | `data/topic-advisor-map.yml` parses as YAML with `topics:` and `aliases:` blocks | Required | shared |
| Project-agnostic source | Skill files contain no project-specific names (cloud IDs, project keys, device names, advisor agents bound to project context) | Required | shared |
| `_analysis/` tier present | `docs/_analysis/README.md` + at least one per-component subfolder | Required | local |
| Component slugs valid | Every component folder under `docs/_analysis/` matches a `project.yml dhfs[].arch_slug` or system-DHF leaf | Required | local |
| Template substitution variables consistent | All `{{ ... }}` placeholders in `templates/gap-analysis.md` are listed in `actions/init.md` step 6 | Recommended | shared |
| Action docs present | One `actions/<action>.md` for each action declared in SKILL.md | Recommended | shared |

## Changelog

- 7 (2026-06-05): **`recs-<advisor>.md` is now a REQUIRED, console-named fan-out output (ben/224).** Fixed a contradiction where SKILL.md said advisors write `recs-<advisor>.md` but `actions/fan-out.md`'s prompt template told them to append F-N findings into the aggregate `## Findings` only — so the canonical fan-out path produced **no** advisor writeups and the project-console advisor tab stayed empty. Fan-out now mandates **two outputs per advisor**: (a) a `recs-<advisor>.md` full writeup, and (b) condensed F-N findings + an `agent:` changelog row in the aggregate. Spelled out the **load-bearing console naming contract** (the filename must equal `recs-<recommended_agents value>.md` — the subagent name verbatim — because `console/gap_analysis/loader.py:load_narratives` matches the sidecar `agents[]` `name` against a `recs-<name>` sibling; a mismatched name leaves the tab empty). Added a **recs-completeness audit** to `scripts/render_sidecars.py` (`missing_recs`, mirroring the console's exact discovery predicate): every contributing (`ran`) agent without a writeup prints a `WARN <id>: missing recs-<name>.md` line in all modes. Warn-by-default (so pre-dual-output analyses like the aggregate-only `qsub-*` ones don't turn `/best-practices` red); new `--strict-recs` flag makes a gap a non-zero exit (3). `--check` exit semantics unchanged (sidecar staleness only, exit 2) — backward-compatible for CI. No `schema_version` bump (additive). Updated SKILL.md (`fan-out` + folder-per-analysis convention + `render` action), `actions/fan-out.md`, `actions/render.md`. Skill-only scope; project-console needed no change (it already supports the advisor tab).
- 6 (2026-06-04): **Optional `## Assertion positions` section — per-advisor stance projection (ben/081).** A new optional section lets an analysis record, per assertion, each advisor's stance (`positive` / `neutral` / `negative`) plus a few-words note — the substantive "who thinks the claim holds, and why" behind the single overall disposition. Authored as `### A<n>` subheadings with `- <stance> — <advisor>: <note>` rows; the renderer (`attach_positions` in `scripts/render_sidecars.py`) parses it and attaches `positions: [{stance, advisor, note}]` to each assertion in the `<id>.gap.json` (additive — `schema_version` stays `1.0`; absent section → empty `positions`, no consumer impact). The project-console (≥1.25.0) renders these as a click-to-expand assertion detail with Positive/Neutral/Negative icons per advisor. `templates/gap-analysis.md` documents the convention. Generic — advisor names match the agents the sidecar already lists.
- 5 (2026-06-02): **`render` action + full folder-per-analysis convergence.** (a) Added the `render` action + `scripts/render_sidecars.py` (pure stdlib) deriving a JSON contract (`<id>.gap.json` per analysis + roll-up `index.json`, `schema_version: 1.0`) for machine consumers — primarily the project-console Gap Analysis view (mirrors the trace-matrix sidecar loose-coupling). New `actions/render.md`; SKILL.md § Actions + Supporting Files updated; `init`/`fan-out` reports remind to re-render. Documented the read-only-advisor fan-out reality (conductor writes back; advisors return findings). (b) Reconciled this project-local render work (originally a parallel `version: 3`) with upstream v4's folder-per-analysis restructure: the renderer and the project-console loader now read the **nested** `docs/_analysis/<component>/<id>/<id>.md` aggregate + `<id>/<id>.gap.json` sidecar layout (`glob("*/*/*.md")`, aggregate = folder-name-matches-file-stem), and the one existing flat analysis was migrated into its folder. Best Practices: renderer-present (Required) + sidecars-current (Recommended). Built under ben/077 (gap-analysis ↔ console showcase tab); v4 history (status-tracking, summary-table) preserved below.
- 4 (2026-05-27): Status-tracking convention added to `templates/gap-analysis.md`. The Summary-table gains a `Status` column (values: open / resolved YYYY-MM-DD / deferred / superseded) and a `Resolution progress: N / total` line below the table. The F-N detail block gains `Status`, `Category`, `Severity`, `Effort`, `Depends on`, and `Resolution applied (YYYY-MM-DD)` fields so each finding carries its own resolution audit trail. Motivated by sequential remediation walkthroughs where the team addresses findings one-at-a-time across multiple sessions and needs a single doc that shows "what's done, what's left" at a glance — alongside the per-edit detail.
- 3 (2026-05-27): Findings summary-table convention added to `templates/gap-analysis.md`. New `### Summary table` subsection sits **before** the detailed F-N entries with: (a) Category taxonomy (Drift / Manifest / Substantiation / Coverage / Methodology / Probe-preempt / Format-Tone), (b) Effort estimate scale, (c) a parameterized `Blocks-<gate>?` column (renamed per analysis), (d) Multi-agent consensus flag, (e) Depends-on field, plus a Coverage-scope note at the top of `## Findings` to make in-scope-vs-out-of-scope explicit. `actions/fan-out.md` updated so advisor prompts now require Category / Severity / Effort / Depends-on fields on every F-N (these populate the summary table). Motivated by real-world fan-out experience: when 20+ findings come back from a multi-advisor fan-out, administrative findings look the same as substantive ones at a glance without a triage view.
- 2 (2026-05-27): Conformance fixes per `skill-creator audit-triggers`. Moved Changelog out of SKILL.md (lives only in README.md per project convention). Reformatted README Changelog from table → bulleted list. Removed the empty `setup` action stub from SKILL.md § Actions (the skill ships no hooks/agents/rules yet, so no setup work to do; will re-add when the skill grows those). Replaced a project-specific arch-name list in the `filing` topic description with a generic "multiple architectural components" phrasing. Genericized two example strings in `actions/list.md` and `templates/gap-analysis.md` that named a regulatory framework abbreviation in example positions where a generic phrasing reads the same.
- 1 (2026-05-27): Initial scaffold. SKILL.md + template + topic-advisor map + four action docs (`init`, `list`, `route`, `fan-out`). Companion to the `docs/_analysis/` first-class doc tier — the tier is the storage; this skill is the authoring convention over it.

## Known false positives in `skill-creator audit-triggers`

The audit script's project-name leakage check tokenizes `project.yml project.name` and flags any skill-file occurrence of those tokens. When a project happens to be named after a regulatory framework abbreviation (e.g., a project named `"Acme PCCP"` because the team is filing a PCCP), the audit will flag legitimate medtech-universal use of that abbreviation as project-name leakage.

For `gap-analysis`, this affects:
- The `pccp` alias in `data/topic-advisor-map.yml` — a user-typed abbreviation that other medtech projects also use; removing it would weaken the skill's natural-language triggering.
- The documentation in `README.md` and `actions/init.md` that lists `pccp` as one of the example aliases users may type.

These are intentional and project-agnostic. Other medtech projects (whose `project.name` does not include the abbreviation) will pass the audit cleanly. The skill's `data/topic-advisor-map.yml` topic-keys and descriptions otherwise use the formal phrasing "predetermined change-control frameworks" / "pre-authorized modification protocols" so the framework concept survives without naming any specific framework abbreviation in description text.
