---
title: "Program Executability Review — 5-Year Commercial Roadmap"
parent_analysis: commercial-roadmap-kol-review
advisor: program-manager
role: consulting
created: 2026-06-03
---

> _Demo sample data — not for clinical use._ Consulting program-management review supporting the clinical-affairs-led KOL gap-analysis of the 5-year commercial roadmap.

## What good looks like (executability bar)

A 5-year roadmap is executable when four things hold: (1) every release names a **regulatory vehicle that exists or has a funded path to existing** by its commit date; (2) the **upstream design-controls evidence** each release rides on is either complete or has a resourced, scheduled task to complete it; (3) **stage-gates are real decision points** with named owners and acceptance criteria, not year-boundary labels; and (4) the **critical path is mapped** so a slip in one workstream has a known blast radius. The roadmap in `commercial-strategy.md` is unusually honest about its seams (R4 names regulatory sequencing slip; the Open Items name the §3 and ben/011 dependencies) — but honesty about a dependency is not the same as a managed dependency. The bar is: is the dependency *scheduled and resourced*, or merely *acknowledged*?

## Overall program read

The **sequencing logic is sound** — front-load cheap, high-certainty Cloud Suite monetization on the already-cleared pump (K210345), defer the capital-intensive predictive-AI and ambulatory-hardware bets until the connected base funds them (D-COMM-1.3, D-COMM-1.7). That is the right shape. The **executability risk is concentrated in Year 1 and in the unresourced upstream dependencies**, not in the back half. Specifically: Y1 commits to three simultaneous GA launches, one of which (Drug Library Manager) requires its *own 510(k)* whose filing path is still undecided in `regulatory-strategy.md`; and the entire feature-to-filing categorization (D-COMM-1.4) sits on a tagging pass (ben/011) that is **Not Started** and an SRS layer (ben/049) that is **paused**. The plan reads as a credible *destination* with an *under-resourced first mile*.

## Critical-path & dependency map (call out unmanaged deps)

| Dependency | Roadmap element it gates | Current state | Managed? |
|---|---|---|---|
| **ben/011 criticality tagging (CtS/CtF/CtC/CtP)** | D-COMM-1.4 feature→filing category; the 510(k)+PCCP filing scope; the V&V split | **Not Started** (`tasks/ben/000-index.md`) | Acknowledged, not scheduled |
| **ben/049 SRS build** | All three core DHFs' SW requirements; trace matrix end-to-end; any V&V the Y1 SaMDs need | **Paused** before SRS authoring | Not flagged in roadmap at all |
| **Drug Library Manager filing path** | F1 — Y1 GA, reg-category C | "accessory bundle vs standalone 510(k) — **TBD**" (`regulatory-strategy.md` §2) | Acknowledged as TBD, but slotted as Y1 GA |
| **Regulatory §3 Jurisdictional Differences** | D-COMM-1.6 / Y5 EU MDR + Canada wave | **Unpopulated** (`regulatory-strategy.md` §3) | Acknowledged in Open Items |
| **PCCP scope (Ct\*-tagged change envelope)** | F4/F5 Y2 PCCP-authorized SaMDs; F6 retraining | Defined structurally but un-instantiated until ben/011 runs | Indirectly blocked by ben/011 |

The **unmanaged critical-path link** is ben/049 (SRS): the roadmap's Open Items name §3 and ben/011 but are **silent on the SRS gap**. A SaMD cannot reach GA without software requirements and the V&V traced to them; Y1's two SaMD/MDDS GAs (F1, and F4/F5 in Y2) inherit that incomplete layer with no acknowledgment.

## Stage-gate & resourcing assessment (per wave)

**Y1 (Defend & connect):** Three concurrent GA launches across three DHFs. F2 (Connectivity Adapter, MDDS, non-device) is the cheapest — defensible as Y1. F3 (Fleet/Telemetry, non-device) likewise. **F1 (Drug Library Manager) is the over-stuffed item** — it is SaMD with its *own 510(k)* (reg-category C), its filing path is TBD, and FDA review for a fresh 510(k) runs ~3–6+ months *after* a complete submission, which itself depends on ben/011 + ben/049 finishing first. Three GAs in one year is credible only if F1 is the one that slips.

**Y2–Y3 (Smart alarms → Predictive):** Gated on PCCP authorization (Q-Sub M12) and a new 510(k). The "each year gated on prior clearance" model (D-COMM-1.3, R4) is the **biggest schedule-realism risk**: it serializes the program against FDA review variance. A single Q-Sub or 510(k) running long cascades into every downstream year. The $24M / 42-month predictive build (`competitive-product-assessment.md`) starting at Y2 lands at ~Y5 — *past* its Y3 launch slot in D-COMM-1.4. That is an internal inconsistency, not just a risk.

**Y4–Y5:** Reasonable to leave soft; §3 unpopulated means Y5 cannot be firmed yet, which is appropriately flagged.

## Worked example (riskiest dependency)

**Before:** "F1 Drug Library Manager GA — Y1, reg-category C (own 510k/accessory)." Reads as a committed Y1 ship.

**After:** "F1 Drug Library Manager — Y1 *target*, **gated on**: (a) ben/011 criticality tagging complete → defines F1's Ct\* filing scope; (b) ben/049 SRS authored for `drug-library-manager` → SW requirements + V&V trace; (c) filing-path decision (accessory-bundle vs standalone 510k) resolved in submission planning; (d) FDA 510(k) clearance. Y1 GA is *commercial readiness*; **regulatory GA is the binding gate** and may land Y2. Owner: Regulatory + Program." The "after" version exposes the four-link chain the "before" version hides behind a single year label.

## Why this matters for THIS program

This is a connected-platform play where the *whole thesis* is post-market change velocity (drug-library cadence, firmware, future ML) flowing through a PCCP envelope (D-COMM-1.1, D-COMM-1.7). That envelope is **defined by the Ct\* tagging** (`regulatory-strategy.md` §1). So ben/011 is not a back-office chore — it is the keystone that makes Y2+ PCCP-authorized releases (F4, F5, F6 retraining) legally shippable without a fresh submission each time. A Not-Started keystone under a roadmap that monetizes change velocity is the single highest-leverage gap.

## Prescriptions (numbered, owner + acceptance)

1. **Resource and schedule ben/011 before any Y1 commit.** Owner: Regulatory + Program. *Acceptance:* all 22 UNs + 34 DIs Ct\*-tagged; trace matrix carries a Filing Scope column; PCCP envelope instantiated.
2. **Add ben/049 (SRS) to the roadmap's dependency register and resource it.** Owner: Engineering + Program. *Acceptance:* SW rows authored for pca-device / connectivity-adapter / drug-library-manager; trace runs UN→DI→SW→V&V end-to-end (not stopping at DI).
3. **Re-label Y1 GA dates as commercial-readiness vs regulatory-clearance gates; move F1's binding gate to "clearance," allow Y2 slip.** Owner: Program. *Acceptance:* each Y1 feature shows both a readiness date and a clearance gate.
4. **Resolve the $24M/42-month predictive timeline against the Y3 slot.** Owner: Commercial + Program. *Acceptance:* either the 42-month build starts early enough to clear by Y3, or F6 is re-slotted to Y4 with the IRR re-underwritten.
5. **De-serialize the gate model with explicit parallel pre-work.** Owner: Regulatory + Program. *Acceptance:* Q-Sub and predictive-evidence generation scheduled to *overlap* prior-year clearance windows, so one FDA slip doesn't cascade through all five years (mitigates R4).

## Evidence base (paths, task ids)

- `docs/project/strategies/commercial-strategy.md` — D-COMM-1.3/1.4/1.5/1.6/1.7/1.9 + Open Items
- `docs/project/strategies/regulatory-strategy.md` — §1 Carve-out, §2 (Drug Library Manager TBD), §3 unpopulated, §9 Pending Decisions
- `docs/project/input-analysis/competitive-landscape/competitive-product-assessment.md` — $24M/42-month, 68% IRR, $350M/58% IRR/$425M NPV
- `tasks/ben/000-index.md` — ben/011 (Not Started), ben/049 (paused/In Progress)

## Cross-discipline open questions

| # | Question | Owning discipline |
|---|---|---|
| 1 | Is Drug Library Manager filed as accessory-bundle within K210345's lineage or as standalone 510(k)? (gates F1 Y1 feasibility) | Regulatory |
| 2 | Can the 42-month predictive build clear FDA by the D-COMM-1.4 Y3 slot, or does F6 move to Y4? | Regulatory + Commercial |
| 3 | Is ben/011 + ben/049 staffing available in the current resource plan, or does it contend with the 30+ in-flight tasks? | Program + Engineering |
| 4 | Does R1 (predictive evidence sufficiency for opioid/PCA context) require a clinical study whose timeline gates F6 independently of FDA review? | Clinical + Regulatory |
