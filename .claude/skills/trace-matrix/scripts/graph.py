"""Trace graph + gap detection.

Combines per-layer node lists into a single graph, computes reverse edges,
detects orphans, and flags broken references.

Layer ordering: UN → DI → SW → Architecture → V&V, with Risk as a parallel
overlay layer. The Software layer is optional — it is populated by item
DHFs whose design controls live in a separate software-requirements
artifact (e.g. Jira stories mirrored under `_jira/<arch>/<version>/`).
When empty, the graph behaves identically to the original
UN → DI → Architecture → V&V topology.
"""
from __future__ import annotations

from dataclasses import dataclass, field

LAYER_ORDER = ["user_needs", "design_inputs", "software", "architecture", "vnv", "risk"]
LAYER_TITLES = {
    "user_needs": "User Needs",
    "design_inputs": "Design Inputs",
    "software": "SW Reqs",
    "architecture": "Architecture",
    "vnv": "VnV",
    "risk": "Risk",
}


@dataclass
class Layer:
    key: str
    title: str
    id_prefix: str
    items: list[dict]
    missing_reason: str | None = None
    edges_known: bool = True
    warnings: list[str] = field(default_factory=list)
    source_files: list[str] = field(default_factory=list)


@dataclass
class TraceGraph:
    layers: list[Layer]
    edges: list[dict] = field(default_factory=list)
    gaps: dict = field(default_factory=dict)
    stats: dict = field(default_factory=dict)

    def by_id(self) -> dict[str, dict]:
        idx = {}
        for layer in self.layers:
            for item in layer.items:
                idx[item["id"]] = item
                jk = item.get("jira_key")
                if jk and jk not in idx:
                    idx[jk] = item
        return idx

    def layer_of(self) -> dict[str, str]:
        m = {}
        for layer in self.layers:
            for item in layer.items:
                m[item["id"]] = layer.key
                jk = item.get("jira_key")
                if jk and jk not in m:
                    m[jk] = layer.key
        return m


def _label(item: dict) -> str:
    return item.get("summary") or item.get("id", "")


def build(layers: list[Layer]) -> TraceGraph:
    g = TraceGraph(layers=layers)

    # V&V scope filter — drop tests whose `Verifies` target isn't an item in
    # the SW layer. The mirror still holds every Test Execution from Jira (for
    # drift / audit), but the V&V layer of the trace matrix is scoped to
    # "tests verifying requirements" only — defect-fix verifications and tests
    # pointing at items outside the requirements universe are out of trace
    # scope.
    sw_layer = next((l for l in layers if l.key == "software"), None)
    vnv_layer = next((l for l in layers if l.key == "vnv"), None)
    if (
        sw_layer
        and vnv_layer
        and not sw_layer.missing_reason
        and not vnv_layer.missing_reason
        and sw_layer.items
    ):
        sw_keys: set[str] = set()
        for it in sw_layer.items:
            sw_keys.add(it["id"])
            jk = it.get("jira_key")
            if jk:
                sw_keys.add(jk)
        kept: list[dict] = []
        dropped: list[dict] = []
        for it in vnv_layer.items:
            fwd = it.get("traces_forward_ids") or []
            if any(t in sw_keys for t in fwd):
                kept.append(it)
            else:
                dropped.append(it)
        vnv_layer.items = kept
        vnv_layer.warnings.append(
            f"scope_filter:vnv_to_sw dropped={len(dropped)}"
        )

    by_id = g.by_id()

    edges: list[dict] = []
    broken: list[dict] = []
    orphans: dict[str, list[str]] = {l.key: [] for l in layers}

    for layer in layers:
        for item in layer.items:
            item["traces_forward"] = []
            item["traces_reverse"] = []

    for layer in layers:
        for item in layer.items:
            fwd_ids = list(item.get("traces_forward_ids", []))

            if layer.key == "design_inputs":
                ver_ids = item.get("verification_ids", [])
                for vid in ver_ids:
                    target = by_id.get(vid)
                    if target is None:
                        broken.append({"from": item["id"], "to": vid, "reason": "unknown_id"})
                        continue
                    edges.append({"from": item["id"], "to": vid, "kind": "di_to_vnv"})
                    item["traces_forward"].append({"id": vid, "summary": _label(target)})
                    target["traces_reverse"].append({"id": item["id"], "summary": _label(item)})
                for un_id in fwd_ids:
                    target = by_id.get(un_id)
                    if target is None:
                        broken.append({"from": item["id"], "to": un_id, "reason": "unknown_id"})
                        continue
                    edges.append({"from": un_id, "to": item["id"], "kind": "un_to_di"})
                    target["traces_forward"].append({"id": item["id"], "summary": _label(item)})
                    item["traces_reverse"].append({"id": un_id, "summary": _label(target)})
                continue

            if layer.key == "software":
                # SW nodes point UP at parent DIs via traces_forward_ids;
                # the resulting edge is DI → SW (downstream-of-DI).
                for di_id in fwd_ids:
                    target = by_id.get(di_id)
                    if target is None:
                        broken.append({"from": item["id"], "to": di_id, "reason": "unknown_id"})
                        continue
                    edges.append({"from": di_id, "to": item["id"], "kind": "di_to_sw"})
                    target["traces_forward"].append({"id": item["id"], "summary": _label(item)})
                    item["traces_reverse"].append({"id": di_id, "summary": _label(target)})
                continue

            if layer.key == "vnv" and fwd_ids:
                # V&V nodes point UP at the SW (story) IDs they verify;
                # the resulting edge is SW → V&V.
                for sw_id in fwd_ids:
                    target = by_id.get(sw_id)
                    if target is None:
                        broken.append({"from": item["id"], "to": sw_id, "reason": "unknown_id"})
                        continue
                    edges.append({"from": sw_id, "to": item["id"], "kind": "sw_to_vnv"})
                    target["traces_forward"].append({"id": item["id"], "summary": _label(item)})
                    item["traces_reverse"].append({"id": sw_id, "summary": _label(target)})
                continue

            for fid in fwd_ids:
                target = by_id.get(fid)
                if target is None:
                    broken.append({"from": item["id"], "to": fid, "reason": "unknown_id"})
                    continue
                edges.append({"from": item["id"], "to": fid, "kind": f"{layer.key}_forward"})
                item["traces_forward"].append({"id": fid, "summary": _label(target)})
                target["traces_reverse"].append({"id": item["id"], "summary": _label(item)})

    for layer in layers:
        if layer.missing_reason:
            continue
        for item in layer.items:
            has_fwd = bool(item["traces_forward"])
            has_rev = bool(item["traces_reverse"])
            if layer.key == "user_needs" and not has_fwd:
                orphans[layer.key].append(item["id"])
            elif layer.key == "design_inputs" and (not has_rev or not has_fwd):
                orphans[layer.key].append(item["id"])
            elif layer.key == "software" and (not has_fwd or not has_rev):
                # SW node should trace up to a DI (parent) AND down to a V&V test.
                orphans[layer.key].append(item["id"])
            elif layer.key == "vnv" and not has_rev:
                orphans[layer.key].append(item["id"])
            elif layer.key == "architecture" and not has_fwd and not has_rev:
                orphans[layer.key].append(item["id"])

    empty_layers = [l.key for l in layers if l.missing_reason or not l.items]

    g.edges = edges
    g.gaps = {
        "orphans": orphans,
        "broken_refs": broken,
        "empty_layers": empty_layers,
    }

    stats: dict[str, dict] = {}
    for layer in layers:
        s: dict = {"count": len(layer.items)}
        if layer.missing_reason:
            s["missing_reason"] = layer.missing_reason
        if layer.key == "architecture":
            s["edges_known"] = layer.edges_known
        s["with_forward"] = sum(1 for it in layer.items if it["traces_forward"])
        s["with_reverse"] = sum(1 for it in layer.items if it["traces_reverse"])
        s["orphan"] = len(orphans.get(layer.key, []))
        stats[layer.key] = s
    g.stats = stats

    return g
