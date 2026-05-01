"""
verify_div_intermediate.py
--------------------------
Headless verification harness for tutorial_div_intermediate.

Checks (per example):
  1. dividend == divisor * quotient      (EXAMPLES invariant)
  2. _short_div_steps walks the correct chain:
       - every step.product == step.quotient_digit * divisor
       - every step.remainder == step.partial - step.product
       - assembled quotient digits match the declared quotient
       - final remainder == 0 (all five examples are exact)
       - start_col / end_col span is consistent (left <= right, both in
         range [0, n_digits_of_dividend - 1])

Checks (per slide):
  - Every slide draws on a MockCanvas without raising, across every
    example in EXAMPLES. Per-slide total draw counts are printed so a
    future regression (e.g. an over-zealous "slim the slides" pass) shows
    up as a divergent total rather than a silent render change.

Run:  python verify_div_intermediate.py
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

from __future__ import annotations

import sys
import traceback


# ── MockCanvas ──────────────────────────────────────────────────────────────
#
# Records every create_* call and returns a fresh monotonic id so create_text
# + bbox lookups (used by helpers like draw_pill) work without a real Tk.

class MockCanvas:
    def __init__(self):
        self.calls = []
        self._next_id = 1
        # Minimal state needed for bbox()
        self._items = {}

    # ---- helpers --------------------------------------------------------
    def _new_id(self):
        i = self._next_id
        self._next_id += 1
        return i

    # ---- drawing API used by slideshow_frame + tutorial module ---------
    def create_text(self, x, y, **kw):
        i = self._new_id()
        self.calls.append(("text", x, y, kw))
        text = str(kw.get("text", ""))
        # Approximate bbox — good enough for draw_pill's measuring probe.
        # Helvetica 11 ~ 7px per char, 13 px tall; we scale with the
        # font size if present.
        font = kw.get("font", ("Helvetica", 11))
        try:
            size = int(font[1])
        except Exception:
            size = 11
        char_w = size * 0.55
        tw = max(1.0, char_w * len(text))
        th = size * 1.2
        anchor = kw.get("anchor", "center")
        if anchor == "w":
            x1, x2 = x, x + tw
        elif anchor == "e":
            x1, x2 = x - tw, x
        else:
            x1, x2 = x - tw / 2, x + tw / 2
        y1, y2 = y - th / 2, y + th / 2
        self._items[i] = (x1, y1, x2, y2)
        return i

    def create_line(self, *coords, **kw):
        self.calls.append(("line", coords, kw))
        i = self._new_id()
        self._items[i] = (min(coords[::2]), min(coords[1::2]),
                          max(coords[::2]), max(coords[1::2]))
        return i

    def create_rectangle(self, x1, y1, x2, y2, **kw):
        self.calls.append(("rect", x1, y1, x2, y2, kw))
        i = self._new_id()
        self._items[i] = (x1, y1, x2, y2)
        return i

    def create_oval(self, x1, y1, x2, y2, **kw):
        self.calls.append(("oval", x1, y1, x2, y2, kw))
        i = self._new_id()
        self._items[i] = (x1, y1, x2, y2)
        return i

    def delete(self, i):
        # draw_pill uses delete() on its measuring probe — just forget it.
        if i in self._items:
            del self._items[i]
        self.calls.append(("delete", i))

    def bbox(self, i):
        return self._items.get(i, (0, 0, 0, 0))


# ── Import targets ─────────────────────────────────────────────────────────

# The tutorial module imports things like `from .slideshow_frame import ...`.
# That relative import needs the `games.tutorials` package path. Easiest is
# to import the module via its package, which requires Tk at import-time
# (slideshow_frame does `import tkinter as tk`). We route around that by
# stubbing tkinter if it isn't available.

try:
    import tkinter  # noqa: F401
except ImportError:
    import types
    fake = types.ModuleType("tkinter")
    fake.LAST = "last"
    class _Stub:
        def __getattr__(self, name): return _Stub()
        def __call__(self, *a, **kw): return _Stub()
    for n in ("Frame", "Label", "Button", "Canvas", "Tk", "Toplevel",
             "StringVar", "IntVar", "BooleanVar"):
        setattr(fake, n, _Stub)
    fake.X = "x"; fake.Y = "y"; fake.BOTH = "both"
    fake.LEFT = "left"; fake.RIGHT = "right"; fake.TOP = "top"; fake.BOTTOM = "bottom"
    sys.modules["tkinter"] = fake
    fake_ttk = types.ModuleType("tkinter.ttk")
    fake_ttk.Style = _Stub
    sys.modules["tkinter.ttk"] = fake_ttk

from games.tutorials import tutorial_div_intermediate as M   # noqa: E402
from games.tutorials.slideshow_frame import CANVAS_W, CANVAS_H   # noqa: E402


# ── Example-level invariants ────────────────────────────────────────────────

def verify_examples():
    print("── EXAMPLE invariants ─────────────────────────────────────────────")
    failed = 0
    for i, ex in enumerate(M.EXAMPLES):
        dividend, divisor, quotient = ex["dividend"], ex["divisor"], ex["quotient"]
        tag = f"[{i}] {dividend} ÷ {divisor} = {quotient}"

        # 1. dividend == divisor * quotient
        assert divisor * quotient == dividend, (
            f"{tag}: divisor * quotient ({divisor*quotient}) != dividend ({dividend})"
        )

        # 2. Step chain correctness
        steps = M._short_div_steps(dividend, divisor)
        assert steps, f"{tag}: no steps produced"

        # Assembled quotient from step digits
        q_digits = "".join(str(s["quotient_digit"]) for s in steps)
        assert int(q_digits) == quotient, (
            f"{tag}: assembled quotient {q_digits} != declared {quotient}"
        )

        # Each step's product / remainder consistency
        for k, s in enumerate(steps):
            assert s["product"] == s["quotient_digit"] * divisor, \
                f"{tag} step {k}: product mismatch"
            assert s["remainder"] == s["partial"] - s["product"], \
                f"{tag} step {k}: remainder mismatch"
            n_digits = len(str(dividend))
            assert 0 <= s["start_col"] <= s["end_col"] < n_digits, \
                f"{tag} step {k}: col span out of range"

        # Final remainder must be zero (all examples are exact)
        assert steps[-1]["remainder"] == 0, \
            f"{tag}: final remainder != 0 (examples must all be exact)"

        print(f"  ✓ {tag}  — {len(steps)} step(s), remainder 0")
    if failed:
        print(f"  ✗ {failed} example(s) failed")
        return False
    print(f"  → {len(M.EXAMPLES)} examples all green")
    return True


# ── Per-slide draw-count audit ──────────────────────────────────────────────

def verify_slides():
    print()
    print("── SLIDE rendering (MockCanvas) ───────────────────────────────────")
    totals_per_slide = [0] * len(M.SLIDES)
    failed = 0
    for slide_idx, slide in enumerate(M.SLIDES):
        draw = slide["draw"]
        title = slide["title"]
        per_example = []
        for ex_idx, ex in enumerate(M.EXAMPLES):
            c = MockCanvas()
            try:
                draw(c, ex, CANVAS_W, CANVAS_H)
            except Exception:
                print(f"  ✗ slide {slide_idx+1} '{title}' FAILED on example {ex_idx}:")
                traceback.print_exc()
                failed += 1
                per_example.append(-1)
                continue
            per_example.append(len(c.calls))
            totals_per_slide[slide_idx] += len(c.calls)
        print(f"  slide {slide_idx+1} '{title}':  per-example draws = {per_example}  "
              f"→ total {totals_per_slide[slide_idx]}")
    grand = sum(t for t in totals_per_slide if t >= 0)
    print()
    print(f"  grand total draws across all slides × examples: {grand}")
    if failed:
        print(f"  ✗ {failed} slide(s) failed")
        return False
    print("  → every slide rendered green across every example")
    return True


# ── Contract sanity ─────────────────────────────────────────────────────────

def verify_contract():
    print()
    print("── CONTRACT sanity ────────────────────────────────────────────────")
    assert isinstance(M.TITLE, str) and len(M.TITLE) <= 50, \
        f"TITLE too long: {len(M.TITLE)} chars (limit 50)"
    assert isinstance(M.LEAD, str) and M.LEAD
    assert isinstance(M.SLIDES, list) and len(M.SLIDES) >= 1
    assert isinstance(M.EXAMPLES, list) and len(M.EXAMPLES) == 5
    for s in M.SLIDES:
        assert set(s.keys()) >= {"title", "caption", "draw"}, \
            f"slide missing required keys: {s.keys()}"
        assert callable(s["draw"])

    # Registry sanity
    from games.tutorials import TUTORIAL_REGISTRY
    assert "div_intermediate" in TUTORIAL_REGISTRY, \
        "TUTORIAL_REGISTRY is missing div_intermediate"
    assert len(TUTORIAL_REGISTRY) == 6, \
        f"TUTORIAL_REGISTRY length should be 6, got {len(TUTORIAL_REGISTRY)}"

    print(f"  ✓ TITLE '{M.TITLE}' ({len(M.TITLE)} chars)")
    print(f"  ✓ {len(M.SLIDES)} slides, {len(M.EXAMPLES)} examples")
    print(f"  ✓ TUTORIAL_REGISTRY length = {len(TUTORIAL_REGISTRY)}")
    return True


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ok = True
    try:
        ok = verify_examples() and ok
        ok = verify_slides() and ok
        ok = verify_contract() and ok
    except AssertionError as e:
        print(f"\n✗ FAIL: {e}")
        sys.exit(1)
    except Exception:
        print("\n✗ Unexpected error:")
        traceback.print_exc()
        sys.exit(1)
    print()
    if ok:
        print("ALL GREEN ✓")
        sys.exit(0)
    else:
        print("FAILED ✗")
        sys.exit(1)
