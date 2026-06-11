"""
games.screens.settings_dialog
-----------------------------
Settings popup. Carved out of game.py in v0.9.0.

Public API:
    show_settings_dialog(app)

Reads from `app`: `.root`, `._purchases_store`, `._show_shop()`,
`.show_menu()`. The host App method is now a one-line delegator into
this function.
"""

import tkinter as tk

from ..theme import theme, available_themes, theme_name as _theme_name
from ..settings_manager import settings


_THEME_META = {
    "light":  {"name": "Light",  "desc": "Default light theme.",                 "icon": "☀",  "shop_id": None},
    "dark":   {"name": "Dark",   "desc": "Clean dark theme.",                    "icon": "🌙", "shop_id": "dark_mode"},
    "matrix": {"name": "Matrix", "desc": "Green-on-black phosphor. Digits glow.", "icon": "🟢", "shop_id": "matrix_mode"},
}


def show_settings_dialog(app):
    """Settings popup — global options, not per-profile."""
    T = theme()
    root = app.root
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
    # Theme picker (v0.7.13.1). Light is free; Dark / Matrix unlock
    # via Shop purchases. Each row is one theme — selecting an owned
    # one writes settings('theme') and rebuilds the menu under the
    # modal. Locked rows offer a "Buy in Shop" shortcut instead.
    _section("Appearance")

    def _select_theme(name):
        settings.set("theme", name)
        try:
            app.show_menu()
        except Exception:
            pass
        # Rebuild the settings dialog so the radio state updates.
        win.destroy()
        show_settings_dialog(app)

    for tk_name in available_themes():
        meta = _THEME_META[tk_name]
        owned = (meta["shop_id"] is None
                 or (app._purchases_store and app._purchases_store.has(meta["shop_id"])))
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
                      command=lambda: (win.destroy(), app._show_shop())
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
