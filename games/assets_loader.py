"""
assets_loader.py
----------------
Optional asset loader for difficulty-tile artwork.

Why this exists
---------------
v0.7.12 lays the groundwork for "progressively cooler" per-difficulty
artwork on each game card. The art itself doesn't exist yet — Aleks
plans to commission / source it later. The renderer should:

  1. Look for `assets/games/<family_id>/<difficulty>.png` first.
  2. Fall back to a tier emoji glyph if the image is missing.

Either path renders without crashing, and adding art later is a
zero-code-change drop-in (just place the file at the expected path).

Asset path contract
-------------------
    assets/games/<family_id>/<difficulty>.png

    family_id  ∈ {"mult", "div", "frac", "conv"}
    difficulty ∈ {"basic", "intermediate", "advanced"}

PNGs only. tkinter's built-in PhotoImage in 3.x reads PNG natively;
no PIL dependency unless we later need resizing. If we do need PIL
(e.g. for crisp 256→128 downscaling of the avatar pack from v0.8.0),
we add it here behind a try/except so headless / dev-tooling paths
still import cleanly.

Reference-keeping
-----------------
Tk garbage-collects PhotoImage instances the moment the calling
function returns, even if the widget is still on screen. The caller
MUST keep a reference (e.g. `self._tile_images.append(img)` on the
App / screen object) — the loader only owns its return value, not
its lifetime.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import pathlib
import tkinter as tk


_REPO_ROOT  = pathlib.Path(__file__).resolve().parent.parent
_GAME_ASSET = _REPO_ROOT / "assets" / "games"


# ── Tier glyphs (emoji fallbacks) ──────────────────────────────────────────
#
# Used when no PNG exists at the expected path. Escalation across the
# three difficulties communicates "progressively cooler" without art:
# a sapling for Beginner, a flame for Intermediate, a lightning bolt
# for Advanced. These are pure visual placeholders — once real art ships
# the loader returns the image and these are never rendered.

TIER_GLYPHS = {
    "basic":        "🌱",
    "intermediate": "🔥",
    "advanced":     "⚡",
}


def game_tile_image(family_id: str, difficulty: str) -> tk.PhotoImage | None:
    """Return a tk.PhotoImage for the requested family/difficulty, or None.

    Caller MUST keep the returned image referenced for as long as the
    widget is on screen, otherwise Tk garbage-collects it and the tile
    renders blank. See module docstring.
    """
    if not family_id or not difficulty:
        return None
    path = _GAME_ASSET / family_id / f"{difficulty}.png"
    if not path.exists():
        return None
    try:
        return tk.PhotoImage(file=str(path))
    except Exception:
        # Corrupt PNG, unsupported subformat, or Tk image cache mishap —
        # any of these is recoverable: fall back to the tier glyph.
        return None


def tier_glyph(difficulty: str) -> str:
    """Return the emoji fallback glyph for a difficulty key. Empty if unknown."""
    return TIER_GLYPHS.get(difficulty, "")
