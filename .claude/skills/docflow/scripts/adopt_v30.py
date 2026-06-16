#!/usr/bin/env python3
"""
adopt_v30.py — deterministic adopt orchestrator (v30).

Replaces the long LLM-driven adopter agent for the `architecture` doc-type path.
Handles every deterministic step as Python subprocesses; emits a dispatch spec
for the parallel per-image agent fan-out that the calling Claude session
executes; then assembles, validates, and commits the result.

Sub-commands:
  plan <source_pdf> <dhf> <dhf_area>
        → runs classify_doc + extract_pdf + extract_title_version +
          splice_hyperlinks; writes staging/dispatch.json describing N agents
          to spawn. Returns wall-clock + counts.
  assemble <staging_dir>
        → stitches staging/fragments/*.md into final MD with frontmatter,
          DOC-CLASSIFY marker, image refs, and (spliced) body text. Writes
          staging/final.md.
  validate <staging_dir>
        → runs validate_phase7.py against staging/final.md. Exits 0/2.
  commit <staging_dir> <dhf_area_dir>
        → transactional move of final MD + images + source PDF rename.
  all <source_pdf> <dhf> <dhf_area>
        → runs plan → (skip agents — for dry-run / skeleton test) →
          assemble-stub → validate → report. Does NOT call commit.

Wall-clock targets on a 16-page SAD:
  plan:     ~1.5s  (extract_pdf ~0.7s + extract_title_version ~0.1s +
                   classify_doc ~0.05s + splice_hyperlinks ~0.3s + IO)
  assemble: ~0.5s
  validate: <0.1s
  commit:   <0.5s
Total deterministic: ~2.5s. LLM time is whatever the parallel agent fan-out
takes (target: ~2 min for 8 concurrent image agents vs 16+ min sequential).

Non-goals for v30.0:
  - Non-architecture doc types → fall through to the v29 adopter agent unchanged
  - Table interpretation (interpret_table.md) — architecture docs use
    table-md only; t-2/t-3/t-4/t-5/t-6 packs are for a later follow-up
  - Override-merge / downgrade detection — delegated to v29 adopter
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
DOCFLOW_DIR = SCRIPTS_DIR.parent
REPO_ROOT = DOCFLOW_DIR.parents[2]
ADOPT_VERSION = "v30"
BYPASS_MARKER = REPO_ROOT / ".state" / "docflow-active"


def _log(msg: str):
    print(f"[adopt_v30] {msg}", file=sys.stderr)


def _acquire_bypass() -> bool:
    """
    Touch the .state/docflow-active marker so our subprocess calls to
    pdfinfo/pdftotext/pdfimages aren't blocked by block-direct-conversion.sh
    if the pipeline happens to shell them out. Returns True if WE created the
    marker (and should remove it on exit), False if it already existed (user
    or a parent docflow run owns it).
    """
    BYPASS_MARKER.parent.mkdir(parents=True, exist_ok=True)
    if BYPASS_MARKER.exists():
        return False  # someone else set it — don't remove on exit
    BYPASS_MARKER.touch()
    return True


def _release_bypass(we_set_it: bool):
    """Remove the marker only if WE set it (symmetric with _acquire_bypass)."""
    if we_set_it and BYPASS_MARKER.exists():
        try:
            BYPASS_MARKER.unlink()
        except OSError as e:
            _log(f"warn: could not remove bypass marker {BYPASS_MARKER}: {e}")


def _run_json(cmd: list[str]) -> dict:
    """Run a subprocess, parse stdout as JSON."""
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode not in (0, 1):  # our scripts use 0=ok, 1=partial-ok
        raise RuntimeError(f"{cmd[0]} failed (exit {r.returncode}): {r.stderr}")
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"{cmd[0]} produced non-JSON output: {r.stdout[:200]}") from e


# --- plan ---

def cmd_plan(source_pdf: Path, dhf: str, dhf_area: str, staging_dir: Path,
             doc_version_override: Optional[str] = None) -> dict:
    """
    Run every deterministic extraction + classification step. Produce a
    dispatch spec for the per-image agent fan-out.
    """
    t0 = time.time()
    staging_dir.mkdir(parents=True, exist_ok=True)

    # 1. classify_doc
    cls = _run_json([
        "python3", str(SCRIPTS_DIR / "classify_doc.py"),
        str(source_pdf),
    ])
    doc_type = cls["doc_type"]
    _log(f"classify_doc → {doc_type} (confidence={cls['confidence']}, basis={cls['basis']})")

    if doc_type not in ("architecture", "requirement"):
        # v30.0 scope: architecture + requirement paths. Everything else
        # falls through to the v29 adopter.
        return {
            "result": "fall-through-to-v29",
            "reason": f"doc_type={doc_type} not in v30.0 scope; use v29 adopter",
            "classify": cls,
        }

    # 2. extract_title_version
    args = ["python3", str(SCRIPTS_DIR / "extract_title_version.py"), str(source_pdf)]
    if doc_version_override:
        args.extend(["--doc-version", doc_version_override])
    tv = _run_json(args)
    if not tv.get("title"):
        return {"result": "fail", "reason": "title extraction failed", "title_version": tv}
    _log(f"extract_title_version → title='{tv['title']}' doc_version={tv['doc_version']}")

    # 3. extract_pdf (writes manifest + images + page text to staging)
    cmd = [
        "python3", str(SCRIPTS_DIR / "extract_pdf.py"),
        "--staging-dir", str(staging_dir),
        str(source_pdf),
    ]
    # extract_pdf.py expects argument order: [flags] pdf_path
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return {"result": "fail", "reason": f"extract_pdf failed: {r.stderr}"}
    manifest = json.loads(r.stdout)
    summary = manifest.get("image_summary", {})
    _log(
        f"extract_pdf → {manifest['page_count']} pages, "
        f"{summary.get('extracted_total', 0)} raw images, "
        f"{summary.get('content_count', 0)} content, "
        f"{summary.get('decorative_count', 0)} decorative, "
        f"{summary.get('duplicate_count', 0)} duplicate"
    )

    # 4. splice_hyperlinks (rewrites the page text cache in-place so the
    # assembled body carries markdown links). The v29 script expects a
    # single cache path; we pass staging/all.txt.
    cache_file = staging_dir / "all.txt"
    splice_log = {"skipped": "cache file not produced"}
    if cache_file.exists():
        sp = subprocess.run(
            [
                "python3", str(SCRIPTS_DIR / "splice_hyperlinks.py"),
                str(source_pdf), str(cache_file), "pdf",
            ],
            capture_output=True, text=True,
        )
        splice_log = {"stdout": sp.stdout.strip(), "returncode": sp.returncode}
        _log(f"splice_hyperlinks → {sp.stdout.strip()[:120]}")

    title_stem = tv["title"].replace("/", "").replace(":", "").strip()
    image_ref_prefix = "images/"

    # --- Branch on doc_type ---
    if doc_type == "requirement":
        # Requirement docs: single body-structurer agent that emits the R1
        # v22 per-requirement shape. Zero image-agent fan-out (SRS docs
        # rarely have content images; if present, they're nearly always
        # type-e ui-capture handled by the body structurer's placeholder).
        body_structurer = {
            "agent": "agents/structure_requirement_body.md",
            "spliced_cache_path": str(cache_file),
            "manifest_path": str(staging_dir / "manifest.json"),
            "title": tv["title"],
            "doc_type_pack": "references/doc-type-packs/requirement.md",
            "classification_taxonomy": "references/classification-taxonomy.md",
            "image_ref_prefix": image_ref_prefix,
            "descriptors_by_order": [],
            "output_path": str(staging_dir / "body.md"),
        }
        (staging_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        (staging_dir / "fragments").mkdir(exist_ok=True)

        dispatch = {
            "adopt_version": ADOPT_VERSION,
            "doc_type": doc_type,
            "dhf": dhf,
            "dhf_area": dhf_area,
            "source_pdf": str(source_pdf),
            "title": tv["title"],
            "title_stem": title_stem,
            "doc_version": tv["doc_version"],
            "doc_version_raw": tv["doc_version_raw"],
            "release_version": tv["release_version"],
            "staging_dir": str(staging_dir),
            "image_ref_prefix": image_ref_prefix,
            "body_structurer": body_structurer,
            "agents": [],
            "splice_hyperlinks": splice_log,
            "classify": cls,
            "wall_clock_s": round(time.time() - t0, 2),
        }
        (staging_dir / "dispatch.json").write_text(json.dumps(dispatch, indent=2))
        _log(
            f"plan complete (requirement path): 1 body-structurer, 0 image agents, "
            f"wall-clock {dispatch['wall_clock_s']}s"
        )
        return dispatch

    # --- Architecture path ---
    # Build dispatch spec: one entry per content image.
    content_images = manifest.get("content_images") or [
        img for img in manifest["images"]
        if img.get("classification_hint") == "content" and not img.get("is_duplicate")
    ]

    dispatch_entries: list[dict] = []
    for idx, img in enumerate(content_images):
        descriptor = _descriptor_for_image(img, idx, title_stem)
        page_num = img.get("page", 0)
        page_text = _page_text(staging_dir, page_num)
        dispatch_entries.append({
            "agent": "agents/interpret_image.md",
            "image_path": img.get("final_path") or img.get("raw_filename"),
            "descriptor": descriptor,
            "page_num": page_num,
            "page_text_snippet": page_text[:1500],
            "doc_type_pack": "references/doc-type-packs/architecture.md",
            "mermaid_packs": [
                "references/mermaid-rule-packs/shared-fidelity.md",
                "references/mermaid-rule-packs/type-a-flow.md",
                "references/mermaid-rule-packs/type-b-logical.md",
                "references/mermaid-rule-packs/type-c-component.md",
                "references/mermaid-rule-packs/type-e-ui-capture.md",
            ],
            "image_ref_path": f"{image_ref_prefix}{descriptor}.png",
            "output_fragment": str(staging_dir / "fragments" / f"image-{descriptor}.md"),
        })

    (staging_dir / "fragments").mkdir(exist_ok=True)

    # 6. Body-structurer dispatch — one agent call, produces staging/body.md
    body_structurer = {
        "agent": "agents/structure_body.md",
        "spliced_cache_path": str(cache_file),
        "manifest_path": str(staging_dir / "manifest.json"),
        "title": tv["title"],
        "doc_type_pack": "references/doc-type-packs/architecture.md",
        "image_ref_prefix": image_ref_prefix,
        "descriptors_by_order": [
            {"descriptor": e["descriptor"], "page_num": e["page_num"]}
            for e in dispatch_entries
        ],
        "output_path": str(staging_dir / "body.md"),
    }

    # Persist the manifest so the structure_body agent can read it
    (staging_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    dispatch = {
        "adopt_version": ADOPT_VERSION,
        "doc_type": doc_type,
        "dhf": dhf,
        "dhf_area": dhf_area,
        "source_pdf": str(source_pdf),
        "title": tv["title"],
        "title_stem": title_stem,
        "doc_version": tv["doc_version"],
        "doc_version_raw": tv["doc_version_raw"],
        "release_version": tv["release_version"],
        "staging_dir": str(staging_dir),
        "image_ref_prefix": image_ref_prefix,
        "body_structurer": body_structurer,
        "agents": dispatch_entries,
        "splice_hyperlinks": splice_log,
        "classify": cls,
        "wall_clock_s": round(time.time() - t0, 2),
    }

    (staging_dir / "dispatch.json").write_text(json.dumps(dispatch, indent=2))
    _log(
        f"plan complete: 1 body-structurer + {len(dispatch_entries)} image agent(s) to spawn "
        f"(total {1 + len(dispatch_entries)} parallel agent calls), "
        f"wall-clock {dispatch['wall_clock_s']}s"
    )
    return dispatch


def _descriptor_for_image(img: dict, idx: int, title_stem: str) -> str:
    """Deterministic descriptor for an image based on title + page + index."""
    title_slug = re.sub(r"[^a-z0-9]+", "-", title_stem.lower()).strip("-")
    # Short prefix to keep filenames reasonable
    short = "-".join(title_slug.split("-")[:4])
    page = img.get("page", 0)
    return f"{short}_p{page:02d}-{idx + 1:02d}"


def _page_text(staging_dir: Path, page_num: int) -> str:
    page_file = staging_dir / "pages" / f"page-{page_num:03d}.txt"
    if page_file.exists():
        return page_file.read_text(encoding="utf-8", errors="ignore")
    return ""


# --- assemble ---

def cmd_assemble(staging_dir: Path) -> dict:
    """
    Stitch the per-image fragments plus the spliced body text into a final MD
    with frontmatter + DOC-CLASSIFY marker + interleaved body.
    """
    t0 = time.time()
    dispatch = json.loads((staging_dir / "dispatch.json").read_text())
    fragments_dir = staging_dir / "fragments"

    # Collect fragments in dispatch order
    fragments: dict[str, str] = {}
    missing: list[str] = []
    for entry in dispatch["agents"]:
        frag_path = Path(entry["output_fragment"])
        if not frag_path.exists():
            missing.append(entry["descriptor"])
            continue
        fragments[entry["descriptor"]] = frag_path.read_text(encoding="utf-8").strip()

    if missing:
        _log(f"assemble: {len(missing)} fragments missing — writing stub placeholders")
        for descriptor in missing:
            fragments[descriptor] = (
                f'<!-- F11-CLASSIFY: descriptor="{descriptor}" type="review" '
                f'mermaid-emit="skip" skip-reason="ambiguous-needs-review" -->\n'
                f'%% REVIEW: FRAGMENT NOT PRODUCED BY AGENT — dispatch this descriptor to '
                f'interpret_image.md manually. %%\n\n'
                f'![Image fragment not yet produced]({dispatch["image_ref_prefix"]}{descriptor}.png)\n'
            )

    # Body comes from structure_body agent's output (staging/body.md). If the
    # agent hasn't run, fall back to flat all.txt + appended fragments so the
    # skeleton smoke test still produces SOMETHING — but validate_phase7 will
    # flag missing structure.
    body_path = staging_dir / "body.md"
    structured = body_path.exists()
    if structured:
        body = body_path.read_text(encoding="utf-8")
        # Substitute each IMAGE-PLACEHOLDER marker with its corresponding fragment
        def _sub(m):
            attrs = dict(re.findall(r'(\w[\w-]*)="([^"]*)"', m.group(0)))
            d = attrs.get("descriptor", "")
            return fragments.get(d, m.group(0))
        body = re.sub(
            r"<!--\s*IMAGE-PLACEHOLDER:\s*[^>]+?\s*-->",
            _sub,
            body,
        )
    else:
        _log("assemble: staging/body.md missing — structure_body agent did not run; "
             "falling back to flat all.txt + appended fragments")
        all_txt = (staging_dir / "all.txt").read_text(encoding="utf-8", errors="ignore")
        image_blocks: list[str] = [
            f"\n<!-- source page {entry['page_num']} -->\n{fragments[entry['descriptor']]}\n"
            for entry in dispatch["agents"]
        ]
        body = (
            all_txt
            + "\n\n## Image supplements (appended by adopt_v30 fallback — structure_body did not run)\n"
            + "\n".join(image_blocks)
        )

    # Write the assembled body to staging so enrich_frontmatter.py can read it
    # for its hyperlink/table/form-field counts + references resolution.
    body_staging = staging_dir / "body-assembled.md"
    body_staging.write_text(body, encoding="utf-8")

    # Run enrich_frontmatter to build the full v30-parity frontmatter dict
    # (version_lineage, source_formal, template_of, authored_per, filings,
    # references, dhf_role, conversion_history, counts — ports v29 Phase 5a/b/c/d).
    try:
        from importlib import util as _iu
        spec = _iu.spec_from_file_location("enrich_frontmatter", SCRIPTS_DIR / "enrich_frontmatter.py")
        ef = _iu.module_from_spec(spec)
        spec.loader.exec_module(ef)
        fm_dict = ef.enrich_with_body(staging_dir, REPO_ROOT, body)
        fm_yaml = ef.dump_yaml(fm_dict)
    except Exception as e:
        _log(f"enrich_frontmatter failed ({e}); falling back to minimal frontmatter")
        # Minimal fallback (same as pre-enrichment shape)
        all_links = re.findall(r"(?<!\!)\[[^\]]+\]\([^)]+\)", body)
        fm_yaml = "\n".join([
            f'title: "{dispatch["title"]}"',
            f'doc_type: "{dispatch["doc_type"]}"',
            f'dhf: "{dispatch["dhf"]}"',
            f'dhf_area: "{dispatch["dhf_area"]}"',
            f'status: "draft"',
            f'doc_version: "{dispatch["doc_version"]}"',
            f'has_hyperlinks: {"true" if all_links else "false"}',
            f'hyperlink_count: {len(all_links)}',
            f'has_images: {"true" if len(dispatch["agents"]) else "false"}',
            f'image_count: {len(dispatch["agents"])}',
        ])

    # Doc-type-specific aggregate injection (requirement → `requirements:` map)
    doc_type = dispatch.get("doc_type", "architecture")
    if doc_type == "requirement":
        try:
            import sys as _sys
            from importlib import util as _iu
            spec = _iu.spec_from_file_location(
                "infer_requirement_metadata",
                SCRIPTS_DIR / "infer_requirement_metadata.py",
            )
            irm = _iu.module_from_spec(spec)
            # Register in sys.modules BEFORE exec_module so @dataclass can
            # resolve cls.__module__ (Python 3.14 requirement).
            _sys.modules[spec.name] = irm
            spec.loader.exec_module(irm)
            blocks = irm.parse_blocks(body)
            agg = irm.aggregate(blocks)
            overlay = "requirements:\n" + irm._dump_yaml(agg, indent=1)
            fm_yaml = fm_yaml.rstrip() + "\n\n# --- Requirements aggregate ---\n" + overlay
            _log(
                f"infer_requirement_metadata → {agg['count']} requirements, "
                f"{sum(agg['criticality'].values())} criticality rows, "
                f"traces_to resolved={agg['traces_to']['resolved']}/"
                f"unresolved={agg['traces_to']['unresolved']}"
            )
        except Exception as e:
            _log(f"infer_requirement_metadata failed ({e}); requirements aggregate omitted")

    pack_path = f"references/doc-type-packs/{doc_type}.md"
    doc_classify = (
        f'<!-- DOC-CLASSIFY: doc_type="{doc_type}" '
        f'pack="{pack_path}" -->\n'
    )

    final = "---\n" + fm_yaml + "\n---\n\n" + doc_classify + "\n" + body
    final_path = staging_dir / "final.md"
    final_path.write_text(final, encoding="utf-8")
    wall = round(time.time() - t0, 2)
    _log(f"assemble → {final_path} ({len(body)} chars body, {len(dispatch['agents'])} images, {wall}s)")
    return {"final_path": str(final_path), "wall_clock_s": wall, "missing_fragments": missing}


# --- validate ---

def cmd_validate(staging_dir: Path, source_path: Optional[Path] = None) -> int:
    final_md = staging_dir / "final.md"
    if not final_md.exists():
        print(json.dumps({"error": f"final.md not found at {final_md}"}), file=sys.stderr)
        return 2

    # Compute K + K_anchors from the spliced cache so the link-count floor
    # check is anchor-aware. Saves the user from passing --expected-* flags.
    cache_file = staging_dir / "all.txt"
    args = ["python3", str(SCRIPTS_DIR / "validate_phase7.py"), str(final_md)]
    # Prose-fidelity check (PDF sources only — flags converted prose absent from
    # the source). validate_phase7 returns `prose_fidelity: warn` + spans for
    # adjudication; the adopter agent (adopter.md Phase 7) spawns the
    # fidelity-adjudicator on a warn before committing.
    if source_path and source_path.exists() and source_path.suffix.lower() == ".pdf":
        args.extend(["--source", str(source_path)])
    if cache_file.exists():
        cache = cache_file.read_text(encoding="utf-8", errors="ignore")
        link_matches = [
            m for m in re.finditer(r"\[[^\]]+\]\([^)]+\)", cache)
            if m.start() == 0 or cache[m.start() - 1] != "!"
        ]
        k_total = len(link_matches)
        k_anchors = sum(1 for m in link_matches if "](#" in m.group(0))
        args.extend([
            "--expected-hyperlink-count", str(k_total),
            "--expected-anchor-count", str(k_anchors),
        ])
        _log(f"validate: computed K={k_total} (K_anchors={k_anchors}) from spliced cache")

    r = subprocess.run(args, capture_output=True, text=True)
    print(r.stdout)
    return r.returncode


# --- commit (stub — full impl lives in a future commit_atomic.py) ---

def cmd_commit(staging_dir: Path, dhf_area_dir: Path) -> int:
    """Delegate transactional commit to `commit_atomic.py`."""
    r = subprocess.run(
        [
            "python3", str(SCRIPTS_DIR / "commit_atomic.py"),
            str(staging_dir), str(dhf_area_dir),
        ],
        text=True,
    )
    return r.returncode


# --- all (skeleton smoke path) ---

def cmd_all(source_pdf: Path, dhf: str, dhf_area: str, staging_dir: Path) -> int:
    plan = cmd_plan(source_pdf, dhf, dhf_area, staging_dir)
    if plan.get("result") == "fall-through-to-v29":
        print(json.dumps(plan, indent=2))
        return 3
    if plan.get("result") == "fail":
        print(json.dumps(plan, indent=2), file=sys.stderr)
        return 2

    _log("all: skipping agent fan-out (SKILL.md would spawn agents here)")
    a = cmd_assemble(staging_dir)
    print(json.dumps({"plan_wall_s": plan["wall_clock_s"], "assemble": a}, indent=2))
    return cmd_validate(staging_dir, source_pdf)


# --- main ---

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_plan = sub.add_parser("plan")
    p_plan.add_argument("source_pdf")
    p_plan.add_argument("dhf")
    p_plan.add_argument("dhf_area")
    p_plan.add_argument("--staging-dir", default="/tmp/docflow-v30-plan")
    p_plan.add_argument("--doc-version", dest="override", default=None)

    p_asm = sub.add_parser("assemble")
    p_asm.add_argument("staging_dir")

    p_val = sub.add_parser("validate")
    p_val.add_argument("staging_dir")
    p_val.add_argument("--source", default=None,
                       help="Source PDF for the prose-fidelity check (optional)")

    p_com = sub.add_parser("commit")
    p_com.add_argument("staging_dir")
    p_com.add_argument("dhf_area_dir")

    p_all = sub.add_parser("all")
    p_all.add_argument("source_pdf")
    p_all.add_argument("dhf")
    p_all.add_argument("dhf_area")
    p_all.add_argument("--staging-dir", default="/tmp/docflow-v30-all")

    args = ap.parse_args()

    # Self-manage the `.state/docflow-active` marker so subprocess calls to
    # pdfinfo/pdftotext/pdfimages aren't blocked by block-direct-conversion.sh.
    # `assemble` + `validate` don't shell any gated verbs, but we acquire for
    # every sub-command anyway for uniformity. The marker is idempotent: if
    # another docflow run already set it, we leave it alone on exit.
    we_set_it = _acquire_bypass()
    try:
        if args.cmd == "plan":
            staging = Path(args.staging_dir).expanduser().resolve()
            r = cmd_plan(Path(args.source_pdf).resolve(), args.dhf, args.dhf_area, staging, args.override)
            print(json.dumps(r, indent=2))
            return 0 if r.get("result") != "fail" else 2
        if args.cmd == "assemble":
            r = cmd_assemble(Path(args.staging_dir).resolve())
            print(json.dumps(r, indent=2))
            return 0
        if args.cmd == "validate":
            src = Path(args.source).resolve() if args.source else None
            return cmd_validate(Path(args.staging_dir).resolve(), src)
        if args.cmd == "commit":
            return cmd_commit(Path(args.staging_dir).resolve(), Path(args.dhf_area_dir).resolve())
        if args.cmd == "all":
            staging = Path(args.staging_dir).expanduser().resolve()
            return cmd_all(Path(args.source_pdf).resolve(), args.dhf, args.dhf_area, staging)
        return 1
    finally:
        _release_bypass(we_set_it)


if __name__ == "__main__":
    sys.exit(main())
