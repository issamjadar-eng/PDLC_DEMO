"""md-deck icon repository.

A curated library of inline SVG icons covering healthcare / regulatory /
engineering / software / documents / people / security / analytics /
workflow / AI domains. Each icon is a self-contained 24×24 viewBox SVG
that uses `currentColor` so it inherits the surrounding text/border color.

Public API:
    pick(label) -> str            # keyword-matched icon, hash fallback
    detect_group(items, title, hint) -> str | None   # homogeneous-group key
    pick_group(group_type) -> str # kind-icon for a detected group
    list_icons() -> list[str]     # debugging
"""

from __future__ import annotations

import hashlib

# ---------------------------------------------------------------------------
# Icon definitions — 24x24 viewBox, currentColor only. Each is one or two
# SVG primitives, kept compact for inline embedding.
# ---------------------------------------------------------------------------

ICONS: dict[str, str] = {
    # ===== Healthcare / clinical / biology =====
    "stethoscope": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3v6a4 4 0 0 0 8 0V3"/><circle cx="18" cy="14" r="2.5"/><path d="M9 13v3a5 5 0 0 0 9 3"/></svg>',
    "heartbeat": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h4l2-6 4 12 2-8 2 4h6"/></svg>',
    "heart": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 21s-7-5-9.5-9.5C0 7 4 3 7.5 4.5 9 5 11 6 12 8c1-2 3-3 4.5-3.5C20 3 24 7 21.5 11.5 19 16 12 21 12 21z"/></svg>',
    "pill": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="9" width="18" height="6" rx="3" transform="rotate(-30 12 12)"/><line x1="9.5" y1="6" x2="14.5" y2="18"/></svg>',
    "syringe": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="21" x2="8" y2="16"/><rect x="8" y="9" width="9" height="6" rx="1" transform="rotate(-45 12.5 12)"/><line x1="17" y1="3" x2="21" y2="7"/><line x1="14" y1="6" x2="18" y2="10"/></svg>',
    "iv-drip": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M9 3h6"/><line x1="12" y1="3" x2="12" y2="7"/><path d="M8 7h8l-1 6H9z"/><line x1="12" y1="13" x2="12" y2="20"/><circle cx="12" cy="20.5" r="0.8" fill="currentColor"/></svg>',
    "dna": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M7 3c0 6 10 6 10 12s-10 6-10 12"/><path d="M17 3c0 6-10 6-10 12s10 6 10 12"/><line x1="9" y1="7" x2="15" y2="7"/><line x1="9" y1="17" x2="15" y2="17"/></svg>',
    "microscope": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="7" r="3"/><line x1="9" y1="10" x2="9" y2="14"/><path d="M5 14h8v3H5z"/><path d="M3 21h18"/><line x1="13" y1="6" x2="18" y2="11"/></svg>',
    "brain": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-3 4 3 3 0 0 0 1 4 3 3 0 0 0 2 4 3 3 0 0 0 5 1V4z"/><path d="M15 4a3 3 0 0 1 3 3 3 3 0 0 1 3 4 3 3 0 0 1-1 4 3 3 0 0 1-2 4 3 3 0 0 1-5 1V4z"/></svg>',
    "lungs": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 4v10"/><path d="M9 7c-2 1-5 4-5 9 0 2 1 4 3 4s3-2 3-4V7z"/><path d="M15 7c2 1 5 4 5 9 0 2-1 4-3 4s-3-2-3-4V7z"/></svg>',
    "test-tube": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h6"/><path d="M10 3v14a3 3 0 0 0 4 0V3"/><path d="M10 14h4"/></svg>',
    "hospital": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="4" y="6" width="16" height="15" rx="1"/><path d="M9 21V11h6v10"/><line x1="12" y1="3" x2="12" y2="9"/><line x1="9" y1="6" x2="15" y2="6"/></svg>',
    "clipboard-medical": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="4" width="12" height="17" rx="1.5"/><rect x="9" y="2" width="6" height="3" rx="0.5"/><line x1="12" y1="11" x2="12" y2="17"/><line x1="9" y1="14" x2="15" y2="14"/></svg>',

    # ===== Regulatory / QMS =====
    "shield-check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 3v7c0 5-3.5 7.5-8 8.5-4.5-1-8-3.5-8-8.5V6z"/><polyline points="9,12 11,14 15,10"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 3l8 3v7c0 5-3.5 7.5-8 8.5-4.5-1-8-3.5-8-8.5V6z"/></svg>',
    "certificate": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="4" width="18" height="13" rx="1"/><circle cx="12" cy="11" r="3"/><path d="M10 14l-1 6 3-2 3 2-1-6"/></svg>',
    "stamp": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3h8l-2 7h-4z"/><rect x="6" y="10" width="12" height="4" rx="1"/><line x1="4" y1="18" x2="20" y2="18"/><line x1="4" y1="21" x2="20" y2="21"/></svg>',
    "scale-justice": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="3" x2="12" y2="21"/><line x1="6" y1="21" x2="18" y2="21"/><line x1="4" y1="6" x2="20" y2="6"/><path d="M5 6l-3 6h6zM19 6l-3 6h6z"/></svg>',
    "ribbon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><circle cx="12" cy="9" r="6"/><polyline points="9,14 7,21 12,18 17,21 15,14"/></svg>',
    "signature": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 17c2 0 3-2 5-6s4-7 6-7 1 4 1 7 0 6 3 6"/><line x1="3" y1="21" x2="21" y2="21"/></svg>',

    # ===== Engineering / mechanical / electrical =====
    "gear": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2"/></svg>',
    "wrench": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 6a4 4 0 1 1 4 4l-9 9a2.5 2.5 0 0 1-3.5-3.5l9-9z"/><line x1="6" y1="18" x2="9" y2="15"/></svg>',
    "circuit": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="6" cy="6" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="18" r="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="8" y1="18" x2="16" y2="18"/><line x1="6" y1="8" x2="6" y2="16"/><line x1="18" y1="8" x2="18" y2="16"/></svg>',
    "microchip": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="6" y="6" width="12" height="12" rx="1"/><rect x="9" y="9" width="6" height="6"/><line x1="3" y1="9" x2="6" y2="9"/><line x1="3" y1="15" x2="6" y2="15"/><line x1="18" y1="9" x2="21" y2="9"/><line x1="18" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="6"/><line x1="15" y1="3" x2="15" y2="6"/><line x1="9" y1="18" x2="9" y2="21"/><line x1="15" y1="18" x2="15" y2="21"/></svg>',
    "ruler": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="2" y="9" width="20" height="6" rx="0.5" transform="rotate(-15 12 12)"/><line x1="6" y1="9" x2="6" y2="11"/><line x1="10" y1="8" x2="10" y2="11"/><line x1="14" y1="7" x2="14" y2="11"/><line x1="18" y1="6" x2="18" y2="11"/></svg>',
    "compass-tool": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="6" r="2"/><line x1="12" y1="8" x2="6" y2="20"/><line x1="12" y1="8" x2="18" y2="20"/><path d="M8 16h8"/></svg>',
    "blueprint": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="1"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="9" x2="9" y2="21"/><rect x="11" y="11" width="6" height="4"/></svg>',

    # ===== Software / dev / infra =====
    "terminal": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="1"/><polyline points="7,9 10,12 7,15"/><line x1="13" y1="15" x2="17" y2="15"/></svg>',
    "code-brackets": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="8,5 3,12 8,19"/><polyline points="16,5 21,12 16,19"/></svg>',
    "git-branch": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="12" r="2"/><line x1="6" y1="7" x2="6" y2="17"/><path d="M6 12h6c2 0 4-2 4-5"/></svg>',
    "git-merge": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="6" cy="5" r="2"/><circle cx="18" cy="5" r="2"/><circle cx="12" cy="19" r="2"/><line x1="6" y1="7" x2="12" y2="17"/><line x1="18" y1="7" x2="12" y2="17"/></svg>',
    "container": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="7" width="18" height="12" rx="0.5"/><line x1="7" y1="7" x2="7" y2="19"/><line x1="11" y1="7" x2="11" y2="19"/><line x1="15" y1="7" x2="15" y2="19"/><line x1="19" y1="7" x2="19" y2="19"/></svg>',
    "database": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="8" ry="2.5"/><path d="M4 5v6c0 1.5 3.5 2.5 8 2.5s8-1 8-2.5V5"/><path d="M4 11v6c0 1.5 3.5 2.5 8 2.5s8-1 8-2.5v-6"/></svg>',
    "cloud": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M7 18a4 4 0 0 1 0-8 6 6 0 0 1 11-1 4 4 0 0 1 1 9z"/></svg>',
    "api-sync": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><polyline points="3,21 3,16 8,16"/><polyline points="21,3 21,8 16,8"/></svg>',
    "plug": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M9 3v6"/><path d="M15 3v6"/><rect x="7" y="9" width="10" height="6" rx="1"/><path d="M12 15v3a3 3 0 0 0 3 3"/></svg>',
    "pipeline": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h14L14 4 M20 16H6L10 20"/></svg>',
    "lens": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="6"/><line x1="15.5" y1="15.5" x2="20" y2="20" stroke-linecap="round" stroke-width="2.5"/></svg>',

    # ===== Documents / process =====
    "document": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M5 3h10l4 4v14H5z"/><polyline points="15,3 15,7 19,7"/></svg>',
    "stack-sheets": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="5" y="6" width="11" height="14" rx="1"/><rect x="8" y="3" width="11" height="14" rx="1"/><line x1="11" y1="8" x2="16" y2="8"/><line x1="11" y1="11" x2="16" y2="11"/></svg>',
    "folder": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 6a1 1 0 0 1 1-1h5l2 2h9a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/></svg>',
    "archive": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="4" width="18" height="4"/><rect x="4" y="8" width="16" height="13"/><line x1="9" y1="12" x2="15" y2="12"/></svg>',
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="6"/><line x1="15.5" y1="15.5" x2="20" y2="20" stroke-linecap="round" stroke-width="2.5"/></svg>',
    "tag": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M4 4h8l9 9-8 8-9-9z"/><circle cx="8" cy="8" r="1.5" fill="currentColor"/></svg>',
    "calendar": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="1"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="8" y1="3" x2="8" y2="7"/><line x1="16" y1="3" x2="16" y2="7"/></svg>',
    "timer": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="14" r="7"/><line x1="9" y1="3" x2="15" y2="3"/><line x1="12" y1="14" x2="12" y2="10"/><line x1="12" y1="14" x2="15" y2="14"/></svg>',
    "flag": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><line x1="5" y1="3" x2="5" y2="21" stroke-linecap="round"/><path d="M5 4h12l-3 4 3 4H5"/></svg>',
    "bookmark": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M6 3h12v18l-6-4-6 4z"/></svg>',
    "link": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M10 14l4-4"/><path d="M9 7l3-3a4 4 0 0 1 6 6l-3 3"/><path d="M15 17l-3 3a4 4 0 0 1-6-6l3-3"/></svg>',

    # ===== People / communication =====
    "users": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><circle cx="9" cy="8" r="3.5"/><path d="M3 21c0-3.5 3-6 6-6s6 2.5 6 6"/><circle cx="17" cy="9" r="2.5"/><path d="M15 21c0-2.5 2-4.5 4-4.5s2 1 2 1"/></svg>',
    "user-single": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-7 8-7s8 3 8 7"/></svg>',
    "chat": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 5a1 1 0 0 1 1-1h16a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1h-9l-5 4v-4H4a1 1 0 0 1-1-1z"/></svg>',
    "megaphone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 11v2a1 1 0 0 0 1 1h2l8 5V5L6 10H4a1 1 0 0 0-1 1z"/><path d="M16 8a4 4 0 0 1 0 8"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="1"/><polyline points="3,7 12,13 21,7"/></svg>',
    "handshake": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 13l4-4 4 2 4-4 4 2 4-2v6l-4 4-4-2-4 2-4-2-4 2z"/></svg>',

    # ===== Security =====
    "lock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="5" y="11" width="14" height="9" rx="1.5"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/><circle cx="12" cy="15.5" r="1.5" fill="currentColor"/></svg>',
    "key": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="14" r="4"/><path d="M11 11l9-9"/><path d="M16 6l3 3"/></svg>',
    "fingerprint": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 12a7 7 0 0 1 14 0v3"/><path d="M8 12a4 4 0 0 1 8 0v5"/><path d="M11 12a1 1 0 0 1 2 0v8"/></svg>',
    "eye-watch": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',

    # ===== Data / analytics =====
    "chart-bar": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="6" y1="20" x2="6" y2="12"/><line x1="12" y1="20" x2="12" y2="6"/><line x1="18" y1="20" x2="18" y2="14"/><line x1="3" y1="20" x2="21" y2="20"/></svg>',
    "chart-line": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3,17 9,11 13,15 21,5"/><polyline points="15,5 21,5 21,11"/></svg>',
    "chart-pie": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 3v9h9a9 9 0 1 1-9-9z"/><path d="M21 12a9 9 0 0 0-9-9v9z"/></svg>',
    "gauge": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 18a8 8 0 1 1 14 0"/><line x1="12" y1="18" x2="16" y2="11"/><circle cx="12" cy="18" r="1" fill="currentColor"/></svg>',
    "trending-up": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3,17 9,11 13,15 21,7"/><polyline points="14,7 21,7 21,14"/></svg>',
    "dashboard": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="3" width="8" height="9" rx="0.5"/><rect x="13" y="3" width="8" height="5" rx="0.5"/><rect x="13" y="10" width="8" height="11" rx="0.5"/><rect x="3" y="14" width="8" height="7" rx="0.5"/></svg>',

    # ===== Workflow / state =====
    "check-circle": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><polyline points="8,12 11,15 16,9"/></svg>',
    "x-circle": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/></svg>',
    "warn": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l10 18H2z"/><line x1="12" y1="10" x2="12" y2="15"/><circle cx="12" cy="18" r="0.8" fill="currentColor"/></svg>',
    "info-circle": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><line x1="12" y1="11" x2="12" y2="16"/><circle cx="12" cy="8" r="0.8" fill="currentColor"/></svg>',
    "lightning": '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="13,2 4,14 11,14 9,22 20,10 13,10"/></svg>',
    "refresh": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><polyline points="21,3 21,8 16,8"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/><polyline points="3,21 3,16 8,16"/></svg>',
    "sync": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 9a8 8 0 0 1 13-3"/><polyline points="18,3 18,8 13,8"/><path d="M19 15a8 8 0 0 1-13 3"/><polyline points="6,21 6,16 11,16"/></svg>',
    "queue": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>',
    "star": '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="12,3 14,10 21,12 14,14 12,21 10,14 3,12 10,10"/></svg>',
    "compass-rose": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><polyline points="8,4 4,8 4,16 8,20"/><polyline points="16,4 20,8 20,16 16,20"/><line x1="12" y1="6" x2="12" y2="18"/><line x1="6" y1="12" x2="18" y2="12"/></svg>',

    # ===== AI / agents =====
    "robot": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="5" y="7" width="14" height="12" rx="1.5"/><circle cx="9" cy="13" r="1.2" fill="currentColor"/><circle cx="15" cy="13" r="1.2" fill="currentColor"/><line x1="12" y1="3" x2="12" y2="7"/><circle cx="12" cy="3" r="1" fill="currentColor"/></svg>',
    "brain-circuit": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M9 4a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3"/><path d="M15 4a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/></svg>',
    "sparkles": '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="12,3 13.5,8.5 19,10 13.5,11.5 12,17 10.5,11.5 5,10 10.5,8.5"/><polygon points="19,16 19.5,18 21.5,18.5 19.5,19 19,21 18.5,19 16.5,18.5 18.5,18"/></svg>',

    # ===== Healthcare extended =====
    "bandage": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="2" y="9" width="20" height="6" rx="3" transform="rotate(-30 12 12)"/><circle cx="10" cy="11" r="0.8" fill="currentColor"/><circle cx="14" cy="13" r="0.8" fill="currentColor"/><circle cx="11" cy="14" r="0.8" fill="currentColor"/><circle cx="13" cy="10" r="0.8" fill="currentColor"/></svg>',
    "scalpel": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 21l8-8"/><path d="M11 13L20 4l-1 5-4 4z"/></svg>',
    "vitals": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="1"/><path d="M5 12h3l1.5-3 2.5 6 1.5-3h6"/></svg>',
    "ambulance": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="2" y="8" width="14" height="9" rx="1"/><path d="M16 11h3l2 3v3h-5z"/><circle cx="6.5" cy="18.5" r="1.5"/><circle cx="17.5" cy="18.5" r="1.5"/><line x1="9" y1="11" x2="9" y2="14"/><line x1="7.5" y1="12.5" x2="10.5" y2="12.5"/></svg>',
    "prescription": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M6 4h6a3 3 0 0 1 0 6h-6V4z"/><line x1="6" y1="10" x2="6" y2="20"/><line x1="9" y1="10" x2="14" y2="15"/><line x1="14" y1="10" x2="9" y2="15"/></svg>',
    "wheelchair": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><circle cx="12" cy="6" r="2"/><path d="M11 9l1 5h6l-2 6"/><circle cx="11" cy="18" r="4"/></svg>',

    # ===== Engineering / hardware extended =====
    "caliper": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="2" y="10" width="20" height="4"/><line x1="6" y1="10" x2="6" y2="6"/><line x1="6" y1="14" x2="6" y2="18"/><line x1="10" y1="10" x2="10" y2="13"/><line x1="14" y1="10" x2="14" y2="13"/><line x1="18" y1="10" x2="18" y2="13"/></svg>',
    "multimeter": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="3" width="18" height="13" rx="1"/><rect x="6" y="6" width="12" height="4"/><line x1="3" y1="20" x2="9" y2="20"/><line x1="15" y1="20" x2="21" y2="20"/></svg>',
    "screwdriver": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 6l4-4 4 4-4 4z"/><line x1="14" y1="6" x2="3" y2="17"/><rect x="2" y="16" width="6" height="4" transform="rotate(-45 5 18)"/></svg>',
    "hammer": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M14 4l6 6-2 2-3-3-9 9-3-3 9-9-3-3z"/></svg>',
    "hard-hat": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 17h18v-2a8 8 0 0 0-16 0v2z"/><line x1="10" y1="9" x2="10" y2="6"/><line x1="14" y1="9" x2="14" y2="6"/><line x1="3" y1="20" x2="21" y2="20"/></svg>',
    "valve": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><line x1="2" y1="12" x2="8" y2="12"/><line x1="16" y1="12" x2="22" y2="12"/><line x1="12" y1="4" x2="12" y2="8"/><line x1="9" y1="4" x2="15" y2="4"/></svg>',
    "sensor": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="2" fill="currentColor"/><path d="M9 12a3 3 0 0 1 6 0"/><path d="M6 12a6 6 0 0 1 12 0"/><path d="M3 12a9 9 0 0 1 18 0"/></svg>',
    "antenna": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="3" x2="12" y2="21"/><path d="M8 5a8 8 0 0 0 0 6"/><path d="M16 5a8 8 0 0 1 0 6"/><path d="M5 3a12 12 0 0 0 0 10"/><path d="M19 3a12 12 0 0 1 0 10"/></svg>',
    "battery": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="8" width="16" height="8" rx="1"/><line x1="20" y1="11" x2="20" y2="13"/><rect x="5" y="10" width="9" height="4" fill="currentColor"/></svg>',

    # ===== Tooling / craft =====
    "toolbox": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="8" width="18" height="12" rx="1"/><path d="M8 8V5a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v3"/><line x1="3" y1="13" x2="21" y2="13"/><rect x="10" y="11" width="4" height="4" rx="0.5"/></svg>',
    "puzzle": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M10 4h4v3a2 2 0 1 0 0 4v3h-4v-3a2 2 0 1 1-4 0v-3h4z"/></svg>',
    "magnet": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M5 4v8a7 7 0 0 0 14 0V4h-4v8a3 3 0 0 1-6 0V4z"/></svg>',
    "level-tool": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="2" y="9" width="20" height="6"/><circle cx="12" cy="12" r="1.5"/><line x1="6" y1="15" x2="6" y2="13"/><line x1="18" y1="15" x2="18" y2="13"/></svg>',
    "filter-funnel": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 4h18l-7 8v8l-4-2v-6z"/></svg>',

    # ===== Web / UI / Internet =====
    "browser": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="1"/><line x1="3" y1="9" x2="21" y2="9"/><circle cx="6" cy="6.5" r="0.6" fill="currentColor"/><circle cx="8.5" cy="6.5" r="0.6" fill="currentColor"/><circle cx="11" cy="6.5" r="0.6" fill="currentColor"/></svg>',
    "window-ui": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="1"/><line x1="3" y1="8" x2="21" y2="8"/></svg>',
    "mouse-pointer": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M5 3l4 16 3-7 7-3z"/></svg>',
    "globe-www": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><line x1="3" y1="12" x2="21" y2="12"/></svg>',
    "server-rack": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="4" y="3" width="16" height="6" rx="1"/><rect x="4" y="11" width="16" height="6" rx="1"/><line x1="7" y1="6" x2="9" y2="6"/><line x1="7" y1="14" x2="9" y2="14"/><circle cx="17" cy="6" r="0.8" fill="currentColor"/><circle cx="17" cy="14" r="0.8" fill="currentColor"/></svg>',
    "load-balancer": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="12" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><line x1="12" y1="7" x2="5" y2="17"/><line x1="12" y1="7" x2="12" y2="17"/><line x1="12" y1="7" x2="19" y2="17"/></svg>',
    "share-net": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><circle cx="6" cy="12" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="18" cy="18" r="2"/><line x1="8" y1="11" x2="16" y2="7"/><line x1="8" y1="13" x2="16" y2="17"/></svg>',
    "https-secure": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="5" y="11" width="14" height="9" rx="1"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/><path d="M11 15l1 1 2-2"/></svg>',
    "wifi-signal": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 12a10 10 0 0 1 14 0"/><path d="M8 15a6 6 0 0 1 8 0"/><circle cx="12" cy="18" r="1" fill="currentColor"/></svg>',

    # ===== Ideas / vision / leadership =====
    "lightbulb": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M9 18h6v-2a6 6 0 1 0-6 0v2z"/><line x1="10" y1="21" x2="14" y2="21"/></svg>',
    "north-star": '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="12,2 13,10 22,12 13,14 12,22 11,14 2,12 11,10"/></svg>',
    "telescope": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 14l8-3 6 5-1 2-7 2z"/><line x1="13" y1="11" x2="20" y2="4"/><line x1="11" y1="20" x2="13" y2="14"/><line x1="8" y1="21" x2="11" y2="20"/></svg>',
    "vision-eye": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="1" fill="currentColor"/></svg>',
    "mountain-summit": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><polygon points="3,20 9,9 13,15 16,11 21,20"/><circle cx="9" cy="6" r="1.5"/></svg>',
    "podium": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="9" y="6" width="6" height="14"/><rect x="3" y="11" width="6" height="9"/><rect x="15" y="9" width="6" height="11"/></svg>',
    "trophy": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M7 4h10v6a5 5 0 0 1-10 0z"/><path d="M7 6H4v3a3 3 0 0 0 3 3"/><path d="M17 6h3v3a3 3 0 0 1-3 3"/><line x1="9" y1="20" x2="15" y2="20"/><line x1="12" y1="15" x2="12" y2="20"/></svg>',
    "medal": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M7 3l3 8M17 3l-3 8"/><circle cx="12" cy="15" r="6"/><polygon points="12,12 13.5,14 16,14 14,15.5 14.5,18 12,16.5 9.5,18 10,15.5 8,14 10.5,14"/></svg>',
    "crown": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 7l4 4 5-7 5 7 4-4-2 12H5z"/></svg>',
    "roadmap": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 19c4-2 6-2 9-9 3-7 5-7 9-5"/><circle cx="6" cy="17" r="1.5" fill="currentColor"/><circle cx="12" cy="10" r="1.5" fill="currentColor"/><circle cx="18" cy="6" r="1.5" fill="currentColor"/></svg>',
    "beacon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="3" x2="12" y2="6"/><circle cx="12" cy="9" r="3" fill="currentColor"/><line x1="6" y1="3" x2="8" y2="6"/><line x1="18" y1="3" x2="16" y2="6"/><path d="M5 20l3-9h8l3 9z"/></svg>',
    "hand-raised": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M9 13v-9a1.5 1.5 0 0 1 3 0v7"/><path d="M12 11v-6a1.5 1.5 0 0 1 3 0v8"/><path d="M15 11v-4a1.5 1.5 0 0 1 3 0v8a6 6 0 0 1-6 6h-2a6 6 0 0 1-5-3l-3-5a1.5 1.5 0 0 1 3-1.5L7 16V8a1.5 1.5 0 0 1 3 0v6"/></svg>',

    # ===== Strategy / planning =====
    "target-bullseye": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="1" fill="currentColor"/></svg>',
    "chess-king": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"/><line x1="10" y1="4" x2="14" y2="4"/><path d="M12 6c-3 2-5 5-5 8h10c0-3-2-6-5-8z"/><rect x="6" y="14" width="12" height="3"/><rect x="4" y="17" width="16" height="3"/></svg>',
    "scenario-tree": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="4" r="2"/><circle cx="6" cy="12" r="2"/><circle cx="18" cy="12" r="2"/><circle cx="3" cy="20" r="2"/><circle cx="9" cy="20" r="2"/><circle cx="15" cy="20" r="2"/><circle cx="21" cy="20" r="2"/><line x1="12" y1="6" x2="6" y2="10"/><line x1="12" y1="6" x2="18" y2="10"/><line x1="6" y1="14" x2="3" y2="18"/><line x1="6" y1="14" x2="9" y2="18"/><line x1="18" y1="14" x2="15" y2="18"/><line x1="18" y1="14" x2="21" y2="18"/></svg>',
    "map-pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 22s7-7.5 7-13a7 7 0 0 0-14 0c0 5.5 7 13 7 13z"/><circle cx="12" cy="9" r="3"/></svg>',
    "hourglass": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><line x1="6" y1="3" x2="18" y2="3"/><line x1="6" y1="21" x2="18" y2="21"/><path d="M7 3l5 9-5 9"/><path d="M17 3l-5 9 5 9"/></svg>',
    "flag-checkered": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><line x1="5" y1="3" x2="5" y2="21" stroke-linecap="round"/><rect x="5" y="4" width="14" height="8"/><line x1="9" y1="4" x2="9" y2="12"/><line x1="13" y1="4" x2="13" y2="12"/><line x1="17" y1="4" x2="17" y2="12"/><line x1="5" y1="6" x2="19" y2="6"/><line x1="5" y1="10" x2="19" y2="10"/></svg>',

    # ===== Reporting / analytics extended =====
    "ledger": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="4" y="3" width="16" height="18" rx="1"/><line x1="4" y1="8" x2="20" y2="8"/><line x1="8" y1="3" x2="8" y2="21"/><line x1="11" y1="11" x2="18" y2="11"/><line x1="11" y1="14" x2="18" y2="14"/><line x1="11" y1="17" x2="16" y2="17"/></svg>',
    "scorecard": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="1"/><line x1="3" y1="8" x2="21" y2="8"/><line x1="9" y1="11" x2="9" y2="19"/><line x1="15" y1="11" x2="15" y2="19"/><circle cx="6" cy="14" r="0.8" fill="currentColor"/><circle cx="12" cy="15" r="0.8" fill="currentColor"/><circle cx="18" cy="13" r="0.8" fill="currentColor"/></svg>',
    "traffic-light": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="8" y="2" width="8" height="20" rx="3"/><circle cx="12" cy="7" r="1.5" fill="currentColor"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="17" r="1.5"/></svg>',
    "heatmap": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="3" width="6" height="6"/><rect x="9" y="3" width="6" height="6" fill="currentColor" opacity="0.4"/><rect x="15" y="3" width="6" height="6"/><rect x="3" y="9" width="6" height="6" fill="currentColor" opacity="0.7"/><rect x="9" y="9" width="6" height="6" fill="currentColor"/><rect x="15" y="9" width="6" height="6" fill="currentColor" opacity="0.4"/><rect x="3" y="15" width="6" height="6"/><rect x="9" y="15" width="6" height="6" fill="currentColor" opacity="0.7"/><rect x="15" y="15" width="6" height="6"/></svg>',
    "audit-trail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><circle cx="6" cy="6" r="2"/><circle cx="6" cy="12" r="2"/><circle cx="6" cy="18" r="2"/><line x1="6" y1="8" x2="6" y2="10"/><line x1="6" y1="14" x2="6" y2="16"/><line x1="9" y1="6" x2="20" y2="6"/><line x1="9" y1="12" x2="17" y2="12"/><line x1="9" y1="18" x2="14" y2="18"/></svg>',
    "report-doc": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M5 3h10l4 4v14H5z"/><polyline points="15,3 15,7 19,7"/><line x1="8" y1="13" x2="16" y2="13"/><polyline points="8,16 11,16 11,18 14,18"/></svg>',
    "donut": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><circle cx="12" cy="12" r="7"/><path d="M12 5a7 7 0 0 1 7 7" stroke-linecap="round"/></svg>',
    "ranking": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="14" width="5" height="6"/><rect x="9.5" y="9" width="5" height="11"/><rect x="16" y="4" width="5" height="16"/></svg>',

    # ===== Meeting / collaboration =====
    "meeting": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><circle cx="12" cy="12" r="2"/><circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="18" r="2"/><line x1="7" y1="7" x2="10" y2="11"/><line x1="17" y1="7" x2="14" y2="11"/><line x1="7" y1="17" x2="10" y2="13"/><line x1="17" y1="17" x2="14" y2="13"/></svg>',
    "whiteboard": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="2" y="4" width="20" height="13" rx="1"/><line x1="6" y1="20" x2="9" y2="17"/><line x1="18" y1="20" x2="15" y2="17"/><polyline points="6,9 9,12 13,8 18,11"/></svg>',
    "thumbs-up": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 11h4v9H3z"/><path d="M7 11l5-8a2 2 0 0 1 4 1l-1 5h5a2 2 0 0 1 2 2l-1 7a2 2 0 0 1-2 2h-9a3 3 0 0 1-3-3"/></svg>',

    # ===== Hazard / failure-mode specific =====
    "bell-alarm": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0-6 6v4l-2 4h16l-2-4V9a6 6 0 0 0-6-6z"/><path d="M10 19a2 2 0 0 0 4 0"/><line x1="3" y1="3" x2="6" y2="6" stroke-linecap="round"/><line x1="21" y1="3" x2="18" y2="6" stroke-linecap="round"/></svg>',
    "leak-drop": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l5 8a5 5 0 1 1-10 0z"/><circle cx="12" cy="11" r="1.5" fill="currentColor"/><path d="M5 18l-1 3M19 18l1 3M12 21v1"/></svg>',
    "bug-defect": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="8" width="10" height="11" rx="5"/><line x1="12" y1="8" x2="12" y2="19"/><path d="M9 6l-2-2M15 6l2-2"/><path d="M5 12H3M5 16H3M19 12h2M19 16h2M5 9l2-2M19 9l-2-2"/></svg>',
    "tamper-shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><line x1="9" y1="9" x2="15" y2="15" stroke-linecap="round"/><line x1="15" y1="9" x2="9" y2="15" stroke-linecap="round"/></svg>',
    "battery-low": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="8" width="16" height="8" rx="1"/><line x1="20" y1="11" x2="20" y2="13"/><rect x="5" y="10" width="3" height="4" fill="currentColor"/><line x1="9" y1="12" x2="9" y2="12"/></svg>',
    "alarm-clock-noisy": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><circle cx="12" cy="13" r="7"/><polyline points="12,9 12,13 15,15"/><line x1="3" y1="6" x2="6" y2="3" stroke-linecap="round"/><line x1="21" y1="6" x2="18" y2="3" stroke-linecap="round"/></svg>',

    # ===== Generic fallback pool =====
    "hexagon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12,3 21,8 21,16 12,21 3,16 3,8"/></svg>',
    "diamond": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12,3 21,12 12,21 3,12"/></svg>',
    "triangle-up": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><polygon points="12,4 21,20 3,20"/></svg>',
    "circle-target": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/></svg>',
    "square-rounded": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="3"/></svg>',
    "asterisk": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="4" x2="12" y2="20"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg>',
    "ring": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="8"/></svg>',
    "plus": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
}


# ---------------------------------------------------------------------------
# Keyword → icon registry (ordered; first match wins).
# Bug-fixes preserved from prior session (see ben/039 §2.6):
#   - "rate" narrowed to "heart-rate" (was hijacking "strat[egy]").
#   - "pr" removed from merge entry (was hijacking "pr[actices]"/"pr[oject]").
#   - "task-first" / "one task" / "session-start" placed BEFORE plain "task".
#   - tracker / trace-matrix / dhf-manifest / advisors registered BEFORE
#     the generic "strateg" entry so the catalog categorizer's "strategy"
#     key doesn't hijack them via name + " " + category_key.
# ---------------------------------------------------------------------------

KEYWORD_REGISTRY: list[tuple[list[str], str]] = [
    # Healthcare / clinical / medical
    (["clinical", "patient", "diagnos"],                   "stethoscope"),
    (["heart", "cardiac", "ecg", "ekg", "heart-rate"],     "heartbeat"),
    (["pain", "ease", "pca", "analgesia", "anesthet"],     "pill"),
    (["drug", "pharmac", "dose", "formular"],              "pill"),
    (["bandage", "wound", "dressing", "first-aid"],        "bandage"),
    (["scalpel", "surgery", "surgical", "incision"],       "scalpel"),
    (["vital", "monitor-vitals", "patient-monitor"],       "vitals"),
    (["ambulance", "emergency-vehicle", "ems", "911"],     "ambulance"),
    (["prescription", "rx", "script"],                     "prescription"),
    (["wheelchair", "mobility", "accessibility"],          "wheelchair"),
    (["needle", "vaccin", "injecti"],                      "syringe"),
    (["infusion", "iv", "drip", "intraven"],               "iv-drip"),
    (["dna", "gene", "genom", "sequenc"],                  "dna"),
    (["lab", "biolog", "molecul", "specimen"],             "microscope"),
    (["brain", "cogniti", "neuro"],                        "brain"),
    (["respirat", "breath", "lung"],                       "lungs"),
    (["sample", "test-tube", "assay"],                     "test-tube"),
    (["hospital", "clinic", "facility"],                   "hospital"),
    (["medical-record", "medical record", "ehr", "emr"],   "clipboard-medical"),
    (["device", "samd", "simd"],                           "circuit"),

    # Regulatory / QMS
    (["regulator", "fda", "510(k)", "510k", "submission", "pccp", "ema"], "shield-check"),
    (["audit", "iso 13485", "iso 14971", "iec 62304"],     "certificate"),
    (["release", "approval", "stamp", "sign-off"],         "stamp"),
    (["risk-management", "iso 14971", "hazard", "fmea"],   "scale-justice"),
    (["cert", "certif", "ribbon", "credenti"],             "ribbon"),
    (["sign", "signat", "signoff"],                        "signature"),

    # Engineering
    (["mechanic", "machine", "gear", "tolera"],            "gear"),
    (["wrench", "fix", "repair"],                          "wrench"),
    (["circuit", "pcb", "schematic"],                      "circuit"),
    (["chip", "asic", "microchip", "soc", "mcu"],          "microchip"),
    (["measure", "ruler", "dimens"],                       "ruler"),
    (["draw", "blueprint", "cad", "design"],               "blueprint"),
    (["compass", "geomet"],                                "compass-tool"),

    # Software / dev / infra
    # Order matters: more-specific phrases first.
    (["task-first", "hard gate", "gating"],                "lock"),
    (["one task", "task, one", "one file"],                "stack-sheets"),
    (["session-start", "security check"],                  "shield"),
    (["task", "lifecycle", "active"],                      "queue"),
    (["terminal", "shell", "cli", "command"],              "terminal"),
    (["code", "source", "implement", "program"],           "code-brackets"),
    (["branch", "fork"],                                   "git-branch"),
    (["merge", "pull-request", "pull request"],            "git-merge"),
    (["container", "docker", "kubernetes", "k8s", "pod"],  "container"),
    (["database", "sql", "postgres", "mysql", "store"],    "database"),
    (["cloud", "aws", "gcp", "azure"],                     "cloud"),
    (["api", "endpoint", "rest", "graphql", "rpc"],        "api-sync"),
    (["plug", "integrat", "mcp", "connector"],             "plug"),
    (["docflow", "convert", "round-trip", "pipeline", "flow", "xform"], "pipeline"),
    (["lens", "agentic-lens", "focus", "spec"],            "lens"),

    # Documents / process
    (["document", "file", "doc"],                          "document"),
    (["folder", "directory", "tree"],                      "folder"),
    (["archive", "package", "bundle"],                     "archive"),
    (["search", "find", "query"],                          "search"),
    (["link", "url", "href"],                              "link"),
    (["tag", "label", "metadata"],                         "tag"),
    (["bookmark", "favorite", "pin"],                      "bookmark"),
    (["calendar", "schedule", "date"],                     "calendar"),
    (["timer", "duration", "clock"],                       "timer"),
    (["flag", "milestone"],                                "flag"),
    (["readme", "convention", "rule", "format"],           "stack-sheets"),

    # People / communication
    (["team", "panel", "advisor", "advisors", "kol", "expert"], "users"),
    (["agent", "persona"],                                 "user-single"),
    (["chat", "conversation", "message", "thread"],        "chat"),
    (["broadcast", "announc", "notify"],                   "megaphone"),
    (["email", "mail", "inbox"],                           "mail"),
    (["handoff", "agreement", "contract"],                 "handshake"),

    # Security
    (["security", "secops", "secure"],                     "shield"),
    (["lock", "gate", "block", "deny", "permission"],      "lock"),
    (["key", "credential", "auth", "oauth"],               "key"),
    (["fingerprint", "biometr", "ident"],                  "fingerprint"),
    (["watch", "monitor", "observ"],                       "eye-watch"),

    # Data / analytics
    (["chart-bar", "histogram", "bar"],                    "chart-bar"),
    (["chart", "trend", "metric", "kpi"],                  "chart-line"),
    (["pie", "share", "split", "compos"],                  "chart-pie"),
    (["gauge", "speedometer", "rpm-dial"],                 "gauge"),
    (["dashboard", "panel", "console", "view"],            "dashboard"),

    # Workflow / state
    (["check", "ok", "pass", "valid", "approve"],          "check-circle"),
    (["fail", "error", "reject"],                          "x-circle"),
    (["warn", "warning", "alert", "caution"],              "warn"),
    (["info", "note", "hint"],                             "info-circle"),
    (["hook", "tripwire", "trigger", "fire"],              "lightning"),
    (["refresh", "rebuild", "regenerat"],                  "refresh"),
    (["sync", "synchroniz", "update"],                     "sync"),
    (["queue", "list", "backlog"],                         "queue"),
    # Project-specific catalog items — placed before the generic "strateg"
    # entry so the categorizer's "strategy" category key doesn't shadow them.
    (["tracker", "kpi", "scoreboard"],                     "chart-line"),
    (["trace-matrix", "trace matrix", "traceability"],     "git-branch"),
    (["dhf-manifest", "manifest"],                         "compass-rose"),
    (["advisors", "advisor"],                              "users"),
    (["strateg", "lesson", "capture", "insight", "real time"], "star"),
    (["compass", "navigat", "direction"],                  "compass-rose"),

    # AI / agents / LLM
    (["ai-", "llm", "model", "claude-ai", "gpt", "gemini", " ai "], "robot"),
    (["mental", "cogniti", "thinking"],                    "brain-circuit"),
    (["magic", "highlight", "feature"],                    "sparkles"),

    # Project / repo / source-of-truth (lower-priority generic catches)
    (["source of truth", "manifest", "config", "yaml", "single", "registry"], "compass-rose"),
    (["fabricat", "verify", "[verify]", "ground", "citation"], "search"),
    (["demo", "banner", "mark"],                           "tag"),

    # ===== Extended categories (v0.2-rebuild expansion) =====

    # Engineering / hardware extended
    (["caliper", "tolerance check", "precision-measure"],  "caliper"),
    (["multimeter", "voltage", "amperage", "ohm"],         "multimeter"),
    (["screwdriver", "fasten", "drive"],                   "screwdriver"),
    (["hammer", "strike", "nail"],                         "hammer"),
    (["hard-hat", "construction", "site-safety", "ppe"],   "hard-hat"),
    (["valve", "regulator-flow", "spigot"],                "valve"),
    (["sensor", "transducer", "iot-sensor"],               "sensor"),
    (["antenna", "broadcast-rf", "wireless-rf"],           "antenna"),
    (["battery", "power", "charge", "voltage-cell"],       "battery"),

    # Tooling / craft
    (["toolbox", "kit", "set-of-tools", "toolset"],        "toolbox"),
    (["puzzle", "piece", "modular", "component"],          "puzzle"),
    (["magnet", "attract", "polarity"],                    "magnet"),
    (["level-tool", "alignment", "horizontal", "plumb"],   "level-tool"),
    (["filter", "funnel", "narrow", "select"],             "filter-funnel"),

    # Web / UI / Internet
    (["browser", "web-page", "webpage", "site-page"],      "browser"),
    (["window-ui", "window", "dialog", "modal"],           "window-ui"),
    (["mouse-pointer", "click", "cursor"],                 "mouse-pointer"),
    (["globe", "internet", "www", "world"],                "globe-www"),
    (["server", "rack", "datacenter", "host-machine"],     "server-rack"),
    (["load-balancer", "traffic-split", "load-balance"],   "load-balancer"),
    (["share", "social", "broadcast-net"],                 "share-net"),
    (["https", "ssl", "tls", "secure-connection"],         "https-secure"),
    (["wifi", "wireless", "signal-strength"],              "wifi-signal"),

    # Ideas / vision / leadership
    (["idea", "lightbulb", "insight-spark", "eureka"],     "lightbulb"),
    (["north-star", "guiding", "polestar"],                "north-star"),
    (["telescope", "future-look", "long-view", "horizon"], "telescope"),
    (["vision", "see-the-future", "outlook"],              "vision-eye"),
    (["mountain", "summit", "peak", "ascent", "climb"],    "mountain-summit"),
    (["podium", "stage", "speaker"],                       "podium"),
    (["trophy", "award", "win", "champion"],               "trophy"),
    (["medal", "honor", "recognition"],                    "medal"),
    (["crown", "leader", "authority", "executive"],        "crown"),
    (["roadmap", "journey", "path-forward"],               "roadmap"),
    (["beacon", "signal-fire", "light-house"],             "beacon"),
    (["raise-hand", "volunteer", "advocate"],              "hand-raised"),

    # Strategy / planning
    (["target", "bullseye", "objective", "goal-set"],      "target-bullseye"),
    (["chess", "tactic", "game-plan", "strategic-move"],   "chess-king"),
    (["scenario", "decision-tree", "branching"],           "scenario-tree"),
    (["heatmap", "intensity-grid", "density-map"],         "heatmap"),
    (["map", "pin", "geo", "place"],                       "map-pin"),
    (["hourglass", "deadline", "time-pressure"],           "hourglass"),
    (["finish", "checkered-flag", "race"],                 "flag-checkered"),

    # Reporting / analytics extended
    (["ledger", "books", "accounting"],                    "ledger"),
    (["scorecard", "report-card", "evaluation"],           "scorecard"),
    (["traffic-light", "rag-status", "ryg"],               "traffic-light"),
    (["heatmap", "intensity-grid", "density-map"],         "heatmap"),
    (["audit-trail", "history-log", "changelog"],          "audit-trail"),
    (["report", "summary", "writeup"],                     "report-doc"),
    (["donut", "ring-chart", "completion"],                "donut"),
    (["ranking", "top-10", "leaderboard", "stack-rank"],   "ranking"),

    # Meeting / collaboration
    (["meeting", "session-mtg", "sync-up"],                "meeting"),
    (["whiteboard", "brainstorm", "diagram-board"],        "whiteboard"),
    (["thumbs-up", "approve-vote", "endorse"],             "thumbs-up"),
]


# ---------------------------------------------------------------------------
# Group-icon registry — when a catalog slide represents N instances of the
# same kind of thing (KOLs, test cases, rules, sites, predicates, …),
# every cell shares one "kind" icon and differentiates by name/color,
# not by glyph. detect_group() returns one of these keys (or None).
# ---------------------------------------------------------------------------

GROUP_ICONS: dict[str, str] = {
    "persona":   "user-single",
    "team":      "users",
    "test-case": "clipboard-medical",
    "rule":      "scale-justice",
    "site":      "hospital",
    "predicate": "circle-target",
    "document":  "document",
    "hazard":    "warn",
    "milestone": "flag",
    "metric":    "chart-line",
}

GROUP_TITLE_HINTS: list[tuple[list[str], str]] = [
    (["kol", "advisor", "advisors", "persona", "personas",
      "digital twin", "digital twins", "expert reviewer"], "persona"),
    (["team", "teams", "panel", "cohort", "participants"], "team"),
    (["test case", "test cases", "test protocol", "test protocols",
      "v&v", "verification protocol", "validation protocol"], "test-case"),
    (["rule", "rules", "policy", "policies", "convention",
      "conventions", "governance"], "rule"),
    (["site", "sites", "facility", "facilities", "clinic", "clinics",
      "location", "locations"], "site"),
    (["predicate", "predicates", "comparator"], "predicate"),
    (["deliverable", "deliverables", "artifact", "artifacts"], "document"),
    (["hazard", "hazards", "risk register", "failure mode"], "hazard"),
    (["milestone", "milestones", "gate", "gates", "phase"], "milestone"),
    (["kpi", "kpis", "metric", "metrics", "indicator"], "metric"),
]


# ---------------------------------------------------------------------------
# Generic fallback pool — used when no keyword matches. Hash-based selection
# so different unmapped labels get different generic icons.
# ---------------------------------------------------------------------------

FALLBACK_POOL: list[str] = [
    "hexagon", "diamond", "triangle-up", "circle-target",
    "square-rounded", "asterisk", "ring", "plus",
]


# ---------------------------------------------------------------------------
# Intent phrases — multi-word semantic patterns that should match BEFORE the
# single-word keyword registry. These capture *what the slide is actually
# about* (the hazard, the failure mode, the concept) rather than incidental
# vocabulary. First match wins; ordered most-specific first.
# ---------------------------------------------------------------------------

INTENT_PHRASES: list[tuple[list[str], str]] = [
    # Hazards / failure modes — medical-device specific
    (["free flow", "uncontrolled bolus", "anti-free-flow", "runaway flow"], "leak-drop"),
    (["drug library mismatch", "wrong concentration", "overdose",
      "underdose", "mismapped"], "pill"),
    (["alarm fatigue", "alarm masking", "nuisance alarm",
      "alarm habituate", "alert habituate"], "bell-alarm"),
    (["battery depletion", "depleted battery", "battery low",
      "battery reserve", "grace-period"], "battery-low"),
    (["pump tampering", "tamper", "unauthorized access",
      "intrusion", "tamper-evident"], "tamper-shield"),
    (["software defect", "regression", "calculation error",
      "code defect", "dose calculation", "field-failure"], "bug-defect"),
    # Concept / phrase shortcuts — strong signals that should not lose
    # to incidental substrings.
    (["digital twin", "persona advisor"], "user-single"),
    (["filing scope", "in-scope", "out of scope"], "scale-justice"),
    (["substantial equivalence", "predicate device"], "circle-target"),
    (["risk register", "hazard register"], "warn"),
    (["change control", "change protocol"], "git-merge"),
    (["dose-error reduction", "dose reduction"], "shield-check"),
]


def _scan_phrases(s: str) -> str | None:
    """Return an icon NAME if any INTENT_PHRASES entry matches; else None."""
    for phrases, name in INTENT_PHRASES:
        for p in phrases:
            if p in s:
                return name
    return None


def _scan_keywords(s: str) -> str | None:
    """Return an icon NAME from KEYWORD_REGISTRY if any keyword matches; else None."""
    for kws, name in KEYWORD_REGISTRY:
        for kw in kws:
            if kw in s:
                return name
    return None


def pick_strict(label: str) -> str | None:
    """Return SVG markup if `label` produces a phrase or keyword match.

    Returns None when no semantic match exists (i.e. the label would have
    fallen back to a hash-based generic). Useful for prioritized lookup
    where the caller wants to try the slide's primary label first, then a
    broader corpus only if the primary label produced no signal.
    """
    s = (label or "").lower()
    name = _scan_phrases(s) or _scan_keywords(s)
    if name is None:
        return None
    return ICONS.get(name, ICONS["hexagon"])


def pick(label: str) -> str:
    """Return inline SVG markup for the given label.

    Strategy:
      1. Multi-word INTENT_PHRASES (most specific). Captures hazard /
         failure-mode / concept patterns the author actually wrote.
      2. KEYWORD_REGISTRY single-word substrings (broad).
      3. Hash-based selection from FALLBACK_POOL (so unmapped labels still
         get visual variety instead of all-hexagon).
    """
    s = (label or "").lower()
    name = _scan_phrases(s)
    if name is None:
        name = _scan_keywords(s)
    if name is not None:
        return ICONS.get(name, ICONS["hexagon"])
    digest = hashlib.md5(s.encode()).digest()[0]
    chosen = FALLBACK_POOL[digest % len(FALLBACK_POOL)]
    return ICONS.get(chosen, ICONS["hexagon"])


def detect_group(items: list, title: str = "", hint: str = "") -> str | None:
    """Return a group-type key (e.g. "persona") if the catalog represents
    N instances of the same kind of thing; otherwise None.

    Signals (any one trips it):
      1. Explicit `hint` argument.
      2. Slide title matches a whitelisted group noun.

    Conservative: requires ≥4 items so small lists don't accidentally
    collapse. Lexical-homogeneity (signal 3) deferred to v0.3.
    """
    if not items or len(items) < 4:
        return None

    if hint:
        h = hint.lower().strip()
        if h in GROUP_ICONS:
            return h

    t = (title or "").lower()
    for kws, group_key in GROUP_TITLE_HINTS:
        for kw in kws:
            if kw in t:
                return group_key

    return None


def pick_group(group_type: str) -> str:
    """Return the inline SVG for the kind-icon associated with a group type."""
    name = GROUP_ICONS.get(group_type, "user-single")
    return ICONS.get(name, ICONS["hexagon"])


def list_icons() -> list[str]:
    """Return the sorted list of icon names (for debugging / docs)."""
    return sorted(ICONS.keys())
