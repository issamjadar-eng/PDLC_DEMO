#!/usr/bin/env python3
"""qms_coverage.py — which imported QMS templates/forms have validation evidence,
which are imported but unused, and which project doctypes have no template at all.

A deployment acquires QMS documents over time. This inventory joins the imported
registry (`docs/internal/source-md/qms-index.md` + each registry document's
frontmatter `doc_type`) with the form-conformance results over the project's
controlled trees, so a validation report can state — from the record, not from
memory — for every template/form:

  instances   how many project documents declare it as their parent
  tested      the conformance check exercised ≥ 1 of those documents
  pass/fail   how those documents fared
  status      covered | covered-failing | unused   (unused = imported, no instance)

…and, for the project side, every document with NO structural template:
`documents_without_template` with a folder-derived doctype hint and a reason —
`no template imported` (nothing in the registry resembles the doctype),
`no reference (template <ID> exists)` (a plausible template is imported but the
document does not declare it), or `intentionally none` (taxonomy `forms: []`).
Documents governed by a procedure (SOP/WI) are listed under `procedures`.

Exit codes: 0 = inventory written and every instantiated template is tested
· 1 = an instantiated template has no conformance evidence · 2 = precondition
(no registry / bad paths). Stdlib + PyYAML.

Usage:
  qms_coverage.py --root <repo> --json-out <path> [--conformance-json <path>] [<doc-or-folder> ...]
  (default document root: docs/project/dhfs — or the paths given; when no
   --conformance-json is supplied the form-conformance checker is run in-process)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("form_conformance_check", _HERE / "form_conformance_check.py")
fcc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fcc)

STRUCTURAL = {"TMP", "FORM", "TEMPLATE"}
PROCEDURAL = {"SOP", "WI", "STD", "MAN", "POL", "QSD", "INDEX"}
INDEX_ROW = re.compile(r"^\|\s*([A-Z][A-Z0-9-]+)\s*\|\s*([^|]*?)\s*\|\s*\[([^\]]*)\]\(([^)]+)\)")


def tokens(text: str) -> set[str]:
    out = set()
    for t in re.split(r"[^a-z0-9]+", text.lower()):
        if len(t) > 2:
            out.add(t[:-1] if t.endswith("s") else t)
    return out


def load_registry(root: Path) -> tuple[list[dict], list[dict]]:
    """(templates, procedures) from qms-index rows + frontmatter doc_type."""
    reg = root / fcc.REGISTRY_REL
    qi = reg / fcc.QMS_INDEX_NAME
    if not qi.is_file():
        return [], []
    templates, procedures, seen = [], [], set()
    for line in qi.read_text(encoding="utf-8", errors="replace").splitlines():
        m = INDEX_ROW.match(line)
        if not m:
            continue
        did, idx_type, title, link = m.group(1), m.group(2), m.group(3), m.group(4)
        target = (qi.parent / link.split("#")[0].replace("%20", " ")).resolve()
        if did in seen:
            continue
        seen.add(did)
        doc_type = ""
        if target.is_file():
            fm, _ = fcc.split_frontmatter(target.read_text(encoding="utf-8", errors="replace"))
            doc_type = str((fm or {}).get("doc_type") or "").upper()
        if not doc_type:
            doc_type = {"template": "TMP", "form": "FORM", "sop": "SOP", "wi": "WI"}.get(idx_type.strip().lower(), idx_type.strip().upper())
        rel = str(target.relative_to(root)) if target.is_file() and target.is_relative_to(root) else link
        entry = {"id": did, "title": title.strip(), "path": rel, "doc_type": doc_type}
        if doc_type in STRUCTURAL:
            templates.append(entry)
        elif doc_type in PROCEDURAL or doc_type:
            procedures.append(entry)
    return templates, procedures


def doctype_hint(doc: str, result: dict, root: Path) -> str:
    fm, _ = fcc.split_frontmatter((root / doc).read_text(encoding="utf-8", errors="replace")) if (root / doc).is_file() else (None, "")
    dt = str((fm or {}).get("doc_type") or "")
    if dt and dt.upper() not in {"QSD", ""}:
        return dt
    parent = Path(doc).parent.name
    stem = re.sub(r"[-_ ]?\d+$", "", Path(doc).stem)
    return parent if parent not in {"docs", "project"} else stem


def build(root: Path, conformance: dict) -> dict:
    templates, procedures = load_registry(root)
    by_id = {t["id"]: t for t in templates}
    for t in templates:
        t.update(instances=0, tested=False, pass_=0, fail=0)
    proc_refs: dict[str, int] = {}
    without = []
    for r in conformance.get("results", []):
        st = r.get("status")
        tid = r.get("template_id")
        if st in ("pass", "warn", "fail") and tid in by_id:
            t = by_id[tid]
            t["instances"] += 1
            t["tested"] = True
            if st == "fail":
                t["fail"] += 1
            else:
                t["pass_"] += 1
        elif st == "procedure":
            proc_refs[tid] = proc_refs.get(tid, 0) + 1
        elif st == "no-form":
            hint = doctype_hint(r["doc"], r, root)
            detail = str(r.get("detail") or "")
            if "intentionally" in detail or "forms: []" in detail:
                reason = "intentionally none (taxonomy)"
            elif "not found in the QMS registry" in detail:
                reason = f"reference to {r.get('template_id')} not in registry"
            else:
                ht = tokens(hint)
                cand = [t for t in templates if ht and ht <= tokens(t["title"] + " " + Path(t["path"]).stem)]
                reason = (f"no reference (template {cand[0]['id']} exists)" if cand else "no template imported")
            without.append({"doc": r["doc"], "doctype_hint": hint, "reason": reason})
        elif st in ("pass", "warn", "fail") and tid and tid not in by_id:
            # template resolved by filename but not listed in the index — still count it
            templates.append({"id": tid, "title": Path(r.get("form", "")).stem, "path": r.get("form"), "doc_type": "TMP",
                              "instances": 1, "tested": True, "pass_": 0 if st == "fail" else 1, "fail": 1 if st == "fail" else 0})
            by_id[tid] = templates[-1]
    for t in templates:
        t["status"] = "unused" if t["instances"] == 0 else ("covered-failing" if t["fail"] else "covered")
    for p in procedures:
        p["referenced_by"] = proc_refs.get(p["id"], 0)
    out_templates = [{"id": t["id"], "title": t["title"], "path": t["path"], "doc_type": t["doc_type"],
                      "instances": t["instances"], "tested": t["tested"], "pass": t["pass_"], "fail": t["fail"],
                      "status": t["status"]} for t in sorted(templates, key=lambda x: x["id"])]
    docs_total = sum(1 for r in conformance.get("results", []) if r.get("status") != "skipped")
    governed = sum(1 for r in conformance.get("results", []) if r.get("status") in ("pass", "warn", "fail"))
    summary = {
        "templates_total": len(out_templates),
        "templates_instantiated": sum(1 for t in out_templates if t["instances"]),
        "templates_tested": sum(1 for t in out_templates if t["tested"]),
        "templates_unused": sum(1 for t in out_templates if t["status"] == "unused"),
        "templates_failing": sum(1 for t in out_templates if t["status"] == "covered-failing"),
        "procedures_total": len(procedures),
        "documents_total": docs_total,
        "documents_governed": governed,
        "documents_governed_by_procedure": sum(proc_refs.values()),
        "documents_without_template": len(without),
    }
    return {"generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "registry": str(fcc.REGISTRY_REL / fcc.QMS_INDEX_NAME),
            "templates": out_templates, "procedures": sorted(procedures, key=lambda p: p["id"]),
            "documents_without_template": sorted(without, key=lambda d: d["doc"]), "summary": summary}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="document files/folders (default: docs/project/dhfs)")
    ap.add_argument("--root", default=".")
    ap.add_argument("--json-out", required=True, help="where to write the inventory JSON")
    ap.add_argument("--conformance-json", default=None, help="reuse a form_conformance_check --json report instead of running it")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    if not (root / fcc.REGISTRY_REL / fcc.QMS_INDEX_NAME).is_file():
        print(f"error: no QMS registry index at {fcc.REGISTRY_REL / fcc.QMS_INDEX_NAME}", file=sys.stderr)
        return 2
    if args.conformance_json:
        cj = Path(args.conformance_json)
        cj = cj if cj.is_absolute() else root / cj
        if not cj.is_file():
            print(f"error: conformance report not found: {cj}", file=sys.stderr)
            return 2
        conformance = json.loads(cj.read_text(encoding="utf-8"))
    else:
        paths = [root / p if not Path(p).is_absolute() else Path(p) for p in (args.paths or ["docs/project/dhfs"])]
        for p in paths:
            if not p.exists():
                print(f"error: path not found: {p}", file=sys.stderr)
                return 2
        idx = fcc.registry_index(root)
        cache: dict = {}
        results = [fcc.check_document(d, root, idx, cache, {}, False, None) for d in fcc.iter_docs(paths)]
        conformance = {"results": results}
    inv = build(root, conformance)
    out = Path(args.json_out)
    out = out if out.is_absolute() else root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")
    s = inv["summary"]
    print(f"qms-coverage: {s['templates_total']} templates/forms imported — {s['templates_instantiated']} instantiated, "
          f"{s['templates_tested']} tested, {s['templates_failing']} failing, {s['templates_unused']} unused; "
          f"{s['procedures_total']} procedures ({s['documents_governed_by_procedure']} documents governed by procedure); "
          f"{s['documents_total']} documents — {s['documents_governed']} template-governed, "
          f"{s['documents_without_template']} without template")
    print(f"{'ID':<16} {'Type':<5} {'Inst':>4} {'Tested':>6} {'Pass':>4} {'Fail':>4}  Status            Title")
    for t in inv["templates"]:
        print(f"{t['id']:<16} {t['doc_type']:<5} {t['instances']:>4} {str(t['tested']):>6} {t['pass']:>4} {t['fail']:>4}  {t['status']:<17} {t['title']}")
    if inv["documents_without_template"]:
        print("documents without a structural template:")
        by_reason: dict = {}
        for d in inv["documents_without_template"]:
            by_reason.setdefault((d["doctype_hint"], d["reason"]), []).append(d["doc"])
        for (hint, reason), docs in sorted(by_reason.items()):
            print(f"  {hint:<28} {len(docs):>3}  {reason}")
    print(f"written: {out.relative_to(root) if out.is_relative_to(root) else out}")
    untested = [t for t in inv["templates"] if t["instances"] and not t["tested"]]
    return 1 if untested else 0


if __name__ == "__main__":
    sys.exit(main())
