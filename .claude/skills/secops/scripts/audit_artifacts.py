#!/usr/bin/env python3
"""
audit_artifacts.py — Static-analysis SecOps audit for installed Claude artifacts.

Scans `.claude/skills/`, `.claude/agents/`, `.claude/hooks/`, and the merged
`settings.json` / `settings.local.json` for trojan-horse-style red flags that
the existing 16 SessionStart checks (identity, allowlists) do not cover.

Pure stdlib — no `pip install`, no network calls. Output is JSON to stdout
plus a human summary on stderr. Exit code:

    0  no Critical/High findings
    1  Critical or High findings present

Usage:
    python3 audit_artifacts.py [--project-dir DIR] [--json]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Rule definitions
# ---------------------------------------------------------------------------

# A rule fires when `pattern` matches a line in a file the rule applies to.
# `applies_to` is a set of file-suffix groups: {"sh","py","md","json"}.
# `severity` is Critical / High / Medium / Low.
# `category` groups findings in the report.
# `description` is shown in the report.
# `suppress_if_path_contains` skips the finding if the file path contains any
#   of the listed substrings (used for setup scripts that legitimately do the
#   thing the rule warns about).

@dataclass(frozen=True)
class Rule:
    id: str
    category: str
    severity: str
    pattern: str
    description: str
    applies_to: tuple = ("sh", "py")
    suppress_if_path_contains: tuple = ()
    # When True, matches in `.py` files that fall entirely inside a string
    # literal (docstring, error message, print arg) are dropped. Used for
    # rules where the dangerous behavior is *executing* the pattern, not
    # *mentioning* it in user-facing text.
    skip_in_py_string_literals: bool = False


RULES: tuple[Rule, ...] = (
    # ---- 1. External network calls ----
    Rule(
        id="NET-CURL-PIPE-SH",
        category="external-execution",
        severity="Critical",
        pattern=r"curl\s+[^|]*\|\s*(sh|bash|zsh|python|perl)\b",
        description="Pipes curl output directly into a shell — classic remote-code-execution vector.",
    ),
    Rule(
        id="NET-WGET-PIPE-SH",
        category="external-execution",
        severity="Critical",
        pattern=r"wget\s+[^|]*\|\s*(sh|bash|zsh|python|perl)\b",
        description="Pipes wget output directly into a shell.",
    ),
    Rule(
        id="NET-RAW-IP",
        category="external-network",
        severity="High",
        pattern=r"\b(curl|wget|nc|ncat|http)\s+[^\s]*\b(?:\d{1,3}\.){3}\d{1,3}\b",
        description="Outbound network call to a raw IP address (no DNS) — common in C2-style beacons.",
    ),
    Rule(
        id="NET-NONSTANDARD-PORT",
        category="external-network",
        severity="High",
        pattern=r"\bnc(?:at)?\s+(?:-\w+\s+)*[a-zA-Z0-9.\-]+\s+\d+\b",
        description="Direct netcat invocation — typical reverse-shell / data-exfil pattern.",
    ),
    Rule(
        id="NET-EXFIL-POST",
        category="external-network",
        severity="High",
        pattern=r"curl\s+[^\n]*-X\s*POST[^\n]*--data[- ]?binary",
        description="POST upload via curl --data-binary — possible exfil channel.",
    ),

    # ---- 2. File operations escaping the project ----
    Rule(
        id="FS-RM-RF-HOME",
        category="filesystem-escape",
        severity="Critical",
        pattern=r"\brm\s+(?:-\w*\s+)*(?:-rf|-fr|-Rf|-fR)\s+(?:\$HOME|~/|/home/|/Users/|/etc/|/usr/|/var/|/private/)",
        description="rm -rf targeting home or system directory.",
    ),
    Rule(
        id="FS-WRITE-SYSTEM",
        category="filesystem-escape",
        severity="High",
        pattern=r"(?:>|>>|tee\b|cp\s+\S+|mv\s+\S+)\s+(?:/etc/|/usr/|/var/|/private/etc/)",
        description="Writes into a system directory.",
        # web-control's Chrome installer legitimately writes the apt source list
        # under /etc/apt/sources.list.d/ as part of the documented setup flow.
        suppress_if_path_contains=("web-control/scripts/install-chrome-wsl.sh",),
    ),
    Rule(
        id="FS-CHMOD-WORLD",
        category="privilege",
        severity="High",
        pattern=r"\bchmod\s+(?:-\w+\s+)*(?:777|a\+w)\b",
        description="World-writable chmod — opens files to any local user.",
    ),
    Rule(
        id="FS-CHMOD-SETUID",
        category="privilege",
        severity="Critical",
        pattern=r"\bchmod\s+(?:-\w+\s+)*(?:[ug]\+s|4\d{3}|2\d{3})\b",
        description="Setuid/setgid bit — escalates privileges.",
    ),
    Rule(
        id="FS-SUDO",
        category="privilege",
        severity="High",
        pattern=r"^\s*sudo\b",
        description="Skill invokes sudo — should not be needed for any approved skill.",
    ),

    # ---- 3. Edits to load-bearing project config from inside skill scripts ----
    Rule(
        id="CFG-PROJECT-YML",
        category="config-tamper",
        severity="High",
        pattern=r"(?:>|>>|tee\b|sed\s+-i|yq\s+(?:-\w+\s+)*-i)\s+[^\n]*project\.yml",
        description="In-place edit of project.yml — should only happen via documented setup or user action.",
        suppress_if_path_contains=("medtech-docs",),  # init owns this
    ),
    Rule(
        id="CFG-CLAUDE-MD",
        category="config-tamper",
        severity="High",
        pattern=r"(?:>|>>|tee\b|sed\s+-i)\s+[^\n]*\bCLAUDE\.md\b",
        description="In-place edit of CLAUDE.md from a skill script.",
        suppress_if_path_contains=("medtech-docs",),
    ),
    Rule(
        id="CFG-GIT-CONFIG-GLOBAL",
        category="config-tamper",
        severity="High",
        pattern=r"git\s+config\s+(?:-\w+\s+)*(?:--global|--system)\b",
        description="Mutates git config at global/system scope — should always be repo-local.",
        skip_in_py_string_literals=True,
    ),
    Rule(
        id="CFG-GITIGNORE",
        category="config-tamper",
        severity="Medium",
        pattern=r"(?:>|>>|tee\b|sed\s+-i)\s+[^\n]*\.gitignore\b",
        description="In-place edit of .gitignore — verify the entries are documented.",
    ),

    # ---- 4. Credential / secret reads ----
    Rule(
        id="SEC-SSH-KEY-READ",
        category="credential-access",
        severity="Critical",
        pattern=r"(?:cat|cp|mv|tar|tee|less|more|head|tail|gpg)\s+[^\n]*~/.ssh/id_(?:rsa|ed25519|ecdsa|dsa)\b",
        description="Reads a private SSH key.",
    ),
    Rule(
        id="SEC-AUTHORIZED-KEYS",
        category="credential-access",
        severity="Critical",
        pattern=r"(?:>|>>|tee\b)\s+[^\n]*~/.ssh/authorized_keys",
        description="Writes to ~/.ssh/authorized_keys — persistence backdoor.",
    ),
    Rule(
        id="SEC-AWS-CREDENTIALS",
        category="credential-access",
        severity="Critical",
        pattern=r"(?:cat|cp|mv|tar|tee|less|head|tail)\s+[^\n]*~/\.aws/(?:credentials|config)",
        description="Reads AWS credentials file.",
    ),
    Rule(
        id="SEC-GNUPG",
        category="credential-access",
        severity="Critical",
        pattern=r"(?:cat|cp|mv|tar)\s+[^\n]*~/\.gnupg/",
        description="Reads GnuPG keyring.",
    ),
    Rule(
        id="SEC-DOTENV",
        category="credential-access",
        severity="High",
        pattern=r"(?:cat|cp|mv|tar|tee|head|tail|less|more|source\b|\.\s+)\s+[^\n]*\.env(?:\.local|\.production)?\b",
        description="Reads or sources a .env file from a skill script.",
        skip_in_py_string_literals=True,
    ),
    Rule(
        id="SEC-TOKEN-ENV",
        category="credential-access",
        severity="High",
        pattern=r"\$\{?(?:GITHUB_TOKEN|ANTHROPIC_API_KEY|OPENAI_API_KEY|AWS_SECRET_ACCESS_KEY|HF_TOKEN)\b",
        description="Reads a secret env var — verify it isn't shipped outbound.",
    ),

    # ---- 5. Obfuscation / dynamic execution ----
    Rule(
        id="EXEC-BASE64-PIPE-SH",
        category="obfuscated-execution",
        severity="Critical",
        pattern=r"base64\s+(?:-\w+\s+)*-d[^\n|]*\|\s*(?:sh|bash|zsh|python|perl)\b",
        description="Decodes base64 directly into a shell — strong indicator of an obfuscated payload.",
    ),
    Rule(
        id="EXEC-EVAL-SUBSHELL",
        category="obfuscated-execution",
        severity="High",
        pattern=r"\beval\s+\$\(",
        description="`eval $(...)` — dynamic evaluation of subshell output.",
        suppress_if_path_contains=("secops/scripts/audit_artifacts.py",),
    ),
    Rule(
        id="EXEC-EVAL-VAR",
        category="obfuscated-execution",
        severity="Medium",
        pattern=r"\beval\s+(?:\"\$|\$[A-Za-z_])",
        description="`eval` of a variable — dynamic evaluation that may run untrusted input.",
        suppress_if_path_contains=("/tests/", "/test-",),
    ),
    Rule(
        id="EXEC-PYTHON-EXEC",
        category="obfuscated-execution",
        severity="Medium",
        pattern=r"\b(?:exec|eval)\s*\(\s*(?:base64|codecs\.decode|binascii\.unhexlify)",
        description="Python exec()/eval() over a decoded payload.",
        applies_to=("py",),
    ),

    # ---- 6. Persistence ----
    Rule(
        id="PERSIST-SHELL-RC",
        category="persistence",
        severity="High",
        pattern=r"(?:>|>>|tee\b)\s+[^\n]*~/(?:\.bashrc|\.zshrc|\.profile|\.bash_profile|\.zprofile)",
        description="Writes to a shell rc file — persistence across user sessions.",
    ),
    Rule(
        id="PERSIST-CRONTAB",
        category="persistence",
        severity="High",
        pattern=r"\bcrontab\s+(?:-\w+\s+)*-",
        description="Installs a crontab entry from stdin.",
    ),
    Rule(
        id="PERSIST-LAUNCHD",
        category="persistence",
        severity="High",
        pattern=r"(?:>|>>|cp\s+\S+|mv\s+\S+)\s+[^\n]*~/Library/LaunchAgents/",
        description="Installs a macOS LaunchAgent — persistence.",
    ),
    Rule(
        id="PERSIST-SYSTEMD",
        category="persistence",
        severity="High",
        pattern=r"(?:>|>>|cp\s+\S+|mv\s+\S+)\s+[^\n]*(?:/etc/systemd/|~/\.config/systemd/)",
        description="Installs a systemd unit — persistence.",
    ),
)


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    rule_id: str
    category: str
    severity: str
    file: str
    line: int
    snippet: str
    description: str

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

SUFFIX_GROUP = {
    ".sh": "sh",
    ".bash": "sh",
    ".zsh": "sh",
    ".py": "py",
    ".md": "md",
    ".json": "json",
    ".yml": "yml",
    ".yaml": "yml",
}

# Files we never scan even if they end up under .claude/.
EXCLUDE_DIR_NAMES = {"__pycache__", ".venv", "venv", "node_modules", ".git"}


def _python_string_literal_spans(text: str) -> dict[int, list[tuple[int, int]]]:
    """Return a map of 1-based line number → list of (start_col, end_col) spans
    that fall inside a Python string literal (incl. f-string body) or comment
    on that line. Columns are 0-based, end exclusive. Used to test whether a
    regex match falls *inside* a string literal even if other code shares the
    same line (e.g., the trailing comma after a multi-line string)."""
    import io
    import token
    import tokenize

    spans: dict[int, list[tuple[int, int]]] = {}
    try:
        toks = list(tokenize.tokenize(io.BytesIO(text.encode("utf-8")).readline))
    except (tokenize.TokenizeError, SyntaxError, IndentationError):
        return spans

    string_like = {token.STRING, tokenize.COMMENT}
    fstring_mid = getattr(tokenize, "FSTRING_MIDDLE", None)
    if fstring_mid is not None:
        string_like.add(fstring_mid)

    lines = text.splitlines()
    for tok in toks:
        if tok.type not in string_like:
            continue
        (sr, sc), (er, ec) = tok.start, tok.end
        if sr == er:
            spans.setdefault(sr, []).append((sc, ec))
        else:
            # Multi-line string: cover from sc to EOL on first line,
            # full lines in between, and 0..ec on last line.
            spans.setdefault(sr, []).append((sc, len(lines[sr - 1]) if sr - 1 < len(lines) else 10**9))
            for ln in range(sr + 1, er):
                spans.setdefault(ln, []).append((0, len(lines[ln - 1]) if ln - 1 < len(lines) else 10**9))
            spans.setdefault(er, []).append((0, ec))
    return spans


def _looks_text(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
    except OSError:
        return False
    return b"\x00" not in chunk


def _iter_target_files(roots: Iterable[Path]) -> Iterable[Path]:
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            yield root
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIR_NAMES]
            for fn in filenames:
                p = Path(dirpath) / fn
                yield p


def _file_group(path: Path) -> str | None:
    return SUFFIX_GROUP.get(path.suffix)


def scan_files(project_dir: Path) -> list[Finding]:
    roots = [
        project_dir / ".claude" / "skills",
        project_dir / ".claude" / "agents",
        project_dir / ".claude" / "hooks",
    ]

    findings: list[Finding] = []
    compiled = [(r, re.compile(r.pattern)) for r in RULES]

    for path in _iter_target_files(roots):
        group = _file_group(path)
        if group is None:
            continue
        if not _looks_text(path):
            continue

        rel = path.relative_to(project_dir)
        rel_str = str(rel)

        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue

        py_lit_spans: dict[int, list[tuple[int, int]]] | None = None  # lazy

        for rule, regex in compiled:
            if group not in rule.applies_to:
                continue
            if any(s in rel_str for s in rule.suppress_if_path_contains):
                continue

            if rule.skip_in_py_string_literals and group == "py" and py_lit_spans is None:
                py_lit_spans = _python_string_literal_spans(text)

            for lineno, line in enumerate(text.splitlines(), start=1):
                m = regex.search(line)
                if not m:
                    continue
                if (
                    rule.skip_in_py_string_literals
                    and group == "py"
                    and py_lit_spans is not None
                ):
                    spans = py_lit_spans.get(lineno, [])
                    ms, me = m.start(), m.end()
                    if any(s <= ms and me <= e for s, e in spans):
                        continue
                findings.append(
                    Finding(
                        rule_id=rule.id,
                        category=rule.category,
                        severity=rule.severity,
                        file=rel_str,
                        line=lineno,
                        snippet=line.strip()[:200],
                        description=rule.description,
                    )
                )
    return findings


# ---------------------------------------------------------------------------
# Symlink + settings.json checks (structural, not regex)
# ---------------------------------------------------------------------------

def scan_symlinks(project_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    proj_real = project_dir.resolve()
    base = project_dir / ".claude"
    if not base.exists():
        return findings
    for dirpath, dirnames, filenames in os.walk(base, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIR_NAMES]
        for name in filenames + dirnames:
            p = Path(dirpath) / name
            if not p.is_symlink():
                continue
            try:
                target = p.resolve()
            except (OSError, RuntimeError):
                findings.append(
                    Finding(
                        rule_id="LINK-BROKEN",
                        category="symlink-escape",
                        severity="Medium",
                        file=str(p.relative_to(project_dir)),
                        line=0,
                        snippet=f"-> {os.readlink(p)}",
                        description="Symlink does not resolve.",
                    )
                )
                continue
            try:
                target.relative_to(proj_real)
            except ValueError:
                findings.append(
                    Finding(
                        rule_id="LINK-ESCAPE",
                        category="symlink-escape",
                        severity="Critical",
                        file=str(p.relative_to(project_dir)),
                        line=0,
                        snippet=f"-> {target}",
                        description="Symlink under .claude/ resolves outside the project tree.",
                    )
                )
    return findings


def scan_settings(project_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    for rel in (".claude/settings.json", ".claude/settings.local.json"):
        sp = project_dir / rel
        if not sp.exists():
            continue
        try:
            data = json.loads(sp.read_text())
        except (OSError, json.JSONDecodeError):
            continue

        # Hooks: every command path should resolve inside the project.
        hooks = data.get("hooks", {})
        if isinstance(hooks, dict):
            for event, entries in hooks.items():
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    for h in (entry or {}).get("hooks", []) or []:
                        cmd = (h or {}).get("command", "")
                        if not isinstance(cmd, str):
                            continue
                        # Strip wrapping quotes / env-var refs like "$CLAUDE_PROJECT_DIR"
                        normalized = cmd.replace(
                            '"$CLAUDE_PROJECT_DIR"', str(project_dir)
                        ).replace("$CLAUDE_PROJECT_DIR", str(project_dir))
                        # First whitespace-separated token = the actual binary
                        first = normalized.strip().split()[0] if normalized.strip() else ""
                        first = first.strip('"').strip("'")
                        if not first:
                            continue
                        # Allow bare command names (PATH lookup) and project-internal paths
                        if "/" not in first:
                            continue
                        try:
                            real = Path(first).resolve()
                            real.relative_to(project_dir.resolve())
                        except (OSError, ValueError):
                            findings.append(
                                Finding(
                                    rule_id="HOOK-OUTSIDE-PROJECT",
                                    category="hook-escape",
                                    severity="High",
                                    file=rel,
                                    line=0,
                                    snippet=f"{event}: {cmd[:160]}",
                                    description="Hook command resolves outside the project tree.",
                                )
                            )

        # MCP servers: surface unknown commands so they can be reviewed.
        mcps = data.get("mcpServers", {})
        if isinstance(mcps, dict) and mcps:
            for name, spec in mcps.items():
                cmd = (spec or {}).get("command") if isinstance(spec, dict) else None
                if cmd:
                    findings.append(
                        Finding(
                            rule_id="MCP-LOCAL-COMMAND",
                            category="mcp-review",
                            severity="Low",
                            file=rel,
                            line=0,
                            snippet=f"{name}: {cmd[:160]}",
                            description="Local MCP server command — confirm binary is trusted.",
                        )
                    )
    return findings


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    @property
    def by_severity(self) -> dict[str, int]:
        out = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for f in self.findings:
            out[f.severity] = out.get(f.severity, 0) + 1
        return out

    def to_json(self) -> str:
        return json.dumps(
            {
                "summary": self.by_severity,
                "findings": [f.to_dict() for f in self.findings],
            },
            indent=2,
        )


def render_human(report: Report) -> str:
    if not report.findings:
        return "Skill/agent audit: no findings.\n"
    sev = report.by_severity
    lines = [
        "Skill/agent audit — findings:",
        f"  Critical: {sev['Critical']}",
        f"  High:     {sev['High']}",
        f"  Medium:   {sev['Medium']}",
        f"  Low:      {sev['Low']}",
        "",
    ]
    by_file: dict[str, list[Finding]] = {}
    for f in report.findings:
        by_file.setdefault(f.file, []).append(f)
    for file, fs in sorted(by_file.items()):
        lines.append(f"## {file}")
        for f in fs:
            loc = f"L{f.line}" if f.line else "—"
            lines.append(f"  [{f.severity:8}] {f.rule_id:24} {loc:>6}  {f.description}")
            if f.snippet:
                lines.append(f"           {f.snippet}")
        lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-dir",
        default=os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()),
        help="Project root (default: $CLAUDE_PROJECT_DIR or cwd).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON to stdout instead of human-readable summary.",
    )
    args = parser.parse_args(argv)

    project_dir = Path(args.project_dir).resolve()

    findings: list[Finding] = []
    findings.extend(scan_files(project_dir))
    findings.extend(scan_symlinks(project_dir))
    findings.extend(scan_settings(project_dir))

    report = Report(findings=findings)

    if args.json:
        sys.stdout.write(report.to_json() + "\n")
    else:
        sys.stdout.write(render_human(report))

    sev = report.by_severity
    return 1 if (sev["Critical"] or sev["High"]) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
