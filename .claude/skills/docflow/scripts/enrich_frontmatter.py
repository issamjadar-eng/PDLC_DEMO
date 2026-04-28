#!/usr/bin/env python3
"""
enrich_frontmatter.py — Produce the v30-parity frontmatter dict for a staged adopt.

Ports `agents/adopter.md` Phase 5a (template inference), 5b (SOP/WI scan),
5c (filing composition), 5d (version lineage seeding), plus references
resolution and deterministic counts to Python. v29's adopter agent walked
these tool-call-by-tool-call; this script does them all once.

Reads from the staging dir (manifest.json, all.txt, body.md, dispatch.json)
and from project-level indexes (project.yml, source-md/Forms/SOPs/WIs,
composition manifests). Emits a dict suitable for YAML-dump into the final MD's
frontmatter.

Entry point for tests + orchestrator:
  enrich(staging_dir, repo_root) -> dict
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path


# ---------- helpers ----------

_STOPWORDS = {"plan", "form", "template", "procedure", "for", "and", "the", "of", "a"}


def _tokenize(s: str) -> set[str]:
    return {t for t in re.split(r"[^A-Za-z0-9]+", s.lower()) if t and t not in _STOPWORDS}


def _token_similarity(a: str, b: str) -> float:
    """Jaccard-like similarity after stop-wording + tokenizing."""
    ta, tb = _tokenize(a), _tokenize(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _title_fuzzy(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _read_md_frontmatter(path: Path) -> tuple[dict, str]:
    """Minimal YAML frontmatter read (title/doc_id only — that's all we need)."""
    if not path.exists():
        return {}, ""
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not m:
        return {}, text
    fm_text, body = m.group(1), m.group(2)
    fm: dict = {}
    for line in fm_text.splitlines():
        mm = re.match(r'^([A-Za-z_][\w]*)\s*:\s*"?([^"\n]*?)"?\s*$', line)
        if mm:
            fm[mm.group(1)] = mm.group(2).strip()
    return fm, body


def _body_headings(body: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^#{1,3}\s+(.+?)\s*$", body, re.MULTILINE)]


# ---------- 5d: version_lineage seeding ----------

def seed_version_lineage(dispatch: dict, today: str) -> list[dict]:
    stem = dispatch["title_stem"]
    ext = Path(dispatch["source_pdf"]).suffix.lstrip(".")
    return [
        {
            "doc_version": dispatch["doc_version"],
            "doc_version_raw": dispatch.get("doc_version_raw") or f'v.{dispatch["doc_version"][1:]}',
            "lifecycle": "formal",
            "format": ext,
            "path": f"formal/{stem}.{ext}",
            "event": "original",
            "date": today,
        },
        {
            "doc_version": dispatch["doc_version"],
            "doc_version_raw": dispatch.get("doc_version_raw") or f'v.{dispatch["doc_version"][1:]}',
            "lifecycle": "draft",
            "format": "md",
            "path": f"{stem}.md",
            "event": "adopt",
            "date": today,
        },
    ]


# ---------- 5a: template_of / template_hints (Forms fuzzy match) ----------

def infer_template(title: str, forms_dir: Path) -> tuple[dict, list[dict]]:
    """
    Scan every .md in forms_dir; pick the best match by title-exact / title-
    fuzzy. Returns (template_of, template_hints[]).
    """
    if not forms_dir.exists():
        return {
            "doc_id": None, "title": None, "template_version": None,
            "inferred": True, "confidence": None, "match_basis": None,
        }, []

    scores: list[tuple[float, str, str, str]] = []
    for md in forms_dir.glob("*.md"):
        fm, _body = _read_md_frontmatter(md)
        cand_title = fm.get("title", "")
        cand_id = fm.get("doc_id", "")
        if not cand_title:
            continue
        # Title-exact (token-set match after stopwords)
        if _tokenize(title) == _tokenize(cand_title) and _tokenize(title):
            return ({
                "doc_id": cand_id or None, "title": cand_title,
                "template_version": None, "inferred": True,
                "confidence": "high", "match_basis": "title-exact",
            }, [])
        # Score by token-set similarity + fuzzy ratio
        score = max(_token_similarity(title, cand_title), _title_fuzzy(title, cand_title))
        if score >= 0.4:
            scores.append((score, cand_id, cand_title, "title-fuzzy"))

    scores.sort(reverse=True)
    if not scores:
        return ({
            "doc_id": None, "title": None, "template_version": None,
            "inferred": True, "confidence": None, "match_basis": None,
        }, [])

    best = scores[0]
    confidence = "medium" if best[0] >= 0.7 else "low"
    template_of = {
        "doc_id": best[1] or None, "title": best[2],
        "template_version": None, "inferred": True,
        "confidence": confidence, "match_basis": best[3],
    }
    hints = [
        {"doc_id": s[1] or None, "title": s[2], "score": round(s[0], 2), "basis": s[3]}
        for s in scores[1:4]
    ]
    return template_of, hints


# ---------- 5b: authored_per (SOP/WI scan) ----------

_SOPWI_RE = re.compile(r"\b(SOP|WI)-(\d+)\b")
_HIGH_CONFIDENCE_HEADINGS = re.compile(
    r"governing procedures|applicable sops|applicable work instructions|standards|references|revision history",
    re.IGNORECASE,
)


def scan_authored_per(cache_text: str, sops_dir: Path, wis_dir: Path) -> tuple[list[dict], list[dict]]:
    matches: dict[str, str] = {}  # doc_id -> context
    for m in _SOPWI_RE.finditer(cache_text):
        doc_id = f"{m.group(1)}-{m.group(2)}"
        start = max(0, m.start() - 200)
        end = min(len(cache_text), m.end() + 200)
        if doc_id not in matches:
            matches[doc_id] = cache_text[start:end]

    authored_per: list[dict] = []
    hints: list[dict] = []
    for doc_id, context in matches.items():
        kind = "SOP" if doc_id.startswith("SOP") else "WI"
        source_dir = sops_dir if kind == "SOP" else wis_dir

        title = None
        note = None
        resolved = False
        if source_dir.exists():
            for md in source_dir.glob("*.md"):
                fm, _ = _read_md_frontmatter(md)
                if fm.get("doc_id") == doc_id:
                    title = fm.get("title")
                    resolved = True
                    break
        if not resolved:
            note = "not in source-md — reference only"

        high_conf = bool(_HIGH_CONFIDENCE_HEADINGS.search(context))
        entry = {
            "doc_id": doc_id, "doc_type": kind, "title": title,
            "inferred": True, "confidence": "high" if high_conf else "medium",
        }
        if note:
            entry["note"] = note
        if high_conf:
            authored_per.append(entry)
        else:
            hints.append(entry)
    return authored_per, hints


# ---------- 5c: filings (composition manifest scan) ----------

def scan_filings(title_stem: str, manifest_paths: list[Path]) -> list[str]:
    filings: list[str] = []
    for mp in manifest_paths:
        if not mp.exists():
            continue
        text = mp.read_text(encoding="utf-8", errors="ignore")
        # Grep for either the .md filename or the formal/<stem>.ext pattern
        if (f"{title_stem}.md" in text or f"formal/{title_stem}" in text):
            slug = mp.parent.name
            if slug not in filings:
                filings.append(slug)
    return filings


# ---------- references (body hyperlink list, external only) ----------

_HYPERLINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def resolve_references(body: str) -> list[dict]:
    """
    Extract every non-image-ref, non-same-page-anchor hyperlink from the body.
    Return a `references[]` list with title, url, resolved=False (future work:
    cross-ref resolution against INDEX.md + qms-reference-graph.md).
    """
    refs: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for m in _HYPERLINK_RE.finditer(body):
        # Skip image refs (preceded by `!`)
        if m.start() > 0 and body[m.start() - 1] == "!":
            continue
        title, url = m.group(1), m.group(2)
        if url.startswith("#"):
            continue  # same-page anchor
        if url.startswith("images/") or url.startswith("../images/"):
            continue  # Authoritative-source per-image link — not a content ref
        key = (title, url)
        if key in seen:
            continue
        seen.add(key)
        refs.append({
            "doc_id": None, "title": title, "url": url,
            "resolved": False,
            "note": None,
        })
    return refs


# ---------- deterministic counts ----------

def compute_counts(body: str, manifest: dict) -> dict:
    return {
        "pages": manifest.get("page_count", 0),
        "has_images": manifest.get("image_summary", {}).get("content_count", 0) > 0,
        "image_count": manifest.get("image_summary", {}).get("content_count", 0),
        "has_tables": bool(re.search(r"^\|.*\|.*\|", body, re.MULTILINE)),
        "has_form_fields": bool(re.search(r"\[____\]|- \[[ x]\]|\[SIGNATURE:", body)),
        "has_hyperlinks": bool(re.search(r"(?<!\!)\[[^\]]+\]\([^)]+\)", body)),
        "hyperlink_count": len(
            re.findall(r"(?<!\!)\[[^\]]+\]\([^)]+\)", body)
        ),
    }


# ---------- dhf_role lookup ----------

def lookup_dhf_role(project_yml: Path, dhf_leaf: str) -> str | None:
    """Parse project.yml for `leaf: <dhf>` -> `role: <role>`. Minimal YAML."""
    if not project_yml.exists():
        return None
    text = project_yml.read_text(encoding="utf-8")
    # Find the dhfs: block and walk entries
    m = re.search(
        rf"-\s*leaf:\s*{re.escape(dhf_leaf)}\s*\n(.*?)(?=\n\s*-\s*leaf:|\n[a-zA-Z])",
        text, re.DOTALL,
    )
    if not m:
        return None
    block = m.group(1)
    rm = re.search(r"role:\s*(\w+)", block)
    return rm.group(1) if rm else None


# ---------- main entry ----------

def enrich(staging_dir: Path, repo_root: Path) -> dict:
    """Read body from staging/body.md (structure_body output)."""
    body_path = staging_dir / "body.md"
    body = body_path.read_text(encoding="utf-8") if body_path.exists() else ""
    return enrich_with_body(staging_dir, repo_root, body)


def enrich_with_body(staging_dir: Path, repo_root: Path, body: str) -> dict:
    """
    Variant called from adopt_v30.py cmd_assemble after placeholder substitution.
    Uses the fully-assembled body (with image fragments spliced in) so counts
    and reference resolution see the final shape.
    """
    dispatch = json.loads((staging_dir / "dispatch.json").read_text())
    manifest = json.loads((staging_dir / "manifest.json").read_text())
    cache = (staging_dir / "all.txt").read_text(encoding="utf-8", errors="ignore")

    today = time.strftime("%Y-%m-%d")

    dhf = dispatch["dhf"]
    dhf_role = lookup_dhf_role(repo_root / "project.yml", dhf)

    forms_dir = repo_root / "docs/internal/source-md/Forms"
    sops_dir = repo_root / "docs/internal/source-md/SOPs"
    wis_dir = repo_root / "docs/internal/source-md/Work Instructions"
    manifest_paths = list(
        (repo_root / "docs/project/submissions").glob("*/composition-manifest.md")
    )

    template_of, template_hints = infer_template(dispatch["title"], forms_dir)
    authored_per, authored_per_hints = scan_authored_per(cache, sops_dir, wis_dir)
    filings = scan_filings(dispatch["title_stem"], manifest_paths)
    references = resolve_references(body)
    counts = compute_counts(body, manifest)
    version_lineage = seed_version_lineage(dispatch, today)

    title_stem = dispatch["title_stem"]
    ext = Path(dispatch["source_pdf"]).suffix.lstrip(".")
    formal_rel = f"formal/{title_stem}.{ext}"

    return {
        # Identity
        "title": dispatch["title"],
        "doc_type": dispatch["doc_type"],
        "dhf": dhf,
        "dhf_role": dhf_role,
        "dhf_area": dispatch["dhf_area"],
        # Lifecycle
        "status": "draft",
        "lifecycle": "draft",
        "owner": "TBD — author to populate",
        "last_modified": today,
        "docflow_version": dispatch.get("adopt_version", "v30"),
        # Versioning
        "doc_version": dispatch["doc_version"],
        "release_version": dispatch.get("release_version"),
        "version_lineage": version_lineage,
        # Provenance
        "source_formal": formal_rel,
        "target_formal": formal_rel,
        "conversion_date": today,
        "conversion_method": "adopt_v30 (classify_doc + extract_pdf + extract_title_version + "
                             "splice_hyperlinks + structure_body agent + parallel interpret_image agents)",
        "conversion_fidelity": "summary",
        **counts,
        # Template binding
        "template_of": template_of,
        "template_hints": template_hints,
        # Process binding
        "authored_per": authored_per,
        "authored_per_hints": authored_per_hints,
        # Filing composition
        "filings": filings,
        # Cross-references
        "references": references,
        # History
        "conversion_history": [
            {
                "date": today,
                "event": (
                    f"Adopted under docflow {dispatch.get('adopt_version', 'v30')} — "
                    f"classify_doc={dispatch.get('classify', {}).get('basis')}, "
                    f"title_basis=cover-page, doc_version_basis=revision-history, "
                    f"{len(dispatch.get('agents', []))} image agents + 1 body structurer "
                    f"dispatched in parallel."
                ),
            },
        ],
    }


# ---------- YAML dump (minimal, scope-tight) ----------

def dump_yaml(d: dict) -> str:
    """
    Minimal YAML serializer that covers the shapes we emit. Handles: scalars
    (str/int/float/bool/None), flat lists, lists of dicts one level deep, and
    top-level mixed dicts. Good enough for frontmatter; avoids pulling PyYAML.
    """
    lines: list[str] = []
    for key, value in d.items():
        lines.append(_dump_pair(key, value, 0))
    return "\n".join(lines)


def _scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if s == "":
        return '""'
    if re.search(r'[:#\[\]{}&*!|>\'"%@`\n]|^\s|\s$|^(true|false|null|yes|no)$', s, re.IGNORECASE):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def _dump_pair(key: str, value, indent: int) -> str:
    pad = "  " * indent
    if isinstance(value, list):
        if not value:
            return f"{pad}{key}: []"
        parts = [f"{pad}{key}:"]
        for item in value:
            if isinstance(item, dict):
                first = True
                for k2, v2 in item.items():
                    if first:
                        parts.append(f"{pad}  - {k2}: {_scalar(v2) if not isinstance(v2, (list, dict)) else _nested(v2, indent + 2)}")
                        first = False
                    else:
                        parts.append(f"{pad}    {k2}: {_scalar(v2) if not isinstance(v2, (list, dict)) else _nested(v2, indent + 2)}")
            else:
                parts.append(f"{pad}  - {_scalar(item)}")
        return "\n".join(parts)
    if isinstance(value, dict):
        if not value:
            return f"{pad}{key}: {{}}"
        parts = [f"{pad}{key}:"]
        for k2, v2 in value.items():
            parts.append(_dump_pair(k2, v2, indent + 1))
        return "\n".join(parts)
    return f"{pad}{key}: {_scalar(value)}"


def _nested(v, indent: int) -> str:
    # Simple nested fallback — lists/dicts inside a list item get a flat scalar.
    # We don't use deeply nested shapes in our frontmatter, so this is rarely hit.
    return _scalar(v) if not isinstance(v, (list, dict)) else json.dumps(v)


# ---------- CLI ----------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("staging_dir")
    ap.add_argument("--repo-root", default=None,
                    help="Repo root (defaults to ancestor containing project.yml)")
    ap.add_argument("--yaml", action="store_true", help="Emit YAML instead of JSON")
    args = ap.parse_args()

    staging = Path(args.staging_dir).expanduser().resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else _find_repo_root(staging)
    if repo_root is None:
        print(json.dumps({"error": "could not find repo root with project.yml"}), file=sys.stderr)
        return 1

    fm = enrich(staging, repo_root)
    if args.yaml:
        print(dump_yaml(fm))
    else:
        print(json.dumps(fm, indent=2, default=str))
    return 0


def _find_repo_root(start: Path) -> Path | None:
    p = start.resolve()
    while p != p.parent:
        if (p / "project.yml").exists():
            return p
        p = p.parent
    return None


if __name__ == "__main__":
    sys.exit(main())
