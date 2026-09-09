#!/usr/bin/env python3
"""ai_changelog_backfill.py — give AI-assisted controlled documents the
provenance block the ai-changelog rule requires, and neutralise vendor names.

Companion to `ai_changelog_check.py` (same zone parsing, imported from the
sibling script). For every document the checker reports as needing a block
(`--ai-authored-only`: frontmatter `conversion_method` names an AI method):

  * an `<!-- AI-CHANGELOG … -->` block is inserted at the END of the leading
    metadata zone — after the YAML frontmatter and any existing HTML-comment
    blocks (the human version changelog), before the first rendered line — with
    exactly one row (`--date`, `--task`, `--summary`; vendor-neutral by default);
  * with `--fix-vendor`, AI product / vendor names in the rendered body are
    replaced by "AI assistant" (the only sanctioned label). Frontmatter is
    tool-managed conversion metadata and is left untouched.

Nothing else in the document changes. Default is a dry run; `--apply` writes.

Exit codes: 0 = nothing to do or applied · 1 = dry run found documents to fix
· 2 = usage / precondition error.

Usage:
  ai_changelog_backfill.py [--root <repo>] [--apply] [--fix-vendor] [--date YYYY-MM-DD]
                           [--task <id>] [--summary <text>] [--json] <doc-or-folder> ...
"""
from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ai_changelog_check", _HERE / "ai_changelog_check.py")
acc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(acc)

DEFAULT_SUMMARY = ("Provenance block added retroactively; document originally AI-assisted "
                   "(frontmatter conversion_method)")
BLOCK = """<!-- AI-CHANGELOG — internal provenance of AI-assisted edits. Metadata only:
     NOT published downstream (Confluence/Doc-Control), NOT part of the controlled
     record, stripped on DOCX/PDF export. Vendor-neutral by convention.
| Date       | Task    | Summary |
|------------|---------|---------|
| {date} | {task} | {summary} |
-->
"""


def make_block(date: str, task: str, summary: str) -> str:
    return BLOCK.format(date=date, task=task.ljust(7), summary=summary.replace("|", "/"))


def insert_block(text: str, block: str) -> str:
    fm, fm_raw, after = acc.split_frontmatter(text)
    head = text[: len(text) - len(after)]
    zone, body = acc.split_metadata_zone(after)
    zone_stripped = zone.rstrip("\n")
    if zone_stripped:
        new_zone = zone_stripped + "\n" + block
    else:
        new_zone = ("\n" if head and not head.endswith("\n") else "") + block
    if not body.startswith("\n"):
        new_zone += "\n"
    return head + new_zone + body


def neutralise_vendor(body: str) -> tuple[str, list[tuple[str, str]]]:
    changed = []
    out_lines = []
    for line in body.split("\n"):
        new = acc.VENDOR_RE.sub("AI assistant", line)
        if new != line:
            changed.append((line, new))
        out_lines.append(new)
    return "\n".join(out_lines), changed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--root", default=".")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--fix-vendor", action="store_true", help="replace product/vendor names in the body with 'AI assistant'")
    ap.add_argument("--all", action="store_true", help="require the block on every document, not only AI-authored ones")
    ap.add_argument("--date", default=_dt.date.today().isoformat())
    ap.add_argument("--task", default="—")
    ap.add_argument("--summary", default=DEFAULT_SUMMARY)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    paths = [Path(p) if Path(p).is_absolute() else root / p for p in args.paths]
    for p in paths:
        if not p.exists():
            print(f"error: path not found: {p}", file=sys.stderr)
            return 2
    block = make_block(args.date, args.task, args.summary)
    plans, applied = [], 0
    for doc in acc.iter_docs(paths):
        res = acc.check_document(doc, root, not args.all, False)
        needs_block = res["block_required"] and not res["block"]
        vendor = any(f.startswith("VENDOR:") for f in res["failures"])
        if not needs_block and not (vendor and args.fix_vendor):
            continue
        text = doc.read_text(encoding="utf-8", errors="replace")
        new = text
        changes = []
        if vendor and args.fix_vendor:
            fm, fm_raw, after = acc.split_frontmatter(new)
            head = new[: len(new) - len(after)]
            zone, body = acc.split_metadata_zone(after)
            body2, changes = neutralise_vendor(body)
            zone2, zchanges = neutralise_vendor(zone)
            changes += zchanges
            new = head + zone2 + body2
        if needs_block:
            new = insert_block(new, block)
        plan = {"doc": res["doc"], "block_added": needs_block, "vendor_lines_fixed": len(changes),
                "vendor_changes": [{"before": b, "after": a} for b, a in changes]}
        plans.append(plan)
        if args.apply:
            doc.write_text(new, encoding="utf-8")
            applied += 1
    summary = {"documents_to_fix": len(plans), "applied": applied if args.apply else 0,
               "blocks_added": sum(1 for p in plans if p["block_added"]),
               "vendor_lines_fixed": sum(p["vendor_lines_fixed"] for p in plans)}
    if args.json:
        print(json.dumps({"root": str(root), "apply": args.apply, "summary": summary, "plans": plans}, indent=2))
    else:
        mode = "APPLIED" if args.apply else "DRY RUN"
        print(f"ai-changelog-backfill [{mode}]: {len(plans)} document(s) — blocks {summary['blocks_added']}, "
              f"vendor lines {summary['vendor_lines_fixed']}")
        for p in plans:
            if p["vendor_changes"]:
                for c in p["vendor_changes"]:
                    print(f"  {p['doc']}\n    - {c['before'][:150]}\n    + {c['after'][:150]}")
    return 0 if args.apply or not plans else 1


if __name__ == "__main__":
    sys.exit(main())
