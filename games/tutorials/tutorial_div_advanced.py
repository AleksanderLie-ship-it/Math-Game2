"""
tutorial_div_advanced.py
------------------------
Tutorial content for Division: Advanced — Norwegian "trappa" long division
extended into terminating decimals.

Method (exactly as Aleks teaches it)
------------------------------------
Same Norwegian vertical layout as Intermediate. Two new beats stacked on
top of the short-division scaffold:

1. **Larger dividends.** Up to 4-digit dividends ÷ 2-digit divisors. The
   estimate-subtract-trekker-ned chain just runs longer; nothing
   structurally new beyond what `tutorial_div_intermediate` teaches.

2. **Decimal extension via comma + zero bring-down.** When the integer
   chain ends with a non-zero remainder, write a comma in the quotient
   and "bring down" an imaginary 0 from the dividend's right edge — the
   new partial is the leftover remainder × 10, which feeds another
   estimate-subtract step. Repeat until the remainder lands on 0
   (terminating decimals only — divisors 2, 4, 5 in the game's range).

Layout (the canonical reference for 17 ÷ 4 = 4,25):

    1 7 0 0 : 4 = 4,25
                   ════
    1 6
    ───
      1 0
      - 8
      ───
        2 0
       -2 0
        ───
          0

The dividend visually grows past the original "17" with imaginary 0s in
DIM colour; a comma sits just after the original integer dividend; the
quotient gets a comma between the integer and decimal portions.

Pedagogy (in order)
-------------------
1. Read the question and lay out the Norwegian vertical form.
2. Refresher — three Intermediate beats; preview "what's new" in Advanced.
3. Decimal extension — fixed reference 13 ÷ 2 = 6,5 demonstrating the
   comma + zero bring-down move.
4. Walk the full chain on the cycled example (integer or decimal).
5. Verify by multiplying the quotient back against the divisor.
6. Pitfalls — forgot the comma, stopped before the remainder hit 0.

Examples (5 — three exact integer cases matching the game's 75% branch
plus two terminating-decimal cases matching the 25% branch). The game
generates `divisor × quotient = dividend` for integers and uses divisors
{2, 4, 5} with `dividend % divisor != 0` for decimals; every example
here matches that contract.

Rendering
---------
Drawn in Courier monospace via the same constants as Intermediate
(COL_W, LINE_H, LAYOUT_FONT) so the two packs read as one visual family.
`_long_div` extends `_short_div_steps`'s integer pass with a decimal
phase that emits one step per imaginary 0 brought down, and returns the
extended dividend string + integer-step count so the layout can shade
the imaginary 0s in DIM and place the dividend comma cleanly.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

from .slideshow_frame import (
    INK, MUTED, DIM, FAINT, SOFT, ACCENT, GOOD, WARN,
    draw_centered_expression, draw_note, draw_pill,
    build_slides,
)
from .tutorial_div_intermediate import (
    COL_W, LINE_H, LAYOUT_FONT, BAR_COLOR,
    _short_div_steps,
    _draw_layout as _draw_intermediate_layout,
)


TITLE = "Division: Advanced — long division + decimals"
LEAD  = "Norwegian trappa method, extended past the comma."


# ── Examples ─────────────────────────────────────────────────────────────────
#
# Three exact integers (game's 75% branch: divisor [2,25] × quotient [21,99]
# = dividend) and two terminating decimals (25% branch: divisors {2, 4, 5},
# dividend not cleanly divisible). Example 1 sits slightly under the game's
# integer range as a gentler warmup before the full-range cases.

EXAMPLES = [
    {"dividend":  156, "divisor": 12, "quotient":   13,
     "is_decimal": False, "quotient_str": "13"},   # one integer warmup
    {"dividend":   13, "divisor":  2, "quotient":  6.5,
     "is_decimal": True,  "quotient_str": "6,5"},   # 1-decimal, divisor 2
    {"dividend":   17, "divisor":  4, "quotient": 4.25,
     "is_decimal": True,  "quotient_str": "4,25"},  # 2-decimal, divisor 4
    {"dividend":   23, "divisor":  5, "quotient":  4.6,
     "is_decimal": True,  "quotient_str": "4,6"},   # 1-decimal, divisor 5
    {"dividend":   27, "divisor":  4, "quotient": 6.75,
     "is_decimal": True,  "quotient_str": "6,75"},  # 2-decimal, larger
]


# ── Core helper: compute long-division steps incl. decimal extension ─────────

def _long_div(dividend: int, divisor: int, max_decimals: int = 6):
    """Return a dict describing every step of the long division.

    Returned dict carries:
        steps              — list of step dicts
        extended_dstr      — dividend string padded with one "0" per
                              decimal step (rendered in DIM)
        int_steps_count    — how many of the steps belong to the integer
                              part (the rest are decimal steps)
        has_decimal        — True iff at least one decimal step was emitted

    The integer phase is delegated to Intermediate's `_short_div_steps` so
    the two packs share the exact same column-bookkeeping. Each step dict
    inherits all of `_short_div_steps`'s fields, augmented here with:
        is_decimal         — True for steps past the comma
        decimal_pos        — for decimal steps, the 0-indexed position
                              past the comma (0 = tenths, 1 = hundredths)

    `max_decimals` guards runaway expansion if a non-terminating divisor
    sneaks in; for the curriculum's {2, 4, 5} divisors the loop exits
    early on remainder 0.
    """
    dstr = str(dividend)

    # Integer phase — reuse Intermediate verbatim, then tag the steps.
    int_steps = _short_div_steps(dividend, divisor)
    for s in int_steps:
        s["is_decimal"]  = False
        s["decimal_pos"] = None
    steps = list(int_steps)

    int_steps_count = len(steps)
    extended_dstr   = dstr
    remainder = steps[-1]["remainder"] if steps else dividend

    # Decimal phase — append imaginary 0s, keep dividing until r == 0.
    if remainder != 0:
        dec_pos = 0
        while remainder != 0 and dec_pos < max_decimals:
            i = len(dstr) + dec_pos
            extended_dstr += "0"
            partial   = remainder * 10
            q         = partial // divisor
            product   = q * divisor
            r         = partial - product
            prev_len  = len(str(remainder)) if remainder > 0 else 1
            start_col = i - prev_len
            steps.append(dict(
                partial=partial, quotient_digit=q, product=product, remainder=r,
                start_col=start_col, end_col=i,
                is_decimal=True, decimal_pos=dec_pos,
            ))
            remainder = r
            dec_pos += 1

    return dict(
        steps=steps,
        extended_dstr=extended_dstr,
        int_steps_count=int_steps_count,
        has_decimal=int_steps_count < len(steps),
    )


def _build_qstr(steps) -> str:
    """Build the quotient display string with a comma between int / dec."""
    int_q  = "".join(str(s["quotient_digit"]) for s in steps if not s["is_decimal"])
    dec_q  = "".join(str(s["quotient_digit"]) for s in steps if s["is_decimal"])
    if int_q == "":
        int_q = "0"
    return int_q + ("," + dec_q if dec_q else "")


# ── Core helper: draw the Norwegian long-division layout ─────────────────────

def _draw_layout(canvas, ox, oy, ex,
                 highlight_step=None, show_through_step=None,
                 show_bring_down_arrow=False,
                 show_comma_callout=False,
                 underline_quotient=True):
    """Render the trappa layout with origin at (ox, oy).

    Parameters mirror Intermediate's `_draw_layout`, plus:
      show_comma_callout : bool — draw a WARN-coloured arrow + label
                                   pointing at the quotient comma. Used by
                                   the decimal-beat slide.
      underline_quotient : bool — Norwegian double-underline. Off for slide 1
                                   (skeleton) and slide 2 (refresher recap).
    """
    dividend, divisor = ex["dividend"], ex["divisor"]
    div_data = _long_div(dividend, divisor)
    steps         = div_data["steps"]
    extended_dstr = div_data["extended_dstr"]
    n_int         = len(str(dividend))
    n_total       = len(extended_dstr)

    if show_through_step is None:
        show_through_step = len(steps) - 1

    qstr = _build_qstr(steps)

    # ── Row 0: dividend (extended) : divisor = quotient ─────────────────────
    for i, ch in enumerate(extended_dstr):
        is_extension = i >= n_int
        canvas.create_text(ox + i * COL_W, oy,
                           text=ch, anchor="w",
                           fill=DIM if is_extension else INK,
                           font=LAYOUT_FONT)

    # Comma between the integer dividend and the imaginary 0s. Only drawn
    # when there are actual decimal steps — keeps slide 1's skeleton honest.
    if div_data["has_decimal"]:
        comma_x = ox + n_int * COL_W - COL_W * 0.45
        canvas.create_text(comma_x, oy, text=",", anchor="w",
                           fill=DIM, font=LAYOUT_FONT)

    # Separators + divisor + quotient (right of the dividend).
    sep_x = ox + n_total * COL_W + COL_W * 0.4
    canvas.create_text(sep_x, oy, text=":", anchor="w",
                       fill=DIM, font=LAYOUT_FONT)
    canvas.create_text(sep_x + COL_W * 0.8, oy, text=str(divisor),
                       anchor="w", fill=INK, font=LAYOUT_FONT)
    eq_x = sep_x + COL_W * 0.8 + len(str(divisor)) * COL_W + COL_W * 0.4
    canvas.create_text(eq_x, oy, text="=", anchor="w",
                       fill=DIM, font=LAYOUT_FONT)
    q_x = eq_x + COL_W * 0.9
    canvas.create_text(q_x, oy, text=qstr, anchor="w",
                       fill=GOOD, font=LAYOUT_FONT)

    # Quotient width via a hidden probe (same trick as Intermediate).
    probe = canvas.create_text(0, -9999, text=qstr, anchor="w", font=LAYOUT_FONT)
    bx1, _, bx2, _ = canvas.bbox(probe)
    canvas.delete(probe)
    q_w = bx2 - bx1

    if underline_quotient:
        u_y = oy + 14
        canvas.create_line(q_x, u_y,     q_x + q_w, u_y,     fill=GOOD, width=2)
        canvas.create_line(q_x, u_y + 4, q_x + q_w, u_y + 4, fill=GOOD, width=2)

    # Comma callout: arrow from above pointing at the quotient comma.
    if show_comma_callout and div_data["has_decimal"]:
        comma_idx = qstr.index(",")
        prefix_probe = canvas.create_text(
            0, -9999, text=qstr[:comma_idx], anchor="w", font=LAYOUT_FONT,
        )
        pbx1, _, pbx2, _ = canvas.bbox(prefix_probe)
        canvas.delete(prefix_probe)
        prefix_w = pbx2 - pbx1
        comma_x_q = q_x + prefix_w
        draw_arrow(canvas,
                   comma_x_q + 4, oy - 26,
                   comma_x_q + 4, oy - 8,
                   color=WARN, width=1)
        canvas.create_text(comma_x_q + 4, oy - 32,
                           text="comma", anchor="s",
                           fill=WARN, font=("Helvetica", 10, "bold"))

    # ── Per-step rows ───────────────────────────────────────────────────────
    row = 1
    for k, step in enumerate(steps):
        if k > show_through_step:
            break
        accent = (highlight_step == k)
        color  = ACCENT if accent else INK

        if k > 0:
            # (a) partial row
            partial_str = str(step["partial"])
            slot_count  = step["end_col"] - step["start_col"] + 1
            padded      = partial_str.rjust(slot_count, "0")
            for j, ch in enumerate(padded):
                col = step["start_col"] + j
                canvas.create_text(ox + col * COL_W, oy + row * LINE_H,
                                   text=ch, anchor="w",
                                   fill=color, font=LAYOUT_FONT)
            if show_bring_down_arrow and highlight_step == k:
                arr_x = ox + step["end_col"] * COL_W + COL_W * 0.3
                draw_arrow(canvas,
                           arr_x, oy + 14,
                           arr_x, oy + row * LINE_H - 10,
                           color=ACCENT, width=1, dash=(3, 3))
            row += 1

        # (b) subtraction row
        prod_str = str(step["product"])
        minus_x  = ox + (step["start_col"] - 0.6) * COL_W
        canvas.create_text(minus_x, oy + row * LINE_H,
                           text="-", anchor="w",
                           fill=color, font=LAYOUT_FONT)
        for j, ch in enumerate(prod_str):
            col = step["end_col"] - len(prod_str) + 1 + j
            canvas.create_text(ox + col * COL_W, oy + row * LINE_H,
                               text=ch, anchor="w",
                               fill=color, font=LAYOUT_FONT)
        row += 1

        # (c) bar row
        bar_y  = oy + row * LINE_H - LINE_H * 0.55
        bar_x1 = ox + (step["start_col"] - 0.6) * COL_W
        bar_x2 = ox + (step["end_col"] + 0.9) * COL_W
        canvas.create_line(bar_x1, bar_y, bar_x2, bar_y,
                           fill=BAR_COLOR, width=1)
        row += 1

    # Final remainder under the last step.
    if show_through_step >= len(steps) - 1:
        last = steps[-1]
        canvas.create_text(ox + last["end_col"] * COL_W, oy + row * LINE_H,
                           text=str(last["remainder"]), anchor="w",
                           fill=GOOD, font=LAYOUT_FONT)


# ── Slide 1 — Read the question, set up the Norwegian layout ────────────────

def _slide_1(canvas, ex, w, h):
    dividend, divisor = ex["dividend"], ex["divisor"]
    is_decimal        = ex.get("is_decimal", False)

    draw_note(canvas, "The question:", 30, color=DIM, size=11)
    draw_centered_expression(canvas,
                             f"{dividend}  ÷  {divisor}  =  ?",
                             72, size=30)

    pill_text = ("set up just like Intermediate — this time the answer "
                 "may continue past a comma" if is_decimal else
                 "set up just like Intermediate — this time the dividend "
                 "is larger")
    draw_pill(canvas, w / 2, 116, pill_text,
              bg=SOFT, fg=ACCENT, size=11)

    # Faint mini-skeleton: dividend in FAINT, separators in DIM, quotient
    # slot dashed. No bar / no underline — the answer hasn't been derived
    # yet, so we don't draw machinery.
    dstr = str(dividend)
    ox = w / 2 - (len(dstr) * COL_W) / 2 - 36
    oy = 168
    for i, ch in enumerate(dstr):
        canvas.create_text(ox + i * COL_W, oy, text=ch, anchor="w",
                           fill=FAINT, font=LAYOUT_FONT)
    sep_x = ox + len(dstr) * COL_W + COL_W * 0.4
    canvas.create_text(sep_x, oy, text=":", anchor="w",
                       fill=DIM, font=LAYOUT_FONT)
    canvas.create_text(sep_x + COL_W * 0.8, oy, text=str(divisor),
                       anchor="w", fill=FAINT, font=LAYOUT_FONT)
    eq_x = sep_x + COL_W * 0.8 + len(str(divisor)) * COL_W + COL_W * 0.4
    canvas.create_text(eq_x, oy, text="=", anchor="w",
                       fill=DIM, font=LAYOUT_FONT)
    q_x = eq_x + COL_W * 0.9
    canvas.create_text(q_x, oy, text="___", anchor="w",
                       fill=FAINT, font=LAYOUT_FONT)
    # Bottom note intentionally omitted — the SlideshowFrame caption
    # below the canvas already says the same thing; doubling it just
    # crowds the slide.


# ── Slide 2 — Refresher: Intermediate beats + what's new ────────────────────
#
# Uses Intermediate's own `_draw_layout` to render a familiar mini-example
# (36 ÷ 3 = 12, the same anchor handwritten reference Intermediate slide 1
# uses). Reusing the helper guarantees pixel-identical visual vocabulary
# with the previous tutorial — the pupil sees the exact same picture they
# already learned, then reads the three numbered beats next to it.

_REFRESHER_REF = {"dividend": 36, "divisor": 3, "quotient": 12}


def _slide_2(canvas, ex, w, h):
    draw_note(canvas, "Refresher — Intermediate beats you already know:",
              26, color=DIM, size=11)

    items = [
        ("1.", "Estimate the next quotient digit",
         "(largest product ≤ the partial)"),
        ("2.", "Multiply and subtract",
         "(write the product, keep the remainder)"),
        ("3.", "Bring down the next dividend digit",
         "(trekker ned — joins the remainder)"),
    ]
    base_y = 64
    for i, (num, head, body) in enumerate(items):
        y = base_y + i * 50
        canvas.create_text(50, y, text=num, anchor="w",
                           fill=ACCENT, font=("Helvetica", 16, "bold"))
        canvas.create_text(76, y, text=head, anchor="w",
                           fill=INK, font=("Helvetica", 12, "bold"))
        canvas.create_text(76, y + 18, text=body, anchor="w",
                           fill=MUTED, font=("Helvetica", 10))

    # Mini Intermediate-style render on the right — same picture the pupil
    # saw in tutorial_div_intermediate, drawn by the very same helper.
    _draw_intermediate_layout(canvas,
                              ox=w / 2 + 110, oy=70,
                              ex=_REFRESHER_REF)

    draw_pill(canvas, w / 2, 226,
              "what is new in Advanced: a non-zero integer remainder — "
              "extend with a comma + a brought-down 0",
              bg="#eef2ff", fg=ACCENT, size=11)

    draw_note(canvas,
              "Everything from Intermediate still applies. Advanced adds "
              "exactly one new move on top — the next slide shows it.",
              h - 28, color=MUTED, size=11)


# ── Slide 3 — Decimal extension (FIXED reference 13 ÷ 2 = 6,5) ──────────────

_DECIMAL_REF = {"dividend": 13, "divisor": 2, "quotient": 6.5,
                "is_decimal": True, "quotient_str": "6,5"}


def _slide_3(canvas, ex, w, h):
    # Always uses the fixed reference so the decimal beat is shown
    # regardless of which example is currently cycled.
    ref = _DECIMAL_REF

    draw_note(canvas,
              "When the integer remainder isn't 0 — example 13 ÷ 2:",
              26, color=DIM, size=11)

    # Layout on the LEFT, full chain visible, decimal step in ACCENT.
    # No callout — the highlighted step + the right-side walkthrough
    # already make the comma move obvious; the earlier WARN-arrow label
    # collided with this title note.
    ox = 70
    oy = 84
    _draw_layout(canvas, ox, oy, ref,
                 highlight_step=1)

    # Right-side explanation of the new beat.
    rx = w / 2 + 60
    ry = 86
    canvas.create_text(rx, ry, text="Step 1 — integer:",
                       fill=ACCENT, font=("Helvetica", 13, "bold"), anchor="w")
    canvas.create_text(rx, ry + 22,
                       text="13 ÷ 2 = 6 with remainder 1",
                       fill=INK, font=("Helvetica", 12), anchor="w")

    canvas.create_text(rx, ry + 56, text="Step 2 — extend past the comma:",
                       fill=WARN, font=("Helvetica", 13, "bold"), anchor="w")
    canvas.create_text(rx, ry + 78,
                       text="• write a comma in the answer  →  6,",
                       fill=INK, font=("Helvetica", 12), anchor="w")
    canvas.create_text(rx, ry + 96,
                       text='• "bring down" a 0  →  new partial = 10',
                       fill=INK, font=("Helvetica", 12), anchor="w")
    canvas.create_text(rx, ry + 114,
                       text="• 10 ÷ 2 = 5, remainder 0  ✓",
                       fill=GOOD, font=("Helvetica", 12, "bold"), anchor="w")

    canvas.create_text(rx, ry + 144, text="answer:  6,5",
                       fill=GOOD, font=("Helvetica", 16, "bold"), anchor="w")

    draw_pill(canvas, w / 2, h - 36,
              "remainder ≠ 0  →  comma in the answer, bring down a 0",
              bg="#fef3c7", fg=WARN, size=11)


# ── Slide 4 — Walk the full chain on the cycled example ─────────────────────

def _slide_4(canvas, ex, w, h):
    dividend, divisor = ex["dividend"], ex["divisor"]
    is_decimal        = ex.get("is_decimal", False)
    qstr              = ex["quotient_str"]

    draw_note(canvas,
              "Walk through the chain — same example as the question:",
              26, color=DIM, size=11)

    # Centred layout. oy=44 leaves room for the worst-case 4,25 chain
    # (10 rows × LINE_H=22 = 220 px → ends at y=264, pill at h−56=284).
    div_data = _long_div(dividend, divisor)
    extended = div_data["extended_dstr"]
    layout_w = (len(extended) + 6) * COL_W
    ox = (w - layout_w) / 2
    oy = 44

    _draw_layout(canvas, ox, oy, ex)

    pill_text = (f"answer: {dividend} ÷ {divisor} = {qstr}"
                 if not is_decimal else
                 f"answer: {dividend} ÷ {divisor} = {qstr} (terminating)")
    draw_pill(canvas, w / 2, h - 56,
              pill_text, bg="#dcfce7", fg=GOOD, size=11)

    bottom_text = ("A final 0 below the last bar means the division "
                   "terminated."
                   if not is_decimal else
                   "The comma in the answer marks where the integer part "
                   "ends and the decimal part begins.")
    draw_note(canvas, bottom_text, h - 28, color=MUTED, size=11)


# ── Slide 5 — Pitfalls ──────────────────────────────────────────────────────
#
# Fixed reference: 17 ÷ 4 = 4,25. Two canonical wrong answers:
#   ✗ 425   — forgot to write the comma in the answer (kept as integer)
#   ✗ 4,2   — stopped after the first decimal step, ignored the leftover
#             remainder of 2 that demanded another bring-down

def _slide_5(canvas, ex, w, h):
    draw_note(canvas,
              "Two mistakes to watch for — using 17 ÷ 4 as reference:",
              32, color=DIM, size=11)

    red    = "#dc2626"
    cy     = 140
    col_cx = [w / 2 - 220, w / 2, w / 2 + 220]

    # ── Column 1: Correct ───────────────────────────────────────────────────
    canvas.create_text(col_cx[0], cy - 78, text="Correct",
                       fill=GOOD, font=("Helvetica", 11, "bold"))
    canvas.create_text(col_cx[0], cy - 10,
                       text="17 ÷ 4 = 4,25",
                       fill=GOOD, font=("Helvetica", 18, "bold"))
    canvas.create_text(col_cx[0], cy + 20,
                       text="comma after integer part,",
                       fill=MUTED, font=("Helvetica", 10))
    canvas.create_text(col_cx[0], cy + 34,
                       text="continued until remainder = 0",
                       fill=MUTED, font=("Helvetica", 10))

    # ── Column 2: Wrong A — forgot the comma ────────────────────────────────
    canvas.create_text(col_cx[1], cy - 78, text="Wrong",
                       fill=red, font=("Helvetica", 11, "bold"))
    canvas.create_text(col_cx[1], cy - 10,
                       text="17 ÷ 4 = 425",
                       fill=red, font=("Helvetica", 18, "bold"))
    canvas.create_text(col_cx[1], cy + 20,
                       text="forgot the comma —",
                       fill=red, font=("Helvetica", 10, "italic"))
    canvas.create_text(col_cx[1], cy + 34,
                       text="off by a factor of 100",
                       fill=red, font=("Helvetica", 10, "italic"))

    # ── Column 3: Wrong B — stopped before remainder hit 0 ──────────────────
    canvas.create_text(col_cx[2], cy - 78, text="Wrong",
                       fill=red, font=("Helvetica", 11, "bold"))
    canvas.create_text(col_cx[2], cy - 10,
                       text="17 ÷ 4 = 4,2",
                       fill=red, font=("Helvetica", 18, "bold"))
    canvas.create_text(col_cx[2], cy + 20,
                       text="stopped at one decimal —",
                       fill=red, font=("Helvetica", 10, "italic"))
    canvas.create_text(col_cx[2], cy + 34,
                       text="leftover remainder of 2 ignored",
                       fill=red, font=("Helvetica", 10, "italic"))

    # ≠ glyphs between columns
    canvas.create_text((col_cx[0] + col_cx[1]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))
    canvas.create_text((col_cx[1] + col_cx[2]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))

    draw_pill(canvas, w / 2, cy + 90,
              "always: comma between the integer and decimal parts, "
              "and keep going until the remainder is 0",
              bg="#fef3c7", fg=WARN, size=11)

    draw_note(canvas,
              "Every example in Advanced terminates — the curriculum picks "
              "divisors {2, 4, 5} so the decimal always ends.",
              h - 26, color=MUTED, size=11)


# ── Slide list ──────────────────────────────────────────────────────────────

SLIDES = build_slides(
    [_slide_1, _slide_2, _slide_3, _slide_4, _slide_5],
    [
        "1 · Read the question",
        "2 · Refresher — Intermediate beats + what's new",
        "3 · Decimal extension — comma + bring down a 0",
        "4 · Walk the full chain",
        "5 · Watch the pitfalls",
    ],
    captions=[
        ("Same Norwegian vertical setup as Intermediate. What is new in "
         "Advanced: dividends are larger, and answers may continue past "
         "a comma when the integer remainder isn't 0."),
        ("Three Intermediate beats — estimate, multiply-and-subtract, "
         "bring down the next digit. Advanced reuses all three; the only "
         "new beat is the comma + zero bring-down on slide 3."),
        ("When the integer chain ends with a non-zero remainder, write a "
         "comma in the answer and bring down an imaginary 0. The new "
         "partial is the leftover × 10 — keep dividing as before."),
        ("Run the full chain on the current example. Integer cases finish "
         "with remainder 0 directly; decimal cases extend past the comma "
         "until the remainder lands on 0."),
        ("Two common mistakes: forgetting to write the comma (off by 100×), "
         "and stopping before the remainder reaches 0 (incomplete decimal). "
         "Always one comma, always continue until remainder = 0."),
    ],
)
