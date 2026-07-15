# Trace-Matrix Adapter Analysis Notes

Rationale log for project adapters under `adapters/`, per the trace-matrix
skill's `init` step 4 (each generated adapter gets a "what the defaults
returned / what the source actually looks like / what the adapter does
differently" block).

## `software.py` — 2026-05-12 (task ben/049)

See the adapter's module docstring: the three system-DHF SRS docs share the
DI-convention column shape but with `SW ID` / `Traces to DI` columns; the
shipped default software parser is a no-op, so a project override was
authored. (This note backfilled 2026-07-14 — the adapter predates this file.)

## `risk.py` — 2026-07-14 (task ben/102)

**What the defaults returned:** `risk` layer for pca-device parsed 0 items
with warning `source is awaiting-content placeholder` — `trace-matrix.yml`
pointed at `risk-management/risk-strategy.md`, a strategy stub, not risk
data. Even against a populated hazard doc, the shipped default risk parser
expects a `Hazard ID` column and never populates `traces_forward_ids`, so
hazards would render with zero edges to design inputs.

**What the source actually looks like:** the backfilled
`docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-003-hazard-analysis.md`
instantiates QMS FORM GL-TMP-RM-003 — a single GFM table whose columns are
`HAZ ID | Hazard (ISO 14971 Annex C class) | Hazardous Situation |
Foreseeable Sequence of Events | Harm | S (pre) | P (pre) | Risk (pre) |
Controls (design / protective / info) | Design Input(s) | Verification(s) |
S (post) | P (post) | Residual Risk | New Hazards Introduced?`. IDs are
`HAZ-###` per the FORM's exemplar row; the `Design Input(s)` cell holds
comma-separated bare DI IDs.

**What the adapter does differently:** parses the FORM columns (ID column
`HAZ ID`, prefix `HAZ`), extracts `DI-\d+` tokens from `Design Input(s)`
into `traces_forward_ids` (risk is a parallel overlay in graph.py → builds
`design_inputs_to_risk` edges), and folds situation / harm / pre-scores /
controls / residual region into `full_text` for the console's expandable
row. `Verification(s)` is deliberately not parsed into edges — its VER
identifiers are planned protocols, not guaranteed nodes in the DI-derived
V&V layer; claiming them would create broken_refs noise. `residual` region
is surfaced via the `criticality` field so the console badge shows
ALARP / Acceptable.

**Config change:** `trace-matrix.yml` pca-device `risk.source` →
`GL-TMP-RM-003-hazard-analysis.md`, `id_prefix: HZ` → `HAZ`. Other DHFs
still point at their `risk-strategy.md` placeholders; when their GL-TMP-RM-003
instances get backfilled, flip source + prefix the same way — this adapter
is shared (default column names match the FORM).
