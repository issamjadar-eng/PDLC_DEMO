"""Trace graph + gap detection.

Combines per-layer node lists into a single graph, computes reverse edges,
detects orphans, and flags broken references.

Layer ordering: UN → DI → Architecture → V&V, with Risk as a parallel
overlay layer that may point into DI and V&V.
"""
from __future__ import annotations

from dataclasses import dataclass, field

LAYER_ORDER = ["user_needs", "design_inputs", "architecture", "vnv", "risk"]
LAYER_TITLES = {
    "user_needs": "User Needs",
    "design_inputs": "Design Inputs",
    "architecture": "Architecture",
    "vnv": "Verification & Validation",
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
        return idx

    def layer_of(self) -> dict[str, str]:
        m = {}
        for layer in self.layers:
            for item in layer.items:
                m[item["id"]] = layer.key
        return m


def _label(item: dict) -> str:
    return item.get("summary") or item.get("id", "")


def build(layers: list[Layer]) -> TraceGraph:
    g = TraceGraph(layers=layers)
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
