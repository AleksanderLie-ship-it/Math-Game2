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

    def __init__(self, parent, back_callback, ach_store, missed_store, scores_store,
                 sessions_store=None):
        # Raw integer parts preserve the same-denominator presentation; the
        # Fraction constructor auto-simplifies, which used to turn "2/4"
        # into "1/2" on display and violated the card's promise.
        self._a_num    = 1
        self._b_num    = 1
        self._denom    = 4
        self._op       = "+"
        self._expected = Fraction(2, 4)
        super().__init__(parent, back_callback, ach_store, missed_store, scores_store,
                         sessions_store=sessions_store)

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
        # Store raw ints; the visual denominator must stay equal on both
        # sides of the operator, even when a/d simplifies (e.g. 2/6).
        self._a_num    = a
        self._b_num    = b
        self._denom    = d
        self._op       = op
        self._expected = (Fraction(a + b, d) if op == "+"
                          else Fraction(a - b, d))
        self.ANSWER_FORMAT = "fraction"

    def get_expected(self) -> Fraction:
        return self._expected

    def _q_left(self) -> str:
        return f"{self._a_num}/{self._denom}"

    def _q_right(self) -> str:
        return f"{self._b_num}/{self._denom}"

    def update_question_display(self):
        self.question_label.configure(
            text=f"{self._q_left()}  {self._op}  {self._q_right()}  =  ?"
        )

    def correct_history_text(self, expected: Fraction) -> str:
        return f"{self._q_left()} {self._op} {self._q_right()} = {_fmt_frac(expected)}"

    def wrong_history_text(self, given: str) -> str:
        return f"{self._q_left()} {self._op} {self._q_right()} ≠ {given}"
