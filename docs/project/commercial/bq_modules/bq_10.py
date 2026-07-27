"""BQ-10 — 5-year TCO per pump vs Alaris / Spectrum IQ / Plum 360.

Contract: run(corpus_root, out, pins) per computations.py module dispatch.
Deterministic. Our TCO from commercial.yml constants; competitor side is the A-004
assumption RANGE (consumables excluded per the record — restated in the report).
Verdict is capped at "indicative, assumption-bounded" per plans/BQ-10.md.
"""

import yaml

import computations as C

CF_DS = "commercial/external-competitor-features"
A004_PATH = "commercial/external-competitor-features/assumptions/A-004.yml"
COMPETITOR_PRODUCTS = ["Alaris", "Spectrum IQ", "Plum 360"]
OUR_PRODUCT = "PainEase PCA Advanced (PP3500)"
FEATURE_ATTRS = ["ders_drug_library", "wireless_connectivity", "predictive_monitoring",
                 "battery_hours", "flow_accuracy_pct"]

# A-004 range constants, transcribed from the assumption record (cited [assume: A-004]).
# The asserts in run() break LOUDLY if the record's ranges are edited, so a stale
# transcription can never silently move the comparison.
COMP_TCO_LO, COMP_TCO_HI = 3_000, 15_000       # indicative 5-yr TCO, capital + service only
CAP_LO, CAP_HI = 2_200, 6_900                  # LVP capital, standalone
CAP_NET_LO, CAP_NET_HI = 4_400, 13_700         # capital once networked/EMR-integrated
SVC_LO, SVC_HI = 150, 250                      # service per pump per year


def run(corpus_root, out, pins):
    p = C.params_for("BQ-10")
    rows, snap = C.load_pin_csv(corpus_root, pins, CF_DS)
    src = f"{CF_DS}@{snap}"
    horizon = int(p["horizon_years"])

    a004 = yaml.safe_load(open(corpus_root / A004_PATH))
    assert a004.get("status") == "active", "A-004 is not active — refresh before answering"
    vr = a004["value_or_range"]
    assert "$3.0k-$15k" in vr and "$2.2k-$6.9k" in vr and "$150-$250" in vr \
        and "$4.4k-$13.7k" in vr, \
        "A-004 ranges changed — update the transcribed constants in bq_10.py"
    # COMP_TCO_LO/HI transcribe A-004's 5-YEAR figure — a different horizon would
    # relabel that range and compare mismatched horizons
    assert horizon == 5, \
        "horizon_years != 5 but the A-004 TCO range is horizon-specific (5-yr) — retranscribe"

    capital = int(p["pp3500_capital_usd"])
    cloud = int(p["cloud_suite_per_pump_annual_usd"])
    consumables = int(p["consumables_per_pump_annual_usd"])
    service = int(p["service_per_pump_annual_usd"])
    our_full = capital + horizon * (cloud + consumables + service)
    our_comparable = capital + horizon * service          # A-004's basis: capital + service only
    comp_svc_5yr = (SVC_LO * horizon, SVC_HI * horizon)

    cells = {}   # (product, attribute) -> (value, verified)
    for r in rows:
        # cell() renders only the "verify" status specially — any other unexpected
        # status would silently render as settled fact, so guard the vocabulary
        assert r["verified"] in ("yes", "verify"), \
            f"unexpected verified status {r['verified']!r} for {r['product']}/{r['attribute']} — update bq_10.py's cell rendering"
        cells[(r["product"], r["attribute"])] = (r["value"], r["verified"])

    headline = (f"Indicative, assumption-bounded: our {horizon}-yr TCO is ${our_full:,}/pump all-in "
                f"(${our_comparable:,} on the capital+service basis) vs a class-wide competitor "
                f"range of ~${COMP_TCO_LO:,}–${COMP_TCO_HI:,} on capital+service ONLY — competitor "
                f"consumables and software subscription are undisclosed and excluded, so their true "
                f"all-in TCO sits ABOVE that range; the ranges overlap and no hard we-win claim is "
                f"supportable")

    exps = C.evaluate_expectations("BQ-10", {})

    narrative = {"issues": [], "risks": [], "watch": []}
    narrative["risks"].append({
        "id": "R1", "severity": "high",
        "statement": "The comparison is not like-for-like by construction: the competitor range "
                     "excludes consumables (undisclosed) and quantifies software subscription only "
                     "as 'required, magnitude unknown', while our figure includes both — the "
                     "spread understates competitor cost",
        "mitigation": "Present only the capital+service basis side-by-side in buyer-facing "
                      "material; state the exclusions verbatim from the assumption record",
        "evidence": ["assume: A-004", "derived: tco-comparison"]})
    narrative["risks"].append({
        "id": "R2", "severity": "medium",
        "statement": "Our own cost constants are demo stand-ins, not finance-validated rates — "
                     "both sides of the buyer's spreadsheet are currently unvalidated",
        "mitigation": "Have finance ratify the four per-pump constants before external use; then "
                      "re-answer",
        "evidence": ["config: commercial.yml"]})
    narrative["watch"].append({
        "id": "W1",
        "statement": "A-004's refresh trigger is a new procurement award / GPO disclosure / analyst "
                     "pricing commentary — any of these should prompt a re-answer",
        "evidence": ["assume: A-004"]})

    lines = [
        "# BQ-10 — The buyer's 5-year TCO spreadsheet (indicative, assumption-bounded)", "",
        C.BANNER, "",
        "_Our per-pump cost constants are demo stand-ins, not finance-validated rates "
        "[config: commercial.yml]; the competitor side is a real-compiled, assumption-bounded "
        "range [assume: A-004]._", "",
        f"**Verdict**: {headline} [derived: v-main] [config: commercial.yml] [assume: A-004]", "",
        f"## Our {horizon}-yr TCO per pump (declared constants) [config: commercial.yml]", "",
        "| Component | Basis | 5-yr amount |",
        "|---|---|---|",
        f"| PP3500 capital [config: commercial.yml] | one-time | ${capital:,} |",
        f"| Cloud Suite subscription [config: commercial.yml] | ${cloud}/yr × {horizon} | "
        f"${cloud * horizon:,} |",
        f"| Consumables [config: commercial.yml] | ${consumables}/yr × {horizon} | "
        f"${consumables * horizon:,} |",
        f"| Service [config: commercial.yml] | ${service}/yr × {horizon} | ${service * horizon:,} |",
        f"| **Total (all-in)** [derived: our-tco] | | **${our_full:,}** |",
        f"| **Capital + service only** (the A-004-comparable basis) [derived: our-tco] | | "
        f"**${our_comparable:,}** |",
        "",
        "## Competitor side — a RANGE, and why it is one", "",
        f"- Realized pump prices are negotiated under confidential GPO/IDN contracts and never "
        f"published; the competitor figures below are the assumption record's compiled range "
        f"[assume: A-004].",
        f"- Capital: ${CAP_LO:,}–${CAP_HI:,} standalone LVP, effectively ${CAP_NET_LO:,}–"
        f"${CAP_NET_HI:,} once networked/EMR-integrated [assume: A-004].",
        f"- Service: ${SVC_LO}–${SVC_HI} per pump/yr → ${comp_svc_5yr[0]:,}–${comp_svc_5yr[1]:,} "
        f"over {horizon} years [assume: A-004].",
        f"- Indicative {horizon}-yr TCO, capital + service only: ~${COMP_TCO_LO:,}–"
        f"${COMP_TCO_HI:,} [assume: A-004].",
        "- EXCLUDED on the competitor side, restated from the record: consumables pricing",
        "  (not publicly disclosed) and software-subscription magnitude (required annually,",
        "  unquantified). Their true all-in TCO is therefore strictly above the quoted range",
        "  [assume: A-004].",
        "- Alaris, Spectrum IQ, and Plum 360 share this one class-wide range [assume: A-004] —",
        "  public pricing does not split by vendor.",
        "",
        "## Feature context per competitor (curated matrix; verification status carried)", "",
        "_Cells marked “(verify)” have a named but independently unfetched source; “—” means no",
        "confirmable source exists and the value is deliberately absent, not guessed",
        f"[src: {src}]._", "",
        "| Attribute | PP3500 (ours) | Alaris | Spectrum IQ | Plum 360 |",
        "|---|---|---|---|---|",
    ]

    def cell(product, attr):
        v = cells.get((product, attr))
        if not v:
            return "—"
        val, verified = v
        return f"{val} (verify)" if verified == "verify" else str(val)

    for attr in FEATURE_ATTRS:
        lines.append(f"| {attr} [src: {src}] | {cell(OUR_PRODUCT, attr)} | {cell('Alaris', attr)} | "
                     f"{cell('Spectrum IQ', attr)} | {cell('Plum 360', attr)} |")
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Data gap (stated, not papered over)", "",
        "- No TCO history exists — a trend needs dated refreshes of the pricing assumption as",
        "  procurement disclosures surface; the history series is published as unavailable, not",
        "  faked [derived: tco-history].",
        "",
        "## Method & provenance", "",
        f"- Our constants and the {horizon}-yr horizon are declared plan constants "
        f"[config: commercial.yml]; totals are arithmetic over them [derived: our-tco].",
        f"- Competitor range transcribed from the assumption record (confidence: "
        f"{a004['confidence']}) [assume: A-004]; feature cells measured from [src: {src}].",
        "- No catalog expectations are declared for this question — none are invented.",
    ]

    data = {
        "bq": "BQ-10",
        "series": [
            {"id": "our-tco", "label": f"Our {horizon}-yr TCO per pump", "unit": "USD",
             "kind": "stat", "evidence_class": "derived",
             "derivation": {"method": f"capital + {horizon} × (cloud + consumables + service) "
                                      "over the declared per-pump constants",
                            "inputs": ["config: commercial.yml"]},
             "provenance": {"note": "declared plan constants in commercial.yml (demo stand-ins "
                                    "for finance-validated rates)"},
             "points": [{"label": "all-in (capital + cloud + consumables + service)",
                         "value": our_full},
                        {"label": "capital + service only (A-004-comparable basis)",
                         "value": our_comparable}]},
            {"id": "tco-comparison", "label": f"{horizon}-yr TCO, capital+service basis: us vs "
                                              "class-wide competitor range", "unit": "USD",
             "evidence_class": "assumed",
             "provenance": {"assumption": "A-004",
                            "note": "competitor side excludes consumables and software "
                                    "subscription (undisclosed) — their true all-in TCO is above "
                                    "this range; ours from commercial.yml constants"},
             "points": [{"label": "PP3500 (capital + service)", "value": our_comparable},
                        {"label": "competitor range, low", "value": COMP_TCO_LO},
                        {"label": "competitor range, high", "value": COMP_TCO_HI}]},
            {"id": "our-tco-components", "label": f"Our {horizon}-yr TCO components", "unit": "USD",
             "evidence_class": "derived",
             "derivation": {"method": f"per-pump constants × {horizon}-yr horizon (capital one-time)",
                            "inputs": ["config: commercial.yml"]},
             "provenance": {"note": "declared plan constants in commercial.yml"},
             "points": [{"label": "capital", "value": capital},
                        {"label": f"cloud subscription × {horizon}yr", "value": cloud * horizon},
                        {"label": f"consumables × {horizon}yr", "value": consumables * horizon},
                        {"label": f"service × {horizon}yr", "value": service * horizon}]},
            {"id": "feature-context", "label": "Feature cells (value + verification status)",
             "unit": "", "evidence_class": "measured",
             "provenance": {"dataset": CF_DS, "snapshot": snap},
             "points": [{"label": f"{prod} — {attr}", "value": cell(prod, attr)}
                        for prod in [OUR_PRODUCT] + COMPETITOR_PRODUCTS
                        for attr in FEATURE_ATTRS if cells.get((prod, attr))]},
            {"id": "tco-history", "label": "TCO position over time", "unit": "USD",
             "kind": "timeseries", "evidence_class": "unavailable",
             "provenance": {"note": "single A-004 vintage and single curated-matrix snapshot — a "
                                    "history needs dated assumption refreshes (procurement "
                                    "disclosures, GPO pricing, analyst commentary); not faked"},
             "lines": [], "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "assumed"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
