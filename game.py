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
from games.achievements_store import store as ach_store
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
        self.root.title("Math Practice")
        self.root.geometry("960x680")
        self.root.minsize(700, 480)
        self.root.configure(bg="#f8fafc")
        self._apply_styles()
        self._current      = None
        self._scroll_target = None   # canvas currently receiving mousewheel

        # Persistent root-level mousewheel — never removed, just re-routed
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

        self._scroll_target = canvas   # route root-level wheel to this canvas

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(inner, bg="#f8fafc", padx=48, pady=32)
        hdr.pack(fill=tk.X)

        # Left: title
        title_col = tk.Frame(hdr, bg="#f8fafc")
        title_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(title_col, text="Math Practice",
                 font=("Helvetica", 32, "bold"),
                 bg="#f8fafc", fg="#0f172a").pack(anchor="w")
        tk.Label(title_col, text="Choose a game to start practising.",
                 font=("Helvetica", 13), bg="#f8fafc", fg="#475569").pack(anchor="w", pady=(4, 0))

        # Right: points + achievements button
        right_col = tk.Frame(hdr, bg="#f8fafc")
        right_col.pack(side=tk.RIGHT, anchor="ne")

        pts = ach_store.get_points()
        earned_count = len(ach_store.get_earned())
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
            padx = (0, 16) if col < n - 1 else 0
            game_id = game.get("game_id", "")
            unlock  = UNLOCK_REQUIREMENTS.get(game_id)
            locked  = bool(unlock and not ach_store.has(unlock))
            self._game_card(cards, game, col, padx, locked=locked, unlock_req=unlock)

    def _review_row(self, parent):
        """Practice Missed card — count updates each time menu loads."""
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

        # Badge row with lock
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

        # Unlock requirement text
        req_name    = ""
        req_desc    = ""
        req_game    = ""
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
        tk.Label(unlock_frame,
                 text=unlock_label,
                 font=("Helvetica", 9), bg="#e2e8f0", fg="#64748b",
                 padx=10, pady=6, wraplength=200, justify="left").pack(anchor="w")

        def _show_lock_info(e=None):
            from tkinter import messagebox
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
        """Open the Trophy Room window — uses tk.Text for reliable scrolling."""
        root = self.root
        root.update_idletasks()
        cx = root.winfo_x() + root.winfo_width()  // 2
        cy = root.winfo_y() + root.winfo_height() // 2

        win = tk.Toplevel(root)
        win.title("Trophy Room")
        win.configure(bg="#f8fafc")
        win.geometry(f"640x580+{cx - 320}+{cy - 290}")
        win.resizable(True, True)

        # ── Header bar ────────────────────────────────────────────────────────
        hdr = tk.Frame(win, bg="#0f172a", padx=24, pady=16)
        hdr.pack(fill=tk.X)

        tk.Label(hdr, text="🏆  Trophy Room",
                 font=("Helvetica", 16, "bold"),
                 bg="#0f172a", fg="white").pack(side=tk.LEFT)

        pts          = ach_store.get_points()
        earned_count = len(ach_store.get_earned())
        total_count  = len(ACHIEVEMENTS)
        tk.Label(hdr, text=f"⭐ {pts:,} pts  ·  {earned_count}/{total_count}",
                 font=("Helvetica", 11), bg="#0f172a", fg="#f59e0b").pack(side=tk.RIGHT)

        # ── Scrollable body via tk.Text ───────────────────────────────────────
        body_outer = tk.Frame(win, bg="#f8fafc")
        body_outer.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(body_outer, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        txt = tk.Text(
            body_outer,
            bg="#f8fafc", relief="flat", bd=0,
            cursor="arrow", wrap="word",
            font=("Helvetica", 11),
            yscrollcommand=vsb.set,
            highlightthickness=0,
            state="normal",
        )
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=txt.yview)

        # Route wheel to this text widget (yview_scroll interface is compatible)
        prev_target      = self._scroll_target
        self._scroll_target = txt

        def _on_trophy_close():
            self._scroll_target = prev_target
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", _on_trophy_close)

        # ── Define text tags ──────────────────────────────────────────────────
        txt.tag_configure("spacer",
                          font=("Helvetica", 4))
        txt.tag_configure("cat",
                          font=("Helvetica", 10, "bold"),
                          foreground="#94a3b8",
                          spacing1=14, spacing3=4,
                          lmargin1=24, lmargin2=24)
        txt.tag_configure("divider",
                          font=("Helvetica", 1),
                          foreground="#e2e8f0",
                          background="#e2e8f0",
                          spacing3=6)
        txt.tag_configure("subcat",
                          font=("Helvetica", 9, "bold"),
                          foreground="#64748b",
                          spacing1=8, spacing3=2,
                          lmargin1=40, lmargin2=40)
        txt.tag_configure("ach_name_earned",
                          font=("Helvetica", 11, "bold"),
                          foreground="#0f172a",
                          background="#f0fdf4",
                          spacing1=6,
                          lmargin1=28, lmargin2=28)
        txt.tag_configure("ach_name_locked",
                          font=("Helvetica", 11),
                          foreground="#94a3b8",
                          spacing1=6,
                          lmargin1=28, lmargin2=28)
        txt.tag_configure("ach_name_earned_indent",
                          font=("Helvetica", 11, "bold"),
                          foreground="#0f172a",
                          background="#f0fdf4",
                          spacing1=6,
                          lmargin1=44, lmargin2=44)
        txt.tag_configure("ach_name_locked_indent",
                          font=("Helvetica", 11),
                          foreground="#94a3b8",
                          spacing1=6,
                          lmargin1=44, lmargin2=44)
        txt.tag_configure("ach_desc_earned",
                          font=("Helvetica", 9),
                          foreground="#64748b",
                          background="#f0fdf4",
                          spacing3=6,
                          lmargin1=28, lmargin2=28)
        txt.tag_configure("ach_desc_locked",
                          font=("Helvetica", 9),
                          foreground="#cbd5e1",
                          spacing3=6,
                          lmargin1=28, lmargin2=28)
        txt.tag_configure("ach_desc_earned_indent",
                          font=("Helvetica", 9),
                          foreground="#64748b",
                          background="#f0fdf4",
                          spacing3=6,
                          lmargin1=44, lmargin2=44)
        txt.tag_configure("ach_desc_locked_indent",
                          font=("Helvetica", 9),
                          foreground="#cbd5e1",
                          spacing3=6,
                          lmargin1=44, lmargin2=44)

        # ── Insert content ────────────────────────────────────────────────────
        earned_set = set(ach_store.get_earned())

        cat_map = {c: [] for c in CATEGORY_ORDER}
        for ach in ACHIEVEMENTS:
            cat_map.setdefault(ach.get("category", "Other"), []).append(ach)

        def _insert_ach(a, indent=False):
            earned = a["id"] in earned_set
            hidden = a.get("hidden", False) and not earned
            icon   = a["icon"] if not hidden else "❓"
            name   = a["name"] if not hidden else "???"
            desc   = a["desc"] if not hidden else "Keep playing to discover this one."
            pts_s  = f"+{a['points']} pts"
            check  = "  ✓" if earned else ""

            if indent:
                name_tag = "ach_name_earned_indent"  if earned else "ach_name_locked_indent"
                desc_tag = "ach_desc_earned_indent"  if earned else "ach_desc_locked_indent"
            else:
                name_tag = "ach_name_earned" if earned else "ach_name_locked"
                desc_tag = "ach_desc_earned" if earned else "ach_desc_locked"

            txt.insert(tk.END, f"{icon}  {name}  {pts_s}{check}\n", name_tag)
            txt.insert(tk.END, f"{desc}\n", desc_tag)

        from collections import defaultdict

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

        # ── Close button ──────────────────────────────────────────────────────
        tk.Button(win, text="Close", command=_on_trophy_close,
                  font=("Helvetica", 11), bg="white", fg="#475569",
                  relief="solid", bd=1, padx=20, pady=6, cursor="hand2").pack(pady=10)

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
        self._scroll_target = None   # stop routing wheel while transitioning
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
