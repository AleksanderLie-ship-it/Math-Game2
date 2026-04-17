"""
frac_basic.py
-------------
Fractions: Beginner — add and subtract fractions with the SAME denominator.

Denominators: 2, 3, 4, 5, 6, 8, 10
Results are always positive proper fractions or 1 (never improper, never 0).
Answers are entered as fractions: "3/4", "1/2", "1"
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import random
import tkinter as tk
from fractions import Fraction

from .frac_base import FractionBase, _fmt_frac


class FracBasic(FractionBase):
    TITLE    = "Fractions: Beginner"
    SUBTITLE = "Add and subtract fractions with the same denominator."
    GAME_ID  = "frac_basic"

    DENOMS = [2, 3, 4, 5, 6, 8, 10]

    # ──────────────────────────────────────────────────── init ────────────────

    def __init__(self, parent, back_callback, ach_store, missed_store, scores_store):
        self._num_a    = Fraction(1, 2)
        self._num_b    = Fraction(1, 4)
        self._op       = "+"
        self._expected = Fraction(3, 4)
        super().__init__(parent, back_callback, ach_store, missed_store, scores_store)

    # ──────────────────────────────────────────── question area layout ─────────

    def _build_question_area(self, parent):
        tk.Label(parent, text="Hint: enter your answer as a fraction, e.g. 3/4",
                 font=("Helvetica", 9), bg="white", fg="#94a3b8").pack(anchor="w", pady=(0, 6))

        q_box = tk.Frame(parent, bg="white",
                         highlightbackground="#e2e8f0", highlightthickness=1)
        q_box.pack(fill=tk.BOTH, expand=True)
        inner = tk.Frame(q_box, bg="white", padx=24, pady=22)
        inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(inner, text="CALCULATE",
                 font=("Helvetica", 9), bg="white", fg="#94a3b8").pack()
        self.question_label = tk.Label(inner, text="",
                                       font=("Helvetica", 42, "bold"),
                                       bg="white", fg="#0f172a")
        self.question_label.pack(pady=(6, 0))

    # ──────────────────────────────────────────────────── logic ───────────────

    def new_question(self):
        d  = random.choice(self.DENOMS)
        op = random.choice(["+", "-"])
        if op == "+":
            a = random.randint(1, d - 1)
            b = random.randint(1, d - a)       # a + b ≤ d → result ≤ 1
        else:
            a = random.randint(2, d)
            b = random.randint(1, a - 1)       # a > b  → result > 0
        self._num_a    = Fraction(a, d)
        self._num_b    = Fraction(b, d)
        self._op       = op
        self._expected = (Fraction(a + b, d) if op == "+"
                          else Fraction(a - b, d))
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
