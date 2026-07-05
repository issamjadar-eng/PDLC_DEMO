#!/usr/bin/env python3
"""gen_qsub_sad_extract — generate a Q-Sub-scoped System Architecture extract from the
canonical 510(k) System Architecture Document.

The canonical SAD is a full 510(k) technical-file artifact (all sections, a child-SAD
tree, module internals). A Q-Submission needs only the boundary/architecture altitude that
frames its transmitted questions. Rather than hand-maintain a divergent copy of a controlled
document, this tool DERIVES a scoped extract as a **generated projection**: it selects an
allowlisted section set, strips 🔒 `<details>` internal containers (by balanced tag) and any
child-SAD reference tables, and stamps a provenance banner (`Generated from … do not
hand-edit`) plus a Q-Sub scoping preface. Regenerate whenever the canonical SAD changes.

Project-agnostic: the section allowlist, title, and preface are CLI arguments — no
project-specific section numbers are baked into the script.

Usage:
  python3 gen_qsub_sad_extract.py --sad <canonical.md> --out <extract.md>
      --sections 1,2,4,5.2,5.3,5.5,8.3,9.3,10.2
      [--title "System Architecture Overview (Q-Sub extract)"]
      [--preface "Provided to frame the …(Topic 2) questions; the full per-module technical
                  architecture accompanies the 510(k)."]
Exit 0 on success.
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

HEADING = re.compile(r"^(#{2,4})\s+(?:§\s*)?(\d+(?:\.\d+)*)[.)]?\s+(.*)$")
DETAILS_OPEN = re.compile(r"<details\b", re.I)
DETAILS_CLOSE = re.compile(r"</details\s*>", re.I)

# Prose child-SAD/SRS references → 510(k)-forward-reference form, so the generated extract is
# self-consistent (no pointer to a non-transmitted doc). Applied only to the derived extract;
# the canonical SAD is never modified. The result matches qsub_scope_lint's C2 allowlist.
REFRAME = [
    # markdown link whose text names a per-module SAD (e.g. "See [Intra-Op SAD 1.0.0](…)") →
    # a forward-reference (drop the link into a non-transmitted doc; keep the meaning).
    (re.compile(r"See\s+\[[^\]]*\bSADs?\b[^\]]*\]\([^)]*\)", re.I),
     "See the per-module Software Architecture Document (part of the 510(k) technical file)"),
    (re.compile(r"(documented in|deferred to)\s+the\s+child\s+[A-Za-z /-]*?SADs?(\s*/\s*SRS)?", re.I),
     r"\1 the per-module architecture records (part of the 510(k) technical file)"),
    (re.compile(r"\bthe\s+child\s+[A-Za-z /-]*?SADs?\b", re.I),
     "the per-module architecture records (part of the 510(k) technical file)"),
    (re.compile(r"\bchild\s+SADs?\b", re.I),
     "per-module architecture records (part of the 510(k) technical file)"),
]


def reframe(line: str) -> str:
    for rx, rep in REFRAME:
        line = rx.sub(rep, line)
    return line


# Conservative, deterministic em-dash reduction for the generated extract. Heavy em-dash use
# is an AI-writing tell (writing-well `slop`); the dominant, SAFE pattern to auto-convert is a
# bold label followed by an em-dash — `**Bold label** — description` → `**Bold label:** description`.
# Only this form is converted (a colon is unambiguous after a label); prose-aside em-dashes need
# human judgment and are left. The canonical SAD is never touched — this acts on the projection.
_EMDASH_LABEL = re.compile(r"(?<=\S)\*\* — ")


def thin_emdashes(line: str) -> str:
    return _EMDASH_LABEL.sub(":** ", line)


def strip_internal_and_tables(lines: list[str]) -> list[str]:
    """Drop 🔒 <details>…</details> containers (balanced tag, nesting-safe), leading <!-- -->
    metadata, and any markdown table whose header row names a Child SAD."""
    out, depth, in_comment = [], 0, False
    i = 0
    while i < len(lines):
        ln = lines[i]
        if in_comment:
            if "-->" in ln:
                in_comment = False
            i += 1
            continue
        if ln.lstrip().startswith("<!--") and "-->" not in ln:
            in_comment = True
            i += 1
            continue
        opens, closes = len(DETAILS_OPEN.findall(ln)), len(DETAILS_CLOSE.findall(ln))
        if depth > 0:
            depth = max(0, depth + opens - closes)
            i += 1
            continue
        if opens > closes:
            depth += opens - closes
            i += 1
            continue
        # a child-SAD table: header row contains "Child SAD" — skip the contiguous table block
        if ln.lstrip().startswith("|") and re.search(r"child\s+sad", ln, re.I):
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                i += 1
            continue
        out.append(ln)
        i += 1
    return out


def select_sections(lines: list[str], allow: list[str]) -> list[str]:
    """Emit allowlisted sections. A heading is 'full' (heading + body) if its number equals or
    descends from an allowlisted number; 'heading-only' if it is an ancestor of one (keeps the
    hierarchy navigable); else skipped. Body = lines until the next heading."""
    # index headings
    heads = []
    for idx, ln in enumerate(lines):
        m = HEADING.match(ln)
        if m:
            heads.append((idx, m.group(2), ln))
    heads.append((len(lines), None, None))  # sentinel

    def mode(num: str) -> str:
        for a in allow:
            if num == a or num.startswith(a + "."):
                return "full"
        for a in allow:
            if a.startswith(num + "."):
                return "heading-only"
        return "skip"

    out = []
    for h in range(len(heads) - 1):
        start, num, hline = heads[h]
        end = heads[h + 1][0]
        m = mode(num)
        if m == "full":
            out.extend(lines[start:end])
        elif m == "heading-only":
            out.append(hline)
            out.append("")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sad", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sections", required=True, help="comma-separated dotted section numbers")
    ap.add_argument("--title", default="System Architecture Overview (Q-Sub extract)")
    ap.add_argument("--preface", default="This Q-Sub extract is the system-level architectural "
                    "view provided to frame the transmitted questions; the full per-module "
                    "technical architecture — including each module's Software Architecture "
                    "Document — accompanies the planned 510(k).")
    a = ap.parse_args()
    sad = Path(a.sad)
    src = sad.read_text(encoding="utf-8").split("\n")
    allow = [s.strip() for s in a.sections.split(",") if s.strip()]

    # derive a source-version tag from the SAD path (…/<doctype>/<version>.md) for provenance
    version = sad.stem
    body = select_sections(src, allow)
    body = strip_internal_and_tables(body)
    body = [thin_emdashes(reframe(l)) for l in body]

    banner = (
        "<!-- GENERATED FILE — do not hand-edit. Produced by "
        "`submissions/scripts/gen_qsub_sad_extract.py` as a Q-Sub-scoped projection of the "
        f"canonical System Architecture Document ({sad.as_posix()}, {version}). "
        f"Sections: § {', § '.join(allow)}. Regenerate when the canonical SAD changes. -->\n"
    )
    header = (
        f"<!-- AUTO:PAGE-TITLE -->\n# {a.title}\n<!-- /AUTO:PAGE-TITLE -->\n\n"
        f"> **Q-Sub scope note.** {a.preface}\n\n"
        f"_Generated from the controlled System Architecture Document {version} "
        f"(§ {', § '.join(allow)}); the child Software Architecture Documents are not attachments "
        f"to this Pre-Submission._\n"
    )
    out_text = banner + "\n" + header + "\n" + "\n".join(body).strip() + "\n"
    Path(a.out).write_text(out_text, encoding="utf-8")
    kept = sum(1 for l in body if HEADING.match(l))
    print(f"wrote {a.out} — {kept} sections (§ {', § '.join(allow)}), {len(out_text.split(chr(10)))} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
