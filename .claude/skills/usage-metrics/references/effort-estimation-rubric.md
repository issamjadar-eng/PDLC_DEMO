# Effort-Estimation Rubric (by-hand person-hours)

_Owned by the `usage-metrics` skill. Read this when recording a task's `## Economics`
block. Method version: **1** (stamp `method_version: 1` so estimates are recalibratable)._

## What you're estimating

For each **completed todo**, estimate **how many specialist person-hours the same work
would have taken a human team by hand** — the traditional, non-agentic baseline. This is
the manual side of the agentic-value comparison (the agentic side — tokens + wall-clock —
is measured automatically). You are NOT estimating how long the agentic run took.

**Who does the estimate:** the main thread that did the work, inline, at checkpoint — it
already holds the context (the diff, what was hard, what was boilerplate). No subagent, no
approval gate. The **range + confidence tag** carry the uncertainty in place of review.

## Where it goes (schema)

A `## Economics` section in the task doc with one fenced **```json** block. (JSON,
not YAML: the aggregator parses it with stdlib `json` — it runs in CI with no
PyYAML. Keep it valid JSON: double-quoted keys/strings, no comments, no trailing
commas.)

```json
{
  "economics": {
    "method_version": 1,
    "agentic_hours": 8,
    "todos": [
      {
        "todo": "Harden resolve_files against bad globs",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 2, "max": 5},
        "confidence": "high",
        "basis": "software: tiny module + guarded try/except + test (LOC-norm, low end)"
      }
    ]
  }
}
```

- **`agentic_hours`** (per task): your honest estimate of the **elapsed supervised hours the
  agentic approach actually took** for this task — the "how long did it take *us*" number.
  This is what makes savings concrete: **hours saved = (Σ by-hand `manual_hours`) − `agentic_hours`**
  (ranged, since by-hand is ranged). A point estimate is fine (you roughly know your own time);
  omit it and the view falls back to showing by-hand hours without a savings figure.
- `personas`: 1+ advisor personas (the by-hand specialists) — this **is** the task's category.
  `manual_hours`: specialist person-hours, **RANGED** (`min`<`max`), never a point.
  `confidence`: `high|med|low`. `basis`: one line — the anchor used (or "judgment") + sizing input.

- **Multi-persona** when the by-hand work needs several specialists: list each in `personas`
  and let `manual_hours` cover the combined specialist-hours (e.g. a DHF section = RA + QA +
  clinical). Persona is the costing dimension — the console prices each persona's hours.
- Roll-up is automatic: Σ todos → task `min`–`max`; tasks → program. Estimate **completed**
  todos; leave open ones out (or mark a rough forward range, `confidence: low`).
- **No `$`** here — person-hours only. The console applies labor rates.

## Anchors (cite one; else mark it judgment)

External references (from ben/096 Phase 0 research). Regulated-device work sits at the
**high end** of any generic range (review cycles, traceability, audit rigor) — anchor up when
unsure, and say so in `basis`.

| Work type | Anchor | Use |
|---|---|---|
| **Document authoring** (procedures, specs, narratives, protocols, reports) | **3–7 hr/page** (TechScribe; top end for regulated) | pages × rate |
| **Software** (code, firmware, scripts, CLI tools / "skills") | **325–750 LOC/dev-month** (~20–25 LOC/day; **low end** for IEC 62304) | net delivered LOC ÷ rate; scripts = small modules |
| **Requirements / arch decomposition** | **10–18% of total project effort** (Wiegers/Jones) | ratio on a total-effort base |
| **Program management / coordination** | **7–15% of project** (PMI) | ratio overhead |
| **QE, risk, cyber, human-factors, V&V, post-market** | **NO published hour norm exists** | per-page authoring + an explicit specialist analysis/workshop adder; mark `confidence: judgment-tier` in `basis` |

**Honesty rule:** if no anchor fits, estimate from judgment and SAY so in `basis`
("model judgment — no external norm"). Never invent a citation. ~half the personas have no
external anchor — that's expected; transparency is what makes the aggregate survive a skeptic.

## Rules

1. **Always a range** (`min` < `max`); a point estimate is a tell that uncertainty was hidden.
2. **Persona-tag** every todo with the real by-hand specialist(s) — drawn from the advisor set
   (`.claude/skills/advisors/agents/`): regulatory-affairs, clinical-affairs, quality-engineering,
   risk-management, cybersecurity, human-factors, vnv-lead, post-market, rd-lead,
   systems-engineering, program-manager.
3. **Confidence** = `high` (anchored, clear scope) / `med` (anchored but fuzzy scope or
   judgment-adjacent) / `low` (mostly judgment / unfindable-anchor persona).
4. **Headline the conservative end.** Downstream claims lead with the `min` ("at least N
   person-hours") — so estimate the `min` as a floor you'd defend.
5. **`basis`** = one line: the anchor used (or "judgment") + the sizing input (pages / LOC /
   ratio / analysis scope). This is the audit trail.
6. **No approval gate.** Record and move on; anyone may edit later. Credibility = ranges +
   confidence + the Phase-6 red-team-the-aggregate pass, not sign-off.
