"""Finance / business vocabulary pack (stub).

Activates finance keyword routing in md-deck's icon classification. Load via:

    from icons import configure_vocabularies
    configure_vocabularies(["finance"])

Status: scaffolding only. Add real entries as md-deck is exercised on
business / finance / investor / board content. Each table mirrors trunk
`icons.py` shape; icon names referenced here must exist in trunk `ICONS`.

Intended coverage (to be filled in):
    - Financial concepts (NPV, ROI, EBITDA, gross margin, cash flow)
    - Investor / funding (ARR, MRR, runway, seed, Series A/B/C, exit)
    - Accounting (ledger, balance sheet, P&L, audit, GAAP, IFRS)
    - Banking (FDIC, SWIFT, basel, fintech, transaction)
    - Markets (equity, bond, derivative, hedge, portfolio)
    - Risk / compliance (SOX, KYC, AML, basel III)
    - Cohorts (LP, GP, fund, portfolio company, board, investor)
"""

KEYWORD_REGISTRY: list[tuple[list[str], str]] = []
INTENT_PHRASES: list[tuple[list[str], str]] = []
GROUP_ICONS: dict[str, str] = {}
GROUP_TITLE_HINTS: list[tuple[list[str], str]] = []
