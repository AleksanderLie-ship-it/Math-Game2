"""
missed_store.py
---------------
Persists wrong answers across sessions so the student can review them later.
Saved to <profile_dir>/missed.json

Each entry is a dict:
  { "op": "×" | "÷", "a": int, "b": int,
    "expected": int | float, "allow_decimal": bool }

Deduplication key: (op, a, b).
"""
# Copyright (c) 2026 Aleksander Lie. All rights reserved.

import json
import pathlib


class MissedStore:
    def __init__(self, profile_dir: pathlib.Path):
        self._path = pathlib.Path(profile_dir) / "missed.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data: list = []
        self._load()

    # ----------------------------------------------------------------- private

    def _key(self, q: dict):
        return (q["op"], q["a"], q["b"])

    def _load(self):
        try:
            if self._path.exists():
                self._data = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            self._data = []

    def _save(self):
        try:
            self._path.write_text(
                json.dumps(self._data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ------------------------------------------------------------------ public

    def add(self, q: dict):
        """Add a missed question; silently deduplicates."""
        if q is None:
            return
        if not any(self._key(x) == self._key(q) for x in self._data):
            self._data.append(q)
            self._save()

    def remove(self, q: dict):
        """Remove a question once the student answers it correctly."""
        key = self._key(q)
        before = len(self._data)
        self._data = [x for x in self._data if self._key(x) != key]
        if len(self._data) != before:
            self._save()

    def get_all(self) -> list:
        return list(self._data)

    def count(self) -> int:
        return len(self._data)

    def clear(self):
        self._data = []
        self._save()
