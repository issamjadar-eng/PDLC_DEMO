# Pre-submission package consistency — the cross-document "seam" checks

Per-document tooling (the leak/repo-path scrub, the authoring lint, the scope lint) validates
each document **in isolation**. A whole class of defect survives that scrutiny because it does
not live *in* any single document — it lives in the **seam between two documents**, where a
pointer in one document *describes*, *numbers*, *reaches for*, or *anchors* another. Each side is
internally clean; only the pair is wrong. This note names the seam-defect classes and the
principle underneath the worst of them.

**Why these keep recurring** (the honest root cause): a submission package is a tightly
cross-linked set that is authored and edited *incrementally*. Every document is internally
reviewed (lint, copy-editor, QA), but until a seam checker exists nothing verifies the
*relationships between* documents — and those relationships are exactly what a human reviewer
skims past. Two distinct failure modes produce the errors: **(a) drift from non-uniform
updates** — a spine fact (an attachment number, a question's ID/transmit-status, a doc's
location, a sibling's tier) changes in its home doc and the referencing siblings are not
updated in lockstep (seams 2, 3, 4); and **(b) a cross-reference authored wrong from the
start** — a tier mislabel (seam 1) or a miscited external source (a statute/standard section),
which no *package-internal* check can catch — that is the job of an independent **reference
audit** against the byte-correct source, run before transmit. The seam checks below close (a)
and the structural half of (b); the citation half stays with `/reference-audit`.

## The three seams

| # | Seam defect | The rule that is violated | Why a per-doc lint misses it |
|---|-------------|---------------------------|------------------------------|
| **1** | **Cross-reference accuracy** | A pointer that *describes* a target document must match the target's **own** self-description. If doc A calls attachment K "the **full** analysis" but attachment K's own § 1 says it is "an **abbreviated** summary; the full analysis accompanies the [later submission]", the two disagree. | The describing words are correct English in doc A; the self-label is correct English in doc K. Neither doc is wrong alone — only the claim *about* K, made in A, contradicts K. |
| **2** | **Attachment-number consistency** | Every prose "attachment N" reference must agree with (a) the package's **numbered attachment table/list** and (b) the **assembly manifest's** transmitted set. | The prose is grammatical; the table is well-formed; the manifest parses. The defect is only visible when you *count* across all three — e.g. prose that forgets to count the cover/transmittal letter as attachment 1 runs one behind a table that does count it. |
| **3** | **Folder-boundary compliance** | Every **transmitted** document must live **inside** the filing folder (`.../submissions/<filing>/`), and filed bodies must not carry cross-folder `../../` references to out-of-package documents. | A doc that lives in an upstream analysis folder is a perfectly valid file; a `../../` link resolves fine on disk. The defect is that a *transmitted* artifact is sourced from outside the package boundary — a package-composition fact, invisible to any single-file check. |
| **4** | **Stable-key liveness** (the *semantic* seam) | An *anchor/support* declaration must name a question that is still **live and transmitted**. When the question set is renumbered or a question is deferred/dropped, every doc that declares it anchors/supports that question must be updated in lockstep. | Both docs are internally clean: doc A says "supports QK-X"; the questions doc has since moved QK-X to the deferred set. Nothing in A is malformed — the reference simply points at a fact that changed elsewhere. This is the failure mode of **non-uniform updates**: a spine fact (a question's number or transmit status) drifts in its home doc while the referencing siblings keep the stale claim. |

## The predicate / substantial-equivalence tiering principle (the root of seam 1)

Predicate and substantial-equivalence (SE) content is authored at **three deliberately
different tiers**, and the three must never be conflated — most cross-reference mislabels are a
tier confusion:

| Tier | Where it lives | Depth |
|------|----------------|-------|
| **Identity-level treatment** | the **device description** — a paragraph naming the predicate and asserting the same intended-use family | one or two sentences; no comparison tables |
| **Abbreviated summary** | a **summary attachment** in the pre-submission — candidate rationale + a highlights comparison, enough to frame the questions | a few pages; explicitly *not* the full argument |
| **Full SE analysis** | **deferred to the marketing submission** (the 510(k)/De Novo) — landscape search, per-attribute comparison in FDA format, the complete SE argument | the full technical-file artifact |

The rules that fall out of this:

1. **Don't conflate the tiers.** The pre-submission carries the *abbreviated summary*; the *full*
   analysis is a later-submission deliverable. Saying the pre-submission attachment *is* the full
   analysis over-claims the package.
2. **A cross-reference must name the right tier.** When any document points at the summary
   attachment, it must call it a *summary/abbreviated* justification — not "the full/complete
   predicate analysis." The adjective is load-bearing: it tells the reviewer which tier they are
   about to open.
3. **Keep the pointer and the target in lockstep.** If the target's self-label changes tier
   (summary → full, or vice versa), every describing pointer to it changes with it — the two are
   one fact expressed in two places.

## How these failed once (illustrative)

> **Seam 1.** A cover letter's predicate section pointed at the summary attachment and called it
> "the **full** predicate justification, with comparison tables in FDA SE format." The attachment's
> own § 1 opened: "this is an **abbreviated** summary; the full SE analysis is a marketing-submission
> deliverable, not included in this pre-submission." Both sentences were clean; the pair over-claimed
> the package's depth. A device-description pointer to the same attachment carried the identical
> mislabel — one tier confusion, replicated across two filed bodies.
>
> **Seam 2.** Prose scattered through the cover letter referred to "attachment 3 / 4 / 5" for the
> predicate / PCCP / questions docs, while the numbered contents table listed them as 4 / 5 / 6. The
> prose had silently *not counted the cover letter itself as attachment 1*; the table had. Every
> number was internally consistent within its own list — off by exactly one across the seam.
>
> **Seam 3.** The predicate summary attachment was *transmitted* (it appeared in the numbered
> attachment table) but the file itself lived in an upstream `input-analysis/` folder and was
> reached from filed bodies via `../../input-analysis/…`. A transmitted artifact was being sourced
> from outside the package boundary — valid on disk, wrong for assembly.

## Authoring rules of thumb

1. **Describe a target in the target's own words.** Before writing "the full/complete/comprehensive
   X" about another document, open X and read its title + first section. If X calls itself a
   summary/overview/abbreviated treatment, your pointer says the same.
2. **Number prose against the one authoritative list.** Pick the numbered attachment table as the
   single source of numbering (decide once whether the cover/transmittal letter is attachment 1),
   and make every "attachment N" in prose agree with it — and with the assembly manifest's set.
3. **A transmitted document lives in the filing folder.** If an upstream analysis doc must be
   transmitted, bring a right-sized copy/extract into the package; do not attach it in place across a
   `../../` boundary. Reserve out-of-folder pointers for *grounding-only* or *provided-on-request*
   material, and mark them as such.

## Where each seam bites

- **Device description / cover letter** → seam 1 (a summary attachment called "full").
- **Any filed body with numbered pointers** → seam 2 (off-by-one against the contents table).
- **Composition manifest + attachment table** → seam 3 (a transmitted piece sourced from outside
  the filing folder; a filed-body `../../` reach into an upstream tree).

All three are the same underlying error — a claim made in one document about *another* document —
which is exactly why a lint that reads one document at a time cannot see them.
