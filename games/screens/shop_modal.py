"""
games.screens.shop_modal
------------------------
Shop modal + SHOP_ITEMS catalogue. Carved out of game.py in v0.9.0.

Public API:
    SHOP_ITEMS                 — registry of buyable cosmetics
    show_shop_modal(app)       — open the modal

Reads from `app`: `.root`, `._ach_store`, `._purchases_store`.

SHOP_ITEMS schema (each entry):
    id          — stable string key, persisted in purchases.json
    name        — display name in the shop card
    category    — group label (Theme / Avatar / Frame …)
    icon        — single emoji for the card hero glyph
    desc        — 1–2 sentence pitch
    price       — cost in achievement points
    on_buy      — optional callable(app) invoked AFTER `purchase()` succeeds.
                  Use this for side effects (e.g. Dark Mode flips the
                  settings 'theme' default to "dark" so the toggle starts
                  on, but the user is free to flip it off in Settings).
    unlock_req  — (optional) achievement id that must be earned before
                  the item can be bought. v0.7.13.2 introduction.
"""

import tkinter as tk
from tkinter import messagebox

from ..theme import theme
from ..achievements import ACHIEVEMENTS_BY_ID


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


def show_shop_modal(app):
    """Modal listing SHOP_ITEMS with buy / owned state per entry."""
    T = theme()
    root = app.root
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
        hdr, text=f"⭐ {app._ach_store.get_points():,} pts",
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
        balance_lbl.config(text=f"⭐ {app._ach_store.get_points():,} pts")

    def _render_item(item):
        owned = app._purchases_store.has(item["id"])
        cost  = item["price"]
        can_afford = app._ach_store.get_points() >= cost

        # Achievement-gate (v0.7.13.2). When `unlock_req` names an
        # achievement id, the item can't be bought until that
        # achievement is earned — even if the pupil has the points.
        # Surfaces the requirement so the user knows how to progress.
        req_id = item.get("unlock_req")
        req_met = (req_id is None) or app._ach_store.has(req_id)
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
        if app._purchases_store.has(item["id"]):
            return
        # Defensive: re-check the achievement gate at click time so a
        # stale UI can't be exploited (e.g. user opened shop, earned
        # nothing, but unlock state somehow flipped). The shop modal
        # rebuilds after every purchase so this normally won't fire.
        req_id = item.get("unlock_req")
        if req_id and not app._ach_store.has(req_id):
            req_ach = ACHIEVEMENTS_BY_ID.get(req_id, {})
            messagebox.showwarning(
                "Locked",
                f"This item requires the '{req_ach.get('name', req_id)}' "
                f"achievement first.",
                parent=win,
            )
            return
        if not app._ach_store.spend(cost):
            messagebox.showwarning(
                "Not enough points",
                f"You need {cost:,} points to buy {item['name']}, "
                f"but only have {app._ach_store.get_points():,}.",
                parent=win,
            )
            return
        app._purchases_store.purchase(item["id"])
        on_buy = item.get("on_buy")
        if callable(on_buy):
            try:
                on_buy(app)
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
