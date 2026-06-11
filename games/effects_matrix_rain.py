"""
effects_matrix_rain.py
----------------------
Falling-katakana "matrix rain" Canvas effect.

Used as a decorative banner at the top of the main menu when Matrix
theme is active (v0.8.1). The rain itself is self-contained: instantiate
a `MatrixRain` against a parent widget, call `start()`, and call
`stop()` on teardown to cancel the animation loop.

Why a banner and not full-screen
--------------------------------
Tk Frames are not transparent — putting a rain Canvas behind a Frame-
based menu layout would hide it behind the opaque page background. A
full-screen rain would require rewriting the entire menu to use
`canvas.create_window()` for every widget, with rain drawn on the
shared canvas surface and content rendered as embedded windows. That's
a substantial rewrite for a cosmetic feature. The banner placement
gets 80% of the visual impact (matrix vibe is the FIRST thing the eye
sees) for ~5% of the cost.

If full-screen rain becomes a priority, the canonical move is:
  1. Replace `show_menu`'s inner Frame with a Canvas.
  2. Position every header / family tile / tools tile via
     `inner.create_window(x, y, anchor="nw", window=widget)`.
  3. Run rain on `inner`. Surface between windows = rain.

Animation contract
------------------
* One `after(_DELAY_MS, _tick)` loop drives every column.
* Each column has a head row (bright), a fading trail behind it, and
  an empty zone between trails. Glyphs are randomly cycled while the
  column is alive — gives the "characters keep changing" Matrix look.
* On `stop()` the after-id is cancelled and existing canvas items are
  deleted so the parent can be torn down cleanly.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import random
import tkinter as tk


# ── Glyph pool ──────────────────────────────────────────────────────────────
# Half-width katakana (U+FF66–U+FF9D) plus a few digits / punctuation
# for the authentic terminal-feed look. Half-width chosen over full-
# width so columns can sit closer together.
# Half-width katakana dominates the pool; digits and a small alphabet
# add variety; math operators (+ − × ÷ = π) are sprinkled in lightly so
# the rain has a "math program reading itself" flavour. Math symbols
# are repeated twice each to bump them slightly above the random-noise
# rate while still keeping the katakana flavour dominant.
_GLYPHS = (
    [chr(c) for c in range(0xFF66, 0xFF9E)] +    # half-width katakana (~56)
    list("0123456789") +
    list("ABCDEFGHIJKLMNOPQRSTUVWXYZ:.\"<>¦|_\\") +
    # math accents (each repeated → ~3% appearance per glyph instead of ~1%)
    list("+−×÷=π+−×÷=π")
)


# ── Tunables ────────────────────────────────────────────────────────────────

_DELAY_MS    = 55            # animation tick — denser since v0.8.2.1
_COL_PX      = 8             # horizontal pixels per column — was 10 (denser)
_ROW_PX      = 16            # vertical pixels per row
_FONT        = ("Consolas", 12, "bold")
_HEAD_COLOR  = "#bbffbb"     # bright lead character
_TRAIL_BODY  = "#00ff41"     # fresh trail (matrix green)
_TRAIL_DIM   = "#00aa2a"     # mid-trail
_TRAIL_FAINT = "#005a16"     # fading tail
_TRAIL_LEN   = 8             # how many rows the trail spans
_RESPAWN_PROB = 0.05         # per-column chance to respawn after running off-screen — bumped 0.018→0.05 in v0.8.2.1 for denser feel


class MatrixRain:
    """Falling-glyph rain rendered onto a caller-supplied `tk.Canvas`.

    The caller owns the canvas — `MatrixRain` does NOT pack, place, or
    destroy it. This lets the menu use the canvas as its layout
    surface (with content widgets packed on top) and have rain show
    through the surface area not covered by content. See `show_menu`
    in `game.py` for the canonical wiring.
    """

    def __init__(self, canvas: tk.Canvas, *, tag: str = "matrix_rain"):
        self.canvas = canvas
        # All canvas items get this tag so we can purge them in `stop()`
        # without disturbing other items the caller may have drawn.
        self._tag = tag

        self._after_id = None
        self._cols     = []
        self._n_cols   = 0
        self._n_rows   = 1
        self._running  = False

        # Bind <Configure> on the canvas to recompute layout. Cache the
        # binding id so we can remove it on stop() and not leak when the
        # caller reuses the same canvas with a different effect.
        self._bind_id = canvas.bind("<Configure>", self._on_resize, add="+")

    # ============================================================ public API

    def start(self):
        if self._running:
            return
        self._running = True
        # Force a layout pass once so the rain is seeded even before the
        # first <Configure> fires (the canvas might already have a size).
        try:
            self.canvas.update_idletasks()
            w = max(1, self.canvas.winfo_width())
            h = max(1, self.canvas.winfo_height())
            self._reseed(w, h)
        except Exception:
            pass
        self._tick()

    def stop(self):
        """Cancel the animation loop and remove our items from the
        canvas. Safe to call multiple times. The canvas itself is left
        intact — caller still owns it."""
        self._running = False
        if self._after_id is not None:
            try:
                self.canvas.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        try:
            self.canvas.delete(self._tag)
        except Exception:
            pass

    def destroy(self):
        """Alias for stop(). Kept so callers don't have to remember
        which method to call on teardown."""
        self.stop()

    # ============================================================ internals

    def _on_resize(self, event):
        self._reseed(event.width, event.height)

    def _reseed(self, w: int, h: int):
        new_cols = max(1, w // _COL_PX)
        new_rows = max(1, h // _ROW_PX)
        # Don't reset everything if the change is trivial — avoids a
        # visible "rain stutter" every time the window resizes by a few px.
        if new_cols == self._n_cols and new_rows == self._n_rows:
            return
        self._n_cols = new_cols
        self._n_rows = new_rows
        self._cols   = [self._fresh_column() for _ in range(self._n_cols)]

    def _fresh_column(self):
        """Initialise a column with a randomised drop position so the
        rain doesn't all start at the same row on first paint."""
        return {
            "head":   random.randint(-self._n_rows, self._n_rows),
            "alive":  True,
            "speed":  random.choice((1, 1, 1, 2)),   # rare faster column
            "glyphs": [random.choice(_GLYPHS) for _ in range(self._n_rows + _TRAIL_LEN)],
        }

    def _tick(self):
        if not self._running:
            return
        try:
            self._draw()
        except tk.TclError:
            # Canvas got destroyed mid-loop; stop cleanly.
            self._running = False
            return
        self._after_id = self.canvas.after(_DELAY_MS, self._tick)

    def _draw(self):
        c = self.canvas
        # Only purge our own items — the caller may have drawn other
        # things on this canvas (e.g. the menu's content windows).
        c.delete(self._tag)

        # Re-read current canvas size every tick so we adapt to a window
        # being resized without waiting for a full <Configure> reseed.
        # v0.8.2.1: also call _reseed each tick — fixes the "only one
        # column on launch" bug where start() ran before the canvas had
        # a real size. _reseed early-exits if the dimensions match.
        try:
            width  = c.winfo_width()
            height = c.winfo_height()
            self._reseed(width, height)
        except Exception:
            return

        for col_idx, col in enumerate(self._cols):
            x = col_idx * _COL_PX + _COL_PX // 2
            head = col["head"]

            # Head glyph (brightest)
            head_y = head * _ROW_PX + _ROW_PX // 2
            if 0 <= head_y < height:
                c.create_text(
                    x, head_y,
                    text=random.choice(_GLYPHS),
                    fill=_HEAD_COLOR, font=_FONT,
                    tags=(self._tag,),
                )

            # Trail behind the head — fades through three colour stops.
            for trail_offset in range(1, _TRAIL_LEN + 1):
                row = head - trail_offset
                y   = row * _ROW_PX + _ROW_PX // 2
                if y < 0 or y >= height:
                    continue
                if trail_offset <= 2:
                    fill = _TRAIL_BODY
                elif trail_offset <= 5:
                    fill = _TRAIL_DIM
                else:
                    fill = _TRAIL_FAINT
                glyph_idx = (row + len(col["glyphs"])) % len(col["glyphs"])
                glyph = col["glyphs"][glyph_idx]
                c.create_text(x, y, text=glyph, fill=fill, font=_FONT,
                              tags=(self._tag,))

            col["head"] += col["speed"]
            if (col["head"] - _TRAIL_LEN) * _ROW_PX > height:
                if random.random() < _RESPAWN_PROB or col["head"] > 3 * self._n_rows:
                    self._cols[col_idx] = self._fresh_column()
                    self._cols[col_idx]["head"] = random.randint(-_TRAIL_LEN, 0)

        # Keep rain *behind* any caller-managed canvas items.
        try:
            c.tag_lower(self._tag)
        except Exception:
            pass
