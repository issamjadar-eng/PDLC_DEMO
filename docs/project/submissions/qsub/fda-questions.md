---
version: v0.1
status: draft
summary: Six primary Q-Sub questions for FDA across three topics — device scope/classification, PCCP envelope, and predicate substantial equivalence.
---

# Questions for FDA — PainEase PCA Advanced (PP3500)

_Demo sample data — not for clinical use._

> **🔒 INTERNAL — reading convention.** 🔒 INTERNAL containers are stripped before transmission; the filed body (Questions Overview + the six numbered questions + Terms) is what FDA sees. Per-question 🔒 anchors hold internal validation notes. Primary set held to three topics per FDA Pre-Submission cadence guidance.

## Questions Overview 📤

| # | Q-ID | Topic | Subject |
|---|------|-------|---------|
| 1 | Q1.1 | Topic 1 — Device Scope | Bundling the Drug Library Manager SaMD accessory into the PP3500 510(k) |
| 2 | Q1.2 | Topic 1 — Device Scope | Connectivity Adapter as Non-Device MDDS |
| 3 | Q1.3 | Topic 1 — Device Scope | Product code and submission structure |
| 4 | Q2.1 | Topic 2 — PCCP | Single PCCP spanning drug-library, firmware, and predictive-alarm changes |
| 5 | Q2.2 | Topic 2 — PCCP | Acceptance criteria for the drug-library modification protocol |
| 6 | Q3.1 | Topic 3 — Predicate | PP3000 (K190567) substantial equivalence with added connectivity |

## Topic 1 — Device Scope, Classification, and Submission Structure 📤

### Q1.1: Bundling the Drug Library Manager SaMD accessory

**Context:** The Drug Library Manager is a Class II SaMD that authors the dose-limit table the pump enforces; it directly affects dose enforcement.
**Question:** Does FDA agree the Drug Library Manager may be cleared as an accessory bundled into the PP3500 510(k), or should it be a standalone 510(k)?
**Preliminary position:** We propose bundling it as an accessory within the PP3500 filing, with its own design-control record, because its safety role is inseparable from the pump's dose enforcement.

> **🔒 internal anchor.** Maps to regulatory-strategy.md § 2 (Drug Library Manager = Class II SaMD; bundle vs standalone flagged TBD for submission planning).

### Q1.2: Connectivity Adapter as Non-Device MDDS

**Context:** The on-prem Connectivity Adapter performs store-and-forward of orders and infusion events with no clinical computation.
**Question:** Does FDA concur the Connectivity Adapter is a Non-Device MDDS that need not be separately filed, while still being identified in the PP3500 submission with its cybersecurity evidence?
**Preliminary position:** We classify the adapter as Non-Device MDDS (post-2015 reclassification) and will identify it as adjacent infrastructure in the 510(k) without expanding the device boundary.

> **🔒 internal anchor.** Maps to regulatory-strategy.md § 2 (Connectivity Adapter = MDDS, not separately filed).

### Q1.3: Product code and submission structure

**Context:** PP3500 succeeds PP3000 (K190567) as a PCA infusion pump.
**Question:** Does FDA confirm the predicate's product code and that a single 510(k) with PCCP is the appropriate structure?
**Preliminary position:** We expect to carry the predicate's PCA infusion-pump product code and file a single 510(k) + PCCP.

## Topic 2 — PCCP Scope & Structure 📤

### Q2.1: Single PCCP spanning three change families

**Context:** Post-clearance change pressure spans drug-library updates, firmware updates, and future predictive-alarm SaMD additions.
**Question:** Does FDA agree a single PCCP may span these three change families, scoped structurally to criticality-tagged change types within pre-specified bounds?
**Preliminary position:** A unified PCCP with per-category modification protocols, bounded by the Ct*-tagged change envelope, is the most coherent structure.

### Q2.2: Acceptance criteria for drug-library updates

**Context:** Drug-library updates change the enforced dose-limit table.
**Question:** What performance and validation evidence does FDA expect in the drug-library modification protocol's acceptance criteria?
**Preliminary position:** We propose validation against the formulary source of truth plus regression of the pump's limit-enforcement behavior; numeric thresholds are pending FDA input.

## Topic 3 — Predicate Strategy 📤

### Q3.1: PP3000 substantial equivalence with added connectivity

**Context:** PP3500 preserves PP3000's intended use and core infusion technology while adding connectivity and a SaMD accessory.
**Question:** Does FDA agree PP3000 (K190567) is an appropriate predicate, and that the added connectivity/SaMD raises no different questions of safety or effectiveness given the proposed controls?
**Preliminary position:** PP3000 is the primary predicate; the added functions are addressed by the separation architecture and the PCCP envelope.

## Terms and Definitions 📖

_Reference vocabulary: PCA (patient-controlled analgesia), SiMD (software in a medical device), SaMD (software as a medical device), MDDS (medical device data system), PCCP (predetermined change control plan), Ct* (criticality tags — see regulatory-strategy.md § 1)._
