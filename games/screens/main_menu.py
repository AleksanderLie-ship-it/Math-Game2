"""
games.screens.main_menu
-----------------------
Main menu screen + matrix-theme variant + family/tools/shop tile builders.
Carved out of game.py in v0.9.0 second decomposition pass.

Public API:
    show_menu(app)
    show_menu_matrix(app, outer)

Internal helpers (called from inside this module only):
    _family_tile, _tools_row, _build_tools_tiles, _shop_tile

Reads from `app`: `.root`, `._clear()`, `._current`, `._current_family`,
`._matrix_rains`, `._scroll_target`, `._install_wheel_handler()`,
`._tile_images`, `._profile_name`, `._ach_store`, `._missed_store`,
`._sessions_store`, `._purchases_store`, `.show_profiles()`,
`._show_settings()`, `._show_achievements()`, `.show_difficulty(f)`,
`._launch_practice()`, `._launch_stats()`, `._launch_tutorials()`,
`._show_shop()`.
"""

import tkinter as tk
from tkinter import ttk

from ..theme import theme, theme_name as _theme_name
from ..achievements import ACHIEVEMENTS, UNLOCK_REQUIREMENTS
from ..tutorials import TUTORIAL_REGISTRY
from .shop_modal import SHOP_ITEMS


def _version():
    """Lazy import to avoid a circular dependency with game.py."""
    from game import __version__
    return __version__


def _registry():
    """Lazy import of GAMES + _DIFFICULTY_TIERS from game.py.

    These live at the top of game.py and are referenced by this module
    only at render time — late binding sidesteps the circular import.
    """
    import game
    return game.GAMES, game._DIFFICULTY_TIERS


def show_menu(app):
    T = theme()
    app._clear()
    app._current_family = None

    outer = tk.Frame(app.root, bg=T["bg"])
    outer.pack(fill=tk.BOTH, expand=True)
    app._current = outer

    # v0.8.2: matrix theme uses a dedicated full-window rain canvas
    # menu where every section is placed via canvas.create_window.
    # Rain shows everywhere not covered by a section — the
    # cinematic curtain look. Non-matrix uses the regular pack
    # layout below.
    if _theme_name() == "matrix":
        show_menu_matrix(app, outer)
        return

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

    # Matrix-mode trick: `inner` is a Canvas (not a Frame) so the
    # canvas surface is visible in the gaps between pack-managed
    # children — that's where the rain becomes visible. tk.Canvas
    # accepts pack-managed children just like tk.Frame does.
    is_matrix = (_theme_name() == "matrix")
    if is_matrix:
        inner = tk.Canvas(canvas, bg=T["bg"], highlightthickness=0, bd=0)
    else:
        inner = tk.Frame(canvas, bg=T["bg"])
    win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    # ── Matrix rain on the inner-canvas surface (v0.8.1) ─────────────
    # Visible everywhere the menu's pack layout doesn't cover —
    # between header and games row, between rows of cards, around
    # the title block, in the area below the footer. Self-cleaning:
    # `_clear()` calls `stop()` so the after-loop never tries to
    # redraw a destroyed canvas.
    app._matrix_rains = []
    if is_matrix:
        try:
            from ..effects_matrix_rain import MatrixRain
            _r = MatrixRain(inner)
            _r.start()
            app._matrix_rains.append(_r)
        except Exception:
            pass

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

    app._scroll_target = canvas
    # Reclaim the root mousewheel binding from whichever subscreen we
    # just returned from; otherwise scrolling only works over the
    # scrollbar itself.
    app._install_wheel_handler()

    # ── Header ────────────────────────────────────────────────────────────
    # v0.8.1.4: hdr is a Canvas in matrix mode so rain shows
    # in the dead zone between title_col (LEFT) and right_col (RIGHT)
    # AND below the right_col block (Trophy Room button is short
    # vertically — leaves bg space below it). Frame otherwise.
    if is_matrix:
        hdr = tk.Canvas(inner, bg=T["bg"], highlightthickness=0,
                        bd=0, height=140)
        try:
            from ..effects_matrix_rain import MatrixRain
            _r = MatrixRain(hdr)
            _r.start()
            app._matrix_rains.append(_r)
        except Exception:
            pass
    else:
        hdr = tk.Frame(inner, bg=T["bg"], padx=48, pady=32)
    # 70px rain band above the title (only visible in matrix mode).
    hdr.pack(fill=tk.X, pady=(70 if is_matrix else 0, 0))

    # Left: title + profile
    title_col = tk.Frame(hdr, bg=T["bg"])
    # In matrix mode hdr is a Canvas with no internal padx/pady,
    # so children supply the spacing themselves.
    _pad_l = (48, 0) if is_matrix else 0
    _pad_v = 32 if is_matrix else 0
    title_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                   padx=_pad_l, pady=_pad_v)

    tk.Label(title_col, text="Math Practice",
             font=("Helvetica", 32, "bold"),
             bg=T["bg"], fg=T["ink"]).pack(anchor="w")
    tk.Label(title_col, text="Choose a game to start practising.",
             font=("Helvetica", 13), bg=T["bg"], fg=T["muted"]).pack(anchor="w", pady=(4, 0))

    # Profile pill + switch button
    profile_row = tk.Frame(title_col, bg=T["bg"])
    profile_row.pack(anchor="w", pady=(8, 0))
    tk.Label(profile_row, text=f"👤  {app._profile_name}",
             font=("Helvetica", 10, "bold"),
             bg=T["card_border"], fg=T["muted"],
             padx=10, pady=4).pack(side=tk.LEFT)
    tk.Button(profile_row, text="Switch profile",
              font=("Helvetica", 9), bg=T["bg"], fg=T["dim"],
              relief="flat", bd=0, padx=8, cursor="hand2",
              activebackground="#f8fafc", activeforeground="#475569",
              command=app.show_profiles).pack(side=tk.LEFT, padx=(8, 0))
    tk.Button(profile_row, text="⚙",
              font=("Helvetica", 10), bg=T["bg"], fg=T["dim"],
              relief="flat", bd=0, padx=6, cursor="hand2",
              activebackground="#f8fafc", activeforeground="#475569",
              command=app._show_settings).pack(side=tk.LEFT, padx=(4, 0))

    # Right: points + achievements button
    right_col = tk.Frame(hdr, bg=T["bg"])
    right_col.pack(side=tk.RIGHT, anchor="ne",
                   padx=((0, 48) if is_matrix else 0),
                   pady=(32 if is_matrix else 0))

    pts          = app._ach_store.get_points()
    earned_count = len(app._ach_store.get_earned())
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
              command=app._show_achievements).pack(anchor="e")

    # ── Game family row (4 tiles) ────────────────────────────────────────
    # One tile per family. Click → show_difficulty(family). Compact
    # by design — 12 game cards collapse to 4 here. Any future
    # families plug in by appending an entry to GAMES.
    GAMES, _DIFFICULTY_TIERS = _registry()
    app._tile_images = []   # release prior refs; renderer repopulates

    family_section = tk.Frame(inner, bg=T["bg"], padx=48)
    family_section.pack(fill=tk.X, pady=(0, 70 if is_matrix else 28))

    tk.Label(family_section, text="GAMES",
             font=("Helvetica", 13, "bold"),
             bg=T["bg"], fg=T["dim"]).pack(anchor="w", pady=(0, 12))

    # family_grid is a plain Frame again (v0.8.2 makes the per-
    # section rain canvases redundant — full-canvas rain in
    # _show_menu_matrix gives the cinematic curtain everywhere
    # already. Keeping family_grid as Canvas was clipping tile
    # heights to its `height=240`).
    family_grid = tk.Frame(family_section, bg=T["bg"])
    family_grid.pack(fill=tk.X)
    for col in range(len(GAMES)):
        family_grid.columnconfigure(col, weight=1)
    for col, family in enumerate(GAMES):
        padx = (0, 14) if col < len(GAMES) - 1 else 0
        _family_tile(app, family_grid, family, col, padx)

    # ── Tools row (4 tiles): Practice / Stats / Tutorials / Shop ────────
    _tools_row(app, inner)

    # ── Footer ────────────────────────────────────────────────────────────
    tk.Frame(inner, bg=T["card_border"], height=1).pack(fill=tk.X, padx=48, pady=(24, 0))
    tk.Label(inner,
             text=f"Math Practice  v{_version()}  ·  © 2026 Aleksander Lie",
             font=("Helvetica", 8), bg=T["bg"], fg=T["faint"]).pack(pady=(6, 24))


# ============================================================ matrix menu

def show_menu_matrix(app, outer):
    """Full-window rain-canvas menu (matrix theme only).

    v0.8.2-fix: header is split into `title_block` (LEFT) and
    `right_block` (RIGHT) so canvas surface — and therefore rain —
    is visible BETWEEN them. tools_row is built inline using
    `_build_tools_tiles`; calling _tools_row(autopack=False) and
    create_window'ing the returned section had broken reqheight
    propagation (tiles rendered as zero-height). Mirroring
    family_row's inline construction made it work.
    """
    T = theme()
    GAMES, _DIFFICULTY_TIERS = _registry()

    # Single full-window rain canvas
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
    app._tile_images = []

    PADX = 48

    # ── Header: split into LEFT title block + RIGHT points block ──
    title_block = tk.Frame(rain_canvas, bg=T["bg"])
    tk.Label(title_block, text="Math Practice",
             font=("Helvetica", 32, "bold"),
             bg=T["bg"], fg=T["ink"]).pack(anchor="w")
    tk.Label(title_block, text="Choose a game to start practising.",
             font=("Helvetica", 13), bg=T["bg"], fg=T["muted"]).pack(anchor="w", pady=(4, 0))
    profile_row = tk.Frame(title_block, bg=T["bg"])
    profile_row.pack(anchor="w", pady=(8, 0))
    tk.Label(profile_row, text=f"\U0001F464  {app._profile_name}",
             font=("Helvetica", 10, "bold"),
             bg=T["card_border"], fg=T["muted"],
             padx=10, pady=4).pack(side=tk.LEFT)
    tk.Button(profile_row, text="Switch profile",
              font=("Helvetica", 9), bg=T["bg"], fg=T["dim"],
              relief="flat", bd=0, padx=8, cursor="hand2",
              activebackground=T["bg"], activeforeground=T["muted"],
              command=app.show_profiles).pack(side=tk.LEFT, padx=(8, 0))
    tk.Button(profile_row, text="⚙",
              font=("Helvetica", 10), bg=T["bg"], fg=T["dim"],
              relief="flat", bd=0, padx=6, cursor="hand2",
              activebackground=T["bg"], activeforeground=T["muted"],
              command=app._show_settings).pack(side=tk.LEFT, padx=(4, 0))

    right_block = tk.Frame(rain_canvas, bg=T["bg"])
    pts          = app._ach_store.get_points()
    earned_count = len(app._ach_store.get_earned())
    total_count  = len(ACHIEVEMENTS)
    tk.Label(right_block, text=f"⭐ {pts:,} pts",
             font=("Helvetica", 14, "bold"),
             bg=T["bg"], fg="#f59e0b").pack(anchor="e")
    tk.Label(right_block, text=f"{earned_count} / {total_count} achievements",
             font=("Helvetica", 9), bg=T["bg"], fg=T["dim"]).pack(anchor="e", pady=(2, 8))
    tk.Button(right_block, text="\U0001F3C6  Trophy Room",
              font=("Helvetica", 10, "bold"),
              bg=T["btn_primary_bg"], fg=T["btn_primary_fg"],
              relief="flat", bd=0, padx=14, pady=7, cursor="hand2",
              activebackground=T["btn_primary_hover"],
              activeforeground=T["btn_primary_fg"],
              command=app._show_achievements).pack(anchor="e")

    # ── GAMES label + family-tile row ──
    games_label = tk.Label(rain_canvas, text="GAMES",
                           font=("Helvetica", 13, "bold"),
                           bg=T["bg"], fg=T["dim"])
    family_row = tk.Frame(rain_canvas, bg=T["bg"])
    for col in range(len(GAMES)):
        family_row.columnconfigure(col, weight=1)
    for col, family in enumerate(GAMES):
        padx_arg = (0, 14) if col < len(GAMES) - 1 else 0
        _family_tile(app, family_row, family, col, padx_arg)

    # ── TOOLS label + tools-tile row (inline build, mirrors family_row) ──
    tools_label = tk.Label(rain_canvas, text="TOOLS",
                           font=("Helvetica", 13, "bold"),
                           bg=T["bg"], fg=T["dim"])
    tools_row = tk.Frame(rain_canvas, bg=T["bg"])
    for col in range(4):
        tools_row.columnconfigure(col, weight=1)
    _build_tools_tiles(app, tools_row)

    # ── Footer ──
    footer_div = tk.Frame(rain_canvas, bg=T["card_border"], height=1)
    footer_lbl = tk.Label(rain_canvas,
        text=f"Math Practice  v{_version()}  ·  © 2026 Aleksander Lie",
        font=("Helvetica", 8), bg=T["bg"], fg=T["faint"])

    # Mount everything on the canvas. Header items get separate
    # create_windows so canvas surface between them shows rain.
    title_id = rain_canvas.create_window(0, 0, anchor="nw", window=title_block)
    right_id = rain_canvas.create_window(0, 0, anchor="ne", window=right_block)

    # Body sections flow from top (after header). Footer is pinned
    # to the bottom of the canvas separately so the gap between the
    # tools row and the footer becomes a wide rain band.
    body_sections = [
        (games_label, False, 12),
        (family_row,  True,  60),
        (tools_label, False, 12),
        (tools_row,   True,  60),
    ]
    body_ids = [
        rain_canvas.create_window(0, 0, anchor="nw", window=w)
        for (w, _, _) in body_sections
    ]
    footer_div_id = rain_canvas.create_window(0, 0, anchor="sw",
                                              window=footer_div)
    footer_lbl_id = rain_canvas.create_window(0, 0, anchor="s",
                                              window=footer_lbl)

    def _layout(_e=None):
        try:
            rain_canvas.update_idletasks()
            cw = rain_canvas.winfo_width()
            ch = rain_canvas.winfo_height()

            # Header row at y=30 — tighter top band than before.
            y = 30
            rain_canvas.coords(title_id, PADX, y)
            rain_canvas.coords(right_id, cw - PADX, y)
            rain_canvas.update_idletasks()
            hdr_h = max(title_block.winfo_reqheight(),
                        right_block.winfo_reqheight())
            y += hdr_h + 60

            for (widget, fill_w, gap), wid in zip(body_sections, body_ids):
                if fill_w:
                    rain_canvas.itemconfig(wid, width=cw - 2 * PADX)
                rain_canvas.coords(wid, PADX, y)
                rain_canvas.update_idletasks()
                y += widget.winfo_reqheight() + gap

            # Pin footer to the bottom of the canvas so a wide rain
            # band remains visible between the tools row and the
            # footer divider.
            rain_canvas.itemconfig(footer_div_id, width=cw - 2 * PADX)
            rain_canvas.coords(footer_div_id, PADX, ch - 30)
            rain_canvas.coords(footer_lbl_id, cw // 2, ch - 12)
        except Exception:
            pass

    rain_canvas.bind("<Configure>", _layout)
    rain_canvas.after(20, _layout)


# ============================================================ family tiles

def _family_tile(app, parent, family, col, padx):
    """Render a single game-family card on the main menu.

    Compact tile — glyph + label + tagline + a row of three small
    status pills (one per difficulty). Clicking anywhere on the tile
    opens the difficulty-selection page for the family.
    """
    _GAMES, _DIFFICULTY_TIERS = _registry()
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
        locked = bool(unlock and not app._ach_store.has(unlock))
        sharp  = app._ach_store.has(f"sharp_{gid}")
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
        command=lambda f=family: app.show_difficulty(f),
    ).pack(anchor="w")

    # Make the entire tile clickable, not just the button.
    def _open(e=None, f=family):
        app.show_difficulty(f)
    for w in (card, inner, top):
        w.bind("<Button-1>", _open)


# ============================================================ tools row

def _tools_row(app, parent, *, autopack=True):
    """Bottom-of-menu tools strip. Four tiles in a row.

    v0.8.2: when autopack=False, returns the section Frame without
    packing it — caller (e.g. _show_menu_matrix) can mount it via
    canvas.create_window instead.
    """
    T = theme()
    # v0.8.1.3: extra bottom pady in matrix mode so the inner
    # canvas surface shows a wide rain band below the tools row.
    section = tk.Frame(parent, bg=T["bg"], padx=48)
    if autopack:
        try:
            _bot = 100 if _theme_name() == "matrix" else 28
        except Exception:
            _bot = 28
        section.pack(fill=tk.X, pady=(0, _bot))

    tk.Label(section, text="TOOLS",
             font=("Helvetica", 13, "bold"),
             bg=T["bg"], fg=T["dim"]).pack(anchor="w", pady=(0, 12))

    # v0.8.2.1: revert to plain Frame. The matrix-mode Canvas
    # variant (with height=200) was clipping the tool tiles in the
    # new full-canvas matrix menu (_show_menu_matrix uses the
    # whole rain_canvas; per-section rain is redundant).
    cards = tk.Frame(section, bg=T["bg"])
    cards.pack(fill=tk.X)
    for col in range(4):
        cards.columnconfigure(col, weight=1)

    _build_tools_tiles(app, cards)
    return section


# ============================================================ tools tiles

def _build_tools_tiles(app, cards):
    """Build the four tool tiles (Practice / Stats / Tutorials /
    Shop) into the given `cards` parent, gridded into columns 0..3.

    Extracted from _tools_row in v0.8.2 so _show_menu_matrix can
    build a tools row inline (mirroring family_row) without the
    section/label wrapping that has create_window reqheight
    issues. The non-matrix path still goes through _tools_row;
    _tools_row now ends by calling this helper.
    """
    T = theme()

    # ── Practice Missed card ─────────────────────────────────────────
    count   = app._missed_store.count()
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
        command=app._launch_practice if enabled else None,
    )
    play_btn.pack(anchor="w")

    if enabled:
        for w in (card, inner):
            w.bind("<Button-1>", lambda e: app._launch_practice())

    # ── Progress & Stats card ────────────────────────────────────────
    sess_count = app._sessions_store.count() if app._sessions_store else 0
    days       = len(app._ach_store.get_stats().get("days_played", []))

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
        command=app._launch_stats,
    ).pack(anchor="w")

    for w in (stats_card, stats_inner):
        w.bind("<Button-1>", lambda e: app._launch_stats())

    # ── Tutorials card ───────────────────────────────────────────────
    # Count tutorials unlocked for the active profile so the subtitle
    # tells the user how many guides are currently available.
    unlocked = sum(
        1 for gid in TUTORIAL_REGISTRY
        if not (UNLOCK_REQUIREMENTS.get(gid) and not app._ach_store.has(UNLOCK_REQUIREMENTS[gid]))
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
        command=app._launch_tutorials,
    ).pack(anchor="w")

    for w in (tut_card, tut_inner):
        w.bind("<Button-1>", lambda e: app._launch_tutorials())

    # ── Shop card ────────────────────────────────────────────────────
    # Functional shop tile (v0.7.13). Click → modal listing every
    # entry in SHOP_ITEMS with its own buy / owned state.
    _shop_tile(app, cards)


def _shop_tile(app, parent):
    """Tools-row entry that opens the Shop modal."""
    T = theme()

    # Item count summary in the subtitle so the pupil knows the
    # shop is non-empty and how much progress they have.
    total = len(SHOP_ITEMS)
    owned = sum(1 for it in SHOP_ITEMS
                if app._purchases_store and app._purchases_store.has(it["id"]))
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
        command=app._show_shop,
    ).pack(anchor="w")

    for w in (card, inner):
        w.bind("<Button-1>", lambda e: app._show_shop())
