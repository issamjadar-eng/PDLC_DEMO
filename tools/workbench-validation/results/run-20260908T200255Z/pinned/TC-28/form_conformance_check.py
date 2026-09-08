#!/usr/bin/env python3
"""form_conformance_check.py — does a controlled document's structure match its
governing QMS form/template?

Deterministic checker behind the doctype-governance rule
(`rules/doctype-governance.md`): the QMS form is the *authoring contract* for a
mirrored regulated document, and its section skeleton is the part a script can
verify. Stdlib + PyYAML only.

How the governing form is resolved for a document (first hit wins):
  1. `--form <path>` — explicit form markdown (all documents checked against it).
  2. Nearest ancestor `.taxonomy.yml` — `mappings[<slug>].governing_qms.forms[]`
     where <slug> is the document's parent folder name (nested `<slug>/v*.md` /
     `<slug>/index.md` layout) or its file stem (flat layout). Form IDs resolve
     to files under the QMS registry (`docs/internal/source-md/**`) whose name
     starts with the ID — the same convention `render-sentinels.py` uses for
     the doc-governance banner.
  3. The document's own YAML frontmatter `references[]`: an entry whose `title`
     or `note` names a parent template/form (regex `parent .*(template|form)`,
     case-insensitive) — its `doc_id` resolves through the registry's `qms-index.md`
     table (`| Doc ID | Type | Title(link) | …`) or by ID-prefix filename match.
  If nothing resolves, the document is reported `no-form` (informational; it
  does not fail the run). A taxonomy mapping with `governing_qms.forms: []` +
  `note:` is the same intentional-null case.

Section-conformance rule (documented so reviewers can judge it):
  * The form's structure is its ordered sequence of LEVEL-2 headings (`## `),
    normalized (numbering prefixes, trailing punctuation, case and surrounding
    whitespace removed). Level-1 is the title; level-3+ is body detail the form
    does not prescribe.
  * MISSING   — a form section absent from the document        → failure
  * ORDER     — form sections present but in a different order  → failure
  * EXTRA     — a document section the form does not carry      → warning
    (a failure only with `--strict`: teams legitimately add sections such as
    Approvals; missing/reordered ones are what break document control)
  * Sections are matched on the normalized text; a `--alias A=B` pair lets a
    project declare accepted renames (e.g. "FMEA Table=Hazard Analysis Table").

Exit codes: 0 = no failures (warnings allowed) · 1 = at least one failure
· 2 = usage / precondition error. `--json` prints a machine-readable report.

Usage:
  form_conformance_check.py [--root <repo>] [--form <path>] [--strict]
                            [--alias A=B ...] [--json] <doc-or-folder> ...
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

REGISTRY_REL = Path("docs/internal/source-md")
QMS_INDEX_NAME = "qms-index.md"
PARENT_NOTE_RE = re.compile(r"parent\b.*\b(template|form)\b", re.IGNORECASE)
EXCLUDE_NAMES = {"README.md"}
EXCLUDE_DIRS = {"formal", "images", "_scratch", "_work", ".git", "node_modules"}


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def split_frontmatter(text: str):
    """(frontmatter_dict_or_None, body_text)."""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    raw = text[3:end]
    body = text[end + 4:]
    try:
        fm = yaml.safe_load(raw)
    except yaml.YAMLError:
        fm = None
    return (fm if isinstance(fm, dict) else None), body


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def strip_fences(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def normalize_heading(h: str) -> str:
    h = h.strip()
    h = re.sub(r"^(\d+(\.\d+)*|[A-Z])[.)]\s+", "", h)   # "3." / "3.1" / "A)" prefixes
    h = re.sub(r"[\s:.\-–—]+$", "", h)
    h = re.sub(r"\s+", " ", h)
    return h.lower()


def level2_sections(text: str) -> list[str]:
    """Ordered normalized `## ` headings of a markdown body (comments and fenced
    code removed first so a heading inside a metadata block or a code sample
    does not count)."""
    body = strip_fences(strip_html_comments(text))
    out = []
    for line in body.splitlines():
        m = re.match(r"^##\s+(?!#)(.+?)\s*$", line)
        if m:
            out.append(normalize_heading(m.group(1)))
    return out


# ---------------------------------------------------------------------------
# Governing-form resolution
# ---------------------------------------------------------------------------

def find_taxonomy(doc: Path, root: Path):
    cur = doc.resolve().parent
    root = root.resolve()
    while True:
        cand = cur / ".taxonomy.yml"
        if cand.is_file():
            return cand
        if cur == root or cur == cur.parent:
            return None
        cur = cur.parent


def registry_index(root: Path) -> dict:
    """{ID: path} — every registry markdown keyed by the first token of its
    filename (the `render-sentinels.py` doc-governance convention) plus every
    `| Doc ID | … | [Title](relative/link) |` row of qms-index.md."""
    reg = root / REGISTRY_REL
    idx: dict = {}
    if not reg.is_dir():
        return idx
    for f in sorted(reg.rglob("*.md")):
        idx.setdefault(f.name.split(" ")[0].split(".")[0], f)
    qi = reg / QMS_INDEX_NAME
    if qi.is_file():
        for line in qi.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^\|\s*([A-Z][A-Z0-9-]+)\s*\|[^|]*\|\s*\[[^\]]*\]\(([^)]+)\)", line)
            if m:
                target = (qi.parent / m.group(2)).resolve()
                if target.is_file():
                    idx[m.group(1)] = target
    return idx


def resolve_form(doc: Path, root: Path, idx: dict, taxonomy_cache: dict):
    """-> (form_path | None, how: str, detail: str)."""
    tax = find_taxonomy(doc, root)
    if tax is not None:
        if tax not in taxonomy_cache:
            try:
                taxonomy_cache[tax] = yaml.safe_load(tax.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                taxonomy_cache[tax] = {}
        mappings = (taxonomy_cache[tax] or {}).get("mappings") or {}
        slug = doc.parent.name if (re.match(r"^v\d", doc.stem) or doc.stem == "index") else doc.stem
        mapping = mappings.get(slug)
        if mapping is not None:
            gov = (mapping or {}).get("governing_qms")
            if not gov:
                return None, "taxonomy", f"slug `{slug}` has no governing_qms block (unverified mapping)"
            forms = gov.get("forms") or []
            if not forms:
                return None, "taxonomy", f"slug `{slug}`: forms: [] — {gov.get('note') or 'intentionally no form'}"
            fid = str(forms[0])
            path = idx.get(fid)
            if path is None:
                return None, "taxonomy", f"form `{fid}` declared for `{slug}` but no registry file found"
            return path, "taxonomy", f"{slug} → {fid}"
    fm, _ = split_frontmatter(doc.read_text(encoding="utf-8", errors="replace"))
    for ref in ((fm or {}).get("references") or []):
        if not isinstance(ref, dict):
            continue
        # The parent marker may sit in `note:` or `title:` (docflow writes
        # `title: "Parent QMS template"` and keeps the standards anchor in note).
        marker = f"{ref.get('title') or ''} {ref.get('note') or ''}"
        if PARENT_NOTE_RE.search(marker):
            fid = str(ref.get("doc_id") or "")
            path = idx.get(fid)
            if path is None:
                return None, "frontmatter", f"parent `{fid}` named but not found in the QMS registry"
            return path, "frontmatter", f"references[] → {fid}"
    return None, "none", "no governing form declared (no taxonomy mapping, no parent-template reference)"


# ---------------------------------------------------------------------------
# Conformance
# ---------------------------------------------------------------------------

def compare(form_sections: list[str], doc_sections: list[str], aliases: dict) -> dict:
    doc_norm = [aliases.get(s, s) for s in doc_sections]
    missing = [s for s in form_sections if s not in doc_norm]
    extra = [s for s in doc_norm if s not in form_sections]
    shared_form_order = [s for s in form_sections if s in doc_norm]
    shared_doc_order = [s for s in doc_norm if s in form_sections]
    order_ok = shared_form_order == shared_doc_order
    return {
        "missing": missing,
        "extra": extra,
        "order_ok": order_ok,
        "form_sections": form_sections,
        "doc_sections": doc_norm,
    }


def iter_docs(paths: list[Path]):
    for p in paths:
        if p.is_file():
            if p.suffix == ".md" and p.name not in EXCLUDE_NAMES:
                yield p
        elif p.is_dir():
            for f in sorted(p.rglob("*.md")):
                if f.name in EXCLUDE_NAMES or EXCLUDE_DIRS & set(f.relative_to(p).parts[:-1]):
                    continue
                yield f


def check_document(doc: Path, root: Path, idx: dict, cache: dict, aliases: dict,
                   strict: bool, explicit_form: Path | None) -> dict:
    text = doc.read_text(encoding="utf-8", errors="replace")
    fm, body = split_frontmatter(text)
    doc_type = str((fm or {}).get("doc_type") or "")
    rel = str(doc.relative_to(root)) if doc.is_relative_to(root) else str(doc)
    result = {"doc": rel, "status": None, "form": None, "resolved_via": None, "detail": None,
              "missing": [], "extra": [], "order_ok": True, "failures": 0, "warnings": 0}
    if doc_type.upper() in {"TMP", "FORM", "SOP", "WI", "STD"} and explicit_form is None:
        result.update(status="skipped", detail=f"doc_type {doc_type}: this is a QMS document, not an instance")
        return result
    if explicit_form is not None:
        form_path, how, detail = explicit_form, "explicit", str(explicit_form)
    else:
        form_path, how, detail = resolve_form(doc, root, idx, cache)
    result.update(resolved_via=how, detail=detail)
    if form_path is None:
        result["status"] = "no-form"
        return result
    result["form"] = str(form_path.relative_to(root)) if form_path.is_relative_to(root) else str(form_path)
    _, form_body = split_frontmatter(form_path.read_text(encoding="utf-8", errors="replace"))
    cmp = compare(level2_sections(form_body), level2_sections(body), aliases)
    result.update(missing=cmp["missing"], extra=cmp["extra"], order_ok=cmp["order_ok"],
                  form_sections=cmp["form_sections"], doc_sections=cmp["doc_sections"])
    failures = len(cmp["missing"]) + (0 if cmp["order_ok"] else 1)
    warnings = len(cmp["extra"])
    if strict:
        failures += warnings
        warnings = 0
    if not cmp["form_sections"]:
        result.update(status="no-form", detail=detail + " — form declares no level-2 sections")
        return result
    result.update(failures=failures, warnings=warnings,
                  status="fail" if failures else ("warn" if warnings else "pass"))
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="document files or folders (recursive)")
    ap.add_argument("--root", default=".", help="project root (default: cwd)")
    ap.add_argument("--form", default=None, help="explicit governing form markdown (overrides resolution)")
    ap.add_argument("--strict", action="store_true", help="extra sections are failures, not warnings")
    ap.add_argument("--alias", action="append", default=[], metavar="DOC=FORM",
                    help="accept a document heading as equivalent to a form heading")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    paths = [Path(p) if Path(p).is_absolute() else root / p for p in args.paths]
    for p in paths:
        if not p.exists():
            print(f"error: path not found: {p}", file=sys.stderr)
            return 2
    explicit = None
    if args.form:
        explicit = Path(args.form) if Path(args.form).is_absolute() else root / args.form
        if not explicit.is_file():
            print(f"error: form not found: {explicit}", file=sys.stderr)
            return 2
    aliases = {}
    for a in args.alias:
        if "=" not in a:
            print(f"error: --alias expects DOC=FORM, got {a!r}", file=sys.stderr)
            return 2
        d, f = a.split("=", 1)
        aliases[normalize_heading(d)] = normalize_heading(f)

    idx = registry_index(root)
    cache: dict = {}
    results = [check_document(d, root, idx, cache, aliases, args.strict, explicit) for d in iter_docs(paths)]
    counts = {"pass": 0, "warn": 0, "fail": 0, "no-form": 0, "skipped": 0}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    report = {"root": str(root), "rule": "level-2 headings: missing/order = failure, extra = warning (strict: failure)",
              "summary": counts, "documents": len(results), "results": results}
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"form-conformance: {len(results)} document(s) — "
              + ", ".join(f"{k} {v}" for k, v in counts.items() if v))
        for r in results:
            if r["status"] in ("fail", "warn"):
                bits = []
                if r["missing"]:
                    bits.append("missing: " + ", ".join(r["missing"]))
                if not r["order_ok"]:
                    bits.append("out of order")
                if r["extra"]:
                    bits.append("extra: " + ", ".join(r["extra"]))
                print(f"  [{r['status'].upper()}] {r['doc']}  (form {r['form']}) — " + "; ".join(bits))
            elif r["status"] == "no-form":
                print(f"  [no-form] {r['doc']} — {r['detail']}")
    return 1 if counts.get("fail") else 0


if __name__ == "__main__":
    sys.exit(main())
