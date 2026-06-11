"""
games.screens.trophy_room
-------------------------
Trophy Room window. Carved out of game.py in v0.9.0.

Public API:
    show_trophy_room(app)

Reads from `app`: `.root`, `._ach_store`, `._scroll_target`. Manages the
mousewheel scroll-target swap on open/close so the wheel handler routes
to the trophy text widget while it's visible.
"""

import tkinter as tk
from tkinter import ttk
from collections import defaultdict

from ..theme import theme
from ..achievements import (
    ACHIEVEMENTS, CATEGORY_ORDER, GAME_NAMES, GAME_IDS,
)


def show_trophy_room(app):
    """Open the Trophy Room window."""
    T = theme()
    root = app.root
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

    pts            = app._ach_store.get_points()
    earned_count   = len(app._ach_store.get_earned())
    total_count    = len(ACHIEVEMENTS)
    spent          = app._ach_store.get_total_spent()
    lifetime       = app._ach_store.get_lifetime_earned()

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

    prev_target         = app._scroll_target
    app._scroll_target  = txt

    def _on_trophy_close():
        app._scroll_target = prev_target
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", _on_trophy_close)

    # Text tags
    # v0.8.2: tag colors come from theme tokens so the Trophy Room
    # follows the active theme. Earned rows use good_bg (faint
    # success surface), locked rows use bg (recede into page).
    txt.tag_configure("cat",
                      font=("Helvetica", 10, "bold"), foreground=T["dim"],
                      spacing1=14, spacing3=4, lmargin1=24, lmargin2=24)
    txt.tag_configure("divider",
                      font=("Helvetica", 1), foreground=T["card_border"],
                      background=T["card_border"], spacing3=6)
    txt.tag_configure("subcat",
                      font=("Helvetica", 9, "bold"), foreground=T["muted"],
                      spacing1=8, spacing3=2, lmargin1=40, lmargin2=40)
    for suffix, fg, bg in [
        ("earned",        T["ink"], T["good_bg"]),
        ("locked",        T["dim"], T["bg"]),
        ("earned_indent", T["ink"], T["good_bg"]),
        ("locked_indent", T["dim"], T["bg"]),
    ]:
        bold   = "bold" if "earned" in suffix else "normal"
        indent = 44 if "indent" in suffix else 28
        txt.tag_configure(f"name_{suffix}",
                          font=("Helvetica", 11, bold), foreground=fg,
                          background=bg, spacing1=6,
                          lmargin1=indent, lmargin2=indent)
        txt.tag_configure(f"desc_{suffix}",
                          font=("Helvetica", 9),
                          foreground=T["muted"] if "earned" in suffix else T["faint"],
                          background=bg, spacing3=6,
                          lmargin1=indent, lmargin2=indent)

    earned_set = set(app._ach_store.get_earned())
    cat_map    = {c: [] for c in CATEGORY_ORDER}
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
