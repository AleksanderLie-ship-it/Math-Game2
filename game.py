"""
game.py
-------
Main entry point. Shows the profile screen, then the game-selection menu,
and launches mini-games.

To add a new game:
  1. Create games/your_game.py subclassing BaseGame
  2. Import it below and add it to CATEGORIES
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

__version__ = "0.4.1"

import tkinter as tk
from tkinter import ttk, messagebox

from games.mult_basic         import MultiplicationBasic
from games.mult_intermediate  import MultiplicationIntermediate
from games.mult_advanced      import MultiplicationAdvanced
from games.div_basic          import DivisionBasic
from games.div_intermediate   import DivisionIntermediate
from games.div_advanced       import DivisionAdvanced
from games.practice_missed    import PracticeMissed
from games.profile_manager    import (
    list_profiles, create_profile, delete_profile, load_stores, last_profile,
)
from games.settings_manager   import settings
from games.achievements       import (
    ACHIEVEMENTS, ACHIEVEMENTS_BY_ID, CATEGORY_ORDER,
    UNLOCK_REQUIREMENTS, GAME_NAMES, GAME_IDS, GAME_SHORT,
)


# ── Game registry ──────────────────────────────────────────────────────────────

CATEGORIES = [
    {
        "label": "Multiplication",
        "games": [
            {
                "name":     "Beginner",
                "desc":     "Times tables 1-10.\nBuild speed and confidence.",
                "badge":    "Beginner",
                "badge_bg": "#f0fdf4",
                "badge_fg": "#15803d",
                "cls":      MultiplicationBasic,
                "game_id":  "mult_basic",
            },
            {
                "name":     "Intermediate",
                "desc":     "Two-digit and mixed problems.\nLike 34 x 7 or 34 x 78.",
                "badge":    "Intermediate",
                "badge_bg": "#fffbeb",
                "badge_fg": "#b45309",
                "cls":      MultiplicationIntermediate,
                "game_id":  "mult_intermediate",
            },
            {
                "name":     "Advanced",
                "desc":     "Three-digit x two-digit.\nLike 134 x 78.",
                "badge":    "Advanced",
                "badge_bg": "#fef2f2",
                "badge_fg": "#b91c1c",
                "cls":      MultiplicationAdvanced,
                "game_id":  "mult_advanced",
            },
        ],
    },
    {
        "label": "Division",
        "games": [
            {
                "name":     "Beginner",
                "desc":     "Whole-number answers.\nDivisors from 2 to 10.",
                "badge":    "Beginner",
                "badge_bg": "#f0fdf4",
                "badge_fg": "#15803d",
                "cls":      DivisionBasic,
                "game_id":  "div_basic",
            },
            {
                "name":     "Intermediate",
                "desc":     "Larger dividends.\nAlways whole-number answers.",
                "badge":    "Intermediate",
                "badge_bg": "#fffbeb",
                "badge_fg": "#b45309",
                "cls":      DivisionIntermediate,
                "game_id":  "div_intermediate",
            },
            {
                "name":     "Advanced",
                "desc":     "Large numbers + decimal answers.\nLike 13 / 2 = 6.5.",
                "badge":    "Advanced",
                "badge_bg": "#fef2f2",
                "badge_fg": "#b91c1c",
                "cls":      DivisionAdvanced,
                "game_id":  "div_advanced",
            },
        ],
    },
]


# ── App controller ─────────────────────────────────────────────────────────────

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Math Practice  v{__version__}")
        self.root.geometry("960x680")
        self.root.minsize(700, 480)
        self.root.configure(bg="#f8fafc")
        self._apply_styles()

        self._current       = None
        self._scroll_target = None

        # Active profile stores — set after profile selection
        self._profile_name  = None
        self._ach_store     = None
        self._missed_store  = None
        self._scores_store  = None

        # Persistent root-level mousewheel
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
        self._profile_name                                       = name
        self._ach_store, self._missed_store, self._scores_store  = load_stores(name)
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

        # ── Game categories ───────────────────────────────────────────────────
        for cat in CATEGORIES:
            self._category_row(inner, cat)

        self._review_row(inner)

        # ── Footer ────────────────────────────────────────────────────────────
        tk.Frame(inner, bg="#e2e8f0", height=1).pack(fill=tk.X, padx=48, pady=(24, 0))
        tk.Label(inner,
                 text=f"Math Practice  v{__version__}  ·  © 2026 Aleksander Lie",
                 font=("Helvetica", 8), bg="#f8fafc", fg="#cbd5e1").pack(pady=(6, 24))

    # ------------------------------------------------------------------ rows

    def _category_row(self, parent, cat):
        section = tk.Frame(parent, bg="#f8fafc", padx=48)
        section.pack(fill=tk.X, pady=(0, 28))

        tk.Label(section, text=cat["label"],
                 font=("Helvetica", 13, "bold"),
                 bg="#f8fafc", fg="#94a3b8").pack(anchor="w", pady=(0, 12))

        cards = tk.Frame(section, bg="#f8fafc")
        cards.pack(fill=tk.X)
        n = len(cat["games"])
        for col, game in enumerate(cat["games"]):
            cards.columnconfigure(col, weight=1)
            padx    = (0, 16) if col < n - 1 else 0
            game_id = game.get("game_id", "")
            unlock  = UNLOCK_REQUIREMENTS.get(game_id)
            locked  = bool(unlock and not self._ach_store.has(unlock))
            self._game_card(cards, game, col, padx, locked=locked, unlock_req=unlock)

    def _review_row(self, parent):
        section = tk.Frame(parent, bg="#f8fafc", padx=48)
        section.pack(fill=tk.X, pady=(0, 28))

        tk.Label(section, text="Review",
                 font=("Helvetica", 13, "bold"),
                 bg="#f8fafc", fg="#94a3b8").pack(anchor="w", pady=(0, 12))

        cards = tk.Frame(section, bg="#f8fafc")
        cards.pack(fill=tk.X)
        for col in range(3):
            cards.columnconfigure(col, weight=1)

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
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        inner = tk.Frame(card, bg=card_bg, padx=22, pady=22)
        inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(inner, text="Review",
                 font=("Helvetica", 9, "bold"),
                 bg="#f0f4ff", fg="#4f46e5",
                 padx=10, pady=3).pack(anchor="w", pady=(0, 12))
        tk.Label(inner, text="Practice Missed",
                 font=("Helvetica", 15, "bold"),
                 bg=card_bg, fg=name_fg).pack(anchor="w")
        tk.Label(inner, text=desc,
                 font=("Helvetica", 10), bg=card_bg, fg=desc_fg,
                 justify="left").pack(anchor="w", pady=(6, 18))

        play_btn = tk.Button(
            inner, text="Start Review  ->",
            font=("Helvetica", 10, "bold"),
            bg="#4f46e5" if enabled else "#e2e8f0",
            fg="white"   if enabled else "#94a3b8",
            relief="flat", bd=0, padx=14, pady=6,
            cursor="hand2" if enabled else "arrow",
            state="normal" if enabled else "disabled",
            command=self._launch_practice if enabled else None,
        )
        play_btn.pack(anchor="w")

        if enabled:
            for w in (card, inner):
                w.bind("<Button-1>", lambda e: self._launch_practice())

    # ------------------------------------------------------------------ cards

    def _game_card(self, parent, game, col, padx, locked=False, unlock_req=None):
        if locked:
            self._locked_card(parent, game, col, padx, unlock_req)
        else:
            self._unlocked_card(parent, game, col, padx)

    def _unlocked_card(self, parent, game, col, padx):
        card = tk.Frame(parent, bg="white",
                        highlightbackground="#e2e8f0", highlightthickness=1,
                        cursor="hand2")
        card.grid(row=0, column=col, sticky="nsew", padx=padx)

        inner = tk.Frame(card, bg="white", padx=22, pady=22)
        inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(inner, text=game["badge"],
                 font=("Helvetica", 9, "bold"),
                 bg=game["badge_bg"], fg=game["badge_fg"],
                 padx=10, pady=3).pack(anchor="w", pady=(0, 12))
        tk.Label(inner, text=game["name"],
                 font=("Helvetica", 15, "bold"),
                 bg="white", fg="#0f172a").pack(anchor="w")
        tk.Label(inner, text=game["desc"],
                 font=("Helvetica", 10), bg="white", fg="#64748b",
                 justify="left").pack(anchor="w", pady=(6, 18))
        tk.Button(inner, text="Play  ->",
                  font=("Helvetica", 10, "bold"),
                  bg="#0f172a", fg="white", relief="flat", bd=0,
                  padx=14, pady=6, cursor="hand2",
                  activebackground="#1e293b", activeforeground="white",
                  command=lambda g=game: self._launch(g)).pack(anchor="w")

        for w in (card, inner):
            w.bind("<Button-1>", lambda e, g=game: self._launch(g))

    def _locked_card(self, parent, game, col, padx, unlock_req):
        card = tk.Frame(parent, bg="#f8fafc",
                        highlightbackground="#e2e8f0", highlightthickness=1,
                        cursor="hand2")
        card.grid(row=0, column=col, sticky="nsew", padx=padx)

        inner = tk.Frame(card, bg="#f8fafc", padx=22, pady=22)
        inner.pack(fill=tk.BOTH, expand=True)

        badge_row = tk.Frame(inner, bg="#f8fafc")
        badge_row.pack(anchor="w", pady=(0, 12))
        tk.Label(badge_row, text=game["badge"],
                 font=("Helvetica", 9, "bold"),
                 bg="#e2e8f0", fg="#94a3b8",
                 padx=10, pady=3).pack(side=tk.LEFT)
        tk.Label(badge_row, text="  🔒 Locked",
                 font=("Helvetica", 9, "bold"),
                 bg="#f8fafc", fg="#94a3b8").pack(side=tk.LEFT)

        tk.Label(inner, text=game["name"],
                 font=("Helvetica", 15, "bold"),
                 bg="#f8fafc", fg="#94a3b8").pack(anchor="w")

        req_name = req_desc = req_game = ""
        if unlock_req:
            ach = ACHIEVEMENTS_BY_ID.get(unlock_req)
            if ach:
                req_name = ach["name"]
                req_desc = ach["desc"]
                req_game = GAME_NAMES.get(ach.get("game_id", ""), "")

        unlock_label = (f"Unlock: '{req_name}' in {req_game}"
                        if req_game else f"Unlock: '{req_name}' achievement")

        tk.Label(inner, text=game["desc"],
                 font=("Helvetica", 10), bg="#f8fafc", fg="#94a3b8",
                 justify="left").pack(anchor="w", pady=(6, 10))

        unlock_frame = tk.Frame(inner, bg="#e2e8f0",
                                highlightbackground="#cbd5e1", highlightthickness=1)
        unlock_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(unlock_frame, text=unlock_label,
                 font=("Helvetica", 9), bg="#e2e8f0", fg="#64748b",
                 padx=10, pady=6, wraplength=200, justify="left").pack(anchor="w")

        def _show_lock_info(e=None):
            messagebox.showinfo(
                "Locked",
                f"This level is locked.\n\n"
                f"Earn the '{req_name}' achievement in {req_game} to unlock it:\n\n"
                f"{req_desc}",
            )

        def _bind_all_children(widget):
            widget.bind("<Button-1>", _show_lock_info)
            for child in widget.winfo_children():
                _bind_all_children(child)

        _bind_all_children(card)

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

    def _launch(self, game):
        self._clear()
        frame = tk.Frame(self.root, bg="#f8fafc")
        frame.pack(fill=tk.BOTH, expand=True)
        self._current = frame
        game["cls"](frame,
                    back_callback=self.show_menu,
                    ach_store=self._ach_store,
                    missed_store=self._missed_store,
                    scores_store=self._scores_store)

    def _launch_practice(self):
        self._clear()
        frame = tk.Frame(self.root, bg="#f8fafc")
        frame.pack(fill=tk.BOTH, expand=True)
        self._current = frame
        PracticeMissed(frame,
                       back_callback=self.show_menu,
                       ach_store=self._ach_store,
                       missed_store=self._missed_store,
                       scores_store=self._scores_store)

    def _clear(self):
        self._scroll_target = None
        if self._current is not None:
            self._current.destroy()
            self._current = None


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.title(f"Math Practice  v{__version__}")
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
