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

# Install
$SUDO apt-get update -qq
$SUDO apt-get install -y google-chrome-stable

google-chrome --version
echo "web-control: install complete"
