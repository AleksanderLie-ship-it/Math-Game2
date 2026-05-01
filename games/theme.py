"""
theme.py
--------
Single source of truth for the UI palette.

Why this exists
---------------
v0.7.12 started the dark-mode rollout by centralising the palette here.
v0.7.13 wired it through every screen. v0.7.13.1 adds Matrix mode and
introduces dedicated `btn_primary_*` and `card_dim` tokens so primary
action buttons stay legible across themes (the Trophy Room button used
to vanish in dark mode because its bg was `T["ink"]` — same as the
text color).

Foundation contract
-------------------
* `theme()` returns a dict of named colour tokens for the active palette.
* The active palette is selected by `settings.get("theme")`:
      - "light"   (default)  → `_LIGHT`
      - "dark"               → `_DARK`     (unlocked via Shop, 500 pts)
      - "matrix"             → `_MATRIX`   (unlocked via Shop, 1000 pts)
* Tokens must be stable strings — downstream code looks them up by name.
  Add new tokens; do NOT rename existing ones without grepping every
  consumer in `game.py`, `base_game.py`, `stats_screen.py`,
  `practice_missed.py`, `tutorials_panel.py`, and the per-game files.

Adding a new theme
------------------
  1. Define a `_NAME` dict that mirrors every key in `_LIGHT`.
  2. Add it to `_PALETTES`.
  3. Append a SHOP_ITEMS entry in `game.py` (id="<name>_mode", price …).
  4. Add the radio in `_show_settings → Appearance`.
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
    "card_dim":     "#f1f5f9",   # disabled / locked card surface — recedes
    "soft":         "#f1f5f9",   # secondary surface (scratch pad, badges)
    "shop_locked":  "#f1f5f9",

    # ink
    "ink":          "#0f172a",   # primary text
    "muted":        "#64748b",   # secondary text
    "dim":          "#94a3b8",   # tertiary text / placeholder
    "faint":        "#cbd5e1",   # disabled text / hairline

    # primary-action button (e.g. Trophy Room, Play)
    "btn_primary_bg":   "#0f172a",
    "btn_primary_fg":   "white",
    "btn_primary_hover":"#1e293b",

    # accents
    "accent":       "#4f46e5",
    "accent_dark":  "#4338ca",
    "good":         "#15803d",
    "good_bg":      "#f0fdf4",
    "warn":         "#b45309",
    "warn_bg":      "#fffbeb",
    "danger":       "#b91c1c",
    "danger_bg":    "#fef2f2",
    "review":       "#4f46e5",
    "review_bg":    "#f0f4ff",
    "insight":      "#047857",
    "insight_bg":   "#ecfdf5",
    "shop":         "#9333ea",
    "shop_bg":      "#faf5ff",
    "highlight_bg": "#fffbeb",

    # progress / chrome
    "progress_fill":  "#0f172a",
    "progress_track": "#e2e8f0",
}


# ── Dark ────────────────────────────────────────────────────────────────────
#
# Calmer, more breathable than the v0.7.13 first cut. Surfaces lifted
# slightly so cards have a subtle elevation against the page; disabled
# `card_dim` collapses to the page bg so demoted tiles recede instead
# of standing out (the v0.7.13 Practice-Missed-disabled bug).

_DARK = {
    "bg":           "#0b1120",
    "card_bg":      "#111a2e",   # was #0f172a — slightly warmer / lifted
    "card_border":  "#1f2a44",
    "card_dim":     "#0b1120",   # collapses to page bg → demoted state
    "soft":         "#1e293b",
    "shop_locked":  "#1e293b",

    "ink":          "#e2e8f0",
    "muted":        "#94a3b8",
    "dim":          "#64748b",
    "faint":        "#475569",

    # Primary buttons in dark mode use the indigo accent so they pop
    # against the dark page. Without this, `bg=T["ink"]` (light grey)
    # rendered an invisible button — Trophy Room button bug.
    "btn_primary_bg":   "#4f46e5",
    "btn_primary_fg":   "white",
    "btn_primary_hover":"#4338ca",

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

    "progress_fill":  "#818cf8",
    "progress_track": "#1f2a44",
}


# ── Matrix ──────────────────────────────────────────────────────────────────
#
# The Matrix-movie aesthetic: green phosphor on black. Digits in the
# question display use `ink` (matrix green) automatically — the headline
# transformation the user asked for. Borders + accents lean monochrome
# green to keep the vibe; only badges (good / warn / danger) stay
# distinguishable so feedback states still read.

_MATRIX = {
    "bg":           "#000000",   # pure black background
    "card_bg":      "#020a02",   # near-black with a green tint
    "card_border":  "#003b00",   # dark phosphor outline
    "card_dim":     "#000000",   # disabled blends to bg
    "soft":         "#001a00",
    "shop_locked":  "#001a00",

    # v0.8.0.1: ink toned from #00ff41 → #00cc33 — the hot phosphor was
    # eye-fatiguing on big digit displays (52pt question text). The hot
    # green is preserved on `accent` and `btn_primary_bg` so buttons
    # still pop. Body text (10–11pt) reads more comfortably at the
    # calmer shade.
    "ink":          "#00cc33",
    "muted":        "#00992b",
    "dim":          "#007a22",
    "faint":        "#004d15",

    # Primary buttons: bright green with black text — high-contrast pop.
    "btn_primary_bg":   "#00ff41",
    "btn_primary_fg":   "#000000",
    "btn_primary_hover":"#00cc33",

    # Accents skewed toward the green spectrum but kept distinct so that
    # success / warn / danger still differentiate.
    "accent":       "#00ff66",
    "accent_dark":  "#00cc52",
    "good":         "#7fff00",
    "good_bg":      "#003300",
    "warn":         "#ffcc00",   # phosphor amber — terminal-warning yellow
    "warn_bg":      "#332600",
    "danger":       "#ff3333",   # red intentionally pops — error must not blend in
    "danger_bg":    "#330000",
    "review":       "#00ff66",
    "review_bg":    "#002211",
    "insight":      "#7fff00",
    "insight_bg":   "#003300",
    "shop":         "#00ff66",
    "shop_bg":      "#002211",
    "highlight_bg": "#002200",

    "progress_fill":  "#00ff41",
    "progress_track": "#003b00",
}


_PALETTES = {
    "light":  _LIGHT,
    "dark":   _DARK,
    "matrix": _MATRIX,
}


def theme() -> dict:
    """Return the active palette dict.

    Reads `settings.get('theme')` each call so a flipped setting takes
    effect on the next screen rebuild. Falls back to light for any
    unknown value (including the legacy unset case).
    """
    name = settings.get("theme") or "light"
    return _PALETTES.get(name, _LIGHT)


def theme_name() -> str:
    """Return the active theme key. Used by the Settings picker."""
    name = settings.get("theme") or "light"
    return name if name in _PALETTES else "light"


def available_themes() -> list[str]:
    """Stable list of theme keys in display order."""
    return ["light", "dark", "matrix"]


def is_dark() -> bool:
    """True when dark or matrix theme is active. Matrix is dark-on-green
    so screens that branch on `is_dark()` for extra outline strokes can
    use this without checking matrix separately."""
    return theme_name() in ("dark", "matrix")
