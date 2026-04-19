"""
tutorial_conv_basic.py
----------------------
Tutorial content for Conversions: Beginner — converting between fractions
and decimals for "clean" denominators (2, 4, 5, 8, 10).

Framing
-------
A decimal IS a fraction in disguise. The digits after the point name a
power-of-ten denominator — 1 digit = tenths (÷10), 2 digits = hundredths
(÷100), 3 digits = thousandths (÷1000). Converting a fraction to a
decimal is just rewriting it with 10, 100, or 1000 on the bottom. For
the five "clean" denominators this is always possible: 2, 4, 5, 8, 10
all divide some power of ten evenly.

Pedagogy (fraction → decimal direction)
---------------------------------------
1. Look at the bottom of the fraction.
2. Find the multiplier m such that denom × m is 10, 100, or 1000.
3. Multiply the TOP by the same m. Read the result off as a decimal.
   - 3/4: 4 × 25 = 100, so 3/4 = 75/100 = 0.75.
   - 1/2: 2 × 5  = 10,  so 1/2 = 5/10  = 0.5.
   - 3/8: 8 × 125 = 1000, so 3/8 = 375/1000 = 0.375.

Pedagogy (decimal → fraction direction)
---------------------------------------
1. Count the digits after the decimal point — that names the denominator
   (1 → 10, 2 → 100, 3 → 1000).
2. Put those digits on top.
3. Simplify (divide top and bottom by the greatest common divisor) to
   reach the clean pool form.
   - 0.4 → 4/10 → ÷2 → 2/5.
   - 0.75 → 75/100 → ÷25 → 3/4.

Examples cycle 5 curated pairs drawn from conv_basic._PAIRS. Four are
canonical fraction→decimal; one (0.4 → 2/5) is canonical decimal→fraction
so the pupil meets the reverse direction inside the carousel.

Raw ints throughout — fractions.Fraction auto-reduces on construction,
which would silently collapse "75/100" into "3/4" and destroy the whole
teaching point of showing the intermediate power-of-ten form.

Slide plan
----------
1. Read the question    — show the current example's prompt cleanly.
2. Place-value anchor   — tenths bar + hundredths grid; "decimals ARE fractions".
3. Find the bridge      — per-direction: den × m = 10/100/1000, or count digits.
4. Apply the rewrite    — ×m on both top & bottom, or "put digits on top".
5. Read or simplify     — frac→dec: read off the decimal.
                          dec→frac: divide by the greatest common divisor.
6. The arrow both ways  — fixed 3/4 ↔ 0.75 round-trip demo.
7. Full chain           — compact end-to-end render of the current example.
8. Pitfall              — 3/8 ≠ 0.38 (can't copy digits),
                          1/4 ≠ 0.4  (4 is the piece count, not a decimal place).
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

from .slideshow_frame import (
    INK, MUTED, DIM, ACCENT, GOOD, WARN, CARD_BG,
    draw_note, draw_arrow, draw_pill,
)


TITLE = "Conversions: Beginner — fraction ↔ decimal"
LEAD  = "A decimal is a fraction with 10, 100, or 1000 on the bottom. That's the whole trick."


# ── Examples ─────────────────────────────────────────────────────────────────
#
# Each example has one canonical direction ("frac_to_dec" or "dec_to_frac")
# and pre-computed fields so every slide can draw the chain without having
# to recompute. Raw ints only — never Fraction.
#
# Fields:
#   direction    : "frac_to_dec" or "dec_to_frac"
#   frac_num     : clean-form numerator  (matches conv_basic._PAIRS)
#   frac_den     : clean-form denominator (∈ {2, 4, 5, 8, 10})
#   dec_str      : decimal string ("0.75", "0.5", "0.375", "0.4", "0.3")
#   mult         : multiplier m such that frac_den × m ∈ {10, 100, 1000}
#                  (also = frac_den × m / frac_den, i.e. the raw→clean factor
#                   on the dec→frac path; equal to gcd_reverse for the pairs
#                   used here because target_num / frac_num = m in every case)
#   target_den   : 10, 100, or 1000 — the power-of-ten denominator
#   target_num   : frac_num × mult    — the numerator at the power-of-ten step
#   digit_n      : number of digits after the decimal point (1 / 2 / 3)
#   gcd_reverse  : gcd(target_num, target_den). On the dec→frac path this is
#                  the factor the pupil divides by to reach the clean form.
EXAMPLES = [
    # 3/4 ↔ 0.75   (frac→dec, ×25, hundredths — headline)
    dict(direction="frac_to_dec", frac_num=3, frac_den=4,  dec_str="0.75",
         mult=25,  target_den=100,  target_num=75,  digit_n=2, gcd_reverse=25),
    # 1/2 ↔ 0.5    (frac→dec, ×5, tenths — easy confidence win)
    dict(direction="frac_to_dec", frac_num=1, frac_den=2,  dec_str="0.5",
         mult=5,   target_den=10,   target_num=5,   digit_n=1, gcd_reverse=5),
    # 3/8 ↔ 0.375  (frac→dec, ×125, thousandths — stretches the method)
    dict(direction="frac_to_dec", frac_num=3, frac_den=8,  dec_str="0.375",
         mult=125, target_den=1000, target_num=375, digit_n=3, gcd_reverse=125),
    # 0.4 ↔ 2/5    (dec→frac, tenths, ÷2 simplify — reverse-direction anchor)
    dict(direction="dec_to_frac", frac_num=2, frac_den=5,  dec_str="0.4",
         mult=2,   target_den=10,   target_num=4,   digit_n=1, gcd_reverse=2),
    # 3/10 ↔ 0.3   (frac→dec, already tenths, mult=1 — "no bridge needed")
    dict(direction="frac_to_dec", frac_num=3, frac_den=10, dec_str="0.3",
         mult=1,   target_den=10,   target_num=3,   digit_n=1, gcd_reverse=1),
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _draw_fraction(canvas, cx, cy, num_text, den_text,
                   num_color=INK, den_color=INK, size=30):
    """Draw a stacked fraction centred around (cx, cy). Returns (top_y, bot_y)."""
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


def _power_word(target_den: int) -> str:
    """Spelled-out name of a power-of-ten denominator."""
    return {10: "tenths", 100: "hundredths", 1000: "thousandths"}.get(
        target_den, f"1/{target_den}ths")


def _digit_word(n: int) -> str:
    return {1: "one", 2: "two", 3: "three"}.get(n, str(n))


def _digit_noun(n: int) -> str:
    return "digit" if n == 1 else "digits"


# ── Slide 1 — Read the question ──────────────────────────────────────────────

def _slide_1(canvas, ex, w, h):
    direction = ex["direction"]

    if direction == "frac_to_dec":
        draw_note(canvas,
                  "The question:  convert this fraction to a decimal.",
                  38, color=DIM, size=11)
    else:
        draw_note(canvas,
                  "The question:  convert this decimal to a fraction.",
                  38, color=DIM, size=11)

    cy = 135

    if direction == "frac_to_dec":
        _draw_fraction(canvas, w / 2 - 80, cy,
                       ex["frac_num"], ex["frac_den"], size=36)
        canvas.create_text(w / 2 + 10, cy, text="=",
                           fill=DIM, font=("Helvetica", 32, "bold"))
        canvas.create_text(w / 2 + 80, cy, text="?",
                           fill=ACCENT, font=("Helvetica", 34, "bold"))
    else:
        canvas.create_text(w / 2 - 80, cy, text=ex["dec_str"],
                           fill=INK, font=("Helvetica", 36, "bold"))
        canvas.create_text(w / 2 + 10, cy, text="=",
                           fill=DIM, font=("Helvetica", 32, "bold"))
        canvas.create_text(w / 2 + 80, cy, text="?",
                           fill=ACCENT, font=("Helvetica", 34, "bold"))

    # Anchor pill carrying the whole-pack framing.
    draw_pill(canvas, w / 2, cy + 82,
              "a decimal is a fraction with 10, 100, or 1000 on the bottom",
              bg="#fef3c7", fg=WARN, size=12)

    draw_note(canvas,
              "Fractions and decimals are two ways of writing the same "
              "number. We just need to match the form the question asks for.",
              h - 28, color=MUTED, size=11)


# ── Slide 2 — Place-value anchor ─────────────────────────────────────────────

def _slide_2(canvas, ex, w, h):
    draw_note(canvas,
              "Decimals just name the piece size with 10 or 100 or 1000.",
              36, color=DIM, size=11)

    # ── Tenths bar — 10 segments, 1 shaded for 0.1 ─────────────────────────
    bar_x1 = 80
    bar_x2 = 400
    bar_y_top = 80
    bar_y_bot = 118
    seg = (bar_x2 - bar_x1) / 10
    for i in range(10):
        fill = "#e0e7ff" if i < 1 else CARD_BG
        canvas.create_rectangle(bar_x1 + i * seg, bar_y_top,
                                bar_x1 + (i + 1) * seg, bar_y_bot,
                                outline=INK, width=1, fill=fill)
    canvas.create_rectangle(bar_x1, bar_y_top, bar_x2, bar_y_bot,
                            outline=INK, width=2, fill="")
    canvas.create_text((bar_x1 + bar_x2) / 2, bar_y_top - 14,
                       text="tenths bar — 10 equal pieces",
                       fill=MUTED, font=("Helvetica", 10, "bold"))
    canvas.create_text((bar_x1 + bar_x2) / 2, bar_y_bot + 16,
                       text="1 piece shaded  →  1/10  =  0.1",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))

    # ── Hundredths grid — 10×10 small squares, 7 shaded for 0.07 ───────────
    grid_size = 150
    grid_x = w - 90 - grid_size
    grid_y = 80
    cell = grid_size / 10
    shaded_n = 7
    idx = 0
    for r in range(10):
        for c in range(10):
            fill = "#dcfce7" if idx < shaded_n else CARD_BG
            canvas.create_rectangle(grid_x + c * cell, grid_y + r * cell,
                                    grid_x + (c + 1) * cell,
                                    grid_y + (r + 1) * cell,
                                    outline=INK, width=1, fill=fill)
            idx += 1
    canvas.create_text(grid_x + grid_size / 2, grid_y - 14,
                       text="hundredths grid — 100 equal squares",
                       fill=MUTED, font=("Helvetica", 10, "bold"))
    canvas.create_text(grid_x + grid_size / 2, grid_y + grid_size + 16,
                       text="7 shaded  →  7/100  =  0.07",
                       fill=GOOD, font=("Helvetica", 10, "bold"))

    draw_pill(canvas, w / 2, 270,
              "1 digit = tenths   ·   "
              "2 digits = hundredths   ·   "
              "3 digits = thousandths",
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              "Count the digits after the point — that names the bottom of the fraction.",
              h - 28, color=MUTED, size=11)


# ── Slide 3 — Find the bridge ────────────────────────────────────────────────

def _slide_3(canvas, ex, w, h):
    if ex["direction"] == "frac_to_dec":
        _slide_3_frac_to_dec(canvas, ex, w, h)
    else:
        _slide_3_dec_to_frac(canvas, ex, w, h)


def _slide_3_frac_to_dec(canvas, ex, w, h):
    frac_den   = ex["frac_den"]
    mult       = ex["mult"]
    target_den = ex["target_den"]

    if mult == 1:
        draw_note(canvas,
                  f"The bottom is already {target_den} — no bridge needed.",
                  36, color=DIM, size=11)
        cy = 135
        canvas.create_text(w / 2, cy,
                           text=f"{frac_den} is already {_power_word(target_den)}",
                           fill=GOOD, font=("Helvetica", 22, "bold"))
        draw_pill(canvas, w / 2, cy + 60,
                  "multiplier = 1  —  skip straight to reading it off",
                  bg="#dcfce7", fg=GOOD, size=12)
        draw_note(canvas,
                  "When the bottom is already 10, 100, or 1000, the decimal "
                  "is right there.",
                  h - 28, color=MUTED, size=11)
        return

    draw_note(canvas,
              f"What do we multiply {frac_den} by to land on 10, 100, or 1000?",
              36, color=DIM, size=11)

    cy = 140
    x_den    = w / 2 - 180
    x_times  = w / 2 - 80
    x_mult   = w / 2
    x_eq     = w / 2 + 80
    x_target = w / 2 + 190

    canvas.create_text(x_den, cy, text=str(frac_den),
                       fill=INK, font=("Helvetica", 34, "bold"))
    canvas.create_text(x_times, cy, text="×",
                       fill=INK, font=("Helvetica", 28, "bold"))
    canvas.create_text(x_mult, cy, text=str(mult),
                       fill=ACCENT, font=("Helvetica", 34, "bold"))
    canvas.create_text(x_eq, cy, text="=",
                       fill=DIM, font=("Helvetica", 28, "bold"))
    canvas.create_text(x_target, cy, text=str(target_den),
                       fill=GOOD, font=("Helvetica", 34, "bold"))

    # Dashed accent arc from frac_den up and over to target_den. Kept flat
    # (simple dashed line) so the arrowhead geometry is predictable and
    # can't intrude on the numerals below.
    canvas.create_text(x_mult, cy - 48, text=f"×{mult}",
                       fill=ACCENT, font=("Helvetica", 12, "bold"))
    draw_arrow(canvas, x_den + 22, cy - 28, x_target - 22, cy - 28,
               color=ACCENT, width=2, dash=(4, 3))

    draw_pill(canvas, w / 2, cy + 82,
              f"{frac_den} × {mult} = {target_den}  "
              f"({_power_word(target_den)} — "
              f"{ex['digit_n']} {_digit_noun(ex['digit_n'])} after the point)",
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              "That's the bridge into decimal land — any of 2, 4, 5, 8, 10 reaches a power of ten.",
              h - 28, color=MUTED, size=11)


def _slide_3_dec_to_frac(canvas, ex, w, h):
    dec_str    = ex["dec_str"]
    digit_n    = ex["digit_n"]
    target_den = ex["target_den"]

    draw_note(canvas,
              "Count the digits after the decimal point — that's your bottom.",
              36, color=DIM, size=11)

    cy = 135

    # Big decimal on the left.
    lx = w / 2 - 140
    canvas.create_text(lx, cy, text=dec_str,
                       fill=INK, font=("Helvetica", 40, "bold"))
    canvas.create_text(lx, cy + 48,
                       text=f"{_digit_word(digit_n)} {_digit_noun(digit_n)} after the point",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))

    # Arrow → denominator.
    canvas.create_text(w / 2, cy, text="→",
                       fill=DIM, font=("Helvetica", 28, "bold"))

    # Target denominator on the right with its power-of-ten name.
    rx = w / 2 + 140
    canvas.create_text(rx, cy, text=str(target_den),
                       fill=GOOD, font=("Helvetica", 40, "bold"))
    canvas.create_text(rx, cy - 44,
                       text=_power_word(target_den),
                       fill=GOOD, font=("Helvetica", 10, "bold"))
    canvas.create_text(rx, cy + 48,
                       text="= denominator",
                       fill=GOOD, font=("Helvetica", 10, "bold"))

    draw_pill(canvas, w / 2, cy + 98,
              f"{digit_n} {_digit_noun(digit_n)} after the point  "
              f"→  {_power_word(target_den)}  "
              f"→  denominator = {target_den}",
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              "1 digit means tenths, 2 digits hundredths, 3 digits thousandths.",
              h - 28, color=MUTED, size=11)


# ── Slide 4 — Apply the rewrite ──────────────────────────────────────────────

def _slide_4(canvas, ex, w, h):
    if ex["direction"] == "frac_to_dec":
        _slide_4_frac_to_dec(canvas, ex, w, h)
    else:
        _slide_4_dec_to_frac(canvas, ex, w, h)


def _slide_4_frac_to_dec(canvas, ex, w, h):
    frac_num   = ex["frac_num"]
    frac_den   = ex["frac_den"]
    mult       = ex["mult"]
    target_den = ex["target_den"]
    target_num = ex["target_num"]

    if mult == 1:
        draw_note(canvas,
                  f"The fraction is already on {target_den} — no rewrite needed.",
                  38, color=DIM, size=11)
        cy = 135
        _draw_fraction(canvas, w / 2, cy, frac_num, frac_den,
                       num_color=GOOD, den_color=GOOD, size=36)
        draw_pill(canvas, w / 2, cy + 90,
                  f"{frac_num}/{target_den} is already in {_power_word(target_den)} form",
                  bg="#dcfce7", fg=GOOD, size=12)
        draw_note(canvas,
                  "Move straight on to reading the decimal.",
                  h - 28, color=MUTED, size=11)
        return

    draw_note(canvas,
              f"Multiply the TOP by the same {mult}.  The value doesn't change.",
              38, color=DIM, size=11)

    cy = 135
    f_cx = [w / 2 - 220, w / 2 - 80, w / 2 + 40, w / 2 + 180]

    _draw_fraction(canvas, f_cx[0], cy, frac_num, frac_den, size=30)
    canvas.create_text(f_cx[1] - 14, cy, text="×",
                       fill=INK, font=("Helvetica", 28, "bold"))
    _draw_fraction(canvas, f_cx[1] + 30, cy, mult, mult,
                   num_color=ACCENT, den_color=ACCENT, size=30)
    canvas.create_text(f_cx[2] + 30, cy, text="=",
                       fill=DIM, font=("Helvetica", 28, "bold"))
    _draw_fraction(canvas, f_cx[3], cy, target_num, target_den,
                   num_color=GOOD, den_color=GOOD, size=30)

    # ×mult call-outs over/under the LEFT fraction.
    # size=30 glyphs span roughly cy±34; labels at cy±66, arrow tips at
    # cy±44 → 10 px clear of each glyph edge. (v0.7.3 post-pupil-test rule.)
    canvas.create_text(f_cx[0], cy - 66, text=f"×{mult}",
                       fill=ACCENT, font=("Helvetica", 11, "bold"))
    canvas.create_text(f_cx[0], cy + 66, text=f"×{mult}",
                       fill=ACCENT, font=("Helvetica", 11, "bold"))
    draw_arrow(canvas, f_cx[0], cy - 56, f_cx[0], cy - 44,
               color=ACCENT, width=2)
    draw_arrow(canvas, f_cx[0], cy + 56, f_cx[0], cy + 44,
               color=ACCENT, width=2)

    draw_pill(canvas, w / 2, cy + 95,
              f"{frac_num}/{frac_den}  =  {target_num}/{target_den}  "
              f"(same value, now in {_power_word(target_den)})",
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              "Multiplying top and bottom by the same number leaves the value unchanged.",
              h - 28, color=MUTED, size=11)


def _slide_4_dec_to_frac(canvas, ex, w, h):
    dec_str    = ex["dec_str"]
    target_num = ex["target_num"]
    target_den = ex["target_den"]

    draw_note(canvas,
              "Put the digits after the point on top. That's the raw fraction.",
              38, color=DIM, size=11)

    cy = 135

    # Left: the decimal.
    lx = w / 2 - 180
    canvas.create_text(lx, cy, text=dec_str,
                       fill=INK, font=("Helvetica", 36, "bold"))

    # Middle: arrow.
    canvas.create_text(w / 2, cy, text="→",
                       fill=DIM, font=("Helvetica", 28, "bold"))

    # Right: raw target_num / target_den.
    rx = w / 2 + 180
    _draw_fraction(canvas, rx, cy, target_num, target_den,
                   num_color=GOOD, den_color=GOOD, size=34)

    # Numerator call-out above the right fraction.
    # size=34 glyph top sits near cy-34; label at cy-72, arrow tip at cy-48
    # → 14 px clear.
    canvas.create_text(rx, cy - 72,
                       text="digits after the point",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))
    draw_arrow(canvas, rx, cy - 60, rx, cy - 48,
               color=ACCENT, width=2)

    # Denominator call-out below.
    canvas.create_text(rx, cy + 72,
                       text=f"{_power_word(target_den)} from the count",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))
    draw_arrow(canvas, rx, cy + 60, rx, cy + 48,
               color=ACCENT, width=2)

    draw_pill(canvas, w / 2, cy + 105,
              f"{dec_str}  =  {target_num}/{target_den}",
              bg="#dcfce7", fg=GOOD, size=12)

    draw_note(canvas,
              "Every decimal can be written this way — it's just a fraction in disguise.",
              h - 28, color=MUTED, size=11)


# ── Slide 5 — Read it off (or simplify) ──────────────────────────────────────

def _slide_5(canvas, ex, w, h):
    if ex["direction"] == "frac_to_dec":
        _slide_5_frac_to_dec(canvas, ex, w, h)
    else:
        _slide_5_dec_to_frac(canvas, ex, w, h)


def _slide_5_frac_to_dec(canvas, ex, w, h):
    target_num = ex["target_num"]
    target_den = ex["target_den"]
    dec_str    = ex["dec_str"]
    digit_n    = ex["digit_n"]

    draw_note(canvas,
              "Read the top as the decimal.  The bottom's zeros set the place value.",
              38, color=DIM, size=11)

    cy = 135

    # Left: target_num / target_den.
    lx = w / 2 - 140
    _draw_fraction(canvas, lx, cy, target_num, target_den, size=34)

    # Middle: equals.
    canvas.create_text(w / 2, cy, text="=",
                       fill=DIM, font=("Helvetica", 28, "bold"))

    # Right: the decimal, big and green.
    rx = w / 2 + 140
    canvas.create_text(rx, cy, text=dec_str,
                       fill=GOOD, font=("Helvetica", 40, "bold"))

    # Double underline under the decimal. 40 pt bold ≈ 12 px per char wide;
    # half-width = len*6 gives a snug underline.
    dec_len = len(dec_str)
    u_half  = dec_len * 12
    u_x1    = rx - u_half
    u_x2    = rx + u_half
    u_y     = cy + 42
    canvas.create_line(u_x1, u_y,     u_x2, u_y,     fill=GOOD, width=2)
    canvas.create_line(u_x1, u_y + 5, u_x2, u_y + 5, fill=GOOD, width=2)

    draw_pill(canvas, w / 2, cy + 100,
              f"{target_num} {_power_word(target_den)}  =  {dec_str}",
              bg="#dcfce7", fg=GOOD, size=12)

    draw_note(canvas,
              f"{digit_n} zero{'s' if digit_n != 1 else ''} on the bottom "
              f"→ {digit_n} {_digit_noun(digit_n)} after the point.",
              h - 28, color=MUTED, size=11)


def _slide_5_dec_to_frac(canvas, ex, w, h):
    target_num = ex["target_num"]
    target_den = ex["target_den"]
    frac_num   = ex["frac_num"]
    frac_den   = ex["frac_den"]
    g          = ex["gcd_reverse"]

    if g > 1:
        draw_note(canvas,
                  f"Simplify {target_num}/{target_den} to lowest terms.",
                  38, color=DIM, size=11)

        cy = 135
        f_cx = [w / 2 - 200, w / 2 - 40, w / 2 + 80, w / 2 + 210]

        _draw_fraction(canvas, f_cx[0], cy, target_num, target_den, size=32)
        canvas.create_text(f_cx[1] - 10, cy, text="÷",
                           fill=INK, font=("Helvetica", 28, "bold"))
        _draw_fraction(canvas, f_cx[1] + 30, cy, g, g,
                       num_color=ACCENT, den_color=ACCENT, size=30)
        canvas.create_text(f_cx[2] + 30, cy, text="=",
                           fill=DIM, font=("Helvetica", 28, "bold"))
        _draw_fraction(canvas, f_cx[3], cy, frac_num, frac_den,
                       num_color=GOOD, den_color=GOOD, size=34)

        # ÷g call-outs on the LEFT fraction (size=32 → cy±36 glyph edges).
        # Labels at cy±70, tips at cy±46 → 10 px clear.
        canvas.create_text(f_cx[0], cy - 70, text=f"÷{g}",
                           fill=ACCENT, font=("Helvetica", 11, "bold"))
        canvas.create_text(f_cx[0], cy + 70, text=f"÷{g}",
                           fill=ACCENT, font=("Helvetica", 11, "bold"))
        draw_arrow(canvas, f_cx[0], cy - 60, f_cx[0], cy - 46,
                   color=ACCENT, width=2)
        draw_arrow(canvas, f_cx[0], cy + 60, f_cx[0], cy + 46,
                   color=ACCENT, width=2)

        # Double underline under reduced answer (size=34 → underline at cy+52).
        u_half = 38
        u_x1   = f_cx[3] - u_half
        u_x2   = f_cx[3] + u_half
        u_y    = cy + 52
        canvas.create_line(u_x1, u_y,     u_x2, u_y,     fill=GOOD, width=2)
        canvas.create_line(u_x1, u_y + 5, u_x2, u_y + 5, fill=GOOD, width=2)

        draw_pill(canvas, w / 2, cy + 105,
                  f"greatest common divisor = {g}  —  divide top and bottom by {g}",
                  bg="#dcfce7", fg=GOOD, size=11)

        draw_note(canvas,
                  "Raw power-of-ten form first; then simplify to clean form.",
                  h - 28, color=MUTED, size=11)
    else:
        # gcd = 1 — already lowest. Doesn't fire for the current 5 examples
        # but is handled so future additions don't break.
        draw_note(canvas,
                  f"{target_num}/{target_den} is already in lowest terms.",
                  38, color=DIM, size=11)
        cy = 135
        _draw_fraction(canvas, w / 2, cy, target_num, target_den,
                       num_color=GOOD, den_color=GOOD, size=36)
        draw_pill(canvas, w / 2, cy + 90,
                  "greatest common divisor = 1  —  already lowest",
                  bg="#dcfce7", fg=GOOD, size=12)
        draw_note(canvas,
                  "Top and bottom share no common factor larger than 1.",
                  h - 28, color=MUTED, size=11)


# ── Slide 6 — The arrow goes both ways ───────────────────────────────────────

def _slide_6(canvas, ex, w, h):
    """Fixed round-trip demo using 3/4 ↔ 0.75, independent of the current
    example. Shows both directions side-by-side so the pupil sees the
    symmetry even when cycling through one-direction examples."""
    draw_note(canvas,
              "Same number, two forms — the arrow goes both ways.",
              36, color=DIM, size=11)

    cy = 140

    # Left: 3/4 → 0.75 (multiply up to 100).
    lcx = w / 2 - 180
    _draw_fraction(canvas, lcx - 70, cy, 3, 4, size=30)
    canvas.create_text(lcx, cy, text="→",
                       fill=DIM, font=("Helvetica", 24, "bold"))
    canvas.create_text(lcx + 80, cy, text="0.75",
                       fill=GOOD, font=("Helvetica", 28, "bold"))
    canvas.create_text(lcx, cy - 50,
                       text="×25 top and bottom",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))
    canvas.create_text(lcx, cy + 52,
                       text="3/4 = 75/100 = 0.75",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))

    # Right: 0.75 → 3/4 (count digits, simplify).
    rcx = w / 2 + 180
    canvas.create_text(rcx - 80, cy, text="0.75",
                       fill=INK, font=("Helvetica", 28, "bold"))
    canvas.create_text(rcx, cy, text="→",
                       fill=DIM, font=("Helvetica", 24, "bold"))
    _draw_fraction(canvas, rcx + 70, cy, 3, 4,
                   num_color=GOOD, den_color=GOOD, size=30)
    canvas.create_text(rcx, cy - 50,
                       text="2 digits → hundredths",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))
    canvas.create_text(rcx, cy + 52,
                       text="75/100 ÷ 25 = 3/4",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))

    draw_pill(canvas, w / 2, cy + 108,
              "multiply up to a power of ten  ↔  divide by the greatest common divisor",
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              "The method depends on which form you start with — but it's the same idea either way.",
              h - 28, color=MUTED, size=11)


# ── Slide 7 — Full chain for this example ────────────────────────────────────

def _slide_7(canvas, ex, w, h):
    if ex["direction"] == "frac_to_dec":
        _slide_7_frac_to_dec(canvas, ex, w, h)
    else:
        _slide_7_dec_to_frac(canvas, ex, w, h)


def _slide_7_frac_to_dec(canvas, ex, w, h):
    frac_num   = ex["frac_num"]
    frac_den   = ex["frac_den"]
    mult       = ex["mult"]
    target_num = ex["target_num"]
    target_den = ex["target_den"]
    dec_str    = ex["dec_str"]

    draw_note(canvas,
              "The whole conversion in one line:",
              36, color=DIM, size=11)

    cy = 140
    x_start   = w / 2 - 240
    x_middle  = w / 2 - 20
    x_end     = w / 2 + 240

    _draw_fraction(canvas, x_start, cy, frac_num, frac_den, size=28)
    canvas.create_text((x_start + x_middle) / 2, cy, text="=",
                       fill=DIM, font=("Helvetica", 24, "bold"))
    _draw_fraction(canvas, x_middle, cy, target_num, target_den,
                   num_color=ACCENT, den_color=ACCENT, size=28)
    canvas.create_text((x_middle + x_end) / 2, cy, text="=",
                       fill=DIM, font=("Helvetica", 24, "bold"))
    canvas.create_text(x_end, cy, text=dec_str,
                       fill=GOOD, font=("Helvetica", 32, "bold"))

    # Beat labels below each stage.
    canvas.create_text(x_start, cy + 62,
                       text="clean form",
                       fill=MUTED, font=("Helvetica", 10))
    middle_text = (f"×{mult} → {_power_word(target_den)}"
                   if mult > 1 else f"already {_power_word(target_den)}")
    canvas.create_text(x_middle, cy + 62,
                       text=middle_text,
                       fill=ACCENT, font=("Helvetica", 10, "bold"))
    canvas.create_text(x_end, cy + 62,
                       text="read it off",
                       fill=GOOD, font=("Helvetica", 10, "bold"))

    draw_pill(canvas, w / 2, cy + 108,
              f"{frac_num}/{frac_den}  =  {target_num}/{target_den}  =  {dec_str}",
              bg="#dcfce7", fg=GOOD, size=12)

    draw_note(canvas,
              "Find the multiplier → rewrite with 10/100/1000 → read the decimal.",
              h - 28, color=MUTED, size=11)


def _slide_7_dec_to_frac(canvas, ex, w, h):
    dec_str    = ex["dec_str"]
    digit_n    = ex["digit_n"]
    target_num = ex["target_num"]
    target_den = ex["target_den"]
    frac_num   = ex["frac_num"]
    frac_den   = ex["frac_den"]
    g          = ex["gcd_reverse"]

    draw_note(canvas,
              "The whole conversion in one line:",
              36, color=DIM, size=11)

    cy = 140
    x_start  = w / 2 - 240
    x_middle = w / 2 - 20
    x_end    = w / 2 + 240

    canvas.create_text(x_start, cy, text=dec_str,
                       fill=INK, font=("Helvetica", 32, "bold"))
    canvas.create_text((x_start + x_middle) / 2, cy, text="=",
                       fill=DIM, font=("Helvetica", 24, "bold"))
    _draw_fraction(canvas, x_middle, cy, target_num, target_den,
                   num_color=ACCENT, den_color=ACCENT, size=28)
    canvas.create_text((x_middle + x_end) / 2, cy, text="=",
                       fill=DIM, font=("Helvetica", 24, "bold"))
    _draw_fraction(canvas, x_end, cy, frac_num, frac_den,
                   num_color=GOOD, den_color=GOOD, size=28)

    canvas.create_text(x_start, cy + 62,
                       text=f"{digit_n} {_digit_noun(digit_n)} after the point",
                       fill=MUTED, font=("Helvetica", 10))
    canvas.create_text(x_middle, cy + 62,
                       text=f"raw {_power_word(target_den)}",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))
    canvas.create_text(x_end, cy + 62,
                       text=f"÷ greatest common divisor ({g})",
                       fill=GOOD, font=("Helvetica", 10, "bold"))

    draw_pill(canvas, w / 2, cy + 108,
              f"{dec_str}  =  {target_num}/{target_den}  =  {frac_num}/{frac_den}",
              bg="#dcfce7", fg=GOOD, size=12)

    draw_note(canvas,
              "Count the digits → put them on top → simplify.  Done.",
              h - 28, color=MUTED, size=11)


# ── Slide 8 — Pitfalls ───────────────────────────────────────────────────────
#
# Fixed example: 3/8 = 0.375 (correct) vs. two canonical wrongs:
#   1)  3/8 ≠ 0.38  — copied the denominator straight into the decimal slot.
#   2)  1/4 ≠ 0.4   — treated the denominator as if it were a decimal place.

def _slide_8(canvas, ex, w, h):
    draw_note(canvas,
              "Watch out for these two common mistakes.",
              36, color=DIM, size=11)

    cy     = 140
    tk_red = "#dc2626"

    col_cx = [w / 2 - 230, w / 2, w / 2 + 230]

    # ── Column 1: Correct, 3/8 = 0.375 ──────────────────────────────────────
    canvas.create_text(col_cx[0], cy - 78, text="Correct",
                       fill=GOOD, font=("Helvetica", 11, "bold"))
    _draw_column_conv(canvas, col_cx[0], cy,
                      "3/8", "0.375", res_color=GOOD)
    canvas.create_text(col_cx[0], cy + 58,
                       text="3/8 × 125/125 = 375/1000",
                       fill=GOOD, font=("Helvetica", 9))

    # ── Column 2: Wrong A — copied digits ───────────────────────────────────
    canvas.create_text(col_cx[1], cy - 78, text="Wrong",
                       fill=tk_red, font=("Helvetica", 11, "bold"))
    _draw_column_conv(canvas, col_cx[1], cy,
                      "3/8", "0.38", res_color=tk_red, faded=True)
    canvas.create_text(col_cx[1], cy + 58,
                       text="can't just copy the digits",
                       fill=tk_red, font=("Helvetica", 9, "italic"))

    # ── Column 3: Wrong B — denominator mistaken for a decimal place ────────
    canvas.create_text(col_cx[2], cy - 78, text="Wrong",
                       fill=tk_red, font=("Helvetica", 11, "bold"))
    _draw_column_conv(canvas, col_cx[2], cy,
                      "1/4", "0.4", res_color=tk_red, faded=True)
    canvas.create_text(col_cx[2], cy + 58,
                       text="4 is the piece count, not the decimal place",
                       fill=tk_red, font=("Helvetica", 9, "italic"))

    # ≠ glyphs between each column.
    canvas.create_text((col_cx[0] + col_cx[1]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))
    canvas.create_text((col_cx[1] + col_cx[2]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))

    draw_pill(canvas, w / 2, cy + 92,
              "always: find the multiplier, rewrite with 10/100/1000, "
              "then read the decimal",
              bg="#fef3c7", fg=WARN, size=11)

    draw_note(canvas,
              "The fraction bar is division — not a free pass to move digits around the point.",
              h - 26, color=WARN, size=12)


def _draw_column_conv(canvas, cx, cy, frac_str, dec_str,
                      res_color=INK, faded=False):
    """Render 'a/b = 0.xx' centred on cx. faded dims the non-result tokens."""
    body_col = DIM if faded else INK
    a, b = frac_str.split("/")
    x_f  = cx - 52
    x_eq = cx
    x_d  = cx + 52
    _draw_fraction(canvas, x_f, cy, a, b,
                   num_color=body_col, den_color=body_col, size=24)
    canvas.create_text(x_eq, cy, text="=",
                       fill=DIM, font=("Helvetica", 22, "bold"))
    canvas.create_text(x_d, cy, text=dec_str,
                       fill=res_color, font=("Helvetica", 22, "bold"))


# ── Slide list (what the framework consumes) ─────────────────────────────────

SLIDES = [
    {
        "title":   "1 · Read the question",
        "caption": ("Fractions and decimals are two ways of writing the "
                    "same number.  The job is to switch between the forms."),
        "draw":    _slide_1,
    },
    {
        "title":   "2 · Decimals name the piece size",
        "caption": ("Each digit after the point counts pieces of a fixed "
                    "size — tenths, hundredths, thousandths."),
        "draw":    _slide_2,
    },
    {
        "title":   "3 · Find the bridge number",
        "caption": ("Going to a decimal: find what the denominator must be "
                    "multiplied by to reach 10, 100, or 1000.  Going to a "
                    "fraction: count the digits after the point — that's "
                    "the bottom."),
        "draw":    _slide_3,
    },
    {
        "title":   "4 · Apply the rewrite",
        "caption": ("Going to a decimal: multiply top AND bottom by the "
                    "same number.  Going to a fraction: put the digits on "
                    "top over the power-of-ten denominator you just "
                    "counted."),
        "draw":    _slide_4,
    },
    {
        "title":   "5 · Read it off (or simplify)",
        "caption": ("Fraction → decimal: the top becomes the digits, and "
                    "the bottom's zeros set the place value.  "
                    "Decimal → fraction: divide top and bottom by the "
                    "greatest common divisor to reach the clean form."),
        "draw":    _slide_5,
    },
    {
        "title":   "6 · The arrow goes both ways",
        "caption": ("Same number, two forms.  Multiplying up to a power "
                    "of ten and dividing back down by the greatest common "
                    "divisor are the two halves of the same round trip."),
        "draw":    _slide_6,
    },
    {
        "title":   "7 · The whole pipeline",
        "caption": ("Starting form to final form on a single line — the "
                    "method for this example, compressed."),
        "draw":    _slide_7,
    },
    {
        "title":   "8 · Watch the pitfalls",
        "caption": ("Two classic mistakes: copying digits straight across "
                    "the fraction bar, and treating the denominator as a "
                    "decimal place.  Always rewrite to 10, 100, or 1000 "
                    "first — that's the one step the pitfalls skip."),
        "draw":    _slide_8,
    },
]
