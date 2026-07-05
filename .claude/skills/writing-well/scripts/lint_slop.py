#!/usr/bin/env python3
"""
lint_slop.py — deterministic detector for AI-generated-text "tells" (slop).

Sibling to lint_prose.py. Where lint_prose finds *quality* problems (Zinsser),
this finds *fingerprints* of un-edited LLM output: the punctuation, vocabulary,
and phrasing that statistically distinguish machine drafts from human prose.

GROUNDING (these are the source-backed, deterministically-detectable tells):
  - Excess academic vocabulary — Kobak et al., Science Advances 2025
    (arXiv:2406.07016); Liang et al., ICML 2024 (arXiv:2403.07183). "delves" ~25x,
    "meticulous" ~35x, "underscores" ~14x more frequent post-ChatGPT.
  - Em-dash density — human mean ~3.23/1k words (range 0.33-17.12); LLMs skew high
    (Freeburg, arXiv:2603.27006, preprint). Flag > ~7/1k.
  - Bold-lead-in colon lists, puffery templates, negative-parallelism ("not just X,
    it's Y") — Wikipedia "Signs of AI writing" (WP:AISLOP).

HARD CAVEATS (baked into the design):
  * These are PROBABILISTIC and COMBINATORIAL. Flag density/clustering, never a
    single occurrence. Advisory only — exit 0 unless --strict.
  * Every word/phrase here occurs in legitimate human writing. A detector study
    found 61.3% of non-native-English essays mislabeled AI (Liang et al., Patterns
    2023). Treat findings as prompts to look, weighted low; never as proof.
  * Heavy editing defeats every tell. This catches un-edited drafts, not "AI use".

No external deps. Run:  python3 lint_slop.py <file> [--json] [--folklore] [--strict]
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Vocabulary tiers. Stored as lemmas; matched with light inflection.
# Tier 1 = academically validated excess words (high weight).
ACADEMIC_EXCESS = {
    "delve", "underscore", "showcase", "intricate", "intricacy", "meticulous",
    "commendable", "pivotal", "realm", "boast", "bolster", "garner", "testament",
    "tapestry", "interplay", "nestle",
}
# Words that, even once, are strong markers (top frequency-ratio in the studies).
ULTRA_MARKERS = {"delve", "underscore", "tapestry", "meticulous", "commendable", "interplay"}
# Tier 2 = curated-consensus (Wikipedia). Medium weight.
CURATED = {
    "vibrant", "enduring", "groundbreaking", "renowned", "multifaceted",
    "nuanced", "profound", "myriad", "encompass", "exemplify",
}
# Tier 3 = FOLKLORE (vendor/editor blogs; NOT in the academic/Wikipedia lists).
# Opt-in via --folklore; clearly labeled unsubstantiated; lowest weight.
FOLKLORE_WORDS = {
    "leverage", "seamless", "navigate", "elevate", "unlock", "harness",
    "foster", "robust", "streamline", "empower", "delicate",
}
# Light inflection for lemma matching.
_SUFFIXES = ("", "s", "es", "d", "ed", "ing", "ment", "ments", "ies", "y")


def _word_variants(lemma: str) -> set[str]:
    base = {lemma}
    if lemma.endswith("e"):
        stem = lemma[:-1]
        base |= {lemma + "s", lemma + "d", stem + "ing", lemma + "ment"}
    elif lemma.endswith("y"):
        stem = lemma[:-1]
        base |= {stem + "ies", lemma + "s", stem + "ied", lemma + "ing"}
    else:
        base |= {lemma + "s", lemma + "es", lemma + "ed", lemma + "ing", lemma + "ment"}
    return base


def _build_vocab_regex(words: set[str]) -> re.Pattern:
    variants = set()
    for w in words:
        variants |= _word_variants(w)
    alt = "|".join(sorted(map(re.escape, variants), key=len, reverse=True))
    return re.compile(rf"\b({alt})\b", re.I)


VOCAB_RE = {
    "academic": (_build_vocab_regex(ACADEMIC_EXCESS), "academic excess-vocabulary"),
    "curated": (_build_vocab_regex(CURATED), "curated AI-vocabulary"),
}
FOLKLORE_RE = _build_vocab_regex(FOLKLORE_WORDS)
ULTRA_RE = _build_vocab_regex(ULTRA_MARKERS)

# --------------------------------------------------------------------------- #
# Phrase / construction tells (regex). Mostly low-FP individually.
CONSTRUCTIONS = [
    # Negative parallelism / antithesis — require the echo form for precision.
    (re.compile(r"\b(it'?s|it is)\s+not\s+(just|only|merely|about)\b[^.;:!?]{1,45}[,;—-]\s*(it'?s|its|but)\b", re.I),
     "antithesis ('it's not just X — it's Y') — a signature AI construction"),
    (re.compile(r"\bnot just\b[^.;:!?]{1,45}\bbut\b", re.I),
     "'not just X but Y' — negative-parallelism tell (also legit; weigh by density)"),
    (re.compile(r"\bnot only\b[^.;:!?]{1,60}\bbut also\b", re.I),
     "'not only X but also Y' — common AI cadence (high false-positive; low weight)"),
    # Puffery / testament templates.
    (re.compile(r"\b(stands|serves) as a testament to\b", re.I), "puffery: 'serves as a testament to'"),
    (re.compile(r"\bis a testament to\b", re.I), "puffery: 'is a testament to'"),
    (re.compile(r"\bplays? an?\s+(vital|crucial|pivotal|key|significant)\s+role\b", re.I),
     "puffery: 'plays a crucial role'"),
    (re.compile(r"\bunderscor(es|ing)\s+(its|the)\s+(importance|significance)\b", re.I),
     "puffery: 'underscores its importance'"),
    (re.compile(r"\bleaves? an?\s+(lasting impact|indelible mark)\b", re.I), "puffery: 'leaves a lasting impact'"),
    (re.compile(r"\brich\s+(cultural\s+)?(tapestry|heritage)\b", re.I), "puffery: 'rich tapestry'"),
    (re.compile(r"\bwatershed moment\b", re.I), "puffery: 'watershed moment'"),
    # Trailing present-participle 'summary' clause.
    (re.compile(r",\s+(highlighting|underscoring|emphasizing|reflecting|ensuring|showcasing|symbolizing|cementing|solidifying)\b", re.I),
     "trailing participle summary clause (', highlighting its …')"),
    # Editorializing.
    (re.compile(r"\bit'?s?\s+(important|worth)\s+(to note|noting|noting that)\b", re.I),
     "editorializing: 'it's worth noting'"),
    (re.compile(r"\bno discussion would be complete without\b", re.I), "filler: 'no discussion would be complete without'"),
]
# Distinctive stock openers/fillers (low FP, higher weight).
OPENERS = [
    re.compile(r"in today'?s (fast-paced|digital|modern|rapidly[- ]changing) world", re.I),
    re.compile(r"in the (ever-evolving|ever-changing|fast-paced) (landscape|world|realm) of", re.I),
    re.compile(r"navigating the complexities of", re.I),
    re.compile(r"\blet'?s dive in\b", re.I),
    re.compile(r"\bin the realm of\b", re.I),
    re.compile(r"\bwhen it comes to\b", re.I),
]
# Folklore phrases — opt-in, low confidence.
FOLKLORE_PHRASES = [
    re.compile(r"\bhere'?s the thing\b", re.I),
    re.compile(r"\bthe truth is\b", re.I),
    re.compile(r"\bneedless to say\b", re.I),
    re.compile(r"\b(that said|with that being said)\b", re.I),
]
# Signposts at paragraph/sentence start — flag only when CLUSTERED.
SIGNPOST_RE = re.compile(
    r"(?m)(?:^|(?<=[.!?]\s))\s*(Moreover|Furthermore|Additionally|Notably|Importantly|Consequently|"
    r"In conclusion|In summary|Overall)\b")
BOLD_COLON_RE = re.compile(r"(?m)^[\s>*\-•]*\*\*[^*\n]{1,40}\*\*\s*:")
SMART_QUOTE_RE = re.compile("[‘’“”]")
EMOJI_HEAD_RE = re.compile(r"(?m)^[\s>*\-#]*[\U0001F000-\U0001FAFF←-➿]")

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
SENT_SPLIT = re.compile(r"[.!?]+(?:\s+|$)")


# --------------------------------------------------------------------------- #
# Skip-zone masking — blank non-prose in place (preserve offsets), like
# lint_prose. Also drop a trailing References/Bibliography/Sources section
# (link-heavy back-matter, not prose to slop-check).
def mask(text: str) -> str:
    out = list(text)

    def blank(start: int, end: int) -> None:
        for i in range(start, min(end, len(out))):
            if out[i] != "\n":
                out[i] = " "

    # YAML frontmatter
    m = re.match(r"\A---\n.*?\n---\n", text, re.DOTALL)
    if m:
        blank(0, m.end())
    # fenced code
    for m in re.finditer(r"(?ms)^```.*?^```", text):
        blank(m.start(), m.end())
    # HTML comments (incl. INTERNAL:BEGIN…END single-comment form)
    for m in re.finditer(r"(?s)<!--.*?-->", text):
        blank(m.start(), m.end())
    # inline code
    for m in re.finditer(r"`[^`\n]+`", text):
        blank(m.start(), m.end())
    # link URLs (keep visible text): [text](url) -> blank the (url)
    for m in re.finditer(r"\]\(([^)]+)\)", text):
        blank(m.start(), m.end())
    # bare autolinks / raw URLs
    for m in re.finditer(r"https?://\S+", text):
        blank(m.start(), m.end())
    # markdown table rows
    for m in re.finditer(r"(?m)^\s*\|.*\|\s*$", text):
        blank(m.start(), m.end())
    # trailing References / Bibliography / Sources section → end
    m = re.search(r"(?im)^#{1,6}\s*(references|bibliography|sources|works cited)\b", text)
    if m:
        blank(m.start(), len(text))
    return "".join(out)


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


# --------------------------------------------------------------------------- #
def lint(raw: str, folklore: bool = False) -> dict:
    masked = mask(raw)
    words = WORD_RE.findall(masked)
    nwords = max(1, len(words))
    findings: list[dict] = []

    def add(tag, pos, match, message, sev):
        findings.append({"tag": tag, "line": line_of(raw, pos),
                         "match": match[:60], "message": message, "severity": sev})

    # 1) em-dash density
    em = [m.start() for m in re.finditer("—", masked)]
    rate = len(em) * 1000.0 / nwords
    if rate > 7:
        findings.append({"tag": "aitell-emdash", "line": line_of(raw, em[0]) if em else 1,
                         "match": f"{len(em)} em-dashes", "severity": "high",
                         "message": f"Em-dash density {rate:.1f}/1k words ({len(em)} total) — "
                         f"well above the human norm (~3.2/1k, flag >7). The strongest AI tell; "
                         f"convert most to periods/colons/commas."})
    elif rate >= 4:
        findings.append({"tag": "aitell-emdash", "line": line_of(raw, em[0]) if em else 1,
                         "match": f"{len(em)} em-dashes", "severity": "low",
                         "message": f"Em-dash density {rate:.1f}/1k words — slightly elevated "
                         f"(human norm ~3.2/1k). Worth thinning."})

    # 2) vocabulary (density-gated; ultra-markers always)
    vocab_hits = []
    for key, (rx, label) in VOCAB_RE.items():
        for m in rx.finditer(masked):
            vocab_hits.append((m.start(), m.group(0), key, label))
    ultra = [h for h in vocab_hits if ULTRA_RE.fullmatch(h[1].lower()) or
             ULTRA_RE.match(h[1].lower())]
    distinct = {h[1].lower() for h in vocab_hits}
    vocab_density = len(vocab_hits) * 500.0 / nwords
    # Emit ultra-markers always; emit the rest only if clustered (>=3 distinct, or density gate).
    gate_open = len(distinct) >= 3 or vocab_density >= 3.0
    for pos, tok, key, label in vocab_hits:
        is_ultra = bool(ULTRA_RE.match(tok.lower()))
        if is_ultra:
            add("aitell-vocab", pos, tok, f"'{tok}' — {label} (high-ratio AI marker; "
                f"Kobak/Liang). Reword unless load-bearing.", "med")
        elif gate_open:
            add("aitell-vocab", pos, tok, f"'{tok}' — {label}; flagged because AI-vocabulary "
                f"is clustered here ({len(distinct)} distinct). Singly these are fine.", "low")

    # 3) constructions
    for rx, msg in CONSTRUCTIONS:
        for m in rx.finditer(masked):
            sev = "low" if "high false-positive" in msg or "also legit" in msg else "med"
            add("aitell-construction", m.start(), m.group(0), msg, sev)

    # 4) distinctive openers
    for rx in OPENERS:
        for m in rx.finditer(masked):
            add("aitell-opener", m.start(), m.group(0),
                f"stock AI opener/filler: '{m.group(0).strip()}'", "med")

    # 5) signposts — clustering only
    sign = [(m.start(), m.group(1)) for m in SIGNPOST_RE.finditer(masked)]
    if len(sign) >= 3:
        for pos, w in sign:
            add("aitell-signpost", pos, w,
                f"signpost '{w}' — {len(sign)} transition signposts in the doc; "
                f"AI over-signposts. Cut where the logic is already clear.", "low")

    # 6) bold-lead-in colon lists — clustering only
    bolds = [m.start() for m in BOLD_COLON_RE.finditer(raw)]  # check raw (format is structural)
    if len(bolds) >= 3:
        for pos in bolds:
            add("aitell-listformat", pos, "**…:**",
                f"'**Bold lead-in:**' list item — {len(bolds)} found; a mechanical AI list "
                f"format. (Note: bold lead-in + PERIOD is a different, fine style.)", "low")

    # 7) smart quotes (low specificity; venue-dependent)
    sq = list(SMART_QUOTE_RE.finditer(masked))
    if len(sq) >= 6:
        add("aitell-smartquote", sq[0].start(), "“ ” ‘ ’",
            f"{len(sq)} curly quotes/apostrophes — an artifact where ASCII was expected "
            f"(LOW specificity; Word/CMS also produce these).", "low")

    # 8) emoji headers/bullets
    for m in EMOJI_HEAD_RE.finditer(raw):
        add("aitell-emoji", m.start(), m.group(0).strip(),
            "emoji as a heading/bullet marker — an AI formatting tell", "low")

    # 9) sentence-length uniformity (burstiness) — informational
    sents = [len(WORD_RE.findall(s)) for s in SENT_SPLIT.split(masked) if WORD_RE.findall(s)]
    if len(sents) >= 12:
        mu = sum(sents) / len(sents)
        sd = (sum((x - mu) ** 2 for x in sents) / len(sents)) ** 0.5
        burst = sd / mu if mu else 0
        if burst < 0.45:
            findings.append({"tag": "aitell-burstiness", "line": 1,
                             "match": f"burstiness {burst:.2f}", "severity": "low",
                             "message": f"Low sentence-length variation (burstiness {burst:.2f}; "
                             f"human prose is usually higher). Vary sentence length. "
                             f"[metric: Goh-Barabasi; threshold is heuristic, not validated]"})

    # 10) folklore (opt-in)
    if folklore:
        for m in FOLKLORE_RE.finditer(masked):
            add("aitell-folklore", m.start(), m.group(0),
                f"'{m.group(0)}' — folklore AI-word (vendor/editor blogs only; "
                f"NOT academically validated). Lowest confidence.", "low")
        for rx in FOLKLORE_PHRASES:
            for m in rx.finditer(masked):
                add("aitell-folklore", m.start(), m.group(0),
                    f"folklore AI-phrase: '{m.group(0).strip()}' (low confidence)", "low")

    findings.sort(key=lambda f: (f["line"], f["tag"]))
    return {"file": None, "words": nwords, "em_per_1k": round(rate, 1),
            "count": len(findings), "findings": findings}


# --------------------------------------------------------------------------- #
CAVEAT = ("AI-tells are PROBABILISTIC and combinatorial — flag density, not single words. "
          "Many are legitimate English; word-list detectors over-flag non-native writers "
          "(61% FP in one study). Advisory only; treat as prompts to look.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Detect AI-generated-text tells (slop).")
    ap.add_argument("file", type=Path)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--folklore", action="store_true", help="add the unvalidated folklore tier")
    ap.add_argument("--strict", action="store_true", help="exit non-zero if any finding")
    ap.add_argument("--no-color", action="store_true")
    args = ap.parse_args()
    if not args.file.exists():
        print(f"error: not found: {args.file}", file=sys.stderr)
        return 2
    raw = args.file.read_text()
    res = lint(raw, folklore=args.folklore)
    res["file"] = str(args.file)

    if args.json:
        print(json.dumps({"results": [res], "total": res["count"]}, indent=2))
        return 1 if (args.strict and res["count"]) else 0

    C = (lambda s, c: s) if args.no_color else (lambda s, c: f"\033[{c}m{s}\033[0m")
    print(f"slop lint — {args.file}  ({res['words']} words, em-dash {res['em_per_1k']}/1k)")
    if not res["findings"]:
        print("  no AI-tells flagged.")
    by_tag: dict[str, list] = {}
    for f in res["findings"]:
        by_tag.setdefault(f["tag"], []).append(f)
    for tag in sorted(by_tag):
        items = by_tag[tag]
        print(C(f"\n  {tag} ({len(items)})", "33"))
        for f in items[:8]:
            print(f"    L{f['line']}: {f['message']}")
        if len(items) > 8:
            print(f"    … +{len(items) - 8} more")
    print(C(f"\n{res['count']} finding(s). Advisory only — exit 0.", "2"))
    print(C(f"⚠ {CAVEAT}", "2"))
    return 1 if (args.strict and res["count"]) else 0


if __name__ == "__main__":
    sys.exit(main())
