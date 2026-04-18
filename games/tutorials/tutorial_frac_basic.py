"""
tutorial_frac_basic.py
----------------------
Tutorial content for Fractions: Beginner — adding and subtracting fractions
that already share the same denominator.

Framing
-------
Same denominator means same-sized pieces. The denominator is the *unit* of
the fraction — like "apples" or "fifths". When the units match, combining
fractions is no harder than combining like things: count the pieces up
(addition) or down (subtraction) and the unit itself does not change.

Pedagogy
--------
1. Notice the denominators match — the pieces are the same size.
2. Add or subtract the numerators only.
3. Keep the denominator the same (the piece size did not change).

The renderer (frac_basic.py) intentionally preserves raw numerators and
denominators without auto-simplification, so these slides present results in
the same raw form the pupil will see in the game (5/9 − 2/9 = 3/9, never
1/3). The pitfall slide addresses the single most common mistake: adding
the denominators as well. That would magically shrink the piece size, which
is nonsense.

Slide plan
----------
1. Setup              — "2/5 + 1/5 = ?" laid out, with "numerator" and
                        "denominator" labels.
2. Same piece size    — highlight both denominators; name the piece.
3. Combine the tops   — arrow from the two numerators to the new one.
4. Keep the bottom    — the denominator stays put; explain why.
5. Answer             — final fraction, double-underlined.
6. See it in pieces   — bar model: five parts, shade two, shade one more.
7. Subtraction        — fixed 4/7 − 1/7 = 3/7; same method, count down.
8. Pitfall            — 2/5 + 1/5 ≠ 3/10 with a one-line explanation.

Examples cycle 5 curated problems (headline first). Results stay in raw
form — no simplification — to match how the game renders them.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

from .slideshow_frame import (
    CANVAS_W, CANVAS_H, INK, MUTED, DIM, SOFT, FAINT, ACCENT, GOOD, WARN,
    CARD_BG,
    draw_centered_expression, draw_note, draw_arrow, draw_pill,
)


TITLE = "Fractions: Beginner — adding and subtracting with the same denominator"
LEAD  = "When the bottoms match, just count the pieces."


# Each example has the same denominator on both sides. Results are kept
# in raw form (5/9 − 2/9 = 3/9, not 1/3) to match how the game renders
# questions — frac_basic stores raw numerator/denominator integers and
# does NOT auto-simplify for display.
EXAMPLES = [
    {"a": 2, "b": 1, "d": 5,  "op": "+"},   # 2/5 + 1/5 = 3/5  — headline
    {"a": 3, "b": 4, "d": 8,  "op": "+"},   # 3/8 + 4/8 = 7/8
    {"a": 5, "b": 2, "d": 9,  "op": "-"},   # 5/9 − 2/9 = 3/9  (raw)
    {"a": 1, "b": 4, "d": 6,  "op": "+"},   # 1/6 + 4/6 = 5/6
    {"a": 6, "b": 3, "d": 11, "op": "-"},   # 6/11 − 3/11 = 3/11
]


# ── helpers ──────────────────────────────────────────────────────────────────

def _result(ex):
    """Raw numerator of the answer; denominator is unchanged."""
    return ex["a"] + ex["b"] if ex["op"] == "+" else ex["a"] - ex["b"]


def _op_word(op: str, cap: bool = False) -> str:
    word = "add" if op == "+" else "subtract"
    return word.capitalize() if cap else word


def _count_word(op: str) -> str:
    return "up" if op == "+" else "down"


def _op_glyph(op: str) -> str:
    # Use a proper minus sign (U+2212) for visual weight when subtracting;
    # the in-game prompt uses the same glyph via frac_basic's update.
    return "+" if op == "+" else "−"


def _draw_fraction(canvas, cx, cy, num_text, den_text,
                   num_color=INK, den_color=INK, size=34):
    """Draw a fraction stacked around (cx, cy). Returns (top_y, bottom_y)."""
    font_spec = ("Helvetica", size, "bold")
    num_y = cy - size * 0.65
    den_y = cy + size * 0.65
    canvas.create_text(cx, num_y, text=str(num_text),
                       fill=num_color, font=font_spec)
    canvas.create_text(cx, den_y, text=str(den_text),
                       fill=den_color, font=font_spec)
    # horizontal bar
    half = size * 0.65
    canvas.create_line(cx - half, cy, cx + half, cy,
                       fill=INK, width=2)
    return num_y, den_y


# ── Slide 1 — Setup ──────────────────────────────────────────────────────────

def _slide_1(canvas, ex, w, h):
    a, b, d, op = ex["a"], ex["b"], ex["d"], ex["op"]

    draw_note(canvas, "The question:", 40, color=DIM, size=11)

    # Layout: left fraction, operator, right fraction, equals, question mark
    cy = 130
    gap = 70
    f_cx = [w / 2 - gap * 2.4, w / 2 - gap * 0.6,
            w / 2 + gap * 0.6, w / 2 + gap * 2.4]

    _draw_fraction(canvas, f_cx[0], cy, a, d)
    canvas.create_text(f_cx[1] - 8, cy, text=_op_glyph(op),
                       fill=INK, font=("Helvetica", 34, "bold"))
    _draw_fraction(canvas, f_cx[2], cy, b, d)
    canvas.create_text(f_cx[3] - 8, cy, text="=",
                       fill=DIM, font=("Helvetica", 34, "bold"))
    canvas.create_text(f_cx[3] + 32, cy, text="?",
                       fill=ACCENT, font=("Helvetica", 34, "bold"))

    # Labels pointing to numerator / denominator on the left fraction
    lbl_x = f_cx[0] - 110
    draw_arrow(canvas, lbl_x + 70, cy - 22, f_cx[0] - 18, cy - 22,
               color=DIM, width=1)
    canvas.create_text(lbl_x, cy - 22, anchor="e",
                       text="numerator", fill=DIM,
                       font=("Helvetica", 10, "italic"))

    draw_arrow(canvas, lbl_x + 70, cy + 22, f_cx[0] - 18, cy + 22,
               color=DIM, width=1)
    canvas.create_text(lbl_x, cy + 22, anchor="e",
                       text="denominator", fill=DIM,
                       font=("Helvetica", 10, "italic"))

    # No bottom-of-canvas note on slide 1 — the caption below the card
    # already carries "the top is the count; the bottom is the piece size",
    # and the two text boxes competing on a narrow window looks misaligned.


# ── Slide 2 — Same piece size ────────────────────────────────────────────────

def _slide_2(canvas, ex, w, h):
    a, b, d, op = ex["a"], ex["b"], ex["d"], ex["op"]

    draw_note(canvas, "First, check: do the bottoms match?", 40,
              color=DIM, size=11)

    cy = 130
    gap = 70
    f_cx = [w / 2 - gap * 1.8, w / 2, w / 2 + gap * 1.8]

    _draw_fraction(canvas, f_cx[0], cy, a, d, den_color=GOOD)
    canvas.create_text(f_cx[1], cy, text=_op_glyph(op),
                       fill=INK, font=("Helvetica", 34, "bold"))
    _draw_fraction(canvas, f_cx[2], cy, b, d, den_color=GOOD)

    # Highlight rings around the two denominators. The denominator glyph
    # sits at cy + 34*0.65 ≈ cy + 22; we centre the oval on that point so
    # the ring wraps the digit itself rather than floating below it.
    for cx_den in (f_cx[0], f_cx[2]):
        canvas.create_oval(cx_den - 22, cy + 4, cx_den + 22, cy + 40,
                           outline=GOOD, width=2)

    # Pill connecting them
    draw_pill(canvas, w / 2, cy + 90,
              f"both pieces are {_denom_name(d)}",
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              "Same denominator means same-size pieces — the same unit.",
              h - 30, color=MUTED, size=11)


def _denom_name(d: int) -> str:
    """English ordinal name for a denominator. Falls back to "d-ths"."""
    names = {
        2:  "halves",    3:  "thirds",  4:  "quarters",
        5:  "fifths",    6:  "sixths",  7:  "sevenths",
        8:  "eighths",   9:  "ninths",  10: "tenths",
        11: "elevenths", 12: "twelfths",
    }
    return names.get(d, f"{d}-ths")


# ── Slide 3 — Combine the tops ───────────────────────────────────────────────

def _slide_3(canvas, ex, w, h):
    a, b, d, op = ex["a"], ex["b"], ex["d"], ex["op"]
    res = _result(ex)

    draw_note(canvas,
              f"{_op_word(op, cap=True)} the numerators — the tops only.",
              40, color=DIM, size=11)

    # Top row: the original expression
    cy_top = 110
    gap = 70
    f_cx = [w / 2 - gap * 2.4, w / 2 - gap * 0.6,
            w / 2 + gap * 0.6, w / 2 + gap * 2.4]

    _draw_fraction(canvas, f_cx[0], cy_top, a, d,
                   num_color=ACCENT, den_color=DIM)
    canvas.create_text(f_cx[1] - 8, cy_top, text=_op_glyph(op),
                       fill=INK, font=("Helvetica", 34, "bold"))
    _draw_fraction(canvas, f_cx[2], cy_top, b, d,
                   num_color=ACCENT, den_color=DIM)
    canvas.create_text(f_cx[3] - 8, cy_top, text="=",
                       fill=DIM, font=("Helvetica", 34, "bold"))
    _draw_fraction(canvas, f_cx[3] + 28, cy_top, "?", d,
                   num_color=ACCENT, den_color=DIM)

    # Arrows from the two numerators down to a "sum box"
    sum_y = cy_top + 92
    sum_x = w / 2
    draw_arrow(canvas, f_cx[0], cy_top - 28, sum_x - 34, sum_y - 4,
               color=ACCENT, width=2)
    draw_arrow(canvas, f_cx[2], cy_top - 28, sum_x + 34, sum_y - 4,
               color=ACCENT, width=2)

    # The numerator-only working
    canvas.create_text(sum_x, sum_y,
                       text=f"{a}  {_op_glyph(op)}  {b}  =  {res}",
                       fill=ACCENT, font=("Helvetica", 22, "bold"))

    piece_plural   = _denom_name(d)
    piece_singular = _piece_singular(d)
    left_piece     = piece_singular if a == 1 else piece_plural
    right_piece    = piece_singular if b == 1 else piece_plural
    res_piece      = piece_singular if res == 1 else piece_plural
    draw_note(canvas,
              f'"{a} {left_piece} {_op_glyph(op)} {b} {right_piece} '
              f'= {res} {res_piece}." Like counting apples.',
              h - 30, color=MUTED, size=11)


# ── Slide 4 — Keep the bottom ────────────────────────────────────────────────

def _slide_4(canvas, ex, w, h):
    a, b, d, op = ex["a"], ex["b"], ex["d"], ex["op"]
    res = _result(ex)

    draw_note(canvas, "Keep the denominator the same.", 40,
              color=DIM, size=11)

    # Left: input expression with denominator in green
    cy = 130
    gap = 60
    f_cx = [w / 2 - gap * 3.2, w / 2 - gap * 1.4,
            w / 2 + gap * 0.4, w / 2 + gap * 2.2,
            w / 2 + gap * 3.7]

    _draw_fraction(canvas, f_cx[0], cy, a, d,
                   num_color=DIM, den_color=GOOD, size=30)
    canvas.create_text(f_cx[1] - 8, cy, text=_op_glyph(op),
                       fill=DIM, font=("Helvetica", 30, "bold"))
    _draw_fraction(canvas, f_cx[2], cy, b, d,
                   num_color=DIM, den_color=GOOD, size=30)
    canvas.create_text(f_cx[3] - 8, cy, text="=",
                       fill=DIM, font=("Helvetica", 30, "bold"))
    _draw_fraction(canvas, f_cx[4], cy, res, d,
                   num_color=INK, den_color=GOOD, size=30)

    # Curved "stays put" arrow under the three denominators
    arc_y = cy + 70
    canvas.create_line(f_cx[0], cy + 35, f_cx[0], arc_y,
                       fill=GOOD, width=2)
    canvas.create_line(f_cx[0], arc_y, f_cx[4], arc_y,
                       fill=GOOD, width=2, dash=(4, 3))
    canvas.create_line(f_cx[4], arc_y, f_cx[4], cy + 35,
                       fill=GOOD, width=2)
    draw_pill(canvas, w / 2, arc_y, "the bottom stays",
              bg="#dcfce7", fg=GOOD, size=10)

    draw_note(canvas,
              "The piece size did not change. Only the count did.",
              h - 30, color=MUTED, size=11)


# ── Slide 5 — Answer ─────────────────────────────────────────────────────────

def _slide_5(canvas, ex, w, h):
    a, b, d, op = ex["a"], ex["b"], ex["d"], ex["op"]
    res = _result(ex)

    draw_note(canvas, "Put the numerator and the denominator back together.",
              40, color=DIM, size=11)

    cy = 130
    gap = 70
    f_cx = [w / 2 - gap * 2.4, w / 2 - gap * 0.6,
            w / 2 + gap * 0.6, w / 2 + gap * 2.4]

    _draw_fraction(canvas, f_cx[0], cy, a, d,
                   num_color=DIM, den_color=DIM, size=28)
    canvas.create_text(f_cx[1] - 8, cy, text=_op_glyph(op),
                       fill=DIM, font=("Helvetica", 28, "bold"))
    _draw_fraction(canvas, f_cx[2], cy, b, d,
                   num_color=DIM, den_color=DIM, size=28)
    canvas.create_text(f_cx[3] - 8, cy, text="=",
                       fill=INK, font=("Helvetica", 34, "bold"))
    _draw_fraction(canvas, f_cx[3] + 32, cy, res, d,
                   num_color=GOOD, den_color=GOOD, size=36)

    # Double underline under the answer
    u_x_left  = f_cx[3] + 32 - 30
    u_x_right = f_cx[3] + 32 + 30
    u_y       = cy + 42
    canvas.create_line(u_x_left, u_y,     u_x_right, u_y,     fill=GOOD, width=2)
    canvas.create_line(u_x_left, u_y + 5, u_x_right, u_y + 5, fill=GOOD, width=2)

    draw_pill(canvas, w / 2, cy + 90,
              f"answer: {res}/{d}", bg="#dcfce7", fg=GOOD, size=12)

    draw_note(canvas,
              f"{a}/{d} {_op_glyph(op)} {b}/{d} = {res}/{d}.",
              h - 30, color=MUTED, size=11)


# ── Slide 6 — See it in pieces (bar model) ───────────────────────────────────

def _slide_6(canvas, ex, w, h):
    a, b, d, op = ex["a"], ex["b"], ex["d"], ex["op"]
    res = _result(ex)

    draw_note(canvas,
              f"Same idea, drawn as pieces. Each piece is one {_piece_singular(d)}.",
              38, color=DIM, size=11)

    # A single bar split into d equal parts. Shading depends on op:
    #   addition:    shade a in ACCENT, then shade b more in GOOD (ending at a+b)
    #   subtraction: shade a in ACCENT, then un-shade b from the right end
    #                (so the remaining shaded count is a - b)
    bar_y  = 110
    bar_h  = 50
    margin = 70
    bar_x1 = margin
    bar_x2 = w - margin
    seg_w  = (bar_x2 - bar_x1) / d

    # outline
    canvas.create_rectangle(bar_x1, bar_y, bar_x2, bar_y + bar_h,
                            outline=INK, width=2, fill=CARD_BG)

    if op == "+":
        # Shade first `a` in ACCENT, next `b` in GOOD
        for i in range(a):
            canvas.create_rectangle(
                bar_x1 + i * seg_w, bar_y,
                bar_x1 + (i + 1) * seg_w, bar_y + bar_h,
                outline=INK, width=1, fill="#c7d2fe")
        for i in range(a, a + b):
            canvas.create_rectangle(
                bar_x1 + i * seg_w, bar_y,
                bar_x1 + (i + 1) * seg_w, bar_y + bar_h,
                outline=INK, width=1, fill="#bbf7d0")
        for i in range(a + b, d):
            canvas.create_rectangle(
                bar_x1 + i * seg_w, bar_y,
                bar_x1 + (i + 1) * seg_w, bar_y + bar_h,
                outline=INK, width=1, fill=SOFT)
    else:
        # Start with `a` shaded; the last `b` of those get crossed off.
        for i in range(a):
            fill = "#c7d2fe" if i < a - b else "#fecaca"
            canvas.create_rectangle(
                bar_x1 + i * seg_w, bar_y,
                bar_x1 + (i + 1) * seg_w, bar_y + bar_h,
                outline=INK, width=1, fill=fill)
            # draw a cross on the removed ones
            if i >= a - b:
                canvas.create_line(
                    bar_x1 + i * seg_w,       bar_y,
                    bar_x1 + (i + 1) * seg_w, bar_y + bar_h,
                    fill=WARN, width=2)
                canvas.create_line(
                    bar_x1 + (i + 1) * seg_w, bar_y,
                    bar_x1 + i * seg_w,       bar_y + bar_h,
                    fill=WARN, width=2)
        for i in range(a, d):
            canvas.create_rectangle(
                bar_x1 + i * seg_w, bar_y,
                bar_x1 + (i + 1) * seg_w, bar_y + bar_h,
                outline=INK, width=1, fill=SOFT)

    # tick marks under the bar
    for i in range(d + 1):
        x = bar_x1 + i * seg_w
        canvas.create_line(x, bar_y + bar_h, x, bar_y + bar_h + 6,
                           fill=DIM, width=1)

    # Explicit fraction expression below the bar — makes the bridge from
    # "coloured pieces" to "fraction arithmetic" direct for the pupil.
    # Accent colour on the left and GOOD on the result so the eye links
    # each coloured segment in the bar to the matching part of the formula.
    expr_y = bar_y + bar_h + 34
    canvas.create_text(w / 2, expr_y,
                       text=f"{a}/{d}   {_op_glyph(op)}   {b}/{d}   =   {res}/{d}",
                       fill=ACCENT, font=("Helvetica", 22, "bold"))

    # Caption row underneath the expression
    if op == "+":
        story = (f"Start with {a}/{d} shaded (blue). "
                 f"Shade {b} more piece{'s' if b != 1 else ''} (green). "
                 f"Count the shaded: {res}. So the answer is {res}/{d}.")
    else:
        story = (f"Start with {a}/{d} shaded. "
                 f"Cross off {b} piece{'s' if b != 1 else ''} from the right. "
                 f"Count what is left: {res}. So the answer is {res}/{d}.")
    canvas.create_text(w / 2, expr_y + 38,
                       text=story, fill=MUTED,
                       font=("Helvetica", 11),
                       width=w - 80, justify="center")

    draw_note(canvas,
              "The pieces are all the same size — that is what 'same denominator' means.",
              h - 30, color=MUTED, size=11)


def _piece_singular(d: int) -> str:
    # Handle the irregular plurals first, then fall back to "chop the s".
    irregular = {2: "half"}
    if d in irregular:
        return irregular[d]
    name = _denom_name(d)
    if name.endswith("s"):
        return name[:-1]
    return name


# ── Slide 7 — Subtraction works the same way ─────────────────────────────────
#
# Fixed example on this slide (4/7 − 1/7 = 3/7) regardless of the current
# cycled example — this slide is about the *idea* that the method is
# identical for subtraction, not a second application of the current problem.

def _slide_7(canvas, ex, w, h):
    draw_note(canvas,
              "Subtraction works the same way — you just count down instead of up.",
              38, color=DIM, size=11)

    # Compact 4/7 − 1/7 = 3/7 walkthrough
    cy = 110
    gap = 60
    f_cx = [w / 2 - gap * 3.2, w / 2 - gap * 1.4,
            w / 2 + gap * 0.4, w / 2 + gap * 2.2,
            w / 2 + gap * 3.7]

    _draw_fraction(canvas, f_cx[0], cy, 4, 7, size=28)
    canvas.create_text(f_cx[1] - 8, cy, text="−",
                       fill=INK, font=("Helvetica", 28, "bold"))
    _draw_fraction(canvas, f_cx[2], cy, 1, 7, size=28)
    canvas.create_text(f_cx[3] - 8, cy, text="=",
                       fill=DIM, font=("Helvetica", 28, "bold"))
    _draw_fraction(canvas, f_cx[4], cy, 3, 7, size=28,
                   num_color=GOOD, den_color=GOOD)

    # numerator working line
    canvas.create_text(w / 2, cy + 90,
                       text="4  −  1  =  3",
                       fill=ACCENT, font=("Helvetica", 20, "bold"))
    draw_pill(canvas, w / 2, cy + 128,
              "denominator stays 7", bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              '"4 sevenths take away 1 seventh leaves 3 sevenths."',
              h - 30, color=MUTED, size=11)


# ── Slide 8 — The pitfall ────────────────────────────────────────────────────
#
# Fixed example: 2/5 + 1/5. Contrasts the correct answer (3/5) with the
# very common wrong answer (3/10) and explains why in one line.

def _slide_8(canvas, ex, w, h):
    draw_note(canvas, "Watch out for this common mistake.", 40,
              color=DIM, size=11)

    cy = 120
    left_cx  = w / 2 - 150
    right_cx = w / 2 + 150
    gap = 50

    # Left column: correct
    tk_red = "#dc2626"
    canvas.create_text(left_cx, cy - 70, text="Correct",
                       fill=GOOD, font=("Helvetica", 11, "bold"))
    _draw_fraction(canvas, left_cx - gap * 0.9, cy, 2, 5, size=24)
    canvas.create_text(left_cx - 8, cy, text="+",
                       fill=INK, font=("Helvetica", 24, "bold"))
    _draw_fraction(canvas, left_cx + gap * 0.9, cy, 1, 5, size=24)
    canvas.create_text(left_cx + gap * 1.7, cy, text="=",
                       fill=DIM, font=("Helvetica", 24, "bold"))
    _draw_fraction(canvas, left_cx + gap * 2.5, cy, 3, 5, size=24,
                   num_color=GOOD, den_color=GOOD)

    # Right column: wrong
    canvas.create_text(right_cx, cy - 70, text="Wrong",
                       fill=tk_red, font=("Helvetica", 11, "bold"))
    _draw_fraction(canvas, right_cx - gap * 0.9, cy, 2, 5, size=24,
                   num_color=DIM, den_color=DIM)
    canvas.create_text(right_cx - 8, cy, text="+",
                       fill=DIM, font=("Helvetica", 24, "bold"))
    _draw_fraction(canvas, right_cx + gap * 0.9, cy, 1, 5, size=24,
                   num_color=DIM, den_color=DIM)
    canvas.create_text(right_cx + gap * 1.7, cy, text="=",
                       fill=DIM, font=("Helvetica", 24, "bold"))
    _draw_fraction(canvas, right_cx + gap * 2.5, cy, 3, 10, size=24,
                   num_color=tk_red, den_color=tk_red)

    # Big "not equals" between the two columns (small, just visually)
    # — actually omitted; labels carry the contrast clearly.

    # Explanation strip — measure-then-draw for a tight centred pill.
    body = ("Adding the bottoms would turn fifths into tenths — "
            "the piece size would magically shrink. The pieces did not "
            "change size, so the denominator does not change either.")
    probe = canvas.create_text(0, -9999, text=body,
                               font=("Helvetica", 11), anchor="w")
    bx1, _, bx2, _ = canvas.bbox(probe)
    canvas.delete(probe)
    box_w = min(bx2 - bx1 + 32, w - 80)
    box_x = (w - box_w) / 2
    box_y = h - 70
    canvas.create_rectangle(box_x, box_y - 24, box_x + box_w, box_y + 24,
                            fill=SOFT, outline="")
    canvas.create_text(w / 2, box_y, text=body,
                       fill=MUTED, font=("Helvetica", 11),
                       width=box_w - 24, justify="center")

    draw_note(canvas,
              "Keep the denominator. Always.",
              h - 22, color=WARN, size=11)


# ── Slide list (what the framework consumes) ─────────────────────────────────

SLIDES = [
    {
        "title":   "1 · Read the question",
        "caption": ("Two fractions with the same bottom number. "
                    "The top is the count; the bottom is the piece size."),
        "draw":    _slide_1,
    },
    {
        "title":   "2 · Same piece size",
        "caption": ("Both fractions have the same denominator, so both are "
                    "counting the same kind of piece. That is what makes "
                    "this case easy."),
        "draw":    _slide_2,
    },
    {
        "title":   "3 · Combine the tops",
        "caption": ("Only the numerators change. Add them (or subtract them) "
                    "just like counting like things — apples with apples, "
                    "fifths with fifths."),
        "draw":    _slide_3,
    },
    {
        "title":   "4 · Keep the bottom",
        "caption": ("The denominator does NOT get added. The piece size did "
                    "not change during the operation, so the bottom number "
                    "stays exactly the same."),
        "draw":    _slide_4,
    },
    {
        "title":   "5 · Answer",
        "caption": ("Write the new numerator over the unchanged denominator. "
                    "That is the final answer."),
        "draw":    _slide_5,
    },
    {
        "title":   "6 · See it in pieces",
        "caption": ("A picture of the same idea. The bar is cut into equal "
                    "pieces; shading (or crossing off) gives the answer."),
        "draw":    _slide_6,
    },
    {
        "title":   "7 · Subtraction works the same way",
        "caption": ("Subtracting fractions with the same denominator uses "
                    "the exact same method — count down instead of up, and "
                    "the denominator still stays put."),
        "draw":    _slide_7,
    },
    {
        "title":   "8 · Watch the pitfall",
        "caption": ("A very common mistake: adding the denominators too. "
                    "Do not. The piece size never changes."),
        "draw":    _slide_8,
    },
]
