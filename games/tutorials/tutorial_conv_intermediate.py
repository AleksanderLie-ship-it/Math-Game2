"""
tutorial_conv_intermediate.py
-----------------------------
Tutorial content for Conversions: Intermediate — converting between
fractions and percentages (integer % only).

Framing
-------
A percentage IS a fraction with 100 on the bottom. The "%" sign literally
reads as "divided by 100" — so "25%" is just another way of writing
"25/100". The job is to move between the two forms without losing the
value.

Pedagogy (fraction → percentage direction)
------------------------------------------
1. Rewrite the fraction with 100 on the bottom. Find the multiplier m
   such that denom × m = 100.
2. Multiply the TOP by the same m. You now have x/100.
3. Read off: x/100 = x%.
   - 3/4:   4 × 25 = 100, 3 × 25 = 75 → 75/100 = 75%.
   - 1/2:   2 × 50 = 100, 1 × 50 = 50 → 50/100 = 50%.
   - 2/5:   5 × 20 = 100, 2 × 20 = 40 → 40/100 = 40%.
   - 3/20: 20 × 5  = 100, 3 × 5  = 15 → 15/100 = 15%.

Pedagogy (percentage → fraction direction)
------------------------------------------
1. Drop the "%" — it becomes a denominator of 100. pct% → pct/100.
2. Divide top AND bottom by the greatest common divisor to simplify.
3. Result lands on the clean-pool fraction (1/2, 1/4, 3/4, 2/5, ...).
   - 25%: 25/100, greatest common divisor = 25, → 1/4.

Examples cycle 5 curated pairs drawn from conv_intermediate._PAIRS.
Four are canonical fraction→percentage; one (25% → 1/4) is canonical
percentage→fraction so the pupil meets the reverse direction inside the
carousel. Only the CLEAN-INTEGER tier of the pool is taught — rounded
pairs (1/3↔33, 2/3↔67, 1/8↔13, 3/8↔38) belong to the game's tolerance
handling, not to the tutorial method.

Raw ints throughout — fractions.Fraction auto-reduces on construction,
which would silently collapse "75/100" into "3/4" and destroy the whole
teaching point of showing the intermediate 100-bottom form.

Slide plan
----------
1. Read the question    — show the current example's prompt cleanly.
2. Place-value anchor   — 10x10 hundredths grid with pct cells shaded.
3. Find the bridge      — per-direction: denom × m = 100, or drop the %.
4. Apply the rewrite    — per-direction: ×m top AND bottom, or ÷g top
                          AND bottom.
5. Read off or simplify — frac_to_pct: read the top with a % sign.
                          pct_to_frac: land on the clean-pool fraction.
6. Round-trip demo      — fixed 3/4 <-> 75%, always visible.
7. Full chain           — compact end-to-end render of the current example.
8. Pitfall              — 1/4 ≠ 14% (bottom dropped straight next to top),
                          3/4 ≠ 34% (read the top, ignored the bottom).
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

from .slideshow_frame import (
    INK, MUTED, DIM, ACCENT, GOOD, WARN, CARD_BG,
    draw_note, draw_arrow, draw_pill,
)


TITLE = "Conversions: Intermediate — fraction ↔ percentage"
LEAD  = "A percentage is a fraction with 100 on the bottom. That's the whole trick."


# ── Examples ─────────────────────────────────────────────────────────────────
#
# Each example has one canonical direction ("frac_to_pct" or "pct_to_frac")
# and pre-computed fields so every slide draws the chain without recomputing.
# Raw ints only — never Fraction.
#
# Fields:
#   direction    : "frac_to_pct" or "pct_to_frac"
#   frac_num     : clean-form numerator  (matches conv_intermediate._PAIRS)
#   frac_den     : clean-form denominator
#   pct          : integer percentage
#   mult         : multiplier m such that frac_den × m == 100
#                  (also  frac_num × m == pct)
#   gcd_reverse  : gcd(pct, 100). On the pct→frac path the pupil divides
#                  both sides by this to reach the clean form.
#
# Invariants (also asserted in the verification harness):
#   frac_den * mult == 100
#   frac_num * mult == pct
#   gcd_reverse == gcd(pct, 100)
#   pct // gcd_reverse == frac_num  and  100 // gcd_reverse == frac_den
#
# Three frac_to_pct + two pct_to_frac — rebalanced in the v0.7.5 polish
# pass so the pupil drills both directions rather than only meeting
# percentage→fraction once inside the carousel.
EXAMPLES = [
    # 3/4 ↔ 75%   (frac→pct, ×25 — headline, matches round-trip demo)
    dict(direction="frac_to_pct", frac_num=3, frac_den=4,  pct=75, mult=25, gcd_reverse=25),
    # 50% ↔ 1/2   (pct→frac, ÷50 — easy confidence win in the reverse direction)
    dict(direction="pct_to_frac", frac_num=1, frac_den=2,  pct=50, mult=50, gcd_reverse=50),
    # 2/5 ↔ 40%   (frac→pct, ×20 — neither 25 nor 50, forces general case)
    dict(direction="frac_to_pct", frac_num=2, frac_den=5,  pct=40, mult=20, gcd_reverse=20),
    # 25% ↔ 1/4   (pct→frac, ÷25 — second reverse example, different gcd)
    dict(direction="pct_to_frac", frac_num=1, frac_den=4,  pct=25, mult=25, gcd_reverse=25),
    # 3/20 ↔ 15%  (frac→pct, ×5 — den already a factor of 100, small bridge)
    dict(direction="frac_to_pct", frac_num=3, frac_den=20, pct=15, mult=5,  gcd_reverse=5),
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _draw_fraction(canvas, cx, cy, num_text, den_text,
                   num_color=INK, den_color=INK, size=30):
    """Draw a stacked fraction centred on (cx, cy). Returns (top_y, bot_y)."""
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


def _draw_hundred_grid_shaded(canvas, gx, gy, size, shaded_n,
                              shade_fill="#dcfce7", empty_fill=None):
    """Draw a 10×10 hundredths grid at (gx, gy) spanning `size` pixels.
    Shade the first `shaded_n` cells (row-major). Returns the cell side
    length for caller layout. Kept private to this tutorial — mirrors the
    helper used in conv_basic slide 2 but generalised on shaded_n."""
    cell = size / 10
    empty = empty_fill if empty_fill is not None else CARD_BG
    idx = 0
    for r in range(10):
        for c in range(10):
            fill = shade_fill if idx < shaded_n else empty
            canvas.create_rectangle(gx + c * cell, gy + r * cell,
                                    gx + (c + 1) * cell,
                                    gy + (r + 1) * cell,
                                    outline=INK, width=1, fill=fill)
            idx += 1
    return cell


# ── Slide 1 — Read the question ──────────────────────────────────────────────

def _slide_1(canvas, ex, w, h):
    direction = ex["direction"]

    if direction == "frac_to_pct":
        draw_note(canvas,
                  "The question:  convert this fraction to a percentage.",
                  38, color=DIM, size=11)
    else:
        draw_note(canvas,
                  "The question:  convert this percentage to a fraction.",
                  38, color=DIM, size=11)

    cy = 135

    if direction == "frac_to_pct":
        _draw_fraction(canvas, w / 2 - 80, cy,
                       ex["frac_num"], ex["frac_den"], size=36)
        canvas.create_text(w / 2 + 10, cy, text="=",
                           fill=DIM, font=("Helvetica", 32, "bold"))
        canvas.create_text(w / 2 + 80, cy, text="?%",
                           fill=ACCENT, font=("Helvetica", 34, "bold"))
    else:
        canvas.create_text(w / 2 - 80, cy, text=f"{ex['pct']}%",
                           fill=INK, font=("Helvetica", 36, "bold"))
        canvas.create_text(w / 2 + 10, cy, text="=",
                           fill=DIM, font=("Helvetica", 32, "bold"))
        canvas.create_text(w / 2 + 80, cy, text="?",
                           fill=ACCENT, font=("Helvetica", 34, "bold"))

    # Anchor pill carrying the whole-pack framing. GOOD green (matches
    # the conv_basic slide 1 anchor treatment).
    draw_pill(canvas, w / 2, cy + 82,
              "% means  /100.  That's the whole trick.",
              bg="#dcfce7", fg=GOOD, size=12)

    # In-canvas muted note is now a one-line complement to the pill above,
    # not a repeat of the caption below. (v0.7.5 polish.)
    draw_note(canvas,
              "The bottom of a percentage is always 100.",
              h - 28, color=MUTED, size=11)


# ── Slide 2 — Place-value anchor (100 grid) ──────────────────────────────────

def _slide_2(canvas, ex, w, h):
    pct = ex["pct"]

    # 10×10 hundredths grid centred horizontally. v0.7.5 polish: grid
    # shrunk from 200 → 170 px so the grid label, the pill and the bottom
    # muted note all sit in non-overlapping y-bands (the original 200 px
    # version pushed the pill to y≈316, which collided with the bottom
    # draw_note at h−28=312). Second polish pass: removed the y=36 top
    # note "A percentage counts pieces out of 100." — it duplicated the
    # slide caption and its baseline brushed the grid label at y=46.
    # New layout:
    #   grid_y = 60, size = 170 → grid bottom at y=230
    #   above-grid label      y = 46  (clear airspace above — no top note)
    #   below-grid label      y = 246 (grid bottom + 16)
    #   pill                  y = 274 (grid bottom + 44)
    #   bottom muted note     y = 312 (h − 28) — clear of the pill
    grid_size = 170
    grid_x    = (w - grid_size) / 2
    grid_y    = 60
    _draw_hundred_grid_shaded(canvas, grid_x, grid_y, grid_size, pct)

    # Labels above and below the grid.
    canvas.create_text(grid_x + grid_size / 2, grid_y - 14,
                       text="hundredths grid — 100 equal squares",
                       fill=MUTED, font=("Helvetica", 10, "bold"))
    canvas.create_text(grid_x + grid_size / 2, grid_y + grid_size + 16,
                       text=f"{pct} shaded  →  {pct}/100  =  {pct}%",
                       fill=GOOD, font=("Helvetica", 11, "bold"))

    # One concise pill carrying the teaching sentence in plain language.
    # v0.7.5 polish: reworded so the pupil sees WHAT a percentage names
    # rather than the abstract "% literally reads as 'out of 100'". Kept
    # under ~55 rendered chars at size=11 bold so the pill bbox stays
    # safely inside [20, w-20].
    draw_pill(canvas, w / 2, grid_y + grid_size + 44,
              "% names how many of the 100 squares are shaded",
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              "The % sign is just shorthand for 'out of 100'.",
              h - 28, color=MUTED, size=11)


# ── Slide 3 — Find the bridge ────────────────────────────────────────────────

def _slide_3(canvas, ex, w, h):
    if ex["direction"] == "frac_to_pct":
        _slide_3_frac_to_pct(canvas, ex, w, h)
    else:
        _slide_3_pct_to_frac(canvas, ex, w, h)


def _slide_3_frac_to_pct(canvas, ex, w, h):
    frac_den = ex["frac_den"]
    mult     = ex["mult"]

    draw_note(canvas,
              f"What do we multiply {frac_den} by to land on 100?",
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
    canvas.create_text(x_target, cy, text="100",
                       fill=GOOD, font=("Helvetica", 34, "bold"))

    # Dashed accent bridge from frac_den over to 100, flat horizontal so
    # the arrowhead geometry is predictable and can't intrude on the
    # numerals below.
    canvas.create_text(x_mult, cy - 48, text=f"×{mult}",
                       fill=ACCENT, font=("Helvetica", 12, "bold"))
    draw_arrow(canvas, x_den + 22, cy - 28, x_target - 22, cy - 28,
               color=ACCENT, width=2, dash=(4, 3))

    # Short edge-case note for den=10 (would be mult=10 — one clean jump
    # to the tens). Inline rather than a separate slide path; the helper
    # slide copy adapts per-example.
    if frac_den == 10:
        note = f"{frac_den} is already tens  —  one jump to 100"
    else:
        note = f"{frac_den} × {mult} = 100"

    draw_pill(canvas, w / 2, cy + 82,
              note,
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              "Every clean-pool bottom (2, 4, 5, 10, 20, 25, 50) reaches 100 with one multiplier.",
              h - 28, color=MUTED, size=11)


def _slide_3_pct_to_frac(canvas, ex, w, h):
    pct = ex["pct"]
    g   = ex["gcd_reverse"]

    draw_note(canvas,
              "Drop the % sign — it becomes a bottom of 100.",
              36, color=DIM, size=11)

    cy = 135

    # Big "pct%" on the left.
    lx = w / 2 - 150
    canvas.create_text(lx, cy, text=f"{pct}%",
                       fill=INK, font=("Helvetica", 40, "bold"))
    canvas.create_text(lx, cy + 48,
                       text="% means ÷100",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))

    # Arrow → raw pct/100 fraction.
    canvas.create_text(w / 2, cy, text="→",
                       fill=DIM, font=("Helvetica", 28, "bold"))

    # Right: the raw fraction pct/100 in green.
    rx = w / 2 + 150
    _draw_fraction(canvas, rx, cy, pct, 100,
                   num_color=GOOD, den_color=GOOD, size=34)
    canvas.create_text(rx, cy - 72,
                       text="top is the percent number",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))
    draw_arrow(canvas, rx, cy - 60, rx, cy - 48,
               color=ACCENT, width=2)

    draw_pill(canvas, w / 2, cy + 98,
              f"{pct}%  =  {pct}/100  —  now find the greatest common divisor of {pct} and 100",
              bg="#dcfce7", fg=GOOD, size=11)

    # Short take-home reminder naming the divisor, in prose.
    draw_note(canvas,
              f"For {pct} and 100 the greatest common divisor is {g}. That's the shrink factor.",
              h - 28, color=MUTED, size=11)


# ── Slide 4 — Apply the rewrite ──────────────────────────────────────────────

def _slide_4(canvas, ex, w, h):
    if ex["direction"] == "frac_to_pct":
        _slide_4_frac_to_pct(canvas, ex, w, h)
    else:
        _slide_4_pct_to_frac(canvas, ex, w, h)


def _slide_4_frac_to_pct(canvas, ex, w, h):
    frac_num = ex["frac_num"]
    frac_den = ex["frac_den"]
    mult     = ex["mult"]
    pct      = ex["pct"]

    draw_note(canvas,
              f"Multiply the TOP by the same {mult}.  The value doesn't change.",
              38, color=DIM, size=11)

    cy   = 135
    f_cx = [w / 2 - 220, w / 2 - 80, w / 2 + 40, w / 2 + 180]

    _draw_fraction(canvas, f_cx[0], cy, frac_num, frac_den, size=30)
    canvas.create_text(f_cx[1] - 14, cy, text="×",
                       fill=INK, font=("Helvetica", 28, "bold"))
    _draw_fraction(canvas, f_cx[1] + 30, cy, mult, mult,
                   num_color=ACCENT, den_color=ACCENT, size=30)
    canvas.create_text(f_cx[2] + 30, cy, text="=",
                       fill=DIM, font=("Helvetica", 28, "bold"))
    _draw_fraction(canvas, f_cx[3], cy, pct, 100,
                   num_color=GOOD, den_color=GOOD, size=30)

    # ×m call-outs on the LEFT fraction.
    # size=30 glyphs → cy±34 glyph edges → labels at cy±66, tips at cy±44
    # gives the v0.7.3 10-px clearance rule.
    canvas.create_text(f_cx[0], cy - 66, text=f"×{mult}",
                       fill=ACCENT, font=("Helvetica", 11, "bold"))
    canvas.create_text(f_cx[0], cy + 66, text=f"×{mult}",
                       fill=ACCENT, font=("Helvetica", 11, "bold"))
    draw_arrow(canvas, f_cx[0], cy - 56, f_cx[0], cy - 44,
               color=ACCENT, width=2)
    draw_arrow(canvas, f_cx[0], cy + 56, f_cx[0], cy + 44,
               color=ACCENT, width=2)

    draw_pill(canvas, w / 2, cy + 95,
              f"{frac_num}/{frac_den}  =  {pct}/100  (same value, now on 100)",
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              "Multiplying top and bottom by the same number leaves the value unchanged.",
              h - 28, color=MUTED, size=11)


def _slide_4_pct_to_frac(canvas, ex, w, h):
    pct      = ex["pct"]
    g        = ex["gcd_reverse"]
    frac_num = ex["frac_num"]
    frac_den = ex["frac_den"]

    draw_note(canvas,
              f"Divide the top AND bottom by {g} — the greatest common divisor.",
              38, color=DIM, size=11)

    cy   = 135
    f_cx = [w / 2 - 220, w / 2 - 80, w / 2 + 40, w / 2 + 180]

    _draw_fraction(canvas, f_cx[0], cy, pct, 100, size=30)
    canvas.create_text(f_cx[1] - 14, cy, text="÷",
                       fill=INK, font=("Helvetica", 28, "bold"))
    _draw_fraction(canvas, f_cx[1] + 30, cy, g, g,
                   num_color=ACCENT, den_color=ACCENT, size=30)
    canvas.create_text(f_cx[2] + 30, cy, text="=",
                       fill=DIM, font=("Helvetica", 28, "bold"))
    _draw_fraction(canvas, f_cx[3], cy, frac_num, frac_den,
                   num_color=GOOD, den_color=GOOD, size=30)

    # ÷g call-outs on the LEFT fraction (size=30 glyphs, same geometry
    # as the frac_to_pct slide 4 ×m callouts).
    canvas.create_text(f_cx[0], cy - 66, text=f"÷{g}",
                       fill=ACCENT, font=("Helvetica", 11, "bold"))
    canvas.create_text(f_cx[0], cy + 66, text=f"÷{g}",
                       fill=ACCENT, font=("Helvetica", 11, "bold"))
    draw_arrow(canvas, f_cx[0], cy - 56, f_cx[0], cy - 44,
               color=ACCENT, width=2)
    draw_arrow(canvas, f_cx[0], cy + 56, f_cx[0], cy + 44,
               color=ACCENT, width=2)

    draw_pill(canvas, w / 2, cy + 95,
              f"{pct}/100  =  {frac_num}/{frac_den}  (same value, now in simplest form)",
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              "Dividing top and bottom by the same number leaves the value unchanged.",
              h - 28, color=MUTED, size=11)


# ── Slide 5 — Read it off (or confirm simplest form) ─────────────────────────

def _slide_5(canvas, ex, w, h):
    if ex["direction"] == "frac_to_pct":
        _slide_5_frac_to_pct(canvas, ex, w, h)
    else:
        _slide_5_pct_to_frac(canvas, ex, w, h)


def _slide_5_frac_to_pct(canvas, ex, w, h):
    pct = ex["pct"]

    draw_note(canvas,
              "Any fraction on 100 — just read the top with a % sign.",
              38, color=DIM, size=11)

    cy = 135

    # Left: pct/100 in the intermediate form.
    lx = w / 2 - 140
    _draw_fraction(canvas, lx, cy, pct, 100, size=34)

    # Middle: equals.
    canvas.create_text(w / 2, cy, text="=",
                       fill=DIM, font=("Helvetica", 28, "bold"))

    # Right: the percentage, big and green.
    rx = w / 2 + 140
    canvas.create_text(rx, cy, text=f"{pct}%",
                       fill=GOOD, font=("Helvetica", 40, "bold"))

    # Double underline under the percentage. 40 pt bold ≈ 12 px per char;
    # half-width = len * 6 gives a snug underline. cy+42 is 10 px below
    # the glyph bottom.
    pct_str = f"{pct}%"
    u_half  = len(pct_str) * 12
    u_x1    = rx - u_half
    u_x2    = rx + u_half
    u_y     = cy + 42
    canvas.create_line(u_x1, u_y,     u_x2, u_y,     fill=GOOD, width=2)
    canvas.create_line(u_x1, u_y + 5, u_x2, u_y + 5, fill=GOOD, width=2)

    draw_pill(canvas, w / 2, cy + 100,
              "any fraction over 100 — just read the top with a % sign",
              bg="#dcfce7", fg=GOOD, size=12)

    draw_note(canvas,
              "The top is the percent number. The % sign carries the ÷100 for you.",
              h - 28, color=MUTED, size=11)


def _slide_5_pct_to_frac(canvas, ex, w, h):
    frac_num = ex["frac_num"]
    frac_den = ex["frac_den"]

    draw_note(canvas,
              "Check: the fraction is now in lowest terms.",
              38, color=DIM, size=11)

    cy = 135

    _draw_fraction(canvas, w / 2, cy, frac_num, frac_den,
                   num_color=GOOD, den_color=GOOD, size=40)

    # Green check to the right of the fraction.
    canvas.create_text(w / 2 + 80, cy, text="✓",
                       fill=GOOD, font=("Helvetica", 30, "bold"))

    # Double underline under the fraction.
    u_half = 42
    u_x1   = w / 2 - u_half
    u_x2   = w / 2 + u_half
    u_y    = cy + 54
    canvas.create_line(u_x1, u_y,     u_x2, u_y,     fill=GOOD, width=2)
    canvas.create_line(u_x1, u_y + 5, u_x2, u_y + 5, fill=GOOD, width=2)

    draw_pill(canvas, w / 2, cy + 105,
              "lowest terms — matches the clean pool",
              bg="#dcfce7", fg=GOOD, size=12)

    draw_note(canvas,
              "Top and bottom share no common factor larger than 1. This is the answer.",
              h - 28, color=MUTED, size=11)


# ── Slide 6 — The arrow goes both ways ───────────────────────────────────────

def _slide_6(canvas, ex, w, h):
    """Fixed round-trip demo using 3/4 ↔ 75%, independent of the current
    example. Same rationale as conv_basic slide 6 — the pupil sees the
    symmetry regardless of which direction the cycled example happens to
    be using."""
    draw_note(canvas,
              "Same number, two forms — the arrow goes both ways.",
              36, color=DIM, size=11)

    cy = 140

    # Left: 3/4 → 75% (multiply top and bottom by 25 to land on 100).
    lcx = w / 2 - 180
    _draw_fraction(canvas, lcx - 70, cy, 3, 4, size=30)
    canvas.create_text(lcx, cy, text="→",
                       fill=DIM, font=("Helvetica", 24, "bold"))
    canvas.create_text(lcx + 80, cy, text="75%",
                       fill=GOOD, font=("Helvetica", 28, "bold"))
    canvas.create_text(lcx, cy - 50,
                       text="×25 top and bottom",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))
    canvas.create_text(lcx, cy + 52,
                       text="3/4 = 75/100 = 75%",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))

    # Right: 75% → 3/4 (drop the %, divide by greatest common divisor).
    rcx = w / 2 + 180
    canvas.create_text(rcx - 80, cy, text="75%",
                       fill=INK, font=("Helvetica", 28, "bold"))
    canvas.create_text(rcx, cy, text="→",
                       fill=DIM, font=("Helvetica", 24, "bold"))
    _draw_fraction(canvas, rcx + 70, cy, 3, 4,
                   num_color=GOOD, den_color=GOOD, size=30)
    canvas.create_text(rcx, cy - 50,
                       text="drop the %, then ÷25",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))
    canvas.create_text(rcx, cy + 52,
                       text="75% = 75/100 ÷25 = 3/4",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))

    draw_pill(canvas, w / 2, cy + 108,
              "multiply up to 100  ·  divide back to the fraction",
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              "The method depends on which form you start with — but it's the same round trip either way.",
              h - 28, color=MUTED, size=11)


# ── Slide 7 — Full chain for this example ────────────────────────────────────

def _slide_7(canvas, ex, w, h):
    if ex["direction"] == "frac_to_pct":
        _slide_7_frac_to_pct(canvas, ex, w, h)
    else:
        _slide_7_pct_to_frac(canvas, ex, w, h)


def _slide_7_frac_to_pct(canvas, ex, w, h):
    frac_num = ex["frac_num"]
    frac_den = ex["frac_den"]
    mult     = ex["mult"]
    pct      = ex["pct"]

    draw_note(canvas,
              "The whole conversion in one line:",
              36, color=DIM, size=11)

    cy = 140
    x_start  = w / 2 - 240
    x_middle = w / 2 - 20
    x_end    = w / 2 + 240

    _draw_fraction(canvas, x_start, cy, frac_num, frac_den, size=28)
    canvas.create_text((x_start + x_middle) / 2, cy, text="=",
                       fill=DIM, font=("Helvetica", 24, "bold"))
    _draw_fraction(canvas, x_middle, cy, pct, 100,
                   num_color=ACCENT, den_color=ACCENT, size=28)
    canvas.create_text((x_middle + x_end) / 2, cy, text="=",
                       fill=DIM, font=("Helvetica", 24, "bold"))
    canvas.create_text(x_end, cy, text=f"{pct}%",
                       fill=GOOD, font=("Helvetica", 32, "bold"))

    # Beat labels below each stage.
    canvas.create_text(x_start, cy + 62,
                       text="clean form",
                       fill=MUTED, font=("Helvetica", 10))
    canvas.create_text(x_middle, cy + 62,
                       text=f"×{mult}  →  on 100",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))
    canvas.create_text(x_end, cy + 62,
                       text="read it with %",
                       fill=GOOD, font=("Helvetica", 10, "bold"))

    draw_pill(canvas, w / 2, cy + 108,
              f"{frac_num}/{frac_den}  =  {pct}/100  =  {pct}%",
              bg="#dcfce7", fg=GOOD, size=12)

    draw_note(canvas,
              "Find the multiplier → rewrite on 100 → read the top with a % sign.",
              h - 28, color=MUTED, size=11)


def _slide_7_pct_to_frac(canvas, ex, w, h):
    pct      = ex["pct"]
    g        = ex["gcd_reverse"]
    frac_num = ex["frac_num"]
    frac_den = ex["frac_den"]

    draw_note(canvas,
              "The whole conversion in one line:",
              36, color=DIM, size=11)

    cy = 140
    x_start  = w / 2 - 240
    x_middle = w / 2 - 20
    x_end    = w / 2 + 240

    canvas.create_text(x_start, cy, text=f"{pct}%",
                       fill=INK, font=("Helvetica", 32, "bold"))
    canvas.create_text((x_start + x_middle) / 2, cy, text="=",
                       fill=DIM, font=("Helvetica", 24, "bold"))
    _draw_fraction(canvas, x_middle, cy, pct, 100,
                   num_color=ACCENT, den_color=ACCENT, size=28)
    canvas.create_text((x_middle + x_end) / 2, cy, text="=",
                       fill=DIM, font=("Helvetica", 24, "bold"))
    _draw_fraction(canvas, x_end, cy, frac_num, frac_den,
                   num_color=GOOD, den_color=GOOD, size=28)

    canvas.create_text(x_start, cy + 62,
                       text="drop the %",
                       fill=MUTED, font=("Helvetica", 10))
    canvas.create_text(x_middle, cy + 62,
                       text="raw over 100",
                       fill=ACCENT, font=("Helvetica", 10, "bold"))
    canvas.create_text(x_end, cy + 62,
                       text=f"÷ greatest common divisor ({g})",
                       fill=GOOD, font=("Helvetica", 10, "bold"))

    draw_pill(canvas, w / 2, cy + 108,
              f"{pct}%  =  {pct}/100  =  {frac_num}/{frac_den}",
              bg="#dcfce7", fg=GOOD, size=12)

    draw_note(canvas,
              "Drop the % → put the number over 100 → simplify.  Done.",
              h - 28, color=MUTED, size=11)


# ── Slide 8 — Pitfalls ───────────────────────────────────────────────────────
#
# Fixed examples. Two canonical wrong readings of the "just combine the
# digits" variety the pupil is most likely to write down:
#   1)  1/4 ≠ 14%  — dropped the denominator and wrote top and bottom
#                    side-by-side as if they made a two-digit number.
#   2)  3/4 ≠ 34%  — read the top as the percent and ignored the bottom.

def _slide_8(canvas, ex, w, h):
    draw_note(canvas,
              "Watch out for these two common mistakes.",
              36, color=DIM, size=11)

    cy     = 140
    tk_red = "#dc2626"

    col_cx = [w / 2 - 230, w / 2, w / 2 + 230]

    # ── Column 1: Correct, 1/4 = 25% ────────────────────────────────────────
    canvas.create_text(col_cx[0], cy - 78, text="Correct",
                       fill=GOOD, font=("Helvetica", 11, "bold"))
    _draw_column_pct(canvas, col_cx[0], cy,
                     "1/4", "25%", res_color=GOOD)
    canvas.create_text(col_cx[0], cy + 58,
                       text="1/4 × 25/25 = 25/100",
                       fill=GOOD, font=("Helvetica", 9))

    # ── Column 2: Wrong A — digits written side by side ─────────────────────
    canvas.create_text(col_cx[1], cy - 78, text="Wrong",
                       fill=tk_red, font=("Helvetica", 11, "bold"))
    _draw_column_pct(canvas, col_cx[1], cy,
                     "1/4", "14%", res_color=tk_red, faded=True)
    canvas.create_text(col_cx[1], cy + 58,
                       text="dropped the denominator",
                       fill=tk_red, font=("Helvetica", 9, "italic"))

    # ── Column 3: Wrong B — top read as the percent ────────────────────────
    canvas.create_text(col_cx[2], cy - 78, text="Wrong",
                       fill=tk_red, font=("Helvetica", 11, "bold"))
    _draw_column_pct(canvas, col_cx[2], cy,
                     "3/4", "34%", res_color=tk_red, faded=True)
    canvas.create_text(col_cx[2], cy + 58,
                       text="ignored the bottom",
                       fill=tk_red, font=("Helvetica", 9, "italic"))

    # ≠ glyphs between columns.
    canvas.create_text((col_cx[0] + col_cx[1]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))
    canvas.create_text((col_cx[1] + col_cx[2]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))

    draw_pill(canvas, w / 2, cy + 92,
              "always: rewrite on 100 first, then read the top as the % number",
              bg="#fef3c7", fg=WARN, size=11)

    draw_note(canvas,
              "The bottom sets the piece size — you can't just staple the top to the word 'percent'.",
              h - 26, color=WARN, size=12)


def _draw_column_pct(canvas, cx, cy, frac_str, pct_str,
                     res_color=INK, faded=False):
    """Render 'a/b = pct%' centred on cx. faded dims the non-result tokens."""
    body_col = DIM if faded else INK
    a, b = frac_str.split("/")
    x_f  = cx - 52
    x_eq = cx
    x_d  = cx + 52
    _draw_fraction(canvas, x_f, cy, a, b,
                   num_color=body_col, den_color=body_col, size=24)
    canvas.create_text(x_eq, cy, text="=",
                       fill=DIM, font=("Helvetica", 22, "bold"))
    canvas.create_text(x_d, cy, text=pct_str,
                       fill=res_color, font=("Helvetica", 22, "bold"))


# ── Slide list (what the framework consumes) ─────────────────────────────────

SLIDES = [
    {
        "title":   "1 · Read the question",
        "caption": ("Percentages and fractions are two ways of writing "
                    "the same number.  The job is to switch between the "
                    "forms."),
        "draw":    _slide_1,
    },
    {
        "title":   "2 · A percentage counts out of 100",
        "caption": ("The hundredths grid has 100 equal squares.  A "
                    "percentage names how many of them are shaded — "
                    "the '%' sign carries the ÷100 for you."),
        "draw":    _slide_2,
    },
    {
        "title":   "3 · Find the bridge number",
        "caption": ("Going to a percentage: find what the denominator "
                    "must be multiplied by to reach 100.\n"
                    "Going to a fraction: drop the % — the number sits "
                    "over 100 — then find the greatest common divisor."),
        "draw":    _slide_3,
    },
    {
        "title":   "4 · Apply the rewrite",
        "caption": ("Going to a percentage: multiply top AND bottom by "
                    "the same number so the new bottom is 100.\n"
                    "Going to a fraction: divide top AND bottom by the "
                    "greatest common divisor to land on the clean form."),
        "draw":    _slide_4,
    },
    {
        "title":   "5 · Read it off (or confirm simplest form)",
        "caption": ("Fraction → percentage: any fraction on 100 is read "
                    "off as its top with a % sign.\n"
                    "Percentage → fraction: confirm the result is in "
                    "lowest terms and matches the clean pool."),
        "draw":    _slide_5,
    },
    {
        "title":   "6 · The arrow goes both ways",
        "caption": ("Same number, two forms.  Multiplying up to a "
                    "bottom of 100 and dividing back down by the "
                    "greatest common divisor are the two halves of the "
                    "same round trip."),
        "draw":    _slide_6,
    },
    {
        "title":   "7 · The whole pipeline",
        "caption": ("Starting form to final form on a single line — "
                    "the method for this example, compressed."),
        "draw":    _slide_7,
    },
    {
        "title":   "8 · Watch the pitfalls",
        "caption": ("Two classic mistakes: writing the top and bottom "
                    "side-by-side as if they were a two-digit percent, "
                    "and reading the top as the percent while ignoring "
                    "the bottom.  Always rewrite on 100 first — that's "
                    "the one step the pitfalls skip."),
        "draw":    _slide_8,
    },
]
