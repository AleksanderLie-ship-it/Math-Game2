"""
tutorial_mult_intermediate.py
-----------------------------
Tutorial content for Multiplication: Intermediate — multi-digit vertical
multiplication via partial products with the Norwegian "X-shift"
placeholder marking the tens-column zero.

Method (exactly as Aleks teaches it)
------------------------------------
Write the two factors INLINE on a single row — `TOP × BOT` — with no
separate stacked "× BOT" row beneath the top. Build one partial product
per digit of the right (bottom) number directly underneath the LEFT
factor, right-aligned to the LEFT factor's ones-digit. Each partial is
shifted one column further left than the previous (handled by
right-aligning a longer padded string). The shift is made VISIBLE by
writing an "X" in the now-empty ones column (and an "XX" for a hundreds
digit, etc.). This makes the invisible place-value zero concrete for
the pupil — they see the X rather than have to remember to leave a
blank. Sum the partials under a single horizontal rule and
double-underline the answer.

Layout (the canonical reference picture):

    234 × 21          ← row 0: inline expression
      234             ← partial 0 (top × 1)
    +468X             ← partial 1 (top × 2, with X-shift)
    ────
     4914             ← answer (double-underlined)

For a digit d in the bottom number:
    partial = top × d                (just times-table)
    write partial right-aligned, then append k "X"s where k is the
    digit's position (ones=0 Xs, tens=1 X, hundreds=2 Xs, …).

Narration (mirrors div_intermediate's "What times X gives closest to Y")
----------------------------------------------------------------------
"Multiply the ones first, write the last digit, remember the rest as
a carry." — the core arithmetic move inside each partial row.
"Mark the shift with an X — it holds the place of the hidden zero."
— the novel concept of this pack.

Pedagogy (in order)
-------------------
1. Read the question and lay out the inline form with skeleton rows.
2. The big idea — each digit of the bottom multiplies the WHOLE top.
3. First partial row — multiply top × ones-digit, with carries.
4. Second partial row — multiply top × tens-digit, plus the X shift.
5. Add the partials — the chain is done.
6. Pitfalls — forgot the X, and carry error in the ones row.

Examples (5 — four 2-digit × 2-digit plus one 3-digit × 2-digit
stress test mirroring the handwritten reference picture). The
game's `mult_intermediate.py` generates 2-dig × 1-dig, 1-dig × 2-dig,
and 2-dig × 2-dig randomly — 2×2 is the method-showcase case, so the
pack prioritises it. The 234 × 21 example sits beyond the game's
range (mult_intermediate maxes at 99 × 99) so `mult_advanced` can
open with a single refresher slide and extend into 3-digit × 2-digit
territory without re-teaching the scaffold.

Rendering
---------
Drawn in Courier monospace so every column (thousands, hundreds, tens,
ones …) stays aligned across the inline expression, the partial rows,
and the sum. The TOP factor's ones-digit defines `col_anchor_x`; all
partials and the answer right-align to it, while the BOT factor sits
inline to the right of the "×" glyph. `_mult_steps` pre-computes each
partial's (digit_val, digit_pos, product, padded_str, carries) so a
slide can focus on a single partial via `highlight_partial` /
`show_through_partial`. Arc arrows (slides 2 and 4) arch ABOVE the
inline expression, anchored on the relevant BOT digit and landing on
each TOP digit, expressing "this digit hits every digit over there".
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

from .slideshow_frame import (
    CANVAS_W, CANVAS_H, INK, MUTED, DIM, FAINT, SOFT, ACCENT, GOOD, WARN,
    CARD_BG,
    draw_centered_expression, draw_note, draw_pill,
    build_slides,
)


TITLE = "Multiplication: Intermediate — partial products"
LEAD  = "Multi-digit multiplication using the X-shift placeholder."


# ── Examples ─────────────────────────────────────────────────────────────────
#
# Four 2-dig × 2-dig anchor cases + one 3-dig × 2-dig stress test. All
# answers are whole numbers (multiplication always is, unlike short
# division where the exactness constraint mattered).
#
# Size progression: 12×14 (small, light carries) → 23×15 (both rows
# carry) → 48×27 (heavier carries) → 17×36 (reversed-size, same method)
# → 234×21 (3×2 stress test, matches the handwritten reference).

EXAMPLES = [
    {"top":  12, "bot": 14, "answer":  168},   # warm-up, clean 2×2
    {"top":  23, "bot": 15, "answer":  345},   # carries in both partials
    {"top":  48, "bot": 27, "answer": 1296},   # heavier arithmetic
    {"top":  17, "bot": 36, "answer":  612},   # top < bot — method unaffected
    {"top": 234, "bot": 21, "answer": 4914},   # 3×2 stress test
                                                # (advanced-ready,
                                                # matches ref picture)
]


# ── Core helper: compute the partial-product steps ───────────────────────────

def _mult_steps(top: int, bot: int):
    """Return a list of partial-product dicts, ordered ones → tens → ….

    Each dict carries:
        digit_val     — the digit of `bot` driving this partial
        digit_pos     — 0 for ones, 1 for tens, 2 for hundreds, …
        product       — top * digit_val (the raw times-table result)
        padded_str    — product as a string with `digit_pos` X-chars
                        appended (e.g. "468" with pos=1 → "468X")
        carries       — per-column carries produced while computing
                        product, listed right-to-left; not currently
                        rendered on the canvas but kept for the harness
                        and future carry-digit overlay.
    """
    bstr = str(bot)
    n = len(bstr)
    steps = []
    for pos, ch in enumerate(reversed(bstr)):
        d = int(ch)
        product = top * d
        # Carry trace (right-to-left) — recompute top×d as a schoolbook
        # move to capture each column's carry. Optional diagnostic; keep
        # it even though the current slides don't render carry digits
        # above the top row.
        carries = []
        tstr = str(top)
        carry = 0
        for tch in reversed(tstr):
            prod = int(tch) * d + carry
            carries.append(carry)
            carry = prod // 10
        padded = str(product) + ("X" * pos)
        steps.append(dict(
            digit_val=d,
            digit_pos=pos,
            product=product,
            padded_str=padded,
            carries=carries,
        ))
    return steps


# ── Core helper: draw the inline-expression vertical layout ──────────────────
#
# This matches Aleks's handwritten reference exactly:
#
#     234 × 21          ← row 0: inline expression (TOP, ×, BOT)
#       234             ← partial 0 (top × ones-digit of bot)
#     +468X             ← partial 1 (top × tens-digit, with X-shift)
#     ────
#      4914             ← answer
#
# There is NO stacked "× bot" row. The bottom factor lives only in the
# inline expression. Partial rows and the answer right-align to the
# TOP number's ones-digit (the col_anchor_x), so they sit DIRECTLY
# beneath the top — not the whole inline expression. Only one bar (the
# sum bar above the answer); the screenshot has none above the partials.
#
# Column indexing: column 0 is the rightmost slot of the partial/answer
# block (the TOP's ones-digit position). Render right-to-left from
# col_anchor_x with a fixed monospace COL_W.

COL_W  = 18
LINE_H = 26
LAYOUT_FONT = ("Courier", 16, "bold")
BAR_COLOR   = INK


def _draw_row_string(canvas, text, right_x, y, *, fill=INK, font=LAYOUT_FONT):
    """Draw `text` right-anchored so its last char sits at `right_x`."""
    # Render char-by-char so every slot lines up on the monospace grid.
    for j, ch in enumerate(reversed(text)):
        canvas.create_text(right_x - j * COL_W, y,
                           text=ch, anchor="e", fill=fill, font=font)


def _inline_anchors(cx, ex):
    """Return (col_anchor_x, bot_lsb_x) for an example centred on cx.

    col_anchor_x is the x-position of the TOP number's ones-digit, which
    is also the right-edge column for partials and the answer.
    bot_lsb_x is the x-position of the BOT number's ones-digit (rightmost
    char of the inline expression).

    The inline expression is "TOP × BOT" laid out as
    `len(TOP) + 3 + len(BOT)` monospace columns (gap, ×, gap between the
    two factors), centred on cx.
    """
    tstr = str(ex["top"])
    bstr = str(ex["bot"])
    inline_n_cols = len(tstr) + 3 + len(bstr)
    inline_left   = cx - (inline_n_cols - 1) * COL_W / 2
    col_anchor_x  = inline_left + (len(tstr) - 1) * COL_W
    bot_lsb_x     = col_anchor_x + (len(bstr) + 2) * COL_W
    return col_anchor_x, bot_lsb_x


def _draw_layout(canvas, cx, oy, ex,
                 highlight_partial=None, show_through_partial=None,
                 show_arc_arrows=False, underline_answer=True,
                 show_sum=None, show_inline=True, inline_color=None,
                 skeleton=False):
    """Render the inline-expression multiplication block.

    Parameters
    ----------
    cx                   : centre x of the inline expression
    oy                   : y of row 0 (the inline TOP × BOT)
    ex                   : example dict (top/bot/answer)
    highlight_partial    : int  — which partial (0=ones, 1=tens, …) to
                                   render in ACCENT; None = plain
    show_through_partial : int  — render only partials 0..k. None = all.
                                   Pass -1 to render no partial rows
                                   (slide 1 skeleton, slide 2 big-idea).
    show_arc_arrows      : bool — draw dashed arcs ABOVE the inline that
                                   start above the highlighted bot-digit
                                   and arch over to land above each
                                   top-digit, showing "every bot-digit
                                   multiplies the whole top"
    underline_answer     : bool — Norwegian double-underline under the sum
    show_sum             : bool or None — explicit control of the sum
                                   bar + answer reveal. None (default)
                                   means "show iff every partial rendered".
                                   Slide 4 passes False to render through
                                   the last partial without the sum.
    show_inline          : bool — render row 0 (TOP × BOT). Default True.
                                   Slide 1 / slide 2 always want it; later
                                   slides want it as the persistent header.
    inline_color         : Tk color or None — override the inline fill
                                   (e.g. FAINT for a skeleton preview).
    skeleton             : bool — render dotted placeholders for the
                                   partial rows instead of real digits.
                                   Used by slide 1.
    """
    top, bot, answer = ex["top"], ex["bot"], ex["answer"]
    steps = _mult_steps(top, bot)
    if show_through_partial is None:
        show_through_partial = len(steps) - 1

    tstr = str(top)
    bstr = str(bot)
    astr = str(answer)

    col_anchor_x, bot_lsb_x = _inline_anchors(cx, ex)

    # ── Row 0: inline TOP × BOT ────────────────────────────────────────────
    if show_inline:
        ic = inline_color if inline_color is not None else INK
        # × glyph sits 2 columns right of TOP_LSB (gap, ×, gap, then BOT).
        times_color = DIM if ic is INK else ic
        for j, ch in enumerate(reversed(tstr)):
            canvas.create_text(col_anchor_x - j * COL_W, oy,
                               text=ch, anchor="e", fill=ic,
                               font=LAYOUT_FONT)
        canvas.create_text(col_anchor_x + 2 * COL_W, oy,
                           text="×", anchor="e",
                           fill=times_color, font=LAYOUT_FONT)
        for j, ch in enumerate(reversed(bstr)):
            canvas.create_text(bot_lsb_x - j * COL_W, oy,
                               text=ch, anchor="e", fill=ic,
                               font=LAYOUT_FONT)

    # ── Partial rows (start one row below the inline) ──────────────────────
    widest_padded = max(len(s["padded_str"]) for s in steps)
    if skeleton:
        # Dotted placeholders, one row per partial.
        for k in range(len(steps)):
            row_y = oy + (1 + k) * LINE_H
            for j in range(widest_padded):
                canvas.create_text(col_anchor_x - j * COL_W, row_y,
                                   text="·", anchor="e", fill=FAINT,
                                   font=LAYOUT_FONT)
    else:
        for k, step in enumerate(steps):
            if k > show_through_partial:
                break
            row_y  = oy + (1 + k) * LINE_H
            color  = ACCENT if highlight_partial == k else INK
            padded = step["padded_str"]
            # X chars always render in DIM so the placeholder reads as
            # "not a normal digit", regardless of highlight.
            for j, ch in enumerate(reversed(padded)):
                ch_fill = DIM if ch == "X" else color
                canvas.create_text(col_anchor_x - j * COL_W, row_y,
                                   text=ch, anchor="e", fill=ch_fill,
                                   font=LAYOUT_FONT)
            # "+" sits one column left of the partial's MSB. Render it on
            # every partial after the first — the first partial is just
            # the product, no leading "+" needed.
            if k >= 1:
                plus_x = col_anchor_x - len(padded) * COL_W
                canvas.create_text(plus_x, row_y, text="+", anchor="e",
                                   fill=color, font=LAYOUT_FONT)

    # ── Arc arrows ─────────────────────────────────────────────────────────
    # Source: just above each bot-digit at the highlighted partial's pos.
    # Destination: just above each top-digit. The control point lifts well
    # above the inline so the curve reads as a clear arch landing on each
    # top-digit. Because BOT is always to the right of TOP in the inline
    # expression, src_x and dst_x are always horizontally separated — no
    # vertical-stub bug to guard against here.
    if show_arc_arrows and highlight_partial is not None \
            and 0 <= highlight_partial < len(steps):
        step  = steps[highlight_partial]
        pos   = step["digit_pos"]
        src_x = bot_lsb_x - pos * COL_W
        # src/dst anchored close to the digit baselines so the tails read as
        # "lifting off" the bot-digit and landing on the top-digit, not as
        # floating in space above the inline.
        src_y = oy - 4
        for tj, _tch in enumerate(reversed(tstr)):
            dst_x   = col_anchor_x - tj * COL_W
            dst_y   = oy - 4
            cx_ctrl = (src_x + dst_x) / 2
            # Lift scales with horizontal distance so wider arcs go
            # higher — keeps the curvature roughly constant visually.
            cy_ctrl = oy - 30 - 0.18 * abs(src_x - dst_x)
            canvas.create_line(src_x, src_y,
                               cx_ctrl, cy_ctrl,
                               dst_x, dst_y,
                               smooth=True, fill=ACCENT,
                               width=1, dash=(3, 3),
                               arrow="last",
                               arrowshape=(8, 10, 4))

    # ── Sum bar + answer ───────────────────────────────────────────────────
    if show_sum is None:
        reveal_sum = (not skeleton) and show_through_partial >= len(steps) - 1
    else:
        reveal_sum = bool(show_sum)
    if reveal_sum:
        sum_row = 1 + len(steps)
        bar_y   = oy + sum_row * LINE_H - LINE_H * 0.55
        # Bar spans from just left of the widest partial's "+" to just
        # right of the ones-column.
        bar_x1  = col_anchor_x - widest_padded * COL_W - COL_W * 0.6
        bar_x2  = col_anchor_x + COL_W * 0.5
        canvas.create_line(bar_x1, bar_y, bar_x2, bar_y,
                           fill=BAR_COLOR, width=1)

        sum_y = oy + sum_row * LINE_H
        for j, ch in enumerate(reversed(astr)):
            canvas.create_text(col_anchor_x - j * COL_W, sum_y,
                               text=ch, anchor="e", fill=GOOD,
                               font=LAYOUT_FONT)

        if underline_answer:
            u_x1 = col_anchor_x - (len(astr) - 1) * COL_W - COL_W * 0.5
            u_x2 = col_anchor_x + COL_W * 0.4
            u_y  = sum_y + 12
            canvas.create_line(u_x1, u_y,     u_x2, u_y,     fill=GOOD, width=2)
            canvas.create_line(u_x1, u_y + 4, u_x2, u_y + 4, fill=GOOD, width=2)


# ── Slide 1 — Read the question, set up the layout ──────────────────────────

def _slide_1(canvas, ex, w, h):
    top, bot = ex["top"], ex["bot"]

    draw_note(canvas, "The question:", 30, color=DIM, size=11)
    draw_centered_expression(canvas,
                             f"{top}  ×  {bot}  =  ?",
                             72, size=30)

    draw_pill(canvas, w / 2, 116,
              "one partial row per right-number digit, right-aligned "
              "beneath the LEFT factor",
              bg=SOFT, fg=ACCENT, size=11)

    # Skeleton preview — inline TOP × BOT in INK at oy=160, with dotted
    # placeholder rows for the partials beneath, right-aligned to the TOP's
    # ones-digit. No bar or answer here — those reveal during slides 4–5.
    _draw_layout(canvas, w / 2, 160, ex,
                 show_through_partial=-1,
                 skeleton=True,
                 underline_answer=False)

    draw_note(canvas,
              'Each digit of the right number multiplies the WHOLE left '
              'number. Mark each shift with "X".',
              h - 28, color=MUTED, size=11)


# ── Slide 2 — The big idea ──────────────────────────────────────────────────

def _slide_2(canvas, ex, w, h):
    top, bot = ex["top"], ex["bot"]
    steps = _mult_steps(top, bot)

    draw_note(canvas,
              "The big idea — every digit of the right number multiplies "
              "the WHOLE left number:",
              22, color=DIM, size=11)

    # Inline expression with arcs arching ABOVE it, from each bot-digit
    # to every top-digit. The arcs realise the "each right-digit reaches
    # all left-digits" move — slides 3–4 then materialise the partials.
    # oy=120 leaves ~70 px above the inline for the arc arch (the widest
    # arc in 234 × 21 lifts to oy − 48 ≈ y=72, clear of the title note).
    _draw_layout(canvas, w / 2, 120, ex,
                 highlight_partial=0,
                 show_through_partial=-1,   # no partial rows yet
                 show_arc_arrows=True,
                 underline_answer=False)

    # Show the SECOND-digit arcs too if there is one — render a second
    # _draw_layout pass with no inline (so we don't double-stamp the
    # text) and only the arcs for partial 1. This way slide 2 visualises
    # both the ones-digit AND the tens-digit reaching the whole top.
    if len(steps) >= 2:
        _draw_layout(canvas, w / 2, 120, ex,
                     highlight_partial=1,
                     show_through_partial=-1,
                     show_arc_arrows=True,
                     show_inline=False,
                     underline_answer=False)

    # Inline gloss of the full beat chain
    draw_pill(canvas, w / 2, 200,
              f"ones × top = {steps[0]['product']}"
              + (f"   ·   tens × top = {steps[1]['product']}"
                 if len(steps) >= 2 else "")
              + ("   ·   X marks the shift" if len(steps) >= 2 else ""),
              bg="#eef2ff", fg=ACCENT, size=11)

    draw_note(canvas,
              'For each digit of the right number, multiply the whole left, '
              'then shift the answer one column left — write "X" to mark the '
              'empty slot.',
              h - 28, color=MUTED, size=11)


# ── Slide 3 — First partial: ones × top (with carry) ────────────────────────

def _slide_3(canvas, ex, w, h):
    top, bot = ex["top"], ex["bot"]
    steps = _mult_steps(top, bot)
    step0 = steps[0]

    draw_note(canvas,
              f"First partial — multiply the ones digit ({step0['digit_val']}) "
              f"by the whole top number ({top}):",
              30, color=DIM, size=11)

    # Column-by-column arithmetic on the LEFT, centred layout on the RIGHT.
    # Left column: show top × digit_val as a compressed "ones-first, carry"
    # trace, one sentence per column.
    lx = 120
    ly = 80
    tstr = str(top)
    carry = 0
    canvas.create_text(lx, ly, text=f"{top} × {step0['digit_val']} :",
                       fill=INK, font=("Helvetica", 13, "bold"),
                       anchor="w")
    for i, tch in enumerate(reversed(tstr)):
        y = ly + 26 + i * 22
        d = int(tch)
        raw = d * step0["digit_val"] + carry
        write = raw % 10
        new_carry = raw // 10
        place = ["ones", "tens", "hundreds"][i] if i < 3 else f"10^{i}"
        if carry:
            line = (f"{place}: {d}×{step0['digit_val']} + {carry} = {raw} "
                    f"— write {write}"
                    + (f", carry {new_carry}" if new_carry else ""))
        else:
            line = (f"{place}: {d}×{step0['digit_val']} = {raw} "
                    f"— write {write}"
                    + (f", carry {new_carry}" if new_carry else ""))
        canvas.create_text(lx, y, text=line,
                           fill=INK, font=("Helvetica", 11), anchor="w")
        carry = new_carry
    if carry:
        y = ly + 26 + len(tstr) * 22
        canvas.create_text(lx, y,
                           text=f"last carry {carry} — write it as the next digit",
                           fill=GOOD, font=("Helvetica", 11, "italic"),
                           anchor="w")

    # Right: live layout through partial 0. Inline at oy=72, partial 0
    # at oy+LINE_H=98. Pill goes below partial 0 (no overlap with inline).
    _draw_layout(canvas, w / 2 + 170, 72, ex,
                 highlight_partial=0,
                 show_through_partial=0,
                 underline_answer=False)

    draw_pill(canvas, w / 2 + 170, 138,
              f"first partial = {step0['product']}",
              bg="#dcfce7", fg=GOOD, size=10)

    draw_note(canvas,
              'Rule of thumb: "multiply the ones first, write the last digit, '
              'remember the rest as a carry."',
              h - 28, color=MUTED, size=11)


# ── Slide 4 — Second partial: tens × top, with X shift ──────────────────────

def _slide_4(canvas, ex, w, h):
    top, bot = ex["top"], ex["bot"]
    steps = _mult_steps(top, bot)
    # Target the first non-ones partial; for 1-digit multipliers fall back
    # to partial 0 (but the X-shift beat is trivially empty).
    target = 1 if len(steps) >= 2 else 0
    step_k = steps[target]

    draw_note(canvas,
              f"Second partial — multiply the tens digit "
              f"({step_k['digit_val']}) by {top}, then mark the shift with X:",
              22, color=DIM, size=11)

    # Live layout through the target partial, highlighted, with arc
    # arrows from the tens-digit only. show_sum=False suppresses the
    # sum bar + answer that the auto-derivation would otherwise emit
    # (target=1 with len(steps)=2 trips the "every partial rendered"
    # check). oy=120 leaves arch clearance above the inline.
    _draw_layout(canvas, w / 2, 120, ex,
                 highlight_partial=target,
                 show_through_partial=target,
                 show_arc_arrows=True,
                 underline_answer=False,
                 show_sum=False)

    # Pill explaining the X — sits below the rendered partials.
    draw_pill(canvas, w / 2, 220,
              f"{top} × {step_k['digit_val']} = {step_k['product']}, "
              f'then append "X" — the X holds the ones slot open.',
              bg="#eef2ff", fg=ACCENT, size=11)

    draw_note(canvas,
              'The X is NOT a new digit — it is a placeholder for the zero '
              'the tens-digit brings with it. Think "tens count ten times".',
              h - 28, color=MUTED, size=11)


# ── Slide 5 — Add the partials ──────────────────────────────────────────────

def _slide_5(canvas, ex, w, h):
    top, bot, answer = ex["top"], ex["bot"], ex["answer"]
    steps = _mult_steps(top, bot)

    draw_note(canvas,
              "Add the partial rows column by column — "
              "the X counts as a zero when adding.",
              24, color=DIM, size=11)

    # Full, completed layout. With the inline form one row is saved
    # vs. the old stacked layout, so oy=80 still leaves headroom for a
    # 3-partial mult_advanced reuse (inline + 3 partials + bar + sum +
    # underline ≈ 7 × LINE_H = 182 px below oy).
    _draw_layout(canvas, w / 2, 80, ex)

    # Answer pill
    draw_pill(canvas, w / 2, h - 56,
              f"answer: {top} × {bot} = {answer}",
              bg="#dcfce7", fg=GOOD, size=11)

    parts_str = " + ".join(str(s["product"]) + ("0" * s["digit_pos"])
                           for s in steps)
    draw_note(canvas,
              f"Add-column meaning: {parts_str} = {answer}.",
              h - 28, color=MUTED, size=11)


# ── Slide 6 — Pitfalls ──────────────────────────────────────────────────────
#
# Fixed reference: 23 × 15 = 345. Two canonical wrong answers:
#   ✗ 138  — forgot the X shift (115 + 23 without the shift)
#   ✗ 335  — carry error in the ones row (105 + 230 instead of 115 + 230)

def _slide_6(canvas, ex, w, h):
    draw_note(canvas,
              "Two mistakes to watch for — using 23 × 15 as reference:",
              32, color=DIM, size=11)

    red = "#dc2626"
    cy = 140
    col_cx = [w / 2 - 220, w / 2, w / 2 + 220]

    # ── Column 1: Correct ───────────────────────────────────────────────────
    canvas.create_text(col_cx[0], cy - 78, text="Correct",
                       fill=GOOD, font=("Helvetica", 11, "bold"))
    canvas.create_text(col_cx[0], cy - 10,
                       text="23 × 15 = 345",
                       fill=GOOD, font=("Helvetica", 18, "bold"))
    canvas.create_text(col_cx[0], cy + 20,
                       text="115 + 23X = 115 + 230",
                       fill=MUTED, font=("Helvetica", 10))
    canvas.create_text(col_cx[0], cy + 34,
                       text="= 345",
                       fill=MUTED, font=("Helvetica", 10))

    # ── Column 2: Wrong A — forgot the X shift ──────────────────────────────
    canvas.create_text(col_cx[1], cy - 78, text="Wrong",
                       fill=red, font=("Helvetica", 11, "bold"))
    canvas.create_text(col_cx[1], cy - 10,
                       text="23 × 15 = 138",
                       fill=red, font=("Helvetica", 18, "bold"))
    canvas.create_text(col_cx[1], cy + 20,
                       text="forgot the X —",
                       fill=red, font=("Helvetica", 10, "italic"))
    canvas.create_text(col_cx[1], cy + 34,
                       text="added 115 + 23 (no shift)",
                       fill=red, font=("Helvetica", 10, "italic"))

    # ── Column 3: Wrong B — carry error in the ones row ─────────────────────
    canvas.create_text(col_cx[2], cy - 78, text="Wrong",
                       fill=red, font=("Helvetica", 11, "bold"))
    canvas.create_text(col_cx[2], cy - 10,
                       text="23 × 15 = 335",
                       fill=red, font=("Helvetica", 18, "bold"))
    canvas.create_text(col_cx[2], cy + 20,
                       text="dropped the carry —",
                       fill=red, font=("Helvetica", 10, "italic"))
    canvas.create_text(col_cx[2], cy + 34,
                       text="wrote 105 instead of 115",
                       fill=red, font=("Helvetica", 10, "italic"))

    # ≠ glyphs between columns
    canvas.create_text((col_cx[0] + col_cx[1]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))
    canvas.create_text((col_cx[1] + col_cx[2]) / 2, cy, text="≠",
                       fill=MUTED, font=("Helvetica", 28, "bold"))

    draw_pill(canvas, w / 2, cy + 90,
              "always: one X per place-shift, and carry every time the "
              "column product is ten or more",
              bg="#fef3c7", fg=WARN, size=11)

    draw_note(canvas,
              "For a 3-digit bottom (e.g. 234 × 321), the hundreds-partial "
              'gets "XX" — two X placeholders. That is the mult_advanced pack.',
              h - 26, color=MUTED, size=11)


# ── Slide list ──────────────────────────────────────────────────────────────

SLIDES = build_slides(
    [_slide_1, _slide_2, _slide_3, _slide_4, _slide_5, _slide_6],
    [
        "1 · Read the question",
        "2 · The big idea — each bottom-digit hits the whole top",
        "3 · First partial: ones × top (with carry)",
        "4 · Second partial: tens × top, then mark the X shift",
        "5 · Add the partials",
        "6 · Watch the pitfalls",
    ],
    captions=[
        ("Set up the inline expression TOP × BOT, then build one partial-"
         "product row per digit of the bottom — right-aligned beneath the "
         "TOP factor."),
        ("Every digit of the bottom number multiplies the WHOLE top number "
         "— not just the digit above it. The partial row for the tens digit "
         "gets one 'X' at the right to mark the shift."),
        ("Multiply the top by the ones digit, column by column starting "
         "from the right. If a column product is ten or more, write the "
         "last digit and carry the rest into the next column."),
        ("Multiply the top by the tens digit the same way — but append an "
         "'X' to the right. The X is a placeholder for the zero the tens-"
         "digit brings (tens count ten times)."),
        ("Add the partial rows column by column to get the answer. The X "
         "counts as 0 while adding. Double-underline the sum — that is "
         "your answer."),
        ("Two common mistakes: forgetting to write the X (so the tens "
         "partial is added without its shift), and dropping a carry in "
         "the ones row. Always one X per place-shift."),
    ],
)
