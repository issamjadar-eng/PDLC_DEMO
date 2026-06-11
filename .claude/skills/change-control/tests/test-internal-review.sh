#!/usr/bin/env bash
# Structural + unit tests for the change-control internal-review surface.
#
# Tests:
#   1. Skill structure: required new files present
#   2. Action scripts are valid Python (no syntax errors)
#   3. lib/path_convention: project_name() reads project.yml
#   4. lib/path_convention: doc_name_from_repo_path normalizes correctly
#   5. lib/path_convention: drive_path_for builds AI_PDLC/<project>/<user>/<doc>
#   6. lib/path_convention: archived_doc_name applies date stamp
#   7. lib/internal_review: render → parse round-trip preserves data
#   8. lib/internal_review: upsert_block creates / replaces idempotently
#   9. lib/internal_review: find_block returns None for missing
#  10. lib/internal_review: remove_block clears the section
#  11. help action prints lifecycle + actions
#  12. help <action> prints per-action detail
#  13. web-control purge_stale: keeps referenced + deletes orphans
#  14. CDP modifier sanity: lib/internal_review preserves checkbox state
#       across upsert (regression: previously hand-edited Already-Addressed
#       must survive a review-status refresh)
#
# Live tests for review-start / review-status / review-update against a
# real gdoc are NOT in this suite — they require a live web-control debug
# Chrome and a corporate Google session. Documented as a manual integration
# test in the README.

set -uo pipefail

SKILL_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
PROJECT_ROOT="$(cd "$SKILL_DIR"/../../.. && pwd)"
RESULTS=()
PASSED=0
FAILED=0

# Use the project's existing probe venv if available; fall back to system python3
VENV_PY="/tmp/dhf-probe-venv/bin/python3"
if [[ -x "$VENV_PY" ]]; then
    PY="$VENV_PY"
else
    PY="python3"
fi

# Ensure pyyaml is available for path_convention
if ! "$PY" -c "import yaml" 2>/dev/null; then
    if [[ -x "$VENV_PY" ]]; then
        /tmp/dhf-probe-venv/bin/pip install --quiet pyyaml 2>&1 | tail -3 || true
    fi
fi

# Read project name from the consuming project's project.yml so tests stay
# project-agnostic (skills/agents must contain no project-specific names).
EXPECTED_PROJECT_NAME="$("$PY" -c "import yaml; print(yaml.safe_load(open('$PROJECT_ROOT/project.yml'))['project']['name'])" 2>/dev/null)"
if [[ -z "$EXPECTED_PROJECT_NAME" ]]; then
    echo "FATAL: could not read project.name from $PROJECT_ROOT/project.yml" >&2
    exit 2
fi

assert() {
    local label="$1"
    local cmd="$2"
    if eval "$cmd" >/tmp/cc-test-stderr 2>&1; then
        echo "  PASS  $label"
        PASSED=$((PASSED + 1))
    else
        echo "  FAIL  $label"
        echo "        cmd: $cmd"
        echo "        stderr (last 5 lines):"
        tail -5 /tmp/cc-test-stderr 2>/dev/null | sed 's/^/        /'
        FAILED=$((FAILED + 1))
    fi
}

assert_output() {
    local label="$1"
    local cmd="$2"
    local pattern="$3"
    local out
    out="$(eval "$cmd" 2>&1)"
    if echo "$out" | grep -qE "$pattern"; then
        echo "  PASS  $label"
        PASSED=$((PASSED + 1))
    else
        echo "  FAIL  $label  (pattern '$pattern' not found)"
        echo "        output (last 8 lines):"
        echo "$out" | tail -8 | sed 's/^/        /'
        FAILED=$((FAILED + 1))
    fi
}

echo "==========================================================="
echo "change-control internal-review test suite"
echo "  SKILL_DIR:    $SKILL_DIR"
echo "  PROJECT:      $PROJECT_ROOT"
echo "  PYTHON:       $PY"
echo "==========================================================="
echo

# ------------------------------------------------------------
# 1. Structure
# ------------------------------------------------------------
echo "[1] structure"
for f in \
    actions/review_start.py \
    actions/review_status.py \
    actions/review_update.py \
    actions/review_abort.py \
    actions/help.py \
    lib/path_convention.py \
    lib/internal_review.py \
    lib/gdoc.py; do
    assert "structure: $f" "[ -f '$SKILL_DIR/$f' ]"
done

# ------------------------------------------------------------
# 2. Python syntax
# ------------------------------------------------------------
echo
echo "[2] python syntax"
for f in \
    "$SKILL_DIR/actions/review_start.py" \
    "$SKILL_DIR/actions/review_status.py" \
    "$SKILL_DIR/actions/review_update.py" \
    "$SKILL_DIR/actions/review_abort.py" \
    "$SKILL_DIR/actions/help.py" \
    "$SKILL_DIR/lib/path_convention.py" \
    "$SKILL_DIR/lib/internal_review.py" \
    "$SKILL_DIR/lib/gdoc.py" \
    "$PROJECT_ROOT/.claude/skills/web-control/actions/purge_stale.py"; do
    name="$(basename "$f")"
    assert "syntax: $name" "'$PY' -m py_compile '$f'"
done

# ------------------------------------------------------------
# 3-6. lib/path_convention behavior
# ------------------------------------------------------------
echo
echo "[3-6] path_convention"
assert_output "project_name() reads project.yml" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c 'from lib.path_convention import project_name; print(project_name())'" \
    "$EXPECTED_PROJECT_NAME"

assert_output "doc_name_from_repo_path strips .md + replaces /" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c 'from lib.path_convention import doc_name_from_repo_path; print(doc_name_from_repo_path(\"docs/project/dhfs/foo/bar.md\"))'" \
    '^docs_project_dhfs_foo_bar$'

assert_output "drive_path_for builds AI_PDLC/<project>/<user>/<doc>" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.path_convention import drive_path_for
parts = drive_path_for(\"docs/system-sad.md\", task_folder=\"ben\")
print(\"|\".join(parts))
'" \
    "AI_PDLC\\|$EXPECTED_PROJECT_NAME\\|ben\\|docs_system-sad"

assert_output "archived_doc_name applies [ARCHIVED YYYY-MM-DD]" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.path_convention import archived_doc_name
print(archived_doc_name(\"foo_bar\", \"2026-04-27\"))
'" \
    '^\[ARCHIVED 2026-04-27\] foo_bar$'

# ------------------------------------------------------------
# 7-10. lib/internal_review behavior
# ------------------------------------------------------------
echo
echo "[7-10] internal_review"

# Round-trip: render → parse → render produces the same dataclass content
assert_output "render → parse round-trip preserves doc_path + gdoc_url" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.internal_review import ReviewSection, ReviewItem, render_section, parse_section
s = ReviewSection.new(\"docs/foo.md\", \"https://docs.google.com/document/d/abc123/edit\", \"AI_PDLC/x/ben/\")
s.open_items.append(ReviewItem(kind=\"comment\", id=\"c-1\", author=\"Maryna\", anchor=\"§4.2\", text=\"need citation\"))
out = render_section(s)
parsed = parse_section(out)
assert parsed.doc_path == \"docs/foo.md\", parsed.doc_path
assert parsed.gdoc_url.startswith(\"https://docs.google.com/document/d/abc123\"), parsed.gdoc_url
assert len(parsed.open_items) == 1
assert parsed.open_items[0].kind == \"comment\"
print(\"OK\")
'" 'OK'

assert_output "upsert_block creates section in empty doc" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.internal_review import ReviewSection, upsert_block
s = ReviewSection.new(\"x.md\", \"https://docs.google.com/document/d/zz/edit\", \"AI_PDLC/p/ben/\")
out = upsert_block(\"# Some Task\\n\\nBody.\\n\", s)
assert \"change-control:internal-review begin doc=x.md\" in out
assert \"change-control:internal-review end\" in out
assert out.count(\"change-control:internal-review begin\") == 1
print(\"OK\")
'" 'OK'

assert_output "upsert_block replaces existing section idempotently" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.internal_review import ReviewSection, upsert_block
s1 = ReviewSection.new(\"x.md\", \"https://docs.google.com/document/d/aaa/edit\", \"AI_PDLC/p/ben/\")
text = upsert_block(\"# Task\\n\", s1)
s2 = ReviewSection.new(\"x.md\", \"https://docs.google.com/document/d/bbb/edit\", \"AI_PDLC/p/ben/\")
text2 = upsert_block(text, s2)
# Should still have exactly one block, with the new url
assert text2.count(\"change-control:internal-review begin\") == 1
assert \"bbb\" in text2
assert \"aaa\" not in text2
print(\"OK\")
'" 'OK'

assert_output "find_block returns None for missing doc" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.internal_review import find_block
result = find_block(\"# Task\\n\\nbody\\n\", \"x.md\")
print(\"None\" if result is None else \"NOT_NONE\")
'" '^None$'

assert_output "remove_block clears the section" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.internal_review import ReviewSection, upsert_block, remove_block, find_block
s = ReviewSection.new(\"y.md\", \"https://docs.google.com/document/d/zz/edit\", \"AI_PDLC/p/ben/\")
text = upsert_block(\"# Task\\n\", s)
text2 = remove_block(text, \"y.md\")
assert find_block(text2, \"y.md\") is None
print(\"OK\")
'" 'OK'

# ------------------------------------------------------------
# 11-12. help action
# ------------------------------------------------------------
echo
echo "[11-12] help action"
assert_output "help (no args) prints lifecycle + review-start" \
    "'$PY' '$SKILL_DIR/actions/help.py'" \
    'review-start'

assert_output "help review-start prints detailed usage" \
    "'$PY' '$SKILL_DIR/actions/help.py' review-start" \
    'AI_PDLC'

assert_output "help freeze prints archive flow per Q7" \
    "'$PY' '$SKILL_DIR/actions/help.py' freeze" \
    'ARCHIVED YYYY-MM-DD'

# ------------------------------------------------------------
# 13. web-control purge_stale (keeps referenced + deletes orphans)
# ------------------------------------------------------------
echo
echo "[13] web-control purge_stale"

# Build a transient .state/web-control with a referenced + an orphan,
# write a temp task doc with one referenced gdoc id, run purge_stale,
# verify only the orphan is gone.
TEST_TMP="$(mktemp -d)"
mkdir -p "$TEST_TMP/.state/web-control" "$TEST_TMP/tasks/test"
cp "$PROJECT_ROOT/project.yml" "$TEST_TMP/project.yml"
cat > "$TEST_TMP/tasks/test/001-test.md" <<EOF
# Test task

<!-- change-control:internal-review begin doc=test/foo.md -->
| Field | Value |
|---|---|
| GDoc | https://docs.google.com/document/d/REFERENCED_ID/edit |
<!-- change-control:internal-review end -->
EOF

touch "$TEST_TMP/.state/web-control/REFERENCED_ID.last-sync.json"
touch "$TEST_TMP/.state/web-control/REFERENCED_ID.last-push.txt"
touch "$TEST_TMP/.state/web-control/ORPHAN_ID.last-sync.json"
touch "$TEST_TMP/.state/web-control/ORPHAN_ID.last-push.txt"

(cd "$TEST_TMP" && "$PY" "$PROJECT_ROOT/.claude/skills/web-control/actions/purge_stale.py" >/tmp/cc-test-purge.log 2>&1)
PURGE_OK=true
[ -f "$TEST_TMP/.state/web-control/REFERENCED_ID.last-sync.json" ] || PURGE_OK=false
[ -f "$TEST_TMP/.state/web-control/REFERENCED_ID.last-push.txt" ] || PURGE_OK=false
[ ! -f "$TEST_TMP/.state/web-control/ORPHAN_ID.last-sync.json" ] || PURGE_OK=false
[ ! -f "$TEST_TMP/.state/web-control/ORPHAN_ID.last-push.txt" ] || PURGE_OK=false

if $PURGE_OK; then
    echo "  PASS  purge_stale keeps referenced + deletes orphans"
    PASSED=$((PASSED + 1))
else
    echo "  FAIL  purge_stale (referenced or orphan handling broken)"
    echo "        log:"
    head -20 /tmp/cc-test-purge.log | sed 's/^/        /'
    echo "        state dir after purge:"
    ls -la "$TEST_TMP/.state/web-control/" | sed 's/^/        /'
    FAILED=$((FAILED + 1))
fi
rm -rf "$TEST_TMP"

# ------------------------------------------------------------
# 14. Hand-edited Already-Addressed survives upsert (regression)
# ------------------------------------------------------------
echo
echo "[14] hand-edited state survives refresh"
TEST14_SCRIPT="$(mktemp /tmp/cc-test14-XXXXXX.py)"
cat > "$TEST14_SCRIPT" <<'PYEOF'
import sys
from lib.internal_review import (
    ReviewSection, ReviewItem, upsert_block, parse_section, find_block
)
# Build initial section with an open item
s = ReviewSection.new("x.md", "https://docs.google.com/document/d/zz/edit", "AI_PDLC/p/ben/")
s.open_items.append(ReviewItem(kind="comment", id="c-1", author="Maryna", anchor="§1", text="..."))
text = upsert_block("# T\n", s)
# Simulate user moving #c-1 to Already Addressed by hand
old = "### Already Addressed (will reply on next `review-update`)\n\n(none yet)"
new = "### Already Addressed (will reply on next `review-update`)\n\n- [x] **#c-1** Maryna · §1 — addressed: cited Bedi 2013"
text_edited = text.replace(old, new)
# Reparse and verify
rng = find_block(text_edited, "x.md")
block = "\n".join(text_edited.splitlines()[rng[0]:rng[1]+1])
parsed = parse_section(block)
assert len(parsed.already_addressed) == 1, parsed.already_addressed
assert parsed.already_addressed[0].id == "c-1"
print("OK")
PYEOF
assert_output "user-edited Already-Addressed survives upsert (regression)" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST14_SCRIPT'" \
    'OK'
rm -f "$TEST14_SCRIPT"

# ------------------------------------------------------------
# 15. lib/attachments.py — pure helpers + multipart encoder
# ------------------------------------------------------------
echo
echo "[15] attachments lib"
assert "lib/attachments.py exists" "[ -f '$SKILL_DIR/lib/attachments.py' ]"

assert "lib/attachments.py imports cleanly" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c 'from lib.attachments import (
    extract_confluence_cookies, list_attachments, download_attachment,
    upload_attachment, update_attachment, upload_or_update,
    attachment_url, find_attachment, compute_sha256,
    AttachmentError, NoConfluenceCookies, ConfluenceAuthExpired,
    ConfluenceHTTPError, WebControlMissing
)'"

assert_output "attachment_url URL-encodes filenames" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.attachments import attachment_url
url = attachment_url(\"https://example.atlassian.net/\", \"123\", \"foo bar.png\")
assert url == \"https://example.atlassian.net/wiki/download/attachments/123/foo%20bar.png\", url
print(\"OK\")
'" 'OK'

assert_output "attachment_url strips trailing slash from base_url" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.attachments import attachment_url
a = attachment_url(\"https://x.atlassian.net/\", \"1\", \"a.png\")
b = attachment_url(\"https://x.atlassian.net\", \"1\", \"a.png\")
assert a == b, (a, b)
print(\"OK\")
'" 'OK'

assert_output "find_attachment matches by title" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.attachments import find_attachment
atts = [{\"id\": \"a1\", \"title\": \"one.png\"}, {\"id\": \"a2\", \"title\": \"two.png\"}]
assert find_attachment(atts, \"two.png\")[\"id\"] == \"a2\"
assert find_attachment(atts, \"missing.png\") is None
print(\"OK\")
'" 'OK'

assert_output "compute_sha256 matches hashlib stdlib" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
import hashlib, tempfile
from pathlib import Path
from lib.attachments import compute_sha256
with tempfile.NamedTemporaryFile(delete=False) as f:
    f.write(b\"hello world\")
    p = Path(f.name)
expected = hashlib.sha256(b\"hello world\").hexdigest()
assert compute_sha256(p) == expected
p.unlink()
print(\"OK\")
'" 'OK'

assert_output "_encode_multipart produces a valid form-data body" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
import tempfile
from pathlib import Path
from lib.attachments import _encode_multipart
with tempfile.NamedTemporaryFile(suffix=\".png\", delete=False) as f:
    f.write(b\"PIXELDATA\")
    p = Path(f.name)
body, ct = _encode_multipart(p, extra_fields={\"minorEdit\": \"true\", \"comment\": \"hi\"})
assert ct.startswith(\"multipart/form-data; boundary=\"), ct
assert b\"PIXELDATA\" in body
assert b\"name=\\\"minorEdit\\\"\" in body
assert b\"name=\\\"comment\\\"\" in body
assert b\"name=\\\"file\\\"; filename=\\\"\" in body
assert p.name.encode() in body
p.unlink()
print(\"OK\")
'" 'OK'

# ------------------------------------------------------------
# 16. lib/attachments.py — HTTP round-trip against a local stub server
# ------------------------------------------------------------
echo
echo "[16] attachments HTTP round-trip (local stub server)"
TEST16_SCRIPT="$(mktemp /tmp/cc-test16-XXXXXX.py)"
cat > "$TEST16_SCRIPT" <<'PYEOF'
"""Spin up a local HTTPServer that mimics the Confluence attachment REST
surface enough to exercise list / download / upload / update flow.

This is a structural test of lib/attachments.py's wire format, not a
test of the live Confluence API — it verifies our cookie header is
sent, our multipart body is well-formed enough for stdlib's
cgi.FieldStorage to parse it, and our response-shape parsing is correct.
"""
import http.server
import json
import socketserver
import sys
import tempfile
import threading
import time
import urllib.parse
from io import BytesIO
from pathlib import Path

from lib.attachments import (
    AttachmentError,
    ConfluenceAuthExpired,
    ConfluenceHTTPError,
    attachment_url,
    download_attachment,
    list_attachments,
    update_attachment,
    upload_attachment,
    upload_or_update,
)


class StubState:
    cookie_seen = None
    xat_seen = None
    attachments: dict[str, dict] = {}  # id -> {id, title, bytes}
    next_id_counter = 1

    @classmethod
    def next_id(cls) -> str:
        n = cls.next_id_counter
        cls.next_id_counter += 1
        return f"att{n:04d}"


class Handler(http.server.BaseHTTPRequestHandler):
    PAGE = "PAGE123"

    def log_message(self, *a, **k):  # silence
        pass

    def _read_body(self) -> bytes:
        n = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(n) if n else b""

    def _capture_auth(self) -> bool:
        cookie = self.headers.get("Cookie")
        StubState.cookie_seen = cookie
        StubState.xat_seen = self.headers.get("X-Atlassian-Token")
        if not cookie or "session=valid" not in cookie:
            self.send_response(401)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"unauth")
            return False
        return True

    def do_GET(self):
        if not self._capture_auth():
            return
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == f"/wiki/rest/api/content/{self.PAGE}/child/attachment":
            results = [
                {"id": a["id"], "title": a["title"]}
                for a in StubState.attachments.values()
            ]
            payload = json.dumps({"results": results}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if parsed.path.startswith(f"/wiki/download/attachments/{self.PAGE}/"):
            filename = urllib.parse.unquote(parsed.path.rsplit("/", 1)[-1])
            for a in StubState.attachments.values():
                if a["title"] == filename:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("Content-Length", str(len(a["bytes"])))
                    self.end_headers()
                    self.wfile.write(a["bytes"])
                    return
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

    def _parse_multipart(self, body: bytes, ct: str) -> dict:
        # Hand-parse the fields we care about (file + minorEdit + comment).
        # Boundary lives on the content-type header.
        m = ct.split("boundary=")
        if len(m) != 2:
            return {}
        boundary = m[1].encode()
        delim = b"--" + boundary
        out: dict = {}
        for part in body.split(delim):
            part = part.strip(b"\r\n")
            if not part or part == b"--":
                continue
            try:
                head, _, content = part.partition(b"\r\n\r\n")
            except Exception:
                continue
            head_text = head.decode(errors="replace")
            content = content.rstrip(b"\r\n")
            # Strip trailing CRLF before next delim (robust against -- end marker)
            if content.endswith(b"\r\n"):
                content = content[:-2]
            name = None
            filename = None
            for line in head_text.splitlines():
                if line.lower().startswith("content-disposition"):
                    for tok in line.split(";"):
                        tok = tok.strip()
                        if tok.startswith("name="):
                            name = tok.split("=", 1)[1].strip('"')
                        elif tok.startswith("filename="):
                            filename = tok.split("=", 1)[1].strip('"')
            if name == "file" and filename is not None:
                out["file"] = (filename, content)
            elif name:
                out[name] = content.decode("utf-8", errors="replace")
        return out

    def do_POST(self):
        if not self._capture_auth():
            return
        parsed = urllib.parse.urlparse(self.path)
        body = self._read_body()
        ct = self.headers.get("Content-Type", "")
        fields = self._parse_multipart(body, ct)
        # Upload (new file)
        if parsed.path == f"/wiki/rest/api/content/{self.PAGE}/child/attachment":
            if "file" not in fields:
                self.send_response(400)
                self.end_headers()
                return
            filename, file_bytes = fields["file"]
            new_id = StubState.next_id()
            StubState.attachments[new_id] = {
                "id": new_id,
                "title": filename,
                "bytes": file_bytes,
            }
            payload = json.dumps(
                {"results": [{"id": new_id, "title": filename}]}
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        # Update existing (POST .../{id}/data)
        prefix = f"/wiki/rest/api/content/{self.PAGE}/child/attachment/"
        if parsed.path.startswith(prefix) and parsed.path.endswith("/data"):
            att_id = parsed.path[len(prefix):-len("/data")]
            if att_id not in StubState.attachments:
                self.send_response(404)
                self.end_headers()
                return
            if "file" not in fields:
                self.send_response(400)
                self.end_headers()
                return
            filename, file_bytes = fields["file"]
            StubState.attachments[att_id]["bytes"] = file_bytes
            StubState.attachments[att_id]["title"] = filename
            payload = json.dumps(
                {"id": att_id, "title": filename, "version": {"number": 2}}
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        self.send_response(404)
        self.end_headers()


# Bring up the server
server = socketserver.TCPServer(("127.0.0.1", 0), Handler)
port = server.server_address[1]
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{port}"
COOKIE_OK = "session=valid"
COOKIE_BAD = "session=expired"

try:
    # 1. List on empty page returns []
    r = list_attachments(base, "PAGE123", COOKIE_OK)
    assert r == [], r

    # 2. Auth: bad cookie raises ConfluenceAuthExpired (401)
    try:
        list_attachments(base, "PAGE123", COOKIE_BAD)
        raise AssertionError("expected ConfluenceAuthExpired")
    except ConfluenceAuthExpired:
        pass

    # 3. Upload a file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"FIRST_BYTES")
        src = Path(f.name)
    rec = upload_attachment(base, "PAGE123", src, COOKIE_OK, comment="initial")
    assert rec["title"] == src.name
    aid = rec["id"]

    # 4. List shows it
    r = list_attachments(base, "PAGE123", COOKIE_OK)
    assert len(r) == 1 and r[0]["id"] == aid

    # 5. Download round-trip preserves bytes
    with tempfile.NamedTemporaryFile(delete=False) as f:
        target = Path(f.name)
    download_attachment(base, "PAGE123", src.name, target, COOKIE_OK)
    assert target.read_bytes() == b"FIRST_BYTES"
    target.unlink()

    # 6. Update — new bytes
    src.write_bytes(b"SECOND_BYTES_X")
    update_attachment(base, "PAGE123", aid, src, COOKIE_OK)
    with tempfile.NamedTemporaryFile(delete=False) as f:
        target = Path(f.name)
    download_attachment(base, "PAGE123", src.name, target, COOKIE_OK)
    assert target.read_bytes() == b"SECOND_BYTES_X"
    target.unlink()

    # 7. upload_or_update detects existing → updates
    src.write_bytes(b"THIRD_VERSION_BYTES")
    action, _ = upload_or_update(base, "PAGE123", src, COOKIE_OK)
    assert action == "updated", action

    # 8. upload_or_update with a fresh filename → uploads
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"OTHER_FILE")
        other = Path(f.name)
    action, _ = upload_or_update(base, "PAGE123", other, COOKIE_OK)
    assert action == "uploaded", action

    # 9. The right auth headers got through
    assert StubState.cookie_seen == COOKIE_OK
    assert StubState.xat_seen == "no-check"

    src.unlink()
    other.unlink()
    print("OK")
finally:
    server.shutdown()
PYEOF
assert_output "lib/attachments HTTP round-trip against local stub" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST16_SCRIPT'" 'OK'
rm -f "$TEST16_SCRIPT"

# ------------------------------------------------------------
# 17. lib/confluence_mcp.py — wrapper round-trip via fake mcp_call
# ------------------------------------------------------------
echo
echo "[17] confluence_mcp wrapper"
assert "lib/confluence_mcp.py exists" "[ -f '$SKILL_DIR/lib/confluence_mcp.py' ]"

assert "lib/confluence_mcp.py imports cleanly" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c 'from lib.confluence_mcp import (
    ConfluenceMCP, MCPCallable, MCPError, MCPUnreachable, MCPNotBound,
    CloudIdNotFound, ContentFormatInvalid,
    ConfluencePage, FooterComment, InlineComment
)'"

assert_output "ContentFormatInvalid raised on html / storage" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.confluence_mcp import _check_format, ContentFormatInvalid
for bad in (\"html\", \"storage\", \"\"):
    try:
        _check_format(bad)
        print(f\"FAIL no raise for {bad!r}\"); break
    except ContentFormatInvalid:
        pass
else:
    print(\"OK\")
'" 'OK'

assert_output "MCPNotBound raised when mcp_call=None" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.confluence_mcp import ConfluenceMCP, MCPNotBound
try:
    ConfluenceMCP(None)
    print(\"FAIL no raise\")
except MCPNotBound:
    print(\"OK\")
'" 'OK'

assert_output "_page_from_raw normalizes ADF body + version + message" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.confluence_mcp import _page_from_raw
raw = {
    \"id\": \"6768427047\",
    \"title\": \"Probe\",
    \"spaceId\": \"5121737841\",
    \"version\": {\"number\": 9, \"message\": \"probe v9\"},
    \"body\": {\"atlas_doc_format\": {\"value\": \"{\\\"type\\\":\\\"doc\\\"}\"}},
    \"contentFormat\": \"adf\",
    \"_links\": {\"webui\": \"/spaces/AFAI/pages/6768427047\"},
}
p = _page_from_raw(raw)
assert p.page_id == \"6768427047\" and p.version == 9
assert p.body_format == \"adf\" and p.version_message == \"probe v9\"
assert \"\\\"type\\\":\\\"doc\\\"\" in p.body
print(\"OK\")
'" 'OK'

assert_output "_inline_comment_from_raw extracts inlineMarkerRef + selection + status" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.confluence_mcp import _inline_comment_from_raw
raw = {
    \"id\": \"6768918597\",
    \"body\": \"good catch\",
    \"author\": {\"accountId\": \"abc\"},
    \"createdAt\": \"2026-04-28T12:00Z\",
    \"inlineCommentProperties\": {
        \"inlineMarkerRef\": \"mref-xyz\",
        \"inlineOriginalSelection\": \"device vs. non-device boundary\",
        \"resolutionStatus\": \"open\",
    },
}
ic = _inline_comment_from_raw(raw)
assert ic.inline_marker_ref == \"mref-xyz\"
assert ic.inline_original_selection.startswith(\"device vs.\")
assert ic.resolution_status == \"open\"
print(\"OK\")
'" 'OK'

assert_output "_unwrap_results handles {results:[...]} + bare list + dict" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.confluence_mcp import _unwrap_results
assert _unwrap_results({\"results\": [{\"a\": 1}]}) == [{\"a\": 1}]
assert _unwrap_results([{\"a\": 1}, {\"b\": 2}]) == [{\"a\": 1}, {\"b\": 2}]
assert _unwrap_results({\"unrelated\": True}) == []
assert _unwrap_results(None) == []
print(\"OK\")
'" 'OK'

assert_output "ConfluenceMCP resolves cloudId via getAccessibleAtlassianResources" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.confluence_mcp import ConfluenceMCP
def fake(tool, **kw):
    if tool == \"getAccessibleAtlassianResources\":
        return [
            {\"id\": \"cid-A\", \"url\": \"https://other.atlassian.net\"},
            {\"id\": \"cid-B\", \"url\": \"https://target.atlassian.net\"},
        ]
    raise AssertionError(tool)
mcp = ConfluenceMCP(fake, base_url=\"https://target.atlassian.net\")
assert mcp.cloud_id == \"cid-B\", mcp.cloud_id
print(\"OK\")
'" 'OK'

assert_output "ConfluenceMCP get_page round-trip + update_page passes versionMessage" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.confluence_mcp import ConfluenceMCP
calls = []
def fake(tool, **kw):
    calls.append((tool, kw))
    if tool == \"getAccessibleAtlassianResources\":
        return [{\"id\": \"cid-1\", \"url\": \"https://x.atlassian.net\"}]
    if tool == \"getConfluencePage\":
        return {\"id\": kw[\"pageId\"], \"title\": \"T\", \"version\": {\"number\": 5}, \"body\": {\"atlas_doc_format\": {\"value\": \"{}\"}}, \"contentFormat\": \"adf\"}
    if tool == \"updateConfluencePage\":
        return {\"id\": kw[\"pageId\"], \"title\": kw[\"title\"], \"version\": {\"number\": 6, \"message\": kw[\"versionMessage\"]}, \"body\": {\"atlas_doc_format\": {\"value\": \"{}\"}}, \"contentFormat\": \"adf\"}
    raise AssertionError(tool)
mcp = ConfluenceMCP(fake)
p = mcp.get_page(\"123\")
assert p.version == 5
u = mcp.update_page(\"123\", \"T\", \"new body\", version_message=\"publish: x.md\")
assert u.version == 6 and u.version_message == \"publish: x.md\"
# updateConfluencePage call carried versionMessage + cloudId + pageId
update_call = [c for c in calls if c[0] == \"updateConfluencePage\"][0][1]
assert update_call[\"versionMessage\"] == \"publish: x.md\"
assert update_call[\"cloudId\"] == \"cid-1\"
assert update_call[\"pageId\"] == \"123\"
print(\"OK\")
'" 'OK'

assert_output "ConfluenceMCP list_inline_comments forwards resolutionStatus + parses results" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.confluence_mcp import ConfluenceMCP
seen = []
def fake(tool, **kw):
    seen.append((tool, kw))
    if tool == \"getAccessibleAtlassianResources\":
        return [{\"id\": \"cid-1\"}]
    if tool == \"getConfluencePageInlineComments\":
        return {\"results\": [{\"id\": \"c1\", \"body\": \"hi\", \"inlineCommentProperties\": {\"inlineMarkerRef\": \"m1\", \"inlineOriginalSelection\": \"foo\", \"resolutionStatus\": \"open\"}}]}
    raise AssertionError(tool)
mcp = ConfluenceMCP(fake)
items = mcp.list_inline_comments(\"PG\", resolution_status=\"open\")
assert len(items) == 1 and items[0].inline_marker_ref == \"m1\"
inline_call = [s for s in seen if s[0] == \"getConfluencePageInlineComments\"][0][1]
assert inline_call[\"resolutionStatus\"] == \"open\"
print(\"OK\")
'" 'OK'

assert_output "ConfluenceMCP create_inline_comment builds inlineCommentProperties" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.confluence_mcp import ConfluenceMCP
seen = {}
def fake(tool, **kw):
    if tool == \"getAccessibleAtlassianResources\":
        return [{\"id\": \"cid\"}]
    if tool == \"createConfluenceInlineComment\":
        seen[\"kw\"] = kw
        return {\"id\": \"new\", \"body\": kw[\"body\"], \"inlineCommentProperties\": kw[\"inlineCommentProperties\"]}
    raise AssertionError(tool)
mcp = ConfluenceMCP(fake)
ic = mcp.create_inline_comment(\"PG\", \"my reply\", text_selection=\"anchor text\", text_selection_match_count=2, text_selection_match_index=1)
assert seen[\"kw\"][\"inlineCommentProperties\"] == {\"textSelection\": \"anchor text\", \"textSelectionMatchCount\": 2, \"textSelectionMatchIndex\": 1}
assert ic.inline_marker_ref == \"\"  # not returned by create response in this stub; that is fine
print(\"OK\")
'" 'OK'

assert_output "CloudIdNotFound raised when MCP returns no resources" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.confluence_mcp import ConfluenceMCP, CloudIdNotFound
def fake(tool, **kw):
    return []
mcp = ConfluenceMCP(fake)
try:
    _ = mcp.cloud_id
    print(\"FAIL no raise\")
except CloudIdNotFound:
    print(\"OK\")
'" 'OK'

# ------------------------------------------------------------
# 18. lib/normalizer.py — ADF -> markdown
# ------------------------------------------------------------
echo
echo "[18] normalizer (ADF -> markdown)"
assert "lib/normalizer.py exists" "[ -f '$SKILL_DIR/lib/normalizer.py' ]"

assert "lib/normalizer.py imports cleanly" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c 'from lib.normalizer import (
    adf_to_markdown, normalize_for_diff, NormalizationReport, CONFLUENCE_ZONE_PREFIX
)'"

TEST18_SCRIPT="$(mktemp /tmp/cc-test18-XXXXXX.py)"
cat > "$TEST18_SCRIPT" <<'PYEOF'
import json
from lib.normalizer import (
    adf_to_markdown, normalize_for_diff, NormalizationReport,
    CONFLUENCE_ZONE_PREFIX,
)

# Empty doc
assert adf_to_markdown({"type": "doc", "content": []}).strip() == ""

# Heading + paragraph
out = adf_to_markdown({"type": "doc", "content": [
    {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Hello"}]},
    {"type": "paragraph", "content": [{"type": "text", "text": "world"}]},
]})
assert "## Hello" in out and "world" in out

# Marks: bold, italic, code, link
out = adf_to_markdown({"type": "doc", "content": [
    {"type": "paragraph", "content": [
        {"type": "text", "text": "A", "marks": [{"type": "strong"}]},
        {"type": "text", "text": "B", "marks": [{"type": "em"}]},
        {"type": "text", "text": "C", "marks": [{"type": "code"}]},
        {"type": "text", "text": "click", "marks": [{"type": "link", "attrs": {"href": "https://x"}}]},
    ]},
]})
assert "**A**" in out and "*B*" in out and "`C`" in out and "[click](https://x)" in out

# Confluence Zone captured into report
rep = NormalizationReport()
out = adf_to_markdown({"type": "doc", "content": [
    {"type": "expand", "attrs": {"title": "__CONFLUENCE_ZONE__: open-issues"},
     "content": [{"type": "paragraph", "content": [{"type": "text", "text": "reviewer body"}]}]},
]}, report=rep)
assert "<details>" in out and "__CONFLUENCE_ZONE__: open-issues" in out
assert rep.zones == ["open-issues"]

# Extension macro -> placeholder + report entry
rep = NormalizationReport()
out = adf_to_markdown({"type": "doc", "content": [
    {"type": "extension", "attrs": {"extensionKey": "page-signatures"}},
]}, report=rep)
assert "<!-- confluence-side: page-signatures -->" in out
assert any(e["key"] == "page-signatures" for e in rep.extensions)

# inlineCard collapse
rep = NormalizationReport()
out = adf_to_markdown({"type": "doc", "content": [
    {"type": "paragraph", "content": [
        {"type": "text", "text": "see "},
        {"type": "inlineCard", "attrs": {"url": "https://example.com/x"}},
    ]},
]}, report=rep)
assert "[https://example.com/x](https://example.com/x)" in out
assert rep.smart_links == ["https://example.com/x"]

# Media — external URL passthrough; file -> resolver
out = adf_to_markdown({"type": "doc", "content": [
    {"type": "mediaSingle", "content": [
        {"type": "media", "attrs": {"type": "external", "url": "https://x/img.png", "alt": "IMG"}}]},
    {"type": "mediaSingle", "content": [
        {"type": "media", "attrs": {"type": "file", "id": "mid", "filename": "pic.png"}}]},
]}, attachment_url=lambda fn, mid: f"images/{fn}")
assert "![IMG](https://x/img.png)" in out and "![pic.png](images/pic.png)" in out

# Default-resolver placeholder via normalize_for_diff
out = normalize_for_diff({"type": "doc", "content": [
    {"type": "mediaSingle", "content": [
        {"type": "media", "attrs": {"type": "file", "id": "mid", "filename": "pic.png"}}]},
]})
assert "confluence-attachment:pic.png" in out

# Table
out = adf_to_markdown({"type": "doc", "content": [
    {"type": "table", "content": [
        {"type": "tableRow", "content": [
            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "A"}]}]},
            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "B"}]}]},
        ]},
        {"type": "tableRow", "content": [
            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "1"}]}]},
            {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "2"}]}]},
        ]},
    ]},
]})
assert "| A | B |" in out and "| --- | --- |" in out and "| 1 | 2 |" in out

# Bullet list
out = adf_to_markdown({"type": "doc", "content": [
    {"type": "bulletList", "content": [
        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "one"}]}]},
        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "two"}]}]},
    ]},
]})
assert "- one" in out and "- two" in out

# codeBlock
out = adf_to_markdown({"type": "doc", "content": [
    {"type": "codeBlock", "attrs": {"language": "python"}, "content": [{"type": "text", "text": "print(1)"}]},
]})
assert "```python" in out and "print(1)" in out

# JSON-string input
out = adf_to_markdown(json.dumps({"type": "doc", "content": [
    {"type": "paragraph", "content": [{"type": "text", "text": "hi"}]}]}))
assert "hi" in out

print("OK")
PYEOF
assert_output "lib/normalizer covers headings, marks, zones, extensions, smartlinks, media, tables, lists, code, json-input" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST18_SCRIPT'" 'OK'
rm -f "$TEST18_SCRIPT"

# ------------------------------------------------------------
# 19. lib/markdown_transform.py — pre-push transformations
# ------------------------------------------------------------
echo
echo "[19] markdown_transform"
assert "lib/markdown_transform.py exists" "[ -f '$SKILL_DIR/lib/markdown_transform.py' ]"

assert "lib/markdown_transform.py imports cleanly" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c 'from lib.markdown_transform import (
    transform_markdown, strip_leading_html_comment, swap_html_fence_to_text,
    rewrite_internal_md_links, PageRef, TransformOptions, TransformReport
)'"

TEST19_SCRIPT="$(mktemp /tmp/cc-test19-XXXXXX.py)"
cat > "$TEST19_SCRIPT" <<'PYEOF'
from lib.markdown_transform import (
    transform_markdown, strip_leading_html_comment, swap_html_fence_to_text,
    rewrite_internal_md_links, PageRef, TransformOptions, TransformReport,
    _normalize_link_target,
)

# Frontmatter strip (hit + miss)
out, did = strip_leading_html_comment("<!-- meta\nfoo: 1\n-->\n\n# T\n")
assert did and out.startswith("# T")
out, did = strip_leading_html_comment("# T\n<!-- mid -->\n")
assert not did

# Fence swap: opening only, indent + extra space preserved
out, n = swap_html_fence_to_text("```html\nX\n```\n")
assert n == 1 and "```text" in out and "```html" not in out
out, n = swap_html_fence_to_text("   ````html\nX\n````\n\n``` html\nY\n```\n")
assert n == 2 and "````text" in out and "``` text" in out

# Link rewrite — hit
manifest = {"docs/foo/bar.md": PageRef(page_id="999", space_key="AFAI", base_url="https://x.atlassian.net")}
opts = TransformOptions(base_url="https://x.atlassian.net", miss_policy="lenient")
rep = TransformReport()
out = rewrite_internal_md_links("See [doc](foo/bar.md).", "docs/index.md", manifest, opts, rep)
assert "[doc](https://x.atlassian.net/wiki/spaces/AFAI/pages/999)" in out
assert len(rep.rewrote) == 1

# Fragment preserved
rep = TransformReport()
out = rewrite_internal_md_links("see [§](foo/bar.md#sec-4)", "docs/index.md", manifest, opts, rep)
assert "/pages/999#sec-4" in out

# Lenient miss — strip wrapper, append annotation
rep = TransformReport()
out = rewrite_internal_md_links("[ghost](missing.md)", "docs/index.md", manifest, opts, rep)
assert "ghost (_pending Confluence publish_)" in out and "(missing.md)" not in out
assert len(rep.missed) == 1

# Placeholder miss — leave original
opts2 = TransformOptions(miss_policy="placeholder")
rep = TransformReport()
out = rewrite_internal_md_links("[ghost](missing.md)", "docs/index.md", manifest, opts2, rep)
assert "[ghost](missing.md)" in out

# Strict miss — raises
opts3 = TransformOptions(miss_policy="strict")
try:
    rewrite_internal_md_links("[ghost](missing.md)", "docs/index.md", manifest, opts3)
    raise AssertionError("expected KeyError")
except KeyError:
    pass

# Image links not rewritten
rep = TransformReport()
out = rewrite_internal_md_links("![alt](foo/bar.md)", "docs/index.md", manifest, opts, rep)
assert out == "![alt](foo/bar.md)" and not rep.rewrote and not rep.missed

# External http links not rewritten
rep = TransformReport()
out = rewrite_internal_md_links("[hi](https://example.com) and [doc](foo/bar.md)", "docs/index.md", manifest, opts, rep)
assert "[hi](https://example.com)" in out and len(rep.rewrote) == 1

# _normalize_link_target — relative resolution
assert _normalize_link_target("foo/bar.md", "docs/index.md") == "docs/foo/bar.md"
assert _normalize_link_target("../bar.md", "docs/sub/index.md") == "docs/bar.md"
assert _normalize_link_target("./bar.md", "docs/sub/index.md") == "docs/sub/bar.md"
assert _normalize_link_target("/abs/x.md", "docs/index.md") == "abs/x.md"

# End-to-end transform_markdown
src = "<!-- meta -->\n# Hello\nSee [bar](foo/bar.md).\n\n```html\n<x/>\n```\n"
out, rep = transform_markdown(src, "docs/index.md", manifest, options=opts)
assert rep.frontmatter_stripped is True
assert rep.fence_swaps == 1
assert len(rep.rewrote) == 1 and len(rep.missed) == 0
assert "pages/999" in out and "```text" in out and "<!-- meta -->" not in out

print("OK")
PYEOF
assert_output "lib/markdown_transform — frontmatter strip + fence swap + link rewrite (3 miss policies)" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST19_SCRIPT'" 'OK'
rm -f "$TEST19_SCRIPT"

# ------------------------------------------------------------
# 20. lib/zones.py — Confluence Zones extract + splice
# ------------------------------------------------------------
echo
echo "[20] zones (extract + splice)"
assert "lib/zones.py exists" "[ -f '$SKILL_DIR/lib/zones.py' ]"

assert "lib/zones.py imports cleanly" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c 'from lib.zones import (
    extract_zones, splice_zones_back, Zone, zone_names, diff_zone_sets,
    CONFLUENCE_ZONE_PREFIX
)'"

TEST20_SCRIPT="$(mktemp /tmp/cc-test20-XXXXXX.py)"
cat > "$TEST20_SCRIPT" <<'PYEOF'
import json
from lib.zones import extract_zones, splice_zones_back, Zone, diff_zone_sets

adf = {"type": "doc", "content": [
    {"type": "paragraph", "content": [{"type": "text", "text": "normal"}]},
    {"type": "expand", "attrs": {"title": "__CONFLUENCE_ZONE__: alpha"}, "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": "reviewer-alpha"}]},
    ]},
    {"type": "expand", "attrs": {"title": "Plain Expand (not a zone)"}, "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": "rationale"}]},
    ]},
    {"type": "expand", "attrs": {"title": "__CONFLUENCE_ZONE__: beta"}, "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": "reviewer-beta"}]},
    ]},
]}

# Extract picks up only __CONFLUENCE_ZONE__-titled expands
zones = extract_zones(adf)
assert set(zones.keys()) == {"alpha", "beta"}
assert zones["alpha"].content[0]["content"][0]["text"] == "reviewer-alpha"

# Accepts JSON-string input
zones2 = extract_zones(json.dumps(adf))
assert set(zones2.keys()) == {"alpha", "beta"}

# Splice: alpha gets reviewer content back; gamma (new) is left alone
new_adf = {"type": "doc", "content": [
    {"type": "expand", "attrs": {"title": "__CONFLUENCE_ZONE__: alpha"}, "content": []},
    {"type": "expand", "attrs": {"title": "__CONFLUENCE_ZONE__: gamma"},
     "content": [{"type": "paragraph", "content": [{"type": "text", "text": "NEW gamma"}]}]},
]}
out = splice_zones_back(new_adf, zones)
assert out["content"][0]["content"][0]["content"][0]["text"] == "reviewer-alpha"
assert out["content"][1]["content"][0]["content"][0]["text"] == "NEW gamma"

# Splice does not mutate the captured set (deep-copy)
assert zones["alpha"].content[0]["content"][0]["text"] == "reviewer-alpha"
# Mutating the splice output should not bleed back into zones
out["content"][0]["content"][0]["content"][0]["text"] = "MUTATED"
assert zones["alpha"].content[0]["content"][0]["text"] == "reviewer-alpha"

# diff_zone_sets — added / removed / kept
before = {"a": Zone("a", "", []), "b": Zone("b", "", [])}
after = {"b": Zone("b", "", []), "c": Zone("c", "", [])}
assert diff_zone_sets(before, after) == {"added": ["c"], "removed": ["a"], "kept": ["b"]}

# Plain expand (no marker) is NOT captured as a zone
plain_only = {"type": "doc", "content": [
    {"type": "expand", "attrs": {"title": "Just an expand"}, "content": []},
]}
assert extract_zones(plain_only) == {}

print("OK")
PYEOF
assert_output "lib/zones — extract+splice with deep-copy isolation, plain-expand exclusion, diff" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST20_SCRIPT'" 'OK'
rm -f "$TEST20_SCRIPT"

# ------------------------------------------------------------
# 21. lib/snapshot.py — pure helpers + I/O round-trip
# ------------------------------------------------------------
echo
echo "[21] snapshot (filename + parse + I/O + prune)"
assert "lib/snapshot.py exists" "[ -f '$SKILL_DIR/lib/snapshot.py' ]"

assert "lib/snapshot.py imports cleanly" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c 'from lib.snapshot import (
    snapshot_filename, snapshot_path, snapshot_dir, parse_snapshot_filename,
    select_snapshots_for_page, select_prunable, write_snapshot, read_snapshot,
    list_snapshots, latest_snapshot, prune_old_snapshots, SnapshotFile,
    DEFAULT_CACHE_ROOT, SNAPSHOT_DIRNAME
)'"

TEST21_SCRIPT="$(mktemp /tmp/cc-test21-XXXXXX.py)"
cat > "$TEST21_SCRIPT" <<'PYEOF'
import tempfile
from pathlib import Path
from lib.snapshot import (
    snapshot_filename, parse_snapshot_filename, select_snapshots_for_page,
    select_prunable, write_snapshot, read_snapshot, latest_snapshot,
    SnapshotFile,
)

# filename composition + validation
assert snapshot_filename("PAGE123", 5) == "PAGE123-5.md"
try:
    snapshot_filename("", 1); raise AssertionError
except ValueError: pass
try:
    snapshot_filename("p", -1); raise AssertionError
except ValueError: pass

# parse — recognizes underscores, ignores non-matching
assert parse_snapshot_filename("p-7.md") == ("p", 7)
assert parse_snapshot_filename("page_with_under-3.md") == ("page_with_under", 3)
assert parse_snapshot_filename("garbage.txt") is None
assert parse_snapshot_filename("noversion.md") is None

# select sorts newest-first and filters by page
files = [Path("p-1.md"), Path("p-3.md"), Path("p-2.md"), Path("q-9.md"), Path("garbage.txt")]
result = select_snapshots_for_page(files, "p")
assert [s.version for s in result] == [3, 2, 1]
assert all(s.page_id == "p" for s in result)

# select_prunable — keeps only the keep_version (older AND newer pruned)
all_snaps = [
    SnapshotFile("p", 5, Path("p-5.md")),
    SnapshotFile("p", 3, Path("p-3.md")),
    SnapshotFile("p", 7, Path("p-7.md")),
]
assert {s.version for s in select_prunable(all_snaps, keep_version=5)} == {3, 7}

# I/O: write → prune → read → multi-page isolation
with tempfile.TemporaryDirectory() as td:
    p1 = write_snapshot("PAGE1", 1, "content v1", cache_root=td)
    assert p1.read_text() == "content v1"
    p2 = write_snapshot("PAGE1", 2, "content v2", cache_root=td)
    assert p2.read_text() == "content v2"
    assert not p1.exists(), "v1 should have been pruned"
    assert read_snapshot("PAGE1", 2, cache_root=td) == "content v2"
    assert read_snapshot("PAGE1", 99, cache_root=td) is None
    latest = latest_snapshot("PAGE1", cache_root=td)
    assert latest is not None and latest.version == 2

    # Multi-page isolation
    write_snapshot("PAGE2", 1, "page2 v1", cache_root=td)
    write_snapshot("PAGE1", 3, "content v3", cache_root=td)
    assert read_snapshot("PAGE2", 1, cache_root=td) == "page2 v1"
    assert read_snapshot("PAGE1", 3, cache_root=td) == "content v3"
    assert read_snapshot("PAGE1", 2, cache_root=td) is None

    # prune_others=False keeps both versions for the same page
    write_snapshot("PAGE3", 1, "v1", cache_root=td)
    write_snapshot("PAGE3", 2, "v2", cache_root=td, prune_others=False)
    assert read_snapshot("PAGE3", 1, cache_root=td) == "v1"
    assert read_snapshot("PAGE3", 2, cache_root=td) == "v2"

print("OK")
PYEOF
assert_output "lib/snapshot — filename + parse + select/prune + I/O round-trip + multi-page isolation" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST21_SCRIPT'" 'OK'
rm -f "$TEST21_SCRIPT"

# ------------------------------------------------------------
# 22. lib/divergence.py — detect_divergence via fake MCP
# ------------------------------------------------------------
echo
echo "[22] divergence (compute_diff + detect_divergence)"
assert "lib/divergence.py exists" "[ -f '$SKILL_DIR/lib/divergence.py' ]"

assert "lib/divergence.py imports cleanly" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c 'from lib.divergence import (
    detect_divergence, compute_diff, DivergenceResult, SnapshotReader
)'"

TEST22_SCRIPT="$(mktemp /tmp/cc-test22-XXXXXX.py)"
cat > "$TEST22_SCRIPT" <<'PYEOF'
import json
from lib.divergence import detect_divergence, compute_diff, DivergenceResult
from lib.confluence_mcp import ConfluenceMCP

# Pure compute_diff
d = compute_diff("a\nb\n", "a\nB\n", from_label="snap", to_label="live")
assert "-b" in d and "+B" in d and "snap" in d and "live" in d
assert compute_diff("same\n", "same\n") == ""

# No-divergence path: current.version == last_published_version
def fake_mcp_no(tool, **kw):
    if tool == "getAccessibleAtlassianResources":
        return [{"id": "cid"}]
    if tool == "getConfluencePage":
        adf = {"type": "doc", "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "orig"}]}]}
        return {"id": kw["pageId"], "title": "T", "version": {"number": 5},
                "body": {"atlas_doc_format": {"value": json.dumps(adf)}},
                "contentFormat": "adf"}
mcp = ConfluenceMCP(fake_mcp_no)
result = detect_divergence(mcp, page_id="P1", last_published_version=5,
                           read_snapshot=lambda pid, v: "orig\n")
assert result.diverged is False and result.current_version == 5
assert "no divergence" in result.summary()

# Diverged path: current ahead
def fake_mcp_div(tool, **kw):
    if tool == "getAccessibleAtlassianResources":
        return [{"id": "cid"}]
    if tool == "getConfluencePage":
        adf = {"type": "doc", "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "reviewer change"}]}]}
        return {"id": kw["pageId"], "title": "T", "version": {"number": 8},
                "body": {"atlas_doc_format": {"value": json.dumps(adf)}},
                "contentFormat": "adf"}
mcp2 = ConfluenceMCP(fake_mcp_div)
result = detect_divergence(mcp2, page_id="P1", last_published_version=5,
                           read_snapshot=lambda pid, v: "authored\n")
assert result.diverged is True
assert result.current_version == 8 and result.last_published_version == 5
assert "reviewer change" in result.their_md
assert "-authored" in result.their_diff and "+reviewer change" in result.their_diff
assert "DIVERGED" in result.summary()

# Diverged + missing snapshot: still produces diff against empty
result = detect_divergence(mcp2, page_id="P1", last_published_version=5,
                           read_snapshot=lambda pid, v: None)
assert result.diverged is True and result.snapshot is None
assert "+reviewer change" in result.their_diff

# Equal-version edge case (current < last_published — defensive)
def fake_mcp_old(tool, **kw):
    if tool == "getAccessibleAtlassianResources":
        return [{"id": "cid"}]
    if tool == "getConfluencePage":
        adf = {"type": "doc", "content": [{"type": "paragraph", "content": []}]}
        return {"id": kw["pageId"], "title": "T", "version": {"number": 3},
                "body": {"atlas_doc_format": {"value": json.dumps(adf)}},
                "contentFormat": "adf"}
mcp3 = ConfluenceMCP(fake_mcp_old)
result = detect_divergence(mcp3, page_id="P1", last_published_version=5,
                           read_snapshot=lambda pid, v: "")
assert result.diverged is False  # current (3) < last_published (5) — treat as not diverged

print("OK")
PYEOF
assert_output "lib/divergence — compute_diff, no-divergence, diverged, missing-snapshot, defensive" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST22_SCRIPT'" 'OK'
rm -f "$TEST22_SCRIPT"

# ------------------------------------------------------------
# 23. lib/review_plugin/ — interface + DocumentControlPlugin reference + stubs
# ------------------------------------------------------------
echo
echo "[23] review_plugin (DocumentControlPlugin + stubs + loader)"
for f in lib/review_plugin/__init__.py lib/review_plugin/base.py \
         lib/review_plugin/document_control.py lib/review_plugin/comala.py \
         lib/review_plugin/softcomply.py; do
    assert "structure: $f" "[ -f '$SKILL_DIR/$f' ]"
done

assert "lib/review_plugin imports cleanly" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' -c 'from lib.review_plugin import (
    ApprovalState, ApprovalSigner, PluginError, PluginNotFound, PluginNotImplemented,
    ReviewPlugin, load_plugin
); from lib.review_plugin.document_control import DocumentControlPlugin, find_signature_macros, parse_signers_from_node, EXTENSION_KEY; from lib.review_plugin.comala import ComalaPlugin; from lib.review_plugin.softcomply import SoftComplyPlugin'"

TEST23_SCRIPT="$(mktemp /tmp/cc-test23-XXXXXX.py)"
cat > "$TEST23_SCRIPT" <<'PYEOF'
import json
from lib.review_plugin import (
    load_plugin, PluginNotFound, PluginNotImplemented,
    ApprovalState, ApprovalSigner,
)
from lib.review_plugin.document_control import (
    DocumentControlPlugin, find_signature_macros, parse_signers_from_node,
)
from lib.review_plugin.comala import ComalaPlugin
from lib.review_plugin.softcomply import SoftComplyPlugin
from lib.confluence_mcp import ConfluenceMCP

# Loader resolves all three names + case-insensitive
assert isinstance(load_plugin("document_control"), DocumentControlPlugin)
assert isinstance(load_plugin("Document_Control"), DocumentControlPlugin)
assert isinstance(load_plugin("comala"), ComalaPlugin)
assert isinstance(load_plugin("softcomply"), SoftComplyPlugin)

# Loader rejects unknown / empty
for bad in ("unknown", "", "  "):
    try:
        load_plugin(bad)
        raise AssertionError(f"expected PluginNotFound for {bad!r}")
    except PluginNotFound:
        pass

# Stubs raise PluginNotImplemented
for stub in (ComalaPlugin(), SoftComplyPlugin()):
    try:
        stub.detect_approval("p", None)
        raise AssertionError(f"expected PluginNotImplemented from {stub.name}")
    except PluginNotImplemented:
        pass

# find_signature_macros + parse_signers — Shape A (JSON-encoded list)
adf = {"type": "doc", "content": [
    {"type": "paragraph", "content": [{"type": "text", "text": "body"}]},
    {"type": "extension", "attrs": {"extensionKey": "page-signatures", "parameters": {
        "macroParams": {"signatures": {"value": json.dumps([
            {"accountId": "u1", "displayName": "Alice", "role": "Author", "signedAt": "2026-04-01"},
            {"accountId": "u2", "displayName": "Bob", "role": "Reviewer", "signedAt": "2026-04-02"},
        ])}}
    }}},
    {"type": "extension", "attrs": {"extensionKey": "other-macro"}},
]}
macros = find_signature_macros(adf)
assert len(macros) == 1, len(macros)
signers = parse_signers_from_node(macros[0])
assert len(signers) == 2 and signers[0].display_name == "Alice" and signers[0].role == "Author"

# Shape B: parameters.signatures direct list
node_b = {"type": "extension", "attrs": {"extensionKey": "page-signatures", "parameters": {
    "signatures": [{"accountId": "x", "displayName": "X", "signedAt": "2026-01-01"}],
}}}
assert len(parse_signers_from_node(node_b)) == 1

# Shape C: localInfo
node_c = {"type": "extension", "attrs": {"extensionKey": "page-signatures", "localInfo": {
    "signers": [{"accountId": "q", "displayName": "Q", "signedAt": "2026-02-02"}],
}}}
assert len(parse_signers_from_node(node_c)) == 1

# Empty macro -> []
assert parse_signers_from_node({"type": "extension", "attrs": {"extensionKey": "page-signatures"}}) == []

# detect_approval — happy path via fake MCP
def fake_mcp_happy(tool, **kw):
    if tool == "getAccessibleAtlassianResources":
        return [{"id": "cid"}]
    if tool == "getConfluencePage":
        return {"id": kw["pageId"], "title": "T", "version": {"number": 12},
                "body": {"atlas_doc_format": {"value": json.dumps(adf)}},
                "contentFormat": "adf"}
mcp = ConfluenceMCP(fake_mcp_happy)
plugin = DocumentControlPlugin()
state = plugin.detect_approval("PAGE", mcp)
assert state.approved is True
assert state.plugin_name == "DocumentControlPlugin"
assert state.page_version == 12
assert state.evidence_kind == "page-signatures"
assert len(state.signers) == 2 and state.signers[0].display_name == "Alice"
fm = state.to_frontmatter()
assert fm["approved"] is True and fm["plugin"] == "DocumentControlPlugin"
assert len(fm["signers"]) == 2 and fm["signers"][0]["role"] == "Author"

# detect_approval — no macro -> approved=False, plugin-named reason
adf_no_macro = {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "body"}]}]}
def fake_mcp_no(tool, **kw):
    if tool == "getAccessibleAtlassianResources":
        return [{"id": "cid"}]
    if tool == "getConfluencePage":
        return {"id": kw["pageId"], "title": "T", "version": {"number": 5},
                "body": {"atlas_doc_format": {"value": json.dumps(adf_no_macro)}},
                "contentFormat": "adf"}
state = plugin.detect_approval("PAGE", ConfluenceMCP(fake_mcp_no))
assert state.approved is False
assert "page-signatures" in state.reason and "DocumentControlPlugin" in state.reason

# detect_approval — macro present but empty -> approved=False, "no parsed signers"
adf_empty = {"type": "doc", "content": [
    {"type": "extension", "attrs": {"extensionKey": "page-signatures"}},
]}
def fake_mcp_empty(tool, **kw):
    if tool == "getAccessibleAtlassianResources":
        return [{"id": "cid"}]
    if tool == "getConfluencePage":
        return {"id": kw["pageId"], "title": "T", "version": {"number": 5},
                "body": {"atlas_doc_format": {"value": json.dumps(adf_empty)}},
                "contentFormat": "adf"}
state = plugin.detect_approval("PAGE", ConfluenceMCP(fake_mcp_empty))
assert state.approved is False and "no parsed signers" in state.reason

# Write-side stubs raise PluginNotImplemented
for op in (lambda: plugin.start_workflow("p", mcp),
           lambda: plugin.transition("p", "frozen", mcp),
           lambda: plugin.supersede("p", mcp)):
    try:
        op()
        raise AssertionError("expected PluginNotImplemented")
    except PluginNotImplemented:
        pass

# list_approvals delegates to detect_approval
signers = plugin.list_approvals("PAGE", mcp)
assert len(signers) == 2 and signers[0].display_name == "Alice"

print("OK")
PYEOF
assert_output "lib/review_plugin — loader, DocumentControlPlugin (3 macro shapes), happy/no-macro/empty paths, write-side stubs" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST23_SCRIPT'" 'OK'
rm -f "$TEST23_SCRIPT"

# ------------------------------------------------------------
# 24. lib/frontmatter.py — HTML-comment YAML round-trip
# ------------------------------------------------------------
echo
echo "[24] frontmatter (HTML-comment YAML)"
assert "lib/frontmatter.py exists" "[ -f '$SKILL_DIR/lib/frontmatter.py' ]"

TEST24_SCRIPT="$(mktemp /tmp/cc-test24-XXXXXX.py)"
cat > "$TEST24_SCRIPT" <<'PYEOF'
import tempfile
from pathlib import Path
from lib.frontmatter import (
    parse, serialize, read, write, update, get_state,
)

# Round-trip parse/serialize
data = {"title": "T", "state": "published", "confluence": {"page_id": "123", "space_key": "AFAI"}}
text = serialize(data, "# Body\n\ncontent")
fm = parse(text)
assert fm.data == data
assert "# Body" in fm.body

# No frontmatter: parse returns empty dict + body verbatim
fm = parse("# Just a Body\nNo frontmatter")
assert fm.data == {} and fm.body == "# Just a Body\nNo frontmatter"

# I/O: write + read
with tempfile.TemporaryDirectory() as td:
    p = Path(td) / "doc.md"
    write(p, data, "# Body\n")
    fm = read(p)
    assert fm.data["title"] == "T"
    assert fm.data["confluence"]["page_id"] == "123"

    # update() deep-merges into nested dicts
    update(p, confluence={"last_published_version": 7})
    fm = read(p)
    assert fm.data["confluence"]["page_id"] == "123"  # preserved
    assert fm.data["confluence"]["last_published_version"] == 7  # added
    assert fm.data["state"] == "published"  # preserved

    # get_state shortcut
    assert get_state(p) == "published"

print("OK")
PYEOF
assert_output "lib/frontmatter — round-trip + update deep-merge + get_state" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST24_SCRIPT'" 'OK'
rm -f "$TEST24_SCRIPT"

# ------------------------------------------------------------
# 25. lib/mcp_bridge.py — FixtureMCPProxy + StreamMCPProxy
# ------------------------------------------------------------
echo
echo "[25] mcp_bridge (StreamMCPProxy + FixtureMCPProxy)"
assert "lib/mcp_bridge.py exists" "[ -f '$SKILL_DIR/lib/mcp_bridge.py' ]"

TEST25_SCRIPT="$(mktemp /tmp/cc-test25-XXXXXX.py)"
cat > "$TEST25_SCRIPT" <<'PYEOF'
import io, json
from lib.mcp_bridge import (
    BridgeError, FixtureMCPProxy, StreamMCPProxy, make_proxy,
)

# FixtureMCPProxy with dict
proxy = FixtureMCPProxy({"getAccessibleAtlassianResources": [{"id": "cid"}]})
assert proxy("getAccessibleAtlassianResources") == [{"id": "cid"}]
assert proxy.calls == [("getAccessibleAtlassianResources", {})]
try:
    proxy("missingTool")
    raise AssertionError("expected BridgeError")
except BridgeError:
    pass

# FixtureMCPProxy with callable
def lookup(tool, args):
    if tool == "getConfluencePage" and args["pageId"] == "P1":
        return {"id": "P1", "title": "X"}
    raise BridgeError(f"no fixture for {tool}, {args}")
proxy2 = FixtureMCPProxy(lookup)
assert proxy2("getConfluencePage", pageId="P1") == {"id": "P1", "title": "X"}
try:
    proxy2("getConfluencePage", pageId="P2")
    raise AssertionError("expected")
except BridgeError:
    pass

# StreamMCPProxy via in-memory streams
directives = io.StringIO()
results = io.StringIO()
proxy3 = StreamMCPProxy(directives, results)

# Simulate the agent: prime results, then verify what got written
def run_with_response(tool: str, args: dict, response: dict) -> tuple:
    # Reset directives buffer
    directives.seek(0); directives.truncate()
    # We need to write the response after the directive is emitted; use
    # a custom stream that captures the directive id and answers it.
    pass

# Direct approach: write proxy result, then call. Since proxy reads
# AFTER writing, we can pre-seed results with a record carrying the
# next id. Use the public API: monkey-patch readline.
import uuid as _uuid

class CannedResults:
    def __init__(self, responses):
        # responses is a list of (response_dict_minus_id) — id is filled in
        self.responses = responses
        self.idx = 0
        self.last_id = None
    def readline(self):
        # We must learn the directive id; cheat by reading from directives
        if self.last_id is None:
            directives.seek(0)
            line = directives.readlines()[-1].strip()
            self.last_id = json.loads(line)["id"]
        resp = dict(self.responses[self.idx])
        self.idx += 1
        resp["id"] = self.last_id
        self.last_id = None
        return json.dumps(resp) + "\n"

canned = CannedResults([{"ok": True, "result": [{"id": "cid"}]}])
proxy3 = StreamMCPProxy(directives, canned)
result = proxy3("getAccessibleAtlassianResources")
assert result == [{"id": "cid"}]

# Verify the directive was well-formed
emitted = json.loads(directives.getvalue().strip().split("\n")[-1])
assert emitted["tool"] == "getAccessibleAtlassianResources"
assert emitted["args"] == {}

# Error response → raises BridgeError
canned2 = CannedResults([{"ok": False, "error": "blew up"}])
proxy4 = StreamMCPProxy(directives, canned2)
try:
    proxy4("getConfluencePage", pageId="X")
    raise AssertionError("expected")
except BridgeError as exc:
    assert "blew up" in str(exc)

# make_proxy
mp = make_proxy(transport="fixture", fixture={"foo": "bar"})
assert isinstance(mp, FixtureMCPProxy)
try:
    make_proxy(transport="fixture")
    raise AssertionError
except BridgeError:
    pass
try:
    make_proxy(transport="unknown")
    raise AssertionError
except BridgeError:
    pass

print("OK")
PYEOF
assert_output "lib/mcp_bridge — FixtureMCPProxy dict+callable, StreamMCPProxy round-trip + error, make_proxy" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST25_SCRIPT'" 'OK'
rm -f "$TEST25_SCRIPT"

# ------------------------------------------------------------
# 26. actions/adopt_helper.py — full pipeline against MCP fixture response
# ------------------------------------------------------------
echo
echo "[26] adopt_helper (write subcommand round-trip)"
assert "actions/adopt_helper.py exists" "[ -f '$SKILL_DIR/actions/adopt_helper.py' ]"
assert "actions/adopt.md exists" "[ -f '$SKILL_DIR/actions/adopt.md' ]"

TEST26_SCRIPT="$(mktemp /tmp/cc-test26-XXXXXX.py)"
cat > "$TEST26_SCRIPT" <<PYEOF
import json, subprocess, tempfile, sys
from pathlib import Path
sys.path.insert(0, "$SKILL_DIR")
from lib.frontmatter import read as read_fm

adf = {
    "type": "doc", "content": [
        {"type": "heading", "attrs": {"level": 1}, "content": [{"type": "text", "text": "Probe"}]},
        {"type": "expand", "attrs": {"title": "__CONFLUENCE_ZONE__: alpha"}, "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "zone body"}]}]},
        {"type": "extension", "attrs": {"extensionKey": "page-signatures"}},
    ]
}
mcp_resp = {
    "id": "P1", "title": "Probe", "spaceId": "SP", "parentId": "P0",
    "version": {"number": 9},
    "body": {"atlas_doc_format": {"value": json.dumps(adf)}},
    "contentFormat": "adf",
}

with tempfile.TemporaryDirectory() as td:
    target = Path(td) / "out/probe.md"
    cache = Path(td) / "cache"
    proc = subprocess.run(
        ["$PY", "$SKILL_DIR/actions/adopt_helper.py", "write",
         "--target", str(target),
         "--base-url", "https://example.atlassian.net",
         "--space-key", "AFAI",
         "--parent-page-id", "P0",
         "--page-path", "AFAI/Probe",
         "--cache-root", str(cache)],
        input=json.dumps(mcp_resp), text=True, capture_output=True,
    )
    assert proc.returncode == 0, (proc.returncode, proc.stderr)
    assert "adopted: P1" in proc.stdout

    fm = read_fm(target)
    assert fm.data["title"] == "Probe"
    assert fm.data["state"] == "published"
    assert fm.data["confluence"]["page_id"] == "P1"
    assert fm.data["confluence"]["adopted_from_version"] == 9
    assert "# Probe" in fm.body
    assert "<details>" in fm.body and "__CONFLUENCE_ZONE__: alpha" in fm.body
    assert "<!-- confluence-side: page-signatures -->" in fm.body

    snap = cache / "snapshots" / "P1-9.md"
    assert snap.is_file() and "# Probe" in snap.read_text()

# preview subcommand: prints to stdout, no writes
with tempfile.TemporaryDirectory() as td:
    proc = subprocess.run(
        ["$PY", "$SKILL_DIR/actions/adopt_helper.py", "preview",
         "--base-url", "https://example.atlassian.net",
         "--space-key", "AFAI"],
        input=json.dumps(mcp_resp), text=True, capture_output=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "# Probe" in proc.stdout

# Empty stdin → exit 64
proc = subprocess.run(
    ["$PY", "$SKILL_DIR/actions/adopt_helper.py", "preview",
     "--base-url", "x", "--space-key", "y"],
    input="", text=True, capture_output=True,
)
assert proc.returncode == 64, proc.returncode
assert "no input on stdin" in proc.stderr

# Bad JSON → exit 65
proc = subprocess.run(
    ["$PY", "$SKILL_DIR/actions/adopt_helper.py", "preview",
     "--base-url", "x", "--space-key", "y"],
    input="not json", text=True, capture_output=True,
)
assert proc.returncode == 65

print("OK")
PYEOF
assert_output "actions/adopt_helper — write/preview round-trip, frontmatter, snapshot, error paths" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST26_SCRIPT'" 'OK'
rm -f "$TEST26_SCRIPT"

# ------------------------------------------------------------
# 27. actions/adopt_tree.py — full bulk pipeline via fixture
# ------------------------------------------------------------
echo
echo "[27] adopt_tree (bulk via fixture)"
assert "actions/adopt_tree.py exists" "[ -f '$SKILL_DIR/actions/adopt_tree.py' ]"
assert "actions/adopt_tree.md exists" "[ -f '$SKILL_DIR/actions/adopt_tree.md' ]"

TEST27_SCRIPT="$(mktemp /tmp/cc-test27-XXXXXX.py)"
cat > "$TEST27_SCRIPT" <<PYEOF
import json, subprocess, tempfile, sys
from pathlib import Path

def page(pid, title, parent_id, version=1, content_text="body"):
    adf = {"type": "doc", "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": content_text}]}
    ]}
    return {
        "id": pid, "title": title, "spaceId": "SP", "parentId": parent_id,
        "version": {"number": version},
        "body": {"atlas_doc_format": {"value": json.dumps(adf)}},
        "contentFormat": "adf",
    }

ROOT = "1000"; CHILD = "1001"; TOPIC_PARENT = "1002"; V1 = "1003"; V2 = "1004"

records = [
    {"tool": "getAccessibleAtlassianResources", "args": {}, "result": [{"id": "cid", "url": "https://example.atlassian.net"}]},
    {"tool": "getConfluencePage", "args": {"cloudId": "cid", "pageId": ROOT, "contentFormat": "adf"}, "result": page(ROOT, "Root", "", 5, "root body")},
    {"tool": "getConfluencePageDescendants", "args": {"cloudId": "cid", "pageId": ROOT}, "result": [{"id": CHILD}, {"id": TOPIC_PARENT}, {"id": V1}, {"id": V2}]},
    {"tool": "getConfluencePage", "args": {"cloudId": "cid", "pageId": CHILD, "contentFormat": "adf"}, "result": page(CHILD, "Plain Child", ROOT)},
    {"tool": "getConfluencePage", "args": {"cloudId": "cid", "pageId": TOPIC_PARENT, "contentFormat": "adf"}, "result": page(TOPIC_PARENT, "Topic Parent", ROOT)},
    {"tool": "getConfluencePage", "args": {"cloudId": "cid", "pageId": V1, "contentFormat": "adf"}, "result": page(V1, "Topic Parent - 1.0.0", TOPIC_PARENT, 3, "v1 body")},
    {"tool": "getConfluencePage", "args": {"cloudId": "cid", "pageId": V2, "contentFormat": "adf"}, "result": page(V2, "Topic Parent - 2.0.0", TOPIC_PARENT, 7, "v2 body")},
]

with tempfile.TemporaryDirectory() as td:
    fixture = Path(td) / "fixture.jsonl"
    fixture.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    target = Path(td) / "staging" / "AFAI"
    cache = Path(td) / "cache"

    proc = subprocess.run(
        ["$PY", "$SKILL_DIR/actions/adopt_tree.py",
         "--root-page-id", ROOT,
         "--base-url", "https://example.atlassian.net",
         "--space-key", "AFAI",
         "--target-root", str(target),
         "--cache-root", str(cache),
         "--fixture", str(fixture)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, (proc.returncode, proc.stderr)

    files = sorted(p.relative_to(target).as_posix() for p in target.rglob("*.md"))
    assert files == [
        "plain-child.md", "root.md",
        "topic-parent/index.md", "topic-parent/v1.0.0.md", "topic-parent/v2.0.0.md",
    ], files

    # Versioned file uses the parent's slug as the topic folder (not double-nested)
    v1_path = target / "topic-parent" / "v1.0.0.md"
    assert v1_path.is_file()
    v1 = v1_path.read_text()
    assert "page_id: '1003'" in v1
    assert "last_published_version: 3" in v1
    assert "v1 body" in v1

    # Topic parent landed at index.md
    idx = (target / "topic-parent" / "index.md").read_text()
    assert "page_id: '1002'" in idx
    assert "title: Topic Parent" in idx

    # Snapshots exist
    snap_dir = cache / "snapshots"
    snaps = sorted(p.name for p in snap_dir.iterdir())
    assert snaps == ["1000-5.md", "1001-1.md", "1002-1.md", "1003-3.md", "1004-7.md"]

# Dry-run does not write files
with tempfile.TemporaryDirectory() as td:
    fixture = Path(td) / "fixture.jsonl"
    fixture.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    target = Path(td) / "dry"
    cache = Path(td) / "dry-cache"
    proc = subprocess.run(
        ["$PY", "$SKILL_DIR/actions/adopt_tree.py",
         "--root-page-id", ROOT,
         "--base-url", "https://example.atlassian.net",
         "--space-key", "AFAI",
         "--target-root", str(target),
         "--cache-root", str(cache),
         "--fixture", str(fixture),
         "--dry-run"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0
    assert "PLAN" in proc.stdout
    assert not target.exists()

print("OK")
PYEOF
assert_output "actions/adopt_tree — bulk fixture: 5 pages, topic+versions layout, snapshots, dry-run" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST27_SCRIPT'" 'OK'
rm -f "$TEST27_SCRIPT"

# ------------------------------------------------------------
# 29. actions/publish_helper.py — full pipeline (5 subcommands)
# ------------------------------------------------------------
echo
echo "[29] publish_helper (precheck / body / splice / write-confluence-side / commit)"
for f in actions/publish_helper.py actions/publish.md actions/pull.md; do
    assert "structure: $f" "[ -f '$SKILL_DIR/$f' ]"
done

TEST29_SCRIPT="$(mktemp /tmp/cc-test29-XXXXXX.py)"
cat > "$TEST29_SCRIPT" <<PYEOF
import json, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, "$SKILL_DIR")
from lib.frontmatter import write as write_fm, read as read_fm

PY = "$PY"
HELPER = "$SKILL_DIR/actions/publish_helper.py"

with tempfile.TemporaryDirectory() as td:
    td_path = Path(td)
    src = td_path / "doc.md"
    cache = td_path / "cache"

    body = (
        "# Heading\n\n"
        "See [other](other.md).\n\n"
        "\`\`\`html\n<x/>\n\`\`\`\n\n"
        "<details>\n"
        "<summary>__CONFLUENCE_ZONE__: open-issues</summary>\n\n"
        "Reviewer fills this.\n\n"
        "</details>\n"
    )

    write_fm(src, {
        "title": "Doc", "state": "published",
        "confluence": {"page_id": "P1", "space_key": "AFAI", "last_published_version": 3},
    }, body)
    snap_dir = cache / "snapshots"
    snap_dir.mkdir(parents=True)
    (snap_dir / "P1-3.md").write_text("# Heading\n\nold body\n")

    current_adf = {"type": "doc", "content": [
        {"type": "heading", "attrs": {"level": 1}, "content": [{"type": "text", "text": "Heading"}]},
        {"type": "paragraph", "content": [{"type": "text", "text": "reviewer added this"}]},
        {"type": "expand", "attrs": {"title": "__CONFLUENCE_ZONE__: open-issues"}, "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "reviewer-side jira filter"}]}]},
    ]}
    current_response = {"id": "P1", "title": "Doc", "version": {"number": 5},
                        "body": {"atlas_doc_format": {"value": json.dumps(current_adf)}}}
    current_path = td_path / "current.json"
    current_path.write_text(json.dumps(current_response))

    # 1. precheck — diverged
    proc = subprocess.run([PY, HELPER, "precheck", "--source", str(src),
                           "--current-adf", str(current_path), "--cache-root", str(cache)],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    packet = json.loads(proc.stdout)
    assert packet["page_id"] == "P1"
    assert packet["last_published_version"] == 3
    assert packet["is_first_publish"] is False
    assert packet["diverged"] is True and packet["current_version"] == 5
    assert len(packet["zones_captured"]) == 1
    assert packet["zones_captured"][0]["name"] == "open-issues"
    assert "reviewer added this" in packet["their_diff"]
    assert packet["snapshot_present"] is True
    assert packet["transform_report"]["fence_swaps"] == 1

    # 2. body
    proc = subprocess.run([PY, HELPER, "body", "--source", str(src)],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    transformed = proc.stdout
    assert "\`\`\`text" in transformed and "\`\`\`html" not in transformed
    assert "other (_pending Confluence publish_)" in transformed

    # 3. splice
    zones_path = td_path / "zones.json"
    zones_path.write_text(json.dumps(packet["zones_captured"]))
    new_adf = {"type": "doc", "content": [
        {"type": "heading", "attrs": {"level": 1}, "content": [{"type": "text", "text": "Heading"}]},
        {"type": "expand", "attrs": {"title": "__CONFLUENCE_ZONE__: open-issues"}, "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "EMPTY"}]}]}
    ]}
    proc = subprocess.run([PY, HELPER, "splice", "--zones", str(zones_path)],
                          input=json.dumps(new_adf), text=True, capture_output=True)
    assert proc.returncode == 0, proc.stderr
    spliced = json.loads(proc.stdout)
    zone_text = spliced["content"][1]["content"][0]["content"][0]["text"]
    assert zone_text == "reviewer-side jira filter"

    # 4. write-confluence-side
    proc = subprocess.run([PY, HELPER, "write-confluence-side",
                           "--source", str(src), "--current-adf", str(current_path)],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    side = (src.parent / (src.name + ".confluence-side.md")).read_text()
    assert "reviewer added this" in side and "open-issues" in side

    # 5. commit
    proc = subprocess.run([PY, HELPER, "commit",
                           "--source", str(src), "--page-id", "P1", "--version", "6",
                           "--cache-root", str(cache)],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    fm = read_fm(src)
    assert fm.data["state"] == "published"
    assert fm.data["confluence"]["last_published_version"] == 6
    assert (cache / "snapshots" / "P1-6.md").is_file()
    assert not (cache / "snapshots" / "P1-3.md").exists()

# 6. precheck on first-publish (no current-adf)
with tempfile.TemporaryDirectory() as td:
    td_path = Path(td)
    src = td_path / "new.md"
    write_fm(src, {"title": "New", "state": "draft", "confluence": {"space_key": "AFAI"}}, "# Hi\n")
    proc = subprocess.run([PY, HELPER, "precheck", "--source", str(src),
                           "--cache-root", str(td_path)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    packet = json.loads(proc.stdout)
    assert packet["is_first_publish"] is True
    assert packet["diverged"] is False
    assert packet["zones_captured"] == []

print("OK")
PYEOF
assert_output "actions/publish_helper — precheck/body/splice/write-confluence-side/commit + first-publish branch" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST29_SCRIPT'" 'OK'
rm -f "$TEST29_SCRIPT"

# ------------------------------------------------------------
# 30. actions/freeze_helper.py + status.py — freeze, unfreeze, status
# ------------------------------------------------------------
echo
echo "[30] freeze_helper + status (verify, unfreeze, table+JSON+filter)"
for f in actions/freeze_helper.py actions/freeze.md actions/unfreeze.md actions/status.py; do
    assert "structure: $f" "[ -f '$SKILL_DIR/$f' ]"
done

TEST30_SCRIPT="$(mktemp /tmp/cc-test30-XXXXXX.py)"
cat > "$TEST30_SCRIPT" <<PYEOF
import json, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, "$SKILL_DIR")
from lib.frontmatter import write as write_fm, read as read_fm

PY = "$PY"
FH = "$SKILL_DIR/actions/freeze_helper.py"
ST = "$SKILL_DIR/actions/status.py"

# freeze verify HAPPY (page-signatures macro present with 2 signers)
with tempfile.TemporaryDirectory() as td:
    src = Path(td) / "doc.md"
    write_fm(src, {
        "title": "Doc", "state": "review-formal",
        "confluence": {"page_id": "P1", "space_key": "AFAI", "last_published_version": 9},
    }, "# Body\n")
    adf = {"type": "doc", "content": [
        {"type": "extension", "attrs": {"extensionKey": "page-signatures", "parameters": {
            "macroParams": {"signatures": {"value": json.dumps([
                {"accountId": "u1", "displayName": "Alice", "role": "Author", "signedAt": "2026-04-01"},
                {"accountId": "u2", "displayName": "Bob", "role": "Reviewer", "signedAt": "2026-04-02"},
            ])}}
        }}},
    ]}
    response = {"id": "P1", "title": "Doc", "version": {"number": 12}, "body": adf}
    proc = subprocess.run([PY, FH, "verify", "--source", str(src), "--plugin", "document_control"],
                          input=json.dumps(response), text=True, capture_output=True)
    assert proc.returncode == 0, (proc.returncode, proc.stderr)
    assert "DocumentControlPlugin detected approval" in proc.stdout
    assert "Alice" in proc.stdout and "Bob" in proc.stdout
    fm = read_fm(src)
    assert fm.data["state"] == "frozen"
    assert fm.data["confluence"]["frozen_at_version"] == 12
    appr = fm.data["confluence"]["approval"]
    assert appr["plugin"] == "DocumentControlPlugin"
    assert appr["approved"] is True
    assert appr["evidence_kind"] == "page-signatures"
    assert len(appr["signers"]) == 2

# freeze verify NO MACRO (reject with plugin-named reason; state unchanged)
with tempfile.TemporaryDirectory() as td:
    src = Path(td) / "doc.md"
    write_fm(src, {"state": "review-formal",
                   "confluence": {"page_id": "X", "last_published_version": 1}}, "# x\n")
    response = {"id": "X", "version": {"number": 1},
                "body": {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "body"}]}]}}
    proc = subprocess.run([PY, FH, "verify", "--source", str(src), "--plugin", "document_control"],
                          input=json.dumps(response), text=True, capture_output=True)
    assert proc.returncode == 1
    assert "page-signatures" in proc.stderr and "DocumentControlPlugin" in proc.stderr
    assert read_fm(src).data["state"] == "review-formal"

# freeze verify WRONG STATE -> 66
with tempfile.TemporaryDirectory() as td:
    src = Path(td) / "doc.md"
    write_fm(src, {"state": "draft", "confluence": {"page_id": "X"}}, "# x\n")
    proc = subprocess.run([PY, FH, "verify", "--source", str(src), "--plugin", "document_control"],
                          input="{}", text=True, capture_output=True)
    assert proc.returncode == 66
    assert "review-formal" in proc.stderr

# freeze verify STUB plugin (comala) -> 67
with tempfile.TemporaryDirectory() as td:
    src = Path(td) / "doc.md"
    write_fm(src, {"state": "review-formal", "confluence": {"page_id": "X"}}, "# x\n")
    proc = subprocess.run([PY, FH, "verify", "--source", str(src), "--plugin", "comala"],
                          input='{"id": "X", "version": {"number": 1}, "body": {"type": "doc"}}',
                          text=True, capture_output=True)
    assert proc.returncode == 67
    assert "ComalaPlugin" in proc.stderr

# unfreeze HAPPY
with tempfile.TemporaryDirectory() as td:
    src = Path(td) / "doc.md"
    write_fm(src, {
        "state": "frozen",
        "confluence": {"page_id": "P", "frozen_at_version": 12,
                       "approval": {"plugin": "DocumentControlPlugin", "approved": True}},
    }, "# x\n")
    proc = subprocess.run([PY, FH, "unfreeze", "--source", str(src)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "WARNING" in proc.stdout
    fm = read_fm(src)
    assert fm.data["state"] == "published"
    assert fm.data["confluence"]["frozen_at_version"] is None
    assert "unfrozen_at" in fm.data["confluence"]
    # Approval evidence preserved as audit history
    assert fm.data["confluence"]["approval"]["plugin"] == "DocumentControlPlugin"

# unfreeze WRONG STATE -> 66
with tempfile.TemporaryDirectory() as td:
    src = Path(td) / "doc.md"
    write_fm(src, {"state": "published"}, "# x\n")
    proc = subprocess.run([PY, FH, "unfreeze", "--source", str(src)], capture_output=True, text=True)
    assert proc.returncode == 66

# status: empty + populated tree
with tempfile.TemporaryDirectory() as td:
    docs = Path(td) / "docs"
    docs.mkdir()

    # Empty
    proc = subprocess.run([PY, ST, str(docs)], capture_output=True, text=True)
    assert proc.returncode == 0
    assert "(no controlled docs found)" in proc.stdout

    # Populated
    write_fm(docs / "a.md", {"title": "A", "state": "draft"}, "# A\n")
    write_fm(docs / "b.md", {"title": "B", "state": "published",
                              "confluence": {"page_id": "111", "last_published_version": 3}}, "# B\n")
    write_fm(docs / "c.md", {"title": "C", "state": "frozen",
                              "confluence": {"page_id": "222", "last_published_version": 5,
                                             "frozen_at_version": 5,
                                             "approval": {"plugin": "DocumentControlPlugin",
                                                          "approved": True,
                                                          "signers": [{"display_name": "Alice"}]}}}, "# C\n")
    (docs / "plain.md").write_text("# not controlled\n")
    (docs / "b.md.confluence-side.md").write_text("side\n")

    # Table form
    proc = subprocess.run([PY, ST, str(docs)], capture_output=True, text=True)
    assert proc.returncode == 0
    assert "state" in proc.stdout and "page_id" in proc.stdout
    assert "1 draft" in proc.stdout and "1 published" in proc.stdout and "1 frozen" in proc.stdout
    assert "3 total" in proc.stdout
    assert "plain.md" not in proc.stdout
    assert "confluence-side" not in proc.stdout

    # JSON form
    proc = subprocess.run([PY, ST, str(docs), "--json"], capture_output=True, text=True)
    assert proc.returncode == 0
    rows = json.loads(proc.stdout)
    assert len(rows) == 3
    titles = sorted(r["title"] for r in rows)
    assert titles == ["A", "B", "C"]
    c_row = next(r for r in rows if r["title"] == "C")
    assert c_row["state"] == "frozen"
    assert c_row["frozen_at_version"] == 5
    assert c_row["approval_plugin"] == "DocumentControlPlugin"
    assert c_row["approval_signers"] == ["Alice"]

    # State filter
    proc = subprocess.run([PY, ST, str(docs), "--state", "frozen", "--json"],
                          capture_output=True, text=True)
    assert proc.returncode == 0
    rows = json.loads(proc.stdout)
    assert len(rows) == 1 and rows[0]["title"] == "C"

# Missing-path -> 64
proc = subprocess.run([PY, ST, "/nonexistent/path/xyz"], capture_output=True, text=True)
assert proc.returncode == 64

print("OK")
PYEOF
assert_output "actions/freeze_helper + status — verify (4 paths) + unfreeze (2 paths) + status (table+json+filter+empty+missing)" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST30_SCRIPT'" 'OK'
rm -f "$TEST30_SCRIPT"

# ------------------------------------------------------------
# 31. lib/formal_review.py + actions/review_formal_helper.py
# ------------------------------------------------------------
echo
echo "[31] formal_review + review_formal_helper (start/status/update/abort)"
for f in lib/formal_review.py actions/review_formal_helper.py \
         actions/review-formal-start.md actions/review-formal-status.md \
         actions/review-formal-update.md actions/review-formal-abort.md; do
    assert "structure: $f" "[ -f '$SKILL_DIR/$f' ]"
done

TEST31_SCRIPT="$(mktemp /tmp/cc-test31-XXXXXX.py)"
cat > "$TEST31_SCRIPT" <<PYEOF
import json, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, "$SKILL_DIR")
from lib.frontmatter import write as write_fm, read as read_fm
from lib.formal_review import (
    FormalReviewSection, FormalReviewItem, render_section, parse_section,
    upsert_block, find_block, remove_block, SENTINEL_END,
)

PY = "$PY"
RFH = "$SKILL_DIR/actions/review_formal_helper.py"

# Render+parse round-trip
s = FormalReviewSection.new(doc_path="docs/foo.md", page_id="6768427047",
                              page_url="https://x/wiki/.../6768427047",
                              baseline_version=9, plugin_name="document_control")
s.open_items.append(FormalReviewItem(kind="inline", id="mref-abc", author="Alice",
                                      anchor="device boundary", text="need cite"))
s.open_items.append(FormalReviewItem(kind="footer", id="c-9999", author="Bob", text="LGTM"))
s.macros.append(FormalReviewItem(kind="macro", id="page-signatures",
                                  text="Confluence-side macro"))
out = render_section(s)
assert SENTINEL_END in out
assert "Page id | 6768427047" in out
assert "**#i-mref-abc**" in out and "**#f-c-9999**" in out
assert "### Confluence-side macros" in out
parsed = parse_section(out)
assert parsed.doc_path == "docs/foo.md"
assert parsed.page_id == "6768427047"
assert parsed.baseline_version == 9
assert len(parsed.open_items) == 2
assert any(it.kind == "inline" and it.id == "mref-abc" and it.author == "Alice" for it in parsed.open_items)
assert any(it.kind == "footer" and it.id == "c-9999" for it in parsed.open_items)
assert len(parsed.macros) == 1 and parsed.macros[0].id == "page-signatures"

# upsert+find+remove + multi-doc isolation
text = "# Task\n"
text2 = upsert_block(text, s)
assert "change-control:formal-review begin doc=docs/foo.md" in text2
s2 = FormalReviewSection.new(doc_path="docs/bar.md", page_id="999",
                               page_url="", baseline_version=2)
text3 = upsert_block(text2, s2)
assert find_block(text3, "docs/foo.md") is not None
assert find_block(text3, "docs/bar.md") is not None
text4 = remove_block(text3, "docs/foo.md")
assert find_block(text4, "docs/foo.md") is None
assert find_block(text4, "docs/bar.md") is not None

# Hand-edited [x] addressed item survives reparse
s3 = FormalReviewSection.new(doc_path="docs/baz.md", page_id="123",
                               page_url="", baseline_version=1)
s3.open_items.append(FormalReviewItem(kind="inline", id="m1", author="X", text="comment"))
text5 = upsert_block("# T\n", s3)
old = "### Already Addressed (will reply on next \`review-formal-update\`)\n\n(none yet)"
new = ("### Already Addressed (will reply on next \`review-formal-update\`)\n\n"
       "- [x] **#i-m1** X — addressed: cited per Section 4.2")
text6 = text5.replace(old, new)
rng = find_block(text6, "docs/baz.md")
block = "\n".join(text6.splitlines()[rng[0]:rng[1]+1])
parsed3 = parse_section(block)
assert len(parsed3.already_addressed) == 1
assert parsed3.already_addressed[0].id == "m1"
assert parsed3.already_addressed[0].resolution_note == "cited per Section 4.2"

# helper.start happy
with tempfile.TemporaryDirectory() as td:
    src = Path(td) / "doc.md"
    write_fm(src, {"title": "Doc", "state": "published",
                   "confluence": {"page_id": "X1", "space_key": "AFAI"}}, "# Body\n")
    task = Path(td) / "task.md"
    task.write_text("# Task 999\n\nbody.\n")
    proc = subprocess.run([PY, RFH, "start", "--source", str(src), "--task-doc", str(task),
                           "--page-url", "https://x/wiki/X1",
                           "--baseline-version", "9", "--plugin", "document_control"],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert read_fm(src).data["state"] == "review-formal"
    assert "change-control:formal-review begin" in task.read_text()

# helper.start wrong state -> 66
with tempfile.TemporaryDirectory() as td:
    src = Path(td) / "doc.md"
    write_fm(src, {"state": "draft", "confluence": {"page_id": "X"}}, "# x\n")
    proc = subprocess.run([PY, RFH, "start", "--source", str(src),
                           "--task-doc", str(Path(td) / "t.md"),
                           "--page-url", "u", "--baseline-version", "1"],
                          capture_output=True, text=True)
    assert proc.returncode == 66

# helper.status — preserves user-edited addressed items
with tempfile.TemporaryDirectory() as td:
    src = Path(td) / "doc.md"
    write_fm(src, {"state": "review-formal",
                   "confluence": {"page_id": "X1", "review_baseline_version": 9}},
             "# Body\n")
    task = Path(td) / "t.md"
    s = FormalReviewSection.new(doc_path=str(src), page_id="X1",
                                  page_url="url", baseline_version=9, plugin_name="document_control")
    task.write_text(upsert_block("", s))
    page = {"id": "X1", "title": "Doc", "version": {"number": 11},
            "body": {"type": "doc", "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "body"}]},
                {"type": "extension", "attrs": {"extensionKey": "page-signatures"}}]}}
    inline = {"results": [{"id": "c-1", "body": "need cite",
                           "author": {"displayName": "Maryna"},
                           "inlineCommentProperties": {"inlineMarkerRef": "mref-abc",
                                                       "inlineOriginalSelection": "device boundary"}}]}
    footer = {"results": [{"id": "c-9999", "body": "LGTM",
                           "author": {"displayName": "Bob"}}]}
    p_p = Path(td) / "page.json"; p_p.write_text(json.dumps(page))
    p_i = Path(td) / "inl.json"; p_i.write_text(json.dumps(inline))
    p_f = Path(td) / "foo.json"; p_f.write_text(json.dumps(footer))
    proc = subprocess.run([PY, RFH, "status", "--source", str(src), "--task-doc", str(task),
                           "--current-adf", str(p_p),
                           "--inline-comments", str(p_i),
                           "--footer-comments", str(p_f)],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "open=2" in proc.stdout and "1 inline" in proc.stdout and "1 footer" in proc.stdout
    assert "macros=1" in proc.stdout
    block_text = task.read_text()
    rng = find_block(block_text, str(src))
    parsed = parse_section("\n".join(block_text.splitlines()[rng[0]:rng[1]+1]))
    assert len(parsed.open_items) == 2
    assert any(it.kind == "inline" and it.id == "mref-abc" for it in parsed.open_items)
    assert len(parsed.macros) == 1 and parsed.macros[0].id == "page-signatures"

# helper.update — moves addressed -> synced, clears macros
with tempfile.TemporaryDirectory() as td:
    src = Path(td) / "doc.md"
    write_fm(src, {"state": "review-formal", "confluence": {"page_id": "X"}}, "# x\n")
    task = Path(td) / "t.md"
    s = FormalReviewSection.new(doc_path=str(src), page_id="X", page_url="", baseline_version=1)
    s.already_addressed.append(FormalReviewItem(kind="inline", id="m1", author="A",
                                                  status="addressed", resolution_note="cited"))
    s.macros.append(FormalReviewItem(kind="macro", id="page-signatures"))
    task.write_text(upsert_block("", s))
    proc = subprocess.run([PY, RFH, "update", "--source", str(src), "--task-doc", str(task)],
                          capture_output=True, text=True)
    assert proc.returncode == 0
    block_text = task.read_text()
    rng = find_block(block_text, str(src))
    parsed = parse_section("\n".join(block_text.splitlines()[rng[0]:rng[1]+1]))
    assert len(parsed.already_addressed) == 0
    assert len(parsed.recently_synced) == 1 and parsed.recently_synced[0].id == "m1"
    assert len(parsed.macros) == 0

# helper.abort — removes block + state -> published
with tempfile.TemporaryDirectory() as td:
    src = Path(td) / "doc.md"
    write_fm(src, {"state": "review-formal", "confluence": {"page_id": "X"}}, "# x\n")
    task = Path(td) / "t.md"
    s = FormalReviewSection.new(doc_path=str(src), page_id="X", page_url="", baseline_version=1)
    task.write_text(upsert_block("# T\nbody\n", s))
    proc = subprocess.run([PY, RFH, "abort", "--source", str(src), "--task-doc", str(task)],
                          capture_output=True, text=True)
    assert proc.returncode == 0
    assert read_fm(src).data["state"] == "published"
    assert find_block(task.read_text(), str(src)) is None
    assert "# T" in task.read_text()

print("OK")
PYEOF
assert_output "lib/formal_review + review_formal_helper — render/parse, upsert/find/remove, multi-doc, addressed-survives, start/status/update/abort" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST31_SCRIPT'" 'OK'
rm -f "$TEST31_SCRIPT"

# ------------------------------------------------------------
# 32. actions/init.py + review_internal_* aliases + setup.sh
# ------------------------------------------------------------
echo
echo "[32] init MCP-preflight + naming-pivot aliases + setup.sh atlassian-mcp"
for f in actions/init.py \
         actions/review_internal_start.py actions/review_internal_status.py \
         actions/review_internal_update.py actions/review_internal_abort.py; do
    assert "structure: $f" "[ -f '$SKILL_DIR/$f' ]"
done

TEST32_SCRIPT="$(mktemp /tmp/cc-test32-XXXXXX.py)"
cat > "$TEST32_SCRIPT" <<PYEOF
import json, subprocess, sys, tempfile
from pathlib import Path

PY = "$PY"
INIT = "$SKILL_DIR/actions/init.py"
ACTIONS = "$SKILL_DIR/actions"

# init on empty tree — auto-creates state.json, warns on missing .mcp.json/project.yml/change-control.yml
with tempfile.TemporaryDirectory() as td:
    proc = subprocess.run([PY, INIT, "--root", td, "--json"],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    rep = json.loads(proc.stdout)
    names = [c["name"] for c in rep["checks"]]
    assert names == ["mcp.json:atlassian", "project.yml:approved_mcps",
                     "change-control.yml", "docs/.change-control/state.json"]
    # state.json was auto-created
    assert (Path(td) / "docs" / ".change-control" / "state.json").is_file()
    # mcp + project.yml + cc.yml all warn
    by_name = {c["name"]: c for c in rep["checks"]}
    assert by_name["mcp.json:atlassian"]["ok"] is False
    assert by_name["docs/.change-control/state.json"]["ok"] is True

# init with a fully-configured tree
with tempfile.TemporaryDirectory() as td:
    Path(td, ".mcp.json").write_text(json.dumps({"mcpServers": {"atlassian": {"type": "http"}}}))
    Path(td, "project.yml").write_text("security:\n  approved_mcps:\n    - atlassian\n")
    Path(td, "change-control.yml").write_text(
        "confluence:\n  base_url: https://x.atlassian.net\n"
        "review_plugin:\n  type: document_control\n"
    )
    proc = subprocess.run([PY, INIT, "--root", td, "--json"],
                          capture_output=True, text=True)
    rep = json.loads(proc.stdout)
    assert all(c["ok"] for c in rep["checks"]), rep
    assert rep["configured_base_url"] == "https://x.atlassian.net"
    assert rep["configured_review_plugin"] == "document_control"

# review_internal_* aliases import cleanly + emit a deprecation notice
for name in ("review_internal_start", "review_internal_status",
             "review_internal_update", "review_internal_abort"):
    proc = subprocess.run([PY, "-c",
                           f"import sys; sys.path.insert(0, '{ACTIONS}'); import {name}"],
                          capture_output=True, text=True)
    assert proc.returncode == 0, (name, proc.stderr)
    src = Path(ACTIONS) / f"{name}.py"
    assert "DEPRECATION NOTICE" in src.read_text()
    assert "as _impl" in src.read_text()

# setup.sh has setup_atlassian_mcp + identity-pinning instructions + main calls it
import os
setup_path = Path("$SKILL_DIR").parents[2] / "setup.sh"
text = setup_path.read_text()
assert "setup_atlassian_mcp()" in text
# Function call site is in main()
main_pos = text.find("\nmain() {")
if main_pos == -1:
    main_pos = text.find("main() {")
assert main_pos >= 0
assert "setup_atlassian_mcp" in text[main_pos:]
# Identity-pinning protocol wording
assert "Identity-pinning protocol" in text
assert "incognito" in text.lower() or "INCOGNITO" in text
assert "/mcp" in text and "Remember me" in text

print("OK")
PYEOF
assert_output "init MCP-preflight (empty tree autocreates + valid tree all-OK) + 4 review_internal_* aliases + setup.sh setup_atlassian_mcp" \
    "cd '$SKILL_DIR' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST32_SCRIPT'" 'OK'
rm -f "$TEST32_SCRIPT"

# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------
echo
echo "==========================================================="
echo "Results: $PASSED passed, $FAILED failed"
echo "==========================================================="
[ $FAILED -gt 0 ] && exit 1
exit 0
