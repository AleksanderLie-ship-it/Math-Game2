"""
tutorial_mult_advanced.py
-------------------------
Tutorial content for Multiplication: Advanced — same Norwegian X-shift
method as Intermediate, just with longer factors. Game generates
3-digit × 2-digit (75 %) and Intermediate-pool fallbacks (25 %); the
tutorial also stretches into 2-digit × 3-digit and 3-digit × 3-digit
territory so the **XX** double-placeholder beat (the only thing
genuinely new vs. Intermediate) shows up in at least two examples.

What's new vs. Intermediate
---------------------------
Nothing about the *method* — it is verbatim the X-shift partial-products
algorithm Intermediate already teaches. The only mechanical change is
that a hundreds-digit multiplier produces a partial padded with **two**
X characters (XX), and a thousands-digit would produce **three** (XXX).
That is just a natural extension of the Intermediate rule
"k X's per place-shift".

Therefore the pack is intentionally short. Aleks's framing was: "longer
XXX × XX or XX × XXX examples — the method and intuition stay the
same; shouldn't need many slides; pitfall should emphasise forgetting
to add the 2 or 3 X's."

Pedagogy (in order)
-------------------
1. Refresher + the new beat — recap the X-shift via Intermediate's own
   `_draw_layout` on a 2-digit × 2-digit case, then announce the only
   new move: a hundreds-digit on the bottom adds **two** X's.
2. Walk the cycled example end-to-end — works for both the 3-digit ×
   2-digit case (game's 75 % branch) and the Intermediate-pool 2 × 2
   fallback (the 25 % branch). Layout fully reuses Intermediate's
   `_mult_steps` + `_draw_layout`.
3. The XX double-placeholder beat — fixed reference 23 × 145 = 3335
   so the pupil always sees the hundreds-row XX even when the cycled
   example doesn't reach 3-digit multipliers.
4. Pitfalls — fixed reference 23 × 145. Wrong A: forgot ONE X
   (treated hundreds-row as a tens-shift) → 1265. Wrong B: forgot
   BOTH X's (no shift on the hundreds row) → 1058. Direct pupil's
   eye to the X count = place-shift count rule.

Examples (5)
------------
Three game-range cases (3-dig × 2-dig and 2-dig × 2-dig from the 25%
branch) plus two stretch cases (2-dig × 3-dig and 3-dig × 3-dig)
that exercise the XX double-placeholder. The stretch cases sit just
beyond the game's generator so the tutorial pre-paves the algorithm
for any 3-digit multiplier the pupil might meet by hand later.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

from .slideshow_frame import (
    INK, MUTED, DIM, FAINT, SOFT, ACCENT, GOOD, WARN,
    draw_centered_expression, draw_note, draw_pill, build_slides,
)
from .tutorial_mult_intermediate import (
    _mult_steps,
    _draw_layout as _draw_intermediate_layout,
    COL_W, LINE_H, LAYOUT_FONT,
)


TITLE = "Multiplication: Advanced — longer factors"
LEAD  = "Same X-shift method as Intermediate. New beat: a hundreds digit means XX."


# ── Examples ─────────────────────────────────────────────────────────────────
#
# 1. 234 × 21  = 4914   — game's typical 3-dig × 2-dig (also the
#                          handwritten reference; revisit from Intermediate
#                          as a gentle "yes you already know this" warmup)
# 2. 312 × 23  = 7176   — different 3-dig × 2-dig, no shared digits
# 3. 145 × 36  = 5220   — 3-dig × 2-dig with a heavier carry
# 4.  23 × 145 = 3335   — 2-dig × 3-dig STRETCH: triggers the XX beat
# 5. 132 × 213 = 28116  — 3-dig × 3-dig STRETCH: XX beat at full strength

EXAMPLES = [
    {"top": 234, "bot":  21, "answer":  4914},
    {"top": 312, "bot":  23, "answer":  7176},
    {"top": 145, "bot":  36, "answer":  5220},
    {"top":  23, "bot": 145, "answer":  3335},
    {"top": 132, "bot": 213, "answer": 28116},
]


# ── Slide 1 — Refresher + the new beat ──────────────────────────────────────
#
# Render a familiar 23 × 15 chain via Intermediate's own `_draw_layout` so
# the pupil sees the exact picture they already know. Beside it, name the
# only new move (XX for a hundreds-digit multiplier).

_REFRESHER_REF = {"top": 23, "bot": 15, "answer": 345}


def _slide_1(canvas, ex, w, h):
    draw_note(canvas, "Refresher — the X-shift method you already know:",
              28, color=DIM, size=11)

    # LEFT half: render Intermediate-style layout of 23 × 15. Centre it
    # on the left third of the canvas; the helper centres on cx, so cx ≈ 220.
    _draw_intermediate_layout(canvas, cx=220, oy=70, ex=_REFRESHER_REF)

    # RIGHT half: the only new beat in Advanced.
    rx = w / 2 + 60
    ry = 78
    canvas.create_text(rx, ry, text="What is new in Advanced:",
                       fill=WARN, font=("Helvetica", 13, "bold"), anchor="w")
    canvas.create_text(rx, ry + 26,
                       text="• ones digit  →  no X",
                       fill=INK, font=("Helvetica", 12), anchor="w")
    canvas.create_text(rx, ry + 46,
                       text="• tens digit  →  one X",
                       fill=INK, font=("Helvetica", 12), anchor="w")
    canvas.create_text(rx, ry + 66,
                       text="• hundreds digit  →  XX",
                       fill=ACCENT, font=("Helvetica", 12, "bold"), anchor="w")
    canvas.create_text(rx, ry + 86,
                       text="• thousands  →  XXX, etc.",
                       fill=MUTED, font=("Helvetica", 11), anchor="w")

    canvas.create_text(rx, ry + 120,
                       text='Rule: "one X per place-shift."',
                       fill=GOOD, font=("Helvetica", 12, "bold"), anchor="w")

    draw_pill(canvas, w / 2, h - 36,
              "method unchanged — only the bottom factor may have more digits",
              bg="#eef2ff", fg=ACCENT, size=11)


# ── Slide 2 — Walk the cycled example end-to-end ────────────────────────────

def _slide_2(canvas, ex, w, h):
    top, bot, answer = ex["top"], ex["bot"], ex["answer"]
    steps = _mult_steps(top, bot)

    draw_note(canvas,
              f"Walk through {top} × {bot} — same chain, longer numbers:",
              26, color=DIM, size=11)

    # Full Intermediate layout, no special highlight. oy=66 leaves headroom
    # for the worst case (3-dig × 3-dig produces 3 partials → 6 rows below
    # the inline = oy + 6·LINE_H = oy + 156; with oy=66 the underline lands
    # at ~y=234, well above the bottom pill at h−56=284).
    _draw_intermediate_layout(canvas, cx=w / 2, oy=66, ex=ex)

    # Spell out the partial chain in one line for verification by sight.
    parts_str = "  +  ".join(
        str(s["product"]) + ("0" * s["digit_pos"]) for s in steps
    )
    draw_pill(canvas, w / 2, h - 56,
              f"answer:  {top} × {bot}  =  {answer}",
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              f"Add-column meaning:  {parts_str}  =  {answer}.",
              h - 28, color=MUTED, size=11)


# ── Slide 3 — The XX double-placeholder beat (FIXED reference 23 × 145) ─────

_XX_REF = {"top": 23, "bot": 145, "answer": 3335}


def _slide_3(canvas, ex, w, h):
    # Fixed reference so the XX beat is shown regardless of the cycled example.
    ref = _XX_REF
    top, bot, answer = ref["top"], ref["bot"], ref["answer"]
    steps = _mult_steps(top, bot)

    draw_note(canvas,
              "When the bottom has a hundreds digit — example 23 × 145:",
              26, color=DIM, size=11)

    # Render the layout, highlighting the hundreds-digit partial (the one
    # whose padded_str ends in "XX").
    _draw_intermediate_layout(canvas, cx=w / 2 - 60, oy=66, ex=ref,
                              highlight_partial=2)

    # Right side: per-row breakdown emphasising the X count.
    rx = w / 2 + 130
    ry = 70
    canvas.create_text(rx, ry, text="Row-by-row:",
                       fill=DIM, font=("Helvetica", 11, "bold"), anchor="w")

    rows = [
        (steps[0]["digit_val"], steps[0]["product"], "",   "ones",     INK),
        (steps[1]["digit_val"], steps[1]["product"], "X",  "tens",     INK),
        (steps[2]["digit_val"], steps[2]["product"], "XX", "hundreds", ACCENT),
    ]
    for i, (d, p, x_pad, place, color) in enumerate(rows):
        y = ry + 26 + i * 26
        bold = "bold" if color == ACCENT else "normal"
        canvas.create_text(rx, y,
                           text=f"{place}: {top} × {d} = {p}  →  {p}{x_pad}",
                           fill=color, font=("Helvetica", 11, bold), anchor="w")

    draw_pill(canvas, w / 2, h - 36,
              "tens partial gets ONE X; hundreds partial gets TWO Xs (XX)",
              bg="#eef2ff", fg=ACCENT, size=11)


# ── Slide 4 — Pitfalls (forgot one X / forgot both X's) ─────────────────────
#
# Fixed reference: 23 × 145 = 3335. Two canonical wrong answers, both
# X-related (per Aleks: "pitfall should emphasise forgetting adding 2
# or 3 X's"):
#
#   ✗ 1265  — forgot ONE X in the hundreds row (treated 23XX as 23X,
#             so the hundreds-partial contributed 230 instead of 2300)
#             115 + 920 + 230 = 1265
#   ✗ 1058  — forgot BOTH X's in the hundreds row (treated 23XX as 23,
#             so the hundreds-partial contributed only 23 instead of 2300)
#             115 + 920 + 23 = 1058

def _slide_4(canvas, ex, w, h):
    draw_note(canvas,
              "Two mistakes to watch for — using 23 × 145 as reference:",
              32, color=DIM, size=11)

    red    = "#dc2626"
    cy     = 140
    col_cx = [w / 2 - 220, w / 2, w / 2 + 220]

    # ── Column 1: Correct ──────────────────────────────────────────────────
    canvas.create_text(col_cx[0], cy - 78, text="Correct",
                       fill=GOOD, font=("Helvetica", 11, "bold"))
    canvas.create_text(col_cx[0], cy - 10,
                       text="23 × 145 = 3335",
                       fill=GOOD, font=("Helvetica", 18, "bold"))
    canvas.create_text(col_cx[0], cy + 20,
                       text="115  +  92X  +  23XX",
                       fill=MUTED, font=("Helvetica", 10))
    canvas.create_text(col_cx[0], cy + 34,
                       text="= 115 + 920 + 2300 = 3335",
                       fill=MUTED, font=("Helvetica", 10))

    # ── Column 2: Wrong A — forgot ONE X (1 of 2) ──────────────────────────
    canvas.create_text(col_cx[1], cy - 78, text="Wrong",
                       fill=red, font=("Helvetica", 11, "bold"))
    canvas.create_text(col_cx[1], cy - 10,
                       text="23 × 145 = 1265",
                       fill=red, font=("Helvetica", 18, "bold"))
    canvas.create_text(col_cx[1], cy + 20,
                       text="forgot ONE X on hundreds —",
                       fill=red, font=("Helvetica", 10, "italic"))
    canvas.create_text(col_cx[1], cy + 34,
                       text="wrote 23X (should be 23XX)",
                       fill=red, font=("Helvetica", 10, "italic"))

    # ── Column 3: Wrong B — forgot BOTH X's ────────────────────────────────
    canvas.create_text(col_cx[2], cy - 78, text="Wrong",
                       fill=red, font=("Helvetica", 11, "bold"))
    canvas.create_text(col_cx[2], cy - 10,
                       text="23 × 145 = 1058",
                       fill=red, font=("Helvetica", 18, "bold"))
    canvas.create_text(col_cx[2], cy + 20,
                       text="forgot BOTH X's on hundreds —",
                       fill=red, font=("Helvetica", 10, "italic"))
    canvas.create_text(col_cx[2], cy + 34,
                       text="wrote 23 (should be 23XX)",
                       fill=red, font=("Helvetica", 10, "italic"))

    canvas.create_text((col_cx[0] + col_cx[1]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))
    canvas.create_text((col_cx[1] + col_cx[2]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))

    draw_pill(canvas, w / 2, cy + 90,
              "X count = place-shift count: ones 0, tens 1, hundreds 2, "
              "thousands 3 — count the digits, count the Xs",
              bg="#fef3c7", fg=WARN, size=11)


# ── Slide list ──────────────────────────────────────────────────────────────

SLIDES = build_slides(
    [_slide_1, _slide_2, _slide_3, _slide_4],
    [
        "1 · Refresher — the X-shift, plus what's new",
        "2 · Walk the chain on this example",
        "3 · The XX double-placeholder",
        "4 · Watch the pitfalls",
    ],
    captions=[
        ("Same X-shift method as Intermediate. The only new move in "
         "Advanced is that a hundreds-digit on the bottom number adds "
         "TWO X's to that partial row (and thousands would add three)."),
        ("Run the full chain on the current example. Method is unchanged "
         "from Intermediate — just longer numbers, more carries to keep "
         "track of column by column."),
        ("Reference 23 × 145. The hundreds partial multiplies the top by "
         "the hundreds-digit and appends XX — two place-shifts left of "
         "the ones column. The tens partial still gets only one X."),
        ("Two common mistakes both hit the X count. Forgetting ONE X "
         "puts the hundreds-partial in the tens column. Forgetting BOTH "
         "puts it in the ones column. Always: X count = place-shift count."),
    ],
)
