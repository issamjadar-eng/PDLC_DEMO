#!/usr/bin/env bash
# =============================================================================
# PDLC_DEMO — Development Environment Setup Script
#
# Works on macOS and Linux (WSL/Ubuntu). Installs and configures:
#   - Homebrew (package manager)
#   - Node.js + npm
#   - Git (with identity and SSH key)
#   - GitHub CLI (gh)
#   - Claude Code CLI
#   - VS Code extensions
#   - Document processing tools (pandoc, poppler, qpdf, LibreOffice, Python+uv)
#   - web-control browser-automation infrastructure (if the skill is installed)
#   - file-locator semantic-search MCP venv (if the tool is present)
#
# Usage:
#   bash setup.sh          # Run all steps
#   bash setup.sh --check  # Check what's installed without changing anything
#
# Things this script does NOT do (require manual steps):
#   - Install VS Code (native GUI app)
#   - Install WSL on Windows (requires admin PowerShell + restart)
#   - Create GitHub or Claude accounts (browser)
#   - Install Claude Desktop or Google Drive Desktop (native GUI apps)
#   - Upload SSH key to GitHub (browser — automated only if gh is authenticated)
#   - Authenticate gh and GitHub SSH (interactive)
#   - Clone the repository (needs access first)
#   - Confirm Claude training opt-out and 2FA attestations (handled by /secops attest)
#
# See setup.md for the full guide including manual steps.
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Colors and output helpers
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No color

info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; }
step()    { echo -e "\n${BOLD}── $* ──${NC}"; }

# ---------------------------------------------------------------------------
# OS detection
# ---------------------------------------------------------------------------
detect_os() {
    case "$(uname -s)" in
        Darwin) OS="mac" ;;
        Linux)
            if grep -qi microsoft /proc/version 2>/dev/null; then
                OS="wsl"
            else
                OS="linux"
            fi
            ;;
        *)
            error "Unsupported operating system: $(uname -s)"
            error "This script supports macOS and Linux (including WSL)."
            exit 1
            ;;
    esac
    success "Detected OS: $OS"
}

# ---------------------------------------------------------------------------
# Check-only mode
# ---------------------------------------------------------------------------
check_only=false
if [[ "${1:-}" == "--check" ]]; then
    check_only=true
    echo -e "${BOLD}Running in check-only mode — no changes will be made.${NC}\n"
fi

# Track whether SSH key was successfully added to GitHub during this run
ssh_key_on_github=false

# ---------------------------------------------------------------------------
# Helper: check if a command exists
# ---------------------------------------------------------------------------
has_command() {
    command -v "$1" &>/dev/null
}

# ---------------------------------------------------------------------------
# Helper: prompt yes/no (defaults to yes)
# ---------------------------------------------------------------------------
ask_yes() {
    local prompt="$1"
    local answer
    read -rp "$(echo -e "${YELLOW}$prompt [Y/n]${NC} ")" answer
    [[ -z "$answer" || "$answer" =~ ^[Yy] ]]
}

# ---------------------------------------------------------------------------
# Helper: prompt for input with a default value
# ---------------------------------------------------------------------------
ask_input() {
    local prompt="$1"
    local default="${2:-}"
    local answer
    if [[ -n "$default" ]]; then
        read -rp "$(echo -e "${YELLOW}$prompt${NC} [$default]: ")" answer
        echo "${answer:-$default}"
    else
        read -rp "$(echo -e "${YELLOW}$prompt${NC}: ")" answer
        echo "$answer"
    fi
}

# ---------------------------------------------------------------------------
# Step: Homebrew
# ---------------------------------------------------------------------------
install_homebrew() {
    step "Homebrew"

    if has_command brew; then
        success "Homebrew is already installed: $(brew --version | head -1)"
        return 0
    fi

    if $check_only; then
        warn "Homebrew is NOT installed"
        return 0
    fi

    info "Installing Homebrew..."
    NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add brew to PATH for the current session
    if [[ "$OS" == "mac" ]]; then
        if [[ -f /opt/homebrew/bin/brew ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f /usr/local/bin/brew ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    else
        # Linux / WSL
        if [[ -f /home/linuxbrew/.linuxbrew/bin/brew ]]; then
            eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

            # Persist to shell profile
            local shell_profile
            if [[ -f "$HOME/.bashrc" ]]; then
                shell_profile="$HOME/.bashrc"
            elif [[ -f "$HOME/.zshrc" ]]; then
                shell_profile="$HOME/.zshrc"
            else
                shell_profile="$HOME/.bashrc"
            fi

            if ! grep -q 'linuxbrew' "$shell_profile" 2>/dev/null; then
                info "Adding Homebrew to $shell_profile..."
                echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> "$shell_profile"
            fi
        fi
    fi

    if has_command brew; then
        success "Homebrew installed: $(brew --version | head -1)"
    else
        error "Homebrew installation completed but 'brew' is not in PATH."
        error "Close this terminal, open a new one, and run this script again."
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# Step: WSL browser bridge (WSL only)
# ---------------------------------------------------------------------------
setup_wsl_browser() {
    if [[ "$OS" != "wsl" ]]; then
        return 0
    fi

    step "WSL Browser Bridge"

    # On WSL, CLI tools (gh auth login, claude, etc.) need BROWSER set to open
    # the Windows browser. We use explorer.exe which is already available in WSL
    # via Windows interop — no extra packages needed.

    # Verify explorer.exe is reachable (confirms Windows interop is working)
    if ! has_command explorer.exe; then
        if $check_only; then
            warn "explorer.exe not found in WSL — Windows interop may be disabled."
            warn "Commands like 'gh auth login' will print a URL instead of opening a browser."
        else
            warn "explorer.exe not found in WSL."
            warn "This usually means Windows-WSL interop is disabled."
            warn "To enable it, add this to /etc/wsl.conf and restart WSL (wsl --shutdown):"
            echo ""
            echo -e "  ${BOLD}[interop]${NC}"
            echo -e "  ${BOLD}enabled=true${NC}"
            echo ""
            warn "Until then, commands like 'gh auth login' will print a URL — copy it and open manually."
        fi
        return 0
    fi

    success "explorer.exe is reachable from WSL — Windows interop is working."

    # Configure BROWSER=explorer.exe in shell profile
    local shell_profile="$HOME/.bashrc"
    if [[ "$(basename "$SHELL")" == "zsh" ]]; then
        shell_profile="$HOME/.zshrc"
    fi

    # Clean up any old wslview config from previous setup runs
    if grep -qF 'BROWSER=wslview' "$shell_profile" 2>/dev/null; then
        grep -v 'BROWSER=wslview' "$shell_profile" > "$shell_profile.tmp" \
            && mv "$shell_profile.tmp" "$shell_profile"
        grep -v '# WSL: open URLs in Windows default browser' "$shell_profile" > "$shell_profile.tmp" \
            && mv "$shell_profile.tmp" "$shell_profile"
        info "Removed old BROWSER=wslview from $shell_profile"
    fi

    local browser_line='export BROWSER=explorer.exe'

    if grep -qF "$browser_line" "$shell_profile" 2>/dev/null; then
        success "BROWSER=explorer.exe already configured in $shell_profile"
    else
        if $check_only; then
            warn "BROWSER is not set in $shell_profile"
            return 0
        fi

        echo "" >> "$shell_profile"
        echo "# WSL: open URLs in Windows default browser (for gh auth, claude, etc.)" >> "$shell_profile"
        echo "$browser_line" >> "$shell_profile"
        success "Added BROWSER=explorer.exe to $shell_profile"
    fi

    # Apply for current session
    export BROWSER=explorer.exe
}

# ---------------------------------------------------------------------------
# Step: VS Code CLI (code command)
# ---------------------------------------------------------------------------
setup_code_cli() {
    step "VS Code CLI"

    if has_command code; then
        success "'code' command is available."
        return 0
    fi

    if [[ "$OS" == "mac" ]]; then
        local vscode_bin="/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
        if [[ -x "$vscode_bin" ]]; then
            if $check_only; then
                warn "'code' CLI not in PATH, but VS Code is installed. Can be fixed by creating a symlink."
                return 0
            fi

            info "VS Code found but 'code' CLI is not in PATH. Creating symlink..."

            if [[ -d /usr/local/bin ]]; then
                if ln -s "$vscode_bin" /usr/local/bin/code 2>/dev/null; then
                    success "'code' symlinked to /usr/local/bin/code"
                else
                    info "Needs elevated permissions. Trying with sudo..."
                    if sudo ln -s "$vscode_bin" /usr/local/bin/code 2>/dev/null; then
                        success "'code' symlinked to /usr/local/bin/code"
                    else
                        warn "Could not create symlink in /usr/local/bin."
                        info "Adding VS Code bin directory to your PATH instead..."
                        local vscode_dir
                        vscode_dir="$(dirname "$vscode_bin")"
                        local shell_profile="$HOME/.zshrc"
                        [[ ! -f "$shell_profile" ]] && shell_profile="$HOME/.bashrc"
                        if ! grep -q "Visual Studio Code" "$shell_profile" 2>/dev/null; then
                            echo "export PATH=\"$vscode_dir:\$PATH\"" >> "$shell_profile"
                            export PATH="$vscode_dir:$PATH"
                            success "Added VS Code to PATH in $shell_profile"
                        fi
                    fi
                fi
            fi
        else
            if $check_only; then
                warn "'code' CLI not found. Install VS Code first, then re-run."
            else
                warn "VS Code not found at /Applications/Visual Studio Code.app"
                warn "Install VS Code first, then re-run this script."
            fi
        fi
    elif [[ "$OS" == "wsl" ]]; then
        if $check_only; then
            warn "'code' CLI not found. Make sure VS Code is installed on Windows with 'Add to PATH' enabled."
        else
            warn "'code' not found in WSL. This usually means:"
            warn "  1. VS Code is not installed on Windows, OR"
            warn "  2. 'Add to PATH' was not checked during VS Code install"
            warn "Reinstall VS Code on Windows and check 'Add to PATH', then restart WSL."
        fi
    else
        if $check_only; then
            warn "'code' CLI not found."
        else
            warn "'code' CLI not found. Install VS Code and add it to your PATH."
        fi
    fi
}

# ---------------------------------------------------------------------------
# Helper: verify LibreOffice headless mode actually works
# ---------------------------------------------------------------------------
# Presence on PATH is not enough — some WSL distros install soffice but lack
# fontconfig / cups / java runtime and headless conversion fails at first use.
# We smoke-test by converting a small text file to PDF. Returns 0 on success.
# ---------------------------------------------------------------------------
verify_soffice_headless() {
    if ! has_command soffice; then
        return 1
    fi

    local tmpdir
    tmpdir=$(mktemp -d /tmp/soffice-verify-XXXXXX)
    local smoke="$tmpdir/smoke.txt"
    echo "Docflow smoke test — confirms soffice headless rendering works." > "$smoke"

    local log="$tmpdir/soffice.log"
    if soffice --headless --convert-to pdf --outdir "$tmpdir" "$smoke" >"$log" 2>&1 \
       && [[ -f "$tmpdir/smoke.pdf" ]]; then
        success "LibreOffice headless rendering verified ($(soffice --headless --version 2>/dev/null | head -1))"
        rm -rf "$tmpdir"
        return 0
    else
        warn "LibreOffice is on PATH but headless rendering failed."
        warn "  Diagnostic: $(head -5 "$log" 2>/dev/null | tr '\n' ' ')"
        warn "  Common fixes:"
        warn "    sudo apt install -y fontconfig libreoffice-core  # missing runtime deps"
        warn "    sudo apt install -y default-jre                  # Java runtime for some filters"
        rm -rf "$tmpdir"
        return 1
    fi
}

# ---------------------------------------------------------------------------
# Step: Brew packages (Node.js, Git, GitHub CLI, jq) + Document tools
# ---------------------------------------------------------------------------
install_brew_packages() {
    step "Brew Packages (Node.js, Git, GitHub CLI, jq)"

    # Core tools — required for development workflow and hook scripts
    local core_packages=(node git gh jq)
    local packages_to_install=()

    for pkg in "${core_packages[@]}"; do
        local cmd="$pkg"
        [[ "$pkg" == "node" ]] && cmd="node"
        [[ "$pkg" == "gh" ]] && cmd="gh"

        if has_command "$cmd"; then
            case "$cmd" in
                node) success "Node.js is already installed: $(node --version)" ;;
                git)  success "Git is already installed: $(git --version)" ;;
                gh)   success "GitHub CLI is already installed: $(gh --version | head -1)" ;;
                jq)   success "jq is already installed: $(jq --version)" ;;
            esac
        else
            if $check_only; then
                warn "$pkg is NOT installed"
            else
                packages_to_install+=("$pkg")
            fi
        fi
    done

    if $check_only; then
        if has_command npm; then
            success "npm is available: $(npm --version)"
        else
            warn "npm is NOT available (installed with Node.js)"
        fi
    fi

    # Document processing tools — needed by /docflow, /pdf, /xlsx, /docx skills
    step "Document Processing Tools (pandoc, poppler, qpdf, LibreOffice, Python 3, uv)"

    local doc_packages=()
    local brew_doc_checks=(
        "pandoc:pandoc"
        "poppler:pdftotext"
        "qpdf:qpdf"
        "python3:python3"
        "uv:uv"
    )

    for entry in "${brew_doc_checks[@]}"; do
        local pkg="${entry%%:*}"
        local cmd="${entry##*:}"

        if has_command "$cmd"; then
            case "$cmd" in
                pandoc)    success "pandoc is already installed: $(pandoc --version | head -1)" ;;
                pdftotext) success "poppler is already installed (pdftotext available)" ;;
                qpdf)      success "qpdf is already installed: $(qpdf --version | head -1)" ;;
                python3)   success "Python 3 is already installed: $(python3 --version)" ;;
                uv)        success "uv is already installed: $(uv --version)" ;;
            esac
        else
            if $check_only; then
                warn "$pkg is NOT installed (needed by document processing skills)"
            else
                doc_packages+=("$pkg")
            fi
        fi
    done

    # LibreOffice — brew cask on Mac, apt on Linux/WSL
    # Required by /docflow (DOC→DOCX, DOCX→PDF rendered pagination), /pptx,
    # and EMF/WMF→PNG image conversion. Full suite incl. impress for PPTX.
    if has_command soffice; then
        if $check_only; then
            verify_soffice_headless || warn "LibreOffice is on PATH but headless mode is broken — conversions will fail"
        else
            success "LibreOffice is already installed"
            verify_soffice_headless || warn "Re-run the install commands above or file a setup issue"
        fi
    else
        if $check_only; then
            warn "LibreOffice is NOT installed (needed by /docflow, /pptx, /docx skills)"
        else
            if [[ "$OS" == "mac" ]]; then
                doc_packages+=("libreoffice")  # brew --cask bundles the full suite incl. Impress
            else
                info "Installing LibreOffice via apt (brew cask not available on Linux)..."
                if sudo apt update -qq && sudo apt install -y \
                        libreoffice-common \
                        libreoffice-core \
                        libreoffice-writer \
                        libreoffice-calc \
                        libreoffice-impress; then
                    if has_command soffice; then
                        success "LibreOffice installed"
                        verify_soffice_headless || warn "Install reports success but smoke test failed — see diagnostic above"
                    else
                        warn "apt install returned success but soffice is still not on PATH"
                    fi
                else
                    warn "LibreOffice apt install failed — check sudo credentials and /etc/apt/sources.list"
                fi
            fi
        fi
    fi

    if $check_only; then
        return 0
    fi

    # Install all missing brew packages in one call
    local all_packages=("${packages_to_install[@]}" "${doc_packages[@]}")

    if [[ ${#all_packages[@]} -eq 0 ]]; then
        info "All brew packages already installed."
    else
        info "Installing: ${all_packages[*]}..."
        brew install "${all_packages[@]}"
    fi

    # Verify core packages
    for pkg in "${packages_to_install[@]}"; do
        case "$pkg" in
            node) has_command node && success "Node.js installed: $(node --version)" || error "Node.js installation failed." ;;
            git)  has_command git  && success "Git installed: $(git --version)"       || error "Git installation failed." ;;
            gh)   has_command gh   && success "GitHub CLI installed: $(gh --version | head -1)" || error "GitHub CLI installation failed." ;;
            jq)   has_command jq   && success "jq installed: $(jq --version)"        || error "jq installation failed." ;;
        esac
    done

    # Verify brew doc packages
    for pkg in "${doc_packages[@]}"; do
        case "$pkg" in
            pandoc)      has_command pandoc    && success "pandoc installed"      || warn "pandoc installation failed." ;;
            poppler)     has_command pdftotext && success "poppler installed"     || warn "poppler installation failed." ;;
            qpdf)        has_command qpdf      && success "qpdf installed"       || warn "qpdf installation failed." ;;
            libreoffice) has_command soffice   && (success "LibreOffice installed"; verify_soffice_headless || true) || warn "LibreOffice installation failed." ;;
            python3)     has_command python3   && success "Python 3 installed"   || warn "Python 3 installation failed." ;;
            uv)          has_command uv        && success "uv installed: $(uv --version)" || warn "uv installation failed." ;;
        esac
    done
}

# ---------------------------------------------------------------------------
# Step: Python packages (for document processing skills)
# ---------------------------------------------------------------------------
install_python_packages() {
    step "Python Packages (document processing)"

    if ! has_command python3; then
        warn "Python 3 not available — skipping Python package installation."
        return 0
    fi

    if ! has_command pip3 && ! python3 -m pip --version &>/dev/null; then
        if $check_only; then
            warn "pip3 is NOT available"
            return 0
        fi
        info "Installing pip..."
        python3 -m ensurepip --upgrade 2>/dev/null || sudo apt install -y python3-pip 2>/dev/null || brew install python3
    fi

    # Packages needed by /pdf, /xlsx, /docx, /docflow skills
    local pip_packages=(
        pypdf
        pdf2image
        pdfplumber
        reportlab
        pandas
        openpyxl
        python-docx
        lxml
        defusedxml
        Pillow
    )

    if $check_only; then
        local missing=()
        for pkg in "${pip_packages[@]}"; do
            if ! python3 -c "import ${pkg//-/_}" 2>/dev/null; then
                missing+=("$pkg")
            fi
        done
        if [[ ${#missing[@]} -eq 0 ]]; then
            success "All Python packages are installed."
        else
            warn "Missing Python packages: ${missing[*]}"
        fi
        return 0
    fi

    info "Installing Python packages: ${pip_packages[*]}..."
    python3 -m pip install --quiet --break-system-packages "${pip_packages[@]}" 2>/dev/null \
        || python3 -m pip install --quiet "${pip_packages[@]}" 2>/dev/null \
        || pip3 install --quiet "${pip_packages[@]}" 2>/dev/null

    if [[ $? -eq 0 ]]; then
        success "Python packages installed."
    else
        warn "Some Python packages may not have installed. Run manually:"
        warn "  pip3 install ${pip_packages[*]}"
    fi
}

# ---------------------------------------------------------------------------
# Browser automation (web-control skill) — OPTIONAL
#
# Only relevant if the web-control skill is installed at .claude/skills/web-control/.
# In PDLC_DEMO web-control drives a dedicated debug Chrome via CDP for skills
# that need to operate under the user's corporate Google identity. Idempotent:
# skips if Chrome already present and skill has been set up.
#
# What this does:
#   - Installs google-chrome-stable (Linux/WSL via the skill's installer;
#     macOS via Homebrew cask if Chrome isn't already at /Applications)
#   - Installs Python websocket-client + pyyaml (consumer skills use websocket
#     for the DevTools Protocol; pyyaml for config parsing)
#   - Runs `python3 .claude/skills/web-control/actions/setup.py` to create
#     the dedicated debug profile dir and mark scripts executable
# ---------------------------------------------------------------------------
setup_web_control() {
    step "Browser Automation (web-control skill) — Optional"

    local skill_dir
    skill_dir="$(dirname "$0")/.claude/skills/web-control"
    if [[ ! -d "$skill_dir" ]]; then
        skill_dir="$PWD/.claude/skills/web-control"
    fi

    if [[ ! -d "$skill_dir" ]]; then
        info "web-control skill not present — skipping (this is fine if you don't need browser automation)."
        return 0
    fi

    # 1. Detect Chrome
    local chrome_bin=""
    if [[ "$OS" == "mac" ]]; then
        if [[ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]]; then
            chrome_bin="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        fi
    else
        for c in /usr/bin/google-chrome /usr/bin/google-chrome-stable; do
            [[ -x "$c" ]] && { chrome_bin="$c"; break; }
        done
    fi

    if [[ -n "$chrome_bin" ]]; then
        success "Chrome already installed: $chrome_bin"
    else
        if $check_only; then
            warn "Chrome is NOT installed (web-control depends on it)"
        else
            if [[ "$OS" == "mac" ]]; then
                if has_command brew; then
                    info "Installing Google Chrome via brew..."
                    brew install --cask google-chrome 2>&1 | tail -5 || warn "brew install --cask google-chrome had issues — you may need to install manually."
                else
                    warn "Homebrew not available — install Chrome manually from https://www.google.com/chrome/"
                fi
            else
                # Linux / WSL — use the skill's installer
                if [[ -x "$skill_dir/scripts/install-chrome-wsl.sh" ]]; then
                    info "Installing google-chrome-stable via web-control's installer..."
                    bash "$skill_dir/scripts/install-chrome-wsl.sh" || warn "Chrome install had issues."
                else
                    warn "web-control installer script missing or not executable: $skill_dir/scripts/install-chrome-wsl.sh"
                fi
            fi
        fi
    fi

    # 2. Python deps (websocket-client + pyyaml)
    if has_command python3; then
        local missing_py=""
        python3 -c "import websocket" 2>/dev/null || missing_py="$missing_py websocket"
        python3 -c "import yaml"      2>/dev/null || missing_py="$missing_py yaml"
        if [[ -z "$missing_py" ]]; then
            success "Python deps available (websocket-client, pyyaml)"
        else
            if $check_only; then
                warn "Python deps NOT installed:$missing_py"
            else
                info "Installing Python deps for web-control..."
                if [[ "$OS" == "linux" || "$OS" == "wsl" ]]; then
                    sudo apt-get install -y python3-websocket python3-yaml \
                        2>&1 | tail -3 || warn "apt install failed; manual: sudo apt-get install python3-websocket python3-yaml"
                else
                    python3 -m pip install --user websocket-client pyyaml 2>&1 | tail -3 \
                        || warn "pip install failed; manual: pip3 install --user websocket-client pyyaml"
                fi
            fi
        fi
    fi

    # 3. WSLg sanity check (Linux/WSL only — catches Win10 and old WSL)
    if [[ "$OS" == "wsl" ]]; then
        if [[ -d /mnt/wslg ]] && [[ -n "${WAYLAND_DISPLAY:-}${DISPLAY:-}" ]]; then
            success "WSLg active — Linux GUI apps will display on Windows desktop"
        else
            warn "WSLg NOT detected — Chrome window will not appear on your Windows desktop."
            warn "  Required: Windows 11 OR Windows 10 + WSL >= 0.65 with WSLg enabled."
            warn "  Fix:      Run 'wsl --update' from Windows PowerShell (admin), then reboot WSL."
            warn "  Verify:   echo \$WAYLAND_DISPLAY  → should print 'wayland-0'"
        fi
    fi

    # 4. Run the skill's own setup action (idempotent)
    if $check_only; then
        if [[ -d "$HOME/.config/google-chrome-debug" ]]; then
            success "web-control profile dir exists: $HOME/.config/google-chrome-debug"
        else
            warn "web-control profile dir is NOT initialized (run setup_web_control without --check)"
        fi
        if [[ -x "$skill_dir/scripts/launch-debug-chrome.sh" ]]; then
            success "web-control launcher is executable"
        else
            warn "web-control launcher is NOT executable"
        fi
    else
        if has_command python3; then
            info "Running: python3 $skill_dir/actions/setup.py"
            python3 "$skill_dir/actions/setup.py" || warn "web-control setup reported issues — see output above."
        fi
    fi

    if ! $check_only; then
        echo ""
        info "web-control is set up. Next-time-you-need-it:"
        info "  1. Run: bash $skill_dir/scripts/launch-debug-chrome.sh"
        info "  2. Sign in to your corporate Google account in the visible Chrome window"
        info "  3. The session persists — future runs reuse it"
    fi
}

# ---------------------------------------------------------------------------
# Semantic file search (file-locator MCP) — OPTIONAL
#
# The file-locator skill ships a stdio MCP server that gives agents semantic
# file search over the project corpus. The index (index.db) and the MCP
# registration (.mcp.json) are committed — the only per-clone step is the
# Python venv the server runs in. The venv is gitignored (its interpreter
# paths are absolute, so it can't be committed) and must be recreated locally.
# Idempotent: skips if the venv already has its deps.
#
# What this does:
#   - Creates tools/file-locator-mcp/.venv via uv (Python 3.12)
#   - Installs fastembed + mcp into it from the committed requirements.txt
# The BGE-small ONNX model (~130 MB) downloads on first query, not here.
# ---------------------------------------------------------------------------
setup_file_locator() {
    step "Semantic File Search (file-locator MCP) — Optional"

    local tool_dir
    tool_dir="$(dirname "$0")/tools/file-locator-mcp"
    if [[ ! -d "$tool_dir" ]]; then
        tool_dir="$PWD/tools/file-locator-mcp"
    fi

    if [[ ! -d "$tool_dir" ]]; then
        info "file-locator MCP not present — skipping (this is fine if the project doesn't use semantic file search)."
        return 0
    fi

    local venv_py="$tool_dir/.venv/bin/python"

    # Already set up? (venv exists and both deps import)
    if [[ -x "$venv_py" ]] && "$venv_py" -c "import fastembed, mcp" 2>/dev/null; then
        success "file-locator venv ready (fastembed + mcp installed)"
        return 0
    fi

    if $check_only; then
        warn "file-locator venv NOT initialized (run setup.sh without --check)"
        return 0
    fi

    if ! has_command uv; then
        warn "uv not available — cannot create the file-locator venv."
        warn "  Fix: ensure install_brew_packages ran, or install uv manually, then re-run setup.sh."
        return 0
    fi

    info "Creating file-locator venv (uv, Python 3.12)..."
    uv venv --python 3.12 "$tool_dir/.venv" 2>&1 | tail -3 \
        || { warn "uv venv failed — skipping file-locator setup."; return 0; }

    info "Installing file-locator deps (fastembed + mcp)..."
    uv pip install --python "$venv_py" -r "$tool_dir/requirements.txt" 2>&1 | tail -3 \
        || { warn "uv pip install failed — manual: uv pip install --python $venv_py -r $tool_dir/requirements.txt"; return 0; }

    if "$venv_py" -c "import fastembed, mcp" 2>/dev/null; then
        success "file-locator venv ready — the MCP loads on the next Claude Code session start"
        info "  The committed index.db is current; refresh it anytime with: bash $tool_dir/rebuild.sh"
    else
        warn "file-locator deps still not importable — see output above"
    fi
}

# ---------------------------------------------------------------------------
# Step: Git identity
# ---------------------------------------------------------------------------
configure_git() {
    step "Git Configuration"

    local current_name current_email

    current_name="$(git config --global user.name 2>/dev/null || true)"
    current_email="$(git config --global user.email 2>/dev/null || true)"

    if $check_only; then
        # Multi-account setups keep a repo-LOCAL identity override — that is
        # what commits in this project actually use, so report it as the
        # effective identity instead of the global one.
        local project_dir repo_name repo_email
        project_dir="$(cd "$(dirname "$0")" && pwd)"
        repo_name="$(git -C "$project_dir" config user.name 2>/dev/null || true)"
        repo_email="$(git -C "$project_dir" config user.email 2>/dev/null || true)"
        if [[ -n "$repo_name" && -n "$repo_email" ]] && \
           [[ "$repo_name" != "$current_name" || "$repo_email" != "$current_email" ]]; then
            success "Project git identity (repo-local override): $repo_name <$repo_email>"
            if [[ -n "$current_name" ]]; then
                info "Global git identity: $current_name <$current_email> — used only by repos without a local override."
            fi
        elif [[ -n "$current_name" && -n "$current_email" ]]; then
            success "Git identity is configured: $current_name <$current_email>"
        else
            warn "Git identity is NOT configured"
        fi
        return 0
    fi

    if [[ -n "$current_name" && -n "$current_email" ]]; then
        success "Git identity is configured: $current_name <$current_email>"
        if ! ask_yes "Keep this identity?"; then
            current_name=""
            current_email=""
        fi
    fi

    if [[ -z "$current_name" ]]; then
        local name
        name=$(ask_input "Your full name (for Git commits)")
        if [[ -n "$name" ]]; then
            git config --global user.name "$name"
            success "Git user.name set to: $name"
        else
            warn "Skipped — you can set this later with: git config --global user.name \"Your Name\""
        fi
    fi

    if [[ -z "$current_email" ]]; then
        local email
        email=$(ask_input "Your email (should match your GitHub account)")
        if [[ -n "$email" ]]; then
            git config --global user.email "$email"
            success "Git user.email set to: $email"
        else
            warn "Skipped — you can set this later with: git config --global user.email \"you@company.com\""
        fi
    fi
}

# ---------------------------------------------------------------------------
# Step: SSH key
# ---------------------------------------------------------------------------
setup_ssh_key() {
    step "SSH Key"

    local key_file="$HOME/.ssh/id_ed25519"

    # Discover keys beyond the default path: multi-account setups name keys
    # id_ed25519_work / id_ed25519_personal and wire them to host aliases via
    # ~/.ssh/config IdentityFile entries. A missing default key is NOT a
    # missing key.
    local found_keys=()
    [[ -f "$key_file" ]] && found_keys+=("$key_file")
    if [[ -f "$HOME/.ssh/config" ]]; then
        local idf
        while IFS= read -r idf; do
            idf="${idf/#\~/$HOME}"
            if [[ -f "$idf" ]]; then
                case " ${found_keys[*]-} " in
                    *" $idf "*) ;;
                    *) found_keys+=("$idf") ;;
                esac
            fi
        done < <(awk 'tolower($1)=="identityfile" {print $2}' "$HOME/.ssh/config")
    fi
    local pub
    for pub in "$HOME"/.ssh/id_*.pub; do
        [[ -f "$pub" ]] || continue
        local priv="${pub%.pub}"
        if [[ -f "$priv" ]]; then
            case " ${found_keys[*]-} " in
                *" $priv "*) ;;
                *) found_keys+=("$priv") ;;
            esac
        fi
    done

    # If this project's origin is an SSH remote, the check that actually
    # matters is whether SSH auth to that host (alias) works — and WHICH
    # GitHub account the key maps to ("Hi <user>!").
    probe_ssh_auth() {
        local project_dir origin_url origin_host ssh_out ssh_user
        project_dir="$(cd "$(dirname "$0")" && pwd)"
        origin_url="$(git -C "$project_dir" remote get-url origin 2>/dev/null || true)"
        case "$origin_url" in
            http*|"") return 0 ;;  # https remotes don't use SSH keys
        esac
        origin_host="$(echo "$origin_url" \
            | sed -n 's/^ssh:\/\///; s/^\([^@\/]*@\)\{0,1\}\([^:\/]*\)[:\/].*/\2/p')"
        [[ -z "$origin_host" ]] && return 0
        ssh_out="$(ssh -o BatchMode=yes -o ConnectTimeout=5 -T "git@$origin_host" 2>&1 || true)"
        if echo "$ssh_out" | grep -q "successfully authenticated"; then
            ssh_user="$(echo "$ssh_out" | sed -n 's/^Hi \([^!]*\)!.*/\1/p')"
            success "SSH auth to $origin_host works — GitHub sees account: ${ssh_user:-unknown}"
        else
            warn "SSH auth to $origin_host failed — check the IdentityFile for this host in ~/.ssh/config."
        fi
    }

    if [[ ${#found_keys[@]} -gt 0 ]]; then
        if [[ ${#found_keys[@]} -eq 1 && "${found_keys[0]}" == "$key_file" ]]; then
            success "SSH key already exists: $key_file"
        else
            success "SSH key(s) found: ${found_keys[*]}"
        fi
        probe_ssh_auth
        if $check_only; then
            return 0
        fi
        [[ ! -f "$key_file" ]] && return 0  # custom-named keys: nothing to generate or upload
    else
        if $check_only; then
            warn "No SSH key found ($key_file, ~/.ssh/config IdentityFile entries, or ~/.ssh/id_*)"
            return 0
        fi

        if ask_yes "No SSH key found. Generate one?"; then
            local email
            email="$(git config --global user.email 2>/dev/null || true)"
            if [[ -z "$email" ]]; then
                email=$(ask_input "Email for SSH key")
            fi

            mkdir -p "$HOME/.ssh"
            ssh-keygen -t ed25519 -C "$email" -f "$key_file" -N ""
            success "SSH key generated: $key_file"
        else
            warn "Skipped SSH key generation."
            return 0
        fi
    fi

    # Add the key to GitHub if gh is authenticated
    if has_command gh && gh auth status &>/dev/null; then
        local key_fingerprint
        key_fingerprint="$(ssh-keygen -lf "${key_file}.pub" 2>/dev/null | awk '{print $2}')"

        local gh_needs_scope=false
        local key_already_added=false

        local gh_keys
        if gh_keys="$(gh ssh-key list 2>/dev/null)"; then
            if echo "$gh_keys" | grep -q "$key_fingerprint" 2>/dev/null; then
                key_already_added=true
            fi
        else
            gh_needs_scope=true
        fi

        if $key_already_added; then
            success "SSH key is already on your GitHub account."
            ssh_key_on_github=true
        elif ask_yes "Add this SSH key to your GitHub account?"; then
            if $gh_needs_scope; then
                info "GitHub CLI needs permission to manage SSH keys."
                echo ""
                echo -e "  ${BOLD}What will happen next:${NC}"
                echo -e "  • A browser should open (or a URL will be printed below)"
                echo -e "  • If a browser opens, authorize the request and come back here"
                echo -e "  • If ${BOLD}no browser opens${NC}, look for a URL below — copy it,"
                echo -e "    open it in a browser on Windows, and complete the authorization"
                echo ""
                if ! gh auth refresh -h github.com -s admin:public_key; then
                    warn "Could not get SSH key permission. Add your key manually at github.com/settings/keys"
                    echo ""
                    info "Your public key:"
                    echo -e "${BOLD}$(cat "${key_file}.pub")${NC}"
                    echo ""
                    return 0
                fi
            fi

            local key_title="$(hostname) ($(date +%Y-%m-%d))"
            if gh ssh-key add "${key_file}.pub" --title "$key_title" 2>/dev/null; then
                success "SSH key added to GitHub as: $key_title"
                ssh_key_on_github=true
            else
                warn "Could not add SSH key automatically. Add it manually at github.com/settings/keys"
                echo ""
                info "Your public key:"
                echo -e "${BOLD}$(cat "${key_file}.pub")${NC}"
                echo ""
            fi
        else
            echo ""
            info "Your public key (add this to GitHub at github.com/settings/keys):"
            echo ""
            echo -e "${BOLD}$(cat "${key_file}.pub")${NC}"
            echo ""

            if [[ "$OS" == "mac" ]] && has_command pbcopy; then
                cat "${key_file}.pub" | pbcopy
                info "Public key copied to clipboard."
            fi
        fi
    else
        echo ""
        info "Your public key (add this to GitHub at github.com/settings/keys):"
        echo ""
        echo -e "${BOLD}$(cat "${key_file}.pub")${NC}"
        echo ""

        if [[ "$OS" == "mac" ]] && has_command pbcopy; then
            cat "${key_file}.pub" | pbcopy
            info "Public key copied to clipboard."
        fi
    fi
}

# ---------------------------------------------------------------------------
# Step: Claude Code CLI
# ---------------------------------------------------------------------------
install_claude_cli() {
    step "Claude Code CLI"

    # Check PATH first, then common install locations
    if ! has_command claude && [[ -x "$HOME/.local/bin/claude" ]]; then
        export PATH="$HOME/.local/bin:$PATH"
        info "Added ~/.local/bin to PATH for current session."
    fi

    if has_command claude; then
        local current_version
        current_version="$(claude --version 2>/dev/null || echo 'unknown')"
        success "Claude Code CLI is already installed: $current_version"
        if $check_only; then
            return 0
        fi
        info "Checking for updates..."
        claude update 2>/dev/null && success "Claude Code CLI is up to date." || info "No update available or update check skipped."
        return 0
    fi

    if $check_only; then
        warn "Claude Code CLI is NOT installed"
        return 0
    fi

    info "Installing Claude Code CLI..."
    curl -fsSL https://claude.ai/install.sh | bash

    local shell_profile="$HOME/.bashrc"
    if [[ "$(basename "$SHELL")" == "zsh" ]]; then
        shell_profile="$HOME/.zshrc"
    fi

    local local_bin_line='export PATH="$HOME/.local/bin:$PATH"'

    if [[ -d "$HOME/.local/bin" ]] && ! echo "$PATH" | tr ':' '\n' | grep -qx "$HOME/.local/bin"; then
        if ! grep -qF '/.local/bin' "$shell_profile" 2>/dev/null; then
            echo "" >> "$shell_profile"
            echo "# Added by setup.sh — Claude Code CLI and other local binaries" >> "$shell_profile"
            echo "$local_bin_line" >> "$shell_profile"
            info "Added ~/.local/bin to PATH in $shell_profile"
        fi
        export PATH="$HOME/.local/bin:$PATH"
    fi

    if [[ -f "$HOME/.bashrc" ]]; then
        source "$HOME/.bashrc" 2>/dev/null || true
    fi
    if [[ -f "$HOME/.zshrc" ]]; then
        source "$HOME/.zshrc" 2>/dev/null || true
    fi

    if has_command claude; then
        success "Claude Code CLI installed: $(claude --version 2>/dev/null || echo 'version unknown')"
    else
        warn "Claude Code CLI install script ran, but 'claude' command not found."
        warn "Try closing and reopening your terminal, then run: claude --version"
    fi
}

# ---------------------------------------------------------------------------
# Step: VS Code extensions
# ---------------------------------------------------------------------------
install_vscode_extensions() {
    step "VS Code Extensions"

    if ! has_command code; then
        if $check_only; then
            warn "'code' CLI not found — cannot check VS Code extensions."
            warn "Make sure VS Code is installed and 'code' is in your PATH."
            if [[ "$OS" == "mac" ]]; then
                warn "In VS Code: Cmd+Shift+P → 'Shell Command: Install code command in PATH'"
            fi
        else
            warn "'code' CLI not found — skipping VS Code extension install."
            warn "After installing VS Code, you can re-run this script or install manually."
        fi
        return 0
    fi

    # Extension IDs
    local extensions=(
        "anthropic.claude-code"
        "shd101wyy.markdown-preview-enhanced"
        "syncfusioninc.document-viewer-vscode-extensions"
        "mathematic.vscode-pdf"
        "wscats.cors-browser"
    )

    # Add WSL extension on Windows/WSL
    if [[ "$OS" == "wsl" ]]; then
        extensions+=("ms-vscode-remote.remote-wsl")
    fi

    # Extension display names (parallel array)
    local names=(
        "Claude Code"
        "Markdown Preview Enhanced"
        "Document Viewer"
        "vscode-pdf"
        "Open Browser Preview"
    )
    if [[ "$OS" == "wsl" ]]; then
        names+=("WSL")
    fi

    local installed
    installed="$(code --list-extensions 2>/dev/null || true)"

    local to_install=()
    for i in "${!extensions[@]}"; do
        local ext="${extensions[$i]}"
        local name="${names[$i]}"
        if echo "$installed" | grep -qi "${ext}"; then
            success "$name ($ext) — already installed"
        else
            if $check_only; then
                warn "$name ($ext) — NOT installed"
            else
                to_install+=("$ext")
                info "Will install: $name"
            fi
        fi
    done

    if $check_only; then
        return 0
    fi

    if [[ ${#to_install[@]} -eq 0 ]]; then
        info "All extensions already installed."
        return 0
    fi

    for ext in "${to_install[@]}"; do
        info "Installing $ext..."
        if code --install-extension "$ext" --force 2>/dev/null; then
            success "Installed $ext"
        else
            warn "Failed to install $ext — install manually from the Extensions panel in VS Code."
        fi
    done
}

# ---------------------------------------------------------------------------
# Step: Team roster access audit (--check only)
# ---------------------------------------------------------------------------
audit_team_access() {
    step "Team Roster Access Audit"

    local config_file="project.yml"

    if [[ -f "$config_file" ]]; then
        : # found in current directory
    elif [[ -f "$(dirname "$0")/../project.yml" ]]; then
        config_file="$(dirname "$0")/../project.yml"
    else
        warn "project.yml not found — cannot audit team access."
        warn "Create project.yml in the project root with the team roster."
        return 0
    fi

    # Extract repo from project.yml (the first repo: line under project:)
    local repo
    repo="$(grep '^[[:space:]]*repo:' "$config_file" | head -1 | sed 's/.*repo:[[:space:]]*//' | xargs)"
    if [[ -z "$repo" ]]; then
        warn "No repo found in project.yml — cannot audit team access."
        return 0
    fi

    # Parse GitHub usernames from project.yml team sections.
    local active_users=()
    local inactive_users=()
    local in_active=false
    local in_inactive=false

    while IFS= read -r line; do
        if echo "$line" | grep -q '^[[:space:]]*active:'; then
            in_active=true; in_inactive=false; continue
        elif echo "$line" | grep -q '^[[:space:]]*inactive:'; then
            in_active=false; in_inactive=true; continue
        fi

        if [[ "$in_active" == true || "$in_inactive" == true ]]; then
            if echo "$line" | grep -q '^[a-z#]'; then
                in_active=false; in_inactive=false; continue
            fi
        fi

        if echo "$line" | grep -q '^[[:space:]]*github:'; then
            local gh_user
            gh_user="$(echo "$line" | sed 's/.*github:[[:space:]]*//' | xargs)"
            if [[ -n "$gh_user" ]]; then
                if $in_active; then
                    active_users+=("$gh_user")
                elif $in_inactive; then
                    inactive_users+=("$gh_user")
                fi
            fi
        fi
    done < "$config_file"

    if [[ ${#active_users[@]} -eq 0 ]]; then
        warn "No active team members found in project.yml."
        return 0
    fi

    success "Active team members in project.yml: ${active_users[*]}"

    if ! has_command gh; then
        warn "GitHub CLI (gh) not available — cannot cross-reference repo collaborators."
        warn "Install gh and run 'gh auth login' to enable access auditing."
        return 0
    fi

    if ! gh auth status &>/dev/null; then
        warn "GitHub CLI not authenticated — cannot cross-reference repo collaborators."
        warn "Run 'gh auth login' to enable access auditing."
        return 0
    fi

    local collaborators
    if ! collaborators="$(gh api "repos/$repo/collaborators" --jq '.[] | "\(.login) \(.role_name)"' 2>/dev/null)"; then
        warn "Could not fetch collaborators for $repo."
        warn "You may not have admin access to view collaborators."
        return 0
    fi

    # Parallel arrays (macOS ships bash 3.2 — no associative arrays).
    local collab_array=()
    local collab_roles=()
    while IFS=' ' read -r user role; do
        if [[ -n "$user" ]]; then
            collab_array+=("$user")
            collab_roles+=("${role:-unknown}")
        fi
    done <<< "$collaborators"

    info "GitHub repo collaborators: ${collab_array[*]}"

    local issues_found=false
    local observer_count=0

    # Check 1: Collaborators not in the active team roster.
    # This is a teaching project: read-only observers are routinely granted
    # access without joining the roster — they never modify the project, so
    # unrostered READ access is informational, not a posture failure.
    # Unrostered WRITE access is different: anyone who can modify the repo
    # should be on the roster (or have their access reduced to read).
    for i in "${!collab_array[@]}"; do
        local collab="${collab_array[$i]}"
        local role="${collab_roles[$i]}"
        local found=false
        for active in "${active_users[@]}"; do
            if [[ "$collab" == "$active" ]]; then
                found=true
                break
            fi
        done
        if ! $found; then
            case "$role" in
                read|triage)
                    info "OBSERVER: '$collab' has $role access and is not in the roster — expected for teaching-project observers."
                    observer_count=$((observer_count + 1))
                    ;;
                *)
                    warn "UNROSTERED WRITE ACCESS: '$collab' has $role access but is NOT in the project.yml roster — add them to team.active or reduce their access to read."
                    issues_found=true
                    ;;
            esac
        fi
    done

    # Check 2: Active team members without repo access (missing access)
    for active in "${active_users[@]}"; do
        local found=false
        for collab in "${collab_array[@]}"; do
            if [[ "$active" == "$collab" ]]; then
                found=true
                break
            fi
        done
        if ! $found; then
            warn "MISSING ACCESS: '$active' is in project.yml active roster but has NO repo access."
            issues_found=true
        fi
    done

    # Check 3: Inactive members who still have access (stale access)
    if [[ ${#inactive_users[@]} -gt 0 ]]; then
        for inactive in "${inactive_users[@]}"; do
            for collab in "${collab_array[@]}"; do
                if [[ "$inactive" == "$collab" ]]; then
                    error "STALE ACCESS: '$inactive' is marked inactive in project.yml but still has repo access. Remove their access."
                    issues_found=true
                fi
            done
        done
    fi

    if ! $issues_found; then
        if [[ $observer_count -gt 0 ]]; then
            success "Team roster and repo access are in sync ($observer_count read-only observer(s) not rostered — expected for a teaching project)."
        else
            success "Team roster and repo access are in sync."
        fi
    fi
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print_summary() {
    step "Summary"

    echo ""
    echo -e "${BOLD}Installed tools:${NC}"
    echo -e "  ${BOLD}Core:${NC}"
    has_command brew    && success "  Homebrew: $(brew --version | head -1)"   || warn "  Homebrew: not found"
    has_command node    && success "  Node.js:  $(node --version)"             || warn "  Node.js: not found"
    has_command npm     && success "  npm:      $(npm --version)"              || warn "  npm: not found"
    has_command git     && success "  Git:      $(git --version)"              || warn "  Git: not found"
    has_command gh      && success "  gh:       $(gh --version | head -1)"     || warn "  gh: not found"
    has_command jq      && success "  jq:       $(jq --version)"              || warn "  jq: not found (required by hooks)"
    has_command claude  && success "  Claude:   installed"                      || warn "  Claude CLI: not found"
    has_command code    && success "  VS Code:  $(code --version | head -1)"   || warn "  VS Code CLI: not found"
    echo -e "  ${BOLD}Document processing:${NC}"
    has_command pandoc   && success "  pandoc:       $(pandoc --version | head -1)" || warn "  pandoc: not found"
    has_command pdftotext && success "  poppler:      installed (pdftotext)"        || warn "  poppler: not found"
    has_command qpdf     && success "  qpdf:         $(qpdf --version | head -1)"  || warn "  qpdf: not found"
    if has_command soffice; then
        local ver; ver="$(soffice --headless --version 2>/dev/null | head -1 | awk '{print $2}')"
        success "  LibreOffice:  installed (v${ver:-?}, headless mode $(verify_soffice_headless &>/dev/null && echo 'verified' || echo 'BROKEN'))"
    else
        warn "  LibreOffice: not found"
    fi
    has_command python3  && success "  Python 3:     $(python3 --version)"          || warn "  Python 3: not found"
    has_command uv       && success "  uv:           $(uv --version)"               || warn "  uv: not found"
    echo ""

    if $check_only; then
        # Run security audits in check mode
        audit_team_access
        echo ""
        info "Run without --check to install missing tools."
        return 0
    fi

    # Open the project in VS Code if the code CLI is available
    if has_command code; then
        step "Opening Project in VS Code"
        local project_dir
        project_dir="$(cd "$(dirname "$0")" && pwd)"
        info "Opening $project_dir in VS Code..."
        code "$project_dir"
        success "VS Code opened with the project."
    fi

    echo -e "${BOLD}Next steps:${NC}"
    echo ""
    echo -e "  Setup is complete! The script handled the install steps from ${BOLD}setup.md${NC}."
    echo ""
    echo -e "  Still to do (manual — see setup.md for details):"
    echo -e "    1. Confirm Claude training opt-out at ${BOLD}claude.ai/settings/data-privacy-controls${NC}"
    echo -e "    2. Enable 2FA on GitHub (skip if you signed in via Google SSO)"
    echo -e "    3. Enable 2FA on your Claude account (skip if Google SSO)"
    echo -e "    4. In Claude Code: run ${BOLD}/secops check${NC} to confirm posture"
    echo ""
    echo -e "  Then read ${BOLD}how-to-guide.md${NC} for day-to-day usage of the project."
    echo ""

    # Stamp the successful full run so tooling (e.g. the project console's
    # Environment view) can answer "has setup.sh been run, and when?"
    local stamp_dir
    stamp_dir="$(cd "$(dirname "$0")" && pwd)/.state"
    mkdir -p "$stamp_dir"
    date -u +"%Y-%m-%dT%H:%M:%SZ" > "$stamp_dir/setup-last-run.txt"
}

# ---------------------------------------------------------------------------
# Pre-flight: Admin privileges check
# ---------------------------------------------------------------------------
check_admin_privileges() {
    step "Admin Privileges"

    local is_admin=false

    if [[ "$OS" == "mac" ]]; then
        if groups "$USER" 2>/dev/null | grep -qw admin; then
            is_admin=true
        fi
    else
        if sudo -n true 2>/dev/null; then
            is_admin=true
        elif groups "$USER" 2>/dev/null | grep -qwE 'sudo|wheel|admin'; then
            is_admin=true
        fi
    fi

    if $is_admin; then
        success "Admin privileges confirmed."
        return 0
    fi

    echo ""
    warn "Admin privileges not detected."
    echo ""

    if [[ "$OS" == "mac" ]]; then
        echo -e "  ${BOLD}Before continuing, you need to elevate your account:${NC}"
        echo ""
        echo -e "  1. Open the ${BOLD}My IT Support${NC} app on your computer"
        echo -e "  2. Click ${BOLD}\"Make Me Admin\"${NC}"
        echo -e "  3. Wait for confirmation that admin access has been approved"
        echo -e "  4. Come back here and continue"
    else
        echo -e "  ${BOLD}You may already have admin rights${NC} — Windows will prompt you for"
        echo -e "  your password when needed. Just answer the prompts and continue."
        echo ""
        echo -e "  If installs fail with 'permission denied':"
        echo -e "    - Check for ${BOLD}Managed Endpoint Central${NC} (or similar IT app) in your Start menu"
        echo -e "    - Contact IT to request admin privileges"
    fi
    echo ""

    if $check_only; then
        if [[ "$OS" == "mac" ]]; then
            warn "Admin privileges are NOT active. Complete the steps above before running the setup."
        else
            warn "Admin privileges not confirmed. You may be prompted for your password during installs."
        fi
        return 0
    fi

    if [[ "$OS" == "mac" ]]; then
        if ask_yes "Have you completed 'Make Me Admin' and received approval?"; then
            if groups "$USER" 2>/dev/null | grep -qw admin; then
                success "Admin privileges confirmed."
                return 0
            fi
            warn "Admin privileges still not detected."
            echo ""
            echo -e "  This can happen if your terminal session started before the elevation."
            echo -e "  Try: ${BOLD}close this terminal, open a new one, and re-run the script.${NC}"
            echo ""
            if ! ask_yes "Continue anyway? (some steps may fail without admin)"; then
                info "Exiting. Re-run this script after getting admin access."
                exit 0
            fi
            warn "Continuing without confirmed admin — some installs may prompt for a password or fail."
        else
            echo ""
            info "No problem. Complete these steps first:"
            echo ""
            echo -e "  1. Open ${BOLD}My IT Support${NC} → click ${BOLD}\"Make Me Admin\"${NC}"
            echo -e "  2. Wait for approval"
            echo -e "  3. Close this terminal and open a new one"
            echo -e "  4. Re-run: ${BOLD}bash setup.sh${NC}"
            echo ""
            exit 0
        fi
    else
        if ask_yes "Continue with setup? (you'll be prompted for your password if needed)"; then
            warn "Continuing — you may be prompted for your password during installs."
        else
            echo ""
            info "No problem. Get admin access first, then re-run this script."
            echo ""
            exit 0
        fi
    fi
}

# ===========================================================================
# Main
# ===========================================================================
main() {
    echo ""
    echo -e "${BOLD}PDLC_DEMO — Development Environment Setup${NC}"
    echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    detect_os
    check_admin_privileges

    install_homebrew
    setup_wsl_browser
    setup_code_cli
    install_brew_packages
    install_python_packages
    setup_web_control
    setup_file_locator
    configure_git
    setup_ssh_key
    install_claude_cli
    install_vscode_extensions
    print_summary
}

main "$@"
