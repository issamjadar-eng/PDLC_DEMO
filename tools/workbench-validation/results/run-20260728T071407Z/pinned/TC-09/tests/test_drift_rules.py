"""Unit tests for lib/drift_rules.py.

Synthetic-fixture tests covering every implemented rule with at least one
clean (no-violation) case and one drift case. All fixtures use generic
placeholder IDs (DEMO-N, DI-N, UN-N) — no project-specific names.

Tests are READ-ONLY. They never touch Jira/Confluence MCPs, never read the
live ``_jira/`` mirror, never load project.yml. Each test builds its own
``JiraState`` / ``DtmState`` / ``RuleConfig`` from scratch.

Run:
    python3 -m unittest .claude/skills/jira-pull/tests/test_drift_rules.py
or:
    python3 .claude/skills/jira-pull/tests/test_drift_rules.py
"""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional

# ─── Synthetic-package loader ────────────────────────────────────────────────
# Skill folder has a hyphen so `import jira_pull.lib` doesn't work. Match the
# pattern used by actions/audit.py.

_SKILL_ROOT = Path(__file__).resolve().parent.parent  # .claude/skills/jira-pull/
_LIB_DIR = _SKILL_ROOT / "lib"

if "lib" not in sys.modules:
    _pkg = types.ModuleType("lib")
    _pkg.__path__ = [str(_LIB_DIR)]
    sys.modules["lib"] = _pkg
for _name in ("config", "drift_rules", "dtm_reader", "htm_reader"):
    if f"lib.{_name}" not in sys.modules:
        _spec = importlib.util.spec_from_file_location(f"lib.{_name}", _LIB_DIR / f"{_name}.py")
        _mod = importlib.util.module_from_spec(_spec)
        sys.modules[f"lib.{_name}"] = _mod
        _spec.loader.exec_module(_mod)

from lib.config import DtmSchema, HtmSchema  # noqa: E402
from lib.dtm_reader import DtmRow, DtmState  # noqa: E402
from lib.htm_reader import HtmRow, HtmState  # noqa: E402
from lib.drift_rules import (  # noqa: E402
    JiraState,
    NATURAL_SEVERITY,
    RULES,
    RuleConfig,
    Violation,
)


# ─── Fixture builders ────────────────────────────────────────────────────────


_DI_EXTRACTOR = r"\b(DI-\d+)\b"
_UN_EXTRACTOR = r"\b(UN-\d+)\b"
_HAZ_EXTRACTOR = r"\b(HZ-?\d+)\b"


def make_schema(*, columns: Optional[Dict[str, str]] = None,
                extractors: Optional[Dict[str, str]] = None,
                tbd: str = "TBD") -> DtmSchema:
    cols = columns if columns is not None else {
        "user_need": "A",
        "design_input": "B",
        "verification": "C",
        "design_output": "D",
        "hazard_refs": "E",
    }
    exts = extractors if extractors is not None else {
        "user_need_id": _UN_EXTRACTOR,
        "design_input_id": _DI_EXTRACTOR,
        "hazard_id": _HAZ_EXTRACTOR,
    }
    return DtmSchema(
        version="v1.0.0",
        xlsx_path="(synthetic)",
        sheet="Sheet1",
        header_row=1,
        data_start_row=2,
        columns=cols,
        extractors=exts,
        tbd_value=tbd,
        empty_means_unknown=False,
        provenance={},
    )


def make_dtm_state(rows_data: List[Dict[str, Any]],
                   *, schema: Optional[DtmSchema] = None) -> DtmState:
    """rows_data is a list of dicts. Each dict is the `cells` map (canonical
    column name → value). The fixture computes `extracted` IDs based on the
    schema's extractors so by_design_input / by_user_need / by_hazard indexes
    populate correctly."""
    sch = schema or make_schema()
    import re as _re
    ext_pats = {n: _re.compile(p) for n, p in sch.extractors.items()}

    rows: List[DtmRow] = []
    by_di: Dict[str, List[DtmRow]] = {}
    by_un: Dict[str, List[DtmRow]] = {}
    by_haz: Dict[str, List[DtmRow]] = {}

    for i, cells in enumerate(rows_data, start=2):
        # Normalize cells dict — fill missing keys with None
        full_cells = {col: cells.get(col) for col in sch.columns}
        extracted: Dict[str, Optional[str]] = {}
        for ext_name, pat in ext_pats.items():
            source_col = ext_name.replace("_id", "")
            text = full_cells.get(source_col)
            if text:
                m = pat.search(text)
                if m:
                    raw = m.group(1) if m.lastindex else m.group(0)
                    canon = _re.sub(r"[\s-]+", "", raw.strip())
                    extracted[ext_name] = canon
                else:
                    extracted[ext_name] = None
            else:
                extracted[ext_name] = None
        row = DtmRow(row_index=i, cells=full_cells, extracted=extracted, is_blank=False)
        rows.append(row)
        if di := extracted.get("design_input_id"):
            by_di.setdefault(di, []).append(row)
        if un := extracted.get("user_need_id"):
            by_un.setdefault(un, []).append(row)
        if hz := extracted.get("hazard_id"):
            by_haz.setdefault(hz, []).append(row)

    return DtmState(
        schema=sch,
        rows=rows,
        sheet_name=sch.sheet,
        source_path="(synthetic)",
        by_design_input=by_di,
        by_user_need=by_un,
        by_hazard=by_haz,
    )


def make_jira_state(*, epics: Optional[List[dict]] = None,
                    stories: Optional[List[dict]] = None,
                    hazards: Optional[List[dict]] = None,
                    tests: Optional[List[dict]] = None,
                    fix_version: str = "Demo v1.0.0") -> JiraState:
    return JiraState(
        epics=epics or [],
        stories=stories or [],
        hazards=hazards or [],
        test_executions=tests or [],
        fix_version=fix_version,
    )


def make_cfg(**overrides) -> RuleConfig:
    defaults = dict(
        extractors={"design_input_id": _DI_EXTRACTOR, "user_need_id": _UN_EXTRACTOR},
        exempt_filters=[],
        severity_overrides={},
        di_resolution_fallback=[],
        design_input_label=None,
        fix_version=None,
        dtm_xlsx_path=None,
        summary_drift_threshold=0.8,
    )
    defaults.update(overrides)
    return RuleConfig(**defaults)


def make_htm_schema(*, columns: Optional[Dict[str, str]] = None,
                    extractors: Optional[Dict[str, str]] = None,
                    tbd: str = "TBD") -> HtmSchema:
    # Canonical column name for the hazard cell is "hazard" — htm_reader's
    # extractor convention strips "_id" from extractor names to find the source
    # column, so extractor "hazard_id" reads from cells["hazard"].
    cols = columns if columns is not None else {
        "hazard": "A",
        "design_input": "B",
        "mitigation": "C",
        "verification": "D",
    }
    exts = extractors if extractors is not None else {
        "hazard_id": _HAZ_EXTRACTOR,
        "design_input_id": _DI_EXTRACTOR,
    }
    return HtmSchema(
        version="v1.0.0",
        xlsx_path="(synthetic)",
        sheet="Sheet1",
        header_row=1,
        data_start_row=2,
        columns=cols,
        extractors=exts,
        tbd_value=tbd,
        provenance={},
    )


def make_htm_state(rows_data: List[Dict[str, Any]],
                   *, schema: Optional[HtmSchema] = None) -> HtmState:
    sch = schema or make_htm_schema()
    import re as _re
    ext_pats = {n: _re.compile(p) for n, p in sch.extractors.items()}
    rows: List[HtmRow] = []
    by_haz: Dict[str, List[HtmRow]] = {}
    by_di: Dict[str, List[HtmRow]] = {}
    for i, cells in enumerate(rows_data, start=2):
        full_cells = {col: cells.get(col) for col in sch.columns}
        extracted: Dict[str, Optional[str]] = {}
        for ext_name, pat in ext_pats.items():
            source_col = ext_name.replace("_id", "")
            text = full_cells.get(source_col)
            if text:
                m = pat.search(text)
                if m:
                    raw = m.group(1) if m.lastindex else m.group(0)
                    extracted[ext_name] = _re.sub(r"[\s-]+", "", raw.strip())
                else:
                    extracted[ext_name] = None
            else:
                extracted[ext_name] = None
        row = HtmRow(row_index=i, cells=full_cells, extracted=extracted, is_blank=False)
        rows.append(row)
        if hz := extracted.get("hazard_id"):
            by_haz.setdefault(hz, []).append(row)
        di_pat = ext_pats.get("design_input_id")
        if di_pat is not None:
            di_text = full_cells.get("design_input") or ""
            for m in di_pat.finditer(di_text):
                raw = m.group(1) if m.lastindex else m.group(0)
                canon = _re.sub(r"[\s-]+", "", raw.strip())
                by_di.setdefault(canon, []).append(row)
    return HtmState(
        schema=sch,
        rows=rows,
        sheet_name=sch.sheet,
        source_path="(synthetic-htm)",
        by_hazard=by_haz,
        by_design_input=by_di,
    )


def make_dtm_with_hazard_refs(rows_data: List[Dict[str, Any]]) -> DtmState:
    """DTM fixture that emulates dtm_reader's multi-PHA decomposition of the
    `hazard_refs` cell — the production reader uses _extract_all_hazards to
    populate `by_hazard` with one entry per PHA mentioned in the cell. The
    standard make_dtm_state only extracts the FIRST PHA, which is a rule-test
    blind-spot for B7 (where multi-PHA cells matter)."""
    import re as _re
    sch = make_schema()
    haz_pat = _re.compile(sch.extractors["hazard_id"])
    state = make_dtm_state(rows_data, schema=sch)
    by_haz: Dict[str, List[DtmRow]] = {}
    for row in state.rows:
        cell = row.cells.get("hazard_refs") or ""
        for m in haz_pat.finditer(cell):
            raw = m.group(1) if m.lastindex else m.group(0)
            canon = _re.sub(r"[\s-]+", "", raw.strip())
            by_haz.setdefault(canon, []).append(row)
    return DtmState(
        schema=state.schema,
        rows=state.rows,
        sheet_name=state.sheet_name,
        source_path=state.source_path,
        by_design_input=state.by_design_input,
        by_user_need=state.by_user_need,
        by_hazard=by_haz,
    )


def hazard(key: str, summary: str) -> dict:
    return {"key": key, "summary": summary, "issuelinks": []}


def epic(key: str, summary: str, *,
         labels: Optional[List[str]] = None,
         status: Optional[str] = None,
         fix_versions: Optional[List[str]] = None) -> dict:
    e = {"key": key, "summary": summary, "labels": labels or [], "issuelinks": []}
    if status is not None:
        e["status"] = status
    if fix_versions is not None:
        e["fix_versions"] = list(fix_versions)
    return e


def story(key: str, summary: str, parent_key: Optional[str] = None,
          *, fix_versions: Optional[List[str]] = None) -> dict:
    s = {"key": key, "summary": summary, "parent_key": parent_key, "issuelinks": []}
    if fix_versions is not None:
        s["fix_versions"] = list(fix_versions)
    return s


def test_exec(key: str, verifies_story_keys: List[str]) -> dict:
    links = [{"type": "1 Relates", "target_issuetype": "Story", "target_key": k}
             for k in verifies_story_keys]
    return {"key": key, "issuelinks": links}


def run(rule_id: str, j: JiraState, d: DtmState, cfg: RuleConfig,
        h: Optional[HtmState] = None) -> List[Violation]:
    return RULES[rule_id](j, d, h, cfg)


# ─── Tests ───────────────────────────────────────────────────────────────────


class A1Test(unittest.TestCase):
    """A1 — Jira-only DI Epic."""

    def test_clean(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First DI")])
        d = make_dtm_state([{"user_need": "UN-1", "design_input": "DI-1"}])
        self.assertEqual(run("A1", j, d, make_cfg()), [])

    def test_fires_when_dtm_missing_di(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First DI")])
        d = make_dtm_state([])
        vs = run("A1", j, d, make_cfg())
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].rule, "A1")
        self.assertEqual(vs[0].item_id, "DEMO-1")
        self.assertEqual(vs[0].severity, NATURAL_SEVERITY["A1"])

    def test_ignores_non_di_epic(self):
        j = make_jira_state(epics=[epic("DEMO-2", "Refactoring epic, no DI")])
        d = make_dtm_state([])
        self.assertEqual(run("A1", j, d, make_cfg()), [])

    def test_label_with_no_di_prefix_fires_distinctly(self):
        j = make_jira_state(epics=[epic("DEMO-3", "Some work", labels=["design-input"])])
        d = make_dtm_state([])
        cfg = make_cfg(design_input_label="design-input")
        vs = run("A1", j, d, cfg)
        self.assertEqual(len(vs), 1)
        self.assertIn("design_input_label", vs[0].message.lower().replace("'", ""))

    def test_format_only_drift_does_not_fire_a1(self):
        # 'DI-1' vs 'DI-001' — same digit value, format diff is C4's job
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First")])
        d = make_dtm_state([{"design_input": "DI-001"}])
        self.assertEqual(run("A1", j, d, make_cfg()), [])


class A2Test(unittest.TestCase):
    """A2 — DTM-only DI."""

    def test_clean(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First")])
        d = make_dtm_state([{"design_input": "DI-1"}])
        self.assertEqual(run("A2", j, d, make_cfg()), [])

    def test_fires_when_dtm_di_missing_from_jira(self):
        j = make_jira_state(epics=[])
        d = make_dtm_state([{"design_input": "DI-7"}])
        vs = run("A2", j, d, make_cfg())
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].rule, "A2")
        self.assertEqual(vs[0].severity, NATURAL_SEVERITY["A2"])

    def test_format_only_drift_does_not_fire_a2(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First")])
        d = make_dtm_state([{"design_input": "DI-001"}])
        self.assertEqual(run("A2", j, d, make_cfg()), [])


class A3A4SchemaGatedTest(unittest.TestCase):
    """A3/A4 — Software item drift; schema-gated on `software_id` extractor."""

    def test_a3_silent_without_software_extractor(self):
        j = make_jira_state(stories=[story("DEMO-100", "A story")])
        d = make_dtm_state([])
        self.assertEqual(run("A3", j, d, make_cfg()), [])

    def test_a4_silent_without_software_extractor(self):
        j = make_jira_state(stories=[])
        d = make_dtm_state([{"design_output": "DEMO-999 something"}])
        self.assertEqual(run("A4", j, d, make_cfg()), [])

    def test_a3_fires_when_extractor_declared_and_story_missing_from_dtm(self):
        sch = make_schema(extractors={
            "design_input_id": _DI_EXTRACTOR,
            "software_id": r"\b(DEMO-\d+)\b",
        })
        j = make_jira_state(stories=[story("DEMO-100", "A story")])
        d = make_dtm_state([{"design_output": "Other text"}], schema=sch)
        cfg = make_cfg(extractors={"design_input_id": _DI_EXTRACTOR,
                                   "software_id": r"\b(DEMO-\d+)\b"})
        vs = run("A3", j, d, cfg)
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].item_id, "DEMO-100")

    def test_a4_fires_when_dtm_cites_unknown_story_id(self):
        sch = make_schema(extractors={
            "design_input_id": _DI_EXTRACTOR,
            "software_id": r"\b(DEMO-\d+)\b",
        })
        j = make_jira_state(stories=[story("DEMO-100", "A story")])
        d = make_dtm_state([{"design_output": "DEMO-999 unknown reference"}], schema=sch)
        cfg = make_cfg(extractors={"design_input_id": _DI_EXTRACTOR,
                                   "software_id": r"\b(DEMO-\d+)\b"})
        vs = run("A4", j, d, cfg)
        self.assertEqual(len(vs), 1)
        self.assertIn("DEMO999", vs[0].item_id)


class B1Test(unittest.TestCase):
    """B1 — DI without UN."""

    def test_clean(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First")])
        d = make_dtm_state([{"user_need": "UN-1", "design_input": "DI-1"}])
        self.assertEqual(run("B1", j, d, make_cfg()), [])

    def test_fires_when_dtm_row_has_no_un(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First")])
        d = make_dtm_state([{"design_input": "DI-1", "user_need": "TBD"}])
        vs = run("B1", j, d, make_cfg())
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].rule, "B1")

    def test_silent_when_no_dtm_row_at_all(self):
        # Belongs to A1, not B1
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First")])
        d = make_dtm_state([])
        self.assertEqual(run("B1", j, d, make_cfg()), [])

    def test_silent_when_dtm_lacks_user_need_column(self):
        sch = make_schema(columns={"design_input": "A", "verification": "B"})
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First")])
        d = make_dtm_state([{"design_input": "DI-1"}], schema=sch)
        self.assertEqual(run("B1", j, d, make_cfg()), [])


class B2Test(unittest.TestCase):
    """B2 — DI Epic without child Story."""

    def test_clean(self):
        j = make_jira_state(
            epics=[epic("DEMO-1", "DI-1 First")],
            stories=[story("DEMO-100", "A story", parent_key="DEMO-1")],
        )
        d = make_dtm_state([])
        self.assertEqual(run("B2", j, d, make_cfg()), [])

    def test_fires_when_no_child_story(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First")])
        d = make_dtm_state([])
        vs = run("B2", j, d, make_cfg())
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].rule, "B2")
        self.assertEqual(vs[0].severity, "warning")


class B3Test(unittest.TestCase):
    """B3 — DI without V&V via inverse '1 Relates' walk."""

    def test_clean(self):
        j = make_jira_state(
            epics=[epic("DEMO-1", "DI-1 First")],
            stories=[story("DEMO-100", "story", parent_key="DEMO-1")],
            tests=[test_exec("DEMO-200", ["DEMO-100"])],
        )
        d = make_dtm_state([{"design_input": "DI-1", "verification": "Test executed"}])
        self.assertEqual(run("B3", j, d, make_cfg()), [])

    def test_fires_error_when_dtm_says_verified_but_no_jira_test(self):
        j = make_jira_state(
            epics=[epic("DEMO-1", "DI-1 First")],
            stories=[story("DEMO-100", "story", parent_key="DEMO-1")],
            tests=[],
        )
        d = make_dtm_state([{"design_input": "DI-1", "verification": "VER-1 executed"}])
        vs = run("B3", j, d, make_cfg())
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].severity, "error")

    def test_downgrades_to_info_when_dtm_verification_is_tbd(self):
        j = make_jira_state(
            epics=[epic("DEMO-1", "DI-1 First")],
            stories=[story("DEMO-100", "story", parent_key="DEMO-1")],
            tests=[],
        )
        d = make_dtm_state([{"design_input": "DI-1", "verification": "TBD"}])
        vs = run("B3", j, d, make_cfg())
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].severity, "info")


class B5Test(unittest.TestCase):
    """B5 — UN without DI."""

    def test_clean(self):
        d = make_dtm_state([{"user_need": "UN-1", "design_input": "DI-1"}])
        self.assertEqual(run("B5", make_jira_state(), d, make_cfg()), [])

    def test_fires_when_un_populated_di_blank(self):
        d = make_dtm_state([{"user_need": "UN-1", "design_input": "TBD"}])
        vs = run("B5", make_jira_state(), d, make_cfg())
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].rule, "B5")
        self.assertEqual(vs[0].severity, "error")

    def test_silent_when_both_blank(self):
        d = make_dtm_state([{"user_need": "TBD", "design_input": "TBD"}])
        self.assertEqual(run("B5", make_jira_state(), d, make_cfg()), [])


class B6Test(unittest.TestCase):
    """B6 — Story without DI parent."""

    def test_clean(self):
        j = make_jira_state(
            epics=[epic("DEMO-1", "DI-1 First")],
            stories=[story("DEMO-100", "story", parent_key="DEMO-1")],
        )
        self.assertEqual(run("B6", j, make_dtm_state([]), make_cfg()), [])

    def test_fires_when_no_parent(self):
        j = make_jira_state(stories=[story("DEMO-100", "story", parent_key=None)])
        vs = run("B6", j, make_dtm_state([]), make_cfg())
        self.assertEqual(len(vs), 1)
        self.assertIn("no parent", vs[0].message)

    def test_fires_when_parent_not_di_epic(self):
        j = make_jira_state(
            epics=[epic("DEMO-2", "Plain epic without DI prefix")],
            stories=[story("DEMO-100", "story", parent_key="DEMO-2")],
        )
        vs = run("B6", j, make_dtm_state([]), make_cfg())
        self.assertEqual(len(vs), 1)
        self.assertIn("not a DI Epic", vs[0].message)

    def test_fires_when_parent_missing_from_mirror(self):
        j = make_jira_state(stories=[story("DEMO-100", "story", parent_key="DEMO-999")])
        vs = run("B6", j, make_dtm_state([]), make_cfg())
        self.assertEqual(len(vs), 1)
        self.assertIn("not in", vs[0].message)


class C4Test(unittest.TestCase):
    """C4 — DI ID format drift."""

    def test_clean_when_formats_match(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First")])
        d = make_dtm_state([{"design_input": "DI-1"}])
        self.assertEqual(run("C4", j, d, make_cfg()), [])

    def test_fires_when_formats_differ_but_digit_same(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First")])
        d = make_dtm_state([{"design_input": "DI-001"}])
        vs = run("C4", j, d, make_cfg())
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].rule, "C4")
        self.assertIn("DI1", vs[0].message)
        self.assertIn("DI001", vs[0].message)


class A5Test(unittest.TestCase):
    """A5 — Jira-only Hazard."""

    def _cfg(self):
        return make_cfg(extractors={"design_input_id": _DI_EXTRACTOR,
                                    "hazard_id": _HAZ_EXTRACTOR})

    def test_silent_without_hazard_extractor(self):
        j = make_jira_state(hazards=[hazard("DEMO-H1", "HZ1: Bad outcome")])
        d = make_dtm_with_hazard_refs([])
        self.assertEqual(run("A5", j, d, make_cfg()), [])

    def test_clean_when_dtm_hazard_refs_lists_pha(self):
        j = make_jira_state(hazards=[hazard("DEMO-H1", "HZ1: Bad outcome")])
        d = make_dtm_with_hazard_refs([{"design_input": "DI-1", "hazard_refs": "HZ1"}])
        self.assertEqual(run("A5", j, d, self._cfg()), [])

    def test_fires_when_hazard_not_referenced_anywhere(self):
        j = make_jira_state(hazards=[hazard("DEMO-H99", "HZ99: Unmapped")])
        d = make_dtm_with_hazard_refs([{"design_input": "DI-1", "hazard_refs": "HZ1"}])
        vs = run("A5", j, d, self._cfg())
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].rule, "A5")

    def test_clean_when_htm_lists_hazard(self):
        j = make_jira_state(hazards=[hazard("DEMO-H1", "HZ1: x")])
        d = make_dtm_with_hazard_refs([])  # DTM does not list it
        h = make_htm_state([{"hazard": "HZ1", "design_input": "DI-1"}])
        self.assertEqual(run("A5", j, d, self._cfg(), h), [])


class A6Test(unittest.TestCase):
    """A6 — HTM-only Hazard."""

    def _cfg(self):
        return make_cfg(extractors={"design_input_id": _DI_EXTRACTOR,
                                    "hazard_id": _HAZ_EXTRACTOR})

    def test_silent_without_htm(self):
        j = make_jira_state()
        d = make_dtm_with_hazard_refs([])
        self.assertEqual(run("A6", j, d, self._cfg()), [])

    def test_fires_when_htm_has_hazard_jira_does_not(self):
        j = make_jira_state(hazards=[])
        d = make_dtm_with_hazard_refs([])
        h = make_htm_state([{"hazard": "HZ7", "design_input": "DI-1"}])
        vs = run("A6", j, d, self._cfg(), h)
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].rule, "A6")
        self.assertEqual(vs[0].item_id, "HZ7")

    def test_clean_when_jira_has_hazard(self):
        j = make_jira_state(hazards=[hazard("DEMO-H7", "HZ7: x")])
        d = make_dtm_with_hazard_refs([])
        h = make_htm_state([{"hazard": "HZ7", "design_input": "DI-1"}])
        self.assertEqual(run("A6", j, d, self._cfg(), h), [])


class A7A8Test(unittest.TestCase):
    """A7/A8 — Test Execution drift; schema-gated on `test_id` extractor."""

    def _schema_with_test(self):
        return make_schema(extractors={
            "design_input_id": _DI_EXTRACTOR,
            "test_id": r"\b(DEMO-\d+)\b",
        })

    def _cfg(self):
        return make_cfg(extractors={"design_input_id": _DI_EXTRACTOR,
                                    "test_id": r"\b(DEMO-\d+)\b"})

    def test_a7_silent_without_extractor(self):
        j = make_jira_state(tests=[test_exec("DEMO-200", [])])
        d = make_dtm_state([])
        self.assertEqual(run("A7", j, d, make_cfg()), [])

    def test_a7_fires_when_jira_test_not_in_dtm(self):
        sch = self._schema_with_test()
        # DTM cites DEMO-201 only; Jira has both DEMO-200 and DEMO-201 — A7 fires for DEMO-200.
        d = make_dtm_state([{"design_input": "DI-1", "verification": "DEMO-201 ran"}], schema=sch)
        j = make_jira_state(tests=[test_exec("DEMO-200", []), test_exec("DEMO-201", [])])
        vs = run("A7", j, d, self._cfg())
        ids = sorted(v.item_id for v in vs)
        self.assertEqual(ids, ["DEMO-200"])

    def test_a8_fires_when_dtm_cites_unknown_test(self):
        sch = self._schema_with_test()
        d = make_dtm_state([{"design_input": "DI-1", "verification": "DEMO-999 ran"}], schema=sch)
        j = make_jira_state(tests=[test_exec("DEMO-200", [])])
        vs = run("A8", j, d, self._cfg())
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].item_id, "DEMO999")

    def test_a8_silent_when_no_test_refs_in_dtm(self):
        sch = self._schema_with_test()
        d = make_dtm_state([{"design_input": "DI-1", "verification": "no test ids here"}], schema=sch)
        j = make_jira_state(tests=[test_exec("DEMO-200", [])])
        self.assertEqual(run("A8", j, d, self._cfg()), [])


class B4Test(unittest.TestCase):
    """B4 — DI without Hazard."""

    def test_silent_without_hazard_refs_column_and_no_htm(self):
        sch = make_schema(columns={"design_input": "A"})
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First")])
        d = make_dtm_state([{"design_input": "DI-1"}], schema=sch)
        self.assertEqual(run("B4", j, d, make_cfg()), [])

    def test_clean_when_dtm_row_has_hazard_refs(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First")])
        d = make_dtm_with_hazard_refs([{"design_input": "DI-1", "hazard_refs": "HZ1"}])
        self.assertEqual(run("B4", j, d, make_cfg()), [])

    def test_fires_when_dtm_row_has_blank_hazard_refs(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First")])
        d = make_dtm_with_hazard_refs([{"design_input": "DI-1", "hazard_refs": "TBD"}])
        vs = run("B4", j, d, make_cfg())
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].rule, "B4")
        self.assertEqual(vs[0].severity, "info")

    def test_clean_when_htm_lists_di(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First")])
        sch = make_schema(columns={"design_input": "A"})
        d = make_dtm_state([{"design_input": "DI-1"}], schema=sch)
        h = make_htm_state([{"hazard": "HZ1", "design_input": "DI-1"}])
        self.assertEqual(run("B4", j, d, make_cfg(), h), [])


class B7Test(unittest.TestCase):
    """B7 — Hazard without DI link."""

    def _cfg(self):
        return make_cfg(extractors={"design_input_id": _DI_EXTRACTOR,
                                    "hazard_id": _HAZ_EXTRACTOR})

    def test_silent_without_hazard_extractor(self):
        j = make_jira_state(hazards=[hazard("DEMO-H1", "HZ1: x")])
        d = make_dtm_with_hazard_refs([])
        self.assertEqual(run("B7", j, d, make_cfg()), [])

    def test_clean_when_dtm_row_pairs_hazard_with_di(self):
        j = make_jira_state(hazards=[hazard("DEMO-H1", "HZ1: x")])
        d = make_dtm_with_hazard_refs([{"design_input": "DI-1", "hazard_refs": "HZ1"}])
        self.assertEqual(run("B7", j, d, self._cfg()), [])

    def test_fires_when_no_dtm_pairing(self):
        j = make_jira_state(hazards=[hazard("DEMO-H1", "HZ1: x")])
        d = make_dtm_with_hazard_refs([{"design_input": "DI-2", "hazard_refs": "HZ2"}])
        vs = run("B7", j, d, self._cfg())
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].rule, "B7")
        self.assertEqual(vs[0].severity, "error")

    def test_fires_when_dtm_row_has_hazard_but_blank_di(self):
        j = make_jira_state(hazards=[hazard("DEMO-H1", "HZ1: x")])
        d = make_dtm_with_hazard_refs([{"design_input": "TBD", "hazard_refs": "HZ1"}])
        vs = run("B7", j, d, self._cfg())
        self.assertEqual(len(vs), 1)


class B8Test(unittest.TestCase):
    """B8 — Hazard without mitigation or V&V."""

    def _cfg(self):
        return make_cfg(extractors={"design_input_id": _DI_EXTRACTOR,
                                    "hazard_id": _HAZ_EXTRACTOR})

    def test_silent_without_htm(self):
        j = make_jira_state(hazards=[hazard("DEMO-H1", "HZ1: x")])
        d = make_dtm_with_hazard_refs([])
        self.assertEqual(run("B8", j, d, self._cfg()), [])

    def test_fires_when_htm_row_missing_mitigation(self):
        j = make_jira_state(hazards=[hazard("DEMO-H1", "HZ1: x")])
        d = make_dtm_with_hazard_refs([])
        h = make_htm_state([{"hazard": "HZ1", "design_input": "DI-1",
                             "mitigation": "TBD", "verification": "test pass"}])
        vs = run("B8", j, d, self._cfg(), h)
        self.assertEqual(len(vs), 1)
        self.assertIn("mitigation", vs[0].message)

    def test_fires_when_htm_row_missing_vv(self):
        j = make_jira_state(hazards=[hazard("DEMO-H1", "HZ1: x")])
        d = make_dtm_with_hazard_refs([])
        h = make_htm_state([{"hazard": "HZ1", "design_input": "DI-1",
                             "mitigation": "control", "verification": "TBD"}])
        vs = run("B8", j, d, self._cfg(), h)
        self.assertEqual(len(vs), 1)
        self.assertIn("V&V", vs[0].message)

    def test_clean(self):
        j = make_jira_state(hazards=[hazard("DEMO-H1", "HZ1: x")])
        d = make_dtm_with_hazard_refs([])
        h = make_htm_state([{"hazard": "HZ1", "design_input": "DI-1",
                             "mitigation": "control", "verification": "test pass"}])
        self.assertEqual(run("B8", j, d, self._cfg(), h), [])


class C1Test(unittest.TestCase):
    """C1 — Status mismatch."""

    def test_silent_without_status_column(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First", status="Done")])
        d = make_dtm_state([{"design_input": "DI-1"}])
        self.assertEqual(run("C1", j, d, make_cfg()), [])

    def test_clean_when_status_matches(self):
        sch = make_schema(columns={"design_input": "A", "status": "B"})
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First", status="Done")])
        d = make_dtm_state([{"design_input": "DI-1", "status": "Done"}], schema=sch)
        self.assertEqual(run("C1", j, d, make_cfg()), [])

    def test_fires_when_status_differs(self):
        sch = make_schema(columns={"design_input": "A", "status": "B"})
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 First", status="In Progress")])
        d = make_dtm_state([{"design_input": "DI-1", "status": "Done"}], schema=sch)
        vs = run("C1", j, d, make_cfg())
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].rule, "C1")


class C2Test(unittest.TestCase):
    """C2 — Summary drift."""

    def test_clean_when_text_aligned(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 The system shall log audit events")])
        d = make_dtm_state([{"design_input": "DI-1 The system shall log audit events"}])
        self.assertEqual(run("C2", j, d, make_cfg()), [])

    def test_fires_when_summaries_diverge(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 Calibrate the imaging sensor")])
        d = make_dtm_state([{"design_input": "DI-1 Display patient demographic data on screen"}])
        vs = run("C2", j, d, make_cfg())
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].rule, "C2")
        self.assertEqual(vs[0].severity, "info")

    def test_threshold_override_widens_match(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 Log audit events to disk")])
        d = make_dtm_state([{"design_input": "DI-1 Log audit events"}])
        # default threshold 0.8 — these are similar enough
        self.assertEqual(run("C2", j, d, make_cfg()), [])
        # crank threshold to 0.99 — now any wording difference fires
        vs = run("C2", j, d, make_cfg(summary_drift_threshold=0.99))
        self.assertEqual(len(vs), 1)


class C3Test(unittest.TestCase):
    """C3 — Version-scope mismatch."""

    def test_silent_without_target_version(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 x")], fix_version="")
        d = make_dtm_state([])
        self.assertEqual(run("C3", j, d, make_cfg()), [])

    def test_silent_when_issue_has_no_fix_versions(self):
        # Empty fix_versions list = mirror-stripped payload, skip silently
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 x")], fix_version="V1")
        d = make_dtm_state([])
        self.assertEqual(run("C3", j, d, make_cfg(fix_version="V1")), [])

    def test_clean_when_issue_lists_target(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 x", fix_versions=["V1", "V2"])],
                            fix_version="V1")
        d = make_dtm_state([])
        self.assertEqual(run("C3", j, d, make_cfg(fix_version="V1")), [])

    def test_fires_when_issue_lacks_target(self):
        j = make_jira_state(epics=[epic("DEMO-1", "DI-1 x", fix_versions=["V2"])],
                            fix_version="V1")
        d = make_dtm_state([])
        vs = run("C3", j, d, make_cfg(fix_version="V1"))
        self.assertEqual(len(vs), 1)
        self.assertEqual(vs[0].rule, "C3")


class C5Test(unittest.TestCase):
    """C5 — Stale WORKING xlsx."""

    def test_silent_without_siblings(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            primary = Path(tmp) / "Design Traceability Matrix.xlsx"
            primary.write_bytes(b"x")
            d = make_dtm_state([])
            cfg = make_cfg(dtm_xlsx_path=str(primary))
            self.assertEqual(run("C5", make_jira_state(), d, cfg), [])

    def test_fires_one_per_working_sibling(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            primary = Path(tmp) / "Design Traceability Matrix.xlsx"
            primary.write_bytes(b"x")
            (Path(tmp) / "WORKING_DTM v.4.xlsx").write_bytes(b"x")
            (Path(tmp) / "WORKING_DTM v.5.xlsx").write_bytes(b"x")
            d = make_dtm_state([])
            cfg = make_cfg(dtm_xlsx_path=str(primary))
            vs = run("C5", make_jira_state(), d, cfg)
            self.assertEqual(len(vs), 2)
            for v in vs:
                self.assertEqual(v.rule, "C5")
                self.assertTrue(v.item_id.startswith("WORKING_"))


class FullCoverageContractTest(unittest.TestCase):
    """All 21 rules are now implemented; none should raise NotImplementedError
    on a minimal fixture. Replaces the prior UnimplementedRulesTest."""

    def test_no_rule_raises_on_minimal_fixture(self):
        j = make_jira_state()
        d = make_dtm_state([])
        cfg = make_cfg()
        for rule_id in RULES:
            with self.subTest(rule=rule_id):
                try:
                    out = RULES[rule_id](j, d, None, cfg)
                except NotImplementedError as e:
                    self.fail(f"{rule_id} raised NotImplementedError: {e}")
                self.assertIsInstance(out, list)


class RegistryShapeTest(unittest.TestCase):
    """Cross-cutting invariants on the rule registry."""

    def test_registry_size(self):
        self.assertEqual(len(RULES), 21)

    def test_severity_table_covers_all(self):
        for rule_id in RULES:
            self.assertIn(rule_id, NATURAL_SEVERITY,
                          f"NATURAL_SEVERITY missing entry for {rule_id}")

    def test_rule_ids_well_formed(self):
        for rule_id in RULES:
            self.assertRegex(rule_id, r"^[ABC]\d+$")


if __name__ == "__main__":
    unittest.main(verbosity=2)
