#!/usr/bin/env python3
"""
commit_atomic.py — Transactional move of staging into the DHF area.

Replaces the v29 adopter Phase 8 dance. Invoked by `adopt_v30.py commit`
after `validate_phase7.py` has passed. Does NOT run validation — callers
MUST pass validation first; this script assumes the staging is good.

Sequence (all-or-nothing):
  1. mkdir DHF_AREA/formal/ and DHF_AREA/images/ (images only if we have any)
  2. git mv SOURCE_PDF → DHF_AREA/formal/<TITLE_STEM>.<ext>  (skip if already there)
  3. Move every image from staging/images/ → DHF_AREA/images/
  4. Verify every image arrived
  5. Verify every `![](images/X)` body ref resolves
  6. Move staging/final.md → DHF_AREA/<TITLE_STEM>.md
  7. Verify the MD arrived
  8. Re-render parent README sentinel blocks (non-blocking)
  9. rm -rf staging

On any step 1-7 failure: roll back (rename any moved files back where they came
from) and emit COMMIT_FAILED.txt in staging. Exit 2.
Step 8 failure is non-blocking (README re-render is a nicety, not a gate).
Step 9 failure is warning-only (user can rm staging manually).

Usage:
  commit_atomic.py <staging_dir> <dhf_area_dir>

Exit codes:
  0 — committed successfully
  1 — invocation error (missing paths, malformed dispatch.json)
  2 — commit failed partway; staging has COMMIT_FAILED.txt with the rollback log
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def _log(msg: str):
    print(f"[commit_atomic] {msg}", file=sys.stderr)


def _run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def commit(staging_dir: Path, dhf_area_dir: Path) -> int:
    # Load dispatch for title_stem + source_pdf + image_ref_prefix
    dispatch_path = staging_dir / "dispatch.json"
    if not dispatch_path.exists():
        _log(f"dispatch.json not found at {dispatch_path}")
        return 1
    dispatch = json.loads(dispatch_path.read_text())

    title_stem = dispatch["title_stem"]
    source_pdf = Path(dispatch["source_pdf"]).resolve()
    image_ref_prefix = dispatch["image_ref_prefix"]
    final_md = staging_dir / "final.md"
    if not final_md.exists():
        _log(f"final.md not found at {final_md} — run `adopt_v30.py assemble` first")
        return 1

    formal_dir = dhf_area_dir / "formal"
    images_dir = dhf_area_dir / "images"
    staging_images = staging_dir / "images"

    # Derive extensions + targets
    src_ext = source_pdf.suffix  # e.g. '.pdf'
    new_formal_path = formal_dir / f"{title_stem}{src_ext}"
    new_md_path = dhf_area_dir / f"{title_stem}.md"

    # Rollback state: list of (from, to) pairs to undo on failure
    rollback: list[tuple[Path, Path]] = []

    def _rollback_and_fail(reason: str) -> int:
        _log(f"COMMIT_FAILED: {reason}")
        for from_path, to_path in reversed(rollback):
            try:
                if to_path.exists():
                    to_path.rename(from_path)
                    _log(f"  rolled back {to_path} → {from_path}")
            except Exception as e:
                _log(f"  rollback failed for {to_path} → {from_path}: {e}")
        (staging_dir / "COMMIT_FAILED.txt").write_text(
            f"reason: {reason}\nrollback attempted on {len(rollback)} moves\n"
        )
        return 2

    # --- Step 1: mkdir targets ---
    try:
        formal_dir.mkdir(parents=True, exist_ok=True)
        has_images = staging_images.exists() and any(staging_images.iterdir())
        if has_images:
            images_dir.mkdir(parents=True, exist_ok=True)
        dhf_area_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return _rollback_and_fail(f"mkdir failed: {e}")

    # --- Step 2: git mv source PDF to new formal location ---
    # Skip if the PDF is already at the target (idempotent)
    if source_pdf.resolve() != new_formal_path.resolve():
        try:
            if new_formal_path.exists():
                return _rollback_and_fail(
                    f"formal target already exists at {new_formal_path} — refusing to overwrite"
                )
            # Prefer `git mv` so the rename stays within git history
            r = subprocess.run(
                ["git", "mv", str(source_pdf), str(new_formal_path)],
                capture_output=True, text=True,
            )
            if r.returncode != 0:
                # Not tracked? Fall back to plain filesystem move
                _log(f"git mv failed ({r.stderr.strip()}); falling back to os.rename")
                source_pdf.rename(new_formal_path)
            rollback.append((source_pdf, new_formal_path))
            _log(f"[2/9] git mv formal → {new_formal_path.name}")
        except Exception as e:
            return _rollback_and_fail(f"formal rename failed: {e}")
    else:
        _log(f"[2/9] formal already at target (skip rename)")

    # --- Step 3: Move images from staging → DHF_AREA/images/ ---
    # Rename staged images to their final descriptor-based names per
    # dispatch.agents[].image_ref_path. The agents' fragments already reference
    # `images/<descriptor>.png`, so we need the files at those final names.
    moved_images: list[tuple[Path, Path]] = []
    if has_images:
        try:
            for entry in dispatch["agents"]:
                staging_img = Path(entry["image_path"])
                if not staging_img.exists():
                    return _rollback_and_fail(
                        f"image from dispatch not found in staging: {staging_img}"
                    )
                # image_ref_path is e.g. "images/descriptor.png" (prefix + descriptor + .png)
                descriptor_png = entry["image_ref_path"].removeprefix(image_ref_prefix)
                final_img = images_dir / descriptor_png
                if final_img.exists():
                    return _rollback_and_fail(
                        f"image target already exists at {final_img}"
                    )
                shutil.move(str(staging_img), str(final_img))
                moved_images.append((staging_img, final_img))
                rollback.append((staging_img, final_img))
            _log(f"[3/9] moved {len(moved_images)} image(s) to {images_dir}")
        except Exception as e:
            return _rollback_and_fail(f"image move failed: {e}")

    # --- Step 4: Verify every image arrived ---
    for _, final_img in moved_images:
        if not final_img.exists():
            return _rollback_and_fail(f"image missing post-move: {final_img}")
    _log(f"[4/9] verified {len(moved_images)} images arrived")

    # --- Step 5: Verify every body image ref resolves ---
    body = final_md.read_text(encoding="utf-8")
    import re as _re
    refs = _re.findall(r"!\[[^\]]*\]\((images/[^)]+)\)", body)
    for ref in refs:
        # Strip the `images/` prefix to get the filename
        descriptor_png = ref.removeprefix("images/")
        target = images_dir / descriptor_png
        if not target.exists():
            return _rollback_and_fail(
                f"MD body references {ref} but file not present at {target}"
            )
    _log(f"[5/9] all {len(refs)} image refs resolve")

    # --- Step 6: Move final.md → DHF_AREA/<title_stem>.md ---
    try:
        if new_md_path.exists():
            return _rollback_and_fail(
                f"MD target already exists at {new_md_path}"
            )
        shutil.move(str(final_md), str(new_md_path))
        rollback.append((final_md, new_md_path))
        _log(f"[6/9] moved final.md → {new_md_path.name}")
    except Exception as e:
        return _rollback_and_fail(f"MD move failed: {e}")

    # --- Step 7: Verify MD arrived ---
    if not new_md_path.exists():
        return _rollback_and_fail(f"MD not present post-move: {new_md_path}")
    _log(f"[7/9] verified MD at {new_md_path}")

    # --- Step 8: Re-render parent README sentinels (non-blocking) ---
    repo_root = _find_repo_root(dhf_area_dir)
    if repo_root:
        render_script = (
            repo_root / ".claude/skills/medtech-docs/scripts/render-sentinels.py"
        )
        if render_script.exists():
            for parent in [dhf_area_dir, dhf_area_dir.parent]:
                readme = parent / "README.md"
                if readme.exists():
                    try:
                        subprocess.run(
                            ["python3", str(render_script), str(readme)],
                            capture_output=True, text=True, check=False, timeout=30,
                        )
                        _log(f"[8/9] re-rendered sentinels in {readme}")
                    except Exception as e:
                        _log(f"[8/9] sentinel re-render for {readme} failed (non-blocking): {e}")

    # --- Step 9: Clean up staging ---
    try:
        shutil.rmtree(staging_dir)
        _log(f"[9/9] removed staging {staging_dir}")
    except Exception as e:
        _log(f"[9/9] staging cleanup failed (non-blocking): {e}")

    _log("COMMIT SUCCESS")
    print(json.dumps({
        "result": "committed",
        "md_path": str(new_md_path),
        "formal_path": str(new_formal_path),
        "images_dir": str(images_dir) if has_images else None,
        "image_count": len(moved_images),
    }, indent=2))
    return 0


def _find_repo_root(start: Path) -> Path | None:
    p = start.resolve()
    while p != p.parent:
        if (p / ".git").exists():
            return p
        p = p.parent
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("staging_dir", help="Staging directory from adopt_v30.py")
    ap.add_argument("dhf_area_dir", help="Target DHF area (e.g., docs/project/dhfs/<dhf>/design-controls/architecture)")
    args = ap.parse_args()

    staging = Path(args.staging_dir).expanduser().resolve()
    dhf_area = Path(args.dhf_area_dir).expanduser().resolve()

    if not staging.exists():
        print(json.dumps({"error": f"staging not found: {staging}"}), file=sys.stderr)
        return 1

    return commit(staging, dhf_area)


if __name__ == "__main__":
    sys.exit(main())
