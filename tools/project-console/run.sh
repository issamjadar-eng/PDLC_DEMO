#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
uv sync
exec uv run uvicorn console.app:app --reload --port 8765
