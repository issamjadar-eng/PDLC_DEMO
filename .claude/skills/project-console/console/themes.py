"""Theme resolver — loads a theme pack and renders a CSS override block.

Resolution order (first match wins):
  1. `<tool_root>/themes/<name>/` (project-owned, from /project-console theme <url>)
  2. `<skill_root>/themes/<name>/` (skill defaults: light, dark)
  3. Fallback: `<skill_root>/themes/light/`
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from console.config import Config


@dataclass(frozen=True)
class Theme:
    name: str
    pack_dir: Path
    tokens: dict
    source_url: str | None

    @property
    def tagline(self) -> str:
        return self.tokens.get("tagline", "")

    @property
    def has_footer(self) -> bool:
        return (self.pack_dir / "footer.html.j2").is_file()

    def css_variables(self) -> str:
        """Render a :root { --token: value; ... } block from the theme tokens."""
        mapping = {
            "primary": "--brand-primary",
            "primary_dark": "--brand-primary-dark",
            "primary_tint": "--brand-primary-tint",
            "accent": "--brand-accent",
            "topnav_bg": "--topnav-bg",
            "topnav_text": "--topnav-text",
            "body_bg": "--body-bg",
            "text": "--body-text",
            "text_muted": "--body-text-muted",
            "border": "--border",
            "font_body": "--font-body",
            "font_heading": "--font-heading",
        }
        lines = [f"  {css}: {self.tokens[key]};"
                 for key, css in mapping.items()
                 if key in self.tokens]
        if not lines:
            return ""
        return ":root {\n" + "\n".join(lines) + "\n}"


def _load_pack(pack_dir: Path) -> dict | None:
    theme_yaml = pack_dir / "theme.yaml"
    if not theme_yaml.is_file():
        return None
    try:
        return yaml.safe_load(theme_yaml.read_text()) or {}
    except Exception:
        return None


def resolve(cfg: Config) -> Theme:
    name = cfg.theme_name
    candidates: list[Path] = []

    project_pack = cfg.themes_dir / name
    candidates.append(project_pack)

    if cfg.skill_root is not None:
        candidates.append(cfg.skill_root / "themes" / name)
        candidates.append(cfg.skill_root / "themes" / "light")  # ultimate fallback

    for pack_dir in candidates:
        tokens = _load_pack(pack_dir)
        if tokens is not None:
            return Theme(
                name=name if pack_dir == candidates[0] or pack_dir.name == name else pack_dir.name,
                pack_dir=pack_dir,
                tokens=tokens,
                source_url=tokens.get("source_url"),
            )

    # Absolute last-resort: empty theme
    return Theme(name="default", pack_dir=Path("/nonexistent"), tokens={}, source_url=None)
