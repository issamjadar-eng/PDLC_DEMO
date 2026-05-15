"""
Disk-backed reader for the `_jira/` mirror snapshots.

This module is the I/O layer between the on-disk Jira mirror (written by
actions/refresh.py) and the in-memory state shape (`JiraState` from
drift_rules) that audit rules consume. It is **read-only and MCP-free** —
production live-pull integration is a separate concern handled by
actions/refresh.py.

On-disk layout (per `lib/config.py` resolution):

    <project_root>/<cache_root>/<arch_slug>/<version_id>/
        epics.json
        stories.json
        hazards.json
        tests.json
        _meta.json

Each layer file has shape: `{"_meta": {...}, "issues": [<issue>, ...]}`.
Each issue is a flat dict with at least: `key, summary, status, issuetype,
labels, components, fix_versions, parent_key, parent_summary, issuelinks,
created, updated`.

`JiraIndex` provides the lookups drift rules actually want: key→issue,
parent→children, story→verifying-tests, and id-prefix extraction. Rules
should prefer the index over scanning the raw lists.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .config import DhfConfig, ResolvedConfig
from .drift_rules import JiraState


# ─── Loader ──────────────────────────────────────────────────────────────────


_LAYER_FILES = {
    "epics": "epics.json",
    "stories": "stories.json",
    "hazards": "hazards.json",
    "test_executions": "tests.json",
}


class MirrorMissing(FileNotFoundError):
    """Raised when a layer file is missing from the mirror snapshot."""


def mirror_dir(cfg: ResolvedConfig, dhf: DhfConfig, version_id: str) -> Path:
    """Resolve the on-disk folder holding the mirror for one DHF×version.

    Reads `change_control.jira.mirror_root` from project.yml (default
    ``docs/project/_jira``). The transient `cache.root` (e.g. `_cache/`) is
    a separate concern and not used for mirror lookups.
    """
    return cfg.project_root / cfg.site.mirror_root.lstrip("/") / dhf.arch_slug / version_id


def _load_layer(path: Path) -> List[dict]:
    if not path.exists():
        raise MirrorMissing(f"Mirror layer file not found: {path}")
    payload = json.loads(path.read_text())
    issues = payload.get("issues")
    if not isinstance(issues, list):
        raise ValueError(f"{path} has no top-level 'issues' list")
    return issues


def load_state(cfg: ResolvedConfig, dhf: DhfConfig, version_id: str) -> JiraState:
    """Read all four layer files for one DHF×version into a `JiraState`."""
    base = mirror_dir(cfg, dhf, version_id)
    if not base.exists():
        raise MirrorMissing(f"Mirror dir not found: {base}")

    epics = _load_layer(base / _LAYER_FILES["epics"])
    stories = _load_layer(base / _LAYER_FILES["stories"])
    hazards = _load_layer(base / _LAYER_FILES["hazards"])
    tests = _load_layer(base / _LAYER_FILES["test_executions"])

    meta_path = base / "_meta.json"
    fix_version = ""
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        fix_version = str(meta.get("fix_version") or "")

    return JiraState(
        epics=epics,
        stories=stories,
        hazards=hazards,
        test_executions=tests,
        fix_version=fix_version,
    )


# ─── Index ───────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class JiraIndex:
    """Pre-computed lookups for drift rules. Build once per audit run.

    All maps are keyed by Jira issue `key` (e.g. ``AFAI-1234``). Children
    lists preserve insertion order from the source `JiraState`.
    """

    state: JiraState

    by_key: Dict[str, dict] = field(default_factory=dict)
    epic_by_key: Dict[str, dict] = field(default_factory=dict)
    story_by_key: Dict[str, dict] = field(default_factory=dict)
    hazard_by_key: Dict[str, dict] = field(default_factory=dict)
    test_by_key: Dict[str, dict] = field(default_factory=dict)

    stories_by_parent: Dict[str, List[dict]] = field(default_factory=lambda: defaultdict(list))
    tests_by_story: Dict[str, List[dict]] = field(default_factory=lambda: defaultdict(list))

    def epic_for_story(self, story: dict) -> Optional[dict]:
        pk = story.get("parent_key")
        if not pk:
            return None
        return self.epic_by_key.get(pk)

    def tests_for_story_key(self, story_key: str) -> List[dict]:
        """All Test Execution issues that verify the given Story key.

        Walks `tests_by_story[story_key]`, built by scanning every Test
        Execution's `issuelinks` for ``type == "1 Relates"`` edges
        (bidirectional — both inward and outward) whose target is the Story.
        """
        return list(self.tests_by_story.get(story_key, []))

    def design_input_epics(self, di_pattern: re.Pattern[str],
                           design_input_label: Optional[str] = None) -> List[dict]:
        """Subset of epics that ARE design inputs.

        An Epic counts as a DI if EITHER:
          - its summary matches `di_pattern` (typically ``DI-NNNN`` prefix), OR
          - it carries `design_input_label` in its `labels` (when configured).

        This is the A1 refinement — without it, infrastructure / QMS-tracking
        Epics flood drift output as false positives.
        """
        out: List[dict] = []
        for ep in self.state.epics:
            if di_pattern.search(ep.get("summary") or ""):
                out.append(ep)
                continue
            if design_input_label and design_input_label in (ep.get("labels") or []):
                out.append(ep)
        return out


def build_index(state: JiraState) -> JiraIndex:
    """Construct a `JiraIndex` over the loaded `JiraState`."""
    idx = JiraIndex(state=state)

    for ep in state.epics:
        idx.by_key[ep["key"]] = ep
        idx.epic_by_key[ep["key"]] = ep
    for st in state.stories:
        idx.by_key[st["key"]] = st
        idx.story_by_key[st["key"]] = st
        pk = st.get("parent_key")
        if pk:
            idx.stories_by_parent[pk].append(st)
    for hz in state.hazards:
        idx.by_key[hz["key"]] = hz
        idx.hazard_by_key[hz["key"]] = hz
    for tx in state.test_executions:
        idx.by_key[tx["key"]] = tx
        idx.test_by_key[tx["key"]] = tx
        for link in tx.get("issuelinks") or []:
            if link.get("type") != "1 Relates":
                continue
            if link.get("target_issuetype") != "Story":
                continue
            target = link.get("target_key")
            if target:
                idx.tests_by_story[target].append(tx)

    return idx


# ─── Pure helpers (used by rules) ────────────────────────────────────────────


def extract_id(text: Optional[str], pattern: re.Pattern[str]) -> Optional[str]:
    """Apply a compiled regex to text, returning the first match group or None.

    If the regex has a group, returns ``match.group(1)``; otherwise the full
    matched substring. Returns None if `text` is falsy or no match.
    """
    if not text:
        return None
    m = pattern.search(text)
    if not m:
        return None
    if m.groups():
        return m.group(1)
    return m.group(0)


def compile_extractor(pattern: str) -> re.Pattern[str]:
    """Compile a project.yml extractor regex string to a re.Pattern."""
    return re.compile(pattern)


def design_input_extractor(cfg: ResolvedConfig) -> re.Pattern[str]:
    """Locate the DI extractor regex from the first DHF that publishes one.

    Falls back to ``r'\\b(DI-\\d+)\\b'`` if no DHF declares one — this keeps
    the project-agnostic contract: rules never read a literal prefix string.
    """
    for dhf in cfg.dhfs:
        for sch in dhf.dtm_schemas:
            di = sch.extractors.get("design_input_id")
            if di:
                return re.compile(di)
    return re.compile(r"\b(DI-\d+)\b")


def iter_layer_keys(state: JiraState, layer: str) -> Iterable[str]:
    """Yield issue keys from one layer of a JiraState."""
    bucket = {
        "epics": state.epics,
        "stories": state.stories,
        "hazards": state.hazards,
        "test_executions": state.test_executions,
    }[layer]
    for issue in bucket:
        yield issue["key"]
