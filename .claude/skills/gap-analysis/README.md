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
                                              docs/_analysis/<component>/<id>.md
                                                  (structured markdown,
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
                                                                                              docs/_analysis/<component>/<id>.md
                                                                                                  (same file, shared editorship)
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

## Best Practices

Consumed by `/best-practices` audit.

| Check | How to verify | Severity | Scope |
|---|---|---|---|
| Skill installed | `.claude/skills/gap-analysis/SKILL.md` exists | Required | shared |
| README.md exists | `.claude/skills/gap-analysis/README.md` exists | Required | shared |
| Template present | `templates/gap-analysis.md` exists | Required | shared |
| Topic-advisor map present | `data/topic-advisor-map.yml` parses as YAML with `topics:` and `aliases:` blocks | Required | shared |
| Project-agnostic source | Skill files contain no project-specific names (cloud IDs, project keys, device names, advisor agents bound to project context) | Required | shared |
| `_analysis/` tier present | `docs/_analysis/README.md` + at least one per-component subfolder | Required | local |
| Component slugs valid | Every component folder under `docs/_analysis/` matches a `project.yml dhfs[].arch_slug` or system-DHF leaf | Required | local |
| Template substitution variables consistent | All `{{ ... }}` placeholders in `templates/gap-analysis.md` are listed in `actions/init.md` step 6 | Recommended | shared |
| Action docs present | One `actions/<action>.md` for each action declared in SKILL.md | Recommended | shared |

## Changelog

- 2 (2026-05-27): Conformance fixes per `skill-creator audit-triggers`. Moved Changelog out of SKILL.md (lives only in README.md per project convention). Reformatted README Changelog from table → bulleted list. Removed the empty `setup` action stub from SKILL.md § Actions (the skill ships no hooks/agents/rules yet, so no setup work to do; will re-add when the skill grows those). Replaced a project-specific arch-name list in the `filing` topic description with a generic "multiple architectural components" phrasing. Genericized two example strings in `actions/list.md` and `templates/gap-analysis.md` that named a regulatory framework abbreviation in example positions where a generic phrasing reads the same.
- 1 (2026-05-27): Initial scaffold. SKILL.md + template + topic-advisor map + four action docs (`init`, `list`, `route`, `fan-out`). Companion to the `docs/_analysis/` first-class doc tier — the tier is the storage; this skill is the authoring convention over it.

## Known false positives in `skill-creator audit-triggers`

The audit script's project-name leakage check tokenizes `project.yml project.name` and flags any skill-file occurrence of those tokens. When a project happens to be named after a regulatory framework abbreviation (e.g., a project named `"Acme PCCP"` because the team is filing a PCCP), the audit will flag legitimate medtech-universal use of that abbreviation as project-name leakage.

For `gap-analysis`, this affects:
- The `pccp` alias in `data/topic-advisor-map.yml` — a user-typed abbreviation that other medtech projects also use; removing it would weaken the skill's natural-language triggering.
- The documentation in `README.md` and `actions/init.md` that lists `pccp` as one of the example aliases users may type.

These are intentional and project-agnostic. Other medtech projects (whose `project.name` does not include the abbreviation) will pass the audit cleanly. The skill's `data/topic-advisor-map.yml` topic-keys and descriptions otherwise use the formal phrasing "predetermined change-control frameworks" / "pre-authorized modification protocols" so the framework concept survives without naming any specific framework abbreviation in description text.
