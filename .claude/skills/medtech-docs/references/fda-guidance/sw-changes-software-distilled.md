# FDA Guidance — Deciding When to Submit a 510(k) for a Software Change to an Existing Device

🔎 **Finding aid — NOT the authoritative source.** Distilled summary for quick orientation and early analysis. Ground and cite the authoritative full text [`source-md/sw-changes-software.md`](source-md/sw-changes-software.md); verify any quote against the byte-correct `source/` PDF before treating it as verbatim. This paraphrases and omits (appendices/worked examples are routinely dropped) — a section's absence here is never evidence the source is silent.

**Full Title**: Deciding When to Submit a 510(k) for a Software Change to an Existing Device — Guidance for Industry and Food and Drug Administration Staff
**Document Date**: October 25, 2017 (final); draft issued August 8, 2016
**Status**: Final (Contains Nonbinding Recommendations)
**PDF Source**: https://www.fda.gov/media/99785/download (document number 1500055; docket FDA-2016-D-2021)
**Issuing Bodies**: CDRH, CBER
**Companion To**: *Deciding When to Submit a 510(k) for a Change to an Existing Device* (Oct 25, 2017) — the parent device-changes guidance ([`sw-changes-distilled.md`](sw-changes-distilled.md))
**Full text**: [`source-md/sw-changes-software.md`](source-md/sw-changes-software.md)

## Scope

This is the **software-specific sibling** of the device-changes guidance. The parent guidance decides whether a **non-software** change (labeling, technology/engineering/performance, materials, IVD) to an existing device crosses the 21 CFR 807.81(a)(3) threshold for a new 510(k); **this guidance decides the same question for software changes** — including firmware, and including embedded software, accessory software, and standalone software with a medical purpose (SaMD, per the IMDRF N10 definition). The threshold itself is identical between the two guidances ("could significantly affect the safety or effectiveness" / "major change or modification in the intended use"); only the assessment lens differs. For mixed software + non-software changes, run **both** guidances — if **either** concludes "New 510(k)," submission is likely required. Intended-use / indications changes are out of this guidance's flowchart — they route to the parent guidance.

Out of scope: 510(k)-exempt devices, PMA devices, enforcement-discretion software (e.g., per the Mobile Medical Applications / device-software-functions policy), software lifecycle process (IEC 62304), 510(k) *content* for software (the software-documentation-in-premarket-submissions guidance), and software validation principles (General Principles of Software Validation). Bug fix, hot fix, patch, tweak — whatever the name, all are **design changes** under 21 CFR 820 and all go through this decision tree.

**Key-question TL;DR**: A software change likely requires a new 510(k) when any of these hold: it was **intended** to significantly affect safety/effectiveness (Guiding Principle 1 — checked before the flowchart); it introduces or modifies a risk that could cause **significant harm** and isn't already effectively mitigated (Q3a); it creates or modifies a **risk control** guarding against significant harm (Q3b); or it could significantly affect **clinical functionality or performance specifications** tied to the intended use (Q4). Cybersecurity-only changes (Q1) and return-to-spec fixes (Q2) are documented to file, no submission. "Document" outcomes still pass through the **Section VI** change-type factors (infrastructure / architecture / core-algorithm / reengineering) before landing.

## The Decision Tree (Figure 1 + Section V companion text)

Compare the changed device against the **"original device"** — the most recently cleared 510(k) version (or preamendments / De Novo-granted version), NOT the last letter-to-file iteration. Cumulative drift across multiple documented-only changes can itself trigger submission (Guiding Principle 7).

```
Q1  Solely to strengthen cybersecurity, no other impact?      YES → DOCUMENT
Q2  Solely to return system to spec of most recently
    cleared device?                                           YES → DOCUMENT
Q3a New/modified risk that could cause significant harm,
    not effectively mitigated in the cleared device?          YES → NEW 510(k)
Q3b New or modified risk control measure for a hazardous
    situation that could cause significant harm?              YES → NEW 510(k)
Q4  Could significantly affect clinical functionality or
    performance specs directly tied to intended use?          YES → NEW 510(k)
    NO → check Section VI additional factors → DOCUMENT
```

- **Q1 (cybersecurity)**: a change made *solely* to strengthen security (encryption, access control, vulnerability removal) likely needs no 510(k) — but any incidental/unintended impact on other software or device aspects sends the change through the rest of the tree. V&V still expected.
- **Q2 (return to spec)**: pure bug fixes restoring the cleared specification → document. But if the fix requires **changing the specification** (e.g., rewording a faulty requirement, adding a new database/design element), the answer is "no" → continue to Q3. Spec-document clarifications with no code or performance change → no 510(k).
- **Q3a (risk)**: new 510(k) likely required only when **all three** hold: (1) the change creates/modifies a hazard, hazardous situation, or cause in the risk management file; (2) the associated harm is **serious or worse** — assessed **pre-mitigation**; (3) it is **not already effectively mitigated** in the cleared device (existing controls adopted for other hazards count as mitigation).
- **Q3b (risk controls)**: new/modified risk controls that are *necessary to prevent significant harm* → new 510(k). Merely **redundant** controls or enhancements on top of already-effective mitigation → continue to Q4. Loosening an existing control beyond its cleared specification fails here (robotic-surgery threshold example, Appendix A 4.1); recalculating within the cleared spec passes (4.2).
- **Q4 (clinical performance)**: "specifications" = anything influencing clinical performance — speed, response time, throughput, reliability, limits of operation, assay performance (for IVDs: analytical sensitivity/specificity, cut-offs, precision). Changed sensitivity/specificity of a detection algorithm → new 510(k); UI conveniences with unchanged clinical outputs (font size, images-per-window) → document.

### "Significant harm" and the risk framing

"Significant harm" = risk level **serious or more severe** — injury or impairment requiring professional medical intervention, permanent impairment, or death. The assessment vehicle is a **"risk-based assessment"** (deliberately distinct term: it covers effects on **effectiveness**, not just safety harms), using ISO 14971 / IEC TR 80002-1 vocabulary (hazard, hazardous situation, cause, sequence of events). Because **software failures are systematic**, probability of failure can't be estimated statistically — when overall probability of harm can't be estimated, **estimate risk on severity alone**. This is the software-side counterpart of the parent guidance's **Section E risk-based assessment** framework ([`sw-changes-distilled.md`](sw-changes-distilled.md)): the parent's flowcharts route to Section E for the could-significantly-affect analysis; here the same risk logic is built directly into gates 3a/3b, with the severity-only convention added for software.

### Guiding Principles worth pinning (Section IV)

1. **Intent test (GP 1)** — a change *intended* to significantly affect safety/effectiveness (improve clinical outcomes, mitigate a known risk, respond to adverse events) likely requires a new 510(k) regardless of the flowchart.
2. **Unintended consequences (GP 3)** — e.g., an OS upgrade rippling into drivers/embedded code; assess all consequences, not just the intended one.
3. **Testing role (GP 5)** — successful routine V&V **confirms** a no-submission decision but never overrides a "could significantly affect" conclusion; unexpected V&V results force re-running the flowchart.
4. **Simultaneous + cumulative changes (GP 6–7)** — assess each change separately and in aggregate, always vs. the original device; individual code-line edits aren't each a "change."
5. **Documentation (GP 8)** — every no-submission decision is documented to file under the QS regulation/QMS (21 CFR 820.30 design change control; record-keeping per 820.181); the decision process itself should be a quality-system procedure.
6. **Catch-up content (GP 9)** — a new 510(k) describes the triggering change(s) **plus** all since-clearance changes that a first 510(k) would have described; independently implementable non-triggering changes may ship immediately (documented).
7. **No SE guarantee (GP 10)** — following this guidance into a submission does not assure an SE determination.

### Section VI — Additional factors (the "gray zone" change types)

Applied to changes that survive the flowchart with "document" — and as standing considerations for code-maintenance work. Modular, planned architecture lowers the unintended-impact risk; loosely-structured code raises it.

| Change type | Definition / examples | Submission signal |
|---|---|---|
| **Infrastructure** | Compiler switch, language change (C→C++, C++→Java), driver/library change | Complexity-driven: syntax-similar language moves may be fine; paradigm shifts (functional → OOP) implying major rewrite → new 510(k) likely. Big V&V-script churn is a red flag for hidden infrastructure change. |
| **Architecture** | Porting to new OS, new hardware platform, new middleware | Judged by extent and device impact (may extend operating environment or affect performance). |
| **Core algorithm** | Algorithm directly serving the intended use (alarm, motor control, detection/measurement engine) | Performance-affecting changes already caught by Q4 — but a **complete rewrite even with identical performance claims and risk profile** may itself require a new 510(k) (indirect performance impact). |
| **Requirement clarification, no functionality change** | Rephrased or newly captured requirement, no code/function change | Likely no new 510(k). |
| **Cosmetic, no functionality change** | Logo/appearance changes, even touching many modules | Likely no new 510(k). |
| **Reengineering / refactoring** | Reconstituting software in a new form (legacy replacement) vs. disciplined internal restructuring | Refactoring within spec for maintainability → unlikely; significant rewrite (typical of reengineering) → likely, via performance/risk-control impact. |

Gray areas → discuss with the review Division that cleared the device.

### Appendix A — 24 worked examples (pattern)

Q1: security patch, added encryption/access control → document. Q2: fixes restoring cleared spec (barcode truncation, DICOM conformance, maintenance parameter, coding-error fix) → document; fix that **adds a new design element** (new database = spec change) → continue. Q3a: new quantitative diagnostic parameter (new miscalculation cause, unmitigated, serious harm) → new 510(k); removing an unused parameter → continue; mitigation of a *minor*-harm hazard → continue (harm not significant); new programming mode / new laser-control integration with new patient-injury risks → new 510(k). Q3b: widening a safety-threshold spec (weakened control) → new 510(k); noise-tolerance recalculation within spec → continue; automating a manual risk control for result mis-association → new 510(k); redundant print-page identifiers → continue; splitting an occlusion alarm into upstream/downstream variants → new 510(k). Q4: throughput gain via shorter incubation (assay performance) → new 510(k); throughput gain via transport timing only → document; more images per summary view, larger display font, sensor-version interoperability shim → document; arrhythmia-detection sensitivity/specificity change → new 510(k); snooze on a non-critical alarm → document.

## Program Relationships

| Companion | Division of labor |
|---|---|
| **Parent device-changes guidance** ([`sw-changes-distilled.md`](sw-changes-distilled.md)) | Same 807.81(a)(3) threshold, non-software lens: labeling (incl. intended-use/indications changes), technology/engineering/performance, materials, IVD flowcharts + Section E risk-based assessment. Mixed changes run both; either "New 510(k)" verdict controls. |
| **PCCP guidances** ([`pccp-aiml-distilled.md`](pccp-aiml-distilled.md), [`pccp-general-distilled.md`](pccp-general-distilled.md)) | Two-way coupling. (1) **Bypass**: a change implemented in conformance with an authorized PCCP needs no new submission — the PCCP's authorized modifications pre-empt this decision tree for those changes. (2) **Gatekeeper**: a PCCP is meant to cover modifications that **would otherwise require** a new submission — this guidance is the authority on whether a given software change crosses that line, so it both qualifies candidate changes *into* a PCCP and adjudicates changes that fall *outside* the authorized scope (which return to this tree). |
| **Special 510(k)** ([`special-510k-distilled.md`](special-510k-distilled.md)) | Sequential: this guidance decides **IF** a new 510(k) is required; the Special 510(k) program then decides **WHICH KIND** can carry it (Special vs Traditional/Abbreviated — own device + well-established methods + summary-reviewable results). Software changes are explicitly flagged there as frequent Special candidates when prior V&V methods are reused. |
| **Cybersecurity guidances** ([`cybersecurity-distilled.md`](cybersecurity-distilled.md)) | Q1's substantive companion: premarket content and postmarket management expectations for the security changes this tree lets through without submission. |
| **510(k) SE guidance** ([`510k-se-distilled.md`](510k-se-distilled.md)) | Where the resulting submission is judged; GP 10 — submission per this guidance ≠ assured SE. |
| **Software documentation / lifecycle guidances** | Out of scope here: 510(k) software documentation content, IEC 62304 lifecycle, and software validation principles live in their own guidances; this one only answers "submit or document." |

## QMSR Note (Posted-Copy Banner)

The FDA-posted copy carries the standard transition banner: 21 CFR part 820 was amended February 2, 2024 (89 FR 7496), retitled the **Quality Management System Regulation (QMSR)** effective **February 2, 2026**, incorporating **ISO 13485:2016** by reference. Read this guidance's QS-regulation cites accordingly: design/production change review-and-approval (820.30/820.70), device master record documentation (820.181), and process validation (820.75) map to the corresponding ISO 13485:2016 requirements (notably Clause 7.3 design and development, incl. 7.3.9 control of changes).

## Practical Checklist (Manufacturer Self-Assessment, per software change)

1. Is the change covered by an **authorized PCCP**? If yes and implemented in conformance — apply the PCCP's methods/protocols; this tree is bypassed.
2. **Intent test**: was the change made to significantly affect safety or effectiveness? Yes → new 510(k) likely, skip the tree.
3. Run **Q1–Q4** against the **original device** (most recently cleared version), covering intended *and* unintended consequences; for risk questions use pre-mitigation severity, severity-only when probability is inestimable.
4. "Document" outcome? Check **Section VI** factors (infrastructure/architecture/core-algorithm rewrite/reengineering signals) before settling.
5. Aggregate check: simultaneous changes individually + together; cumulative drift since last clearance.
6. Confirm with routine **V&V**; unexpected results → re-run the tree.
7. No submission → **document the analysis to file** under QMS change control. Submission → decide the 510(k) **type** via the Special 510(k) program criteria, and describe all since-clearance changes per GP 9.
