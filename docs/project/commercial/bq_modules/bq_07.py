"""BQ-07 — US PCA/smart-pump segment share (honesty showcase: the denominator is A-003).

Contract: run(corpus_root, out, pins) per computations.py module dispatch.
Deterministic; computes only from pinned snapshots + the A-003 assumption record.
Definitions committed in plans/BQ-07.md.
"""

import yaml

import computations as C

SALES_DS = "commercial/internal-sales-accounts"
A003_PATH = "commercial/external-competitor-features/assumptions/A-003.yml"
IN_SEGMENT = ("PP3500", "PP3000", "IP5000")  # PCA + LVP smart pumps, matching A-003 scope
FY_ORDER = ["FY2024", "FY2025", "FY2026H1"]
FY_X = {"FY2024": "2024-12-31", "FY2025": "2025-12-31", "FY2026H1": "2026-06-30"}

# A-003 range constants, transcribed from the assumption record (cited [assume: A-003]).
# The asserts below break the computation LOUDLY if A-003's ranges are ever edited,
# so a stale transcription can never silently misprice the share.
BASE_LO, BASE_HI = 1_100_000, 1_800_000          # US installed base, units
DOLLARS_LO, DOLLARS_HI = 1_500_000_000, 3_000_000_000  # US segment $ market / yr
MARKET_CAGR_PCT = 7.3


def run(corpus_root, out, pins):
    rows, snap = C.load_pin_csv(corpus_root, pins, SALES_DS)
    src = f"{SALES_DS}@{snap}"

    a003 = yaml.safe_load(open(corpus_root / A003_PATH))
    assert a003.get("status") == "active", "A-003 is not active — refresh before answering"
    vr = a003["value_or_range"]
    assert "1.1M-1.8M" in vr and "$1.5B-$3.0B" in vr and "130k-230k" in vr, \
        "A-003 ranges changed — update the transcribed constants in bq_07.py"
    assert "7.3% CAGR" in a003["estimation_method"], \
        "A-003 market-growth figure changed — update bq_07.py"

    na = [r for r in rows if r["region"] == "NA" and r["product_line"] in IN_SEGMENT]
    units = {fy: sum(int(r["units_installed"]) for r in na if r["fy"] == fy) for fy in FY_ORDER}
    rev = {fy: sum(int(r["revenue_usd"]) for r in na if r["fy"] == fy) for fy in FY_ORDER}
    rev_annual = {fy: (rev[fy] * 2 if fy == "FY2026H1" else rev[fy]) for fy in FY_ORDER}

    def unit_share(fy):
        return (round(100.0 * units[fy] / BASE_HI, 3), round(100.0 * units[fy] / BASE_LO, 3))

    def rev_share(fy):
        return (round(100.0 * rev_annual[fy] / DOLLARS_HI, 2),
                round(100.0 * rev_annual[fy] / DOLLARS_LO, 2))

    u_lo, u_hi = unit_share("FY2026H1")
    r_lo, r_hi = rev_share("FY2026H1")
    # installed-base growth FY2024 -> FY2026H1 (2.5 fiscal-year span midpoint-to-midpoint
    # is over-precise for this data; use the 1.5-year span FY2024-year-end to FY2026-H1-end)
    growth_annualized = round(100.0 * ((units["FY2026H1"] / units["FY2024"]) ** (1 / 1.5) - 1), 1)
    units_added_annualized = (units["FY2026H1"] - units["FY2025"]) * 2

    headline = (f"US (NA-proxy) PCA/LVP smart-pump share is a RANGE, not a number: "
                f"~{u_lo}%–{u_hi}% of installed base and ~{r_lo}%–{r_hi}% of annual segment dollars "
                f"(A-003 denominator, LOW confidence); our installed base grew ~{growth_annualized}%/yr "
                f"vs the assumed market ~{MARKET_CAGR_PCT}%/yr — directionally gaining, from a tiny base "
                f"(mismatched bases: ours is UNIT growth of our NA in-segment book; A-003's rate is the "
                f"DOLLAR CAGR of the total US infusion-pump market — directional comparison only)")

    narrative = {
        "issues": [],
        "risks": [
            {"id": "R1", "severity": "high",
             "statement": "The entire share figure rests on A-003 (LOW confidence, triangulated from "
                          "public analyst-report summaries) — the denominator could be off by a large "
                          "factor, and the unit-share and dollar-share bases already tell different "
                          "stories (stock share vs flow share)",
             "mitigation": "Treat share as order-of-magnitude only; refresh A-003 annually or on any "
                           "new market report; consider purchasing analyst unit data to retire the "
                           "assumption",
             "evidence": ["assume: A-003", "derived: share-range"]},
            {"id": "R2", "severity": "medium",
             "statement": "US share is proxied by the NA region and the denominator is held constant "
                          "across fiscal years (market growth not modeled per-year) — both stated "
                          "simplifications of the committed plan",
             "mitigation": "Acceptable at order-of-magnitude precision; revisit if the sales dataset "
                           "gains a country field or A-003 gains dated vintages",
             "evidence": ["derived: share-range", "assume: A-003"]},
        ],
        "watch": [
            {"id": "W1",
             "statement": f"Growth-rate differential (ours ~{growth_annualized}%/yr vs market "
                          f"~{MARKET_CAGR_PCT}%/yr) is the only taking-share evidence available at "
                          "this share magnitude — watch it each quarter",
             "evidence": ["derived: growth-rate", "assume: A-003"]},
        ],
    }
    exps = C.evaluate_expectations("BQ-07", {})

    lines = [
        "# BQ-07 — US PCA/smart-pump segment share (a range, honestly)", "", C.BANNER, "",
        f"**Verdict**: {headline} [derived: v-main] [src: {src}] [assume: A-003]", "",
        "## Share as a range, by fiscal year", "",
        f"_US proxied by the NA region; in-segment = PP3500 + PP3000 + IP5000 [src: {src}] (PCA +",
        "LVP smart pumps, matching the assumption's scope); syringe and cloud-suite lines excluded —",
        "committed definitions in plans/BQ-07.md. Denominators held constant across FYs:",
        "an installed base of 1.1M–1.8M units and a segment market of $1.5B–$3.0B/yr [assume: A-003]._", "",
        "| FY | Our units (installed) | Unit share of installed base | Our revenue (direct book) | Revenue share of annual segment $ |",
        "|---|---|---|---|---|",
    ]
    for fy in FY_ORDER:
        ulo, uhi = unit_share(fy)
        rlo, rhi = rev_share(fy)
        ann = " (half-year actual; dollar share uses ×2)" if fy == "FY2026H1" else ""
        lines.append(f"| {fy} [src: {src}] [assume: A-003] | {units[fy]} | {ulo}%–{uhi}% | "
                     f"${rev[fy]:,}{ann} | {rlo}%–{rhi}% |")
    lines += [
        "",
        "## Taking share, or growing with the market?", "",
        f"- Our NA in-segment installed base grew {units['FY2024']} → {units['FY2026H1']} units "
        f"(FY2024 → FY2026H1), ~{growth_annualized}%/yr annualized [derived: growth-rate] [src: {src}].",
        f"- The market grows ~{MARKET_CAGR_PCT}%/yr under the assumed model [assume: A-003] — that "
        f"figure is the DOLLAR CAGR of the TOTAL US infusion-pump market, not a unit-growth rate and "
        f"not scoped to the PCA/LVP segment, while ours is unit growth of our own NA in-segment base; "
        f"the growth comparison is therefore directional only [derived: growth-rate]. At "
        f"~{units_added_annualized} units added/yr against an assumed annual demand of 130k–230k "
        f"units, share movement vs BD/Baxter is not observable in any data we hold; the defensible "
        f"claim is a growth-rate differential from a tiny base [derived: growth-rate] [assume: A-003].",
        "",
        "## Why this is a range, not a number", "",
        "- No public per-segment unit census exists; vendors do not disclose US installed base by",
        "  segment. The denominator is the assumption record — its confidence is LOW and its own",
        "  method note calls the fleet-ratio term the widest-error input [assume: A-003].",
        "- Unit share (stock: share of installed base) and revenue share (flow: share of annual",
        "  segment dollars) answer different questions and legitimately differ — a growing entrant's",
        "  flow share leads its stock share. Both are shown; neither is a point figure",
        "  [derived: share-range] [assume: A-003].",
        "- Competitor unit split (BD vs Baxter vs ICU installed units) is NOT public — published",
        "  as an unavailable series, never guessed [derived: competitor-unit-split].",
    ]
    lines += C.expectations_section(exps)
    lines += C.narrative_section(narrative)
    lines += [
        "## Method & provenance", "",
        f"- Numerators (units, revenue) measured from [src: {src}] (demo-fabricated direct book:",
        "  hardware + subscription; consumables/service flow through distributors and are absent).",
        "- Denominators and market growth from the assumption record [assume: A-003]; FY2026H1",
        "  revenue annualized ×2 for the dollar-share comparison only [derived: share-range].",
    ]

    trend_lo = [{"x": FY_X[fy], "y": unit_share(fy)[0]} for fy in FY_ORDER]
    trend_hi = [{"x": FY_X[fy], "y": unit_share(fy)[1]} for fy in FY_ORDER]
    data = {
        "bq": "BQ-07",
        "series": [
            {"id": "installed-units", "label": "Our NA in-segment installed base (FY2026H1)",
             "unit": "units", "kind": "stat", "evidence_class": "measured",
             "provenance": {"dataset": SALES_DS, "snapshot": snap},
             "points": [{"label": "PP3500 + PP3000 + IP5000 units installed, NA",
                         "value": units["FY2026H1"]}]},
            {"id": "share-range", "label": "FY2026H1 share range (A-003 denominator)", "unit": "%",
             "evidence_class": "assumed",
             "provenance": {"assumption": "A-003",
                            "note": f"numerator measured from {src}; denominator is the A-003 range "
                                    "(LOW confidence) — order-of-magnitude only"},
             "points": [
                 {"label": "unit share, low (vs 1.8M-unit base)", "value": u_lo},
                 {"label": "unit share, high (vs 1.1M-unit base)", "value": u_hi},
                 {"label": "revenue share, low (vs $3.0B market)", "value": r_lo},
                 {"label": "revenue share, high (vs $1.5B market)", "value": r_hi},
             ]},
            {"id": "units-by-line", "label": "NA in-segment units by product line (FY2026H1)",
             "unit": "units", "evidence_class": "measured",
             "provenance": {"dataset": SALES_DS, "snapshot": snap},
             "points": [{"label": pl,
                         "value": sum(int(r["units_installed"]) for r in na
                                      if r["fy"] == "FY2026H1" and r["product_line"] == pl)}
                        for pl in IN_SEGMENT]},
            {"id": "share-trend", "label": "Unit-share range by FY (constant A-003 denominator)",
             "unit": "%", "kind": "timeseries", "evidence_class": "assumed",
             "provenance": {"assumption": "A-003",
                            "note": "denominator held constant across FYs — trend shape is our "
                                    "unit growth, not market-adjusted share"},
             "lines": [{"label": "share vs 1.8M base (low)", "points": trend_lo},
                       {"label": "share vs 1.1M base (high)", "points": trend_hi}],
             "points": []},
            {"id": "growth-rate", "label": "Installed-base growth vs assumed market growth",
             "unit": "%/yr", "evidence_class": "derived",
             "derivation": {"method": "our rate = (units_FY2026H1 / units_FY2024)^(1/1.5yr) - 1; "
                                      "market rate transcribed from the assumption record",
                            "inputs": [f"src: {src}", "assume: A-003"]},
             "provenance": {"dataset": SALES_DS, "snapshot": snap,
                            "note": "mismatched bases: our rate is unit growth of the NA in-segment "
                                    "installed base; the market rate is A-003's dollar CAGR of the "
                                    "total US infusion-pump market — directional comparison only"},
             "points": [{"label": "our NA in-segment installed base", "value": growth_annualized},
                        {"label": "assumed market CAGR", "value": MARKET_CAGR_PCT}]},
            {"id": "competitor-unit-split", "label": "Competitor US unit split (BD / Baxter / ICU)",
             "unit": "units", "evidence_class": "unavailable",
             "provenance": {"note": "no public competitor unit census; would require purchased "
                                    "analyst unit data or vendor disclosures — never estimated here"},
             "points": []},
        ],
        "verdicts": [{"id": "v-main", "headline": headline, "evidence_class": "assumed"}],
        "narrative": narrative,
        "expectations": exps,
    }
    C.write(out, lines, data)
