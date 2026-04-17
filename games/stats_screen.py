"""
stats_screen.py
---------------
Progress & Stats screen for the active profile.

Sections:
  1. Summary tiles      — total correct, days played, best streak, total minutes
  2. 14-day bar chart   — questions answered per day (Canvas drawn)
  3. Accuracy trend     — one sparkline per game mode that has data
  4. Per-game table     — sessions, total correct, avg accuracy, best streak
  5. Highlights         — latest earned achievements + headline stats
  6. Export             — save a one-page PDF summary (via pdf_export.py)

All charts are rendered on tk.Canvas. No external dependencies.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from .achievements import (
    ACHIEVEMENTS, ACHIEVEMENTS_BY_ID, GAME_IDS, GAME_NAMES, GAME_SHORT,
)
from . import pdf_export


# ── Palette ────────────────────────────────────────────────────────────────────

BG           = "#f8fafc"
INK          = "#0f172a"
MUTED        = "#64748b"
DIM          = "#94a3b8"
FAINT        = "#cbd5e1"
BAR          = "#0f172a"
BAR_GOOD     = "#15803d"
ACCENT       = "#4f46e5"
CARD_BORDER  = "#e2e8f0"
SOFT         = "#f1f5f9"


class StatsScreen:
    """Full-page Progress & Stats view. Mounted into a parent frame."""

    def __init__(self, parent, back_callback,
                 profile_name, ach_store, sessions_store,
                 scores_store=None):
        self.parent         = parent
        self.back_callback  = back_callback
        self.profile_name   = profile_name
        self._as            = ach_store
        self._sess          = sessions_store
        self._ss            = scores_store

        self._build()

    # ================================================================ build

    def _build(self):
        # ── Top bar ──────────────────────────────────────────────────────
        top = tk.Frame(self.parent, bg=BG, padx=24, pady=10)
        top.pack(fill=tk.X)

        tk.Button(top, text="← Menu",
                  font=("Helvetica", 10), bg=BG, fg="#475569",
                  relief="flat", bd=0, cursor="hand2",
                  activebackground=BG, activeforeground=INK,
                  command=self.back_callback).pack(side=tk.LEFT)

        tk.Button(top, text="⬇  Export PDF",
                  font=("Helvetica", 10, "bold"),
                  bg=INK, fg="white",
                  relief="flat", bd=0, padx=14, pady=6, cursor="hand2",
                  activebackground="#1e293b", activeforeground="white",
                  command=self._export_pdf).pack(side=tk.RIGHT)

        # ── Scrollable body ──────────────────────────────────────────────
        outer = tk.Frame(self.parent, bg=BG)
        outer.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(outer, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0,
                           yscrollcommand=vsb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=canvas.yview)

        body = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win_id, width=e.width))

        # mousewheel (local to this screen)
        def _wheel(e):
            try:
                canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
            except Exception:
                pass
        canvas.bind_all("<MouseWheel>", _wheel)

        # ── Header ───────────────────────────────────────────────────────
        hdr = tk.Frame(body, bg=BG, padx=48, pady=28)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="📊  Progress & Stats",
                 font=("Helvetica", 28, "bold"),
                 bg=BG, fg=INK).pack(anchor="w")
        tk.Label(hdr, text=f"A summary of {self.profile_name}'s practice so far.",
                 font=("Helvetica", 12), bg=BG, fg=MUTED).pack(anchor="w", pady=(4, 0))

        # ── Sections ─────────────────────────────────────────────────────
        self._section_summary_tiles(body)
        self._section_bar_chart(body)
        self._section_accuracy_trends(body)
        self._section_per_game_table(body)
        self._section_highlights(body)

        # ── Footer spacer ────────────────────────────────────────────────
        tk.Frame(body, bg=BG, height=30).pack()

    # ================================================================ sections

    def _section_title(self, parent, text, sub=""):
        wrap = tk.Frame(parent, bg=BG, padx=48)
        wrap.pack(fill=tk.X, pady=(8, 8))
        tk.Label(wrap, text=text,
                 font=("Helvetica", 14, "bold"),
                 bg=BG, fg=INK).pack(anchor="w")
        if sub:
            tk.Label(wrap, text=sub,
                     font=("Helvetica", 10),
                     bg=BG, fg=MUTED).pack(anchor="w", pady=(2, 0))

    def _card(self, parent, padx=48, pady=(0, 24)):
        wrap = tk.Frame(parent, bg=BG, padx=padx)
        wrap.pack(fill=tk.X, pady=pady)
        card = tk.Frame(wrap, bg="white",
                        highlightbackground=CARD_BORDER, highlightthickness=1)
        card.pack(fill=tk.X)
        inner = tk.Frame(card, bg="white", padx=22, pady=20)
        inner.pack(fill=tk.BOTH, expand=True)
        return inner

    # ---- 1. Summary tiles --------------------------------------------------

    def _section_summary_tiles(self, parent):
        stats = self._as.get_stats()
        total_correct     = stats.get("total_correct", 0)
        days_played       = len(stats.get("days_played", []))
        best_streak       = stats.get("best_streak_ever", 0)
        total_minutes     = self._sess.total_minutes() if self._sess else 0.0

        wrap = tk.Frame(parent, bg=BG, padx=48)
        wrap.pack(fill=tk.X, pady=(4, 20))

        row = tk.Frame(wrap, bg=BG)
        row.pack(fill=tk.X)
        for i in range(4):
            row.columnconfigure(i, weight=1)

        tiles = [
            ("Total correct",  f"{total_correct:,}",      "✓"),
            ("Days played",    f"{days_played}",          "📅"),
            ("Best streak",    f"{best_streak}",          "🔥"),
            ("Time practising", self._fmt_minutes(total_minutes), "⏱"),
        ]
        for col, (label, value, icon) in enumerate(tiles):
            pad = (0, 12) if col < 3 else (0, 0)
            tile = tk.Frame(row, bg="white",
                            highlightbackground=CARD_BORDER, highlightthickness=1)
            tile.grid(row=0, column=col, sticky="nsew", padx=pad)
            inner = tk.Frame(tile, bg="white", padx=18, pady=16)
            inner.pack(fill=tk.BOTH, expand=True)
            tk.Label(inner, text=f"{icon}  {label}",
                     font=("Helvetica", 10),
                     bg="white", fg=MUTED).pack(anchor="w")
            tk.Label(inner, text=value,
                     font=("Helvetica", 24, "bold"),
                     bg="white", fg=INK).pack(anchor="w", pady=(4, 0))

    # ---- 2. 14-day bar chart ----------------------------------------------

    def _section_bar_chart(self, parent):
        self._section_title(parent,
                            "Questions per day",
                            "Last 14 days. Green bars show correct answers; the full height is total attempts.")

        inner = self._card(parent)
        daily = self._sess.daily_counts(14) if self._sess else []

        if not daily or all(a == 0 for _, _, a in daily):
            tk.Label(inner, text="No activity yet. Play a few sessions and this will light up.",
                     font=("Helvetica", 10), bg="white", fg=DIM).pack(anchor="w")
            return

        w, h = 900, 220
        canvas = tk.Canvas(inner, width=w, height=h, bg="white",
                           highlightthickness=0)
        canvas.pack(fill=tk.X)
        self._draw_bar_chart(canvas, daily, w, h)

    def _draw_bar_chart(self, canvas, daily, w, h):
        """daily: list[(date_iso, correct, attempts)]"""
        n          = len(daily)
        margin_l   = 38
        margin_r   = 14
        margin_t   = 10
        margin_b   = 34
        plot_w     = w - margin_l - margin_r
        plot_h     = h - margin_t - margin_b

        max_val = max((a for _, _, a in daily), default=1)
        # Round up max to a "nice" number
        def _nice_max(v):
            if v <= 5:    return 5
            if v <= 10:   return 10
            if v <= 25:   return 25
            if v <= 50:   return 50
            if v <= 100:  return 100
            # next multiple of 50
            return int(((v + 49) // 50) * 50)
        y_max = _nice_max(max_val)

        # Y axis lines (4 gridlines)
        for i in range(5):
            y = margin_t + plot_h * (1 - i / 4)
            canvas.create_line(margin_l, y, margin_l + plot_w, y,
                               fill=SOFT, width=1)
            val = int(y_max * i / 4)
            canvas.create_text(margin_l - 6, y,
                               text=str(val), anchor="e",
                               font=("Helvetica", 8), fill=DIM)

        # Bars
        gap       = 6
        bar_w     = max(4, (plot_w - gap * (n - 1)) / n - 0)
        x         = margin_l
        today_iso = datetime.date.today().isoformat()

        for i, (date_iso, correct, attempts) in enumerate(daily):
            bar_h_total   = (attempts / y_max) * plot_h if y_max else 0
            bar_h_correct = (correct  / y_max) * plot_h if y_max else 0
            x0 = x
            x1 = x + bar_w
            y_base = margin_t + plot_h

            # total attempts (light)
            if attempts > 0:
                canvas.create_rectangle(x0, y_base - bar_h_total,
                                        x1, y_base,
                                        fill=FAINT, outline="")
                # correct portion (dark green)
                canvas.create_rectangle(x0, y_base - bar_h_correct,
                                        x1, y_base,
                                        fill=BAR_GOOD, outline="")
                # total count label on top of bar
                canvas.create_text((x0 + x1) / 2, y_base - bar_h_total - 8,
                                   text=str(attempts),
                                   font=("Helvetica", 8, "bold"),
                                   fill=INK)

            # x-axis tick: day-of-month; also include month letter on day 1
            try:
                d = datetime.date.fromisoformat(date_iso)
                label = f"{d.day}"
                if d.day == 1 or i == 0:
                    label = d.strftime("%d %b")
            except Exception:
                label = date_iso[-2:]

            is_today = (date_iso == today_iso)
            canvas.create_text((x0 + x1) / 2, y_base + 12,
                               text=label,
                               font=("Helvetica", 8, "bold" if is_today else "normal"),
                               fill=INK if is_today else MUTED)

            x += bar_w + gap

        # Legend
        lx = margin_l
        ly = h - 10
        canvas.create_rectangle(lx, ly - 6, lx + 10, ly + 2,
                                fill=BAR_GOOD, outline="")
        canvas.create_text(lx + 14, ly - 2, text="Correct", anchor="w",
                           font=("Helvetica", 8), fill=MUTED)
        canvas.create_rectangle(lx + 70, ly - 6, lx + 80, ly + 2,
                                fill=FAINT, outline="")
        canvas.create_text(lx + 84, ly - 2, text="Attempts", anchor="w",
                           font=("Helvetica", 8), fill=MUTED)

    # ---- 3. Accuracy trend per game ---------------------------------------

    def _section_accuracy_trends(self, parent):
        self._section_title(parent,
                            "Accuracy trend per game",
                            "Each sparkline shows the last sessions for that game mode — right-hand values are most recent.")

        inner = self._card(parent)

        games_with_data = []
        if self._sess:
            for gid in GAME_IDS:
                series = self._sess.accuracy_series(gid, limit=20)
                if series:
                    games_with_data.append((gid, series))

        if not games_with_data:
            tk.Label(inner, text="No game sessions logged yet.",
                     font=("Helvetica", 10), bg="white", fg=DIM).pack(anchor="w")
            return

        grid = tk.Frame(inner, bg="white")
        grid.pack(fill=tk.X)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        for idx, (gid, series) in enumerate(games_with_data):
            row = idx // 2
            col = idx % 2
            pad_r = (0, 14) if col == 0 else (0, 0)
            self._spark_cell(grid, row, col, pad_r, gid, series)

    def _spark_cell(self, parent, row, col, pad_r, gid, series):
        cell = tk.Frame(parent, bg="white")
        cell.grid(row=row, column=col, sticky="nsew", padx=pad_r, pady=6)

        name = GAME_SHORT.get(gid, gid)
        latest = series[-1]
        avg    = round(sum(series) / len(series))

        hdr = tk.Frame(cell, bg="white")
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=name,
                 font=("Helvetica", 10, "bold"),
                 bg="white", fg=INK).pack(side=tk.LEFT)
        tk.Label(hdr, text=f"avg {avg}%   ·   latest {latest}%",
                 font=("Helvetica", 9),
                 bg="white", fg=MUTED).pack(side=tk.RIGHT)

        spark = tk.Canvas(cell, width=320, height=54, bg="white",
                          highlightthickness=0)
        spark.pack(fill=tk.X, pady=(4, 2))
        self._draw_sparkline(spark, series, 320, 54)

    def _draw_sparkline(self, canvas, series, w, h):
        if not series:
            return
        pad = 4
        plot_w = w - 2 * pad
        plot_h = h - 2 * pad

        # y-axis 0..100 fixed so games are comparable
        def _xy(i, v):
            x = pad + (i / max(1, len(series) - 1)) * plot_w
            y = pad + (1 - v / 100) * plot_h
            return x, y

        # Reference lines: 50%, 80%
        for ref, col in [(50, SOFT), (80, "#e0e7ff")]:
            _, y = _xy(0, ref)
            canvas.create_line(pad, y, pad + plot_w, y, fill=col, width=1)

        # Fill area under line
        if len(series) >= 2:
            pts = [(pad + (i / (len(series) - 1)) * plot_w,
                    pad + (1 - v / 100) * plot_h) for i, v in enumerate(series)]
            poly = [pts[0][0], pad + plot_h]
            for x, y in pts:
                poly.extend([x, y])
            poly.extend([pts[-1][0], pad + plot_h])
            canvas.create_polygon(*poly, fill="#eef2ff", outline="")
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                canvas.create_line(x1, y1, x2, y2, fill=ACCENT, width=2)

        # Dots
        for i, v in enumerate(series):
            x, y = _xy(i, v)
            canvas.create_oval(x - 2, y - 2, x + 2, y + 2,
                               fill=ACCENT, outline="white", width=1)

    # ---- 4. Per-game table ------------------------------------------------

    def _section_per_game_table(self, parent):
        self._section_title(parent,
                            "Per-game summary",
                            "Aggregated across all logged sessions.")

        inner = self._card(parent)
        summary = self._sess.per_game_summary() if self._sess else {}

        if not summary:
            tk.Label(inner, text="No sessions yet.",
                     font=("Helvetica", 10), bg="white", fg=DIM).pack(anchor="w")
            return

        # Header
        cols = [
            ("Game",        "w", 28),
            ("Sessions",    "e",  8),
            ("Correct",     "e",  8),
            ("Attempts",    "e",  8),
            ("Avg acc.",    "e",  8),
            ("Best streak", "e",  10),
            ("Last played", "e",  12),
        ]
        hdr = tk.Frame(inner, bg="white")
        hdr.pack(fill=tk.X, pady=(0, 4))
        for text, anchor, width in cols:
            tk.Label(hdr, text=text, anchor=anchor, width=width,
                     font=("Helvetica", 9, "bold"),
                     bg="white", fg=DIM).pack(side=tk.LEFT)
        tk.Frame(inner, bg=CARD_BORDER, height=1).pack(fill=tk.X, pady=(0, 4))

        # Rows — in canonical game order
        shown = 0
        for gid in GAME_IDS:
            row_data = summary.get(gid)
            if not row_data:
                continue
            shown += 1
            bg = "white" if shown % 2 == 1 else SOFT
            row = tk.Frame(inner, bg=bg)
            row.pack(fill=tk.X)

            values = [
                (GAME_NAMES.get(gid, gid),        "w", 28),
                (str(row_data["sessions"]),       "e",  8),
                (str(row_data["total_correct"]),  "e",  8),
                (str(row_data["total_attempts"]), "e",  8),
                (f"{row_data['avg_accuracy']}%",  "e",  8),
                (str(row_data["best_streak"]),    "e",  10),
                (row_data["last_date"] or "—",    "e",  12),
            ]
            for val, anchor, width in values:
                tk.Label(row, text=val, anchor=anchor, width=width,
                         font=("Helvetica", 10),
                         bg=bg, fg=INK).pack(side=tk.LEFT, pady=4)

    # ---- 5. Highlights ----------------------------------------------------

    def _section_highlights(self, parent):
        self._section_title(parent,
                            "Highlights",
                            "Recent achievements and headline numbers.")

        inner = self._card(parent, pady=(0, 28))

        earned_ids = self._as.get_earned()
        pts        = self._as.get_points()
        ach_total  = len(ACHIEVEMENTS)

        # Top line: points and achievement count
        top = tk.Frame(inner, bg="white")
        top.pack(fill=tk.X, pady=(0, 10))
        tk.Label(top, text=f"⭐ {pts:,} pts",
                 font=("Helvetica", 16, "bold"),
                 bg="white", fg="#f59e0b").pack(side=tk.LEFT)
        tk.Label(top, text=f"   {len(earned_ids)} / {ach_total} achievements earned",
                 font=("Helvetica", 11),
                 bg="white", fg=MUTED).pack(side=tk.LEFT)

        # Latest 5 earned achievements (by order they appear in earned list)
        last_earned = list(earned_ids)[-5:][::-1]
        if not last_earned:
            tk.Label(inner, text="No achievements earned yet.",
                     font=("Helvetica", 10), bg="white", fg=DIM).pack(anchor="w")
            return

        tk.Label(inner, text="Recently earned",
                 font=("Helvetica", 10, "bold"),
                 bg="white", fg=MUTED).pack(anchor="w", pady=(6, 4))

        for aid in last_earned:
            ach = ACHIEVEMENTS_BY_ID.get(aid)
            if not ach:
                continue
            line = tk.Frame(inner, bg=SOFT, padx=12, pady=6)
            line.pack(fill=tk.X, pady=2)
            tk.Label(line, text=f"{ach['icon']}  {ach['name']}",
                     font=("Helvetica", 11, "bold"),
                     bg=SOFT, fg=INK).pack(side=tk.LEFT)
            tk.Label(line, text=f"+{ach['points']} pts",
                     font=("Helvetica", 9),
                     bg=SOFT, fg=MUTED).pack(side=tk.RIGHT)

    # ================================================================ helpers

    @staticmethod
    def _fmt_minutes(m: float) -> str:
        if m < 60:
            return f"{int(round(m))} min"
        hours = m / 60
        if hours < 10:
            return f"{hours:.1f} h"
        return f"{int(round(hours))} h"

    # ================================================================ export

    def _export_pdf(self):
        """Write a one-page PDF summary. Offers the user a Save-As dialog."""
        default_name = f"progress_{self.profile_name}_{datetime.date.today().isoformat()}.pdf"
        try:
            path = filedialog.asksaveasfilename(
                parent=self.parent.winfo_toplevel(),
                title="Save progress report",
                defaultextension=".pdf",
                initialfile=default_name,
                filetypes=[("PDF", "*.pdf")],
            )
        except Exception:
            path = ""

        if not path:
            return

        try:
            pdf_export.export_progress_report(
                path=path,
                profile_name=self.profile_name,
                ach_store=self._as,
                sessions_store=self._sess,
            )
            messagebox.showinfo(
                "Report saved",
                f"Progress report saved to:\n{path}",
            )
        except Exception as exc:
            messagebox.showerror(
                "Export failed",
                f"Could not create the PDF:\n\n{exc}",
            )
