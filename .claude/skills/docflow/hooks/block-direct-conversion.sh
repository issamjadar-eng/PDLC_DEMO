#!/usr/bin/env bash
# =============================================================================
# block-direct-conversion.sh — PreToolUse Bash tripwire for /docflow
#
# Denies direct calls to document-conversion tools (pandoc, libreoffice/soffice,
# pdftotext, pdfimages, pdftoppm, unzip, qpdf, pdftk) when they target office
# documents (.docx/.doc/.xlsx/.xls/.pptx/.pdf). All DOCX/PDF/XLSX <-> markdown
# conversion must go through the /docflow skill — its agents set an active-state
# marker that bypasses this hook while they run.
#
# v3 (task 082) — Shell-aware tokenization via python3 shlex, so prose inside
# quoted arguments to OTHER commands no longer trips the verb/extension match.
# Root cause of v2 false-positive: sed-based statement splitting ignored quote
# boundaries, so `gh pr create --body "... pandoc | unzip | ... .docx ..."`
# was (wrongly) split as if the pipes were real shell pipes.
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

DECISION="$(python3 - "$CMD" <<'PY'
import re
import shlex
import sys

cmd = sys.argv[1]
VERBS = {
    "pandoc", "soffice", "libreoffice", "pdftotext",
    "pdfimages", "pdftoppm", "unzip", "qpdf", "pdftk",
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
)"

if [ "$DECISION" = "deny" ]; then
    cat >&2 <<'EOF'
[docflow] Direct document conversion is disabled — route through /docflow.

  • /docflow adopt <target>      DHF formal DOCX → round-trippable working MD
  • /docflow convert <doc-id>    Internal QMS source → source-md
  • /docflow import <file>       External DOCX/PDF → project MD (Phase 2)
  • /docflow refresh <doc-id>    Update an already-converted source-md

Why: /docflow owns image extraction, frontmatter, cross-reference resolution,
     quality gates, and round-trip metadata. Direct pandoc/unzip/soffice calls
     silently drop colors, images, structure, and round-trip fidelity.

If /docflow truly cannot handle the case (e.g., a colored risk matrix that
needs manual structural preservation), report the gap — do not bypass silently.

Explicit override (use sparingly):
  touch .state/docflow-active   # unlock this session
  rm    .state/docflow-active   # re-lock when finished
EOF
    exit 2
fi

exit 0
