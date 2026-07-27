# Readability in a regulated register — clarity without instructional drift

🔎 **Finding aid + rule sharpening.** A filed regulated document (DHF deliverable, submission narrative) is often dense and read by people new to the domain. It must be **comprehensible without becoming instructional**. The failure mode is meta-discourse: tutorial asides, audience framing, and "this section will…" scaffolding leaking into the filed body. This reference gives the discipline that raises comprehension while holding the register. It sharpens the existing standard (W8/W9 one-term-per-concept; W13 definitions; R1 present-tense declarative; R7 Terms table) — it is not new doctrine.

## The one principle

> **Put reader-help into STRUCTURE and DEFINITION (facts about the content) — never into COMMENTARY (statements about the document or the reader).**

A Definitions table *defines a term* → in-register (a fact about content). A sentence "we define this to help you" → out. A heading "Modification Protocol" *orients* → in-register. "This section describes the modification protocol" → out. The line is not "simple vs. complex" — it is **fact-about-content vs. statement-about-the-document/reader**.

## In-register vs out-of-register

| ✅ IN-REGISTER (sanctioned clarity devices) | ❌ OUT-OF-REGISTER (banned meta-discourse) |
|---|---|
| Present-tense declaratives ("The device processes CT images") | Future-tense framing verbs ("this section **will describe / present / show / discuss**") |
| Active voice with a named actor where the actor matters | Second person — "you / your" |
| Frequent, **accurate headings** carrying the organizing load | "This section / this document …" self-reference |
| A **Definitions / Terms table** | "Note that …", "It is important to understand …", "Keep in mind …" |
| First-use **appositive factual gloss** ("atrial fibrillation (AF), an irregular heart rhythm, …") | Audience framing — "for readers new to X", "to orient the reviewer" |
| Vertical **lists and tables** for dense enumerations | Rhetorical questions in the filed body |
| **Numbered cross-references** ("per § 8") | Reassurance / orientation prose threaded through operative text |

## Defined terms & acronyms

- **Expand each acronym once** at first use — "predetermined change control plan (PCCP)" — then use the acronym consistently; never re-expand, never leave an acronym unexpanded on first use.
- **Define the concept, not just the acronym (W13 sharpening).** A Terms row `DSC | Dice Similarity Coefficient` is *under-defined* — it expands the letters but a newcomer still cannot decode the acceptance criterion. Give a one-clause genus+differentia definition that states what the term *is* and, for a metric, its scale + direction: `DSC — Dice Similarity Coefficient: an overlap metric from 0 to 1; higher is better.` This is a fact about content, fully in-register.
- **Count rule.** A few terms → define inline at first use. More than ~5–7 → a front **Terms/Definitions table** (a structural device, not a "reader's guide"). Signal defined terms consistently (e.g., capitalization) so the reader knows a precise meaning attaches.
- **No elegant variation (W8/W9).** One term per concept, repeated verbatim. A reviewer reads a wording change as a *meaning* change — "better to be thought boring than confusing." This is simultaneously the biggest comprehension lever in a dense doc and a hard register requirement.
- No over-defining ordinary words; no surprise definitions that contradict ordinary meaning.
- **Spell out collision-prone abbreviations (R7.1).** An abbreviation that plausibly expands to more than one common term is a landmine — a Terms-table entry does not cure it, because the collision happens when the reader *decodes* the letters, not when they look up the definition. Canonical case: **IFU** reads as *Indications for Use* to one reader and *Instructions for Use* to another (a cleared clinical claim vs labeling content — different regulatory objects). Write the full term; do not use the bare abbreviation in the filed body.

## Constantly-speaking present tense (R1)

A rule "is constantly speaking" — draft in the present tense, not the future. Not-this / but-this:

- ❌ "No revalidation **will be** required for a UI change." → ✅ "A UI-only change **does not require** revalidation."
- ❌ "This section **will present** the acceptance criteria." → ✅ *(delete; the heading "Acceptance criteria" does this)*.
- ❌ "The device **will perform an assessment of** the anatomy." → ✅ "The device **assesses** the anatomy." *(kill the zombie noun — convert nominalizations back to verbs.)*

## Sentence hygiene

Short sentences (avg ~25–30 words), one idea per sentence, don't delay the verb from its subject, active voice where the actor matters, plain words for the connective tissue — **but preserve terms of art intact** (never simplify the legally/technically operative term). Unpack dense conditions/exceptions/element-lists into vertical lists and tables rather than long block sentences.

## Headings do the signposting

Replace every "this section describes…" sentence with an **accurate heading**. More headings are usually better than fewer, so the reader always has bearings. Headings are the only sanctioned signposting.

## Where a genuine orientation belongs

A **brief factual summary / scope section at the front** is in-register and useful for newcomers. The failure is letting that orientation **leak into the operative body** as recurring "to help you" asides. Keep orientation contained, factual, and up front.

## Sourcing note (cite correctly)

- The **binding** hook is the regulator's own readability standard where one exists (e.g., FDA's PCCP guidance: describe modifications "at a level of detail that permits understanding of the specific modifications," with individual enumeration + explicit cross-references).
- The **US Plain Writing Act (2010)** binds federal *agencies'* public documents — it does **not** legally bind a sponsor's submission. Use plainlanguage.gov techniques and Garner & Kimble's *Essentials for Drafting Clear Legal Rules* (the best model of clarity in a strictly formal, non-tutorial register) as **persuasive best practice**, adapting their legal examples to the domain.
- **Register floor:** when a clarity technique conflicts with precision or consistency, precision and consistency win — never strip a term of art, never merge two distinct defined terms for brevity, prefer the repeated defined term over a clearer-sounding synonym.

## Relationship to the standard + lint

This reference operationalizes W8/W9 (one term per concept), W13 (definition form), R1 (present-tense declarative), and R7 (filed-body Terms table). The register-lint pass should flag, in the filed body: future-tense framing verbs adjacent to describe/present/show/discuss/cover; "this section / this document"; second person "you/your"; "note that" / "it is important" / "keep in mind"; audience-framing phrases; rhetorical questions; unexpanded acronyms on first occurrence; and synonym drift on a defined term.
