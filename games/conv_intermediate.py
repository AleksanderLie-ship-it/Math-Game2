"""
conv_intermediate.py
--------------------
Conversions: Intermediate — fractions ↔ percentages (integer % only).

Uses fractions whose percentage is a clean integer:
    1/4 = 25%,  1/2 = 50%,  3/4 = 75%,  1/5 = 20% …

Each question is randomly either:
    • fraction → percentage  (show "1/4", answer "25")
    • percentage → fraction  (show "25%", answer "1/4")

When asking for a percentage the student types the number only (e.g. "25", not "25%").
ANSWER_FORMAT is set per question ("percentage" or "fraction").
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import random
import tkinter as tk
from fractions import Fraction

from .frac_base import FractionBase, _fmt_frac


# (fraction, percentage_as_int) pairs — all produce clean integer percentages
_PAIRS = [
    (Fraction(1, 2),   50),
    (Fraction(1, 4),   25),
    (Fraction(3, 4),   75),
    (Fraction(1, 5),   20),
    (Fraction(2, 5),   40),
    (Fraction(3, 5),   60),
    (Fraction(4, 5),   80),
    (Fraction(1, 10),  10),
    (Fraction(3, 10),  30),
    (Fraction(7, 10),  70),
    (Fraction(9, 10),  90),
    (Fraction(1, 3),   33),   # ≈ 33% (we accept ±1% via 0.0011 tolerance after /100)
    (Fraction(2, 3),   67),   # ≈ 67%
    (Fraction(1, 8),   13),   # ≈ 12.5% — round to 13 accepted via tolerance
    (Fraction(3, 8),   38),   # ≈ 37.5%
    (Fraction(1, 20),   5),
    (Fraction(3, 20),  15),
    (Fraction(1, 25),   4),
    (Fraction(1, 50),   2),
]


class ConvIntermediate(FractionBase):
    TITLE    = "Conversions: Intermediate"
    SUBTITLE = "Convert between fractions and percentages."
    GAME_ID  = "conv_intermediate"

    # ──────────────────────────────────────────────────── init ────────────────

    def __init__(self, parent, back_callback, ach_store, missed_store, scores_store,
                 sessions_store=None):
        self._frac      = Fraction(1, 4)
        self._pct       = 25
        self._direction = "to_pct"
        self._expected  = Fraction(1, 4)
        super().__init__(parent, back_callback, ach_store, missed_store, scores_store,
                         sessions_store=sessions_store)

    # ──────────────────────────────────────────── question area layout ─────────

    def _build_question_area(self, parent):
        q_box = tk.Frame(parent, bg="white",
                         highlightbackground="#e2e8f0", highlightthickness=1)
        q_box.pack(fill=tk.BOTH, expand=True)
        inner = tk.Frame(q_box, bg="white", padx=24, pady=18)
        inner.pack(fill=tk.BOTH, expand=True)

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
        self._frac, self._pct = random.choice(_PAIRS)
        self._direction = random.choice(["to_pct", "to_fraction"])
        self._expected  = self._frac
        self.ANSWER_FORMAT = ("percentage" if self._direction == "to_pct"
                              else "fraction")

    def get_expected(self) -> Fraction:
        return self._expected

    def _alternate_expected(self):
        # For rounded pairs (1/3↔33, 2/3↔67, 1/8↔13, 3/8↔38) the displayed
        # percentage is not mathematically equal to the stored fraction.
        # Accept the literal pct/100 reading in addition to the exact
        # fraction, so a student who computed 38/100 (= 19/50) or typed
        # 38 as a percentage of 3/8 does not get marked wrong.
        literal = Fraction(self._pct, 100)
        if literal != self._frac:
            return (literal,)
        return ()

    def update_question_display(self):
        if self._direction == "to_pct":
            self.prompt_label.configure(text="Convert to percentage:")
            self.question_label.configure(text=_fmt_frac(self._frac))
            self.hint_label.configure(text="type the number only, e.g. 25")
        else:
            self.prompt_label.configure(text="Convert to fraction:")
            self.question_label.configure(text=f"{self._pct}%")
            self.hint_label.configure(text="type a fraction, e.g. 1/4")

    def correct_history_text(self, expected: Fraction) -> str:
        if self._direction == "to_pct":
            return f"{_fmt_frac(self._frac)} = {self._pct}%"
        return f"{self._pct}% = {_fmt_frac(expected)}"

    def wrong_history_text(self, given: str) -> str:
        if self._direction == "to_pct":
            return f"{_fmt_frac(self._frac)} ≠ {given}%"
        return f"{self._pct}% ≠ {given}"
