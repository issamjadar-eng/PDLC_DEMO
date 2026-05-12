"""Unit tests for the bidirectional edge philosophy in `scripts/graph.py`.

Covers the post-v8 refactor: edges build from claims authored on either
side of a layer pair (or both), DI-derived V&V nodes survive when SW
exists (the v7 scope filter is gone), SW→VER edges build from SW rows'
`verification_ids`, and asymmetric-trace warnings fire only when V&V has
an independent source.

Generic fixtures — no project-specific names. Run from project root:
    python3 -m unittest .claude/skills/trace-matrix/tests/test_graph_bidirectional.py
or:
    python3 .claude/skills/trace-matrix/tests/test_graph_bidirectional.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPT_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from graph import Layer, build  # noqa: E402


def _node(node_id: str, **kwargs) -> dict:
    base = {"id": node_id, "summary": node_id, "full_text": node_id}
    base.update(kwargs)
    return base


def _layers(
    un=None, di=None, sw=None, arch=None, vnv=None, vnv_source=None
) -> list[Layer]:
    """Build a layer list from per-layer node arrays. `vnv_source` toggles
    whether the V&V layer has an independent source file (controls
    asymmetric-trace warning gating)."""
    return [
        Layer(key="user_needs", title="UN", id_prefix="UN", items=un or []),
        Layer(key="design_inputs", title="DI", id_prefix="DI", items=di or []),
        Layer(key="software", title="SW", id_prefix="SW", items=sw or []),
        Layer(key="architecture", title="ARCH", id_prefix="M", items=arch or []),
        Layer(
            key="vnv",
            title="VnV",
            id_prefix="VER",
            items=vnv or [],
            source_files=vnv_source or [],
        ),
        Layer(key="risk", title="Risk", id_prefix="HZ", items=[]),
    ]


def _edge_kinds(graph) -> dict:
    out = {}
    for e in graph.edges:
        out[e["kind"]] = out.get(e["kind"], 0) + 1
    return out


class BidirectionalEdgeTest(unittest.TestCase):
    def test_un_to_di_built_from_di_authoring(self):
        un = [_node("UN-1")]
        di = [_node("DI-1", traces_forward_ids=["UN-1"])]
        g = build(_layers(un=un, di=di))
        self.assertIn("un_to_di", _edge_kinds(g))
        self.assertEqual(_edge_kinds(g)["un_to_di"], 1)
        self.assertEqual(di[0]["traces_reverse"][0]["id"], "UN-1")
        self.assertEqual(un[0]["traces_forward"][0]["id"], "DI-1")

    def test_di_to_sw_built_from_sw_authoring(self):
        di = [_node("DI-1")]
        sw = [_node("SW-1", traces_forward_ids=["DI-1"])]
        g = build(_layers(di=di, sw=sw))
        self.assertEqual(_edge_kinds(g).get("di_to_sw"), 1)

    def test_di_to_vnv_built_from_di_verification_ids(self):
        # Parent-side authoring: DI lists a child VER in its verification
        # column. The DI parser also emits a VER node with
        # verifies_di_ids set, but the engine should produce only ONE
        # canonical edge (both claims resolve to the same edge key).
        di = [_node("DI-1", verification_ids=["VER-1"])]
        vnv = [_node("VER-1", verifies_di_ids=["DI-1"])]
        g = build(_layers(di=di, vnv=vnv))
        self.assertEqual(_edge_kinds(g).get("di_to_vnv"), 1)

    def test_sw_to_vnv_built_from_sw_verification_ids(self):
        # The v7 graph engine ignored SW's verification_ids. v8 must
        # honor it — this is the parallel of DI's verification column.
        sw = [_node("SW-1", traces_forward_ids=[], verification_ids=["VER-1"])]
        vnv = [_node("VER-1")]
        g = build(_layers(sw=sw, vnv=vnv))
        self.assertEqual(_edge_kinds(g).get("sw_to_vnv"), 1)

    def test_sw_to_vnv_built_from_vnv_authoring(self):
        # Jira-mirror direction: V&V row authors the upstream pointer
        # via traces_forward_ids. The engine should still produce a
        # canonical SW→VER edge.
        sw = [_node("SW-1")]
        vnv = [_node("VER-1", traces_forward_ids=["SW-1"])]
        g = build(_layers(sw=sw, vnv=vnv))
        self.assertEqual(_edge_kinds(g).get("sw_to_vnv"), 1)

    def test_bidirectional_authoring_deduplicates_to_one_edge(self):
        # Both sides claim the same relationship. Exactly one canonical
        # edge should appear.
        di = [_node("DI-1", verification_ids=["VER-1"])]
        vnv = [_node("VER-1", traces_forward_ids=["DI-1"])]
        g = build(_layers(di=di, vnv=vnv))
        self.assertEqual(_edge_kinds(g).get("di_to_vnv"), 1)


class ScopeFilterTest(unittest.TestCase):
    def test_di_derived_vnv_survives_when_sw_exists(self):
        # Regression guard for the v7 scope filter bug. Previously the
        # engine dropped DI-derived VER nodes (which lack
        # traces_forward_ids→SW) the moment a SW layer appeared. v8
        # keeps them because V&V has no independent source — the filter
        # should not run.
        di = [_node("DI-1", verification_ids=["VER-1"])]
        sw = [_node("SW-1", traces_forward_ids=["DI-1"])]
        vnv = [_node("VER-1", verifies_di_ids=["DI-1"])]
        g = build(_layers(di=di, sw=sw, vnv=vnv))
        vnv_layer = next(l for l in g.layers if l.key == "vnv")
        self.assertEqual(len(vnv_layer.items), 1)
        self.assertEqual(vnv_layer.items[0]["id"], "VER-1")

    def test_jira_mirror_vnv_drops_non_requirement_targets(self):
        # When V&V has its own source (jira-mirror or a real protocols
        # doc), the test-execution universe may include items that
        # don't verify any requirement — defect-fix verifications,
        # hazards-only tests, etc. The scope filter drops these so the
        # trace matrix stays scoped to requirements-verifying tests.
        sw = [_node("SW-1")]
        vnv = [
            _node("VER-1", traces_forward_ids=["SW-1"]),     # keeps — points at SW
            _node("VER-2", traces_forward_ids=["DEFECT-9"]),  # drops — non-requirement
            _node("VER-3", traces_forward_ids=[]),            # drops — points nowhere
        ]
        g = build(
            _layers(sw=sw, vnv=vnv, vnv_source=["fake/tests.md"])
        )
        vnv_layer = next(l for l in g.layers if l.key == "vnv")
        ids = [it["id"] for it in vnv_layer.items]
        self.assertEqual(ids, ["VER-1"])
        self.assertTrue(any("scope_filter" in w for w in vnv_layer.warnings))

    def test_scope_filter_keeps_vnv_pointing_at_di(self):
        # The v7 filter only kept VERs reciprocating SW, dropping those
        # that pointed at DI directly. v8 broadens to "any requirement"
        # so a VER that verifies a DI (even if no SW intermediary
        # exists) survives.
        di = [_node("DI-1")]
        vnv = [_node("VER-1", traces_forward_ids=["DI-1"])]
        g = build(
            _layers(di=di, vnv=vnv, vnv_source=["fake/tests.md"])
        )
        vnv_layer = next(l for l in g.layers if l.key == "vnv")
        self.assertEqual([it["id"] for it in vnv_layer.items], ["VER-1"])


class AsymmetricTraceWarningTest(unittest.TestCase):
    def test_no_warning_when_vnv_has_no_independent_source(self):
        # When V&V is DI-derived (no source files), the VER node's
        # authoring is just a side-effect of the DI parser — there is no
        # independent VER source to disagree. Suppress the warning.
        di = [_node("DI-1", verification_ids=["VER-1"])]
        sw = [_node("SW-1", traces_forward_ids=["DI-1"], verification_ids=["VER-1"])]
        vnv = [_node("VER-1", verifies_di_ids=["DI-1"])]
        g = build(_layers(di=di, sw=sw, vnv=vnv, vnv_source=None))
        vnv_layer = next(l for l in g.layers if l.key == "vnv")
        asym = [w for w in vnv_layer.warnings if w.startswith("asymmetric_trace")]
        self.assertEqual(asym, [])

    def test_warning_fires_when_vnv_has_independent_source_and_no_reciprocation(self):
        # V&V source exists (jira-mirror style). VER-1 claims to verify
        # SW-1 only. DI-1 also references VER-1 in its verification
        # column. The asymmetry — DI's claim, no reciprocation from VER
        # — is meaningful and the warning should fire.
        di = [_node("DI-1", verification_ids=["VER-1"])]
        sw = [_node("SW-1", traces_forward_ids=["DI-1"])]
        vnv = [_node("VER-1", traces_forward_ids=["SW-1"])]
        g = build(
            _layers(di=di, sw=sw, vnv=vnv, vnv_source=["fake/tests.md"])
        )
        vnv_layer = next(l for l in g.layers if l.key == "vnv")
        asym = [w for w in vnv_layer.warnings if w.startswith("asymmetric_trace")]
        self.assertEqual(len(asym), 1)
        self.assertIn("DI-1", asym[0])
        self.assertIn("VER-1", asym[0])

    def test_no_warning_when_both_sides_authored(self):
        di = [_node("DI-1", verification_ids=["VER-1"])]
        vnv = [_node("VER-1", traces_forward_ids=["DI-1"])]
        g = build(
            _layers(di=di, vnv=vnv, vnv_source=["fake/tests.md"])
        )
        vnv_layer = next(l for l in g.layers if l.key == "vnv")
        asym = [w for w in vnv_layer.warnings if w.startswith("asymmetric_trace")]
        self.assertEqual(asym, [])


class BrokenRefsTest(unittest.TestCase):
    def test_unknown_upstream_in_traces_forward_ids_is_broken(self):
        di = [_node("DI-1", traces_forward_ids=["UN-NOPE"])]
        g = build(_layers(di=di))
        self.assertEqual(len(g.gaps["broken_refs"]), 1)
        self.assertEqual(g.gaps["broken_refs"][0]["to"], "UN-NOPE")
        self.assertEqual(g.gaps["broken_refs"][0]["reason"], "unknown_id")

    def test_unknown_child_in_verification_ids_is_broken(self):
        di = [_node("DI-1", verification_ids=["VER-NOPE"])]
        g = build(_layers(di=di))
        self.assertEqual(len(g.gaps["broken_refs"]), 1)
        self.assertEqual(g.gaps["broken_refs"][0]["to"], "VER-NOPE")


class OrphanTest(unittest.TestCase):
    def test_di_with_no_un_parent_is_orphan(self):
        di = [_node("DI-1", verification_ids=["VER-1"])]
        vnv = [_node("VER-1")]
        g = build(_layers(di=di, vnv=vnv))
        self.assertIn("DI-1", g.gaps["orphans"]["design_inputs"])

    def test_sw_with_no_vnv_child_is_orphan(self):
        un = [_node("UN-1")]
        di = [_node("DI-1", traces_forward_ids=["UN-1"])]
        sw = [_node("SW-1", traces_forward_ids=["DI-1"])]
        g = build(_layers(un=un, di=di, sw=sw))
        self.assertIn("SW-1", g.gaps["orphans"]["software"])

    def test_vnv_without_parent_is_orphan(self):
        vnv = [_node("VER-1")]
        g = build(_layers(vnv=vnv))
        self.assertIn("VER-1", g.gaps["orphans"]["vnv"])


if __name__ == "__main__":
    unittest.main()
