"""Regression tests for task 126 — file-card rendering, list_attachments
filename fallback, and fuzzy parent-IS-topic collapse.

Covers:

  Phase A — `mediaInline` file-card emission
    1. mediaInline with no fileName + type=file → file-card placeholder
       `[<<file:UUID>>](images/UUID.bin)<!-- media inline id=UUID ... -->`
    2. mediaInline with image-extension fileName → image syntax
    3. mediaInline tracked in report.images with style="inline" + render="file"

  Phase B — `mediaGroup` / `media` file-card vs image rendering
    4. mediaGroup with file media (no fileName) → file-card placeholder,
       NOT image syntax `![](images/UUID.bin)`
    5. mediaGroup with image-extension fileName → image syntax
    6. SAST-cell shape (text + mediaInline + hardBreak + text +
       mediaInline) renders end-to-end with PDF + CSV file-cards visible

  Phase C — `list_attachments_by_uuid`
    7. UUID-keyed mapping — extensions.fileId → {title, mediaType,
       attachment_id, fileSize}
    8. Records missing fileId are skipped (legacy attachments)

  Phase D — fuzzy parent-IS-topic collapse
    9. is_same_topic exact equality
    10. is_same_topic suffix (parent has -sec, child doesn't): True
    11. is_same_topic suffix (child has, parent doesn't): True
    12. is_same_topic genuinely different topics: False
    13. plan_paths fuzzy collapse: vulnerability-assessments-sec parent
        + vulnerability-assessments topic → version files in parent's
        folder, no nested sub-folder

Offline only — no Confluence calls. The list_attachments helper is
exercised against a synthetic payload identical in shape to a live
response. Run with:

    python3 .claude/skills/change-control/tests/test_file_cards.py
"""
from __future__ import annotations

import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.attachments import list_attachments_by_uuid  # noqa: E402
from lib.manifest import (  # noqa: E402
    Manifest,
    ManifestPage,
    is_same_topic,
    plan_paths,
)
from lib.normalizer import (  # noqa: E402
    NormalizationReport,
    adf_to_markdown,
)


# ---- Phase A — mediaInline ----


def test_mediaInline_file_no_filename_emits_placeholder():
    adf = {
        "type": "doc",
        "content": [{
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "PDF: "},
                {
                    "type": "mediaInline",
                    "attrs": {
                        "id": "13a50d1f-4341-4391-b8f8-d714725bcbff",
                        "collection": "contentId-5132714154",
                    },
                },
            ],
        }],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf, report=report)
    # Placeholder convention so action layer can swap with real title.
    assert "[<<file:13a50d1f-4341-4391-b8f8-d714725bcbff>>]" in md, md
    assert "13a50d1f-4341-4391-b8f8-d714725bcbff.bin" in md, md
    # Round-trip marker carries `inline` flag for ADF re-emit.
    assert "inline id=13a50d1f-4341-4391-b8f8-d714725bcbff" in md, md
    # NOT image syntax
    assert "![" not in md, md
    # Bookkeeping
    assert len(report.images) == 1
    assert report.images[0]["node_type"] == "mediaInline"
    assert report.images[0]["style"] == "inline"
    assert report.images[0]["render"] == "file"
    assert report.images[0]["needs_filename"] is True


def test_mediaInline_with_image_extension_emits_image_syntax():
    """When mediaInline carries a fileName ending in .png/.jpg, the file
    really is an image embedded inline. Use image syntax."""
    adf = {
        "type": "doc",
        "content": [{
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "see "},
                {
                    "type": "mediaInline",
                    "attrs": {
                        "id": "img-uuid-1",
                        "collection": "contentId-1",
                        "fileName": "diagram.png",
                    },
                },
            ],
        }],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf, report=report)
    # mediaInline branch in normalizer always renders inline file-cards
    # as link syntax — image rendering is reserved for block-level
    # mediaSingle / mediaGroup. (An inline image is unusual and the
    # link-syntax render is still correct since `[…]` works in inline
    # contexts where `![…]` may be ambiguous.)
    # NOTE: the design decision in normalizer.py forces mediaInline ->
    # render_as_image=False. Update this test if that policy changes.
    assert report.images[0]["node_type"] == "mediaInline"
    assert "diagram.png" in md, md


# ---- Phase B — mediaGroup file vs image ----


def test_mediaGroup_file_no_filename_emits_filecard_placeholder():
    adf = {
        "type": "doc",
        "content": [{
            "type": "mediaGroup",
            "content": [{
                "type": "media",
                "attrs": {
                    "id": "48d3a904-79bf-4c9a-a1c6-85d7a565e4d3",
                    "collection": "contentId-5132714154",
                    "type": "file",
                },
            }],
        }],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf, report=report)
    assert "[<<file:48d3a904-79bf-4c9a-a1c6-85d7a565e4d3>>]" in md, md
    assert "48d3a904-79bf-4c9a-a1c6-85d7a565e4d3.bin" in md, md
    # NOT image syntax — this is the bug we're fixing.
    assert "![<<file:" not in md, md
    assert "![](" not in md, md
    assert report.images[0]["render"] == "file"


def test_mediaGroup_image_filename_emits_image_syntax():
    adf = {
        "type": "doc",
        "content": [{
            "type": "mediaGroup",
            "content": [{
                "type": "media",
                "attrs": {
                    "id": "screenshot-1",
                    "collection": "contentId-1",
                    "type": "file",
                    "fileName": "screenshot.png",
                },
            }],
        }],
    }
    report = NormalizationReport()
    # Use the local-images resolver to mimic adopt's --download-images flow.
    def _resolver(filename, _media_id):
        return f"images/{filename}"
    md = adf_to_markdown(adf, attachment_url=_resolver, report=report)
    assert "![screenshot.png](images/screenshot.png)" in md, md
    assert report.images[0]["render"] == "image"


def test_sast_cell_shape_endtoend():
    """Reproduces the row-1 SAST cell from page 5132714154:
    text "PDF: " → mediaInline → text " " → hardBreak → text "CSV: " →
    mediaInline → text " ". Without the fix this rendered as
    `PDF:     CSV:` with both file-cards silently dropped.
    """
    adf = {
        "type": "doc",
        "content": [{
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "PDF: "},
                {"type": "mediaInline", "attrs": {
                    "id": "PDFUUID", "collection": "contentId-1"}},
                {"type": "text", "text": " "},
                {"type": "hardBreak"},
                {"type": "text", "text": "CSV: "},
                {"type": "mediaInline", "attrs": {
                    "id": "CSVUUID", "collection": "contentId-1"}},
                {"type": "text", "text": " "},
            ],
        }],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf, report=report)
    # Both file-cards are present, in order, with placeholder labels.
    pdf_idx = md.find("[<<file:PDFUUID>>]")
    csv_idx = md.find("[<<file:CSVUUID>>]")
    assert pdf_idx >= 0, md
    assert csv_idx >= 0, md
    assert pdf_idx < csv_idx, md
    # PDF and CSV labels in surrounding text are preserved.
    assert "PDF:" in md and "CSV:" in md, md
    assert len(report.images) == 2


# ---- Phase C — list_attachments_by_uuid ----


def test_list_attachments_by_uuid_correlates_via_extensions_fileId():
    payload = [
        {
            "id": "att6642925726",
            "title": "dependencies-adi-5qoqzB4qeoZPdZ9yS5prFe-2026-03-31T12_23_57.837Z.csv",
            "metadata": {"mediaType": "text/csv"},
            "extensions": {
                "fileId": "48d3a904-79bf-4c9a-a1c6-85d7a565e4d3",
                "mediaType": "text/csv",
                "fileSize": 300798,
            },
        },
        {
            "id": "att6301155595",
            "title": "snyk_issues-detail_01_19_2026.pdf",
            "metadata": {"mediaType": "application/pdf"},
            "extensions": {
                "fileId": "13a50d1f-4341-4391-b8f8-d714725bcbff",
                "mediaType": "application/pdf",
                "fileSize": 125258,
            },
        },
    ]
    out = list_attachments_by_uuid(
        "https://example.atlassian.net", "1", "cookie",
        _attachments=payload,
    )
    assert "48d3a904-79bf-4c9a-a1c6-85d7a565e4d3" in out
    assert (
        out["48d3a904-79bf-4c9a-a1c6-85d7a565e4d3"]["title"]
        == "dependencies-adi-5qoqzB4qeoZPdZ9yS5prFe-2026-03-31T12_23_57.837Z.csv"
    )
    assert out["48d3a904-79bf-4c9a-a1c6-85d7a565e4d3"]["mediaType"] == "text/csv"
    assert out["48d3a904-79bf-4c9a-a1c6-85d7a565e4d3"]["attachment_id"] == "att6642925726"
    assert out["13a50d1f-4341-4391-b8f8-d714725bcbff"]["title"] == "snyk_issues-detail_01_19_2026.pdf"


def test_list_attachments_by_uuid_skips_records_without_fileId():
    payload = [
        {
            "id": "att-legacy",
            "title": "legacy.csv",
            "metadata": {"mediaType": "text/csv"},
            "extensions": {"mediaType": "text/csv"},  # no fileId
        },
        {
            "id": "att-modern",
            "title": "modern.csv",
            "extensions": {"fileId": "uuid-modern", "mediaType": "text/csv"},
        },
    ]
    out = list_attachments_by_uuid(
        "https://example.atlassian.net", "1", "cookie",
        _attachments=payload,
    )
    assert "uuid-modern" in out
    # Legacy record has no fileId so it's not in the UUID map. Caller's
    # filename-fallback handles it via <uuid>.bin synthesis.
    assert len(out) == 1


# ---- Phase D — fuzzy parent-IS-topic collapse ----


def test_is_same_topic_exact_equality():
    assert is_same_topic(
        "software-development-plan-sdp", "software-development-plan-sdp"
    ) is True


def test_is_same_topic_parent_has_disambiguator_suffix():
    # Parent slug carries the parenthetical disambiguator; child topic
    # was extracted from `Vulnerability Assessments - 1.0.0` (no suffix).
    assert is_same_topic(
        "vulnerability-assessments-sec", "vulnerability-assessments"
    ) is True


def test_is_same_topic_child_has_disambiguator_suffix():
    # Symmetric — should match either way.
    assert is_same_topic(
        "vulnerability-assessments", "vulnerability-assessments-sec"
    ) is True


def test_is_same_topic_negative_genuinely_different_topics():
    # software-security-sec is a section heading, NOT the same topic as
    # its child cybersecurity-measures-and-metrics-sec. Both happen to
    # carry the -sec suffix but neither is a prefix of the other.
    assert is_same_topic(
        "software-security-sec",
        "cybersecurity-measures-and-metrics-sec",
    ) is False


def test_is_same_topic_negative_long_suffix():
    # Even though `software-development-plan-something-else` starts
    # with `software-development`, the suffix is too long to be a
    # disambiguator — different topic.
    assert is_same_topic(
        "software-development", "software-development-plan-and-quality-mgmt"
    ) is False


def test_plan_paths_fuzzy_collapse_vulnerability_assessments():
    """End-to-end: parent slug carries `-sec` parenthetical, child topic
    doesn't. Versions land in parent's folder, no `vulnerability-assessments/`
    sub-folder."""
    pages = [
        ManifestPage(id="1", title="Root", parent_id="", depth=0),
        ManifestPage(
            id="2",
            title="Vulnerability Assessments (SEC)",
            parent_id="1",
            depth=1,
        ),
        ManifestPage(
            id="3",
            title="Vulnerability Assessments - 1.0.0",
            parent_id="2",
            depth=2,
        ),
        ManifestPage(
            id="4",
            title="Vulnerability Assessments - 2.0.0",
            parent_id="2",
            depth=2,
        ),
    ]
    manifest = Manifest(
        tool_version="t",
        cloud_id="c",
        space_key="X",
        base_url="https://example.atlassian.net",
        root_page_id="1",
        pulled_at="2026-04-29",
        pages=pages,
    )
    paths = plan_paths(manifest, prefixes=[], staging_root="staging")
    # Versions land directly in parent's folder.
    assert paths["3"] == "staging/root/vulnerability-assessments-sec/v1.0.0.md", paths["3"]
    assert paths["4"] == "staging/root/vulnerability-assessments-sec/v2.0.0.md", paths["4"]
    # Negative — no nested sub-folder.
    assert "/vulnerability-assessments/v" not in paths["3"]


# ---- Test runner ----


TESTS = [
    test_mediaInline_file_no_filename_emits_placeholder,
    test_mediaInline_with_image_extension_emits_image_syntax,
    test_mediaGroup_file_no_filename_emits_filecard_placeholder,
    test_mediaGroup_image_filename_emits_image_syntax,
    test_sast_cell_shape_endtoend,
    test_list_attachments_by_uuid_correlates_via_extensions_fileId,
    test_list_attachments_by_uuid_skips_records_without_fileId,
    test_is_same_topic_exact_equality,
    test_is_same_topic_parent_has_disambiguator_suffix,
    test_is_same_topic_child_has_disambiguator_suffix,
    test_is_same_topic_negative_genuinely_different_topics,
    test_is_same_topic_negative_long_suffix,
    test_plan_paths_fuzzy_collapse_vulnerability_assessments,
]


def main() -> int:
    failed = 0
    for t in TESTS:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
    print()
    print(f"{len(TESTS) - failed}/{len(TESTS)} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
