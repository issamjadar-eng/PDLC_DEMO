# Regulatory Authoring Standard

**Status:** Canonical standard text of the **`regulatory-authoring`** skill — the full rules, rationale, and examples, loaded **on demand**. The one-line rule index and the apply-workflow live in `SKILL.md`; the machine lint patterns in `references/lint-signals.yml`; the rule-interaction map in `references/rule-interactions.md`. Project-specific war-story examples and QMS-mirror tooling corollaries are deliberately **not** here — they live in a project-local appendix (see § "What is NOT in this standard").

**What this standard is.** Authoring rules + writing guidelines for **controlled documents that face a regulator (FDA, EU Notified Body) or an auditor (ISO 13485 / 21 CFR 820 QMSR, Notified Body QMS audit)** — Design History File deliverables, submission narratives, and other controlled records. It has two halves that work together: **positive writing guidelines** (how to write well in the regulated register) and **defensive authoring rules** (what must not appear, with greppable lint signals). A clean lint is *necessary, not sufficient* — substance is verified by the QA-conformance pass, never by the lint alone.

---

## How to read this standard

### The three content tiers (defined here because every rule's scope depends on them)

| Tier | What it is | How it renders | Filed to the regulator? |
|------|-----------|----------------|------------------------|
| **Metadata** | HTML comments: front-matter, version changelog, AI-changelog | Invisible when the markdown renders | No — and not even rendered |
| **Internal** | Rendered-but-not-filed: rationale, conventions, governance/draft-status banners, authoring notes | A collapsed `<details>` container — see D2 | No — stripped on export |
| **Filed** | The document body a regulator reads | Top-level content, not inside a 🔒 container | **Yes** |

> **Document-control header (see the D2 exception / D3):** the controlled header — ID, version, status, effective date, approvals — is **visible controlled metadata**: it survives export and is **never 🔒-wrapped**, but it is record-identification, not regulator-facing body substance. Do not mis-tier it as the internal draft-status banner (which *is* wrapped) or as comment-metadata (which is not rendered).

**Tier scope of a rule** — unless a rule says otherwise:
- **Craft rules (most W-series)** apply to **all rendered tiers** (Internal *and* Filed) — an internal rationale block should still be clear and parallel — but never to Metadata comments.
- **Filed-tier-strict rules** apply **only to the Filed tier** (an internal block may legitimately carry an adjective, a status note, a hedge). These are tagged **`[filed-only]`**: R1, R1.1–R1.4, R3, R5, R6, R7, R9, W2, W11, and the filed-body D-rules D5, D8, D9, D10, D11, D12, D13, D14, D15. (The structural D-rules D1–D4, D6, D7 are PORTABLE / cross-tier — D2 *governs* the internal container — so they are **not** filed-only; where a rule's own header tag and this list ever diverge, the rule-level tag wins.)

### Three layers (the extraction seam)

| Layer | Prefix | Scope | Applies to |
|-------|--------|-------|-----------|
| **L1 — Universal Writing Craft** | `W` | Prose craft for any document | Every document, any reader |
| **L2 — Regulated-Document Register** | `R` | The voice of a controlled, reviewer/auditor-facing record | Any regulatory / compliance / audited document |
| **L3 — Medtech DHF/Submission Specifics** | `D` | Structure, citation, classification, jurisdiction for medtech filings | DHF deliverables + FDA/EU submission documents |

If a general-purpose writing skill is ever extracted, **L1 + L2 lift out** and the medtech skill keeps **L3** plus a dependency.

### Audience tags (on L3 rules, where they differ)

`[PORTABLE]` serves all three readers · `[FDA]` FDA reviewer-specific · `[EU-NB]` EU Notified Body-specific · `[AUDIT]` auditor-specific.

**Jurisdiction routing (read before applying D14 / D15 / D-ARB).** Determine the document's filing route from `project.yml` (`dhfs[].filing` / the submission target) or the document front-matter. Absent any signal, treat the document as **FDA-routed and flag the assumption** — never silently apply an EU rule to an unrouted doc.

> ⚠️ **`[EU-NB]` and `[AUDIT]` clause-grounding is PLACEHOLDER.** ISO 13485, 21 CFR 820 (QMSR), and EU MDR are not yet in the reference registry. Rules tagged `[EU-NB]`/`[AUDIT]` state the *authoring behavior* — which **is in force**, grounded in established design-controls/audit practice — and defer only the *clause citation*, marked **⟦ground later⟧**. A `⟦ground later⟧` marker is a **stub, not a verified reference**: do not read it as "this rule is provisional," and **never resolve it from memory** (D1 step 5) — resolve only against the imported distillation. Lint-gate it like a confirmation token: `⟦ground later⟧` (kind `regex`) must not survive into a transmitted filed body.

### Reader models (why the rules exist)

- **FDA reviewer** — skims the overview and the intended-use statement first, then audits for *consistency* and *scope creep*; pounces on contradiction, undefined terms, promissory language, claims with no evidence.
- **EU Notified Body** — reads **claim-by-claim for GSPR conformity**; expects every safety/performance claim mapped to a method-of-conformity + objective evidence, in the "state of the art / as far as possible" register.
- **Auditor** — says **"show me, don't tell me."** Traces an assertion to objective evidence; checks the record's control attributes (version, approval, effective date, change history) and conformance of the document to its governing procedure/FORM.

### Rule structure

Every rule carries: **Rule** (one normative sentence) · **Why** · **Applies** (tier / audience tag) · **Corollaries** (numbered, where any) · **Lint** (greppable signals; each tagged with its **kind**) · **Example** (a real ❌→✅ — required for every rule per this standard's own contract).

**Lint kinds** — an agent must know at load time which lints it can actually execute:

| Kind | Meaning | Agent action |
|------|---------|--------------|
| `regex` | A literal pattern an agent can grep over the text | Run it; report matches |
| `regex, partial` | A runnable pattern that over- or under-matches without packaged exclusion sets or a same-sentence judgment | Run it; treat matches as **candidates**, not verdicts |
| `filesystem` | Needs a path/existence resolution | Run it against the repo |
| `dependency-gated` | Needs data the standard doesn't ship (glossary, discovery index, `project.yml` field) | Run only if the dependency is loaded; else **flag as unverified**, don't guess |
| `judgment` | Not mechanizable — a human/QA-agent decision; an agent may surface *candidates* but never a verdict | Flag candidates; defer disposition to the QA-conformance pass |

`<project:…>` in a pattern marks a value parameterized from `project.yml` at packaging.

---

# Layer 1 — Universal Writing Craft (`W`)

*Prose craft for any document. These are the positive "writing guidelines." §"What makes regulatory writing different" at the end explains where L2/L3 deliberately **invert** general style advice — do not import a generic style guide over these.*

### W1 — One claim per sentence
**Rule:** State one verifiable claim per sentence. **Split** when each conjunct is independently verifiable (has its own acceptance criterion or evidence); **keep** when the conjuncts share one subject, verb, and verification.
**Why:** A reviewer/auditor verifies claims one at a time; a sentence carrying three independent claims lets one ride through unchecked. EU GSPR conformity is claim-by-claim.
**Corollary W1.1:** Do not coordinate a device-actor clause and a human-actor clause in one sentence — they verify differently (the device is tested; the human task is validated). Split them.
**Lint (judgment):** filed sentences with ≥2 coordinated independent capability/performance claims — agent flags candidates; the split decision is judgment.
**Example:** ❌ "The pipeline accepts images, validates them, and forwards them to the PACS, and the operator reviews the results." ✅ "The pipeline accepts images and validates them. Validated images are forwarded to the PACS. The operator reviews the forwarded results." (device-actor and human-actor claims separated — W1.1)

### W2 — Quantify; numbers over adjectives `[filed-only]`
**Rule:** Replace an evaluative-but-measurable adjective ("fast", "accurate", "real-time") with number + unit + tolerance + the acceptance reference. **If the quantity is not yet established, replace the adjective with a managed-TBD acceptance-criterion placeholder (D10) — never leave the bare adjective and never invent a value.**
**Why:** Adjectives are unfalsifiable; an auditor cannot test them and an NB cannot map them to an acceptance criterion. A fabricated number is worse than the adjective.
**Lint (regex, partial):** evaluative adjectives `\b(fast|quick|accurate|precise|reliable|efficient|robust|high-quality|real-?time|instantaneous|immediate|scalable)\b` in the filed body with no number in the **same sentence** — treat as *candidates*: some are legitimate non-evaluative uses ("immediate post-operative period"; "robust **to** malformed input" = a tested behavior). "robust" is shared with R9's examples — do not double-report one span under both.
**Example:** ❌ "Segmentation is highly accurate and fast." ✅ (quantity known) "Segmentation achieves mean Dice ≥ 0.90 (acceptance per [Segmentation Verification Report]); runtime ≤ 60 s on the specified platform." ✅ (quantity not yet established) "Segmentation accuracy and runtime meet the criteria in [Segmentation Verification Protocol] — TBD (owner: V&V lead; gate: design-verification milestone)."

### W3 — Active voice by default
**Rule:** Use active voice by default; use passive only when the system *is* the actor, the actor is genuinely irrelevant, or anonymity is deliberate and noted.
**Why:** Passive hides the actor — correctly when the device is the actor ("input is validated"), but harmfully when it buries responsibility ("it was determined…" — by whom?).
**Lint (regex):** `\bit (was|is) (determined|decided|concluded|found) that\b`; agentive passive in a responsibility statement.
**Example:** ❌ "It was determined that the classification is Class II." ✅ "[Sponsor] determined the classification is Class II." / (device-actor passive, correct) "Malformed input is rejected before processing."

### W4 — No orphan references
**Rule:** Every "it / this / these / the former" has an unambiguous antecedent in the same or immediately preceding sentence; prefer repeating the noun.
**Why:** A pronoun with no clear referent is ambiguity a reviewer reads against you.
**Lint (regex, partial):** sentence-initial `^(This|These|It) ` not immediately followed by a noun. (Mid-sentence orphans are judgment — the regex catches only the common case.)
**Example:** ❌ "The module validates input before display. This is documented in the risk file." ✅ "… before display. This input-validation control is documented in [Risk File]."

### W5 — Topic sentence first
**Rule:** Lead each paragraph with its load-bearing claim; support it afterward.
**Why:** Reviewers skim; a conclusion buried in sentence four is missed.
**Lint (judgment):** the paragraph's load-bearing claim is not in the first sentence.
**Example:** ❌ "The platform was developed over three release cycles. The team evaluated several architectures. After stakeholder review, a modular approach was chosen. The data-management module is a non-device software function." ✅ "The data-management module is a non-device software function. It was developed over three release cycles using a modular architecture chosen after stakeholder review."

### W6 — Given-then-new information flow
**Rule:** Open each sentence on known information; close on the new point.
**Why:** Lets a dense regulated paragraph be read correctly on the first pass.
**Lint (judgment).**
**Example:** ❌ "A mobile C-arm supplies the input. Guidance uses that input." ✅ "Guidance uses fluoroscopic input. That input is supplied by a compatible mobile C-arm."

### W7 — Parallel structure in lists and tables
**Rule:** Every item in a list or table column shares one grammatical shape and one level of abstraction.
**Why:** Asymmetry reads as a different *kind* of thing and hides a missing element.
**Lint (judgment).**
**Example:** ❌ "Inputs: CT images; the user logs in; storage." ✅ "Image ingestion; user authentication; image storage."

### W8 — One term per concept, one concept per term
**Rule:** Pick one term for each concept and use it everywhere; never a synonym, never an alias. (A thesaurus is a hazard here — see §inversions.)
**Why:** Two words for one object lets a reviewer suspect they are different things; in an intended-use statement a synonym can re-scope classification.
**Corollary W8.1 (verify vs. validate — the canonical trap):** "verification" (design **outputs** meet design **inputs** / the specified requirements) and "validation" (the device meets **user needs / intended use** under actual or simulated use conditions) are distinct controlled terms — never interchange them. Their precise definitions are bound to the project glossary; use the glossary's wording.
**Lint (dependency-gated):** synonym/alias sets for a registered term — requires the project glossary/registered-term list; **unenforceable without it** (flag the missing dependency rather than guessing).
**Example:** ❌ "the tablet … the OR unit … the computing device …" (one object). ✅ one registered term ("the Tablet Computing Platform") throughout.

### W9 — House conventions for numbers, units, dates, versions
**Rule:** Apply one house convention throughout — ISO dates (YYYY-MM-DD), SI units with a non-breaking space, semantic versions, explicit ranges ("5 mm to 10 mm").
**Why:** Drift ("v1" vs "1.0.0", "6/12" June-or-December) reads as fragment-assembly and creates genuine ambiguity.
**Lint (regex):** mixed date formats in one doc; `\d-\d+\s*(mm|cm|s)\b` hyphen-ranges; bare `v\d` adjacent to `\d+\.\d+\.\d+`.
**Example:** ❌ "between 5-10mm, released 6/12/26, v1." ✅ "between 5 mm and 10 mm; released 2026-06-12; v1.0.0."

### W10 — Modal precision
**Rule:** Reserve **shall / "is" (declarative)** for binding requirements, **should** for recommendations, **may** for permission. Future tense (`will`) is permitted only **outside** the filed body; in the filed body it is prohibited (see R1).
**Why:** Requirement vs. recommendation vs. permission are different regulatory objects; mixing them mis-scopes V&V.
**Lint (regex):** `\bshould\b` inside a requirement table; `\bwill\b` in a filed capability statement (see R1).
**Example:** ❌ "The application should reject malformed input." (requirement or advice?) ✅ requirement: "The application rejects malformed input." · permission: "The user may export the report." · recommendation: "The operator should verify the patient identifier before import." (Note: the bare modal "should" here is W10-legal; R5 forbids only hedge *phrases* like "should generally".)

### W11 — No marketing register `[filed-only]`
**Rule:** Strike hype adjectives — "seamless", "best-in-class", "cutting-edge", "revolutionary", "industry-leading"; state the capability instead.
**Why:** They have no regulatory meaning, can trip promotional-labeling concerns, and erode the objective register.
**Lint (regex):** `\b(seamless|best-in-class|cutting-edge|revolutionary|industry-leading|world-class|next-generation|game-chang)\b`.
**Example:** ❌ "a seamless, best-in-class planning experience." ✅ "pre-operative measurement and 3D reconstruction."

> **Adjective routing (W2 / W11 / R5, with a fallthrough).** Measurable-but-vague adjective → **W2** (replace with a number or a TBD). Marketing adjective → **W11** (delete). Hedge phrase ("we believe", "should generally") → **R5** (state flatly). A vague qualifier matching none of the three patterns ("industry-standard", "sufficient", "appropriate") is an **underspecified claim** → name the evidence (R3) or gate it as a TBD (W2/D10). Route each to exactly one bucket.

### W12 — Cross-references name the target and the relationship
**Rule:** A cross-reference names the target (by title — see D8) **and** states what the reader will find there.
**Why:** A bare "see above" forces a hunt; auditors follow every cross-reference.
**Lint (regex):** `\bsee (above|below|the .*file)\.` without a titled target.
**Example:** ❌ "See the risk file." ✅ "For the residual-risk evaluation of this control, see [Integrated Risk File] § N."

**(W12.1) Carry the gist inline.** Naming the target and relationship (W12) is necessary but not sufficient: a section built entirely from well-formed "see X" pointers still forces the reader to reassemble the argument across documents. State enough of the substance inline that the reader grasps the point **without** leaving the document; the reference then exists for the authoritative wording and audit depth, not for basic comprehension. This does **not** create drift — the *authoritative* statement still lives in exactly one place (the referenced source); the inline gist is a readable summary, not a second record. Draw the line by content type: a **fact** (classification, identifier, quantity, K-number) is single-sourced and **not** restated (D9/R8); **rationale, explanation, and enumerations** *may* be carried inline for readability (the [`audit-wiring-before-adding-fields`](../../medtech-docs/rules/audit-wiring-before-adding-fields.md) carve-out — "rationale may duplicate; facts may not"). So: reference the fact, restate the gist.
**Lint (judgment):** flag a filed section whose substance is predominantly cross-references with little self-contained content.
**Example:** ❌ "The applicable separation rules are defined in [System Architecture] § N." (the reader learns nothing without jumping) ✅ "The separation rules — clinical-content independence, boundary-data validation, runtime-configuration control, failure isolation, and code/data separation — are stated authoritatively in [System Architecture] § N." (the enumeration is inline; the reference carries the authoritative wording, not the reader's comprehension)

### W13 — Definition form
**Rule:** Define a term as **genus + differentia**, never circularly, never by itself.
**Why:** A loose or circular definition undermines every downstream use; NB scrutinizes definitions because GSPR conformity hangs off them.
**Lint (judgment).**
**Example:** ❌ "COTS: components that are COTS." ✅ "COTS: a hardware or software component [genus] that is commercially available and not developed for this device [differentia]."

---

# Layer 2 — Regulated-Document Register (`R`)

*The voice of a controlled, reviewer/auditor-facing record. Where general writing advice and these rules conflict, these win (see §inversions).*

### R1 — Declarative, as-delivered language `[filed-only]`
**Rule:** State what the system **is** and **does today**, present tense, scoped to validated capability. The filed body carries **no** future/promissory language ("will", "planned", "roadmap", "future"). Avoid both over-claim (capabilities that don't exist) and self-boxing (gratuitous absolute negatives a routine change would contradict) — state what the supported path *is*, not a closed list of what it is not.
**Why:** The filed record is the baseline future changes are judged against; over-claims invite deficiencies and unevidenceable V&V scope, self-boxing turns routine changes into apparent contradictions.
**Corollaries:**
- **R1.1 Absolute-negative scoping.** Scope a capability disclaimer to the *device-relevant* axis — deny the *device function*, not the *technology*. ❌ "The platform uses no AI." ✅ "The platform runs no clinical AI/ML function."
- **R1.2 Approach statements are internal.** Self-referential design-approach commentary is internal guidance — delete or internalize. ❌ (filed) "Our approach is to keep the architecture vendor-agnostic where possible." ✅ (filed) state the architecture declaratively; move the approach note to a 🔒 rationale block.
- **R1.3 Perform, don't recite.** The filed body *performs* obligations; it does not recite them. ❌ "Per the guidance, the impact of each non-device function must be assessed." ✅ "The impact of each non-device function is assessed: [result], per [Integrated Risk File]." (legal/teaching context → internal rationale)
- **R1.4 Status disclosures are always internal.** Process status ("pending verification", "not yet authored/implemented", "design target") is **always** internal — there is no "candid disclosure" exception. ❌ (filed) "The reproducibility study is planned but not yet complete; results will be added later." ✅ (filed) "Reproducibility is verified per [Reproducibility Report] — TBD (owner: V&V lead; gate: design-verification milestone)." + (internal) 🔒 "Reproducibility study not yet complete." (See D10 for the managed-TBD form; the *managed-TBD line* is filed, the *why-pending narrative* is internal.)
**Lint (regex):** `\b(will|planned|future|roadmap|upcoming|eventually)\b` in filed body; unscoped `(contains|has|uses) no (AI|ML|machine learning)` without a `clinical`/`device function` qualifier; `where possible|our approach|we (aim|strive|intend) to`; obligation-recital `must be assessed|guidance requires|note (that|the correct)|does not remove the .*obligation`.

### R2 — Requirement form
**Rule:** Write each requirement as one testable behavior, declarative present ("the application rejects…"), with a verifiable acceptance criterion.
**Why:** Declarative present = the requirement is met as delivered; one-behavior-per-requirement is what V&V can test.
**Lint (judgment):** requirement statements with no acceptance criterion.
**Example:** ❌ "The system should handle errors well." ✅ "The application rejects malformed DICOM input and logs the rejection (acceptance per [test protocol])."

### R3 — Claim ↔ evidence pairing ("show me, don't tell me") `[filed-only]` `[supports AUDIT, EU-NB]`
**Rule:** Every claim of a performed activity or a safety/performance property names — or TBD-points to (D10) — the artifact that substantiates it. No orphan claims.
**Why:** Auditors trace assertions to objective evidence; an unsupported "is done" is the classic finding. EU Annex II requires per-GSPR method-of-conformity + objective evidence. ⟦ground later: ISO 13485 §4.2.5; MDR Annex II §4⟧
**Lint (judgment):** filed claims of a performed activity with no adjacent evidence reference.
**Example:** ❌ "Inputs are validated." ✅ "Input validation is verified per [Test Report, rev/ID]."

### R4 — Rationale form
**Rule:** Write a rationale as **claim → basis (named standard clause / risk control / test) → consequence/fallback.**
**Why:** A rationale that asserts without naming its basis is empty; auditors read rationale as "show me your reasoning."
**Lint (judgment):** a rationale asserting a conclusion with no named basis.
**Example:** ❌ "Class A is appropriate because the risk is low." (asserts; names no clause, control, or fallback) ✅ "Class A applies [claim] because residual risk is acceptable after crediting external controls per IEC 62304 §4.3(a) [basis]; if the credit cannot be substantiated, the function reverts to Class B at filing [fallback]."

### R5 — Limitations stated flatly; no hedging `[filed-only]`
**Rule:** State a limitation or negative result as a plain declarative fact — no "unfortunately", "while not ideal", "we believe", "it appears", "should generally". (R5 targets hedge *phrases*, not the bare modal "should" in its W10 sense.)
**Why:** Defensive or hedged phrasing signals discomfort reviewers probe, and reads as an *unconfirmed claim*. Confidence is mandatory — but only on what the evidence supports (which is why W2/R3/R9 matter).
**Lint (regex):** `\b(we believe|it appears|it seems|unfortunately|while not ideal|should generally|hopefully|to some extent)\b` in filed body.
**Example:** ❌ "Although the system unfortunately cannot yet handle MRI, we believe this is acceptable." ✅ "The device processes CT input. MRI is outside the current indicated input set."

### R6 — Dated, attributable statements `[filed-only]` `[supports AUDIT]`
**Rule:** Pin every time-relative or configuration-state word ("currently", "now", "as delivered") to a date or a versioned event.
**Why:** A controlled record is read years later; "currently a Linux tablet" is unauditable without a date/version anchor. ⟦ground later: ISO 13485 §4.2.5; data-integrity ALCOA⟧
**Lint (regex):** `\b(currently|now|today|recently|at present|as delivered)\b` in filed body without an adjacent date/version.
**Example:** ❌ "currently a Linux-based tablet." ✅ "as of rev 3 (2026-06-12), a Linux-based tablet."

### R7 — Defined-term completeness and consistency `[filed-only]`
**Rule:** Every acronym/initialism used in the filed body appears in the Terms table; each term carries **one** definition, consistent across the document and against the project glossary. Extend the table in the same pass that introduces new vocabulary. (Tier note: only the *Terms-table completeness* obligation is `[filed-only]`; term **consistency** — W8 / W8.1, including verify-vs-validate — applies in **all** rendered tiers, internal blocks included.)
**Why:** An undefined acronym signals fragment-assembly; an inconsistent definition ("validation" in two senses) is both an audit finding and a real safety risk.
**Precedence:** a brand/vendor name flagged for removal by D12 is **not** an acronym to define — D12 removal wins over R7 definition.
**Lint (regex, partial):** capitalized tokens `\b[A-Z][A-Za-z]{1,7}[0-9.]*\b` in filed body, **minus** the packaged stop-word list, defined terms, and proper/brand nouns (the exclusion sets ship in `lint-signals.yml`). The pattern runs without the sets but is high-recall / low-precision — treat matches as candidates; a brand/vendor token is a **D12 removal**, not an R7 definition (precedence above).
**Example:** ❌ "forwards them to the PACS" (PACS never defined). ✅ add a Terms row "PACS — Picture Archiving and Communication System" and use it consistently.

**Corollary R7.1 (collision-prone abbreviations are spelled out) `[filed-only]`:** An abbreviation whose letters plausibly expand to **more than one common regulatory term** is *collision-prone*: spell out the intended full term in the filed body and do **not** use the bare abbreviation. The canonical landmine is **IFU** — it reads as *Indications for Use* to one reader and *Instructions for Use* to another; write "**Indications for Use**" (or "Instructions for Use") in full. (Other collisions: **DHR** — Device History Record vs Design History Record.)
**Why:** the two expansions are **different regulatory objects**. *Indications for Use* are the cleared clinical claims — changing them routes to a new marketing submission; *Instructions for Use* are labeling content — routinely updated. A reader who resolves "IFU" to the wrong expansion **misreads a scope gate**: "no IFU change" reads as forbidding any labeling edit rather than forbidding an indications change (the real, observed confusion). A Terms-table entry does **not** cure this — the collision happens at the point of *reading*, not the point of *definition* — so R7 completeness is necessary but not sufficient; spell the term out. Which expansion a project intends is a project fact (its glossary); the rule to spell it out is universal.
**Precedence:** refines R7 / W8; where a project deliberately abbreviates a *non-colliding* term, R7 (define once) governs and R7.1 does not apply.
**Lint (regex):** bare `\bIFU\b` / `\bDHR\b` in the filed body (registered collision-prone set in `lint-signals.yml`).
**Example:** ❌ "no clinical-claims/IFU change." ✅ "no clinical-claims change; no Indications-for-Use change." (labeling / Directions-for-Use updates are permitted and stated separately, so the two are never conflated.)

### R8 — Cross-record consistency `[supports AUDIT]`
**Rule:** A claim must not contradict the governing/parent record or a sibling controlled document — classification, intended use, and interface facts must agree across the record set.
**Why:** Cross-record contradiction is a high-value audit/review finding (it proves the process didn't catch a divergence). Generalizes the intended-use-boundary rule (D13) to every controlled cross-reference.
**Scope of the obligation:** before asserting conformance, load the parent/manifest record; an agent editing one file in isolation **cannot** verify R8 and must flag it **unverified** rather than declare pass.
**Lint (dependency-gated / judgment):** cross-doc check — needs the parent/manifest loaded; not an in-file regex.
**Example:** ❌ system doc: "The analysis module requires a calibration file." / IFU: "The analysis module operates standalone." (two records disagree on an interface fact) ✅ both records state: "The analysis module operates standalone; a calibration file enhances results when available."

### R9 — Unevidenced property claims are removed or gated, not re-voiced `[filed-only]`
**Rule:** If a **claim of an achieved property or a performed activity** — a performance, safety, security, or quality assertion — has **no supporting evidence and none planned**, the fix is to **remove it or convert it to a managed TBD (D10)** — never to rephrase it into confident declarative voice. Declarative voice on an unevidenced property claim is a worse finding than a hedge.
**Scope — what R9 does NOT touch:** (a) a **design requirement** (R2) is *not* a property claim — its acceptance criterion is its gate and its evidence is the downstream trace (R3/D9); a well-formed "the application rejects X" requirement is **kept** (verify it carries an acceptance criterion + trace target — never delete it for lacking an inline evidence pointer). (b) a **scope-boundary negative / limitation** ("MRI is not supported") is governed by R1/R5 (state it flatly), not R9.
**Why:** The anti-hedging push (R5) and the declarative push (R1/R2), applied mechanically, can turn "we believe X is robust" into "X is robust" — a confident, unsupported, harder-to-detect false claim. R9 is the guardrail: confidence on a *property* must be *earned* by evidence (R3), not manufactured by voice. **Routing:** a requirement → R2 + D9 trace; an *evidenced* property → R3; an *unevidenced* property → R9.
**Lint (judgment):** a filed declarative **property/performance/safety** claim with no evidence reference and no TBD gate — agent flags; disposition (is there evidence? is it actually a requirement?) is the QA pass.
**Example:** ❌ "The architecture is robust enough for the indicated procedures." (property claim; no evidence, no number) ✅ (evidence planned) "Architectural robustness is established per [System Verification Plan] — TBD (owner; gate)." ✅ (not substantiable) delete the sentence. **Contrast — NOT an R9 target:** "The application rejects malformed input (acceptance per [test protocol])." is a *requirement* (R2) and stays.

---

# Layer 3 — Medtech DHF / Submission Specifics (`D`)

*Structure, citation, classification, and jurisdiction for medtech filings. Audience-tagged.*

## Process

### D1 — Pre-flight: schema-first, skeleton-first `[PORTABLE]`
**Rule:** Before drafting body content of any governed document: (1) read the governing QMS contract (FORM/SOP/WI) for *shape*, not ideas; (2) write the FORM-schema map — every column/section/controlled-vocabulary assigned **present / deferred (named gate + owner) / N/A (justified)**; (3) start from the three-tier skeleton (D2), never a blank page; (4) write the filed tier for the regulator; (5) quote-verify every QMS §-citation at the moment of writing it; (6) after editing, run the lint then the QA-conformance pass.
**Why:** Writing content first and applying the structural contract afterward is the root cause of repeated reactive rework; a missing FORM column is invisible until an adversarial review when no schema map exists; a cited provision invented from pattern memory survives until an adversarial agent catches it.
**Lint (judgment):** a new FORM-instance draft with no schema-map artifact (internal block or task doc) = pre-flight skipped.
**Example:** ❌ body content drafted first and the FORM-schema map never written — a missing mandatory column surfaces only at an adversarial review. ✅ a schema-map block listing each FORM column with `present / deferred (owner, gate) / N/A (reason)` written *before* the body is drafted.

## Structure & content control

### D2 — Three-tier content model with bounded internal containers `[PORTABLE]`
**Rule:** Apply the three tiers defined in the preamble. Every Internal region is a collapsed `<details>` container whose summary begins `🔒 INTERNAL …` and whose last line is a visible `**🔒 END INTERNAL**` marker. Filed content never sits inside a container; Internal content never sits at top level — including the **draft-status / governance-commentary** banner before the first filed heading. **Exception (do not conflate with D3):** the document-control header — ID, version, status, effective date, approvals (D3) — is **filed metadata/header content**, not the internal draft-status banner; it stays present and visible, not wrapped in a 🔒 container.
**Why:** The clean export that strips internal tiers may not exist yet; the convention is human-enforced, so visual boundedness is the control. The tiers route content to different readers (the reviewer reads the exported filed body; the auditor reads the whole controlled record including internal tiers).
**Corollaries:**
- **D2.1 Column-level marking.** A scaffolding column in a filed-destined table gets a `🔒` header prefix + named disposition. ❌ header "Notes (internal)" (no rendered distinction). ✅ header "🔒 Flags (internal — issues log)".
- **D2.2 Coded-value legibility.** Filed cells carry the format **`<code> - <controlled-vocabulary label>`**, never a bare code. ❌ "02". ✅ "02 - Intended use of the product".
- **D2.3 Filed-cell commentary.** Filed cells are written for the regulator: value + clean subcategory ("14 - Other (Security)"), never process commentary (provisional/confirm/tailoring asides) — R1.4 status-disclosure at cell granularity.
- **D2.4 No hedge words in filed cells/headings.** ❌ header "Proposed Control"; cell "draft — input validation". ✅ header "Risk Control"; cell "Input validation". (draft status lives once in metadata `state:` + the internal status banner.)
**Lint (regex):** unbalanced `^<details>`/`^</details>`; `<summary>` not beginning `🔒 INTERNAL`; container lacking a `🔒 END INTERNAL` final line; governance/draft banners at top level; `\(internal[^)]*\)` in a table header without a leading `🔒`; bare `\| *[0-9A-Z]{2,4} *\|` enum cells without a label; `\b([Cc]andidate|[Pp]roposed|[Pp]reliminary)\b` in filed headings/headers/cells.
**Example:** ❌ (internal content at top level)

    ## 3. Software Safety Classification
    Class B applies. Note: still provisional pending the formal risk decomposition.

✅ (filed declarative; status routed to a bounded container)

    ## 3. Software Safety Classification
    The software safety class is Class B.

    <details><summary>🔒 INTERNAL — classification status (not filed)</summary>

    Provisional pending the formal risk decomposition. Owner: RA lead; gate: design-verification milestone.

    **🔒 END INTERNAL**
    </details>

### D3 — Document-control header completeness `[PORTABLE, AUDIT]`
**Rule:** Every controlled document carries, as a **filed** authored block (not wrapped in a 🔒 container — see D2 exception): unique ID, version/revision, status (draft/approved/effective/obsolete), effective date, author + reviewer + approver with dates, and a change-history table. Present and complete, not left to the downstream vault.
**Why:** Document control is the single most-cited audit area; a missing approver/effective date is a finding regardless of body quality. ⟦ground later: ISO 13485 §4.2.4/§4.2.5; 21 CFR 820.40⟧
**Lint (judgment):** missing any of {ID, version, status, effective date, approver+date, change-history}.
**Example:** ✅ a header block: "Doc ID: SAD-001 · Version: 1.2 · Status: Approved · Effective: 2026-06-12 · Author: A.B. (2026-06-10) · Reviewer: C.D. (2026-06-11) · Approver: E.F. (2026-06-12)" followed by the change-history table.
*(The authoring contract — which fields the author populates — lives here; vault enforcement/retention lives in the document-control SOP.)*

### D4 — Change-history / revision-rationale legibility `[PORTABLE, AUDIT]`
**Rule:** Each version bump records *what changed and why* in auditor-legible terms, not "updated". (The AI-changelog is internal provenance only and does **not** satisfy the controlled change-history obligation.)
**Why:** Change control requires the nature of the change and its approval to be identifiable. ⟦ground later: ISO 13485 §4.2.4; 21 CFR 820.40(b)⟧
**Lint (regex):** change-history cells matching `^(updated|changes|edits|revised)\.?$` (bare, no substance).
**Example:** ❌ "| v1.1 | 2026-06-25 | Updated. |" ✅ "| v1.1 | 2026-06-25 | Revised § 5 module boundary to add the standalone-operation interface fact; approved by RA lead. |"

### D5 — Contiguous filed section numbering `[PORTABLE]`
**Rule:** The filed body's section numbers read contiguously (1…N) with no gaps. A gap has two causes — a section was internalized/removed (renumber the rest + move content to the tail as a 🔒 container) **or** a mis-numbering typo (relabel only). The agent detects the gap; the author confirms which case. **In-file action is mandatory; cross-document `§ N` pointer sweeps the agent cannot edit are listed/flagged for cross-doc tooling, not silently assumed done.**
**Why:** A § 10 → § 12 jump reads as a missing section — worse than the content it hides.
**Lint (regex):** filed `^## [0-9]+\.` headings not a contiguous ascending sequence (evaluated outside 🔒 containers); `§ <N>`/`Section <N>` to a number with no matching filed heading.
**Example:** ❌ filed headings jump "## 7. …" then "## 9. …" (the § 8 gap reads as a missing section). ✅ either renumber "## 9" → "## 8" (typo case) or, if § 8 was internalized, move it to the tail as a 🔒 container **and** renumber the rest, sweeping `§` cross-references.

### D6 — Markdown / diagram hygiene `[PORTABLE]`
**Rule:** No prose line inside a markdown table (it splits the table); relative links must resolve; in any one ASCII-diagram block (a single code-fence), every box-border row is byte-equal in width — measure and regenerate if not, do not freehand a fix.
**Why:** The rendered/exported artifact is what reviewers see; a split table, dead link, or ragged diagram reads as carelessness in a filing.
**Lint (regex + filesystem):** non-`|` line between `|` rows of one table (regex); link targets failing an existence check (filesystem); within one code-fence, box-bordered lines with >1 distinct length (regex).
**Example:** ❌ a prose sentence on its own line between two `|`-table rows (splits the table in two); a relative link `[X](../wrong/path.md)` that does not resolve; an ASCII box whose border rows differ in width. ✅ move the prose above/below the table; fix the link to a resolving path; regenerate the box so every border row is byte-equal in width.

## Conformance to the contract

### D7 — Conform to the governing QMS template `[PORTABLE, AUDIT]`
**Rule:** A document instantiating a FORM/SOP/WI conforms to its column schema, scoring scales, mandatory sections, and sign-off rows; any deviation is documented and justified, not silent.
**Why:** "As-written-vs-as-done" is the core of a QMS audit; an invented or omitted FORM column is a nonconformity even if the prose reads well. ⟦ground later: ISO 13485 §4.1.1/§4.2.4; 21 CFR 820.30(a)/(j)⟧
**Lint (dependency-gated):** needs the governing FORM (from the taxonomy `governing_qms`); compare columns/sections; flag unverified if the FORM isn't loaded.
**Example:** ❌ a trace matrix with a "Priority" column the governing FORM does not carry, added silently. ✅ the FORM's columns, in the FORM's order; any deviation carries a documented justification.

### D8 — Title-based citations; no internal artifacts in the filed body `[PORTABLE]`
**Rule:** Cite controlled documents by **document title** (hyperlink for internal navigation, stripped at export). Never visible in a filed body: raw repo paths, task references, finding IDs, config-file citations, pointers to non-published metadata, or internal mirror paths for external references (cite the actual guidance/standard title + status + date).
**Why:** Internal file structure means nothing to a reviewer and reads as unfinished work; task/finding IDs leak internal process.
**Relationship to D9:** D8 governs *how* you cite; D9 governs *what* you may trace to. A link to a `submissions/` proposal is a **D9** violation (wrong target), not merely a D8 formatting issue — fix the target, not the path.
**Lint (regex):** `<project:task-id>` (e.g. `<person>/\d+`), `gap-analysis|F\d+|RA-\d+`, `project\.yml`, `\.taxonomy\.yml`, `docs/(project|internal|external)/`, `<project:retired-tree>`, `see the change ?log` — evaluated **outside** metadata comments and 🔒 containers.
**Example:** ❌ "See docs/project/_confluence/.../v1.0.0.md (per task <person>/254, finding F-12)." ✅ "For the module boundary, see [System Architecture Document] § 5." (link resolves internally and is stripped at export; no path, task ID, or finding ID in the filed text)

### D9 — Trace targets are controlled artifacts, resolvable `[PORTABLE, AUDIT]`
**Rule:** Trace/coverage targets are **controlled DHF deliverables** (named TBD placeholders allowed), never submission proposals or internal analyses (Q-Sub briefs, strategy docs, gap analyses, input-analysis notes). Every trace reference uses a stable controlled identifier and is followable in both directions. Before writing "TBD/not-yet-authored", search the DHF trees first **if the discovery index is available**; if it is not, treat the claim as unverified and flag it rather than asserting.
**Why:** Proposals *argue*; DHF artifacts *evidence*. A trace to a proposal traces to nothing auditable; a stale "not yet authored" is an over-modest inaccuracy but still an inaccuracy.
**Lint (regex + dependency-gated):** filed-body `](…submissions/` links or `Q-Sub`/`Q<N>.<N>` prose (regex); trace targets under `submissions/`/`input-analysis/`/`_analysis/` (regex); "forward-plan"/"not yet authored" about doctypes that exist (dependency-gated on the discovery index).
**Example:** ❌ "Cybersecurity risk is addressed per the predicate analysis and the Q-Sub cybersecurity brief." ✅ "Cybersecurity risk controls trace to [Threat Model] and [Cybersecurity Risk Assessment] within the integrated risk file." (named TBD placeholder acceptable if not yet authored)

### D10 — Managed TBDs (owner + gate) `[PORTABLE, AUDIT]`
**Rule:** Every placeholder in a controlled record carries an owner and a closure gate (who, by when/which milestone). The managed-TBD **line** is filed; the *why-pending narrative* is internal (R1.4).
**Why:** An auditor distinguishes a planned, tracked gap (acceptable) from an uncontrolled one (finding).
**Lint (regex):** bare `\bTBD\b` in filed body not followed by an owner + gate.
**Example:** ❌ "TBD." ✅ "TBD — [Integration V&V protocols], owner: V&V lead, gate: design-verification milestone."

### D11 — Non-device software class is QMS policy, not a filed obligation `[FDA]`
**Rule:** Non-device software (Non-Device-MDDS, administrative "other functions") owes FDA no IEC 62304 class — FDA reviews its *impact* on device functions (MFD / §520(o)(2)), not its lifecycle rigor. If a 62304 class is stated for non-device software, label it explicitly as the manufacturer's QMS lifecycle-rigor assignment, orthogonal to device status; keep classification deliberations in internal rationale. Originating risk does not bar Class A (IEC 62304 §4.3(a) external-control limb); determination-first is legitimate with (a) documented basis, (b) defined fallback, (c) risk-file consistency, (d) awareness of the EU Rule 11 companion (D15) — (a)–(d) are judgment + cross-doc, not lintable in-file.
**Why:** Classification churn in a filed body invites questions FDA wasn't going to ask; a class with no documented basis or fallback is the actual audit finding — not the class value.
**Lint (regex):** `candidat(e|cy)|reclassif|pending (formal )?(risk assessment|decomposition)` in filed body; 62304 class cells for non-device rows without the orthogonality note nearby.
**Example:** ❌ "The data-management module is IEC 62304 Class A; class is candidate pending the formal risk decomposition." ✅ "FDA reviews the data-management module for its impact on device functions under the multiple-function-device framework (§ 520(o)). The IEC 62304 Class A designation is the manufacturer's QMS lifecycle-rigor assignment, orthogonal to device status." (basis + fallback live in internal rationale)

## Naming & specificity

### D12 — Two-layer specificity for device/instance naming `[PORTABLE]`
**Rule:** Be **specific on modality + clinical function** (design-true, validation-bound — e.g., "intra-operative fluoroscopic (X-ray) images"); **generic-with-example on swappable instances** ("a compatible fluoroscopic imaging device (e.g., a mobile C-arm)"). Make/model lists live in the item DHF, not the system doc. The "e.g." is the change-control-open seam.
**Why:** Dropping the modality reads as un-validated scope creep; hard-coding the instance closes the door on compatibility changes the change-control plan is meant to cover.
**Tier source:** whether the current document is system-tier or item-DHF (which governs where make/model lists belong) comes from `project.yml dhfs[].role` — do not guess.
**Corollaries:**
- **D12.1 COTS sourcing language.** "supplied by <maker>" reads as "manufactured by" — for COTS write "sourced and configured by <maker>"; define COTS in Terms.
- **D12.2 Compatibility homes.** Architecture docs define the interface *envelope/spec*; the IFU/DFU *asserts* compatibility; V&V records identify the *tested* make/model/version. Never pre-assert vendor/model lists in a system-tier filed body.
- **D12.3 No brand prefix on COTS.** Name the component generically ("the video capture device"); state brand membership separately. Interface lists are envelopes — "compatible … (e.g., …)".
- **D12.4 Computing platform.** Name a platform by function ("a general-purpose tablet computing platform") with the instance/OS as a present-tense configuration fact; the spec lives in the item DHF.
- **D12.5 Cloud / infrastructure instances.** A named cloud provider or managed service in a filed architecture body is a swappable instance, not architecture — name it by function with an `e.g.` ("an object-storage service (e.g., a managed cloud object store)"); the specific provider, where load-bearing (e.g., a data-residence or cybersecurity claim), is stated as a dated configuration fact, not baked into the architecture. Load-bearing example: ✅ "ePHI is stored in a cloud region within [jurisdiction] (as of rev N (YYYY-MM-DD), [named provider, region])" — the provider is named because data residency is a stated control, as a dated fact (R6).
**Lint (regex):** `<brand> (video capture|tablet|capture device)` name patterns; `supplied` adjacent to a maker name on COTS; exhaustive interface lists without `e.g.`/`compatible`; `\b(AWS|S3|Azure|GCP|Okta|Datadog|Snowflake)\b` as architecture rather than `e.g.` examples.
**Example:** ❌ "Guidance runs on the Acme T800 tablet and captures video via the Acme FrameGrabber Pro; images are stored in AWS S3." ✅ "Guidance runs on a general-purpose tablet computing platform and captures intra-operative fluoroscopic (X-ray) images via a compatible video capture device (e.g., a frame-grabber); images are stored in an object-storage service. Tested make/model/version are identified in [item V&V records]." (Note: "Acme" brand removed per D12.3 — it is **not** an acronym for R7 to define.)

## Intended use & boundary

### D13 — Intended-use statement form and boundary consistency `[PORTABLE]`
**Rule:** Write the intended-use / intended-purpose statement in canonical form — **who** uses it, to do **what**, on **what input**, for **what clinical/administrative purpose**, in **what setting** — and reuse it **verbatim** everywhere, never paraphrased. **Any slot whose value is not supplied by a controlled source becomes an explicit managed-TBD token (D10) — never inferred or invented.** Never attach "clinical" (or "patient care", "diagnostic", "guidance") to a function positioned as administrative/non-device; every mention agrees with the boundary section.
**Why:** The intended-use statement is the single most-quoted line in any submission; it sets classification and predicate comparability. One loose overview sentence can contradict the entire non-device argument, and the overview is read first and quoted most. An agent expanding the canonical form will *hallucinate* missing slots unless told to gate them.
**Lint (regex + judgment):** the intended-use statement paraphrased (differs token-for-token) across sections — best made mechanizable with an IU-statement anchor/marker (judgment without one); `clinical` within a sentence naming an administratively-positioned function (regex).
**Example (canonical form, with a gated unknown slot):** ✅ "[Module] is intended for use by [clinician role] to perform [clinical/administrative function] for [the indicated procedure — TBD, owner: RA] using [imaging modality]." — then reused verbatim.
**Example (boundary violation):** ❌ "The reporting module gives surgeons clinical insight into patient outcomes." ✅ "The reporting module produces administrative post-operative case summaries and utilization reports. It makes no clinical recommendation and provides no diagnostic or treatment guidance."

## Jurisdiction band

### D-ARB — Dual-audience arbitration `[FDA, EU-NB]`
**Rule:** When one sentence must satisfy both an FDA reviewer and an EU NB, use jurisdiction-neutral phrasing by default; **"forced" = the concept has no jurisdiction-neutral term** (e.g., the classification rule itself differs between markets) — then **intended-purpose** governs and "indications for use" is the US gloss. Single-market documents use that market's vocabulary (per the routing signal in the preamble).
**Why:** Two parallel copies drift; a neutral default with a clear arbitration rule keeps one record serving both readers.
**Example:** ❌ two parallel copies — a US section "indications for use: …" and an EU section "intended purpose: …" — that drift apart over revisions. ✅ neutral default "intended for pre-operative planning of [procedure]" (serves both); ✅ forced "the intended purpose is … (US indications for use: …)".

### D14 — FDA framing `[FDA]`
**Rule:** Use FDA vocabulary for FDA-routed documents: indications for use; 510(k)/substantial-equivalence/predicate framing; MFD / §520(o); PCCP.
**Corollaries:** **(D14.1) PCCP boundary** — architecture/non-PCCP filed docs carry at most one PCCP cross-reference sentence; perimeter tables and change categories live in the PCCP package or internal containers. **(D14.2) SE-argument tone** — comparison framed as tabular new-vs-predicate; differences stated plainly and shown not to raise different questions of safety/effectiveness, never minimized. **(D14.3) Predicate-selection narrative** — if predicate suitability is asserted, carry the selection rationale and disclose+mitigate any factor failure. **(D14.4) Confirmation token** — the one sanctioned hedge token marks a position the sponsor asks FDA to confirm; convert to prose or remove before transmission.
**Precedence:** for an EU-routed document, D15.6 (zero PCCP) governs over D14.1.
**Lint (regex):** `PCCP` in >1 section of a non-PCCP filed doc; change-category lists outside the PCCP package; `<project:confirm-token>` (e.g. `\[Q-Sub:`) surviving in a transmitted filed body.
**Example:** ❌ (SE) "Any differences from the predicate are minor and not worth detailing." ✅ "Technological differences from the predicate are listed in Table N; each is shown not to raise different questions of safety or effectiveness."

### D15 — EU Notified Body framing `[EU-NB]` ⟦clause-grounding placeholder⟧
**Rule:** Use EU vocabulary for NB-routed documents. **(D15.1) Intended *purpose*,** not "intended use"/"indications for use" — the anchor every GSPR conformity statement traces back to. **(D15.2) State of the art** — affirmatively reference a state-of-the-art development lifecycle, risk management, information security, and V&V. **(D15.3) "As far as possible" (AFAP)** risk language weighed against the benefit-risk ratio — not economic-feasibility hedging ("where commercially practical"), which an NB reads as non-conformance. **(D15.4) GSPR-conformity trace** — EU-facing design content is traceable to a GSPR line item with Applicable + method-of-conformity (referenced harmonized standard) + objective evidence (extends D9 into the EU register). **(D15.5) Rule 11 classification** — EU software class is driven by intended purpose under MDR Rule 11, independent of platform; cite Rule 11 reasoning, not the FDA class. **(D15.6) Zero PCCP** — PCCP is US-only; EU change is governed by significant-change / ongoing conformity assessment; the correct number of PCCP references in an EU document is zero. **(D15.7) CER register** — clinical claims phrased against clinical-evaluation conclusions and MDR equivalence (clinical/technical/biological), distinct from FDA "substantial equivalence". **(D15.8) EU label particulars** — Authorised Representative, UDI carrier, intended-purpose-on-label.
**Why:** Every FDA term of art reads wrong if transplanted into an NB-facing record. ⟦ground later: MDR Annex I §1/§2-8/§17.2/§23; Annex II §4; Rule 11; Art. 61/Annex XIV — import primary MDR + MDCG distillations before asserting clause text⟧
**Lint (regex):** "indications for use"/"510(k)"/"PCCP"/"substantial equivalence" in an EU-routed doc; "where commercially practical" in a risk statement.
**Example:** ❌ (EU doc) "The indications for use are pre-operative planning; changes are managed under the PCCP." ✅ "The intended purpose is pre-operative planning. The software is classified under MDR Rule 11; significant changes are assessed through the Notified Body's ongoing conformity assessment."

---

## What makes regulatory writing different (read before importing any general style guide)

A generic style guide will *degrade* a regulated document, because several general-writing instincts are actively wrong here. The skill and the copy-editor agent must know which to **invert**:

1. **The document is legal evidence, not communication.** Optimize for verifiability and survival under adversarial reading, not "good enough to understand".
2. **Consistency outranks elegance.** General guides prize synonym variety; here, one term per concept forever (W8), the intended-use statement reused verbatim (D13). A thesaurus is a hazard.
3. **Passive voice is sometimes correct** (device-as-actor: "input is validated") — the rule is precision about *when* (W3), not a blanket ban.
4. **Declarative present = a verification commitment**, not a stylistic choice (R1, R2). "Will" is a different regulatory object, not merely weaker prose.
5. **Hedging is forbidden where general writing encourages caution** (R5) — but only on *evidenced* claims; an *unevidenced* claim must be removed or gated, not voiced confidently (R9). Confidence is mandatory, and earned by evidence (W2/R3).
6. **The reader is hostile-by-role, and three readers at once** — FDA reviewer (consistency/scope), EU NB (claim-by-claim conformity), auditor (show-me-evidence). One standard serves all three adversarial modes.
7. **Tier-awareness has no general-writing analog** (D2) — the same paragraph is written differently depending on which reader will see it; flattening internal and filed voice into one tone destroys the control.

---

## Crosswalk — original G/P capture → this standard

| Original | New ID(s) |
|----------|-----------|
| G-0 Pre-flight | D1 |
| G-1 Declarative as-delivered | R1 (+ R1.1–R1.4) |
| G-2 Two-layer specificity | D12 (+ D12.1–D12.5) |
| G-3 PCCP boundary | D14.1 |
| G-4 Title-based citations | D8 |
| G-5 Three-tier model | D2 (+ D2.1–D2.4); project-tooling corollaries → appendix |
| G-6 Hedge tokens | D14.4 |
| G-7 Non-device classification | D11 |
| G-8 Markdown/diagram hygiene | D6 |
| G-9 Contiguous numbering | D5 |
| G-10 Acronyms defined | R7 |
| G-11 Trace targets | D9 |
| G-12 Intended-use boundary | D13 (+ R8 generalized) |
| P-series (writing craft) | W1–W13 |
| EU additions (regulatory lens) | D-ARB, D15 |
| Auditor / evidence-integrity additions (quality lens) | R3, R6, **R9** (unevidenced-property guard), D3, D4, D7, D9, D10 (+ AUDIT tags) |
| Agent-usability additions (v3) | W1.1, W8.1, D2 exception, D12.5, lint-kind tags, tier-scope, jurisdiction routing |

---

## What is NOT in this standard (project-local appendix)

Real and useful but **project-specific** — they live in a project-local appendix (`docs/internal/…`), never in the registry-shipped standard:

- **War-story examples** (specific documents, version numbers, the defect histories that motivated each rule).
- **QMS-mirror tooling corollaries from G-5** — the Confluence-collapse / Windchill-vault-strip mechanics, customer-convention sourcing, the "third-party analysis is counter-analysis" demotion, provenance-at-top sources tables, real-source ALM-key stitching/linking, verbatim multi-cell-fidelity extraction.
- **Project ID schemes** — the project's task-ID, decision-ID, finding-ID, and ALM-key patterns (the lint reads these from `project.yml`, not the standard).
- **Confirmation-token vocabulary** (the specific pre-transmission token + any waiver list).
- **The dependency data sets** the dependency-gated lints need — the project glossary/synonym map (W8), the stop-word + defined-term exclusion lists (R7), the discovery index (D9), the `dhfs[].role` tier map (D12) — are project data, read at runtime, not embedded here.

## Lint single-sourcing (packaging note)

At packaging, every `Lint:` block extracts to `references/lint-signals.yml` (one row: `{id, rule, kind, pattern, zone, jurisdiction, severity, message}` — note the **`kind`** field, from the Lint-kinds table above); the script reads the YAML + `project.yml` (no hard-coded names), and this standard's `Lint:` lines render from the YAML — so doc and script can never drift. A clean lint is necessary, not sufficient; substance is the QA-conformance pass.

---

## Changelog

_(Standard content version history; the skill's own changelog lives in the skill `README.md`.)_

- v4: Second-review polish (dogfood + regression-audit + domain review). R9 scoped to achieved-property/performance/safety claims, excluding design requirements (kept; route to R2 + D9 trace) and scope-boundary limitations (R1/R5). Backfilled examples (D5, D6; ❌ contrasts on D1, D-ARB). `[filed-only]` list de-broadened (structural D1–D4/D6/D7 are cross-tier; rule-level tags win). W2 + R7 lints → `regex, partial`. R7 tier-note. Adjective-routing fallthrough. `⟦ground later⟧` honesty guard + lint-gate. D2/D3 header → "visible controlled metadata". W8.1 verify/validate tightened. D12.5 data-residence example.
- v3: Agent-usability refinement. D2/D3 header carve-out; W2 quantity-not-yet-established → managed-TBD; new R9; D13 unknown-slots → TBD. Tier definitions in preamble + `[filed-only]` tags; per-lint `kind`; jurisdiction routing; adjective routing; modal reconciliation; precedence pairs; dependency-gated marks. Examples added to the 8 high-cost rules; W1.1, W8.1, D12.5 added.
- v2: Restructured a defect-derived lint capture into the three-layer standard (L1 writing craft / L2 regulated register / L3 medtech specifics); added the W-series writing guidelines, the EU-NB band (D15) + D-ARB, and the AUDIT-tagged auditor additions. Crosswalk + project-local-appendix boundary.
