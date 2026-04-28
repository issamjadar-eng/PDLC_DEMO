#!/usr/bin/env python3
"""
extract_title_version.py — Deterministic title + doc_version extraction for adopt orchestrator.

Ports adopter.md Phase 0 (sections 0.1 + 0.2) from LLM tool-calls to Python.
The LLM walked pdfinfo / first-page regex / revision-history search tool-call by
tool-call; this script does all of it in one subprocess call plus regex scanning.

Wall-clock target: < 0.5s for a 16-page SAD.
LLM tool calls: zero (this script is the LLM substitute for adopter Phase 0).

Exit codes:
  0 — both title and doc_version extracted (success)
  1 — title or doc_version not found (orchestrator escalates to agents/interpret_title.md)
  2 — invocation error (bad arguments, pdfinfo/pdftotext not installed)

Output: JSON on stdout with shape:
  {
    "title": "MedTech Project IntraOp - Software Architecture Document (SAD) - 1.0.0",
    "title_basis": "pdf-metadata" | "cover-page" | "body-first-h1" | "filename-stem" | null,
    "doc_version": "v50",
    "doc_version_raw": "v.50",
    "doc_version_basis": "revision-history" | "override" | "header-footer" | "cover-page" | "pdf-metadata" | "semantic-body" | null,
    "release_version": "1.0.0" | null,
    "warnings": [...]
  }

On failure (exit 1), fields that could not be extracted are null and `warnings[]`
captures what was tried.

Requires: pdfinfo, pdftotext (poppler-utils). No Python third-party deps.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


# --- Subprocess helpers ---

def _run(cmd: list[str]) -> str:
    """Run a subprocess, return stdout. Raises on non-zero exit."""
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, check=True
        ).stdout
    except FileNotFoundError as e:
        raise RuntimeError(f"required binary not installed: {cmd[0]}") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"{cmd[0]} failed: {e.stderr}") from e


def _pdfinfo(pdf_path: str) -> dict:
    """Parse `pdfinfo` output into a dict of key -> value."""
    info: dict[str, str] = {}
    for line in _run(["pdfinfo", pdf_path]).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            info[k.strip()] = v.strip()
    return info


def _pdftotext_page(pdf_path: str, page: int) -> str:
    """Extract one page as -layout plain text."""
    return _run(["pdftotext", "-layout", "-f", str(page), "-l", str(page), pdf_path, "-"])


def _pdftotext_all(pdf_path: str) -> str:
    return _run(["pdftotext", "-layout", pdf_path, "-"])


# --- Title extraction ---

# Titles that look like section headings, not document titles
_GENERIC_H1_PATTERNS = re.compile(
    r"^\s*(purpose|introduction|overview|scope|abstract|contents|table of contents)\s*$",
    re.IGNORECASE,
)

# Filesystem-forbidden characters
_FS_FORBIDDEN = re.compile(r'[\\/:*?<>|"]')

# Trailing " - Confluence" / " - ADI FAI - Confluence" suffix that Confluence adds
# to PDF /Title metadata when exporting via headless Chrome
_CONFLUENCE_SUFFIX = re.compile(
    r"\s*-\s*[A-Z][A-Za-z0-9 &]+-\s*Confluence\s*$|\s*-\s*Confluence\s*$"
)


def _sanitize_title(raw: str) -> str:
    """Apply adopter.md 0.1 sanitization rules."""
    t = raw.strip()
    # Strip the " - <Space> - Confluence" trailing suffix that Chrome headless PDF export injects
    t = _CONFLUENCE_SUFFIX.sub("", t).strip()
    t = _FS_FORBIDDEN.sub("", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def _looks_like_title(candidate: str) -> bool:
    """Heuristic — rejects obvious section headings and filesystem paths."""
    if not candidate or len(candidate) < 3:
        return False
    if _GENERIC_H1_PATTERNS.match(candidate):
        return False
    # Looks like a filesystem path
    if candidate.startswith(("/", ".", "~")) or candidate.count("/") > 1:
        return False
    return True


def _extract_release_version(title: str) -> Optional[str]:
    """
    Extract embedded release version like "... - 1.0.0" at end of title.
    Returns "1.0.0" (just the version), not the leading " - ".
    Only trailing semver-like triplets; won't match "v1.0" or document versions.
    """
    m = re.search(r"-\s*(\d+\.\d+(?:\.\d+)?)\s*$", title)
    return m.group(1) if m else None


def _extract_title(pdf_path: str, pdfinfo: dict, all_text: str, page1_text: str,
                   warnings: list) -> tuple[Optional[str], Optional[str]]:
    """
    Returns (title, basis). basis is one of:
      'cover-page', 'pdf-metadata', 'body-first-h1', 'filename-stem'.
    Priority order matches adopter.md 0.1.
    """
    # 1. Cover page / first-page prominent text —
    #    heuristic: first non-blank line of page 1 if it's short-ish (≤120 chars)
    #    and not a generic section heading
    for line in page1_text.splitlines():
        stripped = line.strip()
        if stripped and len(stripped) <= 120:
            if _looks_like_title(stripped):
                sanitized = _sanitize_title(stripped)
                if sanitized:
                    return sanitized, "cover-page"
            break  # first non-blank line wasn't title-like; fall through

    # 2. PDF metadata /Title
    meta_title = pdfinfo.get("Title", "").strip()
    if meta_title and _looks_like_title(meta_title):
        sanitized = _sanitize_title(meta_title)
        if sanitized:
            return sanitized, "pdf-metadata"

    # 3. Body first H1 — proxy: first non-blank line after a blank-line in all_text
    #    (pdftotext -layout preserves heading whitespace; H1s typically surrounded by blanks)
    lines = all_text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and _looks_like_title(stripped) and len(stripped) <= 120:
            # Require a preceding blank or start-of-doc
            if i == 0 or not lines[i - 1].strip():
                sanitized = _sanitize_title(stripped)
                if sanitized:
                    return sanitized, "body-first-h1"
                break

    # 4. Filename stem verbatim — last resort
    stem = Path(pdf_path).stem
    if stem:
        warnings.append(
            "Title extracted from filename — manual review recommended "
            "(content sources did not yield a title)"
        )
        return _sanitize_title(stem), "filename-stem"

    return None, None


# --- Doc-version extraction ---

# Priority-ordered patterns for doc_version. Each entry is (basis_label, compiled_pattern).
# Patterns MUST capture the version number in group(1).
_VERSION_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("revision-history", re.compile(r"Current document version:\s*v\.?\s*(\d+)", re.IGNORECASE)),
    ("revision-history", re.compile(r"\bVersion\s+(\d+)\s*\(current\)", re.IGNORECASE)),
    ("revision-history", re.compile(r"\bRevision:\s*(\d+)\b", re.IGNORECASE)),
    ("cover-page",       re.compile(r"\bDocument\s+Version:?\s*v\.?\s*(\d+)", re.IGNORECASE)),
    ("cover-page",       re.compile(r"\bDoc(?:ument)?\s+Rev(?:ision)?:?\s*v?\.?\s*(\d+)", re.IGNORECASE)),
]

# Semantic body fallback — looser, scored
_SEMANTIC_VERSION = re.compile(r"\bv\.?\s*(\d+)\b", re.IGNORECASE)


def _normalize_version(raw: str) -> str:
    """Normalize a version string to `v<N>` shape."""
    # Pull just the integer
    m = re.search(r"(\d+)", raw)
    if not m:
        return raw
    n = int(m.group(1))
    return f"v{n}"


def _extract_doc_version(all_text: str, pdfinfo: dict, override: Optional[str],
                         warnings: list) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Returns (doc_version, doc_version_raw, basis).
    Priority order matches adopter.md 0.2.
    """
    # 1. Explicit override
    if override:
        return _normalize_version(override), override, "override"

    # 2-5. Try priority patterns over whole body text (covers revision-history,
    #      running header/footer text — pdftotext surfaces these in the linearized flow,
    #      cover-page explicit markers).
    for basis, pattern in _VERSION_PATTERNS:
        m = pattern.search(all_text)
        if m:
            raw_span = m.group(0)
            return _normalize_version(m.group(1)), raw_span.strip(), basis

    # 5. PDF metadata /Subject or /Keywords — check for version tokens
    for field in ("Subject", "Keywords"):
        value = pdfinfo.get(field, "")
        if value:
            m = _SEMANTIC_VERSION.search(value)
            if m:
                return _normalize_version(m.group(1)), m.group(0), "pdf-metadata"

    # 6. Semantic body search — score each match by context, pick the winner.
    #    Only fires when no explicit marker was found. We want to avoid false
    #    positives on things like "iPhone v.10" in a URL.
    candidates: list[tuple[int, str, str]] = []
    for m in _SEMANTIC_VERSION.finditer(all_text):
        start, end = m.span()
        ctx = all_text[max(0, start - 30): end + 30].lower()
        score = 0
        if "version" in ctx:
            score += 2
        # In a revision-history-style table row
        if any(tok in ctx for tok in ["revision", "rev.", "document version", "doc version"]):
            score += 3
        # Near a heading / standalone line
        if ctx.count("\n") >= 1:
            score += 1
        if score >= 2:
            candidates.append((score, m.group(0), m.group(1)))

    if candidates:
        candidates.sort(reverse=True)
        _, raw_hit, num = candidates[0]
        if len(candidates) > 1 and candidates[0][0] == candidates[1][0]:
            warnings.append(
                f"multiple equally-scored version candidates; picked '{raw_hit}' (semantic-body)"
            )
        return _normalize_version(num), raw_hit, "semantic-body"

    # 7. Error-out
    warnings.append(
        "doc_version not found — orchestrator should escalate to interpret_title.md "
        "or surface the --doc-version override request."
    )
    return None, None, None


# --- Main ---

def extract(pdf_path: str, override: Optional[str] = None) -> dict:
    warnings: list[str] = []

    if not os.path.exists(pdf_path):
        raise RuntimeError(f"file not found: {pdf_path}")

    pdfinfo = _pdfinfo(pdf_path)

    try:
        page1_text = _pdftotext_page(pdf_path, 1)
    except RuntimeError as e:
        warnings.append(f"pdftotext page-1 failed: {e}")
        page1_text = ""

    try:
        all_text = _pdftotext_all(pdf_path)
    except RuntimeError as e:
        warnings.append(f"pdftotext full failed: {e}")
        all_text = ""

    title, title_basis = _extract_title(pdf_path, pdfinfo, all_text, page1_text, warnings)
    doc_version, doc_version_raw, version_basis = _extract_doc_version(
        all_text, pdfinfo, override, warnings
    )

    release_version = _extract_release_version(title) if title else None

    return {
        "title": title,
        "title_basis": title_basis,
        "doc_version": doc_version,
        "doc_version_raw": doc_version_raw,
        "doc_version_basis": version_basis,
        "release_version": release_version,
        "warnings": warnings,
    }


def _self_test() -> int:
    """
    Smoke test against the IntraOp SAD. Ground truth:
      title:              MedTech Project IntraOp - Software Architecture Document (SAD) - 1.0.0
      doc_version:        v50  (from "Current document version: v.50" in Review appendix)
      doc_version_raw:    "Current document version: v.50" (or similar text slice)
      doc_version_basis:  revision-history
      release_version:    1.0.0 (embedded in title)
    """
    repo_root = Path(__file__).resolve().parents[4]
    sad = (
        repo_root
        / "docs/project/dhfs/mfd-b/design-controls/architecture/formal"
        / "MedTech Project IntraOp - Software Architecture Document (SAD) - 1.0.0.pdf"
    )
    if not sad.exists():
        print(f"[self-test] SKIP: SAD not at {sad}")
        return 0

    result = extract(str(sad))
    print(json.dumps(result, indent=2))

    fails = []
    expected_title = "MedTech Project IntraOp - Software Architecture Document (SAD) - 1.0.0"
    if result["title"] != expected_title:
        fails.append(f"title: expected '{expected_title}', got '{result['title']}'")
    if result["doc_version"] != "v50":
        fails.append(f"doc_version: expected 'v50', got '{result['doc_version']}'")
    if result["release_version"] != "1.0.0":
        fails.append(f"release_version: expected '1.0.0', got '{result['release_version']}'")

    if fails:
        print("[self-test] FAIL", file=sys.stderr)
        for f in fails:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("[self-test] PASS")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("pdf", nargs="?", help="Path to PDF (omit for --self-test)")
    ap.add_argument(
        "--doc-version",
        dest="override",
        help="Explicit doc version override (e.g. v50); skips extraction heuristics",
    )
    ap.add_argument("--self-test", action="store_true", help="Run smoke test against IntraOp SAD")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    if not args.pdf:
        ap.error("pdf path required (or pass --self-test)")

    try:
        result = extract(args.pdf, override=args.override)
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2))
    return 0 if result["title"] and result["doc_version"] else 1


if __name__ == "__main__":
    sys.exit(main())
