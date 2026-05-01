"""
tutorial_frac_advanced.py
-------------------------
Tutorial content for Fractions: Advanced — adding and subtracting
fractions where the denominators are UNRELATED (neither divides the
other), e.g. 3/13 + 9/19 or 5/8 + 1/12.

Pedagogical distinction from Intermediate
-----------------------------------------
Intermediate's hook is "one bottom is a clean multiple of the other —
scale the smaller-denom side up." Advanced's hook is the opposite:
NEITHER bottom is a multiple of the other, so BOTH fractions must
scale to a shared common denominator. The novel beat is therefore
choosing which common denominator to use.

Method (confirmed with Aleks)
-----------------------------
1. **Default strategy: multiply the denominators.** Always works,
   never fails — for coprime denoms (3/13 + 9/19) this *is* the LCM.
2. **Better when you can spot it: a smaller LCM via shared factor.**
   When the denoms share a factor (8 and 12 share a 4 → LCM 24, not
   product 96; 9 and 12 share a 3 → 36, not 108), use the smaller
   number to keep the arithmetic small. Develops "be aware of
   multiples of two, three, five" as the pupil's eye.
3. **Always simplify the result.** Even though the game's parser
   accepts any equivalent form, the pupil should learn to reduce —
   that's proper.

Layout
------
Same two-fraction-side-by-side style as `tutorial_frac_intermediate`
with ×m callouts on EACH side (vs intermediate where often only one
side scaled). Helpers `_lcm`, `_rewrite`, `_result_raw`,
`_result_reduced`, `_op_word`, `_op_glyph`, `_draw_fraction` are
imported directly from `tutorial_frac_intermediate` so the visual
vocabulary stays identical across the two packs.

Pedagogy (in order)
-------------------
1. Read the question — pill flags "neither bottom divides the other".
2. Find the common denominator — TWO strategies: default (multiply)
   and better-when-possible (spot a smaller LCM). The novel beat.
3. Rewrite the LEFT fraction with ×m to land on the LCM.
4. Rewrite the RIGHT fraction with ×n. Same trick, both sides.
5. Same denominator now — add/subtract numerators, denom stays.
6. Simplify the result — divide top and bottom by their gcd. Fixed
   mini-demo when the cycled example is already in lowest terms.
7. Pitfalls — fixed reference 3/13 + 9/19 with two canonical wrong
   answers (added num+denom; used the bigger denom without scaling).

Examples (5)
------------
Four shared-factor / coprime cases drilling the new beat, plus one
gentle coprime warmup. Every dividend / denom pair sits within
`frac_advanced.py::DENOMS = [5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
17, 18, 19, 20]` so each example matches a question the game can
actually generate.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

from .slideshow_frame import (
    INK, MUTED, DIM, FAINT, SOFT, ACCENT, GOOD, WARN,
    draw_note, draw_arrow, draw_pill, build_slides,
)
from .tutorial_frac_intermediate import (
    _lcm, _rewrite, _result_raw, _result_reduced,
    _op_word, _op_glyph, _draw_fraction,
)


TITLE = "Fractions: Advanced — unrelated denominators"
LEAD  = "Neither bottom divides the other. Scale BOTH to a common denominator."


# ── Examples ─────────────────────────────────────────────────────────────────
#
# Five curated problems. All sit inside the game's DENOMS pool.
#
# 1.  1/5 + 1/7   — coprime warmup. LCM = 35 = product. Default-multiply
#                   teaches itself; clean small numerators keep the focus
#                   on the method.
# 2.  3/8 + 1/12  — shared factor 4. LCM = 24, product = 96. Showcases
#                   the "spot a smaller common denom" strategy.
# 3.  3/14 + 1/10 — shared factor 2. LCM = 70, raw = 22/70 → REDUCES to
#                   11/35 (gcd 2). Slide 6 fires its real branch here.
# 4.  4/9 − 1/12  — subtraction, shared factor 3. LCM = 36. No reduce.
# 5.  3/13 + 9/19 — coprime, big numbers (the roadmap reference and the
#                   slide-7 pitfall reference). LCM = 247 = product.

EXAMPLES = [
    {"a_num": 1, "a_den":  5, "b_num": 1, "b_den":  7, "op": "+"},
    {"a_num": 3, "a_den":  8, "b_num": 1, "b_den": 12, "op": "+"},
    {"a_num": 3, "a_den": 14, "b_num": 1, "b_den": 10, "op": "+"},
    {"a_num": 4, "a_den":  9, "b_num": 1, "b_den": 12, "op": "-"},
    {"a_num": 3, "a_den": 13, "b_num": 9, "b_den": 19, "op": "+"},
]


# ── Slide 1 — Read the question ─────────────────────────────────────────────

def _slide_1(canvas, ex, w, h):
    a_num, a_den = ex["a_num"], ex["a_den"]
    b_num, b_den = ex["b_num"], ex["b_den"]
    op           = ex["op"]
    product      = a_den * b_den
    lcm          = _lcm(a_den, b_den)

    draw_note(canvas, "The question:", 38, color=DIM, size=11)

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

    # Pill plainly names the new constraint vs Intermediate.
    pill_text = (f"neither {a_den} nor {b_den} divides the other — "
                 f"BOTH fractions will scale")
    draw_pill(canvas, w / 2, cy + 82, pill_text,
              bg="#fef3c7", fg=WARN, size=12)

    bottom_text = (
        f"Default strategy: multiply the bottoms ({a_den} × {b_den} "
        f"= {product})." if lcm == product else
        f"Default strategy: multiply the bottoms ({a_den} × {b_den} "
        f"= {product}) — but the bottoms share a factor, so {lcm} "
        "works too and keeps the numbers smaller."
    )
    draw_note(canvas, bottom_text, h - 28, color=MUTED, size=11)


# ── Slide 2 — Find the common denominator: TWO strategies ────────────────────
#
# This is the novel beat. Top half presents the default multiply
# strategy on the cycled example; bottom half presents the
# spot-shared-factor strategy on a fixed reference (8 and 12) so the
# pupil sees the LCM advantage even when the cycled example is coprime.

_LCM_REF = (8, 12)   # (denom_a, denom_b) — fixed reference for strategy 2


def _slide_2(canvas, ex, w, h):
    a_den   = ex["a_den"]
    b_den   = ex["b_den"]
    product = a_den * b_den
    lcm     = _lcm(a_den, b_den)

    draw_note(canvas, "Two strategies for finding a common denominator:",
              28, color=DIM, size=11)

    # ── Top half: Strategy 1 — multiply the denominators ────────────────────
    canvas.create_text(50, 64, text="1.", anchor="w",
                       fill=ACCENT, font=("Helvetica", 16, "bold"))
    canvas.create_text(76, 64, text="Default: multiply the bottoms",
                       fill=INK, font=("Helvetica", 13, "bold"), anchor="w")
    canvas.create_text(76, 84,
                       text=f"{a_den}  ×  {b_den}  =  {product}",
                       fill=ACCENT, font=("Helvetica", 16, "bold"), anchor="w")
    canvas.create_text(76, 106,
                       text="always works — never fails",
                       fill=MUTED, font=("Helvetica", 11, "italic"), anchor="w")

    # ── Bottom half: Strategy 2 — spot the smaller LCM ──────────────────────
    ref_a, ref_b = _LCM_REF
    ref_lcm      = _lcm(ref_a, ref_b)
    ref_product  = ref_a * ref_b

    canvas.create_text(50, 152, text="2.", anchor="w",
                       fill=ACCENT, font=("Helvetica", 16, "bold"))
    canvas.create_text(76, 152, text="Better when you spot it: a smaller LCM",
                       fill=INK, font=("Helvetica", 13, "bold"), anchor="w")
    canvas.create_text(76, 172,
                       text=(f"e.g. {ref_a} and {ref_b} share a factor — "
                             f"both go into {ref_lcm}, not just {ref_product}"),
                       fill=MUTED, font=("Helvetica", 11), anchor="w")

    # Visual: list multiples of ref_a and ref_b until both hit ref_lcm.
    label_x  = 90
    cx_start = 200
    spacing  = 60
    row1 = [ref_a * i for i in range(1, ref_lcm // ref_a + 1)]
    row2 = [ref_b * i for i in range(1, ref_lcm // ref_b + 1)]

    def _draw_chip_row(y, label, vals, tint):
        canvas.create_text(label_x, y, anchor="w", text=label,
                           fill=MUTED, font=("Helvetica", 11, "bold"))
        for i, v in enumerate(vals):
            cx = cx_start + i * spacing
            is_lcm = (v == ref_lcm)
            fill = "#dcfce7" if is_lcm else tint
            ring = GOOD     if is_lcm else DIM
            canvas.create_oval(cx - 18, y - 14, cx + 18, y + 14,
                               fill=fill, outline=ring,
                               width=2 if is_lcm else 1)
            fg = GOOD if is_lcm else INK
            canvas.create_text(cx, y, text=str(v), fill=fg,
                               font=("Helvetica", 11, "bold"))

    _draw_chip_row(204, f"×{ref_a}:", row1, "#e0e7ff")
    _draw_chip_row(238, f"×{ref_b}:", row2, "#fee2e2")

    # Pill picking the strategy used for THIS cycled example.
    if lcm == product:
        pill_text = (f"this example uses strategy 1 — "
                     f"{a_den} and {b_den} share no factor → LCM = "
                     f"{a_den} × {b_den} = {lcm}")
        pill_bg, pill_fg = "#eef2ff", ACCENT
    else:
        pill_text = (f"this example uses strategy 2 — "
                     f"{a_den} and {b_den} share a factor → LCM = "
                     f"{lcm} (smaller than {product})")
        pill_bg, pill_fg = "#dcfce7", GOOD
    draw_pill(canvas, w / 2, h - 36, pill_text,
              bg=pill_bg, fg=pill_fg, size=11)


# ── Slide 3 — Rewrite the LEFT fraction (×m) ────────────────────────────────

def _slide_3(canvas, ex, w, h):
    a_num, a_den = ex["a_num"], ex["a_den"]
    d, a_new, a_mult, _, _ = _rewrite(ex)

    draw_note(canvas,
              f"Rewrite the LEFT fraction with {d} on the bottom.",
              38, color=DIM, size=11)

    cy   = 135
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

    # ×m callouts above and below — labels at cy±66, arrows stop at cy±44
    # (10 px clear of size=30 glyph edges at cy±34). v0.7.3 fix.
    canvas.create_text(f_cx[0], cy - 66, text=f"×{a_mult}",
                       fill=ACCENT, font=("Helvetica", 11, "bold"))
    canvas.create_text(f_cx[0], cy + 66, text=f"×{a_mult}",
                       fill=ACCENT, font=("Helvetica", 11, "bold"))
    draw_arrow(canvas, f_cx[0], cy - 56, f_cx[0], cy - 44,
               color=ACCENT, width=2)
    draw_arrow(canvas, f_cx[0], cy + 56, f_cx[0], cy + 44,
               color=ACCENT, width=2)

    draw_pill(canvas, w / 2, cy + 95,
              f"{a_num}/{a_den}  =  {a_new}/{d}   (same value, smaller pieces)",
              bg="#dcfce7", fg=GOOD, size=12)


# ── Slide 4 — Rewrite the RIGHT fraction (×n) ───────────────────────────────

def _slide_4(canvas, ex, w, h):
    b_num, b_den = ex["b_num"], ex["b_den"]
    d, _, _, b_new, b_mult = _rewrite(ex)

    draw_note(canvas,
              f"Now the RIGHT fraction — same trick, same {d}.",
              38, color=DIM, size=11)

    cy   = 135
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

    canvas.create_text(f_cx[0], cy - 66, text=f"×{b_mult}",
                       fill=ACCENT, font=("Helvetica", 11, "bold"))
    canvas.create_text(f_cx[0], cy + 66, text=f"×{b_mult}",
                       fill=ACCENT, font=("Helvetica", 11, "bold"))
    draw_arrow(canvas, f_cx[0], cy - 56, f_cx[0], cy - 44,
               color=ACCENT, width=2)
    draw_arrow(canvas, f_cx[0], cy + 56, f_cx[0], cy + 44,
               color=ACCENT, width=2)

    draw_pill(canvas, w / 2, cy + 95,
              f"{b_num}/{b_den}  =  {b_new}/{d}   "
              f"— both bottoms are now {d}",
              bg="#dcfce7", fg=GOOD, size=12)


# ── Slide 5 — Same denominator, combine numerators ──────────────────────────

def _slide_5(canvas, ex, w, h):
    op = ex["op"]
    d, a_new, _, b_new, _ = _rewrite(ex)
    raw, _ = _result_raw(ex)

    draw_note(canvas,
              f"Both bottoms are now {d}. {_op_word(op, cap=True)} the "
              f"numerators — the bottom stays.",
              38, color=DIM, size=11)

    cy  = 110
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

    # Numerator-only working line below, with arrows from the top numerators.
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

    draw_arrow(canvas, f_cx[0], cy - 24, x_a, sum_y - 14,
               color=ACCENT, width=2)
    draw_arrow(canvas, f_cx[2], cy - 24, x_b, sum_y - 14,
               color=ACCENT, width=2)

    draw_pill(canvas, w / 2, sum_y + 42,
              f"denominator stays {d} — never add bottoms",
              bg="#dcfce7", fg=GOOD, size=11)


# ── Slide 6 — Simplify the result ───────────────────────────────────────────

def _slide_6(canvas, ex, w, h):
    raw, d_raw       = _result_raw(ex)
    red_n, red_d, g  = _result_reduced(ex)

    if g > 1:
        draw_note(canvas,
                  f"Always simplify. Can {raw}/{d_raw} reduce?",
                  38, color=DIM, size=11)

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

        canvas.create_text(f_cx[0], cy - 70, text=f"÷{g}",
                           fill=ACCENT, font=("Helvetica", 11, "bold"))
        canvas.create_text(f_cx[0], cy + 70, text=f"÷{g}",
                           fill=ACCENT, font=("Helvetica", 11, "bold"))
        draw_arrow(canvas, f_cx[0], cy - 60, f_cx[0], cy - 46,
                   color=ACCENT, width=2)
        draw_arrow(canvas, f_cx[0], cy + 60, f_cx[0], cy + 46,
                   color=ACCENT, width=2)

        # Double-underline under the reduced answer (size=34 glyph → bottom
        # at cy+38; underline pair at cy+52 / cy+57).
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
                  "Top and bottom share a factor — always divide it out.",
                  h - 28, color=MUTED, size=11)

    else:
        draw_note(canvas,
                  f"Always simplify. Can {raw}/{d_raw} reduce?",
                  38, color=DIM, size=11)

        # Left: current result in green — already lowest terms.
        left_cx = w / 2 - 140
        cy      = 130
        _draw_fraction(canvas, left_cx, cy, raw, d_raw,
                       num_color=GOOD, den_color=GOOD, size=34)

        draw_pill(canvas, left_cx, cy + 72,
                  "greatest common divisor = 1 — already lowest",
                  bg="#dcfce7", fg=GOOD, size=11)

        # Right: fixed mini-demo of WHEN you do reduce, so the technique is
        # always visible regardless of which example is cycled.
        right_cx = w / 2 + 170
        canvas.create_text(right_cx, 78, text="When it does reduce:",
                           fill=MUTED, font=("Helvetica", 10, "italic"))
        _draw_fraction(canvas, right_cx - 60, cy, 6, 8, size=24)
        canvas.create_text(right_cx, cy, text="→",
                           fill=DIM, font=("Helvetica", 20, "bold"))
        _draw_fraction(canvas, right_cx + 60, cy, 3, 4,
                       num_color=GOOD, den_color=GOOD, size=24)
        canvas.create_text(right_cx, cy + 48, text="÷2  top and bottom",
                           fill=ACCENT, font=("Helvetica", 10, "bold"))

        draw_note(canvas,
                  "If top and bottom share a factor, divide both by it. "
                  "Otherwise you're done.",
                  h - 28, color=MUTED, size=11)


# ── Slide 7 — Pitfalls ──────────────────────────────────────────────────────
#
# Fixed reference: 3/13 + 9/19. Two canonical wrong answers:
#   ✗ 12/32  — added BOTH numerators AND denominators ("3+9 over 13+19")
#   ✗ 12/19  — used the bigger denom without scaling either fraction

def _slide_7(canvas, ex, w, h):
    draw_note(canvas,
              "Two mistakes to watch for — using 3/13 + 9/19 as reference:",
              32, color=DIM, size=11)

    red    = "#dc2626"
    cy     = 140
    col_cx = [w / 2 - 220, w / 2, w / 2 + 220]

    # ── Column 1: Correct (174/247, gcd=1, no reduce) ──────────────────────
    canvas.create_text(col_cx[0], cy - 78, text="Correct",
                       fill=GOOD, font=("Helvetica", 11, "bold"))
    _draw_fraction(canvas, col_cx[0], cy - 8, 174, 247,
                   num_color=GOOD, den_color=GOOD, size=22)
    canvas.create_text(col_cx[0], cy + 28,
                       text="57/247 + 117/247",
                       fill=MUTED, font=("Helvetica", 10))
    canvas.create_text(col_cx[0], cy + 42,
                       text="= 174/247  (already lowest)",
                       fill=MUTED, font=("Helvetica", 10))

    # ── Column 2: Wrong A — added num and denom ────────────────────────────
    canvas.create_text(col_cx[1], cy - 78, text="Wrong",
                       fill=red, font=("Helvetica", 11, "bold"))
    _draw_fraction(canvas, col_cx[1], cy - 8, 12, 32,
                   num_color=red, den_color=red, size=22)
    canvas.create_text(col_cx[1], cy + 28,
                       text="(3+9)/(13+19) —",
                       fill=red, font=("Helvetica", 10, "italic"))
    canvas.create_text(col_cx[1], cy + 42,
                       text="never add the bottoms",
                       fill=red, font=("Helvetica", 10, "italic"))

    # ── Column 3: Wrong B — used bigger denom without scaling ──────────────
    canvas.create_text(col_cx[2], cy - 78, text="Wrong",
                       fill=red, font=("Helvetica", 11, "bold"))
    _draw_fraction(canvas, col_cx[2], cy - 8, 12, 19,
                   num_color=red, den_color=red, size=22)
    canvas.create_text(col_cx[2], cy + 28,
                       text="picked 19, kept tops as-is —",
                       fill=red, font=("Helvetica", 10, "italic"))
    canvas.create_text(col_cx[2], cy + 42,
                       text="must scale BOTH first",
                       fill=red, font=("Helvetica", 10, "italic"))

    canvas.create_text((col_cx[0] + col_cx[1]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))
    canvas.create_text((col_cx[1] + col_cx[2]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))

    draw_pill(canvas, w / 2, cy + 90,
              "always: scale BOTH fractions to a common denom, "
              "add only the tops, simplify at the end",
              bg="#fef3c7", fg=WARN, size=11)


# ── Slide list ──────────────────────────────────────────────────────────────

SLIDES = build_slides(
    [_slide_1, _slide_2, _slide_3, _slide_4, _slide_5, _slide_6, _slide_7],
    [
        "1 · Read the question",
        "2 · Find the common denominator — two strategies",
        "3 · Rewrite the LEFT fraction",
        "4 · Rewrite the RIGHT fraction",
        "5 · Same denominator — combine the numerators",
        "6 · Simplify the result",
        "7 · Watch the pitfalls",
    ],
    captions=[
        ("Neither bottom divides the other — both fractions need to scale "
         "to a common denominator. The default safe move is to multiply the "
         "bottoms; sometimes you can spot a smaller common one."),
        ("Two strategies. (1) Multiply the bottoms — always works, never "
         "fails. (2) When the bottoms share a factor, list multiples of "
         "each and pick the smallest match — that's the LCM, smaller than "
         "the product, easier arithmetic from here on."),
        ("Multiply the LEFT fraction's top AND bottom by the same number "
         "to land on the chosen common denominator. The fraction's value "
         "doesn't change — each old piece is just cut into smaller equal "
         "pieces."),
        ("Same trick on the RIGHT fraction. Different multiplier, same "
         "destination: both bottoms now match. The problem has collapsed "
         "to the Beginner case."),
        ("Both bottoms agree — add (or subtract) the numerators, the "
         "bottom stays. Never add the bottoms; that gives a different "
         "fraction with the wrong piece size."),
        ("Always check whether top and bottom share a factor. If they do, "
         "divide both by it (the greatest common divisor). The reduced "
         "fraction is the proper final form."),
        ("Two common mistakes: adding both numerators AND denominators "
         "(gives a fraction with the wrong piece size), and using the "
         "bigger denom without scaling either fraction (skips the whole "
         "rewrite). Always scale BOTH first."),
    ],
)
