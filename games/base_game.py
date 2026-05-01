"""
base_game.py
------------
Shared two-column layout for every mini-game.

Subclasses MUST implement:
  new_question()              — generate and store question state
  get_expected()              — return the correct answer (int or float)
  update_question_display()   — update question widget(s)
  correct_history_text(exp)   — one-line string for a correct attempt
  wrong_history_text(given)   — one-line string for a wrong attempt
  get_question_dict()         — dict for missed-question tracking (or None)
  _build_question_area(parent)— create the question widget(s)

Optional overrides:
  GAME_ID       — set to a unique string to enable the leaderboard
  ALLOW_DECIMAL — set True to accept decimal answers
  _add_extra_buttons(btn_row) — add extra buttons to the button row
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import datetime
import time as _time
import tkinter as tk
from tkinter import ttk

from .achievements import ACHIEVEMENTS, ACHIEVEMENTS_BY_ID
from .theme import theme
from .tutorials import TUTORIAL_REGISTRY


class BaseGame:
    TITLE         = "Game"
    SUBTITLE      = ""
    ALLOW_DECIMAL = False
    GAME_ID       = None   # set in subclass to enable leaderboard

    def __init__(self, parent, back_callback, ach_store, missed_store, scores_store,
                 sessions_store=None):
        self.parent        = parent
        self.back_callback = back_callback

        # Injected stores — profile-aware instances from profile_manager
        self._as = ach_store
        self._ms = missed_store
        self._ss = scores_store
        self._sess = sessions_store

        self.correct           = 0
        self.attempts          = 0
        self.streak            = 0
        self.history           = []
        self.feedback_after_id = None

        self._session_start = datetime.datetime.now()
        self._answer_times  = []   # timestamps of recent correct answers (for speed demon)
        self._popup_queue   = []   # pending achievement dicts to display

        # ── In-game helper (i)-button state (added v0.7.11) ───────────────
        # `_helper_used` flips True the first time the pupil opens the
        # tutorial modal mid-session. It gates the entire end-of-session
        # reward path: no points to the achievements store, no mastery
        # checks, no leaderboard prompt. Helper Discovered / Helper
        # Master are the only achievements still reachable.
        # `_helper_pause_seconds` accumulates real wall-clock seconds
        # spent inside the modal so session_minutes excludes them — the
        # Grind / speed-related stats stay honest.
        self._helper_used           = False
        self._helper_pause_seconds  = 0.0
        self._helper_pause_started  = None
        self._helper_modal          = None

        self._build_layout()
        self.new_question()
        self.update_question_display()
        self.update_stats()

    # ================================================================ layout

    def _build_layout(self):
        T = theme()
        # ── Top bar ──────────────────────────────────────────────────────────
        top = tk.Frame(self.parent, bg=T["bg"], padx=24, pady=10)
        top.pack(fill=tk.X)

        tk.Button(top, text="← Menu",
                  font=("Helvetica", 10), bg=T["bg"], fg=T["muted"],
                  relief="flat", bd=0, cursor="hand2",
                  activebackground="#f8fafc", activeforeground="#0f172a",
                  command=self._go_back).pack(side=tk.LEFT)

        if self.GAME_ID:
            tk.Button(top, text="🏆  Scores",
                      font=("Helvetica", 10), bg=T["bg"], fg=T["muted"],
                      relief="flat", bd=0, cursor="hand2",
                      activebackground="#f8fafc", activeforeground="#0f172a",
                      command=self._show_leaderboard).pack(side=tk.RIGHT)

        # In-game (i) helper — only shown for games with a tutorial
        # registered. Opening it pauses the session timer and flags
        # `_helper_used`, which zeroes out all end-of-session rewards
        # except Helper Discovered / Helper Master.
        if self.GAME_ID and self.GAME_ID in TUTORIAL_REGISTRY:
            tk.Button(top, text="ⓘ  Help",
                      font=("Helvetica", 11, "bold"),
                      bg=T["bg"], fg="#4f46e5",
                      relief="flat", bd=0, cursor="hand2",
                      activebackground="#f8fafc", activeforeground="#4338ca",
                      command=self._open_helper_modal).pack(side=tk.RIGHT,
                                                            padx=(0, 14))

        # ── Two-column body ───────────────────────────────────────────────────
        main = tk.Frame(self.parent, bg=T["bg"], padx=24, pady=4)
        main.pack(fill=tk.BOTH, expand=True)

        # RIGHT must be packed first so it reserves its fixed width before
        # the expanding left panel consumes all available space.
        right = tk.Frame(main, bg=T["bg"], width=370)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)

        left = tk.Frame(main, bg=T["bg"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 14))

        self._build_left(left)
        self._build_right(right)

    def _card(self, parent):
        T = theme()
        return tk.Frame(parent, bg=T["card_bg"],
                        highlightbackground=T["card_border"], highlightthickness=1)

    def _build_left(self, parent):
        T = theme()
        card = self._card(parent)
        card.pack(fill=tk.BOTH, expand=True)

        hdr = tk.Frame(card, bg=T["card_bg"], padx=24, pady=18)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=self.TITLE,
                 font=("Helvetica", 20, "bold"),
                 bg=T["card_bg"], fg=T["ink"]).pack(anchor="w")
        if self.SUBTITLE:
            tk.Label(hdr, text=self.SUBTITLE,
                     font=("Helvetica", 11), bg=T["card_bg"], fg=T["muted"]).pack(anchor="w", pady=(3, 0))

        tk.Frame(card, bg=T["card_border"], height=1).pack(fill=tk.X)

        body = tk.Frame(card, bg=T["card_bg"], padx=24, pady=14)
        body.pack(fill=tk.BOTH, expand=True)

        # ── TOP: question area — expands to fill available vertical space ──────
        q_area = tk.Frame(body, bg=T["card_bg"])
        q_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self._build_question_area(q_area)

        # ── BOTTOM: controls — compact, fixed at the bottom of the card ────────
        ctrl = tk.Frame(body, bg=T["card_bg"])
        ctrl.pack(fill=tk.X)

        # Answer entry
        self.answer_var = tk.StringVar()
        self.answer_var.trace("w", self._validate_input)
        self.answer_entry = tk.Entry(ctrl, textvariable=self.answer_var,
                                     font=("Helvetica", 22), justify="center",
                                     relief="solid", bd=1, fg=T["ink"],
                                     highlightthickness=0)
        self.answer_entry.pack(fill=tk.X, ipady=10, pady=(0, 10))
        self.answer_entry.bind("<Return>", self.handle_submit)
        self.answer_entry.focus_set()

        # Buttons
        btn_row = tk.Frame(ctrl, bg=T["card_bg"])
        btn_row.pack(fill=tk.X, pady=(0, 8))
        self._btn(btn_row, "Check Answer", self.handle_submit,
                  bg=T["btn_primary_bg"], fg=T["btn_primary_fg"]).pack(side=tk.LEFT, padx=(0, 8))
        self._btn(btn_row, "Skip", self.skip_question,
                  bg=T["card_bg"], fg=T["ink"], border=True).pack(side=tk.LEFT, padx=(0, 8))
        self._btn(btn_row, "↺  Reset", self.reset_stats,
                  bg=T["card_bg"], fg=T["ink"], border=True).pack(side=tk.LEFT)
        self._add_extra_buttons(btn_row)

        # Feedback strip
        self.feedback_frame = tk.Frame(ctrl, bg=T["card_bg"])
        self.feedback_frame.pack(fill=tk.X)
        self.feedback_label = tk.Label(self.feedback_frame, text="",
                                        font=("Helvetica", 12, "bold"),
                                        bg=T["card_bg"], fg="white",
                                        anchor="w", padx=14, pady=6)
        self.feedback_label.pack(fill=tk.X)

        # Scratch pad
        tk.Frame(ctrl, bg=T["card_border"], height=1).pack(fill=tk.X, pady=(6, 0))
        scratch_hdr = tk.Frame(ctrl, bg=T["card_bg"])
        scratch_hdr.pack(fill=tk.X, pady=(5, 3))
        tk.Label(scratch_hdr, text="✏  Scratch pad",
                 font=("Helvetica", 10, "bold"),
                 bg=T["card_bg"], fg=T["muted"]).pack(side=tk.LEFT)
        tk.Button(scratch_hdr, text="Clear",
                  font=("Helvetica", 8), bg=T["card_bg"], fg=T["dim"],
                  relief="flat", bd=0, cursor="hand2",
                  activebackground="white", activeforeground="#475569",
                  command=lambda: self._scratch.delete("1.0", tk.END)).pack(side=tk.RIGHT)
        self._scratch = tk.Text(ctrl, font=("Courier", 12),
                                bg="#fafaf7", fg="#1e293b",
                                relief="solid", bd=1,
                                highlightthickness=0,
                                wrap=tk.WORD,
                                height=5,
                                padx=10, pady=8,
                                insertbackground="#1e293b")
        self._scratch.pack(fill=tk.X, pady=(0, 4))

    def _build_right(self, parent):
        T = theme()
        card = self._card(parent)
        card.pack(fill=tk.BOTH, expand=True)

        hdr = tk.Frame(card, bg=T["card_bg"], padx=20, pady=16)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="Stats", font=("Helvetica", 18, "bold"),
                 bg=T["card_bg"], fg=T["ink"]).pack(anchor="w")
        tk.Frame(card, bg=T["card_border"], height=1).pack(fill=tk.X)

        body = tk.Frame(card, bg=T["card_bg"], padx=20, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        grid = tk.Frame(body, bg=T["card_bg"])
        grid.pack(fill=tk.X, pady=(0, 16))
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        self.lbl_correct  = self._stat_box(grid, "Correct",  "0",  0, 0)
        self.lbl_attempts = self._stat_box(grid, "Attempts", "0",  0, 1)
        self.lbl_streak   = self._stat_box(grid, "Streak",   "0",  1, 0)
        self.lbl_accuracy = self._stat_box(grid, "Accuracy", "0%", 1, 1)

        tk.Label(body, text="Accuracy progress",
                 font=("Helvetica", 10), bg=T["card_bg"], fg=T["muted"]).pack(anchor="w", pady=(0, 5))
        self.progress_var = tk.DoubleVar(value=0)
        ttk.Progressbar(body, variable=self.progress_var, maximum=100,
                        mode="determinate",
                        style="Custom.Horizontal.TProgressbar").pack(fill=tk.X, pady=(0, 16))

        tk.Label(body, text="Recent attempts",
                 font=("Helvetica", 11, "bold"), bg=T["card_bg"], fg="#334155").pack(anchor="w", pady=(0, 8))
        self.history_frame = tk.Frame(body, bg=T["card_bg"])
        self.history_frame.pack(fill=tk.BOTH, expand=True)

    # ================================================================ helpers

    def _btn(self, parent, text, command, bg, fg, border=False):
        T = theme()
        return tk.Button(parent, text=text, command=command,
                         font=("Helvetica", 11, "bold" if not border else "normal"),
                         bg=bg, fg=fg,
                         relief="solid" if border else "flat", bd=1 if border else 0,
                         padx=18, pady=7, cursor="hand2",
                         activebackground=bg, activeforeground=fg)

    def _stat_box(self, parent, label, value, row, col):
        T = theme()
        f = tk.Frame(parent, bg=T["bg"], padx=8, pady=10)
        f.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
        tk.Label(f, text=label, font=("Helvetica", 9),
                 bg=T["bg"], fg=T["muted"]).pack(anchor="w")
        val = tk.Label(f, text=value, font=("Helvetica", 20, "bold"),
                       bg=T["bg"], fg=T["ink"])
        val.pack(anchor="w")
        return val

    def _add_extra_buttons(self, btn_row):
        """Subclasses can override to append extra buttons."""
        pass

    # ================================================================ updates

    def update_stats(self):
        accuracy = (0 if self.attempts == 0
                    else round((self.correct / self.attempts) * 100))
        self.lbl_correct.configure(text=str(self.correct))
        self.lbl_attempts.configure(text=str(self.attempts))
        self.lbl_streak.configure(text=str(self.streak))
        self.lbl_accuracy.configure(text=f"{accuracy}%")
        self.progress_var.set(accuracy)
        self._refresh_history()

    def _refresh_history(self):
        T = theme()
        for w in self.history_frame.winfo_children():
            w.destroy()
        if not self.history:
            tk.Label(self.history_frame, text="No attempts yet.",
                     font=("Helvetica", 10), bg=T["bg"], fg=T["dim"],
                     padx=12, pady=10, anchor="w").pack(fill=tk.X)
        else:
            for item in self.history:
                bg = T["good_bg"] if item["ok"] else T["danger_bg"]
                fg = T["good"]    if item["ok"] else T["danger"]
                tk.Label(self.history_frame, text=item["text"],
                         font=("Helvetica", 10), bg=bg, fg=fg,
                         padx=12, pady=7, anchor="w").pack(fill=tk.X, pady=2)

    def show_feedback(self, kind, text):
        T = theme()
        bg, fg = (T["good_bg"], T["good"]) if kind == "correct" else (T["danger_bg"], T["danger"])
        self.feedback_frame.configure(bg=bg)
        self.feedback_label.configure(text=text, bg=bg, fg=fg)

    def clear_feedback(self):
        T = theme()
        self.feedback_frame.configure(bg=T["card_bg"])
        self.feedback_label.configure(text="", bg=T["card_bg"])

    # ================================================================ input

    def _validate_input(self, *_):
        v = self.answer_var.get()
        if self.ALLOW_DECIMAL:
            filtered = ""
            dot_seen = False
            for c in v:
                if c.isdigit():
                    filtered += c
                elif c in (".", ",") and not dot_seen:
                    filtered += "."
                    dot_seen = True
        else:
            filtered = "".join(c for c in v if c.isdigit())
        if v != filtered:
            self.answer_var.set(filtered)

    def _parse_answer(self, raw):
        raw = raw.replace(",", ".")
        return float(raw) if self.ALLOW_DECIMAL else int(raw)

    def _answers_match(self, given, expected):
        if self.ALLOW_DECIMAL:
            return abs(float(given) - float(expected)) < 0.0001
        return int(given) == int(expected)

    # ================================================================ actions

    def handle_submit(self, event=None):
        raw = self.answer_var.get().strip()
        if not raw or raw in (".", ","):
            return
        try:
            given = self._parse_answer(raw)
        except ValueError:
            return

        expected = self.get_expected()
        self.attempts += 1

        if self._answers_match(given, expected):
            self.correct += 1
            self.streak  += 1
            self._answer_times.append(_time.time())
            self.history.insert(0, {"text": self.correct_history_text(expected), "ok": True})
            self.history = self.history[:8]
            self.show_feedback("correct", "✓  Correct!  Next one.")
            self.update_stats()
            # Check live achievements (streaks, speed, first correct)
            self._check_live_achievements()
            if self.feedback_after_id:
                self.parent.after_cancel(self.feedback_after_id)
            self.feedback_after_id = self.parent.after(550, self._auto_next)
        else:
            self.streak = 0
            self.history.insert(0, {"text": self.wrong_history_text(raw), "ok": False})
            self.history = self.history[:8]
            self.show_feedback("wrong", "✗  Not quite. Try again.")
            self.answer_var.set("")
            self.update_stats()
            q = self.get_question_dict()
            if q is not None:
                self._ms.add(q)

    def _auto_next(self):
        self.feedback_after_id = None
        self.new_question()
        self.answer_var.set("")
        self.clear_feedback()
        self.update_question_display()
        self.answer_entry.focus_set()

    def skip_question(self):
        if self.feedback_after_id:
            self.parent.after_cancel(self.feedback_after_id)
            self.feedback_after_id = None
        self.new_question()
        self.answer_var.set("")
        self.clear_feedback()
        self.update_question_display()
        self.answer_entry.focus_set()

    def reset_stats(self):
        if self.feedback_after_id:
            self.parent.after_cancel(self.feedback_after_id)
            self.feedback_after_id = None
        self.correct  = 0
        self.attempts = 0
        self.streak   = 0
        self.history  = []
        self._answer_times = []
        self.answer_var.set("")
        self.clear_feedback()
        self.new_question()
        self.update_question_display()
        self.update_stats()
        self.answer_entry.focus_set()

    def _go_back(self):
        if self.feedback_after_id:
            self.parent.after_cancel(self.feedback_after_id)
            self.feedback_after_id = None

        # Commit stats + check end achievements (non-blocking popups)
        newly_earned = self._commit_and_check()
        if newly_earned:
            self._show_popups_queued(newly_earned)

        # Helper-used sessions never prompt for a leaderboard entry —
        # the run is reward-free by design and must not pollute the top-10.
        if self.GAME_ID and self.attempts > 0 and not self._helper_used:
            self._prompt_score_entry()
        else:
            self.back_callback()

    # ============================================================ in-game helper

    def _open_helper_modal(self):
        """Open the current game's tutorial in a modal Toplevel.

        Pauses the session timer (wall-clock seconds spent in the modal
        are subtracted from session_minutes at end of session) and flips
        `_helper_used` True. Helper-used sessions:
          * Award zero points
          * Skip mastery / streak / milestone end achievements
          * Do not prompt for a leaderboard entry
          * Are still logged to sessions_store with helper_used=True
          * Can still earn Helper Discovered (>=1 use) and Helper Master
            (>=10 lifetime uses).
        """
        T = theme()
        if self._helper_modal is not None:
            try:
                self._helper_modal.lift()
            except Exception:
                pass
            return

        mod = TUTORIAL_REGISTRY.get(self.GAME_ID)
        if mod is None:
            return

        # Mark helper used + bump lifetime counter immediately so the
        # achievement check at modal-close has the new value to read.
        self._helper_used = True
        try:
            self._as.record_helper_use()
        except Exception:
            pass

        # Pause any pending feedback redirect — answer auto-advance must
        # not fire while the pupil is reading the slides.
        if self.feedback_after_id:
            self.parent.after_cancel(self.feedback_after_id)
            self.feedback_after_id = None

        # Pause session timer.
        self._helper_pause_started = _time.time()

        # Build the Toplevel modal.
        from .tutorials.slideshow_frame import (
            SlideshowFrame, award_tutorial_achievements,
        )
        from .achievements import GAME_NAMES

        root = self.parent.winfo_toplevel()
        root.update_idletasks()

        win = tk.Toplevel(root)
        win.title("Help")
        win.transient(root)
        win.grab_set()
        win.configure(bg=T["bg"])

        # Size to comfortably hold the SlideshowFrame's 720×340 canvas
        # plus its surrounding card / nav. Mirrors the floor used by
        # SlideshowFrame itself.
        w, h = 1280, 720
        try:
            cx = root.winfo_x() + root.winfo_width()  // 2
            cy = root.winfo_y() + root.winfo_height() // 2
            win.geometry(f"{w}x{h}+{max(cx - w // 2, 0)}+{max(cy - h // 2, 0)}")
        except Exception:
            win.geometry(f"{w}x{h}")

        host = tk.Frame(win, bg=T["bg"])
        host.pack(fill=tk.BOTH, expand=True)

        self._helper_modal = win
        # WM-close (X button) routes through our close handler so timer
        # bookkeeping always runs.
        win.protocol("WM_DELETE_WINDOW", self._close_helper_modal)

        # Record tutorial-viewed so the Bookworm / Scholar achievements
        # remain reachable from the helper path — opening a tutorial
        # really did happen, even if it was via the in-game shortcut.
        try:
            self._as.record_tutorial_viewed(self.GAME_ID)
            award_tutorial_achievements(host, self._as)
        except Exception:
            pass

        SlideshowFrame(
            host,
            back_callback = self._close_helper_modal,
            title         = getattr(mod, "TITLE", GAME_NAMES.get(self.GAME_ID, "Help")),
            lead          = getattr(mod, "LEAD", ""),
            slides        = getattr(mod, "SLIDES", []),
            examples      = getattr(mod, "EXAMPLES", [{}]),
            ach_store     = self._as,
            game_id       = self.GAME_ID,
        )

    def _close_helper_modal(self):
        """Tear down the helper modal, resume timer, fire helper achievements."""
        # Resume timer.
        if self._helper_pause_started is not None:
            self._helper_pause_seconds += max(
                0.0, _time.time() - self._helper_pause_started
            )
            self._helper_pause_started = None

        win = self._helper_modal
        self._helper_modal = None
        if win is not None:
            try:
                win.grab_release()
            except Exception:
                pass
            try:
                win.destroy()
            except Exception:
                pass

        # Fire any newly-earned helper achievements with the standard toast.
        self._check_helper_achievements()

        # Restore focus to the answer entry so the pupil can keep typing.
        try:
            self.answer_entry.focus_set()
        except Exception:
            pass

    def _check_helper_achievements(self):
        """Run `when='helper'` achievements and surface popups."""
        try:
            stats = self._as.get_stats()
        except Exception:
            return
        newly_earned = []
        for ach in ACHIEVEMENTS:
            if ach.get("when") != "helper":
                continue
            if self._as.has(ach["id"]):
                continue
            try:
                if ach["check"](stats, {}):
                    if self._as.earn(ach["id"], ach["points"]):
                        newly_earned.append(ach)
            except Exception:
                continue
        if newly_earned:
            self._show_popups_queued(newly_earned)

    # ============================================================ achievements

    def _check_live_achievements(self):
        """Check streak / speed / first-correct achievements mid-game."""
        # Helper-used sessions earn zero further achievements after the
        # modal is opened — anything earned beforehand stays banked, but
        # the rest of the session is reward-free by design.
        if self._helper_used:
            return

        now     = _time.time()
        recent  = [t for t in self._answer_times if now - t <= 60.0]
        speed_ok = len(recent) >= 10

        ctx = {
            "session_streak":  self.streak,
            "speed_demon":     speed_ok,
            "session_correct": self.correct,
        }
        stats = self._as.get_stats()

        newly_earned = []
        for ach in ACHIEVEMENTS:
            if ach.get("when") != "live":
                continue
            if self._as.has(ach["id"]):
                continue
            try:
                if ach["check"](stats, ctx):
                    if self._as.earn(ach["id"], ach["points"]):
                        newly_earned.append(ach)
            except Exception:
                pass

        if newly_earned:
            self._show_popups_queued(newly_earned)

    def _commit_and_check(self):
        """Commit session stats to store and check end achievements.
        Returns list of newly earned achievement dicts.

        Helper-used sessions short-circuit the achievements-store commit
        and the end achievement sweep — zero points, no mastery unlock,
        no leaderboard contribution. The session is still appended to
        sessions_store with helper_used=True so the parent PDF / stats
        screen still see the engagement.
        """
        if self.attempts == 0:
            return []

        accuracy        = round((self.correct / self.attempts) * 100)
        now             = datetime.datetime.now()
        # Subtract the wall-clock seconds the modal was open so a long
        # tutorial read does not falsely unlock The Grind (>=30 min).
        elapsed = (now - self._session_start).total_seconds()
        session_minutes = max(0.0,
                              (elapsed - self._helper_pause_seconds) / 60.0)

        if not self._helper_used:
            self._as.record_session(
                self.GAME_ID,
                self.correct, self.attempts, accuracy, self.streak,
                now.date().isoformat(), now.hour,
            )

        # Append a full history record for the Progress & Stats screen
        if self._sess is not None:
            try:
                self._sess.record(
                    game_id=self.GAME_ID or "",
                    correct=self.correct,
                    attempts=self.attempts,
                    accuracy=accuracy,
                    streak=self.streak,
                    minutes=session_minutes,
                    ts=self._session_start,
                    helper_used=self._helper_used,
                )
            except Exception:
                pass  # never let logging crash the game

        # Helper-used sessions skip every `when="end"` achievement.
        # Helper Discovered / Helper Master fire from the modal-close
        # path (`_check_helper_achievements`) — there is nothing else
        # to award here.
        if self._helper_used:
            return []

        stats = self._as.get_stats()
        ctx   = {"session_minutes": session_minutes}

        newly_earned = []
        for ach in ACHIEVEMENTS:
            if ach.get("when") != "end":
                continue
            if self._as.has(ach["id"]):
                continue
            try:
                if ach["check"](stats, ctx):
                    if self._as.earn(ach["id"], ach["points"]):
                        newly_earned.append(ach)
            except Exception:
                pass

        return newly_earned

    def _show_achievement_popup(self, ach, slot=0):
        """Display a non-blocking toast popup for an earned achievement."""
        T = theme()
        try:
            root = self.parent.winfo_toplevel()
            root.update_idletasks()

            w, h    = 300, 82
            margin  = 16
            spacing = h + 6
            rx = root.winfo_x() + root.winfo_width()  - w - margin
            ry = root.winfo_y() + root.winfo_height() - margin - h - slot * spacing

            popup = tk.Toplevel(root)
            popup.overrideredirect(True)
            popup.attributes("-topmost", True)
            popup.configure(bg="#1e293b")
            popup.geometry(f"{w}x{h}+{rx}+{ry}")

            f = tk.Frame(popup, bg="#1e293b", padx=14, pady=10)
            f.pack(fill=tk.BOTH, expand=True)

            tk.Label(f, text="  Achievement Unlocked!",
                     font=("Helvetica", 8, "bold"),
                     bg="#1e293b", fg="#f59e0b").pack(anchor="w")
            tk.Label(f, text=f"  {ach['icon']}  {ach['name']}",
                     font=("Helvetica", 11, "bold"),
                     bg="#1e293b", fg="white").pack(anchor="w")
            tk.Label(f, text=f"  +{ach['points']} points",
                     font=("Helvetica", 9),
                     bg="#1e293b", fg=T["dim"]).pack(anchor="w")

            popup.after(3500, popup.destroy)
        except Exception:
            pass   # never let a popup crash the game

    def _show_popups_queued(self, achievements):
        """Show a list of achievement popups, staggered and stacked."""
        for i, ach in enumerate(achievements):
            self.parent.after(i * 600,
                              lambda a=ach, s=i: self._show_achievement_popup(a, s))

    # ============================================================= leaderboard

    def _prompt_score_entry(self):
        """Show name-entry dialog if the session qualifies for top-10."""
        T = theme()
        accuracy = round((self.correct / self.attempts) * 100) if self.attempts else 0
        if not self._ss.qualifies(self.GAME_ID, self.correct, accuracy, self.streak):
            self.back_callback()
            return

        root = self.parent.winfo_toplevel()
        root.update_idletasks()
        cx = root.winfo_x() + root.winfo_width()  // 2
        cy = root.winfo_y() + root.winfo_height() // 2

        dlg = tk.Toplevel(self.parent)
        dlg.title("New High Score!")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.geometry(f"420x210+{cx - 210}+{cy - 105}")
        dlg.configure(bg=T["card_bg"])

        f = tk.Frame(dlg, bg=T["card_bg"], padx=28, pady=24)
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text="You made the leaderboard! 🎉",
                 font=("Helvetica", 14, "bold"), bg=T["card_bg"], fg=T["ink"]).pack(anchor="w")
        tk.Label(f, text=f"{self.correct} correct  ·  {accuracy}% accuracy  ·  streak {self.streak}",
                 font=("Helvetica", 10), bg=T["card_bg"], fg=T["muted"]).pack(anchor="w", pady=(4, 16))

        tk.Label(f, text="Your name:", font=("Helvetica", 10, "bold"),
                 bg=T["card_bg"], fg=T["ink"]).pack(anchor="w")
        name_var = tk.StringVar()
        name_entry = tk.Entry(f, textvariable=name_var, font=("Helvetica", 13),
                              relief="solid", bd=1)
        name_entry.pack(fill=tk.X, ipady=6, pady=(4, 16))
        name_entry.focus_set()

        def _save(event=None):
            name = name_var.get().strip() or "Anonymous"
            self._ss.add_score(self.GAME_ID, {
                "name":     name,
                "correct":  self.correct,
                "attempts": self.attempts,
                "accuracy": accuracy,
                "streak":   self.streak,
                "date":     datetime.date.today().isoformat(),
            })
            # Record leaderboard position and check LB achievements
            scores = self._ss.get_scores(self.GAME_ID)
            for i, sc in enumerate(scores):
                if sc["name"] == name and sc["correct"] == self.correct:
                    self._as.record_lb_position(self.GAME_ID, i + 1)
                    break
            lb_earned = []
            for ach_id in ("lb_top3", "lb_top1", "lb_triple"):
                if self._as.has(ach_id):
                    continue
                ach = ACHIEVEMENTS_BY_ID.get(ach_id)
                if ach and ach["check"](self._as.get_stats(), {}):
                    if self._as.earn(ach_id, ach["points"]):
                        lb_earned.append(ach)
            if lb_earned:
                self._show_popups_queued(lb_earned)
            dlg.destroy()
            self.back_callback()

        def _skip():
            dlg.destroy()
            self.back_callback()

        name_entry.bind("<Return>", _save)

        btn_row = tk.Frame(f, bg=T["card_bg"])
        btn_row.pack(anchor="e")
        tk.Button(btn_row, text="Save", command=_save,
                  font=("Helvetica", 11, "bold"), bg=T["btn_primary_bg"], fg=T["btn_primary_fg"],
                  relief="flat", padx=16, pady=6, cursor="hand2",
                  activebackground="#1e293b", activeforeground="white").pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(btn_row, text="Skip", command=_skip,
                  font=("Helvetica", 11), bg=T["card_bg"], fg=T["muted"],
                  relief="solid", bd=1, padx=16, pady=6, cursor="hand2").pack(side=tk.LEFT)

    def _show_leaderboard(self):
        """Display a top-10 table in a popup window."""
        T = theme()
        scores = self._ss.get_scores(self.GAME_ID)

        root = self.parent.winfo_toplevel()
        root.update_idletasks()
        cx = root.winfo_x() + root.winfo_width()  // 2
        cy = root.winfo_y() + root.winfo_height() // 2

        win = tk.Toplevel(self.parent)
        win.title("Leaderboard")
        win.grab_set()
        win.configure(bg=T["bg"])
        win.geometry(f"560x420+{cx - 280}+{cy - 210}")
        win.resizable(False, False)

        hdr = tk.Frame(win, bg=T["btn_primary_bg"], padx=20, pady=14)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=f"🏆  {self.TITLE}",
                 font=("Helvetica", 13, "bold"), bg=T["btn_primary_bg"], fg=T["btn_primary_fg"]).pack(anchor="w")

        if not scores:
            tk.Label(win, text="No scores yet — play to set the first record!",
                     font=("Helvetica", 12), bg=T["bg"], fg=T["muted"]).pack(expand=True)
        else:
            col_frame = tk.Frame(win, bg=T["card_border"], padx=16, pady=6)
            col_frame.pack(fill=tk.X)
            for text, width in [("#", 4), ("Name", 18), ("Correct", 9),
                                 ("Accuracy", 10), ("Streak", 8), ("Date", 12)]:
                tk.Label(col_frame, text=text, width=width, anchor="w",
                         font=("Helvetica", 9, "bold"),
                         bg=T["card_border"], fg=T["muted"]).pack(side=tk.LEFT)

            rows = tk.Frame(win, bg=T["card_bg"])
            rows.pack(fill=tk.BOTH, expand=True)

            medals = ["🥇", "🥈", "🥉"] + [f" {i}" for i in range(4, 11)]
            for i, s in enumerate(scores):
                # Top spot gets the highlight surface; the rest alternate
                # between card_bg and soft so dark/matrix themes aren't
                # rendered as black/light-grey zebra stripes.
                if i == 0:
                    bg = T["highlight_bg"]
                elif i % 2 == 0:
                    bg = T["card_bg"]
                else:
                    bg = T["soft"]
                row = tk.Frame(rows, bg=bg, padx=16, pady=7)
                row.pack(fill=tk.X)
                for val, width in [
                    (medals[i], 4),
                    (s["name"],              18),
                    (str(s["correct"]),       9),
                    (f"{s['accuracy']}%",    10),
                    (str(s.get("streak", 0)), 8),
                    (s.get("date", ""),      12),
                ]:
                    tk.Label(row, text=val, width=width, anchor="w",
                             font=("Helvetica", 10), bg=bg, fg=T["ink"]).pack(side=tk.LEFT)

        tk.Button(win, text="Close", command=win.destroy,
                  font=("Helvetica", 11), bg=T["card_bg"], fg=T["muted"],
                  relief="solid", bd=1, padx=20, pady=6, cursor="hand2").pack(pady=12)

    # ================================================= abstract — must override
    def new_question(self):             raise NotImplementedError
    def get_expected(self):             raise NotImplementedError
    def update_question_display(self):  raise NotImplementedError
    def correct_history_text(self, e):  raise NotImplementedError
    def wrong_history_text(self, g):    raise NotImplementedError
    def get_question_dict(self):        return None
    def _build_question_area(self, p):  raise NotImplementedError
