---
name: web-control
description: Cross-platform browser automation as shared infrastructure — owns Chrome lifecycle (install / launch / status / stop) and DevTools-Protocol connection helpers (Python lib) for consumer skills. Use when other skills need to drive a Chromium-family browser under the user's corporate Google identity (e.g., Workspace operations where API access is denied by org policy). Provides `setup`, `launch`, `status`, `stop` actions plus a `connect` Python library API. NOT a workflow skill — owns no web-app-specific logic.
version: 0.1.0
updated: 2026-04-27
status: ready
---

Base directory for this skill: `${CLAUDE_SKILL_DIR}`

# web-control

Owns **browser automation as shared infrastructure** for the project. When other skills need to drive a Chromium-family browser under the user's corporate identity — typically because Workspace API access is denied by org admin policy — they lean on `web-control` rather than reinventing Chrome lifecycle management.

**Decision rationale + cross-platform design**: see `README.md` (full design doc) and the spawning task in `tasks/ben/117-web-control-skill.md`. **Origin signal**: see `tasks/ben/116-change-control-internal-review-tier.md` P2.6/P2.9, which validated browser automation as the workable path after corporate Workspace admin denied sensitive API scopes.

## What this skill is — and isn't

| Owns | Does NOT own |
|---|---|
| Chrome install (apt on Linux/WSL, brew/existing on macOS) | Any web-app logic (Google Docs, Drive, Confluence) — those live in consumer skills |
| Dedicated debug profile dir + first-run sign-in flow | Workflow state (review lifecycles, document classes) |
| Launcher script with canonical Chrome flags + small visible window | Headless production runs (documented as opt-in only) |
| DevTools Protocol connection helpers (Python lib) | MCP reconfiguration (uses raw CDP via Python) |
| Lifecycle: launch / status / stop, idempotent | Computer-use model integration (could swap implementation later) |

## Dependencies

| File / Tool | Required by | Purpose | How to create |
|---|---|---|---|
| `bash` + standard POSIX utils | All shell scripts | Cross-platform launcher / installer | Always available on macOS + WSL |
| `curl` | launcher, status checks | HTTP probes against `localhost:9222/json/version` | macOS pre-installed; WSL: `apt install curl` |
| `python3` (>=3.10) | Actions, lib modules | Action scripts + connection lib | Pre-installed on macOS + most Linux distros |
| `websocket-client` (Python) | `lib/connect.py` | DevTools Protocol WebSocket channel | `pip install websocket-client` (or via consumer-skill venv) |
| Chromium-family browser | All | Target of automation | Installed by `setup` action |

## Supporting Files

| File | Purpose | Status |
|---|---|---|
| `actions/setup.py` | Install Chrome (if missing), create profile dir, mark scripts executable | **Ready** |
| `actions/launch.py` | Start debug Chrome (calls `scripts/launch-debug-chrome.sh`), idempotent | **Ready** |
| `actions/status.py` | Health-check: platform / binary / profile / processes / port / sign-in heuristic | **Ready** |
| `actions/stop.py` | Terminate debug Chrome processes — only those matching our profile dir | **Ready** |
| `lib/errors.py` | `WebControlError` hierarchy with built-in recovery hints | **Ready** |
| `lib/platform.py` | Platform detection, Chrome path resolution, canonical flag list | **Ready** |
| `lib/lifecycle.py` | PID lookup, port-listening detection, kill | **Ready** |
| `lib/connect.py` | DevTools Protocol connection helpers — `connect_to_chrome`, `find_tab`, `with_page` | **Ready** |
| `lib/input.py` | Keyboard / mouse / text-input + shortcut helpers | **Ready** |
| `lib/a11y.py` | Screen-reader-mode toggle + a11y-tree text reader | **Ready** |
| `scripts/launch-debug-chrome.sh` | Cross-platform launcher (macOS + WSL/Linux), idempotent | **Ready** |
| `scripts/install-chrome-wsl.sh` | apt-based Linux/WSL installer for `google-chrome-stable` | **Ready** |
| `templates/mcp-attach-block.json` | Reference snippet for `.mcp.json` if a teammate wants chrome-devtools MCP to attach to the same debug Chrome | **Ready** |
| `tests/test-lifecycle.sh` | End-to-end smoke test: setup → launch (idempotent) → status → stop | **Ready** |
| `README.md` | Design documentation + Best Practices + troubleshooting | **Ready** |

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform.

### `setup`

Install Chrome if missing, create the dedicated debug profile dir, mark scripts executable. Idempotent — safe to re-run. Detects platform (macOS / WSL / Linux) and uses the right install path.

Output explains what's installed and the next-step command.

### `launch`

Start the debug Chrome with canonical flags. If the debug port is already responding, the action exits 0 without launching a duplicate.

First-time launch shows a visible Chrome window where the user signs in to their corporate Google account. Subsequent launches reuse the persisted session.

Required Chrome flags (see `lib/platform.py:REQUIRED_CHROME_FLAGS`):

```
--remote-debugging-port=9222
--remote-allow-origins=http://localhost:9222
--user-data-dir=$HOME/.config/google-chrome-debug
--window-size=800,700
--window-position=100,100
```

The small fixed-size window is a deliberate choice — it stays user-responsive for re-auth challenges (MFA, session expiry, FIDO2, "verify it's you" prompts) without disrupting the rest of the desktop.

### `status`

Health-check the debug Chrome:

- Platform detection
- Chrome binary path + version
- Profile dir presence
- Matching Chrome process PIDs (only ones using our profile dir — never the user's main Chrome)
- Debug port reachable (TCP connect)
- Open page tabs (sample)
- Sign-in heuristic

Exit code 0 if all green or harmlessly missing; non-zero if Chrome is missing entirely.

### `stop`

Send SIGTERM to Chrome processes matching our `--user-data-dir`. The user's main Chrome (different profile dir) is never touched. Falls back to SIGKILL after 5s if needed. Idempotent — succeeds if no matching process.

## Consumer-skill integration

Consumers declare a dependency on `web-control` and import from its lib:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "web-control"))
from lib import connect_to_chrome, find_tab, type_text, keyboard_shortcut, get_a11y_text
```

Then in the consumer flow:

```python
chrome = connect_to_chrome()              # raises ChromeNotRunning if not up
tab = chrome.find_tab(lambda t: "/document/d/" in t.url)
with chrome.with_page(tab) as page:
    page.wait_ready()
    page.eval("document.title")
    keyboard_shortcut(page, "Ctrl+Alt+M")  # opens the comment dialog in Google Docs
    type_text(page, "review note")
```

The consumer is responsible for:
- Calling `/web-control launch` (or instructing the user to) before any automation
- Surfacing re-auth prompts to the user when the session expires
- Releasing the connection (the `with_page` context manager handles the WebSocket)

The consumer is NOT responsible for:
- Chrome install, lifecycle, profile management — owned by web-control
- Knowing which platform you're on — `platform.py` abstracts that

## Notes

- **Headless is OPT-IN only.** Default is small visible window for responsiveness to re-auth. Setting `WEB_CONTROL_HEADLESS=1` in env switches to `--headless=new`. Documented caveats: corporate IdPs often block headless on first sign-in; Google's anti-abuse may detect headless fingerprints; FIDO2/security-key MFA requires a real browser.
- **Profile dir is dedicated** — `~/.config/google-chrome-debug` (override via `WEB_CONTROL_PROFILE_DIR`). Chrome's security model refuses `--remote-debugging-port` against the default profile, so this is mandatory.
- **`--remote-allow-origins` is required for Chrome 124+.** Without it, WebSocket connections from `http://localhost:9222` are 403'd.
- **Only Chrome processes matching our profile dir are killed by `stop`.** The user's main Chrome (different `--user-data-dir`) is invisible to us and untouched.
- **chrome-devtools MCP coexistence**: if a teammate has it enabled, it spawns its own isolated Chrome separate from web-control's. `templates/mcp-attach-block.json` shows how to optionally attach the MCP to web-control's debug Chrome instead.

## Best Practices

See `README.md` — consumed by `/best-practices` audit.

## Changelog

See `README.md` for version history.
