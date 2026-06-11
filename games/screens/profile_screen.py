"""
games.screens.profile_screen
----------------------------
Profile landing screen + load_profile flow. Carved out of game.py in
v0.9.0 second decomposition pass.

Public API:
    show_profile_screen(app)
    load_profile(app, name)

Reads from `app`: `.root`, `._clear()`, `._current`, `._profile_name`,
`._ach_store`, `._missed_store`, `._scores_store`, `._sessions_store`,
`._purchases_store`, `._show_settings()`, `.show_menu()`,
`._load_profile()` (which is the App-level wrapper around `load_profile`).
"""

import tkinter as tk
from tkinter import messagebox

from ..theme import theme
from ..settings_manager import settings
from ..profile_manager import (
    list_profiles, create_profile, delete_profile, load_stores,
)


def _version():
    """Lazy import to avoid circular dependency with game.py."""
    from game import __version__
    return __version__


def show_profile_screen(app):
    """Landing screen — choose or create a profile."""
    T = theme()
    app._clear()
    app._profile_name = None
    app._ach_store = app._missed_store = app._scores_store = None
    app._sessions_store = None
    app._purchases_store = None

    outer = tk.Frame(app.root, bg=T["bg"])
    outer.pack(fill=tk.BOTH, expand=True)
    app._current = outer

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
            _profile_card(app, profiles_frame, name)

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
        app._load_profile(name)

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
             text=f"Math Practice  v{_version()}  ·  © 2026 Aleksander Lie",
             font=("Helvetica", 8), bg=T["bg"], fg=T["faint"]).pack(side=tk.LEFT, padx=16)
    tk.Button(footer, text="⚙  Settings",
              font=("Helvetica", 9), bg=T["bg"], fg=T["dim"],
              relief="flat", bd=0, padx=8, cursor="hand2",
              activebackground="#f8fafc", activeforeground="#475569",
              command=app._show_settings).pack(side=tk.RIGHT, padx=16)


def _profile_card(app, parent, name):
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
            app.show_profiles()   # refresh

    tk.Button(inner, text="✕",
              font=("Helvetica", 10), bg=T["card_bg"], fg=T["dim"],
              relief="flat", bd=0, padx=6, cursor="hand2",
              activebackground="white", activeforeground="#b91c1c",
              command=_confirm_delete).pack(side=tk.RIGHT)

    # Clicking card or name launches profile
    for w in (card, inner, name_lbl):
        w.bind("<Button-1>", lambda e, n=name: app._load_profile(n))


def load_profile(app, name: str):
    """Load stores for the chosen profile and go to game menu.

    v0.8.2: validate the active theme is owned by the loaded
    profile. The `theme` setting is global but each theme is
    unlocked via a per-profile shop purchase. Without this, a
    profile that bought Dark Mode could give the unlock to a
    sibling profile by leaving Dark Mode active when switching —
    a free pass that defeats the shop. If the active theme isn't
    owned, reset to Light.
    """
    app._profile_name = name
    (app._ach_store, app._missed_store,
     app._scores_store, app._sessions_store,
     app._purchases_store) = load_stores(name)

    try:
        from ..theme import theme_name
        cur = theme_name()
        theme_to_item = {"dark": "dark_mode", "matrix": "matrix_mode"}
        shop_id = theme_to_item.get(cur)
        if shop_id and not app._purchases_store.has(shop_id):
            settings.set("theme", "light")
    except Exception:
        pass

    app.show_menu()
