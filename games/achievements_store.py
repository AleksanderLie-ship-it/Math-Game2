"""
achievements_store.py
---------------------
Persistent store for earned achievements and global gameplay stats.
Saved to <profile_dir>/achievements.json
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import json
import os
import pathlib

_DEFAULT_STATS = {
    "total_correct":           0,
    "best_streak_ever":        0,
    "days_played":             [],
    "games_played":            [],
    "per_game":                {},
    "missed_attempted":        False,
    "missed_cleared":          False,
    "missed_resilient":        False,
    "lb_positions":            {},
    "night_owl":               False,
    "early_bird":              False,
    # Tutorial-tracking fields (added v0.7.2). Fuel the "Learning"
    # achievement category; nothing else depends on them.
    "tutorials_viewed":        [],      # unique game_ids opened from the Tutorials panel
    "tutorials_finished":      [],      # unique game_ids read to the last slide
    "tutorial_example_cycled": False,   # flipped True the first time the pupil uses "Next example"
}


class AchievementsStore:
    def __init__(self, profile_dir: pathlib.Path):
        self._path = pathlib.Path(profile_dir) / "achievements.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    # ------------------------------------------------------------------ I/O

    def _load(self):
        try:
            with open(self._path, encoding="utf-8") as f:
                d = json.load(f)
            d.setdefault("earned", [])
            d.setdefault("points", 0)
            d.setdefault("stats",  {})
            for k, v in _DEFAULT_STATS.items():
                d["stats"].setdefault(k, v)
            return d
        except Exception:
            return {"earned": [], "points": 0, "stats": dict(_DEFAULT_STATS)}

    def _save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    # ---------------------------------------------------------------- queries

    def has(self, ach_id: str) -> bool:
        return ach_id in self._data["earned"]

    def get_points(self) -> int:
        return self._data["points"]

    def get_earned(self) -> list:
        return list(self._data["earned"])

    def get_stats(self) -> dict:
        return self._data["stats"]

    # ---------------------------------------------------------------- earning

    def earn(self, ach_id: str, points: int) -> bool:
        """Award an achievement. Returns True only if newly earned."""
        if ach_id in self._data["earned"]:
            return False
        self._data["earned"].append(ach_id)
        self._data["points"] += points
        self._save()
        return True

    # ------------------------------------------------------------------ stats

    def record_session(self, game_id, correct, attempts, accuracy, streak, today_str, hour):
        """Commit end-of-session stats. Call before checking end achievements."""
        s = self._data["stats"]

        s["total_correct"]    = s.get("total_correct", 0) + correct
        s["best_streak_ever"] = max(s.get("best_streak_ever", 0), streak)

        days = s.setdefault("days_played", [])
        if today_str not in days:
            days.append(today_str)

        if game_id:
            played = s.setdefault("games_played", [])
            if game_id not in played:
                played.append(game_id)

            pg    = s.setdefault("per_game", {})
            entry = pg.setdefault(game_id, {
                "sessions": 0, "best_accuracy": 0,
                "best_correct": 0, "best_attempts": 0,
            })
            entry["sessions"]      += 1
            entry["best_accuracy"]  = max(entry.get("best_accuracy",  0), accuracy)
            entry["best_correct"]   = max(entry.get("best_correct",   0), correct)
            entry["best_attempts"]  = max(entry.get("best_attempts",  0), attempts)

        if hour >= 21:
            s["night_owl"]  = True
        if hour < 7:
            s["early_bird"] = True

        self._save()

    def record_lb_position(self, game_id: str, position: int):
        """Record a leaderboard position for a game (lower is better)."""
        s   = self._data["stats"]
        pos = s.setdefault("lb_positions", {})
        if game_id not in pos or position < pos[game_id]:
            pos[game_id] = position
            self._save()

    def set_stat(self, key: str, value):
        """Set a single stat flag (e.g. missed_attempted)."""
        self._data["stats"][key] = value
        self._save()

    # --------------------------------------------------------- tutorial stats

    def record_tutorial_viewed(self, game_id: str):
        """Mark that the tutorial for game_id was opened. Idempotent."""
        s = self._data["stats"]
        viewed = s.setdefault("tutorials_viewed", [])
        if game_id and game_id not in viewed:
            viewed.append(game_id)
            self._save()

    def record_tutorial_finished(self, game_id: str):
        """Mark that the tutorial for game_id was read to the last slide."""
        s = self._data["stats"]
        done = s.setdefault("tutorials_finished", [])
        if game_id and game_id not in done:
            done.append(game_id)
            self._save()

    def mark_tutorial_example_cycled(self):
        """Flip the 'Next example button used at least once' flag."""
        s = self._data["stats"]
        if not s.get("tutorial_example_cycled", False):
            s["tutorial_example_cycled"] = True
            self._save()
