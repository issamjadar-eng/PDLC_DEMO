"""Regression tests for task 128 — Confluence Attachments-macro expander.

Covers:

  Phase A — normalizer captures macro params
    1. Attachments extension with `labels=actual` populates
       `report.attachment_macros[0]` with labels="actual" and emits an
       OPEN+CLOSE sentinel pair carrying `position=0`.
    2. Two attachments macros on the same page (labels=actual,
       labels=outdated) get distinct position markers (0 and 1).

  Phase B — action-layer expander renders filtered attachment list
    3. `_filter_attachments_by_macro(labels="actual", ...)` selects only
       attachments whose `metadata.labels.results[]` contains the label.
    4. `_expand_attachment_macros(...)` splices a rendered table between
       the OPEN and CLOSE sentinels, matched by position marker, and
       returns synthetic `report.images`-shaped entries to feed the
       existing image-download infrastructure.

  Phase C — publish-side strip
    5. `_md_to_adf(...)` emits a single `extension` node with
       `extensionKey="attachments"` and reconstructed macroParams when
       it sees the OPEN sentinel; the rendered table is dropped.

  Phase D — round-trip
    6. ADF → md → ADF preserves the macro `labels` parameter verbatim
       across two passes.

Offline only — no Confluence calls. The cookie / list_attachments path
is replaced by a fake `lib.attachments` module installed through pytest's
`monkeypatch` (restored after each test — `mocked` tier, see conftest.py).
Run:

    python3 .claude/skills/change-control/tests/test_attachments_macro.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.normalizer import (  # noqa: E402
    NormalizationReport,
    adf_to_markdown,
)


# ---- Phase A — normalizer ----


def _attachments_ext(labels: str) -> dict:
    return {
        "type": "extension",
        "attrs": {
            "layout": "wide",
            "extensionType": "com.atlassian.confluence.macro.core",
            "extensionKey": "attachments",
            "parameters": {
                "macroParams": {
                    "_parentId": {"value": "5619318892"},
                    "upload": {"value": "false"},
                    "labels": {"value": labels},
                },
                "macroMetadata": {"title": "Attachments"},
            },
        },
    }


def test_normalizer_captures_attachments_macro_params():
    adf = {"type": "doc", "content": [_attachments_ext("actual")]}
    report = NormalizationReport()
    md = adf_to_markdown(adf, report=report)
    assert len(report.attachment_macros) == 1, report.attachment_macros
    macro = report.attachment_macros[0]
    assert macro["labels"] == "actual"
    assert macro["parent_page_id"] == "5619318892"
    assert macro["position"] == 0
    # OPEN/CLOSE sentinel pair present, both with position=0
    assert "confluence-side: attachments labels=actual position=0" in md
    assert "/confluence-side: attachments position=0" in md


def test_normalizer_two_macros_get_distinct_positions():
    adf = {
        "type": "doc",
        "content": [
            _attachments_ext("actual"),
            {"type": "paragraph", "content": [{"type": "text", "text": "Outdated"}]},
            _attachments_ext("outdated"),
        ],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf, report=report)
    assert len(report.attachment_macros) == 2
    assert report.attachment_macros[0]["labels"] == "actual"
    assert report.attachment_macros[0]["position"] == 0
    assert report.attachment_macros[1]["labels"] == "outdated"
    assert report.attachment_macros[1]["position"] == 1
    assert "labels=actual position=0" in md
    assert "labels=outdated position=1" in md
    # Both close sentinels with their respective markers
    assert "/confluence-side: attachments position=0" in md
    assert "/confluence-side: attachments position=1" in md


# ---- Phase B — action-layer expander ----


# Import after sys.path setup
from actions.adopt_helper import (  # noqa: E402
    _expand_attachment_macros,
    _filter_attachments_by_macro,
    _render_attachment_table,
)
from actions import adopt_helper as _ah_mod  # noqa: E402


def _att_record(title: str, labels: list[str], size: int = 12345) -> dict:
    return {
        "id": f"att-{title}",
        "title": title,
        "metadata": {
            "mediaType": "application/octet-stream",
            "labels": {"results": [{"name": n, "prefix": "global"} for n in labels]},
        },
        "version": {"when": "2026-01-15T12:00:00Z"},
        "extensions": {"fileSize": size, "fileId": f"uuid-{title}"},
    }


def test_filter_attachments_by_label_or_semantics():
    atts = [
        _att_record("A.docx", ["actual"]),
        _att_record("B.docx", ["outdated"]),
        _att_record("C.docx", ["actual", "draft"]),
        _att_record("D.docx", []),
    ]
    selected = _filter_attachments_by_macro(
        atts, labels="actual", name_filter=None
    )
    titles = [a["title"] for a in selected]
    assert titles == ["A.docx", "C.docx"], titles

    # Comma-separated → OR
    selected2 = _filter_attachments_by_macro(
        atts, labels="actual,outdated", name_filter=None
    )
    titles2 = [a["title"] for a in selected2]
    assert titles2 == ["A.docx", "B.docx", "C.docx"], titles2

    # No filter → everything
    selected3 = _filter_attachments_by_macro(
        atts, labels=None, name_filter=None
    )
    assert len(selected3) == 4


@pytest.mark.mocked
def test_expand_attachment_macros_splices_rendered_table(monkeypatch):
    """Source markdown has an OPEN/CLOSE sentinel pair; expander
    splices a rendered file-list table between them and returns
    synthetic image refs for download."""
    atts = [
        _att_record("Module One PHA.docx", ["actual"]),
        _att_record("FORM-285130 PHASE1.docx", ["actual"]),
        _att_record("OLD VERSION.docx", ["outdated"]),
    ]

    # Replace the cookie + listing functions referenced inside
    # _expand_attachment_macros via lazy import by installing a fake
    # module at the `sys.modules` seam the function resolves through.
    # monkeypatch.setitem restores the real module after the test —
    # a bare assignment here leaked into later test files and made an
    # unrelated Jira-renderer test reach the network.
    import types
    fake_lib = types.ModuleType("lib.attachments")
    fake_lib.extract_confluence_cookies = lambda url: "fake=cookie"
    fake_lib.list_attachments = lambda url, pid, c, expand_labels=False: list(atts)
    monkeypatch.setitem(sys.modules, "lib.attachments", fake_lib)

    src_md = (
        "# Heading\n\n"
        "<!-- confluence-side: attachments labels=actual position=0 -->\n"
        "<!-- /confluence-side: attachments position=0 -->\n\n"
        "Some intervening text\n\n"
        "<!-- confluence-side: attachments labels=outdated position=1 -->\n"
        "<!-- /confluence-side: attachments position=1 -->\n"
    )
    report = NormalizationReport()
    report.attachment_macros = [
        {
            "position": 0,
            "labels": "actual",
            "name_filter": None,
            "page_size": None,
            "parent_page_id": "5619318892",
            "raw_params": {},
        },
        {
            "position": 1,
            "labels": "outdated",
            "name_filter": None,
            "page_size": None,
            "parent_page_id": "5619318892",
            "raw_params": {},
        },
    ]
    new_md, synthetic, warnings = _expand_attachment_macros(
        src_md, "https://example.atlassian.net", "5619318892", report
    )
    assert warnings == [], warnings
    # Each rendered table appears between its open/close sentinels
    assert "Module One PHA.docx" in new_md
    assert "FORM-285130 PHASE1.docx" in new_md
    assert "OLD VERSION.docx" in new_md
    # Filename links to the local images path. URL slot is percent-encoded
    # so spaces / parens / etc. don't break CommonMark parsing (task 129).
    # Bracketed text (link label) stays human-readable.
    assert "[Module One PHA.docx](images/Module%20One%20PHA.docx)" in new_md
    assert "[OLD VERSION.docx](images/OLD%20VERSION.docx)" in new_md
    # Synthetic image refs were generated for each unique title
    syn_titles = sorted(s["filename"] for s in synthetic)
    assert syn_titles == [
        "FORM-285130 PHASE1.docx",
        "Module One PHA.docx",
        "OLD VERSION.docx",
    ]
    # Sentinels still wrap the rendered tables (round-trip preserved)
    assert "labels=actual position=0" in new_md
    assert "/confluence-side: attachments position=0" in new_md


# ---- Phase C — publish-side strip ----


def test_publish_md_to_adf_emits_attachments_extension_node():
    """The publish-side `_md_to_adf` recognizes the OPEN sentinel,
    skips to CLOSE, and emits a single `extension` ADF node — the
    rendered table content is dropped."""
    from actions.publish_helper import _md_to_adf

    md = (
        "# Heading\n\n"
        "<!-- confluence-side: attachments labels=actual position=0 -->\n\n"
        "| Filename | Size | Modified | Labels |\n"
        "| --- | --- | --- | --- |\n"
        "| [Module One PHA.docx](images/Module One PHA.docx) | 12.1 KB | 2026-01-15 | actual |\n\n"
        "<!-- /confluence-side: attachments position=0 -->\n\n"
        "Some text after.\n"
    )
    doc = _md_to_adf(md)
    # Find the extension node
    types_seen = [c.get("type") for c in doc["content"]]
    assert "extension" in types_seen, types_seen
    ext = next(c for c in doc["content"] if c.get("type") == "extension")
    assert ext["attrs"]["extensionKey"] == "attachments"
    macro_params = ext["attrs"]["parameters"]["macroParams"]
    assert macro_params["labels"]["value"] == "actual", macro_params
    # The rendered table was dropped — no `tableRow` nodes between the
    # extension and the trailing paragraph
    table_nodes = [c for c in doc["content"] if c.get("type") == "table"]
    assert table_nodes == [], (
        "publish path leaked the rendered file-list table; should be dropped"
    )
    # Trailing text survives
    last = doc["content"][-1]
    assert last["type"] == "paragraph"


# ---- Phase D — round-trip ----


def test_roundtrip_adf_md_adf_preserves_macro_labels():
    """ADF with attachments extension → md → ADF must preserve the
    `labels` macroParam verbatim (the position marker is a per-pull
    artifact and may differ — that's fine; what matters is that the
    user-meaningful filter is preserved)."""
    from actions.publish_helper import _md_to_adf

    src_adf = {
        "type": "doc",
        "content": [_attachments_ext("actual"), _attachments_ext("outdated")],
    }
    report = NormalizationReport()
    md = adf_to_markdown(src_adf, report=report)
    out_doc = _md_to_adf(md)

    # Find the two extension nodes in output and verify their labels
    exts = [
        c for c in out_doc["content"]
        if c.get("type") == "extension"
        and c.get("attrs", {}).get("extensionKey") == "attachments"
    ]
    assert len(exts) == 2, json.dumps(exts, indent=2)
    out_labels = [
        e["attrs"]["parameters"]["macroParams"]["labels"]["value"]
        for e in exts
    ]
    assert out_labels == ["actual", "outdated"], out_labels


# ---- Test runner ----


def main() -> int:
    """Direct invocation delegates to pytest so fixture-taking tests run."""
    return pytest.main([__file__, "-q"])


if __name__ == "__main__":
    sys.exit(main())
