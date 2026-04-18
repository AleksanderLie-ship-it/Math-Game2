"""
tutorial_frac_intermediate.py
-----------------------------
Tutorial content for Fractions: Intermediate — adding and subtracting
fractions with DIFFERENT denominators.

Framing
-------
Different denominators means different-sized pieces. You cannot count
thirds and quarters together any more than you can count apples and
oranges as one kind of thing. The fix is to cut both fractions into a
*common* piece size — the Least Common Multiple (LCM) of the two
denominators. Once both bottoms match, the problem collapses to the
frac_basic case: add (or subtract) the numerators, keep the denominator.

Pedagogy (in order)
-------------------
1. Notice the bottoms are different — the pieces are not the same size.
2. Find a common denominator (LCM).
3. Rewrite each fraction with that denominator (multiply top AND bottom
   by the same number — no change in value, just smaller pieces).
4. Now the bottoms match — add/subtract the numerators, keep the bottom.
5. Reduce the final answer if it can be simplified.
6. Pitfall: never add the bottoms, and never stretch only the numerator.

Examples cycle 5 curated problems (headline first). The five include one
reducer (5/6 − 1/2 = 2/6 → 1/3) so the pupil meets the reduce step
inside the carousel. Raw numerators / denominators are handled with
plain ints — fractions.Fraction auto-reduces on construction, which
would silently turn "8/12" into "2/3" and destroy the whole teaching
point of this pack.

Slide plan
----------
1. Read the question    — show a/b op c/d = ?; highlight the mismatched bottoms.
2. Pieces don't match   — two bars cut in different numbers of pieces.
3. Find the LCM         — list the multiples of each denominator; ring the first hit.
4. Rewrite the left     — a/b × (m/m) = (a·m)/LCM; ×m in accent on top AND bottom.
5. Rewrite the right    — c/d × (n/n) = (c·n)/LCM.
6. Same denominator now — (a·m)/LCM op (c·n)/LCM = (result)/LCM, frac_basic style.
7. Reduce if possible   — if gcd(result, LCM) > 1, divide both by it; otherwise
                          note "already in lowest terms" and show a fixed mini
                          demo so the pupil still sees the technique.
8. Pitfall              — 2/3 + 1/4 ≠ 3/7 (can't add bottoms) and ≠ 3/12
                          (must rewrite the tops too).
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

from math import gcd

from .slideshow_frame import (
    CANVAS_W, CANVAS_H, INK, MUTED, DIM, SOFT, FAINT, ACCENT, GOOD, WARN,
    CARD_BG,
    draw_centered_expression, draw_note, draw_arrow, draw_pill,
)


TITLE = "Fractions: Intermediate — unlike denominators"
LEAD  = "Make the pieces the same size first. Then it's just like Beginner."


# ── Examples ─────────────────────────────────────────────────────────────────
#
# Raw ints; never Fraction (auto-reduction would hide the teaching step).
# Five curated problems. Headline first. The fifth is a reducer so the pupil
# meets the "divide by the gcd" step inside the cycle.
EXAMPLES = [
    # 2/3 + 1/4 = 8/12 + 3/12 = 11/12               (no reduce — headline)
    {"a_num": 2, "a_den": 3, "b_num": 1, "b_den": 4, "op": "+"},
    # 1/2 + 1/3 = 3/6 + 2/6 = 5/6                   (no reduce)
    {"a_num": 1, "a_den": 2, "b_num": 1, "b_den": 3, "op": "+"},
    # 3/4 − 1/3 = 9/12 − 4/12 = 5/12                (no reduce)
    {"a_num": 3, "a_den": 4, "b_num": 1, "b_den": 3, "op": "-"},
    # 2/5 + 1/2 = 4/10 + 5/10 = 9/10                (no reduce)
    {"a_num": 2, "a_den": 5, "b_num": 1, "b_den": 2, "op": "+"},
    # 5/6 − 1/2 = 5/6 − 3/6 = 2/6 → 1/3             (REDUCER)
    {"a_num": 5, "a_den": 6, "b_num": 1, "b_den": 2, "op": "-"},
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _lcm(a: int, b: int) -> int:
    return a * b // gcd(a, b)


def _rewrite(ex):
    """Return (common_d, a_new, a_mult, b_new, b_mult) for the example."""
    d      = _lcm(ex["a_den"], ex["b_den"])
    a_mult = d // ex["a_den"]
    b_mult = d // ex["b_den"]
    a_new  = ex["a_num"] * a_mult
    b_new  = ex["b_num"] * b_mult
    return d, a_new, a_mult, b_new, b_mult


def _result_raw(ex):
    """Raw result numerator and the common denominator, before reducing."""
    d, a_new, _, b_new, _ = _rewrite(ex)
    raw = a_new + b_new if ex["op"] == "+" else a_new - b_new
    return raw, d


def _result_reduced(ex):
    """Return (reduced_num, reduced_den, gcd_used). gcd_used is 1 when no
    reduction was applied."""
    raw, d = _result_raw(ex)
    g = gcd(abs(raw), d) or 1
    return raw // g, d // g, g


def _op_word(op: str, cap: bool = False) -> str:
    word = "add" if op == "+" else "subtract"
    return word.capitalize() if cap else word


def _op_glyph(op: str) -> str:
    # Real minus sign (U+2212), consistent with frac_basic and the
    # in-game prompt.
    return "+" if op == "+" else "−"


def _draw_fraction(canvas, cx, cy, num_text, den_text,
                   num_color=INK, den_color=INK, size=30):
    """Draw a fraction stacked around (cx, cy). Returns (top_y, bottom_y)."""
    font_spec = ("Helvetica", size, "bold")
    num_y = cy - size * 0.65
    den_y = cy + size * 0.65
    canvas.create_text(cx, num_y, text=str(num_text),
                       fill=num_color, font=font_spec)
    canvas.create_text(cx, den_y, text=str(den_text),
                       fill=den_color, font=font_spec)
    half = size * 0.65
    canvas.create_line(cx - half, cy, cx + half, cy,
                       fill=INK, width=2)
    return num_y, den_y


# ── Slide 1 — Read the question ──────────────────────────────────────────────

def _slide_1(canvas, ex, w, h):
    a_num, a_den = ex["a_num"], ex["a_den"]
    b_num, b_den = ex["b_num"], ex["b_den"]
    op = ex["op"]

    draw_note(canvas, "The question:", 38, color=DIM, size=11)

    # Lay out:  a/b  op  c/d  =  ?
    cy  = 130
    gap = 70
    f_cx = [w / 2 - gap * 2.4, w / 2 - gap * 0.6,
            w / 2 + gap * 0.6, w / 2 + gap * 2.4]

    _draw_fraction(canvas, f_cx[0], cy, a_num, a_den, den_color=WARN, size=32)
    canvas.create_text(f_cx[1] - 8, cy, text=_op_glyph(op),
                       fill=INK, font=("Helvetica", 32, "bold"))
    _draw_fraction(canvas, f_cx[2], cy, b_num, b_den, den_color=WARN, size=32)
    canvas.create_text(f_cx[3] - 8, cy, text="=",
                       fill=DIM, font=("Helvetica", 32, "bold"))
    canvas.create_text(f_cx[3] + 32, cy, text="?",
                       fill=ACCENT, font=("Helvetica", 32, "bold"))

    # Single amber pill under the equation carries the mismatch message.
    # The WARN-coloured denominators in the fractions above already show
    # WHICH numbers don't match; the pill names the problem plainly.
    draw_pill(canvas, w / 2, cy + 82,
              f"the bottoms: {a_den} ≠ {b_den}",
              bg="#fef3c7", fg=WARN, size=12)

    draw_note(canvas,
              "The bottoms are different — the pieces are not the same size yet.",
              h - 28, color=MUTED, size=11)


# ── Slide 2 — Pieces don't match ─────────────────────────────────────────────

def _slide_2(canvas, ex, w, h):
    a_den = ex["a_den"]
    b_den = ex["b_den"]

    draw_note(canvas,
              "Two bars of the same length, cut into different pieces:",
              38, color=DIM, size=11)

    # Two bars stacked, same width, split into a_den and b_den segments.
    bar_x1 = 110
    bar_x2 = w - 110
    bar_h  = 40
    top_y  = 85
    gap    = 36
    bot_y  = top_y + bar_h + gap

    def _draw_bar(y, d, label, tint):
        canvas.create_rectangle(bar_x1, y, bar_x2, y + bar_h,
                                outline=INK, width=2, fill=CARD_BG)
        seg = (bar_x2 - bar_x1) / d
        for i in range(d):
            canvas.create_rectangle(bar_x1 + i * seg, y,
                                    bar_x1 + (i + 1) * seg, y + bar_h,
                                    outline=INK, width=1, fill=tint)
        canvas.create_text(bar_x1 - 16, y + bar_h / 2, anchor="e",
                           text=label, fill=MUTED,
                           font=("Helvetica", 11, "bold"))

    _draw_bar(top_y, a_den, f"cut in {a_den}", "#e0e7ff")
    _draw_bar(bot_y, b_den, f"cut in {b_den}", "#fee2e2")

    # Pill under both bars
    draw_pill(canvas, w / 2, bot_y + bar_h + 30,
              f"one {_piece_sg(a_den)} ≠ one {_piece_sg(b_den)}",
              bg="#fef3c7", fg=WARN, size=11)

    draw_note(canvas,
              "You can't count pieces of different sizes together. "
              "Make them match first.",
              h - 28, color=MUTED, size=11)


def _piece_sg(d: int) -> str:
    """Singular name of a 1/d piece. Falls back to '1/d'."""
    singular = {
        2: "half", 3: "third", 4: "quarter", 5: "fifth",
        6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth",
        10: "tenth", 11: "eleventh", 12: "twelfth",
    }
    return singular.get(d, f"1/{d}")


# ── Slide 3 — Find the LCM ───────────────────────────────────────────────────

def _slide_3(canvas, ex, w, h):
    a_den = ex["a_den"]
    b_den = ex["b_den"]
    d     = _lcm(a_den, b_den)

    draw_note(canvas,
              f"Find the smallest number that both {a_den} and "
              f"{b_den} divide into (the Lowest Common Denominator).",
              36, color=DIM, size=11)

    # Build multiples up to and including the LCM
    row1 = [a_den * i for i in range(1, d // a_den + 1)]
    row2 = [b_den * i for i in range(1, d // b_den + 1)]

    # Render two rows of coloured chips
    label_x = 90
    cx_start = 190
    spacing  = min(72, (w - cx_start - 40) / max(len(row1), len(row2)))

    def _draw_row(y, label, vals, tint):
        canvas.create_text(label_x, y, anchor="w", text=label,
                           fill=MUTED, font=("Helvetica", 12, "bold"))
        for i, v in enumerate(vals):
            cx = cx_start + i * spacing
            is_lcm = v == d
            fill = "#dcfce7" if is_lcm else tint
            ring = GOOD if is_lcm else DIM
            canvas.create_oval(cx - 20, y - 18, cx + 20, y + 18,
                               fill=fill, outline=ring, width=2 if is_lcm else 1)
            fg = GOOD if is_lcm else INK
            canvas.create_text(cx, y, text=str(v), fill=fg,
                               font=("Helvetica", 13, "bold"))

    _draw_row(100, f"×{a_den}:", row1, "#e0e7ff")
    _draw_row(155, f"×{b_den}:", row2, "#fee2e2")

    # Pill pointing to the match
    draw_pill(canvas, w / 2, 215,
              f"both lists hit {d}  →  common denominator = {d}",
              bg="#dcfce7", fg=GOOD, size=12)

    draw_note(canvas,
              f'"Walk the {a_den}-times and {b_den}-times tables until '
              f'you land on the same number."',
              h - 28, color=MUTED, size=11)


# ── Slide 4 — Rewrite the left fraction ──────────────────────────────────────

def _slide_4(canvas, ex, w, h):
    a_num, a_den = ex["a_num"], ex["a_den"]
    d, a_new, a_mult, _, _ = _rewrite(ex)

    draw_note(canvas,
              f"Rewrite the LEFT fraction with {d} on the bottom.",
              38, color=DIM, size=11)

    # Layout:  a/den  ×  m/m  =  a_new/d
    cy  = 135
    f_cx = [w / 2 - 220, w / 2 - 80, w / 2 + 40, w / 2 + 180]

    _draw_fraction(canvas, f_cx[0], cy, a_num, a_den, size=30)
    canvas.create_text(f_cx[1] - 14, cy, text="×",
                       fill=INK, font=("Helvetica", 28, "bold"))
    _draw_fraction(canvas, f_cx[1] + 30, cy, a_mult, a_mult,
                   num_color=ACCENT, den_color=ACCENT, size=30)
    canvas.create_text(f_cx[2] + 30, cy, text="=",
                       fill=DIM, font=("Helvetica", 28, "bold"))
    _draw_fraction(canvas, f_cx[3], cy, a_new, d,
                   num_color=GOOD, den_color=GOOD, size=30)

    # Accent ×m callouts ABOVE the numerator and BELOW the denominator.
    # A size=30 glyph spans roughly cy±34; labels at cy±66 give 32px
    # clearance; arrows stop at cy±44, 10px outside the glyph top/bottom,
    # so the arrowhead never pierces into a digit. (v0.7.3 post-pupil-test fix.)
    canvas.create_text(f_cx[0], cy - 66, text=f"×{a_mult}",
                       fill=ACCENT, font=("Helvetica", 11, "bold"))
    canvas.create_text(f_cx[0], cy + 66, text=f"×{a_mult}",
                       fill=ACCENT, font=("Helvetica", 11, "bold"))
    draw_arrow(canvas, f_cx[0], cy - 56, f_cx[0], cy - 44,
               color=ACCENT, width=2)
    draw_arrow(canvas, f_cx[0], cy + 56, f_cx[0], cy + 44,
               color=ACCENT, width=2)

    draw_pill(canvas, w / 2, cy + 95,
              f"same value — each {_piece_sg(a_den)} is just cut into "
              f"{a_mult} smaller equal pieces",
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              "Multiply the top AND the bottom by the same number. "
              "The value doesn't change.",
              h - 28, color=MUTED, size=11)


# ── Slide 5 — Rewrite the right fraction ─────────────────────────────────────

def _slide_5(canvas, ex, w, h):
    b_num, b_den = ex["b_num"], ex["b_den"]
    d, _, _, b_new, b_mult = _rewrite(ex)

    draw_note(canvas,
              f"Now the RIGHT fraction — same trick, same {d}.",
              38, color=DIM, size=11)

    cy = 135
    f_cx = [w / 2 - 220, w / 2 - 80, w / 2 + 40, w / 2 + 180]

    _draw_fraction(canvas, f_cx[0], cy, b_num, b_den, size=30)
    canvas.create_text(f_cx[1] - 14, cy, text="×",
                       fill=INK, font=("Helvetica", 28, "bold"))
    _draw_fraction(canvas, f_cx[1] + 30, cy, b_mult, b_mult,
                   num_color=ACCENT, den_color=ACCENT, size=30)
    canvas.create_text(f_cx[2] + 30, cy, text="=",
                       fill=DIM, font=("Helvetica", 28, "bold"))
    _draw_fraction(canvas, f_cx[3], cy, b_new, d,
                   num_color=GOOD, den_color=GOOD, size=30)

    # Same ×m layout as slide 4 — labels at cy±66, arrows stop at cy±44
    # (10px clear of the size=30 glyph edges at cy±34).
    canvas.create_text(f_cx[0], cy - 66, text=f"×{b_mult}",
                       fill=ACCENT, font=("Helvetica", 11, "bold"))
    canvas.create_text(f_cx[0], cy + 66, text=f"×{b_mult}",
                       fill=ACCENT, font=("Helvetica", 11, "bold"))
    draw_arrow(canvas, f_cx[0], cy - 56, f_cx[0], cy - 44,
               color=ACCENT, width=2)
    draw_arrow(canvas, f_cx[0], cy + 56, f_cx[0], cy + 44,
               color=ACCENT, width=2)

    draw_pill(canvas, w / 2, cy + 95,
              f"{b_num}/{b_den}  =  {b_new}/{d}",
              bg="#dcfce7", fg=GOOD, size=12)

    draw_note(canvas,
              "Both fractions now have the same bottom. We're ready to combine.",
              h - 28, color=MUTED, size=11)


# ── Slide 6 — Same denominator, now combine ──────────────────────────────────

def _slide_6(canvas, ex, w, h):
    op = ex["op"]
    d, a_new, _, b_new, _ = _rewrite(ex)
    raw, _ = _result_raw(ex)

    draw_note(canvas,
              f"Both bottoms are now {d}. {_op_word(op, cap=True)} the "
              f"numerators — the bottom stays.",
              38, color=DIM, size=11)

    # Top row: a_new/d  op  b_new/d  =  raw/d
    cy = 110
    gap = 70
    f_cx = [w / 2 - gap * 2.4, w / 2 - gap * 0.6,
            w / 2 + gap * 0.6, w / 2 + gap * 2.4]

    _draw_fraction(canvas, f_cx[0], cy, a_new, d,
                   num_color=ACCENT, den_color=DIM, size=28)
    canvas.create_text(f_cx[1] - 8, cy, text=_op_glyph(op),
                       fill=INK, font=("Helvetica", 28, "bold"))
    _draw_fraction(canvas, f_cx[2], cy, b_new, d,
                   num_color=ACCENT, den_color=DIM, size=28)
    canvas.create_text(f_cx[3] - 8, cy, text="=",
                       fill=DIM, font=("Helvetica", 28, "bold"))
    _draw_fraction(canvas, f_cx[3] + 28, cy, raw, d,
                   num_color=GOOD, den_color=GOOD, size=30)

    # Numerator working line with individually-placed tokens so arrows aim true.
    sum_y   = cy + 92
    sum_x   = w / 2
    tok_gap = 36
    x_a   = sum_x - 2 * tok_gap
    x_op  = sum_x - 1 * tok_gap
    x_b   = sum_x
    x_eq  = sum_x + 1 * tok_gap
    x_res = sum_x + 2 * tok_gap
    for tx, ts in ((x_a, str(a_new)), (x_op, _op_glyph(op)),
                   (x_b, str(b_new)), (x_eq, "="), (x_res, str(raw))):
        canvas.create_text(tx, sum_y, text=ts, fill=ACCENT,
                           font=("Helvetica", 22, "bold"))

    # Arrows from the numerators down to the matching digits in the
    # working line (endpoint just above the 22pt cap so the arrowhead
    # touches the digit, not overlapping it).
    draw_arrow(canvas, f_cx[0], cy - 24, x_a, sum_y - 14,
               color=ACCENT, width=2)
    draw_arrow(canvas, f_cx[2], cy - 24, x_b, sum_y - 14,
               color=ACCENT, width=2)

    draw_pill(canvas, w / 2, sum_y + 42,
              f"denominator stays {d}",
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              "Same piece size on both sides — so this is just the Beginner case now.",
              h - 28, color=MUTED, size=11)


# ── Slide 7 — Reduce if possible ─────────────────────────────────────────────

def _slide_7(canvas, ex, w, h):
    raw, d_raw          = _result_raw(ex)
    red_n, red_d, g     = _result_reduced(ex)

    if g > 1:
        draw_note(canvas,
                  f"Check: can {raw}/{d_raw} be simplified?",
                  38, color=DIM, size=11)

        # raw/d_raw  ÷g/g  =  red/red_d
        cy   = 130
        f_cx = [w / 2 - 200, w / 2 - 40, w / 2 + 80, w / 2 + 210]

        _draw_fraction(canvas, f_cx[0], cy, raw, d_raw, size=32)
        canvas.create_text(f_cx[1] - 10, cy, text="÷",
                           fill=INK, font=("Helvetica", 28, "bold"))
        _draw_fraction(canvas, f_cx[1] + 30, cy, g, g,
                       num_color=ACCENT, den_color=ACCENT, size=30)
        canvas.create_text(f_cx[2] + 30, cy, text="=",
                           fill=DIM, font=("Helvetica", 28, "bold"))
        _draw_fraction(canvas, f_cx[3], cy, red_n, red_d,
                       num_color=GOOD, den_color=GOOD, size=34)

        # ÷g accent labels well clear of the size=32 glyphs (spans cy±36).
        # Labels at cy±70, arrow tips at cy±46 — 10px outside each glyph.
        canvas.create_text(f_cx[0], cy - 70, text=f"÷{g}",
                           fill=ACCENT, font=("Helvetica", 11, "bold"))
        canvas.create_text(f_cx[0], cy + 70, text=f"÷{g}",
                           fill=ACCENT, font=("Helvetica", 11, "bold"))
        draw_arrow(canvas, f_cx[0], cy - 60, f_cx[0], cy - 46,
                   color=ACCENT, width=2)
        draw_arrow(canvas, f_cx[0], cy + 60, f_cx[0], cy + 46,
                   color=ACCENT, width=2)

        # Double underline under the reduced answer (size=34 glyph → bottom
        # at cy+38; underline pair at cy+52 / cy+57, clear of the glyph).
        u_half = 38
        u_x_left  = f_cx[3] - u_half
        u_x_right = f_cx[3] + u_half
        u_y       = cy + 52
        canvas.create_line(u_x_left, u_y,     u_x_right, u_y,     fill=GOOD, width=2)
        canvas.create_line(u_x_left, u_y + 5, u_x_right, u_y + 5, fill=GOOD, width=2)

        draw_pill(canvas, w / 2, cy + 105,
                  f"greatest common divisor = {g} — divide top and bottom by {g}",
                  bg="#dcfce7", fg=GOOD, size=11)

        draw_note(canvas,
                  "Top and bottom share a factor — always divide it out at the end.",
                  h - 28, color=MUTED, size=11)

    else:
        draw_note(canvas,
                  f"Check: can {raw}/{d_raw} be simplified?",
                  38, color=DIM, size=11)

        # Left: current result as-is, green
        left_cx = w / 2 - 140
        cy      = 130
        _draw_fraction(canvas, left_cx, cy, raw, d_raw,
                       num_color=GOOD, den_color=GOOD, size=34)

        draw_pill(canvas, left_cx, cy + 72,
                  f"greatest common divisor = 1 — already lowest",
                  bg="#dcfce7", fg=GOOD, size=11)

        # Right: fixed mini-demo of WHEN you do reduce, so the pupil
        # still sees the technique even on a non-reducing example.
        right_cx = w / 2 + 170
        canvas.create_text(right_cx, 78, text="When it does reduce:",
                           fill=MUTED, font=("Helvetica", 10, "italic"))
        _draw_fraction(canvas, right_cx - 60, cy, 2, 6, size=24)
        canvas.create_text(right_cx, cy, text="→",
                           fill=DIM, font=("Helvetica", 20, "bold"))
        _draw_fraction(canvas, right_cx + 60, cy, 1, 3,
                       num_color=GOOD, den_color=GOOD, size=24)
        canvas.create_text(right_cx, cy + 48, text="÷2  top and bottom",
                           fill=ACCENT, font=("Helvetica", 10, "bold"))

        draw_note(canvas,
                  "If the top and bottom share a factor, divide both by it. "
                  "Otherwise you're done.",
                  h - 28, color=MUTED, size=11)


# ── Slide 8 — Pitfall ────────────────────────────────────────────────────────
#
# Fixed example: 2/3 + 1/4. Contrasts the correct answer (11/12) with
# the two most common wrong answers:
#   1)  3/7  — adds the denominators as well as the numerators.
#   2)  3/12 — gets the common denom right but forgets to rewrite the tops.

def _slide_8(canvas, ex, w, h):
    draw_note(canvas, "Watch out for these two common mistakes.", 36,
              color=DIM, size=11)

    cy = 140
    tk_red = "#dc2626"

    # Three columns: Correct | Wrong (added bottoms) | Wrong (didn't rewrite)
    col_cx = [w / 2 - 230, w / 2, w / 2 + 230]

    # ── Column 1: Correct, 2/3 + 1/4 = 11/12 ────────────────────────────────
    canvas.create_text(col_cx[0], cy - 78, text="Correct",
                       fill=GOOD, font=("Helvetica", 11, "bold"))
    _draw_column_expr(canvas, col_cx[0], cy,
                      2, 3, "+", 1, 4, 11, 12,
                      res_color=GOOD)

    # ── Column 2: Wrong A — added denominators ──────────────────────────────
    canvas.create_text(col_cx[1], cy - 78, text="Wrong",
                       fill=tk_red, font=("Helvetica", 11, "bold"))
    _draw_column_expr(canvas, col_cx[1], cy,
                      2, 3, "+", 1, 4, 3, 7,
                      res_color=tk_red, faded=True)
    canvas.create_text(col_cx[1], cy + 58, text="added the bottoms",
                       fill=tk_red, font=("Helvetica", 9, "italic"))

    # ── Column 3: Wrong B — right bottom, but didn't rewrite tops ──────────
    canvas.create_text(col_cx[2], cy - 78, text="Wrong",
                       fill=tk_red, font=("Helvetica", 11, "bold"))
    _draw_column_expr(canvas, col_cx[2], cy,
                      2, 3, "+", 1, 4, 3, 12,
                      res_color=tk_red, faded=True)
    canvas.create_text(col_cx[2], cy + 58, text="forgot to rewrite the tops",
                       fill=tk_red, font=("Helvetica", 9, "italic"))

    # ≠ glyphs between the columns, same cleanup pattern as frac_basic slide 8
    canvas.create_text((col_cx[0] + col_cx[1]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))
    canvas.create_text((col_cx[1] + col_cx[2]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))

    draw_pill(canvas, w / 2, cy + 92,
              "Always: find the LCM, rewrite BOTH tops, then add the numerators only.",
              bg="#fef3c7", fg=WARN, size=11)

    draw_note(canvas,
              "Bottoms match first — then only the tops combine.",
              h - 26, color=WARN, size=12)


def _draw_column_expr(canvas, cx, cy, a_n, a_d, op, b_n, b_d,
                      res_n, res_d, res_color=INK, faded=False):
    """Render 'a/b op c/d = e/f' centred on cx. 'faded' dims the inputs so
    the eye is drawn to the result column."""
    gap = 30
    body_col = DIM if faded else INK
    f_cx = [cx - gap * 2.1, cx - gap * 0.7,
            cx + gap * 0.7, cx + gap * 2.1]

    _draw_fraction(canvas, f_cx[0], cy, a_n, a_d,
                   num_color=body_col, den_color=body_col, size=22)
    canvas.create_text(f_cx[1] - 4, cy, text=_op_glyph(op),
                       fill=body_col, font=("Helvetica", 22, "bold"))
    _draw_fraction(canvas, f_cx[2], cy, b_n, b_d,
                   num_color=body_col, den_color=body_col, size=22)
    canvas.create_text(f_cx[3] - 4, cy, text="=",
                       fill=DIM, font=("Helvetica", 22, "bold"))
    _draw_fraction(canvas, f_cx[3] + 22, cy, res_n, res_d,
                   num_color=res_color, den_color=res_color, size=24)


# ── Slide list (what the framework consumes) ─────────────────────────────────

SLIDES = [
    {
        "title":   "1 · Read the question",
        "caption": ("Two fractions with DIFFERENT bottoms. The pieces "
                    "are not the same size yet — we have to fix that "
                    "before we can combine them."),
        "draw":    _slide_1,
    },
    {
        "title":   "2 · The pieces don't match",
        "caption": ("Same-length bars cut into different numbers of "
                    "pieces. One third is a bigger piece than one "
                    "quarter — you can't count them together."),
        "draw":    _slide_2,
    },
    {
        "title":   "3 · Find the common denominator (LCM)",
        "caption": ("Walk the multiples of each bottom number until "
                    "you hit the same number on both lists. That number "
                    "is the new piece size."),
        "draw":    _slide_3,
    },
    {
        "title":   "4 · Rewrite the left fraction",
        "caption": ("Multiply the top AND the bottom by the same number "
                    "so the new bottom matches the Lowest Common Denominator. The value of the "
                    "fraction doesn't change — you've only cut each "
                    "piece into smaller equal slices."),
        "draw":    _slide_4,
    },
    {
        "title":   "5 · Rewrite the right fraction",
        "caption": ("Same trick on the right. After this step both "
                    "fractions share the same bottom — the same piece "
                    "size — and we can combine them."),
        "draw":    _slide_5,
    },
    {
        "title":   "6 · Now it's just like Beginner",
        "caption": ("Same denominator on both sides. Add (or subtract) "
                    "the numerators only. The bottom stays put — the "
                    "piece size didn't change."),
        "draw":    _slide_6,
    },
    {
        "title":   "7 · Reduce if you can",
        "caption": ("If the top and the bottom share a common factor, "
                    "divide both by it to get the simplest form. "
                    "Otherwise the answer is already done."),
        "draw":    _slide_7,
    },
    {
        "title":   "8 · Watch the pitfalls",
        "caption": ("Two classic mistakes: adding the bottoms, and "
                    "using the right common denominator but forgetting "
                    "to rewrite the tops. Either one gives a wrong answer."),
        "draw":    _slide_8,
    },
]
