"""
slideshow_frame.py
------------------
Reusable tutorial slideshow widget.

Usage
-----
    from games.tutorials import slideshow_frame, tutorial_div_basic

    SlideshowFrame(
        parent,
        back_callback = go_back,
        title         = tutorial_div_basic.TITLE,
        lead          = tutorial_div_basic.LEAD,
        slides        = tutorial_div_basic.SLIDES,
        examples      = tutorial_div_basic.EXAMPLES,
    )

A slide is a dict:
    {
      "title":   "Step 1 — Flip the question",
      "caption": "Instead of dividing, ask a multiplication question.",
      "draw":    draw_fn,   # def draw_fn(canvas, example, w, h) -> None
    }

`examples` is a list of dicts whose shape is tutorial-specific — the slide's
`draw` function is responsible for reading the fields it needs.

Design notes
------------
* Pure tkinter Canvas + widgets, no new dependencies.
* Static slides. No animated reveals. (Added later if a specific mode needs it.)
* The "Next example" button cycles through curated examples and redraws the
  current slide — learners see the method on a different problem without
  losing their place.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import tkinter as tk
from tkinter import ttk


# ── Palette (mirrors stats_screen.py for visual consistency) ─────────────────

BG          = "#f8fafc"
CARD_BG     = "white"
CARD_BORDER = "#e2e8f0"
INK         = "#0f172a"
MUTED       = "#64748b"
DIM         = "#94a3b8"
FAINT       = "#cbd5e1"
SOFT        = "#f1f5f9"
ACCENT      = "#4f46e5"
ACCENT_DARK = "#4338ca"
GOOD        = "#15803d"
WARN        = "#b45309"

CANVAS_W    = 720
CANVAS_H    = 340


class SlideshowFrame:
    """Full-page tutorial slideshow. Mounted into a parent frame.

    Parameters
    ----------
    parent : tk.Frame
    back_callback : callable — invoked when the user clicks "← Back"
    title, lead : header strings
    slides : list of slide dicts (title, caption, draw)
    examples : list of example dicts (shape is tutorial-defined)
    """

    def __init__(self, parent, back_callback,
                 title: str, lead: str,
                 slides: list[dict], examples: list[dict]):
        self.parent        = parent
        self.back_callback = back_callback
        self.title_text    = title
        self.lead_text     = lead
        self.slides        = list(slides)
        self.examples      = list(examples) if examples else [{}]

        self._slide_idx    = 0
        self._example_idx  = 0

        # Pre-declare widget attributes so callbacks that fire before _build
        # finishes (e.g. a button click after a partial build) fail loudly
        # with a clear None-check rather than a cryptic AttributeError.
        self._example_btn     = None
        self._slide_title_lbl = None
        self._canvas          = None
        self._caption_lbl     = None
        self._prev_btn        = None
        self._next_btn        = None
        self._counter_lbl     = None

        self._build()
        self._render_current()

    # ================================================================ build

    def _build(self):
        # ── Top bar: back button + example selector ──────────────────────
        top = tk.Frame(self.parent, bg=BG, padx=24, pady=10)
        top.pack(fill=tk.X)

        tk.Button(top, text="← Back",
                  font=("Helvetica", 10), bg=BG, fg="#475569",
                  relief="flat", bd=0, cursor="hand2",
                  activebackground=BG, activeforeground=INK,
                  command=self.back_callback).pack(side=tk.LEFT)

        # "Next example" button lives on the right of the top bar so it is
        # always reachable without scrolling.
        self._example_btn = tk.Button(
            top, text="Next example  ↻",
            font=("Helvetica", 10, "bold"),
            bg=INK, fg="white",
            relief="flat", bd=0, padx=12, pady=5, cursor="hand2",
            activebackground="#1e293b", activeforeground="white",
            command=self._cycle_example,
        )
        if len(self.examples) > 1:
            self._example_btn.pack(side=tk.RIGHT)

        # ── Header ───────────────────────────────────────────────────────
        # NOTE: widget-level `pady=` must be a single integer in Tk 9 /
        # Python 3.14 (tuples are only valid on .pack(pady=...) etc.). The
        # asymmetric top/bottom padding is applied on the .pack() call below.
        hdr = tk.Frame(self.parent, bg=BG, padx=48)
        hdr.pack(fill=tk.X, pady=(14, 8))
        tk.Label(hdr, text=self.title_text,
                 font=("Helvetica", 26, "bold"),
                 bg=BG, fg=INK).pack(anchor="w")
        if self.lead_text:
            tk.Label(hdr, text=self.lead_text,
                     font=("Helvetica", 12), bg=BG, fg=MUTED).pack(anchor="w",
                                                                   pady=(4, 0))

        # ── Slide card ───────────────────────────────────────────────────
        card_wrap = tk.Frame(self.parent, bg=BG, padx=48, pady=10)
        card_wrap.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(card_wrap, bg=CARD_BG,
                        highlightbackground=CARD_BORDER, highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        # Slide title (above canvas)
        self._slide_title_lbl = tk.Label(
            card, text="", font=("Helvetica", 16, "bold"),
            bg=CARD_BG, fg=INK, padx=24, pady=18, anchor="w", justify="left")
        self._slide_title_lbl.pack(fill=tk.X)

        # Canvas area
        self._canvas = tk.Canvas(card, width=CANVAS_W, height=CANVAS_H,
                                 bg=CARD_BG, highlightthickness=0)
        self._canvas.pack(pady=(0, 4))

        # Caption below canvas
        self._caption_lbl = tk.Label(
            card, text="", font=("Helvetica", 11),
            bg=CARD_BG, fg=MUTED, padx=24, pady=18,
            anchor="w", justify="left", wraplength=720)
        self._caption_lbl.pack(fill=tk.X)

        # ── Navigation bar ───────────────────────────────────────────────
        nav = tk.Frame(self.parent, bg=BG, padx=48, pady=14)
        nav.pack(fill=tk.X)

        self._prev_btn = tk.Button(
            nav, text="←  Previous",
            font=("Helvetica", 10, "bold"),
            bg=SOFT, fg=INK,
            relief="flat", bd=0, padx=14, pady=6, cursor="hand2",
            activebackground=FAINT, activeforeground=INK,
            command=self._go_prev,
        )
        self._prev_btn.pack(side=tk.LEFT)

        self._next_btn = tk.Button(
            nav, text="Next  →",
            font=("Helvetica", 10, "bold"),
            bg=ACCENT, fg="white",
            relief="flat", bd=0, padx=14, pady=6, cursor="hand2",
            activebackground=ACCENT_DARK, activeforeground="white",
            command=self._go_next,
        )
        self._next_btn.pack(side=tk.RIGHT)

        self._counter_lbl = tk.Label(
            nav, text="", font=("Helvetica", 10),
            bg=BG, fg=MUTED)
        self._counter_lbl.pack(side=tk.TOP)

        # Keyboard bindings for convenience
        self.parent.bind_all("<Left>",  lambda e: self._go_prev())
        self.parent.bind_all("<Right>", lambda e: self._go_next())
        self.parent.bind_all("<Escape>", lambda e: self.back_callback())

    # ============================================================== render

    def _render_current(self):
        # Guard against callbacks firing before _build finished (e.g. when
        # a Tcl error aborted _build partway through). Without this, a
        # Next/Prev click here would raise a misleading AttributeError and
        # the real cause (from _build) would stay hidden.
        if self._slide_title_lbl is None or self._canvas is None:
            return

        slide   = self.slides[self._slide_idx]
        example = self.examples[self._example_idx] if self.examples else {}

        self._slide_title_lbl.config(text=slide.get("title", ""))
        self._caption_lbl.config(text=slide.get("caption", ""))

        self._canvas.delete("all")
        draw = slide.get("draw")
        if callable(draw):
            try:
                draw(self._canvas, example, CANVAS_W, CANVAS_H)
            except Exception as exc:
                # Don't crash the UI if a slide has a drawing bug; show a
                # minimal fallback instead so the framework keeps flowing.
                self._canvas.create_text(
                    CANVAS_W / 2, CANVAS_H / 2,
                    text=f"(slide render error: {exc})",
                    fill=MUTED, font=("Helvetica", 10))

        # counter
        total = len(self.slides)
        ex_n  = len(self.examples)
        parts = [f"Slide {self._slide_idx + 1} of {total}"]
        if ex_n > 1:
            parts.append(f"Example {self._example_idx + 1} of {ex_n}")
        self._counter_lbl.config(text="   ·   ".join(parts))

        # enable/disable nav buttons at the ends
        self._prev_btn.config(state="normal" if self._slide_idx > 0 else "disabled")
        self._next_btn.config(state="normal" if self._slide_idx < total - 1 else "disabled")

    # ============================================================ actions

    def _go_prev(self):
        if self._slide_idx > 0:
            self._slide_idx -= 1
            self._render_current()

    def _go_next(self):
        if self._slide_idx < len(self.slides) - 1:
            self._slide_idx += 1
            self._render_current()

    def _cycle_example(self):
        if len(self.examples) > 1:
            self._example_idx = (self._example_idx + 1) % len(self.examples)
            self._render_current()


# ── Shared drawing helpers ───────────────────────────────────────────────────
#
# These are exported so individual tutorial modules can stay small and focus
# on pedagogy rather than Canvas plumbing.

def draw_centered_expression(canvas, text, y,
                             size=36, color=INK, bold=True, w=CANVAS_W):
    """Draw a large centered math expression at vertical position y."""
    font_spec = ("Helvetica", size, "bold") if bold else ("Helvetica", size)
    canvas.create_text(w / 2, y, text=text, fill=color, font=font_spec)


def draw_note(canvas, text, y, w=CANVAS_W, color=MUTED, size=11):
    """Draw a centered italic-ish subtitle line."""
    canvas.create_text(w / 2, y, text=text, fill=color,
                       font=("Helvetica", size), width=w - 80, justify="center")


def draw_arrow(canvas, x1, y1, x2, y2, color=ACCENT, width=2, dash=None):
    """Draw a labelled arrow from (x1, y1) to (x2, y2)."""
    kwargs = {"arrow": tk.LAST, "fill": color, "width": width,
              "arrowshape": (12, 14, 5)}
    if dash:
        kwargs["dash"] = dash
    canvas.create_line(x1, y1, x2, y2, **kwargs)


def draw_pill(canvas, cx, cy, text, bg=SOFT, fg=INK, pad=10, size=13, bold=True):
    """Draw a pill-shaped label centered on (cx, cy)."""
    font_spec = ("Helvetica", size, "bold") if bold else ("Helvetica", size)
    # measure
    tmp = canvas.create_text(0, -9999, text=text, font=font_spec)
    bx1, by1, bx2, by2 = canvas.bbox(tmp)
    canvas.delete(tmp)
    tw = bx2 - bx1
    th = by2 - by1
    w  = tw + pad * 2
    h  = th + pad
    x1 = cx - w / 2
    y1 = cy - h / 2
    x2 = cx + w / 2
    y2 = cy + h / 2
    # draw a rounded-ish rectangle with fill
    r = h / 2
    canvas.create_oval(x1, y1, x1 + 2 * r, y2, fill=bg, outline=bg)
    canvas.create_oval(x2 - 2 * r, y1, x2, y2, fill=bg, outline=bg)
    canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=bg, outline=bg)
    canvas.create_text(cx, cy, text=text, fill=fg, font=font_spec)
