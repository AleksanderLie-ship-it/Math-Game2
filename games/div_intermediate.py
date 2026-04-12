"""
div_intermediate.py
-------------------
Intermediate division: multi-digit dividends, always whole-number answers.

Two alternating types:
  Type A — one-digit divisor, two-digit quotient   e.g. 252 ÷ 9 = 28
  Type B — two-digit divisor, one-digit quotient   e.g. 156 ÷ 13 = 12

Generated as divisor × quotient = dividend to guarantee exact answers.
"""

import tkinter as tk
import random

from .base_game import BaseGame


class DivisionIntermediate(BaseGame):
    TITLE    = "Division — Intermediate"
    SUBTITLE = "Larger dividends, whole-number answers."
    GAME_ID  = "div_intermediate"

    def _build_question_area(self, parent):
        q_box = tk.Frame(parent, bg="white",
                         highlightbackground="#e2e8f0", highlightthickness=1)
        q_box.pack(fill=tk.X, pady=(0, 18))
        inner = tk.Frame(q_box, bg="white", padx=24, pady=22)
        inner.pack(fill=tk.X)
        tk.Label(inner, text="CURRENT TASK",
                 font=("Helvetica", 9), bg="white", fg="#94a3b8").pack()
        self.question_label = tk.Label(inner, text="",
                                        font=("Helvetica", 52, "bold"),
                                        bg="white", fg="#0f172a")
        self.question_label.pack(pady=(6, 0))

    # ---------------------------------------------------------------- abstract

    def new_question(self):
        if random.random() < 0.5:    # Type A: one-digit divisor
            self.divisor  = random.randint(2, 9)
            self.quotient = random.randint(11, 30)
        else:                        # Type B: two-digit divisor
            self.divisor  = random.randint(11, 19)
            self.quotient = random.randint(2, 12)
        self.dividend = self.divisor * self.quotient

    def get_expected(self):
        return self.quotient

    def update_question_display(self):
        self.question_label.configure(text=f"{self.dividend} ÷ {self.divisor}")

    def correct_history_text(self, expected):
        return f"{self.dividend} ÷ {self.divisor} = {expected}"

    def wrong_history_text(self, given):
        return f"{self.dividend} ÷ {self.divisor} ≠ {given}"

    def get_question_dict(self):
        return {"op": "÷", "a": self.dividend, "b": self.divisor,
                "expected": self.quotient, "allow_decimal": False}
