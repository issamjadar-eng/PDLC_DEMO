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
            "logo_filter": "--logo-filter",
            # Semantic surfaces — primary/secondary/recessed panel fills.
            "surface": "--surface",
            "surface_2": "--surface-2",
            "surface_muted": "--surface-muted",
            # Inline-code / pre wells.
            "code_bg": "--code-bg",
            "code_text": "--code-text",
            # Warning banners (.pc-msg-warning etc.).
            "banner_warning_bg": "--banner-warning-bg",
            "banner_warning_text": "--banner-warning-text",
            # Footer pill — independent of body-text so dark themes
            # can keep the footer visually grounded.
            "footer_bg": "--footer-bg",
            "footer_text": "--footer-text",
            "footer_heading": "--footer-heading",
            "footer_muted": "--footer-muted",
            "footer_divider": "--footer-divider",
            # Docs-explorer folder glyph color.
            "icon_folder": "--icon-folder",
            # Badge pill (e.g. agents page "Panel · 5 members") — separate
            # from primary so themes can pick a high-contrast pair without
            # disturbing brand-primary.
            "badge_bg": "--badge-bg",
            "badge_text": "--badge-text",
        }
        lines = [f"  {css}: {self.tokens[key]};"
                 for key, css in mapping.items()
                 if key in self.tokens]

        # Category ramp -> --cat-1..N plus --cat-alt for the reserved final
        # entry. Emitted for any console surface that renders a repeating
        # dimension (the usage-metrics token series, for one), so a series
        # stays legible on a light pack instead of carrying dark-tuned
        # literals. Same contract as the tracker consumes: sequential entries
        # in order, last entry reserved and never assigned positionally.
        cats = [c.strip() for c in (self.tokens.get("category_colors") or "").split(",") if c.strip()]
        if len(cats) >= 2:
            lines += [f"  --cat-{i}: {c};" for i, c in enumerate(cats[:-1], start=1)]
            lines.append(f"  --cat-alt: {cats[-1]};")

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


def _resolve_pack(name: str, cfg: Config) -> tuple[Path, dict] | None:
    """Find a theme pack by name. Project themes win over skill defaults.

    Returns (pack_dir, tokens) for the first match, or None.
    """
    candidates: list[Path] = [cfg.themes_dir / name]
    if cfg.skill_root is not None:
        candidates.append(cfg.skill_root / "themes" / name)
    for pack_dir in candidates:
        tokens = _load_pack(pack_dir)
        if tokens is not None:
            return pack_dir, tokens
    return None


def _load_with_inheritance(name: str, cfg: Config, _seen: set[str] | None = None) -> tuple[Path, dict] | None:
    """Load a theme pack and recursively merge any `extends:` parent.

    A theme.yaml may declare `extends: <theme-name>` to inherit all tokens
    from the named parent. Child fields override parent fields key-by-key
    (shallow merge — every token is a scalar, no nested structures). The
    parent itself may also extend another theme; cycles raise ValueError.

    Project theme packs are resolved first by `_resolve_pack`, so a project
    pack can extend a skill default (`extends: dark`) and override only the
    brand-specific bits (logo_filter, brand_name, tagline, accent).
    """
    if _seen is None:
        _seen = set()
    if name in _seen:
        raise ValueError(f"theme inheritance cycle: {' -> '.join(list(_seen) + [name])}")
    _seen.add(name)

    found = _resolve_pack(name, cfg)
    if found is None:
        return None
    pack_dir, tokens = found

    parent_name = tokens.get("extends")
    if parent_name:
        parent = _load_with_inheritance(parent_name, cfg, _seen)
        if parent is None:
            # Parent missing — proceed with child-only tokens (still better
            # than failing the whole console launch over a typoed extends).
            return pack_dir, tokens
        _, parent_tokens = parent
        merged = {**parent_tokens, **tokens}  # child wins
        merged.pop("extends", None)
        return pack_dir, merged

    return pack_dir, tokens


def list_packs(cfg: Config) -> list[dict]:
    """Every installed theme pack, project packs first (they win on name).

    Each entry carries the RESOLVED tokens (inheritance applied) so a caller
    can render a swatch without re-reading the pack. `source` distinguishes a
    project-owned pack from one bundled with the skill.
    """
    seen: dict[str, dict] = {}
    sources = [(cfg.themes_dir, "project")]
    if cfg.skill_root is not None:
        sources.append((cfg.skill_root / "themes", "builtin"))

    for base, source in sources:
        if not base.is_dir():
            continue
        for pack_dir in sorted(base.iterdir()):
            name = pack_dir.name
            if name in seen or not (pack_dir / "theme.yaml").is_file():
                continue          # project packs are visited first and win
            try:
                found = _load_with_inheritance(name, cfg)
            except ValueError:    # inheritance cycle — surface, don't crash
                continue
            if found is None:
                continue
            _, tokens = found
            seen[name] = {
                "name": name,
                "label": tokens.get("name") or name,
                "source": source,
                "tokens": tokens,
                "is_default": name == cfg.theme_name,
            }
    return list(seen.values())


def safe_theme_name(cfg: Config, candidate: str | None) -> str | None:
    """Validate an UNTRUSTED theme name (e.g. from a cookie) against installed packs.

    The name is used to build a filesystem path (`themes_dir / name`), so it
    can never be trusted from a client. Anything not matching an installed
    pack exactly — including traversal attempts — returns None, and the caller
    falls back to the project default.
    """
    if not candidate:
        return None
    return candidate if any(p["name"] == candidate for p in list_packs(cfg)) else None


def resolve(cfg: Config, name: str | None = None) -> Theme:
    """Resolve the active theme.

    `name` overrides the project default (`console.yaml theme:`) — used for
    the per-browser selection, which must already have been validated through
    `safe_theme_name`. Omitted or None means the project default.
    """
    name = name or cfg.theme_name

    found = _load_with_inheritance(name, cfg)
    if found is not None:
        pack_dir, tokens = found
        return Theme(
            name=name,
            pack_dir=pack_dir,
            tokens=tokens,
            source_url=tokens.get("source_url"),
        )

    # Ultimate fallback: skill's bundled `light` theme
    if cfg.skill_root is not None:
        fallback = cfg.skill_root / "themes" / "light"
        tokens = _load_pack(fallback)
        if tokens is not None:
            return Theme(name="light", pack_dir=fallback, tokens=tokens,
                         source_url=tokens.get("source_url"))

    # Absolute last-resort: empty theme
    return Theme(name="default", pack_dir=Path("/nonexistent"), tokens={}, source_url=None)
