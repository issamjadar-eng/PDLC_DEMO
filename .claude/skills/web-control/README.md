# web-control — Design & Architecture

This document describes the design behind the `web-control` skill. It is **not loaded by Claude during normal skill operation** — it exists for human understanding and for future maintainers adding capabilities.

For skill usage, see `SKILL.md`. For the project-side decision history that drove this skill into existence, see `tasks/ben/116-change-control-internal-review-tier.md` (P2.6/P2.8/P2.9 captured the empirical findings) and `tasks/ben/117-web-control-skill.md` (the spawning task with scope + decisions).

---

## Why this skill exists

Browser automation is **not the goal**. It is the workable fallback when corporate IT/admin policy denies the API surface a workflow needs. The pattern is:

1. A workflow skill (e.g., `change-control` for internal review of design-controls docs) wants to operate against a Workspace surface like Google Docs.
2. Direct API access requires an OAuth scope that the Workspace admin denies for the corporate identity.
3. The user's browser, however, is allowed to access the surface — that's how they do the work day-to-day.
4. Driving the user's browser via Chrome's DevTools Protocol gets us back to the same surface, under the same corporate identity, with no admin engagement.

This pattern has multiple plausible consumers (any Workspace skill that gets API-blocked, plus skills that want to scrape user-facing dashboards or vendor portals). Hosting the lifecycle and connection layer as shared infrastructure avoids each consumer reinventing it.

**Origin story** — see `tasks/ben/116`. Probe T10 confirmed GlobalLogic's Workspace admin uses App Access Control to block sensitive scopes (Docs, Drive) for both gcloud's first-party client and likely all third-party OAuth clients, but the user's authenticated browser accesses the same surfaces with no friction.

---

## Architectural choices

### Separate skill, kept small

The discipline: `web-control` owns Chrome lifecycle + CDP fabric only. It contains **zero web-app-specific logic** — Google Docs, Confluence, Drive operations all live in consumer skills. This keeps the abstraction stable across consumers and avoids the "abstraction grew tentacles into all consumers" failure mode.

### Cross-platform: macOS + WSL/Linux

| Platform | Chrome install | Window display | Localhost |
|---|---|---|---|
| macOS | brew or pre-existing Google Chrome | Native macOS window | Native |
| WSL | apt install google-chrome-stable (Google's official repo) | WSLg — appears as Windows window | Native to WSL processes |
| Native Windows | Documented Path B alternative only — uses Windows Chrome via 0.0.0.0 + host IP, or WSL2 mirrored networking. Not the primary supported path. | n/a | Requires bridging |

We **prefer Path A (install Chrome on each platform)** over Path B (Windows Chrome bridged into WSL). Tradeoffs documented in task 116 P2.9: simpler, single code path, validated, no networking gymnastics, no security exposure of debug ports to local network.

### Dedicated debug profile dir — mandatory

Chrome's security model **refuses `--remote-debugging-port` against the default user-data-dir**. Discovered while probing in task 116 (the launcher hit `"DevTools remote debugging requires a non-default data directory"`). Implication: we cannot attach to the user's day-to-day Chrome profile; we always use a dedicated profile dir. Default location: `~/.config/google-chrome-debug` (override via `WEB_CONTROL_PROFILE_DIR`).

Side benefit: corporate creds in the dedicated profile are isolated from the user's personal browsing. If the dedicated profile gets compromised somehow, the impact is contained.

### `--remote-allow-origins` is required

Chrome 124+ rejects WebSocket connections from `http://localhost:9222` unless `--remote-allow-origins=http://localhost:9222` is passed. Without it, `Handshake status 403 Forbidden` on every CDP WebSocket connect. This was a probe-time gotcha (task 116) — bake it in.

### Small visible window — not minimized, not headless

`--window-size=800,700 --window-position=100,100`.

Rationale (task 116 P2.9): Google occasionally surfaces re-auth prompts mid-session — MFA "Verify it's you", FIDO2 challenges, post-anomaly verification, session-expiry sign-in. These appear in the doc tab and need the user to respond. A minimized or off-screen window would trap the user; fully headless triggers anti-abuse and can't complete MFA at all. Small visible is the safe default.

Headless is **opt-in via `WEB_CONTROL_HEADLESS=1`**, intended for scheduled/CI flows where no human is present and the session has already been established. Documented caveat: `--headless=new` may be detected by Google's anti-abuse and force re-auth.

### Raw CDP via Python lib, not MCP

Why not "configure chrome-devtools MCP to attach to our Chrome and consume that"?

- MCP changes require a Claude Code session restart per teammate every time debug Chrome lifecycle changes.
- Consumer skills become tightly coupled to a specific MCP version and its action surface.
- Raw CDP via `websocket-client` is a small, stable surface — `Page.navigate`, `Runtime.evaluate`, `Input.dispatchKeyEvent`, `Accessibility.getFullAXTree`. ~6 endpoints cover the entire need.

The MCP attach pattern is documented as **optional** for ad-hoc Claude inspection (`templates/mcp-attach-block.json`), separate from the consumer-skill lib API.

### Stop only matches our profile dir — never the user's main Chrome

`lib/lifecycle.py:chrome_pids()` filters by `--user-data-dir=<our profile>`. The user's personal Chrome (different user-data-dir) is invisible to us; we cannot accidentally kill it.

---

## Connector architecture

```
Consumer skill (e.g., change-control)
       │
       ├── imports lib.connect_to_chrome → returns Chrome handle
       │
       ▼
.claude/skills/web-control/lib/
├── connect.py    — Chrome / Page / Tab / connect_to_chrome / find_tab / with_page
├── input.py      — keyboard / mouse / text-insert / shortcut helpers
├── a11y.py       — SR-mode toggle + Accessibility.getFullAXTree wrapper (read body text)
├── platform.py   — detect_platform / chrome_binary_path / profile_dir / canonical flags
├── lifecycle.py  — chrome_pids / is_debug_port_listening / kill_chrome
└── errors.py     — WebControlError hierarchy with built-in recovery hints

       │
       ▼
http://localhost:9222
       │
       ▼
       Chrome (debug Chrome, dedicated profile, signed in to corporate Google)
```

The lifecycle layer (actions/) is operationally independent — `setup` / `launch` / `status` / `stop` are entry points users invoke. The lib/ layer is what consumer skills import.

---

## Extensibility seams (designed in)

1. **`connect.Page`**: low-level CDP wrapper. Add new helpers (e.g., `take_screenshot`, `wait_for_selector`) by extending Page methods or composing thin functions over `cmd()`.
2. **`input.keyboard_shortcut`**: friendly shortcut parser. Add new named keys to the dict; chord notation (`Ctrl+Alt+M`) handled.
3. **`a11y.get_a11y_text`**: filter by role; pass `role_filter=()` to widen. Add new helpers (e.g., `get_aria_landmarks`) on top.
4. **Platform detection**: add new platforms in `platform.detect_platform()`. Mac/WSL/Linux today; native Windows (via WSL Path B) explicitly out for now.
5. **Computer-use model swap**: if Anthropic's computer-use becomes the better path for some workflows, consumer skills can switch implementations behind the same `connect_to_chrome` interface — the contract is "give me a thing I can drive with `eval()` / `click()` / `type_text()`".

---

## Configuration via environment variables

| Variable | Purpose | Default |
|---|---|---|
| `WEB_CONTROL_PORT` | Debug port | `9222` |
| `WEB_CONTROL_PROFILE_DIR` | User-data-dir path | `~/.config/google-chrome-debug` |
| `WEB_CONTROL_BROWSER` | Path to chrome binary (override auto-detect) | (auto-detected) |
| `WEB_CONTROL_HEADLESS` | Set to `1` to enable `--headless=new` | (empty / headed) |
| `WEB_CONTROL_LAUNCH_URL` | URL to load on launch | `https://drive.google.com` |

---

## Re-authentication flow

When the user's corporate Google session expires (default ~14d, admin-configurable):

1. Consumer-skill code calls `connect_to_chrome()` and tries an operation
2. `is_signed_in(page)` returns False (URL redirects to `accounts.google.com`)
3. Consumer surfaces "session expired — please sign in in the visible Chrome window"
4. User completes sign-in in the visible debug Chrome
5. Consumer retries the operation

Sign-in cookies persist across `web-control stop` + `launch` cycles (validated in task 116 (C)).

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `web-control launch` says debug port already responding, but my consumer-skill code can't connect | Either it's responding (success — you can connect) OR something else is bound to 9222 | `web-control status` reports tab health; if it lists `<unrelated tabs>`, something else is on 9222 — `WEB_CONTROL_PORT=9223 web-control launch` |
| Chrome window opens but never gets the debug port up | Chrome silently rejected debug-port flag (e.g., default profile) | Check log: `${TMPDIR:-/tmp}/web-control-chrome.log`. Most common: someone overrode `WEB_CONTROL_PROFILE_DIR` to the default Chrome profile |
| `Handshake status 403 Forbidden` on WebSocket | Chrome version too old or `--remote-allow-origins` missing | `web-control setup` re-checks; if old Chrome, upgrade |
| WSL Chrome not visible on desktop | WSLg not installed / not enabled | `wsl --update` on Windows side |
| `web-control status` says "no chrome processes" but I see a Chrome window | The visible Chrome is the user's personal Chrome (different profile dir). Our debug Chrome isn't running. | `web-control launch` |
| First-time sign-in fails with "this browser doesn't support the sign-in form" | Old Chromium release missing the necessary FedCM features | Upgrade Chrome via `web-control setup` (or apt upgrade google-chrome-stable) |
| Sign-in works but redirects somewhere unexpected | Workspace admin policy intercepts sign-in (e.g., enforced device trust). Probably also blocks browser automation regardless of skill. | Consult IT — this is a tenant-level policy, not a skill bug |

---

## Best Practices

These checks are intended to be picked up by `/best-practices`:

| Check | Severity | Description |
|---|---|---|
| `web-control: launcher is executable` | Required | `scripts/launch-debug-chrome.sh` is `+x` |
| `web-control: installer is executable` | Required | `scripts/install-chrome-wsl.sh` is `+x` |
| `web-control: profile dir convention documented` | Required | `~/.config/google-chrome-debug` referenced consistently |
| `web-control: errors carry recovery hints` | Required | Every subclass of `WebControlError` defines `recovery` |
| `web-control: tests exist and pass` | Required | `tests/test-lifecycle.sh` runs and exits 0 |
| `web-control: setup is idempotent` | Required | Re-running `setup` produces no diff after first run |
| `web-control: stop only kills our profile` | Critical | `kill_chrome` filters by user-data-dir — never matches user's main Chrome |
| `web-control: required Chrome flags include `--remote-allow-origins`` | Required | `REQUIRED_CHROME_FLAGS` returns the flag |
| `web-control: small visible window default` | Recommended | `--window-size=800,700` present unless `WEB_CONTROL_HEADLESS=1` |
| `web-control: README troubleshooting matrix exists` | Recommended | This file has the table above with at least 5 rows |

---

## Roadmap

| Version | Scope |
|---|---|
| 0.1.0 (initial) | Setup / launch / status / stop actions; lib API for connect / input / a11y; cross-platform launcher; tests pass |
| 0.2.x | Add `WEB_CONTROL_PORT`-aware port-conflict detection; structured launch log; `--reset` flag for setup |
| 0.3.x | Optional `Accessibility.enable` autopilot — consumer requests body text and we toggle SR mode + query a11y tree on demand |
| 0.4.x | First-class headless-with-recording mode (screenshot + DOM dumps each step) for QA evidence |
| 0.5.x | Computer-use model swap layer — alt implementation behind same `connect_to_chrome` contract |
| Later | Multi-tab orchestration, advisory locking for concurrent consumers, structured audit log to `~/.config/web-control/log/` |

---

## Changelog

- **0.1.0** (2026-04-27): Initial release. Cross-platform (macOS + WSL/Linux). 4 user-facing actions (`setup` / `launch` / `status` / `stop`) + Python lib API (`connect_to_chrome`, `find_tab`, `with_page`, `send_key`, `click_at`, `type_text`, `keyboard_shortcut`, `get_a11y_text`, `is_signed_in`). Validated end-to-end in task 116 probes (sign-in, type, comment, resolve, session persistence, body-text via SR mode + a11y tree). 8 of 8 tests in `tests/test-lifecycle.sh` pass. Best Practices section consumed by `/best-practices`. Origin: task 117.
