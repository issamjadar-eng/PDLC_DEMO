#!/usr/bin/env bash
# Launch the dedicated debug Chrome with the canonical web-control flags.
# Cross-platform: macOS + Linux/WSL.
#
# Idempotent: if the debug Chrome is already running against this profile
# dir, the script reports its state and exits 0 instead of launching a
# duplicate.
#
# Reads (env, optional):
#   WEB_CONTROL_PORT          Debug port (default: 9222)
#   WEB_CONTROL_PROFILE_DIR   Profile dir (default: ~/.config/google-chrome-debug)
#   WEB_CONTROL_BROWSER       Path to chrome binary (default: auto-detect)
#   WEB_CONTROL_HEADLESS      "1" to enable --headless=new (default: empty/headed)

set -euo pipefail

PORT="${WEB_CONTROL_PORT:-9222}"
PROFILE="${WEB_CONTROL_PROFILE_DIR:-$HOME/.config/google-chrome-debug}"
HEADLESS="${WEB_CONTROL_HEADLESS:-}"

# ---------- Detect platform ----------

case "$(uname -s)" in
  Darwin)  PLAT=macos ;;
  Linux)   PLAT=linux
           if grep -qiE 'microsoft|wsl' /proc/version 2>/dev/null; then
             PLAT=wsl
           fi ;;
  *)       echo "ERROR: unsupported platform: $(uname -s)" >&2
           echo "  -> web-control supports macOS and Linux/WSL." >&2
           exit 64 ;;
esac

# ---------- Resolve Chrome binary ----------

resolve_chrome() {
  if [ -n "${WEB_CONTROL_BROWSER:-}" ]; then
    if [ -x "$WEB_CONTROL_BROWSER" ]; then
      echo "$WEB_CONTROL_BROWSER"
      return 0
    fi
    echo "ERROR: WEB_CONTROL_BROWSER=$WEB_CONTROL_BROWSER is not executable" >&2
    return 1
  fi

  case "$PLAT" in
    macos)
      for c in \
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" \
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"; do
        [ -x "$c" ] && { echo "$c"; return 0; }
      done ;;
    linux|wsl)
      for c in \
        /usr/bin/google-chrome \
        /usr/bin/google-chrome-stable \
        /usr/bin/chromium-browser \
        /usr/bin/chromium \
        /snap/bin/chromium; do
        [ -x "$c" ] && { echo "$c"; return 0; }
      done
      for n in google-chrome google-chrome-stable chromium chromium-browser; do
        if command -v "$n" >/dev/null 2>&1; then
          command -v "$n"
          return 0
        fi
      done ;;
  esac

  echo "ERROR: no Chrome-family browser found on $PLAT" >&2
  echo "  -> Run: /web-control setup    (installs Chrome if missing)" >&2
  return 1
}

CHROME="$(resolve_chrome)"
[ -z "$CHROME" ] && exit 64

# ---------- Idempotency: if already up on the right profile + port, do nothing ----------

if curl -sSf -m 2 "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
  echo "web-control: debug Chrome already responding on port ${PORT}"
  echo "  Profile: ${PROFILE}"
  echo "  -> Skipping launch (idempotent)."
  exit 0
fi

# ---------- Make profile dir ----------

mkdir -p "$PROFILE"

# ---------- Build flag list ----------

FLAGS=(
  "--remote-debugging-port=${PORT}"
  "--remote-allow-origins=http://localhost:${PORT}"
  "--user-data-dir=${PROFILE}"
  "--window-size=800,700"
  "--window-position=100,100"
)

if [ -n "$HEADLESS" ]; then
  FLAGS+=("--headless=new")
  # Disable GPU is generally a good companion for headless on Linux
  case "$PLAT" in
    linux|wsl) FLAGS+=("--disable-gpu") ;;
  esac
fi

# Default landing URL (Drive home is a reasonable starting point)
URL="${WEB_CONTROL_LAUNCH_URL:-https://drive.google.com}"

# ---------- Launch ----------

echo "web-control: launching debug Chrome"
echo "  Binary:  $CHROME"
echo "  Port:    $PORT"
echo "  Profile: $PROFILE"
echo "  URL:     $URL"

# Detach completely from the controlling terminal so the process survives the
# parent's exit. setsid is available on Linux + WSL; on macOS we use a
# nohup + disown idiom.
LAUNCH_LOG="${TMPDIR:-/tmp}/web-control-chrome.log"

if command -v setsid >/dev/null 2>&1; then
  setsid "$CHROME" "${FLAGS[@]}" "$URL" </dev/null >"$LAUNCH_LOG" 2>&1 &
else
  # macOS: setsid not always available — use nohup + disown
  nohup "$CHROME" "${FLAGS[@]}" "$URL" </dev/null >"$LAUNCH_LOG" 2>&1 &
  disown 2>/dev/null || true
fi

# ---------- Wait for the debug port to become reachable ----------

for _ in $(seq 1 20); do
  if curl -sSf -m 1 "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
    echo "web-control: debug Chrome is up on port ${PORT}"
    echo "  Log: $LAUNCH_LOG"
    exit 0
  fi
  sleep 0.5
done

echo "ERROR: debug Chrome failed to expose port ${PORT} within 10s" >&2
echo "  Log tail:" >&2
tail -20 "$LAUNCH_LOG" >&2 || true
echo "" >&2
echo "  Diagnostic suggestions:" >&2
echo "  1. Check whether Chrome printed an error in the log above" >&2
echo "  2. Re-check binary path:    $CHROME --version" >&2
echo "  3. Verify profile is writable: ls -ld $PROFILE" >&2
echo "  4. Run /web-control status   (independently checks port + processes)" >&2
exit 1
