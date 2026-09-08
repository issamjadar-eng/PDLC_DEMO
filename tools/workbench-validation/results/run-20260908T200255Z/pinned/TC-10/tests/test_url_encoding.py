"""URL-encoding regression tests for change-control link destinations.

CommonMark + GFM require URL-encoded characters (or angle-bracket-wrapped
URLs) for link destinations containing spaces, parentheses, ampersands,
non-ASCII, etc. A literal space inside a `[...](...)` destination breaks
the parser and the link renders as plain text.

These tests cover the helper pair (`md_link_dest` / `md_link_dest_decode`)
and the round-trip through the adopt → publish path: a media node with a
spaces-in-title resolves to encoded markdown that `_md_to_adf` decodes
back to the original local relpath in the images-collector sidecar.

Offline only — no Confluence calls. Run with:

    python3 .claude/skills/change-control/tests/test_url_encoding.py
"""
from __future__ import annotations

import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.markdown_transform import md_link_dest, md_link_dest_decode  # noqa: E402
from lib.normalizer import NormalizationReport, adf_to_markdown  # noqa: E402
from actions.publish_helper import _md_to_adf  # noqa: E402


# ---- Phase A — helper unit tests ----


def test_md_link_dest_encodes_spaces():
    name = "FORM-000105316 - DTM - Design Traceability Matrix.xlsx"
    enc = md_link_dest(name)
    assert enc == (
        "FORM-000105316%20-%20DTM%20-%20Design%20Traceability%20Matrix.xlsx"
    ), enc


def test_md_link_dest_encodes_parens():
    enc = md_link_dest("file (with parens).pdf")
    assert enc == "file%20%28with%20parens%29.pdf", enc


def test_md_link_dest_encodes_ampersand():
    enc = md_link_dest("file&with&ampersand.pdf")
    assert enc == "file%26with%26ampersand.pdf", enc


def test_md_link_dest_no_op_on_safe_chars():
    name = "name-with-no-issues.pdf"
    assert md_link_dest(name) == name


def test_md_link_dest_preserves_path_separator():
    enc = md_link_dest("images/file with space.pdf")
    assert enc == "images/file%20with%20space.pdf", enc


def test_md_link_dest_handles_non_ascii():
    # Confluence allows non-ASCII filenames (e.g., Cyrillic, Latin-1 accents).
    # urllib.parse.quote percent-encodes the UTF-8 bytes by default.
    enc = md_link_dest("résumé.pdf")
    # 'é' is U+00E9, UTF-8 c3 a9 → %C3%A9
    assert enc == "r%C3%A9sum%C3%A9.pdf", enc
    assert md_link_dest_decode(enc) == "résumé.pdf"


def test_md_link_dest_roundtrip():
    samples = [
        "FORM-000105316 - DTM - Design Traceability Matrix.xlsx",
        "file (with parens).pdf",
        "file&with&ampersand.pdf",
        "name-with-no-issues.pdf",
        "images/file with space.pdf",
        "résumé.pdf",
    ]
    for s in samples:
        assert md_link_dest_decode(md_link_dest(s)) == s, s


def test_md_link_dest_handles_empty():
    assert md_link_dest("") == ""
    assert md_link_dest_decode("") == ""


# ---- Phase B — adopt → md → adopt round-trip with spaces ----


def _local_resolver(filename: str, media_id):
    return f"images/{filename}" if filename else f"images/{media_id or 'media'}.bin"


def test_normalizer_emits_encoded_url_slot_for_image_with_spaces():
    """An ADF media node whose fileName has spaces must render to
    markdown with the URL slot percent-encoded — otherwise CommonMark
    parses up to the first space as the URL and breaks the link."""
    adf = {
        "type": "doc",
        "content": [
            {"type": "mediaSingle", "content": [
                {"type": "media", "attrs": {
                    "type": "file",
                    "id": "abc",
                    "fileName": "Hero Diagram (final).png",
                    "alt": "Hero Diagram",
                }},
            ]},
        ],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf, attachment_url=_local_resolver, report=report)
    # URL slot: encoded
    assert "(images/Hero%20Diagram%20%28final%29.png)" in md, md
    # Link text (alt): human-readable, raw
    assert "![Hero Diagram]" in md, md


def test_normalizer_emits_encoded_url_slot_for_filecard_with_spaces():
    """File-card render path: same encoding requirement applies to the
    `[label](url)` link syntax."""
    adf = {
        "type": "doc",
        "content": [
            {"type": "paragraph", "content": [
                {"type": "mediaInline", "attrs": {
                    "type": "file",
                    "id": "xyz",
                    "fileName": "FORM-000105316 - DTM - Design Traceability Matrix.xlsx",
                }},
            ]},
        ],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf, attachment_url=_local_resolver, report=report)
    # URL slot: encoded
    assert (
        "(images/FORM-000105316%20-%20DTM%20-%20Design%20Traceability%20Matrix.xlsx)"
        in md
    ), md
    # Link text (filename): human-readable, raw
    assert "[FORM-000105316 - DTM - Design Traceability Matrix.xlsx]" in md, md


def test_full_roundtrip_with_spaces_decodes_to_original_relpath():
    """ADF (media node, fileName with spaces) → md → ADF must surface
    the un-encoded local relpath in the images-collector sidecar so the
    upload step can find the binary on disk."""
    adf_in = {
        "type": "doc",
        "content": [
            {"type": "mediaSingle", "content": [
                {"type": "media", "attrs": {
                    "type": "file",
                    "id": "abc",
                    "fileName": "Hero Diagram (final).png",
                    "alt": "Hero Diagram",
                }},
            ]},
        ],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf_in, attachment_url=_local_resolver, report=report)
    # Sanity: URL slot is encoded in markdown.
    assert "%20" in md
    # Now feed the markdown to publish-side _md_to_adf.
    sidecar: list = []
    adf_out = _md_to_adf(md, images_collector=sidecar)
    assert any(n.get("type") == "mediaSingle" for n in adf_out["content"])
    # Sidecar must contain the DECODED relpath so the file lookup at
    # upload time succeeds against the on-disk file (which uses literal
    # spaces, not %20).
    assert len(sidecar) == 1, sidecar
    assert sidecar[0]["source_relpath"] == "images/Hero Diagram (final).png", (
        f"expected decoded relpath, got {sidecar[0]['source_relpath']!r}"
    )
    # Placeholder id matches the decoded form so patch-adf swaps work.
    assert sidecar[0]["placeholder"] == (
        "PLACEHOLDER:images/Hero Diagram (final).png"
    )


def test_no_double_encoding_on_safe_filename():
    """A filename with no special chars must round-trip as a no-op
    (no double-encoding artifacts)."""
    adf = {
        "type": "doc",
        "content": [
            {"type": "mediaSingle", "content": [
                {"type": "media", "attrs": {
                    "type": "file",
                    "id": "abc",
                    "fileName": "diagram.svg",
                }},
            ]},
        ],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf, attachment_url=_local_resolver, report=report)
    assert "(images/diagram.svg)" in md, md
    # No `%` artifacts whatsoever
    assert "%" not in md, md


# ---- Test runner ----


TESTS = [
    test_md_link_dest_encodes_spaces,
    test_md_link_dest_encodes_parens,
    test_md_link_dest_encodes_ampersand,
    test_md_link_dest_no_op_on_safe_chars,
    test_md_link_dest_preserves_path_separator,
    test_md_link_dest_handles_non_ascii,
    test_md_link_dest_roundtrip,
    test_md_link_dest_handles_empty,
    test_normalizer_emits_encoded_url_slot_for_image_with_spaces,
    test_normalizer_emits_encoded_url_slot_for_filecard_with_spaces,
    test_full_roundtrip_with_spaces_decodes_to_original_relpath,
    test_no_double_encoding_on_safe_filename,
]


def main() -> int:
    passed = 0
    failed = 0
    for t in TESTS:
        try:
            t()
            print(f"PASS  {t.__name__}")
            passed += 1
        except AssertionError as exc:
            print(f"FAIL  {t.__name__}: {exc}")
            failed += 1
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR {t.__name__}: {type(exc).__name__}: {exc}")
            failed += 1
    print(f"\n{passed}/{passed + failed} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
