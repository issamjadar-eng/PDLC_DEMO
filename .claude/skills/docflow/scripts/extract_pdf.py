#!/usr/bin/env python3
"""
extract_pdf.py — Deterministic PDF extraction for /docflow adopt orchestrator.

Replaces the per-page LLM tool-calling that today dominates adopter wall-clock.
Produces a JSON manifest the orchestrator can hand to per-image agents in parallel.

Outputs:
  - JSON manifest on stdout describing the document structure
  - Image files in <staging-dir>/images/ (extracted via pdfimages, hashed, deduped,
    classified as decorative vs content by dimension + alpha heuristics)
  - Page text in <staging-dir>/pages/page-NNN.txt (one file per page)
  - Combined text in <staging-dir>/all.txt (pdftotext layout mode)

Wall-clock target: < 30 seconds for a 16-page, 8-image SAD.
LLM tool calls: zero (this script is the LLM substitute for Phases 1, 2, 4.1-4.5, 4.9).

Requires: pdfinfo, pdftotext, pdfimages (poppler-utils); Pillow (for orientation+alpha)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a subprocess, capturing output. Raises on non-zero exit."""
    return subprocess.run(cmd, capture_output=True, text=True, check=True, **kwargs)


def _pdfinfo(pdf_path: str) -> dict:
    """Parse pdfinfo output into a dict."""
    try:
        out = _run(["pdfinfo", pdf_path]).stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"pdfinfo failed: {e.stderr}") from e
    info = {}
    for line in out.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            info[k.strip()] = v.strip()
    return info


def _extract_text(pdf_path: str, staging_dir: Path, page_count: int) -> tuple[Path, list[Path]]:
    """Extract text via pdftotext. Returns (combined_path, [per_page_paths])."""
    pages_dir = staging_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    combined = staging_dir / "all.txt"
    _run(["pdftotext", "-layout", pdf_path, str(combined)])

    page_paths = []
    for i in range(1, page_count + 1):
        page_path = pages_dir / f"page-{i:03d}.txt"
        _run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), pdf_path, str(page_path)])
        page_paths.append(page_path)

    return combined, page_paths


def _extract_images(pdf_path: str, staging_dir: Path) -> list[dict]:
    """
    Extract images via pdfimages. Hash each, dedup, classify decorative-vs-content
    by dimension + alpha heuristics. Returns a list of image manifest dicts.
    """
    raw_dir = staging_dir / "images-raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    final_dir = staging_dir / "images"
    final_dir.mkdir(parents=True, exist_ok=True)

    # pdfimages -png merges color + soft-mask into a single PNG per visible image,
    # avoiding the spurious image+mask pairs that -all produces. Each visible image
    # becomes ONE file in raw_dir, not two.
    _run(["pdfimages", "-png", "-p", pdf_path, str(raw_dir / "img")])

    # Try to import Pillow; fall back to dimension-only classification
    try:
        from PIL import Image
        have_pil = True
    except ImportError:
        have_pil = False

    seen_hashes: dict[str, str] = {}  # hash -> first-seen filename
    # Track (page, dimensions) pairs to detect pdfimages foreground+mask companions:
    # pdfimages -png emits two PNG files for an image+softmask object — same page,
    # same dimensions, adjacent indices, but different bytes. Dedupe these as
    # "sibling pairs" — keep the first, mark the second as duplicate.
    seen_page_dims: dict[tuple[int, tuple[int, int]], str] = {}  # (page, dims) -> first filename
    images: list[dict] = []
    raw_files = sorted(raw_dir.iterdir())

    for raw in raw_files:
        if not raw.is_file():
            continue
        # pdfimages -p produces names like img-NNN-MMM.ext where NNN is page, MMM is index
        m = re.match(r"img-(\d+)-(\d+)\.(\w+)", raw.name)
        page_num = int(m.group(1)) if m else 0

        # Hash (catches byte-identical duplicates)
        h = hashlib.sha1(raw.read_bytes()).hexdigest()[:12]
        is_dup = h in seen_hashes
        sibling_pair = False  # track whether dup detection came from sibling rule (vs hash)

        # Probe dimensions + alpha
        dims = (0, 0)
        alpha_ratio = 0.0
        decorative_score = 0.0
        if have_pil:
            try:
                with Image.open(raw) as im:
                    dims = im.size
                    # Alpha analysis — if mostly transparent or very small, likely decorative
                    if im.mode in ("RGBA", "LA"):
                        alpha = im.split()[-1]
                        bbox = alpha.getbbox()
                        if bbox is None:
                            alpha_ratio = 1.0  # fully transparent
                        else:
                            opaque_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                            total_area = im.size[0] * im.size[1]
                            alpha_ratio = 1.0 - (opaque_area / max(total_area, 1))
            except Exception:
                pass

        # Heuristic refinement (2026-04-21 — task ben/089 Phase F):
        #   1. Fully transparent → decorative
        #   2. Tiny (max < 100px) → decorative (icons, bullets)
        #   3. Small squarish (max ≤ 280, aspect 0.85–1.18) → decorative
        #      Catches Confluence/Atlassian footer chrome (16x16, 128x128, 256x256
        #      page-badge icons appearing on the last page of every export).
        #   4. Very thin (min < 50) → decorative (separator lines, narrow logos)
        #   5. Large with non-square aspect (max > 300, aspect < 0.85 or > 1.18)
        #      → content (almost always real diagrams)
        #   6. Otherwise → ambiguous (defer to LLM)
        max_dim = max(dims)
        min_dim = min(dims) if dims[0] and dims[1] else 0
        aspect = (min_dim / max_dim) if max_dim else 0.0  # 1.0 = square, < 1 = rectangular
        is_squarish = 0.85 <= aspect <= 1.18 if max_dim else False

        if alpha_ratio > 0.95:
            decorative_score = 0.9
        elif max_dim < 100:
            decorative_score = 0.85
        elif max_dim <= 280 and is_squarish:
            decorative_score = 0.75  # small square = icon/badge/footer chrome
        elif min_dim < 50:
            decorative_score = 0.7
        elif max_dim > 300 and not is_squarish:
            decorative_score = 0.0  # large rectangular = content
        elif max_dim > 300 and is_squarish:
            decorative_score = 0.2  # large square = probably content (rare diagrams)
        else:
            decorative_score = 0.4

        # Sibling-pair detection: if a prior image on this same page has identical
        # dimensions, this is almost certainly the foreground+softmask companion
        # that pdfimages emits as a separate file. Mark as duplicate.
        page_dim_key = (page_num, dims)
        if not is_dup and page_dim_key in seen_page_dims:
            is_dup = True
            sibling_pair = True

        # Move to final dir if content + not dup
        if is_dup:
            final_path = None
            dup_of = seen_hashes.get(h) or seen_page_dims.get(page_dim_key)
        else:
            seen_hashes[h] = raw.name
            seen_page_dims[page_dim_key] = raw.name
            if decorative_score < 0.5:
                final_path = final_dir / raw.name
                shutil.move(str(raw), str(final_path))
            else:
                final_path = None  # decorative — leave in raw dir for inspection
            dup_of = None

        images.append({
            "raw_filename": raw.name,
            "final_path": str(final_path) if final_path else None,
            "page": page_num,
            "hash": h,
            "is_duplicate": is_dup,
            "duplicate_kind": ("hash" if (is_dup and not sibling_pair) else ("sibling-pair" if sibling_pair else None)),
            "duplicate_of": dup_of,
            "dimensions": list(dims),
            "alpha_ratio": round(alpha_ratio, 3),
            "decorative_score": round(decorative_score, 2),
            "classification_hint": "decorative" if decorative_score >= 0.5 else "content",
        })

    return images


def extract(pdf_path: str, staging_dir: str, image_prefix: str = "img") -> dict:
    """
    Run the full extraction pipeline. Returns a manifest dict suitable for
    JSON serialization and consumption by the adopter orchestrator.
    """
    pdf = Path(pdf_path).resolve()
    if not pdf.exists():
        raise FileNotFoundError(pdf_path)

    staging = Path(staging_dir).resolve()
    staging.mkdir(parents=True, exist_ok=True)

    info = _pdfinfo(str(pdf))
    page_count = int(info.get("Pages", "0"))
    title_meta = info.get("Title", "").strip()

    combined_text, page_paths = _extract_text(str(pdf), staging, page_count)
    images = _extract_images(str(pdf), staging)

    content_images = [im for im in images if im["classification_hint"] == "content" and not im["is_duplicate"]]
    decorative_images = [im for im in images if im["classification_hint"] == "decorative"]
    duplicate_images = [im for im in images if im["is_duplicate"]]

    return {
        "format": "pdf",
        "source_path": str(pdf),
        "staging_dir": str(staging),
        "pdfinfo": info,
        "page_count": page_count,
        "title_meta": title_meta,
        "combined_text_path": str(combined_text),
        "page_text_paths": [str(p) for p in page_paths],
        "image_summary": {
            "extracted_total": len(images),
            "content_count": len(content_images),
            "decorative_count": len(decorative_images),
            "duplicate_count": len(duplicate_images),
        },
        "images": images,
        "content_images": content_images,  # convenience subset for orchestrator
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("pdf_path", help="Path to source PDF")
    parser.add_argument("--staging-dir", required=True, help="Staging directory for extracted artifacts")
    parser.add_argument("--image-prefix", default="img", help="Image filename prefix")
    parser.add_argument("--manifest-out", default=None, help="Write JSON manifest to this path (default: stdout)")
    args = parser.parse_args(argv)

    try:
        manifest = extract(args.pdf_path, args.staging_dir, args.image_prefix)
    except FileNotFoundError as e:
        print(f"PDF not found: {e}", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as e:
        print(f"Subprocess failed: {e}\nstderr: {e.stderr}", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"Extraction failed: {e}", file=sys.stderr)
        return 4

    out_json = json.dumps(manifest, indent=2)
    if args.manifest_out:
        Path(args.manifest_out).write_text(out_json)
        print(f"Manifest written to {args.manifest_out}")
        print(f"Pages: {manifest['page_count']}, content images: {manifest['image_summary']['content_count']}, "
              f"decorative: {manifest['image_summary']['decorative_count']}, duplicates: {manifest['image_summary']['duplicate_count']}")
    else:
        print(out_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
