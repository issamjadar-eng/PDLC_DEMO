"""Tests for task 134 — cross-page UNKNOWN_MEDIA_ID resolution +
orphan-file (no-marker) round-trip.

Phase A — inbound (cross-page resolution)
  1. Normalizer detects `UNKNOWN_MEDIA_ID` and tracks position
  2. `parse_storage_xhtml` extracts `<ri:attachment>` with filename + content-title
  3. `pair_unknowns_to_storage` correctly pairs by structural position
  4. Cross-page resolver: title-search + list_attachments + download → markdown gets real filename (mocked HTTP)
  5. Cross-page graceful degradation: title-search returns nothing → emits warning placeholder, NOT UNKNOWN_MEDIA_ID

Phase B — outbound (orphan-file no-marker round-trip)
  6. `_md_to_adf` recognizes plain `[X](images/Y.pdf)` (no marker) → emits PLACEHOLDER mediaSingle file-card
  7. `_md_to_adf` recognizes plain `![X](images/Y.png)` → emits PLACEHOLDER mediaSingle image
  8. `_md_to_adf` honors round-trip marker when present (no double-handling)
  9. `upload-images` reference scanner catches plain `[X](images/Y.pdf)` links
 10. Round-trip mock: ADF UNKNOWN_MEDIA_ID → adopt resolves → markdown has filename + marker → publish uploads → re-adopt has standard marker (mocked end-to-end)

Offline only — no Confluence calls. The cookie bridge / list_attachments
helpers are not invoked; the cross-page resolver branches that need
them are exercised through the cross_page_resolve.py pure functions
(mocking is unnecessary for the parsing + pairing + markdown-emit
tests). The mocked end-to-end test stitches together the pure-function
boundaries.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.cross_page_resolve import (  # noqa: E402
    build_resolved_markdown,
    build_warning_markdown,
    pair_unknowns_to_storage,
    parse_storage_xhtml,
)
from lib.mime import decide_card_kind, is_image_extension  # noqa: E402
from lib.normalizer import (  # noqa: E402
    NormalizationReport,
    adf_to_markdown,
)


_PASSED = 0
_FAILED = 0


def _ok(name: str) -> None:
    global _PASSED
    _PASSED += 1
    print(f"PASS  {name}")


def _fail(name: str, exc: BaseException) -> None:
    global _FAILED
    _FAILED += 1
    print(f"FAIL  {name}: {exc}")


def _run(name: str, fn) -> None:
    try:
        fn()
    except AssertionError as exc:  # noqa: BLE001
        _fail(name, exc)
    except Exception as exc:  # noqa: BLE001
        _fail(name, exc)
    else:
        _ok(name)


# ============================================================================
# Phase A — inbound
# ============================================================================


def test_normalizer_detects_unknown_media_id_and_tracks_position():
    """ADF media node with id == 'UNKNOWN_MEDIA_ID' is detected,
    cross_page_unknowns is populated with structural position, and the
    markdown carries a CROSSPAGE placeholder (NOT a literal
    UNKNOWN_MEDIA_ID string)."""
    adf = {
        "type": "doc",
        "content": [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "DHF Phase 1 document"}]},
            {"type": "mediaGroup", "content": [
                {"type": "media", "attrs": {
                    "id": "UNKNOWN_MEDIA_ID",
                    "collection": "",
                    "type": "file",
                    "__fileName": "UNKNOWN_ATTACHMENT",
                }}
            ]},
        ],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf, report=report)
    assert len(report.cross_page_unknowns) == 1, (
        f"expected 1 cross_page_unknowns, got {len(report.cross_page_unknowns)}"
    )
    unk = report.cross_page_unknowns[0]
    assert unk["placeholder_id"] == "CROSSPAGE-0", unk
    assert unk["position"] == 0, unk
    assert "UNKNOWN_MEDIA_ID" not in md, md
    assert "<<crosspage:0>>" in md, md
    assert "<!-- crosspage position=0 -->" in md, md


def test_parse_storage_xhtml_extracts_ri_attachment():
    """Storage XHTML walker extracts <ri:attachment> attrs in order."""
    xhtml = """
    <p>Header</p>
    <ac:structured-macro ac:name="view-file">
      <ri:attachment ri:filename="design.docx" ri:content-title="Source Page A" />
    </ac:structured-macro>
    <ri:attachment ri:filename="data.csv" ri:content-title="Source Page B" ri:version-at-save="3" />
    """
    out = parse_storage_xhtml(xhtml)
    assert len(out) == 2, out
    assert out[0]["filename"] == "design.docx", out[0]
    assert out[0]["content_title"] == "Source Page A", out[0]
    assert out[0]["position"] == 0, out[0]
    assert out[1]["filename"] == "data.csv", out[1]
    assert out[1]["content_title"] == "Source Page B", out[1]
    assert out[1]["version_at_save"] == "3", out[1]


def test_pair_unknowns_to_storage_pairs_by_position():
    """ADF unknowns at positions 0,1 pair with the first 2 cross-page
    storage attachments. Storage entries WITHOUT content_title (same-page
    ones) are excluded from pairing."""
    adf_unknowns = [
        {"position": 0, "placeholder_id": "CROSSPAGE-0"},
        {"position": 5, "placeholder_id": "CROSSPAGE-5"},
    ]
    storage = [
        # same-page (no content_title)
        {"position": 0, "filename": "local.png", "content_title": ""},
        # cross-page #1
        {"position": 1, "filename": "design.docx",
         "content_title": "Source Page A"},
        # cross-page #2
        {"position": 2, "filename": "data.csv",
         "content_title": "Source Page B"},
    ]
    pairs = pair_unknowns_to_storage(adf_unknowns, storage)
    assert len(pairs) == 2, pairs
    assert pairs[0]["filename"] == "design.docx", pairs[0]
    assert pairs[0]["content_title"] == "Source Page A", pairs[0]
    assert pairs[0]["matched"] is True, pairs[0]
    assert pairs[1]["filename"] == "data.csv", pairs[1]
    assert pairs[1]["content_title"] == "Source Page B", pairs[1]


def test_cross_page_resolved_markdown_has_filename_and_marker():
    """build_resolved_markdown produces a clean file-card link with the
    full round-trip marker carrying source-page provenance."""
    md = build_resolved_markdown(
        filename="design.docx",
        media_id="abc-123-def",
        source_page_id="9999",
        source_page_title="Source Page A",
    )
    assert "[design.docx]" in md, md
    assert "(images/design.docx)" in md, md
    assert "id=abc-123-def" in md, md
    assert "collection=contentId-9999" in md, md
    assert "source-page=9999" in md, md
    assert 'source-page-title="Source Page A"' in md, md
    assert "UNKNOWN" not in md, md


def test_cross_page_graceful_warning_no_unknown_token():
    """Graceful warning blockquote when source page can't be located —
    no UNKNOWN_MEDIA_ID literal, no <<crosspage:N>> placeholder."""
    md = build_warning_markdown(
        filename="design.docx",
        source_page_title="Lost Source Page",
        base_url="https://example.atlassian.net",
        space_key="SPACE",
    )
    assert "design.docx" in md, md
    assert "Lost Source Page" in md, md
    assert "Cross-page attachment" in md, md
    assert "UNKNOWN" not in md, md
    assert "<<crosspage" not in md, md
    # Includes a search link as fallback
    assert "https://example.atlassian.net/wiki" in md, md


# ============================================================================
# Phase B — outbound
# ============================================================================


def _import_md_to_adf():
    # Late import — actions/publish_helper.py has heavy imports
    actions_dir = SKILL_ROOT / "actions"
    if str(actions_dir) not in sys.path:
        sys.path.insert(0, str(actions_dir))
    import publish_helper  # type: ignore
    return publish_helper._md_to_adf


def test_md_to_adf_plain_link_to_images_pdf_emits_mediasingle_filecard():
    """A standalone paragraph `[Test](images/test.pdf)` (NO marker) is
    promoted to a mediaSingle with file-card placeholder."""
    md_to_adf = _import_md_to_adf()
    images: list = []
    md = "[Test SDP Doc](images/test-doc.pdf)\n"
    adf = md_to_adf(md, images_collector=images)
    # Find media node
    media_nodes: list = []

    def _walk(n):
        if isinstance(n, dict):
            if n.get("type") == "media":
                media_nodes.append(n)
            for v in n.values():
                _walk(v)
        elif isinstance(n, list):
            for x in n:
                _walk(x)
    _walk(adf)
    assert len(media_nodes) >= 1, f"expected media node; adf={adf}"
    mn = media_nodes[0]
    assert mn["attrs"].get("id", "").startswith("PLACEHOLDER:images/"), mn
    assert mn["attrs"]["type"] == "file", mn
    # Sidecar collected
    assert any(
        "test-doc.pdf" in (i.get("source_relpath") or "")
        for i in images
    ), images


def test_md_to_adf_plain_image_link_emits_mediasingle_image():
    """A standalone `![alt](images/X.png)` (no marker) still works as
    image-card — regression coverage."""
    md_to_adf = _import_md_to_adf()
    images: list = []
    md = "![logo](images/logo.png)\n"
    adf = md_to_adf(md, images_collector=images)
    media_nodes: list = []

    def _walk(n):
        if isinstance(n, dict):
            if n.get("type") == "mediaSingle":
                media_nodes.append(n)
            for v in n.values():
                _walk(v)
        elif isinstance(n, list):
            for x in n:
                _walk(x)
    _walk(adf)
    assert len(media_nodes) >= 1, adf
    assert any(i["source_relpath"].endswith("logo.png") for i in images)


def test_md_to_adf_marker_present_no_double_handling():
    """When the round-trip marker IS present, the existing path handles
    it — no duplicate media node from the new plain-link branch."""
    md_to_adf = _import_md_to_adf()
    images: list = []
    md = "[design.docx](images/design.docx)<!-- media id=abc -->\n"
    adf = md_to_adf(md, images_collector=images)
    media_nodes: list = []

    def _walk(n):
        if isinstance(n, dict):
            if n.get("type") in ("media", "mediaInline"):
                media_nodes.append(n)
            for v in n.values():
                _walk(v)
        elif isinstance(n, list):
            for x in n:
                _walk(x)
    _walk(adf)
    # Exactly one media node — no duplication
    assert len(media_nodes) == 1, f"expected 1 media node, got {media_nodes}"
    # Sidecar has exactly one entry
    assert len(images) == 1, images


def test_upload_images_scanner_catches_plain_link():
    """When _md_to_adf processes plain `[X](images/Y.pdf)` (no marker), the
    images_collector sidecar still picks it up — same behavior as
    upload-images would see."""
    md_to_adf = _import_md_to_adf()
    images: list = []
    md = (
        "Some prose. Here is a link: [Test](images/test.pdf) inline.\n\n"
        "And a standalone:\n\n"
        "[Standalone](images/standalone.docx)\n"
    )
    md_to_adf(md, images_collector=images)
    relpaths = {i["source_relpath"] for i in images}
    assert "images/test.pdf" in relpaths, relpaths
    assert "images/standalone.docx" in relpaths, relpaths


# ============================================================================
# Phase C — round-trip + utilities
# ============================================================================


def test_mime_decide_card_kind():
    """Image extensions go image-card; everything else is file-card."""
    assert is_image_extension("images/foo.png") is True
    assert is_image_extension("images/foo.jpg") is True
    assert is_image_extension("images/FOO.GIF") is True
    assert is_image_extension("images/data.csv") is False
    assert is_image_extension("images/doc.pdf") is False
    assert decide_card_kind("images/foo.png") == "image"
    assert decide_card_kind("images/data.csv") == "file"
    assert decide_card_kind("") == "file"


def test_round_trip_unknown_to_resolved_to_publish_to_re_adopt():
    """Mocked end-to-end:
       1. ADF with UNKNOWN_MEDIA_ID → normalize captures cross_page_unknowns
       2. Storage XHTML provides filename + source_page_title
       3. pair_unknowns_to_storage gives us the pair
       4. build_resolved_markdown emits the proper file-card + marker
       5. _md_to_adf round-trips that markdown → media node with media_id
       6. After publish, the page's ADF would have id=<real-uuid> +
          collection=contentId-<page>; that ADF normalizes back to
          standard marker (no CROSSPAGE).
    """
    # Step 1: ADF unknown
    adf_unknown = {
        "type": "doc",
        "content": [
            {"type": "mediaGroup", "content": [
                {"type": "media", "attrs": {
                    "id": "UNKNOWN_MEDIA_ID",
                    "collection": "",
                    "type": "file",
                    "__fileName": "UNKNOWN_ATTACHMENT",
                }}
            ]}
        ],
    }
    rep = NormalizationReport()
    adf_to_markdown(adf_unknown, report=rep)
    assert len(rep.cross_page_unknowns) == 1

    # Step 2 + 3: storage XHTML pairs to filename + title
    xhtml = '<ri:attachment ri:filename="design.docx" ri:content-title="Source Page X" />'
    pairs = pair_unknowns_to_storage(
        rep.cross_page_unknowns, parse_storage_xhtml(xhtml)
    )
    assert pairs[0]["matched"]
    assert pairs[0]["filename"] == "design.docx"

    # Step 4: resolved markdown
    resolved_md = build_resolved_markdown(
        filename=pairs[0]["filename"],
        media_id="real-uuid-456",
        source_page_id="7777",
        source_page_title=pairs[0]["content_title"],
    )
    assert "id=real-uuid-456" in resolved_md
    assert "source-page=7777" in resolved_md

    # Step 5: publish round-trip — _md_to_adf consumes the resolved markdown
    md_to_adf = _import_md_to_adf()
    images: list = []
    adf2 = md_to_adf(resolved_md + "\n", images_collector=images)
    media_nodes: list = []

    def _walk(n):
        if isinstance(n, dict):
            if n.get("type") in ("media", "mediaInline"):
                media_nodes.append(n)
            for v in n.values():
                _walk(v)
        elif isinstance(n, list):
            for x in n:
                _walk(x)
    _walk(adf2)
    assert len(media_nodes) == 1, media_nodes
    # Media node id is the placeholder (publish would patch it post-upload)
    assert media_nodes[0]["attrs"]["id"].startswith("PLACEHOLDER:images/"), media_nodes
    assert images[0]["source_relpath"] == "images/design.docx", images

    # Step 6: simulate post-upload re-adopt — Confluence has now stored
    # the file as a normal page attachment, so the next ADF carries
    # id=real-uuid + collection=contentId-<page>. Normalize back.
    adf_after = {
        "type": "doc",
        "content": [
            {"type": "mediaGroup", "content": [
                {"type": "media", "attrs": {
                    "id": "real-uuid-456",
                    "collection": "contentId-7777",
                    "type": "file",
                    "fileName": "design.docx",
                }}
            ]}
        ],
    }
    rep2 = NormalizationReport()
    md3 = adf_to_markdown(adf_after, report=rep2)
    # Standard round-trip marker, no CROSSPAGE token
    assert len(rep2.cross_page_unknowns) == 0
    assert "<!-- media id=real-uuid-456 collection=contentId-7777 -->" in md3, md3
    assert "<<crosspage" not in md3
    assert "UNKNOWN" not in md3


# ============================================================================
# Driver
# ============================================================================

if __name__ == "__main__":
    _run("test_normalizer_detects_unknown_media_id_and_tracks_position",
         test_normalizer_detects_unknown_media_id_and_tracks_position)
    _run("test_parse_storage_xhtml_extracts_ri_attachment",
         test_parse_storage_xhtml_extracts_ri_attachment)
    _run("test_pair_unknowns_to_storage_pairs_by_position",
         test_pair_unknowns_to_storage_pairs_by_position)
    _run("test_cross_page_resolved_markdown_has_filename_and_marker",
         test_cross_page_resolved_markdown_has_filename_and_marker)
    _run("test_cross_page_graceful_warning_no_unknown_token",
         test_cross_page_graceful_warning_no_unknown_token)
    _run("test_md_to_adf_plain_link_to_images_pdf_emits_mediasingle_filecard",
         test_md_to_adf_plain_link_to_images_pdf_emits_mediasingle_filecard)
    _run("test_md_to_adf_plain_image_link_emits_mediasingle_image",
         test_md_to_adf_plain_image_link_emits_mediasingle_image)
    _run("test_md_to_adf_marker_present_no_double_handling",
         test_md_to_adf_marker_present_no_double_handling)
    _run("test_upload_images_scanner_catches_plain_link",
         test_upload_images_scanner_catches_plain_link)
    _run("test_mime_decide_card_kind", test_mime_decide_card_kind)
    _run("test_round_trip_unknown_to_resolved_to_publish_to_re_adopt",
         test_round_trip_unknown_to_resolved_to_publish_to_re_adopt)

    print()
    print(f"{_PASSED}/{_PASSED + _FAILED} passed")
    sys.exit(0 if _FAILED == 0 else 1)
