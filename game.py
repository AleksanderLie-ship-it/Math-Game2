"""
game.py
-------
Main entry point. Shows the profile screen, then the game-selection menu,
and launches mini-games.

Menu architecture (v0.7.12)
---------------------------
The main menu is two rows:

  Row 1 — Game families (4 tiles): Multiplication, Division,
          Fractions: Operations, Fractions: Conversions. One tile per
          family. Click a tile -> difficulty-selection screen with three
          cards (Beginner / Intermediate / Advanced).

  Row 2 — Tools (4 tiles): Practice Missed, Progress & Stats,
          Tutorials, Shop (locked, ships with v0.8.0).

To add a new game family:
  1. Create games/<family>_basic.py / _intermediate.py / _advanced.py
     subclassing BaseGame.
  2. Add an entry to GAMES below — one family record with a
     difficulties list of three classes / game_ids.
  3. (Optional) drop PNGs in assets/games/<family>/<difficulty>.png to
     replace the emoji placeholders on the difficulty cards. See
     games/assets_loader.py for the path contract.

Foundation hooks landed in v0.7.12 (ready, not yet active):
  * games.theme.theme()       — palette source-of-truth (light + dark).
                                 New menu screens read from it. Existing
                                 screens keep their hardcoded hex until
                                 each is migrated; dark-mode toggle in
                                 Settings stays disabled until then.
  * games.assets_loader       — optional per-difficulty PNG loader with
                                 emoji fallback so adding art later is
                                 a zero-code drop-in.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

__version__ = "0.8.2"

import tkinter as tk
from tkinter import ttk, messagebox

from games.mult_basic         import MultiplicationBasic
from games.mult_intermediate  import MultiplicationIntermediate
from games.mult_advanced      import MultiplicationAdvanced
from games.div_basic          import DivisionBasic
from games.div_intermediate   import DivisionIntermediate
from games.div_advanced       import DivisionAdvanced
from games.frac_basic         import FracBasic
from games.frac_intermediate  import FracIntermediate
from games.frac_advanced      import FracAdvanced
from games.conv_basic         import ConvBasic
from games.conv_intermediate  import ConvIntermediate
from games.conv_advanced      import ConvAdvanced
from games.practice_missed    import PracticeMissed
from games.stats_screen       import StatsScreen
from games.tutorials.tutorials_panel import TutorialsPanel
from games.tutorials          import TUTORIAL_REGISTRY
from games.screens.shop_modal import SHOP_ITEMS
from games.profile_manager    import (
    list_profiles, create_profile, delete_profile, load_stores, last_profile,
)
from games.settings_manager   import settings
from games.achievements       import (
    ACHIEVEMENTS, ACHIEVEMENTS_BY_ID, CATEGORY_ORDER,
    UNLOCK_REQUIREMENTS, GAME_NAMES, GAME_IDS, GAME_SHORT,
)
from games.theme              import theme
from games.assets_loader      import game_tile_image, tier_glyph


# ── Game family registry ───────────────────────────────────────────────────────
#
# One entry per game family. Each family expands to three difficulties on the
# difficulty-selection screen. The shape was widened in v0.7.12 from a flat
# list-of-cards into this nested form so the main menu can compress to four
# tiles instead of twelve, and so future families plug in by appending a
# single record.
#
# Per-difficulty `asset_key` matches the path `assets/games/<family_id>/<key>.png`
# read by `assets_loader.game_tile_image`. PNGs are optional — the renderer
# falls back to `assets_loader.tier_glyph(key)` (🌱 / 🔥 / ⚡) when missing.

GAMES = [
    {
        "id":      "mult",
        "label":   "Multiplication",
        "tagline": "Times tables, multi-digit partial products, the X-shift method.",
        "glyph":   "✕",
        "accent":  "#4f46e5",
        "difficulties": [
            {
                "key":       "basic",
                "name":      "Beginner",
                "desc":      "Times tables 1-10.\nBuild speed and confidence.",
                "cls":       MultiplicationBasic,
                "game_id":   "mult_basic",
            },
            {
                "key":       "intermediate",
                "name":      "Intermediate",
                "desc":      "Two-digit and mixed problems.\nLike 34 x 7 or 34 x 78.",
                "cls":       MultiplicationIntermediate,
                "game_id":   "mult_intermediate",
            },
            {
                "key":       "advanced",
                "name":      "Advanced",
                "desc":      "Three-digit x two-digit.\nLike 134 x 78.",
                "cls":       MultiplicationAdvanced,
                "game_id":   "mult_advanced",
            },
        ],
    },
    {
        "id":      "div",
        "label":   "Division",
        "tagline": "Norwegian short division and trappa long division into decimals.",
        "glyph":   "÷",
        "accent":  "#0ea5e9",
        "difficulties": [
            {
                "key":       "basic",
                "name":      "Beginner",
                "desc":      "Whole-number answers.\nDivisors from 2 to 10.",
                "cls":       DivisionBasic,
                "game_id":   "div_basic",
            },
            {
                "key":       "intermediate",
                "name":      "Intermediate",
                "desc":      "Larger dividends.\nAlways whole-number answers.",
                "cls":       DivisionIntermediate,
                "game_id":   "div_intermediate",
            },
            {
                "key":       "advanced",
                "name":      "Advanced",
                "desc":      "Large numbers + decimal answers.\nLike 13 / 2 = 6.5.",
                "cls":       DivisionAdvanced,
                "game_id":   "div_advanced",
            },
        ],
    },
    {
        "id":      "frac",
        "label":   "Fractions: Operations",
        "tagline": "Adding and subtracting fractions with same / different / unrelated denominators.",
        "glyph":   "½",
        "accent":  "#9333ea",
        "difficulties": [
            {
                "key":       "basic",
                "name":      "Beginner",
                "desc":      "Same-denominator +/−.\nLike 2/5 + 1/5 = 3/5.",
                "cls":       FracBasic,
                "game_id":   "frac_basic",
            },
            {
                "key":       "intermediate",
                "name":      "Intermediate",
                "desc":      "Different denominators.\nFind the common denominator first.",
                "cls":       FracIntermediate,
                "game_id":   "frac_intermediate",
            },
            {
                "key":       "advanced",
                "name":      "Advanced",
                "desc":      "Unrelated denominators.\nLike 3/13 + 9/19 = 174/247.",
                "cls":       FracAdvanced,
                "game_id":   "frac_advanced",
            },
        ],
    },
    {
        "id":      "conv",
        "label":   "Fractions: Conversions",
        "tagline": "Switching between fractions, decimals, and percentages.",
        "glyph":   "%",
        "accent":  "#10b981",
        "difficulties": [
            {
                "key":       "basic",
                "name":      "Beginner",
                "desc":      "Fractions ↔ decimals.\nLike 3/4 = 0.75.",
                "cls":       ConvBasic,
                "game_id":   "conv_basic",
            },
            {
                "key":       "intermediate",
                "name":      "Intermediate",
                "desc":      "Fractions ↔ percentages.\nLike 1/4 = 25%.",
                "cls":       ConvIntermediate,
                "game_id":   "conv_intermediate",
            },
            {
                "key":       "advanced",
                "name":      "Advanced",
                "desc":      "All three directions.\nFraction, decimal, percentage.",
                "cls":       ConvAdvanced,
                "game_id":   "conv_advanced",
            },
        ],
    },
]


# Difficulty-tier metadata (shared across all families). Order matters —
# this is also the order in which difficulty cards are rendered.
_DIFFICULTY_TIERS = [
    {"key": "basic",        "label": "Beginner",     "badge_bg_token": "good_bg",   "badge_fg_token": "good"},
    {"key": "intermediate", "label": "Intermediate", "badge_bg_token": "warn_bg",   "badge_fg_token": "warn"},
    {"key": "advanced",     "label": "Advanced",     "badge_bg_token": "danger_bg", "badge_fg_token": "danger"},
]


# ── App controller ─────────────────────────────────────────────────────────────

class App:
    def __init__(self, root):
        T = theme()
        self.root = root
        self.root.title(f"Math Practice  v{__version__}")
        # 1120x800 fits the v0.7.12 compressed menu (4 family tiles + 4-tile
        # tools row + header + footer) without requiring a scrollbar at
        # the default size. The auto-hide scrollbar in show_menu kicks in
        # only when the user shrinks the window below the content height.
        #
        # Minimum width is 1080 — below that the 4 equal-width family
        # tiles squish past their labels ("Fractions: Conversions" wraps
        # awkwardly and the rightmost tile starts clipping). Computed
        # floor: 4 tiles × ~235 px + 3 × 14 px gap + 2 × 48 px section
        # padding ≈ 1078, rounded up.
        # v0.8.0.1: 1120x800 → 1180x920. The 800-tall window still
        # triggered the auto-hide scrollbar at default size (header +
        # games row + tools row + footer + page padding ≈ 850 px).
        # Bumped past that threshold so a fresh launch is scroll-free.
        self.root.geometry("1180x850")
        self.root.minsize(1080, 700)
        self.root.configure(bg=T["bg"])
        self._apply_styles()

        self._current       = None
        self._scroll_target = None

        # The difficulty-selection screen needs to know which family it
        # belongs to so the back-button on the game itself can return to
        # the right difficulty page (rather than the main menu directly).
        # Cleared by show_menu(); set by show_difficulty(family).
        self._current_family = None

        # Tk garbage-collects PhotoImage instances the moment the
        # function that loaded them returns, even if the widget is still
        # on screen. We hold every loaded tile image in this list so it
        # stays alive for as long as the App does. show_menu() and
        # show_difficulty() both clear and repopulate it on rebuild.
        self._tile_images: list[tk.PhotoImage] = []

        # Active profile stores — set after profile selection
        self._profile_name    = None
        self._ach_store       = None
        self._missed_store    = None
        self._scores_store    = None
        self._sessions_store  = None
        self._purchases_store = None   # v0.7.13: cosmetic ledger

        # Persistent root-level mousewheel. Installed now and re-installed
        # every time show_menu() runs — subscreens (Stats, Practice Missed,
        # Tutorials) rebind <MouseWheel> via bind_all to scroll their own
        # canvases. bind_all is application-wide, so the menu must reclaim
        # the binding each time it becomes visible, or its scroll silently
        # dispatches to a destroyed subscreen canvas.
        self._install_wheel_handler()

        # Apply start-maximized before first screen shows
        if settings.get("start_maximized"):
            self.root.state("zoomed")

        # Auto-login: skip profile screen if setting is on and last profile exists
        last = last_profile()
        if settings.get("auto_login") and last and last in list_profiles():
            self._load_profile(last)
        else:
            self.show_profiles()

    # ----------------------------------------------------------------- styles

    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Horizontal.TProgressbar",
                        thickness=10,
                        troughcolor="#e2e8f0",
                        background="#0f172a",
                        bordercolor="#e2e8f0",
                        lightcolor="#0f172a",
                        darkcolor="#0f172a")

    # --------------------------------------------------------- profile screen

    def show_profiles(self):
        """Profile landing screen. Body lives in games.screens.profile_screen."""
        from games.screens.profile_screen import show_profile_screen
        show_profile_screen(self)

    def _load_profile(self, name: str):
        """Load profile + go to menu. Body in games.screens.profile_screen."""
        from games.screens.profile_screen import load_profile
        load_profile(self, name)

    # ---------------------------------------------------------------- settings

    def _show_settings(self):
        """Settings popup. Body lives in games.screens.settings_dialog."""
        from games.screens.settings_dialog import show_settings_dialog
        show_settings_dialog(self)

    # ------------------------------------------------------------------- menu

    def show_menu(self):
        """Main menu. Body lives in games.screens.main_menu."""
        from games.screens.main_menu import show_menu as _show
        _show(self)

    def _show_shop(self):
        """Shop modal. Body lives in games.screens.shop_modal."""
        from games.screens.shop_modal import show_shop_modal
        show_shop_modal(self)

    # ============================================================ difficulty page

    def show_difficulty(self, family):
        """Difficulty-selection screen. Body in games.screens.difficulty_screen."""
        from games.screens.difficulty_screen import show_difficulty as _show
        _show(self, family)

    # ------------------------------------------------------------ achievements

    def _show_achievements(self):
        """Trophy Room. Body lives in games.screens.trophy_room."""
        from games.screens.trophy_room import show_trophy_room
        show_trophy_room(self)

    # ----------------------------------------------------------------- launch

    def _launch(self, family, difficulty):
        """Launch a game. Back returns to the family's difficulty page."""
        T = theme()
        self._clear()
        frame = tk.Frame(self.root, bg=T["bg"])
        frame.pack(fill=tk.BOTH, expand=True)
        self._current = frame
        difficulty["cls"](
            frame,
            back_callback=lambda f=family: self.show_difficulty(f),
            ach_store=self._ach_store,
            missed_store=self._missed_store,
            scores_store=self._scores_store,
            sessions_store=self._sessions_store,
        )

    def _launch_practice(self):
        T = theme()
        self._clear()
        frame = tk.Frame(self.root, bg=T["bg"])
        frame.pack(fill=tk.BOTH, expand=True)
        self._current = frame
        PracticeMissed(frame,
                       back_callback=self.show_menu,
                       ach_store=self._ach_store,
                       missed_store=self._missed_store,
                       scores_store=self._scores_store,
                       sessions_store=self._sessions_store)

    def _launch_stats(self):
        T = theme()
        self._clear()
        frame = tk.Frame(self.root, bg=T["bg"])
        frame.pack(fill=tk.BOTH, expand=True)
        self._current = frame
        StatsScreen(frame,
                    back_callback=self.show_menu,
                    profile_name=self._profile_name,
                    ach_store=self._ach_store,
                    sessions_store=self._sessions_store,
                    scores_store=self._scores_store)

    def _launch_tutorials(self):
        T = theme()
        self._clear()
        frame = tk.Frame(self.root, bg=T["bg"])
        frame.pack(fill=tk.BOTH, expand=True)
        self._current = frame
        TutorialsPanel(frame,
                       back_callback=self.show_menu,
                       ach_store=self._ach_store)

    def _clear(self):
        self._scroll_target = None
        # Stop the matrix-rain after-loop before destroying its parent —
        # otherwise the loop would try to redraw a destroyed Canvas on
        # the next tick and emit a TclError into the console.
        try:
            for _r in getattr(self, "_matrix_rains", []) or []:
                try:
                    _r.stop()
                except Exception:
                    pass
            self._matrix_rains = []
        except Exception:
            self._matrix_rains = []
        if self._current is not None:
            self._current.destroy()
            self._current = None

    def _install_wheel_handler(self):
        """Install (or re-install) the root-level mousewheel handler."""
        def _content_fits(t):
            try:
                first, last = t.yview()
                return first <= 0.0 and last >= 1.0 - 1e-6
            except Exception:
                return True

        def _wheel(e):
            t = self._scroll_target
            if not t or _content_fits(t):
                return
            try:
                t.yview_scroll(int(-1 * (e.delta / 120)), "units")
            except Exception:
                pass

        def _wheel_up(_e):
            t = self._scroll_target
            if not t or _content_fits(t):
                return
            try:
                t.yview_scroll(-1, "units")
            except Exception:
                pass

        def _wheel_down(_e):
            t = self._scroll_target
            if not t or _content_fits(t):
                return
            try:
                t.yview_scroll(1, "units")
            except Exception:
                pass

        self.root.bind_all("<MouseWheel>", _wheel)
        self.root.bind_all("<Button-4>",   _wheel_up)
        self.root.bind_all("<Button-5>",   _wheel_down)


# Entry point

def main():
    """Entry point.

    v0.8.2: explicit WM_DELETE_WINDOW handler stops every after() loop
    (matrix rain, feedback timers, achievement popups) before destroy().
    Without this the Python process lingers after the window closes —
    Tk's after callbacks keep firing into a half-destroyed widget tree
    and prevent the interpreter from exiting cleanly. Symptom: the next
    `python game.py` or PyInstaller build fails with PermissionError
    "file in use" because the previous .exe is still running headless.

    Belt-and-braces: sys.exit(0) after mainloop returns forces interpreter
    teardown even if a leftover after() reference is somehow alive.
    """
    import sys
    root = tk.Tk()
    root.title(f"Math Practice  v{__version__}")
    app = App(root)

    def _on_close():
        try:
            app._clear()
        except Exception:
            pass
        try:
            root.quit()
            root.destroy()
        except Exception:
            pass
        sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", _on_close)
    try:
        root.mainloop()
    finally:
        try:
            app._clear()
        except Exception:
            pass
        sys.exit(0)


if __name__ == "__main__":
    main()
