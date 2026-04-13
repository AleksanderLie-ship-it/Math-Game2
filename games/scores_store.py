"""
scores_store.py
---------------
Per-game top-10 leaderboards, persisted across sessions.
Saved to <profile_dir>/scores.json

Schema:
  { "<game_id>": [ { "name", "correct", "attempts", "accuracy", "streak", "date" }, ... ] }

Ranking: correct DESC -> accuracy DESC -> streak DESC.
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import json
import pathlib


def _sort_key(s: dict):
    return (-s["correct"], -s["accuracy"], -s.get("streak", 0))


class ScoresStore:
    TOP_N = 10

    def __init__(self, profile_dir: pathlib.Path):
        self._path = pathlib.Path(profile_dir) / "scores.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict = {}
        self._load()

    # ----------------------------------------------------------------- private

    def _load(self):
        try:
            if self._path.exists():
                self._data = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            self._data = {}

    def _save(self):
        try:
            self._path.write_text(
                json.dumps(self._data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ------------------------------------------------------------------ public

    def get_scores(self, game_id: str) -> list:
        return sorted(self._data.get(game_id, []), key=_sort_key)

    def qualifies(self, game_id: str, correct: int, accuracy: int, streak: int) -> bool:
        """Return True if this result belongs in the top-10 leaderboard."""
        if correct == 0:
            return False
        scores = self.get_scores(game_id)
        if len(scores) < self.TOP_N:
            return True
        tenth = scores[self.TOP_N - 1]
        return (-correct, -accuracy, -streak) < _sort_key(tenth)

    def add_score(self, game_id: str, entry: dict):
        bucket = self._data.setdefault(game_id, [])
        bucket.append(entry)
        self._data[game_id] = sorted(bucket, key=_sort_key)[: self.TOP_N]
        self._save()
