"""
Cosmetic vs substantive edit classification for the freeze hook.

STATUS: STUB. The classifier is conservative — false positives (treat
substantive as cosmetic) are much worse than false negatives.

Cosmetic edits get a lighter prompt from the freeze hook. Substantive
edits require typing the full confirmation phrase.

Cosmetic categories (under consideration — see task 017 open question #6):
  - frontmatter-only changes
  - HTML-comment-only changes
  - changelog row appends
  - whitespace / formatting only

Anything else = substantive.
"""
from __future__ import annotations

from enum import Enum


class EditKind(str, Enum):
    COSMETIC = "cosmetic"
    SUBSTANTIVE = "substantive"


def classify(old_content: str, new_content: str) -> EditKind:
    """Classify a proposed edit. STUB — always returns SUBSTANTIVE for safety."""
    raise NotImplementedError("diff_classify.classify is a stub.")
