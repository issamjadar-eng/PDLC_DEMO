# Mermaid Rule Packs

**Status (2026-04-21)**: Phase A scaffold under task ben/089. Stubs only — populated in Phase C.

## Purpose

Each pack defines docflow's Mermaid emission rules for one image element type. The image classifier (`scripts/classify_images.py`, written in Phase F) inspects each extracted image and returns `(image_type, mermaid_pack, classify_confidence)`. The per-image agent (`agents/interpret_image.md`, written in Phase G) loads the matching pack to govern Mermaid emission for that image.

This split solves the omnibus-prompt problem from converter.md v29: today the agent reads ~260 lines of F11 rules covering every image type before emitting any single image. After Phase C splits, each per-image agent loads ~140 lines (shared-fidelity + 1 type-specific pack) instead of 260.

## Pack registry

| Pack | Image type | Trigger | Rules cover |
|------|-----------|---------|-------------|
| `shared-fidelity.md` | (all) | Always loaded alongside one type pack | F11d containment fidelity, F11h layout fidelity, F11i edge-routing fidelity, F12 label quoting, F13 multi-occurrence emission |
| `type-a-flow.md` | (a) flow | Swim lanes, decision diamonds, fork/join, terminators detected | Standard flowchart emission; swim-lane subgraph patterns |
| `type-a-flow-nested.md` | (a) flow with nested regions | Nested iteration regions, dashed boundaries detected | Nested subgraph patterns; dashed boundary preservation |
| `type-b-logical.md` | (b) logical / architectural | No directional edges in source; layered or block-stack layout | No-edges containment; `~~~` invisible layout hints; never invent connectors |
| `type-c-component.md` | (c) component | Bounded regions (VPC/subnet/cluster) with leaf services inside | Cluster-granularity emission; containment fidelity |
| `type-c-network.md` | (c) network | Topology / adjacency without bounded regions | Topology emission; undirected adjacency |
| `type-d-matrix.md` | (d) matrix | Grid/heatmap/X×Y structure | Skip Mermaid emission; emit as table or HTML matrix |
| `type-e-ui-capture.md` | (e) UI screenshot | Screenshot, photo, mockup, application UI capture | Skip Mermaid emission; alt-text-only |
| `type-review.md` | review | Classifier ambiguous; needs human | `%% REVIEW:` flag protocol; do not emit Mermaid until resolved |

## Conventions

- Each pack starts with a YAML frontmatter block declaring `pack_name`, `version`, `applies_to_type`, `loaded_with` (always includes `shared-fidelity.md` for emit packs), `emit_required` (true/false).
- Pack body is ≤80 lines (shared-fidelity may be ≤120). Each pack must include a "When this pack DOESN'T apply" section pointing to sibling packs.
- Worked examples live in `.examples/` subfolder per pack — not loaded into agent context, available for human reference and test fixtures.

## Source for the split

Today's Phase 4.7 of `agents/converter.md` (lines 553–812, ~260 lines) contains the omnibus rules. Phase C extracts and reorganizes — does not rewrite.

## Changelog

- 2026-04-21: README created during task ben/089 Phase A scaffolding.
