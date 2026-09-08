"""Configuration loading.

The layer takes a plain mapping ``{"providers": {name: {...}}, "policy": {...}}``.
Where that mapping comes from is the host project's business; two sources are
supported out of the box:

- **`project.yml`** (default) — the block under the top-level key ``multimodel:``.
  This is the project-wiring convention: one manifest, read at runtime, never
  duplicated into the skill. Needs PyYAML, which host projects that use
  ``project.yml`` already have.
- **A `.toml` file** — the whole document (``[providers.<name>]`` tables).
  Standard library `tomllib`; useful for a project with no YAML tooling.

Config is walked up from the working directory so a script run from a
subfolder still finds the project root.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

DEFAULT_FILENAME = "project.yml"
DEFAULT_KEY = "multimodel"


class ConfigError(RuntimeError):
    """Config missing, unreadable, or shaped wrong. Message says how to fix it."""


def find_project_file(filename: str = DEFAULT_FILENAME, start: Path | None = None) -> Path | None:
    """Locate `filename` in `start` or any parent. None if not found."""
    here = (start or Path.cwd()).resolve()
    for base in (here, *here.parents):
        candidate = base / filename
        if candidate.is_file():
            return candidate
    return None


def project_root(start: Path | None = None) -> Path:
    """The directory holding `project.yml`, else the working directory.

    This is where a `project`-workspace provider is launched, so a call made
    from a subfolder still gives the vendor's agent the whole project (and its
    trusted-directory status) rather than a slice of it.
    """
    found = find_project_file(start=start)
    return found.parent if found else (start or Path.cwd()).resolve()


def load_config(path: str | Path | None = None, key: str = DEFAULT_KEY) -> dict[str, Any]:
    """Return the multimodel config mapping.

    `path` may be a YAML manifest (the `key` block is returned) or a TOML file
    (the whole document is returned). With no path, `project.yml` is searched
    for from the working directory upward.
    """
    if path is None:
        found = find_project_file()
        if found is None:
            raise ConfigError(
                f"{DEFAULT_FILENAME} not found in the working directory or any parent. "
                "Pass --config, or run from inside the project."
            )
        path = found
    path = Path(path)
    if not path.is_file():
        raise ConfigError(f"config not found: {path}")

    if path.suffix == ".toml":
        with path.open("rb") as fh:
            document = tomllib.load(fh)
        return _validate(document, path)

    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover - environment-specific
        raise ConfigError(
            f"PyYAML is needed to read {path.name}; install it or pass a .toml config"
        ) from exc
    with path.open("r", encoding="utf-8") as fh:
        document = yaml.safe_load(fh) or {}
    block = document.get(key)
    if block is None:
        raise ConfigError(
            f"{path} has no top-level `{key}:` block. Run the skill's setup action "
            "to append one from the template, or pass --config <file.toml>."
        )
    return _validate(block, path)


def _validate(config: Any, path: Path) -> dict[str, Any]:
    if not isinstance(config, dict):
        raise ConfigError(f"{path}: multimodel config must be a mapping")
    providers = config.get("providers")
    if not isinstance(providers, dict) or not providers:
        raise ConfigError(
            f"{path}: multimodel config needs a non-empty `providers:` mapping"
        )
    for name, entry in providers.items():
        if entry is not None and not isinstance(entry, dict):
            raise ConfigError(f"{path}: providers.{name} must be a mapping")
    return config


def external_send_allowed(config: dict[str, Any]) -> tuple[bool, str]:
    """Read `policy.external_send`. Every prompt through this layer leaves the
    machine for a third-party service; a project may forbid that outright.

    Returns (allowed, reason). Absent policy means allowed — the template the
    setup action writes states the posture explicitly so that default is rare.
    """
    policy = config.get("policy") or {}
    value = str(policy.get("external_send", "allowed")).lower()
    if value == "forbidden":
        return False, "policy.external_send is 'forbidden' in the multimodel config"
    if value != "allowed":
        return False, f"policy.external_send must be 'allowed' or 'forbidden', got {value!r}"
    return True, "policy.external_send is 'allowed'"
