"""
games.screens.difficulty_screen
-------------------------------
Difficulty-selection screen + matrix-theme variant + tile/lock-hint
helpers. Carved out of game.py in v0.9.0 second decomposition pass.

Public API:
    show_difficulty(app, family)
    show_difficulty_matrix(app, family)

Internal helpers:
    _difficulty_tile, _render_lock_hint

Reads from `app`: `.root`, `._clear()`, `._current`, `._current_family`,
`._tile_images`, `._matrix_rains`, `._scroll_target`,
`._install_wheel_handler()`, `._ach_store`, `.show_menu()`,
`._launch(family, difficulty)`.
"""

import tkinter as tk
from tkinter import messagebox

from ..theme import theme, theme_name as _theme_name
from ..achievements import ACHIEVEMENTS_BY_ID, GAME_NAMES, UNLOCK_REQUIREMENTS
from ..assets_loader import game_tile_image, tier_glyph


def _tiers():
    """Lazy import _DIFFICULTY_TIERS from game.py (avoids circular imp)."""
    import game
    return game._DIFFICULTY_TIERS


def show_difficulty(app, family):
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
    app._clear()
    app._current_family = family
    app._tile_images    = []   # release prior refs

    # v0.8.2: matrix theme branches into _show_difficulty_matrix
    # which uses the same full-canvas-rain pattern as
    # _show_menu_matrix (rain everywhere not covered by content).
    if _theme_name() == "matrix":
        show_difficulty_matrix(app, family)
        return

    outer = tk.Frame(app.root, bg=T["bg"])
    outer.pack(fill=tk.BOTH, expand=True)
    app._current = outer

    # Top bar — back button only
    top = tk.Frame(outer, bg=T["bg"], padx=24, pady=10)
    top.pack(fill=tk.X)
    tk.Button(top, text="← Menu",
              font=("Helvetica", 10), bg=T["bg"], fg=T["muted"],
              relief="flat", bd=0, cursor="hand2",
              activebackground="#f8fafc", activeforeground="#0f172a",
              command=app.show_menu).pack(side=tk.LEFT)

    # Header — family glyph + label + tagline
    hdr = tk.Frame(outer, bg=T["bg"], padx=48, pady=18)
    hdr.pack(fill=tk.X)

    glyph_box = tk.Frame(hdr, bg=family["accent"], padx=14, pady=8)
    glyph_box.pack(side=tk.LEFT)
    tk.Label(glyph_box, text=family["glyph"],
             font=("Helvetica", 28, "bold"),
             bg=family["accent"], fg="white").pack()

    title_col = tk.Frame(hdr, bg=T["bg"])
    # No fill=X / expand=True — let title_col size naturally so the
    # surrounding rain canvas is visible to the right of the header.
    title_col.pack(side=tk.LEFT, padx=(16, 0))
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
        locked = bool(unlock and not app._ach_store.has(unlock))
        _difficulty_tile(app, cards, family, diff, col, padx,
                         locked=locked, unlock_req=unlock)


# ============================================================ matrix difficulty page

def show_difficulty_matrix(app, family):
    """Difficulty-selection screen, matrix theme.

    Same trick as _show_menu_matrix: one full-window rain Canvas,
    every section (back button, header, 3 difficulty cards) mounted
    as a canvas window. Rain visible everywhere not covered.
    """
    T = theme()

    outer = tk.Frame(app.root, bg=T["bg"])
    outer.pack(fill=tk.BOTH, expand=True)
    app._current = outer

    rain_canvas = tk.Canvas(outer, bg=T["bg"], highlightthickness=0, bd=0)
    rain_canvas.pack(fill=tk.BOTH, expand=True)
    app._scroll_target = None

    app._matrix_rains = []
    try:
        from ..effects_matrix_rain import MatrixRain
        mr = MatrixRain(rain_canvas)
        mr.start()
        app._matrix_rains.append(mr)
    except Exception:
        pass

    app._install_wheel_handler()

    PADX = 48

    # ── Back button (top-left, separate widget) ──
    back_btn = tk.Button(rain_canvas, text="← Menu",
                         font=("Helvetica", 10), bg=T["bg"], fg=T["muted"],
                         relief="flat", bd=0, cursor="hand2",
                         activebackground=T["bg"], activeforeground=T["ink"],
                         command=app.show_menu)

    # ── Header block (family glyph + title + tagline + "Choose…" line) ──
    hdr = tk.Frame(rain_canvas, bg=T["bg"])
    glyph_box = tk.Frame(hdr, bg=family["accent"], padx=14, pady=8)
    glyph_box.pack(side=tk.LEFT)
    tk.Label(glyph_box, text=family["glyph"],
             font=("Helvetica", 28, "bold"),
             bg=family["accent"], fg="white").pack()

    title_col = tk.Frame(hdr, bg=T["bg"])
    # No fill=X / expand=True — let title_col size naturally so the
    # surrounding rain canvas is visible to the right of the header.
    title_col.pack(side=tk.LEFT, padx=(16, 0))
    tk.Label(title_col, text=family["label"],
             font=("Helvetica", 26, "bold"),
             bg=T["bg"], fg=T["ink"]).pack(anchor="w")
    tk.Label(title_col, text=family["tagline"],
             font=("Helvetica", 11),
             bg=T["bg"], fg=T["muted"]).pack(anchor="w", pady=(4, 0))
    tk.Label(title_col, text="Choose a difficulty.",
             font=("Helvetica", 11, "bold"),
             bg=T["bg"], fg=T["muted"]).pack(anchor="w", pady=(8, 0))

    # ── 3 difficulty cards (gridded into a Frame, mounted as window) ──
    cards = tk.Frame(rain_canvas, bg=T["bg"])
    for col in range(3):
        cards.columnconfigure(col, weight=1)
    for col, diff in enumerate(family["difficulties"]):
        padx_arg = (0, 16) if col < len(family["difficulties"]) - 1 else 0
        unlock = UNLOCK_REQUIREMENTS.get(diff["game_id"])
        locked = bool(unlock and not app._ach_store.has(unlock))
        _difficulty_tile(app, cards, family, diff, col, padx_arg,
                         locked=locked, unlock_req=unlock)

    # ── Mount on the rain canvas ──
    back_id = rain_canvas.create_window(0, 0, anchor="nw", window=back_btn)
    hdr_id  = rain_canvas.create_window(0, 0, anchor="nw", window=hdr)
    cards_id = rain_canvas.create_window(0, 0, anchor="nw", window=cards)

    def _layout(_e=None):
        try:
            rain_canvas.update_idletasks()
            cw = rain_canvas.winfo_width()

            # Back button at top-left
            rain_canvas.coords(back_id, 24, 14)
            rain_canvas.update_idletasks()

            # Header at PADX, y=60 — natural width (no fill) so rain
            # is visible to the right of the family glyph + title block.
            y = 60
            rain_canvas.coords(hdr_id, PADX, y)
            rain_canvas.update_idletasks()
            y += hdr.winfo_reqheight() + 50

            # 3 difficulty cards row
            rain_canvas.coords(cards_id, PADX, y)
            rain_canvas.itemconfig(cards_id, width=cw - 2 * PADX)
            rain_canvas.update_idletasks()
        except Exception:
            pass

    rain_canvas.bind("<Configure>", _layout)
    rain_canvas.after(20, _layout)


def _difficulty_tile(app, parent, family, diff, col, padx,
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
    _DIFFICULTY_TIERS = _tiers()
    # Tier metadata (badge colours match the existing per-difficulty palette).
    tier = next((t for t in _DIFFICULTY_TIERS if t["key"] == diff["key"]), _DIFFICULTY_TIERS[0])
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
        app._tile_images.append(img)   # keep ref alive
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
        _render_lock_hint(inner, unlock_req)
        return

    tk.Button(
        inner, text="Play  →",
        font=("Helvetica", 10, "bold"),
        bg=T["btn_primary_bg"], fg=T["btn_primary_fg"], relief="flat", bd=0,
        padx=14, pady=6, cursor="hand2",
        activebackground="#1e293b", activeforeground="white",
        command=lambda f=family, d=diff: app._launch(f, d),
    ).pack(anchor="w")

    for w in (card, asset_slot, inner):
        w.bind("<Button-1>",
               lambda e, f=family, d=diff: app._launch(f, d))


def _render_lock_hint(parent, unlock_req):
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
