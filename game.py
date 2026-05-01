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

__version__ = "0.7.12"

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
        self.root = root
        self.root.title(f"Math Practice  v{__version__}")
        self.root.geometry("1080x720")
        self.root.minsize(920, 560)
        self.root.configure(bg="#f8fafc")
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
        """Landing screen — choose or create a profile."""
        self._clear()
        self._profile_name = None
        self._ach_store = self._missed_store = self._scores_store = None
        self._sessions_store = None

        outer = tk.Frame(self.root, bg="#f8fafc")
        outer.pack(fill=tk.BOTH, expand=True)
        self._current = outer

        # ── Centred card ──────────────────────────────────────────────────────
        wrapper = tk.Frame(outer, bg="#f8fafc")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(wrapper, text="Math Practice",
                 font=("Helvetica", 30, "bold"),
                 bg="#f8fafc", fg="#0f172a").pack(pady=(0, 4))
        tk.Label(wrapper, text="Who is playing?",
                 font=("Helvetica", 13), bg="#f8fafc", fg="#475569").pack(pady=(0, 28))

        profiles = list_profiles()

        if profiles:
            profiles_frame = tk.Frame(wrapper, bg="#f8fafc")
            profiles_frame.pack(pady=(0, 20))

            for name in profiles:
                self._profile_card(profiles_frame, name)

        # ── Divider ───────────────────────────────────────────────────────────
        if profiles:
            div_row = tk.Frame(wrapper, bg="#f8fafc")
            div_row.pack(fill=tk.X, pady=(4, 16))
            tk.Frame(div_row, bg="#e2e8f0", height=1).pack(
                side=tk.LEFT, fill=tk.X, expand=True, pady=8)
            tk.Label(div_row, text="  or  ", font=("Helvetica", 9),
                     bg="#f8fafc", fg="#94a3b8").pack(side=tk.LEFT)
            tk.Frame(div_row, bg="#e2e8f0", height=1).pack(
                side=tk.LEFT, fill=tk.X, expand=True, pady=8)

        # ── New profile entry ─────────────────────────────────────────────────
        new_frame = tk.Frame(wrapper, bg="#f8fafc")
        new_frame.pack()

        tk.Label(new_frame,
                 text="Create new profile" if profiles else "Enter your name to start:",
                 font=("Helvetica", 10, "bold"), bg="#f8fafc", fg="#0f172a").pack(anchor="w")

        entry_row = tk.Frame(new_frame, bg="#f8fafc")
        entry_row.pack(fill=tk.X, pady=(6, 0))

        name_var = tk.StringVar()
        name_entry = tk.Entry(entry_row, textvariable=name_var,
                              font=("Helvetica", 13), relief="solid", bd=1,
                              fg="#0f172a", width=20)
        name_entry.pack(side=tk.LEFT, ipady=6, padx=(0, 8))
        name_entry.focus_set()

        def _create(event=None):
            name = name_var.get().strip()
            if not name:
                return
            if not create_profile(name):
                messagebox.showwarning(
                    "Name taken",
                    f"A profile named '{name}' already exists.\nChoose a different name.",
                )
                return
            self._load_profile(name)

        name_entry.bind("<Return>", _create)
        tk.Button(entry_row, text="Start  →",
                  font=("Helvetica", 11, "bold"),
                  bg="#0f172a", fg="white", relief="flat", bd=0,
                  padx=14, pady=6, cursor="hand2",
                  activebackground="#1e293b", activeforeground="white",
                  command=_create).pack(side=tk.LEFT)

        # ── Footer ────────────────────────────────────────────────────────────
        footer = tk.Frame(outer, bg="#f8fafc")
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=8)
        tk.Label(footer,
                 text=f"Math Practice  v{__version__}  ·  © 2026 Aleksander Lie",
                 font=("Helvetica", 8), bg="#f8fafc", fg="#cbd5e1").pack(side=tk.LEFT, padx=16)
        tk.Button(footer, text="⚙  Settings",
                  font=("Helvetica", 9), bg="#f8fafc", fg="#94a3b8",
                  relief="flat", bd=0, padx=8, cursor="hand2",
                  activebackground="#f8fafc", activeforeground="#475569",
                  command=self._show_settings).pack(side=tk.RIGHT, padx=16)

    def _profile_card(self, parent, name):
        """A clickable card for an existing profile with a delete button."""
        card = tk.Frame(parent, bg="white",
                        highlightbackground="#e2e8f0", highlightthickness=1,
                        cursor="hand2")
        card.pack(fill=tk.X, pady=4)

        inner = tk.Frame(card, bg="white", padx=18, pady=12)
        inner.pack(fill=tk.X)

        # Name label
        name_lbl = tk.Label(inner, text=f"👤  {name}",
                            font=("Helvetica", 13, "bold"),
                            bg="white", fg="#0f172a", cursor="hand2")
        name_lbl.pack(side=tk.LEFT)

        # Delete button
        def _confirm_delete(n=name):
            if messagebox.askyesno(
                "Delete Profile",
                f"Permanently delete '{n}' and all their data?\n\nThis cannot be undone.",
                icon="warning",
            ):
                delete_profile(n)
                self.show_profiles()   # refresh

        tk.Button(inner, text="✕",
                  font=("Helvetica", 10), bg="white", fg="#94a3b8",
                  relief="flat", bd=0, padx=6, cursor="hand2",
                  activebackground="white", activeforeground="#b91c1c",
                  command=_confirm_delete).pack(side=tk.RIGHT)

        # Clicking card or name launches profile
        for w in (card, inner, name_lbl):
            w.bind("<Button-1>", lambda e, n=name: self._load_profile(n))

    def _load_profile(self, name: str):
        """Load stores for the chosen profile and go to game menu."""
        self._profile_name = name
        (self._ach_store, self._missed_store,
         self._scores_store, self._sessions_store) = load_stores(name)
        self.show_menu()

    # ---------------------------------------------------------------- settings

    def _show_settings(self):
        """Settings popup — global options, not per-profile."""
        root = self.root
        root.update_idletasks()
        cx = root.winfo_x() + root.winfo_width()  // 2
        cy = root.winfo_y() + root.winfo_height() // 2

        win = tk.Toplevel(root)
        win.title("Settings")
        win.configure(bg="#f8fafc")
        win.geometry(f"460x400+{cx - 230}+{cy - 200}")
        win.resizable(False, False)
        win.grab_set()

        # Header
        hdr = tk.Frame(win, bg="#0f172a", padx=24, pady=16)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="⚙  Settings",
                 font=("Helvetica", 15, "bold"),
                 bg="#0f172a", fg="white").pack(side=tk.LEFT)

        body = tk.Frame(win, bg="#f8fafc", padx=28, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        def _section(text):
            tk.Label(body, text=text.upper(),
                     font=("Helvetica", 9, "bold"),
                     bg="#f8fafc", fg="#94a3b8").pack(anchor="w", pady=(14, 4))
            tk.Frame(body, bg="#e2e8f0", height=1).pack(fill=tk.X, pady=(0, 10))

        def _toggle_row(label, desc, key, enabled=True):
            """A row with a label and a live-updating On/Off toggle."""
            row = tk.Frame(body, bg="#f8fafc")
            row.pack(fill=tk.X, pady=5)

            text_col = tk.Frame(row, bg="#f8fafc")
            text_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            fg = "#0f172a" if enabled else "#cbd5e1"
            tk.Label(text_col, text=label,
                     font=("Helvetica", 11, "bold"),
                     bg="#f8fafc", fg=fg).pack(anchor="w")
            tk.Label(text_col, text=desc,
                     font=("Helvetica", 9),
                     bg="#f8fafc", fg="#94a3b8" if enabled else "#e2e8f0").pack(anchor="w")

            if not enabled:
                tk.Label(row, text="Coming soon",
                         font=("Helvetica", 8), bg="#f8fafc",
                         fg="#cbd5e1").pack(side=tk.RIGHT, padx=4)
                return

            val = tk.BooleanVar(value=settings.get(key))
            btn_frame = tk.Frame(row, bg="#f8fafc")
            btn_frame.pack(side=tk.RIGHT)

            def _refresh_btn():
                on = val.get()
                btn.configure(
                    text="ON " if on else "OFF",
                    bg="#0f172a" if on else "#e2e8f0",
                    fg="white"  if on else "#94a3b8",
                )

            def _toggle():
                val.set(not val.get())
                settings.set(key, val.get())
                _refresh_btn()

            btn = tk.Button(btn_frame, text="",
                            font=("Helvetica", 9, "bold"),
                            relief="flat", bd=0, padx=14, pady=4,
                            cursor="hand2", command=_toggle)
            btn.pack()
            _refresh_btn()

        # ── General ───────────────────────────────────────────────────────────
        _section("General")
        _toggle_row(
            "Auto-login",
            "Skip the profile screen and load the last used profile on startup.",
            "auto_login",
        )
        _toggle_row(
            "Start maximized",
            "Open the window fullscreen every time.",
            "start_maximized",
        )

        # ── Coming soon ───────────────────────────────────────────────────────
        _section("Appearance  (coming soon)")
        _toggle_row("Dark mode",    "Switch to a dark colour theme.",        "theme",  enabled=False)
        _toggle_row("Sound effects","Play sounds on correct/wrong answers.", "sound",  enabled=False)

        _section("Language  (coming soon)")
        _toggle_row("Norsk / English", "Switch the interface language.",     "lang",   enabled=False)

        # Close
        tk.Button(win, text="Done", command=win.destroy,
                  font=("Helvetica", 11, "bold"),
                  bg="#0f172a", fg="white", relief="flat", bd=0,
                  padx=24, pady=8, cursor="hand2",
                  activebackground="#1e293b", activeforeground="white").pack(pady=12)

    # ------------------------------------------------------------------- menu

    def show_menu(self):
        self._clear()
        self._current_family = None

        outer = tk.Frame(self.root, bg="#f8fafc")
        outer.pack(fill=tk.BOTH, expand=True)
        self._current = outer

        vsb = ttk.Scrollbar(outer, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        canvas = tk.Canvas(outer, bg="#f8fafc", highlightthickness=0,
                           yscrollcommand=vsb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=canvas.yview)

        inner = tk.Frame(canvas, bg="#f8fafc")
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win_id, width=e.width))

        self._scroll_target = canvas
        # Reclaim the root mousewheel binding from whichever subscreen we
        # just returned from; otherwise scrolling only works over the
        # scrollbar itself.
        self._install_wheel_handler()

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(inner, bg="#f8fafc", padx=48, pady=32)
        hdr.pack(fill=tk.X)

        # Left: title + profile
        title_col = tk.Frame(hdr, bg="#f8fafc")
        title_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(title_col, text="Math Practice",
                 font=("Helvetica", 32, "bold"),
                 bg="#f8fafc", fg="#0f172a").pack(anchor="w")
        tk.Label(title_col, text="Choose a game to start practising.",
                 font=("Helvetica", 13), bg="#f8fafc", fg="#475569").pack(anchor="w", pady=(4, 0))

        # Profile pill + switch button
        profile_row = tk.Frame(title_col, bg="#f8fafc")
        profile_row.pack(anchor="w", pady=(8, 0))
        tk.Label(profile_row, text=f"👤  {self._profile_name}",
                 font=("Helvetica", 10, "bold"),
                 bg="#e2e8f0", fg="#475569",
                 padx=10, pady=4).pack(side=tk.LEFT)
        tk.Button(profile_row, text="Switch profile",
                  font=("Helvetica", 9), bg="#f8fafc", fg="#94a3b8",
                  relief="flat", bd=0, padx=8, cursor="hand2",
                  activebackground="#f8fafc", activeforeground="#475569",
                  command=self.show_profiles).pack(side=tk.LEFT, padx=(8, 0))
        tk.Button(profile_row, text="⚙",
                  font=("Helvetica", 10), bg="#f8fafc", fg="#94a3b8",
                  relief="flat", bd=0, padx=6, cursor="hand2",
                  activebackground="#f8fafc", activeforeground="#475569",
                  command=self._show_settings).pack(side=tk.LEFT, padx=(4, 0))

        # Right: points + achievements button
        right_col = tk.Frame(hdr, bg="#f8fafc")
        right_col.pack(side=tk.RIGHT, anchor="ne")

        pts          = self._ach_store.get_points()
        earned_count = len(self._ach_store.get_earned())
        total_count  = len(ACHIEVEMENTS)
        tk.Label(right_col,
                 text=f"⭐ {pts:,} pts",
                 font=("Helvetica", 14, "bold"),
                 bg="#f8fafc", fg="#f59e0b").pack(anchor="e")
        tk.Label(right_col,
                 text=f"{earned_count} / {total_count} achievements",
                 font=("Helvetica", 9), bg="#f8fafc", fg="#94a3b8").pack(anchor="e", pady=(2, 8))
        tk.Button(right_col, text="🏆  Trophy Room",
                  font=("Helvetica", 10, "bold"),
                  bg="#0f172a", fg="white", relief="flat", bd=0,
                  padx=14, pady=7, cursor="hand2",
                  activebackground="#1e293b", activeforeground="white",
                  command=self._show_achievements).pack(anchor="e")

        # ── Game family row (4 tiles) ────────────────────────────────────────
        # One tile per family. Click → show_difficulty(family). Compact
        # by design — 12 game cards collapse to 4 here. Any future
        # families plug in by appending an entry to GAMES.
        self._tile_images = []   # release prior refs; renderer repopulates

        family_section = tk.Frame(inner, bg="#f8fafc", padx=48)
        family_section.pack(fill=tk.X, pady=(0, 28))

        tk.Label(family_section, text="GAMES",
                 font=("Helvetica", 13, "bold"),
                 bg="#f8fafc", fg="#94a3b8").pack(anchor="w", pady=(0, 12))

        family_grid = tk.Frame(family_section, bg="#f8fafc")
        family_grid.pack(fill=tk.X)
        for col in range(len(GAMES)):
            family_grid.columnconfigure(col, weight=1)
        for col, family in enumerate(GAMES):
            padx = (0, 14) if col < len(GAMES) - 1 else 0
            self._family_tile(family_grid, family, col, padx)

        # ── Tools row (4 tiles): Practice / Stats / Tutorials / Shop ────────
        self._tools_row(inner)

        # ── Footer ────────────────────────────────────────────────────────────
        tk.Frame(inner, bg="#e2e8f0", height=1).pack(fill=tk.X, padx=48, pady=(24, 0))
        tk.Label(inner,
                 text=f"Math Practice  v{__version__}  ·  © 2026 Aleksander Lie",
                 font=("Helvetica", 8), bg="#f8fafc", fg="#cbd5e1").pack(pady=(6, 24))

    # ============================================================ family tiles

    def _family_tile(self, parent, family, col, padx):
        """Render a single game-family card on the main menu.

        Compact tile — glyph + label + tagline + a row of three small
        status pills (one per difficulty). Clicking anywhere on the tile
        opens the difficulty-selection page for the family.
        """
        card = tk.Frame(parent, bg="white",
                        highlightbackground="#e2e8f0", highlightthickness=1,
                        cursor="hand2")
        card.grid(row=0, column=col, sticky="nsew", padx=padx)

        inner = tk.Frame(card, bg="white", padx=20, pady=20)
        inner.pack(fill=tk.BOTH, expand=True)

        # Top: family glyph in a colored disc + "Game" pill on the right.
        top = tk.Frame(inner, bg="white")
        top.pack(fill=tk.X, pady=(0, 12))

        glyph_box = tk.Frame(top, bg=family["accent"], padx=12, pady=4)
        glyph_box.pack(side=tk.LEFT)
        tk.Label(glyph_box, text=family["glyph"],
                 font=("Helvetica", 22, "bold"),
                 bg=family["accent"], fg="white").pack()

        tk.Label(top, text="Game",
                 font=("Helvetica", 8, "bold"),
                 bg="#eef2ff", fg="#4f46e5",
                 padx=8, pady=2).pack(side=tk.RIGHT)

        # Family label + tagline
        tk.Label(inner, text=family["label"],
                 font=("Helvetica", 14, "bold"),
                 bg="white", fg="#0f172a",
                 wraplength=220, justify="left", anchor="w").pack(fill=tk.X)
        tk.Label(inner, text=family["tagline"],
                 font=("Helvetica", 9), bg="white", fg="#64748b",
                 wraplength=220, justify="left", anchor="w").pack(fill=tk.X,
                                                                   pady=(4, 14))

        # Difficulty status pills — one per difficulty, in tier order.
        # State: "open", "locked", or "sharp" (sharp_<gid> achievement
        # earned). Surfaces progression at a glance without making the
        # user click into the family.
        status_row = tk.Frame(inner, bg="white")
        status_row.pack(fill=tk.X, pady=(0, 10))
        for tier in _DIFFICULTY_TIERS:
            diff = next((d for d in family["difficulties"]
                         if d["key"] == tier["key"]), None)
            if not diff:
                continue
            gid    = diff["game_id"]
            unlock = UNLOCK_REQUIREMENTS.get(gid)
            locked = bool(unlock and not self._ach_store.has(unlock))
            sharp  = self._ach_store.has(f"sharp_{gid}")
            if sharp:
                pill_bg, pill_fg, pill_txt = "#f0fdf4", "#15803d", f"✓ {tier['label'][:3]}"
            elif locked:
                pill_bg, pill_fg, pill_txt = "#f1f5f9", "#94a3b8", f"🔒 {tier['label'][:3]}"
            else:
                pill_bg, pill_fg, pill_txt = "#eef2ff", "#4f46e5", tier['label'][:3]
            tk.Label(status_row, text=pill_txt,
                     font=("Helvetica", 8, "bold"),
                     bg=pill_bg, fg=pill_fg,
                     padx=7, pady=2).pack(side=tk.LEFT, padx=(0, 4))

        tk.Button(
            inner, text="Choose difficulty  →",
            font=("Helvetica", 10, "bold"),
            bg=family["accent"], fg="white",
            relief="flat", bd=0, padx=12, pady=6, cursor="hand2",
            activebackground="#1e293b", activeforeground="white",
            command=lambda f=family: self.show_difficulty(f),
        ).pack(anchor="w")

        # Make the entire tile clickable, not just the button.
        def _open(e=None, f=family):
            self.show_difficulty(f)
        for w in (card, inner, top):
            w.bind("<Button-1>", _open)

    # ============================================================ tools row

    def _tools_row(self, parent):
        """Bottom-of-menu tools strip. Four tiles in a row.

        Layout was widened from 3 → 4 in v0.7.12 to make room for the
        Shop placeholder (locked, ships in v0.8.0). Order is: Practice
        Missed, Progress & Stats, Tutorials, Shop.
        """
        section = tk.Frame(parent, bg="#f8fafc", padx=48)
        section.pack(fill=tk.X, pady=(0, 28))

        tk.Label(section, text="TOOLS",
                 font=("Helvetica", 13, "bold"),
                 bg="#f8fafc", fg="#94a3b8").pack(anchor="w", pady=(0, 12))

        cards = tk.Frame(section, bg="#f8fafc")
        cards.pack(fill=tk.X)
        for col in range(4):
            cards.columnconfigure(col, weight=1)

        # ── Practice Missed card ─────────────────────────────────────────
        count   = self._missed_store.count()
        enabled = count > 0

        card_bg = "white"   if enabled else "#f1f5f9"
        name_fg = "#0f172a" if enabled else "#94a3b8"
        desc_fg = "#64748b" if enabled else "#94a3b8"
        desc    = (f"{count} question{'s' if count != 1 else ''} waiting for review."
                   if enabled else "No missed questions yet — keep playing!")

        card = tk.Frame(cards, bg=card_bg,
                        highlightbackground="#e2e8f0", highlightthickness=1,
                        cursor="hand2" if enabled else "arrow")
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        inner = tk.Frame(card, bg=card_bg, padx=20, pady=20)
        inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(inner, text="Review",
                 font=("Helvetica", 9, "bold"),
                 bg="#f0f4ff", fg="#4f46e5",
                 padx=10, pady=3).pack(anchor="w", pady=(0, 12))
        tk.Label(inner, text="Practice Missed",
                 font=("Helvetica", 14, "bold"),
                 bg=card_bg, fg=name_fg).pack(anchor="w")
        tk.Label(inner, text=desc,
                 font=("Helvetica", 9), bg=card_bg, fg=desc_fg,
                 justify="left", wraplength=200).pack(anchor="w", pady=(6, 14))

        play_btn = tk.Button(
            inner, text="Start  →",
            font=("Helvetica", 10, "bold"),
            bg="#4f46e5" if enabled else "#e2e8f0",
            fg="white"   if enabled else "#94a3b8",
            relief="flat", bd=0, padx=12, pady=5,
            cursor="hand2" if enabled else "arrow",
            state="normal" if enabled else "disabled",
            command=self._launch_practice if enabled else None,
        )
        play_btn.pack(anchor="w")

        if enabled:
            for w in (card, inner):
                w.bind("<Button-1>", lambda e: self._launch_practice())

        # ── Progress & Stats card ────────────────────────────────────────
        sess_count = self._sessions_store.count() if self._sessions_store else 0
        days       = len(self._ach_store.get_stats().get("days_played", []))

        if sess_count > 0:
            stats_desc = (f"{sess_count} session{'s' if sess_count != 1 else ''}"
                          f" across {days} day{'s' if days != 1 else ''}.")
        else:
            stats_desc = "Charts, trends, parent PDF."

        stats_card = tk.Frame(cards, bg="white",
                              highlightbackground="#e2e8f0", highlightthickness=1,
                              cursor="hand2")
        stats_card.grid(row=0, column=1, sticky="nsew", padx=(0, 14))

        stats_inner = tk.Frame(stats_card, bg="white", padx=20, pady=20)
        stats_inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(stats_inner, text="Insights",
                 font=("Helvetica", 9, "bold"),
                 bg="#ecfdf5", fg="#047857",
                 padx=10, pady=3).pack(anchor="w", pady=(0, 12))
        tk.Label(stats_inner, text="Progress & Stats",
                 font=("Helvetica", 14, "bold"),
                 bg="white", fg="#0f172a").pack(anchor="w")
        tk.Label(stats_inner, text=stats_desc,
                 font=("Helvetica", 9), bg="white", fg="#64748b",
                 justify="left", wraplength=200).pack(anchor="w", pady=(6, 14))

        tk.Button(
            stats_inner, text="Open  →",
            font=("Helvetica", 10, "bold"),
            bg="#047857", fg="white",
            relief="flat", bd=0, padx=12, pady=5, cursor="hand2",
            activebackground="#065f46", activeforeground="white",
            command=self._launch_stats,
        ).pack(anchor="w")

        for w in (stats_card, stats_inner):
            w.bind("<Button-1>", lambda e: self._launch_stats())

        # ── Tutorials card ───────────────────────────────────────────────
        # Count tutorials unlocked for the active profile so the subtitle
        # tells the user how many guides are currently available.
        from games.achievements import UNLOCK_REQUIREMENTS as _UR
        unlocked = sum(
            1 for gid in TUTORIAL_REGISTRY
            if not (_UR.get(gid) and not self._ach_store.has(_UR[gid]))
        )
        total = len(TUTORIAL_REGISTRY)
        tut_desc = (f"{unlocked}/{total} guide{'s' if total != 1 else ''} "
                    f"unlocked.\nStep-by-step walkthroughs.")

        tut_card = tk.Frame(cards, bg="white",
                            highlightbackground="#e2e8f0", highlightthickness=1,
                            cursor="hand2")
        tut_card.grid(row=0, column=2, sticky="nsew", padx=(0, 14))

        tut_inner = tk.Frame(tut_card, bg="white", padx=20, pady=20)
        tut_inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(tut_inner, text="Learn",
                 font=("Helvetica", 9, "bold"),
                 bg="#eef2ff", fg="#4f46e5",
                 padx=10, pady=3).pack(anchor="w", pady=(0, 12))
        tk.Label(tut_inner, text="Tutorials",
                 font=("Helvetica", 14, "bold"),
                 bg="white", fg="#0f172a").pack(anchor="w")
        tk.Label(tut_inner, text=tut_desc,
                 font=("Helvetica", 9), bg="white", fg="#64748b",
                 justify="left", wraplength=200).pack(anchor="w", pady=(6, 14))

        tk.Button(
            tut_inner, text="Open  →",
            font=("Helvetica", 10, "bold"),
            bg="#4f46e5", fg="white",
            relief="flat", bd=0, padx=12, pady=5, cursor="hand2",
            activebackground="#4338ca", activeforeground="white",
            command=self._launch_tutorials,
        ).pack(anchor="w")

        for w in (tut_card, tut_inner):
            w.bind("<Button-1>", lambda e: self._launch_tutorials())

        # ── Shop card (locked placeholder, ships v0.8.0) ─────────────────
        # Reserved for the achievement-points spending loop: themes
        # (dark mode), avatars, frames. Click → messagebox describing
        # planned content. Architecture note: the tile is a regular
        # Tools-row entry, not a special case — when v0.8.0 wires it up
        # we just flip `enabled` and replace `_show_shop` with a real
        # launcher.
        self._shop_tile(cards)

    def _shop_tile(self, parent):
        """Locked Shop tile in the Tools row. Placeholder for v0.8.0."""
        card = tk.Frame(parent, bg="#f1f5f9",
                        highlightbackground="#e2e8f0", highlightthickness=1,
                        cursor="hand2")
        card.grid(row=0, column=3, sticky="nsew")

        inner = tk.Frame(card, bg="#f1f5f9", padx=20, pady=20)
        inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(inner, text="Coming v0.8.0",
                 font=("Helvetica", 9, "bold"),
                 bg="#faf5ff", fg="#9333ea",
                 padx=10, pady=3).pack(anchor="w", pady=(0, 12))
        tk.Label(inner, text="🛍  Shop",
                 font=("Helvetica", 14, "bold"),
                 bg="#f1f5f9", fg="#475569").pack(anchor="w")
        tk.Label(inner,
                 text="Spend points on themes, avatars, and frames.",
                 font=("Helvetica", 9), bg="#f1f5f9", fg="#94a3b8",
                 justify="left", wraplength=200).pack(anchor="w", pady=(6, 14))

        tk.Button(
            inner, text="🔒 Locked",
            font=("Helvetica", 10, "bold"),
            bg="#e2e8f0", fg="#94a3b8",
            relief="flat", bd=0, padx=12, pady=5, cursor="hand2",
            activebackground="#cbd5e1", activeforeground="#475569",
            command=self._show_shop,
        ).pack(anchor="w")

        for w in (card, inner):
            w.bind("<Button-1>", lambda e: self._show_shop())

    def _show_shop(self):
        """Placeholder Shop entry. Replace with a real launcher in v0.8.0."""
        messagebox.showinfo(
            "Shop — coming in v0.8.0",
            "The Shop will let you spend achievement points on:\n\n"
            "  • Color themes  (Dark mode is the priority unlock)\n"
            "  • Avatar portraits  (fantasy classes — knight, wizard, ...)\n"
            "  • Avatar border frames\n\n"
            "Keep earning points — they'll have somewhere to go soon.",
        )

    # ============================================================ difficulty page

    def show_difficulty(self, family):
        """Render the difficulty-selection screen for a game family.

        Three cards in a row, one per difficulty. Cards locked behind
        UNLOCK_REQUIREMENTS show a clear unlock hint instead of the
        play button. Back returns to the main menu.

        Per-difficulty artwork is loaded from
        `assets/games/<family_id>/<difficulty>.png` if present, otherwise
        the renderer falls back to the tier emoji glyph (🌱 / 🔥 / ⚡).
        Adding art later is a zero-code drop-in.
        """
        self._clear()
        self._current_family = family
        self._tile_images    = []   # release prior refs

        outer = tk.Frame(self.root, bg="#f8fafc")
        outer.pack(fill=tk.BOTH, expand=True)
        self._current = outer

        # Top bar — back button only
        top = tk.Frame(outer, bg="#f8fafc", padx=24, pady=10)
        top.pack(fill=tk.X)
        tk.Button(top, text="← Menu",
                  font=("Helvetica", 10), bg="#f8fafc", fg="#475569",
                  relief="flat", bd=0, cursor="hand2",
                  activebackground="#f8fafc", activeforeground="#0f172a",
                  command=self.show_menu).pack(side=tk.LEFT)

        # Header — family glyph + label + tagline
        hdr = tk.Frame(outer, bg="#f8fafc", padx=48, pady=18)
        hdr.pack(fill=tk.X)

        glyph_box = tk.Frame(hdr, bg=family["accent"], padx=14, pady=8)
        glyph_box.pack(side=tk.LEFT)
        tk.Label(glyph_box, text=family["glyph"],
                 font=("Helvetica", 28, "bold"),
                 bg=family["accent"], fg="white").pack()

        title_col = tk.Frame(hdr, bg="#f8fafc")
        title_col.pack(side=tk.LEFT, padx=(16, 0), fill=tk.X, expand=True)
        tk.Label(title_col, text=family["label"],
                 font=("Helvetica", 26, "bold"),
                 bg="#f8fafc", fg="#0f172a").pack(anchor="w")
        tk.Label(title_col, text=family["tagline"],
                 font=("Helvetica", 11),
                 bg="#f8fafc", fg="#64748b").pack(anchor="w", pady=(4, 0))
        tk.Label(title_col, text="Choose a difficulty.",
                 font=("Helvetica", 11, "bold"),
                 bg="#f8fafc", fg="#475569").pack(anchor="w", pady=(8, 0))

        # 3-column difficulty grid
        cards_wrap = tk.Frame(outer, bg="#f8fafc", padx=48, pady=20)
        cards_wrap.pack(fill=tk.BOTH, expand=True)

        cards = tk.Frame(cards_wrap, bg="#f8fafc")
        cards.pack(fill=tk.BOTH, expand=True)
        for col in range(3):
            cards.columnconfigure(col, weight=1)
        cards.rowconfigure(0, weight=1)

        for col, diff in enumerate(family["difficulties"]):
            padx   = (0, 16) if col < len(family["difficulties"]) - 1 else 0
            unlock = UNLOCK_REQUIREMENTS.get(diff["game_id"])
            locked = bool(unlock and not self._ach_store.has(unlock))
            self._difficulty_tile(cards, family, diff, col, padx,
                                  locked=locked, unlock_req=unlock)

    def _difficulty_tile(self, parent, family, diff, col, padx,
                         locked=False, unlock_req=None):
        """One card on the difficulty-selection screen.

        Card structure (top→bottom):
          1. Asset slot — PNG from assets/games/<fam>/<diff>.png if it
             exists, else a large tier glyph (🌱 / 🔥 / ⚡).
          2. Difficulty badge (Beginner / Intermediate / Advanced).
          3. Difficulty name.
          4. Description.
          5. Play button (or locked-unlock hint).
        """
        # Tier metadata (badge colours match the existing per-difficulty palette).
        tier = next((t for t in _DIFFICULTY_TIERS if t["key"] == diff["key"]), _DIFFICULTY_TIERS[0])
        T    = theme()
        badge_bg = T[tier["badge_bg_token"]]
        badge_fg = T[tier["badge_fg_token"]]

        bg     = "white"   if not locked else "#f8fafc"
        ink_fg = "#0f172a" if not locked else "#94a3b8"
        sub_fg = "#64748b" if not locked else "#94a3b8"

        card = tk.Frame(parent, bg=bg,
                        highlightbackground="#e2e8f0", highlightthickness=1,
                        cursor="hand2")
        card.grid(row=0, column=col, sticky="nsew", padx=padx)

        # Asset slot — fixed 200×120 box, centered glyph or PNG.
        asset_slot = tk.Frame(card, bg=bg, height=140)
        asset_slot.pack(fill=tk.X)
        asset_slot.pack_propagate(False)

        img = game_tile_image(family["id"], diff["key"])
        if img is not None:
            self._tile_images.append(img)   # keep ref alive
            tk.Label(asset_slot, image=img, bg=bg).pack(expand=True)
        else:
            # Fallback: large emoji tier glyph centered on the slot.
            tk.Label(asset_slot, text=tier_glyph(diff["key"]),
                     font=("Helvetica", 56),
                     bg=bg, fg=ink_fg if not locked else "#cbd5e1").pack(expand=True)

        # 1px divider between asset and body
        tk.Frame(card, bg="#e2e8f0", height=1).pack(fill=tk.X)

        inner = tk.Frame(card, bg=bg, padx=20, pady=18)
        inner.pack(fill=tk.BOTH, expand=True)

        badge_row = tk.Frame(inner, bg=bg)
        badge_row.pack(anchor="w", pady=(0, 10))
        tk.Label(badge_row, text=tier["label"],
                 font=("Helvetica", 9, "bold"),
                 bg=badge_bg if not locked else "#e2e8f0",
                 fg=badge_fg if not locked else "#94a3b8",
                 padx=10, pady=3).pack(side=tk.LEFT)
        if locked:
            tk.Label(badge_row, text="  🔒 Locked",
                     font=("Helvetica", 9, "bold"),
                     bg=bg, fg="#94a3b8").pack(side=tk.LEFT)

        tk.Label(inner, text=diff["name"],
                 font=("Helvetica", 15, "bold"),
                 bg=bg, fg=ink_fg).pack(anchor="w")
        tk.Label(inner, text=diff["desc"],
                 font=("Helvetica", 10), bg=bg, fg=sub_fg,
                 justify="left").pack(anchor="w", pady=(6, 14))

        if locked:
            self._render_lock_hint(inner, unlock_req)
            return

        tk.Button(
            inner, text="Play  →",
            font=("Helvetica", 10, "bold"),
            bg="#0f172a", fg="white", relief="flat", bd=0,
            padx=14, pady=6, cursor="hand2",
            activebackground="#1e293b", activeforeground="white",
            command=lambda f=family, d=diff: self._launch(f, d),
        ).pack(anchor="w")

        for w in (card, asset_slot, inner):
            w.bind("<Button-1>",
                   lambda e, f=family, d=diff: self._launch(f, d))

    def _render_lock_hint(self, parent, unlock_req):
        """Render the unlock-hint block inside a locked difficulty card."""
        req_name = req_desc = req_game = ""
        if unlock_req:
            ach = ACHIEVEMENTS_BY_ID.get(unlock_req)
            if ach:
                req_name = ach["name"]
                req_desc = ach["desc"]
                req_game = GAME_NAMES.get(ach.get("game_id", ""), "")

        unlock_label = (f"Unlock: '{req_name}' in {req_game}"
                        if req_game else f"Unlock: '{req_name}' achievement")

        unlock_frame = tk.Frame(parent, bg="#e2e8f0",
                                highlightbackground="#cbd5e1", highlightthickness=1)
        unlock_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(unlock_frame, text=unlock_label,
                 font=("Helvetica", 9), bg="#e2e8f0", fg="#64748b",
                 padx=10, pady=6, wraplength=220, justify="left").pack(anchor="w")

        def _show_lock_info(e=None):
            messagebox.showinfo(
                "Locked",
                f"This level is locked.\n\n"
                f"Earn the '{req_name}' achievement in {req_game} to unlock it:\n\n"
                f"{req_desc}",
            )
        # Bind on the unlock_frame itself; the parent card binds in caller.
        for w in (unlock_frame,) + tuple(unlock_frame.winfo_children()):
            w.bind("<Button-1>", _show_lock_info)

    # ------------------------------------------------------------ achievements

    def _show_achievements(self):
        """Open the Trophy Room window."""
        root = self.root
        root.update_idletasks()
        cx = root.winfo_x() + root.winfo_width()  // 2
        cy = root.winfo_y() + root.winfo_height() // 2

        win = tk.Toplevel(root)
        win.title("Trophy Room")
        win.configure(bg="#f8fafc")
        win.geometry(f"640x580+{cx - 320}+{cy - 290}")
        win.resizable(True, True)

        hdr = tk.Frame(win, bg="#0f172a", padx=24, pady=16)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="🏆  Trophy Room",
                 font=("Helvetica", 16, "bold"),
                 bg="#0f172a", fg="white").pack(side=tk.LEFT)

        pts          = self._ach_store.get_points()
        earned_count = len(self._ach_store.get_earned())
        total_count  = len(ACHIEVEMENTS)
        tk.Label(hdr, text=f"⭐ {pts:,} pts  ·  {earned_count}/{total_count}",
                 font=("Helvetica", 11), bg="#0f172a", fg="#f59e0b").pack(side=tk.RIGHT)

        body_outer = tk.Frame(win, bg="#f8fafc")
        body_outer.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(body_outer, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        txt = tk.Text(
            body_outer, bg="#f8fafc", relief="flat", bd=0,
            cursor="arrow", wrap="word", font=("Helvetica", 11),
            yscrollcommand=vsb.set, highlightthickness=0, state="normal",
        )
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=txt.yview)

        prev_target         = self._scroll_target
        self._scroll_target = txt

        def _on_trophy_close():
            self._scroll_target = prev_target
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", _on_trophy_close)

        # Text tags
        txt.tag_configure("cat",
                          font=("Helvetica", 10, "bold"), foreground="#94a3b8",
                          spacing1=14, spacing3=4, lmargin1=24, lmargin2=24)
        txt.tag_configure("divider",
                          font=("Helvetica", 1), foreground="#e2e8f0",
                          background="#e2e8f0", spacing3=6)
        txt.tag_configure("subcat",
                          font=("Helvetica", 9, "bold"), foreground="#64748b",
                          spacing1=8, spacing3=2, lmargin1=40, lmargin2=40)
        for suffix, fg, bg in [
            ("earned",        "#0f172a", "#f0fdf4"),
            ("locked",        "#94a3b8", "#f8fafc"),
            ("earned_indent", "#0f172a", "#f0fdf4"),
            ("locked_indent", "#94a3b8", "#f8fafc"),
        ]:
            bold   = "bold" if "earned" in suffix else "normal"
            indent = 44 if "indent" in suffix else 28
            txt.tag_configure(f"name_{suffix}",
                              font=("Helvetica", 11, bold), foreground=fg,
                              background=bg, spacing1=6,
                              lmargin1=indent, lmargin2=indent)
            txt.tag_configure(f"desc_{suffix}",
                              font=("Helvetica", 9),
                              foreground="#64748b" if "earned" in suffix else "#cbd5e1",
                              background=bg, spacing3=6,
                              lmargin1=indent, lmargin2=indent)

        earned_set = set(self._ach_store.get_earned())
        cat_map    = {c: [] for c in CATEGORY_ORDER}
        for ach in ACHIEVEMENTS:
            cat_map.setdefault(ach.get("category", "Other"), []).append(ach)

        from collections import defaultdict

        def _insert_ach(a, indent=False):
            earned = a["id"] in earned_set
            hidden = a.get("hidden", False) and not earned
            icon   = a["icon"] if not hidden else "❓"
            name   = a["name"] if not hidden else "???"
            desc   = a["desc"] if not hidden else "Keep playing to discover this one."
            pts_s  = f"+{a['points']} pts"
            check  = "  ✓" if earned else ""
            sfx    = ("earned" if earned else "locked") + ("_indent" if indent else "")
            txt.insert(tk.END, f"{icon}  {name}  {pts_s}{check}\n", f"name_{sfx}")
            txt.insert(tk.END, f"{desc}\n", f"desc_{sfx}")

        for cat in CATEGORY_ORDER:
            achs_in_cat = cat_map.get(cat, [])
            if not achs_in_cat:
                continue
            txt.insert(tk.END, f"\n{cat.upper()}\n", "cat")
            txt.insert(tk.END, " " * 80 + "\n", "divider")
            if cat == "Game Mastery":
                by_game = defaultdict(list)
                for a in achs_in_cat:
                    by_game[a.get("game_id", "")].append(a)
                for gid in GAME_IDS:
                    game_achs = by_game.get(gid, [])
                    if not game_achs:
                        continue
                    txt.insert(tk.END, f"{GAME_NAMES[gid]}\n", "subcat")
                    for a in game_achs:
                        _insert_ach(a, indent=True)
            else:
                for a in achs_in_cat:
                    _insert_ach(a)

        txt.insert(tk.END, "\n")
        txt.configure(state="disabled")

        tk.Button(win, text="Close", command=_on_trophy_close,
                  font=("Helvetica", 11), bg="white", fg="#475569",
                  relief="solid", bd=1, padx=20, pady=6, cursor="hand2").pack(pady=10)

    # ----------------------------------------------------------------- launch

    def _launch(self, family, difficulty):
        """Launch a game.

        Back button on the game returns to the difficulty-selection
        screen for the same family (not all the way to the main menu) —
        the pupil typically wants to try a sibling difficulty next, and
        a single extra back-press still gets them to the menu.
        """
        self._clear()
        frame = tk.Frame(self.root, bg="#f8fafc")
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
        self._clear()
        frame = tk.Frame(self.root, bg="#f8fafc")
        frame.pack(fill=tk.BOTH, expand=True)
        self._current = frame
        PracticeMissed(frame,
                       back_callback=self.show_menu,
                       ach_store=self._ach_store,
                       missed_store=self._missed_store,
                       scores_store=self._scores_store,
                       sessions_store=self._sessions_store)

    def _launch_stats(self):
        self._clear()
        frame = tk.Frame(self.root, bg="#f8fafc")
        frame.pack(fill=tk.BOTH, expand=True)
        self._current = frame
        StatsScreen(frame,
                    back_callback=self.show_menu,
                    profile_name=self._profile_name,
                    ach_store=self._ach_store,
                    sessions_store=self._sessions_store,
                    scores_store=self._scores_store)

    def _launch_tutorials(self):
        self._clear()
        frame = tk.Frame(self.root, bg="#f8fafc")
        frame.pack(fill=tk.BOTH, expand=True)
        self._current = frame
        TutorialsPanel(frame,
                       back_callback=self.show_menu,
                       ach_store=self._ach_store)

    def _clear(self):
        self._scroll_target = None
        if self._current is not None:
            self._current.destroy()
            self._current = None

    def _install_wheel_handler(self):
        """Install (or re-install) the root-level mousewheel handler.

        Called from __init__ and from show_menu() so the menu reclaims the
        <MouseWheel> binding after returning from a subscreen whose own
        bind_all call overrode ours.
        """
        def _wheel(e):
            t = self._scroll_target
            if t:
                try:
                    t.yview_scroll(int(-1 * (e.delta / 120)), "units")
                except Exception:
                    pass
        self.root.bind_all("<MouseWheel>", _wheel)
        self.root.bind_all("<Button-4>",
                           lambda e: self._scroll_target and
                           self._scroll_target.yview_scroll(-1, "units"))
        self.root.bind_all("<Button-5>",
                           lambda e: self._scroll_target and
                           self._scroll_target.yview_scroll(1, "units"))


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.title(f"Math Practice  v{__version__}")
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
