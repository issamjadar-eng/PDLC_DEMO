"""ben/163 3.1 — Cache-behavior assertions for slug-based section identity.

Runs the md-deck build pipeline (template-only, no `--creative`, so no LLM)
against `tests/fixtures/section-edit-cases.md` after each of four mutations:

  - insert: a new section dropped between existing ones
  - delete: an existing section removed
  - rename: an existing section's heading retitled
  - edit:   an existing section's body changed

For each case we assert the design-table behavior:

  insert → unrelated slugs unchanged, new slug minted.
  delete → orphan slug disappears from current build.
  rename → new slug minted, old slug becomes orphan.
  edit   → slug unchanged, source_sha256 changes.

The build is invoked in-process (no subprocess) and reads only the fixture
file plus a tmp output directory, so the test is hermetic and fast.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Make the build module importable without packaging the skill.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import build  # noqa: E402


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "section-edit-cases.md"


def _slides_for(text: str) -> list[dict]:
    """Synthesize slides directly from in-memory markdown (no file I/O)."""
    blocks = build.parse_markdown(text)
    # synthesize_slides expects a Path for source_path; the value is only used
    # for the title-slide subtitle, so a placeholder works.
    return build.synthesize_slides(blocks, Path("fixture.md"), source_text=text)


def _slug_index(text: str) -> dict[str, dict]:
    """Map slug → {source_sha256, source_lines, title} for variant-eligible slides."""
    out: dict[str, dict] = {}
    for s in _slides_for(text):
        slug = s.get("slug")
        if not slug or slug.startswith("_"):
            continue
        if slug in out:
            continue  # first wins; variants/density-splits inherit identity
        out[slug] = {
            "source_sha256": s.get("source_sha256", ""),
            "source_lines": s.get("source_lines", ""),
            "title": s.get("title", ""),
        }
    return out


class SectionIdentityCases(unittest.TestCase):
    """Each test mutates a copy of the fixture in `self.work` and compares
    the slug index before vs after.
    """

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="md-deck-test-"))
        self.work = self.tmp / "section-edit-cases.md"
        shutil.copy(FIXTURE_PATH, self.work)
        self.baseline_text = self.work.read_text(encoding="utf-8")
        self.baseline = _slug_index(self.baseline_text)
        # Sanity — baseline must contain the four expected slugs
        for expected in ("s1-1-first-section", "s1-2-second-section",
                         "s2-1-third-section", "s2-2-fourth-section"):
            self.assertIn(expected, self.baseline, f"missing baseline slug {expected}")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -- insert -------------------------------------------------------

    def test_insert_section_preserves_unrelated_slugs(self):
        """Insert a new H3 between 1.2 and 2.1; unrelated slug+SHAs unchanged."""
        new_text = self.baseline_text.replace(
            "## 2. Body\n",
            "## 2. Body\n\n### 1.3 Inserted section\n\nFreshly minted body.\n\n",
            1,
        )
        after = _slug_index(new_text)
        # New slug appears
        self.assertIn("s1-3-inserted-section", after)
        # Untouched slugs survive with same content-SHA
        for slug in ("s1-1-first-section", "s1-2-second-section"):
            self.assertEqual(
                self.baseline[slug]["source_sha256"],
                after[slug]["source_sha256"],
                f"insert shifted SHA for unrelated slug {slug}",
            )

    # -- delete -------------------------------------------------------

    def test_delete_section_removes_slug(self):
        """Delete §1.2 — its slug disappears from the current build."""
        text = self.baseline_text
        start = text.index("### 1.2 Second section")
        end = text.index("## 2. Body")
        new_text = text[:start] + text[end:]
        after = _slug_index(new_text)
        self.assertNotIn("s1-2-second-section", after)
        self.assertIn("s1-1-first-section", after)
        self.assertIn("s2-1-third-section", after)

    # -- rename -------------------------------------------------------

    def test_rename_section_mints_new_slug(self):
        """Rename §1.1 — old slug becomes orphan; new slug minted."""
        new_text = self.baseline_text.replace(
            "### 1.1 First section",
            "### 1.1 Renamed first section",
        )
        after = _slug_index(new_text)
        self.assertNotIn("s1-1-first-section", after)
        self.assertIn("s1-1-renamed-first-section", after)

    # -- edit content -------------------------------------------------

    def test_edit_content_keeps_slug_changes_sha(self):
        """Edit §2.2 body — slug unchanged, source_sha256 flips."""
        old_sha = self.baseline["s2-2-fourth-section"]["source_sha256"]
        new_text = self.baseline_text.replace(
            "Fourth section, plain prose. Slug: `s2-2-fourth-section`.",
            "Fourth section — body rewritten. Slug: `s2-2-fourth-section`.",
        )
        self.assertNotEqual(self.baseline_text, new_text)
        after = _slug_index(new_text)
        self.assertIn("s2-2-fourth-section", after)
        self.assertNotEqual(
            old_sha,
            after["s2-2-fourth-section"]["source_sha256"],
            "content edit did not flip source_sha256",
        )


class SweepCacheBehavior(unittest.TestCase):
    """Smoke-check that `sweep_creative_cache` partitions correctly given
    a synthetic on-disk cache. No agent calls."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="md-deck-sweep-"))
        self.cache_dir = self.tmp / ".creative-cache"
        self.cache_dir.mkdir()
        # Live: slug present in current build, sha matches
        # Stale: slug present, sha mismatches
        # Orphan: slug not in current build
        self._write("slug-live", "abc1234", "current")
        self._write("slug-stale", "deadbee", "stale-sha")
        self._write("slug-orphan", "abc1234", "current")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, slug: str, sha7: str, full_sha: str) -> None:
        body = f"<!-- md-deck/cache@1 slug={slug} slot=creative-c source_sha={full_sha} personality= generated_at= -->\n<div>x</div>"
        (self.cache_dir / f"{slug}__{sha7}-creative-c.html").write_text(body, encoding="utf-8")

    def test_partitions_live_stale_orphan(self):
        orphan, stale = build.sweep_creative_cache(
            self.tmp,
            current_slugs={"slug-live", "slug-stale"},
            current_sha="current",
            dry_run=True,
        )
        self.assertEqual(len(orphan), 1, f"expected 1 orphan, got {[p.name for p in orphan]}")
        self.assertIn("slug-orphan", orphan[0].name)
        self.assertEqual(len(stale), 1, f"expected 1 stale, got {[p.name for p in stale]}")
        self.assertIn("slug-stale", stale[0].name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
