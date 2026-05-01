"""
games.tutorials
---------------
Tutorial slideshows — one per game mode where a guided explanation adds value.

Architecture
------------
* `slideshow_frame.SlideshowFrame` — reusable widget that renders a slide list
  on a Canvas with prev/next/close navigation and an optional
  "Next example" toggle. Pure framework, no content.
* `tutorial_<game_id>.py` — per-game content module. Exports:
      TITLE    : str            — shown in the header
      LEAD     : str            — short one-liner under the title
      SLIDES   : list[Slide]    — ordered steps
      EXAMPLES : list[dict]     — curated worked examples
* This `__init__.py` — registry mapping game_id → content module.
  Adding a new tutorial is a single line here + one file.

Notes
-----
* `mult_basic` has no tutorial by design — single-digit × single-digit is
  memorisation, not a concept.
* All in-game UI (including slide text) is in English. The Norwegian copy
  lives in the parent-facing PDF report only.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

from . import tutorial_conv_basic
from . import tutorial_conv_intermediate
from . import tutorial_div_advanced
from . import tutorial_div_basic
from . import tutorial_div_intermediate
from . import tutorial_frac_advanced
from . import tutorial_frac_basic
from . import tutorial_frac_intermediate
from . import tutorial_mult_advanced
from . import tutorial_mult_intermediate


# ── Registry ─────────────────────────────────────────────────────────────────
#
# Add new tutorials here. Order follows GAME_IDS in achievements.py so the
# tutorials panel lays them out in curriculum order.

TUTORIAL_REGISTRY: dict[str, object] = {
    # "mult_basic":        None,   # intentionally no tutorial — see INTENTIONAL_NO_GUIDE
    "mult_intermediate": tutorial_mult_intermediate,
    "mult_advanced":     tutorial_mult_advanced,
    "div_basic":         tutorial_div_basic,
    "div_intermediate":  tutorial_div_intermediate,
    "div_advanced":      tutorial_div_advanced,
    "frac_basic":        tutorial_frac_basic,
    "frac_intermediate": tutorial_frac_intermediate,
    "frac_advanced":     tutorial_frac_advanced,
    "conv_basic":        tutorial_conv_basic,
    "conv_intermediate": tutorial_conv_intermediate,
    # conv_advanced intentionally has no tutorial — it's the union of the
    # two methods already taught (frac↔dec from Beginner, frac↔pct from
    # Intermediate). See INTENTIONAL_NO_GUIDE below.
}

# Game modes that intentionally have no tutorial. The panel renders these
# with a "No guide needed" placeholder explaining why. Anything NOT in
# this set and NOT in TUTORIAL_REGISTRY is a genuine TODO — the panel
# will render a "Guide coming soon" placeholder instead, so we don't
# mislabel substantive topics (short division, long division, fractions)
# as "nothing to walk through".
INTENTIONAL_NO_GUIDE: set[str] = {
    "mult_basic",     # single-digit × single-digit is pure memorisation
    "conv_advanced",  # union of conv_basic (frac↔dec) and conv_intermediate
                      # (frac↔pct) — no new method to teach, just mixed

                      # directions. Per-gid copy in tutorials_panel
                      # explains "all three forms are the same number".
}


def get_tutorial(game_id: str):
    """Return the tutorial module for a game_id, or None if there isn't one."""
    return TUTORIAL_REGISTRY.get(game_id)


def has_tutorial(game_id: str) -> bool:
    return game_id in TUTORIAL_REGISTRY


def is_intentionally_no_guide(game_id: str) -> bool:
    return game_id in INTENTIONAL_NO_GUIDE
