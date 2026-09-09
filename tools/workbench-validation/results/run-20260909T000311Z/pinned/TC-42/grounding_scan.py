#!/usr/bin/env python3
"""grounding_scan.py — verify that advisor grounding and semantic search
stay on canonical sources.

Two checks:
  (a) agents — every `<!-- BEGIN GROUNDING ... -->` … `<!-- END GROUNDING -->`
      block in the given agent prompt files references only canonical paths:
      no path under a non-canonical pattern (audience explainers under
      `articles/**`, personal sandboxes `**/_work/**` / `**/_scratch/**`,
      machine data `**/_usage-metrics/**`, built knowledge packs
      `tools/knowledge-packs/**/pack/**`, docflow `**/formal/**` drafts).
  (b) index — the file-locator SQLite index (`indexed_files.path`) contains
      no row matching the project's `file_locator.corpus_excludes` globs
      (or the built-in non-canonical patterns when project.yml is absent).

Owner: the advisors skill — it owns the GROUNDING blocks; the index check
reuses the same "never a grounding source" rule that governs them.

Exit codes: 0 clean · 1 findings · 2 usage/precondition.
Usage: grounding_scan.py [--project-root DIR] [--agents GLOB ...]
                          [--index PATH | --no-index] [--json]
"""
from __future__ import annotations

import argparse
import fnmatch
import glob
import json
import re
import sqlite3
import sys
from pathlib import Path

NON_CANONICAL = [
    "articles/**", "**/articles/**",
    "**/_work/**", "**/_scratch/**", "**/_usage-metrics/**",
    "tools/knowledge-packs/**/pack/**", "**/formal/**",
]
BLOCK = re.compile(r"<!--\s*BEGIN GROUNDING.*?-->(.*?)<!--\s*END GROUNDING\s*-->", re.S)
# Path-like tokens: repo-relative paths with at least one slash, optionally in backticks/links.
PATHLIKE = re.compile(r"(?<![\w/.-])((?:\.claude|docs|tasks|tools|articles|assets)/[\w./*<>-]+)")


def _match(path: str, patterns) -> str | None:
    p = path.lstrip("./")
    for pat in patterns:
        if fnmatch.fnmatch(p, pat) or fnmatch.fnmatch("/" + p, pat) or fnmatch.fnmatch(p, pat.lstrip("*/")):
            return pat
        # `**/x/**` should also match a path that *starts* with x/
        core = pat.replace("**/", "").replace("/**", "")
        if core and ("/" + core + "/") in ("/" + p) or p.startswith(core + "/"):
            return pat
    return None


def scan_agents(files, patterns):
    findings, blocks = [], 0
    for f in files:
        text = Path(f).read_text(encoding="utf-8", errors="replace")
        for b in BLOCK.finditer(text):
            blocks += 1
            body = b.group(1)
            for tok in sorted(set(PATHLIKE.findall(body))):
                pat = _match(tok.rstrip(".,;:)`"), patterns)
                if pat:
                    line = text[:b.start(1) + body.find(tok)].count("\n") + 1
                    findings.append({"check": "agents", "file": str(f), "line": line,
                                     "path": tok, "pattern": pat,
                                     "why": "GROUNDING block references a non-canonical source"})
    return blocks, findings


def load_excludes(root: Path):
    pyml = root / "project.yml"
    if not pyml.is_file():
        return None
    text = pyml.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^\s*corpus_excludes:\s*$(.*?)(?=^\s{0,2}\S|\Z)", text, re.S | re.M)
    if not m:
        return None
    return [x.strip().strip('"').strip("'") for x in re.findall(r"^\s*-\s*([^\n#]+)", m.group(1), re.M)]


def scan_index(index_path: Path, patterns):
    if not index_path.is_file():
        return None, [{"check": "index", "why": f"index not found: {index_path}"}]
    con = sqlite3.connect(str(index_path))
    try:
        rows = [r[0] for r in con.execute("SELECT path FROM indexed_files")]
    finally:
        con.close()
    findings = []
    for p in rows:
        pat = _match(p, patterns)
        if pat:
            findings.append({"check": "index", "path": p, "pattern": pat,
                             "why": "indexed file matches a corpus_excludes pattern"})
    return len(rows), findings


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--agents", nargs="*", default=None, help="agent prompt files/globs (default .claude/agents/*.md)")
    ap.add_argument("--index", default=None, help="file-locator index path (default from project.yml file_locator.index_path)")
    ap.add_argument("--no-index", action="store_true", help="skip the index check")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.project_root).resolve()
    agent_globs = args.agents or [str(root / ".claude" / "agents" / "*.md")]
    files = sorted({f for g in agent_globs for f in glob.glob(g)})
    if not files:
        print("grounding_scan: no agent files found", file=sys.stderr)
        return 2
    excludes = load_excludes(root)
    patterns = sorted(set(NON_CANONICAL) | set(excludes or []))
    blocks, findings = scan_agents(files, patterns)
    report = {"agents_scanned": len(files), "grounding_blocks": blocks,
              "patterns": patterns, "index": None, "findings": findings}
    if not args.no_index:
        idx = Path(args.index) if args.index else None
        if idx is None:
            m = re.search(r"^\s*index_path:\s*([^\s#]+)", (root / "project.yml").read_text(encoding="utf-8", errors="replace")
                          if (root / "project.yml").is_file() else "", re.M)
            idx = root / (m.group(1) if m else "tools/file-locator-mcp/index.db")
        n, idx_findings = scan_index(idx, patterns)
        if n is None:
            print(f"grounding_scan: {idx_findings[0]['why']}", file=sys.stderr)
            return 2
        report["index"] = {"path": str(idx), "rows": n}
        findings += idx_findings
    report["findings"] = findings
    report["total_findings"] = len(findings)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"grounding_scan: {len(files)} agent(s), {blocks} GROUNDING block(s)"
              + (f", index rows {report['index']['rows']}" if report["index"] else "")
              + f" — {len(findings)} finding(s)")
        for x in findings:
            print(f"  [{x['check']}] {x.get('file', x.get('path'))}: {x.get('path', '')} ({x.get('pattern', '')})")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
