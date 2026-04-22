#!/usr/bin/env bash
# =============================================================================
# block-direct-conversion.sh — PreToolUse Bash tripwire for /docflow
#
# Denies LLM-initiated Bash calls to document-conversion tools (pandoc,
# libreoffice/soffice, pdftotext, pdfinfo, pdfimages, pdftoppm, unzip, qpdf,
# pdftk) when they target office documents (.docx/.doc/.xlsx/.xls/.pptx/.pdf).
# All DOCX/PDF/XLSX <-> markdown conversion should go through the /docflow skill
# (which under v30 routes to scripts/adopt_v30.py — a classifier + deterministic
# extractors + parallel focused agents; falls through to the v29 adopter agent
# for non-architecture doc types). Those scripts run gated tools via subprocess
# — NOT through the Bash tool — so the hook never fires on them.
#
# User override: this hook denies by default but is explicitly overrideable —
# `touch .state/docflow-active` unlocks the session so the user can run a gated
# verb directly (quick probes, one-off conversions, cases /docflow can't
# handle). Remove the marker when done. The denial message surfaced to the LLM
# documents this path.
#
# v3 (task 082) — Shell-aware tokenization via python3 shlex, so prose inside
# quoted arguments to OTHER commands no longer trips the verb/extension match.
# Root cause of v2 false-positive: sed-based statement splitting ignored quote
# boundaries, so `gh pr create --body "... pandoc | unzip | ... .docx ..."`
# was (wrongly) split as if the pipes were real shell pipes.
#
# v4 (task 089 session 3) — Added `pdfinfo` to VERBS (v30 extract_pdf.py and
# extract_title_version.py both shell pdfinfo; direct LLM use is still gated
# for parity). Updated denial message to explicitly acknowledge user override
# as a legitimate path, not a "last resort".
#
# Matching algorithm (see task ben/082):
#   1. If tool != Bash, allow.
#   2. If .state/docflow-active exists, allow (docflow agent bypass; relocated
#      from .claude/state/ in ben/083 to escape .claude/** sensitive-file guard).
#   3. Use python3 shlex to tokenize the command into shell-statement chunks
#      (split on ; && || | that are NOT inside quoted strings).
#   4. For each chunk:
#      a. Strip leading `sudo` (possibly with -flags).
#      b. Extract the FIRST token — the command being invoked.
#      c. If that token is NOT in the verb list, continue. Verbs or extensions
#         that appear inside a quoted argument to some OTHER command (prose in
#         a `gh pr create --body`, a commit message, a grep pattern, a string
#         literal) do NOT trigger — they never become a first token of their
#         own chunk because shlex respects quote boundaries.
#      d. If first token IS a verb, check the remaining tokens for any arg
#         ending in a gated extension. If found -> DENY. Purely informational
#         calls (--help, --version, --list-*) are allowed because none of
#         their args end in a gated extension.
#   5. If no chunk triggered a deny, allow.
#
# Known limitations (documented, not fixed):
#   - `bash -c "pandoc foo.docx"` — first token is `bash`, not `pandoc` —
#     ALLOWED. Deliberate bypass surface: users who wrap a conversion call
#     in `bash -c` clearly know what they're doing. The `.state/docflow-active`
#     marker remains the preferred bypass path.
#   - `find . -name '*.docx' -exec pandoc {} \;` — first token is `find`,
#     ALLOWED. Same rationale.
#   - Process substitution `<(pandoc foo.docx)` — not parsed as a chunk;
#     ALLOWED.
#   The hook catches casual drift ("I'll just probe with pandoc"), not a
#   determined bypass.
#
# Exit codes:
#   0 — allow the Bash call to proceed
#   2 — deny; stderr message is surfaced to Claude
# =============================================================================

set -uo pipefail

INPUT="$(cat)"

TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)"
[ "$TOOL_NAME" = "Bash" ] || exit 0

CMD="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)"
[ -n "$CMD" ] || exit 0

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$SCRIPT_DIR/../../../.." && pwd)}"
BYPASS_MARKER="$PROJECT_DIR/.state/docflow-active"

if [ -f "$BYPASS_MARKER" ]; then
    exit 0
fi

# macOS bash 3.2 parser bug workaround (task ben/092):
# `DECISION="$(python3 - "$CMD" <<'PY' ... PY )"` breaks on bash 3.2 when the
# heredoc body contains apostrophes (docstrings with "don't", etc.) — the
# command-substitution tokenizer doesn't treat the quoted heredoc body as inert
# and reports a bogus unmatched-quote error, which also corrupts parsing of the
# later `<<'EOF'` error-message heredoc. Fixed in bash 4.0, but macOS still
# ships 3.2.57 as /bin/bash. Pattern below (read into var, then pipe) avoids
# the $(... <<HEREDOC ...) combo and works on bash 3.2 + 4+ + 5+.
PYCODE=""
IFS= read -r -d '' PYCODE <<'PY' || true
import re
import shlex
import sys

cmd = sys.argv[1]
VERBS = {
    "pandoc", "soffice", "libreoffice", "pdftotext",
    "pdfinfo", "pdfimages", "pdftoppm", "unzip", "qpdf", "pdftk",
}
EXT_RE = re.compile(r"\.(docx|doc|xlsx|xls|pptx|ppt|pdf)(?:$|[/\)])", re.IGNORECASE)

# shlex with posix=True, whitespace_split=False, and punctuation_chars including
# shell operators gives us shell-aware tokenization. tokens=[...] includes
# operators like ';', '&&', '||', '|' as their own tokens, NOT inside quoted
# strings.
try:
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    tokens = list(lex)
except ValueError:
    # Unclosed quote or similar — fall back to allow. We don't want the hook
    # to deny on malformed input; Claude Code will get a shell error anyway.
    print("allow")
    sys.exit(0)

# Split tokens into chunks on shell separators. These separator tokens only
# appear OUTSIDE quotes thanks to shlex, so prose inside a --body="..." stays
# intact in one chunk.
SEPARATORS = {";", "&&", "||", "|", "&", "\n"}
chunks = []
current = []
for t in tokens:
    if t in SEPARATORS:
        if current:
            chunks.append(current)
            current = []
    else:
        current.append(t)
if current:
    chunks.append(current)

def first_token(chunk):
    """Return the first real command token after skipping leading `sudo ...`."""
    i = 0
    while i < len(chunk):
        tok = chunk[i]
        if tok == "sudo":
            i += 1
            # Skip any -flags after sudo (e.g. sudo -E, sudo -H)
            while i < len(chunk) and chunk[i].startswith("-"):
                i += 1
            continue
        return tok, chunk[i + 1:]
    return None, []

for chunk in chunks:
    head, rest = first_token(chunk)
    if head is None:
        continue
    if head not in VERBS:
        continue
    # First token IS a gated verb. Look for a gated extension in any remaining arg.
    for arg in rest:
        if EXT_RE.search(arg):
            print("deny")
            sys.exit(0)

print("allow")
PY

DECISION="$(printf '%s' "$PYCODE" | python3 - "$CMD")"

if [ "$DECISION" = "deny" ]; then
    cat >&2 <<'EOF'
[docflow] This document-conversion verb routes through /docflow by default.

  Default path (owns image extraction, frontmatter, cross-refs, round-trip):
    • /docflow adopt <target>      DHF formal (PDF/DOCX/XLSX) → working MD
                                   (v30 architecture-doc path: adopt_v30.py
                                    orchestrator + classifier + parallel agents;
                                    other doc types fall through to the v29
                                    adopter agent)
    • /docflow convert <doc-id>    Internal QMS source → source-md
    • /docflow import <file>       External DOCX/PDF → project MD
    • /docflow refresh <doc-id>    Update an already-converted source-md

  Direct calls to pandoc/pdftotext/pdfimages/soffice silently drop colors,
  images, structure, and round-trip fidelity — that's why they're gated.

Override — user-initiated ad-hoc use is legitimate and explicitly supported:

  Some situations don't need the /docflow pipeline (one-off text inspection,
  quick metadata probe, a tool /docflow genuinely can't handle). In those
  cases, unlock and proceed:

    touch .state/docflow-active   # unlock (persists until removed)
    <your command>
    rm    .state/docflow-active   # re-lock when finished

  The /docflow scripts themselves self-manage this marker — users only set it
  for ad-hoc manual work. If you find yourself repeatedly overriding for the
  SAME workflow, report it as a /docflow gap so the pipeline can handle it.
EOF
    exit 2
fi

exit 0
