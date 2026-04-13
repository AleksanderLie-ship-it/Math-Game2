"""
practice_missed.py
------------------
Review game that draws exclusively from the student's missed-question store.

Correct answer  -> question removed from the store (and from the session queue).
Wrong answer    -> question stays in the store; the student must try again.
Skip            -> question moves to the back of the session queue (stays in store).
Wipe All button -> clears the entire store after a confirmation prompt.

When the queue is exhausted the game shows a completion screen.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import random
import tkinter as tk
from tkinter import messagebox

from .base_game          import BaseGame
from .missed_store       import store as _ms
from .achievements_store import store as _as
from .achievements       import ACHIEVEMENTS_BY_ID


def _fmt(n):
    """Drop the '.0' from whole floats; keep other decimals as-is."""
    if isinstance(n, float) and n == int(n):
        return str(int(n))
    return str(n)


class PracticeMissed(BaseGame):
    TITLE         = "Practice — Missed Questions"
    SUBTITLE      = "Work through your wrong answers until the list is empty."
    ALLOW_DECIMAL = True
    GAME_ID       = None   # no leaderboard for review mode

    # ------------------------------------------------------------------ init

    def __init__(self, parent, back_callback):
        # Set up queue BEFORE super().__init__ calls new_question()
        self._queue: list         = list(_ms.get_all())
        random.shuffle(self._queue)
        self._current_q: dict | None = None
        self._queue_empty: bool      = len(self._queue) == 0
        self._pending_open_ach       = None   # awarded on open, shown after UI builds

        # Award "Facing Fears" the first time Practice Missed is opened
        if not _as.get_stats().get("missed_attempted", False):
            _as.set_stat("missed_attempted", True)
            ach = ACHIEVEMENTS_BY_ID.get("missed_attempted")
            if ach and _as.earn(ach["id"], ach["points"]):
                self._pending_open_ach = ach

        super().__init__(parent, back_callback)

        # Show the open-achievement popup now that the UI is ready
        if self._pending_open_ach:
            self.parent.after(500, lambda: self._show_achievement_popup(self._pending_open_ach))

    # ---------------------------------------------------- question area

    def _build_question_area(self, parent):
        self.remaining_label = tk.Label(
            parent, text="", font=("Helvetica", 10),
            bg="white", fg="#64748b"
        )
        self.remaining_label.pack(anchor="w", pady=(0, 6))

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

    def _add_extra_buttons(self, btn_row):
        self._btn(btn_row, "🗑  Wipe All", self._wipe_all,
                  bg="white", fg="#b91c1c", border=True).pack(side=tk.LEFT, padx=(8, 0))

    # ---------------------------------------------------------------- abstract

    def new_question(self):
        if self._queue:
            self._current_q   = self._queue[0]
            self._queue_empty = False
        else:
            self._current_q   = None
            self._queue_empty = True

    def get_expected(self):
        return self._current_q["expected"] if self._current_q else 0

    def update_question_display(self):
        if self._queue_empty:
            n = _ms.count()
            if n == 0:
                self.question_label.configure(text="All cleared!")
                self.remaining_label.configure(
                    text="Every missed question answered correctly. Returning to menu..."
                )
                self.answer_entry.configure(state="disabled")
                # Auto-return after 3 seconds (only schedule once)
                if not getattr(self, "_return_scheduled", False):
                    self._return_scheduled = True
                    self.parent.after(3000, self._go_back)
            else:
                self.question_label.configure(text="No missed questions yet.")
                self.remaining_label.configure(text="")
                self.answer_entry.configure(state="disabled")
        else:
            self.answer_entry.configure(state="normal")
            q   = self._current_q
            cnt = _ms.count()
            self.remaining_label.configure(
                text=f"{cnt} question{'s' if cnt != 1 else ''} remaining"
            )
            self.question_label.configure(text=f"{q['a']} {q['op']} {q['b']}")

    def get_question_dict(self):
        return None   # never re-add to missed from within practice mode

    def correct_history_text(self, expected):
        if not self._current_q:
            return ""
        q = self._current_q
        return f"{q['a']} {q['op']} {q['b']} = {_fmt(expected)}"

    def wrong_history_text(self, given):
        if not self._current_q:
            return ""
        q = self._current_q
        return f"{q['a']} {q['op']} {q['b']} != {_fmt(float(given))}"

    # -------------------------------------------------- custom submit

    def handle_submit(self, event=None):
        """Fully overrides base: removes from store on correct, never re-adds."""
        if self._queue_empty or self._current_q is None:
            return

        raw = self.answer_var.get().strip()
        if not raw or raw in (".", ","):
            return
        try:
            given = self._parse_answer(raw)
        except ValueError:
            return

        expected   = self.get_expected()
        self.attempts += 1

        if self._answers_match(given, expected):
            self.correct += 1
            self.streak  += 1
            _ms.remove(self._current_q)
            self._queue.pop(0)

            # Achievement: Resilient (first missed question answered correctly)
            newly_ach = []
            if not _as.get_stats().get("missed_resilient", False):
                _as.set_stat("missed_resilient", True)
                ach = ACHIEVEMENTS_BY_ID.get("missed_resilient")
                if ach and _as.earn(ach["id"], ach["points"]):
                    newly_ach.append(ach)

            self.history.insert(0, {"text": self.correct_history_text(expected), "ok": True})
            self.history = self.history[:8]

            # Achievement: Clean Slate (all cleared)
            if not self._queue:
                if not _as.get_stats().get("missed_cleared", False):
                    _as.set_stat("missed_cleared", True)
                    ach = ACHIEVEMENTS_BY_ID.get("missed_cleared")
                    if ach and _as.earn(ach["id"], ach["points"]):
                        newly_ach.append(ach)
                self.show_feedback("correct", "✓  All questions cleared!  Great work!")
            else:
                self.show_feedback("correct", "✓  Correct! Removed from missed list.")

            self.update_stats()
            if newly_ach:
                self._show_popups_queued(newly_ach)

            if self.feedback_after_id:
                self.parent.after_cancel(self.feedback_after_id)
            self.feedback_after_id = self.parent.after(700, self._auto_next)
        else:
            self.streak = 0
            self.history.insert(0, {"text": self.wrong_history_text(raw), "ok": False})
            self.history = self.history[:8]
            self.show_feedback("wrong", "✗  Not quite. Try again.")
            self.answer_var.set("")
            self.update_stats()

    # --------------------------------------------------- custom skip

    def skip_question(self):
        """Move current question to end of queue (stays in store)."""
        if self.feedback_after_id:
            self.parent.after_cancel(self.feedback_after_id)
            self.feedback_after_id = None
        if self._queue and not self._queue_empty:
            self._queue.append(self._queue.pop(0))
        self.new_question()
        self.answer_var.set("")
        self.clear_feedback()
        self.update_question_display()
        self.answer_entry.focus_set()

    # -------------------------------------------------- custom reset

    def reset_stats(self):
        self._return_scheduled = False
        if self.feedback_after_id:
            self.parent.after_cancel(self.feedback_after_id)
            self.feedback_after_id = None
        self.correct  = 0
        self.attempts = 0
        self.streak   = 0
        self.history  = []
        self._queue        = list(_ms.get_all())
        random.shuffle(self._queue)
        self._queue_empty  = len(self._queue) == 0
        self._current_q    = None
        self.answer_var.set("")
        self.clear_feedback()
        self.new_question()
        self.update_question_display()
        self.update_stats()
        self.answer_entry.focus_set()

    # --------------------------------------------------------- wipe all

    def _wipe_all(self):
        self._return_scheduled = False
        if not messagebox.askyesno(
            "Wipe All",
            f"This will permanently delete all {_ms.count()} missed question(s).\n\nAre you sure?",
            icon="warning",
        ):
            return
        _ms.clear()
        self._queue       = []
        self._queue_empty = True
        self._current_q   = None
        self.answer_var.set("")
        self.clear_feedback()
        self.update_question_display()
        self.update_stats()
