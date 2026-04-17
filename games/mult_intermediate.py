"""
mult_intermediate.py
--------------------
Intermediate multiplication: two-digit × one-digit, one-digit × two-digit,
and two-digit × two-digit, chosen randomly each round.
No noisy labels — just the problem.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import tkinter as tk
import random

from .base_game import BaseGame


# (range_a, range_b)
PROBLEM_TYPES = [
    ((10, 99), (2, 9)),    # ab × c
    ((2,  9),  (10, 99)),  # c × ab
    ((10, 99), (10, 99)),  # ab × cd
]


class MultiplicationIntermediate(BaseGame):
    TITLE    = "Multiplication – Intermediate"
    SUBTITLE = "Two-digit and mixed problems."
    GAME_ID  = "mult_intermediate"

    def _build_question_area(self, parent):
        q_box = tk.Frame(parent, bg="white",
                         highlightbackground="#e2e8f0", highlightthickness=1)
        q_box.pack(fill=tk.BOTH, expand=True)
        inner = tk.Frame(q_box, bg="white", padx=24, pady=22)
        inner.pack(fill=tk.BOTH, expand=True)
        tk.Label(inner, text="CURRENT TASK",
                 font=("Helvetica", 9), bg="white", fg="#94a3b8").pack()
        self.question_label = tk.Label(inner, text="",
                                        font=("Helvetica", 52, "bold"),
                                        bg="white", fg="#0f172a")
        self.question_label.pack(pady=(6, 0))

    # ---------------------------------------------------------------- abstract

    def new_question(self):
        range_a, range_b = random.choice(PROBLEM_TYPES)
        self.a = random.randint(*range_a)
        self.b = random.randint(*range_b)

    def get_expected(self):
        return self.a * self.b

    def update_question_display(self):
        self.question_label.configure(text=f"{self.a} × {self.b}")

    def correct_history_text(self, expected):
        return f"{self.a} × {self.b} = {expected}"

    def wrong_history_text(self, given):
        return f"{self.a} × {self.b} ≠ {given}"

    def get_question_dict(self):
        return {"op": "×", "a": self.a, "b": self.b,
                "expected": self.a * self.b, "allow_decimal": False}
