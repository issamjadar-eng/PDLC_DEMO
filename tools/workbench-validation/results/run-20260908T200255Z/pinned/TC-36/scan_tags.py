#!/usr/bin/env python3
"""scan_tags.py — deterministic lint for the tagged-content blocks the
/strategy and /lessons harvesters read out of task documents.

Grammar (shared/task-content-scanner.md): a block marker is a line that,
after trimming, is exactly one HTML comment of the form

    <!-- STRATEGY CONTENT: <domain>, <topic>, ... -->
    <!-- LESSONS LEARNED: <category>, ... -->

outside fenced code blocks. The harvesters grep for the exact marker text
and silently skip anything else — so a tag with a typo in the marker, a
missing colon, an unknown domain key, an unclosed comment, or prose on the
same line is content that will never reach the durable record. This script
finds those blocks and reports them, so "tagged but never harvested" becomes
a finding instead of a surprise.

Owner: the strategy skill (it owns the domain-key vocabulary, read from
project.yml strategy_domains[]); the lessons harvester shares the grammar.

Exit codes: 0 no malformed tags · 1 malformed tags found · 2 usage/precondition.
Usage: scan_tags.py [--project-root DIR] [--json] [PATH ...]
  PATH defaults to <root>/tasks/*/[0-9][0-9][0-9]-*.md
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

STRATEGY = "STRATEGY CONTENT"
LESSONS = "LESSONS LEARNED"
EXACT = re.compile(r"^<!--\s(STRATEGY CONTENT|LESSONS LEARNED):\s*([^>]*?)\s*-->$")
# Anything that looks like an attempt at either marker (case/punctuation-insensitive).
LOOSE = re.compile(r"<!--\s*(strategy[\s_-]*content|lessons?[\s_-]*learn(?:ed|t)?)\b", re.IGNORECASE)
FENCE = re.compile(r"^\s*(```|~~~)")


def load_domain_keys(root: Path):
    """Domain keys from project.yml strategy_domains[].key (None if unavailable)."""
    pyml = root / "project.yml"
    if not pyml.is_file():
        return None
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(pyml.read_text(encoding="utf-8")) or {}
        keys = [d.get("key") for d in data.get("strategy_domains") or [] if isinstance(d, dict)]
        return sorted(k for k in keys if k)
    except Exception:
        # PyYAML missing or file odd — regex fallback on the block.
        text = pyml.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^strategy_domains:\s*$(.*?)(?=^\S)", text, re.S | re.M)
        if not m:
            return None
        return sorted(set(re.findall(r"^\s*-\s*key:\s*([\w-]+)", m.group(1), re.M)))


def _strip_inline_code(line: str) -> str:
    return re.sub(r"`[^`]*`", "", line)


def scan_file(path: Path, domain_keys):
    ok, bad = 0, []
    in_fence = False
    for lineno, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = raw.strip()
        m = EXACT.match(stripped)
        if m:
            kind, values = m.group(1), [v.strip() for v in m.group(2).split(",") if v.strip()]
            if not values:
                bad.append(_f(path, lineno, "empty-tag", stripped,
                              f"no values after '{kind}:' — expected domain/category, topics"))
            elif kind == STRATEGY and domain_keys is not None and values[0] not in domain_keys:
                bad.append(_f(path, lineno, "unknown-domain", stripped,
                              f"domain '{values[0]}' not in project.yml strategy_domains "
                              f"(known: {', '.join(domain_keys)})"))
            else:
                ok += 1
            continue
        # Not an exact marker — is it an attempt at one, outside inline code?
        visible = _strip_inline_code(raw)
        lm = LOOSE.search(visible)
        if not lm:
            continue
        if "-->" not in visible:
            bad.append(_f(path, lineno, "unclosed-comment", stripped, "no closing '-->' on the tag line"))
        elif not stripped.startswith("<!--") or not stripped.endswith("-->"):
            bad.append(_f(path, lineno, "prose-on-line", stripped,
                          "tag shares its line with other text — the harvester only reads a "
                          "comment standing alone on the line"))
        elif re.match(r"^<!--\s*(STRATEGY CONTENT|LESSONS LEARNED)\s*-->$", stripped):
            bad.append(_f(path, lineno, "empty-tag", stripped, "bare marker with no ': values'"))
        elif re.match(r"^<!--\s(STRATEGY CONTENT|LESSONS LEARNED)\s*-->$", stripped):
            bad.append(_f(path, lineno, "empty-tag", stripped, "bare marker with no ': values'"))
        else:
            # Same words, wrong spelling/spacing/case/punctuation → harvester will not match.
            bad.append(_f(path, lineno, "marker-text", stripped,
                          "marker must read exactly '<!-- STRATEGY CONTENT: ...' or "
                          "'<!-- LESSONS LEARNED: ...' (one space after '<!--', a colon, uppercase)"))
    return ok, bad


def _f(path, lineno, kind, text, why):
    return {"file": str(path), "line": lineno, "kind": kind, "text": text[:160], "why": why}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="task docs or folders (default: tasks/*/NNN-*.md)")
    ap.add_argument("--project-root", default=".", help="repo root (project.yml for domain keys)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.project_root).resolve()
    files: list[Path] = []
    if args.paths:
        for p in args.paths:
            pp = Path(p)
            if pp.is_dir():
                files += sorted(pp.rglob("*.md"))
            elif pp.is_file():
                files.append(pp)
            else:
                files += [Path(x) for x in sorted(glob.glob(p))]
    else:
        files = [Path(x) for x in sorted(glob.glob(str(root / "tasks" / "*" / "[0-9][0-9][0-9]-*.md")))]
    if not files:
        print("scan_tags: no task documents found", file=sys.stderr)
        return 2
    domain_keys = load_domain_keys(root)
    total_ok, findings = 0, []
    for f in files:
        ok, bad = scan_file(f, domain_keys)
        total_ok += ok
        findings += bad
    report = {
        "files_scanned": len(files),
        "well_formed_blocks": total_ok,
        "malformed": len(findings),
        "domain_keys": domain_keys,
        "findings": findings,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"scan_tags: {len(files)} file(s), {total_ok} well-formed block(s), "
              f"{len(findings)} malformed tag(s)"
              + ("" if domain_keys is not None else " (domain keys unavailable — not validated)"))
        for x in findings:
            print(f"  {x['file']}:{x['line']} [{x['kind']}] {x['why']}\n      {x['text']}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
