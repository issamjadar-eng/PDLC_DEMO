# Rule: Internal-Review-Doc Scope Labels (📤 / 📝 / ⏸️ / 📖)

Some regulated-project documents serve a **dual audience**: they're authored and reviewed by the internal cross-functional team, and they also distill into a **formal external submission** (regulatory filing, IRB package, notified-body dossier, audit-response package). When a single markdown file mixes (a) proposed language going to the external recipient with (b) internal rationale, decision history, deferred questions, and reference material, readers — and the eventual packager — need a clear visual signal of which content is which.

This rule defines a four-icon label system that:

1. **Avoids status-traffic-light semantics** — the icons deliberately do NOT use green/yellow/red colored bubbles (🟢/🟡/🔴) because those carry universal "good / warning / error" connotations and would conflict with the content-routing dimension this system encodes.
2. **Is markdown-portable and Confluence-compatible** — every icon is a standard Unicode emoji that renders in GitHub-rendered markdown, MkDocs, pandoc HTML, and Confluence pages (including when imported via `markdown-to-confluence` pipelines).
3. **Is icon-only by default** — text tags like `[Q-SUB CONTENT]` are not used inline with the icon; the icon alone carries the meaning. The scope banner at the top of the document explains what each icon means.

## The four icons

| Icon | Meaning | Where to apply |
|---|---|---|
| **📤** | **External-bound** — proposed language that lands in the formal external submission. The entire body under a 📤 heading goes to the external recipient (Context + Question + Refinement-seeking follow-up + Preliminary position + any embedded inline summaries / commitments / bright-lines), **except** inline 📝 anchors which are stripped during packaging. | Each primary question heading in a Q-Sub questions doc; the "Primary Set" caption; each section heading of any sub-document that lands in the external package (cover letter sections, device-description sections, etc.). |
| **📝** | **Internal context inline within otherwise-external content** — rationale, decision history, audit-trail notes, internal references to decision identifiers / finding identifiers / task identifiers. Useful for internal reviewers; **stripped during package assembly**. Cross-section references inside the same package (e.g., "per Q4.4 commitment") and forward-commitment placeholders (e.g., `[V&V-anchored, locked at design transfer]`) **stay** because the external reader sees the same package. `[VERIFY …]` tags must be **resolved** before transmission, not just stripped. | "Rationale superseded (per finding F-N resolution)" blockquotes; "Cross-reference: D-REG-X.Y" anchors; "task ben/NNN" references; "per F-N" cross-references; "per ben/187 forthcoming brief" notes. |
| **⏸️** | **Deferred** — content (typically deferred questions) deliberately not surfaced at the current external interaction. Preserved in the document for audit and possible inclusion in a follow-up submission. | Deferred question headings; parking-lot sections; any section explicitly held back from the current submission. |
| **📖** | **Reference material** — Terms and Definitions, regulatory-context notes, document traceability, changelog, glossaries. Available to internal readers; not submitted to the external recipient. | "Terms and Definitions" section; "Document Traceability" table; "Changelog" section; appendix-style reference tables. |

## Scope banner at the top of the document

Every internal-review doc that uses this label system MUST include a scope banner at the top, immediately after the title metadata and before the first content section. The banner serves two purposes: (1) tells the reader the document is for internal review (not the external submission itself); (2) defines the four-icon label system in a single table so the reader can decode every heading they encounter below.

The scope banner template — substitute `<external-recipient>` with the actual recipient (e.g., "FDA", "Notified Body", "IRB", "ISO 13485 auditor") and `<package>` with the name of the formal external package (e.g., "Q-Sub package", "MDR Technical Documentation", "IRB submission"):

```markdown
## 📋 Document Scope and Reading Guide (INTERNAL REVIEW DOC)

**This is an internal review document for the <package> — not the <external-recipient> submission itself.**

_Icon-only labels are used (no text tag) to keep visual noise low. The icon set was deliberately chosen to **avoid green/yellow/red status semantics** (good/warning/error), which would conflict with the document's content-routing dimension._

| Icon | Meaning | Examples in this document |
|---|---|---|
| **📤** | **<external-recipient>-bound** — proposed language that lands in the formal <package>. The entire body under a 📤 heading goes to <external-recipient>, except inline 📝 anchors stripped during packaging. | _List specific section IDs / question IDs / table IDs in this document._ |
| **📝** | **Internal context inline within 📤 content** — rationale, internal anchors, decision-identifier references. Stripped during package assembly. `[VERIFY …]` tags must be **resolved** before transmission. | _List specific anchor patterns used in this document (e.g., D-REG-X.Y / F-N / ben/NNN)._ |
| **⏸️** | **Deferred** — content not surfaced at the current interaction. Preserved for audit + possible follow-up. | _List the deferred section IDs._ |
| **📖** | **Reference material** — Terms, traceability, changelog, glossaries. Not submitted to <external-recipient>. | _List the reference-section names._ |

### What Lands in the Actual <package> 📤

_Bulleted list of every artifact that ships in the formal external package._
```

## When to apply this rule

Apply the scope-label system to a markdown document under `docs/project/submissions/`, `docs/project/dhfs/<dhf>/**/formal/`, or any other internal-review-doc location, when **all three** conditions hold:

1. The document serves an internal review audience.
2. Some content within the document distills into a formal external submission.
3. Other content within the document is internal-only (rationale, deferred items, reference material).

Documents that are **wholly internal** (e.g., task docs, gap analyses) or **wholly external** (e.g., the cover letter sent verbatim) do not need this system — the entire document is one category. Only mixed-audience documents benefit.

## When NOT to apply this rule

- **Task docs under `tasks/<person>/`** — wholly internal; no external destination.
- **Gap-analysis docs under `docs/_analysis/`** — wholly internal; findings are internal artifacts.
- **Pure regulatory artifacts already in formal/** — the regulated document IS the external submission; no internal-vs-external split.
- **READMEs** — folder documentation, not submission content.

## How to apply this rule (drop-in steps)

1. **Add the scope banner** at the top of the document (after title metadata, before the first content section).
2. **Tag each top-level / heading section** with the appropriate icon at the END of the heading line. Examples:
   ```
   ### Q4.1 — Single PCCP spanning two independent SaMD components 📤
   ### Q3.1 — Enhanced documentation across all components ⏸️ *via ben/179 — rationale…*
   ## Terms and Definitions 📖
   ## Changelog 📖
   ## Parking Lot — Questions Deferred to Future Meetings ⏸️
   ```
3. **Tag inline internal anchors with 📝 only when they need visual signalling**. For high-density anchor patterns (D-REG-X.Y / F-N / ben/NNN appearing inline within preliminary positions), an icon-per-anchor is too noisy — the scope banner already establishes that those anchors are internal. Reserve inline 📝 for sentinel blockquotes (`> **📝 Rationale superseded …**`) or major standalone notes that benefit from visual flagging.
4. **Cross-section references inside the package** (e.g., "consistent with Q4.4 commitment") are **not** internal anchors — they're external-reader-readable cross-references. Do not tag them 📝.
5. **`[VERIFY …]` tags** are explicit reminders that something must be resolved before transmission. Leave them visible (don't tag with 📝); they're called out separately in the scope banner.

## Why the colored bubbles (🟢🟡🟣🔵) are NOT used

An earlier draft of this convention used 🟢 / 🟡 / 🟣 / 🔵 for external-bound / deferred / reference / internal. That was rejected because:

- 🟢/🟡/🔴 carry near-universal "pass / warning / fail" semantics from status indicators, traffic lights, and CI/CD dashboards. Using them for content-routing creates immediate cognitive conflict: a reader sees 🟢 next to a heading and asks "is this question in a good state?" rather than "is this question going to FDA?"
- 🟣/🔵 are less status-loaded but still inherit the "colored bubble" pattern that the eye reads as a status badge.
- The 📤 / 📝 / ⏸️ / 📖 set encodes content-routing through **content metaphors** (outbox, memo, pause, book) rather than colors, eliminating the status-semantics overlap.

If your project genuinely needs a status-tracking dimension in addition to content-routing (e.g., "this question is approved 🟢 / under review 🟡 / blocked 🔴"), apply the colored bubbles to a status column or status badge separately — never on the same line as the content-routing icon.

## Confluence push compatibility

All four icons are standard Unicode emojis with established Confluence rendering:

- **📤** Outbox tray — U+1F4E4
- **📝** Memo — U+1F4DD
- **⏸️** Pause button — U+23F8 + U+FE0F
- **📖** Open book — U+1F4D6

These render natively in Confluence Cloud pages, comments, panels, and table cells. No Confluence-specific macros are required. When the document is pushed to Confluence via `markdown-to-confluence` (or any pandoc-based pipeline), the icons preserve verbatim.

For Confluence Status macros (the colored badge that Confluence displays inline, e.g., `{status:colour=Green|title=DONE}`), that's a separate UI concept for tracking workflow status of a Confluence page. Do not confuse it with this rule's content-routing icons.

## How this rule interacts with other rules

- **`readme-before-write.md`** — orthogonal. Reading the folder README before writing to a folder is unchanged. This rule defines what icons go INTO the file once you write it.
- **`sentinel-blocks.md`** — orthogonal. Sentinel-block-rendered content (subfolder tables, DHF tables, etc.) is structural metadata; it sits outside the 📤/📝/⏸️/📖 content-routing dimension.
- **`claude-md-references.md`** — independent. Persistent docs referencing durable artifacts is a separate rule about WHAT to reference; this rule is about HOW to tag scope of what's referenced.
- **`audit-wiring-before-adding-fields.md`** — independent. Auditing wiring before adding metadata fields is a separate concern from labelling existing content for scope.
