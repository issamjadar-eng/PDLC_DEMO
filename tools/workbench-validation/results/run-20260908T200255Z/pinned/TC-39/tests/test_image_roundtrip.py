"""Image roundtrip regression tests for change-control.

Covers the three code paths added when the skill gained end-to-end
image roundtrip support:

  1. Normalizer captures media-node metadata in `report.images` and
     emits markdown with a `<!-- media id=... -->` round-trip marker.
  2. `_md_to_adf` recognizes both `![alt](images/<file>)` (block-level
     promotion to `mediaSingle`) and inline images (mediaInline), and
     emits placeholder ids of the form `PLACEHOLDER:<relpath>` while
     populating an `images_collector` sidecar list.
  3. `_patch_adf_placeholders` swaps every placeholder id for the
     real attachment id from a {placeholder: id} map.

Offline only — no Confluence calls. Run with:

    python3 .claude/skills/change-control/tests/test_image_roundtrip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.normalizer import NormalizationReport, adf_to_markdown  # noqa: E402
from actions.publish_helper import (  # noqa: E402
    _md_to_adf,
    _patch_adf_placeholders,
)


def _local_resolver(filename: str, media_id):
    return f"images/{filename}" if filename else f"images/{media_id or 'media'}.bin"


def test_normalizer_extracts_media_metadata():
    adf = {
        "type": "doc",
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "before"}]},
            {"type": "mediaSingle", "content": [
                {"type": "media", "attrs": {
                    "type": "file",
                    "id": "media-id-abc",
                    "collection": "contentId-123",
                    "fileName": "screenshot.png",
                    "alt": "Test image",
                    "width": 800,
                    "height": 600,
                }},
            ]},
            {"type": "paragraph", "content": [{"type": "text", "text": "after"}]},
        ],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf, attachment_url=_local_resolver, report=report)
    assert "images/screenshot.png" in md
    assert "<!-- media id=media-id-abc" in md
    assert len(report.images) == 1
    img = report.images[0]
    assert img["media_id"] == "media-id-abc"
    assert img["filename"] == "screenshot.png"
    assert img["target_relpath"] == "images/screenshot.png"
    assert img["width"] == 800
    assert img["height"] == 600


def test_md_to_adf_emits_mediaSingle_with_placeholder():
    md = (
        "# Title\n\nSome text.\n\n"
        "![Screenshot](images/screenshot.png)<!-- media id=abc -->\n\n"
        "More text.\n"
    )
    sidecar: list = []
    adf = _md_to_adf(md, images_collector=sidecar)
    media_singles = [n for n in adf["content"] if n.get("type") == "mediaSingle"]
    assert len(media_singles) == 1
    media = media_singles[0]["content"][0]
    assert media["type"] == "media"
    assert media["attrs"]["id"] == "PLACEHOLDER:images/screenshot.png"
    assert media["attrs"]["type"] == "file"
    assert media["attrs"].get("alt") == "Screenshot"
    assert len(sidecar) == 1
    assert sidecar[0]["placeholder"] == "PLACEHOLDER:images/screenshot.png"
    assert sidecar[0]["source_relpath"] == "images/screenshot.png"
    assert sidecar[0]["alt"] == "Screenshot"


def test_md_to_adf_external_image_skips_sidecar():
    sidecar: list = []
    _md_to_adf(
        "![External](https://example.com/img.png)\n",
        images_collector=sidecar,
    )
    assert sidecar == [], "external image should not enter sidecar"


def test_md_to_adf_no_images_yields_empty_sidecar():
    sidecar: list = []
    _md_to_adf("# Just text\n\nNo images here.\n", images_collector=sidecar)
    assert sidecar == []


def test_patch_adf_swaps_placeholders():
    md = "![X](images/file.png)<!-- media id=abc -->\n"
    sidecar: list = []
    adf = _md_to_adf(md, images_collector=sidecar)
    patched = _patch_adf_placeholders(
        adf,
        {"PLACEHOLDER:images/file.png": "real-id-xyz"},
    )
    media = patched["content"][0]["content"][0]
    assert media["attrs"]["id"] == "real-id-xyz"
    assert media["attrs"]["type"] == "file"


def test_patch_adf_leaves_unmapped_placeholders_alone():
    md = "![X](images/file.png)\n"
    adf = _md_to_adf(md)
    patched = _patch_adf_placeholders(adf, {})  # empty map
    media = patched["content"][0]["content"][0]
    # Untouched — caller can surface the unresolved placeholder.
    assert media["attrs"]["id"] == "PLACEHOLDER:images/file.png"


def test_full_roundtrip_preserves_media_node():
    """ADF (with media node) → md → ADF should preserve a mediaSingle."""
    adf_in = {
        "type": "doc",
        "content": [
            {"type": "mediaSingle", "content": [
                {"type": "media", "attrs": {
                    "type": "file",
                    "id": "abc",
                    "fileName": "diagram.svg",
                    "alt": "diagram",
                }},
            ]},
        ],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf_in, attachment_url=_local_resolver, report=report)
    sidecar: list = []
    adf_out = _md_to_adf(md, images_collector=sidecar)
    assert any(n.get("type") == "mediaSingle" for n in adf_out["content"])
    assert len(sidecar) == 1
    assert sidecar[0]["source_relpath"] == "images/diagram.svg"


def test_existing_publish_paths_still_work():
    """Heading / panel / table / extension nodes still emit correctly
    after the image-handling additions."""
    md = (
        "# Heading\n\n"
        "Para with **bold** and *italic* and [link](https://example.com).\n\n"
        "> **[info]** This is an info panel.\n\n"
        "| col1 | col2 |\n| --- | --- |\n| a | b |\n\n"
        "<!-- confluence-side: toc -->\n"
    )
    adf = _md_to_adf(md)
    types = [n.get("type") for n in adf["content"]]
    assert "heading" in types
    assert "panel" in types
    assert "table" in types
    assert "extension" in types


def _run_all() -> int:
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {t.__name__}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"ERROR {t.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run_all())
