"""
frac_advanced.py
----------------
Fractions: Advanced — add and subtract MIXED NUMBERS.

Operands are mixed numbers like 1 1/2, 2 1/3, 1 1/4 etc.
Results can be any positive mixed number or whole number.
The student types their answer in mixed-number format: "2 3/4" or "3".

Denominators used: 2, 3, 4, 6 (keeps arithmetic manageable for 5th grade).
Whole-number parts: 1 or 2.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import random
import tkinter as tk
from fractions import Fraction

from .frac_base import FractionBase, _fmt_frac, _fmt_mixed


class FracAdvanced(FractionBase):
    TITLE    = "Fractions: Advanced"
    SUBTITLE = "Add and subtract mixed numbers."
    GAME_ID  = "frac_advanced"

    DENOMS = [2, 3, 4, 6]

    # ──────────────────────────────────────────────────── init ────────────────

    def __init__(self, parent, back_callback, ach_store, missed_store, scores_store):
        self._num_a    = Fraction(3, 2)    # 1 1/2
        self._num_b    = Fraction(5, 4)    # 1 1/4
        self._op       = "+"
        self._expected = Fraction(11, 4)   # 2 3/4
        super().__init__(parent, back_callback, ach_store, missed_store, scores_store)

    # ──────────────────────────────────────────── question area layout ─────────

    def _build_question_area(self, parent):
        tk.Label(parent,
                 text="Hint: type mixed numbers as '1 3/4', whole numbers as '3'",
                 font=("Helvetica", 9), bg="white", fg="#94a3b8").pack(anchor="w", pady=(0, 6))

        q_box = tk.Frame(parent, bg="white",
                         highlightbackground="#e2e8f0", highlightthickness=1)
        q_box.pack(fill=tk.BOTH, expand=True)
        inner = tk.Frame(q_box, bg="white", padx=24, pady=22)
        inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(inner, text="CALCULATE",
                 font=("Helvetica", 9), bg="white", fg="#94a3b8").pack()
        self.question_label = tk.Label(inner, text="",
                                       font=("Helvetica", 36, "bold"),
                                       bg="white", fg="#0f172a")
        self.question_label.pack(pady=(6, 0))

    # ──────────────────────────────────────────────────── logic ───────────────

    def _rand_mixed(self, denom) -> Fraction:
        """Return a random mixed number with the given denominator: whole in {1,2}, frac part > 0."""
        whole = random.randint(1, 2)
        numer = random.randint(1, denom - 1)
        return Fraction(whole * denom + numer, denom)

    def new_question(self):
        op = random.choice(["+", "-"])

        for _ in range(50):
            # Pick two compatible denominators (same or one multiple of other)
            d1 = random.choice(self.DENOMS)
            # d2 is either same as d1, or related
            related = [d for d in self.DENOMS
                       if d == d1 or d % d1 == 0 or d1 % d == 0]
            d2 = random.choice(related)

            fa = self._rand_mixed(d1)
            fb = self._rand_mixed(d2)

            if op == "-" and fa < fb:
                fa, fb = fb, fa          # ensure positive result

            result = fa + fb if op == "+" else fa - fb
            if result > 0:
                break
        else:
            fa, fb, op, result = (Fraction(3, 2), Fraction(5, 4),
                                   "+", Fraction(11, 4))

        self._num_a    = fa
        self._num_b    = fb
        self._op       = op
        self._expected = result
        self.ANSWER_FORMAT = "fraction"

    def get_expected(self) -> Fraction:
        return self._expected

    def update_question_display(self):
        a = _fmt_mixed(self._num_a)
        b = _fmt_mixed(self._num_b)
        self.question_label.configure(text=f"{a}  {self._op}  {b}  =  ?")

    def correct_history_text(self, expected: Fraction) -> str:
        a = _fmt_mixed(self._num_a)
        b = _fmt_mixed(self._num_b)
        return f"{a} {self._op} {b} = {_fmt_mixed(expected)}"

    def wrong_history_text(self, given: str) -> str:
        a = _fmt_mixed(self._num_a)
        b = _fmt_mixed(self._num_b)
        return f"{a} {self._op} {b} ≠ {given}"
