"""
div_basic.py
------------
Beginner division: mirrors the 1–10 multiplication table.
Divisor in [2, 10], quotient in [1, 10] — always a whole number.
e.g. 42 ÷ 7 = 6
"""

import tkinter as tk
import random

from .base_game import BaseGame


class DivisionBasic(BaseGame):
    TITLE    = "Division — Beginner"
    SUBTITLE = "Whole-number answers. Divisors from 2 to 10."
    GAME_ID  = "div_basic"

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
        self.divisor   = random.randint(2, 10)
        self.quotient  = random.randint(1, 10)
        self.dividend  = self.divisor * self.quotient

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
