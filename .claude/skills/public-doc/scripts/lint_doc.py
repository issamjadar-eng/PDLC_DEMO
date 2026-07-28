#!/usr/bin/env python3
"""
lint_doc.py — advisory lint for public-doc drafts.

Reports findings grouped by category. It is ADVISORY: it always exits 0 so it
never blocks a build. (A future policy may promote the `leak` category to a hard
gate — see the skill README roadmap.)

It reads project-specific values from `tools/public-doc/` if present:
  - brand.yml      : naming rules, required disclaimers, banned phrases
  - lint-rules.yml : written-guideline patterns (banned words, weasel words, ...)
  - style.md       : human-readable style guide (not parsed; mentioned in output)

The skill itself ships NO company values — everything brand/style-specific is in
the project config, which keeps the skill reusable across projects.

Usage:
    python3 lint_doc.py DRAFT.md [--config-dir tools/public-doc] [--json]
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path

# Optional YAML — degrade to a tiny parser if PyYAML isn't installed, so the
# skill works in a bare environment.
try:
    import yaml  # type: ignore
    _HAVE_YAML = True
except Exception:
    _HAVE_YAML = False


@dataclass
class Finding:
    category: str   # leak | brand | style | verify
    line: int
    message: str
    excerpt: str = ""


@dataclass
class Report:
    path: str
    findings: list[Finding] = field(default_factory=list)

    def add(self, *a, **kw):
        self.findings.append(Finding(*a, **kw))

    def by_category(self) -> dict[str, list[Finding]]:
        out: dict[str, list[Finding]] = {}
        for f in self.findings:
            out.setdefault(f.category, []).append(f)
        return out


def lineno(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


# --------------------------------------------------------------------------- #
# config loading
# --------------------------------------------------------------------------- #
def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    raw = path.read_text()
    if _HAVE_YAML:
        try:
            return yaml.safe_load(raw) or {}
        except Exception as e:
            print(f"[lint] warning: could not parse {path}: {e}", file=sys.stderr)
            return {}
    # Minimal fallback: parse top-level `key:` and simple `- item` lists.
    return _mini_yaml(raw)


def _mini_yaml(raw: str) -> dict:
    """A small but correct YAML-subset parser used when PyYAML is absent.

    Handles the shapes the seed configs use: nested mappings, block lists
    (`- item`), block lists of flow dicts (`- {word: x, suggest: y}`), flow lists
    (`[a, b]`), quoted/unquoted scalars, and inline `# comments`. PyYAML is still
    preferred when installed; this keeps the skill working in a bare environment.
    """
    lines = [ln for ln in raw.splitlines()
             if ln.strip() and not ln.lstrip().startswith("#")]
    if not lines:
        return {}
    val, _ = _parse_block(lines, 0, _indent(lines[0]))
    return val if isinstance(val, dict) else {}


def _indent(s: str) -> int:
    return len(s) - len(s.lstrip())


def _strip_inline_comment(s: str) -> str:
    out, q, i = [], None, 0
    while i < len(s):
        c = s[i]
        if q:
            out.append(c)
            if c == q:
                q = None
        elif c in ('"', "'"):
            q = c
            out.append(c)
        elif c == "#" and (not out or s[i - 1] == " "):
            break
        else:
            out.append(c)
        i += 1
    return "".join(out).rstrip()


def _split_commas(s: str) -> list[str]:
    parts, q, depth, cur = [], None, 0, ""
    for c in s:
        if q:
            cur += c
            if c == q:
                q = None
        elif c in ('"', "'"):
            q = c
            cur += c
        elif c in "{[":
            depth += 1
            cur += c
        elif c in "}]":
            depth -= 1
            cur += c
        elif c == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += c
    if cur.strip():
        parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def _flow_map(v: str) -> dict:
    d = {}
    for item in _split_commas(v[1:-1].strip()):
        if ":" in item:
            k, _, val = item.partition(":")
            d[k.strip().strip("'\"")] = _scalar(val.strip())
    return d


def _scalar(v: str):
    v = v.strip()
    if not v:
        return ""
    if v[0] == "{" and v[-1] == "}":
        return _flow_map(v)
    if v[0] == "[" and v[-1] == "]":
        inner = v[1:-1].strip()
        return [_scalar(x) for x in _split_commas(inner)] if inner else []
    if len(v) >= 2 and v[0] == v[-1] == '"':
        return _decode_double(v[1:-1])     # double-quote: process escapes (\\ -> \)
    if len(v) >= 2 and v[0] == v[-1] == "'":
        return v[1:-1].replace("''", "'")  # single-quote: only '' -> '
    return v


def _decode_double(s: str) -> str:
    """Decode YAML double-quote escapes the way PyYAML would, so a regex written
    as "\\b..." yields \\b (one backslash) under either parser."""
    out, i = [], 0
    table = {"n": "\n", "t": "\t", "\\": "\\", '"': '"', "'": "'", "/": "/", "0": "\0"}
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            out.append(table.get(s[i + 1], s[i + 1]))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _parse_block(lines: list[str], i: int, indent: int):
    first = _strip_inline_comment(lines[i]).strip()
    if first.startswith("- "):
        return _parse_list(lines, i, indent)
    return _parse_map(lines, i, indent)


def _parse_map(lines: list[str], i: int, indent: int):
    d: dict = {}
    while i < len(lines):
        raw = _strip_inline_comment(lines[i])
        if not raw.strip():
            i += 1
            continue
        ind = _indent(raw)
        if ind < indent:
            break
        s = raw.strip()
        if s.startswith("- ") or ":" not in s:
            i += 1
            continue
        k, _, v = s.partition(":")
        k, v = k.strip(), v.strip()
        if v == "":
            j = i + 1
            while j < len(lines) and not _strip_inline_comment(lines[j]).strip():
                j += 1
            if j < len(lines):
                child = _strip_inline_comment(lines[j])
                nind = _indent(child)
                if nind > indent or (nind == indent and child.strip().startswith("- ")):
                    d[k], i = _parse_block(lines, j, nind)
                    continue
            d[k] = {}
            i += 1
        else:
            d[k] = _scalar(v)
            i += 1
    return d, i


def _parse_list(lines: list[str], i: int, indent: int):
    lst: list = []
    while i < len(lines):
        raw = _strip_inline_comment(lines[i])
        if not raw.strip():
            i += 1
            continue
        ind = _indent(raw)
        if ind < indent or not raw.strip().startswith("- "):
            break
        item = raw.strip()[2:].strip()
        if item == "":
            val, i = _parse_block(lines, i + 1, indent + 2)
            lst.append(val)
        else:
            lst.append(_scalar(item))
            i += 1
    return lst, i


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #
INTERNAL_BLOCK = re.compile(r"<!--\s*INTERNAL:BEGIN\b.*?INTERNAL:END\s*-->", re.DOTALL)
VERIFY_FLAG = re.compile(r"\[VERIFY\]")


COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def _comment_spans(md: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in COMMENT.finditer(md)]


def _in_span(idx: int, spans: list[tuple[int, int]]) -> bool:
    return any(s <= idx < e for s, e in spans)


def check_leaks(md: str, rep: Report) -> None:
    """The leak category: anything that risks internal content reaching the public
    artifact, or a malformed block that strip can't handle.

    Two valid INTERNAL forms are supported:
      - collapsible/paired:  <!-- INTERNAL:BEGIN [label] -->  …content…  <!-- INTERNAL:END -->
      - single comment:      <!-- INTERNAL:BEGIN [label] …content… INTERNAL:END -->
    The robust, form-agnostic check: every INTERNAL marker must sit inside an HTML
    comment. If one doesn't, either the marker itself or the content around it would
    render into the public artifact. (This also catches the single-comment `-->`
    early-close case — the stray `-->` ends the comment, leaving INTERNAL:END outside
    any comment.)"""
    begins = list(re.finditer(r"INTERNAL:BEGIN\b", md))
    ends = list(re.finditer(r"INTERNAL:END\b", md))
    if len(begins) != len(ends):
        rep.add("leak", lineno(md, begins[0].start()) if begins else 1,
                f"unbalanced INTERNAL markers ({len(begins)} BEGIN / {len(ends)} END) — "
                "a block won't strip cleanly")

    spans = _comment_spans(md)
    for mo in begins + ends:
        if not _in_span(mo.start(), spans):
            rep.add("leak", lineno(md, mo.start()),
                    f"{mo.group(0)} marker is not inside an HTML comment — the marker "
                    "or its surrounding content would render. Wrap as "
                    "'<!-- INTERNAL:BEGIN -->' … '<!-- INTERNAL:END -->' (collapsible) "
                    "or a single '<!-- INTERNAL:BEGIN … INTERNAL:END -->'.")


def public_text(md: str) -> str:
    """Markdown with INTERNAL blocks blanked (line-count preserved) so brand/style
    checks only see what the public will actually read."""
    def blank(m: re.Match) -> str:
        return "\n" * m.group(0).count("\n")
    return INTERNAL_BLOCK.sub(blank, md)


def check_verify(md: str, rep: Report) -> None:
    pub = public_text(md)
    for mo in VERIFY_FLAG.finditer(pub):
        rep.add("verify", lineno(pub, mo.start()),
                "[VERIFY] flag in public-facing text — resolve before publishing")
    # VERIFY inside INTERNAL is fine (it's a note-to-self), so only public counts.


def read_brand_profile(md: str) -> str | None:
    m = re.match(r"\A---\n(.*?)\n---\n", md, re.DOTALL)
    if m:
        pm = re.search(r"^\s*brand_profile:\s*(.+?)\s*$", m.group(1), re.MULTILINE)
        if pm:
            return pm.group(1).strip().strip("'\"")
    return None


def resolve_profile(brand: dict, profile: str) -> dict:
    """brand.yml is profile-nested (default:, neutral:, ...). Pick the requested
    profile; fall back to `default`; tolerate a flat (un-profiled) file."""
    if isinstance(brand.get(profile), dict):
        return brand[profile]
    if isinstance(brand.get("default"), dict):
        return brand["default"]
    return brand  # already flat


def check_brand(md: str, brand: dict, rep: Report) -> None:
    pub = public_text(md)
    # banned phrases (e.g., internal-only economics language in an external doc)
    for phrase in brand.get("banned_phrases", []) or []:
        for mo in re.finditer(re.escape(phrase), pub, re.IGNORECASE):
            rep.add("brand", lineno(pub, mo.start()),
                    f"banned phrase {phrase!r} (brand.yml) appears in public text",
                    excerpt=phrase)
    # required naming: e.g., first mention must be the full legal form
    naming = brand.get("naming", {}) or {}
    canonical = naming.get("canonical")
    variants = naming.get("disallowed_variants", []) or []
    for v in variants:
        for mo in re.finditer(re.escape(v), pub):
            rep.add("brand", lineno(pub, mo.start()),
                    f"use the canonical name {canonical!r} instead of {v!r} (brand.yml)",
                    excerpt=v)
    # required disclaimers must be present somewhere
    for disc in brand.get("required_disclaimers", []) or []:
        if disc and disc.lower() not in pub.lower():
            rep.add("brand", 0, f"required disclaimer missing: {disc!r} (brand.yml)")


def check_style(md: str, rules: dict, rep: Report) -> None:
    pub = public_text(md)
    for entry in rules.get("banned_words", []) or []:
        # entry may be a string or {word, suggest}
        word = entry if isinstance(entry, str) else entry.get("word", "")
        suggest = "" if isinstance(entry, str) else entry.get("suggest", "")
        if not word:
            continue
        for mo in re.finditer(rf"\b{re.escape(word)}\b", pub, re.IGNORECASE):
            msg = f"avoid {word!r}" + (f" — prefer {suggest!r}" if suggest else "")
            rep.add("style", lineno(pub, mo.start()), f"{msg} (lint-rules.yml)", excerpt=word)
    for pat in rules.get("regex_flags", []) or []:
        rx = pat if isinstance(pat, str) else pat.get("pattern", "")
        note = "" if isinstance(pat, str) else pat.get("note", "")
        if not rx:
            continue
        try:
            for mo in re.finditer(rx, pub):
                rep.add("style", lineno(pub, mo.start()),
                        f"matched style pattern {rx!r}" + (f": {note}" if note else ""),
                        excerpt=mo.group(0)[:60])
        except re.error as e:
            print(f"[lint] warning: bad regex in lint-rules.yml: {rx!r} ({e})", file=sys.stderr)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def render_text(rep: Report) -> str:
    cats = rep.by_category()
    order = ["leak", "brand", "style", "verify"]
    icons = {"leak": "🚨 LEAK", "brand": "🅱  BRAND", "style": "✎ STYLE", "verify": "⚑ VERIFY"}
    lines = [f"public-doc lint — {rep.path}"]
    total = len(rep.findings)
    if total == 0:
        lines.append("  ✓ no findings")
        return "\n".join(lines)
    for cat in order:
        items = cats.get(cat, [])
        if not items:
            continue
        lines.append(f"\n{icons[cat]} ({len(items)})")
        for f in sorted(items, key=lambda x: x.line):
            loc = f"L{f.line}" if f.line else "—"
            lines.append(f"  {loc}: {f.message}")
    lines.append(f"\n{total} finding(s). Advisory only — nothing blocked. "
                 "(leak findings are the ones to fix before publishing.)")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("--config-dir", type=Path, default=Path("tools/public-doc"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 0  # advisory: still exit 0

    md = args.input.read_text()
    rep = Report(path=str(args.input))

    brand = load_yaml(args.config_dir / "brand.yml")
    rules = load_yaml(args.config_dir / "lint-rules.yml")
    if not (args.config_dir / "brand.yml").exists():
        print(f"[lint] note: no project config at {args.config_dir} — "
              "run `/public-doc init` to scaffold it. Running leak+verify checks only.",
              file=sys.stderr)

    brand_cfg = resolve_profile(brand, read_brand_profile(md) or "default")

    check_leaks(md, rep)
    check_verify(md, rep)
    check_brand(md, brand_cfg, rep)
    check_style(md, rules, rep)

    if args.json:
        print(json.dumps({"path": rep.path,
                          "findings": [asdict(f) for f in rep.findings]}, indent=2))
    else:
        print(render_text(rep))
    return 0  # always advisory


if __name__ == "__main__":
    sys.exit(main())
