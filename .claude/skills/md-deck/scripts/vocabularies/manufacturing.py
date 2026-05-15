"""Manufacturing / operations vocabulary pack (stub).

Activates manufacturing keyword routing in md-deck's icon classification. Load via:

    from icons import configure_vocabularies
    configure_vocabularies(["manufacturing"])

Status: scaffolding only. Add real entries as md-deck is exercised on
manufacturing / operations / supply-chain / plant-launch content. Each table
mirrors trunk `icons.py` shape; icon names referenced here must exist in
trunk `ICONS`.

Intended coverage (to be filled in):
    - Lean / Six Sigma (kaizen, kanban, takt time, OEE, defect rate)
    - Production (line, throughput, cycle time, lead time, WIP, finished goods)
    - Quality / inspection (FAI, PPAP, SPC, control chart, capability)
    - Supply chain (SKU, BOM, MRP, ERP, supplier, vendor, logistics)
    - Plant / facility (assembly line, cell, station, fixture, tooling)
    - Safety / EHS (hazard, near-miss, JSA, PPE, lockout-tagout)
    - Cohorts (suppliers, lines, plants, shifts, operators)
"""

KEYWORD_REGISTRY: list[tuple[list[str], str]] = []
INTENT_PHRASES: list[tuple[list[str], str]] = []
GROUP_ICONS: dict[str, str] = {}
GROUP_TITLE_HINTS: list[tuple[list[str], str]] = []
