"""Conversion-fidelity gate (WUN-24) — hermetic capability tests.

Covers the deterministic verifier that catches silently *regenerated* prose in a
conversion (`scripts/verify_conversion_fidelity.py`, importable API) and the
Phase-7 script gate's built-in self-test. NOT covered here: an end-to-end
DOCX/PDF → markdown conversion through the adopt pipeline (`adopt_v30.py`
needs a doc-id registry and the project's conversion cache; pandoc is
available on this host but the pipeline is orchestrated per document).

Run: uv run --no-project --with pytest --with pyyaml -- pytest .claude/skills/docflow/tests -q
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SKILL / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


vcf = _load("verify_conversion_fidelity")

SOURCE = (
    "1 Scope. This document describes the software development plan for the infusion "
    "controller. It defines the life cycle model, the activities and deliverables for "
    "each phase, and the responsibilities of the development team. 2 Safety class. The "
    "software is assigned safety class C because a failure can contribute to a "
    "hazardous situation resulting in serious injury. 3 Planning. The plan shall be "
    "updated at each phase gate and reviewed by the software lead and quality "
    "engineering. Traceability is maintained from requirements through architecture "
    "to verification, and deviations are recorded in the deviation log with rationale."
)

FAITHFUL_MD = (
    "# Software Development Plan\n\n"
    "## 1 Scope\n\nThis document describes the software development plan for the infusion "
    "controller. It defines the life cycle model, the activities and deliverables for each "
    "phase, and the responsibilities of the development team.\n\n"
    "## 2 Safety class\n\nThe software is assigned safety class C because a failure can "
    "contribute to a hazardous situation resulting in serious injury.\n\n"
    "## 3 Planning\n\nThe plan shall be updated at each phase gate and reviewed by the software "
    "lead and quality engineering. Traceability is maintained from requirements through "
    "architecture to verification, and deviations are recorded in the deviation log with "
    "rationale.\n"
)

FABRICATED_PARAGRAPH = (
    "\n\n## 4 Worked example\n\nAs an illustration, consider a bolus request issued while a "
    "background infusion is running at the maximum permitted rate; the controller must "
    "first evaluate the cumulative dose against the hourly limit configured in the drug "
    "library, then apply the lockout interval, and only if both checks pass may the pump "
    "motor be commanded, with the event written to the audit log together with the "
    "clinician identifier, the timestamp, the requested volume, the delivered volume, and "
    "the resulting residual limit so that a later review can reconstruct the decision "
    "sequence exactly as the software evaluated it at the time of the request.\n"
)


def test_faithful_conversion_passes():
    res = vcf.assess(FAITHFUL_MD, SOURCE)
    assert res["status"] == "pass", res


def test_fabricated_passage_fails():
    res = vcf.assess(FAITHFUL_MD + FABRICATED_PARAGRAPH, SOURCE, span=25, fail=60)
    assert res["status"] == "fail", res
    assert res["longest"] >= 60
    assert res["spans"], "the invented span must be reported for adjudication"


def test_moderate_invention_warns_not_fails():
    md = FAITHFUL_MD + "\n\nNote: this section was restructured for readability during " \
                       "conversion and the headings were numbered by the editor for clarity " \
                       "and navigation across the document set.\n"
    res = vcf.assess(md, SOURCE, span=20, fail=80)
    assert res["status"] == "warn", res


def test_metadata_comments_are_ignored():
    md = "<!-- docflow: converted 2026-01-01 by the AI assistant from source.pdf -->\n" + FAITHFUL_MD
    assert vcf.assess(md, SOURCE)["status"] == "pass"


def test_longest_invented_runs_locates_the_span():
    src = vcf.norm_words(SOURCE)
    md = vcf.norm_words(vcf.strip_md_metadata(FAITHFUL_MD + FABRICATED_PARAGRAPH))
    runs = vcf.longest_invented_runs(md, src, n=8)
    assert runs and (runs[0][1] - runs[0][0]) >= 60


def test_unsupported_source_format_skips_not_fails(tmp_path):
    src = tmp_path / "source.docx"
    src.write_bytes(b"not a pdf")
    assert vcf.extract_source_words(str(src)) is None


def test_phase7_gate_self_test_exits_zero():
    proc = subprocess.run([sys.executable, str(SKILL / "scripts" / "validate_phase7.py"), "--self-test"],
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stdout + proc.stderr
