"""Pre-push markdown transformations for `publish` / `review-formal-update`.

Source markdown in this repo is authored for human + git workflows;
Confluence's storage pipeline doesn't quite handle every form. The
transformations here are the locked list from Probe A + Probe G:

  1. **Frontmatter strip** — repo docs lead with an HTML comment block
     (`<!-- ... -->`) holding YAML-style metadata or a changelog. Confluence
     would render the comment markers as-is in some flavors. We strip the
     leading comment block before push.
  2. **Internal `.md` cross-link rewrite** — `[text](relative/path.md)`
     → `[text](https://<base>/wiki/spaces/<KEY>/pages/<ID>)` using the
     project-wide page-ID manifest (`docs/.change-control/state.json`
     `page_index`). Three miss policies: `lenient` (default; strip wrapper,
     keep anchor text, append `(_pending Confluence publish_)`), `strict`
     (raise — caller decides whether to fail-loud), `placeholder` (keep
     broken link + warn).
  3. **Code-fence language sanitization** — swap an opening fence
     ``` ```html ``` to ``` ```text ``` so embedded HTML inside
     doc-conventions example blocks doesn't get re-parsed by the
     markdown→storage pipeline (Probe A finding #3).

This module is intentionally pure — no I/O. The caller resolves the
manifest and frontmatter ahead of time and passes them in.
"""
from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass, field
from typing import Literal, Mapping


# ---- Markdown link-destination encode/decode ----
#
# CommonMark + GFM require URL-encoded characters (or angle-bracket-wrapped
# URLs) for link destinations that contain spaces, parentheses, ampersands,
# etc. A literal space inside a `[...](...)` destination breaks the parser
# and the link renders as plain text. We always emit the percent-encoded
# form into the URL slot of any markdown link (image, file-card, attachment
# table row, smartcard placeholder ref) and decode on the publish side
# before mapping the destination back to a local file path.
#
# `safe="/_-."` keeps path separators and common filename punctuation
# unescaped so encoded paths remain human-readable.


def md_link_dest(path: str) -> str:
    """URL-encode a relative path for use inside a markdown `(...)`
    destination. Preserves `/`, `_`, `-`, and `.`; encodes spaces, parens,
    ampersands, non-ASCII, and other CommonMark/GFM-significant chars."""
    if path is None:
        return ""
    return urllib.parse.quote(path, safe="/_-.")


def md_link_dest_decode(dest: str) -> str:
    """Inverse of :func:`md_link_dest`. Used on the publish side to map a
    markdown link destination back to a local relpath before looking up
    the binary on disk."""
    if dest is None:
        return ""
    return urllib.parse.unquote(dest)


# ---- Public types ----


MissPolicy = Literal["lenient", "strict", "placeholder"]


@dataclass
class PageRef:
    """A single entry in the project-wide cross-link manifest."""

    page_id: str
    space_key: str
    title: str = ""
    base_url: str = ""

    def confluence_url(self, base_url: str | None = None) -> str:
        url = (self.base_url or base_url or "").rstrip("/")
        if not url:
            return f"/wiki/spaces/{self.space_key}/pages/{self.page_id}"
        return f"{url}/wiki/spaces/{self.space_key}/pages/{self.page_id}"


@dataclass
class TransformReport:
    """What the transformer did. Surfaced in publish output."""

    rewrote: list[dict] = field(default_factory=list)  # {anchor, target_md, target_url}
    missed: list[dict] = field(default_factory=list)  # {anchor, target_md, policy_applied}
    fence_swaps: int = 0
    frontmatter_stripped: bool = False
    internal_blocks_stripped: list[dict] = field(default_factory=list)  # {kind, line_count}


# Kinds of HTML-comment blocks that are project-internal tooling-only and
# MUST NOT round-trip to Confluence. Distinct from `AUTO:*` and
# `confluence-side:*` (which are tooling-owned but round-trip-safe — the
# adopt path re-renders them on inbound). Anything in this list is stripped
# during the publish transform.
#
# Adding a kind here is a contract: it is invisible on the published page,
# but the source-of-truth for that metadata must live somewhere ELSE that
# the round-trip cannot see (e.g., under tools/project-console/...).
#
# History:
#   - TRACE: trace-matrix schema-map pointers (task ben/152). External
#     projection lives under tools/project-console/trace-matrix/; the
#     in-source comment is a discoverability + refresh-contract pointer.
INTERNAL_ONLY_BLOCK_KINDS: tuple[str, ...] = ("TRACE",)


@dataclass
class TransformOptions:
    base_url: str = ""
    miss_policy: MissPolicy = "lenient"
    pending_annotation: str = "(_pending Confluence publish_)"
    # Optional: a function that resolves a relative .md path (relative
    # to the source doc, or repo-root) → manifest key. Defaults to
    # normalizing to a clean repo-relative path.
    path_normalizer: str | None = None  # reserved for future use


# ---- Public API ----


def transform_markdown(
    source: str,
    source_doc_path: str,
    page_index: Mapping[str, PageRef],
    options: TransformOptions | None = None,
) -> tuple[str, TransformReport]:
    """Apply the pre-push transformations.

    `source` — markdown source string.
    `source_doc_path` — repo-relative path of the source doc; used as
        the base for resolving relative `.md` cross-links.
    `page_index` — manifest mapping of repo-relative `.md` path →
        `PageRef`. Caller is responsible for keying consistently
        (we normalize lookups via `_normalize_link_target`).
    `options` — `TransformOptions` controlling miss policy + base URL.

    Returns `(transformed_markdown, TransformReport)`.
    """
    opts = options or TransformOptions()
    rep = TransformReport()

    text, did_strip = strip_leading_html_comment(source)
    rep.frontmatter_stripped = did_strip

    text, stripped_blocks = strip_internal_only_blocks(text)
    rep.internal_blocks_stripped = stripped_blocks

    text, swap_count = swap_html_fence_to_text(text)
    rep.fence_swaps = swap_count

    text = rewrite_internal_md_links(
        text,
        source_doc_path=source_doc_path,
        page_index=page_index,
        options=opts,
        report=rep,
    )

    return text, rep


# ---- Step 1: frontmatter strip ----


_LEADING_HTML_COMMENT_RE = re.compile(
    r"\A\s*<!--.*?-->\s*",
    re.DOTALL,
)


def strip_leading_html_comment(source: str) -> tuple[str, bool]:
    """If the doc opens with a frontmatter HTML comment block, strip it
    (and the immediately following blank line). Returns
    `(stripped, did_strip)`.

    A frontmatter block is multiline with at least one `key: value`
    line — distinguishing it from single-line zone sentinels like
    `<!-- confluence-side: attachments labels=actual position=0 -->`
    which `read_frontmatter` may leave at the body's leading edge but
    which must NOT be eaten here (they carry round-trip macro params).
    """
    m = _LEADING_HTML_COMMENT_RE.match(source)
    if not m:
        return source, False
    block = m.group(0)
    # Single-line comment → not frontmatter; leave it alone.
    if "\n" not in block.rstrip():
        return source, False
    # Confluence-side sentinel → also leave alone (cross-comment line
    # noise is possible but unusual; in practice the sentinel is one
    # line). Be conservative: a leading `<!-- confluence-side:` or
    # `<!-- /confluence-side:` is never a frontmatter block.
    head = block.lstrip().lstrip("<!").lstrip().lower()
    if head.startswith("confluence-side:") or head.startswith("/confluence-side:"):
        return source, False
    return source[m.end():], True


# ---- Step 1b: internal-only block strip ----


def _build_internal_block_re(kinds: tuple[str, ...]) -> re.Pattern[str]:
    """Compile the regex that matches any HTML comment whose first token
    is one of `kinds:` (with optional leading `/` for paired-closing form).
    """
    if not kinds:
        # Match nothing.
        return re.compile(r"(?!.*)")
    alt = "|".join(re.escape(k) for k in kinds)
    return re.compile(
        rf"<!--\s*/?(?P<kind>{alt}):[A-Z][A-Z0-9-]*\b.*?-->[ \t]*\n?",
        re.DOTALL,
    )


_INTERNAL_BLOCK_RE = _build_internal_block_re(INTERNAL_ONLY_BLOCK_KINDS)


def strip_internal_only_blocks(
    source: str,
    kinds: tuple[str, ...] | None = None,
) -> tuple[str, list[dict]]:
    """Remove every HTML-comment block whose first token is one of
    `INTERNAL_ONLY_BLOCK_KINDS` (or the explicit `kinds` override).
    Returns `(stripped, blocks)` where each block is a dict with
    `kind` and `line_count` (1 for single-line, >1 for multi-line).

    Designed to run AFTER `strip_leading_html_comment` so the doc's
    leading frontmatter (which is also a multi-line HTML comment but
    contains `key: value` lines, not `KIND:SUBKIND` first-tokens) is not
    re-evaluated. Idempotent — running on already-stripped output is a
    no-op.
    """
    pattern = (
        _INTERNAL_BLOCK_RE
        if kinds is None
        else _build_internal_block_re(kinds)
    )
    blocks: list[dict] = []

    def _capture(m: re.Match) -> str:
        body = m.group(0)
        blocks.append({
            "kind": m.group("kind"),
            "line_count": body.count("\n") + (0 if body.endswith("\n") else 1),
        })
        return ""

    out = pattern.sub(_capture, source)
    return out, blocks


# ---- Step 2: code-fence language swap ----


# Match opening fence lines that declare html (case-insensitive). We do
# NOT swap the closing fence (it has no language hint to begin with).
_HTML_FENCE_OPEN_RE = re.compile(
    r"^(?P<indent> {0,3})(?P<fence>`{3,})(?P<spaces> *)html\s*$",
    re.MULTILINE | re.IGNORECASE,
)


def swap_html_fence_to_text(source: str) -> tuple[str, int]:
    """Swap ` ```html ` opening fences to ` ```text `. Returns
    `(transformed, swap_count)`. Only the language token is replaced
    — fence length and indent are preserved.
    """
    count = 0

    def _sub(m: re.Match) -> str:
        nonlocal count
        count += 1
        return f"{m.group('indent')}{m.group('fence')}{m.group('spaces')}text"

    out = _HTML_FENCE_OPEN_RE.sub(_sub, source)
    return out, count


# ---- Step 3: internal .md cross-link rewrite ----


# Matches `[text](relative/path.md)` and `[text](relative/path.md#anchor)`,
# excluding URL-scheme links (http://, https://, mailto:, etc.). Conservative
# — we only rewrite where the destination ends in .md (case-insensitive)
# with an optional #fragment.
_MD_LINK_RE = re.compile(
    r"(?<!\!)"  # not an image
    r"\["
    r"(?P<text>[^\]\n]+)"
    r"\]\("
    r"(?P<target>[^\s)]+?\.md(?:#[^\s)]*)?)"
    r"\)",
    re.IGNORECASE,
)


def rewrite_internal_md_links(
    source: str,
    source_doc_path: str,
    page_index: Mapping[str, PageRef],
    options: TransformOptions | None = None,
    report: TransformReport | None = None,
) -> str:
    """Rewrite `[text](relative/path.md)` to a Confluence URL.

    Misses are handled per `options.miss_policy`:
      - `"lenient"` (default): emit `text {pending_annotation}` (no link)
      - `"strict"`: raise `KeyError` naming the missing target
      - `"placeholder"`: leave the original `[text](path.md)` link, no rewrite
    """
    opts = options or TransformOptions()
    rep = report if report is not None else TransformReport()

    def _resolve(target: str) -> tuple[str, str]:
        """Return `(normalized_key, fragment)` for a link target."""
        fragment = ""
        if "#" in target:
            target, fragment = target.split("#", 1)
        key = _normalize_link_target(target, source_doc_path)
        return key, fragment

    def _sub(m: re.Match) -> str:
        text = m.group("text")
        target = m.group("target")
        key, fragment = _resolve(target)
        ref = page_index.get(key)
        if ref is None:
            # Try without leading "./" or normalized variants
            for cand in _candidate_keys(key):
                ref = page_index.get(cand)
                if ref is not None:
                    break
        if ref is None:
            rep.missed.append({
                "anchor": text,
                "target_md": target,
                "policy_applied": opts.miss_policy,
            })
            if opts.miss_policy == "strict":
                raise KeyError(f"no page-index entry for {target!r} (resolved as {key!r})")
            if opts.miss_policy == "placeholder":
                return m.group(0)  # leave original link untouched
            # lenient
            return f"{text} {opts.pending_annotation}"
        url = ref.confluence_url(opts.base_url)
        if fragment:
            url += "#" + fragment
        rep.rewrote.append({"anchor": text, "target_md": target, "target_url": url})
        return f"[{text}]({url})"

    return _MD_LINK_RE.sub(_sub, source)


def _normalize_link_target(target: str, source_doc_path: str) -> str:
    """Resolve a relative target against the source doc's directory and
    normalize to a forward-slash repo-relative path.

    Pure-string normalization — no filesystem access; preserves keys
    that don't exist on disk (the manifest may use canonical keys).
    """
    target = target.strip()
    # Absolute repo-rooted (leading slash) — strip the slash
    if target.startswith("/"):
        return target.lstrip("/")
    # If the source doc lives at "a/b/c.md", its dir is "a/b".
    src_dir_parts = source_doc_path.replace("\\", "/").split("/")[:-1]
    target_parts = target.replace("\\", "/").split("/")
    stack: list[str] = list(src_dir_parts)
    for part in target_parts:
        if part in ("", "."):
            continue
        if part == "..":
            if stack:
                stack.pop()
            continue
        stack.append(part)
    return "/".join(stack)


def _candidate_keys(key: str) -> list[str]:
    """Try a few alternate spellings to be forgiving about manifest casing."""
    out = [key]
    if not key.startswith("./"):
        out.append("./" + key)
    if key.startswith("./"):
        out.append(key[2:])
    return out
