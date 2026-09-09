#!/usr/bin/env python3
"""ai_changelog_check.py — is AI-assisted provenance recorded the way the
ai-changelog rule requires, and is the document vendor-neutral?

Deterministic checker behind `rules/ai-changelog.md`. Stdlib + PyYAML only.

For every controlled markdown document given (files, or folders walked
recursively — README.md, `formal/`, `images/`, `_scratch/`, `_work/` excluded):

  BLOCK      An `<!-- AI-CHANGELOG … -->` HTML comment exists in the LEADING
             METADATA ZONE — the run of YAML frontmatter and HTML comments before
             the first rendered line — and carries a `| Date | Task | Summary |`
             table with at least one data row.                        → failure
  PLACEMENT  No `AI-CHANGELOG` marker appears in the rendered body or inside a
             `<details>` block (those round-trip downstream).          → failure
  VENDOR     No AI model / tool / vendor product name appears in the document's
             CONTENT — the rendered body, the AI-CHANGELOG rows, and any other
             leading HTML-comment changelog. The only sanctioned label is
             "AI assistant(s)".                                        → failure
             Reading of the rule for the YAML frontmatter: it is tool-managed
             conversion metadata (docflow round-trip fields such as
             `conversion_method`), not authored content or a changelog, so a
             vendor name there is reported as a WARNING, not a failure. Pass
             `--strict` to make it a failure too.

Which documents must carry the block: by default every document checked
(`--require-block`, the posture for a controlled tree where AI assistance is the
norm). With `--ai-authored-only` the block is required only where the
frontmatter itself says an AI produced the file (`conversion_method` containing
`ai`, `llm`, `assistant`, `claude`, `gpt`, `copilot`, `gemini`); VENDOR and
PLACEMENT still apply to every document.

Exit codes: 0 = no failures (warnings allowed) · 1 = failures · 2 = usage error.
`--json` prints a machine-readable report.

Usage:
  ai_changelog_check.py [--root <repo>] [--ai-authored-only] [--strict] [--json] <doc-or-folder> ...
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required (uv run --with pyyaml ...).")

EXCLUDE_NAMES = {"README.md"}
EXCLUDE_DIRS = {"formal", "images", "_scratch", "_work", ".git", "node_modules"}

# Product / vendor names the rule forbids in document content. Matched as whole
# words, case-insensitive. "AI assistant" is the sanctioned label.
VENDOR_TELLS = [
    r"claude(?:\s+code)?", r"anthropic", r"chatgpt", r"gpt-?\d*[a-z0-9.-]*", r"openai",
    r"gemini", r"copilot", r"llama", r"mistral", r"cursor\s+ai",
]
VENDOR_RE = re.compile(r"(?<![\w/.])(" + "|".join(VENDOR_TELLS) + r")(?!\w)", re.IGNORECASE)
AI_METHOD_RE = re.compile(r"\b(ai|llm|assistant|claude|gpt|copilot|gemini)\b", re.IGNORECASE)
BLOCK_RE = re.compile(r"<!--\s*AI-CHANGELOG\b.*?-->", re.DOTALL | re.IGNORECASE)
HEADER_RE = re.compile(r"^\|\s*Date\s*\|\s*Task\s*\|\s*Summary\s*\|\s*$", re.IGNORECASE | re.MULTILINE)


def split_frontmatter(text: str):
    if not text.startswith("---"):
        return None, "", text
    end = text.find("\n---", 3)
    if end == -1:
        return None, "", text
    raw = text[3:end]
    body = text[end + 4:]
    try:
        fm = yaml.safe_load(raw)
    except yaml.YAMLError:
        fm = None
    return (fm if isinstance(fm, dict) else None), raw, body


def split_metadata_zone(after_fm: str):
    """Return (metadata_zone, rendered_body). The zone is the leading run of
    blank lines and complete HTML comments before the first rendered line."""
    pos = 0
    n = len(after_fm)
    while pos < n:
        m = re.match(r"\s*", after_fm[pos:])
        pos += m.end()
        if pos >= n:
            break
        if after_fm.startswith("<!--", pos):
            close = after_fm.find("-->", pos)
            if close == -1:
                break
            pos = close + 3
            continue
        break
    return after_fm[:pos], after_fm[pos:]


def block_ok(zone: str) -> tuple[bool, str]:
    m = BLOCK_RE.search(zone)
    if not m:
        return False, "no <!-- AI-CHANGELOG --> block in the leading metadata zone"
    block = m.group(0)
    if not HEADER_RE.search(block):
        return False, "AI-CHANGELOG block has no `| Date | Task | Summary |` header"
    rows = [ln for ln in block.splitlines()
            if ln.strip().startswith("|") and not HEADER_RE.match(ln.strip())
            and not re.match(r"^\|[\s:-]+\|[\s:|-]*$", ln.strip())]
    if not rows:
        return False, "AI-CHANGELOG block has a header but no rows"
    return True, f"{len(rows)} row(s)"


def vendor_hits(text: str) -> list[str]:
    seen, out = set(), []
    for m in VENDOR_RE.finditer(text):
        w = m.group(1)
        key = w.lower()
        if key not in seen:
            seen.add(key)
            out.append(w)
    return out


def iter_docs(paths):
    for p in paths:
        if p.is_file():
            if p.suffix == ".md" and p.name not in EXCLUDE_NAMES:
                yield p
        elif p.is_dir():
            for f in sorted(p.rglob("*.md")):
                if f.name in EXCLUDE_NAMES or EXCLUDE_DIRS & set(f.relative_to(p).parts[:-1]):
                    continue
                yield f


def check_document(doc: Path, root: Path, ai_authored_only: bool, strict: bool) -> dict:
    text = doc.read_text(encoding="utf-8", errors="replace")
    fm, fm_raw, after = split_frontmatter(text)
    zone, body = split_metadata_zone(after)
    rel = str(doc.relative_to(root)) if doc.is_relative_to(root) else str(doc)
    failures, warnings = [], []

    method = str((fm or {}).get("conversion_method") or "")
    requires_block = True if not ai_authored_only else bool(AI_METHOD_RE.search(method))
    ok, detail = block_ok(zone)
    if requires_block and not ok:
        failures.append(f"BLOCK: {detail}")

    body_no_fences = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    if re.search(r"AI-CHANGELOG", body_no_fences, re.IGNORECASE):
        failures.append("PLACEMENT: AI-CHANGELOG marker appears in the rendered body (or inside a <details> block)")

    content_hits = vendor_hits(body) + vendor_hits(zone)
    if content_hits:
        failures.append("VENDOR: product/vendor name in content: " + ", ".join(sorted(set(content_hits))))
    fm_hits = vendor_hits(fm_raw)
    if fm_hits:
        (failures if strict else warnings).append(
            "VENDOR-FRONTMATTER: vendor name in tool-managed frontmatter: " + ", ".join(sorted(set(fm_hits))))

    return {"doc": rel, "status": "fail" if failures else ("warn" if warnings else "pass"),
            "block": ok, "block_detail": detail, "block_required": requires_block,
            "failures": failures, "warnings": warnings}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--root", default=".")
    ap.add_argument("--ai-authored-only", action="store_true",
                    help="require the block only where frontmatter conversion_method names an AI method")
    ap.add_argument("--strict", action="store_true", help="vendor names in frontmatter fail too")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    paths = [Path(p) if Path(p).is_absolute() else root / p for p in args.paths]
    for p in paths:
        if not p.exists():
            print(f"error: path not found: {p}", file=sys.stderr)
            return 2
    results = [check_document(d, root, args.ai_authored_only, args.strict) for d in iter_docs(paths)]
    counts = {"pass": 0, "warn": 0, "fail": 0}
    for r in results:
        counts[r["status"]] += 1
    report = {"root": str(root), "documents": len(results), "summary": counts, "results": results}
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"ai-changelog: {len(results)} document(s) — pass {counts['pass']}, warn {counts['warn']}, fail {counts['fail']}")
        for r in results:
            for f in r["failures"]:
                print(f"  [FAIL] {r['doc']} — {f}")
            for w in r["warnings"]:
                print(f"  [warn] {r['doc']} — {w}")
    return 1 if counts["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
