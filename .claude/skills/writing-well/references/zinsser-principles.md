# Zinsser Principles — Operating Rules for Nonfiction Prose

These are the standards the `writing-well` skill edits toward, distilled from William
Zinsser's *On Writing Well* into our own operating rules. **No verbatim text from the
book is reproduced here** — the ideas (simplicity, clutter, the audience, active verbs)
are not copyrightable; only their expression is, so we re-express. Read this before any
`review`, `copyedit`, or `draft` pass; it is the ground truth every judgment call appeals to.

The whole discipline reduces to one sentence: **strip every sentence to its cleanest
components, then trust the reader.** Everything below serves that.

---

## The four pillars

1. **Simplicity.** The reader's attention is the scarcest resource. Most first drafts can
   lose a third of their words with no loss of meaning — and gain force by it. Clutter is
   not style; it is the enemy of style. If a word does no work, cut it.
2. **Clarity.** If the reader is lost, it is almost always the writer's fault, not the
   reader's. Muddy writing reflects muddy thinking — clear up the thought and the sentence
   clears with it. There is no "writing well but unclearly."
3. **Brevity.** The shorter version, if it says the same thing, is the better version.
   Brevity is not terseness — it is the absence of waste.
4. **Humanity.** Nonfiction is one person talking to another. Warmth, a real voice, and
   the willingness to say "I" (where appropriate) are what make a reader stay. A correct
   but lifeless paragraph has failed.

---

## The mechanical layer — what the linter catches (and *why*)

The linter (`scripts/lint_prose.py`) finds these without judgment. The point is not the
flag; it is the move the flag teaches. Each rule below names the move.

- **Clutter phrases.** "In order to" is "to." "Due to the fact that" is "because." "At
  this point in time" is "now." These are not wrong — they are *padding*, and padding
  dilutes. The move: swap the phrase for the shorter word, or cut it.
- **Hedges and qualifiers.** "Very," "rather," "quite," "sort of," "I think," "it seems."
  Zinsser calls these leeches — they suck the conviction out of a sentence. "Very unique"
  is weaker than "unique." The move: cut the qualifier and let the strong word stand, or,
  if you genuinely don't believe the claim, fix the claim.
- **Passive voice.** "A decision was reached" hides who decided. The passive is not banned
  — sometimes the actor is unknown or irrelevant — but the default should be active:
  somebody does something. The move: name the actor and let them act.
- **Nominalizations (buried verbs).** "Make a decision" is "decide." "Provide assistance"
  is "help." "Conduct an investigation" is "investigate." A verb has been embalmed into a
  noun and propped up with a weak helper verb. The move: dig the verb back out.
- **-ly adverbs.** "Shouted loudly," "ran quickly." If the verb is strong, the adverb is
  redundant; if the verb is weak, replace the verb instead of bracing it with an adverb.
  The move: find the one verb that carries the manner by itself.
- **Weak verb + abstract noun.** "Is a reflection of" → "reflects." "Has a dependency on"
  → "depends on." The move: collapse the helper-verb-plus-noun into the single verb hiding
  inside it.
- **Empty openers.** "There is," "there are," "it is X that." These back into the sentence
  instead of starting it. The move: delete the scaffolding and lead with the real subject.
- **Over-long sentences and paragraphs.** Length is not a sin, but a 45-word sentence
  usually carries two or three ideas that each deserve their own. The move: find the joint
  and break it.
- **Clichés.** "At the end of the day," "low-hanging fruit," "move the needle." A cliché is
  a phrase the reader skims because they've seen it a thousand times — it buys no attention.
  The move: say the thing in your own words, or cut it.

**These are heuristics, not verdicts.** Every flag is a prompt to look. A flagged passive
may be the right call; a long sentence may be deliberately cumulative. The linter never
decides — it points.

---

## The judgment layer — what only a reader can hear

The `prose-editor` agent owns these. A script cannot judge them; they require an ear and a
sense of the whole.

- **Rhythm — read it aloud.** The final test of a sentence is the spoken one. If you
  stumble reading it, the reader stumbles too. Vary sentence length: a short sentence after
  two long ones lands like a punch. Monotony is a flaw even when every sentence is correct.
- **Voice and warmth.** Does this sound like a person, or like a committee? The same fact
  can be stated coldly or with life. Prefer the version a reader would want to keep reading.
  Do not strip personality in the name of "professionalism" — voice is what makes nonfiction
  worth reading over a fact sheet.
- **The lead.** The first sentence must make the reader want the second; the second must
  make them want the third. A lead that explains, hedges, or clears its throat has already
  lost. Earn the next sentence, every time.
- **The ending.** Stop when you're done. The best endings land a beat sooner than the
  reader expects and often circle back to an image or phrase from the lead. Do not trail
  off into summary; do not append "in conclusion."
- **One idea per paragraph.** A paragraph is a unit of thought. When it changes subject,
  start a new one. Long paragraphs that braid two ideas leave the reader unsure which one
  to hold.
- **Trust the reader.** Do not over-explain, do not repeat the point three ways, do not
  signpost every turn ("As we will see…", "It is worth noting…"). Respect the reader's
  intelligence: say it once, clearly, and move on.
- **Unity.** Decide on a tense, a person, and a level of formality, and hold them. Drift in
  any of these is felt even when the reader can't name it.
- **Unearned terminology — coined terms must be re-grounded where they are used.** A document
  that defines its own vocabulary (a "binding," a "seam," a "pin," an "estate") makes a quiet
  bet: that the reader internalized the definition and carries it forward. Real readers don't —
  they skim, they hold the gist, and by the halfway mark a sentence whose weight rests on three
  coined terms reads as noise. The failure compounds with depth: early sections feel clear,
  late sections feel impenetrable, and the author can't see it because the author holds all the
  definitions. The fix is cheap: at each load-bearing use far from the definition, re-anchor
  the term in six or eight plain words ("the bindings — which product fills which role —") or
  replace it with the plain phrase outright. Two hard sub-rules: internal editorial vocabulary
  (how the authors talk about the document — "the per-section closers," "the parent piece's
  spine") never belongs on the page; and a term's *definition section* is not a license — the
  test is whether a reader who only skimmed that section still lands the sentence. This is a
  judgment-layer check: build the coined-term inventory first, then walk the later uses.
- **The cold reader — expertise the page never granted.** Expert prose fails quietly by
  assuming context the reader was never given. The author cannot see it, because the author
  has the context; a cold reader stalls in the first two pages and never says why. Four
  shapes, all cheap to fix at first use:
  - *Acronyms after their names.* Spell the term out once, then use the acronym freely
    ("the Product Development Life Cycle (PDLC)…" — thereafter PDLC). An abstract or lead
    that opens on a bare acronym stalls every reader outside the authors' hallway.
  - *Coined terms defined at birth.* The companion to unearned terminology above: when a
    document introduces its own vocabulary ("seams," "invariants," "pins"), the first use
    carries a six-to-eight-word plain anchor ("the seams — where work crosses from one half
    to the other"). Definition-by-context feels sufficient to the author and is not; say
    what kind of thing the word names, once, where the word is born. Beware borrowed words
    especially: a coinage assembled from terms that already mean something ("browser
    console" reads as the devtools console) resolves to the meaning the reader already
    knows, not yours — describe the thing plainly at first mention and let the coined name
    arrive with its definition.
  - *Unframed proper nouns — lead with the role, attach the name.* A sentence built on
    product names ("agents reach ToolA and ToolB over XYZ") reads as tool soup to anyone
    unfamiliar with even one of them. Reorder role-first: "the team's ticketing and
    working-document systems — ToolA and ToolB — through governed tools." The informed
    reader still gets the names and the credibility signal; the cold reader gets through on
    roles alone. The test: delete every proper noun — does the sentence still say what
    happens?
  - *Compression that needs decoding.* Parallel constructions can compress past the point
    of parse: "bound to a concrete product where one fits, and to a named build where none
    does" forces the reader to expand "named build" and resolve two "where" clauses before
    the meaning lands — and reads as pretension besides. Unpack it: "an off-the-shelf
    product where one exists, and where none does, a component you build yourself." Ten
    words longer, zero decoding.
  These are considerations, not bans — a document for a single expert audience may earn
  denser defaults, and a name-dense inventory can itself be the point of a passage. The
  test is constant: hand the page to a reader who knows none of the tools and none of the
  coinages; every place they stall is a finding.
- **Flourish and pretension — clever is not clear.** A distinct failure mode where every
  sentence performs: epigrams stacked one per line ("X is Y, not Z" three times in a
  paragraph), colon-label scaffolds ("The practice: … The residue: …") that outline instead
  of write, asides nested inside em-dashes inside clauses, and sentences that admire
  themselves ("— that is its qualification"). Each device works once; in density the prose
  reads as posture and the reader has to translate it back into plain statements. The fix
  is Zinsser's oldest: one idea per sentence, finish the thought, and let the point carry
  the weight instead of the phrasing. Keep the single best epigram on a page; rewrite the
  rest as ordinary sentences. (The slop linter's `aitell-flourish` tag catches the
  mechanical forms; the judgment pass decides which single flourish, if any, earns its place.)

---

## Process truths (for `draft` and `copyedit`)

- **Rewriting is the work.** Almost nobody writes well in one pass. The first draft is for
  getting it down; the craft is in the cutting that follows. A `copyedit` pass *is* the
  rewriting — that's why it shows its work.
- **Show, don't tell.** Prefer the concrete detail to the abstract claim. "The build took
  forty minutes" beats "the build was slow." Detail is what the reader remembers.
- **Strong nouns and verbs over adjectives and adverbs.** A sentence carried by its nouns
  and verbs is sturdy; one propped up by modifiers is brittle. Spend your effort choosing
  the right verb, not decorating a weak one.
- **Teach the move, don't just fix the line.** When `copyedit` proposes a change, it names
  the principle ("cut clutter," "buried verb," "passive → active") so the writer learns to
  make the cut themselves next time. The goal is a writer who needs the skill less over
  time, not more.

---

## What this skill is *not*

- Not a grammar checker — it assumes the grammar is already right and works on the next
  layer: force, clarity, economy.
- Not a style cop for a house brand — that's `public-doc`'s job (brand, banned words,
  disclaimers, internal-leak). This skill is about prose quality in any voice.
- Not a gate — it is advisory. The author always decides. Marketing copy may *want* a
  punchy fragment; an engineering spec may *want* a precise passive. The principles are
  defaults to reason from, not rules to apply blindly.
