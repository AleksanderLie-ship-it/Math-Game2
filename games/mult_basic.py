"""
mult_basic.py
-------------
Basic multiplication practice: single-digit × single-digit (1–10).
"""

import tkinter as tk
import random

from .base_game import BaseGame


class MultiplicationBasic(BaseGame):
    TITLE    = "Multiplication Practice 1–10"
    SUBTITLE = "A new task appears every time you answer correctly."
    GAME_ID  = "mult_basic"

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
        self.a = random.randint(1, 10)
        self.b = random.randint(1, 10)

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
