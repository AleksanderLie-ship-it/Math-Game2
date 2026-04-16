"""
frac_intermediate.py
--------------------
Fractions: Intermediate — add and subtract fractions with DIFFERENT denominators
where one denominator is a simple multiple of the other.

Denominator pairs: (2,4), (2,6), (2,8), (2,10), (3,6), (3,9), (4,8), (5,10)
The student must find the LCD and convert before computing.
Results are always positive proper fractions or whole numbers (≤ 1).
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import random
import tkinter as tk
from fractions import Fraction

from .frac_base import FractionBase, _fmt_frac


class FracIntermediate(FractionBase):
    TITLE    = "Fractions: Intermediate"
    SUBTITLE = "Add and subtract fractions with different denominators."
    GAME_ID  = "frac_intermediate"

    # (small_denom, large_denom) — large is always a multiple of small
    DENOM_PAIRS = [
        (2, 4), (2, 6), (2, 8), (2, 10),
        (3, 6), (3, 9),
        (4, 8),
        (5, 10),
    ]

    # ──────────────────────────────────────────────────── init ────────────────

    def __init__(self, parent, back_callback, ach_store, missed_store, scores_store):
        self._num_a    = Fraction(1, 2)
        self._num_b    = Fraction(1, 4)
        self._op       = "+"
        self._expected = Fraction(3, 4)
        super().__init__(parent, back_callback, ach_store, missed_store, scores_store)

    # ──────────────────────────────────────────── question area layout ─────────

    def _build_question_area(self, parent):
        tk.Label(parent, text="Hint: find the common denominator first, e.g. 1/2 + 1/4 = 3/4",
                 font=("Helvetica", 9), bg="white", fg="#94a3b8").pack(anchor="w", pady=(0, 6))

        q_box = tk.Frame(parent, bg="white",
                         highlightbackground="#e2e8f0", highlightthickness=1)
        q_box.pack(fill=tk.X, pady=(0, 18))
        inner = tk.Frame(q_box, bg="white", padx=24, pady=22)
        inner.pack(fill=tk.X)

        tk.Label(inner, text="CALCULATE",
                 font=("Helvetica", 9), bg="white", fg="#94a3b8").pack()
        self.question_label = tk.Label(inner, text="",
                                       font=("Helvetica", 42, "bold"),
                                       bg="white", fg="#0f172a")
        self.question_label.pack(pady=(6, 0))

    # ──────────────────────────────────────────────────── logic ───────────────

    def new_question(self):
        d_small, d_large = random.choice(self.DENOM_PAIRS)
        op = random.choice(["+", "-"])

        # Pick numerators such that result stays in (0, 1]
        for _ in range(50):          # retry loop to find valid combo
            a = random.randint(1, d_small - 1)           # a/d_small < 1
            b = random.randint(1, d_large - 1)           # b/d_large < 1
            fa = Fraction(a, d_small)
            fb = Fraction(b, d_large)
            result = fa + fb if op == "+" else fa - fb
            if 0 < result <= 1:
                break
        else:
            # Fallback: 1/2 + 1/4 = 3/4
            fa, fb, op, result = Fraction(1, 2), Fraction(1, 4), "+", Fraction(3, 4)

        # Randomly swap order (doesn't change result for +, keeps a > b for -)
        if op == "+" and random.random() < 0.5:
            fa, fb = fb, fa

        self._num_a    = fa
        self._num_b    = fb
        self._op       = op
        self._expected = result
        self.ANSWER_FORMAT = "fraction"

    def get_expected(self) -> Fraction:
        return self._expected

    def update_question_display(self):
        a = _fmt_frac(self._num_a)
        b = _fmt_frac(self._num_b)
        self.question_label.configure(text=f"{a}  {self._op}  {b}  =  ?")

    def correct_history_text(self, expected: Fraction) -> str:
        a = _fmt_frac(self._num_a)
        b = _fmt_frac(self._num_b)
        return f"{a} {self._op} {b} = {_fmt_frac(expected)}"

    def wrong_history_text(self, given: str) -> str:
        a = _fmt_frac(self._num_a)
        b = _fmt_frac(self._num_b)
        return f"{a} {self._op} {b} ≠ {given}"
