"""
Drift rule registry for /jira-pull audit.

Each rule is a pure function with the signature:

    rule(jira_state: JiraState,
         dtm_state: DtmState,
         htm_state: HtmState | None,
         cfg: RuleConfig) -> List[Violation]

Rules emit zero or more Violation records. The runner (actions/audit.py)
applies severity overrides from project.yml `jira_pull.severity_overrides`
*after* the rule emits, so rules emit at their natural severity.

NO project-specific values are hardcoded in this module. DI/UN/PHA prefix
regexes, project keys, exempt filters, and severity overrides all come from
`cfg`, which is built from project.yml at runtime.

Implementation status: SCAFFOLD — signatures and rule IDs only. The runner
should treat any rule whose body raises NotImplementedError as "not yet
implemented" and report it in the drift summary so partial coverage is
visible to reviewers.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Literal, Optional, Set, Tuple


# ─── Shared helpers ─────────────────────────────────────────────────────────


def _canonicalize(raw: Optional[str]) -> Optional[str]:
    """Collapse internal whitespace + hyphens. Mirrors dtm_reader._normalize_id
    so Jira-side and DTM-side extracted IDs canonicalize identically.
    'DI-5'  -> 'DI5'    'DI 005' -> 'DI005'    None -> None
    """
    if not raw:
        return None
    return re.sub(r"[\s-]+", "", raw.strip())


def _di_digit_value(canonical_di: Optional[str]) -> Optional[str]:
    """Reduce a canonical DI string to its trailing digit value, leading zeros
    stripped. 'DI5' -> '5', 'DI005' -> '5', 'DI0' -> '0'. Returns None if no
    trailing digit run."""
    if not canonical_di:
        return None
    m = re.search(r"(\d+)$", canonical_di)
    if not m:
        return None
    return m.group(1).lstrip("0") or "0"


def _is_blank(text: Optional[str], tbd_value: str) -> bool:
    """Mirror dtm_reader._is_blank — None / whitespace-only / TBD all blank."""
    if text is None:
        return True
    s = str(text).strip()
    return s == "" or s == tbd_value


# ─── Data shapes ────────────────────────────────────────────────────────────

Severity = Literal["error", "warning", "info"]
Category = Literal["A", "B", "C"]


@dataclass(frozen=True)
class Violation:
    """One drift finding — surfaced in drift.json + drift.md + inline badges."""

    rule: str               # e.g. "A1", "B3", "C5"
    severity: Severity      # natural severity; runner may override per-project
    item_id: str            # Jira key, DTM row id, HTM row id, or composite
    item_kind: str          # "epic", "story", "hazard", "test_execution", "dtm_row", "htm_row"
    message: str            # human-readable summary of the drift
    resolution_hint: str    # short pointer toward how to fix
    references: Dict[str, str] = field(default_factory=dict)  # browse_url, dtm_path, etc.


@dataclass(frozen=True)
class JiraState:
    """Mirrored Jira snapshot — populated by actions/refresh.py from the cache."""

    epics: List[dict]
    stories: List[dict]
    hazards: List[dict]
    test_executions: List[dict]
    fix_version: str


@dataclass(frozen=True)
class DtmState:
    """Normalized DTM xlsx — populated by lib/dtm_reader.py per the schema map."""

    rows: List[dict]                # one dict per data row, keyed by canonical column name
    sheet: str
    columns: Dict[str, str]         # canonical name -> column letter (mirrors project.yml)
    tbd_value: str                  # typically "TBD"
    empty_means_unknown: bool       # some DTMs use blanks instead of TBD


@dataclass(frozen=True)
class HtmState:
    """Normalized HTM page + xlsx — populated by lib/htm_reader.py."""

    rows: List[dict]
    page_path: Optional[str]
    xlsx_path: Optional[str]


@dataclass(frozen=True)
class RuleConfig:
    """All project-specific values a rule may need.

    Built by lib/config.py from project.yml. Rules MUST NOT read globals or
    re-load project.yml; everything they need comes through this struct.
    """

    extractors: Dict[str, str]              # e.g. {"design_input_id": r"^(DI-\d+)", "user_need_id": ...}
    exempt_filters: List[Dict[str, str]] = field(default_factory=list)
    severity_overrides: Dict[str, Severity] = field(default_factory=dict)
    di_resolution_fallback: List[str] = field(default_factory=list)
    design_input_label: Optional[str] = None  # if set, an Epic with this label is treated as DI even without prefix
    fix_version: Optional[str] = None        # the version under audit (for C3 scope check)
    dtm_xlsx_path: Optional[str] = None      # absolute path to the DTM xlsx (for C5 sibling glob)
    summary_drift_threshold: float = 0.8     # C2 string-similarity threshold (0..1)


# ─── Rule signatures (Category A — Item drift) ──────────────────────────────


def rule_a1_jira_only_di(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """A1 — Epic in Jira (DI-prefixed or design-input-labeled) but no row in DTM.

    Refinement (per task ben/153 Phase A finding): apply only to Epics that ARE
    design-inputs — DI-prefixed OR carrying cfg.design_input_label. Without this
    refinement, infrastructure / research / QMS-tracking Epics flood the output
    as false positives.
    """
    di_pattern_str = cfg.extractors.get("design_input_id")
    if not di_pattern_str:
        return []
    di_pattern = re.compile(di_pattern_str)

    dtm_dis_by_digit = {
        _di_digit_value(canonical_di): canonical_di
        for canonical_di in d.by_design_input.keys()
    }

    violations: List[Violation] = []
    for ep in j.epics:
        summary = ep.get("summary") or ""
        labels = ep.get("labels") or []
        m = di_pattern.search(summary)
        has_label = bool(cfg.design_input_label and cfg.design_input_label in labels)

        if not m and not has_label:
            continue  # not a DI Epic — out of A1 scope

        if m:
            raw = m.group(1) if m.lastindex else m.group(0)
            canonical = _canonicalize(raw)
            digit = _di_digit_value(canonical)
            # If the DTM has any row matching this DI by digit-value, A1 does
            # not fire — format-only drift becomes C4's domain instead.
            if digit is not None and digit in dtm_dis_by_digit:
                continue
            violations.append(Violation(
                rule="A1",
                severity=NATURAL_SEVERITY["A1"],
                item_id=ep["key"],
                item_kind="epic",
                message=f"DI Epic {ep['key']} ({canonical}) has no DTM row.",
                resolution_hint="Add a DTM row for this DI, or remove the DI prefix from the Epic if it is not a design-input.",
                references={"summary": summary, "extracted_di": canonical or ""},
            ))
        else:
            # Has design_input_label but no DI prefix in summary — cannot match
            # against the DTM's DI column; flag for human review.
            violations.append(Violation(
                rule="A1",
                severity=NATURAL_SEVERITY["A1"],
                item_id=ep["key"],
                item_kind="epic",
                message=f"Epic {ep['key']} carries design_input_label {cfg.design_input_label!r} but has no DI-NNNN prefix in its summary.",
                resolution_hint="Add a DI-NNNN prefix to the Epic summary so it can be paired with a DTM row, or remove the label.",
                references={"summary": summary},
            ))
    return violations


def rule_a2_dtm_only_di(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """A2 — DTM cites a DI ID that doesn't resolve to any Jira Epic."""
    di_pattern_str = cfg.extractors.get("design_input_id")
    if not di_pattern_str:
        return []
    di_pattern = re.compile(di_pattern_str)

    jira_di_digits: Dict[str, str] = {}  # digit_value -> canonical Jira DI
    for ep in j.epics:
        m = di_pattern.search(ep.get("summary") or "")
        if not m:
            continue
        canonical = _canonicalize(m.group(1) if m.lastindex else m.group(0))
        digit = _di_digit_value(canonical)
        if digit is not None:
            jira_di_digits.setdefault(digit, canonical or "")

    violations: List[Violation] = []
    for canonical_di, rows in d.by_design_input.items():
        digit = _di_digit_value(canonical_di)
        if digit is not None and digit in jira_di_digits:
            continue  # paired (possibly with format drift — that's C4's job)
        first_row = rows[0]
        violations.append(Violation(
            rule="A2",
            severity=NATURAL_SEVERITY["A2"],
            item_id=canonical_di,
            item_kind="dtm_row",
            message=f"DTM cites DI {canonical_di} (row {first_row.row_index}) but no matching Jira Epic exists.",
            resolution_hint="Create the DI Epic in Jira, or correct the DTM DI ID if it's a typo.",
            references={"dtm_row_index": str(first_row.row_index),
                        "dtm_path": d.source_path},
        ))
    return violations


def rule_a3_jira_only_sw(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """A3 — Jira Story present but no DTM row references it (warning).

    Schema-gated: requires `software_id` extractor in the DTM schema. Projects
    whose DTM doesn't enumerate Story-level references return [] (Story-level
    granularity isn't represented in the DTM today; A3 has nothing to compare).
    """
    sw_pat = cfg.extractors.get("software_id")
    if not sw_pat:
        return []
    sw_pattern = re.compile(sw_pat)
    dtm_sw_refs: set = set()
    for row in d.rows:
        for col_name in ("software", "design_output"):
            text = row.cells.get(col_name)
            if not text:
                continue
            for m in sw_pattern.finditer(text):
                raw = m.group(1) if m.lastindex else m.group(0)
                canon = _canonicalize(raw)
                if canon:
                    dtm_sw_refs.add(canon)

    violations: List[Violation] = []
    for st in j.stories:
        key_canon = _canonicalize(st["key"])
        if key_canon in dtm_sw_refs:
            continue
        violations.append(Violation(
            rule="A3",
            severity=NATURAL_SEVERITY["A3"],
            item_id=st["key"],
            item_kind="story",
            message=f"Story {st['key']} is in Jira ({j.fix_version}) but no DTM row references it.",
            resolution_hint="Cite the Story key in the DTM design-output column, or move the Story out of this fixVersion if not in scope.",
            references={"summary": (st.get("summary") or "")[:120]},
        ))
    return violations


def rule_a4_dtm_only_sw(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """A4 — DTM cites SW reference that doesn't resolve to a Jira Story.

    Schema-gated like A3: requires `software_id` extractor. Pairs DTM-extracted
    SW IDs against the Jira Story key set; silent when the schema can't extract.
    """
    sw_pat = cfg.extractors.get("software_id")
    if not sw_pat:
        return []
    sw_pattern = re.compile(sw_pat)
    jira_story_keys = {_canonicalize(st["key"]) for st in j.stories}

    seen: set = set()
    violations: List[Violation] = []
    for row in d.rows:
        for col_name in ("software", "design_output"):
            text = row.cells.get(col_name)
            if not text:
                continue
            for m in sw_pattern.finditer(text):
                raw = m.group(1) if m.lastindex else m.group(0)
                canon = _canonicalize(raw)
                if not canon or canon in jira_story_keys or canon in seen:
                    continue
                seen.add(canon)
                violations.append(Violation(
                    rule="A4",
                    severity=NATURAL_SEVERITY["A4"],
                    item_id=canon,
                    item_kind="dtm_row",
                    message=f"DTM row {row.row_index} cites SW reference {canon} but no matching Jira Story exists in {j.fix_version}.",
                    resolution_hint="Correct the DTM SW reference, or create the matching Story in Jira.",
                    references={"dtm_row_index": str(row.row_index),
                                "dtm_path": d.source_path},
                ))
    return violations


def rule_a5_jira_only_hazard(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """A5 — Jira Hazard with no corresponding HTM row and no PHA ref in DTM ``hazard_refs``.

    Schema-gated on a ``hazard_id`` extractor — silent if neither side exposes one.
    The Jira hazard summary typically carries ``PHA NN: ...``; we extract the canonical
    hazard ID and look it up against (a) ``HtmState.by_hazard`` if HTM is loaded,
    OR (b) ``DtmState.by_hazard`` (built from the DTM ``hazard_refs`` column —
    multi-PHA cells are decomposed by the dtm_reader). Fires only when the hazard
    appears in NEITHER fallback source.
    """
    hz_pat_str = cfg.extractors.get("hazard_id")
    if not hz_pat_str:
        return []
    hz_pattern = re.compile(hz_pat_str)

    # Build pairing universe — union of HTM hazards (when present) and DTM hazard_refs.
    paired: Set[str] = set()
    if h is not None:
        paired.update(h.by_hazard.keys())
    paired.update(d.by_hazard.keys())
    if not paired:
        # Neither HTM nor DTM hazard column populated → can't compare.
        return []

    violations: List[Violation] = []
    seen: Set[str] = set()
    for hz in j.hazards:
        summary = hz.get("summary") or ""
        m = hz_pattern.search(summary)
        if not m:
            continue
        raw = m.group(1) if m.lastindex else m.group(0)
        canon = _canonicalize(raw)
        if not canon or canon in seen:
            continue
        seen.add(canon)
        if canon in paired:
            continue
        sources = []
        if h is not None:
            sources.append("HTM")
        sources.append("DTM hazard_refs")
        violations.append(Violation(
            rule="A5",
            severity=NATURAL_SEVERITY["A5"],
            item_id=hz["key"],
            item_kind="hazard",
            message=f"Jira Hazard {hz['key']} ({canon}) is not referenced in {' or '.join(sources)}.",
            resolution_hint="Add the hazard to the HTM (preferred) or to the DTM hazard_refs column, or retire the Jira Hazard if obsolete.",
            references={"summary": summary, "extracted_hazard": canon},
        ))
    return violations


def rule_a6_htm_only_hazard(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """A6 — HTM cites a hazard ID that doesn't resolve to a Jira Hazard.

    Requires HTM to be loaded — returns [] otherwise.
    """
    if h is None:
        return []
    hz_pat_str = cfg.extractors.get("hazard_id")
    if not hz_pat_str:
        return []
    hz_pattern = re.compile(hz_pat_str)

    jira_hazard_canons: Set[str] = set()
    for hz in j.hazards:
        m = hz_pattern.search(hz.get("summary") or "")
        if not m:
            continue
        raw = m.group(1) if m.lastindex else m.group(0)
        canon = _canonicalize(raw)
        if canon:
            jira_hazard_canons.add(canon)

    violations: List[Violation] = []
    seen: Set[str] = set()
    for canon, rows in h.by_hazard.items():
        if canon in seen or canon in jira_hazard_canons:
            continue
        seen.add(canon)
        first = rows[0]
        violations.append(Violation(
            rule="A6",
            severity=NATURAL_SEVERITY["A6"],
            item_id=canon,
            item_kind="htm_row",
            message=f"HTM cites Hazard {canon} (row {first.row_index}) but no matching Jira Hazard exists.",
            resolution_hint="Create the Hazard issue in Jira, or correct the HTM hazard ID if it is a typo.",
            references={"htm_row_index": str(first.row_index), "htm_path": h.source_path},
        ))
    return violations


def _dtm_test_refs(d: DtmState) -> Set[str]:
    """Collect canonical test IDs referenced anywhere in the DTM.

    Reads any cell whose canonical column is ``verification`` or ``test_id`` and
    extracts via the schema's ``test_id`` extractor. Returns canonicalized refs.
    Returns the empty set when the schema has neither column nor extractor.
    """
    pat_str = (d.schema.extractors or {}).get("test_id")
    if not pat_str:
        return set()
    pat = re.compile(pat_str)
    cols = [c for c in ("test_id", "verification") if c in d.schema.columns]
    if not cols:
        return set()
    refs: Set[str] = set()
    for row in d.rows:
        for col in cols:
            text = row.cells.get(col)
            if not text:
                continue
            for m in pat.finditer(text):
                raw = m.group(1) if m.lastindex else m.group(0)
                canon = _canonicalize(raw)
                if canon:
                    refs.add(canon)
    return refs


def rule_a7_jira_only_test(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """A7 — Test Execution in Jira but the DTM cites no test ID resolving to it.

    Schema-gated on a ``test_id`` extractor + a ``verification`` or ``test_id``
    column. Silent when not declared (Story-level granularity DTMs that don't
    enumerate tests have nothing to compare).
    """
    refs = _dtm_test_refs(d)
    if not refs and "test_id" not in (d.schema.extractors or {}):
        return []
    violations: List[Violation] = []
    for tx in j.test_executions:
        canon = _canonicalize(tx["key"])
        if not canon or canon in refs:
            continue
        violations.append(Violation(
            rule="A7",
            severity=NATURAL_SEVERITY["A7"],
            item_id=tx["key"],
            item_kind="test_execution",
            message=f"Test Execution {tx['key']} runs in {j.fix_version} but the DTM does not cite it.",
            resolution_hint="Cite the Test Execution key in the DTM verification column, or accept as exploratory and exempt via project.yml.",
            references={"summary": (tx.get("summary") or "")[:120]},
        ))
    return violations


def rule_a8_dtm_only_test(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """A8 — DTM cites a test ID with no matching Jira Test Execution. Schema-gated."""
    refs = _dtm_test_refs(d)
    if not refs:
        return []
    jira_test_keys = {_canonicalize(tx["key"]) for tx in j.test_executions}

    violations: List[Violation] = []
    for canon in sorted(refs):
        if canon in jira_test_keys:
            continue
        violations.append(Violation(
            rule="A8",
            severity=NATURAL_SEVERITY["A8"],
            item_id=canon,
            item_kind="dtm_row",
            message=f"DTM cites test reference {canon} but no matching Jira Test Execution exists in {j.fix_version}.",
            resolution_hint="Correct the DTM test reference, attach the missing Test Execution to this fixVersion in Jira, or retire the citation.",
            references={"dtm_path": d.source_path},
        ))
    return violations


# ─── Rule signatures (Category B — Edge drift) ──────────────────────────────


def rule_b1_di_without_un(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """B1 — DI exists but no DTM UN row links to it.

    Iterates Jira DI Epics; for each, locates DTM rows by digit-value match; if
    none have a populated UN cell, emit. A DI with no DTM row at all is A1's
    domain — B1 stays silent there to avoid double-counting.
    """
    di_pattern_str = cfg.extractors.get("design_input_id")
    if not di_pattern_str:
        return []
    if "user_need" not in d.schema.columns:
        return []
    di_pattern = re.compile(di_pattern_str)

    dtm_rows_by_digit: Dict[str, list] = {}
    for canonical_di, rows in d.by_design_input.items():
        digit = _di_digit_value(canonical_di)
        if digit is not None:
            dtm_rows_by_digit.setdefault(digit, []).extend(rows)

    violations: List[Violation] = []
    for ep in j.epics:
        m = di_pattern.search(ep.get("summary") or "")
        if not m:
            continue
        canonical = _canonicalize(m.group(1) if m.lastindex else m.group(0))
        digit = _di_digit_value(canonical)
        if digit is None:
            continue
        rows = dtm_rows_by_digit.get(digit, [])
        if not rows:
            continue  # no DTM row at all → A1's domain
        has_un = any(
            not _is_blank(row.cells.get("user_need"), d.schema.tbd_value)
            for row in rows
        )
        if has_un:
            continue
        violations.append(Violation(
            rule="B1",
            severity=NATURAL_SEVERITY["B1"],
            item_id=ep["key"],
            item_kind="epic",
            message=f"DI Epic {ep['key']} ({canonical}) is in the DTM but no row populates a User Need.",
            resolution_hint="Populate the UN column in at least one DTM row for this DI, or capture the DI→UN trace.",
            references={"dtm_row_indices": ",".join(str(r.row_index) for r in rows),
                        "extracted_di": canonical or ""},
        ))
    return violations


def rule_b2_di_without_sw(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """B2 — DI Epic has no child Story (parent.key = DI Epic key)."""
    di_pat = cfg.extractors.get("design_input_id")
    if not di_pat:
        return []
    di_pattern = re.compile(di_pat)

    stories_by_parent: Dict[str, list] = {}
    for st in j.stories:
        pk = st.get("parent_key")
        if pk:
            stories_by_parent.setdefault(pk, []).append(st)

    violations: List[Violation] = []
    for ep in j.epics:
        m = di_pattern.search(ep.get("summary") or "")
        has_label = bool(cfg.design_input_label and cfg.design_input_label in (ep.get("labels") or []))
        if not m and not has_label:
            continue
        if stories_by_parent.get(ep["key"]):
            continue
        canonical = _canonicalize(m.group(1) if m and m.lastindex else (m.group(0) if m else None))
        violations.append(Violation(
            rule="B2",
            severity=NATURAL_SEVERITY["B2"],
            item_id=ep["key"],
            item_kind="epic",
            message=f"DI Epic {ep['key']} ({canonical or '<no DI>'}) has no child Story in {j.fix_version}.",
            resolution_hint="Create at least one Software Requirement Story under this DI Epic, or move the DI to a fixVersion where its scope is being implemented.",
            references={"summary": ep.get("summary") or "", "extracted_di": canonical or ""},
        ))
    return violations


def rule_b3_di_without_vv(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """B3 — DI has no Test Execution coverage via inverse '1 Relates' issuelink walk.

    Walks DI Epic → child Stories → Test Executions whose `issuelinks[type=='1 Relates']`
    points (inward) to one of the child Stories. Severity: 'info' when DTM verification
    column is TBD/blank for the DI (Jira just hasn't been populated yet); otherwise
    'error' (DTM claims verification but Jira disagrees).
    """
    di_pat = cfg.extractors.get("design_input_id")
    if not di_pat:
        return []
    di_pattern = re.compile(di_pat)

    stories_by_parent: Dict[str, list] = {}
    for st in j.stories:
        pk = st.get("parent_key")
        if pk:
            stories_by_parent.setdefault(pk, []).append(st)

    tests_by_story: Dict[str, list] = {}
    for tx in j.test_executions:
        for link in tx.get("issuelinks") or []:
            if link.get("type") != "1 Relates":
                continue
            if link.get("target_issuetype") != "Story":
                continue
            target = link.get("target_key")
            if target:
                tests_by_story.setdefault(target, []).append(tx)

    has_dtm_v = "verification" in d.schema.columns
    dtm_rows_by_di_digit: Dict[str, list] = {}
    if has_dtm_v:
        for canonical_di, rows in d.by_design_input.items():
            digit = _di_digit_value(canonical_di)
            if digit is not None:
                dtm_rows_by_di_digit.setdefault(digit, []).extend(rows)

    violations: List[Violation] = []
    for ep in j.epics:
        m = di_pattern.search(ep.get("summary") or "")
        has_label = bool(cfg.design_input_label and cfg.design_input_label in (ep.get("labels") or []))
        if not m and not has_label:
            continue
        children = stories_by_parent.get(ep["key"], [])
        test_count = sum(len(tests_by_story.get(st["key"], [])) for st in children)
        if test_count > 0:
            continue
        canonical = _canonicalize(m.group(1) if m and m.lastindex else (m.group(0) if m else None))
        digit = _di_digit_value(canonical) if canonical else None
        sev = NATURAL_SEVERITY["B3"]  # default 'error'
        msg_suffix = ""
        if has_dtm_v and digit is not None:
            rows = dtm_rows_by_di_digit.get(digit, [])
            if rows and all(_is_blank(r.cells.get("verification"), d.schema.tbd_value) for r in rows):
                sev = "info"
                msg_suffix = " (DTM verification column TBD; Jira coverage = 0)"
        violations.append(Violation(
            rule="B3",
            severity=sev,
            item_id=ep["key"],
            item_kind="epic",
            message=f"DI Epic {ep['key']} ({canonical or '<no DI>'}) has {len(children)} child Stories but 0 verifying Test Executions.{msg_suffix}",
            resolution_hint="Add Xray Test Executions linked to the child Stories (issuelinks type='1 Relates' inwardIssue=Story), or update the DTM verification column to reflect coverage.",
            references={"child_story_count": str(len(children)), "extracted_di": canonical or ""},
        ))
    return violations


def rule_b4_di_without_hazard(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """B4 — DI has no inbound Hazard link (info — often intentional).

    Considered linked when EITHER (a) HTM has a row pairing the DI digit to a
    hazard, OR (b) any DTM row whose ``design_input`` resolves to the DI also
    populates ``hazard_refs``. Schema-gated on the design_input extractor; if
    neither HTM nor a DTM ``hazard_refs`` column is available, returns [].
    """
    di_pat = cfg.extractors.get("design_input_id")
    if not di_pat:
        return []
    if h is None and "hazard_refs" not in d.schema.columns:
        return []
    di_pattern = re.compile(di_pat)

    # Build set of DI digit-values that have a hazard link in DTM.
    dtm_di_digits_with_hazard: Set[str] = set()
    if "hazard_refs" in d.schema.columns:
        for canonical_di, rows in d.by_design_input.items():
            digit = _di_digit_value(canonical_di)
            if digit is None:
                continue
            for row in rows:
                if not _is_blank(row.cells.get("hazard_refs"), d.schema.tbd_value):
                    dtm_di_digits_with_hazard.add(digit)
                    break

    htm_di_digits: Set[str] = set()
    if h is not None:
        for canonical_di in h.by_design_input.keys():
            digit = _di_digit_value(canonical_di)
            if digit is not None:
                htm_di_digits.add(digit)

    violations: List[Violation] = []
    for ep in j.epics:
        m = di_pattern.search(ep.get("summary") or "")
        has_label = bool(cfg.design_input_label and cfg.design_input_label in (ep.get("labels") or []))
        if not m and not has_label:
            continue
        canonical = _canonicalize(m.group(1) if m and m.lastindex else (m.group(0) if m else None))
        digit = _di_digit_value(canonical) if canonical else None
        if digit is None:
            continue
        if digit in dtm_di_digits_with_hazard or digit in htm_di_digits:
            continue
        violations.append(Violation(
            rule="B4",
            severity=NATURAL_SEVERITY["B4"],
            item_id=ep["key"],
            item_kind="epic",
            message=f"DI Epic {ep['key']} ({canonical}) has no Hazard link in HTM or DTM hazard_refs.",
            resolution_hint="Confirm whether the DI is intentionally non-safety-critical; otherwise add a Hazard link in the HTM or populate the DTM hazard_refs column.",
            references={"extracted_di": canonical or ""},
        ))
    return violations


def rule_b5_un_without_di(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """B5 — DTM UN row has no DI populated."""
    if "user_need" not in d.schema.columns or "design_input" not in d.schema.columns:
        return []
    violations: List[Violation] = []
    for row in d.rows:
        un_text = row.cells.get("user_need")
        di_text = row.cells.get("design_input")
        if _is_blank(un_text, d.schema.tbd_value):
            continue
        if not _is_blank(di_text, d.schema.tbd_value):
            continue
        un_canonical = row.extracted.get("user_need_id") or _canonicalize(un_text) or (un_text or "")
        violations.append(Violation(
            rule="B5",
            severity=NATURAL_SEVERITY["B5"],
            item_id=f"row{row.row_index}:{un_canonical}",
            item_kind="dtm_row",
            message=f"DTM row {row.row_index} populates UN ({un_canonical}) but DI is blank/TBD.",
            resolution_hint="Populate the DI column for this UN row in the DTM, or remove the UN row if it is no longer in scope.",
            references={"dtm_row_index": str(row.row_index),
                        "user_need_text": un_text or "",
                        "dtm_path": d.source_path},
        ))
    return violations


def rule_b6_sw_without_parent_di(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """B6 — Story has empty parent or parent.issuetype != Epic.

    Stronger reading enforced here: the parent must be a DI Epic (DI-prefixed
    or carrying cfg.design_input_label). A Story whose parent is an Epic but
    NOT a DI Epic still violates the design-controls trace (every SW item
    should descend from a Design Input).
    """
    di_pat = cfg.extractors.get("design_input_id")
    if not di_pat:
        return []
    di_pattern = re.compile(di_pat)

    di_epic_keys: set = set()
    epic_by_key: Dict[str, dict] = {}
    for ep in j.epics:
        epic_by_key[ep["key"]] = ep
        m = di_pattern.search(ep.get("summary") or "")
        has_label = bool(cfg.design_input_label and cfg.design_input_label in (ep.get("labels") or []))
        if m or has_label:
            di_epic_keys.add(ep["key"])

    violations: List[Violation] = []
    for st in j.stories:
        pk = st.get("parent_key")
        if pk and pk in di_epic_keys:
            continue
        if not pk:
            msg = f"Story {st['key']} has no parent Epic."
        elif pk not in epic_by_key:
            msg = f"Story {st['key']} parent {pk} is not in the {j.fix_version} mirror."
        else:
            parent_summary = (epic_by_key[pk].get("summary") or "")[:60]
            msg = f"Story {st['key']} parent {pk} ({parent_summary!r}) is not a DI Epic."
        violations.append(Violation(
            rule="B6",
            severity=NATURAL_SEVERITY["B6"],
            item_id=st["key"],
            item_kind="story",
            message=msg,
            resolution_hint="Reparent the Story under a DI-NNNN Epic, or add a DI prefix / design_input_label to the parent Epic if it actually represents a design input.",
            references={"summary": (st.get("summary") or "")[:120], "parent_key": pk or ""},
        ))
    return violations


def rule_b7_hazard_without_di(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """B7 — Jira Hazard has no DI link, in HTM or DTM ``hazard_refs``.

    A hazard is considered linked to a DI when EITHER (a) the HTM has a row
    pairing this hazard to at least one DI, OR (b) at least one DTM row lists
    this hazard in ``hazard_refs`` AND has a populated ``design_input``.
    Schema-gated on a ``hazard_id`` extractor.
    """
    hz_pat_str = cfg.extractors.get("hazard_id")
    if not hz_pat_str:
        return []
    hz_pattern = re.compile(hz_pat_str)
    has_dtm_haz = "hazard_refs" in d.schema.columns and "design_input" in d.schema.columns
    if h is None and not has_dtm_haz:
        return []

    violations: List[Violation] = []
    seen: Set[str] = set()
    for hz in j.hazards:
        summary = hz.get("summary") or ""
        m = hz_pattern.search(summary)
        if not m:
            continue
        raw = m.group(1) if m.lastindex else m.group(0)
        canon = _canonicalize(raw)
        if not canon or canon in seen:
            continue
        seen.add(canon)

        linked = False
        if h is not None:
            htm_rows = h.by_hazard.get(canon, [])
            for row in htm_rows:
                if not _is_blank(row.cells.get("design_input"), h.schema.tbd_value):
                    linked = True
                    break
        if not linked and has_dtm_haz:
            dtm_rows = d.by_hazard.get(canon, [])
            for row in dtm_rows:
                if not _is_blank(row.cells.get("design_input"), d.schema.tbd_value):
                    linked = True
                    break
        if linked:
            continue

        sources = []
        if h is not None:
            sources.append("HTM")
        if has_dtm_haz:
            sources.append("DTM")
        violations.append(Violation(
            rule="B7",
            severity=NATURAL_SEVERITY["B7"],
            item_id=hz["key"],
            item_kind="hazard",
            message=f"Hazard {hz['key']} ({canon}) has no DI link in {' or '.join(sources)}.",
            resolution_hint="Add a Hazard→DI row in the HTM, or populate the DTM design_input column for this hazard's row.",
            references={"summary": summary, "extracted_hazard": canon},
        ))
    return violations


def rule_b8_hazard_without_mitigation_or_vv(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """B8 — Hazard has no SW (control measure) or no V&V evidence (per ISO 14971).

    Requires HTM to be loaded (``mitigation`` and ``verification`` columns).
    Returns [] otherwise — the DTM does not currently encode mitigation+V&V
    per hazard, so absent the HTM there's no source of truth to compare against.
    """
    if h is None:
        return []
    hz_pat_str = cfg.extractors.get("hazard_id")
    if not hz_pat_str:
        return []
    has_mit = "mitigation" in h.schema.columns
    has_vv = "verification" in h.schema.columns
    if not has_mit and not has_vv:
        return []
    hz_pattern = re.compile(hz_pat_str)

    violations: List[Violation] = []
    seen: Set[str] = set()
    for hz in j.hazards:
        m = hz_pattern.search(hz.get("summary") or "")
        if not m:
            continue
        raw = m.group(1) if m.lastindex else m.group(0)
        canon = _canonicalize(raw)
        if not canon or canon in seen:
            continue
        seen.add(canon)
        rows = h.by_hazard.get(canon, [])

        has_mit_evidence = (not has_mit) or any(
            not _is_blank(r.cells.get("mitigation"), h.schema.tbd_value) for r in rows
        )
        has_vv_evidence = (not has_vv) or any(
            not _is_blank(r.cells.get("verification"), h.schema.tbd_value) for r in rows
        )
        missing = []
        if has_mit and not has_mit_evidence:
            missing.append("mitigation")
        if has_vv and not has_vv_evidence:
            missing.append("V&V")
        if not missing:
            continue
        violations.append(Violation(
            rule="B8",
            severity=NATURAL_SEVERITY["B8"],
            item_id=hz["key"],
            item_kind="hazard",
            message=f"Hazard {hz['key']} ({canon}) is missing {', '.join(missing)} evidence in the HTM.",
            resolution_hint="Document the control measure and verifying test in the HTM per ISO 14971 risk-control requirements.",
            references={"extracted_hazard": canon, "htm_path": h.source_path},
        ))
    return violations


# ─── Rule signatures (Category C — Metadata drift) ──────────────────────────


def _normalize_summary(text: Optional[str]) -> str:
    """Normalize a summary string for similarity comparison: lowercase, collapse
    whitespace, strip a leading DI-NNNN prefix (which shouldn't drive similarity)."""
    if not text:
        return ""
    s = re.sub(r"^\s*DI[\s-]*\d+[\s:.\-]*", "", text, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def rule_c1_status_mismatch(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """C1 — Jira status differs from DTM ``status`` column for paired DI rows.

    Schema-gated on a DTM ``status`` column. Silent when the DTM does not
    declare one (the common case during early development).
    """
    di_pat = cfg.extractors.get("design_input_id")
    if not di_pat:
        return []
    if "status" not in d.schema.columns:
        return []
    di_pattern = re.compile(di_pat)

    dtm_by_digit: Dict[str, list] = {}
    for canonical_di, rows in d.by_design_input.items():
        digit = _di_digit_value(canonical_di)
        if digit is None:
            continue
        dtm_by_digit.setdefault(digit, []).extend(rows)

    violations: List[Violation] = []
    for ep in j.epics:
        m = di_pattern.search(ep.get("summary") or "")
        if not m:
            continue
        canonical = _canonicalize(m.group(1) if m.lastindex else m.group(0))
        digit = _di_digit_value(canonical)
        if digit is None:
            continue
        rows = dtm_by_digit.get(digit, [])
        if not rows:
            continue
        jira_status = (ep.get("status") or "").strip().lower()
        if not jira_status:
            continue
        for row in rows:
            dtm_status = (row.cells.get("status") or "").strip().lower()
            if not dtm_status:
                continue
            if dtm_status == jira_status:
                continue
            violations.append(Violation(
                rule="C1",
                severity=NATURAL_SEVERITY["C1"],
                item_id=ep["key"],
                item_kind="epic",
                message=f"Status mismatch on DI {canonical}: Jira={ep.get('status')!r}, DTM row {row.row_index}={row.cells.get('status')!r}.",
                resolution_hint="Refresh the DTM status column from Jira (Jira is the live source of truth for status).",
                references={"jira_status": ep.get("status") or "",
                            "dtm_status": row.cells.get("status") or "",
                            "dtm_row_index": str(row.row_index)},
            ))
            break  # one violation per DI is enough
    return violations


def rule_c2_summary_drift(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """C2 — DTM DI description differs materially from Jira Epic summary.

    Uses ``difflib.SequenceMatcher.ratio`` on normalized strings; emits when
    similarity < ``cfg.summary_drift_threshold`` (default 0.8). Schema-gated:
    needs a DTM ``design_input`` cell with non-blank text to compare.
    """
    di_pat = cfg.extractors.get("design_input_id")
    if not di_pat:
        return []
    di_pattern = re.compile(di_pat)
    threshold = cfg.summary_drift_threshold or 0.8

    dtm_by_digit: Dict[str, list] = {}
    for canonical_di, rows in d.by_design_input.items():
        digit = _di_digit_value(canonical_di)
        if digit is None:
            continue
        dtm_by_digit.setdefault(digit, []).append((canonical_di, rows[0]))

    violations: List[Violation] = []
    seen: Set[Tuple[str, int]] = set()
    for ep in j.epics:
        m = di_pattern.search(ep.get("summary") or "")
        if not m:
            continue
        canonical = _canonicalize(m.group(1) if m.lastindex else m.group(0))
        digit = _di_digit_value(canonical)
        if digit is None:
            continue
        for dtm_canonical, row in dtm_by_digit.get(digit, []):
            dtm_text = row.cells.get("design_input") or ""
            jira_text = ep.get("summary") or ""
            a = _normalize_summary(jira_text)
            b = _normalize_summary(dtm_text)
            if not a or not b:
                continue
            ratio = difflib.SequenceMatcher(a=a, b=b).ratio()
            if ratio >= threshold:
                continue
            pair = (ep["key"], row.row_index)
            if pair in seen:
                continue
            seen.add(pair)
            violations.append(Violation(
                rule="C2",
                severity=NATURAL_SEVERITY["C2"],
                item_id=ep["key"],
                item_kind="epic",
                message=f"DI {canonical} summary drift: similarity={ratio:.2f} (threshold {threshold:.2f}). Jira={jira_text[:80]!r}; DTM={dtm_text[:80]!r}.",
                resolution_hint="Investigate whether the DTM lags Jira's wording, or vice-versa, and align the canonical description.",
                references={"similarity": f"{ratio:.3f}",
                            "jira_summary": jira_text,
                            "dtm_text": dtm_text,
                            "dtm_row_index": str(row.row_index)},
            ))
    return violations


def rule_c3_version_scope_mismatch(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """C3 — Jira issue's fix_versions doesn't include the audited fix_version.

    Detects cross-version Epic reuse — e.g. ``AFAI-14`` appearing in both v1 and
    v2 mirrors because Jira tagged it with both fix_versions. When the audited
    pair carries a Jira issue whose fix_versions list does NOT contain
    ``cfg.fix_version`` or ``j.fix_version``, that's a scope-tag drift between
    the mirror snapshot and Jira's view of the world.
    """
    target = (cfg.fix_version or j.fix_version or "").strip()
    if not target:
        return []
    violations: List[Violation] = []
    for layer_name, bucket in (("epic", j.epics), ("story", j.stories),
                                ("hazard", j.hazards), ("test_execution", j.test_executions)):
        for issue in bucket:
            fvs = issue.get("fix_versions") or []
            # fix_versions is typically a list of strings (or dicts in some MCP shapes); normalize.
            fv_strs: List[str] = []
            for fv in fvs:
                if isinstance(fv, str):
                    fv_strs.append(fv.strip())
                elif isinstance(fv, dict):
                    name = fv.get("name") or fv.get("fix_version") or ""
                    if name:
                        fv_strs.append(name.strip())
            if any(fv == target for fv in fv_strs):
                continue
            if not fv_strs:
                # No fix_versions data — common in mirror-stripped payloads. Skip silently.
                continue
            violations.append(Violation(
                rule="C3",
                severity=NATURAL_SEVERITY["C3"],
                item_id=issue["key"],
                item_kind=layer_name,
                message=f"{layer_name.title()} {issue['key']} appears in mirror for {target!r} but Jira fix_versions={fv_strs!r}.",
                resolution_hint="Either re-tag the Jira issue with the audited fixVersion, or remove it from this version's mirror snapshot.",
                references={"jira_fix_versions": ",".join(fv_strs), "audit_fix_version": target},
            ))
    return violations


def rule_c4_id_format_drift(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """C4 — Jira Epic summary's DI-NNNN prefix doesn't match DTM's DI ID column.

    Note: handled with care for Epics that lack a prefix entirely — those
    are A1's domain when they ARE design-inputs, not C4's. C4 fires only
    when both sides have an extractable ID and they disagree.

    Pairing strategy: collapse both sides to their digit value (leading zeros
    stripped). Same digit value → same conceptual DI; if the canonical strings
    still differ (e.g. ``DI5`` vs ``DI005``), it's a format drift.
    """
    di_pattern_str = cfg.extractors.get("design_input_id")
    if not di_pattern_str:
        return []
    di_pattern = re.compile(di_pattern_str)

    dtm_by_digit: Dict[str, list] = {}
    for canonical_di, rows in d.by_design_input.items():
        digit = _di_digit_value(canonical_di)
        if digit is not None:
            dtm_by_digit.setdefault(digit, []).append((canonical_di, rows[0]))

    violations: List[Violation] = []
    seen_pairs = set()
    for ep in j.epics:
        m = di_pattern.search(ep.get("summary") or "")
        if not m:
            continue
        jira_canonical = _canonicalize(m.group(1) if m.lastindex else m.group(0))
        digit = _di_digit_value(jira_canonical)
        if digit is None:
            continue
        for dtm_canonical, first_row in dtm_by_digit.get(digit, []):
            if dtm_canonical == jira_canonical:
                continue
            pair = (jira_canonical, dtm_canonical)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            violations.append(Violation(
                rule="C4",
                severity=NATURAL_SEVERITY["C4"],
                item_id=ep["key"],
                item_kind="epic",
                message=f"DI ID format drift: Jira Epic {ep['key']} uses {jira_canonical!r}, DTM row {first_row.row_index} uses {dtm_canonical!r}.",
                resolution_hint="Pick one canonical DI format and align the Jira Epic summary with the DTM cell.",
                references={"jira_di": jira_canonical or "",
                            "dtm_di": dtm_canonical,
                            "dtm_row_index": str(first_row.row_index),
                            "dtm_path": d.source_path},
            ))
    return violations


def rule_c5_stale_working_xlsx(j: JiraState, d: DtmState, h: Optional[HtmState], cfg: RuleConfig) -> List[Violation]:
    """C5 — ``WORKING_*.xlsx`` siblings exist alongside the configured DTM file.

    Filename heuristic. Emits one info per stale sibling so reviewers can
    confirm the configured file is the authoritative one and consider archiving
    the working copies. Uses ``cfg.dtm_xlsx_path`` (set by audit.py to the
    schema's resolved path) and falls back to ``d.source_path``.
    """
    path_str = cfg.dtm_xlsx_path or d.source_path
    if not path_str:
        return []
    primary = Path(path_str)
    parent = primary.parent
    if not parent.exists():
        return []
    violations: List[Violation] = []
    for sibling in sorted(parent.glob("WORKING_*.xlsx")):
        if sibling.resolve() == primary.resolve():
            continue
        try:
            rel = str(sibling.relative_to(Path.cwd()))
        except ValueError:
            rel = str(sibling)
        violations.append(Violation(
            rule="C5",
            severity=NATURAL_SEVERITY["C5"],
            item_id=sibling.name,
            item_kind="dtm_row",
            message=f"WORKING xlsx sibling found alongside the configured DTM: {sibling.name}.",
            resolution_hint="Confirm the configured DTM is authoritative and archive or remove the WORKING copy.",
            references={"sibling_path": rel, "primary_path": str(primary)},
        ))
    return violations


# ─── Registry ───────────────────────────────────────────────────────────────


RuleFn = Callable[[JiraState, DtmState, Optional[HtmState], RuleConfig], List[Violation]]


RULES: Dict[str, RuleFn] = {
    # Category A — Item drift
    "A1": rule_a1_jira_only_di,
    "A2": rule_a2_dtm_only_di,
    "A3": rule_a3_jira_only_sw,
    "A4": rule_a4_dtm_only_sw,
    "A5": rule_a5_jira_only_hazard,
    "A6": rule_a6_htm_only_hazard,
    "A7": rule_a7_jira_only_test,
    "A8": rule_a8_dtm_only_test,
    # Category B — Edge drift
    "B1": rule_b1_di_without_un,
    "B2": rule_b2_di_without_sw,
    "B3": rule_b3_di_without_vv,
    "B4": rule_b4_di_without_hazard,
    "B5": rule_b5_un_without_di,
    "B6": rule_b6_sw_without_parent_di,
    "B7": rule_b7_hazard_without_di,
    "B8": rule_b8_hazard_without_mitigation_or_vv,
    # Category C — Metadata drift
    "C1": rule_c1_status_mismatch,
    "C2": rule_c2_summary_drift,
    "C3": rule_c3_version_scope_mismatch,
    "C4": rule_c4_id_format_drift,
    "C5": rule_c5_stale_working_xlsx,
}


NATURAL_SEVERITY: Dict[str, Severity] = {
    "A1": "error", "A2": "error", "A3": "warning", "A4": "warning",
    "A5": "warning", "A6": "warning", "A7": "info", "A8": "warning",
    "B1": "error", "B2": "warning", "B3": "error", "B4": "info",
    "B5": "error", "B6": "warning", "B7": "error", "B8": "error",
    "C1": "warning", "C2": "info", "C3": "warning", "C4": "error", "C5": "info",
}


def category(rule_id: str) -> Category:
    return rule_id[0]  # type: ignore[return-value]
