#!/usr/bin/env bash
# run_tests.sh — self-test for the writing-well deterministic linter.
# Exits non-zero if any assertion fails. No external dependencies.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$HERE/test_lint.py"
python3 "$HERE/test_slop.py"
