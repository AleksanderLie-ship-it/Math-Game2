"""
tutorial_div_intermediate.py
----------------------------
Tutorial content for Division: Intermediate — short division, Norwegian
vertical layout, with whole-number quotients.

Framing
-------
Short division is just div_basic (the times-table trick) applied one digit
at a time. For each step you ask: "what number times the divisor gives
the closest product to the running partial, WITHOUT going over?" Write
that digit on the quotient line, subtract the product from the partial,
and drop down (norsk: "trekker vi ned") the next digit of the dividend.
Continue until every digit has been consumed. A final remainder of 0
means the division is exact.

Pedagogy (in order)
-------------------
1. Read the question and lay out the Norwegian vertical form.
2. The big idea — div_basic applied one digit at a time.
3. First step — estimate the first quotient digit via the times table.
4. Subtract the product, then drop down the next dividend digit.
5. Finish the chain — walk every remaining digit to the end.
6. Verify by multiplying the quotient back against the divisor.
7. Pitfalls — the two canonical wrong answers.

Examples (5, all exact — matches `div_intermediate.py` which always
generates exact quotients). Example 3 (738 ÷ 2 = 369) deliberately sits
outside the game's Type-A quotient range (11..30) as a stress-test of
the method — the `div_advanced` tutorial will build on top of this pack
by opening with a single refresher slide and then extending into
remainders-as-decimals.

Rendering
---------
The Norwegian vertical block is drawn in Courier monospace so every digit
lines up column-for-column regardless of number width. `_short_div_steps`
pre-computes each step's (partial, quotient_digit, product, remainder)
and the start/end dividend columns the step's subtraction rows should
span — that makes slide 4 (focus on one step) and slide 5 (full chain)
a matter of passing `show_through_step` / `highlight_step`.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

from .slideshow_frame import (
    CANVAS_W, CANVAS_H, INK, MUTED, DIM, FAINT, SOFT, ACCENT, GOOD, WARN,
    CARD_BG,
    draw_centered_expression, draw_note, draw_arrow, draw_pill,
    build_slides,
)


TITLE = "Division: Intermediate — short division"
LEAD  = "Same times-table trick as Beginner, applied one digit at a time."


# ── Examples ─────────────────────────────────────────────────────────────────
#
# All five are exact (remainder 0) to match div_intermediate.py's generator.
# Example 3 (738 ÷ 2) intentionally scales past the game's quotient range —
# it pre-paves the div_advanced tutorial so the pupil meets 3-digit quotients
# under the same visual vocabulary.

EXAMPLES = [
    {"dividend":  36, "divisor":  3, "quotient":  12},   # warmup, matches the
                                                          # handwritten picture
                                                          # that anchors Norwegian
                                                          # vertical style
    {"dividend": 252, "divisor":  9, "quotient":  28},   # 1-digit divisor with
                                                          # mid-chain carry
    {"dividend": 738, "divisor":  2, "quotient": 369},   # 7xx ÷ 2 — scales the
                                                          # method (advanced-ready)
    {"dividend": 156, "divisor": 13, "quotient":  12},   # first 2-digit divisor
    {"dividend": 192, "divisor": 16, "quotient":  12},   # 2-digit divisor, tighter
                                                          # first-digit estimation
]


# ── Core helper: compute the short-division steps ────────────────────────────

def _short_div_steps(dividend: int, divisor: int):
    """Return a list of step dicts describing Norwegian short division.

    Each step dict carries:
        partial        — the running partial BEFORE dividing (e.g. 25 in 252÷9)
        quotient_digit — the digit written on the quotient line
        product        — quotient_digit * divisor (the subtrahend)
        remainder      — partial - product (carries into next step)
        start_col      — leftmost dividend-column the partial/subtraction sits under
        end_col        — rightmost dividend-column (the just-brought-down digit)

    Columns are 0-indexed across the dividend string. Leading digits that
    can't accommodate the divisor (e.g. "2" in 252÷9) are absorbed into
    the first step rather than emitted as a step of their own.
    """
    dstr = str(dividend)
    steps = []
    remainder = 0
    for i, ch in enumerate(dstr):
        partial = remainder * 10 + int(ch)
        if not steps and partial < divisor:
            # Leading dividend digits still too small — absorb into the
            # first real step rather than emit a (0 × divisor) no-op.
            remainder = partial
            continue
        q = partial // divisor
        product = q * divisor
        r = partial - product
        if not steps:
            # First real step: partial spans from column 0 to i (includes any
            # absorbed leading digits).
            start_col = 0
        else:
            # Subsequent steps: the previous remainder's digits sit to the
            # left of the newly-brought-down digit at column i.
            start_col = i - len(str(remainder))
        steps.append(dict(
            partial=partial,
            quotient_digit=q,
            product=product,
            remainder=r,
            start_col=start_col,
            end_col=i,
        ))
        remainder = r
    return steps


# ── Core helper: draw the Norwegian vertical layout ──────────────────────────

# Monospace column pitch. Sized so the 3-step example (738 ÷ 2 = 369) fits
# vertically in the 340 px canvas without colliding with slide 5's bottom
# pill. Worst-case row count: dividend (1) + 2 setup rows for step 0 + 3
# rows each for steps 1 and 2 + final-remainder row = 10 rows. At
# LINE_H=22 starting from oy=68, the final remainder lands at y=266,
# leaving an 18 px gap under the pill at h − 56.
COL_W  = 15
LINE_H = 22
LAYOUT_FONT = ("Courier", 16, "bold")
BAR_COLOR   = INK


def _draw_layout(canvas, ox, oy, ex,
                 highlight_step=None, show_through_step=None,
                 show_bring_down_arrow=False):
    """Render the Norwegian short-division layout with origin at (ox, oy).

    Parameters
    ----------
    ox, oy : float            — top-left of the dividend row.
    ex     : example dict     — must carry dividend / divisor / quotient.
    highlight_step   : int    — colour this step in ACCENT (or None).
    show_through_step: int    — render only steps 0..show_through_step. None
                                 means render every step.
    show_bring_down_arrow : bool — draw a dotted arrow from the just-used
                                 dividend digit DOWN into the next partial
                                 row, emphasising the "trekker ned" move.
                                 Only meaningful when highlight_step points
                                 at a step k>=1 and we're rendering at least
                                 through that step.
    """
    dividend = ex["dividend"]
    divisor  = ex["divisor"]
    quotient = ex["quotient"]
    steps    = _short_div_steps(dividend, divisor)
    if show_through_step is None:
        show_through_step = len(steps) - 1

    dstr = str(dividend)
    n_digits = len(dstr)

    # ── Row 0: dividend : divisor = quotient  (quotient double-underlined) ──
    #
    # We want the quotient digit to sit above the dividend column it
    # corresponds to (first real quotient digit above end_col of step 0,
    # next quotient digit above end_col of step 1, …). That keeps the
    # "picture" consistent with handwritten Norwegian division.
    for i, ch in enumerate(dstr):
        canvas.create_text(ox + i * COL_W, oy,
                           text=ch, anchor="w", fill=INK, font=LAYOUT_FONT)

    # ":" and "=" are decorative separators between dividend and quotient.
    sep_x = ox + n_digits * COL_W + COL_W * 0.4
    canvas.create_text(sep_x, oy, text=":", anchor="w", fill=DIM, font=LAYOUT_FONT)
    canvas.create_text(sep_x + COL_W * 0.8, oy, text=str(divisor),
                       anchor="w", fill=INK, font=LAYOUT_FONT)
    eq_x = sep_x + COL_W * 0.8 + len(str(divisor)) * COL_W + COL_W * 0.4
    canvas.create_text(eq_x, oy, text="=", anchor="w", fill=DIM, font=LAYOUT_FONT)

    # Quotient digits: place each above its corresponding step.end_col,
    # offset by the x where the = sign sits. We still want tightly packed
    # digits for the quotient itself (so the pupil reads "12", not "1  2"),
    # so the quotient renders as a simple left-anchored string right of '='.
    q_x = eq_x + COL_W * 0.9
    qstr = str(quotient)
    canvas.create_text(q_x, oy, text=qstr, anchor="w",
                       fill=GOOD, font=LAYOUT_FONT)

    # Double underline under the quotient (Norwegian convention).
    # Probe to measure the exact width of the quotient string at this font.
    probe = canvas.create_text(0, -9999, text=qstr, anchor="w", font=LAYOUT_FONT)
    bx1, _, bx2, _ = canvas.bbox(probe)
    canvas.delete(probe)
    q_w = bx2 - bx1
    u_y = oy + 14
    canvas.create_line(q_x, u_y,     q_x + q_w, u_y,     fill=GOOD, width=2)
    canvas.create_line(q_x, u_y + 4, q_x + q_w, u_y + 4, fill=GOOD, width=2)

    # ── Per-step rows ───────────────────────────────────────────────────────
    #
    # Row cadence per step:
    #   (a) partial row         — skipped for step 0 (partial is already
    #                              visible as the leading dividend digits)
    #   (b) subtraction row     — "-product" aligned under the partial
    #   (c) bar row             — horizontal rule under the subtraction

    row = 1  # next free row (row 0 is the dividend)
    for k, step in enumerate(steps):
        if k > show_through_step:
            break
        accent = (highlight_step == k)
        color  = ACCENT if accent else INK

        if k > 0:
            # (a) partial row — show the remainder-digits + brought-down digit
            partial_str = str(step["partial"])
            # Left-pad with zeros so partial occupies end_col - start_col + 1
            # slots. This matches the handwritten convention in the 36÷3 =
            # 12 reference where the "06" carries an explicit leading 0.
            slot_count = step["end_col"] - step["start_col"] + 1
            padded = partial_str.rjust(slot_count, "0")
            for j, ch in enumerate(padded):
                col = step["start_col"] + j
                canvas.create_text(ox + col * COL_W, oy + row * LINE_H,
                                   text=ch, anchor="w",
                                   fill=color, font=LAYOUT_FONT)
            # Optional "trekker ned" dotted arrow: from the brought-down
            # dividend digit (row 0, col = end_col) to the partial row
            # (this row, col = end_col).
            if show_bring_down_arrow and highlight_step == k:
                arr_x = ox + step["end_col"] * COL_W + COL_W * 0.3
                draw_arrow(canvas,
                           arr_x, oy + 14,
                           arr_x, oy + row * LINE_H - 10,
                           color=ACCENT, width=1, dash=(3, 3))
            row += 1

        # (b) subtraction row — "-product" aligned under the partial
        prod_str = str(step["product"])
        # Minus sign sits ~0.6 columns to the left of start_col.
        minus_x = ox + (step["start_col"] - 0.6) * COL_W
        canvas.create_text(minus_x, oy + row * LINE_H,
                           text="-", anchor="w",
                           fill=color, font=LAYOUT_FONT)
        # Right-align product under end_col so a 1-digit product under a
        # 2-digit partial (e.g. 6 under "13") sits correctly.
        for j, ch in enumerate(prod_str):
            col = step["end_col"] - len(prod_str) + 1 + j
            canvas.create_text(ox + col * COL_W, oy + row * LINE_H,
                               text=ch, anchor="w",
                               fill=color, font=LAYOUT_FONT)
        row += 1

        # (c) bar row — short horizontal rule under the step's column span
        bar_y  = oy + row * LINE_H - LINE_H * 0.55
        bar_x1 = ox + (step["start_col"] - 0.6) * COL_W
        bar_x2 = ox + (step["end_col"] + 0.9) * COL_W
        canvas.create_line(bar_x1, bar_y, bar_x2, bar_y,
                           fill=BAR_COLOR, width=1)
        row += 1

    # ── Final remainder (always 0 for these examples) ───────────────────────
    if show_through_step >= len(steps) - 1:
        last = steps[-1]
        rem_col = last["end_col"]
        canvas.create_text(ox + rem_col * COL_W, oy + row * LINE_H,
                           text=str(last["remainder"]), anchor="w",
                           fill=GOOD, font=LAYOUT_FONT)


# ── Slide 1 — Read the question, set up the Norwegian layout ────────────────

def _slide_1(canvas, ex, w, h):
    dividend, divisor = ex["dividend"], ex["divisor"]

    draw_note(canvas, "The question:", 34, color=DIM, size=11)
    draw_centered_expression(canvas,
                             f"{dividend}  ÷  {divisor}  =  ?",
                             78, size=32)

    # Anchor pill naming the skeleton
    draw_pill(canvas, w / 2, 122,
              "set up the skeleton: dividend : divisor = quotient",
              bg=SOFT, fg=ACCENT, size=11)

    # Mini-skeleton of the layout, un-filled, centred in the lower half
    ox = w / 2 - (len(str(dividend)) * COL_W) / 2 - 40
    oy = 170
    # Dividend digits in faint grey, separators in dim, empty quotient slot
    dstr = str(dividend)
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
    # Dashed placeholder for the (still-unknown) quotient
    q_x = eq_x + COL_W * 0.9
    canvas.create_text(q_x, oy, text="___", anchor="w",
                       fill=FAINT, font=LAYOUT_FONT)

    draw_note(canvas,
              "Lay out the problem just like in your notebook — "
              "the double underline under the answer comes at the end.",
              h - 30, color=MUTED, size=11)


# ── Slide 2 — The big idea ──────────────────────────────────────────────────

def _slide_2(canvas, ex, w, h):
    dividend, divisor, quotient = ex["dividend"], ex["divisor"], ex["quotient"]
    steps = _short_div_steps(dividend, divisor)
    first_partial = steps[0]["partial"]

    draw_note(canvas,
              f"At every step, ask the same question. "
              f"For {dividend} ÷ {divisor} the first partial is {first_partial}:",
              40, color=DIM, size=11)

    # Big centered question template — bound to the actual first partial
    # of the cycled example so the pupil sees a concrete number, not a
    # bare placeholder.
    draw_centered_expression(canvas,
                             f'"What times {divisor} gives closest to '
                             f'{first_partial}  WITHOUT going over?"',
                             96, size=16)

    # A tiny times-table strip for the divisor (first six rows), so the
    # pupil sees the familiar anchor — same look as div_basic slide 3.
    rows = 6
    col_x = [w / 2 - 90, w / 2, w / 2 + 90]
    top_y = 150
    row_h = 22
    for i in range(1, rows + 1):
        y = top_y + (i - 1) * row_h
        canvas.create_text(col_x[0], y, text=str(i),
                           fill=DIM,  font=("Helvetica", 12), anchor="e")
        canvas.create_text(col_x[0] + 12, y, text="×",
                           fill=FAINT, font=("Helvetica", 11), anchor="w")
        canvas.create_text(col_x[1], y, text=str(divisor),
                           fill=DIM, font=("Helvetica", 12))
        canvas.create_text(col_x[1] + 14, y, text="=",
                           fill=FAINT, font=("Helvetica", 11), anchor="w")
        canvas.create_text(col_x[2], y, text=str(i * divisor),
                           fill=INK, font=("Helvetica", 12, "bold"), anchor="w")

    draw_note(canvas,
              "You already know the times tables from Beginner. "
              "Short division reuses them — one digit of the answer at a time.",
              h - 28, color=MUTED, size=11)


# ── Slide 3 — First step: estimate the first quotient digit ─────────────────

def _slide_3(canvas, ex, w, h):
    dividend, divisor = ex["dividend"], ex["divisor"]
    steps = _short_div_steps(dividend, divisor)
    step0 = steps[0]

    draw_note(canvas,
              f"First partial is {step0['partial']}. "
              f"What times {divisor} lands closest, without going over?",
              34, color=DIM, size=11)

    # Render a small times-table column on the LEFT, matching div_basic
    # slide 3 style. Highlight the row where product == step0['product'].
    rows = max(step0["quotient_digit"] + 2, 5)
    rows = min(rows, 9)
    tx0 = 110
    ty0 = 72
    row_h = 24
    for i in range(1, rows + 1):
        y = ty0 + (i - 1) * row_h
        is_match = (i == step0["quotient_digit"])
        is_over  = (i * divisor > step0["partial"])
        if is_match:
            color = GOOD
            font = ("Helvetica", 13, "bold")
        elif is_over:
            color = WARN
            font = ("Helvetica", 12)
        else:
            color = INK
            font = ("Helvetica", 12)
        canvas.create_text(tx0,        y, text=str(i),        fill=color, font=font, anchor="e")
        canvas.create_text(tx0 + 14,   y, text="×",           fill=DIM,   font=("Helvetica", 11), anchor="w")
        canvas.create_text(tx0 + 34,   y, text=str(divisor),  fill=color, font=font)
        canvas.create_text(tx0 + 52,   y, text="=",           fill=DIM,   font=("Helvetica", 11), anchor="w")
        canvas.create_text(tx0 + 74,   y, text=str(i * divisor),
                           fill=color, font=font, anchor="w")
        if is_match:
            canvas.create_text(tx0 + 130, y, text=f"≤ {step0['partial']}  ✓",
                               fill=GOOD, font=("Helvetica", 11, "bold"), anchor="w")
        elif is_over:
            canvas.create_text(tx0 + 130, y, text=f"> {step0['partial']}  ✗",
                               fill=WARN, font=("Helvetica", 11), anchor="w")

    # On the right side, render the partial layout so far, highlighting
    # the first step.
    layout_ox = w / 2 + 80
    layout_oy = 80
    _draw_layout(canvas, layout_ox, layout_oy, ex,
                 highlight_step=0, show_through_step=0)

    # Anchor pill above the layout
    draw_pill(canvas, layout_ox + 60, 58,
              f"first answer digit = {step0['quotient_digit']}",
              bg="#dcfce7", fg=GOOD, size=10)

    draw_note(canvas,
              f"Write {step0['quotient_digit']} on the answer line, "
              f"then subtract {step0['product']} from {step0['partial']} — "
              f"that leaves {step0['remainder']}.",
              h - 28, color=MUTED, size=11)


# ── Slide 4 — Subtract, then bring down ─────────────────────────────────────

def _slide_4(canvas, ex, w, h):
    dividend, divisor = ex["dividend"], ex["divisor"]
    steps = _short_div_steps(dividend, divisor)

    # If there's only one step (never happens for our examples but be safe),
    # the bring-down beat has no meaning; fall back to showing step 0 only.
    target_step = 1 if len(steps) >= 2 else 0

    draw_note(canvas,
              'After subtracting, DROP DOWN the next digit '
              '(norsk: "så trekker vi ned dette tallet").',
              34, color=DIM, size=11)

    # Full layout showing through step `target_step`, with the bring-down
    # arrow animating the move visually.
    # Centred horizontally based on rough dividend width.
    dstr = str(dividend)
    layout_w = (len(dstr) + 6) * COL_W
    ox = (w - layout_w) / 2
    oy = 80

    _draw_layout(canvas, ox, oy, ex,
                 highlight_step=target_step,
                 show_through_step=target_step,
                 show_bring_down_arrow=True)

    if target_step >= 1:
        step_k = steps[target_step]
        draw_pill(canvas, w / 2, h - 74,
                  f"bring down → new partial = {step_k['partial']}, "
                  f"which gives quotient digit {step_k['quotient_digit']}",
                  bg="#eef2ff", fg=ACCENT, size=11)

    draw_note(canvas,
              "The dotted arrow shows the dropped-down digit joining "
              "the leftover remainder to form the next partial.",
              h - 28, color=MUTED, size=11)


# ── Slide 5 — Finish the chain ──────────────────────────────────────────────

def _slide_5(canvas, ex, w, h):
    dividend, divisor, quotient = ex["dividend"], ex["divisor"], ex["quotient"]

    draw_note(canvas,
              "Repeat the two moves — estimate, subtract, drop down — "
              "until every dividend digit has been used.",
              24, color=DIM, size=11)

    # Full, completed layout, no highlight. oy chosen so the 3-step
    # example (738 ÷ 2 → 10 rows) leaves ~30 px of clearance under the
    # final remainder before the answer pill — the earlier oy=68 put the
    # '0' on top of the pill for this specific case.
    dstr = str(dividend)
    layout_w = (len(dstr) + 6) * COL_W
    ox = (w - layout_w) / 2
    oy = 52

    _draw_layout(canvas, ox, oy, ex)

    # Pill with the completed quotient
    draw_pill(canvas, w / 2, h - 56,
              f"answer: {dividend} ÷ {divisor} = {quotient}  (remainder 0)",
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              "A final 0 at the bottom means the division was exact.",
              h - 28, color=MUTED, size=11)


# ── Slide 6 — Verify by multiplying back ────────────────────────────────────

def _slide_6(canvas, ex, w, h):
    dividend, divisor, quotient = ex["dividend"], ex["divisor"], ex["quotient"]

    draw_note(canvas, "Check by multiplying back — same ritual as Beginner:",
              40, color=DIM, size=11)

    draw_centered_expression(canvas,
                             f"{quotient}  ×  {divisor}  =  ?",
                             92, size=32)

    draw_arrow(canvas, w / 2, 128, w / 2, 168, color=ACCENT, width=2)

    draw_centered_expression(canvas,
                             f"{quotient}  ×  {divisor}  =  {dividend}  ✓",
                             210, size=32, color=GOOD)

    draw_pill(canvas, w / 2, 262,
              "if the product lands back on the dividend, "
              "the quotient is correct",
              bg="#dcfce7", fg=GOOD, size=11)

    draw_note(canvas,
              "If it lands off, the step where the numbers first drift "
              "is where the bad times-table row lives.",
              h - 28, color=MUTED, size=11)


# ── Slide 7 — Pitfall ───────────────────────────────────────────────────────
#
# Fixed reference example: 252 ÷ 9 = 28. Two canonical wrong answers:
#   ✗ 2   — forgot to bring down the last digit (stopped after step 1)
#   ✗ 38  — mis-estimated the first digit (3 × 9 = 27 > 25, "went over")
# Uses a fixed example (not the cycled one) so the pitfalls stay stable.

def _slide_7(canvas, ex, w, h):
    draw_note(canvas,
              "Two mistakes to watch for — using 252 ÷ 9 as reference:",
              32, color=DIM, size=11)

    red = "#dc2626"
    cy = 140

    col_cx = [w / 2 - 220, w / 2, w / 2 + 220]

    # ── Column 1: Correct (252 ÷ 9 = 28) ────────────────────────────────────
    canvas.create_text(col_cx[0], cy - 78, text="Correct",
                       fill=GOOD, font=("Helvetica", 11, "bold"))
    canvas.create_text(col_cx[0], cy - 10,
                       text="252 ÷ 9 = 28",
                       fill=GOOD, font=("Helvetica", 18, "bold"))
    canvas.create_text(col_cx[0], cy + 20,
                       text="both digits written,",
                       fill=MUTED, font=("Helvetica", 10))
    canvas.create_text(col_cx[0], cy + 34,
                       text="remainder 0",
                       fill=MUTED, font=("Helvetica", 10))

    # ── Column 2: Wrong A — forgot to bring down ────────────────────────────
    canvas.create_text(col_cx[1], cy - 78, text="Wrong",
                       fill=red, font=("Helvetica", 11, "bold"))
    canvas.create_text(col_cx[1], cy - 10,
                       text="252 ÷ 9 = 2",
                       fill=red, font=("Helvetica", 18, "bold"))
    canvas.create_text(col_cx[1], cy + 20,
                       text="stopped at step 1 —",
                       fill=red, font=("Helvetica", 10, "italic"))
    canvas.create_text(col_cx[1], cy + 34,
                       text="forgot to drop down the 2",
                       fill=red, font=("Helvetica", 10, "italic"))

    # ── Column 3: Wrong B — mis-estimated first digit ───────────────────────
    canvas.create_text(col_cx[2], cy - 78, text="Wrong",
                       fill=red, font=("Helvetica", 11, "bold"))
    canvas.create_text(col_cx[2], cy - 10,
                       text="252 ÷ 9 = 38",
                       fill=red, font=("Helvetica", 18, "bold"))
    canvas.create_text(col_cx[2], cy + 20,
                       text="3 × 9 = 27 > 25 —",
                       fill=red, font=("Helvetica", 10, "italic"))
    canvas.create_text(col_cx[2], cy + 34,
                       text="went over on step 1",
                       fill=red, font=("Helvetica", 10, "italic"))

    # ≠ glyphs between the columns
    canvas.create_text((col_cx[0] + col_cx[1]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))
    canvas.create_text((col_cx[1] + col_cx[2]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))

    draw_pill(canvas, w / 2, cy + 90,
              "always: walk every dividend digit, and pick the largest "
              "product that doesn't go over the partial",
              bg="#fef3c7", fg=WARN, size=11)

    draw_note(canvas,
              "If a division doesn't end on 0, the remainder continues "
              "as a decimal — that's the next tutorial pack.",
              h - 26, color=MUTED, size=11)


# ── Slide list ──────────────────────────────────────────────────────────────

SLIDES = build_slides(
    [_slide_1, _slide_2, _slide_3, _slide_4, _slide_5, _slide_6, _slide_7],
    [
        "1 · Read the question",
        "2 · The big idea — one digit at a time",
        "3 · First step: estimate the first quotient digit",
        "4 · Subtract, then drop down",
        "5 · Finish the chain",
        "6 · Verify by multiplying back",
        "7 · Watch the pitfalls",
    ],
    captions=[
        ("Set up the problem in vertical form, just like in your notebook. "
         "The answer goes to the right of '=' and gets a double underline "
         "once every digit has been worked out."),
        ("At every step you ask the same question from Beginner: what number "
         "times the divisor gives a product as close as possible to the "
         "partial, WITHOUT going over? That number is the next digit of the "
         "quotient."),
        ("Find the first quotient digit by walking the divisor's times "
         "table. Pick the biggest product that still stays ≤ the partial. "
         "Write the digit on the quotient line, subtract the product, "
         "keep the remainder."),
        ("Subtract the product, then drop down the next dividend digit to "
         "join the remainder — the dotted arrow shows the move. That forms "
         "the next partial. Repeat the same estimate-subtract ritual on it."),
        ("Keep going — estimate, subtract, drop down — until every dividend "
         "digit has been used. A final 0 at the bottom means the division "
         "was exact."),
        ("Multiply the quotient by the divisor. If the product lands back on "
         "the original dividend, the answer is correct. If not, re-check "
         "the times-table row at the step where it feels off."),
        ("Two common mistakes: stopping early and not dropping down the "
         "last digit, and picking a quotient digit whose product goes OVER "
         "the partial. Both are caught by the verify step."),
    ],
)
