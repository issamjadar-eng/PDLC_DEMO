#!/usr/bin/env python3
"""
lint_prose.py — deterministic prose linter grounded in Zinsser's *On Writing Well*.

This is the MECHANICAL pass of the `writing-well` skill: the clutter a machine
can find without judgment — clutter phrases, hedges, passive voice,
nominalizations, -ly adverbs, weak verb+noun, empty openers, over-long
sentences/paragraphs, and clichés. It runs with NO LLM, so it is cheap, fast,
reproducible, and CI-able.

It is ADVISORY by default: every finding is a prompt to look, not a verdict, and
the script exits 0 unless you pass --strict (opt-in CI gate). The judgment layer
(rhythm, voice, structure, the lead and the ending) is the `prose-editor` agent's
job — this script deliberately does not attempt it.

Prose-only: YAML frontmatter, fenced code blocks, inline code, link URLs, and
markdown table rows are skipped so the linter only ever sees actual prose.

Usage:
    python3 lint_prose.py FILE.md [FILE2.md ...]
        [--json] [--max-len N] [--max-para N] [--strict]
        [--only TAG[,TAG...]] [--no-color]

Tags: clutter hedge passive nominalization adverb weak-verb opener length cliche
Exit: 0 always, unless --strict and findings exist (then 1).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path

# --------------------------------------------------------------------------- #
# Rule data — curated, paraphrased into our own operating rules (no book text).
# --------------------------------------------------------------------------- #

# Clutter dictionary: wordy phrase -> tighter replacement. Matched case-insensitively
# on word boundaries. Keep these unambiguous — every entry should be safe to suggest.
CLUTTER = {
    "in order to": "to",
    "in order for": "for",
    "due to the fact that": "because",
    "owing to the fact that": "because",
    "in spite of the fact that": "although",
    "despite the fact that": "although",
    "in the event that": "if",
    "in the event of": "if",
    "for the purpose of": "for",
    "with the exception of": "except",
    "at this point in time": "now",
    "at the present time": "now",
    "at this moment in time": "now",
    "in this day and age": "today",
    "a large number of": "many",
    "a majority of": "most",
    "the majority of": "most",
    "a small number of": "a few",
    "a sufficient number of": "enough",
    "in the near future": "soon",
    "on a regular basis": "regularly",
    "in a timely manner": "promptly",
    "in close proximity to": "near",
    "in the vicinity of": "near",
    "has the ability to": "can",
    "have the ability to": "can",
    "is able to": "can",
    "are able to": "can",
    "take into consideration": "consider",
    "take into account": "consider",
    "is indicative of": "indicates",
    "in the absence of": "without",
    "with regard to": "about",
    "with respect to": "about",
    "in regard to": "about",
    "in terms of": "in",
    "in relation to": "about",
    "a number of": "several",
    "the fact that": "that",
    "in connection with": "about",
    "prior to": "before",
    "subsequent to": "after",
    "in the process of": "",
    "needless to say": "",
    "it should be noted that": "",
    "it is important to note that": "",
    "for all intents and purposes": "",
    "each and every": "every",
    "first and foremost": "first",
    "few and far between": "rare",
}

# Hedges / qualifiers Zinsser flags as leeches — they drain force from a sentence.
HEDGES = [
    "very", "rather", "quite", "somewhat", "sort of", "kind of", "a bit",
    "pretty much", "really", "actually", "basically", "essentially",
    "literally", "virtually", "arguably", "fairly", "relatively", "slightly",
    "more or less", "to some extent", "in a sense", "if you will",
    "i think", "i believe", "i feel", "it seems", "it appears",
    "perhaps", "maybe", "possibly", "presumably", "in my opinion",
]

# Clichés — tired phrases that signal autopilot. Shareable with public-doc's list.
CLICHES = [
    "at the end of the day", "low-hanging fruit", "think outside the box",
    "move the needle", "boil the ocean", "circle back", "touch base",
    "drill down", "deep dive", "best of breed", "best in class",
    "game changer", "game-changer", "paradigm shift", "synergy", "synergies",
    "bleeding edge", "cutting edge", "cutting-edge", "state of the art",
    "win-win", "going forward", "at scale", "north star", "secret sauce",
    "table stakes", "raise the bar", "push the envelope", "hit the ground running",
    "needle in a haystack", "tip of the iceberg", "the elephant in the room",
    "when all is said and done", "last but not least", "few and far between",
    "in today's fast-paced world", "a perfect storm", "the new normal",
    "double-edged sword", "bring to the table", "on the same page",
    "at the speed of light", "leverage", "leveraging", "unlock value",
]

# Nominalizations: a buried verb dressed up as a noun. phrase -> the verb it hides.
NOMINALIZATIONS = {
    "make a decision": "decide",
    "made a decision": "decided",
    "reach a conclusion": "conclude",
    "came to a conclusion": "concluded",
    "provide assistance": "help",
    "provide a recommendation": "recommend",
    "give consideration": "consider",
    "perform an analysis": "analyze",
    "conduct an investigation": "investigate",
    "conduct a review": "review",
    "make an assumption": "assume",
    "make an adjustment": "adjust",
    "make an improvement": "improve",
    "make a contribution": "contribute",
    "make a recommendation": "recommend",
    "make use of": "use",
    "make reference to": "mention",
    "carry out an evaluation": "evaluate",
    "give an explanation": "explain",
    "have a discussion": "discuss",
    "take action": "act",
    "take steps": "act",
    "is a reflection of": "reflects",
    "provide protection": "protect",
    "has a dependency on": "depends on",
    "have a dependency on": "depend on",
    "had a dependency on": "depended on",
}

# Empty openers — a sentence that backs into its subject. (regex, suggestion)
OPENERS = [
    (re.compile(r"\bthere\s+(is|are|was|were|has been|have been)\b", re.I),
     "Empty opener — name the actor; cut 'there is/are'."),
    (re.compile(r"\bit\s+(is|was)\b(?=[^.?!]*\bthat\b)", re.I),
     "Empty opener — 'it is … that …' usually hides a stronger subject."),
    (re.compile(r"\bit\s+(is|was)\s+(important|interesting|worth noting|clear|obvious|evident)\b", re.I),
     "Empty opener — say the thing directly instead of framing it."),
]

# Passive voice: a 'be' verb followed (within a couple of words) by a past
# participle. A heuristic — it will miss some and over-flag a few; that's fine,
# every flag is a prompt to look.
BE = r"(?:am|is|are|was|were|be|been|being|get|gets|got|gotten)"
# Past participle: -ed/-en/-wn endings cover the bulk; an explicit irregular set
# catches the common ones that don't. We deliberately keep this tight — better to
# miss a passive than to flag every word ending in 'nt' (important, present, …).
IRREGULAR_PP = (
    r"made|sent|kept|held|told|sold|paid|built|brought|caught|taught|"
    r"thought|found|bound|lost|left|met|set|put|cut|read|led|fed"
)
PASSIVE_RE = re.compile(
    rf"\b{BE}\b(?:\s+\w+ly)?\s+(\w+(?:ed|en|wn)|{IRREGULAR_PP})\b",
    re.I,
)
# Past participles that are really adjectives/false hits — skip these. After a
# be-verb most -ed/-en words are predicate ADJECTIVES, not passives ("was thrilled",
# "is golden", "is happily married"); denylisting the common ones is what keeps the
# passive tag's signal-to-noise high (it is the highest-volume tag — noise here trains
# the reader to ignore it). Genuine passives ("was written", "is being reviewed") are
# unaffected.
PASSIVE_FALSE = {
    # original adjectival participles
    "based", "interested", "concerned", "involved", "located", "related",
    "supposed", "used", "limited", "experienced", "advanced", "detailed",
    "complicated", "tired", "excited", "needed", "intended", "dedicated",
    "open", "even", "often", "seen", "been", "given", "taken", "known",
    "done", "gone", "shown",
    # emotive/stative participles used as predicate adjectives
    "thrilled", "scared", "bored", "worried", "pleased", "frustrated",
    "delighted", "satisfied", "surprised", "confused", "married", "exhausted",
    "annoyed", "embarrassed", "determined", "disappointed", "amazed", "ashamed",
    "devoted", "gifted", "talented", "renowned", "distinguished", "sophisticated",
    "accomplished", "convinced", "engaged", "exposed",
    # color/material/quality adjectives ending -en/-ed (not verbs)
    "golden", "wooden", "sudden", "molten", "ashen", "oaken", "leaden",
    "silken", "brazen", "green", "drunken", "mistaken", "rotten", "woollen",
    "woolen",
}

# -ly adverb, captured with the word before it (to spot adverb+strong-verb).
ADVERB_RE = re.compile(r"\b(\w+)\s+(\w+ly)\b", re.I)
# Common -ly words that are not manner adverbs, or are load-bearing — skip.
ADVERB_FALSE = {
    "only", "early", "family", "supply", "apply", "reply", "ally", "rally",
    "fully", "likely", "lonely", "lovely", "friendly", "daily", "weekly",
    "monthly", "yearly", "quarterly", "ugly", "silly", "holy", "italy",
    "assembly", "anomaly", "panoply", "july", "wholly", "solely", "duly",
    "namely", "notably", "specifically", "particularly",
    "lively", "unwieldy", "measly", "homely",
}

# Weak verb + abstract noun: "is/are/has + ...tion/ment/..." where a verb exists.
WEAK_VERB_RE = re.compile(
    r"\b(is|are|was|were|has|have|had|provides?|gives?|makes?)\s+"
    r"(?:a|an|the|some|its|their|our|your)?\s*"
    r"(\w+(?:tion|ment|ance|ence|ity|ness|sion))\b",
    re.I,
)

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")


def phrase_re(phrase: str) -> re.Pattern:
    """Compile a multi-word phrase so it tolerates line-wraps and runs of
    whitespace between words (markdown prose wraps mid-phrase constantly)."""
    parts = [re.escape(w) for w in phrase.split()]
    return re.compile(r"\b" + r"\s+".join(parts) + r"\b", re.I)


# Pre-compile the phrase dictionaries once (whitespace-tolerant).
CLUTTER_RE = {p: (phrase_re(p), r) for p, r in CLUTTER.items()}
NOMINALIZATION_RE = {p: (phrase_re(p), v) for p, v in NOMINALIZATIONS.items()}
HEDGE_RE = {h: phrase_re(h) for h in HEDGES}
CLICHE_RE = {c: phrase_re(c) for c in CLICHES}


@dataclass
class Finding:
    tag: str          # clutter|hedge|passive|nominalization|adverb|weak-verb|opener|length|cliche
    line: int
    col: int
    match: str
    message: str
    suggest: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------- #
# Prose extraction — blank out everything that isn't prose so rules never see it.
# --------------------------------------------------------------------------- #
def mask_non_prose(lines: list[str]) -> list[str]:
    """Return a copy of `lines` where non-prose spans are replaced by spaces.

    Line numbers and columns stay aligned with the original. We blank rather than
    delete so a finding's (line, col) maps back to the real file. Masked:
    YAML frontmatter, fenced code blocks, indented code, ATX heading markers,
    inline `code`, link URLs/targets, markdown table rows, and HTML comments.
    """
    out = list(lines)
    in_fence = False
    fence_marker = ""
    in_frontmatter = False

    for i, raw in enumerate(lines):
        stripped = raw.strip()

        # YAML frontmatter: a leading '---' on line 0 opens it.
        if i == 0 and stripped == "---":
            in_frontmatter = True
            out[i] = " " * len(raw)
            continue
        if in_frontmatter:
            out[i] = " " * len(raw)
            if stripped in ("---", "..."):
                in_frontmatter = False
            continue

        # Fenced code blocks (``` or ~~~).
        fence_open = re.match(r"^(\s*)(`{3,}|~{3,})", raw)
        if fence_open:
            marker = fence_open.group(2)[0] * 3
            if not in_fence:
                in_fence = True
                fence_marker = marker
                out[i] = " " * len(raw)
                continue
            elif marker == fence_marker:
                in_fence = False
                out[i] = " " * len(raw)
                continue
        if in_fence:
            out[i] = " " * len(raw)
            continue

        # Indented code block (4+ spaces) — but not a list continuation we care about.
        if re.match(r"^ {4,}\S", raw) and not re.match(r"^ {4,}[-*+] ", raw):
            out[i] = " " * len(raw)
            continue

        # HTML comment line (incl. INTERNAL blocks) — skip whole line if it's a comment.
        if stripped.startswith("<!--") or stripped.startswith("-->"):
            out[i] = " " * len(raw)
            continue

        line = out[i]

        # Markdown table row — pipe-delimited. Blank it (table cells aren't prose).
        if stripped.startswith("|") and stripped.count("|") >= 2:
            out[i] = " " * len(raw)
            continue

        # Blank the heading hashes/markers but keep the heading text (it's prose).
        line = re.sub(r"^(\s*)(#{1,6})(\s+)", lambda m: m.group(1) + " " * len(m.group(2)) + m.group(3), line)
        # Blockquote / list markers -> spaces (keep the text).
        line = re.sub(r"^(\s*)([-*+]|\d+\.|>)(\s+)", lambda m: m.group(1) + " " * len(m.group(2)) + m.group(3), line)

        # Inline code `...` -> spaces.
        line = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), line)
        # Images ![alt](url) and links [text](url): keep the visible text, blank the url.
        line = re.sub(r"!\[[^\]]*\]\([^)]*\)", lambda m: " " * len(m.group(0)), line)
        line = re.sub(r"\]\(([^)]*)\)", lambda m: "]" + "(" + " " * len(m.group(1)) + ")", line)
        # Bare URLs / autolinks.
        line = re.sub(r"<?https?://\S+>?", lambda m: " " * len(m.group(0)), line)
        # Strip emphasis markers but keep the words.
        line = re.sub(r"[*_]{1,3}", lambda m: " " * len(m.group(0)), line)

        out[i] = line

    return out


# --------------------------------------------------------------------------- #
# Sentence segmentation (over the masked prose, per paragraph).
# --------------------------------------------------------------------------- #
ABBREV = {"e.g", "i.e", "etc", "vs", "mr", "mrs", "ms", "dr", "st", "fig", "no",
          "al", "inc", "ltd", "co", "cf", "ca", "approx"}


def split_sentences(text: str) -> list[tuple[int, str]]:
    """Yield (start_offset, sentence) over `text`. Crude but adequate for length."""
    out = []
    n = len(text)
    start = 0
    i = 0
    while i < n:
        c = text[i]
        if c in ".!?":
            # Look back for abbreviation.
            j = i - 1
            while j >= 0 and text[j].isalpha():
                j -= 1
            word = text[j + 1:i].lower()
            is_abbrev = word in ABBREV or (i >= 1 and text[i - 1].isdigit())
            # Need whitespace+capital (or EOL) after to count as a boundary.
            k = i + 1
            while k < n and text[k] in ".!?)\"'”’]":
                k += 1
            after_ok = k >= n or (k < n and text[k] in " \n\t")
            if not is_abbrev and after_ok:
                seg = text[start:k].strip()
                if seg:
                    out.append((start, seg))
                start = k
                i = k
                continue
        i += 1
    tail = text[start:].strip()
    if tail:
        out.append((start, tail))
    return out


def offset_to_linecol(text: str, idx: int) -> tuple[int, int]:
    line = text.count("\n", 0, idx) + 1
    last_nl = text.rfind("\n", 0, idx)
    col = idx - last_nl
    return line, col


# --------------------------------------------------------------------------- #
# The rules.
# --------------------------------------------------------------------------- #
def run_rules(masked_text: str, max_len: int, max_para: int) -> list[Finding]:
    findings: list[Finding] = []

    def add(tag, idx, match, message, suggest=""):
        line, col = offset_to_linecol(masked_text, idx)
        match = re.sub(r"\s+", " ", match).strip()
        message = re.sub(r"'[^']*'", lambda m: "'" + re.sub(r"\s+", " ", m.group(0)[1:-1]).strip() + "'", message)
        findings.append(Finding(tag, line, col, match, message, suggest))

    # --- Clutter dictionary (longest match wins; suppress contained overlaps) -
    clutter_hits = []  # (start, end, phrase, repl)
    for phrase, (rx, repl) in CLUTTER_RE.items():
        for m in rx.finditer(masked_text):
            clutter_hits.append((m.start(), m.end(), phrase, repl))
    clutter_hits.sort(key=lambda h: (h[0], -(h[1] - h[0])))
    kept_clutter: list[tuple[int, int]] = []
    for start, end, phrase, repl in clutter_hits:
        if any(s <= start and end <= e for s, e in kept_clutter):
            continue  # fully contained in a longer clutter phrase already kept
        kept_clutter.append((start, end))
        actual = masked_text[start:end]
        sug = f"→ {repl!r}" if repl else "→ (cut)"
        add("clutter", start, actual,
            f"Clutter: '{actual}' " + (f"→ '{repl}'" if repl else "→ cut it"),
            sug)

    # --- Nominalizations (check before generic weak-verb) -------------------
    nominalization_spans: list[tuple[int, int]] = []
    for phrase, (rx, verb) in NOMINALIZATION_RE.items():
        for m in rx.finditer(masked_text):
            actual = masked_text[m.start():m.end()]
            nominalization_spans.append((m.start(), m.end()))
            add("nominalization", m.start(), actual,
                f"Buried verb: '{actual}' → '{verb}'", f"→ {verb!r}")

    # --- Hedges / qualifiers ------------------------------------------------
    for h, rx in HEDGE_RE.items():
        for m in rx.finditer(masked_text):
            actual = masked_text[m.start():m.end()]
            add("hedge", m.start(), actual,
                f"Hedge: '{actual}' weakens the sentence — cut or commit.",
                "→ (cut)")

    # --- Clichés ------------------------------------------------------------
    for c, rx in CLICHE_RE.items():
        for m in rx.finditer(masked_text):
            actual = masked_text[m.start():m.end()]
            add("cliche", m.start(), actual,
                f"Cliché: '{actual}' — say it fresh or cut it.", "→ (rephrase)")

    # --- Empty openers (dedupe overlapping hits at the same start) ----------
    seen_opener: set[int] = set()
    for rx, msg in OPENERS:
        for m in rx.finditer(masked_text):
            if m.start() in seen_opener:
                continue
            seen_opener.add(m.start())
            add("opener", m.start(), m.group(0), msg)

    # --- Passive voice ------------------------------------------------------
    for m in PASSIVE_RE.finditer(masked_text):
        participle = m.group(1).lower()
        if participle in PASSIVE_FALSE:
            continue
        add("passive", m.start(), m.group(0),
            f"Possible passive: '{m.group(0).strip()}' — prefer an active verb with a subject.")

    # --- Weak verb + abstract noun -----------------------------------------
    for m in WEAK_VERB_RE.finditer(masked_text):
        phrase = m.group(0)
        # Skip if this span overlaps a nominalization we already reported.
        if any(m.start() < ne and ns < m.end() for ns, ne in nominalization_spans):
            continue
        add("weak-verb", m.start(), phrase,
            f"Weak verb + abstract noun: '{phrase}' — a stronger verb is usually hiding in the noun.")

    # --- -ly adverbs --------------------------------------------------------
    for m in ADVERB_RE.finditer(masked_text):
        before, adv = m.group(1), m.group(2)
        if adv.lower() in ADVERB_FALSE:
            continue
        # Two-syllable-ish guard: require the stem before 'ly' to look like an adjective.
        stem = adv[:-2]
        if len(stem) < 3:
            continue
        add("adverb", m.start(1), f"{before} {adv}",
            f"Adverb: '{adv}' (after '{before}') — if the verb is already strong, the -ly is dead weight.")

    # --- Sentence length ----------------------------------------------------
    for off, sent in split_sentences(masked_text):
        words = WORD_RE.findall(sent)
        if len(words) > max_len:
            add("length", off, sent[:48] + ("…" if len(sent) > 48 else ""),
                f"Long sentence: {len(words)} words (>{max_len}) — consider splitting.")

    # --- Paragraph length ---------------------------------------------------
    para_start = 0
    for para in re.split(r"\n[ \t]*\n", masked_text):
        words = WORD_RE.findall(para)
        if len(words) > max_para:
            add("length", para_start, "(paragraph)",
                f"Long paragraph: {len(words)} words (>{max_para}) — consider a break.")
        para_start += len(para) + 2

    findings.sort(key=lambda f: (f.line, f.col))
    return findings


# --------------------------------------------------------------------------- #
# Output.
# --------------------------------------------------------------------------- #
COLORS = {
    "clutter": "\033[33m", "hedge": "\033[33m", "passive": "\033[35m",
    "nominalization": "\033[36m", "adverb": "\033[36m", "weak-verb": "\033[35m",
    "opener": "\033[34m", "length": "\033[31m", "cliche": "\033[33m",
}
RESET = "\033[0m"


def render_human(path: str, findings: list[Finding], use_color: bool) -> str:
    if not findings:
        return f"{path}: clean — no mechanical flags. (Rhythm/voice/structure still want the agent pass.)"
    lines = [f"{path}: {len(findings)} flag(s) — advisory; every flag is a prompt to look, not a verdict.\n"]
    for f in findings:
        tag = f.tag
        if use_color:
            tag = f"{COLORS.get(f.tag, '')}{f.tag}{RESET}"
        loc = f"{f.line}:{f.col}"
        lines.append(f"  {loc:>8}  [{tag}] {f.message}")
    # Summary by tag.
    counts: dict[str, int] = {}
    for f in findings:
        counts[f.tag] = counts.get(f.tag, 0) + 1
    summary = "  ".join(f"{k}:{v}" for k, v in sorted(counts.items()))
    lines.append(f"\n  totals  {summary}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Deterministic Zinsser-style prose linter (no LLM).")
    ap.add_argument("files", nargs="+", help="Markdown/text files to lint.")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of human text.")
    ap.add_argument("--max-len", type=int, default=30, help="Flag sentences longer than N words (default 30).")
    ap.add_argument("--max-para", type=int, default=160, help="Flag paragraphs longer than N words (default 160).")
    ap.add_argument("--strict", action="store_true", help="Exit non-zero if any finding exists (opt-in CI gate).")
    ap.add_argument("--only", default="", help="Comma-separated tags to keep (e.g. clutter,hedge).")
    ap.add_argument("--no-color", action="store_true", help="Disable ANSI color.")
    args = ap.parse_args(argv)

    only = {t.strip() for t in args.only.split(",") if t.strip()}
    use_color = (not args.no_color) and sys.stdout.isatty()

    all_results = []
    total = 0
    for fp in args.files:
        p = Path(fp)
        if not p.exists():
            print(f"{fp}: not found", file=sys.stderr)
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        masked = "\n".join(mask_non_prose(text.splitlines()))
        findings = run_rules(masked, args.max_len, args.max_para)
        if only:
            findings = [f for f in findings if f.tag in only]
        total += len(findings)
        all_results.append((fp, findings))

    if args.json:
        payload = {
            "results": [
                {"file": fp, "count": len(fs), "findings": [f.to_dict() for f in fs]}
                for fp, fs in all_results
            ],
            "total": total,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        for fp, fs in all_results:
            print(render_human(fp, fs, use_color))
            print()

    if args.strict and total > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
