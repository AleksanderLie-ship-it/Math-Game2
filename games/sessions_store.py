"""
sessions_store.py
-----------------
Per-session history log. One record per completed session.
Saved to <profile_dir>/sessions.json

Schema:
  {
    "sessions": [
      {
        "date":     "2026-04-17",      # ISO date
        "ts":       "2026-04-17T19:32:14", # ISO timestamp (start of session)
        "game_id":  "mult_basic",
        "correct":  12,
        "attempts": 15,
        "accuracy": 80,
        "streak":   7,
        "minutes":  3.4
      },
      ...
    ]
  }

Consumed by the Progress & Stats screen to render:
  - Questions-per-day bar chart (last 14 days)
  - Accuracy trend per game mode
  - Per-game summary table
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import json
import pathlib
import datetime
from collections import defaultdict


class SessionsStore:
    def __init__(self, profile_dir: pathlib.Path):
        self._path = pathlib.Path(profile_dir) / "sessions.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    # ------------------------------------------------------------------ I/O

    def _load(self) -> dict:
        try:
            if self._path.exists():
                d = json.loads(self._path.read_text(encoding="utf-8"))
                d.setdefault("sessions", [])
                return d
        except Exception:
            pass
        return {"sessions": []}

    def _save(self):
        try:
            self._path.write_text(
                json.dumps(self._data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ----------------------------------------------------------------- write

    def record(self, game_id: str, correct: int, attempts: int,
               accuracy: int, streak: int, minutes: float,
               ts: datetime.datetime | None = None):
        """Append a new session record. Silent on empty sessions."""
        if attempts <= 0:
            return
        ts = ts or datetime.datetime.now()
        entry = {
            "date":     ts.date().isoformat(),
            "ts":       ts.replace(microsecond=0).isoformat(),
            "game_id":  game_id or "",
            "correct":  int(correct),
            "attempts": int(attempts),
            "accuracy": int(accuracy),
            "streak":   int(streak),
            "minutes":  round(float(minutes), 2),
        }
        self._data["sessions"].append(entry)
        self._save()

    # ----------------------------------------------------------------- query

    def all_sessions(self) -> list[dict]:
        return list(self._data.get("sessions", []))

    def count(self) -> int:
        return len(self._data.get("sessions", []))

    # ---- aggregations for the stats screen ---------------------------------

    def daily_counts(self, days: int = 14,
                     today: datetime.date | None = None) -> list[tuple[str, int, int]]:
        """Return [(date_iso, correct, attempts), ...] for the last `days` days
        up to and including `today` (defaults to today). Days with no activity
        are included with zeros so the bar chart has a stable x-axis.
        """
        today = today or datetime.date.today()
        buckets = {(today - datetime.timedelta(days=i)).isoformat(): [0, 0]
                   for i in range(days - 1, -1, -1)}

        for s in self._data.get("sessions", []):
            d = s.get("date")
            if d in buckets:
                buckets[d][0] += int(s.get("correct", 0))
                buckets[d][1] += int(s.get("attempts", 0))

        # Preserve insertion order (oldest → newest)
        return [(d, c, a) for d, (c, a) in buckets.items()]

    def per_game_summary(self) -> dict[str, dict]:
        """Return per-game aggregates:
        { game_id: { sessions, total_correct, total_attempts, avg_accuracy,
                     best_streak, last_date } }
        """
        out: dict[str, dict] = defaultdict(lambda: {
            "sessions": 0,
            "total_correct": 0,
            "total_attempts": 0,
            "acc_sum": 0,        # internal; stripped before returning
            "best_streak": 0,
            "last_date": "",
        })

        for s in self._data.get("sessions", []):
            gid = s.get("game_id", "") or "unknown"
            row = out[gid]
            row["sessions"]       += 1
            row["total_correct"]  += int(s.get("correct", 0))
            row["total_attempts"] += int(s.get("attempts", 0))
            row["acc_sum"]        += int(s.get("accuracy", 0))
            row["best_streak"]     = max(row["best_streak"], int(s.get("streak", 0)))
            d = s.get("date", "")
            if d > row["last_date"]:
                row["last_date"] = d

        # Finalise: compute avg accuracy, drop internal field
        result = {}
        for gid, row in out.items():
            n = row["sessions"] or 1
            result[gid] = {
                "sessions":       row["sessions"],
                "total_correct":  row["total_correct"],
                "total_attempts": row["total_attempts"],
                "avg_accuracy":   round(row["acc_sum"] / n),
                "best_streak":    row["best_streak"],
                "last_date":      row["last_date"],
            }
        return result

    def accuracy_series(self, game_id: str, limit: int = 20) -> list[int]:
        """Return the most recent accuracy values (oldest → newest) for a game,
        capped at `limit` points. Empty if no sessions for that game."""
        rows = [int(s.get("accuracy", 0))
                for s in self._data.get("sessions", [])
                if s.get("game_id") == game_id]
        return rows[-limit:]

    def total_minutes(self) -> float:
        return round(sum(float(s.get("minutes", 0))
                         for s in self._data.get("sessions", [])), 1)

    def first_session_date(self) -> str | None:
        ses = self._data.get("sessions", [])
        if not ses:
            return None
        return min(s.get("date", "") for s in ses if s.get("date"))
