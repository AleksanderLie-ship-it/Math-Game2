"""
verify_mult_intermediate.py
---------------------------
Headless verification harness for tutorial_mult_intermediate.

Checks (per example):
  1. top * bot == answer                         (EXAMPLES invariant)
  2. _mult_steps produces one step per digit of `bot`
  3. Every step.product == step.digit_val * top
  4. Sum of step.product × 10^step.digit_pos == answer
  5. padded_str == str(product) + "X" * digit_pos

Checks (per slide):
  - Every slide draws on a MockCanvas without raising, across every
    example in EXAMPLES. Per-slide total draw counts are printed so a
    regression in the rendering path shows up as a divergent total.

Run:  python verify_mult_intermediate.py
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

from __future__ import annotations

import sys
import traceback


# ── MockCanvas ──────────────────────────────────────────────────────────────

class MockCanvas:
    def __init__(self):
        self.calls = []
        self._next_id = 1
        self._items = {}

    def _new_id(self):
        i = self._next_id
        self._next_id += 1
        return i

    def create_text(self, x, y, **kw):
        i = self._new_id()
        self.calls.append(("text", x, y, kw))
        text = str(kw.get("text", ""))
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
        xs = list(coords[::2])
        ys = list(coords[1::2])
        self._items[i] = (min(xs), min(ys), max(xs), max(ys))
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
        if i in self._items:
            del self._items[i]
        self.calls.append(("delete", i))

    def bbox(self, i):
        return self._items.get(i, (0, 0, 0, 0))


# ── Import targets ─────────────────────────────────────────────────────────

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

from games.tutorials import tutorial_mult_intermediate as M   # noqa: E402
from games.tutorials.slideshow_frame import CANVAS_W, CANVAS_H   # noqa: E402


# ── Example-level invariants ────────────────────────────────────────────────

def verify_examples():
    print("── EXAMPLE invariants ─────────────────────────────────────────────")
    for i, ex in enumerate(M.EXAMPLES):
        top, bot, answer = ex["top"], ex["bot"], ex["answer"]
        tag = f"[{i}] {top} × {bot} = {answer}"

        assert top * bot == answer, (
            f"{tag}: top * bot ({top*bot}) != answer ({answer})"
        )

        steps = M._mult_steps(top, bot)
        assert len(steps) == len(str(bot)), (
            f"{tag}: step count {len(steps)} != digits of bot ({len(str(bot))})"
        )

        # Per-step checks
        for k, s in enumerate(steps):
            expected_digit = int(str(bot)[-(k + 1)])
            assert s["digit_val"] == expected_digit, (
                f"{tag} step {k}: digit_val {s['digit_val']} != {expected_digit}"
            )
            assert s["digit_pos"] == k, \
                f"{tag} step {k}: digit_pos {s['digit_pos']} != {k}"
            assert s["product"] == top * s["digit_val"], (
                f"{tag} step {k}: product {s['product']} != {top}*{s['digit_val']}"
            )
            assert s["padded_str"] == str(s["product"]) + "X" * k, (
                f"{tag} step {k}: padded_str mismatch "
                f"(got {s['padded_str']!r})"
            )

        # Sum invariant: sum(product × 10^pos) == answer
        total = sum(s["product"] * (10 ** s["digit_pos"]) for s in steps)
        assert total == answer, \
            f"{tag}: step sum {total} != answer {answer}"

        print(f"  ✓ {tag}  — {len(steps)} partial(s)")
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

    from games.tutorials import TUTORIAL_REGISTRY
    assert "mult_intermediate" in TUTORIAL_REGISTRY, \
        "TUTORIAL_REGISTRY is missing mult_intermediate"
    assert len(TUTORIAL_REGISTRY) == 7, \
        f"TUTORIAL_REGISTRY length should be 7, got {len(TUTORIAL_REGISTRY)}"

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
