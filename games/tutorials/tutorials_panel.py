"""
tutorials_panel.py
------------------
Grid of tutorial cards. Entered from the main menu.

Each card represents one game mode for which a tutorial exists. Locking
mirrors the existing game-unlock requirements (UNLOCK_REQUIREMENTS) so the
pupil never sees a tutorial for content they can't yet play.

Cards without a tutorial module registered (e.g. mult_basic) are not shown
at all — no empty placeholders.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import tkinter as tk
from tkinter import ttk

from ..achievements import (
    GAME_IDS, GAME_NAMES, UNLOCK_REQUIREMENTS, ACHIEVEMENTS_BY_ID,
)
from . import TUTORIAL_REGISTRY, INTENTIONAL_NO_GUIDE
from .slideshow_frame import (
    SlideshowFrame,
    BG, CARD_BG, CARD_BORDER, INK, MUTED, DIM, SOFT, FAINT, ACCENT, GOOD,
)


# Curriculum category groupings, mirroring the main menu layout
_CATEGORIES = [
    ("Multiplication", ["mult_basic", "mult_intermediate", "mult_advanced"]),
    ("Division",       ["div_basic",  "div_intermediate",  "div_advanced"]),
    ("Fractions — Operations",
                       ["frac_basic", "frac_intermediate", "frac_advanced"]),
    ("Fractions — Conversions",
                       ["conv_basic", "conv_intermediate", "conv_advanced"]),
]


class TutorialsPanel:
    """Full-page tutorial browser.

    Parameters
    ----------
    parent : tk.Frame
    back_callback : callable — return to main menu
    ach_store : AchievementsStore — read-only, used for lock resolution
    """

    def __init__(self, parent, back_callback, ach_store):
        self.parent        = parent
        self.back_callback = back_callback
        self._as           = ach_store
        self._current_child = None

        self._build()

    # ================================================================ build

    def _build(self):
        # Top bar
        top = tk.Frame(self.parent, bg=BG, padx=24, pady=10)
        top.pack(fill=tk.X)

        tk.Button(top, text="← Menu",
                  font=("Helvetica", 10), bg=BG, fg="#475569",
                  relief="flat", bd=0, cursor="hand2",
                  activebackground=BG, activeforeground=INK,
                  command=self.back_callback).pack(side=tk.LEFT)

        # Header
        hdr = tk.Frame(self.parent, bg=BG, padx=48, pady=24)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="📖  Tutorials",
                 font=("Helvetica", 28, "bold"),
                 bg=BG, fg=INK).pack(anchor="w")
        tk.Label(hdr,
                 text=("Step-by-step explanations for each game. "
                       "Unlocked in the same order as the games themselves."),
                 font=("Helvetica", 12), bg=BG, fg=MUTED).pack(anchor="w",
                                                               pady=(4, 0))

        # Scrollable body — same pattern as stats_screen
        outer = tk.Frame(self.parent, bg=BG)
        outer.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(outer, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0,
                           yscrollcommand=vsb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=canvas.yview)

        body = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win_id, width=e.width))

        def _wheel(e):
            try:
                canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
            except Exception:
                pass
        canvas.bind_all("<MouseWheel>", _wheel)

        self._body = body
        self._render_categories()

    # ================================================================ render

    def _render_categories(self):
        for cat_label, game_ids in _CATEGORIES:
            # skip whole category if none of its games has a tutorial
            tutorials_in_cat = [gid for gid in game_ids if gid in TUTORIAL_REGISTRY]
            if not tutorials_in_cat:
                continue

            section = tk.Frame(self._body, bg=BG, padx=48)
            section.pack(fill=tk.X, pady=(4, 24))

            tk.Label(section, text=cat_label,
                     font=("Helvetica", 13, "bold"),
                     bg=BG, fg=DIM).pack(anchor="w", pady=(0, 12))

            cards = tk.Frame(section, bg=BG)
            cards.pack(fill=tk.X)
            for col in range(3):
                cards.columnconfigure(col, weight=1)

            for col, gid in enumerate(game_ids):
                padx = (0, 16) if col < 2 else 0
                if gid in TUTORIAL_REGISTRY:
                    locked = self._is_locked(gid)
                    self._tutorial_card(cards, col, padx, gid, locked=locked)
                elif gid in INTENTIONAL_NO_GUIDE:
                    # Designed to have no tutorial — mult_basic is pure
                    # rote memorisation. Say so explicitly.
                    self._not_needed_card(cards, col, padx, gid)
                else:
                    # Genuine TODO — the topic needs a guide; we just
                    # haven't written it yet. Don't mislabel long/short
                    # division or fractions as "recall speed work".
                    self._coming_soon_card(cards, col, padx, gid)

    # ============================================================= cards

    def _is_locked(self, gid: str) -> bool:
        req = UNLOCK_REQUIREMENTS.get(gid)
        return bool(req and not self._as.has(req))

    def _tutorial_card(self, parent, col, padx, gid, locked=False):
        mod = TUTORIAL_REGISTRY[gid]
        title = getattr(mod, "TITLE", GAME_NAMES.get(gid, gid))
        lead  = getattr(mod, "LEAD", "")
        slides = getattr(mod, "SLIDES", [])
        examples = getattr(mod, "EXAMPLES", [{}])

        if locked:
            self._locked_card(parent, col, padx, gid)
            return

        card = tk.Frame(parent, bg=CARD_BG,
                        highlightbackground=CARD_BORDER, highlightthickness=1,
                        cursor="hand2")
        card.grid(row=0, column=col, sticky="nsew", padx=padx)

        inner = tk.Frame(card, bg=CARD_BG, padx=22, pady=22)
        inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(inner, text="Guide",
                 font=("Helvetica", 9, "bold"),
                 bg="#eef2ff", fg=ACCENT,
                 padx=10, pady=3).pack(anchor="w", pady=(0, 12))

        tk.Label(inner, text=GAME_NAMES.get(gid, gid),
                 font=("Helvetica", 15, "bold"),
                 bg=CARD_BG, fg=INK).pack(anchor="w")

        blurb = lead or f"{len(slides)}-step walkthrough."
        tk.Label(inner, text=blurb,
                 font=("Helvetica", 10), bg=CARD_BG, fg=MUTED,
                 justify="left", wraplength=260).pack(anchor="w", pady=(6, 18))

        meta = f"{len(slides)} slides"
        if len(examples) > 1:
            meta += f"   ·   {len(examples)} examples"
        tk.Label(inner, text=meta,
                 font=("Helvetica", 9), bg=CARD_BG, fg=DIM).pack(anchor="w",
                                                                 pady=(0, 10))

        tk.Button(
            inner, text="Open guide  →",
            font=("Helvetica", 10, "bold"),
            bg=ACCENT, fg="white",
            relief="flat", bd=0, padx=14, pady=6, cursor="hand2",
            activebackground="#4338ca", activeforeground="white",
            command=lambda g=gid: self._launch_tutorial(g),
        ).pack(anchor="w")

        for w in (card, inner):
            w.bind("<Button-1>", lambda e, g=gid: self._launch_tutorial(g))

    def _locked_card(self, parent, col, padx, gid):
        req_id = UNLOCK_REQUIREMENTS.get(gid, "")
        req    = ACHIEVEMENTS_BY_ID.get(req_id, {})
        req_name = req.get("name", "a previous achievement")

        card = tk.Frame(parent, bg=SOFT,
                        highlightbackground=CARD_BORDER, highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew", padx=padx)

        inner = tk.Frame(card, bg=SOFT, padx=22, pady=22)
        inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(inner, text="🔒  Locked",
                 font=("Helvetica", 9, "bold"),
                 bg=FAINT, fg="#475569",
                 padx=10, pady=3).pack(anchor="w", pady=(0, 12))

        tk.Label(inner, text=GAME_NAMES.get(gid, gid),
                 font=("Helvetica", 15, "bold"),
                 bg=SOFT, fg="#475569").pack(anchor="w")

        tk.Label(inner,
                 text=f"Unlocks with: {req_name}",
                 font=("Helvetica", 10), bg=SOFT, fg=MUTED,
                 justify="left", wraplength=260).pack(anchor="w",
                                                     pady=(6, 18))

        tk.Label(inner, text="Play the game first, then the guide opens.",
                 font=("Helvetica", 9), bg=SOFT, fg=DIM,
                 justify="left", wraplength=260).pack(anchor="w")

    def _not_needed_card(self, parent, col, padx, gid):
        """
        Placeholder for modes that will never have a tutorial by design
        (currently just mult_basic — single-digit × single-digit memorisation).
        """
        card = tk.Frame(parent, bg=SOFT,
                        highlightbackground=CARD_BORDER, highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew", padx=padx)

        inner = tk.Frame(card, bg=SOFT, padx=22, pady=22)
        inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(inner, text="No guide needed",
                 font=("Helvetica", 9, "bold"),
                 bg="#f1f5f9", fg=DIM,
                 padx=10, pady=3).pack(anchor="w", pady=(0, 12))

        tk.Label(inner, text=GAME_NAMES.get(gid, gid),
                 font=("Helvetica", 15, "bold"),
                 bg=SOFT, fg="#475569").pack(anchor="w")

        tk.Label(inner,
                 text=("This mode is about recall speed, "
                       "so there's nothing to walk through. Just play."),
                 font=("Helvetica", 10), bg=SOFT, fg=MUTED,
                 justify="left", wraplength=260).pack(anchor="w", pady=(6, 0))

    def _coming_soon_card(self, parent, col, padx, gid):
        """
        Placeholder for modes that should have a tutorial but don't yet.
        Used for everything not in TUTORIAL_REGISTRY and not in
        INTENTIONAL_NO_GUIDE. Don't claim there's "nothing to walk
        through" — these topics (short division, long division,
        fractions, conversions) all warrant proper guides.
        """
        card = tk.Frame(parent, bg=SOFT,
                        highlightbackground=CARD_BORDER, highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew", padx=padx)

        inner = tk.Frame(card, bg=SOFT, padx=22, pady=22)
        inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(inner, text="Guide coming soon",
                 font=("Helvetica", 9, "bold"),
                 bg="#fef3c7", fg="#92400e",
                 padx=10, pady=3).pack(anchor="w", pady=(0, 12))

        tk.Label(inner, text=GAME_NAMES.get(gid, gid),
                 font=("Helvetica", 15, "bold"),
                 bg=SOFT, fg="#475569").pack(anchor="w")

        tk.Label(inner,
                 text=("A step-by-step walkthrough for this mode is "
                       "in the works. Play the game in the meantime."),
                 font=("Helvetica", 10), bg=SOFT, fg=MUTED,
                 justify="left", wraplength=260).pack(anchor="w", pady=(6, 0))

    # ============================================================ navigation

    def _launch_tutorial(self, gid: str):
        mod = TUTORIAL_REGISTRY.get(gid)
        if mod is None:
            return

        # Clear the current panel contents and swap in a SlideshowFrame
        for w in self.parent.winfo_children():
            w.destroy()

        SlideshowFrame(
            self.parent,
            back_callback = self._return_to_panel,
            title         = getattr(mod, "TITLE", GAME_NAMES.get(gid, gid)),
            lead          = getattr(mod, "LEAD", ""),
            slides        = getattr(mod, "SLIDES", []),
            examples      = getattr(mod, "EXAMPLES", [{}]),
        )

    def _return_to_panel(self):
        for w in self.parent.winfo_children():
            w.destroy()
        self._build()
