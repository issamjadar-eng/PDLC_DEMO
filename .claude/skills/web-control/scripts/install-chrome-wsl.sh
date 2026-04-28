#!/usr/bin/env bash
# Install google-chrome-stable on Linux/WSL via Google's official apt repo.
# Idempotent: skips if already installed.
#
# Requires sudo for apt operations.

set -euo pipefail

if command -v google-chrome >/dev/null 2>&1; then
  echo "web-control: google-chrome already installed at $(command -v google-chrome)"
  google-chrome --version
  exit 0
fi

if ! grep -qiE 'microsoft|wsl|linux' /proc/version 2>/dev/null; then
  echo "ERROR: this installer only runs on Linux/WSL" >&2
  exit 64
fi

if [ "$(id -u)" -ne 0 ] && ! command -v sudo >/dev/null 2>&1; then
  echo "ERROR: must run as root or have sudo available" >&2
  exit 64
fi

SUDO=""
[ "$(id -u)" -ne 0 ] && SUDO="sudo"

echo "web-control: installing google-chrome-stable from Google's official apt repo"

# Add the signing key
$SUDO install -m 0755 -d /etc/apt/keyrings
TEMP_KEY="$(mktemp)"
curl -fsSL https://dl.google.com/linux/linux_signing_key.pub -o "$TEMP_KEY"
$SUDO gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg "$TEMP_KEY"
$SUDO chmod a+r /etc/apt/keyrings/google-chrome.gpg
rm -f "$TEMP_KEY"

# Add the apt source
echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] https://dl.google.com/linux/chrome/deb/ stable main' \
  | $SUDO tee /etc/apt/sources.list.d/google-chrome.list >/dev/null

# Install Chrome + the runtime libs Chrome needs on Ubuntu 24.04+ (the
# t64-suffixed packages are the time_t-64bit transitional names; on older
# Ubuntu the unsuffixed names work and apt resolves to whatever is present).
$SUDO apt-get update -qq

# Try the t64 names first (Ubuntu 24.04+). If unavailable, fall back to
# unsuffixed names (Ubuntu 22.04 and earlier, Debian).
RUNTIME_DEPS_T64="libgtk-3-0t64 libasound2t64 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64"
RUNTIME_DEPS_BASE="libnss3 libgbm1 libxss1 libdrm2 fonts-liberation libxkbcommon0 libpango-1.0-0"

if $SUDO apt-get install -y --simulate $RUNTIME_DEPS_T64 >/dev/null 2>&1; then
    $SUDO apt-get install -y $RUNTIME_DEPS_T64 $RUNTIME_DEPS_BASE google-chrome-stable
else
    # Pre-24.04 names
    RUNTIME_DEPS_LEGACY="libgtk-3-0 libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2"
    $SUDO apt-get install -y $RUNTIME_DEPS_LEGACY $RUNTIME_DEPS_BASE google-chrome-stable
fi

# Python deps for web-control's CDP runtime (system-wide via apt — avoids
# PEP 668 / --break-system-packages issues)
$SUDO apt-get install -y python3-websocket python3-yaml

google-chrome --version
echo "web-control: install complete"
