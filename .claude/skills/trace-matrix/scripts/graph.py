"""Trace graph + gap detection.

Combines per-layer node lists into a single graph, computes reverse edges,
detects orphans, and flags broken references.

Layer ordering: UN → DI → SW → Architecture → V&V, with Risk as a parallel
overlay layer. The Software layer is optional — it is populated by item
DHFs whose design controls live in a separate software-requirements
artifact (e.g. Jira stories mirrored under `_jira/<arch>/<version>/`).
When empty, the graph behaves identically to the original
UN → DI → Architecture → V&V topology.

Edge-building philosophy (bidirectional, since version 8):
Each layer-pair relationship is logically undirected — either side may
author the claim. Authoring fields:

  * `traces_forward_ids`  — "I claim these upstream parents" (child→parent).
                            Used by DI rows ("Traces to UN"), SW rows
                            ("Traces to DI"), and Jira-mirror VER rows
                            ("Verifies"), as well as any future child-side
                            authoring.
  * `verification_ids`    — "I claim these downstream V&V children that
                            verify me" (parent→child). Used by DI rows
                            and SW rows whose Verification Method column
                            references VER-* IDs.
  * `verifies_di_ids`     — Legacy "I claim these DI parents" field set by
                            the default DI parser on the VER nodes it
                            emits. Functionally equivalent to
                            `traces_forward_ids` for those nodes; carried
                            for backward compatibility.

The engine collects every claim into a canonical (upstream_id,
downstream_id) edge set, deduping claims authored from both sides, and
builds the rendered edge + per-item forward/reverse lists from that set.
When the V&V layer is downstream of DI or SW and only one side authored
the claim, an asymmetric_trace warning is emitted on the V&V layer so
human reviewers can spot inconsistent authoring.
"""
from __future__ import annotations

from collections import defaultdict
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


# Historical edge `kind` labels — preserved for any downstream consumer
# (dashboards, drift reports) that filters edges by kind. Newer layer
# pairings fall back to `<upstream>_to_<downstream>`.
_EDGE_KIND_ALIASES = {
    ("user_needs", "design_inputs"): "un_to_di",
    ("design_inputs", "software"): "di_to_sw",
    ("design_inputs", "vnv"): "di_to_vnv",
    ("software", "vnv"): "sw_to_vnv",
}


def _kind_for(up_layer: str, down_layer: str) -> str:
    return _EDGE_KIND_ALIASES.get(
        (up_layer, down_layer), f"{up_layer}_to_{down_layer}"
    )


def build(layers: list[Layer]) -> TraceGraph:
    g = TraceGraph(layers=layers)
    layer_idx = {key: i for i, key in enumerate(LAYER_ORDER)}

    # V&V scope filter — narrower than v7. The trace matrix is scoped to
    # "tests that verify REQUIREMENTS" (DI or SW), not the full
    # test-execution universe (which a Jira mirror happily imports —
    # including defect-fix verifications and tests pointing at hazards
    # only). Drop V&V items whose own authored upstream claims
    # (traces_forward_ids / verifies_di_ids) name no requirement-layer
    # target.
    #
    # Critical: only run this filter when V&V has its own source
    # (jira-mirror or a real verification-protocols doc). When V&V is
    # derived from the DI parser's extras (no V&V source), every VER
    # node IS already a DI-verifying node by construction — filtering
    # would drop legitimate trace data, which is exactly the v7 bug
    # (orphaning DI-derived VERs when SW appears). The independent-
    # source check is the discriminator.
    vnv_layer = next((l for l in layers if l.key == "vnv"), None)
    if vnv_layer and vnv_layer.source_files and vnv_layer.items:
        req_ids: set[str] = set()
        for layer in layers:
            if layer.key not in ("design_inputs", "software"):
                continue
            for item in layer.items:
                req_ids.add(item["id"])
                jk = item.get("jira_key")
                if jk:
                    req_ids.add(jk)
        kept: list[dict] = []
        dropped = 0
        for it in vnv_layer.items:
            up_claims = (it.get("traces_forward_ids") or []) + (
                it.get("verifies_di_ids") or []
            )
            if any(t in req_ids for t in up_claims):
                kept.append(it)
            else:
                dropped += 1
        if dropped:
            vnv_layer.items = kept
            vnv_layer.warnings.append(
                f"scope_filter: dropped {dropped} V&V items whose authored "
                f"upstream targets are not in the requirements universe "
                f"(DI/SW)"
            )

    by_id = g.by_id()
    layer_of = g.layer_of()

    for layer in layers:
        for item in layer.items:
            item["traces_forward"] = []
            item["traces_reverse"] = []

    # Canonical-edge collection — each authored relationship is normalized
    # into a (upstream_id, downstream_id) tuple regardless of which side
    # wrote the claim. Both sides may author the same relationship; we
    # dedupe at the edge level and retain the authoring set for the
    # asymmetric-trace check below.
    canonical: dict[tuple[str, str], list[dict]] = defaultdict(list)
    broken: list[dict] = []

    def _record_claim(parent_id: str, child_id: str, author_id: str, field_name: str) -> None:
        """Record one authored claim. Routes broken refs and wrong-orientation
        claims to the gap report rather than into the edge set."""
        if parent_id not in by_id:
            broken.append({"from": author_id, "to": parent_id, "reason": "unknown_id"})
            return
        if child_id not in by_id:
            broken.append({"from": author_id, "to": child_id, "reason": "unknown_id"})
            return
        up_layer = layer_of[parent_id]
        down_layer = layer_of[child_id]
        # Risk is a parallel overlay — skip its layer-order check.
        if up_layer != "risk" and down_layer != "risk":
            if layer_idx.get(up_layer, 99) >= layer_idx.get(down_layer, 99):
                broken.append({
                    "from": author_id,
                    "to": parent_id if author_id == child_id else child_id,
                    "reason": "wrong_orientation",
                })
                return
        canonical[(parent_id, child_id)].append(
            {"author": author_id, "field": field_name}
        )

    # Walk every layer's items and collect claims from all three authoring
    # fields. Each field has a fixed convention:
    #   traces_forward_ids → "my upstream parent(s)" (child→parent claim)
    #   verifies_di_ids    → "my DI parent(s)"      (legacy child→parent)
    #   verification_ids   → "my V&V child(ren)"     (parent→child claim)
    for layer in layers:
        for item in layer.items:
            item_id = item["id"]

            for parent_id in item.get("traces_forward_ids", []) or []:
                _record_claim(parent_id, item_id, item_id, "traces_forward_ids")

            for parent_id in item.get("verifies_di_ids", []) or []:
                _record_claim(parent_id, item_id, item_id, "verifies_di_ids")

            for child_id in item.get("verification_ids", []) or []:
                _record_claim(item_id, child_id, item_id, "verification_ids")

    # Build the rendered edges + per-item forward/reverse lists from the
    # canonical set. Iteration is sorted for deterministic output.
    edges: list[dict] = []
    for (up_id, down_id) in sorted(canonical.keys()):
        up = by_id[up_id]
        down = by_id[down_id]
        kind = _kind_for(layer_of[up_id], layer_of[down_id])
        edges.append({"from": up_id, "to": down_id, "kind": kind})
        up["traces_forward"].append({"id": down_id, "summary": _label(down)})
        down["traces_reverse"].append({"id": up_id, "summary": _label(up)})

    # Asymmetric-trace warnings — scoped to the V&V layer because that's
    # the only downstream layer whose default doc shape (verification
    # column on the parent + "Verifies" column on the child) routinely
    # supports authoring from BOTH sides. UN↔DI and DI↔SW are
    # child-authored-only by convention, so absence of upstream
    # reciprocation is not informative for them. Architecture and Risk
    # are not requirement layers and are excluded.
    #
    # Further scoped to V&V layers whose source is independent of DI —
    # i.e., V&V has its own source files. When V&V is derived from the DI
    # parser's extras (no V&V source), the VER nodes are echoes of DI's
    # authoring and cannot "reciprocate" anything beyond what DI said;
    # flagging that absence as asymmetry produces noise. Independent V&V
    # authoring (e.g., Jira-mirror tests.md, or a real
    # verification-protocols.md) is where this check earns its keep.
    vnv_layer = next((l for l in layers if l.key == "vnv"), None)
    vnv_has_independent_source = bool(vnv_layer and vnv_layer.source_files)
    if vnv_has_independent_source:
        for (up_id, down_id), authorings in canonical.items():
            down_layer_key = layer_of[down_id]
            up_layer_key = layer_of[up_id]
            if down_layer_key != "vnv":
                continue
            if up_layer_key not in ("design_inputs", "software"):
                continue
            up_authored = any(a["author"] == up_id for a in authorings)
            down_authored = any(a["author"] == down_id for a in authorings)
            if up_authored and down_authored:
                continue
            if up_authored and not down_authored:
                down = by_id[down_id]
                has_own_up_claims = bool(
                    (down.get("traces_forward_ids") or [])
                    + (down.get("verifies_di_ids") or [])
                )
                if has_own_up_claims:
                    vnv_layer.warnings.append(
                        f"asymmetric_trace: {up_id} references {down_id} in "
                        f"its verification column, but {down_id} does not "
                        f"reciprocate (claims other parents instead)"
                    )

    # Orphan detection — runs against the populated per-item
    # forward/reverse lists. The rules are intentionally per-layer because
    # each layer's "coverage" obligation differs:
    #   UN must have at least one downstream DI.
    #   DI must have both an upstream UN and at least one downstream (SW or V&V).
    #   SW must have both an upstream DI and at least one downstream V&V.
    #   V&V must have at least one upstream requirement (DI or SW).
    #   Architecture is orphan only if isolated in both directions.
    orphans: dict[str, list[str]] = {l.key: [] for l in layers}
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
