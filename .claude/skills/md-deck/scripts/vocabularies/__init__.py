"""Vocabulary packs for md-deck icon classification.

Trunk `icons.py` ships with domain-neutral keyword/phrase tables. Domain-specific
vocabulary (medtech, finance, manufacturing, …) lives in this package as opt-in
packs that the consumer activates explicitly at startup:

    from icons import configure_vocabularies
    configure_vocabularies(["medtech"])           # single domain
    configure_vocabularies(["medtech", "finance"]) # multi-domain practice

Each pack is a Python module exposing four optional names:

    KEYWORD_REGISTRY   : list[tuple[list[str], str]]
    INTENT_PHRASES     : list[tuple[list[str], str]]
    GROUP_ICONS        : dict[str, str]
    GROUP_TITLE_HINTS  : list[tuple[list[str], str]]

The structures mirror trunk `icons.py`. When a pack is loaded, its entries are
**prepended** to the trunk's scan order, so domain-specific vocabulary matches
before generic catches (e.g., a `"fda"` keyword from the medtech pack matches
before a generic `"regulator"` entry could shadow it).

This package contains no business logic — it is purely data. The loader and
scan functions live in `icons.py`.
"""
