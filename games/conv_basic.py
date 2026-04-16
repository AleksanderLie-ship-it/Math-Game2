"""
conv_basic.py
-------------
Conversions: Beginner — fractions ↔ decimals.

Uses clean denominators (2, 4, 5, 8, 10) that produce terminating decimals.
Each question is randomly either:
    • fraction → decimal  (show "3/4", answer "0.75")
    • decimal  → fraction (show "0.75", answer "3/4")

ANSWER_FORMAT is set per question ("fraction" or "decimal").
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import random
import tkinter as tk
from fractions import Fraction

from .frac_base import FractionBase, _fmt_frac


# Pre-built pool of (fraction, decimal_str) pairs — all terminating decimals
_PAIRS = [
    (Fraction(1, 2),  "0.5"),
    (Fraction(1, 4),  "0.25"),
    (Fraction(3, 4),  "0.75"),
    (Fraction(1, 5),  "0.2"),
    (Fraction(2, 5),  "0.4"),
    (Fraction(3, 5),  "0.6"),
    (Fraction(4, 5),  "0.8"),
    (Fraction(1, 8),  "0.125"),
    (Fraction(3, 8),  "0.375"),
    (Fraction(5, 8),  "0.625"),
    (Fraction(7, 8),  "0.875"),
    (Fraction(1, 10), "0.1"),
    (Fraction(3, 10), "0.3"),
    (Fraction(7, 10), "0.7"),
    (Fraction(9, 10), "0.9"),
    (Fraction(2, 4),  "0.5"),   # = 1/2 — shown as 2/4 on purpose (tests simplification)
]


class ConvBasic(FractionBase):
    TITLE    = "Conversions: Beginner"
    SUBTITLE = "Convert between fractions and decimals."
    GAME_ID  = "conv_basic"

    # ──────────────────────────────────────────────────── init ────────────────

    def __init__(self, parent, back_callback, ach_store, missed_store, scores_store):
        self._frac      = Fraction(3, 4)
        self._dec_str   = "0.75"
        self._direction = "to_decimal"   # "to_decimal" or "to_fraction"
        self._expected  = Fraction(3, 4)
        super().__init__(parent, back_callback, ach_store, missed_store, scores_store)

    # ──────────────────────────────────────────── question area layout ─────────

    def _build_question_area(self, parent):
        q_box = tk.Frame(parent, bg="white",
                         highlightbackground="#e2e8f0", highlightthickness=1)
        q_box.pack(fill=tk.X, pady=(0, 18))
        inner = tk.Frame(q_box, bg="white", padx=24, pady=18)
        inner.pack(fill=tk.X)

        self.prompt_label = tk.Label(inner, text="",
                                     font=("Helvetica", 11),
                                     bg="white", fg="#64748b")
        self.prompt_label.pack(anchor="w")

        self.question_label = tk.Label(inner, text="",
                                       font=("Helvetica", 52, "bold"),
                                       bg="white", fg="#0f172a")
        self.question_label.pack(pady=(8, 4))

        self.hint_label = tk.Label(inner, text="",
                                   font=("Helvetica", 9),
                                   bg="white", fg="#94a3b8")
        self.hint_label.pack(anchor="e")

    # ──────────────────────────────────────────────────── logic ───────────────

    def new_question(self):
        self._frac, self._dec_str = random.choice(_PAIRS)
        self._direction = random.choice(["to_decimal", "to_fraction"])
        self._expected  = self._frac          # always store as Fraction
        self.ANSWER_FORMAT = ("decimal" if self._direction == "to_decimal"
                              else "fraction")

    def get_expected(self) -> Fraction:
        return self._expected

    def update_question_display(self):
        if self._direction == "to_decimal":
            self.prompt_label.configure(text="Convert to decimal:")
            self.question_label.configure(text=_fmt_frac(self._frac))
            self.hint_label.configure(text="type a decimal, e.g. 0.75")
        else:
            self.prompt_label.configure(text="Convert to fraction:")
            self.question_label.configure(text=self._dec_str)
            self.hint_label.configure(text="type a fraction, e.g. 3/4")

    def correct_history_text(self, expected: Fraction) -> str:
        if self._direction == "to_decimal":
            return f"{_fmt_frac(self._frac)} = {self._dec_str}"
        return f"{self._dec_str} = {_fmt_frac(expected)}"

    def wrong_history_text(self, given: str) -> str:
        if self._direction == "to_decimal":
            return f"{_fmt_frac(self._frac)} ≠ {given}"
        return f"{self._dec_str} ≠ {given}"
