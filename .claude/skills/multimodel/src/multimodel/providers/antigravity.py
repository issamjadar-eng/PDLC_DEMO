"""Google/Gemini, via the Antigravity CLI (`agy`) on Google OAuth.

The older `gemini` CLI is not treated as an alternative here: the sister project
that originated this adapter recorded Google withdrawing Gemini CLI OAuth for
individual accounts (mid-2026) and moving the terminal experience to Antigravity.
If a `gemini` binary answers on your machine, add it as a custom provider rather
than "fixing" this adapter to call it.

Install from the vendor's Antigravity CLI page, then run `agy` once
interactively to complete OAuth.

Authentication is checked by asking the tool (`agy models` answers "Please sign
in" when it is not), never by looking for a token file — the file's location
changed between CLI versions and a cached credential proves nothing anyway.

READ-ONLY PROJECT ACCESS = A WORKSPACE-BOUND PROJECT, NO PERMISSION RULE.
The permission engine (antigravity.google/docs/permissions) auto-allows reads
and writes *inside the active project directory*; everything else (shell, web)
defaults to ask, and headless mode soft-denies whatever would ask. Measured on
1.1.27 in print mode: attached to a project whose `folderUri` is this
workspace, `view_file` ran with no rule at all, while `write_to_file` was
auto-denied ("a tool required the write_file permission") and the run ended
with no output. Under the default CLI project — which has no workspace bound —
reads were denied too. So project mode here means: resolve (or, via `setup`,
create) a project file under `~/.gemini/config/projects/` whose `folderUri` is
the project root, and pass `--project <id>`. Nothing global is written. The
only way writes could land is a `write_file(...)` allow rule in the user's own
CLI settings covering the project, so the adapter refuses project mode when it
sees one. `--mode plan` is deliberately NOT passed: it pushed the model onto
shell commands, which are denied. `--dangerously-skip-permissions` and
`--sandbox` are never passed (both let writes land). The `verify` action, not
this docstring, is the evidence on any given machine and CLI version.

Cleanest output contract of the CLI providers: `--output-format json
--json-schema FILE` returns an envelope with an already-parsed
`structured_output` object, so no text scraping is needed.
"""

from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path
from typing import Any

from .. import jsonx
from ..base import Provider, resolve_binary, run_cli
from ..types import Response

#: The CLI's own settings file — read to check for a write grant, never written.
SETTINGS = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
#: Where the CLI keeps its projects (one JSON per project, `id` = file stem).
PROJECTS_DIR = Path.home() / ".gemini" / "config" / "projects"
#: The read tools the CLI exposes (its own listing, 1.1.27).
READ_TOOLS = ("view_file", "list_dir", "grep_search", "find_by_name")
WRITE_ACTION = "write_file"
READ_ACTION = "read_file"

_SLUG = re.compile(r"[^a-z0-9]+")


# -- permission rules ----------------------------------------------------------


def _rule_target(rule: str, action: str) -> str | None:
    rule = rule.strip()
    if rule.startswith(action + "(") and rule.endswith(")"):
        return rule[len(action) + 1 : -1].strip()
    return None


def _covers(target: str, root: Path) -> bool:
    if target == "*":
        return True
    try:
        expanded = Path(target).expanduser()
        if not expanded.is_absolute():
            expanded = root / expanded
        expanded = expanded.resolve()
    except (OSError, RuntimeError):
        return False
    root = root.resolve()
    return expanded == root or root.is_relative_to(expanded)


def write_rules_clear(settings_path: Path | None = None, root: Path | None = None) -> tuple[bool, str]:
    """True when no `write_file(...)` allow rule in the CLI settings covers the
    project root (a write grant implies read and would let writes land), and no
    `read_file(...)` deny rule covers it (which would blind the agent)."""
    settings_path = settings_path or SETTINGS
    root = (root or Path.cwd()).resolve()
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return True, "no CLI settings file — defaults apply"
    except (OSError, json.JSONDecodeError):
        return False, f"could not read {settings_path}"
    permissions = settings.get("permissions") or {}
    for rule in (str(r) for r in (permissions.get("allow") or [])):
        target = _rule_target(rule, WRITE_ACTION)
        if target is not None and _covers(target, root):
            return False, (
                f"{rule!r} in permissions.allow of {settings_path} grants WRITES over the "
                "project (write_file implies read_file); remove it or scope it away from the project"
            )
    for rule in (str(r) for r in (permissions.get("deny") or [])):
        target = _rule_target(rule, READ_ACTION)
        if target is not None and _covers(target, root):
            return False, f"{rule!r} in permissions.deny of {settings_path} denies reading the project"
    return True, "no write grant over the project in CLI settings"


# -- workspace-bound project ---------------------------------------------------


def folder_uri(root: Path) -> str:
    return root.resolve().as_uri()


def project_slug(root: Path) -> str:
    return _SLUG.sub("-", root.resolve().name.lower()).strip("-") or "project"


def find_workspace_project(root: Path, projects_dir: Path | None = None) -> tuple[str, Path] | None:
    """The first project file whose `folderUri` is exactly this root, as (id, path).

    Reuses whatever project the user (or the CLI) already bound to the
    workspace — a team that runs Antigravity as its primary agent already has
    one, and a second binding would only confuse its project list."""
    projects_dir = projects_dir or PROJECTS_DIR
    if not projects_dir.is_dir():
        return None
    wanted = folder_uri(root)
    for path in sorted(projects_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        resources = ((data.get("projectResources") or {}).get("resources")) or []
        if any(isinstance(r, dict) and r.get("folderUri") == wanted for r in resources):
            project_id = str(data.get("id") or path.stem)
            return project_id, path
    return None


def ensure_workspace_project(root: Path, projects_dir: Path | None = None) -> tuple[str, Path, bool]:
    """Return (id, path, created). Creates `multimodel-<slug>.json` only when no
    project is bound to this workspace yet; never modifies an existing file."""
    projects_dir = projects_dir or PROJECTS_DIR
    found = find_workspace_project(root, projects_dir)
    if found:
        return found[0], found[1], False
    project_id = f"multimodel-{project_slug(root)}"
    path = projects_dir / f"{project_id}.json"
    if path.exists():
        # Same id, different folder: do not clobber someone else's project.
        raise FileExistsError(f"{path} exists but is not bound to {root}")
    projects_dir.mkdir(parents=True, exist_ok=True)
    document = {
        "id": project_id,
        "name": f"{root.resolve().name} (multimodel)",
        "projectResources": {"resources": [{"folderUri": folder_uri(root)}]},
    }
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return project_id, path, True


class AntigravityProvider(Provider):
    def __init__(self, name: str, cfg: dict[str, Any]) -> None:
        super().__init__(name, cfg)
        self.command = cfg.get("command", "agy")
        self.model = cfg.get("model")
        self.effort = cfg.get("effort")
        self.project_id = cfg.get("project_id")  # override; else resolved from folderUri

    # -- project resolution -------------------------------------------------

    def _resolve_project(self, root: Path) -> tuple[str | None, str]:
        if self.project_id:
            return str(self.project_id), f"project_id {self.project_id!r} from config"
        found = find_workspace_project(root)
        if found:
            return found[0], f"project {found[0]!r} bound to {root} ({found[1].name})"
        return None, (
            f"no Antigravity project is bound to {root} — run the multimodel setup action "
            "(it creates one under ~/.gemini/config/projects/ only if absent), or set "
            "`project_id` on this provider; keep `workspace: isolated` to stay prompt-only"
        )

    def project_ready(self, root: Path) -> tuple[bool, str]:
        clear, why = write_rules_clear(root=root)
        if not clear:
            return False, why
        project_id, note = self._resolve_project(root)
        if project_id is None:
            return False, note
        return True, note

    # -- availability -------------------------------------------------------

    def available(self) -> tuple[bool, str]:
        resolved = resolve_binary(self.command)
        if not resolved:
            return False, (
                f"Antigravity CLI {self.command!r} not found. Install it from the "
                "vendor's Antigravity CLI page, then run `agy` once to sign in."
            )
        # Ask the tool, not the filesystem. `models` is a cheap metadata call
        # that fails fast and unambiguously when the CLI is not signed in.
        status = run_cli([resolved, "models"], timeout=45)
        combined = f"{status.stdout}{status.stderr}".strip()
        if not status.ok or "sign in" in combined.lower():
            return False, (
                "Antigravity CLI installed but NOT authenticated. Run `agy` once "
                "interactively and sign in with Google."
            )
        count = sum(1 for line in status.stdout.splitlines() if line.strip())
        note = f"Antigravity CLI at {resolved} (signed in; {count} models listed)"
        if self.workspace == "project":
            from ..config import project_root
            ok, why = self.project_ready(project_root())
            note += f"; {why}" if ok else f"; project workspace NOT usable — {why}"
        return True, note

    # -- ask ----------------------------------------------------------------

    def ask(self, prompt: str, schema: dict[str, Any] | None = None, tag: str = "") -> Response:
        ok, reason = self.available()
        if not ok:
            return Response.failure(self.name, reason, tag)

        binary = resolve_binary(self.command) or self.command

        with tempfile.TemporaryDirectory(prefix="mm-agy-") as tmp, self.workdir() as work:
            args = [binary, "-p", prompt, "--output-format", "json",
                    # Align the CLI's own print-mode wait with our timeout so a
                    # hang is reported by whichever fires first, never silently.
                    "--print-timeout", f"{self.timeout}s"]
            if self.workspace == "project":
                ready, why = self.project_ready(work)
                if not ready:
                    return Response.failure(self.name, f"refusing project workspace: {why}", tag)
                project_id, _ = self._resolve_project(work)
                # Attaching to the workspace-bound project is what makes reads
                # auto-allowed; writes stay soft-denied by the permission engine.
                args += ["--project", str(project_id)]
            if schema:
                schema_file = Path(tmp) / "schema.json"
                schema_file.write_text(json.dumps(schema), encoding="utf-8")
                args += ["--json-schema", str(schema_file)]
            if self.model:
                args += ["--model", self.model]
            if self.effort:
                args += ["--effort", self.effort]

            # No --cwd flag in this CLI; the process working directory is the
            # workspace (project root, or an empty temp dir — see base.py).
            result = run_cli(args, self.timeout, cwd=str(work))

        if not result.ok:
            return Response.failure(
                self.name, f"Antigravity CLI {result.error}", tag, result.stdout
            )

        raw = result.stdout.strip()
        try:
            envelope = json.loads(raw)
        except json.JSONDecodeError as exc:
            return Response.failure(
                self.name, f"unparseable envelope: {exc}; got {raw[:200]}", tag, raw
            )

        status = envelope.get("status")
        if status != "SUCCESS":
            return Response.failure(
                self.name, f"status={status!r}: {str(envelope)[:300]}", tag, raw
            )

        usage = envelope.get("usage")
        text = str(envelope.get("response", "")).strip()
        denied = _denial(result.stderr)

        if not schema:
            if not text and denied:
                return Response.failure(self.name, f"no answer: {denied}", tag, raw)
            return Response.success(self.name, text=text, tag=tag, raw=raw, usage=usage)

        data = envelope.get("structured_output")
        required = jsonx.first_required_key(schema)
        if not isinstance(data, dict) or (required and required not in data):
            detail = f"no structured_output with required key {required!r}"
            if denied:
                # The CLI ends a headless run at the first denial with no
                # output; say which permission it wanted rather than "empty".
                detail += f" — {denied}"
            return Response.failure(
                self.name, detail + "; treating as no answer rather than an empty one", tag, raw,
            )
        return Response.success(
            self.name, text=text, data=data, tag=tag, raw=raw, usage=usage
        )


def _denial(stderr: str) -> str | None:
    """The CLI's headless soft-deny notice, e.g. 'a tool required the "write_file"
    permission ... auto-denied', trimmed to its first sentence."""
    if not stderr:
        return None
    match = re.search(r'a tool required the "([a-z_]+)" permission[^.]*auto-denied', stderr)
    if match:
        return f'tool call auto-denied (needs the {match.group(1)!r} permission)'
    return None
