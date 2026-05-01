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

__version__ = "0.8.0.1"

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


# ── Shop catalogue ─────────────────────────────────────────────────────────────
#
# Items the pupil can buy with achievement points. v0.7.13 ships a single
# item — Dark Mode. Future avatar packs / border frames append entries
# here; the shop modal renders one card per item and gates each behind
# `purchases_store.has(id)`.
#
# Each entry:
#   id        — stable string key, persisted in purchases.json
#   name      — display name in the shop card
#   category  — group label (Theme / Avatar / Frame …)
#   icon      — single emoji for the card hero glyph
#   desc      — 1–2 sentence pitch
#   price     — cost in achievement points
#   on_buy    — optional callable(app) invoked AFTER `purchase()` succeeds.
#               Use this for side effects (e.g. Dark Mode flips the
#               settings 'theme' default to "dark" so the toggle starts
#               on, but the user is free to flip it off in Settings).

SHOP_ITEMS = [
    {
        "id":       "dark_mode",
        "name":     "Dark Mode",
        "category": "Theme",
        "icon":     "🌙",
        "desc":     ("A clean dark colour theme. Activate from "
                     "Settings → Appearance once purchased."),
        "price":    500,
        "on_buy":   None,
    },
    {
        "id":       "matrix_mode",
        "name":     "Matrix Mode",
        "category": "Theme",
        "icon":     "🟢",
        "desc":     ("Green-on-black phosphor like the Matrix movie. "
                     "Digits glow. Activate from Settings → Appearance."),
        "price":    1000,
        # v0.7.13.2: Matrix has a *prerequisite achievement* on top of
        # the price. Hides the item behind real progress so it feels
        # earned, not just bought. The achievement chosen — Sharp on
        # Multiplication: Intermediate — is the same one that unlocks
        # Multiplication: Advanced, so "Matrix unlocks once Mult
        # Advanced is open" lines up with curriculum progression.
        "unlock_req": "sharp_mult_intermediate",
        "on_buy":     None,
    },
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
        self.root.geometry("1180x920")
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
        """Landing screen — choose or create a profile."""
        T = theme()
        self._clear()
        self._profile_name = None
        self._ach_store = self._missed_store = self._scores_store = None
        self._sessions_store = None
        self._purchases_store = None

        outer = tk.Frame(self.root, bg=T["bg"])
        outer.pack(fill=tk.BOTH, expand=True)
        self._current = outer

        # ── Centred card ──────────────────────────────────────────────────────
        wrapper = tk.Frame(outer, bg=T["bg"])
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(wrapper, text="Math Practice",
                 font=("Helvetica", 30, "bold"),
                 bg=T["bg"], fg=T["ink"]).pack(pady=(0, 4))
        tk.Label(wrapper, text="Who is playing?",
                 font=("Helvetica", 13), bg=T["bg"], fg=T["muted"]).pack(pady=(0, 28))

        profiles = list_profiles()

        if profiles:
            profiles_frame = tk.Frame(wrapper, bg=T["bg"])
            profiles_frame.pack(pady=(0, 20))

            for name in profiles:
                self._profile_card(profiles_frame, name)

        # ── Divider ───────────────────────────────────────────────────────────
        if profiles:
            div_row = tk.Frame(wrapper, bg=T["bg"])
            div_row.pack(fill=tk.X, pady=(4, 16))
            tk.Frame(div_row, bg=T["card_border"], height=1).pack(
                side=tk.LEFT, fill=tk.X, expand=True, pady=8)
            tk.Label(div_row, text="  or  ", font=("Helvetica", 9),
                     bg=T["bg"], fg=T["dim"]).pack(side=tk.LEFT)
            tk.Frame(div_row, bg=T["card_border"], height=1).pack(
                side=tk.LEFT, fill=tk.X, expand=True, pady=8)

        # ── New profile entry ─────────────────────────────────────────────────
        new_frame = tk.Frame(wrapper, bg=T["bg"])
        new_frame.pack()

        tk.Label(new_frame,
                 text="Create new profile" if profiles else "Enter your name to start:",
                 font=("Helvetica", 10, "bold"), bg=T["bg"], fg=T["ink"]).pack(anchor="w")

        entry_row = tk.Frame(new_frame, bg=T["bg"])
        entry_row.pack(fill=tk.X, pady=(6, 0))

        name_var = tk.StringVar()
        name_entry = tk.Entry(entry_row, textvariable=name_var,
                              font=("Helvetica", 13), relief="solid", bd=1,
                              fg=T["ink"], width=20)
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
                  bg=T["btn_primary_bg"], fg=T["btn_primary_fg"], relief="flat", bd=0,
                  padx=14, pady=6, cursor="hand2",
                  activebackground="#1e293b", activeforeground="white",
                  command=_create).pack(side=tk.LEFT)

        # ── Footer ────────────────────────────────────────────────────────────
        footer = tk.Frame(outer, bg=T["bg"])
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=8)
        tk.Label(footer,
                 text=f"Math Practice  v{__version__}  ·  © 2026 Aleksander Lie",
                 font=("Helvetica", 8), bg=T["bg"], fg=T["faint"]).pack(side=tk.LEFT, padx=16)
        tk.Button(footer, text="⚙  Settings",
                  font=("Helvetica", 9), bg=T["bg"], fg=T["dim"],
                  relief="flat", bd=0, padx=8, cursor="hand2",
                  activebackground="#f8fafc", activeforeground="#475569",
                  command=self._show_settings).pack(side=tk.RIGHT, padx=16)

    def _profile_card(self, parent, name):
        """A clickable card for an existing profile with a delete button."""
        T = theme()
        card = tk.Frame(parent, bg=T["card_bg"],
                        highlightbackground=T["card_border"], highlightthickness=1,
                        cursor="hand2")
        card.pack(fill=tk.X, pady=4)

        inner = tk.Frame(card, bg=T["card_bg"], padx=18, pady=12)
        inner.pack(fill=tk.X)

        # Name label
        name_lbl = tk.Label(inner, text=f"👤  {name}",
                            font=("Helvetica", 13, "bold"),
                            bg=T["card_bg"], fg=T["ink"], cursor="hand2")
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
                  font=("Helvetica", 10), bg=T["card_bg"], fg=T["dim"],
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
         self._scores_store, self._sessions_store,
         self._purchases_store) = load_stores(name)
        self.show_menu()

    # ---------------------------------------------------------------- settings

    def _show_settings(self):
        """Settings popup — global options, not per-profile."""
        T = theme()
        root = self.root
        root.update_idletasks()
        cx = root.winfo_x() + root.winfo_width()  // 2
        cy = root.winfo_y() + root.winfo_height() // 2

        win = tk.Toplevel(root)
        win.title("Settings")
        win.configure(bg=T["bg"])
        # Geometry bumped to 560×600 (v0.7.13.3) so all 3 themes fit
        # without clipping the Matrix row. Made resizable too — if a
        # future settings section pushes content past 600px, the user
        # can drag.
        win.geometry(f"560x600+{cx - 280}+{cy - 300}")
        win.resizable(False, True)
        win.grab_set()

        # Header
        hdr = tk.Frame(win, bg=T["btn_primary_bg"], padx=24, pady=16)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="⚙  Settings",
                 font=("Helvetica", 15, "bold"),
                 bg=T["btn_primary_bg"], fg=T["btn_primary_fg"]).pack(side=tk.LEFT)

        body = tk.Frame(win, bg=T["bg"], padx=28, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        def _section(text):
            tk.Label(body, text=text.upper(),
                     font=("Helvetica", 9, "bold"),
                     bg=T["bg"], fg=T["dim"]).pack(anchor="w", pady=(14, 4))
            tk.Frame(body, bg=T["card_border"], height=1).pack(fill=tk.X, pady=(0, 10))

        def _toggle_row(label, desc, key, enabled=True):
            """A row with a label and a live-updating On/Off toggle.

            v0.7.13.3: theme-aware. Previously used hardcoded #0f172a
            label fg + #e2e8f0 OFF-button bg which made the row almost
            invisible in dark/matrix mode (label disappeared, OFF button
            was bright on dark).
            """
            row = tk.Frame(body, bg=T["bg"])
            row.pack(fill=tk.X, pady=5)

            text_col = tk.Frame(row, bg=T["bg"])
            text_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            label_fg = T["ink"]   if enabled else T["faint"]
            desc_fg  = T["dim"]   if enabled else T["faint"]
            tk.Label(text_col, text=label,
                     font=("Helvetica", 11, "bold"),
                     bg=T["bg"], fg=label_fg).pack(anchor="w")
            tk.Label(text_col, text=desc,
                     font=("Helvetica", 9),
                     bg=T["bg"], fg=desc_fg).pack(anchor="w")

            if not enabled:
                tk.Label(row, text="Coming soon",
                         font=("Helvetica", 8), bg=T["bg"],
                         fg=T["faint"]).pack(side=tk.RIGHT, padx=4)
                return

            val = tk.BooleanVar(value=settings.get(key))
            btn_frame = tk.Frame(row, bg=T["bg"])
            btn_frame.pack(side=tk.RIGHT)

            def _refresh_btn():
                on = val.get()
                btn.configure(
                    text="ON " if on else "OFF",
                    bg=T["btn_primary_bg"] if on else T["soft"],
                    fg=T["btn_primary_fg"] if on else T["dim"],
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

        # ── Appearance ────────────────────────────────────────────────────────
        # Dark mode is gated behind the Shop purchase. Once owned, the
        # toggle is enabled and writes settings('theme') as "dark"/"light".
        # Toggling rebuilds the menu under the modal so the change is
        # visible the moment the user closes settings.
        # ── Appearance ────────────────────────────────────────────────────────
        # Theme picker (v0.7.13.1). Light is free; Dark / Matrix unlock
        # via Shop purchases. Each row is one theme — selecting an owned
        # one writes settings('theme') and rebuilds the menu under the
        # modal. Locked rows offer a "Buy in Shop" shortcut instead.
        _section("Appearance")

        from games.theme import available_themes, theme_name as _theme_name

        _THEME_META = {
            "light":  {"name": "Light",     "desc": "Default light theme.",                "icon": "☀",  "shop_id": None},
            "dark":   {"name": "Dark",      "desc": "Clean dark theme.",                   "icon": "🌙", "shop_id": "dark_mode"},
            "matrix": {"name": "Matrix",    "desc": "Green-on-black phosphor. Digits glow.","icon": "🟢", "shop_id": "matrix_mode"},
        }

        def _select_theme(name):
            settings.set("theme", name)
            try:
                self.show_menu()
            except Exception:
                pass
            # Rebuild the settings dialog so the radio state updates.
            win.destroy()
            self._show_settings()

        for tk_name in available_themes():
            meta = _THEME_META[tk_name]
            owned = (meta["shop_id"] is None
                     or (self._purchases_store and self._purchases_store.has(meta["shop_id"])))
            active = (_theme_name() == tk_name)

            row = tk.Frame(body, bg=T["bg"])
            row.pack(fill=tk.X, pady=4)

            text_col = tk.Frame(row, bg=T["bg"])
            text_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            label_fg = T["ink"] if owned else T["faint"]
            tk.Label(text_col, text=f"{meta['icon']}  {meta['name']}",
                     font=("Helvetica", 11, "bold"),
                     bg=T["bg"], fg=label_fg).pack(anchor="w")
            tk.Label(text_col, text=meta["desc"],
                     font=("Helvetica", 9),
                     bg=T["bg"], fg=(T["dim"] if owned else T["faint"])
                     ).pack(anchor="w")

            btn_col = tk.Frame(row, bg=T["bg"])
            btn_col.pack(side=tk.RIGHT)

            if owned:
                if active:
                    tk.Label(btn_col, text="✓ Active",
                             font=("Helvetica", 9, "bold"),
                             bg=T["good_bg"], fg=T["good"],
                             padx=12, pady=6).pack()
                else:
                    tk.Button(btn_col, text="Use",
                              font=("Helvetica", 9, "bold"),
                              bg=T["btn_primary_bg"], fg=T["btn_primary_fg"],
                              relief="flat", bd=0, padx=14, pady=4,
                              cursor="hand2",
                              activebackground=T["btn_primary_hover"],
                              activeforeground=T["btn_primary_fg"],
                              command=lambda n=tk_name: _select_theme(n)
                              ).pack()
            else:
                tk.Button(btn_col, text="🔒 Buy in Shop",
                          font=("Helvetica", 9, "bold"),
                          bg="#faf5ff", fg="#9333ea",
                          relief="flat", bd=0, padx=12, pady=4,
                          cursor="hand2",
                          activebackground="#f3e8ff", activeforeground="#7e22ce",
                          command=lambda: (win.destroy(), self._show_shop())
                          ).pack()

        _toggle_row("Sound effects", "Play sounds on correct/wrong answers.",
                    "sound", enabled=False)

        _section("Language  (coming soon)")
        _toggle_row("Norsk / English", "Switch the interface language.",     "lang",   enabled=False)

        # Close
        tk.Button(win, text="Done", command=win.destroy,
                  font=("Helvetica", 11, "bold"),
                  bg=T["btn_primary_bg"], fg=T["btn_primary_fg"], relief="flat", bd=0,
                  padx=24, pady=8, cursor="hand2",
                  activebackground="#1e293b", activeforeground="white").pack(pady=12)

    # ------------------------------------------------------------------- menu

    def show_menu(self):
        T = theme()
        self._clear()
        self._current_family = None

        outer = tk.Frame(self.root, bg=T["bg"])
        outer.pack(fill=tk.BOTH, expand=True)
        self._current = outer

        # Auto-hide scrollbar pattern. The scrollbar is created but
        # NOT packed up-front; it only appears when content overflows
        # the canvas viewport. _sync_scrollbar runs on every <Configure>
        # of either the inner content or the outer canvas and pack/
        # pack_forgets the scrollbar accordingly. Wrapping
        # `yscrollcommand` keeps Tk's normal scroll-position updates
        # working while letting us steal the side effect for visibility.
        canvas = tk.Canvas(outer, bg=T["bg"], highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        # NOT packed initially — _sync_scrollbar will pack it the first
        # time content overflows.
        _vsb_visible = [False]

        def _sync_scrollbar(*_):
            try:
                bbox = canvas.bbox("all")
                if bbox is None:
                    return
                content_h = bbox[3] - bbox[1]
                view_h    = canvas.winfo_height()
                needed    = content_h > view_h + 1
                if needed and not _vsb_visible[0]:
                    vsb.pack(side=tk.RIGHT, fill=tk.Y)
                    _vsb_visible[0] = True
                elif not needed and _vsb_visible[0]:
                    vsb.pack_forget()
                    _vsb_visible[0] = False
            except Exception:
                pass

        def _yscroll(first, last):
            vsb.set(first, last)
            _sync_scrollbar()

        canvas.configure(yscrollcommand=_yscroll)

        inner = tk.Frame(canvas, bg=T["bg"])
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner_configure(_e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            _sync_scrollbar()
        inner.bind("<Configure>", _on_inner_configure)

        def _on_canvas_configure(e):
            canvas.itemconfig(win_id, width=e.width)
            # Window resizes can change overflow status without the
            # inner content changing; re-sync the scrollbar visibility.
            _sync_scrollbar()
        canvas.bind("<Configure>", _on_canvas_configure)

        self._scroll_target = canvas
        # Reclaim the root mousewheel binding from whichever subscreen we
        # just returned from; otherwise scrolling only works over the
        # scrollbar itself.
        self._install_wheel_handler()

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(inner, bg=T["bg"], padx=48, pady=32)
        hdr.pack(fill=tk.X)

        # Left: title + profile
        title_col = tk.Frame(hdr, bg=T["bg"])
        title_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(title_col, text="Math Practice",
                 font=("Helvetica", 32, "bold"),
                 bg=T["bg"], fg=T["ink"]).pack(anchor="w")
        tk.Label(title_col, text="Choose a game to start practising.",
                 font=("Helvetica", 13), bg=T["bg"], fg=T["muted"]).pack(anchor="w", pady=(4, 0))

        # Profile pill + switch button
        profile_row = tk.Frame(title_col, bg=T["bg"])
        profile_row.pack(anchor="w", pady=(8, 0))
        tk.Label(profile_row, text=f"👤  {self._profile_name}",
                 font=("Helvetica", 10, "bold"),
                 bg=T["card_border"], fg=T["muted"],
                 padx=10, pady=4).pack(side=tk.LEFT)
        tk.Button(profile_row, text="Switch profile",
                  font=("Helvetica", 9), bg=T["bg"], fg=T["dim"],
                  relief="flat", bd=0, padx=8, cursor="hand2",
                  activebackground="#f8fafc", activeforeground="#475569",
                  command=self.show_profiles).pack(side=tk.LEFT, padx=(8, 0))
        tk.Button(profile_row, text="⚙",
                  font=("Helvetica", 10), bg=T["bg"], fg=T["dim"],
                  relief="flat", bd=0, padx=6, cursor="hand2",
                  activebackground="#f8fafc", activeforeground="#475569",
                  command=self._show_settings).pack(side=tk.LEFT, padx=(4, 0))

        # Right: points + achievements button
        right_col = tk.Frame(hdr, bg=T["bg"])
        right_col.pack(side=tk.RIGHT, anchor="ne")

        pts          = self._ach_store.get_points()
        earned_count = len(self._ach_store.get_earned())
        total_count  = len(ACHIEVEMENTS)
        tk.Label(right_col,
                 text=f"⭐ {pts:,} pts",
                 font=("Helvetica", 14, "bold"),
                 bg=T["bg"], fg="#f59e0b").pack(anchor="e")
        tk.Label(right_col,
                 text=f"{earned_count} / {total_count} achievements",
                 font=("Helvetica", 9), bg=T["bg"], fg=T["dim"]).pack(anchor="e", pady=(2, 8))
        tk.Button(right_col, text="🏆  Trophy Room",
                  font=("Helvetica", 10, "bold"),
                  bg=T["btn_primary_bg"], fg=T["btn_primary_fg"], relief="flat", bd=0,
                  padx=14, pady=7, cursor="hand2",
                  activebackground="#1e293b", activeforeground="white",
                  command=self._show_achievements).pack(anchor="e")

        # ── Game family row (4 tiles) ────────────────────────────────────────
        # One tile per family. Click → show_difficulty(family). Compact
        # by design — 12 game cards collapse to 4 here. Any future
        # families plug in by appending an entry to GAMES.
        self._tile_images = []   # release prior refs; renderer repopulates

        family_section = tk.Frame(inner, bg=T["bg"], padx=48)
        family_section.pack(fill=tk.X, pady=(0, 28))

        tk.Label(family_section, text="GAMES",
                 font=("Helvetica", 13, "bold"),
                 bg=T["bg"], fg=T["dim"]).pack(anchor="w", pady=(0, 12))

        family_grid = tk.Frame(family_section, bg=T["bg"])
        family_grid.pack(fill=tk.X)
        for col in range(len(GAMES)):
            family_grid.columnconfigure(col, weight=1)
        for col, family in enumerate(GAMES):
            padx = (0, 14) if col < len(GAMES) - 1 else 0
            self._family_tile(family_grid, family, col, padx)

        # ── Tools row (4 tiles): Practice / Stats / Tutorials / Shop ────────
        self._tools_row(inner)

        # ── Footer ────────────────────────────────────────────────────────────
        tk.Frame(inner, bg=T["card_border"], height=1).pack(fill=tk.X, padx=48, pady=(24, 0))
        tk.Label(inner,
                 text=f"Math Practice  v{__version__}  ·  © 2026 Aleksander Lie",
                 font=("Helvetica", 8), bg=T["bg"], fg=T["faint"]).pack(pady=(6, 24))

    # ============================================================ family tiles

    def _family_tile(self, parent, family, col, padx):
        """Render a single game-family card on the main menu.

        Compact tile — glyph + label + tagline + a row of three small
        status pills (one per difficulty). Clicking anywhere on the tile
        opens the difficulty-selection page for the family.
        """
        T = theme()
        card = tk.Frame(parent, bg=T["card_bg"],
                        highlightbackground=T["card_border"], highlightthickness=1,
                        cursor="hand2")
        card.grid(row=0, column=col, sticky="nsew", padx=padx)

        inner = tk.Frame(card, bg=T["card_bg"], padx=20, pady=20)
        inner.pack(fill=tk.BOTH, expand=True)

        # Top: family glyph in a colored disc + "Game" pill on the right.
        top = tk.Frame(inner, bg=T["card_bg"])
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
                 bg=T["card_bg"], fg=T["ink"],
                 wraplength=220, justify="left", anchor="w").pack(fill=tk.X)
        tk.Label(inner, text=family["tagline"],
                 font=("Helvetica", 9), bg=T["card_bg"], fg=T["muted"],
                 wraplength=220, justify="left", anchor="w").pack(fill=tk.X,
                                                                   pady=(4, 14))

        # Difficulty status pills — one per difficulty, in tier order.
        # State: "open", "locked", or "sharp" (sharp_<gid> achievement
        # earned). Surfaces progression at a glance without making the
        # user click into the family.
        status_row = tk.Frame(inner, bg=T["card_bg"])
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
        T = theme()
        section = tk.Frame(parent, bg=T["bg"], padx=48)
        section.pack(fill=tk.X, pady=(0, 28))

        tk.Label(section, text="TOOLS",
                 font=("Helvetica", 13, "bold"),
                 bg=T["bg"], fg=T["dim"]).pack(anchor="w", pady=(0, 12))

        cards = tk.Frame(section, bg=T["bg"])
        cards.pack(fill=tk.X)
        for col in range(4):
            cards.columnconfigure(col, weight=1)

        # ── Practice Missed card ─────────────────────────────────────────
        count   = self._missed_store.count()
        enabled = count > 0

        card_bg = T["card_bg"] if enabled else T["card_dim"]
        name_fg = T["ink"]      if enabled else T["dim"]
        desc_fg = T["muted"]    if enabled else T["dim"]
        desc    = (f"{count} question{'s' if count != 1 else ''} waiting for review."
                   if enabled else "No missed questions yet — keep playing!")

        card = tk.Frame(cards, bg=card_bg,
                        highlightbackground=T["card_border"], highlightthickness=1,
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

        stats_card = tk.Frame(cards, bg=T["card_bg"],
                              highlightbackground=T["card_border"], highlightthickness=1,
                              cursor="hand2")
        stats_card.grid(row=0, column=1, sticky="nsew", padx=(0, 14))

        stats_inner = tk.Frame(stats_card, bg=T["card_bg"], padx=20, pady=20)
        stats_inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(stats_inner, text="Insights",
                 font=("Helvetica", 9, "bold"),
                 bg="#ecfdf5", fg="#047857",
                 padx=10, pady=3).pack(anchor="w", pady=(0, 12))
        tk.Label(stats_inner, text="Progress & Stats",
                 font=("Helvetica", 14, "bold"),
                 bg=T["card_bg"], fg=T["ink"]).pack(anchor="w")
        tk.Label(stats_inner, text=stats_desc,
                 font=("Helvetica", 9), bg=T["card_bg"], fg=T["muted"],
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

        tut_card = tk.Frame(cards, bg=T["card_bg"],
                            highlightbackground=T["card_border"], highlightthickness=1,
                            cursor="hand2")
        tut_card.grid(row=0, column=2, sticky="nsew", padx=(0, 14))

        tut_inner = tk.Frame(tut_card, bg=T["card_bg"], padx=20, pady=20)
        tut_inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(tut_inner, text="Learn",
                 font=("Helvetica", 9, "bold"),
                 bg="#eef2ff", fg="#4f46e5",
                 padx=10, pady=3).pack(anchor="w", pady=(0, 12))
        tk.Label(tut_inner, text="Tutorials",
                 font=("Helvetica", 14, "bold"),
                 bg=T["card_bg"], fg=T["ink"]).pack(anchor="w")
        tk.Label(tut_inner, text=tut_desc,
                 font=("Helvetica", 9), bg=T["card_bg"], fg=T["muted"],
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

        # ── Shop card ────────────────────────────────────────────────────
        # Functional shop tile (v0.7.13). Click → modal listing every
        # entry in SHOP_ITEMS with its own buy / owned state.
        self._shop_tile(cards)

    def _shop_tile(self, parent):
        """Tools-row entry that opens the Shop modal."""
        T = theme()

        # Item count summary in the subtitle so the pupil knows the
        # shop is non-empty and how much progress they have.
        total = len(SHOP_ITEMS)
        owned = sum(1 for it in SHOP_ITEMS
                    if self._purchases_store and self._purchases_store.has(it["id"]))
        if total == 0:
            subtitle = "Nothing on the shelves yet."
        else:
            subtitle = f"{owned}/{total} items owned. Spend your points."

        card = tk.Frame(parent, bg=T["card_bg"],
                        highlightbackground=T["card_border"], highlightthickness=1,
                        cursor="hand2")
        card.grid(row=0, column=3, sticky="nsew")

        inner = tk.Frame(card, bg=T["card_bg"], padx=20, pady=20)
        inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(inner, text="Spend",
                 font=("Helvetica", 9, "bold"),
                 bg=T["shop_bg"], fg=T["shop"],
                 padx=10, pady=3).pack(anchor="w", pady=(0, 12))
        tk.Label(inner, text="🛍  Shop",
                 font=("Helvetica", 14, "bold"),
                 bg=T["card_bg"], fg=T["ink"]).pack(anchor="w")
        tk.Label(inner, text=subtitle,
                 font=("Helvetica", 9), bg=T["card_bg"], fg=T["muted"],
                 justify="left", wraplength=200).pack(anchor="w", pady=(6, 14))

        tk.Button(
            inner, text="Open  →",
            font=("Helvetica", 10, "bold"),
            bg=T["shop"], fg="white",
            relief="flat", bd=0, padx=12, pady=5, cursor="hand2",
            activebackground=T["accent_dark"], activeforeground="white",
            command=self._show_shop,
        ).pack(anchor="w")

        for w in (card, inner):
            w.bind("<Button-1>", lambda e: self._show_shop())

    def _show_shop(self):
        """Modal listing SHOP_ITEMS with buy / owned state per entry."""
        T = theme()
        root = self.root
        root.update_idletasks()
        cx = root.winfo_x() + root.winfo_width()  // 2
        cy = root.winfo_y() + root.winfo_height() // 2

        win = tk.Toplevel(root)
        win.title("Shop")
        win.configure(bg=T["bg"])
        win.transient(root)
        win.grab_set()

        w_px, h_px = 560, 480
        win.geometry(f"{w_px}x{h_px}+{cx - w_px // 2}+{cy - h_px // 2}")
        win.resizable(False, False)

        # Header — title + balance
        hdr = tk.Frame(win, bg=T["btn_primary_bg"], padx=24, pady=16)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="🛍  Shop",
                 font=("Helvetica", 16, "bold"),
                 bg=T["btn_primary_bg"], fg=T["btn_primary_fg"]).pack(side=tk.LEFT)

        balance_lbl = tk.Label(
            hdr, text=f"⭐ {self._ach_store.get_points():,} pts",
            font=("Helvetica", 12, "bold"),
            bg=T["btn_primary_bg"], fg="#f59e0b",
        )
        balance_lbl.pack(side=tk.RIGHT)

        # Body
        body = tk.Frame(win, bg=T["bg"], padx=20, pady=18)
        body.pack(fill=tk.BOTH, expand=True)

        if not SHOP_ITEMS:
            tk.Label(body, text="No items in stock yet.",
                     font=("Helvetica", 11),
                     bg=T["bg"], fg=T["muted"]).pack(expand=True)

        # Render each item card. Cards are self-refreshing — `_render_item`
        # destroys + redraws the per-item frame so the Buy → Owned
        # transition lands without rebuilding the whole modal.
        item_frames = {}

        def _refresh_balance():
            balance_lbl.config(text=f"⭐ {self._ach_store.get_points():,} pts")

        def _render_item(item):
            owned = self._purchases_store.has(item["id"])
            cost  = item["price"]
            can_afford = self._ach_store.get_points() >= cost

            # Achievement-gate (v0.7.13.2). When `unlock_req` names an
            # achievement id, the item can't be bought until that
            # achievement is earned — even if the pupil has the points.
            # Surfaces the requirement so the user knows how to progress.
            req_id = item.get("unlock_req")
            req_met = (req_id is None) or self._ach_store.has(req_id)
            req_ach = ACHIEVEMENTS_BY_ID.get(req_id) if req_id else None

            row = tk.Frame(body, bg=T["card_bg"],
                           highlightbackground=T["card_border"], highlightthickness=1)
            row.pack(fill=tk.X, pady=(0, 12))
            row_inner = tk.Frame(row, bg=T["card_bg"], padx=18, pady=14)
            row_inner.pack(fill=tk.X)

            # Left column: icon
            tk.Label(row_inner, text=item["icon"],
                     font=("Helvetica", 28),
                     bg=T["card_bg"], fg=T["ink"]).pack(side=tk.LEFT, padx=(0, 14))

            # Middle column: name / category / desc
            text_col = tk.Frame(row_inner, bg=T["card_bg"])
            text_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            head = tk.Frame(text_col, bg=T["card_bg"])
            head.pack(fill=tk.X)
            tk.Label(head, text=item["name"],
                     font=("Helvetica", 13, "bold"),
                     bg=T["card_bg"], fg=T["ink"]).pack(side=tk.LEFT)
            tk.Label(head, text=f"  {item['category']}",
                     font=("Helvetica", 9),
                     bg=T["card_bg"], fg=T["dim"]).pack(side=tk.LEFT, padx=(6, 0))
            tk.Label(text_col, text=item["desc"],
                     font=("Helvetica", 9),
                     bg=T["card_bg"], fg=T["muted"],
                     justify="left", wraplength=320,
                     anchor="w").pack(fill=tk.X, pady=(2, 0))

            # Right column: price + buy/owned button
            right_col = tk.Frame(row_inner, bg=T["card_bg"])
            right_col.pack(side=tk.RIGHT, padx=(14, 0))

            if owned:
                tk.Label(right_col, text="✓ Owned",
                         font=("Helvetica", 10, "bold"),
                         bg=T["good_bg"], fg=T["good"],
                         padx=12, pady=6).pack()
            else:
                tk.Label(right_col, text=f"⭐ {cost:,} pts",
                         font=("Helvetica", 11, "bold"),
                         bg=T["card_bg"], fg=T["ink"]).pack(pady=(0, 6))

                if not req_met:
                    # Achievement-locked. Show a hint instead of Buy and
                    # surface the requirement description in the body so
                    # the pupil knows what to chase.
                    btn = tk.Button(
                        right_col, text="🔒 Locked",
                        font=("Helvetica", 10, "bold"),
                        bg=T["soft"], fg=T["dim"],
                        relief="flat", bd=0, padx=12, pady=5,
                        cursor="arrow", state="disabled",
                    )
                    if req_ach:
                        tk.Label(text_col,
                                 text=f"🔒 Earn '{req_ach['name']}' first "
                                      f"({req_ach.get('desc','')})",
                                 font=("Helvetica", 9, "bold"),
                                 bg=T["card_bg"], fg=T["warn"],
                                 wraplength=320, justify="left", anchor="w"
                                 ).pack(fill=tk.X, pady=(4, 0))
                elif can_afford:
                    btn = tk.Button(
                        right_col, text="Buy",
                        font=("Helvetica", 10, "bold"),
                        bg=T["shop"], fg="white",
                        relief="flat", bd=0, padx=18, pady=5, cursor="hand2",
                        activebackground=T["accent_dark"], activeforeground="white",
                        command=lambda i=item: _buy(i),
                    )
                else:
                    btn = tk.Button(
                        right_col, text="Need points",
                        font=("Helvetica", 10, "bold"),
                        bg=T["soft"], fg=T["dim"],
                        relief="flat", bd=0, padx=12, pady=5,
                        cursor="arrow", state="disabled",
                    )
                btn.pack()

            return row

        def _buy(item):
            cost = item["price"]
            if self._purchases_store.has(item["id"]):
                return
            # Defensive: re-check the achievement gate at click time so a
            # stale UI can't be exploited (e.g. user opened shop, earned
            # nothing, but unlock state somehow flipped). The shop modal
            # rebuilds after every purchase so this normally won't fire.
            req_id = item.get("unlock_req")
            if req_id and not self._ach_store.has(req_id):
                req_ach = ACHIEVEMENTS_BY_ID.get(req_id, {})
                messagebox.showwarning(
                    "Locked",
                    f"This item requires the '{req_ach.get('name', req_id)}' "
                    f"achievement first.",
                    parent=win,
                )
                return
            if not self._ach_store.spend(cost):
                messagebox.showwarning(
                    "Not enough points",
                    f"You need {cost:,} points to buy {item['name']}, "
                    f"but only have {self._ach_store.get_points():,}.",
                    parent=win,
                )
                return
            self._purchases_store.purchase(item["id"])
            on_buy = item.get("on_buy")
            if callable(on_buy):
                try:
                    on_buy(self)
                except Exception:
                    pass

            messagebox.showinfo(
                "Purchase complete",
                f"{item['icon']}  {item['name']} unlocked!\n\n"
                + ("Toggle it on from Settings → Appearance."
                   if item["id"] == "dark_mode"
                   else "Enjoy your new cosmetic."),
                parent=win,
            )

            # Re-render: rebuild the list cleanly so owned/locked states
            # all update together (e.g. balance change might disable
            # other Buy buttons).
            for w in body.winfo_children():
                w.destroy()
            for it in SHOP_ITEMS:
                item_frames[it["id"]] = _render_item(it)
            _refresh_balance()

        for it in SHOP_ITEMS:
            item_frames[it["id"]] = _render_item(it)

        # Footer close
        tk.Button(win, text="Close", command=win.destroy,
                  font=("Helvetica", 11),
                  bg=T["card_bg"], fg=T["muted"],
                  relief="solid", bd=1, padx=20, pady=6, cursor="hand2"
                  ).pack(pady=10)

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
        T = theme()
        self._clear()
        self._current_family = family
        self._tile_images    = []   # release prior refs

        outer = tk.Frame(self.root, bg=T["bg"])
        outer.pack(fill=tk.BOTH, expand=True)
        self._current = outer

        # Top bar — back button only
        top = tk.Frame(outer, bg=T["bg"], padx=24, pady=10)
        top.pack(fill=tk.X)
        tk.Button(top, text="← Menu",
                  font=("Helvetica", 10), bg=T["bg"], fg=T["muted"],
                  relief="flat", bd=0, cursor="hand2",
                  activebackground="#f8fafc", activeforeground="#0f172a",
                  command=self.show_menu).pack(side=tk.LEFT)

        # Header — family glyph + label + tagline
        hdr = tk.Frame(outer, bg=T["bg"], padx=48, pady=18)
        hdr.pack(fill=tk.X)

        glyph_box = tk.Frame(hdr, bg=family["accent"], padx=14, pady=8)
        glyph_box.pack(side=tk.LEFT)
        tk.Label(glyph_box, text=family["glyph"],
                 font=("Helvetica", 28, "bold"),
                 bg=family["accent"], fg="white").pack()

        title_col = tk.Frame(hdr, bg=T["bg"])
        title_col.pack(side=tk.LEFT, padx=(16, 0), fill=tk.X, expand=True)
        tk.Label(title_col, text=family["label"],
                 font=("Helvetica", 26, "bold"),
                 bg=T["bg"], fg=T["ink"]).pack(anchor="w")
        tk.Label(title_col, text=family["tagline"],
                 font=("Helvetica", 11),
                 bg=T["bg"], fg=T["muted"]).pack(anchor="w", pady=(4, 0))
        tk.Label(title_col, text="Choose a difficulty.",
                 font=("Helvetica", 11, "bold"),
                 bg=T["bg"], fg=T["muted"]).pack(anchor="w", pady=(8, 0))

        # 3-column difficulty grid.
        # Cards size to their content and sit at the top of the wrap
        # rather than stretching to fill the window. Stretching produced
        # a tall white void below the Play button on a maximised window;
        # `sticky="new"` plus no rowconfigure-weight keeps each card
        # only as tall as the asset slot + body content require.
        cards_wrap = tk.Frame(outer, bg=T["bg"], padx=48, pady=20)
        cards_wrap.pack(fill=tk.X, expand=False)

        cards = tk.Frame(cards_wrap, bg=T["bg"])
        cards.pack(fill=tk.X)
        for col in range(3):
            cards.columnconfigure(col, weight=1)

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
        T = theme()
        # Tier metadata (badge colours match the existing per-difficulty palette).
        tier = next((t for t in _DIFFICULTY_TIERS if t["key"] == diff["key"]), _DIFFICULTY_TIERS[0])
        T    = theme()
        badge_bg = T[tier["badge_bg_token"]]
        badge_fg = T[tier["badge_fg_token"]]

        bg     = T["card_bg"] if not locked else T["card_dim"]
        ink_fg = T["ink"]      if not locked else T["dim"]
        sub_fg = T["muted"]    if not locked else T["dim"]

        card = tk.Frame(parent, bg=bg,
                        highlightbackground=T["card_border"], highlightthickness=1,
                        cursor="hand2")
        # `sticky="new"` (not nsew) — cards top-align and only take the
        # height their content needs. Combined with no rowconfigure-weight
        # on the parent, this kills the empty-white-void problem on
        # maximised windows.
        card.grid(row=0, column=col, sticky="new", padx=padx)

        # Asset slot — fixed-height 160px box, centered glyph or PNG.
        # Slightly taller than v0.7.12's first cut so the tier glyph
        # has more breathing room without a hairline divider stranded
        # in the middle of the card.
        asset_slot = tk.Frame(card, bg=bg, height=160)
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
        tk.Frame(card, bg=T["card_border"], height=1).pack(fill=tk.X)

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
                     bg=bg, fg=T["dim"]).pack(side=tk.LEFT)

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
            bg=T["btn_primary_bg"], fg=T["btn_primary_fg"], relief="flat", bd=0,
            padx=14, pady=6, cursor="hand2",
            activebackground="#1e293b", activeforeground="white",
            command=lambda f=family, d=diff: self._launch(f, d),
        ).pack(anchor="w")

        for w in (card, asset_slot, inner):
            w.bind("<Button-1>",
                   lambda e, f=family, d=diff: self._launch(f, d))

    def _render_lock_hint(self, parent, unlock_req):
        """Render the unlock-hint block inside a locked difficulty card."""
        T = theme()
        req_name = req_desc = req_game = ""
        if unlock_req:
            ach = ACHIEVEMENTS_BY_ID.get(unlock_req)
            if ach:
                req_name = ach["name"]
                req_desc = ach["desc"]
                req_game = GAME_NAMES.get(ach.get("game_id", ""), "")

        unlock_label = (f"Unlock: '{req_name}' in {req_game}"
                        if req_game else f"Unlock: '{req_name}' achievement")

        unlock_frame = tk.Frame(parent, bg=T["card_border"],
                                highlightbackground=T["faint"], highlightthickness=1)
        unlock_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(unlock_frame, text=unlock_label,
                 font=("Helvetica", 9), bg=T["card_border"], fg=T["muted"],
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
        T = theme()
        root = self.root
        root.update_idletasks()
        cx = root.winfo_x() + root.winfo_width()  // 2
        cy = root.winfo_y() + root.winfo_height() // 2

        win = tk.Toplevel(root)
        win.title("Trophy Room")
        win.configure(bg=T["bg"])
        win.geometry(f"640x580+{cx - 320}+{cy - 290}")
        win.resizable(True, True)

        # Header strip — uses btn_primary_bg as a "branded title bar"
        # so it stays a clear contrast band in every theme (dark slate
        # in light mode, indigo in dark mode, phosphor green in matrix).
        hdr = tk.Frame(win, bg=T["btn_primary_bg"], padx=24, pady=14)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="🏆  Trophy Room",
                 font=("Helvetica", 16, "bold"),
                 bg=T["btn_primary_bg"], fg=T["btn_primary_fg"]).pack(side=tk.LEFT)

        pts            = self._ach_store.get_points()
        earned_count   = len(self._ach_store.get_earned())
        total_count    = len(ACHIEVEMENTS)
        spent          = self._ach_store.get_total_spent()
        lifetime       = self._ach_store.get_lifetime_earned()

        # Right-side stat block: balance, achievement progress, and
        # (when the profile has spent anything) a lifetime/spent line.
        right_block = tk.Frame(hdr, bg=T["btn_primary_bg"])
        right_block.pack(side=tk.RIGHT)
        tk.Label(right_block,
                 text=f"⭐ {pts:,} pts  ·  {earned_count}/{total_count}",
                 font=("Helvetica", 11, "bold"),
                 bg=T["btn_primary_bg"], fg="#f59e0b").pack(anchor="e")
        if spent > 0:
            tk.Label(right_block,
                     text=f"{lifetime:,} lifetime  ·  {spent:,} spent",
                     font=("Helvetica", 9),
                     bg=T["btn_primary_bg"], fg=T["btn_primary_fg"]
                     ).pack(anchor="e", pady=(2, 0))

        body_outer = tk.Frame(win, bg=T["bg"])
        body_outer.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(body_outer, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        txt = tk.Text(
            body_outer, bg=T["bg"], relief="flat", bd=0,
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
    root = tk.Tk()
    root.title(f"Math Practice  v{__version__}")
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
