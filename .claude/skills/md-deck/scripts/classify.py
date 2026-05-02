#!/usr/bin/env python3
"""md-deck v0.4 — classify.py

Pure-stdlib feature extractor + component scorer for md-deck's 3-variant
selection engine.

Public API:
    extract_features(slide: dict) -> dict[str, float]
    score_components(features, registry, top_k=3, cluster_spread=True)
        -> list[ComponentScore]

A `slide` here is a synthesized base slide dict from build.synthesize_slides
(types: card-grid, list-slide, prose-slide, table-slide, quote-slide,
image-feature, etc.). The classifier produces a feature vector and scores
every viable component in the registry.

Cluster-spread bias (open-question 7, locked): when the top-3 by raw score
would all come from the same cluster, the third slot is forcibly drawn from
a different cluster — even if its raw score is lower — so the user sees
genuinely different visual treatments.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

_DATE_RE = re.compile(
    r"\b("
    r"week\s*\d+|q[1-4]\b|h[12]\b|"
    r"\d{4}[-/]\d{1,2}([-/]\d{1,2})?|"
    r"\d{4}-q[1-4]|"
    r"jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
    r")\b",
    re.IGNORECASE,
)
_NUMERIC_RE = re.compile(r"(\d+%|\$\s*\d+|\d+\s*x\b|\d+(\.\d+)?\s*(bps|ms|kg|mg|sec|min|hr))")
_PERCENT_RE = re.compile(r"\b\d+(\.\d+)?%")
_RATIO_PHRASE_RE = re.compile(
    r"\b(reduction|down|up|increase|decrease|improvement|drop|rise|cut)\s+(by\s+)?\d+",
    re.IGNORECASE,
)
_BIPOLAR_PHRASES = (
    "in vs out", "in-scope", "out of scope", "out-of-scope", "before / after",
    "before/after", "carve-out", "carve out", "us vs them", "us vs. them",
    "then vs now", "now vs then", "human/agent", "human-agent", "agent/human",
)
_DEFINITIONAL_PHRASES = (
    "what an ", "what is ", "what are ", "where the ", "how it works",
    "actually is", "what \"",
)
_COHORT_NOUNS = (
    "advisor", "advisors", "kol", "kols", "persona", "personas", "investigator",
    "investigators", "site", "sites", "predicate", "predicates", "test case",
    "test cases", "rule", "rules", "hazard", "hazards", "milestone",
    "milestones", "metric", "metrics", "team",
)


def _all_text(slide: dict) -> str:
    """Concatenate every textual surface on the slide for keyword matching."""
    parts: list[str] = [str(slide.get("title", "")), str(slide.get("lead", "")), str(slide.get("quote", ""))]
    for t in slide.get("tiles", []) or []:
        if isinstance(t, dict):
            parts.extend([str(t.get("label", "")), str(t.get("subtitle", ""))])
    for it in slide.get("items", []) or []:
        if isinstance(it, (list, tuple)):
            parts.append(" ".join(str(x) for x in it))
        else:
            parts.append(str(it))
    parts.extend(str(p) for p in (slide.get("paragraphs") or []))
    parts.extend(str(b) for b in (slide.get("bullets") or []))
    table = slide.get("table") or {}
    for row in table.get("rows", []) or []:
        parts.append(" ".join(str(c) for c in row))
    parts.extend(str(c) for c in (table.get("header") or []))
    return " ".join(p for p in parts if p)


def _list_units(slide: dict) -> list[str]:
    """Return one-string-per-bullet for the slide's primary enumerated content."""
    if slide.get("tiles"):
        return [
            (t.get("label", "") + " " + t.get("subtitle", "")).strip()
            for t in slide["tiles"]
            if isinstance(t, dict)
        ]
    if slide.get("items"):
        items = slide["items"]
        return [
            " ".join(str(x) for x in it) if isinstance(it, (list, tuple)) else str(it)
            for it in items
        ]
    if slide.get("bullets"):
        return [str(b) for b in slide["bullets"]]
    table = slide.get("table") or {}
    rows = table.get("rows") or []
    if rows:
        return [" ".join(str(c) for c in r) for r in rows]
    return []


def extract_features(slide: dict) -> dict[str, float]:
    """Compute a 0–1 score for each rhetorical feature across the slide."""
    title = (slide.get("title") or "").lower()
    text = _all_text(slide).lower()
    units = _list_units(slide)
    n_units = len(units)

    # Structural gates (boolean → 0/1, used as `requires`)
    has_image = 1.0 if slide.get("image") else 0.0
    table = slide.get("table") or {}
    is_catalog_table = 1.0 if (table and len(table.get("rows", []) or []) >= 4) else 0.0

    # Person cohort: ≥half of table rows or list units have person-name patterns
    person_re = re.compile(r"\b(dr[.-]|nurse[-]|prof[.-]|investigator|advisor|nurse|md\b|phd\b)", re.IGNORECASE)
    person_hits = 0
    person_total = 0
    if (table.get("rows") or []):
        person_total = len(table["rows"])
        person_hits = sum(1 for r in table["rows"] if r and person_re.search(str(r[0])))
    elif units:
        person_total = len(units)
        person_hits = sum(1 for u in units if person_re.search(u))
    is_person_cohort = (person_hits / person_total) if person_total else 0.0
    if person_total and person_hits / person_total >= 0.5:
        is_person_cohort = 1.0

    # Explicit scope: title or content carries a clear in-vs-out / scope phrase
    explicit_scope = 0.0
    for p in ("filing scope", "in scope", "out of scope", "out-of-scope", "carve-out", "carve out", "scope =", "in vs out"):
        if p in text or p in title:
            explicit_scope = 1.0
            break

    # Temporal: fraction of units containing a date/quarter/year/month
    if n_units:
        temporal_hits = sum(1 for u in units if _DATE_RE.search(u))
        temporal = min(1.0, temporal_hits / n_units * 1.2)
    else:
        temporal = 1.0 if _DATE_RE.search(text) else 0.0
        temporal = min(0.4, temporal)  # without units, keep modest

    # Numeric: fraction of units carrying a percent / $ / x-multiplier
    if n_units:
        numeric_hits = sum(1 for u in units if _NUMERIC_RE.search(u))
        numeric = min(1.0, numeric_hits / n_units * 1.2)
    else:
        numeric = 0.6 if _NUMERIC_RE.search(text) else 0.0

    # Ratio comparison: phrases like "down 21%", "38% reduction", "up 2x"
    ratio_hits = len(_RATIO_PHRASE_RE.findall(text)) + len(_PERCENT_RE.findall(text))
    ratio_comparison = min(1.0, ratio_hits / 3.0)

    # Bipolar: explicit two-side framing
    bipolar = 0.0
    for p in _BIPOLAR_PHRASES:
        if p in text or p in title:
            bipolar = max(bipolar, 0.7)
    if n_units == 2:
        bipolar = max(bipolar, 0.5)

    # Enumerative: ordered list (olist) OR bullets that begin with `1. 2. 3.`
    enumerative = 0.0
    if slide.get("type") in ("list-slide", "card-grid"):
        enumerative = 0.4
    if any(re.match(r"^\d+\.\s", u) for u in units):
        enumerative = max(enumerative, 0.6)
    if n_units >= 3:
        enumerative = max(enumerative, 0.3)

    # Homogeneous cohort: title or table-header contains a cohort noun
    homogeneous_cohort = 0.0
    for n in _COHORT_NOUNS:
        if n in title:
            homogeneous_cohort = max(homogeneous_cohort, 0.7)
    if is_catalog_table and homogeneous_cohort < 0.7:
        homogeneous_cohort = 0.5

    # Declarative short: a short single-sentence section (lead/quote/single paragraph)
    declarative_short = 0.0
    quote = slide.get("quote") or ""
    lead = slide.get("lead") or ""
    paras = slide.get("paragraphs") or []
    candidate = quote or (paras[0] if paras else "") or lead
    if candidate:
        wc = len(candidate.split())
        if wc <= 35:
            declarative_short = 0.7
        elif wc <= 60:
            declarative_short = 0.4

    # Definitional: title matches teach-keywords
    definitional = 0.0
    for p in _DEFINITIONAL_PHRASES:
        if p in title:
            definitional = max(definitional, 0.7)

    # Hierarchical: bullets with ≥2 levels (we approximate via colon-prefixed sub-items)
    hierarchical = 0.0
    if any(":" in u and len(u) > 20 for u in units):
        hierarchical = 0.3
    if table and table.get("header") and len(table.get("header", [])) >= 3:
        hierarchical = max(hierarchical, 0.4)

    # Factual density: many units, each with bold lead and supporting text
    factual_density = 0.0
    if n_units >= 4:
        bold_units = sum(1 for u in units if "**" in u or u[:1].isupper())
        factual_density = min(1.0, n_units / 8.0 + bold_units / max(1, n_units) * 0.3)

    return {
        "temporal": temporal,
        "numeric": numeric,
        "ratio_comparison": ratio_comparison,
        "bipolar": bipolar,
        "enumerative": enumerative,
        "homogeneous_cohort": homogeneous_cohort,
        "declarative_short": declarative_short,
        "definitional": definitional,
        "hierarchical": hierarchical,
        "factual_density": factual_density,
        "has_image": has_image,
        "is_catalog_table": is_catalog_table,
        "is_person_cohort": is_person_cohort,
        "explicit_scope": explicit_scope,
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

@dataclass
class ComponentScore:
    name: str
    cluster: str
    score: float
    rationale: str
    viable: bool


def _score_one(features: dict[str, float], meta: dict) -> ComponentScore:
    name = meta["name"]
    cluster = meta.get("cluster", "uncategorized")
    requires = meta.get("requires") or []
    forbids = meta.get("forbids") or []
    favors = meta.get("favors") or {}

    # Veto: required features must score > 0.3
    missing = [r for r in requires if features.get(r, 0.0) < 0.3]
    if missing:
        return ComponentScore(
            name=name, cluster=cluster, score=0.0,
            rationale=f"requires {missing}: not present",
            viable=False,
        )
    forbidden_hits = [f for f in forbids if features.get(f, 0.0) > 0.6]
    if forbidden_hits:
        return ComponentScore(
            name=name, cluster=cluster, score=0.0,
            rationale=f"forbidden by {forbidden_hits}",
            viable=False,
        )

    # Score: weighted sum of favors, clipped 0–1
    total_weight = sum(float(w) for w in favors.values()) or 1.0
    weighted = sum(features.get(k, 0.0) * float(w) for k, w in favors.items())
    score = weighted / total_weight if total_weight else 0.0
    score = max(0.0, min(1.0, score))

    # Bonus: components with NO favors (neutral) get a low baseline so they
    # remain viable but don't dominate well-tuned scorers
    if not favors:
        score = 0.25

    top_features = sorted(
        [(k, features.get(k, 0.0) * float(w)) for k, w in favors.items()],
        key=lambda x: -x[1],
    )[:2]
    rationale = ", ".join(f"{k}={v:.2f}" for k, v in top_features) or "neutral"
    return ComponentScore(
        name=name, cluster=cluster, score=score,
        rationale=rationale, viable=True,
    )


def score_components(
    features: dict[str, float],
    registry: dict[str, dict],
    *,
    top_k: int = 3,
    cluster_spread: bool = True,
) -> list[ComponentScore]:
    """Score every component in the registry; return top-K with cluster spread.

    Cluster-spread rule (open-question 7, locked): at most 2 of the top-K may
    come from the same cluster. The K-th slot, if filled, must come from a
    different cluster than the first two. If no eligible alternate exists,
    fall back to the third-best within-cluster.
    """
    scored = [_score_one(features, meta) for meta in registry.values()]
    scored = [s for s in scored if s.viable]
    scored.sort(key=lambda s: -s.score)

    if not cluster_spread or len(scored) <= top_k:
        return scored[:top_k]

    picks: list[ComponentScore] = []
    cluster_counts: dict[str, int] = {}
    for s in scored:
        if len(picks) >= top_k:
            break
        # Slot 1 + slot 2 fill freely; slot K (the last) must be a fresh cluster
        if len(picks) == top_k - 1:
            if cluster_counts.get(s.cluster, 0) >= 1 and any(
                cluster_counts.get(s2.cluster, 0) == 0 for s2 in scored if s2 not in picks
            ):
                continue
        if cluster_counts.get(s.cluster, 0) >= 2:
            continue
        picks.append(s)
        cluster_counts[s.cluster] = cluster_counts.get(s.cluster, 0) + 1

    if len(picks) < top_k:
        # Top-up with raw-score order, ignoring spread, to ensure we always get K
        for s in scored:
            if s in picks:
                continue
            picks.append(s)
            if len(picks) >= top_k:
                break
    return picks
