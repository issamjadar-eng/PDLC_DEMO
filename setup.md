# Setup — PDLC_DEMO

Onboarding for a new contributor joining the PDLC_DEMO repository. Walks from a blank machine through admin privileges, terminal, accounts, installs, repo clone, and security posture. Follow each step in order — later steps depend on earlier ones.

> **About PDLC_DEMO**: this is a *demonstration* project for agentic workflows across the Product Development Life Cycle (PDLC) in MedTech. The DHF, design controls, V&V, and submission artifacts anchor on the **PainEase PCA Advanced (PP3500)** — a patient-controlled analgesia infusion pump (combination SaMD / SiMD / hardware device). Fabricated clinical data and placeholder predicates are clearly flagged — read `CLAUDE.md` and `project-overview.md` for the full scope.
>
> **Companion docs**:
> - `setup.sh` — automated installer for everything in steps 8–14 below (works on macOS, WSL, Linux).
> - `how-to-guide.md` — day-to-day usage once setup is complete (opening VS Code, `git pull`, launching Claude Code, project tour, skills).
> - `new-project-bootstrap.md` — different audience: how to stand up a *brand-new* MedTech project from scratch using the same skill stack.

> **Windows users**: This project uses Unix-based tools for document processing, automation, and AI workflows. To keep the team consistent, Windows users run these tools inside **WSL** (Windows Subsystem for Linux). Step 3 walks you through it.

---

## 🤖 You don't have to do this alone — let Claude help

Many steps below have an **"✨ Or just ask Claude"** callout. Once you have Claude Code installed (step 13) — or already have it from another project — you can do most of the manual work in plain English instead of copying commands.

**Examples of things you can just ask:**

- *"Set up my Git identity. My name is Jane Smith and my email is jane.smith@globallogic.com."*
- *"Generate an SSH key for me and add it to my GitHub account."*
- *"Install all the VS Code extensions this project needs."*
- *"Add me to the team roster — I'm Jane Smith, GitHub username `jsmith`, email `jane.smith@globallogic.com`, role 'Regulatory Affairs'."*
- *"Record my training opt-out and 2FA attestations."*
- *"Run the security posture check and the project audit."*

You don't need to know the underlying commands. Claude reads the project conventions, runs the right tools, edits the right files, and tells you what changed. **This is the recommended path for non-engineer roles** (regulatory affairs, clinical, QE).

The manual commands are still in the doc — you'll see exactly what Claude is doing under the hood — but you only need to type them yourself if you prefer to.

**Bootstrap caveat**: steps 1–12 happen *before* Claude Code is installed (step 13), so you can't ask Claude for those yet — they need to happen manually, OR via the automated `setup.sh` path. After step 13, every remaining step has an "ask Claude" option.

---

## Before You Start: Admin Privileges

Installing development tools requires admin privileges on your computer.

### Mac

1. Open the **My IT Support** app on your computer
2. Click **"Make Me Admin"**
3. **Wait for confirmation** that admin access has been approved — this may take a moment
4. Once approved, proceed with setup

> If you skip this step, installations will fail with "permission denied" errors.

### Windows

You may already have admin rights — Windows will prompt you for your password when needed (click **Yes** / enter your credentials to proceed). **Just proceed with setup** and answer the prompts as they appear.

If an installation fails with "permission denied" or "access denied":

1. Check if you have **Managed Endpoint Central** (or a similar IT management app) — look in the Start menu or system tray. It may have an option to request elevated access.
2. If you can't find a self-service tool, contact IT to request admin privileges for development tool installation.

---

## 1. How to Open a Terminal

You'll use the terminal (also called command line) throughout this guide to run commands. Here's how to open one:

### Mac

1. Press `Cmd+Space` to open Spotlight Search
2. Type **Terminal** and press Enter
3. A window with a command prompt appears — this is where you'll type commands

> **Tip**: You can also find Terminal in **Applications → Utilities → Terminal**. Consider keeping it in your Dock since you'll use it regularly.

### Windows

Windows users will use two different terminals during setup:

**PowerShell** (needed only for step 3 — installing WSL):
1. Click the **Start button** (Windows icon, bottom-left)
2. Type **PowerShell**
3. **Right-click** on "Windows PowerShell" and select **Run as administrator**
4. Click **Yes** if asked to allow changes

**Ubuntu / WSL terminal** (used for everything else after step 3):
- This becomes available after you install WSL in step 3
- Open it by clicking the **Start button**, typing **Ubuntu**, and pressing Enter

> **Important**: After step 3, when this guide says "open your terminal" or "run this command", **Windows users should use the Ubuntu terminal**, not PowerShell or CMD. The only exceptions are steps that explicitly say to use your regular Windows desktop (like installing VS Code or Google Drive Desktop).

---

## 2. Install VS Code

VS Code is the team's primary editor for all project files. Install this from your regular desktop — not from a terminal.

- **Mac**: Download from [code.visualstudio.com](https://code.visualstudio.com/), open the `.dmg`, drag to Applications.
- **Windows**: Download the installer from [code.visualstudio.com](https://code.visualstudio.com/), run it, follow the wizard. Check **"Add to PATH"** when prompted.

### Enable the `code` CLI (Mac only)

Open VS Code, press `Cmd+Shift+P`, type **"Shell Command: Install 'code' command in PATH"**, and run it. This lets you launch VS Code from your terminal with `code .`.

---

## 3. Install WSL (Windows only)

Mac users — skip to [step 4](#4-create-a-github-account).

WSL gives you a Linux terminal inside Windows. All development tools (Git, Node.js, Claude Code, etc.) will be installed here, not in regular Windows.

### Install WSL and Ubuntu

> **Already have WSL?** If you've installed WSL before, you can skip the install command. Open PowerShell, type `wsl`, and if Ubuntu launches, jump straight to [Verify WSL is working](#verify-wsl-is-working). If you see **"no installed distributions"**, jump to step 2b below.

1. Open **PowerShell as Administrator** (see step 1 for how)
2. Type this command and press Enter:

```
wsl --install -d Ubuntu
```

   This installs both the WSL platform **and** the Ubuntu distribution. If it says a restart is needed, restart and continue with step 3.

   > **Troubleshooting — "no installed distributions"**: If you already ran `wsl --install` previously (or WSL was pre-installed on your machine), it may have enabled WSL without installing Ubuntu. Run `wsl --install -d Ubuntu` in an admin PowerShell to install the distribution explicitly.

3. After restart, **open Ubuntu yourself** — WSL does not always launch automatically. Either method works:
   - **Option A (recommended)**: Click the **Start button**, type **Ubuntu**, and press Enter
   - **Option B**: Open **PowerShell** and type `wsl`
4. The first time Ubuntu opens, it will finish setting up and ask you to create a Linux username and password:
   - **Username**: Use your **Windows username** in lowercase. If you're not sure what it is, open PowerShell and run `echo $env:USERNAME`. Linux usernames don't allow dots or spaces — if yours contains them (e.g., `ben.xavier`), use your first name or `firstname-lastname` instead (e.g., `ben` or `ben-xavier`).
   - **Password**: Use your **Windows password**. You'll need this password occasionally when installing software (any time you see a `sudo` prompt).
   - The password won't show characters as you type — that's normal. Just type it and press Enter.

### Verify WSL is working

Open the Ubuntu app from your Start menu (or type `wsl` in PowerShell) and type:

```
cat /etc/os-release
```

You should see output mentioning "Ubuntu". **This is your terminal for the rest of the setup.**

### Install the VS Code WSL extension

1. Open VS Code (the regular Windows app)
2. Go to Extensions (`Ctrl+Shift+X`)
3. Search for **"WSL"** by Microsoft and install it

This lets VS Code open folders and run terminals inside your WSL environment.

---

## 4. Create a GitHub Account

You need a GitHub account to access the project repository. The repo is **private** — you must be granted access before you can clone it.

1. Go to [github.com/signup](https://github.com/signup)
2. Click **"Sign up"** and choose **"Continue with Google"**
3. Sign in with your **company Google/Gmail account**
4. Choose a username, complete the setup prompts
5. **Send your GitHub username to the project admin** (Ben Xavier — ben.xavier@globallogic.com) and request access to `GlobalLogic-a-Hitachi-Company/PDLC_DEMO`
6. **Wait for confirmation** that access has been granted — you'll receive an email invitation from GitHub. Click **"Accept invitation"** in that email.

> **You cannot proceed with cloning the project until your access is confirmed.** While you wait, continue with steps 5 (Claude account), 6 (Google Drive Desktop), and 7 (Claude Desktop).

GitHub two-factor authentication is covered in [§15 — Security posture](#15-security-posture-required) at the end of this guide.

---

## 5. Create a Claude Account

1. Go to [claude.ai](https://claude.ai/) and click **"Sign up"**
2. Sign up using your **company Google/Gmail account**
3. After account creation, upgrade to the **Pro plan** (minimum required) at [claude.ai/settings/billing](https://claude.ai/settings/billing) — this is needed for Claude Code CLI access and higher usage limits
4. Disabling training on your data and 2FA are both covered in [§15 — Security posture](#15-security-posture-required) at the end of this guide.

---

## 6. Install Google Drive Desktop

> **Note**: This is a native Windows/Mac app — install it from your regular desktop, not inside WSL.

Google Drive Desktop syncs shared drives to your local machine. Useful for accessing project artifacts (reference PDFs, original Word/PowerPoint deliverables) that aren't checked into git.

- **Mac**: Download from [google.com/drive/download](https://www.google.com/drive/download/), open the `.dmg`, follow the installer.
- **Windows**: Download from [google.com/drive/download](https://www.google.com/drive/download/), run the installer, follow the wizard.

Sign in with your company Google account when prompted. Your Google Drive files will appear under:
- **Mac**: `/Volumes/GoogleDrive/` or in Finder sidebar under **Google Drive**
- **Windows**: A mounted drive letter (e.g., `G:`) or under **Google Drive** in File Explorer

### Verify Google Drive starts automatically on login

Google Drive Desktop should launch automatically when you log in to your computer.

**Mac**: System Settings → **General → Login Items** → look for **Google Drive** in the list. If absent, open Google Drive from Applications → menu-bar icon → **Settings** → **Preferences** → check **"Open Google Drive on startup"**.

**Windows**: Settings → **Apps → Startup** (or Task Manager → **Startup** tab). If absent, open Google Drive from the Start menu → system-tray icon → **Settings** → **Preferences** → check **"Open Google Drive on system startup"**.

> **WSL users**: Google Drive is a native Windows app. From inside WSL, synced files are accessible via `/mnt/c/Users/yourname/Google Drive/` (or `/mnt/g/` if Drive is mapped to a drive letter). This path is only available while Google Drive Desktop is running.

---

## 7. Install Claude Desktop

> **Note**: This is a native Windows/Mac app — install it from your regular desktop, not inside WSL.

Claude Desktop is a companion app for chatting with Claude, connecting integrations (Gmail, Calendar, GitHub), and general conversations. Claude Code (installed later) is the primary tool for project file work.

- **Mac**: Download from [claude.ai/download](https://claude.ai/download), open the `.dmg`, drag to Applications.
- **Windows**: Download the installer from [claude.ai/download](https://claude.ai/download), run it, follow the wizard.

### Log in

Launch the app and sign in with your Claude account (step 5).

### Connect Integrations

Claude Desktop supports integrations that let Claude interact with external services. Here's how:

1. Open Claude Desktop and start a new conversation
2. In the bottom-right of the chat input area, click **Customize** (the sliders icon)
3. Select **Connectors**
4. Click the **+** icon to add a new connector
5. Enable each of the following, one at a time:

| Integration | Account | What it enables |
|-------------|---------|-----------------|
| **Gmail** | Company Google account | Read, search, and draft emails |
| **Google Calendar** | Company Google account | View, create, and manage calendar events |
| **GitHub** | Your GitHub account (step 4) | Access repos, issues, and pull requests |

Use the same company Google account for Gmail and Calendar, and your GitHub account for the GitHub integration.

---

## Choose Your Path

Now that you have your accounts, native apps, and a terminal (plus WSL if on Windows), choose how to continue:

| Path | Best for | What it does |
|------|----------|--------------|
| **Automated** (`setup.sh`) | Most people, including non-engineers | One script installs Homebrew, Node.js, Git, gh, jq, document tools (pandoc / poppler / qpdf / LibreOffice headless-tested / Python 3 / uv / pip packages), Claude Code CLI, VS Code extensions, SSH key, optional web-control browser automation, optional file-locator MCP venv. Skips anything already installed. Opens VS Code when done. |
| **Claude-assisted** (already have Claude Code from another project?) | Non-engineers who already have Claude Code | Open Claude Code in another project and say *"Help me set up PDLC_DEMO. Clone it, run setup.sh, register me on the team, and walk me through the security posture."* Claude handles the whole thing in one conversation — you only sign in to browsers when prompted. |
| **Manual** (continue step-by-step) | Engineers who want to understand each tool | Walk through each tool one at a time with full explanations. |

### Automated Path

First, install Homebrew and the GitHub CLI so you can authenticate and clone the private repo. Open your terminal and run each block in order:

**Install Homebrew** (skip if `brew --version` already works):

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

> After the install finishes, it prints **"Next steps"** commands to add Homebrew to your PATH. **You must run these** before continuing — see step 8 for examples by platform.

**Set up browser access from WSL** (Windows only — Mac users skip):

```
echo 'export BROWSER=explorer.exe' >> ~/.bashrc
export BROWSER=explorer.exe
```

> This tells CLI tools (`gh auth login`, `claude`, etc.) to open URLs in your Windows default browser. The first line makes it permanent; the second applies it immediately for this terminal session.

**Install the GitHub CLI and authenticate**:

```
brew install gh
gh auth login
```

When prompted:
- Account: **GitHub.com**
- Protocol: **HTTPS**
- Authenticate: **Login with a web browser**

A one-time code displays and your browser opens. Enter the code to complete authentication.

> **If no browser opens**: copy the URL from the terminal, open it manually (usually `github.com/login/device`), enter the code.

**Create a projects folder, clone the repo, and run the setup script**:

```
mkdir -p ~/projects
cd ~/projects
gh repo clone GlobalLogic-a-Hitachi-Company/PDLC_DEMO
cd PDLC_DEMO
bash setup.sh
```

The script installs everything else, skips tools already installed, and opens VS Code with the project when it finishes.

> **When VS Code opens**, it asks: **"Do you trust the authors of the files in this folder?"** — click **"Yes, I trust the authors"**. This is a one-time prompt; without it, the project's shared settings won't apply.

After the script finishes, the install side of setup is complete. Jump to **[§15 — Security posture](#15-security-posture-required)** at the bottom of this guide to confirm training opt-out, 2FA, and `/secops` attestation.

### Manual Path

Continue with step 8 below.

---

## 8. Install Homebrew

> **Automated path**: Skip — the setup script handles this.

Homebrew is the package manager we use to install development tools. It works on both Mac and Linux (WSL).

### Mac

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, the installer prints **"Next steps"**. On Apple Silicon Macs (M1/M2/M3/M4) they look like:

```
echo >> ~/.zprofile 'eval "$(/opt/homebrew/bin/brew shellenv)"'
eval "$(/opt/homebrew/bin/brew shellenv)"
```

> **Important**: If you skip this, `brew` won't be found when you open a new terminal. Copy and run the exact commands the installer prints.

### Windows (in WSL terminal)

Open your Ubuntu terminal and run:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

> The installer may ask for your password and install system packages. Scrolling `apt-get` output is normal — let it finish.

After installation, the installer prints "Next steps". Run:

```
echo >> ~/.bashrc 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"'
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
```

### Verify

```
brew --version
```

---

## 9. Install Node.js and core utilities

> **Automated path**: Skip — the setup script handles this.

Run in your terminal (Mac Terminal or WSL Ubuntu):

```
brew install node git gh jq
```

This installs:
- **Node.js** + npm (required by various VS Code extensions and Claude Code skills)
- **Git** (version control — Mac and WSL may already have one; the brew version is fine to coexist)
- **gh** (the GitHub CLI — used by `/sync-skills`, the team-roster audit, etc.)
- **jq** (JSON parsing — required by the task gate and several other hook scripts; **non-optional**)

### Verify

```
node --version
npm --version
git --version
gh --version
jq --version
```

---

## 10. Install Document Processing Tools

> **Automated path**: Skip — the setup script handles this.

Several Claude Code skills (`/docflow`, `/pdf`, `/xlsx`, `/docx`, `/pptx`) convert documents between markdown, Word, PDF, Excel, and PowerPoint. These need a stack of native tools.

### Brew-installable

```
brew install pandoc poppler qpdf python3 uv
```

| Tool | Used by | What it does |
|------|---------|--------------|
| **pandoc** | `/docflow`, `/docx`, `/md-deck` | Universal document converter (markdown ↔ DOCX / HTML / LaTeX) |
| **poppler** | `/pdf`, `/docflow` | Provides `pdftotext` and PDF rendering helpers |
| **qpdf** | `/pdf` | PDF structure manipulation (merge, split, repair) |
| **python3** | All Python-based skills | Python 3 runtime |
| **uv** | `/project-console`, `/file-locator` | Fast Python venv + dependency manager |

### LibreOffice (separate install)

LibreOffice is required by `/docflow` (DOC→DOCX, DOCX→PDF rendered pagination) and `/pptx` (PPTX slide handling). The install path differs by platform:

- **Mac**: `brew install --cask libreoffice` (bundles writer + calc + impress)
- **WSL / Linux**: `sudo apt install -y libreoffice-common libreoffice-core libreoffice-writer libreoffice-calc libreoffice-impress`

After install, smoke-test that headless mode actually works (presence on PATH alone isn't enough — Ubuntu sometimes lacks fontconfig / java):

```
echo test > /tmp/smoke.txt
soffice --headless --convert-to pdf --outdir /tmp /tmp/smoke.txt
ls /tmp/smoke.pdf   # should print the path
```

If the smoke test fails, the typical fixes are `sudo apt install -y fontconfig libreoffice-core` (missing runtime deps) or `sudo apt install -y default-jre` (Java filter dependencies).

### Python packages

A handful of Python libraries the document skills need on top of the above tools:

```
python3 -m pip install --user --break-system-packages \
  pypdf pdf2image pdfplumber reportlab pandas openpyxl python-docx lxml defusedxml Pillow
```

The `--break-system-packages` flag is needed on Ubuntu 24.04 to bypass PEP 668; on macOS or older Ubuntu the flag is harmless (Python ignores it).

---

## 11. Configure Git and SSH

> **Automated path**: Skip — the setup script handles this.
>
> **✨ Or just ask Claude (if you already have Claude Code from another project)**: *"Set up Git and SSH for me. My name is Jane Smith and my email is jane.smith@globallogic.com."* Claude will configure your Git identity, generate an SSH key if you don't already have one, upload it to GitHub via the `gh` CLI, and verify SSH access — without you typing any commands.

### Configure your identity

Set your **full name** (not your GitHub username) and your **email** to match your GitHub account:

```
git config --global user.name "Jane Smith"
git config --global user.email "jane.smith@globallogic.com"
```

> `user.name` is your **full name** (e.g., `Jane Smith`), not your GitHub username (e.g., `jsmith42`). Your GitHub username is only used when logging in to github.com.

### Generate an SSH key (if you don't have one)

```
ls ~/.ssh/id_ed25519.pub
```

- If you see a file path — skip the generation step below and go straight to "Add your SSH key to GitHub".
- If you see "No such file or directory" — generate one:

```
ssh-keygen -t ed25519 -C "your.email@globallogic.com"
```

Press Enter to accept defaults; set a passphrase if desired.

### Add your SSH key to GitHub

1. Copy your public key:
   - **Mac**: `pbcopy < ~/.ssh/id_ed25519.pub` (copies silently — nothing prints)
   - **Windows (WSL)**: `cat ~/.ssh/id_ed25519.pub`, select the whole line, copy with `Ctrl+Shift+C`

   Your key looks like: `ssh-ed25519 AAAA…long-string… your.email@globallogic.com`

2. Go to [github.com/settings/keys](https://github.com/settings/keys) in your browser
3. Click **"New SSH key"**, paste the key into the **Key** field
4. **Title**: name that identifies which machine this key is on — e.g., `GL Win Laptop`, `GL Mac`, `Home Desktop`
5. Click **"Add SSH key"**

### Enable browser access from WSL (Windows only)

```
echo 'export BROWSER=explorer.exe' >> ~/.bashrc
export BROWSER=explorer.exe
```

> Tells CLI tools to open URLs in your Windows default browser. Mac users — skip this block (macOS terminals open browsers natively).

### Authenticate the GitHub CLI

```
gh auth login
```

When prompted:
- Account: **GitHub.com**
- Protocol: **SSH**
- SSH key: select the key you just created
- Authentication: **Login with a web browser**

### Verify SSH access

```
ssh -T git@github.com
```

First time you'll see "The authenticity of host 'github.com (...)' can't be established" — type **yes** and press Enter. You should then see `Hi yourusername! You've successfully authenticated, …`.

---

## 12. Install VS Code Extensions

> **Automated path**: Skip — the setup script handles this.
>
> **✨ Or just ask Claude (if you already have Claude Code from another project)**: *"Install the VS Code extensions this project needs."* Claude will run `code --install-extension` for each extension below and confirm what's installed.

Open VS Code → Extensions (`Ctrl+Shift+X` / `Cmd+Shift+X`) → search for each, click **Install**:

### Everyone

| Extension | Author | What it does |
|-----------|--------|--------------|
| **Claude Code** | Anthropic | Claude Code integration in VS Code |
| **Markdown Preview Enhanced** | Yiyi Wang | Preview `.md` files with tables, diagrams, and styling |
| **Document Viewer** | Syncfusion | View `.docx`, `.pdf`, `.xlsx` files inside VS Code |
| **vscode-pdf** | Mathematic Inc | Lightweight PDF viewer |
| **Open Browser Preview** | Eno Yao (Wscats) | Right-click a file → open in your default browser (useful for HTML dashboards) |

### Windows only

| Extension | Author | What it does |
|-----------|--------|--------------|
| **WSL** | Microsoft | Connects VS Code to your WSL/Ubuntu environment |

> Mac users do **not** need the WSL extension.

---

## 13. Install Claude Code CLI

> **Automated path**: Skip — the setup script handles this.

In your terminal:

```
curl -fsSL https://claude.ai/install.sh | bash
```

### Log in

```
claude
```

Follow the prompts to authenticate with your Anthropic account. One-time login — your session persists across terminal restarts.

---

## 14. Clone the Repository

> **Automated path**: Skip — you already cloned the repo before running `setup.sh`.
>
> **✨ Or just ask Claude (in another project's Claude Code session)**: *"Clone the PDLC_DEMO repo for me into `~/projects/`."* Claude will run the `git clone` for you and open the folder.

```
mkdir -p ~/projects
cd ~/projects
git clone git@github.com:GlobalLogic-a-Hitachi-Company/PDLC_DEMO.git
cd PDLC_DEMO
```

(HTTPS alternative: `git clone https://github.com/GlobalLogic-a-Hitachi-Company/PDLC_DEMO.git` — GitHub will prompt for username + personal access token.)

### Open the project in VS Code

```
code .
```

VS Code opens with the project's files visible. First time, click **"Yes, I trust the authors"** when prompted.

> **Windows users**: Check the bottom-left corner of VS Code — you should see **"WSL: Ubuntu"**. If not, press `Ctrl+Shift+P`, run **"WSL: Reopen Folder in WSL"**.

### Set Markdown Preview Enhanced as the default `.md` viewer

1. Right-click any `.md` file in the Explorer panel
2. **"Open With..."** → **Markdown Preview Enhanced** → **"Set as Default"**

---

## 15. Security Posture (required)

PDLC_DEMO includes a security-posture check (`/secops`) that audits training opt-outs, 2FA attestations, repo collaborator drift, and the security allowlist in `project.yml`. **Every contributor must complete this section** before they begin editing project files.

This section folds in what used to live in a separate `setup.md` security checklist — it's part of contributor onboarding, not a separate concern.

> **✨ Easiest path — let Claude run all of §15 for you**: open Claude Code in the project and say:
> *"Walk me through the security posture setup. I'm Jane Smith, my GitHub is `jsmith`, my email is `jane.smith@globallogic.com`, and my role is 'Regulatory Affairs'. I've already turned off the 'Help improve Claude' toggle and confirmed 2FA via Google SSO."*
>
> Claude will: (1) add you to `project.yml` `team.active`, (2) create your `tasks/<you>/SECOPS.md` file, (3) record your training-opt-out and 2FA attestations, (4) run `/secops check` to confirm. You only need to do the browser toggles yourself (15a step 1–2, 15b/c if not on SSO). Then you're done.
>
> The subsections below explain what Claude is doing under the hood if you want to follow along — or do it manually.

### 15a. Claude training opt-out

Anthropic does not train models on Claude Code conversations by default for Pro / Team / Enterprise tiers, but confirm:

1. Go to https://claude.ai/settings/data-privacy-controls
2. Confirm **"Help improve Claude"** (or equivalent training toggle) is **OFF**
3. In Claude Code, record the attestation:
   ```
   /secops attest training-opt-out
   ```
   This updates your `tasks/<person>/SECOPS.md` with a 30-day expiry. The SessionStart hook will warn when it's stale.

### 15b. GitHub two-factor authentication

If you signed up with **"Continue with Google"** using your corporate Google account, your login is already protected by Google Workspace 2FA — **no separate GitHub 2FA setup needed**. Skip to 15c.

If you created a GitHub account with username/password (not Google SSO):

1. Go to [github.com/settings/security](https://github.com/settings/security)
2. Under **"Two-factor authentication"**, click **Enable**. Use an authenticator app (TOTP) or hardware key — **not SMS**.
3. Generate 2–3 recovery codes and store them in a password manager.
4. If you have a `gh` CLI token, refresh it so the API returns the `two_factor_authentication` field:
   ```bash
   gh auth refresh -s read:user
   gh api /user --jq '.two_factor_authentication'   # should print: true
   ```
5. Record the attestation:
   ```
   /secops attest 2fa
   ```

### 15c. Claude account 2FA

Corporate Google SSO covers this (same reasoning as 15b). If you're not on Google SSO, enable 2FA at https://claude.ai/settings/account (authenticator app preferred), then record:

```
/secops attest 2fa
```

(The `/secops attest 2fa` attestation covers both GitHub and Claude account 2FA.)

### 15d. Conversation hygiene

A few rules to internalize before you start using Claude Code on this repo:

- **Claude conversations are logs.** Treat them like commit messages — don't paste customer PHI, credentials, or anything you wouldn't write in a PR description. `**/PHI/**` and patient-data paths are gitignored, but that only stops commits, not chat transcripts.
- **The `.claude/` directory is shared.** Skills, agents, hooks, settings, and MEMORY files in `.claude/` are checked into git and loaded across every session for every teammate. A personal reminder belongs in your user memory at `~/.claude/memory/`, not the project's `.claude/memory/`.
- **The task gate is real.** Edits outside the exempt list (`tasks/*`, `.claude/state/*`, `.claude/settings*.json`, `.claude/sync-log.md`, `.claude/MEMORY.md`, `.claude/memory/*`) require an active task. This is a feature — it forces every change to be captured somewhere the team can find it.
- **Strategy and Lessons must be captured inline.** When a non-obvious decision or insight lands, add a `<!-- STRATEGY CONTENT -->` or `<!-- LESSONS LEARNED -->` block to the active task **in the same turn** — not as a deferred cleanup pass. The `/strategy` and `/lessons` skills only surface what was written.

### 15e. Integration awareness — MCP servers, plugins, agents

The project uses a security allowlist in `project.yml` (`security.approved_skills`, `approved_mcps`, `approved_plugins`, `approved_agents`). The `project-secops` agent audits what's actually installed against the allowlist at session start.

Before adding a new MCP server, plugin, or agent:

1. Understand what data it accesses. MCP servers run in your shell and can read files, make network requests, hold credentials. Review the server's source (or at minimum its README) before approving.
2. Add it to the corresponding `approved_*` list in `project.yml` under an active task. This is how the team audits what tools touch project data.
3. If the MCP server requires an API token or OAuth, store secrets in your user-scoped config (`~/.claude/`) — never in the project `.env`. The `.gitignore` blocks `.env` from commits, but user-scoped secrets are the safer default.
4. For MCP servers that bridge to external services, assume every piece of context you share with Claude during that session may be transmitted to the external service. Do not share PHI or other regulated data through those bridges.

`chrome-devtools` and `file-locator` are already approved in this project. They do not need special handling.

### 15f. Register as a team member

> **✨ Or just ask Claude**: *"Add me to the team roster. I'm Jane Smith, GitHub username `jsmith`, email `jane.smith@globallogic.com`, role 'Regulatory Affairs'."* Claude edits `project.yml`, creates `tasks/jsmith/000-index.md` for you (lowercase first name as the task folder), and runs `/secops check` to confirm your entry is wired correctly. You do **not** need to know YAML or hand-edit `project.yml`.

The manual steps (what Claude does under the hood):

1. Open `project.yml`.
2. Add yourself to `team.active` — name, GitHub username, task folder (lowercase first name), role, email on an approved domain (see `security.approved_email_domains`), and `added: <YYYY-MM-DD>`.
3. Open a Claude Code session and run `/secops check` (or just start a new session — the SessionStart hook runs it automatically). The hook writes your `tasks/<person>/SECOPS.md` file with a 7-day freshness cycle and a 30-day attestation cycle.

---

## 16. Browser Automation Setup (`web-control`) — Optional

> **This step is optional**. Only relevant if a skill in this project leans on the **`web-control`** shared infrastructure (e.g., `change-control`'s internal-review tier driving Google Docs under your corporate identity).
>
> **✨ Or just ask Claude**: *"Set up web-control for me."* / *"Walk me through signing in to the debug Chrome."* Claude runs the install, the smoke test, and the first-launch sign-in flow — you only sign into Google in the browser window that pops up.
>
> Background: when org policy denies the Workspace API scopes that would let us automate Google Docs / Drive directly, `web-control` drives a dedicated Chrome browser running under your already-authenticated corporate identity. See `.claude/skills/web-control/README.md` for the full design rationale.

### What gets installed

| Component | macOS | Windows / WSL |
|---|---|---|
| **Google Chrome** | `brew install --cask google-chrome` (skipped if already at `/Applications/Google Chrome.app`) | `apt install google-chrome-stable` from Google's official repo + Ubuntu 24.04 runtime libs (`libgtk-3-0t64`, `libasound2t64`, …) |
| **Python deps for CDP** (`websocket-client`, `pyyaml`) | `pip install --user` | `apt install python3-websocket python3-yaml` (avoids PEP 668) |
| **Dedicated debug profile dir** | `~/.config/google-chrome-debug` | Same |
| **Launcher script** | `.claude/skills/web-control/scripts/launch-debug-chrome.sh` | Same |
| **WSLg sanity check** | n/a | `setup.sh` warns if `/mnt/wslg` is missing or `WAYLAND_DISPLAY` is empty |

### What does NOT get installed

- Does NOT touch your everyday Chrome profile (uses a separate `--user-data-dir`).
- Does NOT configure any Windows ↔ WSL networking bridge — the browser-automation workflow runs entirely Linux-side; the Windows host is only the display surface (via WSLg).
- Is NOT the same as Anthropic's `chrome-devtools-mcp` MCP server. The production internal-review workflow does not depend on it.

### One-time first-launch setup

After `setup.sh` (or manual install), the first time you actually use it:

1. Launch:
   ```bash
   bash .claude/skills/web-control/scripts/launch-debug-chrome.sh
   ```
2. A small Chrome window (~800×700) appears — on WSL it shows via WSLg as a regular Windows window. Pointed at `https://drive.google.com`.
3. Sign in with your **GlobalLogic** Google account. Complete SSO + MFA as you would in any browser.
4. The session cookies persist on disk in the dedicated profile dir. Subsequent automation runs reuse the session.

If your corporate Google session expires (Workspace default ~14 days), re-launching the debug Chrome lands you back on the sign-in page; sign in again.

### Verifying setup worked

```bash
python3 .claude/skills/web-control/actions/status.py
```

Should print Chrome binary, version, profile dir, and current state.

### Stopping when done

```bash
python3 .claude/skills/web-control/actions/stop.py
```

Kills only Chrome processes whose `--user-data-dir` matches the debug profile. Your everyday Chrome is untouched.

### Skipping this step

If no installed skill needs browser automation, you can skip it entirely. `setup.sh` auto-detects whether `web-control` is present; if so, it runs this setup; if not, it's a no-op. Re-run anytime via:

```bash
bash setup.sh
```

---

## 17. Semantic File Search Setup (`file-locator`) — Optional

> **This step is handled automatically by `setup.sh`**. Only relevant because the project ships the **`file-locator`** skill — a local MCP server giving Claude Code agents semantic file search over the project corpus.
>
> **✨ Or just ask Claude**: *"The file-locator MCP is failing to connect."* / *"Set up file-locator for me."* Claude diagnoses the venv state and recreates it via `uv` — no Python knowledge required.
>
> Background: `file-locator` answers natural-language queries ("where do we argue MDDS classification?") with ranked `(path, summary, score)` tuples, so agents pick which whole files to read instead of blindly globbing. Fully local — `fastembed` BGE-small ONNX + SQLite FTS5; no API calls during indexing.

### What gets installed

| Component | Where | Notes |
|---|---|---|
| **Python venv** | `tools/file-locator-mcp/.venv` | Created via `uv` (Python 3.12). Gitignored. |
| **Python deps** (`fastembed`, `mcp`) | inside that venv | From committed `tools/file-locator-mcp/requirements.txt`. |
| **BGE-small ONNX model** (~130 MB) | `~/.cache/fastembed/` | **Not** downloaded by setup — downloads on first query. Internet required once; offline after. |

### What does NOT get installed (already committed)

- The search index (`tools/file-locator-mcp/index.db`) is **committed** — a fresh clone has a current index. CI refreshes on `main` changes.
- The MCP registration (`.mcp.json` `file-locator` entry) is **committed**.

So the only per-clone work is the venv, which `setup.sh` does for you.

### Verifying setup worked

After `setup.sh` finishes, **restart Claude Code** (MCP servers load only at session start), then confirm the tool is available — `mcp__file-locator__locate` should be in the tool set.

### Troubleshooting — MCP shows `✗ Failed to connect`

If `/mcp` (or `claude mcp list`) shows `file-locator: … ✗ Failed to connect`, the cause is almost always a **missing Python venv**. Three ways to fix it, easiest first:

1. **Ask Claude to resolve it (recommended).** In a session, say *"the file-locator MCP is failing to connect."* Claude diagnoses the missing venv and recreates it.
2. **Re-run the setup script** — it's idempotent: `bash setup.sh`
3. **Create the venv manually**:
   ```bash
   uv venv --python 3.12 tools/file-locator-mcp/.venv
   uv pip install --python tools/file-locator-mcp/.venv/bin/python -r tools/file-locator-mcp/requirements.txt
   ```

After any of these, **restart Claude Code** — MCP servers connect only at session start.

### Refreshing the index manually

```bash
bash tools/file-locator-mcp/rebuild.sh          # incremental
bash tools/file-locator-mcp/rebuild.sh --full   # from scratch
```

---

## 18. Confirm Everything Is Wired Up

> **✨ Just ask Claude**: *"Run the security posture check and the best-practices audit, then tell me if I need to fix anything."* Claude runs both, summarizes the results, and walks you through any failures (often by fixing them for you).

The underlying commands, if you prefer to run them yourself:

```
/secops check         # security posture check
/best-practices       # project-wide audit against the shared skill registry
```

Both should exit with zero Required FAILs after you complete the steps above. If anything fails, the output includes the specific fix for each check.

---

## You're Done!

Setup is complete. Head over to **[`how-to-guide.md`](how-to-guide.md)** to learn how to use VS Code, launch Claude Code, and start working with the project day-to-day.

If you're a *team lead* starting a new MedTech project (not just joining this one), see **[`new-project-bootstrap.md`](new-project-bootstrap.md)** for the from-scratch walkthrough.

---

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-05-30 | Ben Xavier | Follow-up to the initial rewrite: added an **"ask Claude"** layer for non-engineer users. New top-banner explaining the pattern. "✨ Or just ask Claude" callouts added at steps 11 (Git + SSH), 12 (VS Code extensions), 14 (repo clone), 15 banner (security posture overview), 15f (team registration), 16 (web-control), 17 (file-locator), 18 (confirmation). Added a third row to the "Choose Your Path" table: "Claude-assisted" — for users who already have Claude Code from another project. Under-the-hood manual commands still present so engineers can see what Claude is doing. |
| 2026-05-30 | Ben Xavier | Rewrote setup.md as a full new-contributor onboarding guide modeled on the arthrex-pccp sister project (task ben/069). Adopted 18-section structure: admin → terminal → VS Code → WSL → GitHub account → Claude account → Google Drive → Claude Desktop → automated/manual install paths → Homebrew → Node + core utils → document tools → Git + SSH → VS Code extensions → Claude Code CLI → repo clone → security posture (training opt-out, 2FA, conversation hygiene, integration awareness, team registration) → web-control (optional) → file-locator (optional) → confirmation. Companion `setup.sh` introduced for the automated path. Folded prior security-posture content (training opt-out, 2FA, `/secops attest`) into §15 rather than keeping it as a separate doc. |
| 2026-04-20 | Ben Xavier | Initial version (now superseded) — created under task ben/018 sync-skills to close the four security-posture best-practices FAILs (training opt-out, GitHub 2FA, conversation hygiene, integration awareness). Content folded into §15 of the rewrite. |
