"""
div_advanced.py
---------------
Advanced division: 75/25 split.

  75% — large integer problems (divisor [2,25], quotient [21,99])
         e.g. 1624 ÷ 24 = 67

  25% — decimal answers using divisors that give terminating decimals {2, 4, 5}
         e.g. 13 ÷ 2 = 6.5   |   17 ÷ 4 = 4.25   |   23 ÷ 5 = 4.6

Answers are always exact — generated as divisor × quotient = dividend.
For decimal questions, dividend is chosen so dividend % divisor ≠ 0,
guaranteeing a non-integer result that still terminates.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import tkinter as tk
import random

from .base_game import BaseGame


# Divisors whose multiples always give terminating decimals
_DECIMAL_DIVISORS = [2, 4, 5]


def _fmt(n):
    """Format a number: drop '.0' for whole floats, keep other decimals."""
    if isinstance(n, float) and n == int(n):
        return str(int(n))
    return str(n)


class DivisionAdvanced(BaseGame):
    TITLE         = "Division — Advanced"
    SUBTITLE      = "Some answers are decimals — use a dot  (e.g. 6.5)"
    ALLOW_DECIMAL = True
    GAME_ID       = "div_advanced"

    def _build_question_area(self, parent):
        q_box = tk.Frame(parent, bg="white",
                         highlightbackground="#e2e8f0", highlightthickness=1)
        q_box.pack(fill=tk.BOTH, expand=True)
        inner = tk.Frame(q_box, bg="white", padx=24, pady=22)
        inner.pack(fill=tk.BOTH, expand=True)
        tk.Label(inner, text="CURRENT TASK",
                 font=("Helvetica", 9), bg="white", fg="#94a3b8").pack()
        self.question_label = tk.Label(inner, text="",
                                        font=("Helvetica", 48, "bold"),
                                        bg="white", fg="#0f172a")
        self.question_label.pack(pady=(6, 0))

    # ---------------------------------------------------------------- abstract

    def new_question(self):
        if random.random() < 0.75:
            # Large integer problem
            self.divisor  = random.randint(2, 25)
            self.quotient = random.randint(21, 99)
            self.dividend = self.divisor * self.quotient      # exact integer
            self._is_decimal = False
        else:
            # Decimal problem — pick a dividend not cleanly divisible by divisor
            self.divisor = random.choice(_DECIMAL_DIVISORS)
            while True:
                self.dividend = random.randint(11, 60)
                if self.dividend % self.divisor != 0:
                    break
            self.quotient = self.dividend / self.divisor      # float
            self._is_decimal = True

    def get_expected(self):
        return self.quotient   # int or float

    def update_question_display(self):
        self.question_label.configure(text=f"{self.dividend} ÷ {self.divisor}")

    def correct_history_text(self, expected):
        return f"{self.dividend} ÷ {self.divisor} = {_fmt(expected)}"

    def wrong_history_text(self, given):
        return f"{self.dividend} ÷ {self.divisor} ≠ {_fmt(float(given))}"

    def get_question_dict(self):
        return {"op": "÷", "a": self.dividend, "b": self.divisor,
                "expected": self.quotient, "allow_decimal": self._is_decimal}
