---
id: recs-cybersecurity
parent_analysis: competitive-threat-assessment
type: recommendation
authored_by: agent:cybersecurity
created: 2026-08-06
---

# Cybersecurity Assessment — Cyber as a Competitive Gate (PP3500 / PainEase PCA Advanced)

> _Demo sample data — not for clinical use. GlobalLogic device and DHF content is fabricated by construction and graded `INTERNAL-DEMO`. Every external cybersecurity fact below is graded against the source that carries it._

---

## What good looks like

**1. It holds a threat model that is a document, not a filename.** Enumerates assets, threat agents and threats by a justified method, covers the *full system and lifecycle* — not the device in isolation — and is redrawn whenever the architecture moves. `SUBSTANTIATED` — `docs/external/fda-guidance/cybersecurity.md` § *Threat Modeling* ("Must include the full system and lifecycle… Justify chosen methodology"; "Considering the device in isolation risks missing threats and controls").

**2. Its SBOM is a delivered artifact with a support posture attached.** Machine-readable, complete through transitive dependencies, carrying per-component level-of-support and end-of-support date plus a safety/security risk assessment for each known vulnerability, checked against NVD and CISA KEV. `SUBSTANTIATED` — both L1a and L1b § *SBOM Requirements*.

**3. It knows which edition of the guidance is in force, and re-checks at every gate.** `SUBSTANTIATED`

**4. It treats the buyer's security review as a design input, not a sales objection.** MDS2 completed and warranted accurate, SBOM deliverable, architecture diagram, security summary — assembled as a *Vendor Assessment Package* before the RFP. `SUBSTANTIATED` — HHS HICP 2023 Practice 9.L.B verbatim; HSCC JSP 2.0 §F.5.

**5. Its security requirements trace to a threat, and its threats trace to a control that is tested.** `SUBSTANTIATED` — the guidance's four cybersecurity test types and its security-architecture-views requirement.

---

## What the project does instead

**Start with the honest positive.** The security requirements exist and they are good ones. `software-requirements.md` §G8 carries five: SW-025 (firmware signature verification, RSA-3072 chained to a signing root, refuse-and-log on failure), SW-026 (RBAC across four roles), SW-027 (TLS with trust-store validation on all outbound channels), SW-028 (hash-chained tamper-evident audit log, ≥10,000 entries), SW-029 (gated audit-log export). Three are tagged **CtS** (critical-to-safety) and three name *Cybersecurity test* as the verification method. `INTERNAL-DEMO` for content; `SUBSTANTIATED` that the rows exist. That is a better starting position than most programs have.

Now the exposure.

**The cybersecurity plan does not exist — in any DHF.** `pdlc-demo-dhf-discovery.json` resolves `cybersecurity_plan` to `null` for **all ten** DHFs. `SUBSTANTIATED`. `recs-commercial.md` §8 flags the `pca-device` null; the finding is ten times larger.

**The threat model and SBOM resolve as `exists: true` — and the bytes are empty templates.** `GL-TMP-SW-002-threat-model.md` is 1,810 bytes: `Revision: 0.1 DRAFT`, `Effective Date: — (not released)`, and a body of `{{DHF_NAME}}`, `{{Summary per the parent QMS template}}`, `{{list sources, evidence, linked artifacts}}`, `{{}}`. The SBOM at `GL-WI-SW-002-sbom.md` is the same shape: an *Entries* table with one empty row. The same two stubs are replicated across all ten DHFs at identical size. `SUBSTANTIATED`

**This is the single most important thing in this assessment: role resolution is not content.** Any dashboard, tracker or readiness report keyed on `exists: true` currently reports this program as having a threat model and an SBOM for ten components. It has neither, for any.

**The vulnerability-management plan is a stub, and it is missing from seven of ten DHFs.** Present only under `pca-device`, `connectivity-adapter` and `cloud-suite`, and in each the same unfilled template. `vulnerability_management` resolves to a non-existent folder in all ten. `SUBSTANTIATED`

**Three manifests assert this evidence exists.** `510k/composition-manifest.md` L50 pulls "Cybersecurity Plan + Threat Model + SBOM" from `pca-device/cybersecurity/`; L61–62 from `connectivity-adapter/cybersecurity/`; L77 pulls "Cybersecurity Plan + Threat Model + Signing Trust Chain" from `drug-library-manager/cybersecurity/`. And `qsub/composition-manifest.md` L67 excludes the system-level cybersecurity assessment with the justification: *"Per-component evidence exists; system-level assessment ships with 510(k) Release."* **Per-component evidence does not exist.** `SUBSTANTIATED` — the manifest line and the stub files were both read this pass.

**The reference stack the program would cite is two supersessions stale — on both tiers.** L1a `.claude/skills/medtech-docs/references/fda-guidance/cybersecurity-distilled.md` and L1b `docs/external/fda-guidance/cybersecurity.md` both carry `**Document Date**: September 27, 2023` and the old title *"Quality **System** Considerations."* The operative guidance is the **February 3, 2026** issue, retitled *"Quality **Management** System Considerations,"* docket FDA-2021-D-1158, superseding the June 27, 2025 issue, which superseded September 2023. `SUBSTANTIATED` — verified independently twice.

**One L1b file states a requirement FDA does not impose.** `docs/external/standards/iec-81001-5-1.md` L156 asserts SBOM *"Machine-readable format required (**SPDX or CycloneDX**)."* FDA says industry-accepted formats *"are **encouraged**"* — those formats come from the NTIA document, not an FDA mandate. Citation verdict: **broken**.

**And the clause numbers in that same file are self-flagged as unverified.** Its last line reads `[VERIFY: All clause numbers and deliverables against the actual IEC 81001-5-1:2021 document]`, and every row of its *Verification Checks* table is `[VERIFY — populate from source]`. IEC clause text is paywalled and absent from this repo at every rung. Citation verdict: **unverified** — closing it requires the purchased standard, not more searching. I therefore cite 81001-5-1 below by *deliverable*, not by clause number.

---

## Walk-through of the exposure

### 1. Is a hospital security review a purchase gate? Yes — contractually, not regulatorily

**Established.** HHS HICP 2023, sub-practice 9.L.B, instructs HDOs to memorialize cybersecurity requirements *"in your organization's contracting processes"* and *"incorporated into prospective procurements through… RFIs or RFPs,"* to *"require procurements… to undergo security evaluations,"* and to *"insist on receiving a MDS2"* plus an SBOM and architecture diagram as a *Vendor Assessment Package*. **HICP's worked example is an infusion pump.** HSCC MC2 v2 (November 2025) converts this to contract terms with hard numbers: SBOM delivery (#44), 3-business-day notice on CISA-KEV-listed vulnerabilities (#33), 30-day patching (#31), 5-day breach notice (#35), and no OS within 2 years of end-of-support at delivery with the upgrade path at supplier expense (#40). `SUBSTANTIATED` (verbatim)

**The structural signal is who wrote it.** MC2 v2 is co-chaired by Mayo Clinic and **Premier, a national GPO**, and MC2 describes itself as *"in effect, a pre-negotiated contract."* Read against `recs-commercial.md` §2 (GPO contract status is an evaluability gate), the two findings compose: **the body that controls the gate we must pass co-authored the cybersecurity terms.** That is a stronger claim than any survey.

**Directional only.** RunSafe's 2026 index reports 56% of 551 purchasing-involved professionals have rejected a device on cybersecurity grounds, up from 46%, and 35% will not consider a device without an SBOM. RunSafe sells runtime exploit protection. `SUBSTANTIATED as a vendor-sponsored survey`. **Use the 46%→56% direction; never quote 56% as independent.**

**What is opinion.** That cyber is *the* axis where a connected pump most plausibly loses a sale is my judgment, not a sourced finding. `OPINION` — no source ranks loss causes for pump procurements.

### 2. The competitive asymmetry cuts both ways, and the second way is under-argued

**In our favour.** Every major pump vendor carries a CISA advisory history: Hospira LifeCare PCA at CVSS v2 **10.0** (unauthenticated root Telnet, CVE-2015-3459), BD Alaris Gateway Workstation at v3 **10.0** (unsigned firmware upload, CVE-2019-10959), B. Braun Infusomat/Perfusor at v3 **9.0**, Smiths Medfusion 4000 at v3 **9.8**, plus URGENT/11 and Ripple20. `SUBSTANTIATED`. Unit 42 scanned 200,000+ pumps on live hospital networks and found **75% with known security gaps**. A greenfield device can ship modern crypto, signed updates and a current OS with no legacy-compat debt — and MC2 #40 (no OS within 2 years of EoS) is a clause a new entrant passes trivially and a fifteen-year-old fleet does not.

**Against us, and this is the part the strategy has not priced.** A hospital security review is not a vulnerability count — it is an assessment of *whether the vendor has a process.* An incumbent with a decade of advisories has, by necessity, a coordinated disclosure channel with a track record, a patch cadence a customer can point at, a PSIRT that has been exercised, and MDS2 forms filled in across product generations. We have none of that, and "we have never had a vulnerability" reads to a security officer exactly as "we have never had a recall" reads to a value-analysis committee — as a **denominator artifact**. `INFERRED` — MC2 #31/#33/#35 and HICP 9.L.B all ask for *demonstrated process capability*, unevidenceable at zero field exposure; the inference fails if buyers accept attestation in lieu of record, which MC2 #46's secure-development attestation suggests is partly true.

**Net.** Legacy debt is a real incumbent liability on *product* criteria and a real new-entrant liability on *process* criteria. The defensible position is not "we are clean" — it is a **contractual risk-absorption offer**: accept MC2 v2's numbers as written, warrant the MDS2, commit the SBOM as a deliverable. That converts an unevidenceable claim into a signed obligation, which is the only form a buyer can act on. `OPINION`

### 3. §524B as a date-stamped obligation

The statute (21 U.S.C. §360n-2, added by P.L. 117-328 **§3305(a)** — not "the PATCH Act," which appears nowhere in the statute) requires four things of a cyber-device submission: a postmarket vulnerability-monitoring plan **including coordinated vulnerability disclosure**; designed-and-maintained processes with **on-cycle patches for known unacceptable vulnerabilities and out-of-cycle patches for critical ones**; **an SBOM covering commercial, open-source and off-the-shelf components**; and the Secretary's catch-all. `SUBSTANTIATED` (verbatim)

Three things break a plan written a year ago:

- **The guidance moved twice in eight months** — September 2023 → June 27, 2025 → **February 3, 2026**, with a retitle to "Quality *Management* System" tracking QMSR/ISO 13485 alignment. **This repo's own L1a and L1b files are stuck at September 2023.**
- **The modification trap.** §524B applies to *any* submission under 510(k)/De Novo/PMA/PDP/HDE, **including modifications**. Even for changes "unlikely to impact cybersecurity," a §524B(b)(1) plan must be provided if not previously submitted, and the SBOM is still required. **A Special or Abbreviated 510(k) does not exempt.** `SUBSTANTIATED`. This lands directly on D-COMM-1.4's regulatory-category column: every row marked **A (Letter-to-File)** or **B (PCCP)** that ends up as a submission carries the §524B content burden anyway.
- **The SBOM baseline diverged after FDA's guidance froze.** FDA's February 2026 guidance anchors to the **October 2021 NTIA** minimum elements. CISA's **2026 Minimum Elements**, published **2026-07-29** with NSA/FBI and 15 international partners, states verbatim that it *"updates and replaces"* the NTIA 2021 baseline — adding SBOM Author Signature, Data Format Name/Version, Generation Context, Tool Name/Version, SBOM Version, **Component Hash Value and Algorithm**, and Component License. An SBOM built to FDA's cited baseline today lacks all of those. `SUBSTANTIATED` for dates and contents; **building to the 2026 superset satisfies both** is `INFERRED` — FDA has issued no statement on the gap.

**RTA implication.** FDA's forbearance ended **2023-10-01**; from that date FDA may refuse to accept a cyber-device submission lacking §524B content (88 FR 19148, verbatim). Against a filing whose threat model, SBOM and cybersecurity plan are template stubs, the RTA exposure is not theoretical.

### 4. Our own exposure, against the two governing documents

| FDA-guidance deliverable | Project state | Grade |
|---|---|---|
| Security risk management report (e.g. AAMI TIR57) | No role, no file | `SUBSTANTIATED` |
| Threat modeling documentation, full system + lifecycle | Stub, `{{}}` body, ×10 DHFs | `SUBSTANTIATED` |
| Cybersecurity risk assessment (exploitability-based) | Absent; `software_risk_assessment` null ×10 | `SUBSTANTIATED` |
| SBOM (statutory, §524B) | Stub with one empty row, ×10 DHFs | `SUBSTANTIATED` |
| Security architecture views — all four categories | Partial: PCA SAD §2/§6 ≈ global system view; **no multi-patient-harm view, no updateability/patchability view, no security use-case views** | `INFERRED` |
| Cybersecurity testing — all four types | SRS §G8 names *Cybersecurity test* for SW-025/026/027; `verification_protocols` and `verification_reports` folders do not exist (`file_count: 0`) | `SUBSTANTIATED` |
| Cybersecurity labeling | No artifact located | `SUBSTANTIATED` (absence checked by glob) |
| Cybersecurity management plan (statutory, §524B) | `cybersecurity_plan: null` ×10 | `SUBSTANTIATED` |

Against IEC 81001-5-1's deliverable set — security risk assessment/threat model, security requirements, security architecture, security test report, SBOM, vulnerability-management plan, security incident-response plan — **one of seven is populated** (security requirements, SRS §G8). The clause numbers that file attaches to each deliverable are `UNVERIFIED` by the file's own `[VERIFY]` marker; the *deliverable list itself* is corroborated independently by the FDA guidance's submission-requirements list, so the gap finding does not depend on the unverified clause mapping.

**A defensible cross-check.** SW-027 requires **TLS 1.2 or higher**; both SADs specify **TLS 1.3 mutual auth** on the device↔adapter link. Not a defect, but exactly the kind of drift a threat model exists to arbitrate — and there is no threat model.

### 5. Cyber as a threat *from* competitors — the ICU Medical case, read carefully

On **2025-04-10** ICU Medical issued three simultaneous Class I recalls across the CADD-Solis family — including **HPCA and HSPCA, the PCA configurations** — covering thermal damage, false upstream-occlusion alarms, and **wireless-module intermittent connection alarms interrupting an active infusion (Z-1662-2025)**, whose scope was still expanding as late as **2026-05-27**. `SUBSTANTIATED`

**Say precisely what this is and is not.** Z-1662-2025 is a **wireless-module reliability failure, not a cybersecurity exploit.** No CVE, no advisory, no adversary. Treating it as cyber evidence would repeat the error already flagged for the 2025 BD Alaris recall, which is an infusion-set flow-accuracy issue and is **REFUTED** as cyber evidence.

**What it legitimately supports.** It is the cleanest available demonstration that **the connected surface is where PCA pumps now fail in a way that interrupts therapy** — and it is a *direct PCA competitor's* connectivity layer. Pair it with BD's own connectivity-layer Class I (2025-02-18, Alaris Systems Manager and Care Coordination Engine Infusion Adapter sending **outdated automated programming requests** to the pump) and the pattern is: **two of the three leading vendors have had Class I events originating in the integration layer, not the pump.** That is the layer D-COMM-1.4 F2 ships in Year 1.

**Does a competitor's cyber incident help or hurt us?** Both, asymmetrically. The Symbiq precedent is the sharpest datum available: FDA told providers **"transition to alternative infusion systems, and discontinue use of these pumps"** for a cybersecurity reason alone, with **no known adverse event and no known unauthorized access**. `SUBSTANTIATED` (verbatim). That is a fleet-replacement trigger of exactly the kind `recs-commercial.md` §2 identifies as the displacement mechanism. But the same event teaches hospital security officers that connected pumps are a category risk. A category freeze hurts a new entrant more than an incumbent: the incumbent's fleet is already installed and running under existing contracts; ours is a net-new connected deployment requiring fresh security sign-off. `INFERRED` — fails if a freeze triggers rip-and-replace rather than pause, which Symbiq did in that one case.

### 6. The AI/predictive roadmap changes the trust boundary, not just the feature set

D-COMM-1.4 commits F4 (Alerts Engine, Y2), F5 (Clinical Surveillance, Y2), F6 (Predictive monitoring, Y3), F8 (Dose personalization, Y4) — all cloud-hosted SaMD. Four specific new threats follow, none present in any current artifact:

1. **The de-identification claim stops being sufficient.** PCA SAD §6 states *"PHI does not leave the hospital… Cloud egress is de-identified."* Per-patient deterioration prediction needs longitudinal per-patient physiologic series. A stable pseudonymous identifier plus a timestamped vital-sign trace is a re-identification surface, and de-identified data that drives a patient-specific clinical alarm is functionally re-identified at the point of use. `INFERRED` — fails only if inference runs on-prem and only anonymous aggregates leave.
2. **Model integrity becomes a safety-critical inbound payload.** M3's drug library and M6's firmware are signed and verified (SW-025). A model artifact or inference result crossing the same boundary has **no equivalent requirement** in SRS §G8. `SUBSTANTIATED` — SW-025 covers firmware bundles only.
3. **Availability becomes a clinical dependency.** A cloud alerting service a clinician relies on is a denial-of-service target with a clinical consequence, and ECRI's 2026 hazard list already carries *"Unpreparedness for a 'digital darkness' event"* at #2. `SUBSTANTIATED`
4. **Training-data poisoning and inference manipulation** are new threat classes with no analogue in a rules-based DERS pump, and no methodology in this repo addresses them.

Worth stating plainly: **no infusion pump of any kind appears on FDA's AI-Enabled Medical Device List** (1,524 rows, three independent checks). So there is **no competitor precedent for how a regulator or a hospital security office reviews AI-on-a-pump.** We would be defining that review, not passing it.

---

## Worked example (before / after)

**The element:** the Connectivity Adapter trust boundary — where an architecture assertion, a roadmap commitment and an unresolved strategy question all collide.

### Before — as currently written

`connectivity-adapter-system-sad.md` §2 draws the Adapter→Cloud Suite link as *"(optional, out of baseline)"*; §5 states outbound is *"de-identified fleet telemetry only. Disabled by default in the cleared baseline"*; §5 also says the device certificate is issued during provisioning *"(see Cybersecurity Plan)"*; §7 commits four artifacts to the PP3500 510(k), two of which are "Cybersecurity Plan" and "Threat model + SBOM."

Four compounding defects:

1. **The referenced document does not exist.** `cybersecurity_plan` is `null` for `connectivity-adapter`. §5's provisioning trust anchor — the root of the entire mutual-TLS story — points at nothing.
2. **The governing question is formally open.** `architecture-strategy.md` § *Open Items* still lists *"Trust and network boundaries — where PHI lives across device↔adapter↔hospital-IT↔cloud"* and *"Whether the Connectivity Adapter talks to Our Cloud Suite directly, only via hospital network egress, or not at all in the cleared baseline."* The SAD asserts an answer the strategy records as undecided.
3. **The roadmap contradicts "disabled by default."** D-COMM-1.4 ships F3 (Fleet Management + Telemetry dashboards) in **Y1** and F4/F5 in **Y2**. Those require the link enabled. The "cleared baseline" posture has a ~12-month life, and nothing records what happens at month 13. `INFERRED` — a cloud dashboard cannot render telemetry over a disabled egress path.
4. **No threat model can arbitrate any of this,** because there isn't one.

### After — a defensible shape

> **Adapter trust-boundary specification.** Three zones, separately assessed: **Z1** device↔Adapter (mutual TLS 1.3, device identity provisioned from the GlobalLogic PKI, trust anchor and revocation path specified in the Cybersecurity Management Plan §[x]); **Z2** Adapter↔hospital IT (HL7v2.5/MLLP-TLS or FHIR R4/HTTPS, hospital IdP, PHI-bearing, same trust zone as the EHR); **Z3** Adapter↔Cloud Suite (**two states, both modeled**).
>
> **Z3-A — cleared baseline: disabled.** Egress blocked at the Adapter. Threat model records Z3 as out-of-scope for the 510(k) attack surface.
>
> **Z3-B — enabled (required by F3 from Y1).** Data classification stated field-by-field, not asserted as "de-identified": which fields leave, what identifier links records across time, and a written re-identification-risk assessment against the HIPAA de-identification standard. Outbound-only by default; any inbound cloud→Adapter path (model artifacts, config, alerts) is enumerated separately and each inbound payload type carries a signature-verification requirement equivalent to SW-025.
>
> **The gate:** Z3-B is not enabled in any released configuration until (a) the threat model covers Z3-B, (b) a security requirement exists for every Z3-B inbound payload type, and (c) those requirements have a verification protocol. **If F3 ships in Y1, Z3-B is the cleared baseline and must be filed as such** — the "optional / disabled by default" framing is not available.

**What changes.** The "before" is one asserted sentence resting on a document that does not exist, contradicted by the roadmap and by the strategy's own open-items list. The "after" is two named configurations, an explicit data-classification obligation replacing the word "de-identified," a signature requirement extended to a payload class that currently has none, and a stated gate. It is also honest about the consequence: **the roadmap has already decided this question, and the architecture record has not caught up.**

---

## Why this project specifically

**1. Ten DHFs, one attack surface, zero cybersecurity plans.** This is a modular-DHF platform where the PCA's cyber posture is *defined by* what touches it — the 510(k) composition manifest says so explicitly — and the composition pulls cybersecurity artifacts from three DHFs, none of which have them.

**2. The manifests already made the claim.** The Q-Sub manifest's *"Per-component evidence exists"* is a written assertion, in a submission-composition document, that is false against the bytes. That is different in kind from an empty folder: it is a statement a reviewer or auditor can hold the program to.

**3. Our own reference layer is the stale one.** The program cannot cite the current guidance because both tiers stop at September 2023, and one L1b file asserts an SBOM format mandate FDA does not impose. Fixing the DHF without fixing the references means authoring the plan against superseded content.

**4. The connected roadmap front-loads the attack surface.** D-COMM-1.4 puts the Adapter, fleet management and telemetry dashboards in **Year 1** — the integration layer where two competitors have had Class I events — while the cybersecurity evidence for that layer is a template.

**5. The one wedge with real evidence is the one our file is emptiest on.** The cybersecurity nulls are the same finding as the quality-posture gap, and they are the half a **GPO co-authored contract** (MC2 v2) will test line-by-line.

---

## Step-by-step prescription

**1. Correct the false evidence assertions in both composition manifests — this week.**
`Owner: Regulatory Affairs + Cybersecurity Lead` | `Artifact: qsub/composition-manifest.md L67; 510k/composition-manifest.md L50, L61–62, L77` | `Acceptance: the qsub "Per-component evidence exists" line is replaced with the true state; every 510(k) manifest row pointing at a cybersecurity artifact is annotated with that artifact's actual revision status; no manifest row asserts an artifact that resolves to an unfilled template.`

**2. Refresh both reference tiers to the February 2026 guidance before authoring anything.**
`Owner: Regulatory Affairs` | `Artifact: docs/external/fda-guidance/cybersecurity.md (L1b); the L1a distilled reference and its source-md` | `Acceptance: title updated to "Quality Management System Considerations"; date 2026-02-03; docket FDA-2021-D-1158; supersession chain recorded; §VII.D modification-trap and fn-61 USB-connectivity points captured; the byte-correct PDF placed under source/ and re-distilled.`

**3. Strike the SPDX/CycloneDX mandate and resolve the 81001-5-1 [VERIFY].**
`Owner: Regulatory Affairs + Cybersecurity Lead` | `Artifact: docs/external/standards/iec-81001-5-1.md L156, L193, Verification Checks table` | `Acceptance: L156 restated as "industry-accepted machine-readable formats are encouraged (FDA); NTIA October 2021 is the cited baseline"; the clause-number [VERIFY] closed against a purchased copy or the clause numbers removed and the file cites deliverables only.`

**4. Author one system-level threat model spanning the composed system, then per-DHF views.**
`Owner: Cybersecurity Lead` | `Artifact: the four cybersecurity/ threat-model instances` | `Acceptance: methodology named and justified (STRIDE or NIST 800-30) per the guidance's "justify chosen methodology"; scope covers device + Adapter + Cloud + hospital-IT boundary, not the device in isolation; assets, threat agents, threats and vulnerabilities enumerated; likelihood expressed as exploitability, not probability; every threat maps to a control and every control to a security requirement; zero {{placeholder}} tokens remain.`

**5. Produce a real SBOM built to the CISA 2026 superset.**
`Owner: R&D Lead (generate) + Cybersecurity Lead (assess)` | `Artifact: machine-readable SBOM under each DHF's cybersecurity/formal/` | `Acceptance: complete through transitive dependencies (gaps justified in writing); per-component level-of-support and end-of-support date; known vulnerabilities checked against NVD and CISA KEV each with a safety/security risk assessment; carries the CISA 2026 additions (author signature, tool name/version, generation context, component hash + algorithm, license) so it satisfies both baselines; explicit coverage of the RTOS and crypto libraries M7 declares as SOUP.`

**6. Author the Cybersecurity Management Plan — the §524B(b)(1) artifact — once, at platform level.**
`Owner: Cybersecurity Lead + Quality Engineering` | `Artifact: a new plan under pca-device/cybersecurity/, referenced by the other nine DHFs` | `Acceptance: covers lifecycle management, vulnerability and incident response, coordinated vulnerability disclosure, periodic security testing, patch development timeline, patching capability, and accountable organizational roles; the numeric commitments are set against HSCC MC2 v2 #31/#33/#35 so the plan and the contract we will be asked to sign carry the same numbers; the Adapter SAD §5 "(see Cybersecurity Plan)" reference resolves.`

**7. Resolve the Adapter→Cloud trust boundary and reconcile it with the Year-1 roadmap.**
`Owner: Systems Engineering + Cybersecurity Lead` | `Artifact: architecture-strategy.md open item (d); connectivity-adapter-system-sad.md §5/§8; D-COMM-1.4 F3 row` | `Acceptance: Z3 modeled in both states per the worked example; field-level data classification replaces the unqualified word "de-identified" with a written re-identification-risk assessment; every inbound cloud→Adapter payload type carries a signature-verification requirement equivalent to SW-025; if F3 ships in Y1, Z3-enabled is recorded as the cleared baseline and the filing reflects it.`

**8. Build the four security architecture views the guidance asks for.**
`Owner: Systems Engineering + Cybersecurity Lead` | `Artifact: a security-architecture section under each DHF's cybersecurity/` | `Acceptance: global system, multi-patient harm, updateability/patchability, and security use-case views all present; each identifies security-relevant elements, interfaces, domains and boundaries, and traces to security requirements; the multi-patient-harm view specifically addresses fleet-wide compromise via the Adapter and via the drug-library signing chain.`

**9. Extend SRS §G8 to cover the AI/cloud surface before F4 development starts.**
`Owner: Cybersecurity Lead + R&D Lead` | `Artifact: software-requirements.md §G8; the cloud-suite and alerts-engine SRS` | `Acceptance: requirements added for model/inference-payload integrity, cloud-service availability degradation behaviour (what the pump does when the alerting service is unreachable), and cloud-side authentication/authorization; SW-027's "TLS 1.2 or higher" reconciled against the SADs' TLS 1.3; each new requirement carries a cybersecurity-test verification method and a protocol placeholder.`

**10. Assemble the buyer-facing Vendor Assessment Package as a tracked commercial deliverable.**
`Owner: Cybersecurity Lead (build) + Commercial Lead (consume)` | `Artifact: MDS2 (NEMA/MITA HN 1-2019), SBOM, enterprise architecture diagram, security summary report, security whitepaper` | `Acceptance: MDS2 completed across all 21 capability categories and warranted accurate per MC2 v2 #11/#43; the package is a named Year-1 deliverable in the commercial sequencing table alongside the GPO contract-award milestone; the security review is treated as a gate on the RFP path, not a post-award task — per NIST SP 1800-8 §6.1's warning that "the Information Security team is not brought in until after contracts have been signed."`

---

## Evidence base

| Claim | Grade | Source |
|---|---|---|
| `cybersecurity_plan` resolves `null` for all 10 DHFs | `SUBSTANTIATED` — read this pass | `pdlc-demo-dhf-discovery.json`, all `dhf_roles` blocks |
| Threat model + SBOM resolve `exists: true` but are unfilled `{{placeholder}}` templates, rev 0.1 DRAFT, not released, ×10 | `SUBSTANTIATED` — read this pass | `pca-device/cybersecurity/GL-TMP-SW-002-threat-model.md`, `GL-WI-SW-002-sbom.md` |
| Vulnerability-management plan is a stub, present in only 3 of 10 DHFs; folder absent in all 10 | `SUBSTANTIATED` | `GL-SOP-SW-004-vulnerability-management-plan.md`; discovery index |
| Q-Sub manifest asserts "Per-component evidence exists" for cybersecurity | `SUBSTANTIATED` — read this pass | `qsub/composition-manifest.md` L67 |
| 510(k) manifest pulls Cybersecurity Plan / Threat Model / SBOM from three DHFs | `SUBSTANTIATED` | `510k/composition-manifest.md` L50, L61–62, L77 |
| SRS §G8 carries 5 real security requirements (SW-025…SW-029), 3 tagged CtS | `INTERNAL-DEMO` for content; `SUBSTANTIATED` that rows exist | `software-requirements.md` |
| `verification_protocols` and `verification_reports` folders do not exist | `SUBSTANTIATED` | discovery index |
| Both L1a and L1b FDA cyber-guidance files carry Document Date September 27, 2023 and the old "Quality System" title | `SUBSTANTIATED` — read this pass | L1a distilled reference; `docs/external/fda-guidance/cybersecurity.md` |
| Operative guidance is February 3, 2026, retitled "Quality **Management** System," superseding 2025-06-27 | `SUBSTANTIATED` — two independent retrievals | `research-ai-connectivity-regulatory.md` §D.5; `research-competitor-regulatory-record.md` claim 75 |
| L1b iec-81001-5-1.md asserts SPDX/CycloneDX "required"; FDA says formats "are encouraged". **Citation verdict: broken** | `SUBSTANTIATED` for the refutation | `docs/external/standards/iec-81001-5-1.md` L156 vs §D.6 |
| IEC 81001-5-1 clause numbers in the L1b file are self-flagged unverified | `UNVERIFIED` — closes only with the purchased standard | `docs/external/standards/iec-81001-5-1.md` |
| §524B(b) requires postmarket vuln plan + CVD, patch cycles, SBOM; §524B(c) three conjunctive prongs; a connected PCA pump qualifies | `SUBSTANTIATED` (verbatim statute) | §D.4 |
| §524B added by P.L. 117-328 §3305(a); effective 2023-03-29; RTA forbearance ended 2023-10-01 (88 FR 19148) | `SUBSTANTIATED` (verbatim) | §D.4 |
| §524B applies to modification submissions; Special/Abbreviated 510(k) does not exempt | `SUBSTANTIATED` | §D.4, guidance §VII.D |
| A device serviced briefly over USB "has the ability to connect to the internet" | `SUBSTANTIATED` (verbatim fn 61) | §D.4 |
| FDA anchors SBOM to NTIA Oct-2021; CISA's 2026 Minimum Elements (2026-07-29) "updates and replaces" it | `SUBSTANTIATED` for dates/contents; `INFERRED` for "build to the superset" | §D.6 |
| HICP 2023 §9.L.B: memorialize cyber requirements in contracting/RFPs, "insist on receiving a MDS2" — worked example is an infusion pump | `SUBSTANTIATED` (verbatim) | §D.7 |
| HSCC MC2 v2 (Nov 2025): SBOM #44, 3-business-day KEV notice #33, 30-day patch #31, 5-day breach notice #35, no OS within 2 yr of EoS #40; co-chaired by Mayo Clinic and Premier (a national GPO) | `SUBSTANTIATED` (verbatim) | §D.7 |
| 56% of 551 purchasing-involved professionals rejected a device on cyber grounds, up from 46%; 35% require an SBOM | `SUBSTANTIATED as vendor-sponsored survey` — use the trend only | §D.8 |
| Every major pump vendor carries CISA advisories, peaking at CVSS 10.0 (Hospira LifeCare PCA, BD Alaris Gateway) | `SUBSTANTIATED` | §D.2 |
| Unit 42: 200,000+ pumps scanned, 75% with known security gaps | `SUBSTANTIATED` (vendor research, method described) | §D.2 |
| FDA told providers to discontinue the Symbiq pump for a cybersecurity reason alone, with no known adverse event or unauthorized access | `SUBSTANTIATED` (verbatim, 2015-07-31) | §D.2 |
| ICU Medical 2025-04-10 triple Class I on CADD-Solis incl. HPCA/HSPCA; Z-1662-2025 = wireless-module connection alarms interrupting active infusion; scope expanding to 2026-05-27 | `SUBSTANTIATED` | claim 35 |
| Z-1662-2025 is a reliability failure, **not** a cyber exploit — no CVE, no advisory, no adversary | `SUBSTANTIATED` | claim 35 |
| BD 2025-02-18 Class I on Alaris Systems Manager + Care Coordination Engine Infusion Adapter (outdated automated programming requests) — the connectivity layer | `SUBSTANTIATED` | claim 22 |
| FDA Warning Letter 702535: CADD Solis VIP and Medfusion 4000 adulterated/misbranded for unfiled software changes remedying a Class I recall | `SUBSTANTIATED` (verbatim) | claims 29–32 |
| Zero infusion pumps on FDA's AI-Enabled Medical Device List (1,524 rows, three checks) | `SUBSTANTIATED` | §A.1 |
| `architecture-strategy.md` still lists trust/network boundaries and the Adapter→Cloud link as **open items** | `SUBSTANTIATED` — read this pass | `architecture-strategy.md` § *Open Items* |
| Adapter SAD §5 references a "Cybersecurity Plan" that resolves `null` | `SUBSTANTIATED` | Adapter SAD vs discovery index |
| D-COMM-1.4 ships F2/F3 in Y1 and F4/F5 in Y2 — incompatible with "Cloud egress disabled by default in the cleared baseline" | `SUBSTANTIATED` for the rows; `INFERRED` for the incompatibility | `commercial-strategy.md` vs Adapter SAD §5 |
| SW-027 specifies TLS 1.2+; both SADs specify TLS 1.3 | `SUBSTANTIATED` | `software-requirements.md`; both SADs |
| Only 1 of 7 IEC 81001-5-1 deliverables is populated | `SUBSTANTIATED` for the count; the deliverable list corroborated by the FDA guidance's independent list | `docs/external/standards/iec-81001-5-1.md` |
| Incumbent legacy debt is a product-criteria liability and a process-criteria asset; a new entrant's clean record is a denominator artifact | `INFERRED` — MC2/HICP ask for demonstrated process capability, unevidenceable at zero exposure | §D.7 + `recs-commercial.md` |
| A category-wide freeze on connected pumps hurts a new entrant more than an incumbent | `INFERRED` — fails if the freeze triggers rip-and-replace | — |
| Cloud model inference on infusion telemetry defeats the "de-identified egress" claim | `INFERRED` — fails if inference is on-prem | PCA SAD §6 vs D-COMM-1.4 F6 |
| Cyber is *the* axis where a connected pump most plausibly loses a sale | `OPINION` — no source ranks loss causes | §D.1 |
| Accepting MC2 v2 numbers contractually is the strongest available substitute for a track record | `OPINION` | — |

---

## Cross-discipline open questions

| Question | Owning discipline | Why blocked here |
|---|---|---|
| Does the February 2026 guidance's §VII.D modification trap change the regulatory category of any D-COMM-1.4 row currently marked **A** or **B**? | Regulatory Affairs | §524B content is required on any submission including modifications; whether a given change becomes a submission is a pathway call. |
| If F3 ships in Y1 with cloud egress enabled, must the cleared baseline in the 510(k) describe Z3-enabled — and does that alter the Adapter's MDDS classification? | Regulatory Affairs + Systems Engineering | The Adapter SAD already flags that behaviour beyond pass-through flips it toward accessory-of-device. |
| Are the security risks in the (unwritten) threat model to be carried in the ISO 14971 file, and under what acceptability criteria, given `risk_management_plan` and `hazard_analysis` are `null` across all 10 DHFs? | Risk Management | FDA guidance says safety and security risk management are distinct but must feed each other, and 81001-5-1 requires integration with ISO 14971. There is no risk file to integrate with. |
| Does telemetry or model-inference data leaving the hospital constitute a business-associate relationship under HIPAA, and does the "de-identified" claim meet 45 CFR §164.514? | Regulatory Affairs + Legal | A privacy-law determination, not a threat-model output. |
| What is the realistic effort and calendar to move cybersecurity evidence from stub to submission-grade across ten DHFs, and does it fit before the Q-Sub or only before the 510(k)? | Program Manager + Quality Engineering | Scope is now countable; sequencing against the gates is a program call. |
| Should a cybersecurity risk-absorption offer (MC2 v2 terms accepted as written) be a contractual commitment in the GPO/IDN motion, and what does warranting the MDS2 expose us to? | Commercial Lead + Legal | Committing the company to contract terms is not an advisor's call. |
| Do SW-025's signing root and the drug-library signing chain share a trust anchor across pca-device, Adapter and Drug Library Manager — and who owns key custody and revocation? | Systems Engineering + R&D | The 510(k) manifest names a "Signing Trust Chain" artifact that does not exist, so the chain cannot be assessed. |

---

## Counterpoints & considerations

**The stub problem may be a scaffolding artifact rather than a program failure.** Every one of these files was created by a single templating task, and the folder README says plainly *"Contents are to be authored."* Read charitably, the program knows these are placeholders. My finding is not that the team is confused — it is that **three manifests and one discovery index now report them as evidence**, and downstream consumers cannot tell scaffolding from substance. The fix for that is one honest annotation pass, which is cheap; the fix for the underlying gap is not.

**I may be over-weighting the purchasing gate.** The strongest procurement evidence is a model contract and a best-practice document — neither binding on any individual hospital — and no GPO contractually mandating MDS2 could be found. The 56% rejection figure is vendor-sponsored. It is entirely possible that in practice a security review delays a sale rather than blocking one, and that the real gate remains GPO contract status and TCO. My position rests on the *composition* — that the GPO co-chairing the model contract is also the body running the gate `recs-commercial.md` calls binary — and that is an inference, not a measurement.

**A skeptical reviewer would say cybersecurity is table stakes, not a wedge, and they would be half right.** Every competitor will file §524B content; nobody wins an RFP on having an SBOM. The defensible version is narrower: cyber is a **gate, not a differentiator** — it does not win the sale, it decides whether we are in the evaluation. That means the correct budget posture is "sufficient to pass," not "best in class." Where a genuine *differentiator* may exist is the one place incumbents structurally cannot follow: MC2 #40's two-year end-of-support OS bar, which a 2026 platform passes and a fifteen-year-old fleet cannot. Worth testing commercially before it is claimed.

**The ICU Medical recall is weaker evidence than it looks, and I want that on the record.** Z-1662-2025 is a connectivity *reliability* failure. Its legitimate use here is narrow — evidence that the integration layer is where connected pumps now fail in ways that stop therapy — and the aggregate should carry it with that qualification attached, or not at all.

---

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-08-06 | AI assistant(s) — `cybersecurity` advisor | Initial cybersecurity assessment. Contributed F-12…F-14. Established that `cybersecurity_plan` resolves `null` across all ten DHFs and that the threat-model and SBOM roles resolve `exists: true` to unfilled QMS templates — **role resolution is not content**. Identified the false "per-component evidence exists" assertion in the Q-Sub composition manifest; the two-supersession staleness of both L1a and L1b FDA cybersecurity references; the broken SPDX/CycloneDX "required" claim in the project's IEC 81001-5-1 applicability file; and the collision between D-COMM-1.4's Year-1 connected roadmap and an Adapter→Cloud trust boundary the architecture strategy still records as an open question. Separated the substantiated contractual purchasing gate from vendor-sponsored survey evidence, and declined to treat the ICU Medical wireless-module Class I recall as cybersecurity evidence. |
