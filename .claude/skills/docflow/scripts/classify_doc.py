#!/usr/bin/env python3
"""
classify_doc.py — Doc-type classifier for /docflow adopt orchestrator.

Inspects a source file's path + filename and returns the matching doc-type pack
to govern the adopt run. Validated against the project's existing 122 adopted
DHF MDs (frontmatter doc_type field is the ground truth).

Three-tier classification (priority order — first match wins):
  Tier 1: definitive path matches under docs/internal/source/{Forms,SOPs,...}/
  Tier 2: path + filename rules for DHF folders (some folders are heterogeneous)
  Tier 3: filename-only keyword fallback for ad-hoc paths

Doc-type vocabulary (matches existing project frontmatter usage):
  architecture, cybersecurity, vnv, plan, report, form-instance, requirement,
  assessment, tool-validation, hazard-analysis, trace-matrix, user-need, form,
  phase-closure-review, fmea, other (fallback), qms-sop, qms-wi, qms-policy,
  qms-standard, qms-form

Usage:
  python3 classify_doc.py <source-file-path>
  python3 classify_doc.py --self-test    # validate against existing adopted MDs

Exit codes:
  0  classification succeeded
  2  source path does not exist
  3  --self-test mode and accuracy < 0.95
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Tier 1 — QMS source folder definitive matches (paths under docs/internal/source/)
# These map 1:1 because the source folder convention is enforced.
# ---------------------------------------------------------------------------
_QMS_PATH_RULES = [
    ("docs/internal/source/Forms/", "qms-form", "high", "path-internal-forms"),
    ("docs/internal/source/SOPs/", "qms-sop", "high", "path-internal-sops"),
    ("docs/internal/source/Work Instructions/", "qms-wi", "high", "path-internal-wis"),
    ("docs/internal/source/Policies/", "qms-policy", "high", "path-internal-policies"),
    ("docs/internal/source/Standards/", "qms-standard", "high", "path-internal-standards"),
]

# ---------------------------------------------------------------------------
# Tier 2 — DHF folder path matches (homogeneous folders → single type)
# Empirically validated: these folders contain ONLY this doc_type in the
# project's existing 122 adopted MDs. Match is "high" confidence.
# ---------------------------------------------------------------------------
_DHF_HOMOGENEOUS_PATH_RULES = [
    ("/cybersecurity/", "cybersecurity", "high", "path-dhf-cybersecurity"),
    ("/design-controls/architecture/", "architecture", "high", "path-dhf-architecture"),
    ("/design-controls/requirements/", "requirement", "high", "path-dhf-requirements"),
    ("/design-controls/user-needs/", "user-need", "high", "path-dhf-user-needs"),
    ("/design-controls/vnv/", "vnv", "high", "path-dhf-vnv"),
    ("/clinical/", "clinical-doc", "high", "path-dhf-clinical"),
    ("/postmarket/", "clinical-doc", "medium", "path-dhf-postmarket-fallback"),
]

# ---------------------------------------------------------------------------
# Tier 2b — DHF folder + filename pattern rules (heterogeneous folders)
# These folders contain multiple doc types; filename pattern picks the right one.
# Format: (path_segment, [(filename_regex, doc_type, confidence, basis), ...], default_type)
# Default_type fires when the path matches but no filename pattern does (medium confidence).
# ---------------------------------------------------------------------------
_DHF_PATH_PLUS_FILENAME_RULES = [
    (
        "/design-controls/release-closure/",
        [
            (r"\b(SWR|Software Release|SVI|Software Version Identification|SOD|Software Open Defects)\b", "report", "high", "path+name-release-report"),
            (r"\bPhase\s*\d+\s*Closure", "phase-closure-review", "high", "path+name-phase-closure"),
        ],
        ("report", "medium", "path-dhf-release-closure-default"),
    ),
    (
        "/design-controls/plans/",
        [
            # FORM-XXX-prefixed plans are filled-in form instances of the plan template (e.g., FORM-000137230 - DDP)
            (r"^(FORM|FRM)-\d+", "form-instance", "high", "path+name-plan-form-prefix"),
            # Otherwise, plan-keyword filenames are plans
            (r"\b(SDP|DDP|D&D Plan|Software Development Plan|Software Deployment Plan|Configuration Management Plan|Verification Plan|Validation Plan)\b", "plan", "high", "path+name-plan"),
        ],
        ("plan", "medium", "path-dhf-plans-default"),
    ),
    (
        "/design-controls/tool-validation/c-arm-video-stream-simulator/",
        # This subfolder contains blank template artifacts adopted as evidence; existing project types them as `form`
        [],
        ("form", "medium", "path-dhf-tool-validation-cavss-default"),
    ),
    (
        "/design-controls/tool-validation/",
        # All docs in tool-validation/ are tool-validation evidence — the "Form" in their names refers to
        # the validation form filled in for the tool, not to a separate doc category.
        # EXCEPT: inventory lists and OTS (off-the-shelf) component records are filed as form-instance
        # because they are filled-in records of the SDLC inventory form template.
        [
            (r"\b(Inventory List|OTS|Off-the-Shelf|Software Tools Inventory)\b", "form-instance", "high", "path+name-tool-inventory"),
            (r"\b(Tool Validation Plan|Tool Validation Report)\b", "tool-validation", "high", "path+name-tool-validation"),
        ],
        ("tool-validation", "medium", "path-dhf-tool-validation-default"),
    ),
    (
        "/design-controls/trace-matrix/",
        # Empirically, docs in this folder are filled-in trace matrix form instances, not free-form trace matrix docs.
        # The project's `trace-matrix` doc_type is reserved for risk-management trace matrices.
        [
            (r"\b(Trace Matrix Form|Traceability Form)\b", "form-instance", "high", "path+name-trace-form-explicit"),
        ],
        ("form-instance", "medium", "path-dhf-trace-matrix-default"),
    ),
    (
        "/risk-management/",
        [
            (r"\bRMP\b|\bRisk Management Plan\b", "plan", "high", "path+name-risk-plan"),
            (r"\bFMEA\b|\bdFMEA\b|\bFailure Mode and Effects\b", "fmea", "high", "path+name-fmea"),
            (r"\bHazard Analysis\b|\bHazard Identification\b", "hazard-analysis", "high", "path+name-hazard-analysis"),
            (r"\bTrace Matrix\b|\bTraceability\b", "trace-matrix", "high", "path+name-risk-trace"),
            (r"\b(Risk Assessment|Risk Analysis Report|Master Harms|Harms List|Residual Risk|Benefit-Risk)\b", "assessment", "high", "path+name-risk-assessment"),
        ],
        ("assessment", "medium", "path-dhf-risk-default"),
    ),
]

# ---------------------------------------------------------------------------
# Tier 3 — filename-only keyword fallback (when no path rule fires)
# Fires for ad-hoc paths, dropped-in formal not yet under area folder, etc.
# ---------------------------------------------------------------------------
_FILENAME_KEYWORD_RULES = [
    (r"\b(SAD|SDD|System Architecture|Software Architecture|Detailed Design)\b", "architecture", "high", "filename-architecture"),
    (r"\b(SRS|FRS|NFR|System Requirements|Software Requirements|Functional Requirements|Non-?Functional Requirements)\b", "requirement", "high", "filename-requirement"),
    (r"\b(URS|User Requirements|User Needs)\b", "user-need", "high", "filename-user-need"),
    (r"\b(Trace Matrix|RTM|Traceability Matrix)\b", "trace-matrix", "high", "filename-trace-matrix"),
    (r"\bFMEA\b|\bdFMEA\b", "fmea", "high", "filename-fmea"),
    (r"\bHazard Analysis\b", "hazard-analysis", "high", "filename-hazard-analysis"),
    (r"\b(RMP|Risk Management Plan)\b", "plan", "high", "filename-rmp"),
    (r"\b(Risk Assessment|Risk Analysis Report)\b", "assessment", "high", "filename-risk-assessment"),
    (r"\b(Threat Model|SBOM|CSRA|PSRA|Cybersecurity|Vulnerability Assessment|Software Bill of Materials)\b", "cybersecurity", "high", "filename-cybersecurity"),
    (r"\b(Test Protocol|Test Plan|VnV|V&V Plan|Verification Protocol|Validation Protocol|Software Test|Reliability Testing)\b", "vnv", "high", "filename-vnv"),
    (r"\b(Tool Validation|Tool Qualification)\b", "tool-validation", "high", "filename-tool-validation"),
    (r"\b(SDP|DDP|D&D Plan|Software Development Plan|Software Deployment Plan|Configuration Management Plan)\b", "plan", "high", "filename-plan"),
    (r"\b(SWR|Software Release|SVI|Software Version Identification|SOD|Software Open Defects)\b", "report", "high", "filename-report"),
    (r"\bPhase\s*\d+\s*Closure", "phase-closure-review", "high", "filename-phase-closure"),
    (r"\b(CER|Clinical Evaluation|Clinical Investigation|Literature Review)\b", "clinical-doc", "high", "filename-clinical"),
    # QMS doc-id fallback for adopted DHF copies
    (r"\bSOP-\d+", "qms-sop", "medium", "filename-sop-id"),
    (r"\b(FORM|FRM)-\d+", "qms-form", "medium", "filename-form-id"),
    (r"\bWI-\d+", "qms-wi", "medium", "filename-wi-id"),
    (r"\bPOL-\d+", "qms-policy", "medium", "filename-pol-id"),
    (r"\bQSD-\d+", "qms-standard", "medium", "filename-standard-id"),
    # Last-resort form/template fallback
    (r"\bForm\b|\bWorksheet\b|\bTemplate\b", "form-instance", "low", "filename-form-fallback"),
]


def classify(source_path: str) -> dict:
    """Classify a source file. Returns {doc_type, pack, confidence, basis, source_path}."""
    p = Path(source_path)
    posix = p.as_posix()
    stem = p.stem

    # Tier 1: QMS source folders
    for needle, doc_type, conf, basis in _QMS_PATH_RULES:
        if needle in posix:
            return _result(source_path, doc_type, conf, basis)

    # Tier 2: DHF homogeneous folders
    for needle, doc_type, conf, basis in _DHF_HOMOGENEOUS_PATH_RULES:
        if needle in posix:
            return _result(source_path, doc_type, conf, basis)

    # Tier 2b: DHF heterogeneous folders (path + filename pattern)
    for path_segment, name_rules, default in _DHF_PATH_PLUS_FILENAME_RULES:
        if path_segment in posix:
            for pattern, doc_type, conf, basis in name_rules:
                if re.search(pattern, stem, re.IGNORECASE):
                    return _result(source_path, doc_type, conf, basis)
            # Path matched but no filename pattern did → use folder default
            default_type, default_conf, default_basis = default
            return _result(source_path, default_type, default_conf, default_basis)

    # Tier 3: filename keyword fallback
    for pattern, doc_type, conf, basis in _FILENAME_KEYWORD_RULES:
        if re.search(pattern, stem, re.IGNORECASE):
            return _result(source_path, doc_type, conf, basis)

    # No match — flag for agent escalation
    return _result(source_path, "other", "low", "no-rule-match")


def _result(source_path: str, doc_type: str, confidence: str, basis: str) -> dict:
    return {
        "source_path": source_path,
        "doc_type": doc_type,
        "pack": f"references/doc-type-packs/{doc_type}.md",
        "confidence": confidence,
        "basis": basis,
    }


# ---------------------------------------------------------------------------
# Self-test mode
# ---------------------------------------------------------------------------

def self_test(project_root: Path) -> int:
    """Walk every adopted MD, classify its source_formal, compare to frontmatter doc_type."""
    import yaml

    dhfs_root = project_root / "docs" / "project" / "dhfs"
    if not dhfs_root.is_dir():
        print(f"[self-test] dhfs root not found at {dhfs_root}", file=sys.stderr)
        return 2

    total = 0
    agreed = 0
    high_conf_total = 0
    high_conf_agreed = 0
    disagreements: list[tuple[str, str, str, str, str]] = []
    by_basis_pass: dict[str, int] = {}
    by_basis_fail: dict[str, int] = {}

    for md in dhfs_root.rglob("*.md"):
        if md.name == "README.md":
            continue

        text = md.read_text(encoding="utf-8", errors="ignore")
        if not text.startswith("---\n"):
            continue
        end = text.find("\n---\n", 4)
        if end < 0:
            continue
        try:
            fm = yaml.safe_load(text[4:end])
        except yaml.YAMLError:
            continue
        if not isinstance(fm, dict):
            continue

        expected = fm.get("doc_type")
        source_formal = fm.get("source_formal")
        if not expected or not source_formal:
            continue
        source_path = (md.parent / source_formal).resolve()
        if not source_path.exists():
            continue

        result = classify(str(source_path))
        got = result["doc_type"]
        conf = result["confidence"]
        basis = result["basis"]

        total += 1
        ok = (got == expected)
        if ok:
            agreed += 1
            by_basis_pass[basis] = by_basis_pass.get(basis, 0) + 1
        else:
            disagreements.append((str(md.relative_to(project_root)), expected, got, conf, basis))
            by_basis_fail[basis] = by_basis_fail.get(basis, 0) + 1

        if conf == "high":
            high_conf_total += 1
            if ok:
                high_conf_agreed += 1

    if total == 0:
        print("[self-test] No adopted MDs found", file=sys.stderr)
        return 2

    overall = agreed / total
    high_conf = (high_conf_agreed / high_conf_total) if high_conf_total else 1.0

    print(f"[self-test] Total adopted MDs evaluated: {total}")
    print(f"[self-test] Overall agreement: {agreed}/{total} = {overall:.1%}")
    print(f"[self-test] High-confidence agreement: {high_conf_agreed}/{high_conf_total} = {high_conf:.1%}")

    if disagreements:
        print(f"\n[self-test] Disagreements ({len(disagreements)}):")
        for md_path, expected, got, conf, basis in disagreements[:30]:
            print(f"  expected={expected:<22} got={got:<22} conf={conf:<6} basis={basis}")
            print(f"    {md_path}")
        if len(disagreements) > 30:
            print(f"  ... and {len(disagreements) - 30} more")

    print(f"\n[self-test] Pass rates by classification basis:")
    all_bases = sorted(set(by_basis_pass) | set(by_basis_fail))
    for basis in all_bases:
        p, f = by_basis_pass.get(basis, 0), by_basis_fail.get(basis, 0)
        print(f"  {basis:<40} pass {p:>3} / fail {f:>3}")

    if overall >= 0.95:
        print(f"\n[self-test] PASS (>= 95% target)")
        return 0
    else:
        print(f"\n[self-test] FAIL (target 95%, got {overall:.1%})")
        return 3


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("source_path", nargs="?", help="Path to the source file to classify")
    parser.add_argument("--self-test", action="store_true", help="Validate against existing adopted MDs")
    parser.add_argument("--project-root", default=None, help="Project root for self-test (default: auto-detect)")
    args = parser.parse_args(argv)

    if args.self_test:
        if args.project_root:
            root = Path(args.project_root).resolve()
        else:
            root = Path(__file__).resolve().parents[4]
        return self_test(root)

    if not args.source_path:
        parser.error("source_path is required (or use --self-test)")

    p = Path(args.source_path)
    if not p.exists():
        print(f"Source path does not exist: {args.source_path}", file=sys.stderr)
        return 2

    print(json.dumps(classify(args.source_path), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
