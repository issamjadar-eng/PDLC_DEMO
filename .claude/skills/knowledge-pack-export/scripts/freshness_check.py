#!/usr/bin/env python3
"""
freshness_check.py — drift / staleness CANDIDATE-FINDER for knowledge-pack-export.

Contract: this is a high-recall, deterministic candidate-finder, NOT an adjudicator.
A pack is a verbatim snapshot of source docs; its biggest failure mode is ingesting a
doc whose prose has rotted relative to the project's source-of-truth wiring — e.g. a
doc asserting an obsolete classification for a module the project has since reclassified.

This tool finds every candidate and returns it WITH CONTEXT + SIGNAL HINTS. It never
suppresses. The CALLER (Claude, or an agent in a workflow) does the semantic final pass —
deciding whether a hit ASSERTS the wrong value (real drift) or merely MENTIONS it
(a definition, a changelog row, prose discussing the drift, another vendor's software).

Why this split: the engine is regex — it cannot read intent, and precision-filtering
would hide findings from the smart layer. So it optimizes recall + context, mirroring the
skill's hybrid build (deterministic finds; LLM judges). The tool is grep-with-grounding;
the caller is the judge.

PROJECT-AGNOSTIC: this engine hard-codes no project facts. The contradiction patterns,
module aliases, and hint markers all come from project.yml. See "Configuration" below.
READ-ONLY: reports, never edits.

Configuration (project.yml)
---------------------------
  knowledge_pack:
    freshness:
      module_aliases: [<Module A>, <Module B>]   # optional; supplements module names
                                                 # derived from dhfs[] architecture_name/marketed_name/leaf
      contradictions:                            # project-keyed contradiction patterns
        - id: <some-obsolete-value>
          regex: 'Obsolete Value'                # a regex matching the stale assertion
          oracle: "what project.yml now says is correct"
      hint_markers:                              # optional; tune the advisory hints
        changelog: [PROJECT-123, reconciled]     # extra substrings that flag likely_changelog
        predicate: [REF-001]                     # substrings that flag likely_predicate_cell

  Each `contradictions[].regex` is matched case-insensitively against every line; a match
  is a CANDIDATE (caller adjudicates). `oracle` is the human-readable "what's correct now"
  shown beside each hit. If `contradictions` is absent, the contradiction check prints a
  notice and skips (staleness + variants still run — they need no project facts).

Checks
------
  contradiction  per-project-config: each hit is a line matching a configured pattern,
                 returned with context + advisory signal hints.
  staleness      per-source git last-commit age + docflow frontmatter (status/lifecycle).
  variants       sibling near-name file clusters (confirm which is canonical).

Signal hints (NOT filters — advisory only, attached to each contradiction hit):
  likely_definition       line defines a class/scale (generic: "X: <definition>")
  likely_changelog        line records a fix (generic verbs + project changelog markers)
  likely_predicate_cell   line matches a configured predicate marker
  in_analysis_doc         path under */_analysis/ (often discusses drift as a finding)
  in_external_doc         path under docs/external/ (often another vendor / standard text)
  review_comment          line is a %% REVIEW authoring note
  in_table_row            line looks like a markdown table cell (assertions live in tables)
  module_named_nearby     a project module name (from config/dhfs) appears on the line

Scope
-----
  --pack <slug>   only the sources named in tools/knowledge-packs/<slug>/<slug>.pack.yml
  --repo          all markdown under docs/ + root *.md (default)

Output
------
  default          human-readable, grouped, every hit with context + hints
  --json           structured JSON for an agent/workflow caller
  --context N      lines of surrounding context per hit (default 2)

Usage
-----
  freshness_check.py [contradiction|staleness|variants|all] [--pack S|--repo] [--json] [--context N]
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML required (pip install pyyaml).")


def repo_root():
    try:
        out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"],
                                      stderr=subprocess.DEVNULL)
        return Path(out.decode().strip())
    except Exception:
        return Path.cwd()


ROOT = repo_root()
A = {"red": "\033[31m", "yel": "\033[33m", "grn": "\033[32m", "cyn": "\033[36m",
     "dim": "\033[2m", "0": "\033[0m"}


def c(s, k):
    return f"{A[k]}{s}{A['0']}" if sys.stdout.isatty() else str(s)


# ───────────────────────── project.yml: oracle + config ─────────────────────────

def load_project():
    p = ROOT / "project.yml"
    if not p.exists():
        return {}
    return yaml.safe_load(open(p)) or {}


def load_dhfs(proj):
    out = []
    for x in proj.get("dhfs", []) or []:
        cls = x.get("classification") or {}
        out.append({
            "leaf": x.get("leaf"), "role": x.get("role"),
            "arch": x.get("architecture_name"), "marketed": x.get("marketed_name"),
            "samd": cls.get("samd"), "class": cls.get("class"),
            "iec62304": cls.get("iec62304"),
        })
    return out


def load_freshness_cfg(proj):
    return ((proj.get("knowledge_pack") or {}).get("freshness")) or {}


def module_names(dhfs, cfg):
    """Module names to flag proximity on — derived from dhfs[] + optional config aliases.
    No hard-coded project names."""
    names = set()
    for d in dhfs:
        for k in ("arch", "marketed"):
            if d.get(k):
                names.add(d[k])
        if d.get("leaf"):
            # leaf is kebab; turn it into a spaced form for prose matching
            names.add(d["leaf"].replace("-", " "))
    for a in cfg.get("module_aliases") or []:
        names.add(a)
    return sorted(n for n in names if n and len(n) > 2)


def build_contra_patterns(cfg):
    """Compile the configured contradiction patterns. Returns [(id, compiled_rx, oracle)]."""
    out = []
    for item in cfg.get("contradictions") or []:
        rx = item.get("regex")
        if not rx:
            continue
        try:
            out.append((item.get("id", rx), re.compile(rx, re.I), item.get("oracle", "")))
        except re.error as e:
            sys.stderr.write(f"WARN: bad regex for contradiction '{item.get('id')}': {e}\n")
    return out


# ───────────────────────── corpus ─────────────────────────

def md_corpus(pack=None):
    if pack:
        manifest = ROOT / "tools" / "knowledge-packs" / pack / f"{pack}.pack.yml"
        if not manifest.exists():
            sys.exit(f"ERROR: no manifest at {manifest}")
        m = yaml.safe_load(open(manifest))
        files = []
        for slot in m.get("slots", []):
            for pat in slot.get("sources", []):
                files += [Path(p) for p in glob.glob(str(ROOT / pat), recursive=True)
                          if os.path.isfile(p)]
        return sorted(set(files))
    files = [Path(p) for p in glob.glob(str(ROOT / "*.md"))]
    files += [Path(p) for p in glob.glob(str(ROOT / "docs" / "**" / "*.md"), recursive=True)]
    return sorted(set(f for f in files if os.path.isfile(f)))


def git_age(path):
    try:
        out = subprocess.check_output(
            ["git", "-C", str(ROOT), "log", "-1", "--format=%cr", "--", str(path)],
            stderr=subprocess.DEVNULL)
        return out.decode().strip() or "uncommitted"
    except Exception:
        return "unknown"


# ───────────────────────── signal hints (advisory, never suppress) ─────────────────────────

# Generic, project-agnostic markers. Projects extend these via hint_markers in config.
GENERIC_CHANGELOG_MARKERS = ["changelog", "reconcil", "recharacter", "superseded",
                             "left unchanged", "resolved", "alignment note"]


def signal_hints(line, rel, module_names_list, hint_markers):
    low = line.lower()
    hints = []
    # definition: a "Term: <definition>" line, or one enumerating multiple class levels
    if re.search(r"\bclass\s*[a-z]\W{0,4}:?\s*\**\s*(no |non-|death|serious|injury)", low) or \
       (low.count("class ") >= 3 and ("injury" in low or "no injury" in low)):
        hints.append("likely_definition")
    changelog_markers = [m.lower() for m in (GENERIC_CHANGELOG_MARKERS +
                                             list(hint_markers.get("changelog") or []))]
    if re.search(r"\b\w\s*(→|->|to)\s*\w\b", low) and any(
            k in low for k in ("class", "→", "->")):
        # a "X → Y" transition phrasing often marks a changelog/fix row
        pass
    if any(m in low for m in changelog_markers):
        hints.append("likely_changelog")
    pred_markers = [m.lower() for m in (hint_markers.get("predicate") or [])]
    if "[verify against" in low or any(m in low for m in pred_markers):
        hints.append("likely_predicate_cell")
    if "/_analysis/" in rel:
        hints.append("in_analysis_doc")
    if rel.startswith("docs/external/") or "/external/" in rel:
        hints.append("in_external_doc")
    if "%% review" in low:
        hints.append("review_comment")
    if line.lstrip().startswith("|") and line.rstrip().endswith("|"):
        hints.append("in_table_row")
    if any(m.lower() in low for m in module_names_list):
        hints.append("module_named_nearby")
    return hints


# ───────────────────────── checks ─────────────────────────

def check_contradiction(files, patterns, mods, hint_markers, ctx):
    hits = []
    for f in files:
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        rel = os.path.relpath(f, ROOT)
        for i, ln in enumerate(lines):
            for term, rx, why in patterns:
                if rx.search(ln):
                    lo, hi = max(0, i - ctx), min(len(lines), i + ctx + 1)
                    hits.append({
                        "file": rel, "line": i + 1, "term": term,
                        "oracle": why, "match": ln.strip(),
                        "context": [{"n": j + 1, "t": lines[j]} for j in range(lo, hi)],
                        "hints": signal_hints(ln, rel, mods, hint_markers),
                    })
    return hits


def check_staleness(files):
    out = []
    for f in files:
        try:
            head = f.read_text(encoding="utf-8", errors="replace")[:2000]
        except Exception:
            continue
        rel = os.path.relpath(f, ROOT)
        flags = []
        for field in ("status", "lifecycle"):
            m = re.search(rf"^{field}:\s*[\"']?(\w+)", head, re.M)
            if m and m.group(1) == "draft":
                flags.append(f"{field}:draft")
        if flags:
            lm = re.search(r"^last_modified:\s*[\"']?([\d-]+)", head, re.M)
            out.append({"file": rel, "flags": flags,
                        "last_modified": lm.group(1) if lm else "?",
                        "git_age": git_age(f)})
    return out


def check_variants(files):
    groups = {}
    for f in files:
        key = re.sub(r"[-_ ]?(v?\d+(\.\d+)*|-?\d+)$", "", f.stem).strip("-_ ").lower()
        key = re.sub(r"\s*\(.*?\)\s*", "", key)
        groups.setdefault(key, []).append(os.path.relpath(f, ROOT))
    return {k: sorted(v) for k, v in groups.items() if len(v) > 1}


# ───────────────────────── render ─────────────────────────

def human(check, contra, stale, variants, have_patterns):
    if check in ("contradiction", "all"):
        print(c("\n■ contradiction candidates "
                "(ALL hits — caller adjudicates assertion vs mention)", "yel"))
        if not have_patterns:
            print(c("  · no `knowledge_pack.freshness.contradictions` patterns in project.yml "
                    "— contradiction scan skipped.", "dim"))
        elif not contra:
            print(c("  ✓ no candidates.", "grn"))
        else:
            print(c(f"  {len(contra)} candidate(s). Hints are ADVISORY — not a verdict.\n", "dim"))
            for h in contra:
                print(c(f"  {h['file']}:{h['line']}", "cyn") + f"  [{h['term']}]")
                print(c(f"     oracle: {h['oracle']}", "dim"))
                if h["hints"]:
                    print(c(f"     hints:  {', '.join(h['hints'])}", "dim"))
                for cl in h["context"]:
                    mark = c("›", "red") if cl["n"] == h["line"] else " "
                    print(c(f"     {mark} {cl['n']:>4} | {cl['t'][:150]}", "dim"))
                print()
    if check in ("staleness", "all"):
        print(c("\n■ source staleness (draft status / git age)", "yel"))
        if not stale:
            print(c("  ✓ none.", "grn"))
        for s in stale:
            print(f"  {s['file']}  [{', '.join(s['flags'])}]  "
                  f"last_modified={s['last_modified']}  last-commit={s['git_age']}")
    if check in ("variants", "all"):
        print(c("\n■ sibling-variant clusters (confirm canonical)", "yel"))
        if not variants:
            print(c("  ✓ none.", "grn"))
        for k, v in sorted(variants.items()):
            print(f"  concept {c(k, 'yel')}: {len(v)} files")
            for p in v:
                print(c(f"      {p}", "dim"))
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("check", nargs="?", default="all",
                    choices=["contradiction", "staleness", "variants", "all"])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--pack")
    g.add_argument("--repo", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--context", type=int, default=2)
    args = ap.parse_args()

    proj = load_project()
    dhfs = load_dhfs(proj)
    cfg = load_freshness_cfg(proj)
    patterns = build_contra_patterns(cfg)
    mods = module_names(dhfs, cfg)
    hint_markers = cfg.get("hint_markers") or {}

    files = md_corpus(pack=args.pack)
    contra = (check_contradiction(files, patterns, mods, hint_markers, args.context)
              if args.check in ("contradiction", "all") and patterns else [])
    stale = check_staleness(files) if args.check in ("staleness", "all") else []
    variants = check_variants(files) if args.check in ("variants", "all") else {}

    if args.json:
        print(json.dumps({
            "scope": f"pack:{args.pack}" if args.pack else "repo",
            "files_scanned": len(files),
            "contradiction_patterns_configured": len(patterns),
            "note": "Candidate-finder output. hints[] are ADVISORY signals, NOT a verdict. "
                    "Caller must read each hit's context to decide assertion vs mention. "
                    "Patterns + module aliases come from project.yml knowledge_pack.freshness.",
            "contradiction": contra, "staleness": stale, "variants": variants,
        }, indent=2, ensure_ascii=False))
    else:
        scope = f"pack:{args.pack}" if args.pack else "repo-wide (docs/ + root *.md)"
        print(c(f"freshness check (candidate-finder) — {scope} — {len(files)} file(s)", "yel"))
        print(c(f"  {len(patterns)} contradiction pattern(s) from project.yml; "
                f"{len(mods)} module name(s) for proximity hints", "dim"))
        human(args.check, contra, stale, variants, bool(patterns))
    sys.exit(0)


if __name__ == "__main__":
    main()
