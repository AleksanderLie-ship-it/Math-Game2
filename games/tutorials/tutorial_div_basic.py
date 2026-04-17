"""
tutorial_div_basic.py
---------------------
Tutorial content for Division: Beginner.

Framing: division is the reverse of multiplication. Rather than teaching a
fresh procedure, this tutorial maps every division question back to a
multiplication question the learner already knows from the times tables.

Slide plan
----------
1. The big idea       — "Division undoes multiplication."
2. Flip the question  — rewrite a÷b as "what × b = a?"
3. Use the times table — find the missing factor.
4. Verify             — multiply back to check.

Examples are curated: one clean (12 ÷ 3) and one slightly bigger (20 ÷ 4).
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

from .slideshow_frame import (
    CANVAS_W, CANVAS_H, INK, MUTED, DIM, SOFT, ACCENT, GOOD, WARN,
    draw_centered_expression, draw_note, draw_arrow, draw_pill,
)


TITLE = "Division: Beginner — how it works"
LEAD  = "Division is just multiplication in reverse. Here's how to use that."


EXAMPLES = [
    # (a, b, answer)   —   a ÷ b = answer,  answer * b = a
    {"a": 12, "b": 3, "ans": 4},
    {"a": 20, "b": 4, "ans": 5},
    {"a": 18, "b": 6, "ans": 3},
]


# ── Slide 1 — The big idea ───────────────────────────────────────────────────

def _slide_1(canvas, ex, w, h):
    a, b, ans = ex["a"], ex["b"], ex["ans"]

    # Top row: a × b = (a*b)    (but we show b * ans = a — the mult the pupil knows)
    draw_note(canvas, "You already know:", 40, color=DIM, size=11)
    draw_centered_expression(canvas, f"{ans}  ×  {b}  =  {a}", 90, size=34)

    # Middle: separator line
    canvas.create_line(w / 2 - 180, 140, w / 2 + 180, 140,
                       fill=DIM, width=1, dash=(3, 3))
    draw_note(canvas, "So the reverse is also true:", 160, color=DIM, size=11)

    # Bottom row: a ÷ b = ans
    draw_centered_expression(canvas, f"{a}  ÷  {b}  =  {ans}", 210, size=34, color=GOOD)

    # Footer hint
    draw_note(canvas,
              "Division and multiplication are two sides of the same coin.",
              h - 30, color=MUTED, size=11)


# ── Slide 2 — Flip the question ──────────────────────────────────────────────

def _slide_2(canvas, ex, w, h):
    a, b, ans = ex["a"], ex["b"], ex["ans"]

    # The original division, big
    draw_note(canvas, "The question you see:", 38, color=DIM, size=11)
    draw_centered_expression(canvas, f"{a}  ÷  {b}  =  ?", 85, size=34)

    # Down arrow
    draw_arrow(canvas, w / 2, 125, w / 2, 165, color=ACCENT, width=2)
    draw_pill(canvas, w / 2 + 90, 145, "flip it", bg="#eef2ff", fg=ACCENT, size=10)

    # The multiplication form
    draw_note(canvas, "Ask instead:", 190, color=DIM, size=11)
    draw_centered_expression(canvas, f"?  ×  {b}  =  {a}", 240, size=34, color=INK)

    draw_note(canvas,
              f'Read as: "What number times {b} gives {a}?"',
              h - 30, color=MUTED, size=11)


# ── Slide 3 — Use the times table ────────────────────────────────────────────

def _slide_3(canvas, ex, w, h):
    a, b, ans = ex["a"], ex["b"], ex["ans"]

    draw_note(canvas, f"Walk through the {b}-times table "
                      "until you land on the target.",
              34, color=DIM, size=11)

    # Draw the first 6 rows of the b-times table, highlighting the match
    rows = min(6, max(ans + 1, 5))
    col_x = [w / 2 - 110, w / 2, w / 2 + 110]
    top_y = 70
    row_h = 30
    for i in range(1, rows + 1):
        y = top_y + (i - 1) * row_h
        is_match = (i == ans)
        color = GOOD if is_match else INK
        font_style = ("Helvetica", 16, "bold") if is_match else ("Helvetica", 15)
        canvas.create_text(col_x[0], y, text=str(i),       fill=color, font=font_style, anchor="e")
        canvas.create_text(col_x[0] + 15, y, text="×",     fill=DIM,   font=("Helvetica", 14), anchor="w")
        canvas.create_text(col_x[1], y, text=str(b),       fill=color, font=font_style)
        canvas.create_text(col_x[1] + 18, y, text="=",     fill=DIM,   font=("Helvetica", 14), anchor="w")
        canvas.create_text(col_x[2], y, text=str(i * b),   fill=color, font=font_style, anchor="w")

        if is_match:
            # draw a soft highlight pill behind the row
            canvas.create_rectangle(col_x[0] - 70, y - 14, col_x[2] + 70, y + 14,
                                    outline="", fill="")
            # shorter arrow + label — "match — answer is 4" used to run past
            # the 720px canvas edge; just "match!" fits inside comfortably and
            # the pupil's eye is already on the highlighted row.
            draw_arrow(canvas, col_x[2] + 80, y, col_x[2] + 140, y,
                       color=GOOD, width=2)
            canvas.create_text(col_x[2] + 155, y,
                               text="match!",
                               fill=GOOD, font=("Helvetica", 12, "bold"),
                               anchor="w")

    draw_note(canvas,
              f"So {a} ÷ {b} = {ans}.",
              h - 30, color=MUTED, size=11)


# ── Slide 4 — Verify by multiplying back ─────────────────────────────────────

def _slide_4(canvas, ex, w, h):
    a, b, ans = ex["a"], ex["b"], ex["ans"]

    draw_note(canvas, "Check your work:", 40, color=DIM, size=11)
    draw_centered_expression(canvas, f"{ans}  ×  {b}  =  ?", 90, size=34)

    draw_arrow(canvas, w / 2, 130, w / 2, 170, color=ACCENT, width=2)

    draw_centered_expression(canvas, f"{ans}  ×  {b}  =  {a}  ✓", 215,
                             size=34, color=GOOD)

    # Tip strip — auto-sized and centered. Measuring the body text with a
    # hidden create_text/bbox call lets us wrap a tight pill around "Tip +
    # body" rather than the fixed-width bar we used to draw, which looked
    # lopsided because the content filled only ~70% of the box.
    tip_label = "Tip"
    tip_body  = ("If the multiplication doesn't come back to the "
                 "original number, re-check the times table row.")
    lbl_font  = ("Helvetica", 10, "bold")
    body_font = ("Helvetica", 11)

    probe_l = canvas.create_text(0, -9999, text=tip_label, font=lbl_font, anchor="w")
    lx1, _, lx2, _ = canvas.bbox(probe_l)
    canvas.delete(probe_l)
    probe_b = canvas.create_text(0, -9999, text=tip_body, font=body_font, anchor="w")
    bx1, _, bx2, _ = canvas.bbox(probe_b)
    canvas.delete(probe_b)

    lbl_w, body_w = lx2 - lx1, bx2 - bx1
    gap, pad     = 14, 16  # gap between label and body, inside-padding
    inner_w      = lbl_w + gap + body_w
    box_w        = min(inner_w + pad * 2, w - 80)
    box_x1       = (w - box_w) / 2
    box_y        = h - 55
    canvas.create_rectangle(box_x1, box_y - 18, box_x1 + box_w, box_y + 18,
                            fill=SOFT, outline="")
    canvas.create_text(box_x1 + pad, box_y, anchor="w",
                       text=tip_label, fill=WARN, font=lbl_font)
    canvas.create_text(box_x1 + pad + lbl_w + gap, box_y, anchor="w",
                       text=tip_body, fill=MUTED, font=body_font)


# ── Slide list (what the framework consumes) ─────────────────────────────────

SLIDES = [
    {
        "title":   "1 · The big idea",
        "caption": ("Division answers the opposite of a multiplication. "
                    "If you know the times tables, you already know the division."),
        "draw":    _slide_1,
    },
    {
        "title":   "2 · Flip the question",
        "caption": ("Rewrite the division as a multiplication with a missing "
                    "factor. The missing factor is the answer you're looking for."),
        "draw":    _slide_2,
    },
    {
        "title":   "3 · Use the times table",
        "caption": ("Step through the times table of the divisor until the "
                    "product matches the number you started with."),
        "draw":    _slide_3,
    },
    {
        "title":   "4 · Verify",
        "caption": ("Multiply the answer back by the divisor. If it equals "
                    "the original number, the answer is correct."),
        "draw":    _slide_4,
    },
]
