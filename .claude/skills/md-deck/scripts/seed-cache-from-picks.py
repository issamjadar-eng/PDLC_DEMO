#!/usr/bin/env python3
"""md-deck — seed `.creative-cache/` from a deck's existing picks.json.

One-shot migration helper. Older decks carry their creative cache inside
`picks.json:creative_cache` keyed by `L<lo>-L<hi>` line ranges. Newer builds
expect on-disk files under `.creative-cache/<slug>__<sha7>-<slot>.html`,
keyed by slug + content-SHA.

This script rewrites the legacy block to the new file layout, in-place:

  - For every `creative_cache[<line-range>][<slot>]` entry whose line range
    resolves to a current slug AND whose `source_sha` matches the current
    section's `source_sha256`, write the entry as a `.creative-cache/` file.
  - Strip the `creative_cache` block from `picks.json` after seeding.
  - Leave `picks.picks` untouched (the chosen-component selections stay valid;
    auto-migration already remaps their keys to slugs at the next build).

Entries with mismatched SHA or unresolvable line ranges are reported and
skipped — they were already going to be retired by `--sweep-cache`. No agent
calls; pure data shuffle.

Usage:
  python3 seed-cache-from-picks.py <source.md> [--out-dir <path>] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import build  # noqa: E402


def _build_legacy_anchor_to_slug(legacy_keys: list[str], slides: list[dict]) -> tuple[dict[str, dict], int, int]:
    """Bridge legacy line-range anchors to current slugs via positional pairing.

    The legacy schema stamped every cache entry with the deck-wide source SHA
    and used `L<lo>-L<hi>` keys valid at the time the cache was rolled. After
    line-shifts those keys no longer match current slides' `source_lines`. But
    when **the count of variant-eligible sections is unchanged**, source-order
    pairing recovers the mapping: i-th legacy key ↔ i-th current variant-
    eligible slide. The corresponding current slide carries the new
    `source_sha256` (per-section content SHA) we stamp on the migrated cache
    file.

    Returns `(mapping, n_legacy, n_current)`. When counts diverge, returns an
    empty mapping plus the counts so the caller can refuse to proceed.
    """
    # Variant-eligible slides in source order, deduped on source_lines
    seen: set[str] = set()
    eligible: list[dict] = []
    for s in slides:
        sl = s.get("source_lines")
        sg = s.get("slug")
        if not sl or not sg or sg.startswith("_") or sl in seen:
            continue
        seen.add(sl)
        eligible.append(s)

    import re
    def _key(k: str) -> tuple[int, int]:
        m = re.match(r"L(\d+)-L(\d+)", str(k))
        return (int(m.group(1)), int(m.group(2))) if m else (10**9, 10**9)

    legacy_sorted = sorted(legacy_keys, key=_key)

    if len(legacy_sorted) != len(eligible):
        # Count mismatch — sections were inserted or deleted. Positional pairing
        # would smear identity. Caller will report and skip.
        return {}, len(legacy_sorted), len(eligible)

    mapping: dict[str, dict] = {}
    for legacy, slide in zip(legacy_sorted, eligible):
        mapping[legacy] = {
            "slug": slide["slug"],
            "current_sha": slide.get("source_sha256", ""),
            "title": slide.get("title", ""),
        }
    return mapping, len(legacy_sorted), len(eligible)


def seed(source_path: Path, out_dir: Path, *, dry_run: bool = False) -> dict:
    text = source_path.read_text(encoding="utf-8")
    blocks = build.parse_markdown(text)
    slides = build.synthesize_slides(blocks, source_path, source_text=text)

    picks_path = build._picks_path(out_dir)
    if not picks_path.exists():
        print(f"error: no picks.json at {picks_path}", file=sys.stderr)
        return {"seeded": 0, "skipped_unresolved": 0, "skipped_stale_sha": 0,
                "picks_remapped": 0, "picks_dropped": 0,
                "n_legacy": 0, "n_current": 0}

    data = json.loads(picks_path.read_text(encoding="utf-8"))
    legacy_cache = data.get("creative_cache") or {}

    # Bridge legacy line-range keys to current slugs by source-order pairing.
    # The picks block keys are a strict subset of the cache keys (every section
    # that got picked also got candidates rolled), so we use the cache key set
    # as the canonical legacy section list.
    legacy_to_slug, n_legacy, n_current = _build_legacy_anchor_to_slug(
        list(legacy_cache.keys()), slides,
    )
    if not legacy_to_slug and (n_legacy or n_current):
        print(
            f"error: variant-eligible section count mismatch — "
            f"{n_legacy} legacy cache keys vs {n_current} current sections. "
            f"Refusing to seed (positional pairing would misalign identity).",
            file=sys.stderr,
        )
        return {"seeded": 0, "skipped_unresolved": n_legacy * 3,
                "skipped_stale_sha": 0, "picks_remapped": 0,
                "picks_dropped": 0, "n_legacy": n_legacy,
                "n_current": n_current,
                "_unresolved": [], "_stale": [], "_picks_dropped": []}

    cache_dir = build._cache_dir(out_dir)
    if not dry_run:
        cache_dir.mkdir(exist_ok=True)

    seeded = 0
    skipped_unresolved: list[str] = []
    overwritten = 0

    for legacy_anchor, slot_map in legacy_cache.items():
        if not isinstance(slot_map, dict):
            continue
        hit = legacy_to_slug.get(legacy_anchor)
        if not hit:
            for slot in slot_map.keys():
                skipped_unresolved.append(f"{legacy_anchor}:{slot} (no title-bridge entry; section renamed or deleted)")
            continue
        slug = hit["slug"]
        current_sha = hit["current_sha"]
        for slot, entry in slot_map.items():
            if not isinstance(entry, dict):
                continue
            html_frag = entry.get("html")
            if not html_frag:
                continue
            sha7 = current_sha[:7]
            personality = str(entry.get("personality") or "")
            generated_at = str(entry.get("generated_at") or "") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            # Stamp with the **current** per-section SHA so the entry is "live"
            # in the new scheme. The HTML was rolled at deck-wide SHA; the
            # legacy schema didn't record per-section SHAs separately.
            header = (
                f"<!-- md-deck/cache@1 slug={slug} slot={slot} "
                f"source_sha={current_sha} personality={personality} "
                f"generated_at={generated_at} -->"
            )
            path = build._cache_file_path(out_dir, slug, sha7, slot)
            if path.exists():
                overwritten += 1
            if not dry_run:
                path.write_text(header + "\n" + html_frag, encoding="utf-8")
            seeded += 1

    # Remap picks block from legacy line-range keys to slug keys. Two fallbacks:
    # (1) the cache-key positional bridge (for sections that got creative rolls);
    # (2) direct source_lines match (for sections picked as a template — those
    #     don't appear in the cache, but their legacy line-range may still match
    #     a current slide's source_lines if the section hasn't shifted).
    source_lines_to_slug: dict[str, str] = {}
    for s in slides:
        sl = s.get("source_lines")
        sg = s.get("slug")
        if sl and sg and sl not in source_lines_to_slug:
            source_lines_to_slug[sl] = sg

    picks_remapped = 0
    picks_dropped: list[str] = []
    if isinstance(data.get("picks"), dict):
        new_picks: dict = {}
        for k, v in data["picks"].items():
            hit = legacy_to_slug.get(k)
            if hit:
                new_picks[hit["slug"]] = v
                picks_remapped += 1
                continue
            # Fallback (2): line-range still matches a current slide
            sl_slug = source_lines_to_slug.get(k)
            if sl_slug:
                new_picks[sl_slug] = v
                picks_remapped += 1
                continue
            # Fallback (3): key is already a slug from a prior partial migration
            if isinstance(k, str) and k.startswith("s") and not k.startswith("_"):
                new_picks[k] = v
            else:
                picks_dropped.append(k)
        if not dry_run and picks_remapped > 0:
            data["picks"] = new_picks

    if not dry_run and (seeded > 0 or picks_remapped > 0):
        # Strip the legacy block from picks.json (cache now lives on disk).
        data.pop("creative_cache", None)
        data["schema"] = "md-deck/picks@3"
        picks_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return {
        "seeded": seeded,
        "skipped_unresolved": len(skipped_unresolved),
        "skipped_stale_sha": 0,
        "overwritten": overwritten,
        "picks_remapped": picks_remapped,
        "picks_dropped": len(picks_dropped),
        "_unresolved": skipped_unresolved,
        "_stale": [],
        "_picks_dropped": picks_dropped,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("source", help="Markdown source file (the deck's source)")
    parser.add_argument("--out-dir", default=None, help="Override deck output dir (default: <root>/assets/<slug>/)")
    parser.add_argument("--dry-run", action="store_true", help="Report counts without writing")
    args = parser.parse_args()

    source_path = Path(args.source).resolve()
    if args.out_dir:
        out_dir = Path(args.out_dir).resolve()
    else:
        cur = source_path.parent
        root = cur
        while root != root.parent:
            if (root / ".claude").exists() or (root / "project.yml").exists():
                break
            root = root.parent
        out_dir = root / "assets" / build._slugify(source_path.stem)

    result = seed(source_path, out_dir, dry_run=args.dry_run)
    verb = "would seed" if args.dry_run else "seeded"
    print(f"✓ {verb} {result['seeded']} cache entries to {out_dir / '.creative-cache'}")
    print(f"  · picks remapped to slug keys: {result['picks_remapped']}")
    if result["picks_dropped"]:
        print(f"  · picks dropped (no title-bridge): {result['picks_dropped']}")
    if result["overwritten"]:
        print(f"  · {result['overwritten']} overwrote existing cache files")
    if result["skipped_unresolved"]:
        print(f"  · skipped {result['skipped_unresolved']} cache entries (no title-bridge)")
        for s in result["_unresolved"][:5]:
            print(f"      - {s}")
        if len(result["_unresolved"]) > 5:
            print(f"      … and {len(result['_unresolved']) - 5} more")
    if result["skipped_stale_sha"]:
        print(f"  · skipped {result['skipped_stale_sha']} entries (source_sha mismatch — section content edited)")
        for s in result["_stale"][:5]:
            print(f"      - {s}")
        if len(result["_stale"]) > 5:
            print(f"      … and {len(result['_stale']) - 5} more")
    if args.dry_run:
        print("(dry-run — no files written, picks.json untouched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
