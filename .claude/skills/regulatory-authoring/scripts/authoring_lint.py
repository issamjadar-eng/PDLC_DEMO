#!/usr/bin/env python3
"""
authoring_lint.py — regulatory-authoring lint.

Single-sourced from references/lint-signals.yml (the standard's Lint: lines derive from
the same file). Reads project.yml for project-parameterized tokens so NO names are
hard-coded here — this script is project-agnostic and ships to the registry.

Usage:
    authoring_lint.py <file.md> [--jurisdiction fda|eu|all] [--signals <path>] [--project <path>]

Zones (per the three-tier model, D2):
    metadata  = inside <!-- ... --> HTML comments         (never linted; not rendered)
    internal  = inside a 🔒 INTERNAL <details> container   (rendered but not filed)
    filed     = everything else                            (the regulator-facing body)

A signal with zone=filed is evaluated only on filed lines; zone=any on filed+internal.
Lint kinds: regex / regex_partial run; filesystem resolves links; dependency_gated and
judgment are listed as flag-only (an agent runs judgment, not this script).

Exit code: 0 if no `error`-severity findings, 1 otherwise (so it can gate).
"""
import argparse
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("error: PyYAML required (pip install pyyaml)\n")
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SIGNALS = os.path.join(HERE, "..", "references", "lint-signals.yml")


def find_project_yml(start):
    d = os.path.abspath(start)
    for _ in range(12):
        cand = os.path.join(d, "project.yml")
        if os.path.isfile(cand):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


def project_params(project_path):
    """Resolve {{...}} tokens from project.yml. Missing → None (signal skipped)."""
    params = {"task_folders": None, "jira_keys": None,
              "confirm_token": None, "retired_tree": None}
    if not project_path or not os.path.isfile(project_path):
        return params
    try:
        with open(project_path) as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return params
    folders = [m.get("task_folder") for m in
               (data.get("team", {}) or {}).get("active", []) or []
               if m.get("task_folder")]
    if folders:
        params["task_folders"] = "(" + "|".join(re.escape(x) for x in folders) + ")"
    jira = ((data.get("change_control", {}) or {}).get("jira", {}) or {})
    keys = jira.get("project_keys") or []
    if keys:
        params["jira_keys"] = "(" + "|".join(re.escape(x) for x in keys) + ")"
    ra = data.get("regulatory_authoring", {}) or {}
    if ra.get("confirm_token"):
        params["confirm_token"] = re.escape(ra["confirm_token"])
    if ra.get("retired_tree"):
        params["retired_tree"] = re.escape(ra["retired_tree"])
    return params


def substitute(pattern, params):
    """Fill {{tokens}}. Returns (pattern, missing_token_or_None)."""
    for tok, val in params.items():
        ph = "{{" + tok + "}}"
        if ph in pattern:
            if not val:
                return pattern, tok
            pattern = pattern.replace(ph, val)
    return pattern, None


def zone_flags(lines):
    """Per-line (is_metadata, is_internal)."""
    meta = [False] * len(lines)
    internal = [False] * len(lines)
    in_comment = False
    in_internal = False
    for i, ln in enumerate(lines):
        # HTML comment tracking (single- or multi-line)
        if in_comment:
            meta[i] = True
            if "-->" in ln:
                in_comment = False
            continue
        if "<!--" in ln and "-->" not in ln:
            meta[i] = True
            in_comment = True
            continue
        if "<!--" in ln and "-->" in ln:
            meta[i] = True
            continue
        # 🔒 INTERNAL container tracking
        if not in_internal and re.search(r"<summary>\s*🔒 INTERNAL", ln):
            in_internal = True
            internal[i] = True
            continue
        if in_internal:
            internal[i] = True
            if "🔒 END INTERNAL" in ln or "</details>" in ln:
                in_internal = False
            continue
    return meta, internal


def check_links(path, lines, meta, internal):
    """Filesystem: relative markdown link targets that don't resolve."""
    findings = []
    base = os.path.dirname(os.path.abspath(path))
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for i, ln in enumerate(lines):
        if meta[i]:
            continue
        for m in link_re.finditer(ln):
            target = m.group(1).split("#")[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if not os.path.exists(os.path.join(base, target)):
                findings.append((i + 1, target))
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--jurisdiction", default="all", choices=["fda", "eu", "all"])
    ap.add_argument("--signals", default=DEFAULT_SIGNALS)
    ap.add_argument("--project", default=None)
    args = ap.parse_args()

    if not os.path.isfile(args.file):
        sys.stderr.write(f"error: file not found: {args.file}\n")
        sys.exit(2)
    with open(args.signals) as f:
        spec = yaml.safe_load(f)
    signals = spec.get("signals", [])

    project_path = args.project or find_project_yml(args.file)
    params = project_params(project_path)

    with open(args.file) as f:
        text = f.read()
    lines = text.splitlines()
    meta, internal = zone_flags(lines)

    def line_in_zone(i, zone):
        if meta[i]:
            return False
        if zone == "filed":
            return not internal[i]
        return True  # zone == any: filed + internal

    runnable = {"regex", "regex_partial"}
    findings = []          # (severity, id, rule, kind, line, snippet, message)
    flagged = []           # dependency_gated / judgment / skipped
    error_count = 0

    for sig in signals:
        jur = sig.get("jurisdiction", "portable")
        if args.jurisdiction != "all" and jur not in ("portable", args.jurisdiction):
            continue
        kind = sig.get("kind")
        if kind in ("dependency_gated", "judgment"):
            flagged.append((sig["id"], sig["rule"], kind, sig.get("message", "")))
            continue
        if kind == "filesystem":
            for (lineno, target) in check_links(args.file, lines, meta, internal):
                sev = sig.get("severity", "warn")
                findings.append((sev, sig["id"], sig["rule"], kind, lineno,
                                 target, sig.get("message", "")))
                if sev == "error":
                    error_count += 1
            continue
        if kind in runnable:
            pat, missing = substitute(sig.get("pattern", ""), params)
            if missing:
                flagged.append((sig["id"], sig["rule"], "skipped",
                                f"project param {{{{{missing}}}}} not configured — signal skipped"))
                continue
            try:
                flags = 0 if sig.get("case_sensitive") else re.IGNORECASE
                rx = re.compile(pat, flags)
            except re.error as e:
                flagged.append((sig["id"], sig["rule"], "bad-regex", str(e)))
                continue
            zone = sig.get("zone", "filed")
            for i, ln in enumerate(lines):
                if not line_in_zone(i, zone):
                    continue
                if rx.search(ln):
                    sev = sig.get("severity", "warn")
                    snippet = ln.strip()[:120]
                    findings.append((sev, sig["id"], sig["rule"], kind, i + 1,
                                     snippet, sig.get("message", "")))
                    if sev == "error":
                        error_count += 1

    # ---- report ----
    sev_rank = {"error": 0, "warn": 1, "info": 2}
    findings.sort(key=lambda x: (sev_rank.get(x[0], 3), x[4]))
    print(f"# regulatory-authoring lint — {args.file}")
    print(f"  jurisdiction={args.jurisdiction}  project.yml={'found' if project_path else 'NOT FOUND'}")
    print(f"  {len(lines)} lines  ·  {sum(meta)} metadata  ·  {sum(internal)} internal\n")

    if findings:
        print("## Runnable findings (regex / regex_partial / filesystem)")
        for sev, sid, rule, kind, lineno, snip, msg in findings:
            tag = "CANDIDATE" if kind == "regex_partial" else sev.upper()
            print(f"  [{tag}] L{lineno} {rule} ({sid}): {snip}")
            print(f"      → {msg}")
    else:
        print("## Runnable findings: none")

    print("\n## Flag-only (run by an agent / needs data — NOT auto-checked here)")
    for sid, rule, kind, msg in flagged:
        print(f"  [{kind}] {rule} ({sid}): {msg}")

    print(f"\n## Summary: {len(findings)} runnable finding(s), {error_count} error(s); "
          f"{len(flagged)} flag-only. A clean lint is necessary, not sufficient — "
          f"run the copy-edit + QA-conformance stages.")
    sys.exit(1 if error_count else 0)


if __name__ == "__main__":
    main()
