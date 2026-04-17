"""
frac_advanced.py
----------------
Fractions: Advanced — add and subtract proper fractions whose denominators
are UNRELATED (neither divides the other). This forces a real
common-denominator step (multiplying both denominators, or the LCM when
they share a factor), not just scaling one operand up to match the other.

Pedagogical distinction from Intermediate:
    Intermediate:  one denom is a clean multiple of the other (1/4 + 3/8).
                   The student scales the smaller-denom operand and adds.
    Advanced:      neither divides the other (3/13 + 9/19, 5/6 + 4/9).
                   The student must find an LCM — usually the product,
                   occasionally smaller when there is a shared factor
                   (e.g. 6 and 9 share a 3 → LCM 18, not 54).

Denominator pool is deliberately big: primes (7, 11, 13, 17, 19) next to
composites (10, 12, 14, 15, 16, 18, 20). Numerators are 1..denom-1, so
on denom 13 a student can land on 12/13, well past the "numbers only
between 1 and 10" floor Aleks flagged in the roadmap.

Operands are shown in raw a/b form (no auto-simplification), so 4/12 stays
"4/12" on screen even though Fraction(4, 12) = Fraction(1, 3) internally.
Results can be less than, equal to, or greater than 1. The
FractionBase parser accepts any equivalent form the student types —
improper ("23/15"), mixed ("1 8/15"), or reduced — via Fraction equality.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import random
import tkinter as tk
from fractions import Fraction

from .frac_base import FractionBase, _fmt_frac


class FracAdvanced(FractionBase):
    TITLE    = "Fractions: Advanced"
    SUBTITLE = "Add and subtract fractions with unrelated denominators."
    GAME_ID  = "frac_advanced"

    # Mix of primes and composites — ensures both coprime pairs
    # (13, 19) and non-coprime non-divisor pairs (6, 9) appear.
    DENOMS = [5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    # ──────────────────────────────────────────────────── init ────────────────

    def __init__(self, parent, back_callback, ach_store, missed_store, scores_store,
                 sessions_store=None):
        # Raw ints preserve the displayed form, independent of Fraction's
        # auto-simplification.
        self._a_num    = 3
        self._a_denom  = 13
        self._b_num    = 9
        self._b_denom  = 19
        self._op       = "+"
        self._expected = Fraction(3, 13) + Fraction(9, 19)
        super().__init__(parent, back_callback, ach_store, missed_store, scores_store,
                         sessions_store=sessions_store)

    # ──────────────────────────────────────────── question area layout ─────────

    def _build_question_area(self, parent):
        tk.Label(parent,
                 text="Hint: find a common denominator first — any equivalent answer works",
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

    def _pick_unrelated_pair(self):
        """
        Sample two different denoms where neither divides the other.
        Guaranteed terminating: DENOMS contains enough primes to make
        the search succeed in 1-2 tries on average.
        """
        for _ in range(100):
            d1, d2 = random.sample(self.DENOMS, 2)
            if d1 % d2 == 0 or d2 % d1 == 0:
                continue
            return d1, d2
        return 13, 19   # safe coprime fallback

    def new_question(self):
        op = random.choice(["+", "-"])

        a = b = d1 = d2 = None
        fa = fb = result = None
        for _ in range(50):
            d1, d2 = self._pick_unrelated_pair()
            a = random.randint(1, d1 - 1)
            b = random.randint(1, d2 - 1)
            fa = Fraction(a, d1)
            fb = Fraction(b, d2)

            if op == "-" and fa < fb:
                # Ensure positive result by swapping — keep raw ints in sync.
                fa, fb = fb, fa
                d1, d2 = d2, d1
                a,  b  = b,  a

            result = fa + fb if op == "+" else fa - fb
            if result > 0:
                break
        else:
            # Fallback: the example from the roadmap note.
            a, d1, b, d2, op = 3, 13, 9, 19, "+"
            fa, fb = Fraction(a, d1), Fraction(b, d2)
            result = fa + fb

        self._a_num    = a
        self._a_denom  = d1
        self._b_num    = b
        self._b_denom  = d2
        self._op       = op
        self._expected = result
        self.ANSWER_FORMAT = "fraction"

    def get_expected(self) -> Fraction:
        return self._expected

    # Raw operand strings — never simplified. Display 4/12 as "4/12",
    # not "1/3", so the common-denominator task is visible to the student.
    def _q_left(self) -> str:
        return f"{self._a_num}/{self._a_denom}"

    def _q_right(self) -> str:
        return f"{self._b_num}/{self._b_denom}"

    def update_question_display(self):
        self.question_label.configure(
            text=f"{self._q_left()}  {self._op}  {self._q_right()}  =  ?"
        )

    def correct_history_text(self, expected: Fraction) -> str:
        return f"{self._q_left()} {self._op} {self._q_right()} = {_fmt_frac(expected)}"

    def wrong_history_text(self, given: str) -> str:
        return f"{self._q_left()} {self._op} {self._q_right()} ≠ {given}"
