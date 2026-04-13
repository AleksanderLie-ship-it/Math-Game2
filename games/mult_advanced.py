"""
mult_advanced.py
----------------
Advanced multiplication: 75% three-digit × two-digit, 25% intermediate-style.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import tkinter as tk
import random

from .base_game import BaseGame


def _intermediate_question():
    """Same pool as MultiplicationIntermediate."""
    choice = random.randint(0, 2)
    if choice == 0:
        return random.randint(10, 99), random.randint(2, 9)
    elif choice == 1:
        return random.randint(2, 9), random.randint(10, 99)
    else:
        return random.randint(10, 99), random.randint(10, 99)


class MultiplicationAdvanced(BaseGame):
    TITLE    = "Multiplication — Advanced"
    SUBTITLE = "Three-digit × two-digit, with mixed problems."
    GAME_ID  = "mult_advanced"

    def _build_question_area(self, parent):
        q_box = tk.Frame(parent, bg="white",
                         highlightbackground="#e2e8f0", highlightthickness=1)
        q_box.pack(fill=tk.X, pady=(0, 18))
        inner = tk.Frame(q_box, bg="white", padx=24, pady=22)
        inner.pack(fill=tk.X)
        tk.Label(inner, text="CURRENT TASK",
                 font=("Helvetica", 9), bg="white", fg="#94a3b8").pack()
        self.question_label = tk.Label(inner, text="",
                                        font=("Helvetica", 48, "bold"),
                                        bg="white", fg="#0f172a")
        self.question_label.pack(pady=(6, 0))

    # ---------------------------------------------------------------- abstract

    def new_question(self):
        if random.random() < 0.75:          # 75% — abc × cd
            self.a = random.randint(100, 999)
            self.b = random.randint(10, 99)
        else:                               # 25% — intermediate pool
            self.a, self.b = _intermediate_question()

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
