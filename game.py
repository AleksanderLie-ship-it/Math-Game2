"""
game.py
-------
Main entry point. Shows the game-selection menu and launches mini-games.

To add a new game:
  1. Create games/your_game.py subclassing BaseGame
  2. Import it below and add it to CATEGORIES
"""

import tkinter as tk
from tkinter import ttk

from games.mult_basic         import MultiplicationBasic
from games.mult_intermediate  import MultiplicationIntermediate
from games.mult_advanced      import MultiplicationAdvanced
from games.div_basic          import DivisionBasic
from games.div_intermediate   import DivisionIntermediate
from games.div_advanced       import DivisionAdvanced
from games.practice_missed    import PracticeMissed
from games.missed_store       import store as missed_store


# ── Game registry ──────────────────────────────────────────────────────────────

CATEGORIES = [
    {
        "label": "Multiplication",
        "games": [
            {
                "name":     "Beginner",
                "desc":     "Times tables 1–10.\nBuild speed and confidence.",
                "badge":    "Beginner",
                "badge_bg": "#f0fdf4",
                "badge_fg": "#15803d",
                "cls":      MultiplicationBasic,
            },
            {
                "name":     "Intermediate",
                "desc":     "Two-digit and mixed problems.\nLike 34 × 7 or 34 × 78.",
                "badge":    "Intermediate",
                "badge_bg": "#fffbeb",
                "badge_fg": "#b45309",
                "cls":      MultiplicationIntermediate,
            },
            {
                "name":     "Advanced",
                "desc":     "Three-digit × two-digit.\nLike 134 × 78.",
                "badge":    "Advanced",
                "badge_bg": "#fef2f2",
                "badge_fg": "#b91c1c",
                "cls":      MultiplicationAdvanced,
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
            },
            {
                "name":     "Intermediate",
                "desc":     "Larger dividends.\nAlways whole-number answers.",
                "badge":    "Intermediate",
                "badge_bg": "#fffbeb",
                "badge_fg": "#b45309",
                "cls":      DivisionIntermediate,
            },
            {
                "name":     "Advanced",
                "desc":     "Large numbers + decimal answers.\nLike 13 ÷ 2 = 6.5.",
                "badge":    "Advanced",
                "badge_bg": "#fef2f2",
                "badge_fg": "#b91c1c",
                "cls":      DivisionAdvanced,
            },
        ],
    },
]


# ── App controller ─────────────────────────────────────────────────────────────

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Math Practice")
        self.root.geometry("960x660")
        self.root.minsize(700, 480)
        self.root.configure(bg="#f8fafc")
        self._apply_styles()
        self._current = None
        self.show_menu()

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

        def _frame_resized(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _canvas_resized(e):
            canvas.itemconfig(win_id, width=e.width)

        inner.bind("<Configure>", _frame_resized)
        canvas.bind("<Configure>", _canvas_resized)

        def _on_wheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_wheel)
        canvas.bind_all("<Button-4>",   lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>",   lambda e: canvas.yview_scroll( 1, "units"))

        # ── Content ───────────────────────────────────────────────────────────
        hdr = tk.Frame(inner, bg="#f8fafc", padx=48, pady=36)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="Math Practice",
                 font=("Helvetica", 32, "bold"),
                 bg="#f8fafc", fg="#0f172a").pack(anchor="w")
        tk.Label(hdr, text="Choose a game to start practising.",
                 font=("Helvetica", 13), bg="#f8fafc", fg="#475569").pack(anchor="w", pady=(4, 0))

        for cat in CATEGORIES:
            self._category_row(inner, cat)

        self._review_row(inner)           # Practice Missed section at bottom

        tk.Frame(inner, bg="#f8fafc", height=36).pack()

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
            self._game_card(cards, game, col, padx=(0, 16) if col < n - 1 else 0)

    def _review_row(self, parent):
        """The special Practice Missed card — count updates each time menu loads."""
        section = tk.Frame(parent, bg="#f8fafc", padx=48)
        section.pack(fill=tk.X, pady=(0, 28))

        tk.Label(section, text="Review",
                 font=("Helvetica", 13, "bold"),
                 bg="#f8fafc", fg="#94a3b8").pack(anchor="w", pady=(0, 12))

        cards = tk.Frame(section, bg="#f8fafc")
        cards.pack(fill=tk.X)
        for col in range(3):
            cards.columnconfigure(col, weight=1)

        count   = missed_store.count()
        enabled = count > 0

        card_bg  = "white"    if enabled else "#f1f5f9"
        name_fg  = "#0f172a"  if enabled else "#94a3b8"
        desc_fg  = "#64748b"  if enabled else "#94a3b8"
        desc     = (f"{count} question{'s' if count != 1 else ''} waiting for review."
                    if enabled else "No missed questions yet — keep playing!")

        card = tk.Frame(cards, bg=card_bg,
                        highlightbackground="#e2e8f0", highlightthickness=1,
                        cursor="hand2" if enabled else "arrow")
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        inner = tk.Frame(card, bg=card_bg, padx=22, pady=22)
        inner.pack(fill=tk.BOTH, expand=True)

        # Badge
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
            inner, text="Start Review  →",
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

    def _game_card(self, parent, game, col, padx):
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

        tk.Button(inner, text="Play  →",
                  font=("Helvetica", 10, "bold"),
                  bg="#0f172a", fg="white", relief="flat", bd=0,
                  padx=14, pady=6, cursor="hand2",
                  activebackground="#1e293b", activeforeground="white",
                  command=lambda g=game: self._launch(g)).pack(anchor="w")

        for w in (card, inner):
            w.bind("<Button-1>", lambda e, g=game: self._launch(g))

    # ----------------------------------------------------------------- launch

    def _launch(self, game):
        self._clear()
        frame = tk.Frame(self.root, bg="#f8fafc")
        frame.pack(fill=tk.BOTH, expand=True)
        self._current = frame
        game["cls"](frame, back_callback=self.show_menu)

    def _launch_practice(self):
        self._clear()
        frame = tk.Frame(self.root, bg="#f8fafc")
        frame.pack(fill=tk.BOTH, expand=True)
        self._current = frame
        PracticeMissed(frame, back_callback=self.show_menu)

    def _clear(self):
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            try:
                self.root.unbind_all(seq)
            except Exception:
                pass
        if self._current is not None:
            self._current.destroy()
            self._current = None


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.title("Math Practice")
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
