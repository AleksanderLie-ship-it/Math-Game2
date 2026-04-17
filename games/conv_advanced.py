"""
conv_advanced.py
----------------
Conversions: Advanced — all three directions across fraction, decimal, percentage.

Question types (chosen randomly):
    • fraction  → decimal     (e.g. "3/4 = ?"  answer 0.75)
    • fraction  → percentage  (e.g. "3/4 = ?"  answer 75)
    • decimal   → fraction    (e.g. "0.75 = ?" answer 3/4)
    • decimal   → percentage  (e.g. "0.75 = ?" answer 75)
    • percentage→ fraction    (e.g. "75% = ?"  answer 3/4)
    • percentage→ decimal     (e.g. "75% = ?"  answer 0.75)

Uses the same pool as conv_basic (clean denominators / integer percentages).
ANSWER_FORMAT is set per question.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import random
import tkinter as tk
from fractions import Fraction

from .frac_base import FractionBase, _fmt_frac


# (fraction, decimal_str, percentage_int)
_POOL = [
    (Fraction(1, 2),  "0.5",   50),
    (Fraction(1, 4),  "0.25",  25),
    (Fraction(3, 4),  "0.75",  75),
    (Fraction(1, 5),  "0.2",   20),
    (Fraction(2, 5),  "0.4",   40),
    (Fraction(3, 5),  "0.6",   60),
    (Fraction(4, 5),  "0.8",   80),
    (Fraction(1, 8),  "0.125", 13),   # 12.5% → accepted as 13 via tolerance
    (Fraction(3, 8),  "0.375", 38),
    (Fraction(1, 10), "0.1",   10),
    (Fraction(3, 10), "0.3",   30),
    (Fraction(7, 10), "0.7",   70),
    (Fraction(9, 10), "0.9",   90),
]

_DIRECTIONS = [
    "frac_to_dec",
    "frac_to_pct",
    "dec_to_frac",
    "dec_to_pct",
    "pct_to_frac",
    "pct_to_dec",
]


class ConvAdvanced(FractionBase):
    TITLE    = "Conversions: Advanced"
    SUBTITLE = "Convert freely between fractions, decimals, and percentages."
    GAME_ID  = "conv_advanced"

    # ──────────────────────────────────────────────────── init ────────────────

    def __init__(self, parent, back_callback, ach_store, missed_store, scores_store,
                 sessions_store=None):
        self._frac      = Fraction(3, 4)
        self._dec_str   = "0.75"
        self._pct       = 75
        self._direction = "frac_to_dec"
        self._expected  = Fraction(3, 4)
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
        self._frac, self._dec_str, self._pct = random.choice(_POOL)
        self._direction = random.choice(_DIRECTIONS)

        d = self._direction
        if d in ("frac_to_dec", "pct_to_dec"):
            self.ANSWER_FORMAT = "decimal"
            self._expected     = self._frac
        elif d in ("frac_to_pct", "dec_to_pct"):
            self.ANSWER_FORMAT = "percentage"
            self._expected     = self._frac
        else:   # dec_to_frac or pct_to_frac
            self.ANSWER_FORMAT = "fraction"
            self._expected     = self._frac

    def get_expected(self) -> Fraction:
        return self._expected

    def update_question_display(self):
        d = self._direction
        prompts = {
            "frac_to_dec": ("Convert to decimal:",      _fmt_frac(self._frac),  "type a decimal, e.g. 0.75"),
            "frac_to_pct": ("Convert to percentage:",   _fmt_frac(self._frac),  "type the number only, e.g. 75"),
            "dec_to_frac": ("Convert to fraction:",     self._dec_str,           "type a fraction, e.g. 3/4"),
            "dec_to_pct":  ("Convert to percentage:",   self._dec_str,           "type the number only, e.g. 75"),
            "pct_to_frac": ("Convert to fraction:",     f"{self._pct}%",         "type a fraction, e.g. 3/4"),
            "pct_to_dec":  ("Convert to decimal:",      f"{self._pct}%",         "type a decimal, e.g. 0.75"),
        }
        prompt, value, hint = prompts[d]
        self.prompt_label.configure(text=prompt)
        self.question_label.configure(text=value)
        self.hint_label.configure(text=hint)

    def _given_display(self) -> str:
        d = self._direction
        if d.startswith("frac"):    return _fmt_frac(self._frac)
        if d.startswith("dec"):     return self._dec_str
        return f"{self._pct}%"

    def _expected_display(self) -> str:
        d = self._direction
        if self.ANSWER_FORMAT == "decimal":     return self._dec_str
        if self.ANSWER_FORMAT == "percentage":  return f"{self._pct}%"
        return _fmt_frac(self._expected)

    def correct_history_text(self, expected: Fraction) -> str:
        return f"{self._given_display()} = {self._expected_display()}"

    def wrong_history_text(self, given: str) -> str:
        return f"{self._given_display()} ≠ {given}"
