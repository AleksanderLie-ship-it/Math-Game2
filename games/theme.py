"""
theme.py
--------
Single source of truth for the UI palette.

Why this exists
---------------
v0.7.12 starts the dark-mode rollout by centralising the palette here.
Hex codes used to live inline in `game.py`, `slideshow_frame.py`,
`base_game.py`, `stats_screen.py`, etc. Each new screen would copy a
slightly different shade of the same colour, and the "Dark mode" toggle
in Settings stayed permanently "Coming soon" because flipping it would
have required hunting hex codes across half the codebase.

Foundation contract
-------------------
* `theme()` returns a dict of named colour tokens for the active palette.
* The active palette is selected by `settings.get("theme")`:
      - "light"  (default)  → `_LIGHT`
      - "dark"              → `_DARK`
* Tokens must be stable strings — downstream code looks them up by name.
  Add new tokens; do NOT rename existing ones without grepping.
* Existing screens that hardcode hex are NOT migrated yet — they remain
  visually identical in light mode and look mismatched in dark mode
  until each is touched. The Settings "Dark mode" toggle therefore stays
  disabled until rollout completes; this module is the foundation that
  makes that rollout mechanical rather than archaeological.

Token names mirror `slideshow_frame.py`'s palette so existing tutorial
modules can migrate by a single line change (`from .theme import theme; T = theme()`)
without renaming references.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

from .settings_manager import settings


# ── Light (default) ──────────────────────────────────────────────────────────
#
# Mirrors the values that were previously hardcoded across the codebase.
# Any change here is a global cosmetic change in light mode — verify on
# the menu, BaseGame, tutorials_panel, and stats_screen before shipping.

_LIGHT = {
    # surfaces
    "bg":           "#f8fafc",   # page background
    "card_bg":      "white",     # raised card surface
    "card_border":  "#e2e8f0",   # 1px card outline
    "soft":         "#f1f5f9",   # secondary surface (locked tiles, scratch pad)
    "shop_locked":  "#f1f5f9",

    # ink
    "ink":          "#0f172a",   # primary text
    "muted":        "#64748b",   # secondary text
    "dim":          "#94a3b8",   # tertiary text / placeholder
    "faint":        "#cbd5e1",   # disabled text / hairline

    # accents
    "accent":       "#4f46e5",   # primary action / Tutorials & Helper
    "accent_dark":  "#4338ca",   # primary action hover
    "good":         "#15803d",   # correct answer / Beginner badge
    "good_bg":      "#f0fdf4",
    "warn":         "#b45309",   # Intermediate badge fg
    "warn_bg":      "#fffbeb",
    "danger":       "#b91c1c",   # wrong answer / Advanced badge fg
    "danger_bg":    "#fef2f2",
    "review":       "#4f46e5",
    "review_bg":    "#f0f4ff",
    "insight":      "#047857",
    "insight_bg":   "#ecfdf5",
    "shop":         "#9333ea",   # Shop accent (purple — distinct from review/insight)
    "shop_bg":      "#faf5ff",
    "highlight_bg": "#fffbeb",   # leaderboard #1 row

    # progress / chrome
    "progress_fill":"#0f172a",
    "progress_track":"#e2e8f0",
}


# ── Dark (foundation only — not user-toggleable until rollout completes) ────
#
# Keep tokens 1:1 with _LIGHT so theme() consumers never see a missing key.
# Values are first-pass — Aleks will tune once the screens that consume
# them actually exist. Stay close to the slate-9xx scale and the indigo
# accent so it feels like the same product, not a different app.

_DARK = {
    "bg":           "#0b1120",
    "card_bg":      "#0f172a",
    "card_border":  "#1e293b",
    "soft":         "#1e293b",
    "shop_locked":  "#1e293b",

    "ink":          "#e2e8f0",
    "muted":        "#94a3b8",
    "dim":          "#64748b",
    "faint":        "#475569",

    "accent":       "#818cf8",
    "accent_dark":  "#6366f1",
    "good":         "#4ade80",
    "good_bg":      "#052e16",
    "warn":         "#facc15",
    "warn_bg":      "#3b2f0a",
    "danger":       "#f87171",
    "danger_bg":    "#3f1414",
    "review":       "#a5b4fc",
    "review_bg":    "#1e1b4b",
    "insight":      "#6ee7b7",
    "insight_bg":   "#062b22",
    "shop":         "#c084fc",
    "shop_bg":      "#2e1065",
    "highlight_bg": "#3b2f0a",

    "progress_fill":"#818cf8",
    "progress_track":"#1e293b",
}


_PALETTES = {
    "light": _LIGHT,
    "dark":  _DARK,
}


def theme() -> dict:
    """Return the active palette dict.

    Reads `settings.get('theme')` each call so a flipped setting takes
    effect on the next screen rebuild. Falls back to light for any
    unknown value (including the legacy unset case).
    """
    name = settings.get("theme") or "light"
    return _PALETTES.get(name, _LIGHT)


def is_dark() -> bool:
    """Convenience predicate; True when dark mode is active."""
    return (settings.get("theme") or "light") == "dark"
