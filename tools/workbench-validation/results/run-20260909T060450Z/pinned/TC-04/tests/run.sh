#!/usr/bin/env bash
# Run the advisors skill test suite under pytest.
#
# pytest and PyYAML are resolved ephemerally by `uv` — `--no-project` keeps
# uv from picking up any pyproject / PEP 723 script environment, so nothing
# is installed into the repo. The only on-disk artifacts are uv's own cache
# (outside the repo) and pytest/python caches under this skill directory,
# which the skill's .gitignore excludes from version control.
#
# Usage:
#   tests/run.sh                  # whole suite
#   tests/run.sh -k locator -v    # extra args pass straight through to pytest
set -euo pipefail
cd "$(dirname "$0")/.."
exec uv run --no-project --with pytest --with pyyaml python -m pytest tests "$@"
