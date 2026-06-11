#!/usr/bin/env python3
"""locate_md_target.py — convention-detection for "where should this binary's markdown live?"

Given a controlled binary (.docx/.doc/.pdf/.xlsx/...) that has no markdown view,
infer the canonical markdown target by reading the project's OWN conventions —
never by guessing from the filename alone. Signal priority (highest first):

  1. Already covered  — a sibling md with the same stem, OR any indexed md whose
                        frontmatter links this binary (source_path/source_file/
                        source_formal/target_formal) → nothing to do.
  2. Tier rule        — deterministic structural mirrors defined by medtech-docs:
                          docs/internal/source/<sub>/X.ext → docs/internal/source-md/<sub>/X.md
  3. Taxonomy         — nearest ancestor .taxonomy.yml governs the folder (the
                        _confluence regime): target is the doctype <slug> page.
  4. Sibling pattern  — a sibling directory at the same level already follows a
                        binary↔md convention (e.g. <peer>/<title>.md + formal/<bin>).
  5. README presence  — folder/parent README.md is captured as the human-authored
                        convention source the resolver/agent must read.

Output: a single JSON object on stdout describing the proposal + confidence band:
  confidence ∈ {covered, high, prompt, none}
    covered → md already exists/linked (target points at it)
    high    → exactly one strong, unambiguous convention signal → auto-resolve
    prompt  → multiple candidates, or pre-existing unlinked md in the folder, or
              only weak signals → ask the user to confirm before generating
    none    → no signal at all → ask the user for an explicit --into path

This module is project-agnostic: it encodes only generic medtech-docs / docflow
structural conventions (source→source-md mirror, .taxonomy.yml governance,
formal/ siblings, README-before-write). No project, device, or team names.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BINARY_EXTS = {".docx", ".doc", ".pdf", ".xlsx", ".xls", ".pptx", ".ppt"}
# Frontmatter / sentinel keys that constitute an md→binary "claim".
LINK_KEYS = ("source_path", "source_file", "source_formal", "target_formal")


def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _find_up(start: Path, root: Path, name: str) -> Path | None:
    """Walk from start's folder up to root, returning the nearest <dir>/<name>."""
    cur = start if start.is_dir() else start.parent
    while True:
        cand = cur / name
        if cand.is_file():
            return cand
        if cur == root or cur.parent == cur:
            return None
        cur = cur.parent


def _claimed_by(root: Path, binary_rel: str, binary_base: str) -> Path | None:
    """Return an indexed md that already claims this binary, if any."""
    docs = root / "docs"
    if not docs.is_dir():
        return None
    needle_base = binary_base
    for md in docs.rglob("*.md"):
        if "/dhfs-retired/" in md.as_posix() or "/_scratch/" in md.as_posix():
            continue
        txt = _read_text(md)
        if not txt:
            continue
        # cheap pre-filter: the basename must appear at all
        if needle_base not in txt:
            continue
        for key in LINK_KEYS:
            # key: "...<binary_base>..." on a line
            if re.search(rf"^\s*{key}\s*:\s*.*{re.escape(needle_base)}", txt, re.MULTILINE):
                return md
    return None


def _sibling_md_same_stem(binary: Path) -> Path | None:
    cand = binary.with_suffix(".md")
    return cand if cand.is_file() else None


def _folder_md_views(folder: Path) -> list[str]:
    """Non-README markdown files already in the folder (ambiguity signal)."""
    return sorted(
        p.name for p in folder.glob("*.md") if p.name.lower() != "readme.md"
    )


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _title_match_view(folder: Path, binary_stem: str) -> Path | None:
    """An existing folder md that looks like it's ALREADY the view of this binary.

    Heuristic: the md's frontmatter `title:` (or its filename stem) normalizes to
    the same string as the binary's stem after stripping a leading DOC-ID prefix
    (e.g. 'FORM-000108237 - Validation Assessment - X' ~ 'Validation Assessment - X').
    A hit means the right action is almost certainly "link the existing view",
    not "generate a new one" — so the caller should PROMPT, not auto-generate.
    """
    stem_no_id = re.sub(r"^[A-Z]+-\d+\s*[-–]?\s*", "", binary_stem)
    targets = {_norm(binary_stem), _norm(stem_no_id)}
    for md in folder.glob("*.md"):
        if md.name.lower() == "readme.md":
            continue
        if _norm(md.stem) in targets:
            return md
        txt = _read_text(md)
        m = re.search(r'^\s*title\s*:\s*["\']?(.+?)["\']?\s*$', txt, re.MULTILINE)
        if m and _norm(m.group(1)) in targets:
            return md
    return None


def _tier_rule_target(root: Path, binary: Path) -> tuple[Path, str] | None:
    """docs/internal/source/<sub>/X.ext → docs/internal/source-md/<sub>/X.md"""
    try:
        rel = binary.relative_to(root / "docs" / "internal" / "source")
    except ValueError:
        return None
    target = root / "docs" / "internal" / "source-md" / rel.parent / (binary.stem + ".md")
    return target, "source→source-md mirror (medtech-docs tier rule)"


def _taxonomy_target(root: Path, binary: Path) -> tuple[Path, str, list[str]] | None:
    """If a .taxonomy.yml governs the folder, this is the _confluence regime.

    Convention: the controlled binary sits in <slug>/images/<bin>; the page body
    is <slug>/v*.md (splice target) or <slug>/index.md. We point at an existing
    v*.md page if present (SPLICE), else propose <slug>/<stem>.md.
    """
    tax = _find_up(binary, root, ".taxonomy.yml")
    if tax is None:
        return None
    folder = binary.parent
    # slug folder = the folder above an images/ attachment dir, else the parent
    slug_dir = folder.parent if folder.name == "images" else folder
    versioned = sorted(slug_dir.glob("v*.md"))
    rationale_extra = [f".taxonomy.yml governs (nearest: {tax.relative_to(root)})"]
    # band: 'high' only for an unambiguous single doc-page splice; otherwise prompt.
    if versioned:
        band = "high" if len(versioned) == 1 else "prompt"
        why = ("managed _confluence page → SPLICE into existing version body"
               if band == "high"
               else f"{len(versioned)} versioned pages — confirm which is the splice target")
        return versioned[0], why, rationale_extra, band
    idx = slug_dir / "index.md"
    if idx.is_file():
        # A node index.md is NOT necessarily the body for THIS attachment — an
        # images/ folder can hold several controlled binaries. Always prompt.
        return idx, "managed _confluence node has index.md — confirm whether this attachment IS the page body (images/ may hold multiple binaries)", rationale_extra, "prompt"
    return slug_dir / (binary.stem + ".md"), "managed _confluence node (no page yet)", rationale_extra, "prompt"


def _sibling_pattern_target(root: Path, binary: Path) -> tuple[Path, str] | None:
    """A peer directory already pairs a working md with a formal/<binary>.

    e.g. <area>/peer/<Title>.md + <area>/peer/formal/<bin>  ⇒ for a binary at
    <area>/this/formal/<bin>, propose <area>/this/<Title-from-content>.md.
    Only fires when the binary is inside a formal/ dir whose grandparent has a
    sibling folder containing both a formal/ subdir and a linked md.
    """
    folder = binary.parent
    if folder.name != "formal":
        return None
    this_dir = folder.parent
    area = this_dir.parent
    for peer in area.iterdir():
        if not peer.is_dir() or peer == this_dir:
            continue
        if (peer / "formal").is_dir() and any(
            p.suffix == ".md" and p.name.lower() != "readme.md" for p in peer.glob("*.md")
        ):
            target = this_dir / (binary.stem + ".md")
            return target, f"sibling folder '{peer.name}/' follows <dir>/<title>.md + formal/<bin>"
    return None


def locate(root: Path, binary: Path) -> dict:
    root = root.resolve()
    binary = binary.resolve()
    rel = binary.relative_to(root).as_posix() if binary.is_relative_to(root) else str(binary)
    out: dict = {
        "binary": rel,
        "exists": binary.is_file(),
        "ext": binary.suffix.lower(),
        "confidence": "none",
        "regime": None,
        "authoritative": "formal",  # binary is the controlled record by default
        "target_md": None,
        "rationale": [],
        "signals": {},
        "alternatives": [],
    }
    if not binary.is_file():
        out["rationale"].append("binary not found")
        return out
    if binary.suffix.lower() not in BINARY_EXTS:
        out["rationale"].append(f"not a recognized binary type ({binary.suffix})")
        return out

    folder = binary.parent
    base = binary.name

    # ---- 1. Already covered? ----------------------------------------------
    sib = _sibling_md_same_stem(binary)
    if sib:
        out.update(confidence="covered", target_md=sib.relative_to(root).as_posix(),
                   regime="sibling-stem")
        out["rationale"].append(f"sibling md with same stem already exists: {sib.name}")
        return out
    claimed = _claimed_by(root, rel, base)
    if claimed:
        out.update(confidence="covered", target_md=claimed.relative_to(root).as_posix(),
                   regime="linked")
        out["rationale"].append(f"an indexed md already links this binary: {claimed.relative_to(root)}")
        return out

    # ---- gather ambiguity + README signals --------------------------------
    folder_views = _folder_md_views(folder)
    out["signals"]["folder_md_views_unlinked"] = folder_views
    readme = _find_up(binary, root, "README.md")
    out["signals"]["nearest_readme"] = readme.relative_to(root).as_posix() if readme else None

    # ---- 2. Tier rule (strongest deterministic convention) ----------------
    tier = _tier_rule_target(root, binary)
    if tier:
        target, why = tier
        out.update(regime="source-md", target_md=target.relative_to(root).as_posix())
        out["rationale"].append(why)
        out["confidence"] = "high" if not target.is_file() else "covered"
        if target.is_file():
            out["rationale"].append("target already exists — treat as covered")
        return out

    # A folder md whose title matches the binary is almost certainly the view
    # already — surfaced as a "link this instead of generating" alternative.
    likely = _title_match_view(folder, binary.stem)
    if likely:
        out["alternatives"].append({
            "action": "link-existing",
            "md": likely.relative_to(root).as_posix(),
            "why": "title matches the binary — likely already the view; add source_formal link instead of generating a duplicate",
        })

    # ---- 3. Taxonomy (_confluence regime) ---------------------------------
    tax = _taxonomy_target(root, binary)
    if tax:
        target, why, extra, band = tax
        out.update(regime="_confluence", target_md=target.relative_to(root).as_posix())
        out["rationale"].extend(extra + [why])
        out["confidence"] = band
        return out

    # ---- 4. Sibling pattern ----------------------------------------------
    sibpat = _sibling_pattern_target(root, binary)
    if sibpat:
        target, why = sibpat
        out.update(regime="sibling-pattern", target_md=target.relative_to(root).as_posix())
        out["rationale"].append(why)
        # The proposed target lives in the parent dir (not the binary's formal/
        # dir) — check there for an existing title-matching view too.
        if not likely:
            likely = _title_match_view(target.parent, binary.stem)
            if likely:
                out["alternatives"].append({
                    "action": "link-existing",
                    "md": likely.relative_to(root).as_posix(),
                    "why": "title matches the binary — likely already the view; add source_formal link instead of generating a duplicate",
                })
        # If the folder already has unlinked md views, the right action is
        # ambiguous (link existing vs generate new) → prompt.
        out["confidence"] = "prompt"
        if likely:
            out["rationale"].append(
                f"an existing md ('{likely.name}') matches this binary's title — "
                "likely already the view; confirm link-vs-generate (see alternatives)"
            )
        elif folder_views:
            out["rationale"].append(
                f"folder already has unlinked md ({', '.join(folder_views)}) — "
                "confirm whether to link an existing view or generate a new one"
            )
        return out

    # ---- 5. Nothing decisive ---------------------------------------------
    if likely:
        out["confidence"] = "prompt"
        out["rationale"].append(
            f"no folder-convention signal, but an existing md ('{likely.name}') matches "
            "this binary's title — likely already the view; confirm link-vs-generate"
        )
    elif folder_views:
        out["confidence"] = "prompt"
        out["rationale"].append(
            f"no convention signal, but folder has unlinked md ({', '.join(folder_views)}) — "
            "one may already be the view; confirm or pass --into"
        )
    else:
        out["confidence"] = "none"
        out["rationale"].append("no README/taxonomy/sibling convention signal — pass --into explicitly")
    return out


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("binary", help="path to the controlled binary (rel or abs)")
    ap.add_argument("--root", default=".", help="project root (default: cwd)")
    args = ap.parse_args()
    result = locate(Path(args.root), Path(args.binary))
    print(json.dumps(result, indent=2))
    # exit code encodes the band for scripting: 0 high/covered, 2 prompt, 3 none
    return {"high": 0, "covered": 0, "prompt": 2, "none": 3}.get(result["confidence"], 1)


if __name__ == "__main__":
    sys.exit(main())
