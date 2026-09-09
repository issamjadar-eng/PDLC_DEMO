#!/usr/bin/env python3
"""form_conformance_fix.py — rebuild a controlled document's section skeleton so
it follows its governing QMS template, without dropping a line of real content.

Companion to `form_conformance_check.py` (same resolution rules; imported from
the sibling script). For every document the checker reports `fail` — and for
every `warn` document that carries this fixer's own footprint (a TBD placeholder
or a retained-sections appendix) so an earlier pass can be re-shaped — the body
is rebuilt:

  * the template's level-2 sections are laid down IN TEMPLATE ORDER — an
    existing document section whose normalized heading matches (aliases
    honoured) is moved into place with its body unchanged; when the two raw
    headings differ only in numbering / punctuation the document heading is
    re-headed with the template's text so the numbering follows the template
    (`## 4. Approvals` → `## 12. Approvals`); a section the document lacks is
    inserted as `## <template heading>` followed by one placeholder line
      _[TBD — section required by <template id>; content to be authored.]_
  * with `--rename-aliases`, a section matched through an `--alias DOC=FORM`
    pair is re-headed with the template's heading text too;
  * every remaining document section (the checker's EXTRA) is handled one of
    two ways: an EMPTY TEMPLATE SKELETON — a section whose body is only
    `{{…}}` placeholders, TBD placeholders, empty table rows, table scaffolding
    or blank lines — is DROPPED (it duplicates the template's TBD sections and
    carries no content; counted as `dropped_empty_skeleton`); a section with
    real content is RETAINED under one closing section
      ## Appendix — Sections retained from the previous structure
    as `### <heading without its numbering prefix>`, its sub-headings demoted
    one level — so the document numbers run once, in template order;
  * an appendix produced by an earlier pass is recognised and rebuilt (its
    retained sections are promoted back, re-matched against the template, and
    re-appended) — the fixer is idempotent: a second run is a no-op;
  * the frontmatter, the leading HTML-comment metadata zone and everything
    before the first level-2 heading (title, banner, preamble) are preserved
    byte-for-byte; headings inside fenced code or HTML comments are never
    treated as sections. A section with real content is never dropped; the
    fixer refuses to write any document where a content line would be lost.
  * `--provenance-row TASK` appends one `| <date> | TASK | <summary> |` row to
    the document's existing `<!-- AI-CHANGELOG -->` block for every document
    it writes (the ai-changelog rule: each AI-assisted editing pass adds a row).

Documents reported pass / no-form / procedure / skipped, and `warn` documents
without the fixer's footprint, are left alone. Default is a dry run (per-document
plan + totals); `--apply` writes.

Exit codes: 0 = nothing to do or applied · 1 = dry run found documents to fix
· 2 = usage / precondition error.

Usage:
  form_conformance_fix.py [--root <repo>] [--apply] [--alias A=B ...] [--rename-aliases]
                          [--provenance-row TASK] [--date YYYY-MM-DD] [--json] <doc-or-folder> ...
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from datetime import date
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("form_conformance_check", _HERE / "form_conformance_check.py")
fcc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fcc)

PLACEHOLDER = "_[TBD — section required by {tid}; content to be authored.]_"
PLACEHOLDER_MARK = "_[TBD — section required by "
APPENDIX_HEADING = "Appendix — Sections retained from the previous structure"
APPENDIX_NORM = fcc.normalize_heading(APPENDIX_HEADING)
NUM_PREFIX = re.compile(r"^\d+(\.\d+)*\.?\s+")
PROVENANCE_SUMMARY = ("Section skeleton re-shaped by form_conformance_fix: template numbering "
                      "restored on reused sections, empty template-skeleton sections dropped, "
                      "sections with content retained under a single appendix")


# ---------------------------------------------------------------------------
# Heading scanning
# ---------------------------------------------------------------------------

def heading_lines(body: str, level: int) -> list[tuple[int, str]]:
    """(line_index, raw heading text) for every heading of exactly `level`
    that is not inside a fenced code block or an HTML comment."""
    out, in_fence, in_comment = [], False, False
    pat = re.compile(r"^" + "#" * level + r"\s+(?!#)(.+?)\s*$")
    for i, line in enumerate(body.split("\n")):
        stripped = line.strip()
        if in_comment:
            if "-->" in stripped:
                in_comment = False
            continue
        if stripped.startswith("<!--") and "-->" not in stripped:
            in_comment = True
            continue
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = pat.match(line)
        if m:
            out.append((i, m.group(1)))
    return out


def level2_heading_lines(body: str) -> list[tuple[int, str]]:
    return heading_lines(body, 2)


def raw_form_headings(form_body: str) -> list[str]:
    return [h for _, h in level2_heading_lines(form_body)]


def _split_blocks(lines: list[str], heads: list[tuple[int, str]]) -> list[dict]:
    blocks = []
    for n, (idx, raw) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        blocks.append({"raw": raw, "lines": lines[idx:end]})
    return blocks


def _shift_headings(lines: list[str], delta: int) -> list[str]:
    """Demote (delta=+1) or promote (delta=-1) every markdown heading in
    `lines` outside fences / comments. Never promotes below level 1."""
    out, in_fence, in_comment = [], False, False
    for line in lines:
        stripped = line.strip()
        if in_comment:
            if "-->" in stripped:
                in_comment = False
            out.append(line)
            continue
        if stripped.startswith("<!--") and "-->" not in stripped:
            in_comment = True
            out.append(line)
            continue
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        m = re.match(r"^(#{1,6})(\s+)(.*)$", line) if not in_fence else None
        if m:
            n = max(1, min(6, len(m.group(1)) + delta))
            out.append("#" * n + m.group(2) + m.group(3))
        else:
            out.append(line)
    return out


# ---------------------------------------------------------------------------
# Empty-skeleton detection
# ---------------------------------------------------------------------------

_PLACEHOLDER_RE = re.compile(r"`?\{\{[^}]*\}\}`?")
_SEP_ROW = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")


def _cells(line: str) -> list[str]:
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [c.strip() for c in inner.split("|")]


def is_empty_skeleton(section_lines: list[str]) -> bool:
    """True when a section's body (everything after its heading) carries no
    content of its own: only `{{…}}` placeholders, TBD placeholders, table
    scaffolding (headers / separators / empty rows / label-plus-placeholder
    rows), sub-headings without content, or blanks."""
    body = section_lines[1:]
    nonblank = [(i, ln) for i, ln in enumerate(body) if ln.strip()]
    if not nonblank:
        return True
    for i, ln in nonblank:
        s = ln.strip()
        if _SEP_ROW.match(s):
            continue
        if s.startswith(PLACEHOLDER_MARK):
            continue
        if re.match(r"^#{1,6}\s+", s):
            continue
        if s.startswith("|"):
            # header row: next non-blank line is a separator
            nxt = next((b.strip() for b in body[i + 1:] if b.strip()), "")
            if _SEP_ROW.match(nxt):
                continue
            cells = _cells(s)
            if all(not c for c in cells):
                continue
            if any(_PLACEHOLDER_RE.search(c) for c in cells):
                # label + placeholder row: every non-placeholder cell is a short label
                rest = [_PLACEHOLDER_RE.sub("", c).strip("` ") for c in cells]
                if all(len(r.split()) <= 4 for r in rest):
                    continue
            return False
        if _PLACEHOLDER_RE.search(s):
            residue = _PLACEHOLDER_RE.sub("", s).strip("`_* ")
            if len(residue.split()) <= 4:
                continue
            return False
        return False
    return True


# ---------------------------------------------------------------------------
# Rebuild
# ---------------------------------------------------------------------------

def _harvest_sections(body: str, aliases: dict) -> tuple[list[str], list[dict]]:
    """Preamble lines + candidate sections. A retained-sections appendix from an
    earlier pass is dissolved: each `### ` block inside it is promoted one level
    and becomes a candidate section again."""
    lines = body.split("\n")
    heads = level2_heading_lines(body)
    if not heads:
        return lines, []
    preamble = lines[: heads[0][0]]
    sections = []
    for blk in _split_blocks(lines, heads):
        norm = fcc.normalize_heading(blk["raw"])
        if norm == APPENDIX_NORM:
            inner = blk["lines"][1:]
            sub = heading_lines("\n".join(inner), 3)
            for sb in _split_blocks(inner, sub):
                promoted = _shift_headings(sb["lines"], -1)
                sections.append({"raw": sb["raw"], "lines": promoted, "from_appendix": True})
            continue
        sections.append({"raw": blk["raw"], "lines": blk["lines"], "from_appendix": False})
    for s in sections:
        n = fcc.normalize_heading(s["raw"])
        s["norm"] = aliases.get(n, n)
        s["used"] = False
    return preamble, sections


def _tail_blank(block: list[str]) -> list[str]:
    block = list(block)
    if block and block[-1].strip() != "":
        block.append("")
    return block


def rebuild(body: str, form_body: str, template_id: str, aliases: dict,
            rename_aliases: bool = False) -> tuple[str, dict]:
    preamble, sections = _harvest_sections(body, aliases)
    plan = {"reused": [], "inserted": [], "appended": [], "renamed": [], "reheaded": [],
            "dropped_empty_skeleton": [], "dropped_lines": [], "transformed_headings": []}
    out = list(preamble)
    if out and out[-1].strip() != "":
        out.append("")
    for raw_form in raw_form_headings(form_body):
        norm = fcc.normalize_heading(raw_form)
        match = next((s for s in sections if not s["used"] and s["norm"] == norm), None)
        if match is not None:
            match["used"] = True
            block = list(match["lines"])
            if block[0] != f"## {raw_form}":
                via_alias = fcc.normalize_heading(match["raw"]) != norm
                if not via_alias or rename_aliases:
                    plan["transformed_headings"].append(block[0])
                    block[0] = f"## {raw_form}"
                    (plan["renamed"] if via_alias else plan["reheaded"]).append(
                        {"from": match["raw"], "to": raw_form})
            plan["reused"].append(norm)
        else:
            block = [f"## {raw_form}", "", PLACEHOLDER.format(tid=template_id), ""]
            plan["inserted"].append(norm)
        out.extend(_tail_blank(block))
    retained = []
    for s in sections:
        if s["used"]:
            continue
        if is_empty_skeleton(s["lines"]):
            plan["dropped_empty_skeleton"].append(s["norm"])
            plan["dropped_lines"].extend(ln for ln in s["lines"] if ln.strip())
            continue
        retained.append(s)
    if retained:
        out.extend(["## " + APPENDIX_HEADING, ""])
        for s in retained:
            block = list(s["lines"])
            plan["transformed_headings"].append(block[0])
            block[0] = "### " + NUM_PREFIX.sub("", s["raw"]).strip()
            inner = _shift_headings(block[1:], +1)
            plan["transformed_headings"].extend(
                o for o, n in zip(block[1:], inner) if o != n)
            out.extend(_tail_blank([block[0]] + inner))
            plan["appended"].append(s["norm"])
    text = "\n".join(out)
    if not text.endswith("\n"):
        text += "\n"
    return text, plan


# ---------------------------------------------------------------------------
# Provenance row
# ---------------------------------------------------------------------------

def append_provenance_row(text: str, day: str, task: str, summary: str) -> tuple[str, bool]:
    """Append one row to the document's AI-CHANGELOG block (inside the leading
    HTML-comment metadata zone). Returns (text, appended)."""
    m = re.search(r"<!--\s*AI-CHANGELOG\b.*?-->", text, re.S)
    if not m:
        return text, False
    block = m.group(0)
    rows = [ln for ln in block.split("\n") if ln.strip().startswith("|")]
    if len(rows) < 2:
        return text, False
    row = f"| {day} | {task} | {summary} |"
    if row in block:
        return text, False
    last_row = rows[-1]
    idx = block.rfind(last_row)
    new_block = block[: idx + len(last_row)] + "\n" + row + block[idx + len(last_row):]
    return text[: m.start()] + new_block + text[m.end():], True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def needs_reshape(body: str) -> bool:
    return PLACEHOLDER_MARK in body or any(
        fcc.normalize_heading(h) == APPENDIX_NORM for _, h in level2_heading_lines(body))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--root", default=".")
    ap.add_argument("--apply", action="store_true", help="write the rebuilt documents (default: dry run)")
    ap.add_argument("--alias", action="append", default=[], metavar="DOC=FORM")
    ap.add_argument("--rename-aliases", action="store_true",
                    help="re-head alias-matched sections with the template's heading text")
    ap.add_argument("--provenance-row", default=None, metavar="TASK",
                    help="append a `| date | TASK | summary |` row to each written document's AI-CHANGELOG block")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    paths = [Path(p) if Path(p).is_absolute() else root / p for p in args.paths]
    for p in paths:
        if not p.exists():
            print(f"error: path not found: {p}", file=sys.stderr)
            return 2
    aliases = {}
    for a in args.alias:
        if "=" not in a:
            print(f"error: --alias expects DOC=FORM, got {a!r}", file=sys.stderr)
            return 2
        d, f = a.split("=", 1)
        aliases[fcc.normalize_heading(d)] = fcc.normalize_heading(f)

    idx = fcc.registry_index(root)
    cache: dict = {}
    plans, fixed, rows_added = [], 0, 0
    for doc in fcc.iter_docs(paths):
        res = fcc.check_document(doc, root, idx, cache, aliases, False, None)
        text = doc.read_text(encoding="utf-8", errors="replace")
        fm_end = 0
        if text.startswith("---"):
            e = text.find("\n---", 3)
            fm_end = e + 4 if e != -1 else 0
        head, body = text[:fm_end], text[fm_end:]
        if res["status"] == "fail":
            pass
        elif res["status"] == "warn" and needs_reshape(body):
            pass
        else:
            continue
        form_path = root / res["form"]
        _, form_body = fcc.split_frontmatter(form_path.read_text(encoding="utf-8", errors="replace"))
        new_body, plan = rebuild(body, form_body, res["template_id"] or Path(res["form"]).stem, aliases,
                                 args.rename_aliases)
        if new_body == body:
            continue  # already in shape — idempotent no-op
        plan.update(doc=res["doc"], template_id=res["template_id"], form=res["form"], status_before=res["status"])
        # Safety: every original non-blank line must survive, except headings the
        # fixer deliberately re-headed / demoted and lines of dropped empty skeletons.
        excluded = set(plan["transformed_headings"])
        dropped = list(plan["dropped_lines"])
        before = [ln for ln in body.split("\n") if ln.strip() and ln not in excluded]
        for ln in dropped:
            if ln in before:
                before.remove(ln)
        after = [ln for ln in new_body.split("\n") if ln.strip()]
        lost = [ln for ln in before if before.count(ln) > after.count(ln)]
        plan["content_preserved"] = not lost
        if lost:
            plan["lost_lines"] = lost[:5]
        plans.append(plan)
        if args.apply and not lost:
            final = head + new_body
            if args.provenance_row:
                final, added = append_provenance_row(final, args.date, args.provenance_row, PROVENANCE_SUMMARY)
                plan["provenance_row_added"] = added
                rows_added += int(added)
            doc.write_text(final, encoding="utf-8")
            fixed += 1
    summary = {"documents_to_fix": len(plans), "applied": fixed if args.apply else 0,
               "inserted_sections": sum(len(p["inserted"]) for p in plans),
               "reused_sections": sum(len(p["reused"]) for p in plans),
               "reheaded_sections": sum(len(p["reheaded"]) for p in plans),
               "appended_extra_sections": sum(len(p["appended"]) for p in plans),
               "dropped_empty_skeleton": sum(len(p["dropped_empty_skeleton"]) for p in plans),
               "dropped_lines": sum(len(p["dropped_lines"]) for p in plans),
               "provenance_rows_added": rows_added,
               "content_preserved_all": all(p["content_preserved"] for p in plans)}
    if args.json:
        print(json.dumps({"root": str(root), "apply": args.apply, "summary": summary, "plans": plans}, indent=2))
    else:
        mode = "APPLIED" if args.apply else "DRY RUN"
        print(f"form-conformance-fix [{mode}]: {len(plans)} document(s) to fix — "
              f"insert {summary['inserted_sections']}, reuse {summary['reused_sections']} "
              f"(re-headed {summary['reheaded_sections']}), retain {summary['appended_extra_sections']} in appendix, "
              f"drop {summary['dropped_empty_skeleton']} empty skeleton(s); "
              f"content preserved: {summary['content_preserved_all']}")
        for p in plans:
            print(f"  {p['doc']}  ← {p['template_id']}: +{len(p['inserted'])} inserted, {len(p['reused'])} reused, "
                  f"{len(p['appended'])} retained, {len(p['dropped_empty_skeleton'])} dropped"
                  + ("" if p["content_preserved"] else "  !! CONTENT LOSS — skipped"))
    if args.apply:
        return 0 if summary["content_preserved_all"] else 1
    return 1 if plans else 0


if __name__ == "__main__":
    sys.exit(main())
