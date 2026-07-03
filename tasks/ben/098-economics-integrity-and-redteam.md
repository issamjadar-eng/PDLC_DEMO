# 098 — Economics Model Integrity + Red-Team the Aggregate

**ID**: 098
**Created**: 2026-06-30
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — tick the relevant Todo checkbox, add a dated Changelog line naming the concrete artifact, update Goals counts. **When you tick a Todo off (or add/restructure Todos), fill/refresh the corresponding `## Economics` entry in the same edit** (if usage-metrics is installed) — checking the box is the estimate trigger.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.** Git records code; this doc records the project narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**
6. **Estimation provenance (if `## Economics` is present).** Built per `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (usage-metrics); the block carries a `method_ref`. Point to the rubric, never copy it in. Skip if usage-metrics isn't installed.

Success test: a fresh Claude session, given only this file, can re-enter the work without asking "what were we doing?"

## Goals

_Make the agentic-value model defensible before the ROI claim (~800–2,753 person-hours saved) goes anywhere external._

- **Close the economics fill-gap (task v33).** The `## Economics` stub (v32) exists from creation but only gets *filled* at checkpoint — so a task can be created, worked, and Completed with an empty stub (sister-project 267). Trigger the fill on the events that actually happen: **todo check-off / todo edits**, **task completion**, and **session end**.
- **Tighten the `agentic_hours` definition (usage-metrics v9).** Redefine from "elapsed supervised wall-clock" → **human supervised-attention hours** (labor actually contributed), so the number is additive across tasks and honestly comparable to by-hand person-hours. Flag that pre-existing retrospective values (elapsed-ish) are conservative floors.
- **Red-team the aggregate.** Run the buyer-committee skeptics (CFO/PMO/CEO/CTO/VP-Eng/RA-VP/QA-VP) over the corrected ROI narrative; capture and triage findings.

## Todos

- [x] task v33: PERMANENT RULE 1 gains the todo-check → economics-fill trigger (template `create` rule 1)
- [x] task v33: `update … Complete` fills economics before flipping Status (completion gate — new step 1b)
- [x] task v33: lower SessionEnd marker threshold 30 → 15 min (`session-cleanup.sh` + 2 doc refs)
- [x] task v33: version bump + changelog; pushed (project PR #88, registry PR #244 merged)
- [x] usage-metrics v9: tightened `agentic_hours` → **human supervised-attention hours** (additive, labor-vs-labor) + unit-migration note (old wall-clock values = conservative floors, method_version stays 1). Fixed the console Agentic-hrs tooltip copy to match (dropped the now-wrong "not additive"; project-console 1.30.5). Verified live: methodology re-renders from the rubric + tooltip consistent.
- [x] Assemble the ROI narrative (claim + method + honest caveats) as the red-team target
- [x] Run the red-team panel (5 skeptics: CFO/PMO/QA-VP/CEO/RA-VP); captured 14 triaged findings above. **Unanimous: honest but not externalize-ready.** F1–F10 = unambiguous fixes; F12–F13 (calibration + independent gate) = decision fork.
- [x] **DECISION (F12/F13):** user chose fixes + independent re-estimate + relabel. **F13 done** — independent blind re-estimate of 12 tasks → **~88% mean inter-estimator deviation, 1.52× higher in aggregate (imprecise but not biased high)**. F12 done — headline relabeled "modeled, uncalibrated illustration."
- [x] Apply F1–F10: narrative v2 rewritten (F1 $53 reconciled, F3 false-precision killed, F4 regulatory wording, F5 index caveat bound, F6 work-type split, F7 risks-of-approach, F8 governance asymmetry, F9 single-operator); rubric+aggregate F2 (agentic_hours ranged, conservative floor) + F10 (inverted-task guard); usage-metrics v10. **Deferred:** F11 ([VERIFY] rate correction — needs real loaded-rate data); **Accepted:** F14 (no moat — reframed as efficiency observation in the narrative).

## ROI Narrative (v2 — hardened after red-team)

> **INTERNAL DEMONSTRATION ARTIFACT — NOT FOR EXTERNAL QUOTATION without the caveats below.**
> This is a **modeled, uncalibrated illustration of engineering-effort savings — not a measured saving.** It is **not a regulatory commitment**, makes **no claim about clearance or submission speed**, and asserts **no design-control review, approval, or human accountability was reduced or automated away** — DHF/submission deliverables retain their QMS design-review and approval controls (GL-SOP-DC-001/DC-005; 21 CFR 820.30(e)) **unchanged**. AI **assisted** human specialists who authored, reviewed, and remain the **accountable authors of record**. Demo program with **fabricated** clinical/predicate data; `[VERIFY]` placeholder labor rates.

**What this is.** A first-pass, **single-operator** estimate that across **95 demo tasks**, an agentic-first workflow performed engineering/authoring work a human team would have taken **on the order of ~1,300–3,200 by-hand person-hours** to produce, at a self-reported **~480 human supervised-attention hours** — a modeled **several-hundred to a few-thousand person-hours of effort avoided**. **Order-of-magnitude, not precise** (see Validation). _(Numbers rounded deliberately — the earlier "~800–2,753 / 1,280–3,233" four-significant-figure framing was false precision over 94 low-confidence single-lump guesses.)_

**Population + coverage.** **94 of 95 estimates were reconstructed retrospectively at `confidence: low`** (single-lump, from task summaries — the weakest evidence tier); only 1 (ben/096) was estimated in real time. Token-cost coverage is **separate and partial**: per the committed `usage.json` the per-task attributed cost is **$0** and ~**$152.57** of measured agentic spend sits in the `_unattributed` bucket (the ledger post-dates most of the work). _(An earlier note cited ~$53 from a local re-collection that was never committed — disregard it; the committed system-of-record shows $0 attributed / ~$152.57 unattributed.)_

**Work-type split.** The 95 tasks are **mostly tooling/skill/console engineering** (`rd-lead`), **not** regulated specialist deliverables. Only a minority (submission/QMS reference authoring, DHF sections) map to RA/QA/clinical. A specialist-rate `$` overlay must apply **only to the specialist-persona slice**, never the tooling majority — otherwise it inflates the dollar figure.

**How it's produced (4 stages):** (1) **Attribution** — tokens → active task via activation ledger + time-slicing + subagent scan; cost = tokens × rate card. (2) **By-hand estimation** — inline ranged, persona-tagged, per the research-anchored rubric (Wiegers/Fagan/Cisco/IAF/DO-178C where a norm exists; judgment-tier where none does); **the estimate carries no approval gate — range + confidence carry the uncertainty in its place. This gate is over the *estimate*, not the deliverables; DHF/submission work retains its QMS review/approval.** (3) **Agentic hours** — self-reported supervised-attention hours, now **ranged**; savings floor = by-hand-min − agentic-max. (4) **Roll-up** — deterministic; inverted tasks flagged not summed.

**Validation — the honest part.** No calibration against a real actual is possible (no task was ever hand-done). As the strongest available proxy, an **independent second estimator blind-re-estimated a 12-task sample** (originals stripped). Result: **~88% mean midpoint deviation** between the two estimators (2 of 12 diverged 3.8–5.5×; 10/12 within 2×). Directionally the independent estimate was **1.52× *higher*** in aggregate (215–538 vs 140–356 h) — **no evidence of upward inflation on the by-hand side; if anything the originals under-scoped.** **Takeaway: the estimate is imprecise (±~90% at task level) but not biased high** — treat the headline as an order-of-magnitude floor, never a precise figure.

**Risks of the ESTIMATE (accuracy):** retrospective low-confidence backfill; self-reported, un-instrumented agentic hours; ~half the personas judgment-tier; **no independent approval gate** (estimator = doer — an LLM is non-deterministic and the ~88% variance above quantifies the imprecision); cost/hours population mismatch; **single-operator** — additivity caps one operator, says nothing about many coordinating, so this does **not** generalize to portfolio scale.

**Risks of the APPROACH (business):** rework/error exposure when a non-deterministic tool is wrong in a regulated context (mitigation: unchanged QMS review gates); the **human-review + governance labor to catch that is real and only partly inside the 480h** — the by-hand side models PM/review/audit overhead, but the agentic side does not fully net its mandatory 3-stage authoring/QA/regulatory governance, so **480h likely *understates* human cost → savings likely *overstated* on that axis**; over-reliance / skill-atrophy; what the freed hours were reinvested in is unmeasured. _(This is a productivity-accounting unit — it does not describe design-control roles; accountable human authorship/review is unchanged.)_

**Bottom line.** Internally credible as a **directional efficiency indicator**; **not** defensible as a precise external ROI claim. Hardening further would require a real calibration (hand-do or historical-actual A/B) and an independent approval gate — neither of which a demo can manufacture. This is **not moat or strategy** — it's an efficiency observation on a commodity, reproducible method.

## Red-Team Findings + Triage

_5 buyer-committee skeptics (CFO, PMO, QA-VP, CEO, RA-VP) critiqued the ROI Narrative above. **Unanimous verdict: honest internally, NOT safe to externalize as written.** The cure they all converged on is not more caveats — it's **one calibration event + one independent verification gate** + tightening the claim language._

**What every reviewer conceded (real strengths):** genuine disclosure discipline (6 weaknesses stated up front); anchored rubric rows cite real primary literature (Wiegers/Fagan/Cisco-SmartBear/IAF MD 5/DO-178C); the roll-up arithmetic is deterministic and ties to `usage.json value_summary` (no inflation in the math); token cost is genuinely measured. The exposure is in the **inputs and the claim language**, not the arithmetic.

**Two cross-cutting themes (all 5 lenses):**
1. **Disclosure ≠ validation.** The estimator is a non-deterministic LLM reviewing its own work with no approval gate; "recalibratable" was never calibrated (no task ever hand-done; no MMRE/PRED accuracy metric); the deterministic-aggregation control sits on the arithmetic, not the estimating (same-estimator re-estimates diverge ~71% — Grimstad & Jørgensen; LLMs non-deterministic even at temp 0; METR RCT: devs self-estimated +20% while measured −19%).
2. **Claim language overreaches the method** — especially for regulated work.

**Triage:**

| # | Finding (reviewer) | Sev | Disposition |
|---|---|---|---|
| F1 | **`$53` doesn't reconcile to `usage.json`** — committed data shows $0/task + ~$152.57 unattributed (CFO-9, CEO-3) | blocker | **FIX** — factual error; the $53 was a local re-collection never committed. |
| F2 | **`agentic_hours` is an un-ranged point** — violates the rubric's own "always a range" rule; it's the subtrahend that most drives savings (QA-VP-5, CEO-6) | major | **FIX** — make it a range; floor = by-hand-min − agentic-**max**. |
| F3 | **False precision** — 94/95 tasks `retrospective:true, confidence:low`, single-lump; 4-sig-fig headline over lumped guesses (CFO-1, PMO-2, QA-VP-4) | blocker | **FIX** — drop false precision; report retrospective set separately + coverage fraction. |
| F4 | **Regulatory language** — no non-commitment disclaimer; "No human approval gate" landmine; "produced regulated DHF/submission work" reads as AI-authored-the-record (RA-VP-1,2,3) | blocker | **FIX** — disclaimer; scope "no gate" to the *estimate*; "assisted human authors who remain accountable." |
| F5 | **Demo caveat detaches when the number travels** — already in `000-index.md` bare (CEO-2) | blocker | **FIX** — bind the qualifier to the number; "not for external quotation." |
| F6 | **Persona-costing tooling at specialist rates** — skill/sync/console work priced as RA/QA/clinical (CEO-5, RA-VP-4) | major | **FIX** — segment headline by work type. |
| F7 | **"Risks of the estimate" but not "risks of the approach"** — rework/error/review-cost/over-reliance omitted (CEO-4) | major | **FIX** — add a risks-of-the-approach block. |
| F8 | **Coordination/governance asymmetry** — by-hand models PM/review/audit; 480h agentic side omits the mandatory 3-stage authoring/QA/regulatory governance still owed (PMO-5) | major | **FIX** — net the agentic-side governance overhead. |
| F9 | **Single-operator; no portfolio-scale evidence** (PMO-4) | major | **FIX** — scope claim to single-operator. |
| F10 | **`aggregate.py` L816 has no floor on `hours_saved`** — an inverted task nets a silent negative (PMO-10) | minor | **FIX** — guard/flag, don't silently sum. |
| F11 | **`[VERIFY]` rates ~2× high** — $210/hr vs ~$70–105/hr (CFO-4) | major | **DEFER** — needs real loaded-rate data; already `[VERIFY]`, console-side. |
| F12 | **No calibration** — never checked against one real actual (QA-VP-3, PMO-1, CEO-1) | blocker | **DECISION** — run a calibration event, OR relabel headline as "modeled illustration." |
| F13 | **No independent gate** — estimator demonstrates own value (QA-VP-1, CFO-10) | blocker | **DECISION** — independent blind re-estimate of a 10–15% sample; report variance. |
| F14 | **No moat / why-us** (CEO-7) | major | **ACCEPT/DEFER** — reframe as efficiency, not competitive advantage. |

**Net:** F1–F10 are unambiguous fixes (factual, consistency, wording, scoping). **F12–F13 are the fork the whole panel converged on** — either invest in a calibration + independent-re-estimate gate, or step the claim down to a "modeled illustration."

## Economics

_By-hand person-hour estimate, **filled at checkpoint / on todo check-off** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated; an empty `todos` list is ignored by the aggregator._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {"min": 4, "max": 8},
    "todos": [
      {
        "todo": "task v33 — economics fill-cadence (todo-check trigger + completion gate + 15-min SessionEnd)",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 3, "max": 6},
        "confidence": "med",
        "basis": "skill authoring: PERMANENT RULE 1 + update step 1b + session-cleanup threshold + 2 doc refs + versioning across 4 sites — small module, LOC-norm low end + judgment on trigger semantics"
      },
      {
        "todo": "usage-metrics v9 — tighten agentic_hours definition (attention-hours) + fix console tooltip to match",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 1, "max": 3},
        "confidence": "med",
        "basis": "definition/authoring: rubric paragraph rewrite + unit-migration note + tooltip copy fix + 2 version bumps — judgment-tier (conceptual clarity work, no LOC anchor)"
      },
      {
        "todo": "red-team the ROI aggregate — assemble narrative + run 5-skeptic panel + synthesize/triage 14 findings",
        "personas": ["quality-engineering", "program-manager"],
        "manual_hours": {"min": 8, "max": 20},
        "confidence": "med",
        "basis": "by-hand analogue = a formal cross-functional review of a value/ROI claim (5 reviewers × prep+read+writeup + synthesis) — anchored to audit/review effort (IAF/Wiegers review rates), regulated high end; ranged wide (review scope varies)"
      },
      {
        "todo": "F13 independent re-estimate (blind 12-task sample + variance analysis) + apply F1–F10 fixes (narrative v2, rubric+aggregate F2/F10, index caveats)",
        "personas": ["quality-engineering", "rd-lead"],
        "manual_hours": {"min": 6, "max": 16},
        "confidence": "med",
        "basis": "validation + remediation: design a blind re-estimation protocol + variance analysis (QE/verification labor) + code changes to aggregate.py (F2 range parse + F10 guard, ~40 LOC) + rubric/narrative authoring — mixed audit + software, mid-range"
      }
    ]
  }
}
```
_`agentic_hours` set to a 4–8 h range at the completion gate (2026-07-03) — supervised-attention hours across v33/v9/v10 authoring + the 5-skeptic red-team panel + the F13 blind re-estimate. Deferred: F11 (rate data), F12–F13 calibration fork (user decision)._

## Changelog

- 2026-07-03: Status changed to Complete. `agentic_hours` set at the completion gate (4–8 h). Deferred F11 + the F12–F13 calibration fork remain a user decision (spin a follow-up task if pursued).
- 2026-07-03 (checkpoint recovery — no transcript): Reconciled doc vs git. Everything below marked *"uncommitted / Next: push"* **shipped and is merged to `main`**: PR #88 (`42cfa62` — task v33 economics fill-cadence), PR #89 (`43b799f` — agentic_hours = attention-hours, usage-metrics v9 + console 1.30.5), PR #90 (`84605b0` — red-team fixes, narrative v2, usage-metrics v10), PR #91 (`0fb291a` — console renders agentic_hours as a range, 1.30.6 + ben/096 ranged estimate). Red-team + F1–F10 fixes all delivered. **Do not re-push.** Only residual is the deferred F11 (rate data) / user's F12–F13 calibration fork; `agentic_hours` still `null` at the completion gate. Status left `In Progress` pending user confirmation to close.
- 2026-06-30: **F13 independent re-estimate + F1–F10 fixes applied (uncommitted).** (F13) Blind-re-estimated a 12-task sample (economics stripped, verified no leak) with a second estimator → **~88% mean midpoint deviation** between estimators (2/12 diverged 3.8–5.5×; 10/12 within 2×), aggregate **1.52× higher** (215–538 vs 140–356 h). Honest read: **imprecise (±~90%/task) but not biased high** — refutes the "thumb on the scale" worry on the by-hand side while confirming "don't claim precision." (Fixes) Rewrote the ROI narrative → **v2 "modeled, uncalibrated illustration"** with a not-for-external-quotation banner, regulatory non-commitment disclaimer, "assisted not produced," work-type split, single-operator scoping, governance-asymmetry note, risks-of-the-approach block, and the $53→$0/$152.57 reconciliation. Method: **F2** — `agentic_hours` now ranged, roll-up floor = by-hand-min − agentic-max (`aggregate.py` tolerant of scalar-or-range; back-compat scalar = agentic-max so `value.js` unaffected); **F10** — inverted tasks flagged + excluded from the sum. usage-metrics v9→**v10**. Bound the demo caveat to the number in `000-index.md` (3 spots). F11 deferred (rate data), F14 accepted (reframed as efficiency, not moat). Next: push.
- 2026-06-30: **Red-team complete — 5 skeptics, 14 findings, unanimous verdict (uncommitted).** Assembled the honest ROI narrative (claim + 4-stage method + 6 stated weaknesses) and ran CFO/PMO/QA-VP/CEO/RA-VP against it. **Verdict: honest internally, NOT externalize-ready.** Two cross-cutting themes: (1) *disclosure ≠ validation* — never calibrated against one real actual, self-estimated by a non-deterministic LLM with no independent gate (~71% re-estimate inconsistency; METR: self-report runs optimistic); (2) claim language overreaches, esp. for regulated work. Conceded across all 5: the disclosure discipline is genuine, anchored citations are real, the arithmetic is clean/deterministic, token cost is measured — exposure is in inputs + wording, not math. Captured 14 triaged findings (F1–F14) in the new `## Red-Team Findings + Triage` section. F1–F10 = unambiguous fixes (incl. a real one they caught: **the narrative's `$53` doesn't reconcile to the committed `usage.json`, which shows $0/task + ~$152.57 unattributed** — my $53 was a discarded local re-collection). F12–F13 (calibration + independent gate) = decision fork for the user. Next: user's call on the fork, then apply F1–F10.
- 2026-06-30: **usage-metrics v9 — `agentic_hours` = attention-hours (uncommitted).** Tightened the rubric definition from "elapsed supervised wall-clock" → **human supervised-attention hours** (hands-on + active review; not compute, not background/unattended time). Now additive across tasks (one person can't attend two things at once) → `Σ agentic_hours` is a real "human hours" number and `hours_saved` is labor-vs-labor. Old wall-clock estimates over-state human cost → bias savings down → conservative floors; `method_version` stays 1 (definition sharpened, not changed). Fixed the console Agentic-hrs tooltip (project-console 1.30.5) — it still said "not additive" (old framing); now "sums honestly across tasks." Verified live: methodology re-renders from rubric + tooltip consistent (0 stale strings). This directly answers your "if you add agentic_hours up, it's not human hours" point. Next: red-team the corrected model.
- 2026-06-30: **task v32→v33 — economics fill-cadence (uncommitted).** Closed the fill-gap (v32 made the section exist; it only got *filled* at manual checkpoint). Three triggers, no per-turn hook (per user — didn't re-introduce the ben/100 pattern): (1) **PERMANENT RULE 1** (template `create` rule 1) now says ticking a Todo off fills the matching `## Economics` entry in the same edit; (2) **`update … Complete` step 1b** — completion gate refuses to close on an unfilled stub; (3) **SessionEnd threshold 30→15 min** (`session-cleanup.sh` + 2 SKILL.md doc refs). `checkpoint` 3b reworded "fill"→"reconcile". Bumped v32→v33 (frontmatter + README row). **Dogfooded:** checked off the three v33 todos above and filled this doc's `## Economics` entry in the same edit (rd-lead, 3–6 h). Next: push v33, then agentic_hours (v9) + red-team.
- 2026-06-30: Task created — economics model integrity (checkpoint-cadence fill fix + agentic_hours definition) + red-team the aggregate ROI claim. Spun out of the ben/096 close-out discussion (agentic_hours ambiguity + the checkpoint fill-gap surfaced while fixing the missing-economics-section issue).
